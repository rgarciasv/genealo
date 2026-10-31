# Project: Navarredondilla Parroquial Ingestion & Verification (Option A)

## Architecture
- **Corpus Parser & Grouping**:
  - Reads `catalogo_corpus.json` with BOM safety (`utf-8-sig`).
  - Filters strictly by `cuaderno_asignado_id == notebook_title` (CRITICAL: avoids range interleaving where `NRDL-MATR-01` fotogramas 1955–1987 is nested inside `NRDL-BAUT-01` 1870–2147).
  - Validates physical file existence on disk (`imagenes/rollo {rollo_dgs}/{id_imagen}`) before upload.
- **Persistent Dual-Tier Checkpointing & Ingestion Engine**:
  - Leverages Python virtual environment (`venv\Scripts\python.exe`) with `notebooklm-py` v0.8.5.
  - Persistent local JSON state (`scripts/ingest_checkpoint_nrdl.json`) tracks each uploaded image `(notebook_id, filename, source_id, status)` atomically.
  - Pre-upload remote sync via `client.sources.list(notebook_id)` detects any existing sources (`is_ready` or `is_processing`), guaranteeing 0 duplicate uploads upon restart.
  - Granular CLI flags (`--notebook`, `--dry-run`, `--pause`, `--limit`, `--skip-readiness-wait`).
  - Pacing of 1.5s between uploads and 5-attempt exponential backoff (2s, 4s, 8s, 16s, 32s) for rate limit / network error resilience.
- **Untouchable Assets Hard Shielding**:
  - Active sacramental notebook `7967d647-8ca2-4863-a576-11843e8e8802` (`Lib. Baut. Navarre Vol. 1 (1594-1695)`, NRDL-BAUT-04) strictly asserted: exactly 188 sources, 0 modifications.
  - 4 Ensenada Legos notebooks (`ec86de71-...` [87], `407d5cb4-...` [28], `e7fba70b-...` [51], `cd72ef58-...` [34]) asserted: exactly 200 sources total, 0 modifications.
  - Pre-execution and post-execution automated shield check fails with `RuntimeError` if any preserved notebook is altered.
- **E2E Independent Verification & Forensic Audit**:
  - Out-of-band verification script `scripts/verify_nrdl_parroquial_sources.py` queries live NotebookLM API.
  - Validates 15 notebooks exist, each contains exact expected source count (total 2,276), exact naming format `^\d{9}_\d{5}\.jpg$` [L-28], 100% `READY` status (0 ERROR, 0 PENDING), and preserved notebooks shield intact.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | F1: BOM-Safe Catalog Filtering | Filter records by `cuaderno_asignado_id` from `catalogo_corpus.json` (utf-8-sig), safely handling range interleaving | M1 | Survey |
| 2 | F2: Physical Disk Asset Validation | Verify presence of all 2,276 JPG files on disk under `imagenes/rollo 004306112` and `rollo 004306113` | M1 | Survey |
| 3 | F3: Preserved Notebooks Shield Barrier | Assert 5 existing notebooks (388 sources total) remain untouched and collision-free | M1 & M2 | Survey |
| 4 | F4: Idempotent 15-Notebook Creation | Create/resolve 15 canonical notebooks in NotebookLM without creating duplicates | M1 | Survey |
| 5 | F5: Dual-Tier Checkpointed Ingestion Pipeline | Implement `scripts/ingest_navarredondilla_parroquial.py` with JSON state file and remote sync, ingesting 2,276 images | M1 | Survey |
| 6 | F6: E2E Verification Test Harness | Implement `scripts/verify_nrdl_parroquial_sources.py` verifying all 15 notebooks, 2,276 sources READY, and 0 defects | M2 | Survey |
| 7 | F7: Adversarial Verification & Forensic Audit | Challenger tests and Forensic Integrity Audit confirming 0 dummy stubs, genuine uploads, and clean verdict | M2 | Survey |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | M1: Parochial Ingestion Pipeline & Live Upload | Implement `scripts/ingest_navarredondilla_parroquial.py`, test pilot, execute upload of 2,276 images to 15 notebooks, verify READY | Survey | DONE |
| 2 | M2: E2E Independent Verification & Forensic Audit | Implement `scripts/verify_nrdl_parroquial_sources.py`, execute independent verification, adversarial checks, and Forensic Audit | M1 | DONE |

## Interface Contracts
### Catalog Parser ↔ Ingestion Engine
- Input: `catalogo_corpus.json` (BOM UTF-8)
- Filter: `r.get("cuaderno_asignado_id") == notebook_title`
- Output: List of records `{ "id_imagen": str, "rollo_dgs": str, "fotograma_numero": int, "path": Path }`

### Checkpoint Manager ↔ Ingestion Loop
- State File: `scripts/ingest_checkpoint_nrdl.json`
- Schema:
  ```json
  {
    "notebook_ids": { "<title>": "<id>" },
    "completed_notebooks": ["<title>"],
    "uploaded_sources": {
      "<id_imagen>": {
        "notebook_title": "<title>",
        "notebook_id": "<id>",
        "source_id": "<id>",
        "status": "PROCESSING",
        "timestamp": "<iso>"
      }
    }
  }
  ```
- Ingestion Loop checks both local checkpoint and live `client.sources.list(notebook_id)`.

### Verification Harness ↔ NotebookLM Live API
- Verification Script: `scripts/verify_nrdl_parroquial_sources.py`
- Queries: `client.notebooks.list()` and `client.sources.list(notebook_id)`
- Asserts:
  1. Exactly 15 target notebooks present with canonical titles.
  2. Exactly 2,276 sources across the 15 notebooks matching catalog counts.
  3. All source filenames match `^\d{9}_\d{5}\.jpg$`.
  4. 100% of sources in `READY` status.
  5. Protected notebooks (7967d647-8ca2-4863-a576-11843e8e8802 and 4 Ensenada Legos) have exactly their original source counts (188, 87, 28, 51, 34).
  6. Exit code 0 on complete pass, 1 on failure.

## Code Layout
- Ingestion Script: `scripts/ingest_navarredondilla_parroquial.py`
- Ingestion State/Log: `scripts/ingest_checkpoint_nrdl.json`, `scripts/ingest_navarredondilla_parroquial.log`
- Verification Script: `scripts/verify_nrdl_parroquial_sources.py`
- Verification Report: `scripts/verification_report_nrdl.json`
