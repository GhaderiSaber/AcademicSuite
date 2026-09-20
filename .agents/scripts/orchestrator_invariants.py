#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/orchestrator_invariants.py — Permanent Architectural Invariants (Phase 26)

Mandate:
Codifies two permanent architectural laws for academic-orchestrator:

1. Orchestrator Non-Execution Invariant:
   academic-orchestrator MUST NOT possess:
       - run_command
       - write_to_file
       - replace_file_content
       - edit_file

2. Delegation Availability Invariant:
   academic-orchestrator MUST possess:
       - invoke_subagent

These invariants are immutable architectural laws governing the cognitive twin
and academic conductor architecture.
"""

import os
import sys
import yaml
import argparse
from typing import Dict, Any, List, Set, Iterable, Optional, Tuple

_CURR_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(os.path.dirname(_CURR_DIR)) == ".agents":
    ROOT_DIR = os.path.abspath(os.path.join(_CURR_DIR, "..", ".."))
else:
    ROOT_DIR = os.path.abspath(os.path.join(_CURR_DIR, ".."))

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
agents_dir = os.path.join(ROOT_DIR, ".agents")
if agents_dir not in sys.path:
    sys.path.insert(0, agents_dir)

# =============================================================================
# 1. Architectural Invariant Constants
# =============================================================================

ORCHESTRATOR_TARGET_AGENT = "academic-orchestrator"

# Law 1: Orchestrator Non-Execution Invariant
# academic-orchestrator MUST NOT possess these tools:
FORBIDDEN_ORCHESTRATOR_TOOLS: frozenset = frozenset({
    "run_command",
    "write_to_file",
    "replace_file_content",
    "edit_file",
})

# Law 2: Delegation Availability Invariant
# academic-orchestrator MUST possess this tool:
REQUIRED_ORCHESTRATOR_TOOLS: frozenset = frozenset({
    "invoke_subagent",
})


# =============================================================================
# 2. Exception Hierarchy
# =============================================================================

class OrchestratorInvariantViolationError(Exception):
    """Base exception for violations of permanent orchestrator architectural laws."""
    pass


class OrchestratorNonExecutionInvariantViolationError(OrchestratorInvariantViolationError):
    """
    Raised when academic-orchestrator possesses or is granted forbidden execution
    or file mutation tools (run_command, write_to_file, replace_file_content, edit_file).
    """
    pass


class DelegationAvailabilityInvariantViolationError(OrchestratorInvariantViolationError):
    """
    Raised when academic-orchestrator does not possess or is stripped of
    its required delegation tool (invoke_subagent).
    """
    pass


# =============================================================================
# 3. Invariant Verifiers
# =============================================================================

def verify_orchestrator_non_execution_invariant(
    tools: Iterable[str],
    agent_name: str = ORCHESTRATOR_TARGET_AGENT
) -> None:
    """
    Verifies the Orchestrator Non-Execution Invariant.
    Raises OrchestratorNonExecutionInvariantViolationError if any forbidden tool is present.
    """
    if agent_name != ORCHESTRATOR_TARGET_AGENT:
        return

    tool_set = set(tools or [])
    forbidden_present = sorted(tool_set.intersection(FORBIDDEN_ORCHESTRATOR_TOOLS))
    if forbidden_present:
        raise OrchestratorNonExecutionInvariantViolationError(
            f"ORCHESTRATOR_NON_EXECUTION_INVARIANT_VIOLATION: '{agent_name}' MUST NOT possess: "
            f"{', '.join(sorted(FORBIDDEN_ORCHESTRATOR_TOOLS))}. "
            f"Detected forbidden tools: {', '.join(forbidden_present)}. "
            f"The orchestrator is a pure cognitive conductor and coordinator, strictly forbidden from "
            f"executing shell/computational commands or mutating project files on disk."
        )


def verify_delegation_availability_invariant(
    tools: Iterable[str],
    agent_name: str = ORCHESTRATOR_TARGET_AGENT
) -> None:
    """
    Verifies the Delegation Availability Invariant.
    Raises DelegationAvailabilityInvariantViolationError if invoke_subagent is missing.
    """
    if agent_name != ORCHESTRATOR_TARGET_AGENT:
        return

    tool_set = set(tools or [])
    missing_required = sorted(REQUIRED_ORCHESTRATOR_TOOLS.difference(tool_set))
    if missing_required:
        raise DelegationAvailabilityInvariantViolationError(
            f"DELEGATION_AVAILABILITY_INVARIANT_VIOLATION: '{agent_name}' MUST possess: "
            f"{', '.join(sorted(REQUIRED_ORCHESTRATOR_TOOLS))}. "
            f"Missing required delegation tools: {', '.join(missing_required)}. "
            f"The orchestrator coordinates work through specialist subagents and must always retain "
            f"native multi-agent delegation capabilities."
        )


def verify_orchestrator_invariants(
    tools: Iterable[str],
    agent_name: str = ORCHESTRATOR_TARGET_AGENT
) -> Dict[str, Any]:
    """
    Verifies both invariants for academic-orchestrator.
    Returns a structured verdict dictionary if valid, raises an invariant error otherwise.
    """
    verify_orchestrator_non_execution_invariant(tools, agent_name=agent_name)
    verify_delegation_availability_invariant(tools, agent_name=agent_name)

    return {
        "agent": agent_name,
        "verdict": "PASS",
        "orchestrator_non_execution_invariant": {
            "status": "PASS",
            "forbidden_tools_checked": sorted(FORBIDDEN_ORCHESTRATOR_TOOLS),
            "forbidden_tools_detected": []
        },
        "delegation_availability_invariant": {
            "status": "PASS",
            "required_tools_checked": sorted(REQUIRED_ORCHESTRATOR_TOOLS),
            "required_tools_present": sorted(REQUIRED_ORCHESTRATOR_TOOLS.intersection(set(tools or [])))
        }
    }


def audit_orchestrator_frontmatter(
    frontmatter: Dict[str, Any],
    agent_name: str = ORCHESTRATOR_TARGET_AGENT
) -> Dict[str, Any]:
    """Audits agent frontmatter dictionary against both permanent architectural invariants."""
    tools = frontmatter.get("tools", [])
    return verify_orchestrator_invariants(tools, agent_name=agent_name)


def audit_orchestrator_agent_file(file_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Reads the canonical academic-orchestrator agent markdown file and verifies
    both permanent architectural invariants.
    """
    if file_path is None:
        file_path = os.path.join(ROOT_DIR, ".agents", "agents", "academic-orchestrator", "agent.md")

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Agent specification not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Parse YAML frontmatter
    fm: Dict[str, Any] = {}
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            fm = yaml.safe_load(parts[1]) or {}

    return audit_orchestrator_frontmatter(fm, agent_name=fm.get("name", ORCHESTRATOR_TARGET_AGENT))


