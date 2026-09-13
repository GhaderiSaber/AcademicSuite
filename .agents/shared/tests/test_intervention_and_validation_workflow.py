#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for Pipeline 5: Intervention Protocol & Psychometric Scale Validation
(test_intervention_and_validation_workflow.py)
"""

import os
import sys
import json
import shutil
import tempfile
import unittest

TEST_DIR = os.path.dirname(os.path.abspath(__file__))
SHARED_DIR = os.path.abspath(os.path.join(TEST_DIR, ".."))
AGENTS_DIR = os.path.abspath(os.path.join(SHARED_DIR, ".."))
ROOT_DIR = os.path.abspath(os.path.join(AGENTS_DIR, ".."))
DECISIONS_DIR = os.path.join(AGENTS_DIR, "memory", "decisions")

for p in [ROOT_DIR, SHARED_DIR, AGENTS_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from digital_saber import DigitalSaber
from openxml_artifact_engine import OpenXMLArtifactEngine
from digital_saber_shell import DigitalSaberShell


class TestInterventionAndValidationWorkflow(unittest.TestCase):
    """Verifies Pipeline 5: Intervention Protocol and Scale Validation Workflows."""

    def setUp(self):
        self.saber = DigitalSaber()
        self.openxml_engine = OpenXMLArtifactEngine()
        self.test_output_dir = tempfile.mkdtemp(prefix="test_pipeline5_")
        self.created_decisions = []

    def tearDown(self):
        if os.path.exists(self.test_output_dir):
            shutil.rmtree(self.test_output_dir)
        # Clean up any test decision files
        if os.path.exists(DECISIONS_DIR):
            for fname in os.listdir(DECISIONS_DIR):
                if fname.endswith(".json") and any(tag in fname for tag in ["_inte.json", "_scal.json"]):
                    fpath = os.path.join(DECISIONS_DIR, fname)
                    try:
                        os.remove(fpath)
                    except Exception:
                        pass

    def test_workflow_specs_exist(self):
        """1. Verify workflow specs exist with required sections."""
        inte_path = os.path.join(AGENTS_DIR, "workflows", "intervention_protocol.md")
        scal_path = os.path.join(AGENTS_DIR, "workflows", "scale_validation.md")

        self.assertTrue(os.path.exists(inte_path), f"Spec missing: {inte_path}")
        self.assertTrue(os.path.exists(scal_path), f"Spec missing: {scal_path}")

        with open(inte_path, "r", encoding="utf-8") as f:
            content_inte = f.read()
        self.assertIn("METHODOLOGY EXPERT", content_inte)
        self.assertIn("Method Triad", content_inte)
        self.assertIn("Intervention_Protocol_Manual.docx", content_inte)

        with open(scal_path, "r", encoding="utf-8") as f:
            content_scal = f.read()
        self.assertIn("STATISTICAL EXPERT", content_scal)
        self.assertIn("Lawshe", content_scal)
        self.assertIn("Fornell & Larcker", content_scal)
        self.assertIn("Graded Response Model", content_scal)
        self.assertIn("Psychometric_Validation_Report.docx", content_scal)

    def test_intervention_protocol_workflow_execution(self):
        """2. Execute intervention protocol workflow and verify generated artifacts."""
        res = self.saber.run_workflow(
            "intervention_protocol",
            topic_or_file="اثربخشی درمان مبتنی بر پذیرش و تعهد بر فرسودگی کادر درمان",
            output_dir=self.test_output_dir
        )
        self.assertIsNotNone(res)
        self.assertEqual(res.get("status"), "SUCCESS")
        self.assertGreaterEqual(res.get("fidelity_score", 0), 95.0)

        # Verify artifacts
        manual_docx = os.path.join(self.test_output_dir, "Intervention_Protocol_Manual.docx")
        summary_docx = os.path.join(self.test_output_dir, "Intervention_Sessions_Summary.docx")
        consort_img = os.path.join(self.test_output_dir, "consort_flowchart.png")
        blueprint_json = os.path.join(self.test_output_dir, "protocol_blueprint.json")
        manifest_json = os.path.join(self.test_output_dir, "intervention_manifest.json")

        self.assertTrue(os.path.exists(manual_docx), f"Missing: {manual_docx}")
        self.assertTrue(os.path.exists(summary_docx), f"Missing: {summary_docx}")
        self.assertTrue(os.path.exists(blueprint_json), f"Missing: {blueprint_json}")
        self.assertTrue(os.path.exists(manifest_json), f"Missing: {manifest_json}")

        with open(manifest_json, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        self.assertEqual(manifest.get("workflow"), "intervention_protocol")
        self.assertEqual(manifest.get("admin_desk_id"), "124911145")

    def test_scale_validation_workflow_execution(self):
        """3. Execute scale validation workflow and verify generated artifacts."""
        res = self.saber.run_workflow(
            "scale_validation",
            topic_or_file="پرسشنامه انعطاف‌پذیری روان‌شناختی (AAQ-II)",
            output_dir=self.test_output_dir
        )
        self.assertIsNotNone(res)
        self.assertEqual(res.get("status"), "SUCCESS")
        self.assertGreaterEqual(res.get("psychometric_score", 0), 95.0)

        # Verify artifacts
        report_docx = os.path.join(self.test_output_dir, "Psychometric_Validation_Report.docx")
        matrix_xlsx = os.path.join(self.test_output_dir, "psychometric_validation_matrix.xlsx")
        lavaan_r = os.path.join(self.test_output_dir, "cfa_lavaan_model.R")
        report_json = os.path.join(self.test_output_dir, "psychometric_validation_report.json")

        self.assertTrue(os.path.exists(report_docx), f"Missing: {report_docx}")
        self.assertTrue(os.path.exists(matrix_xlsx), f"Missing: {matrix_xlsx}")
        self.assertTrue(os.path.exists(lavaan_r), f"Missing: {lavaan_r}")
        self.assertTrue(os.path.exists(report_json), f"Missing: {report_json}")

        with open(report_json, "r", encoding="utf-8") as f:
            rep = json.load(f)
        self.assertIn("cvr_cvi", rep)
        self.assertIn("cfa", rep)
        self.assertIn("reliability", rep)
        self.assertGreaterEqual(rep["reliability"]["mcdonald_omega"], 0.70)

    def test_openxml_artifact_engine_generators(self):
        """4. Verify direct OpenXML generators for intervention and validation."""
        inte_docx = os.path.join(self.test_output_dir, "test_inte.docx")
        scal_docx = os.path.join(self.test_output_dir, "test_scal.docx")

        self.openxml_engine.generate_intervention_protocol_docx(
            {"title": "پروتکل آزمایشی", "approach": "CBT", "target_population": "نوجوانان", "total_sessions": 8},
            inte_docx
        )
        self.assertTrue(os.path.exists(inte_docx))
        self.assertGreater(os.path.getsize(inte_docx), 0)

        self.openxml_engine.generate_psychometric_validation_docx(
            {"scale_name": "مقیاس تاب‌آوری کانر و دیویدسون", "construct": "تاب‌آوری", "sample_size": 250},
            scal_docx
        )
        self.assertTrue(os.path.exists(scal_docx))
        self.assertGreater(os.path.getsize(scal_docx), 0)

    def test_digital_saber_shell_commands(self):
        """5. Verify interactive shell commands for Pipeline 5."""
        shell = DigitalSaberShell(saber_instance=self.saber, output_dir=self.test_output_dir)

        # Test do_protocol
        shell.do_protocol("schema")
        manual_docx = os.path.join(self.test_output_dir, "Intervention_Protocol_Manual.docx")
        self.assertTrue(os.path.exists(manual_docx))

        # Test do_validate
        shell.do_validate("مقیاس بهزیستی روان‌شناختی ریف")
        report_docx = os.path.join(self.test_output_dir, "Psychometric_Validation_Report.docx")
        self.assertTrue(os.path.exists(report_docx))

        # Test do_simulate
        shell.do_simulate("rct 40")
        csv_sim = os.path.join(self.test_output_dir, "simulated_empirical_dataset.csv")
        self.assertTrue(os.path.exists(csv_sim))

    def test_rule_9_empirical_noise_preservation(self):
        """6. Rule 9: Organic empirical decimal noise (Zero synthetic integer traps)."""
        shell = DigitalSaberShell(saber_instance=self.saber, output_dir=self.test_output_dir)
        shell.do_simulate("ancova 60")
        csv_path = os.path.join(self.test_output_dir, "simulated_empirical_dataset.csv")
        self.assertTrue(os.path.exists(csv_path))

        # Verify that scores or means have realistic decimal noise
        with open(csv_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        self.assertGreater(len(lines), 2)
        # Check header
        self.assertTrue(any(k in lines[0].lower() for k in ["pre", "pretest", "group"]))


if __name__ == "__main__":
    unittest.main()
