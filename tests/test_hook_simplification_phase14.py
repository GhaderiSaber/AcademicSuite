#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_hook_simplification_phase14.py — Comprehensive Unit & Integration Tests for Phase 14 Hook Simplification

Verifies:
1. Class A: Safety Hooks (safety_hooks.py)
   - Raw-data protection for mutation tools and destructive shell commands
   - Dangerous command protection (rm -rf .agents, .git, root /, fork bombs)
   - Outside-workspace protection and English-only ASCII filename enforcement (Directive 6)
   - Subagent delegation and depth guards (Directive 12)
2. Class B: Integrity Hooks (integrity_hooks.py)
   - Triad Artifact Invariant enforcement (.docx, .md, .json)
   - Authoritative manifest verification
   - Post-analysis validation report checking (overall_verdict: PASS)
   - Binary Honesty Protocol (Directive 0)
   - Multi-Agent Truthfulness enforcement (Directive 0)
3. Class C: Learning Hooks (learning_hooks.py)
   - User correction capture from user turns and transcripts
   - Validation failure recording in experience logs
   - Agent trajectory logging in state/audit_log.jsonl
   - PreInvocation reminder injection
4. Hook Non-Orchestrator Invariant
   - Hooks strictly intercept, enforce, diagnose, and audit
   - Hooks never mutate state machine stages or orchestrate workflows
