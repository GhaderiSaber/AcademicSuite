#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_automatic_experience_capture.py — Comprehensive Unit Tests for Automatic Experience Capture

Validates:
1. Successful task automatically creates structured experience and trajectory.
2. Failed task automatically creates structured experience with FAILURE outcome.
3. User rejection/correction automatically creates feedback contract and links to trajectory.
4. Approval with supervisor stipulations creates feedback contract.
5. Physical stage directory capture with triad artifacts (.docx, .md, .json).
6. Zero private chain-of-thought enforcement (rejects thinking / reasoning tokens).
7. Process restart survivability: persistent experience and trajectory records survive across process restarts.
8. Artifact SHA-256 integrity and contract schema validity across all generated files.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest

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

from scripts.academic_state_manager import (
    StrictStateMachine,
    MilestoneState,
)
from scripts.academic_experience_recorder import (
    AcademicExperienceRecorder,
    ExperienceRecordingError,
    PrivateChainOfThoughtLeakError,
    compute_file_sha256,
)
from contracts.contract_validator import (
    validate_experience,
    validate_trajectory,
    validate_feedback,
)


class TestAutomaticExperienceCapture(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="academic_exp_test_")
        self.state_dir = os.path.join(self.temp_dir, "state")
        self.learning_dir = os.path.join(self.temp_dir, "learning", "experience")
        self.recorder = AcademicExperienceRecorder(
            store_dir=self.learning_dir,
            project_root=self.temp_dir
        )
        self.sm = StrictStateMachine(state_dir=self.state_dir, project_id="test_exp_proj_001")
        # Direct state machine to use our test learning store
        self.sm.experience_recorder = self.recorder

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _create_mock_triad(self, stage_dir: str, prefix: str):
        """Creates a mock synchronized triad: .docx, .md, and .json."""
        os.makedirs(stage_dir, exist_ok=True)
        docx_p = os.path.join(stage_dir, f"{prefix}.docx")
        md_p = os.path.join(stage_dir, f"{prefix}.md")
        json_p = os.path.join(stage_dir, f"{prefix}.json")

        with open(docx_p, "wb") as f:
            f.write(b"MOCK_DOCX_STREAM_12345")
        with open(md_p, "w", encoding="utf-8") as f:
            f.write(f"# Stage {prefix}\n\nScholarly APA 7 findings narrative.\n")
        with open(json_p, "w", encoding="utf-8") as f:
            json.dump({"stage": prefix, "n": 250, "p_value": 0.001}, f)

        return docx_p, md_p, json_p

    def test_01_successful_task_auto_capture(self):
        """A successfully approved milestone automatically produces valid experience & trajectory records."""
        # 1. Setup milestone and required output artifact
        self.sm.register_milestone(
            "M_SUCCESS_TASK",
            "Demographic Analysis Task",
            current_stage="01_demographics",
            required_output_artifacts=["demographics_table.docx"],
            active_agent="data-agent"
        )
        # Create output artifact on disk
        art_path = os.path.join(self.state_dir, "demographics_table.docx")
        with open(art_path, "wb") as f:
            f.write(b"MOCK_DEMOGRAPHICS_DOCX")

        # Create passing validation report
        val_rep = os.path.join(self.state_dir, "validation_report.json")
        with open(val_rep, "w", encoding="utf-8") as f:
            json.dump({
                "report_id": "VAL-DEMO-001",
                "overall_verdict": "PASS",
                "checks_passed": 5,
                "checks_failed": 0,
                "validator_name": "DemographicsValidator"
            }, f)

        # Transition lifecycle
        self.sm.transition_milestone("M_SUCCESS_TASK", MilestoneState.SCOPED)
        self.sm.transition_milestone("M_SUCCESS_TASK", MilestoneState.PLANNED)
        self.sm.transition_milestone("M_SUCCESS_TASK", MilestoneState.READY)
        self.sm.transition_milestone("M_SUCCESS_TASK", MilestoneState.RUNNING)
        self.sm.transition_milestone("M_SUCCESS_TASK", MilestoneState.VALIDATING)
        self.sm.transition_milestone("M_SUCCESS_TASK", MilestoneState.AWAITING_APPROVAL)

        # Request & grant approval
        appr = self.sm.request_approval("M_SUCCESS_TASK", "data_curation", "data-agent", "Ready for approval")
        self.sm.grant_approval(appr["approval_id"], "GhaderiSaber", "ACK-SIGNATURE-001", comments="Approved without issues.")

        # Transition to APPROVED -> triggers automatic experience capture
        res = self.sm.transition_milestone("M_SUCCESS_TASK", MilestoneState.APPROVED)
        self.assertEqual(res["to_state"], MilestoneState.APPROVED.value)

        # Check learning store
        experiences = self.recorder.list_experiences(project_id="test_exp_proj_001")
        self.assertEqual(len(experiences), 1)
        exp_entry = experiences[0]
        self.assertEqual(exp_entry["outcome"], "SUCCESS")
        self.assertEqual(exp_entry["agent"], "data-agent")
        self.assertEqual(exp_entry["validation_verdict"], "PASS")

        # Inspect disk records
        exp_id = exp_entry["experience_id"]
        exp_data = self.recorder.get_experience(exp_id)
        trj_data = self.recorder.get_trajectory(exp_id)

        # Verify contracts
        val_exp = validate_experience(exp_data)
        self.assertTrue(val_exp["valid"], f"Experience contract error: {val_exp.get('error')}")

        val_trj = validate_trajectory(trj_data)
        self.assertTrue(val_trj["valid"], f"Trajectory contract error: {val_trj.get('error')}")

        self.assertEqual(exp_data["outcome"], "SUCCESS")
        self.assertEqual(trj_data["outcome"], "SUCCESS")
        self.assertGreaterEqual(len(exp_data["artifact_references"]), 1)
        self.assertEqual(exp_data["artifact_references"][0]["path"], "demographics_table.docx")

    def test_02_failed_task_auto_capture(self):
        """A failed milestone execution automatically records structured experience with FAILURE outcome."""
        self.sm.register_milestone(
            "M_FAIL_TASK",
            "SEM Fitting Task",
            current_stage="06_hypothesis_1",
            active_agent="statistics-agent"
        )
        self.sm.transition_milestone("M_FAIL_TASK", MilestoneState.SCOPED)
        self.sm.transition_milestone("M_FAIL_TASK", MilestoneState.PLANNED)
        self.sm.transition_milestone("M_FAIL_TASK", MilestoneState.READY)
        self.sm.transition_milestone("M_FAIL_TASK", MilestoneState.RUNNING)

        # Transition to FAILED directly from RUNNING -> triggers automatic experience capture
        res = self.sm.transition_milestone(
            "M_FAIL_TASK",
            MilestoneState.FAILED,
            actor="statistics-agent",
            rationale="Covariance matrix is non-positive definite; estimator failed to converge."
        )
        self.assertEqual(res["to_state"], MilestoneState.FAILED.value)

        # Check learning store
        experiences = self.recorder.list_experiences(project_id="test_exp_proj_001")
        self.assertEqual(len(experiences), 1)
        exp_entry = experiences[0]
        self.assertEqual(exp_entry["outcome"], "FAILURE")
        self.assertEqual(exp_entry["validation_verdict"], "FAIL")

        exp_data = self.recorder.get_experience(exp_entry["experience_id"])
        trj_data = self.recorder.get_trajectory(exp_entry["experience_id"])

        val_exp = validate_experience(exp_data)
        self.assertTrue(val_exp["valid"], f"Experience contract error: {val_exp.get('error')}")
        val_trj = validate_trajectory(trj_data)
        self.assertTrue(val_trj["valid"], f"Trajectory contract error: {val_trj.get('error')}")

        self.assertEqual(exp_data["outcome"], "FAILURE")
        self.assertEqual(trj_data["outcome"], "FAILURE")

    def test_03_supervisor_rejection_and_feedback_capture(self):
        """A supervisor rejection automatically creates a Feedback contract and records trajectory."""
        self.sm.register_milestone(
            "M_REJECT_TASK",
            "Factor Analysis Task",
            current_stage="05_cfa",
            active_agent="psychometric-expert"
        )
        self.sm.transition_milestone("M_REJECT_TASK", MilestoneState.SCOPED)
        self.sm.transition_milestone("M_REJECT_TASK", MilestoneState.PLANNED)
        self.sm.transition_milestone("M_REJECT_TASK", MilestoneState.READY)
        self.sm.transition_milestone("M_REJECT_TASK", MilestoneState.RUNNING)
        self.sm.transition_milestone("M_REJECT_TASK", MilestoneState.VALIDATING)
        self.sm.transition_milestone("M_REJECT_TASK", MilestoneState.AWAITING_APPROVAL)

        # Request approval
        appr = self.sm.request_approval("M_REJECT_TASK", "statistical_deliberation", "psychometric-expert", "CFA 3-factor model")

        # Supervisor rejects with explicit critique
        rejection_reason = "Factor loadings on item 7 are below 0.30. Re-specify model with cross-loadings or remove item."
        self.sm.reject_approval(appr["approval_id"], approver_identity="GhaderiSaber", comments=rejection_reason)

        # Rejection transitions milestone to REJECTED and triggers experience capture with feedback
        self.assertEqual(self.sm.milestones["M_REJECT_TASK"]["status"], MilestoneState.REJECTED.value)

        experiences = self.recorder.list_experiences(project_id="test_exp_proj_001")
        self.assertEqual(len(experiences), 1)
        exp_entry = experiences[0]
        self.assertTrue(exp_entry["has_feedback"])

        exp_id = exp_entry["experience_id"]
        exp_data = self.recorder.get_experience(exp_id)
        trj_data = self.recorder.get_trajectory(exp_id)
        fdb_data = self.recorder.get_feedback(exp_id)

        self.assertIsNotNone(fdb_data)
        val_fdb = validate_feedback(fdb_data)
        self.assertTrue(val_fdb["valid"], f"Feedback contract error: {val_fdb.get('error')}")

        self.assertEqual(fdb_data["source"]["origin"], "HUMAN_SUPERVISOR")
        self.assertEqual(fdb_data["source"]["identifier"], "GhaderiSaber")
        self.assertEqual(fdb_data["target_agent"], "psychometric-expert")
        self.assertEqual(fdb_data["correction"], rejection_reason)
        self.assertIn(fdb_data["feedback_id"], trj_data["feedback"])

    def test_04_approval_with_stipulations(self):
        """Approval granted with stipulations captures a STIPULATION feedback contract."""
        self.sm.register_milestone(
            "M_STIP_TASK",
            "Regression Modeling",
            current_stage="06_hypothesis_1",
            active_agent="statistics-agent"
        )
        self.sm.transition_milestone("M_STIP_TASK", MilestoneState.SCOPED)
        self.sm.transition_milestone("M_STIP_TASK", MilestoneState.PLANNED)
        self.sm.transition_milestone("M_STIP_TASK", MilestoneState.READY)
        self.sm.transition_milestone("M_STIP_TASK", MilestoneState.RUNNING)
        self.sm.transition_milestone("M_STIP_TASK", MilestoneState.VALIDATING)
        self.sm.transition_milestone("M_STIP_TASK", MilestoneState.AWAITING_APPROVAL)

        appr = self.sm.request_approval("M_STIP_TASK", "hypothesis_testing", "statistics-agent", "Ready")
        self.sm.grant_approval(
            appr["approval_id"],
            approver_identity="AdminDesk_124911145",
            digital_signature="ACK-STIP-001",
            comments="Approved with conditions.",
            stipulations=["Report VIF collinearity diagnostics in Chapter 4 Table 4-3", "Include Cook distance outlier plot"]
        )
        self.sm.transition_milestone("M_STIP_TASK", MilestoneState.APPROVED)

        experiences = self.recorder.list_experiences(project_id="test_exp_proj_001")
        self.assertEqual(len(experiences), 1)
        exp_id = experiences[0]["experience_id"]
        fdb_data = self.recorder.get_feedback(exp_id)
        self.assertIsNotNone(fdb_data)
        self.assertEqual(fdb_data["type"], "STIPULATION")
        self.assertIn("Report VIF", fdb_data["desired_behavior"])

    def test_05_record_from_stage_directory(self):
        """Directly records experience from a physical stage directory with triad artifacts."""
        stage_dir = os.path.join(self.temp_dir, "stages", "01_demographics")
        docx_p, md_p, json_p = self._create_mock_triad(stage_dir, "01_demographics")

        res = self.recorder.record_from_stage(
            stage_dir=stage_dir,
            project_id="test_stage_proj",
            agent="data-agent",
            skill="descriptive-statistics"
        )
        self.assertEqual(res["status"], "RECORDED")
        exp_id = res["experience_id"]

        exp_data = self.recorder.get_experience(exp_id)
        trj_data = self.recorder.get_trajectory(exp_id)

        self.assertEqual(exp_data["outcome"], "SUCCESS")
        self.assertEqual(len(exp_data["artifact_references"]), 3)
        # Verify SHA-256 matches actual files
        for art in exp_data["artifact_references"]:
            disk_p = os.path.join(self.temp_dir, art["path"])
            self.assertEqual(art["sha256"], compute_file_sha256(disk_p))

        val_res = self.recorder.validate_stored_experience(exp_id)
        self.assertTrue(val_res["valid"], f"Validation errors: {val_res.get('errors')}")

    def test_06_zero_private_chain_of_thought_enforcement(self):
        """Recorder strictly rejects trajectories containing private chain-of-thought or reasoning tokens."""
        now_iso = "2026-09-18T18:00:00Z"
        exp_payload = {
            "contract_version": "1.0.0",
            "experience_id": "EXP-COT-TEST-001",
            "project_id": "proj_cot",
            "task_id": "task_cot",
            "agent": "statistics-agent",
            "skill": "sem",
            "start_time": now_iso,
            "end_time": now_iso,
            "outcome": "SUCCESS",
            "artifact_references": [],
            "validation_status": {"verdict": "PASS"}
        }

        # Trajectory with forbidden 'chain_of_thought'
        trj_with_cot = {
            "contract_version": "1.0.0",
            "trajectory_id": "TRJ-COT-TEST-001",
            "experience_id": "EXP-COT-TEST-001",
            "project_id": "proj_cot",
            "ordered_actions": [],
            "tool_usages": [],
            "skill_activations": [],
            "subagent_delegations": [],
            "important_decisions": [],
            "outputs": [],
            "validation_events": [],
            "feedback": [],
            "outcome": "SUCCESS",
            "chain_of_thought": "Thinking about calculating the p-value..."  # FORBIDDEN
        }

        with self.assertRaises(PrivateChainOfThoughtLeakError):
            self.recorder.record_experience(exp_payload, trj_with_cot)

        # Trajectory with nested forbidden 'reasoning_tokens'
        trj_with_tokens = {
            "contract_version": "1.0.0",
            "trajectory_id": "TRJ-COT-TEST-002",
            "experience_id": "EXP-COT-TEST-001",
            "project_id": "proj_cot",
            "ordered_actions": [
                {
                    "step_number": 1,
                    "action_type": "TOOL_CALL",
                    "actor": "statistics-agent",
                    "timestamp": now_iso,
                    "description": "Running calculation",
                    "reasoning_tokens": 512  # FORBIDDEN
                }
            ],
            "tool_usages": [],
            "skill_activations": [],
            "subagent_delegations": [],
            "important_decisions": [],
            "outputs": [],
            "validation_events": [],
            "feedback": [],
            "outcome": "SUCCESS"
        }

        with self.assertRaises(PrivateChainOfThoughtLeakError):
            self.recorder.record_experience(exp_payload, trj_with_tokens)

    def test_07_process_restart_survivability(self):
        """
        Records experiences with recorder A, destroys the instance,
        and instantiates recorder B in a fresh state.
        All records must persist, remain queryable, and validate 100% against schemas.
        """
        # Step 1: Record 3 diverse experiences
        stage_dir = os.path.join(self.temp_dir, "stages", "02_correlation")
        self._create_mock_triad(stage_dir, "02_correlation")
        r1 = self.recorder.record_from_stage(stage_dir, project_id="restart_proj", outcome="SUCCESS")
        r2 = self.recorder.record_from_stage(stage_dir, project_id="restart_proj", outcome="FAILURE")

        # Add milestone experience
        self.sm.register_milestone("M_RESTART_TEST", "Restart Test", current_stage="07_hyp_2", active_agent="statistics-agent")
        self.sm.transition_milestone("M_RESTART_TEST", MilestoneState.SCOPED)
        self.sm.transition_milestone("M_RESTART_TEST", MilestoneState.PLANNED)
        self.sm.transition_milestone("M_RESTART_TEST", MilestoneState.READY)
        self.sm.transition_milestone("M_RESTART_TEST", MilestoneState.RUNNING)
        self.sm.transition_milestone("M_RESTART_TEST", MilestoneState.FAILED, rationale="Convergence failure")

        # Step 2: Destroy existing references
        del self.recorder
        del self.sm

        # Step 3: Instantiate fresh recorder in new process context
        fresh_recorder = AcademicExperienceRecorder(store_dir=self.learning_dir, project_root=self.temp_dir)
        all_stored = fresh_recorder.list_experiences()
        self.assertEqual(len(all_stored), 3)

        # Verify querying by outcome
        success_list = fresh_recorder.list_experiences(outcome="SUCCESS")
        failure_list = fresh_recorder.list_experiences(outcome="FAILURE")
        self.assertEqual(len(success_list), 1)
        self.assertEqual(len(failure_list), 2)

        # Audit all stored experiences against contracts
        audit_rep = fresh_recorder.validate_all_stored()
        self.assertEqual(audit_rep["total_experiences"], 3)
        self.assertEqual(audit_rep["valid_count"], 3)
        self.assertEqual(audit_rep["invalid_count"], 0)


if __name__ == "__main__":
    unittest.main()
