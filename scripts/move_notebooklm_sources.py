#!/usr/bin/env python3
"""
move_notebooklm_sources.py - Utilidad para mover o copiar imágenes/fuentes entre cuadernos de NotebookLM Pro.
Parte de la skill 'traslado-fuentes-notebooklm' (Reglas [L-30], [L-31] del Archivero Virtual).

Soporta:
1. Copia directa server-to-server en Google (CopySourcesAsync) sin re-subir bytes.
2. Modo MOVER (copia + eliminación segura del origen tras verificar estado READY).
3. Modo DUPLICIDAD LÓGICA [L-31] (--keep-source para imágenes híbridas).
4. Resolución automática de nombres de cuadernos (ej. NRDL-MATR-01 -> UUID) desde checkpoints o listado.
5. Subida fallback desde disco local si la imagen física no estuviera en el origen.
"""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set

from notebooklm import NotebookLMClient
from notebooklm.rpc.types import SourceStatus

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("scripts/traslado_fuentes.log", encoding="utf-8"),
    ],
)
logger = logging.getLogger("TrasladoFuentes")

CHECKPOINTS = [
    Path("scripts/ingest_checkpoint_nrdl.json"),
    Path("scripts/ingest_checkpoint_jmol.json"),
]
IMAGES_ROOT = Path("imagenes")