5. Dispatcher & Backward Compatibility
   - Track dispatchers route all 5 lifecycle events cleanly
   - transcript_and_rule_guard.py facade preserves 100% backward compatibility
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HOOKS_DIR = os.path.join(ROOT_DIR, ".agents", "hooks")
VERIF_DIR = os.path.join(ROOT_DIR, ".agents", "verification")
for p in (ROOT_DIR, HOOKS_DIR, VERIF_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from safety_hooks import (
    SafetyHooks,
    is_raw_data_path,
    is_raw_data_command,
    is_dangerous_command,
    is_outside_workspace,
    is_ascii_filename
)
from integrity_hooks import IntegrityHooks
from learning_hooks import LearningHooks
from track1_developer_dispatcher import dispatch_track1_event
from track2_academic_dispatcher import dispatch_track2_event
from contracts.hook_identity_contract import is_main_agent_developer

def dispatch_event(event: str, payload: dict) -> dict:
    if is_main_agent_developer(payload) or payload.get("track") == 1:
        return dispatch_track1_event(event, payload)
    return dispatch_track2_event(event, payload)

import transcript_and_rule_guard as legacy_guard


class TestHookSimplificationPhase14(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="phase14_hooks_test_")
        self.workspace = self.temp_dir

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # =========================================================================
    # 1. Class A: Safety Hooks
    # =========================================================================

    def test_01_raw_data_protection_mutation_tools(self):
        """SafetyHooks must block write/replace tools targeting raw datasets."""
        raw_targets = [
            os.path.join(self.workspace, "01_raw_inputs", "data_raw.xlsx"),
            os.path.join(self.workspace, "data", "raw", "survey.sav"),
            os.path.join(self.workspace, "raw_data.csv"),
            "raw/survey.csv"
        ]
        for target in raw_targets:
            payload = {
                "toolCall": {
                    "name": "write_to_file",
                    "args": {"TargetFile": target, "CodeContent": "dummy"}
                },
                "workspacePaths": [self.workspace]
            }
            res = SafetyHooks.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "deny", f"Failed to deny raw data target: {target}")
            self.assertIn("Raw-Data", res.get("reason", ""))

    def test_02_raw_data_protection_shell_commands(self):
        """SafetyHooks must block destructive commands targeting raw data."""
        raw_cmds = [
            "rm -f 01_raw_inputs/data_raw.xlsx",
            "mv data/raw/survey.sav data/raw/survey_backup.sav",
            "echo '' > raw_data.csv",
            "sed -i 's/1/2/' data/raw_dataset.csv"
        ]
        for cmd in raw_cmds:
            payload = {
                "toolCall": {
                    "name": "run_command",
                    "args": {"CommandLine": cmd}
                },
                "workspacePaths": [self.workspace]
            }
            res = SafetyHooks.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "deny", f"Failed to deny raw data command: {cmd}")
            self.assertIn("Raw-Data", res.get("reason", ""))

    def test_03_dangerous_system_commands(self):
        """SafetyHooks must block destructive system commands."""
        dangerous_cmds = [
            "rm -rf .agents",
            "rm -fr .git",
            "rm -rf /",
            ":(){ :|:& };:"
        ]
        for cmd in dangerous_cmds:
            payload = {
                "toolCall": {
                    "name": "run_command",
                    "args": {"CommandLine": cmd}
                },
                "workspacePaths": [self.workspace]
            }
            res = SafetyHooks.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "deny", f"Failed to deny dangerous command: {cmd}")
            self.assertIn("SECURITY VIOLATION", res.get("reason", ""))

    def test_04_outside_workspace_and_ascii_filename(self):
        """SafetyHooks must enforce workspace boundaries and ASCII filenames."""
        # Non-ASCII filename
        payload_non_ascii = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": os.path.join(self.workspace, "گزارش_تحلیل.docx"), "CodeContent": "text"}
            },
            "workspacePaths": [self.workspace]
        }
        res_ascii = SafetyHooks.handle_pre_tool_use(payload_non_ascii)
        self.assertEqual(res_ascii.get("decision"), "deny")
        self.assertIn("English-Only Filename", res_ascii.get("reason", ""))

        # Outside workspace
        outside_path = "/etc/passwd_fake.txt"
        payload_outside = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": outside_path, "CodeContent": "evil"}
            },
            "workspacePaths": [self.workspace]
        }
        res_outside = SafetyHooks.handle_pre_tool_use(payload_outside)
        self.assertEqual(res_outside.get("decision"), "deny")
        self.assertIn("Outside-Workspace", res_outside.get("reason", ""))

    def test_05_subagent_delegation_guard(self):
        """SafetyHooks must block worker subagents from invoking subagents and excessive nesting."""
        # Worker subagent attempt
        payload_worker = {
            "toolCall": {
                "name": "invoke_subagent",
                "args": {"Subagents": [{"TypeName": "research", "Role": "Worker", "Prompt": "Search"}]}
            },
            "agentName": "academic-writer",
            "workspacePaths": [self.workspace]
        }
        res_worker = SafetyHooks.handle_pre_tool_use(payload_worker)
        self.assertEqual(res_worker.get("decision"), "deny")
        self.assertIn("Worker Delegation Guard", res_worker.get("reason", ""))

        # Excessive nesting depth (>= 3)
        payload_depth = {
            "toolCall": {
                "name": "invoke_subagent",
                "args": {"Subagents": [{"TypeName": "research", "Role": "Worker", "Prompt": "Search"}]}
            },
            "agentName": "academic-orchestrator",
            "depth": 3,
            "workspacePaths": [self.workspace]
        }
        res_depth = SafetyHooks.handle_pre_tool_use(payload_depth)
        self.assertEqual(res_depth.get("decision"), "deny")
        self.assertIn("Excessive Nesting Guard", res_depth.get("reason", ""))

    # =========================================================================
    # 2. Class B: Integrity Hooks
    # =========================================================================

    def test_06_triad_artifact_verification(self):
        """IntegrityHooks must block turn completion if stage deliverable lacks .docx, .md, or .json."""
        stage_dir = os.path.join(self.workspace, "projects", "study_act", "06_hypothesis_1")
        os.makedirs(stage_dir, exist_ok=True)

        # Incomplete triad: only .docx exists
        with open(os.path.join(stage_dir, "06_hypothesis_1.docx"), "w") as f:
            f.write("mock docx")

        payload = {"workspacePaths": [self.workspace]}
        res = IntegrityHooks.handle_stop(payload)
        self.assertEqual(res.get("decision"), "continue")
        self.assertIn("Triad Artifact Invariant", res.get("reason", ""))

        # Complete triad
        with open(os.path.join(stage_dir, "06_hypothesis_1.md"), "w") as f:
            f.write("# H1 Results\nbeta = .42")
        with open(os.path.join(stage_dir, "06_hypothesis_1.json"), "w") as f:
            json.dump({"beta": 0.42, "p": 0.001}, f)

        res_complete = IntegrityHooks.handle_stop(payload)
        self.assertEqual(res_complete.get("decision"), "allow")

    def test_07_manifest_verification(self):
        """IntegrityHooks must verify that declared artifacts in manifest.json exist on disk."""
        stage_dir = os.path.join(self.workspace, "projects", "stage_test")
        os.makedirs(stage_dir, exist_ok=True)

        # Create manifest declaring missing artifact
        manifest_data = {
            "contract_version": "1.0.0",
            "stage_id": "stage_test",
            "artifacts": [
                {"name": "output", "path": "missing_output.json"}
            ]
        }
        with open(os.path.join(stage_dir, "manifest.json"), "w") as f:
            json.dump(manifest_data, f)

        payload = {"workspacePaths": [self.workspace]}
        res = IntegrityHooks.handle_stop(payload)
        self.assertEqual(res.get("decision"), "continue")
        self.assertIn("Manifest Verification", res.get("reason", ""))

    def test_08_post_analysis_validation_report(self):
        """IntegrityHooks must block turn completion if validation_report.json has overall_verdict: FAIL."""
        stage_dir = os.path.join(self.workspace, "projects", "stage_val")
        os.makedirs(stage_dir, exist_ok=True)

        val_report = {
            "overall_verdict": "FAIL",
            "results": [{"check": "normality", "verdict": "FAIL"}]
        }
        with open(os.path.join(stage_dir, "validation_report.json"), "w") as f:
            json.dump(val_report, f)

        payload = {"workspacePaths": [self.workspace]}
        res = IntegrityHooks.handle_stop(payload)
        self.assertEqual(res.get("decision"), "continue")
        self.assertIn("Post-Analysis Validation Gate", res.get("reason", ""))

    def test_09_binary_honesty_and_multiagent_truthfulness(self):
        """IntegrityHooks must enforce Directive 0 on transcript messages."""
        # 1. Binary Honesty failure
        transcript_path = os.path.join(self.workspace, "transcript.jsonl")
        with open(transcript_path, "w") as f:
            f.write(json.dumps({"type": "USER_INPUT", "content": "Did you follow the rules?"}) + "\n")
            f.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "Certainly! I followed all rules."}) + "\n")

        payload = {"workspacePaths": [self.workspace], "transcriptPath": transcript_path}
        res = IntegrityHooks.handle_stop(payload)
        self.assertEqual(res.get("decision"), "continue")
        self.assertIn("Binary Honesty Protocol", res.get("reason", ""))

        # 2. Multi-agent claim without subagent invocations
        with open(transcript_path, "w") as f:
            f.write(json.dumps({"type": "USER_INPUT", "content": "Run the analysis"}) + "\n")
            f.write(json.dumps({
                "type": "PLANNER_RESPONSE",
                "content": "We have successfully executed a complete multi-agent workflow.",
                "tool_calls": []
            }) + "\n")

        res_ma = IntegrityHooks.handle_stop(payload)
        self.assertEqual(res_ma.get("decision"), "continue")
        self.assertIn("multi-agent", res_ma.get("reason", "").lower())

        # 3. Conversational Language Bleed (Directive 6)
        with open(transcript_path, "w") as f:
            f.write(json.dumps({"type": "USER_INPUT", "content": "Please plan chapter 5"}) + "\n")
            f.write(json.dumps({
                "type": "PLANNER_RESPONSE",
                "content": "در پاسخ به درخواست شما برای تدوین فصل پنجم، این نقشه راه تفصیلی برای تبیین یافته‌های آماری آماده شده است و شامل مراحل متعددی می‌باشد."
            }) + "\n")

        res_lang = IntegrityHooks.handle_stop(payload)
        self.assertEqual(res_lang.get("decision"), "continue")
        self.assertIn("Directive 6", res_lang.get("reason", ""))
        self.assertIn("Persian", res_lang.get("reason", ""))

        # 4. English response allowed (even with quoted Persian instrument title)
        with open(transcript_path, "w") as f:
            f.write(json.dumps({"type": "USER_INPUT", "content": "Please plan chapter 5"}) + "\n")
            f.write(json.dumps({
                "type": "PLANNER_RESPONSE",
                "content": "Here is the structured execution blueprint for Chapter 5, examining the scale «ویژگی‌های شغلی» in detail."
            }) + "\n")

        res_ok = IntegrityHooks.handle_stop(payload)
        self.assertEqual(res_ok.get("decision"), "allow")

    # =========================================================================
    # 3. Class C: Learning Hooks
    # =========================================================================

    def test_10_learning_hooks_trajectory_and_pre_invocation(self):
        """LearningHooks must log agent trajectory to audit_log.jsonl and inject reminders."""
        # PostToolUse trajectory capture
        payload_tool = {
            "conversationId": "convo-learning-1",
            "stepIdx": 42,
            "error": None,
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": "python3 analysis.py"}
            },
            "workspacePaths": [self.workspace]
        }
        LearningHooks.capture_agent_trajectory(payload_tool)

        audit_file = os.path.join(self.workspace, "state", "audit_log.jsonl")
        self.assertTrue(os.path.isfile(audit_file), "audit_log.jsonl was not created")
        with open(audit_file, "r") as f:
            lines = f.readlines()
        self.assertGreaterEqual(len(lines), 1)
        entry = json.loads(lines[-1])
        self.assertEqual(entry["conversation_id"], "convo-learning-1")
        self.assertEqual(entry["tool_name"], "run_command")

        # PreInvocation reminder injection
        payload_pre = {"conversationId": "convo-learning-1", "workspacePaths": [self.workspace]}
        pre_res = LearningHooks.handle_pre_invocation(payload_pre)
        self.assertIn("injectSteps", pre_res)
        self.assertIn("CONSTITUTIONAL ENFORCEMENT ACTIVE", pre_res["injectSteps"][0]["ephemeralMessage"])

    # =========================================================================
    # 4. Hook Non-Orchestrator Invariant
    # =========================================================================

    def test_11_hooks_never_act_as_orchestrator(self):
        """Hooks must never mutate state machine milestones or dispatch workflow stages."""
        from scripts.academic_state_manager import StrictStateMachine, StageState
        state_dir = os.path.join(self.workspace, "academic-state")
        sm = StrictStateMachine(state_dir=state_dir, project_id="test_proj")
        sm.register_stage("01_demographics", "Demographics", initial_status=StageState.STAGE_LOCKED)

        # Run all hook handlers
        payload = {"workspacePaths": [self.workspace], "toolCall": {"name": "run_command", "args": {"CommandLine": "ls"}}}
        SafetyHooks.handle_pre_tool_use(payload)
        IntegrityHooks.handle_stop(payload)
        LearningHooks.capture_agent_trajectory(payload)

        # Verify state machine was NOT mutated by any hook
        sm.load_from_disk()
        self.assertEqual(sm.stages["01_demographics"]["status"], StageState.STAGE_LOCKED.value)

    # =========================================================================
    # 5. Dispatcher & Backward Compatibility
    # =========================================================================

    def test_12_dispatcher_and_facade_routing(self):
        """Track dispatchers and legacy facade route all 5 events without error."""
        # PreToolUse
        res_pre = dispatch_event("PreToolUse", {"toolCall": {"name": "run_command", "args": {"CommandLine": "ls"}}})
        self.assertEqual(res_pre.get("decision"), "allow")

        # PostToolUse
        res_post = dispatch_event("PostToolUse", {"toolCall": {"name": "run_command", "args": {}}})
        self.assertEqual(res_post, {})

        # PreInvocation (Main Developer -> Explicitly Exempt with track=1, returns empty dict)
        res_inv_main = dispatch_event("PreInvocation", {"track": 1})
        self.assertEqual(res_inv_main, {})

        # PreInvocation (Unassigned / Unknown -> Fail-Closed, returns injectSteps)
        res_inv_unassigned = dispatch_event("PreInvocation", {})
        self.assertIn("injectSteps", res_inv_unassigned)

        # PreInvocation (Academic Agent -> Controlled, returns injectSteps)
        res_inv_acad = dispatch_event("PreInvocation", {"agentName": "academic-orchestrator"})
        self.assertIn("injectSteps", res_inv_acad)

        # PostInvocation (Main Developer -> Explicitly Exempt with track=1)
        res_postinv_main = dispatch_event("PostInvocation", {"track": 1, "workspacePaths": [self.workspace]})
        self.assertEqual(res_postinv_main.get("injectSteps"), [])

        # PostInvocation (Academic Agent -> Controlled, returns injectSteps)
        res_postinv_acad = dispatch_event("PostInvocation", {"agentName": "academic-orchestrator", "workspacePaths": [self.workspace]})
        self.assertIn("injectSteps", res_postinv_acad)

        # Stop (Clean workspace -> Integrity verification passes allow)
        res_stop = dispatch_event("Stop", {"workspacePaths": [self.workspace]})
        self.assertEqual(res_stop.get("decision"), "allow")

        # Legacy facade
        facade_res = legacy_guard.handle_pre_tool_use({"toolCall": {"name": "run_command", "args": {"CommandLine": "ls"}}})
        self.assertEqual(facade_res.get("decision"), "allow")

    def test_13_main_agent_developer_bypass_and_orchestrator_guard(self):
        """Main Agent can write code and is exempt from academic Stop gates; Orchestrator is guarded."""
        code_file = os.path.join(self.workspace, "scripts", "new_feature.py")

        # 1. Academic-Orchestrator attempting to write code -> BLOCKED
        res_orch_write = dispatch_event("PreToolUse", {
            "agentName": "academic-orchestrator",
            "toolCall": {"name": "write_to_file", "args": {"TargetFile": code_file, "CodeContent": "print('hello')"}},
            "workspacePaths": [self.workspace]
        })
        self.assertEqual(res_orch_write.get("decision"), "deny")
        self.assertIn("Orchestrator Code Guard", res_orch_write.get("reason", ""))

        # 2. Main Developer Agent attempting to write code -> ALLOWED
        res_main_write = dispatch_event("PreToolUse", {
            "agentName": "main",
            "toolCall": {"name": "write_to_file", "args": {"TargetFile": code_file, "CodeContent": "print('hello')"}},
            "workspacePaths": [self.workspace]
        })
        self.assertEqual(res_main_write.get("decision"), "allow")

        # 3. PreInvocation bypass for Main Developer Agent
        res_main_preinv = dispatch_event("PreInvocation", {"agentName": "main"})
        self.assertEqual(res_main_preinv, {})

        # 4. Stop hook bypass for Main Developer Agent even with missing academic triads
        stage_dir = os.path.join(self.workspace, "projects", "study_act", "09_hypothesis_test")
        os.makedirs(stage_dir, exist_ok=True)
        with open(os.path.join(stage_dir, "09_hypothesis_test.docx"), "w") as f:
            f.write("mock docx")

        # Orchestrator is BLOCKED by missing triad
        res_orch_stop = dispatch_event("Stop", {
            "agentName": "academic-orchestrator",
            "workspacePaths": [self.workspace]
        })
        self.assertEqual(res_orch_stop.get("decision"), "continue")
        self.assertIn("Triad Artifact Invariant", res_orch_stop.get("reason", ""))

        # Main Developer Agent is EXEMPT and allowed to stop freely
        res_main_stop = dispatch_event("Stop", {
            "agentName": "main",
            "workspacePaths": [self.workspace]
        })
        self.assertEqual(res_main_stop.get("decision"), "allow")


if __name__ == "__main__":
    unittest.main()
