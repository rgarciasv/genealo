#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit and Adversarial Test Suite for scripts/verify_notebooklm_sources.py
Executed via python -m unittest in .agents/teamwork/test_writer_1/
"""

import asyncio
import json
import os
import sys
import unittest
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from scripts.verify_notebooklm_sources import (
    CANONICAL_FILENAME_REGEX,
    DEFAULT_CATALOG_PATH,
    PROTECTED_EXPECTED_SOURCES_COUNT,
    PROTECTED_NOTEBOOK_ID,
    PROTECTED_NOTEBOOK_TITLE,
    TARGET_NOTEBOOKS,
    TOTAL_EXPECTED_TARGET_SOURCES,
    MockNotebook,
    MockNotebookLMClient,
    MockSource,
    NotebookLMVerifier,
    build_mock_passing_client,
    get_source_status_str,
    is_source_error,
    is_source_ready,
    load_and_verify_canonical_corpus,
)


class TestCanonicalCorpusLoader(unittest.TestCase):
    def test_canonical_corpus_loads_with_bom(self):
        corpus = load_and_verify_canonical_corpus(DEFAULT_CATALOG_PATH)
        self.assertEqual(len(corpus), 4)
        self.assertIn("NRDL-ENSENADA-LEGOS-01", corpus)
        self.assertIn("JMOL-ENSENADA-LEGOS-01", corpus)
        self.assertIn("VLLR-ENSENADA-LEGOS-01", corpus)
        self.assertIn("NDRN-ENSENADA-LEGOS-01", corpus)

    def test_canonical_corpus_exact_counts(self):
        corpus = load_and_verify_canonical_corpus(DEFAULT_CATALOG_PATH)
        self.assertEqual(len(corpus["NRDL-ENSENADA-LEGOS-01"]), 87)
        self.assertEqual(len(corpus["JMOL-ENSENADA-LEGOS-01"]), 28)
        self.assertEqual(len(corpus["VLLR-ENSENADA-LEGOS-01"]), 51)
        self.assertEqual(len(corpus["NDRN-ENSENADA-LEGOS-01"]), 34)
        total = sum(len(v) for v in corpus.values())
        self.assertEqual(total, 200)

    def test_canonical_corpus_naming_compliance(self):
        corpus = load_and_verify_canonical_corpus(DEFAULT_CATALOG_PATH)
        for name, records in corpus.items():
            for r in records:
                img_id = r["id_imagen"]
                self.assertTrue(
                    CANONICAL_FILENAME_REGEX.match(img_id),
                    f"Image ID '{img_id}' violates canonical naming in {name}",
                )


class TestProtectedNotebookAudit(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.corpus = load_and_verify_canonical_corpus(DEFAULT_CATALOG_PATH)

    async def test_protected_notebook_valid_when_188_sources(self):
        client = build_mock_passing_client(self.corpus)
        verifier = NotebookLMVerifier(client=client)
        res = await verifier.verify_protected_notebook(client)
        self.assertTrue(res["valid"])
        self.assertTrue(res["is_alive"])
        self.assertEqual(res["actual_sources"], 188)
        self.assertIsNone(res["error"])

    async def test_protected_notebook_fails_when_sources_altered(self):
        client = build_mock_passing_client(self.corpus)
        # Drop one source
        client.sources._sources_map[PROTECTED_NOTEBOOK_ID].pop()
        verifier = NotebookLMVerifier(client=client)
        res = await verifier.verify_protected_notebook(client)
        self.assertFalse(res["valid"])
        self.assertEqual(res["actual_sources"], 187)
        self.assertIsNotNone(res["error"])
        self.assertTrue(any("mismatch" in d for d in verifier.discrepancies))

    async def test_protected_notebook_fails_when_missing(self):
        client = build_mock_passing_client(self.corpus)
        # Remove protected notebook
        client.notebooks._notebooks = [
            nb for nb in client.notebooks._notebooks if nb.id != PROTECTED_NOTEBOOK_ID
        ]
        verifier = NotebookLMVerifier(client=client)
        res = await verifier.verify_protected_notebook(client)
        self.assertFalse(res["valid"])
        self.assertFalse(res["is_alive"])


class TestTargetNotebooksVerification(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.corpus = load_and_verify_canonical_corpus(DEFAULT_CATALOG_PATH)
        self.test_report_path = Path(__file__).parent / "test_report_temp.json"

    async def asyncTearDown(self):
        if self.test_report_path.is_file():
            self.test_report_path.unlink()

    async def test_all_target_notebooks_and_sources_valid(self):
        client = build_mock_passing_client(self.corpus)
        verifier = NotebookLMVerifier(
            client=client,
            corpus_path=DEFAULT_CATALOG_PATH,
            report_path=self.test_report_path,
        )
        passed, report = await verifier.execute_verification()
        self.assertTrue(passed)
        self.assertEqual(report["overall_status"], "PASS")
        self.assertEqual(report["exit_code"], 0)
        self.assertEqual(report["summary"]["total_sources_ready"], 200)
        self.assertEqual(report["summary"]["total_sources_error"], 0)
        self.assertEqual(report["summary"]["total_sources_missing"], 0)
        self.assertEqual(report["summary"]["total_naming_violations"], 0)
        self.assertEqual(len(report["discrepancies"]), 0)

    async def test_adversarial_zero_truncation_detection(self):
        """[L-28] Verifies that truncated filenames like 00881.jpg are flagged."""
        client = build_mock_passing_client(self.corpus)
        # Inject truncated filename
        client.sources._sources_map["mock-nb-nrdl-01"][0] = MockSource(
            id="bad-trunc-01",
            title="00881.jpg",
            status_name="READY",
            is_ready=True,
        )
        verifier = NotebookLMVerifier(
            client=client,
            corpus_path=DEFAULT_CATALOG_PATH,
            report_path=self.test_report_path,
        )
        passed, report = await verifier.execute_verification()
        self.assertFalse(passed)
        self.assertEqual(report["overall_status"], "FAIL")
        self.assertEqual(report["exit_code"], 1)
        self.assertGreater(report["summary"]["total_naming_violations"], 0)
        self.assertGreater(report["summary"]["total_sources_missing"], 0)

    async def test_adversarial_error_status_detection(self):
        """Verifies that non-ready / error sources are flagged."""
        client = build_mock_passing_client(self.corpus)
        vllr_sources = client.sources._sources_map["mock-nb-vllr-01"]
        vllr_sources[5] = MockSource(
            id="err-vllr-5",
            title=vllr_sources[5].title,
            status_name="ERROR",
            is_ready=False,
            is_error=True,
        )
        verifier = NotebookLMVerifier(
            client=client,
            corpus_path=DEFAULT_CATALOG_PATH,
            report_path=self.test_report_path,
        )
        passed, report = await verifier.execute_verification()
        self.assertFalse(passed)
        self.assertEqual(report["overall_status"], "FAIL")
        self.assertEqual(report["summary"]["total_sources_error"], 1)

    async def test_adversarial_extra_source_detection(self):
        """Verifies that unexpected / extra sources are flagged."""
        client = build_mock_passing_client(self.corpus)
        # Add an extra image from outside
        client.sources._sources_map["mock-nb-jmol-01"].append(
            MockSource(
                id="extra-src-999",
                title="004469028_09999.jpg",
                status_name="READY",
                is_ready=True,
            )
        )
        verifier = NotebookLMVerifier(
            client=client,
            corpus_path=DEFAULT_CATALOG_PATH,
            report_path=self.test_report_path,
        )
        passed, report = await verifier.execute_verification()
        self.assertFalse(passed)
        self.assertEqual(report["overall_status"], "FAIL")
        self.assertEqual(report["summary"]["total_sources_extra"], 1)

    async def test_adversarial_duplicate_source_title_detection(self):
        """Verifies that duplicate sources inside a notebook are flagged."""
        client = build_mock_passing_client(self.corpus)
        # Duplicate the first source in NDRN
        ndrn_sources = client.sources._sources_map["mock-nb-ndrn-01"]
        ndrn_sources.append(
            MockSource(
                id="dup-src-1",
                title=ndrn_sources[0].title,
                status_name="READY",
                is_ready=True,
            )
        )
        verifier = NotebookLMVerifier(
            client=client,
            corpus_path=DEFAULT_CATALOG_PATH,
            report_path=self.test_report_path,
        )
        passed, report = await verifier.execute_verification()
        self.assertFalse(passed)
        self.assertGreater(report["summary"]["total_duplicates"], 0)


if __name__ == "__main__":
    unittest.main()
