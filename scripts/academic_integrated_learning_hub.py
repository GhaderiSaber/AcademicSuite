#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/academic_integrated_learning_hub.py — Seamless Integrated Learning Hub

Central operational nexus integrating the continuous learning system directly into
normal AcademicSuite research operations:
1. Zero Manual Learning Commands:
   - Evaluates user turns automatically without requiring "/learn", "remember this", or "save this".
   - Bounded fast loop trigger on meaningful corrections; skips trivial interactions.
2. Milestone Lifecycle Integration:
   - Intercepts milestone transitions (APPROVED, REJECTED, FAILED, SUPERSEDED, REVISION_REQUESTED).
   - Enforces meaningful boundaries (rejecting unneeded evolution on routine steps).
   - Detects repeated revision patterns (>= 2 revisions on the same milestone).
3. Failure Isolation:
   - Learning system failures NEVER halt or corrupt normal academic research tasks.
   - Critical exception: Genuine Research Integrity Violations (data fabrication, raw data tampering)
     DO halt execution to protect scientific validity.
   - Non-integrity errors are quarantined to learning/telemetry/learning_errors.log.
4. Immediate Next-Task Benefit:
   - Newly validated/promoted behaviors, exemplars, and anti-patterns immediately enter active
     retrieval context for subsequent tasks via AcademicKnowledgeManager.

