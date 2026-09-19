#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_contradiction_handling_phase27.py — Phase 27 Contradiction Handling Test Suite

Validates that:
1. CONFLICT_DETECTED is NEVER automatically converted into RESOLVED_WITH_CONDITIONS.
2. Premature resolution without completing stages is strictly blocked (fail-closed).
3. The full 6-stage lifecycle executes sequentially:
   CONFLICT_DETECTED -> CONFLICT_ANALYSIS -> EVIDENCE_COMPARISON -> CONDITION_IDENTIFICATION -> INDEPENDENT_TEST -> RESOLVED (or UNRESOLVED).
4. Independent test failures transition strictly to UNRESOLVED rather than falsely resolving.
5. Real methodological conflict 1 (RM-ANOVA vs LMM) resolves under empirical boundary conditions.
6. Real methodological conflict 2 (Baron & Kenny vs Bootstrap Mediation) resolves under empirical boundary conditions.
7. Schema validation passes across all intermediate and terminal stages.
8. Active/unresolved contradictions penalize confidence, but verified RESOLVED contradictions do not.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from contracts.contract_validator import validate_contradiction_record
from scripts.academic_contradiction_engine import (
    AcademicContradictionEngine,
    ContradictionError,
    PrematureContradictionResolutionError
)
from scripts.academic_behavior_consolidator import AcademicBehaviorConsolidator
from scripts.academic_confidence_engine import AcademicConfidenceEngine
from scripts.academic_knowledge_manager import AcademicKnowledgeManager


