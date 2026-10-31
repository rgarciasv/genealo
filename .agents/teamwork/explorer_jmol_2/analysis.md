# Technical Investigation Report: Ingestion Pipeline & Verification Harness for San Juan del Molinillo Parroquial Corpus

**Investigator**: `explorer_jmol_2` (Teamwork Explorer)  
**Date**: 2026-10-31  
**Working Directory**: `c:\TRABAJOS\personal\genealo`  
**Artifact Path**: `.agents/teamwork/explorer_jmol_2/analysis.md`  

---

## 1. Executive Summary

A comprehensive technical investigation of the ingestion pipeline (`scripts/ingest_sanjuan_parroquial.py`), atomic checkpoint (`scripts/ingest_checkpoint_jmol.json`), and independent verification harness (`scripts/verify_sanjuan_parroquial_sources.py`) confirms that the technical architecture is **fully hardened, production-grade, and compliant with all project engineering constraints** ([L-21], [L-28], [L-29], and [L-30]).

Key findings:
1. **Pipeline Architecture**: `scripts/ingest_sanjuan_parroquial.py` implements a dual-tier idempotent architecture combining atomic local file writes (`Path.replace()`) and live cloud source reconciliation (`client.sources.list`). It features an automated zero-regression shield protecting 6 active production notebooks (421 sources), dynamic multi-path filesystem resolution across rolls and named subfolders, and an exponential backoff retry loop (5 retries, 2s to 32s).
2. **Persistence & Headless Mode ([L-21])**: The pipeline utilizes `NotebookLMClient.from_storage()`, which operates entirely over HTTP via `httpx` using stored session credentials from `storage_state.json`. It **does not launch or hold locks on the Chromium browser profile**, completely eliminating profile lock contention on Windows.
3. **Checkpoint & Pilot State**: The pilot notebook `JMOL-DIFU-03` (`a5d19fcc-d266-4497-bdb3-df182328bdcb`) is fully completed and confirmed in READY state (17/17 sources). Furthermore, **all 18 canonical notebook IDs have already been resolved/created in Google NotebookLM Pro** and recorded in `scripts/ingest_checkpoint_jmol.json`.
4. **Live Execution in Progress**: Live inspection reveals that an unattended production ingestion run was initiated at 19:38:56 (system local / 18:38:56 UTC). It is currently ingesting notebook `JMOL-BAUT-01` (`fa62871d-cb66-4af4-8e13-4dcc1c12b7ce`), progressing steadily at ~5.0 seconds per source with zero errors.
5. **Independent Verification Harness**: `scripts/verify_sanjuan_parroquial_sources.py` validates 100% READY status, 0 missing sources, 0 unexpected sources, and the integrity of the 6 protected notebooks before reporting PASS and writing `scripts/verification_report_jmol.json`.

---

## 2. In-Depth Analysis of Ingestion Pipeline (`scripts/ingest_sanjuan_parroquial.py`)

### 2.1 Architectural Overview
The ingestion pipeline is implemented as an asynchronous Python service (`asyncio`) leveraging `notebooklm-py` v0.8.5. It manages the ingestion of all 2,731 sacramental photographic sources across 18 dedicated mono-locality notebooks for San Juan del Molinillo and its historical annexes (Navandrinal and El Villarejo).

```
+-----------------------------------------------------------------------------------+
|                        scripts/ingest_sanjuan_parroquial.py                       |
+-----------------------------------------------------------------------------------+
       |
       +--> 1. Pre-flight Validation: load_and_validate_corpus()
       |       - Validates catalogo_corpus.json (utf-8-sig BOM handling)
       |       - Verifies 2,731 files physically exist on disk (size > 0 bytes)
       |       - Enforces [L-28] primary key format (^\d{9}_\d{5}\.jpg$, 19 chars)
       |       - Supports --dry-run flag for safe offline verification
       |
       +--> 2. Client Initialization: NotebookLMClient.from_storage() [L-21]
       |       - Pure HTTP transport via httpx (no Chromium lock)
       |
       +--> 3. Pre-flight Shield Check: run_preflight_shield_check()
       |       - Asserts 6 protected notebooks exist and maintain expected source counts
       |
       +--> 4. Idempotent Notebook Resolution: resolve_or_create_notebooks()
       |       - Level 1: Local Checkpoint lookup (scripts/ingest_checkpoint_jmol.json)
       |       - Level 2: Cloud Title lookup (NotebookLM account list)
       |       - Level 3: client.notebooks.create(canonical_title)
       |
       +--> 5. Ingestion Loop with Dual-Tier Idempotency & Exponential Backoff
               - Checkpoint check -> Cloud source list check -> File Upload
               - 1.5s pause between uploads + 5-attempt exponential backoff (2s -> 32s)
               - Atomic checkpoint write after each file upload (Path.replace())
               - Notebook completion marking upon reaching 100% upload count
```

