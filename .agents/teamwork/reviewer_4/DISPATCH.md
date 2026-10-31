## 2026-10-31T11:00:55Z
You are reviewer_4 (Compliance & Corpus Alignment Reviewer).
Your working directory is: c:\TRABAJOS\personal\genealo\.agents\teamwork\reviewer_4\

Read:
- c:\TRABAJOS\personal\genealo\.agents\teamwork\ORIGINAL_REQUEST.md
- c:\TRABAJOS\personal\genealo\.agents\teamwork\orchestrator\PROJECT.md
- c:\TRABAJOS\personal\genealo\.agents\teamwork\orchestrator\TEST_READY.md
- c:\TRABAJOS\personal\genealo\.agents\teamwork\worker_m2\handoff.md
- c:\TRABAJOS\personal\genealo\scripts\verification_report.json

TASK:
Audit the alignment between `catalogo_corpus.json` and the sources ingested in NotebookLM:
1. Run the verification harness:
   `c:\TRABAJOS\personal\genealo\venv\Scripts\python.exe scripts/verify_notebooklm_sources.py`
   with `BypassSandbox: true` and verify exit code 0.
2. Verify Rule [L-28]: check that 100% of source titles follow `{DGS}_{FOTOGRAMA}.jpg` without zero truncation.
3. Verify Rule [L-29]: check that each notebook is strictly mono-locality (`NRDL-ENSENADA-LEGOS-01`, `JMOL-ENSENADA-LEGOS-01`, `VLLR-ENSENADA-LEGOS-01`, `NDRN-ENSENADA-LEGOS-01`) and does not mix parishes or document types.
4. Verify Requirement R3: confirm active notebook `7967d647-8ca2-4863-a576-11843e8e8802` (`Lib. Baut. Navarre Vol. 1 (1594-1695)`) has exactly 188 sources and has not been altered.
5. Deliver your verdict in `c:\TRABAJOS\personal\genealo\.agents\teamwork\reviewer_4\handoff.md`: APPROVE or REQUEST_CHANGES. Send a message to orchestrator when finished.
