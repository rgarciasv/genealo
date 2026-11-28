# Estado de Reanudación de Sesión (`2026-11-28 12:34`)

Documento de traspaso rápido para continuar sin pérdida de contexto si se agotan los tokens de la sesión actual.

---

## 1. Dónde estábamos exactamente

La **repesca dirigida** (`task-6919` + revisión local Neon en `JMOL-BAUT-05`) **ha finalizado** (`done=20 | failed=3`) y ya se ha ejecutado `--apply-only` (`12:33:44`):

### Resultado ya aplicado en CSVs verificados
- **Casados (`1716–1920`):** [JMOL_INDICE_CASADOS_1716_1920_casados_VERIFICADO_NLM.csv](file:///c:/TRABAJOS/personal/genealo/htr_pipeline/outputs/indice_jmol_casados/JMOL_INDICE_CASADOS_1716_1920_casados_VERIFICADO_NLM.csv) pasó de `NO_ENCONTRADO=21` a:
  - **`OK=41 | CORREGIDO=54 | NO_ENCONTRADO=1`**
- **Bautismos (`1750–1921`):** [JMOL_INDICE_BAUTISMOS_1750_1921_bautismos_VERIFICADO_NLM.csv](file:///c:/TRABAJOS/personal/genealo/htr_pipeline/outputs/indice_jmol_bautismos/JMOL_INDICE_BAUTISMOS_1750_1921_bautismos_VERIFICADO_NLM.csv) pasó de `NO_ENCONTRADO=32` (+ 6 pendientes) a:
  - **`OK=108 | CORREGIDO=193 | NO_ENCONTRADO=12`**

### Únicos 3 micro-lotes que fallaron en `task-6919` (pendientes de reintento)
1. `casados_repesca_08_matr03_1898` (`fila 1062`, 1898, fol. 184, `00514..00518`) — `Timeout (280s)`.
2. `bautismos_repesca_04_baut03_1801` (`filas 3196, 3197, 2754, 1169, 2250`, 1801–1802, `02051..02060`) — `Timeout (280s)`. *(Nota: `3196` y `3197` pertenecen al Libro 3.º bis según la nota de 1981 en `02052.jpg`.)*
3. `bautismos_repesca_15_baut04_1850b` (`filas 3433, 1535, 3434`, 1850, `02399..02404`) — `Sin tabla válida (0 chars)`.

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