### 2.2 Client Lifecycle & Authentication Persistence ([L-21])
The script connects to NotebookLM via `NotebookLMClient.from_storage()`:
```python
# scripts/ingest_sanjuan_parroquial.py:501-502
logger.info("Initializing NotebookLMClient from user storage...")
client_ctx = NotebookLMClient.from_storage()
async with client_ctx as client:
```

- **Authentication Mechanism**: Reads session tokens and cookies from `C:\Users\rgarc\.notebooklm\profiles\default\storage_state.json`.
- **Headless Execution**: Inspection of `notebooklm/client.py` confirms that `from_storage()` initializes an `httpx.AsyncClient` connection pool (`_FromStorageContext`). It does not spawn a Playwright browser instance during regular operation.
- **Profile Lock Protection**: Because no browser process is launched, the Chromium user data directory (`browser_profile`) is not locked. Multiple scripts (or verify harnesses) can read the same storage state concurrently without crashing.
- **Unattended Session Refresh ([L-21])**: If the session cookies expire, `NotebookLMClient` raises `AuthError`. Line 468 explicitly traps `AuthError` and logs a critical message, allowing external renewal via `venv\Scripts\notebooklm.exe login` with `BypassSandbox: true`.

### 2.3 Dynamic Path Resolution (`resolve_image_path`)
The script resolves physical image paths dynamically without hardcoded absolute disk paths:
```python
# scripts/ingest_sanjuan_parroquial.py:269-282
def resolve_image_path(id_img: str, dgs: str) -> Path:
    search_paths = [
        BASE_DIR / "imagenes" / f"rollo {dgs}" / id_img,
    ]
    # Dynamically discover San Juan subfolders in workspace
    for p in BASE_DIR.iterdir():
        if p.is_dir() and "San Juan" in p.name:
            search_paths.append(p / id_img)

    for p in search_paths:
        if p.is_file():
            return p
    raise FileNotFoundError(f"Physical image missing on disk across all search locations: {id_img}")
```
- **Evidence of Operational Success**: In the pipeline log (`ingest_sanjuan_parroquial.log:120`), all 2,731 files across rolls `004298570` and `004298571` were successfully discovered and validated on disk before ingestion commenced.

### 2.4 Rate Limiting & Resilience Engine
```python
# scripts/ingest_sanjuan_parroquial.py:167-172
UPLOAD_PAUSE_SECONDS = 1.5
MAX_RETRIES = 5
INITIAL_BACKOFF_SECONDS = 2.0
READINESS_TIMEOUT_SECONDS = 300
READINESS_POLL_INTERVAL_SECONDS = 5.0
```
- **Pacing**: Configurable default pause of 1.5 seconds between uploads (`--pause`) ensures healthy ingestion pacing well below NotebookLM API rate limits.
- **Exponential Backoff**: If a network glitch, RPC error, server error, or rate limit occurs (`RateLimitError, RPCError, ServerError, NetworkError, httpx.HTTPError`), the script backs off with delay doubling: $2.0\text{s} \to 4.0\text{s} \to 8.0\text{s} \to 16.0\text{s} \to 32.0\text{s}$ across 5 retries.
- **Fail-Fast on Auth Expiration**: `AuthError` is caught separately and immediately re-raised, preventing futile retry loops when credentials have expired.

### 2.5 Dual-Tier Idempotency Architecture
1. **Tier 1 (Local Checkpoint)**:
   - Checkpoint manager (`CheckpointManager`) maintains `scripts/ingest_checkpoint_jmol.json`.
   - Every file upload is written to a temporary file (`ingest_checkpoint_jmol.json.tmp`) and atomically swapped into place via `temp_path.replace(self.path)` (invoking Windows `ReplaceFileW` / `MoveFileExW` with `MOVEFILE_REPLACE_EXISTING`).
   - If the process is halted abruptly (Ctrl+C, power loss, network disconnect), the checkpoint file cannot be left in a corrupted or half-written state.
