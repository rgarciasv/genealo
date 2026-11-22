#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Segmentador local en lote con Kraken (`blla.mlmodel`) para Windows 11.
- Carga el modelo una única vez (reutilizándolo en todo el lote).
- Genera PAGE-XML estándar compatible con Aletheia, nw-page-editor y eScriptorium.
- Copia la imagen junto al XML en la carpeta de salida para apertura directa en Aletheia.
- Genera un overlay visual `_preview.png` (baselines en azul, máscaras en verde) para auditoría rápida.
"""

from __future__ import annotations

import argparse
import logging
import shutil
import sys
import time
from pathlib import Path

import cv2
import numpy as np
import torch
from kraken import blla, serialization
from kraken.lib import vgsl
from lxml import etree
from PIL import Image

from htr_pipeline.config import DEFAULT_MIN_LINE_WIDTH_PX, PAGE_NS, PROJECT_ROOT
from htr_pipeline.pagexml_utils import load_image_unicode, parse_points, save_image_unicode

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("segmentar_lote")


def _normalize_pagexml_metadata(xml_str: str, image_filename: str, min_width_px: int) -> tuple[str, int, int]:
    """Asegura imageFilename relativo (nombre de archivo) y filtra micro-líneas residuales."""
    parser = etree.XMLParser(remove_blank_text=False)
    root = etree.fromstring(xml_str.encode("utf-8"), parser)
    ns = {"p": PAGE_NS}

    page_el = root.find(".//p:Page", ns)
    if page_el is not None:
        page_el.attrib["imageFilename"] = image_filename

    kept = 0
    removed = 0
    for region in root.findall(".//p:TextRegion", ns):
        for line_el in list(region.findall("p:TextLine", ns)):
            coords_el = line_el.find("p:Coords", ns)
            if coords_el is None or "points" not in coords_el.attrib:
                region.remove(line_el)
                removed += 1
                continue
            pts = parse_points(coords_el.attrib["points"], min_pts=3)
            width = int(pts[:, 0].max() - pts[:, 0].min())
            if width < min_width_px:
                region.remove(line_el)
                removed += 1
            else:
                kept += 1

    xml_bytes = etree.tostring(root, encoding="UTF-8", xml_declaration=True, pretty_print=True)
    return xml_bytes.decode("utf-8"), kept, removed


def _render_preview_overlay(image_path: Path, xml_path: Path, preview_path: Path) -> None:
    """Genera imagen de auditoría rápida con regiones (naranja), polígonos (verde) y baselines (azul)."""
    img = load_image_unicode(image_path)
    tree = etree.parse(str(xml_path))
    root = tree.getroot()
    ns = {"p": PAGE_NS}

    for region in root.findall(".//p:TextRegion", ns):
        rcoords = region.find("p:Coords", ns)
        if rcoords is not None and "points" in rcoords.attrib:
            rpts = parse_points(rcoords.attrib["points"], min_pts=3)
            cv2.polylines(img, [rpts], True, (0, 140, 255), 3)

    for idx, line_el in enumerate(root.findall(".//p:TextLine", ns), start=1):
        c_el = line_el.find("p:Coords", ns)
        b_el = line_el.find("p:Baseline", ns)
        if c_el is not None and "points" in c_el.attrib:
            cpts = parse_points(c_el.attrib["points"], min_pts=3)
            cv2.polylines(img, [cpts], True, (0, 185, 0), 1)
        if b_el is not None and "points" in b_el.attrib:
            bpts = parse_points(b_el.attrib["points"], min_pts=2)
            cv2.polylines(img, [bpts], False, (255, 60, 0), 3)

    # Reducir al 50% para previsualización ligera y nítida
    h, w = img.shape[:2]
    resized = cv2.resize(img, (w // 2, h // 2), interpolation=cv2.INTER_AREA)
    save_image_unicode(preview_path, resized)


def main() -> int:
    parser = argparse.ArgumentParser(description="Segmentación local en lote con Kraken (blla).")
    parser.add_argument(
        "--input-dir",
        default=str(PROJECT_ROOT / "htr_pipeline" / "inputs" / "lote_prueba_5"),
        help="Carpeta con imágenes .jpg de entrada.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(PROJECT_ROOT / "htr_pipeline" / "outputs" / "lote_prueba_5"),
        help="Carpeta donde guardar los PAGE-XML, copias JPG y previews.",
    )
    parser.add_argument(
        "--device",
        default="cuda:0" if torch.cuda.is_available() else "cpu",
        help="Dispositivo PyTorch ('cuda:0' o 'cpu').",
    )
    parser.add_argument(
        "--min-width",
        type=int,
        default=DEFAULT_MIN_LINE_WIDTH_PX,
        help="Ancho mínimo de línea en píxeles para filtrar ruido.",
    )
    args = parser.parse_args()

    in_dir = Path(args.input_dir)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    preview_dir = out_dir / "previews"
    preview_dir.mkdir(parents=True, exist_ok=True)

    images = sorted(
        list(in_dir.glob("*.jpg")) + list(in_dir.glob("*.jpeg")) + list(in_dir.glob("*.png"))
    )
    if not images:
        logger.error("No se encontraron imágenes en %s", in_dir)
        return 1

    logger.info("Cargando modelo por defecto blla.mlmodel en dispositivo: %s", args.device)
    model_path = Path(blla.__file__).resolve().parent / "blla.mlmodel"
    model = vgsl.TorchVGSLModel.load_model(model_path)

    for idx, img_path in enumerate(images, start=1):
        t0 = time.perf_counter()
        logger.info("[%d/%d] Segmentando %s...", idx, len(images), img_path.name)
        with Image.open(img_path) as im:
            im_rgb = im.convert("RGB")
            seg = blla.segment(im_rgb, model=model, device=args.device)
            raw_xml = serialization.serialize(seg, image_size=im_rgb.size, template="pagexml")

        clean_xml, kept, removed = _normalize_pagexml_metadata(
            raw_xml, image_filename=img_path.name, min_width_px=args.min_width
        )

        xml_out = out_dir / f"{img_path.stem}.xml"
        xml_out.write_text(clean_xml, encoding="utf-8")

        jpg_copy = out_dir / img_path.name
        if not jpg_copy.exists():
            shutil.copy2(img_path, jpg_copy)

        preview_out = preview_dir / f"{img_path.stem}_preview.png"
        _render_preview_overlay(jpg_copy, xml_out, preview_out)

        elapsed = time.perf_counter() - t0
        logger.info(
            "  -> OK en %.1fs | Líneas válidas: %d | Filtradas (<%dpx): %d | XML: %s",
            elapsed,
            kept,
            args.min_width,
            removed,
            xml_out.name,
        )

    logger.info("Lote completado. Revisa los previews en %s", preview_dir)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
