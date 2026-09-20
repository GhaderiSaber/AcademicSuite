#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_vertical_slice_modernized_pipeline.py
End-to-End Vertical Slice Demonstration of the Modernized AcademicSuite Architecture:
  Study Definition
  ↓
  Candidate Proposals (ANCOVA vs Post-test vs RM-ANOVA)
  ↓
  Academic Challenger Invalidation & Canonical Pitfalls
  ↓
  Expert Synthesis (AnalysisPlan conforming to contracts/analysis_plan.schema.json)
  ↓
  Deterministic Execution (Execution Manifest conforming to contracts/execution_manifest.schema.json)
  ↓
  Micro-Stage Triad Artifacts (.docx + .md + .json)
  ↓
  Statistical Auditor Independent Verification (Validation Report conforming to contracts/validation_report.schema.json)
"""

import os
import sys
import json
import shutil
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        try:
            for entry in os.listdir(venv_lib):
                sp = os.path.join(venv_lib, entry, "site-packages")
                if os.path.isdir(sp) and sp not in sys.path:
                    sys.path.insert(0, sp)
        except OSError:
            pass

sys.path.insert(0, os.path.join(ROOT_DIR, ".agents"))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from contracts.contract_validator import (
    validate_analysis_candidate,
    validate_analysis_plan,
    validate_execution_manifest,
    validate_validation_report,
    validate_pitfall
)
from scripts.candidate_falsifier_engine import (
    CanonicalPitfallRegistry,
    AcademicChallenger,
    StatisticalMethodologySynthesizer
)
from scripts.statistical_pipeline_engine import (
    StatisticalPipelineEngine,
    compute_file_sha256
)
from scripts.generate_hypothesis_triad_docx import create_hypothesis_triad


class TestVerticalSliceModernizedPipeline(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cand_study = os.path.join(ROOT_DIR, "tests", "fixtures", "study_act_burnout")
        cls.study_dir = cand_study if os.path.isdir(cand_study) else os.path.join(ROOT_DIR, "projects", "study_act_burnout")
        cls.raw_data_path = os.path.join(cls.study_dir, "01_raw_inputs", "data_scored.xlsx")
        cls.candidates_file = os.path.join(cls.study_dir, "academic-state", "deliberation_candidates.json")
        cls.deliverables_dir = os.path.join(cls.study_dir, "03_deliverables", "stage_06_hypothesis_1")

    def test_01_study_deliberation_candidates_schema_conformity(self):
        """Verify each proposed candidate conforms to contracts/analysis_candidate.schema.json."""
        self.assertTrue(os.path.exists(self.candidates_file), "deliberation_candidates.json must exist")
        with open(self.candidates_file, "r", encoding="utf-8") as f:
            payload = json.load(f)

        candidates = payload.get("candidates", [])
        self.assertEqual(len(candidates), 3, "Must evaluate exactly 3 competing candidates")

        for cand in candidates:
            val = validate_analysis_candidate(cand)
            self.assertTrue(val["valid"], f"Candidate {cand.get('candidate_id')} failed schema: {val.get('errors')}")

    def test_02_deliberation_falsifier_verdicts(self):
        """Verify Academic Challenger invalidates flawed candidates and selects ANCOVA conditionally."""
        temp_dir = tempfile.mkdtemp(prefix="test_vs_delib_")
        try:
            pitfalls_file = os.path.join(temp_dir, "pitfalls.jsonl")
            registry = CanonicalPitfallRegistry(registry_path=pitfalls_file)
            synthesizer = StatisticalMethodologySynthesizer(pitfall_registry=registry)

            with open(self.candidates_file, "r", encoding="utf-8") as f:
                payload = json.load(f)

            res = synthesizer.synthesize_and_select(
                candidates=payload["candidates"],
                study_context=payload["study_context"],
                project_id="study_act_burnout"
            )

            self.assertEqual(res["status"], "SUCCESS")
            self.assertEqual(res["selected_candidate_id"], "CAND-ANCOVA-BURNOUT-01")
            self.assertEqual(res["selection_category"], "CONDITIONAL")
            self.assertEqual(len(res["rejected_candidates"]), 2)

            # Check pitfall persistence
            saved_pitfalls = registry.load_pitfalls()
            self.assertEqual(len(saved_pitfalls), 2)
            for pf in saved_pitfalls:
                val = validate_pitfall(pf)
                self.assertTrue(val["valid"], f"Pitfall failed schema: {val.get('errors')}")
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_03_synthesized_analysis_plan_contract(self):
        """Verify the synthesized AnalysisPlan passes contracts/analysis_plan.schema.json."""
        plan_file = os.path.join(self.study_dir, "academic-state", "analysis_plan.json")
        self.assertTrue(os.path.exists(plan_file), "analysis_plan.json must exist in academic-state")
        with open(plan_file, "r", encoding="utf-8") as f:
            plan = json.load(f)

        val = validate_analysis_plan(plan)
        self.assertTrue(val["valid"], f"AnalysisPlan failed contract schema: {val.get('errors')}")
        self.assertEqual(plan["statistical_models"][0]["family"], "ancova_analysis_of_covariance")

    def test_04_deterministic_statistical_execution(self):
        """Verify statistical execution produces schema-valid execution_manifest.json with hashes."""
        plan_file = os.path.join(self.study_dir, "academic-state", "analysis_plan.json")
        temp_out = tempfile.mkdtemp(prefix="test_vs_exec_")
        try:
            engine = StatisticalPipelineEngine()
            exec_res = engine.execute_statistical_pipeline(
                analysis_plan=plan_file,
                dataset_path=self.raw_data_path,
                out_dir=temp_out,
                mode="production"
            )

            self.assertEqual(exec_res["status"], "SUCCESS")
            self.assertEqual(exec_res["execution_mode"], "production")

            manifest_path = exec_res["manifest_path"]
            self.assertTrue(os.path.exists(manifest_path))
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)

            val = validate_execution_manifest(manifest)
            self.assertTrue(val["valid"], f"Execution manifest failed schema: {val.get('errors')}")
            self.assertEqual(manifest["analysis_plan_hash"], compute_file_sha256(plan_file))
            self.assertEqual(manifest["input_dataset_hash"], compute_file_sha256(self.raw_data_path))
            self.assertEqual(manifest["exit_code"], 0)

            # Results verification
            stats_results_path = exec_res["stats_results_path"]
            with open(stats_results_path, "r", encoding="utf-8") as f:
                res_data = json.load(f)
            self.assertEqual(res_data["sample_size"], 60)
            self.assertIn("F", res_data["test_statistics"])
            self.assertEqual(res_data["degrees_of_freedom"]["df_total"], 59)
        finally:
            shutil.rmtree(temp_out, ignore_errors=True)

    def test_05_triad_artifact_invariant(self):
        """Verify that Stage 06 produces a synchronized triad (.docx, .md, .json) on disk."""
        triad = create_hypothesis_triad(self.deliverables_dir)
        self.assertTrue(os.path.exists(triad["docx"]), "06_hypothesis_1.docx must exist")
        self.assertTrue(os.path.exists(triad["md"]), "06_hypothesis_1.md must exist")
        self.assertTrue(os.path.exists(triad["json"]), "06_hypothesis_1.json must exist")

        self.assertGreater(os.path.getsize(triad["docx"]), 1000)
        self.assertGreater(os.path.getsize(triad["md"]), 100)
        self.assertGreater(os.path.getsize(triad["json"]), 100)

    def test_06_statistical_auditor_independent_report(self):
        """Verify statistical auditor produces a valid contracts/validation_report.schema.json with MSAI."""
        audit_file = os.path.join(self.deliverables_dir, "statistical_audit_report.json")
        self.assertTrue(os.path.exists(audit_file), "statistical_audit_report.json must exist")
        with open(audit_file, "r", encoding="utf-8") as f:
            audit_report = json.load(f)

        val = validate_validation_report(audit_report)
        self.assertTrue(val["valid"], f"Audit report failed schema: {val.get('errors')}")

        # Verify df check was evaluated and passed
        df_checks = [c for c in audit_report["results"] if c.get("check_id") == "CHK-DF-01"]
        self.assertEqual(len(df_checks), 1)
        self.assertEqual(df_checks[0]["verdict"], "PASS")

        # Verify assumption and MSAI audits were recorded
        assump_checks = [c for c in audit_report["results"] if c.get("check_id") == "CHK-ASSUMP-01"]
        self.assertEqual(len(assump_checks), 1)
        msai_checks = [c for c in audit_report["results"] if c.get("check_id") == "CHK-MSAI-01"]
        self.assertEqual(len(msai_checks), 1)

    def test_07_academic_challenger_pitfall_dossier(self):
        """Verify academic challenger produces a valid contracts/pitfall.schema.json."""
        pitfall_file = os.path.join(self.deliverables_dir, "pitfall_challenge_report.json")
        self.assertTrue(os.path.exists(pitfall_file), "pitfall_challenge_report.json must exist")
        with open(pitfall_file, "r", encoding="utf-8") as f:
            pf_dossier = json.load(f)

        val = validate_pitfall(pf_dossier)
        self.assertTrue(val["valid"], f"Pitfall dossier failed schema: {val.get('errors')}")


if __name__ == "__main__":
    unittest.main()
