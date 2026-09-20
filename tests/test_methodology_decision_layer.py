#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_methodology_decision_layer.py — Verification of the Methodology Decision Layer (Phase 4)

Verifies:
1. Complete 8-Step Methodological Decision Ladder formulation
2. Estimand definition (ATE, indirect effect, factor loadings)
3. Candidate methods evaluation and comparative assessment
4. Explicit scientific refutations with literature citations (Lord's paradox, power loss, etc.)
5. Schema compliance against contracts/methodology_decision_record.schema.json
6. Downstream execution contract decoupling ('The Hands' receive the contract)
7. StatisticalPipelineEngine method lock enforcement (executor cannot invent methodology)
8. CLI execution of scripts/methodology_decision_engine.py
"""

import os
import sys
import json
import unittest
import subprocess
import tempfile

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.methodology_decision_engine import (
    MethodologyDecisionEngine,
    format_human_mdr
)
from contracts.contract_validator import (
    validate_methodology_decision_record,
    load_schema
)
from scripts.statistical_pipeline_engine import (
    StatisticalPipelineEngine,
    InvalidAnalysisPlanError,
    MethodMismatchError
)


class TestMethodologyDecisionLayer(unittest.TestCase):

    def setUp(self):
        self.engine = MethodologyDecisionEngine(repo_root=ROOT_DIR)
        self.act_prompt = (
            "Analyze whether ACT affects anxiety and psychological distress "
            "across post-test and two-month follow-up."
        )

    def test_01_act_rct_methodology_decision_record(self):
        """Verify complete 8-step decision ladder for ACT RCT prompt."""
        record = self.engine.formulate_decision_record(self.act_prompt)

        # 1. Research Question
        self.assertEqual(record["research_question"], self.act_prompt)

        # 2. Design
        design = record["design"]
        self.assertEqual(design["study_type"], "RCT")
        self.assertEqual(design["group_structure"], "multi-group")
        self.assertEqual(design["temporal_dynamics"], "repeated measures")
        self.assertEqual(design["waves"], "follow-up")
        self.assertIn("RCT", design["factors"])
        self.assertIn("follow-up", design["factors"])

        # 3. Estimand
        estimand = record["estimand"]
        self.assertEqual(estimand["type"], "ATE")
        self.assertIn("Average Treatment Effect", estimand["targeted_parameter"])
        self.assertIn("ACT", estimand["targeted_parameter"])
        self.assertIn("two-month follow-up", estimand["timepoints"])

        # 4. Candidate Methods
        candidates = record["candidate_methods"]
        self.assertGreaterEqual(len(candidates), 3)
        candidate_names = [c["method"] for c in candidates]
        self.assertTrue(any("Repeated Measures" in name for name in candidate_names))
        self.assertTrue(any("Linear Mixed" in name for name in candidate_names))
        self.assertTrue(any("Gain Score" in name for name in candidate_names))

        # 5. Assumptions
        assumptions = record["assumptions"]
        self.assertGreaterEqual(len(assumptions), 4)
        assumption_names = [a["assumption"] for a in assumptions]
        self.assertTrue(any("Normality" in name for name in assumption_names))
        self.assertTrue(any("Homogeneity" in name for name in assumption_names))
        self.assertTrue(any("Sphericity" in name for name in assumption_names))

        # 6. Selected Method & Refutations
        selected = record["selected_method"]
        self.assertIn("Repeated Measures", selected["name"])
        self.assertIn("General Linear Model", selected["family"])

        rejected = record["rejected_methods"]
        self.assertGreaterEqual(len(rejected), 2)
        rejected_names = [r["method"] for r in rejected]
        self.assertTrue(any("Gain Score" in name for name in rejected_names))
        self.assertTrue(any("Post-Test Only" in name for name in rejected_names))

        # 7. Decision Rationale
        self.assertGreater(len(record["decision_rationale"]), 50)
        self.assertIn("Lord's paradox", record["decision_rationale"])

        # 8. Execution Contract
        ec = record["execution_contract"]
        self.assertEqual(ec["assigned_executor"], "statistics-agent")
        self.assertEqual(ec["engine"], "python")
        self.assertIn("run_repeated_measures.py", ec["script"])
        self.assertIn("alpha", ec["parameters"])
        self.assertIn("expected_triad_artifacts", ec)
        self.assertIn("validation_gates", ec)

    def test_02_rejected_methods_scientific_refutations(self):
        """Verify that rejected methods contain rigorous scientific refutations with citations."""
        record = self.engine.formulate_decision_record(self.act_prompt)
        for rm in record["rejected_methods"]:
            self.assertIn("method", rm)
            self.assertIn("reason", rm)
            self.assertIn("literature_citation", rm)
            self.assertGreater(len(rm["reason"]), 30, f"Refutation reason for '{rm['method']}' must be substantive")
            self.assertGreater(len(rm["literature_citation"]), 10, f"Refutation citation for '{rm['method']}' must exist")

        # Specific refutation checks
        gain_score_refutation = next(r for r in record["rejected_methods"] if "Gain Score" in r["method"])
        self.assertIn("Lord's Paradox", gain_score_refutation["reason"])
        self.assertIn("Vickers", gain_score_refutation["literature_citation"])

        post_only_refutation = next(r for r in record["rejected_methods"] if "Post-Test Only" in r["method"])
        self.assertIn("power", post_only_refutation["reason"].lower())
        self.assertIn("Cohen", post_only_refutation["literature_citation"])

    def test_03_mediation_methodology_decision_record(self):
        """Verify mediation inquiry selects bootstrap and refutes Baron & Kenny and Sobel."""
        q = "Evaluate whether emotional regulation mediates the effect of childhood trauma on adult depression."
        record = self.engine.formulate_decision_record(q)

        self.assertEqual(record["estimand"]["type"], "indirect_effect")
        self.assertIn("Preacher & Hayes", record["selected_method"]["name"])
        self.assertIn("5,000", record["selected_method"]["name"])

        rejected_names = [r["method"] for r in record["rejected_methods"]]
        self.assertTrue(any("Baron & Kenny" in name for name in rejected_names))
        self.assertTrue(any("Sobel" in name for name in rejected_names))

        baron_refutation = next(r for r in record["rejected_methods"] if "Baron & Kenny" in r["method"])
        self.assertIn("power", baron_refutation["reason"].lower())
        self.assertIn("Hayes", baron_refutation["literature_citation"])

        sobel_refutation = next(r for r in record["rejected_methods"] if "Sobel" in r["method"])
        self.assertIn("normal", sobel_refutation["reason"].lower())
        self.assertIn("skewed", sobel_refutation["reason"].lower())

    def test_04_schema_validation(self):
        """Verify that formulated MDR instances validate against methodology_decision_record.schema.json."""
        prompts = [
            self.act_prompt,
            "Evaluate whether emotional regulation mediates the relationship between trauma and depression.",
            "Fit a multiple linear regression predicting academic burnout from neuroticism and study hours."
        ]
        for p in prompts:
            record = self.engine.formulate_decision_record(p)
            verdict = validate_methodology_decision_record(record)
            self.assertTrue(
                verdict.get("valid", False),
                f"Schema validation failed for prompt '{p}': {verdict.get('errors')}"
            )

    def test_05_statistical_executor_enforces_execution_contract(self):
        """Verify that StatisticalPipelineEngine enforces method lock from Methodology Decision Record."""
        pipeline_engine = StatisticalPipelineEngine(repo_root=ROOT_DIR)
        record = self.engine.formulate_decision_record(self.act_prompt, status="APPROVED")

        temp_dir = tempfile.mkdtemp(prefix="test_mdr_enforce_")
        dataset_path = os.path.join(temp_dir, "test_data.xlsx")
        # Create minimal dummy dataset file
        with open(dataset_path, "wb") as f:
            f.write(b"dummy")

        # 1. Validation check
        val = pipeline_engine.validate_analysis_plan(record)
        self.assertTrue(val["valid"])

        # 2. Attempting to execute an unapproved method (e.g. independent_samples_ttest) MUST fail
        with self.assertRaises(MethodMismatchError) as ctx:
            pipeline_engine.execute_plan(
                analysis_plan=record,
                dataset_path=dataset_path,
                mode="dry_run",
                out_dir=temp_dir,
                chosen_method="independent_samples_ttest"
            )
        self.assertIn("violates the approved Methodology Decision Record", str(ctx.exception))

        # 3. Executing with matching method passes method lock check
        res = pipeline_engine.execute_plan(
            analysis_plan=record,
            dataset_path=dataset_path,
            mode="dry_run",
            out_dir=temp_dir,
            chosen_method="General Linear Model"
        )
        self.assertEqual(res["status"], "DRY_RUN_VALIDATED")

    def test_06_unapproved_mdr_blocked(self):
        """Verify that unapproved Methodology Decision Records are blocked fail-closed."""
        pipeline_engine = StatisticalPipelineEngine(repo_root=ROOT_DIR)
        record = self.engine.formulate_decision_record(self.act_prompt, status="DRAFT")

        temp_dir = tempfile.mkdtemp(prefix="test_mdr_draft_")
        dataset_path = os.path.join(temp_dir, "test_data.xlsx")
        with open(dataset_path, "wb") as f:
            f.write(b"dummy")

        with self.assertRaises(InvalidAnalysisPlanError) as ctx:
            pipeline_engine.execute_plan(
                analysis_plan=record,
                dataset_path=dataset_path,
                mode="dry_run",
                out_dir=temp_dir
            )
        self.assertIn("CRITICAL PLAN REJECTION", str(ctx.exception))

    def test_07_cli_execution(self):
        """Verify CLI scripts/methodology_decision_engine.py runs and formats output."""
        cand = os.path.join(ROOT_DIR, ".agents", "scripts", "methodology_decision_engine.py")
        script_path = cand if os.path.isfile(cand) else os.path.join(ROOT_DIR, "scripts", "methodology_decision_engine.py")

        # Text mode
        proc = subprocess.run(
            [sys.executable, script_path, "--prompt", self.act_prompt],
            capture_output=True,
            text=True
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("METHODOLOGY DECISION RECORD (MDR)", proc.stdout)
        self.assertIn("ESTIMAND DEFINITION", proc.stdout)
        self.assertIn("REFUTATION MATRIX", proc.stdout)

        # JSON mode
        proc_json = subprocess.run(
            [sys.executable, script_path, "--prompt", self.act_prompt, "--json"],
            capture_output=True,
            text=True
        )
        self.assertEqual(proc_json.returncode, 0)
        data = json.loads(proc_json.stdout)
        self.assertEqual(data["contract_version"], "1.0.0")
        self.assertEqual(data["status"], "APPROVED")
        self.assertIn("execution_contract", data)


if __name__ == "__main__":
    unittest.main()
