#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/architecture/test_hook_identity_resolution.py — Multi-Signal Hook Identity Contract Verification

Verifies:
1. Schema conformity across all 6 captured hook payload fixtures:
   - main_antigravity.json
   - custom_main_agent.json
   - custom_subagent.json
   - cli.json
   - ide.json
   - official_minimal.json
2. Multi-signal resolution precedence (explicit payload > environment variables > transcript > path > fail-closed default).
3. Fail-closed default boundary enforcement for unvetted or minimal payloads.
4. Hook dispatcher end-to-end integration and dual-track isolation.
"""

import os
import sys
import json
import tempfile
import pytest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
AGENTS_DIR = os.path.abspath(os.path.join(ROOT_DIR, ".agents"))
FIXTURES_DIR = os.path.abspath(os.path.join(AGENTS_DIR, "contracts", "fixtures", "hook_payloads"))

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if AGENTS_DIR not in sys.path:
    sys.path.insert(0, AGENTS_DIR)

from contracts.hook_identity_contract import (
    HookIdentity,
    resolve_hook_identity,
    validate_hook_payload_schema,
    detect_interface,
    extract_subagent_info,
    is_main_agent_developer,
    resolve_transcript_path,
    SURFACE_APP_DATA_DIRS
)
from hooks.track1_developer_dispatcher import dispatch_track1_event
from hooks.track2_academic_dispatcher import dispatch_track2_event

def dispatch_event(event: str, payload: dict) -> dict:
    if is_main_agent_developer(payload) or payload.get("track") == 1:
        return dispatch_track1_event(event, payload)
    return dispatch_track2_event(event, payload)

dispatcher_is_main = is_main_agent_developer


def load_fixture(fixture_name: str) -> dict:
    path = os.path.join(FIXTURES_DIR, fixture_name)
    assert os.path.exists(path), f"Fixture not found: {path}"
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


class TestHookPayloadSchemaValidation:
    """Verifies that all 6 standardized hook payload fixtures strictly conform to the schema."""

    FIXTURE_NAMES = [
        "main_antigravity.json",
        "custom_main_agent.json",
        "custom_subagent.json",
        "cli.json",
        "ide.json",
        "official_minimal.json"
    ]

    @pytest.mark.parametrize("fixture_name", FIXTURE_NAMES)
    def test_fixture_schema_conformity(self, fixture_name: str):
        payload = load_fixture(fixture_name)
        is_valid, errors = validate_hook_payload_schema(payload)
        assert is_valid, f"Schema validation failed for {fixture_name}: {errors}"
        assert errors == [], f"Unexpected validation errors for {fixture_name}: {errors}"

    def test_schema_rejects_missing_required_fields(self):
        invalid_payload = {"stepIdx": 1}
        is_valid, errors = validate_hook_payload_schema(invalid_payload)
        assert not is_valid
        assert len(errors) > 0


class TestHookIdentityResolutionFixtures:
    """Verifies identity resolution behavior across the 6 captured payload fixtures."""

    def test_main_antigravity_fixture(self):
        payload = load_fixture("main_antigravity.json")
        identity = resolve_hook_identity(payload)
        assert identity.is_main_developer is True
        assert identity.track == "track_1_developer"
        assert identity.interface == "desktop_or_web"
        assert identity.is_subagent is False
        assert identity.confidence == "high"
        assert identity.resolution_source == "explicit_payload"

    def test_custom_main_agent_fixture(self):
        payload = load_fixture("custom_main_agent.json")
        identity = resolve_hook_identity(payload)
        assert identity.is_main_developer is False
        assert identity.track == "track_2_academic"
        assert identity.agent_name == "academic-orchestrator"
        assert identity.is_subagent is False
        assert identity.confidence == "high"

    def test_custom_subagent_fixture(self):
        payload = load_fixture("custom_subagent.json")
        identity = resolve_hook_identity(payload)
        assert identity.is_main_developer is False
        assert identity.track == "track_2_academic"
        assert identity.agent_name == "statistics-agent"
        assert identity.is_subagent is True
        assert identity.parent_conversation_id == "326940d3-3f79-47c6-ac67-d358fe2ccadf"

    def test_cli_fixture(self):
        payload = load_fixture("cli.json")
        identity = resolve_hook_identity(payload)
        assert identity.is_main_developer is True
        assert identity.track == "track_1_developer"
        assert identity.interface == "cli"
        assert identity.is_subagent is False

    def test_ide_fixture(self):
        payload = load_fixture("ide.json")
        identity = resolve_hook_identity(payload)
        assert identity.is_main_developer is True
        assert identity.track == "track_1_developer"
        assert identity.interface == "ide"
        assert identity.is_subagent is False

    def test_official_minimal_fixture_fails_closed(self):
        """The official minimal payload contains no identity markers; it must fail-closed."""
        payload = load_fixture("official_minimal.json")
        identity = resolve_hook_identity(payload)
        assert identity.is_main_developer is False
        assert identity.track == "unknown"
        assert identity.confidence == "fail_closed_default"
        assert identity.resolution_source == "fail_closed_default"


class TestMultiSignalResolutionPrecedence:
    """Verifies that environment variables, transcript analysis, and fail-closed defaults operate correctly."""

    def test_env_var_academic_orchestrator(self):
        minimal_payload = load_fixture("official_minimal.json")
        env = {"ANTIGRAVITY_AGENT_NAME": "academic-orchestrator"}
        identity = resolve_hook_identity(minimal_payload, env=env)
        assert identity.is_main_developer is False
        assert identity.track == "track_2_academic"
        assert identity.agent_name == "academic-orchestrator"
        assert identity.resolution_source == "environment_variable"

    def test_env_var_developer_track(self):
        minimal_payload = load_fixture("official_minimal.json")
        env = {"ANTIGRAVITY_TRACK": "1", "ANTIGRAVITY_MODE": "developer"}
        identity = resolve_hook_identity(minimal_payload, env=env)
        assert identity.is_main_developer is True
        assert identity.track == "track_1_developer"
        assert identity.resolution_source == "environment_variable"

    def test_subagent_blocked_from_main_developer_exemption_even_with_track_1(self):
        payload = {
            "conversationId": "subagent-1234",
            "workspacePaths": ["/workspace"],
            "track": 1,
            "isSubagent": True,
            "parentConversationId": "parent-root"
        }
        identity = resolve_hook_identity(payload)
        assert identity.is_subagent is True
        assert identity.is_main_developer is False  # Invariant: subagents cannot hold root developer exemption

    def test_transcript_inspection_resolves_built_in_developer(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            transcript_file = os.path.join(tmpdir, "transcript.jsonl")
            with open(transcript_file, "w", encoding="utf-8") as f:
                f.write(json.dumps({
                    "step_index": 0,
                    "content": "<identity>You are Antigravity, a powerful agentic AI coding assistant.</identity>"
                }) + "\n")

            payload = {
                "conversationId": "trans-123",
                "workspacePaths": ["/workspace"],
                "transcriptPath": transcript_file
            }
            identity = resolve_hook_identity(payload, env={})
            assert identity.is_main_developer is True
            assert identity.track == "track_1_developer"
            assert identity.resolution_source == "transcript_analysis"

    def test_transcript_inspection_resolves_academic_orchestrator(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            transcript_file = os.path.join(tmpdir, "transcript.jsonl")
            with open(transcript_file, "w", encoding="utf-8") as f:
                f.write(json.dumps({
                    "step_index": 0,
                    "content": "<identity>You are academic-orchestrator, coordinating multi-agent thesis pipelines.</identity>"
                }) + "\n")

            payload = {
                "conversationId": "trans-456",
                "workspacePaths": ["/workspace"],
                "transcriptPath": transcript_file
            }
            identity = resolve_hook_identity(payload, env={})
            assert identity.is_main_developer is False
            assert identity.track == "track_2_academic"
            assert identity.agent_name == "academic-orchestrator"
            assert identity.resolution_source == "transcript_analysis"


class TestInterfaceDetection:
    """Verifies runtime interface detection across CLI, IDE, and Desktop/Web."""

    def test_detect_cli_interface(self):
        payload = {
            "transcriptPath": "/home/user/.gemini/antigravity-cli/brain/123/transcript.jsonl",
            "artifactDirectoryPath": "/home/user/.gemini/antigravity-cli/brain/123"
        }
        assert detect_interface(payload) == "cli"

    def test_detect_ide_interface(self):
        payload = {
            "transcriptPath": "/home/user/.gemini/antigravity-ide/brain/456/transcript.jsonl",
            "artifactDirectoryPath": "/home/user/.gemini/antigravity-ide/brain/456"
        }
        assert detect_interface(payload) == "ide"

    def test_detect_desktop_or_web_interface(self):
        payload = {
            "transcriptPath": "/home/user/.gemini/antigravity/brain/789/transcript.jsonl",
            "artifactDirectoryPath": "/home/user/.gemini/antigravity/brain/789"
        }
        assert detect_interface(payload) == "desktop_or_web"


class TestHookDispatcherDualTrackEnforcement:
    """Verifies that track dispatchers correctly integrate resolve_hook_identity."""

    def test_main_developer_stop_hook_immediately_allowed(self):
        payload = load_fixture("main_antigravity.json")
        res = dispatch_event("Stop", payload)
        assert res.get("decision") == "allow"

    def test_official_minimal_stop_hook_fails_closed_into_governed_checks(self):
        payload = load_fixture("official_minimal.json")
        # In a clean workspace with no violated files, governed check returns allow or continue
        assert dispatcher_is_main(payload) is False

    def test_academic_orchestrator_pre_tool_use_blocks_run_command(self):
        payload = {
            "conversationId": "orch-123",
            "workspacePaths": [ROOT_DIR],
            "agentName": "academic-orchestrator",
            "track": 2,
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": "python3 script.py"}
            }
        }
        res = dispatch_event("PreToolUse", payload)
        assert res.get("decision") == "deny"
        assert "strictly forbidden from executing shell commands" in res.get("reason", "")

    def test_main_developer_pre_tool_use_allows_run_command(self):
        payload = {
            "conversationId": "dev-123",
            "workspacePaths": [ROOT_DIR],
            "agentName": "default",
            "track": 1,
            "mode": "developer",
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": "pytest tests/"}
            }
        }
        res = dispatch_event("PreToolUse", payload)
        assert res.get("decision") != "deny"


class TestSurfaceAwareTranscriptResolution:
    """Verifies that transcriptPath is prioritized directly and fallback is surface-aware."""

    def test_direct_runtime_transcript_path_is_prioritized(self):
        """When transcriptPath is provided by runtime, use it directly without alteration."""
        payload = {
            "conversationId": "cid-direct-101",
            "workspacePaths": [ROOT_DIR],
            "transcriptPath": "/var/log/custom/special_transcript.jsonl",
            "artifactDirectoryPath": "/var/artifacts/desk"
        }
        res = resolve_transcript_path(payload)
        assert res == "/var/log/custom/special_transcript.jsonl"

    def test_derive_from_artifact_directory_path(self):
        """When transcriptPath is absent, derive from artifactDirectoryPath if present."""
        payload = {
            "conversationId": "cid-artifact-202",
            "workspacePaths": [ROOT_DIR],
            "artifactDirectoryPath": "/tmp/custom_brain/cid-artifact-202"
        }
        res = resolve_transcript_path(payload)
        assert res == "/tmp/custom_brain/cid-artifact-202/.system_generated/logs/transcript.jsonl"

    def test_surface_aware_cli_fallback(self):
        """When transcriptPath is absent and surface is CLI, derive under ~/.gemini/antigravity-cli."""
        payload = {
            "conversationId": "cid-cli-303",
            "workspacePaths": [ROOT_DIR]
        }
        env = {"ANTIGRAVITY_SURFACE": "cli"}
        res = resolve_transcript_path(payload, env=env)
        expected = os.path.expanduser("~/.gemini/antigravity-cli/brain/cid-cli-303/.system_generated/logs/transcript.jsonl")
        assert res == expected

    def test_surface_aware_ide_fallback(self):
        """When transcriptPath is absent and surface is IDE, derive under ~/.gemini/antigravity-ide."""
        payload = {
            "conversationId": "cid-ide-404",
            "workspacePaths": [ROOT_DIR]
        }
        env = {"ANTIGRAVITY_SURFACE": "ide"}
        res = resolve_transcript_path(payload, env=env)
        expected = os.path.expanduser("~/.gemini/antigravity-ide/brain/cid-ide-404/.system_generated/logs/transcript.jsonl")
        assert res == expected

    def test_surface_aware_desktop_fallback(self):
        """When transcriptPath is absent and surface is Desktop, derive under ~/.gemini/antigravity."""
        payload = {
            "conversationId": "cid-desk-505",
            "workspacePaths": [ROOT_DIR]
        }
        env = {"ANTIGRAVITY_SURFACE": "desktop"}
        res = resolve_transcript_path(payload, env=env)
        expected = os.path.expanduser("~/.gemini/antigravity/brain/cid-desk-505/.system_generated/logs/transcript.jsonl")
        assert res == expected

    def test_multi_surface_on_disk_discovery(self):
        """When transcriptPath is absent, scans across surfaces and returns existing file on disk."""
        cid = "cid-disk-discovery-606"
        ide_log_dir = os.path.expanduser(f"~/.gemini/antigravity-ide/brain/{cid}/.system_generated/logs")
        os.makedirs(ide_log_dir, exist_ok=True)
        ide_transcript_file = os.path.join(ide_log_dir, "transcript.jsonl")
        try:
            with open(ide_transcript_file, "w", encoding="utf-8") as f:
                f.write('{"type": "PLANNER_RESPONSE", "content": "test"}\n')

            payload = {
                "conversationId": cid,
                "workspacePaths": [ROOT_DIR]
            }
            # Surface unknown: will check desktop, cli, ide in order and find the existing file in ide
            res = resolve_transcript_path(payload, env={})
            assert res == ide_transcript_file
        finally:
            if os.path.exists(ide_transcript_file):
                os.remove(ide_transcript_file)
            brain_dir = os.path.expanduser(f"~/.gemini/antigravity-ide/brain/{cid}")
            if os.path.exists(brain_dir):
                import shutil
                shutil.rmtree(brain_dir)

    def test_env_var_app_data_dir_override(self):
        """When ANTIGRAVITY_APP_DATA_DIR is set, resolves under the specified directory."""
        payload = {
            "conversationId": "cid-env-707",
            "workspacePaths": [ROOT_DIR]
        }
        with tempfile.TemporaryDirectory() as tmpdir:
            env = {"ANTIGRAVITY_APP_DATA_DIR": tmpdir}
            log_dir = os.path.join(tmpdir, "brain", "cid-env-707", ".system_generated", "logs")
            os.makedirs(log_dir, exist_ok=True)
            custom_file = os.path.join(log_dir, "transcript.jsonl")
            with open(custom_file, "w", encoding="utf-8") as f:
                f.write('{"type": "USER_INPUT", "content": "hi"}\n')

            res = resolve_transcript_path(payload, env=env)
            assert res == custom_file