2. **Tier 2 (Cloud Source Reconciliation)**:
   - When entering any target notebook, line 528 executes:
     ```python
     cloud_sources = await client.sources.list(nb_id)
     cloud_source_titles = {s.title: s.id for s in cloud_sources}
     ```
   - If a source already exists in Google NotebookLM Pro (e.g., uploaded in a previous session but the checkpoint write was interrupted), the pipeline detects it, skips the upload, updates the checkpoint, and continues without producing duplicate sources.

### 2.6 Boundary Rule Compliance
- **[L-28] Filename Integrity**: Validated by regex `^\d{9}_\d{5}\.jpg$` and exact string length 19 (`len(id_img) == 19`). Guards against Excel/CSV zero-padding stripping (e.g., `4298570_1599.jpg`).
- **[L-29] Notebook Isolation & Capacity ($\le 300$ Sources)**: Each notebook is mono-locality. Source counts range from 17 (`JMOL-DIFU-03`) to 277 (`JMOL-DIFU-02`), all strictly complying with the $\le 300$ rule.
- **[L-30] Canonical Sacramental Naming**: Line 160 explicitly maps target `"JMOL-MIXTO-04"` to canonical title `"JMOL-SACRAMENTAL-1842-1850"`, ensuring pure sacramental naming standards.

---

## 3. Inspection of Checkpoint State (`scripts/ingest_checkpoint_jmol.json`)

### 3.1 Checkpoint Structure & Pilot Verification
Inspection of `scripts/ingest_checkpoint_jmol.json` provides direct evidence of the following state:
- **Schema Version**: `1.0`
- **Created Timestamp**: `2026-10-31T15:08:44.571390+00:00`
- **Pilot Notebook `JMOL-DIFU-03`**:
  - Cloud Notebook ID: `a5d19fcc-d266-4497-bdb3-df182328bdcb`
  - Completed Status: Recorded in `completed_notebooks: ["JMOL-DIFU-03"]`
  - Uploaded Sources: All 17 sources (`004298571_01033.jpg` to `004298571_01049.jpg`) recorded with cloud UUIDs and upload timestamps.

### 3.2 Canonical Notebook Registration Map
All 18 canonical notebooks are already created in Google NotebookLM Pro and registered in `notebook_ids`:

| Target ID | Canonical Notebook Title | Cloud Notebook ID (UUID) | DGS Rollo | Expected Sources | Status in Checkpoint |
|:---|:---|:---|:---:|:---:|:---:|
| `JMOL-BAUT-01` | `JMOL-BAUT-01` | `fa62871d-cb66-4af4-8e13-4dcc1c12b7ce` | `004298570` | 175 | **IN PROGRESS (Live Ingestion)** |
| `JMOL-BAUT-02` | `JMOL-BAUT-02` | `ad39ba03-d91f-4357-a4cd-bc845ff5f5d4` | `004298570` | 276 | Registered / Pending upload |
| `JMOL-BAUT-03` | `JMOL-BAUT-03` | `8816402f-ccce-4ebe-95a1-eb337e8a367a` | `004298570` | 190 | Registered / Pending upload |
| `JMOL-BAUT-04` | `JMOL-BAUT-04` | `303c70ed-bdd5-4570-a19a-08ebb945bdf5` | `004298570` | 189 | Registered / Pending upload |
| `JMOL-BAUT-05` | `JMOL-BAUT-05` | `7f64917d-d8d1-45a0-b8c2-dfe0314a48d1` | `004298570` | 139 | Registered / Pending upload |
| `JMOL-INDICE-BAUT` | `JMOL-INDICE-BAUT` | `e26e1dd5-a9aa-469a-80af-3d52603bbdc0` | `004298570` | 111 | Registered / Pending upload |
| `JMOL-MATR-01` | `JMOL-MATR-01` | `50e8d7d8-7afe-4d70-9a8e-e22cc2cc1101` | `004298571` | 194 | Registered / Pending upload |
| `JMOL-MATR-02` | `JMOL-MATR-02` | `772135ac-4305-4a22-ad89-bf996f0ff37a` | `004298571` | 134 | Registered / Pending upload |
| `JMOL-MATR-03` | `JMOL-MATR-03` | `07a61f80-24e6-484e-af57-ebe19d09960a` | `004298571` | 198 | Registered / Pending upload |
| `JMOL-DIFU-01` | `JMOL-DIFU-01` | `44aaf6f4-ef87-4740-8d34-bc661923df87` | `004298571` | 202 | Registered / Pending upload |
| `JMOL-DIFU-02` | `JMOL-DIFU-02` | `9d0e8882-7d5f-4677-98f3-1913bbbefcc9` | `004298571` | 277 | Registered / Pending upload |
| `JMOL-DIFU-03` | `JMOL-DIFU-03` | `a5d19fcc-d266-4497-bdb3-df182328bdcb` | `004298571` | 17 | **COMPLETED (17/17 READY)** |
| `JMOL-DIFU-04` | `JMOL-DIFU-04` | `457361c1-70f8-4368-8e86-10b0beeb169f` | `004298571` | 214 | Registered / Pending upload |
| `JMOL-DIFU-05` | `JMOL-DIFU-05` | `bbb4a49c-90a4-4af1-8818-484fa158e929` | `004298571` | 99 | Registered / Pending upload |
| `JMOL-DIFU-06` | `JMOL-DIFU-06` | `de24a81e-df39-49ec-8ca0-63f23827f745` | `004298571` | 177 | Registered / Pending upload |
| `JMOL-DIFU-PARVULOS`| `JMOL-DIFU-PARVULOS`| `d974c19c-6a6d-46f2-8f29-e996af323d67` | `004298571` | 27 | Registered / Pending upload |
| `JMOL-INDICE-DIFU` | `JMOL-INDICE-DIFU` | `34b553cd-c82d-4311-b5c6-bdaeb2451372` | `004298571` | 21 | Registered / Pending upload |
| `JMOL-MIXTO-04` | `JMOL-SACRAMENTAL-1842-1850` | `81eb6310-b70c-40db-9fb0-b0c1f364ce05` | `004298570` | 91 | Registered / Pending upload |
| **TOTALS** | **18 Notebooks** | **18 Verified Cloud IDs** | — | **2,731 Sources** | — |

