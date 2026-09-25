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
            {"type": "USER_INPUT", "content": "The tone was too dramatic and headings had no blank line."},
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

        # Case B: knowledge-curator followed by skill-evolver and evaluation-agent (complete pipeline)
        records_complete = [
            {"type": "USER_INPUT", "content": "The tone was too dramatic and headings had no blank line."},
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
            },
            {
                "type": "PLANNER_RESPONSE",
                "tool_calls": [
                    {
                        "name": "invoke_subagent",
                        "args": {"Subagents": [{"TypeName": "evaluation-agent", "Prompt": "Compile lesson with graduation compiler"}]}
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

    def test_08_premature_remediation_stop_gate(self):
        """Stop hook must block invoking delivery workers before tool evolution completes (Directive 21.1)."""
        from integrity_hooks import IntegrityHooks

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

    def test_09_affirmative_critique_learning_required(self):
        """Stop hook must block concluding the turn if a critique was reported but learning was not invoked."""
        from integrity_hooks import IntegrityHooks

        # User reports critique, orchestrator attempts to stop without invoking learning
        records_no_learning = [
            {"type": "USER_INPUT", "content": "Problem: You should have a blank line before each header."},
            {
                "type": "PLANNER_RESPONSE",
                "content": "I will fix that right away."
            }
        ]
        ok, reason = IntegrityHooks.verify_learning_pipeline_completion(records_no_learning)
        self.assertFalse(ok)
        self.assertIn("Uninvoked Learning Pipeline on Critique", reason)

        # If full cascade including evaluation-agent is invoked, passes
        records_with_cascade = [
            {"type": "USER_INPUT", "content": "Problem: You should have a blank line before each header."},
            {
                "type": "PLANNER_RESPONSE",
                "tool_calls": [
                    {
                        "name": "invoke_subagent",
                        "args": {"Subagents": [{"TypeName": "trajectory-analyzer", "Prompt": "Diagnose trajectory"}]}
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
                        "args": {"Subagents": [{"TypeName": "evaluation-agent", "Prompt": "Compile candidate and graduate lesson"}]}
                    }
                ]
            }
        ]
        ok_casc, reason_casc = IntegrityHooks.verify_learning_pipeline_completion(records_with_cascade)
        self.assertTrue(ok_casc)
        self.assertEqual(reason_casc, "")

    def test_10_send_message_premature_remediation_gate(self):
        """Safety hook PreToolUse must deny send_message to delivery workers when critique is active before evolution."""
        from safety_hooks import SafetyHooks
        import tempfile

        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "USER_INPUT", "content": "Problem: You should have a blank line before each header."}) + "\n")
            tf.flush()
            transcript_file = tf.name

        try:
            payload = {
                "caller": "academic-orchestrator",
                "toolCall": {
                    "name": "send_message",
                    "args": {
                        "Recipient": "test-uuid-writer",
                        "Message": "Task: remediation of recommendations in process_rec.py and 08_recommendations.docx for academic-writer"
                    }
                },
                "transcriptPath": transcript_file
            }
            res = SafetyHooks.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "deny")
            self.assertIn("Premature Remediation Without Tool Evolution", res.get("reason", ""))
        finally:
            if os.path.exists(transcript_file):
                os.unlink(transcript_file)

    def test_11_skill_evolver_alone_without_evaluation_agent_blocked(self):
        """Stop hook must block if skill-evolver staged a candidate but evaluation-agent was never dispatched."""
        from integrity_hooks import IntegrityHooks

        records_se_alone = [
            {"type": "USER_INPUT", "content": "Problem: Header was duplicated during concatenation."},
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
                        "args": {"Subagents": [{"TypeName": "skill-evolver", "Prompt": "Formulate candidate JSON"}]}
                    }
                ]
            }
        ]
        ok, reason = IntegrityHooks.verify_learning_pipeline_completion(records_se_alone)
        self.assertFalse(ok)
        self.assertIn("Missing Evaluation & Graduation Step", reason)

    def test_12_pending_graduation_lesson_blocks_stop(self):
        """Stop hook must block if a lesson referenced in turn is still PENDING_GRADUATION on disk."""
        from integrity_hooks import IntegrityHooks
        import tempfile

        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".json", prefix="LSN-TEST-") as tf:
            tf.write(json.dumps({
                "lesson_id": "LSN-TEST-001",
                "graduation_status": "PENDING_GRADUATION",
                "graduation_track": "TRACK_1_IMMEDIATE_GRADUATION"
            }))
            tf.flush()
            lesson_file = tf.name

        try:
            records_pending = [
                {"type": "USER_INPUT", "content": "Problem: heading has duplicate titles."},
                {
                    "type": "PLANNER_RESPONSE",
                    "content": f"Saved lesson to {lesson_file}",
                    "tool_calls": [
                        {
                            "name": "invoke_subagent",
                            "args": {"Subagents": [{"TypeName": "knowledge-curator", "Prompt": "Catalog lesson"}]}
                        },
                        {
                            "name": "invoke_subagent",
                            "args": {"Subagents": [{"TypeName": "skill-evolver", "Prompt": "Evolve skill"}]}
                        },
                        {
                            "name": "invoke_subagent",
                            "args": {"Subagents": [{"TypeName": "evaluation-agent", "Prompt": "Run tests"}]}
                        }
                    ]
                }
            ]
            ok, reason = IntegrityHooks.verify_learning_pipeline_completion(records_pending)
            self.assertFalse(ok)
            self.assertIn("Incomplete Invariant Graduation", reason)
        finally:
            if os.path.exists(lesson_file):
                os.unlink(lesson_file)

    def test_13_directive_24_mechanical_rule_registry_immutability_guard(self):
        """PreToolUse must block write_to_file and replace_file_content targeting enforced_invariants.json (Directive 24)."""
        forbidden_targets = [
            ".agents/hooks/rules/enforced_invariants.json",
            os.path.join(ROOT, ".agents", "hooks", "rules", "enforced_invariants.json"),
            "enforced_invariants.json"
        ]
        for t in forbidden_targets:
            payload = {
                "toolCall": {
                    "name": "write_to_file",
                    "args": {"TargetFile": t, "CodeContent": "{}"}
                },
                "workspacePaths": [ROOT]
            }
            res = guard.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "deny", f"Failed to deny write to: {t}")
            self.assertIn("Directive 24", res.get("reason", ""))

            payload_replace = {
                "toolCall": {
                    "name": "replace_file_content",
                    "args": {"TargetFile": t, "TargetContent": "a", "ReplacementContent": "b"}
                },
                "workspacePaths": [ROOT]
            }
            res_replace = guard.handle_pre_tool_use(payload_replace)
            self.assertEqual(res_replace.get("decision"), "deny", f"Failed to deny replace in: {t}")
            self.assertIn("Directive 24", res_replace.get("reason", ""))

    def test_14_directive_24_skill_invariant_manual_injection_guard(self):
        """PreToolUse must block manual modification of Active Learned Behavioral Invariants in SKILL.md (Directive 24)."""
        skill_path = os.path.join(ROOT, ".agents", "skills", "chapter-4-writing", "SKILL.md")
        payload = {
            "toolCall": {
                "name": "replace_file_content",
                "args": {
                    "TargetFile": skill_path,
                    "TargetContent": "## 1. Scope",
                    "ReplacementContent": "## 🧠 Active Learned Behavioral Invariants\n- Manually injected"
                }
            },
            "workspacePaths": [ROOT]
        }
        res = guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Directive 24", res.get("reason", ""))
        self.assertIn("Active Learned Behavioral Invariants", res.get("reason", ""))

    def test_15_directive_24_mechanical_rule_shell_guard(self):
        """PreToolUse must block shell redirection or manipulation of enforced_invariants.json (Directive 24)."""
        shell_cmds = [
            "echo '{}' > .agents/hooks/rules/enforced_invariants.json",
            "sed -i 's/a/b/' .agents/hooks/rules/enforced_invariants.json",
            "rm -f .agents/hooks/rules/enforced_invariants.json"
        ]
        for cmd in shell_cmds:
            payload = {
                "toolCall": {
                    "name": "run_command",
                    "args": {"CommandLine": cmd}
                },
                "workspacePaths": [ROOT]
            }
            res = guard.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "deny", f"Failed to block shell command: {cmd}")
            self.assertIn("Directive 24", res.get("reason", ""))

    def test_16_directive_25_shell_shortcut_guard(self):
        """PreToolUse must block execution bypass flags like --skip-validation or --no-verify (Directive 25)."""
        bypass_cmds = [
            "python3 script.py --skip-validation",
            "git commit -m 'test' --no-verify",
            "run_analysis.sh --skip-tests",
            "python3 run.py --bypass-gates",
            "python3 tool.py --fast-path"
        ]
        for cmd in bypass_cmds:
            payload = {
                "toolCall": {
                    "name": "run_command",
                    "args": {"CommandLine": cmd}
                },
                "workspacePaths": [ROOT]
            }
            res = guard.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "deny", f"Failed to block bypass command: {cmd}")
            self.assertIn("Directive 25", res.get("reason", ""))

    def test_17_directive_25_transcript_anti_shortcut_no_rush_guard(self):
        """Stop hook must deny turns where agent rationalizes shortcuts, fastpaths, or rushing (Directive 25)."""
        test_dir = tempfile.mkdtemp(prefix="test_d25_")
        try:
            transcript_file = os.path.join(test_dir, "transcript.jsonl")
            with open(transcript_file, "w", encoding="utf-8") as f:
                f.write(json.dumps({"type": "USER_INPUT", "content": "Please generate the full analysis."}) + "\n")
                f.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "I am in a rush so I used a shortpath to finish quickly."}) + "\n")

            payload = {
                "transcriptPath": transcript_file,
                "workspacePaths": [test_dir]
            }
            res = guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Directive 25", res.get("reason", ""))
        finally:
            shutil.rmtree(test_dir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()


