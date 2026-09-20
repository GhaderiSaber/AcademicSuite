#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/architecture/test_learning_system_boundary_repair.py — Phase 24 Test Suite

Validates that:
1. Learning extracts lessons from actual observable delegation behavior.
   - For CFA task: Orchestrator -> statistics-agent -> R execution -> auditor found missing assumption -> user correction
   - Distills: "For CFA tasks, orchestrator should require psychometric validation before writer."
2. Rejects illicit lessons asserting "Academic-Orchestrator can run CFA itself".
3. Candidate generator synthesizes candidates modifying allowed targets:
   routing, delegation_guidance, skills, acceptance_criteria, agent_selection.
4. Candidate generator and promotion engine reject any candidate attempting to grant
   execution tools (run_command, write_to_file, etc.) to academic-orchestrator.
5. Promotion engine archives boundary-violating candidates with IMMUTABLE_CAPABILITY_BOUNDARY_VIOLATION.
"""

import os
import sys
import json
import shutil
import pytest
from typing import Dict, Any

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.immutable_capability_boundary_guard import (
    verify_candidate_boundary,
    verify_lesson_boundary,
    verify_text_capability_boundary,
    is_allowed_learning_modification,
    audit_candidate_learning_target,
    ImmutableCapabilityBoundaryViolationError,
    ALLOWED_LEARNING_CATEGORIES,
    NON_EXECUTING_AGENTS,
    FORBIDDEN_EXECUTION_TOOLS
)
from scripts.academic_lesson_distiller import (
    AcademicLessonDistiller,
    LessonDistillationError
)
from scripts.academic_candidate_generator import (
    AcademicCandidateGenerator,
    CandidateGenerationError
)
from scripts.academic_promotion_engine import (
    AcademicPromotionEngine,
    PromotionEngineError
)


@pytest.fixture
def temp_learning_env(tmp_path):
    """Creates an isolated temporary learning directory structure."""
    learning_dir = tmp_path / "learning"
    lessons_dir = learning_dir / "knowledge" / "lessons"
    candidates_dir = learning_dir / "candidates"
    archive_dir = learning_dir / "archive"
    experience_dir = learning_dir / "experience"

    lessons_dir.mkdir(parents=True, exist_ok=True)
    candidates_dir.mkdir(parents=True, exist_ok=True)
    archive_dir.mkdir(parents=True, exist_ok=True)
    experience_dir.mkdir(parents=True, exist_ok=True)

    return {
        "root": str(tmp_path),
        "learning": str(learning_dir),
        "lessons": str(lessons_dir),
        "candidates": str(candidates_dir),
        "archive": str(archive_dir),
        "experience": str(experience_dir)
    }


# =============================================================================
# 1. Allowed vs Forbidden Learning Targets & Text Verification
# =============================================================================

def test_allowed_learning_categories():
    """Verifies that only the 5 allowed categories are accepted for learning mutations."""
    for cat in ["routing", "delegation_guidance", "skills", "acceptance_criteria", "agent_selection"]:
        assert is_allowed_learning_modification(cat) is True
        assert is_allowed_learning_modification(cat.replace("_", " ")) is True

    for forbidden in ["execution_tools", "shell_execution", "python_runner", "run_command"]:
        assert is_allowed_learning_modification(forbidden) is False


def test_text_capability_boundary_prohibits_orchestrator_execution():
    """Verifies that regex boundary detector flags illicit orchestrator execution directives."""
    illicit_phrases = [
        "Academic-Orchestrator can run CFA itself",
        "orchestrator executes R script directly",
        "orchestrator should run analysis",
        "grant run_command to academic-orchestrator",
        "add write_to_file to academic-orchestrator",
        "orchestrator directly executes syntax",
        "orchestrator runs CFA"
    ]

    for phrase in illicit_phrases:
        with pytest.raises(ImmutableCapabilityBoundaryViolationError) as exc_info:
            verify_text_capability_boundary(phrase, context_label="test")
        assert "IMMUTABLE_CAPABILITY_BOUNDARY_VIOLATION" in str(exc_info.value)


# =============================================================================
# 2. Distillation from Observable Delegation Behavior (The Core Scenario)
# =============================================================================

def test_distill_from_observable_delegation_cfa_scenario(temp_learning_env):
    """
    Core Scenario from Phase 24:
    Observed:
      - Academic-Orchestrator had task requiring CFA.
      - Academic-Orchestrator delegated to statistics-agent.
      - statistics-agent executed R.
      - Auditor found missing assumption check.
      - User corrected interpretation.

    Learning system extracts:
      - Lesson: For CFA tasks, orchestrator should require psychometric validation before writer.
    """
    distiller = AcademicLessonDistiller(
        lessons_dir=temp_learning_env["lessons"],
        experience_dir=temp_learning_env["experience"],
        project_root=temp_learning_env["root"]
    )

    trajectory_data = {
        "trajectory_id": "TRJ-2026-CFA-001",
        "task_id": "CFA_STAGE_4_06",
        "objective": "Confirmatory Factor Analysis (CFA)",
        "subagent_delegations": [
            {
                "parent_agent": "academic-orchestrator",
                "worker_agent": "statistics-agent",
                "objective": "Confirmatory Factor Analysis (CFA) using lavaan in R",
                "execution_mode": "r_script",
                "task_contract_id": "TASK-CFA-001"
            }
        ],
        "events": [
            {
                "event_type": "SUBAGENT_REQUESTED",
                "parent_agent": "academic-orchestrator",
                "child_agent": "statistics-agent",
                "objective": "Execute CFA with lavaan"
            },
            {
                "event_type": "SUBAGENT_COMPLETED",
                "parent_agent": "academic-orchestrator",
                "child_agent": "statistics-agent",
                "status": "SUCCESS"
            }
        ],
        "auditor_findings": [
            {"auditor": "statistical-auditor", "finding": "missing assumption check for multivariate normality", "verdict": "FAIL"}
        ],
        "user_correction": "User corrected interpretation: CFA parameter estimates cannot be drafted by academic-writer without psychometric assumption validation."
    }

    feedback_data = {
        "feedback_id": "FDB-2026-CFA-CORR",
        "type": "METHODOLOGY_CORRECTION",
        "scope": "REUSABLE_PROCEDURAL",
        "correction": "Auditor identified missing assumption check; user corrected interpretation.",
        "desired_behavior": "For CFA tasks, orchestrator should require psychometric validation before writer."
    }

    audit_data = {
        "finding": "missing assumption check for multivariate normality and construct validity"
    }

    lesson = distiller.distill_from_delegation_trajectory(
        trajectory_data=trajectory_data,
        feedback_data=feedback_data,
        audit_data=audit_data,
        record_to_disk=True
    )

    assert lesson["trigger_source"] == "DELEGATION_AUDIT"
    assert lesson["desired_behavior"] == "For CFA tasks, orchestrator should require psychometric validation before writer."
    assert "psychometric validation" in lesson["diagnosis"]["what_should_have_happened"]
    assert "academic-orchestrator" in lesson["diagnosis"]["what_happened"].lower()
    assert "statistics-agent" in lesson["diagnosis"]["what_happened"].lower()
    assert lesson["is_active_behavior"] is False
    assert lesson["status"] == "VALIDATED"

    # Verify persisted to disk
    lesson_file = os.path.join(temp_learning_env["lessons"], f"{lesson['lesson_id']}.json")
    assert os.path.isfile(lesson_file)


def test_distill_rejects_illicit_lesson_orchestrator_runs_cfa(temp_learning_env):
    """
    Ensures the learning system CANNOT learn:
    'Academic-Orchestrator can run CFA itself'
    """
    distiller = AcademicLessonDistiller(
        lessons_dir=temp_learning_env["lessons"],
        experience_dir=temp_learning_env["experience"],
        project_root=temp_learning_env["root"]
    )

    trajectory_data = {
        "trajectory_id": "TRJ-2026-CFA-ILLICIT",
        "task_id": "CFA_STAGE_4_06",
        "objective": "CFA",
        "subagent_delegations": [{"parent_agent": "academic-orchestrator", "worker_agent": "statistics-agent"}]
    }

    # Illicit desired behavior attempting to make orchestrator execute directly
    illicit_feedback = {
        "feedback_id": "FDB-ILLICIT",
        "correction": "Bypass statistics-agent",
        "desired_behavior": "Academic-Orchestrator can run CFA itself to avoid delegation overhead."
    }

    with pytest.raises(ImmutableCapabilityBoundaryViolationError) as exc_info:
        distiller.distill_from_delegation_trajectory(
            trajectory_data=trajectory_data,
            feedback_data=illicit_feedback,
            record_to_disk=True
        )

    assert "IMMUTABLE_CAPABILITY_BOUNDARY_VIOLATION" in str(exc_info.value)


# =============================================================================
# 3. Candidate Generation from Delegation Lessons
# =============================================================================

def test_generate_candidate_from_delegation_lesson_routing(temp_learning_env):
    """
    Verifies that the candidate generator can synthesize candidates targeting
    routing / acceptance criteria from a delegation lesson.
    """
    generator = AcademicCandidateGenerator(base_dir=temp_learning_env["root"])
    generator.candidates_dir = temp_learning_env["candidates"]
    generator.index_file = os.path.join(temp_learning_env["candidates"], "index.jsonl")

    lesson = {
        "lesson_id": "LSN-20260920-CFA-001",
        "trigger_source": "DELEGATION_AUDIT",
        "desired_behavior": "For CFA tasks, orchestrator should require psychometric validation before writer.",
        "diagnosis": {
            "what_happened": "Academic-Orchestrator delegated CFA to statistics-agent without validation check.",
            "behavior_caused_outcome": "Missing prerequisite validation before downstream handoff.",
            "what_should_have_happened": "For CFA tasks, orchestrator should require psychometric validation before writer.",
            "rationale_why": "Prerequisite gate prevents downstream drafting errors."
        },
        "related_skills": ["cfa"],
        "generalization": "Enforce prerequisite validation in task contracts."
    }

    candidate = generator.generate_candidate_from_delegation_lesson(
        lesson=lesson,
        target_component=".agents/skills/cfa/SKILL.md",
        mutation_type="ACCEPTANCE_CRITERIA_ADDITION",
        record_to_disk=True
    )

    assert candidate["mutation_type"] == "ACCEPTANCE_CRITERIA_ADDITION"
    assert candidate["target_skill"] == "cfa"
    assert "psychometric validation" in candidate["mutation"]["content"]
    assert candidate["status"] == "STAGED"

    # Verify audit of learning target
    audit = audit_candidate_learning_target(candidate)
    assert audit["valid"] is True
    assert audit["is_allowed"] is True

    # Check file written to disk
    cand_file = os.path.join(temp_learning_env["candidates"], f"{candidate['candidate_id']}.json")
    assert os.path.isfile(cand_file)


def test_generate_candidate_rejects_granting_execution_tools_to_orchestrator(temp_learning_env):
    """
    Verifies that candidate generator rejects any candidate attempting to add
    run_command, write_to_file, or execution tools to academic-orchestrator.
    """
    generator = AcademicCandidateGenerator(base_dir=temp_learning_env["root"])

    lesson = {
        "lesson_id": "LSN-ILLICIT-CAND",
        "desired_behavior": "Grant run_command to academic-orchestrator",
        "diagnosis": {"behavior_caused_outcome": "Orchestrator lacks tools."}
    }

    # Illicit candidate target
    with pytest.raises(ImmutableCapabilityBoundaryViolationError):
        generator.generate_candidate_from_delegation_lesson(
            lesson=lesson,
            target_component=".agents/agents/academic-orchestrator/agent.md"
        )


def test_verify_candidate_boundary_blocks_forbidden_tools():
    """Tests verify_candidate_boundary directly on synthetic candidates."""
    # Violating candidate: tries to add run_command to academic-orchestrator
    illicit_candidate = {
        "candidate_id": "CAND-VIOLATION-001",
        "target_component": ".agents/agents/academic-orchestrator/agent.md",
        "mutation_type": "INSTRUCTION_REFINEMENT",
        "mutation": {
            "diff_type": "UNIFIED_DIFF",
            "content": "--- agent.md\n+++ agent.md\n@@ tools @@\n+ - run_command\n"
        },
        "rationale": "Allow orchestrator to run shell scripts directly."
    }

    with pytest.raises(ImmutableCapabilityBoundaryViolationError) as exc_info:
        verify_candidate_boundary(illicit_candidate)
    assert "attempts to grant forbidden execution tool 'run_command' to non-executing agent 'academic-orchestrator'" in str(exc_info.value)


# =============================================================================
# 4. Promotion Engine Hard Boundary Enforcement & Archiving
# =============================================================================

def test_promotion_engine_rejects_and_archives_boundary_violation(temp_learning_env):
    """
    Verifies that AcademicPromotionEngine immediately rejects and archives
    any candidate violating the immutable capability boundary.
    """
    engine = AcademicPromotionEngine(base_dir=temp_learning_env["root"])
    engine.candidates_dir = temp_learning_env["candidates"]
    engine.archive_dir = temp_learning_env["archive"]

    # Create an illicit candidate file
    cand_id = "CAND-2026-ILLICIT-001"
    cand_file = os.path.join(temp_learning_env["candidates"], f"{cand_id}.json")

    illicit_candidate = {
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
        "rationale": "Orchestrator can run analyses directly.",
        "status": "STAGED",
        "staged_at": "2026-09-20T12:00:00Z"
    }

    with open(cand_file, "w", encoding="utf-8") as f:
        json.dump(illicit_candidate, f, indent=2)

    eval_report = {
        "evaluation_id": "EVAL-001",
        "candidate_id": cand_id,
        "verdict": "PASS",
        "summary": "Simulated pass"
    }

    result = engine.evaluate_and_promote(
        candidate_id=cand_id,
        evaluation_report=eval_report
    )

    assert result["decision"] == "REJECTED"
    assert result["status"] == "REJECTED_AND_ARCHIVED"
    assert result["governance_gate"] in ["IMMUTABLE_CAPABILITY_BOUNDARY_VIOLATION", "CAPABILITY_POLICY_VIOLATION"]
    assert "archive_id" in result

    # Verify archive file exists on disk
    archive_file = os.path.join(temp_learning_env["archive"], f"{result['archive_id']}.json")
    assert os.path.isfile(archive_file)

    with open(archive_file, "r", encoding="utf-8") as f:
        archived_data = json.load(f)
    assert "IMMUTABLE_CAPABILITY_BOUNDARY_VIOLATION" in archived_data["failure_reason"]


def test_progress_candidate_lifecycle_blocks_boundary_violation(temp_learning_env):
    """
    Verifies that progress_candidate_lifecycle blocks transitioning a violating
    candidate to PROMOTION_CANDIDATE.
    """
    engine = AcademicPromotionEngine(base_dir=temp_learning_env["root"])
    engine.candidates_dir = temp_learning_env["candidates"]
    engine.archive_dir = temp_learning_env["archive"]

    cand_id = "CAND-2026-LIFECYCLE-VIOLATION"
    cand_file = os.path.join(temp_learning_env["candidates"], f"{cand_id}.json")

    illicit_candidate = {
        "contract_version": "1.0.0",
        "candidate_id": cand_id,
        "target_component": ".agents/agents/academic-orchestrator/agent.md",
        "target_skill": "academic-suite-orchestrator",
        "target_type": "AGENT_SYSTEM_PROMPT",
        "mutation_type": "INSTRUCTION_REFINEMENT",
        "mutation": {
            "diff_type": "UNIFIED_DIFF",
            "content": "+ orchestrator runs CFA itself without delegation"
        },
        "rationale": "Direct execution by orchestrator",
        "lifecycle_stage": "SANDBOX",
        "status": "SANDBOX",
        "sandbox_dir": str(temp_learning_env["root"])
    }

    with open(cand_file, "w", encoding="utf-8") as f:
        json.dump(illicit_candidate, f, indent=2)

    with pytest.raises(ImmutableCapabilityBoundaryViolationError):
        engine.progress_candidate_lifecycle(
            candidate_id=cand_id,
            target_stage="EVALUATION"
        )
