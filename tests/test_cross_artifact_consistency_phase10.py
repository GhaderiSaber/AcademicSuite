#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_cross_artifact_consistency_phase10.py

Comprehensive Phase 10 Test Suite:
1. 3-Way Discrepancy Detection Across the Triad (.json, .md, .docx)
   (e.g., β = .42 in JSON vs β = .37 in MD vs β = .39 in DOCX -> FAIL)
2. Table Concordance Validation across n, mean, SD, p, effect size, and CI
3. Deterministic Structured DOCX Generation (Zero Authoring Drift)
4. Authoritative Stage Manifest Integration (ManifestCrossAgreementError)
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
import zipfile

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from validators.result_consistency.validator import (
    validate_cross_artifacts,
    extract_markdown_tables,
    extract_docx_tables,
    extract_docx_text,
    audit_table_concordance,
    compare_artifacts_pairwise
)
from scripts.structured_docx_generator import build_structured_docx
from scripts.stage_manifest_engine import (
    build_stage_manifest,
    ManifestCrossAgreementError
)


class TestCrossArtifactConsistencyPhase10(unittest.TestCase):
    """Unit tests for Phase 10 Cross-Artifact Consistency Validation."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="phase10_test_")
        self.stage_dir = os.path.join(self.temp_dir, "stage_06_hypothesis_1")
        os.makedirs(self.stage_dir, exist_ok=True)

        self.json_file = os.path.join(self.stage_dir, "06_hypothesis_1.json")
        self.md_file = os.path.join(self.stage_dir, "06_hypothesis_1.md")
        self.docx_file = os.path.join(self.stage_dir, "06_hypothesis_1.docx")

        self.valid_stats = {
            "stage_id": "06_hypothesis_1",
            "sample_size": 120,
            "f_stat": 14.52,
            "t_stat": 3.81,
            "beta": 0.42,
            "p_value": 0.001,
            "effect_size": 0.28,
            "ci": [0.15, 0.45],
            "table_data": [
                {
                    "name": "مؤلفه اول",
                    "n": 120,
                    "mean": 24.50,
                    "sd": 4.12,
                    "f": 14.52,
                    "t": 3.81,
                    "beta": 0.42,
                    "p": 0.001,
                    "effect_size": 0.28,
                    "ci": [0.15, 0.45]
                }
            ]
        }

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _write_docx_with_text(self, path: str, text: str):
        """Helper to create a valid minimal DOCX package with specific text."""
        xml_text = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">\n'
            f'  <w:body><w:p><w:r><w:t>{text}</w:t></w:r></w:p></w:body>\n'
            '</w:document>'
        )
        content_types = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
            '  <Default Extension="xml" ContentType="application/xml"/>\n'
            '  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>\n'
            '</Types>'
        )
        with zipfile.ZipFile(path, "w") as zf:
            zf.writestr("[Content_Types].xml", content_types)
            zf.writestr("word/document.xml", xml_text)

    def test_01_user_scenario_three_way_beta_discrepancy(self):
        """
        Tests the explicit user prompt requirement:
        result.json: beta = .42
        result.md: beta = .37
        result.docx: beta = .39
        System MUST automatically reject the stage with FAIL.
        """
        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(self.valid_stats, f)  # beta = 0.42

        # Markdown specifies beta = 0.37
        md_text = (
            "# بررسی فرضیه اول\n\n"
            "یافته‌ها نشان داد که ضریب مسیر استاندارد شده برابر با beta = 0.37 برآورد شد."
        )
        with open(self.md_file, "w", encoding="utf-8") as f:
            f.write(md_text)

        # Word document specifies beta = 0.39
        docx_text = "یافته‌های پژوهش نشان داد که مقدار ضریب بتا برابر با β = 0.39 می‌باشد."
        self._write_docx_with_text(self.docx_file, docx_text)

        res = validate_cross_artifacts(
            json_path=self.json_file,
            md_path=self.md_file,
            docx_path=self.docx_file
        )

        self.assertEqual(res["verdict"], "FAIL")
        # Ensure errors capture both the MD contradiction and the DOCX contradiction
        error_blob = " ".join(res["errors"])
        self.assertIn("0.37", error_blob)
        self.assertIn("0.39", error_blob)
        self.assertTrue(len(res["errors"]) >= 2)

    def test_02_pairwise_md_docx_beta_mismatch(self):
        """Tests that a mismatch between MD and DOCX is caught and rejected."""
        stats = dict(self.valid_stats)
        stats["beta"] = 0.42
        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(stats, f)

        # MD matches JSON (0.42)
        with open(self.md_file, "w", encoding="utf-8") as f:
            f.write("تحلیل رگرسیون حاکی از β = 0.42 بود.")

        # DOCX contradicts (0.39)
        self._write_docx_with_text(self.docx_file, "گزارش نهایی وکیل: β = 0.39 برآورد گردید.")

        res = validate_cross_artifacts(self.json_file, self.md_file, self.docx_file)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertTrue(any("0.39" in err for err in res["errors"]))

    def test_03_table_concordance_mean_mismatch(self):
        """Table reports Mean = 25.40, but JSON source specifies Mean = 24.50 -> FAIL."""
        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(self.valid_stats, f)

        # Markdown table with altered Mean
        md_text = (
            "# جدول نتایج\n\n"
            "| شاخص | تعداد | میانگین | انحراف استاندارد | سطح معناداری | فاصله اطمینان |\n"
            "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
            "| مؤلفه اول | 120 | 25.40 | 4.12 | ۰.۰۰۱ > p | [0.15, 0.45] |\n"
        )
        with open(self.md_file, "w", encoding="utf-8") as f:
            f.write(md_text)

        build_structured_docx(self.json_file, self.md_file, self.docx_file)

        # Cross validate MD (which has the error)
        res = validate_cross_artifacts(self.json_file, md_path=self.md_file)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertTrue(any("25.4" in err and "24.5" in err for err in res["errors"]))

    def test_04_table_concordance_sd_mismatch(self):
        """Table reports SD = 5.20, but JSON specifies SD = 4.12 -> FAIL."""
        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(self.valid_stats, f)

        md_text = (
            "# جدول ۴-۳\n\n"
            "| شاخص | تعداد | میانگین | انحراف استاندارد | سطح معناداری |\n"
            "| :--- | :--- | :--- | :--- | :--- |\n"
            "| مؤلفه اول | 120 | 24.50 | 5.20 | ۰.۰۰۱ > p |\n"
        )
        with open(self.md_file, "w", encoding="utf-8") as f:
            f.write(md_text)

        res = validate_cross_artifacts(self.json_file, md_path=self.md_file)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertTrue(any("5.2" in err and "4.12" in err for err in res["errors"]))

    def test_05_table_concordance_ci_mismatch(self):
        """Table reports CI = [0.20, 0.50], but JSON specifies CI = [0.15, 0.45] -> FAIL."""
        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(self.valid_stats, f)

        md_text = (
            "# جدول ۴-۳\n\n"
            "| متغیر | تعداد | میانگین | انحراف معیار | فاصله اطمینان |\n"
            "| :--- | :--- | :--- | :--- | :--- |\n"
            "| مؤلفه اول | 120 | 24.50 | 4.12 | [0.20, 0.50] |\n"
        )
        with open(self.md_file, "w", encoding="utf-8") as f:
            f.write(md_text)

        res = validate_cross_artifacts(self.json_file, md_path=self.md_file)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertTrue(any("Confidence interval" in err for err in res["errors"]))

    def test_06_table_concordance_p_value_mismatch(self):
        """Table reports p = 0.042, but JSON specifies p = 0.001 -> FAIL."""
        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(self.valid_stats, f)

        md_text = (
            "# جدول ۴-۳\n\n"
            "| متغیر | حجم نمونه | آماره آزمون | سطح معناداری |\n"
            "| :--- | :--- | :--- | :--- |\n"
            "| مؤلفه اول | 120 | 14.52 | 0.042 |\n"
        )
        with open(self.md_file, "w", encoding="utf-8") as f:
            f.write(md_text)

        res = validate_cross_artifacts(self.json_file, md_path=self.md_file)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertTrue(any("p-value" in err for err in res["errors"]))

    def test_07_table_concordance_effect_size_mismatch(self):
        """Table reports effect size = 0.18, but JSON specifies effect_size = 0.28 -> FAIL."""
        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(self.valid_stats, f)

        md_text = (
            "# جدول ۴-۳\n\n"
            "| متغیر | تعداد | میانگین | اندازه اثر |\n"
            "| :--- | :--- | :--- | :--- |\n"
            "| مؤلفه اول | 120 | 24.50 | 0.18 |\n"
        )
        with open(self.md_file, "w", encoding="utf-8") as f:
            f.write(md_text)

        res = validate_cross_artifacts(self.json_file, md_path=self.md_file)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertTrue(any("0.18" in err and "0.28" in err for err in res["errors"]))

    def test_08_table_concordance_sample_size_mismatch(self):
        """Table reports N = 80, but JSON specifies N = 120 -> FAIL."""
        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(self.valid_stats, f)

        md_text = (
            "# جدول ۴-۳\n\n"
            "| متغیر | تعداد | میانگین | انحراف معیار |\n"
            "| :--- | :--- | :--- | :--- |\n"
            "| مؤلفه اول | 80 | 24.50 | 4.12 |\n"
        )
        with open(self.md_file, "w", encoding="utf-8") as f:
            f.write(md_text)

        res = validate_cross_artifacts(self.json_file, md_path=self.md_file)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertTrue(any("80" in err and "120" in err for err in res["errors"]))

    def test_09_structured_docx_compiler_guarantees_concordance(self):
        """
        Tests that generating DOCX via scripts/structured_docx_generator.py
        pulls data directly from JSON and produces zero discrepancies.
        """
        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(self.valid_stats, f, indent=2)

        md_narrative = (
            "# یافته‌های فرضیه اول\n\n"
            "تحلیل واریانس با N = 120 اجرا شد و حاکی از F = 14.52, p < 0.001, eta_p^2 = 0.28 بود. "
            "ضریب استاندارد رگرسیون beta = 0.42 و آماره آزمون t = 3.81 محاسبه گردید.\n"
        )
        with open(self.md_file, "w", encoding="utf-8") as f:
            f.write(md_narrative)

        # Compile structured DOCX
        doc_out = build_structured_docx(
            json_path=self.json_file,
            md_path=self.md_file,
            out_docx_path=self.docx_file
        )
        self.assertTrue(os.path.exists(doc_out))

        # Check extracted tables from compiled docx
        docx_tables = extract_docx_tables(doc_out)
        self.assertGreaterEqual(len(docx_tables), 1)

        # Cross-validate Triad
        val_res = validate_cross_artifacts(
            json_path=self.json_file,
            md_path=self.md_file,
            docx_path=self.docx_file
        )
        self.assertEqual(val_res["verdict"], "PASS")
        self.assertEqual(val_res["errors"], [])

    def test_10_authoritative_manifest_rejects_discrepancy(self):
        """
        Tests that build_stage_manifest() raises ManifestCrossAgreementError
        when cross-artifact discrepancy exists in the stage directory.
        """
        with open(self.json_file, "w", encoding="utf-8") as f:
            json.dump(self.valid_stats, f)

        # Contradicting MD
        with open(self.md_file, "w", encoding="utf-8") as f:
            f.write("# فرضیه\n\nضریب beta = 0.12 و N = 50 گزارش شد.")

        self._write_docx_with_text(self.docx_file, "ضریب beta = 0.12")

        with self.assertRaises(ManifestCrossAgreementError):
            build_stage_manifest(
                stage_dir=self.stage_dir,
                stage_id="06_hypothesis_1",
                project_id="phase10_study",
                agent="statistics-agent",
                script_or_generator="scripts/structured_docx_generator.py",
                cross_agreement_required=True
            )


if __name__ == "__main__":
    unittest.main()
