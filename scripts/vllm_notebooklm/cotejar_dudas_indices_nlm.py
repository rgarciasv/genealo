"""
Cotejo automático de dudas y alertas de los CSV de Índices de San Juan del Molinillo
contra los libros sacramentales originales alojados en NotebookLM Pro (coste $0 de API).

- Lee JMOL_INDICE_BAUTISMOS_1750_1921_bautismos.csv y JMOL_INDICE_CASADOS_1716_1920_casados.csv.
- Filtra filas con duda=True o alerta_auditoria != "" cuyo año/libro tenga cuaderno en NotebookLM.
- Agrupa por cuaderno destino en lotes de 20 filas, consulta a NotebookLM y guarda cada lote
  en htr_pipeline/outputs/cotejo_dudas_nlm/lotes/ (100% reanudable).
- Aplica las correcciones generando CSVs verificados (*_VERIFICADO_NLM.csv) conservando
  las lecturas originales en columnas `*_orig` para trazabilidad ecdótica completa.

Uso:
  .\\venv\\Scripts\\python.exe scripts/vllm_notebooklm/cotejar_dudas_indices_nlm.py --dry-run
  .\\venv\\Scripts\\python.exe scripts/vllm_notebooklm/cotejar_dudas_indices_nlm.py --serie bautismos
  .\\venv\\Scripts\\python.exe scripts/vllm_notebooklm/cotejar_dudas_indices_nlm.py --apply-only
"""

