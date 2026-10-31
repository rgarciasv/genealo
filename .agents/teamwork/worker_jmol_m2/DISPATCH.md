# Task Assignment: E2E Verification Runner (worker_jmol_m2)

**Timestamp**: 2026-11-01T00:18:00Z  
**Assigned Agent**: worker_jmol_m2 (teamwork_worker)  
**Assigned By**: orchestrator_1 (efdbc414-905b-4b33-84ab-8e3f24e32ae8)  
**Working Directory**: c:\TRABAJOS\personal\genealo\.agents\teamwork\worker_jmol_m2  

## Mission
Execute the independent verification harness `scripts/verify_sanjuan_parroquial_sources.py` against live Google Cloud NotebookLM Pro, inspect `scripts/verification_report_jmol.json`, and certify whether all 2,731 sources across all 18 notebooks are in READY status, with 0 missing, 0 duplicates, 0 errors, and zero regression across the 6 protected production notebooks.

## Inputs
- `c:\TRABAJOS\personal\genealo\.agents\teamwork\ORIGINAL_REQUEST.md` (MANDATORY TO READ FIRST)
- `c:\TRABAJOS\personal\genealo\.agents\teamwork\orchestrator_1\PROJECT.md`
- `c:\TRABAJOS\personal\genealo\catalogo_corpus.json`
- `c:\TRABAJOS\personal\genealo\scripts\ingest_checkpoint_jmol.json`
- `c:\TRABAJOS\personal\genealo\scripts\verify_sanjuan_parroquial_sources.py`

## Instructions
1. Read `ORIGINAL_REQUEST.md` and `PROJECT.md`.
2. Execute the verification harness using `.\venv\Scripts\python.exe scripts\verify_sanjuan_parroquial_sources.py`.
3. Capture execution output and inspect the generated artifact `scripts/verification_report_jmol.json`.
4. Validate that:
   - Exit code is 0.
   - `overall_status == "PASS"`.
   - Missing sources: 0.
   - Extra / duplicate sources: 0.
   - Error count: 0.
   - Exactly 2,731 sources confirmed in READY status.
   - Protected production notebooks shield is 100% intact.
5. Write your complete handoff report in `c:\TRABAJOS\personal\genealo\.agents\teamwork\worker_jmol_m2\handoff.md` and analysis in `analysis.md`.
6. Send completion message to orchestrator (`efdbc414-905b-4b33-84ab-8e3f24e32ae8`).
