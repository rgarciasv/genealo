"""Auditoría Unicode cerrada y conector preparado para validación choco-mufin."""

from __future__ import annotations

import logging
import subprocess
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from lxml import etree

from .config import ALLOWED_SPECIAL_UNICODE, FORBIDDEN_OR_CONFUSED_CHARS, PAGE_NS

logger = logging.getLogger(__name__)


@dataclass
class UnicodeIssue:
    line_id: str
    char: str
    codepoint: str
    reason: str


def audit_text_line(line_id: str, text: str) -> list[UnicodeIssue]:
    """Audita una cadena contra el inventario Unicode cerrado del proyecto."""
    issues: list[UnicodeIssue] = []
    # Descomponer NFD para validar macrón combinante U+0304 y detectar ligaduras/confusiones
    for ch in text:
        if ch in FORBIDDEN_OR_CONFUSED_CHARS:
            issues.append(
                UnicodeIssue(
                    line_id=line_id,
                    char=ch,
                    codepoint=f"U+{ord(ch):04X}",
                    reason=FORBIDDEN_OR_CONFUSED_CHARS[ch],
                )
            )
            continue

        code = ord(ch)
        if 0x20 <= code <= 0x7E:
            continue

        if ch not in ALLOWED_SPECIAL_UNICODE:
            nfd = unicodedata.normalize("NFD", ch)
            if all((0x20 <= ord(c) <= 0x7E) or (c in ALLOWED_SPECIAL_UNICODE) for c in nfd):
                continue
            issues.append(
                UnicodeIssue(
                    line_id=line_id,
                    char=ch,
                    codepoint=f"U+{code:04X}",
                    reason=f"Carácter fuera del inventario Unicode cerrado ({unicodedata.name(ch, 'UNKNOWN')}).",
                )
            )
    return issues


def audit_pagexml_unicode(xml_path: Path) -> list[UnicodeIssue]:
    """Audita todas las líneas `<TextEquiv><Unicode>` de un PAGE-XML."""
    tree = etree.parse(str(xml_path))
    root = tree.getroot()
    ns = {"p": PAGE_NS}

    all_issues: list[UnicodeIssue] = []
    for line_el in root.findall(".//p:TextLine", ns):
        line_id = line_el.attrib.get("id", "unknown")
        unicode_el = line_el.find("p:TextEquiv/p:Unicode", ns)
        if unicode_el is None or not unicode_el.text:
            continue
        all_issues.extend(audit_text_line(line_id, unicode_el.text))
    return all_issues


def run_choco_mufin_control(xml_paths: Iterable[Path], table_path: Path) -> int:
    """Hook preparado para invocar `choco-mufin` en fases posteriores de control masivo."""
    cmd = ["choco-mufin", "control", str(table_path), *[str(p) for p in xml_paths]]
    logger.info("Ejecutando choco-mufin: %s", " ".join(cmd))
    res = subprocess.run(cmd, check=False)
    return res.returncode
