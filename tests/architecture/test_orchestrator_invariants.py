#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/architecture/test_orchestrator_invariants.py — Phase 26 Test Suite

Validates the two permanent architectural laws for academic-orchestrator:
1. Orchestrator Non-Execution Invariant:
   academic-orchestrator MUST NOT possess:
       - run_command
       - write_to_file
       - replace_file_content
       - edit_file

2. Delegation Availability Invariant:
   academic-orchestrator MUST possess:
       - invoke_subagent
"""

import os
import sys
import yaml
import pytest
from typing import Dict, Any, List, Set

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.orchestrator_invariants import (
    ORCHESTRATOR_TARGET_AGENT,
    FORBIDDEN_ORCHESTRATOR_TOOLS,
    REQUIRED_ORCHESTRATOR_TOOLS,
    OrchestratorInvariantViolationError,
    OrchestratorNonExecutionInvariantViolationError,
    DelegationAvailabilityInvariantViolationError,
    verify_orchestrator_non_execution_invariant,
    verify_delegation_availability_invariant,
    verify_orchestrator_invariants,
    audit_orchestrator_frontmatter,
    audit_orchestrator_agent_file
)
from scripts.capability_policy_gate import (
    CapabilityPolicyGate,
    CapabilityPolicyViolationError,
    VIOLATION_ORCHESTRATOR_NON_EXECUTION_INVARIANT,
    VIOLATION_DELEGATION_AVAILABILITY_INVARIANT
)
from validators.agent_integrity import AgentCapabilityValidator, AGENTS_DIR, SKILLS_DIR


# =============================================================================
# 1. Physical Disk Invariant Checks for Canonical academic-orchestrator
# =============================================================================

def test_canonical_orchestrator_on_disk_satisfies_non_execution_invariant():
    """
    Law 1: academic-orchestrator on disk MUST NOT possess:
    - run_command
    - write_to_file
    - replace_file_content
    - edit_file
    """
    agent_path = os.path.join(ROOT_DIR, ".agents", "agents", "academic-orchestrator", "agent.md")
    assert os.path.isfile(agent_path), f"Agent file not found: {agent_path}"

    with open(agent_path, "r", encoding="utf-8") as f:
        content = f.read()

    parts = content.split("---", 2)
    assert len(parts) >= 3, "Failed to parse YAML frontmatter"
    fm = yaml.safe_load(parts[1])
    tools = set(fm.get("tools", []))

    for forbidden in FORBIDDEN_ORCHESTRATOR_TOOLS:
        assert forbidden not in tools, (
            f"VIOLATION of Orchestrator Non-Execution Invariant: "
            f"academic-orchestrator possesses forbidden tool '{forbidden}'"
        )


def test_canonical_orchestrator_on_disk_satisfies_delegation_availability_invariant():
    """
    Law 2: academic-orchestrator on disk MUST possess:
    - invoke_subagent
    """
    agent_path = os.path.join(ROOT_DIR, ".agents", "agents", "academic-orchestrator", "agent.md")
    with open(agent_path, "r", encoding="utf-8") as f:
        content = f.read()

    parts = content.split("---", 2)
    fm = yaml.safe_load(parts[1])
    tools = set(fm.get("tools", []))

    for required in REQUIRED_ORCHESTRATOR_TOOLS:
        assert required in tools, (
            f"VIOLATION of Delegation Availability Invariant: "
            f"academic-orchestrator does not possess required tool '{required}'"
        )


def test_audit_orchestrator_agent_file_passes():
    """Validates that audit_orchestrator_agent_file() returns PASS on canonical agent."""
    verdict = audit_orchestrator_agent_file()
    assert verdict["verdict"] == "PASS"
    assert verdict["agent"] == "academic-orchestrator"
    assert verdict["orchestrator_non_execution_invariant"]["status"] == "PASS"
    assert verdict["delegation_availability_invariant"]["status"] == "PASS"


# =============================================================================
# 2. Functional & Unit Invariant Verifier Tests
# =============================================================================

def test_verify_orchestrator_non_execution_invariant_rejects_each_forbidden_tool():
    """
    Verifies that verify_orchestrator_non_execution_invariant raises
    OrchestratorNonExecutionInvariantViolationError for each forbidden tool.
    """
    valid_tools = ["invoke_subagent", "manage_subagents", "view_file", "ask_question"]

    # Valid toolset passes cleanly
    verify_orchestrator_non_execution_invariant(valid_tools)

    # Each forbidden tool must be rejected
    for forbidden in ["run_command", "write_to_file", "replace_file_content", "edit_file"]:
        violating_tools = valid_tools + [forbidden]
        with pytest.raises(OrchestratorNonExecutionInvariantViolationError) as exc_info:
            verify_orchestrator_non_execution_invariant(violating_tools)
        assert "ORCHESTRATOR_NON_EXECUTION_INVARIANT_VIOLATION" in str(exc_info.value)
        assert forbidden in str(exc_info.value)


def test_verify_delegation_availability_invariant_rejects_missing_invoke_subagent():
    """
    Verifies that verify_delegation_availability_invariant raises
    DelegationAvailabilityInvariantViolationError when invoke_subagent is omitted.
    """
    valid_tools = ["invoke_subagent", "manage_subagents", "view_file"]
    verify_delegation_availability_invariant(valid_tools)

    # Missing invoke_subagent must be rejected
    invalid_tools = ["manage_subagents", "view_file", "ask_question"]
    with pytest.raises(DelegationAvailabilityInvariantViolationError) as exc_info:
        verify_delegation_availability_invariant(invalid_tools)
    assert "DELEGATION_AVAILABILITY_INVARIANT_VIOLATION" in str(exc_info.value)
    assert "invoke_subagent" in str(exc_info.value)


def test_verify_orchestrator_invariants_full_verdict():
    """Validates verify_orchestrator_invariants returns complete structured audit."""
    tools = ["invoke_subagent", "manage_subagents", "view_file"]
    res = verify_orchestrator_invariants(tools)
    assert res["verdict"] == "PASS"
    assert "invoke_subagent" in res["delegation_availability_invariant"]["required_tools_present"]


# =============================================================================
# 3. Capability Policy Gate Integration
# =============================================================================

@pytest.mark.parametrize("forbidden_tool", [
    "run_command",
    "write_to_file",
    "replace_file_content",
    "multi_replace_file_content",
    "edit_file"
])
def test_policy_gate_rejects_adding_forbidden_execution_tool_to_orchestrator(forbidden_tool):
    """
    Verifies that CapabilityPolicyGate categorically rejects candidate patches attempting
    to grant any forbidden execution/file mutation tools to academic-orchestrator.
    """
    candidate = {
        "candidate_id": f"CAND-INVARIANT-TEST-{forbidden_tool.upper()}",
        "target_component": ".agents/agents/academic-orchestrator/agent.md",
        "target_type": "AGENT_SYSTEM_PROMPT",
        "mutation_type": "INSTRUCTION_REFINEMENT",
        "mutation": {
            "diff_type": "UNIFIED_DIFF",
            "content": f"+ - {forbidden_tool}\n+ grant {forbidden_tool} to academic-orchestrator"
        },
        "rationale": f"Grant {forbidden_tool} to orchestrator"
    }

    verdict = CapabilityPolicyGate.evaluate_candidate_patch(candidate)
    assert verdict.decision == "REJECT"
    assert VIOLATION_ORCHESTRATOR_NON_EXECUTION_INVARIANT in verdict.violations

    with pytest.raises(CapabilityPolicyViolationError) as exc_info:
        CapabilityPolicyGate.enforce_capability_policy(candidate)
    assert "CAPABILITY_POLICY_VIOLATION" in str(exc_info.value)
    assert "Orchestrator Non-Execution Invariant" in str(exc_info.value)


def test_policy_gate_rejects_removing_invoke_subagent_from_orchestrator():
    """
    Verifies that CapabilityPolicyGate categorically rejects candidate patches attempting
    to strip or remove invoke_subagent from academic-orchestrator.
    """
    candidate = {
        "candidate_id": "CAND-INVARIANT-TEST-STRIP-INVOKE",
        "target_component": ".agents/agents/academic-orchestrator/agent.md",
        "target_type": "AGENT_SYSTEM_PROMPT",
        "mutation_type": "INSTRUCTION_REFINEMENT",
        "mutation": {
            "diff_type": "UNIFIED_DIFF",
            "content": (
                "--- a/.agents/agents/academic-orchestrator/agent.md\n"
                "+++ b/.agents/agents/academic-orchestrator/agent.md\n"
                "@@ tools @@\n"
                "- - invoke_subagent\n"
                "+ remove invoke_subagent from orchestrator\n"
            )
        },
        "rationale": "Orchestrator should operate without subagent delegation."
    }

    verdict = CapabilityPolicyGate.evaluate_candidate_patch(candidate)
    assert verdict.decision == "REJECT"
    assert VIOLATION_DELEGATION_AVAILABILITY_INVARIANT in verdict.violations
    assert "invoke_subagent" in verdict.affected_tools

    with pytest.raises(CapabilityPolicyViolationError) as exc_info:
        CapabilityPolicyGate.enforce_capability_policy(candidate)
    assert "Delegation Availability Invariant" in str(exc_info.value)


# =============================================================================
# 4. AgentCapabilityValidator Integration
# =============================================================================

def test_agent_capability_validator_enforces_both_invariants():
    """
    Validates that AgentCapabilityValidator checks both invariants and passes
    on the current canonical repository state.
    """
    validator = AgentCapabilityValidator(
        agents_dir=AGENTS_DIR,
        skills_dir=SKILLS_DIR,
        enforce_capability_policy=True
    )
    result = validator.run_validation()

    assert result["overall_verdict"] == "PASS"
    assert result["errors"] == 0

    # Ensure no issues regarding orchestrator invariants
    for issue in result["issues"]:
        assert issue["check"] not in ("orchestrator_non_execution_invariant", "delegation_availability_invariant")
