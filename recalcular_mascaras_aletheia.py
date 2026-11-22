r"""Recalcula las máscaras poligonales <Coords> de cada <TextLine> en archivos PAGE-XML
a partir de sus <Baseline> editadas o cortadas (Split) en Aletheia 4.1.

Utiliza `kraken.lib.segmentation.calculate_polygonal_environment` sobre la imagen original,
preservando intactos:
- Los IDs de región y línea (<TextRegion>, <TextLine>)
- Los tipos semánticos de región (cuerpo_partida, margen_indice, firma, nota_extra)
- La jerarquía <ReadingOrder> (<OrderedGroup>)
- Las transcripciones <TextEquiv><Unicode> existentes

Uso:
  .\.venv\Scripts\python.exe recalcular_mascaras_aletheia.py --xml htr_pipeline/outputs/lote_prueba_5/004298570_02637.xml
  .\.venv\Scripts\python.exe recalcular_mascaras_aletheia.py --xml-dir htr_pipeline/outputs/lote_prueba_5
"""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from kraken.lib.segmentation import calculate_polygonal_environment
from lxml import etree
from PIL import Image

from htr_pipeline.pagexml_utils import parse_points


def format_points(pts: list[tuple[int, int]] | list[list[int]]) -> str:
    """Convierte una lista de puntos [(x, y), ...] al formato PAGE-XML 'x1,y1 x2,y2 ...'."""
    return " ".join(f"{int(round(p[0]))},{int(round(p[1]))}" for p in pts)


def resolve_image_for_xml(xml_path: Path, root: etree._Element) -> Path:
    """Resuelve la ruta de la imagen asociada al PAGE-XML."""
    page_el = root.find(".//{*}Page")
    if page_el is not None:
        img_attr = page_el.get("imageFilename")
        if img_attr:
            candidate = xml_path.parent / Path(img_attr).name
            if candidate.exists():
                return candidate
    for ext in (".jpg", ".JPG", ".png", ".PNG", ".tif", ".TIF"):
        candidate = xml_path.with_suffix(ext)
        if candidate.exists():
            return candidate
    raise FileNotFoundError(f"No se encontró la imagen asociada a {xml_path}")


def recalculate_xml_polygons(xml_path: Path, backup: bool = True) -> tuple[int, float]:
    """Recalcula los polígonos <Coords> de todas las <TextLine> con <Baseline> válida."""
    t0 = time.perf_counter()
    parser = etree.XMLParser(remove_blank_text=False)
    tree = etree.parse(str(xml_path), parser)
    root = tree.getroot()
    ns = root.nsmap.get(None, "http://schema.primaresearch.org/PAGE/gts/pagecontent/2019-07-15")

    img_path = resolve_image_for_xml(xml_path, root)
    pil_im = Image.open(img_path).convert("L")

    text_lines = root.findall(".//{*}TextLine")
    valid_elements: list[etree._Element] = []
    baselines: list[list[tuple[int, int]]] = []

    for line_el in text_lines:
        bl_el = line_el.find("{*}Baseline")
        if bl_el is None or not bl_el.get("points"):
            continue
        try:
            pts_arr = parse_points(bl_el.get("points", ""), min_pts=2)
            bl_pts = [(int(p[0]), int(p[1])) for p in pts_arr]
            if len(bl_pts) >= 2:
                valid_elements.append(line_el)
                baselines.append(bl_pts)
        except ValueError:
            continue

    if not baselines:
        return 0, time.perf_counter() - t0

    polygons = calculate_polygonal_environment(im=pil_im, baselines=baselines)

    if backup:
        bak_path = xml_path.with_suffix(".xml.bak")
        if not bak_path.exists():
            bak_path.write_bytes(xml_path.read_bytes())

    updated_count = 0
    for line_el, poly in zip(valid_elements, polygons):
        if poly is None or len(poly) < 3:
            continue
        coords_el = line_el.find("{*}Coords")
        if coords_el is None:
            coords_el = etree.Element(f"{{{ns}}}Coords")
            line_el.insert(0, coords_el)
        coords_el.set("points", format_points(poly))
        updated_count += 1

    tree.write(
        str(xml_path),
        encoding="utf-8",
        xml_declaration=True,
        pretty_print=True,
    )
    return updated_count, time.perf_counter() - t0


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Recalcula máscaras poligonales <Coords> en PAGE-XML tras editar <Baseline> en Aletheia 4.1."
    )
    parser.add_argument("--xml", type=Path, help="Ruta a un archivo PAGE-XML individual.")
    parser.add_argument("--xml-dir", type=Path, help="Carpeta con archivos PAGE-XML (.xml).")
    parser.add_argument("--no-backup", action="store_true", help="No crear copia .xml.bak.")
    args = parser.parse_args()

    xml_files: list[Path] = []
    if args.xml:
        xml_files.append(args.xml)
    if args.xml_dir:
        for p in sorted(args.xml_dir.glob("*.xml")):
            if not p.name.startswith("METS"):
                xml_files.append(p)

    if not xml_files:
        parser.error("Debes indicar --xml <archivo.xml> o --xml-dir <carpeta>.")

    print(f"Recalculando mascaras poligonales <Coords> en {len(xml_files)} archivo(s) PAGE-XML...")
    for xp in xml_files:
        count, elapsed = recalculate_xml_polygons(xp, backup=not args.no_backup)
        print(f"  [OK] {xp.name}: {count} poligonos recalculados en {elapsed:.2f}s")


if __name__ == "__main__":
    main()
