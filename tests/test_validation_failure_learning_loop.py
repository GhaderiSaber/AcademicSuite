#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_validation_failure_learning_loop.py

Comprehensive test suite verifying that validation failures (overall_verdict: FAIL or checks_failed > 0)
mechanically trigger the 5-stage continuous learning loop and block premature remediation:
1. is_validation_failure_active detects FAIL from transcript messages and on-disk reports.
2. academic-orchestrator guard blocks execution delivery workers (PreToolUse) under active validation failure.
3. academic-orchestrator guard allows learning subagents (trajectory-analyzer, etc.).
4. academic-orchestrator guard blocks Stop when validation failure is unhandled by the learning cascade.
5. academic-orchestrator guard allows execution workers once evaluation-agent has run and candidates are graduated.
6. IntegrityHooks.verify_learning_pipeline_completion enforces learning cascade on validation failure.
7. LearningHooks.detect_recent_validation_failure detects failures and injects the imperative learning mandate.
8. run_all_validators records validation failures upon non-PASS outcomes.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
from unittest.mock import patch, MagicMock

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
if AGENTS_DIR not in sys.path:
    sys.path.insert(0, AGENTS_DIR)
HOOKS_DIR = os.path.join(AGENTS_DIR, "hooks")
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)

import importlib.util

# Load academic-orchestrator guard
guard_path = os.path.join(AGENTS_DIR, "agents", "academic-orchestrator", "guard.py")
spec = importlib.util.spec_from_file_location("orch_guard_test_module", guard_path)
orch_guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(orch_guard)

from integrity_hooks import IntegrityHooks
from learning_hooks import LearningHooks


