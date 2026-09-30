#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/architecture/test_dual_track_developer_and_orchestrator.py — Dual-Track Accessibility Verification

Verifies:
1. Track 1 Main Developer Agent has 100% unrestricted access to code-authoring & execution tools
   (run_command, write_to_file, replace_file_content) across fresh and existing conversations.
2. Track 1 Developer Agent is never falsely classified as academic-orchestrator by hook-injected
   ephemeral messages or viewed files.
3. Track 2 Academic Orchestrator remains strictly governed by Directive 20 Zero-Hands Contract
   (prohibited from run_command and file mutations; allowed invoke_subagent).
4. Subagents remain bounded to their respective operational planes and capability contracts.
"""

import os
import sys
import json
import tempfile
import pytest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
AGENTS_DIR = os.path.abspath(os.path.join(ROOT_DIR, ".agents"))

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if AGENTS_DIR not in sys.path:
    sys.path.insert(0, AGENTS_DIR)

from contracts.hook_identity_contract import (
    resolve_hook_identity,
    is_main_agent_developer,
    inspect_transcript_for_identity
)
from hooks.track1_developer_dispatcher import dispatch_track1_event
from hooks.track2_academic_dispatcher import dispatch_track2_event


class TestDeveloperAgentAccessibility:
    """Verifies that the Developer Agent is never blocked from coding or running commands."""

    def test_fresh_developer_conversation_allows_run_command(self):
        """When user starts a new dev conversation (e.g. audit god files), run_command must be allowed."""
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({
                "step_index": 0,
                "source": "USER_EXPLICIT",
                "type": "USER_INPUT",
                "content": "<USER_REQUEST>\nScan the god files in the repo and audit them.\n</USER_REQUEST>"
            }) + "\n")
            tpath = tf.name

        try:
            payload = {
                "conversationId": "dev-fresh-001",
                "workspacePaths": [ROOT_DIR],
                "transcriptPath": tpath,
                "toolCall": {
                    "name": "run_command",
                    "args": {"CommandLine": "find . -maxdepth 4"}
                }
            }
            ident = resolve_hook_identity(payload)
            assert ident.is_main_developer is True
            assert ident.track == "track_1_developer"

            # Must allow on PreToolUse in both dispatchers
            res1 = dispatch_track1_event("PreToolUse", payload)
            assert res1.get("decision") != "deny"

            res2 = dispatch_track2_event("PreToolUse", payload)
            assert res2.get("decision") == "allow"

            # PreInvocation must be empty (no academic reminders injected)
            res_pre = dispatch_track2_event("PreInvocation", payload)
            assert res_pre == {}

            # Stop must be allow (no triad artifact blocking)
            res_stop = dispatch_track2_event("Stop", payload)
            assert res_stop.get("decision") == "allow"
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)

    def test_ephemeral_message_does_not_poison_developer_identity(self):
        """An ephemeral message injected into transcript must NEVER cause developer to be classified as academic."""
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({
                "step_index": 0,
                "source": "USER_EXPLICIT",
                "type": "USER_INPUT",
                "content": "<USER_REQUEST>\nFix the test failure in test_agent_hooks.py\n</USER_REQUEST>"
            }) + "\n")
            tf.write(json.dumps({
                "step_index": 1,
                "source": "SYSTEM_SDK",
                "type": "EPHEMERAL_MESSAGE",
                "content": "🚨 CONSTITUTIONAL ENFORCEMENT ACTIVE\n- **Agent**: `academic-orchestrator`"
            }) + "\n")
            tpath = tf.name

        try:
            payload = {
                "conversationId": "dev-poison-test",
                "workspacePaths": [ROOT_DIR],
                "transcriptPath": tpath,
                "toolCall": {
                    "name": "run_command",
                    "args": {"CommandLine": "pytest tests/test_agent_hooks.py"}
                }
            }
            ident = resolve_hook_identity(payload)
            assert ident.is_main_developer is True
            assert ident.track == "track_1_developer"

            res = dispatch_track2_event("PreToolUse", payload)
            assert res.get("decision") == "allow"
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)

    def test_viewed_file_content_does_not_poison_developer_identity(self):
        """Viewing a file containing <identity>academic-orchestrator</identity> must not hijack caller identity."""
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({
                "step_index": 0,
                "source": "USER_EXPLICIT",
                "type": "USER_INPUT",
                "content": "<USER_REQUEST>\nReview the identity contract code\n</USER_REQUEST>"
            }) + "\n")
            tf.write(json.dumps({
                "step_index": 1,
                "source": "MODEL",
                "type": "PLANNER_RESPONSE",
                "tool_calls": [{"name": "view_file", "args": {"AbsolutePath": "contracts/hook_identity_contract.py"}}]
            }) + "\n")
            tf.write(json.dumps({
                "step_index": 2,
                "source": "MODEL",
                "type": "GENERIC",
                "content": "File Path: contracts/hook_identity_contract.py\nif '<identity>' in content:\n  return 'academic-orchestrator'"
            }) + "\n")
            tpath = tf.name

        try:
            payload = {
                "conversationId": "dev-view-test",
                "workspacePaths": [ROOT_DIR],
                "transcriptPath": tpath,
                "toolCall": {
                    "name": "replace_file_content",
                    "args": {"TargetFile": "/path/to/file.py", "Instruction": "fix"}
                }
            }
            ident = resolve_hook_identity(payload)
            assert ident.is_main_developer is True
            assert ident.track == "track_1_developer"

            res = dispatch_track2_event("PreToolUse", payload)
            assert res.get("decision") == "allow"
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)


class TestAcademicOrchestratorGovernance:
    """Verifies that Academic Orchestrator remains strictly governed and non-executing."""

    def test_academic_orchestrator_denied_run_command(self):
        """academic-orchestrator must be denied direct run_command (Directive 20)."""
        payload = {
            "conversationId": "orch-001",
            "workspacePaths": [ROOT_DIR],
            "agentName": "academic-orchestrator",
            "track": 2,
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": "python3 script.py"}
            }
        }
        res = dispatch_track2_event("PreToolUse", payload)
        assert res.get("decision") == "deny"
        assert "Directive 2" in res.get("reason", "") or "strictly forbidden" in res.get("reason", "")

    def test_academic_orchestrator_allowed_invoke_subagent(self):
        """academic-orchestrator must be allowed to invoke specialist subagents."""
        payload = {
            "conversationId": "orch-002",
            "workspacePaths": [ROOT_DIR],
            "agentName": "academic-orchestrator",
            "track": 2,
            "toolCall": {
                "name": "invoke_subagent",
                "args": {
                    "Subagents": [
                        {
                            "TypeName": "academic-writer",
                            "Prompt": '{"contract_version": "1.0.0", "task_id": "TSK-001", "worker_agent": "academic-writer", "objective": "Draft chapter", "inputs": ["data.xlsx"], "required_artifacts": ["draft.md"]}'
                        }
                    ]
                }
            }
        }
        res = dispatch_track2_event("PreToolUse", payload)
        assert res.get("decision") != "deny"
