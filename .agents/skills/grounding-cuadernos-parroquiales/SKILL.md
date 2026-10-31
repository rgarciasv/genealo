---
name: grounding-cuadernos-parroquiales
description: >-
  Puesta a punto y preparación ecdótica de cascarones vacíos de cuadernos parroquiales
  en NotebookLM Pro. Automatiza la inyección de fuentes maestras (00 ecdótica, 01 léxico
  y toponimia menor, 03 autoridades paleográficas, 04 historia canónica), la redacción
  e inyección de la fuente específica 02_INSTRUCCIONES_CRONOLOGICAS con mapas de dislocaciones
  y la configuración de ChatSettings (goal=CUSTOM, response_length=LONGER, prompt maestro
  del sistema).
---

# Grounding y Puesta a Punto de Cuadernos Parroquiales

Esta skill describe el protocolo para transformar un "cascarón vacío con imágenes" en un entorno de transcripción paleográfica de alta precisión grounded en fuentes ecdóticas maestras.

---

## 1. Las 5 Fuentes Maestras de Grounding

Ningún cuaderno parroquial debe ponerse en producción sin contar con su batería de fuentes `.md` de referencia:

| # | Archivo Fuente | Función Ecdótica | Ámbito |
| :-: | :--- | :--- | :--- |
| **`00`** | `00_INSTRUCCIONES_PALEOGRAFICAS_V2.md` | Normas de transcripción literal, marcado de lagunas (`[ROTO]`, `[ILEGIBLE]`), marginalia y esquema JSON. | Universal |
| **`01`** | `01_DICCIONARIO_ANCLAJE_<LOCALIDAD>.md` | Léxico pasivo de mundo cerrado: toponimia menor (pagos, arroyos, cerros), nombres y fórmulas notariales. | Local |
| **`02`** | `02_INSTRUCCIONES_CRONOLOGICAS_<LOCALIDAD>_<SERIE>.md` | Mapa forense de dislocaciones, saltos de folio, tramos mixtos y fechas reales. | Cuaderno |
| **`03`** | `03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE.md` | Fichas de escribanos, párrocos, evolución del ductus caligráfico y tics abreviativos (`[L-22]`). | Comarcal |
| **`04`** | `04_JURISDICCIONES_Y_DEPENDENCIAS_PARROQUIALES.md` | Historia institucional, régimen de anejos, diezmos y dependencias canónicas (`[L-24]`). | Comarcal |

---

## 2. Redacción de la Guía Específica `02_INSTRUCCIONES_CRONOLOGICAS`

Antes de inyectar la fuente `02`, el agente debe auditar la secuencia de fotogramas del cuaderno:
1. Identificar la portada, licencias y placas técnicas de FamilySearch.
2. Mapear cada cambio de mano de párroco o escribano.
3. Señalizar folios traspuestos o encuadernados fuera de orden temporal (ej. años posteriores cosidos al frente).
4. Localizar los autos de Santa Visita Pastoral (`[L-32]`) y padrones de confirmaciones.
5. Indicar las imágenes híbridas (`[L-31]`) especificando qué lado corresponde a este cuaderno.

---

## 3. Configuración de `ChatSettings`

Para que el modelo de IA responda con el tono archivístico adecuado, se debe configurar el chat del cuaderno utilizando la API de NotebookLM:

```python
import asyncio
from notebooklm import NotebookLMClient
from notebooklm.types import ChatSettings, ChatGoal, ChatResponseLength

SYSTEM_PROMPT = """Eres el Motor de Transcripción Paleográfica del Proyecto de I+D Genealógico Alto Alberche.
Tu cometido exclusivo es la lectura diplomática rigurosa de las partidas sacramentales del cuaderno.
NORMAS ESTRICTAS:
1. Fidelidad absoluta al texto original manuscrito. No modernices grafías arcaicas (conserva ç, x, b/v, ss).
2. Prohibido alucinar nombres, apellidos o fechas ausentes del manuscrito.
3. Si un texto está dañado o cortado, usa [ROTO] o [ILEGIBLE].
4. En folios híbridos [L-31], transcribe únicamente la plana asignada a esta serie sacramental.
5. Devuelve siempre las partidas estructuradas en JSON Schema estricto."""

async def configure_notebook(notebook_id):
    async with NotebookLMClient.from_storage() as client:
        await client.chat.configure(
            notebook_id=notebook_id,
            settings=ChatSettings(
                goal=ChatGoal.CUSTOM,
                response_length=ChatResponseLength.LONGER,
                custom_prompt=SYSTEM_PROMPT,
            )
        )
```

---

## 4. Script de Referencia y Verificación

* **Script:** `scripts/prepare_nrdl_baut01.py` implementa la subida de los 5 archivos `.md` y la configuración de `ChatSettings`.
* **Verificación:** Ejecutar `scripts/verify_nrdl_parroquial_sources.py` para constatar que el cuaderno contiene el número de fotogramas originales más las fuentes Markdown añadidas.
