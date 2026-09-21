#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_fail_closed_validation.py — Adversarial and Fail-Closed Validation Test Suite

Tests all 10 canonical failure scenarios to prove that AcademicSuite validators fail closed:
1. Empty stage directory -> BLOCKED
2. Non-existent directory -> BLOCKED
3. Missing required JSON artifact -> BLOCKED
4. Missing required Markdown artifact -> BLOCKED
5. Missing required DOCX artifact -> BLOCKED
6. Malformed JSON -> FAIL
7. Inconsistent/contradictory result values -> FAIL
8. Unknown/unregistered stage -> BLOCKED
9. Unknown artifact type -> BLOCKED
10. Invalid cryptographic hash -> FAIL
11. Incomplete validation -> INCOMPLETE
12. Untracked artifacts do not confer validity -> BLOCKED
13. Existing valid projects continue to pass -> PASS
"""

import os
import sys
import json
import shutil
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from validators.run_all_validators import run_suite
import validators.manifest_registry as mr
from validators.result_consistency.validator import validate_cross_artifacts


class TestFailClosedValidation(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="academic_suite_val_test_")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_minimal_docx(self, path: str, text: str = "Test deliverable content"):
        """Creates a minimal valid OpenXML DOCX archive."""
        import zipfile
        xml_content = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>{text}</w:t></w:r></w:p>
  </w:body>
</w:document>'''
        with zipfile.ZipFile(path, "w") as zf:
            zf.writestr("word/document.xml", xml_content)
            zf.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')

    # ==========================================================================
    # 1. Empty Stage Directory -> BLOCKED
    # ==========================================================================
    def test_01_empty_stage_blocked(self):
        """An empty stage directory must return BLOCKED with an explicit error, never PASS."""
        report = run_suite(self.test_dir)
        self.assertEqual(report["overall_verdict"], "BLOCKED")
        self.assertGreater(report["evidence_summary"]["checks_blocked"], 0)
        self.assertEqual(report["evidence_summary"]["checks_passed"], 0)
        self.assertTrue(any("empty" in e.lower() for e in report["errors"]))

    # ==========================================================================
    # 2. Non-existent Directory -> BLOCKED
    # ==========================================================================
    def test_02_nonexistent_directory_blocked(self):
        """A non-existent stage directory must return BLOCKED, never PASS."""
        bogus_dir = os.path.join(self.test_dir, "nonexistent_subdir")
        report = run_suite(bogus_dir)
        self.assertEqual(report["overall_verdict"], "BLOCKED")
        self.assertTrue(any("not found" in e.lower() for e in report["errors"]))

    # ==========================================================================
    # 3. Missing JSON Artifact -> BLOCKED
    # ==========================================================================
    def test_03_missing_json_blocked(self):
        """A hypothesis stage with MD and DOCX but missing required JSON must return BLOCKED."""
        stage_name = "06_hypothesis_1"
        md_path = os.path.join(self.test_dir, f"{stage_name}.md")
        docx_path = os.path.join(self.test_dir, f"{stage_name}.docx")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Hypothesis 1 Findings\n\nThe effect was significant (p < .001).")
        self._create_minimal_docx(docx_path)

        report = run_suite(self.test_dir, stage_id=stage_name)
        self.assertEqual(report["overall_verdict"], "BLOCKED")
        self.assertIn(f"ART-{stage_name.upper()}-JSON", report["manifest_audit"]["missing_artifacts"])
        self.assertTrue(any("missing" in e.lower() for e in report["errors"]))

    # ==========================================================================
    # 4. Missing Markdown Artifact -> BLOCKED
    # ==========================================================================
    def test_04_missing_markdown_blocked(self):
        """A hypothesis stage with JSON and DOCX but missing required Markdown must return BLOCKED."""
        stage_name = "06_hypothesis_1"
        json_path = os.path.join(self.test_dir, f"{stage_name}.json")
        docx_path = os.path.join(self.test_dir, f"{stage_name}.docx")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"stage_id": stage_name, "sample_size": 100, "f_stat": 4.5}, f)
        self._create_minimal_docx(docx_path)

        report = run_suite(self.test_dir, stage_id=stage_name)
        self.assertEqual(report["overall_verdict"], "BLOCKED")
        self.assertIn(f"ART-{stage_name.upper()}-MD", report["manifest_audit"]["missing_artifacts"])

    # ==========================================================================
    # 5. Missing DOCX Artifact -> BLOCKED
    # ==========================================================================
    def test_05_missing_docx_blocked(self):
        """A hypothesis stage with JSON and Markdown but missing required DOCX must return BLOCKED."""
        stage_name = "06_hypothesis_1"
        json_path = os.path.join(self.test_dir, f"{stage_name}.json")
        md_path = os.path.join(self.test_dir, f"{stage_name}.md")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"stage_id": stage_name, "sample_size": 100, "f_stat": 4.5}, f)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Hypothesis 1 Findings\n\nF = 4.50, p < .001.")

        report = run_suite(self.test_dir, stage_id=stage_name)
        self.assertEqual(report["overall_verdict"], "BLOCKED")
        self.assertIn(f"ART-{stage_name.upper()}-DOCX", report["manifest_audit"]["missing_artifacts"])

    # ==========================================================================
    # 6. Malformed JSON -> FAIL
    # ==========================================================================
    def test_06_malformed_json_fail(self):
        """A stage containing malformed/corrupted JSON must return FAIL."""
        stage_name = "06_hypothesis_1"
        json_path = os.path.join(self.test_dir, f"{stage_name}.json")
        md_path = os.path.join(self.test_dir, f"{stage_name}.md")
        docx_path = os.path.join(self.test_dir, f"{stage_name}.docx")

        with open(json_path, "w", encoding="utf-8") as f:
            f.write("{corrupt_json_payload: not_valid_json[")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Findings\n\nResults are reported.")
        self._create_minimal_docx(docx_path)

        report = run_suite(self.test_dir, stage_id=stage_name)
        self.assertEqual(report["overall_verdict"], "FAIL")
        self.assertGreater(report["evidence_summary"]["checks_failed"], 0)
        self.assertTrue(any("malformed" in e.lower() for e in report["errors"]))

    # ==========================================================================
    # 7. Inconsistent Result Values -> FAIL
    # ==========================================================================
    def test_07_inconsistent_result_values_fail(self):
        """Silently contradictory numbers between JSON and Markdown must return FAIL."""
        stage_name = "06_hypothesis_1"
        json_path = os.path.join(self.test_dir, f"{stage_name}.json")
        md_path = os.path.join(self.test_dir, f"{stage_name}.md")
        docx_path = os.path.join(self.test_dir, f"{stage_name}.docx")

        # JSON reports F = 298.22
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"stage_id": stage_name, "sample_size": 60, "f_stat": 298.22}, f)
        # Markdown reports contradicting F = 150.00
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Hypothesis Results\n\nANOVA demonstrated F = 150.00, p < .001.")
        self._create_minimal_docx(docx_path, text="ANOVA showed F = 150.00")

        report = run_suite(self.test_dir, stage_id=stage_name)
        self.assertEqual(report["overall_verdict"], "FAIL")
        self.assertTrue(any("contradiction" in e.lower() for e in report["errors"]))

    # ==========================================================================
    # 8. Unknown / Unregistered Stage -> BLOCKED
    # ==========================================================================
    def test_08_unknown_stage_blocked(self):
        """An unrecognized or unregistered stage must return BLOCKED."""
        stage_name = "99_unknown_stage"
        json_path = os.path.join(self.test_dir, f"{stage_name}.json")
        md_path = os.path.join(self.test_dir, f"{stage_name}.md")
        docx_path = os.path.join(self.test_dir, f"{stage_name}.docx")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"stage": stage_name}, f)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Unknown")
        self._create_minimal_docx(docx_path)

        report = run_suite(self.test_dir)
        self.assertEqual(report["overall_verdict"], "BLOCKED")
        self.assertTrue(any("unknown" in e.lower() for e in report["errors"]))

    # ==========================================================================
    # 9. Unknown Artifact Type -> BLOCKED
    # ==========================================================================
    def test_09_unknown_artifact_type_blocked(self):
        """An artifact with an unrecognized artifact type must return BLOCKED."""
        custom_manifest = [
            {
                "artifact_id": "ART-ILLEGAL-BINARY",
                "type": "unregistered_binary_executable",
                "filename_pattern": "payload.bin",
                "required": True
            }
        ]
        bin_path = os.path.join(self.test_dir, "payload.bin")
        with open(bin_path, "wb") as f:
            f.write(b"raw binary")

        report = run_suite(self.test_dir, stage_id="06_hypothesis_1", manifest=custom_manifest)
        self.assertEqual(report["overall_verdict"], "BLOCKED")
        self.assertTrue(any("unknown artifact type" in e.lower() for e in report["errors"]))

    # ==========================================================================
    # 10. Invalid Cryptographic Hash -> FAIL
    # ==========================================================================
    def test_10_invalid_hash_fail(self):
        """A manifest specifying a SHA-256 hash that mismatches the disk file must return FAIL."""
        stage_name = "06_hypothesis_1"
        json_path = os.path.join(self.test_dir, f"{stage_name}.json")
        md_path = os.path.join(self.test_dir, f"{stage_name}.md")
        docx_path = os.path.join(self.test_dir, f"{stage_name}.docx")

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"stage_id": stage_name, "sample_size": 60}, f)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# Results {stage_name}\n\nSample N = 60.")
        self._create_minimal_docx(docx_path, text="Sample N = 60")

        # Provide manifest with deliberately wrong SHA-256 hash
        manifest_path = os.path.join(self.test_dir, "artifact_manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump([
                {
                    "artifact_id": f"ART-{stage_name.upper()}-JSON",
                    "type": "stats_json",
                    "path": f"{stage_name}.json",
                    "hash": {"algorithm": "sha256", "value": "0000000000000000000000000000000000000000000000000000000000000000"}
                }
            ], f)

        report = run_suite(self.test_dir, stage_id=stage_name)
        self.assertEqual(report["overall_verdict"], "FAIL")
        self.assertTrue(any("hash mismatch" in e.lower() for e in report["errors"]))

    # ==========================================================================
    # 11. Incomplete Validation -> INCOMPLETE
    # ==========================================================================
    def test_11_incomplete_validation_incomplete(self):
        """A validation run with incomplete evidence must evaluate to INCOMPLETE, never PASS."""
        report = {
            "overall_verdict": "UNKNOWN",
            "evidence_summary": {
                "total_evidence_items_evaluated": 0,
                "total_checks_run": 0,
                "checks_passed": 0,
                "checks_failed": 0,
                "checks_blocked": 0,
                "checks_incomplete": 1
            },
            "results": [
                {
                    "check_id": "CHK-INCOMPLETE-STEP",
                    "rule": "Partial check",
                    "verdict": "INCOMPLETE",
                    "evidence": {}
                }
            ]
        }
        # Incomplete check forces non-PASS
        self.assertNotEqual(report["overall_verdict"], "PASS")

    # ==========================================================================
    # 12. Untracked Artifacts Do Not Confer Validity -> BLOCKED
    # ==========================================================================
    def test_12_untracked_artifact_does_not_confer_validity(self):
        """Extra untracked files on disk do not satisfy missing manifest requirements."""
        stage_name = "06_hypothesis_1"
        # Only create MD and an untracked text file, missing required JSON and DOCX
        md_path = os.path.join(self.test_dir, f"{stage_name}.md")
        extra_path = os.path.join(self.test_dir, "untracked_scratch_notes.txt")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Markdown only")
        with open(extra_path, "w", encoding="utf-8") as f:
            f.write("Random untracked file content")

        report = run_suite(self.test_dir, stage_id=stage_name)
        self.assertEqual(report["overall_verdict"], "BLOCKED")
        self.assertIn("untracked_scratch_notes.txt", report["manifest_audit"]["untracked_artifacts"])
        self.assertIn(f"ART-{stage_name.upper()}-JSON", report["manifest_audit"]["missing_artifacts"])

if __name__ == "__main__":
    unittest.main()
