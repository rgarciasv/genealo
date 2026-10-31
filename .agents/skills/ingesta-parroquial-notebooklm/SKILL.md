---
name: ingesta-parroquial-notebooklm
description: >-
  Automatiza la ingesta masiva y desatendida de rollos de microfilm parroquiales
  (FamilySearch DGS) en Google NotebookLM Pro. Aplica particionado de series
  canónicas (<=300 fuentes por cuaderno), checkpointing atómico para reanudación
  idempotente sin duplicados, rate-limiting anti-429 (pausas de 2.5s y backoff exponencial),
  monitorización de procesos y renovación desatendida de tokens mediante perfil
  persistente de Chromium [Regla L-21].
---

# Ingesta Parroquial Desatendida en NotebookLM Pro

Esta skill proporciona el protocolo técnico, los scripts y las directivas de control de fallos para subir de forma desatendida y masiva miles de fotogramas de microfilms históricos de FamilySearch a **Google NotebookLM Pro**.

---

## 1. Reglas Operativas Fundamentales

1. **Límite Estricto por Cuaderno (`<= 300` fuentes):**
   * NotebookLM impone un límite estricto de **300 fuentes por cuaderno**.
   * Cualquier libro histórico que supere ~200 imágenes debe dividirse en tomos canónicos o volúmenes cronológicos (ej. `JMOL-BAUT-01`, `JMOL-BAUT-02`).
   * Mantener siempre margen (idealmente 200–280 imágenes) para permitir la inyección posterior de las 5 fuentes maestras de grounding (`00..04`).

2. **Checkpointing Atómico Bidireccional (`ingest_checkpoint_<localidad>.json`):**
   * Cada fotograma subido con éxito debe persistirse **inmediatamente** en el archivo JSON de checkpoint con:
     `{ "id_imagen": "004298570_00001.jpg", "source_id": "uuid-google-cloud", "notebook_id": "uuid-cuaderno" }`.
   * En caso de parada forzada, cuelgue de red o reinicio del script, el pipeline lee el checkpoint y **omite instantáneamente** las fuentes ya cargadas, garantizando idempotencia total con cero duplicados.

3. **Rate Limiting y Prevención de 429:**
   * Pausa obligatoria entre subidas consecutivas: **2.5 segundos** (`--pause 2.5`).
   * En caso de error transitorio (`RateLimitError`, `RPCError`, `httpx.HTTPError`), aplicar **Backoff Exponencial**:
     * Intento 1: reintento en 5.0s.
     * Intento 2: reintento en 10.0s.
     * Intento 3: reintento en 20.0s.
     * Intento 4: reintento en 40.0s.
     * Intento 5: reintento en 80.0s.

4. **Escudo de Cuadernos Protegidos (`shield_check`):**
   * Antes de iniciar cualquier subida, el script debe verificar la integridad de los cuadernos ya certificados (ej. el cuaderno piloto de Navarredondilla `7967d647` o los 4 cuadernos de Ensenada Legos). Si alguno ha sido alterado, el proceso debe abortar de inmediato.

5. **Renovación Desatendida de Tokens (`[L-21]`):**
   * Las cookies de sesión web de Google rotan aproximadamente cada 60 minutos.
   * Cuando se capture una excepción `AuthError` o `unauthenticated`, no requerir intervención manual:
     Ejecutar fuera del sandbox:
     ```powershell
     .\venv\Scripts\notebooklm.exe login
     ```
     El navegador Chromium se abrirá conectado al perfil persistente (`C:\Users\<user>\.notebooklm\profiles\default\browser_profile`), capturará automáticamente las nuevas cookies (`storage_state.json`) en 5 segundos y cerrará. A continuación se reanuda el script.

---

## 2. Estructura del Script de Ingesta

El script de ingesta debe seguir el patrón consolidado en `scripts/ingest_sanjuan_parroquial.py`:

```python
import asyncio
from notebooklm import NotebookLMClient
from notebooklm.exceptions import RateLimitError, RPCError, AuthError

async def upload_single_image(client, notebook_id, img_path, img_title, pause=2.5):
    for attempt in range(1, 6):
        try:
            source = await client.sources.add_file(
                notebook_id=notebook_id,
                file_path=str(img_path)
            )
            await asyncio.sleep(pause)
            return source.id
        except (RateLimitError, RPCError) as e:
            delay = 5.0 * (2 ** (attempt - 1))
            await asyncio.sleep(delay)
        except AuthError as e:
            # Señal para el supervisor [L-21]
            raise
```

---

## 3. Prevención de Duplicados y Concurrencia (Singleton)

> [!WARNING]
> **Prohibición de Procesos Concurrentes:** Nunca deben correr dos instancias del script de ingesta simultáneamente sobre el mismo checkpoint. Si se utiliza un supervisor (`supervise_m1.py`), debe verificar mediante el PID del sistema operativo que no existe otro worker activo antes de lanzar un nuevo proceso.

Si por un reinicio abrupto se llegaran a duplicar fuentes en un cuaderno remoto:
* Ejecutar el deduplicador atómico (`scripts/dedup_jmol_parroquial.py`).
* El script lista todas las fuentes del cuaderno, agrupa por título (`004298571_XXXXX.jpg`), conserva el primer `source_id` y ejecuta `client.sources.delete(duplicate_id)` para purgar el exceso y restaurar la cuota.

---

## 4. Checklist para Nuevas Localidades (ej. Navalmoral `NMRL`)

1. Catalogar los fotogramas en `catalogo_corpus.json` asignando un `cuaderno_asignado_id` canónico a cada bloque.
2. Calcular el número de fuentes por cuaderno (verificar que ninguna supere las 280 imágenes).
3. Configurar el diccionario de cuadernos destino (`PARROQUIAL_TARGETS`).
4. Lanzar la ingesta con supervisión en segundo plano:
   ```powershell
   .\venv\Scripts\python.exe scripts/ingest_<localidad>_parroquial.py --pause 2.5
   ```
5. Al concluir, ejecutar la verificación E2E independiente.