import argparse
import csv
import json
import logging
import re
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("scripts/vllm_notebooklm/cotejar_dudas_indices.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("CotejoDudasNLM")

OUT_ROOT = Path("htr_pipeline/outputs/cotejo_dudas_nlm")
LOTES_DIR = OUT_ROOT / "lotes"
LOTES_DIR.mkdir(parents=True, exist_ok=True)

CSV_PATHS = {
    "bautismos": Path("htr_pipeline/outputs/indice_jmol_bautismos/JMOL_INDICE_BAUTISMOS_1750_1921_bautismos.csv"),
    "casados": Path("htr_pipeline/outputs/indice_jmol_casados/JMOL_INDICE_CASADOS_1716_1920_casados.csv"),
}

DEFAULT_NOTEBOOK_IDS = {
    "JMOL-BAUT-01": "fa62871d-cb66-4af4-8e13-4dcc1c12b7ce",
    "JMOL-BAUT-02": "ad39ba03-d91f-4357-a4cd-bc845ff5f5d4",
    "JMOL-BAUT-03": "8816402f-ccce-4ebe-95a1-eb337e8a367a",
    "JMOL-BAUT-04": "303c70ed-bdd5-4570-a19a-08ebb945bdf5",
    "JMOL-BAUT-05": "7f64917d-d8d1-45a0-b8c2-dfe0314a48d1",
    "JMOL-MATR-01": "50e8d7d8-7afe-4d70-9a8e-e22cc2cc1101",
    "JMOL-MATR-02": "772135ac-4305-4a22-ad89-bf996f0ff37a",
    "JMOL-MATR-03": "07a61f80-24e6-484e-af57-ebe19d09960a",
}


def load_notebook_ids() -> dict[str, str]:
    ids = dict(DEFAULT_NOTEBOOK_IDS)
    ckpt = Path("scripts/vllm_notebooklm/ingest_checkpoint_jmol.json")
    if ckpt.exists():
        data = json.loads(ckpt.read_text(encoding="utf-8"))
        ids.update(data.get("notebook_ids", {}))
    return ids


def route_row_to_notebook(serie: str, row: dict) -> str | None:
    y_str = (row.get("anio_resuelto") or "").strip()
    if not y_str.isdigit():
        return None
    y = int(y_str)
    lib = (row.get("libro_resuelto") or "").strip().lower()
    fol_str = re.sub(r"\D+", "", row.get("folio_literal") or "")
    fol = int(fol_str) if fol_str.isdigit() else 0

    if serie == "bautismos":
        if y <= 1751:
            return "JMOL-BAUT-01"
        if y <= 1800:
            return "JMOL-BAUT-02"
        if y <= 1833:
            return "JMOL-BAUT-03"
        if y == 1834:
            return "JMOL-BAUT-04" if fol >= 286 else "JMOL-BAUT-03"
        if y <= 1850:
            return "JMOL-BAUT-04"
        if y in (1851, 1852):
            if "4" in lib or (0 < fol < 150):
                return "JMOL-BAUT-05"
            return "JMOL-BAUT-04"
        if y <= 1862:
            return "JMOL-BAUT-05"
        return None

    if serie == "casados":
        if y <= 1789:
            return "JMOL-MATR-01"
        if y <= 1850:
            return "JMOL-MATR-02"
        if y in (1851, 1852):
            if "3" in lib or (0 < fol < 50):
                return "JMOL-MATR-03"
            return "JMOL-MATR-02"
        if y <= 1899:
            return "JMOL-MATR-03"
        return None

    return None


def is_flagged(row: dict) -> bool:
    is_d = (row.get("duda") or "").strip().lower() in ("true", "1", "si", "sí")
    is_a = bool((row.get("alerta_auditoria") or "").strip())
    return is_d or is_a


def build_prompt(serie: str, nb_name: str, batch: list[dict]) -> str:
    if serie == "bautismos":
        lines = [
            f"Actúa como paleógrafo y archivero experto. Coteja las siguientes {len(batch)} entradas del índice de Bautismos contra las partidas ORIGINALES de este cuaderno ({nb_name}).",
            "",
            "Para cada `fila_global`, busca la partida correspondiente por año, folio aproximado (puede haber desfase de ±10 folios o de centena `2xx`↔`3xx`) y nombres de padres/bautizado.",
            "",
            "Devuelve **ÚNICAMENTE una tabla Markdown estricta** con EXACTAMENTE estas 8 columnas:",
            "| fila_global | estado | nombre_corregido | padres_corregidos | anio_real | folio_real | vuelto_real | imagen_jpg | nota |",
            "",
            "Valores permitidos en `estado`: `OK` (coincide), `CORREGIDO` (encontrado con corrección de nombre/padres/año/folio), `NO_ENCONTRADO`.",
            "Usa exactamente 9 columnas (las 9 indicadas arriba) y no omitas ninguna `fila_global`.",
            "",
            "ENTRADAS A COTEJAR:",
            "| fila_global | nombre_indice | padres_indice | anio | folio | motivo_o_alerta |",
            "| :---: | :--- | :--- | :---: | :---: | :--- |",
        ]
        for r in batch:
            motivo = " / ".join(x for x in [r.get("motivo", ""), r.get("alerta_auditoria", "")] if x)
            lines.append(
                f"| {r['fila_global']} | {r.get('nombre_bautizado','')} | {r.get('padres','')} | "
                f"{r.get('anio_resuelto','')} | {r.get('folio_literal','')} {r.get('vuelto','')} | {motivo} |"
            )
        return "\n".join(lines)

    # casados
    lines = [
        f"Actúa como paleógrafo y archivero experto. Coteja las siguientes {len(batch)} entradas del índice de Matrimonios contra las partidas ORIGINALES de este cuaderno ({nb_name}).",
        "",
        "Para cada `fila_global`, busca la partida correspondiente por año, folio aproximado y nombres de los contrayentes.",
        "",
        "Devuelve **ÚNICAMENTE una tabla Markdown estricta** con EXACTAMENTE estas 9 columnas:",
        "| fila_global | estado | novio_corregido | novia_corregida | estado_pareja_real | anio_real | folio_real | imagen_jpg | nota |",
        "",
        "Valores permitidos en `estado`: `OK`, `CORREGIDO`, `NO_ENCONTRADO`. No omitas ninguna `fila_global`.",
        "",
        "ENTRADAS A COTEJAR:",
        "| fila_global | novio_indice | novia_indice | anio | folio | motivo_o_alerta |",
        "| :---: | :--- | :--- | :---: | :---: | :--- |",
    ]
    for r in batch:
        motivo = " / ".join(x for x in [r.get("motivo", ""), r.get("alerta_auditoria", "")] if x)
        lines.append(
            f"| {r['fila_global']} | {r.get('novio','')} | {r.get('novia','')} | "
            f"{r.get('anio_resuelto','')} | {r.get('folio_literal','')} | {motivo} |"
        )
    return "\n".join(lines)


def parse_md_table(text: str, expected_cols: int = 9) -> list[list[str]]:
    rows = []
    header_seen = False
    sep_seen = False
    for line in text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not header_seen:
            if any("fila_global" in c.lower() for c in cells):
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


def refresh_token(cli_path: Path):
    logger.info("[REGLA L-21] Renovando sesión de NotebookLM...")
    try:
        subprocess.run([str(cli_path), "login"], capture_output=True, text=True, timeout=90)
        time.sleep(5)
    except Exception as e:
        logger.error(f"Error renovando token: {e}")


def is_auth_error(text: str) -> bool:
    low = text.lower()
    return any(kw in low for kw in ("authentication", "signed-out", "signed out", "login", "unauthorized", "401", "cookie", "expired"))


def is_rate_limit_error(text: str) -> bool:
    low = text.lower()
    return "rate limited" in low or "rejected by the api" in low or "429" in low


def ask_nlm(cli_path: Path, n_id: str, prompt_file: Path, timeout_sec: int = 240) -> tuple[str | None, bool, str]:
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
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout_sec + 40)
        if res.returncode == 0:
            try:
                ans = (json.loads(res.stdout).get("answer") or "").strip()
            except json.JSONDecodeError:
                ans = res.stdout.strip()
            if parse_md_table(ans, 9):
                return ans, False, ""
            return None, False, f"Sin tabla válida ({len(ans)} chars)"
        err = ((res.stderr or "") + "\n" + (res.stdout or "")).strip()
        return None, is_auth_error(err), err[:300]
    except subprocess.TimeoutExpired:
        return None, False, f"Timeout ({timeout_sec + 40}s)"
    except Exception as e:
        return None, False, str(e)


