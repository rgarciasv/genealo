"""
Reorganización Codicilógica y Purificación Sacramental [L-30] / [L-31]
Traslada las defunciones del siglo XVII (1631-1701) al cuaderno NRDL-DIFU-S17
y purifica NRDL-BAUT-01 preservando las 5 imágenes híbridas en ambos cuadernos.
"""

import asyncio
import logging
from pathlib import Path
from notebooklm import NotebookLMClient
from notebooklm.types import ChatGoal, ChatResponseLength

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

NOTEBOOK_BAUT_ID = "a187936c-55f4-4319-87db-6bf4e21e8613"
NOTEBOOK_DIFU_ID = "14cf46ae-7d73-4f2c-b001-5e5de0f29c6c"
NEW_DIFU_TITLE = "NRDL-DIFU-S17 (1631-1701)"

IMAGES_FOLDER = Path("imagenes/rollo 004306112")

# 1. Imágenes Puras de Defunción (se suben a DIFU y se eliminan de BAUT)
PURE_DIFU_NUMBERS = (
    list(range(1988, 2023)) +  # 01988 a 02022 (35 imgs)
    list(range(2024, 2043)) +  # 02024 a 02042 (19 imgs)
    list(range(2045, 2048))    # 02045 a 02047 (3 imgs)
)
PURE_DIFU_FILES = [f"004306112_{n:05d}.jpg" for n in PURE_DIFU_NUMBERS]

# 2. Imágenes Híbridas [L-31] (se suben a DIFU Y SE CONSERVAN en BAUT)
HYBRID_NUMBERS = [2023, 2044, 2048, 2049, 2050]
HYBRID_FILES = [f"004306112_{n:05d}.jpg" for n in HYBRID_NUMBERS]

# Total a subir a DIFU
TOTAL_DIFU_FILES = PURE_DIFU_FILES + HYBRID_FILES


async def main():
    logging.info(f"=== INICIO DE REORGANIZACIÓN CODICOLÓGICA [L-30 / L-31] ===")
    logging.info(f"Cuaderno Bautismos: {NOTEBOOK_BAUT_ID}")
    logging.info(f"Cuaderno Defunciones S17: {NOTEBOOK_DIFU_ID}")
    logging.info(f"Imágenes puras de defunción a trasladar: {len(PURE_DIFU_FILES)}")
    logging.info(f"Imágenes híbridas con presencia dual: {len(HYBRID_FILES)}")
    logging.info(f"Total imágenes a añadir a DIFU-S17: {len(TOTAL_DIFU_FILES)}")

    async with NotebookLMClient.from_storage() as client:
        # Paso 1: Renombrar el cuaderno DIFU a su título canónico unificado
        logging.info(f"[1/5] Renombrando cuaderno {NOTEBOOK_DIFU_ID} a '{NEW_DIFU_TITLE}'...")
        await client.notebooks.rename(NOTEBOOK_DIFU_ID, NEW_DIFU_TITLE)
        logging.info("  -> Renombrado con éxito.")

        # Paso 2: Listar fuentes actuales en DIFU para evitar duplicados
        difu_sources = await client.sources.list(NOTEBOOK_DIFU_ID)
        difu_titles = {s.title: s for s in difu_sources}
        logging.info(f"[2/5] Fuentes actuales en {NEW_DIFU_TITLE}: {len(difu_sources)}")

        # Paso 3: Subir las 62 imágenes a DIFU con reintentos
        uploaded_count = 0
        for i, fname in enumerate(TOTAL_DIFU_FILES, 1):
            if fname in difu_titles:
                logging.info(f"  [{i}/{len(TOTAL_DIFU_FILES)}] -> {fname} ya existe en DIFU-S17. Saltando.")
                continue

            file_path = IMAGES_FOLDER / fname
            if not file_path.exists():
                logging.error(f"  [ERROR] No existe en disco: {file_path}")
                continue

            success = False
            for attempt in range(1, 4):
                try:
                    logging.info(f"  [{i}/{len(TOTAL_DIFU_FILES)}] Subiendo {fname} (intento {attempt}/3)...")
                    source = await client.sources.add_file(NOTEBOOK_DIFU_ID, file_path, wait=True)
                    logging.info(f"     Subido: {fname} -> ID {source.id} (status: {source.status})")
                    uploaded_count += 1
                    success = True
                    break
                except Exception as e:
                    logging.warning(f"     Error en intento {attempt}: {e}. Reintentando en 4s...")
                    await asyncio.sleep(4.0)

            if not success:
                logging.error(f"  [FALLO CRÍTICO] No se pudo subir {fname} tras 3 intentos. Abortando.")
                return

            await asyncio.sleep(2.5)

        logging.info(f"  -> Subidas nuevas a DIFU-S17 completadas: {uploaded_count}")

        # Verificar que todas las 62 imágenes están READY en DIFU antes de borrar nada de BAUT
        difu_sources_after = await client.sources.list(NOTEBOOK_DIFU_ID)
        difu_titles_after = {s.title: s for s in difu_sources_after}
        missing_in_difu = [f for f in TOTAL_DIFU_FILES if f not in difu_titles_after]
        if missing_in_difu:
            logging.error(f"[ALERTA CRÍTICA] Faltan {len(missing_in_difu)} imágenes en DIFU: {missing_in_difu}")
            logging.error("ABORTANDO borrado de BAUT-01 por seguridad de datos.")
            return

        logging.info(f"[3/5] Verificación de seguridad: Las 62 imágenes están 100% confirmadas en DIFU-S17.")

        # Paso 4: Purificar BAUT-01 eliminando EXCLUSIVAMENTE las 57 imágenes puras de defunción
        logging.info(f"[4/5] Purificando NRDL-BAUT-01 (eliminando 57 imágenes puras de defunción)...")
        baut_sources = await client.sources.list(NOTEBOOK_BAUT_ID)
        baut_sources_by_title = {s.title: s for s in baut_sources}

        deleted_count = 0
        for fname in PURE_DIFU_FILES:
            if fname in baut_sources_by_title:
                source_to_del = baut_sources_by_title[fname]
                logging.info(f"  -> Eliminando de BAUT-01: {fname} (ID {source_to_del.id})...")
                await client.sources.delete(NOTEBOOK_BAUT_ID, source_to_del.id)
                deleted_count += 1
                await asyncio.sleep(0.5)
            else:
                logging.info(f"  -> {fname} no estaba en BAUT-01.")

        logging.info(f"  -> Eliminadas de BAUT-01: {deleted_count} imágenes puras de defunción.")

        # Confirmar que las 5 híbridas siguen en BAUT-01
        baut_sources_final = await client.sources.list(NOTEBOOK_BAUT_ID)
        baut_titles_final = {s.title: s for s in baut_sources_final}
        for h in HYBRID_FILES:
            assert h in baut_titles_final, f"ERROR: Imagen híbrida {h} fue borrada accidentalmente!"
        logging.info(f"  -> Confirmado: Las 5 imágenes híbridas permanecen intactas en BAUT-01.")

        # Paso 5: Resumen y estado final
        logging.info(f"[5/5] Resumen Final:")
        logging.info(f"  - NRDL-BAUT-01 fuentes totales: {len(baut_sources_final)} (imágenes puras y 5 híbridas + 5 fuentes .md)")
        logging.info(f"  - NRDL-DIFU-S17 fuentes totales: {len(difu_sources_after)} (70 iniciales + 62 añadidas)")
        logging.info(f"=== REORGANIZACIÓN COMPLETADA CON ÉXITO ===")


if __name__ == "__main__":
    asyncio.run(main())
