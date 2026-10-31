#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Independent Adversarial Verification Harness by challenger_1.
Tests the live NotebookLM API directly and validates:
1. Notebook Duplication Check across the entire account.
2. Target Notebooks Presence (NRDL-ENSENADA-LEGOS-01, JMOL-ENSENADA-LEGOS-01, VLLR-ENSENADA-LEGOS-01, NDRN-ENSENADA-LEGOS-01).
3. Exact Source Counts (87, 28, 51, 34 -> total 200) and readiness status.
4. Absence of pending, error, or duplicate sources.
5. Bidirectional 1:1 mapping against catalogo_corpus.json and physical files on disk.
6. Protected Notebook 7967d647-8ca2-4863-a576-11843e8e8802 isolation and count (188 sources).
7. Mutual disjointness of source sets across all notebooks.
"""

import asyncio
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Any

from notebooklm import NotebookLMClient

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

BASE_DIR = Path(__file__).resolve().parent.parent
CATALOG_PATH = BASE_DIR / "catalogo_corpus.json"
IMAGES_DIR = BASE_DIR / "imagenes"

PROTECTED_NOTEBOOK_ID = "7967d647-8ca2-4863-a576-11843e8e8802"
PROTECTED_NOTEBOOK_TITLE = "Lib. Baut. Navarre Vol. 1 (1594-1695)"
PROTECTED_SOURCES_COUNT = 188

TARGETS = {
    "NRDL-ENSENADA-LEGOS-01": {
        "expected_count": 87,
        "rollo_dgs": "004469033",
        "start_fotograma": 881,
        "end_fotograma": 967,
    },
    "JMOL-ENSENADA-LEGOS-01": {
        "expected_count": 28,
        "rollo_dgs": "004469028",
        "start_fotograma": 952,
        "end_fotograma": 979,
    },
    "VLLR-ENSENADA-LEGOS-01": {
        "expected_count": 51,
        "rollo_dgs": "004469028",
        "start_fotograma": 901,
        "end_fotograma": 951,
    },
    "NDRN-ENSENADA-LEGOS-01": {
        "expected_count": 34,
        "rollo_dgs": "004469028",
        "start_fotograma": 980,
        "end_fotograma": 1013,
    },
}

FILENAME_REGEX = re.compile(r"^\d{9}_\d{5}\.jpg$")


async def run_adversarial_verification():
    print("=" * 80)
    print("STARTING INDEPENDENT ADVERSARIAL VERIFICATION (challenger_1)")
    print("=" * 80)

    # 1. Load canonical catalog
    with open(CATALOG_PATH, "r", encoding="utf-8-sig") as f:
        corpus = json.load(f)

    catalog_by_notebook: Dict[str, Set[str]] = {k: set() for k in TARGETS}
    for item in corpus:
        nb_id = item.get("cuaderno_asignado_id")
        if nb_id in catalog_by_notebook:
            catalog_by_notebook[nb_id].add(item["id_imagen"])

    all_catalog_images = set().union(*catalog_by_notebook.values())
    assert len(all_catalog_images) == 200, f"Expected 200 catalog images, got {len(all_catalog_images)}"
    print(f"[*] Canonical catalog loaded: exactly 200 target images defined.")

    failures = []
    warnings = []

    async with NotebookLMClient.from_storage() as client:
        # 2. List all notebooks in the account
        print("[*] Querying all notebooks from live NotebookLM API...")
        all_notebooks = await client.notebooks.list()
        print(f"[*] Total notebooks in account: {len(all_notebooks)}")

        # Check duplicate titles
        notebooks_by_title: Dict[str, List[Any]] = {}
        for nb in all_notebooks:
            notebooks_by_title.setdefault(nb.title, []).append(nb)

        for target_title in TARGETS:
            matches = notebooks_by_title.get(target_title, [])
            if len(matches) == 0:
                failures.append(f"CRITICAL: Target notebook '{target_title}' NOT FOUND in live account!")
            elif len(matches) > 1:
                failures.append(
                    f"CRITICAL: Duplicate target notebooks found for '{target_title}'! Count: {len(matches)} IDs: {[m.id for m in matches]}"
                )
            else:
                print(f"    [+] Target notebook '{target_title}' found: ID={matches[0].id} (No duplicates)")

        # Check similar or accidental duplicate titles
        for title in notebooks_by_title:
            if "ENSENADA" in title.upper() and title not in TARGETS:
                print(f"    [i] Note: Other notebook with 'ENSENADA' in title: '{title}' (Count: {len(notebooks_by_title[title])})")

        # 3. Check Protected Active Notebook
        print(f"[*] Verifying Protected Active Notebook '{PROTECTED_NOTEBOOK_ID}'...")
        protected_matches = [nb for nb in all_notebooks if nb.id == PROTECTED_NOTEBOOK_ID]
        if not protected_matches:
            failures.append(f"CRITICAL: Protected notebook '{PROTECTED_NOTEBOOK_ID}' NOT FOUND in account!")
        else:
            p_nb = protected_matches[0]
            if p_nb.title != PROTECTED_NOTEBOOK_TITLE:
                failures.append(
                    f"CRITICAL: Protected notebook title altered! Expected '{PROTECTED_NOTEBOOK_TITLE}', got '{p_nb.title}'"
                )
            print(f"    [+] Title matches: '{p_nb.title}'")

            # Check sources in protected notebook
            p_sources = await client.sources.list(PROTECTED_NOTEBOOK_ID)
            print(f"    [+] Source count in protected notebook: {len(p_sources)} (Expected: {PROTECTED_SOURCES_COUNT})")
            if len(p_sources) != PROTECTED_SOURCES_COUNT:
                failures.append(
                    f"CRITICAL: Protected notebook source count altered! Expected {PROTECTED_SOURCES_COUNT}, got {len(p_sources)}"
                )

            # Check for contamination from Ensenada images into protected notebook
            p_source_titles = {s.title for s in p_sources if s.title}
            contamination = p_source_titles.intersection(all_catalog_images)
            if contamination:
                failures.append(
                    f"CRITICAL: Protected notebook contaminated with Ensenada sources! Contaminated items: {contamination}"
                )
            else:
                print(f"    [+] Zero contamination: None of the 200 Ensenada images exist in protected notebook.")

        # 4. Check each Target Notebook
        notebook_sources_map: Dict[str, Set[str]] = {}
        for target_title, meta in TARGETS.items():
            print(f"\n[*] Auditing Target Notebook '{target_title}'...")
            matches = notebooks_by_title.get(target_title, [])
            if not matches:
                continue
            nb = matches[0]

            sources = await client.sources.list(nb.id)
            print(f"    [+] Sources retrieved: {len(sources)}")

            expected_cnt = meta["expected_count"]
            if len(sources) != expected_cnt:
                failures.append(
                    f"Count mismatch in '{target_title}': expected {expected_cnt}, found {len(sources)}"
                )

            seen_titles = []
            duplicate_titles = set()
            error_sources = []
            pending_sources = []
            ready_sources = []

            for s in sources:
                title = s.title or ""
                seen_titles.append(title)
                if seen_titles.count(title) > 1:
                    duplicate_titles.add(title)

                # Format check
                if not FILENAME_REGEX.match(title):
                    failures.append(f"Format violation in '{target_title}': Source '{title}' does not match regex")

                # Readiness check
                status_name = getattr(s, "status_label", getattr(getattr(s, "status", None), "name", str(getattr(s, "status", ""))))
                is_ready = getattr(s, "is_ready", False) or status_name.upper() == "READY"
                is_error = getattr(s, "is_error", False) or status_name.upper() in ("ERROR", "FAILED")
                is_processing = getattr(s, "is_processing", False) or status_name.upper() in ("PROCESSING", "PENDING")

                if is_ready:
                    ready_sources.append(title)
                elif is_error:
                    error_sources.append((title, status_name))
                elif is_processing:
                    pending_sources.append((title, status_name))
                else:
                    pending_sources.append((title, status_name))

            if duplicate_titles:
                failures.append(f"Duplicate sources in '{target_title}': {duplicate_titles}")

            if error_sources:
                failures.append(f"Error sources in '{target_title}': {error_sources}")

            if pending_sources:
                failures.append(f"Pending sources in '{target_title}': {pending_sources}")

            print(f"    [+] Ready: {len(ready_sources)} | Error: {len(error_sources)} | Pending: {len(pending_sources)} | Duplicates: {len(duplicate_titles)}")

            # Check exact match with canonical catalog
            actual_set = set(seen_titles)
            expected_set = catalog_by_notebook[target_title]

            missing = expected_set - actual_set
            extra = actual_set - expected_set

            if missing:
                failures.append(f"Missing sources in '{target_title}': {sorted(list(missing))}")
            if extra:
                failures.append(f"Extra unexpected sources in '{target_title}': {sorted(list(extra))}")

            if not missing and not extra:
                print(f"    [+] 1:1 Exact Match with canonical catalog ({len(actual_set)} files)")

            # Check fotograma sequence bounds
            fotogramas = []
            for t in actual_set:
                match = FILENAME_REGEX.match(t)
                if match:
                    parts = t.split("_")
                    fotogramas.append(int(parts[1].split(".")[0]))
            fotogramas.sort()
            if fotogramas:
                min_f, max_f = fotogramas[0], fotogramas[-1]
                expected_min, expected_max = meta["start_fotograma"], meta["end_fotograma"]
                if min_f != expected_min or max_f != expected_max:
                    failures.append(
                        f"Range violation in '{target_title}': found [{min_f}, {max_f}], expected [{expected_min}, {expected_max}]"
                    )
                else:
                    print(f"    [+] Fotograma range strictly continuous: [{min_f} .. {max_f}]")

            notebook_sources_map[target_title] = actual_set

        # 5. Check pairwise disjointness across target notebooks
        print("\n[*] Checking pairwise disjointness across the 4 notebooks...")
        nb_names = list(TARGETS.keys())
        for i in range(len(nb_names)):
            for j in range(i + 1, len(nb_names)):
                n1, n2 = nb_names[i], nb_names[j]
                s1 = notebook_sources_map.get(n1, set())
                s2 = notebook_sources_map.get(n2, set())
                overlap = s1.intersection(s2)
                if overlap:
                    failures.append(f"Overlap between '{n1}' and '{n2}': {overlap}")
                else:
                    print(f"    [+] Disjoint: '{n1}' intersect '{n2}' = EMPTY SET")

        # 6. Physical Image Validation on Disk
        print("\n[*] Validating physical disk images in imagenes/ directory...")
        missing_disk = []
        zero_byte_disk = []
        for target_title, titles in notebook_sources_map.items():
            meta = TARGETS[target_title]
            rollo = meta["rollo_dgs"]
            for t in titles:
                disk_path = IMAGES_DIR / f"rollo {rollo}" / t
                if not disk_path.is_file():
                    missing_disk.append(str(disk_path))
                elif disk_path.stat().st_size == 0:
                    zero_byte_disk.append(str(disk_path))

        if missing_disk:
            failures.append(f"Physical images missing on disk: {len(missing_disk)} files, e.g. {missing_disk[:3]}")
        else:
            print("    [+] All 200 physical image files exist on disk.")

        if zero_byte_disk:
            failures.append(f"Physical images with 0 bytes: {zero_byte_disk}")
        else:
            print("    [+] All 200 physical image files have non-zero size.")

        # 7. Spot check reading source details
        print("\n[*] Spot-checking source details from live API...")
        for target_title in TARGETS:
            matches = notebooks_by_title.get(target_title, [])
            if matches:
                nb = matches[0]
                sources = await client.sources.list(nb.id)
                if sources:
                    sample = sources[0]
                    print(f"    [+] Notebook '{target_title}' sample source: ID={sample.id}, Title='{sample.title}'")

    print("\n" + "=" * 80)
    print("ADVERSARIAL VERIFICATION SUMMARY")
    print("=" * 80)
    if warnings:
        print(f"WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")
    if failures:
        print(f"FAILURES ({len(failures)}):")
        for f in failures:
            print(f"  [X] {f}")
        print("\nOVERALL VERDICT: FAIL")
        sys.exit(1)
    else:
        print("ALL ADVERSARIAL CHECKS PASSED: ZERO DEFECTS, ZERO DUPLICATES, ZERO ERRORS, 100% READY.")
        print("\nOVERALL VERDICT: PASS")
        sys.exit(0)


if __name__ == "__main__":
    asyncio.run(run_adversarial_verification())
