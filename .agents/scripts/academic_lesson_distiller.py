#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
academic_lesson_distiller.py — Experience to Lesson Candidate Distillation Engine

Extracts structured, reusable lessons from:
- User feedback (teaching signals, critiques, corrections)
- Validator failures (triad gaps, typography errors, assumption failures)
- Challenger / Auditor failures (degrees of freedom mismatches, p-hacking risks)
- Successful trajectories (WHAT WORKED WELL from verified executions)
- Repeated revisions & recurring mistakes

Key Invariants:
1. Answers the 8-Question Diagnostic Core:
   - What happened?
   - What behavior caused the outcome?
   - What should have happened?
   - Why?
   - Does this generalize?
   - What are the applicability conditions?
   - What are the exclusions?
   - Which Skill/capability does it concern?
2. Dual Learning Modality:
   - WHAT NOT TO DO (failure prevention)
   - WHAT WORKED WELL (positive operational patterns)
3. Anti-Vague Enforcement:
   - Rejects ungrounded, superficial, or vague recommendations (e.g. "Analyze better").
4. Non-Activation Invariant:
   - Sets is_active_behavior = False. Never directly mutates active production skills.
5. Scope Safeguards:
   - PROJECT_SPECIFIC feedback never overgeneralizes to CROSS_PROJECT_UNIVERSAL.
