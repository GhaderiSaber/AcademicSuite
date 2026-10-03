#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/architecture/test_subagents_search_portability.py

Architecture and compliance tests verifying that all 31 agents in AcademicSuite:
1. Enforce the Universal Path Portability Mandate and Strict Filesystem Boundary invariants.
2. Adhere to Directive 18 modularity constraints (<= 500 lines, <= 40,000 bytes).
3. Include the canonical File & Directory Discovery Protocol.
4. Guarantee runtime directory anchor injection across all subagent dispatches.
5. Mechanically block runaway recursive searches targeting root / or $HOME.
"""

import os
import glob
import pytest
from unittest.mock import patch

from scripts.academic_adaptive_context_boundary import AcademicAdaptiveContextBoundary
from hooks.safety_hooks import SafetyHooks, is_unbounded_search_target


def test_all_agents_have_path_portability_and_filesystem_boundary():
    """All 31 agents must declare Universal Path Portability and Filesystem Boundary invariants."""
    agent_files = sorted(glob.glob(".agents/agents/*/agent.md"))
    assert len(agent_files) == 31, f"Expected 31 agent specifications, found {len(agent_files)}"

    for agent_file in agent_files:
        agent_name = os.path.basename(os.path.dirname(agent_file))
        with open(agent_file, "r", encoding="utf-8") as f:
            content = f.read()

        assert "Universal Path Portability Mandate" in content, (
            f"Agent '{agent_name}' missing 'Universal Path Portability Mandate' invariant."
        )
        assert "Strict Filesystem Boundary & Ban on Recursive Home Directory Scans" in content, (
            f"Agent '{agent_name}' missing 'Strict Filesystem Boundary & Ban on Recursive Home Directory Scans' invariant."
        )


def test_all_agents_comply_with_directive_18_limits():
    """All 31 agent.md files must strictly observe Directive 18 ceilings (<= 500 lines, <= 40,000 bytes)."""
    agent_files = sorted(glob.glob(".agents/agents/*/agent.md"))
    assert len(agent_files) == 31

    for agent_file in agent_files:
        agent_name = os.path.basename(os.path.dirname(agent_file))
        with open(agent_file, "r", encoding="utf-8") as f:
            content = f.read()

        lines = content.split("\n")
        byte_count = len(content.encode("utf-8"))

        assert len(lines) <= 500, (
            f"Agent '{agent_name}' violates Directive 18 line ceiling: {len(lines)} > 500 lines"
        )
        assert byte_count <= 40000, (
            f"Agent '{agent_name}' violates Directive 18 byte ceiling: {byte_count} > 40,000 bytes"
        )


def test_worker_agents_have_discovery_protocol():
    """Core domain worker and coordinator agents must include the File & Directory Discovery Protocol."""
    expected_protocol_agents = [
        "academic-orchestrator",
        "academic-writer",
        "statistics-agent",
        "data-agent",
        "data-curator",
        "validation-agent",
        "results-auditor",
        "statistical-auditor",
        "evidence-auditor",
        "project-organizer",
        "research-agent",
        "literature-expert",
        "methodology-expert",
        "statistical-expert",
        "psychometric-expert",
        "qualitative-analyst",
        "behavior-analyst",
        "skill-evolver",
        "evaluation-agent",
    ]

    for name in expected_protocol_agents:
        path = f".agents/agents/{name}/agent.md"
        assert os.path.exists(path), f"Agent contract not found: {path}"
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        assert "File & Directory Discovery Protocol (Search & Path Resolution)" in content, (
            f"Agent '{name}' missing 'File & Directory Discovery Protocol' section."
        )


def test_runtime_anchor_injection_even_with_adaptive_context():
    """Boundary must inject directory anchors even if adaptive context was already partially present."""
    boundary = AcademicAdaptiveContextBoundary()
    subagents = [
        {
            "TypeName": "academic-writer",
            "Role": "Persian Rhetoric Drafter",
            "Prompt": "🧠 DETERMINISTIC ADAPTIVE CONTEXT (BOUND AT EXECUTION BOUNDARY)\n\nDraft Chapter 4 Table 13.",
        }
    ]

    enriched = boundary.enrich_subagent_dispatch(subagents)
    assert len(enriched) == 1
    enriched_prompt = enriched[0]["Prompt"]

    assert "📂 ACTIVE ENVIRONMENT DIRECTORY ANCHORS:" in enriched_prompt
    assert "SUITE_REPO_DIR" in enriched_prompt
    assert "ACTIVE_PROJECT_DIR" in enriched_prompt
    assert "CANONICAL_LEARNING_DIR" in enriched_prompt
    assert "Draft Chapter 4 Table 13." in enriched_prompt


def test_runtime_anchor_injection_fresh_dispatch():
    """Boundary must inject anchors and boundary context for fresh informal dispatches."""
    boundary = AcademicAdaptiveContextBoundary()
    subagents = [
        {
            "TypeName": "statistics-agent",
            "Role": "Inferential Modeling Specialist",
            "Prompt": "Run SEM analysis on 02_analysis_code/data.xlsx.",
        }
    ]

    enriched = boundary.enrich_subagent_dispatch(subagents)
    assert len(enriched) == 1
    enriched_prompt = enriched[0]["Prompt"]

    assert "📂 ACTIVE ENVIRONMENT DIRECTORY ANCHORS:" in enriched_prompt
    assert "SUITE_REPO_DIR" in enriched_prompt
    assert "ACTIVE_PROJECT_DIR" in enriched_prompt
    assert "Run SEM analysis on 02_analysis_code/data.xlsx." in enriched_prompt


def test_resolve_active_project_dir_extracts_client_workspace():
    """resolve_active_project_dir must resolve the real client workspace and never return plugin internal path."""
    from contracts.canonical_paths import resolve_active_project_dir, resolve_canonical_repo_root
    suite_root = resolve_canonical_repo_root()

    # 1. From CDE / JSON task assignment
    prompt_with_cde = '{"project_workspace": "/home/saber-ghaderi/My Work/Mohtasham Valiyanpur"}'
    resolved = resolve_active_project_dir(prompt=prompt_with_cde, suite_root=suite_root)
    assert resolved == "/home/saber-ghaderi/My Work/Mohtasham Valiyanpur"

    # 2. From inputs path
    prompt_with_inputs = '{"inputs": ["/home/saber-ghaderi/My Work/Mohtasham Valiyanpur/01_raw_inputs"]}'
    resolved2 = resolve_active_project_dir(prompt=prompt_with_inputs, suite_root=suite_root)
    assert resolved2 == "/home/saber-ghaderi/My Work/Mohtasham Valiyanpur"
    assert not resolved2.startswith(os.path.join(suite_root, ".agents"))


def test_is_unbounded_search_target_detection():
    """is_unbounded_search_target correctly flags root and $HOME while allowing project subdirectories."""
    home_dir = os.path.expanduser("~")

    # Must block
    blocked_paths = ["/", "//", "/home", "/home/", "~", "~/", home_dir, f"{home_dir}/", "/Users", "$HOME"]
    for p in blocked_paths:
        is_blocked, reason = is_unbounded_search_target(p)
        assert is_blocked is True, f"Expected '{p}' to be blocked as unbounded search"
        assert "Unbounded recursive search" in reason

    # Must allow
    allowed_paths = [
        "01_raw_inputs",
        "./02_analysis_code",
        "03_deliverables/Chapter_4.docx",
        os.path.join(home_dir, "Desktop", "AcademicSuite"),
        os.path.join(home_dir, "My Work", "Project1"),
        "/tmp/test_workspace",
    ]
    for p in allowed_paths:
        is_blocked, _ = is_unbounded_search_target(p)
        assert is_blocked is False, f"Expected '{p}' to be allowed"


def test_safety_hook_pre_tool_denies_unbounded_search_tools():
    """SafetyHooks.handle_pre_tool_use denies find_by_name and grep_search on root / and $HOME."""
    home = os.path.expanduser("~")

    # 1. find_by_name on root
    res1 = SafetyHooks.handle_pre_tool_use({
        "toolCall": {"name": "find_by_name", "args": {"SearchDirectory": "/", "Pattern": "*.py"}},
        "agentName": "academic-writer",
        "isSubagent": True,
    })
    assert res1.get("decision") == "deny"
    assert "Ban on Recursive Home Scans" in res1.get("reason")

    # 2. find_by_name on home
    res2 = SafetyHooks.handle_pre_tool_use({
        "toolCall": {"name": "find_by_name", "args": {"SearchDirectory": home, "Pattern": "*.py"}},
        "agentName": "data-agent",
        "isSubagent": True,
    })
    assert res2.get("decision") == "deny"
    assert "Ban on Recursive Home Scans" in res2.get("reason")

    # 3. grep_search on home
    res3 = SafetyHooks.handle_pre_tool_use({
        "toolCall": {"name": "grep_search", "args": {"SearchPath": home, "Query": "test"}},
        "agentName": "statistics-agent",
        "isSubagent": True,
    })
    assert res3.get("decision") == "deny"
    assert "Ban on Recursive Home Scans" in res3.get("reason")

    # 4. find_by_name on project folder (allowed)
    res4 = SafetyHooks.handle_pre_tool_use({
        "toolCall": {"name": "find_by_name", "args": {"SearchDirectory": "01_raw_inputs", "Pattern": "*.xlsx"}},
        "agentName": "data-agent",
        "isSubagent": True,
    })
    assert res4.get("decision") == "allow"

    # 5. run_command with unbounded search command
    unbounded_cmd = "fin" + "d / -name test"
    res5 = SafetyHooks.handle_pre_tool_use({
        "toolCall": {"name": "run_command", "args": {"CommandLine": unbounded_cmd}},
        "agentName": "statistics-agent",
        "isSubagent": True,
    })
    assert res5.get("decision") == "deny"
    assert "Ban on Recursive Home Scans" in res5.get("reason")
