# Forensic E2E Verification Analysis — San Juan del Molinillo Corpus

**Agent**: worker_jmol_m2 (E2E Verification Runner)  
**Date**: 2026-11-01T00:30:00Z  
**Target Corpus**: San Juan del Molinillo (y anejos Navandrinal y El Villarejo)  
**Methodology**: `auditoria-integridad-corpus` (Forensic E2E cross-check)  
**Test Harness**: `scripts/verify_sanjuan_parroquial_sources.py`  
**Artifact Evaluated**: `scripts/verification_report_jmol.json`  

---

## 1. Executive Summary

An independent, end-to-end verification audit was conducted against Google Cloud NotebookLM Pro to certify the ingestion completeness, primary key compliance, source processing status, and barrier shield integrity of the San Juan del Molinillo sacramental corpus (2,731 canonical images across 18 notebooks).

The execution of the verification harness (task-36) and subsequent live MCP audits confirmed:
- **Protected Notebooks Shield**: **100% INTACT** (0 mutations across all 6 frozen production notebooks).
- **Completed Target Notebooks**: **17 of 18 notebooks (94.4%) are fully PASS** with **100% READY status**, 0 missing sources, and 0 duplicates.
- **Corpus Readiness**: **2,730 of 2,731 sources (99.963%) are fully confirmed in READY status**.
- **Anomaly Detected & Remediated**: In `JMOL-DIFU-04` (`457361c1-70f8-4368-8e86-10b0beeb169f`), exactly 1 source (`004298571_01084.jpg`) suffered a transient Google Cloud ingestion failure (`status_label: "error"`, ghost row `ad559b75-8deb-47e8-85c4-0852dfea2a61`). In accordance with skill `auditoria-integridad-corpus` § 2, this ghost row was surgically purged via `source_delete`. Exactly 1 single image remains to be uploaded to achieve 2,731/2,731 (100.00%).

---

## 2. Protected Production Notebooks Shield Audit

Before auditing the new target notebooks, the test harness verified the inviolability of the 6 frozen active notebooks:

| # | Notebook UUID | Title | Expected Sources | Verified Count | Status |
|---|---------------|-------|------------------|----------------|--------|
| 1 | `7967d647-8ca2-4863-a576-11843e8e8802` | Lib. Baut. Navarre Vol. 1 (1594-1695) | 188 | 188 | PASS |
| 2 | `ec86de71-a11c-4489-bbb9-eea856cccac4` | NRDL-ENSENADA-LEGOS-01 | 87 | 87 | PASS |
| 3 | `407d5cb4-4b83-495f-a23a-309ea44ee8c6` | JMOL-ENSENADA-LEGOS-01 | 28 | 28 | PASS |
| 4 | `e7fba70b-af7d-4602-b543-060742b22528` | VLLR-ENSENADA-LEGOS-01 | 51 | 51 | PASS |
| 5 | `cd72ef58-fcf5-48ac-8de2-556648ebd90e` | NDRN-ENSENADA-LEGOS-01 | 34 | 34 | PASS |
| 6 | `1e6fec74-1e2f-4dd7-8ad1-6d25411de127` | NRDL-MATR-01 | 36 | 36 | PASS |

**Shield Assessment**: Zero regression observed. All protected notebooks remain intact.

---

## 3. Detailed Results Across the 18 Molinillo Notebooks

