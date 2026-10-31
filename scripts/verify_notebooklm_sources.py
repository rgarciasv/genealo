#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Independent E2E Verification Harness for NotebookLM Sources & Notebooks.
Project: Genealo - Catastro de Ensenada (Personal de Legos)

Validates:
1. Active Notebook Protection:
   Notebook '7967d647-8ca2-4863-a576-11843e8e8802' ('Lib. Baut. Navarre Vol. 1 (1594-1695)')
   is alive and has exactly 188 sources.
2. Target Notebooks Existence [L-29]:
   The 4 target mono-locality notebooks exist with exact canonical names:
   - 'NRDL-ENSENADA-LEGOS-01'
   - 'JMOL-ENSENADA-LEGOS-01'
   - 'VLLR-ENSENADA-LEGOS-01'
   - 'NDRN-ENSENADA-LEGOS-01'
3. Source Completeness & Exact Alignment against 'catalogo_corpus.json' (BOM-safe utf-8-sig):
   - NRDL: exactly 87 sources (range 881 to 967 on roll 004469033)
   - JMOL: exactly 28 sources (range 952 to 979 on roll 004469028)
   - VLLR: exactly 51 sources (range 901 to 951 on roll 004469028)
   - NDRN: exactly 34 sources (range 980 to 1013 on roll 004469028)
   Total: exactly 200 sources.
   Detects any missing or unexpected/extra sources.
4. Source Naming Standard [L-28]:
   Every source title strictly matches '{DGS}_{FOTOGRAMA}.jpg' without zero truncation.
5. Source Status:
   All sources must be in READY status with 0 errors and 0 pending.
6. Detailed Reporting:
   Produces a formatted ASCII summary and dumps 'scripts/verification_report.json'.
   Returns exit code 0 if all 200 sources and 4 notebooks are valid; non-zero otherwise.
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
DEFAULT_REPORT_PATH = BASE_DIR / "scripts" / "verification_report.json"

PROTECTED_NOTEBOOK_ID = "7967d647-8ca2-4863-a576-11843e8e8802"
PROTECTED_NOTEBOOK_TITLE = "Lib. Baut. Navarre Vol. 1 (1594-1695)"
PROTECTED_EXPECTED_SOURCES_COUNT = 188

TARGET_NOTEBOOKS = {
    "NRDL-ENSENADA-LEGOS-01": {
        "localidad": "Navarredondilla",
        "parroquia": "NRDL",
        "rollo_dgs": "004469033",
        "expected_count": 87,
        "fotograma_start": 881,
        "fotograma_end": 967,
    },
    "JMOL-ENSENADA-LEGOS-01": {
        "localidad": "San Juan del Molinillo",
        "parroquia": "JMOL",
        "rollo_dgs": "004469028",
        "expected_count": 28,
        "fotograma_start": 952,
        "fotograma_end": 979,
    },
    "VLLR-ENSENADA-LEGOS-01": {
        "localidad": "El Villarejo",
        "parroquia": "VLLR",
        "rollo_dgs": "004469028",
        "expected_count": 51,
        "fotograma_start": 901,
        "fotograma_end": 951,
    },
    "NDRN-ENSENADA-LEGOS-01": {
        "localidad": "Navandrinal",
        "parroquia": "NDRN",
        "rollo_dgs": "004469028",
        "expected_count": 34,
        "fotograma_start": 980,
        "fotograma_end": 1013,
    },
}

TOTAL_EXPECTED_TARGET_SOURCES = 200
CANONICAL_FILENAME_REGEX = re.compile(r"^\d{9}_\d{5}\.jpg$")

