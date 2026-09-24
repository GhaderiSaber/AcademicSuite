#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_inquisitive_auditor.py — Comprehensive Test Suite for Hardened Inquisitive Auditor

Verifies eradication of leniency bias ("naive person" flaw):
1. Substantive Density Guard: Low word count narrative strictly FAILS.
2. Chapter 4 Table Mandate: Chapter 4 findings without statistical tables strictly FAILS.
3. Chapter 5 Prose-Only Invariant: Chapter 5 containing tables strictly FAILS.
4. Saber 4-Element Narrative Mandate: Ch 4 missing Context, Data, Table cite, or Verdict FAILS.
5. 4-Element Psychological Mechanism Mandate: Ch 5 missing Finding, Literature, Theory, or Nuance FAILS.
6. Anti-Hollow Stats Gate: JSON files without substantive test statistics strictly FAIL.
7. Required Exact p-value: Primary test statistics without p-values strictly FAIL.
8. Bidirectional Inquest: Text deliverables omitting JSON statistics strictly FAIL.
9. Hardened Adversarial Gate: Open HIGH challenges block PASS (CHALLENGE_BLOCKED).
10. Earned-Score Defense Committee: Empty or hollow deliverables receive <= 10.00 / 20.00 (REJECT).
11. Rigorous Deliverable Certification: Complete, compliant deliverables earn >= 18.00 (PASS_EXCELLENT).
"""

import os
import sys
import json
import shutil
import tempfile
import zipfile
import unittest
import xml.etree.ElementTree as ET

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
for p in (ROOT_DIR, AGENTS_DIR, os.path.join(AGENTS_DIR, "validators"), os.path.join(AGENTS_DIR, "hooks", "agents")):
    if os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)

from validators.academic_chapter_auditor import AcademicChapterAuditor
from validators.numerical_consistency.validator import validate_numbers
from validators.result_consistency.validator import validate_cross_artifacts
from validators.adversarial_challenge_runner import run_adversarial_audit
from validators.defense_readiness_compiler import run_defense_certification
from validators.run_all_validators import run_suite


def create_minimal_docx(docx_path: str, body_xml_content: str):
    """Creates a minimal valid OpenXML .docx file with given body XML content."""
    doc_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">
    <w:body>
        {body_xml_content}
    </w:body>
</w:document>"""
    with zipfile.ZipFile(docx_path, "w") as zf:
        zf.writestr("word/document.xml", doc_xml)


