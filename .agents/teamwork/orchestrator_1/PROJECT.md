# Project: San Juan del Molinillo Parish Corpus Ingestion & E2E Verification

## Architecture
- **Canonical Catalog**: `catalogo_corpus.json` defines exactly 2,731 photographic sources for San Juan del Molinillo across 18 sacramental notebooks.
- **Physical Assets**: 2,731 non-corrupt JPEG files (2.84 GB) located across `imagenes\rollo 004298571`, `imagenes\rollo 004298570`, and root-level bautismo directories.
- **Ingestion Engine**: `scripts/ingest_sanjuan_parroquial.py` running in background (task-2618), featuring dynamic multi-path resolution, atomic dual-tier checkpointing (`scripts/ingest_checkpoint_jmol.json`), headless HTTP client via `httpx` (zero profile contention), and exponential backoff retry.
- **Independent Verification Harness**: `scripts/verify_sanjuan_parroquial_sources.py`, executing live opaque-box verification against Google NotebookLM Pro to certify 0 missing, 0 duplicates, 0 errors, 100% READY status, and zero regression across protected production notebooks.

## Feature Inventory
| # | Feature / Notebook | Description | Sources | Milestone | Source |
|---|--------------------|-------------|---------|-----------|--------|
| 1 | `JMOL-BAUT-01` | Bautismos 1572-1663 | 175 | M1 & M2 | catalogo_corpus.json |
| 2 | `JMOL-BAUT-02` | Bautismos 1752-1800 | 276 | M1 & M2 | catalogo_corpus.json |
| 3 | `JMOL-BAUT-03` | Bautismos 1801-1827 | 190 | M1 & M2 | catalogo_corpus.json |
| 4 | `JMOL-BAUT-04` | Bautismos 1827-1852 | 189 | M1 & M2 | catalogo_corpus.json |
| 5 | `JMOL-BAUT-05` | Bautismos 1852-1875 | 139 | M1 & M2 | catalogo_corpus.json |
| 6 | `JMOL-INDICE-BAUT` | Índices de Bautismos | 111 | M1 & M2 | catalogo_corpus.json |
| 7 | `JMOL-MATR-01` | Matrimonios 1634-1772 | 194 | M1 & M2 | catalogo_corpus.json |
| 8 | `JMOL-MATR-02` | Matrimonios 1773-1823 | 134 | M1 & M2 | catalogo_corpus.json |
| 9 | `JMOL-MATR-03` | Matrimonios 1823-1894 | 198 | M1 & M2 | catalogo_corpus.json |
| 10 | `JMOL-MIXTO-04` (`JMOL-SACRAMENTAL-1842-1850`) | Códice Transición Sacramental | 91 | M1 & M2 | catalogo_corpus.json [L-30] |
| 11 | `JMOL-DIFU-01` | Difuntos 1633-1765 | 202 | M1 & M2 | catalogo_corpus.json |
| 12 | `JMOL-DIFU-02` | Difuntos 1765-1822 | 277 | M1 & M2 | catalogo_corpus.json |
| 13 | `JMOL-DIFU-03` | Difuntos 1822-1826 (Piloto previo) | 17 | Completed (M1) / Verify (M2) | catalogo_corpus.json |
| 14 | `JMOL-DIFU-04` | Difuntos 1826-1851 | 214 | M1 & M2 | catalogo_corpus.json |
| 15 | `JMOL-DIFU-05` | Difuntos 1852-1867 | 99 | M1 & M2 | catalogo_corpus.json |
| 16 | `JMOL-DIFU-06` | Difuntos 1867-1903 | 177 | M1 & M2 | catalogo_corpus.json |
| 17 | `JMOL-DIFU-PARVULOS` | Difuntos Párvulos | 27 | M1 & M2 | catalogo_corpus.json |
| 18 | `JMOL-INDICE-DIFU` | Índices de Difuntos | 21 | M1 & M2 | catalogo_corpus.json |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| M0 | Survey & Corpus Mapping | Disk filesystem, catalog, scripts & specification audit | none | DONE |
| M1 | Ingestion Supervision & Completion | Monitor background task-2618, track atomic checkpoint, handle session refresh, verify 17 remaining notebooks completed | M0 | DONE |
| M2 | Independent E2E Verification | Execute `verify_sanjuan_parroquial_sources.py` across all 18 notebooks and 2,731 sources, verify 6 protected notebooks intact, forensic audit | M1 | DONE |

## Interface Contracts
### Ingestion Pipeline ↔ Checkpoint
- Pipeline writes atomically to `scripts/ingest_checkpoint_jmol.json` via temp file + replace.
- Checkpoint tracks: `notebook_ids` (dict of 18 UUIDs), `completed_notebooks` (list of completed target IDs), `uploaded_sources` (dict mapping source ID to metadata).

### Checkpoint ↔ E2E Verification Harness
- Verification harness reads `scripts/ingest_checkpoint_jmol.json` and `catalogo_corpus.json`.
- Compares expected sources with live Google Cloud NotebookLM source listing.
- Requires: `missing == 0`, `extra == 0`, `ready_count == expected_count` (100% READY).
- Generates: `scripts/verification_report_jmol.json`.

## Protected Notebooks Shield (Zero Mutation Guarantee)
1. `7967d647-8ca2-4863-a576-11843e8e8802` (`Lib. Baut. Navarre Vol. 1 (1594-1695)`, 188 sources)
2. `ec86de71-2cb2-4fdf-9730-a3e9c612f002` (`NRDL-ENSENADA-LEGOS-01`, 38 sources)
3. `407d5cb4-ce0b-4824-be02-4fc82aa0639d` (`JMOL-ENSENADA-LEGOS-01`, 28 sources)
4. `e7fba70b-0447-4949-8cba-66774ec2658e` (`VLLR-ENSENADA-LEGOS-01`, 49 sources)
5. `cd72ef58-3755-46ee-abde-cb8d1d8ef3df` (`NDRN-ENSENADA-LEGOS-01`, 85 sources)
6. `1e6fec74-1e2f-4dd7-8ad1-6d25411de127` (`NRDL-MATR-01`, 33 sources)
7. All 14 other completed Navarredondilla parish notebooks
8. `a5d19fcc-d266-4497-bdb3-df182328bdcb` (`JMOL-DIFU-03`, 17 sources, pilot)

## Code Layout
- `catalogo_corpus.json`: Canonical catalog source of truth.
- `scripts/ingest_sanjuan_parroquial.py`: Ingestion pipeline script.
- `scripts/ingest_checkpoint_jmol.json`: Atomic checkpoint file.
- `scripts/verify_sanjuan_parroquial_sources.py`: E2E verification test harness.
- `scripts/verification_report_jmol.json`: Independent verification audit output.
- `scripts/ingest_sanjuan_parroquial.log`: Ingestion execution log.
