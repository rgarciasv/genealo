import json
import logging
import subprocess
import sys
import time
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("scripts/audit_codicological.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("CodicologicalAudit")

OUTPUT_DIR = Path("transcripciones/auditoria_codicologica")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PROMPT_BAUT = """Necesito estas tres cosas:
1) Dime si hay algo en el cuaderno que no sean partidas bautismales (bautismos) e indicame que es y el nombre de la fuente (fuentes) donde esta (portadas, autos de visita pastoral, notas al margen, otros sacramentos, licencias, confirmaciones, misas, etc.).
2) Dime cual es la fecha de la primera partida de bautismo (dia/mes/ano) y el nombre de esa imagen, y dime cual es la fecha de la ultima partida de bautismo (dia/mes/ano) y el nombre de la imagen de la fuente.
3) Dime el nombre de la primera imagen del cuaderno y de la ultima (teniendo en cuenta el orden alfabetico por nombre de archivo).

Devuelveme los resultados en formato markdown limpio y estructurado."""

PROMPT_MATR = """Necesito estas tres cosas:
1) Dime si hay algo en el cuaderno que no sean partidas matrimoniales (casados/velaciones) e indicame que es y el nombre de la fuente (fuentes) donde esta (portadas, autos de visita pastoral, notas al margen, otros sacramentos, dispensas, etc.).
2) Dime cual es la fecha de la primera partida de matrimonio (dia/mes/ano) y el nombre de esa imagen, y dime cual es la fecha de la ultima partida de matrimonio (dia/mes/ano) y el nombre de la imagen de la fuente.
3) Dime el nombre de la primera imagen del cuaderno y de la ultima (teniendo en cuenta el orden alfabetico por nombre de archivo).

Devuelveme los resultados en formato markdown limpio y estructurado."""

PROMPT_DIFU = """Necesito estas tres cosas:
1) Dime si hay algo en el cuaderno que no sean partidas de defuncion o entierro (finados) e indicame que es y el nombre de la fuente (fuentes) donde esta (portadas, autos de visita pastoral, notas al margen, otros sacramentos, testamentos, etc.).
2) Dime cual es la fecha de la primera partida de defuncion/entierro (dia/mes/ano) y el nombre de esa imagen, y dime cual es la fecha de la ultima partida de defuncion/entierro (dia/mes/ano) y el nombre de la imagen de la fuente.
3) Dime el nombre de la primera imagen del cuaderno y de la ultima (teniendo en cuenta el orden alfabetico por nombre de archivo).

Devuelveme los resultados en formato markdown limpio y estructurado."""

PROMPT_INDICE = """Necesito estas tres cosas:
1) Dime que tipo de indice o documentos contiene el cuaderno (si hay partidas sacramentales completas o solo indices/asientos alfabeticos o cronologicos, bautismos, matrimonios, defunciones) y el nombre de las fuentes clave donde cambia de seccion.
2) Dime cual es el rango de anos que cubre el indice, la primera entrada (fecha o ano) y su imagen, y la ultima entrada (fecha o ano) y su imagen.
3) Dime el nombre de la primera imagen del cuaderno y de la ultima (teniendo en cuenta el orden alfabetico por nombre de archivo).

Devuelveme los resultados en formato markdown limpio y estructurado."""

PROMPT_MIXTO = """Necesito estas tres cosas:
1) Dime que tipos de documentos o sacramentos contiene el cuaderno (bautismos, matrimonios, defunciones, visitas pastorales, etc.) y los rangos exactos de imagenes donde se encuentra cada tipo o seccion sacramental.
2) Dime las fechas de inicio y fin de cada seccion sacramental y los nombres de las imagenes de la fuente donde empiezan y terminan.
3) Dime el nombre de la primera imagen del cuaderno y de la ultima (teniendo en cuenta el orden alfabetico por nombre de archivo).

Devuelveme los resultados en formato markdown limpio y estructurado."""


def get_prompt_for_notebook(name: str) -> str:
    upper = name.upper()
    if "INDICE" in upper:
        return PROMPT_INDICE
    elif "MIXTO" in upper:
        return PROMPT_MIXTO
    elif "BAUT" in upper:
        return PROMPT_BAUT
    elif "MATR" in upper:
        return PROMPT_MATR
    elif "DIFU" in upper:
        return PROMPT_DIFU
    return PROMPT_MIXTO


def refresh_token(cli_path: Path):
    logger.info("[REGLA L-21] Refreshing NotebookLM session via persistent profile...")
    try:
        res = subprocess.run([str(cli_path), "login"], capture_output=True, text=True, timeout=60)
        logger.info(f"[REGLA L-21] Login output: {res.stdout.strip()}")
        time.sleep(5)
    except Exception as e:
        logger.error(f"[REGLA L-21] Error refreshing token: {e}")


def load_notebooks():
    notebooks = []

    # JMOL
    jmol_path = Path("scripts/ingest_checkpoint_jmol.json")
    if jmol_path.exists():
        with open(jmol_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for name, n_id in data.get("notebook_ids", {}).items():
                notebooks.append(("JMOL", name, n_id))

    # NRDL
    nrdl_path = Path("scripts/ingest_checkpoint_nrdl.json")
    if nrdl_path.exists():
        with open(nrdl_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            for name, n_id in data.get("notebook_ids", {}).items():
                notebooks.append(("NRDL", name, n_id))

    return notebooks


def main():
    notebooks = load_notebooks()
    logger.info(f"Loaded {len(notebooks)} total notebooks across JMOL and NRDL.")

    cli_path = Path("venv/Scripts/notebooklm.exe").resolve()
    temp_prompt_file = Path("scripts/temp_audit_prompt.txt").resolve()

    pending = []
    for parish, name, n_id in notebooks:
        out_file = OUTPUT_DIR / f"{name}.md"
        if out_file.exists():
            logger.info(f"Skipping already audited: {name}")
        else:
            pending.append((parish, name, n_id, out_file))

    logger.info(f"Found {len(pending)} notebooks pending codicological audit.")

    for i, (parish, name, n_id, out_file) in enumerate(pending, start=1):
        prompt = get_prompt_for_notebook(name)
        with open(temp_prompt_file, "w", encoding="utf-8") as f:
            f.write(prompt)

        logger.info(f"[{i}/{len(pending)}] Auditing {name} ({n_id}) via NotebookLM...")

        cmd = [
            str(cli_path),
            "ask",
            "-n",
            n_id,
            "--prompt-file",
            str(temp_prompt_file),
            "--timeout",
            "300",
        ]

        retries = 3
        success = False
        while retries > 0 and not success:
            try:
                res = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=340,
                )
                if res.returncode == 0:
                    answer = res.stdout.strip()
                    lines = answer.split("\n")
                    clean_lines = []
                    skip_header = True
                    for line in lines:
                        if skip_header:
                            if line.startswith("Answer:"):
                                skip_header = False
                                continue
                            elif (
                                line.startswith("Continuing conversation")
                                or line.startswith("Resumed conversation")
                            ):
                                continue
                            elif line.strip() == "":
                                continue
                            else:
                                skip_header = False
                        clean_lines.append(line)

                    clean_answer = "\n".join(clean_lines).strip()
                    if not clean_answer:
                        clean_answer = answer

                    # Format Markdown
                    md_content = f"# Auditoría Codicológica: {name}\n"
                    md_content += f"**Parroquia:** {parish}\n"
                    md_content += f"**Notebook ID:** `{n_id}`\n"
                    md_content += f"**Fecha Auditoría:** 2026-11-01\n\n---\n\n"
                    md_content += clean_answer + "\n"

                    with open(out_file, "w", encoding="utf-8") as f:
                        f.write(md_content)

                    logger.info(f"  -> SUCCESS! Saved audit to {out_file.name}")
                    success = True
                else:
                    err_msg = res.stderr
                    logger.error(f"  -> CLI Error (code {res.returncode}): {err_msg[:200]}")
                    if "Authentication" in err_msg or "signed-out" in err_msg or "login" in err_msg:
                        refresh_token(cli_path)
                    retries -= 1
                    time.sleep(10)
            except subprocess.TimeoutExpired:
                logger.warning(f"  -> Timeout (340s) querying {name}. Retrying in 15 seconds...")
                retries -= 1
                time.sleep(15)
            except Exception as e:
                logger.error(f"  -> Exception: {e}")
                retries -= 1
                time.sleep(10)

        # Politeness pause between notebooks
        time.sleep(8)

    logger.info("Codicological audit pipeline completed.")


if __name__ == "__main__":
    main()
