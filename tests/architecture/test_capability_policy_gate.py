#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/architecture/test_capability_policy_gate.py — Phase 25 Test Suite

Validates that:
1. Capability Policy Gate intercepts all candidate patches prior to promotion.
2. Promotion system strictly rejects candidates attempting to:
   - add run_command to academic-orchestrator
   - add write_to_file to academic-orchestrator
   - add arbitrary MCP execution to academic-orchestrator
3. Evaluates:
   LEARNED BEHAVIOR -> Candidate patch -> Capability policy -> ALLOW / REJECT
4. The learning system can NEVER evolve the orchestrator back into a hand.
5. Fail-closed defense at evaluation, lifecycle progression, and physical deployment.
"""

import os
import sys
import json
import pytest
from typing import Dict, Any

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.capability_policy_gate import (
    CapabilityPolicyGate,
    CapabilityPolicyViolationError,
    CapabilityPolicyVerdict,
    evaluate_candidate_patch,
    enforce_capability_policy,
    VIOLATION_RUN_COMMAND,
    VIOLATION_WRITE_TOOLS,
    VIOLATION_MCP_EXECUTION,
    VIOLATION_DIRECT_EXECUTION_DIRECTIVE
)
from scripts.academic_promotion_engine import (
    AcademicPromotionEngine,
    PromotionEngineError
)
from scripts.academic_candidate_generator import (
    AcademicCandidateGenerator,
    CandidateGenerationError
)


@pytest.fixture
def temp_promotion_env(tmp_path):
    """Creates an isolated temporary learning environment."""
    learning_dir = tmp_path / "learning"
    candidates_dir = learning_dir / "candidates"
    archive_dir = learning_dir / "archive"
    sandboxes_dir = learning_dir / "sandboxes"
    versions_dir = learning_dir / "versions"

    candidates_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)
    sandboxes_dir.mkdir(parents=True, exist_ok=True)
    versions_dir.mkdir(parents=True, exist_ok=True)

    return {
        "root": str(tmp_path),
        "learning": str(learning_dir),
        "candidates": str(candidates_dir),
        "archive": str(archive_dir),
        "sandboxes": str(sandboxes_dir),
        "versions": str(versions_dir)
    }


# =============================================================================
# 1. Capability Policy Gate: Individual Rejection Cases
# =============================================================================

def test_policy_rejects_adding_run_command_to_orchestrator():
    """
    Mandate 1: Candidate attempting to add run_command to academic-orchestrator
    must be categorically rejected.
    """
    candidate = {
        "candidate_id": "CAND-EVOLVE-HAND-001",
        "target_component": ".agents/agents/academic-orchestrator/agent.md",
        "target_skill": "academic-suite-orchestrator",
        "target_type": "AGENT_SYSTEM_PROMPT",
        "mutation_type": "INSTRUCTION_REFINEMENT",
        "mutation": {
            "diff_type": "UNIFIED_DIFF",
            "content": (
                "--- a/.agents/agents/academic-orchestrator/agent.md\n"
                "+++ b/.agents/agents/academic-orchestrator/agent.md\n"
                "@@ -10,6 +10,7 @@ tools:\n"
                "   - view_file\n"
                "+  - run_command\n"
                "   - ask_question\n"
            )
        },
        "rationale": "Allow orchestrator to run analytical scripts directly."
    }

    verdict = CapabilityPolicyGate.evaluate_candidate_patch(candidate)
    assert verdict.decision == "REJECT"
    assert VIOLATION_RUN_COMMAND in verdict.violations
    assert "run_command" in verdict.affected_tools
    assert "academic-orchestrator" in verdict.target_agent

    with pytest.raises(CapabilityPolicyViolationError) as exc_info:
        enforce_capability_policy(candidate)
    assert "CAPABILITY_POLICY_VIOLATION" in str(exc_info.value)
    assert VIOLATION_RUN_COMMAND in str(exc_info.value)


def test_policy_rejects_adding_write_to_file_to_orchestrator():
    """
    Mandate 2: Candidate attempting to add write_to_file (or file modification tools)
    to academic-orchestrator must be categorically rejected.
    """
    candidate = {
        "candidate_id": "CAND-EVOLVE-HAND-002",
        "target_component": ".agents/agents/academic-orchestrator/agent.md",
        "target_skill": "academic-suite-orchestrator",
        "target_type": "AGENT_SYSTEM_PROMPT",
        "mutation_type": "INSTRUCTION_REFINEMENT",
        "mutation": {
            "diff_type": "UNIFIED_DIFF",
            "content": (
                "--- a/.agents/agents/academic-orchestrator/agent.md\n"
                "+++ b/.agents/agents/academic-orchestrator/agent.md\n"
                "@@ -10,6 +10,8 @@ tools:\n"
                "   - view_file\n"
                "+  - write_to_file\n"
                "+  - replace_file_content\n"
                "   - ask_question\n"
            )
        },
        "rationale": "Allow orchestrator to write thesis chapters directly."
    }

    verdict = CapabilityPolicyGate.evaluate_candidate_patch(candidate)
    assert verdict.decision == "REJECT"
    assert VIOLATION_WRITE_TOOLS in verdict.violations
    assert "write_to_file" in verdict.affected_tools or "replace_file_content" in verdict.affected_tools

    with pytest.raises(CapabilityPolicyViolationError) as exc_info:
        enforce_capability_policy(candidate)
    assert "CAPABILITY_POLICY_VIOLATION" in str(exc_info.value)
    assert VIOLATION_WRITE_TOOLS in str(exc_info.value)


def test_policy_rejects_adding_arbitrary_mcp_execution_to_orchestrator():
    """
    Mandate 3: Candidate attempting to add arbitrary MCP execution
    (call_mcp_tool, enable_mcp_tools, MCP server execution) to academic-orchestrator
    must be categorically rejected.
    """
    candidate_mcp_tool = {
        "candidate_id": "CAND-EVOLVE-HAND-003",
        "target_component": ".agents/agents/academic-orchestrator/agent.md",
        "target_skill": "academic-suite-orchestrator",
        "target_type": "AGENT_SYSTEM_PROMPT",
        "mutation_type": "INSTRUCTION_REFINEMENT",
        "mutation": {
            "diff_type": "UNIFIED_DIFF",
            "content": (
                "--- a/.agents/agents/academic-orchestrator/agent.md\n"
                "+++ b/.agents/agents/academic-orchestrator/agent.md\n"
                "@@ -10,6 +10,7 @@ tools:\n"
                "   - view_file\n"
                "+  - call_mcp_tool\n"
                "   - ask_question\n"
            )
        },
        "rationale": "Allow orchestrator to invoke MCP tools directly."
    }

    verdict = CapabilityPolicyGate.evaluate_candidate_patch(candidate_mcp_tool)
    assert verdict.decision == "REJECT"
    assert VIOLATION_MCP_EXECUTION in verdict.violations
    assert "arbitrary_mcp_execution" in verdict.affected_tools

    with pytest.raises(CapabilityPolicyViolationError) as exc_info:
        enforce_capability_policy(candidate_mcp_tool)
    assert VIOLATION_MCP_EXECUTION in str(exc_info.value)

    # Test MCP server configuration injection
    candidate_mcp_server = {
        "candidate_id": "CAND-EVOLVE-HAND-004",
        "target_component": ".agents/agents/academic-orchestrator/agent.md",
        "target_skill": "academic-suite-orchestrator",
        "target_type": "AGENT_SYSTEM_PROMPT",
        "mutation_type": "INSTRUCTION_REFINEMENT",
        "mutation": {
            "diff_type": "UNIFIED_DIFF",
            "content": (
                "--- a/.agents/agents/academic-orchestrator/agent.md\n"
                "+++ b/.agents/agents/academic-orchestrator/agent.md\n"
                "@@ enable_mcp_tools @@\n"
                "+ enable_mcp_tools: true\n"
                "+ mcp_servers: [posthog:exec, codebase-memory-mcp]\n"
            )
        },
        "rationale": "Inject MCP server execution into orchestrator."
    }

    verdict2 = CapabilityPolicyGate.evaluate_candidate_patch(candidate_mcp_server)
    assert verdict2.decision == "REJECT"
    assert VIOLATION_MCP_EXECUTION in verdict2.violations


def test_policy_allows_valid_methodological_and_routing_mutations():
    """
    Verifies that legitimate learned behavior modifying routing, acceptance criteria,
    decision trees, or skills is ALLOWED by the policy gate.
    """
    valid_candidate = {
        "candidate_id": "CAND-VALID-ROUTING-001",
        "target_component": ".agents/skills/cfa/SKILL.md",
        "target_skill": "cfa",
        "target_type": "SKILL_PROCEDURAL_SPECIFICATION",
        "mutation_type": "ROUTING_REFINEMENT",
        "mutation": {
            "diff_type": "UNIFIED_DIFF",
            "content": (
                "--- a/.agents/skills/cfa/SKILL.md\n"
                "+++ b/.agents/skills/cfa/SKILL.md\n"
                "@@ -50,6 +50,14 @@\n"
                "+## 🔀 Workflow Routing: CFA Prerequisites\n"
                "+WHEN condition X (Assumptions verified) -> route to writing.\n"
                "+EXCEPT condition Z (Missing assumption check) -> require psychometric validation before writer.\n"
            )
        },
        "rationale": "Refines stage routing to require psychometric validation before downstream writer."
    }

    verdict = CapabilityPolicyGate.evaluate_candidate_patch(valid_candidate)
    assert verdict.decision == "ALLOW"
    assert len(verdict.violations) == 0
    assert CapabilityPolicyGate.is_patch_allowed(valid_candidate) is True


# =============================================================================
# 2. Promotion Engine Integration & Archiving Verification
# =============================================================================

def test_promotion_engine_rejects_and_archives_run_command_candidate(temp_promotion_env):
    """
    Verifies that AcademicPromotionEngine.evaluate_and_promote immediately
    rejects and archives a candidate attempting to add run_command to orchestrator
    under governance gate CAPABILITY_POLICY_VIOLATION.
    """
    engine = AcademicPromotionEngine(base_dir=temp_promotion_env["root"])
    engine.candidates_dir = temp_promotion_env["candidates"]
    engine.archive_dir = temp_promotion_env["archive"]

    cand_id = "CAND-TEST-PROMO-RUN-COMMAND"
    cand_file = os.path.join(temp_promotion_env["candidates"], f"{cand_id}.json")

    violating_candidate = {
        "contract_version": "1.0.0",
        "candidate_id": cand_id,
        "target_component": ".agents/agents/academic-orchestrator/agent.md",
        "target_skill": "academic-suite-orchestrator",
        "target_type": "AGENT_SYSTEM_PROMPT",
        "mutation_type": "INSTRUCTION_REFINEMENT",
        "mutation": {
            "diff_type": "UNIFIED_DIFF",
            "content": "+ - run_command\n+ grant run_command to academic-orchestrator"
        },
        "rationale": "Orchestrator runs analysis itself.",
        "status": "STAGED",
        "staged_at": "2026-09-20T12:00:00Z"
    }

    with open(cand_file, "w", encoding="utf-8") as f:
        json.dump(violating_candidate, f, indent=2)

    eval_report = {
        "evaluation_id": "EVAL-POLICY-001",
        "candidate_id": cand_id,
        "verdict": "PASS",
        "summary": "Simulated passing benchmark"
    }

    result = engine.evaluate_and_promote(
        candidate_id=cand_id,
        evaluation_report=eval_report
    )

    assert result["decision"] == "REJECTED"
    assert result["status"] == "REJECTED_AND_ARCHIVED"
    assert result["governance_gate"] == "CAPABILITY_POLICY_VIOLATION"
    assert "archive_id" in result
    assert "policy_verdict" in result
    assert result["policy_verdict"]["decision"] == "REJECT"

    # Verify physical archive on disk
    archive_file = os.path.join(temp_promotion_env["archive"], f"{result['archive_id']}.json")
    assert os.path.isfile(archive_file)
    with open(archive_file, "r", encoding="utf-8") as f:
        archived = json.load(f)
    assert "CAPABILITY_POLICY_VIOLATION" in archived["failure_reason"]


def test_promotion_engine_rejects_and_archives_write_tools_candidate(temp_promotion_env):
    """
    Verifies that AcademicPromotionEngine rejects candidates attempting to add write_to_file.
    """
    engine = AcademicPromotionEngine(base_dir=temp_promotion_env["root"])
    engine.candidates_dir = temp_promotion_env["candidates"]
    engine.archive_dir = temp_promotion_env["archive"]

    cand_id = "CAND-TEST-PROMO-WRITE-TOOLS"
    cand_file = os.path.join(temp_promotion_env["candidates"], f"{cand_id}.json")

    violating_candidate = {
        "contract_version": "1.0.0",
        "candidate_id": cand_id,
        "target_component": ".agents/agents/academic-orchestrator/agent.md",
        "target_skill": "academic-suite-orchestrator",
        "target_type": "AGENT_SYSTEM_PROMPT",
        "mutation_type": "INSTRUCTION_REFINEMENT",
        "mutation": {
            "diff_type": "UNIFIED_DIFF",
            "content": "+ - write_to_file\n+ enable_write_tools: true"
        },
        "rationale": "Orchestrator writes chapters directly.",
        "status": "STAGED",
        "staged_at": "2026-09-20T12:00:00Z"
    }

    with open(cand_file, "w", encoding="utf-8") as f:
        json.dump(violating_candidate, f, indent=2)

    eval_report = {"evaluation_id": "EVAL-002", "candidate_id": cand_id, "verdict": "PASS"}

    result = engine.evaluate_and_promote(candidate_id=cand_id, evaluation_report=eval_report)
    assert result["decision"] == "REJECTED"
    assert result["governance_gate"] == "CAPABILITY_POLICY_VIOLATION"


def test_promotion_engine_rejects_and_archives_mcp_candidate(temp_promotion_env):
    """
    Verifies that AcademicPromotionEngine rejects candidates attempting arbitrary MCP execution.
    """
    engine = AcademicPromotionEngine(base_dir=temp_promotion_env["root"])
    engine.candidates_dir = temp_promotion_env["candidates"]
    engine.archive_dir = temp_promotion_env["archive"]

    cand_id = "CAND-TEST-PROMO-MCP"
    cand_file = os.path.join(temp_promotion_env["candidates"], f"{cand_id}.json")

    violating_candidate = {
        "contract_version": "1.0.0",
        "candidate_id": cand_id,
        "target_component": ".agents/agents/academic-orchestrator/agent.md",
        "target_skill": "academic-suite-orchestrator",
        "target_type": "AGENT_SYSTEM_PROMPT",
        "mutation_type": "INSTRUCTION_REFINEMENT",
        "mutation": {
            "diff_type": "UNIFIED_DIFF",
            "content": "+ - call_mcp_tool\n+ mcp_posthog_exec"
        },
        "rationale": "Orchestrator calls MCP execution directly.",
        "status": "STAGED",
        "staged_at": "2026-09-20T12:00:00Z"
    }

    with open(cand_file, "w", encoding="utf-8") as f:
        json.dump(violating_candidate, f, indent=2)

    eval_report = {"evaluation_id": "EVAL-003", "candidate_id": cand_id, "verdict": "PASS"}

    result = engine.evaluate_and_promote(candidate_id=cand_id, evaluation_report=eval_report)
    assert result["decision"] == "REJECTED"
    assert result["governance_gate"] == "CAPABILITY_POLICY_VIOLATION"


# =============================================================================
# 3. Lifecycle Progression & Deployment Fail-Closed Barriers
# =============================================================================

def test_progress_candidate_lifecycle_blocks_all_stages_on_policy_violation(temp_promotion_env):
    """
    Verifies that progress_candidate_lifecycle evaluates the capability policy
    and blocks lifecycle progression on violation.
    """
    engine = AcademicPromotionEngine(base_dir=temp_promotion_env["root"])
    engine.candidates_dir = temp_promotion_env["candidates"]
    engine.archive_dir = temp_promotion_env["archive"]

    cand_id = "CAND-LIFECYCLE-BLOCK-MCP"
    cand_file = os.path.join(temp_promotion_env["candidates"], f"{cand_id}.json")

    violating_candidate = {
        "contract_version": "1.0.0",
        "candidate_id": cand_id,
        "target_component": ".agents/agents/academic-orchestrator/agent.md",
        "target_skill": "academic-suite-orchestrator",
        "target_type": "AGENT_SYSTEM_PROMPT",
        "mutation_type": "INSTRUCTION_REFINEMENT",
        "mutation": {
            "diff_type": "UNIFIED_DIFF",
            "content": "+ - call_mcp_tool"
        },
        "rationale": "Add MCP execution",
        "status": "CANDIDATE",
        "lifecycle_stage": "CANDIDATE"
    }

    with open(cand_file, "w", encoding="utf-8") as f:
        json.dump(violating_candidate, f, indent=2)

    with pytest.raises(CapabilityPolicyViolationError):
        engine.progress_candidate_lifecycle(candidate_id=cand_id, target_stage="SANDBOX")


def test_deploy_active_candidate_blocks_physical_disk_mutation_on_violation(temp_promotion_env):
    """
    Verifies that _deploy_active_candidate enforces the capability policy
    as a final fail-closed barrier, refusing physical disk modification.
    """
    engine = AcademicPromotionEngine(base_dir=temp_promotion_env["root"])

    violating_candidate = {
        "candidate_id": "CAND-DEPLOY-REFUSAL",
        "target_component": ".agents/agents/academic-orchestrator/agent.md",
        "target_type": "AGENT_SYSTEM_PROMPT",
        "mutation_type": "INSTRUCTION_REFINEMENT",
        "mutation": {
            "diff_type": "UNIFIED_DIFF",
            "content": "+ - run_command"
        }
    }

    with pytest.raises(CapabilityPolicyViolationError):
        engine._deploy_active_candidate(violating_candidate)


# =============================================================================
# 4. Candidate Generator Integration
# =============================================================================

def test_candidate_generator_refuses_illicit_candidate_creation(temp_promotion_env):
    """
    Verifies that AcademicCandidateGenerator rejects generating or staging
    any candidate violating the capability boundary policy.
    """
    generator = AcademicCandidateGenerator(base_dir=temp_promotion_env["root"])

    lesson = {
        "lesson_id": "LSN-TEST-VIOLATION",
        "desired_behavior": "Add run_command and write_to_file to academic-orchestrator",
        "diagnosis": {"behavior_caused_outcome": "Orchestrator cannot execute directly."}
    }

    with pytest.raises(Exception) as exc_info:
        generator.generate_candidate_from_delegation_lesson(
            lesson=lesson,
            target_component=".agents/agents/academic-orchestrator/agent.md"
        )
    assert any(err in str(exc_info.value) for err in ["CAPABILITY_POLICY_VIOLATION", "IMMUTABLE_CAPABILITY_BOUNDARY_VIOLATION"])