class TestInquisitiveAuditor(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="academic_inquisitive_auditor_test_")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # ==========================================================================
    # 1. Substantive Density & Epistemic Guard Tests
    # ==========================================================================
    def test_01_hollow_text_low_word_count_fails(self):
        """A short vacuous 2-sentence deliverable (< 80 words) strictly FAILS."""
        docx_path = os.path.join(self.test_dir, "draft.docx")
        body_xml = """
        <w:p><w:r><w:t>این یک متن بسیار کوتاه برای آزمودن سیستم اعتبارسنجی است.</w:t></w:r></w:p>
        <w:p><w:r><w:t>جمله دوم نیز کوتاه است و محتوای کافی ندارد.</w:t></w:r></w:p>
        """
        create_minimal_docx(docx_path, body_xml)
        auditor = AcademicChapterAuditor(docx_path=docx_path)
        report = auditor.audit()

        self.assertEqual(report["overall_verdict"], "FAIL")
        density_res = next((r for r in report["results"] if r["check_id"] == "CHK-MINIMUM-SUBSTANTIVE-DENSITY"), None)
        self.assertIsNotNone(density_res)
        self.assertEqual(density_res["verdict"], "FAIL")
        self.assertIn("Substantive density failure", density_res["errors"][0])

    def test_02_chapter4_findings_missing_tables_fails(self):
        """A Chapter 4 hypothesis findings deliverable with ZERO tables strictly FAILS."""
        docx_path = os.path.join(self.test_dir, "ch4_hypothesis_1_findings.docx")
        # 250 words of narrative without tables
        words = ["فرضیه", "پژوهش", "حاضر", "عبارت", "است", "از", "بررسی", "اثربخشی", "مداخله"] * 30
        body_xml = f"<w:p><w:r><w:t>{' '.join(words)}</w:t></w:r></w:p>"
        create_minimal_docx(docx_path, body_xml)

        auditor = AcademicChapterAuditor(docx_path=docx_path)
        report = auditor.audit()

        self.assertEqual(report["overall_verdict"], "FAIL")
        tbl_res = next((r for r in report["results"] if r["check_id"] == "CHK-APA7-TABLE-BORDERS"), None)
        self.assertIsNotNone(tbl_res)
        self.assertEqual(tbl_res["verdict"], "FAIL")
        self.assertIn("strictly requires at least one APA 7 statistical table", tbl_res["errors"][0])

    def test_03_chapter5_with_tables_fails_prose_only_invariant(self):
        """A Chapter 5 discussion deliverable with a table strictly FAILS (Directive 3.1)."""
        docx_path = os.path.join(self.test_dir, "ch5_hypothesis_1_discussion.docx")
        body_xml = """
        <w:p><w:r><w:t>یافته‌های پژوهش نشان داد که مداخله اثربخش بود. این نتیجه همسو با پژوهش احمدی (۱۴۰۱) است. از منظر شناختی و طرحواره درمانی، تغییر باورها سازوکار اصلی است. پیشنهاد می‌شود روان‌شناسان بالینی از این پروتکل استفاده کنند.</w:t></w:r></w:p>
        <w:tbl>
            <w:tr><w:tc><w:p><w:r><w:t>داده نامربوط در فصل ۵</w:t></w:r></w:p></w:tc></w:tr>
        </w:tbl>
        """
        create_minimal_docx(docx_path, body_xml)
        auditor = AcademicChapterAuditor(docx_path=docx_path)
        report = auditor.audit()

        self.assertEqual(report["overall_verdict"], "FAIL")
        prose_res = next((r for r in report["results"] if r["check_id"] == "CHK-CHAPTER5-PROSE-ONLY"), None)
        self.assertIsNotNone(prose_res)
        self.assertEqual(prose_res["verdict"], "FAIL")
        self.assertIn("Directive 3.1 Prose-Only Invariant", prose_res["errors"][0])

    def test_04_chapter4_missing_saber_4element_fails(self):
        """Chapter 4 findings missing in-text table reference or decision strictly FAILS."""
        docx_path = os.path.join(self.test_dir, "ch4_hypothesis_findings.docx")
        # Narrative mentions hypothesis and stats, but omits in-text table reference and verdict
        narrative = "فرضیه پژوهش مورد ارزیابی قرار گرفت. مقادیر محاسبه شده عبارتند از t = 2.45 و p = 0.015 با حجم نمونه مناسب."
        words = [narrative] * 20
        body_xml = f"""
        <w:p><w:r><w:t>{' '.join(words)}</w:t></w:r></w:p>
        <w:p><w:r><w:t>جدول ۱: نتایج آزمون تی</w:t></w:r></w:p>
        <w:tbl><w:tr><w:tc><w:p><w:r><w:t>Cell</w:t></w:r></w:p></w:tc></w:tr></w:tbl>
        <w:p><w:r><w:t>یادداشت: p &lt; .05</w:t></w:r></w:p>
        """
        create_minimal_docx(docx_path, body_xml)
        auditor = AcademicChapterAuditor(docx_path=docx_path)
        report = auditor.audit()

        saber_res = next((r for r in report["results"] if r["check_id"] == "CHK-SABER-4ELEMENT-NARRATIVE"), None)
        self.assertIsNotNone(saber_res)
        self.assertEqual(saber_res["verdict"], "FAIL")
        self.assertIn("missing required epistemic components", saber_res["errors"][0])

    def test_05_chapter5_missing_psychological_mechanism_fails(self):
        """Chapter 5 discussion missing theoretical psychological mechanism strictly FAILS."""
        docx_path = os.path.join(self.test_dir, "ch5_discussion.docx")
        # Mentions finding and literature concordance, but no psychological theory/mechanism
        narrative = "یافته‌های پژوهش نشان داد که متغیرها معنادار بودند. این یافته همسو با اسمیت (۲۰۲۲) است. در نتیجه کاربردهای بالینی متعددی متصور است."
        words = [narrative] * 25
        body_xml = f"<w:p><w:r><w:t>{' '.join(words)}</w:t></w:r></w:p>"
        create_minimal_docx(docx_path, body_xml)
        auditor = AcademicChapterAuditor(docx_path=docx_path)
        report = auditor.audit()

        mech_res = next((r for r in report["results"] if r["check_id"] == "CHK-CHAPTER5-PSYCH-MECHANISM"), None)
        self.assertIsNotNone(mech_res)
        self.assertEqual(mech_res["verdict"], "FAIL")
        self.assertIn("missing required components", mech_res["errors"][0])

    # ==========================================================================
    # 2. Numerical Consistency & Stats Inquest Tests
    # ==========================================================================
    def test_06_empty_stats_json_fails_numerical_validator(self):
        """JSON file with only sample_size and no substantive statistics strictly FAILS."""
        stats_file = os.path.join(self.test_dir, "empty_stats.json")
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump({"sample_size": 60}, f)

        res = validate_numbers(stats_file)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertTrue(any("lacks substantive empirical parameters" in err for err in res["errors"]))
        self.assertGreater(len(res["actionable_repair_prescriptions"]), 0)

    def test_07_stats_json_with_test_stat_missing_p_value_fails(self):
        """JSON file with t-statistic but missing p-value strictly FAILS."""
        stats_file = os.path.join(self.test_dir, "missing_p_stats.json")
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump({"sample_size": 60, "t_stat": 3.42, "effect_size": 0.45}, f)

        res = validate_numbers(stats_file)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertTrue(any("omits exact p-value" in err for err in res["errors"]))

    # ==========================================================================
    # 3. Bidirectional Reporting & Anti-Silent-Omission Tests
    # ==========================================================================
    def test_08_silent_omission_fails_result_consistency(self):
        """Text omitting primary test statistics present in JSON strictly FAILS."""
        stats_file = os.path.join(self.test_dir, "h1_stats.json")
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump({"sample_size": 60, "t_stat": 3.42, "p_value": 0.001, "effect_size": 0.45}, f)

        md_file = os.path.join(self.test_dir, "h1_report.md")
        with open(md_file, "w", encoding="utf-8") as f:
            # Narrative mentions NO numbers or statistics at all!
            f.write("# فصل چهارم: یافته‌های فرضیه اول\n\nدر این فرضیه اثر مداخله به طور کامل بررسی شد و نتایج بسیار خوبی حاصل گردید.\n")

        res = validate_cross_artifacts(stats_file, md_path=md_file)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertTrue(any("Omitted statistical reporting" in err for err in res["errors"]))

    # ==========================================================================
    # 4. Hardened Adversarial Gate Tests (Tier 3)
    # ==========================================================================
    def test_09_unrebutted_high_adversarial_challenge_blocks_pass(self):
        """Small sample (N < 60) multivariate model without bootstrap returns CHALLENGE_BLOCKED."""
        stats_file = os.path.join(self.test_dir, "regression_stats.json")
        with open(stats_file, "w", encoding="utf-8") as f:
            json.dump({
                "sample_size": 40,
                "coefficients": [
                    {"predictor": "X", "beta": 0.35, "t": 2.30, "p_value": 0.025, "se": 0.15}
                ]
            }, f)

        adv_rep = run_adversarial_audit(self.test_dir)
        self.assertEqual(adv_rep["overall_verdict"], "CHALLENGE_BLOCKED")
        self.assertGreater(adv_rep["evidence_summary"]["open_high"], 0)

    # ==========================================================================
    # 5. Earned-Score Defense Committee Tests (Tier 4)
    # ==========================================================================
    def test_10_empty_stage_fails_defense_readiness(self):
        """An empty or hollow stage scores <= 10.00 / 20.00 and receives REJECT (مردود)."""
        empty_dir = os.path.join(self.test_dir, "empty_stage")
        os.makedirs(empty_dir, exist_ok=True)

        cert = run_defense_certification(empty_dir, has_wos_publication=False)
        self.assertEqual(cert["defense_verdict"], "REJECT")
        self.assertEqual(cert["persian_verdict"], "مردود")
        self.assertLessEqual(cert["overall_score_out_of_20"], 10.00)

    def test_11_rich_compliant_stage_passes_defense_readiness(self):
        """A fully certified deliverable with verified tiers earns high honors (>= 18.00 PASS_EXCELLENT)."""
        valid_dir = os.path.join(self.test_dir, "valid_stage")
        os.makedirs(valid_dir, exist_ok=True)

        # Create valid mock files
        with open(os.path.join(valid_dir, "sample.docx"), "w") as f:
            f.write("mock docx")
        with open(os.path.join(valid_dir, "sample.md"), "w") as f:
            f.write("mock md")
        with open(os.path.join(valid_dir, "sample.json"), "w") as f:
            f.write("{}")

        cert = run_defense_certification(
            valid_dir,
            tier1_result={"verdict": "PASS", "errors": []},
            tier2_result={"verdict": "PASS", "gross_decision_errors": 0, "reporting_errors": 0, "grim_failures": 0},
            tier3_result={"verdict": "PASS", "open_critical": 0, "open_high": 0},
            has_wos_publication=False
        )

        self.assertEqual(cert["defense_verdict"], "PASS_EXCELLENT")
        self.assertEqual(cert["persian_verdict"], "قبول - عالی")
        self.assertGreaterEqual(cert["overall_score_out_of_20"], 18.00)
        self.assertLessEqual(cert["overall_score_out_of_20"], 19.00)  # Capped ceiling


if __name__ == '__main__':
    unittest.main()
