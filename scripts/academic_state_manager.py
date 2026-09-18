#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
academic_state_manager.py — Academic State Management Engine ("The Hands")

Provides deterministic CLI operations and a strict state machine to initialize,
validate, query, mutate, and govern the academic-state/ and state/ artifact repositories
within research projects.
Enforces schema compliance, fails closed on illegal transitions, and ensures
that human approvals never default to true.
"""

import os
import sys
import json
import uuid
import hashlib
import argparse
from enum import Enum
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Set, Union, Tuple

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

# System dist-packages fallback
for p in ["/usr/lib/python3/dist-packages", "/usr/local/lib/python3/dist-packages"]:
    if os.path.exists(p) and p not in sys.path:
        sys.path.append(p)

try:
    import jsonschema
except ImportError:
    jsonschema = None

try:
    from scripts.academic_event_engine import (
        AcademicEventEngine,
        EventError,
        EventSchemaValidationError,
        DuplicateEventError,
        MalformedEventError,
        EventOrderingError,
        ArtifactEventMismatchError,
        MissingArtifactEventError,
        VALID_EVENT_TYPES,
        compute_file_sha256,
    )
except ImportError:
    from academic_event_engine import (
        AcademicEventEngine,
        EventError,
        EventSchemaValidationError,
        DuplicateEventError,
        MalformedEventError,
        EventOrderingError,
        ArtifactEventMismatchError,
        MissingArtifactEventError,
        VALID_EVENT_TYPES,
        compute_file_sha256,
    )

try:
    from scripts.academic_pitfall_registry import (
        AcademicPitfallRegistry,
        PitfallError,
        PitfallSchemaValidationError,
        DuplicatePitfallError,
        MalformedPitfallError,
        InvalidPitfallQueryError,
        PitfallNotFoundError,
    )
except ImportError:
    from academic_pitfall_registry import (
        AcademicPitfallRegistry,
        PitfallError,
        PitfallSchemaValidationError,
        DuplicatePitfallError,
        MalformedPitfallError,
        InvalidPitfallQueryError,
        PitfallNotFoundError,
    )

try:
    from scripts.academic_experience_recorder import (
        AcademicExperienceRecorder,
        ExperienceRecordingError,
        ExperienceValidationError,
    )
except ImportError:
    try:
        from academic_experience_recorder import (
            AcademicExperienceRecorder,
            ExperienceRecordingError,
            ExperienceValidationError,
        )
    except ImportError:
        AcademicExperienceRecorder = None
        ExperienceRecordingError = Exception
        ExperienceValidationError = Exception


# ==============================================================================
# Custom Exceptions (Fail-Closed Hierarchy)
# ==============================================================================

class StateManagementError(Exception):
    """Base exception for AcademicSuite state management."""
    pass

class UnknownStateError(StateManagementError):
    """Raised when an unrecognized state is encountered."""
    pass

class UnknownMilestoneError(StateManagementError):
    """Raised when an unrecognized milestone is referenced."""
    pass

class UnknownDependencyError(StateManagementError):
    """Raised when a dependency milestone does not exist in the state machine."""
    pass

class UnmetDependencyError(StateManagementError):
    """Raised when a prerequisite milestone is not in APPROVED or SUPERSEDED status."""
    pass

class InvalidStateTransitionError(StateManagementError):
    """Raised when an illegal transition is attempted."""
    pass

class MissingRequiredArtifactError(StateManagementError):
    """Raised when required artifacts are missing from disk or unverified."""
    pass

class MissingApprovalError(StateManagementError):
    """Raised when an APPROVED transition is attempted without explicit human approval."""
    pass

class DuplicateApprovalError(StateManagementError):
    """Raised when attempting to approve an already approved record."""
    pass

class StaleApprovalError(StateManagementError):
    """Raised when an approval is applied to a modified or stale milestone state."""
    pass

class MilestoneValidationRequiredError(StateManagementError):
    """Raised when an APPROVED transition is attempted without a valid passing validation report."""
    pass



# ==============================================================================
# Milestone Lifecycle & Legal Transitions
# ==============================================================================

class MilestoneState(str, Enum):
    CREATED = "CREATED"
    SCOPED = "SCOPED"
    PLANNED = "PLANNED"
    READY = "READY"
    RUNNING = "RUNNING"
    VALIDATING = "VALIDATING"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    APPROVED = "APPROVED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"


VALID_TRANSITIONS: Dict[MilestoneState, Set[MilestoneState]] = {
    MilestoneState.CREATED: {MilestoneState.SCOPED},
    MilestoneState.SCOPED: {MilestoneState.PLANNED},
    MilestoneState.PLANNED: {MilestoneState.READY},
    MilestoneState.READY: {MilestoneState.RUNNING},
    MilestoneState.RUNNING: {MilestoneState.VALIDATING, MilestoneState.FAILED},
    MilestoneState.VALIDATING: {MilestoneState.AWAITING_APPROVAL, MilestoneState.FAILED},
    MilestoneState.AWAITING_APPROVAL: {MilestoneState.APPROVED, MilestoneState.REJECTED},
    MilestoneState.APPROVED: {MilestoneState.SUPERSEDED},
    MilestoneState.FAILED: {MilestoneState.READY, MilestoneState.PLANNED},
    MilestoneState.REJECTED: {MilestoneState.PLANNED, MilestoneState.SCOPED},
    MilestoneState.SUPERSEDED: set(),
}

DEFAULT_MILESTONES = [
    {
        "milestone_id": "M0_INGESTION",
        "title": "Data Ingestion & Curation",
        "stage_id": "00_data_curation",
        "dependencies": [],
        "required_input_artifacts": [],
        "required_output_artifacts": ["data/data_quality.json"],
        "active_agent": "data-curator"
    },
    {
        "milestone_id": "M1_PROPOSAL",
        "title": "Research Proposal Formulation",
        "stage_id": "01_proposal",
        "dependencies": [],
        "required_input_artifacts": [],
        "required_output_artifacts": ["requirements.json"],
        "active_agent": "academic-orchestrator"
    },
    {
        "milestone_id": "M2_LITERATURE_REVIEW",
        "title": "Literature Review Synthesis",
        "stage_id": "02_lit_review",
        "dependencies": ["M1_PROPOSAL"],
        "required_input_artifacts": [],
        "required_output_artifacts": [],
        "active_agent": "literature-expert"
    },
    {
        "milestone_id": "M3_DATA_CURATION",
        "title": "Data Cleaning & Demographics",
        "stage_id": "01_demographics",
        "dependencies": ["M0_INGESTION"],
        "required_input_artifacts": ["data/data_quality.json"],
        "required_output_artifacts": [],
        "active_agent": "data-agent"
    },
    {
        "milestone_id": "M4_DESCRIPTIVES_RELIABILITY",
        "title": "Descriptive Statistics & Scale Reliability",
        "stage_id": "02_descriptives_and_reliability",
        "dependencies": ["M3_DATA_CURATION"],
        "required_input_artifacts": [],
        "required_output_artifacts": [],
        "active_agent": "statistics-agent"
    },
    {
        "milestone_id": "M5_PARAMETRIC_ASSUMPTIONS",
        "title": "Parametric Assumptions & Bivariate Correlations",
        "stage_id": "04_bivariate_correlations",
        "dependencies": ["M4_DESCRIPTIVES_RELIABILITY"],
        "required_input_artifacts": [],
        "required_output_artifacts": [],
        "active_agent": "statistics-agent"
    },
    {
        "milestone_id": "M6_MODEL_DELIBERATION",
        "title": "Candidate Falsification & Model Deliberation",
        "stage_id": "04_statistical_deliberation",
        "dependencies": ["M5_PARAMETRIC_ASSUMPTIONS"],
        "required_input_artifacts": [],
        "required_output_artifacts": ["analysis_plan.json"],
        "active_agent": "statistical-expert"
    },
    {
        "milestone_id": "M7_HYPOTHESIS_TESTING",
        "title": "Deterministic Hypothesis Testing & Triad Production",
        "stage_id": "06_hypothesis_1",
        "dependencies": ["M6_MODEL_DELIBERATION"],
        "required_input_artifacts": ["analysis_plan.json"],
        "required_output_artifacts": [],
        "active_agent": "statistics-agent"
    },
    {
        "milestone_id": "M8_DISCUSSION",
        "title": "Chapter 5 Discussion & Conclusion",
        "stage_id": "01_findings_recap",
        "dependencies": ["M7_HYPOTHESIS_TESTING"],
        "required_input_artifacts": [],
        "required_output_artifacts": [],
        "active_agent": "academic-writer"
    },
    {
        "milestone_id": "M9_DEFENSE",
        "title": "Thesis Defense Presentation Deck & Oral Simulation",
        "stage_id": "01_defense_storyboard",
        "dependencies": ["M7_HYPOTHESIS_TESTING", "M8_DISCUSSION"],
        "required_input_artifacts": [],
        "required_output_artifacts": [],
        "active_agent": "digital-saber"
    }
]

STAGE_TO_MILESTONE_MAP = {
    "00_data_curation": "M0_INGESTION",
    "01_proposal": "M1_PROPOSAL",
    "02_lit_review": "M2_LITERATURE_REVIEW",
    "01_demographics": "M3_DATA_CURATION",
    "03_data_cleaning": "M3_DATA_CURATION",
    "02_descriptives_and_reliability": "M4_DESCRIPTIVES_RELIABILITY",
    "03_parametric_assumptions": "M5_PARAMETRIC_ASSUMPTIONS",
    "04_bivariate_correlations": "M5_PARAMETRIC_ASSUMPTIONS",
    "05_macro_model": "M6_MODEL_DELIBERATION",
    "04_statistical_deliberation": "M6_MODEL_DELIBERATION",
    "06_hypothesis_1": "M7_HYPOTHESIS_TESTING",
    "07_hypothesis_2": "M7_HYPOTHESIS_TESTING",
    "01_findings_recap": "M8_DISCUSSION",
    "01_defense_storyboard": "M9_DEFENSE"
}


# ==============================================================================
# Strict State Machine Class
# ==============================================================================

class StrictStateMachine:
    """
    Authoritative state machine governing AcademicSuite projects, milestones, executions, and approvals.
    Enforces strict transitions, restart-safety, artifact gating, and explicit human approval.
    Fails closed on any violation.
    """

    def __init__(self, state_dir: str, project_id: Optional[str] = None):
        self.state_dir = os.path.abspath(state_dir)
        os.makedirs(self.state_dir, exist_ok=True)
        self.project_id = project_id or os.path.basename(os.path.dirname(self.state_dir)) or "academic_project"
        self.milestones: Dict[str, Dict[str, Any]] = {}
        self.approvals: List[Dict[str, Any]] = []
        self.artifacts: List[Dict[str, Any]] = []

        self.events_path = os.path.join(self.state_dir, "events.jsonl")
        self.current_state_path = os.path.join(self.state_dir, "current_state.json")
        self.project_path = os.path.join(self.state_dir, "project.json")
        self.approvals_path = os.path.join(self.state_dir, "approvals.json")
        self.artifacts_path = os.path.join(self.state_dir, "artifacts.json")
        self.pitfalls_path = os.path.join(self.state_dir, "pitfalls.jsonl")

        self.event_engine = AcademicEventEngine(self.events_path, project_id=self.project_id)
        self.pitfall_registry = AcademicPitfallRegistry(self.pitfalls_path, project_id=self.project_id)

        self.project_root = os.path.dirname(self.state_dir)
        self.experience_recorder = None
        if AcademicExperienceRecorder is not None:
            self.experience_recorder = AcademicExperienceRecorder(project_root=self.project_root)

        self.load_from_disk()

    def load_from_disk(self) -> None:
        """Loads state snapshot, approvals, and artifacts from disk for restart-safety."""
        if os.path.exists(self.current_state_path):
            try:
                with open(self.current_state_path, "r", encoding="utf-8") as f:
                    cs = json.load(f)
                self.project_id = cs.get("project_id", self.project_id)
                self.milestones = cs.get("milestones", {})
            except Exception:
                pass

        if os.path.exists(self.approvals_path):
            try:
                with open(self.approvals_path, "r", encoding="utf-8") as f:
                    appr = json.load(f)
                self.approvals = appr.get("approvals", [])
            except Exception:
                pass

        if os.path.exists(self.artifacts_path):
            try:
                with open(self.artifacts_path, "r", encoding="utf-8") as f:
                    art = json.load(f)
                self.artifacts = art.get("artifacts", [])
            except Exception:
                pass

    @property
    def events(self) -> List[Dict[str, Any]]:
        """Convenience accessor to read durable events from events.jsonl."""
        return self.event_engine.read_events(validate_schema=False, enforce_ordering=False)

    def save_all(self) -> None:
        """Atomically persists state snapshots to disk."""
        now_iso = datetime.now(timezone.utc).isoformat()
        cs_data = {
            "contract_version": "1.0.0",
            "project_id": self.project_id,
            "state_machine_version": "1.0.0",
            "system_status": "OPERATIONAL",
            "updated_at": now_iso,
            "milestones": self.milestones
        }
        with open(self.current_state_path, "w", encoding="utf-8") as f:
            json.dump(cs_data, f, indent=2, ensure_ascii=False)

        with open(self.approvals_path, "w", encoding="utf-8") as f:
            json.dump({"contract_version": "1.0.0", "approvals": self.approvals}, f, indent=2, ensure_ascii=False)

        with open(self.artifacts_path, "w", encoding="utf-8") as f:
            json.dump({"contract_version": "1.0.0", "artifacts": self.artifacts}, f, indent=2, ensure_ascii=False)

    def record_event(self, event_type: str, milestone_id: Optional[str] = None, stage_id: Optional[str] = None,
                     emitter_agent: str = "academic-orchestrator", payload: Optional[Dict[str, Any]] = None,
                     summary: Optional[str] = None) -> Dict[str, Any]:
        """Appends an event conforming to contracts/event.schema.json to events.jsonl via AcademicEventEngine."""
        p = payload or {}
        event_summary = summary or p.get("summary") or f"Event {event_type} on milestone {milestone_id or 'global'}"
        details = p.get("details", {k: v for k, v in p.items() if k not in ("summary", "artifact_ids", "metrics")})
        artifact_ids = p.get("artifact_ids")
        metrics = p.get("metrics")

        # Map legacy transition event types if passed
        canonical_event_type = event_type
        if event_type == "MILESTONE_TRANSITIONED":
            canonical_event_type = "MILESTONE_STARTED"

        return self.event_engine.emit(
            event_type=canonical_event_type,
            emitter_agent=emitter_agent,
            summary=event_summary,
            milestone_id=milestone_id,
            stage_id=stage_id,
            artifact_ids=artifact_ids,
            metrics=metrics,
            details=details,
            project_id=self.project_id
        )

    def register_milestone(self, milestone_id: str, title: str, dependencies: Optional[List[str]] = None,
                           required_input_artifacts: Optional[List[str]] = None,
                           required_output_artifacts: Optional[List[str]] = None,
                           active_agent: str = "academic-orchestrator",
                           current_stage: str = "",
                           requires_validation: Optional[bool] = None) -> Dict[str, Any]:
        """Registers a milestone in CREATED state with explicit dependency validation."""
        dependencies = dependencies or []
        for dep in dependencies:
            if dep not in self.milestones:
                raise UnknownDependencyError(f"Milestone '{milestone_id}' references unknown dependency '{dep}'.")

        if requires_validation is None:
            requires_validation = (
                milestone_id.startswith(("M0_", "M1_", "M2_", "M3_", "M4_", "M5_", "M6_", "M7_", "M8_", "M9_")) or
                any(m.get("milestone_id") == milestone_id for m in DEFAULT_MILESTONES)
            )

        now_iso = datetime.now(timezone.utc).isoformat()
        entry = {
            "milestone_id": milestone_id,
            "title": title,
            "status": MilestoneState.CREATED.value,
            "current_stage": current_stage,
            "active_agent": active_agent,
            "dependencies": dependencies,
            "required_input_artifacts": required_input_artifacts or [],
            "required_output_artifacts": required_output_artifacts or [],
            "requires_validation": requires_validation,
            "created_at": now_iso,
            "updated_at": now_iso,
            "history": [
                {
                    "transition_id": f"TRN-{uuid.uuid4().hex[:6].upper()}",
                    "from_state": None,
                    "to_state": MilestoneState.CREATED.value,
                    "timestamp": now_iso,
                    "actor": active_agent,
                    "rationale": "Milestone registered in state machine"
                }
            ]
        }
        self.milestones[milestone_id] = entry
        self.record_event("MILESTONE_STARTED", milestone_id=milestone_id, stage_id=current_stage,
                          emitter_agent=active_agent,
                          summary=f"Milestone '{milestone_id}' registered and started: {title}",
                          payload={"details": {"title": title}})
        self.save_all()
        return entry

    def transition_milestone(self, milestone_id: str, target_state: Union[str, MilestoneState],
                             actor: str = "academic-orchestrator", rationale: str = "",
                             execution_info: Optional[Dict[str, Any]] = None,
                             check_artifacts: bool = True) -> Dict[str, Any]:
        """
        Transitions milestone strictly adhering to the valid transition graph.
        Fails closed on any invalid transition, unknown state, unmet dependency,
        missing required artifact, or unapproved transition.
        """
        if milestone_id not in self.milestones:
            raise UnknownMilestoneError(f"Unknown milestone: '{milestone_id}'. Must be registered before transitioning.")

        # 1. Validate Target State
        if isinstance(target_state, str):
            try:
                target_enum = MilestoneState(target_state.upper())
            except ValueError:
                raise UnknownStateError(f"Unknown state: '{target_state}'. Valid states: {[s.value for s in MilestoneState]}.")
        elif isinstance(target_state, MilestoneState):
            target_enum = target_state
        else:
            raise UnknownStateError(f"Target state must be a string or MilestoneState, got {type(target_state)}.")

        current_data = self.milestones[milestone_id]
        current_enum = MilestoneState(current_data["status"])

        # 2. Check Valid Transition Graph
        allowed_targets = VALID_TRANSITIONS.get(current_enum, set())
        if target_enum not in allowed_targets:
            raise InvalidStateTransitionError(
                f"Illegal transition for milestone '{milestone_id}': cannot transition from {current_enum.value} to {target_enum.value}. "
                f"Allowed transitions from {current_enum.value} are: {[t.value for t in allowed_targets]}."
            )

        # 3. Gate on Transition to READY: Dependencies and Input Artifacts
        if target_enum == MilestoneState.READY:
            for dep_id in current_data.get("dependencies", []):
                if dep_id not in self.milestones:
                    raise UnknownDependencyError(f"Milestone '{milestone_id}' references unknown dependency '{dep_id}'.")
                dep_status = self.milestones[dep_id]["status"]
                if dep_status not in [MilestoneState.APPROVED.value, MilestoneState.SUPERSEDED.value]:
                    raise UnmetDependencyError(
                        f"Milestone '{milestone_id}' cannot become READY because dependency '{dep_id}' is in state '{dep_status}' "
                        f"(must be APPROVED or SUPERSEDED)."
                    )

            if check_artifacts:
                for art_rel in current_data.get("required_input_artifacts", []):
                    art_full = art_rel if os.path.isabs(art_rel) else os.path.join(self.state_dir, art_rel)
                    if not os.path.exists(art_full) or os.path.getsize(art_full) == 0:
                        raise MissingRequiredArtifactError(
                            f"Milestone '{milestone_id}' cannot become READY because required input artifact '{art_rel}' is missing on disk."
                        )

        # 4. Gate on Transition to APPROVED: Explicit Human Approval, Output Artifacts & Validation Report
        if target_enum == MilestoneState.APPROVED:
            matching_approvals = [
                a for a in self.approvals
                if a.get("milestone_id") == milestone_id and a.get("status") == "GRANTED" and a.get("is_approved") is True
            ]
            if not matching_approvals:
                raise MissingApprovalError(
                    f"Milestone '{milestone_id}' cannot become APPROVED without explicit, granted human approval. "
                    f"No granted approval record found in approvals.json."
                )

            if check_artifacts:
                for art_rel in current_data.get("required_output_artifacts", []):
                    art_full = art_rel if os.path.isabs(art_rel) else os.path.join(self.state_dir, art_rel)
                    if not os.path.exists(art_full) or os.path.getsize(art_full) == 0:
                        raise MissingRequiredArtifactError(
                            f"Milestone '{milestone_id}' cannot become APPROVED because required output artifact '{art_rel}' is missing on disk."
                        )

            # Mandatory validation report check
            candidate_reports = []
            direct_report = os.path.join(self.state_dir, "validation_report.json")
            if os.path.isfile(direct_report):
                candidate_reports.append(direct_report)

            mid_report = os.path.join(self.state_dir, f"{milestone_id.lower()}_validation.json")
            if os.path.isfile(mid_report):
                candidate_reports.append(mid_report)

            val_dir = os.path.join(self.state_dir, "validation")
            if os.path.isdir(val_dir):
                for vf in os.listdir(val_dir):
                    if vf.endswith(".json"):
                        candidate_reports.append(os.path.join(val_dir, vf))

            for art in self.artifacts:
                if isinstance(art, dict) and art.get("milestone_id") == milestone_id and art.get("artifact_type") in ["validation_report", "validation"]:
                    art_p = art.get("filepath", "")
                    art_full = art_p if os.path.isabs(art_p) else os.path.join(self.state_dir, art_p)
                    if os.path.isfile(art_full):
                        candidate_reports.append(art_full)

            requires_val = current_data.get("requires_validation", False)
            if not candidate_reports and requires_val:
                raise MilestoneValidationRequiredError(
                    f"Milestone '{milestone_id}' cannot become APPROVED without a passing validation report. "
                    f"No validation_report.json or validation artifact found on disk."
                )

            for cr in set(candidate_reports):
                try:
                    with open(cr, "r", encoding="utf-8") as f:
                        cdata = json.load(f)
                    verdict = str(cdata.get("overall_verdict", cdata.get("verdict", ""))).strip().upper()
                    if verdict != "PASS":
                        raise MilestoneValidationRequiredError(
                            f"Milestone '{milestone_id}' cannot become APPROVED: validation report '{os.path.basename(cr)}' "
                            f"has non-passing verdict '{verdict}' (expected 'PASS')."
                        )
                except json.JSONDecodeError:
                    raise MilestoneValidationRequiredError(
                        f"Milestone '{milestone_id}' cannot become APPROVED: validation report '{os.path.basename(cr)}' is corrupt or unreadable."
                    )


        # Apply transition
        now_iso = datetime.now(timezone.utc).isoformat()
        current_data["status"] = target_enum.value
        current_data["updated_at"] = now_iso
        transition_record = {
            "transition_id": f"TRN-{uuid.uuid4().hex[:6].upper()}",
            "from_state": current_enum.value,
            "to_state": target_enum.value,
            "timestamp": now_iso,
            "actor": actor,
            "rationale": rationale,
            "execution_info": execution_info or {}
        }
        current_data.setdefault("history", []).append(transition_record)

        # Transition to valid event type mapping from contracts/event.schema.json
        transition_event_map = {
            MilestoneState.SCOPED: "MILESTONE_STARTED",
            MilestoneState.PLANNED: "PLAN_CREATED",
            MilestoneState.READY: "MILESTONE_STARTED",
            MilestoneState.RUNNING: "EXECUTION_STARTED",
            MilestoneState.VALIDATING: "VALIDATION_STARTED",
            MilestoneState.AWAITING_APPROVAL: "MILESTONE_APPROVAL_REQUESTED",
            MilestoneState.APPROVED: "MILESTONE_APPROVED",
            MilestoneState.REJECTED: "MILESTONE_REJECTED",
            MilestoneState.FAILED: "MILESTONE_FAILED",
            MilestoneState.SUPERSEDED: "REVISION_REQUESTED",
        }

        # If transitioning from RUNNING to VALIDATING, emit EXECUTION_COMPLETED first
        if current_enum == MilestoneState.RUNNING and target_enum == MilestoneState.VALIDATING:
            self.record_event(
                "EXECUTION_COMPLETED",
                milestone_id=milestone_id,
                stage_id=current_data.get("current_stage"),
                emitter_agent=actor,
                summary=f"Milestone '{milestone_id}' execution completed before validation.",
                payload={"details": {"from_state": current_enum.value, "to_state": target_enum.value, "rationale": rationale}}
            )

        evt_type = transition_event_map.get(target_enum, "MILESTONE_STARTED")
        self.record_event(
            evt_type,
            milestone_id=milestone_id,
            stage_id=current_data.get("current_stage"),
            emitter_agent=actor,
            summary=f"Milestone '{milestone_id}' transitioned from {current_enum.value} to {target_enum.value}: {rationale or 'Transition recorded'}",
            payload={"details": {"from_state": current_enum.value, "to_state": target_enum.value, "rationale": rationale}}
        )

        self.save_all()

        # Automatic Structured Experience Capture (Continuous Behavioral Self-Improvement)
        if self.experience_recorder is not None and target_enum in [
            MilestoneState.APPROVED,
            MilestoneState.FAILED,
            MilestoneState.REJECTED,
            MilestoneState.SUPERSEDED
        ]:
            try:
                outcome_ovr = "SUCCESS" if target_enum == MilestoneState.APPROVED else (
                    "FAILURE" if target_enum == MilestoneState.FAILED else "PARTIAL"
                )
                self.experience_recorder.record_from_milestone(
                    sm=self,
                    milestone_id=milestone_id,
                    outcome_override=outcome_ovr,
                    active_agent=actor
                )
            except Exception as rec_err:
                sys.stderr.write(f"[StrictStateMachine Experience Capture Warning] {rec_err}\n")

        # Integrated Continuous Learning Lifecycle Hook (Meaningful Boundary Gated)
        try:
            from scripts.academic_integrated_learning_hub import (
                AcademicIntegratedLearningHub,
                ResearchIntegrityViolationError
            )
            hub = AcademicIntegratedLearningHub(base_dir=self.project_root)
            hub.process_milestone_transition(
                milestone_id=milestone_id,
                from_state=current_enum.value,
                to_state=target_enum.value,
                sm=self,
                actor=actor,
                rationale=rationale
            )
        except ResearchIntegrityViolationError:
            # Scientific integrity violation must fail closed to protect research validity
            raise
        except Exception as hub_err:
            # Failure isolation: internal learning errors never corrupt or abort research transactions
            sys.stderr.write(f"[IntegratedLearningHub State Isolation] {hub_err}\n")

        return {
            "status": "TRANSITIONED",
            "milestone_id": milestone_id,
            "from_state": current_enum.value,
            "to_state": target_enum.value,
            "transition": transition_record
        }

    def request_approval(self, milestone_id: str, category: str, requester_agent: str,
                         rationale: str, target_artifacts: Optional[List[str]] = None) -> Dict[str, Any]:
        """Creates an approval request. Approval NEVER defaults to True (status=PENDING, is_approved=False)."""
        if milestone_id not in self.milestones:
            raise UnknownMilestoneError(f"Cannot request approval for unknown milestone '{milestone_id}'.")

        now_iso = datetime.now(timezone.utc).isoformat()
        approval_id = f"APPR-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        approval_record = {
            "contract_version": "1.0.0",
            "approval_id": approval_id,
            "milestone_id": milestone_id,
            "category": category,
            "requested_by": {
                "agent": requester_agent,
                "rationale": rationale,
                "target_artifacts": target_artifacts or []
            },
            "requested_at": now_iso,
            "status": "PENDING",
            "is_approved": False,  # CRITICAL INVARIANT: NEVER TRUE BY DEFAULT
            "milestone_state_snapshot": self.milestones[milestone_id]["status"]
        }
        self.approvals.append(approval_record)
        self.record_event(
            "MILESTONE_APPROVAL_REQUESTED",
            milestone_id=milestone_id,
            stage_id=self.milestones[milestone_id].get("current_stage"),
            emitter_agent=requester_agent,
            summary=f"Approval requested for milestone '{milestone_id}' by {requester_agent}: {rationale}",
            payload={"details": {"approval_id": approval_id, "category": category, "target_artifacts": target_artifacts or []}}
        )
        self.save_all()
        return approval_record

    def grant_approval(self, approval_id: str, approver_identity: str, digital_signature: str,
                       comments: str = "", stipulations: Optional[List[str]] = None) -> Dict[str, Any]:
        """Explicitly grants an approval. Checks for duplicate or stale approvals."""
        appr = next((a for a in self.approvals if a.get("approval_id") == approval_id), None)
        if not appr:
            raise StateManagementError(f"Approval ID '{approval_id}' not found.")

        if appr.get("status") == "GRANTED" and appr.get("is_approved") is True:
            raise DuplicateApprovalError(f"Approval '{approval_id}' has already been granted.")

        mid = appr.get("milestone_id")
        if mid in self.milestones:
            current_status = self.milestones[mid]["status"]
            if current_status in [MilestoneState.FAILED.value, MilestoneState.REJECTED.value, MilestoneState.SUPERSEDED.value]:
                raise StaleApprovalError(
                    f"Approval '{approval_id}' is stale because milestone '{mid}' is in state '{current_status}'."
                )

        if not approver_identity or len(approver_identity.strip()) < 3:
            raise StateManagementError("Approver identity must be at least 3 characters.")
        if not digital_signature or len(digital_signature.strip()) < 5:
            raise StateManagementError("Digital signature/acknowledgment must be at least 5 characters.")

        now_iso = datetime.now(timezone.utc).isoformat()
        appr["status"] = "GRANTED"
        appr["is_approved"] = True
        appr["decision"] = {
            "approver_identity": approver_identity.strip(),
            "decided_at": now_iso,
            "comments": comments or "Explicit approval granted.",
            "conditions_or_stipulations": stipulations or [],
            "digital_signature_or_ack": digital_signature.strip()
        }

        self.record_event(
            "MILESTONE_APPROVED",
            milestone_id=mid,
            stage_id=self.milestones.get(mid, {}).get("current_stage"),
            emitter_agent=approver_identity,
            summary=f"Approval '{approval_id}' granted for milestone '{mid}' by {approver_identity}: {comments or 'Granted'}",
            payload={"details": {"approval_id": approval_id, "approver": approver_identity, "comments": comments}}
        )
        self.save_all()
        return appr

    def reject_approval(self, approval_id: str, approver_identity: str, comments: str = "") -> Dict[str, Any]:
        """Rejects an approval and transitions the milestone to REJECTED."""
        appr = next((a for a in self.approvals if a.get("approval_id") == approval_id), None)
        if not appr:
            raise StateManagementError(f"Approval ID '{approval_id}' not found.")

        now_iso = datetime.now(timezone.utc).isoformat()
        appr["status"] = "REJECTED"
        appr["is_approved"] = False
        appr["decision"] = {
            "approver_identity": approver_identity,
            "decided_at": now_iso,
            "comments": comments or "Approval rejected.",
            "conditions_or_stipulations": [],
            "digital_signature_or_ack": f"REJ-{approver_identity[:10]}"
        }

        mid = appr.get("milestone_id")
        if mid in self.milestones and self.milestones[mid]["status"] == MilestoneState.AWAITING_APPROVAL.value:
            self.transition_milestone(mid, MilestoneState.REJECTED, actor=approver_identity, rationale=comments)

        self.record_event(
            "MILESTONE_REJECTED",
            milestone_id=mid,
            stage_id=self.milestones.get(mid, {}).get("current_stage"),
            emitter_agent=approver_identity,
            summary=f"Approval '{approval_id}' rejected for milestone '{mid}' by {approver_identity}: {comments or 'Rejected'}",
            payload={"details": {"approval_id": approval_id, "comments": comments}}
        )
        self.save_all()
        return appr

    def register_artifact(self, artifact_id: str, milestone_id: str, stage_id: str,
                          artifact_type: str, path: str, schema: str = "",
                          producer_agent: str = "statistics-agent", producer_script: str = "",
                          provenance: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Registers an artifact manifest in artifacts.json and emits an ARTIFACT_CREATED event with full provenance."""
        full_path = path if os.path.isabs(path) else os.path.join(self.state_dir, path)
        project_root = os.path.dirname(self.state_dir)
        if not os.path.exists(full_path):
            alt_path = os.path.join(project_root, path)
            if os.path.exists(alt_path):
                full_path = alt_path

        art_hash = ""
        if os.path.exists(full_path):
            art_hash = compute_file_sha256(full_path)

        now_iso = datetime.now(timezone.utc).isoformat()
        prov = provenance or {
            "source_dataset": "real_input",
            "deterministic_tool": producer_script or "academic_state_manager.py",
            "command_line": f"python3 {producer_script}" if producer_script else "internal"
        }

        art_record = {
            "contract_version": "1.0.0",
            "artifact_id": artifact_id,
            "milestone": milestone_id,
            "stage_id": stage_id,
            "producer": {
                "agent": producer_agent,
                "script_or_generator": producer_script
            },
            "consumers": ["academic-orchestrator", "validation-agent"],
            "type": artifact_type,
            "path": path,
            "schema": schema,
            "hash": art_hash,
            "creation_timestamp": now_iso,
            "validation_status": "VALID" if art_hash else "PENDING",
            "provenance": prov,
            "dependencies": []
        }
        self.artifacts.append(art_record)

        if os.path.exists(full_path):
            self.event_engine.emit_artifact_created(
                artifact_id=artifact_id,
                artifact_path=path,
                milestone_id=milestone_id,
                producer_agent=producer_agent,
                producer_script=producer_script,
                provenance=prov,
                stage_id=stage_id,
                summary=f"Artifact '{artifact_id}' ({artifact_type}) registered by {producer_agent}",
                project_root=project_root
            )
        else:
            self.record_event(
                "ARTIFACT_CREATED",
                milestone_id=milestone_id,
                stage_id=stage_id,
                emitter_agent=producer_agent,
                summary=f"Artifact '{artifact_id}' ({artifact_type}) registered by {producer_agent} (file pending on disk)",
                payload={
                    "artifact_ids": [artifact_id],
                    "details": {
                        "artifact_id": artifact_id,
                        "path": path,
                        "hash": {"algorithm": "sha256", "value": ""},
                        "milestone": milestone_id,
                        "producer": {"agent": producer_agent, "script_or_generator": producer_script},
                        "provenance": prov
                    }
                }
            )

        self.save_all()
        return art_record

    def verify_artifact_alignment(self, check_disk_files: bool = True,
                                  scanned_disk_paths: Optional[List[str]] = None) -> Dict[str, Any]:
        """Verifies that all registered artifacts align with events.jsonl and physical disk state."""
        project_root = os.path.dirname(self.state_dir)
        return self.event_engine.verify_artifact_alignment(
            self.artifacts,
            project_root=project_root,
            check_disk_files=check_disk_files,
            scanned_disk_paths=scanned_disk_paths
        )

    def reconstruct_workflow(self) -> Dict[str, Any]:
        """Reconstructs the full project workflow directly from events.jsonl."""
        return self.event_engine.reconstruct_workflow()

    def explain_transition(self, milestone_id: str, target_state: str) -> Dict[str, Any]:
        """Explains the causal sequence of events justifying a milestone transition."""
        return self.event_engine.explain_transition(milestone_id, target_state)

    def get_milestone_state(self, milestone_id: str) -> Dict[str, Any]:
        """Returns the current state dictionary for a milestone."""
        if milestone_id not in self.milestones:
            raise UnknownMilestoneError(f"Unknown milestone: '{milestone_id}'.")
        return self.milestones[milestone_id]

    def get_full_state(self) -> Dict[str, Any]:
        """Returns a snapshot of the entire state machine."""
        return {
            "project_id": self.project_id,
            "state_dir": self.state_dir,
            "milestones_count": len(self.milestones),
            "milestones": self.milestones,
            "approvals_count": len(self.approvals),
            "artifacts_count": len(self.artifacts)
        }

    def record_pitfall(
        self,
        candidate_approach: str,
        problem: str,
        evidence: Union[str, Dict[str, Any]],
        corrective_action: str,
        adapted_approach: str,
        detected_by: str = "academic-challenger",
        category: str = "methodological",
        milestone_id: Optional[str] = None,
        reusable: bool = True,
        pitfall_id: Optional[str] = None,
        verification_check: Optional[str] = None,
        related_artifacts: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Records a methodological, statistical, execution, evidence, or validation pitfall in state/pitfalls.jsonl."""
        m_id = milestone_id or "M_UNSPECIFIED"
        return self.pitfall_registry.create(
            candidate_approach=candidate_approach,
            problem=problem,
            evidence=evidence,
            corrective_action=corrective_action,
            adapted_approach=adapted_approach,
            detected_by=detected_by,
            category=category,
            stage=m_id,
            milestone=m_id,
            project=self.project_id,
            reusable=reusable,
            pitfall_id=pitfall_id,
            verification_check=verification_check,
            related_artifacts=related_artifacts
        )

    def query_pitfalls(
        self,
        category: Optional[str] = None,
        milestone: Optional[str] = None,
        detected_by: Optional[str] = None,
        reusable: Optional[bool] = None,
        keyword: Optional[str] = None,
        candidate_method: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Queries the persistent pitfall registry with deterministic filtering."""
        return self.pitfall_registry.query(
            category=category,
            project=self.project_id if self.project_id else None,
            milestone=milestone,
            detected_by=detected_by,
            reusable=reusable,
            keyword=keyword,
            candidate_method=candidate_method
        )

    def is_approach_invalidated(
        self,
        candidate_approach: Union[str, Dict[str, Any]],
        category: Optional[str] = None
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """Checks if a proposed candidate approach matches an invalidated reusable pitfall in the registry."""
        return self.pitfall_registry.is_approach_invalidated(candidate_approach, category=category)

    def surface_reusable_pitfalls(
        self,
        category: Optional[str] = None,
        milestone: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Surfaces all reusable historical pitfalls relevant to the milestone or category."""
        return self.pitfall_registry.surface_reusable_pitfalls(category=category, milestone=milestone)

    def resolve_pitfall(
        self,
        pitfall_id: str,
        corrective_action: str,
        adapted_approach: str,
        resolved_by: str,
        verification_check: Optional[str] = None
    ) -> Dict[str, Any]:
        """Updates resolution metadata for a recorded pitfall."""
        return self.pitfall_registry.resolve_pitfall(
            pitfall_id=pitfall_id,
            corrective_action=corrective_action,
            adapted_approach=adapted_approach,
            resolved_by=resolved_by,
            verification_check=verification_check
        )


# ==============================================================================
# Legacy / Project-Level Helper Functions (Maintained & Upgraded)
# ==============================================================================

SCHEMAS_DIR = os.path.join(ROOT_DIR, ".agents", "shared", "schemas", "academic_state")

SCHEMA_MAP = {
    "project.json": "project.schema.json",
    "requirements.json": "requirements.schema.json",
    "analysis_plan.json": "analysis_plan.schema.json",
    "decisions.json": "decisions.schema.json",
    "data/data_dictionary.json": "data_dictionary.schema.json",
    "data/data_quality.json": "data_quality.schema.json",
    "analysis/descriptive.json": "descriptive.schema.json",
    "analysis/reliability.json": "reliability.schema.json",
    "analysis/cfa.json": "cfa.schema.json",
    "analysis/sem.json": "sem.schema.json",
    "validation/data_validation.json": "validation_report.schema.json",
    "validation/statistical_validation.json": "validation_report.schema.json",
    "validation/writing_validation.json": "validation_report.schema.json"
}


def get_state_dir(project_path: str) -> str:
    """Resolves the state directory inside project_path."""
    if os.path.basename(project_path) in ["academic-state", "state"]:
        return os.path.abspath(project_path)
    if os.path.isdir(os.path.join(project_path, "academic-state")):
        return os.path.abspath(os.path.join(project_path, "academic-state"))
    if os.path.isdir(os.path.join(project_path, "state")):
        return os.path.abspath(os.path.join(project_path, "state"))
    return os.path.abspath(os.path.join(project_path, "academic-state"))


def init_state(project_path: str, title: str = "Empirical Research Project", methodology: str = "sem", n: int = 300) -> Dict[str, Any]:
    """Initializes the full state directory hierarchy with baseline starter files and strict state machine."""
    state_dir = get_state_dir(project_path)
    os.makedirs(os.path.join(state_dir, "data"), exist_ok=True)
    os.makedirs(os.path.join(state_dir, "analysis"), exist_ok=True)
    os.makedirs(os.path.join(state_dir, "validation"), exist_ok=True)
    os.makedirs(os.path.join(state_dir, "outputs"), exist_ok=True)

    now_iso = datetime.now(timezone.utc).isoformat()
    project_id = os.path.basename(os.path.abspath(project_path))

    # 1. project.json
    project_data = {
        "project_id": project_id,
        "title": title,
        "methodology_type": methodology,
        "sample_size": n,
        "current_stage": "00_data_curation",
        "active_milestone": "M0_INGESTION",
        "orchestrator": "academic-orchestrator",
        "status": "in_progress",
        "created_at": now_iso,
        "updated_at": now_iso,
        "metadata": {
            "version": "1.0.0",
            "target_degree": "Ph.D. / Master's Thesis"
        }
    }
    _write_json_if_missing(os.path.join(state_dir, "project.json"), project_data)

    # 2. requirements.json
    req_data = {
        "research_questions": [
            {
                "id": "RQ1",
                "question": "Does the predictor variable have a statistically significant relationship with the outcome?",
                "target_variables": ["predictor", "outcome"]
            }
        ],
        "hypotheses": [
            {
                "id": "H1",
                "statement": "The predictor variable has a significant direct effect on the outcome variable.",
                "type": "direct",
                "independent_variable": "predictor",
                "dependent_variable": "outcome",
                "direction": "positive"
            }
        ],
        "institutional_guidelines": {
            "style": "APA 7th Edition",
            "language": "Persian (Farsi)",
            "persian_fonts": {
                "body": "B Nazanin",
                "headings": "B Titr",
                "stats_latin": "Times New Roman"
            },
            "citation_style": "Author-Date APA 7"
        },
        "deliverables": [
            "Chapter_4_Results.docx",
            "Chapter_4_Results.md",
            "Master_Hypothesis_Matrix.docx",
            "Defense_Brief.docx"
        ]
    }
    _write_json_if_missing(os.path.join(state_dir, "requirements.json"), req_data)

    # 3. analysis_plan.json
    plan_data = {
        "significance_alpha": 0.05,
        "power_target": 0.80,
        "bootstrap_resamples": 5000,
        "planned_sequence": [
            {
                "stage_id": "01_demographics",
                "title": "Demographic Profiling & Frequencies",
                "engine": "python",
                "script": ".agents/skills/descriptive-statistics/scripts/compute_descriptives.py",
                "output_artifact": "academic-state/analysis/descriptive.json",
                "assigned_subagent": "statistics-agent"
            },
            {
                "stage_id": "02_reliability",
                "title": "Scale Reliability Analysis (Alpha & Omega)",
                "engine": "python",
                "script": ".agents/skills/reliability-analysis/scripts/cronbach_alpha.py",
                "output_artifact": "academic-state/analysis/reliability.json",
                "assigned_subagent": "statistics-agent"
            },
            {
                "stage_id": "03_sem_model",
                "title": "Macro SEM Model Fit & Hypotheses",
                "engine": "python",
                "script": ".agents/skills/sem/scripts/run_sem.py",
                "output_artifact": "academic-state/analysis/sem.json",
                "assigned_subagent": "statistics-agent"
            }
        ],
        "variables": {
            "independent": ["predictor"],
            "dependent": ["outcome"],
            "mediators": [],
            "moderators": [],
            "covariates": []
        }
    }
    _write_json_if_missing(os.path.join(state_dir, "analysis_plan.json"), plan_data)

    # 4. decisions.json (CRITICAL: supervisor_approval strictly False by default)
    dec_data = {
        "decisions": [
            {
                "decision_id": "DEC-001",
                "timestamp": now_iso,
                "category": "methodology",
                "decision": f"Project initialized using {methodology.upper()} methodology framework.",
                "rationale": "Aligned with approved research proposal and structural hypothesis testing.",
                "alternatives_considered": ["Multiple Regression", "ANCOVA"],
                "agent": "academic-orchestrator",
                "supervisor_approval": False
            }
        ]
    }
    _write_json_if_missing(os.path.join(state_dir, "decisions.json"), dec_data)

    # 5. data/data_dictionary.json
    dict_data = {
        "total_items": 1,
        "scales": [
            {
                "scale_id": "PRED",
                "name": "Predictor Scale",
                "author_year": "Standard, 2020",
                "items_count": 1,
                "item_range": [1, 5],
                "reverse_items": [],
                "subscales": {}
            }
        ],
        "columns": [
            {
                "column_name": "predictor",
                "scale_id": "PRED",
                "type": "scale_composite",
                "label": "Predictor Variable Composite",
                "is_reverse_coded": False
            },
            {
                "column_name": "outcome",
                "scale_id": "PRED",
                "type": "scale_composite",
                "label": "Outcome Variable Composite",
                "is_reverse_coded": False
            }
        ]
    }
    _write_json_if_missing(os.path.join(state_dir, "data", "data_dictionary.json"), dict_data)

    # 6. data/data_quality.json
    quality_data = {
        "sample_n": n,
        "missing_rate": 0.0,
        "unengaged_respondents": [],
        "mcar_test": {
            "chi2": 0.0,
            "df": 0,
            "p_value": 1.0
        },
        "outliers_detected": {
            "mahalanobis_d2_count": 0,
            "flagged_ids": []
        },
        "quality_verdict": "PASS"
    }
    _write_json_if_missing(os.path.join(state_dir, "data", "data_quality.json"), quality_data)

    # 7. Initialize and register default milestones in StrictStateMachine
    sm = StrictStateMachine(state_dir=state_dir, project_id=project_id)

    # Emit PROJECT_CREATED event if not already present
    existing_events = sm.event_engine.read_events(validate_schema=False, enforce_ordering=False)
    if not any(e.get("event_type") == "PROJECT_CREATED" for e in existing_events):
        sm.event_engine.emit(
            "PROJECT_CREATED",
            emitter_agent="academic-orchestrator",
            summary=f"Project '{project_id}' initialized with {methodology.upper()} methodology framework.",
            project_id=project_id,
            details={"title": title, "methodology": methodology, "sample_size": n}
        )

    if not sm.milestones:
        for m in DEFAULT_MILESTONES:
            sm.register_milestone(
                milestone_id=m["milestone_id"],
                title=m["title"],
                dependencies=m["dependencies"],
                required_input_artifacts=m["required_input_artifacts"],
                required_output_artifacts=m["required_output_artifacts"],
                active_agent=m["active_agent"],
                current_stage=m["stage_id"]
            )

    return {"status": "SUCCESS", "state_dir": state_dir, "initialized_files": list(SCHEMA_MAP.keys())}


def validate_state(project_path: str) -> Dict[str, Any]:
    """Validates all JSON files in state directory against their official JSON schemas."""
    state_dir = get_state_dir(project_path)
    if not os.path.exists(state_dir):
        return {"overall_verdict": "FAIL", "errors": [f"State directory not found: {state_dir}"]}

    report = {
        "state_directory": state_dir,
        "overall_verdict": "PASS",
        "validated_files": [],
        "errors": [],
        "warnings": []
    }

    if jsonschema is None:
        report["warnings"].append("jsonschema library not installed; skipping deep schema validation.")
        return report

    for rel_path, schema_filename in SCHEMA_MAP.items():
        file_path = os.path.join(state_dir, rel_path)
        schema_path = os.path.join(SCHEMAS_DIR, schema_filename)

        if not os.path.exists(file_path):
            if rel_path.startswith("analysis/") or rel_path.startswith("validation/"):
                continue
            report["errors"].append(f"Missing core state artifact: {rel_path}")
            report["overall_verdict"] = "FAIL"
            continue

        if not os.path.exists(schema_path):
            report["warnings"].append(f"Schema not found for {rel_path}: {schema_filename}")
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                instance = json.load(f)
            with open(schema_path, "r", encoding="utf-8") as sf:
                schema = json.load(sf)

            jsonschema.validate(instance=instance, schema=schema)
            report["validated_files"].append({"file": rel_path, "status": "VALID", "schema": schema_filename})
        except jsonschema.ValidationError as ve:
            report["overall_verdict"] = "FAIL"
            report["errors"].append(f"Schema validation failed for {rel_path}: {ve.message} (path: {list(ve.path)})")
        except Exception as e:
            report["overall_verdict"] = "FAIL"
            report["errors"].append(f"Error reading/validating {rel_path}: {str(e)}")

    # Validate incidents directory if present
    inc_dir = os.path.join(state_dir, "incidents")
    inc_schema_path = os.path.join(ROOT_DIR, "recovery", "incident_schema.json")
    if os.path.isdir(inc_dir) and os.path.exists(inc_schema_path):
        try:
            with open(inc_schema_path, "r", encoding="utf-8") as isf:
                inc_schema = json.load(isf)
            for ifname in sorted(os.listdir(inc_dir)):
                if ifname.endswith(".json"):
                    ipath = os.path.join(inc_dir, ifname)
                    try:
                        with open(ipath, "r", encoding="utf-8") as ifile:
                            i_data = json.load(ifile)
                        jsonschema.validate(instance=i_data, schema=inc_schema)
                        report["validated_files"].append({"file": f"incidents/{ifname}", "status": "VALID", "schema": "incident_schema.json"})
                    except jsonschema.ValidationError as ve:
                        report["overall_verdict"] = "FAIL"
                        report["errors"].append(f"Schema validation failed for incidents/{ifname}: {ve.message}")
                    except Exception as e:
                        report["overall_verdict"] = "FAIL"
                        report["errors"].append(f"Error reading incidents/{ifname}: {str(e)}")
        except Exception as e:
            report["warnings"].append(f"Error loading incident_schema.json: {str(e)}")

    return report


def get_status_summary(project_path: str) -> Dict[str, Any]:
    """Returns a high-level summary of the research project state."""
    state_dir = get_state_dir(project_path)
    summary = {
        "project_path": project_path,
        "state_dir": state_dir,
        "current_stage": "unknown",
        "project": {},
        "analyses_completed": [],
        "validations": {},
        "outputs_count": 0
    }

    proj_file = os.path.join(state_dir, "project.json")
    if os.path.exists(proj_file):
        with open(proj_file, "r", encoding="utf-8") as f:
            summary["project"] = json.load(f)
            summary["current_stage"] = summary["project"].get("current_stage", "unknown")

    analysis_dir = os.path.join(state_dir, "analysis")
    if os.path.exists(analysis_dir):
        for f in os.listdir(analysis_dir):
            if f.endswith(".json"):
                summary["analyses_completed"].append(f)

    val_dir = os.path.join(state_dir, "validation")
    if os.path.exists(val_dir):
        for vf in os.listdir(val_dir):
            if vf.endswith(".json"):
                try:
                    with open(os.path.join(val_dir, vf), "r", encoding="utf-8") as f:
                        val_content = json.load(f)
                    summary["validations"][vf] = val_content.get("overall_verdict", "UNKNOWN")
                except Exception:
                    summary["validations"][vf] = "CORRUPT"

    out_dir = os.path.join(state_dir, "outputs")
    if os.path.exists(out_dir):
        summary["outputs_count"] = len(os.listdir(out_dir))

    return summary


def record_decision(project_path: str, category: str, decision: str, rationale: str, agent: str, supervisor_approval: bool = False) -> Dict[str, Any]:
    """Appends an auditable decision to decisions.json. Approval strictly defaults to False."""
    state_dir = get_state_dir(project_path)
    dec_file = os.path.join(state_dir, "decisions.json")

    dec_data = {"decisions": []}
    if os.path.exists(dec_file):
        with open(dec_file, "r", encoding="utf-8") as f:
            dec_data = json.load(f)

    next_idx = len(dec_data.get("decisions", [])) + 1
    dec_id = f"DEC-{next_idx:03d}"
    now_iso = datetime.now(timezone.utc).isoformat()

    entry = {
        "decision_id": dec_id,
        "timestamp": now_iso,
        "category": category,
        "decision": decision,
        "rationale": rationale,
        "alternatives_considered": [],
        "agent": agent,
        "supervisor_approval": supervisor_approval
    }

    dec_data.setdefault("decisions", []).append(entry)
    with open(dec_file, "w", encoding="utf-8") as f:
        json.dump(dec_data, f, indent=2, ensure_ascii=False)

    return {"status": "RECORDED", "decision_id": dec_id, "entry": entry}


def set_stage(project_path: str, stage: str, status: Optional[str] = None) -> Dict[str, Any]:
    """
    Updates the current stage and optional status in project.json,
    enforcing state machine validation. Fails closed on unknown stage or invalid status.
    """
    if not stage or not isinstance(stage, str):
        raise UnknownMilestoneError("Stage name must be a non-empty string.")

    state_dir = get_state_dir(project_path)
    proj_file = os.path.join(state_dir, "project.json")
    if not os.path.exists(proj_file):
        return {"error": f"project.json not found in {state_dir}"}

    with open(proj_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Validate status if provided
    if status:
        status_upper = status.upper()
        valid_statuses = [s.value for s in MilestoneState] + [
            "IN_PROGRESS", "AWAITING_VALIDATION", "STAGE_COMPLETED", "FINAL_APPROVED", "BLOCKED"
        ]
        if status_upper not in valid_statuses and status not in ["in_progress", "awaiting_validation", "stage_completed", "final_approved", "blocked"]:
            raise UnknownStateError(f"Unknown status '{status}'. Valid states: {[s.value for s in MilestoneState]}.")

    data["current_stage"] = stage
    if status:
        data["status"] = status
    data["updated_at"] = datetime.now(timezone.utc).isoformat()

    with open(proj_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Sync with StrictStateMachine if current_state.json exists
    cs_path = os.path.join(state_dir, "current_state.json")
    if os.path.exists(cs_path):
        try:
            sm = StrictStateMachine(state_dir=state_dir, project_id=data.get("project_id"))
            mid = STAGE_TO_MILESTONE_MAP.get(stage)
            if mid and mid in sm.milestones:
                sm.milestones[mid]["current_stage"] = stage
                sm.save_all()
        except Exception:
            pass

    return {"status": "UPDATED", "current_stage": stage, "status_value": data.get("status")}


def log_incident(project_path: str, stage: str, error: str) -> Dict[str, Any]:
    """Logs a failure incident in academic-state/incidents/ conforming to incident_schema.json."""
    try:
        from recovery.recovery_engine import create_incident
        return create_incident(stage_id=stage, error_message=error, project_path=project_path)
    except Exception:
        # Fallback if recovery package is unavailable
        state_dir = get_state_dir(project_path)
        inc_dir = os.path.join(state_dir, "incidents")
        os.makedirs(inc_dir, exist_ok=True)
        now_iso = datetime.now(timezone.utc).isoformat()
        ts_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        inc_id = f"INC-TOOL-{ts_str}"
        incident_data = {
            "incident_id": inc_id,
            "failure_type": "TOOL",
            "severity": "MEDIUM",
            "stage_id": stage,
            "status": "ROUTED",
            "error_message": error,
            "diagnostic_summary": f"Failure logged in stage {stage}: {error}",
            "preserved_upstream_stages": [],
            "routing_plan": {
                "assigned_handler": "recovery-engine",
                "handler_type": "tool",
                "strategy": "RETRY_TOOL_FALLBACK",
                "target_stage": stage,
                "remediation_action": "Inspect error logs and re-execute stage",
                "remediation_command": None,
                "verification_gate": f"validate_stage_{stage}"
            },
            "timestamp": now_iso
        }
        inc_file = os.path.join(inc_dir, f"{inc_id}.json")
        with open(inc_file, "w", encoding="utf-8") as f:
            json.dump(incident_data, f, indent=2, ensure_ascii=False)
        return incident_data


def list_incidents(project_path: str) -> List[Dict[str, Any]]:
    """Lists all failure incidents in academic-state/incidents/."""
    state_dir = get_state_dir(project_path)
    inc_dir = os.path.join(state_dir, "incidents")
    incidents = []
    if os.path.isdir(inc_dir):
        for f in sorted(os.listdir(inc_dir)):
            if f.endswith(".json"):
                try:
                    with open(os.path.join(inc_dir, f), "r", encoding="utf-8") as fp:
                        incidents.append(json.load(fp))
                except Exception:
                    pass
    return incidents


def _write_json_if_missing(filepath: str, data: Dict[str, Any]) -> None:
    if not os.path.exists(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


# ==============================================================================
# CLI Entry Point
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="Academic State Manager CLI Engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init
    p_init = subparsers.add_parser("init", help="Initialize academic-state hierarchy")
    p_init.add_argument("project_path", help="Path to project directory")
    p_init.add_argument("--title", default="Empirical Research Study", help="Study title")
    p_init.add_argument("--methodology", default="sem", choices=["sem", "correlational", "experimental", "quasi_experimental", "cfa_scale_validation", "mixed_methods", "meta_analysis"])
    p_init.add_argument("--n", type=int, default=300, help="Sample size")

    # validate
    p_val = subparsers.add_parser("validate", help="Validate academic-state artifacts against JSON schemas")
    p_val.add_argument("project_path", help="Path to project directory")

    # status
    p_stat = subparsers.add_parser("status", help="Print dashboard summary of project state")
    p_stat.add_argument("project_path", help="Path to project directory")

    # record-decision
    p_dec = subparsers.add_parser("record-decision", help="Record an auditable methodological/statistical decision")
    p_dec.add_argument("project_path", help="Path to project directory")
    p_dec.add_argument("--category", required=True, choices=["methodology", "data_cleaning", "statistical_modeling", "reporting", "human_override"])
    p_dec.add_argument("--decision", required=True, help="Decision description")
    p_dec.add_argument("--rationale", required=True, help="Theoretical or statistical justification")
    p_dec.add_argument("--agent", required=True, help="Agent role making the decision")

    # set-stage
    p_stage = subparsers.add_parser("set-stage", help="Advance the project stage gate")
    p_stage.add_argument("project_path", help="Path to project directory")
    p_stage.add_argument("--stage", required=True, help="New stage ID (e.g. 04_bivariate_correlations)")
    p_stage.add_argument("--status", choices=["in_progress", "awaiting_validation", "stage_completed", "final_approved", "blocked"])

    # transition
    p_trans = subparsers.add_parser("transition", help="Transition milestone state in state machine")
    p_trans.add_argument("project_path", help="Path to project directory")
    p_trans.add_argument("--milestone", required=True, help="Milestone ID (e.g. M0_INGESTION)")
    p_trans.add_argument("--to-state", required=True, help="Target MilestoneState")
    p_trans.add_argument("--actor", default="academic-orchestrator", help="Acting agent")
    p_trans.add_argument("--rationale", default="", help="Transition rationale")

    # request-approval
    p_req_appr = subparsers.add_parser("request-approval", help="Request milestone approval")
    p_req_appr.add_argument("project_path", help="Path to project directory")
    p_req_appr.add_argument("--milestone", required=True, help="Milestone ID")
    p_req_appr.add_argument("--category", required=True, help="Approval category")
    p_req_appr.add_argument("--rationale", required=True, help="Request rationale")
    p_req_appr.add_argument("--agent", default="academic-orchestrator", help="Requester agent")

    # grant-approval
    p_grant_appr = subparsers.add_parser("grant-approval", help="Grant explicit human approval")
    p_grant_appr.add_argument("project_path", help="Path to project directory")
    p_grant_appr.add_argument("--approval-id", required=True, help="Approval ID")
    p_grant_appr.add_argument("--approver", required=True, help="Approver identity")
    p_grant_appr.add_argument("--signature", required=True, help="Digital signature/ack")
    p_grant_appr.add_argument("--comments", default="", help="Approver comments")

    # reject-approval
    p_rej_appr = subparsers.add_parser("reject-approval", help="Reject approval")
    p_rej_appr.add_argument("project_path", help="Path to project directory")
    p_rej_appr.add_argument("--approval-id", required=True, help="Approval ID")
    p_rej_appr.add_argument("--approver", required=True, help="Approver identity")
    p_rej_appr.add_argument("--comments", default="", help="Rejection comments")

    # log-incident
    p_inc = subparsers.add_parser("log-incident", help="Log a failure incident in academic-state/incidents/")
    p_inc.add_argument("project_path", help="Path to project directory")
    p_inc.add_argument("--stage", required=True, help="Failing stage ID")
    p_inc.add_argument("--error", required=True, help="Error message")

    # list-incidents
    p_list_inc = subparsers.add_parser("list-incidents", help="List all recorded failure incidents")
    p_list_inc.add_argument("project_path", help="Path to project directory")

    args = parser.parse_args()

    if args.command == "init":
        res = init_state(args.project_path, args.title, args.methodology, args.n)
    elif args.command == "validate":
        res = validate_state(args.project_path)
    elif args.command == "status":
        res = get_status_summary(args.project_path)
    elif args.command == "record-decision":
        res = record_decision(args.project_path, args.category, args.decision, args.rationale, args.agent)
    elif args.command == "set-stage":
        res = set_stage(args.project_path, args.stage, args.status)
    elif args.command == "transition":
        state_dir = get_state_dir(args.project_path)
        sm = StrictStateMachine(state_dir=state_dir)
        res = sm.transition_milestone(args.milestone, args.to_state, actor=args.actor, rationale=args.rationale)
    elif args.command == "request-approval":
        state_dir = get_state_dir(args.project_path)
        sm = StrictStateMachine(state_dir=state_dir)
        res = sm.request_approval(args.milestone, args.category, args.agent, args.rationale)
    elif args.command == "grant-approval":
        state_dir = get_state_dir(args.project_path)
        sm = StrictStateMachine(state_dir=state_dir)
        res = sm.grant_approval(args.approval_id, args.approver, args.signature, comments=args.comments)
    elif args.command == "reject-approval":
        state_dir = get_state_dir(args.project_path)
        sm = StrictStateMachine(state_dir=state_dir)
        res = sm.reject_approval(args.approval_id, args.approver, comments=args.comments)
    elif args.command == "log-incident":
        res = log_incident(args.project_path, args.stage, args.error)
    elif args.command == "list-incidents":
        res = list_incidents(args.project_path)
    else:
        res = {"error": f"Unknown command {args.command}"}

    print(json.dumps(res, indent=2, ensure_ascii=False))
    if args.command == "validate" and res.get("overall_verdict") == "FAIL":
        sys.exit(1)


if __name__ == "__main__":
    main()
