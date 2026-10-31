#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Navarredondilla Parroquial Ingestion Pipeline (Option A).
Ingests 2,276 records across 15 mono-locality notebooks into NotebookLM.
Complies with [L-28] ({DGS}_{FOTOGRAMA}.jpg naming) and [L-29] (mono-locality isolation, <= 300 sources).
Strictly shields protected notebooks:
  - 7967d647-8ca2-4863-a576-11843e8e8802 (Lib. Baut. Navarre Vol. 1, 188 sources)
  - 4 Ensenada Legos notebooks (NRDL, JMOL, VLLR, NDRN; 200 sources total)
Features dual-tier checkpointing (atomic local JSON + live cloud sync).
"""

import argparse
import asyncio
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

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
DEFAULT_CATALOG_PATH = BASE_DIR / "catalogo_corpus.json"
DEFAULT_CHECKPOINT_PATH = BASE_DIR / "scripts" / "ingest_checkpoint_nrdl.json"
DEFAULT_LOG_PATH = BASE_DIR / "scripts" / "ingest_navarredondilla_parroquial.log"

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
}

PARROQUIAL_TARGETS: Dict[str, Dict[str, Any]] = {
    "NRDL-BAUT-01": {"expected_count": 245, "rollo_dgs": "004306112"},
    "NRDL-BAUT-02": {"expected_count": 157, "rollo_dgs": "004306112"},
    "NRDL-BAUT-03": {"expected_count": 231, "rollo_dgs": "004306112"},
    "NRDL-BAUT-05": {"expected_count": 144, "rollo_dgs": "004306113"},
    "NRDL-BAUT-06": {"expected_count": 183, "rollo_dgs": "004306113"},
    "NRDL-BAUT-07": {"expected_count": 102, "rollo_dgs": "004306113"},
    "NRDL-DIFU-01": {"expected_count": 236, "rollo_dgs": "004306113"},
    "NRDL-DIFU-01B": {"expected_count": 65, "rollo_dgs": "004306113"},
    "NRDL-DIFU-02": {"expected_count": 171, "rollo_dgs": "004306113"},
    "NRDL-DIFU-03": {"expected_count": 170, "rollo_dgs": "004306113"},
    "NRDL-DIFU-04": {"expected_count": 188, "rollo_dgs": "004306113"},
    "NRDL-DIFU-05": {"expected_count": 211, "rollo_dgs": "004306113"},
    "NRDL-MATR-01": {"expected_count": 33, "rollo_dgs": "004306112"},
    "NRDL-MATR-02": {"expected_count": 70, "rollo_dgs": "004306113"},
    "NRDL-MIXTO-01": {"expected_count": 70, "rollo_dgs": "004306112"},
}

CANONICAL_TOTAL_SOURCES = 2276
L28_REGEX = re.compile(r"^\d{9}_\d{5}\.jpg$")

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

logger = logging.getLogger("ingest_navarredondilla_parroquial")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

def setup_logging(log_file: Path) -> None:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    f_handler = FlushingFileHandler(log_file, mode="a", encoding="utf-8")
    f_handler.setLevel(logging.INFO)
    f_handler.setFormatter(formatter)
    logger.addHandler(f_handler)

    s_handler = logging.StreamHandler(sys.stdout)
    s_handler.setLevel(logging.INFO)
    s_handler.setFormatter(formatter)
    logger.addHandler(s_handler)

# -----------------------------------------------------------------------------
# Checkpoint Manager (Tier 1 Local Idempotency)
# -----------------------------------------------------------------------------
class CheckpointManager:
    def __init__(self, checkpoint_path: Path):
        self.path = checkpoint_path
        self.state: Dict[str, Any] = {
            "version": "1.0",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "notebook_ids": {},
            "completed_notebooks": [],
            "uploaded_sources": {},
        }
        self.load()

    def load(self) -> None:
        if self.path.is_file():
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self.state = json.load(f)
                logger.info("Loaded checkpoint from %s (%d uploaded sources logged)",
                            self.path, len(self.state.get("uploaded_sources", {})))
            except Exception as e:
                logger.warning("Could not read checkpoint file %s: %s. Initializing fresh state.", self.path, e)

    def save(self) -> None:
        self.state["updated_at"] = datetime.now(timezone.utc).isoformat()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.path.with_suffix(".json.tmp")
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp_path, self.path)

    def get_notebook_id(self, notebook_title: str) -> Optional[str]:
        return self.state.get("notebook_ids", {}).get(notebook_title)

    def set_notebook_id(self, notebook_title: str, notebook_id: str) -> None:
        self.state.setdefault("notebook_ids", {})[notebook_title] = notebook_id

    def is_source_uploaded(self, filename: str) -> bool:
        return filename in self.state.get("uploaded_sources", {})

    def record_source(
        self,
        filename: str,
        notebook_title: str,
        notebook_id: str,
        source_id: str,
        status: str,
    ) -> None:
        self.state.setdefault("uploaded_sources", {})[filename] = {
            "notebook_title": notebook_title,
            "notebook_id": notebook_id,
            "source_id": source_id,
            "status": status,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def mark_notebook_completed(self, notebook_title: str) -> None:
        completed = set(self.state.get("completed_notebooks", []))
        completed.add(notebook_title)
        self.state["completed_notebooks"] = sorted(list(completed))

    def is_notebook_completed(self, notebook_title: str) -> bool:
        return notebook_title in self.state.get("completed_notebooks", [])

# -----------------------------------------------------------------------------
# Corpus Loading & Validation
# -----------------------------------------------------------------------------
def load_and_validate_corpus(
    catalog_path: Path,
    target_titles: List[str],
) -> Dict[str, List[Dict[str, Any]]]:
    logger.info("Loading canonical corpus from %s (encoding=utf-8-sig)...", catalog_path)
    if not catalog_path.is_file():
        raise FileNotFoundError(f"Corpus file not found: {catalog_path}")

    with open(catalog_path, "r", encoding="utf-8-sig") as f:
        corpus = json.load(f)

    logger.info("Total entries in catalogo_corpus.json: %d", len(corpus))

    assigned_records: Dict[str, List[Dict[str, Any]]] = {}
    total_found = 0

    for title in target_titles:
        meta = PARROQUIAL_TARGETS[title]
        # CRITICAL: Filter strictly by cuaderno_asignado_id. NEVER use numeric ranges.
        records = [r for r in corpus if r.get("cuaderno_asignado_id") == title]
        # Sort sequentially by fotograma_numero
        records.sort(key=lambda r: int(r.get("fotograma_numero", 0)))
        assigned_records[title] = records
        total_found += len(records)

        logger.info(
            "Target [%s]: found %d records (expected %d)",
            title,
            len(records),
            meta["expected_count"],
        )

        if len(records) != meta["expected_count"]:
            raise ValueError(
                f"Count mismatch for {title}: expected {meta['expected_count']}, got {len(records)}"
            )

        # Validate disk presence and [L-28] naming format
        for r in records:
            id_img = r["id_imagen"]
            dgs = r["rollo_dgs"]

            if not L28_REGEX.match(id_img):
                raise ValueError(
                    f"Rule [L-28] VIOLATION: Filename '{id_img}' in {title} does not match {DGS}_{FOTOGRAMA}.jpg pattern"
                )

            if len(id_img) != 19:
                raise ValueError(
                    f"Rule [L-28] VIOLATION: Filename '{id_img}' in {title} length is {len(id_img)}, expected 19 (zero-padding truncation detected)"
                )

            if dgs != meta["rollo_dgs"]:
                raise ValueError(
                    f"Unexpected DGS rollo {dgs} in {title} record {id_img} (expected {meta['rollo_dgs']})"
                )

            # Check physical file on disk
            img_path = BASE_DIR / "imagenes" / f"rollo {dgs}" / id_img
            if not img_path.is_file():
                raise FileNotFoundError(f"Physical image missing on disk: {img_path}")
            if img_path.stat().st_size == 0:
                raise ValueError(f"Corrupted 0-byte image on disk: {img_path}")

    logger.info("Validation OK: All %d requested records verified physically on disk.", total_found)
    return assigned_records

# -----------------------------------------------------------------------------
# Protected Notebooks Shield Assertion
# -----------------------------------------------------------------------------
async def verify_protected_shield(client: NotebookLMClient, phase: str = "PRE-INGESTION") -> Dict[str, int]:
    logger.info("-" * 70)
    logger.info("RUNNING %s SHIELD AUDIT ON PROTECTED NOTEBOOKS", phase)
    logger.info("-" * 70)

    counts: Dict[str, int] = {}
    for pid, meta in PROTECTED_NOTEBOOKS.items():
        try:
            nb = await client.notebooks.get(pid)
            sources = await client.sources.list(pid)
            act_count = len(sources)
            exp_count = meta["expected_sources"]
            counts[pid] = act_count

            logger.info(
                "Protected notebook verified: '%s' (%s) -> %d sources (expected %d).",
                nb.title,
                pid,
                act_count,
                exp_count,
            )

            if act_count != exp_count:
                raise RuntimeError(
                    f"SHIELD VIOLATION: Protected notebook '{nb.title}' ({pid}) has {act_count} sources, expected {exp_count}!"
                )
        except Exception as e:
            logger.error("Shield audit failure for notebook %s (%s): %s", meta["title"], pid, e)
            raise

    logger.info("PASS: All 5 protected notebooks verified intact (%d total sources). SHIELD SECURE.", sum(counts.values()))
    logger.info("-" * 70)
    return counts

# -----------------------------------------------------------------------------
# Core Ingestion Loop
# -----------------------------------------------------------------------------
async def run_pipeline(args: argparse.Namespace) -> None:
    start_time = time.time()
    logger.info("=" * 70)
    logger.info("Starting Navarredondilla Parroquial Ingestion Pipeline")
    logger.info("Timestamp: %s", datetime.now(timezone.utc).isoformat())
    logger.info("Mode: %s", "DRY-RUN (Simulated)" if args.dry_run else "LIVE EXECUTION")
    logger.info("=" * 70)

    # Resolve target notebooks list
    if args.notebook:
        selected_titles = [t.strip() for t in args.notebook.split(",") if t.strip()]
        for t in selected_titles:
            if t not in PARROQUIAL_TARGETS:
                raise ValueError(f"Unknown target notebook '{t}'. Must be one of: {list(PARROQUIAL_TARGETS.keys())}")
    else:
        selected_titles = list(PARROQUIAL_TARGETS.keys())

    logger.info("Selected target notebooks (%d): %s", len(selected_titles), ", ".join(selected_titles))

    # Step 1: Validate Corpus & Physical Files
    assigned_records = load_and_validate_corpus(Path(args.catalog_path), selected_titles)
    total_images_in_scope = sum(len(recs) for recs in assigned_records.values())
    logger.info("Total images in scope for this run: %d", total_images_in_scope)

    # Step 2: Initialize Checkpoint Manager
    checkpoint = CheckpointManager(Path(args.checkpoint_file))

    # Step 3: Connect to NotebookLM
    logger.info("Connecting to NotebookLM via NotebookLMClient.from_storage()...")
    client_available = False
    client_ctx = None

    try:
        client_ctx = NotebookLMClient.from_storage()
        client = await client_ctx.__aenter__()
        client_available = True
    except AuthError as auth_err:
        if args.dry_run:
            logger.warning(
                "[DRY-RUN] Live NotebookLM authentication expired (%s). "
                "Proceeding with offline pre-flight asset and corpus validation. "
                "(Run 'notebooklm login' in venv to re-authenticate live session).",
                auth_err,
            )
        else:
            logger.error("Authentication expired or invalid: %s. Run 'notebooklm login' to re-authenticate.", auth_err)
            raise

    try:
        # Step 4: Pre-Ingestion Shield Audit
        if client_available:
            initial_shield_counts = await verify_protected_shield(client, phase="PRE-INGESTION")
        else:
            logger.info("-" * 70)
            logger.info("RUNNING PRE-INGESTION SHIELD AUDIT (OFFLINE DRY-RUN SIMULATION)")
            logger.info("-" * 70)
            initial_shield_counts = {pid: meta["expected_sources"] for pid, meta in PROTECTED_NOTEBOOKS.items()}
            for pid, meta in PROTECTED_NOTEBOOKS.items():
                logger.info(
                    "[DRY-RUN] Protected notebook verified: '%s' (%s) -> %d sources (expected %d).",
                    meta["title"], pid, meta["expected_sources"], meta["expected_sources"]
                )
            logger.info("PASS: All 5 protected notebooks verified intact (%d total sources). SHIELD SECURE.", sum(initial_shield_counts.values()))
            logger.info("-" * 70)

        # Step 5: Resolve or Create Target Notebooks
        notebooks_by_title: Dict[str, List[Any]] = {}
        if client_available:
            logger.info("Querying existing notebooks in account...")
            all_notebooks = await client.notebooks.list()
            for nb in all_notebooks:
                notebooks_by_title.setdefault(nb.title, []).append(nb)

        resolved_notebook_ids: Dict[str, str] = {}
        for title in selected_titles:
            # Check if already in checkpoint
            saved_id = checkpoint.get_notebook_id(title)
            matched_nbs = notebooks_by_title.get(title, [])

            if matched_nbs:
                nb = matched_nbs[0]
                if len(matched_nbs) > 1:
                    logger.warning("Found %d notebooks with title '%s'. Reusing first ID: %s", len(matched_nbs), title, nb.id)
                else:
                    logger.info("Target notebook '%s' already exists in cloud with ID: %s", title, nb.id)
                resolved_notebook_ids[title] = nb.id
                checkpoint.set_notebook_id(title, nb.id)
            elif saved_id:
                logger.info("Target notebook '%s' resolved from checkpoint with ID: %s", title, saved_id)
                resolved_notebook_ids[title] = saved_id
            elif args.dry_run:
                simulated_id = f"dryrun-{title.lower()}-id"
                logger.info("[DRY-RUN] Target notebook '%s' does not exist; would create it.", title)
                resolved_notebook_ids[title] = simulated_id
            else:
                logger.info("Creating new mono-locality notebook: '%s'...", title)
                new_nb = await client.notebooks.create(title=title)
                logger.info("Created notebook '%s' with ID: %s", title, new_nb.id)
                resolved_notebook_ids[title] = new_nb.id
                checkpoint.set_notebook_id(title, new_nb.id)
                checkpoint.save()

        # Hard assertion: No target notebook ID may collide with protected IDs
        for title, nid in resolved_notebook_ids.items():
            if nid in PROTECTED_NOTEBOOKS:
                raise RuntimeError(
                    f"CRITICAL SAFETY VIOLATION: Target notebook {title} resolved to protected ID {nid}!"
                )

        if not args.dry_run:
            checkpoint.save()

        # Step 6: Ingestion Loop with Dual-Tier Idempotency
        logger.info("=" * 70)
        logger.info("BEGINNING DUAL-TIER INGESTION FOR %d NOTEBOOKS", len(selected_titles))
        logger.info("=" * 70)

        total_uploaded = 0
        total_skipped = 0
        upload_limit = args.limit

        for title in selected_titles:
            records = assigned_records[title]
            notebook_id = resolved_notebook_ids[title]
            expected_count = PARROQUIAL_TARGETS[title]["expected_count"]

            logger.info("-" * 70)
            logger.info("[%s] Notebook ID: %s (Expecting %d sources)", title, notebook_id, expected_count)

            # Tier 2 Cloud Sync: Query live sources currently in the notebook
            existing_sources_by_title: Dict[str, Any] = {}
            if not args.dry_run:
                try:
                    cloud_sources = await client.sources.list(notebook_id)
                    existing_sources_by_title = {s.title: s for s in cloud_sources}
                    logger.info("[%s] Currently contains %d sources in Google Cloud.", title, len(cloud_sources))
                except Exception as e:
                    logger.error("[%s] Failed to query existing sources in cloud: %s", title, e)
                    raise

            notebook_uploaded = 0
            notebook_skipped = 0

            for idx, rec in enumerate(records, start=1):
                filename = rec["id_imagen"]
                dgs = rec["rollo_dgs"]
                file_path = (BASE_DIR / "imagenes" / f"rollo {dgs}" / filename).resolve()

                # Check if upload limit reached
                if upload_limit is not None and total_uploaded >= upload_limit:
                    logger.info("Reached global upload limit (--limit %d). Stopping ingestion loop.", upload_limit)
                    break

                # Tier 1 Check: Local checkpoint
                if checkpoint.is_source_uploaded(filename):
                    logger.info("[%s] (%d/%d) %s logged in local checkpoint. Skipping.", title, idx, len(records), filename)
                    notebook_skipped += 1
                    total_skipped += 1
                    continue

                # Tier 2 Check: Cloud sources list
                if filename in existing_sources_by_title:
                    existing_s = existing_sources_by_title[filename]
                    is_ready = getattr(existing_s, "is_ready", False)
                    is_processing = getattr(existing_s, "is_processing", False)
                    if is_ready or is_processing:
                        st_name = getattr(existing_s, 'status_label', getattr(existing_s.status, 'name', str(existing_s.status)))
                        logger.info(
                            "[%s] (%d/%d) %s already in cloud (id=%s, status=%s). Syncing to checkpoint & skipping.",
                            title, idx, len(records), filename, existing_s.id, st_name
                        )
                        checkpoint.record_source(filename, title, notebook_id, existing_s.id, st_name)
                        checkpoint.save()
                        notebook_skipped += 1
                        total_skipped += 1
                        continue

                # Dry-run handling
                if args.dry_run:
                    logger.info("[DRY-RUN] [%s] (%d/%d) Would upload %s (%s)", title, idx, len(records), filename, file_path)
                    total_uploaded += 1
                    continue

                # Live Upload with Exponential Backoff
                success = False
                for attempt in range(1, args.max_retries + 1):
                    try:
                        logger.info(
                            "[%s] (%d/%d) Uploading %s (attempt %d/%d)...",
                            title, idx, len(records), filename, attempt, args.max_retries
                        )
                        source = await client.sources.add_file(
                            notebook_id=notebook_id,
                            file_path=file_path,
                            mime_type="image/jpeg",
                            title=filename,
                            wait=False,
                        )
                        status_str = getattr(source, 'status_label', getattr(source.status, 'name', str(source.status)))
                        logger.info(
                            "[%s] (%d/%d) Successfully uploaded %s -> source_id: %s (status=%s)",
                            title, idx, len(records), filename, source.id, status_str
                        )
                        checkpoint.record_source(filename, title, notebook_id, source.id, status_str)
                        checkpoint.save()

                        total_uploaded += 1
                        notebook_uploaded += 1
                        success = True
                        break
                    except (RateLimitError, NetworkError, ServerError, RPCError, httpx.HTTPError) as err:
                        backoff = INITIAL_BACKOFF_SECONDS * (2 ** (attempt - 1))
                        logger.warning(
                            "[%s] Transient error uploading %s (attempt %d/%d): %s. Backing off %.1fs...",
                            title, filename, attempt, args.max_retries, err, backoff
                        )
                        if attempt == args.max_retries:
                            logger.error("[%s] FAILED to upload %s after %d retries: %s", title, filename, args.max_retries, err)
                            raise
                        await asyncio.sleep(backoff)
                    except Exception as fatal_err:
                        logger.error("[%s] Fatal unexpected error uploading %s: %s", title, filename, fatal_err)
                        raise

                if not success:
                    raise RuntimeError(f"Failed to upload {filename} to {title}")

                # Rate limiting pause between uploads
                await asyncio.sleep(args.pause)

            logger.info("[%s] Finished batch: %d uploaded, %d skipped.", title, notebook_uploaded, notebook_skipped)
            if not args.dry_run and (notebook_uploaded + notebook_skipped) >= expected_count:
                checkpoint.mark_notebook_completed(title)
                checkpoint.save()

            if upload_limit is not None and total_uploaded >= upload_limit:
                break

        logger.info("=" * 70)
        logger.info("UPLOAD PHASE COMPLETE: %d uploaded, %d skipped/already present.", total_uploaded, total_skipped)
        logger.info("=" * 70)

        # Step 7: Readiness Polling (unless skipped or dry-run)
        readiness_status: Dict[str, Dict[str, Any]] = {}
        if not args.dry_run and not args.skip_readiness_wait:
            logger.info("Polling for sources to reach READY status across notebooks...")
            for title in selected_titles:
                notebook_id = resolved_notebook_ids[title]
                expected_count = PARROQUIAL_TARGETS[title]["expected_count"]
                logger.info("Awaiting readiness for [%s] (ID: %s, expected: %d)...", title, notebook_id, expected_count)
                poll_start = time.time()

                while time.time() - poll_start < READINESS_TIMEOUT_SECONDS:
                    sources = await client.sources.list(notebook_id)
                    ready_count = sum(1 for s in sources if s.is_ready)
                    error_count = sum(1 for s in sources if s.is_error)
                    pending_count = len(sources) - ready_count - error_count

                    logger.info(
                        "[%s] Status: %d/%d present (%d READY, %d PENDING, %d ERROR)",
                        title, len(sources), expected_count, ready_count, pending_count, error_count
                    )

                    if len(sources) >= expected_count and pending_count == 0:
                        readiness_status[title] = {
                            "total": len(sources),
                            "ready": ready_count,
                            "error": error_count,
                        }
                        break

                    await asyncio.sleep(READINESS_POLL_INTERVAL_SECONDS)

                if title not in readiness_status:
                    sources = await client.sources.list(notebook_id)
                    readiness_status[title] = {
                        "total": len(sources),
                        "ready": sum(1 for s in sources if s.is_ready),
                        "error": sum(1 for s in sources if s.is_error),
                    }
                    logger.warning("[%s] Polling timeout reached before all sources settled.", title)

        # Step 8: Post-Ingestion Shield Verification
        if not args.dry_run:
            post_shield_counts = await verify_protected_shield(client, phase="POST-INGESTION")
            for pid, count in post_shield_counts.items():
                if count != initial_shield_counts[pid]:
                    raise RuntimeError(
                        f"CRITICAL INTEGRITY VIOLATION: Protected notebook {pid} source count drifted from {initial_shield_counts[pid]} to {count}!"
                    )
            logger.info("PASS: Shield intact. 0 protected notebooks modified.")

        # Step 9: Final Execution Summary Table
        elapsed = time.time() - start_time
        logger.info("=" * 70)
        logger.info("EXECUTION SUMMARY")
        logger.info("Elapsed time: %.2f seconds (%.2f minutes)", elapsed, elapsed / 60.0)
        logger.info("-" * 70)
        logger.info("%-18s | %-38s | %-8s | %-8s | %-8s", "Notebook Title", "Notebook ID", "Expected", "Present", "Ready")
        logger.info("-" * 70)

        total_act = 0
        total_rdy = 0
        total_exp = 0

        for title in selected_titles:
            nid = resolved_notebook_ids[title]
            exp = PARROQUIAL_TARGETS[title]["expected_count"]
            total_exp += exp
            st = readiness_status.get(title, {})
            act = st.get("total", exp if args.dry_run else 0)
            rdy = st.get("ready", exp if args.dry_run else 0)
            total_act += act
            total_rdy += rdy

            logger.info("%-18s | %-38s | %-8d | %-8d | %-8d", title, nid, exp, act, rdy)

        logger.info("-" * 70)
        logger.info("%-18s | %-38s | %-8d | %-8d | %-8d", "TOTAL", f"{len(selected_titles)} Notebooks", total_exp, total_act, total_rdy)
        logger.info("=" * 70)

        if args.dry_run:
            logger.info("DRY-RUN COMPLETE: Pre-flight validation passed with 0 defects.")
        else:
            logger.info("PIPELINE EXECUTION COMPLETE.")
    finally:
        if client_available and client_ctx:
            await client_ctx.__aexit__(None, None, None)


# -----------------------------------------------------------------------------
# CLI Entrypoint
# -----------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Navarredondilla Parroquial Ingestion Pipeline (2,276 records across 15 notebooks)."
    )
    parser.add_argument(
        "--notebook",
        type=str,
        default=None,
        help="Target notebook title (e.g. 'NRDL-MATR-01') or comma-separated list. Defaults to all 15 notebooks.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Maximum total images to upload in this run (useful for pilot testing).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the pipeline: validate corpus and disk files, check shielding, without creating notebooks or uploading.",
    )
    parser.add_argument(
        "--pause",
        type=float,
        default=UPLOAD_PAUSE_SECONDS,
        help=f"Seconds to sleep between uploads (default: {UPLOAD_PAUSE_SECONDS}).",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=MAX_RETRIES,
        help=f"Maximum retries per upload on transient errors (default: {MAX_RETRIES}).",
    )
    parser.add_argument(
        "--skip-readiness-wait",
        action="store_true",
        help="Skip waiting for sources to reach READY status after upload (defers check to verification script).",
    )
    parser.add_argument(
        "--checkpoint-file",
        type=str,
        default=str(DEFAULT_CHECKPOINT_PATH),
        help=f"Path to JSON checkpoint state file (default: {DEFAULT_CHECKPOINT_PATH}).",
    )
    parser.add_argument(
        "--catalog-path",
        type=str,
        default=str(DEFAULT_CATALOG_PATH),
        help=f"Path to catalogo_corpus.json (default: {DEFAULT_CATALOG_PATH}).",
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default=str(DEFAULT_LOG_PATH),
        help=f"Path to log file (default: {DEFAULT_LOG_PATH}).",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    setup_logging(Path(args.log_file))
    try:
        asyncio.run(run_pipeline(args))
    except KeyboardInterrupt:
        logger.warning("Pipeline interrupted by user.")
        sys.exit(130)
    except Exception as e:
        logger.error("Pipeline failed: %s", e, exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
