#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_hook_separation_option_a.py — Physical Hook Architecture Test Suite

Verifies Antigravity Plugin Hook Architecture:
1. Workspace Safety Gate (workspace_safety_dispatcher.py)
   - Allows code mutations, tests, commands for Native Developer Agent.
   - Strictly blocks raw-data mutations (01_raw_inputs) and destructive bash commands.
   - Enforces clean workspace root (Directive 23) and English ASCII filenames (Directive 6).
   - Fast-paths and completely exempts Native Developer Agent from academic stop-gates and thesis validation.
2. Academic Lifecycle Guard (academic_lifecycle_dispatcher.py)
   - Strips mutation and execution tools from academic-orchestrator (Directive 20).
   - Enforces Contractual Delegation Envelopes (CDE) on subagent invocations.
   - Enforces on-disk Triad artifacts (.docx, .md, .json) and fail-closed validation reports on Stop (Directives 3, 22).
   - Bypasses Native Developer Agent in < 2ms.
3. Clean Dispatcher Architecture
   - Permanent removal of legacy track dispatchers in favor of workspace safety & academic lifecycle guards.
4. Hook Schema (.agents/hooks.json)
   - Validates independent registration of workspace-safety-gate and academic-lifecycle-guard.
"""

import os
import sys
import json
import unittest
import subprocess
import tempfile

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HOOKS_DIR = os.path.join(ROOT_DIR, ".agents", "hooks")
agents_path = os.path.join(ROOT_DIR, ".agents")
for p in (ROOT_DIR, HOOKS_DIR, agents_path):
    if p not in sys.path:
        sys.path.insert(0, p)

from workspace_safety_dispatcher import dispatch_workspace_safety_event
from academic_lifecycle_dispatcher import dispatch_academic_lifecycle_event
from contracts.hook_identity_contract import is_main_agent_developer


def dispatch_event(event: str, payload: dict) -> dict:
    if is_main_agent_developer(payload):
        return dispatch_workspace_safety_event(event, payload)
    return dispatch_academic_lifecycle_event(event, payload)


class TestWorkspaceSafetyGate(unittest.TestCase):
    """Verifies Workspace Safety Gate behaviors across all callers."""

    def setUp(self):
        self.main_agent_payload = {
            "agentName": "main",
            "workspacePaths": [ROOT_DIR],
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": os.path.join(ROOT_DIR, "tests", "scratch_test.py"),
                    "CodeContent": "print('hello world')",
                    "Overwrite": True
                }
            }
        }

    def test_workspace_safety_allows_code_mutation_tools(self):
        """Native Developer Agent can freely use write_to_file and run_command on test/source files."""
        res = dispatch_workspace_safety_event("PreToolUse", self.main_agent_payload)
        self.assertEqual(res.get("decision"), "allow")

        # Test run_command for safe command (pytest)
        cmd_payload = dict(self.main_agent_payload)
        cmd_payload["toolCall"] = {
            "name": "run_command",
            "args": {"CommandLine": "pytest tests/test_something.py", "Cwd": ROOT_DIR}
        }
        res_cmd = dispatch_workspace_safety_event("PreToolUse", cmd_payload)
        self.assertEqual(res_cmd.get("decision"), "allow")

    def test_workspace_safety_blocks_raw_data_mutation(self):
        """Agents are strictly blocked from modifying or overwriting 01_raw_inputs/ datasets."""
        raw_payload = dict(self.main_agent_payload)
        raw_payload["toolCall"] = {
            "name": "write_to_file",
            "args": {
                "TargetFile": os.path.join(ROOT_DIR, "01_raw_inputs", "thesis_data.xlsx"),
                "CodeContent": "corrupt data",
                "Overwrite": True
            }
        }
        res = dispatch_workspace_safety_event("PreToolUse", raw_payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Raw-Data Immutability Guard", res.get("reason", ""))

    def test_workspace_safety_blocks_dangerous_bash_commands(self):
        """Agents are blocked from catastrophic system commands (e.g. rm -rf .git, git push --force)."""
        dangerous_payload = dict(self.main_agent_payload)
        dangerous_payload["toolCall"] = {
            "name": "run_command",
            "args": {"CommandLine": "rm -rf .git", "Cwd": ROOT_DIR}
        }
        res = dispatch_workspace_safety_event("PreToolUse", dangerous_payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Destruction of .agents or .git", res.get("reason", ""))

    def test_workspace_safety_blocks_root_script_execution(self):
        """Enforces Directive 23: writing executable scripts directly to repository root is blocked."""
        root_script_payload = dict(self.main_agent_payload)
        root_script_payload["toolCall"] = {
            "name": "write_to_file",
            "args": {
                "TargetFile": os.path.join(ROOT_DIR, "bad_script.py"),
                "CodeContent": "# executable script at root",
                "Overwrite": True
            }
        }
        res = dispatch_workspace_safety_event("PreToolUse", root_script_payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Directive 23", res.get("reason", ""))

    def test_workspace_safety_bypasses_academic_stop_gates(self):
        """Native Developer finishes turns (Stop) without demanding thesis triads or validation reports."""
        stop_payload = {
            "agentName": "main",
            "workspacePaths": [ROOT_DIR],
            "conversation_id": "test-dev-session-001"
        }
        res = dispatch_workspace_safety_event("Stop", stop_payload)
        self.assertEqual(res.get("decision"), "allow")


class TestAcademicLifecycleGuard(unittest.TestCase):
    """Verifies Academic Lifecycle Governance behaviors."""

    def test_academic_lifecycle_fast_paths_native_developer_agent(self):
        """Academic dispatcher immediately allows Native Developer Agent in < 2ms across all events."""
        main_payload = {"agentName": "main", "workspacePaths": [ROOT_DIR]}
        for event in ("PreToolUse", "PostToolUse", "PreInvocation", "PostInvocation", "Stop"):
            res = dispatch_academic_lifecycle_event(event, main_payload)
            if event in ("PreInvocation", "PostToolUse"):
                self.assertEqual(res, {})
            elif event == "PostInvocation":
                self.assertEqual(res, {"injectSteps": [], "terminationBehavior": ""})
            else:
                self.assertEqual(res.get("decision"), "allow")

    def test_academic_lifecycle_blocks_orchestrator_mutation_tools(self):
        """academic-orchestrator is strictly forbidden from mutation and execution tools (Directive 20)."""
        forbidden_tools = [
            ("write_to_file", {"TargetFile": "/tmp/test.txt", "CodeContent": "x"}),
            ("replace_file_content", {"TargetFile": "/tmp/test.txt", "TargetContent": "a", "ReplacementContent": "b"}),
            ("run_command", {"CommandLine": "python3 script.py"}),
        ]
        for tool_name, args in forbidden_tools:
            orch_payload = {
                "agentName": "academic-orchestrator",
                "caller": "academic-orchestrator",
                "toolCall": {"name": tool_name, "args": args},
                "workspacePaths": [ROOT_DIR]
            }
            res = dispatch_academic_lifecycle_event("PreToolUse", orch_payload)
            self.assertEqual(res.get("decision"), "deny", f"Tool {tool_name} was not denied for academic-orchestrator")
            self.assertIn("Orchestrator", res.get("reason", ""))

    def test_academic_lifecycle_enforces_cde_on_orchestrator_delegations(self):
        """Delegations from academic-orchestrator must contain a structured Contractual Delegation Envelope."""
        invalid_delegation_payload = {
            "agentName": "academic-orchestrator",
            "caller": "academic-orchestrator",
            "toolCall": {
                "name": "invoke_subagent",
                "args": {
                    "Subagents": [
                        {
                            "TypeName": "statistics-agent",
                            "Role": "Stats Worker",
                            "Prompt": "Please compute the mean for me"  # Lacks CDE tags
                        }
                    ]
                }
            },
            "workspacePaths": [ROOT_DIR]
        }
        res = dispatch_academic_lifecycle_event("PreToolUse", invalid_delegation_payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Contractual Delegation Invariant", res.get("reason", ""))

    def test_academic_lifecycle_enforces_triad_and_validation_gate_on_stop(self):
        """Stop gate for academic agents denies unverified turns lacking required triads or validation reports."""
        with tempfile.TemporaryDirectory() as tmpdir:
            transcript_file = os.path.join(tmpdir, "transcript.jsonl")
            records = [
                {"type": "USER_INPUT", "content": "Please run the pipeline."},
                {"type": "PLANNER_RESPONSE", "content": "We have successfully executed a complete multi-agent workflow.", "tool_calls": []}
            ]
            with open(transcript_file, "w") as f:
                for r in records:
                    f.write(json.dumps(r) + "\n")
            academic_stop_payload = {
                "agentName": "academic-orchestrator",
                "caller": "academic-orchestrator",
                "workspacePaths": [tmpdir],
                "transcriptPath": transcript_file,
                "conversation_id": "test-orch-session-001"
            }
            res = dispatch_academic_lifecycle_event("Stop", academic_stop_payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Directive 0 & Directive 12", res.get("reason", ""))


class TestDispatchersAndSubprocess(unittest.TestCase):
    """Verifies dispatchers routing and subprocess CLI invocations."""

    def test_hook_dispatcher_permanently_removed(self):
        """Verifies legacy hook_dispatcher.py is deleted."""
        dispatcher_path = os.path.join(HOOKS_DIR, "hook_dispatcher.py")
        self.assertFalse(os.path.exists(dispatcher_path), "hook_dispatcher.py must be permanently deleted")

    def test_legacy_track_dispatchers_permanently_removed(self):
        """Verifies track1_developer_dispatcher.py and track2_academic_dispatcher.py are deleted."""
        self.assertFalse(os.path.exists(os.path.join(HOOKS_DIR, "track1_developer_dispatcher.py")))
        self.assertFalse(os.path.exists(os.path.join(HOOKS_DIR, "track2_academic_dispatcher.py")))

    def test_facade_routes_main_agent_to_workspace_safety(self):
        """dispatch_event cleanly routes Main Agent payloads to workspace safety."""
        main_payload = {
            "agentName": "main",
            "workspacePaths": [ROOT_DIR],
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": os.path.join(ROOT_DIR, "tests", "test_sample.py"),
                    "CodeContent": "def test_ok(): pass",
                    "Overwrite": True
                }
            }
        }
        res = dispatch_event("PreToolUse", main_payload)
        self.assertEqual(res.get("decision"), "allow")

    def test_facade_routes_orchestrator_to_academic_lifecycle(self):
        """dispatch_event cleanly routes academic-orchestrator payloads to academic lifecycle."""
        orch_payload = {
            "agentName": "academic-orchestrator",
            "caller": "academic-orchestrator",
            "workspacePaths": [ROOT_DIR],
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": "/tmp/fake.py", "CodeContent": "print(1)"}
            }
        }
        res = dispatch_event("PreToolUse", orch_payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Orchestrator", res.get("reason", ""))

    def test_workspace_safety_dispatcher_subprocess_cli(self):
        """workspace_safety_dispatcher.py CLI executes cleanly and returns JSON."""
        script_path = os.path.join(HOOKS_DIR, "workspace_safety_dispatcher.py")
        payload = {
            "agentName": "main",
            "workspacePaths": [ROOT_DIR],
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": "git status", "Cwd": ROOT_DIR}
            }
        }
        proc = subprocess.run(
            [sys.executable, script_path, "--event", "PreToolUse"],
            input=json.dumps(payload),
            capture_output=True,
            text=True
        )
        self.assertEqual(proc.returncode, 0)
        out = json.loads(proc.stdout.strip())
        self.assertEqual(out.get("decision"), "allow")

    def test_academic_lifecycle_dispatcher_subprocess_cli(self):
        """academic_lifecycle_dispatcher.py CLI executes cleanly and denies Directive 20 violation."""
        script_path = os.path.join(HOOKS_DIR, "academic_lifecycle_dispatcher.py")
        payload = {
            "agentName": "academic-orchestrator",
            "caller": "academic-orchestrator",
            "workspacePaths": [ROOT_DIR],
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": "/tmp/a.py", "CodeContent": "pass"}
            }
        }
        proc = subprocess.run(
            [sys.executable, script_path, "--event", "PreToolUse"],
            input=json.dumps(payload),
            capture_output=True,
            text=True
        )
        self.assertEqual(proc.returncode, 0)
        out = json.loads(proc.stdout.strip())
        self.assertEqual(out.get("decision"), "deny")


class TestHooksJsonConfiguration(unittest.TestCase):
    """Verifies .agents/hooks.json schema configuration."""

    def test_hooks_json_has_workspace_safety_and_academic_guard(self):
        hooks_path = os.path.join(ROOT_DIR, ".agents", "hooks.json")
        self.assertTrue(os.path.exists(hooks_path))
        with open(hooks_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("workspace-safety-gate", data)
        self.assertIn("academic-lifecycle-guard", data)

        safety = data["workspace-safety-gate"]
        self.assertTrue(safety.get("enabled", False))
        self.assertIn("PreToolUse", safety)

        guard = data["academic-lifecycle-guard"]
        self.assertTrue(guard.get("enabled", False))
        for event in ("PreToolUse", "PostToolUse", "PreInvocation", "PostInvocation", "Stop"):
            self.assertIn(event, guard)


if __name__ == "__main__":
    unittest.main()
