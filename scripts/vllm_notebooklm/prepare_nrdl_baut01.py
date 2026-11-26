"""
Script de Puesta a Punto y Preparación de NRDL-BAUT-01
Inyecta las 5 fuentes maestras (.md) y configura ChatSettings con el System Prompt oficial.
"""

import asyncio
from pathlib import Path
from notebooklm import NotebookLMClient
from notebooklm.types import ChatGoal, ChatResponseLength

NOTEBOOK_ID = "a187936c-55f4-4319-87db-6bf4e21e8613"

SYSTEM_PROMPT = (
    "Eres un Catedrático de Paleografía y Diplomática Hispánica especializado en "
    "archivos parroquiales y catastrales de los siglos XVI al XIX (letra procesal encadenada, "
    "cortesana y humanística).\n"
    "REGLAS INQUEBRANTABLES:\n"
    "1. INSPECCIÓN VISUAL MULTIMODAL [L-03]: No confíes a ciegas en el índice OCR preliminar. "
    "Examina visualmente los píxeles de cada imagen adjunta línea por línea, separando la tinta "
    "oscura de la cara frontal del traspaso invertido del reverso (bleed-through).\n"
    "2. CERO RESÚMENES Y CERO OMISIONES [L-03]: Cuando se te pida transcribir una imagen, "
    "transcribe absolutamente todas las partidas presentes de arriba abajo sin omitir ninguna "
    "ni añadir introducciones retóricas.\n"
    "3. PROHIBICIÓN DE SESGO Y CONTAMINACIÓN [L-01, L-02]: Lee exclusivamente lo que está trazado "
    "físicamente en el papel. Usa el Diccionario Onomástico (Fuente 01) y las Autoridades "
    "Paleográficas (Fuente 03) solo para desambiguar ligaduras cursivas compatibles con el trazo "
    "visual; jamás inventes ni traslades datos de otra página.\n"
    "4. GESTIÓN DE ROTURAS Y DUDAS [L-07]: Marca el papel roto como [ROTO], la tinta perdida como "
    "[ILEGIBLE] y cualquier lectura dudosa como [DUDOSO: opción_A / opción_B]."
)

TEXT_SOURCES = [
    ("00_INSTRUCCIONES_PALEOGRAFICAS_V2", Path("00_INSTRUCCIONES_PALEOGRAFICAS_V2.md")),
    ("01_DICCIONARIO_ANCLAJE_NAVARREDONDILLA", Path("01_DICCIONARIO_ANCLAJE_NAVARREDONDILLA.md")),
    ("02_INSTRUCCIONES_CRONOLOGICAS_NAVARREDONDILLA_1594_1695", Path("02_INSTRUCCIONES_CRONOLOGICAS_NAVARREDONDILLA_1594_1695.md")),
    ("03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE", Path("03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md")),
    ("04_JURISDICCIONES_Y_DEPENDENCIAS_PARROQUIALES", Path("04_JURISDICCIONES_Y_DEPENDENCIAS_PARROQUIALES.md")),
]


async def main():
    print(f"=== PUESTA A PUNTO DE NRDL-BAUT-01 ({NOTEBOOK_ID}) ===")
    
    async with NotebookLMClient.from_storage() as client:
        # 1. Configurar ChatSettings
        print("[1/3] Configurando ChatSettings (System Prompt + response_length=LONGER)...")
        await client.chat.configure(
            notebook_id=NOTEBOOK_ID,
            goal=ChatGoal.CUSTOM,
            response_length=ChatResponseLength.LONGER,
            custom_prompt=SYSTEM_PROMPT,
        )
        print("  -> ChatSettings configurado correctamente.")
        
        # 2. Verificar fuentes existentes para evitar duplicados
        existing_sources = await client.sources.list(NOTEBOOK_ID)
        existing_titles = {s.title: s for s in existing_sources}
        print(f"[2/3] Fuentes actuales en cuaderno: {len(existing_sources)}")
        
        # 3. Inyectar las 5 fuentes .md
        for title, path in TEXT_SOURCES:
            if title in existing_titles:
                print(f"  -> Fuente '{title}' ya existe en el cuaderno. Saltando.")
                continue
            
            if not path.exists():
                print(f"  [ERROR] No se encuentra el archivo local: {path}")
                continue
            
            content = path.read_text(encoding="utf-8")
            print(f"  -> Subiendo fuente '{title}' ({len(content)} caracteres)...")
            source = await client.sources.add_text(
                notebook_id=NOTEBOOK_ID,
                title=title,
                content=content,
                wait=True,
                wait_timeout=120.0,
            )
            print(f"     Listo: ID {source.id} (status: {source.status})")
            await asyncio.sleep(2.0)
        
        # 4. Verificación final
        final_sources = await client.sources.list(NOTEBOOK_ID)
        print(f"[3/3] Total fuentes final en NRDL-BAUT-01: {len(final_sources)}")
        
        text_count = sum(1 for s in final_sources if s.title.startswith("0") and not s.title.endswith(".jpg"))
        jpg_count = sum(1 for s in final_sources if s.title.endswith(".jpg"))
        print(f"  - Imágenes JPG: {jpg_count} (esperadas 245)")
        print(f"  - Fuentes Maestras de Texto: {text_count} (esperadas 5)")
        
        settings = await client.chat.get_settings(NOTEBOOK_ID)
        print(f"  - Configuración Chat verificada: goal={settings.goal}, length={settings.response_length}")
        print("=== PUESTA A PUNTO COMPLETADA CON ÉXITO ===")


if __name__ == "__main__":
    asyncio.run(main())
