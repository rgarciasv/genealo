# Analysis & Ingestion Monitoring Log — San Juan del Molinillo Parroquial

**Date**: 2026-10-31 / 2026-11-01  
**Last Telemetry Update**: 2026-10-31T23:15:00+00:00  
**Agent**: teamwork_worker (`worker_jmol_m1`)  
**Pipeline**: `scripts/ingest_sanjuan_parroquial.py`  
**Active Ingestion PID**: None (Pipeline finished cleanly with exit code 0)  
**Checkpoint**: `scripts/ingest_checkpoint_jmol.json`  
**Log Path**: `scripts/ingest_sanjuan_parroquial.log`  

---

## 1. Executive Summary & Final Telemetry

- **Canonical Corpus Requirement**: 2,731 photographic records across 18 notebooks.
- **Final Checkpoint Sources**: **2,731 / 2,731** (**100.0%**).
- **Completed Notebooks**: **18 / 18** (**100.0%**).
- **Missing Sources**: **0**.
- **Exit Status**: Exit Code 0 (`San Juan del Molinillo Pipeline Completed Successfully!`).
- **Pacing & Throughput**: ~3.5s upload + 2.5s pause = ~6.0s per source (~10 sources/min).

---

## 2. Comprehensive Notebook Breakdown

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
| 14 | `JMOL-DIFU-05` | 99 | 99 | COMPLETED | YES |
| 15 | `JMOL-DIFU-06` | 177 | 177 | COMPLETED | YES |
| 16 | `JMOL-DIFU-PARVULOS` | 27 | 27 | COMPLETED | YES |
| 17 | `JMOL-INDICE-DIFU` | 21 | 21 | COMPLETED | YES |
| 18 | `JMOL-MIXTO-04` | 91 | 91 | COMPLETED | YES |
| **TOTAL** | **18 Cuadernos** | **2,731** | **2,731** | **100% COMPLETADO** | **18/18 YES** |

---

## 3. Series Totals Summary

- **Bautismos** (6 cuadernos): **1,080 / 1,080** (100.0%)
- **Matrimonios** (3 cuadernos): **526 / 526** (100.0%)
- **Defunciones** (7 cuadernos + párvulos + índice): **1,034 / 1,034** (100.0%)
- **Mixto** (1 cuaderno): **91 / 91** (100.0%)
- **Gran Total Parroquial**: **2,731 / 2,731** (100.0%)

---

## 4. Key Fault Tolerance & Operational Resolutions

1. **Purga Quirúrgica de Duplicados en Nube**:
   - `JMOL-MATR-02`: Eliminadas 9 instancias duplicadas; consolidado en 134/134.
   - `JMOL-MATR-03`: Eliminadas 149 instancias duplicadas que causaban `SourceAddError` por saturación del límite de 300 fuentes por cuaderno en Google; consolidado en 151/151 antes del relanzamiento y completado en 198/198.
2. **Renovación Desatendida de Sesión [L-21]**:
   - Rotación y refresco transparente de credenciales en `storage_state.json` tras la expiración cíclica horaria (~23:44 UTC), permitiendo al pipeline retomar la subida de `JMOL-DIFU-06` en attempt 1/5 sin intervención manual.
3. **Manejo de Errores Transitorios**:
   - Backoff exponencial operativo frente a micro-desconexiones (ej. `004298571_00807.jpg` en attempt 2/5).
4. **Cero Mutaciones en Cuadernos Protegidos**:
   - Escudo pre-flight validado en cada arranque sobre `Lib. Baut. Navarre Vol. 1`, `NRDL-ENSENADA-LEGOS-01`, `JMOL-ENSENADA-LEGOS-01`, `VLLR-ENSENADA-LEGOS-01`, `NDRN-ENSENADA-LEGOS-01` y `NRDL-MATR-01`.
