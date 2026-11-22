"""Utilidades para parseo PAGE-XML, recorte poligonal enmascarado y empaquetado METS ZIP."""

from __future__ import annotations

import logging
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import cv2
import numpy as np
from lxml import etree

from .config import (
    DEFAULT_DILATION_PX,
    DEFAULT_MIN_LINE_WIDTH_PX,
    PAGE_NS,
)

logger = logging.getLogger(__name__)

METS_NS = "http://www.loc.gov/METS/"
XLINK_NS = "http://www.w3.org/1999/xlink"


@dataclass
class ExtractedLine:
    """Representa una línea segmentada en PAGE-XML junto con su recorte poligonal."""

    line_id: str
    region_id: str
    width: int
    height: int
    bbox: tuple[int, int, int, int]
    coords_pts: np.ndarray
    crop_bgr: np.ndarray
    crop_path: Path
    existing_unicode: str = ""
    side: str = "unknown"


@dataclass
class EntryGroup:
    """Agrupa todas las líneas pertenecientes a una misma partida documental."""

    partida_id: str
    side: str
    lines: list[ExtractedLine]
    context_bbox: tuple[int, int, int, int]
    context_bgr: np.ndarray
    context_path: Path


def load_image_unicode(image_path: Path) -> np.ndarray:
    """Carga una imagen a resolución nativa soportando rutas Unicode en Windows 11."""
    if not image_path.exists():
        raise FileNotFoundError(f"No se encuentra la imagen: {image_path}")
    data = np.fromfile(str(image_path), dtype=np.uint8)
    img = cv2.imdecode(data, cv2.IMREAD_COLOR)
    if img is None:
        raise ValueError(f"OpenCV no pudo decodificar la imagen: {image_path}")
    return img


