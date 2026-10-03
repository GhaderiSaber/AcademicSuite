#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/architecture/test_current_work_validation_isolation.py

Verifies that lifecycle hooks and validation guards strictly isolate validation report
checks to the active 'current work' stage and do NOT block agents or subagents on
unrelated validation reports elsewhere in the project or workspace.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
for p in (ROOT_DIR, os.path.join(ROOT_DIR, ".agents"), os.path.join(ROOT_DIR, ".agents", "hooks"), os.path.join(ROOT_DIR, ".agents", "contracts")):
    if p not in sys.path:
        sys.path.insert(0, p)

from integrity_hooks import IntegrityHooks
from contracts.current_work_resolver import (
    resolve_current_work_stage_dirs,
    get_current_work_validation_reports,
    is_validation_report_for_current_work
)


class TestCurrentWorkValidationIsolation(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="agy_val_isolation_test_")
        self.workspace = self.temp_dir

        # Create two distinct stages in 03_deliverables
        self.stage1_dir = os.path.join(self.workspace, "03_deliverables", "stage_01_data_audit")
        self.stage2_dir = os.path.join(self.workspace, "03_deliverables", "stage_02_descriptives")
        os.makedirs(self.stage1_dir, exist_ok=True)
        os.makedirs(self.stage2_dir, exist_ok=True)

        # Stage 1 has a FAILING validation report (unrelated past/other work)
        self.stage1_val_path = os.path.join(self.stage1_dir, "validation_report.json")
        with open(self.stage1_val_path, "w", encoding="utf-8") as f:
            json.dump({
                "overall_verdict": "FAIL",
                "checks_failed": 3,
                "evidence_summary": {"checks_failed": 3, "checks_passed": 10},
                "results": [{"validator_name": "AuditCheck", "verdict": "FAIL"}]
            }, f)

        # Stage 2 has a PASSING validation report
        self.stage2_val_path = os.path.join(self.stage2_dir, "validation_report.json")
        with open(self.stage2_val_path, "w", encoding="utf-8") as f:
            json.dump({
                "overall_verdict": "PASS",
                "checks_failed": 0,
                "evidence_summary": {"checks_failed": 0, "checks_passed": 15, "checks_blocked": 0},
                "results": [{"validator_name": "DescCheck", "verdict": "PASS"}]
            }, f)

        # Create a transcript directory
        self.transcript_dir = os.path.join(self.workspace, ".system_generated", "logs")
        os.makedirs(self.transcript_dir, exist_ok=True)
        self.transcript_path = os.path.join(self.transcript_dir, "transcript.jsonl")

    def tearDown(self):
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _write_transcript(self, records):
        with open(self.transcript_path, "w", encoding="utf-8") as f:
            for r in records:
                f.write(json.dumps(r) + "\n")

    def test_current_work_resolver_isolates_stage_from_tool_calls(self):
        """Test that resolve_current_work_stage_dirs identifies only the stage touched by tool calls."""
        records = [
            {"type": "USER_INPUT", "content": "Please write descriptive tables for Stage 2"},
            {
                "type": "PLANNER_RESPONSE",
                "tool_calls": [
                    {
                        "name": "write_to_file",
                        "args": {
                            "TargetFile": os.path.join(self.stage2_dir, "descriptives.md"),
                            "CodeContent": "# Stage 2 Descriptives"
                        }
                    }
                ]
            }
        ]
        self._write_transcript(records)

        payload = {
            "workspacePaths": [self.workspace],
            "transcriptPath": self.transcript_path,
            "caller": "academic-writer"
        }

        stage_dirs = resolve_current_work_stage_dirs(
            workspaces=[self.workspace],
            payload=payload,
            records=records
        )
        self.assertEqual(len(stage_dirs), 1)
        self.assertEqual(os.path.abspath(stage_dirs[0]), os.path.abspath(self.stage2_dir))

    def test_agent_working_on_stage2_is_not_blocked_by_stage1_fail_report(self):
        """Verify that an agent working on stage 2 is allowed to Stop, ignoring stage 1's FAIL report."""
        records = [
            {"type": "USER_INPUT", "content": "Finalize Stage 2 deliverables"},
            {
                "type": "PLANNER_RESPONSE",
                "tool_calls": [
                    {
                        "name": "write_to_file",
                        "args": {
                            "TargetFile": os.path.join(self.stage2_dir, "descriptives.docx"),
                            "CodeContent": "mock docx content"
                        }
                    }
                ]
            }
        ]
        self._write_transcript(records)

        payload = {
            "workspacePaths": [self.workspace],
            "transcriptPath": self.transcript_path,
            "caller": "academic-writer"
        }

        # handle_stop should allow because stage 2's validation report is PASS,
        # even though stage 1 has a FAIL report.
        res = IntegrityHooks.handle_stop(payload)
        self.assertEqual(
            res.get("decision"), "allow",
            f"Expected 'allow' on stage 2 work, but was blocked by unrelated stage 1 report: {res.get('reason')}"
        )

    def test_agent_working_on_stage1_is_strictly_blocked_by_stage1_fail_report(self):
        """Verify that an agent actively modifying stage 1 is blocked because stage 1 has a FAIL report."""
        records = [
            {"type": "USER_INPUT", "content": "Update Stage 1 data audit"},
            {
                "type": "PLANNER_RESPONSE",
                "tool_calls": [
                    {
                        "name": "replace_file_content",
                        "args": {
                            "TargetFile": os.path.join(self.stage1_dir, "data_screening.json"),
                            "Instruction": "Fix screening",
                            "ReplacementContent": "{}"
                        }
                    }
                ]
            }
        ]
        self._write_transcript(records)

        payload = {
            "workspacePaths": [self.workspace],
            "transcriptPath": self.transcript_path,
            "caller": "academic-writer"
        }

        # handle_stop must block because stage 1's validation report is FAIL
        res = IntegrityHooks.handle_stop(payload)
        self.assertEqual(res.get("decision"), "continue")
        self.assertIn("Post-Analysis Validation Gate", res.get("reason", ""))
        self.assertIn("stage_01_data_audit", res.get("reason", ""))

    def test_subagent_cde_prompt_isolates_target_stage(self):
        """Verify that subagent descriptor prompt isolates current work to target stage."""
        subagent_cde = json.dumps({
            "contract_version": "1.0.0",
            "task_id": "TSK-002",
            "worker_agent": "statistics-agent",
            "stage_dir": self.stage2_dir,
            "required_artifacts": [os.path.join(self.stage2_dir, "descriptives.json")]
        })

        payload = {
            "workspacePaths": [self.workspace],
            "caller": "statistics-agent",
            "subagentDescriptor": {
                "typeName": "statistics-agent",
                "role": "Statistical Analyst",
                "prompt": subagent_cde
            }
        }

        stage_dirs = resolve_current_work_stage_dirs(
            workspaces=[self.workspace],
            payload=payload
        )
        self.assertEqual(len(stage_dirs), 1)
        self.assertEqual(os.path.abspath(stage_dirs[0]), os.path.abspath(self.stage2_dir))

        # Check that stop verification passes since stage 2 is PASS
        res = IntegrityHooks.handle_stop(payload)
        self.assertEqual(res.get("decision"), "allow")

    def test_non_deliverable_work_is_never_blocked_by_unrelated_validation_reports(self):
        """Verify that general tasks (editing scripts, answering questions) are never blocked by deliverable reports."""
        script_dir = os.path.join(self.workspace, "scripts")
        os.makedirs(script_dir, exist_ok=True)
        script_file = os.path.join(script_dir, "helper.py")

        records = [
            {"type": "USER_INPUT", "content": "Please write a helper script for calculations"},
            {
                "type": "PLANNER_RESPONSE",
                "tool_calls": [
                    {
                        "name": "write_to_file",
                        "args": {
                            "TargetFile": script_file,
                            "CodeContent": "def add(a, b): return a + b"
                        }
                    }
                ]
            }
        ]
        self._write_transcript(records)

        payload = {
            "workspacePaths": [self.workspace],
            "transcriptPath": self.transcript_path,
            "caller": "default"
        }

        stage_dirs = resolve_current_work_stage_dirs(
            workspaces=[self.workspace],
            payload=payload,
            records=records
        )
        # Non-deliverable work must resolve to no deliverable stage directories
        self.assertEqual(stage_dirs, [])

        # verify_post_analysis should pass without blocking
        ok, reason = IntegrityHooks.verify_post_analysis([self.workspace], caller="academic-orchestrator", payload=payload)
        self.assertTrue(ok)
        self.assertEqual(reason, "")

    def test_run_command_stage_dir_argument_isolates_current_work(self):
        """Verify that run_command with --stage-dir isolates current work."""
        records = [
            {"type": "USER_INPUT", "content": "Run validation on Stage 2"},
            {
                "type": "PLANNER_RESPONSE",
                "tool_calls": [
                    {
                        "name": "run_command",
                        "args": {
                            "CommandLine": f"python3 .agents/validators/run_all_validators.py --stage-dir {self.stage2_dir}",
                            "Cwd": self.workspace
                        }
                    }
                ]
            }
        ]
        self._write_transcript(records)

        payload = {
            "workspacePaths": [self.workspace],
            "transcriptPath": self.transcript_path,
            "caller": "academic-orchestrator"
        }

        stage_dirs = resolve_current_work_stage_dirs(
            workspaces=[self.workspace],
            payload=payload,
            records=records
        )
        self.assertEqual(len(stage_dirs), 1)
        self.assertEqual(os.path.abspath(stage_dirs[0]), os.path.abspath(self.stage2_dir))

    def test_detect_validation_failure_ignores_unrelated_stages(self):
        """Verify that detect_validation_failure only inspects current work stages."""
        records = [
            {"type": "USER_INPUT", "content": "Review Stage 2"},
            {
                "type": "PLANNER_RESPONSE",
                "tool_calls": [
                    {
                        "name": "view_file",
                        "args": {"AbsolutePath": os.path.join(self.stage2_dir, "descriptives.md")}
                    }
                ]
            }
        ]
        self._write_transcript(records)

        is_fail, summary = IntegrityHooks.detect_validation_failure(
            records=records,
            workspaces=[self.workspace]
        )
        # Because the active records touched stage 2 (which is PASS),
        # detect_validation_failure must NOT report failure despite stage 1's FAIL report on disk.
        self.assertFalse(is_fail)
        self.assertEqual(summary, "")


if __name__ == "__main__":
    unittest.main()
