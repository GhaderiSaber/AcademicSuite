#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_directive_21_learning_cascade_enforcement.py

Comprehensive Verification Suite for Directive 21 & 21.1 Continuous Learning Cascade
Mechanical Hooks Enforcement:
1. PreToolUse Premature Remediation Gate: Blocks delivery workers on active critique.
2. PreToolUse Learning Agent Allow Gate: Allows learning subagents on active critique.
3. Stop Gate: Blocks stop (decision: continue) when learning cascade was not executed on critique.
4. Stop Gate: Allows stop when full 5-stage learning cascade completed.
5. hooks.json Flat Structure Verification: Verifies Antigravity 2.0 flat Stop/PreInvocation/PostInvocation spec.
"""

import os
import sys
import json
import tempfile
import shutil
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
for p in (ROOT_DIR, os.path.join(ROOT_DIR, ".agents"), os.path.join(ROOT_DIR, ".agents", "hooks"), os.path.join(ROOT_DIR, ".agents", "contracts")):
    if p not in sys.path:
        sys.path.insert(0, p)

from track2_academic_dispatcher import dispatch_track2_event
from integrity_hooks import IntegrityHooks
import importlib.util
_guard_spec = importlib.util.spec_from_file_location("orch_guard", os.path.join(ROOT_DIR, ".agents", "agents", "academic-orchestrator", "guard.py"))
orch_guard = importlib.util.module_from_spec(_guard_spec)
_guard_spec.loader.exec_module(orch_guard)


class TestDirective21LearningCascadeEnforcement(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_d21_cascade_")
        self.logs_dir = os.path.join(self.temp_dir, ".system_generated", "logs")
        os.makedirs(self.logs_dir, exist_ok=True)
        self.transcript_path = os.path.join(self.logs_dir, "transcript.jsonl")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _write_transcript(self, steps):
        with open(self.transcript_path, "w", encoding="utf-8") as f:
            for s in steps:
                f.write(json.dumps(s, ensure_ascii=False) + "\n")

    def test_01_critique_blocks_delivery_worker_pre_tool_use(self):
        """PreToolUse must deny invoking delivery workers (academic-writer) when user critique is active."""
        steps = [
            {"step_index": 0, "type": "USER_INPUT", "source": "USER_EXPLICIT", "content": "There is a problem: We have a lot of references, you put only a small batch."},
            {"step_index": 1, "type": "PLANNER_RESPONSE", "source": "MODEL", "content": "I will fix this immediately."}
        ]
        self._write_transcript(steps)

        delivery_call = {
            "name": "invoke_subagent",
            "args": {
                "Subagents": [
                    {
                        "TypeName": "academic-writer",
                        "Role": "Drafter",
                        "Prompt": "### Contractual Delegation Envelope (CDE)\n```json\n{\"task_id\": \"TSK-FIX\", \"worker_agent\": \"academic-writer\", \"inputs\": [], \"required_artifacts\": [], \"objective\": \"fix\"}\n```"
                    }
                ]
            }
        }

        payload = {
            "conversationId": "test-d21-conv",
            "workspacePaths": [self.temp_dir],
            "transcriptPath": self.transcript_path,
            "toolCall": delivery_call
        }

        res = dispatch_track2_event("PreToolUse", payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Directive 21.1", res.get("reason", ""))
        self.assertEqual(res.get("reason"), res.get("message"))

    def test_02_critique_allows_learning_agent_pre_tool_use(self):
        """PreToolUse must allow invoking learning agents (trajectory-analyzer) when user critique is active."""
        steps = [
            {"step_index": 0, "type": "USER_INPUT", "source": "USER_EXPLICIT", "content": "There is a defect in the references list."},
            {"step_index": 1, "type": "PLANNER_RESPONSE", "source": "MODEL", "content": "Initiating learning cascade."}
        ]
        self._write_transcript(steps)

        learning_call = {
            "name": "invoke_subagent",
            "args": {
                "Subagents": [
                    {
                        "TypeName": "trajectory-analyzer",
                        "Role": "Trajectory Analyzer",
                        "Prompt": "Analyze observable trajectory for reference omission defect."
                    }
                ]
            }
        }

        payload = {
            "conversationId": "test-d21-conv",
            "workspacePaths": [self.temp_dir],
            "transcriptPath": self.transcript_path,
            "toolCall": learning_call
        }

        res = dispatch_track2_event("PreToolUse", payload)
        self.assertEqual(res.get("decision"), "allow")

    def test_03_critique_blocks_stop_without_learning_cascade(self):
        """Stop hook must return continue (fail-closed) when user critique was not addressed via learning cascade."""
        steps = [
            {"step_index": 0, "type": "USER_INPUT", "source": "USER_EXPLICIT", "content": "You made an error: the references are missing."},
            {"step_index": 1, "type": "PLANNER_RESPONSE", "source": "MODEL", "content": "I finished fixing the references."}
        ]
        self._write_transcript(steps)

        payload = {
            "conversationId": "test-d21-conv",
            "workspacePaths": [self.temp_dir],
            "transcriptPath": self.transcript_path
        }

        res = dispatch_track2_event("Stop", payload)
        self.assertEqual(res.get("decision"), "continue")
        self.assertIn("Directive 21", res.get("reason", ""))
        self.assertEqual(res.get("reason"), res.get("message"))

    def test_04_critique_allows_stop_when_learning_cascade_completed(self):
        """Stop hook must allow stop when full 5-stage continuous learning cascade was executed."""
        steps = [
            {"step_index": 0, "type": "USER_INPUT", "source": "USER_EXPLICIT", "content": "There is a bug in the reference generation."},
            {
                "step_index": 1,
                "type": "PLANNER_RESPONSE",
                "source": "MODEL",
                "content": "Executing continuous learning cascade.",
                "tool_calls": [
                    {
                        "name": "invoke_subagent",
                        "args": {"Subagents": [{"TypeName": "trajectory-analyzer"}, {"TypeName": "behavior-analyst"}, {"TypeName": "knowledge-curator"}]}
                    },
                    {
                        "name": "invoke_subagent",
                        "args": {"Subagents": [{"TypeName": "skill-evolver"}, {"TypeName": "evaluation-agent"}]}
                    }
                ]
            },
            {
                "step_index": 2,
                "type": "PLANNER_RESPONSE",
                "source": "MODEL",
                "content": "### Stage Completion Report\n- What was done: The learning cascade completed and tools have been evolved on disk.\n- What will be done next: Awaiting confirmation to re-run validation.\n\nShall we proceed?"
            }
        ]
        self._write_transcript(steps)

        payload = {
            "conversationId": "test-d21-conv",
            "workspacePaths": [self.temp_dir],
            "transcriptPath": self.transcript_path
        }

        res = dispatch_track2_event("Stop", payload)
        self.assertEqual(res.get("decision"), "allow")

    def test_05_hooks_json_structure_conforms_to_antigravity_spec(self):
        """Verifies hooks.json has flat Stop/PreInvocation/PostInvocation handlers and invoke_subagent matcher."""
        hooks_files = [
            os.path.join(ROOT_DIR, ".agents", "hooks.json"),
            os.path.join(ROOT_DIR, ".agents", "agents", "academic-orchestrator", "hooks.json"),
            os.path.join(ROOT_DIR, ".agents", "plugins", "academic-suite", "hooks.json")
        ]

        for hpath in hooks_files:
            self.assertTrue(os.path.isfile(hpath), f"File {hpath} does not exist")
            with open(hpath, "r", encoding="utf-8") as f:
                data = json.load(f)

            for guard_key, guard_data in data.items():
                if not isinstance(guard_data, dict):
                    continue

                # Stop must be a flat list of handler objects, NOT {"hooks": [...]}
                if "Stop" in guard_data:
                    stop_handlers = guard_data["Stop"]
                    self.assertIsInstance(stop_handlers, list, f"'Stop' in {hpath} must be a list")
                    for h in stop_handlers:
                        self.assertNotIn("hooks", h, f"'Stop' in {hpath} must be flat (found nested 'hooks' wrapper)")
                        self.assertIn("command", h, f"'Stop' handler in {hpath} missing 'command' field")

                # PreInvocation must be flat
                if "PreInvocation" in guard_data:
                    for h in guard_data["PreInvocation"]:
                        self.assertNotIn("hooks", h, f"'PreInvocation' in {hpath} must be flat")
                        self.assertIn("command", h, f"'PreInvocation' handler in {hpath} missing 'command' field")

                # PostInvocation must be flat
                if "PostInvocation" in guard_data:
                    for h in guard_data["PostInvocation"]:
                        self.assertNotIn("hooks", h, f"'PostInvocation' in {hpath} must be flat")
                        self.assertIn("command", h, f"'PostInvocation' handler in {hpath} missing 'command' field")

                # Track 2 Academic Orchestrator PreToolUse matcher must include invoke_subagent
                if "orchestrator" in guard_key.lower() and "PreToolUse" in guard_data:
                    for group in guard_data["PreToolUse"]:
                        matcher = group.get("matcher", "")
                        self.assertIn("invoke_subagent", matcher, f"'PreToolUse' matcher in {guard_key} ({hpath}) missing invoke_subagent")


if __name__ == "__main__":
    unittest.main()
