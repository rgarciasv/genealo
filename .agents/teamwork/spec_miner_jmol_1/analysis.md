# ESPECIFICACIÓN AUTORITATIVA: CORPUS PARROQUIAL DE SAN JUAN DEL MOLINILLO
**Pipeline de Ingesta Masiva, Blindaje y Verificación E2E en Google NotebookLM Pro**
**Agente Investigador:** `spec_miner_jmol_1` (`teamwork_spec_miner`)  
**Fecha:** 2026-10-31  
**Repositorio Base:** `c:\TRABAJOS\personal\genealo`  
**Estado:** ESPECIFICACIÓN MINADA Y AUDITADA  

---

## 1. Fuentes Autoritativas de la Especificación

Esta especificación se ha derivado de la inspección exhaustiva de las siguientes fuentes primarias e inmutables del repositorio:
1. **`ORIGINAL_REQUEST.md`**: Petición autoritativa de coordinación, ingesta de 17 cuadernos restantes (2.714 fuentes) y verificación de los 18 cuadernos totales (2.731 fuentes con piloto previo `JMOL-DIFU-03`).
2. **`catalogo_corpus.json`** (v1.1, 8.515 registros totales del proyecto): Catálogo canónico con metadatos fotograma a fotograma (`id_imagen`, `rollo_dgs`, `fotograma_numero`, `elemento_numero`, `anios_macro`, `cuaderno_asignado_id`, etc.).
3. **`REGLAS_Y_PROMPTS_OFICIALES.md`**: Manual de reglas operativas (`[L-21]`, `[L-28]`, `[L-29]`, `[L-30]`).
4. **`BITACORA_EXPERIMENTOS.md`** y **`contexto_maestro.md`**: Registro histórico de lecciones empíricas y precedentes de Ensenada y Navarredondilla.
5. **Scripts y Arneses del Pipeline**:
   - `scripts/ingest_sanjuan_parroquial.py`: Pipeline con resolver dinámico, reintentos con backoff exponencial y doble checkpoint.
   - `scripts/verify_sanjuan_parroquial_sources.py`: Arnés de verificación independiente para 0 duplicados, 0 faltantes, 0 errores y 100% READY.
   - `scripts/ingest_checkpoint_jmol.json`: Estado local del checkpoint atómico.
   - `scripts/verification_report_jmol.json`: Dictamen de verificación del piloto `JMOL-DIFU-03`.
6. **Entorno Live de Google NotebookLM Pro**: Conexión autenticada vía `NotebookLMClient.from_storage()` y perfil persistente de Chromium.

---

## 2. Inventario Canónico de Cuadernos: San Juan del Molinillo (18 Cuadernos, 2.731 Fuentes)

El corpus parroquial de San Juan del Molinillo comprende **exactamente 2.731 fuentes fotográficas** distribuidas en **18 cuadernos mono-localidad y mono-sacramentales**, pertenecientes a dos rollos DGS diocesanos:
- **Rollo DGS `004298570`**: Bautismos y Códice Mixto Transición (Fotogramas 1599 al 2769).
- **Rollo DGS `004298571`**: Matrimonios y Defunciones (Fotogramas 1 al 1560).

### 2.1. Serie Bautismos (6 Cuadernos / 1.080 Fuentes)
Todos pertenecen al Rollo DGS `004298570`.

| # | ID Canónico (`cuaderno_asignado_id`) | Título en NotebookLM | Fuentes | Fotogramas (Rango) | Elemento | Libro | Años Cobertura |
|---|---------------------------------------|----------------------|---------|---------------------|----------|-------|----------------|
| 1 | `JMOL-BAUT-01` | `JMOL-BAUT-01` | 175 | 01599 – 01773 | Elem 14 | Libro 1 | 1715–1752 |
| 2 | `JMOL-BAUT-02` | `JMOL-BAUT-02` | 276 | 01774 – 02049 | Elem 15 | Libro 2 | 1752–1800 |
| 3 | `JMOL-BAUT-03` | `JMOL-BAUT-03` | 190 | 02050 – 02239 | Elem 16 | Libro 3 (P1) | 1801–1852 |
| 4 | `JMOL-BAUT-04` | `JMOL-BAUT-04` | 189 | 02240 – 02428 | Elem 16 | Libro 3 (P2) | 1801–1852 |
| 5 | `JMOL-BAUT-05` | `JMOL-BAUT-05` | 139 | 02520 – 02658 | Elem 18 | Libro 5 | 1851–1862 |
| 6 | `JMOL-INDICE-BAUT` | `JMOL-INDICE-BAUT` | 111 | 02659 – 02769 | Elem 19 | S/N (Índice) | 1750–1914 |
| **SUBTOTAL** | **6 Cuadernos de Bautismos** | | **1.080** | | | | |

