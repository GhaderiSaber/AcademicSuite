#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_lifecycle_hooks.py — Comprehensive tests for Antigravity lifecycle hooks
Tests:
1. PreToolUse: Raw-data immutability guard
2. Stop: Required validation & Triad artifact gate
3. PostToolUse: Audit event logging to .agents/memory/audit_log.jsonl
"""
import os
import sys
import json
import unittest
import tempfile
import shutil

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, ".agents", "verification"))
import transcript_and_rule_guard as guard

class TestLifecycleHooks(unittest.TestCase):

    def test_01_raw_data_protection_write(self):
        """PreToolUse must block writes to raw data paths."""
        raw_paths = [
            "projects/study_act_burnout/01_raw_inputs/data_raw.xlsx",
            "data/raw/survey.sav",
            "/home/user/workspace/01_raw/input.csv",
            "projects/test/raw_data.xlsx"
        ]
        for p in raw_paths:
            payload = {
                "toolCall": {
                    "name": "write_to_file",
                    "args": {"TargetFile": p}
                },
                "workspacePaths": [ROOT]
            }
            res = guard.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "deny", f"Failed to deny write to: {p}")
            self.assertIn("Raw-Data", res.get("reason", ""))

    def test_02_clean_data_write_allowed(self):
        """PreToolUse must allow writes to analytical and code files."""
        allowed_paths = [
            "projects/study_act_burnout/02_analysis_code/clean.py",
            "data_cleaned.xlsx",
            "data_scored.xlsx",
            "projects/study_act_burnout/03_deliverables/stats_results.json"
        ]
        for p in allowed_paths:
            payload = {
                "toolCall": {
                    "name": "write_to_file",
                    "args": {"TargetFile": p}
                },
                "workspacePaths": [ROOT]
            }
            res = guard.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "allow", f"Incorrectly denied write to: {p}")

    def test_03_raw_data_protection_command(self):
        """PreToolUse must block commands targeting raw data."""
        destructive_cmds = [
            "rm -f projects/study_act_burnout/01_raw_inputs/data_raw.xlsx",
            "mv data/raw/survey.sav data/raw/survey_old.sav",
            "echo '' > projects/01_raw_inputs/data_raw.xlsx",
            "sed -i 's/1/2/' data/raw_data.csv"
        ]
        for cmd in destructive_cmds:
            payload = {
                "toolCall": {
                    "name": "run_command",
                    "args": {"CommandLine": cmd}
                },
                "workspacePaths": [ROOT]
            }
            res = guard.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "deny", f"Failed to deny command: {cmd}")

    def test_04_audit_logging(self):
        """PostToolUse must append an event record to audit_log.jsonl."""
        audit_file = os.path.join(ROOT, ".agents", "memory", "audit_log.jsonl")
        if os.path.exists(audit_file):
            os.remove(audit_file)

        payload = {
            "conversationId": "test-convo-999",
            "stepIdx": 105,
            "error": None,
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": "python3 script.py", "WaitMsBeforeAsync": 1000}
            },
            "workspacePaths": [ROOT]
        }
        res = guard.handle_post_tool_use(payload)
        self.assertEqual(res, {})
        self.assertTrue(os.path.exists(audit_file), "audit_log.jsonl was not created")

        with open(audit_file, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f if l.strip()]
        self.assertGreaterEqual(len(lines), 1)
        entry = json.loads(lines[-1])
        self.assertEqual(entry["conversation_id"], "test-convo-999")
        self.assertEqual(entry["tool_name"], "run_command")
        self.assertEqual(entry["status"], "SUCCESS")

    def test_05_triad_artifact_stop_gate(self):
        """Stop hook must block completion if a stage has incomplete triad artifacts."""
        with tempfile.TemporaryDirectory() as tmpdir:
            temp_stage = os.path.join(tmpdir, "projects", "test_stage_temp")
            os.makedirs(temp_stage, exist_ok=True)
            # Create only .docx without .md and .json
            with open(os.path.join(temp_stage, "01_demographics.docx"), "w") as f:
                f.write("fake docx")

            payload = {
                "workspacePaths": [tmpdir],
                "conversationId": "test-convo-triad"
            }
            res = guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Triad Artifact Invariant", res.get("reason", ""))

            # Now provide full triad
            with open(os.path.join(temp_stage, "01_demographics.md"), "w") as f:
                f.write("# Demographics Table\n| N | Mean | SD |\n|---|---|---|\n| 100 | 25.4 | 4.2 |")
            with open(os.path.join(temp_stage, "01_demographics.json"), "w") as f:
                json.dump({"n": 100, "mean": 25.4, "sd": 4.2}, f)

            res2 = guard.handle_stop(payload)
            # Full triad provided; validator passes
            self.assertEqual(res2.get("decision"), "allow")

    def test_06_learning_pipeline_completion_stop_gate(self):
        """Stop hook must block completion if knowledge-curator was invoked without evolution subagents."""
        from integrity_hooks import IntegrityHooks

        # Case A: knowledge-curator invoked alone (incomplete pipeline)
        records_incomplete = [
            {"type": "USER_INPUT", "content": "Problem: tone was too dramatic and headings had no blank line."},
            {
                "type": "PLANNER_RESPONSE",
                "tool_calls": [
                    {
                        "name": "invoke_subagent",
                        "args": {"Subagents": [{"TypeName": "knowledge-curator", "Prompt": "Catalog lesson"}]}
                    }
                ]
            }
        ]
        ok, reason = IntegrityHooks.verify_learning_pipeline_completion(records_incomplete)
        self.assertFalse(ok)
        self.assertIn("Continuous Learning & Evolution Pipeline Incomplete", reason)

        # Case B: knowledge-curator followed by skill-evolver (complete pipeline)
        records_complete = [
            {"type": "USER_INPUT", "content": "Problem: tone was too dramatic and headings had no blank line."},
            {
                "type": "PLANNER_RESPONSE",
                "tool_calls": [
                    {
                        "name": "invoke_subagent",
                        "args": {"Subagents": [{"TypeName": "knowledge-curator", "Prompt": "Catalog lesson"}]}
                    }
                ]
            },
            {
                "type": "PLANNER_RESPONSE",
                "tool_calls": [
                    {
                        "name": "invoke_subagent",
                        "args": {"Subagents": [{"TypeName": "skill-evolver", "Prompt": "Synthesize candidate tool diff"}]}
                    }
                ]
            }
        ]
        ok_complete, reason_complete = IntegrityHooks.verify_learning_pipeline_completion(records_complete)
        self.assertTrue(ok_complete)
        self.assertEqual(reason_complete, "")

    def test_07_zero_fast_path_rationalization_stop_gate(self):
        """Stop hook must block rationalizing a fast-path to postpone code evolution (Directive 21.1)."""
        from integrity_hooks import IntegrityHooks

        # Case A: Model claims fast-path and that slower path will occur later
        records_fast_path = [
            {"type": "USER_INPUT", "content": "The heading had no blank line and was too dramatic."},
            {
                "type": "PLANNER_RESPONSE",
                "content": (
                    "The system prioritizes a fast-path for immediate behavioral updates via context modification "
                    "to avoid conversational delays, followed by a slower path that modifies code. "
                    "Full code mutation via the slow path will occur later."
                ),
                "tool_calls": [
                    {
                        "name": "invoke_subagent",
                        "args": {"Subagents": [{"TypeName": "knowledge-curator", "Prompt": "Catalog lesson"}]}
                    }
                ]
            }
        ]
        ok, reason = IntegrityHooks.verify_learning_pipeline_completion(records_fast_path)
        self.assertFalse(ok)
        self.assertIn("Zero 'Fast-Path' Rationalization Invariant", reason)

        # Case B: Model explicitly cites the prohibition (allowed exemption) and runs evolution
        records_exemption = [
            {"type": "USER_INPUT", "content": "The heading had no blank line."},
            {
                "type": "PLANNER_RESPONSE",
                "content": "Zero 'fast-path' invariant is active. Bypassing tool evolution is prohibited.",
                "tool_calls": [
                    {
                        "name": "invoke_subagent",
                        "args": {"Subagents": [{"TypeName": "knowledge-curator", "Prompt": "Catalog lesson"}]}
                    }
                ]
            },
            {
                "type": "PLANNER_RESPONSE",
                "tool_calls": [
                    {
                        "name": "invoke_subagent",
                        "args": {"Subagents": [{"TypeName": "skill-evolver", "Prompt": "Synthesize tool diff"}]}
                    }
                ]
            }
        ]
        ok_ex, reason_ex = IntegrityHooks.verify_learning_pipeline_completion(records_exemption)
        self.assertTrue(ok_ex)
        self.assertEqual(reason_ex, "")

    def test_08_premature_remediation_stop_gate(self):
        """Stop hook must block invoking delivery workers before tool evolution completes (Directive 21.1)."""
        from integrity_hooks import IntegrityHooks

        # Case A: Deliverable worker invoked before skill-evolver
        records_premature = [
            {"type": "USER_INPUT", "content": "Problem: heading has no blank line and tone is dramatic."},
            {
                "type": "PLANNER_RESPONSE",
                "tool_calls": [
                    {
                        "name": "invoke_subagent",
                        "args": {"Subagents": [{"TypeName": "knowledge-curator", "Prompt": "Catalog lesson"}]}
                    }
                ]
            },
            {
                "type": "PLANNER_RESPONSE",
                "tool_calls": [
                    {
                        "name": "invoke_subagent",
                        "args": {"Subagents": [{"TypeName": "academic-writer", "Prompt": "Rewrite the recommendations stage"}]}
                    }
                ]
            }
        ]
        ok, reason = IntegrityHooks.verify_learning_pipeline_completion(records_premature)
        self.assertFalse(ok)
        self.assertIn("Premature Remediation Without Tool Evolution", reason)

        # Case B: Evolution subagent runs before delivery worker
        records_proper = [
            {"type": "USER_INPUT", "content": "Problem: heading has no blank line and tone is dramatic."},
            {
                "type": "PLANNER_RESPONSE",
                "tool_calls": [
                    {
                        "name": "invoke_subagent",
                        "args": {"Subagents": [{"TypeName": "knowledge-curator", "Prompt": "Catalog lesson"}]}
                    }
                ]
            },
            {
                "type": "PLANNER_RESPONSE",
                "tool_calls": [
                    {
                        "name": "invoke_subagent",
                        "args": {"Subagents": [{"TypeName": "skill-evolver", "Prompt": "Evolve canonical tool"}]}
                    }
                ]
            },
            {
                "type": "PLANNER_RESPONSE",
                "tool_calls": [
                    {
                        "name": "invoke_subagent",
                        "args": {"Subagents": [{"TypeName": "academic-writer", "Prompt": "Execute remediation with evolved tool"}]}
                    }
                ]
            }
        ]
        ok_prop, reason_prop = IntegrityHooks.verify_learning_pipeline_completion(records_proper)
        self.assertTrue(ok_prop)
        self.assertEqual(reason_prop, "")


if __name__ == "__main__":
    unittest.main()

