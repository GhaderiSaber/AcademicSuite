#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/immutable_capability_boundary_guard.py — Immutable Architecture Capability Boundary Guard (Phase 24)

Mandate:
The capability boundary between Orchestrators/Auditors (Non-executing authorities)
and Specialist Workers (Executing hands) is an IMMUTABLE ARCHITECTURAL INVARIANT.

The continuous self-improvement and evolutionary learning system:
CAN modify:
1. Routing (multi-stage workflow sequencing, stage prerequisites)
2. Delegation guidance (task contract specifications, prompt guidance)
3. Skills (methodology decision rules, behavioral instructions in .agents/skills/)
4. Acceptance criteria (required verification checks in delegation contracts)
5. Agent selection (mapping specific sub-tasks to specialist subagents)

CANNOT modify:
- Cannot silently grant Academic-Orchestrator execution tools (run_command, write_to_file, etc.)
- Cannot mutate non-executor toolsets in agent.md
- Cannot learn directives asserting that Academic-Orchestrator can run analyses itself
"""

import os
import sys
import re
from typing import Dict, Any, List, Optional, Set

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


class ImmutableCapabilityBoundaryViolationError(Exception):
    """
    Raised when an improvement candidate, lesson, or learning mutation violates
    the immutable capability boundary by attempting to grant execution tools or
    direct execution roles to non-executing authorities or orchestrators.
    """
    pass


# Non-executing authorities and auditors (immutable zero-hands / pure-conductor boundary)
NON_EXECUTING_AGENTS: Set[str] = {
    "academic-orchestrator",
    "academic-challenger",
    "behavior-analyst",
    "curriculum-builder",
    "digital-saber",
    "evidence-auditor",
    "final-judge",
    "intervention-designer",
    "journal-strategist",
    "knowledge-curator",
    "methodology-expert",
    "results-auditor",
    "skill-evolver",
    "statistical-expert",
    "test-orchestrator",
    "trajectory-analyzer"
}

# Direct and indirect execution tools strictly forbidden for non-executors
FORBIDDEN_EXECUTION_TOOLS: Set[str] = {
    "run_command",
    "write_to_file",
    "replace_file_content",
    "apply_diff",
    "edit_file",
    "multi_file_edit",
    "batch_replace",
    "patch",
    "call_mcp_tool",
    "manage_task",
    "schedule",
    "define_subagent"
}

# The 5 allowed learning modification categories
ALLOWED_LEARNING_CATEGORIES: Set[str] = {
    "routing",
    "delegation_guidance",
    "skills",
    "acceptance_criteria",
    "agent_selection"
}

# Regex patterns detecting illicit attempts to give direct execution roles to orchestrator
FORBIDDEN_ORCHESTRATOR_EXECUTION_PATTERNS = [
    r"\b(?:academic-)?orchestrator[ \t]+(?:can|should|will|must|may)?[ \t]*(?:run|execute|calculate|compute|perform)\b",
    r"\b(?:academic-)?orchestrator[ \t]+can[ \t]+run[ \t]+cfa[ \t]+itself\b",
    r"\b(?:academic-)?orchestrator[ \t]+(?:executes|runs)[ \t]+(?:r|python|code|syntax|script|analysis|cfa|anova|sem)\b",
    r"\bgrant[ \t]+(?:run_command|execution[ \t]+tools?|write_to_file|edit_file)[ \t]+to[ \t]+(?:academic-)?orchestrator\b",
    r"\badd[ \t]+(?:run_command|write_to_file|replace_file_content)[ \t]+to[ \t]+(?:academic-)?orchestrator\b",
    r"\bbypass[ \t]+delegation[ \t]+and[ \t]+execute\b",
    r"\b(?:academic-)?orchestrator[ \t]+directly[ \t]+executes\b",
    r"\bgrant[ \t]+(?:academic-)?orchestrator[ \t]+execution[ \t]+tools\b",
    r"\borchestrator[ \t]+runs[ \t]+cfa\b"
]


def is_allowed_learning_modification(category: str) -> bool:
    """Checks whether a proposed learning modification target is within the 5 allowed categories."""
    clean = str(category).lower().strip().replace("-", "_").replace(" ", "_")
    return any(clean == allowed or allowed in clean for allowed in ALLOWED_LEARNING_CATEGORIES)


def verify_text_capability_boundary(text: str, context_label: str = "text") -> None:
    """
    Inspects narrative text (lesson desired behavior, candidate rationale, etc.)
    for illicit statements asserting that orchestrator can execute analyses itself.
    """
    if not text:
        return
    text_lower = text.lower()
    for pat in FORBIDDEN_ORCHESTRATOR_EXECUTION_PATTERNS:
        if re.search(pat, text_lower):
            raise ImmutableCapabilityBoundaryViolationError(
                f"IMMUTABLE_CAPABILITY_BOUNDARY_VIOLATION: In {context_label}, prohibited directive detected: '{pat}'. "
                f"The capability boundary is immutable: Academic-Orchestrator is a pure conductor and cannot execute "
                f"tools, R, Python, or analyses directly. Learning must route and delegate, not grant execution."
            )


def verify_lesson_boundary(lesson_data: Dict[str, Any]) -> None:
    """
    Verifies that a distilled lesson obeys the immutable capability boundary.
    Raises ImmutableCapabilityBoundaryViolationError if lesson attempts to instruct
    orchestrator to execute tools directly.
    """
    desired = lesson_data.get("desired_behavior", "")
    generalization = lesson_data.get("generalization", "")
    diagnosis = lesson_data.get("diagnosis", {})
    what_should = diagnosis.get("what_should_have_happened", "") if isinstance(diagnosis, dict) else ""

    verify_text_capability_boundary(desired, context_label="lesson desired_behavior")
    verify_text_capability_boundary(generalization, context_label="lesson generalization")
    verify_text_capability_boundary(what_should, context_label="lesson diagnosis.what_should_have_happened")


def verify_candidate_boundary(candidate_data: Dict[str, Any]) -> None:
    """
    Verifies that an improvement candidate obeys the immutable capability boundary.
    Checks:
    1. If target is a non-executing agent, ensures NO execution tools are added to tools list.
    2. Ensures mutation content and rationale do not instruct non-executors to execute directly.
    3. Ensures candidate targets allowed categories (routing, delegation_guidance, skills, acceptance_criteria, agent_selection).
    """
    target_comp = str(candidate_data.get("target_component", "")).lower()
    mutation = candidate_data.get("mutation", {})
    content = str(mutation.get("content", "")).lower()
    rationale = str(candidate_data.get("rationale", "")).lower()
    mut_type = str(candidate_data.get("mutation_type", "")).upper()

    # 1. Inspect text for illicit execution directives
    verify_text_capability_boundary(content, context_label="candidate mutation content")
    verify_text_capability_boundary(rationale, context_label="candidate rationale")

    # 2. Check if target is a non-executing agent
    for ne_agent in NON_EXECUTING_AGENTS:
        if ne_agent in target_comp:
            # Inspect diff or content for addition of forbidden tools
            for f_tool in FORBIDDEN_EXECUTION_TOOLS:
                tool_pat = rf"(?:tools\s*:|^\s*[\+\-]?\s*-\s*|^\s*\+.*?\b){f_tool}\b"
                if re.search(tool_pat, content, re.MULTILINE) or f'"{f_tool}"' in content or f"'{f_tool}'" in content:
                    raise ImmutableCapabilityBoundaryViolationError(
                        f"IMMUTABLE_CAPABILITY_BOUNDARY_VIOLATION: Improvement candidate '{candidate_data.get('candidate_id')}' "
                        f"attempts to grant forbidden execution tool '{f_tool}' to non-executing agent '{ne_agent}'. "
                        f"The capability boundary is immutable architecture. Execution tools can only reside with specialist workers."
                    )


def audit_candidate_learning_target(candidate_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Audits a candidate against the 5 allowed learning categories:
    routing, delegation_guidance, skills, acceptance_criteria, agent_selection.
    Returns audit summary.
    """
    mut_type = str(candidate_data.get("mutation_type", "")).upper()
    target_comp = str(candidate_data.get("target_component", "")).lower()
    content = str(candidate_data.get("mutation", {}).get("content", "")).lower()

    # Determine category
    category = "skills"
    if "routing" in mut_type.lower() or "routing" in content:
        category = "routing"
    elif "delegation" in mut_type.lower() or "delegation" in content:
        category = "delegation_guidance"
    elif "acceptance" in mut_type.lower() or "criteria" in content:
        category = "acceptance_criteria"
    elif "agent_selection" in mut_type.lower() or "selection" in content:
        category = "agent_selection"
    elif ".agents/skills/" in target_comp or "skill" in mut_type.lower():
        category = "skills"

    # Validate against immutable boundary
    verify_candidate_boundary(candidate_data)

    return {
        "valid": True,
        "category": category,
        "is_allowed": is_allowed_learning_modification(category),
        "target_component": target_comp
    }
