"""
Extracción exhaustiva del cuaderno tripartito JMOL-SACRAMENTAL-1842-1850 (JMOL-MIXTO-04)
mediante NotebookLM Pro en microlotes de 6 imágenes (con solape de 1 imagen) y coste $0 de API.

Genera:
  1) CSVs independientes por sacramento en htr_pipeline/outputs/jmol_sacramental_1842_1850/
  2) CSVs maestros enriquecidos (*_CON_SUPLEMENTO.csv) anexando Bautismos y Matrimonios
     con libro_resuelto="Supl. 1842-1850" sin sobrescribir los CSV originales de índices.

Uso:
  .\\venv\\Scripts\\python.exe scripts/vllm_notebooklm/extraer_sacramental_1842_1850_nlm.py
  .\\venv\\Scripts\\python.exe scripts/vllm_notebooklm/extraer_sacramental_1842_1850_nlm.py --serie bautismos
  .\\venv\\Scripts\\python.exe scripts/vllm_notebooklm/extraer_sacramental_1842_1850_nlm.py --merge-only
"""

import argparse
import csv
import json
import logging
import re
import subprocess
import sys
import time
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(
            "scripts/vllm_notebooklm/extraer_sacramental_1842_1850.log", encoding="utf-8"
        ),
    ],
)
logger = logging.getLogger("Sacramental1842")

DEFAULT_NOTEBOOK_ID = "81eb6310-b70c-40db-9fb0-b0c1f364ce05"
OUT_ROOT = Path("htr_pipeline/outputs/jmol_sacramental_1842_1850")
LOTES_DIR = OUT_ROOT / "lotes"
LOTES_DIR.mkdir(parents=True, exist_ok=True)

INDICE_BAUT_CSV = Path(
    "htr_pipeline/outputs/indice_jmol_bautismos/JMOL_INDICE_BAUTISMOS_1750_1921_bautismos.csv"
)
INDICE_CAS_CSV = Path(
    "htr_pipeline/outputs/indice_jmol_casados/JMOL_INDICE_CASADOS_1716_1920_casados.csv"
)

# Bloques exactos dentro de JMOL-SACRAMENTAL-1842-1850 (004298570_02429..02519)
# Microlotes de 4 imágenes (solape 1, paso 3) + ChatSettings LONGER + Reglas [L-03]/[L-07]
# heredadas del cuaderno piloto NRDL-BAUT-01 (prepare_nrdl_baut01.py).
SYSTEM_PROMPT_NLM = (
    "Eres un Catedrático de Paleografía y Diplomática Hispánica especializado en "
    "archivos parroquiales de los siglos XVI al XIX.\n"
    "REGLAS INQUEBRANTABLES:\n"
    "1. INSPECCIÓN VISUAL MULTIMODAL [L-03]: No confíes a ciegas en el índice OCR preliminar. "
    "Examina visualmente los píxeles de cada imagen adjunta línea por línea.\n"
    "2. CERO RESÚMENES Y CERO OMISIONES [L-03]: Extrae absolutamente todas las partidas "
    "presentes de arriba abajo en cada plana (izquierda y derecha) sin omitir ninguna ni añadir prosa.\n"
    "3. PROHIBICIÓN DE SESGO Y CONTAMINACIÓN [L-01, L-02]: Lee exclusivamente lo trazado "
    "físicamente en las imágenes seleccionadas; jamás inventes ni mezcles datos de otra página.\n"
    "4. GESTIÓN DE ROTURAS Y DUDAS [L-07]: Marca texto dañado como [ROTO], tinta perdida como "
    "[ILEGIBLE] y cualquier nombre/fecha dudosa como [DUDOSO: opción_A / opción_B]."
)

GROUNDING_FILES = [
    ("00_INSTRUCCIONES_PALEOGRAFICAS_V2", Path("00_INSTRUCCIONES_PALEOGRAFICAS_V2.md")),
    ("03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE", Path("03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md")),
    ("04_JURISDICCIONES_Y_DEPENDENCIAS_PARROQUIALES", Path("04_JURISDICCIONES_Y_DEPENDENCIAS_PARROQUIALES.md")),
]

