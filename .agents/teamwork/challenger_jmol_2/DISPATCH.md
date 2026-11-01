# Task Assignment: Challenger 2 (challenger_jmol_2)

**Timestamp**: 2026-11-01T01:16:00Z  
**Assigned Agent**: challenger_jmol_2 (teamwork_challenger)  
**Assigned By**: efdbc414-905b-4b33-84ab-8e3f24e32ae8 (orchestrator_1)  
**Working Directory**: c:\TRABAJOS\personal\genealo\.agents\teamwork\challenger_jmol_2  

## Mission
Adversarially challenge the completeness and integrity of the corpus across the physical filesystem, `catalogo_corpus.json`, `ingest_checkpoint_jmol.json`, and `verification_report_jmol.json`. Search for orphan images, cross-notebook duplicate assignments, filename anomalies, zero-byte files, and verify 1:1 bijectivity across all 2,731 photographic sources.

## Inputs
- `c:\TRABAJOS\personal\genealo\.agents\teamwork\ORIGINAL_REQUEST.md` (MANDATORY TO READ FIRST)
- `c:\TRABAJOS\personal\genealo\.agents\teamwork\orchestrator_1\PROJECT.md`
- `c:\TRABAJOS\personal\genealo\catalogo_corpus.json`
- `c:\TRABAJOS\personal\genealo\scripts\ingest_checkpoint_jmol.json`
- `c:\TRABAJOS\personal\genealo\scripts\verification_report_jmol.json`
- Physical image directories: `c:\TRABAJOS\personal\genealo\imagenes\`

## Instructions
1. Read `ORIGINAL_REQUEST.md` and `PROJECT.md` before starting work.
2. Develop an empirical verification script/oracle (via PowerShell or python script in your working directory):
   - Bijective 1:1 Mapping Check:
     * Assert that `catalogo_corpus.json` (filtered for JMOL sacramental notebooks) contains exactly 2,731 records.
     * Assert that every one of the 2,731 image filenames exists physically on disk as a non-empty, non-corrupt JPEG.
     * Assert that the set of 2,731 filenames in the catalog exactly matches the set of keys in `ingest_checkpoint_jmol.json`'s `uploaded_sources` (difference must be empty).
     * Assert that the set of 18 notebooks in `verification_report_jmol.json` matches the 18 notebooks in the catalog.
     * Assert that no image is assigned to more than one notebook (zero duplicate assignments).
   - Boundary & Edge Cases:
     * Check rule [L-28] naming format (`^\d{9}_\d{5}\.jpg$`) on all 2,731 keys.
     * Check that all source UUIDs in `uploaded_sources` are valid, non-null, and unique (2,731 distinct cloud source IDs).
3. Shield Check:
   - Verify that none of the 6 protected production notebooks was referenced or modified in the checkpoint or verification report.
4. Provide an explicit verdict in your handoff report: `APPROVE` or `REQUEST_CHANGES`.
5. Write your complete report in `c:\TRABAJOS\personal\genealo\.agents\teamwork\challenger_jmol_2\handoff.md` (with Observation, Logic Chain, Caveats, Conclusion, Verification Method).
6. Send a message to orchestrator (`efdbc414-905b-4b33-84ab-8e3f24e32ae8`) with your verdict.

## 2026-11-01T00:15:53Z
Sender: efdbc414-905b-4b33-84ab-8e3f24e32ae8
Priority: MESSAGE_PRIORITY_HIGH

TASK:
1. Develop an empirical verification script/oracle to cross-check:
   - Bijective 1:1 mapping: 2,731 corpus catalog images <-> 2,731 physical files on disk <-> 2,731 checkpoint uploaded_sources entries <-> 2,731 verified sources in verification_report_jmol.json.
   - Assert zero missing, zero duplicates, zero orphan images, zero zero-byte files.
   - Assert rule [L-28] compliance on all 2,731 image keys.
   - Assert 2,731 unique valid cloud UUIDs in uploaded_sources.
2. Verify zero regression across the 6 protected production notebooks.
3. Provide an explicit verdict: APPROVE or REQUEST_CHANGES.
4. Write your complete handoff in c:\TRABAJOS\personal\genealo\.agents\teamwork\challenger_jmol_2\handoff.md.
5. Send completion message to orchestrator efdbc414-905b-4b33-84ab-8e3f24e32ae8 with your verdict.

