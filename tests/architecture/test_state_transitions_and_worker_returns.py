#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/architecture/test_state_transitions_and_worker_returns.py — Architecture Verification for Phase 21

Verifies Phase 21 mandates:
1. Strict sequential state machine progression:
   LOCKED -> READY -> RUNNING -> VALIDATING -> AWAITING_APPROVAL -> APPROVED -> NEXT_STAGE
2. Orchestrator cannot bypass workflow states simply because it has a tool:
   - Cannot bypass LOCKED -> RUNNING or LOCKED -> APPROVED
   - Cannot bypass READY -> VALIDATING or READY -> APPROVED
   - Cannot bypass RUNNING -> AWAITING_APPROVAL or RUNNING -> APPROVED
   - Cannot bypass VALIDATING -> APPROVED (must pass through AWAITING_APPROVAL)
   - Cannot advance to NEXT_STAGE unless current stage is STAGE_APPROVED
3. Worker return payload invariant:
   - Worker must return: artifact, evidence, status, validation
   - Plain string returns like 'done', 'completed', 'finished' are strictly REJECTED
   - Missing any of the 4 mandatory blocks raises InvalidWorkerReturnError
4. Advancing to NEXT_STAGE unlocks downstream dependent stages to STAGE_READY
5. Secondary enforcement hooks detect and deny trivial returns and invalid transitions
"""

import os
import sys
import json
import shutil
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.academic_state_manager import (
    StrictStateMachine,
    StageState,
    STAGE_LEGAL_TRANSITIONS,
    InvalidStateTransitionError,
    InvalidWorkerReturnError,
    MissingApprovalError,
    advance_to_next_stage,
)
from validators.worker_return_validator import (
    validate_worker_return_payload,
    WorkerReturnValidationError,
)
hooks_dir = os.path.join(ROOT_DIR, ".agents", "hooks")
if hooks_dir not in sys.path:
    sys.path.insert(0, hooks_dir)

from safety_hooks import SafetyHooks
from integrity_hooks import IntegrityHooks


class TestStateTransitionsAndWorkerReturns(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix='phase21_test_')
        self.state_dir = os.path.join(self.temp_dir, 'academic-state')
        os.makedirs(self.state_dir, exist_ok=True)
        self.sm = StrictStateMachine(state_dir=self.state_dir, project_id='phase21_study')

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # 1. Full Happy Path: LOCKED -> READY -> RUNNING -> VALIDATING ->
    #                     AWAITING_APPROVAL -> APPROVED -> NEXT_STAGE
    # -------------------------------------------------------------------------
    def test_01_full_sequential_progression_happy_path(self):
        """Tests the complete 7-step sequence ending with NEXT_STAGE."""
        self.sm.register_stage(
            stage_id='stage_01',
            title='Demographics',
            initial_status=StageState.STAGE_LOCKED,
            dependencies=[],
            requires_validation=False,
            requires_manifest=False
        )
        self.sm.register_stage(
            stage_id='stage_02',
            title='Reliability',
            initial_status=StageState.STAGE_LOCKED,
            dependencies=['stage_01'],
            requires_validation=False,
            requires_manifest=False
        )

        # 1. LOCKED -> READY
        r1 = self.sm.request_transition('stage_01', StageState.STAGE_READY, rationale='Inputs verified')
        self.assertEqual(r1['to_state'], StageState.STAGE_READY.value)
        self.assertEqual(self.sm.stages['stage_01']['status'], StageState.STAGE_READY.value)

        # 2. READY -> RUNNING
        r2 = self.sm.request_transition('stage_01', StageState.STAGE_RUNNING, rationale='Worker started')
        self.assertEqual(r2['to_state'], StageState.STAGE_RUNNING.value)
        self.assertEqual(self.sm.stages['stage_01']['status'], StageState.STAGE_RUNNING.value)

        # 3. RUNNING -> VALIDATING (with compliant worker return)
        valid_worker_payload = {
            'status': 'SUCCESS',
            'artifact': ['outputs/demographics.docx', 'outputs/demographics.json'],
            'evidence': {'n_total': 300, 'female_pct': 58.3, 'mean_age': 34.2},
            'validation': {'verdict': 'PASS', 'checks_passed': 6, 'checks_failed': 0}
        }
        r3 = self.sm.request_transition(
            'stage_01',
            StageState.STAGE_VALIDATING,
            worker_return=valid_worker_payload,
            rationale='Worker completed computation and produced outputs'
        )
        self.assertEqual(r3['to_state'], StageState.STAGE_VALIDATING.value)
        self.assertEqual(self.sm.stages['stage_01']['status'], StageState.STAGE_VALIDATING.value)
        self.assertIn('worker_return', self.sm.stages['stage_01'])

        # 4. VALIDATING -> AWAITING_APPROVAL
        r4 = self.sm.request_transition('stage_01', StageState.STAGE_AWAITING_APPROVAL, rationale='Validation passed')
        self.assertEqual(r4['to_state'], StageState.STAGE_AWAITING_APPROVAL.value)
        self.assertEqual(self.sm.stages['stage_01']['status'], StageState.STAGE_AWAITING_APPROVAL.value)

        # Verify stage_02 is strictly LOCKED while stage_01 is awaiting approval
        self.assertEqual(self.sm.stages['stage_02']['status'], StageState.STAGE_LOCKED.value)

        # 5. Grant human approval
        appr = self.sm.request_approval('stage_01', 'DELIVERABLE', 'academic-orchestrator', 'Stage 1 verified')
        self.sm.grant_approval(appr['approval_id'], 'admin_124911145', 'valid_signature_hash')

        # 6. AWAITING_APPROVAL -> APPROVED
        r5 = self.sm.request_transition('stage_01', StageState.STAGE_APPROVED, check_artifacts=False)
        self.assertEqual(r5['to_state'], StageState.STAGE_APPROVED.value)
        self.assertEqual(self.sm.stages['stage_01']['status'], StageState.STAGE_APPROVED.value)

        # 7. APPROVED -> NEXT_STAGE
        r6 = self.sm.advance_to_next_stage('stage_01')
        self.assertEqual(r6['to_state'], StageState.NEXT_STAGE.value)
        self.assertEqual(r6['next_stage_id'], 'stage_02')
        self.assertEqual(r6['next_stage_status'], StageState.STAGE_READY.value)
        # Stage 02 is now unlocked to STAGE_READY
        self.assertEqual(self.sm.stages['stage_02']['status'], StageState.STAGE_READY.value)

    # -------------------------------------------------------------------------
    # 2. Negative Tests: Orchestrator Cannot Bypass States
    # -------------------------------------------------------------------------
    def test_02_cannot_bypass_locked_directly_to_running(self):
        """Attempting LOCKED -> RUNNING raises InvalidStateTransitionError."""
        self.sm.register_stage('s_test', 'Test Stage', initial_status=StageState.STAGE_LOCKED)
        with self.assertRaises(InvalidStateTransitionError):
            self.sm.request_transition('s_test', StageState.STAGE_RUNNING)

    def test_03_cannot_bypass_locked_directly_to_approved(self):
        """Attempting LOCKED -> APPROVED raises InvalidStateTransitionError."""
        self.sm.register_stage('s_test', 'Test Stage', initial_status=StageState.STAGE_LOCKED)
        with self.assertRaises(InvalidStateTransitionError):
            self.sm.request_transition('s_test', StageState.STAGE_APPROVED)

    def test_04_cannot_bypass_ready_directly_to_validating(self):
        """Attempting READY -> VALIDATING raises InvalidStateTransitionError."""
        self.sm.register_stage('s_test', 'Test Stage', initial_status=StageState.STAGE_READY)
        with self.assertRaises(InvalidStateTransitionError):
            self.sm.request_transition('s_test', StageState.STAGE_VALIDATING)

    def test_05_cannot_bypass_ready_directly_to_approved(self):
        """Attempting READY -> APPROVED raises InvalidStateTransitionError."""
        self.sm.register_stage('s_test', 'Test Stage', initial_status=StageState.STAGE_READY)
        with self.assertRaises(InvalidStateTransitionError):
            self.sm.request_transition('s_test', StageState.STAGE_APPROVED)

    def test_06_cannot_bypass_running_directly_to_awaiting_approval(self):
        """Attempting RUNNING -> AWAITING_APPROVAL raises InvalidStateTransitionError."""
        self.sm.register_stage('s_test', 'Test Stage', initial_status=StageState.STAGE_RUNNING)
        with self.assertRaises(InvalidStateTransitionError):
            self.sm.request_transition('s_test', StageState.STAGE_AWAITING_APPROVAL)

    def test_07_cannot_bypass_running_directly_to_approved(self):
        """Attempting RUNNING -> APPROVED raises InvalidStateTransitionError."""
        self.sm.register_stage('s_test', 'Test Stage', initial_status=StageState.STAGE_RUNNING)
        with self.assertRaises(InvalidStateTransitionError):
            self.sm.request_transition('s_test', StageState.STAGE_APPROVED)

    def test_08_cannot_bypass_validating_directly_to_approved(self):
        """Attempting VALIDATING -> APPROVED without AWAITING_APPROVAL raises InvalidStateTransitionError."""
        self.sm.register_stage('s_test', 'Test Stage', initial_status=StageState.STAGE_VALIDATING)
        with self.assertRaises(InvalidStateTransitionError):
            self.sm.request_transition('s_test', StageState.STAGE_APPROVED)

    def test_09_cannot_advance_to_next_stage_when_not_approved(self):
        """Calling advance_to_next_stage when stage is not STAGE_APPROVED raises InvalidStateTransitionError."""
        unapproved_states = [
            StageState.STAGE_LOCKED,
            StageState.STAGE_READY,
            StageState.STAGE_RUNNING,
            StageState.STAGE_VALIDATING,
            StageState.STAGE_AWAITING_APPROVAL,
            StageState.STAGE_FAILED,
            StageState.STAGE_REJECTED,
        ]
        for st in unapproved_states:
            stage_id = f"stage_{st.value.lower()}"
            self.sm.register_stage(stage_id, 'Test', initial_status=st)
            with self.assertRaises(InvalidStateTransitionError):
                self.sm.advance_to_next_stage(stage_id)

    # -------------------------------------------------------------------------
    # 3. Worker Return Structure Invariant (artifact, evidence, status, validation)
    # -------------------------------------------------------------------------
    def test_10_worker_return_rejects_plain_string_done(self):
        """Worker returning simply 'done' is rejected with InvalidWorkerReturnError."""
        self.sm.register_stage('s_worker', 'Worker Stage', initial_status=StageState.STAGE_RUNNING, requires_validation=False)
        with self.assertRaises(InvalidWorkerReturnError) as cm:
            self.sm.request_transition('s_worker', StageState.STAGE_VALIDATING, worker_return='done', check_artifacts=False)
        self.assertIn('TRIVIAL WORKER RETURN DETECTED', str(cm.exception))

    def test_11_worker_return_rejects_other_trivial_strings(self):
        """Worker returning 'completed', 'finished', etc. is strictly rejected."""
        self.sm.register_stage('s_worker_2', 'Worker Stage', initial_status=StageState.STAGE_RUNNING, requires_validation=False)
        for trivial in ['completed', 'finished', 'all done', 'ok']:
            with self.assertRaises(InvalidWorkerReturnError):
                self.sm.request_transition('s_worker_2', StageState.STAGE_VALIDATING, worker_return=trivial, check_artifacts=False)

    def test_12_worker_return_rejects_missing_artifact(self):
        """Worker return missing 'artifact' is rejected."""
        payload = {
            'status': 'SUCCESS',
            'evidence': {'t': 3.12, 'p': 0.002},
            'validation': {'verdict': 'PASS'}
        }
        with self.assertRaises(WorkerReturnValidationError):
            validate_worker_return_payload(payload, fail_closed=True)

    def test_13_worker_return_rejects_missing_evidence(self):
        """Worker return missing 'evidence' is rejected."""
        payload = {
            'status': 'SUCCESS',
            'artifact': ['outputs/results.json'],
            'validation': {'verdict': 'PASS'}
        }
        with self.assertRaises(WorkerReturnValidationError):
            validate_worker_return_payload(payload, fail_closed=True)

    def test_14_worker_return_rejects_missing_status(self):
        """Worker return missing 'status' is rejected."""
        payload = {
            'artifact': ['outputs/results.json'],
            'evidence': {'t': 3.12, 'p': 0.002},
            'validation': {'verdict': 'PASS'}
        }
        with self.assertRaises(WorkerReturnValidationError):
            validate_worker_return_payload(payload, fail_closed=True)

    def test_15_worker_return_rejects_missing_validation(self):
        """Worker return missing 'validation' is rejected."""
        payload = {
            'status': 'SUCCESS',
            'artifact': ['outputs/results.json'],
            'evidence': {'t': 3.12, 'p': 0.002}
        }
        with self.assertRaises(WorkerReturnValidationError):
            validate_worker_return_payload(payload, fail_closed=True)

    def test_16_worker_return_accepts_complete_structured_payload(self):
        """Worker return containing all 4 required blocks is accepted and validated."""
        payload = {
            'status': 'SUCCESS',
            'artifact': ['outputs/ch4_hypothesis_1.docx', 'outputs/ch4_hypothesis_1.json'],
            'evidence': {'F': 5.21, 'df': [1, 58], 'p': 0.026, 'partial_eta_sq': 0.082},
            'validation': {'verdict': 'PASS', 'overall_verdict': 'PASS', 'checks_passed': 12, 'checks_failed': 0}
        }
        res = validate_worker_return_payload(payload, fail_closed=True)
        self.assertTrue(res['valid'])
        self.assertEqual(res['errors'], [])

    # -------------------------------------------------------------------------
    # 4. Secondary Hook Enforcement for Worker Returns & State Transitions
    # -------------------------------------------------------------------------
    def test_17_safety_hook_denies_send_message_with_trivial_done(self):
        """Safety hook intercepts send_message containing simply 'done'."""
        res = SafetyHooks.handle_pre_tool_use({
            'toolCall': {
                'name': 'send_message',
                'args': {'Recipient': 'academic-orchestrator', 'Message': 'done'}
            }
        })
        self.assertEqual(res['decision'], 'deny')
        self.assertIn('Worker Return Invariant', res['reason'])

    def test_18_integrity_hook_flags_trivial_worker_return_in_state(self):
        """Integrity hook flags invalid worker return in current_state.json."""
        cs_file = os.path.join(self.state_dir, 'current_state.json')
        with open(cs_file, 'w', encoding='utf-8') as f:
            json.dump({
                'stages': {
                    's_corrupt': {
                        'status': 'STAGE_VALIDATING',
                        'worker_return': 'done'
                    }
                }
            }, f)
        ok, reason = IntegrityHooks.verify_worker_returns([self.temp_dir])
        self.assertFalse(ok)
        self.assertIn('Worker Return Invariant Guard', reason)

    def test_19_advance_stage_cli_advances_approved_stage(self):
        """CLI advance-stage subcommand advances approved stage to NEXT_STAGE."""
        import subprocess
        self.sm.register_stage('stage_01', 'Stage 1', initial_status=StageState.STAGE_APPROVED, dependencies=[], requires_validation=False)
        self.sm.register_stage('stage_02', 'Stage 2', initial_status=StageState.STAGE_LOCKED, dependencies=['stage_01'], requires_validation=False)

        cand = os.path.join(ROOT_DIR, '.agents', 'scripts', 'academic_state_manager.py')
        state_mgr_path = cand if os.path.isfile(cand) else os.path.join(ROOT_DIR, 'scripts', 'academic_state_manager.py')
        cmd = [
            sys.executable,
            state_mgr_path,
            'advance-stage',
            self.temp_dir,
            '--stage', 'stage_01',
            '--actor', 'academic-orchestrator'
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, f"STDOUT: {proc.stdout}, STDERR: {proc.stderr}")
        sm_reloaded = StrictStateMachine(state_dir=self.state_dir, project_id='phase21_study')
        self.assertEqual(sm_reloaded.stages['stage_02']['status'], StageState.STAGE_READY.value)

    def test_20_worker_return_via_cli_rejects_done(self):
        """CLI request-transition rejects --worker-return 'done'."""
        import subprocess
        self.sm.register_stage('stage_01', 'Stage 1', initial_status=StageState.STAGE_RUNNING, requires_validation=False)
        cand = os.path.join(ROOT_DIR, '.agents', 'scripts', 'academic_state_manager.py')
        state_mgr_path = cand if os.path.isfile(cand) else os.path.join(ROOT_DIR, 'scripts', 'academic_state_manager.py')
        cmd = [
            sys.executable,
            state_mgr_path,
            'request-transition',
            self.temp_dir,
            '--target-id', 'stage_01',
            '--to-state', 'STAGE_VALIDATING',
            '--worker-return', 'done'
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn('InvalidWorkerReturnError', proc.stderr + proc.stdout)


if __name__ == '__main__':
    unittest.main()
