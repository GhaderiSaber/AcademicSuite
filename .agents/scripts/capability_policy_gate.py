#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/capability_policy_gate.py — Capability Boundary Policy Gate (Phase 25)

Mandate:
The capability boundary between Orchestrators/Auditors (pure conductors/critics)
and Specialist Workers (executing hands) is an IMMUTABLE ARCHITECTURAL INVARIANT.

The promotion and self-improvement system evaluates:

LEARNED BEHAVIOR
        │
        ▼
   Candidate patch
        │
        ▼
Capability policy
        │
   ┌────┴────┐
   │         │
 ALLOW     REJECT

The learning system must NEVER be able to evolve the orchestrator back into a hand.

Specifically, the policy categorically rejects candidates attempting to:
1. add run_command to academic-orchestrator
2. add write_to_file (or file modification tools) to academic-orchestrator
3. add arbitrary MCP execution (call_mcp_tool, enable_mcp_tools, MCP servers/tools) to academic-orchestrator
"""

import os
import sys
import re
import json
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Set, NamedTuple

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.immutable_capability_boundary_guard import (
    NON_EXECUTING_AGENTS,
    FORBIDDEN_EXECUTION_TOOLS,
    ALLOWED_LEARNING_CATEGORIES,
    FORBIDDEN_ORCHESTRATOR_EXECUTION_PATTERNS,
    ImmutableCapabilityBoundaryViolationError
)
from scripts.orchestrator_invariants import (
    FORBIDDEN_ORCHESTRATOR_TOOLS,
    REQUIRED_ORCHESTRATOR_TOOLS,
    OrchestratorInvariantViolationError,
    OrchestratorNonExecutionInvariantViolationError,
    DelegationAvailabilityInvariantViolationError,
)


class CapabilityPolicyViolationError(ImmutableCapabilityBoundaryViolationError, OrchestratorInvariantViolationError):
    """
    Raised when an improvement candidate patch violates the capability policy
    by attempting to evolve the academic-orchestrator (or any non-executing agent)
    back into a hand, or by violating the Orchestrator Non-Execution / Delegation
    Availability Invariants.
    """
    pass


# Specific Policy Violation Codes
VIOLATION_RUN_COMMAND = "CANNOT_ADD_RUN_COMMAND_TO_ORCHESTRATOR"
VIOLATION_WRITE_TOOLS = "CANNOT_ADD_WRITE_TO_FILE_TO_ORCHESTRATOR"
VIOLATION_MCP_EXECUTION = "CANNOT_ADD_MCP_EXECUTION_TO_ORCHESTRATOR"
VIOLATION_DIRECT_EXECUTION_DIRECTIVE = "CANNOT_INSTRUCT_ORCHESTRATOR_TO_EXECUTE"
VIOLATION_NON_EXECUTOR_TOOL_MUTATION = "CANNOT_ADD_EXECUTION_TOOLS_TO_NON_EXECUTING_AGENT"
VIOLATION_ORCHESTRATOR_NON_EXECUTION_INVARIANT = "ORCHESTRATOR_NON_EXECUTION_INVARIANT_VIOLATION"
VIOLATION_DELEGATION_AVAILABILITY_INVARIANT = "DELEGATION_AVAILABILITY_INVARIANT_VIOLATION"

# Direct file mutation tools forbidden for orchestrator (SSOT: contracts/canonical_tools.py)
try:
    from contracts.canonical_tools import ALL_MUTATION_TOOLS as FILE_MUTATION_TOOLS
except ImportError:
    FILE_MUTATION_TOOLS: Set[str] = {
        "write_to_file",
        "replace_file_content",
        "multi_replace_file_content",
        "edit_file",
        "apply_diff",
        "multi_file_edit",
        "batch_replace",
        "patch"
    }

# Arbitrary MCP execution tokens forbidden for orchestrator
MCP_EXECUTION_PATTERNS = [
    r"\bcall_mcp_tool\b",
    r"\benable_mcp_tools\s*:\s*true\b",
    r"\bmcp_servers\b",
    r"\bmcp_tools\b",
    r"\bmcp_[a-zA-Z0-9_]+\b",
    r"\bposthog:exec\b",
    r"\bmcp_posthog_exec\b",
    r"\bcodebase-memory-mcp\b",
    r"\bexecute\s+via\s+mcp\b",
    r"\bcall\s+mcp\b"
]


class CapabilityPolicyVerdict(NamedTuple):
    """Formal verdict emitted by the Capability Policy Gate."""
    decision: str  # "ALLOW" or "REJECT"
    violations: List[str]
    affected_tools: List[str]
    target_agent: str
    message: str
    timestamp: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision,
            "violations": self.violations,
            "affected_tools": self.affected_tools,
            "target_agent": self.target_agent,
            "message": self.message,
            "timestamp": self.timestamp
        }


class CapabilityPolicyGate:
    """
    Authoritative gate enforcing capability boundary policy against candidate patches
    prior to sandbox deployment, evaluation, promotion, or physical file deployment.
    """

    @classmethod
    def evaluate_candidate_patch(cls, candidate_data: Dict[str, Any]) -> CapabilityPolicyVerdict:
        """
        Evaluates a proposed improvement candidate patch against the immutable capability policy.

        Returns:
            CapabilityPolicyVerdict with decision="ALLOW" or decision="REJECT".
        """
        candidate_id = str(candidate_data.get("candidate_id") or candidate_data.get("id") or "CAND-UNKNOWN")
        target_comp = str(
            candidate_data.get("target_component")
            or candidate_data.get("target")
            or candidate_data.get("target_file")
            or ""
        ).lower()
        mutation = candidate_data.get("mutation")
        if isinstance(mutation, dict):
            content = str(mutation.get("content") or "")
        else:
            content = str(mutation or "")
        if not content:
            content = str(
                candidate_data.get("diff")
                or candidate_data.get("patch")
                or candidate_data.get("content")
                or ""
            )
        rationale = str(candidate_data.get("rationale", ""))
        now_iso = datetime.now(timezone.utc).isoformat()

        violations: List[str] = []
        affected_tools: List[str] = []
        target_agent = "academic-orchestrator" if "academic-orchestrator" in target_comp else ""

        if not target_agent:
            for ne in NON_EXECUTING_AGENTS:
                if ne in target_comp:
                    target_agent = ne
                    break

        content_lower = content.lower()
        rationale_lower = rationale.lower()

        # ---------------------------------------------------------------------
        # CHECK 1: Adding run_command to academic-orchestrator or non-executors
        # ---------------------------------------------------------------------
        run_command_patterns = [
            r"(?:tools\s*:|^\s*[\+\-]?\s*-\s*|^\s*\+.*?\b)run_command\b",
            r"['\"]run_command['\"]",
            r"\btools\s*:\s*\[?[^\]]*\brun_command\b",
            r"\bgrant\s+run_command\b",
            r"\badd\s+run_command\b"
        ]

        if target_agent:
            for pat in run_command_patterns:
                if re.search(pat, content, re.MULTILINE | re.IGNORECASE):
                    violations.append(
                        VIOLATION_RUN_COMMAND if target_agent == "academic-orchestrator" else VIOLATION_NON_EXECUTOR_TOOL_MUTATION
                    )
                    if target_agent == "academic-orchestrator":
                        violations.append(VIOLATION_ORCHESTRATOR_NON_EXECUTION_INVARIANT)
                    affected_tools.append("run_command")
                    break

        # ---------------------------------------------------------------------
        # CHECK 2: Adding write_to_file or file modification tools to orchestrator
        # (Orchestrator Non-Execution Invariant: write_to_file, replace_file_content, edit_file)
        # ---------------------------------------------------------------------
        if target_agent:
            for w_tool in FILE_MUTATION_TOOLS:
                w_patterns = [
                    rf"(?:tools\s*:|^\s*[\+\-]?\s*-\s*|^\s*\+.*?\b){w_tool}\b",
                    rf"['\"]{w_tool}['\"]",
                    rf"\btools\s*:\s*\[?[^\]]*\b{w_tool}\b",
                    rf"\bgrant\s+{w_tool}\b",
                    rf"\badd\s+{w_tool}\b"
                ]
                for pat in w_patterns:
                    if re.search(pat, content, re.MULTILINE | re.IGNORECASE):
                        violations.append(
                            VIOLATION_WRITE_TOOLS if target_agent == "academic-orchestrator" else VIOLATION_NON_EXECUTOR_TOOL_MUTATION
                        )
                        if target_agent == "academic-orchestrator" and w_tool in FORBIDDEN_ORCHESTRATOR_TOOLS:
                            violations.append(VIOLATION_ORCHESTRATOR_NON_EXECUTION_INVARIANT)
                        affected_tools.append(w_tool)
                        break

            # Also check generic write tool grants
            if re.search(r"\benable_write_tools\s*:\s*true\b", content_lower):
                violations.append(VIOLATION_WRITE_TOOLS)
                if target_agent == "academic-orchestrator":
                    violations.append(VIOLATION_ORCHESTRATOR_NON_EXECUTION_INVARIANT)
                affected_tools.append("enable_write_tools")

        # ---------------------------------------------------------------------
        # CHECK 3: Adding arbitrary MCP execution to orchestrator
        # ---------------------------------------------------------------------
        if target_agent:
            for mcp_pat in MCP_EXECUTION_PATTERNS:
                if re.search(mcp_pat, content, re.MULTILINE | re.IGNORECASE):
                    violations.append(VIOLATION_MCP_EXECUTION)
                    affected_tools.append("arbitrary_mcp_execution")
                    break

        # ---------------------------------------------------------------------
        # CHECK 4: Direct execution directives in prompt / rationale
        # ---------------------------------------------------------------------
        for pat in FORBIDDEN_ORCHESTRATOR_EXECUTION_PATTERNS:
            if re.search(pat, content_lower) or re.search(pat, rationale_lower):
                violations.append(VIOLATION_DIRECT_EXECUTION_DIRECTIVE)
                affected_tools.append("direct_execution_directive")
                break

        # ---------------------------------------------------------------------
        # CHECK 5: Delegation Availability Invariant (Phase 26)
        # academic-orchestrator MUST possess invoke_subagent
        # ---------------------------------------------------------------------
        if target_agent == "academic-orchestrator":
            remove_patterns = [
                r"^\s*-\s*-\s*invoke_subagent\b",
                r"\bremove\s+invoke_subagent\b",
                r"\bdelete\s+invoke_subagent\b",
                r"\bstrip\s+invoke_subagent\b",
                r"\bwithout\s+invoke_subagent\b",
                r"\bdisable_subagents\b",
            ]
            for r_pat in remove_patterns:
                if re.search(r_pat, content, re.MULTILINE | re.IGNORECASE) or re.search(r_pat, rationale_lower):
                    violations.append(VIOLATION_DELEGATION_AVAILABILITY_INVARIANT)
                    affected_tools.append("invoke_subagent")
                    break

        # Dedup violations and affected tools
        violations = list(dict.fromkeys(violations))
        affected_tools = list(dict.fromkeys(affected_tools))

        if violations:
            msg = (
                f"CAPABILITY_POLICY_VIOLATION: IMMUTABLE_CAPABILITY_BOUNDARY_VIOLATION: Candidate '{candidate_id}' violates capability boundary policy for "
                f"agent '{target_agent or 'academic-orchestrator'}'. Violations: {', '.join(violations)}. "
                f"Affected tools/directives: {', '.join(affected_tools)}. "
                f"The capability boundary is immutable under permanent architectural laws (Directive 20): "
                f"Orchestrator Non-Execution Invariant (cannot possess {', '.join(sorted(FORBIDDEN_ORCHESTRATOR_TOOLS))}) and "
                f"Delegation Availability Invariant (MUST possess {', '.join(sorted(REQUIRED_ORCHESTRATOR_TOOLS))})."
            )
            return CapabilityPolicyVerdict(
                decision="REJECT",
                violations=violations,
                affected_tools=affected_tools,
                target_agent=target_agent or "academic-orchestrator",
                message=msg,
                timestamp=now_iso
            )

        return CapabilityPolicyVerdict(
            decision="ALLOW",
            violations=[],
            affected_tools=[],
            target_agent=target_agent,
            message="Candidate patch satisfies all capability boundary policy rules.",
            timestamp=now_iso
        )

    @classmethod
    def enforce_capability_policy(cls, candidate_data: Dict[str, Any]) -> None:
        """
        Enforces the capability policy, raising CapabilityPolicyViolationError if rejected.
        """
        verdict = cls.evaluate_candidate_patch(candidate_data)
        if verdict.decision == "REJECT":
            raise CapabilityPolicyViolationError(verdict.message)

    @classmethod
    def is_patch_allowed(cls, candidate_data: Dict[str, Any]) -> bool:
        """Convenience method returning True if patch is allowed, False otherwise."""
        verdict = cls.evaluate_candidate_patch(candidate_data)
        return verdict.decision == "ALLOW"


def evaluate_candidate_patch(candidate_data: Dict[str, Any]) -> CapabilityPolicyVerdict:
    """Convenience functional interface."""
    return CapabilityPolicyGate.evaluate_candidate_patch(candidate_data)


def enforce_capability_policy(candidate_data: Dict[str, Any]) -> None:
    """Convenience functional interface enforcing policy."""
    CapabilityPolicyGate.enforce_capability_policy(candidate_data)


def main():
    parser = argparse.ArgumentParser(description="Capability Policy Gate CLI (Phase 25)")
    parser.add_argument("--candidate", type=str, required=True, help="Path to candidate JSON file or candidate ID")
    args = parser.parse_args()

    cand_path = args.candidate
    if not os.path.isfile(cand_path):
        cand_path = os.path.join(ROOT_DIR, "learning", "candidates", f"{args.candidate}.json")

    if not os.path.isfile(cand_path):
        print(json.dumps({"error": f"Candidate file not found: {cand_path}"}, indent=2))
        sys.exit(1)

    with open(cand_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    verdict = CapabilityPolicyGate.evaluate_candidate_patch(data)
    print(json.dumps(verdict.to_dict(), indent=2))
    sys.exit(0 if verdict.decision == "ALLOW" else 2)


if __name__ == "__main__":
    main()
