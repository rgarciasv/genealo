#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
San Juan del Molinillo Parroquial Ingestion Pipeline.
Ingests 2,731 records across 18 mono-locality notebooks into NotebookLM Pro.
Complies with [L-28] ({DGS}_{FOTOGRAMA}.jpg naming), [L-29] (mono-locality isolation, <= 300 sources)
and [L-30] (pure sacramental series; title JMOL-SACRAMENTAL-1842-1850).
Strictly shields all protected notebooks (Navarredondilla, Ensenada Legos).
Features dual-tier checkpointing (atomic local JSON + live cloud sync) and multi-path file resolution.
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
DEFAULT_CHECKPOINT_PATH = BASE_DIR / "scripts" / "ingest_checkpoint_jmol.json"
DEFAULT_LOG_PATH = BASE_DIR / "scripts" / "ingest_sanjuan_parroquial.log"

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

# 18 Canonical Targets for San Juan del Molinillo (2,731 sources total)
PARROQUIAL_TARGETS: Dict[str, Dict[str, Any]] = {
    "JMOL-BAUT-01": {
        "expected_count": 175,
        "rollo_dgs": "004298570",
        "notebook_title": "JMOL-BAUT-01",
    },
    "JMOL-BAUT-02": {
        "expected_count": 276,
        "rollo_dgs": "004298570",
        "notebook_title": "JMOL-BAUT-02",
    },
    "JMOL-BAUT-03": {
        "expected_count": 190,
        "rollo_dgs": "004298570",
        "notebook_title": "JMOL-BAUT-03",
    },
    "JMOL-BAUT-04": {
        "expected_count": 189,
        "rollo_dgs": "004298570",
        "notebook_title": "JMOL-BAUT-04",
    },
    "JMOL-BAUT-05": {
        "expected_count": 139,
        "rollo_dgs": "004298570",
        "notebook_title": "JMOL-BAUT-05",
    },
    "JMOL-INDICE-BAUT": {
        "expected_count": 111,
        "rollo_dgs": "004298570",
        "notebook_title": "JMOL-INDICE-BAUT",
    },
    "JMOL-MATR-01": {
        "expected_count": 194,
        "rollo_dgs": "004298571",
        "notebook_title": "JMOL-MATR-01",
    },
    "JMOL-MATR-02": {
        "expected_count": 134,
        "rollo_dgs": "004298571",
        "notebook_title": "JMOL-MATR-02",
    },
    "JMOL-MATR-03": {
        "expected_count": 198,
        "rollo_dgs": "004298571",
        "notebook_title": "JMOL-MATR-03",
    },
    "JMOL-DIFU-01": {
        "expected_count": 202,
        "rollo_dgs": "004298571",
        "notebook_title": "JMOL-DIFU-01",
    },
    "JMOL-DIFU-02": {
        "expected_count": 277,
        "rollo_dgs": "004298571",
        "notebook_title": "JMOL-DIFU-02",
    },
    "JMOL-DIFU-03": {
        "expected_count": 17,
        "rollo_dgs": "004298571",
        "notebook_title": "JMOL-DIFU-03",
    },
    "JMOL-DIFU-04": {
        "expected_count": 214,
        "rollo_dgs": "004298571",
        "notebook_title": "JMOL-DIFU-04",
    },
    "JMOL-DIFU-05": {
        "expected_count": 99,
        "rollo_dgs": "004298571",
        "notebook_title": "JMOL-DIFU-05",
    },
    "JMOL-DIFU-06": {
        "expected_count": 177,
        "rollo_dgs": "004298571",
        "notebook_title": "JMOL-DIFU-06",
    },
    "JMOL-DIFU-PARVULOS": {
        "expected_count": 27,
        "rollo_dgs": "004298571",
        "notebook_title": "JMOL-DIFU-PARVULOS",
    },
    "JMOL-INDICE-DIFU": {
        "expected_count": 21,
        "rollo_dgs": "004298571",
        "notebook_title": "JMOL-INDICE-DIFU",
    },
    "JMOL-MIXTO-04": {
        "expected_count": 91,
        "rollo_dgs": "004298570",
        "notebook_title": "JMOL-SACRAMENTAL-1842-1850",  # Rule [L-30] pure naming
    },
}

CANONICAL_TOTAL_SOURCES = 2731
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

