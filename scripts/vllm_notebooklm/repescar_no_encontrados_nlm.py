"""Repesca dirigida en NotebookLM de filas NO_ENCONTRADO y pendientes (JMOL).

Usa ventanas exactas de imágenes JPG (-s) identificadas tras la primera pasada
de cotejo, ejecutando las consultas secuencialmente (Regla L-45) y guardando
cada micro-lote en `htr_pipeline/outputs/cotejo_dudas_nlm/lotes/` para su
fusión automática con `cotejar_dudas_indices_nlm.py --apply-only`.
"""

from __future__ import annotations

import csv
import logging
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))

from cotejar_dudas_indices_nlm import (  # noqa: E402
    CSV_PATHS,
    DEFAULT_NOTEBOOK_IDS as NOTEBOOKS,
    LOTES_DIR,
    ask_nlm,
    build_prompt,
    get_notebook_sources,
    is_rate_limit_error,
    refresh_token,
)

CLI_PATH = ROOT / "venv" / "Scripts" / "notebooklm.exe"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("repesca_nlm")

REPESCA_JOBS: list[dict] = [
    # --- CASADOS (8 consultas, 21 filas) ---
    {
        "serie": "casados",
        "tag": "repesca_01_matr01_1740",
        "nb": "JMOL-MATR-01",
        "img_start": 58,
        "img_end": 66,
        "filas": ["91", "92", "93", "94", "99"],
        "pista": "Fols. 108-116 (años 1740-1743), justo antes de la imagen 00066 (fol. 117).",
    },
    {
        "serie": "casados",
        "tag": "repesca_02_matr01_1762",
        "nb": "JMOL-MATR-01",
        "img_start": 120,
        "img_end": 128,
        "filas": ["188", "189"],
        "pista": "Año 1762, justo después de la imagen 00120 (fol. 226).",
    },
    {
        "serie": "casados",
        "tag": "repesca_03_matr02_1794",
        "nb": "JMOL-MATR-02",
        "img_start": 202,
        "img_end": 207,
        "filas": ["322", "325"],
        "pista": "Fols. 7-8 (1794-1795), justo antes de la imagen 00207 (fol. 9v).",
    },
    {
        "serie": "casados",
        "tag": "repesca_04_matr02_1824",
        "nb": "JMOL-MATR-02",
        "img_start": 243,
        "img_end": 263,
        "filas": ["495", "514"],
        "pista": "Fol. 49 (1824) y fol. 57 (1829), antes de fol. 65v.",
    },
    {
        "serie": "casados",
        "tag": "repesca_05_matr03_1853",
        "nb": "JMOL-MATR-03",
        "img_start": 332,
        "img_end": 347,
        "filas": ["673", "676", "684", "687"],
        "pista": "Fols. 7-12 (1853-1855), antes de la imagen 00348 (fol. 18).",
    },
    {
        "serie": "casados",
        "tag": "repesca_06_matr03_1870",
        "nb": "JMOL-MATR-03",
        "img_start": 394,
        "img_end": 406,
        "filas": ["793", "813"],
        "pista": "Fol. 62 (1870) y fol. 71 o anterior (1871; en 00406 ya es nov. 1872).",
    },
    {
        "serie": "casados",
        "tag": "repesca_07_matr03_1884",
        "nb": "JMOL-MATR-03",
        "img_start": 450,
        "img_end": 461,
        "filas": ["923", "931", "934"],
        "pista": "Fols. 120-126 (1884), antes de 00461 (fol. 128v).",
    },
    {
        "serie": "casados",
        "tag": "repesca_08_matr03_1898",
        "nb": "JMOL-MATR-03",
        "img_start": 514,
        "img_end": 518,
        "filas": ["1062"],
        "pista": "Fol. 184 (1898), justo después de 00515 (fol. 183).",
    },
    # --- BAUTISMOS (15 consultas, 31 filas; omite 2013, 833, 1065 y BAUT-05 local) ---
    {
        "serie": "bautismos",
        "tag": "repesca_01_baut02_1756",
        "nb": "JMOL-BAUT-02",
        "img_start": 1811,
        "img_end": 1816,
        "filas": ["2128", "2129", "2130"],
        "pista": "Fols. 38 y 38v (1756), justo después del fol. 36r.",
    },
    {
        "serie": "bautismos",
        "tag": "repesca_02_baut02_1762",
        "nb": "JMOL-BAUT-02",
        "img_start": 1844,
        "img_end": 1849,
        "filas": ["2971", "4731"],
        "pista": "Fols. 71v y 72v (1762), justo después de 01844 (fol. 70r).",
    },
    {
        "serie": "bautismos",
        "tag": "repesca_03_baut02_1800",
        "nb": "JMOL-BAUT-02",
        "img_start": 2044,
        "img_end": 2049,
        "filas": ["3878", "4761"],
        "pista": "Final del libro (1800), fol. 274 y posible resto tras julio 1800 (fols. 268-274).",
    },
    {
        "serie": "bautismos",
        "tag": "repesca_04_baut03_1801",
        "nb": "JMOL-BAUT-03",
        "img_start": 2051,
        "img_end": 2060,
        "filas": ["3196", "3197", "2754", "1169", "2250"],
        "pista": "Arranque 1801-1802 (fols. 2-5v); verificar nota de 1981 en 02052 sobre Libro 3º bis.",
    },
    {
        "serie": "bautismos",
        "tag": "repesca_05_baut03_1804",
        "nb": "JMOL-BAUT-03",
        "img_start": 2063,
        "img_end": 2083,
        "filas": ["1994", "2762"],
        "pista": "1804 (fols. 11-16v) y 1806/1808 (fol. 27).",
    },
    {
        "serie": "bautismos",
        "tag": "repesca_06_baut03_1814",
        "nb": "JMOL-BAUT-03",
        "img_start": 2104,
        "img_end": 2110,
        "filas": ["2004", "1462"],
        "pista": "Fols. 54v y 55 (1814), justo antes de 02110 (fol. 57v).",
    },
    {
        "serie": "bautismos",
        "tag": "repesca_07_baut03_1818",
        "nb": "JMOL-BAUT-03",
        "img_start": 2123,
        "img_end": 2133,
        "filas": ["4023", "4952", "3287"],
        "pista": "Fols. 75, 75v y 78v (1818), antes de 02133 (fol. 81r).",
    },
    {
        "serie": "bautismos",
        "tag": "repesca_08_baut03_1829",
        "nb": "JMOL-BAUT-03",
        "img_start": 2205,
        "img_end": 2216,
        "filas": ["1190"],
        "pista": "Fol. 230 (1829), antes de fol. 232v.",
    },
    {
        "serie": "bautismos",
        "tag": "repesca_09_baut03_1834",
        "nb": "JMOL-BAUT-03",
        "img_start": 2235,
        "img_end": 2239,
        "filas": ["2025"],
        "pista": "Fol. 285 (1834, posible errata 295 por 285) al final de JMOL-BAUT-03.",
    },
    {
        "serie": "bautismos",
        "tag": "repesca_10_baut04_1834",
        "nb": "JMOL-BAUT-04",
        "img_start": 2240,
        "img_end": 2244,
        "filas": ["3377"],
        "pista": "Fol. 287 (1834) al inicio de JMOL-BAUT-04, antes de fol. 292v.",
    },
    {
        "serie": "bautismos",
        "tag": "repesca_11_baut04_1839",
        "nb": "JMOL-BAUT-04",
        "img_start": 2273,
        "img_end": 2282,
        "filas": ["3395", "1822"],
        "pista": "Fols. 320v y 323/326 (1839), antes de 02281 (fol. 325v).",
    },
    {
        "serie": "bautismos",
        "tag": "repesca_12_baut04_1842",
        "nb": "JMOL-BAUT-04",
        "img_start": 2304,
        "img_end": 2316,
        "filas": ["2792"],
        "pista": "Año 1842, fol. ~351-361 (posible errata de índice 381v por 351).",
    },
    {
        "serie": "bautismos",
        "tag": "repesca_13_baut04_1848",
        "nb": "JMOL-BAUT-04",
        "img_start": 2370,
        "img_end": 2373,
        "filas": ["4597"],
        "pista": "Fol. 416v (1848), justo antes de 02372.",
    },
    {
        "serie": "bautismos",
        "tag": "repesca_14_baut04_1850a",
        "nb": "JMOL-BAUT-04",
        "img_start": 2395,
        "img_end": 2400,
        "filas": ["2800", "1536", "3435"],
        "pista": "Fols. 441-443 (1850), pendiente de verificar en JMOL-BAUT-04.",
    },
    {
        "serie": "bautismos",
        "tag": "repesca_15_baut04_1850b",
        "nb": "JMOL-BAUT-04",
        "img_start": 2399,
        "img_end": 2404,
        "filas": ["3433", "1535", "3434"],
        "pista": "Fols. 442-446v (1850), pendiente de verificar en JMOL-BAUT-04.",
    },
]