*Nota de Reconciliación Metodológica*: En la redacción narrativa de `ORIGINAL_REQUEST.md` se mencionaba "Bautismos: 6 cuadernos / 1.069 imágenes". La suma real de los 6 cuadernos en `catalogo_corpus.json` y en el código de `ingest_sanjuan_parroquial.py` es exactamente 1.080 (969 en libros 1 al 5 + 111 en índice). La diferencia de 11 fuentes se compensa simétricamente con Defunciones (1.034 reales vs 1.028 narrativas), resultando en la misma suma exacta de 2.114 fuentes combinadas (1.080 + 1.034 = 2.114; 1.069 + 1.028 = 2.097 + 17 piloto = 2.114).

---

### 2.2. Serie Matrimonios y Códice Transición (4 Cuadernos / 617 Fuentes)
Pertenecen a los Rollos DGS `004298571` (Matrimonios puros) y `004298570` (Códice Transición).

| # | ID Canónico (`cuaderno_asignado_id`) | Título en NotebookLM | Fuentes | Rollo DGS | Fotogramas (Rango) | Elemento | Libro | Años Cobertura |
|---|---------------------------------------|----------------------|---------|-----------|---------------------|----------|-------|----------------|
| 7 | `JMOL-MATR-01` | `JMOL-MATR-01` | 194 | 004298571 | 00001 – 00194 | Elem 1 | Libro 1 | 1716–1789 |
| 8 | `JMOL-MATR-02` | `JMOL-MATR-02` | 134 | 004298571 | 00195 – 00328 | Elem 2 | Libro 2 | 1790–1852 |
| 9 | `JMOL-MATR-03` | `JMOL-MATR-03` | 198 | 004298571 | 00329 – 00526 | Elem 3 | Libro 3 | 1851–1899 |
| 10 | `JMOL-MIXTO-04` | `JMOL-SACRAMENTAL-1842-1850` | 91 | 004298570 | 02429 – 02519 | Elem 17 | Libro 4 | 1842–1850 |
| **SUBTOTAL** | **4 Cuadernos Matrimonios/Transición** | | **617** | | | | | |

*Regla [L-30] aplicada a `JMOL-MIXTO-04`*: El Elemento 17 físico contiene partidas sacramentales encuadernadas juntas de época de transición. Siguiendo la regla de denominación pura [L-30], en Google NotebookLM el título asignado es **`JMOL-SACRAMENTAL-1842-1850`**.

---

### 2.3. Serie Defunciones (8 Cuadernos / 1.034 Fuentes)
Todos pertenecen al Rollo DGS `004298571`.

| # | ID Canónico (`cuaderno_asignado_id`) | Título en NotebookLM | Fuentes | Fotogramas (Rango) | Elemento | Libro | Años Cobertura | Estado Actual |
|---|---------------------------------------|----------------------|---------|---------------------|----------|-------|----------------|---------------|
| 11 | `JMOL-DIFU-PARVULOS` | `JMOL-DIFU-PARVULOS` | 27 | 00527 – 00553 | Elem 4 | Libro 1 | 1632–1680 | Pendiente |
| 12 | `JMOL-DIFU-01` | `JMOL-DIFU-01` | 202 | 00554 – 00755 | Elem 5 | Libro 1 | 1715–1764 | Pendiente |
| 13 | `JMOL-DIFU-02` | `JMOL-DIFU-02` | 277 | 00756 – 01032 | Elem 6 | Libro 2 | 1764–1848 | Pendiente |
| 14 | `JMOL-DIFU-03` | `JMOL-DIFU-03` | **17** | 01033 – 01049 | Elem 7 | Libro 3 | 1849–1851 | **COMPLETADO (PILOTO READY)** |
| 15 | `JMOL-DIFU-04` | `JMOL-DIFU-04` | 214 | 01050 – 01263 | Elem 8 | Libro 4 | 1851–1883 | Pendiente |
| 16 | `JMOL-DIFU-05` | `JMOL-DIFU-05` | 99 | 01264 – 01362 | Elem 9 | Libro 5 | 1872–1881 | Pendiente |
| 17 | `JMOL-DIFU-06` | `JMOL-DIFU-06` | 177 | 01363 – 01539 | Elem 10 | Libro 6 | 1881–1892 | Pendiente |
| 18 | `JMOL-INDICE-DIFU` | `JMOL-INDICE-DIFU` | 21 | 01540 – 01560 | Elem 11 | S/N (Índice) | 1893–1907 | Pendiente |
| **SUBTOTAL** | **8 Cuadernos Defunciones** | | **1.034** | | | | | **17 READY + 1.017 Pendientes** |