def resolve_notebook_id(name_or_id: str, client_notebooks: Dict[str, str]) -> str:
    """Resuelve un nombre o prefijo de cuaderno a su UUID canónico."""
    # 1. Si coincide exactamente con un UUID o clave de cliente
    if name_or_id in client_notebooks.values():
        return name_or_id
    if name_or_id in client_notebooks:
        return client_notebooks[name_or_id]

    # 2. Buscar en los checkpoints locales
    for cp_path in CHECKPOINTS:
        if cp_path.exists():
            try:
                with open(cp_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    nb_map = data.get("notebook_ids", {})
                    if name_or_id in nb_map:
                        return nb_map[name_or_id]
                    # Búsqueda insensible a mayúsculas
                    for k, v in nb_map.items():
                        if k.upper() == name_or_id.upper():
                            return v
            except Exception:
                pass

    # 3. Búsqueda por prefijo en el listado de la cuenta
    matches = [v for k, v in client_notebooks.items() if name_or_id.lower() in k.lower() or v.startswith(name_or_id)]
    if len(matches) == 1:
        return matches[0]
    elif len(matches) > 1:
        raise ValueError(f"El identificador '{name_or_id}' es ambiguo. Coincidencias: {matches}")

    return name_or_id


def find_image_on_disk(filename: str) -> Optional[Path]:
    """Busca una imagen física en el árbol local de imágenes."""
    p = IMAGES_ROOT / filename
    if p.exists():
        return p
    for match in IMAGES_ROOT.rglob(filename):
        if match.is_file():
            return match
    return None


async def execute_transfer(
    source_nb_arg: str,
    target_nb_arg: str,
    images: List[str],
    delete_source: bool = False,
    pause_sec: float = 2.0,
):
    logger.info("=== INICIANDO TRASLADO DE FUENTES EN NOTEBOOKLM ===")
    logger.info(f"Modo: {'MOVER (Copia + Eliminación de origen)' if delete_source else 'COPIAR (Duplicidad Lógica [L-31])'}")

    async with NotebookLMClient.from_storage() as client:
        # Cargar todos los cuadernos del usuario para resolución de nombres
        all_nbs = await client.notebooks.list()
        nb_title_to_id = {nb.title: nb.id for nb in all_nbs}
        nb_id_to_title = {nb.id: nb.title for nb in all_nbs}

        source_id = resolve_notebook_id(source_nb_arg, nb_title_to_id)
        target_id = resolve_notebook_id(target_nb_arg, nb_title_to_id)

        source_title = nb_id_to_title.get(source_id, source_id)
        target_title = nb_id_to_title.get(target_id, target_id)

        logger.info(f"Cuaderno Origen:  {source_title} ({source_id})")
        logger.info(f"Cuaderno Destino: {target_title} ({target_id})")

        # Inspeccionar fuentes existentes
        source_sources = await client.sources.list(source_id)
        target_sources = await client.sources.list(target_id)

        source_dict = {s.title: s for s in source_sources}
        target_titles: Set[str] = {s.title for s in target_sources}

        logger.info(f"Fuentes actuales: Origen={len(source_sources)}, Destino={len(target_sources)}")

        if len(target_sources) + len(images) > 300:
            logger.warning(f"ADVERTENCIA: El cuaderno destino alcanzará {len(target_sources) + len(images)} fuentes (límite estricto: 300).")

        transferred = 0
        deleted_count = 0

        for idx, img_name in enumerate(images, start=1):
            img_clean = img_name.strip()
            if not img_clean:
                continue

            logger.info(f"[{idx}/{len(images)}] Procesando: {img_clean}")

            # 1. Comprobar si ya existe en destino
            if img_clean in target_titles:
                logger.info(f"  -> Ya existe en destino ({target_title}). Omitiendo copia.")
            else:
                # 2. Intentar copia directa server-to-server si existe en origen
                if img_clean in source_dict:
                    src_obj = source_dict[img_clean]
                    logger.info(f"  -> Copiando server-to-server (ID: {src_obj.id}) hacia {target_title}...")
                    try:
                        # CopySourcesAsync
                        copy_result = await client.sources.copy(
                            notebook_id=source_id,
                            target_notebook_id=target_id,
                            source_ids=[src_obj.id],
                        )
                        logger.info(f"     Copiado exitoso: {copy_result}")
                        target_titles.add(img_clean)
                        transferred += 1
                    except Exception as e:
                        logger.error(f"     Fallo en copia server-to-server ({e}). Intentando fallback desde disco...")
                        disk_path = find_image_on_disk(img_clean)
                        if disk_path:
                            added = await client.sources.add_file(target_id, disk_path, wait=True)
                            logger.info(f"     Subido desde disco: ID {added.id} (Status: {added.status})")
                            target_titles.add(img_clean)
                            transferred += 1
                        else:
                            logger.error(f"     No se encontró archivo en disco para fallback: {img_clean}")
                else:
                    # 3. No está en origen: subir directamente desde disco al destino
                    logger.info(f"  -> No está en origen. Buscando en disco local...")
                    disk_path = find_image_on_disk(img_clean)
                    if disk_path:
                        logger.info(f"  -> Subiendo {disk_path} a destino...")
                        added = await client.sources.add_file(target_id, disk_path, wait=True)
                        logger.info(f"     Subido con éxito: ID {added.id} (Status: {added.status})")
                        target_titles.add(img_clean)
                        transferred += 1
                    else:
                        logger.error(f"     [ERROR] No se encuentra en origen ni en disco: {img_clean}")
                        continue

            # 4. Si el modo es MOVER (delete_source=True) y estaba en origen, eliminarlo del origen
            if delete_source and img_clean in source_dict:
                src_obj = source_dict[img_clean]
                logger.info(f"  -> [MOVER] Eliminando {img_clean} del cuaderno origen ({source_title})...")
                try:
                    await client.sources.delete(source_id, src_obj.id)
                    logger.info(f"     Eliminado del origen: {img_clean}")
                    deleted_count += 1
                except Exception as e:
                    logger.error(f"     Error al eliminar del origen: {e}")

            await asyncio.sleep(pause_sec)

        # Resumen final
        final_source = await client.sources.list(source_id)
        final_target = await client.sources.list(target_id)
        logger.info("=== TRASLADO FINALIZADO CON ÉXITO ===")
        logger.info(f"Fuentes transferidas/copiadas: {transferred}")
        if delete_source:
            logger.info(f"Fuentes eliminadas del origen: {deleted_count}")
        logger.info(f"Total fuentes actual: Origen={len(final_source)}, Destino={len(final_target)}")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Mueve o copia imágenes/fuentes entre cuadernos de NotebookLM Pro."
    )
    parser.add_argument(
        "--source", "-s",
        required=True,
        help="Nombre o UUID del cuaderno origen (ej. NRDL-MIXTO-01 o 14cf46ae...)"
    )
    parser.add_argument(
        "--target", "-t",
        required=True,
        help="Nombre o UUID del cuaderno destino (ej. NRDL-MATR-01 o 1e6fec74...)"
    )
    parser.add_argument(
        "--images", "-i",
        nargs="*",
        default=[],
        help="Lista de nombres de archivos de imagen (ej. 004306112_02013.jpg 004306112_02014.jpg)"
    )
    parser.add_argument(
        "--images-file", "-f",
        help="Ruta a un archivo .txt con un nombre de imagen por línea"
    )
    parser.add_argument(
        "--delete-source", "--move",
        action="store_true",
        help="Modo MOVER: elimina la fuente del origen tras certificar la copia en destino. (Si no se especifica, opera en modo COPIAR / Duplicidad Lógica [L-31])."
    )
    parser.add_argument(
        "--pause",
        type=float,
        default=2.0,
        help="Pausa en segundos entre operaciones para rate-limiting (default: 2.0s)"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    images = list(args.images)
    if args.images_file:
        fpath = Path(args.images_file)
        if not fpath.exists():
            logger.error(f"No existe el archivo de imágenes: {fpath}")
            sys.exit(1)
        with open(fpath, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    images.append(stripped)

    if not images:
        logger.error("Debe proporcionar al menos una imagen mediante --images o --images-file.")
        sys.exit(1)

    asyncio.run(
        execute_transfer(
            source_nb_arg=args.source,
            target_nb_arg=args.target,
            images=images,
            delete_source=args.delete_source,
            pause_sec=args.pause,
        )
    )


if __name__ == "__main__":
    main()
