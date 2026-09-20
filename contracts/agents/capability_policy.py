#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
contracts/agents/capability_policy.py — Machine-Checkable Capability Policy Interface

Provides programmatic loading, querying, and verification against the canonical
Single Source of Truth (contracts/agents/agent_capabilities.yaml).
"""

import os
import sys
import yaml
from typing import Dict, Any, List, Optional, Set

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_POLICY_PATH = os.path.join(os.path.dirname(__file__), "agent_capabilities.yaml")


class CapabilityPolicyError(Exception):
    """Raised when the capability policy is missing, malformed, or violated."""
    pass


def load_capability_policy(policy_path: Optional[str] = None) -> Dict[str, Any]:
    """Loads and validates the structure of the agent capabilities YAML policy."""
    path = policy_path or DEFAULT_POLICY_PATH
    if not os.path.isfile(path):
        raise FileNotFoundError(f"Capability policy file not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict) or "agents" not in data:
        raise CapabilityPolicyError(f"Malformed capability policy: 'agents' mapping missing in {path}")

    return data


def get_all_policy_agents(policy: Optional[Dict[str, Any]] = None) -> List[str]:
    """Returns sorted list of all agent names declared in the policy."""
    pol = policy or load_capability_policy()
    return sorted(pol.get("agents", {}).keys())


def get_agent_policy(agent_name: str, policy: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Retrieves the capability policy entry for a specific agent."""
    pol = policy or load_capability_policy()
    agents = pol.get("agents", {})
    if agent_name not in agents:
        raise KeyError(f"Agent '{agent_name}' not defined in capability policy.")
    return agents[agent_name]


def validate_agent_against_policy(
    agent_name: str,
    frontmatter: Dict[str, Any],
    policy: Optional[Dict[str, Any]] = None
) -> List[str]:
    """
    Validates an agent's frontmatter configuration against its canonical capability policy.

    Checks:
    1. Agent exists in policy.
    2. All 'required' tools are present in frontmatter 'tools'.
    3. Zero 'forbidden' tools are present in frontmatter 'tools'.
    4. 'mainAgent' boolean matches policy.
    5. 'subagent' boolean matches policy.

    Returns:
        List of issue strings (empty if 100% compliant).
    """
    issues: List[str] = []
    pol = policy or load_capability_policy()
    agents = pol.get("agents", {})

    if agent_name not in agents:
        issues.append(f"Agent '{agent_name}' is not registered in contracts/agents/agent_capabilities.yaml")
        return issues

    spec = agents[agent_name]
    tools = set(frontmatter.get("tools", []))
    required_tools = set(spec.get("required", []))
    forbidden_tools = set(spec.get("forbidden", []))

    # 1. Missing required tools
    missing = required_tools - tools
    if missing:
        issues.append(
            f"Agent '{agent_name}' missing required tools from capability policy: {sorted(missing)}"
        )

    # 2. Present forbidden tools
    illegal = forbidden_tools & tools
    if illegal:
        issues.append(
            f"Agent '{agent_name}' declares forbidden tools in violation of capability policy: {sorted(illegal)}"
        )

    # 3. mainAgent match
    expected_main = bool(spec.get("mainAgent", False))
    actual_main = bool(frontmatter.get("mainAgent", False))
    if actual_main != expected_main:
        issues.append(
            f"Agent '{agent_name}' mainAgent={actual_main} does not match capability policy (expected {expected_main})"
        )

    # 4. subagent match
    expected_sub = bool(spec.get("subagent", True))
    actual_sub = bool(frontmatter.get("subagent", True))
    if actual_sub != expected_sub:
        issues.append(
            f"Agent '{agent_name}' subagent={actual_sub} does not match capability policy (expected {expected_sub})"
        )

    # 5. Delegation match
    can_delegate = spec.get("can_delegate", True)
    declared_delegations = frontmatter.get("agents", [])
    if not can_delegate and declared_delegations:
        issues.append(
            f"Agent '{agent_name}' has can_delegate=False in capability policy but declares delegated subagents: {declared_delegations}"
        )

    return issues


def validate_policy_schema(policy: Optional[Dict[str, Any]] = None) -> List[str]:
    """
    Validates the internal consistency and schema of agent_capabilities.yaml itself.
    """
    issues: List[str] = []
    pol = policy or load_capability_policy()

    if not isinstance(pol, dict):
        return ["Capability policy root is not a dictionary"]

    agents = pol.get("agents")
    if not isinstance(agents, dict) or not agents:
        return ["Capability policy missing non-empty 'agents' mapping"]

    # Canonical Antigravity tools for validation
    valid_tools = {
        "view_file", "write_to_file", "replace_file_content", "list_dir",
        "grep_search", "find_by_name", "run_command", "manage_task",
        "schedule", "invoke_subagent", "manage_subagents", "send_message",
        "define_subagent", "ask_question", "read_url_content", "search_web",
        "generate_image", "call_mcp_tool", "list_resources", "read_resource"
    }

    main_agent_count = 0

    for name, spec in agents.items():
        if not isinstance(spec, dict):
            issues.append(f"Agent '{name}' policy specification must be a dictionary")
            continue

        required_fields = ["role", "tier", "mainAgent", "subagent", "can_delegate", "can_execute_code", "can_write_files", "required", "forbidden"]
        for rf in required_fields:
            if rf not in spec:
                issues.append(f"Agent '{name}' policy specification missing required field: '{rf}'")

        req = set(spec.get("required", []))
        forb = set(spec.get("forbidden", []))

        # Check tool canonicality
        for t in req:
            if t not in valid_tools:
                issues.append(f"Agent '{name}' has invalid required tool: '{t}'")
        for t in forb:
            if t not in valid_tools:
                issues.append(f"Agent '{name}' has invalid forbidden tool: '{t}'")

        # Mutually exclusive
        overlap = req & forb
        if overlap:
            issues.append(f"Agent '{name}' has tools in both required and forbidden: {sorted(overlap)}")

        # Semantic constraints
        if not spec.get("can_execute_code", True):
            if "run_command" not in forb:
                issues.append(f"Agent '{name}' has can_execute_code=False but 'run_command' is not in forbidden")

        if not spec.get("can_delegate", True):
            if "invoke_subagent" not in forb:
                issues.append(f"Agent '{name}' has can_delegate=False but 'invoke_subagent' is not in forbidden")

        if not spec.get("can_write_files", True):
            if "write_to_file" not in forb:
                issues.append(f"Agent '{name}' has can_write_files=False but 'write_to_file' is not in forbidden")

        if spec.get("mainAgent") is True:
            main_agent_count += 1

    if main_agent_count != 1:
        issues.append(f"Expected exactly 1 agent with mainAgent: true, found {main_agent_count}")

    return issues