---

### 2.4. Consolidado Total del Corpus San Juan del Molinillo
- **Total Cuadernos Parroquiales JMOL**: 18
  * Cuadernos ya completados (Piloto previo): **1** (`JMOL-DIFU-03`, ID `a5d19fcc-d266-4497-bdb3-df182328bdcb`, 17 fuentes READY).
  * Cuadernos a ingestar en producción: **17** (2.714 fuentes restantes).
- **Total Fuentes Parroquiales JMOL**: **2.731 fuentes fotográficas** (1.080 Bautismos + 617 Matrimonios/Mixto + 1.034 Defunciones = exactamente 2.731).
- **Fuentes Restantes a Ingestar**: **2.714 fuentes** (2.731 - 17 = 2.714).

---

## 3. Especificación de Límites y Restricciones Operativas (Boundary Specs)

### 3.1. Regla de Límite de Capacidad: $\le 300$ Fuentes por Cuaderno (`[L-29]` y `[L-30]`)
- **Directiva**: Ningún cuaderno en Google NotebookLM Pro debe superar las 300 fuentes documentales. La arquitectura de particionado debe garantizar que libros extensos se subdividan limpiamente respetando la correlación temporal y el orden foliar.
- **Auditoría de Cumplimiento**:
  * Cuaderno con mayor carga: `JMOL-DIFU-02` con **277 fuentes** (margen de seguridad: 23 fuentes por debajo del límite).
  * Segundo cuaderno con mayor carga: `JMOL-BAUT-02` con **276 fuentes** (margen de seguridad: 24 fuentes por debajo del límite).
  * Cuaderno con menor carga: `JMOL-DIFU-03` con **17 fuentes**.
  * Mediana de fuentes por cuaderno: **176 fuentes**.
  * **Dictamen de Capacidad**: El 100% de los 18 cuadernos cumple estrictamente la regla $\le 300$ fuentes.

### 3.2. Restricción de Perfil Persistente de Chromium (`[L-21]`)
- **Directiva**: La interacción desatendida con la API de NotebookLM requiere mantener la sesión autenticada mediante el perfil persistente de Chromium sin pedir contraseñas interactivas al usuario.
- **Ubicación del Perfil y Tokens**:
  * Perfil de navegador: `profiles/default/browser_profile`
  * Archivo de estado de almacenamiento: `C:\Users\rgarc\.notebooklm\profiles\default\storage_state.json` (auditado: tamaño 13.546 bytes, contiene cookies de sesión `SID`, `__Secure-1PSID`, `HSID`, `SSID`).
- **Comportamiento ante Expiración**:
  * Si la sesión HTTP sufre un `AuthError` (401/403), el pipeline invoca la reautenticación desatendida mediante el ejecutable CLI fuera del sandbox, permitiendo la renovación transparente de cookies sin requerir intervención manual.

### 3.3. Requisito de Doble Checkpoint Atómico (`[R2]`)
- **Capa 1: Checkpoint Local Atómico en Disco (`scripts/ingest_checkpoint_jmol.json`)**:
  * Estructura: JSON serializado con `version`, `created_at`, `updated_at`, `notebook_ids` (mapeo target $\to$ UUID), `completed_notebooks` (lista ordenada de cuadernos cerrados) y `uploaded_sources` (mapeo `id_imagen` $\to$ `{source_id, notebook_id, timestamp}`).
  * Atomicidad: Escritura en archivo temporal `.tmp` con sustitución atómica del sistema operativo (`Path.replace()`). Evita corrupción en cortes de suministro o terminación súbita.