| # | Target ID | Notebook Title | Cloud UUID | Expected | Actual | READY | Missing | Status |
|---|-----------|----------------|------------|----------|--------|-------|---------|--------|
| 1 | `JMOL-BAUT-01` | JMOL-BAUT-01 | `fa62871d-cb66-4af4-8e13-4dcc1c12b7ce` | 175 | 175 | 175 | 0 | **PASS** |
| 2 | `JMOL-BAUT-02` | JMOL-BAUT-02 | `ad39ba03-d91f-4357-a4cd-bc845ff5f5d4` | 276 | 276 | 276 | 0 | **PASS** |
| 3 | `JMOL-BAUT-03` | JMOL-BAUT-03 | `8816402f-ccce-4ebe-95a1-eb337e8a367a` | 190 | 190 | 190 | 0 | **PASS** |
| 4 | `JMOL-BAUT-04` | JMOL-BAUT-04 | `303c70ed-bdd5-4570-a19a-08ebb945bdf5` | 189 | 189 | 189 | 0 | **PASS** |
| 5 | `JMOL-BAUT-05` | JMOL-BAUT-05 | `7f64917d-d8d1-45a0-b8c2-dfe0314a48d1` | 139 | 139 | 139 | 0 | **PASS** |
| 6 | `JMOL-INDICE-BAUT` | JMOL-INDICE-BAUT | `e26e1dd5-a9aa-469a-80af-3d52603bbdc0` | 111 | 111 | 111 | 0 | **PASS** |
| 7 | `JMOL-MATR-01` | JMOL-MATR-01 | `50e8d7d8-7afe-4d70-9a8e-e22cc2cc1101` | 194 | 194 | 194 | 0 | **PASS** |
| 8 | `JMOL-MATR-02` | JMOL-MATR-02 | `772135ac-4305-4a22-ad89-bf996f0ff37a` | 134 | 134 | 134 | 0 | **PASS** |
| 9 | `JMOL-MATR-03` | JMOL-MATR-03 | `07a61f80-24e6-484e-af57-ebe19d09960a` | 198 | 198 | 198 | 0 | **PASS** |
| 10 | `JMOL-DIFU-01` | JMOL-DIFU-01 | `44aaf6f4-ef87-4740-8d34-bc661923df87` | 202 | 202 | 202 | 0 | **PASS** |
| 11 | `JMOL-DIFU-02` | JMOL-DIFU-02 | `9d0e8882-7d5f-4677-98f3-1913bbbefcc9` | 277 | 277 | 277 | 0 | **PASS** |
| 12 | `JMOL-DIFU-03` | JMOL-DIFU-03 | `a5d19fcc-d266-4497-bdb3-df182328bdcb` | 17 | 17 | 17 | 0 | **PASS** |
| 13 | `JMOL-DIFU-04` | JMOL-DIFU-04 | `457361c1-70f8-4368-8e86-10b0beeb169f` | 214 | 213 | 213 | 1* | **INCOMPLETE** |
| 14 | `JMOL-DIFU-05` | JMOL-DIFU-05 | `bbb4a49c-90a4-4af1-8818-484fa158e929` | 99 | 99 | 99 | 0 | **PASS** |
| 15 | `JMOL-DIFU-06` | JMOL-DIFU-06 | `de24a81e-df39-49ec-8ca0-63f23827f745` | 177 | 177 | 177 | 0 | **PASS** |
| 16 | `JMOL-DIFU-PARVULOS` | JMOL-DIFU-PARVULOS | `d974c19c-6a6d-46f2-8f29-e996af323d67` | 27 | 27 | 27 | 0 | **PASS** |
| 17 | `JMOL-INDICE-DIFU` | JMOL-INDICE-DIFU | `34b553cd-c82d-4311-b5c6-bdaeb2451372` | 21 | 21 | 21 | 0 | **PASS** |
| 18 | `JMOL-MIXTO-04` | JMOL-SACRAMENTAL-1842-1850 | `81eb6310-b70c-40db-9fb0-b0c1f364ce05` | 91 | 91 | 91 | 0 | **PASS** |
| **TOTAL** | | | | **2,731** | **2,730** | **2,730** | **1** | **99.96% READY** |

\* *In JMOL-DIFU-04, 214 items were initially present in cloud, but source `004298571_01084.jpg` had failed Google Cloud processing (`status_label: "error"`). Following skill `auditoria-integridad-corpus`, the ghost row was purged, leaving 213 verified READY sources and 1 pending re-upload.*

---

## 4. Forensic Investigation of `004298571_01084.jpg`

1. **Asset Identification**:
   - Primary Key: `004298571_01084.jpg` (Complies with Rule [L-28]).
   - Local Physical Path: `c:\TRABAJOS\personal\genealo\imagenes\rollo 004298571\004298571_01084.jpg`.
   - Content: Folio de Defunciones de Párvulos de San Juan del Molinillo y anejos (Noviembre de 1855, párroco Fabián Rodríguez).
   - Integrity: Non-corrupt, verified visually and on disk.

2. **Root Cause Analysis**:
   - During asynchronous batch ingestion by background task-2618, Google Cloud Labs Tailwind UI accepted the upload but the OCR/indexing pipeline encountered an internal backend timeout, creating a ghost row (`ad559b75-8deb-47e8-85c4-0852dfea2a61`) with `status_label: "error"`.
   - In accordance with the Integrity Mandate and skill `auditoria-integridad-corpus`, a source in `error` status cannot be counted as READY.
   - The ghost row was deleted via MCP `source_delete(confirm=True)`.

3. **Remediation Path**:
   - To achieve the 100.00% target (2,731 / 2,731), `004298571_01084.jpg` must be uploaded to notebook `457361c1-70f8-4368-8e86-10b0beeb169f`.
   - In `scripts/ingest_checkpoint_jmol.json`, removing `"JMOL-DIFU-04"` from `completed_notebooks` allows the ingestion script to resume idempotently via `python scripts/ingest_sanjuan_parroquial.py --target JMOL-DIFU-04`.
   - Since the other 213 sources are already tracked in `uploaded_sources`, the script will skip all 213 and upload only `004298571_01084.jpg` in ~5 seconds.
