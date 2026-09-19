#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/academic_confidence_engine.py — AcademicSuite Evidence-Derived Confidence Engine

Implements Phase 26: Eliminates arbitrary confidence increments (confidence += 0.05)
and replaces them with an authoritative, evidence-derived formula:

confidence = (evidence_strength × independence × generalization × validation) - contradiction_penalty

Constitutional Directives:
- Directive 0: Radical Honesty & Epistemic Integrity.
- Directive 6: English-only ASCII file naming.
- Directive 12.1: Python scripts strictly as 'The Hands' (deterministic calculation).
- Directive 18: Single-view ceilings (<= 500 lines, <= 40,000 bytes).
- Directive 19: The Six-Part Functional Separation Invariant.
"""

import os
import sys
import math
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from contracts.contract_validator import validate_confidence_evidence


class AcademicConfidenceEngine:
    """
    Deterministic engine computing evidence-derived confidence for lessons,
    knowledge items, clusters, and principles across AcademicSuite.
    """

    TASK_QUALITY_WEIGHTS = {
        "HIGH_FIDELITY_BENCHMARK": 1.00,
        "EMPIRICAL_EXECUTION": 0.75,
        "DIAGNOSTIC_OBSERVATION": 0.50,
        "UNVERIFIED_HEURISTIC": 0.25,
        "UNSPECIFIED": 0.50
    }

    FAILURE_SEVERITY_WEIGHTS = {
        "CRITICAL": 1.00,
        "HIGH": 0.85,
        "MEDIUM": 0.70,
        "LOW": 0.50,
        "NEGLIGIBLE": 0.30,
        "UNSPECIFIED": 0.60
    }

    GENERALIZATION_STAGE_WEIGHTS = {
        "OBSERVED": 0.30,
        "LOCAL_LESSON": 0.40,
        "REPEATED_PATTERN": 0.55,
        "GENERALIZATION_CANDIDATE": 0.70,
        "CROSS_CONTEXT_VALIDATION": 0.85,
        "CROSS_DOMAIN_VALIDATION": 0.95,
        "PROMOTED_PRINCIPLE": 1.00
    }

    def __init__(self):
        pass

    def compute_confidence(self, factors: Dict[str, Any]) -> Dict[str, Any]:
        """
        Computes evidence-derived confidence score from explicit multi-factor dimensions:
        confidence = (evidence_strength * independence * generalization * validation) - contradiction_penalty
        """
        breakdown = factors.get("factors_breakdown", {})

        # 1. Evidence Strength (E_s in [0.10, 1.00])
        raw_quality = breakdown.get("task_quality", "UNSPECIFIED")
        q_weight = self.TASK_QUALITY_WEIGHTS.get(raw_quality, 0.50)

        raw_severity = breakdown.get("failure_severity", "UNSPECIFIED")
        s_weight = self.FAILURE_SEVERITY_WEIGHTS.get(raw_severity, 0.60)

        exp_count = max(1, breakdown.get("independent_experiences_count", 1))
        vol_weight = min(1.0, 0.40 + 0.20 * math.log(exp_count + 1))

        evidence_strength = min(1.0, max(0.10, 0.50 * q_weight + 0.30 * s_weight + 0.20 * vol_weight))

        # 2. Independence (I in [0.20, 1.00])
        unique_sessions = max(1, breakdown.get("unique_sessions_count", 1))
        if exp_count <= 1:
            independence = 0.70 if raw_quality == "HIGH_FIDELITY_BENCHMARK" else 0.50
        else:
            session_ratio = min(1.0, unique_sessions / exp_count)
            # Redundant observations from same session get penalized
            independence = min(1.0, max(0.20, 0.25 + 0.75 * session_ratio))

        # 3. Generalization (G in [0.10, 1.00])
        stage = breakdown.get("generalization_stage", "LOCAL_LESSON")
        stage_base = self.GENERALIZATION_STAGE_WEIGHTS.get(stage, 0.40)

        designs_count = breakdown.get("distinct_designs_count", 1)
        domains_count = breakdown.get("distinct_domains_count", 1)

        design_bonus = 0.05 if designs_count >= 2 else 0.0
        domain_bonus = 0.05 if domains_count >= 2 else 0.0

        generalization = min(1.0, max(0.10, stage_base + design_bonus + domain_bonus))

        # 4. Validation (V in [0.10, 1.00])
        reg_score = breakdown.get("regression_score")
        adv_score = breakdown.get("adversarial_score")
        held_score = breakdown.get("heldout_score")

        has_eval = any(s is not None for s in [reg_score, adv_score, held_score])
        if not has_eval:
            validation = 0.40  # Conservative unvalidated prior
        else:
            r = 0.40 if reg_score is None else float(reg_score)
            a = 0.40 if adv_score is None else float(adv_score)
            h = 0.40 if held_score is None else float(held_score)
            validation = min(1.0, max(0.10, 0.35 * r + 0.35 * a + 0.30 * h))

        # 5. Contradiction Penalty (C_p >= 0.0)
        contra_count = max(0, breakdown.get("contradictions_count", 0))
        regress_count = max(0, breakdown.get("regressions_count", 0))
        boundary_violation = bool(breakdown.get("boundary_violation", False))

        c_penalty = min(
            0.80,
            0.15 * contra_count + 0.25 * regress_count + (0.20 if boundary_violation else 0.0)
        )

        # Composite Multiplicative Formula
        raw_composite = (evidence_strength * independence * generalization * validation) - c_penalty
        computed_confidence = round(min(0.99, max(0.01, raw_composite)), 3)

        now_iso = datetime.now(timezone.utc).isoformat()
        complete_breakdown = {
            "independent_experiences_count": exp_count,
            "unique_sessions_count": unique_sessions,
            "distinct_designs_count": designs_count,
            "distinct_domains_count": domains_count,
            "generalization_stage": stage,
            "regression_score": reg_score if reg_score is not None else 0.40,
            "adversarial_score": adv_score if adv_score is not None else 0.40,
            "heldout_score": held_score if held_score is not None else 0.40,
            "contradictions_count": contra_count,
            "regressions_count": regress_count,
            "failure_severity": raw_severity,
            "task_quality": raw_quality
        }

        result = {
            "contract_version": "1.0.0",
            "computed_confidence": computed_confidence,
            "evidence_strength": round(evidence_strength, 3),
            "independence": round(independence, 3),
            "generalization": round(generalization, 3),
            "validation": round(validation, 3),
            "contradiction_penalty": round(c_penalty, 3),
            "formula": "(evidence_strength * independence * generalization * validation) - contradiction_penalty",
            "factors_breakdown": complete_breakdown,
            "evaluated_at": now_iso
        }

        return result

    def assess_lesson_confidence(
        self,
        lesson: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Assesses confidence for an individual newly-distilled lesson based on its originating evidence.
        """
        ctx = context or {}
        obs_fail = lesson.get("observed_failure", {})
        sev = obs_fail.get("severity") or ctx.get("severity", "MEDIUM")

        # Determine task quality
        trigger = lesson.get("trigger_source", "")
        if "BENCHMARK" in trigger or ctx.get("is_benchmark"):
            quality = "HIGH_FIDELITY_BENCHMARK"
        elif trigger in ["USER_FEEDBACK", "VALIDATOR_FAILURE"]:
            quality = "EMPIRICAL_EXECUTION"
        else:
            quality = "DIAGNOSTIC_OBSERVATION"

        factors = {
            "factors_breakdown": {
                "independent_experiences_count": 1,
                "unique_sessions_count": 1,
                "distinct_designs_count": 1,
                "distinct_domains_count": 1,
                "generalization_stage": lesson.get("generalization_stage", "LOCAL_LESSON"),
                "contradictions_count": 0,
                "regressions_count": 0,
                "failure_severity": sev.upper() if isinstance(sev, str) else "MEDIUM",
                "task_quality": quality
            }
        }

        return self.compute_confidence(factors)

    def assess_cluster_confidence(
        self,
        lesson_cluster: List[Dict[str, Any]],
        evaluations: Optional[List[Dict[str, Any]]] = None,
        stage: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Computes evidence-derived confidence when merging or consolidating a cluster of lessons.
        Replaces arbitrary `confidence += 0.05` with strict multi-factor analysis:
        - Checks true independence across sessions.
        - Checks context diversity across experimental designs.
        - Checks empirical evaluation records across the 3 suites.
        - Deducts penalties for active contradictions.
        """
        if not lesson_cluster:
            return self.compute_confidence({"factors_breakdown": {
                "independent_experiences_count": 0,
                "unique_sessions_count": 0,
                "distinct_designs_count": 0,
                "contradictions_count": 0
            }})

        eval_list = evaluations or []

        # Extract independent experiences and sessions
        exp_ids = set()
        session_ids = set()
        designs = set()
        domains = set()
        severities = []
        qualities = []

        for l in lesson_cluster:
            src_exp = l.get("source_experience_id")
            if src_exp:
                exp_ids.add(src_exp)
            else:
                exp_ids.add(l.get("lesson_id", id(l)))

            # Session / context discovery
            diag = l.get("diagnosis", {})
            sess = l.get("session_id") or diag.get("session_id") or l.get("project_id", "local_session")
            session_ids.add(sess)

            # Design & domain diversity
            app = l.get("applicability_conditions", [])
            for a in app:
                if any(k in a.lower() for k in ["rct", "pre-post", "longitudinal", "ancova", "cfa", "sem"]):
                    designs.add(a.lower())

            domain = l.get("domain") or diag.get("domain")
            if domain:
                domains.add(domain.lower())

            obs_fail = l.get("observed_failure", {})
            if obs_fail.get("severity"):
                severities.append(obs_fail.get("severity").upper())
            if l.get("task_quality"):
                qualities.append(l.get("task_quality"))

        # Also extract designs and domains from evaluation records
        for ev in eval_list:
            if isinstance(ev, dict):
                if ev.get("design"):
                    designs.add(str(ev.get("design")).lower())
                if ev.get("domain"):
                    domains.add(str(ev.get("domain")).lower())
                if ev.get("context_id"):
                    session_ids.add(str(ev.get("context_id")))

        # Determine stage
        if stage:
            top_stage = stage
        else:
            stages = [l.get("generalization_stage", "LOCAL_LESSON") for l in lesson_cluster]
            top_stage = max(stages, key=lambda s: self.GENERALIZATION_STAGE_WEIGHTS.get(s, 0.40))

        # Determine highest quality and severity
        top_quality = "EMPIRICAL_EXECUTION"
        if "HIGH_FIDELITY_BENCHMARK" in qualities or top_stage in ["CROSS_DOMAIN_VALIDATION", "PROMOTED_PRINCIPLE"]:
            top_quality = "HIGH_FIDELITY_BENCHMARK"
        elif not qualities and any(l.get("trigger_source") == "BENCHMARK" for l in lesson_cluster):
            top_quality = "HIGH_FIDELITY_BENCHMARK"

        top_sev = "MEDIUM"
        if "CRITICAL" in severities:
            top_sev = "CRITICAL"
        elif "HIGH" in severities or top_stage in ["CROSS_CONTEXT_VALIDATION", "CROSS_DOMAIN_VALIDATION", "PROMOTED_PRINCIPLE"]:
            top_sev = "HIGH"

        # Check evaluations for 3-category scores
        reg_score = None
        adv_score = None
        held_score = None
        for ev in eval_list:
            if isinstance(ev, dict):
                unblinded = ev.get("unblinded_comparison", ev)
                reg_res = unblinded.get("regression_result", {})
                if reg_res.get("fixes_original_mistake") or reg_res.get("verdict") == "PASS":
                    reg_score = 1.0
                elif reg_res.get("verdict") == "FAIL":
                    reg_score = 0.0

                adv_res = unblinded.get("adversarial_result", {})
                if adv_res.get("verdict") == "PASS":
                    adv_score = 1.0
                elif adv_res.get("verdict") == "FAIL":
                    adv_score = 0.0

                held_res = unblinded.get("heldout_result", {})
                if held_res.get("verdict") == "PASS":
                    held_score = 1.0
                elif held_res.get("verdict") == "FAIL":
                    held_score = 0.0

                cat = str(ev.get("category") or ev.get("suite") or "").upper()
                v = str(ev.get("verdict") or ev.get("status") or "").upper()
                if "REGRESSION" in cat and v == "PASS":
                    reg_score = 1.0
                elif "ADVERSARIAL" in cat and v == "PASS":
                    adv_score = 1.0
                elif "HELD" in cat and v == "PASS":
                    held_score = 1.0

        if eval_list and reg_score is None and adv_score is None and held_score is None:
            pass_count = sum(1 for e in eval_list if isinstance(e, dict) and (e.get("verdict") == "PASS" or e.get("status") == "PASS"))
            gen_pass_rate = pass_count / len(eval_list)
            reg_score = gen_pass_rate
            adv_score = gen_pass_rate
            held_score = gen_pass_rate

        # Check contradictions
        contra_count = 0
        for l in lesson_cluster:
            contra_count += len(l.get("contradictions", []))

        factors = {
            "factors_breakdown": {
                "independent_experiences_count": max(len(exp_ids), len(lesson_cluster)),
                "unique_sessions_count": max(1, len(session_ids)),
                "distinct_designs_count": max(1, len(designs)),
                "distinct_domains_count": max(1, len(domains)),
                "generalization_stage": top_stage,
                "regression_score": reg_score,
                "adversarial_score": adv_score,
                "heldout_score": held_score,
                "contradictions_count": contra_count,
                "regressions_count": 0,
                "failure_severity": top_sev,
                "task_quality": top_quality
            }
        }

        return self.compute_confidence(factors)

    def assess_generalization_confidence(
        self,
        gen_record: Dict[str, Any],
        evaluations: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Computes evidence-derived confidence for a generalization record at any of the 7 stages.
        """
        ev_summary = gen_record.get("evidence_summary", {})
        obs_list = ev_summary.get("observations", [])
        contexts = ev_summary.get("contexts_validated", [])
        domains = ev_summary.get("domains_validated", [])

        # Count distinct sessions, experiences, and designs
        session_set = set(o.get("project_id", "proj") for o in obs_list)
        for c in contexts:
            if c.get("context_id"):
                session_set.add(c.get("context_id"))
        for d in domains:
            if d.get("domain"):
                session_set.add(d.get("domain"))
        unique_sessions = len(session_set) or 1
        distinct_designs = len(set(c.get("design") for c in contexts if c.get("design"))) or 1
        distinct_domains = len(set(d.get("domain") for d in domains if d.get("domain"))) or 1
        total_exp_count = max(1, len(obs_list) + len(contexts) + len(domains))

        stage = gen_record.get("stage", "OBSERVED")

        reg_score = None
        adv_score = None
        held_score = None
        eval_list = evaluations or []
        for ev in eval_list:
            if isinstance(ev, dict):
                unblinded = ev.get("unblinded_comparison", ev)
                if unblinded.get("regression_result", {}).get("verdict") == "PASS":
                    reg_score = 1.0
                if unblinded.get("adversarial_result", {}).get("verdict") == "PASS":
                    adv_score = 1.0
                if unblinded.get("heldout_result", {}).get("verdict") == "PASS":
                    held_score = 1.0

                cat = str(ev.get("category") or ev.get("suite") or "").upper()
                v = str(ev.get("verdict") or ev.get("status") or "").upper()
                if "REGRESSION" in cat and v == "PASS":
                    reg_score = 1.0
                elif "ADVERSARIAL" in cat and v == "PASS":
                    adv_score = 1.0
                elif "HELD" in cat and v == "PASS":
                    held_score = 1.0

        if eval_list and reg_score is None and adv_score is None and held_score is None:
            pass_count = sum(1 for e in eval_list if isinstance(e, dict) and (e.get("verdict") == "PASS" or e.get("status") == "PASS"))
            gen_pass_rate = pass_count / len(eval_list)
            reg_score = gen_pass_rate
            adv_score = gen_pass_rate
            held_score = gen_pass_rate

        factors = {
            "factors_breakdown": {
                "independent_experiences_count": total_exp_count,
                "unique_sessions_count": unique_sessions,
                "distinct_designs_count": distinct_designs,
                "distinct_domains_count": distinct_domains,
                "generalization_stage": stage,
                "regression_score": reg_score,
                "adversarial_score": adv_score,
                "heldout_score": held_score,
                "contradictions_count": 0,
                "regressions_count": 0,
                "failure_severity": "HIGH",
                "task_quality": "HIGH_FIDELITY_BENCHMARK" if stage in ["CROSS_CONTEXT_VALIDATION", "CROSS_DOMAIN_VALIDATION", "PROMOTED_PRINCIPLE"] else "EMPIRICAL_EXECUTION"
            }
        }

        return self.compute_confidence(factors)
