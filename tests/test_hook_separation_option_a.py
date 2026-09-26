#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_hook_separation_option_a.py — Physical Hook Separation Test Suite

Verifies Option A:
1. Track 1 Developer Safety Gate (track1_developer_dispatcher.py)
   - Allows code mutations, tests, commands for Main Developer Agent.
   - Strictly blocks raw-data mutations (01_raw_inputs) and destructive bash commands.
   - Enforces clean workspace root (Directive 23) and English ASCII filenames (Directive 6).
   - Fast-paths and completely exempts Main Agent from academic stop-gates and thesis validation.
2. Track 2 Academic Governance Guard (track2_academic_dispatcher.py)
   - Strips mutation and execution tools from academic-orchestrator (Directive 20).
   - Enforces Contractual Delegation Envelopes (CDE) on subagent invocations.
   - Enforces on-disk Triad artifacts (.docx, .md, .json) and fail-closed validation reports on Stop (Directives 3, 22).
   - Bypasses Main Developer Agent in < 2ms.
3. Track Dispatchers & Native Agent Hooks
   - Permanent removal of legacy hook_dispatcher.py in favor of native agent-scoped hooks.
4. Hook Schema (.agents/hooks.json)
   - Validates independent registration of track1-developer-safety-gate and track2-academic-orchestrator-guard.