class TestContradictionHandlingPhase27(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="phase27_ctd_test_")
        self.engine = AcademicContradictionEngine(base_dir=self.test_dir)
        self.km = AcademicKnowledgeManager(base_dir=self.test_dir)
        self.consolidator = AcademicBehaviorConsolidator(base_dir=self.test_dir)
        self.conf_engine = AcademicConfidenceEngine(base_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # Test 1: Never automatically convert CONFLICT_DETECTED
    # -------------------------------------------------------------------------
    def test_01_never_auto_resolves_conflict_detected(self):
        """Proves newly detected contradiction is strictly CONFLICT_DETECTED and never RESOLVED_WITH_CONDITIONS."""
        lesson_a = {
            "lesson_id": "LSN-METHOD-01",
            "statement": "Always report partial eta-squared for repeated-measures ANOVA.",
            "target_skill": "statistical-data-analyst"
        }
        lesson_b = {
            "lesson_id": "LSN-METHOD-02",
            "statement": "Never report partial eta-squared; always report generalized eta-squared.",
            "target_skill": "statistical-data-analyst"
        }

        record = self.engine.detect_conflict(
            lesson_a=lesson_a,
            lesson_b=lesson_b,
            conflict_type="OPPOSING_RECOMMENDATIONS",
            description="Tension between partial eta-squared and generalized eta-squared.",
            target_skill="statistical-data-analyst"
        )

        self.assertEqual(record["stage"], "CONFLICT_DETECTED")
        self.assertEqual(record["status"], "CONFLICT_DETECTED")
        self.assertNotEqual(record["status"], "RESOLVED_WITH_CONDITIONS")
        self.assertNotEqual(record["status"], "RESOLVED")
        self.assertEqual(record["reconciliation_strategy"], "PENDING_HUMAN_RESOLUTION")

    # -------------------------------------------------------------------------
    # Test 2: Premature resolution blocked (Fail-Closed)
    # -------------------------------------------------------------------------
    def test_02_premature_resolution_blocked(self):
        """Proves attempting to resolve directly from CONFLICT_DETECTED raises PrematureContradictionResolutionError."""
        record = self.engine.detect_conflict(
            lesson_a={"lesson_id": "LSN-A"},
            lesson_b={"lesson_id": "LSN-B"},
            conflict_type="CONTRADICTORY_CONSTRAINTS",
            description="Opposing constraints between requirements."
        )

        with self.assertRaises(PrematureContradictionResolutionError):
            self.engine.resolve_with_test_evidence(
                contradiction_id=record["contradiction_id"],
                test_result={"independent_verdict": "PASS"}
            )

        # Check resolution check also raises
        record["status"] = "RESOLVED"
        with self.assertRaises(PrematureContradictionResolutionError):
            self.engine.check_resolution_allowed(record)

    # -------------------------------------------------------------------------
    # Test 3: Full 6-Stage Resolution Pipeline
    # -------------------------------------------------------------------------
    def test_03_full_six_stage_resolution_pipeline(self):
        """Validates sequential progression through all 6 stages."""
        # Stage 1: Detection
        r1 = self.engine.detect_conflict(
            lesson_a={"lesson_id": "LSN-RM"},
            lesson_b={"lesson_id": "LSN-LMM"},
            conflict_type="MODEL_SPECIFICATION_CONFLICT",
            description="RM-ANOVA vs LMM longitudinal modeling tension."
        )
        ctd_id = r1["contradiction_id"]
        self.assertEqual(r1["stage"], "CONFLICT_DETECTED")

        # Stage 2: Conflict Analysis
        r2 = self.engine.advance_to_conflict_analysis(
            contradiction_id=ctd_id,
            assumptions_a=["Assumes sphericity (Mauchly p > .05)", "Requires complete balanced data"],
            assumptions_b=["Robust to sphericity violations", "Accommodates missing at random data"],
            root_cause="Different statistical trade-offs: exact F-distribution vs missing-data flexibility."
        )
        self.assertEqual(r2["stage"], "CONFLICT_ANALYSIS")
        self.assertIn("root_cause", r2["conflict_analysis"])

        # Stage 3: Evidence Comparison
        r3 = self.engine.advance_to_evidence_comparison(
            contradiction_id=ctd_id,
            evidence_for_a=["Kirk (2013) Experimental Design", "Maxwell & Delaney (2004)"],
            evidence_for_b=["Gelman & Hill (2006)", "Singer & Willett (2003)"],
            divergence_analysis="Empirical divergence under missing wave attrition."
        )
        self.assertEqual(r3["stage"], "EVIDENCE_COMPARISON")
        self.assertIn("evidence_for_a", r3["evidence_comparison"])

        # Stage 4: Condition Identification
        r4 = self.engine.advance_to_condition_identification(
            contradiction_id=ctd_id,
            condition_for_a="Complete cases, sphericity confirmed (Mauchly p > .05), balanced design",
            condition_for_b="Missing waves present, severe sphericity violation (epsilon < .75)",
            boundary_exceptions=["Total unmeasured attrition > 40%"]
        )
        self.assertEqual(r4["stage"], "CONDITION_IDENTIFICATION")
        self.assertIn("condition_for_a", r4["identified_conditions"])

        # Stage 5: Independent Test
        r5 = self.engine.advance_to_independent_test(
            contradiction_id=ctd_id,
            test_suite_id="SUITE-METHODOLOGY-RM-LMM-01",
            test_arms={
                "arm_rm_balanced": "PASS",
                "arm_lmm_missing_waves": "PASS"
            }
        )
        self.assertEqual(r5["stage"], "INDEPENDENT_TEST")
        self.assertEqual(r5["independent_test"]["independent_verdict"], "PENDING")

        # Stage 6: Terminal Resolution
        r6 = self.engine.resolve_with_test_evidence(
            contradiction_id=ctd_id,
            test_result={
                "test_suite_id": "SUITE-METHODOLOGY-RM-LMM-01",
                "independent_verdict": "PASS",
                "evaluator": "AcademicIndependentEvaluator"
            },
            resolution_summary="Resolved under verified condition: RM-ANOVA for complete balanced data, LMM for attrition."
        )
        self.assertEqual(r6["stage"], "RESOLVED")
        self.assertEqual(r6["status"], "RESOLVED")
        self.assertEqual(r6["independent_test"]["independent_verdict"], "PASS")

        # Check resolution invariant passes
        self.engine.check_resolution_allowed(r6)

    # -------------------------------------------------------------------------
    # Test 4: Independent Test Failure Transitions to UNRESOLVED
    # -------------------------------------------------------------------------
    def test_04_independent_test_failure_leads_to_unresolved(self):
        """Proves that a failed independent test marks contradiction as UNRESOLVED, not RESOLVED."""
        r = self.engine.detect_conflict(
            lesson_a={"lesson_id": "LSN-X"},
            lesson_b={"lesson_id": "LSN-Y"},
            conflict_type="INCOMPATIBLE_ASSUMPTIONS",
            description="Conflicting assumption claims across paradigms."
        )
        ctd_id = r["contradiction_id"]
        self.engine.advance_to_conflict_analysis(
            contradiction_id=ctd_id,
            assumptions_a=["Parametric efficiency"],
            assumptions_b=["Non-parametric robustness"],
            root_cause="Distributional normality contention."
        )
        self.engine.advance_to_evidence_comparison(
            contradiction_id=ctd_id,
            evidence_for_a=["Study A (2020)"],
            evidence_for_b=["Study B (2022)"]
        )
        self.engine.advance_to_condition_identification(
            contradiction_id=ctd_id,
            condition_for_a="Skewness < 1.0",
            condition_for_b="Skewness >= 1.0"
        )
        self.engine.advance_to_independent_test(
            contradiction_id=ctd_id,
            test_suite_id="SUITE-SKEWNESS-TEST-01"
        )

        # Submit failing test result
        unresolved_record = self.engine.resolve_with_test_evidence(
            contradiction_id=ctd_id,
            test_result={
                "test_suite_id": "SUITE-SKEWNESS-TEST-01",
                "independent_verdict": "FAIL",
                "evaluator": "AcademicIndependentEvaluator"
            }
        )

        self.assertEqual(unresolved_record["stage"], "UNRESOLVED")
        self.assertEqual(unresolved_record["status"], "UNRESOLVED")
        self.assertEqual(unresolved_record["independent_test"]["independent_verdict"], "FAIL")
        self.assertIn("failed", unresolved_record["resolution_summary"].lower())

    # -------------------------------------------------------------------------
    # Test 5: Real Methodological Conflict: RM-ANOVA vs LMM
    # -------------------------------------------------------------------------
    def test_05_methodological_conflict_rm_vs_lmm(self):
        """Tests end-to-end resolution of RM-ANOVA vs LMM tension via consolidator."""
        l_rm = {
            "lesson_id": "LSN-RM-01",
            "desired_behavior": "For repeated measurements, always execute repeated-measures ANOVA assuming sphericity.",
            "statement": "For repeated measurements, always execute repeated-measures ANOVA assuming sphericity.",
            "related_skills": ["statistical-data-analyst"]
        }
        l_lmm = {
            "lesson_id": "LSN-LMM-01",
            "desired_behavior": "For repeated measurements, use linear mixed models LMM instead of repeated-measures ANOVA.",
            "statement": "For repeated measurements, use linear mixed models LMM instead of repeated-measures ANOVA.",
            "related_skills": ["statistical-data-analyst"]
        }

        detected = self.consolidator.detect_contradictions([l_rm, l_lmm], record_to_disk=True)
        self.assertEqual(len(detected), 1)
        ctd = detected[0]
        self.assertEqual(ctd["stage"], "CONFLICT_DETECTED")
        self.assertEqual(ctd["status"], "CONFLICT_DETECTED")

        # Full reconciliation pipeline
        resolved = self.consolidator.reconcile_contradiction_pipeline(
            contradiction_id=ctd["contradiction_id"],
            assumptions_a=["Assumes sphericity (Mauchly p > .05)", "Balanced designs without missing waves"],
            assumptions_b=["Robust to sphericity violations", "Handles missing at random longitudinal data"],
            root_cause="Trade-off between exact F-tests under balanced data vs mixed-effects flexibility under attrition",
            evidence_for_a=["Kirk (2013) Experimental Design"],
            evidence_for_b=["Gelman & Hill (2006) Data Analysis Using Regression and Multilevel Models"],
            condition_for_a="Complete balanced cases, sphericity met (Mauchly p > .05)",
            condition_for_b="Missing waves, severe sphericity violation (Greenhouse-Geisser epsilon < .75)",
            test_result={
                "test_suite_id": "TEST-RM-LMM-METHODOLOGY",
                "independent_verdict": "PASS",
                "evaluator": "AcademicIndependentEvaluator"
            }
        )

        self.assertEqual(resolved["stage"], "RESOLVED")
        self.assertEqual(resolved["status"], "RESOLVED")
        self.assertIn("condition_for_a", resolved["applicability_conditions"])
        self.assertIn("condition_for_b", resolved["applicability_conditions"])

    # -------------------------------------------------------------------------
    # Test 6: Real Methodological Conflict: Baron & Kenny vs Bootstrap Mediation
    # -------------------------------------------------------------------------
    def test_06_methodological_conflict_baron_kenny_vs_bootstrap(self):
        """Tests end-to-end resolution of Baron & Kenny vs Bootstrap Mediation tension."""
        l_bk = {
            "lesson_id": "LSN-BK-01",
            "desired_behavior": "For mediation analysis, always follow Baron & Kenny causal steps requiring significant step 1 total effect.",
            "statement": "For mediation analysis, always follow Baron & Kenny causal steps requiring significant step 1 total effect.",
            "related_skills": ["mediation"]
        }
        l_boot = {
            "lesson_id": "LSN-BOOT-01",
            "desired_behavior": "For mediation analysis, use Preacher & Hayes bootstrap mediation; significant total effect step 1 is not required.",
            "statement": "For mediation analysis, use Preacher & Hayes bootstrap mediation; significant total effect step 1 is not required.",
            "related_skills": ["mediation"]
        }

        detected = self.consolidator.detect_contradictions([l_bk, l_boot], record_to_disk=True)
        self.assertEqual(len(detected), 1)
        ctd = detected[0]
        self.assertEqual(ctd["conflict_type"], "MUTUALLY_EXCLUSIVE_METHODS")
        self.assertEqual(ctd["stage"], "CONFLICT_DETECTED")

        # Full reconciliation pipeline
        resolved = self.consolidator.reconcile_contradiction_pipeline(
            contradiction_id=ctd["contradiction_id"],
            assumptions_a=["Normal distribution of indirect effect product", "Total effect prerequisite"],
            assumptions_b=["Asymmetric indirect effect sampling distribution", "Indirect effect can exist without total effect"],
            root_cause="Baron & Kenny Sobel test lacks power due to non-normal product distribution; Bootstrap handles asymmetry",
            evidence_for_a=["Baron & Kenny (1986)"],
            evidence_for_b=["Preacher & Hayes (2004, 2008)", "Hayes (2022) PROCESS"],
            condition_for_a="Historical legacy replication where protocol explicitly mandates 4-step causal chain",
            condition_for_b="Modern empirical mediation via Preacher & Hayes bootstrap (5,000 resamples) with 95% BCa confidence intervals",
            test_result={
                "test_suite_id": "TEST-MEDIATION-BOOTSTRAP",
                "independent_verdict": "PASS",
                "evaluator": "AcademicIndependentEvaluator"
            }
        )

        self.assertEqual(resolved["stage"], "RESOLVED")
        self.assertEqual(resolved["status"], "RESOLVED")
        self.assertIn("Preacher & Hayes", resolved["identified_conditions"]["condition_for_b"])

    # -------------------------------------------------------------------------
    # Test 7: Contract Schema Compliance Across All Stages
    # -------------------------------------------------------------------------
    def test_07_contract_schema_compliance_across_all_stages(self):
        """Validates that contradiction records strictly conform to the JSON schema at each of the 6 stages."""
        # 1. CONFLICT_DETECTED
        r1 = self.engine.detect_conflict(
            lesson_a={"lesson_id": "LSN-A1"},
            lesson_b={"lesson_id": "LSN-B1"},
            conflict_type="INCOMPATIBLE_ASSUMPTIONS",
            description="Testing schema across stages of contradiction lifecycle."
        )
        self.assertTrue(validate_contradiction_record(r1)["valid"])

        # 2. CONFLICT_ANALYSIS
        r2 = self.engine.advance_to_conflict_analysis(
            contradiction_id=r1["contradiction_id"],
            assumptions_a=["Assumption A requires strict normality"],
            assumptions_b=["Assumption B allows skewed distributions"],
            root_cause="Underlying assumption differences between statistical estimators"
        )
        self.assertTrue(validate_contradiction_record(r2)["valid"])

        # 3. EVIDENCE_COMPARISON
        r3 = self.engine.advance_to_evidence_comparison(
            contradiction_id=r1["contradiction_id"],
            evidence_for_a=["Empirical Study A (2020)"],
            evidence_for_b=["Empirical Study B (2022)"]
        )
        self.assertTrue(validate_contradiction_record(r3)["valid"])

        # 4. CONDITION_IDENTIFICATION
        r4 = self.engine.advance_to_condition_identification(
            contradiction_id=r1["contradiction_id"],
            condition_for_a="Parametric normality satisfied with skewness under 1.0",
            condition_for_b="Non-parametric robustness required for severe skewness"
        )
        self.assertTrue(validate_contradiction_record(r4)["valid"])

        # 5. INDEPENDENT_TEST
        r5 = self.engine.advance_to_independent_test(
            contradiction_id=r1["contradiction_id"],
            test_suite_id="SUITE-SCHEMA-01"
        )
        self.assertTrue(validate_contradiction_record(r5)["valid"])

        # 6. RESOLVED
        r6 = self.engine.resolve_with_test_evidence(
            contradiction_id=r1["contradiction_id"],
            test_result={"test_suite_id": "SUITE-SCHEMA-01", "independent_verdict": "PASS"}
        )
        self.assertTrue(validate_contradiction_record(r6)["valid"])

    # -------------------------------------------------------------------------
    # Test 8: Active Contradictions Penalize Confidence Until Resolved
    # -------------------------------------------------------------------------
    def test_08_active_contradictions_penalize_confidence_until_resolved(self):
        """Proves that active contradictions impose a penalty on confidence, but resolved ones do not."""
        # Baseline with no contradictions
        baseline_factors = {
            "factors_breakdown": {
                "independent_experiences_count": 5,
                "unique_sessions_count": 3,
                "distinct_designs_count": 2,
                "distinct_domains_count": 2,
                "generalization_stage": "GENERALIZATION_CANDIDATE",
                "regression_score": 0.80,
                "adversarial_score": 0.80,
                "heldout_score": 0.80,
                "contradictions_count": 0,
                "regressions_count": 0,
                "failure_severity": "LOW",
                "task_quality": "HIGH_FIDELITY_BENCHMARK"
            }
        }
        baseline_conf = self.conf_engine.compute_confidence(baseline_factors)
        self.assertEqual(baseline_conf["contradiction_penalty"], 0.0)

        # With 2 active contradictions
        active_factors = {
            "factors_breakdown": {
                "independent_experiences_count": 5,
                "unique_sessions_count": 3,
                "distinct_designs_count": 2,
                "distinct_domains_count": 2,
                "generalization_stage": "GENERALIZATION_CANDIDATE",
                "regression_score": 0.80,
                "adversarial_score": 0.80,
                "heldout_score": 0.80,
                "contradictions": [
                    {"contradiction_id": "CTD-01", "status": "CONFLICT_DETECTED"},
                    {"contradiction_id": "CTD-02", "status": "CONFLICT_ANALYSIS"}
                ],
                "regressions_count": 0,
                "failure_severity": "LOW",
                "task_quality": "HIGH_FIDELITY_BENCHMARK"
            }
        }
        active_conf = self.conf_engine.compute_confidence(active_factors)
        self.assertEqual(active_conf["factors_breakdown"]["contradictions_count"], 2)
        self.assertGreater(active_conf["contradiction_penalty"], 0.0)
        self.assertLess(active_conf["computed_confidence"], baseline_conf["computed_confidence"])

        # With resolved contradictions
        resolved_factors = {
            "factors_breakdown": {
                "independent_experiences_count": 5,
                "unique_sessions_count": 3,
                "distinct_designs_count": 2,
                "distinct_domains_count": 2,
                "generalization_stage": "GENERALIZATION_CANDIDATE",
                "regression_score": 0.80,
                "adversarial_score": 0.80,
                "heldout_score": 0.80,
                "contradictions": [
                    {"contradiction_id": "CTD-01", "status": "RESOLVED"},
                    {"contradiction_id": "CTD-02", "status": "RESOLVED"}
                ],
                "regressions_count": 0,
                "failure_severity": "LOW",
                "task_quality": "HIGH_FIDELITY_BENCHMARK"
            }
        }
        resolved_conf = self.conf_engine.compute_confidence(resolved_factors)
        self.assertEqual(resolved_conf["factors_breakdown"]["contradictions_count"], 0)
        self.assertEqual(resolved_conf["contradiction_penalty"], 0.0)
        self.assertEqual(resolved_conf["computed_confidence"], baseline_conf["computed_confidence"])


if __name__ == "__main__":
    unittest.main()