def load_rows_by_fg(serie: str) -> dict[str, dict]:
    with open(CSV_PATHS[serie], encoding="utf-8-sig", newline="") as f:
        return {
            str(r.get("fila_global", "")).strip(): r
            for r in csv.DictReader(f, delimiter=";")
        }


def extract_img_num(title: str) -> int | None:
    m = re.search(r"_(\d+)\.jpg$", title or "", re.IGNORECASE)
    return int(m.group(1)) if m else None


def main() -> int:
    LOTES_DIR.mkdir(parents=True, exist_ok=True)
    prompt_dir = LOTES_DIR.parent / "_tmp_repesca_prompts"
    prompt_dir.mkdir(parents=True, exist_ok=True)

    rows_cache = {
        "casados": load_rows_by_fg("casados"),
        "bautismos": load_rows_by_fg("bautismos"),
    }
    sources_cache: dict[str, tuple[list[dict], list[dict]]] = {}

    refresh_token(CLI_PATH)

    done = 0
    skipped = 0
    failed = 0

    for job in REPESCA_JOBS:
        serie = job["serie"]
        tag = job["tag"]
        nb = job["nb"]
        n_id = NOTEBOOKS[nb]
        out_file = LOTES_DIR / f"{serie}_{tag}.md"

        if out_file.exists() and out_file.stat().st_size > 20:
            logger.info(f"[{tag}] Ya existe ({out_file.name}); omitido.")
            skipped += 1
            continue

        batch = [rows_cache[serie][fg] for fg in job["filas"] if fg in rows_cache[serie]]
        if not batch:
            logger.warning(f"[{tag}] Ninguna fila encontrada en CSV {serie}.")
            continue

        if nb not in sources_cache:
            imgs, non_imgs = get_notebook_sources(CLI_PATH, n_id)
            sources_cache[nb] = (imgs, non_imgs)
            logger.info(f"[{nb}] Fuentes cacheadas: {len(imgs)} imgs, {len(non_imgs)} docs")
        else:
            imgs, non_imgs = sources_cache[nb]

        win_imgs = [
            s for s in imgs
            if (num := extract_img_num(s.get("title", ""))) is not None
            and job["img_start"] <= num <= job["img_end"]
        ]
        sids = [s["id"] for s in win_imgs + non_imgs if s.get("id")]
        logger.info(
            f"[{tag}] Consultando {nb} ({len(batch)} filas) sobre {len(win_imgs)} imgs "
            f"[{job['img_start']:05d}..{job['img_end']:05d}]..."
        )

        prompt_text = build_prompt(serie, nb, batch) + f"\n\nPISTA DE BÚSQUEDA DIRIGIDA: {job['pista']}\n"
        prompt_file = prompt_dir / f"{serie}_{tag}.txt"
        prompt_file.write_text(prompt_text, encoding="utf-8")

        ans, is_auth, err = ask_nlm(CLI_PATH, n_id, prompt_file, source_ids=sids, timeout_sec=240)
        if is_auth:
            refresh_token(CLI_PATH)
            ans, is_auth, err = ask_nlm(CLI_PATH, n_id, prompt_file, source_ids=sids, timeout_sec=240)

        if ans:
            out_file.write_text(ans + "\n", encoding="utf-8")
            logger.info(f"[{tag}] OK guardado en {out_file.name}")
            done += 1
        else:
            logger.error(f"[{tag}] Error: {err}")
            failed += 1
            if is_rate_limit_error(err):
                logger.warning("Rate limit detectado (429). Deteniendo repesca limpiamente.")
                break

        time.sleep(6)

    logger.info(f"Resumen repesca: done={done} skipped={skipped} failed={failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
