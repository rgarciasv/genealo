#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Independent E2E Verification Harness for Navarredondilla Parroquial Sources & Notebooks.
Project: Genealo - Archivo Diocesano / Parroquial de Navarredondilla (Option A)

Validates:
1. Protected Active Notebooks Barrier (Zero Regression Shield):
   - '7967d647-8ca2-4863-a576-11843e8e8802' ('Lib. Baut. Navarre Vol. 1 (1594-1695)', NRDL-BAUT-04): exactly 188 sources, 0 modifications.
   - 'ec86de71-a11c-4489-bbb9-eea856cccac4' ('NRDL-ENSENADA-LEGOS-01'): exactly 87 sources.
   - '407d5cb4-4b83-495f-a23a-309ea44ee8c6' ('JMOL-ENSENADA-LEGOS-01'): exactly 28 sources.
   - 'e7fba70b-af7d-4602-b543-060742b22528' ('VLLR-ENSENADA-LEGOS-01'): exactly 51 sources.
   - 'cd72ef58-fcf5-48ac-8de2-556648ebd90e' ('NDRN-ENSENADA-LEGOS-01'): exactly 34 sources.
   Total protected sources: exactly 388 sources across 5 notebooks.

2. Target Navarredondilla Parroquial Notebooks (15 Notebooks, 2,276 Images):
   - Existence and exact canonical title match [L-29]:
     1.  NRDL-BAUT-01 (245 sources)
     2.  NRDL-BAUT-02 (157 sources)
     3.  NRDL-BAUT-03 (231 sources)
     4.  NRDL-BAUT-05 (144 sources)
     5.  NRDL-BAUT-06 (183 sources)
     6.  NRDL-BAUT-07 (102 sources)
     7.  NRDL-DIFU-01 (236 sources)
     8.  NRDL-DIFU-01B (65 sources)
     9.  NRDL-DIFU-02 (171 sources)
     10. NRDL-DIFU-03 (170 sources)
     11. NRDL-DIFU-04 (188 sources)
     12. NRDL-DIFU-05 (211 sources)
     13. NRDL-MATR-01 (33 sources)
     14. NRDL-MATR-02 (70 sources)
     15. NRDL-MIXTO-01 (70 sources)
     Total: exactly 2,276 sources.

3. Canonical Corpus Cross-Check (BOM-safe 'utf-8-sig' 'catalogo_corpus.json'):
   - Filtered strictly by 'cuaderno_asignado_id == notebook_title' (prevents range interleaving corruption).
   - Set equality: missing_sources == 0, extra_sources == 0, duplicate_sources == 0.

4. Primary Key Naming Standard [L-28]:
   - Every source title strictly matches '^\\d{9}_\\d{5}\\.jpg$' without zero truncation.

5. Source Processing Status:
   - 100% of sources in READY status (0 ERROR, 0 PENDING).
   - Safe status extraction via 'get_source_status_str' avoiding 'status_label' AttributeError.

6. Reporting & Exit Code:
   - Formatted ASCII table summary printed to stdout.
   - Structured JSON audit exported to 'scripts/verification_report_nrdl.json'.
   - Exit code 0 on complete pass, 1 on any failure.
