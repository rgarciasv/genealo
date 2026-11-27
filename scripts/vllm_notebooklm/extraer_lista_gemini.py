#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extractor de Molde LISTA (Índices Parroquiales Tabulares) con Gemini 4 (`ultra_high`).

Estrategia anti-alucinación y anti-desalineación para listas densas (~30–38 filas/plana):
1. Detecta automáticamente la caja de papel brillante (elimina el marco negro del microfilm).
2. Divide por el lomo central en Plana Izquierda y Plana Derecha.
3. Corta cada plana en N tiras horizontales solapadas (por defecto 3 tiras con ~7% de solape = ~12–14 filas/tira).
4. Envía cada tira a Gemini 4 con `resolution="ultra_high"` (2.240 tokens visuales) y salida Pydantic JSON estricta.
5. Deduplica automáticamente las filas de la zona de solape, propaga `id`/`id.` (carry-forward) y ejecuta
   auditoría determinista de monotonía de años y folios.
6. Exporta CSV (UTF-8 con BOM para Excel), JSON completo y tabla Markdown de inspección.
"""

from __future__ import annotations

import argparse
import base64
import csv
import difflib
import json
import logging
import os
import re
import sys
import time
from pathlib import Path
from typing import Literal, Optional

import cv2
import numpy as np
from google import genai
from pydantic import BaseModel, Field

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("extraer_lista_gemini")


# =============================================================================
# 1. ESQUEMAS PYDANTIC ESTRICTOS POR SUBTIPO DE LISTA
# =============================================================================


class BautismoIndiceRow(BaseModel):
    fila: int = Field(description="Número secuencial de fila dentro de la tira (1..N, de arriba abajo).")
    cortada: bool = Field(
        default=False,
        description="True SOLO si la línea está físicamente cortada horizontalmente en el borde superior o inferior de la imagen.",
    )
    nombre_bautizado: str = Field(
        description="Nombre y apellidos exactos del bautizado tal como están escritos en la columna izquierda."
    )
    padres: str = Field(
        description="Filiación/padres exactamente como aparecen tras el nombre (ej. 'de Lorenzo y Juana', 'de Mateo y Alfonsa')."
    )
    anio_literal: str = Field(
        description="Valor literal en la columna de Año: 4 dígitos (ej. '1841'), 'id' (si pone id/id./comillas) o '' si vacío."
    )
    libro_literal: str = Field(
        description="Valor literal en la columna de Libro: ej. '3º', '4º', '5º', 'id' o '' si vacío."
    )
    folio_literal: str = Field(
        description="Número de folio literal (solo los dígitos, ej. '240', '246', '8')."
    )
    vuelto: bool = Field(
        default=False,
        description="True si aparece 'v.' o 'v' a la derecha del número de folio indicando reverso/vuelto.",
    )
    duda: bool = Field(
        default=False,
        description="True si algún nombre, apellido o número presenta tinta muy borrosa o duda real.",
    )
    motivo: str = Field(default="", description="Breve motivo si duda=true; cadena vacía si no.")


class BautismoIndiceStripResult(BaseModel):
    filas: list[BautismoIndiceRow] = Field(
        description="Lista ordenada de arriba abajo con TODAS las filas visibles en esta tira."
    )


class CasadoIndiceRow(BaseModel):
    fila: int = Field(description="Número secuencial de fila dentro de la tira (1..N, de arriba abajo).")
    cortada: bool = Field(
        default=False,
        description="True SOLO si la línea está físicamente cortada horizontalmente en el borde superior o inferior de la imagen.",
    )
    novio: str = Field(description="Nombre y apellidos del contrayente varón (sin el estado civil entre paréntesis).")
    estado_novio: str = Field(
        default="",
        description="Estado civil explícito junto al novio si consta (ej. 'viudo', 's.'); '' si no consta por separado.",
    )
    novia: str = Field(description="Nombre y apellidos de la contrayente mujer (sin el estado civil entre paréntesis).")
    estado_novia: str = Field(
        default="",
        description="Estado civil explícito junto a la novia si consta (ej. 'viuda', 'soltera', 's.'); '' si no consta.",
    )
    estado_pareja: str = Field(
        default="",
        description="Indicador general al final de los nombres (ej. 's.' para solteros, 'viudos', etc.).",
    )
    anio_literal: str = Field(
        description="Valor literal en la columna de Año: 4 dígitos (ej. '1725'), 'id' o '' si vacío."
    )
    libro_literal: str = Field(
        description="Valor literal en la columna de Libro: ej. '1º', '2º', 'id' o '' si vacío."
    )
    folio_literal: str = Field(
        description="Número de folio literal en la columna de folios (ej. '37', '58', '81'). NO confundir con numeración a lápiz del borde derecho extremo."
    )
    nota_extra: str = Field(
        default="",
        description="Cualquier marca adicional junto al folio (ej. 'vis', 'v.', 'bis').",
    )
    num_margen_derecho: str = Field(
        default="",
        description="Si existe una columna auxiliar de números a lápiz en el borde extremo derecho (ej. '152', '154'), ponerla aquí; si no, ''.",
    )
    duda: bool = Field(
        default=False,
        description="True si algún nombre, apellido o número presenta tinta borrosa o duda real.",
    )
    motivo: str = Field(default="", description="Breve motivo si duda=true; cadena vacía si no.")


class CasadoIndiceStripResult(BaseModel):
    filas: list[CasadoIndiceRow] = Field(
        description="Lista ordenada de arriba abajo con TODAS las filas visibles en esta tira."
    )


# =============================================================================
# 2. UTILIDADES DE IMAGEN: RECORTE DE BORDE NEGRO, LOMO Y TIRAS SOLAPADAS
# =============================================================================


def load_image_unicode(path: Path) -> np.ndarray:
    data = np.fromfile(str(path), dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(f"No se pudo cargar la imagen: {path}")
    return img


def save_image_unicode(path: Path, img: np.ndarray) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    ok, buf = cv2.imencode(path.suffix or ".png", img)
    if not ok:
        raise RuntimeError(f"No se pudo codificar {path}")
    buf.tofile(str(path))


def _wide_true_bounds(mask_1d: np.ndarray, min_run: int = 200) -> tuple[int, int]:
    """Devuelve (inicio_min, fin_max) uniendo todos los bloques contiguos anchos (>= min_run).
    Así ignora hilos claros finos del borde del microfilm, pero conserva AMBAS planas abiertas aunque el lomo sea negro.
    """
    n = len(mask_1d)
    spans: list[tuple[int, int]] = []
    in_run = False
    cur_s = 0
    for i, val in enumerate(mask_1d):
        if val and not in_run:
            cur_s = i
            in_run = True
        elif not val and in_run:
            if (i - cur_s) >= min_run:
                spans.append((cur_s, i - 1))
            in_run = False
    if in_run and (n - cur_s) >= min_run:
        spans.append((cur_s, n - 1))
    if not spans:
        idx = np.where(mask_1d)[0]
        return (int(idx[0]), int(idx[-1])) if len(idx) else (0, n - 1)
    return spans[0][0], spans[-1][1]


def crop_book_paper_and_split_pages(img_bgr: np.ndarray) -> tuple[np.ndarray, np.ndarray, dict[str, int]]:
    """Elimina el marco negro del microfilm (incluyendo hilos claros en bordes) y divide en plana izq/dcha."""
    h, w = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # Umbral de píxeles de papel (> 75 evita el fondo negro del microfilm)
    paper_mask = (gray > 75).astype(np.uint8)

    col_frac = paper_mask.mean(axis=0)
    row_frac = paper_mask.mean(axis=1)

    x1, x2 = _wide_true_bounds(col_frac > 0.25, min_run=int(w * 0.12))
    y1, y2 = _wide_true_bounds(row_frac > 0.25, min_run=int(h * 0.15))

    # Margen de seguridad amplio (28 px en X para no rozar nunca el último dígito del folio derecho)
    x1 = max(0, x1 - 24)
    x2 = min(w, x2 + 28)
    y1 = max(0, y1 - 16)
    y2 = min(h, y2 + 16)

    book = img_bgr[y1:y2, x1:x2]
    bh, bw = book.shape[:2]

    # Buscar el lomo central (valle de menor brillo en la franja central [40%..60%])
    book_gray = cv2.cvtColor(book, cv2.COLOR_BGR2GRAY)
    search_l = int(bw * 0.42)
    search_r = int(bw * 0.58)
    col_profile = book_gray[int(bh * 0.15) : int(bh * 0.85), search_l:search_r].mean(axis=0)
    gutter_rel = int(np.argmin(col_profile)) + search_l

    # Dar 55 px de holgura a ambos lados del lomo para no morder nunca folios ni iniciales junto al pliegue
    left_page = book[:, : min(bw, gutter_rel + 55)]
    right_page = book[:, max(0, gutter_rel - 55) :]

    meta = {
        "orig_w": w,
        "orig_h": h,
        "book_x1": x1,
        "book_y1": y1,
        "book_x2": x2,
        "book_y2": y2,
        "gutter_x_book": gutter_rel,
    }
    return left_page, right_page, meta


def slice_page_into_strips(
    page_bgr: np.ndarray,
    num_strips: int = 3,
    overlap_ratio: float = 0.08,
) -> list[tuple[int, int, int, np.ndarray]]:
    """Recorta márgenes en blanco arriba/abajo de la plana y la divide en tiras horizontales solapadas."""
    ph, pw = page_bgr.shape[:2]
    # Recorte ligero de cabecera/pie vacíos (sin perder la primera ni la última fila)
    # Conservamos prácticamente toda la altura útil del papel (3% a 97%)
    top_y = int(ph * 0.02)
    bot_y = int(ph * 0.98)
    usable_h = bot_y - top_y

    strips: list[tuple[int, int, int, np.ndarray]] = []
    step = usable_h / num_strips
    ov = int(usable_h * overlap_ratio)

    for i in range(num_strips):
        sy1 = max(0, int(top_y + i * step) - (ov if i > 0 else 0))
        sy2 = min(ph, int(top_y + (i + 1) * step) + (ov if i < num_strips - 1 else 0))
        strips.append((i + 1, sy1, sy2, page_bgr[sy1:sy2, :].copy()))
    return strips


# =============================================================================
# 3. LLAMADA A GEMINI 4 (`ultra_high`)
# =============================================================================

SYSTEM_PROMPT_BAUT = """Eres un paleógrafo experto en índices parroquiales españoles del siglo XIX (Archivo Diocesano de Ávila, Parroquia de San Juan del Molinillo y sus anejos Navandrinal y El Villarejo).