# -----------------------------------------------------------------------------
# Corpus Loading & Canonical Cross-Check Preparation
# -----------------------------------------------------------------------------
def load_and_verify_canonical_corpus(corpus_path: Path) -> Dict[str, List[Dict[str, Any]]]:
    """
    Loads 'catalogo_corpus.json' using 'utf-8-sig' to strip UTF-8 BOM.
    Extracts and verifies the 200 target records across the 4 target notebooks.
    Ensures the canonical catalog itself is internally consistent.
    """
    if not corpus_path.is_file():
        raise FileNotFoundError(f"Canonical corpus file not found: {corpus_path}")

    with open(corpus_path, "r", encoding="utf-8-sig") as f:
        corpus_data = json.load(f)

    if not isinstance(corpus_data, list):
        raise ValueError(f"Expected list in corpus JSON, got {type(corpus_data)}")

    expected_records: Dict[str, List[Dict[str, Any]]] = {}

    for target_title, meta in TARGET_NOTEBOOKS.items():
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

        # Verify each record's format and range
        for rec in matched:
            img_id = rec.get("id_imagen", "")
            dgs = rec.get("rollo_dgs", "")
            fotograma_num = int(rec.get("fotograma_numero", 0))

            if not CANONICAL_FILENAME_REGEX.match(img_id):
                raise ValueError(
                    f"Corpus record {img_id} violates [L-28] canonical filename pattern ({{DGS}}_{{FOTOGRAMA}}.jpg)"
                )

            if dgs != meta["rollo_dgs"]:
                raise ValueError(
                    f"Corpus record {img_id} has unexpected rollo {dgs}, expected {meta['rollo_dgs']}"
                )

            if not (meta["fotograma_start"] <= fotograma_num <= meta["fotograma_end"]):
                raise ValueError(
                    f"Corpus record {img_id} fotograma {fotograma_num} outside expected range "
                    f"[{meta['fotograma_start']}, {meta['fotograma_end']}]"
                )

    total_count = sum(len(recs) for recs in expected_records.values())
    if total_count != TOTAL_EXPECTED_TARGET_SOURCES:
        raise ValueError(
            f"Corpus total target records mismatch: expected {TOTAL_EXPECTED_TARGET_SOURCES}, got {total_count}"
        )

    return expected_records


# -----------------------------------------------------------------------------
# Helper Utilities for Source Inspection
# -----------------------------------------------------------------------------
def get_source_status_str(source: Any) -> str:
    """Safely extracts the string status representation from a Source object."""
    if hasattr(source, "status"):
        st = source.status
        if hasattr(st, "name"):
            return st.name
        return str(st)
    return "UNKNOWN"


def is_source_ready(source: Any) -> bool:
    """Determines whether a source is confirmed READY."""
    if getattr(source, "is_ready", False):
        return True
    if SourceStatus and getattr(source, "status", None) == SourceStatus.READY:
        return True
    if get_source_status_str(source).upper() == "READY":
        return True
    return False