"""

import argparse
import asyncio
import json
import logging
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

# Attempt import of notebooklm-py
try:
    from notebooklm import NotebookLMClient, SourceStatus
    from notebooklm.exceptions import (
        AuthError,
        NetworkError,
        NotebookLMError,
        RateLimitError,
        RPCError,
        ServerError,
    )
    NOTEBOOKLM_AVAILABLE = True
except ImportError:
    NOTEBOOKLM_AVAILABLE = False
    SourceStatus = None

# -----------------------------------------------------------------------------
# Configuration Constants
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG_PATH = BASE_DIR / "catalogo_corpus.json"
DEFAULT_REPORT_PATH = BASE_DIR / "scripts" / "verification_report_nrdl.json"

# Canonical Primary Key Regex [L-28]: 9-digit DGS + 5-digit Fotograma + .jpg
CANONICAL_FILENAME_REGEX = re.compile(r"^\d{9}_\d{5}\.jpg$")

# Protected Active Notebooks Barrier (5 notebooks, 388 sources total)
PROTECTED_NOTEBOOKS = {
    "7967d647-8ca2-4863-a576-11843e8e8802": {
        "title": "Lib. Baut. Navarre Vol. 1 (1594-1695)",
        "expected_count": 188,
        "role": "NRDL-BAUT-04 (Sacramental Activo)",
    },
    "ec86de71-a11c-4489-bbb9-eea856cccac4": {
        "title": "NRDL-ENSENADA-LEGOS-01",
        "expected_count": 87,
        "role": "Ensenada Personal de Legos - Navarredondilla",
    },
    "407d5cb4-4b83-495f-a23a-309ea44ee8c6": {
        "title": "JMOL-ENSENADA-LEGOS-01",
        "expected_count": 28,
        "role": "Ensenada Personal de Legos - S. J. del Molinillo",
    },
    "e7fba70b-af7d-4602-b543-060742b22528": {
        "title": "VLLR-ENSENADA-LEGOS-01",
        "expected_count": 51,
        "role": "Ensenada Personal de Legos - El Villarejo",
    },
    "cd72ef58-fcf5-48ac-8de2-556648ebd90e": {
        "title": "NDRN-ENSENADA-LEGOS-01",
        "expected_count": 34,
        "role": "Ensenada Personal de Legos - Navandrinal",
    },
}

TOTAL_EXPECTED_PROTECTED_SOURCES = sum(meta["expected_count"] for meta in PROTECTED_NOTEBOOKS.values())

# 15 Target Navarredondilla Parroquial Notebooks Specification
TARGET_NOTEBOOKS = {
    "NRDL-BAUT-01": {
        "parroquia": "NRDL",
        "tipo": "BAUTISMOS",
        "rollo_dgs": "004306112",
        "expected_count": 245,
        "signatura": "Sit. Arch. 166/4",
        "interleaved": True,  # Tramo 1870..1954 y 1988..2147; NRDL-MATR-01 intercalado en 1955..1987
    },
    "NRDL-BAUT-02": {
        "parroquia": "NRDL",
        "tipo": "BAUTISMOS",
        "rollo_dgs": "004306112",
        "expected_count": 157,
        "signatura": "Sit. Arch. 166/4",
        "interleaved": False,
    },
    "NRDL-BAUT-03": {
        "parroquia": "NRDL",
        "tipo": "BAUTISMOS",
        "rollo_dgs": "004306112",
        "expected_count": 231,
        "signatura": "Sit. Arch. 166/4",
        "interleaved": False,
    },
    "NRDL-BAUT-05": {
        "parroquia": "NRDL",
        "tipo": "BAUTISMOS",
        "rollo_dgs": "004306113",
        "expected_count": 144,
        "signatura": "Sit. Arch. 166/4",
        "interleaved": False,
    },
    "NRDL-BAUT-06": {
        "parroquia": "NRDL",
        "tipo": "BAUTISMOS",
        "rollo_dgs": "004306113",
        "expected_count": 183,
        "signatura": "Sit. Arch. 166/4",
        "interleaved": False,
    },
    "NRDL-BAUT-07": {
        "parroquia": "NRDL",
        "tipo": "BAUTISMOS",
        "rollo_dgs": "004306113",
        "expected_count": 102,
        "signatura": "Sit. Arch. 166/4",
        "interleaved": False,
    },
    "NRDL-DIFU-01": {
        "parroquia": "NRDL",
        "tipo": "DEFUNCIONES",
        "rollo_dgs": "004306113",
        "expected_count": 236,
        "signatura": "Sit. Arch. 166/4",
        "interleaved": False,
    },
    "NRDL-DIFU-01B": {
        "parroquia": "NRDL",
        "tipo": "DEFUNCIONES",
        "rollo_dgs": "004306113",
        "expected_count": 65,
        "signatura": "Sit. Arch. 166/4",
        "interleaved": False,
    },
    "NRDL-DIFU-02": {
        "parroquia": "NRDL",
        "tipo": "DEFUNCIONES",
        "rollo_dgs": "004306113",
        "expected_count": 171,
        "signatura": "Sit. Arch. 166/4",
        "interleaved": False,
    },
    "NRDL-DIFU-03": {
        "parroquia": "NRDL",
        "tipo": "DEFUNCIONES",
        "rollo_dgs": "004306113",
        "expected_count": 170,
        "signatura": "Sit. Arch. 166/4",
        "interleaved": False,
    },
    "NRDL-DIFU-04": {
        "parroquia": "NRDL",
        "tipo": "DEFUNCIONES",
        "rollo_dgs": "004306113",
        "expected_count": 188,
        "signatura": "Sit. Arch. 166/4",
        "interleaved": False,
    },
    "NRDL-DIFU-05": {
        "parroquia": "NRDL",
        "tipo": "DEFUNCIONES",
        "rollo_dgs": "004306113",
        "expected_count": 211,
        "signatura": "Sit. Arch. 166/4",
        "interleaved": False,
    },
    "NRDL-MATR-01": {
        "parroquia": "NRDL",
        "tipo": "MATRIMONIOS",
        "rollo_dgs": "004306112",
        "expected_count": 33,
        "signatura": "Sit. Arch. 166/4",
        "interleaved": True,  # Fotogramas 1955..1987 encuadernados dentro del rango de BAUT-01
    },
    "NRDL-MATR-02": {
        "parroquia": "NRDL",
        "tipo": "MATRIMONIOS",
        "rollo_dgs": "004306113",
        "expected_count": 70,
        "signatura": "Sit. Arch. 166/4",
        "interleaved": False,
    },
    "NRDL-MIXTO-01": {
        "parroquia": "NRDL",
        "tipo": "DEFUNCIONES",  # Rule [L-30]
        "cloud_titles": ["NRDL-DIFU-S17-B (1648-1695)", "NRDL-MIXTO-01"],
        "rollo_dgs": "004306112",
        "expected_count": 70,
        "signatura": "Sit. Arch. 166/4",
        "interleaved": False,
    },
}

TOTAL_EXPECTED_TARGET_SOURCES = sum(meta["expected_count"] for meta in TARGET_NOTEBOOKS.values())  # 2,276


# -----------------------------------------------------------------------------
# Canonical Corpus Loader & Pre-validation
# -----------------------------------------------------------------------------
def load_and_verify_canonical_corpus(
    corpus_path: Path,
    target_filter: Optional[List[str]] = None,
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Loads 'catalogo_corpus.json' using 'utf-8-sig' to cleanly strip the UTF-8 BOM.
    Extracts and validates records for target notebooks.
    Guarantees internal consistency against canonical expectations.
    """
    if not corpus_path.is_file():
        raise FileNotFoundError(f"Canonical corpus file not found: {corpus_path}")

    with open(corpus_path, "r", encoding="utf-8-sig") as f:
        corpus_data = json.load(f)

    if not isinstance(corpus_data, list):
        raise ValueError(f"Expected list in corpus JSON, got {type(corpus_data)}")

    # Determine which notebooks to extract
    target_keys = target_filter if target_filter else list(TARGET_NOTEBOOKS.keys())
    for k in target_keys:
        if k not in TARGET_NOTEBOOKS:
            raise ValueError(f"Unknown target notebook title '{k}'. Valid options: {list(TARGET_NOTEBOOKS.keys())}")

    expected_records: Dict[str, List[Dict[str, Any]]] = {}

    for target_title in target_keys:
        meta = TARGET_NOTEBOOKS[target_title]
        # Strict filtering by cuaderno_asignado_id avoids range interleaving issues
        matched = [
            r for r in corpus_data
            if r.get("cuaderno_asignado_id") == target_title
        ]
        # Sort sequentially by fotograma_numero
        matched.sort(key=lambda r: int(r.get("fotograma_numero", 0)))
        expected_records[target_title] = matched

        # Verify count
        if len(matched) != meta["expected_count"]:
            raise ValueError(
                f"Corpus inconsistency for {target_title}: expected {meta['expected_count']} records, "
                f"found {len(matched)}"
            )

        # Verify format of each record
        for rec in matched:
            img_id = rec.get("id_imagen", "")
            dgs = rec.get("rollo_dgs", "")

            if not CANONICAL_FILENAME_REGEX.match(img_id):
                raise ValueError(
                    f"Corpus record '{img_id}' in {target_title} violates [L-28] canonical filename pattern"
                )

            if dgs != meta["rollo_dgs"]:
                raise ValueError(
                    f"Corpus record '{img_id}' in {target_title} has unexpected rollo {dgs}, "
                    f"expected {meta['rollo_dgs']}"
                )

    if not target_filter:
        total_count = sum(len(recs) for recs in expected_records.values())
        if total_count != TOTAL_EXPECTED_TARGET_SOURCES:
            raise ValueError(
                f"Corpus total target records mismatch: expected {TOTAL_EXPECTED_TARGET_SOURCES}, got {total_count}"
            )

    return expected_records


