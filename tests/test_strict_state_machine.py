#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_strict_state_machine.py — Comprehensive Unit Tests for Strict State Machine

Tests:
1. Valid transition sequence: CREATED -> SCOPED -> PLANNED -> READY -> RUNNING -> VALIDATING -> AWAITING_APPROVAL -> APPROVED -> SUPERSEDED
2. Recovery valid transitions: FAILED -> READY, FAILED -> PLANNED, REJECTED -> PLANNED, REJECTED -> SCOPED
3. Invalid transitions: CREATED -> APPROVED, READY -> APPROVED, APPROVED -> RUNNING, etc. (InvalidStateTransitionError)
4. Unknown state validation (UnknownStateError)
5. Unknown milestone validation (UnknownMilestoneError)
6. Unknown dependency validation (UnknownDependencyError)
7. Unmet dependency validation (UnmetDependencyError)
8. Missing required input artifact prevents READY transition (MissingRequiredArtifactError)
9. Missing required output artifact prevents APPROVED transition (MissingRequiredArtifactError)
10. Missing human approval prevents APPROVED transition (MissingApprovalError)
11. Approval never defaults to True (status=PENDING, is_approved=False)
12. Duplicate approval detection (DuplicateApprovalError)
13. Stale approval rejection (StaleApprovalError)
14. Restart/Resume safety across process restarts
15. Superseded milestone handling (terminal for current, satisfies downstream dependencies)
"""

import os
import sys
import json
import shutil
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT_DIR, "scripts"))

from academic_state_manager import (
    StrictStateMachine,
    MilestoneState,
    VALID_TRANSITIONS,
    StateManagementError,
    UnknownStateError,
    UnknownMilestoneError,
    UnknownDependencyError,
    UnmetDependencyError,
    InvalidStateTransitionError,
    MissingRequiredArtifactError,
    MissingApprovalError,
    DuplicateApprovalError,
    StaleApprovalError,
    record_decision
)


class TestStrictStateMachine(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_state_machine_")
        self.state_dir = os.path.join(self.temp_dir, "state")
        self.sm = StrictStateMachine(state_dir=self.state_dir, project_id="test_proj_001")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_every_valid_transition_happy_path(self):
        """Tests the entire complete lifecycle: CREATED -> SCOPED -> PLANNED -> READY -> RUNNING -> VALIDATING -> AWAITING_APPROVAL -> APPROVED -> SUPERSEDED."""
        # 1. Register milestone
        self.sm.register_milestone(
            milestone_id="M_TEST_01",
            title="Statistical Model Testing",
            dependencies=[],
            required_input_artifacts=[],
            required_output_artifacts=[]
        )
        self.assertEqual(self.sm.milestones["M_TEST_01"]["status"], MilestoneState.CREATED.value)

        # 2. CREATED -> SCOPED
        res = self.sm.transition_milestone("M_TEST_01", MilestoneState.SCOPED, rationale="Scope defined")
        self.assertEqual(res["to_state"], MilestoneState.SCOPED.value)

        # 3. SCOPED -> PLANNED
        res = self.sm.transition_milestone("M_TEST_01", MilestoneState.PLANNED, rationale="Plan formulated")
        self.assertEqual(res["to_state"], MilestoneState.PLANNED.value)

        # 4. PLANNED -> READY
        res = self.sm.transition_milestone("M_TEST_01", MilestoneState.READY, rationale="Prerequisites ready")
        self.assertEqual(res["to_state"], MilestoneState.READY.value)

        # 5. READY -> RUNNING
        res = self.sm.transition_milestone("M_TEST_01", MilestoneState.RUNNING, rationale="Execution started")
        self.assertEqual(res["to_state"], MilestoneState.RUNNING.value)

        # 6. RUNNING -> VALIDATING
        res = self.sm.transition_milestone("M_TEST_01", MilestoneState.VALIDATING, rationale="Execution finished")
        self.assertEqual(res["to_state"], MilestoneState.VALIDATING.value)

        # 7. VALIDATING -> AWAITING_APPROVAL
        res = self.sm.transition_milestone("M_TEST_01", MilestoneState.AWAITING_APPROVAL, rationale="Validation PASS")
        self.assertEqual(res["to_state"], MilestoneState.AWAITING_APPROVAL.value)

        # 8. Request and Grant Approval
        appr = self.sm.request_approval(
            milestone_id="M_TEST_01",
            category="methodology_specification",
            requester_agent="statistical-expert",
            rationale="All models verified"
        )
        self.assertFalse(appr["is_approved"])
        self.assertEqual(appr["status"], "PENDING")

        self.sm.grant_approval(
            approval_id=appr["approval_id"],
            approver_identity="Saber Admin Desk 124911145",
            digital_signature="SIG-AUTH-124911145",
            comments="Approved"
        )

        # 9. AWAITING_APPROVAL -> APPROVED
        res = self.sm.transition_milestone("M_TEST_01", MilestoneState.APPROVED, rationale="Explicit approval granted")
        self.assertEqual(res["to_state"], MilestoneState.APPROVED.value)

        # 10. APPROVED -> SUPERSEDED
        res = self.sm.transition_milestone("M_TEST_01", MilestoneState.SUPERSEDED, rationale="Next iteration approved")
        self.assertEqual(res["to_state"], MilestoneState.SUPERSEDED.value)

    def test_02_recovery_valid_transitions(self):
        """Tests valid failure and rejection recovery paths: RUNNING -> FAILED -> READY, VALIDATING -> FAILED -> PLANNED, REJECTED -> PLANNED."""
        self.sm.register_milestone("M_REC_01", "Recovery Milestone")
        self.sm.transition_milestone("M_REC_01", MilestoneState.SCOPED)
        self.sm.transition_milestone("M_REC_01", MilestoneState.PLANNED)
        self.sm.transition_milestone("M_REC_01", MilestoneState.READY)
        self.sm.transition_milestone("M_REC_01", MilestoneState.RUNNING)

        # RUNNING -> FAILED
        self.sm.transition_milestone("M_REC_01", MilestoneState.FAILED, rationale="Process crashed")
        self.assertEqual(self.sm.milestones["M_REC_01"]["status"], MilestoneState.FAILED.value)

        # FAILED -> READY (retry)
        self.sm.transition_milestone("M_REC_01", MilestoneState.READY, rationale="Retrying execution")
        self.assertEqual(self.sm.milestones["M_REC_01"]["status"], MilestoneState.READY.value)

        # READY -> RUNNING -> VALIDATING -> FAILED
        self.sm.transition_milestone("M_REC_01", MilestoneState.RUNNING)
        self.sm.transition_milestone("M_REC_01", MilestoneState.VALIDATING)
        self.sm.transition_milestone("M_REC_01", MilestoneState.FAILED, rationale="Validation failed")
        self.assertEqual(self.sm.milestones["M_REC_01"]["status"], MilestoneState.FAILED.value)

        # FAILED -> PLANNED (re-planning)
        self.sm.transition_milestone("M_REC_01", MilestoneState.PLANNED, rationale="Re-planning approach")
        self.assertEqual(self.sm.milestones["M_REC_01"]["status"], MilestoneState.PLANNED.value)

        # PLANNED -> READY -> RUNNING -> VALIDATING -> AWAITING_APPROVAL -> REJECTED
        self.sm.transition_milestone("M_REC_01", MilestoneState.READY)
        self.sm.transition_milestone("M_REC_01", MilestoneState.RUNNING)
        self.sm.transition_milestone("M_REC_01", MilestoneState.VALIDATING)
        self.sm.transition_milestone("M_REC_01", MilestoneState.AWAITING_APPROVAL)
        self.sm.transition_milestone("M_REC_01", MilestoneState.REJECTED, rationale="Supervisor rejected")
        self.assertEqual(self.sm.milestones["M_REC_01"]["status"], MilestoneState.REJECTED.value)

        # REJECTED -> PLANNED
        self.sm.transition_milestone("M_REC_01", MilestoneState.PLANNED, rationale="Revising plan")
        self.assertEqual(self.sm.milestones["M_REC_01"]["status"], MilestoneState.PLANNED.value)

    def test_03_invalid_transitions_blocked(self):
        """Illegal state transitions must strictly raise InvalidStateTransitionError."""
        self.sm.register_milestone("M_ILLEGAL", "Illegal Transition Test")

        # CREATED -> APPROVED (illegal leap)
        with self.assertRaises(InvalidStateTransitionError):
            self.sm.transition_milestone("M_ILLEGAL", MilestoneState.APPROVED)

        # CREATED -> RUNNING (illegal leap)
        with self.assertRaises(InvalidStateTransitionError):
            self.sm.transition_milestone("M_ILLEGAL", MilestoneState.RUNNING)

        # CREATED -> READY (illegal leap)
        with self.assertRaises(InvalidStateTransitionError):
            self.sm.transition_milestone("M_ILLEGAL", MilestoneState.READY)

        self.sm.transition_milestone("M_ILLEGAL", MilestoneState.SCOPED)

        # SCOPED -> APPROVED
        with self.assertRaises(InvalidStateTransitionError):
            self.sm.transition_milestone("M_ILLEGAL", MilestoneState.APPROVED)

        self.sm.transition_milestone("M_ILLEGAL", MilestoneState.PLANNED)
        self.sm.transition_milestone("M_ILLEGAL", MilestoneState.READY)

        # READY -> APPROVED
        with self.assertRaises(InvalidStateTransitionError):
            self.sm.transition_milestone("M_ILLEGAL", MilestoneState.APPROVED)

    def test_04_unknown_state_raises_error(self):
        """Unknown or arbitrary state names must raise UnknownStateError."""
        self.sm.register_milestone("M_STATE_TEST", "Test")
        with self.assertRaises(UnknownStateError):
            self.sm.transition_milestone("M_STATE_TEST", "NON_EXISTENT_STATE")

        with self.assertRaises(UnknownStateError):
            self.sm.transition_milestone("M_STATE_TEST", "MAGIC_STATE")

    def test_05_unknown_milestone_raises_error(self):
        """Referencing an unregistered milestone must raise UnknownMilestoneError."""
        with self.assertRaises(UnknownMilestoneError):
            self.sm.transition_milestone("M_GHOST_MILESTONE", MilestoneState.SCOPED)

        with self.assertRaises(UnknownMilestoneError):
            self.sm.request_approval("M_GHOST_MILESTONE", "cat", "agent", "rationale")

    def test_06_unknown_dependency_raises_error(self):
        """Declaring a dependency on an unknown milestone must raise UnknownDependencyError."""
        with self.assertRaises(UnknownDependencyError):
            self.sm.register_milestone(
                "M_DEP_TEST",
                "Dependency Test",
                dependencies=["M_DOES_NOT_EXIST"]
            )

    def test_07_unmet_dependency_blocks_ready_transition(self):
        """A milestone cannot become READY if upstream dependencies are not APPROVED or SUPERSEDED."""
        # M_PARENT in CREATED
        self.sm.register_milestone("M_PARENT", "Parent Milestone")
        # M_CHILD depends on M_PARENT
        self.sm.register_milestone("M_CHILD", "Child Milestone", dependencies=["M_PARENT"])

        self.sm.transition_milestone("M_CHILD", MilestoneState.SCOPED)
        self.sm.transition_milestone("M_CHILD", MilestoneState.PLANNED)

        # Attempting M_CHILD -> READY while M_PARENT is CREATED must fail
        with self.assertRaises(UnmetDependencyError):
            self.sm.transition_milestone("M_CHILD", MilestoneState.READY)

        # Advance parent to APPROVED
        self.sm.transition_milestone("M_PARENT", MilestoneState.SCOPED)
        self.sm.transition_milestone("M_PARENT", MilestoneState.PLANNED)
        self.sm.transition_milestone("M_PARENT", MilestoneState.READY)
        self.sm.transition_milestone("M_PARENT", MilestoneState.RUNNING)
        self.sm.transition_milestone("M_PARENT", MilestoneState.VALIDATING)
        self.sm.transition_milestone("M_PARENT", MilestoneState.AWAITING_APPROVAL)

        appr = self.sm.request_approval("M_PARENT", "methodology_specification", "agent", "done")
        self.sm.grant_approval(appr["approval_id"], "Admin", "ACK-SIGNATURE-001")
        self.sm.transition_milestone("M_PARENT", MilestoneState.APPROVED)

        # Now M_CHILD -> READY must succeed because M_PARENT is APPROVED
        res = self.sm.transition_milestone("M_CHILD", MilestoneState.READY)
        self.assertEqual(res["to_state"], MilestoneState.READY.value)

    def test_08_missing_required_artifacts_block_transitions(self):
        """Missing required input artifacts block READY; missing output artifacts block APPROVED."""
        input_art = os.path.join(self.state_dir, "required_input.json")
        output_art = os.path.join(self.state_dir, "required_output.docx")

        self.sm.register_milestone(
            "M_ART_GATED",
            "Artifact Gated Milestone",
            dependencies=[],
            required_input_artifacts=[input_art],
            required_output_artifacts=[output_art]
        )
        self.sm.transition_milestone("M_ART_GATED", MilestoneState.SCOPED)
        self.sm.transition_milestone("M_ART_GATED", MilestoneState.PLANNED)

        # 1. Missing input artifact blocks PLANNED -> READY
        with self.assertRaises(MissingRequiredArtifactError):
            self.sm.transition_milestone("M_ART_GATED", MilestoneState.READY)

        # Create input artifact
        with open(input_art, "w") as f:
            f.write('{"status": "ok"}')

        # Now READY succeeds
        self.sm.transition_milestone("M_ART_GATED", MilestoneState.READY)
        self.sm.transition_milestone("M_ART_GATED", MilestoneState.RUNNING)
        self.sm.transition_milestone("M_ART_GATED", MilestoneState.VALIDATING)
        self.sm.transition_milestone("M_ART_GATED", MilestoneState.AWAITING_APPROVAL)

        # Approve
        appr = self.sm.request_approval("M_ART_GATED", "methodology_specification", "agent", "ready")
        self.sm.grant_approval(appr["approval_id"], "Admin", "ACK-SIGNATURE-002")

        # 2. Missing output artifact blocks AWAITING_APPROVAL -> APPROVED
        with self.assertRaises(MissingRequiredArtifactError):
            self.sm.transition_milestone("M_ART_GATED", MilestoneState.APPROVED)

        # Create output artifact
        with open(output_art, "w") as f:
            f.write("fake docx content")

        # Now APPROVED succeeds
        res = self.sm.transition_milestone("M_ART_GATED", MilestoneState.APPROVED)
        self.assertEqual(res["to_state"], MilestoneState.APPROVED.value)

    def test_09_missing_human_approval_blocks_approved_transition(self):
        """A milestone CANNOT transition to APPROVED without explicit, granted human approval."""
        self.sm.register_milestone("M_APPROVAL_TEST", "Approval Gate Test")
        self.sm.transition_milestone("M_APPROVAL_TEST", MilestoneState.SCOPED)
        self.sm.transition_milestone("M_APPROVAL_TEST", MilestoneState.PLANNED)
        self.sm.transition_milestone("M_APPROVAL_TEST", MilestoneState.READY)
        self.sm.transition_milestone("M_APPROVAL_TEST", MilestoneState.RUNNING)
        self.sm.transition_milestone("M_APPROVAL_TEST", MilestoneState.VALIDATING)
        self.sm.transition_milestone("M_APPROVAL_TEST", MilestoneState.AWAITING_APPROVAL)

        # Case A: No approval requested at all
        with self.assertRaises(MissingApprovalError):
            self.sm.transition_milestone("M_APPROVAL_TEST", MilestoneState.APPROVED)

        # Case B: Approval requested, but status is still PENDING (is_approved = False)
        appr = self.sm.request_approval("M_APPROVAL_TEST", "methodology_specification", "agent", "check")
        with self.assertRaises(MissingApprovalError):
            self.sm.transition_milestone("M_APPROVAL_TEST", MilestoneState.APPROVED)

        # Case C: Explicitly granted approval enables APPROVED transition
        self.sm.grant_approval(appr["approval_id"], "Saber Admin Desk", "ACK-124911145-PASS")
        res = self.sm.transition_milestone("M_APPROVAL_TEST", MilestoneState.APPROVED)
        self.assertEqual(res["to_state"], MilestoneState.APPROVED.value)

    def test_10_approval_defaults_to_false(self):
        """Approval requests and decision records must NEVER default to True."""
        self.sm.register_milestone("M_DEFAULT_CHECK", "Default Check")
        appr = self.sm.request_approval("M_DEFAULT_CHECK", "pricing", "agent", "rationale")
        self.assertFalse(appr["is_approved"], "Approval MUST default to False")
        self.assertEqual(appr["status"], "PENDING")

        # Check record_decision default
        dec_res = record_decision(self.temp_dir, "methodology", "Decision text", "Rationale text", "orchestrator")
        self.assertFalse(dec_res["entry"]["supervisor_approval"], "record_decision must default to supervisor_approval=False")

    def test_11_duplicate_approval_raises_error(self):
        """Granting an already granted approval must raise DuplicateApprovalError."""
        self.sm.register_milestone("M_DUP_APPR", "Duplicate Approval Test")
        appr = self.sm.request_approval("M_DUP_APPR", "pricing", "agent", "rationale")

        self.sm.grant_approval(appr["approval_id"], "Admin", "ACK-SIGNATURE-003")

        with self.assertRaises(DuplicateApprovalError):
            self.sm.grant_approval(appr["approval_id"], "Admin", "ACK-SIGNATURE-003")

    def test_12_stale_approval_raises_error(self):
        """Attempting to grant or use an approval for a milestone that changed state raises StaleApprovalError."""
        self.sm.register_milestone("M_STALE", "Stale Test")
        self.sm.transition_milestone("M_STALE", MilestoneState.SCOPED)
        self.sm.transition_milestone("M_STALE", MilestoneState.PLANNED)
        self.sm.transition_milestone("M_STALE", MilestoneState.READY)
        self.sm.transition_milestone("M_STALE", MilestoneState.RUNNING)
        self.sm.transition_milestone("M_STALE", MilestoneState.VALIDATING)
        self.sm.transition_milestone("M_STALE", MilestoneState.AWAITING_APPROVAL)

        appr = self.sm.request_approval("M_STALE", "methodology_specification", "agent", "review")

        # Milestone transitions to FAILED or REJECTED due to issue discovered
        self.sm.transition_milestone("M_STALE", MilestoneState.REJECTED, rationale="Issue detected")

        # Now attempting to grant the stale approval must fail
        with self.assertRaises(StaleApprovalError):
            self.sm.grant_approval(appr["approval_id"], "Admin", "ACK-SIGNATURE-004")

    def test_13_restart_resume_safety(self):
        """State machine completely reloads all milestones, statuses, and approvals on restart."""
        self.sm.register_milestone("M_PERSIST", "Persistence Test")
        self.sm.transition_milestone("M_PERSIST", MilestoneState.SCOPED)
        self.sm.transition_milestone("M_PERSIST", MilestoneState.PLANNED)
        self.sm.transition_milestone("M_PERSIST", MilestoneState.READY)
        self.sm.transition_milestone("M_PERSIST", MilestoneState.RUNNING)

        # Register artifact
        art_path = os.path.join(self.state_dir, "test_artifact.json")
        with open(art_path, "w") as f:
            f.write('{"test": 123}')
        self.sm.register_artifact("ART-TEST-001", "M_PERSIST", "06_hypothesis_1", "stats_json", "test_artifact.json")

        # Re-instantiate a fresh state machine pointing to the same state directory
        sm2 = StrictStateMachine(state_dir=self.state_dir, project_id="test_proj_001")

        self.assertIn("M_PERSIST", sm2.milestones)
        self.assertEqual(sm2.milestones["M_PERSIST"]["status"], MilestoneState.RUNNING.value)
        self.assertEqual(len(sm2.artifacts), 1)
        self.assertEqual(sm2.artifacts[0]["artifact_id"], "ART-TEST-001")

        # Can continue valid transitions seamlessly on sm2
        sm2.transition_milestone("M_PERSIST", MilestoneState.VALIDATING)
        self.assertEqual(sm2.milestones["M_PERSIST"]["status"], MilestoneState.VALIDATING.value)

    def test_14_superseded_milestone_lifecycle(self):
        """A superseded milestone cannot transition further, but satisfies dependencies for downstream milestones."""
        self.sm.register_milestone("M_VER_1", "Version 1")
        self.sm.transition_milestone("M_VER_1", MilestoneState.SCOPED)
        self.sm.transition_milestone("M_VER_1", MilestoneState.PLANNED)
        self.sm.transition_milestone("M_VER_1", MilestoneState.READY)
        self.sm.transition_milestone("M_VER_1", MilestoneState.RUNNING)
        self.sm.transition_milestone("M_VER_1", MilestoneState.VALIDATING)
        self.sm.transition_milestone("M_VER_1", MilestoneState.AWAITING_APPROVAL)

        appr = self.sm.request_approval("M_VER_1", "methodology_specification", "agent", "ready")
        self.sm.grant_approval(appr["approval_id"], "Admin", "ACK-SIGNATURE-005")
        self.sm.transition_milestone("M_VER_1", MilestoneState.APPROVED)

        # Transition to SUPERSEDED
        self.sm.transition_milestone("M_VER_1", MilestoneState.SUPERSEDED, rationale="Superseded by Version 2")
        self.assertEqual(self.sm.milestones["M_VER_1"]["status"], MilestoneState.SUPERSEDED.value)

        # Attempting any transition from SUPERSEDED must fail
        with self.assertRaises(InvalidStateTransitionError):
            self.sm.transition_milestone("M_VER_1", MilestoneState.RUNNING)

        # Downstream milestone depending on M_VER_1 is satisfied by SUPERSEDED status
        self.sm.register_milestone("M_DOWNSTREAM", "Downstream Milestone", dependencies=["M_VER_1"])
        self.sm.transition_milestone("M_DOWNSTREAM", MilestoneState.SCOPED)
        self.sm.transition_milestone("M_DOWNSTREAM", MilestoneState.PLANNED)
        res = self.sm.transition_milestone("M_DOWNSTREAM", MilestoneState.READY)
        self.assertEqual(res["to_state"], MilestoneState.READY.value)


if __name__ == "__main__":
    unittest.main()
