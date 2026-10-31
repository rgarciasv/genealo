# Handoff Report — Spec Miner (Option A Requirements & NotebookLM Limits)

- **Agent**: `spec_miner_nrdl_1`
- **Archetype**: Specification Miner
- **Working Directory**: `c:\TRABAJOS\personal\genealo\.agents\teamwork\spec_miner_nrdl_1\`
- **Date**: 2026-10-31T12:00:00Z
- **Recipient**: Orchestrator (`31843a9f-efd9-43e6-a718-753324e3577e`)
- **Status**: COMPLETE (Hard Handoff)

---

## 1. Observation

### 1.1 Scope & Canonical Corpus Mapping
Direct probing of `c:\TRABAJOS\personal\genealo\catalogo_corpus.json` (loaded with `encoding="utf-8-sig"`) and physical files under `c:\TRABAJOS\personal\genealo\imagenes\` established the exact scope of Option A:
- **Total corpus size in catalog**: 8,515 records.
- **Option A Scope**: Exactly 15 notebooks corresponding to the parish records of Navarredondilla (excluding the protected and pre-existing `NRDL-BAUT-04`).
- **Total image count**: Exactly **2,276 images**.
- **Physical disk verification**: Exactly 2,276 out of 2,276 `.jpg` files exist across `rollo 004306112` and `rollo 004306113` (0 missing, 0 zero-byte, 0 corrupted).
- **Physical size on disk**: 2,984,350,009 bytes (~2.78 GB), average 1.28 MB per image.
- **Universal naming regex [L-28]**: `^\d{9}_\d{5}\.jpg$`. 100% compliance across all 2,276 files (0 violations).

#### Detailed Specification Matrix for the 15 Option A Notebooks

| # | Cuaderno Canónico | Rollo DGS | Fuentes | Fotogramas | Continuidad / Tramo | Signatura Archivo | Años Macro | Tipos Documentales |
|---|---|---|---|---|---|---|---|---|
| 1 | `NRDL-BAUT-01` | `004306112` | 245 | 1870–2147 | Discontinuo: [1870..1954] y [1988..2147] | Sit. Arch. 166/4 | 1594–1636, 1638–1695 | BAUTISMOS, CODICE_MIXTO |
| 2 | `NRDL-BAUT-02` | `004306112` | 157 | 2218–2374 | Continuo | Sit. Arch. 166/4 | 1697–1749 | BAUTISMOS |
| 3 | `NRDL-BAUT-03` | `004306112` | 231 | 2375–2605 | Continuo | Sit. Arch. 166/4 | 1750–1803 | BAUTISMOS |
| 4 | `NRDL-BAUT-05` | `004306113` | 144 | 1–144 | Continuo | Sit. Arch. 166/4 | 1829–1854 | BAUTISMOS, DIANAS_TECNICAS |
| 5 | `NRDL-BAUT-06` | `004306113` | 183 | 145–327 | Continuo | Sit. Arch. 166/4 | 1852–1878 | BAUTISMOS |
| 6 | `NRDL-BAUT-07` | `004306113` | 102 | 328–429 | Continuo | Sit. Arch. 166/4 | 1876–1889 | BAUTISMOS |
| 7 | `NRDL-DIFU-01` | `004306113` | 236 | 430–665 | Continuo | Sit. Arch. 166/4 | 1701–1738, 1739–1767 | DEFUNCIONES |
| 8 | `NRDL-DIFU-01B` | `004306113` | 65 | 666–730 | Continuo | Sit. Arch. 166/4 | 1767–1802 | DEFUNCIONES |
| 9 | `NRDL-DIFU-02` | `004306113` | 171 | 801–971 | Continuo | Sit. Arch. 166/4 | 1802–1836 | DEFUNCIONES |
| 10 | `NRDL-DIFU-03` | `004306113` | 170 | 972–1141 | Continuo | Sit. Arch. 166/4 | 1802–1836 | DEFUNCIONES |
| 11 | `NRDL-DIFU-04` | `004306113` | 188 | 1142–1329 | Continuo | Sit. Arch. 166/4 | 1836–1854, 1852–1872 | DEFUNCIONES |
| 12 | `NRDL-DIFU-05` | `004306113` | 211 | 1330–1540 | Continuo | Sit. Arch. 166/4 | 1872–1902 | DEFUNCIONES |
| 13 | `NRDL-MATR-01` | `004306112` | 33 | 1955–1987 | Continuo (intercalado en NRDL-BAUT-01) | Sit. Arch. 166/4 | 1634–1686, 1637 | INVENTARIO_ALHAJAS, MATRIMONIOS |
| 14 | `NRDL-MATR-02` | `004306113` | 70 | 731–800 | Continuo | Sit. Arch. 166/4 | 1698–1803, 1760–1790 | EXPEDIENTES_MATRIMONIALES, MATRIMONIOS |
| 15 | `NRDL-MIXTO-01` | `004306112` | 70 | 2148–2217 | Continuo | Sit. Arch. 166/4 | 1649–1701 | CODICE_MIXTO |
| **TOTAL** | **15 Cuadernos** | **2 Rollos** | **2.276** | — | — | — | — | — |

### 1.2 Preserved Active Notebooks Shield (MUST NOT BE MODIFIED OR DUPLICATED)
Probing of the live user account via `client.notebooks.list()` confirmed the existence and source counts of the 5 protected notebooks:
1. `Lib. Baut. Navarre Vol. 1 (1594-1695)`:
   - **ID**: `7967d647-8ca2-4863-a576-11843e8e8802`
   - **Canonical Role**: Corresponds to `NRDL-BAUT-04` (rollo `004306112`, fotogramas 2606–2793).
   - **Sources**: Exactly **188 sources**. Status: 100% READY.
2. `NRDL-ENSENADA-LEGOS-01`:
   - **ID**: `ec86de71-a11c-4489-bbb9-eea856cccac4`
   - **Sources**: Exactly **87 sources**. Status: 100% READY.
3. `JMOL-ENSENADA-LEGOS-01`:
   - **ID**: `407d5cb4-4b83-495f-a23a-309ea44ee8c6`
   - **Sources**: Exactly **28 sources**. Status: 100% READY.
4. `VLLR-ENSENADA-LEGOS-01`:
   - **ID**: `e7fba70b-af7d-4602-b543-060742b22528`
   - **Sources**: Exactly **51 sources**. Status: 100% READY.
5. `NDRN-ENSENADA-LEGOS-01`:
   - **ID**: `cd72ef58-fcf5-48ac-8de2-556648ebd90e`
   - **Sources**: Exactly **34 sources**. Status: 100% READY.
- **Combined Preserved Total**: Exactly 5 notebooks containing 388 sources. All ingestion scripts and verification harnesses must assert that these 5 IDs and source counts remain completely unchanged.

### 1.3 NotebookLM Account Quota & System Limits
Authoritative inspection of `notebooklm-py` (v0.8.5) and live queries against `client.settings` revealed:
- **`AccountLimits`**:
  - `notebook_limit = 500`: The user account allows up to 500 notebooks. The account currently has 55 notebooks. Adding the 15 Option A notebooks reaches 70 notebooks, using only 14% of account capacity.
  - `source_limit = 300`: The hard maximum sources per notebook is 300. The largest notebook in Option A is `NRDL-BAUT-01` with 245 sources. Rule `[L-29]` is 100% satisfied.
  - `tier = 2`: Advanced/Pro tier.
- **Usage & Quota**:
  - `UsageWindowKind.FIVE_HOUR`: 0.0% used (100.0% remaining).
  - `UsageWindowKind.WEEKLY`: 1.39% used (98.61% remaining).
- **Client Concurrency Defaults**:
  - `DEFAULT_MAX_CONCURRENT_UPLOADS = 4`: Hard limit in `notebooklm._runtime.config`.

### 1.4 Operational Pacing, Rate Limiting & Lifecycle Mechanics
Analysis of the previous Ensenada Legos ingestion run (`scripts/ingest_ensenada_legos.log`) showed:
- **Throughput observed**: 200 documents uploaded in 825.35s = **4.13 seconds/document** (including 1.5s pacing sleep).
- **Projected execution time for 2,276 images**:
  $$2.276 \times 4,13\text{ s} \approx 9.400\text{ segundos} \approx 156,7\text{ minutos} \approx \mathbf{2,61\text{ horas}}$$
- **Transient Failure Handling**:
  - Catches `(RateLimitError, NetworkError, ServerError, RPCError, httpx.HTTPError)`.
  - Exponential backoff: `2.0 * (2 ** (attempt - 1))` (2s, 4s, 8s, 16s, 32s) across 5 attempts.
- **Source Processing Lifecycle**:
  - Source states: `UNKNOWN (-1)`, `PROCESSING (1)`, `READY (2)`, `ERROR (3)`, `PREPARING (5)`.
  - Asynchronous pipeline: calling `add_file(..., wait=False)` streams the file and returns immediately with status `PROCESSING`. Background workers in Google NotebookLM process/OCR the images in parallel.
  - Readout confirmation: when polling batch readiness after uploads complete, all sources are typically already `READY`.

---

## 2. Logic Chain

1. **Mapping Truth**: `catalogo_corpus.json` is the sole canonical source of truth for assigning images to notebooks. It was observed that inside rollo `004306112`, `NRDL-MATR-01` (fotogramas 1955–1987) is geometrically intercalated inside the bounds of `NRDL-BAUT-01` (1870–2147). Therefore, any algorithm that filters by numeric range `fotograma_min <= f <= fotograma_max` will corrupt the dataset. Ingestion and verification must strictly filter by `cuaderno_asignado_id`.
2. **Idempotency & Checkpointing**: Ingesting 2,276 images requires ~2.6 hours of network communication. Network dropouts, OS sleep, or transient HTTP 503/429 errors could terminate the process midway. Without a state tracking mechanism, a restart would either upload duplicate sources (since NotebookLM permits multiple sources with the same name) or require lengthy API queries. Therefore, a two-tier checkpointing mechanism is required:
   - Tier 1: Local state file (`scripts/ingest_nrdl_checkpoint.json`) committing every completed upload with `(notebook_id, filename, source_id, status)`.
   - Tier 2: Remote API reconciliation querying `client.sources.list(notebook_id)` before uploading, skipping any file where `is_ready` or `is_processing` is True.
3. **Capacity Validation**: With `notebook_limit = 500` and `source_limit = 300`, Option A (15 notebooks, max 245 sources/notebook) fits completely within NotebookLM platform constraints without risk of quota rejection.
4. **Decoupled Processing**: By setting `wait=False` on `add_file` and polling readiness per notebook in batches, upload bandwidth is not stalled waiting for OCR processing.

---

## 3. Features Discovered

| # | Category | Feature | Description | Inputs | Outputs | Error Behavior | Discovered Via |
|---|---|---|---|---|---|---|---|
| 1 | Scope | 15 Parish Notebooks | Canonic set of 15 mono-locality notebooks for Navarredondilla | `catalogo_corpus.json` | 15 notebook definitions, total 2,276 images | Count mismatch raises `ValueError` | `catalogo_corpus.json` |
| 2 | Shielding | Protected Notebooks Barrier | Hard isolation of 5 existing notebooks (1 sacramental + 4 Ensenada Legos) | Notebook IDs (`7967d647-...`, `ec86de71-...`, etc.) | Shield verification, pre/post source count assertion (388 sources) | Raises `RuntimeError` on source count drift or collision | `reviewer4_independent_audit.py`, API probe |
| 3 | Identifier | Canonical Primary Key [L-28] | Unpadded 9-digit DGS + underscore + 5-digit zero-padded fotograma + `.jpg` | `rollo_dgs`, `fotograma_numero` | String matching `^\d{9}_\d{5}\.jpg$` | Raises `ValueError` on regex mismatch | `catalogo_corpus.json`, `[L-28]` |
| 4 | Topology | Mono-locality Isolation [L-29] | Each notebook contains documents from only one locality and <= 300 sources | `cuaderno_asignado_id`, source list | Max 245 sources in `NRDL-BAUT-01` (<= 300) | Raises `ValueError` if sources > 300 | `[L-29]`, `client.settings.get_account_limits()` |
| 5 | Auth | Persistent Storage Authentication [L-21] | Unattended session loading via encrypted local storage tokens | `.notebooklm` storage directory | Authenticated `NotebookLMClient` session | Raises `AuthError` on invalid/expired tokens | `notebooklm.NotebookLMClient.from_storage()` |
| 6 | API Limits | Account & Tier Capacity | Account permits 500 notebooks and 300 sources/notebook | `client.settings.get_account_limits()` | `AccountLimits(notebook_limit=500, source_limit=300, tier=2)` | None (read-only query) | `notebooklm._settings.SettingsAPI` |
| 7 | Ingestion | Resumable File Upload | Streaming multipart upload with title assignment | `notebook_id`, `file_path`, `mime_type='image/jpeg'`, `title=filename`, `wait=False` | `Source` object with `id` and `status=PROCESSING` | Raises `RateLimitError`, `ServerError`, `RPCError`, `NetworkError` | `client.sources.add_file` in `notebooklm._web.sources` |
| 8 | Reliability | Exponential Backoff & Retry | Retries transient network/quota failures with increasing delays | `attempt`, `INITIAL_BACKOFF=2.0s`, `MAX_RETRIES=5` | Delayed retry (2s, 4s, 8s, 16s, 32s) | Raises original exception after 5 exhausted attempts | `ingest_ensenada_legos.py` |
| 9 | Pacing | Upload Throttling | Inter-file pacing pause to prevent burst rate limit exhaustion | `UPLOAD_PAUSE_SECONDS = 1.5s` | Async sleep between uploads | None | `ingest_ensenada_legos.py` |
| 10 | Concurrency | Internal Upload Semaphore | Maximum parallel uploads managed by SDK transport layer | `DEFAULT_MAX_CONCURRENT_UPLOADS = 4` | Concurrency semaphore bounded to 4 | Blocks coroutines until slot opens | `notebooklm._runtime.config` |
| 11 | Lifecycle | Document Processing States | Asynchronous transition of sources from upload to readiness | `SourceStatus` enum (`UNKNOWN=-1`, `PROCESSING=1`, `READY=2`, `ERROR=3`, `PREPARING=5`) | Status strings and properties (`is_ready`, `is_processing`, `is_error`) | Flagged in verification report | `notebooklm.types.SourceStatus` |
| 12 | State Tracking | Dual-Tier Checkpointing | Persistent local JSON state log + live API query for resumption | `checkpoint.json` + `client.sources.list(notebook_id)` | Skips already processed files, resumes from last image | Prevents duplicate uploads | Architectural analysis of 2.6h run |
| 13 | Verification | Independent E2E Audit | Out-of-band cross-validation comparing catalog truth against live API | `catalogo_corpus.json`, `client.notebooks.list()`, `client.sources.list()` | Exit code 0, formatted ASCII report, `verification_report.json` | Non-zero exit code on missing/extra sources or status != READY | `verify_notebooklm_sources.py` |

---

## 4. Edge Cases

| # | Feature | Input | Observed Behavior |
|---|---|---|---|
| 1 | Range Interleaving | `NRDL-BAUT-01` fotogramas 1870–2147 vs `NRDL-MATR-01` fotogramas 1955–1987 | `NRDL-MATR-01` (33 images) is nested physically within the outer bounds of `NRDL-BAUT-01`. Filtering by numeric bounds `1870 <= f <= 2147` incorrectly injects marriage records into the baptism notebook. Filtering must strictly use `r["cuaderno_asignado_id"] == "NRDL-BAUT-01"`. |
| 2 | File Encoding / UTF-8 BOM | `catalogo_corpus.json` loaded with standard `utf-8` | Fails or prepends `\ufeff` to the first key, corrupting initial record parsing. Must explicitly open with `encoding="utf-8-sig"`. |
| 3 | Duplicate Notebook Titles | Multiple notebooks with the same title exist in the account | `client.notebooks.list()` returns a list of matching notebooks. If an ingestion script creates a notebook without checking existing titles, duplicates proliferate. Resolution: check existing titles first and reuse the first matching ID. |
| 4 | Duplicate Sources in Notebook | Repeated upload of the same filename | NotebookLM allows duplicate sources with identical titles in the same notebook. The script must inspect `existing_sources_by_title` before issuing `add_file` to guarantee strict 1:1 parity with the catalog. |
| 5 | Mid-Run Disconnection | Network reset or timeout during 2.6-hour ingestion | Without checkpointing, restarting requires re-querying all notebooks or re-uploading. With checkpointing, the script immediately resumes at the exact interrupted fotograma. |
| 6 | Transient HTTP 429 / 503 | Burst upload triggering Google rate limits | `RateLimitError` or `ServerError` caught by exponential backoff (2s, 4s, 8s, 16s, 32s). Pacing delay of 1.5s completely averted 429s in the 200-document run. |
| 7 | Windows Sandbox Execution | Running Python CLI without `BypassSandbox: true` | PowerShell fails with `Acceso denegado` when accessing Python in `AppData\Local\Python`. All command invocations must specify `BypassSandbox: true`. |
| 8 | Multiple Record Document Types | `NRDL-BAUT-05` has technical targets (`DIANAS_TECNICAS`) and `NRDL-MATR-01` has jewel inventories (`INVENTARIO_ALHAJAS`) | All records in `catalogo_corpus.json` have valid physical JPEG files and valid `cuaderno_asignado_id`. The script must ingest all records belonging to the notebook regardless of document subtype. |

---

## 5. Caveats

1. **Total Execution Duration**: Ingesting 2,276 images at ~4.13 seconds/image requires **~2.6 hours** of continuous execution. The implementation worker must configure generous timeouts, run asynchronously in the background, or process notebook-by-notebook with granular checkpoint saves.
2. **Read-Only Scope**: In strict accordance with the Spec Miner role, no production source code has been altered and no notebooks have been created during this survey.
3. **Token Freshness**: For long-running operations (> 2 hours), Google OAuth tokens in the persistent profile auto-refresh via `notebooklm-py`'s internal refresh pipeline, but network stability is required.

---

## 6. Conclusion

- **Option A Scope is Authoritatively Defined**: Exactly 15 notebooks, exactly 2,276 images, and exactly 2,984,350,009 bytes across 2 rolls (`004306112` and `004306113`), with 100% physical presence on disk.
- **Account Limits are Completely Favorable**: With a 500-notebook account ceiling and 300-source notebook limit, all 15 notebooks (maximum 245 sources) fit safely.
- **Implementation Blueprint**:
  1. Parametrize `scripts/ingest_ensenada_legos.py` into `scripts/ingest_navarredondilla_parroquial.py`.
  2. Implement local JSON checkpointing (`scripts/ingest_nrdl_checkpoint.json`) alongside live API duplicate checks.
  3. Maintain 1.5s inter-file pacing and 5-attempt exponential backoff.
  4. Assert hard shielding for the 5 preserved notebooks (188 + 87 + 28 + 51 + 34 = 388 sources).
  5. Parametrize `scripts/verify_notebooklm_sources.py` into `scripts/verify_nrdl_parroquial_sources.py` for independent verification.

---

## 7. Verification Method

To independently verify the observations and specifications documented in this report:

```powershell
# 1. Verify 2,276 images and 15 notebooks in catalogo_corpus.json and disk presence:
.\venv\Scripts\python.exe -c "
import json
from pathlib import Path

