"""
Añade las imágenes con partidas matrimoniales dispersas del siglo XVII (procedentes del Libro Mixto 01)
al cuaderno puro NRDL-MATR-01 (1634-1698) bajo la Regla [L-31] (duplicidad lógica):
- Bloque continuo 1656-1698: 004306112_02013.jpg a 004306112_02019.jpg
- Folios intercalados / sueltos: 02021, 02022, 02042, 02043, 02044, 02048, 02049, 02150, 02151, 02152, 02153, 02154
"""

import asyncio
import logging
from pathlib import Path
from notebooklm import NotebookLMClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

NOTEBOOK_MATR_ID = "1e6fec74-1e2f-4dd7-8ad1-6d25411de127"
IMAGES_FOLDER = Path("imagenes/rollo 004306112")

TARGET_FILES = [
    # Bloque continuo principal 1656-1698
    "004306112_02013.jpg",
    "004306112_02014.jpg",
    "004306112_02015.jpg",
    "004306112_02016.jpg",
    "004306112_02017.jpg",
    "004306112_02018.jpg",
    "004306112_02019.jpg",
    # Folios intercalados con asientos de casados
    "004306112_02021.jpg",
    "004306112_02022.jpg",
    "004306112_02042.jpg",
    "004306112_02043.jpg",
    "004306112_02044.jpg",
    "004306112_02048.jpg",
    "004306112_02049.jpg",
    # Tiras cosidas y minutas de casados
    "004306112_02150.jpg",
    "004306112_02151.jpg",
    "004306112_02152.jpg",
    "004306112_02153.jpg",
    "004306112_02154.jpg",
]


async def main():
    logging.info("=== REORGANIZACIÓN CODICOLÓGICA [L-30]: MATRIMONIOS S. XVII EN NRDL-MATR-01 ===")
    async with NotebookLMClient.from_storage() as client:
        sources = await client.sources.list(NOTEBOOK_MATR_ID)
        existing_titles = {s.title: s for s in sources}
        logging.info(f"Fuentes iniciales en NRDL-MATR-01: {len(sources)}")

        added = 0
        for fname in TARGET_FILES:
            if fname in existing_titles:
                logging.info(f"  -> {fname} ya está presente en el cuaderno. Saltando.")
                continue

            file_path = IMAGES_FOLDER / fname
            if not file_path.exists():
                logging.error(f"  [ERROR] No se encuentra en disco: {file_path}")
                continue

            logging.info(f"  -> Inyectando {fname} en NRDL-MATR-01...")
            source = await client.sources.add_file(NOTEBOOK_MATR_ID, file_path, wait=True)
            logging.info(f"     Subido con éxito: {fname} -> ID {source.id} (estado: {source.status})")
            added += 1
            await asyncio.sleep(2.5)  # Respetar rate-limit anti-429

        final_sources = await client.sources.list(NOTEBOOK_MATR_ID)
        logging.info(f"=== RESULTADO: {added} imágenes añadidas. Total fuentes en NRDL-MATR-01: {len(final_sources)} ===")


if __name__ == "__main__":
    asyncio.run(main())
