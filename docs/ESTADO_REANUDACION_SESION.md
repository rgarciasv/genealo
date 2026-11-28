# Estado de Reanudación de Sesión (`2026-11-28 12:49`)

Documento de traspaso rápido para continuar sin pérdida de contexto si se agotan los tokens de la sesión actual.

---

## 1. Dónde estábamos exactamente

La **repesca dirigida** (`task-6919` + `task-6950` + revisión local Neon en `JMOL-BAUT-05`) **ha finalizado al 100% (23/23 micro-lotes en NotebookLM + 3 locales, `failed=0`)** y ya se ha ejecutado `--apply-only` (`12:48:46`):

### Resultado final aplicado en CSVs verificados
- **Casados (`1716–1920`):** [JMOL_INDICE_CASADOS_1716_1920_casados_VERIFICADO_NLM.csv](file:///c:/TRABAJOS/personal/genealo/htr_pipeline/outputs/indice_jmol_casados/JMOL_INDICE_CASADOS_1716_1920_casados_VERIFICADO_NLM.csv)
  - **`OK=42 | CORREGIDO=54 | NO_ENCONTRADO=0`** (**100% resuelto**, `fila 1062` *Eladia Remarti* confirmada en `004298571_00516.jpg`).
- **Bautismos (`1750–1921`):** [JMOL_INDICE_BAUTISMOS_1750_1921_bautismos_VERIFICADO_NLM.csv](file:///c:/TRABAJOS/personal/genealo/htr_pipeline/outputs/indice_jmol_bautismos/JMOL_INDICE_BAUTISMOS_1750_1921_bautismos_VERIFICADO_NLM.csv)
  - **`OK=108 | CORREGIDO=193 | NO_ENCONTRADO=15`** (sobre los 316 registros marcados con duda/alerta).
  - De los `15` `NO_ENCONTRADO` restantes en Bautismos:
    - **5 filas (`3196, 3197, 2754, 1169, 2250`)** están **documentadas en el Libro 3.º bis** (nota archivística de 1981 en `004298570_02052.jpg`, desfase `456->4`).
    - **2 filas (`833, 1065`)** son **post-1862** (Libro 5.º, no microfilmado).
    - **1 fila (`2013`)** está **tachada con aspas** en el índice y confirmada inexistente en 1824.
    - **3 filas de 1850 (`3433, 1535, 3434`)** en `JMOL-BAUT-04`: `02400.jpg` (fol. `445v`/`446`) ya es **1851**, por lo que si se desean revisar hay que mirar justo antes (`02390..02398`) o en el arranque de `JMOL-BAUT-05` (`1851`).
    - Más los pocos casos residuales (`4761` tachado en 1800, etc.) que puedan quedar en `bautismos`.

---

## 2. Comandos exactos para reanudar en la siguiente sesión

1. **Comprobar / completar los lotes que falten** (el script es 100% idempotente: salta cualquier `*_repesca_*.md` ya guardado en `htr_pipeline/outputs/cotejo_dudas_nlm/lotes/`):
   ```powershell
   .\.venv\Scripts\python.exe scripts/vllm_notebooklm/repescar_no_encontrados_nlm.py
   ```
   *(Nota: si `repesca_04_baut03_1801` vuelve a dar timeout con 5 filas, dividirlo en 2 micro-consultas de 2–3 filas sobre `02051..02055` y `02056..02060`; tener en cuenta que `3196` y `3197` pertenecen al Libro 3.º bis según la nota de 1981 en `02052.jpg`.)*

2. **Fusionar todos los resultados en los CSV verificados:**
   ```powershell
   .\.venv\Scripts\python.exe scripts/vllm_notebooklm/cotejar_dudas_indices_nlm.py --apply-only
   ```

3. **Revisar qué filas sigan como `NO_ENCONTRADO` (si queda alguna):**
   - Consultar los `.md` generados en `htr_pipeline/outputs/cotejo_dudas_nlm/lotes/` y actualizar `LISTA_NO_ENCONTRADOS_REVISION_MANUAL.md` si procede.

---

## 3. Siguientes bloques en el backlog del proyecto
Documentados previamente en `docs/` (commits `ade8be1`, `64b5ef5`, `7ea81df`):
- **Confirmaciones:** extraer e indexar listas de confirmaciones de `JMOL` y `NMRL` (pendiente).
- **Navalmoral (`NMRL`):** aplicar el protocolo optimizado (`01_DICCIONARIO_ANCLAJE_NMRL.md`, particionado hasta ~300 fuentes/cuaderno en NotebookLM Pro, censo completo de folios/anomalías).
- **Descarga de imágenes FamilySearch:** Codex dejó avances sin commitear en `scripts/familysearch/` (revisar antes de commitear).
