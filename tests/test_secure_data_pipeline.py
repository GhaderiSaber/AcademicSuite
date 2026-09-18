#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_secure_data_pipeline.py — Comprehensive Security & Integrity Tests for Empirical Data Pipeline

Tests:
1. Raw Data Immutability:
   - OS-level read-only permissions (0444) via enforce_raw_data_readonly
   - Direct write attempts raise PermissionError
   - Hook interceptor (transcript_and_rule_guard) detects raw paths and destructive commands
2. Provenance Generation:
   - SHA-256 calculation
   - Schema fingerprinting (columns, dtypes, row count, null counts, schema hash)
   - Dataset provenance records
3. DataCurator Engine:
   - Ingestion enforces read-only on raw inputs
   - Produces curated dataset and linked data_provenance.json
4. Execution Modes in MasterAcademicOrchestrator:
   - PRODUCTION: rejects sample fallbacks, missing payloads, and /examples/ paths
   - DEMO: allows sample fallbacks with notice
   - TEST: allows test fixtures
   - DRY_RUN: activates dry-run mode without empirical tasks
5. Execution Modes in Specialized Science Engines:
   - bibliometric_engine: rejects missing --input in production; permits in demo
   - citation_visualizer_engine: rejects missing --input in production; permits in demo
6. AnalysisPlan Approval Gating in StatisticalPipelineEngine:
   - Unapproved plans (DRAFT, PENDING_APPROVAL, REJECTED) are blocked
   - Approved plans (APPROVED) pass gate
7. Dry-Run Mode in StatisticalPipelineEngine:
   - Skips numerical heavy tasks, validates inputs, outputs manifest
8. Execution Manifest Integrity & Schema Validation:
   - Validates required fields: plan_hash, data_hash, execution_mode, dataset_provenance, etc.