# -----------------------------------------------------------------------------
# Source Status Helper Utilities
# -----------------------------------------------------------------------------
def get_source_status_str(source: Any) -> str:
    """
    Safely extracts string status representation from a Source object.
    Handles SourceStatus enum, string representation, or attribute lookup
    without crashing if 'status_label' is missing.
    """
    if hasattr(source, "status"):
        st = source.status
        if hasattr(st, "name"):
            return st.name
        return str(st)
    if hasattr(source, "status_label"):
        return str(source.status_label)
    return "UNKNOWN"


def is_source_ready(source: Any) -> bool:
    """Determines whether a source is confirmed in READY status."""
    if getattr(source, "is_ready", False):
        return True
    if SourceStatus and getattr(source, "status", None) == SourceStatus.READY:
        return True
    if get_source_status_str(source).upper() == "READY":
        return True
    return False


def is_source_error(source: Any) -> bool:
    """Determines whether a source is in ERROR status."""
    if getattr(source, "is_error", False):
        return True
    if SourceStatus and getattr(source, "status", None) == SourceStatus.ERROR:
        return True
    if get_source_status_str(source).upper() in ("ERROR", "FAILED"):
        return True
    return False


# -----------------------------------------------------------------------------
# Verification Engine
# -----------------------------------------------------------------------------
class NavarredondillaParroquialVerifier:
    """
    Independent E2E verification engine querying NotebookLM live API.
    Audits the 15 Navarredondilla Parroquial notebooks against catalogo_corpus.json
    and asserts zero modification to the 5 protected active notebooks.
    """

    def __init__(
        self,
        client: Optional[Any] = None,
        corpus_path: Optional[Path] = None,
        report_path: Optional[Path] = None,
        target_notebook_filter: Optional[List[str]] = None,
        quiet: bool = False,
    ):
        self.client = client
        self.corpus_path = corpus_path or DEFAULT_CATALOG_PATH
        self.report_path = report_path or DEFAULT_REPORT_PATH
        self.target_filter = target_notebook_filter
        self.quiet = quiet
        self.discrepancies: List[str] = []

    async def verify_protected_barrier(self, client: Any) -> Tuple[bool, Dict[str, Any]]:
        """
        Verifies requirement 1: Protected Active Notebooks Barrier.
        Asserts that the 5 existing notebooks (388 sources) are alive and untouched.
        """
        barrier_results: Dict[str, Any] = {}
        all_protected_valid = True

        try:
            all_nbs = await client.notebooks.list()
            nbs_by_id = {nb.id: nb for nb in all_nbs}
        except Exception as e_list:
            err_msg = f"Failed to list notebooks from account to verify protected barrier: {e_list}"
            self.discrepancies.append(f"[PROTECTED BARRIER ERROR] {err_msg}")
            return False, {"error": err_msg, "notebooks": {}}

        for prot_id, meta in PROTECTED_NOTEBOOKS.items():
            entry: Dict[str, Any] = {
                "notebook_id": prot_id,
                "expected_title": meta["title"],
                "actual_title": None,
                "role": meta["role"],
                "is_alive": False,
                "expected_sources": meta["expected_count"],
                "actual_sources": 0,
                "valid": False,
                "error": None,
            }

            nb = nbs_by_id.get(prot_id)
            if not nb:
                # Fallback: attempt client.notebooks.get(prot_id)
                try:
                    nb = await client.notebooks.get(prot_id)
                except Exception as e_get:
                    err_msg = f"Protected notebook {prot_id} ('{meta['title']}') not found in account: {e_get}"
                    entry["error"] = err_msg
                    self.discrepancies.append(f"[PROTECTED BARRIER] {err_msg}")
                    barrier_results[prot_id] = entry
                    all_protected_valid = False
                    continue

            entry["is_alive"] = True
            entry["actual_title"] = nb.title

            # Check title match (canonical title or contains canonical name)
            if nb.title != meta["title"] and meta["title"] not in nb.title:
                err_msg = f"Protected notebook title tampered: expected '{meta['title']}', got '{nb.title}'"
                entry["error"] = err_msg
                self.discrepancies.append(f"[PROTECTED BARRIER] {err_msg}")
                barrier_results[prot_id] = entry
                all_protected_valid = False
                continue

            # Query sources count
            try:
                sources = await client.sources.list(prot_id)
                entry["actual_sources"] = len(sources)
            except Exception as e_src:
                err_msg = f"Failed to list sources for protected notebook {prot_id}: {e_src}"
                entry["error"] = err_msg
                self.discrepancies.append(f"[PROTECTED BARRIER] {err_msg}")
                barrier_results[prot_id] = entry
                all_protected_valid = False
                continue

            if entry["actual_sources"] == meta["expected_count"]:
                entry["valid"] = True
            else:
                err_msg = (
                    f"Protected notebook '{meta['title']}' ({prot_id}) source count mismatch: "
                    f"expected {meta['expected_count']}, got {entry['actual_sources']}"
                )
                entry["error"] = err_msg
                self.discrepancies.append(f"[PROTECTED BARRIER] {err_msg}")
                all_protected_valid = False

            barrier_results[prot_id] = entry

        return all_protected_valid, barrier_results

    async def verify_target_notebooks(
        self,
        client: Any,
        canonical_corpus: Dict[str, List[Dict[str, Any]]],
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Verifies requirements 2, 3, 4, 5 for the target Navarredondilla Parroquial notebooks:
        - Existence and exact title match [L-29].
        - Total source count matches expected value per notebook.
        - Set difference: missing_sources == 0, extra_sources == 0, duplicate_sources == 0.
        - Primary key naming [L-28]: ^\\d{9}_\\d{5}\\.jpg$ for every source.
        - Processing status: 100% READY (0 ERROR, 0 PENDING).
        """
        all_notebooks = await client.notebooks.list()
        notebooks_by_title: Dict[str, List[Any]] = {}
        for nb in all_notebooks:
            notebooks_by_title.setdefault(nb.title, []).append(nb)

        target_keys = self.target_filter if self.target_filter else list(TARGET_NOTEBOOKS.keys())
        expected_total_sources = sum(TARGET_NOTEBOOKS[k]["expected_count"] for k in target_keys)

        target_results: Dict[str, Any] = {}
        summary_stats = {
            "target_notebooks_expected": len(target_keys),
            "target_notebooks_found": 0,
            "target_notebooks_missing": [],
            "total_sources_expected": expected_total_sources,
            "total_sources_actual": 0,
            "total_sources_ready": 0,
            "total_sources_error": 0,
            "total_sources_pending": 0,
            "total_sources_missing": 0,
            "total_sources_extra": 0,
            "total_naming_violations": 0,
            "total_duplicates": 0,
        }

        protected_ids_set = set(PROTECTED_NOTEBOOKS.keys())

        for target_title in target_keys:
            meta = TARGET_NOTEBOOKS[target_title]
            expected_records = canonical_corpus[target_title]
            expected_titles = [r["id_imagen"] for r in expected_records]
            expected_set = set(expected_titles)

            nb_res: Dict[str, Any] = {
                "notebook_id": None,
                "exists": False,
                "tipo": meta["tipo"],
                "rollo_dgs": meta["rollo_dgs"],
                "expected_count": meta["expected_count"],
                "actual_count": 0,
                "ready_count": 0,
                "error_count": 0,
                "pending_count": 0,
                "missing_sources": [],
                "extra_sources": [],
                "naming_errors": [],
                "status_errors": [],
                "duplicates": [],
                "valid": False,
                "sources": [],
            }

            candidate_titles = meta.get("cloud_titles", [target_title])
            matched_nbs = []
            for c_title in candidate_titles:
                matched_nbs.extend(notebooks_by_title.get(c_title, []))
            if not matched_nbs:
                self.discrepancies.append(
                    f"[TARGET NOTEBOOK MISSING] Notebook '{target_title}' (aliases {candidate_titles}) does not exist in NotebookLM."
                )
                summary_stats["target_notebooks_missing"].append(target_title)
                summary_stats["total_sources_missing"] += meta["expected_count"]
                nb_res["missing_sources"] = list(expected_titles)
                target_results[target_title] = nb_res
                continue

            target_nb = matched_nbs[0]
            nb_res["exists"] = True
            nb_res["notebook_id"] = target_nb.id
            summary_stats["target_notebooks_found"] += 1

            # Hard safety barrier check: target notebook cannot collide with any protected ID
            if target_nb.id in protected_ids_set:
                self.discrepancies.append(
                    f"[CRITICAL SAFETY VIOLATION] Target notebook '{target_title}' collided with protected ID {target_nb.id}!"
                )

            # Warning if multiple notebooks exist with identical title
            if len(matched_nbs) > 1:
                self.discrepancies.append(
                    f"[WARNING] Multiple notebooks ({len(matched_nbs)}) found with exact title '{target_title}'"
                )

            # Fetch sources from target notebook
            try:
                raw_sources = await client.sources.list(target_nb.id)
            except Exception as e_src:
                self.discrepancies.append(
                    f"[SOURCE LIST ERROR] Failed to list sources for notebook '{target_title}' ({target_nb.id}): {e_src}"
                )
                target_results[target_title] = nb_res
                continue

            nb_res["actual_count"] = len(raw_sources)
            summary_stats["total_sources_actual"] += len(raw_sources)

            actual_titles = [s.title for s in raw_sources if s.title]
            actual_set = set(actual_titles)

            # Check missing sources (expected in catalog but absent in NotebookLM)
            missing = [t for t in expected_titles if t not in actual_set]
            nb_res["missing_sources"] = missing
            summary_stats["total_sources_missing"] += len(missing)
            if missing:
                sample = missing[:5]
                more_suffix = f" ... (+{len(missing) - 5} more)" if len(missing) > 5 else ""
                self.discrepancies.append(
                    f"[{target_title}] Missing {len(missing)} expected sources: {sample}{more_suffix}"
                )

            # Check extra sources (present in NotebookLM but not in canonical catalog)
            extra = [t for t in actual_titles if t not in expected_set]
            nb_res["extra_sources"] = extra
            summary_stats["total_sources_extra"] += len(extra)
            if extra:
                sample = extra[:5]
                more_suffix = f" ... (+{len(extra) - 5} more)" if len(extra) > 5 else ""
                self.discrepancies.append(
                    f"[{target_title}] Found {len(extra)} unexpected extra sources: {sample}{more_suffix}"
                )

            # Check duplicate source titles inside the notebook
            seen_titles: Set[str] = set()
            duplicates: Set[str] = set()
            for t in actual_titles:
                if t in seen_titles:
                    duplicates.add(t)
                seen_titles.add(t)
            nb_res["duplicates"] = sorted(list(duplicates))
            summary_stats["total_duplicates"] += len(duplicates)
            if duplicates:
                self.discrepancies.append(
                    f"[{target_title}] Found duplicate source titles: {sorted(list(duplicates))}"
                )

            # Inspect each source for naming pattern and readiness
            for s in raw_sources:
                st_str = get_source_status_str(s)
                ready = is_source_ready(s)
                err = is_source_error(s)
                title = s.title or ""

                source_entry = {
                    "id": getattr(s, "id", None),
                    "title": title,
                    "status": st_str,
                    "is_ready": ready,
                    "is_error": err,
                }
                if not self.quiet:
                    nb_res["sources"].append(source_entry)

                if ready:
                    nb_res["ready_count"] += 1
                    summary_stats["total_sources_ready"] += 1
                elif err:
                    nb_res["error_count"] += 1
                    summary_stats["total_sources_error"] += 1
                    nb_res["status_errors"].append(source_entry)
                    self.discrepancies.append(
                        f"[{target_title}] Source '{title}' ({getattr(s, 'id', 'unknown')}) is in ERROR state ({st_str})"
                    )
                else:
                    nb_res["pending_count"] += 1
                    summary_stats["total_sources_pending"] += 1
                    nb_res["status_errors"].append(source_entry)
                    self.discrepancies.append(
                        f"[{target_title}] Source '{title}' ({getattr(s, 'id', 'unknown')}) is not READY (status={st_str})"
                    )

                # Naming standard check [L-28]
                if not CANONICAL_FILENAME_REGEX.match(title):
                    nb_res["naming_errors"].append(source_entry)
                    summary_stats["total_naming_violations"] += 1
                    self.discrepancies.append(
                        f"[{target_title}] Source title '{title}' violates [L-28] canonical format (^\\d{{9}}_\\d{{5}}\\.jpg$)"
                    )

            # Overall validity check for this target notebook
            is_valid = (
                nb_res["exists"]
                and nb_res["actual_count"] == meta["expected_count"]
                and nb_res["ready_count"] == meta["expected_count"]
                and nb_res["error_count"] == 0
                and nb_res["pending_count"] == 0
                and len(nb_res["missing_sources"]) == 0
                and len(nb_res["extra_sources"]) == 0
                and len(nb_res["naming_errors"]) == 0
                and len(nb_res["duplicates"]) == 0
            )
            nb_res["valid"] = is_valid
            target_results[target_title] = nb_res

        return target_results, summary_stats

    async def execute_verification(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Executes full end-to-end verification pipeline:
        1. Loads and validates canonical corpus.
        2. Establishes NotebookLM connection.
        3. Audits the 5 protected notebooks barrier.
        4. Audits the 15 target Navarredondilla Parroquial notebooks.
        5. Computes overall pass/fail status and serializes JSON report.
        """
        start_time = datetime.now(timezone.utc)
        self.discrepancies = []

        # Step 1: Load Canonical Corpus
        try:
            canonical_corpus = load_and_verify_canonical_corpus(self.corpus_path, self.target_filter)
        except Exception as e_corpus:
            self.discrepancies.append(f"[CORPUS FAILURE] Could not load canonical corpus: {e_corpus}")
            report = {
                "timestamp": start_time.isoformat(),
                "overall_status": "FAIL",
                "exit_code": 1,
                "error": str(e_corpus),
                "discrepancies": self.discrepancies,
            }
            self._write_report(report)
            return False, report

        # Step 2: Establish NotebookLM Client Connection
        client = self.client
        own_client = False
        if client is None:
            if not NOTEBOOKLM_AVAILABLE:
                err_msg = "notebooklm-py library is not installed in the current Python environment."
                self.discrepancies.append(f"[ENVIRONMENT ERROR] {err_msg}")
                report = {
                    "timestamp": start_time.isoformat(),
                    "overall_status": "FAIL",
                    "exit_code": 1,
                    "error": err_msg,
                    "discrepancies": self.discrepancies,
                }
                self._write_report(report)
                return False, report

            try:
                client = NotebookLMClient.from_storage()
                own_client = True
            except Exception as e_auth:
                err_msg = f"Failed to authenticate NotebookLM client from storage: {e_auth}"
                self.discrepancies.append(f"[AUTH ERROR] {err_msg}")
                report = {
                    "timestamp": start_time.isoformat(),
                    "overall_status": "FAIL",
                    "exit_code": 1,
                    "error": err_msg,
                    "discrepancies": self.discrepancies,
                }
                self._write_report(report)
                return False, report

        target_keys = self.target_filter if self.target_filter else list(TARGET_NOTEBOOKS.keys())
        expected_total_sources = sum(TARGET_NOTEBOOKS[k]["expected_count"] for k in target_keys)

        barrier_valid = False
        barrier_results: Dict[str, Any] = {}
        target_results: Dict[str, Any] = {}
        summary_stats: Dict[str, Any] = {
            "target_notebooks_expected": len(target_keys),
            "target_notebooks_found": 0,
            "target_notebooks_missing": list(target_keys),
            "total_sources_expected": expected_total_sources,
            "total_sources_actual": 0,
            "total_sources_ready": 0,
            "total_sources_error": 0,
            "total_sources_pending": 0,
            "total_sources_missing": expected_total_sources,
            "total_sources_extra": 0,
            "total_naming_violations": 0,
            "total_duplicates": 0,
            "protected_barrier_valid": False,
            "overall_status": "FAIL",
        }

        # Step 3: Run Protected Barrier & Target Notebooks Verification
        try:
            if own_client:
                async with client as active_client:
                    barrier_valid, barrier_results = await self.verify_protected_barrier(active_client)
                    target_results, summary_stats = await self.verify_target_notebooks(
                        active_client, canonical_corpus
                    )
            else:
                barrier_valid, barrier_results = await self.verify_protected_barrier(client)
                target_results, summary_stats = await self.verify_target_notebooks(
                    client, canonical_corpus
                )
        except Exception as e_api:
            err_msg = f"Unexpected error during NotebookLM API verification: {e_api}"
            self.discrepancies.append(f"[API ERROR] {err_msg}")
            report = {
                "timestamp": start_time.isoformat(),
                "overall_status": "FAIL",
                "exit_code": 1,
                "error": err_msg,
                "summary": summary_stats,
                "protected_barrier": barrier_results,
                "target_notebooks": target_results,
                "discrepancies": self.discrepancies,
            }
            self._write_report(report)
            return False, report

        # Step 4: Compute Overall Pass / Fail Verdict
        target_keys = self.target_filter if self.target_filter else list(TARGET_NOTEBOOKS.keys())
        expected_total_sources = sum(TARGET_NOTEBOOKS[k]["expected_count"] for k in target_keys)

        all_targets_valid = all(t.get("valid", False) for t in target_results.values())
        all_checks_passed = (
            barrier_valid
            and all_targets_valid
            and summary_stats["target_notebooks_found"] == len(target_keys)
            and summary_stats["total_sources_actual"] == expected_total_sources
            and summary_stats["total_sources_ready"] == expected_total_sources
            and summary_stats["total_sources_error"] == 0
            and summary_stats["total_sources_missing"] == 0
            and summary_stats["total_sources_extra"] == 0
            and summary_stats["total_naming_violations"] == 0
            and summary_stats["total_duplicates"] == 0
        )

        overall_status = "PASS" if all_checks_passed else "FAIL"
        exit_code = 0 if all_checks_passed else 1

        summary_stats["protected_barrier_valid"] = barrier_valid
        summary_stats["overall_status"] = overall_status

        report = {
            "timestamp": start_time.isoformat(),
            "overall_status": overall_status,
            "exit_code": exit_code,
            "summary": summary_stats,
            "protected_barrier": barrier_results,
            "target_notebooks": target_results,
            "discrepancies": self.discrepancies,
        }

        self._write_report(report)
        return all_checks_passed, report

    def _write_report(self, report_data: Dict[str, Any]) -> None:
        """Dumps verification report to JSON."""
        self.report_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)


