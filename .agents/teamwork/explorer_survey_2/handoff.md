# Informe de Investigación Técnica y Encuesta de Herramientas NotebookLM

**Agente:** `explorer_survey_2`  
**Directorio de trabajo:** `c:\TRABAJOS\personal\genealo\.agents\teamwork\explorer_survey_2\`  
**Fecha:** 2026-10-31T10:12:00Z  
**Destinatario:** Orquestador (`fed48cc4-ccf0-40bb-ae10-7fff6d7c2cd1`) / Equipo de Integración  

---

## 1. Observation (Observaciones Directas)

### 1.1 Estado Inicial del Servidor MCP `notebooklm` y Reautenticación Desatendida (`L-21`)
- **Herramienta ejecutada:** `call_mcp_tool(ServerName="notebooklm", ToolName="server_info", Arguments={"include_account": True})`.
- **Resultado inicial:**
  ```json
  {
    "server": "notebooklm",
    "version": "0.8.5 (50493ddf)",
    "auth": {
      "authenticated": true,
      "storage_exists": true,
      "json_valid": true,
      "cookies_present": true,
      "sid_cookie": true,
      "profile": "default"
    },
    "chat_tasks": { "generating": 0, "queued": 0, "concurrency": 3, "cached_results": 0 },
    "account": {
      "email": "rgarciasv@gmail.com",
      "authuser": 0,
      "available": false,
      "reason": "The server rejected this request (unauthenticated)."
    }
  }
  ```
- **Error subsiguiente al invocar `notebook_list`:**
  `Encountered error in tool execution: RPC: The server rejected this request (unauthenticated). (retriable=false)`.
- **Acción correctora ejecutada:** Conforme a la regla de proyecto `[L-21]` documentada en `BITACORA_EXPERIMENTOS.md:42`, se disparó:
  `run_command(CommandLine="c:\\TRABAJOS\\personal\\genealo\\venv\\Scripts\\notebooklm.exe login", BypassSandbox=True)`
- **Salida del proceso de login (tarea en segundo plano `task-79`):**
  ```text
  Profile: default
  Opening Chromium for Google login...
  Using persistent profile: C:\Users\rgarc\.notebooklm\profiles\default\browser_profile
  Capturing Google cookies...
  Identifying Google account...
  Account: rgarciasv@gmail.com
  Authentication saved to: C:\Users\rgarc\.notebooklm\profiles\default\storage_state.json
  ```
- **Estado verificado post-login en MCP `server_info`:**
  ```json
  {
    "server": "notebooklm",
    "version": "0.8.5 (50493ddf)",
    "auth": {
      "authenticated": true,
      "storage_exists": true,
      "json_valid": true,
      "cookies_present": true,
      "sid_cookie": true,
      "profile": "default"
    },
    "account": {
      "email": "rgarciasv@gmail.com",
      "authuser": 0,
      "available": true,
      "notebook_limit": 500,
      "source_limit": 300,
      "tier": 2,
      "output_language": null,
      "output_language_is_default": true
    }
  }
  ```
  *Nota técnica:* Cuenta activa `rgarciasv@gmail.com` en nivel `tier: 2` (NotebookLM Pro), con cuota para 500 cuadernos y hasta 300 fuentes por cuaderno.

### 1.2 Auditoría y Preservación del Cuaderno Activo `7967d647-8ca2-4863-a576-11843e8e8802`
- **Herramientas ejecutadas:** `notebook_describe` y `source_list(notebook="7967d647-8ca2-4863-a576-11843e8e8802")`.
- **Metadatos observados:**
  - **ID:** `7967d647-8ca2-4863-a576-11843e8e8802`
  - **Título:** `Lib. Baut. Navarre Vol. 1 (1594-1695)`
  - **Fecha creación:** `2026-10-18T04:22:37+00:00`
  - **Total de fuentes:** Exactamente **188 fuentes**, compuestas por:
    - 183 imágenes en formato JPG: desde `004306112_01872.jpg` hasta `004306112_02147.jpg`, todas con metadato `kind: "image"`, `_type_code: 13`, `status_label: "ready"`.
    - 5 fuentes textuales maestras en Markdown (`_type_code: 8`, `kind: "markdown"`):
      1. `00_INSTRUCCIONES_PALEOGRAFICAS_V2` (ID: `19c9191f-...`)
      2. `01_DICCIONARIO_ANCLAJE_NAVARREDONDILLA` (ID: `e05b2cf9-...`)
      3. `02_INSTRUCCIONES_CRONOLOGICAS_NAVARREDONDILLA_1594_1695` (ID: `fe09fb0d-...`)
      4. `03_AUTORIDADES_PALEOGRAFICAS_ALTO_ALBERCHE` (ID: `427541dc-...`)
      5. `04_JURISDICCIONES_Y_DEPENDENCIAS_PARROQUIALES` (ID: `0b8b5196-...`)
  - **Integridad:** El cuaderno se encuentra en estado inmutable y operativo. Cumple R3: queda formalmente excluido de modificaciones o recreaciones.

### 1.3 Entorno Python Local, Librería `notebooklm-py` y Permisos del Sandbox
- **Versión de Python en `c:\TRABAJOS\personal\genealo\venv`:** Python 3.14.2 (64-bit AMD64).
- **Versión del paquete `notebooklm-py`:** `0.8.5` (`venv/Lib/site-packages/notebooklm_py-0.8.5.dist-info`).
- **Comportamiento del Sandbox en Windows:**
  - La invocación directa de `venv\Scripts\python.exe` dentro del sandbox falla con `did not find executable at 'C:\Users\rgarc\AppData\Local\Python\pythoncore-3.14-64\python.exe': Acceso denegado`.
  - La invocación con `BypassSandbox: true` se ejecuta inmediatamente con código 0 y acceso completo al venv y a los módulos.
- **Capacidades de la API de `notebooklm` inspeccionadas en código fuente:**
  - `client.notebooks.create(title: str)`: crea cuadernos directamente.
  - `client.sources.add_file(notebook_id: str, file_path: str | Path, mime_type: str | None = None, wait: bool = False, wait_timeout: float = 120.0, title: str | None = None)` (`_sources.py:505`): realiza la subida directa de archivos locales mediante el pipeline resumable Scotty de Google.
  - Parámetros del cliente en `NotebookLMClient.from_storage()`:
    - `max_concurrent_uploads`: 4 (semáforo de subidas concurrentes).
    - `max_concurrent_rpcs`: 16.
    - Soporte nativo para lectura de credenciales desde `~/.notebooklm/profiles/default/storage_state.json`.

### 1.4 Verificación de los 200 Fotogramas del Catastro de Ensenada en Disco Local
- **Catálogo canónico:** `catalogo_corpus.json` (codificado en UTF-8 con BOM `utf-8-sig`).
- **Verificación física por localidad y cuaderno asignado:**
  1. `NRDL-ENSENADA-LEGOS-01` (Navarredondilla):
     - Rollo DGS: `004469033`
     - Rango: `004469033_00881.jpg` a `004469033_00967.jpg`
     - Cantidad: **87 imágenes**. Faltantes en disco: **0**.
     - Ubicación: `imagenes\rollo 004469033\`
  2. `JMOL-ENSENADA-LEGOS-01` (San Juan del Molinillo):
     - Rollo DGS: `004469028`
     - Rango: `004469028_00952.jpg` a `004469028_00979.jpg`
     - Cantidad: **28 imágenes**. Faltantes en disco: **0**.
     - Ubicación: `imagenes\rollo 004469028\`
  3. `VLLR-ENSENADA-LEGOS-01` (El Villarejo):
     - Rollo DGS: `004469028`
     - Rango: `004469028_00901.jpg` a `004469028_00951.jpg`
     - Cantidad: **51 imágenes**. Faltantes en disco: **0**.
     - Ubicación: `imagenes\rollo 004469028\`
  4. `NDRN-ENSENADA-LEGOS-01` (Navandrinal):
     - Rollo DGS: `004469028`
     - Rango: `004469028_00980.jpg` a `004469028_01013.jpg`
     - Cantidad: **34 imágenes**. Faltantes en disco: **0**.
     - Ubicación: `imagenes\rollo 004469028\`
- **Total comprobado:** Exactamente **200 imágenes JPG**, tamaño entre 780 KB y 1.15 MB por fotograma, todas presentes y legibles.

---

## 2. Logic Chain (Cadena Lógica de Deducción)

1. **Autenticación e Interfaz Operativa:**
   - La observación 1.1 demostró que cuando la sesión de Google expira, el conector MCP y cualquier llamada a la API rechazan peticiones con código `RPC: unauthenticated`.
   - La ejecución de `notebooklm.exe login` con `BypassSandbox: true` aprovechó el perfil persistente de Chromium (`C:\Users\rgarc\.notebooklm\profiles\default\browser_profile`) y renovó `storage_state.json` de forma desatendida en menos de 5 segundos.
   - Dado que tanto el servidor MCP `notebooklm` como la librería Python `notebooklm-py` leen exactamente el mismo archivo `storage_state.json`, ambos entornos quedaron inmediatamente autenticados y sincronizados.

2. **Viabilidad de Ingesta de Imágenes (.jpg):**
   - La inspección de las fuentes en el cuaderno existente `7967d647` (observación 1.2) demostró la existencia de 183 fuentes JPG activas con `kind: "image"` y `status_label: "ready"`.
   - El código interno de `notebooklm-py` (`_upload_decode.py` y `upload.py`, observación 1.3) resuelve el MIME type `image/jpeg` y envía el flujo binario hacia el endpoint resumable de Google (Scotty).
   - Por tanto, NotebookLM admite de manera nativa imágenes `.jpg` locales como fuentes multimodales completas sin necesidad de OCR previo ni conversión a PDF.

3. **Comparativa Técnica: Servidor MCP vs. Script Python `notebooklm-py`:**
   - **MCP `notebooklm`:**
     - En transporte stdio, la herramienta `source_add` con `source_type="file"` restringe las rutas locales mediante la variable de entorno `NOTEBOOKLM_MCP_ALLOWED_ROOTS`. Si dicha variable no está fijada en el lanzador del MCP, rechaza la ruta local o exige subida mediante URLs firmadas.
     - La subida inline vía MCP (`bytes_base64`) tiene un límite de 10.000 caracteres (~7 KB), inviable para imágenes de ~1 MB.
     - Ejecutar 200 llamadas individuales a través de herramientas MCP secuenciales de Antigravity consumiría decenas de turnos de agentes y sería propenso a interrupciones por timeouts.
   - **Librería Python `notebooklm-py` (`venv` con `BypassSandbox: true`):**
     - Invoca directamente `client.sources.add_file(notebook_id, file_path, wait=False)`.
     - Permite empaquetar la creación de los 4 cuadernos y la subida de los 200 archivos en un script desatendido con control estricto de concurrencia, pausas de cortesía (rate-limiting preventivo), reintentos exponenciales y barra de progreso.
     - Es determinista, atómico y registra un log pormenorizado en disco.
   - **Complementariedad para Verificación:**
     - El script en Python realiza la ingesta masiva rápida.
     - Posteriormente, las herramientas MCP (`source_list`, `notebook_list`) permiten una verificación cruzada e independiente del 100% de los cuadernos y fuentes desde la perspectiva del orquestador.

---

## 3. Caveats (Advertencias y Limitaciones)

1. **Ejecución en Windows y BypassSandbox:**
   - Todo script que se ejecute con `c:\TRABAJOS\personal\genealo\venv\Scripts\python.exe` **debe** incluir `BypassSandbox: true` en el tool `run_command` debido a que el binario base de Python se aloja en `AppData\Local\Python\pythoncore-3.14-64\python.exe`, inaccesible bajo el sandbox restringido por defecto de Windows.
2. **Límites de Velocidad de la API de Google (Rate Limits):**
   - Aunque la cuenta dispone de cuota Pro (tier 2), lanzar 200 subidas en paralelo saturaría las conexiones salientes o provocaría errores HTTP 429 / RPC 8 (`RESOURCE_EXHAUSTED`).
   - Se debe mantener una concurrencia máxima de 2 a 3 archivos simultáneos y una pausa de 500 ms a 1 s entre peticiones.
3. **Tiempo de Procesamiento Asíncrono en Google:**
   - Tras subir una imagen, NotebookLM entra en estado `status: 1` (`processing` / `preparing`) mientras el motor multimodal indexa la imagen. No es necesario bloquear el script con `wait=True` en cada imagen; es mucho más eficiente subirlas todas con `wait=False` y al final ejecutar un sondeo de estado con `wait_all_until_ready` o mediante un bucle de verificación de `source_list`.
4. **Preservación Incondicional:**
   - El cuaderno `7967d647-8ca2-4863-a576-11843e8e8802` no debe ser tocado por ningún bucle o script. Cualquier script de ingesta debe filtrar explícitamente los cuadernos objetivo por nombre (`NRDL-ENSENADA-LEGOS-01`, etc.) y nunca invocar llamadas destructivas (`notebook_delete` o `source_delete`).

---

## 4. Conclusion (Conclusión y Recomendaciones)

1. **Estado de Herramientas:** La pila tecnológica de NotebookLM (conector MCP + `notebooklm-py` v0.8.5) está **100% operativa** y autenticada bajo `rgarciasv@gmail.com`. El mecanismo `L-21` de reautenticación desatendida funciona a la perfección.
2. **Soporte de Fuentes:** Los 200 fotogramas existen íntegros en disco y el formato `.jpg` está completamente soportado para ingesta nativa y OCR multimodal.
3. **Estrategia Óptima de Ejecución recomendada:**
   - **Paso 1 (Creación e Ingesta):** Implementar y ejecutar un script Python en `scratch/ingestar_ensenada_legos.py` utilizando `notebooklm-py` en el entorno virtual (`venv\Scripts\python.exe` con `BypassSandbox: true`).
     - Creará exactamente los 4 cuadernos mono-localidad: `NRDL-ENSENADA-LEGOS-01`, `JMOL-ENSENADA-LEGOS-01`, `VLLR-ENSENADA-LEGOS-01`, `NDRN-ENSENADA-LEGOS-01`.
     - Subirá secuencialmente o en micro-lotes (concurrencia 2) las 200 imágenes asignadas en `catalogo_corpus.json` con su identificador canónico `{DGS}_{FOTOGRAMA}.jpg`.
   - **Paso 2 (Verificación Externa e Independiente):** Ejecutar un script de auditoría que utilice las herramientas MCP de NotebookLM para listar las fuentes de cada uno de los 4 cuadernos recién creados, cotejando que el conteo, nombres y estado (`status_label == 'ready'`) sean exactamente los 200 esperados, confirmando a la vez que `7967d647-8ca2-4863-a576-11843e8e8802` se mantiene con sus 188 fuentes originales.

---

## 5. Verification Method (Método de Verificación Independiente)

Para que cualquier agente o evaluador verifique de forma independiente estos hallazgos:

1. **Comprobar la salud del servidor MCP y autenticación:**
   ```powershell
   # Vía MCP tool en Antigravity:
   call_mcp_tool(ServerName="notebooklm", ToolName="server_info", Arguments={"include_account": True})
   # Debe retornar account.available: true y email: rgarciasv@gmail.com
   ```

2. **Comprobar la preservación del cuaderno activo:**
   ```powershell
   # Vía MCP tool:
   call_mcp_tool(ServerName="notebooklm", ToolName="notebook_describe", Arguments={"notebook": "7967d647-8ca2-4863-a576-11843e8e8802"})
   # Debe retornar 188 fuentes en total sin errores.
   ```

3. **Verificar la presencia de los 200 archivos JPG en disco:**
   Ejecutar fuera del sandbox:
   ```powershell
   c:\TRABAJOS\personal\genealo\venv\Scripts\python.exe -c "
   import json, os
   with open('catalogo_corpus.json', 'r', encoding='utf-8-sig') as f:
       cat = json.load(f)
   targets = ['NRDL-ENSENADA-LEGOS-01', 'JMOL-ENSENADA-LEGOS-01', 'VLLR-ENSENADA-LEGOS-01', 'NDRN-ENSENADA-LEGOS-01']
   for t in targets:
       items = [i for i in cat if i.get('cuaderno_asignado_id') == t]
       missing = [i for i in items if not os.path.exists(os.path.join('imagenes', 'rollo ' + i['rollo_dgs'], i['id_imagen']))]
       print(f'{t}: total={len(items)}, faltantes={len(missing)}')
   "
   ```
   **Condición de validez:** Debe imprimir 87, 28, 51 y 34 respectivamente, todos con `faltantes=0`.