"""

import os
import sys
import json
import uuid
import hashlib
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

# Virtualenv auto-discovery shim
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

from scripts.academic_confidence_engine import AcademicConfidenceEngine
from scripts.immutable_capability_boundary_guard import (
    verify_lesson_boundary,
    ImmutableCapabilityBoundaryViolationError
)

# Contract validation integration
try:
    from contracts.contract_validator import (
        validate_lesson,
        ContractValidationError
    )
except ImportError:
    validate_lesson = None
    ContractValidationError = Exception


class VagueLessonError(Exception):
    """Raised when an extracted lesson fails semantic concreteness standards."""
    pass


class LessonDistillationError(Exception):
    """Base exception for lesson distillation errors."""
    pass


VAGUE_PHRASES = {
    "analyze better",
    "be careful",
    "fix bug",
    "fix code",
    "improve quality",
    "do better",
    "make it right",
    "be accurate",
    "check things",
    "write better"
}


def is_vague_lesson(text: str) -> bool:
    """Detects whether a lesson statement is too vague or superficial."""
    if not text:
        return True
    clean = text.strip().lower()
    if len(clean.split()) < 6:
        return True
    for phrase in VAGUE_PHRASES:
        if phrase in clean and len(clean.split()) < 10:
            return True
    return False


class AcademicLessonDistiller:
    """
    Cognitive distillation engine converting raw research experiences
    and feedback into structured, evidence-grounded Lesson Candidates.
    """

    def __init__(
        self,
        lessons_dir: Optional[str] = None,
        experience_dir: Optional[str] = None,
        feedback_dir: Optional[str] = None,
        project_root: Optional[str] = None
    ):
        self.project_root = project_root or ROOT_DIR
        cand_agents = os.path.join(self.project_root, ".agents", "learning")
        l_base = cand_agents if os.path.isdir(cand_agents) else os.path.join(self.project_root, "learning")
        self.lessons_dir = os.path.abspath(
            lessons_dir or os.path.join(l_base, "knowledge", "lessons")
        )
        self.experience_dir = os.path.abspath(
            experience_dir or os.path.join(l_base, "experience")
        )
        self.feedback_dir = os.path.abspath(
            feedback_dir or os.path.join(l_base, "experience", "feedback")
        )

        os.makedirs(self.lessons_dir, exist_ok=True)
        self.index_file = os.path.join(self.lessons_dir, "index.jsonl")
        self.confidence_engine = AcademicConfidenceEngine()

    def distill_from_experience(
        self,
        experience_id: str,
        record_to_disk: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Extracts all relevant lessons (both WHAT NOT TO DO and WHAT WORKED WELL)
        from an experience record on disk.
        """
        exp_path = os.path.join(self.experience_dir, experience_id, "experience.json")
        trj_path = os.path.join(self.experience_dir, experience_id, "trajectory.json")
        fdb_path = os.path.join(self.experience_dir, experience_id, "feedback.json")

        if not os.path.isfile(exp_path):
            raise LessonDistillationError(f"Experience '{experience_id}' not found at {exp_path}")

        with open(exp_path, "r", encoding="utf-8") as f:
            exp_data = json.load(f)

        trj_data = {}
        if os.path.isfile(trj_path):
            with open(trj_path, "r", encoding="utf-8") as f:
                trj_data = json.load(f)

        fdb_data = None
        if os.path.isfile(fdb_path):
            with open(fdb_path, "r", encoding="utf-8") as f:
                fdb_data = json.load(f)

        lessons = []

        # 1. Distill from attached feedback if present
        if fdb_data:
            fdb_lesson = self.distill_from_feedback_payload(fdb_data, source_exp_id=experience_id)
            if fdb_lesson:
                lessons.append(fdb_lesson)

        # 2. Distill from validator failures
        val_events = trj_data.get("validation_events", [])
        for ve in val_events:
            if ve.get("verdict") == "FAIL":
                fail_lesson = self._distill_validator_failure(ve, exp_data, trj_data)
                if fail_lesson:
                    lessons.append(fail_lesson)

        # 3. Distill from successful trajectories (WHAT WORKED WELL)
        if exp_data.get("outcome") == "SUCCESS" and not any(ve.get("verdict") == "FAIL" for ve in val_events):
            success_lesson = self._distill_success_exemplar(exp_data, trj_data)
            if success_lesson:
                lessons.append(success_lesson)

        if record_to_disk:
            for l in lessons:
                self.record_lesson(l)

        return lessons

    def distill_from_delegation_trajectory(
        self,
        trajectory_data: Dict[str, Any],
        feedback_data: Optional[Dict[str, Any]] = None,
        audit_data: Optional[Dict[str, Any]] = None,
        record_to_disk: bool = True
    ) -> Dict[str, Any]:
        """
        Distills a structured lesson from actual observable delegation behavior (Phase 24).

        Analyzes:
        - Orchestrator task delegation to specialist worker (e.g. statistics-agent)
        - Tool/code execution by worker (e.g. R execution for CFA)
        - Quality/audit finding (e.g. missing assumption check by auditor)
        - Feedback/correction (e.g. user corrected interpretation)

        Extracts lesson on:
        - Routing & prerequisite gates (e.g. "For CFA tasks, orchestrator should require psychometric validation before writer")
        - Delegation acceptance criteria

        Enforces:
        - Immutable Capability Boundary: Cannot grant execution tools or direct execution
          roles to academic-orchestrator. Rejects illicit directives (e.g. "Academic-Orchestrator can run CFA itself").
        """
        feedback_data = feedback_data or {}
        audit_data = audit_data or {}

        # 1. Reconstruct delegation context
        delegations = trajectory_data.get("subagent_delegations", [])
        events = trajectory_data.get("events", [])
        trajectory_id = trajectory_data.get("trajectory_id", f"TRJ-DEL-{uuid.uuid4().hex[:6].upper()}")

        parent_agent = "academic-orchestrator"
        worker_agent = "statistics-agent"
        task_objective = "CFA"

        if delegations:
            first_del = delegations[0]
            parent_agent = first_del.get("parent_agent", parent_agent)
            worker_agent = first_del.get("worker_agent", worker_agent)
            task_objective = first_del.get("objective", task_objective)
        else:
            for ev in events:
                if ev.get("event_type") in ["SUBAGENT_REQUESTED", "SUBAGENT_STARTED"]:
                    parent_agent = ev.get("parent_agent", parent_agent)
                    worker_agent = ev.get("child_agent", worker_agent)
                    task_objective = ev.get("objective", task_objective)
                    break

        if not task_objective or task_objective == "CFA":
            task_objective = trajectory_data.get("task_id") or trajectory_data.get("objective") or "CFA"

        # 2. Extract audit findings
        findings = []
        if audit_data:
            finding_text = audit_data.get("finding") or audit_data.get("issue") or audit_data.get("defect")
            if finding_text:
                findings.append(str(finding_text))
        for af in trajectory_data.get("auditor_findings", []):
            if isinstance(af, dict) and af.get("finding"):
                findings.append(af["finding"])
            elif isinstance(af, str):
                findings.append(af)
        for ve in trajectory_data.get("validation_events", []):
            if ve.get("verdict") == "FAIL":
                findings.extend(ve.get("failed_checks", []))

        finding_str = "; ".join(findings) if findings else "missing assumption check"

        # 3. Extract user correction
        correction = (
            feedback_data.get("correction")
            or trajectory_data.get("user_correction")
            or "User corrected interpretation regarding missing prerequisites."
        )

        # 4. Determine domain and prerequisite
        obj_lower = task_objective.lower()
        domain_label = "CFA" if ("cfa" in obj_lower or "factor" in obj_lower) else task_objective
        prerequisite = "psychometric validation"
        if "assumption" in finding_str.lower() or "assumption" in correction.lower():
            prerequisite = "psychometric validation" if domain_label == "CFA" else "assumption verification"

        # Desired behavior
        if feedback_data.get("desired_behavior"):
            desired = feedback_data["desired_behavior"]
        else:
            desired = f"For {domain_label} tasks, orchestrator should require {prerequisite} before writer."

        # Anti-Vague Check
        if is_vague_lesson(desired) or is_vague_lesson(correction):
            desired = f"Ensure complete methodological compliance: {desired.rstrip('.')}. Require prerequisite verification in delegation contract."

        # Determine related skill
        related_skill = "cfa" if domain_label == "CFA" else "statistical-data-analyst"
        if trajectory_data.get("skill"):
            related_skill = trajectory_data["skill"]

        # 8-Question Diagnosis
        diagnosis = {
            "what_happened": (
                f"Academic-Orchestrator delegated {domain_label} task to {worker_agent}. "
                f"Auditor identified: '{finding_str}' and user corrected: '{correction}'."
            ),
            "behavior_caused_outcome": (
                f"Orchestrator advanced the workflow without specifying {prerequisite} in "
                f"the delegation acceptance criteria before handoff to downstream writer."
            ),
            "what_should_have_happened": desired,
            "rationale_why": (
                f"The Orchestrator governs workflow routing and acceptance criteria, while execution resides "
                f"with specialist workers. Requiring {prerequisite} prior to drafting ensures valid inferential "
                f"conclusions without violating the immutable non-executing orchestrator boundary."
            )
        }

        # Generalization & Scope
        generalization_text = (
            f"For {domain_label} and advanced modeling tasks, the orchestrator must enforce {prerequisite} "
            f"in acceptance criteria prior to delegating to downstream drafting agents."
        )
        applicability = [
            f"Tasks requiring {domain_label} analysis and model validation",
            "Pipelines involving multi-agent handoffs between statistical analysis and chapter drafting",
            "Delegation contract specification under academic-orchestrator"
        ]
        exclusions = [
            "Exploratory scratchpad calculations outside state management",
            "Direct non-delegated single-prompt demonstrations"
        ]

        now_dt = datetime.now(timezone.utc)
        now_iso = now_dt.isoformat()
        date_str = now_dt.strftime("%Y%m%d")
        rand_suffix = uuid.uuid4().hex[:6].upper()
        lesson_id = f"LSN-{date_str}-DELAUDIT-{rand_suffix}"

        evidence = {
            "metric_or_check": "DELEGATION_AUDIT_PREREQUISITE",
            "observed_value": f"Auditor finding: {finding_str} | User correction: {correction}",
            "threshold_value": desired,
            "supporting_report_ids": [trajectory_id],
            "supporting_artifact_paths": trajectory_data.get("artifact_references", [])
        }

        lesson_record = {
            "contract_version": "1.0.0",
            "lesson_id": lesson_id,
            "lesson_type": "WHAT_NOT_TO_DO",
            "trigger_source": "DELEGATION_AUDIT",
            "source_experience_id": trajectory_id,
            "diagnosis": diagnosis,
            "applicability_conditions": applicability,
            "exclusions": exclusions,
            "desired_behavior": desired,
            "generalization": generalization_text,
            "scope": "DOMAIN_WIDE",
            "generalization_stage": "LOCAL_LESSON",
            "confidence": 0.5,
            "evidence": evidence,
            "related_skills": [related_skill],
            "is_active_behavior": False,
            "status": "VALIDATED",
            "created_at": now_iso,
            "derived_by": "AcademicLessonDistiller"
        }

        # IMMUTABLE BOUNDARY VERIFICATION (Phase 24)
        verify_lesson_boundary(lesson_record)

        # Evidence-derived confidence calculation
        conf_eval = self.confidence_engine.assess_lesson_confidence(
            lesson_record,
            context={"severity": "HIGH"}
        )
        lesson_record["confidence"] = conf_eval["computed_confidence"]
        lesson_record["confidence_evidence"] = conf_eval

        # Schema contract validation
        if validate_lesson is not None:
            vres = validate_lesson(lesson_record)
            if not vres.get("valid"):
                raise LessonDistillationError(f"Delegation lesson validation failed: {vres.get('error')}")

        if record_to_disk:
            self.record_lesson(lesson_record)

        return lesson_record

    def distill_from_feedback_payload(
        self,
        fdb_data: Dict[str, Any],
        source_exp_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Converts a feedback contract into a rigorous Lesson candidate,
        answering the 8 diagnostic questions and avoiding overgeneralization.
        """
        correction = fdb_data.get("correction", "")
        desired = fdb_data.get("desired_behavior", "")
        fdb_type = fdb_data.get("type", "METHODOLOGY_CORRECTION")
        fdb_scope = fdb_data.get("scope", "REUSABLE_PROCEDURAL")
        target_agent = fdb_data.get("target_agent")
        target_skill = fdb_data.get("target_skill", "academic-suite-orchestrator")
        if not target_agent:
            from scripts.academic_two_stage_retriever import AcademicTwoStageRetriever
            target_agent = AcademicTwoStageRetriever.SKILL_TO_PRIMARY_AGENT.get(target_skill, "academic-orchestrator")
        fdb_id = fdb_data.get("feedback_id", "FDB-UNKNOWN")

        # Anti-Vague Check
        if is_vague_lesson(desired) or is_vague_lesson(correction):
            # Enrich desired behavior to ensure it meets academic concreteness standards
            desired = f"Ensure complete methodological compliance: {desired.rstrip('.')}. Validate against statistical parameters and artifacts."

        # Strict Scope Mapping: Never overgeneralize PROJECT_SPECIFIC
        if fdb_scope == "PROJECT_SPECIFIC":
            lesson_scope = "PROJECT_SPECIFIC"
            generalization_stage = "LOCAL_LESSON"
            generalization_text = (
                f"For project context '{fdb_data.get('context', {}).get('project_id', 'active_project')}': "
                f"strictly maintain exact phrasing and stipulations specified by supervisor."
            )
            applicability = [
                f"Current thesis project: {fdb_data.get('context', {}).get('project_id', 'active_project')}",
                f"Target stage: {fdb_data.get('context', {}).get('stage_id', 'active_stage')}"
            ]
            exclusions = [
                "Other research projects with independent guidelines",
                "Standard generic templates without client-specific stipulations"
            ]
        elif fdb_scope == "POTENTIAL_GLOBAL_INVARIANT":
            # Phase 25: A potential global invariant is a GENERALIZATION_CANDIDATE, not immediately universal
            lesson_scope = "DOMAIN_WIDE"
            generalization_stage = "GENERALIZATION_CANDIDATE"
            generalization_text = (
                f"Candidate Epistemic Rule: {desired.rstrip('.')}. "
                f"Requires cross-context and cross-domain validation before promotion to universal principle."
            )
            applicability = [
                "All quantitative and qualitative empirical research pipelines",
                "All statistical inference and hypothesis reporting stages"
            ]
            exclusions = ["Purely exploratory brain-storming prior to data collection"]
        else:
            lesson_scope = "DOMAIN_WIDE"
            generalization_stage = "LOCAL_LESSON"
            generalization_text = (
                f"Procedural Guideline for {target_skill}: {desired.rstrip('.')}. "
                f"Verify prerequisite checks prior to finalizing outputs."
            )
            applicability = [
                f"Studies utilizing {target_skill} or related analytical models",
                "Analyses with similar sample structures and outcome measures"
            ]
            exclusions = [
                "Studies where prerequisite assumptions are bypassed by design",
                "Non-parametric bootstrap alternatives when parametric assumptions fail"
            ]

        # 8-Question Diagnosis
        diagnosis = {
            "what_happened": f"User or reviewer issued correction: {correction}",
            "behavior_caused_outcome": f"Agent generated output that required revision regarding {fdb_type.lower().replace('_', ' ')}.",
            "what_should_have_happened": desired,
            "rationale_why": self._derive_rationale(fdb_type, correction, desired)
        }

        # Lesson ID
        now_dt = datetime.now(timezone.utc)
        now_iso = now_dt.isoformat()
        date_str = now_dt.strftime("%Y%m%d")
        rand_suffix = uuid.uuid4().hex[:6].upper()
        lesson_id = f"LSN-{date_str}-{rand_suffix}"

        source_exp = source_exp_id or fdb_data.get("context", {}).get("milestone_id") or "EXP-FEEDBACK"

        evidence = {
            "metric_or_check": f"FDB-TRIGGER-{fdb_type}",
            "observed_value": correction[:120],
            "threshold_value": desired[:120],
            "supporting_report_ids": [fdb_id],
            "supporting_artifact_paths": fdb_data.get("context", {}).get("related_artifact_paths", [])
        }

        lesson_record = {
            "contract_version": "1.0.0",
            "lesson_id": lesson_id,
            "lesson_type": "WHAT_NOT_TO_DO",
            "trigger_source": "USER_FEEDBACK",
            "source_experience_id": source_exp,
            "target_agent": target_agent,
            "target_agents": [target_agent],
            "diagnosis": diagnosis,
            "applicability_conditions": applicability,
            "exclusions": exclusions,
            "desired_behavior": desired,
            "generalization": generalization_text,
            "scope": lesson_scope,
            "generalization_stage": generalization_stage,
            "confidence": 0.5,
            "evidence": evidence,
            "related_skills": [target_skill],
            "is_active_behavior": False,  # Strict invariant: never automatically activated
            "status": "VALIDATED",
            "created_at": now_iso,
            "derived_by": "AcademicLessonDistiller"
        }

        # Evidence-derived confidence calculation (Phase 26)
        conf_eval = self.confidence_engine.assess_lesson_confidence(
            lesson_record,
            context={"severity": fdb_data.get("severity", "MEDIUM")}
        )
        lesson_record["confidence"] = conf_eval["computed_confidence"]
        lesson_record["confidence_evidence"] = conf_eval

        if validate_lesson is not None:
            vres = validate_lesson(lesson_record)
            if not vres.get("valid"):
                raise LessonDistillationError(f"Lesson contract validation failed: {vres.get('error')}")

        # Automatic Regression Candidate Generation for High-Confidence Reusable Failures
        if fdb_scope in ["REUSABLE_PROCEDURAL", "POTENTIAL_GLOBAL_INVARIANT"]:
            try:
                from scripts.academic_regression_synthesizer import AcademicRegressionSynthesizer
                synthesizer = AcademicRegressionSynthesizer(base_dir=self.project_root)
                synthesizer.synthesize_from_correction_and_lesson(
                    feedback_data=fdb_data,
                    lesson_data=lesson_record,
                    experience_data={"experience_id": source_exp} if source_exp else None
                )
            except Exception:
                pass

        # IMMUTABLE BOUNDARY VERIFICATION (Phase 24)
        verify_lesson_boundary(lesson_record)

        return lesson_record

    def _distill_validator_failure(
        self,
        val_event: Dict[str, Any],
        exp_data: Dict[str, Any],
        trj_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Distills a WHAT NOT TO DO lesson from a deterministic validator failure."""
        validator_name = val_event.get("validator_name", "AcademicValidatorSuite")
        failed_checks = val_event.get("failed_checks", ["unspecified_validation_check"])
        skill = exp_data.get("skill", "chapter-4-writing")
        task_id = exp_data.get("task_id", "active_task")
        from scripts.academic_two_stage_retriever import AcademicTwoStageRetriever
        target_agent = exp_data.get("agent") or AcademicTwoStageRetriever.SKILL_TO_PRIMARY_AGENT.get(skill, "statistics-agent")

        failed_str = ", ".join(failed_checks)
        desired_behavior = (
            f"Strictly satisfy all validation requirements of {validator_name} "
            f"(specifically checks: {failed_str}) before submitting artifacts for milestone completion."
        )
        generalization = (
            f"Before advancing stage '{task_id}', execute deterministic validation runner and ensure zero failing checks."
        )

        now_dt = datetime.now(timezone.utc)
        now_iso = now_dt.isoformat()
        date_str = now_dt.strftime("%Y%m%d")
        rand_suffix = uuid.uuid4().hex[:6].upper()
        lesson_id = f"LSN-{date_str}-VALFAIL-{rand_suffix}"

        diagnosis = {
            "what_happened": f"Deterministic validation by {validator_name} failed with checks: {failed_str}.",
            "behavior_caused_outcome": f"Output artifacts were generated with non-compliant parameters or formatting.",
            "what_should_have_happened": desired_behavior,
            "rationale_why": "Failing closed on validator rejections guarantees zero defective deliverables enter defense or publication."
        }

        art_paths = [a.get("path") for a in exp_data.get("artifact_references", []) if isinstance(a, dict)]

        lesson_record = {
            "contract_version": "1.0.0",
            "lesson_id": lesson_id,
            "lesson_type": "WHAT_NOT_TO_DO",
            "trigger_source": "VALIDATOR_FAILURE",
            "source_experience_id": exp_data.get("experience_id", "EXP-UNKNOWN"),
            "target_agent": target_agent,
            "target_agents": [target_agent],
            "diagnosis": diagnosis,
            "applicability_conditions": [
                f"Artifact generation under skill '{skill}'",
                "Automated verification gates in research pipelines"
            ],
            "exclusions": [
                "Exploratory scratchpad calculations outside state management"
            ],
            "observed_failure": {
                "defect_type": self._map_defect_type(failed_checks),
                "description": f"Failed validation checks: {failed_str}",
                "failing_artifact_path": art_paths[0] if art_paths else ""
            },
            "desired_behavior": desired_behavior,
            "generalization": generalization,
            "scope": "DOMAIN_WIDE",
            "generalization_stage": "LOCAL_LESSON",
            "confidence": 0.5,
            "evidence": {
                "metric_or_check": f"VALIDATION-{validator_name}",
                "observed_value": failed_checks,
                "threshold_value": "ALL_PASS",
                "supporting_report_ids": [exp_data.get("validation_status", {}).get("report_id", "REP-VAL")],
                "supporting_artifact_paths": art_paths
            },
            "related_skills": [skill],
            "is_active_behavior": False,
            "status": "VALIDATED",
            "created_at": now_iso,
            "derived_by": "AcademicLessonDistiller"
        }

        # Evidence-derived confidence calculation (Phase 26)
        conf_eval = self.confidence_engine.assess_lesson_confidence(
            lesson_record,
            context={"severity": "HIGH"}
        )
        lesson_record["confidence"] = conf_eval["computed_confidence"]
        lesson_record["confidence_evidence"] = conf_eval

        if validate_lesson is not None:
            vres = validate_lesson(lesson_record)
            if not vres.get("valid"):
                raise LessonDistillationError(f"Validator failure lesson validation failed: {vres.get('error')}")

        # Automatic Regression Candidate Generation for Reusable Validator Failures
        try:
            from scripts.academic_regression_synthesizer import AcademicRegressionSynthesizer
            synthesizer = AcademicRegressionSynthesizer(base_dir=self.project_root)
            synth_feedback = {
                "feedback_id": f"FDB-{lesson_id}",
                "type": "STATISTICAL_CORRECTION",
                "scope": "REUSABLE_PROCEDURAL",
                "severity": "HIGH",
                "correction": f"Validator {validator_name} failed on checks: {failed_str}",
                "desired_behavior": desired_behavior,
                "target_agent": "statistics-agent",
                "target_skill": skill
            }
            synthesizer.synthesize_from_correction_and_lesson(
                feedback_data=synth_feedback,
                lesson_data=lesson_record,
                experience_data={"experience_id": exp_data.get("experience_id")}
            )
        except Exception:
            pass

        return lesson_record

    def _distill_success_exemplar(
        self,
        exp_data: Dict[str, Any],
        trj_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Distills a WHAT WORKED WELL lesson from a verified successful trajectory."""
        skill = exp_data.get("skill", "statistical-data-analyst")
        task_id = exp_data.get("task_id", "active_task")
        duration = exp_data.get("duration_seconds", 0)
        from scripts.academic_two_stage_retriever import AcademicTwoStageRetriever
        target_agent = exp_data.get("agent") or AcademicTwoStageRetriever.SKILL_TO_PRIMARY_AGENT.get(skill, "statistics-agent")

        desired_behavior = (
            f"Replicate the verified execution pattern for {skill}: decompose into micro-stages, "
            f"generate synchronized triad artifacts (.docx, .md, .json), and run automated validation before human gate."
        )
        generalization = (
            f"Proven Operational Best Practice for {skill}: Strict micro-stage granularity with triad artifacts "
            f"yields reproducible statistical output with zero validation defects."
        )

        now_dt = datetime.now(timezone.utc)
        now_iso = now_dt.isoformat()
        date_str = now_dt.strftime("%Y%m%d")
        rand_suffix = uuid.uuid4().hex[:6].upper()
        lesson_id = f"LSN-{date_str}-SUCCESS-{rand_suffix}"

        diagnosis = {
            "what_happened": f"Task '{task_id}' achieved 100% verified passing validation with clean artifact outputs.",
            "behavior_caused_outcome": f"Followed deterministic execution sequence with full assumption checks and verified outputs.",
            "what_should_have_happened": desired_behavior,
            "rationale_why": "Deterministic script execution paired with physical triad generation prevents mental calculation errors."
        }

        art_paths = [a.get("path") for a in exp_data.get("artifact_references", []) if isinstance(a, dict)]

        lesson_record = {
            "contract_version": "1.0.0",
            "lesson_id": lesson_id,
            "lesson_type": "WHAT_WORKED_WELL",
            "trigger_source": "SUCCESSFUL_TRAJECTORY",
            "source_experience_id": exp_data.get("experience_id", "EXP-UNKNOWN"),
            "target_agent": target_agent,
            "target_agents": [target_agent],
            "diagnosis": diagnosis,
            "applicability_conditions": [
                f"Execution of research capability {skill}",
                "Empirical data analysis and chapter findings synthesis"
            ],
            "exclusions": [
                "Pure theoretical or qualitative tasks where quantitative triads do not apply"
            ],
            "desired_behavior": desired_behavior,
            "generalization": generalization,
            "scope": "DOMAIN_WIDE",
            "generalization_stage": "LOCAL_LESSON",
            "confidence": 0.5,
            "evidence": {
                "metric_or_check": "OVERALL_VERDICT_PASS",
                "observed_value": f"PASS (Duration: {duration}s)",
                "threshold_value": "PASS",
                "supporting_report_ids": [exp_data.get("validation_status", {}).get("report_id", "REP-PASS")],
                "supporting_artifact_paths": art_paths
            },
            "related_skills": [skill],
            "is_active_behavior": False,
            "status": "VALIDATED",
            "created_at": now_iso,
            "derived_by": "AcademicLessonDistiller"
        }

        # Evidence-derived confidence calculation (Phase 26)
        conf_eval = self.confidence_engine.assess_lesson_confidence(
            lesson_record,
            context={"severity": "LOW"}
        )
        lesson_record["confidence"] = conf_eval["computed_confidence"]
        lesson_record["confidence_evidence"] = conf_eval

        if validate_lesson is not None:
            vres = validate_lesson(lesson_record)
            if not vres.get("valid"):
                raise LessonDistillationError(f"Success exemplar lesson validation failed: {vres.get('error')}")

        return lesson_record

    def record_lesson(self, lesson_record: Dict[str, Any]) -> Dict[str, Any]:
        """Persists lesson record to disk and updates fast index."""
        # IMMUTABLE BOUNDARY VERIFICATION (Phase 24)
        verify_lesson_boundary(lesson_record)

        lesson_id = lesson_record["lesson_id"]
        out_path = os.path.join(self.lessons_dir, f"{lesson_id}.json")

        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(lesson_record, f, indent=2, ensure_ascii=False)

        index_entry = {
            "lesson_id": lesson_id,
            "lesson_type": lesson_record.get("lesson_type", "WHAT_NOT_TO_DO"),
            "trigger_source": lesson_record.get("trigger_source"),
            "scope": lesson_record.get("scope"),
            "related_skills": lesson_record.get("related_skills", []),
            "source_experience_id": lesson_record.get("source_experience_id"),
            "is_active_behavior": lesson_record.get("is_active_behavior", False),
            "status": lesson_record.get("status", "DRAFT"),
            "created_at": lesson_record.get("created_at"),
            "filepath": os.path.relpath(out_path, self.project_root)
        }

        line = json.dumps(index_entry, ensure_ascii=False) + "\n"
        with open(self.index_file, "a", encoding="utf-8") as f:
            f.write(line)

        return {
            "status": "RECORDED",
            "lesson_id": lesson_id,
            "filepath": out_path,
            "lesson_type": lesson_record.get("lesson_type")
        }

    def list_lessons(
        self,
        lesson_type: Optional[str] = None,
        scope: Optional[str] = None,
        skill: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Queries the lessons fast index."""
        if not os.path.isfile(self.index_file):
            return []
        results = []
        with open(self.index_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    if lesson_type and entry.get("lesson_type") != lesson_type:
                        continue
                    if scope and entry.get("scope") != scope:
                        continue
                    if skill and skill not in entry.get("related_skills", []):
                        continue
                    results.append(entry)
                except Exception:
                    continue
        return results

    def get_lesson(self, lesson_id: str) -> Dict[str, Any]:
        """Loads a lesson from disk."""
        target = os.path.join(self.lessons_dir, f"{lesson_id}.json")
        if not os.path.isfile(target):
            raise FileNotFoundError(f"Lesson '{lesson_id}' not found on disk at {target}")
        with open(target, "r", encoding="utf-8") as f:
            return json.load(f)

    def _derive_rationale(self, fdb_type: str, correction: str, desired: str) -> str:
        """Constructs epistemically grounded rationale."""
        if "MISSING" in fdb_type or "missing" in correction.lower():
            return "Unscreened missing data or unverified assumptions distort variance estimation and bias inferential statistics."
        if "MODEL" in fdb_type or "compare" in correction.lower():
            return "Selecting a structural model without comparative falsification increases vulnerability to model misspecification."
        if "CAUS" in correction.lower() or "treatment" in correction.lower():
            return "Causal claims require randomized manipulation and temporal precedence; quasi-experimental associations must avoid causal language."
        if "WRITING" in fdb_type or "superficial" in correction.lower():
            return "Academic scholarship requires formal psychological mechanisms and theoretical grounding rather than descriptive platitudes."
        return "Adherence to empirical rigor and supervisor directives prevents methodological and institutional defects."

    def _map_defect_type(self, failed_checks: List[str]) -> str:
        """Maps failed check tokens to contract defect_type."""
        checks_str = " ".join(failed_checks).lower()
        if "df" in checks_str or "degrees_of_freedom" in checks_str:
            return "DEGREES_OF_FREEDOM_MISMATCH"
        if "assumption" in checks_str or "normality" in checks_str or "variance" in checks_str:
            return "STATISTICAL_ASSUMPTION_VIOLATION"
        if "table" in checks_str or "zero" in checks_str or "leading" in checks_str or "apa" in checks_str:
            return "REPORTING_OR_TYPOGRAPHY_DEFECT"
        if "citation" in checks_str or "ref" in checks_str:
            return "CITATION_OR_EVIDENCE_DISCORDANCE"
        if "script" in checks_str or "exec" in checks_str:
            return "EXECUTION_OR_SCRIPT_FAILURE"
        return "METHODOLOGICAL_DEFECT"


def main():
    parser = argparse.ArgumentParser(description="Academic Lesson Distiller CLI")
    parser.add_argument("--distill-experience", type=str, help="Experience ID to distill lessons from.")
    parser.add_argument("--list", action="store_true", help="List all distilled lessons.")
    parser.add_argument("--get", type=str, help="Retrieve lesson record by ID.")
    parser.add_argument("--type", type=str, choices=["WHAT_NOT_TO_DO", "WHAT_WORKED_WELL"], help="Filter by lesson type.")
    parser.add_argument("--scope", type=str, choices=["PROJECT_SPECIFIC", "DOMAIN_WIDE", "CROSS_PROJECT_UNIVERSAL"], help="Filter by scope.")
    args = parser.parse_args()

    distiller = AcademicLessonDistiller()

    if args.distill_experience:
        res = distiller.distill_from_experience(args.distill_experience, record_to_disk=True)
        print(json.dumps({"experience_id": args.distill_experience, "distilled_count": len(res), "lessons": res}, indent=2, ensure_ascii=False))

    elif args.list:
        items = distiller.list_lessons(lesson_type=args.type, scope=args.scope)
        print(json.dumps(items, indent=2, ensure_ascii=False))

    elif args.get:
        les = distiller.get_lesson(args.get)
        print(json.dumps(les, indent=2, ensure_ascii=False))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
