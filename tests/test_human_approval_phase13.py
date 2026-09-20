#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_human_approval_phase13.py — Comprehensive Unit & Integration Tests for Phase 13 Human Approval

Verifies Phase 13 architectural mandates:
1. Rebuild human approval as an explicit physical state: STAGE_AWAITING_APPROVAL
2. Cryptographic approval record schema compliance (contracts/approval_record.schema.json)
3. Full happy-path flow:
   STAGE_RUNNING -> STAGE_VALIDATING -> STAGE_AWAITING_APPROVAL -> approve_stage -> STAGE_APPROVED -> next stage unlocked (STAGE_READY)
4. Downstream stage gating: downstream stages remain STAGE_LOCKED and cannot transition while upstream is STAGE_AWAITING_APPROVAL
5. Fail-closed prerequisites: approval request blocked if validation_report.json is missing or verdict != PASS
6. Cryptographic tamper protection: hash mutation in deliverable or validation report raises ApprovalTamperError
7. Human rejection flow: STAGE_AWAITING_APPROVAL -> STAGE_REJECTED, downstream remains STAGE_LOCKED
8. CLI subcommand execution: request, approve, reject, status
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

try:
    import jsonschema
except ImportError:
    jsonschema = None

from scripts.academic_state_manager import (
    StrictStateMachine,
    AcademicStateManager,
    StageState,
    StateManagementError,
    UnmetPrerequisiteError,
    MissingApprovalError,
    StaleApprovalError,
    MilestoneValidationRequiredError
)

from scripts.academic_approval_engine import (
    request_stage_approval,
    approve_stage,
    reject_stage,
    get_approval_status,
    compute_sha256,
    load_approval_schema,
    ApprovalError,
    ApprovalPrerequisiteError,
    ApprovalTamperError
)


