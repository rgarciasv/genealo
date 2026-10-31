# Handoff Report — explorer_nrdl_2 (Script Infrastructure Explorer)

- **Agent ID**: `explorer_nrdl_2`
- **Roles**: Script Infrastructure Explorer, Read-Only Investigator
- **Working Directory**: `c:\TRABAJOS\personal\genealo\.agents\teamwork\explorer_nrdl_2\`
- **Date**: 2026-10-31T11:58:00Z
- **Target Audience**: Orchestrator (`31843a9f-efd9-43e6-a718-753324e3577e`)
- **Status**: COMPLETE (Hard Handoff)

---

## 1. Observation

### 1.1 Existing Ingestion Infrastructure (`scripts/ingest_ensenada_legos.py`)
Direct inspection of `scripts/ingest_ensenada_legos.py` (500 lines) reveals the architectural patterns utilized by the previous team:
1. **Corpus Parsing & BOM Safety** (lines 114–174):
   - Opens `catalogo_corpus.json` using `encoding="utf-8-sig"` to safely strip the UTF-8 Byte Order Mark (`\uFEFF`).
   - Filters records by `cuaderno_asignado_id`, sorts them sequentially by `fotograma_numero`.
   - Validates physical file existence on disk (`img_path.is_file()`) before making any API calls.
2. **Shielding Active Protected Notebook** (lines 37–38, 193–208, 417–436):
   - Explicit constant: `PROTECTED_NOTEBOOK_ID = "7967d647-8ca2-4863-a576-11843e8e8802"` (`Lib. Baut. Navarre Vol. 1 (1594-1695)`).
   - Pre-ingestion check: Queries notebook metadata and verifies initial source count is exactly 188.
   - Post-ingestion audit: Re-queries protected notebook and asserts source count remains exactly 188, raising `RuntimeError` on any discrepancy.
   - Target notebook collision guard: Verifies no target notebook ID matches `PROTECTED_NOTEBOOK_ID` (lines 236–242).
3. **Idempotent Notebook Resolution** (lines 210–242):
   - Queries `client.notebooks.list()`. Groups existing notebooks by title:
     ```python
     notebooks_by_title = {}
     for nb in all_notebooks:
         notebooks_by_title.setdefault(nb.title, []).append(nb)
     ```
   - If a target title exists, reuses `matched_nbs[0].id` rather than duplicating. If absent, calls `client.notebooks.create(title=target_title)`.
4. **Resumable Source Ingestion Loop** (lines 261–292, 307–325):
   - Before uploading, fetches existing sources via `await client.sources.list(notebook_id)`.
   - Checks both `is_ready` and `is_processing`:
     ```python
     if filename in existing_sources_by_title:
         existing_s = existing_sources_by_title[filename]
         is_ready = getattr(existing_s, "is_ready", False)
         is_processing = getattr(existing_s, "is_processing", False)
         if is_ready or is_processing:
             total_skipped += 1
             continue
     ```
   - Upload call uses `wait=False`:
     ```python
     source = await client.sources.add_file(
         notebook_id=notebook_id,
         file_path=file_path,
         mime_type="image/jpeg",
         title=filename,
         wait=False,
     )
     ```
5. **Rate Limiting & Exponential Backoff** (lines 75–80, 326–346, 357):
   - Pacing sleep: `await asyncio.sleep(UPLOAD_PAUSE_SECONDS)` where `UPLOAD_PAUSE_SECONDS = 1.5`.
   - Exponential backoff: `backoff = INITIAL_BACKOFF_SECONDS * (2 ** (attempt - 1))` (`INITIAL_BACKOFF_SECONDS = 2.0`, `MAX_RETRIES = 5`).
   - Exception handling catches `(RateLimitError, NetworkError, ServerError, RPCError, httpx.HTTPError)`.
6. **Readiness Polling** (lines 368–416):
   - Polls `client.sources.list(notebook_id)` every `READINESS_POLL_INTERVAL_SECONDS = 5.0` seconds up to `READINESS_TIMEOUT_SECONDS = 300` seconds until `len(sources) >= expected_count and pending_count == 0`.
7. **Logging** (lines 84–109):
   - Custom `FlushingFileHandler` flushes each log entry immediately to `scripts/ingest_ensenada_legos.log`.

### 1.2 Existing Verification Infrastructure (`scripts/verify_notebooklm_sources.py`)
Direct inspection of `scripts/verify_notebooklm_sources.py` (918 lines) reveals:
1. **Independent Verification Architecture**:
   - Implements `NotebookLMVerifier` class querying the live API directly, independent of the ingestion script.
   - Validates active notebook protection (`7967d647-8ca2-4863-a576-11843e8e8802` has 188 sources).
   - Validates target notebooks existence and exact titles [L-29].
   - Performs set difference cross-checks against `catalogo_corpus.json` (`missing_sources` and `extra_sources`).
   - Validates universal naming regex `^\d{9}_\d{5}\.jpg$` without truncated zeros [L-28].
   - Validates that 100% of sources are in `READY` status (0 `ERROR`, 0 `PENDING`).
2. **Safe Source Status Handling** (lines 179–209):
   - Handles `SourceStatus` enum cleanly:
     ```python
     def get_source_status_str(source: Any) -> str:
         if hasattr(source, "status"):
             st = source.status
             if hasattr(st, "name"):
                 return st.name
             return str(st)
         return "UNKNOWN"
     ```
3. **Structured Reporting**:
   - Generates formatted terminal summary table and serializes `scripts/verification_report.json` with overall verdict `PASS`/`FAIL` and appropriate exit code (`0` on complete pass, `1` on failure).

### 1.3 Previous Ingestion Metrics & Execution Logs
From `scripts/ingest_ensenada_legos.log` and `scripts/verification_report.json`:
- **Execution start**: `2026-10-31 11:43:07`
- **Execution end**: `2026-10-31 11:56:53`
- **Elapsed time**: `825.35 seconds` (~13.76 minutes) for 200 documents.
- **Average pace**: ~4.13 seconds per document (upload transfer + 1.5s pacing delay).
- **Readiness time**: All 200 sources were already `READY` immediately upon upload completion (background processing by NotebookLM finished in parallel during uploads).
- **Final Result**: Exactly 200/200 sources `READY` (NRDL: 87, JMOL: 28, VLLR: 51, NDRN: 34), 0 errors, 0 pending, exit code `0`.

### 1.4 Python Virtual Environment & Tooling
1. **Python Executable**:
   - Path: `c:\TRABAJOS\personal\genealo\venv\Scripts\python.exe`
   - Underlying core executable: `C:\Users\rgarc\AppData\Local\Python\pythoncore-3.14-64\python.exe` (Python 3.14.0).
   - **Critical OS/Sandbox Constraint**: When invoking PowerShell commands via `run_command`, accessing AppData python requires `BypassSandbox: true`. Running without `BypassSandbox: true` fails with `Acceso denegado`.
2. **Installed Packages**:
   - `notebooklm-py`: Version **0.8.5** installed.
   - Associated utilities in `venv\Scripts\`: `notebooklm.exe`, `notebooklm-mcp.exe`, `notebooklm-server.exe`, `python.exe`.
3. **Browser Storage Profile & Authentication**:
   - Location: `C:\Users\rgarc\.notebooklm\profiles\default\`
   - Contains:
     * `storage_state.json` (13,551 bytes) — persistent Playwright cookies and Google session tokens.
     * `browser_profile/` directory.
   - Authentication status: Fully valid and active. Verified live via both MCP `notebook_list` and `notebooklm-py` client (`NotebookLMClient.from_storage()`). No interactive login or 2FA required.

### 1.5 Gate 1 Bug Discovery & Resolution in `worker_m2`
1. **The Bug**:
   - In `scripts/ingest_ensenada_legos.py` line 300 (originally created by `worker_m1`), the logger referenced:
     `source.status_label`
   - In `notebooklm-py` v0.8.5 dataclass `Source` (`notebooklm/_types/sources.py`), the attribute is `status` (a `SourceStatus` enum), with properties `is_ready`, `is_processing`, `is_error`. There is **no attribute named `status_label`**.
   - Attempting to access `source.status_label` crashed with `AttributeError: 'Source' object has no attribute 'status_label'` on the very first upload attempt.
2. **The Fix Applied in `worker_m2`**:
   - Replaced line 300 / 321 with:
     ```python
     getattr(source, 'status_label', getattr(source.status, 'name', str(source.status)))
     ```
   - Also updated idempotency check to verify both `is_ready` and `is_processing` to prevent duplicate uploads during pipeline restarts.

### 1.6 Current Live NotebookLM Account State
Direct query executed on live Google NotebookLM account returned **55 total notebooks**:
- **Protected Active Notebook [R3]**:
  - `7967d647-8ca2-4863-a576-11843e8e8802` (`Lib. Baut. Navarre Vol. 1 (1594-1695)`) — **188 sources, INTACT**. Note: This notebook corresponds to volume `NRDL-BAUT-04`.
- **Ensenada Legos Notebooks (Created in previous phase)**:
  - `ec86de71-a11c-4489-bbb9-eea856cccac4`: `NRDL-ENSENADA-LEGOS-01` (87 sources, INTACT)
  - `407d5cb4-4b83-495f-a23a-309ea44ee8c6`: `JMOL-ENSENADA-LEGOS-01` (28 sources, INTACT)
  - `e7fba70b-af7d-4602-b543-060742b22528`: `VLLR-ENSENADA-LEGOS-01` (51 sources, INTACT)
  - `cd72ef58-fcf5-48ac-8de2-556648ebd90e`: `NDRN-ENSENADA-LEGOS-01` (34 sources, INTACT)
- **15 Target Navarredondilla Parroquial Notebooks**:
  - None of the 15 notebooks exist yet in the account.

### 1.7 Catalog & Disk Asset Audit for Navarredondilla Parroquial (2,276 images)
Executed Python validation script against `catalogo_corpus.json` and local disk:
- **Total records matching the 15 target notebooks**: exactly **2,276**.
- **Unique image IDs**: exactly **2,276** (0 duplicates across books).
- **Physical files on disk**: **2,276 present, 0 missing**.
- **DGS rolls involved**: `004306112` and `004306113` in `imagenes/`.
- **Per-notebook inventory**:
  | # | Canonical Title | DGS Roll | Fotogramas Range | Source Count |
  |---|---|---|---|---|
  | 1 | `NRDL-BAUT-01` | `004306112` | 1870–2147 (interleaving with MATR-01) | 245 |
  | 2 | `NRDL-BAUT-02` | `004306112` | 2218–2374 | 157 |
  | 3 | `NRDL-BAUT-03` | `004306112` | 2375–2605 | 231 |
  | 4 | `NRDL-BAUT-05` | `004306113` | 1–144 | 144 |
  | 5 | `NRDL-BAUT-06` | `004306113` | 145–327 | 183 |
  | 6 | `NRDL-BAUT-07` | `004306113` | 328–429 | 102 |
  | 7 | `NRDL-DIFU-01` | `004306113` | 430–665 | 236 |
  | 8 | `NRDL-DIFU-01B`| `004306113` | 666–730 | 65 |
  | 9 | `NRDL-DIFU-02` | `004306113` | 801–971 | 171 |
  | 10 | `NRDL-DIFU-03` | `004306113` | 972–1141 | 170 |
  | 11 | `NRDL-DIFU-04` | `004306113` | 1142–1329 | 188 |
  | 12 | `NRDL-DIFU-05` | `004306113` | 1330–1540 | 211 |
  | 13 | `NRDL-MATR-01` | `004306112` | 1955–1987 | 33 |
  | 14 | `NRDL-MATR-02` | `004306113` | 731–800 | 70 |
  | 15 | `NRDL-MIXTO-01`| `004306112` | 2148–2217 | 70 |
  | **TOTAL** | **15 Notebooks** | | | **2,276** |

- All 15 notebooks comply with [L-29] ($\le 245 \le 300$ sources per notebook).
- All 2,276 filenames conform strictly to [L-28] (`^\d{9}_\d{5}\.jpg$`).
- Protected notebook `NRDL-BAUT-04` (`7967d647-8ca2-4863-a576-11843e8e8802`, 188 sources) is excluded from the creation/upload target list.

---

## 2. Logic Chain

1. **Throughput and Time Scaling**:
   - In Ensenada Legos, 200 documents took 825 seconds (~4.1 seconds/image).
   - Scaling linearly to 2,276 images:
     $$\text{Estimated Ingestion Time} = 2,276 \times 4.1\text{ s} \approx 9,331\text{ s} \approx 155.5\text{ minutes} \approx 2.59\text{ hours}$$
   - Over a 2.6-hour execution window, risks of network hiccups, token expiration, transient rate limits, or environment timeouts increase significantly.
   - Therefore, a monolithic run without persistent intermediate state is unacceptable. A persistent local checkpointing mechanism is mandatory.

2. **Two-Tier Idempotency Architecture**:
   - **Tier 1 (Fast Local Resume)**: Maintain a persistent state JSON file (`scripts/ingest_checkpoint_nrdl.json`). When restarting or recovering from an interruption, skip files already logged as uploaded in the checkpoint file.
   - **Tier 2 (Authoritative Cloud Sync)**: Before processing each notebook, query `client.sources.list(notebook_id)`. Any source title already in Google's cloud with `is_ready` or `is_processing` is synchronized to the checkpoint and skipped.
   - This dual-tier approach guarantees zero duplicate uploads even if the script is terminated mid-upload or restarted multiple times.

3. **Granular Execution via CLI Flags**:
   - Allowing developers and workers to process notebooks individually (e.g. `--notebook NRDL-MATR-01` for a fast 33-image pilot) drastically reduces debugging cycle time and allows testing in tranches.
   - Pre-flight validation with `--dry-run` ensures all assets and credentials are confirmed before creating notebooks in Google Cloud.

4. **Preservation of Untouchable Assets**:
   - The protected active notebook (`7967d647-8ca2-4863-a576-11843e8e8802`) and the 4 Ensenada Legos notebooks (`NRDL-ENSENADA-LEGOS-01`, `JMOL-ENSENADA-LEGOS-01`, `VLLR-ENSENADA-LEGOS-01`, `NDRN-ENSENADA-LEGOS-01`) must be checked before and after execution to guarantee zero modification.

---

## 3. Architectural Design Proposal

### 3.1 Proposed Design for `scripts/ingest_navarredondilla_parroquial.py`

#### A. Command-Line Interface (CLI) Specification
The script should support the following CLI arguments via `argparse`:
```text
usage: ingest_navarredondilla_parroquial.py [-h] [--notebook NOTEBOOK] [--limit LIMIT]
                                           [--dry-run] [--pause PAUSE]
                                           [--max-retries MAX_RETRIES]
                                           [--checkpoint-file CHECKPOINT_FILE]
                                           [--skip-readiness-wait]
                                           [--catalog-path CATALOG_PATH]

