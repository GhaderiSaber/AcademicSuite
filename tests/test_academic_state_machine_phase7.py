#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_academic_state_machine_phase7.py — Comprehensive Unit Tests for Phase 7 State Machine

Verifies:
1. Legal state transitions for stages:
   STAGE_LOCKED -> STAGE_READY -> STAGE_RUNNING -> STAGE_VALIDATING -> STAGE_AWAITING_APPROVAL -> STAGE_APPROVED
2. Legal recovery transitions:
   STAGE_RUNNING -> STAGE_FAILED -> STAGE_READY
   STAGE_VALIDATING -> STAGE_FAILED -> STAGE_READY
   STAGE_AWAITING_APPROVAL -> STAGE_REJECTED -> STAGE_READY
   STAGE_RUNNING -> STAGE_BLOCKED -> STAGE_READY
3. Illegal transitions fail closed (InvalidStateTransitionError)
4. Prerequisite stage dependency gating (UnmetPrerequisiteError)
5. Artifact existence gating (MissingRequiredArtifactError)
6. Authorization & Validation report gating for STAGE_APPROVED (MissingApprovalError, MilestoneValidationRequiredError)
7. Direct set_stage() mutation strictly blocked in production mode (DirectStageMutationBlockedError)
8. Project-level lifecycle transitions (PROJECT_CREATED -> PROJECT_APPROVED / PROJECT_REJECTED)
9. CLI request-transition subcommand execution
10. Persistence and restart-safety across process lifecycles
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

from scripts.academic_state_manager import (
    StrictStateMachine,
    StageState,
    ProjectState,
    STAGE_LEGAL_TRANSITIONS,
    PROJECT_LEGAL_TRANSITIONS,
    StateManagementError,
    UnknownStateError,
    UnknownStageError,
    UnknownDependencyError,
    UnmetPrerequisiteError,
    InvalidStateTransitionError,
    MissingRequiredArtifactError,
    MissingApprovalError,
    MilestoneValidationRequiredError,
    DirectStageMutationBlockedError,
    init_state,
    set_stage,
    request_transition,
    get_state_dir
)


