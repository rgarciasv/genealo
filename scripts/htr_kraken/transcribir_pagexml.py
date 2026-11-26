#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script principal (Flujo A1/A2): Transcripción paleográfica asistida por líneas desde PAGE-XML.

Flujo de ejecución en Windows 11 / PowerShell:
1. Lee la imagen original a resolución nativa (sin reducir resolución).
2. Parsea el PAGE-XML exportado de eScriptorium y filtra micro-líneas (< 45 px de ancho).
3. Extrae recortes poligonales enmascarados (<Coords>) con dilatación suave (4 px) y
   relleno exterior con la mediana del color de fondo del papel, guardándolos en `debug_crops/`.
4. Envía cada recorte a Gemini (`gemini-3.1-pro-preview`) con salida Pydantic estructurada
   (`{"texto": str, "duda": bool, "motivo": str}`).
5. Audita el inventario Unicode cerrado e inyecta el texto limpio en `<TextEquiv><Unicode>`.
6. Empaqueta el PAGE-XML junto con `METS.xml` en `reimport_escriptorium_01608.zip` y exporta
   `cola_revision_01608.json` con todas las líneas dudosas.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path
from typing import Optional

_ROOT = Path(__file__).resolve().parents[2]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from htr_pipeline.config import (
    DEFAULT_DILATION_PX,
    DEFAULT_INPUT_DIR,
    DEFAULT_MIN_LINE_WIDTH_PX,
    DEFAULT_MODEL,
    DEFAULT_OUTPUT_DIR,
    DEFAULT_TEMPERATURE,
    PROJECT_ROOT,
)
from htr_pipeline.gemini_transcriber import GeminiLineTranscriber, LineTranscriptionResult
from htr_pipeline.pagexml_utils import (
    ExtractedLine,
    extract_lines_from_pagexml,
    package_escriptorium_zip,
    write_updated_pagexml,
)
from htr_pipeline.unicode_audit import audit_pagexml_unicode

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("transcribir_pagexml")


def _resolve_existing_path(explicit: Optional[str], candidates: list[Path], label: str) -> Path:
    if explicit:
        p = Path(explicit)
        if not p.exists():
            raise FileNotFoundError(f"No se encuentra {label}: {p}")
        return p
    for cand in candidates:
        if cand.exists():
            return cand
    searched = "\n  - ".join(str(c) for c in candidates)
    raise FileNotFoundError(f"No se encontró {label} en ninguna ruta esperada:\n  - {searched}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Recorta líneas poligonales de PAGE-XML y transcribe con Gemini API."
    )
    parser.add_argument("--image", help="Ruta a la imagen original (ej. 004298570_01608.jpg)")
    parser.add_argument("--xml", help="Ruta al PAGE-XML de entrada (ej. 004298570_01608_4.xml)")
    parser.add_argument("--mets", help="Ruta al manifiesto METS (ej. METS_4.xml)")
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help=f"Directorio de salida (por defecto: {DEFAULT_OUTPUT_DIR})",
    )
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Modelo Gemini (default: {DEFAULT_MODEL})")
    parser.add_argument(
        "--temperature",
        type=float,
        default=DEFAULT_TEMPERATURE,
        help=f"Temperatura de generación (default: {DEFAULT_TEMPERATURE})",
    )
    parser.add_argument(
        "--dilation",
        type=int,
        default=DEFAULT_DILATION_PX,
        help=f"Dilatación del polígono en px (default: {DEFAULT_DILATION_PX})",
    )
    parser.add_argument(
        "--min-width",
        type=int,
        default=DEFAULT_MIN_LINE_WIDTH_PX,
        help=f"Ancho mínimo de línea en px para no descartarla (default: {DEFAULT_MIN_LINE_WIDTH_PX})",
    )
    parser.add_argument("--delay", type=float, default=0.35, help="Pausa entre llamadas API en segundos.")
    parser.add_argument("--limit", type=int, default=0, help="Procesar solo las primeras N líneas (0 = todas).")
    parser.add_argument("--line-ids", default="", help="Lista separada por comas de IDs concretos a transcribir.")
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Reanuda desde checkpoint JSON omitiendo líneas ya transcritas.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo recorta polígonos en debug_crops/ y valida XML/ZIP sin llamar a la API de Gemini.",
    )
    return parser.parse_args()


