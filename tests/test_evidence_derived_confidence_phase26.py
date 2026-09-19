#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_evidence_derived_confidence_phase26.py — Phase 26 Evidence-Derived Confidence Test Suite

Validates that confidence is mathematically derived from explicit evidence factors:
  confidence = (evidence_strength * independence * generalization * validation) - contradiction_penalty

Proves:
1. Merging identical lessons without new evidence does NOT arbitrarily increment confidence (confidence += 0.05 is dead).
2. Independence factor rewards multi-session variety and penalizes single-session repeats.
3. Context diversity across experimental designs directly boosts the generalization factor.
4. The 3 mandatory suites (Regression, Adversarial, Held-out) deterministically drive the validation factor.
5. Active contradictions and baseline regressions inflict explicit mathematical deductions.
6. Task quality (high-fidelity benchmark) and failure severity calibrate evidence strength.
7. All confidence payloads conform strictly to confidence_evidence.schema.json.
8. The 7-stage Generalization Ladder drives monotonic confidence progression as evidence accumulates.
"""

import os
import sys
import shutil
import tempfile
import unittest
from datetime import datetime, timezone

# Ensure project root is in sys.path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from contracts.contract_validator import (
    validate_confidence_evidence,
    validate_lesson,
    validate_generalization_lifecycle
)
from scripts.academic_confidence_engine import AcademicConfidenceEngine
from scripts.academic_behavior_consolidator import AcademicBehaviorConsolidator
from scripts.academic_generalization_engine import AcademicGeneralizationEngine
from scripts.academic_lesson_distiller import AcademicLessonDistiller


class TestEvidenceDerivedConfidencePhase26(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="agy_test_confidence_p26_")
        self.engine = AcademicConfidenceEngine()
        self.consolidator = AcademicBehaviorConsolidator(base_dir=self.test_dir)
        self.gen_engine = AcademicGeneralizationEngine(base_dir=self.test_dir)
        self.distiller = AcademicLessonDistiller(project_root=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _sample_lesson(self, lesson_id: str, desc: str, session: str = "sess-1", exp_id: str = "EXP-1"):
        return {
            "contract_version": "1.0.0",
            "lesson_id": lesson_id,
            "lesson_type": "WHAT_NOT_TO_DO",
            "trigger_source": "USER_FEEDBACK",
            "source_experience_id": exp_id,
            "session_id": session,
            "diagnosis": {
                "what_happened": desc,
                "why": "Methodological precision requirement"
            },
            "applicability_conditions": [
                "ANCOVA baseline covariates in RCT designs"
            ],
            "exclusions": [
                "Observational designs without random assignment"
            ],
            "desired_behavior": "Always test regression slope homogeneity prior to ANCOVA.",
            "generalization": "Parametric baseline adjustments require prerequisite assumption checking.",
            "scope": "DOMAIN_WIDE",
            "generalization_stage": "LOCAL_LESSON",
            "confidence": 0.50,
            "evidence": {
                "metric_or_check": "SLOPE_HOMOGENEITY",
                "observed_value": "INTERACTION_P_LT_05",
                "threshold_value": "INTERACTION_P_GE_05"
            },
            "related_skills": ["assumption-testing"],
            "is_active_behavior": False,
            "status": "VALIDATED",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "derived_by": "AcademicLessonDistiller"
        }

    # -------------------------------------------------------------------------
    # Test 1: Proof that `confidence += 0.05` is eliminated
    # -------------------------------------------------------------------------
    def test_01_confidence_plus_point_zero_five_is_dead(self):
        """Merging duplicate lessons from the same session without evaluations MUST NOT increment confidence."""
        l1 = self._sample_lesson("LSN-01", "Covariate slope check omitted", session="sess-1", exp_id="EXP-1")
        l2 = self._sample_lesson("LSN-02", "Covariate slope check omitted", session="sess-1", exp_id="EXP-2")

        # In the old flawed architecture: min(0.99, max(0.5, 0.5) + 0.05) -> 0.55
        # In evidence-derived architecture: unvalidated candidate from same session has low confidence (~0.05 - 0.20)
        res = self.consolidator.generalize_lessons([l1, l2])

        self.assertIn("confidence", res)
        self.assertIn("confidence_evidence", res)
        conf_report = res["confidence_evidence"]

        # Confidence is evidence-derived, not heuristically bumped
        self.assertNotEqual(res["confidence"], 0.55)
        self.assertLess(res["confidence"], 0.30)
        self.assertEqual(conf_report["validation"], 0.40)  # Conservative unvalidated prior

        val_res = validate_confidence_evidence(conf_report)
        self.assertTrue(val_res["valid"], f"Schema validation failed: {val_res.get('errors')}")

    # -------------------------------------------------------------------------
    # Test 2: Independence Factor Scaling
    # -------------------------------------------------------------------------
    def test_02_independence_factor_penalizes_same_session_repetition(self):
        """Distinct sessions provide genuine independence; same-session repeats are penalized."""
        # Case A: 5 observations, all in 1 session
        single_sess_factors = {
            "factors_breakdown": {
                "independent_experiences_count": 5,
                "unique_sessions_count": 1,
                "distinct_designs_count": 1,
                "distinct_domains_count": 1,
                "generalization_stage": "LOCAL_LESSON",
                "task_quality": "EMPIRICAL_EXECUTION",
                "failure_severity": "MEDIUM"
            }
        }
        res_single = self.engine.compute_confidence(single_sess_factors)

        # Case B: 5 observations across 5 distinct sessions
        multi_sess_factors = {
            "factors_breakdown": {
                "independent_experiences_count": 5,
                "unique_sessions_count": 5,
                "distinct_designs_count": 1,
                "distinct_domains_count": 1,
                "generalization_stage": "LOCAL_LESSON",
                "task_quality": "EMPIRICAL_EXECUTION",
                "failure_severity": "MEDIUM"
            }
        }
        res_multi = self.engine.compute_confidence(multi_sess_factors)

        self.assertLess(res_single["independence"], res_multi["independence"])
        self.assertLess(res_single["computed_confidence"], res_multi["computed_confidence"])
        self.assertEqual(res_multi["independence"], 1.00)

    # -------------------------------------------------------------------------
    # Test 3: Context Diversity Boosts Generalization Factor
    # -------------------------------------------------------------------------
    def test_03_context_diversity_boosts_generalization(self):
        """Testing across multiple experimental designs awards a context diversity bonus."""
        single_design = {
            "factors_breakdown": {
                "independent_experiences_count": 3,
                "unique_sessions_count": 3,
                "distinct_designs_count": 1,
                "distinct_domains_count": 1,
                "generalization_stage": "GENERALIZATION_CANDIDATE"
            }
        }
        multi_design = {
            "factors_breakdown": {
                "independent_experiences_count": 3,
                "unique_sessions_count": 3,
                "distinct_designs_count": 3,
                "distinct_domains_count": 1,
                "generalization_stage": "GENERALIZATION_CANDIDATE"
            }
        }

        res_single = self.engine.compute_confidence(single_design)
        res_multi = self.engine.compute_confidence(multi_design)

        self.assertGreater(res_multi["generalization"], res_single["generalization"])
        self.assertGreater(res_multi["computed_confidence"], res_single["computed_confidence"])

    # -------------------------------------------------------------------------
    # Test 4: Three Suites Drive Validation Factor
    # -------------------------------------------------------------------------
    def test_04_three_suites_drive_validation_factor(self):
        """Validation factor is governed by performance on Regression, Adversarial, and Held-out suites."""
        # Unvalidated prior
        unvalidated = self.engine.compute_confidence({
            "factors_breakdown": {
                "independent_experiences_count": 2,
                "unique_sessions_count": 2,
                "generalization_stage": "GENERALIZATION_CANDIDATE"
            }
        })
        self.assertEqual(unvalidated["validation"], 0.40)

        # All 3 suites passing
        all_pass = self.engine.compute_confidence({
            "factors_breakdown": {
                "independent_experiences_count": 2,
                "unique_sessions_count": 2,
                "generalization_stage": "GENERALIZATION_CANDIDATE",
                "regression_score": 1.0,
                "adversarial_score": 1.0,
                "heldout_score": 1.0
            }
        })
        self.assertEqual(all_pass["validation"], 1.00)
        self.assertGreater(all_pass["computed_confidence"], unvalidated["computed_confidence"])

        # Adversarial failure
        adv_fail = self.engine.compute_confidence({
            "factors_breakdown": {
                "independent_experiences_count": 2,
                "unique_sessions_count": 2,
                "generalization_stage": "GENERALIZATION_CANDIDATE",
                "regression_score": 1.0,
                "adversarial_score": 0.0,
                "heldout_score": 1.0
            }
        })
        self.assertLess(adv_fail["validation"], all_pass["validation"])
        self.assertLess(adv_fail["computed_confidence"], all_pass["computed_confidence"])

    # -------------------------------------------------------------------------
    # Test 5: Contradiction and Regression Deductions
    # -------------------------------------------------------------------------
    def test_05_contradiction_and_regression_penalties(self):
        """Active contradictions and baseline regressions incur explicit penalties."""
        clean = self.engine.compute_confidence({
            "factors_breakdown": {
                "independent_experiences_count": 4,
                "unique_sessions_count": 4,
                "generalization_stage": "CROSS_CONTEXT_VALIDATION",
                "regression_score": 1.0,
                "adversarial_score": 1.0,
                "heldout_score": 1.0,
                "contradictions_count": 0,
                "regressions_count": 0
            }
        })
        self.assertEqual(clean["contradiction_penalty"], 0.0)

        penalized = self.engine.compute_confidence({
            "factors_breakdown": {
                "independent_experiences_count": 4,
                "unique_sessions_count": 4,
                "generalization_stage": "CROSS_CONTEXT_VALIDATION",
                "regression_score": 1.0,
                "adversarial_score": 1.0,
                "heldout_score": 1.0,
                "contradictions_count": 2,
                "regressions_count": 1
            }
        })
        # 2 * 0.15 + 1 * 0.25 = 0.55 penalty
        self.assertAlmostEqual(penalized["contradiction_penalty"], 0.55, places=2)
        self.assertLess(penalized["computed_confidence"], clean["computed_confidence"])

    # -------------------------------------------------------------------------
    # Test 6: Failure Severity and Task Quality Scaling
    # -------------------------------------------------------------------------
    def test_06_failure_severity_and_task_quality_drive_evidence_strength(self):
        """High-fidelity benchmark testing and critical failures produce higher evidence strength."""
        low_evidence = self.engine.compute_confidence({
            "factors_breakdown": {
                "independent_experiences_count": 1,
                "unique_sessions_count": 1,
                "task_quality": "DIAGNOSTIC_OBSERVATION",
                "failure_severity": "LOW"
            }
        })
        high_evidence = self.engine.compute_confidence({
            "factors_breakdown": {
                "independent_experiences_count": 1,
                "unique_sessions_count": 1,
                "task_quality": "HIGH_FIDELITY_BENCHMARK",
                "failure_severity": "CRITICAL"
            }
        })
        self.assertGreater(high_evidence["evidence_strength"], low_evidence["evidence_strength"])

    # -------------------------------------------------------------------------
    # Test 7: Distiller Produces Evidence-Derived Confidence
    # -------------------------------------------------------------------------
    def test_07_distiller_produces_evidence_derived_confidence(self):
        """Distiller attaches valid confidence and confidence_evidence to distilled lessons."""
        fdb = {
            "feedback_id": "FDB-TEST-001",
            "type": "CORRECTION",
            "severity": "HIGH",
            "scope": "REUSABLE_PROCEDURAL",
            "correction": "Always decouple numeric cells to LTR Times New Roman in Persian Word tables.",
            "desired_behavior": "Enforce decoupled LTR numbers in Arabic-script table cells.",
            "target_skill": "apa-reporting",
            "context": {
                "milestone_id": "M-DEMO-01",
                "related_artifact_paths": ["04_findings/tables.docx"]
            }
        }
        lesson = self.distiller.distill_from_feedback_payload(fdb)

        self.assertIn("confidence", lesson)
        self.assertIn("confidence_evidence", lesson)
        self.assertIsInstance(lesson["confidence"], float)

        # Validate lesson against schema
        vres = validate_lesson(lesson)
        self.assertTrue(vres["valid"], f"Lesson contract invalid: {vres.get('errors')}")

        # Validate confidence evidence structure
        cres = validate_confidence_evidence(lesson["confidence_evidence"])
        self.assertTrue(cres["valid"], f"Confidence evidence contract invalid: {cres.get('errors')}")

    # -------------------------------------------------------------------------
    # Test 8: Monotonic Confidence Progression along Generalization Ladder
    # -------------------------------------------------------------------------
    def test_08_generalization_ladder_confidence_progression(self):
        """Confidence progresses monotonically as evidence accumulates through the 7 ladder stages."""
        # 1. OBSERVED
        rec1 = self.gen_engine.record_observation(
            target_rule="Use Welch ANOVA when Levene test is significant",
            project_id="PROJ-ALPHA"
        )
        conf_obs = rec1["confidence"]

        # 2. LOCAL_LESSON
        rec2 = self.gen_engine.advance_to_local_lesson(
            generalization_id=rec1["generalization_id"],
            lesson_id="LSN-LOCAL-001",
            desired_behavior="Apply Welch robust F-test whenever variance homogeneity is rejected."
        )
        conf_loc = rec2["confidence"]

        # 3. REPEATED_PATTERN (add 2nd observation)
        obs2 = {
            "observation_id": "OBS-002",
            "source_experience_id": "EXP-002",
            "project_id": "PROJ-ALPHA",
            "task_id": "task-02",
            "context": {"domain": "statistics", "design": "between_subjects"}
        }
        rec3 = self.gen_engine.advance_to_repeated_pattern(
            generalization_id=rec1["generalization_id"],
            new_observation=obs2
        )
        conf_rep = rec3["confidence"]

        # 4. GENERALIZATION_CANDIDATE
        cond_rule = {
            "when_conditions": ["Between-subjects comparison", "Levene p < .05"],
            "then_approach": "Welch robust ANOVA",
            "except_conditions": ["Severely non-normal data with N < 15 per cell"],
            "statement": "WHEN Levene p < .05 in ANOVA → use Welch robust test EXCEPT when severe skew with small N."
        }
        rec4 = self.gen_engine.advance_to_generalization_candidate(
            generalization_id=rec1["generalization_id"],
            conditional_rule=cond_rule
        )
        conf_cand = rec4["confidence"]

        # 5. CROSS_CONTEXT_VALIDATION (2 passing heterogeneous contexts)
        ctx_evals = [
            {"context_id": "CTX-1", "design": "2_group_independent", "sample_size_tier": "small", "verdict": "PASS"},
            {"context_id": "CTX-2", "design": "4_group_factorial", "sample_size_tier": "large", "verdict": "PASS"}
        ]
        rec5 = self.gen_engine.advance_to_cross_context_validation(
            generalization_id=rec1["generalization_id"],
            context_evaluations=ctx_evals
        )
        conf_ctx = rec5["confidence"]

        # 6. CROSS_DOMAIN_VALIDATION (2 passing heterogeneous domains)
        dom_evals = [
            {"domain": "clinical_psychology", "verdict": "PASS"},
            {"domain": "educational_assessment", "verdict": "PASS"}
        ]
        rec6 = self.gen_engine.advance_to_cross_domain_validation(
            generalization_id=rec1["generalization_id"],
            domain_evaluations=dom_evals
        )
        conf_dom = rec6["confidence"]

        # 7. PROMOTED_PRINCIPLE
        rec7 = self.gen_engine.promote_to_principle(
            generalization_id=rec1["generalization_id"]
        )
        conf_prn = rec7["confidence"]

        # Assert monotonic progression
        self.assertLessEqual(conf_obs, conf_loc)
        self.assertLessEqual(conf_loc, conf_rep)
        self.assertLessEqual(conf_rep, conf_cand)
        self.assertLess(conf_cand, conf_ctx)
        self.assertLess(conf_ctx, conf_dom)
        self.assertLessEqual(conf_dom, conf_prn)
        self.assertGreater(conf_prn, 0.70)

        # Validate schema of final record
        val_res = validate_generalization_lifecycle(rec7)
        self.assertTrue(val_res["valid"], f"Lifecycle record invalid: {val_res.get('errors')}")


if __name__ == "__main__":
    unittest.main()