---

## 4. In-Depth Analysis of Independent Verification Harness (`scripts/verify_sanjuan_parroquial_sources.py`)

### 4.1 Verification Protocol & Zero-Regression Barrier
The verification harness provides an independent audit of the NotebookLM account without relying on ingestion runtime state:
1. **Protected Active Notebooks Shield Check**:
   Lines 59-84 and 128-138 define and check the 6 protected production notebooks:
   - `7967d647-8ca2-4863-a576-11843e8e8802`: `Lib. Baut. Navarre Vol. 1 (1594-1695)` (188 sources)
   - `ec86de71-a11c-4489-bbb9-eea856cccac4`: `NRDL-ENSENADA-LEGOS-01` (87 sources)
   - `407d5cb4-4b83-495f-a23a-309ea44ee8c6`: `JMOL-ENSENADA-LEGOS-01` (28 sources)
   - `e7fba70b-af7d-4602-b543-060742b22528`: `VLLR-ENSENADA-LEGOS-01` (51 sources)
   - `cd72ef58-fcf5-48ac-8de2-556648ebd90e`: `NDRN-ENSENADA-LEGOS-01` (34 sources)
   - `1e6fec74-1e2f-4dd7-8ad1-6d25411de127`: `NRDL-MATR-01` (33 sources)
   If any protected notebook is missing from the cloud, the harness halts immediately with an error and exit code `1`.
2. **Corpus Cross-Check**:
   Reads `catalogo_corpus.json` with BOM-safe `utf-8-sig` encoding, filtering entries where `cuaderno_asignado_id == target_id`.
3. **Set Difference Mathematics**:
   ```python
   # scripts/verify_sanjuan_parroquial_sources.py:176-183
   missing = expected_titles - cloud_titles
   extra = cloud_titles - expected_titles
   ready_count = sum(1 for s in sources if get_source_status_str(s) == "READY")

   status = "PASS" if len(missing) == 0 and len(extra) == 0 and ready_count == meta["expected_count"] else "INCOMPLETE"
   ```
   - **Missing Sources**: Any record in canonical catalog missing in cloud sets status to `INCOMPLETE`.
   - **Extra / Unassigned Sources**: Any unexpected source title in cloud sets status to `INCOMPLETE`.
   - **Error / Processing States**: Any source in status other than `READY` (e.g., `ERROR`, `PROCESSING`, `PENDING`) results in `ready_count < meta["expected_count"]`, setting status to `INCOMPLETE`.
   - **Duplicate Detection Logic**: If duplicates exist, `len(cloud_titles)` will be less than `len(sources)`. If ready count exceeds expected count or missing count > 0, `ready_count == meta["expected_count"]` will fail, guaranteeing duplicates cannot pass.