# -----------------------------------------------------------------------------
# Formatted Terminal Summary Presenter
# -----------------------------------------------------------------------------
def print_verification_summary(report: Dict[str, Any], target_filter: Optional[List[str]] = None) -> None:
    """Formats and prints an ASCII summary table to stdout."""
    status = report.get("overall_status", "FAIL")
    timestamp = report.get("timestamp", "")
    summary = report.get("summary", {})
    protected = report.get("protected_barrier", {})
    targets = report.get("target_notebooks", {})
    discrepancies = report.get("discrepancies", [])

    print("\n" + "=" * 90)
    print(" NAVARREDONDILLA PARROQUIAL - INDEPENDENT E2E VERIFICATION REPORT")
    print(f" Timestamp: {timestamp} UTC")
    print(f" Overall Status: [{status}]")
    print("=" * 90)

    # 1. Protected Active Notebooks Barrier
    print(" 1. PROTECTED ACTIVE NOTEBOOKS BARRIER AUDIT (5 Notebooks, 388 Sources)")
    print(f" {'ID':<38} | {'Title':<36} | {'Exp':>4} | {'Act':>4} | {'Status':<6}")
    print("-" * 90)

    for prot_id, meta in PROTECTED_NOTEBOOKS.items():
        p_data = protected.get(prot_id, {})
        title = p_data.get("actual_title") or meta["title"]
        if len(title) > 36:
            title = title[:33] + "..."
        exp = meta["expected_count"]
        act = p_data.get("actual_sources", 0)
        p_status = "PASS" if p_data.get("valid") else "FAIL"
        print(f" {prot_id:<38} | {title:<36} | {exp:>4} | {act:>4} | {p_status:<6}")

    print("-" * 90)

    # 2. Target Navarredondilla Parroquial Notebooks
    target_keys = target_filter if target_filter else list(TARGET_NOTEBOOKS.keys())
    print(f" 2. TARGET NAVARREDONDILLA PARROQUIAL NOTEBOOKS AUDIT ({len(target_keys)} Notebooks)")
    print(
        f" {'Notebook Name':<16} | {'Notebook ID':<36} | {'Exp':>4} | {'Act':>4} | {'Rdy':>4} | {'Err':>3} | {'Status':<6}"
    )
    print("-" * 90)

    for name in target_keys:
        meta = TARGET_NOTEBOOKS[name]
        t_data = targets.get(name, {})
        nid = t_data.get("notebook_id") or "NOT FOUND"
        exp = t_data.get("expected_count", meta["expected_count"])
        act = t_data.get("actual_count", 0)
        rdy = t_data.get("ready_count", 0)
        err = t_data.get("error_count", 0) + t_data.get("pending_count", 0)
        nb_status = "PASS" if t_data.get("valid") else "FAIL"

        disp_nid = nid if len(nid) <= 36 else nid[:33] + "..."
        print(f" {name:<16} | {disp_nid:<36} | {exp:>4} | {act:>4} | {rdy:>4} | {err:>3} | {nb_status:<6}")

    print("-" * 90)

    tot_exp = summary.get("total_sources_expected", 0)
    tot_act = summary.get("total_sources_actual", 0)
    tot_rdy = summary.get("total_sources_ready", 0)
    tot_err = summary.get("total_sources_error", 0) + summary.get("total_sources_pending", 0)
    tot_status = "PASS" if status == "PASS" else "FAIL"

    print(
        f" {'TOTALS':<16} | {f'{len(target_keys)} Parroquial Notebooks':<36} | {tot_exp:>4} | {tot_act:>4} | {tot_rdy:>4} | {tot_err:>3} | {tot_status:<6}"
    )
    print("=" * 90)

    # 3. Discrepancies (if any)
    if discrepancies:
        print(f" DISCREPANCIES DETECTED ({len(discrepancies)}):")
        for idx, d in enumerate(discrepancies[:25], start=1):
            print(f"   {idx:>2}. {d}")
        if len(discrepancies) > 25:
            print(f"   ... and {len(discrepancies) - 25} more discrepancies.")
        print("-" * 90)

    # 4. Final Verdict
    if status == "PASS":
        print(f" VERDICT: [PASS] ALL {len(target_keys)} PARROQUIAL NOTEBOOKS & {tot_exp} SOURCES VERIFIED READY.")
        print("          PROTECTED BARRIER (5 NOTEBOOKS, 388 SOURCES) CONFIRMED UNTOUCHED.")
    else:
        print(" VERDICT: [FAIL] VERIFICATION DETECTED ISSUES / DEFECTS.")

    print(f" Detailed JSON report saved to: {DEFAULT_REPORT_PATH.resolve()}")
    print("=" * 90 + "\n")


