#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_statistical_pipeline_separation.py — Statistical Reasoning vs Execution Separation Tests

Validates:
1. production + missing real data = BLOCKED (MissingProductionDataError)
2. production + sample fallback = BLOCKED (ProductionSampleFallbackBlockedError)
3. demo + sample data = ALLOWED
4. test + fixture data = ALLOWED
5. valid analysis plan = EXECUTABLE
6. invalid analysis plan = BLOCKED (InvalidAnalysisPlanError)
7. statistics-agent cannot switch method (MethodMismatchError)
8. execution manifest records complete cryptographic provenance
9. machine-readable results & strictly derived APA 7 presentation artifacts
10. statistical auditor independent verification (df vs N, assumptions, MSAI)
11. academic challenger adversarial challenge generation (contracts/pitfall.schema.json)
12. orchestrator_cli production mode blocks silent fallback to default_sample
"""

import os
import sys

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

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

ORCH_DIR = os.path.join(ROOT_DIR, ".agents", "skills", "academic-suite-orchestrator", "scripts")
if ORCH_DIR not in sys.path:
    sys.path.insert(0, ORCH_DIR)

import json
import shutil
import tempfile
import unittest
import numpy as np
import pandas as pd

from scripts.statistical_pipeline_engine import (
    StatisticalPipelineEngine,
    MissingProductionDataError,
    ProductionSampleFallbackBlockedError,
    InvalidAnalysisPlanError,
    MethodMismatchError,
    ExecutionIntegrityError,
    is_sample_or_demo_data
)
from contracts.contract_validator import (
    validate_analysis_plan,
    validate_execution_manifest,
    validate_validation_report,
    validate_pitfall
)
from orchestrator_cli import (
    MasterAcademicOrchestrator,
    StageDependencyError,
    ProductionSampleFallbackBlockedError as OrchFallbackBlockedError
)


class TestStatisticalPipelineSeparation(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_stats_sep_")
        self.engine = StatisticalPipelineEngine(repo_root=ROOT_DIR)

        # Build a valid AnalysisPlan conforming to contracts/analysis_plan.schema.json
        self.valid_plan = {
            "contract_version": "1.0.0",
            "plan_id": "PLAN-2026-CH4-001",
            "project_id": "study_act_burnout",
            "created_at": "2026-09-18T07:45:00Z",
            "decided_by": "statistical-expert",
            "status": "APPROVED",
            "research_questions": [
                {
                    "id": "RQ1",
                    "question": "Does ACT intervention reduce posttest burnout controlling for baseline?",
                    "target_variables": ["group", "burnout_post", "burnout_pre"]
                }
            ],
            "hypotheses": [
                {
                    "id": "H1",
                    "statement": "ACT intervention group exhibits lower posttest burnout than control.",
                    "type": "group_comparison",
                    "direction": "negative",
                    "independent_variable": "group",
                    "dependent_variable": "burnout_post"
                }
            ],
            "design": {
                "type": "experimental",
                "time_structure": "pre_post_repeated_measures",
                "grouping": {
                    "is_grouped": True,
                    "group_variable": "group",
                    "levels": ["intervention", "control"]
                },
                "power_analysis": {
                    "target_power": 0.85,
                    "significance_alpha": 0.05,
                    "required_n": 60,
                    "software": "G*Power 3.1"
                }
            },
            "variables": {
                "outcome_variables": ["burnout_post"],
                "predictors": ["group"],
                "covariates": ["burnout_pre"]
            },
            "estimands": [
                {
                    "id": "EST-01",
                    "description": "Adjusted mean difference between intervention and control at posttest.",
                    "target_parameter": "average_treatment_effect"
                }
            ],
            "statistical_models": [
                {
                    "model_id": "MOD-ANCOVA-01",
                    "family": "ancova_analysis_of_covariance",
                    "estimator": "OLS",
                    "specification": "burnout_post ~ group + burnout_pre"
                }
            ],
            "assumptions": [
                {
                    "test_name": "Levene",
                    "target": "variance_homogeneity",
                    "threshold": "p > .05",
                    "action_on_violation": "Robust Welch or rank-transform"
                }
            ],
            "missing_data_strategy": {
                "strategy": "listwise_deletion",
                "mcar_diagnostic_required": True,
                "maximum_allowed_missing_rate": 0.05,
                "mean_imputation_prohibited": True
            },
            "exclusion_rules": [
                {
                    "rule_id": "EXC-01",
                    "criterion": "Mahalanobis D2 p < .001",
                    "action": "flag_for_review"
                }
            ],
            "effect_size_specifications": [
                {
                    "metric": "partial_eta_squared",
                    "benchmark_scale": "Cohen 1988 (small=.01, medium=.06, large=.14)"
                }
            ],
            "confidence_intervals": {
                "confidence_level": 0.95,
                "estimation_method": "bca_bias_corrected_accelerated_bootstrap",
                "bootstrap_resamples": 5000
            },
            "multiple_testing_strategy": {
                "correction_method": "none_planned_orthogonal_hypotheses",
                "family_definition": "Pre-planned primary hypothesis"
            },
            "diagnostics": ["Residual normality Q-Q plot", "VIF collinearity check"],
            "required_tables": [
                {
                    "table_id": "Table 1",
                    "title": "ANCOVA results for posttest burnout",
                    "standard": "apa_7_three_line"
                }
            ],
            "required_figures": [
                {
                    "figure_id": "Figure 1",
                    "type": "ANCOVA adjusted means bar chart",
                    "dpi": 300
                }
            ],
            "execution_specification": {
                "assigned_subagent": "statistics-agent",
                "engine": "python",
                "scripts": ["scripts/run_ancova.py"],
                "expected_triad_artifacts": {
                    "docx_path": "06_hypothesis_1.docx",
                    "md_path": "06_hypothesis_1.md",
                    "json_path": "06_hypothesis_1.json"
                }
            }
        }

        # Save valid plan file
        self.plan_file = os.path.join(self.temp_dir, "analysis_plan.json")
        with open(self.plan_file, "w", encoding="utf-8") as f:
            json.dump(self.valid_plan, f, indent=2)

        # Generate a synthetic empirical dataset (60 cases: 30 intervention, 30 control)
        np.random.seed(42)
        n_group = 30
        groups = ["intervention"] * n_group + ["control"] * n_group
        pre = np.random.normal(35.0, 4.0, n_group * 2)
        # Moderate realistic treatment effect: intervention mean drops by ~2.5 points, control drops by ~0.5
        post = np.where(np.array(groups) == "intervention", pre - 2.5 + np.random.normal(0, 3.0, n_group * 2), pre - 0.5 + np.random.normal(0, 3.0, n_group * 2))

        self.df = pd.DataFrame({
            "group": groups,
            "burnout_pre": pre,
            "burnout_post": post
        })

        # Real empirical dataset path (production)
        self.real_data_path = os.path.join(self.temp_dir, "empirical_clinical_data.xlsx")
        self.df.to_excel(self.real_data_path, index=False)

        # Sample / Demo dataset path
        self.sample_data_path = os.path.join(self.temp_dir, "sample_burnout_demo.xlsx")
        self.df.to_excel(self.sample_data_path, index=False)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_production_missing_data_blocked(self):
        """Production empirical execution MUST raise MissingProductionDataError if data is missing."""
        out_dir = os.path.join(self.temp_dir, "out_missing")
        non_existent_path = os.path.join(self.temp_dir, "does_not_exist.xlsx")

        with self.assertRaises(MissingProductionDataError):
            self.engine.execute_statistical_pipeline(
                analysis_plan=self.plan_file,
                dataset_path=non_existent_path,
                out_dir=out_dir,
                mode="production"
            )

        with self.assertRaises(MissingProductionDataError):
            self.engine.execute_statistical_pipeline(
                analysis_plan=self.plan_file,
                dataset_path="",
                out_dir=out_dir,
                mode="production"
            )

    def test_02_production_sample_fallback_blocked(self):
        """Production execution MUST NEVER silently fall back to sample/demo data (raises ProductionSampleFallbackBlockedError)."""
        out_dir = os.path.join(self.temp_dir, "out_fallback")

        with self.assertRaises(ProductionSampleFallbackBlockedError):
            self.engine.execute_statistical_pipeline(
                analysis_plan=self.plan_file,
                dataset_path=self.sample_data_path,
                out_dir=out_dir,
                mode="production"
            )

    def test_03_demo_mode_allows_sample_data(self):
        """In explicit 'demo' mode, sample datasets are permitted and manifest records mode='demo'."""
        out_dir = os.path.join(self.temp_dir, "out_demo")
        res = self.engine.execute_statistical_pipeline(
            analysis_plan=self.plan_file,
            dataset_path=self.sample_data_path,
            out_dir=out_dir,
            mode="demo"
        )
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["execution_mode"], "demo")
        self.assertTrue(os.path.exists(res["stats_results_path"]))
        self.assertTrue(os.path.exists(res["manifest_path"]))

        with open(res["manifest_path"], "r", encoding="utf-8") as f:
            manifest = json.load(f)
        self.assertEqual(manifest["execution_mode"], "demo")

    def test_04_test_mode_allows_fixture_data(self):
        """In explicit 'test' mode, fixture datasets are permitted and manifest records mode='test'."""
        out_dir = os.path.join(self.temp_dir, "out_test")
        res = self.engine.execute_statistical_pipeline(
            analysis_plan=self.plan_file,
            dataset_path=self.real_data_path,
            out_dir=out_dir,
            mode="test"
        )
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["execution_mode"], "test")
        self.assertTrue(os.path.exists(res["manifest_path"]))

    def test_05_valid_analysis_plan_executes_in_production(self):
        """An approved and schema-valid AnalysisPlan with real empirical data executes successfully in production."""
        out_dir = os.path.join(self.temp_dir, "out_prod_valid")
        res = self.engine.execute_statistical_pipeline(
            analysis_plan=self.plan_file,
            dataset_path=self.real_data_path,
            out_dir=out_dir,
            mode="production"
        )
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["execution_mode"], "production")
        self.assertTrue(os.path.exists(res["stats_results_path"]))
        self.assertTrue(os.path.exists(res["stats_table_path"]))
        self.assertTrue(os.path.exists(res["stats_summary_path"]))
        self.assertTrue(os.path.exists(res["manifest_path"]))

    def test_06_invalid_analysis_plan_blocked(self):
        """An invalid AnalysisPlan missing required contract fields is blocked immediately with InvalidAnalysisPlanError."""
        out_dir = os.path.join(self.temp_dir, "out_invalid_plan")
        broken_plan = {
            "contract_version": "1.0.0",
            "plan_id": "BROKEN-001"
            # Missing research_questions, hypotheses, variables, statistical_models, etc.
        }

        with self.assertRaises(InvalidAnalysisPlanError):
            self.engine.execute_statistical_pipeline(
                analysis_plan=broken_plan,
                dataset_path=self.real_data_path,
                out_dir=out_dir,
                mode="production"
            )

    def test_07_statistics_agent_method_lock_enforced(self):
        """statistics-agent CANNOT switch to an unauthorized statistical method (raises MethodMismatchError)."""
        out_dir = os.path.join(self.temp_dir, "out_method_lock")

        # Plan mandates 'ancova_analysis_of_covariance'
        # Attempting to execute unauthorized method 'two_way_anova' must be blocked
        with self.assertRaises(MethodMismatchError):
            self.engine.execute_statistical_pipeline(
                analysis_plan=self.plan_file,
                dataset_path=self.real_data_path,
                out_dir=out_dir,
                mode="production",
                chosen_method="two_way_anova"
            )

        # Attempting authorized method succeeds
        res = self.engine.execute_statistical_pipeline(
            analysis_plan=self.plan_file,
            dataset_path=self.real_data_path,
            out_dir=out_dir,
            mode="production",
            chosen_method="ancova_analysis_of_covariance"
        )
        self.assertEqual(res["status"], "SUCCESS")

    def test_08_execution_manifest_provenance_records(self):
        """Execution manifest provably records hashes, environment, code identity, and validates against contract schema."""
        out_dir = os.path.join(self.temp_dir, "out_provenance")
        res = self.engine.execute_statistical_pipeline(
            analysis_plan=self.plan_file,
            dataset_path=self.real_data_path,
            out_dir=out_dir,
            mode="production"
        )

        with open(res["manifest_path"], "r", encoding="utf-8") as f:
            manifest = json.load(f)

        # Check required contract schema validity
        val_res = validate_execution_manifest(manifest)
        self.assertTrue(val_res["valid"], f"Execution manifest failed schema: {val_res.get('errors')}")

        # Check provenance details
        self.assertIn("analysis_plan_hash", manifest)
        self.assertEqual(len(manifest["analysis_plan_hash"]), 64)
        self.assertIn("input_dataset_hash", manifest)
        self.assertEqual(len(manifest["input_dataset_hash"]), 64)
        self.assertIn("code_identity", manifest)
        self.assertEqual(manifest["execution_mode"], "production")
        self.assertEqual(manifest["exit_code"], 0)
        self.assertGreaterEqual(len(manifest["produced_artifacts"]), 3)

    def test_09_results_machine_readable_and_presentations_derived(self):
        """Machine-readable results exist and derived presentations reflect exact numbers without hallucination."""
        out_dir = os.path.join(self.temp_dir, "out_derived")
        res = self.engine.execute_statistical_pipeline(
            analysis_plan=self.plan_file,
            dataset_path=self.real_data_path,
            out_dir=out_dir,
            mode="production"
        )

        with open(res["stats_results_path"], "r", encoding="utf-8") as f:
            stats_json = json.load(f)

        with open(res["stats_table_path"], "r", encoding="utf-8") as f:
            table_md = f.read()

        with open(res["stats_summary_path"], "r", encoding="utf-8") as f:
            summary_md = f.read()

        # Check exact numbers in json
        self.assertEqual(stats_json["sample_size"], 60)
        f_val = str(stats_json["test_statistics"]["F"])
        p_val = str(stats_json["test_statistics"]["p_value"])

        # Table must contain F value
        self.assertIn(f_val, table_md)
        self.assertIn("Table 1", table_md)

        # Summary narrative must contain exact N, F, and plan ID
        self.assertIn("N* = 60", summary_md)
        self.assertIn(f_val, summary_md)
        self.assertIn(self.valid_plan["plan_id"], summary_md)

    def test_10_statistical_auditor_independent_verification(self):
        """statistical-auditor verifies degrees of freedom, assumptions, and generates valid validation report."""
        out_dir = os.path.join(self.temp_dir, "out_audit")
        exec_res = self.engine.execute_statistical_pipeline(
            analysis_plan=self.plan_file,
            dataset_path=self.real_data_path,
            out_dir=out_dir,
            mode="production"
        )

        audit_res = self.engine.run_statistical_auditor(
            stats_results_path=exec_res["stats_results_path"],
            dataset_path=self.real_data_path,
            manifest_path=exec_res["manifest_path"],
            out_dir=out_dir
        )

        self.assertEqual(audit_res["overall_verdict"], "PASS")
        report = audit_res["report"]

        # Validate audit report against contracts/validation_report.schema.json
        val_res = validate_validation_report(report)
        self.assertTrue(val_res["valid"], f"Audit report failed contract schema: {val_res.get('errors')}")
        self.assertEqual(report["validator_name"], "statistical-auditor")
        self.assertGreaterEqual(report["evidence_summary"]["checks_passed"], 2)

    def test_11_academic_challenger_generates_pitfall_dossier(self):
        """academic-challenger produces a structured pitfall challenge conforming to contracts/pitfall.schema.json."""
        out_dir = os.path.join(self.temp_dir, "out_challenge")
        exec_res = self.engine.execute_statistical_pipeline(
            analysis_plan=self.plan_file,
            dataset_path=self.real_data_path,
            out_dir=out_dir,
            mode="production"
        )

        chal_res = self.engine.run_academic_challenger(
            analysis_plan_path=self.plan_file,
            stats_results_path=exec_res["stats_results_path"],
            manifest_path=exec_res["manifest_path"],
            out_dir=out_dir
        )

        pitfall = chal_res["pitfall"]
        val_res = validate_pitfall(pitfall)
        self.assertTrue(val_res["valid"], f"Pitfall challenge failed contract schema: {val_res.get('errors')}")
        self.assertEqual(pitfall["detected_by"], "academic-challenger")
        self.assertIn("resolution", pitfall)
        self.assertIn("corrective_action", pitfall["resolution"])

    def test_12_orchestrator_cli_blocks_silent_fallback_in_production(self):
        """orchestrator_cli in 'production' mode blocks fallback to default_sample for statistics step."""
        out_dir = os.path.join(self.temp_dir, "out_orch_safety")
        
        # In production mode with no payload_path configured for 'statistics'
        orch = MasterAcademicOrchestrator(
            config_path=None,
            out_dir=out_dir,
            single_step="statistics",
            mode="production"
        )
        orch.load_configuration()

        # In production mode, building step command without payload must be blocked
        with self.assertRaises(OrchFallbackBlockedError):
            orch._build_step_command("statistics")

        # In demo mode, fallback to default_sample is permitted
        orch_demo = MasterAcademicOrchestrator(
            config_path=None,
            out_dir=out_dir,
            single_step="statistics",
            mode="demo"
        )
        orch_demo.load_configuration()
        cmd, outputs = orch_demo._build_step_command("statistics")
        self.assertIn("Chapter_4_Results.docx", outputs["docx"])
        self.assertTrue(len(cmd) > 0)


if __name__ == "__main__":
    unittest.main()