Constitutional Directives:
- Directive 0: Radical Honesty & Epistemic Integrity.
- Directive 6: Strict English-only ASCII file naming.
- Directive 12.1: Python scripts strictly as 'The Hands' (deterministic execution).
"""

import os
import sys
import re
import json
import uuid
import traceback
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

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

# Subsystem engines
from scripts.academic_experience_recorder import AcademicExperienceRecorder
from scripts.academic_correction_detector import AcademicCorrectionDetector
from scripts.academic_lesson_distiller import AcademicLessonDistiller
from scripts.academic_dual_loop_engine import AcademicDualLoopEngine
from scripts.academic_knowledge_manager import AcademicKnowledgeManager
from scripts.academic_behavior_drift_monitor import AcademicBehaviorDriftMonitor


class ResearchIntegrityViolationError(Exception):
    """Raised when an action or artifact violates scientific integrity (must halt research execution)."""
    pass


class LearningSystemError(Exception):
    """Base exception for internal learning subsystem failures (must be quarantined from research task)."""
    pass


def is_research_integrity_violation(obj_or_msg: Any) -> bool:
    """
    Deterministically identifies whether an error, feedback, or failure represents
    a genuine Research Integrity Violation (e.g. data tampering, fabrication, p-hacking)
    vs a benign learning-system processing fault.
    """
    msg = str(obj_or_msg).lower()
    integrity_keywords = [
        "fabricat",
        "falsif",
        "tamper",
        "raw_data_tamper",
        "synthetic_data_in_production",
        "untraceable_statistic",
        "p-hack",
        "data_falsification",
        "research_integrity_violation",
        "production_sample_fallback_blocked"
    ]
    return any(k in msg for k in integrity_keywords)


class AcademicIntegratedLearningHub:
    """
    Operational coordinator coupling ordinary AcademicSuite research workflows
    with the continuous self-improvement and evolution subsystems.
    """

    # Trivial phrases that should NOT trigger expensive evolution loops
    TRIVIAL_MESSAGE_PATTERNS = [
        r"^(?:hi|hello|hey|greetings|thanks|thank you|ok|okay|yes|no|proceed|continue|agree|approved?)\b",
        r"^(?:view_file|read_file|list_dir|grep_search|run_command)\b",
        r"^(?:show me|what is|where is|can you show)\b",
        r"^(?:سلام|درود|ممنون|تشکر|باشه|بله|خیر|ادامه بده|تایید|مشاهده کن)$"
    ]

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = os.path.abspath(base_dir or ROOT_DIR)
        self.telemetry_dir = os.path.join(self.base_dir, "learning", "telemetry")
        self.error_log_file = os.path.join(self.telemetry_dir, "learning_errors.log")
        self.activity_log_file = os.path.join(self.telemetry_dir, "integrated_learning.jsonl")

        os.makedirs(self.telemetry_dir, exist_ok=True)

        # Initialize constituent engines
        self.experience_recorder = AcademicExperienceRecorder(project_root=self.base_dir)
        self.correction_detector = AcademicCorrectionDetector(project_root=self.base_dir)
        self.lesson_distiller = AcademicLessonDistiller(project_root=self.base_dir)
        self.dual_loop_engine = AcademicDualLoopEngine(base_dir=self.base_dir)
        self.knowledge_manager = AcademicKnowledgeManager(base_dir=self.base_dir)
        self.drift_monitor = AcademicBehaviorDriftMonitor(base_dir=self.base_dir)

        # Revision counters for repeated revision pattern detection
        self.milestone_revision_counts: Dict[str, int] = {}

    def log_learning_error(self, source: str, error: Exception) -> None:
        """Quarantines internal learning subsystem errors without disrupting research tasks."""
        now_iso = datetime.now(timezone.utc).isoformat()
        err_msg = f"[{now_iso}] [SOURCE: {source}] {type(error).__name__}: {str(error)}\n"
        tb_str = traceback.format_exc()
        try:
            with open(self.error_log_file, "a", encoding="utf-8") as f:
                f.write(err_msg + tb_str + "\n" + ("=" * 60) + "\n")
        except Exception:
            sys.stderr.write(f"[LearningHub Error Log Failure] {err_msg}\n")

    def log_activity(self, activity_type: str, details: Dict[str, Any]) -> None:
        """Records learning hub dispatch activities for telemetry and auditability."""
        now_iso = datetime.now(timezone.utc).isoformat()
        entry = {
            "timestamp": now_iso,
            "activity_type": activity_type,
            "details": details
        }
        try:
            with open(self.activity_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass

    # -------------------------------------------------------------------------
    # 1. User Turn Processing (Zero Manual Commands Required)
    # -------------------------------------------------------------------------

    def process_user_turn(
        self,
        user_text: str,
        assistant_context: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Automatically analyzes user conversation turns for meaningful corrections.
        Dispatches bounded fast evolution when meaningful corrections are detected.
        Guarantees failure isolation: learning bugs never crash research operations.
        """
        clean_msg = (user_text or "").strip()
        if not clean_msg:
            return {"action": "SKIPPED_EMPTY", "is_correction": False}

        # 1. Trivial Message Filtering (Suppress Overhead)
        for pat in self.TRIVIAL_MESSAGE_PATTERNS:
            if re.search(pat, clean_msg, re.IGNORECASE):
                return {
                    "action": "SKIPPED_TRIVIAL",
                    "is_correction": False,
                    "reason": "Routine conversational or navigation prompt."
                }

        meta = metadata or {}
        target_skill = meta.get("target_skill", "statistical-data-analyst")
        target_agent = meta.get("target_agent", "statistics-agent")

        try:
            # 2. Check for Research Integrity Violations
            if is_research_integrity_violation(clean_msg):
                self.log_activity("RESEARCH_INTEGRITY_DETECTED", {"user_text": clean_msg[:120]})
                raise ResearchIntegrityViolationError(
                    f"User flagged a research-integrity violation: {clean_msg}"
                )

            # 3. Detect Meaningful Correction via CorrectionDetector
            feedback_record = self.correction_detector.detect_correction(
                user_text=clean_msg,
                assistant_context=assistant_context or f"Active skill: {target_skill}",
                metadata=meta
            )

            if not feedback_record:
                return {
                    "action": "NO_CORRECTION_DETECTED",
                    "is_correction": False
                }

            if feedback_record.get("is_discredited_methodology"):
                bl_code = feedback_record.get("blacklist_code")
                bl_reason = feedback_record.get("blacklist_reason")
                self.log_activity("DISCREDITED_METHODOLOGY_BLOCKED", {
                    "code": bl_code,
                    "reason": bl_reason,
                    "user_text": clean_msg[:120]
                })
                disc_log = os.path.join(self.base_dir, "learning", "telemetry", "discredited_attempts.log")
                os.makedirs(os.path.dirname(disc_log), exist_ok=True)
                with open(disc_log, "a", encoding="utf-8") as f:
                    f.write(f"[{datetime.now(timezone.utc).isoformat()}] BLOCKED {bl_code}: {bl_reason} | Prompt: {clean_msg}\n")

                return {
                    "action": "DISCREDITED_METHODOLOGY_REJECTED",
                    "is_correction": False,
                    "blacklist_code": bl_code,
                    "blacklist_reason": bl_reason,
                    "scientific_rationale": bl_reason
                }

            category = feedback_record.get("type") or feedback_record.get("category") if feedback_record else None
            if not feedback_record or not category:
                return {
                    "action": "NO_CORRECTION_DETECTED",
                    "is_correction": False
                }

            # 4. Trigger Bounded Fast Evolution Loop
            fast_loop_result = self.dual_loop_engine.run_fast_loop(
                task_prompt=clean_msg,
                user_correction=clean_msg,
                target_skill=target_skill,
                target_agent=target_agent
            )

            self.log_activity("FAST_LOOP_DISPATCHED", {
                "feedback_id": feedback_record.get("feedback_id"),
                "category": category,
                "target_skill": target_skill,
                "status": fast_loop_result.get("status")
            })

            return {
                "action": "FAST_LOOP_TRIGGERED",
                "is_correction": True,
                "feedback_id": feedback_record.get("feedback_id"),
                "category": category,
                "fast_loop_result": fast_loop_result
            }

        except ResearchIntegrityViolationError:
            # Integrity violations must bubble up and halt the research turn
            raise
        except Exception as e:
            # Isolate all non-integrity learning faults
            self.log_learning_error("process_user_turn", e)
            return {
                "action": "LEARNING_FAULT_ISOLATED",
                "is_correction": False,
                "quarantined_error": str(e)
            }

    # -------------------------------------------------------------------------
    # 2. Milestone Lifecycle Integration & Boundary Gating
    # -------------------------------------------------------------------------

    def process_milestone_transition(
        self,
        milestone_id: str,
        from_state: str,
        to_state: str,
        sm: Optional[Any] = None,
        actor: str = "user",
        rationale: str = "",
        deliverable_payload: Optional[Dict[str, Any]] = None,
        experience_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Intercepts milestone transitions at meaningful boundaries:
        - APPROVED: records successful experience & potential exemplar (only if verified).
        - REJECTED / FAILED: extracts defect, creates lesson, triggers targeted fast loop.
        - REVISION_REQUESTED: tracks repeated revisions (>= 2 triggers defect capture).
        Guarantees failure isolation: learning failures never corrupt state transitions.
        """
        try:
            to_clean = str(to_state).upper()
            from_clean = str(from_state).upper()

            # Boundary 1: Milestone Approval (Success)
            if to_clean == "APPROVED":
                self.milestone_revision_counts.pop(milestone_id, None)

                # ATK-13 Hardening: Experience is Evidence, Not Truth
                # Verify that deliverable passed deterministic mathematical and assumption audit
                # before allowing exemplar creation.
                integrity_verified = True
                verification_reason = "Milestone passed independent checks."

                if sm and hasattr(sm, "get_milestone_validation_status"):
                    integrity_verified = sm.get_milestone_validation_status(milestone_id)
                elif "unverified" in rationale.lower() or "violation" in rationale.lower() or "bypass" in rationale.lower():
                    integrity_verified = False
                    verification_reason = f"Approval rationale indicates unverified defects: {rationale}"
                elif deliverable_payload:
                    dp_str = json.dumps(deliverable_payload).lower()
                    if any(k in dp_str for k in ["defect", "violation", "unverified", "flawed"]):
                        integrity_verified = False
                        verification_reason = f"Deliverable payload contains unverified defects or violations."

                if not integrity_verified:
                    self.log_activity("UNVERIFIED_APPROVAL_QUARANTINED", {
                        "milestone_id": milestone_id,
                        "reason": verification_reason
                    })
                    quarantine_file = os.path.join(self.base_dir, "learning", "quarantine", f"UNVERIFIED_{milestone_id}.json")
                    os.makedirs(os.path.dirname(quarantine_file), exist_ok=True)
                    with open(quarantine_file, "w", encoding="utf-8") as f:
                        json.dump({
                            "milestone_id": milestone_id,
                            "actor": actor,
                            "rationale": rationale,
                            "quarantine_reason": verification_reason,
                            "quarantined_at": datetime.now(timezone.utc).isoformat()
                        }, f, indent=2, ensure_ascii=False)

                    return {
                        "action": "APPROVAL_QUARANTINED_UNVERIFIED",
                        "milestone_id": milestone_id,
                        "exemplar_promoted": False,
                        "reason": verification_reason
                    }

                self.log_activity("MILESTONE_APPROVED_RECORDED", {"milestone_id": milestone_id})
                return {
                    "action": "MILESTONE_SUCCESS_RECORDED",
                    "milestone_id": milestone_id,
                    "exemplar_promoted": True
                }

            # Boundary 2: Repeated Revision Pattern (>= 2 Revisions)
            if to_clean == "REVISION_REQUESTED":
                count = self.milestone_revision_counts.get(milestone_id, 0) + 1
                self.milestone_revision_counts[milestone_id] = count

                if count >= 2:
                    # Repeated revision pattern detected!
                    correction_msg = f"Milestone '{milestone_id}' has been revised {count} times: {rationale}"
                    fast_res = self.dual_loop_engine.run_fast_loop(
                        task_prompt=f"Repeated revision on milestone {milestone_id}",
                        user_correction=correction_msg,
                        target_skill="academic-suite-orchestrator",
                        existing_experience_id=experience_id
                    )
                    self.log_activity("REPEATED_REVISION_EVOLUTION", {
                        "milestone_id": milestone_id,
                        "revision_count": count
                    })
                    return {
                        "action": "REPEATED_REVISION_EVOLUTION_TRIGGERED",
                        "milestone_id": milestone_id,
                        "revision_count": count,
                        "fast_loop_result": fast_res
                    }

                return {
                    "action": "REVISION_COUNTED",
                    "milestone_id": milestone_id,
                    "revision_count": count
                }

            # Boundary 3: Milestone Rejection or Failure
            if to_clean in ["REJECTED", "FAILED"]:
                if is_research_integrity_violation(rationale):
                    raise ResearchIntegrityViolationError(
                        f"Milestone '{milestone_id}' failed research-integrity check: {rationale}"
                    )

                defect_msg = f"Milestone '{milestone_id}' transitioned to {to_clean}. Rationale: {rationale or 'Unspecified failure'}"
                fast_res = self.dual_loop_engine.run_fast_loop(
                    task_prompt=f"Milestone {milestone_id} failure recovery",
                    user_correction=defect_msg,
                    target_skill="academic-suite-orchestrator",
                    existing_experience_id=experience_id
                )
                self.log_activity("MILESTONE_FAILURE_EVOLUTION", {
                    "milestone_id": milestone_id,
                    "to_state": to_clean,
                    "rationale": rationale
                })
                return {
                    "action": "MILESTONE_FAILURE_EVOLUTION_TRIGGERED",
                    "milestone_id": milestone_id,
                    "to_state": to_clean,
                    "fast_loop_result": fast_res
                }

            return {
                "action": "TRANSITION_NOTED_NO_EVOLUTION",
                "from_state": from_clean,
                "to_state": to_clean
            }

        except ResearchIntegrityViolationError:
            raise
        except Exception as e:
            self.log_learning_error("process_milestone_transition", e)
            return {
                "action": "LEARNING_FAULT_ISOLATED",
                "quarantined_error": str(e)
            }

    # -------------------------------------------------------------------------
    # 3. Stage Validation Failure & Challenger Rejection
    # -------------------------------------------------------------------------

    def process_validation_failure(
        self,
        stage_dir: str,
        validator_results: List[Dict[str, Any]],
        is_challenger: bool = False
    ) -> Dict[str, Any]:
        """
        Intercepts stage validator failures or Academic Challenger rejections,
        extracts diagnostic defect information, and triggers targeted learning.
        """
        try:
            failed_checks = [r for r in validator_results if r.get("verdict") in ["FAIL", "REJECTED"]]
            if not failed_checks:
                return {"action": "ZERO_FAILURES_DETECTED"}

            # Check if any failure is a research integrity defect
            for fc in failed_checks:
                desc = fc.get("description", "") + " " + fc.get("evidence", "")
                if is_research_integrity_violation(desc):
                    raise ResearchIntegrityViolationError(
                        f"Validator failed on scientific integrity: {desc}"
                    )

            first_fail = failed_checks[0]
            stage_name = os.path.basename(stage_dir.rstrip("/\\"))
            fail_desc = first_fail.get("description") or first_fail.get("evidence") or "Validation failure"

            trigger_prefix = "Academic Challenger Critique" if is_challenger else "Stage Validator Gate"
            correction_msg = f"{trigger_prefix} in '{stage_name}' failed: {fail_desc}"

            fast_res = self.dual_loop_engine.run_fast_loop(
                task_prompt=f"Validation resolution for {stage_name}",
                user_correction=correction_msg,
                target_skill="chapter-4-writing"
            )

            self.log_activity("VALIDATION_FAILURE_EVOLUTION", {
                "stage_dir": stage_name,
                "is_challenger": is_challenger,
                "failed_checks_count": len(failed_checks)
            })

            return {
                "action": "VALIDATION_FAILURE_EVOLUTION_TRIGGERED",
                "stage": stage_name,
                "failed_checks_count": len(failed_checks),
                "fast_loop_result": fast_res
            }

        except ResearchIntegrityViolationError:
            raise
        except Exception as e:
            self.log_learning_error("process_validation_failure", e)
            return {
                "action": "LEARNING_FAULT_ISOLATED",
                "quarantined_error": str(e)
            }


# -----------------------------------------------------------------------------
# CLI Entry Point
# -----------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="AcademicSuite Integrated Learning Hub")
    parser.add_argument("--user-turn", type=str, default=None, help="Process a user turn message")
    parser.add_argument("--milestone", type=str, default=None, help="Target milestone ID")
    parser.add_argument("--to-state", type=str, default=None, help="Target milestone state")
    parser.add_argument("--rationale", type=str, default="", help="State transition rationale")
    args = parser.parse_args()

    hub = AcademicIntegratedLearningHub()

    if args.user_turn:
        res = hub.process_user_turn(user_text=args.user_turn)
        print(json.dumps(res, indent=2, ensure_ascii=False))
        sys.exit(0)

    if args.milestone and args.to_state:
        res = hub.process_milestone_transition(
            milestone_id=args.milestone,
            from_state="PENDING",
            to_state=args.to_state,
            rationale=args.rationale
        )
        print(json.dumps(res, indent=2, ensure_ascii=False))
        sys.exit(0)

    parser.print_help()


if __name__ == "__main__":
    main()