def _load_checkpoint(checkpoint_path: Path) -> dict[str, dict[str, object]]:
    if not checkpoint_path.exists():
        return {}
    try:
        return json.loads(checkpoint_path.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.warning("No se pudo leer checkpoint %s: %s", checkpoint_path, exc)
        return {}


def _save_checkpoint(checkpoint_path: Path, data: dict[str, dict[str, object]]) -> None:
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    checkpoint_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> int:
    # Garantizar UTF-8 en consola Windows
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    args = parse_args()

    image_path = _resolve_existing_path(
        args.image,
        [
            Path("004298570_01608.jpg"),
            DEFAULT_INPUT_DIR / "004298570_01608.jpg",
            PROJECT_ROOT / "imagenes" / "rollo 004298570" / "004298570_01608.jpg",
        ],
        "imagen fuente",
    )
    xml_path = _resolve_existing_path(
        args.xml,
        [
            Path("004298570_01608_4.xml"),
            DEFAULT_INPUT_DIR / "004298570_01608_4.xml",
            DEFAULT_INPUT_DIR / "004298570_01608.xml",
            Path("004298570_01608.xml"),
        ],
        "archivo PAGE-XML",
    )
    mets_path = _resolve_existing_path(
        args.mets,
        [
            Path("METS_4.xml"),
            DEFAULT_INPUT_DIR / "METS_4.xml",
            DEFAULT_INPUT_DIR / "METS.xml",
            Path("METS.xml"),
        ],
        "manifiesto METS",
    )

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    debug_crops_dir = out_dir / "debug_crops"

    page_stem = image_path.stem
    folio_suffix = page_stem.split("_")[-1] if "_" in page_stem else page_stem
    output_xml_path = out_dir / f"{page_stem}.xml"
    output_zip_path = out_dir / f"reimport_escriptorium_{folio_suffix}.zip"
    review_queue_path = out_dir / f"cola_revision_{folio_suffix}.json"
    checkpoint_path = out_dir / f"checkpoint_{folio_suffix}.json"

    logger.info("Imagen fuente : %s", image_path)
    logger.info("PAGE-XML      : %s", xml_path)
    logger.info("METS          : %s", mets_path)
    logger.info("Salida        : %s", out_dir)

    lines, skipped, (img_w, img_h) = extract_lines_from_pagexml(
        image_path=image_path,
        xml_path=xml_path,
        debug_crops_dir=debug_crops_dir,
        min_line_width_px=args.min_width,
        dilation_px=args.dilation,
    )
    logger.info(
        "Resolución nativa: %dx%d px | Líneas válidas: %d | Descartadas (<%dpx): %d",
        img_w,
        img_h,
        len(lines),
        args.min_width,
        len(skipped),
    )

    target_lines: list[ExtractedLine] = lines
    if args.line_ids.strip():
        wanted = {x.strip() for x in args.line_ids.split(",") if x.strip()}
        target_lines = [ln for ln in lines if ln.line_id in wanted]
        logger.info("Filtrado por --line-ids: %d líneas seleccionadas.", len(target_lines))
    if args.limit and args.limit > 0:
        target_lines = target_lines[: args.limit]
        logger.info("Limitado por --limit: %d líneas.", len(target_lines))

    checkpoint_data: dict[str, dict[str, object]] = _load_checkpoint(checkpoint_path) if args.resume else {}

    transcriber: Optional[GeminiLineTranscriber] = None
    if not args.dry_run:
        transcriber = GeminiLineTranscriber(model=args.model, temperature=args.temperature)

    transcriptions_map: dict[str, str] = {}
    review_queue: list[dict[str, object]] = []

    total = len(target_lines)
    for idx, line in enumerate(target_lines, start=1):
        if args.resume and line.line_id in checkpoint_data:
            cached = checkpoint_data[line.line_id]
            result = LineTranscriptionResult(
                texto=str(cached.get("texto", "")),
                duda=bool(cached.get("duda", False)),
                motivo=str(cached.get("motivo", "")),
            )
            logger.info("[%d/%d] (CACHE) %s -> %s", idx, total, line.line_id, result.texto)
        elif args.dry_run:
            result = LineTranscriptionResult(texto="", duda=False, motivo="dry-run")
        else:
            assert transcriber is not None
            result = transcriber.transcribe_line(
                crop_bgr=line.crop_bgr,
                line_id=line.line_id,
                side=line.side,
            )
            logger.info(
                "[%d/%d] %s (%s, %dx%dpx) | duda=%s | %s",
                idx,
                total,
                line.line_id,
                line.side,
                line.width,
                line.height,
                result.duda,
                result.texto if result.texto else "<VACÍO>",
            )
            checkpoint_data[line.line_id] = {
                "texto": result.texto,
                "duda": result.duda,
                "motivo": result.motivo,
                "side": line.side,
                "crop": str(line.crop_path),
            }
            _save_checkpoint(checkpoint_path, checkpoint_data)
            if idx < total and args.delay > 0:
                time.sleep(args.delay)

        transcriptions_map[line.line_id] = result.texto
        if result.duda:
            review_queue.append(
                {
                    "line_id": line.line_id,
                    "side": line.side,
                    "bbox": list(line.bbox),
                    "crop_path": str(line.crop_path),
                    "texto_propuesto": result.texto,
                    "motivo": result.motivo,
                }
            )

    if args.dry_run:
        updated_count = write_updated_pagexml(xml_path, output_xml_path, {})
    else:
        updated_count = write_updated_pagexml(xml_path, output_xml_path, transcriptions_map)

    issues = audit_pagexml_unicode(output_xml_path)
    if issues:
        logger.warning("Auditoría Unicode detectó %d incidencias:", len(issues))
        for issue in issues[:20]:
            logger.warning("  - %s [%s %s]: %s", issue.line_id, issue.char, issue.codepoint, issue.reason)
    else:
        logger.info("Auditoría Unicode cerrada: 0 incidencias.")

    package_escriptorium_zip(output_xml_path, mets_path, output_zip_path)
    review_queue_path.write_text(json.dumps(review_queue, ensure_ascii=False, indent=2), encoding="utf-8")

    logger.info("=" * 68)
    logger.info("RESUMEN FINAL")
    logger.info("  Recortes guardados   : %s (%d PNGs)", debug_crops_dir, len(lines))
    logger.info("  Líneas actualizadas  : %d", updated_count)
    logger.info("  PAGE-XML generado    : %s", output_xml_path)
    logger.info("  ZIP eScriptorium     : %s", output_zip_path)
    logger.info("  Cola revisión dudas  : %s (%d líneas con duda)", review_queue_path, len(review_queue))
    logger.info("=" * 68)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