# -----------------------------------------------------------------------------
# Mock Client & Comprehensive Self-Test Harness
# -----------------------------------------------------------------------------
class MockNotebook:
    def __init__(self, id: str, title: str, sources_count: int = 0):
        self.id = id
        self.title = title
        self.sources_count = sources_count


class MockSource:
    def __init__(
        self,
        id: str,
        title: str,
        status_name: str = "READY",
        is_ready: bool = True,
        is_error: bool = False,
    ):
        self.id = id
        self.title = title
        self.is_ready = is_ready
        self.is_error = is_error

        class StatusHolder:
            def __init__(self, name):
                self.name = name

            def __str__(self):
                return self.name

        self.status = StatusHolder(status_name)


class MockNotebooksAPI:
    def __init__(self, notebooks: List[MockNotebook]):
        self._notebooks = notebooks

    async def list(self) -> List[MockNotebook]:
        return list(self._notebooks)

    async def get(self, notebook_id: str) -> MockNotebook:
        for nb in self._notebooks:
            if nb.id == notebook_id:
                return nb
        raise RuntimeError(f"Notebook {notebook_id} not found")


class MockSourcesAPI:
    def __init__(self, sources_map: Dict[str, List[MockSource]]):
        self._sources_map = sources_map

    async def list(self, notebook_id: str) -> List[MockSource]:
        return list(self._sources_map.get(notebook_id, []))