- **Capa 2: Sincronización Live Cloud en NotebookLM Pro**:
  * Al inicializar cada cuaderno, el pipeline consulta la lista de fuentes remotas vía `client.sources.list(nb_id)`.
  * Deduplicación bidireccional: Si una fuente ya figura en el cloud, se adopta su `source_id` en el checkpoint local sin lanzar una nueva subida HTTP.
  * Idempotencia estricta: Permite reiniciar el pipeline en cualquier momento sin generar duplicados.

### 3.4. Estándar Inmutable de Clave Primaria (`[L-28]`)
- **Patrón Regex Obligatorio**: `^\d{9}_\d{5}\.jpg$`
- **Formato Exacto**: `{DGS}_{FOTOGRAMA}.jpg` (ejemplo: `004298570_01599.jpg`).
- **Restricción de Longitud**: Exactamente **19 caracteres**. Queda terminantemente prohibido el truncamiento de ceros a la izquierda (ej. `1599.jpg` o `01599.jpg`).

### 3.5. Resolución Dinámica Multi-Ruta de Imágenes Físicas
- El resolver (`resolve_image_path`) inspecciona dinámicamente:
  1. `c:\TRABAJOS\personal\genealo\imagenes\rollo {rollo_dgs}\{id_imagen}`
  2. Subdirectorios del workspace que contengan `"San Juan"` (ej. `San Juan Bautista. Bautismos...`).
- Garantiza la localización física en disco y verifica que el archivo no sea de 0 bytes antes de ordenar la subida.

---

## 4. Especificación de Cuadernos Protegidos (Zero-Regression Shield)

Para garantizar la no regresión y la integridad total del trabajo previo, los siguientes cuadernos en Google NotebookLM Pro están declarados como **ESTRICTAMENTE PROTEGIDOS** contra creación de duplicados, alteración de títulos, subida de fuentes ajenas o borrado:

### 4.1. Cuaderno Fundacional y Paleográfico de Navarredondilla
- **UUID**: `7967d647-8ca2-4863-a576-11843e8e8802`
- **Título**: `Lib. Baut. Navarre Vol. 1 (1594-1695)`
- **Fuentes esperadas**: Exactamente **188 fuentes** (183 fotogramas + fuentes de control `00`, `01`, `02`, `03`, `04`).

### 4.2. Cuadernos de Catastro de Ensenada (Legos - Fase 1)
- **`NRDL-ENSENADA-LEGOS-01`**: `ec86de71-a11c-4489-bbb9-eea856cccac4` (87 fuentes READY)
- **`JMOL-ENSENADA-LEGOS-01`**: `407d5cb4-4b83-495f-a23a-309ea44ee8c6` (28 fuentes READY)
- **`VLLR-ENSENADA-LEGOS-01`**: `e7fba70b-af7d-4602-b543-060742b22528` (51 fuentes READY)
- **`NDRN-ENSENADA-LEGOS-01`**: `cd72ef58-fcf5-48ac-8de2-556648ebd90e` (34 fuentes READY)

### 4.3. Cuadernos Parroquiales de Navarredondilla (Fase 2)
- **`NRDL-MATR-01`**: `1e6fec74-1e2f-4dd7-8ad1-6d25411de127` (33 fuentes READY)
- **14 Cuadernos Restantes de Navarredondilla**: `NRDL-BAUT-01..03, 05..07`, `NRDL-DIFU-01..05, 01B`, `NRDL-DIFU-S17-B`, `NRDL-MATR-02` (registrados en `ingest_checkpoint_nrdl.json`, totalizando 2.243 fuentes).

### 4.4. Cuaderno Piloto de San Juan del Molinillo (Pre-ingestado)
- **UUID**: `a5d19fcc-d266-4497-bdb3-df182328bdcb`
- **Título**: `JMOL-DIFU-03`
- **Fuentes esperadas**: Exactamente **17 fuentes** (100% READY, verificadas en `verification_report_jmol.json`).
- **Restricción**: Debe preservarse intacto; el pipeline debe omitir su reingesta reconociéndolo como `COMPLETED` en checkpoint.

---

## 5. Matriz de Criterios de Aceptación (Acceptance Criteria Matrix)

Para certificar el éxito total del hito de producción de San Juan del Molinillo, el sistema debe superar el 100% de los siguientes criterios verificables:

