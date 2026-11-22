"""Módulo preparado para exportación de datasets Kraken (.arrow/XML) y Chandra OCR 2 (JSONL/HF)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from lxml import etree

from .config import PAGE_NS


def export_chandra_jsonl_stub(
    page_items: Iterable[tuple[Path, Path]],
    output_jsonl: Path,
) -> Path:
    """Esqueleto para Flujo C: convierte imagen recortada + PAGE-XML con regiones semánticas a JSONL.

    Regla obligatoria de arquitectura: exportar recortes por plana individual (izquierda/derecha)
    o por partida completa (`margen_indice` + `cuerpo_partida`) para evitar degradación por `scale_to_fit`.
    """
    ns = {"p": PAGE_NS}
    output_jsonl.parent.mkdir(parents=True, exist_ok=True)
    records = 0

    with output_jsonl.open("w", encoding="utf-8") as fh:
        for image_path, xml_path in page_items:
            tree = etree.parse(str(xml_path))
            root = tree.getroot()
            blocks: list[dict[str, object]] = []

            for region in root.findall(".//p:TextRegion", ns):
                lines_text = [
                    (el.text or "").strip()
                    for el in region.findall(".//p:TextLine/p:TextEquiv/p:Unicode", ns)
                    if (el.text or "").strip()
                ]
                coords_el = region.find("p:Coords", ns)
                if not lines_text or coords_el is None:
                    continue

                pts = [
                    tuple(map(int, p.split(",")))
                    for p in coords_el.attrib.get("points", "").split()
                    if "," in p
                ]
                if not pts:
                    continue
                xs = [p[0] for p in pts]
                ys = [p[1] for p in pts]
                blocks.append(
                    {
                        "region_id": region.attrib.get("id", ""),
                        "custom": region.attrib.get("custom", ""),
                        "bbox": [min(xs), min(ys), max(xs), max(ys)],
                        "text": "\n".join(lines_text),
                    }
                )

            payload = {"image": str(image_path), "blocks": blocks}
            fh.write(json.dumps(payload, ensure_ascii=False) + "\n")
            records += 1

    return output_jsonl
