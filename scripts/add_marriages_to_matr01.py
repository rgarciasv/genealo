"""
Añade las 3 imágenes con partidas matrimoniales dispersas/híbridas al cuaderno NRDL-MATR-01:
- 004306112_02050.jpg (boda Alonso Sánchez con Francisca Andrino intercalada en bautismos)
- 004306112_02148.jpg (tira de papel cosida con 3 bodas de 1667)
- 004306112_02149.jpg (tira de papel cosida con bodas de 1667-1668)
"""

import asyncio
import logging
from pathlib import Path
from notebooklm import NotebookLMClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

NOTEBOOK_MATR_ID = "1e6fec74-1e2f-4dd7-8ad1-6d25411de127"
IMAGES_FOLDER = Path("imagenes/rollo 004306112")

TARGET_FILES = [
    "004306112_02050.jpg",
    "004306112_02148.jpg",
    "004306112_02149.jpg",
]


async def main():
    logging.info(f"=== DUPLICACIÓN LÓGICA DE PARTIDAS MATRIMONIALES [L-31] EN NRDL-MATR-01 ===")
    async with NotebookLMClient.from_storage() as client:
        sources = await client.sources.list(NOTEBOOK_MATR_ID)
        existing_titles = {s.title: s for s in sources}
        logging.info(f"Fuentes actuales en NRDL-MATR-01: {len(sources)}")

        for fname in TARGET_FILES:
            if fname in existing_titles:
                logging.info(f"  -> {fname} ya está en NRDL-MATR-01. Saltando.")
                continue

            file_path = IMAGES_FOLDER / fname
            if not file_path.exists():
                logging.error(f"  [ERROR] No se encuentra en disco: {file_path}")
                continue

            logging.info(f"  -> Subiendo {fname} a NRDL-MATR-01...")
            source = await client.sources.add_file(NOTEBOOK_MATR_ID, file_path, wait=True)
            logging.info(f"     Subido: {fname} -> ID {source.id} (status: {source.status})")
            await asyncio.sleep(2.0)

        final_sources = await client.sources.list(NOTEBOOK_MATR_ID)
        logging.info(f"Total fuentes final en NRDL-MATR-01: {len(final_sources)} (33 iniciales + 3 añadidas)")
        logging.info("=== COMPLETADO CON ÉXITO ===")


if __name__ == "__main__":
    asyncio.run(main())