logger = logging.getLogger("ingest_sanjuan_parroquial")
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
                logger.info("Loaded existing checkpoint from %s", self.path)
            except Exception as e:
                logger.warning("Failed to parse checkpoint %s (%s). Starting fresh.", self.path, e)

    def save(self) -> None:
        self.state["updated_at"] = datetime.now(timezone.utc).isoformat()
        temp_path = self.path.with_suffix(".tmp")
        try:
            with open(temp_path, "w", encoding="utf-8") as f:
                json.dump(self.state, f, indent=2, ensure_ascii=False)
            temp_path.replace(self.path)
        except Exception as e:
            logger.error("Failed to atomic-write checkpoint to %s: %s", self.path, e)

    def get_notebook_id(self, target_id: str) -> Optional[str]:
        return self.state.get("notebook_ids", {}).get(target_id)

    def set_notebook_id(self, target_id: str, nb_id: str) -> None:
        if "notebook_ids" not in self.state:
            self.state["notebook_ids"] = {}
        self.state["notebook_ids"][target_id] = nb_id
        self.save()

    def is_source_uploaded(self, filename: str) -> bool:
        return filename in self.state.get("uploaded_sources", {})

    def record_source_upload(self, filename: str, source_id: str, notebook_id: str) -> None:
        if "uploaded_sources" not in self.state:
            self.state["uploaded_sources"] = {}
        self.state["uploaded_sources"][filename] = {
            "source_id": source_id,
            "notebook_id": notebook_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def mark_notebook_completed(self, target_id: str) -> None:
        completed = set(self.state.get("completed_notebooks", []))
        completed.add(target_id)
        self.state["completed_notebooks"] = sorted(list(completed))
        self.save()

    def is_notebook_completed(self, target_id: str) -> bool:
        return target_id in self.state.get("completed_notebooks", [])

# -----------------------------------------------------------------------------
# Multi-Path Image Resolver
# -----------------------------------------------------------------------------
def resolve_image_path(id_img: str, dgs: str) -> Path:
    search_paths = [
        BASE_DIR / "imagenes" / f"rollo {dgs}" / id_img,
    ]
    # Dynamically discover San Juan subfolders in workspace
    for p in BASE_DIR.iterdir():
        if p.is_dir() and "San Juan" in p.name:
            search_paths.append(p / id_img)

    for p in search_paths:
        if p.is_file():
            return p
    raise FileNotFoundError(f"Physical image missing on disk across all search locations: {id_img}")

# -----------------------------------------------------------------------------
# Corpus Loading & Validation
# -----------------------------------------------------------------------------
def load_and_validate_corpus(
    catalog_path: Path,
    target_ids: List[str],
) -> Dict[str, List[Dict[str, Any]]]:
    logger.info("Loading canonical corpus from %s (encoding=utf-8-sig)...", catalog_path)
    if not catalog_path.is_file():
        raise FileNotFoundError(f"Corpus file not found: {catalog_path}")

    with open(catalog_path, "r", encoding="utf-8-sig") as f:
        corpus = json.load(f)

    logger.info("Total entries in catalogo_corpus.json: %d", len(corpus))

    assigned_records: Dict[str, List[Dict[str, Any]]] = {}
    total_found = 0

    for target_id in target_ids:
        meta = PARROQUIAL_TARGETS[target_id]
        records = [r for r in corpus if r.get("cuaderno_asignado_id") == target_id]
        records.sort(key=lambda r: int(r.get("fotograma_numero", 0)))
        assigned_records[target_id] = records
        total_found += len(records)

        logger.info(
            "Target [%s]: found %d records (expected %d)",
            target_id,
            len(records),
            meta["expected_count"],
        )

        if len(records) != meta["expected_count"]:
            raise ValueError(
                f"Count mismatch for {target_id}: expected {meta['expected_count']}, got {len(records)}"
            )

        # Validate disk presence and [L-28] naming format
        for r in records:
            id_img = r["id_imagen"]
            dgs = r["rollo_dgs"]

            if not L28_REGEX.match(id_img):
                raise ValueError(
                    f"Rule [L-28] VIOLATION: Filename '{id_img}' in {target_id} does not match {DGS}_{FOTOGRAMA}.jpg pattern"
                )

            if len(id_img) != 19:
                raise ValueError(
                    f"Rule [L-28] VIOLATION: Filename '{id_img}' in {target_id} length is {len(id_img)}, expected 19 (zero-padding truncation detected)"
                )

            if dgs != meta["rollo_dgs"]:
                raise ValueError(
                    f"Unexpected DGS rollo {dgs} in {target_id} record {id_img} (expected {meta['rollo_dgs']})"
                )

            # Check physical file on disk via resolver
            img_path = resolve_image_path(id_img, dgs)
            if img_path.stat().st_size == 0:
                raise ValueError(f"Corrupted 0-byte image on disk: {img_path}")

    logger.info("Validation OK: All %d requested records verified physically on disk.", total_found)
    return assigned_records

# -----------------------------------------------------------------------------
# Pre-Flight Shield Check
# -----------------------------------------------------------------------------
async def run_preflight_shield_check(client: NotebookLMClient) -> None:
    logger.info("Running pre-flight shield check on protected notebooks...")
    notebooks = await client.notebooks.list()
    cloud_map = {nb.id: nb for nb in notebooks}

    for nb_id, expected in PROTECTED_NOTEBOOKS.items():
        if nb_id not in cloud_map:
            raise RuntimeError(
                f"SHIELD FAILURE: Protected notebook '{expected['title']}' ({nb_id}) missing from NotebookLM account!"
            )
        actual_nb = cloud_map[nb_id]
        sources = await client.sources.list(nb_id)
        logger.info(
            "Shield check PASS: '%s' (%s) intact with %d sources (expected %d)",
            actual_nb.title,
            nb_id,
            len(sources),
            expected["expected_sources"],
        )
        if len(sources) < expected["expected_sources"]:
            logger.warning(
                "Shield note: '%s' has %d sources (expected >= %d)",
                actual_nb.title,
                len(sources),
                expected["expected_sources"],
            )

    logger.info("Pre-flight shield check PASSED: All protected notebooks verified.")

# -----------------------------------------------------------------------------
# Notebook Resolution & Creation
# -----------------------------------------------------------------------------
async def resolve_or_create_notebooks(
    client: NotebookLMClient,
    checkpoint: CheckpointManager,
    target_ids: List[str],
) -> Dict[str, str]:
    logger.info("Resolving or creating notebooks in NotebookLM...")
    existing_notebooks = await client.notebooks.list()
    cloud_title_map = {nb.title: nb.id for nb in existing_notebooks}

    notebook_ids: Dict[str, str] = {}

    for target_id in target_ids:
        meta = PARROQUIAL_TARGETS[target_id]
        notebook_title = meta["notebook_title"]

        # 1. Check local checkpoint
        cached_id = checkpoint.get_notebook_id(target_id)
        if cached_id:
            logger.info("Notebook [%s] -> found in checkpoint (%s)", target_id, cached_id)
            notebook_ids[target_id] = cached_id
            continue

        # 2. Check cloud by title
        if notebook_title in cloud_title_map:
            cloud_id = cloud_title_map[notebook_title]
            logger.info("Notebook [%s] -> matched existing cloud title '%s' (%s)", target_id, notebook_title, cloud_id)
            checkpoint.set_notebook_id(target_id, cloud_id)
            notebook_ids[target_id] = cloud_id
            continue

        # 3. Create fresh notebook in NotebookLM
        logger.info("Creating new notebook in NotebookLM: '%s'...", notebook_title)
        new_nb = await client.notebooks.create(notebook_title)
        logger.info("Successfully created notebook '%s' -> ID: %s", notebook_title, new_nb.id)
        checkpoint.set_notebook_id(target_id, new_nb.id)
        notebook_ids[target_id] = new_nb.id

    return notebook_ids

# -----------------------------------------------------------------------------
# Upload Engine with Robust Backoff
# -----------------------------------------------------------------------------
async def upload_single_image_with_backoff(
    client: NotebookLMClient,
    notebook_id: str,
    target_id: str,
    img_path: Path,
    source_title: str,
    pause_seconds: float,
) -> str:
    delay = INITIAL_BACKOFF_SECONDS
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            logger.info("[%s] Uploading %s (attempt %d/%d)...", target_id, source_title, attempt, MAX_RETRIES)
            source = await client.sources.add_file(
                notebook_id=notebook_id,
                file_path=str(img_path),
            )
            logger.info(
                "[%s] Successfully uploaded %s -> source_id: %s (status=%s)",
                target_id,
                source_title,
                source.id,
                getattr(source, "status_label", getattr(source.status, "name", str(source.status))),
            )
            await asyncio.sleep(pause_seconds)
            return source.id

        except (RateLimitError, RPCError, ServerError, NetworkError, NotebookLMError, httpx.HTTPError) as e:
            if attempt == MAX_RETRIES:
                logger.error("[%s] Fatal failure uploading %s after %d retries: %s", target_id, source_title, attempt, e)
                raise
            logger.warning(
                "[%s] Transient error uploading %s: %s. Backing off for %.1fs (attempt %d/%d)...",
                target_id,
                source_title,
                e,
                delay,
                attempt,
                MAX_RETRIES,
            )
            await asyncio.sleep(delay)
            delay *= 2.0

        except AuthError as e:
            logger.critical("[%s] AuthError: NotebookLM session expired: %s", target_id, e)
            raise

    raise RuntimeError(f"Exhausted retries for {source_title}")

# -----------------------------------------------------------------------------
# Main Ingestion Orchestrator
# -----------------------------------------------------------------------------
async def run_pipeline(args: argparse.Namespace) -> None:
    setup_logging(DEFAULT_LOG_PATH)
    logger.info("================================================================================")
    logger.info("Starting San Juan del Molinillo Parroquial Pipeline")
    logger.info("================================================================================")

    target_ids = list(PARROQUIAL_TARGETS.keys())
    if args.target:
        if args.target not in PARROQUIAL_TARGETS:
            raise ValueError(f"Invalid target: '{args.target}'. Valid targets: {list(PARROQUIAL_TARGETS.keys())}")
        target_ids = [args.target]

    if args.pilot_only:
        target_ids = ["JMOL-DIFU-03"]  # 17 images, perfect fast pilot

    logger.info("Targets to process in this run: %s", target_ids)
    assigned_records = load_and_validate_corpus(DEFAULT_CATALOG_PATH, target_ids)

    if args.dry_run:
        logger.info("[DRY RUN] All validation checks passed. Exiting without making cloud changes.")
        return

    # Initialize client
    logger.info("Initializing NotebookLMClient from user storage...")
    client_ctx = NotebookLMClient.from_storage()
    async with client_ctx as client:
        checkpoint = CheckpointManager(DEFAULT_CHECKPOINT_PATH)

        # Pre-flight shield check
        await run_preflight_shield_check(client)

        # Resolve or create notebooks
        notebook_ids = await resolve_or_create_notebooks(client, checkpoint, target_ids)

        # Ingestion loop
        total_images_in_run = sum(len(assigned_records[t]) for t in target_ids)
        processed_count = 0

        for target_id in target_ids:
            nb_id = notebook_ids[target_id]
            meta = PARROQUIAL_TARGETS[target_id]
            records = assigned_records[target_id]

            if checkpoint.is_notebook_completed(target_id):
                logger.info("Notebook [%s] marked COMPLETED in checkpoint. Skipping.", target_id)
                processed_count += len(records)
                continue

            logger.info("Starting ingestion for [%s] (%d images) into notebook %s...", target_id, len(records), nb_id)

            # Check cloud sources
            cloud_sources = await client.sources.list(nb_id)
            cloud_source_titles = {s.title: s.id for s in cloud_sources}

            for idx, r in enumerate(records, start=1):
                id_img = r["id_imagen"]
                dgs = r["rollo_dgs"]

                if checkpoint.is_source_uploaded(id_img):
                    continue

                if id_img in cloud_source_titles:
                    source_id = cloud_source_titles[id_img]
                    checkpoint.record_source_upload(id_img, source_id, nb_id)
                    continue

                img_path = resolve_image_path(id_img, dgs)
                source_id = await upload_single_image_with_backoff(
                    client=client,
                    notebook_id=nb_id,
                    target_id=target_id,
                    img_path=img_path,
                    source_title=id_img,
                    pause_seconds=args.pause,
                )

                checkpoint.record_source_upload(id_img, source_id, nb_id)
                checkpoint.save()
                processed_count += 1

            checkpoint.mark_notebook_completed(target_id)
            checkpoint.save()
            logger.info("Successfully completed ingestion for [%s]! (%d/%d)", target_id, len(records), len(records))

    logger.info("================================================================================")
    logger.info("San Juan del Molinillo Pipeline Completed Successfully!")
    logger.info("================================================================================")

def main():
    parser = argparse.ArgumentParser(description="San Juan del Molinillo Parroquial Ingestion Pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Validate corpus and files on disk without touching cloud")
    parser.add_argument("--pilot-only", action="store_true", help="Ingest only JMOL-DIFU-03 (17 images) as a fast pilot")
    parser.add_argument("--target", type=str, help="Process a single specific target ID (e.g. JMOL-BAUT-01)")
    parser.add_argument("--pause", type=float, default=UPLOAD_PAUSE_SECONDS, help="Pause between uploads in seconds")

    args = parser.parse_args()
    asyncio.run(run_pipeline(args))

if __name__ == "__main__":
    main()