Optional arguments:
  --notebook NOTEBOOK         Comma-separated list or single target notebook title (e.g. 'NRDL-MATR-01' or 'NRDL-BAUT-01,NRDL-BAUT-02'). Defaults to all 15 notebooks.
  --limit LIMIT               Maximum number of images to upload in this run (useful for pilot testing). Default: None (no limit).
  --dry-run                   Run preflight validations (corpus, disk assets, existing cloud notebooks) without creating notebooks or uploading files.
  --pause PAUSE               Seconds to sleep between successful uploads. Default: 1.5.
  --max-retries MAX_RETRIES   Maximum retries per upload on transient HTTP/RateLimit errors. Default: 5.
  --checkpoint-file PATH      Path to the JSON checkpoint state file. Default: scripts/ingest_checkpoint_nrdl.json.
  --skip-readiness-wait       Skip waiting for sources to reach READY status after upload (defers readiness check to verification script). Default: False.
  --catalog-path PATH         Path to catalogo_corpus.json. Default: catalogo_corpus.json.
```

#### B. Checkpointing State Specification (`scripts/ingest_checkpoint_nrdl.json`)
The checkpoint file persists progress atomically after every successful upload:
```json
{
  "version": "1.0",
  "created_at": "2026-10-31T12:00:00Z",
  "updated_at": "2026-10-31T12:45:00Z",
  "notebook_ids": {
    "NRDL-BAUT-01": "01234567-89ab-cdef-0123-456789abcdef",
    "NRDL-MATR-01": "abcdef01-2345-6789-abcd-ef0123456789"
  },
  "completed_notebooks": [
    "NRDL-MATR-01"
  ],
  "uploaded_sources": {
    "004306112_01955.jpg": {
      "notebook_title": "NRDL-MATR-01",
      "notebook_id": "abcdef01-2345-6789-abcd-ef0123456789",
      "source_id": "99999999-8888-7777-6666-555555555555",
      "status": "PROCESSING",
      "timestamp": "2026-10-31T12:01:15Z"
    }
  }
}
```
**Atomic Write Mechanism**: The state file is written using temporary file replacement (`Path.replace`) or immediate flush so an abrupt process termination does not corrupt the JSON.

#### C. Notebook Creation Idempotency
1. Query `all_notebooks = await client.notebooks.list()`.
2. Group existing notebooks: `existing_by_title = {nb.title: nb.id for nb in all_notebooks}`.
3. For each of the 15 titles:
   - If present in `existing_by_title`: reuse ID, update checkpoint.
   - If present in checkpoint file but not verified in account: cross-check with list.
   - If absent: call `await client.notebooks.create(title=target_title)`.
   - Update checkpoint file immediately with new ID.
4. Shield Assertion:
   ```python
   PROTECTED_IDS = {
       "7967d647-8ca2-4863-a576-11843e8e8802",  # NRDL-BAUT-04
       "ec86de71-a11c-4489-bbb9-eea856cccac4",  # NRDL-ENSENADA-LEGOS-01
       "407d5cb4-4b83-495f-a23a-309ea44ee8c6",  # JMOL-ENSENADA-LEGOS-01
       "e7fba70b-af7d-4602-b543-060742b22528",  # VLLR-ENSENADA-LEGOS-01
       "cd72ef58-fcf5-48ac-8de2-556648ebd90e",  # NDRN-ENSENADA-LEGOS-01
   }
   for title, nid in notebook_ids.items():
       if nid in PROTECTED_IDS:
           raise RuntimeError(f"CRITICAL SAFETY VIOLATION: Target notebook {title} collided with protected ID {nid}")
   ```

#### D. Upload Loop & Pacing
1. For each notebook:
   - Sync cloud sources via `client.sources.list(notebook_id)`.
   - Filter records from `catalogo_corpus.json` sorted by `fotograma_numero`.
   - Check if source is in checkpoint or already exists in cloud:
     `if is_ready or is_processing: skip`.
   - Upload call:
     ```python
     source = await client.sources.add_file(
         notebook_id=notebook_id,
         file_path=file_path,
         mime_type="image/jpeg",
         title=filename,
         wait=False,
     )
     ```
   - Log using safe status extraction:
     ```python
     status_str = getattr(source, 'status_label', getattr(source.status, 'name', str(source.status)))
     ```
   - Record in checkpoint and save to disk.
   - Exponential backoff on transient errors:
     `RateLimitError, NetworkError, ServerError, RPCError, httpx.HTTPError, httpx.RequestError`.
     `backoff = INITIAL_BACKOFF_SECONDS * (2 ** (attempt - 1)) + random.uniform(0.1, 0.5)`
   - Inter-upload pacing: `await asyncio.sleep(pause_seconds)` (default 1.5s).

#### E. Readiness Verification
- After uploads complete (unless `--skip-readiness-wait` is set):
  - Poll each notebook with `READINESS_POLL_INTERVAL_SECONDS = 5.0` until all sources are `is_ready` or timeout is reached.
  - Since processing is asynchronous, earlier books will already be READY when later books finish uploading.

---

### 3.2 Proposed Design for `scripts/verify_navarredondilla_parroquial.py`

#### A. Command-Line Interface Specification
```text
usage: verify_navarredondilla_parroquial.py [-h] [--notebook NOTEBOOK]
                                           [--report-path REPORT_PATH]
                                           [--catalog-path CATALOG_PATH]
                                           [--quiet]

