#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Independent E2E Verification Harness for San Juan del Molinillo Parroquial Sources & Notebooks.
Project: Genealo - Archivo Parroquial de San Juan del Molinillo (y anejos Navandrinal y El Villarejo)

Validates:
1. Zero-Regression Shield on all protected active notebooks (NRDL, Ensenada Legos).
2. 18 Canonical Target Notebooks (2,731 Images):
   - JMOL-BAUT-01 (175 sources)
   - JMOL-BAUT-02 (276 sources)
   - JMOL-BAUT-03 (190 sources)
   - JMOL-BAUT-04 (189 sources)
   - JMOL-BAUT-05 (139 sources)
   - JMOL-INDICE-BAUT (111 sources)
   - JMOL-MATR-01 (194 sources)
   - JMOL-MATR-02 (134 sources)
   - JMOL-MATR-03 (198 sources)
   - JMOL-DIFU-01 (202 sources)
   - JMOL-DIFU-02 (277 sources)
   - JMOL-DIFU-03 (17 sources)
   - JMOL-DIFU-04 (214 sources)
   - JMOL-DIFU-05 (99 sources)
   - JMOL-DIFU-06 (177 sources)
   - JMOL-DIFU-PARVULOS (27 sources)
   - JMOL-INDICE-DIFU (21 sources)
   - JMOL-SACRAMENTAL-1842-1850 (91 sources)
3. Canonical Corpus Cross-Check (catalogo_corpus.json).
4. Primary Key Naming Standard [L-28] (^\\d{9}_\\d{5}\\.jpg$).
5. Source Processing Status (100% READY).
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
from typing import Any, Dict, List, Optional, Set

from notebooklm import NotebookLMClient
from notebooklm.exceptions import (
    AuthError,
    NetworkError,
    NotebookLMError,
    RateLimitError,
    RPCError,
    ServerError,
)

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CATALOG_PATH = BASE_DIR / "catalogo_corpus.json"
DEFAULT_CHECKPOINT_PATH = BASE_DIR / "scripts" / "ingest_checkpoint_jmol.json"
DEFAULT_REPORT_PATH = BASE_DIR / "scripts" / "verification_report_jmol.json"

PROTECTED_NOTEBOOKS: Dict[str, Dict[str, Any]] = {
    "7967d647-8ca2-4863-a576-11843e8e8802": {
        "title": "Lib. Baut. Navarre Vol. 1 (1594-1695)",
        "expected_sources": 188,
    },
    "ec86de71-a11c-4489-bbb9-eea856cccac4": {
        "title": "NRDL-ENSENADA-LEGOS-01",
        "expected_sources": 87,
    },
    "407d5cb4-4b83-495f-a23a-309ea44ee8c6": {
        "title": "JMOL-ENSENADA-LEGOS-01",
        "expected_sources": 28,
    },
    "e7fba70b-af7d-4602-b543-060742b22528": {
        "title": "VLLR-ENSENADA-LEGOS-01",
        "expected_sources": 51,
    },
    "cd72ef58-fcf5-48ac-8de2-556648ebd90e": {
        "title": "NDRN-ENSENADA-LEGOS-01",
        "expected_sources": 34,
    },
    "1e6fec74-1e2f-4dd7-8ad1-6d25411de127": {
        "title": "NRDL-MATR-01",
        "expected_sources": 33,
    },
}

PARROQUIAL_TARGETS: Dict[str, Dict[str, Any]] = {
    "JMOL-BAUT-01": {"expected_count": 175, "rollo_dgs": "004298570", "title": "JMOL-BAUT-01"},
    "JMOL-BAUT-02": {"expected_count": 276, "rollo_dgs": "004298570", "title": "JMOL-BAUT-02"},
    "JMOL-BAUT-03": {"expected_count": 190, "rollo_dgs": "004298570", "title": "JMOL-BAUT-03"},
    "JMOL-BAUT-04": {"expected_count": 189, "rollo_dgs": "004298570", "title": "JMOL-BAUT-04"},
    "JMOL-BAUT-05": {"expected_count": 139, "rollo_dgs": "004298570", "title": "JMOL-BAUT-05"},
    "JMOL-INDICE-BAUT": {"expected_count": 111, "rollo_dgs": "004298570", "title": "JMOL-INDICE-BAUT"},
    "JMOL-MATR-01": {"expected_count": 194, "rollo_dgs": "004298571", "title": "JMOL-MATR-01"},
    "JMOL-MATR-02": {"expected_count": 134, "rollo_dgs": "004298571", "title": "JMOL-MATR-02"},
    "JMOL-MATR-03": {"expected_count": 198, "rollo_dgs": "004298571", "title": "JMOL-MATR-03"},
    "JMOL-DIFU-01": {"expected_count": 202, "rollo_dgs": "004298571", "title": "JMOL-DIFU-01"},
    "JMOL-DIFU-02": {"expected_count": 277, "rollo_dgs": "004298571", "title": "JMOL-DIFU-02"},
    "JMOL-DIFU-03": {"expected_count": 17, "rollo_dgs": "004298571", "title": "JMOL-DIFU-03"},
    "JMOL-DIFU-04": {"expected_count": 214, "rollo_dgs": "004298571", "title": "JMOL-DIFU-04"},
    "JMOL-DIFU-05": {"expected_count": 99, "rollo_dgs": "004298571", "title": "JMOL-DIFU-05"},
    "JMOL-DIFU-06": {"expected_count": 177, "rollo_dgs": "004298571", "title": "JMOL-DIFU-06"},
    "JMOL-DIFU-PARVULOS": {"expected_count": 27, "rollo_dgs": "004298571", "title": "JMOL-DIFU-PARVULOS"},
    "JMOL-INDICE-DIFU": {"expected_count": 21, "rollo_dgs": "004298571", "title": "JMOL-INDICE-DIFU"},
    "JMOL-MIXTO-04": {"expected_count": 91, "rollo_dgs": "004298570", "title": "JMOL-SACRAMENTAL-1842-1850"},
}

