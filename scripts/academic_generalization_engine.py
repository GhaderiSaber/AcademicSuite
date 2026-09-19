#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/academic_generalization_engine.py — AcademicSuite 7-Stage Generalization Progression Engine

Implements Phase 25: Replacing premature 2-experience elevation to CROSS_PROJECT_UNIVERSAL
with a strict 7-stage Generalization Progression Ladder requiring heterogeneous evidence:

OBSERVED
    ↓
LOCAL_LESSON
    ↓
REPEATED_PATTERN
    ↓
GENERALIZATION_CANDIDATE
    ↓
CROSS_CONTEXT_VALIDATION
    ↓
CROSS_DOMAIN_VALIDATION
    ↓
PROMOTED_PRINCIPLE

Constitutional Directives:
- Directive 0: Radical Honesty & Epistemic Integrity.
- Directive 6: Strict English-only ASCII file naming.
- Directive 12.1: Python scripts strictly as 'The Hands' (deterministic execution).
- Directive 19: The Six-Part Functional Separation Invariant.
- Premature Generalization Invariant: 2 experiences within the same project can NEVER
  elevate a lesson or rule to CROSS_PROJECT_UNIVERSAL.
"""

import os
import sys
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Set

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

from contracts.contract_validator import validate_generalization_lifecycle


class GeneralizationError(Exception):
    """Base exception for generalization engine errors."""
    pass


class PrematureGeneralizationError(GeneralizationError):
    """Raised when an attempt is made to elevate or promote a rule without required heterogeneous evidence."""
    pass


class AcademicGeneralizationEngine:
    """
    Deterministic engine governing the 7-stage Generalization Progression Ladder.
    Ensures that empirical lessons move from local observations to promoted universal principles
    only when backed by verified evidence across heterogeneous contexts and domains.
    """

    STAGES = [
        "OBSERVED",
        "LOCAL_LESSON",
        "REPEATED_PATTERN",
        "GENERALIZATION_CANDIDATE",
        "CROSS_CONTEXT_VALIDATION",
        "CROSS_DOMAIN_VALIDATION",
        "PROMOTED_PRINCIPLE"
    ]

    STAGE_SCOPES = {
        "OBSERVED": "PROJECT_SPECIFIC",
        "LOCAL_LESSON": "PROJECT_SPECIFIC",
        "REPEATED_PATTERN": "LOCAL_PATTERN",
        "GENERALIZATION_CANDIDATE": "GENERALIZATION_CANDIDATE",
        "CROSS_CONTEXT_VALIDATION": "CROSS_CONTEXT_VALIDATED",
        "CROSS_DOMAIN_VALIDATION": "CROSS_DOMAIN_VALIDATED",
        "PROMOTED_PRINCIPLE": "CROSS_PROJECT_UNIVERSAL"
    }

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = os.path.abspath(base_dir or ROOT_DIR)
        self.learning_dir = os.path.join(self.base_dir, "learning")
        self.knowledge_dir = os.path.join(self.learning_dir, "knowledge")
        self.generalizations_dir = os.path.join(self.knowledge_dir, "generalizations")
        self.principles_dir = os.path.join(self.knowledge_dir, "principles")
        os.makedirs(self.generalizations_dir, exist_ok=True)
        os.makedirs(self.principles_dir, exist_ok=True)

    def _get_path(self, generalization_id: str) -> str:
        return os.path.join(self.generalizations_dir, f"{generalization_id}.json")

    def _save_record(self, record: Dict[str, Any]) -> None:
        val_res = validate_generalization_lifecycle(record)
        if not val_res.get("valid"):
            raise GeneralizationError(
                f"Generalization lifecycle contract validation failed: {val_res.get('errors')}"
            )
        path = self._get_path(record["generalization_id"])
        with open(path, "w", encoding="utf-8") as f:
            json.dump(record, f, indent=2)

    def load_record(self, generalization_id: str) -> Dict[str, Any]:
        path = self._get_path(generalization_id)
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Generalization record not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    # -------------------------------------------------------------------------
    # Stage 1: OBSERVED
    # -------------------------------------------------------------------------

    def record_observation(
        self,
        target_rule: str,
        project_id: str,
        task_id: str = "task-01",
        source_experience_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        generalization_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Stage 1: Records an initial empirical observation.
        """
        now_iso = datetime.now(timezone.utc).isoformat()
        gen_id = generalization_id or f"GEN-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        obs_entry = {
            "observation_id": f"OBS-{uuid.uuid4().hex[:8].upper()}",
            "source_experience_id": source_experience_id or "EXP-OBS-001",
            "project_id": project_id,
            "task_id": task_id,
            "context": context or {
                "domain": "statistics",
                "design": "unknown",
                "sample_size": 100,
                "data_type": "continuous"
            }
        }

        record = {
            "contract_version": "1.0.0",
            "generalization_id": gen_id,
            "target_rule": target_rule,
            "stage": "OBSERVED",
            "scope": self.STAGE_SCOPES["OBSERVED"],
            "evidence_summary": {
                "observations": [obs_entry],
                "contexts_validated": [],
                "domains_validated": [],
                "heterogeneous_evidence_verified": False
            },
            "conditional_rule": {
                "when_conditions": [f"In local project context '{project_id}'"],
                "then_approach": target_rule,
                "except_conditions": ["Unspecified boundary conditions"],
                "statement": f"WHEN local context is '{project_id}' → use approach '{target_rule}' EXCEPT when unconfirmed."
            },
            "status": "IN_PROGRESS",
            "created_at": now_iso,
            "updated_at": now_iso
        }

        self._save_record(record)
        return record

    # -------------------------------------------------------------------------
    # Stage 2: LOCAL_LESSON
    # -------------------------------------------------------------------------

    def advance_to_local_lesson(
        self,
        generalization_id: str,
        lesson_id: str,
        desired_behavior: str,
        diagnosis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Stage 2: Elevates an observation to a localized, project-specific lesson.
        """
        record = self.load_record(generalization_id)
        if record["stage"] not in ["OBSERVED", "LOCAL_LESSON"]:
            raise GeneralizationError(
                f"Cannot advance to LOCAL_LESSON from stage '{record['stage']}'."
            )

        if not record["evidence_summary"]["observations"]:
            raise PrematureGeneralizationError("Cannot form LOCAL_LESSON without at least one empirical observation.")

        obs = record["evidence_summary"]["observations"][0]
        project_id = obs["project_id"]

        record["stage"] = "LOCAL_LESSON"
        record["scope"] = self.STAGE_SCOPES["LOCAL_LESSON"]
        record["target_rule"] = desired_behavior
        record["conditional_rule"] = {
            "when_conditions": [f"Executing tasks within project '{project_id}'"],
            "then_approach": desired_behavior,
            "except_conditions": ["External research projects with different protocols"],
            "statement": f"WHEN working in project '{project_id}' → apply: {desired_behavior} EXCEPT when project guidelines specify otherwise."
        }
        record.setdefault("lineage", {})["source_lessons"] = [lesson_id]
        record["updated_at"] = datetime.now(timezone.utc).isoformat()

        self._save_record(record)
        return record

    # -------------------------------------------------------------------------
    # Stage 3: REPEATED_PATTERN
    # -------------------------------------------------------------------------

    def advance_to_repeated_pattern(
        self,
        generalization_id: str,
        new_observation: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Stage 3: Confirms that the behavior is a recurring pattern within the local context.
        Requires >= 2 distinct observations. Still strictly local (scope: LOCAL_PATTERN).
        """
        record = self.load_record(generalization_id)
        if record["stage"] not in ["LOCAL_LESSON", "REPEATED_PATTERN"]:
            raise GeneralizationError(
                f"Cannot advance to REPEATED_PATTERN from stage '{record['stage']}'."
            )

        if new_observation:
            record["evidence_summary"]["observations"].append(new_observation)

        if len(record["evidence_summary"]["observations"]) < 2:
            raise PrematureGeneralizationError(
                f"REPEATED_PATTERN requires at least 2 distinct observations within context. Found: {len(record['evidence_summary']['observations'])}"
            )

        record["stage"] = "REPEATED_PATTERN"
        record["scope"] = self.STAGE_SCOPES["REPEATED_PATTERN"]
        record["updated_at"] = datetime.now(timezone.utc).isoformat()

        self._save_record(record)
        return record

    # -------------------------------------------------------------------------
    # Stage 4: GENERALIZATION_CANDIDATE
    # -------------------------------------------------------------------------

    def advance_to_generalization_candidate(
        self,
        generalization_id: str,
        conditional_rule: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Stage 4: Formulates a structured candidate rule hypothesized to apply beyond local context.
        Requires conditional rule structure (WHEN / THEN / EXCEPT).
        """
        record = self.load_record(generalization_id)
        if record["stage"] not in ["REPEATED_PATTERN", "GENERALIZATION_CANDIDATE"]:
            raise GeneralizationError(
                f"Cannot advance to GENERALIZATION_CANDIDATE from stage '{record['stage']}'. Must reach REPEATED_PATTERN first."
            )

        # Validate conditional rule structure
        for req in ["when_conditions", "then_approach", "except_conditions", "statement"]:
            if req not in conditional_rule:
                raise GeneralizationError(f"Conditional rule missing required field: {req}")

        if not conditional_rule["when_conditions"] or not conditional_rule["except_conditions"]:
            raise GeneralizationError("Conditional rule must specify non-empty when_conditions and except_conditions.")

        record["stage"] = "GENERALIZATION_CANDIDATE"
        record["scope"] = self.STAGE_SCOPES["GENERALIZATION_CANDIDATE"]
        record["conditional_rule"] = conditional_rule
        record["target_rule"] = conditional_rule["then_approach"]
        record["updated_at"] = datetime.now(timezone.utc).isoformat()

        self._save_record(record)
        return record

    # -------------------------------------------------------------------------
    # Stage 5: CROSS_CONTEXT_VALIDATION
    # -------------------------------------------------------------------------

    def advance_to_cross_context_validation(
        self,
        generalization_id: str,
        context_evaluations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Stage 5: Validates candidate against heterogeneous contexts within the same domain.
        Requires at least 2 distinct contexts passing validation.
        """
        record = self.load_record(generalization_id)
        if record["stage"] not in ["GENERALIZATION_CANDIDATE", "CROSS_CONTEXT_VALIDATION"]:
            raise GeneralizationError(
                f"Cannot advance to CROSS_CONTEXT_VALIDATION from stage '{record['stage']}'. Must be a GENERALIZATION_CANDIDATE."
            )

        # Verify passing evaluations across distinct designs or sample size tiers
        passing_contexts = [c for c in context_evaluations if c.get("verdict") == "PASS"]
        distinct_designs = set(c.get("design") for c in passing_contexts if c.get("design"))
        distinct_sample_tiers = set(c.get("sample_size_tier") for c in passing_contexts if c.get("sample_size_tier"))

        if len(passing_contexts) < 2 or (len(distinct_designs) < 2 and len(distinct_sample_tiers) < 2):
            raise PrematureGeneralizationError(
                f"CROSS_CONTEXT_VALIDATION requires passing evaluations from at least 2 heterogeneous contexts. "
                f"Found {len(passing_contexts)} passing contexts with {len(distinct_designs)} distinct designs "
                f"and {len(distinct_sample_tiers)} distinct sample tiers."
            )

        record["stage"] = "CROSS_CONTEXT_VALIDATION"
        record["scope"] = self.STAGE_SCOPES["CROSS_CONTEXT_VALIDATION"]
        record["evidence_summary"]["contexts_validated"] = context_evaluations
        record["updated_at"] = datetime.now(timezone.utc).isoformat()

        self._save_record(record)
        return record

    # -------------------------------------------------------------------------
    # Stage 6: CROSS_DOMAIN_VALIDATION
    # -------------------------------------------------------------------------

    def advance_to_cross_domain_validation(
        self,
        generalization_id: str,
        domain_evaluations: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Stage 6: Validates candidate across heterogeneous research domains.
        Requires at least 2 distinct research domains passing validation.
        """
        record = self.load_record(generalization_id)
        if record["stage"] not in ["CROSS_CONTEXT_VALIDATION", "CROSS_DOMAIN_VALIDATION"]:
            raise GeneralizationError(
                f"Cannot advance to CROSS_DOMAIN_VALIDATION from stage '{record['stage']}'. Must complete CROSS_CONTEXT_VALIDATION first."
            )

        passing_domains = [d for d in domain_evaluations if d.get("verdict") == "PASS"]
        distinct_domains = set(d.get("domain") for d in passing_domains if d.get("domain"))

        if len(passing_domains) < 2 or len(distinct_domains) < 2:
            raise PrematureGeneralizationError(
                f"CROSS_DOMAIN_VALIDATION requires passing evaluations from at least 2 heterogeneous domains. "
                f"Found {len(passing_domains)} passing domains with {len(distinct_domains)} distinct domains: {distinct_domains}"
            )

        record["stage"] = "CROSS_DOMAIN_VALIDATION"
        record["scope"] = self.STAGE_SCOPES["CROSS_DOMAIN_VALIDATION"]
        record["evidence_summary"]["domains_validated"] = domain_evaluations
        record["evidence_summary"]["heterogeneous_evidence_verified"] = True
        record["updated_at"] = datetime.now(timezone.utc).isoformat()

        self._save_record(record)
        return record

    # -------------------------------------------------------------------------
    # Stage 7: PROMOTED_PRINCIPLE
    # -------------------------------------------------------------------------

    def promote_to_principle(
        self,
        generalization_id: str,
        author_or_gatekeeper: str = "digital-saber"
    ) -> Dict[str, Any]:
        """
        Stage 7: Promotes validated candidate to an authoritative foundational principle.
        Only allowed when both cross-context and cross-domain validations are satisfied.
        """
        record = self.load_record(generalization_id)
        if record["stage"] != "CROSS_DOMAIN_VALIDATION":
            raise PrematureGeneralizationError(
                f"Cannot promote to PROMOTED_PRINCIPLE from stage '{record['stage']}'. "
                f"Must successfully pass CROSS_DOMAIN_VALIDATION first."
            )

        ev_sum = record["evidence_summary"]
        if not ev_sum.get("heterogeneous_evidence_verified"):
            raise PrematureGeneralizationError(
                "Cannot promote to PROMOTED_PRINCIPLE without heterogeneous_evidence_verified == True."
            )

        now_iso = datetime.now(timezone.utc).isoformat()
        prn_id = f"PRN-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        record["stage"] = "PROMOTED_PRINCIPLE"
        record["scope"] = self.STAGE_SCOPES["PROMOTED_PRINCIPLE"]
        record["status"] = "PROMOTED"
        record["promoted_at"] = now_iso
        record["promoted_principle_id"] = prn_id
        record["updated_at"] = now_iso

        self._save_record(record)

        # Materialize principle in learning/knowledge/principles/
        principle_data = {
            "contract_version": "1.0.0",
            "knowledge_id": prn_id,
            "statement": record["conditional_rule"]["statement"],
            "scope": "CROSS_PROJECT_UNIVERSAL",
            "item_type": "principle",
            "generalization_stage": "PROMOTED_PRINCIPLE",
            "applicability": {
                "criteria": record["conditional_rule"]["when_conditions"]
            },
            "exclusions": record["conditional_rule"]["except_conditions"],
            "source_lessons": record.get("lineage", {}).get("source_lessons", ["LSN-GENERALIZED"]),
            "supporting_evaluations": [
                c.get("evidence_ref", "EVL-CTX") for c in ev_sum["contexts_validated"]
            ] + [
                d.get("evidence_ref", "EVL-DOM") for d in ev_sum["domains_validated"]
            ],
            "contradictions": [],
            "status": "ACCEPTED_ACTIVE",
            "version": "1.0.0",
            "updated_at": now_iso,
            "curated_by": author_or_gatekeeper
        }

        prn_path = os.path.join(self.principles_dir, f"{prn_id}.json")
        with open(prn_path, "w", encoding="utf-8") as f:
            json.dump(principle_data, f, indent=2)

        return record

    def check_scope_allowed(self, current_stage: str, requested_scope: str) -> None:
        """
        Enforces fail-closed scope gating:
        Raises PrematureGeneralizationError if an un-promoted stage attempts universal scope.
        """
        if requested_scope in ["CROSS_PROJECT_UNIVERSAL", "UNIVERSAL"]:
            if current_stage != "PROMOTED_PRINCIPLE":
                raise PrematureGeneralizationError(
                    f"Scope '{requested_scope}' is prohibited at stage '{current_stage}'. "
                    f"Must reach PROMOTED_PRINCIPLE through the 7-stage generalization ladder."
                )
