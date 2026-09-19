#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_writing_architecture_phase12.py — Comprehensive Test Suite for Phase 12

Verifies:
1. Chapter 4 micro-flow: statistical result -> table -> interpretation -> paragraph
2. Chapter 5 micro-flow: verified finding -> theoretical interpretation -> literature -> limitations -> implications
3. Statistical truth preservation: Writer cannot modify statistical numbers (fail-closed)
4. Forbidden claims & mandated phrases enforcement
5. Chapter 4 strict prohibition against external literature citations
6. Writing QC: AI cliché elimination & Persian leading zero standard
7. Two-stage QC pipeline: Writing QC -> Statistical Claim QC -> Final Document Assembly
8. Integration with run_all_validators Gate 4
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
from typing import Dict, Any

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.writing_pipeline_engine import (
    generate_interpretation_contract,
    verify_draft_against_contract,
    run_writing_qc,
    run_statistical_claim_qc,
    assemble_final_document
)
from validators.run_all_validators import run_suite


class TestWritingArchitecturePhase12(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="phase12_test_")
        self.stage_dir = os.path.join(self.temp_dir, "06_hypothesis_1")
        os.makedirs(self.stage_dir, exist_ok=True)

        # Verified result JSON
        self.result_json_path = os.path.join(self.stage_dir, "06_hypothesis_1.json")
        self.result_json_data = {
            "hypothesis_id": "H1",
            "test_type": "ANCOVA",
            "parameters": {
                "treatment_effect_F": {
                    "F": 18.42,
                    "df1": 1,
                    "df2": 57,
                    "p": 0.0001,
                    "eta_sq_p": 0.244
                }
            },
            "table_data": [
                {"Source": "Pretest", "SS": 85.2, "df": 1, "MS": 85.2, "F": 11.02, "p": 0.001, "eta_p2": 0.16},
                {"Source": "Group", "SS": 142.5, "df": 1, "MS": 142.5, "F": 18.42, "p": 0.0001, "eta_p2": 0.24}
            ]
        }
        with open(self.result_json_path, "w", encoding="utf-8") as f:
            json.dump(self.result_json_data, f, indent=2)

        # Chapter 4 compliant draft
        self.ch4_draft_content = (
            "# یافته‌های آزمون فرضیه اول\n\n"
            "برای بررسی اثربخشی مداخله در کاهش فرسودگی شغلی، تحلیل کوواریانس تک‌متغیره اجرا گردید. "
            "نتایج مندرج در جدول ۴-۱ نشان داد که اثر گروه پس از تعدیل نمرات پیش‌آزمون در سطح آلفای ۰.۰۵ معنادار است "
            "(F(1, 57) = 18.42, p < ۰.۰۰۱, η²p = ۰.۲۴). "
            "بنابراین، فرضیه اول تأیید شد و گروه مداخله کاهش معناداری در فرسودگی شغلی گزارش دادند.\n\n"
            "| منبع تغییرات | مجموع مجذورات | درجه آزادی | میانگین مجذورات | F | p | η²p |\n"
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
            "| پیش‌آزمون | ۸۵.۲۰ | ۱ | ۸۵.۲۰ | ۱۱.۰۲ | ۰.۰۰۱ | ۰.۱۶ |\n"
            "| گروه (مداخله) | ۱۴۲.۵۰ | ۱ | ۱۴۲.۵۰ | ۱۸.۴۲ | ۰.۰۰۱ | ۰.۲۴ |\n"
        )
        self.ch4_draft_path = os.path.join(self.stage_dir, "draft_ch4.md")
        with open(self.ch4_draft_path, "w", encoding="utf-8") as f:
            f.write(self.ch4_draft_content)

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_01_chapter_4_micro_flow(self):
        """Test 1: Chapter 4 micro-flow (statistical result -> table -> interpretation -> paragraph)."""
        contract = generate_interpretation_contract(
            stage_dir=self.stage_dir,
            stage_id="06_hypothesis_1",
            project_id="PROJ-01",
            chapter=4,
            result_json_path=self.result_json_path,
            spec={
                "table_number": "۴-۱",
                "interpretation": {
                    "hypothesis_verdict": "SUPPORTED",
                    "mandated_phrases": [
                        "فرضیه اول تأیید شد",
                        "F(1, 57) = 18.42"
                    ],
                    "forbidden_claims": [
                        "اثبات قطعی علیت"
                    ]
                }
            }
        )
        self.assertEqual(contract["chapter"], 4)
        self.assertEqual(contract["status"], "CONTRACTED")

        # 1. Verify draft against contract
        c_res = verify_draft_against_contract(self.ch4_draft_content, contract)
        self.assertEqual(c_res["verdict"], "PASS")

        # 2. Writing QC
        w_res = run_writing_qc(self.ch4_draft_content)
        self.assertEqual(w_res["verdict"], "PASS")

        # 3. Statistical Claim QC
        s_res = run_statistical_claim_qc(self.ch4_draft_content, contract)
        self.assertEqual(s_res["verdict"], "PASS")
        self.assertEqual(s_res["evidence"]["parameters_matched"], 1)

        # 4. Final Document Assembly
        asm = assemble_final_document(self.ch4_draft_content, contract, self.stage_dir, output_stem="06_hypothesis_1")
        self.assertEqual(asm["status"], "ASSEMBLED")
        self.assertTrue(os.path.isfile(asm["artifacts"]["markdown"]))
        self.assertTrue(os.path.isfile(asm["artifacts"]["docx"]))
        self.assertTrue(os.path.isfile(asm["artifacts"]["json"]))

    def test_02_chapter_5_micro_flow(self):
        """Test 2: Chapter 5 micro-flow (verified finding -> theoretical interp -> literature -> limitations -> implications)."""
        c5_dir = os.path.join(self.temp_dir, "05_discussion")
        os.makedirs(c5_dir, exist_ok=True)

        contract = generate_interpretation_contract(
            stage_dir=c5_dir,
            stage_id="05_discussion",
            project_id="PROJ-01",
            chapter=5,
            result_json_path=self.result_json_path,
            spec={
                "verified_finding": {
                    "hypothesis_ref": "H1",
                    "claim_id": "CLM-H1-01",
                    "verified_statistics": {"F": 18.42, "p": 0.0001}
                },
                "theoretical_interpretation": {
                    "theory_name": "نظریه درمان مبتنی بر پذیرش و تعهد",
                    "mechanism_explanation": "افزایش انعطاف‌پذیری روان‌شناختی"
                },
                "comparison_with_literature": {
                    "concordant_studies": [
                        {"citation": "Hayes et al. (2021)", "finding": "کاهش فرسودگی شغلی"}
                    ]
                },
                "limitations": ["عدم پیگیری طولانی‌مدت"],
                "implications": ["اجرای کارگاه‌های مداخله‌ای"]
            }
        )
        self.assertEqual(contract["chapter"], 5)

        ch5_draft = (
            "# بحث و نتیجه‌گیری پیرامون فرضیه اول\n\n"
            "یافته‌های فصل چهارم نشان داد که درمان مبتنی بر پذیرش و تعهد اثربخشی معناداری دارد (F(1, 57) = 18.42, p < ۰.۰۰۱). "
            "در تبیین نظری این یافته می‌توان بیان داشت که افزایش انعطاف‌پذیری روان‌شناختی منجر به گسلش از افکار ناکارآمد شغلی گردیده است. "
            "این نتیجه با یافته‌های پژوهش Hayes et al. (2021) همسو می‌باشد. "
            "از جمله محدودیت‌های پژوهش حاضر عدم پیگیری طولانی‌مدت فراتر از ۳ ماه بود. "
            "بر این اساس، پیشنهاد کاربردی پژوهش برگزاری کارگاه‌های توانمندسازی روان‌شناختی برای کادر درمان است.\n"
        )

        # 1. Verify against contract
        c_res = verify_draft_against_contract(ch5_draft, contract)
        self.assertEqual(c_res["verdict"], "PASS")

        # 2. Writing QC
        w_res = run_writing_qc(ch5_draft)
        self.assertEqual(w_res["verdict"], "PASS")

        # 3. Statistical Claim QC
        s_res = run_statistical_claim_qc(ch5_draft, contract)
        self.assertEqual(s_res["verdict"], "PASS")

    def test_03_writer_modifies_statistical_truth(self):
        """Test 3: Writer modifies statistical truth (e.g. F = 25.00 instead of 18.42) -> FAIL."""
        contract = generate_interpretation_contract(
            stage_dir=self.stage_dir,
            stage_id="06_hypothesis_1",
            project_id="PROJ-01",
            chapter=4,
            result_json_path=self.result_json_path,
            spec={"interpretation": {"mandated_phrases": ["فرضیه اول تأیید شد"]}}
        )

        tampered_draft = self.ch4_draft_content.replace("F(1, 57) = 18.42", "F(1, 57) = 25.00")
        s_res = run_statistical_claim_qc(tampered_draft, contract)
        self.assertEqual(s_res["verdict"], "FAIL")
        self.assertTrue(any("Writer modified statistical truth" in e for e in s_res["errors"]))

    def test_04_writer_makes_forbidden_claim(self):
        """Test 4: Writer includes forbidden claim or external literature in Chapter 4 -> FAIL."""
        contract = generate_interpretation_contract(
            stage_dir=self.stage_dir,
            stage_id="06_hypothesis_1",
            project_id="PROJ-01",
            chapter=4,
            result_json_path=self.result_json_path,
            spec={
                "interpretation": {
                    "mandated_phrases": ["فرضیه اول تأیید شد"],
                    "forbidden_claims": ["اثبات قطعی علیت"]
                }
            }
        )

        # Forbidden claim
        draft_with_forbidden = self.ch4_draft_content + "\nاین نتیجه اثبات قطعی علیت بین متغیرها را نشان می‌دهد.\n"
        c_res = verify_draft_against_contract(draft_with_forbidden, contract)
        self.assertEqual(c_res["verdict"], "FAIL")
        self.assertTrue(any("Forbidden claim detected" in e for e in c_res["errors"]))

        # External literature citation in Chapter 4
        draft_with_lit = self.ch4_draft_content + "\nاین نتیجه با یافته‌های Smith et al. (2023) کاملاً همسو است.\n"
        c_res2 = verify_draft_against_contract(draft_with_lit, contract)
        self.assertEqual(c_res2["verdict"], "FAIL")
        self.assertTrue(any("Chapter 4 violation: External literature citations detected" in e for e in c_res2["errors"]))

    def test_05_writer_omits_mandated_phrase(self):
        """Test 5: Writer omits mandated phrase -> FAIL."""
        contract = generate_interpretation_contract(
            stage_dir=self.stage_dir,
            stage_id="06_hypothesis_1",
            project_id="PROJ-01",
            chapter=4,
            result_json_path=self.result_json_path,
            spec={
                "interpretation": {
                    "mandated_phrases": ["فرضیه اول تأیید شد", "تحلیل کوواریانس تک‌متغیره"]
                }
            }
        )

        incomplete_draft = "نتایج نشان داد که تفاوت معنادار است ولی نام آزمون و تأیید فرضیه ذکر نشد."
        c_res = verify_draft_against_contract(incomplete_draft, contract)
        self.assertEqual(c_res["verdict"], "FAIL")
        self.assertTrue(any("Mandated phrase missing from draft" in e for e in c_res["errors"]))

    def test_06_writing_qc_fails_on_cliches_or_leading_zero(self):
        """Test 6: Writing QC rejects AI clichés and Persian leading zero violations."""
        # 1. AI cliché
        draft_cliche = self.ch4_draft_content + "\nشایان ذکر است که نتایج بسیار درخشان بودند.\n"
        w_res = run_writing_qc(draft_cliche)
        self.assertEqual(w_res["verdict"], "FAIL")
        self.assertTrue(any("AI cliché detected" in e for e in w_res["errors"]))

        # 2. Persian leading zero violation (.05 instead of ۰.۰۵)
        draft_bad_zero = self.ch4_draft_content.replace("سطح آلفای ۰.۰۵", "سطح آلفای .05")
        w_res2 = run_writing_qc(draft_bad_zero)
        self.assertEqual(w_res2["verdict"], "FAIL")
        self.assertTrue(any("Persian leading zero violation" in e for e in w_res2["errors"]))

    def test_07_integration_with_run_all_validators(self):
        """Test 7: Master run_all_validators checks interpretation contract adherence in Gate 4."""
        # Generate contract in stage_dir
        generate_interpretation_contract(
            stage_dir=self.stage_dir,
            stage_id="06_hypothesis_1",
            project_id="PROJ-01",
            chapter=4,
            result_json_path=self.result_json_path,
            spec={
                "table_number": "۴-۱",
                "interpretation": {
                    "mandated_phrases": ["فرضیه اول تأیید شد"],
                    "forbidden_claims": ["اثبات قطعی علیت"]
                }
            }
        )

        # Compliant run
        suite_rep = run_suite(stage_dir=self.stage_dir, stage_id="06_hypothesis_1", enforce_cross_artifacts=False)
        contract_checks = [r for r in suite_rep["results"] if "CHK-CONTRACT" in r.get("check_id", "")]
        self.assertEqual(len(contract_checks), 1)
        self.assertEqual(contract_checks[0]["verdict"], "PASS")

        # Tampered run (tamper draft by modifying numbers)
        with open(self.ch4_draft_path, "w", encoding="utf-8") as f:
            f.write(self.ch4_draft_content.replace("F(1, 57) = 18.42", "F(1, 57) = 35.00"))

        suite_rep2 = run_suite(stage_dir=self.stage_dir, stage_id="06_hypothesis_1", enforce_cross_artifacts=False)
        stat_checks = [r for r in suite_rep2["results"] if "CHK-STAT-CLAIM-QC" in r.get("check_id", "")]
        self.assertEqual(len(stat_checks), 1)
        self.assertEqual(stat_checks[0]["verdict"], "FAIL")


if __name__ == "__main__":
    unittest.main()