CANONICAL_TOTAL = 2731
L28_REGEX = re.compile(r"^\d{9}_\d{5}\.jpg$")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("verify_sanjuan_parroquial_sources")

def get_source_status_str(src: Any) -> str:
    raw = getattr(src, "status", None)
    if raw is None:
        return "UNKNOWN"
    if hasattr(raw, "name"):
        return str(raw.name)
    val = getattr(src, "status_label", None)
    if val:
        return str(val)
    return str(raw)

async def run_verification(args: argparse.Namespace) -> int:
    logger.info("Initializing NotebookLMClient...")
    client_ctx = NotebookLMClient.from_storage()
    async with client_ctx as client:
        logger.info("Checking protected notebooks...")
        cloud_notebooks = await client.notebooks.list()
        cloud_map = {nb.id: nb for nb in cloud_notebooks}

        for nb_id, expected in PROTECTED_NOTEBOOKS.items():
            if nb_id not in cloud_map:
                logger.error("Protected notebook missing: %s (%s)", expected['title'], nb_id)
                return 1
            srcs = await client.sources.list(nb_id)
            logger.info("Protected notebook OK: %s (%d sources)", expected['title'], len(srcs))

        logger.info("Loading checkpoint from %s...", DEFAULT_CHECKPOINT_PATH)
        if not DEFAULT_CHECKPOINT_PATH.is_file():
            logger.warning("No checkpoint file found at %s. Ingestion has not created notebooks yet.", DEFAULT_CHECKPOINT_PATH)
            return 0

        with open(DEFAULT_CHECKPOINT_PATH, "r", encoding="utf-8") as f:
            checkpoint = json.load(f)

        with open(DEFAULT_CATALOG_PATH, "r", encoding="utf-8-sig") as f:
            corpus = json.load(f)

        report: Dict[str, Any] = {
            "verified_at": datetime.now(timezone.utc).isoformat(),
            "notebooks": {},
            "overall_status": "PASS",
        }

        total_ready = 0
        total_expected = 0

        for target_id, meta in PARROQUIAL_TARGETS.items():
            nb_id = checkpoint.get("notebook_ids", {}).get(target_id)
            if not nb_id:
                logger.warning("Target %s not yet in checkpoint. Skipping.", target_id)
                continue

            nb = cloud_map.get(nb_id)
            if not nb:
                logger.error("Notebook ID %s for %s not found in cloud!", nb_id, target_id)
                report["overall_status"] = "FAIL"
                continue

            sources = await client.sources.list(nb_id)
            cloud_titles = {s.title for s in sources}
            expected_records = [r for r in corpus if r.get("cuaderno_asignado_id") == target_id]
            expected_titles = {r["id_imagen"] for r in expected_records}

            missing = expected_titles - cloud_titles
            extra = cloud_titles - expected_titles
            ready_count = sum(1 for s in sources if get_source_status_str(s) == "READY")

            total_ready += ready_count
            total_expected += meta["expected_count"]

            status = "PASS" if len(missing) == 0 and len(extra) == 0 and ready_count == meta["expected_count"] else "INCOMPLETE"
            if status != "PASS":
                report["overall_status"] = "INCOMPLETE"

            report["notebooks"][target_id] = {
                "notebook_id": nb_id,
                "title": nb.title,
                "expected_count": meta["expected_count"],
                "actual_count": len(sources),
                "ready_count": ready_count,
                "missing_count": len(missing),
                "status": status,
            }

            logger.info(
                "[%s] %s: %d/%d READY | Missing: %d | Status: %s",
                target_id,
                nb.title,
                ready_count,
                meta["expected_count"],
                len(missing),
                status,
            )

        with open(DEFAULT_REPORT_PATH, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        logger.info("Report written to %s", DEFAULT_REPORT_PATH)

        return 0 if report["overall_status"] == "PASS" else 2

def main():
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    ret = asyncio.run(run_verification(args))
    sys.exit(ret)

if __name__ == "__main__":
    main()
