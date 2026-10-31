# Handoff Report — reviewer_2 (Interface & Compliance Reviewer)

- **Agent ID**: reviewer_2
- **Roles**: reviewer, critic
- **Working Directory**: `c:\TRABAJOS\personal\genealo\.agents\teamwork\reviewer_2\`
- **Date**: 2026-10-31T10:34:00Z
- **Target Audience**: Orchestrator (`fed48cc4-ccf0-40bb-ae10-7fff6d7c2cd1`)
- **Review Target**: `scripts/ingest_ensenada_legos.py`
- **Verdict**: **REQUEST_CHANGES**

---

## Review Summary

**Verdict**: **REQUEST_CHANGES**

The script `scripts/ingest_ensenada_legos.py` contains strong architectural defenses for notebook shielding, corpus loading, and mono-locality isolation. However, an independent audit of the `notebooklm-py` SDK v0.8.5 interface revealed a **Critical fatal defect at line 300** (`source.status_label`). The dataclass `Source` does not define `status_label`. Consequently, running the script will raise `AttributeError` on the very first upload, terminating the entire process. The script cannot be approved until this line is corrected.

---

## Findings

### [Critical] Finding 1: Fatal `AttributeError` on `source.status_label` (SDK Conformance Violation)
- **What**: The script attempts to access `source.status_label`, an attribute that does not exist in `notebooklm-py` SDK v0.8.5.
- **Where**: `scripts/ingest_ensenada_legos.py`, Line 300:
  ```python
  293:                        logger.info(
  294:                            "[%s] (%d/%d) Successfully uploaded %s -> source_id: %s (status=%s)",
  295:                            target_title,
  296:                            idx,
  297:                            len(records),
  298:                            filename,
  299:                            source.id,
  300:                            source.status_label,
  301:                        )
  ```
- **Why**: Inspection of `venv\Lib\site-packages\notebooklm\_types\sources.py` (lines 488–618) confirms that `Source` has the following attributes and properties:
  - Attributes: `id`, `title`, `url`, `_type_code`, `created_at`, `status` (a `SourceStatus` enum), `drive_document_id`, `drive_status`, `download_url`, `viewer_url`, `content_mime`, `word_count`, `revision_id`, `revision_timestamp`, `last_modified_at`, `expert_intelligence`.
  - Properties: `kind`, `is_ready`, `is_drive_degraded`, `is_processing`, `is_error`.
  There is **no** `status_label` property or attribute on `Source`. When Python evaluates `source.status_label`, it immediately raises `AttributeError: 'Source' object has no attribute 'status_label'`. Because `AttributeError` is not caught by the transient retry clause (`RateLimitError`, `NetworkError`, `ServerError`, `RPCError`, `httpx.HTTPError`), it falls through to line 326 (`except Exception as fatal_err:`), logs a fatal error, and aborts execution on the first image upload.
- **Suggestion**: Replace `source.status_label` with `source.status.name` (or `source.status` or `source_status_to_str(source.status)`).

### [Minor] Finding 2: Missing Fotograma Range Assertion in Preflight Validation
- **What**: `TARGET_NOTEBOOKS` defines `fotograma_start` and `fotograma_end` for all four series (lines 46–47, 54–55, 62–63, 70–71), but `load_and_validate_corpus()` does not check that `int(r["fotograma_numero"])` falls within `[fotograma_start, fotograma_end]`.
- **Where**: `scripts/ingest_ensenada_legos.py`, Lines 147–161.
- **Why**: While all 200 records in `catalogo_corpus.json` currently fall within the expected ranges, defensive programming dictates that this range check should be asserted to prevent any accidental cross-parish inclusion if the corpus is edited.
- **Suggestion**: Add inside `load_and_validate_corpus()`:
  ```python
  fotograma = int(r.get("fotograma_numero", 0))
  if not (meta["fotograma_start"] <= fotograma <= meta["fotograma_end"]):
      raise ValueError(f"Fotograma {fotograma} outside range [{meta['fotograma_start']}, {meta['fotograma_end']}] for {target_name}")
  ```

### [Minor] Finding 3: Non-Deterministic Resolution of Duplicate Notebook Titles
- **What**: `existing_by_title = {nb.title: nb for nb in all_notebooks}` silently overrides duplicate titles.
- **Where**: `scripts/ingest_ensenada_legos.py`, Line 205.
- **Why**: NotebookLM does not enforce unique titles. If an aborted earlier run created a duplicate notebook with the same name, this dict comprehension keeps only the last notebook without warning or checking if another instance already has uploaded sources.
- **Suggestion**: Group by title (`notebooks_by_title.setdefault(nb.title, []).append(nb)`) and emit a warning if `len(matched) > 1`, as done in `scripts/verify_notebooklm_sources.py:368-372`.

---

## 1. Observation

### 1.1 SDK Conformance (`notebooklm-py` v0.8.5)
- **Client Factory**: `NotebookLMClient.from_storage()` at line 185 is fully conformant with `notebooklm/client.py:688-710` as an async context manager.
- **Notebook Creation**: `client.notebooks.create(title=target_title)` at line 215 matches `notebooklm/_notebooks.py:144` (`async def create(self, title: str) -> Notebook`).
- **File Ingestion**: `client.sources.add_file(...)` at line 286 matches `notebooklm/_sources.py:505-548`:
  - `notebook_id: str`
  - `file_path: str | Path`
  - `mime_type: str | None = "image/jpeg"`
  - `title: str | None = filename`
  - `wait: bool = False`
- **Source Attribute Access**: Line 300 accesses `source.status_label`.
  - Verbatim inspection of `notebooklm/_types/sources.py:488-660`: No attribute or property named `status_label`.
  - Verbatim inspection of `notebooklm/_types/enums.py:483-499`: Defines `_SOURCE_STATUS_MAP` and `SOURCE_STATUS_LABELS = tuple(_SOURCE_STATUS_MAP.values())`, but this is a module-level tuple, not bound to `Source`.

### 1.2 Corpus File Path Resolution
- Verified existence of all 200 target files on disk:
  1. `NRDL-ENSENADA-LEGOS-01`: 87 images from `imagenes\rollo 004469033\004469033_00881.jpg` to `004469033_00967.jpg`. Verified present with size ~700KB–1.3MB each.
  2. `JMOL-ENSENADA-LEGOS-01`: 28 images from `imagenes\rollo 004469028\004469028_00952.jpg` to `004469028_00979.jpg`. Verified present.
  3. `VLLR-ENSENADA-LEGOS-01`: 51 images from `imagenes\rollo 004469028\004469028_00901.jpg` to `004469028_00951.jpg`. Verified present.
  4. `NDRN-ENSENADA-LEGOS-01`: 34 images from `imagenes\rollo 004469028\004469028_00980.jpg` to `004469028_01013.jpg`. Verified present.
  - Path construction at line 256: `(BASE_DIR / "imagenes" / f"rollo {dgs}" / filename).resolve()` resolves accurately to absolute paths on Windows without double slashes or escaping bugs.

### 1.3 Parish Contamination [L-29] and Naming [L-28]
- Strict mono-locality filtering:
  - Records are partitioned into `assigned_records` by exact key `cuaderno_asignado_id`.
  - Ingestion loop processes one notebook title at a time, uploading only that locality's records into its dedicated `notebook_id`.
  - In `rollo 004469028` (shared between VLLR, JMOL, NDRN), the fotograma ranges are strictly disjoint:
    * VLLR: 901 to 951
    * JMOL: 952 to 979
    * NDRN: 980 to 1013
  - No overlap exists; 0 risk of cross-parish data mixing.
- Filename format:
  - Exact `id_imagen` string (e.g. `004469033_00881.jpg`) is passed to `title=filename` [L-28]. Leading zeros are preserved.

### 1.4 Protection of Notebook `7967d647-8ca2-4863-a576-11843e8e8802`
- Hardcoded constant `PROTECTED_NOTEBOOK_ID = "7967d647-8ca2-4863-a576-11843e8e8802"`.
- Lines 188–200: Preflight verification queries title and initial source count (188 sources).
- Lines 219–224: Safety assertion raises `RuntimeError` if any target notebook resolves to `7967d647-8ca2-4863-a576-11843e8e8802`.
- Lines 397–414: Post-ingestion audit verifies source count remains strictly unchanged.
- Zero mutation calls (`delete`, `update`, `add_file`) target the protected ID under any execution path or error branch.

---

## 2. Logic Chain

1. **Premise 1**: Python evaluates expression arguments to function calls before the function is called.
2. **Observation**: On line 300 of `scripts/ingest_ensenada_legos.py`, `source.status_label` is passed as an argument to `logger.info(...)`.
3. **Observation**: In `notebooklm-py` 0.8.5 (`_types/sources.py`), `Source` does not possess an attribute or property named `status_label`.
4. **Deduction**: Evaluating `source.status_label` raises `AttributeError: 'Source' object has no attribute 'status_label'`.
5. **Observation**: Lines 305–325 only catch `(RateLimitError, NetworkError, ServerError, RPCError, httpx.HTTPError)`.
6. **Observation**: Lines 326–333 catch `Exception as fatal_err:` and immediately execute `raise`.
7. **Conclusion**: When `scripts/ingest_ensenada_legos.py` runs, it will abort with an unhandled `AttributeError` during the very first file upload. It cannot successfully ingest the 200 documents in its current state. Therefore, changes must be requested.

---

## 3. Caveats

1. **Runtime Execution**: Live execution of the script was not performed during this review because unsandboxed terminal execution was denied by the user. Static analysis of the SDK bytecode and Python source files is definitive.
2. **Rate Limits on Execution**: Although exponential backoff and a 1.5s delay are implemented, uploading 200 files in a single session may occasionally hit NotebookLM's rolling hourly upload limits. The script's resumption mechanism (`if filename in existing_by_title and existing_s.is_ready: continue`) will allow resuming if re-executed.

---

## 4. Conclusion

The script `scripts/ingest_ensenada_legos.py` satisfies 4 of the 5 audit requirements:
- File paths resolve accurately to `imagenes\rollo 004469033\` and `imagenes\rollo 004469028\` (100% verified, 200/200 files present).
- Strict mono-locality isolation [L-29] is enforced.
- Naming format `{DGS}_{FOTOGRAMA}.jpg` [L-28] without zero truncation is enforced.
- Active notebook `7967d647-8ca2-4863-a576-11843e8e8802` is shielded and cannot be touched under any execution path.

However, it **fails Requirement 1 (SDK Interface Conformance)** due to `source.status_label` at line 300.
**Verdict**: **REQUEST_CHANGES**.

---

## 5. Verification Method

To verify Finding 1 independently:

1. **SDK Source Code Inspection**:
   Inspect `c:\TRABAJOS\personal\genealo\venv\Lib\site-packages\notebooklm\_types\sources.py` lines 488–660 to confirm the fields and properties of `class Source`. Note the absence of `status_label`.

2. **Target File Inspection**:
   Inspect line 300 of `scripts/ingest_ensenada_legos.py`:
   ```python
   source.status_label,
   ```

3. **Required Fix**:
   In `scripts/ingest_ensenada_legos.py`, replace line 300 with:
   ```python
   source.status.name,
   ```
   (or `source.status,`).

4. **Invalidation Condition**:
   If `Source` in `notebooklm` has a `status_label` attribute added dynamically or via monkeypatching, this finding would be invalidated. Verification of `client.py` and `_client_assembly.py` confirms no monkeypatching is applied.