class TestValidationFailureLearningLoop(unittest.TestCase):

    def setUp(self):
        self.tmp_dir = tempfile.mkdtemp(prefix="val_fail_test_")
        self.deliv_dir = os.path.join(self.tmp_dir, "03_deliverables")
        os.makedirs(self.deliv_dir, exist_ok=True)
        self.state_dir = os.path.join(self.tmp_dir, "state")
        os.makedirs(self.state_dir, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.tmp_dir, ignore_errors=True)

    def test_01_is_validation_failure_active_from_transcript_fail_message(self):
        """Transcript message from validation-agent with overall_verdict: FAIL triggers detection."""
        records = [
            {"type": "USER_INPUT", "content": "Please validate stage D.1"},
            {"type": "PLANNER_RESPONSE", "content": "Delegating to validation-agent", "tool_calls": [
                {"name": "invoke_subagent", "args": {"Subagents": [{"TypeName": "validation-agent"}]}}
            ]},
            {
                "type": "GENERIC",
                "source": "SYSTEM_MESSAGE",
                "content": "The run_all_validators.py output validation_report.json states an overall_verdict of FAIL. There are 11 total checks_failed."
            }
        ]
        is_active, summary, _ = orch_guard.is_validation_failure_active(records, [self.tmp_dir])
        self.assertTrue(is_active)
        self.assertIn("FAIL", summary)
        self.assertIn("11", summary)

    def test_02_is_validation_failure_active_from_transcript_pass_message(self):
        """Transcript message with overall_verdict: PASS and checks_failed: 0 does not trigger failure."""
        records = [
            {"type": "USER_INPUT", "content": "Please validate stage D.1"},
            {
                "type": "GENERIC",
                "source": "SYSTEM_MESSAGE",
                "content": "The run_all_validators.py output validation_report.json states an overall_verdict of PASS. checks_failed: 0."
            }
        ]
        is_active, summary, _ = orch_guard.is_validation_failure_active(records, [self.tmp_dir])
        self.assertFalse(is_active)

    def test_03_is_validation_failure_active_from_disk_report(self):
        """On-disk validation_report.json with overall_verdict: FAIL triggers detection."""
        report_path = os.path.join(self.deliv_dir, "validation_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump({
                "overall_verdict": "FAIL",
                "evidence_summary": {"checks_failed": 8}
            }, f)

        records = [
            {"type": "USER_INPUT", "content": "Continue work"}
        ]
        is_active, summary, _ = orch_guard.is_validation_failure_active(records, [self.tmp_dir])
        self.assertTrue(is_active)
        self.assertIn("FAIL", summary)
        self.assertIn("8", summary)

    def test_04_orchestrator_guard_blocks_delivery_worker_under_validation_failure(self):
        """academic-orchestrator PreToolUse denies invoking academic-writer before learning cascade completes."""
        transcript_path = os.path.join(self.tmp_dir, "transcript.jsonl")
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(json.dumps({"type": "USER_INPUT", "content": "Generate the thesis"}) + "\n")
            f.write(json.dumps({
                "type": "GENERIC",
                "source": "SYSTEM_MESSAGE",
                "content": "validation_report.json overall_verdict: FAIL. 5 total checks_failed."
            }) + "\n")

        payload = {
            "caller": "academic-orchestrator",
            "transcriptPath": transcript_path,
            "workspacePaths": [self.tmp_dir],
            "toolCall": {
                "name": "invoke_subagent",
                "args": {
                    "Subagents": [
                        {
                            "TypeName": "academic-writer",
                            "Prompt": "Please remediate the table formatting in 01_defense_storyboard.docx"
                        }
                    ]
                }
            }
        }

        res = orch_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Validation failure is active", res.get("reason", ""))
        self.assertIn("AP-2026-PATCHING-WITHOUT-LEARNING", res.get("reason", ""))

    def test_05_orchestrator_guard_allows_learning_subagents_under_validation_failure(self):
        """academic-orchestrator PreToolUse allows trajectory-analyzer, behavior-analyst, etc."""
        transcript_path = os.path.join(self.tmp_dir, "transcript.jsonl")
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(json.dumps({"type": "USER_INPUT", "content": "Generate the thesis"}) + "\n")
            f.write(json.dumps({
                "type": "GENERIC",
                "source": "SYSTEM_MESSAGE",
                "content": "validation_report.json overall_verdict: FAIL. 5 total checks_failed."
            }) + "\n")

        for learning_agent in ("trajectory-analyzer", "behavior-analyst", "knowledge-curator", "skill-evolver", "evaluation-agent"):
            payload = {
                "caller": "academic-orchestrator",
                "transcriptPath": transcript_path,
                "workspacePaths": [self.tmp_dir],
                "toolCall": {
                    "name": "invoke_subagent",
                    "args": {
                        "Subagents": [
                            {
                                "TypeName": learning_agent,
                                "Prompt": f"Diagnose and evolve against the validation failure"
                            }
                        ]
                    }
                }
            }
            res = orch_guard.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "allow", f"Failed to allow {learning_agent}")

    def test_06_orchestrator_guard_blocks_stop_when_validation_failed_and_learning_uninvoked(self):
        """academic-orchestrator Stop hook returns 'continue' if validation failed but learning cascade was not run."""
        transcript_path = os.path.join(self.tmp_dir, "transcript.jsonl")
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(json.dumps({"type": "USER_INPUT", "content": "Continue with stage D.1"}) + "\n")
            f.write(json.dumps({
                "type": "GENERIC",
                "source": "SYSTEM_MESSAGE",
                "content": "The validation_report.json states an overall_verdict of FAIL with 4 checks_failed."
            }) + "\n")
            f.write(json.dumps({
                "type": "PLANNER_RESPONSE",
                "content": "I noticed the validation failed. I will now examine the files directly."
            }) + "\n")

        payload = {
            "caller": "academic-orchestrator",
            "transcriptPath": transcript_path,
            "workspacePaths": [self.tmp_dir]
        }

        res = orch_guard.handle_stop(payload)
        self.assertEqual(res.get("decision"), "continue")
        self.assertIn("Uninvoked Learning Pipeline on Validation Failure", res.get("reason", ""))
        self.assertIn("trajectory-analyzer", res.get("reason", ""))

    def test_07_orchestrator_guard_allows_delivery_worker_after_evaluation_and_graduation(self):
        """After evaluation-agent has completed and candidates are graduated, delivery workers are permitted."""
        transcript_path = os.path.join(self.tmp_dir, "transcript.jsonl")
        with open(transcript_path, "w", encoding="utf-8") as f:
            f.write(json.dumps({"type": "USER_INPUT", "content": "Fix the chapter"}) + "\n")
            f.write(json.dumps({
                "type": "GENERIC",
                "source": "SYSTEM_MESSAGE",
                "content": "validation_report.json overall_verdict: FAIL. 3 checks_failed."
            }) + "\n")
            f.write(json.dumps({
                "type": "PLANNER_RESPONSE",
                "content": "Dispatching learning cascade",
                "tool_calls": [
                    {"name": "invoke_subagent", "args": {"Subagents": [{"TypeName": "trajectory-analyzer"}]}},
                    {"name": "invoke_subagent", "args": {"Subagents": [{"TypeName": "behavior-analyst"}]}},
                    {"name": "invoke_subagent", "args": {"Subagents": [{"TypeName": "knowledge-curator"}]}},
                    {"name": "invoke_subagent", "args": {"Subagents": [{"TypeName": "skill-evolver"}]}},
                    {"name": "invoke_subagent", "args": {"Subagents": [{"TypeName": "evaluation-agent"}]}}
                ]
            }) + "\n")

        cde_prompt = (
            "```json\n"
            "{\n"
            '  "task_id": "TSK-REMEDIATION-001",\n'
            '  "worker_agent": "academic-writer",\n'
            '  "stage": "03_deliverables",\n'
            '  "objective": "Remediate formatting using evolved tools",\n'
            '  "inputs": ["03_deliverables/doc.docx"],\n'
            '  "required_artifacts": ["03_deliverables/doc.docx"]\n'
            "}\n"
            "```\n"
        )
        payload = {
            "caller": "academic-orchestrator",
            "transcriptPath": transcript_path,
            "workspacePaths": [self.tmp_dir],
            "toolCall": {
                "name": "invoke_subagent",
                "args": {
                    "Subagents": [
                        {
                            "TypeName": "academic-writer",
                            "Prompt": cde_prompt
                        }
                    ]
                }
            }
        }

        res = orch_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "allow")

    def test_08_integrity_hooks_detects_validation_failure_and_blocks_stop(self):
        """IntegrityHooks.verify_learning_pipeline_completion returns False when validation failed and cascade not run."""
        records = [
            {"type": "USER_INPUT", "content": "Please inspect deliverables"},
            {"type": "GENERIC", "content": "validation_report.json overall_verdict: FAIL. 7 checks_failed."}
        ]
        ok, reason = IntegrityHooks.verify_learning_pipeline_completion(records, workspaces=[self.tmp_dir])
        self.assertFalse(ok)
        self.assertIn("Validation Failure", reason)
        self.assertIn("trajectory-analyzer", reason)

    def test_09_learning_hooks_detect_recent_validation_failure_and_injects_mandate(self):
        """LearningHooks.handle_pre_invocation injects CONTINUOUS LEARNING TRIGGER ACTIVE (VALIDATION_FAILED)."""
        report_path = os.path.join(self.deliv_dir, "validation_report.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump({
                "overall_verdict": "FAIL",
                "evidence_summary": {"checks_failed": 10},
                "results": [{"validator_name": "TestValidator", "verdict": "FAIL", "failed_checks": ["chk_1"]}]
            }, f)

        payload = {
            "caller": "academic-orchestrator",
            "workspacePaths": [self.tmp_dir],
            "userMessage": "Please check progress"
        }

        res = LearningHooks.handle_pre_invocation(payload)
        injected = [s.get("ephemeralMessage", "") for s in res.get("injectSteps", [])]
        combined = "\n".join(injected)

        self.assertIn("CONTINUOUS LEARNING TRIGGER ACTIVE (VALIDATION_FAILED)", combined)
        self.assertIn("trajectory-analyzer", combined)
        self.assertIn("behavior-analyst", combined)
        self.assertIn("skill-evolver", combined)

    def test_10_capture_validation_failure_creates_trajectory_event(self):
        """LearningHooks.capture_validation_failure creates VALIDATION_FAILED event in state/trajectory_events.jsonl."""
        validator_results = [
            {"validator_name": "APA7Validator", "verdict": "FAIL", "failed_checks": ["p_value_leading_zero"]}
        ]
        LearningHooks.capture_validation_failure(stage_dir=self.deliv_dir, validator_results=validator_results)
        events_file = os.path.join(self.state_dir, "trajectory_events.jsonl")
        self.assertTrue(os.path.isfile(events_file), "trajectory_events.jsonl was not created")
        with open(events_file, "r", encoding="utf-8") as f:
            events = [json.loads(line) for line in f if line.strip()]
        self.assertTrue(any(e.get("event_type") == "VALIDATION_FAILED" for e in events))


if __name__ == "__main__":
    unittest.main()
