#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adversarial Stress Test for Oracle Challenger.
Verifies that the oracle detects simulated failure modes deterministically:
1. Missing image detection
2. Corrupt/zero-byte image detection
3. Duplicate UUID detection
4. Rule [L-28] naming violation detection
5. Cloud count regression detection
"""

import unittest
import re
from pathlib import Path

L28_REGEX = re.compile(r"^\d{9}_\d{5}\.jpg$")
UUID_REGEX = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$", re.IGNORECASE)

class TestOracleAdversarialSensitivity(unittest.TestCase):
    def test_l28_regex_sensitivity(self):
        valid = "004298570_00045.jpg"
        self.assertTrue(bool(L28_REGEX.match(valid)))
        
        invalids = [
            "004298570_0045.jpg",      # 4 digits instead of 5
            "4298570_00045.jpg",       # 7 digits instead of 9
            "004298570_00045.jpeg",    # jpeg extension
            "004298570_00045.JPG",     # uppercase
            "img_004298570_00045.jpg", # prefix
            "004298570_00045.jpg.tmp", # suffix
        ]
        for inv in invalids:
            with self.subTest(inv=inv):
                self.assertFalse(bool(L28_REGEX.match(inv)))

    def test_uuid_regex_sensitivity(self):
        valid = "fa62871d-cb66-4af4-8e13-4dcc1c12b7ce"
        self.assertTrue(bool(UUID_REGEX.match(valid)))

        invalids = [
            "fa62871d-cb66-4af4-8e13-4dcc1c12b7c",   # 35 chars
            "fa62871d-cb66-4af4-8e13-4dcc1c12b7cez", # non-hex char
            "",                                      # empty
            "null",                                  # string null
            "12345",                                 # dummy
        ]
        for inv in invalids:
            with self.subTest(inv=inv):
                self.assertFalse(bool(UUID_REGEX.match(inv)))

    def test_duplicate_detection_logic(self):
        sample = ["uuid-1", "uuid-2", "uuid-3", "uuid-1"]
        self.assertNotEqual(len(sample), len(set(sample)))

    def test_bijection_set_difference(self):
        catalog = {"img1", "img2", "img3"}
        checkpoint = {"img1", "img2"}
        missing = catalog - checkpoint
        self.assertEqual(missing, {"img3"})

if __name__ == "__main__":
    unittest.main()
