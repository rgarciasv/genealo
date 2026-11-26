import argparse
import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("scripts/vllm_notebooklm/censo_manos.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("CensoManos")

OUTPUT_DIR = Path("transcripciones/censo_manos")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

TAXONOMY_BLOCK = """TAXONOMÍA OFICIAL DE 12 CLÚSTERES MORFOGRÁFICOS (C01-C12):
- C01: Gótico-cortesana tardía (1500–1560: trazo anguloso y quebrado, módulo pequeño, líneas muy juntas, alta densidad de abreviaturas medievales y signos tironianos)
- C02: Procesal redonda / abierta (1530–1620: formas curvas y anchas, letras aislables pero con nexos envolventes largos, pluma gruesa de ave)
- C03: Procesal encadenada pura (1560–1650: renglones casi sin levantar la pluma; c, e, n, m, r, s reducidas a ondas similares)
- C04: Humanística / Itálica libraria (1550–1640: vertical o levemente inclinada, letras sueltas casi de imprenta, limpia y sin apenas lazos)
- C05: Híbrida procesal-bastarda (1610–1680: base inclinada de bastarda con ataduras procesales, d unciales vueltas atrás y abreviaturas arcaicas)
- C06: Bastarda cancilleresca / magistral (1660–1780: caja redonda y uniforme, inclinación constante, renglones rectos y separación clara)
- C07: Bastarda angulosa / picuda (1680–1790: módulo comprimido lateralmente, picos agudos y aspecto «aserrado», enlaces rápidos)
- C08: Bastarda corriente / desbordada (1670–1810: ejecución rápida y descuidada, ojales gigantescos que invaden dos renglones, renglón caído y aglutinaciones)
- C09: Micro-cursiva compacta (1650–1830: letra diminuta y empastada por aprovechamiento de espacio o notas marginales)
- C10: Bastarda ilustrada / neoclásica (1770–1840: pluma más fina, limpia, simplificación de abreviaturas y casi sin lazos envolventes)
- C11: Cursiva inglesa / comercial (plumilla metálica) (1840–1899: plumilla metálica, ascendentes finísimos y descendentes gruesos, muy inclinada)
- C12: Rústica / senil o temblorosa (transversal) (trazo roto o tembloroso, manchas de goteo y formas irregulares sin escuela clara)"""

PROMPT_SACRAMENTAL = f"""Actúa como paleógrafo experto y archivero ecdótico. Tu misión es realizar el **Censo Exhaustivo de Manos, Ductus Paleográfico y Volumen de Páginas** examinando TODAS las imágenes `.jpg` de este libro sacramental parroquial (ignora los archivos de instrucciones `00_`..`04_` al indicar nombres de imagen).

{TAXONOMY_BLOCK}

INSTRUCCIONES DE ANÁLISIS:
1. Recorre cronológicamente TODAS las fuentes `.jpg` del cuaderno desde la primera hasta la última.
2. Identifica cada mano / redactor material que escribe las partidas o diligencias (cura propio/titular, teniente de cura, ecónomo, cura sustituto o foráneo de otro pueblo, visitador/secretario de visita pastoral, o mano anónima si no firma).
3. Si una misma mano cambia de tramo tras una sustitución intermedia, o cambia significativamente de ductus/módulo, registra cada tramo continuo con su primera y última imagen `.jpg` exacta para poder calcular el volumen real de páginas. Si solo hay interrupciones puntuales de 1-2 partidas por un sustituto, indica el rango principal del titular y añade una fila propia para el sustituto con su imagen exacta.
4. Indica SIEMPRE los nombres exactos de archivo `.jpg` tal como aparecen en las fuentes (ej. `004298571_01037.jpg`), sin inventar extensiones ni omitir ceros.
5. En la columna `Cluster (C01-C12)` usa el código oficial (`C01`..`C12`; si una mano muestra transición clara o senilidad, puedes anotar p.ej. `C10 -> C12` o `C08 / C09`).

FORMATO DE RESPUESTA OBLIGATORIO:
Devuelve **primero una única tabla Markdown estricta** con EXACTAMENTE estas 10 columnas y encabezados literales:

| Orden | Cura / Redactor Material | Variantes de Firma | Rol y Parroquia (Titular / Teniente / Sustituto foráneo) | Años | Primera Imagen (.jpg) | Última Imagen (.jpg) | N_Folios_Aprox | Cluster (C01-C12) | Rasgos Visuales y Observaciones |

Después de la tabla, incluye un apartado breve con exactamente estas tres subsecciones:
### (a) Curas sustitutos y foráneos detectados
(Menciona nombre, pueblo/parroquia de origen si consta en las partidas, fechas e imágenes `.jpg`).
### (b) Cambios de ductus o envejecimiento de manos (`-> C12`)
(Detalla casos donde un mismo escribano cambia de módulo, pluma o envejece hacia trazo tembloroso `C12`).
### (c) Imágenes `.jpg` más representativas y limpias (3–5 muestras)
(Lista 3–5 archivos `.jpg` con buena legibilidad y contraste de las manos principales de este cuaderno, indicando a qué mano y clúster corresponde cada una)."""

PROMPT_INDICE = f"""Actúa como paleógrafo experto y archivero ecdótico. Este cuaderno es un **Libro Índice parroquial** (índices alfabéticos o cronológicos de partidas sacramentales). Tu misión es realizar el **Censo Exhaustivo de Manos, Ductus Paleográfico y Volumen de Páginas** examinando TODAS las imágenes `.jpg` de este cuaderno (ignora los archivos de instrucciones `00_`..`04_` al indicar nombres de imagen).

{TAXONOMY_BLOCK}

INSTRUCCIONES DE ANÁLISIS:
1. Recorre TODAS las fuentes `.jpg` del cuaderno índice desde la primera hasta la última.
2. Identifica cada mano / redactor material que confeccionó o continuó las distintas secciones del índice (tanto si firma en portadas/diligencias/cierres como si es una mano anónima distinguible por su letra y cronología de asientos añadidos).
3. Indica qué secciones del índice escribe cada mano (ej. letras A–Z de Bautismos, Matrimonios, Defunciones, añadidos posteriores), sus años cubiertos y el rango exacto de imágenes `.jpg` (`Primera Imagen (.jpg)` y `Última Imagen (.jpg)` tal como aparecen en las fuentes, ej. `004298570_01600.jpg`).
4. En la columna `Cluster (C01-C12)` usa el código oficial (`C01`..`C12`).

FORMATO DE RESPUESTA OBLIGATORIO:
Devuelve **primero una única tabla Markdown estricta** con EXACTAMENTE estas 10 columnas y encabezados literales:

| Orden | Cura / Redactor Material | Variantes de Firma | Rol y Parroquia (Titular / Teniente / Sustituto foráneo) | Años | Primera Imagen (.jpg) | Última Imagen (.jpg) | N_Folios_Aprox | Cluster (C01-C12) | Rasgos Visuales y Observaciones |

Después de la tabla, incluye un apartado breve con exactamente estas tres subsecciones:
### (a) Curas sustitutos y foráneos detectados
(Indica si consta autoría de algún cura titular, teniente o sustituto en diligencias o notas del índice; si no consta, indícalo).
### (b) Cambios de ductus o envejecimiento de manos (`-> C12`)
(Detalla si las manos del índice cambian de módulo, tinta/pluma o muestran añadidos posteriores de manos distintas).
### (c) Imágenes `.jpg` más representativas y limpias (3–5 muestras)
(Lista 3–5 archivos `.jpg` con buena legibilidad de las manos principales del índice, indicando a qué mano y clúster corresponde cada una)."""


def get_prompt_for_notebook(name: str) -> str:
    if "INDICE" in name.upper():
        return PROMPT_INDICE
    return PROMPT_SACRAMENTAL


def refresh_token(cli_path: Path):
    logger.info("[REGLA L-21] Refreshing NotebookLM session via persistent profile...")
    try:
        res = subprocess.run(
            [str(cli_path), "login"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=90,
        )
        logger.info(f"[REGLA L-21] Login exit={res.returncode}: {res.stdout.strip()[:200]}")
        time.sleep(5)
    except Exception as e:
        logger.error(f"[REGLA L-21] Error refreshing token: {e}")


def load_notebooks():
    notebooks = []
    seen = set()

    for parish, ckpt_path in [
        ("JMOL", Path("scripts/vllm_notebooklm/ingest_checkpoint_jmol.json")),
        ("NRDL", Path("scripts/vllm_notebooklm/ingest_checkpoint_nrdl.json")),
    ]:
        if not ckpt_path.exists():
            raise FileNotFoundError(f"Checkpoint no encontrado: {ckpt_path}")
        with open(ckpt_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for name, n_id in data.get("notebook_ids", {}).items():
            if "ENSENADA" in name.upper():
                logger.warning(f"Excluyendo cuaderno de Ensenada: {name}")
                continue
            if name in seen:
                continue
            seen.add(name)
            notebooks.append((parish, name, n_id))

    return notebooks


def is_valid_existing_output(path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8", errors="replace").strip()
    if len(text) <= 300:
        return False
    lower = text.lower()
    if "traceback (most recent call last)" in lower or "error:" in lower[:300]:
        return False
    if "| orden" not in lower and "|orden" not in lower:
        return False
    return True


def clean_cli_answer(raw_stdout: str) -> str:
    lines = raw_stdout.strip().splitlines()
    clean_lines = []
    skip_header = True
    for line in lines:
        if skip_header:
            stripped = line.strip()
            if stripped.startswith("Answer:"):
                skip_header = False
                rest = stripped[len("Answer:"):].strip()
                if rest:
                    clean_lines.append(rest)
                continue
            if (
                stripped.startswith("Continuing conversation")
                or stripped.startswith("Resumed conversation")
                or stripped.startswith("Starting new conversation")
                or stripped.startswith("Deleted conversation")
                or stripped == ""
            ):
                continue
            skip_header = False
        if line.strip().startswith("New conversation:"):
            continue
        clean_lines.append(line)

    clean_answer = "\n".join(clean_lines).strip()
    return clean_answer if clean_answer else raw_stdout.strip()


def is_auth_error(text: str) -> bool:
    lower = text.lower()
    return any(
        kw in lower
        for kw in [
            "authentication",
            "signed-out",
            "signed out",
            "login",
            "unauthorized",
            "401",
            "cookie",
            "expired",
        ]
    )


def try_recover_from_history(cli_path: Path, n_id: str) -> str | None:
    """Checks server-side history in case a prior/timed-out ask completed on the server."""
    try:
        res = subprocess.run(
            [str(cli_path), "history", "-n", n_id, "--json"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=60,
        )
        if res.returncode != 0 or not res.stdout.strip():
            return None
        data = json.loads(res.stdout)
        for qa in reversed(data.get("qa_pairs", [])):
            q = qa.get("question", "")
            a = (qa.get("answer") or "").strip()
            if (
                "Censo Exhaustivo de Manos" in q
                and len(a) > 300
                and ("| orden" in a.lower() or "|orden" in a.lower())
            ):
                return a
    except Exception as e:
        logger.debug(f"No se pudo recuperar historial de {n_id}: {e}")
    return None


def get_notebook_sources(cli_path: Path, n_id: str) -> tuple[list[dict], list[dict]]:
    """Fetch notebook sources split into sorted .jpg image sources and non-image grounding sources."""
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


def extract_table_and_sections(answer: str) -> tuple[list[list[str]], dict[str, str]]:
    """Parse Markdown table rows (re-joining wrapped rows) and (a)/(b)/(c) sections."""
    lines = answer.splitlines()
    rows: list[list[str]] = []
    header_seen = False
    sep_seen = False
    buf = ""

    def flush_buf():
        nonlocal buf
        if not buf:
            return
        parts = [c.strip() for c in buf.strip().strip("|").split("|")]
        if len(parts) >= 10:
            rows.append(parts[:10])
        buf = ""

    body_lines: list[str] = []
    in_table = False
    for line in lines:
        s = line.strip()
        if not header_seen and s.startswith("|") and "orden" in s.lower():
            header_seen = True
            in_table = True
            continue
        if header_seen and not sep_seen and s.startswith("|") and set(s.replace("|", "").replace(":", "").replace("-", "").replace(" ", "")) == set():
            sep_seen = True
            continue
        if in_table and sep_seen:
            if s.startswith("|"):
                flush_buf()
                buf = s
                if buf.count("|") >= 11 and buf.endswith("|"):
                    flush_buf()
                continue
            elif buf and not s.startswith("#") and s != "---" and s != "":
                buf += " " + s
                if buf.count("|") >= 11 and buf.endswith("|"):
                    flush_buf()
                continue
            else:
                flush_buf()
                in_table = False
        if not in_table:
            body_lines.append(line)
    flush_buf()

    sections = {"a": "", "b": "", "c": ""}
    current = None
    buf_sec: list[str] = []
    for line in body_lines:
        low = line.strip().lower()
        if low.startswith("### (a)") or low.startswith("## (a)"):
            if current:
                sections[current] = "\n".join(buf_sec).strip()
            current = "a"
            buf_sec = []
        elif low.startswith("### (b)") or low.startswith("## (b)"):
            if current:
                sections[current] = "\n".join(buf_sec).strip()
            current = "b"
            buf_sec = []
        elif low.startswith("### (c)") or low.startswith("## (c)"):
            if current:
                sections[current] = "\n".join(buf_sec).strip()
            current = "c"
            buf_sec = []
        elif current:
            if line.strip() == "---":
                continue
            buf_sec.append(line)
    if current:
        sections[current] = "\n".join(buf_sec).strip()

    return rows, sections


def merge_chunk_answers(chunk_results: list[tuple[str, str]]) -> str:
    """Merge multiple chunked Markdown answers into one unified 10-column table + (a)/(b)/(c) sections."""
    all_rows: list[list[str]] = []
    sec_a, sec_b, sec_c = [], [], []
    for label, ans in chunk_results:
        rows, secs = extract_table_and_sections(ans)
        all_rows.extend(rows)
        if secs["a"]:
            sec_a.append(f"#### {label}\n{secs['a']}")
        if secs["b"]:
            sec_b.append(f"#### {label}\n{secs['b']}")
        if secs["c"]:
            sec_c.append(f"#### {label}\n{secs['c']}")

    out = [
        "### Censo General de Manos y Tramos Redaccionales (consolidado por tramos)",
        "",
        "| Orden | Cura / Redactor Material | Variantes de Firma | Rol y Parroquia (Titular / Teniente / Sustituto foráneo) | Años | Primera Imagen (.jpg) | Última Imagen (.jpg) | N_Folios_Aprox | Cluster (C01-C12) | Rasgos Visuales y Observaciones |",
        "| :---: | :--- | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |",
    ]
    for i, r in enumerate(all_rows, start=1):
        cells = [str(i)] + [c.replace("|", "/") for c in r[1:10]]
        out.append("| " + " | ".join(cells) + " |")

    out.extend([
        "",
        "---",
        "",
        "### (a) Curas sustitutos y foráneos detectados",
        "\n\n".join(sec_a) if sec_a else "Sin datos adicionales.",
        "",
        "### (b) Cambios de ductus o envejecimiento de manos (`-> C12`)",
        "\n\n".join(sec_b) if sec_b else "Sin datos adicionales.",
        "",
        "### (c) Imágenes `.jpg` más representativas y limpias (3–5 muestras)",
        "\n\n".join(sec_c) if sec_c else "Sin datos adicionales.",
    ])
    return "\n".join(out)


def run_single_ask(
    cli_path: Path,
    n_id: str,
    prompt_file: Path,
    source_ids: list[str] | None = None,
    timeout_sec: int = 600,
) -> tuple[str | None, bool, str]:
    """Run one notebooklm ask call. Returns (answer_or_none, is_auth, err_msg)."""
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
    if source_ids:
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
                ans = clean_cli_answer(res.stdout)
            if len(ans) > 300 and ("| orden" in ans.lower() or "|orden" in ans.lower()):
                return ans, False, ""
            return None, False, f"Respuesta incompleta ({len(ans)} chars)"
        err_msg = ((res.stderr or "") + "\n" + (res.stdout or "")).strip()
        return None, is_auth_error(err_msg), err_msg[:300]
    except subprocess.TimeoutExpired:
        return None, False, f"Timeout ({timeout_sec + 40}s)"
    except Exception as e:
        return None, False, str(e)


def run_chunked_census(
    cli_path: Path,
    name: str,
    n_id: str,
    prompt_file: Path,
    chunk_size: int = 90,
) -> str | None:
    """Split a large notebook into chronological <=chunk_size image batches and merge."""
    imgs, non_imgs = get_notebook_sources(cli_path, n_id)
    if len(imgs) <= 100:
        return None
    non_img_ids = [s["id"] for s in non_imgs if s.get("id")]
    batches = [imgs[i : i + chunk_size] for i in range(0, len(imgs), chunk_size)]
    logger.info(f"  -> Activando modo por tramos para {name}: {len(imgs)} imágenes en {len(batches)} lotes de <= {chunk_size}.")

    chunk_results: list[tuple[str, str]] = []
    for bi, batch in enumerate(batches, start=1):
        first_img = batch[0].get("title", f"Lote {bi}")
        last_img = batch[-1].get("title", f"Lote {bi}")
        label = f"Tramo {bi}/{len(batches)} ({first_img} .. {last_img})"
        sids = [s["id"] for s in batch if s.get("id")] + non_img_ids

        ans = None
        for attempt in range(1, 4):
            logger.info(f"    [{label}] intento {attempt}/3 ({len(batch)} imgs)...")
            ans, is_auth, err = run_single_ask(cli_path, n_id, prompt_file, source_ids=sids, timeout_sec=600)
            if ans:
                logger.info(f"    -> {label} OK ({len(ans)} chars)")
                break
            logger.warning(f"    -> {label} fallo: {err}")
            if is_auth:
                refresh_token(cli_path)
            else:
                time.sleep(10)
                rec = try_recover_from_history(cli_path, n_id)
                if rec and first_img[:9] in rec:
                    ans = rec
                    logger.info(f"    -> {label} recuperado del servidor!")
                    break
            time.sleep(10 * attempt)

        if not ans:
            logger.error(f"    -> FALLO en {label} de {name}.")
            return None
        chunk_results.append((label, ans))
        if bi < len(batches):
            time.sleep(5)

    return merge_chunk_answers(chunk_results)


def save_census_md(out_file: Path, name: str, parish: str, n_id: str, answer: str):
    md_content = (
        f"# Censo Paleográfico de Manos: {name}\n"
        f"**Parroquia:** {parish}\n"
        f"**Notebook ID:** `{n_id}`\n"
        f"**Fecha Censo:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        f"---\n\n"
        f"{answer.strip()}\n"
    )
    out_file.write_text(md_content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description="Censo global de manos en los 33 cuadernos parroquiales.")
    parser.add_argument("--only", type=str, default=None, help="Ejecutar solo el cuaderno con este nombre exacto.")
    parser.add_argument("--limit", type=int, default=None, help="Número máximo de cuadernos pendientes a procesar.")
    parser.add_argument("--force", action="store_true", help="Re-ejecutar aunque ya exista salida válida.")
    args = parser.parse_args()

    notebooks = load_notebooks()
    logger.info(f"Cargados {len(notebooks)} cuadernos parroquiales (JMOL + NRDL, sin Ensenada).")

    if args.only:
        notebooks = [nb for nb in notebooks if nb[1] == args.only]
        if not notebooks:
            logger.error(f"Cuaderno no encontrado: {args.only}")
            sys.exit(1)

    cli_path = Path("venv/Scripts/notebooklm.exe").resolve()
    temp_prompt_file = Path("scripts/vllm_notebooklm/temp_censo_manos_prompt.txt").resolve()

    pending = []
    for parish, name, n_id in notebooks:
        out_file = OUTPUT_DIR / f"{name}.md"
        if not args.force and is_valid_existing_output(out_file):
            logger.info(f"Omitiendo ya completado: {name}")
        else:
            pending.append((parish, name, n_id, out_file))

    if args.limit is not None:
        pending = pending[: args.limit]

    logger.info(f"Pendientes de censo paleográfico: {len(pending)} cuaderno(s).")

    failed = []
    for idx, (parish, name, n_id, out_file) in enumerate(pending, start=1):
        prompt = get_prompt_for_notebook(name)
        temp_prompt_file.write_text(prompt, encoding="utf-8")

        logger.info(f"[{idx}/{len(pending)}] Consultando {name} ({n_id})...")

        if not args.force:
            recovered = try_recover_from_history(cli_path, n_id)
            if recovered:
                save_census_md(out_file, name, parish, n_id, recovered)
                logger.info(f"  -> RECUPERADO del servidor! Guardado {out_file} ({len(recovered)} chars)")
                if idx < len(pending):
                    time.sleep(2)
                continue

        success = False
        max_retries = 3
        for attempt in range(1, max_retries + 1):
            backoff = 10 * (2 ** (attempt - 1))
            ans, is_auth, err = run_single_ask(cli_path, n_id, temp_prompt_file, timeout_sec=600)
            if ans:
                save_census_md(out_file, name, parish, n_id, ans)
                logger.info(f"  -> OK! Guardado {out_file} ({len(ans)} chars)")
                success = True
                break

            logger.warning(f"  -> Fallo en {name} (intento {attempt}/{max_retries}): {err}")
            if is_auth:
                refresh_token(cli_path)
            else:
                time.sleep(10)
                recovered = try_recover_from_history(cli_path, n_id)
                if recovered:
                    save_census_md(out_file, name, parish, n_id, recovered)
                    logger.info(f"  -> RECUPERADO del servidor! Guardado {out_file} ({len(recovered)} chars)")
                    success = True
                    break

                # Si falla un cuaderno grande tras el intento 1 sin error de auth, dividir en tramos <=90 imgs
                merged = run_chunked_census(cli_path, name, n_id, temp_prompt_file, chunk_size=90)
                if merged:
                    save_census_md(out_file, name, parish, n_id, merged)
                    logger.info(f"  -> OK POR TRAMOS! Guardado {out_file} ({len(merged)} chars)")
                    success = True
                    break

            if attempt < max_retries:
                logger.info(f"  -> Esperando {backoff}s antes de reintentar...")
                time.sleep(backoff)

        if not success:
            failed.append(name)
            logger.error(f"  -> FALLO DEFINITIVO en {name} tras {max_retries} intentos.")

        if idx < len(pending):
            time.sleep(5)

    logger.info(f"Censo finalizado. Fallos: {len(failed)} -> {failed}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
