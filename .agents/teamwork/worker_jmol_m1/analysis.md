# Analysis & Ingestion Monitoring Log — San Juan del Molinillo Parroquial

**Date**: 2026-10-31  
**Last Telemetry Update**: 2026-10-31T22:50:40+00:00  
**Agent**: teamwork_worker (`worker_jmol_m1`)  
**Pipeline**: `scripts/ingest_sanjuan_parroquial.py`  
**Active Ingestion PID**: 181048 (Task ID: `task-566`, RUNNING)  
**Checkpoint**: `scripts/ingest_checkpoint_jmol.json`  
**Log Path**: `scripts/ingest_sanjuan_parroquial.log`  

---

## 1. Executive Summary & Telemetry

- **Canonical Corpus Requirement**: 2,731 photographic records across 18 notebooks.
- **Current Checkpoint Sources**: **2,460 / 2,731** (90.1%).
- **Remaining Sources**: **271**.
- **Completed Notebooks**: **14 / 18** (77.8%).
- **Upload Pacing**: ~3.5s upload + 2.5s pause = ~6.0s per source.
- **Session Health**: Renovación desatendida ejecutada [L-21]; `storage_state.json` actualizado y activo; subidas progresando sin fallos en `attempt 1/5`.

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
| 11 | `JMOL-DIFU-02` | 277 | 277 | COMPLETED | YES |
| 12 | `JMOL-DIFU-03` | 17 | 17 | COMPLETED | YES (pilot) |
| 13 | `JMOL-DIFU-04` | 214 | 214 | COMPLETED | YES |
| 14 | `JMOL-DIFU-05` | 99 | 99 | COMPLETED | YES (finished at 23:35:10 UTC) |
| 15 | `JMOL-DIFU-06` | 177 | 45 | IN_PROGRESS | NO (actively uploading: 132 remaining) |
| 16 | `JMOL-DIFU-PARVULOS` | 27 | 0 | QUEUED | NO |
| 17 | `JMOL-INDICE-DIFU` | 21 | 0 | QUEUED | NO |
| 18 | `JMOL-MIXTO-04` | 91 | 0 | QUEUED | NO |

---

## 3. Milestones & Unattended Session Management Log

1. **Hitos Completados**:
   - Serie Bautismos: 100% (1.080/1.080 fuentes, 6 cuadernos).
   - Serie Matrimonios: 100% (526/526 fuentes, 3 cuadernos).
   - Serie Defunciones: DIFU-01 (202), DIFU-02 (277), DIFU-03 (17), DIFU-04 (214), DIFU-05 (99) completados al 100%. Total 809 fuentes en Defunciones.
2. **Renovación Desatendida de Sesión [L-21]**:
   - A las 23:44 UTC, la expiración horaria de tokens Google provocó un `unauthenticated` en `JMOL-DIFU-06` (`004298571_01404.jpg`).
   - Se activó el mecanismo de recuperación y rotación de credenciales, renovándose `storage_state.json` (`__Secure-1PSIDTS` válido hasta 2027).
   - El pipeline fue relanzado bajo el **PID 181048** (Task ID: `task-566`), retomando exactamente en `004298571_01405.jpg`.
   - El proceso se encuentra activo, con 2.460 fuentes registradas (90,1% del corpus).
