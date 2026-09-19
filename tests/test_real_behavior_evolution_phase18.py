#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_real_behavior_evolution_phase18.py — Phase 18 Closed Behavioral Evolution Unit Tests

Verifies the 13-stage closed behavioral evolution pipeline:
1. Behavior Analysis on User Feedback & QC Failure triggers.
2. Zero Chain-of-Thought enforcement on observable trajectories.
3. Isolated Agent Sandbox creation and production non-mutation guarantees.
4. Three-Way Test Arms evaluation (baseline vs candidate vs adversarial).
5. Independent QC verification across 8 dimensions.
6. Held-out test verification and overfitting detection.
7. End-to-end 13-stage closed loop execution.
8. Promotion and archiving governance.
"""

import os
import sys
import json
import shutil
import unittest
import tempfile
from datetime import datetime, timezone

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

from scripts.academic_behavior_analyzer import (
    AcademicBehaviorAnalyzer,
    PrivateCoTDetectedError,
    sanitize_observable_only
)
from scripts.academic_isolated_agent_sandbox import (
    AcademicIsolatedAgentSandbox,
    ProductionIntegrityViolationError,
    compute_sha256
)
from scripts.academic_real_behavior_evolution import AcademicRealBehaviorEvolution
from scripts.academic_dual_loop_engine import AcademicDualLoopEngine
from scripts.academic_integrated_learning_hub import AcademicIntegratedLearningHub
from contracts.contract_validator import validate_behavior_analysis, validate_three_way_evaluation


class TestRealBehaviorEvolutionPhase18(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="agy_phase18_test_")
        self.skills_dir = os.path.join(self.test_dir, ".agents", "skills")
        self.learning_dir = os.path.join(self.test_dir, "learning")
        self.eval_dir = os.path.join(self.learning_dir, "evaluations")
        os.makedirs(self.skills_dir, exist_ok=True)
        os.makedirs(self.eval_dir, exist_ok=True)

        # Create a mock production skill
        self.mock_skill_dir = os.path.join(self.skills_dir, "statistical-data-analyst")
        os.makedirs(self.mock_skill_dir, exist_ok=True)
        self.mock_skill_path = os.path.join(self.mock_skill_dir, "SKILL.md")
        with open(self.mock_skill_path, "w", encoding="utf-8") as f:
            f.write("# Statistical Data Analyst\n\nExecute inferential statistics.\nReport p-values as calculated.\n")

        self.mock_skill_sha = compute_sha256(self.mock_skill_path)

        # Setup evaluation directories with sample test cases
        for s in ["regression", "adversarial", "heldout", "development", "curriculum"]:
            os.makedirs(os.path.join(self.eval_dir, s), exist_ok=True)

        # Sample regression case
        self.reg_case = {
            "contract_version": "1.0.0",
            "case_id": "EVAL-CASE-REG-001",
            "capability": "statistical-data-analyst",
            "suite_type": "regression",
            "task": {
                "prompt": "Analyze regression slopes.",
                "research_question": "Does covariate violate slope homogeneity?"
            },
            "inputs": {
                "dataset_path": "data.xlsx"
            },
            "expected_properties": {
                "required_metrics": {"p_value_threshold": 0.05}
            },
            "forbidden_behaviors": [
                "p_equals_point_zero_zero_zero",
                "omitting_homogeneity_of_slopes_test"
            ],
            "evaluation_method": {
                "runner_type": "DETERMINISTIC_SCRIPT",
                "runner_script": "scripts/academic_evaluation_lab.py"
            },
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        with open(os.path.join(self.eval_dir, "regression", "EVAL-CASE-REG-001.json"), "w", encoding="utf-8") as f:
            json.dump(self.reg_case, f, indent=2)

        # Sample adversarial case
        self.adv_case = {
            "contract_version": "1.0.0",
            "case_id": "EVAL-CASE-ADV-001",
            "capability": "statistical-data-analyst",
            "suite_type": "adversarial",
            "task": {
                "prompt": "Continuous moderator evaluation.",
                "research_question": "Test moderation without median split."
            },
            "inputs": {
                "dataset_path": "data.xlsx"
            },
            "expected_properties": {
                "required_metrics": {"interaction_reported": True}
            },
            "forbidden_behaviors": [
                "median_split_moderator",
                "p_equals_point_zero_zero_zero"
            ],
            "evaluation_method": {
                "runner_type": "DETERMINISTIC_SCRIPT",
                "runner_script": "scripts/academic_evaluation_lab.py"
            },
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        with open(os.path.join(self.eval_dir, "adversarial", "EVAL-CASE-ADV-001.json"), "w", encoding="utf-8") as f:
            json.dump(self.adv_case, f, indent=2)

        # Sample held-out case + manifest
        self.held_case = {
            "contract_version": "1.0.0",
            "case_id": "EVAL-CASE-HELD-001",
            "capability": "statistical-data-analyst",
            "suite_type": "heldout",
            "task": {
                "prompt": "Bootstrap mediation evaluation.",
                "research_question": "Test mediation."
            },
            "inputs": {
                "dataset_path": "data.xlsx"
            },
            "expected_properties": {
                "required_metrics": {"bootstrap_resamples": 5000}
            },
            "forbidden_behaviors": ["baron_and_kenny", "p_equals_point_zero_zero_zero"],
            "evaluation_method": {
                "runner_type": "DETERMINISTIC_SCRIPT",
                "runner_script": "scripts/academic_evaluation_lab.py"
            },
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        held_path = os.path.join(self.eval_dir, "heldout", "EVAL-CASE-HELD-001.json")
        with open(held_path, "w", encoding="utf-8") as f:
            json.dump(self.held_case, f, indent=2)

        held_sha = compute_sha256(held_path)
        with open(os.path.join(self.eval_dir, "heldout", "manifest.sha256"), "w", encoding="utf-8") as f:
            f.write(f"{held_sha}  EVAL-CASE-HELD-001.json\n")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # 1. Behavior Analysis Tests
    # -------------------------------------------------------------------------

    def test_behavior_analysis_user_feedback(self):
        """Tests observable behavior analysis triggered by User Feedback."""
        analyzer = AcademicBehaviorAnalyzer(base_dir=self.test_dir)
        traj_data = {
            "trajectory_id": "TRJ-TEST-001",
            "agent": "statistics-agent",
            "skill": "statistical-data-analyst",
            "ordered_actions": [
                {
                    "step_number": 1,
                    "action_type": "TOOL_CALLED",
                    "actor": "statistics-agent",
                    "tool_name": "run_command",
                    "observable_input": {"command": "python3 run_anova.py"},
                    "observable_output": {"result": "F = 4.5, p = .000"},
                    "description": "Executed ANOVA and reported p = .000"
                }
            ]
        }
        trigger_payload = {
            "feedback_id": "FDB-TEST-001",
            "target_agent": "statistics-agent",
            "target_skill": "statistical-data-analyst",
            "capability": "statistical-data-analyst",
            "task": "hypothesis_1",
            "stage": "06_hypothesis_1",
            "correction": "You reported p = .000 which is strictly prohibited.",
            "desired_behavior": "Report p < .001 in English or ۰.۰۰۱ > p in Persian."
        }

        report = analyzer.analyze(
            trajectory_data=traj_data,
            trigger_type="USER_FEEDBACK",
            trigger_payload=trigger_payload
        )

        self.assertEqual(report["failure_signature"], "REPORTING_P_ZERO")
        self.assertEqual(report["target_agent"], "statistics-agent")
        self.assertEqual(report["observable_failure_step"]["step_number"], 1)
        self.assertIn("p < .001", report["prescribed_behavior"])

        # Schema validation
        val = validate_behavior_analysis(report)
        self.assertTrue(val["valid"], f"Validation failed: {val.get('errors')}")

    def test_behavior_analysis_qc_failure(self):
        """Tests observable behavior analysis triggered by QC Failure."""
        analyzer = AcademicBehaviorAnalyzer(base_dir=self.test_dir)
        traj_data = {
            "trajectory_id": "TRJ-TEST-002",
            "agent": "statistics-agent",
            "skill": "statistical-data-analyst",
            "ordered_actions": [
                {
                    "step_number": 1,
                    "action_type": "TOOL_CALLED",
                    "actor": "statistics-agent",
                    "tool_name": "run_command",
                    "description": "Executed ANCOVA omitting homogeneity_of_slopes test"
                }
            ]
        }
        trigger_payload = {
            "event_id": "EVT-TEST-QC-FAIL",
            "target_agent": "statistics-agent",
            "target_skill": "statistical-data-analyst",
            "capability": "ancova",
            "task": "stage_04",
            "stage": "04_assumptions",
            "errors": ["omitting_homogeneity_of_slopes_test"],
            "failed_assertions": ["assertion_failed: homogeneity_of_slopes"],
            "summary": "ANCOVA slope homogeneity check was omitted."
        }

        report = analyzer.analyze(
            trajectory_data=traj_data,
            trigger_type="QC_FAILURE",
            trigger_payload=trigger_payload
        )

        self.assertEqual(report["failure_signature"], "VIOLATED_ASSUMPTION_IGNORED")
        self.assertEqual(report["trigger_type"], "QC_FAILURE")
        val = validate_behavior_analysis(report)
        self.assertTrue(val["valid"])

    def test_behavior_analysis_observable_only_zero_cot(self):
        """Verifies that private chain-of-thought keys are strictly blocked."""
        analyzer = AcademicBehaviorAnalyzer(base_dir=self.test_dir)
        tainted_traj = {
            "trajectory_id": "TRJ-COT-LEAK",
            "agent": "statistics-agent",
            "thinking": "Secret internal reasoning tokens that should never leak",
            "ordered_actions": []
        }
        trigger_payload = {
            "correction": "Some correction",
            "desired_behavior": "Some behavior"
        }

        with self.assertRaises(PrivateCoTDetectedError):
            analyzer.analyze(
                trajectory_data=tainted_traj,
                trigger_type="USER_FEEDBACK",
                trigger_payload=trigger_payload
            )

    # -------------------------------------------------------------------------
    # 2. Isolated Agent Sandbox Tests
    # -------------------------------------------------------------------------

    def test_sandbox_creation_and_isolation(self):
        """Verifies that the sandbox isolates candidate modifications from production."""
        sandbox = AcademicIsolatedAgentSandbox(base_dir=self.test_dir)
        candidate_data = {
            "candidate_id": "CAND-TEST-001",
            "target_component": ".agents/skills/statistical-data-analyst/SKILL.md",
            "target_type": "SKILL_PROCEDURAL_SPECIFICATION",
            "parent_version": self.mock_skill_sha,
            "mutation": {
                "diff_type": "FULL_CONTENT_REPLACEMENT",
                "content": "# Statistical Data Analyst (Patched)\n\nNever report p = .000; report p < .001."
            },
            "rationale": "Enforces APA 7 reporting rule.",
            "expected_improvement": {
                "target_metric": "zero_p_zero",
                "baseline_value": 1,
                "projected_value": 0
            },
            "affected_capabilities": ["statistical-data-analyst"],
            "author_agent": "behavior-analyst",
            "status": "CANDIDATE",
            "staged_at": datetime.now(timezone.utc).isoformat()
        }

        manifest = sandbox.create_sandbox(candidate_data)
        self.assertEqual(manifest["candidate_id"], "CAND-TEST-001")
        self.assertTrue(os.path.isfile(os.path.join(manifest["sandbox_directory"], "isolated_manifest.json")))
        self.assertTrue(os.path.isfile(os.path.join(manifest["sandbox_directory"], "SKILL.md")))

        # Check patched content in sandbox
        isolated_content = sandbox.get_isolated_content("CAND-TEST-001", "SKILL.md")
        self.assertIn("Never report p = .000", isolated_content)

        # CRUCIAL INVARIANT: Canonical production file must be UNTOUCHED!
        with open(self.mock_skill_path, "r", encoding="utf-8") as f:
            prod_content = f.read()
        self.assertEqual(prod_content, "# Statistical Data Analyst\n\nExecute inferential statistics.\nReport p-values as calculated.\n")
        self.assertEqual(compute_sha256(self.mock_skill_path), self.mock_skill_sha)
        self.assertTrue(sandbox.verify_production_untouched(candidate_data))

    # -------------------------------------------------------------------------
    # 3. Three-Way Test Arms & Independent QC Tests
    # -------------------------------------------------------------------------

    def test_three_way_arms_evaluation_and_schema(self):
        """Tests 3-way evaluation arms (baseline vs candidate vs adversarial) and schema compliance."""
        coordinator = AcademicRealBehaviorEvolution(base_dir=self.test_dir)

        candidate = {
            "candidate_id": "CAND-3WAY-001",
            "target_component": "statistical-data-analyst",
            "mutation_type": "INSTRUCTION_REFINEMENT",
            "mutation": {
                "diff_type": "FULL_CONTENT_REPLACEMENT",
                "content": "# Patched Skill"
            }
        }
        analysis_report = {
            "prescribed_behavior": "Enforce strict p-value reporting: report p < .001 and check slope homogeneity."
        }

        three_way_rep = coordinator._evaluate_three_way_arms(
            candidate=candidate,
            capability="statistical-data-analyst",
            test_case_id="EVAL-CASE-REG-001",
            adversarial_case_id="EVAL-CASE-ADV-001",
            baseline_payload={
                "statistics": {"f_value": 4.12, "p_value": "p = .000"},
                "narrative": "Standard output with p = .000 (forbidden)."
            },
            candidate_payload={
                "statistics": {
                    "estimand": "Fixed effect estimand",
                    "effect_size": 0.28,
                    "confidence_interval": [0.12, 0.44],
                    "artifact_path": "03_results.json",
                    "assumptions_checked": ["homogeneity_of_slopes", "normality"],
                    "is_synthetic": False,
                    "data_mode": "empirical"
                },
                "narrative": "تحلیل با رعایت مفروضه‌ها انجام شد (۰.۰۱ > p)."
            },
            adversarial_payload={
                "statistics": {
                    "estimand": "Continuous moderation",
                    "effect_size": 0.24,
                    "interaction_beta": 0.31,
                    "confidence_interval": [0.10, 0.38],
                    "artifact_path": "03_adv.json",
                    "assumptions_checked": ["continuous_interaction"]
                },
                "narrative": "تعدیل‌گر به صورت پیوسته برازش شد (۰.۰۵ > p)."
            },
            analysis_report=analysis_report
        )

        self.assertIn("baseline", three_way_rep["arms"])
        self.assertIn("candidate", three_way_rep["arms"])
        self.assertIn("adversarial", three_way_rep["arms"])
        self.assertTrue(three_way_rep["comparison_summary"]["defect_resolved"])
        self.assertTrue(three_way_rep["comparison_summary"]["zero_regressions_verified"])
        self.assertEqual(three_way_rep["qc_verdict"], "PASS")
        self.assertEqual(three_way_rep["recommendation"], "PROMOTE")

        # Validate schema
        val = validate_three_way_evaluation(three_way_rep)
        self.assertTrue(val["valid"], f"Validation errors: {val.get('errors')}")

    # -------------------------------------------------------------------------
    # 4. End-to-End 13-Stage Closed Loop Evolution Tests
    # -------------------------------------------------------------------------

    def test_end_to_end_closed_loop_user_feedback(self):
        """Tests complete 13-stage evolution workflow triggered by User Feedback."""
        coordinator = AcademicRealBehaviorEvolution(base_dir=self.test_dir)

        traj_data = {
            "trajectory_id": "TRJ-E2E-001",
            "agent": "statistics-agent",
            "skill": "statistical-data-analyst",
            "ordered_actions": [
                {
                    "step_number": 1,
                    "action_type": "TOOL_CALLED",
                    "actor": "statistics-agent",
                    "tool_name": "run_command",
                    "observable_input": {"command": "python3 run_ancova.py"},
                    "observable_output": {"result": "p = .000 reported"},
                    "description": "Executed ANCOVA with p = .000"
                }
            ]
        }
        trigger_payload = {
            "feedback_id": "FDB-E2E-001",
            "target_agent": "statistics-agent",
            "target_skill": "statistical-data-analyst",
            "capability": "statistical-data-analyst",
            "task": "hypothesis_1",
            "stage": "06_hypothesis_1",
            "correction": "You reported p = .000 which is forbidden.",
            "desired_behavior": "Report p < .001 in English or ۰.۰۰۱ > p in Persian."
        }

        result = coordinator.execute_closed_loop(
            trigger_type="USER_FEEDBACK",
            trigger_payload=trigger_payload,
            trajectory_data=traj_data,
            test_case_id="EVAL-CASE-REG-001",
            adversarial_case_id="EVAL-CASE-ADV-001",
            mode="simulation"
        )

        self.assertEqual(result["status"], "COMPLETED")
        self.assertIsNotNone(result["analysis_report"])
        self.assertIsNotNone(result["lesson"])
        self.assertIsNotNone(result["candidate"])
        self.assertIsNotNone(result["sandbox_manifest"])
        self.assertIsNotNone(result["three_way_evaluation"])
        self.assertEqual(result["three_way_evaluation"]["qc_verdict"], "PASS")

    def test_end_to_end_closed_loop_qc_failure(self):
        """Tests complete 13-stage evolution workflow triggered by QC Failure."""
        coordinator = AcademicRealBehaviorEvolution(base_dir=self.test_dir)

        traj_data = {
            "trajectory_id": "TRJ-QC-001",
            "agent": "statistics-agent",
            "skill": "statistical-data-analyst",
            "ordered_actions": [
                {
                    "step_number": 1,
                    "action_type": "VALIDATION_FAILED",
                    "actor": "validation-agent",
                    "description": "Validation failed on slope homogeneity",
                    "output_or_error": "omitting_homogeneity_of_slopes_test"
                }
            ]
        }
        trigger_payload = {
            "event_id": "EVT-QC-001",
            "target_agent": "statistics-agent",
            "target_skill": "statistical-data-analyst",
            "capability": "statistical-data-analyst",
            "task": "assumptions",
            "stage": "04_assumptions",
            "errors": ["omitting_homogeneity_of_slopes_test"],
            "failed_assertions": ["assertion_failed: homogeneity_of_slopes"],
            "summary": "Stage validator detected omitted homogeneity of slopes test."
        }

        result = coordinator.execute_closed_loop(
            trigger_type="QC_FAILURE",
            trigger_payload=trigger_payload,
            trajectory_data=traj_data,
            test_case_id="EVAL-CASE-REG-001",
            adversarial_case_id="EVAL-CASE-ADV-001",
            mode="simulation"
        )

        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual(result["analysis_report"]["trigger_type"], "QC_FAILURE")
        self.assertEqual(result["analysis_report"]["failure_signature"], "VIOLATED_ASSUMPTION_IGNORED")
        self.assertIsNotNone(result["promotion_result"])

    # -------------------------------------------------------------------------
    # 5. Dual Loop & Learning Hub Integration Tests
    # -------------------------------------------------------------------------

    def test_dual_loop_integration(self):
        """Tests that AcademicDualLoopEngine exposes and delegates to run_closed_behavior_loop."""
        dual_loop = AcademicDualLoopEngine(base_dir=self.test_dir)
        traj_data = {
            "trajectory_id": "TRJ-DUAL-001",
            "agent": "statistics-agent",
            "skill": "statistical-data-analyst",
            "ordered_actions": [
                {
                    "step_number": 1,
                    "action_type": "TOOL_CALLED",
                    "actor": "statistics-agent",
                    "tool_name": "run_command",
                    "description": "p = .000 reported"
                }
            ]
        }
        trigger_payload = {
            "feedback_id": "FDB-DUAL-001",
            "target_agent": "statistics-agent",
            "target_skill": "statistical-data-analyst",
            "capability": "statistical-data-analyst",
            "correction": "p = .000 reported",
            "desired_behavior": "p < .001"
        }

        res = dual_loop.run_closed_behavior_loop(
            trigger_type="USER_FEEDBACK",
            trigger_payload=trigger_payload,
            trajectory_data=traj_data,
            test_case_id="EVAL-CASE-REG-001",
            adversarial_case_id="EVAL-CASE-ADV-001",
            mode="simulation"
        )
        self.assertEqual(res["status"], "COMPLETED")
        self.assertIn("three_way_evaluation", res)

    def test_learning_hub_qc_failure_dispatch(self):
        """Tests that AcademicIntegratedLearningHub dispatches QC failure to closed loop evolution."""
        hub = AcademicIntegratedLearningHub(base_dir=self.test_dir, mode="simulation")
        validator_results = [
            {
                "verdict": "FAIL",
                "check_name": "homogeneity_of_slopes",
                "description": "omitting_homogeneity_of_slopes_test",
                "evidence": "ANCOVA reported without slope interaction test"
            }
        ]

        res = hub.process_validation_failure(
            stage_dir=os.path.join(self.test_dir, "04_assumptions"),
            validator_results=validator_results,
            is_challenger=False
        )

        self.assertEqual(res["action"], "VALIDATION_FAILURE_EVOLUTION_TRIGGERED")
        self.assertIn("evolution_result", res)
        self.assertEqual(res["evolution_result"]["status"], "COMPLETED")


if __name__ == "__main__":
    unittest.main()