# =============================================================================
# 4. CLI Runner
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Verify Permanent Architectural Invariants for academic-orchestrator (Phase 26)"
    )
    parser.add_argument(
        "--agent-file",
        default=os.path.join(ROOT_DIR, ".agents", "agents", "academic-orchestrator", "agent.md"),
        help="Path to academic-orchestrator agent.md"
    )
    args = parser.parse_args()

    print("=" * 70)
    print("⚖️ AcademicSuite Permanent Architectural Invariants Auditor (Phase 26)")
    print("=" * 70)
    print(f"Target Agent File: {args.agent_file}")

    try:
        verdict = audit_orchestrator_agent_file(args.agent_file)
        print("\nINVARIANT RESULTS:")
        print("  ✓ Orchestrator Non-Execution Invariant: PASS (0 forbidden tools)")
        print(f"    Forbidden set: {sorted(FORBIDDEN_ORCHESTRATOR_TOOLS)}")
        print("  ✓ Delegation Availability Invariant:    PASS (invoke_subagent is present)")
        print(f"    Required set:  {sorted(REQUIRED_ORCHESTRATOR_TOOLS)}")
        print("\n" + "=" * 70)
        print("✅ ALL PERMANENT ARCHITECTURAL INVARIANTS SATISFIED.")
        print("=" * 70)
        sys.exit(0)
    except OrchestratorInvariantViolationError as e:
        print(f"\n❌ ARCHITECTURAL INVARIANT VIOLATION: {e}")
        print("=" * 70)
        sys.exit(1)


if __name__ == "__main__":
    main()
