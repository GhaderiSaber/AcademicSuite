#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_canonical_tools_sync.py — Test Suite for Canonical Tools SSOT and Synchronization

Verifies:
1. Canonical Antigravity tool taxonomy (21 tools, precise categorization).
2. Lifecycle hook matcher generation and synchronization with .agents/hooks.json.
3. multi_replace_file_content enforcement across safety hooks (raw data, state ledger, ASCII filenames).
4. Non-writing agent policy enforcement forbidding multi_replace_file_content.
5. 100% concordance between agent declarations and canonical vocabulary.
"""

import os
import sys
import json
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if AGENTS_DIR not in sys.path:
    sys.path.insert(0, AGENTS_DIR)

from contracts.canonical_tools import (
    CANONICAL_ANTIGRAVITY_TOOLS,
    CANONICAL_FILE_READ_TOOLS,
    CANONICAL_FILE_MUTATION_TOOLS,
    CANONICAL_DIRECT_EXECUTION_TOOLS,
    CANONICAL_INDIRECT_EXECUTION_TOOLS,
    CANONICAL_DELEGATION_TOOLS,
    CANONICAL_INTERACTION_TOOLS,
    CANONICAL_WEB_MEDIA_TOOLS,
    CANONICAL_MCP_RESOURCE_TOOLS,
    LEGACY_OR_ALIAS_MUTATION_TOOLS,
    ALL_MUTATION_TOOLS,
    HOOK_INTERCEPTED_TOOLS,
    generate_hook_matcher,
    validate_hooks_json,
    sync_hooks_json,
    get_hooks_json_path,
)
from hooks.safety_hooks import (
    MUTATION_TOOLS,
    extract_target_paths,
    SafetyHooks,
)
from contracts.agents.capability_policy import (
    load_capability_policy,
    validate_policy_schema,
    validate_agent_against_policy,
)
from scripts.orchestrator_invariants import FORBIDDEN_ORCHESTRATOR_TOOLS


class TestCanonicalToolTaxonomy:
    """Validates the canonical Antigravity tool taxonomy."""

    def test_canonical_tool_count_and_completeness(self):
        """Authoritative Antigravity environment has exactly 21 canonical tools."""
        expected_21_tools = {
            "view_file", "list_dir", "grep_search", "find_by_name",
            "write_to_file", "replace_file_content", "multi_replace_file_content",
            "run_command", "manage_task", "schedule",
            "invoke_subagent", "manage_subagents", "send_message", "define_subagent",
            "ask_question", "read_url_content", "search_web", "generate_image",
            "call_mcp_tool", "list_resources", "read_resource"
        }
        assert CANONICAL_ANTIGRAVITY_TOOLS == expected_21_tools
        assert len(CANONICAL_ANTIGRAVITY_TOOLS) == 21

    def test_canonical_file_mutation_tools(self):
        """Canonical file mutation tools must include multi_replace_file_content."""
        assert CANONICAL_FILE_MUTATION_TOOLS == {
            "write_to_file",
            "replace_file_content",
            "multi_replace_file_content",
        }

    def test_all_mutation_tools_includes_aliases(self):
        """ALL_MUTATION_TOOLS contains canonical and legacy aliases for fail-closed safety."""
        assert "multi_replace_file_content" in ALL_MUTATION_TOOLS
        assert "write_to_file" in ALL_MUTATION_TOOLS
        assert "replace_file_content" in ALL_MUTATION_TOOLS
        assert "edit_file" in ALL_MUTATION_TOOLS
        assert "apply_diff" in ALL_MUTATION_TOOLS
        assert CANONICAL_FILE_MUTATION_TOOLS.issubset(ALL_MUTATION_TOOLS)
        assert LEGACY_OR_ALIAS_MUTATION_TOOLS.issubset(ALL_MUTATION_TOOLS)


class TestHooksJsonSynchronization:
    """Validates .agents/hooks.json synchronization with canonical tools SSOT."""

    def test_hooks_json_is_100_percent_valid(self):
        """Disk .agents/hooks.json must match generate_hook_matcher() with zero discrepancies."""
        is_valid, issues = validate_hooks_json()
        assert is_valid is True, f"hooks.json validation failed: {issues}"
        assert len(issues) == 0

    def test_multi_replace_file_content_is_in_hook_matchers(self):
        """PreToolUse and PostToolUse matchers must explicitly include multi_replace_file_content."""
        hooks_path = get_hooks_json_path()
        with open(hooks_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        guard = data["constitutional-guard"]
        pre_matcher = guard["PreToolUse"][0]["matcher"]
        post_matcher = guard["PostToolUse"][0]["matcher"]

        assert "multi_replace_file_content" in pre_matcher.split("|")
        assert "multi_replace_file_content" in post_matcher.split("|")

    def test_sync_hooks_json_idempotence(self):
        """sync_hooks_json() must be idempotent."""
        assert sync_hooks_json() is True
        is_valid, issues = validate_hooks_json()
        assert is_valid is True
        assert len(issues) == 0


class TestSafetyHooksMultiReplaceEnforcement:
    """Validates that safety hooks enforce all invariants on multi_replace_file_content."""

    def test_multi_replace_in_safety_hooks_mutation_tools(self):
        """safety_hooks.MUTATION_TOOLS must contain multi_replace_file_content."""
        assert "multi_replace_file_content" in MUTATION_TOOLS

    def test_extract_target_paths_handles_multi_replace(self):
        """extract_target_paths must extract TargetFile from multi_replace_file_content arguments."""
        args = {
            "TargetFile": "/workspace/chapter4.docx",
            "ReplacementChunks": [{"StartLine": 1, "EndLine": 5, "TargetContent": "a", "ReplacementContent": "b"}]
        }
        paths = extract_target_paths("multi_replace_file_content", args)
        assert paths == ["/workspace/chapter4.docx"]

    def test_blocks_multi_replace_targeting_raw_data(self):
        """multi_replace_file_content targeting raw data must be denied."""
        payload = {
            "agentName": "statistics-agent",
            "toolCall": {
                "name": "multi_replace_file_content",
                "args": {
                    "TargetFile": "/workspace/01_raw_inputs/raw_data.xlsx",
                    "ReplacementChunks": []
                }
            }
        }
        res = SafetyHooks.handle_pre_tool_use(payload)
        assert res.get("decision") == "deny"
        assert "Raw datasets are immutable" in res.get("reason", "") or "raw dataset" in res.get("reason", "").lower()

    def test_blocks_multi_replace_targeting_state_ledger(self):
        """multi_replace_file_content targeting state ledger files must be denied."""
        for state_file in ("current_state.json", "events.jsonl", "approvals.json"):
            payload = {
                "agentName": "statistics-agent",
                "toolCall": {
                    "name": "multi_replace_file_content",
                    "args": {
                        "TargetFile": f"/workspace/academic-state/{state_file}",
                        "ReplacementChunks": []
                    }
                }
            }
            res = SafetyHooks.handle_pre_tool_use(payload)
            assert res.get("decision") == "deny"
            assert "state ledger" in res.get("reason", "").lower()

    def test_blocks_multi_replace_for_non_writing_agents(self):
        """Agents with can_write_files: false must be denied multi_replace_file_content."""
        for agent in ("academic-orchestrator", "test-orchestrator", "digital-saber", "methodology-expert"):
            payload = {
                "agentName": agent,
                "toolCall": {
                    "name": "multi_replace_file_content",
                    "args": {
                        "TargetFile": "/workspace/output.md",
                        "ReplacementChunks": []
                    }
                }
            }
            res = SafetyHooks.handle_pre_tool_use(payload)
            assert res.get("decision") == "deny"
            reason = res.get("reason", "")
            assert any(phrase in reason for phrase in (
                "forbidden from writing",
                "forbidden from mutating",
                "not permitted to write",
                "can_write_files",
                "Orchestrator Code Guard"
            ))

    def test_blocks_multi_replace_for_learning_subagents(self):
        """Learning subagents must be denied non-JSON file writing."""
        for agent in ("behavior-analyst", "trajectory-analyzer", "knowledge-curator", "skill-evolver"):
            payload = {
                "agentName": agent,
                "toolCall": {
                    "name": "multi_replace_file_content",
                    "args": {
                        "TargetFile": "/workspace/output.md",
                        "ReplacementChunks": []
                    }
                }
            }
            res = SafetyHooks.handle_pre_tool_use(payload)
            assert res.get("decision") == "deny"
            assert "Learning Subagent" in res.get("reason", "")


    def test_blocks_multi_replace_with_non_ascii_filename(self):
        """multi_replace_file_content with non-ASCII filename must be denied (Directive 6)."""
        payload = {
            "agentName": "statistics-agent",
            "toolCall": {
                "name": "multi_replace_file_content",
                "args": {
                    "TargetFile": "/workspace/فصل_چهارم.docx",
                    "ReplacementChunks": []
                }
            }
        }
        res = SafetyHooks.handle_pre_tool_use(payload)
        assert res.get("decision") == "deny"
        assert "Directive 6" in res.get("reason", "")


class TestCapabilityPolicyConcordance:
    """Validates capability policy and agent tool concordance."""

    def test_capability_policy_schema_passes(self):
        """The agent_capabilities.yaml schema validation must pass with zero issues."""
        issues = validate_policy_schema()
        assert issues == [], f"Policy schema issues: {issues}"

    def test_orchestrator_invariants_include_multi_replace(self):
        """FORBIDDEN_ORCHESTRATOR_TOOLS must include multi_replace_file_content."""
        assert "multi_replace_file_content" in FORBIDDEN_ORCHESTRATOR_TOOLS

    def test_all_non_writing_agents_forbid_multi_replace(self):
        """All agents with can_write_files: false must have multi_replace_file_content in forbidden."""
        pol = load_capability_policy()
        for name, spec in pol.get("agents", {}).items():
            if not spec.get("can_write_files", True):
                forb = set(spec.get("forbidden", []))
                assert "multi_replace_file_content" in forb, (
                    f"Agent '{name}' has can_write_files=False but multi_replace_file_content is not in forbidden"
                )
