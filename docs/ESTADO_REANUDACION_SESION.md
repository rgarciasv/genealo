# Estado de Reanudación de Sesión (`2026-11-28 11:51`)

Documento de traspaso rápido para continuar sin pérdida de contexto si se agotan los tokens de la sesión actual.

---

## 1. Dónde estábamos exactamente

Se estaba ejecutando la **repesca dirigida** de las filas `NO_ENCONTRADO` y pendientes del cotejo de índices de San Juan del Molinillo (`JMOL`) mediante:
- Revisión local en disco (`JMOL-BAUT-05`, `filas 284, 3904, 3905`) con Gemini 4 Neon: **COMPLETADA (3/3 `CORREGIDO`)** en `htr_pipeline/outputs/cotejo_dudas_nlm/lotes/bautismos_repesca_baut05_local.md`.
- Script secuencial idempotente en NotebookLM Pro: [repescar_no_encontrados_nlm.py](file:///c:/TRABAJOS/personal/genealo/scripts/vllm_notebooklm/repescar_no_encontrados_nlm.py).

### Resultado ya aplicado (`--apply-only` ejecutado a las `11:50:53`)
- **Casados (`1716–1920`):** los 8 lotes de repesca completaron. El CSV `htr_pipeline/outputs/indice_jmol_casados/JMOL_INDICE_CASADOS_1716_1920_casados_VERIFICADO_NLM.csv` pasó de `NO_ENCONTRADO=21` a:
  - **`OK=41 | CORREGIDO=54 | NO_ENCONTRADO=1`**
- **Bautismos (`1750–1921`):** con `baut02` (`01..03`), `baut03` (`05..07`) y `baut05_local` ya aplicados, el CSV `htr_pipeline/outputs/indice_jmol_bautismos/JMOL_INDICE_BAUTISMOS_1750_1921_bautismos_VERIFICADO_NLM.csv` pasó de `NO_ENCONTRADO=32` a:
  - **`OK=106 | CORREGIDO=187 | NO_ENCONTRADO=17`**
- **Pendiente en curso al escribir este resumen:**
  - `repesca_04_baut03_1801` (`filas 3196, 3197, 2754, 1169, 2250` sobre `02051..02060`) dio `Timeout (280s)`.
  - Los lotes `repesca_08_baut03_1829` a `repesca_15_baut04_1850b` estaban todavía ejecutándose en segundo plano (`task-6919`).

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
