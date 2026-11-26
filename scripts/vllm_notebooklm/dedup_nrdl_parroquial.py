import asyncio
import logging
from notebooklm import NotebookLMClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("dedup_nrdl")

NOTEBOOKS_TO_CHECK = {
    "NRDL-BAUT-03": "6853e55d-3e72-42d3-bf01-6d2a510978b7",
    "NRDL-DIFU-02": "1e77ba17-cf48-4fca-8a0a-e91aa41eb4bb",
    "NRDL-DIFU-05": "d73e0a6c-7fa9-4c78-aec9-6c0bfcfd2ccf",
}

async def main():
    logger.info("Initializing NotebookLMClient...")
    client_ctx = NotebookLMClient.from_storage()
    async with client_ctx as client:
        for title, nb_id in NOTEBOOKS_TO_CHECK.items():
            logger.info("Checking %s (%s)...", title, nb_id)
            sources = await client.sources.list(nb_id)
            by_title = {}
            for s in sources:
                by_title.setdefault(s.title, []).append(s)

            for src_title, src_list in by_title.items():
                if len(src_list) > 1:
                    logger.warning("[%s] Found %d duplicates for %s", title, len(src_list), src_title)
                    # Sort so READY ones are first, if any is non-READY it goes to the end
                    # Then keep the first, delete the rest
                    def sort_key(s):
                        st = getattr(s, "status_label", getattr(s.status, "name", str(s.status))).upper()
                        return 0 if st == "READY" else 1

                    sorted_sources = sorted(src_list, key=sort_key)
                    keep = sorted_sources[0]
                    to_delete = sorted_sources[1:]
                    
                    logger.info("  Keeping source ID: %s (status=%s)", keep.id, getattr(keep.status, "name", str(keep.status)))
                    for d in to_delete:
                        logger.info("  Deleting duplicate source ID: %s (status=%s)...", d.id, getattr(d.status, "name", str(d.status)))
                        await client.sources.delete(nb_id, d.id)
                        logger.info("  Deleted successfully: %s", d.id)

            # Re-list to check final count
            updated = await client.sources.list(nb_id)
            ready_count = sum(1 for s in updated if getattr(s.status, "name", str(s.status)) == "READY")
            logger.info("[%s] Final count: %d sources (%d READY)", title, len(updated), ready_count)

if __name__ == "__main__":
    asyncio.run(main())
