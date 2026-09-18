#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_contracts.py — Comprehensive Unit Tests for AcademicSuite Contract Layer

Validates:
1. All 9 contract schemas exist and compile under JSON Schema Draft 7.
2. AnalysisPlan strictly separates statistical decision from execution specifications.
3. ArtifactManifest correctly captures provenance, hashes, and validation status.
4. Event schema supports all 14 mandatory academic lifecycle events.
5. MilestoneState schema enforces status transitions, active agents, and retry tracking.
6. Approval schema mathematically forbids default-true approval and validates explicit grant conditions.
7. ValidationReport schema distinguishes 5 verdicts and strictly forbids PASS on missing evidence.
8. Handoff schema validates delegation envelopes and artifact transfers.
9. Pitfall schema enforces problem, evidence, resolution, and reusable flags.
10. ExecutionManifest validates deterministic pipeline steps and environments.
"""

import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from contracts.contract_validator import (
    load_schema,
    validate_contract,
    validate_analysis_plan,
    validate_artifact_manifest,
    validate_event,
    validate_milestone_state,
    validate_approval,
    validate_validation_report,
    validate_handoff,
    validate_pitfall,
    validate_execution_manifest,
    SCHEMA_FILES
)


class TestContractSystem(unittest.TestCase):

    def test_01_all_nine_schema_files_exist_and_compile(self):
        """All contract schemas must exist in contracts/ and compile as valid Draft-7 schemas."""
        self.assertGreaterEqual(len(SCHEMA_FILES), 9)
        self.assertIn("teamwork_boundary", SCHEMA_FILES)
        for key, fname in SCHEMA_FILES.items():
            schema = load_schema(key)
            self.assertIsInstance(schema, dict, f"Schema '{key}' is not a valid JSON object.")
            self.assertEqual(schema.get("$schema"), "http://json-schema.org/draft-07/schema#")
            self.assertIn("title", schema)

    def test_02_analysis_plan_contract_decision_vs_execution(self):
        """AnalysisPlan must validate all required decision fields and execution specifications."""
        valid_plan = {
            "contract_version": "1.0.0",
            "plan_id": "PLAN-2026-CH4-001",
            "project_id": "study_act_burnout",
            "created_at": "2026-09-18T07:45:00Z",
            "decided_by": "statistical-expert",
            "research_questions": [
                {
                    "id": "RQ1",
                    "question": "Does ACT reduce burnout after controlling for baseline?",
                    "target_variables": ["group", "burnout_post", "burnout_pre"]
                }
            ],
            "hypotheses": [
                {
                    "id": "H1",
                    "statement": "ACT intervention group shows lower posttest burnout than control.",
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
                    "title": "Descriptive statistics across groups",
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

        res = validate_analysis_plan(valid_plan)
        self.assertTrue(res["valid"], f"Valid analysis plan failed: {res.get('errors')}")

        # Invalid plan: missing execution specification
        invalid_plan = dict(valid_plan)
        del invalid_plan["execution_specification"]
        res_invalid = validate_analysis_plan(invalid_plan)
        self.assertFalse(res_invalid["valid"])
        self.assertTrue(any("execution_specification" in e for e in res_invalid["errors"]))

    def test_03_artifact_manifest_provenance_and_hash(self):
        """ArtifactManifest must enforce provenance, hash algorithm, and validation status."""
        valid_manifest = {
            "contract_version": "1.0.0",
            "artifact_id": "ART-2026-CH4-HYPO1-JSON",
            "milestone": "M4_CHAPTER4",
            "stage_id": "06_hypothesis_1",
            "producer": {
                "agent": "statistics-agent",
                "script_or_generator": "scripts/build_hypothesis_1_triad_docx.py",
                "execution_id": "EXEC-2026-0918-01"
            },
            "consumers": ["academic-writer", "results-auditor", "validation-agent"],
            "type": "stats_json",
            "path": "projects/study_act_burnout/03_deliverables/06_hypothesis_1.json",
            "schema": "contracts/analysis_plan.schema.json",
            "hash": {
                "algorithm": "sha256",
                "value": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
            },
            "creation_timestamp": "2026-09-18T07:45:00Z",
            "validation_status": "VALIDATED_PASS",
            "provenance": {
                "source_dataset": "projects/study_act_burnout/01_raw_inputs/data_cleaned.xlsx",
                "deterministic_tool": "scripts/run_ancova.py",
                "command_line": "python3 scripts/run_ancova.py --data ...",
                "git_commit_hash": "f1015b5"
            },
            "dependencies": [
                {
                    "artifact_id": "ART-2026-CH4-CURATION-XLSX",
                    "path": "projects/study_act_burnout/01_raw_inputs/data_cleaned.xlsx",
                    "hash_at_consumption": "a6b1c..."
                }
            ]
        }
        res = validate_artifact_manifest(valid_manifest)
        self.assertTrue(res["valid"], f"Valid manifest failed: {res.get('errors')}")

        # Invalid manifest: non-ASCII path (Directive 6)
        invalid_manifest = dict(valid_manifest)
        invalid_manifest["path"] = "projects/فصل_چهارم/output.json"
        res_invalid = validate_artifact_manifest(invalid_manifest)
        self.assertFalse(res_invalid["valid"])

    def test_04_event_contract_all_fourteen_events(self):
        """Event schema must validate all 14 required academic lifecycle and milestone events."""
        mandatory_events = [
            "PROJECT_CREATED",
            "MILESTONE_STARTED",
            "PLAN_CREATED",
            "ARTIFACT_CREATED",
            "EXECUTION_STARTED",
            "EXECUTION_COMPLETED",
            "VALIDATION_STARTED",
            "VALIDATION_FAILED",
            "CRITIQUE_CREATED",
            "REVISION_REQUESTED",
            "MILESTONE_APPROVAL_REQUESTED",
            "MILESTONE_APPROVED",
            "MILESTONE_REJECTED",
            "MILESTONE_FAILED"
        ]
        for evt_type in mandatory_events:
            instance = {
                "contract_version": "1.0.0",
                "event_id": f"EVT-TEST-{evt_type}",
                "event_type": evt_type,
                "timestamp": "2026-09-18T07:45:00Z",
                "project_id": "study_act_burnout",
                "emitter_agent": "academic-orchestrator",
                "payload": {
                    "summary": f"Emitted {evt_type} for test suite."
                }
            }
            res = validate_event(instance)
            self.assertTrue(res["valid"], f"Event type '{evt_type}' failed validation: {res.get('errors')}")

        # Invalid event type
        invalid_evt = {
            "contract_version": "1.0.0",
            "event_id": "EVT-INVALID",
            "event_type": "ARBITRARY_UNREGISTERED_EVENT",
            "timestamp": "2026-09-18T07:45:00Z",
            "project_id": "study_test",
            "emitter_agent": "unknown",
            "payload": {"summary": "test"}
        }
        res_inv = validate_event(invalid_evt)
        self.assertFalse(res_inv["valid"])

    def test_05_milestone_state_contract(self):
        """MilestoneState must enforce valid lifecycle statuses, stage sequences, and retry counters."""
        valid_state = {
            "contract_version": "1.0.0",
            "milestone_id": "M4_CHAPTER4",
            "title": "Chapter 4 Empirical Findings",
            "project_id": "study_act_burnout",
            "status": "VALIDATING",
            "current_stage": "06_hypothesis_1",
            "active_agent": "academic-writer",
            "stages_sequence": [
                {
                    "stage_id": "06_hypothesis_1",
                    "title": "Hypothesis 1 Testing",
                    "assigned_role": "academic-writer",
                    "status": "RUNNING",
                    "triad_completed": True
                }
            ],
            "input_artifacts": ["academic-state/analysis/ancova_burnout.json"],
            "produced_artifacts": [
                {
                    "artifact_id": "ART-HYPO1-DOCX",
                    "path": "06_hypothesis_1.docx",
                    "type": "openxml_word",
                    "validation_verdict": "PASS"
                }
            ],
            "validation_summary": {
                "overall_verdict": "PASS",
                "total_checks_run": 12,
                "failed_checks_count": 0
            },
            "approval_state": {
                "status": "APPROVAL_NOT_REQUIRED"
            },
            "timestamps": {
                "created_at": "2026-09-18T07:00:00Z",
                "updated_at": "2026-09-18T07:45:00Z"
            },
            "retry_tracking": {
                "retry_count": 0,
                "max_retries": 2
            }
        }
        res = validate_milestone_state(valid_state)
        self.assertTrue(res["valid"], f"Valid milestone state failed: {res.get('errors')}")

    def test_06_human_approval_contract_invariants(self):
        """Approval schema MUST mathematically prevent default-true approvals and enforce explicit grant constraints."""
        # 1. Valid pending approval (is_approved must be false)
        pending_appr = {
            "contract_version": "1.0.0",
            "approval_id": "APPR-2026-001",
            "milestone_id": "M4_CHAPTER4",
            "category": "final_dissertation_release",
            "requested_by": {
                "agent": "digital-saber",
                "rationale": "Chapter 4 validated; requesting release authorization."
            },
            "requested_at": "2026-09-18T07:45:00Z",
            "status": "PENDING",
            "is_approved": False
        }
        res_pending = validate_approval(pending_appr)
        self.assertTrue(res_pending["valid"], f"Pending approval failed: {res_pending.get('errors')}")

        # 2. INVARIANT VIOLATION: status=PENDING but is_approved=True MUST FAIL at schema level
        corrupt_pending = dict(pending_appr)
        corrupt_pending["is_approved"] = True
        res_corrupt = validate_approval(corrupt_pending)
        self.assertFalse(res_corrupt["valid"], "Schema allowed is_approved=True while status=PENDING!")

        # 3. INVARIANT VIOLATION: status=REJECTED but is_approved=True MUST FAIL at schema level
        corrupt_rejected = dict(pending_appr)
        corrupt_rejected["status"] = "REJECTED"
        corrupt_rejected["is_approved"] = True
        res_corrupt_rej = validate_approval(corrupt_rejected)
        self.assertFalse(res_corrupt_rej["valid"], "Schema allowed is_approved=True while status=REJECTED!")

        # 4. INVARIANT VIOLATION: status=GRANTED but decision block missing MUST FAIL at schema level
        corrupt_granted = dict(pending_appr)
        corrupt_granted["status"] = "GRANTED"
        corrupt_granted["is_approved"] = True
        # missing decision object
        res_no_dec = validate_approval(corrupt_granted)
        self.assertFalse(res_no_dec["valid"], "Schema allowed status=GRANTED without decision payload!")

        # 5. Legitimate affirmative grant with full decision payload
        valid_granted = dict(pending_appr)
        valid_granted["status"] = "GRANTED"
        valid_granted["is_approved"] = True
        valid_granted["decision"] = {
            "approver_identity": "Saber Ghaderi (Admin Desk 124911145)",
            "decided_at": "2026-09-18T07:50:00Z",
            "comments": "Methodology and p-values certified. Release granted.",
            "digital_signature_or_ack": "SG-ADMIN-ACK-984321"
        }
        res_valid_granted = validate_approval(valid_granted)
        self.assertTrue(res_valid_granted["valid"], f"Valid granted approval failed: {res_valid_granted.get('errors')}")

    def test_07_validation_report_contract_invariants(self):
        """ValidationReport must support 5 verdicts and FORBID PASS verdict when evidence is missing."""
        # 1. Valid PASS with affirmative evidence
        valid_pass = {
            "contract_version": "1.0.0",
            "report_id": "VAL-2026-CH4-001",
            "validator_name": "run_all_validators",
            "target_artifacts": ["06_hypothesis_1.docx", "06_hypothesis_1.json"],
            "timestamp": "2026-09-18T07:45:00Z",
            "overall_verdict": "PASS",
            "evidence_summary": {
                "total_evidence_items_evaluated": 15,
                "total_checks_run": 5,
                "checks_passed": 5,
                "checks_failed": 0
            },
            "results": [
                {
                    "check_id": "CHK-APA-01",
                    "rule": "Persian leading zero retention (۰.۰۵)",
                    "verdict": "PASS",
                    "evidence": {
                        "instances_checked": 12,
                        "violations_found": 0,
                        "sample_verified": "p < ۰.۰۰۱"
                    }
                }
            ]
        }
        res_pass = validate_validation_report(valid_pass)
        self.assertTrue(res_pass["valid"], f"Valid PASS report failed: {res_pass.get('errors')}")

        # 2. INVARIANT VIOLATION: overall_verdict=PASS with 0 evidence evaluated MUST FAIL at schema level
        fail_open_pass = dict(valid_pass)
        fail_open_pass["evidence_summary"] = {
            "total_evidence_items_evaluated": 0,  # Zero evidence!
            "total_checks_run": 0,
            "checks_passed": 0,
            "checks_failed": 0
        }
        res_fail_open = validate_validation_report(fail_open_pass)
        self.assertFalse(res_fail_open["valid"], "Schema allowed overall_verdict=PASS with 0 evidence items evaluated!")

        # 3. All 5 distinct verdicts supported
        all_verdicts = ["PASS", "FAIL", "BLOCKED", "INCOMPLETE", "UNKNOWN"]
        for v in all_verdicts:
            rep = {
                "contract_version": "1.0.0",
                "report_id": f"VAL-TEST-{v}",
                "validator_name": "test_validator",
                "target_artifacts": ["artifact.json"],
                "timestamp": "2026-09-18T07:45:00Z",
                "overall_verdict": v,
                "evidence_summary": {
                    "total_evidence_items_evaluated": 10 if v == "PASS" else 0,
                    "total_checks_run": 1 if v == "PASS" else 0,
                    "checks_passed": 1 if v == "PASS" else 0,
                    "checks_failed": 0
                },
                "results": [
                    {
                        "check_id": "CHK-01",
                        "rule": "test rule",
                        "verdict": v,
                        "evidence": {"checked": True}
                    }
                ]
            }
            res_v = validate_validation_report(rep)
            self.assertTrue(res_v["valid"], f"Verdict '{v}' failed validation: {res_v.get('errors')}")

    def test_08_handoff_contract(self):
        """Handoff schema must validate delegation envelopes, input/output artifacts, and completion criteria."""
        valid_handoff = {
            "contract_version": "1.0.0",
            "handoff_id": "HND-2026-CH4-001",
            "milestone_id": "M4_CHAPTER4",
            "stage_id": "06_hypothesis_1",
            "source_agent": "statistical-expert",
            "target_agent": "statistics-agent",
            "timestamp": "2026-09-18T07:45:00Z",
            "delegation_envelope": {
                "task_summary": "Execute ANCOVA on job burnout using cleaned baseline dataset.",
                "prompt_instructions": "Run scripts/run_ancova.py with specified parameters.",
                "context_bounds": {
                    "allowed_tools": ["run_command", "view_file", "write_to_file"],
                    "workspace_mode": "inherit",
                    "model_tier": "flash"
                }
            },
            "input_artifacts": [
                {
                    "artifact_id": "ART-CLEANED-DATA",
                    "path": "data_cleaned.xlsx",
                    "validation_status": "VALIDATED_PASS"
                }
            ],
            "expected_outputs": {
                "triad_required": True,
                "expected_files": ["06_hypothesis_1.docx", "06_hypothesis_1.md", "06_hypothesis_1.json"]
            },
            "completion_criteria": [
                "ANCOVA model converged with zero matrix collinearity errors.",
                "Synchronized triad (.docx, .md, .json) produced on disk.",
                "Deterministic validation returns overall_verdict PASS."
            ]
        }
        res = validate_handoff(valid_handoff)
        self.assertTrue(res["valid"], f"Valid handoff failed: {res.get('errors')}")

    def test_09_pitfall_contract(self):
        """Pitfall schema must enforce candidate approach, problem, evidence, resolution, and reusable flag."""
        valid_pitfall = {
            "contract_version": "1.0.0",
            "pitfall_id": "PIT-2026-ANCOVA-001",
            "stage": "03_parametric_assumptions",
            "candidate_approach": "Standard one-way ANCOVA assuming homogeneous regression slopes.",
            "problem": "Homogeneity of regression slopes violated (interaction group * covariate p = .021).",
            "evidence": {
                "description": "F-test on group-by-covariate interaction was statistically significant.",
                "metric_or_statistic": "F(1, 56)",
                "observed_value": 5.62,
                "threshold_value": "p > .05"
            },
            "detected_by": "statistical-auditor",
            "resolution": {
                "corrective_action": "Switch to Johnson-Neyman technique to identify regions of significance.",
                "adapted_approach": "Moderation analysis using PROCESS Model 1 centered covariates.",
                "verification_check": "verify_assumptions.py returned PASS on JN boundaries."
            },
            "reusable": True
        }
        res = validate_pitfall(valid_pitfall)
        self.assertTrue(res["valid"], f"Valid pitfall failed: {res.get('errors')}")

    def test_10_execution_manifest_contract(self):
        """ExecutionManifest must validate pipeline steps, assigned subagents, and dry_run flag."""
        valid_manifest = {
            "contract_version": "1.0.0",
            "manifest_id": "MANIFEST-2026-CH4-BURNOUT",
            "project_id": "study_act_burnout",
            "milestone_id": "M4_CHAPTER4",
            "generated_by": "academic-orchestrator",
            "execution_environment": {
                "working_directory": "/home/ghaderi-saber/Desktop/AcademicSuite/projects/study_act_burnout",
                "python_interpreter": "python3"
            },
            "dry_run": False,
            "steps": [
                {
                    "step_number": 1,
                    "stage_id": "06_hypothesis_1",
                    "capability": "statistical_hypothesis_testing",
                    "assigned_subagent": "statistics-agent",
                    "skill_name": "statistical-data-analyst",
                    "script_path": "02_analysis_code/build_chapter_4_docx.py",
                    "input_artifacts": ["01_raw_inputs/data_cleaned.xlsx"],
                    "output_artifacts": ["03_deliverables/06_hypothesis_1.docx"],
                    "timeout_seconds": 60,
                    "required_validation": {
                        "validator_suite_required": True,
                        "validator_script": "validators/run_all_validators.py",
                        "expected_verdict": "PASS"
                    }
                }
            ]
        }
        res = validate_execution_manifest(valid_manifest)
        self.assertTrue(res["valid"], f"Valid execution manifest failed: {res.get('errors')}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
