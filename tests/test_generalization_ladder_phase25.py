#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_generalization_ladder_phase25.py — Test Suite for Phase 25 Generalization Ladder

Verifies the 7-stage Generalization Progression Ladder:
OBSERVED → LOCAL_LESSON → REPEATED_PATTERN → GENERALIZATION_CANDIDATE →
CROSS_CONTEXT_VALIDATION → CROSS_DOMAIN_VALIDATION → PROMOTED_PRINCIPLE

Guarantees that 2 experiences NEVER directly elevate to CROSS_PROJECT_UNIVERSAL,
and that promotion to universal principle strictly requires verified evidence
across heterogeneous contexts and domains.
"""

import os
import sys
import shutil
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.academic_generalization_engine import (
    AcademicGeneralizationEngine,
    GeneralizationError,
    PrematureGeneralizationError
)
from scripts.academic_behavior_consolidator import AcademicBehaviorConsolidator
from contracts.contract_validator import validate_generalization_lifecycle


class TestGeneralizationLadderPhase25(unittest.TestCase):
    """Unit test suite for Phase 25 7-stage generalization progression."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="agy_test_gen_phase25_")
        self.engine = AcademicGeneralizationEngine(base_dir=self.test_dir)
        self.consolidator = AcademicBehaviorConsolidator(base_dir=self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_stage_1_observation_creation(self):
        """Stage 1: Verifies initial observation creates record in stage OBSERVED with PROJECT_SPECIFIC scope."""
        record = self.engine.record_observation(
            target_rule="Use ANCOVA when baseline covariates are measured",
            project_id="PROJ-RCT-001",
            task_id="TASK-FINDINGS-01",
            source_experience_id="EXP-RCT-001",
            context={
                "domain": "clinical_trials",
                "design": "2_group_rct_pre_post",
                "sample_size": 120,
                "data_type": "continuous"
            }
        )

        self.assertEqual(record["stage"], "OBSERVED")
        self.assertEqual(record["scope"], "PROJECT_SPECIFIC")
        self.assertEqual(len(record["evidence_summary"]["observations"]), 1)
        self.assertFalse(record["evidence_summary"]["heterogeneous_evidence_verified"])

        val_res = validate_generalization_lifecycle(record)
        self.assertTrue(val_res["valid"], f"Schema error: {val_res.get('errors')}")

    def test_02_stage_2_local_lesson_elevation(self):
        """Stage 2: Verifies advancing observation to LOCAL_LESSON bounds scope to PROJECT_SPECIFIC."""
        rec1 = self.engine.record_observation(
            target_rule="Report exact p-values with leading zero",
            project_id="PROJ-THESIS-001"
        )
        gen_id = rec1["generalization_id"]

        rec2 = self.engine.advance_to_local_lesson(
            generalization_id=gen_id,
            lesson_id="LSN-LOCAL-001",
            desired_behavior="Always preserve leading zero in Persian reporting (۰.۰۵ instead of .۰۵)"
        )

        self.assertEqual(rec2["stage"], "LOCAL_LESSON")
        self.assertEqual(rec2["scope"], "PROJECT_SPECIFIC")
        self.assertIn("PROJ-THESIS-001", rec2["conditional_rule"]["statement"])

        val_res = validate_generalization_lifecycle(rec2)
        self.assertTrue(val_res["valid"], f"Schema error: {val_res.get('errors')}")

    def test_03_stage_3_repeated_pattern_requires_multiple_observations(self):
        """Stage 3: Verifies REPEATED_PATTERN requires >= 2 observations and remains local."""
        rec1 = self.engine.record_observation(
            target_rule="Verify Levene assumption before ANOVA",
            project_id="PROJ-STUDY-001"
        )
        gen_id = rec1["generalization_id"]
        self.engine.advance_to_local_lesson(gen_id, "LSN-01", "Verify Levene test")

        # Attempting REPEATED_PATTERN with only 1 observation must fail
        with self.assertRaises(PrematureGeneralizationError):
            self.engine.advance_to_repeated_pattern(gen_id)

        # Add second observation within same project
        obs2 = {
            "observation_id": "OBS-002",
            "source_experience_id": "EXP-002",
            "project_id": "PROJ-STUDY-001",
            "task_id": "TASK-02",
            "context": {"design": "2_group_pre_post", "domain": "psychometrics"}
        }
        rec3 = self.engine.advance_to_repeated_pattern(gen_id, new_observation=obs2)

        self.assertEqual(rec3["stage"], "REPEATED_PATTERN")
        self.assertEqual(rec3["scope"], "LOCAL_PATTERN")
        self.assertEqual(len(rec3["evidence_summary"]["observations"]), 2)

        # Crucial check: 2 observations did NOT become universal!
        self.assertNotEqual(rec3["scope"], "CROSS_PROJECT_UNIVERSAL")

    def test_04_stage_4_generalization_candidate_formulation(self):
        """Stage 4: Verifies GENERALIZATION_CANDIDATE requires structured conditional rule."""
        rec1 = self.engine.record_observation(
            target_rule="Use bootstrap mediation with 5000 resamples",
            project_id="PROJ-MED-001"
        )
        gen_id = rec1["generalization_id"]
        self.engine.advance_to_local_lesson(gen_id, "LSN-MED-01", "Use bootstrap mediation")
        self.engine.advance_to_repeated_pattern(gen_id, new_observation={
            "observation_id": "OBS-MED-02", "project_id": "PROJ-MED-001"
        })

        conditional_rule = {
            "when_conditions": ["Testing indirect effects in mediation models"],
            "then_approach": "Apply Preacher & Hayes bootstrap mediation with 5,000 resamples and 95% BCa CIs",
            "except_conditions": ["Model contains categorical mediators or latent variables requiring SEM"],
            "statement": "WHEN testing indirect mediation effects → use Preacher & Hayes bootstrap (5,000 resamples, 95% BCa) EXCEPT when latent variables require SEM."
        }

        rec4 = self.engine.advance_to_generalization_candidate(gen_id, conditional_rule)
        self.assertEqual(rec4["stage"], "GENERALIZATION_CANDIDATE")
        self.assertEqual(rec4["scope"], "GENERALIZATION_CANDIDATE")

        val_res = validate_generalization_lifecycle(rec4)
        self.assertTrue(val_res["valid"], f"Schema error: {val_res.get('errors')}")

    def test_05_stage_5_cross_context_validation_requires_heterogeneous_contexts(self):
        """Stage 5: Verifies CROSS_CONTEXT_VALIDATION requires >= 2 distinct, heterogeneous contexts."""
        rec = self.engine.record_observation("Use ANCOVA", "PROJ-A")
        gen_id = rec["generalization_id"]
        self.engine.advance_to_local_lesson(gen_id, "LSN-01", "Use ANCOVA")
        self.engine.advance_to_repeated_pattern(gen_id, new_observation={"observation_id": "O2", "project_id": "PROJ-A"})
        self.engine.advance_to_generalization_candidate(gen_id, {
            "when_conditions": ["Baseline covariate measured"],
            "then_approach": "ANCOVA",
            "except_conditions": ["Heterogeneous regression slopes"],
            "statement": "WHEN baseline covariate measured → use ANCOVA EXCEPT when slopes are heterogeneous."
        })

        # Test with homogeneous/insufficient contexts (only 1 context)
        homo_contexts = [
            {"context_id": "CTX-01", "design": "2_group_rct", "sample_size_tier": "moderate", "verdict": "PASS"}
        ]
        with self.assertRaises(PrematureGeneralizationError):
            self.engine.advance_to_cross_context_validation(gen_id, homo_contexts)

        # Test with 2 heterogeneous contexts (different designs)
        hetero_contexts = [
            {"context_id": "CTX-01", "design": "2_group_rct", "sample_size_tier": "small", "verdict": "PASS"},
            {"context_id": "CTX-02", "design": "3_group_factorial", "sample_size_tier": "large", "verdict": "PASS"}
        ]
        rec5 = self.engine.advance_to_cross_context_validation(gen_id, hetero_contexts)
        self.assertEqual(rec5["stage"], "CROSS_CONTEXT_VALIDATION")
        self.assertEqual(rec5["scope"], "CROSS_CONTEXT_VALIDATED")

    def test_06_stage_6_and_7_cross_domain_and_promoted_principle(self):
        """Stages 6 & 7: Verifies promotion to principle requires heterogeneous cross-domain validation."""
        rec = self.engine.record_observation("Apply Bonferroni/FDR correction", "PROJ-MULT-001")
        gen_id = rec["generalization_id"]
        self.engine.advance_to_local_lesson(gen_id, "LSN-MULT-01", "Apply multiple testing correction")
        self.engine.advance_to_repeated_pattern(gen_id, new_observation={"observation_id": "O2", "project_id": "PROJ-MULT-001"})
        self.engine.advance_to_generalization_candidate(gen_id, {
            "when_conditions": ["Conducting multiple pairwise comparisons"],
            "then_approach": "Adjust alpha threshold via Benjamini-Hochberg FDR or Bonferroni",
            "except_conditions": ["Pre-planned orthogonal contrasts defined a priori"],
            "statement": "WHEN conducting multiple pairwise comparisons → adjust alpha via FDR/Bonferroni EXCEPT for a priori orthogonal contrasts."
        })
        self.engine.advance_to_cross_context_validation(gen_id, [
            {"context_id": "CTX-01", "design": "repeated_measures", "sample_size_tier": "moderate", "verdict": "PASS"},
            {"context_id": "CTX-02", "design": "factorial_anova", "sample_size_tier": "large", "verdict": "PASS"}
        ])

        # Attempting to promote to principle before cross-domain validation must fail
        with self.assertRaises(PrematureGeneralizationError):
            self.engine.promote_to_principle(gen_id)

        # Provide homogeneous domains (same domain repeated) -> must fail
        homo_domains = [
            {"domain": "clinical_trials", "verdict": "PASS"},
            {"domain": "clinical_trials", "verdict": "PASS"}
        ]
        with self.assertRaises(PrematureGeneralizationError):
            self.engine.advance_to_cross_domain_validation(gen_id, homo_domains)

        # Provide 2 distinct, heterogeneous domains
        hetero_domains = [
            {"domain": "clinical_trials", "subdiscipline": "psychopharmacology", "verdict": "PASS", "evidence_ref": "EVL-DOM-01"},
            {"domain": "psychometrics", "subdiscipline": "educational_testing", "verdict": "PASS", "evidence_ref": "EVL-DOM-02"}
        ]
        rec6 = self.engine.advance_to_cross_domain_validation(gen_id, hetero_domains)
        self.assertEqual(rec6["stage"], "CROSS_DOMAIN_VALIDATION")
        self.assertEqual(rec6["scope"], "CROSS_DOMAIN_VALIDATED")
        self.assertTrue(rec6["evidence_summary"]["heterogeneous_evidence_verified"])

        # Stage 7: Promotion to Principle
        rec7 = self.engine.promote_to_principle(gen_id, author_or_gatekeeper="digital-saber")
        self.assertEqual(rec7["stage"], "PROMOTED_PRINCIPLE")
        self.assertEqual(rec7["scope"], "CROSS_PROJECT_UNIVERSAL")
        self.assertEqual(rec7["status"], "PROMOTED")

        # Verify physical principle artifact was materialized on disk
        prn_id = rec7["promoted_principle_id"]
        prn_file = os.path.join(self.engine.principles_dir, f"{prn_id}.json")
        self.assertTrue(os.path.isfile(prn_file))

    def test_07_consolidator_refuses_premature_universal_elevation(self):
        """Verifies AcademicBehaviorConsolidator does NOT elevate 2 experiences to CROSS_PROJECT_UNIVERSAL."""
        l1 = {
            "lesson_id": "LSN-01",
            "source_experience_id": "EXP-01",
            "desired_behavior": "Report confidence intervals for effect sizes.",
            "confidence": 0.90
        }
        l2 = {
            "lesson_id": "LSN-02",
            "source_experience_id": "EXP-02",
            "desired_behavior": "Report confidence intervals for effect sizes.",
            "confidence": 0.90
        }

        # Under the old flawed logic, 2 experiences -> CROSS_PROJECT_UNIVERSAL
        # Under Phase 25, 2 experiences without heterogeneous cross-validation produce GENERALIZATION_CANDIDATE
        gen_result = self.consolidator.generalize_lessons([l1, l2])
        self.assertNotEqual(gen_result["scope"], "CROSS_PROJECT_UNIVERSAL")
        self.assertEqual(gen_result["generalization_stage"], "GENERALIZATION_CANDIDATE")
        self.assertEqual(gen_result["scope"], "DOMAIN_WIDE")


if __name__ == "__main__":
    unittest.main()
