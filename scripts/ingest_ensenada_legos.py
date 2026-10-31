#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ingestion Pipeline for Ensenada Personal de Legos (200 records across 4 mono-locality notebooks).
Project: Genealo - Catastro de Ensenada
Compliant with [L-28] ({DGS}_{FOTOGRAMA}.jpg naming) and [L-29] (mono-locality isolation).
Shields protected notebook 7967d647-8ca2-4863-a576-11843e8e8802.
"""

import asyncio
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
from notebooklm import NotebookLMClient
from notebooklm.exceptions import (
    AuthError,
    NetworkError,
    NotebookLMError,
    RateLimitError,
    RPCError,
    ServerError,
)

# -----------------------------------------------------------------------------
# Configuration and Constants
# -----------------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
CATALOGO_PATH = BASE_DIR / "catalogo_corpus.json"
LOG_PATH = BASE_DIR / "scripts" / "ingest_ensenada_legos.log"

PROTECTED_NOTEBOOK_ID = "7967d647-8ca2-4863-a576-11843e8e8802"
PROTECTED_NOTEBOOK_TITLE = "Lib. Baut. Navarre Vol. 1 (1594-1695)"

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

UPLOAD_PAUSE_SECONDS = 1.5
MAX_RETRIES = 5
INITIAL_BACKOFF_SECONDS = 2.0
READINESS_TIMEOUT_SECONDS = 300
READINESS_POLL_INTERVAL_SECONDS = 5.0

# -----------------------------------------------------------------------------
# Logging Configuration
# -----------------------------------------------------------------------------
class FlushingFileHandler(logging.FileHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()

logger = logging.getLogger("ingest_ensenada_legos")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# File handler with auto-flush
LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
file_handler = FlushingFileHandler(LOG_PATH, mode="a", encoding="utf-8")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Stdout handler
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.INFO)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


# -----------------------------------------------------------------------------
# Corpus Loading & Validation
# -----------------------------------------------------------------------------
def load_and_validate_corpus():
    logger.info("Loading canonical corpus from %s (encoding=utf-8-sig)...", CATALOGO_PATH)
    if not CATALOGO_PATH.is_file():
        raise FileNotFoundError(f"Corpus file not found: {CATALOGO_PATH}")

    with open(CATALOGO_PATH, "r", encoding="utf-8-sig") as f:
        corpus = json.load(f)

    logger.info("Total entries in catalogo_corpus.json: %d", len(corpus))

    assigned_records = {}
    for target_name, meta in TARGET_NOTEBOOKS.items():
        records = [
            r for r in corpus if r.get("cuaderno_asignado_id") == target_name
        ]
        # Sort sequentially by fotograma_numero
        records.sort(key=lambda r: int(r.get("fotograma_numero", 0)))
        assigned_records[target_name] = records

        logger.info(
            "Target [%s] (%s): found %d records (expected %d)",
            target_name,
            meta["localidad"],
            len(records),
            meta["expected_count"],
        )

        if len(records) != meta["expected_count"]:
            raise ValueError(
                f"Count mismatch for {target_name}: expected {meta['expected_count']}, got {len(records)}"
            )

        # Validate range and files
        for r in records:
            id_img = r["id_imagen"]
            dgs = r["rollo_dgs"]
            if dgs != meta["rollo_dgs"]:
                raise ValueError(
                    f"Unexpected DGS rollo {dgs} in {target_name} record {id_img}"
                )

            # Validate fotograma range
            fotograma = int(r.get("fotograma_numero", 0))
            if not (meta["fotograma_start"] <= fotograma <= meta["fotograma_end"]):
                raise ValueError(
                    f"Fotograma {fotograma} outside range [{meta['fotograma_start']}, {meta['fotograma_end']}] for {target_name} record {id_img}"
                )

            # Check physical file on disk
            img_path = BASE_DIR / "imagenes" / f"rollo {dgs}" / id_img
            if not img_path.is_file():
                raise FileNotFoundError(
                    f"Physical image missing on disk: {img_path}"
                )

    total_images = sum(len(recs) for recs in assigned_records.values())
    logger.info("Validation OK: Exactly %d target images verified on disk.", total_images)
    if total_images != 200:
        raise ValueError(f"Total target images must be exactly 200, got {total_images}")

    return assigned_records


# -----------------------------------------------------------------------------
# Core Ingestion Engine
# -----------------------------------------------------------------------------
async def main():
    start_time = time.time()
    logger.info("=" * 70)
    logger.info("Starting Ensenada Personal de Legos Ingestion Pipeline")
    logger.info("Timestamp: %s", datetime.now(timezone.utc).isoformat())
    logger.info("=" * 70)

    # Step 1: Validate Corpus & Physical Files
    assigned_records = load_and_validate_corpus()

    # Step 2: Connect to NotebookLM
    logger.info("Connecting to NotebookLM via NotebookLMClient.from_storage()...")
    async with NotebookLMClient.from_storage() as client:
        # Step 3: Verify and Shield Active Notebook
        logger.info("Verifying protected active notebook %s...", PROTECTED_NOTEBOOK_ID)
        try:
            protected_nb = await client.notebooks.get(PROTECTED_NOTEBOOK_ID)
            protected_sources = await client.sources.list(PROTECTED_NOTEBOOK_ID)
            initial_protected_count = len(protected_sources)
            logger.info(
                "Protected notebook verified: '%s' (%s) with %d sources. (SHIELD ACTIVE)",
                protected_nb.title,
                protected_nb.id,
                initial_protected_count,
            )
        except Exception as e:
            logger.error("Failed to query protected notebook %s: %s", PROTECTED_NOTEBOOK_ID, e)
            raise

        # Step 4: Resolve or Create the 4 Target Notebooks
        logger.info("Querying existing notebooks in account...")
        all_notebooks = await client.notebooks.list()
        notebooks_by_title = {}
        for nb in all_notebooks:
            notebooks_by_title.setdefault(nb.title, []).append(nb)

        notebook_ids = {}
        for target_title in TARGET_NOTEBOOKS.keys():
            matched_nbs = notebooks_by_title.get(target_title, [])
            if matched_nbs:
                if len(matched_nbs) > 1:
                    logger.warning(
                        "Found %d existing notebooks with title '%s'. Selecting the first one (ID: %s).",
                        len(matched_nbs),
                        target_title,
                        matched_nbs[0].id,
                    )
                nb = matched_nbs[0]
                logger.info("Target notebook '%s' already exists with ID: %s", target_title, nb.id)
                notebook_ids[target_title] = nb.id
            else:
                logger.info("Creating new mono-locality notebook: '%s'...", target_title)
                new_nb = await client.notebooks.create(title=target_title)
                logger.info("Created notebook '%s' with ID: %s", target_title, new_nb.id)
                notebook_ids[target_title] = new_nb.id

        # Safety assertion: none of target IDs can match protected notebook
        for title, nid in notebook_ids.items():
            if nid == PROTECTED_NOTEBOOK_ID:
                raise RuntimeError(
                    f"CRITICAL SAFETY VIOLATION: Target notebook {title} mapped to protected ID {nid}!"
                )

        # Step 5: Ingest Images per Notebook
        logger.info("-" * 70)
        logger.info("Beginning batch upload for 200 documents across 4 notebooks")
        logger.info("-" * 70)

        total_uploaded = 0
        total_skipped = 0

        for target_title, records in assigned_records.items():
            notebook_id = notebook_ids[target_title]
            expected_count = TARGET_NOTEBOOKS[target_title]["expected_count"]
            logger.info(
                "[%s] Target notebook ID: %s (Expecting %d sources)",
                target_title,
                notebook_id,
                expected_count,
            )

            # Query existing sources in notebook to enable resumption/idempotency
            existing_sources = await client.sources.list(notebook_id)
            existing_sources_by_title = {s.title: s for s in existing_sources}
            logger.info(
                "[%s] Currently contains %d existing sources.",
                target_title,
                len(existing_sources),
            )

            for idx, rec in enumerate(records, start=1):
                filename = rec["id_imagen"]
                dgs = rec["rollo_dgs"]
                file_path = (BASE_DIR / "imagenes" / f"rollo {dgs}" / filename).resolve()

                # Check if already present and ready or processing
                if filename in existing_sources_by_title:
                    existing_s = existing_sources_by_title[filename]
                    is_ready = getattr(existing_s, "is_ready", False)
                    is_processing = getattr(existing_s, "is_processing", False)
                    if is_ready or is_processing:
                        logger.info(
                            "[%s] (%d/%d) %s already uploaded (id=%s, ready=%s, processing=%s). Skipping.",
                            target_title,
                            idx,
                            len(records),
                            filename,
                            existing_s.id,
                            is_ready,
                            is_processing,
                        )
                        total_skipped += 1
                        continue

                # Upload with retries & exponential backoff
                success = False
                for attempt in range(1, MAX_RETRIES + 1):
                    try:
                        logger.info(
                            "[%s] (%d/%d) Uploading %s (attempt %d/%d)...",
                            target_title,
                            idx,
                            len(records),
                            filename,
                            attempt,
                            MAX_RETRIES,
                        )
                        source = await client.sources.add_file(
                            notebook_id=notebook_id,
                            file_path=file_path,
                            mime_type="image/jpeg",
                            title=filename,
                            wait=False,
                        )
                        logger.info(
                            "[%s] (%d/%d) Successfully uploaded %s -> source_id: %s (status=%s)",
                            target_title,
                            idx,
                            len(records),
                            filename,
                            source.id,
                            getattr(source, 'status_label', getattr(source.status, 'name', str(source.status))),
                        )
                        total_uploaded += 1
                        success = True
                        break
                    except (RateLimitError, NetworkError, ServerError, RPCError, httpx.HTTPError) as err:
                        backoff = INITIAL_BACKOFF_SECONDS * (2 ** (attempt - 1))
                        logger.warning(
                            "[%s] Transient error uploading %s (attempt %d/%d): %s. Backoff %.1fs...",
                            target_title,
                            filename,
                            attempt,
                            MAX_RETRIES,
                            err,
                            backoff,
                        )
                        if attempt == MAX_RETRIES:
                            logger.error(
                                "[%s] FAILED to upload %s after %d attempts: %s",
                                target_title,
                                filename,
                                MAX_RETRIES,
                                err,
                            )
                            raise
                        await asyncio.sleep(backoff)
                    except Exception as fatal_err:
                        logger.error(
                            "[%s] Unexpected fatal error uploading %s: %s",
                            target_title,
                            filename,
                            fatal_err,
                        )
                        raise

                # Rate limiting sleep between successful uploads
                await asyncio.sleep(UPLOAD_PAUSE_SECONDS)

        logger.info("-" * 70)
        logger.info(
            "Upload phase complete. Uploaded: %d, Already present/skipped: %d",
            total_uploaded,
            total_skipped,
        )
        logger.info("-" * 70)

        # Step 6: Wait for Source Readiness across all 4 notebooks
        logger.info("Polling for all sources to reach READY status...")
        readiness_status = {}

        for target_title, expected_count in [
            (t, TARGET_NOTEBOOKS[t]["expected_count"]) for t in TARGET_NOTEBOOKS.keys()
        ]:
            notebook_id = notebook_ids[target_title]
            logger.info("Awaiting readiness for [%s] (ID: %s, expected: %d)...", target_title, notebook_id, expected_count)
            poll_start = time.time()

            while time.time() - poll_start < READINESS_TIMEOUT_SECONDS:
                sources = await client.sources.list(notebook_id)
                ready_count = sum(1 for s in sources if s.is_ready)
                error_count = sum(1 for s in sources if s.is_error)
                pending_count = len(sources) - ready_count - error_count

                logger.info(
                    "[%s] Status: %d/%d sources present (%d READY, %d PENDING, %d ERROR)",
                    target_title,
                    len(sources),
                    expected_count,
                    ready_count,
                    pending_count,
                    error_count,
                )

                if len(sources) >= expected_count and pending_count == 0:
                    readiness_status[target_title] = {
                        "total": len(sources),
                        "ready": ready_count,
                        "error": error_count,
                        "sources": sources,
                    }
                    break

                await asyncio.sleep(READINESS_POLL_INTERVAL_SECONDS)

            if target_title not in readiness_status:
                sources = await client.sources.list(notebook_id)
                readiness_status[target_title] = {
                    "total": len(sources),
                    "ready": sum(1 for s in sources if s.is_ready),
                    "error": sum(1 for s in sources if s.is_error),
                    "sources": sources,
                }
                logger.warning(
                    "[%s] Polling deadline reached before all sources settled.", target_title
                )

        # Step 7: Post-Ingestion Shield Audit of Protected Notebook
        logger.info("Running post-ingestion integrity check on protected notebook %s...", PROTECTED_NOTEBOOK_ID)
        post_protected_nb = await client.notebooks.get(PROTECTED_NOTEBOOK_ID)
        post_protected_sources = await client.sources.list(PROTECTED_NOTEBOOK_ID)
        post_protected_count = len(post_protected_sources)

        logger.info(
            "Protected notebook verification: '%s' (%s) initial sources=%d, post sources=%d",
            post_protected_nb.title,
            post_protected_nb.id,
            initial_protected_count,
            post_protected_count,
        )

        if post_protected_count != initial_protected_count:
            raise RuntimeError(
                f"INTEGRITY VIOLATION: Protected notebook source count changed from {initial_protected_count} to {post_protected_count}!"
            )
        logger.info("PASS: Protected active notebook remains 100% UNTOUCHED.")

        # Step 8: Final Summary Table
        elapsed = time.time() - start_time
        logger.info("=" * 70)
        logger.info("INGESTION PIPELINE EXECUTION SUMMARY")
        logger.info("Elapsed time: %.2f seconds (%.2f minutes)", elapsed, elapsed / 60.0)
        logger.info("-" * 70)
        logger.info(
            "%-25s | %-38s | %-8s | %-8s | %-8s",
            "Notebook Name",
            "Notebook ID",
            "Expected",
            "Actual",
            "Ready",
        )
        logger.info("-" * 70)

        all_ok = True
        total_actual = 0
        total_ready = 0

        for target_title, meta in TARGET_NOTEBOOKS.items():
            nid = notebook_ids[target_title]
            st = readiness_status.get(target_title, {})
            act = st.get("total", 0)
            rdy = st.get("ready", 0)
            exp = meta["expected_count"]
            total_actual += act
            total_ready += rdy

            status_str = f"{act}"
            if act != exp or rdy != exp:
                all_ok = False

            logger.info(
                "%-25s | %-38s | %-8d | %-8d | %-8d",
                target_title,
                nid,
                exp,
                act,
                rdy,
            )

        logger.info("-" * 70)
        logger.info(
            "%-25s | %-38s | %-8d | %-8d | %-8d",
            "TOTAL",
            "4 Notebooks",
            200,
            total_actual,
            total_ready,
        )
        logger.info("=" * 70)

        if not all_ok:
            logger.error("Ingestion finished with mismatches or incomplete sources.")
            sys.exit(1)
        else:
            logger.info("ALL 200 SOURCES SUCCESSFULLY INGESTED AND VERIFIED READY!")
            logger.info("Execution complete.")


if __name__ == "__main__":
    asyncio.run(main())