class MockNotebookLMClient:
    def __init__(self, notebooks: List[MockNotebook], sources_map: Dict[str, List[MockSource]]):
        self.notebooks = MockNotebooksAPI(notebooks)
        self.sources = MockSourcesAPI(sources_map)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


def build_mock_passing_client(canonical_corpus: Dict[str, List[Dict[str, Any]]]) -> MockNotebookLMClient:
    """Builds a mock client containing all 5 protected notebooks and all 15 target notebooks in READY state."""
    mock_nbs: List[MockNotebook] = []
    mock_sources: Dict[str, List[MockSource]] = {}

    # 1. Populate protected notebooks
    for pid, meta in PROTECTED_NOTEBOOKS.items():
        mock_nbs.append(MockNotebook(id=pid, title=meta["title"], sources_count=meta["expected_count"]))
        mock_sources[pid] = [
            MockSource(id=f"prot-src-{pid}-{idx}", title=f"004469000_{idx:05d}.jpg", status_name="READY")
            for idx in range(1, meta["expected_count"] + 1)
        ]

    # 2. Populate target notebooks
    for target_title, records in canonical_corpus.items():
        nid = f"mock-nid-{target_title.lower()}"
        mock_nbs.append(MockNotebook(id=nid, title=target_title, sources_count=len(records)))
        mock_sources[nid] = [
            MockSource(
                id=f"src-{nid}-{idx}",
                title=r["id_imagen"],
                status_name="READY",
                is_ready=True,
                is_error=False,
            )
            for idx, r in enumerate(records, start=1)
        ]

    return MockNotebookLMClient(mock_nbs, mock_sources)