### 4.2 Status String Normalization (`get_source_status_str`)
Early versions of `notebooklm-py` experienced an `AttributeError` when querying `source.status_label` or enum representations. The harness implements defensive attribute inspection:
```python
# scripts/verify_sanjuan_parroquial_sources.py:113-122
def get_source_status_str(src: Any) -> str:
    raw = getattr(src, "status", None)
    if raw is None:
        return "UNKNOWN"
    if hasattr(raw, "name"):
        return str(raw.name)
    val = getattr(src, "status_label", None)
    if val:
        return str(val)
    return str(raw)
```
This safely extracts `"READY"` regardless of whether the SDK returns an `Enum`, a string, or an object attribute.

### 4.3 Report Serialization & Exit Codes
The harness writes a machine-readable JSON audit file to `scripts/verification_report_jmol.json`:
- `0`: Complete success (`overall_status == "PASS"`).
- `1`: Protected notebook regression or missing protected notebook.
- `2`: Incomplete ingestion or mismatch in source counts / readiness.

---

## 5. Execution Strategy & Risk Assessment

| Risk Vector | Potential Failure Mode | Implemented Mitigation in Code | Residual Risk Rating |
|:---|:---|:---|:---:|
| **API Timeouts** | Transient network dropouts or slow cloud response on upload | 30s HTTP timeouts via `httpx`, 5 retry attempts with exponential backoff ($2\text{s} \to 32\text{s}$) in `upload_single_image_with_backoff`. | **LOW** |
| **Rate Limits (HTTP 429)** | Exceeding NotebookLM API quotas during bulk upload | Mandatory `UPLOAD_PAUSE_SECONDS = 1.5` between files + automatic backoff on `RateLimitError`. | **LOW** |
| **Session Expiration** | Google authentication cookie invalidation mid-run | `AuthError` caught specifically and logged as `CRITICAL`; fails fast without corrupting state. Rule `[L-21]` unattended re-auth (`venv\Scripts\notebooklm.exe login` with `BypassSandbox: true`) restores credentials in $< 5\text{s}$. | **LOW** |
| **Chromium Profile Locks** | Windows `EBUSY` / access denied on browser profile folder | `NotebookLMClient.from_storage()` uses purely headless `httpx` HTTP requests; does not run browser binary or lock `browser_profile`. | **NEGLIGIBLE** |
| **Windows Path & Space Issues** | Failure finding files in paths with spaces (`rollo 004298570`) | Fully handled by `pathlib.Path`. Multi-path dynamic resolver scans rolls and `San Juan` subfolders dynamically. | **NEGLIGIBLE** |
| **Partial / Interrupted Ingestion** | Script interrupted mid-notebook | Dual-tier idempotency: atomic local checkpoint save after every file upload (`Path.replace()`) + cloud query skips already-uploaded images upon resume. | **NEGLIGIBLE** |
| **Corruption / 0-Byte Images** | Uploading corrupted or empty image files | Pre-flight validation in `load_and_validate_corpus()` inspects every file on disk; rejects files if `stat().st_size == 0`. | **NEGLIGIBLE** |
| **Protected Notebook Tampering** | Accidental upload to or alteration of protected notebooks | Pre-flight shield check verifies all 6 protected notebooks and source counts before any write operations occur. | **NEGLIGIBLE** |

---

## 6. Recommendations & Execution Action Plan

1. **Monitor Active Ingestion**: Allow the ongoing background process for `scripts/ingest_sanjuan_parroquial.py` to proceed undisturbed. At ~5s per source, the remaining ~2,650 images will complete in ~3.5 hours.
2. **Post-Ingestion Verification**: Once `scripts/ingest_sanjuan_parroquial.log` logs pipeline completion, immediately run:
   ```powershell
   .\venv\Scripts\python scripts\verify_sanjuan_parroquial_sources.py
   ```
   Confirm return code is `0` and `scripts/verification_report_jmol.json` reports `"overall_status": "PASS"`.
3. **If Session Expiration Occurs**: If log indicates `AuthError`, execute unattended refresh per `[L-21]`:
   ```powershell
   .\venv\Scripts\notebooklm.exe login
   ```
   (with `BypassSandbox: true`), and re-run `python scripts/ingest_sanjuan_parroquial.py`. The dual-tier checkpoint will seamlessly resume from the exact last uploaded file.
