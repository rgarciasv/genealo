"""Módulo preparado para postprocesado espacial y reconstrucción documental (Flujo D)."""

from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Iterable


@dataclass
class SemanticRegion:
    """Representa una región semántica del esquema DLA (folio, margen_indice, cuerpo_partida, etc.)."""

    region_id: str
    region_type: str  # folio | margen_indice | margen_nota | cuerpo_partida | firma | reclamo | texto_vertical
    bbox: tuple[int, int, int, int]  # (x1, y1, x2, y2)
    text: str

    @property
    def center_x(self) -> float:
        return (self.bbox[0] + self.bbox[2]) / 2.0

    @property
    def center_y(self) -> float:
        return (self.bbox[1] + self.bbox[3]) / 2.0


def sort_double_page_regions(regions: Iterable[SemanticRegion], image_width: int) -> list[SemanticRegion]:
    """Fuerza orden de lectura estricto en doble página: mitad izquierda completa -> mitad derecha completa."""
    x_mid = image_width / 2.0
    left = sorted((r for r in regions if r.center_x < x_mid), key=lambda r: (r.bbox[1], r.bbox[0]))
    right = sorted((r for r in regions if r.center_x >= x_mid), key=lambda r: (r.bbox[1], r.bbox[0]))
    return left + right


def match_margins_to_entries(
    margins: list[SemanticRegion],
    entries: list[SemanticRegion],
    min_name_similarity: float = 0.55,
) -> dict[str, str]:
    """Empareja `margen_indice` con `cuerpo_partida` por coincidencia léxica o solapamiento vertical.

    Returns:
        Diccionario `{cuerpo_partida.region_id: margen_indice.region_id}`.
    """
    matches: dict[str, str] = {}
    used_entries: set[str] = set()

    for margin in margins:
        best_id: str | None = None
        best_score = -1.0
        margin_tokens = margin.text.lower().strip()

        for entry in entries:
            if entry.region_id in used_entries:
                continue

            # 1) Proximidad vertical
            y1, y2 = entry.bbox[1], entry.bbox[3]
            in_vertical_band = y1 <= margin.center_y <= y2
            dist_y = abs(margin.center_y - entry.center_y)
            spatial_score = 1.0 if in_vertical_band else max(0.0, 1.0 - dist_y / 1200.0)

            # 2) Coincidencia aproximada de nombre dentro de las primeras líneas del cuerpo
            entry_head = entry.text[:250].lower()
            lexical_score = SequenceMatcher(None, margin_tokens, entry_head).quick_ratio()
            combined = (0.65 * lexical_score + 0.35 * spatial_score) if lexical_score >= min_name_similarity else spatial_score * 0.5

            if combined > best_score:
                best_score = combined
                best_id = entry.region_id

        if best_id is not None:
            matches[best_id] = margin.region_id
            used_entries.add(best_id)

    return matches
