#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_evolution_contracts.py — Unit Tests for AcademicSuite Evolution Contract Layer

Verifies:
1. All 14 evolution contract schemas compile under JSON Schema Draft 7.
2. Experience schema validates raw research episodes.
3. Trajectory schema strictly forbids private model chain-of-thought and validates observable actions.
4. Feedback schema validates corrections, desired behaviors, and severities.
5. Lesson schema allows lessons to exist without active behavior and distinguishes project-specific scope.
6. KnowledgeItem schema captures applicability, exclusions, and counter-indications.
7. Exemplar and AntiPattern schemas enforce gold standards and failure cataloging.
8. SkillMemoryRecord and CapabilityProfile validate operational bounds and telemetry.
9. ImprovementCandidate validates staged mutations, diffs, and target components.
10. EvaluationCase and EvaluationResult preserve multidimensional metrics and forbid scalar intelligence scores.
11. PromotionDecision structurally forbids promotion without passing evaluation evidence, zero regressions, and human approval.
12. CurriculumTask validates graduated training scenarios.
"""

import os
import sys
import json
import unittest
from datetime import datetime, timezone

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from contracts.contract_validator import (
    load_schema,
    validate_contract,
    validate_experience,
    validate_trajectory,
    validate_feedback,
    validate_lesson,
    validate_knowledge_item,
    validate_exemplar,
    validate_anti_pattern,
    validate_skill_memory_record,
    validate_improvement_candidate,
    validate_evaluation_case,
    validate_evaluation_result,
    validate_promotion_decision,
    validate_capability_profile,
    validate_curriculum_task,
    SCHEMA_FILES
)


class TestEvolutionContractSystem(unittest.TestCase):
    """Authoritative test suite for the AcademicSuite Evolution Contract Layer."""

    def test_01_all_fourteen_evolution_schemas_compile(self):
        """All 14 evolution contract schemas must exist in contracts/evolution/ and compile under Draft-7."""
        evolution_keys = [
            "experience",
            "trajectory",
            "feedback",
            "lesson",
            "knowledge_item",
            "exemplar",
            "anti_pattern",
            "skill_memory_record",
            "improvement_candidate",
            "evaluation_case",
            "evaluation_result",
            "promotion_decision",
            "capability_profile",
            "curriculum_task"
        ]

        for key in evolution_keys:
            self.assertIn(key, SCHEMA_FILES, f"Schema key '{key}' missing from SCHEMA_FILES")
            schema = load_schema(key)
            self.assertIsInstance(schema, dict, f"Schema '{key}' is not a valid JSON dictionary")
            self.assertEqual(schema.get("$schema"), "http://json-schema.org/draft-07/schema#", f"Schema '{key}' must be Draft-07")
            self.assertTrue(schema.get("title", "").startswith("Academic"), f"Schema '{key}' title must start with 'Academic'")

    def test_02_experience_contract_valid_and_invalid(self):
        """Experience contract must validate complete episodes and reject missing required fields."""
        valid_exp = {
            "contract_version": "1.0.0",
            "experience_id": "EXP-2026-CH4-001",
            "project_id": "study_act_burnout",
            "task_id": "stage_06_hypothesis_1",
            "milestone_id": "M7_HYPOTHESIS_TESTING",
            "agent": "statistics-agent",
            "skill": "mediation",
            "start_time": "2026-09-18T10:00:00Z",
            "end_time": "2026-09-18T10:05:30Z",
            "duration_seconds": 330.0,
            "outcome": "SUCCESS",
            "artifact_references": [
                {
                    "path": "projects/study_act_burnout/03_deliverables/stage_06_hypothesis_1/06_hypothesis_1.json",
                    "sha256": "1566197905886a890378220ad078003a5848aae3d77cb49da330fc614caff3da",
                    "type": "json"
                }
            ],
            "validation_status": {
                "verdict": "PASS",
                "report_id": "VAL-20260918-001",
                "checks_passed": 12,
                "checks_failed": 0
            }
        }
        res = validate_experience(valid_exp)
        self.assertTrue(res["valid"], f"Valid experience failed: {res.get('errors')}")

        # Invalid: missing outcome
        invalid_exp = dict(valid_exp)
        del invalid_exp["outcome"]
        res_inv = validate_experience(invalid_exp)
        self.assertFalse(res_inv["valid"])

    def test_03_trajectory_contract_forbids_chain_of_thought(self):
        """Trajectory schema strictly forbids private model chain-of-thought and validates observable actions."""
        valid_trj = {
            "contract_version": "1.0.0",
            "trajectory_id": "TRJ-2026-CH4-001",
            "experience_id": "EXP-2026-CH4-001",
            "project_id": "study_act_burnout",
            "task_id": "stage_06_hypothesis_1",
            "ordered_actions": [
                {
                    "step_number": 1,
                    "action_type": "SKILL_INVOCATION",
                    "actor": "statistics-agent",
                    "timestamp": "2026-09-18T10:00:05Z",
                    "description": "Executed mediation bootstrap script with 5,000 resamples",
                    "observable_input": {"model": 4, "bootstrap": 5000},
                    "observable_output": {"indirect_effect": 0.34, "p_value": 0.002}
                }
            ],
            "tool_usages": [
                {
                    "tool_name": "run_command",
                    "invocation_index": 1,
                    "arguments_summary": {"command": "python3 run_mediation.py"},
                    "status": "SUCCESS",
                    "execution_time_ms": 1250.0
                }
            ],
            "skill_activations": [
                {
                    "skill_name": "mediation",
                    "script_path": ".agents/skills/mediation/scripts/run_mediation.py",
                    "cli_command": "python3 run_mediation.py --spec spec.json",
                    "exit_code": 0,
                    "duration_seconds": 1.25
                }
            ],
            "subagent_delegations": [
                {
                    "delegator": "academic-orchestrator",
                    "delegatee": "statistics-agent",
                    "stage_id": "stage_06_hypothesis_1",
                    "envelope_summary": "Perform bootstrap mediation on ACT dataset",
                    "status": "COMPLETED",
                    "handoff_artifact_path": "projects/study_act_burnout/handoff.json"
                }
            ],
            "important_decisions": [
                {
                    "decision_id": "DEC-001",
                    "decision_type": "statistical_estimator",
                    "selected_option": "Percentile Bootstrap 5,000",
                    "rationale": "Robust against non-normal ab indirect product distribution",
                    "alternatives_considered": [
                        {"option": "Sobel Normal Z Test", "verdict": "REJECTED", "reason": "Low power"}
                    ]
                }
            ],
            "outputs": [
                {
                    "path": "projects/study_act_burnout/outputs/mediation.json",
                    "sha256": "1566197905886a890378220ad078003a5848aae3d77cb49da330fc614caff3da",
                    "type": "json"
                }
            ],
            "validation_events": [
                {
                    "validator_name": "run_all_validators",
                    "verdict": "PASS",
                    "failed_checks": [],
                    "evidence_summary": {"checks_passed": 10, "checks_failed": 0}
                }
            ],
            "feedback": ["FDB-001"],
            "outcome": "SUCCESS"
        }
        res = validate_trajectory(valid_trj)
        self.assertTrue(res["valid"], f"Valid trajectory failed: {res.get('errors')}")

        # Violation: trajectory containing private chain_of_thought must FAIL
        forbidden_trj = dict(valid_trj)
        forbidden_trj["chain_of_thought"] = "The agent thought about whether to use Sobel test..."
        res_forbid = validate_trajectory(forbidden_trj)
        self.assertFalse(res_forbid["valid"], "Trajectory with chain_of_thought must fail schema validation")

        # Violation: trajectory containing thinking must FAIL
        forbidden_trj2 = dict(valid_trj)
        forbidden_trj2["thinking"] = "Internal model reasoning tokens..."
        res_forbid2 = validate_trajectory(forbidden_trj2)
        self.assertFalse(res_forbid2["valid"], "Trajectory with thinking must fail schema validation")

    def test_04_feedback_contract_valid_and_invalid(self):
        """Feedback contract must validate human and automated feedback records."""
        valid_fdb = {
            "contract_version": "1.0.0",
            "feedback_id": "FDB-2026-CH4-001",
            "source": {
                "origin": "ADMIN_DESK_124911145",
                "identifier": "Saber Ghaderi"
            },
            "type": "STATISTICAL_CORRECTION",
            "target_agent": "statistics-agent",
            "target_skill": "assumption-testing",
            "capability": "assumption-testing",
            "task": "M5_PARAMETRIC_ASSUMPTIONS",
            "stage": "03_parametric_assumptions",
            "correction": "Pre-test group variance difference indicated non-parallel regression slopes.",
            "desired_behavior": "Prepare Johnson-Neyman floodlight probing contingency alongside ANCOVA.",
            "scope": "DOMAIN_WIDE",
            "severity": "HIGH",
            "timestamp": "2026-09-18T10:30:00Z",
            "context": {
                "project_id": "study_act_burnout",
                "milestone_id": "M5_PARAMETRIC_ASSUMPTIONS",
                "stage_id": "03_parametric_assumptions"
            }
        }
        res = validate_feedback(valid_fdb)
        self.assertTrue(res["valid"], f"Valid feedback failed: {res.get('errors')}")

    def test_05_lesson_contract_scope_and_inactive_by_default(self):
        """Lesson schema allows lessons to exist without active behavior and distinguishes project scope."""
        valid_lesson = {
            "contract_version": "1.0.0",
            "lesson_id": "LSN-2026-CH4-001",
            "source_experience_id": "EXP-2026-CH4-001",
            "observed_failure": {
                "defect_type": "REPORTING_OR_TYPOGRAPHY_DEFECT",
                "description": "Missing leading zero in Persian narrative: .041 was written instead of ۰.۰۴۱.",
                "failing_artifact_path": "projects/study/06_hypothesis_1.md"
            },
            "desired_behavior": "Always preserve leading zero in Persian text (۰.۰۴۱) per Directive 4.",
            "generalization": "In all Persian academic documents, numbers between 0 and 1 must maintain leading zero.",
            "scope": "CROSS_PROJECT_UNIVERSAL",
            "confidence": 0.99,
            "evidence": {
                "metric_or_check": "CHK-APA-LEADING-ZERO",
                "observed_value": ".041",
                "threshold_value": "۰.۰۴۱"
            },
            "related_skills": ["apa-reporting", "chapter-4-writing"],
            "is_active_behavior": False,  # Exists without becoming active behavior
            "status": "VALIDATED",
            "created_at": "2026-09-18T11:00:00Z",
            "derived_by": "results-auditor"
        }
        res = validate_lesson(valid_lesson)
        self.assertTrue(res["valid"], f"Valid lesson failed: {res.get('errors')}")

        # Distinguish PROJECT_SPECIFIC scope
        proj_lesson = dict(valid_lesson)
        proj_lesson["scope"] = "PROJECT_SPECIFIC"
        res_proj = validate_lesson(proj_lesson)
        self.assertTrue(res_proj["valid"], f"Project-specific lesson failed: {res_proj.get('errors')}")

    def test_06_knowledge_item_contract(self):
        """KnowledgeItem contract captures domain rules, applicability criteria, and exclusions."""
        valid_knw = {
            "contract_version": "1.0.0",
            "knowledge_id": "KNW-STAT-ANCOVA-SLOPE-001",
            "statement": "When homogeneity of regression slopes is violated (Group x Pretest p < .05), standard ANCOVA is invalid and Johnson-Neyman floodlight probing must be used.",
            "scope": "EXPERIMENTAL_DESIGN",
            "applicability": {
                "criteria": ["pre_post_control design", "baseline covariate measured", "slope interaction p < .05"],
                "target_skills": ["assumption-testing", "statistical-data-analyst"],
                "target_designs": ["quasi_experimental"]
            },
            "exclusions": ["designs without continuous pretest", "unrelated repeated measures without covariates"],
            "source_lessons": ["LSN-2026-CH4-001"],
            "supporting_evaluations": ["EVAL-001"],
            "contradictions": [
                {
                    "competing_approach": "Ignore slope violation and report standard ANCOVA F-test anyway",
                    "rejection_rationale": "Inflates Type I error and produces biased group difference estimates."
                }
            ],
            "status": "ACCEPTED_ACTIVE",
            "version": "1.0.0",
            "updated_at": "2026-09-18T11:15:00Z",
            "curated_by": "digital-saber"
        }
        res = validate_knowledge_item(valid_knw)
        self.assertTrue(res["valid"], f"Valid knowledge item failed: {res.get('errors')}")

    def test_07_exemplar_and_anti_pattern_contracts(self):
        """Exemplar and AntiPattern contracts validate gold standards and failure anti-patterns."""
        valid_exm = {
            "contract_version": "1.0.0",
            "exemplar_id": "EXM-SEM-LAVAAN-001",
            "domain": "sem",
            "task_type": "macro_model_estimation",
            "input_specification": {
                "dataset_description": "Cleaned psychological burnout dataset N=120",
                "sample_size": 120,
                "variables": ["emotional_exhaustion", "depersonalization", "personal_accomplishment"]
            },
            "gold_standard_artifacts": [
                {
                    "path": "evals/sem/gold_sem.json",
                    "sha256": "1566197905886a890378220ad078003a5848aae3d77cb49da330fc614caff3da",
                    "format": "json"
                }
            ],
            "why_exemplary": "Satisfies all 11 Hu & Bentler fit cutoffs, reports decoupled LTR parameters, and includes bootstrap BCa intervals.",
            "created_at": "2026-09-18T11:30:00Z"
        }
        res_exm = validate_exemplar(valid_exm)
        self.assertTrue(res_exm["valid"], f"Valid exemplar failed: {res_exm.get('errors')}")

        valid_ap = {
            "contract_version": "1.0.0",
            "anti_pattern_id": "AP-STAT-MEDIAN-SPLIT-001",
            "category": "statistical",
            "defective_pattern": "Dichotomizing continuous moderator into High/Low groups via median split followed by 2x2 ANOVA.",
            "why_defective": "Discards 35-50% statistical power, inflates spurious significance, and creates artificial group boundaries.",
            "observed_symptoms": ["Median split performed on Likert total", "Loss of statistical power"],
            "corrective_remedy": "Continuous moderation interaction analysis using Hayes PROCESS Model 1 with mean-centering.",
            "detection_heuristic": {
                "trigger_rule": "Look for median split or dichotomized moderator variables in regression analysis."
            },
            "reusable": True,
            "updated_at": "2026-09-18T11:45:00Z"
        }
        res_ap = validate_anti_pattern(valid_ap)
        self.assertTrue(res_ap["valid"], f"Valid anti-pattern failed: {res_ap.get('errors')}")

    def test_08_skill_memory_record_and_capability_profile(self):
        """SkillMemoryRecord and CapabilityProfile validate telemetry and operational bounds."""
        valid_smr = {
            "contract_version": "1.0.0",
            "record_id": "SMR-SKILL-SEM-001",
            "skill_name": "sem",
            "total_invocations": 45,
            "success_count": 42,
            "failure_count": 3,
            "average_duration_seconds": 3.4,
            "common_failure_modes": [
                {
                    "failure_type": "NON_POSITIVE_DEFINITE_COVARIANCE",
                    "frequency": 2,
                    "typical_remedy": "Check for extreme multicollinearity or remove negative error variance item"
                }
            ],
            "calibrated_parameter_defaults": {"bootstrap_resamples": 5000, "estimator": "MLR"},
            "last_evaluated_at": "2026-09-18T12:00:00Z"
        }
        res_smr = validate_skill_memory_record(valid_smr)
        self.assertTrue(res_smr["valid"], f"Valid skill memory record failed: {res_smr.get('errors')}")

        valid_cap = {
            "contract_version": "1.0.0",
            "profile_id": "CAP-SEM-001",
            "capability_key": "sem",
            "primary_agent": "statistics-agent",
            "primary_skill": "sem",
            "proficiency_level": "DEFENSE_READY",
            "benchmarked_accuracy": {
                "test_pass_rate": 0.98,
                "total_benchmarks_evaluated": 50,
                "mean_error_margin": 0.001
            },
            "known_limitations": ["Degrades when N < 100 with 4+ latent factors"],
            "supported_topologies": ["Recursive path models", "Multi-group latent structural models"],
            "last_profiled_at": "2026-09-18T12:15:00Z"
        }
        res_cap = validate_capability_profile(valid_cap)
        self.assertTrue(res_cap["valid"], f"Valid capability profile failed: {res_cap.get('errors')}")

    def test_09_improvement_candidate_contract(self):
        """ImprovementCandidate validates staged mutations, diffs, and target components."""
        valid_cand = {
            "contract_version": "1.0.0",
            "candidate_id": "CAND-2026-CH4-TYPO-001",
            "target_component": ".agents/skills/apa-reporting/scripts/generate_apa_tables.py",
            "target_type": "SKILL_DETERMINISTIC_SCRIPT",
            "parent_version": "git-commit-c5bdb92",
            "mutation": {
                "diff_type": "UNIFIED_DIFF",
                "content": "--- a/table.py\n+++ b/table.py\n@@ -10 +10 @@\n-val_str = f'{val:.3f}'\n+val_str = f'0{val:.3f}' if 0 < val < 1 else f'{val:.3f}'",
                "checksum_sha256": "1566197905886a890378220ad078003a5848aae3d77cb49da330fc614caff3da"
            },
            "rationale": "Automates Persian leading zero insertion in decimal formatting logic to eliminate Directive 4 failures.",
            "expected_improvement": {
                "target_metric": "persian_leading_zero_violations",
                "baseline_value": 4,
                "projected_value": 0,
                "qualitative_outcome": "Zero leading zero violations across Chapter 4 tables."
            },
            "affected_capabilities": ["apa_reporting", "chapter_4_writing"],
            "author_agent": "results-auditor",
            "status": "STAGED",
            "staged_at": "2026-09-18T12:30:00Z"
        }
        res_cand = validate_improvement_candidate(valid_cand)
        self.assertTrue(res_cand["valid"], f"Valid improvement candidate failed: {res_cand.get('errors')}")

    def test_10_evaluation_case_and_result_multidimensional_metrics(self):
        """EvaluationCase and EvaluationResult preserve multidimensional metrics and forbid scalar intelligence scores."""
        valid_case = {
            "contract_version": "1.0.0",
            "case_id": "EVAL-CASE-REG-001",
            "capability": "regression",
            "task": {
                "prompt": "Run hierarchical multiple regression predicting post-test burnout",
                "research_question": "Does ACT predict burnout after controlling for age?"
            },
            "inputs": {
                "dataset_path": "evals/regression/data.xlsx",
                "dataset_sha256": "1566197905886a890378220ad078003a5848aae3d77cb49da330fc614caff3da"
            },
            "expected_properties": {
                "required_metrics": {"r2_change_min": 0.15, "df_error": 58},
                "required_artifacts": ["results.json", "table.docx"]
            },
            "forbidden_behaviors": ["p = .000", "missing leading zeros", "stepwise variable selection"],
            "evaluation_method": {
                "runner_type": "DETERMINISTIC_SCRIPT",
                "runner_script": "evals/regression/run_eval.py"
            },
            "created_at": "2026-09-18T12:45:00Z"
        }
        res_case = validate_evaluation_case(valid_case)
        self.assertTrue(res_case["valid"], f"Valid evaluation case failed: {res_case.get('errors')}")

        valid_result = {
            "contract_version": "1.0.0",
            "evaluation_id": "EVR-2026-001",
            "candidate_id": "CAND-2026-CH4-TYPO-001",
            "baseline_version": "git-commit-c5bdb92",
            "metrics": {
                "statistical_precision": {
                    "df_concordance_rate": 1.0,
                    "fit_index_pass_rate": 1.0,
                    "parameter_error_margin": 0.0
                },
                "typography_compliance": {
                    "persian_leading_zero_violations": 0,
                    "apa_table_border_violations": 0,
                    "prohibited_cliche_count": 0
                },
                "execution_reliability": {
                    "successful_runs": 20,
                    "total_runs": 20,
                    "crash_count": 0,
                    "average_latency_seconds": 1.1
                },
                "msai_anomaly_score": 12.5
            },
            "diagnostics": [
                {"check_id": "CHK-LEADING-ZERO", "status": "PASS", "finding": "All Persian numbers have leading zero."}
            ],
            "regressions": {
                "count": 0,
                "details": []
            },
            "failures": [],
            "evidence": [
                {
                    "artifact_path": "evals/results/report_001.json",
                    "sha256": "1566197905886a890378220ad078003a5848aae3d77cb49da330fc614caff3da"
                }
            ],
            "overall_verdict": "PASS",
            "evaluated_at": "2026-09-18T13:00:00Z"
        }
        res_res = validate_evaluation_result(valid_result)
        self.assertTrue(res_res["valid"], f"Valid evaluation result failed: {res_res.get('errors')}")

        # Violation: Scalar intelligence score must FAIL
        forbidden_result = dict(valid_result)
        forbidden_result["overall_intelligence"] = 94.5
        res_forbid = validate_evaluation_result(forbidden_result)
        self.assertFalse(res_forbid["valid"], "Evaluation result with overall_intelligence must fail schema validation")

    def test_11_promotion_decision_gate_enforcement(self):
        """PromotionDecision structurally forbids promotion without passing evaluation evidence, zero regressions, and approval."""
        # Valid PROMOTED decision satisfying all gates
        valid_promoted = {
            "contract_version": "1.0.0",
            "promotion_id": "PRM-2026-001",
            "candidate": {
                "candidate_id": "CAND-2026-CH4-TYPO-001",
                "target_component": ".agents/skills/apa-reporting/scripts/generate_apa_tables.py",
                "target_type": "SKILL_DETERMINISTIC_SCRIPT",
                "checksum_sha256": "1566197905886a890378220ad078003a5848aae3d77cb49da330fc614caff3da"
            },
            "baseline": {
                "version_identifier": "git-commit-c5bdb92",
                "active_component_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            },
            "evaluation_evidence": {
                "evaluation_id": "EVR-2026-001",
                "report_path": "evals/results/report_001.json",
                "report_sha256": "1566197905886a890378220ad078003a5848aae3d77cb49da330fc614caff3da",
                "verdict": "PASS"
            },
            "regression_result": {
                "total_cases_evaluated": 50,
                "regressions_count": 0,
                "zero_regressions_verified": True
            },
            "held_out_result": {
                "dataset_identifier": "held_out_study_act_panel",
                "verdict": "PASS"
            },
            "adversarial_result": {
                "auditor_agent": "academic-challenger",
                "verdict": "PASS",
                "vulnerability_score": "NONE",
                "critique_summary": "Zero side-effects or regressions detected."
            },
            "decision": "PROMOTED",
            "rationale": "All 50 benchmark cases passed with zero regressions. Persian leading zero error completely resolved.",
            "approver": {
                "identity": "Saber Ghaderi (Admin Desk 124911145)",
                "approval_contract_id": "APPR-20260918-001",
                "approved_at": "2026-09-18T13:30:00Z"
            },
            "rollback_snapshot": {
                "snapshot_path": "evolution/promotions/snapshots/snap_20260918.tar.gz",
                "snapshot_sha256": "1566197905886a890378220ad078003a5848aae3d77cb49da330fc614caff3da"
            },
            "timestamp": "2026-09-18T13:30:00Z"
        }
        res_prom = validate_promotion_decision(valid_promoted)
        self.assertTrue(res_prom["valid"], f"Valid promotion decision failed: {res_prom.get('errors')}")

        # Gate Violation 1: PROMOTED with failing evaluation verdict must FAIL
        inv_prom_verdict = json.loads(json.dumps(valid_promoted))
        inv_prom_verdict["evaluation_evidence"]["verdict"] = "FAIL"
        res_gate1 = validate_promotion_decision(inv_prom_verdict)
        self.assertFalse(res_gate1["valid"], "Promotion with failing evaluation must fail")

        # Gate Violation 2: PROMOTED with regressions_count > 0 must FAIL
        inv_prom_reg = json.loads(json.dumps(valid_promoted))
        inv_prom_reg["regression_result"]["regressions_count"] = 2
        inv_prom_reg["regression_result"]["zero_regressions_verified"] = False
        res_gate2 = validate_promotion_decision(inv_prom_reg)
        self.assertFalse(res_gate2["valid"], "Promotion with regressions must fail")

        # Gate Violation 3: PROMOTED with failing adversarial result must FAIL
        inv_prom_adv = json.loads(json.dumps(valid_promoted))
        inv_prom_adv["adversarial_result"]["verdict"] = "FAIL"
        res_gate3 = validate_promotion_decision(inv_prom_adv)
        self.assertFalse(res_gate3["valid"], "Promotion with failing adversarial red-team must fail")

        # Gate Violation 4: PROMOTED without approver must FAIL
        inv_prom_appr = json.loads(json.dumps(valid_promoted))
        del inv_prom_appr["approver"]
        res_gate4 = validate_promotion_decision(inv_prom_appr)
        self.assertFalse(res_gate4["valid"], "Promotion without approver must fail")

        # Valid REJECTED decision without approver/snapshot passes (gate applies only to PROMOTED)
        valid_rejected = json.loads(json.dumps(valid_promoted))
        valid_rejected["decision"] = "REJECTED"
        valid_rejected["rationale"] = "Rejected due to experimental instability."
        del valid_rejected["approver"]
        del valid_rejected["rollback_snapshot"]
        valid_rejected["regression_result"]["regressions_count"] = 3
        valid_rejected["evaluation_evidence"]["verdict"] = "FAIL"
        res_rej = validate_promotion_decision(valid_rejected)
        self.assertTrue(res_rej["valid"], f"Valid rejection decision failed: {res_rej.get('errors')}")

    def test_12_curriculum_task_contract(self):
        """CurriculumTask validates progressive training tasks across graduated complexity levels."""
        valid_cur = {
            "contract_version": "1.0.0",
            "task_id": "CUR-L2-ANCOVA-001",
            "curriculum_phase": "PARAMETRIC_ASSUMPTIONS",
            "difficulty_level": "L2_INTERDEPENDENT_MODELS",
            "task_prompt": "Evaluate pre-post burnout difference between ACT and control groups, test regression slope homogeneity, and select optimal model.",
            "required_datasets": [
                {
                    "dataset_path": "evals/curriculum/data_l2_ancova.xlsx",
                    "sha256": "1566197905886a890378220ad078003a5848aae3d77cb49da330fc614caff3da",
                    "format": "xlsx"
                }
            ],
            "success_criteria": [
                {
                    "criterion_id": "CRIT-01",
                    "description": "Must test Levene and regression slope homogeneity before modeling.",
                    "evaluator_check": "CHK-HOMOGENEITY-SLOPES"
                }
            ],
            "prerequisites": ["CUR-L1-DESCRIPTIVES-001"],
            "created_at": "2026-09-18T14:00:00Z"
        }
        res_cur = validate_curriculum_task(valid_cur)
        self.assertTrue(res_cur["valid"], f"Valid curriculum task failed: {res_cur.get('errors')}")


if __name__ == "__main__":
    import json
    unittest.main()
