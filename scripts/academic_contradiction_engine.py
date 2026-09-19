#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/academic_contradiction_engine.py — AcademicSuite 6-Stage Contradiction Resolution Engine

Governs Phase 27: Eliminates premature/automatic conversion of CONFLICT_DETECTED
into RESOLVED_WITH_CONDITIONS.

Enforces the strict, empirical 6-stage lifecycle:
CONFLICT_DETECTED
       ↓
CONFLICT_ANALYSIS
       ↓
EVIDENCE_COMPARISON
       ↓
CONDITION_IDENTIFICATION
       ↓
INDEPENDENT_TEST
       ↓
RESOLVED (or UNRESOLVED)

Particularly vital for methodological tensions:
- RM-ANOVA vs Linear Mixed Models (LMM)
- Baron & Kenny vs Preacher & Hayes Bootstrap Mediation
- Median Split (Dichotomization) vs Continuous Interaction / Johnson-Neyman
- Listwise Deletion vs Full Information Maximum Likelihood (FIML)
- Parametric vs Non-Parametric/Bootstrap Testing
"""

import os
import sys
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

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

from contracts.contract_validator import validate_contradiction_record


class ContradictionError(Exception):
    """Base exception for contradiction lifecycle errors."""
    pass


class PrematureContradictionResolutionError(ContradictionError):
    """Raised when a contradiction attempts to resolve without independent empirical verification."""
    pass


class AcademicContradictionEngine:
    """
    Deterministic engine governing the 6-stage Contradiction Resolution Lifecycle.
    Ensures that conflicting academic, methodological, or statistical directives are
    never automatically converted into RESOLVED_WITH_CONDITIONS without empirical evidence.
    """

    STAGES = [
        "CONFLICT_DETECTED",
        "CONFLICT_ANALYSIS",
        "EVIDENCE_COMPARISON",
        "CONDITION_IDENTIFICATION",
        "INDEPENDENT_TEST",
        "RESOLVED",
        "UNRESOLVED"
    ]

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = os.path.abspath(base_dir or ROOT_DIR)
        self.learning_dir = os.path.join(self.base_dir, "learning")
        self.knowledge_dir = os.path.join(self.learning_dir, "knowledge")
        self.contradictions_dir = os.path.join(self.knowledge_dir, "contradictions")
        os.makedirs(self.contradictions_dir, exist_ok=True)
        self.index_file = os.path.join(self.contradictions_dir, "index.jsonl")

    def _get_path(self, contradiction_id: str) -> str:
        return os.path.join(self.contradictions_dir, f"{contradiction_id}.json")

    def save_record(self, record: Dict[str, Any]) -> None:
        """Validates contract and writes record to disk."""
        val_res = validate_contradiction_record(record)
        if not val_res.get("valid"):
            raise ContradictionError(f"Contradiction schema validation failed: {val_res.get('errors')}")

        file_path = self._get_path(record["contradiction_id"])
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2, ensure_ascii=False)

        # Update fast index
        index_entry = {
            "contradiction_id": record["contradiction_id"],
            "target_skill": record["target_skill"],
            "lesson_a_id": record["lesson_a_id"],
            "lesson_b_id": record["lesson_b_id"],
            "conflict_type": record["conflict_type"],
            "stage": record.get("stage", "CONFLICT_DETECTED"),
            "status": record["status"],
            "detected_at": record["detected_at"],
            "resolved_at": record.get("resolved_at"),
            "file_path": file_path
        }
        with open(self.index_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(index_entry, ensure_ascii=False) + "\n")

    def load_record(self, contradiction_id: str) -> Dict[str, Any]:
        """Loads contradiction record from disk."""
        file_path = self._get_path(contradiction_id)
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Contradiction record '{contradiction_id}' not found at {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    # -------------------------------------------------------------------------
    # Stage 1: CONFLICT_DETECTED
    # -------------------------------------------------------------------------

    def detect_conflict(
        self,
        lesson_a: Dict[str, Any],
        lesson_b: Dict[str, Any],
        conflict_type: str,
        description: str,
        target_skill: Optional[str] = None,
        contradiction_id: Optional[str] = None,
        record_to_disk: bool = True
    ) -> Dict[str, Any]:
        """
        Stage 1: Records an initial contradiction detection event.
        STRICT INVARIANT: NEVER automatically converts into RESOLVED_WITH_CONDITIONS.
        Initial status is strictly CONFLICT_DETECTED.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        date_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        ctd_id = contradiction_id or f"CTD-{date_str}-{uuid.uuid4().hex[:6].upper()}"

        skill = (
            target_skill
            or lesson_a.get("target_skill")
            or (lesson_a.get("related_skills", ["methodology-review"])[0] if lesson_a.get("related_skills") else "methodology-review")
        )

        record = {
            "contract_version": "1.0.0",
            "contradiction_id": ctd_id,
            "target_skill": skill,
            "lesson_a_id": lesson_a.get("lesson_id", "LSN-A"),
            "lesson_b_id": lesson_b.get("lesson_id", "LSN-B"),
            "conflict_type": conflict_type,
            "description": description,
            "stage": "CONFLICT_DETECTED",
            "status": "CONFLICT_DETECTED",
            "reconciliation_strategy": "PENDING_HUMAN_RESOLUTION",
            "detected_at": now_iso
        }

        if record_to_disk:
            self.save_record(record)
        return record

    # -------------------------------------------------------------------------
    # Stage 2: CONFLICT_ANALYSIS
    # -------------------------------------------------------------------------

    def advance_to_conflict_analysis(
        self,
        contradiction_id: str,
        assumptions_a: List[str],
        assumptions_b: List[str],
        root_cause: str,
        methodological_risk: Optional[str] = None,
        record_to_disk: bool = True
    ) -> Dict[str, Any]:
        """
        Stage 2: Conducts in-depth causal and theoretical analysis of competing assumptions.
        """
        record = self.load_record(contradiction_id)
        if record["stage"] not in ["CONFLICT_DETECTED", "CONFLICT_ANALYSIS"]:
            raise ContradictionError(
                f"Cannot transition to CONFLICT_ANALYSIS from stage '{record['stage']}'."
            )

        if not assumptions_a or not assumptions_b or not root_cause:
            raise ContradictionError("Conflict analysis requires non-empty assumptions and root cause explanation.")

        record["stage"] = "CONFLICT_ANALYSIS"
        record["status"] = "CONFLICT_ANALYSIS"
        record["conflict_analysis"] = {
            "assumptions_a": assumptions_a,
            "assumptions_b": assumptions_b,
            "root_cause": root_cause,
            "methodological_risk": methodological_risk or "Risk of statistical conclusion invalidity or biased estimates."
        }

        if record_to_disk:
            self.save_record(record)
        return record

    # -------------------------------------------------------------------------
    # Stage 3: EVIDENCE_COMPARISON
    # -------------------------------------------------------------------------

    def advance_to_evidence_comparison(
        self,
        contradiction_id: str,
        evidence_for_a: List[str],
        evidence_for_b: List[str],
        divergence_analysis: Optional[str] = None,
        record_to_disk: bool = True
    ) -> Dict[str, Any]:
        """
        Stage 3: Compares empirical evidence supporting both directives.
        """
        record = self.load_record(contradiction_id)
        if record["stage"] not in ["CONFLICT_ANALYSIS", "EVIDENCE_COMPARISON"]:
            raise ContradictionError(
                f"Cannot transition to EVIDENCE_COMPARISON from stage '{record['stage']}'. Must complete CONFLICT_ANALYSIS first."
            )

        if not evidence_for_a or not evidence_for_b:
            raise ContradictionError("Evidence comparison requires non-empty evidence citations for both directives.")

        record["stage"] = "EVIDENCE_COMPARISON"
        record["status"] = "EVIDENCE_COMPARISON"
        record["evidence_comparison"] = {
            "evidence_for_a": evidence_for_a,
            "evidence_for_b": evidence_for_b,
            "divergence_analysis": divergence_analysis or "Empirical divergence between parametric efficiency and robustness."
        }

        if record_to_disk:
            self.save_record(record)
        return record

    # -------------------------------------------------------------------------
    # Stage 4: CONDITION_IDENTIFICATION
    # -------------------------------------------------------------------------

    def advance_to_condition_identification(
        self,
        contradiction_id: str,
        condition_for_a: str,
        condition_for_b: str,
        boundary_exceptions: Optional[List[str]] = None,
        conditional_rule: Optional[str] = None,
        reconciliation_strategy: str = "CONTEXTUAL_DISAMBIGUATION",
        record_to_disk: bool = True
    ) -> Dict[str, Any]:
        """
        Stage 4: Formulates precise contextual boundary conditions where each approach is valid.
        """
        record = self.load_record(contradiction_id)
        if record["stage"] not in ["EVIDENCE_COMPARISON", "CONDITION_IDENTIFICATION"]:
            raise ContradictionError(
                f"Cannot transition to CONDITION_IDENTIFICATION from stage '{record['stage']}'. Must complete EVIDENCE_COMPARISON first."
            )

        if not condition_for_a or not condition_for_b:
            raise ContradictionError("Condition identification requires explicit non-empty conditions for both directives.")

        exceptions = boundary_exceptions or ["Severe simultaneous assumption breakdown"]
        rule_str = conditional_rule or (
            f"WHEN {condition_for_a} → apply approach A; "
            f"WHEN {condition_for_b} → apply approach B; "
            f"EXCEPT when {exceptions[0]}."
        )

        record["stage"] = "CONDITION_IDENTIFICATION"
        record["status"] = "CONDITION_IDENTIFICATION"
        record["reconciliation_strategy"] = reconciliation_strategy
        record["applicability_conditions"] = {
            "condition_for_a": condition_for_a,
            "condition_for_b": condition_for_b
        }
        record["identified_conditions"] = {
            "condition_for_a": condition_for_a,
            "condition_for_b": condition_for_b,
            "boundary_exceptions": exceptions,
            "conditional_rule": rule_str
        }

        if record_to_disk:
            self.save_record(record)
        return record

    # -------------------------------------------------------------------------
    # Stage 5: INDEPENDENT_TEST
    # -------------------------------------------------------------------------

    def advance_to_independent_test(
        self,
        contradiction_id: str,
        test_suite_id: str,
        test_arms: Optional[Dict[str, Any]] = None,
        evaluator: str = "AcademicIndependentEvaluator",
        record_to_disk: bool = True
    ) -> Dict[str, Any]:
        """
        Stage 5: Submits the identified boundary conditions to an independent empirical evaluation suite.
        """
        record = self.load_record(contradiction_id)
        if record["stage"] not in ["CONDITION_IDENTIFICATION", "INDEPENDENT_TEST"]:
            raise ContradictionError(
                f"Cannot transition to INDEPENDENT_TEST from stage '{record['stage']}'. Must complete CONDITION_IDENTIFICATION first."
            )

        record["stage"] = "INDEPENDENT_TEST"
        record["status"] = "INDEPENDENT_TEST"
        record["independent_test"] = {
            "test_suite_id": test_suite_id,
            "test_arms": test_arms or {
                "arm_a_under_condition_a": "PENDING",
                "arm_a_under_condition_b": "PENDING",
                "arm_b_under_condition_b": "PENDING",
                "arm_b_under_condition_a": "PENDING"
            },
            "independent_verdict": "PENDING",
            "evaluator": evaluator
        }

        if record_to_disk:
            self.save_record(record)
        return record

    # -------------------------------------------------------------------------
    # Stage 6: Terminal Outcomes (RESOLVED or UNRESOLVED)
    # -------------------------------------------------------------------------

    def resolve_with_test_evidence(
        self,
        contradiction_id: str,
        test_result: Dict[str, Any],
        reconciled_by: str = "digital-saber",
        resolution_summary: Optional[str] = None,
        record_to_disk: bool = True
    ) -> Dict[str, Any]:
        """
        Stage 6a: Resolves the contradiction IF AND ONLY IF independent empirical test passes.
        FAIL-CLOSED INVARIANT: Attempting to resolve without passing independent test is blocked.
        """
        record = self.load_record(contradiction_id)
        if record["stage"] != "INDEPENDENT_TEST":
            raise PrematureContradictionResolutionError(
                f"Cannot resolve contradiction from stage '{record['stage']}'. "
                f"Must execute INDEPENDENT_TEST first."
            )

        verdict = str(test_result.get("independent_verdict") or test_result.get("verdict") or "").upper()
        if verdict != "PASS":
            # If test fails, transition to UNRESOLVED rather than falsely resolving!
            return self.mark_unresolved(
                contradiction_id=contradiction_id,
                rationale=f"Independent test '{test_result.get('test_suite_id', 'TEST')}' failed with verdict '{verdict}'.",
                evaluator=test_result.get("evaluator", "AcademicIndependentEvaluator"),
                record_to_disk=record_to_disk
            )

        now_iso = datetime.now(timezone.utc).isoformat()
        test_payload = {
            "test_suite_id": test_result.get("test_suite_id", "TEST-INDEPENDENT-001"),
            "test_results": test_result.get("test_results", {"condition_a_verified": True, "condition_b_verified": True}),
            "independent_verdict": "PASS",
            "evaluator": test_result.get("evaluator", "AcademicIndependentEvaluator")
        }

        summary = resolution_summary or (
            f"Contradiction between '{record['lesson_a_id']}' and '{record['lesson_b_id']}' "
            f"empirically resolved under verified contextual boundary conditions."
        )

        record["stage"] = "RESOLVED"
        record["status"] = "RESOLVED"
        record["independent_test"] = test_payload
        record["resolution_summary"] = summary
        record["resolved_at"] = now_iso
        record["reconciled_by"] = reconciled_by

        if record_to_disk:
            self.save_record(record)
        return record

    def mark_unresolved(
        self,
        contradiction_id: str,
        rationale: str,
        evaluator: Optional[str] = None,
        record_to_disk: bool = True
    ) -> Dict[str, Any]:
        """
        Stage 6b: Marks contradiction as UNRESOLVED due to empirical failure or irreconcilable assumptions.
        """
        record = self.load_record(contradiction_id)
        record["stage"] = "UNRESOLVED"
        record["status"] = "UNRESOLVED"
        record["resolution_summary"] = rationale
        if "independent_test" not in record:
            record["independent_test"] = {
                "test_suite_id": "TEST-EVAL-FAILED",
                "independent_verdict": "FAIL",
                "evaluator": evaluator or "AcademicIndependentEvaluator"
            }
        else:
            record["independent_test"]["independent_verdict"] = "FAIL"

        if record_to_disk:
            self.save_record(record)
        return record

    def check_resolution_allowed(self, record: Dict[str, Any]) -> None:
        """
        Enforces fail-closed resolution invariant:
        Raises PrematureContradictionResolutionError if an unvalidated contradiction is treated as resolved.
        """
        status = record.get("status", "")
        if status in ["RESOLVED", "RESOLVED_WITH_CONDITIONS"]:
            if record.get("stage") != "RESOLVED":
                raise PrematureContradictionResolutionError(
                    f"Contradiction '{record.get('contradiction_id')}' cannot be resolved at stage '{record.get('stage')}'. "
                    f"Must complete full 6-stage lifecycle through INDEPENDENT_TEST."
                )
            ind_test = record.get("independent_test", {})
            if ind_test.get("independent_verdict") != "PASS":
                raise PrematureContradictionResolutionError(
                    f"Contradiction '{record.get('contradiction_id')}' requires a passing independent test verdict."
                )
