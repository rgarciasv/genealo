#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Deduplication utility for San Juan del Molinillo parish notebooks.
Removes duplicate cloud sources in JMOL-MATR-02 and JMOL-MATR-03, keeping READY sources.
"""

import asyncio
import logging
from notebooklm import NotebookLMClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("dedup_jmol")

NOTEBOOKS_TO_CLEAN = {
    "JMOL-MATR-02": "772135ac-4305-4a22-ad89-bf996f0ff37a",
    "JMOL-MATR-03": "07a61f80-24e6-484e-af57-ebe19d09960a",
}


async def main():
    logger.info("Initializing NotebookLMClient for deduplication...")
    async with NotebookLMClient.from_storage() as client:
        for title, nb_id in NOTEBOOKS_TO_CLEAN.items():
            logger.info("Checking %s (%s)...", title, nb_id)
            sources = await client.sources.list(nb_id)
            by_title = {}
            for s in sources:
                by_title.setdefault(s.title, []).append(s)

            deleted_count = 0
            for src_title, src_list in by_title.items():
                if len(src_list) > 1:
                    # Sort so READY ones are first
                    def sort_key(s):
                        st = getattr(s, "status_label", getattr(s.status, "name", str(s.status))).upper()
                        return 0 if st == "READY" else 1

                    sorted_sources = sorted(src_list, key=sort_key)
                    keep = sorted_sources[0]
                    to_delete = sorted_sources[1:]

                    for d in to_delete:
                        st_name = getattr(d.status, "name", str(d.status))
                        logger.info("[%s] Deleting duplicate %s (id=%s, status=%s)...", title, src_title, d.id, st_name)
                        await client.sources.delete(nb_id, d.id)
                        deleted_count += 1
                        await asyncio.sleep(0.5)

            # Re-verify count
            updated = await client.sources.list(nb_id)
            ready_count = sum(1 for s in updated if getattr(s.status, "name", str(s.status)) == "READY")
            logger.info("[%s] Finished: Deleted %d duplicates. Remaining total: %d (%d READY).", title, deleted_count, len(updated), ready_count)


if __name__ == "__main__":
    asyncio.run(main())
