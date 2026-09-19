#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_evidence_provenance_phase11.py — Comprehensive Test Suite for Phase 11

Verifies:
1. 4-tier evidence layer hierarchy (Raw output -> Verified result -> Interpretation -> Claim)
2. Authoritative 5-link provenance relationship (claim -> artifact -> statistic -> analysis -> data)
3. Fail-closed rejection on broken links (artifact hash, statistic mismatch, script hash, dataset hash)
4. Orphan claim detection in narrative text
5. Multi-scope support (Chapter 4 findings, Chapter 5 discussion, abstract, conclusion, paper)
6. CLI commands: build, verify, trace
7. Integration with run_all_validators and stage_manifest_engine
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

from scripts.evidence_provenance_engine import (
    build_claim_provenance,
    trace_claim_provenance,
    verify_claim_provenance,
    compute_sha256,
    format_trace_report
)
from validators.provenance_validator import validate_provenance, detect_orphan_claims
from validators.run_all_validators import run_suite
from scripts.stage_manifest_engine import (
    build_stage_manifest,
    verify_stage_manifest,
    ManifestProvenanceError
)


class TestEvidenceProvenancePhase11(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="phase11_test_")
        self.stage_dir = os.path.join(self.temp_dir, "06_hypothesis_1")
        os.makedirs(self.stage_dir, exist_ok=True)

        # 1. Tier 1: Raw statistical output
        self.raw_output_path = os.path.join(self.stage_dir, "raw_output.json")
        self.raw_output_data = {
            "matrix": [[1.2, 3.4], [5.6, 7.8]],
            "raw_anova": {
                "sum_sq": [142.5, 438.1],
                "df": [1, 57],
                "F_val": 18.42,
                "p_val": 0.0001
            },
            "timestamp": "2026-09-19T10:00:00Z"
        }
        with open(self.raw_output_path, "w", encoding="utf-8") as f:
            json.dump(self.raw_output_data, f, indent=2)

        # 2. Tier 2: Verified result JSON
        self.result_json_path = os.path.join(self.stage_dir, "06_hypothesis_1.json")
        self.result_json_data = {
            "hypothesis_id": "H1",
            "test_type": "ANCOVA",
            "sample_size": 60,
            "parameters": {
                "treatment_effect_F": {
                    "F": 18.42,
                    "df1": 1,
                    "df2": 57,
                    "p": 0.0001,
                    "eta_sq_p": 0.244,
                    "CI": [0.11, 0.39]
                }
            },
            "table_data": [
                {"Source": "Pretest", "SS": 85.2, "df": 1, "MS": 85.2, "F": 11.02, "p": 0.001, "eta_p2": 0.16},
                {"Source": "Group", "SS": 142.5, "df": 1, "MS": 142.5, "F": 18.42, "p": 0.0001, "eta_p2": 0.24}
            ]
        }
        with open(self.result_json_path, "w", encoding="utf-8") as f:
            json.dump(self.result_json_data, f, indent=2)

        # 3. Tier 3: Narrative Markdown
        self.narrative_md_path = os.path.join(self.stage_dir, "06_hypothesis_1.md")
        self.narrative_md_content = (
            "# یافته‌های فرضیه اول\n\n"
            "برای بررسی اثربخشی مداخله درمان مبتنی بر پذیرش و تعهد بر فرسودگی شغلی پرستاران، "
            "از تحلیل کوواریانس تک‌متغیره استفاده شد. نتایج نشان داد که پس از کنترل اثر پیش‌آزمون، "
            "اثر گروه بر فرسودگی شغلی معنادار بود (F(1, 57) = 18.42, p < ۰.۰۰۱, η²p = ۰.۲۴). "
            "بنابراین، فرضیه اول تأیید شد و گروه مداخله کاهش معناداری در فرسودگی شغلی نشان داد.\n\n"
            "| منبع تغییرات | مجموع مجذورات | درجه آزادی | میانگین مجذورات | F | p | η²p |\n"
            "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
            "| پیش‌آزمون | ۸۵.۲۰ | ۱ | ۸۵.۲۰ | ۱۱.۰۲ | ۰.۰۰۱ | ۰.۱۶ |\n"
            "| گروه (مداخله) | ۱۴۲.۵۰ | ۱ | ۱۴۲.۵۰ | ۱۸.۴۲ | ۰.۰۰۱ | ۰.۲۴ |\n"
        )
        with open(self.narrative_md_path, "w", encoding="utf-8") as f:
            f.write(self.narrative_md_content)

        # 4. OpenXML DOCX placeholder
        self.narrative_docx_path = os.path.join(self.stage_dir, "06_hypothesis_1.docx")
        with open(self.narrative_docx_path, "wb") as f:
            f.write(b"MOCK_DOCX_FILE_BYTES_FOR_PHASE11")

        # 5. Analysis script & Raw dataset
        self.script_path = os.path.join(self.stage_dir, "ancova_runner.py")
        with open(self.script_path, "w", encoding="utf-8") as f:
            f.write("# Deterministic ANCOVA script\nprint('ANCOVA executed')\n")

        self.dataset_path = os.path.join(self.stage_dir, "study_dataset.csv")
        with open(self.dataset_path, "w", encoding="utf-8") as f:
            f.write("id,group,pre,post\n1,1,25,15\n2,0,24,23\n")

        # Claims specification
        self.claims_spec = [
            {
                "claim_id": "CLM-H1-01",
                "statement": "فرضیه اول تأیید شد و گروه مداخله کاهش معناداری در فرسودگی شغلی نشان داد.",
                "claim_type": "DIRECT_FINDING",
                "target_scope": "CHAPTER_4_FINDINGS",
                "parameter_key": "treatment_effect_F",
                "metrics": {
                    "F": 18.42,
                    "df1": 1,
                    "df2": 57,
                    "p": 0.0001,
                    "eta_sq_p": 0.244
                },
                "analysis_id": "AN-ANCOVA-H1",
                "method": "One-Way ANCOVA",
                "model_formula": "burnout_post ~ burnout_pre + group",
                "location": "بخش یافته‌های فرضیه اول"
            }
        ]

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_01_complete_valid_5_link_chain(self):
        """Test 1: Full valid 4-tier evidence layer and unbroken 5-link provenance chain returns PASS."""
        doc = build_claim_provenance(
            stage_dir=self.stage_dir,
            stage_id="06_hypothesis_1",
            project_id="PROJ-TEST-01",
            target_scope="CHAPTER_4_FINDINGS",
            raw_output_path=self.raw_output_path,
            result_json_path=self.result_json_path,
            narrative_md_path=self.narrative_md_path,
            claims_spec=self.claims_spec,
            script_path=self.script_path,
            dataset_path=self.dataset_path,
            sample_size=60,
            narrative_docx_path=self.narrative_docx_path
        )

        self.assertEqual(doc["status"], "VERIFIED")
        self.assertEqual(len(doc["claims"]), 1)
        self.assertIn("tier_1_raw_output", doc["evidence_tiers"])
        self.assertIn("tier_2_verified_result", doc["evidence_tiers"])
        self.assertIn("tier_3_interpretation", doc["evidence_tiers"])
        self.assertIn("tier_4_claims", doc["evidence_tiers"])

        # Master verification
        prov_file = os.path.join(self.stage_dir, "claim_provenance.json")
        res = verify_claim_provenance(prov_file, stage_dir=self.stage_dir)
        self.assertEqual(res["verdict"], "PASS")
        self.assertEqual(res["evidence"]["claims_unbroken"], 1)
        self.assertEqual(res["evidence"]["claims_broken"], 0)

        # Trace check
        trace = trace_claim_provenance("CLM-H1-01", prov_file, stage_dir=self.stage_dir)
        self.assertTrue(trace["unbroken"])
        self.assertTrue(trace["trace"]["link_2_artifact"]["hash_verified"])
        self.assertTrue(trace["trace"]["link_3_statistic"]["metrics_verified"])
        self.assertTrue(trace["trace"]["link_4_analysis"]["script_hash_verified"])
        self.assertTrue(trace["trace"]["link_5_data"]["dataset_hash_verified"])

        # Format report test
        report_str = format_trace_report(trace)
        self.assertIn("CLAIM PROVENANCE TRACE: CLM-H1-01 [UNBROKEN (VERIFIED)]", report_str)
        self.assertIn("LINK 1: CLAIM", report_str)
        self.assertIn("LINK 2: ARTIFACT", report_str)
        self.assertIn("LINK 3: STATISTIC", report_str)
        self.assertIn("LINK 4: ANALYSIS", report_str)
        self.assertIn("LINK 5: DATA", report_str)

    def test_02_broken_link_2_artifact_modified(self):
        """Test 2: Modifying deliverable artifact after provenance creation breaks Link 2 (FAIL)."""
        build_claim_provenance(
            stage_dir=self.stage_dir,
            stage_id="06_hypothesis_1",
            project_id="PROJ-TEST-01",
            target_scope="CHAPTER_4_FINDINGS",
            raw_output_path=self.raw_output_path,
            result_json_path=self.result_json_path,
            narrative_md_path=self.narrative_md_path,
            claims_spec=self.claims_spec,
            script_path=self.script_path,
            dataset_path=self.dataset_path,
            sample_size=60
        )

        # Tamper with markdown artifact
        with open(self.narrative_md_path, "a", encoding="utf-8") as f:
            f.write("\nTAMPERED LINE ALTERING HASH\n")

        prov_file = os.path.join(self.stage_dir, "claim_provenance.json")
        res = verify_claim_provenance(prov_file, stage_dir=self.stage_dir)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertTrue(any("Link 2 (Artifact) SHA-256 mismatch" in err for err in res["errors"]))

    def test_03_broken_link_3_statistic_metric_mismatch(self):
        """Test 3: Claim citing a statistic that contradicts result.json breaks Link 3 (FAIL)."""
        bad_claims = [
            {
                "claim_id": "CLM-H1-01",
                "statement": "فرضیه اول تأیید شد و اثر مداخله معنادار بود.",
                "claim_type": "DIRECT_FINDING",
                "target_scope": "CHAPTER_4_FINDINGS",
                "parameter_key": "treatment_effect_F",
                "metrics": {
                    "F": 35.50,  # Contradicts result.json which has 18.42
                    "p": 0.0001
                }
            }
        ]

        build_claim_provenance(
            stage_dir=self.stage_dir,
            stage_id="06_hypothesis_1",
            project_id="PROJ-TEST-01",
            target_scope="CHAPTER_4_FINDINGS",
            raw_output_path=self.raw_output_path,
            result_json_path=self.result_json_path,
            narrative_md_path=self.narrative_md_path,
            claims_spec=bad_claims,
            script_path=self.script_path,
            dataset_path=self.dataset_path,
            sample_size=60
        )

        prov_file = os.path.join(self.stage_dir, "claim_provenance.json")
        res = verify_claim_provenance(prov_file, stage_dir=self.stage_dir)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertTrue(any("metric mismatch for 'F'" in err for err in res["errors"]))

    def test_04_broken_link_4_analysis_script_modified(self):
        """Test 4: Modifying analysis script breaks Link 4 (FAIL)."""
        build_claim_provenance(
            stage_dir=self.stage_dir,
            stage_id="06_hypothesis_1",
            project_id="PROJ-TEST-01",
            target_scope="CHAPTER_4_FINDINGS",
            raw_output_path=self.raw_output_path,
            result_json_path=self.result_json_path,
            narrative_md_path=self.narrative_md_path,
            claims_spec=self.claims_spec,
            script_path=self.script_path,
            dataset_path=self.dataset_path,
            sample_size=60
        )

        # Tamper with analysis script
        with open(self.script_path, "a", encoding="utf-8") as f:
            f.write("\n# Altered script logic\n")

        prov_file = os.path.join(self.stage_dir, "claim_provenance.json")
        res = verify_claim_provenance(prov_file, stage_dir=self.stage_dir)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertTrue(any("Link 4 (Analysis script) SHA-256 mismatch" in err for err in res["errors"]))

    def test_05_broken_link_5_dataset_modified(self):
        """Test 5: Modifying raw dataset breaks Link 5 (FAIL)."""
        build_claim_provenance(
            stage_dir=self.stage_dir,
            stage_id="06_hypothesis_1",
            project_id="PROJ-TEST-01",
            target_scope="CHAPTER_4_FINDINGS",
            raw_output_path=self.raw_output_path,
            result_json_path=self.result_json_path,
            narrative_md_path=self.narrative_md_path,
            claims_spec=self.claims_spec,
            script_path=self.script_path,
            dataset_path=self.dataset_path,
            sample_size=60
        )

        # Tamper with raw dataset
        with open(self.dataset_path, "a", encoding="utf-8") as f:
            f.write("999,1,99,99\n")

        prov_file = os.path.join(self.stage_dir, "claim_provenance.json")
        res = verify_claim_provenance(prov_file, stage_dir=self.stage_dir)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertTrue(any("Link 5 (Data) SHA-256 mismatch" in err for err in res["errors"]))

    def test_06_orphan_claim_detection(self):
        """Test 6: Substantive scientific claims in text without provenance registration trigger FAIL."""
        build_claim_provenance(
            stage_dir=self.stage_dir,
            stage_id="06_hypothesis_1",
            project_id="PROJ-TEST-01",
            target_scope="CHAPTER_4_FINDINGS",
            raw_output_path=self.raw_output_path,
            result_json_path=self.result_json_path,
            narrative_md_path=self.narrative_md_path,
            claims_spec=self.claims_spec,
            script_path=self.script_path,
            dataset_path=self.dataset_path,
            sample_size=60
        )

        # Add an unregistered second claim to the narrative
        orphan_md = os.path.join(self.stage_dir, "orphan_section.md")
        with open(orphan_md, "w", encoding="utf-8") as f:
            f.write(
                "# بخش الحاقی\n\n"
                "همچنین فرضیه سوم تأیید شد و درمان منجر به بهبود معنادار انعطاف‌پذیری روان‌شناختی گردید "
                "(t(58) = 4.88, p < ۰.۰۰۱).\n"
            )

        res = validate_provenance(self.stage_dir, check_orphan_claims=True)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertTrue(any("Unregistered orphan claim detected" in err for err in res["errors"]))

    def test_07_multi_scope_support(self):
        """Test 7: Verification supports findings, discussion, abstract, conclusion, paper scopes."""
        scopes = [
            ("CHAPTER_4_FINDINGS", "06_hypothesis_1"),
            ("CHAPTER_5_DISCUSSION", "05_discussion"),
            ("ABSTRACT", "thesis_abstract"),
            ("CONCLUSION", "thesis_conclusion"),
            ("PAPER", "journal_manuscript")
        ]

        for scope, sid in scopes:
            c_spec = [
                {
                    "claim_id": f"CLM-{sid}-01",
                    "statement": f"Statement for scope {scope} demonstrating scientific evidence.",
                    "claim_type": "DIRECT_FINDING",
                    "target_scope": scope,
                    "parameter_key": "treatment_effect_F",
                    "metrics": {"F": 18.42, "p": 0.0001}
                }
            ]
            doc = build_claim_provenance(
                stage_dir=self.stage_dir,
                stage_id=sid,
                project_id="PROJ-TEST-01",
                target_scope=scope,
                raw_output_path=self.raw_output_path,
                result_json_path=self.result_json_path,
                narrative_md_path=self.narrative_md_path,
                claims_spec=c_spec,
                script_path=self.script_path,
                dataset_path=self.dataset_path,
                sample_size=60,
                output_filename=f"prov_{sid}.json"
            )
            self.assertEqual(doc["target_scope"], scope)
            prov_p = os.path.join(self.stage_dir, f"prov_{sid}.json")
            res = verify_claim_provenance(prov_p, stage_dir=self.stage_dir)
            self.assertEqual(res["verdict"], "PASS")

    def test_08_integration_with_run_all_validators(self):
        """Test 8: Master run_all_validators executes Gate 4 claim provenance check cleanly."""
        build_claim_provenance(
            stage_dir=self.stage_dir,
            stage_id="06_hypothesis_1",
            project_id="PROJ-TEST-01",
            target_scope="CHAPTER_4_FINDINGS",
            raw_output_path=self.raw_output_path,
            result_json_path=self.result_json_path,
            narrative_md_path=self.narrative_md_path,
            claims_spec=self.claims_spec,
            script_path=self.script_path,
            dataset_path=self.dataset_path,
            sample_size=60,
            narrative_docx_path=self.narrative_docx_path
        )

        suite_rep = run_suite(stage_dir=self.stage_dir, stage_id="06_hypothesis_1", enforce_cross_artifacts=False)
        prov_results = [r for r in suite_rep["results"] if r.get("check_id") == "CHK-CLAIM-PROVENANCE"]
        self.assertEqual(len(prov_results), 1)
        self.assertEqual(prov_results[0]["verdict"], "PASS")

    def test_09_integration_with_stage_manifest_engine(self):
        """Test 9: Stage manifest engine validates claim_provenance.json during build and verify."""
        build_claim_provenance(
            stage_dir=self.stage_dir,
            stage_id="06_hypothesis_1",
            project_id="PROJ-TEST-01",
            target_scope="CHAPTER_4_FINDINGS",
            raw_output_path=self.raw_output_path,
            result_json_path=self.result_json_path,
            narrative_md_path=self.narrative_md_path,
            claims_spec=self.claims_spec,
            script_path=self.script_path,
            dataset_path=self.dataset_path,
            sample_size=60,
            narrative_docx_path=self.narrative_docx_path
        )

        # Build stage manifest
        manifest = build_stage_manifest(
            stage_dir=self.stage_dir,
            stage_id="06_hypothesis_1",
            project_id="PROJ-TEST-01",
            agent="statistics-agent",
            script_or_generator=self.script_path,
            inputs=[{"path": self.dataset_path, "description": "Raw dataset"}],
            required_artifacts=[
                {"path": "06_hypothesis_1.json", "type": "stats_json", "required": True},
                {"path": "06_hypothesis_1.md", "type": "narrative_markdown", "required": True},
                {"path": "06_hypothesis_1.docx", "type": "openxml_word", "required": True},
                {"path": "claim_provenance.json", "type": "claim_provenance_json", "required": True}
            ],
            cross_agreement_required=False
        )
        self.assertEqual(manifest["status"], "GENERATED")

        # Verify manifest
        res = verify_stage_manifest(os.path.join(self.stage_dir, "manifest.json"), check_cross_agreement=False)
        self.assertEqual(res["verdict"], "PASS")


if __name__ == "__main__":
    unittest.main()