class TestAcademicStateMachinePhase7(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="phase7_state_test_")
        self.state_dir = os.path.join(self.temp_dir, "academic-state")
        self.sm = StrictStateMachine(state_dir=self.state_dir, project_id="phase7_study")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_stage_happy_path_lifecycle(self):
        """Tests the full happy path lifecycle: LOCKED -> READY -> RUNNING -> VALIDATING -> AWAITING_APPROVAL -> APPROVED."""
        self.sm.register_stage(
            stage_id="01_demographics",
            title="Demographic Profiling",
            initial_status=StageState.STAGE_LOCKED,
            dependencies=[],
            required_input_artifacts=[],
            required_output_artifacts=[],
            requires_validation=False
        )
        self.assertEqual(self.sm.stages["01_demographics"]["status"], StageState.STAGE_LOCKED.value)

        # 1. LOCKED -> READY
        res = self.sm.request_transition("01_demographics", StageState.STAGE_READY, rationale="Prerequisites satisfied")
        self.assertEqual(res["to_state"], StageState.STAGE_READY.value)
        self.assertEqual(self.sm.stages["01_demographics"]["status"], StageState.STAGE_READY.value)

        # 2. READY -> RUNNING
        res = self.sm.request_transition("01_demographics", StageState.STAGE_RUNNING, rationale="Execution started")
        self.assertEqual(res["to_state"], StageState.STAGE_RUNNING.value)

        # 3. RUNNING -> VALIDATING
        res = self.sm.request_transition("01_demographics", StageState.STAGE_VALIDATING, rationale="Execution completed")
        self.assertEqual(res["to_state"], StageState.STAGE_VALIDATING.value)

        # 4. VALIDATING -> AWAITING_APPROVAL
        res = self.sm.request_transition("01_demographics", StageState.STAGE_AWAITING_APPROVAL, rationale="Validation completed")
        self.assertEqual(res["to_state"], StageState.STAGE_AWAITING_APPROVAL.value)

        # 5. Grant human approval
        appr = self.sm.request_approval(
            milestone_id="01_demographics",
            category="demographics",
            requester_agent="data-agent",
            rationale="Demographics report verified"
        )
        self.sm.grant_approval(
            approval_id=appr["approval_id"],
            approver_identity="Saber Admin Desk 124911145",
            digital_signature="SIG-VERIFIED-124911145",
            comments="Approved"
        )

        # 6. AWAITING_APPROVAL -> APPROVED
        res = self.sm.request_transition("01_demographics", StageState.STAGE_APPROVED, rationale="Approval granted")
        self.assertEqual(res["to_state"], StageState.STAGE_APPROVED.value)

        # Verify event log contains events
        events = self.sm.events
        event_types = [e.get("event_type") for e in events]
        self.assertIn("MILESTONE_STARTED", event_types)
        self.assertIn("EXECUTION_STARTED", event_types)
        self.assertIn("VALIDATION_STARTED", event_types)
        self.assertIn("MILESTONE_APPROVED", event_types)

    def test_02_stage_recovery_transitions(self):
        """Tests legal failure and recovery transitions."""
        self.sm.register_stage("02_recovery_test", "Recovery Test", initial_status=StageState.STAGE_READY, requires_validation=False)

        # READY -> RUNNING -> FAILED -> READY
        self.sm.request_transition("02_recovery_test", StageState.STAGE_RUNNING)
        self.sm.request_transition("02_recovery_test", StageState.STAGE_FAILED, rationale="Script syntax error")
        self.assertEqual(self.sm.stages["02_recovery_test"]["status"], StageState.STAGE_FAILED.value)

        self.sm.request_transition("02_recovery_test", StageState.STAGE_READY, rationale="Retry after fix")
        self.assertEqual(self.sm.stages["02_recovery_test"]["status"], StageState.STAGE_READY.value)

        # READY -> RUNNING -> VALIDATING -> FAILED -> READY
        self.sm.request_transition("02_recovery_test", StageState.STAGE_RUNNING)
        self.sm.request_transition("02_recovery_test", StageState.STAGE_VALIDATING)
        self.sm.request_transition("02_recovery_test", StageState.STAGE_FAILED, rationale="Anomaly check failed")
        self.assertEqual(self.sm.stages["02_recovery_test"]["status"], StageState.STAGE_FAILED.value)

        self.sm.request_transition("02_recovery_test", StageState.STAGE_READY, rationale="Re-run")
        self.assertEqual(self.sm.stages["02_recovery_test"]["status"], StageState.STAGE_READY.value)

        # READY -> RUNNING -> VALIDATING -> AWAITING_APPROVAL -> REJECTED -> READY
        self.sm.request_transition("02_recovery_test", StageState.STAGE_RUNNING)
        self.sm.request_transition("02_recovery_test", StageState.STAGE_VALIDATING)
        self.sm.request_transition("02_recovery_test", StageState.STAGE_AWAITING_APPROVAL)
        self.sm.request_transition("02_recovery_test", StageState.STAGE_REJECTED, rationale="Supervisor requested revisions")
        self.assertEqual(self.sm.stages["02_recovery_test"]["status"], StageState.STAGE_REJECTED.value)

        self.sm.request_transition("02_recovery_test", StageState.STAGE_READY, rationale="Revisions applied")
        self.assertEqual(self.sm.stages["02_recovery_test"]["status"], StageState.STAGE_READY.value)

        # READY -> RUNNING -> BLOCKED -> READY
        self.sm.request_transition("02_recovery_test", StageState.STAGE_RUNNING)
        self.sm.request_transition("02_recovery_test", StageState.STAGE_BLOCKED, rationale="Missing external service")
        self.assertEqual(self.sm.stages["02_recovery_test"]["status"], StageState.STAGE_BLOCKED.value)

        self.sm.request_transition("02_recovery_test", StageState.STAGE_READY, rationale="Service restored")
        self.assertEqual(self.sm.stages["02_recovery_test"]["status"], StageState.STAGE_READY.value)

    def test_03_invalid_state_transitions_fail_closed(self):
        """Tests that illegal shortcuts and skipped states strictly raise InvalidStateTransitionError."""
        self.sm.register_stage("03_invalid_test", "Invalid Transition Test", initial_status=StageState.STAGE_LOCKED)

        # LOCKED -> APPROVED (Illegal)
        with self.assertRaises(InvalidStateTransitionError):
            self.sm.request_transition("03_invalid_test", StageState.STAGE_APPROVED)

        # LOCKED -> RUNNING (Illegal)
        with self.assertRaises(InvalidStateTransitionError):
            self.sm.request_transition("03_invalid_test", StageState.STAGE_RUNNING)

        # LOCKED -> VALIDATING (Illegal)
        with self.assertRaises(InvalidStateTransitionError):
            self.sm.request_transition("03_invalid_test", StageState.STAGE_VALIDATING)

        # Advance to READY
        self.sm.request_transition("03_invalid_test", StageState.STAGE_READY)

        # READY -> APPROVED (Illegal)
        with self.assertRaises(InvalidStateTransitionError):
            self.sm.request_transition("03_invalid_test", StageState.STAGE_APPROVED)

        # Advance to RUNNING
        self.sm.request_transition("03_invalid_test", StageState.STAGE_RUNNING)

        # RUNNING -> AWAITING_APPROVAL (Illegal: must go through VALIDATING)
        with self.assertRaises(InvalidStateTransitionError):
            self.sm.request_transition("03_invalid_test", StageState.STAGE_AWAITING_APPROVAL)

        # Advance to VALIDATING
        self.sm.request_transition("03_invalid_test", StageState.STAGE_VALIDATING)

        # VALIDATING -> RUNNING (Illegal)
        with self.assertRaises(InvalidStateTransitionError):
            self.sm.request_transition("03_invalid_test", StageState.STAGE_RUNNING)

        # Unknown state string
        with self.assertRaises(UnknownStateError):
            self.sm.request_transition("03_invalid_test", "SOME_ARBITRARY_STATE")

    def test_04_prerequisite_stage_gating(self):
        """Tests that a dependent stage cannot become READY or RUNNING until upstream stage is STAGE_APPROVED."""
        self.sm.register_stage("stage_a", "Upstream Stage", initial_status=StageState.STAGE_LOCKED, requires_validation=False)
        self.sm.register_stage("stage_b", "Downstream Stage", initial_status=StageState.STAGE_LOCKED, dependencies=["stage_a"], requires_validation=False)

        # Transitioning Stage B to READY while Stage A is LOCKED must fail closed
        with self.assertRaises(UnmetPrerequisiteError):
            self.sm.request_transition("stage_b", StageState.STAGE_READY)

        # Progress Stage A to RUNNING (still not APPROVED)
        self.sm.request_transition("stage_a", StageState.STAGE_READY)
        self.sm.request_transition("stage_a", StageState.STAGE_RUNNING)

        with self.assertRaises(UnmetPrerequisiteError):
            self.sm.request_transition("stage_b", StageState.STAGE_READY)

        # Progress Stage A through VALIDATING and AWAITING_APPROVAL to APPROVED
        self.sm.request_transition("stage_a", StageState.STAGE_VALIDATING)
        self.sm.request_transition("stage_a", StageState.STAGE_AWAITING_APPROVAL)
        appr = self.sm.request_approval("stage_a", "stage_a", "agent", "ready")
        self.sm.grant_approval(appr["approval_id"], "Saber Admin Desk 124911145", "SIG-AUTH-001", "Approved")
        self.sm.request_transition("stage_a", StageState.STAGE_APPROVED)

        # Stage A is now APPROVED -> Stage B auto-unlocked to READY!
        self.assertEqual(self.sm.stages["stage_b"]["status"], StageState.STAGE_READY.value)
        # Stage B can now transition to RUNNING
        res = self.sm.request_transition("stage_b", StageState.STAGE_RUNNING)
        self.assertEqual(res["to_state"], StageState.STAGE_RUNNING.value)

    def test_05_artifact_existence_gating(self):
        """Tests that missing input or output artifacts mechanically block transitions."""
        self.sm.register_stage(
            "stage_artifacts",
            "Artifact Stage",
            initial_status=StageState.STAGE_LOCKED,
            required_input_artifacts=["data/raw_dataset.csv"],
            required_output_artifacts=["analysis/descriptive_output.json"],
            requires_validation=False
        )

        # Missing input artifact blocks READY transition
        with self.assertRaises(MissingRequiredArtifactError):
            self.sm.request_transition("stage_artifacts", StageState.STAGE_READY, check_artifacts=True)

        # Create input artifact
        os.makedirs(os.path.join(self.state_dir, "data"), exist_ok=True)
        with open(os.path.join(self.state_dir, "data", "raw_dataset.csv"), "w") as f:
            f.write("id,var1,var2\n1,10,20\n")

        # Now READY transition succeeds
        res = self.sm.request_transition("stage_artifacts", StageState.STAGE_READY, check_artifacts=True)
        self.assertEqual(res["to_state"], StageState.STAGE_READY.value)

        # Advance to RUNNING
        self.sm.request_transition("stage_artifacts", StageState.STAGE_RUNNING, check_artifacts=True)

        # Transition to VALIDATING requires output artifact; currently missing!
        with self.assertRaises(MissingRequiredArtifactError):
            self.sm.request_transition("stage_artifacts", StageState.STAGE_VALIDATING, check_artifacts=True)

        # Create output artifact
        os.makedirs(os.path.join(self.state_dir, "analysis"), exist_ok=True)
        with open(os.path.join(self.state_dir, "analysis", "descriptive_output.json"), "w") as f:
            f.write('{"status": "COMPUTED"}')

        # Now VALIDATING succeeds
        res = self.sm.request_transition("stage_artifacts", StageState.STAGE_VALIDATING, check_artifacts=True)
        self.assertEqual(res["to_state"], StageState.STAGE_VALIDATING.value)

    def test_06_authorization_and_validation_gating(self):
        """Tests that STAGE_APPROVED strictly requires granted human approval and a PASS validation report."""
        self.sm.register_stage(
            "stage_auth_test",
            "Authorization Test",
            initial_status=StageState.STAGE_AWAITING_APPROVAL,
            requires_validation=True
        )

        # 1. Attempt approval without approval grant -> MissingApprovalError
        with self.assertRaises(MissingApprovalError):
            self.sm.request_transition("stage_auth_test", StageState.STAGE_APPROVED, check_artifacts=False)

        # 2. Grant approval
        appr = self.sm.request_approval("stage_auth_test", "auth_test", "statistics-agent", "Ready for approval")
        self.sm.grant_approval(appr["approval_id"], "Saber Admin Desk 124911145", "SIG-PASS-124911145", "Approved")

        # 3. Attempt approval with missing validation report -> MilestoneValidationRequiredError
        with self.assertRaises(MilestoneValidationRequiredError):
            self.sm.request_transition("stage_auth_test", StageState.STAGE_APPROVED, check_artifacts=False)

        # 4. Create failing validation report -> MilestoneValidationRequiredError
        val_path = os.path.join(self.state_dir, "validation_report.json")
        with open(val_path, "w", encoding="utf-8") as f:
            json.dump({"overall_verdict": "FAIL", "errors": ["Normality assumption violated"]}, f)

        with self.assertRaises(MilestoneValidationRequiredError):
            self.sm.request_transition("stage_auth_test", StageState.STAGE_APPROVED, check_artifacts=False)

        # 5. Create passing validation report -> STAGE_APPROVED succeeds
        with open(val_path, "w", encoding="utf-8") as f:
            json.dump({"overall_verdict": "PASS", "checks": {"normality": "PASS"}}, f)

        res = self.sm.request_transition("stage_auth_test", StageState.STAGE_APPROVED, check_artifacts=False)
        self.assertEqual(res["to_state"], StageState.STAGE_APPROVED.value)

    def test_07_direct_set_stage_mutation_blocked_in_production(self):
        """Tests that direct set_stage() mutation is fail-closed in production and permitted in test mode."""
        init_state(self.temp_dir, title="Direct Mutation Test", methodology="sem", n=200)

        # In production mode (default), set_stage must strictly raise DirectStageMutationBlockedError
        with self.assertRaises(DirectStageMutationBlockedError):
            set_stage(self.temp_dir, stage="05_macro_model", status="in_progress", mode="production")

        # In test mode, mutation is allowed
        res = set_stage(self.temp_dir, stage="05_macro_model", status="in_progress", mode="test")
        self.assertEqual(res["status"], "UPDATED")
        self.assertEqual(res["current_stage"], "05_macro_model")

    def test_08_project_level_lifecycle(self):
        """Tests PROJECT_CREATED -> PROJECT_APPROVED and PROJECT_REJECTED transitions."""
        self.assertEqual(self.sm.project_state, ProjectState.PROJECT_CREATED.value)

        # Attempting PROJECT_APPROVED when stages are not approved must raise UnmetPrerequisiteError
        self.sm.register_stage("p_stage_1", "Stage 1", initial_status=StageState.STAGE_LOCKED)
        with self.assertRaises(UnmetPrerequisiteError):
            self.sm.request_transition(self.sm.project_id, ProjectState.PROJECT_APPROVED, target_type="PROJECT")

        # Progress stage to approved
        self.sm.stages["p_stage_1"]["status"] = StageState.STAGE_APPROVED.value

        # Attempting PROJECT_APPROVED without release approval must raise MissingApprovalError
        with self.assertRaises(MissingApprovalError):
            self.sm.request_transition(self.sm.project_id, ProjectState.PROJECT_APPROVED, target_type="PROJECT")

        # Grant release approval
        appr = self.sm.request_approval("PROJECT_LEVEL", "final_release", "academic-orchestrator", "Project ready")
        self.sm.grant_approval(appr["approval_id"], "Saber Admin Desk 124911145", "SIG-FINAL-RELEASE", "Final Release Approved")

        # Transition to PROJECT_APPROVED succeeds
        res = self.sm.request_transition(self.sm.project_id, ProjectState.PROJECT_APPROVED, target_type="PROJECT")
        self.assertEqual(res["to_state"], ProjectState.PROJECT_APPROVED.value)
        self.assertEqual(self.sm.project_state, ProjectState.PROJECT_APPROVED.value)

    def test_09_cli_request_transition(self):
        """Tests the request_transition module-level function and CLI interface."""
        init_state(self.temp_dir, title="CLI Transition Test", methodology="sem", n=150)

        # Transition initial stage 00_data_curation (which starts READY) to RUNNING via request_transition()
        res = request_transition(
            project_path=self.temp_dir,
            target_id="00_data_curation",
            target_state=StageState.STAGE_RUNNING,
            actor="data-curator",
            rationale="Starting data ingestion",
            check_artifacts=False
        )
        self.assertEqual(res["status"], "TRANSITIONED")
        self.assertEqual(res["to_state"], StageState.STAGE_RUNNING.value)

    def test_10_restart_safety(self):
        """Tests that state snapshots in current_state.json completely recover stage states across process restarts."""
        self.sm.register_stage("persist_stage", "Persist Stage", initial_status=StageState.STAGE_READY)
        self.sm.request_transition("persist_stage", StageState.STAGE_RUNNING, rationale="Testing persistence")
        self.assertEqual(self.sm.stages["persist_stage"]["status"], StageState.STAGE_RUNNING.value)

        # Simulate process termination and re-instantiation
        del self.sm
        reloaded_sm = StrictStateMachine(state_dir=self.state_dir, project_id="phase7_study")

        self.assertIn("persist_stage", reloaded_sm.stages)
        self.assertEqual(reloaded_sm.stages["persist_stage"]["status"], StageState.STAGE_RUNNING.value)
        self.assertGreaterEqual(len(reloaded_sm.stages["persist_stage"]["history"]), 2)


if __name__ == "__main__":
    unittest.main()
