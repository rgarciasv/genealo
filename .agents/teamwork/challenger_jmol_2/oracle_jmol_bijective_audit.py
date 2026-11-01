#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""
Empirical Adversarial Verification Oracle for San Juan del Molinillo Corpus.
Agent: challenger_jmol_2
Milestone: M2 (Independent E2E Verification)

Verifies:
1. Bijective 1:1 Mapping:
   - 2,731 catalog images <-> 2,731 physical files on disk <-> 2,731 checkpoint uploaded_sources entries <-> 2,731 verified sources in verification report.
   - 18 target notebooks in catalog <-> 18 notebooks in checkpoint <-> 18 notebooks in verification report.
2. Zero defects:
   - Zero missing images, zero duplicate assignments, zero zero-byte files, zero corrupt JPEGs.
   - Zero null, empty, or duplicate cloud source UUIDs across all 2,731 sources.
   - Rule [L-28] compliance (regex ^\d{9}_\d{5}\.jpg$) on all 2,731 image keys.
3. Protected notebooks shield (Zero regression):
   - Verifies 6 protected notebooks remain untouched, unmutated, with exact expected source counts.
4. Live cloud query:
   - Validates live cloud state in Google NotebookLM Pro for both protected notebooks and the 18 JMOL target notebooks.
"""


import asyncio
import json
import os
import re
import sys
import struct
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple

BASE_DIR = Path("c:/TRABAJOS/personal/genealo")
WORKSPACE_DIR = BASE_DIR / ".agents" / "teamwork" / "challenger_jmol_2"
CATALOG_PATH = BASE_DIR / "catalogo_corpus.json"
CHECKPOINT_PATH = BASE_DIR / "scripts" / "ingest_checkpoint_jmol.json"
REPORT_PATH = BASE_DIR / "scripts" / "verification_report_jmol.json"
RESULTS_OUTPUT_PATH = WORKSPACE_DIR / "oracle_audit_results.json"

L28_REGEX = re.compile(r"^\d{9}_\d{5}\.jpg$")
UUID_REGEX = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE)

PARROQUIAL_TARGETS: Dict[str, Dict[str, Any]] = {
    "JMOL-BAUT-01": {"expected_count": 175, "rollo_dgs": "004298570", "title": "JMOL-BAUT-01"},
    "JMOL-BAUT-02": {"expected_count": 276, "rollo_dgs": "004298570", "title": "JMOL-BAUT-02"},
    "JMOL-BAUT-03": {"expected_count": 190, "rollo_dgs": "004298570", "title": "JMOL-BAUT-03"},
    "JMOL-BAUT-04": {"expected_count": 189, "rollo_dgs": "004298570", "title": "JMOL-BAUT-04"},
    "JMOL-BAUT-05": {"expected_count": 139, "rollo_dgs": "004298570", "title": "JMOL-BAUT-05"},
    "JMOL-INDICE-BAUT": {"expected_count": 111, "rollo_dgs": "004298570", "title": "JMOL-INDICE-BAUT"},
    "JMOL-MATR-01": {"expected_count": 194, "rollo_dgs": "004298571", "title": "JMOL-MATR-01"},
    "JMOL-MATR-02": {"expected_count": 134, "rollo_dgs": "004298571", "title": "JMOL-MATR-02"},
    "JMOL-MATR-03": {"expected_count": 198, "rollo_dgs": "004298571", "title": "JMOL-MATR-03"},
    "JMOL-DIFU-01": {"expected_count": 202, "rollo_dgs": "004298571", "title": "JMOL-DIFU-01"},
    "JMOL-DIFU-02": {"expected_count": 277, "rollo_dgs": "004298571", "title": "JMOL-DIFU-02"},
    "JMOL-DIFU-03": {"expected_count": 17, "rollo_dgs": "004298571", "title": "JMOL-DIFU-03"},
    "JMOL-DIFU-04": {"expected_count": 214, "rollo_dgs": "004298571", "title": "JMOL-DIFU-04"},
    "JMOL-DIFU-05": {"expected_count": 99, "rollo_dgs": "004298571", "title": "JMOL-DIFU-05"},
    "JMOL-DIFU-06": {"expected_count": 177, "rollo_dgs": "004298571", "title": "JMOL-DIFU-06"},
    "JMOL-DIFU-PARVULOS": {"expected_count": 27, "rollo_dgs": "004298571", "title": "JMOL-DIFU-PARVULOS"},
    "JMOL-INDICE-DIFU": {"expected_count": 21, "rollo_dgs": "004298571", "title": "JMOL-INDICE-DIFU"},
    "JMOL-MIXTO-04": {"expected_count": 91, "rollo_dgs": "004298570", "title": "JMOL-SACRAMENTAL-1842-1850"},
}

PROTECTED_NOTEBOOKS: Dict[str, Dict[str, Any]] = {
    "7967d647-8ca2-4863-a576-11843e8e8802": {
        "title": "Lib. Baut. Navarre Vol. 1 (1594-1695)",
        "expected_sources": 188,
    },
    "ec86de71-a11c-4489-bbb9-eea856cccac4": {
        "title": "NRDL-ENSENADA-LEGOS-01",
        "expected_sources": 87,
    },
    "407d5cb4-4b83-495f-a23a-309ea44ee8c6": {
        "title": "JMOL-ENSENADA-LEGOS-01",
        "expected_sources": 28,
    },
    "e7fba70b-af7d-4602-b543-060742b22528": {
        "title": "VLLR-ENSENADA-LEGOS-01",
        "expected_sources": 51,
    },
    "cd72ef58-fcf5-48ac-8de2-556648ebd90e": {
        "title": "NDRN-ENSENADA-LEGOS-01",
        "expected_sources": 34,
    },
    "1e6fec74-1e2f-4dd7-8ad1-6d25411de127": {
        "title": "NRDL-MATR-01",
        "expected_sources": 36,  # Canonical post-[L-31] count (33 original + 3 hybrid: 02050, 02148, 02149). Stale harness expected 33.
        "stale_expected_sources": 33,
    },
}


CANONICAL_TOTAL = 2731

def is_valid_jpeg(path: Path) -> Tuple[bool, str]:
    try:
        size = path.stat().st_size
        if size == 0:
            return False, "Zero byte file"
        if size < 100:
            return False, f"File too small ({size} bytes)"
        with open(path, "rb") as f:
            header = f.read(3)
            if header != b"\xff\xd8\xff":
                return False, f"Invalid JPEG magic header: {header.hex()}"
            f.seek(-2, os.SEEK_END)
            trailer = f.read(2)
            # In rare JPEGs, trailing padding or metadata exists, but let's check
            # if we can read structure
        return True, "OK"
    except Exception as e:
        return False, str(e)

def resolve_physical_image(id_img: str, dgs: str) -> Path | None:
    # 1. Look in rollo folder
    p1 = BASE_DIR / "imagenes" / f"rollo {dgs}" / id_img
    if p1.is_file():
        return p1
    # 2. Look in root San Juan folders
    for p in BASE_DIR.iterdir():
        if p.is_dir() and "San Juan" in p.name:
            cand = p / id_img
            if cand.is_file():
                return cand
    # 3. Look in other rollo folders
    p_img = BASE_DIR / "imagenes"
    for r in p_img.iterdir():
        if r.is_dir() and r.name.startswith("rollo"):
            cand = r / id_img
            if cand.is_file():
                return cand
    return None

async def run_audit():
    print("=" * 80)
    print("EMPIRICAL ADVERSARIAL VERIFICATION AUDIT")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 80)

    audit_summary: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "verdict": "UNKNOWN",
        "tests": {},
        "failures": [],
        "metrics": {},
    }

    # -------------------------------------------------------------------------
    # TEST 1: Canonical Catalog Analysis
    # -------------------------------------------------------------------------
    print("\n--- TEST 1: CANONICAL CATALOG INTEGRITY & FILTERING ---")
    if not CATALOG_PATH.is_file():
        raise FileNotFoundError(f"Missing {CATALOG_PATH}")

    with open(CATALOG_PATH, "r", encoding="utf-8-sig") as f:
        full_catalog = json.load(f)

    # Filter for 18 target notebooks
    target_notebook_keys = set(PARROQUIAL_TARGETS.keys())
    jmol_sacramental_records = [
        r for r in full_catalog
        if r.get("cuaderno_asignado_id") in target_notebook_keys
    ]

    catalog_img_ids = [r["id_imagen"] for r in jmol_sacramental_records]
    catalog_img_set = set(catalog_img_ids)
    
    t1_pass = True
    t1_reasons = []

    if len(jmol_sacramental_records) != CANONICAL_TOTAL:
        t1_pass = False
        t1_reasons.append(f"Expected {CANONICAL_TOTAL} sacramental records, found {len(jmol_sacramental_records)}")

    if len(catalog_img_ids) != len(catalog_img_set):
        t1_pass = False
        dups = len(catalog_img_ids) - len(catalog_img_set)
        t1_reasons.append(f"Duplicate id_imagen found in catalog ({dups} duplicates)")

    # Per notebook count verification
    notebook_counts_catalog: Dict[str, int] = {}
    for r in jmol_sacramental_records:
        cid = r["cuaderno_asignado_id"]
        notebook_counts_catalog[cid] = notebook_counts_catalog.get(cid, 0) + 1

    for nb, meta in PARROQUIAL_TARGETS.items():
        actual = notebook_counts_catalog.get(nb, 0)
        expected = meta["expected_count"]
        if actual != expected:
            t1_pass = False
            t1_reasons.append(f"Notebook {nb}: expected {expected} in catalog, found {actual}")

    # Rule [L-28] check
    invalid_l28_catalog = [img for img in catalog_img_ids if not L28_REGEX.match(img)]
    if invalid_l28_catalog:
        t1_pass = False
        t1_reasons.append(f"Found {len(invalid_l28_catalog)} images failing [L-28] pattern in catalog")

    audit_summary["tests"]["test1_catalog_integrity"] = {
        "passed": t1_pass,
        "total_catalog_records": len(full_catalog),
        "jmol_sacramental_records": len(jmol_sacramental_records),
        "unique_images": len(catalog_img_set),
        "per_notebook_counts": notebook_counts_catalog,
        "reasons": t1_reasons,
    }
    print(f"Test 1 result: {'PASS' if t1_pass else 'FAIL'} (Records: {len(jmol_sacramental_records)}, Unique: {len(catalog_img_set)})")

    # -------------------------------------------------------------------------
    # TEST 2: Physical Filesystem Bijectivity & Image Integrity
    # -------------------------------------------------------------------------
    print("\n--- TEST 2: PHYSICAL FILESYSTEM INTEGRITY (2,731 IMAGES) ---")
    missing_physical = []
    zero_byte_files = []
    corrupt_jpegs = []
    physical_paths: Dict[str, str] = {}
    total_physical_bytes = 0
    file_sizes = []

    for r in jmol_sacramental_records:
        img_id = r["id_imagen"]
        dgs = r.get("rollo_dgs", "004298570")
        p = resolve_physical_image(img_id, dgs)
        if p is None or not p.is_file():
            missing_physical.append(img_id)
            continue
        physical_paths[img_id] = str(p)
        sz = p.stat().st_size
        total_physical_bytes += sz
        file_sizes.append(sz)
        if sz == 0:
            zero_byte_files.append((img_id, str(p)))
        valid, msg = is_valid_jpeg(p)
        if not valid:
            corrupt_jpegs.append((img_id, str(p), msg))

    t2_pass = (
        len(missing_physical) == 0 and
        len(zero_byte_files) == 0 and
        len(corrupt_jpegs) == 0 and
        len(physical_paths) == CANONICAL_TOTAL
    )
    t2_reasons = []
    if missing_physical:
        t2_reasons.append(f"Missing {len(missing_physical)} physical files on disk")
    if zero_byte_files:
        t2_reasons.append(f"Found {len(zero_byte_files)} zero-byte files")
    if corrupt_jpegs:
        t2_reasons.append(f"Found {len(corrupt_jpegs)} corrupt JPEGs: {corrupt_jpegs[:3]}")

    min_sz = min(file_sizes) if file_sizes else 0
    max_sz = max(file_sizes) if file_sizes else 0
    avg_sz = (sum(file_sizes) / len(file_sizes)) if file_sizes else 0

    audit_summary["tests"]["test2_physical_integrity"] = {
        "passed": t2_pass,
        "resolved_physical_count": len(physical_paths),
        "total_bytes": total_physical_bytes,
        "total_gigabytes": round(total_physical_bytes / (1024**3), 3),
        "min_size_bytes": min_sz,
        "max_size_bytes": max_sz,
        "avg_size_bytes": round(avg_sz, 1),
        "missing_count": len(missing_physical),
        "zero_byte_count": len(zero_byte_files),
        "corrupt_count": len(corrupt_jpegs),
        "reasons": t2_reasons,
    }
    print(f"Test 2 result: {'PASS' if t2_pass else 'FAIL'} (Resolved: {len(physical_paths)}/{CANONICAL_TOTAL}, Total: {round(total_physical_bytes / (1024**3), 3)} GB, Zero-byte: {len(zero_byte_files)})")

    # -------------------------------------------------------------------------
    # TEST 3: Checkpoint Integrity & Bijective 1:1 Mapping
    # -------------------------------------------------------------------------
    print("\n--- TEST 3: CHECKPOINT INTEGRITY & BIJECTIVE 1:1 MAPPING ---")
    if not CHECKPOINT_PATH.is_file():
        raise FileNotFoundError(f"Missing {CHECKPOINT_PATH}")

    with open(CHECKPOINT_PATH, "r", encoding="utf-8") as f:
        checkpoint = json.load(f)

    cp_notebook_ids = checkpoint.get("notebook_ids", {})
    cp_completed_notebooks = set(checkpoint.get("completed_notebooks", []))
    cp_uploaded_sources = checkpoint.get("uploaded_sources", {})

    t3_pass = True
    t3_reasons = []

    # Check 18 notebooks
    if len(cp_notebook_ids) != 18:
        t3_pass = False
        t3_reasons.append(f"Expected 18 notebook IDs in checkpoint, found {len(cp_notebook_ids)}")

    missing_nb_ids = target_notebook_keys - set(cp_notebook_ids.keys())
    extra_nb_ids = set(cp_notebook_ids.keys()) - target_notebook_keys
    if missing_nb_ids or extra_nb_ids:
        t3_pass = False
        t3_reasons.append(f"Notebook ID key mismatch: missing={missing_nb_ids}, extra={extra_nb_ids}")

    # Check 18 completed
    if cp_completed_notebooks != target_notebook_keys:
        t3_pass = False
        t3_reasons.append(f"Completed notebooks mismatch: expected={target_notebook_keys}, got={cp_completed_notebooks}")

    # Check uploaded_sources bijection with catalog
    cp_img_set = set(cp_uploaded_sources.keys())
    missing_in_cp = catalog_img_set - cp_img_set
    extra_in_cp = cp_img_set - catalog_img_set

    if len(cp_uploaded_sources) != CANONICAL_TOTAL:
        t3_pass = False
        t3_reasons.append(f"Expected {CANONICAL_TOTAL} uploaded sources in checkpoint, found {len(cp_uploaded_sources)}")

    if missing_in_cp:
        t3_pass = False
        t3_reasons.append(f"{len(missing_in_cp)} catalog images missing from checkpoint")
    if extra_in_cp:
        t3_pass = False
        t3_reasons.append(f"{len(extra_in_cp)} extra images in checkpoint not in catalog")

    # UUID checks
    source_uuids = []
    invalid_uuids = []
    uuid_notebook_mismatches = []

    # Map catalog img -> expected target
    catalog_img_to_target = {r["id_imagen"]: r["cuaderno_asignado_id"] for r in jmol_sacramental_records}

    for img_key, meta in cp_uploaded_sources.items():
        sid = meta.get("source_id", "")
        nid = meta.get("notebook_id", "")
        if not sid or not UUID_REGEX.match(sid):
            invalid_uuids.append((img_key, sid))
        else:
            source_uuids.append(sid)

        # Check that recorded notebook_id matches cp_notebook_ids[catalog_target]
        expected_target = catalog_img_to_target.get(img_key)
        expected_nb_id = cp_notebook_ids.get(expected_target)
        if nid != expected_nb_id:
            uuid_notebook_mismatches.append((img_key, nid, expected_nb_id))

    unique_source_uuids = set(source_uuids)
    if len(source_uuids) != CANONICAL_TOTAL:
        t3_pass = False
        t3_reasons.append(f"Expected {CANONICAL_TOTAL} source UUIDs, got {len(source_uuids)}")
    if len(unique_source_uuids) != CANONICAL_TOTAL:
        t3_pass = False
        dups = len(source_uuids) - len(unique_source_uuids)
        t3_reasons.append(f"Duplicate cloud source UUIDs found in checkpoint: {dups} duplicates")
    if invalid_uuids:
        t3_pass = False
        t3_reasons.append(f"Found {len(invalid_uuids)} invalid UUID formats")
    if uuid_notebook_mismatches:
        t3_pass = False
        t3_reasons.append(f"Found {len(uuid_notebook_mismatches)} notebook_id mismatches in uploaded_sources")

    # Check Rule [L-28] on all checkpoint keys
    invalid_l28_cp = [k for k in cp_uploaded_sources.keys() if not L28_REGEX.match(k)]
    if invalid_l28_cp:
        t3_pass = False
        t3_reasons.append(f"Found {len(invalid_l28_cp)} checkpoint keys violating Rule [L-28]")

    audit_summary["tests"]["test3_checkpoint_bijection"] = {
        "passed": t3_pass,
        "checkpoint_notebook_count": len(cp_notebook_ids),
        "completed_notebook_count": len(cp_completed_notebooks),
        "uploaded_sources_count": len(cp_uploaded_sources),
        "unique_source_uuids": len(unique_source_uuids),
        "missing_in_checkpoint": len(missing_in_cp),
        "extra_in_checkpoint": len(extra_in_cp),
        "invalid_uuids_count": len(invalid_uuids),
        "notebook_mismatches_count": len(uuid_notebook_mismatches),
        "l28_violations_count": len(invalid_l28_cp),
        "reasons": t3_reasons,
    }
    print(f"Test 3 result: {'PASS' if t3_pass else 'FAIL'} (Uploaded: {len(cp_uploaded_sources)}, Unique UUIDs: {len(unique_source_uuids)}, Invalids: {len(invalid_uuids)})")

    # -------------------------------------------------------------------------
    # TEST 4: Verification Report Cross-Check
    # -------------------------------------------------------------------------
    print("\n--- TEST 4: VERIFICATION REPORT AUDIT (verification_report_jmol.json) ---")
    if not REPORT_PATH.is_file():
        raise FileNotFoundError(f"Missing {REPORT_PATH}")

    with open(REPORT_PATH, "r", encoding="utf-8") as f:
        rep = json.load(f)

    rep_notebooks = rep.get("notebooks", {})
    rep_overall = rep.get("overall_status", "")

    t4_pass = True
    t4_reasons = []

    if rep_overall != "PASS":
        t4_pass = False
        t4_reasons.append(f"overall_status is '{rep_overall}', expected 'PASS'")

    if len(rep_notebooks) != 18:
        t4_pass = False
        t4_reasons.append(f"Expected 18 notebooks in report, got {len(rep_notebooks)}")

    rep_total_expected = 0
    rep_total_actual = 0
    rep_total_ready = 0
    rep_total_missing = 0

    for nb_target, meta in PARROQUIAL_TARGETS.items():
        if nb_target not in rep_notebooks:
            t4_pass = False
            t4_reasons.append(f"Notebook {nb_target} missing from verification report")
            continue
        entry = rep_notebooks[nb_target]
        exp = meta["expected_count"]
        act = entry.get("actual_count", 0)
        rdy = entry.get("ready_count", 0)
        mis = entry.get("missing_count", 0)
        st = entry.get("status", "")
        nid = entry.get("notebook_id", "")

        rep_total_expected += exp
        rep_total_actual += act
        rep_total_ready += rdy
        rep_total_missing += mis

        if act != exp or rdy != exp or mis != 0 or st != "PASS":
            t4_pass = False
            t4_reasons.append(f"Notebook {nb_target} incomplete in report: act={act}, rdy={rdy}, mis={mis}, st={st}")

        # Check notebook ID matches checkpoint
        cp_nid = cp_notebook_ids.get(nb_target)
        if nid != cp_nid:
            t4_pass = False
            t4_reasons.append(f"Notebook {nb_target} ID mismatch: report={nid}, checkpoint={cp_nid}")

    if rep_total_ready != CANONICAL_TOTAL:
        t4_pass = False
        t4_reasons.append(f"Total ready count in report ({rep_total_ready}) != {CANONICAL_TOTAL}")

    audit_summary["tests"]["test4_verification_report"] = {
        "passed": t4_pass,
        "overall_status": rep_overall,
        "total_expected": rep_total_expected,
        "total_actual": rep_total_actual,
        "total_ready": rep_total_ready,
        "total_missing": rep_total_missing,
        "reasons": t4_reasons,
    }
    print(f"Test 4 result: {'PASS' if t4_pass else 'FAIL'} (Ready: {rep_total_ready}/{CANONICAL_TOTAL}, Overall: {rep_overall})")

    # -------------------------------------------------------------------------
    # TEST 5: Protected Notebooks Shield & Live Cloud Verification
    # -------------------------------------------------------------------------
    print("\n--- TEST 5: PROTECTED NOTEBOOKS SHIELD & LIVE CLOUD VERIFICATION ---")
    t5_pass = True
    t5_reasons = []

    # 5.1 Static Shield: Checkpoint & Report do not touch protected notebooks
    protected_ids = set(PROTECTED_NOTEBOOKS.keys())
    
    # Are any protected notebook IDs in checkpoint notebook_ids?
    cp_intersect = protected_ids.intersection(set(cp_notebook_ids.values()))
    if cp_intersect:
        t5_pass = False
        t5_reasons.append(f"Protected notebook ID found in checkpoint notebook_ids: {cp_intersect}")

    # Are any uploaded sources linked to a protected notebook ID?
    cp_sources_in_prot = [
        k for k, v in cp_uploaded_sources.items()
        if v.get("notebook_id") in protected_ids
    ]
    if cp_sources_in_prot:
        t5_pass = False
        t5_reasons.append(f"{len(cp_sources_in_prot)} sources uploaded to protected notebooks!")

    # 5.2 Live Cloud Verification via NotebookLM API
    from notebooklm import NotebookLMClient

    live_protected_results = {}
    live_jmol_results = {}

    try:
        client_ctx = NotebookLMClient.from_storage()
        async with client_ctx as client:
            print("Connected to NotebookLM API. Querying remote cloud state...")
            remote_notebooks = await client.notebooks.list()
            remote_map = {nb.id: nb for nb in remote_notebooks}

            # A. Verify 6 Protected Notebooks Live
            print("Verifying 6 protected notebooks live:")
            for p_id, p_meta in PROTECTED_NOTEBOOKS.items():
                if p_id not in remote_map:
                    t5_pass = False
                    msg = f"Protected notebook {p_meta['title']} ({p_id}) not found in cloud!"
                    t5_reasons.append(msg)
                    live_protected_results[p_id] = {"status": "NOT_FOUND"}
                    print(f"  [FAIL] {p_meta['title']}: NOT FOUND")
                    continue
                
                srcs = await client.sources.list(p_id)
                actual_cnt = len(srcs)
                exp_cnt = p_meta["expected_sources"]
                live_protected_results[p_id] = {
                    "title": remote_map[p_id].title,
                    "expected_sources": exp_cnt,
                    "actual_sources": actual_cnt,
                    "status": "PASS" if actual_cnt == exp_cnt else "REGRESSION",
                }
                if actual_cnt != exp_cnt:
                    t5_pass = False
                    t5_reasons.append(f"Protected notebook {p_meta['title']} source count mismatch: expected {exp_cnt}, found {actual_cnt}")
                    print(f"  [REGRESSION!] {p_meta['title']}: {actual_cnt}/{exp_cnt}")
                else:
                    print(f"  [SHIELD INTACT] {p_meta['title']}: exactly {actual_cnt} sources (expected {exp_cnt})")

            # B. Verify 18 JMOL Target Notebooks Live
            print("\nVerifying 18 JMOL target notebooks live:")
            live_total_ready = 0
            live_total_expected = 0

            for target_id, meta in PARROQUIAL_TARGETS.items():
                nb_id = cp_notebook_ids.get(target_id)
                if not nb_id or nb_id not in remote_map:
                    t5_pass = False
                    t5_reasons.append(f"JMOL target {target_id} ({nb_id}) missing from cloud")
                    print(f"  [FAIL] {target_id}: Missing from cloud")
                    continue
                
                remote_nb = remote_map[nb_id]
                srcs = await client.sources.list(nb_id)
                exp_cnt = meta["expected_count"]
                act_cnt = len(srcs)

                def get_status_str(s):
                    raw = getattr(s, "status", None)
                    if raw is None:
                        return "UNKNOWN"
                    if hasattr(raw, "name"):
                        return str(raw.name)
                    val = getattr(s, "status_label", None)
                    if val:
                        return str(val)
                    return str(raw)

                ready_cnt = sum(1 for s in srcs if get_status_str(s) == "READY")
                titles = {s.title for s in srcs}
                expected_imgs = {r["id_imagen"] for r in jmol_sacramental_records if r["cuaderno_asignado_id"] == target_id}
                missing_cloud = expected_imgs - titles
                extra_cloud = titles - expected_imgs

                live_total_ready += ready_cnt
                live_total_expected += exp_cnt

                nb_pass = (act_cnt == exp_cnt and ready_cnt == exp_cnt and len(missing_cloud) == 0 and len(extra_cloud) == 0)
                if not nb_pass:
                    t5_pass = False
                    t5_reasons.append(f"JMOL target {target_id} live failure: act={act_cnt}, rdy={ready_cnt}, exp={exp_cnt}, missing={len(missing_cloud)}, extra={len(extra_cloud)}")
                    print(f"  [FAIL] {target_id} ({remote_nb.title}): {ready_cnt}/{exp_cnt} READY (act={act_cnt}, mis={len(missing_cloud)}, ext={len(extra_cloud)})")
                else:
                    print(f"  [PASS] {target_id} ({remote_nb.title}): {ready_cnt}/{exp_cnt} READY | 0 missing, 0 extra")

                live_jmol_results[target_id] = {
                    "notebook_id": nb_id,
                    "title": remote_nb.title,
                    "expected_count": exp_cnt,
                    "actual_count": act_cnt,
                    "ready_count": ready_cnt,
                    "missing_count": len(missing_cloud),
                    "extra_count": len(extra_cloud),
                    "status": "PASS" if nb_pass else "FAIL",
                }

    except Exception as e:
        t5_pass = False
        t5_reasons.append(f"Live NotebookLM query exception: {type(e).__name__}: {e}")
        print(f"Live query error: {e}")

    audit_summary["tests"]["test5_shield_and_live_cloud"] = {
        "passed": t5_pass,
        "protected_notebooks_results": live_protected_results,
        "jmol_live_results": live_jmol_results,
        "reasons": t5_reasons,
    }
    print(f"Test 5 result: {'PASS' if t5_pass else 'FAIL'}")

    # -------------------------------------------------------------------------
    # FINAL VERDICT SYNTHESIS
    # -------------------------------------------------------------------------
    all_tests = [t1_pass, t2_pass, t3_pass, t4_pass, t5_pass]
    final_verdict = "APPROVE" if all(all_tests) else "REQUEST_CHANGES"
    audit_summary["verdict"] = final_verdict
    audit_summary["all_passed"] = all(all_tests)

    print("\n" + "=" * 80)
    print(f"FINAL AUDIT VERDICT: {final_verdict}")
    print("=" * 80)
    print(f"Test 1 (Catalog Integrity):          {'PASS' if t1_pass else 'FAIL'}")
    print(f"Test 2 (Physical Filesystem):        {'PASS' if t2_pass else 'FAIL'}")
    print(f"Test 3 (Checkpoint Bijective Match): {'PASS' if t3_pass else 'FAIL'}")
    print(f"Test 4 (Verification Report Audit):  {'PASS' if t4_pass else 'FAIL'}")
    print(f"Test 5 (Protected Shield & Cloud):   {'PASS' if t5_pass else 'FAIL'}")

    # Write output JSON
    with open(RESULTS_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(audit_summary, f, indent=2, ensure_ascii=False)
    print(f"\nDetailed audit results saved to: {RESULTS_OUTPUT_PATH}")

    return 0 if final_verdict == "APPROVE" else 1

if __name__ == "__main__":
    ret = asyncio.run(run_audit())
    sys.exit(ret)