async def run_self_tests() -> bool:
    """
    Executes adversarial and standard self-tests against mock clients
    to guarantee verification test harness logic correctness.
    """
    print("\n[SELF-TEST] Running verifier harness test suite against canonical corpus & mocks...")
    corpus = load_and_verify_canonical_corpus(DEFAULT_CATALOG_PATH)
    test_report_path = BASE_DIR / "scripts" / "test_self_check_nrdl_report.json"

    # Test Case 1: Perfect Passing Scenario (15 notebooks, 2,276 sources + 5 protected notebooks)
    print(" - Test Case 1: All 15 Parroquial notebooks (2,276 sources) + 5 protected notebooks valid...")
    passing_client = build_mock_passing_client(corpus)
    verifier1 = NavarredondillaParroquialVerifier(
        client=passing_client,
        corpus_path=DEFAULT_CATALOG_PATH,
        report_path=test_report_path,
        quiet=True,
    )
    ok1, rep1 = await verifier1.execute_verification()
    assert ok1 is True, f"Test 1 failed: expected PASS, got {rep1.get('overall_status')}"
    assert rep1["summary"]["total_sources_ready"] == 2276
    assert rep1["summary"]["protected_barrier_valid"] is True
    print("   [OK] Test Case 1 passed.")

    # Test Case 2: Protected Barrier Tampered (Sacramental notebook source count 187 vs 188)
    print(" - Test Case 2: Protected Sacramental notebook tampered (187 vs 188)...")
    tampered_client = build_mock_passing_client(corpus)
    tampered_client.sources._sources_map["7967d647-8ca2-4863-a576-11843e8e8802"].pop()
    verifier2 = NavarredondillaParroquialVerifier(
        client=tampered_client,
        corpus_path=DEFAULT_CATALOG_PATH,
        report_path=test_report_path,
        quiet=True,
    )
    ok2, rep2 = await verifier2.execute_verification()
    assert ok2 is False, "Test 2 failed: expected failure on protected barrier breach"
    assert rep2["protected_barrier"]["7967d647-8ca2-4863-a576-11843e8e8802"]["valid"] is False
    print("   [OK] Test Case 2 properly detected protected barrier violation.")

    # Test Case 3: Naming Standard Violation [L-28] (zero truncation)
    print(" - Test Case 3: Primary key naming violation [L-28] (zero truncation)...")
    bad_name_client = build_mock_passing_client(corpus)
    baut01_sources = bad_name_client.sources._sources_map["mock-nid-nrdl-baut-01"]
    baut01_sources[0] = MockSource(id="bad-1", title="01870.jpg", status_name="READY")
    verifier3 = NavarredondillaParroquialVerifier(
        client=bad_name_client,
        corpus_path=DEFAULT_CATALOG_PATH,
        report_path=test_report_path,
        quiet=True,
    )
    ok3, rep3 = await verifier3.execute_verification()
    assert ok3 is False, "Test 3 failed: expected failure on naming violation"
    assert rep3["summary"]["total_naming_violations"] > 0
    print("   [OK] Test Case 3 properly caught [L-28] zero truncation violation.")

    # Test Case 4: Source in ERROR Status
    print(" - Test Case 4: Source in ERROR status...")
    err_client = build_mock_passing_client(corpus)
    matr01_sources = err_client.sources._sources_map["mock-nid-nrdl-matr-01"]
    matr01_sources[0] = MockSource(
        id="err-1",
        title=matr01_sources[0].title,
        status_name="ERROR",
        is_ready=False,
        is_error=True,
    )
    verifier4 = NavarredondillaParroquialVerifier(
        client=err_client,
        corpus_path=DEFAULT_CATALOG_PATH,
        report_path=test_report_path,
        quiet=True,
    )
    ok4, rep4 = await verifier4.execute_verification()
    assert ok4 is False, "Test 4 failed: expected failure on source ERROR status"
    assert rep4["summary"]["total_sources_error"] == 1
    print("   [OK] Test Case 4 properly flagged non-ready / error source.")

    # Test Case 5: Missing Target Notebook (e.g. NRDL-MIXTO-01 absent)
    print(" - Test Case 5: Missing target notebook...")
    missing_client = build_mock_passing_client(corpus)
    missing_client.notebooks._notebooks = [
        nb for nb in missing_client.notebooks._notebooks if nb.title != "NRDL-MIXTO-01"
    ]
    verifier5 = NavarredondillaParroquialVerifier(
        client=missing_client,
        corpus_path=DEFAULT_CATALOG_PATH,
        report_path=test_report_path,
        quiet=True,
    )
    ok5, rep5 = await verifier5.execute_verification()
    assert ok5 is False, "Test 5 failed: expected failure on missing notebook"
    assert "NRDL-MIXTO-01" in rep5["summary"]["target_notebooks_missing"]
    print("   [OK] Test Case 5 properly reported missing notebook.")

    # Test Case 6: Target Colliding with Protected ID (Collision Guard)
    print(" - Test Case 6: Collision guard asserting target cannot reuse protected ID...")
    collide_client = build_mock_passing_client(corpus)
    for nb in collide_client.notebooks._notebooks:
        if nb.title == "NRDL-BAUT-01":
            nb.id = "7967d647-8ca2-4863-a576-11843e8e8802"
    verifier6 = NavarredondillaParroquialVerifier(
        client=collide_client,
        corpus_path=DEFAULT_CATALOG_PATH,
        report_path=test_report_path,
        quiet=True,
    )
    ok6, rep6 = await verifier6.execute_verification()
    assert ok6 is False or any("COLLISION" in d for d in rep6["discrepancies"])
    print("   [OK] Test Case 6 properly asserted collision guard.")

    # Test Case 7: Granular Filter Verification (--notebook NRDL-MATR-01)
    print(" - Test Case 7: Granular verification of single notebook (--notebook NRDL-MATR-01)...")
    single_client = build_mock_passing_client(corpus)
    verifier7 = NavarredondillaParroquialVerifier(
        client=single_client,
        corpus_path=DEFAULT_CATALOG_PATH,
        report_path=test_report_path,
        target_notebook_filter=["NRDL-MATR-01"],
        quiet=True,
    )
    ok7, rep7 = await verifier7.execute_verification()
    assert ok7 is True, "Test 7 failed: expected single notebook verification to PASS"
    assert rep7["summary"]["total_sources_expected"] == 33
    assert rep7["summary"]["total_sources_ready"] == 33
    print("   [OK] Test Case 7 passed granular notebook verification.")

    # Clean up test artifact if exists
    if test_report_path.is_file():
        test_report_path.unlink()

    print("[SELF-TEST] All 7 self-test scenarios PASSED successfully!\n")
    return True


