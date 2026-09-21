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

# Canonical Antigravity Tools & Classifications (SSOT: contracts/canonical_tools.py)
try:
    from contracts.canonical_tools import (
        CANONICAL_ANTIGRAVITY_TOOLS,
        CANONICAL_FILE_MUTATION_TOOLS,
        CANONICAL_DIRECT_EXECUTION_TOOLS as DIRECT_EXECUTION_TOOLS,
        CANONICAL_INDIRECT_EXECUTION_TOOLS as INDIRECT_EXECUTION_TOOLS,
    )
except ImportError:
    DIRECT_EXECUTION_TOOLS: Set[str] = {"run_command"}
    INDIRECT_EXECUTION_TOOLS: Set[str] = {"call_mcp_tool", "define_subagent", "manage_task", "schedule"}
    CANONICAL_FILE_MUTATION_TOOLS: Set[str] = {"write_to_file", "replace_file_content", "multi_replace_file_content"}
    CANONICAL_ANTIGRAVITY_TOOLS: Set[str] = {
        "view_file", "write_to_file", "replace_file_content", "multi_replace_file_content",
        "list_dir", "grep_search", "find_by_name", "run_command", "manage_task",
        "schedule", "invoke_subagent", "manage_subagents", "send_message",
        "define_subagent", "ask_question", "read_url_content", "search_web",
        "generate_image", "call_mcp_tool", "list_resources", "read_resource"
    }

# MCP servers capable of executing code, arbitrary SQL, remote functions, or pipeline actions
EXECUTION_CAPABLE_MCP_SERVERS: Set[str] = {
    "posthog",
    "supabase",
    "github",
}

# High-risk execution tools inside MCP servers
EXECUTION_CAPABLE_MCP_TOOLS: Set[str] = {
    "exec",
    "execute_sql",
    "deploy_edge_function",
    "apply_migration",
    "actions_run_trigger",
}

# Skills that encapsulate deterministic batch CLI runners ("The Hands")
EXECUTION_RUNNER_SKILLS: Set[str] = {
    "academic-suite-orchestrator",
}



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


def classify_execution_capabilities(
    agent_name: str,
    frontmatter: Dict[str, Any],
    policy: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Analyzes and classifies an agent's direct and indirect execution capabilities.

    Distinguishes:
    - DIRECT EXECUTION: Tools that execute shell or binary code directly on the host ('run_command').
    - INDIRECT EXECUTION: Tools, skills, or vectors that can trigger proxy execution, background process
      manipulation, or dynamic privilege elevation ('call_mcp_tool', 'define_subagent', 'manage_task',
      'schedule', execution runner skills).

    Returns:
        Structured classification dictionary containing found tools, permissions, and violations.
    """
    pol = policy or load_capability_policy()
    agents = pol.get("agents", {})
    spec = agents.get(agent_name, {})
    can_execute = bool(spec.get("can_execute_code", True))

    tools = set(frontmatter.get("tools", []))
    skills = set(frontmatter.get("skills", []))

    direct_found = tools & DIRECT_EXECUTION_TOOLS
    indirect_tools_found = tools & INDIRECT_EXECUTION_TOOLS
    indirect_skills_found = skills & EXECUTION_RUNNER_SKILLS

    violations: List[str] = []

    if not can_execute:
        # Non-executing agents must have ZERO direct execution tools
        if direct_found:
            violations.append(
                f"DIRECT EXECUTION VIOLATION: Agent '{agent_name}' has can_execute_code=False "
                f"but declares direct execution tools: {sorted(direct_found)}"
            )
        # Non-executing agents must have ZERO indirect execution tools
        if indirect_tools_found:
            violations.append(
                f"INDIRECT EXECUTION VIOLATION: Agent '{agent_name}' has can_execute_code=False "
                f"but declares indirect execution tools: {sorted(indirect_tools_found)}"
            )
        # Non-executing agents must NOT declare batch CLI runner skills
        if indirect_skills_found:
            violations.append(
                f"INDIRECT SKILL VIOLATION: Agent '{agent_name}' has can_execute_code=False "
                f"but declares batch execution runner skills: {sorted(indirect_skills_found)}"
            )
    else:
        # Executing agents should declare run_command unless justified
        if not direct_found and not spec.get("execution_justification"):
            violations.append(
                f"DIRECT EXECUTION DEFICIENCY: Agent '{agent_name}' has can_execute_code=True "
                f"but does not declare any direct execution tools ({sorted(DIRECT_EXECUTION_TOOLS)})"
            )

    indirect_all = sorted(list(indirect_tools_found) + [f"skill:{s}" for s in indirect_skills_found])

    return {
        "agent": agent_name,
        "can_execute_code": can_execute,
        "execution_scope": spec.get("execution_scope", "general" if can_execute else "none"),
        "direct_execution": sorted(direct_found),
        "indirect_execution": indirect_all,
        "indirect_tools": sorted(indirect_tools_found),
        "indirect_skills": sorted(indirect_skills_found),
        "has_direct_execution": bool(direct_found),
        "has_indirect_execution": bool(indirect_all),
        "has_any_execution": bool(direct_found or indirect_all),
        "is_compliant": len(violations) == 0,
        "violations": violations,
    }


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
    6. Direct vs. Indirect execution classification compliance.

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

    # 6. Direct vs. Indirect Execution Classification
    exec_class = classify_execution_capabilities(agent_name, frontmatter, pol)
    for violation in exec_class["violations"]:
        issues.append(violation)

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

    # Canonical Antigravity tools for validation (SSOT)
    valid_tools = CANONICAL_ANTIGRAVITY_TOOLS

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
            # Indirect execution tools must also be forbidden for non-executing agents
            for indirect_tool in ["define_subagent", "call_mcp_tool", "manage_task", "schedule"]:
                if indirect_tool not in forb:
                    issues.append(f"Agent '{name}' has can_execute_code=False but indirect execution tool '{indirect_tool}' is not in forbidden")

        if not spec.get("can_delegate", True):
            if "invoke_subagent" not in forb:
                issues.append(f"Agent '{name}' has can_delegate=False but 'invoke_subagent' is not in forbidden")

        if not spec.get("can_write_files", True):
            for mutation_tool in sorted(CANONICAL_FILE_MUTATION_TOOLS):
                if mutation_tool not in forb:
                    issues.append(f"Agent '{name}' has can_write_files=False but '{mutation_tool}' is not in forbidden")

        if spec.get("mainAgent") is True:
            main_agent_count += 1

    if main_agent_count != 1:
        issues.append(f"Expected exactly 1 agent with mainAgent: true, found {main_agent_count}")

    return issues