"""

import os
import sys
import json
import unittest
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HOOKS_DIR = os.path.join(ROOT_DIR, ".agents", "hooks")
agents_path = os.path.join(ROOT_DIR, ".agents")
for p in (ROOT_DIR, HOOKS_DIR, agents_path):
    if p not in sys.path:
        sys.path.insert(0, p)

from track1_developer_dispatcher import dispatch_track1_event
from track2_academic_dispatcher import dispatch_track2_event
from contracts.hook_identity_contract import is_main_agent_developer

def dispatch_event(event: str, payload: dict) -> dict:
    if is_main_agent_developer(payload) or payload.get("track") == 1:
        return dispatch_track1_event(event, payload)
    return dispatch_track2_event(event, payload)


import tempfile


class TestTrack1DeveloperSafetyGate(unittest.TestCase):
    """Verifies Track 1 Developer Safety Gate behaviors for Built-in Main Agent."""

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

    def test_track1_allows_code_mutation_tools(self):
        """Main Developer Agent can freely use write_to_file and run_command on test/source files."""
        res = dispatch_track1_event("PreToolUse", self.main_agent_payload)
        self.assertEqual(res.get("decision"), "allow")

        # Test run_command for safe command (pytest)
        cmd_payload = dict(self.main_agent_payload)
        cmd_payload["toolCall"] = {
            "name": "run_command",
            "args": {"CommandLine": "pytest tests/test_something.py", "Cwd": ROOT_DIR}
        }
        res_cmd = dispatch_track1_event("PreToolUse", cmd_payload)
        self.assertEqual(res_cmd.get("decision"), "allow")

    def test_track1_blocks_raw_data_mutation(self):
        """Main Agent is strictly blocked from modifying or overwriting 01_raw_inputs/ datasets."""
        raw_payload = dict(self.main_agent_payload)
        raw_payload["toolCall"] = {
            "name": "write_to_file",
            "args": {
                "TargetFile": os.path.join(ROOT_DIR, "01_raw_inputs", "thesis_data.xlsx"),
                "CodeContent": "corrupt data",
                "Overwrite": True
            }
        }
        res = dispatch_track1_event("PreToolUse", raw_payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Raw-Data Immutability Guard", res.get("reason", ""))

    def test_track1_blocks_dangerous_bash_commands(self):
        """Main Agent is blocked from catastrophic system commands (e.g. rm -rf .git, git push --force)."""
        dangerous_payload = dict(self.main_agent_payload)
        dangerous_payload["toolCall"] = {
            "name": "run_command",
            "args": {"CommandLine": "rm -rf .git", "Cwd": ROOT_DIR}
        }
        res = dispatch_track1_event("PreToolUse", dangerous_payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Destruction of .agents or .git", res.get("reason", ""))

    def test_track1_blocks_root_script_execution(self):
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
        res = dispatch_track1_event("PreToolUse", root_script_payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Directive 23", res.get("reason", ""))

    def test_track1_bypasses_academic_stop_gates(self):
        """Main Agent finishes turns (Stop) without demanding thesis triads or validation reports."""
        stop_payload = {
            "agentName": "main",
            "workspacePaths": [ROOT_DIR],
            "conversation_id": "test-dev-session-001"
        }
        res = dispatch_track1_event("Stop", stop_payload)
        self.assertEqual(res.get("decision"), "allow")

    def test_track1_yields_for_academic_agents(self):
        """If caller is an academic agent, track1 dispatcher yields immediately."""
        academic_payload = {
            "agentName": "academic-orchestrator",
            "workspacePaths": [ROOT_DIR],
            "toolCall": {"name": "run_command", "args": {"CommandLine": "ls"}}
        }
        res = dispatch_track1_event("PreToolUse", academic_payload)
        # Yields allow so Track 2 dispatcher can govern
        self.assertEqual(res.get("decision"), "allow")


class TestTrack2AcademicGovernanceGuard(unittest.TestCase):
    """Verifies Track 2 Academic Governance behaviors."""

    def test_track2_fast_paths_main_developer_agent(self):
        """Track 2 dispatcher immediately allows Main Developer Agent in < 2ms across all events."""
        main_payload = {"agentName": "main", "workspacePaths": [ROOT_DIR]}
        for event in ("PreToolUse", "PostToolUse", "PreInvocation", "PostInvocation", "Stop"):
            res = dispatch_track2_event(event, main_payload)
            if event in ("PreInvocation", "PostToolUse"):
                self.assertEqual(res, {})
            elif event == "PostInvocation":
                self.assertEqual(res, {"injectSteps": [], "terminationBehavior": ""})
            else:
                self.assertEqual(res.get("decision"), "allow")

    def test_track2_blocks_orchestrator_mutation_tools(self):
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
            res = dispatch_track2_event("PreToolUse", orch_payload)
            self.assertEqual(res.get("decision"), "deny", f"Tool {tool_name} was not denied for academic-orchestrator")
            self.assertIn("Orchestrator", res.get("reason", ""))

    def test_track2_enforces_cde_on_orchestrator_delegations(self):
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
        res = dispatch_track2_event("PreToolUse", invalid_delegation_payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Contractual Delegation Invariant", res.get("reason", ""))

    def test_track2_enforces_triad_and_validation_gate_on_stop(self):
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
            res = dispatch_track2_event("Stop", academic_stop_payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Directive 0 & Directive 12", res.get("reason", ""))


class TestTrackDispatchersAndSubprocess(unittest.TestCase):
    """Verifies track dispatchers routing and subprocess CLI invocations without legacy facade."""

    def test_hook_dispatcher_permanently_removed(self):
        """Verifies hook_dispatcher.py is deleted and replaced by native agent-scoped hooks."""
        dispatcher_path = os.path.join(HOOKS_DIR, "hook_dispatcher.py")
        self.assertFalse(os.path.exists(dispatcher_path), "hook_dispatcher.py must be permanently deleted")

    def test_facade_routes_main_agent_to_track1(self):
        """dispatch_event cleanly routes Main Agent payloads to Track 1."""
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

    def test_facade_routes_orchestrator_to_track2(self):
        """dispatch_event cleanly routes academic-orchestrator payloads to Track 2."""
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

    def test_track1_dispatcher_subprocess_cli(self):
        """track1_developer_dispatcher.py CLI executes cleanly and returns JSON."""
        script_path = os.path.join(HOOKS_DIR, "track1_developer_dispatcher.py")
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

    def test_track2_dispatcher_subprocess_cli(self):
        """track2_academic_dispatcher.py CLI executes cleanly and denies Directive 20 violation."""
        script_path = os.path.join(HOOKS_DIR, "track2_academic_dispatcher.py")
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

    def test_hooks_json_has_both_tracks_configured(self):
        hooks_path = os.path.join(ROOT_DIR, ".agents", "hooks.json")
        self.assertTrue(os.path.exists(hooks_path))
        with open(hooks_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.assertIn("track1-developer-safety-gate", data)
        self.assertIn("track2-academic-orchestrator-guard", data)

        track1 = data["track1-developer-safety-gate"]
        self.assertTrue(track1.get("enabled", False))
        self.assertIn("PreToolUse", track1)

        track2 = data["track2-academic-orchestrator-guard"]
        self.assertTrue(track2.get("enabled", False))
        for event in ("PreToolUse", "PostToolUse", "PreInvocation", "PostInvocation", "Stop"):
            self.assertIn(event, track2)


if __name__ == "__main__":
    unittest.main()
