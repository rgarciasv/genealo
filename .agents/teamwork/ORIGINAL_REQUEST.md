# Original User Request

## Parameters
[skip-interview]
How this run was launched; not part of the task.

## Initial Request — 2026-10-31T09:52:17Z

Usa agentes para esta tarea: "usa agentes que me hace ilusion ver como funcionan, si es que en este caso sirven para algo". Crear en NotebookLM los 4 cuadernos de Personal de Legos del Catastro de Ensenada para Navarredondilla, San Juan del Molinillo, Navandrinal y El Villarejo, y cargar sus 200 fuentes documentales correspondientes para producción en la investigación genealógica del proyecto.

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
## Follow-up — 2026-10-31 11:43:23 UTC

Ejecutar la Opción A: Crear en NotebookLM los 15 cuadernos de los fondos parroquiales de Navarredondilla (todos los restantes excepto NRDL-BAUT-04 que ya existe y es intocable) y cargar sus 2.276 fuentes documentales correspondientes desde catalogo_corpus.json, reutilizando la infraestructura de scripts/ y verificando programáticamente con 0 fallos.

---
### Contexto relevante del proyecto:
- **Proyecto**: "Proyecto de I+D Genealógico Alto Alberche".
- **Petición del usuario**:
  - *"me refiero a los libros parroquiales de los pueblos, no los que faltan del catastro del marques de la ensenada"*
  - *"y haciendo lo mismo que han hecho los agentes, y usando los mismo agentes para que no comiencen desde cero vamos a ponernos a crear el resto de libros y subir las imagenes (respetando el que ya existe)"*
  - *"la opcion A"* (Navarredondilla primero: 15 cuadernos, 2.276 imágenes).
- **Catálogo maestro**: `c:\TRABAJOS\personal\genealo\catalogo_corpus.json` (todas las 2.276 imágenes de Navarredondilla Parroquial mapeadas a sus cuadernos canónicos y rutas físicas en disco).
- **15 Cuadernos a Crear e Ingestar (Navarredondilla Parroquial)**:
  1. `NRDL-BAUT-01` (245 imágenes)
  2. `NRDL-BAUT-02` (157 imágenes)
  3. `NRDL-BAUT-03` (231 imágenes)
  4. `NRDL-BAUT-05` (144 imágenes)
  5. `NRDL-BAUT-06` (183 imágenes)
  6. `NRDL-BAUT-07` (102 imágenes)
  7. `NRDL-DIFU-01` (236 imágenes)
  8. `NRDL-DIFU-01B` (65 imágenes)
  9. `NRDL-DIFU-02` (171 imágenes)
  10. `NRDL-DIFU-03` (170 imágenes)
  11. `NRDL-DIFU-04` (188 imágenes)
  12. `NRDL-DIFU-05` (211 imágenes)
  13. `NRDL-MATR-01` (33 imágenes)
  14. `NRDL-MATR-02` (70 imágenes)
  15. `NRDL-MIXTO-01` (70 imágenes)
  Total: 2.276 imágenes en 15 cuadernos. Todos cumplen estrictamente $\le 245$ fuentes por cuaderno ($\le 300$).
- **Blindaje inmutable de cuadernos existentes**:
  - `Lib. Baut. Navarre Vol. 1 (1594-1695)` (`7967d647-8ca2-4863-a576-11843e8e8802`, que es `NRDL-BAUT-04`) NO debe ser modificado ni recreado.
  - Los 4 cuadernos recién creados de Ensenada Legos (`ec86de71-...`, `407d5cb4-...`, `e7fba70b-...`, `cd72ef58-...`) tampoco deben tocarse.
- **Reglas del proyecto**:
  - `[L-28]`: Identificador físico primario `{DGS}_{FOTOGRAMA}.jpg` sin truncar ceros.
  - `[L-29]`: Cuadernos mono-localidad, $\le 300$ fuentes por cuaderno.
  - `[L-21]`: Autenticación desatendida mediante perfil persistente en venv (`notebooklm.exe login` con `BypassSandbox: true` si se requiere refresco).
- **Herramientas existentes**:
  - Reutilizar / parametrizar los scripts en `c:\TRABAJOS\personal\genealo\scripts\` (`ingest_ensenada_legos.py` y `verify_notebooklm_sources.py`) adaptándolos a la serie parroquial de Navarredondilla usando `notebooklm-py` (v0.8.5).
- **Criterio de Aceptación**:
  - Creación de los 15 cuadernos con nomenclatura canónica.
  - Carga efectiva de las 2.276 fuentes en estado `READY`.
  - Verificación programática E2E independiente con 0 fallos o ausencias.
