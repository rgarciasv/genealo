# Project: Ensenada Legos Notebooks Creation & Ingestion

## Architecture
- Module/package boundaries, data flow, shared interfaces:
  - **Corpus Parser & Validator**: Reads `catalogo_corpus.json` with UTF-8 BOM handling (`utf-8-sig`), extracting the 200 target records for Ensenada Personal de Legos:
    - Navarredondilla (`NRDL-ENSENADA-LEGOS-01`): 87 images
    - San Juan del Molinillo (`JMOL-ENSENADA-LEGOS-01`): 28 images
    - El Villarejo (`VLLR-ENSENADA-LEGOS-01`): 51 images
    - Navandrinal (`NDRN-ENSENADA-LEGOS-01`): 34 images
  - **NotebookLM Client Integration**: Leverages Python virtual environment (`c:\TRABAJOS\personal\genealo\venv\Scripts\python.exe`) with `notebooklm-py` 0.8.5 via persistent browser profile `C:\Users\rgarc\.notebooklm\profiles\default\storage_state.json`. Unattended re-authentication via `venv\Scripts\notebooklm.exe login` with `BypassSandbox: true` [L-21].
  - **Ingestion Pipeline**: Automated creation of the 4 mono-locality notebooks [L-29] and controlled batch upload of 200 JPG images [L-28] with rate-limit backoff, progress logging, and status validation.
  - **E2E Verification & Forensic Integrity**: Independent automated verification harness querying NotebookLM API directly, validating exact counts, naming formats, source statuses, and preservation of active notebook `7967d647-8ca2-4863-a576-11843e8e8802`.

## Feature Inventory
| # | Feature | Description | Milestone | Source |
|---|---------|-------------|-----------|--------|
| 1 | F1: BOM-safe Corpus Parsing | Parse `catalogo_corpus.json` with `utf-8-sig`, extract exactly 200 records across 4 series | M1 | Survey |
| 2 | F2: Physical Image Validation | Validate existence and readability of all 200 files in `imagenes/` with `{DGS}_{FOTOGRAMA}.jpg` [L-28] | M1 | Survey |
| 3 | F3: Mono-locality Notebook Creation | Create 4 notebooks: `NRDL-ENSENADA-LEGOS-01`, `JMOL-ENSENADA-LEGOS-01`, `VLLR-ENSENADA-LEGOS-01`, `NDRN-ENSENADA-LEGOS-01` [L-29] | M1 | Survey |
| 4 | F4: Document Ingestion Pipeline | Upload 200 local JPG images (NRDL: 87, JMOL: 28, VLLR: 51, NDRN: 34) into NotebookLM with batching & retries | M1 | Survey |
| 5 | F5: Active Notebook Shielding | Strict preservation of active notebook `7967d647-8ca2-4863-a576-11843e8e8802` | M1 & M2 | Survey |
| 6 | F6: E2E Test Suite & Test Runner | Independent test suite validating notebooks, source count, status, naming, and active notebook preservation | M2 | Survey |
| 7 | F7: Adversarial Hardening & Forensic Audit | Verification of zero hallucinations, zero dummy stubs, 100% genuine API operations and 0 source errors | M2 | Survey |

## Milestones
| # | Name | Scope | Dependencies | Status |
|---|------|-------|-------------|--------|
| 1 | M1: Notebook Creation & Ingestion | Implement ingestion script and ingest 200 images into 4 notebooks via `notebooklm-py` | none | DONE |
| 2 | M2: E2E Verification & Forensic Audit | Develop verification test harness, verify 100% pass across all 4 notebooks & 200 sources, conduct audit | M1 | DONE |

## Interface Contracts
### Corpus Parser ↔ Ingestion Engine
- Input: `catalogo_corpus.json` (BOM UTF-8)
- Output: Dictionary mapping `cuaderno_id` -> list of records `{ "path": str, "filename": str, "dgs": str, "fotograma": str }`
- Error handling: Raise `FileNotFoundError` or `ValueError` if any file or attribute is missing.

### Ingestion Engine ↔ NotebookLM Client
- Client: `NotebookLMClient.from_storage()`
- Notebook Creation: `client.notebooks.create(title=notebook_name)` -> returns `notebook` with `id`
- Source Upload: `client.sources.add_file(notebook_id, file_path)` -> uploads local JPG image
- Resilience: Micro-batches with pacing (1-2s delay) to respect API rate limits.

### E2E Verifier ↔ NotebookLM API
- Query: `client.notebooks.list()` and `client.sources.list(notebook_id)`
- Validation criteria:
  1. Notebooks exist with exact names.
  2. Exactly 200 sources distributed across notebooks (87, 28, 51, 34).
  3. Source titles match `{DGS}_{FOTOGRAMA}.jpg` without zero truncation.
  4. Processing status is `READY` or equivalent success state.
  5. Protected notebook `7967d647-8ca2-4863-a576-11843e8e8802` remains unaltered.

## Code Layout
- Implementation: `scripts/ingest_ensenada_legos.py`
- Verification: `scripts/verify_notebooklm_sources.py`
- Log/Artifacts: `scripts/ingest_ensenada_legos.log`, `scripts/verification_report.json`
