#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/academic_two_stage_retriever.py — AcademicSuite Two-Stage Knowledge Retrieval Engine

Implements Phase 29 Two-Stage Retrieval Architecture:
    Stage 1: Hard Filtering (Fail-Closed Structural Boundary Gate)
        - capability, domain, skill, task, failure type, scope, status
        - Dropped with explicit rejection rationale; zero semantic leakage.
    Stage 2: Semantic Ranking (Multi-Factor Scholarly Scoring)
        - relevance (deterministic metadata & tags)
        - context similarity (semantic & lexical token overlap)
        - evidence strength (empirical backing & benchmark fidelity)
        - recency (temporal decay relative to calendar anchor)
        - confidence (evidence-derived score from Phase 26)
        - contradiction penalty (deductions for active conflicts from Phase 27)

Strictly complies with Directive 18 (<= 500 lines, <= 40,000 bytes) and Directive 12.1.
"""

import os
import sys
import re
import json
import math
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Set

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from contracts.contract_validator import validate_knowledge_retrieval


class AcademicTwoStageRetriever:
    """Production Two-Stage Knowledge Retrieval Engine."""

    CANONICAL_CAPABILITIES = {
        "longitudinal-analysis",
        "mediation",
        "moderation",
        "SEM",
        "psychometrics",
        "chapter4",
        "chapter5",
        "evidence",
        "ancova",
        "regression",
        "data_cleaning",
        "methodology"
    }

    CAPABILITY_ALIASES = {
        "longitudinal": "longitudinal-analysis",
        "longitudinal_analysis": "longitudinal-analysis",
        "longitudinal-modmed": "longitudinal-analysis",
        "mediation-analysis": "mediation",
        "process-mediation": "mediation",
        "moderation-analysis": "moderation",
        "sem": "SEM",
        "structural-equation-modeling": "SEM",
        "cfa": "SEM",
        "psychometric": "psychometrics",
        "scale-validation": "psychometrics",
        "chapter-4": "chapter4",
        "chapter_4": "chapter4",
        "chapter-5": "chapter5",
        "chapter_5": "chapter5",
        "literature": "evidence",
        "literature_review": "evidence",
        "systematic-review": "evidence",
        "meta-analysis": "evidence",
        "data-cleaning": "data_cleaning",
        "data-curation": "data_cleaning"
    }

    # Cross-capability generic principles/rules
    CROSS_CAPABILITY_TAGS = {"cross-capability", "general_academic", "universal", "foundational"}

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = os.path.abspath(base_dir or ROOT_DIR)
        self.anchor_time = datetime(2026, 9, 19, 0, 0, 0, tzinfo=timezone.utc)

    def normalize_capability(self, capability: Optional[str]) -> Optional[str]:
        """Normalize capability name to canonical form."""
        if not capability:
            return None
        c_clean = capability.strip().lower()
        for canon in self.CANONICAL_CAPABILITIES:
            if canon.lower() == c_clean:
                return canon
        return self.CAPABILITY_ALIASES.get(c_clean, capability)

    # -------------------------------------------------------------------------
    # Stage 1: Hard Filtering
    # -------------------------------------------------------------------------

    def stage_1_hard_filter(
        self,
        items: List[Dict[str, Any]],
        query: Dict[str, Any]
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Executes fail-closed hard filtering across all structural dimensions:
        scope, capability, domain, skill, task, failure_type, status.
        """
        passed: List[Dict[str, Any]] = []
        pruned_details: List[Dict[str, Any]] = []
        pruned_counts: Dict[str, int] = {
            "scope": 0, "capability": 0, "domain": 0,
            "skill": 0, "task": 0, "failure_type": 0, "status": 0
        }

        target_cap = self.normalize_capability(query.get("capability"))
        target_domain = (query.get("domain") or "").strip().lower()
        target_skill = (query.get("skill") or "").strip().lower()
        target_task = (query.get("task") or "").strip().lower()
        target_fail = (query.get("failure_type") or "").strip().lower()
        project_id = query.get("project_id")
        include_superseded = bool(query.get("include_superseded", False))

        for item in items:
            item_id = str(item.get("lesson_id") or item.get("anti_pattern_id") or item.get("knowledge_id") or item.get("exemplar_id") or item.get("item_id") or "UNKNOWN")

            # 1. Status Gate
            status = str(item.get("status") or "").upper()
            if not include_superseded and status in ["RETIRED_OBSOLETE", "SUPERSEDED", "REJECTED", "DEPRECATED"]:
                pruned_counts["status"] += 1
                pruned_details.append({"item_id": item_id, "failed_dimension": "status", "reason": f"Status '{status}' is inactive."})
                continue

            # 2. Scope Containment Gate (ADR-014)
            scope = str(item.get("scope") or "domain").lower()
            item_proj = item.get("project_id") or item.get("context", {}).get("project_id") or item.get("metadata", {}).get("project_id")
            is_proj_scoped = scope in ["project", "local_project", "global-in-project", "project_specific", "project-specific"] or bool(item_proj)
            if is_proj_scoped:
                if not project_id or (item_proj and item_proj != project_id):
                    pruned_counts["scope"] += 1
                    pruned_details.append({"item_id": item_id, "failed_dimension": "scope", "reason": f"Project-scoped item '{item_proj}' does not match query '{project_id}'."})
                    continue

            # 3. Capability Boundary Gate
            if target_cap:
                item_cap = self.normalize_capability(item.get("capability") or item.get("target_capability"))
                rel_caps = [self.normalize_capability(c) for c in item.get("related_capabilities", [])]
                item_tags = set(t.lower() for t in item.get("tags", []))
                is_cross = bool(item_tags.intersection(self.CROSS_CAPABILITY_TAGS)) or scope in ["cross-project", "global-in-project"] or item.get("item_type") == "principle"
                is_general = (item_cap in ["general_academic", "universal", "foundational", None]) and (is_cross or item_cap is None)

                if item_cap and item_cap != target_cap and target_cap not in rel_caps and not is_general:
                    pruned_counts["capability"] += 1
                    pruned_details.append({"item_id": item_id, "failed_dimension": "capability", "reason": f"Capability '{item_cap}' conflicts with target '{target_cap}'."})
                    continue

            # 4. Domain Boundary Gate
            if target_domain:
                item_dom = str(item.get("domain") or "").strip().lower()
                if item_dom and item_dom != "general" and item_dom != "cross-domain":
                    # Check mutual exclusion between quantitative and qualitative
                    if ("qualitative" in target_domain and "quantitative" in item_dom) or \
                       ("quantitative" in target_domain and "qualitative" in item_dom):
                        pruned_counts["domain"] += 1
                        pruned_details.append({"item_id": item_id, "failed_dimension": "domain", "reason": f"Mutually exclusive domain '{item_dom}' vs target '{target_domain}'."})
                        continue
                    if target_domain not in item_dom and item_dom not in target_domain:
                        pruned_counts["domain"] += 1
                        pruned_details.append({"item_id": item_id, "failed_dimension": "domain", "reason": f"Domain '{item_dom}' does not match target '{target_domain}'."})
                        continue

            # 5. Skill Boundary Gate
            if target_skill:
                item_skill = str(item.get("target_skill") or item.get("skill") or "").strip().lower()
                rel_skills = [s.lower() for s in item.get("related_skills", [])]
                app_skills = [s.lower() for s in item.get("applicability", {}).get("target_skills", [])]
                all_skills = set([item_skill] + rel_skills + app_skills) - {""}
                if all_skills and target_skill not in all_skills and not any(target_skill in s for s in all_skills):
                    pruned_counts["skill"] += 1
                    pruned_details.append({"item_id": item_id, "failed_dimension": "skill", "reason": f"Item skills {list(all_skills)} do not match target '{target_skill}'."})
                    continue

            # 6. Task Boundary Gate
            if target_task:
                item_task = str(item.get("task_type") or item.get("task") or "").strip().lower()
                app_tasks = [t.lower() for t in item.get("applicability", {}).get("tasks", [])]
                if item_task and item_task not in ["general_task", "general", "all"] and target_task not in item_task and item_task not in target_task and target_task not in app_tasks:
                    pruned_counts["task"] += 1
                    pruned_details.append({"item_id": item_id, "failed_dimension": "task", "reason": f"Item task '{item_task}' incompatible with target '{target_task}'."})
                    continue

            # 7. Failure Type Gate (for defect/anti-pattern screening)
            if target_fail:
                obs_fail = item.get("observed_failure", {})
                f_types = [
                    str(item.get("failure_type") or "").lower(),
                    str(obs_fail.get("defect_type") or "").lower(),
                    str(item.get("defect_type") or "").lower(),
                    str(item.get("category") or "").lower()
                ]
                f_types = [f for f in f_types if f]
                if f_types and not any(target_fail in f or f in target_fail for f in f_types):
                    pruned_counts["failure_type"] += 1
                    pruned_details.append({"item_id": item_id, "failed_dimension": "failure_type", "reason": f"Failure types {f_types} do not match target '{target_fail}'."})
                    continue

            passed.append(item)

        filter_meta = {
            "candidates_evaluated": len(items),
            "passed_count": len(passed),
            "pruned_count": len(items) - len(passed),
            "pruned_by_dimension": pruned_counts,
            "pruned_details": pruned_details
        }
        return passed, filter_meta

    # -------------------------------------------------------------------------
    # Stage 2: Semantic Ranking
    # -------------------------------------------------------------------------

    def stage_2_rank(
        self,
        candidates: List[Dict[str, Any]],
        query: Dict[str, Any],
        active_contradictions: Optional[List[Dict[str, Any]]] = None
    ) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Computes multi-factor scholarly ranking across the 6 dimensions:
        relevance (0.25), context_similarity (0.25), evidence_strength (0.15),
        recency (0.10), confidence (0.25) minus contradiction_penalty.
        """
        ranked_scores: List[Dict[str, Any]] = []
        active_ctds = active_contradictions or []

        # Disputed lesson IDs from active contradictions
        disputed_ids = set()
        for c in active_ctds:
            status = c.get("status")
            if status in ["CONFLICT_DETECTED", "CONFLICT_ANALYSIS", "UNRESOLVED"]:
                if c.get("lesson_a_id"):
                    disputed_ids.add(c["lesson_a_id"])
                if c.get("lesson_b_id"):
                    disputed_ids.add(c["lesson_b_id"])
                if c.get("contradiction_id"):
                    disputed_ids.add(c["contradiction_id"])

        for item in candidates:
            item_id = str(item.get("lesson_id") or item.get("anti_pattern_id") or item.get("knowledge_id") or item.get("exemplar_id") or item.get("item_id") or "UNKNOWN")
            itype = str(item.get("item_type") or ("lesson" if "lesson_id" in item else "anti_pattern" if "anti_pattern_id" in item else "knowledge_item"))

            s_rel = self._compute_relevance(item, query)
            s_sim = self._compute_context_similarity(item, query)
            s_ev = self._compute_evidence_strength(item)
            s_rec = self._compute_recency(item)
            s_conf = self._compute_confidence(item)
            p_ctd = self._compute_contradiction_penalty(item_id, item, disputed_ids)

            # Composite scholarly score
            final_score = round(
                (0.25 * s_rel) +
                (0.25 * s_sim) +
                (0.15 * s_ev) +
                (0.10 * s_rec) +
                (0.25 * s_conf) -
                p_ctd,
                4
            )

            score_record = {
                "item_id": item_id,
                "item_type": itype,
                "final_score": final_score,
                "relevance_score": s_rel,
                "similarity_score": s_sim,
                "evidence_strength_score": s_ev,
                "recency_score": s_rec,
                "confidence_score": s_conf,
                "contradiction_penalty": p_ctd,
                "_item": item
            }
            ranked_scores.append(score_record)

        # Sort descending by final score
        ranked_scores.sort(key=lambda x: x["final_score"], reverse=True)

        ranking_meta = {
            "ranked_candidates_count": len(ranked_scores),
            "candidates_scores": [
                {k: v for k, v in r.items() if k != "_item"}
                for r in ranked_scores
            ]
        }

        results = [r["_item"] for r in ranked_scores]
        return results, ranking_meta

    # -------------------------------------------------------------------------
    # Dimension Computations
    # -------------------------------------------------------------------------

    def _compute_relevance(self, item: Dict[str, Any], query: Dict[str, Any]) -> float:
        """Deterministic metadata relevance: tags overlap, exact skills, status."""
        score = 0.50
        tags_query = set(t.lower() for t in query.get("tags", []))
        item_tags = set(t.lower() for t in item.get("tags", []))
        if tags_query and item_tags:
            overlap = len(tags_query.intersection(item_tags))
            score += min(0.30, overlap * 0.10)

        # Skill match bonus
        q_skill = (query.get("skill") or "").lower()
        if q_skill and q_skill in str(item.get("related_skills", [])).lower():
            score += 0.10

        # Status bonus
        st = str(item.get("status") or "").upper()
        if st in ["ACCEPTED_ACTIVE", "VALIDATED"]:
            score += 0.10

        return min(1.0, max(0.0, round(score, 3)))

    def _compute_context_similarity(self, item: Dict[str, Any], query: Dict[str, Any]) -> float:
        """Semantic & lexical token similarity between query text/context and item body."""
        query_text = " ".join(filter(None, [
            query.get("prompt_text"),
            query.get("task"),
            query.get("task_description"),
            query.get("capability")
        ])).lower()

        if not query_text:
            return 0.50

        # Extract text representations from candidate
        diag = item.get("diagnosis", {})
        item_text = " ".join(filter(None, [
            item.get("statement"),
            item.get("desired_behavior"),
            item.get("generalization"),
            item.get("defective_pattern"),
            item.get("corrective_remedy"),
            item.get("why_exemplary"),
            item.get("description"),
            diag.get("what_happened"),
            diag.get("rationale_why")
        ])).lower()

        if not item_text:
            return 0.40

        # Tokenize words (alphanumeric >= 3 chars)
        q_tokens = set(re.findall(r"\b[a-z0-9_]{3,}\b", query_text))
        i_tokens = set(re.findall(r"\b[a-z0-9_]{3,}\b", item_text))

        if not q_tokens or not i_tokens:
            return 0.40

        # Jaccard + Dice overlap
        intersection = len(q_tokens.intersection(i_tokens))
        union = len(q_tokens.union(i_tokens))
        jaccard = intersection / union if union > 0 else 0.0

        # Academic keyword weighting
        academic_salient = {"bootstrap", "mediation", "moderation", "sem", "cfa", "ancova", "regression", "levene", "shapiro", "vif", "omega", "alpha", "mcar"}
        salient_overlap = len(q_tokens.intersection(i_tokens).intersection(academic_salient))
        salient_bonus = min(0.30, salient_overlap * 0.10)

        sim_score = min(1.0, max(0.10, round(jaccard * 1.5 + salient_bonus + 0.20, 3)))
        return sim_score

    def _compute_evidence_strength(self, item: Dict[str, Any]) -> float:
        """Empirical backing from Phase 26 evidence decomposition."""
        ce = item.get("confidence_evidence", {})
        if "evidence_strength" in ce and isinstance(ce["evidence_strength"], (int, float)):
            return min(1.0, max(0.10, float(ce["evidence_strength"])))

        ev = item.get("evidence", {})
        reps = ev.get("supporting_report_ids", [])
        evals = item.get("supporting_evaluations", [])
        obs = ev.get("observation_count", len(reps) + len(evals))

        if obs >= 5:
            return 0.90
        elif obs >= 2:
            return 0.75
        elif obs >= 1:
            return 0.60
        return 0.45

    def _compute_recency(self, item: Dict[str, Any]) -> float:
        """Temporal decay relative to anchor (2026-09-19)."""
        ts_str = item.get("updated_at") or item.get("created_at")
        if not ts_str:
            return 0.50
        try:
            # Handle ISO timestamps
            dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            diff_days = max(0.0, (self.anchor_time - dt).total_seconds() / 86400.0)
            # Exponential decay: lambda = 0.005 (~half-life of 140 days)
            rec = math.exp(-0.005 * diff_days)
            return min(1.0, max(0.10, round(rec, 3)))
        except Exception:
            return 0.50

    def _compute_confidence(self, item: Dict[str, Any]) -> float:
        """Evidence-derived confidence from Phase 26."""
        conf = item.get("confidence")
        if conf is not None and isinstance(conf, (int, float)):
            return min(1.0, max(0.01, float(conf)))
        return 0.50

    def _compute_contradiction_penalty(self, item_id: str, item: Dict[str, Any], disputed_ids: Set[str]) -> float:
        """Deductions for active conflicts under Phase 27."""
        if item_id in disputed_ids:
            return 0.35
        # If item itself references active unresolved contradictions
        active_ctds = [c for c in item.get("contradictions", []) if isinstance(c, dict) and c.get("status") in ["CONFLICT_DETECTED", "UNRESOLVED"]]
        if active_ctds:
            return 0.25
        return 0.0

    # -------------------------------------------------------------------------
    # Unified Public API
    # -------------------------------------------------------------------------

    def retrieve(
        self,
        items: List[Dict[str, Any]],
        query: Dict[str, Any],
        active_contradictions: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Executes full Phase 29 Two-Stage Retrieval pipeline and validates output contract.
        """
        filtered_candidates, stage_1_meta = self.stage_1_hard_filter(items, query)
        ranked_results, stage_2_meta = self.stage_2_rank(filtered_candidates, query, active_contradictions)

        limit = query.get("limit", 20)
        final_results = ranked_results[:limit]

        retrieval_record = {
            "contract_version": "1.0.0",
            "retrieval_id": f"RET-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}",
            "query": query,
            "stage_1_filtering": stage_1_meta,
            "stage_2_ranking": stage_2_meta,
            "results": final_results,
            "retrieved_at": datetime.now(timezone.utc).isoformat()
        }

        # Contract validation
        val = validate_knowledge_retrieval(retrieval_record)
        if not val["valid"]:
            raise ValueError(f"Retrieval record contract invalid: {val.get('errors')}")

        return retrieval_record
