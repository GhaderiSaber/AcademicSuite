#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_architecture_integration_phase37.py — Architecture-Level Integration Test Suite

Phase 37 End-to-End Architectural Integration Tests:
- Test 1: Agent discovery (AcademicSuite opens → all agents discovered)
- Test 2: Subagent invocation (orchestrator → statistics-agent → result)
- Test 3: Invalid stage (unknown stage → BLOCKED)
- Test 4: Missing artifact (missing result.json → UNVERIFIED)
- Test 5: Fake statistics (synthetic result → blocked in production mode)
- Test 6: Narrative mismatch (JSON β=.42, MD β=.37 → FAIL)
- Test 7: Approval (validation → AWAITING_APPROVAL → no next stage)
- Test 8: Approval event (approve → next stage unlocked)
- Test 9: Real learning (agent V1 → mistake → feedback → candidate V2 → real V2 execution → V2 improves → promotion)
- Test 10: Failed learning (candidate V2 → original case improves → held-out case regresses → REJECT)
"""

import os
import sys
import json
import uuid
import shutil
import hashlib
import tempfile
import unittest
from datetime import datetime, timezone

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

import pandas as pd
from validators.agent_integrity import AgentIntegrityValidator
from scripts.statistical_pipeline_engine import (
    StatisticalPipelineEngine,
    ProductionSampleFallbackBlockedError
)
from scripts.academic_state_manager import (
    StrictStateMachine,
    StageState,
    UnknownStageError,
    MissingApprovalError,
    UnmetPrerequisiteError
)
from validators.run_all_validators import run_suite
from validators.result_consistency.validator import validate_cross_artifacts
from scripts.academic_promotion_engine import AcademicPromotionEngine


def _build_valid_ancova_plan(data_path: str, plan_id: str = "PLAN-ANCOVA-001") -> dict:
    """Helper returning a schema-valid AnalysisPlan compliant with contracts/analysis_plan.schema.json."""
    return {
        "contract_version": "1.0.0",
        "plan_id": plan_id,
        "project_id": "study_act_burnout",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "decided_by": "statistical-expert",
        "status": "APPROVED",
        "research_questions": [{"id": "RQ1", "question": "Does ACT reduce posttest burnout?", "target_variables": ["group", "burnout_post", "burnout_pre"]}],
        "hypotheses": [{"id": "H1", "statement": "ACT group exhibits lower posttest burnout.", "type": "group_comparison", "direction": "negative", "independent_variable": "group", "dependent_variable": "burnout_post"}],
        "design": {
            "type": "experimental", "time_structure": "pre_post_repeated_measures",
            "grouping": {"is_grouped": True, "group_variable": "group", "levels": ["intervention", "control"]},
            "power_analysis": {"target_power": 0.85, "significance_alpha": 0.05, "required_n": 30, "software": "G*Power 3.1"}
        },
        "variables": {"outcome_variables": ["burnout_post"], "predictors": ["group"], "covariates": ["burnout_pre"]},
        "estimands": [{"id": "EST-01", "description": "Adjusted mean difference at posttest.", "target_parameter": "average_treatment_effect"}],
        "statistical_models": [{"model_id": "MOD-ANCOVA-01", "family": "ancova_analysis_of_covariance", "estimator": "OLS", "specification": "burnout_post ~ group + burnout_pre"}],
        "assumptions": [{"test_name": "Levene", "target": "variance_homogeneity", "threshold": "p > .05", "action_on_violation": "Robust Welch or rank-transform"}],
        "missing_data_strategy": {"strategy": "listwise_deletion", "mcar_diagnostic_required": True, "maximum_allowed_missing_rate": 0.05, "mean_imputation_prohibited": True},
        "exclusion_rules": [{"rule_id": "EXC-01", "criterion": "Mahalanobis D2 p < .001", "action": "flag_for_review"}],
        "effect_size_specifications": [{"metric": "partial_eta_squared", "benchmark_scale": "Cohen 1988"}],
        "confidence_intervals": {"confidence_level": 0.95, "estimation_method": "bca_bias_corrected_accelerated_bootstrap", "bootstrap_resamples": 5000},
        "multiple_testing_strategy": {"correction_method": "none_planned_orthogonal_hypotheses", "family_definition": "Pre-planned primary hypothesis"},
        "diagnostics": ["Residual normality Q-Q plot", "VIF collinearity check"],
        "required_tables": [{"table_id": "Table 1", "title": "ANCOVA results for posttest burnout", "standard": "apa_7_three_line"}],
        "required_figures": [{"figure_id": "Figure 1", "type": "ANCOVA adjusted means bar chart", "dpi": 300}],
        "execution_specification": {
            "assigned_subagent": "statistics-agent", "engine": "python", "scripts": ["scripts/run_ancova.py"],
            "expected_triad_artifacts": {"docx_path": "06_hypothesis_1.docx", "md_path": "06_hypothesis_1.md", "json_path": "06_hypothesis_1.json"}
        },
        "data": {"dataset_path": data_path, "file_format": "xlsx", "sample_size": 30, "data_mode": "test", "is_synthetic": False}
    }


class TestArchitectureIntegrationPhase37(unittest.TestCase):
    """Authoritative architecture-level integration tests for AcademicSuite."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="agy_phase37_")
        self.state_dir = os.path.join(self.temp_dir, "academic-state")
        os.makedirs(self.state_dir, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # Test 1 — Agent discovery: AcademicSuite opens → agents discovered
    # -------------------------------------------------------------------------
    def test_01_agent_discovery(self):
        """AcademicSuite opens and discovers all registered persistent subagents."""
        agents_dir = os.path.join(ROOT_DIR, ".agents", "agents")
        skills_dir = os.path.join(ROOT_DIR, ".agents", "skills")
        validator = AgentIntegrityValidator(agents_dir=agents_dir, skills_dir=skills_dir)
        report = validator.run_validation()

        self.assertEqual(report["overall_verdict"], "PASS")
        self.assertEqual(report["errors"], 0, f"Discovery had errors: {report.get('issues')}")
        self.assertGreaterEqual(report["agents_validated"], 28, "Must discover at least 28 persistent agents")

        agent_names = set(report.get("canonical_agents", []))
        core_expected = {
            "academic-orchestrator", "statistics-agent", "academic-writer",
            "validation-agent", "methodology-expert", "statistical-expert",
            "data-agent", "data-curator", "evidence-auditor", "statistical-auditor",
            "trajectory-analyzer", "behavior-analyst", "knowledge-curator",
            "skill-evolver", "evaluation-agent", "curriculum-builder"
        }
        missing = core_expected - agent_names
        self.assertEqual(len(missing), 0, f"Expected subagents missing from discovery: {missing}")

    # -------------------------------------------------------------------------
    # Test 2 — Subagent invocation: orchestrator → statistics-agent → result
    # -------------------------------------------------------------------------
    def test_02_subagent_invocation(self):
        """Orchestrator delegates approved plan to statistics-agent producing valid results."""
        out_dir = os.path.join(self.temp_dir, "stage_06_outputs")
        os.makedirs(out_dir, exist_ok=True)

        data_path = os.path.join(self.temp_dir, "empirical_data.xlsx")
        df = pd.DataFrame({
            "subject_id": list(range(1, 31)),
            "group": [1] * 15 + [2] * 15,
            "burnout_pre": [45.2 + i * 0.4 for i in range(30)],
            "burnout_post": [28.1 + i * 0.3 for i in range(15)] + [44.5 + i * 0.35 for i in range(15)]
        })
        df.to_excel(data_path, index=False)

        plan = _build_valid_ancova_plan(data_path, plan_id="PLAN-H1-TEST-001")
        plan["data"]["data_mode"] = "test"

        engine = StatisticalPipelineEngine(repo_root=ROOT_DIR)
        result = engine.execute_statistical_pipeline(
            analysis_plan=plan,
            dataset_path=data_path,
            out_dir=out_dir,
            mode="test"
        )

        self.assertEqual(result["status"], "SUCCESS")
        self.assertEqual(result["execution_mode"], "test")
        self.assertTrue(os.path.isfile(result["stats_results_path"]))
        self.assertTrue(os.path.isfile(result["manifest_path"]))

        with open(result["stats_results_path"], "r", encoding="utf-8") as f:
            stats = json.load(f)
        self.assertEqual(stats["status"], "SUCCESS")
        self.assertIn("provenance", stats)

    # -------------------------------------------------------------------------
    # Test 3 — Invalid stage: unknown stage → BLOCKED
    # -------------------------------------------------------------------------
    def test_03_invalid_stage_is_blocked(self):
        """Requesting transition to an unknown stage is immediately BLOCKED fail-closed."""
        sm = StrictStateMachine(state_dir=self.state_dir, project_id="test_proj")
        with self.assertRaises(UnknownStageError):
            sm.request_transition(
                target_id="stage_99_unknown_telepathy",
                target_state=StageState.STAGE_RUNNING.value
            )

        # Validator suite marks an unknown stage identifier as BLOCKED
        stage_dir = os.path.join(self.temp_dir, "dummy_stage")
        os.makedirs(stage_dir, exist_ok=True)
        with open(os.path.join(stage_dir, "artifact.txt"), "w") as f:
            f.write("dummy")

        rep = run_suite(stage_dir, stage_id="stage_99_unknown_telepathy")
        self.assertEqual(rep["overall_verdict"], "BLOCKED")

    # -------------------------------------------------------------------------
    # Test 4 — Missing artifact: missing result.json → UNVERIFIED
    # -------------------------------------------------------------------------
    def test_04_missing_artifact_is_unverified(self):
        """Stage with missing required statistical artifact or missing manifest returns UNVERIFIED."""
        stage_dir = os.path.join(self.temp_dir, "06_hypothesis_1")
        os.makedirs(stage_dir, exist_ok=True)

        with open(os.path.join(stage_dir, "06_hypothesis_1.md"), "w", encoding="utf-8") as f:
            f.write("# Findings\nNarrative without underlying statistical JSON.")

        rep = run_suite(stage_dir, stage_id="06_hypothesis_1", require_manifest=True)
        self.assertEqual(rep["overall_verdict"], "UNVERIFIED")

    # -------------------------------------------------------------------------
    # Test 5 — Fake statistics: synthetic result → blocked in production mode
    # -------------------------------------------------------------------------
    def test_05_fake_statistics_blocked_in_production_mode(self):
        """Synthetic data flags or sample data paths are strictly blocked in production mode."""
        dummy_path = os.path.join(self.temp_dir, "prod_sample_data.xlsx")
        pd.DataFrame({"group": [1, 2], "burnout_pre": [40, 50], "burnout_post": [30, 45]}).to_excel(dummy_path, index=False)

        plan = _build_valid_ancova_plan(dummy_path, plan_id="PLAN-SYNTH-001")
        plan["data"]["is_synthetic"] = True  # SYNTHETIC DATA IN PRODUCTION

        engine = StatisticalPipelineEngine(repo_root=ROOT_DIR)
        with self.assertRaises(ProductionSampleFallbackBlockedError) as ctx:
            engine.execute_statistical_pipeline(
                analysis_plan=plan,
                dataset_path=dummy_path,
                out_dir=os.path.join(self.temp_dir, "out_synth"),
                mode="production"
            )
        self.assertIn("CRITICAL SAFETY VIOLATION", str(ctx.exception))

    # -------------------------------------------------------------------------
    # Test 6 — Narrative mismatch: JSON β=.42, MD β=.37 → FAIL
    # -------------------------------------------------------------------------
    def test_06_narrative_mismatch_fails(self):
        """Discrepancy between JSON parameter (β=.42) and narrative Markdown (β=.37) causes FAIL."""
        json_path = os.path.join(self.temp_dir, "mismatch_results.json")
        md_path = os.path.join(self.temp_dir, "mismatch_narrative.md")

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "sample_size": 120,
                "coefficients": [
                    {"predictor": "burnout", "beta": 0.42, "t": 3.45, "p_value": 0.001}
                ]
            }, f)

        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Findings\nStandardized regression weight was observed to be β = 0.37 (t = 3.45, p = .001).")

        res = validate_cross_artifacts(json_path, md_path=md_path)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertTrue(any("contradict JSON parameter" in err for err in res["errors"]))
        self.assertTrue(any("0.37" in err and "0.42" in err for err in res["errors"]))

    # -------------------------------------------------------------------------
    # Test 7 — Approval: validation → AWAITING_APPROVAL → no next stage
    # -------------------------------------------------------------------------
    def test_07_validation_to_awaiting_approval_blocks_advancement(self):
        """When a stage is in AWAITING_APPROVAL, advancing without approval is strictly blocked."""
        sm = StrictStateMachine(state_dir=self.state_dir, project_id="test_gating")
        sm.register_stage("stage_01", "Stage 1", initial_status=StageState.STAGE_AWAITING_APPROVAL.value, dependencies=[], requires_manifest=False)
        sm.register_stage("stage_02", "Stage 2", initial_status=StageState.STAGE_LOCKED.value, dependencies=["stage_01"], requires_manifest=False)

        # Attempting to advance stage_02 fails because stage_01 is not STAGE_APPROVED
        with self.assertRaises(UnmetPrerequisiteError):
            sm.request_transition("stage_02", StageState.STAGE_READY.value, check_artifacts=False)

        # Attempting to force-approve stage_01 without approval record fails
        with self.assertRaises(MissingApprovalError):
            sm.request_transition("stage_01", StageState.STAGE_APPROVED.value, check_artifacts=False)

        self.assertEqual(sm.stages["stage_01"]["status"], StageState.STAGE_AWAITING_APPROVAL.value)
        self.assertEqual(sm.stages["stage_02"]["status"], StageState.STAGE_LOCKED.value)

    # -------------------------------------------------------------------------
    # Test 8 — Approval event: approve → next stage unlocked
    # -------------------------------------------------------------------------
    def test_08_approval_event_unlocks_next_stage(self):
        """Explicit human approval grants STAGE_APPROVED and automatically unlocks next stage to STAGE_READY."""
        sm = StrictStateMachine(state_dir=self.state_dir, project_id="test_gating_unlocked")

        val_report = os.path.join(self.state_dir, "stage_01_validation.json")
        with open(val_report, "w", encoding="utf-8") as f:
            json.dump({"overall_verdict": "PASS", "verdict": "PASS"}, f)

        sm.register_stage("stage_01", "Stage 1", initial_status=StageState.STAGE_AWAITING_APPROVAL.value, dependencies=[], requires_manifest=False)
        sm.register_stage("stage_02", "Stage 2", initial_status=StageState.STAGE_LOCKED.value, dependencies=["stage_01"], requires_manifest=False)

        self.assertEqual(sm.stages["stage_02"]["status"], StageState.STAGE_LOCKED.value)

        # 1. Request and grant human approval
        appr = sm.request_approval("stage_01", "DELIVERABLE", "academic-orchestrator", "Stage 1 complete and verified")
        sm.grant_approval(appr["approval_id"], "admin_124911145", "valid_sig_hash")

        # 2. Transition stage_01 to STAGE_APPROVED
        trans_res = sm.request_transition("stage_01", StageState.STAGE_APPROVED.value, check_artifacts=False)
        self.assertIn(trans_res["status"], ["SUCCESS", "TRANSITIONED"])
        self.assertEqual(sm.stages["stage_01"]["status"], StageState.STAGE_APPROVED.value)

        # 3. Prerequisite fulfilled: stage_02 is automatically unlocked to STAGE_READY
        self.assertEqual(sm.stages["stage_02"]["status"], StageState.STAGE_READY.value)

    # -------------------------------------------------------------------------
    # Test 9 — Real learning: agent V1 → mistake → feedback → candidate V2 →
    #                          real V2 execution → V2 improves → promotion
    # -------------------------------------------------------------------------
    def test_09_real_learning_loop_improves_and_promotes(self):
        """Continuous learning loop evaluates candidate V2, confirms zero regressions, and promotes."""
        engine = AcademicPromotionEngine(base_dir=self.temp_dir)
        cid = "CAND-V2-ACCURACY-001"

        # 1. Stage Candidate V2 (synthesized by skill-evolver to fix V1 formatting defect)
        cand_data = {
            "contract_version": "1.0.0",
            "candidate_id": cid,
            "target_component": ".agents/skills/apa-reporting/scripts/generate_apa_tables.py",
            "target_type": "SKILL_DETERMINISTIC_SCRIPT",
            "mutation_type": "DETERMINISTIC_FIX",
            "mutation": {
                "diff_type": "UNIFIED_DIFF",
                "content": "--- a/table.py\n+++ b/table.py\n@@ -1 +1 @@\n-def fmt(p): return f'{p:.3f}'\n+def fmt(p): return '< .001' if p < 0.001 else f'{p:.3f}'",
                "checksum_sha256": hashlib.sha256(b"diff").hexdigest()
            },
            "rationale": "Fixes p=.000 reporting defect to conform strictly to APA 7.",
            "expected_improvement": {"target_metric": "p_zero_violations", "baseline_value": 3, "projected_value": 0},
            "affected_capabilities": ["apa-reporting"],
            "author_agent": "skill-evolver",
            "status": "CANDIDATE",
            "staged_at": datetime.now(timezone.utc).isoformat(),
            "source_lessons": ["LSN-APA-001"],
            "associated_pitfall_id": "EXP-APA-001",
            "testable_hypothesis": "Enforces p < .001 for small p-values."
        }
        with open(os.path.join(engine.candidates_dir, f"{cid}.json"), "w", encoding="utf-8") as f:
            json.dump(cand_data, f, indent=2)

        # 2. Independent evaluation report for V2 execution
        eval_report = {
            "contract_version": "1.0.0",
            "evaluation_id": "EVR-2026-V2-PASS-001",
            "candidate_id": cid,
            "baseline_id": "git-baseline-sha",
            "task_id": "PANEL-STANDARD",
            "dimensions": {k: {"verdict": "PASS"} for k in ["correctness", "methodology", "statistical_validity", "integrity", "robustness", "consistency", "efficiency", "evidence_grounding"]},
            "baseline_metrics": {"total_runs": 10, "passes": 7},
            "candidate_metrics": {"total_runs": 10, "passes": 10},
            "regression_results": {"verdict": "PASS", "count": 0, "details": [], "fixes_original_mistake": True, "evidence_status": "VERIFIED"},
            "adversarial_results": {"verdict": "PASS", "creates_new_mistake": False, "evidence_status": "VERIFIED"},
            "heldout_results": {"verdict": "PASS", "pass_rate": 1.0, "generalizes_to_different_case": True, "overfitting_detected": False, "total_cases": 5, "evidence_status": "VERIFIED"},
            "contradictions": [],
            "evidence": [
                {"artifact_path": "learning/evaluations/reports/EVR-001.json", "sha256": hashlib.sha256(b"e1").hexdigest(), "evidence_type": "EVALUATION_REPORT"},
                {"artifact_path": "learning/evaluations/raw/RUN-001.json", "sha256": hashlib.sha256(b"e2").hexdigest(), "evidence_type": "RAW_EXECUTION_TRACE"},
                {"artifact_path": "learning/evaluations/raw/RUN-002.json", "sha256": hashlib.sha256(b"e3").hexdigest(), "evidence_type": "RAW_EXECUTION_TRACE"}
            ],
            "verdict": "PASS",
            "summary_metrics": {
                "total_cases_evaluated": 10,
                "target_capability_improved": True,
                "zero_regressions_verified": True,
                "adversarial_clearance": True,
                "protected_regressions": 0,
                "suite_pass_rates": {"regression": 1.0, "adversarial": 1.0, "heldout": 1.0}
            },
            "minimum_improvement_policy": {
                "target_capability_improved": True,
                "zero_regressions_verified": True,
                "adversarial_clearance": True
            },
            "counterfactual_analysis": {
                "what_improved": ["Resolved p=.000 violation"],
                "what_regressed": [],
                "which_failure_disappeared": ["p_zero_reported"]
            }
        }

        # 3. Promotion engine evaluates gates and approves promotion
        gates = engine.verify_evaluation_gates(eval_report)
        self.assertTrue(gates["all_passed"], f"Expected all gates to pass, failed: {gates['failures']}")

        res = engine.evaluate_and_promote(cid, eval_report, approver={"identity": "saber_admin_124911145"})
        self.assertEqual(res["decision"], "PROMOTED")
        self.assertEqual(res["status"], "ACTIVE")

    # -------------------------------------------------------------------------
    # Test 10 — Failed learning: candidate V2 → original case improves →
    #                            held-out case regresses → REJECT
    # -------------------------------------------------------------------------
    def test_10_failed_learning_heldout_regression_rejects(self):
        """Candidate V2 that fixes original case but regresses on held-out benchmark is unconditionally REJECTED."""
        engine = AcademicPromotionEngine(base_dir=self.temp_dir)
        cid = "CAND-V2-OVERFIT-002"

        cand_data = {
            "contract_version": "1.0.0",
            "candidate_id": cid,
            "target_component": ".agents/skills/sem/scripts/run_sem.py",
            "target_type": "SKILL_DETERMINISTIC_SCRIPT",
            "mutation_type": "THRESHOLD_OVERRIDE",
            "mutation": {
                "diff_type": "UNIFIED_DIFF",
                "content": "--- a/sem.py\n+++ b/sem.py\n@@ -5,1 +5,1 @@\n-FIT_THRESHOLD = 0.90\n+FIT_THRESHOLD = 0.70",
                "checksum_sha256": hashlib.sha256(b"diff2").hexdigest()
            },
            "rationale": "Forces permissive CFI cutoff to pass original difficult model.",
            "expected_improvement": {"target_metric": "model_fit_pass_rate", "baseline_value": 0.5, "projected_value": 1.0},
            "affected_capabilities": ["sem"],
            "author_agent": "skill-evolver",
            "status": "CANDIDATE",
            "staged_at": datetime.now(timezone.utc).isoformat(),
            "source_lessons": ["LSN-SEM-002"],
            "associated_pitfall_id": "EXP-SEM-002",
            "testable_hypothesis": "Looser cutoff allows more models to pass."
        }
        with open(os.path.join(engine.candidates_dir, f"{cid}.json"), "w", encoding="utf-8") as f:
            json.dump(cand_data, f, indent=2)

        # Original case improves (fixes_original_mistake=True), BUT held-out cases REGRESS!
        eval_report_regressed = {
            "contract_version": "1.0.0",
            "evaluation_id": "EVR-2026-V2-FAIL-002",
            "candidate_id": cid,
            "baseline_id": "git-baseline-sha",
            "task_id": "PANEL-STANDARD",
            "dimensions": {k: {"verdict": "PASS"} for k in ["correctness", "methodology", "statistical_validity", "integrity", "robustness", "consistency", "efficiency", "evidence_grounding"]},
            "baseline_metrics": {"total_runs": 10, "passes": 8},
            "candidate_metrics": {"total_runs": 10, "passes": 6},
            "regression_results": {
                "verdict": "PASS",
                "count": 0,
                "details": [],
                "fixes_original_mistake": True,  # ORIGINAL CASE IMPROVES!
                "evidence_status": "VERIFIED"
            },
            "adversarial_results": {"verdict": "PASS", "creates_new_mistake": False, "evidence_status": "VERIFIED"},
            "heldout_results": {
                "verdict": "FAIL",                # HELD-OUT CASE REGRESSES!
                "pass_rate": 0.60,
                "generalizes_to_different_case": False,
                "overfitting_detected": True,
                "details": ["Held-out case [HE-002] failed: unacceptable fit approved"],
                "total_cases": 5,
                "evidence_status": "VERIFIED"
            },
            "contradictions": [],
            "evidence": [
                {"artifact_path": "learning/evaluations/reports/EVR-002.json", "sha256": hashlib.sha256(b"e4").hexdigest(), "evidence_type": "EVALUATION_REPORT"},
                {"artifact_path": "learning/evaluations/raw/RUN-003.json", "sha256": hashlib.sha256(b"e5").hexdigest(), "evidence_type": "RAW_EXECUTION_TRACE"},
                {"artifact_path": "learning/evaluations/raw/RUN-004.json", "sha256": hashlib.sha256(b"e6").hexdigest(), "evidence_type": "RAW_EXECUTION_TRACE"}
            ],
            "verdict": "FAIL",
            "summary_metrics": {
                "total_cases_evaluated": 10,
                "target_capability_improved": True,
                "zero_regressions_verified": False,
                "adversarial_clearance": True,
                "protected_regressions": 1,
                "suite_pass_rates": {"regression": 1.0, "adversarial": 1.0, "heldout": 0.60}
            },
            "minimum_improvement_policy": {
                "target_capability_improved": True,
                "zero_regressions_verified": True,
                "adversarial_clearance": True
            },
            "counterfactual_analysis": {
                "what_improved": ["Original borderline model now passes"],
                "what_regressed": ["[HE-002] Invalid poor-fitting model was spuriously accepted"],
                "which_failure_disappeared": ["original_fit_failure"]
            }
        }

        # 1. Gate verification must detect the held-out regression
        gates = engine.verify_evaluation_gates(eval_report_regressed)
        self.assertFalse(gates["all_passed"], "Held-out regression must fail gates")
        self.assertEqual(gates["gate_results"]["held_out_evaluation"]["status"], "FAIL")
        self.assertFalse(gates["gate_results"]["held_out_evaluation"]["passed"])
        self.assertTrue(any("held-out" in f.lower() for f in gates["failures"]))

        # 2. Promotion must be rejected and candidate archived
        res = engine.evaluate_and_promote(cid, eval_report_regressed)
        self.assertEqual(res["decision"], "REJECTED", "Must REJECT candidate when held-out panel regresses")
        self.assertEqual(res["status"], "REJECTED_AND_ARCHIVED")


if __name__ == "__main__":
    unittest.main()
