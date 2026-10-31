## 2026-10-31T10:25:37Z
[Message] sender=fed48cc4-ccf0-40bb-ae10-7fff6d7c2cd1 priority=MESSAGE_PRIORITY_HIGH
You are test_writer_1 (E2E Test Writer).
Your working directory is: c:\TRABAJOS\personal\genealo\.agents\teamwork\test_writer_1\

Read the original request at:
c:\TRABAJOS\personal\genealo\.agents\teamwork\ORIGINAL_REQUEST.md
and the project architecture at:
c:\TRABAJOS\personal\genealo\.agents\teamwork\orchestrator\PROJECT.md
and specifications at:
c:\TRABAJOS\personal\genealo\.agents\teamwork\spec_miner_survey_1\handoff.md

FILE OWNERSHIP:
You EXCLUSIVELY own:
- scripts/verify_notebooklm_sources.py
- scripts/verification_report.json
Do NOT touch or modify other files.

TASK:
Write the complete, production-grade independent verification script `scripts/verify_notebooklm_sources.py` using `notebooklm-py` in Python (compatible with `c:\TRABAJOS\personal\genealo\venv\Scripts\python.exe`).
The script must independently verify:
1. Active notebook protection: Notebook `7967d647-8ca2-4863-a576-11843e8e8802` (`Lib. Baut. Navarre Vol. 1 (1594-1695)`) is alive and has exactly 188 sources.
2. The 4 target notebooks exist with exact names [L-29]:
   - `NRDL-ENSENADA-LEGOS-01`
   - `JMOL-ENSENADA-LEGOS-01`
   - `VLLR-ENSENADA-LEGOS-01`
   - `NDRN-ENSENADA-LEGOS-01`
3. Each notebook contains exactly the expected sources as cross-checked with `catalogo_corpus.json` (loaded with `encoding="utf-8-sig"`):
   - NRDL: exactly 87 sources (range 881 to 967 on roll 004469033)
   - JMOL: exactly 28 sources (range 952 to 979 on roll 004469028)
   - VLLR: exactly 51 sources (range 901 to 951 on roll 004469028)
   - NDRN: exactly 34 sources (range 980 to 1013 on roll 004469028)
   Total: exactly 200 sources.
4. Source naming standard: Every source title must strictly conform to `{DGS}_{FOTOGRAMA}.jpg` without zero truncation [L-28].
5. Source status: Check that sources are in READY status with 0 errors.
6. The script should produce a formatted summary and dump `scripts/verification_report.json` with detailed per-notebook and per-source validation results. Exit code 0 if all 200 sources and 4 notebooks are valid; non-zero if any gap, extra, or error is found.

Keep progress updated in `c:\TRABAJOS\personal\genealo\.agents\teamwork\test_writer_1\progress.md`.
Produce your handoff in `c:\TRABAJOS\personal\genealo\.agents\teamwork\test_writer_1\handoff.md` and send a message when done.