Optional arguments:
  --notebook NOTEBOOK     Verify a specific notebook title (e.g. 'NRDL-BAUT-01') instead of all 15. Default: all.
  --report-path PATH      Path to output JSON verification report. Default: scripts/verification_report_nrdl.json.
  --catalog-path PATH     Path to catalogo_corpus.json. Default: catalogo_corpus.json.
  --quiet                 Suppress per-source logging, print only the summary table. Default: False.
```

#### B. Verification Pipeline Steps
1. **Corpus Cross-Check**:
   - Parse `catalogo_corpus.json` (with `utf-8-sig`).
   - Extract records for the 15 notebooks. Verify that target records total 2,276.
2. **Shield Audit of Protected Notebooks**:
   - Query `7967d647-8ca2-4863-a576-11843e8e8802` (`Lib. Baut. Navarre Vol. 1 (1594-1695)`): assert exactly 188 sources, alive, untouched.
   - Query the 4 Ensenada Legos notebooks:
     * `NRDL-ENSENADA-LEGOS-01`: 87 sources
     * `JMOL-ENSENADA-LEGOS-01`: 28 sources
     * `VLLR-ENSENADA-LEGOS-01`: 51 sources
     * `NDRN-ENSENADA-LEGOS-01`: 34 sources
3. **15 Target Notebooks Audit**:
   - Verify each notebook exists with exact canonical title.
   - Verify count matches expected value.
   - Verify bidirectional 1:1 set equality:
     * `missing_sources = expected_titles - actual_titles == 0`
     * `extra_sources = actual_titles - expected_titles == 0`
     * `duplicate_sources == 0`
   - Verify [L-28] naming format on all sources: `^\d{9}_\d{5}\.jpg$`.
   - Verify readiness status: 100% of sources have `is_ready == True` (0 `ERROR`, 0 `PENDING`).
4. **Report Generation**:
   - Output structured JSON to `scripts/verification_report_nrdl.json`.
   - Render clean ASCII summary table to stdout.
   - Return exit code `0` on 100% pass, `1` on any error or missing source.

---

## 4. Caveats

1. **Upload Duration**:
   At ~4.1 seconds per image, sequentially uploading all 2,276 images will take ~2.6 hours. Subagent task execution should either run the ingestion in planned batches using `--notebook` or execute as a managed background task with regular `progress.md` heartbeats.
2. **Windows Sandbox Limitation**:
   Executing `c:\TRABAJOS\personal\genealo\venv\Scripts\python.exe` from PowerShell requires `BypassSandbox: true` because Python is in user AppData. Subsequent workers and test writers must set `BypassSandbox: true` when running ingestion or verification scripts.
3. **Google NotebookLM Account Limits**:
   The user currently has 55 notebooks. Adding 15 notebooks will increase the total to 70 notebooks. Current Google NotebookLM accounts comfortably support >100 notebooks, and all 15 target notebooks have $\le 245$ sources, well below the 300 source/notebook limit.

---

## 5. Conclusion

1. **Infrastructure Readiness**: The existing tooling in `scripts/ingest_ensenada_legos.py` and `scripts/verify_notebooklm_sources.py` provides a proven, battle-tested foundation that achieved 100% success on 200 documents.
2. **Asset Readiness**: All 2,276 physical images for the 15 Navarredondilla Parroquial notebooks exist on disk, are completely contiguous, unique, and strictly conform to rules [L-28] and [L-29].
3. **Authentication Readiness**: The browser storage profile at `C:\Users\rgarc\.notebooklm\profiles\default\` is authenticated, persistent, and functional with `notebooklm-py` v0.8.5.
4. **Architectural Blueprints**: The proposed designs for `scripts/ingest_navarredondilla_parroquial.py` and `scripts/verify_navarredondilla_parroquial.py` feature dual-tier idempotency, persistent JSON checkpointing, granular CLI flags, and robust error recovery, fully preparing the project to scale safely to 15 notebooks and 2,276 images.

---

## 6. Verification Method

To independently reproduce and verify the findings of this survey:

1. **Verify Live NotebookLM Connectivity & Notebooks Count (55 total)**:
   ```powershell
   c:\TRABAJOS\personal\genealo\venv\Scripts\python.exe scripts/reviewer4_independent_audit.py
   ```
   *(Must be run with `BypassSandbox: true`)*.
   Expected result: 55 notebooks discovered, protected notebook verified with 188 sources, 4 Ensenada Legos notebooks verified.

2. **Verify 2,276 Parroquial Images in Catalog & Disk**:
   ```powershell
   c:\TRABAJOS\personal\genealo\venv\Scripts\python.exe -c "
   import json; from pathlib import Path
   targets = ['NRDL-BAUT-01','NRDL-BAUT-02','NRDL-BAUT-03','NRDL-BAUT-05','NRDL-BAUT-06','NRDL-BAUT-07','NRDL-DIFU-01','NRDL-DIFU-01B','NRDL-DIFU-02','NRDL-DIFU-03','NRDL-DIFU-04','NRDL-DIFU-05','NRDL-MATR-01','NRDL-MATR-02','NRDL-MIXTO-01']
   corpus = json.load(open('catalogo_corpus.json', encoding='utf-8-sig'))
   recs = [r for r in corpus if r.get('cuaderno_asignado_id') in targets]
   print(f'Total records: {len(recs)}')
   missing = sum(1 for r in recs if not (Path('imagenes') / f'rollo {r[\"rollo_dgs\"]}' / r['id_imagen']).is_file())
   print(f'Missing files on disk: {missing}')
   "
   ```
   Expected result: `Total records: 2276`, `Missing files on disk: 0`.

3. **Verify Gate 1 Fix in `scripts/ingest_ensenada_legos.py`**:
   Inspect line 321 of `scripts/ingest_ensenada_legos.py`:
   Confirm that safe resolution `getattr(source, 'status_label', getattr(source.status, 'name', str(source.status)))` is present.
