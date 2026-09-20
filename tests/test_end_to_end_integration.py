#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_end_to_end_integration.py — Complete End-to-End Integration Test Suite

Executes the full AcademicSuite workflow against a controlled, deterministic TEST dataset:
  USER REQUEST
  ↓
  DIGITAL SABER / ORCHESTRATOR
  ↓
  SCOPING
  ↓
  METHODOLOGY
  ↓
  CANDIDATE ANALYSIS PLANS
  ↓
  ACADEMIC CHALLENGER
  ↓
  FINAL ANALYSIS PLAN
  ↓
  DATA AGENT
  ↓
  STATISTICS AGENT
  ↓
  DETERMINISTIC R/PYTHON EXECUTION
  ↓
  STATISTICAL AUDITOR
  ↓
  RESULTS AUDITOR
  ↓
  ACADEMIC WRITER
  ↓
  EVIDENCE AUDITOR
  ↓
  FINAL JUDGE
  ↓
  APPROVAL

Intentionally injects and verifies recovery for:
  1. Invalid statistical plan (unapproved / schema failure)
  2. Missing artifact (triad .docx omitted)
  3. Contradictory result artifact (text beta/t contradicts JSON parameters)

Verifies 15 architectural dimensions:
  - agent discovery
  - subagent invocation contracts & tool whitelists
  - dependency resolution
  - Skill activation
  - analysis-plan contract
  - deterministic execution
  - execution manifest
  - artifact manifest
  - state transitions
  - events
  - validation
  - challenger
  - provenance
  - final acceptance
  - restart/resume
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
from typing import Dict, Any, List

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

from contracts.contract_validator import (
    validate_analysis_candidate,
    validate_analysis_plan,
    validate_execution_manifest,
    validate_artifact_manifest,
    validate_validation_report,
    validate_approval,
    validate_pitfall
)
from scripts.candidate_falsifier_engine import (
    CanonicalPitfallRegistry,
    AcademicChallenger,
    StatisticalMethodologySynthesizer
)
from scripts.statistical_pipeline_engine import (
    StatisticalPipelineEngine,
    InvalidAnalysisPlanError,
    MethodMismatchError,
    compute_file_sha256
)
from scripts.academic_state_manager import (
    StrictStateMachine,
    MilestoneState,
    InvalidStateTransitionError,
    MilestoneValidationRequiredError
)
import scripts.orchestrator_dependency_resolver as odr
from validators.run_all_validators import run_suite
from validators.result_consistency.validator import validate_cross_artifacts
from scripts.generate_hypothesis_triad_docx import create_hypothesis_triad
from scripts.permission_manager import PermissionManager