def apply_corrections(serie: str):
    src_csv = CSV_PATHS[serie]
    out_csv = src_csv.with_name(src_csv.stem + "_VERIFICADO_NLM.csv")
    fixes: dict[str, list[str]] = {}
    for lf in sorted(LOTES_DIR.glob(f"{serie}_*_lote_*.md")):
        for row in parse_md_table(lf.read_text(encoding="utf-8"), 9):
            fg = re.sub(r"\D+", "", row[0])
            if fg:
                fixes[fg] = row

    with open(src_csv, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    extra_cols = ["estado_cotejo_nlm", "lectura_original_indice", "imagen_partida_nlm", "nota_cotejo_nlm"]
    for c in extra_cols:
        if c not in fieldnames:
            fieldnames.append(c)

    n_ok = n_corr = n_miss = 0
    for r in rows:
        fg = str(r.get("fila_global", "")).strip()
        r.setdefault("estado_cotejo_nlm", "")
        r.setdefault("lectura_original_indice", "")
        r.setdefault("imagen_partida_nlm", "")
        r.setdefault("nota_cotejo_nlm", "")
        if fg not in fixes:
            continue
        fix = fixes[fg]
        estado = fix[1].upper()
        r["estado_cotejo_nlm"] = estado
        r["imagen_partida_nlm"] = fix[7]
        r["nota_cotejo_nlm"] = fix[8]
        if "CORREG" in estado:
            n_corr += 1
            if serie == "bautismos":
                r["lectura_original_indice"] = f"{r.get('nombre_bautizado','')} | {r.get('padres','')} | {r.get('anio_resuelto','')} | {r.get('folio_literal','')}"
                if fix[2]:
                    r["nombre_bautizado"] = fix[2]
                if fix[3]:
                    r["padres"] = fix[3]
                if fix[4]:
                    r["anio_resuelto"] = fix[4]
                if fix[5]:
                    r["folio_literal"] = fix[5]
                if fix[6]:
                    r["vuelto"] = fix[6]
            else:
                r["lectura_original_indice"] = f"{r.get('novio','')} & {r.get('novia','')} | {r.get('anio_resuelto','')} | {r.get('folio_literal','')}"
                if fix[2]:
                    r["novio"] = fix[2]
                if fix[3]:
                    r["novia"] = fix[3]
                if fix[4]:
                    r["estado_pareja"] = fix[4]
                if fix[5]:
                    r["anio_resuelto"] = fix[5]
                if fix[6]:
                    r["folio_literal"] = fix[6]
        elif "OK" in estado:
            n_ok += 1
        else:
            n_miss += 1

    with open(out_csv, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, delimiter=";")
        w.writeheader()
        w.writerows(rows)
    logger.info(f"[{serie.upper()}] Escrito {out_csv} | OK={n_ok} | CORREGIDO={n_corr} | NO_ENCONTRADO={n_miss}")


def main():
    parser = argparse.ArgumentParser(description="Cotejar dudas/alertas de índices contra NotebookLM.")
    parser.add_argument("--serie", choices=["bautismos", "casados", "all"], default="all")
    parser.add_argument("--batch-size", type=int, default=20, help="Filas por consulta a NotebookLM.")
    parser.add_argument("--dry-run", action="store_true", help="Mostrar el plan de lotes sin consultar NotebookLM.")
    parser.add_argument("--apply-only", action="store_true", help="Solo aplicar lotes ya descargados.")
    parser.add_argument("--force", action="store_true", help="Re-ejecutar lotes ya guardados.")
    parser.add_argument("--pause", type=int, default=8)
    args = parser.parse_args()

    series_list = ["bautismos", "casados"] if args.serie == "all" else [args.serie]

    if args.apply_only:
        for s in series_list:
            apply_corrections(s)
        return

    nb_ids = load_notebook_ids()
    cli_path = Path("venv/Scripts/notebooklm.exe").resolve()
    temp_prompt = Path("scripts/vllm_notebooklm/temp_cotejo_prompt.txt").resolve()

    plan: list[tuple[str, str, str, int, list[dict]]] = []
    for serie in series_list:
        with open(CSV_PATHS[serie], encoding="utf-8-sig", newline="") as f:
            rows = list(csv.DictReader(f, delimiter=";"))
        by_nb: dict[str, list[dict]] = defaultdict(list)
        for r in rows:
            if not is_flagged(r):
                continue
            nb = route_row_to_notebook(serie, r)
            if nb and nb in nb_ids:
                by_nb[nb].append(r)
        for nb in sorted(by_nb):
            lst = by_nb[nb]
            for i in range(0, len(lst), args.batch_size):
                lote_idx = (i // args.batch_size) + 1
                plan.append((serie, nb, nb_ids[nb], lote_idx, lst[i : i + args.batch_size]))

    logger.info(f"Plan total de cotejo: {len(plan)} consultas a NotebookLM (lotes de <= {args.batch_size} filas).")
    summary = defaultdict(int)
    for serie, nb, _, _, batch in plan:
        summary[(serie, nb)] += len(batch)
    for (serie, nb), cnt in sorted(summary.items()):
        logger.info(f"  - {serie:10s} | {nb:14s} -> {cnt:3d} filas marcadas")

    if args.dry_run:
        return

    failed = []
    for idx, (serie, nb, n_id, lote_idx, batch) in enumerate(plan, start=1):
        out_md = LOTES_DIR / f"{serie}_{nb}_lote_{lote_idx:02d}.md"
        if not args.force and out_md.exists() and parse_md_table(out_md.read_text(encoding="utf-8"), 9):
            logger.info(f"[{idx}/{len(plan)}] Ya existe {out_md.name}, omitiendo.")
            continue

        temp_prompt.write_text(build_prompt(serie, nb, batch), encoding="utf-8")
        ans = None
        for attempt in range(1, 4):
            logger.info(f"[{idx}/{len(plan)}] {serie} / {nb} lote {lote_idx} ({len(batch)} filas, intento {attempt}/3)...")
            ans, is_auth, err = ask_nlm(cli_path, n_id, temp_prompt, timeout_sec=240)
            if ans:
                out_md.write_text(ans + "\n", encoding="utf-8")
                logger.info(f"  -> OK! Guardado {out_md.name} ({len(parse_md_table(ans, 9))} filas)")
                break
            logger.warning(f"  -> Fallo: {err}")
            if is_auth:
                refresh_token(cli_path)
            elif is_rate_limit_error(err):
                wait_s = 90 * attempt
                logger.warning(f"  -> Rate limit; esperando {wait_s}s...")
                time.sleep(wait_s)
            else:
                time.sleep(10 * attempt)

        if not ans:
            failed.append(out_md.name)
            if is_rate_limit_error(err):
                logger.error("[VENTANA 5H NOTEBOOKLM] Límite de cuota alcanzado. Deteniendo limpiamente (progreso guardado; reanuda tras el reset).")
                for serie in series_list:
                    apply_corrections(serie)
                sys.exit(2)
        time.sleep(args.pause)

    for serie in series_list:
        apply_corrections(serie)

    if failed:
        logger.error(f"Lotes fallidos (reanudables): {failed}")
        sys.exit(1)
    logger.info("Cotejo completado al 100%.")


if __name__ == "__main__":
    main()