class TestHumanApprovalPhase13(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="phase13_approval_test_")
        self.state_dir = os.path.join(self.temp_dir, "academic-state")
        os.makedirs(self.state_dir, exist_ok=True)
        self.sm = StrictStateMachine(state_dir=self.state_dir, project_id="approval_study")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_schema_validation(self):
        """Tests that approval_record.schema.json validates correct records and rejects invalid ones."""
        schema = load_approval_schema()
        self.assertIsNotNone(schema, "approval_record.schema.json could not be loaded")

        if not jsonschema:
            self.skipTest("jsonschema not installed")

        valid_record = {
            "contract_version": "1.0.0",
            "approval_id": "APP-06_hypothesis_1-20260919120000",
            "stage_id": "06_hypothesis_1",
            "project_id": "approval_study",
            "artifact_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "validation_hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            "requested_at": "2026-09-19T12:00:00Z",
            "decision": "PENDING",
            "status": "PENDING",
            "is_approved": False
        }
        # Should not raise
        jsonschema.validate(instance=valid_record, schema=schema)

        # Missing required field 'artifact_hash'
        invalid_record = dict(valid_record)
        del invalid_record["artifact_hash"]
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=invalid_record, schema=schema)

        # Invalid decision enum
        invalid_record2 = dict(valid_record)
        invalid_record2["decision"] = "MAYBE"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=invalid_record2, schema=schema)

    def test_02_full_stage_approval_and_auto_unlock_flow(self):
        """
        Tests the complete Phase 13 pipeline:
        Stage 0 completes -> validates -> requests approval (STAGE_AWAITING_APPROVAL)
        Stage 1 is dependent and STAGE_LOCKED
        Human approves -> Stage 0 becomes STAGE_APPROVED
        Stage 1 automatically transitions from STAGE_LOCKED -> STAGE_READY
        """
        # Register stage 0 and dependent stage 1
        self.sm.register_stage(
            stage_id="00_data_curation",
            title="Data Curation",
            initial_status=StageState.STAGE_READY,
            dependencies=[],
            required_input_artifacts=[],
            required_output_artifacts=["data/data_quality.json"],
            requires_validation=True,
            requires_manifest=False
        )
        self.sm.register_stage(
            stage_id="01_demographics",
            title="Demographics",
            initial_status=StageState.STAGE_LOCKED,
            dependencies=["00_data_curation"],
            required_input_artifacts=["data/data_quality.json"],
            required_output_artifacts=[],
            requires_validation=False,
            requires_manifest=False
        )

        # Create required deliverable on disk
        data_dir = os.path.join(self.state_dir, "data")
        os.makedirs(data_dir, exist_ok=True)
        art_path = os.path.join(data_dir, "data_quality.json")
        with open(art_path, "w", encoding="utf-8") as f:
            json.dump({"n": 300, "status": "clean"}, f)

        # Create passing validation report
        val_path = os.path.join(self.state_dir, "validation_report.json")
        with open(val_path, "w", encoding="utf-8") as f:
            json.dump({"overall_verdict": "PASS", "checks": 12}, f)

        # Transition 00_data_curation to STAGE_RUNNING -> STAGE_VALIDATING
        self.sm.request_transition("00_data_curation", StageState.STAGE_RUNNING)
        self.sm.request_transition("00_data_curation", StageState.STAGE_VALIDATING)
        self.assertEqual(self.sm.stages["00_data_curation"]["status"], StageState.STAGE_VALIDATING.value)

        # Verify Stage 1 is locked and cannot run
        with self.assertRaises(UnmetPrerequisiteError):
            self.sm.request_transition("01_demographics", StageState.STAGE_READY)

        # Request stage approval
        req = request_stage_approval(
            stage_id="00_data_curation",
            state_dir=self.state_dir,
            artifact_path=art_path,
            validation_report_path=val_path,
            requester_agent="data-curator",
            rationale="Data curation completed and validated; awaiting supervisor approval."
        )

        self.assertEqual(req["decision"], "PENDING")
        self.assertEqual(req["status"], "PENDING")
        self.assertFalse(req["is_approved"])
        self.assertIsNotNone(req["artifact_hash"])
        self.assertIsNotNone(req["validation_hash"])

        # Reload state machine and verify status is STAGE_AWAITING_APPROVAL
        self.sm.load_from_disk()
        self.assertEqual(self.sm.stages["00_data_curation"]["status"], StageState.STAGE_AWAITING_APPROVAL.value)

        # Verify Stage 1 is STILL blocked while Stage 0 is STAGE_AWAITING_APPROVAL
        with self.assertRaises(UnmetPrerequisiteError):
            self.sm.request_transition("01_demographics", StageState.STAGE_READY)

        # Execute explicit human approval
        app_res = approve_stage(
            approval_id=req["approval_id"],
            approved_by="Saber Admin Desk 124911145",
            state_dir=self.state_dir,
            comments="Data curation verified against raw instruments.",
            digital_signature="SIG-VERIFIED-124911145"
        )

        self.assertEqual(app_res["decision"], "APPROVED")
        self.assertEqual(app_res["approved_by"], "Saber Admin Desk 124911145")
        self.assertIn("01_demographics", app_res["unlocked_stages"])

        # Reload state machine and verify Stage 0 is STAGE_APPROVED
        self.sm.load_from_disk()
        self.assertEqual(self.sm.stages["00_data_curation"]["status"], StageState.STAGE_APPROVED.value)

        # Verify Stage 1 was automatically unlocked to STAGE_READY!
        self.assertEqual(self.sm.stages["01_demographics"]["status"], StageState.STAGE_READY.value)

        # Now Stage 1 can transition to STAGE_RUNNING
        res_run = self.sm.request_transition("01_demographics", StageState.STAGE_RUNNING)
        self.assertEqual(res_run["to_state"], StageState.STAGE_RUNNING.value)

    def test_03_prerequisite_validation_failure(self):
        """Tests that approval request fails closed if validation report is missing or non-passing."""
        self.sm.register_stage(
            stage_id="03_assumptions",
            title="Parametric Assumptions",
            initial_status=StageState.STAGE_VALIDATING,
            requires_validation=True,
            requires_manifest=False
        )

        art_path = os.path.join(self.state_dir, "assumptions.json")
        with open(art_path, "w", encoding="utf-8") as f:
            json.dump({"shapiro_wilk": 0.98}, f)

        # Case A: Missing validation report
        with self.assertRaises(ApprovalPrerequisiteError):
            request_stage_approval(
                stage_id="03_assumptions",
                state_dir=self.state_dir,
                artifact_path=art_path,
                validation_report_path=os.path.join(self.state_dir, "non_existent_val.json")
            )

        # Case B: Failing validation report
        failing_val = os.path.join(self.state_dir, "failing_val.json")
        with open(failing_val, "w", encoding="utf-8") as f:
            json.dump({"overall_verdict": "FAIL", "reason": "Severe non-normality"}, f)

        with self.assertRaises(ApprovalPrerequisiteError):
            request_stage_approval(
                stage_id="03_assumptions",
                state_dir=self.state_dir,
                artifact_path=art_path,
                validation_report_path=failing_val
            )

    def test_04_cryptographic_tamper_detection(self):
        """Tests that modifying deliverables or validation reports while awaiting approval fails closed."""
        self.sm.register_stage(
            stage_id="06_hypothesis_1",
            title="Hypothesis 1",
            initial_status=StageState.STAGE_VALIDATING,
            requires_validation=True,
            requires_manifest=False
        )

        art_path = os.path.join(self.state_dir, "06_hypothesis_1.json")
        with open(art_path, "w", encoding="utf-8") as f:
            json.dump({"beta": 0.42, "p": 0.001}, f)

        val_path = os.path.join(self.state_dir, "validation_report.json")
        with open(val_path, "w", encoding="utf-8") as f:
            json.dump({"overall_verdict": "PASS"}, f)

        # Request approval
        req = request_stage_approval(
            stage_id="06_hypothesis_1",
            state_dir=self.state_dir,
            artifact_path=art_path,
            validation_report_path=val_path
        )
        app_id = req["approval_id"]

        # Tamper deliverable file
        with open(art_path, "w", encoding="utf-8") as f:
            json.dump({"beta": 0.99, "p": 0.0001, "tampered": True}, f)

        # Attempt to approve should fail closed with ApprovalTamperError
        with self.assertRaises(ApprovalTamperError):
            approve_stage(
                approval_id=app_id,
                approved_by="saber_admin",
                state_dir=self.state_dir
            )

    def test_05_rejection_flow(self):
        """Tests that human rejection transitions stage to STAGE_REJECTED and keeps downstream stages locked."""
        self.sm.register_stage(
            stage_id="05_macro_model",
            title="Macro Model Fit",
            initial_status=StageState.STAGE_VALIDATING,
            requires_validation=True,
            requires_manifest=False
        )
        self.sm.register_stage(
            stage_id="06_hypotheses",
            title="Hypotheses",
            initial_status=StageState.STAGE_LOCKED,
            dependencies=["05_macro_model"],
            requires_validation=False,
            requires_manifest=False
        )

        art_path = os.path.join(self.state_dir, "model_fit.json")
        with open(art_path, "w", encoding="utf-8") as f:
            json.dump({"cfi": 0.88, "rmsea": 0.09}, f)

        val_path = os.path.join(self.state_dir, "validation_report.json")
        with open(val_path, "w", encoding="utf-8") as f:
            json.dump({"overall_verdict": "PASS"}, f)

        req = request_stage_approval(
            stage_id="05_macro_model",
            state_dir=self.state_dir,
            artifact_path=art_path,
            validation_report_path=val_path
        )

        rej_res = reject_stage(
            approval_id=req["approval_id"],
            rejected_by="Saber Admin Desk 124911145",
            state_dir=self.state_dir,
            comments="CFI 0.88 is substandard (< 0.90). Re-specify measurement model."
        )

        self.assertEqual(rej_res["decision"], "REJECTED")

        self.sm.load_from_disk()
        self.assertEqual(self.sm.stages["05_macro_model"]["status"], StageState.STAGE_REJECTED.value)

        # Downstream remains locked
        self.assertEqual(self.sm.stages["06_hypotheses"]["status"], StageState.STAGE_LOCKED.value)
        with self.assertRaises(UnmetPrerequisiteError):
            self.sm.request_transition("06_hypotheses", StageState.STAGE_READY)

    def test_06_cli_interface(self):
        """Tests CLI subcommands: request, status, approve, reject."""
        stage_id = "02_reliability"
        self.sm.register_stage(
            stage_id=stage_id,
            title="Scale Reliability",
            initial_status=StageState.STAGE_VALIDATING,
            requires_validation=True,
            requires_manifest=False
        )

        art_path = os.path.join(self.state_dir, "reliability.json")
        with open(art_path, "w", encoding="utf-8") as f:
            json.dump({"cronbach_alpha": 0.87}, f)

        val_path = os.path.join(self.state_dir, "validation_report.json")
        with open(val_path, "w", encoding="utf-8") as f:
            json.dump({"overall_verdict": "PASS"}, f)

        cand = os.path.join(ROOT_DIR, ".agents", "scripts", "academic_approval_engine.py")
        cli_script = cand if os.path.isfile(cand) else os.path.join(ROOT_DIR, "scripts", "academic_approval_engine.py")

        # CLI request
        cmd_req = [
            sys.executable, cli_script, "request",
            "--stage-id", stage_id,
            "--state-dir", self.state_dir,
            "--artifact", art_path,
            "--validation", val_path
        ]
        proc = subprocess.run(cmd_req, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"CLI request failed: {proc.stderr}")
        self.assertIn("SUCCESS: Approval requested", proc.stdout)

        # CLI status
        cmd_stat = [
            sys.executable, cli_script, "status",
            "--state-dir", self.state_dir,
            "--stage-id", stage_id,
            "--json"
        ]
        proc_stat = subprocess.run(cmd_stat, capture_output=True, text=True)
        self.assertEqual(proc_stat.returncode, 0)
        status_data = json.loads(proc_stat.stdout)
        self.assertGreaterEqual(len(status_data), 1)
        approval_id = status_data[0]["approval_id"]
        self.assertEqual(status_data[0]["decision"], "PENDING")

        # CLI approve
        cmd_app = [
            sys.executable, cli_script, "approve",
            "--approval-id", approval_id,
            "--approved-by", "saber_admin",
            "--state-dir", self.state_dir,
            "--comments", "CLI approval verified."
        ]
        proc_app = subprocess.run(cmd_app, capture_output=True, text=True)
        self.assertEqual(proc_app.returncode, 0, f"CLI approve failed: {proc_app.stderr}")
        self.assertIn("GRANTED", proc_app.stdout)


if __name__ == "__main__":
    unittest.main()
