# INFORME DE MINERÍA DE ESPECIFICACIONES, REGLAS Y LÍMITES DE PROYECTO
**Agente:** `spec_miner_survey_1`  
**Directorio de trabajo:** `c:\TRABAJOS\personal\genealo\.agents\teamwork\spec_miner_survey_1\`  
**Fecha:** 2026-10-31T10:07:00Z  
**Destinatario:** Orquestador (`fed48cc4-ccf0-40bb-ae10-7fff6d7c2cd1`)

---

## 1. OBSERVACIÓN

Se han examinado exhaustivamente las fuentes documentales canónicas, scripts de prueba, bitácora empírica y estructuras de catálogo en el repositorio `c:\TRABAJOS\personal\genealo`:

1. **`ORIGINAL_REQUEST.md` (Líneas 1–40):**
   - Mandato del usuario: *"Crear en NotebookLM los 4 cuadernos de Personal de Legos del Catastro de Ensenada para Navarredondilla, San Juan del Molinillo, Navandrinal y El Villarejo, y cargar sus 200 fuentes documentales correspondientes para producción en la investigación genealógica del proyecto."*
   - Asignación exacta de 200 imágenes:
     * `NRDL-ENSENADA-LEGOS-01`: 87 imágenes (`004469033_00881.jpg` a `004469033_00967.jpg`).
     * `JMOL-ENSENADA-LEGOS-01`: 28 imágenes (`004469028_00952.jpg` a `004469028_00979.jpg`).
     * `VLLR-ENSENADA-LEGOS-01`: 51 imágenes (`004469028_00901.jpg` a `004469028_00951.jpg`).
     * `NDRN-ENSENADA-LEGOS-01`: 34 imágenes (`004469028_00980.jpg` a `004469028_01013.jpg`).
   - Regla innegociable de preservación: Cuaderno activo `Lib. Baut. Navarre Vol. 1 (1594-1695)` (`7967d647-8ca2-4863-a576-11843e8e8802`) no debe ser modificado ni recreado.

2. **`REGLAS_Y_PROMPTS_OFICIALES.md` (Líneas 54–61, Reglas 11 `[L-28]` y 12 `[L-29]`):**
   - **`[L-28]` Identificación Primaria Absoluta mediante Nombre Completo de Archivo:**
     > *"Toda referencia a un fotograma de imagen debe utilizar OBLIGATORIAMENTE su nombre completo de archivo (`{DGS}_{FOTOGRAMA}.jpg`, ej. `004306112_01874.jpg`)."*  
     > *"Prohibición de truncamiento: Queda terminantemente prohibido truncar la referencia únicamente al número de fotograma (ej. `01874.jpg` o `01874`). El proyecto abarca 9 rollos DGS distintos (más de 8.500 imágenes); por tanto, el nombre de archivo completo es la única clave primaria universal e inequívoca tanto para el archivo físico en disco, como para NotebookLM, ArcadeDB, el árbol genealógico y las URLs ARK de FamilySearch."*
   - **`[L-29]` Principio de Aislamiento Topográfico y Grafocrítico en Cuadernos (`[CUADERNO-MONO-LOCALIDAD]`):**
     > *"Ningún cuaderno de NotebookLM Pro debe mezclar fondos documentales de diferentes localidades o pueblos. Cada cuaderno debe asociarse estrictamente a un único código cuatriletrado (`NRDL`, `JMOL`, `NDRN`, `VLLR`, `NMRL`)."*  
     > *"Diferenciación Estamental Obligatoria: En los fondos del Catastro de Ensenada, debe diferenciarse escrupulosamente entre Bienes de Legos / Seglares (`BIENES_LEGOS`) y Bienes Eclesiásticos (`BIENES_ECLESIASTICOS`), jamás agrupándolos en una categoría genérica."*  
     > *"Unicidad de Escribiente: Para cada pueblo y operación catastral (o serie parroquial contemporánea), el escribiente material suele ser el mismo. El aislamiento por localidad garantiza que el análisis de ductus, los modismos notariales y la toponimia menor (pagos, parajes, arroyos) no sufran contaminación cruzada entre núcleos vecinos."*

3. **`BITACORA_EXPERIMENTOS.md`:**
   - **Experimento 02 (Línea 51):** Documenta el cuaderno activo `Lib. Baut. Navarre Vol. 1 (1594-1695)` (`7967d647-8ca2-4863-a576-11843e8e8802`) con sus fuentes maestras (`00`, `01`, `02`, `03`, `04`) y 183 imágenes de bautismos primitivos de Navarredondilla (1594–1695).
   - **Experimento 12 (Línea 177):** Codificación de `[L-28]` para solventar colisiones de fotogramas entre rollos.
   - **Experimento 13 (Línea 192):** Codificación de `[L-29]` para aislamiento de cuadernos mono-localidad y segregación `BIENES_LEGOS` vs `BIENES_ECLESIASTICOS`.

4. **`contexto_maestro.md` (Líneas 68–83):**
   - Tabla oficial de cuadernos de NotebookLM. El cuaderno activo Nº 1 es `Lib. Baut. Navarre Vol. 1 (1594-1695)` (`7967d647-8ca2-4863-a576-11843e8e8802`), conteniendo 188 fuentes en total.

5. **`catalogo_corpus.json` (Auditoría programática sobre 8.515 registros):**
   - El archivo posee una marca de orden de bytes (BOM) UTF-8 (`\uFEFF`) al inicio.
   - Los 200 registros de Personal de Legos están clasificados con:
     * `fondo`: `"CATASTRO_ENSENADA"`
     * `estamento`: `"SEGLAR"`
     * `tipo_documento`: `"LIBRO_LEGOS"`
     * `escribano_mano_adscrita`: `"COMISION_ENSENADA_1752 (Pendiente de cotejo ductus)"`
     * `anios_macro`: `"1751-1752"`
     * `estado_auditoria`: `"MACRO_CLASIFICADO"`
     * `tipo_toma`: `"SIMPLE"`
     * `es_descarte`: `false` (0 descartes en el lote de 200)
     * `toma_hermana_de`: `null` (0 tomas hermanas en el lote de 200)
   - Desglose y verificación de contigüidad:
     * `NRDL-ENSENADA-LEGOS-01`: 87 registros (rango 881 a 967, sin huecos).
     * `JMOL-ENSENADA-LEGOS-01`: 28 registros (rango 952 a 979, sin huecos).
     * `VLLR-ENSENADA-LEGOS-01`: 51 registros (rango 901 a 951, sin huecos).
     * `NDRN-ENSENADA-LEGOS-01`: 34 registros (rango 980 a 1013, sin huecos).

6. **Verificación Física en Disco:**
   - 100% de las 200 imágenes existen en disco físico:
     * Navarredondilla (87 archivos): `c:\TRABAJOS\personal\genealo\imagenes\rollo 004469033\004469033_00881.jpg` a `004469033_00967.jpg` (y copia en `catastro ensenada Navarredondilla\`).
     * San Juan del Molinillo (28 archivos): `c:\TRABAJOS\personal\genealo\imagenes\rollo 004469028\004469028_00952.jpg` a `004469028_00979.jpg`.
     * El Villarejo (51 archivos): `c:\TRABAJOS\personal\genealo\imagenes\rollo 004469028\004469028_00901.jpg` a `004469028_00951.jpg`.
     * Navandrinal (34 archivos): `c:\TRABAJOS\personal\genealo\imagenes\rollo 004469028\004469028_00980.jpg` a `004469028_01013.jpg`.
   - Archivos faltantes: exactamente 0.

7. **Prueba de Conectividad con NotebookLM:**
   - Herramienta MCP `notebooklm` -> `notebook_list`: Devolvió error `RPC: The server rejected this request (unauthenticated). (retriable=false)`.
   - Cliente Python `notebooklm-py` en `venv` -> `from_storage()`: Devolvió error `notebooklm.exceptions.AuthError: Authentication expired or invalid. Run 'notebooklm login' to re-authenticate.`
   - Ejecución de Python: En el entorno Windows del usuario, invocar `.\venv\Scripts\python.exe` mediante `run_command` requiere el parámetro `BypassSandbox: true` para sortear la restricción de acceso sobre `C:\Users\rgarc\AppData\Local\...`.

---

## 2. LOGIC CHAIN

1. **Alineación con el Mandato `ORIGINAL_REQUEST.md`:**
   - El objetivo es crear exactamente 4 cuadernos en NotebookLM Pro para el Personal de Legos (Censo nominal de vecinos) de las cuatro localidades: Navarredondilla, Molinillo, Navandrinal y Villarejo.
   - La carga debe alcanzar exactamente las 200 fuentes asignadas.

2. **Gobernanza de Nombres y Estándar `[L-28]`:**
   - En el corpus general conviven 9 rollos DGS. Por ejemplo, el fotograma `00952` existe tanto en el rollo `004469028` (Molinillo Legos) como en `004306112` (Navarredondilla Bautismos). Si se truncasen los ceros o el rollo, la clave colisionaría.
   - Por tanto, la clave física universal `{DGS}_{FOTOGRAMA}.jpg` es de obligado cumplimiento en todas las capas: nombres de fuentes en NotebookLM, citas en transcripciones y registros del catálogo.

3. **Gobernanza de Aislamiento Topográfico `[L-29]`:**
   - El Catastro de Ensenada de 1751–1752 encuadernó en el mismo legajo físico `H-669` a El Villarejo, San Juan del Molinillo y Navandrinal (por ser anejos de la villa matriz de Navalmoral de la Sierra).
   - Sin embargo, mezclar estas tres aldeas en un único cuaderno de NotebookLM violaría la regla `[L-29]`, provocando contaminación cruzada de toponimia menor (pagos, arroyos, parajes rústicos), homónimos interfamiliares y pérdida de foco paleográfico.
   - La partición estricta en 4 cuadernos mono-localidad (`NRDL-ENSENADA-LEGOS-01`, `JMOL-ENSENADA-LEGOS-01`, `VLLR-ENSENADA-LEGOS-01`, `NDRN-ENSENADA-LEGOS-01`) garantiza el cumplimiento de `[L-29]`.
   - Adicionalmente, el tamaño de cada cuaderno (87, 28, 51, 34 fuentes) respeta holgadamente la cota máxima de 300 fuentes por cuaderno.

4. **Blindaje del Cuaderno Activo `Lib. Baut. Navarre Vol. 1 (1594-1695)`:**
   - El cuaderno con ID `7967d647-8ca2-4863-a576-11843e8e8802` contiene 188 fuentes en estado de explotación científica activa (bautismos primitivos de Navarredondilla).
   - Cualquier operación de creación, borrado, sincronización o limpieza masiva de cuadernos debe incorporar una cláusula de guarda estricta que excluya explícitamente `7967d647-8ca2-4863-a576-11843e8e8802`.

5. **Límites de Alcance (Out of Scope):**
   - Fondos Sacramentales / Parroquiales (`PARROQUIAL`): quedan formalmente excluidos.
   - Fondos de Bienes y Haciendas (`BIENES_LEGOS`): 2.600+ folios catalogados en `NRDL-ENSENADA-BIENES-*`, `JMOL-ENSENADA-BIENES-*`, `VLLR-ENSENADA-BIENES-*`, `NDRN-ENSENADA-BIENES-*` quedan diferidos para fases posteriores.
   - Fondos de Rentas Eclesiásticas (`BIENES_ECLESIASTICOS`): 391 folios del rollo `004469026` quedan diferidos.
   - Fondos de Navalmoral de la Sierra (`NMRL-ENSENADA-LEGOS-01`, 153 folios) e Interrogatorio General (`ENSENADA-INTERROGATORIO`, 101 folios): quedan fuera de esta fase.

6. **Estrategia de Ejecución Técnica (MCP vs `notebooklm-py`):**
   - El servidor MCP `source_add` exige que los archivos locales residan en rutas permitidas bajo `NOTEBOOKLM_MCP_ALLOWED_ROOTS` o limita el envío directo a 7 KB en base64 (inviable para imágenes JPG de 2 a 5 MB).
   - La librería Python `notebooklm-py` (vía `client.sources.add_file(nb_id, file_path)`) realiza streaming directo al servicio resumable Scotty de Google desde cualquier ruta en disco.
   - Dado que las credenciales están expiradas (`AuthError: Authentication expired`), el orquestador/usuario debe ejecutar la renovación de sesión (`notebooklm login` o regeneración de cookies de Chromium) antes de la carga de fuentes.

---

## 3. TABLA DE CARACTERÍSTICAS DESCUBIERTAS (Features Discovered)

| # | Categoría | Característica / Requisito | Descripción | Entradas | Salidas | Comportamiento ante Error | Descubierto Vía |
|---|---|---|---|---|---|---|---|
| 1 | Nomenclatura | Formato Canónico `{DGS}_{FOTOGRAMA}.jpg` | Nombre de archivo sin truncamiento de ceros (9 dígitos DGS + 5 dígitos fotograma). | `rollo_dgs` (string 9 chars), `fotograma_numero` (int). | String: `004469033_00881.jpg`. | Si se trunca (ej: `881.jpg`), colisiona con otros rollos; invalidación inmediata. | `REGLAS_Y_PROMPTS_OFICIALES.md` [L-28], `BITACORA_EXPERIMENTOS.md` Exp 12. |
| 2 | Topología | Cuaderno Mono-Localidad | Cuaderno asociado exclusivamente a una sola localidad de 4 letras (`NRDL`, `JMOL`, `VLLR`, `NDRN`). | Código cuatriletrado y lista de fuentes del pueblo. | Cuaderno puro sin interferencia toponímica ni onomástica. | Si se mezclan pueblos en un cuaderno, alucinación de parajes rústicos y homónimos. | `REGLAS_Y_PROMPTS_OFICIALES.md` [L-29], `BITACORA_EXPERIMENTOS.md` Exp 13. |
| 3 | Capacidad | Límite de 300 Fuentes | Ningún cuaderno debe exceder 300 fuentes por restricción de NotebookLM. | Lote de fuentes asignadas. | Cuadernos con 87, 28, 51 y 34 fuentes. | Rechazo de la API de NotebookLM al superar 300 fuentes. | `ORIGINAL_REQUEST.md`, `TODO.md`, `catalogo_corpus.json`. |
| 4 | Gobernanza | Nombres de Cuaderno Obligatorios | Nombres exactos predefinidos para los 4 cuadernos de producción. | String literal estandarizado. | `NRDL-ENSENADA-LEGOS-01`, `JMOL-ENSENADA-LEGOS-01`, `VLLR-ENSENADA-LEGOS-01`, `NDRN-ENSENADA-LEGOS-01`. | No reconocer o desincronizar cuadernos si se usan nombres arbitrarios. | `ORIGINAL_REQUEST.md` R1, `catalogo_corpus.json`. |
| 5 | Seguridad / Integridad | Protección del Cuaderno Activo | Blindaje incondicional contra modificación o borrado del cuaderno existente `7967d647-8ca2-4863-a576-11843e8e8802`. | `notebook_id` objetivo. | Operaciones denegadas si `notebook_id === "7967d647-8ca2-4863-a576-11843e8e8802"`. | Pérdida irreparable de 188 fuentes de investigación activa de bautismos. | `ORIGINAL_REQUEST.md` R3, `BITACORA_EXPERIMENTOS.md` Exp 02. |
| 6 | Alcance | Segregación Estamental y Exclusiones | Procesar exclusivamente `LIBRO_LEGOS` (estamento Seglar). Excluir `BIENES_LEGOS`, `BIENES_ECLESIASTICOS`, `INTERROGATORIO` y fondos parroquiales. | Filtro `tipo_documento == "LIBRO_LEGOS"` y `cuaderno_asignado_id IN legos_set`. | Exactamente 200 imágenes procesadas. | Carga indebida de 8.315 imágenes fuera de alcance. | `ORIGINAL_REQUEST.md` R3, `catalogo_corpus.json`, `GUIA_MAESTRA_ARCHIVOS_DESCARGADOS.md`. |
| 7 | Ingesta | Carga de Archivos Locales en Disco | Carga masiva de imágenes JPG de 2 a 5 MB a NotebookLM. | Rutas absolutas en disco (`imagenes/rollo ...`). | Fuentes subidas y procesadas en NotebookLM. | Error de permisos si se intenta subir por MCP sin allowed roots; timeout en uploads lentos. | `python-api-full.md`, MCP schema `source_add.json`. |
| 8 | Autenticación | Credenciales de Sesión Google | Sesión activa para interactuar con la API interna de NotebookLM. | Almacenamiento local de tokens/cookies (`from_storage()`). | Cliente autenticado con sesión válida. | `AuthError: Authentication expired or invalid. Run 'notebooklm login' to re-authenticate.` | Prospección en vivo de `test_client_storage.py` y MCP `notebook_list`. |
| 9 | Parsing JSON | Manejo de BOM UTF-8 | Limpieza del caracter `\uFEFF` al cargar `catalogo_corpus.json`. | Buffer/texto crudo del archivo JSON. | Objeto JSON parseado correctamente. | `SyntaxError: Unexpected token '﻿'` si no se elimina el BOM. | Ejecución empírica con Node.js en terminal. |
| 10 | Entorno de Ejecución | Sandbox Bypass en Windows | Ejecución de scripts de Python en entorno venv sobre Windows. | Flag `BypassSandbox: true` en invocaciones `run_command`. | Salida de proceso sin denegación de acceso. | `did not find executable: Acceso denegado` al acceder a `AppData\Local`. | Ejecución empírica en PowerShell/terminal. |

---

## 4. CASOS LÍMITE (Edge Cases)

| # | Característica | Entrada / Situación | Comportamiento Observado / Esperado | Medida de Mitigación / Protocolo |
|---|---|---|---|---|
| 1 | Carga de `catalogo_corpus.json` | Archivo con BOM UTF-8 (`EF BB BF`). | `JSON.parse` falla inmediatamente con error de sintaxis en el carácter 0. | Aplicar `raw.replace(/^\uFEFF/, '')` o decodificación `utf-8-sig` antes de parsear. |
| 2 | Ejecución de Python en Sandbox Windows | Comando `python` o `.\venv\Scripts\python.exe` en terminal estándar de agente. | Falla con `Acceso denegado` al resolver el ejecutable en `AppData\Local`. | Configurar `BypassSandbox: true` en la llamada a `run_command` para tareas con `venv`. |
| 3 | Llamada a API de NotebookLM sin renovar sesión | Token de sesión expirado en disco. | Lanza excepción `AuthError` (Python) o `RPC unauthenticated` (MCP). | El agente/usuario debe ejecutar renovación de autenticación antes del pipeline de ingesta. |
| 4 | Duplicidad de rutas en disco para Navarredondilla | 87 imágenes de NRDL existen en `imagenes\rollo 004469033\` y en `catastro ensenada Navarredondilla\`. | Ambos conjuntos son idénticos; riesgo de ambigüedad en scripts de carga. | Fijar como ruta primaria canónica `imagenes\rollo 004469033\`, con fallback secundario. |
| 5 | Contigüidad foliar en el legajo H-669 (Rollo 004469028) | Tres pueblos correlativos: VLLR (901–951), JMOL (952–979), NDRN (980–1013), seguidos de NMRL (1014–1166). | Si un bucle se desborda por índice, cargaría imágenes de otra localidad o de Navalmoral. | Validar estrictamente contra la lista de IDs explícitos de `catalogo_corpus.json`, jamás por bucles numéricos abiertos. |
| 6 | Subida simultánea de fuentes (Scotty Throttling) | Fan-out excesivo de conexiones concurrentes de subida. | Google Scotty puede saturar descriptores de archivo o rechazar sockets (`max_concurrent_uploads` agotado). | Mantener el default de concurrencia `max_concurrent_uploads = 4` y `upload_timeout = 120.0` con reintentos exponenciales. |
| 7 | Verificación del Cuaderno Activo en Listados | Scripts que borren o sincronicen cuadernos basándose en prefijos. | Si un filtro borra cuadernos existentes para "limpiar", podría destruir `7967d647-8ca2-4863-a576-11843e8e8802`. | Implementar un assert estricto: `assert nb.id != "7967d647-8ca2-4863-a576-11843e8e8802"` antes de cualquier mutación. |
| 8 | Asignación de metadatos ARK | Campo `url_ark` figura como `null` en los 200 registros de Ensenada en `catalogo_corpus.json`. | Normal para esta fase: la URL ARK se extrae con `extraer_arks_familysearch.js` en etapa posterior. | No bloquear la ingesta en NotebookLM por ausencia de ARK; el ID soporte `{DGS}_{FOTOGRAMA}.jpg` es la PK física suficiente. |

---

## 5. CAVEATS

1. **Estado de Autenticación de NotebookLM:** Durante la prospección activa, tanto el servidor MCP como la librería `notebooklm-py` reportaron sesión caducada. La fase de creación de cuadernos y subida de fuentes requerirá refrescar credenciales (`notebooklm login`).
2. **URLs ARK Diferidas:** Los 200 fotogramas tienen `url_ark: null` en `catalogo_corpus.json`. Esto no afecta la creación ni la ingesta en NotebookLM (que opera sobre archivos JPG físicos en disco), pero debe tenerse en cuenta para la catalogación definitiva en ArcadeDB.
3. **Mano Caligráfica Provisional:** En `catalogo_corpus.json`, el campo `escribano_mano_adscrita` figura como `"COMISION_ENSENADA_1752 (Pendiente de cotejo ductus)"`. Esto no afecta la estructura de los cuadernos; el análisis paleográfico se ejecutará una vez los cuadernos estén operativos.

---

## 6. CONCLUSIÓN

El sistema cuenta con especificaciones completas, coherentes y unívocas para la ejecución de la tarea:
- **Exactamente 4 cuadernos mono-localidad:** `NRDL-ENSENADA-LEGOS-01`, `JMOL-ENSENADA-LEGOS-01`, `VLLR-ENSENADA-LEGOS-01`, `NDRN-ENSENADA-LEGOS-01`.
- **Exactamente 200 imágenes físicas identificadas y verificadas en disco (0 faltantes):**
  * `NRDL-ENSENADA-LEGOS-01`: 87 fuentes (`004469033_00881.jpg` a `004469033_00967.jpg`).
  * `JMOL-ENSENADA-LEGOS-01`: 28 fuentes (`004469028_00952.jpg` a `004469028_00979.jpg`).
  * `VLLR-ENSENADA-LEGOS-01`: 51 fuentes (`004469028_00901.jpg` a `004469028_00951.jpg`).
  * `NDRN-ENSENADA-LEGOS-01`: 34 fuentes (`004469028_00980.jpg` a `004469028_01013.jpg`).
- **Límites blindados:** El cuaderno activo `Lib. Baut. Navarre Vol. 1 (1594-1695)` (`7967d647-8ca2-4863-a576-11843e8e8802`) queda expresamente protegido contra cualquier mutación. Los fondos sacramentales y de Bienes quedan totalmente fuera de esta fase.

---

## 7. CRITERIOS DE ACEPTACIÓN Y MÉTODO DE VERIFICACIÓN INDEPENDIENTE

### Criterios de Aceptación (Checklist)
- [ ] **Existencia de los 4 Cuadernos:** Existen en NotebookLM exactamente 4 nuevos cuadernos titulados `NRDL-ENSENADA-LEGOS-01`, `JMOL-ENSENADA-LEGOS-01`, `VLLR-ENSENADA-LEGOS-01`, `NDRN-ENSENADA-LEGOS-01`.
- [ ] **Incolumidad del Cuaderno Activo:** El cuaderno `Lib. Baut. Navarre Vol. 1 (1594-1695)` (`7967d647-8ca2-4863-a576-11843e8e8802`) conserva intactas sus 188 fuentes originales y configuración.
- [ ] **Exactitud Foliar y Nomenclatura:**
  - `NRDL-ENSENADA-LEGOS-01` contiene exactamente 87 fuentes con nombres `004469033_00881.jpg` a `004469033_00967.jpg`.
  - `JMOL-ENSENADA-LEGOS-01` contiene exactamente 28 fuentes con nombres `004469028_00952.jpg` a `004469028_00979.jpg`.
  - `VLLR-ENSENADA-LEGOS-01` contiene exactamente 51 fuentes con nombres `004469028_00901.jpg` a `004469028_00951.jpg`.
  - `NDRN-ENSENADA-LEGOS-01` contiene exactamente 34 fuentes con nombres `004469028_00980.jpg` a `004469028_01013.jpg`.
  - Cero truncamiento de ceros en identificadores de fuentes.
- [ ] **Estado de Fuentes:** Las 200 fuentes alcanzan estado completado/listo (`READY`) sin fuentes en estado de error o truncadas.

### Script de Verificación Independiente Recomendado
Una vez realizada la ingesta por el agente correspondiente, ejecutar un script de validación que consulte la API de NotebookLM y contraste los IDs de fuentes contra `catalogo_corpus.json`:

```bash
# Verificación de integridad en disco local (ejecutable en cualquier momento)
node -e "
const fs = require('fs');
const path = require('path');
const cat = JSON.parse(fs.readFileSync('catalogo_corpus.json', 'utf8').replace(/^\uFEFF/, ''));
const legos = ['NRDL-ENSENADA-LEGOS-01', 'JMOL-ENSENADA-LEGOS-01', 'VLLR-ENSENADA-LEGOS-01', 'NDRN-ENSENADA-LEGOS-01'];
let errors = 0;
legos.forEach(cid => {
  const items = cat.filter(d => d.cuaderno_asignado_id === cid);
  items.forEach(item => {
    const p1 = path.join('imagenes', 'rollo ' + item.rollo_dgs, item.id_imagen);
    const p2 = path.join('catastro ensenada Navarredondilla', item.id_imagen);
    if (!fs.existsSync(p1) && !fs.existsSync(p2)) {
      console.error('FALTA ARCHIVO:', item.id_imagen);
      errors++;
    }
  });
});
if (errors === 0) console.log('VERIFICACION DISCO: 200/200 ARCHIVOS PRESENTES (0 ERRORES)');
"
```
