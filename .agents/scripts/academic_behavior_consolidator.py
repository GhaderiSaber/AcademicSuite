#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/academic_behavior_consolidator.py — AcademicSuite Periodic Behavioral Consolidator

Implements periodic consolidation of learned behavior to prevent knowledge bloat,
prompt inflation, and contradictory instructions:

ACTIVE LESSONS
→ DUPLICATE DETECTION
→ CONTRADICTION DETECTION
→ GENERALIZATION
→ MERGING
→ OBSOLETE LESSON DETECTION
→ CANONICAL SKILL UPDATE

Constitutional Directives:
- Directive 0: Radical Honesty & Epistemic Integrity.
- Directive 6: Strict English-only ASCII file naming.
- Directive 12.1: Python scripts strictly as 'The Hands' (deterministic execution).
- Directive 18: Skill Modularity & Context Budget Standard (Single-View Invariant: < 500 lines, < 40k bytes).
- Contradiction Rule: When a new lesson contradicts an older lesson, NEVER silently overwrite it.
  Create a formal Contradiction Record with contextual applicability conditions.
- Strict Provenance Invariant: Merged lessons preserve lineage back to source lessons, experiences, and evaluations.
"""

import os
import sys
import re
import json
import uuid
import hashlib
import argparse
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

from scripts.academic_knowledge_manager import AcademicKnowledgeManager
from scripts.academic_generalization_engine import AcademicGeneralizationEngine, PrematureGeneralizationError
from scripts.academic_confidence_engine import AcademicConfidenceEngine
from scripts.academic_contradiction_engine import AcademicContradictionEngine, PrematureContradictionResolutionError
from contracts.contract_validator import (
    validate_lesson,
    validate_contradiction_record,
    validate_knowledge_item
)


class ConsolidationError(Exception):
    """Base exception for consolidation pipeline operations."""
    pass


# Known methodological tension pairs for deterministic contradiction detection
KNOWN_METHODOLOGICAL_CONFLICTS = [
    {
        "pattern_a": [r"\brepeated[- ]measures anova\b", r"\brm[- ]anova\b"],
        "pattern_b": [r"\blinear mixed model\b", r"\blmm\b", r"\bhlm\b"],
        "conflict_type": "MODEL_SPECIFICATION_CONFLICT",
        "description": "Conflict between RM-ANOVA and Linear Mixed Model (LMM) for multi-wave longitudinal data.",
        "condition_a": "Balanced cell sizes, complete follow-up data across all waves, and Mauchly sphericity holds.",
        "condition_b": "Subject attrition, missing longitudinal waves, unequal group allocations, or time-varying covariates."
    },
    {
        "pattern_a": [r"\bbaron (?:&|and) kenny\b", r"\bcausal steps\b"],
        "pattern_b": [r"\bpreacher (?:&|and) hayes\b", r"\bbootstrap mediation\b", r"\bbca\b"],
        "conflict_type": "MUTUALLY_EXCLUSIVE_METHODS",
        "description": "Conflict between Baron & Kenny causal steps and Preacher & Hayes bootstrap confidence intervals.",
        "condition_a": "Heuristic historical comparison or didactic demonstration only.",
        "condition_b": "Mandatory empirical mediation analysis with 5,000 bootstrap resamples and 95% BCa confidence intervals."
    },
    {
        "pattern_a": [r"\bmedian split\b", r"\bdichotomiz\b"],
        "pattern_b": [r"\bcontinuous interaction\b", r"\bjohnson[- ]neyman\b", r"\bmean[- ]center\b"],
        "conflict_type": "MUTUALLY_EXCLUSIVE_METHODS",
        "description": "Conflict between artificial dichotomization (median split) and continuous moderation analysis.",
        "condition_a": "Strictly prohibited in empirical inferential modeling due to severe variance loss.",
        "condition_b": "Continuous moderation modeling with mean-centering, simple slopes at -1 SD/Mean/+1 SD, and Johnson-Neyman regions."
    },
    {
        "pattern_a": [r"\blistwise deletion\b", r"\bcomplete case analysis\b"],
        "pattern_b": [r"\bfull information maximum likelihood\b", r"\bfiml\b", r"\bmultiple imputation\b"],
        "conflict_type": "INCOMPATIBLE_ASSUMPTIONS",
        "description": "Conflict between listwise deletion and modern missingness handling (FIML/Multiple Imputation).",
        "condition_a": "Permissible strictly when missingness is under 5% and Little's MCAR test is non-significant (p > .05).",
        "condition_b": "Missingness exceeds 5%, data is Missing at Random (MAR), or attrition occurs in longitudinal waves."
    },
    {
        "pattern_a": [r"\bparametric anova\b", r"\bstudent'?s t\b"],
        "pattern_b": [r"\bmann[- ]whitney\b", r"\bwilcoxon\b", r"\bnon[- ]parametric\b", r"\bbootstrap\b"],
        "conflict_type": "INCOMPATIBLE_ASSUMPTIONS",
        "description": "Conflict between parametric tests and non-parametric or bootstrap alternatives.",
        "condition_a": "Normality (Shapiro-Wilk p > .05) and homogeneity of variances (Levene p > .05) assumptions are satisfied.",
        "condition_b": "Parametric assumptions are violated in small-to-moderate samples, or ordinal Likert scores fail interval scaling."
    }
]


def tokenize_text(text: str) -> Set[str]:
    """Extracts normalized significant tokens (words >= 4 chars, ignoring common stopwords)."""
    if not text:
        return set()
    stopwords = {
        "this", "that", "with", "from", "were", "been", "have", "then", "must",
        "should", "would", "could", "also", "into", "onto", "upon", "each", "other",
        "under", "where", "which", "while", "during", "before", "after", "about",
        "between", "through", "against", "always", "never", "ensure", "verify"
    }
    words = re.findall(r"\b[a-zA-Z]{4,}\b", text.lower())
    return set(w for w in words if w not in stopwords)


def compute_jaccard_similarity(set_a: Set[str], set_b: Set[str]) -> float:
    """Computes Jaccard similarity coefficient between two token sets."""
    if not set_a or not set_b:
        return 0.0
    intersection = len(set_a.intersection(set_b))
    union = len(set_a.union(set_b))
    return round(intersection / union, 4) if union > 0 else 0.0


class AcademicBehaviorConsolidator:
    """
    Production consolidation engine managing periodic knowledge distillation:
    eliminates duplicates, reconciles contradictions with explicit applicability boundaries,
    merges clusters preserving complete provenance lineage, retires obsolete rules, and
    updates canonical skills while strictly enforcing Directive 18 single-view ceilings.
    """

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = os.path.abspath(base_dir or ROOT_DIR)
        cand_learning = os.path.join(self.base_dir, ".agents", "learning")
        self.learning_dir = cand_learning if os.path.isdir(cand_learning) else os.path.join(self.base_dir, "learning")
        self.knowledge_dir = os.path.join(self.learning_dir, "knowledge")
        self.lessons_dir = os.path.join(self.knowledge_dir, "lessons")
        self.contradictions_dir = os.path.join(self.knowledge_dir, "contradictions")
        self.snapshots_dir = os.path.join(self.learning_dir, "snapshots", "skills")
        self.skills_dir = os.path.join(self.base_dir, ".agents", "skills")

        self.knowledge_manager = AcademicKnowledgeManager(base_dir=self.base_dir)
        self.generalization_engine = AcademicGeneralizationEngine(base_dir=self.base_dir)
        self.confidence_engine = AcademicConfidenceEngine()
        self.contradiction_engine = AcademicContradictionEngine(base_dir=self.base_dir)

        self.quarantine_dir = os.path.join(self.learning_dir, "quarantine")
        self.telemetry_dir = os.path.join(self.learning_dir, "telemetry")
        self.error_log_path = os.path.join(self.telemetry_dir, "learning_errors.log")

        # Ensure directory structures exist
        os.makedirs(self.lessons_dir, exist_ok=True)
        os.makedirs(self.contradictions_dir, exist_ok=True)
        os.makedirs(self.snapshots_dir, exist_ok=True)
        os.makedirs(self.quarantine_dir, exist_ok=True)
        os.makedirs(self.telemetry_dir, exist_ok=True)

        # Directive 18 Thresholds
        self.MAX_SKILL_LINES = 500
        self.MAX_SKILL_BYTES = 40000
        self.WARNING_SKILL_LINES = 450

    def safe_load_json(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Safely loads a JSON file with fault isolation (ATK-17).
        If malformed or corrupt:
        - Isolates and moves corrupt artifact to learning/quarantine/
        - Appends structured diagnostic to learning/telemetry/learning_errors.log
        - Returns None to allow batch operations to proceed without failure.
        """
        if not os.path.isfile(file_path):
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, ValueError) as ex:
            # Fault isolation: quarantine malformed artifact
            os.makedirs(self.quarantine_dir, exist_ok=True)
            fname = os.path.basename(file_path)
            quarantine_path = os.path.join(self.quarantine_dir, f"CORRUPT_{uuid.uuid4().hex[:6]}_{fname}")
            try:
                import shutil
                shutil.move(file_path, quarantine_path)
            except Exception:
                pass

            # Structured error log
            try:
                os.makedirs(os.path.dirname(self.error_log_path), exist_ok=True)
                with open(self.error_log_path, "a", encoding="utf-8") as elf:
                    log_entry = {
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "error_type": "JSONDecodeError",
                        "original_path": file_path,
                        "quarantined_to": quarantine_path,
                        "exception": str(ex),
                        "component": "AcademicBehaviorConsolidator"
                    }
                    elf.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
            except Exception:
                pass

            return None
        except Exception:
            return None

    # -------------------------------------------------------------------------
    # Stage 1: Active Lessons Ingestion
    # -------------------------------------------------------------------------

    def ingest_active_lessons(
        self,
        skill: Optional[str] = None,
        capability: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Discovers all active lessons on disk.
        Strictly excludes RETIRED_OBSOLETE, SUPERSEDED, and REJECTED lessons.
        Safely isolates corrupt artifacts without halting batch processing (ATK-17).
        """
        active_lessons = []
        if not os.path.isdir(self.lessons_dir):
            return active_lessons

        target_cap = self.knowledge_manager.normalize_capability(capability)

        for fn in sorted(os.listdir(self.lessons_dir)):
            if not fn.endswith(".json") or fn == "index.jsonl":
                continue
            fp = os.path.join(self.lessons_dir, fn)
            lesson = self.safe_load_json(fp)
            if not lesson:
                continue

            status = lesson.get("status", "VALIDATED")
            # Filter out non-active statuses
            if status in ["RETIRED_OBSOLETE", "SUPERSEDED", "REJECTED", "DEPRECATED"]:
                continue

            # Skill match filter
            if skill:
                rel_skills = [s.lower() for s in lesson.get("related_skills", [])]
                if skill.lower() not in rel_skills and lesson.get("target_skill") != skill:
                    continue

            # Capability match filter
            if target_cap:
                item_cap = lesson.get("capability") or self.knowledge_manager.normalize_capability(lesson.get("domain"))
                if item_cap != target_cap and target_cap.lower() not in json.dumps(lesson).lower():
                    continue

            active_lessons.append(lesson)

        return active_lessons

    # -------------------------------------------------------------------------
    # Stage 2: Duplicate Detection
    # -------------------------------------------------------------------------

    def detect_duplicates(
        self,
        lessons: List[Dict[str, Any]],
        similarity_threshold: float = 0.55
    ) -> List[Dict[str, Any]]:
        """
        Identifies repeated and semantically equivalent lessons.
        Groups duplicate / near-duplicate lessons into consolidation clusters.
        """
        clusters = []
        assigned_ids = set()

        for i, lsn_a in enumerate(lessons):
            id_a = lsn_a.get("lesson_id")
            if id_a in assigned_ids:
                continue

            text_a = f"{lsn_a.get('desired_behavior', '')} {lsn_a.get('generalization', '')} {lsn_a.get('diagnosis', {}).get('what_happened', '')}"
            tokens_a = tokenize_text(text_a)
            defect_a = lsn_a.get("observed_failure", {}).get("defect_type")

            cluster_members = [lsn_a]

            for j in range(i + 1, len(lessons)):
                lsn_b = lessons[j]
                id_b = lsn_b.get("lesson_id")
                if id_b in assigned_ids:
                    continue

                text_b = f"{lsn_b.get('desired_behavior', '')} {lsn_b.get('generalization', '')} {lsn_b.get('diagnosis', {}).get('what_happened', '')}"
                tokens_b = tokenize_text(text_b)
                defect_b = lsn_b.get("observed_failure", {}).get("defect_type")

                sim = compute_jaccard_similarity(tokens_a, tokens_b)

                # Matching criteria: high token overlap, or same defect type with moderate overlap
                is_duplicate = False
                if sim >= similarity_threshold:
                    is_duplicate = True
                elif defect_a and defect_b and defect_a == defect_b and sim >= 0.40:
                    is_duplicate = True
                elif lsn_a.get("desired_behavior") and lsn_a.get("desired_behavior") == lsn_b.get("desired_behavior"):
                    is_duplicate = True

                if is_duplicate:
                    cluster_members.append(lsn_b)
                    assigned_ids.add(id_b)

            if len(cluster_members) > 1:
                assigned_ids.add(id_a)
                cluster_id = f"CLUST-DUP-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
                primary_skill = lsn_a.get("related_skills", ["academic-suite-orchestrator"])[0]
                clusters.append({
                    "cluster_id": cluster_id,
                    "target_skill": primary_skill,
                    "representative_rule": lsn_a.get("desired_behavior", ""),
                    "similarity_score": sim if 'sim' in locals() else 1.0,
                    "lessons": cluster_members
                })

        return clusters

    # -------------------------------------------------------------------------
    # Stage 3: Contradiction Detection
    # -------------------------------------------------------------------------

    def detect_contradictions(
        self,
        lessons: List[Dict[str, Any]],
        record_to_disk: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Identifies contradictory instructions across lessons for the same skill or capability.
        Strict Rule: NEVER silently overwrites! Creates an authoritative Contradiction Record
        with explicit, mutually exclusive contextual applicability conditions.
        """
        contradiction_records = []
        checked_pairs = set()

        for i, lsn_a in enumerate(lessons):
            id_a = lsn_a.get("lesson_id")
            text_a = f"{lsn_a.get('desired_behavior', '')} {lsn_a.get('statement', '')} {lsn_a.get('generalization', '')} {json.dumps(lsn_a.get('diagnosis', {}))}".lower()

            for j in range(i + 1, len(lessons)):
                lsn_b = lessons[j]
                id_b = lsn_b.get("lesson_id")
                pair_key = tuple(sorted([id_a, id_b]))
                if pair_key in checked_pairs:
                    continue
                checked_pairs.add(pair_key)

                text_b = f"{lsn_b.get('desired_behavior', '')} {lsn_b.get('statement', '')} {lsn_b.get('generalization', '')} {json.dumps(lsn_b.get('diagnosis', {}))}".lower()

                # 1. Evaluate against Known Methodological Conflict Signatures
                for conflict_def in KNOWN_METHODOLOGICAL_CONFLICTS:
                    matches_a_in_a = any(re.search(p, text_a) for p in conflict_def["pattern_a"])
                    matches_b_in_b = any(re.search(p, text_b) for p in conflict_def["pattern_b"])

                    matches_b_in_a = any(re.search(p, text_a) for p in conflict_def["pattern_b"])
                    matches_a_in_b = any(re.search(p, text_b) for p in conflict_def["pattern_a"])

                    if (matches_a_in_a and matches_b_in_b) or (matches_b_in_a and matches_a_in_b):
                        # Identified genuine contradiction!
                        target_skill = lsn_a.get("related_skills", ["statistical-data-analyst"])[0]
                        today_str = datetime.now(timezone.utc).strftime("%Y%m%d")
                        ctd_id = f"CTD-{today_str}-{uuid.uuid4().hex[:6].upper()}"

                        # Phase 27: Initial stage is strictly CONFLICT_DETECTED (never auto-resolved)
                        ctd_record = {
                            "contract_version": "1.0.0",
                            "contradiction_id": ctd_id,
                            "target_skill": target_skill,
                            "lesson_a_id": id_a,
                            "lesson_b_id": id_b,
                            "conflict_type": conflict_def["conflict_type"],
                            "description": conflict_def["description"],
                            "stage": "CONFLICT_DETECTED",
                            "status": "CONFLICT_DETECTED",
                            "reconciliation_strategy": "PENDING_HUMAN_RESOLUTION",
                            "detected_at": datetime.now(timezone.utc).isoformat()
                        }

                        # Validate schema
                        val_res = validate_contradiction_record(ctd_record)
                        if val_res["valid"]:
                            if record_to_disk:
                                self.knowledge_manager.add_contradiction_record(ctd_record)
                            contradiction_records.append(ctd_record)
                        break

                # 2. Check Direct Opposing Directives (e.g. "must do X" vs "do not do X")
                if "always" in text_a and "never" in text_b:
                    overlap = tokenize_text(text_a).intersection(tokenize_text(text_b))
                    if len(overlap) >= 3:
                        target_skill = lsn_a.get("related_skills", ["academic-suite-orchestrator"])[0]
                        today_str = datetime.now(timezone.utc).strftime("%Y%m%d")
                        ctd_id = f"CTD-{today_str}-{uuid.uuid4().hex[:6].upper()}"
                        opposing_record = {
                            "contract_version": "1.0.0",
                            "contradiction_id": ctd_id,
                            "target_skill": target_skill,
                            "lesson_a_id": id_a,
                            "lesson_b_id": id_b,
                            "conflict_type": "CONTRADICTORY_CONSTRAINTS",
                            "description": f"Direct tension between mandatory directive ({id_a}) and prohibitive directive ({id_b}).",
                            "stage": "CONFLICT_DETECTED",
                            "status": "CONFLICT_DETECTED",
                            "reconciliation_strategy": "PENDING_HUMAN_RESOLUTION",
                            "detected_at": datetime.now(timezone.utc).isoformat()
                        }
                        if validate_contradiction_record(opposing_record)["valid"]:
                            if record_to_disk:
                                self.knowledge_manager.add_contradiction_record(opposing_record)
                            contradiction_records.append(opposing_record)

        return contradiction_records

    def reconcile_contradiction_pipeline(
        self,
        contradiction_id: str,
        assumptions_a: List[str],
        assumptions_b: List[str],
        root_cause: str,
        evidence_for_a: List[str],
        evidence_for_b: List[str],
        condition_for_a: str,
        condition_for_b: str,
        test_result: Dict[str, Any],
        boundary_exceptions: Optional[List[str]] = None,
        conditional_rule: Optional[str] = None,
        divergence_analysis: Optional[str] = None,
        methodological_risk: Optional[str] = None,
        reconciled_by: str = "digital-saber"
    ) -> Dict[str, Any]:
        """
        Phase 27: Executes the mandatory 6-stage contradiction resolution lifecycle:
        CONFLICT_DETECTED -> CONFLICT_ANALYSIS -> EVIDENCE_COMPARISON ->
        CONDITION_IDENTIFICATION -> INDEPENDENT_TEST -> RESOLVED (or UNRESOLVED).
        """
        # 1. Advance to CONFLICT_ANALYSIS
        self.contradiction_engine.advance_to_conflict_analysis(
            contradiction_id=contradiction_id,
            assumptions_a=assumptions_a,
            assumptions_b=assumptions_b,
            root_cause=root_cause,
            methodological_risk=methodological_risk
        )

        # 2. Advance to EVIDENCE_COMPARISON
        self.contradiction_engine.advance_to_evidence_comparison(
            contradiction_id=contradiction_id,
            evidence_for_a=evidence_for_a,
            evidence_for_b=evidence_for_b,
            divergence_analysis=divergence_analysis
        )

        # 3. Advance to CONDITION_IDENTIFICATION
        self.contradiction_engine.advance_to_condition_identification(
            contradiction_id=contradiction_id,
            condition_for_a=condition_for_a,
            condition_for_b=condition_for_b,
            boundary_exceptions=boundary_exceptions,
            conditional_rule=conditional_rule
        )

        # 4. Advance to INDEPENDENT_TEST
        test_suite_id = test_result.get("test_suite_id", "TEST-INDEPENDENT-001")
        self.contradiction_engine.advance_to_independent_test(
            contradiction_id=contradiction_id,
            test_suite_id=test_suite_id,
            test_arms=test_result.get("test_arms")
        )

        # 5. Resolve with test evidence (or mark unresolved if test failed)
        return self.contradiction_engine.resolve_with_test_evidence(
            contradiction_id=contradiction_id,
            test_result=test_result,
            reconciled_by=reconciled_by
        )

    # -------------------------------------------------------------------------
    # Stage 4: Generalization
    # -------------------------------------------------------------------------

    def generalize_lessons(
        self,
        lesson_cluster: List[Dict[str, Any]],
        context_evaluations: Optional[List[Dict[str, Any]]] = None,
        domain_evaluations: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Elevates episodic, scenario-specific lessons through the 7-stage Generalization Progression Ladder.
        Multi-experience clusters without heterogeneous validation form a GENERALIZATION_CANDIDATE
        (scope: DOMAIN_WIDE or PROJECT_SPECIFIC).
        Elevation to CROSS_PROJECT_UNIVERSAL is strictly gated on heterogeneous cross-context and cross-domain validation.
        """
        experiences = set()
        for lsn in lesson_cluster:
            exp_id = lsn.get("source_experience_id")
            if exp_id:
                experiences.add(exp_id)

        rep_lesson = lesson_cluster[0] if lesson_cluster else {}
        desired = rep_lesson.get("desired_behavior", "")

        # Formulate synthesized general rule statement
        clean_rule = desired.rstrip(".")
        general_statement = (
            f"Consolidated Methodological Principle: {clean_rule}. "
            f"Enforce trade-off evaluation and verify prerequisite checks before output finalization."
        )

        # Aggregate applicability conditions and exclusions
        combined_applicability = []
        combined_exclusions = []
        for l in lesson_cluster:
            combined_applicability.extend(l.get("applicability_conditions", []))
            combined_exclusions.extend(l.get("exclusions", []))

        # Deduplicate while preserving order
        clean_applicability = list(dict.fromkeys(combined_applicability)) or ["All empirical quantitative and qualitative pipelines"]
        clean_exclusions = list(dict.fromkeys(combined_exclusions)) or ["Exploratory informal scratchpad analysis"]

        # Phase 25 Ladder Logic:
        # Default for multi-experience clusters without cross-validation is GENERALIZATION_CANDIDATE
        elevated_scope = "DOMAIN_WIDE"
        generalization_stage = "GENERALIZATION_CANDIDATE"

        if len(experiences) < 2 and len(lesson_cluster) < 2:
            elevated_scope = "PROJECT_SPECIFIC"
            generalization_stage = "LOCAL_LESSON"
        elif len(experiences) >= 2 and not (context_evaluations and domain_evaluations):
            # 2 experiences in the local context -> REPEATED_PATTERN / GENERALIZATION_CANDIDATE
            # NEVER CROSS_PROJECT_UNIVERSAL
            elevated_scope = "DOMAIN_WIDE"
            generalization_stage = "GENERALIZATION_CANDIDATE"
        elif context_evaluations and domain_evaluations:
            # Heterogeneous cross-context and cross-domain validation verified
            passing_ctx = [c for c in context_evaluations if c.get("verdict") == "PASS"]
            passing_dom = [d for d in domain_evaluations if d.get("verdict") == "PASS"]
            distinct_designs = set(c.get("design") for c in passing_ctx if c.get("design"))
            distinct_doms = set(d.get("domain") for d in passing_dom if d.get("domain"))
            if len(passing_ctx) >= 2 and len(distinct_designs) >= 2 and len(passing_dom) >= 2 and len(distinct_doms) >= 2:
                elevated_scope = "CROSS_PROJECT_UNIVERSAL"
                generalization_stage = "PROMOTED_PRINCIPLE"
            elif len(passing_ctx) >= 2 and len(distinct_designs) >= 2:
                elevated_scope = "DOMAIN_WIDE"
                generalization_stage = "CROSS_CONTEXT_VALIDATION"

        # Phase 26: Evidence-Derived Confidence Assessment
        all_evals = []
        if context_evaluations:
            all_evals.extend(context_evaluations)
        if domain_evaluations:
            all_evals.extend(domain_evaluations)

        confidence_report = self.confidence_engine.assess_cluster_confidence(
            lesson_cluster=lesson_cluster,
            evaluations=all_evals,
            stage=generalization_stage
        )
        confidence_score = confidence_report["computed_confidence"]

        return {
            "statement": general_statement,
            "scope": elevated_scope,
            "generalization_stage": generalization_stage,
            "applicability": clean_applicability,
            "exclusions": clean_exclusions,
            "confidence": confidence_score,
            "confidence_evidence": confidence_report
        }

    # -------------------------------------------------------------------------
    # Stage 5: Merging with Strict Provenance Lineage
    # -------------------------------------------------------------------------

    def merge_lessons(
        self,
        lesson_cluster: List[Dict[str, Any]],
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Merges a cluster of duplicate / related lessons into a single authoritative lesson.
        Preserves strict provenance:
          merged_lesson ← source_lessons ← source_experiences ← evaluations
        Marks all source lessons as SUPERSEDED.
        """
        if not lesson_cluster:
            raise ConsolidationError("Cannot merge empty lesson cluster.")

        today_str = datetime.now(timezone.utc).strftime("%Y%m%d")
        merged_id = f"LSN-CONSOLIDATED-{today_str}-{uuid.uuid4().hex[:6].upper()}"

        generalization = self.generalize_lessons(lesson_cluster)

        source_lesson_ids = [l["lesson_id"] for l in lesson_cluster]
        source_exp_ids = list(dict.fromkeys([
            l.get("source_experience_id") for l in lesson_cluster if l.get("source_experience_id")
        ]))

        supporting_eval_ids = []
        for l in lesson_cluster:
            supporting_eval_ids.extend(l.get("evidence", {}).get("supporting_report_ids", []))
        supporting_eval_ids = list(dict.fromkeys(supporting_eval_ids))

        target_skills = []
        for l in lesson_cluster:
            target_skills.extend(l.get("related_skills", []))
        target_skills = list(dict.fromkeys(target_skills)) or ["statistical-data-analyst"]

        target_agents_set = set()
        for l in lesson_cluster:
            if l.get("target_agent"):
                target_agents_set.add(l["target_agent"])
            for a in l.get("target_agents", []):
                target_agents_set.add(a)

        if not target_agents_set:
            primary_skill = target_skills[0] if target_skills else "statistical-data-analyst"
            from scripts.academic_two_stage_retriever import AcademicTwoStageRetriever
            target_agent = AcademicTwoStageRetriever.SKILL_TO_PRIMARY_AGENT.get(primary_skill, "academic-orchestrator")
            target_agents = [target_agent]
        else:
            target_agents = sorted(list(target_agents_set))
            target_agent = target_agents[0]

        now_iso = datetime.now(timezone.utc).isoformat()

        # Synthesize consolidated lesson contract
        merged_lesson = {
            "contract_version": "1.0.0",
            "lesson_id": merged_id,
            "lesson_type": "WHAT_NOT_TO_DO",
            "trigger_source": "RECURRING_MISTAKE",
            "source_experience_id": source_exp_ids[0] if source_exp_ids else "EXP-CONSOLIDATED",
            "diagnosis": {
                "what_happened": f"Consolidated {len(lesson_cluster)} redundant micro-lessons into a unified standard.",
                "behavior_caused_outcome": "Agent previously operated with fragmented micro-patches.",
                "what_should_have_happened": generalization["statement"],
                "rationale_why": "Consolidated higher-order rules prevent prompt bloat and reinforce epistemic consistency."
            },
            "applicability_conditions": generalization["applicability"],
            "exclusions": generalization["exclusions"],
            "desired_behavior": generalization["statement"],
            "generalization": generalization["statement"],
            "scope": generalization["scope"],
            "generalization_stage": generalization.get("generalization_stage", "GENERALIZATION_CANDIDATE"),
            "confidence": generalization["confidence"],
            "confidence_evidence": generalization.get("confidence_evidence"),
            "evidence": {
                "metric_or_check": "CONSOLIDATION_SYNTHESIS",
                "observed_value": f"Merged {len(lesson_cluster)} lessons",
                "threshold_value": "ZERO_DUPLICATES",
                "supporting_report_ids": supporting_eval_ids,
                "supporting_artifact_paths": []
            },
            "related_skills": target_skills,
            "target_agent": target_agent,
            "target_agents": target_agents,
            "is_active_behavior": True,
            "status": "VALIDATED",
            "created_at": now_iso,
            "derived_by": "AcademicBehaviorConsolidator",
            "provenance": {
                "source_lessons": source_lesson_ids,
                "source_experiences": source_exp_ids,
                "supporting_evaluations": supporting_eval_ids,
                "consolidated_at": now_iso
            }
        }

        # Validate consolidated lesson
        val_res = validate_lesson(merged_lesson)
        if not val_res["valid"]:
            raise ConsolidationError(f"Synthesized consolidated lesson violates schema: {val_res.get('errors')}")

        if not dry_run:
            # 1. Save merged lesson to disk
            merged_file = os.path.join(self.lessons_dir, f"{merged_id}.json")
            with open(merged_file, "w", encoding="utf-8") as f:
                json.dump(merged_lesson, f, indent=2, ensure_ascii=False)

            # 2. Mark source lessons as SUPERSEDED
            for lsn in lesson_cluster:
                src_id = lsn["lesson_id"]
                src_file = os.path.join(self.lessons_dir, f"{src_id}.json")
                if os.path.isfile(src_file):
                    try:
                        with open(src_file, "r", encoding="utf-8") as sf:
                            s_data = json.load(sf)
                        s_data["status"] = "SUPERSEDED"
                        s_data["superseded_by"] = merged_id
                        s_data["superseded_at"] = now_iso
                        with open(src_file, "w", encoding="utf-8") as sf:
                            json.dump(s_data, sf, indent=2, ensure_ascii=False)
                    except Exception:
                        pass

                # Graph relationship: source is superseded by merged
                self.knowledge_manager.link_items(
                    source_id=src_id,
                    target_id=merged_id,
                    relation_type="supersedes",
                    description=f"Consolidated into {merged_id}"
                )

        return merged_lesson

    # -------------------------------------------------------------------------
    # Stage 6: Obsolete Lesson Detection & Retirement
    # -------------------------------------------------------------------------

    def detect_obsolete_lessons(
        self,
        lessons: List[Dict[str, Any]],
        merged_source_ids: Set[str],
        dry_run: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Identifies lessons that are obsolete (e.g. superseded by merged rules or permanently fixed).
        Transitions their status to RETIRED_OBSOLETE with explicit reason and timestamp.
        Historical files remain on disk for permanent auditability.
        """
        retired_lessons = []
        now_iso = datetime.now(timezone.utc).isoformat()

        for lsn in lessons:
            lid = lsn.get("lesson_id")
            status = lsn.get("status", "VALIDATED")

            # Condition 1: Source lesson absorbed in a merge
            is_absorbed = lid in merged_source_ids
            # Condition 2: Marked superseded but status not yet formalized
            is_superseded = status == "SUPERSEDED" or bool(lsn.get("superseded_by"))

            if is_absorbed or is_superseded:
                retired_copy = dict(lsn)
                retired_copy["status"] = "RETIRED_OBSOLETE"
                retired_copy["obsolete_reason"] = (
                    f"Absorbed into consolidated rule {lsn.get('superseded_by', 'CONSOLIDATED_STANDARD')}."
                )
                retired_copy["retired_at"] = now_iso

                if not dry_run:
                    l_file = os.path.join(self.lessons_dir, f"{lid}.json")
                    if os.path.isfile(l_file):
                        try:
                            with open(l_file, "w", encoding="utf-8") as f:
                                json.dump(retired_copy, f, indent=2, ensure_ascii=False)
                        except Exception:
                            pass

                retired_lessons.append(retired_copy)

        return retired_lessons

    # -------------------------------------------------------------------------
    # Stage 7: Canonical Skill Update (Strict Directive 18 Ceilings)
    # -------------------------------------------------------------------------

    def update_canonical_skill(
        self,
        skill: str,
        consolidated_lessons: List[Dict[str, Any]],
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Updates the canonical SKILL.md for a skill to reflect consolidated learning:
        - Creates a rollback snapshot in learning/snapshots/skills/
        - Preserves strong exemplars and anti-patterns
        - Reduces redundant instructions
        - STRICT DIRECTIVE 18 COMPLIANCE:
          Hard single-view ceilings (max 500 lines, max 40,000 bytes).
          Never bloats SKILL.md; offloads detailed catalogs to references/learned_consolidations.md.
        """
        skill_dir = os.path.join(self.skills_dir, skill)
        skill_file = os.path.join(skill_dir, "SKILL.md")

        if not os.path.isfile(skill_file):
            return {
                "skill": skill,
                "status": "SKIPPED_NOT_FOUND",
                "message": f"Canonical skill file not found at {skill_file}"
            }

        with open(skill_file, "r", encoding="utf-8") as f:
            current_content = f.read()

        current_lines = current_content.splitlines()
        current_line_count = len(current_lines)
        current_byte_count = len(current_content.encode("utf-8"))

        # 1. Create Rollback Snapshot
        now_ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        snapshot_filename = f"{skill}_v{now_ts}.md"
        snapshot_path = os.path.join(self.snapshots_dir, snapshot_filename)

        if not dry_run:
            with open(snapshot_path, "w", encoding="utf-8") as f:
                f.write(current_content)

        # 2. Check Line Budget (< 500 lines limit)
        available_lines = self.MAX_SKILL_LINES - current_line_count
        should_offload_to_references = (available_lines < 30) or (current_line_count > self.WARNING_SKILL_LINES)

        # Formulate consolidated operational directives
        operational_directives = []
        for cl in consolidated_lessons:
            rule = cl.get("desired_behavior") or cl.get("generalization")
            if rule:
                clean_r = rule.strip().rstrip(".")
                operational_directives.append(f"- **Consolidated Principle**: {clean_r}.")

        # Deduplicate directives
        unique_directives = list(dict.fromkeys(operational_directives))[:5]

        # 3. Offload detailed references if approaching budget ceiling
        references_file = None
        if should_offload_to_references or len(consolidated_lessons) > 3:
            refs_dir = os.path.join(skill_dir, "references")
            os.makedirs(refs_dir, exist_ok=True)
            references_file = os.path.join(refs_dir, "learned_consolidations.md")

            ref_content = (
                f"# Learned Behavioral Consolidations for {skill}\n\n"
                f"Generated: {datetime.now(timezone.utc).isoformat()}\n\n"
                f"## 📚 Consolidated Methodological Principles\n\n"
            )
            for d in unique_directives:
                ref_content += f"{d}\n\n"

            ref_content += (
                "## 🏆 Preserved Exemplars & Anti-Patterns\n"
                "- Exemplars cataloged in `learning/knowledge/exemplars/`\n"
                "- Anti-patterns cataloged in `learning/knowledge/anti-patterns/`\n"
            )

            if not dry_run:
                with open(references_file, "w", encoding="utf-8") as rf:
                    rf.write(ref_content)

            # Insert a clean reference link into SKILL.md without bloating lines
            new_section = (
                "\n\n## 🧠 Active Learned Behavioral Invariants\n"
                "Before execution, observe consolidated standards:\n"
            )
            for d in unique_directives[:2]:
                new_section += f"{d}\n"
            new_section += f"- Detailed catalog: See [learned_consolidations.md](file://{os.path.relpath(references_file, self.base_dir)})\n"

        else:
            # Inline concise operational section
            new_section = (
                "\n\n## 🧠 Active Learned Behavioral Invariants\n"
                "Before execution, verify consolidated standards:\n"
            )
            for d in unique_directives:
                new_section += f"{d}\n"

        # Check if already present to avoid duplication
        if "## 🧠 Active Learned Behavioral Invariants" in current_content:
            # Replace existing section cleanly
            pattern = r"## 🧠 Active Learned Behavioral Invariants[\s\S]*?(?=\n## |\Z)"
            updated_content = re.sub(pattern, new_section.strip(), current_content)
        else:
            updated_content = current_content.rstrip() + new_section

        updated_line_count = len(updated_content.splitlines())
        updated_byte_count = len(updated_content.encode("utf-8"))

        # Verify Directive 18 hard ceilings
        if updated_line_count > self.MAX_SKILL_LINES or updated_byte_count > self.MAX_SKILL_BYTES:
            # Revert to snapshot in memory and enforce references offloading
            updated_content = current_content.rstrip() + (
                f"\n\n## 🧠 Active Learned Behavioral Invariants\n"
                f"- See consolidated guidelines in references/learned_consolidations.md (Directive 18).\n"
            )
            updated_line_count = len(updated_content.splitlines())
            updated_byte_count = len(updated_content.encode("utf-8"))

        if not dry_run:
            with open(skill_file, "w", encoding="utf-8") as f:
                f.write(updated_content)

        return {
            "skill": skill,
            "status": "UPDATED",
            "snapshot": snapshot_path,
            "references_file": references_file,
            "original_lines": current_line_count,
            "updated_lines": updated_line_count,
            "directive_18_compliant": (updated_line_count <= self.MAX_SKILL_LINES and updated_byte_count <= self.MAX_SKILL_BYTES)
        }

    # -------------------------------------------------------------------------
    # End-to-End Periodic Consolidation Cycle
    # -------------------------------------------------------------------------

    def run_periodic_consolidation(
        self,
        target_skill: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Executes the full 7-stage periodic consolidation pipeline:
        ACTIVE LESSONS → DUPLICATE DETECTION → CONTRADICTION DETECTION →
        GENERALIZATION → MERGING → OBSOLETE DETECTION → CANONICAL SKILL UPDATE
        """
        # 1. Ingest Active Lessons
        active_lessons = self.ingest_active_lessons(skill=target_skill)

        if not active_lessons:
            return {
                "status": "NO_ACTIVE_LESSONS",
                "message": "Zero active lessons eligible for consolidation.",
                "active_lessons_count": 0
            }

        # 2. Duplicate Detection
        duplicate_clusters = self.detect_duplicates(active_lessons)

        # 3. Contradiction Detection
        contradictions = self.detect_contradictions(active_lessons, record_to_disk=(not dry_run))

        # 4 & 5. Generalization & Merging
        merged_lessons = []
        absorbed_source_ids = set()

        for cluster in duplicate_clusters:
            merged = self.merge_lessons(cluster["lessons"], dry_run=dry_run)
            merged_lessons.append(merged)
            for l in cluster["lessons"]:
                absorbed_source_ids.add(l["lesson_id"])

        # 6. Obsolete Lesson Detection & Retirement
        retired_lessons = self.detect_obsolete_lessons(
            lessons=active_lessons,
            merged_source_ids=absorbed_source_ids,
            dry_run=dry_run
        )

        # 7. Canonical Skill Update
        skill_updates = []
        skills_to_update = [target_skill] if target_skill else list(set(
            l.get("related_skills", ["statistical-data-analyst"])[0] for l in merged_lessons
        ))

        for sk in skills_to_update:
            sk_lessons = [m for m in merged_lessons if sk in m.get("related_skills", [])]
            if sk_lessons or not target_skill:
                res = self.update_canonical_skill(sk, sk_lessons, dry_run=dry_run)
                skill_updates.append(res)

        # Calculate metrics
        initial_count = len(active_lessons)
        final_active_count = initial_count - len(absorbed_source_ids) + len(merged_lessons)
        reduction_pct = round(((initial_count - final_active_count) / max(1, initial_count)) * 100, 2)

        report = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "CONSOLIDATION_COMPLETED",
            "target_skill": target_skill or "ALL_SKILLS",
            "initial_active_lessons": initial_count,
            "final_active_lessons": max(1, final_active_count),
            "duplicates_detected": len(duplicate_clusters),
            "contradictions_detected": len(contradictions),
            "merged_clusters": len(merged_lessons),
            "obsolete_lessons_retired": len(retired_lessons),
            "canonical_skills_updated": len(skill_updates),
            "context_reduction_percent": max(0.0, reduction_pct),
            "merged_lesson_ids": [m["lesson_id"] for m in merged_lessons],
            "contradiction_ids": [c["contradiction_id"] for c in contradictions],
            "skill_update_details": skill_updates
        }

        # Save consolidation audit report
        if not dry_run:
            audit_file = os.path.join(
                self.knowledge_dir,
                f"consolidation_report_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
            )
            try:
                with open(audit_file, "w", encoding="utf-8") as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
            except Exception:
                pass

        return report


def main():
    parser = argparse.ArgumentParser(description="AcademicSuite Periodic Behavioral Consolidator")
    parser.add_argument("--skill", type=str, default=None, help="Target skill to consolidate")
    parser.add_argument("--dry-run", action="store_true", help="Simulate consolidation without writing to disk")
    parser.add_argument("--report", action="store_true", help="Output summary report in JSON format")
    args = parser.parse_args()

    consolidator = AcademicBehaviorConsolidator()
    result = consolidator.run_periodic_consolidation(target_skill=args.skill, dry_run=args.dry_run)

    print(json.dumps(result, indent=2, ensure_ascii=False))
AcademicConsolidationEngine = AcademicBehaviorConsolidator


if __name__ == "__main__":
    main()