def is_source_error(source: Any) -> bool:
    """Determines whether a source is in ERROR state."""
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
class NotebookLMVerifier:
    """
    Independent verification engine querying NotebookLM API to cross-validate
    the 4 Ensenada Legos notebooks and the protected active notebook.
    """

    def __init__(
        self,
        client: Optional[Any] = None,
        corpus_path: Optional[Path] = None,
        report_path: Optional[Path] = None,
    ):
        self.client = client
        self.corpus_path = corpus_path or DEFAULT_CATALOG_PATH
        self.report_path = report_path or DEFAULT_REPORT_PATH
        self.discrepancies: List[str] = []

    async def verify_protected_notebook(self, client: Any) -> Dict[str, Any]:
        """
        Verifies requirement 1: Active notebook protection.
        Notebook 7967d647-8ca2-4863-a576-11843e8e8802 must be alive and have exactly 188 sources.
        """
        result: Dict[str, Any] = {
            "notebook_id": PROTECTED_NOTEBOOK_ID,
            "expected_title": PROTECTED_NOTEBOOK_TITLE,
            "actual_title": None,
            "is_alive": False,
            "actual_sources": 0,
            "expected_sources": PROTECTED_EXPECTED_SOURCES_COUNT,
            "valid": False,
            "error": None,
        }

        try:
            # Query notebook metadata
            try:
                nb = await client.notebooks.get(PROTECTED_NOTEBOOK_ID)
                result["actual_title"] = nb.title
                result["is_alive"] = True
            except Exception as e_get:
                # Fallback: search in list
                all_nbs = await client.notebooks.list()
                found = next((n for n in all_nbs if n.id == PROTECTED_NOTEBOOK_ID), None)
                if found:
                    result["actual_title"] = found.title
                    result["is_alive"] = True
                else:
                    result["error"] = f"Protected notebook not found: {e_get}"
                    self.discrepancies.append(
                        f"[PROTECTED NOTEBOOK] ID {PROTECTED_NOTEBOOK_ID} could not be retrieved: {e_get}"
                    )
                    return result

            # Query sources count
            sources = await client.sources.list(PROTECTED_NOTEBOOK_ID)
            result["actual_sources"] = len(sources)

            # Check exact 188 sources
            if result["actual_sources"] == PROTECTED_EXPECTED_SOURCES_COUNT:
                result["valid"] = True
            else:
                err_msg = (
                    f"Protected notebook source count mismatch: expected {PROTECTED_EXPECTED_SOURCES_COUNT}, "
                    f"got {result['actual_sources']}"
                )
                result["error"] = err_msg
                self.discrepancies.append(f"[PROTECTED NOTEBOOK] {err_msg}")

        except Exception as exc:
            err_msg = f"Exception querying protected notebook: {exc}"
            result["error"] = err_msg
            self.discrepancies.append(f"[PROTECTED NOTEBOOK] {err_msg}")

        return result

    async def verify_target_notebooks(
        self, client: Any, canonical_corpus: Dict[str, List[Dict[str, Any]]]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        Verifies requirements 2, 3, 4, 5:
        - Target notebooks exist with exact canonical names [L-29].
        - Source completeness & cross-check with catalogo_corpus.json (87, 28, 51, 34 = 200).
        - Source naming standard {DGS}_{FOTOGRAMA}.jpg [L-28].
        - Source status READY with 0 errors.
        """
        all_notebooks = await client.notebooks.list()
        notebooks_by_title: Dict[str, List[Any]] = {}
        for nb in all_notebooks:
            notebooks_by_title.setdefault(nb.title, []).append(nb)

        target_results: Dict[str, Any] = {}
        summary_stats = {
            "target_notebooks_expected": len(TARGET_NOTEBOOKS),
            "target_notebooks_found": 0,
            "target_notebooks_missing": [],
            "total_sources_expected": TOTAL_EXPECTED_TARGET_SOURCES,
            "total_sources_actual": 0,
            "total_sources_ready": 0,
            "total_sources_error": 0,
            "total_sources_pending": 0,
            "total_sources_missing": 0,
            "total_sources_extra": 0,
            "total_naming_violations": 0,
            "total_duplicates": 0,
        }

        for target_title, meta in TARGET_NOTEBOOKS.items():
            expected_records = canonical_corpus[target_title]
            expected_titles = [r["id_imagen"] for r in expected_records]
            expected_set = set(expected_titles)

            nb_res: Dict[str, Any] = {
                "notebook_id": None,
                "exists": False,
                "localidad": meta["localidad"],
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

            matched_nbs = notebooks_by_title.get(target_title, [])
            if not matched_nbs:
                self.discrepancies.append(
                    f"[TARGET NOTEBOOK MISSING] Notebook '{target_title}' does not exist in NotebookLM."
                )
                summary_stats["target_notebooks_missing"].append(target_title)
                summary_stats["total_sources_missing"] += meta["expected_count"]
                nb_res["missing_sources"] = list(expected_titles)
                target_results[target_title] = nb_res
                continue

            # Found notebook
            target_nb = matched_nbs[0]
            nb_res["exists"] = True
            nb_res["notebook_id"] = target_nb.id
            summary_stats["target_notebooks_found"] += 1

            # Safety check: target ID cannot match protected ID
            if target_nb.id == PROTECTED_NOTEBOOK_ID:
                self.discrepancies.append(
                    f"[SAFETY VIOLATION] Target notebook '{target_title}' maps to protected ID {PROTECTED_NOTEBOOK_ID}!"
                )

            # Check duplicate notebooks with same title
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

            # Missing sources (expected in catalog but absent in notebook)
            missing = [t for t in expected_titles if t not in actual_set]
            nb_res["missing_sources"] = missing
            summary_stats["total_sources_missing"] += len(missing)
            if missing:
                self.discrepancies.append(
                    f"[{target_title}] Missing {len(missing)} expected sources: {missing[:5]}"
                    + (f" ... (+{len(missing)-5} more)" if len(missing) > 5 else "")
                )

            # Extra sources (in notebook but not in catalog)
            extra = [t for t in actual_titles if t not in expected_set]
            nb_res["extra_sources"] = extra
            summary_stats["total_sources_extra"] += len(extra)
            if extra:
                self.discrepancies.append(
                    f"[{target_title}] Found {len(extra)} unexpected extra sources: {extra[:5]}"
                    + (f" ... (+{len(extra)-5} more)" if len(extra) > 5 else "")
                )

            # Check duplicate source titles
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

            # Detailed source inspection: naming format & readiness status
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
                nb_res["sources"].append(source_entry)

                if ready:
                    nb_res["ready_count"] += 1
                    summary_stats["total_sources_ready"] += 1
                elif err:
                    nb_res["error_count"] += 1
                    summary_stats["total_sources_error"] += 1
                    nb_res["status_errors"].append(source_entry)
                    self.discrepancies.append(
                        f"[{target_title}] Source '{title}' ({s.id}) is in ERROR state ({st_str})"
                    )
                else:
                    nb_res["pending_count"] += 1
                    summary_stats["total_sources_pending"] += 1
                    nb_res["status_errors"].append(source_entry)
                    self.discrepancies.append(
                        f"[{target_title}] Source '{title}' ({s.id}) is not READY (status={st_str})"
                    )

                # Naming standard check [L-28]
                if not CANONICAL_FILENAME_REGEX.match(title):
                    nb_res["naming_errors"].append(source_entry)
                    summary_stats["total_naming_violations"] += 1
                    self.discrepancies.append(
                        f"[{target_title}] Source title '{title}' violates [L-28] canonical format"
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
        Executes complete verification flow and builds verification report dict.
        """
        start_time = datetime.now(timezone.utc)
        self.discrepancies = []

        # Step 1: Load Canonical Corpus
        try:
            canonical_corpus = load_and_verify_canonical_corpus(self.corpus_path)
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

        # Step 2: Establish NotebookLM Connection
        client = self.client
        own_client = False
        if client is None:
            if not NOTEBOOKLM_AVAILABLE:
                err_msg = "notebooklm-py library is not installed in the current environment."
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

        try:
            if own_client:
                async with client as active_client:
                    protected_res = await self.verify_protected_notebook(active_client)
                    target_results, summary_stats = await self.verify_target_notebooks(
                        active_client, canonical_corpus
                    )
            else:
                protected_res = await self.verify_protected_notebook(client)
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
                "discrepancies": self.discrepancies,
            }
            self._write_report(report)
            return False, report

        # Step 3: Compute Overall Pass / Fail Verdict
        all_targets_valid = all(t.get("valid", False) for t in target_results.values())
        protected_valid = protected_res.get("valid", False)
        all_checks_passed = (
            protected_valid
            and all_targets_valid
            and summary_stats["target_notebooks_found"] == len(TARGET_NOTEBOOKS)
            and summary_stats["total_sources_actual"] == TOTAL_EXPECTED_TARGET_SOURCES
            and summary_stats["total_sources_ready"] == TOTAL_EXPECTED_TARGET_SOURCES
            and summary_stats["total_sources_error"] == 0
            and summary_stats["total_sources_missing"] == 0
            and summary_stats["total_sources_extra"] == 0
            and summary_stats["total_naming_violations"] == 0
            and summary_stats["total_duplicates"] == 0
        )

        overall_status = "PASS" if all_checks_passed else "FAIL"
        exit_code = 0 if all_checks_passed else 1

        summary_stats["protected_notebook_valid"] = protected_valid
        summary_stats["overall_status"] = overall_status

        report = {
            "timestamp": start_time.isoformat(),
            "overall_status": overall_status,
            "exit_code": exit_code,
            "summary": summary_stats,
            "protected_notebook": protected_res,
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
def print_verification_summary(report: Dict[str, Any]) -> None:
    """Formats and prints an ASCII summary table to stdout."""
    status = report.get("overall_status", "FAIL")
    timestamp = report.get("timestamp", "")
    summary = report.get("summary", {})
    protected = report.get("protected_notebook", {})
    targets = report.get("target_notebooks", {})
    discrepancies = report.get("discrepancies", [])

    print("\n" + "=" * 80)
    print(" NOTEBOOKLM INDEPENDENT VERIFICATION REPORT")
    print(f" Timestamp: {timestamp} UTC")
    print(f" Overall Status: [{status}]")
    print("=" * 80)

    # 1. Protected Active Notebook
    print(" 1. ACTIVE NOTEBOOK PROTECTION AUDIT")
    p_id = protected.get("notebook_id", PROTECTED_NOTEBOOK_ID)
    p_title = protected.get("actual_title") or protected.get("expected_title")
    p_alive = "ALIVE" if protected.get("is_alive") else "UNREACHABLE"
    p_act = protected.get("actual_sources", 0)
    p_exp = protected.get("expected_sources", PROTECTED_EXPECTED_SOURCES_COUNT)
    p_valid = "[PASS] SHIELD INTACT" if protected.get("valid") else "[FAIL] PROTECTION COMPROMISED"

    print(f"    Notebook ID:     {p_id}")
    print(f"    Title:           {p_title}")
    print(f"    Liveness:        {p_alive}")
    print(f"    Sources Count:   {p_act} / {p_exp} expected")
    print(f"    Audit Verdict:   {p_valid}")
    if protected.get("error"):
        print(f"    Error:           {protected.get('error')}")

    print("-" * 80)

    # 2. Target Notebooks & Sources Table
    print(" 2. TARGET NOTEBOOKS & SOURCES AUDIT")
    print(
        f" {'Notebook Name':<24} | {'Notebook ID':<36} | {'Exp':>4} | {'Act':>4} | {'Rdy':>4} | {'Err':>3} | {'Status':<6}"
    )
    print("-" * 80)

    for name, meta in TARGET_NOTEBOOKS.items():
        t_data = targets.get(name, {})
        nid = t_data.get("notebook_id") or "NOT FOUND"
        exp = t_data.get("expected_count", meta["expected_count"])
        act = t_data.get("actual_count", 0)
        rdy = t_data.get("ready_count", 0)
        err = t_data.get("error_count", 0) + t_data.get("pending_count", 0)
        nb_status = "PASS" if t_data.get("valid") else "FAIL"

        # Truncate nid for neat display if needed
        disp_nid = nid if len(nid) <= 36 else nid[:33] + "..."
        print(f" {name:<24} | {disp_nid:<36} | {exp:>4} | {act:>4} | {rdy:>4} | {err:>3} | {nb_status:<6}")

    print("-" * 80)

    tot_exp = summary.get("total_sources_expected", TOTAL_EXPECTED_TARGET_SOURCES)
    tot_act = summary.get("total_sources_actual", 0)
    tot_rdy = summary.get("total_sources_ready", 0)
    tot_err = summary.get("total_sources_error", 0) + summary.get("total_sources_pending", 0)
    tot_status = "PASS" if status == "PASS" else "FAIL"

    print(
        f" {'TOTALS':<24} | {'4 Mono-locality Notebooks':<36} | {tot_exp:>4} | {tot_act:>4} | {tot_rdy:>4} | {tot_err:>3} | {tot_status:<6}"
    )
    print("=" * 80)

    # 3. Discrepancies (if any)
    if discrepancies:
        print(f" DISCREPANCIES DETECTED ({len(discrepancies)}):")
        for idx, d in enumerate(discrepancies[:20], start=1):
            print(f"   {idx:>2}. {d}")
        if len(discrepancies) > 20:
            print(f"   ... and {len(discrepancies) - 20} more discrepancies.")
        print("-" * 80)

    # 4. Final Verdict
    if status == "PASS":
        print(" VERDICT: [PASS] ALL 4 NOTEBOOKS & 200 SOURCES VERIFIED READY IN NOTEBOOKLM.")
    else:
        print(" VERDICT: [FAIL] VERIFICATION DETECTED ISSUES / MISSING ASSETS.")

    print(f" Detailed report saved to: {DEFAULT_REPORT_PATH.resolve()}")
    print("=" * 80 + "\n")


# -----------------------------------------------------------------------------
# Mock Client & Self-Test Harness for Robustness & Adversarial Testing
# -----------------------------------------------------------------------------
class MockNotebook:
    def __init__(self, id: str, title: str, sources_count: int = 0):
        self.id = id
        self.title = title
        self.sources_count = sources_count


class MockSource:
    def __init__(self, id: str, title: str, status_name: str = "READY", is_ready: bool = True, is_error: bool = False):
        self.id = id
        self.title = title
        self.is_ready = is_ready
        self.is_error = is_error

        # Emulate SourceStatus enum attribute
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
    """Builds a mock client containing all valid notebooks and sources."""
    mock_nbs = [
        MockNotebook(id=PROTECTED_NOTEBOOK_ID, title=PROTECTED_NOTEBOOK_TITLE, sources_count=188),
    ]
    mock_sources: Dict[str, List[MockSource]] = {
        PROTECTED_NOTEBOOK_ID: [
            MockSource(id=f"prot-src-{i}", title=f"004306112_{1870+i:05d}.jpg")
            for i in range(188)
        ]
    }

    nb_id_map = {
        "NRDL-ENSENADA-LEGOS-01": "mock-nb-nrdl-01",
        "JMOL-ENSENADA-LEGOS-01": "mock-nb-jmol-01",
        "VLLR-ENSENADA-LEGOS-01": "mock-nb-vllr-01",
        "NDRN-ENSENADA-LEGOS-01": "mock-nb-ndrn-01",
    }

    for name, nid in nb_id_map.items():
        records = canonical_corpus[name]
        mock_nbs.append(MockNotebook(id=nid, title=name, sources_count=len(records)))
        mock_sources[nid] = [
            MockSource(id=f"src-{nid}-{idx}", title=r["id_imagen"], status_name="READY", is_ready=True)
            for idx, r in enumerate(records, start=1)
        ]

    return MockNotebookLMClient(mock_nbs, mock_sources)


async def run_self_tests() -> bool:
    """
    Executes adversarial and standard self-tests against mocked environments
    to guarantee test verifier logic correctness.
    """
    print("\n[SELF-TEST] Running verifier test suite against canonical corpus and mock clients...")
    corpus = load_and_verify_canonical_corpus(DEFAULT_CATALOG_PATH)
    test_report_path = BASE_DIR / "scripts" / "test_self_check_report.json"

    # Test 1: Perfect Passing Scenario
    print(" - Test Case 1: All 200 sources and protected notebook valid...")
    passing_client = build_mock_passing_client(corpus)
    verifier = NotebookLMVerifier(client=passing_client, corpus_path=DEFAULT_CATALOG_PATH, report_path=test_report_path)
    ok, rep = await verifier.execute_verification()
    assert ok is True, f"Test 1 failed: expected PASS, got {rep.get('overall_status')}"
    assert rep["summary"]["total_sources_ready"] == 200
    assert rep["summary"]["protected_notebook_valid"] is True
    print("   [OK] Test Case 1 passed.")

    # Test 2: Protected notebook tampered (source count 187 instead of 188)
    print(" - Test Case 2: Protected notebook has source count mismatch (187 vs 188)...")
    tampered_client = build_mock_passing_client(corpus)
    # Remove one source from protected
    tampered_client.sources._sources_map[PROTECTED_NOTEBOOK_ID].pop()
    verifier2 = NotebookLMVerifier(client=tampered_client, corpus_path=DEFAULT_CATALOG_PATH, report_path=test_report_path)
    ok2, rep2 = await verifier2.execute_verification()
    assert ok2 is False, "Test 2 failed: expected failure on protected notebook mismatch"
    assert rep2["protected_notebook"]["valid"] is False
    print("   [OK] Test Case 2 properly detected protection violation.")

    # Test 3: Truncated source title (e.g. 00881.jpg instead of 004469033_00881.jpg) [L-28]
    print(" - Test Case 3: Naming violation with zero truncation [L-28]...")
    bad_name_client = build_mock_passing_client(corpus)
    nrdl_sources = bad_name_client.sources._sources_map["mock-nb-nrdl-01"]
    nrdl_sources[0] = MockSource(id="bad-1", title="00881.jpg", status_name="READY")
    verifier3 = NotebookLMVerifier(client=bad_name_client, corpus_path=DEFAULT_CATALOG_PATH, report_path=test_report_path)
    ok3, rep3 = await verifier3.execute_verification()
    assert ok3 is False, "Test 3 failed: expected failure on naming violation"
    assert rep3["summary"]["total_naming_violations"] > 0
    print("   [OK] Test Case 3 properly caught [L-28] truncation violation.")

    # Test 4: Source in ERROR status
    print(" - Test Case 4: Source in ERROR status...")
    err_client = build_mock_passing_client(corpus)
    jmol_sources = err_client.sources._sources_map["mock-nb-jmol-01"]
    jmol_sources[0] = MockSource(id="err-1", title=jmol_sources[0].title, status_name="ERROR", is_ready=False, is_error=True)
    verifier4 = NotebookLMVerifier(client=err_client, corpus_path=DEFAULT_CATALOG_PATH, report_path=test_report_path)
    ok4, rep4 = await verifier4.execute_verification()
    assert ok4 is False, "Test 4 failed: expected failure on source ERROR status"
    assert rep4["summary"]["total_sources_error"] == 1
    print("   [OK] Test Case 4 properly flagged non-ready / error source.")

    # Test 5: Missing target notebook
    print(" - Test Case 5: Missing target notebook...")
    missing_client = build_mock_passing_client(corpus)
    # Remove NDRN notebook
    missing_client.notebooks._notebooks = [
        nb for nb in missing_client.notebooks._notebooks if nb.title != "NDRN-ENSENADA-LEGOS-01"
    ]
    verifier5 = NotebookLMVerifier(client=missing_client, corpus_path=DEFAULT_CATALOG_PATH, report_path=test_report_path)
    ok5, rep5 = await verifier5.execute_verification()
    assert ok5 is False, "Test 5 failed: expected failure on missing notebook"
    assert "NDRN-ENSENADA-LEGOS-01" in rep5["summary"]["target_notebooks_missing"]
    print("   [OK] Test Case 5 properly reported missing notebook.")

    # Clean up test artifact if exists
    if test_report_path.is_file():
        test_report_path.unlink()

    print("[SELF-TEST] All 5 self-test scenarios PASSED successfully!\n")
    return True


# -----------------------------------------------------------------------------
# Main Entry Point
# -----------------------------------------------------------------------------
def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify NotebookLM sources and notebooks for Ensenada Personal de Legos."
    )
    parser.add_argument(
        "--corpus-path",
        type=Path,
        default=DEFAULT_CATALOG_PATH,
        help="Path to canonical catalogo_corpus.json (default: catalogo_corpus.json)",
    )
    parser.add_argument(
        "--report-path",
        type=Path,
        default=DEFAULT_REPORT_PATH,
        help="Path to output verification_report.json (default: scripts/verification_report.json)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run internal mock self-test suite and adversarial scenarios",
    )
    return parser.parse_args()


async def main_async() -> int:
    args = parse_arguments()

    if args.self_test:
        success = await run_self_tests()
        return 0 if success else 1

    verifier = NotebookLMVerifier(
        client=None,
        corpus_path=args.corpus_path,
        report_path=args.report_path,
    )

    passed, report = await verifier.execute_verification()
    print_verification_summary(report)

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