"""

import os
import sys
import json
import stat
import shutil
import tempfile
import unittest
import pandas as pd
import numpy as np

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT_DIR, "scripts"))
sys.path.insert(0, os.path.join(ROOT_DIR, ".agents", "verification"))
sys.path.insert(0, os.path.join(ROOT_DIR, ".agents", "skills", "academic-suite-orchestrator", "scripts"))
sys.path.insert(0, os.path.join(ROOT_DIR, ".agents", "skills", "bibliometric-network-analyst", "scripts"))
sys.path.insert(0, os.path.join(ROOT_DIR, ".agents", "skills", "citation-network-visualizer", "scripts"))

from data_curation_engine import (
    compute_sha256,
    compute_schema_fingerprint,
    enforce_raw_data_readonly,
    record_raw_provenance,
    DataCurator
)
from transcript_and_rule_guard import is_raw_data_path, is_raw_data_command
from orchestrator_cli import MasterAcademicOrchestrator
from statistical_pipeline_engine import (
    StatisticalPipelineEngine,
    InvalidAnalysisPlanError
)


class TestRawDataImmutability(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_raw_immutability_")
        self.raw_file = os.path.join(self.temp_dir, "survey_data_raw.xlsx")
        # Create a sample raw DataFrame
        df = pd.DataFrame({
            "subject_id": [1, 2, 3, 4, 5],
            "group": [1, 1, 2, 2, 2],
            "score_pre": [10.5, 12.0, 11.2, 9.8, 13.1],
            "score_post": [14.0, 15.5, 12.0, 11.0, 14.5]
        })
        df.to_excel(self.raw_file, index=False)

    def tearDown(self):
        # Reset permissions so temp directory can be deleted cleanly
        try:
            os.chmod(self.raw_file, stat.S_IWRITE | stat.S_IREAD)
        except OSError:
            pass
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_enforce_raw_data_readonly(self):
        enforce_raw_data_readonly(self.raw_file)
        file_stat = os.stat(self.raw_file)
        mode = file_stat.st_mode
        # File must not have write permissions for user, group, or other
        self.assertEqual(mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH), 0)

        # Attempting to write directly must raise PermissionError
        with self.assertRaises(PermissionError):
            with open(self.raw_file, "a") as f:
                f.write("corrupted data")

    def test_hook_is_raw_data_path(self):
        # Positive raw path matches
        self.assertTrue(is_raw_data_path("/project/data/raw/survey.xlsx"))
        self.assertTrue(is_raw_data_path("01_raw_inputs/dataset.sav"))
        self.assertTrue(is_raw_data_path("data/raw_data/scores.csv"))
        self.assertTrue(is_raw_data_path("thesis_data_raw.xlsx"))
        self.assertTrue(is_raw_data_path("data/raw_dataset.csv"))

        # Non-raw derived/output paths should not be flagged
        self.assertFalse(is_raw_data_path("/project/data/derived/data_curated.xlsx"))
        self.assertFalse(is_raw_data_path("output/results/stats_results.json"))
        self.assertFalse(is_raw_data_path("docs/Chapter_4.docx"))

    def test_hook_is_raw_data_command(self):
        # Destructive shell commands targeting raw data
        self.assertTrue(is_raw_data_command("rm data/raw/survey.xlsx"))
        self.assertTrue(is_raw_data_command("mv raw_data.csv /tmp/"))
        self.assertTrue(is_raw_data_command("echo '' > 01_raw_inputs/data.csv"))
        self.assertTrue(is_raw_data_command("sed -i 's/old/new/' raw_file.xlsx"))
        self.assertTrue(is_raw_data_command("truncate -s 0 data_raw.xlsx"))

        # Safe commands or non-raw targets
        self.assertFalse(is_raw_data_command("python3 scripts/run_analysis.py --input data/curated.xlsx"))
        self.assertFalse(is_raw_data_command("ls -la data/raw/"))
        self.assertFalse(is_raw_data_command("cat data/raw/survey.csv"))


class TestProvenanceGeneration(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_provenance_")
        self.csv_file = os.path.join(self.temp_dir, "raw_data.csv")
        self.df = pd.DataFrame({
            "id": [101, 102, 103, 104],
            "age": [25, 30, 28, np.nan],
            "depression_score": [15.2, 18.0, 12.5, 20.1]
        })
        self.df.to_csv(self.csv_file, index=False)

    def tearDown(self):
        try:
            os.chmod(self.csv_file, stat.S_IWRITE | stat.S_IREAD)
        except OSError:
            pass
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_compute_sha256(self):
        h = compute_sha256(self.csv_file)
        self.assertIsInstance(h, str)
        self.assertEqual(len(h), 64)

    def test_compute_schema_fingerprint(self):
        fp = compute_schema_fingerprint(self.df)
        self.assertIn("columns", fp)
        self.assertEqual(fp["columns"], ["id", "age", "depression_score"])
        self.assertEqual(fp["row_count"], 4)
        self.assertEqual(fp["column_count"], 3)
        self.assertIn("schema_hash", fp)
        self.assertEqual(fp["null_counts"]["age"], 1)

    def test_record_raw_provenance(self):
        prov = record_raw_provenance(self.csv_file, dataset_id="PROJ_SURVEY_RAW")
        self.assertEqual(prov["dataset_identifier"], "PROJ_SURVEY_RAW")
        self.assertEqual(len(prov["sha256"]), 64)
        self.assertTrue(prov["file_size_bytes"] > 0)
        self.assertTrue(prov["is_read_only"])
        self.assertIn("schema_fingerprint", prov)


class TestDataCuratorEngine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_curator_")
        self.raw_file = os.path.join(self.temp_dir, "survey_raw.xlsx")
        self.out_dir = os.path.join(self.temp_dir, "curated_out")
        os.makedirs(self.out_dir, exist_ok=True)

        # Create realistic dataset with items
        data = {
            "id": list(range(1, 21)),
            "group": [1] * 10 + [2] * 10,
            "q1": [3, 4, 3, 2, 4, 5, 3, 4, 3, 4,   2, 3, 2, 1, 2, 3, 2, 1, 2, 2],
            "q2": [3, 4, 3, 2, 4, 5, 3, 4, 3, 4,   2, 3, 2, 1, 2, 3, 2, 1, 2, 2],
            "q3": [3, 4, 3, 2, 4, 5, 3, 4, 3, 4,   2, 3, 2, 1, 2, 3, 2, 1, 2, 2],
        }
        pd.DataFrame(data).to_excel(self.raw_file, index=False)

    def tearDown(self):
        try:
            os.chmod(self.raw_file, stat.S_IWRITE | stat.S_IREAD)
        except OSError:
            pass
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_curation_process(self):
        curator = DataCurator(
            raw_path=self.raw_file,
            output_dir=self.out_dir,
            dataset_id="TEST_RAW_SET",
            mode="production"
        )
        curated_path, prov_path = curator.curate()

        # Check raw file is now read-only
        mode = os.stat(self.raw_file).st_mode
        self.assertEqual(mode & (stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH), 0)

        # Check curated files exist
        self.assertTrue(os.path.exists(curated_path))
        self.assertTrue(os.path.exists(prov_path))

        # Check provenance links raw and curated
        with open(prov_path, "r", encoding="utf-8") as f:
            prov = json.load(f)

        self.assertEqual(prov["execution_mode"], "production")
        self.assertEqual(prov["raw_dataset"]["dataset_identifier"], "TEST_RAW_SET")
        self.assertEqual(len(prov["raw_dataset"]["sha256"]), 64)
        self.assertEqual(len(prov["curated_dataset"]["sha256"]), 64)


class TestExecutionModesOrchestrator(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_orch_modes_")
        self.out_dir = os.path.join(self.temp_dir, "orch_out")
        os.makedirs(self.out_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_production_mode_rejects_missing_payload(self):
        orch = MasterAcademicOrchestrator(
            config_path="",
            out_dir=self.out_dir,
            mode="production"
        )
        # In production mode, _resolve_payload must raise ValueError if step provides no payload
        # and would otherwise fall back to default_sample
        with self.assertRaises(ValueError) as ctx:
            orch._resolve_payload(
                step="demographics",
                step_conf={},
                default_sample="/path/to/examples/sample_data.xlsx"
            )
        self.assertIn("cannot fall back to sample/demo data", str(ctx.exception))

    def test_production_mode_rejects_example_sample_paths(self):
        orch = MasterAcademicOrchestrator(
            config_path="",
            out_dir=self.out_dir,
            mode="production"
        )
        # If payload path points to sample/examples directory, it must be rejected in production
        fake_sample_file = os.path.join(self.temp_dir, "sample_survey.xlsx")
        with open(fake_sample_file, "w") as f:
            f.write("fake")

        with self.assertRaises(ValueError) as ctx:
            orch._resolve_payload(
                step="demographics",
                step_conf={"payload": fake_sample_file}
            )
        self.assertIn("Production execution attempted with sample/demo payload", str(ctx.exception))

    def test_demo_mode_allows_sample_fallback(self):
        fake_sample_file = os.path.join(self.temp_dir, "sample_ok.xlsx")
        with open(fake_sample_file, "w") as f:
            f.write("fake sample")

        orch = MasterAcademicOrchestrator(
            config_path="",
            out_dir=self.out_dir,
            mode="demo"
        )
        resolved = orch._resolve_payload(
            step="demographics",
            step_conf={},
            default_sample=fake_sample_file
        )
        self.assertEqual(resolved, fake_sample_file)

    def test_test_mode_allows_fixtures(self):
        fixture_file = os.path.join(self.temp_dir, "test_fixture.xlsx")
        with open(fixture_file, "w") as f:
            f.write("fixture")

        orch = MasterAcademicOrchestrator(
            config_path="",
            out_dir=self.out_dir,
            mode="test"
        )
        resolved = orch._resolve_payload(
            step="demographics",
            step_conf={"payload": fixture_file}
        )
        self.assertEqual(resolved, fixture_file)

    def test_dry_run_mode_sets_flag(self):
        orch = MasterAcademicOrchestrator(
            config_path="",
            out_dir=self.out_dir,
            mode="dry_run"
        )
        self.assertTrue(orch.dry_run)
        self.assertEqual(orch.mode, "dry_run")


class TestExecutionModesSkillEngines(unittest.TestCase):

    def test_bibliometric_engine_rejects_missing_input_in_production(self):
        import subprocess
        script = os.path.join(
            ROOT_DIR, ".agents", "skills", "bibliometric-network-analyst", "scripts", "bibliometric_engine.py"
        )
        cmd = [sys.executable, script, "--mode", "production"]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("strictly prohibited in production", proc.stderr + proc.stdout)

    def test_citation_visualizer_engine_rejects_missing_input_in_production(self):
        import subprocess
        script = os.path.join(
            ROOT_DIR, ".agents", "skills", "citation-network-visualizer", "scripts", "citation_visualizer_engine.py"
        )
        cmd = [sys.executable, script, "--mode", "production"]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("strictly prohibited in production", proc.stderr + proc.stdout)


class TestStatisticalPipelineSecurity(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_stat_security_")
        self.out_dir = os.path.join(self.temp_dir, "results")
        os.makedirs(self.out_dir, exist_ok=True)

        # Create real curated data file
        self.data_file = os.path.join(self.temp_dir, "real_curated_data.xlsx")
        df = pd.DataFrame({
            "subject_id": list(range(1, 31)),
            "group": ["intervention"] * 15 + ["control"] * 15,
            "burnout_pre": np.random.normal(25, 4, 30),
            "burnout_post": np.random.normal(18, 3, 30)
        })
        df.to_excel(self.data_file, index=False)

        # Base valid analysis plan conforming to contracts/analysis_plan.schema.json
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
                    "required_n": 30,
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

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_unapproved_plan_is_rejected(self):
        unapproved_statuses = ["DRAFT", "PENDING_APPROVAL", "REJECTED", "UNAPPROVED", None]
        for st in unapproved_statuses:
            plan = dict(self.valid_plan)
            if st is None:
                plan.pop("status", None)
            else:
                plan["status"] = st

            engine = StatisticalPipelineEngine()
            with self.assertRaises(InvalidAnalysisPlanError) as ctx:
                engine.execute_statistical_pipeline(
                    analysis_plan=plan,
                    dataset_path=self.data_file,
                    out_dir=self.out_dir,
                    mode="production"
                )
            self.assertTrue(
                "may execute ONLY an approved AnalysisPlan" in str(ctx.exception)
                or "failed contract schema validation" in str(ctx.exception)
            )

    def test_production_mode_rejects_sample_data_path(self):
        plan = dict(self.valid_plan)
        sample_path = os.path.join(self.temp_dir, "sample_burnout_data.xlsx")
        with open(sample_path, "w") as f:
            f.write("sample")

        engine = StatisticalPipelineEngine()
        with self.assertRaises(Exception) as ctx:
            engine.execute_statistical_pipeline(
                analysis_plan=plan,
                dataset_path=sample_path,
                out_dir=self.out_dir,
                mode="production"
            )
        self.assertTrue(
            "Production execution attempted with sample/demo dataset" in str(ctx.exception)
            or "cannot use sample" in str(ctx.exception)
        )

    def test_dry_run_mode_validates_without_empirical_execution(self):
        plan = dict(self.valid_plan)
        engine = StatisticalPipelineEngine()
        result = engine.execute_statistical_pipeline(
            analysis_plan=plan,
            dataset_path=self.data_file,
            out_dir=self.out_dir,
            mode="dry_run"
        )

        self.assertTrue(result.get("dry_run", False))
        self.assertEqual(result.get("execution_mode"), "dry_run")
        manifest_path = os.path.join(self.out_dir, "execution_manifest.json")
        self.assertTrue(os.path.exists(manifest_path))

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)
        self.assertEqual(manifest["execution_mode"], "dry_run")
        self.assertEqual(manifest["exit_code"], 0)
        self.assertIn("dataset_provenance", manifest)

    def test_execution_manifest_records_provenance_and_audit(self):
        plan = dict(self.valid_plan)
        engine = StatisticalPipelineEngine()
        result = engine.execute_statistical_pipeline(
            analysis_plan=plan,
            dataset_path=self.data_file,
            out_dir=self.out_dir,
            mode="test"
        )
        manifest_path = os.path.join(self.out_dir, "execution_manifest.json")
        self.assertTrue(os.path.exists(manifest_path))

        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        # Check required fields
        self.assertIn("manifest_id", manifest)
        self.assertIn("analysis_plan_hash", manifest)
        self.assertIn("input_dataset_hash", manifest)
        self.assertEqual(manifest["execution_mode"], "test")
        self.assertIn("dataset_provenance", manifest)
        self.assertIn("sha256", manifest["dataset_provenance"])
        self.assertIn("schema_fingerprint", manifest["dataset_provenance"])


if __name__ == "__main__":
    unittest.main()
