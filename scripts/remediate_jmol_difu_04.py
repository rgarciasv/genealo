#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Remediation script for San Juan del Molinillo notebook JMOL-DIFU-04.
Uploads the missing image 004298571_01084.jpg, waits for READY status,
and updates scripts/ingest_checkpoint_jmol.json.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from notebooklm import NotebookLMClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("remediate_difu_04")

BASE_DIR = Path(__file__).resolve().parent.parent
TARGET_NOTEBOOK_ID = "457361c1-70f8-4368-8e86-10b0beeb169f"
TARGET_NOTEBOOK_TITLE = "JMOL-DIFU-04"
IMAGE_FILENAME = "004298571_01084.jpg"
IMAGE_PATH = BASE_DIR / "imagenes" / "rollo 004298571" / IMAGE_FILENAME
CHECKPOINT_PATH = BASE_DIR / "scripts" / "ingest_checkpoint_jmol.json"


def get_status_str(src) -> str:
    raw = getattr(src, "status", None)
    if raw is None:
        return "UNKNOWN"
    if hasattr(raw, "name"):
        return str(raw.name)
    val = getattr(src, "status_label", None)
    if val:
        return str(val)
    return str(raw)


async def main():
    if not IMAGE_PATH.is_file():
        logger.error("Image file not found: %s", IMAGE_PATH)
        sys.exit(1)

    logger.info("Target image: %s (size: %d bytes)", IMAGE_PATH, IMAGE_PATH.stat().st_size)
    logger.info("Initializing NotebookLMClient...")

    async with NotebookLMClient.from_storage() as client:
        # Check current notebook status
        sources = await client.sources.list(TARGET_NOTEBOOK_ID)
        logger.info("Current sources in %s: %d", TARGET_NOTEBOOK_TITLE, len(sources))

        existing = [s for s in sources if s.title == IMAGE_FILENAME]
        source_id = None

        if existing:
            st = get_status_str(existing[0]).upper()
            logger.info("Found existing source %s with status %s", existing[0].id, st)
            if st == "READY":
                source_id = existing[0].id
                logger.info("Source is already READY with ID %s", source_id)
            else:
                logger.warning("Deleting non-READY source %s (status=%s)...", existing[0].id, st)
                await client.sources.delete(TARGET_NOTEBOOK_ID, existing[0].id)
                await asyncio.sleep(1.0)

        if not source_id:
            logger.info("Uploading %s to notebook %s (%s)...", IMAGE_FILENAME, TARGET_NOTEBOOK_TITLE, TARGET_NOTEBOOK_ID)
            upload_result = await client.sources.add_file(
                TARGET_NOTEBOOK_ID,
                str(IMAGE_PATH),
                wait=False,
            )
            source_id = upload_result.id
            logger.info("Upload initiated -> source_id: %s", source_id)

        # Confirm status is READY
        logger.info("Verifying source %s readiness...", source_id)
        st = "UNKNOWN"
        for poll_attempt in range(1, 61):
            src_info = await client.sources.get_or_none(TARGET_NOTEBOOK_ID, source_id)
            if src_info is None:
                logger.info("Poll attempt %d/60: source %s not returned yet...", poll_attempt, source_id)
                await asyncio.sleep(2.0)
                continue
            st = get_status_str(src_info).upper()
            logger.info("Poll attempt %d/60: source %s status is %s", poll_attempt, source_id, st)
            if st == "READY":
                logger.info("Source %s reached READY status on attempt %d!", source_id, poll_attempt)
                break
            await asyncio.sleep(2.5)
        else:
            logger.error("Source %s did not reach READY status in time! Last status: %s", source_id, st)
            sys.exit(1)

        # Re-list all sources in JMOL-DIFU-04
        all_sources = await client.sources.list(TARGET_NOTEBOOK_ID)
        ready_count = sum(1 for s in all_sources if get_status_str(s).upper() == "READY")
        logger.info(
            "JMOL-DIFU-04 validation: %d sources present (%d READY / expected 214)",
            len(all_sources),
            ready_count,
        )

        if len(all_sources) != 214 or ready_count != 214:
            logger.error("Count mismatch in JMOL-DIFU-04: total=%d, ready=%d", len(all_sources), ready_count)
            sys.exit(1)

        # Update checkpoint
        logger.info("Updating checkpoint file %s...", CHECKPOINT_PATH)
        with open(CHECKPOINT_PATH, "r", encoding="utf-8") as f:
            checkpoint = json.load(f)

        now_iso = datetime.now(timezone.utc).isoformat()
        checkpoint.setdefault("uploaded_sources", {})[IMAGE_FILENAME] = {
            "source_id": source_id,
            "notebook_id": TARGET_NOTEBOOK_ID,
            "timestamp": now_iso,
        }
        checkpoint["updated_at"] = now_iso

        tmp_path = CHECKPOINT_PATH.with_suffix(".json.tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(checkpoint, f, indent=2, ensure_ascii=False)
        os.replace(tmp_path, CHECKPOINT_PATH)
        logger.info("Checkpoint successfully updated with %s (source_id: %s)", IMAGE_FILENAME, source_id)


if __name__ == "__main__":
    asyncio.run(main())