SERIES_CONFIG = {
    "bautismos": {
        "start_frame": 2433,
        "end_frame": 2450,
        "chunk_size": 4,
        "overlap": 1,
        "headers": [
            "Imagen",
            "Folio",
            "Vuelto",
            "Fecha_Bautismo",
            "Anio",
            "Nombre_Bautizado",
            "Padres",
            "Aldea",
            "Observaciones",
        ],
        "prompt": """Actúa como archivero y paleógrafo experto. Examina TODAS y CADA UNA de las imágenes `.jpg` seleccionadas del cuaderno de **Bautismos convalidados (1847–1848)** de San Juan del Molinillo.

REGLAS ESTRICTAS:
1. Extrae **ABSOLUTAMENTE TODAS** las partidas de bautismo visibles en estas imágenes, sin omitir ni resumir ninguna (ignora diligencias de apertura/cierre o autos episcopales salvo mencionarlos en una nota final fuera de la tabla).
2. Si una partida comienza en una imagen y termina en la siguiente, inclúyela una sola vez indicando la imagen donde comienza.
3. En `Nombre_Bautizado` escribe nombre de pila y apellidos si constan (si solo consta el nombre de pila, reconstruye los apellidos a partir de los padres entre corchetes solo si es seguro, o pon el nombre literal y deja los padres completos en `Padres`).
4. En `Padres` escribe los nombres y apellidos completos de padre y madre (ej. `Pedro González y María López`).
5. En `Vuelto` pon `v.` si es folio vuelto o déjalo vacío si es recto.
6. En `Aldea` indica `Molinillo`, `Navandrinal`, `Villarejo` o el lugar que conste.
7. Si algún nombre o dato es dudoso, anota `[?]` y explícalo brevemente en `Observaciones`.

FORMATO OBLIGATORIO:
Devuelve **únicamente una tabla Markdown estricta** con EXACTAMENTE estas 9 columnas:

| Imagen | Folio | Vuelto | Fecha_Bautismo | Anio | Nombre_Bautizado | Padres | Aldea | Observaciones |
| :--- | :---: | :---: | :---: | :---: | :--- | :--- | :--- | :--- |""",
    },
    "casados": {
        "start_frame": 2452,
        "end_frame": 2483,
        "chunk_size": 4,
        "overlap": 1,
        "headers": [
            "Imagen",
            "Folio",
            "Vuelto",
            "Fecha_Matrimonio",
            "Anio",
            "Novio",
            "Estado_Novio",
            "Novia",
            "Estado_Novia",
            "Aldea",
            "Observaciones",
        ],
        "prompt": """Actúa como archivero y paleógrafo experto. Examina TODAS y CADA UNA de las imágenes `.jpg` seleccionadas del cuaderno de **Matrimonios convalidados (1842–1849)** de San Juan del Molinillo.

REGLAS ESTRICTAS:
1. Extrae **ABSOLUTAMENTE TODAS** las partidas de matrimonio/velación visibles en estas imágenes, sin omitir ni resumir ninguna.
2. Si una partida se reparte entre dos imágenes, inclúyela una sola vez indicando la imagen donde comienza.
3. En `Estado_Novio` y `Estado_Novia` indica `s.` (soltero/a) o `viudo`/`viuda` si consta (vacío si no consta).
4. En `Vuelto` pon `v.` si es folio vuelto o déjalo vacío si es recto.
5. En `Aldea` indica la vecindad o naturaleza (`Molinillo`, `Navandrinal`, `Villarejo`, etc.).
6. Si hay dispensa de parentesco, velación posterior o duda paleográfica, indícalo brevemente en `Observaciones`.

FORMATO OBLIGATORIO:
Devuelve **únicamente una tabla Markdown estricta** con EXACTAMENTE estas 11 columnas:

| Imagen | Folio | Vuelto | Fecha_Matrimonio | Anio | Novio | Estado_Novio | Novia | Estado_Novia | Aldea | Observaciones |
| :--- | :---: | :---: | :---: | :---: | :--- | :---: | :--- | :---: | :--- | :--- |""",
    },
    "difuntos": {
        "start_frame": 2485,
        "end_frame": 2518,
        "chunk_size": 4,
        "overlap": 1,
        "headers": [
            "Imagen",
            "Folio",
            "Vuelto",
            "Fecha_Entierro",
            "Anio",
            "Mes",
            "Dia",
            "Nombre_Difunto",
            "Condicion_o_Padres",
            "Aldea",
            "Observaciones",
        ],
        "prompt": """Actúa como archivero y paleógrafo experto. Examina TODAS y CADA UNA de las imágenes `.jpg` seleccionadas del cuaderno de **Defunciones / Entierros convalidados (1843–1849)** de San Juan del Molinillo.

REGLAS ESTRICTAS:
1. Extrae **ABSOLUTAMENTE TODAS** las partidas de defunción/entierro (tanto adultos como párvulos) visibles en estas imágenes, sin omitir ni resumir ninguna.
2. Si una partida se reparte entre dos imágenes, inclúyela una sola vez indicando la imagen donde comienza.
3. En `Mes` escribe el mes en español (ej. `Enero`, `Febrero`...) y en `Dia` el número del día.
4. En `Condicion_o_Padres` indica si es párvulo (y sus padres) o adulto (estado civil, cónyuge o viudez).
5. En `Vuelto` pon `v.` si es folio vuelto o déjalo vacío si es recto.
6. En `Aldea` indica `Molinillo`, `Navandrinal`, `Villarejo` o el lugar que conste.
7. Si hay duda paleográfica o nota de testamento/sacramentos relevante, indícalo brevemente en `Observaciones`.

FORMATO OBLIGATORIO:
Devuelve **únicamente una tabla Markdown estricta** con EXACTAMENTE estas 11 columnas:

| Imagen | Folio | Vuelto | Fecha_Entierro | Anio | Mes | Dia | Nombre_Difunto | Condicion_o_Padres | Aldea | Observaciones |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- | :--- | :--- | :--- |""",
    },
}