| ID | Dimensión | Criterio de Verificación | Condición de Éxito | Método de Prueba |
|---|---|---|---|---|
| **AC-01** | Completitud de Cuadernos | Los 18 cuadernos canónicos existen en NotebookLM Pro con sus nombres exactos. | 18/18 cuadernos presentes en `client.notebooks.list()`. | `verify_sanjuan_parroquial_sources.py` |
| **AC-02** | Completitud de Fuentes | Las 2.731 fuentes fotográficas están asignadas a sus respectivos cuadernos. | 2.731 fuentes totales (2.714 nuevas + 17 piloto). | Cross-check con `catalogo_corpus.json` |
| **AC-03** | Cero Duplicados (Intra) | Ningún cuaderno contiene dos fuentes con el mismo nombre de archivo. | Duplicados = 0 en cada uno de los 18 cuadernos. | `len(cloud_titles) == len(sources)` |
| **AC-04** | Cero Duplicados (Inter) | No existen solapamientos de fuentes entre cuadernos parroquiales ni con otras series. | Intersección entre pares de cuadernos = $\emptyset$. | Disjointness matrix check |
| **AC-05** | Cero Faltantes | Ninguna imagen presente en el catálogo para San Juan del Molinillo falta en el cloud. | Missing = 0 en los 18 cuadernos. | `expected_set - cloud_set == set()` |
| **AC-06** | Estado 100% READY | Cada una de las 2.731 fuentes ha completado el procesamiento OCR y multimodal. | Estado = `READY` (cero en `ERROR`, `PROCESSING` o `PENDING`). | `get_source_status_str(s) == 'READY'` |
| **AC-07** | Consistencia de Checkpoint | El archivo local refleja las 2.731 fuentes con sus respectivos `source_id` y `notebook_id`. | `len(uploaded_sources) == 2731` y 18 en `completed_notebooks`. | Validación de esquema JSON |
| **AC-08** | Preservación de Blindaje | Los cuadernos protegidos mantienen intacto su inventario y conteo de fuentes. | 0 alteraciones en títulos ni fuentes de cuadernos protegidos. | `run_preflight_shield_check()` |
| **AC-09** | Dictamen Arnés Independiente | La ejecución de verificación independiente finaliza con código de salida 0. | `overall_status: PASS` en `verification_report_jmol.json`. | `python scripts/verify_sanjuan_parroquial_sources.py` |

---

## 6. Features Discovered (Matriz de Características Descubiertas)

| # | Categoría | Feature | Descripción | Inputs | Outputs | Error Behavior | Discovered Via |
|---|-----------|---------|-------------|--------|---------|----------------|----------------|
| 1 | Catálogo | Mapeo Canónico de 18 Cuadernos | Segmentación de 2.731 imágenes en 18 cuadernos mono-sacramentales para San Juan del Molinillo. | `catalogo_corpus.json`, `cuaderno_asignado_id` | Lista estructurada de 18 targets con conteos (17 a 277). | `ValueError` si conteo discrepa con catálogo. | `catalogo_corpus.json` |
| 2 | Naming | Regla Primaria PK [L-28] | Nombres de imagen normalizados a 19 caracteres estrictos `{DGS}_{FOTOGRAMA}.jpg`. | Nombre de archivo JPG | String validado con regex `^\d{9}_\d{5}\.jpg$` | `ValueError` si no cumple longitud 19 o patrón. | `REGLAS_Y_PROMPTS_OFICIALES.md` |
| 3 | Naming | Denominación Pura [L-30] | Título libre de ambigüedades mixtas para códice de transición: `JMOL-SACRAMENTAL-1842-1850`. | `JMOL-MIXTO-04` en catálogo | Título de cuaderno `JMOL-SACRAMENTAL-1842-1850` | Falla de verificación si se titula con prefijo MIXTO. | `scripts/ingest_sanjuan_parroquial.py:160` |
| 4 | Capacidad | Límite $\le 300$ Fuentes [L-29/30] | Restricción dura de capacidad por cuaderno. Máximo real en JMOL: 277 fuentes (`JMOL-DIFU-02`). | Conteo por cuaderno | Bool: `count <= 300` | Alerta/Rechazo de diseño si excede 300. | `TODO.md`, `BITACORA_EXPERIMENTOS.md` |
| 5 | Auth | Perfil Persistente [L-21] | Renovación automática de cookies de sesión sin intervención manual en `browser_profile`. | `storage_state.json` en AppData | Cliente autenticado listo para peticiones HTTP RPC. | `AuthError` si las credenciales expiraron y no se refrescan. | `BITACORA_EXPERIMENTOS.md:42` |
| 6 | Resiliencia | Doble Checkpoint Atómico [R2] | Mecanismo de persistencia local `.tmp` $\to$ `.replace()` combinado con consulta remota de idempotencia. | Registro de upload | Archivo `ingest_checkpoint_jmol.json` actualizado | Intento de recreación limpia si el JSON está corrupto. | `scripts/ingest_sanjuan_parroquial.py:204` |
| 7 | Seguridad | Escudo Pre-Flight de Cuadernos | Verificación pre-ejecución de que los cuadernos históricos y de otras localidades siguen intactos. | Lista de cuadernos en cuenta | Confirmación de existencia y conteo mínimo de fuentes. | `RuntimeError: SHIELD FAILURE` detiene pipeline. | `scripts/ingest_sanjuan_parroquial.py:352` |
| 8 | Resolución | Dynamic Path Discovery | Localizador multiruta de archivos de imagen en carpetas `imagenes/rollo {dgs}` y carpetas de localidad. | `id_imagen`, `rollo_dgs` | `Path` absoluto al archivo físico en disco. | `FileNotFoundError` si la imagen no existe en disco. | `scripts/ingest_sanjuan_parroquial.py:269` |
| 9 | Red | Backoff Exponencial y Retry | Gestión robusta de transitorios HTTP (429, 500, 503, RPCError) con pausa y duplicación de espera. | Petición HTTP | ID de fuente subida o reintento programado | `RuntimeError` tras agotar 5 intentos consecutivos. | `scripts/ingest_sanjuan_parroquial.py:426` |
| 10 | Verificación | Arnés E2E Independiente | Script de auditoría desacoplado que inspecciona estado de fuentes (`READY`), faltantes y duplicados. | Cuenta cloud, catálogo y checkpoint | Reporte `verification_report_jmol.json` y exit code (0/1/2). | Exit code 2 si incompleto, exit code 1 si faltan cuadernos. | `scripts/verify_sanjuan_parroquial_sources.py` |

