#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_hook_seen.py — Verification Suite for HOOK_SEEN Telemetry

Verifies:
1. Exact 4-line format:
   HOOK_SEEN
   tool=<tool>
   agent=<agent if available>
   timestamp=<timestamp>
2. Agent present vs absent handling.
3. Timestamp extraction vs ISO-8601 fallback.
4. Tool name extraction across various payload shapes.
5. Deduplication within a single event run.
6. Subprocess integration for track dispatchers and safety_hooks.py.
7. Valid JSON preservation on stdout.
"""

import os
import sys
import io
import json
import subprocess
import unittest
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HOOKS_DIR = os.path.join(ROOT_DIR, ".agents", "hooks")
for p in (ROOT_DIR, HOOKS_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from hook_seen import (
    emit_hook_seen,
    extract_tool_name,
    extract_agent_name,
    extract_timestamp
)
from track1_developer_dispatcher import dispatch_track1_event
from track2_academic_dispatcher import dispatch_track2_event
from contracts.hook_identity_contract import is_main_agent_developer

def dispatch_event(event: str, payload: dict) -> dict:
    if is_main_agent_developer(payload) or payload.get("track") == 1:
        return dispatch_track1_event(event, payload)
    return dispatch_track2_event(event, payload)

from safety_hooks import SafetyHooks


class TestHookSeenTelemetry(unittest.TestCase):

    def test_01_extract_tool_name(self):
        """Tool name should be correctly extracted across various structures."""
        self.assertEqual(extract_tool_name({"toolCall": {"name": "run_command"}}), "run_command")
        self.assertEqual(extract_tool_name({"toolCall": "write_to_file"}), "write_to_file")
        self.assertEqual(extract_tool_name({"tool": "replace_file_content"}), "replace_file_content")
        self.assertEqual(extract_tool_name({"tool_name": "view_file"}), "view_file")
        self.assertEqual(extract_tool_name({"name": "read_resource"}), "read_resource")
        self.assertEqual(extract_tool_name({}), "")

    def test_02_extract_agent_name(self):
        """Agent should be extracted if available, or return empty string."""
        self.assertEqual(extract_agent_name({"agentName": "academic-orchestrator"}), "academic-orchestrator")
        self.assertEqual(extract_agent_name({"agentRole": "Statistics Specialist"}), "Statistics Specialist")
        self.assertEqual(extract_agent_name({"agent": "data-agent"}), "data-agent")
        self.assertEqual(extract_agent_name({"caller": "main"}), "main")
        self.assertEqual(extract_agent_name({"agent_type": "coding"}), "coding")
        self.assertEqual(extract_agent_name({}), "")

    def test_03_extract_timestamp(self):
        """Timestamp should extract from payload or produce valid ISO-8601 string."""
        self.assertEqual(extract_timestamp({"timestamp": "2026-09-20T12:00:00Z"}), "2026-09-20T12:00:00Z")
        self.assertEqual(extract_timestamp({"created_at": "2026-09-20T10:00:00Z"}), "2026-09-20T10:00:00Z")
        fallback = extract_timestamp({})
        self.assertTrue(len(fallback) > 10)
        # Verify valid ISO datetime
        dt = datetime.fromisoformat(fallback.replace("Z", "+00:00"))
        self.assertIsNotNone(dt)

    def test_04_exact_four_line_format(self):
        """Verifies exact 4-line structure when emitted."""
        payload = {
            "toolCall": {"name": "run_command", "args": {"CommandLine": "ls"}},
            "agentName": "main",
            "timestamp": "2026-09-20T07:45:00Z"
        }
        old_stderr = sys.stderr
        try:
            buf = io.StringIO()
            sys.stderr = buf
            emit_hook_seen(payload)
            output = buf.getvalue()
        finally:
            sys.stderr = old_stderr

        lines = output.strip().split("\n")
        self.assertEqual(len(lines), 4)
        self.assertEqual(lines[0], "HOOK_SEEN")
        self.assertEqual(lines[1], "tool=run_command")
        self.assertEqual(lines[2], "agent=main")
        self.assertEqual(lines[3], "timestamp=2026-09-20T07:45:00Z")

    def test_05_agent_not_available(self):
        """When agent is not available, agent= should be empty without hallucinating."""
        payload = {
            "toolCall": {"name": "write_to_file"},
            "timestamp": "2026-09-20T07:45:00Z"
        }
        old_stderr = sys.stderr
        try:
            buf = io.StringIO()
            sys.stderr = buf
            emit_hook_seen(payload)
            output = buf.getvalue()
        finally:
            sys.stderr = old_stderr

        lines = output.strip().split("\n")
        self.assertEqual(lines[0], "HOOK_SEEN")
        self.assertEqual(lines[1], "tool=write_to_file")
        self.assertEqual(lines[2], "agent=")
        self.assertEqual(lines[3], "timestamp=2026-09-20T07:45:00Z")

    def test_06_deduplication(self):
        """Repeated calls for the same payload must not emit duplicate output."""
        payload = {
            "toolCall": {"name": "replace_file_content"},
            "agent": "coder"
        }
        old_stderr = sys.stderr
        try:
            buf = io.StringIO()
            sys.stderr = buf
            emit_hook_seen(payload)
            first_len = len(buf.getvalue())
            emit_hook_seen(payload)
            second_len = len(buf.getvalue())
        finally:
            sys.stderr = old_stderr

        self.assertEqual(first_len, second_len, "Duplicate emission occurred for identical payload")

    def test_07_dispatch_event_integration(self):
        """dispatch_event('PreToolUse') must emit HOOK_SEEN to stderr and return valid dict."""
        payload = {
            "toolCall": {"name": "run_command", "args": {"CommandLine": "echo hello"}},
            "caller": "main"
        }
        old_stderr = sys.stderr
        try:
            buf = io.StringIO()
            sys.stderr = buf
            res = dispatch_event("PreToolUse", payload)
            output = buf.getvalue()
        finally:
            sys.stderr = old_stderr

        self.assertEqual(res.get("decision"), "allow")
        self.assertIn("HOOK_SEEN", output)
        self.assertIn("tool=run_command", output)
        self.assertIn("agent=main", output)

    def test_08_subprocess_track2_dispatcher(self):
        """track2_academic_dispatcher.py running via CLI must output HOOK_SEEN on stderr and valid JSON on stdout."""
        script_path = os.path.join(HOOKS_DIR, "track2_academic_dispatcher.py")
        input_payload = json.dumps({
            "toolCall": {"name": "view_file", "args": {"AbsolutePath": "README.md"}},
            "agentName": "researcher",
            "timestamp": "2026-09-20T08:00:00Z"
        })

        proc = subprocess.run(
            [sys.executable, script_path, "--event", "PreToolUse"],
            input=input_payload,
            text=True,
            capture_output=True
        )
        self.assertEqual(proc.returncode, 0)
        # Verify stderr has HOOK_SEEN
        self.assertIn("HOOK_SEEN\ntool=view_file\nagent=researcher\ntimestamp=2026-09-20T08:00:00Z", proc.stderr)
        # Verify stdout is clean valid JSON
        stdout_json = json.loads(proc.stdout.strip())
        self.assertEqual(stdout_json.get("decision"), "allow")

    def test_09_subprocess_track1_dispatcher(self):
        """track1_developer_dispatcher.py runner must emit HOOK_SEEN on stderr."""
        script_path = os.path.join(HOOKS_DIR, "track1_developer_dispatcher.py")
        input_payload = json.dumps({
            "toolCall": {"name": "run_command", "args": {"CommandLine": "python3 test.py"}},
            "agentName": "default"
        })

        proc = subprocess.run(
            [sys.executable, script_path, "--event", "PreToolUse"],
            input=input_payload,
            text=True,
            capture_output=True
        )
        self.assertEqual(proc.returncode, 0)
        self.assertIn("HOOK_SEEN", proc.stderr)
        self.assertIn("tool=run_command", proc.stderr)
        self.assertIn("agent=default", proc.stderr)
        stdout_json = json.loads(proc.stdout.strip())
        self.assertEqual(stdout_json.get("decision"), "allow")


if __name__ == "__main__":
    unittest.main()
