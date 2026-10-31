# E2E Test Suite Ready

## Test Runner
- Command: `c:\TRABAJOS\personal\genealo\venv\Scripts\python.exe scripts/verify_notebooklm_sources.py`
- Self-test command: `c:\TRABAJOS\personal\genealo\venv\Scripts\python.exe scripts/verify_notebooklm_sources.py --self-test`
- Expected: all tests pass with exit code 0, 0 failures, 0 missing, 0 extra.

## Coverage Summary
| Tier | Count | Description |
|------|------:|-------------|
| 1. Feature Coverage | 200 | 1 per physical image file in the 4 Ensenada Legos series |
| 2. Boundary & Monolocality | 4 | Mono-locality isolation across NRDL, JMOL, VLLR, NDRN [L-29] |
| 3. Primary Key Standard | 200 | Exact `{DGS}_{FOTOGRAMA}.jpg` without zero truncation [L-28] |
| 4. Active Notebook Preservation | 1 | Unaltered active notebook `7967d647-8ca2-4863-a576-11843e8e8802` with 188 sources |
| **Total** | **405** | Complete requirement verification |

## Feature Checklist
| Feature | Target Notebook | Expected Count | Rollo DGS | Fotograma Range |
|---|---|---|---|---|
| F1/F3/F4 | `NRDL-ENSENADA-LEGOS-01` | 87 | 004469033 | 00881 - 00967 |
| F1/F3/F4 | `JMOL-ENSENADA-LEGOS-01` | 28 | 004469028 | 00952 - 00979 |
| F1/F3/F4 | `VLLR-ENSENADA-LEGOS-01` | 51 | 004469028 | 00901 - 00951 |
| F1/F3/F4 | `NDRN-ENSENADA-LEGOS-01` | 34 | 004469028 | 00980 - 01013 |
| F5 | `Lib. Baut. Navarre Vol. 1 (1594-1695)` | 188 | 004306112 | 7967d647-8ca2-4863-a576-11843e8e8802 |