def save_image_unicode(output_path: Path, img: np.ndarray) -> None:
    """Guarda una imagen PNG soportando rutas Unicode en Windows 11."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    ok, encoded = cv2.imencode(".png", img)
    if not ok:
        raise RuntimeError(f"Error al codificar PNG para {output_path}")
    output_path.write_bytes(encoded.tobytes())


def parse_points(points_str: str, min_pts: int = 2) -> np.ndarray:
    """Convierte atributo PAGE-XML points='x1,y1 x2,y2 ...' en array Nx2 int32."""
    pts: list[list[int]] = []
    for token in points_str.strip().split():
        if "," not in token:
            continue
        x_str, y_str = token.split(",", 1)
        pts.append([int(round(float(x_str))), int(round(float(y_str)))])
    if len(pts) < min_pts:
        raise ValueError(f"Geometría insuficiente (<{min_pts} puntos): {points_str[:80]}")
    return np.array(pts, dtype=np.int32)


def _compute_paper_median_bgr(roi: np.ndarray, poly_mask: np.ndarray) -> np.ndarray:
    """Calcula la mediana del color de fondo del papel dentro de la línea.

    Excluye píxeles muy oscuros (borde negro del microfilm o tinta densa) si hay
    suficiente área de papel luminoso dentro del polígono, para garantizar que el
    relleno exterior no pinte recuadros negros.
    """
    pixels = roi[poly_mask > 0]
    if pixels.size == 0:
        return np.array([220, 220, 220], dtype=np.uint8)

    # Luminosidad aproximada en escala de grises
    gray_vals = pixels.mean(axis=1)
    # Píxeles de papel claros (> percentil 40 y > umbral 55 para evitar bordes negros)
    paper_candidates = pixels[(gray_vals > 55) & (gray_vals >= np.percentile(gray_vals, 35))]
    if len(paper_candidates) >= 10:
        median_bgr = np.median(paper_candidates, axis=0)
    else:
        median_bgr = np.median(pixels, axis=0)
    return np.clip(np.round(median_bgr), 0, 255).astype(np.uint8)


def extract_polygonal_line_crop(
    image: np.ndarray,
    coords_pts: np.ndarray,
    dilation_px: int = DEFAULT_DILATION_PX,
    extra_pad_px: int = 2,
) -> tuple[np.ndarray, tuple[int, int, int, int]]:
    """Extrae un recorte poligonal enmascarado con dilatación suave y relleno de fondo.

    Args:
        image: Imagen completa en formato BGR (resolución nativa).
        coords_pts: Puntos Nx2 del polígono `<Coords>`.
        dilation_px: Dilatación suave en píxeles (3-5 px) para no amputar caídos ni astas.
        extra_pad_px: Margen exterior adicional alrededor del polígono dilatado.

    Returns:
        (crop_bgr, (raw_x1, raw_y1, raw_x2, raw_y2))
    """
    img_h, img_w = image.shape[:2]

    raw_x1 = int(np.min(coords_pts[:, 0]))
    raw_y1 = int(np.min(coords_pts[:, 1]))
    raw_x2 = int(np.max(coords_pts[:, 0]))
    raw_y2 = int(np.max(coords_pts[:, 1]))

    pad = dilation_px + extra_pad_px
    roi_x1 = max(0, raw_x1 - pad)
    roi_y1 = max(0, raw_y1 - pad)
    roi_x2 = min(img_w, raw_x2 + 1 + pad)
    roi_y2 = min(img_h, raw_y2 + 1 + pad)

    roi = image[roi_y1:roi_y2, roi_x1:roi_x2]
    if roi.size == 0:
        raise ValueError(f"ROI vacío para bbox {(raw_x1, raw_y1, raw_x2, raw_y2)}")

    local_pts = coords_pts - np.array([roi_x1, roi_y1], dtype=np.int32)
    mask = np.zeros((roi.shape[0], roi.shape[1]), dtype=np.uint8)
    cv2.fillPoly(mask, [local_pts], 255)

    bg_bgr = _compute_paper_median_bgr(roi, mask)

    if dilation_px > 0:
        ksize = 2 * dilation_px + 1
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (ksize, ksize))
        mask_dilated = cv2.dilate(mask, kernel, iterations=1)
    else:
        mask_dilated = mask

    crop = np.empty_like(roi)
    crop[:, :] = bg_bgr
    fg_idx = mask_dilated > 0
    crop[fg_idx] = roi[fg_idx]

    return crop, (raw_x1, raw_y1, raw_x2, raw_y2)


def detect_gutter_x(bboxes: list[tuple[int, int, int, int]], img_w: int) -> float:
    """Detecta el eje X del lomo central buscando la zona de menor cruce horizontal.

    Evita usar `img_w / 2` a ciegas, ya que los fotogramas microfilmados suelen tener
    márgenes negros asimétricos que desplazan el lomo real respecto al centro de la imagen.
    """
    if not bboxes:
        return img_w / 2.0

    search_min = int(img_w * 0.35)
    search_max = int(img_w * 0.70)
    if search_max <= search_min:
        return img_w / 2.0

    # Proyección horizontal: cuántas líneas cruzan cada columna X
    counts = np.zeros(img_w, dtype=np.int32)
    for x1, _, x2, _ in bboxes:
        cx1 = max(0, x1)
        cx2 = min(img_w, x2)
        if cx2 > cx1:
            counts[cx1:cx2] += 1

    window = counts[search_min:search_max]
    min_cross = int(np.min(window))
    # Buscar la franja continua más ancha con mínimo cruce (idealmente 0 cruces = lomo limpio)
    zero_mask = (window == min_cross)
    best_start, best_len = 0, 0
    cur_start, cur_len = 0, 0
    for i, is_min in enumerate(zero_mask):
        if is_min:
            if cur_len == 0:
                cur_start = i
            cur_len += 1
            if cur_len > best_len:
                best_start, best_len = cur_start, cur_len
        else:
            cur_len = 0

    gutter = search_min + best_start + (best_len / 2.0)
    logger.info("Lomo central detectado automáticamente en X=%.1f px (mitad imagen=%.1f px)", gutter, img_w / 2.0)
    return gutter


def extract_lines_from_pagexml(
    image_path: Path,
    xml_path: Path,
    debug_crops_dir: Path,
    min_line_width_px: int = DEFAULT_MIN_LINE_WIDTH_PX,
    dilation_px: int = DEFAULT_DILATION_PX,
) -> tuple[list[ExtractedLine], list[dict[str, object]], tuple[int, int]]:
    """Parsea el PAGE-XML, valida dimensiones y extrae recortes poligonales a disco.

    Returns:
        (lineas_validas, lineas_descartadas, (img_w, img_h))
    """
    image = load_image_unicode(image_path)
    img_h, img_w = image.shape[:2]

    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(xml_path), parser)
    root = tree.getroot()

    ns = {"p": PAGE_NS}
    page_el = root.find(".//p:Page", ns)
    if page_el is None:
        raise ValueError(f"No se encontró elemento <Page> en {xml_path}")

    xml_w = int(page_el.attrib.get("imageWidth", img_w))
    xml_h = int(page_el.attrib.get("imageHeight", img_h))
    if (xml_w, xml_h) != (img_w, img_h):
        logger.warning(
            "Dimensiones de imagen (%dx%d) difieren del PAGE-XML (%dx%d). Se usan coordenadas nativas.",
            img_w,
            img_h,
            xml_w,
            xml_h,
        )

    debug_crops_dir.mkdir(parents=True, exist_ok=True)

    raw_items: list[tuple[str, str, np.ndarray, tuple[int, int, int, int], str]] = []
    skipped: list[dict[str, object]] = []

    for region in root.findall(".//p:TextRegion", ns):
        region_id = region.attrib.get("id", "region_sin_id")
        for line_el in region.findall("p:TextLine", ns):
            line_id = line_el.attrib.get("id", f"line_{len(raw_items) + 1:03d}")
            coords_el = line_el.find("p:Coords", ns)
            if coords_el is None or "points" not in coords_el.attrib:
                skipped.append({"line_id": line_id, "reason": "sin_coords"})
                continue

            coords_pts = parse_points(coords_el.attrib["points"])
            raw_x1 = int(np.min(coords_pts[:, 0]))
            raw_y1 = int(np.min(coords_pts[:, 1]))
            raw_x2 = int(np.max(coords_pts[:, 0]))
            raw_y2 = int(np.max(coords_pts[:, 1]))
            raw_w = raw_x2 - raw_x1

            if raw_w < min_line_width_px:
                logger.info(
                    "Descartando línea residual %s (ancho=%d px < %d px)",
                    line_id,
                    raw_w,
                    min_line_width_px,
                )
                skipped.append({"line_id": line_id, "reason": f"width_lt_{min_line_width_px}", "width": raw_w})
                continue

            unicode_el = line_el.find("p:TextEquiv/p:Unicode", ns)
            existing_text = (unicode_el.text or "").strip() if unicode_el is not None else ""
            raw_items.append((line_id, region_id, coords_pts, (raw_x1, raw_y1, raw_x2, raw_y2), existing_text))

    gutter_x = detect_gutter_x([item[3] for item in raw_items], img_w)
    extracted: list[ExtractedLine] = []

    for idx, (line_id, region_id, coords_pts, raw_bbox, existing_text) in enumerate(raw_items, start=1):
        crop_bgr, bbox = extract_polygonal_line_crop(
            image=image,
            coords_pts=coords_pts,
            dilation_px=dilation_px,
        )
        raw_w = bbox[2] - bbox[0]
        raw_h = bbox[3] - bbox[1]
        center_x = (bbox[0] + bbox[2]) / 2.0
        side = "izquierda" if center_x < gutter_x else "derecha"

        crop_filename = f"{idx:03d}_{side}_{line_id}.png"
        crop_path = debug_crops_dir / crop_filename
        save_image_unicode(crop_path, crop_bgr)

        extracted.append(
            ExtractedLine(
                line_id=line_id,
                region_id=region_id,
                width=raw_w,
                height=raw_h,
                bbox=bbox,
                coords_pts=coords_pts,
                crop_bgr=crop_bgr,
                crop_path=crop_path,
                existing_unicode=existing_text,
                side=side,
            )
        )

    return extracted, skipped, (img_w, img_h)


def _split_half_page_into_entries(side_lines: list[ExtractedLine]) -> list[list[ExtractedLine]]:
    """Segmenta espacialmente las líneas de una plana en partidas individuales.

    Detecta cierres de partida combinando saltos verticales claros entre líneas consecutivas
    del cuerpo (excluyendo apuntes marginales estrechos) o firmas sangradas seguidas de salto.
    """
    if len(side_lines) <= 1:
        return [side_lines] if side_lines else []

    ordered = sorted(side_lines, key=lambda ln: ((ln.bbox[1] + ln.bbox[3]) / 2.0, ln.bbox[0]))

    # Ancho típico del cuerpo de partida para distinguir cuerpo/firma frente a notas al margen
    max_w = max(ln.width for ln in ordered)
    body_lines = [ln for ln in ordered if ln.width >= max_w * 0.45]

    if len(body_lines) >= 4:
        body_ys = [(ln.bbox[1] + ln.bbox[3]) / 2.0 for ln in body_lines]
        deltas = [body_ys[i + 1] - body_ys[i] for i in range(len(body_ys) - 1) if body_ys[i + 1] > body_ys[i]]
        median_step = float(np.median(deltas)) if deltas else 65.0
    else:
        median_step = 65.0

    # Calcular límites Y de separación entre partidas
    split_y_thresholds: list[float] = []
    min_body_x1 = min((ln.bbox[0] for ln in ordered if ln.width >= max_w * 0.70), default=ordered[0].bbox[0])

    for i in range(len(ordered) - 1):
        cur = ordered[i]
        nxt = ordered[i + 1]
        cur_cy = (cur.bbox[1] + cur.bbox[3]) / 2.0
        nxt_cy = (nxt.bbox[1] + nxt.bbox[3]) / 2.0
        gap_y = nxt_cy - cur_cy

        # Detectar firma sangrada hacia la derecha o corta respecto al bloque principal, seguida de salto claro
        is_indented_signature = (
            cur.width < max_w * 0.65
            and cur.bbox[0] > min_body_x1 + 200
            and gap_y >= median_step * 1.35
        )
        is_large_vertical_gap = gap_y >= median_step * 1.95

        if is_indented_signature or is_large_vertical_gap:
            split_y_thresholds.append((cur_cy + nxt_cy) / 2.0)

    if not split_y_thresholds:
        return [ordered]

    groups: list[list[ExtractedLine]] = [[] for _ in range(len(split_y_thresholds) + 1)]
    for ln in ordered:
        cy = (ln.bbox[1] + ln.bbox[3]) / 2.0
        bucket = 0
        for thr in split_y_thresholds:
            if cy > thr:
                bucket += 1
        groups[bucket].append(ln)

    non_empty = [g for g in groups if g]
    # Fusionar cualquier cola residual corta (<3 líneas o solo firma sangrada) en la partida anterior
    merged: list[list[ExtractedLine]] = []
    for grp in non_empty:
        has_full_body = any(ln.width >= max_w * 0.65 for ln in grp)
        if merged and (len(grp) <= 2 or not has_full_body):
            merged[-1].extend(grp)
        else:
            merged.append(grp)

    return merged


def group_lines_by_partida(
    image_path: Path,
    lines: list[ExtractedLine],
    debug_crops_dir: Path,
    pad_px: int = 24,
) -> list[EntryGroup]:
    """Agrupa las líneas extraídas por partida documental (izquierda arriba/abajo, derecha arriba/abajo)
    y genera un recorte contextual completo por partida para pasarlo a Gemini.
    """
    image = load_image_unicode(image_path)
    img_h, img_w = image.shape[:2]

    left_lines = [ln for ln in lines if ln.side == "izquierda"]
    right_lines = [ln for ln in lines if ln.side == "derecha"]

    raw_groups: list[tuple[str, list[ExtractedLine]]] = []
    for grp in _split_half_page_into_entries(left_lines):
        raw_groups.append(("izquierda", grp))
    for grp in _split_half_page_into_entries(right_lines):
        raw_groups.append(("derecha", grp))

    entries: list[EntryGroup] = []
    for idx, (side, grp_lines) in enumerate(raw_groups, start=1):
        # Orden de lectura dentro de la partida: arriba->abajo, izquierda->derecha
        grp_sorted = sorted(grp_lines, key=lambda ln: (round(((ln.bbox[1] + ln.bbox[3]) / 2.0) / 20.0), ln.bbox[0]))

        x1 = max(0, min(ln.bbox[0] for ln in grp_sorted) - pad_px)
        y1 = max(0, min(ln.bbox[1] for ln in grp_sorted) - pad_px)
        x2 = min(img_w, max(ln.bbox[2] for ln in grp_sorted) + pad_px)
        y2 = min(img_h, max(ln.bbox[3] for ln in grp_sorted) + pad_px)

        context_bgr = image[y1:y2, x1:x2].copy()
        partida_id = f"partida_{idx:02d}_{side}"
        context_path = debug_crops_dir / f"{partida_id}_contexto.png"
        save_image_unicode(context_path, context_bgr)

        entries.append(
            EntryGroup(
                partida_id=partida_id,
                side=side,
                lines=grp_sorted,
                context_bbox=(x1, y1, x2, y2),
                context_bgr=context_bgr,
                context_path=context_path,
            )
        )

    return entries


def render_annotated_entry_crop(
    image: np.ndarray,
    entry: EntryGroup,
    output_path: Path,
    left_pad: int = 80,
) -> dict[int, str]:
    """Genera una imagen anotada de una partida con bandas sutiles y etiquetas [01]..[N].

    No tapa la tinta original (usa transparencia baja sobre polígonos) y añade margen izquierdo
    extra para etiquetas de líneas marginales. Devuelve mapa `{indice_1based: line_id}`.
    """
    x1, y1, x2, y2 = entry.context_bbox
    rx1 = max(0, x1 - left_pad)
    ry1 = y1
    rx2 = x2
    ry2 = y2

    canvas = image[ry1:ry2, rx1:rx2].copy()
    overlay = canvas.copy()

    palette = [
        (255, 190, 60),   # Azul/cian BGR
        (80, 210, 100),   # Verde BGR
        (70, 150, 255),   # Naranja BGR
        (220, 120, 220),  # Magenta BGR
    ]

    index_to_id: dict[int, str] = {}
    for idx, ln in enumerate(entry.lines, start=1):
        index_to_id[idx] = ln.line_id
        color = palette[(idx - 1) % len(palette)]
        local_pts = ln.coords_pts - np.array([rx1, ry1], dtype=np.int32)
        cv2.fillPoly(overlay, [local_pts], color)
        cv2.polylines(canvas, [local_pts], isClosed=True, color=color, thickness=1)

    # Mezcla sutil para no oscurecer tinta pálida
    cv2.addWeighted(overlay, 0.14, canvas, 0.86, 0, canvas)

    for idx, ln in enumerate(entry.lines, start=1):
        color = palette[(idx - 1) % len(palette)]
        lx1, ly1, lx2, ly2 = ln.bbox
        cy = int((ly1 + ly2) / 2.0) - ry1
        anchor_x = lx1 - rx1
        label = f"{idx:02d}"

        # Si es cuerpo junto a margen cercano, colocar pastilla justo antes del borde izquierdo del polígono
        box_w, box_h = 34, 20
        tx1 = max(2, anchor_x - box_w - 4)
        ty1 = max(2, min(canvas.shape[0] - box_h - 2, cy - box_h // 2))
        cv2.rectangle(canvas, (tx1, ty1), (tx1 + box_w, ty1 + box_h), (255, 255, 255), -1)
        cv2.rectangle(canvas, (tx1, ty1), (tx1 + box_w, ty1 + box_h), color, 2)
        cv2.putText(
            canvas,
            label,
            (tx1 + 4, ty1 + 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.52,
            (0, 0, 0),
            2,
            cv2.LINE_AA,
        )

    save_image_unicode(output_path, canvas)
    return index_to_id


def write_updated_pagexml(
    source_xml_path: Path,
    output_xml_path: Path,
    transcriptions: dict[str, str],
) -> int:
    """Inyecta las transcripciones en `<TextEquiv><Unicode>` preservando geometría y atributos.

    Returns:
        Número de líneas actualizadas en el XML.
    """
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(source_xml_path), parser)
    root = tree.getroot()
    ns = {"p": PAGE_NS}

    updated_count = 0
    for line_el in root.findall(".//p:TextLine", ns):
        line_id = line_el.attrib.get("id")
        if not line_id or line_id not in transcriptions:
            continue

        text_equiv = line_el.find("p:TextEquiv", ns)
        if text_equiv is None:
            text_equiv = etree.SubElement(line_el, f"{{{PAGE_NS}}}TextEquiv")

        unicode_el = text_equiv.find("p:Unicode", ns)
        if unicode_el is None:
            unicode_el = etree.SubElement(text_equiv, f"{{{PAGE_NS}}}Unicode")

        unicode_el.text = transcriptions[line_id]
        updated_count += 1

    output_xml_path.parent.mkdir(parents=True, exist_ok=True)
    tree.write(
        str(output_xml_path),
        encoding="UTF-8",
        xml_declaration=True,
        pretty_print=False,
    )
    return updated_count


def package_escriptorium_zip(
    xml_path: Path,
    mets_path: Path,
    zip_path: Path,
) -> Path:
    """Empaqueta el PAGE-XML transcrito y METS_4.xml (como METS.xml) en un ZIP para eScriptorium."""
    if not xml_path.exists():
        raise FileNotFoundError(f"No existe el PAGE-XML de salida: {xml_path}")
    if not mets_path.exists():
        raise FileNotFoundError(f"No existe el manifiesto METS: {mets_path}")

    parser = etree.XMLParser(remove_blank_text=False)
    mets_tree = etree.parse(str(mets_path), parser)
    mets_root = mets_tree.getroot()
    flocat = mets_root.find(f".//{{{METS_NS}}}FLocat")
    href_attr = f"{{{XLINK_NS}}}href"

    if flocat is not None and href_attr in flocat.attrib:
        target_xml_name = flocat.attrib[href_attr]
        if target_xml_name != xml_path.name:
            logger.info(
                "Actualizando xlink:href en METS.xml de '%s' a '%s' para empaquetado consistente.",
                target_xml_name,
                xml_path.name,
            )
            flocat.attrib[href_attr] = xml_path.name
    mets_bytes = etree.tostring(mets_tree, encoding="UTF-8", xml_declaration=False)

    zip_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(zip_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.write(xml_path, arcname=xml_path.name)
        zf.writestr("METS.xml", mets_bytes)

    return zip_path
