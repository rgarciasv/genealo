# Task Assignment: Remediation & Final E2E Certification Runner (worker_jmol_m2_remediation)

**Timestamp**: 2026-11-01T00:32:00Z  
**Assigned Agent**: worker_jmol_m2_remediation (teamwork_worker)  
**Assigned By**: orchestrator_1 (efdbc414-905b-4b33-84ab-8e3f24e32ae8)  
**Working Directory**: c:\TRABAJOS\personal\genealo\.agents\teamwork\worker_jmol_m2_remediation  

## Mission
Upload the single remaining image `004298571_01084.jpg` to notebook `JMOL-DIFU-04` (`457361c1-70f8-4368-8e86-10b0beeb169f`), verify that it transitions to `READY` status, update the checkpoint `scripts/ingest_checkpoint_jmol.json`, execute the verification harness `scripts/verify_sanjuan_parroquial_sources.py` to achieve exit code 0 with `overall_status: PASS` across all 18 notebooks and 2,731 sources, and report final certification.

## Inputs
- `c:\TRABAJOS\personal\genealo\.agents\teamwork\ORIGINAL_REQUEST.md` (MANDATORY TO READ FIRST)
- `c:\TRABAJOS\personal\genealo\.agents\teamwork\orchestrator_1\PROJECT.md`
- `c:\TRABAJOS\personal\genealo\.agents\teamwork\worker_jmol_m2\handoff.md`
- Target Image: `c:\TRABAJOS\personal\genealo\imagenes\rollo 004298571\004298571_01084.jpg`
- Target Notebook: `457361c1-70f8-4368-8e86-10b0beeb169f` (`JMOL-DIFU-04`)
- Checkpoint: `c:\TRABAJOS\personal\genealo\scripts\ingest_checkpoint_jmol.json`
- Verification Harness: `c:\TRABAJOS\personal\genealo\scripts\verify_sanjuan_parroquial_sources.py`

## Instructions
1. Read `ORIGINAL_REQUEST.md` and `worker_jmol_m2/handoff.md`.
2. Add the source `c:\TRABAJOS\personal\genealo\imagenes\rollo 004298571\004298571_01084.jpg` to notebook `457361c1-70f8-4368-8e86-10b0beeb169f` using the `notebooklm` MCP tool `source_add` (or equivalent python client script).
3. Wait for the source to reach `READY` status using `source_wait` or status inspection.
4. Record the uploaded source in `scripts/ingest_checkpoint_jmol.json` under `uploaded_sources["004298571_01084.jpg"]` with its `source_id`, `notebook_id`, and timestamp.
5. Execute the full verification harness:
   `.\venv\Scripts\python.exe scripts\verify_sanjuan_parroquial_sources.py`
6. Verify:
   - Exit code is 0.
   - `scripts/verification_report_jmol.json` reports `overall_status: PASS`.
   - Exactly 2,731 / 2,731 sources are confirmed in READY status.
   - Missing sources: 0. Extra/duplicate sources: 0. Errors: 0.
   - All 6 protected production notebooks remain intact.
7. Write `handoff.md` and `analysis.md` in your working directory.
8. Send completion message to orchestrator (`efdbc414-905b-4b33-84ab-8e3f24e32ae8`).