Tu tarea es transcribir EXACTAMENTE todas las filas visibles de una tira horizontal de un **Índice Alfabético de Bautismos** (estructura: Nombre y apellidos del bautizado | padres 'de X y Y' | Año | Libro | Folio | 'v.' si vuelto).

REGLAS CRÍTICAS:
1. Lee TODAS las filas de arriba abajo SIN saltarte ninguna y SIN mezclar columnas entre filas adyacentes. Sigue cuidadosamente cada renglón horizontal de izquierda a derecha hasta su Año, Libro y Folio exactos.
2. En Año y Libro, escribe exactamente lo que aparece en tinta: ej. '1841', '1856', '3º', '4º', '5º', o 'id' cuando pone 'id' / 'id.' (ídem). NO resuelvas los 'id' por tu cuenta: transcribe literalmente 'id'.
3. Si a la derecha del número de folio hay una 'v' o 'v.' (vuelto), marca vuelto=true (y deja folio_literal solo con el número).
4. Si la primerísima o ultimísima fila del recorte está cortada horizontalmente por el borde de la imagen de forma que falta parte de la letra, marca cortada=true; si se lee íntegra, cortada=false.
5. Apellidos frecuentes de la comarca (solo ayuda visual, nunca forzar contra la tinta): Toribio, González, López, Jiménez, Hernández, Martín, Herranz, Encabo, Andrino, Blázquez, García, de la Fuente, Muñoz, Gil, Rodríguez, Sánchez, del Peso, Pérez.
6. Marca duda=true SOLO cuando algún nombre o cifra sea realmente dudoso por borrón, tachón o tinta muy desvaída.
Devuelve exclusivamente JSON válido según el esquema."""

SYSTEM_PROMPT_CAS = """Eres un paleógrafo experto en índices parroquiales españoles de los siglos XVIII–XIX (Archivo Diocesano de Ávila, Parroquia de San Juan del Molinillo y sus anejos Navandrinal y El Villarejo).

