#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_verify_references_persian.py — Regression Test for Persian Citation Verification

Tests that:
1. Fabricated Persian citations with no verified bibliography or DOI return is_verified: False.
2. Legitimate Persian citations matching local verified bibliography return is_verified: True.
"""

import os
import sys
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

SKILL_SCRIPTS = os.path.join(ROOT_DIR, ".agents", "skills", "academic-reference-extractor", "scripts")
if SKILL_SCRIPTS not in sys.path:
    sys.path.insert(0, SKILL_SCRIPTS)

from verify_references import verify_bibliographic_record


class TestPersianReferenceVerification(unittest.TestCase):

    def test_fabricated_persian_citation_rejected(self):
        fake_persian_record = {
            "raw": "قادری، صابر. (۱۴۰۴). تأثیر پرتوهای تله‌پاتی کوانتومی بر متغیرهای نامرئی. مجله پژوهش‌های خیالی، ۱(۱)، ۱-۲۰.",
            "title": "تأثیر پرتوهای تله‌پاتی کوانتومی بر متغیرهای نامرئی",
            "authors": ["صابر قادری"],
            "year": "۱۴۰۴"
        }
        res = verify_bibliographic_record(fake_persian_record)
        self.assertFalse(res.get("is_verified", False))
        self.assertEqual(res.get("confidence"), 0.0)
        self.assertIn("UNVERIFIED", res.get("status", ""))

    def test_verified_local_persian_citation_accepted(self):
        # Create a temporary verified references file
        temp_dir = tempfile.mkdtemp()
        orig_cwd = os.getcwd()
        try:
            os.chdir(temp_dir)
            bib_file = os.path.join(temp_dir, "references.bib")
            with open(bib_file, "w", encoding="utf-8") as f:
                f.write("@article{ghaderi2024,\n  title={اثربخشی درمان مبتنی بر پذیرش و تعهد بر فرسودگی شغلی},\n  author={قادری، صابر},\n  year={1403}\n}\n")

            valid_record = {
                "raw": "قادری، صابر. (۱۴۰۳). اثربخشی درمان مبتنی بر پذیرش و تعهد بر فرسودگی شغلی.",
                "title": "اثربخشی درمان مبتنی بر پذیرش و تعهد بر فرسودگی شغلی",
                "authors": ["صابر قادری"],
                "year": "۱۴۰۳"
            }
            res = verify_bibliographic_record(valid_record)
            self.assertTrue(res.get("is_verified", False))
            self.assertEqual(res.get("status"), "VERIFIED (LOCAL VERIFIED BIBLIOGRAPHY)")
            self.assertGreaterEqual(res.get("confidence", 0), 0.90)
        finally:
            os.chdir(orig_cwd)
            import shutil
            shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
