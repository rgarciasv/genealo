# Dispatch History

## 2026-10-31T11:45:44Z

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
  Total: 2.276 imágenes en 15 cuadernos. Todos cumplen estrictamente <= 245 fuentes por cuaderno (<= 300).
- **Blindaje inmutable de cuadernos existentes**:
  - `Lib. Baut. Navarre Vol. 1 (1594-1695)` (`7967d647-8ca2-4863-a576-11843e8e8802`, que es `NRDL-BAUT-04`) NO debe ser modificado ni recreado.
  - Los 4 cuadernos recién creados de Ensenada Legos (`ec86de71-...`, `407d5cb4-...`, `e7fba70b-...`, `cd72ef58-...`) tampoco deben tocarse.
- **Reglas del proyecto**:
  - `[L-28]`: Identificador físico primario `{DGS}_{FOTOGRAMA}.jpg` sin truncar ceros.
  - `[L-29]`: Cuadernos mono-localidad, <= 300 fuentes por cuaderno.
  - `[L-21]`: Autenticación desatendida mediante perfil persistente en venv (`notebooklm.exe login` con `BypassSandbox: true` si se requiere refresco).
- **Herramientas existentes**:
  - Reutilizar / parametrizar los scripts en `c:\TRABAJOS\personal\genealo\scripts\` (`ingest_ensenada_legos.py` y `verify_notebooklm_sources.py`) adaptándolos a la serie parroquial de Navarredondilla usando `notebooklm-py` (v0.8.5).
- **Criterio de Aceptación**:
  - Creación de los 15 cuadernos con nomenclatura canónica.
  - Carga efectiva de las 2.276 fuentes en estado `READY`.
  - Verificación programática E2E independiente con 0 fallos o ausencias.

## 2026-10-31T12:46:31Z

Quota has reset. Please resume orchestration. Check worker_nrdl_m1 and test_writer_nrdl_1 handoffs and continue execution.