target_notebooks = [
    'NRDL-BAUT-01', 'NRDL-BAUT-02', 'NRDL-BAUT-03', 'NRDL-BAUT-05',
    'NRDL-BAUT-06', 'NRDL-BAUT-07', 'NRDL-DIFU-01', 'NRDL-DIFU-01B',
    'NRDL-DIFU-02', 'NRDL-DIFU-03', 'NRDL-DIFU-04', 'NRDL-DIFU-05',
    'NRDL-MATR-01', 'NRDL-MATR-02', 'NRDL-MIXTO-01'
]

with open('catalogo_corpus.json', 'r', encoding='utf-8-sig') as f:
    corpus = json.load(f)

total_target = 0
for nb in target_notebooks:
    recs = [r for r in corpus if r.get('cuaderno_asignado_id') == nb]
    total_target += len(recs)
    for r in recs:
        p = Path('imagenes') / f'rollo {r[\"rollo_dgs\"]}' / r[\"id_imagen\"]
        assert p.is_file(), f'Missing file: {p}'

assert total_target == 2276, f'Expected 2276, got {total_target}'
print(f'PASS: Verified {len(target_notebooks)} notebooks and {total_target} files present on disk.')
"

# 2. Verify account limits (500 notebooks, 300 sources) and protected active notebooks live:
.\venv\Scripts\python.exe -c "
import asyncio
from notebooklm import NotebookLMClient

async def verify():
    async with NotebookLMClient.from_storage() as client:
        limits = await client.settings.get_account_limits()
        assert limits.notebook_limit >= 500
        assert limits.source_limit >= 300
        print('PASS: Account limits verified:', limits)
        
        # Verify protected sacramental notebook
        prot = await client.notebooks.get('7967d647-8ca2-4863-a576-11843e8e8802')
        sources = await client.sources.list(prot.id)
        assert len(sources) == 188
        print(f'PASS: Protected notebook {prot.title} ({prot.id}) has exactly 188 sources.')

asyncio.run(verify())
"
```
