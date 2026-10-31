# Analysis & Ingestion Monitoring Log — San Juan del Molinillo Parroquial

**Date**: 2026-10-31  
**Last Telemetry Update**: 2026-10-31T22:14:30+00:00  
**Agent**: teamwork_worker (`worker_jmol_m1`)  
**Pipeline**: `scripts/ingest_sanjuan_parroquial.py`  
**Active Ingestion PID**: 160988 (Task ID: `task-402`, RUNNING)  
**Checkpoint**: `scripts/ingest_checkpoint_jmol.json`  
**Log Path**: `scripts/ingest_sanjuan_parroquial.log`  

---

## 1. Executive Summary & Telemetry

- **Canonical Corpus Requirement**: 2,731 photographic records across 18 notebooks.
- **Current Checkpoint Sources**: **2,176 / 2,731** (79.7%).
- **Remaining Sources**: **555**.
- **Completed Notebooks**: **12 / 18** (66.7%).
- **Upload Pacing**: ~3.5s upload + 2.5s pause = ~6.0s per source.
- **Session Health**: Authentication valid, zero unhandled errors, uploads proceeding on attempt 1/5.

---

## 2. Notebook Ingestion Breakdown

| # | Target ID | Expected | Uploaded | Status | Checkpoint Completion |
|---|-----------|----------|----------|--------|-----------------------|
| 1 | `JMOL-BAUT-01` | 175 | 175 | COMPLETED | YES |
| 2 | `JMOL-BAUT-02` | 276 | 276 | COMPLETED | YES |
| 3 | `JMOL-BAUT-03` | 190 | 190 | COMPLETED | YES |
| 4 | `JMOL-BAUT-04` | 189 | 189 | COMPLETED | YES |
| 5 | `JMOL-BAUT-05` | 139 | 139 | COMPLETED | YES |
| 6 | `JMOL-INDICE-BAUT` | 111 | 111 | COMPLETED | YES |
| 7 | `JMOL-MATR-01` | 194 | 194 | COMPLETED | YES |
| 8 | `JMOL-MATR-02` | 134 | 134 | COMPLETED | YES |
| 9 | `JMOL-MATR-03` | 198 | 198 | COMPLETED | YES |
| 10 | `JMOL-DIFU-01` | 202 | 202 | COMPLETED | YES |
| 11 | `JMOL-DIFU-02` | 277 | 277 | COMPLETED | YES (finished at 23:07:22 UTC) |
| 12 | `JMOL-DIFU-03` | 17 | 17 | COMPLETED | YES (pilot) |
| 13 | `JMOL-DIFU-04` | 214 | 74 | IN_PROGRESS | NO (actively uploading: 140 remaining) |
| 14 | `JMOL-DIFU-05` | 99 | 0 | QUEUED | NO |
| 15 | `JMOL-DIFU-06` | 177 | 0 | QUEUED | NO |
| 16 | `JMOL-DIFU-PARVULOS` | 27 | 0 | QUEUED | NO |
| 17 | `JMOL-INDICE-DIFU` | 21 | 0 | QUEUED | NO |
| 18 | `JMOL-MIXTO-04` | 91 | 0 | QUEUED | NO |

---

## 3. Milestones & Progress Log

1. **Serie Bautismos**: 100% completada (1.080 fuentes en 6 cuadernos).
2. **Serie Matrimonios**: 100% completada (526 fuentes en 3 cuadernos).
3. **Serie Defunciones**:
   - `JMOL-DIFU-01`: 202/202 (COMPLETADO)
   - `JMOL-DIFU-02`: 277/277 (COMPLETADO a las 23:07:22 UTC)
   - `JMOL-DIFU-03`: 17/17 (COMPLETADO en piloto)
   - `JMOL-DIFU-04`: En progreso activo (74/214 subidas).
4. **Resumen de Salud**: El pipeline avanza sin interrupciones ni bloqueos de sesión, con una tasa sostenida de ~10 fuentes/minuto.