def load_notebook_id() -> str:
    ckpt = Path("scripts/vllm_notebooklm/ingest_checkpoint_jmol.json")
    if ckpt.exists():
        data = json.loads(ckpt.read_text(encoding="utf-8"))
        for k, v in data.get("notebook_ids", {}).items():
            if k in ("JMOL-MIXTO-04", "JMOL-SACRAMENTAL-1842-1850"):
                return v
    return DEFAULT_NOTEBOOK_ID


def refresh_token(cli_path: Path):
    logger.info("[REGLA L-21] Renovando sesión de NotebookLM...")
    try:
        res = subprocess.run(
            [str(cli_path), "login"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=90,
        )
        logger.info(f"[REGLA L-21] Login exit={res.returncode}")
        time.sleep(5)
    except Exception as e:
        logger.error(f"[REGLA L-21] Error renovando token: {e}")


def is_auth_error(text: str) -> bool:
    low = text.lower()
    return any(
        kw in low
        for kw in ("authentication", "signed-out", "signed out", "login", "unauthorized", "401", "cookie", "expired")
    )


def is_rate_limit_error(text: str) -> bool:
    low = text.lower()
    return "rate limited" in low or "rejected by the api" in low or "429" in low


def get_notebook_sources(cli_path: Path, n_id: str) -> tuple[list[dict], list[dict]]:
    res = subprocess.run(
        [str(cli_path), "source", "list", "-n", n_id, "--json"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    if res.returncode != 0:
        return [], []
    data = json.loads(res.stdout)
    srcs = data if isinstance(data, list) else data.get("sources", [])
    imgs = [s for s in srcs if (s.get("title") or "").lower().endswith(".jpg") or s.get("type") == "image"]
    non_imgs = [s for s in srcs if s not in imgs]
    imgs.sort(key=lambda s: s.get("title") or "")
    return imgs, non_imgs


def frame_number(title: str) -> int:
    m = re.search(r"_(\d+)\.jpg$", title, re.IGNORECASE)
    return int(m.group(1)) if m else -1


def build_overlapping_batches(imgs: list[dict], chunk_size: int, overlap: int) -> list[list[dict]]:
    if not imgs:
        return []
    step = max(1, chunk_size - overlap)
    batches = []
    i = 0
    while i < len(imgs):
        batch = imgs[i : i + chunk_size]
        batches.append(batch)
        if i + chunk_size >= len(imgs):
            break
        i += step
    return batches


def parse_md_table(text: str, expected_cols: int) -> list[list[str]]:
    rows: list[list[str]] = []
    header_seen = False
    sep_seen = False
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not header_seen:
            if any("imagen" in c.lower() for c in cells):
                header_seen = True
            continue
        if not sep_seen:
            if all(set(c.replace(":", "").replace("-", "").replace(" ", "")) == set() for c in cells):
                sep_seen = True
                continue
        if header_seen:
            if len(cells) < expected_cols:
                cells.extend([""] * (expected_cols - len(cells)))
            rows.append(cells[:expected_cols])
    return rows


def run_single_ask(
    cli_path: Path, n_id: str, prompt_file: Path, source_ids: list[str], expected_cols: int, timeout_sec: int = 240
) -> tuple[str | None, bool, str]:
    cmd = [
        str(cli_path),
        "ask",
        "-n",
        n_id,
        "--new",
        "--yes",
        "--json",
        "--prompt-file",
        str(prompt_file),
        "--timeout",
        str(timeout_sec),
    ]
    for sid in source_ids:
        cmd.extend(["-s", sid])
    try:
        res = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_sec + 40,
        )
        if res.returncode == 0:
            try:
                payload = json.loads(res.stdout)
                ans = (payload.get("answer") or "").strip()
            except json.JSONDecodeError:
                ans = res.stdout.strip()
            rows = parse_md_table(ans, expected_cols)
            if rows:
                return ans, False, ""
            return None, False, f"Sin tabla válida ({len(ans)} chars)"
        err_msg = ((res.stderr or "") + "\n" + (res.stdout or "")).strip()
        return None, is_auth_error(err_msg), err_msg[:300]
    except subprocess.TimeoutExpired:
        return None, False, f"Timeout ({timeout_sec + 40}s)"
    except Exception as e:
        return None, False, str(e)


def norm_key(s: str) -> str:
    return re.sub(r"\W+", "", (s or "").lower())


def deduplicate_rows(rows: list[list[str]], serie: str) -> list[list[str]]:
    seen = set()
    clean = []
    for r in rows:
        if serie == "bautismos":
            # (Imagen, Folio, Nombre_Bautizado)
            key = (norm_key(r[0]), norm_key(r[1]), norm_key(r[5])[:24])
            key_alt = (norm_key(r[1]), norm_key(r[4]), norm_key(r[5])[:24])
        elif serie == "casados":
            # (Folio, Anio, Novio, Novia)
            key = (norm_key(r[0]), norm_key(r[1]), norm_key(r[5])[:18], norm_key(r[7])[:18])
            key_alt = (norm_key(r[1]), norm_key(r[4]), norm_key(r[5])[:18], norm_key(r[7])[:18])
        else:
            # difuntos: (Folio, Anio, Nombre_Difunto)
            key = (norm_key(r[0]), norm_key(r[1]), norm_key(r[7])[:24])
            key_alt = (norm_key(r[1]), norm_key(r[4]), norm_key(r[7])[:24])
        if key in seen or key_alt in seen:
            continue
        seen.add(key)
        seen.add(key_alt)
        clean.append(r)
    return clean


def merge_and_integrate(series_list: list[str]):
    for serie in series_list:
        cfg = SERIES_CONFIG[serie]
        headers = cfg["headers"]
        lote_files = sorted(LOTES_DIR.glob(f"{serie}_lote_*.md"))
        if not lote_files:
            logger.warning(f"No hay lotes guardados para {serie}.")
            continue
        raw_rows = []
        for lf in lote_files:
            raw_rows.extend(parse_md_table(lf.read_text(encoding="utf-8"), len(headers)))
        dedup = deduplicate_rows(raw_rows, serie)
        out_csv = OUT_ROOT / f"JMOL_SACRAMENTAL_1842_1850_{serie}.csv"
        with open(out_csv, "w", encoding="utf-8-sig", newline="") as f:
            w = csv.writer(f, delimiter=";")
            w.writerow(headers)
            w.writerows(dedup)
        logger.info(f"[{serie.upper()}] Consolidado {out_csv} -> {len(dedup)} partidas (de {len(raw_rows)} brutas).")

        # Integración en maestros de índices (sin sobrescribir originales)
        if serie == "bautismos" and INDICE_BAUT_CSV.exists():
            integrate_bautismos(dedup)
        elif serie == "casados" and INDICE_CAS_CSV.exists():
            integrate_casados(dedup)


def integrate_bautismos(rows: list[list[str]]):
    out_path = INDICE_BAUT_CSV.with_name("JMOL_INDICE_BAUTISMOS_1750_1921_CON_SUPLEMENTO.csv")
    with open(INDICE_BAUT_CSV, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        fieldnames = list(reader.fieldnames or [])
        base_rows = list(reader)
    if "fuente_volumen" not in fieldnames:
        fieldnames.append("fuente_volumen")
    for r in base_rows:
        r["fuente_volumen"] = "JMOL-INDICE-BAUT-MAT"

    next_id = len(base_rows) + 1
    for r in rows:
        img, fol, vto, fecha, anio, nombre, padres, aldea, obs = r
        duda = "True" if "[?]" in (nombre + padres + obs) else "False"
        motivo = f"Fecha: {fecha} | Aldea: {aldea} | {obs}".strip(" |")
        base_rows.append(
            {
                "fila_global": str(next_id),
                "plana": "expediente",
                "nombre_bautizado": nombre,
                "padres": padres,
                "anio_literal": anio,
                "anio_resuelto": anio,
                "libro_literal": "Supl. 1842-1850",
                "libro_resuelto": "Supl. 1842-1850",
                "folio_literal": fol,
                "vuelto": vto,
                "duda": duda,
                "motivo": motivo,
                "alerta_auditoria": "",
                "imagen": img,
                "fuente_volumen": "JMOL-SACRAMENTAL-1842-1850",
            }
        )
        next_id += 1

    with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        w.writeheader()
        w.writerows(base_rows)
    logger.info(f"[INTEGRACIÓN] Generado {out_path} ({len(base_rows)} filas totales, +{len(rows)} del suplemento).")


def integrate_casados(rows: list[list[str]]):
    out_path = INDICE_CAS_CSV.with_name("JMOL_INDICE_CASADOS_1716_1920_CON_SUPLEMENTO.csv")
    with open(INDICE_CAS_CSV, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        fieldnames = list(reader.fieldnames or [])
        base_rows = list(reader)
    if "fuente_volumen" not in fieldnames:
        fieldnames.append("fuente_volumen")
    for r in base_rows:
        r["fuente_volumen"] = "JMOL-INDICE-BAUT-MAT"

    next_id = len(base_rows) + 1
    for r in rows:
        img, fol, vto, fecha, anio, novio, est_novio, novia, est_novia, aldea, obs = r
        duda = "True" if "[?]" in (novio + novia + obs) else "False"
        nota = f"Fecha: {fecha} | Aldea: {aldea} | {obs}".strip(" |")
        base_rows.append(
            {
                "fila_global": str(next_id),
                "plana": "expediente",
                "novio": novio,
                "estado_novio": est_novio,
                "novia": novia,
                "estado_novia": est_novia,
                "estado_pareja": "",
                "anio_literal": anio,
                "anio_resuelto": anio,
                "libro_literal": "Supl. 1842-1850",
                "libro_resuelto": "Supl. 1842-1850",
                "folio_literal": f"{fol} {vto}".strip(),
                "nota_extra": nota,
                "num_margen_derecho": "",
                "duda": duda,
                "motivo": obs if duda == "True" else "",
                "alerta_auditoria": "",
                "imagen": img,
                "fuente_volumen": "JMOL-SACRAMENTAL-1842-1850",
            }
        )
        next_id += 1

    with open(out_path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        w.writeheader()
        w.writerows(base_rows)
    logger.info(f"[INTEGRACIÓN] Generado {out_path} ({len(base_rows)} filas totales, +{len(rows)} del suplemento).")


def prepare_notebook_grounding(cli_path: Path, n_id: str, existing_non_imgs: list[dict]):
    """Configura ChatSettings (goal=CUSTOM, response_length=LONGER, SYSTEM_PROMPT_NLM)
    e inyecta las fuentes maestras 00/03/04 si faltan (patrón prepare_nrdl_baut01.py)."""
    logger.info(f"[GROUNDING] Configurando ChatSettings (CUSTOM + LONGER) en {n_id}...")
    res = subprocess.run(
        [
            str(cli_path),
            "configure",
            "-n",
            n_id,
            "--persona",
            SYSTEM_PROMPT_NLM,
            "--response-length",
            "longer",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    if res.returncode == 0:
        logger.info("  -> ChatSettings configurado correctamente.")
    else:
        logger.warning(f"  -> Aviso configurando ChatSettings: {(res.stderr or res.stdout).strip()[:200]}")

    existing_titles = {(s.get("title") or "").strip() for s in existing_non_imgs}
    for title, path in GROUNDING_FILES:
        if any(title in t for t in existing_titles):
            logger.info(f"  -> Fuente '{title}' ya presente en el cuaderno.")
            continue
        if not path.exists():
            logger.warning(f"  -> No se encontró archivo local de grounding: {path}")
            continue
        logger.info(f"  -> Subiendo fuente de grounding '{title}'...")
        res_add = subprocess.run(
            [str(cli_path), "source", "add", "-n", n_id, str(path.resolve()), "--title", title],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=120,
        )
        if res_add.returncode == 0:
            logger.info(f"     OK: '{title}' inyectada.")
        else:
            logger.warning(f"     Aviso subiendo '{title}': {(res_add.stderr or res_add.stdout).strip()[:200]}")
        time.sleep(2)


def main():
    parser = argparse.ArgumentParser(description="Extraer JMOL-SACRAMENTAL-1842-1850 vía NotebookLM.")
    parser.add_argument(
        "--serie", choices=["bautismos", "casados", "difuntos", "all"], default="all", help="Serie a procesar."
    )
    parser.add_argument("--prepare", action="store_true", help="Configurar ChatSettings LONGER e inyectar grounding 00/03/04 antes de extraer.")
    parser.add_argument("--merge-only", action="store_true", help="Solo consolidar lotes ya descargados.")
    parser.add_argument("--force", action="store_true", help="Re-ejecutar lotes ya guardados.")
    parser.add_argument("--pause", type=int, default=8, help="Pausa en segundos entre consultas a NotebookLM.")
    args = parser.parse_args()

    series_list = ["bautismos", "casados", "difuntos"] if args.serie == "all" else [args.serie]

    if args.merge_only:
        merge_and_integrate(series_list)
        return

    cli_path = Path("venv/Scripts/notebooklm.exe").resolve()
    n_id = load_notebook_id()
    temp_prompt = Path("scripts/vllm_notebooklm/temp_sacramental_prompt.txt").resolve()

    imgs, non_imgs = get_notebook_sources(cli_path, n_id)
    if not imgs:
        refresh_token(cli_path)
        imgs, non_imgs = get_notebook_sources(cli_path, n_id)
    if not imgs:
        logger.error(f"No se pudieron listar las fuentes de {n_id}.")
        sys.exit(1)

    if args.prepare:
        prepare_notebook_grounding(cli_path, n_id, non_imgs)
        imgs, non_imgs = get_notebook_sources(cli_path, n_id)

    non_img_ids = [s["id"] for s in non_imgs if s.get("id")]
    logger.info(f"Cuaderno {n_id}: {len(imgs)} imágenes + {len(non_imgs)} fuentes de grounding.")

    failed = []
    for serie in series_list:
        cfg = SERIES_CONFIG[serie]
        serie_imgs = [
            s for s in imgs if cfg["start_frame"] <= frame_number(s.get("title", "")) <= cfg["end_frame"]
        ]
        batches = build_overlapping_batches(serie_imgs, cfg["chunk_size"], cfg["overlap"])
        logger.info(f"=== {serie.upper()}: {len(serie_imgs)} imgs en {len(batches)} microlotes ===")

        temp_prompt.write_text(cfg["prompt"], encoding="utf-8")
        expected_cols = len(cfg["headers"])

        for bi, batch in enumerate(batches, start=1):
            out_md = LOTES_DIR / f"{serie}_lote_{bi:02d}.md"
            if not args.force and out_md.exists() and parse_md_table(out_md.read_text(encoding="utf-8"), expected_cols):
                logger.info(f"  [{serie} {bi}/{len(batches)}] Ya existe {out_md.name}, omitiendo.")
                continue

            first_t = batch[0].get("title", "")
            last_t = batch[-1].get("title", "")
            sids = [s["id"] for s in batch if s.get("id")] + non_img_ids

            ans = None
            for attempt in range(1, 4):
                logger.info(f"  [{serie} {bi}/{len(batches)}] {first_t}..{last_t} (intento {attempt}/3)...")
                ans, is_auth, err = run_single_ask(cli_path, n_id, temp_prompt, sids, expected_cols, timeout_sec=240)
                if ans:
                    out_md.write_text(ans + "\n", encoding="utf-8")
                    n_rows = len(parse_md_table(ans, expected_cols))
                    logger.info(f"    -> OK! {n_rows} filas guardadas en {out_md.name}")
                    break
                logger.warning(f"    -> Fallo: {err}")
                if is_auth:
                    refresh_token(cli_path)
                elif is_rate_limit_error(err):
                    wait_s = 90 * attempt
                    logger.warning(f"    -> Rate limit; esperando {wait_s}s...")
                    time.sleep(wait_s)
                else:
                    time.sleep(10 * attempt)

            if not ans:
                failed.append(f"{serie}_lote_{bi:02d}")
                if is_rate_limit_error(err):
                    logger.error("[VENTANA 5H NOTEBOOKLM] Límite de cuota alcanzado. Deteniendo limpiamente (progreso guardado; reanuda tras el reset).")
                    merge_and_integrate(series_list)
                    sys.exit(2)
            time.sleep(args.pause)

    merge_and_integrate(series_list)
    if failed:
        logger.error(f"Lotes fallidos (reanudables ejecutando de nuevo): {failed}")
        sys.exit(1)
    logger.info("Proceso completado al 100%.")


if __name__ == "__main__":
    main()