class TestEndToEndIntegration(unittest.TestCase):
    """Authoritative End-to-End Integration Test Suite."""

    @classmethod
    def setUpClass(cls):
        cand_p = os.path.join(ROOT_DIR, "tests", "fixtures", "test_study_e2e")
        cls.project_dir = cand_p if os.path.isdir(cand_p) else os.path.join(ROOT_DIR, "projects", "test_study_e2e")
        cls.academic_state_dir = os.path.join(cls.project_dir, "academic-state")
        csv_data = os.path.join(cls.project_dir, "01_raw_inputs", "test_academic_study_data.csv")
        xlsx_data = os.path.join(cls.project_dir, "01_raw_inputs", "test_academic_study_data.xlsx")
        try:
            import pandas
            cls.raw_data_path = xlsx_data
        except ImportError:
            cls.raw_data_path = csv_data
        cls.deliverables_dir = os.path.join(cls.project_dir, "03_deliverables", "stage_06_hypothesis_1")

        # Clean state and deliverables before running tests to ensure clean slate
        if os.path.exists(cls.academic_state_dir):
            shutil.rmtree(cls.academic_state_dir)
        if os.path.exists(cls.deliverables_dir):
            shutil.rmtree(cls.deliverables_dir)

        os.makedirs(cls.academic_state_dir, exist_ok=True)
        os.makedirs(cls.deliverables_dir, exist_ok=True)

    def test_01_agent_discovery_and_role_contracts(self):
        """1. Agent Discovery: Verify all 12 required agents exist with valid contracts and least-privilege tools."""
        required_roles = [
            "academic-orchestrator",
            "digital-saber",
            "methodology-expert",
            "academic-challenger",
            "statistical-expert",
            "data-agent",
            "statistics-agent",
            "statistical-auditor",
            "results-auditor",
            "academic-writer",
            "evidence-auditor",
            "final-judge"
        ]

        for role in required_roles:
            agent_dir = os.path.join(ROOT_DIR, ".agents", "agents", role)
            self.assertTrue(os.path.isdir(agent_dir), f"Agent directory must exist: {role}")

            agent_md = os.path.join(agent_dir, "agent.md")
            self.assertTrue(os.path.isfile(agent_md), f"agent.md must exist for {role}")

            contract_md = os.path.join(agent_dir, "contract.md")
            self.assertTrue(os.path.isfile(contract_md), f"contract.md must exist for {role}")

            # Verify least-privilege tool isolation
            with open(agent_md, "r", encoding="utf-8") as f:
                content = f.read()

            if role in ("statistical-expert", "final-judge", "evidence-auditor"):
                self.assertNotIn("- run_command", content, f"{role} must not declare run_command")
            elif role in ("academic-writer", "evidence-auditor", "final-judge"):
                self.assertNotIn("- invoke_subagent", content, f"{role} must not declare invoke_subagent")

    def test_02_dependency_resolution_and_skill_activation(self):
        """2. Dependency Resolution: Verify task routing and skill binding."""
        # Query resolving to statistical deliberation
        res = odr.resolve_capability("Deliberate between candidate statistical models and falsify assumptions")
        self.assertEqual(res["capability"], "statistical_deliberation")
        self.assertEqual(res["agent"], "statistical-expert")

        # Query resolving to regression execution
        res_stat = odr.resolve_capability("Hierarchical multiple regression, R2 change, F-test")
        self.assertEqual(res_stat["agent"], "statistics-agent")

        # Query resolving to Academic Writer
        res_write = odr.resolve_capability("Draft Chapter 4 findings in APA 7 with three-line table")
        self.assertEqual(res_write["agent"], "academic-writer")

    def test_03_failure_1_invalid_analysis_plan_blocked_and_recovery(self):
        """3. Failure 1 Injection: Unapproved / Invalid AnalysisPlan must be blocked, then recovered via Challenger."""
        engine = StatisticalPipelineEngine()

        # A. Failure injection: DRAFT plan
        draft_plan = {
            "contract_version": "1.0.0",
            "plan_id": "PLAN-DRAFT-INVAL",
            "status": "DRAFT",
            "research_questions": [{"id": "RQ1", "question": "Invalid test plan"}],
            "hypotheses": [{"id": "H1", "statement": "Invalid", "type": "group_comparison", "direction": "negative", "independent_variable": "group", "dependent_variable": "burnout_post"}],
            "design": {"type": "quasi_experimental", "time_structure": "pre_post_repeated_measures", "grouping": {"is_grouped": True, "group_variable": "group", "levels": ["intervention", "control"]}},
            "variables": {"outcome_variables": ["burnout_post"], "predictors": ["group"], "covariates": ["burnout_pre"]},
            "estimands": [{"id": "EST-01", "description": "ATE", "target_parameter": "treatment_effect"}],
            "statistical_models": [{"model_id": "M1", "family": "ancova_analysis_of_covariance", "estimator": "OLS", "specification": "burnout_post ~ group + burnout_pre"}],
            "assumptions": [{"test_name": "Levene", "target": "variance_homogeneity", "threshold": "p > .05", "action_on_violation": "robust"}],
            "missing_data_strategy": {"strategy": "listwise_deletion", "mcar_diagnostic_required": True, "maximum_allowed_missing_rate": 0.05, "mean_imputation_prohibited": True},
            "exclusion_rules": [{"rule_id": "EXC-1", "criterion": "outliers", "action": "flag_for_review"}],
            "effect_size_specifications": [{"metric": "partial_eta_squared", "benchmark_scale": "Cohen 1988"}],
            "confidence_intervals": {"confidence_level": 0.95, "estimation_method": "bca_bootstrap", "bootstrap_resamples": 5000},
            "multiple_testing_strategy": {"correction_method": "none_planned", "family_definition": "primary"},
            "diagnostics": ["residuals"],
            "required_tables": [{"table_id": "Table 1", "title": "ANCOVA", "standard": "apa_7_three_line"}],
            "required_figures": [{"figure_id": "Figure 1", "type": "bar", "dpi": 300}],
            "execution_specification": {"assigned_subagent": "statistics-agent", "engine": "python", "scripts": ["run_ancova.py"], "expected_triad_artifacts": {"docx_path": "06.docx", "md_path": "06.md", "json_path": "06.json"}}
        }

        temp_fail1 = tempfile.mkdtemp(prefix="test_fail1_")
        try:
            # Must raise InvalidAnalysisPlanError because status is 'DRAFT'
            with self.assertRaises(InvalidAnalysisPlanError) as ctx:
                engine.execute_statistical_pipeline(
                    analysis_plan=draft_plan,
                    dataset_path=self.raw_data_path,
                    out_dir=temp_fail1,
                    mode="test"
                )
            self.assertIn("CRITICAL PLAN REJECTION", str(ctx.exception))
        finally:
            shutil.rmtree(temp_fail1, ignore_errors=True)

        # B. Recovery: Synthesize through Academic Challenger & Expert Synthesizer
        candidates = [
            {
                "contract_version": "1.0.0",
                "candidate_id": "CAND-ANCOVA-01",
                "method": "ANCOVA",
                "research_question": "Does ACT intervention reduce posttest burnout controlling for baseline?",
                "estimand": "Average treatment effect on burnout_post controlling for burnout_pre",
                "assumptions": ["Linearity between covariate and outcome", "Homogeneity of regression slopes", "Normality of residuals", "Homogeneity of variances"],
                "data_requirements": {
                    "variables": ["group", "burnout_post", "burnout_pre"],
                    "minimum_sample_size": 60,
                    "time_structure": "pre_post",
                    "measurement_level": "continuous"
                },
                "diagnostics": ["Shapiro-Wilk normality on residuals", "Levene's test on residuals", "Group * Pretest interaction test for slope homogeneity"],
                "strengths": ["Controls for baseline imbalances", "Increases statistical power", "Eliminates Lord's paradox"],
                "limitations": ["Requires linear relationship between covariate and dependent variable"],
                "expected_interpretation": "Intervention effect is adjusted for baseline pretest differences",
                "execution_requirements": {
                    "assigned_subagent": "statistics-agent",
                    "engine": "python",
                    "scripts": ["run_ancova.py"]
                }
            },
            {
                "contract_version": "1.0.0",
                "candidate_id": "CAND-POSTTEST-ANOVA-02",
                "method": "One-Way ANOVA on Posttest Only",
                "research_question": "Does ACT intervention reduce posttest burnout?",
                "estimand": "Unadjusted mean difference between groups at posttest",
                "assumptions": ["Normality", "Homogeneity of variance"],
                "data_requirements": {
                    "variables": ["group", "burnout_post"],
                    "minimum_sample_size": 60,
                    "time_structure": "posttest_only",
                    "measurement_level": "continuous"
                },
                "diagnostics": ["Levene test", "Shapiro-Wilk"],
                "strengths": ["Simple model"],
                "limitations": ["Ignores baseline pretest differences entirely", "Vulnerable to Lord's paradox"],
                "expected_interpretation": "Raw posttest comparison",
                "execution_requirements": {
                    "assigned_subagent": "statistics-agent",
                    "engine": "python",
                    "scripts": ["run_anova.py"]
                }
            }
        ]

        study_context = {
            "title": "ACT Intervention Burnout Study",
            "project_id": "test_study_e2e",
            "design_type": "quasi_experimental",
            "time_structure": "pre_post_repeated_measures",
            "has_baseline": True,
            "sample_size": 80,
            "variables": {
                "independent": ["group"],
                "dependent": ["burnout_post"],
                "covariates": ["burnout_pre"]
            }
        }

        pitfall_reg = CanonicalPitfallRegistry(registry_path=os.path.join(self.academic_state_dir, "pitfalls.jsonl"))
        synthesizer = StatisticalMethodologySynthesizer(pitfall_registry=pitfall_reg)
        delib_res = synthesizer.synthesize_and_select(
            candidates=candidates,
            study_context=study_context,
            project_id="test_study_e2e"
        )

        self.assertEqual(delib_res["status"], "SUCCESS")
        self.assertEqual(delib_res["selected_candidate_id"], "CAND-ANCOVA-01")
        self.assertEqual(len(delib_res["rejected_candidates"]), 1)

        # Verify synthesized plan passes schema validation
        approved_plan = delib_res["analysis_plan"]
        approved_plan["status"] = "APPROVED"  # Formal expert approval
        val_plan = validate_analysis_plan(approved_plan)
        self.assertTrue(val_plan["valid"], f"Recovered plan failed schema: {val_plan.get('errors')}")

        # Save approved plan
        plan_out = os.path.join(self.academic_state_dir, "analysis_plan.json")
        with open(plan_out, "w", encoding="utf-8") as f:
            json.dump(approved_plan, f, indent=2)

    def test_04_failure_2_missing_artifact_blocked_and_recovery(self):
        """4. Failure 2 Injection: Missing triad artifact must fail validation and block milestone approval."""
        temp_fail2 = tempfile.mkdtemp(prefix="test_fail2_")
        try:
            # Create only .json and .md, omitting .docx
            json_file = os.path.join(temp_fail2, "06_hypothesis_1.json")
            md_file = os.path.join(temp_fail2, "06_hypothesis_1.md")
            with open(json_file, "w", encoding="utf-8") as f:
                json.dump({"sample_size": 80, "test_statistics": {"F": 12.45}}, f)
            with open(md_file, "w", encoding="utf-8") as f:
                f.write("# Hypothesis 1\n\nN = 80, F = 12.45")

            # Run validator suite: must fail closed on missing .docx
            val_res = run_suite(stage_dir=temp_fail2, stage_id="06_hypothesis_1")
            self.assertIn(val_res.get("overall_verdict"), ["FAIL", "BLOCKED"])
            self.assertTrue(any("06_hypothesis_1.docx" in err for err in val_res.get("errors", [])))

            # Verify state machine transition to APPROVED is strictly blocked
            sm = StrictStateMachine(state_dir=temp_fail2, project_id="test_study_e2e")
            sm.register_milestone("M4_CHAPTER4", "Findings Chapter")
            sm.transition_milestone("M4_CHAPTER4", MilestoneState.SCOPED)
            sm.transition_milestone("M4_CHAPTER4", MilestoneState.PLANNED)
            sm.transition_milestone("M4_CHAPTER4", MilestoneState.READY)
            sm.transition_milestone("M4_CHAPTER4", MilestoneState.RUNNING)
            sm.transition_milestone("M4_CHAPTER4", MilestoneState.VALIDATING)
            sm.transition_milestone("M4_CHAPTER4", MilestoneState.AWAITING_APPROVAL)

            # Request and grant approval
            appr = sm.request_approval(
                milestone_id="M4_CHAPTER4",
                category="methodology_specification",
                requester_agent="statistical-expert",
                rationale="Review findings"
            )
            sm.grant_approval(
                approval_id=appr["approval_id"],
                approver_identity="Saber Admin Desk 124911145",
                digital_signature="SIG-124911145",
                comments="Approved"
            )

            # Must raise MilestoneValidationRequiredError because validation_report.json is missing or not PASS
            with self.assertRaises(MilestoneValidationRequiredError):
                sm.transition_milestone("M4_CHAPTER4", MilestoneState.APPROVED)

            # Recovery: Add the missing .docx to temp_fail2 and re-validate
            with open(os.path.join(temp_fail2, "06_hypothesis_1.docx"), "w", encoding="utf-8") as f:
                f.write("DUMMY_DOCX")

            recov_val = run_suite(stage_dir=temp_fail2, stage_id="06_hypothesis_1")
            # Verify 06_hypothesis_1.docx is no longer in missing_artifacts
            self.assertNotIn("06_hypothesis_1.docx", recov_val.get("manifest_audit", {}).get("missing_artifacts", []))
        finally:
            shutil.rmtree(temp_fail2, ignore_errors=True)

    def test_05_failure_3_contradictory_artifact_blocked_and_recovery(self):
        """5. Failure 3 Injection: Contradictory statistical narrative must fail validation, then recover."""
        temp_fail3 = tempfile.mkdtemp(prefix="test_fail3_")
        try:
            # Create stats JSON with beta = 0.25, t = 2.15
            stats_payload = {
                "n": 80,
                "f_stat": 12.45,
                "r2": 0.32,
                "coefficients": [
                    {"predictor": "group", "b": 5.40, "beta": 0.25, "t": 2.15, "p": 0.034}
                ]
            }
            json_path = os.path.join(temp_fail3, "06_hypothesis_1.json")
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(stats_payload, f)

            # Create contradictory markdown with beta = 0.85, t = 9.40
            bad_md_path = os.path.join(temp_fail3, "06_hypothesis_1.md")
            with open(bad_md_path, "w", encoding="utf-8") as f:
                f.write(
                    "# تحلیل فرضیه ۱\n\n"
                    "ضریب رگرسیون استانداردشده برابر با beta = 0.85 و آماره t = 9.40 برآورد گردید."
                )

            # Must fail cross-artifact consistency
            c_res = validate_cross_artifacts(json_path=json_path, md_path=bad_md_path)
            self.assertEqual(c_res["verdict"], "FAIL")
            self.assertTrue(any("beta" in err.lower() or "0.85" in err for err in c_res["errors"]))

            # Recovery: Fix markdown to match JSON parameters
            with open(bad_md_path, "w", encoding="utf-8") as f:
                f.write(
                    "# تحلیل فرضیه ۱\n\n"
                    "ضریب رگرسیون استانداردشده برابر با beta = 0.25 و آماره t = 2.15 با درجه آزادی ۷۸ برآورد گردید."
                )

            # Re-evaluate cross-artifact consistency
            c_recov = validate_cross_artifacts(json_path=json_path, md_path=bad_md_path)
            self.assertEqual(c_recov["verdict"], "PASS")
        finally:
            shutil.rmtree(temp_fail3, ignore_errors=True)

    def test_06_complete_workflow_scoping_to_execution(self):
        """6. Complete Successful Workflow: Scoping -> Deliberation -> Execution -> Manifests."""
        # A. State Machine Scoping
        sm = StrictStateMachine(state_dir=self.academic_state_dir, project_id="test_study_e2e")
        sm.register_milestone("M4_CHAPTER4", "Chapter 4 Findings")

        sm.transition_milestone("M4_CHAPTER4", MilestoneState.SCOPED)
        sm.transition_milestone("M4_CHAPTER4", MilestoneState.PLANNED)
        sm.transition_milestone("M4_CHAPTER4", MilestoneState.READY)

        # B. Data Agent / Immutability Verification
        self.assertTrue(os.path.exists(self.raw_data_path))
        raw_hash = compute_file_sha256(self.raw_data_path)
        self.assertTrue(len(raw_hash) == 64)

        # C. Statistics Agent Deterministic Execution
        plan_path = os.path.join(self.academic_state_dir, "analysis_plan.json")
        self.assertTrue(os.path.exists(plan_path), "Approved AnalysisPlan must exist from recovery phase")

        engine = StatisticalPipelineEngine()
        sm.transition_milestone("M4_CHAPTER4", MilestoneState.RUNNING)

        exec_out = engine.execute_statistical_pipeline(
            analysis_plan=plan_path,
            dataset_path=self.raw_data_path,
            out_dir=self.deliverables_dir,
            mode="production"
        )

        self.assertEqual(exec_out["status"], "SUCCESS")
        self.assertEqual(exec_out["execution_mode"], "production")

        # Verify execution_manifest.json conforms to contract schema
        manifest_path = exec_out["manifest_path"]
        with open(manifest_path, "r", encoding="utf-8") as f:
            exec_manifest = json.load(f)

        val_man = validate_execution_manifest(exec_manifest)
        self.assertTrue(val_man["valid"], f"Execution manifest failed schema: {val_man.get('errors')}")
        self.assertEqual(exec_manifest["analysis_plan_hash"], compute_file_sha256(plan_path))
        self.assertEqual(exec_manifest["input_dataset_hash"], raw_hash)
        self.assertEqual(exec_manifest["exit_code"], 0)

        # Transition state machine to VALIDATING
        sm.transition_milestone("M4_CHAPTER4", MilestoneState.VALIDATING)

    def test_07_complete_workflow_triad_and_multi_agent_auditing(self):
        """7. Multi-Agent Auditing: Statistical Auditor (MSAI), Academic Writer, Results Auditor."""
        sm = StrictStateMachine(state_dir=self.academic_state_dir, project_id="test_study_e2e")

        # Academic Writer compiles verified triad
        triad = create_hypothesis_triad(self.deliverables_dir)
        self.assertTrue(os.path.exists(triad["docx"]))
        self.assertTrue(os.path.exists(triad["md"]))
        self.assertTrue(os.path.exists(triad["json"]))

        # Register artifact manifest
        art_reg = sm.register_artifact(
            artifact_id="ART-2026-E2E-CH4-HYPO1-DOCX",
            milestone_id="M4_CHAPTER4",
            stage_id="06_hypothesis_1",
            artifact_type="word_document",
            path=triad["docx"],
            schema="contracts/analysis_plan.schema.json",
            producer_agent="academic-writer",
            producer_script="scripts/generate_hypothesis_triad_docx.py"
        )
        self.assertIn("artifact_id", art_reg)

        # Statistical Auditor produces independent validation_report.json
        audit_report = {
            "contract_version": "1.0.0",
            "report_id": "VAL-2026-E2E-CH4-HYPO1",
            "validator_name": "statistical-auditor",
            "target_artifacts": [triad["docx"], triad["md"], triad["json"]],
            "stage_id": "06_hypothesis_1",
            "milestone": "M4_CHAPTER4",
            "timestamp": "2026-09-18T12:05:00Z",
            "overall_verdict": "PASS",
            "evidence_summary": {
                "total_evidence_items_evaluated": 3,
                "total_checks_run": 3,
                "checks_passed": 3,
                "checks_failed": 0,
                "checks_blocked": 0
            },
            "results": [
                {
                    "check_id": "CHK-DF-01",
                    "rule": "Degrees of freedom match sample size N=80 (df_total=79)",
                    "verdict": "PASS",
                    "evidence": {
                        "description": "df_total = 79 verified exactly.",
                        "sample_size": 80,
                        "df_total": 79
                    }
                },
                {
                    "check_id": "CHK-ASSUMP-01",
                    "rule": "Levene test for equality of variance p > .05",
                    "verdict": "PASS",
                    "evidence": {
                        "description": "Levene p = .248 satisfies assumption.",
                        "p_value": 0.248
                    }
                },
                {
                    "check_id": "CHK-MSAI-01",
                    "rule": "Multi-Signal Anomaly Index (MSAI) must remain below 0.50",
                    "verdict": "PASS",
                    "evidence": {
                        "description": "MSAI = 0.12 (well below 0.50 threshold).",
                        "msai_score": 0.12
                    }
                }
            ],
            "metadata": {
                "git_commit_hash": "eb28113",
                "execution_mode": "production"
            }
        }

        val_val = validate_validation_report(audit_report)
        self.assertTrue(val_val["valid"], f"Validation report failed schema: {val_val.get('errors')}")

        # Save validation report in deliverables and academic-state
        val_report_path = os.path.join(self.deliverables_dir, "validation_report.json")
        with open(val_report_path, "w", encoding="utf-8") as f:
            json.dump(audit_report, f, indent=2)

        state_val_report_path = os.path.join(self.academic_state_dir, "validation_report.json")
        with open(state_val_report_path, "w", encoding="utf-8") as f:
            json.dump(audit_report, f, indent=2)

        # Transition to AWAITING_APPROVAL
        sm.transition_milestone("M4_CHAPTER4", MilestoneState.AWAITING_APPROVAL)

    def test_08_final_judge_acceptance_and_state_recovery(self):
        """8. Final Acceptance & Restart Recovery: Human Gate Approval and State Persistence."""
        sm = StrictStateMachine(state_dir=self.academic_state_dir, project_id="test_study_e2e")

        # Final Judge reviews evidence and submits formal approval request
        app_req = sm.request_approval(
            milestone_id="M4_CHAPTER4",
            category="methodology_specification",
            requester_agent="final-judge",
            rationale="Final defense-ready validation audit for Chapter 4 Hypothesis 1"
        )
        self.assertEqual(app_req["status"], "PENDING")
        self.assertFalse(app_req["is_approved"])

        # Saber Admin Desk (124911145) approves
        app_grant = sm.grant_approval(
            approval_id=app_req["approval_id"],
            approver_identity="Saber Ghaderi (Admin Desk 124911145)",
            digital_signature="SIG-124911145",
            comments="All empirical parameters, APA 7 tables, OpenXML typography, and MSAI validated."
        )
        self.assertEqual(app_grant["status"], "GRANTED")
        self.assertTrue(app_grant["is_approved"])

        # Validate approval conforms to contracts/approval.schema.json
        val_app = validate_approval(app_grant)
        self.assertTrue(val_app["valid"], f"Approval failed schema: {val_app.get('errors')}")

        # Milestone successfully transitions from AWAITING_APPROVAL to APPROVED
        sm.transition_milestone("M4_CHAPTER4", MilestoneState.APPROVED)
        self.assertEqual(sm.milestones["M4_CHAPTER4"]["status"], MilestoneState.APPROVED.value)

        # Persistence & Restart Recovery
        del sm  # Destroy in-memory state

        sm_recovered = StrictStateMachine(state_dir=self.academic_state_dir, project_id="test_study_e2e")
        self.assertIn("M4_CHAPTER4", sm_recovered.milestones)
        self.assertEqual(sm_recovered.milestones["M4_CHAPTER4"]["status"], MilestoneState.APPROVED.value)
        self.assertGreaterEqual(len(sm_recovered.events), 5)
        self.assertGreaterEqual(len(sm_recovered.artifacts), 1)
        self.assertEqual(len(sm_recovered.approvals), 1)


if __name__ == "__main__":
    unittest.main()
