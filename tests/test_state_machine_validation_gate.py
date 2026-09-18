#!/usr/bin/env python3
"""
Regression test for ATK-11: State Machine Milestone Approval without Validation Check.

Verifies that StrictStateMachine.transition_milestone(..., APPROVED) strictly requires
a passing validation report (overall_verdict == 'PASS') and blocks approval if missing or non-passing.
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
    MilestoneState,
    MilestoneValidationRequiredError,
    MissingApprovalError
)


class TestStateMachineValidationGate(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_val_gate_")
        self.state_dir = os.path.join(self.temp_dir, "state")
        self.sm = StrictStateMachine(state_dir=self.state_dir, project_id="test_val_proj")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_missing_validation_report_blocks_approval(self):
        """Milestone requiring validation cannot transition to APPROVED if validation_report.json is missing."""
        self.sm.register_milestone(
            milestone_id="M7_HYPOTHESIS_TESTING",
            title="Hypothesis Testing",
            required_output_artifacts=["hypothesis_1.docx"]
        )
        self.sm.milestones["M7_HYPOTHESIS_TESTING"]["status"] = MilestoneState.AWAITING_APPROVAL.value

        # Grant human approval
        appr = self.sm.request_approval(
            milestone_id="M7_HYPOTHESIS_TESTING",
            category="hypothesis_testing",
            requester_agent="final-judge",
            rationale="Ready for approval"
        )
        self.sm.grant_approval(appr["approval_id"], "Saber Admin Desk 124911145", "SIG-VALID-123", "Approved")

        # Attempt transition without validation report
        with self.assertRaises(MilestoneValidationRequiredError):
            self.sm.transition_milestone("M7_HYPOTHESIS_TESTING", MilestoneState.APPROVED, check_artifacts=False)

    def test_failing_validation_report_blocks_approval(self):
        """Milestone cannot transition to APPROVED if validation report has overall_verdict != 'PASS'."""
        self.sm.register_milestone(
            milestone_id="M7_HYPOTHESIS_TESTING",
            title="Hypothesis Testing"
        )
        self.sm.milestones["M7_HYPOTHESIS_TESTING"]["status"] = MilestoneState.AWAITING_APPROVAL.value

        # Grant human approval
        appr = self.sm.request_approval("M7_HYPOTHESIS_TESTING", "hypothesis_testing", "final-judge", "Ready")
        self.sm.grant_approval(appr["approval_id"], "Saber Admin Desk 124911145", "SIG-VALID-123", "Approved")

        # Create failing validation report
        val_path = os.path.join(self.state_dir, "validation_report.json")
        with open(val_path, "w", encoding="utf-8") as f:
            json.dump({
                "overall_verdict": "FAIL",
                "discrepancies": ["p-value mismatch between json and docx"]
            }, f)

        with self.assertRaises(MilestoneValidationRequiredError):
            self.sm.transition_milestone("M7_HYPOTHESIS_TESTING", MilestoneState.APPROVED, check_artifacts=False)

    def test_passing_validation_report_allows_approval(self):
        """Milestone successfully transitions to APPROVED when a valid passing report exists."""
        self.sm.register_milestone(
            milestone_id="M7_HYPOTHESIS_TESTING",
            title="Hypothesis Testing"
        )
        self.sm.milestones["M7_HYPOTHESIS_TESTING"]["status"] = MilestoneState.AWAITING_APPROVAL.value

        appr = self.sm.request_approval("M7_HYPOTHESIS_TESTING", "hypothesis_testing", "final-judge", "Ready")
        self.sm.grant_approval(appr["approval_id"], "Saber Admin Desk 124911145", "SIG-VALID-123", "Approved")

        # Create passing validation report
        val_path = os.path.join(self.state_dir, "validation_report.json")
        with open(val_path, "w", encoding="utf-8") as f:
            json.dump({
                "overall_verdict": "PASS",
                "checks": {"result_consistency": "PASS", "provenance": "PASS"}
            }, f)

        res = self.sm.transition_milestone("M7_HYPOTHESIS_TESTING", MilestoneState.APPROVED, check_artifacts=False)
        self.assertEqual(res["to_state"], MilestoneState.APPROVED.value)


if __name__ == "__main__":
    unittest.main()
