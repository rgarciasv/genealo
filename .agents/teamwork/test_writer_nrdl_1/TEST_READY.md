# TEST_READY — Navarredondilla Parroquial E2E Verification Test Suite

**Author**: `test_writer_nrdl_1` (Independent E2E Test Engineer)  
**Date**: 2026-10-31T12:20:00Z  
**Target Milestone**: M2 / E2E Verification & Forensic Audit  
**Artifacts Produced**:
- `scripts/verify_nrdl_parroquial_sources.py` (Verification Harness Engine)
- `scripts/verification_report_nrdl.json` (Structured JSON Verification Report)

---

## 1. Test Harness Overview

`scripts/verify_nrdl_parroquial_sources.py` provides independent, out-of-band verification of the 15 Navarredondilla Parroquial notebooks (2,276 images) against the canonical truth in `catalogo_corpus.json` and asserts hard isolation of 5 existing protected notebooks (388 sources).

### Core Capabilities:
1. **Protected Active Notebooks Shield (5 Notebooks, 388 Sources)**:
   - `7967d647-8ca2-4863-a576-11843e8e8802` (`Lib. Baut. Navarre Vol. 1 (1594-1695)`, NRDL-BAUT-04): exactly 188 sources, 0 modifications.
   - `ec86de71-a11c-4489-bbb9-eea856cccac4` (`NRDL-ENSENADA-LEGOS-01`): exactly 87 sources.
   - `407d5cb4-4b83-495f-a23a-309ea44ee8c6` (`JMOL-ENSENADA-LEGOS-01`): exactly 28 sources.
   - `e7fba70b-af7d-4602-b543-060742b22528` (`VLLR-ENSENADA-LEGOS-01`): exactly 51 sources.
   - `cd72ef58-fcf5-48ac-8de2-556648ebd90e` (`NDRN-ENSENADA-LEGOS-01`): exactly 34 sources.
   - Hard collision guard: fails immediately if any newly created notebook ID collides with a protected notebook.
2. **Canonical Corpus Cross-Check (2,276 Sources across 15 Notebooks)**:
   - Reads `catalogo_corpus.json` with BOM safety (`utf-8-sig`).
   - Filters strictly by `cuaderno_asignado_id == notebook_title`, eliminating interleaving hazards (e.g. `NRDL-MATR-01` fotogramas 1955–1987 nested inside `NRDL-BAUT-01`).
   - Asserts exact bidirectional set equality (`missing_sources == 0`, `extra_sources == 0`, `duplicate_sources == 0`).
3. **Primary Key Naming Standard [L-28]**:
   - Asserts pattern `^\d{9}_\d{5}\.jpg$` on every source without zero truncation.
4. **Source Processing Status**:
   - Asserts 100% `READY` status (0 `ERROR`, 0 `PENDING`).
   - Safe status extraction via `get_source_status_str` preventing `AttributeError: 'Source' object has no attribute 'status_label'`.
5. **CLI Flexibility**:
   - `--notebook`: Filter verification to a specific notebook (e.g. `--notebook NRDL-MATR-01`) or comma-separated list.
   - `--catalog-path`: Custom corpus path.
   - `--report-path`: Custom JSON output destination.
   - `--quiet`: Suppress verbose per-source lists.
   - `--self-test`: Full offline mock test suite covering standard and adversarial scenarios.
6. **Reporting**:
   - Structured ASCII table printed to stdout.
   - JSON report serialized to `scripts/verification_report_nrdl.json`.
   - Exit code: `0` on 100% pass, `1` on any failure.

---

## 2. Test Execution Commands

### A. Offline Self-Test & Adversarial Verification (No Cloud Connection Required)
To verify the internal correctness of the test harness logic, assertions, and mock scenarios:
```powershell
c:\TRABAJOS\personal\genealo\venv\Scripts\python.exe scripts/verify_nrdl_parroquial_sources.py --self-test
```
*(Requires `BypassSandbox: true`)*

**Self-Test Scenarios Covered**:
1. Perfect pass: 15 target notebooks (2,276 sources) + 5 protected notebooks (388 sources) -> PASS (0).
2. Protected barrier violation: Sacramental notebook altered (187 vs 188 sources) -> FAIL (1).
3. Primary key naming violation [L-28]: Zero-truncated title detected -> FAIL (1).
4. Error status detection: Source in `ERROR` status -> FAIL (1).
5. Missing target notebook: Missing notebook detected -> FAIL (1).
6. Collision guard: Target notebook aliasing a protected ID caught -> FAIL (1).
7. Granular filtering: `--notebook NRDL-MATR-01` single notebook audit -> PASS (0).

**Status**: Verified 7/7 PASSED.

---

### B. Live E2E Verification (Full Audit of NotebookLM Cloud Account)
Once the ingestion engine finishes uploading the 15 notebooks and 2,276 images:
```powershell
c:\TRABAJOS\personal\genealo\venv\Scripts\python.exe scripts/verify_nrdl_parroquial_sources.py
```
*(Requires `BypassSandbox: true`)*

### C. Live Granular Verification (Single Pilot Notebook)
To verify an individual notebook (e.g. after a pilot ingestion):
```powershell
c:\TRABAJOS\personal\genealo\venv\Scripts\python.exe scripts/verify_nrdl_parroquial_sources.py --notebook NRDL-MATR-01
```

---

## 3. Current Live Status & Authentication Note

- **Script Readiness**: Complete, validated, and operational.
- **Live Google Session Status**: The current stored profile session in `C:\Users\rgarc\.notebooklm\profiles\default\storage_state.json` received a signed-out redirect from `https://notebook.google.com/`.
- **Action Required for Live Ingestion/Verification**: Run `venv\Scripts\notebooklm.exe login` (or `notebooklm login --browser-cookies chrome/edge`) with `BypassSandbox: true` to refresh the session tokens, per rule `[L-21]`.