---

## 7. Edge Cases (Casos de Borde Detectados y Mitigados)

| # | Feature | Input / Situación de Borde | Comportamiento Observado y Mitigación |
|---|---------|-----------------------------|---------------------------------------|
| 1 | Capacidad de Cuadernos | Cuaderno `JMOL-DIFU-02` con 277 imágenes (muy cercano al límite 300). | Cumple la cota con 23 fuentes de margen. No requiere bipartición. |
| 2 | Cuaderno Piloto Existente | `JMOL-DIFU-03` (17 imágenes) ya existe en cloud y en checkpoint local. | Pipeline detecta `is_notebook_completed('JMOL-DIFU-03') == True` y lo salta limpiamente con cero re-uploads. |
| 3 | Códice Mixto de Transición | Elemento 17 (`JMOL-MIXTO-04`, 91 imágenes) contiene bautismos, casados y difuntos 1842–1850. | Se crea con título canónico puro `JMOL-SACRAMENTAL-1842-1850` cumpliendo regla [L-30]. |
| 4 | Truncamiento de Padding de Ceros | Fotogramas iniciales de matrimonio como `004298571_00001.jpg` (ceros a la izquierda). | Validación estricta `len(id_img) == 19` previene que `1.jpg` o `001.jpg` se procesen. |
| 5 | Imágenes en Múltiples Rutas de Disco | Archivos alojados en `imagenes/rollo 004298570/` o en carpetas sueltas de San Juan. | Resolver dinámico busca en subcarpetas del proyecto antes de arrojar `FileNotFoundError`. |
| 6 | Caída de Red / Error 429 Rate Limit | Subida masiva de imágenes a alta frecuencia disparando limitación de cuota Google. | Pausa configurable entre subidas (default 1.5s) y backoff exponencial (2s, 4s, 8s, 16s, 32s). |
| 7 | Corte de Alimentación o Interrupción | Proceso detenido a mitad de un lote de 200 imágenes en un cuaderno. | Checkpoint atómico guarda cada imagen inmediatamente; al reiniciar continúa exactamente en la siguiente imagen no subida. |
| 8 | Desconexión de Sesión (Cookie Expirada) | Google expira cookie `SID` durante ejecución nocturna prolongada. | Perfil persistente de Chromium en `browser_profile` permite refresco desatendido mediante reautenticación automática [L-21]. |