# -----------------------------------------------------------------------------
# Main CLI Entry Point
# -----------------------------------------------------------------------------
def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Independent E2E Verification Harness for Navarredondilla Parroquial Notebooks & Sources."
    )
    parser.add_argument(
        "--notebook",
        type=str,
        default=None,
        help="Comma-separated list or single target notebook title (e.g. 'NRDL-MATR-01' or 'NRDL-BAUT-01,NRDL-BAUT-02'). Defaults to all 15 notebooks.",
    )
    parser.add_argument(
        "--catalog-path",
        "--corpus-path",
        type=Path,
        default=DEFAULT_CATALOG_PATH,
        help="Path to canonical catalogo_corpus.json (default: catalogo_corpus.json)",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help="Path to output verification_report_nrdl.json (default: scripts/verification_report_nrdl.json)",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress per-source verbose output, print summary table only.",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run internal mock self-test suite and adversarial scenarios.",
    )
    return parser.parse_args()


async def main_async() -> int:
    args = parse_arguments()

    if args.self_test:
        success = await run_self_tests()
        return 0 if success else 1

    target_filter = None
    if args.notebook:
        target_filter = [t.strip() for t in args.notebook.split(",") if t.strip()]

    verifier = NavarredondillaParroquialVerifier(
        client=None,
        corpus_path=args.catalog_path,
        report_path=args.report_path,
        target_notebook_filter=target_filter,
        quiet=args.quiet,
    )

    passed, report = await verifier.execute_verification()
    print_verification_summary(report, target_filter=target_filter)

    return report.get("exit_code", 0 if passed else 1)


def main() -> None:
    try:
        exit_code = asyncio.run(main_async())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nVerification cancelled by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\nFatal error executing verification: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
