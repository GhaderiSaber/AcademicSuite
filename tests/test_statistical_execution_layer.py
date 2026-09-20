#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_statistical_execution_layer.py — Verification of the Hardened Statistical Execution Layer (Phase 5)

Verifies:
1. 7-Part Input Contract (StatisticalExecutorContract) schema validation.
2. 7-Part Output Package (StatisticalExecutionResult) schema validation.
3. Fail-closed anti-synthetic guards in production mode:
   - Missing production dataset raises MissingProductionDataError.
   - Sample/demo dataset name raises ProductionSampleFallbackBlockedError.
   - is_synthetic=True in production raises ProductionSampleFallbackBlockedError.
4. Simulation and test mode permissions (is_synthetic=True permitted only in simulation/test).
5. Deterministic ANCOVA execution and result verification.
6. Deterministic multiple regression execution and result verification.
7. Cryptographic provenance generation (SHA-256 data and contract hashes).
8. CLI execution with --contract flag.
"""

import os
import sys
import json
import tempfile
import unittest
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from contracts.contract_validator import (
    validate_statistical_executor_contract,
    validate_statistical_execution_result,
    load_schema
)
from scripts.statistical_pipeline_engine import (
    StatisticalPipelineEngine,
    MissingProductionDataError,
    ProductionSampleFallbackBlockedError,
    MethodMismatchError,
    InvalidAnalysisPlanError
)


class TestStatisticalExecutionLayer(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_stat_exec_")
        self.engine = StatisticalPipelineEngine(repo_root=ROOT_DIR)

        # Create a small deterministic dataset for testing
        self.dataset_path = os.path.join(self.temp_dir, "empirical_trial.csv")
        with open(self.dataset_path, "w", encoding="utf-8") as f:
            f.write("id,group,pre_score,post_score,covariate\n")
            # Group 1 (Treatment: ACT)
            for i in range(1, 16):
                pre = 30.0 + (i % 5)
                post = 18.0 + (i % 4)
                cov = 50.0 + (i % 3)
                f.write(f"{i},ACT,{pre},{post},{cov}\n")
            # Group 2 (Control: TAU)
            for i in range(16, 31):
                pre = 31.0 + (i % 5)
                post = 29.0 + (i % 4)
                cov = 51.0 + (i % 3)
                f.write(f"{i},TAU,{pre},{post},{cov}\n")

    def tearDown(self):
        # Clean up temporary directory
        if os.path.exists(self.temp_dir):
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_valid_executor_contract(self, data_mode="test", is_synthetic=False, method="ancova"):
        """Helper to create a valid 7-part StatisticalExecutorContract."""
        return {
            "contract_version": "1.0.0",
            "contract_id": "SEC-2026-ACT-001",
            "project_id": "test_project",
            "status": "APPROVED",
            "data": {
                "dataset_path": self.dataset_path,
                "dataset_format": "csv",
                "data_mode": data_mode,
                "is_synthetic": is_synthetic
            },
            "variable_map": {
                "subject_id_variable": "id",
                "dependent_variables": ["post_score"],
                "independent_variables": ["group"],
                "covariates": ["pre_score"]
            },
            "design": {
                "study_type": "RCT",
                "group_structure": "multi-group",
                "temporal_dynamics": "repeated measures",
                "waves": "pre-post",
                "factors": ["group"]
            },
            "method_specification": {
                "model_name": method,
                "model_family": "General Linear Model",
                "estimation_method": "OLS",
                "formula": "post_score ~ group + pre_score"
            },
            "assumptions": {
                "required_checks": [
                    {"name": "normality", "metric_or_test": "shapiro_wilk"},
                    {"name": "homoscedasticity", "metric_or_test": "levene"},
                    {"name": "homogeneity_of_slopes", "metric_or_test": "interaction_f"}
                ]
            },
            "parameters": {
                "alpha": 0.05,
                "confidence_level": 0.95,
                "bootstrap_resamples": 5000,
                "random_seed": 42,
                "missing_data_strategy": "listwise"
            },
            "output_contract": {
                "out_dir": self.temp_dir,
                "stats_results_filename": "stats_results.json",
                "stats_table_filename": "stats_table.md",
                "required_table_format": "apa_7_markdown"
            }
        }

    def test_01_valid_executor_contract_validation(self):
        """Verify that a valid 7-part contract passes validation."""
        contract = self._create_valid_executor_contract()
        report = validate_statistical_executor_contract(contract)
        self.assertTrue(report["valid"], f"Contract validation failed: {report.get('errors')}")
        self.assertEqual(len(report["errors"]), 0)

    def test_02_invalid_executor_contract_missing_blocks(self):
        """Verify that missing required blocks in the 7-part contract fail validation."""
        contract = self._create_valid_executor_contract()
        del contract["variable_map"]
        del contract["method_specification"]

        report = validate_statistical_executor_contract(contract)
        self.assertFalse(report["valid"])
        self.assertGreaterEqual(len(report["errors"]), 1)

    def test_03_anti_synthetic_guard_missing_production_data(self):
        """Verify that missing dataset in production mode raises MissingProductionDataError."""
        contract = self._create_valid_executor_contract(data_mode="production")
        contract["data"]["dataset_path"] = "/path/to/nonexistent/production_data.csv"

        with self.assertRaises(MissingProductionDataError):
            self.engine.execute_plan(contract)

    def test_04_anti_synthetic_guard_sample_data_in_production(self):
        """Verify that sample or demo dataset names in production mode raise ProductionSampleFallbackBlockedError."""
        demo_path = os.path.join(self.temp_dir, "sample_rct_demo.csv")
        with open(demo_path, "w") as f:
            f.write("id,group,post_score\n1,ACT,10\n")

        contract = self._create_valid_executor_contract(data_mode="production")
        contract["data"]["dataset_path"] = demo_path

        with self.assertRaises(ProductionSampleFallbackBlockedError):
            self.engine.execute_plan(contract)

    def test_05_anti_synthetic_guard_is_synthetic_true_in_production(self):
        """Verify that is_synthetic=True in production mode raises ProductionSampleFallbackBlockedError."""
        contract = self._create_valid_executor_contract(data_mode="production", is_synthetic=True)

        with self.assertRaises(ProductionSampleFallbackBlockedError):
            self.engine.execute_plan(contract)

    def test_06_simulation_mode_permitted(self):
        """Verify that is_synthetic=True is permitted in simulation mode."""
        contract = self._create_valid_executor_contract(data_mode="simulation", is_synthetic=True)
        report = validate_statistical_executor_contract(contract)
        self.assertTrue(report["valid"])

        # Execution should succeed in simulation mode without ProductionSampleFallbackBlockedError
        output_dir = os.path.join(self.temp_dir, "sim_output")
        results = self.engine.execute_plan(contract, out_dir=output_dir)
        self.assertEqual(results["status"], "SUCCESS")
        self.assertIn("results", results)
        self.assertEqual(results["results"]["status"], "SUCCESS")

    def test_07_deterministic_ancova_execution_and_schema_conformance(self):
        """Verify deterministic ANCOVA calculation and output conforms to statistical_execution_result.schema.json."""
        contract = self._create_valid_executor_contract(method="ancova")
        output_dir = os.path.join(self.temp_dir, "ancova_output")

        execution = self.engine.execute_plan(contract, out_dir=output_dir)
        self.assertEqual(execution["status"], "SUCCESS")

        results = execution["results"]

        # Verify against formal schema
        report = validate_statistical_execution_result(results)
        self.assertTrue(report["valid"], f"Result schema validation failed: {report.get('errors')}")

        # Check the 7 output blocks
        self.assertIn("result_json", results)
        self.assertIn("tables", results)
        self.assertIn("diagnostics", results)
        self.assertIn("effect_sizes", results)
        self.assertIn("confidence_intervals", results)
        self.assertIn("model_information", results)
        self.assertIn("provenance", results)

        # Verify numerical accuracy
        res = results["result_json"]
        self.assertIn("ANCOVA", res["model_name"])
        self.assertEqual(results["model_information"]["sample_size"], 30)
        test_stats = res["test_statistics"]
        self.assertGreater(test_stats["F"], 0.0)
        self.assertLess(test_stats["p_value"], 0.05)

        # Verify diagnostics
        diag = results["diagnostics"]
        self.assertIn("assumption_checks", diag)
        self.assertGreaterEqual(len(diag["assumption_checks"]), 1)

        # Verify provenance
        prov = results["provenance"]
        self.assertEqual(len(prov["dataset_sha256"]), 64)
        self.assertIn("execution_timestamp", results)
        self.assertIn("script_identity", prov)
        self.assertIn("command", prov)

    def test_08_deterministic_regression_execution(self):
        """Verify deterministic multiple regression execution."""
        contract = self._create_valid_executor_contract(method="multiple_regression")
        contract["variable_map"] = {
            "dependent_variables": ["post_score"],
            "independent_variables": ["pre_score", "covariate"]
        }
        contract["method_specification"]["model_name"] = "multiple_regression"
        contract["method_specification"]["formula"] = "post_score ~ pre_score + covariate"

        output_dir = os.path.join(self.temp_dir, "reg_output")
        execution = self.engine.execute_plan(contract, out_dir=output_dir)
        self.assertEqual(execution["status"], "SUCCESS")

        results = execution["results"]
        report = validate_statistical_execution_result(results)
        self.assertTrue(report["valid"], f"Regression result schema validation failed: {report.get('errors')}")

        res = results["result_json"]
        self.assertIn("Regression", res["model_name"])
        self.assertEqual(results["effect_sizes"]["primary_effect"]["metric"], "r_squared")
        self.assertIn("collinearity", results["diagnostics"])
        self.assertIn("assumption_checks", results["diagnostics"])

    def test_09_cli_contract_execution(self):
        """Verify that CLI --contract flag executes successfully."""
        contract = self._create_valid_executor_contract(method="ancova")
        contract_file = os.path.join(self.temp_dir, "cli_contract.json")
        with open(contract_file, "w", encoding="utf-8") as f:
            json.dump(contract, f, indent=2)

        output_dir = os.path.join(self.temp_dir, "cli_output")

        cand = os.path.join(ROOT_DIR, ".agents", "scripts", "statistical_pipeline_engine.py")
        engine_script = cand if os.path.isfile(cand) else os.path.join(ROOT_DIR, "scripts", "statistical_pipeline_engine.py")
        cmd = [
            sys.executable,
            engine_script,
            "--contract", contract_file,
            "--out-dir", output_dir
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"CLI execution failed:\nSTDOUT:\n{proc.stdout}\nSTDERR:\n{proc.stderr}")

        # Check results file
        results_file = os.path.join(output_dir, "stats_results.json")
        self.assertTrue(os.path.exists(results_file))
        with open(results_file, "r", encoding="utf-8") as f:
            saved_results = json.load(f)

        report = validate_statistical_execution_result(saved_results)
        self.assertTrue(report["valid"], f"CLI result schema validation failed: {report.get('errors')}")


if __name__ == "__main__":
    unittest.main()