Tu tarea es transcribir EXACTAMENTE todas las filas visibles de una tira horizontal de un **Índice Cronológico de Casados (Matrimonios)** (estructura: Novio [estado] con Novia [estado] | indicador s. | Año | Libro | Folio [| nota como 'vis']).

REGLAS CRÍTICAS:
1. Lee TODAS las filas de arriba abajo SIN saltarte ninguna y SIN desalinear columnas: sigue horizontalmente cada línea desde el nombre de los novios hasta su Año, Libro y Folio exactos.
2. En Año y Libro, transcribe exactamente lo que está escrito: ej. '1725', '1734', '1º', '2º', o 'id' cuando aparece 'id' / 'id.'. NO expandas 'id' por tu cuenta.
3. Si en el borde derecho extremo hay una columna auxiliar de números a lápiz más grandes (ej. 152, 154, 157, 160...), ponla en `num_margen_derecho` y JAMÁS la confundas con `folio_literal`.
4. Distingue bien `estado_novio` / `estado_novia` (cuando dice '(viudo)', 'viudo', '(viuda)', 'soltera') y `estado_pareja` (la 's.' o '(viudos)' al final de la línea).
5. Si la primera o última fila está físicamente cortada horizontalmente por el borde de la imagen, marca cortada=true.
6. Apellidos frecuentes de la comarca (solo ayuda visual): Hernández, González, Muñoz, García, Toribio, Andrino, de la Fuente, Gil, Jiménez, Blázquez, Martín, López, Sánchez, Pérez, Herranz, Gómez, del Valle.
Devuelve exclusivamente JSON válido según el esquema."""


def encode_png_b64(img_bgr: np.ndarray) -> str:
    ok, buf = cv2.imencode(".png", img_bgr)
    if not ok:
        raise RuntimeError("Error codificando PNG en memoria")
    return base64.b64encode(buf.tobytes()).decode("utf-8")


def call_gemini_strip(
    client: genai.Client,
    strip_bgr: np.ndarray,
    tipo: Literal["bautismos", "casados"],
    model: str,
    resolution: str,
    thinking_level: str,
    strip_label: str,
) -> list[dict]:
    b64 = encode_png_b64(strip_bgr)
    if tipo == "bautismos":
        sys_prompt = SYSTEM_PROMPT_BAUT
        schema_cls = BautismoIndiceStripResult
    else:
        sys_prompt = SYSTEM_PROMPT_CAS
        schema_cls = CasadoIndiceStripResult

    user_prompt = (
        f"Transcribe todas las filas visibles de esta tira ({strip_label}) de arriba abajo, "
        "manteniendo alineación horizontal estricta entre los nombres y sus columnas de Año, Libro y Folio."
    )

    kwargs: dict = {
        "model": model,
        "system_instruction": sys_prompt,
        "input": [
            {"type": "text", "text": user_prompt},
            {
                "type": "image",
                "data": b64,
                "mime_type": "image/png",
                "resolution": resolution,
            },
        ],
        "response_format": {
            "type": "text",
            "mime_type": "application/json",
            "schema": schema_cls.model_json_schema(),
        },
        "store": False,
    }
    if model.lower().startswith("gemini-4") and thinking_level and thinking_level != "none":
        kwargs["generation_config"] = {"thinking_level": thinking_level}

    for attempt in range(1, 4):
        try:
            resp = client.interactions.create(**kwargs)
            parsed = schema_cls.model_validate_json(resp.output_text)
            return [r.model_dump() for r in parsed.filas]
        except Exception as exc:
            wait = 2.5 * (2 ** (attempt - 1))
            logger.warning("Error en %s (intento %d/3): %s. Reintentando en %.1fs...", strip_label, attempt, exc, wait)
            if attempt == 3:
                raise
            time.sleep(wait)
    return []


# =============================================================================
# 4. DEDUPLICACIÓN DE SOLAPE, PROPAGACIÓN `id` Y AUDITORÍA
# =============================================================================


def _row_signature(row: dict, tipo: str) -> str:
    if tipo == "bautismos":
        raw = f"{row.get('nombre_bautizado', '')} {row.get('padres', '')} {row.get('folio_literal', '')}"
    elif tipo == "difuntos":
        raw = f"{row.get('nombre_difunto', '')} {row.get('anio_literal', '')} {row.get('folio_literal', '')}"
    else:
        raw = f"{row.get('novio', '')} {row.get('novia', '')} {row.get('folio_literal', '')}"
    return re.sub(r"[^a-z0-9]+", " ", raw.lower()).strip()


def merge_overlapping_strips(strip_rows_list: list[list[dict]], tipo: str) -> list[dict]:
    """Cose las tiras consecutivas de una plana eliminando las filas duplicadas de la franja de solape."""
    merged: list[dict] = []
    for s_idx, rows in enumerate(strip_rows_list):
        # Descartar filas marcadas cortada=True en los bordes internos donde la tira vecina sí las tiene enteras
        cleaned = []
        for idx, r in enumerate(rows):
            if r.get("cortada"):
                # Si es primera fila de tira > 0 o última fila de tira < last, la vecina la tendrá completa
                if (idx == 0 and s_idx > 0) or (idx == len(rows) - 1 and s_idx < len(strip_rows_list) - 1):
                    continue
            cleaned.append(r)

        if not merged:
            merged.extend(cleaned)
            continue

        # Buscar mejor solapamiento k (de 1 a min(6, len)) entre cola de `merged` y cabeza de `cleaned`
        max_k = min(6, len(merged), len(cleaned))
        best_k = 0
        best_score = 0.0
        for k in range(1, max_k + 1):
            tail_sigs = [_row_signature(r, tipo) for r in merged[-k:]]
            head_sigs = [_row_signature(r, tipo) for r in cleaned[:k]]
            scores = [difflib.SequenceMatcher(None, a, b).ratio() for a, b in zip(tail_sigs, head_sigs)]
            avg_score = sum(scores) / k
            if min(scores) >= 0.62 and avg_score > best_score:
                best_score = avg_score
                best_k = k

        if best_k > 0:
            logger.info("    -> Solape detectado entre tiras: %d fila(s) (similitud %.2f), deduplicadas.", best_k, best_score)
            # Si alguna fila del solape en `merged` tenía duda y en `cleaned` no, preferir la limpia
            for j in range(best_k):
                old_r = merged[-best_k + j]
                new_r = cleaned[j]
                if old_r.get("duda") and not new_r.get("duda"):
                    merged[-best_k + j] = new_r
            merged.extend(cleaned[best_k:])
        else:
            # Chequeo extra por si 1 fila suelta duplicada aparece en la posición 0 o 1
            if cleaned and merged:
                s_last = _row_signature(merged[-1], tipo)
                s_first = _row_signature(cleaned[0], tipo)
                if difflib.SequenceMatcher(None, s_last, s_first).ratio() >= 0.72:
                    logger.info("    -> Solape puntual de 1 fila deduplicado.")
                    cleaned = cleaned[1:]
            merged.extend(cleaned)

    return merged


def _is_idem(val: str) -> bool:
    v = (val or "").strip().lower().rstrip(".")
    return v in ("", "id", "idem", "íd", "ídem", '"', "''", ",,", "dho", "dicho", "y")


def propagate_and_audit(rows: list[dict], tipo: str, image_name: str) -> list[dict]:
    """Resuelve carry-forward de `id` en Año y Libro y marca alertas de monotonía de folios."""
    cur_anio = ""
    cur_libro = ""
    cur_mes = ""
    prev_folio_by_book: dict[str, int] = {}

    enriched: list[dict] = []
    for idx, r in enumerate(rows, start=1):
        row = dict(r)
        if not row.get("imagen"):
            row["imagen"] = image_name
        row["fila_global"] = idx

        anio_lit = (row.get("anio_literal") or "").strip()
        libro_lit = (row.get("libro_literal") or "").strip()
        mes_lit = (row.get("mes_literal") or "").strip()
        folio_lit = (row.get("folio_literal") or "").strip()

        # Resolver año
        if not _is_idem(anio_lit) and re.search(r"\d{3,4}", anio_lit):
            m = re.search(r"\d{3,4}", anio_lit)
            yr = m.group(0)
            # Corregir notación abreviada tipo "846" -> "1846" si el año previo era 18xx
            if len(yr) == 3 and cur_anio and len(cur_anio) == 4:
                yr = cur_anio[0] + yr
            cur_anio = yr
        row["anio_resuelto"] = cur_anio

        # Resolver mes (para difuntos)
        if tipo == "difuntos":
            if not _is_idem(mes_lit):
                cur_mes = mes_lit
            row["mes_resuelto"] = cur_mes

        # Resolver libro
        if not _is_idem(libro_lit):
            cur_libro = libro_lit
        row["libro_resuelto"] = cur_libro

        # Auditoría de monotonía de folio dentro del mismo libro
        alerts: list[str] = []
        m_fol = re.search(r"\d+", folio_lit)
        if m_fol:
            fnum = int(m_fol.group(0))
            bkey = cur_libro or "UNKNOWN"
            prev_f = prev_folio_by_book.get(bkey)
            if prev_f is not None:
                if fnum < prev_f - 2:
                    alerts.append(f"Folio retrocede ({prev_f} -> {fnum}) en libro {bkey}")
                elif fnum > prev_f + 80:
                    alerts.append(f"Salto brusco de folio ({prev_f} -> {fnum}) en libro {bkey}")
            prev_folio_by_book[bkey] = fnum
        else:
            alerts.append("Folio sin número legible")

        row["alerta_auditoria"] = " | ".join(alerts)
        enriched.append(row)

    return enriched


# =============================================================================
# 5. EXPORTADORES Y MAIN
# =============================================================================


def export_results(rows: list[dict], tipo: str, out_dir: Path, stem: str) -> tuple[Path, Path, Path]:
    json_path = out_dir / f"{stem}_{tipo}.json"
    csv_path = out_dir / f"{stem}_{tipo}.csv"
    md_path = out_dir / f"{stem}_{tipo}.md"

    json_path.write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")

    if tipo == "bautismos":
        cols = [
            "fila_global", "plana", "nombre_bautizado", "padres",
            "anio_literal", "anio_resuelto", "libro_literal", "libro_resuelto",
            "folio_literal", "vuelto", "duda", "motivo", "alerta_auditoria", "imagen",
        ]
    elif tipo == "difuntos":
        cols = [
            "fila_global", "plana", "letra_seccion", "nombre_difunto",
            "anio_literal", "anio_resuelto", "mes_literal", "mes_resuelto", "dia_literal",
            "folio_literal", "vuelto", "duda", "motivo", "alerta_auditoria", "imagen",
        ]
    else:
        cols = [
            "fila_global", "plana", "novio", "estado_novio", "novia", "estado_novia",
            "estado_pareja", "anio_literal", "anio_resuelto", "libro_literal", "libro_resuelto",
            "folio_literal", "nota_extra", "num_margen_derecho", "duda", "motivo", "alerta_auditoria", "imagen",
        ]

    with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore", delimiter=";")
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    # Markdown limpio de auditoría visual
    md_lines = [
        f"# Extracción Piloto Molde LISTA ({tipo.upper()}): `{stem}.jpg`",
        "",
        f"- **Total filas extraídas (tras deduplicar solapes):** `{len(rows)}`",
        f"- **Filas marcadas con duda:** `{sum(1 for r in rows if r.get('duda'))}`",
        f"- **Alertas automáticas de monotonía/folio:** `{sum(1 for r in rows if r.get('alerta_auditoria'))}`",
        "",
    ]
    if tipo == "bautismos":
        md_lines.append("| # | Plana | Bautizado | Padres | Año (lit→res) | Libro (lit→res) | Folio | Vuelto | Duda / Alerta |")
        md_lines.append("| :-: | :-: | :--- | :--- | :-: | :-: | :-: | :-: | :--- |")
        for r in rows:
            flags = " / ".join(x for x in [f"DUDA: {r.get('motivo')}" if r.get("duda") else "", r.get("alerta_auditoria", "")] if x)
            md_lines.append(
                f"| {r['fila_global']} | {r.get('plana','')} | {r.get('nombre_bautizado','')} | {r.get('padres','')} | "
                f"{r.get('anio_literal','')}→**{r.get('anio_resuelto','')}** | {r.get('libro_literal','')}→**{r.get('libro_resuelto','')}** | "
                f"{r.get('folio_literal','')} | {'v.' if r.get('vuelto') else ''} | {flags} |"
            )
    elif tipo == "difuntos":
        md_lines.append("| # | Plana | Difunto / Observación | Año (lit→res) | Mes (lit→res) | Día | Folio | Vuelto | Duda / Alerta |")
        md_lines.append("| :-: | :-: | :--- | :-: | :-: | :-: | :-: | :-: | :--- |")
        for r in rows:
            flags = " / ".join(x for x in [f"DUDA: {r.get('motivo')}" if r.get("duda") else "", r.get("alerta_auditoria", "")] if x)
            md_lines.append(
                f"| {r['fila_global']} | {r.get('plana','')} | {r.get('nombre_difunto','')} | "
                f"{r.get('anio_literal','')}→**{r.get('anio_resuelto','')}** | {r.get('mes_literal','')}→**{r.get('mes_resuelto','')}** | "
                f"{r.get('dia_literal','')} | {r.get('folio_literal','')} | {'v.' if r.get('vuelto') else ''} | {flags} |"
            )
    else:
        md_lines.append("| # | Plana | Novio | Novia | Estado | Año (lit→res) | Libro (lit→res) | Folio | Nota / Duda / Alerta |")
        md_lines.append("| :-: | :-: | :--- | :--- | :-: | :-: | :-: | :-: | :--- |")
        for r in rows:
            est = " / ".join(x for x in [r.get("estado_novio",""), r.get("estado_novia",""), r.get("estado_pareja","")] if x)
            flags = " / ".join(x for x in [r.get("nota_extra",""), f"DUDA: {r.get('motivo')}" if r.get("duda") else "", r.get("alerta_auditoria", "")] if x)
            md_lines.append(
                f"| {r['fila_global']} | {r.get('plana','')} | {r.get('novio','')} | {r.get('novia','')} | {est} | "
                f"{r.get('anio_literal','')}→**{r.get('anio_resuelto','')}** | {r.get('libro_literal','')}→**{r.get('libro_resuelto','')}** | "
                f"{r.get('folio_literal','')} | {flags} |"
            )

    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    return csv_path, json_path, md_path


def run_slice_batch(
    input_dir: Path,
    start_img: str,
    end_img: str,
    out_dir: Path,
    num_strips: int,
    overlap: float,
) -> int:
    """Recorta en local un lote de imágenes en tiras solapadas (0 tokens / 0 API) para lectura por subagentes."""
    strips_dir = out_dir / "strips"
    raw_json_dir = out_dir / "raw_json"
    strips_dir.mkdir(parents=True, exist_ok=True)
    raw_json_dir.mkdir(parents=True, exist_ok=True)

    imgs = sorted(
        p for p in input_dir.glob("*.jpg")
        if (not start_img or p.name >= start_img) and (not end_img or p.name <= end_img)
    )
    if not imgs:
        logger.error("No se encontraron imágenes en %s entre %s y %s", input_dir, start_img, end_img)
        return 1

    manifest: list[dict] = []
    for img_path in imgs:
        img = load_image_unicode(img_path)
        left_page, right_page, meta = crop_book_paper_and_split_pages(img)
        img_strips: list[dict] = []
        for side_name, page_bgr in [("izquierda", left_page), ("derecha", right_page)]:
            for s_num, sy1, sy2, s_bgr in slice_page_into_strips(page_bgr, num_strips=num_strips, overlap_ratio=overlap):
                strip_name = f"{img_path.stem}_{side_name}_tira{s_num}.png"
                strip_file = strips_dir / strip_name
                save_image_unicode(strip_file, s_bgr)
                img_strips.append({
                    "side": side_name,
                    "tira": s_num,
                    "png": str(strip_file.resolve()),
                    "json_out": str((raw_json_dir / f"{img_path.stem}_{side_name}_tira{s_num}.json").resolve()),
                    "w": int(s_bgr.shape[1]),
                    "h": int(s_bgr.shape[0]),
                })
        manifest.append({"image": img_path.name, "stem": img_path.stem, "meta": meta, "strips": img_strips})
        logger.info("Recortada %s -> %d tiras (%s)", img_path.name, len(img_strips), strips_dir)

    manifest_path = out_dir / "manifest_strips.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info("Lote recortado: %d imágenes, %d tiras totales -> %s", len(manifest), sum(len(m["strips"]) for m in manifest), manifest_path)
    return 0


def run_merge_batch(out_dir: Path, tipo: str, output_stem: str, exclude_imgs: set[str] | None = None) -> int:
    """Consolida todos los JSON de tiras generados por subagentes en un único CSV/JSON/MD maestro."""
    manifest_path = out_dir / "manifest_strips.json"
    if not manifest_path.exists():
        logger.error("No existe %s. Ejecuta primero --slice-batch.", manifest_path)
        return 1
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    excl = exclude_imgs or set()

    all_rows: list[dict] = []
    missing_json: list[str] = []

    for entry in manifest:
        img_name = entry["image"]
        if img_name in excl or entry.get("stem", "") in excl:
            logger.info("Omitiendo imagen excluida/duplicada: %s", img_name)
            continue
        for side_name in ("izquierda", "derecha"):
            side_strips = sorted([s for s in entry["strips"] if s["side"] == side_name], key=lambda s: s["tira"])
            strip_rows_list: list[list[dict]] = []
            for s in side_strips:
                jp = Path(s["json_out"])
                if not jp.exists():
                    missing_json.append(jp.name)
                    continue
                raw = json.loads(jp.read_text(encoding="utf-8"))
                rows = raw.get("filas", raw) if isinstance(raw, dict) else raw
                if not isinstance(rows, list):
                    rows = []
                for r in rows:
                    r["plana"] = side_name
                    r["imagen"] = img_name
                strip_rows_list.append(rows)
            if strip_rows_list:
                merged_side = merge_overlapping_strips(strip_rows_list, tipo=tipo)
                all_rows.extend(merged_side)

    if missing_json:
        logger.warning("Faltan %d archivos JSON de tiras (primeros 10): %s", len(missing_json), missing_json[:10])

    final_rows = propagate_and_audit(all_rows, tipo=tipo, image_name=output_stem)
    csv_path, json_path, md_path = export_results(final_rows, tipo=tipo, out_dir=out_dir, stem=output_stem)
    n_dudas = sum(1 for r in final_rows if r.get("duda"))
    n_alerts = sum(1 for r in final_rows if r.get("alerta_auditoria"))
    logger.info(
        "CONSOLIDADO %s (%s) | Imágenes=%d | Filas=%d | Dudas=%d | Alertas=%d | Faltantes=%d | Salidas: %s, %s",
        output_stem, tipo, len(manifest), len(final_rows), n_dudas, n_alerts, len(missing_json), csv_path.name, md_path.name,
    )
    return 0


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Extractor tabular de Molde LISTA (Índices) en tiras solapadas.")
    parser.add_argument("--image", help="Ruta a una imagen .jpg individual (modo API directo).")
    parser.add_argument("--tipo", required=True, choices=["bautismos", "casados", "difuntos"], help="Tipo de índice tabular.")
    parser.add_argument("--output-dir", default="htr_pipeline/outputs/test_indice_jmol", help="Carpeta de salida.")
    parser.add_argument("--slice-batch", action="store_true", help="Solo recorta un lote de imágenes a tiras PNG (0 API).")
    parser.add_argument("--merge-batch", action="store_true", help="Consolida los JSON de tiras en raw_json/ a CSV/JSON/MD.")
    parser.add_argument("--input-dir", default="imagenes/rollo 004298570", help="Carpeta de imágenes para --slice-batch.")
    parser.add_argument("--start-img", default="", help="Nombre inicial inclusivo (ej. 004298570_02749.jpg).")
    parser.add_argument("--end-img", default="", help="Nombre final inclusivo (ej. 004298570_02766.jpg).")
    parser.add_argument("--output-stem", default="JMOL_INDICE", help="Prefijo de salida para --merge-batch.")
    parser.add_argument("--exclude-imgs", default="", help="Lista separada por comas de imágenes duplicadas a excluir en --merge-batch.")
    parser.add_argument("--model", default="gemini-4-hydrogen", help="Modelo Gemini 4 (modo API directo).")
    parser.add_argument("--resolution", default="ultra_high", choices=["high", "ultra_high"], help="Resolución visual por tira.")
    parser.add_argument("--thinking-level", default="medium", choices=["none", "low", "medium", "high"], help="Nivel de pensamiento.")
    parser.add_argument("--strips", type=int, default=4, help="Número de tiras horizontales por plana (default: 4).")
    parser.add_argument("--overlap", type=float, default=0.075, help="Solape vertical entre tiras (default: 0.075).")
    args = parser.parse_args()

    out_dir = Path(args.output_dir)
    if args.slice_batch:
        return run_slice_batch(Path(args.input_dir), args.start_img, args.end_img, out_dir, args.strips, args.overlap)
    if args.merge_batch:
        excl = {x.strip() for x in args.exclude_imgs.split(",") if x.strip()}
        return run_merge_batch(out_dir, args.tipo, args.output_stem, exclude_imgs=excl)

    if not args.image:
        logger.error("Indica --image (modo API) o --slice-batch / --merge-batch.")
        return 1

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        logger.error("Falta GEMINI_API_KEY en el entorno.")
        return 1

    img_path = Path(args.image)
    strips_dir = out_dir / "strips"
    out_dir.mkdir(parents=True, exist_ok=True)
    strips_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.perf_counter()
    img = load_image_unicode(img_path)
    left_page, right_page, meta = crop_book_paper_and_split_pages(img)
    logger.info(
        "Imagen %s (%dx%d) -> Papel [%d:%d, %d:%d] | Lomo rel=%d | Izq=%dx%d, Dcha=%dx%d",
        img_path.name,
        meta["orig_w"], meta["orig_h"],
        meta["book_x1"], meta["book_x2"], meta["book_y1"], meta["book_y2"],
        meta["gutter_x_book"],
        left_page.shape[1], left_page.shape[0],
        right_page.shape[1], right_page.shape[0],
    )

    client = genai.Client(api_key=api_key)
    all_page_rows: list[dict] = []

    for side_name, page_bgr in [("izquierda", left_page), ("derecha", right_page)]:
        strips = slice_page_into_strips(page_bgr, num_strips=args.strips, overlap_ratio=args.overlap)
        strip_results: list[list[dict]] = []
        for s_num, sy1, sy2, s_bgr in strips:
            strip_file = strips_dir / f"{img_path.stem}_{side_name}_tira{s_num}.png"
            save_image_unicode(strip_file, s_bgr)
            label = f"{img_path.stem} | plana {side_name} | tira {s_num}/{args.strips}"
            logger.info("  -> Consultando %s (%dx%d px) con %s (%s)...", label, s_bgr.shape[1], s_bgr.shape[0], args.model, args.resolution)
            rows = call_gemini_strip(
                client=client,
                strip_bgr=s_bgr,
                tipo=args.tipo,
                model=args.model,
                resolution=args.resolution,
                thinking_level=args.thinking_level,
                strip_label=label,
            )
            logger.info("     Extraídas %d filas brutas en %s", len(rows), label)
            for r in rows:
                r["plana"] = side_name
            strip_results.append(rows)
            time.sleep(0.5)

        merged_side = merge_overlapping_strips(strip_results, tipo=args.tipo)
        logger.info("  == Plana %s consolidada: %d filas únicas ==", side_name, len(merged_side))
        all_page_rows.extend(merged_side)

    final_rows = propagate_and_audit(all_page_rows, tipo=args.tipo, image_name=img_path.name)
    csv_path, json_path, md_path = export_results(final_rows, tipo=args.tipo, out_dir=out_dir, stem=img_path.stem)

    elapsed = time.perf_counter() - t0
    n_dudas = sum(1 for r in final_rows if r.get("duda"))
    n_alerts = sum(1 for r in final_rows if r.get("alerta_auditoria"))
    logger.info(
        "COMPLETADO %s (%s) en %.1fs | Filas=%d | Dudas=%d | Alertas=%d | Salidas: %s, %s",
        img_path.name, args.tipo, elapsed, len(final_rows), n_dudas, n_alerts, csv_path.name, md_path.name,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
