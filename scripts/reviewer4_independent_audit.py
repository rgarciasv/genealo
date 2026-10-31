#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adversarial Independent Audit by Reviewer 4.
Verifies Rules [L-28], [L-29], Requirement R3, and checks for integrity violations.
"""

import asyncio
import json
import re
import sys
from pathlib import Path

from notebooklm import NotebookLMClient

BASE_DIR = Path(__file__).resolve().parent.parent

TARGETS = {
    "NRDL-ENSENADA-LEGOS-01": {
        "loc": "Navarredondilla",
        "parroquia": "NRDL",
        "dgs": "004469033",
        "exp": 87,
        "start": 881,
        "end": 967,
    },
    "JMOL-ENSENADA-LEGOS-01": {
        "loc": "San Juan del Molinillo",
        "parroquia": "JMOL",
        "dgs": "004469028",
        "exp": 28,
        "start": 952,
        "end": 979,
    },
    "VLLR-ENSENADA-LEGOS-01": {
        "loc": "El Villarejo",
        "parroquia": "VLLR",
        "dgs": "004469028",
        "exp": 51,
        "start": 901,
        "end": 951,
    },
    "NDRN-ENSENADA-LEGOS-01": {
        "loc": "Navandrinal",
        "parroquia": "NDRN",
        "dgs": "004469028",
        "exp": 34,
        "start": 980,
        "end": 1013,
    },
}

PROTECTED_ID = "7967d647-8ca2-4863-a576-11843e8e8802"
PROTECTED_TITLE = "Lib. Baut. Navarre Vol. 1 (1594-1695)"
PROTECTED_EXP_SOURCES = 188


async def audit():
    print("=" * 70)
    print("STARTING INDEPENDENT ADVERSARIAL AUDIT (REVIEWER 4)")
    print("=" * 70)

    # 1. Load canonical corpus
    corpus_path = BASE_DIR / "catalogo_corpus.json"
    print(f"Loading canonical corpus from {corpus_path}...")
    with open(corpus_path, "r", encoding="utf-8-sig") as f:
        catalog = json.load(f)

    catalog_targets = {}
    for cid, meta in TARGETS.items():
        recs = [r for r in catalog if r.get("cuaderno_asignado_id") == cid]
        assert len(recs) == meta["exp"], f"Catalog has {len(recs)} records for {cid}, expected {meta['exp']}"
        catalog_targets[cid] = recs

    regex_l28 = re.compile(r"^\d{9}_\d{5}\.jpg$")

    # 2. Connect to NotebookLM live
    print("\nConnecting to live NotebookLM account via NotebookLMClient.from_storage()...")
    async with NotebookLMClient.from_storage() as client:
        all_nbs = await client.notebooks.list()
        print(f"Total notebooks discovered in account: {len(all_nbs)}")
        for nb in all_nbs:
            print(f"  Notebook ID: {nb.id} | Title: {nb.title}")

        # 3. Requirement R3: Active Protected Notebook Audit
        print("\n" + "-" * 70)
        print("AUDIT R3: ACTIVE NOTEBOOK SHIELD VERIFICATION")
        print("-" * 70)
        prot_nb = next((n for n in all_nbs if n.id == PROTECTED_ID), None)
        assert prot_nb is not None, f"PROTECTED NOTEBOOK MISSING: ID {PROTECTED_ID} not found!"
        assert prot_nb.title == PROTECTED_TITLE, f"TITLE TAMPERED: {prot_nb.title} != {PROTECTED_TITLE}"

        prot_sources = await client.sources.list(PROTECTED_ID)
        print(f"Protected notebook title: '{prot_nb.title}'")
        print(f"Protected notebook source count: {len(prot_sources)} (expected exactly {PROTECTED_EXP_SOURCES})")
        assert len(prot_sources) == PROTECTED_EXP_SOURCES, (
            f"SOURCE COUNT TAMPERED: Protected notebook has {len(prot_sources)} sources, expected {PROTECTED_EXP_SOURCES}"
        )

        # Cross-check that no Ensenada Legos images were leaked into the protected notebook
        prot_titles = {s.title for s in prot_sources}
        for cid, recs in catalog_targets.items():
            for r in recs:
                img = r["id_imagen"]
                assert img not in prot_titles, (
                    f"INTEGRITY VIOLATION: Source {img} from {cid} was found in protected notebook {PROTECTED_ID}!"
                )
        print("[PASS] Requirement R3 strictly verified: Protected notebook is untouched with 188 sources and zero contamination.")

        # 4. Target Notebooks & Monolocality [L-29] and Naming [L-28]
        print("\n" + "-" * 70)
        print("AUDIT TARGET NOTEBOOKS: MONO-LOCALITY [L-29] & PRIMARY KEY [L-28]")
        print("-" * 70)

        all_seen_target_sources = {}
        for cid, meta in TARGETS.items():
            print(f"\nAuditing Notebook: {cid}")
            matching_nbs = [n for n in all_nbs if n.title == cid]
            assert len(matching_nbs) == 1, (
                f"Notebook count anomaly for '{cid}': expected exactly 1 notebook, found {len(matching_nbs)}"
            )
            nb = matching_nbs[0]
            print(f"  Verified unique notebook instance: ID={nb.id}, Title='{nb.title}'")

            sources = await client.sources.list(nb.id)
            print(f"  Discovered sources count: {len(sources)} (expected {meta['exp']})")
            assert len(sources) == meta["exp"], (
                f"Source count mismatch for {cid}: expected {meta['exp']}, actual {len(sources)}"
            )

            cat_recs = catalog_targets[cid]
            cat_titles = [r["id_imagen"] for r in cat_recs]
            cat_set = set(cat_titles)

            nb_source_titles = []
            for s in sources:
                t = s.title
                nb_source_titles.append(t)

                # Rule [L-28]: Primary key naming format
                assert regex_l28.match(t), (
                    f"Rule [L-28] VIOLATION: Title '{t}' in {cid} does not match canonical pattern {{DGS}}_{{FOTOGRAMA}}.jpg"
                )
                assert len(t) == 19, (
                    f"Rule [L-28] VIOLATION: Title '{t}' length is {len(t)}, expected 19 (zero-padding truncation detected)"
                )

                # Rule [L-29]: Mono-locality isolation & Parish/Document consistency
                dgs, fotograma_ext = t.split("_")
                fotograma = int(fotograma_ext.split(".")[0])
                assert dgs == meta["dgs"], (
                    f"Rule [L-29] VIOLATION: DGS rollo '{dgs}' in {cid} does not match expected '{meta['dgs']}'"
                )
                assert meta["start"] <= fotograma <= meta["end"], (
                    f"Rule [L-29] VIOLATION: Fotograma {fotograma} in {cid} outside expected range [{meta['start']}, {meta['end']}]"
                )

                # Source status
                assert s.is_ready is True, f"STATUS FAILURE: Source '{t}' ({s.id}) in {cid} is not ready!"
                assert s.is_error is False, f"STATUS FAILURE: Source '{t}' ({s.id}) in {cid} has error status!"

                # Global uniqueness check across all target notebooks
                if t in all_seen_target_sources:
                    raise AssertionError(
                        f"INTEGRITY VIOLATION: Duplicate source '{t}' found across notebooks {cid} and {all_seen_target_sources[t]}"
                    )
                all_seen_target_sources[t] = cid

            # Check 1-to-1 bijection with canonical corpus
            nb_set = set(nb_source_titles)
            missing = cat_set - nb_set
            extra = nb_set - cat_set
            assert len(missing) == 0, f"Missing sources in {cid}: {missing}"
            assert len(extra) == 0, f"Unexpected extra sources in {cid}: {extra}"
            assert len(nb_source_titles) == len(nb_set), f"Duplicate sources inside notebook {cid}"

            print(f"  [PASS] {cid}: Perfectly aligned with catalogo_corpus.json, 100% READY, compliant with [L-28] & [L-29].")

        print("\n" + "=" * 70)
        print("SUMMARY AUDIT METRICS")
        print("=" * 70)
        print(f"Total unique target sources verified: {len(all_seen_target_sources)} / 200")
        assert len(all_seen_target_sources) == 200, f"Expected 200 sources, got {len(all_seen_target_sources)}"
        print("Total target notebooks verified: 4 / 4")
        print("Protected notebook verified: 188 / 188 sources intact")
        print("Corpus alignment rate: 100.0%")
        print("Naming rule [L-28] compliance rate: 100.0%")
        print("Mono-locality rule [L-29] compliance rate: 100.0%")
        print("Integrity violations detected: ZERO")
        print("=" * 70)
        print("VERDICT: ALL VERIFICATIONS PASSED UNCONDITIONALLY.")
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(audit())
