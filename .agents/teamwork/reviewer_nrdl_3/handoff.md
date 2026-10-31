# Handoff & Quality / Adversarial Review Report — Reviewer 3

- **Agent ID**: `reviewer_nrdl_3` (Ingestion Pipeline Reviewer & Adversarial Critic)
- **Roles**: Reviewer, Critic
- **Working Directory**: `c:\TRABAJOS\personal\genealo\.agents\teamwork\reviewer_nrdl_3\`
- **Date**: 2026-10-31T13:53:00Z
- **Target Audience**: Orchestrator (`31843a9f-efd9-43e6-a718-753324e3577e`)
- **Status**: COMPLETE (Hard Handoff)
- **Reviewed Work Product**: Navarredondilla Parroquial Ingestion Pipeline:
  - `scripts/ingest_navarredondilla_parroquial.py` (708 lines)
  - `scripts/ingest_checkpoint_nrdl.json` (atomic state)
  - `scripts/ingest_navarredondilla_parroquial.log` (5,228 lines)
  - Pilot notebook live in Google NotebookLM (`1e6fec74-1e2f-4dd7-8ad1-6d25411de127`)
- **Verdict**: **APPROVE**

---

## Executive Review Summary

**Verdict**: **APPROVE**

The Navarredondilla parochial ingestion engine (`scripts/ingest_navarredondilla_parroquial.py`) is exceptionally well-engineered, robust, and mathematically sound. It adheres to all project rules:
1. **Rule [L-28]**: Enforces regex `^\d{9}_\d{5}\.jpg$` and exact length 19 (zero-padding truncation prevention).
2. **Rule [L-29]**: Enforces mono-locality notebooks, each strictly $\le 245$ sources ($\le 300$ limit).
3. **Corpus & Range Interleaving**: Uses `utf-8-sig` BOM handling and filters strictly by `cuaderno_asignado_id`, properly handling the range interleaving of `NRDL-MATR-01` (fotogramas 1955–1987) embedded within `NRDL-BAUT-01` (fotogramas 1870–2147).
4. **Active Preserved Shield**: Pre- and post-execution assertions strictly protect all 5 pre-existing notebooks (1 sacramental + 4 Ensenada Legos; exactly 388 sources) and enforce collision guards against ID reuse.
5. **Dual-Tier Checkpointing**: Combines local atomic JSON persistence (`scripts/ingest_checkpoint_nrdl.json` with `.tmp` + `os.fsync` + `os.replace`) with live remote sync via `client.sources.list(notebook_id)`.
6. **Pilot Ingestion Empirical Pass**: Independent live query via the `notebooklm` MCP server confirmed notebook `1e6fec74-1e2f-4dd7-8ad1-6d25411de127` exists, contains exactly 33 sources, and 100% (33/33) are in `READY` status.
7. **Adversarial / Integrity Forensics**: Zero cheating, zero hardcoded pass mocks, zero circumvention of the user's elevation denial dialog. Checkpoint is clean and ready to resume from `NRDL-BAUT-01` with 0 duplicate uploads.

---

## 1. Observation

### 1.1 Source Code Architecture (`scripts/ingest_navarredondilla_parroquial.py`)
Direct code inspection reveals complete implementation across all architectural dimensions:
1. **BOM Safety & Range Interleaving** (lines 194–260):
   - Opens `catalogo_corpus.json` with `encoding="utf-8-sig"` (line 202).
   - Filters strictly by `r.get("cuaderno_asignado_id") == title` (line 213).
   - In rollo `004306112`, `NRDL-BAUT-01` spans fotogramas 1870–2147 but skips fotogramas 1955–1987. Line 263-264 of the execution log confirms that `NRDL-BAUT-01` uploads fotograma 01954 (record 85/245) and immediately jumps to 01988 (record 86/245). The intervening 33 fotogramas (01955–01987) are correctly isolated into `NRDL-MATR-01`.
   - Validates regex `^\d{9}_\d{5}\.jpg$` and `len(id_img) == 19` (lines 236–244).
   - Validates physical file existence and non-zero byte size on disk (lines 252–256).
2. **Preserved Notebooks Hard Shield** (lines 44–65, 264–296, 404–409, 584–592):
   - Asserts all 5 preserved notebooks:
     * `7967d647-8ca2-4863-a576-11843e8e8802` (`Lib. Baut. Navarre Vol. 1 (1594-1695)`): 188 sources.
     * `ec86de71-a11c-4489-bbb9-eea856cccac4` (`NRDL-ENSENADA-LEGOS-01`): 87 sources.
     * `407d5cb4-4b83-495f-a23a-309ea44ee8c6` (`JMOL-ENSENADA-LEGOS-01`): 28 sources.
     * `e7fba70b-af7d-4602-b543-060742b22528` (`VLLR-ENSENADA-LEGOS-01`): 51 sources.
     * `cd72ef58-fcf5-48ac-8de2-556648ebd90e` (`NDRN-ENSENADA-LEGOS-01`): 34 sources.
     * Total: 388 sources.
   - Raises `RuntimeError` immediately if source counts deviate before or after ingestion.
   - Raises `RuntimeError` if any target notebook resolves to an ID in `PROTECTED_NOTEBOOKS` (lines 404–408).
3. **Dual-Tier Checkpointing & Idempotency** (lines 125–190, 430–477, 504–506):
   - **Tier 1 (Local Checkpoint)**: `CheckpointManager` records state atomically via `.tmp` file, `flush()`, `os.fsync()`, and `os.replace()`. It saves after every single source upload (line 505).
   - **Tier 2 (Cloud Remote Sync)**: Queries `client.sources.list(notebook_id)` before uploading. If a file is in Google Cloud with `is_ready` or `is_processing`, it updates the checkpoint and skips upload (lines 462–476).
4. **Transient Error Resilience**:
   - `UPLOAD_PAUSE_SECONDS = 1.5` between uploads (line 88, line 529).
   - `MAX_RETRIES = 5` with exponential backoff: 2s, 4s, 8s, 16s, 32s (line 512).
   - Traps `(RateLimitError, NetworkError, ServerError, RPCError, httpx.HTTPError)` (line 511).
   - Safely resolves source status: `status_str = getattr(source, 'status_label', getattr(source.status, 'name', str(source.status)))` (line 499).

### 1.2 Independent Live Cloud Verification (MCP `notebook_list` & `source_list`)
Reviewer 3 independently queried Google NotebookLM live using the `notebooklm` MCP tools:
1. **Live Notebook Listing (`notebook_list`)**:
   Verbatim output received:
   ```json
   {
     "id": "1e6fec74-1e2f-4dd7-8ad1-6d25411de127",
     "title": "NRDL-MATR-01",
     "created_at": "2026-10-31T12:25:51+00:00",
     "sources_count": 33,
     "is_owner": true,
     "modified_at": "2026-10-31T12:34:53+00:00",
     "role_label": "owner"
   }
   ```
2. **Preserved Notebooks Audit**:
   - `7967d647-8ca2-4863-a576-11843e8e8802`: `sources_count`: 188 (expected: 188)
   - `ec86de71-a11c-4489-bbb9-eea856cccac4`: `sources_count`: 87 (expected: 87)
   - `407d5cb4-4b83-495f-a23a-309ea44ee8c6`: `sources_count`: 28 (expected: 28)
   - `e7fba70b-af7d-4602-b543-060742b22528`: `sources_count`: 51 (expected: 51)
   - `cd72ef58-fcf5-48ac-8de2-556648ebd90e`: `sources_count`: 34 (expected: 34)
   - **Total Preserved**: exactly **388 sources** (100% intact).
3. **Live Source List on `1e6fec74-1e2f-4dd7-8ad1-6d25411de127` (`source_list`)**:
   - Total sources returned: **33**.
   - Filenames: `004306112_01955.jpg` through `004306112_01987.jpg`.
   - Status: All 33 sources have `status_label: "ready"`, `kind: "image"`, `drive_status_label: null`.
   - Source UUIDs match `scripts/ingest_checkpoint_nrdl.json` with 100% precision.

### 1.3 Checkpoint & Log State
1. `scripts/ingest_checkpoint_nrdl.json`:
   - `"notebook_ids"`: `{"NRDL-MATR-01": "1e6fec74-1e2f-4dd7-8ad1-6d25411de127"}`
   - `"completed_notebooks"`: `["NRDL-MATR-01"]`
   - `"uploaded_sources"`: Exactly 33 keys (`004306112_01955.jpg` to `004306112_01987.jpg`).
2. `scripts/ingest_navarredondilla_parroquial.log`:
   - Records successful dry-run (lines 121–5007), verifying all 2,276 records on disk and shield intact.
   - Records live pilot for `NRDL-MATR-01` (lines 5008–5134): 33 uploaded, 33 reached `READY`, shield intact, elapsed time 162.65s.
   - Records live idempotency test for `NRDL-MATR-01` (lines 5135–5227): 0 uploaded, 33 skipped via checkpoint, shield intact, elapsed time 15.95s.

---

## 2. Logic Chain

1. **Requirement Conformance**:
   - The user requested Option A: Ingest 15 notebooks of Navarredondilla parish records (2,276 images) while preserving existing notebooks.
   - The worker implemented `scripts/ingest_navarredondilla_parroquial.py`, conducted preflight validation on all 2,276 images, executed a verified live pilot on `NRDL-MATR-01` (33 images), and tested idempotency.
2. **Correctness of Filtering & Interleaving**:
   - `NRDL-MATR-01` (fotogramas 1955–1987) is physically nestled in the middle of `NRDL-BAUT-01` (fotogramas 1870–2147).
   - By filtering on `cuaderno_asignado_id == title`, `NRDL-BAUT-01` correctly selects 85 fotogramas prior (1870–1954) and 160 fotogramas after (1988–2147), totaling exactly 245 fotogramas.
   - `NRDL-MATR-01` selects the 33 marriage fotogramas without overlap or data contamination.
3. **Preservation & Collision Safety**:
   - Explicit pre- and post-assertions ensure that if any of the 5 preserved notebooks changes even by a single source, execution halts immediately with `RuntimeError`.
   - The collision guard prevents any target notebook from resolving to a protected ID.
   - Live query confirmed all 5 notebooks remain untouched with 388 sources.
4. **Idempotency & Resume Reliability**:
   - The pilot upload completed and committed `NRDL-MATR-01` into `scripts/ingest_checkpoint_nrdl.json`.
   - When the user denied elevated execution for the full 2.5-hour run, the worker respected the choice without attempting circumvention.
   - Because `NRDL-MATR-01` is recorded as completed and all 33 files are in `uploaded_sources`, resuming execution will immediately skip `NRDL-MATR-01` and upload only the remaining 14 notebooks (2,243 sources).
5. **Quality & Adversarial Audit**:
   - All code is genuine production logic using `notebooklm-py` and `httpx`.
   - No hardcoded test responses, dummy functions, or bypass flags exist in the ingestion script.
   - The verdict is firmly APPROVE.

---

## 3. Caveats

1. **Unsandboxed Execution & User Denial**:
   Automated subagents running in Windows cannot run the ~2.5-hour ingestion pipeline without `BypassSandbox: true`. When the worker attempted this command, the user declined permission. Therefore, the remaining 14 notebooks (2,243 sources) have not yet been uploaded to Google Cloud.
2. **Execution Duration for Remaining Batch**:
   Uploading 2,243 sources at ~4.1 seconds per source will require approximately **2.5 hours** of continuous execution.
3. **Session Cookie Expiration**:
   Google NotebookLM session cookies in `storage_state.json` expire periodically. If the session expires during the 2.5-hour run, the script will exit cleanly, and the user simply needs to run `notebooklm login` in PowerShell and restart the script; the checkpoint guarantees zero duplication upon restart.

---

## 4. Conclusion

`scripts/ingest_navarredondilla_parroquial.py`, the checkpoint state `scripts/ingest_checkpoint_nrdl.json`, and the live pilot `NRDL-MATR-01` (`1e6fec74-1e2f-4dd7-8ad1-6d25411de127`) meet all quality, architectural, and security requirements with 0 defects.

**VERDICT**: **APPROVE**

---

## 5. Verification Method

To independently verify these findings and resume the ingestion:

1. **Verify Live Status of Pilot Notebook (`NRDL-MATR-01`) via MCP**:
   Call `call_mcp_tool` with `ServerName: "notebooklm"`, `ToolName: "source_list"`, `Arguments: {"notebook": "1e6fec74-1e2f-4dd7-8ad1-6d25411de127", "detail": "compact"}`.
   Observe: 33 sources returned, all matching `004306112_01955.jpg`..`004306112_01987.jpg`, all with `status_label: "ready"`.

2. **Verify Checkpoint File**:
   Open `scripts/ingest_checkpoint_nrdl.json` and confirm:
   - `"completed_notebooks": ["NRDL-MATR-01"]`
   - Exactly 33 entries in `"uploaded_sources"`

3. **Verify Preserved Shield via MCP**:
   Call `call_mcp_tool` with `ServerName: "notebooklm"`, `ToolName: "notebook_list"`.
   Observe:
   - `7967d647-...`: 188 sources
   - `ec86de71-...`: 87 sources
   - `407d5cb4-...`: 28 sources
   - `e7fba70b-...`: 51 sources
   - `cd72ef58-...`: 34 sources
   Total: 388 sources.

4. **Resume Full Parochial Ingestion**:
   In an elevated PowerShell prompt at the project root:
   ```powershell
   .\venv\Scripts\python.exe scripts/ingest_navarredondilla_parroquial.py
   ```
   The engine will automatically detect `NRDL-MATR-01` in the checkpoint, skip its 33 sources, and process the remaining 14 notebooks sequentially.

---

## Verified Claims Matrix

| # | Claim | Verification Method | Result |
|---|-------|---------------------|:------:|
| 1 | BOM utf-8-sig properly handled on catalog | Static code inspection (line 202) & log audit | **PASS** |
| 2 | Range interleaving separated by cuaderno_asignado_id | Code inspection (line 213) & log fotograma jump (01954->01988) | **PASS** |
| 3 | Naming format [L-28] validated (`^\d{9}_\d{5}\.jpg$`, len=19) | Static code regex (line 86, lines 236-244) | **PASS** |
| 4 | Preserved 5 notebooks (388 sources) have pre/post assertions | Static inspection (lines 264-296, 584-592) & MCP live query | **PASS** |
| 5 | Target notebook collision guard prevents overwriting protected IDs | Static inspection (lines 404-409) | **PASS** |
| 6 | Dual-tier checkpointing prevents duplicate uploads | Static inspection (lines 125-190, 455, 462-476) & Idempotency rerun log | **PASS** |
| 7 | Pilot notebook created (`1e6fec74-...`) with 33/33 READY sources | Live empirical query via NotebookLM MCP tool `source_list` | **PASS** |
| 8 | Checkpoint is ready to resume from `NRDL-BAUT-01` | `scripts/ingest_checkpoint_nrdl.json` verification | **PASS** |

---

## Adversarial Challenge & Stress-Test Report

**Overall Risk Assessment**: **LOW**

### Challenge 1: Process Interruption During Mid-Batch Upload
- **Assumption Challenged**: Script survives unexpected termination during large multi-hour run.
- **Attack Scenario**: Kill process at image 123 of 245 in `NRDL-BAUT-01`.
- **Blast Radius**: Potential loss of upload tracking leading to duplicate images or broken notebooks.
- **Mitigation & Evaluation**: `CheckpointManager.record_source()` is called and saved after *each single image* (line 505) with `.tmp` write, `os.fsync`, and atomic `os.replace`. Furthermore, Tier 2 queries `client.sources.list(notebook_id)` on resume, catching any source uploaded on Google's side even if local checkpoint saving failed. **PASSED**.

### Challenge 2: Accidental Overwrite of Preserved Notebooks
- **Assumption Challenged**: New notebook resolution could inadvertently target an existing protected notebook.
- **Attack Scenario**: Target title resolution maps to a protected ID.
- **Blast Radius**: Sacramental or Ensenada Legos notebook contaminated.
- **Mitigation & Evaluation**: Triple barrier: (1) `verify_protected_shield` runs pre-ingestion; (2) explicit assertion `if nid in PROTECTED_NOTEBOOKS: raise RuntimeError(...)` at line 405 halts execution before any upload; (3) `verify_protected_shield` runs post-ingestion. **PASSED**.

### Challenge 3: Google Token Expiry During 2.5-Hour Execution
- **Assumption Challenged**: Auth token remains valid for 2,243 uploads.
- **Attack Scenario**: Session cookies expire at hour 2.
- **Blast Radius**: Pipeline throws `AuthError` and exits.
- **Mitigation & Evaluation**: Because state is checkpointed atomically per image, no work is lost. User runs `notebooklm login` in PowerShell and re-runs the script; ingestion resumes at the exact interrupted document. **PASSED**.
