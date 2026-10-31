## 2026-10-31T09:53:32Z

[Message] timestamp=2026-10-31T09:53:32Z sender=51844bfa-235d-45b8-933b-b08449a4bb96 priority=MESSAGE_PRIORITY_HIGH content=Usa agentes para esta tarea: "usa agentes que me hace ilusion ver como funcionan, si es que en este caso sirven para algo". Crear en NotebookLM los 4 cuadernos de Personal de Legos del Catastro de Ensenada para Navarredondilla, San Juan del Molinillo, Navandrinal y El Villarejo, y cargar sus 200 fuentes documentales correspondientes para producción en la investigación genealógica del proyecto.

Working directory: c:\TRABAJOS\personal\genealo
Integrity mode: development

## Requirements

### R1. Creación de los cuadernos de Personal de Legos
Crear en NotebookLM los 4 cuadernos mono-localidad específicos para los padrones de Personal de Legos del Catastro de Ensenada:
- `NRDL-ENSENADA-LEGOS-01` (Navarredondilla)
- `JMOL-ENSENADA-LEGOS-01` (San Juan del Molinillo)
- `VLLR-ENSENADA-LEGOS-01` (El Villarejo)
- `NDRN-ENSENADA-LEGOS-01` (Navandrinal)
Cada cuaderno debe ser estrictamente mono-localidad [L-29] y no exceder el límite de 300 fuentes por cuaderno.

### R2. Carga de las 200 fuentes documentales desde el catálogo canónico
Cargar en cada cuaderno las fuentes documentales asignadas en `catalogo_corpus.json` (rutas físicas en disco y signaturas correspondientes) usando el identificador físico primario `{DGS}_{FOTOGRAMA}.jpg` sin truncar ceros [L-28]:
- `NRDL-ENSENADA-LEGOS-01`: 87 imágenes (`004469033_00881.jpg` a `004469033_00967.jpg`).
- `JMOL-ENSENADA-LEGOS-01`: 28 imágenes (`004469028_00952.jpg` a `004469028_00979.jpg`).
- `VLLR-ENSENADA-LEGOS-01`: 51 imágenes (`004469028_00901.jpg` a `004469028_00951.jpg`).
- `NDRN-ENSENADA-LEGOS-01`: 34 imágenes (`004469028_00980.jpg` a `004469028_01013.jpg`).
Total: exactamente 200 imágenes. La elección entre el servidor MCP `notebooklm` o la librería Python `notebooklm-py` en el entorno virtual (`venv`) queda a decisión del equipo.

### R3. Preservación del cuaderno activo y exclusión de fases diferidas
No modificar ni recrear el cuaderno existente `Lib. Baut. Navarre Vol. 1 (1594-1695)` (`7967d647-8ca2-4863-a576-11843e8e8802`). No procesar en esta fase los cuadernos de registros parroquiales ni los padrones de Bienes de Legos ni Eclesiásticos del Catastro de Ensenada.

## Acceptance Criteria

### Cuadernos y Fuentes en NotebookLM
- [ ] Existen exactamente 4 cuadernos nuevos creados con los nombres y localidades estipulados (`NRDL-ENSENADA-LEGOS-01`, `JMOL-ENSENADA-LEGOS-01`, `VLLR-ENSENADA-LEGOS-01`, `NDRN-ENSENADA-LEGOS-01`).
- [ ] El cuaderno activo existente `Lib. Baut. Navarre Vol. 1 (1594-1695)` (`7967d647-8ca2-4863-a576-11843e8e8802`) permanece inalterado.
- [ ] Cada uno de los 4 cuadernos contiene exactamente el conjunto de fuentes asignadas en `catalogo_corpus.json` (87 en NRDL, 28 en JMOL, 51 en VLLR, 34 en NDRN; 200 fuentes en total), nombradas bajo el estándar `{DGS}_{FOTOGRAMA}.jpg`.

### Verificación Programática
- [ ] Un script de verificación independiente consulta la API de NotebookLM y valida que los 4 cuadernos existen, que cada uno contiene sus fuentes asignadas según `catalogo_corpus.json`, y que el estado de procesamiento de todas las 200 fuentes es correcto, reportando 0 fallos o ausencias.


## 2026-10-31T10:00:39Z

[Message] sender=29d7a117-bbe1-4622-a95f-c3693c372260 priority=MESSAGE_PRIORITY_HIGH content=Actualización arquitectónica del usuario para el Project Orchestrator:

Se ha transmitido a explorer_survey_2 la directiva canónica sobre cómo nos conectamos y operamos con NotebookLM en el proyecto:
1. Usamos el conector MCP `notebooklm` registrado en Antigravity (`venv\Scripts\notebooklm-mcp.exe`).
2. La autenticación se basa en el perfil persistente de Chromium en `C:\Users\rgarc\.notebooklm\profiles\default\browser_profile` (Regla [L-21]). Cuando expira, se renueva con `venv\Scripts\notebooklm.exe login` fuera del sandbox de forma 100% desatendida.
3. Para la creación de cuadernos y subida de las 200 imágenes: la mejor opción técnica comprobada es ejecutar un script en el `venv` con `notebooklm-py` (`NotebookLMClient.from_storage()`), con `client.notebooks.create()` y `client.sources.add_file(notebook_id, path)`, lo cual evita fricciones de variables de entorno en stdio y sube los archivos directamente con la sesión activa.
4. Preservación absoluta del cuaderno activo `7967d647-8ca2-4863-a576-11843e8e8802`.
