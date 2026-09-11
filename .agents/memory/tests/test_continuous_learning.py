#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Digital Saber Continuous Learning Engine & Dynamic Evaluator
"""

import os
import sys
import unittest
import tempfile
import shutil
import json

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
MEMORY_DIR = os.path.abspath(os.path.join(TESTS_DIR, ".."))
AGENTS_DIR = os.path.abspath(os.path.join(MEMORY_DIR, ".."))
EVAL_DIR = os.path.join(AGENTS_DIR, "evaluation")
REASONING_DIR = os.path.join(AGENTS_DIR, "reasoning")

for p in [MEMORY_DIR, EVAL_DIR, REASONING_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from case_memory_engine import CaseMemoryEngine
from decision_journal_engine import DecisionJournalEngine
from continuous_learning_engine import ContinuousLearningEngine
from saber_similarity_evaluator import SaberSimilarityEvaluator


class TestContinuousLearning(unittest.TestCase):

    def setUp(self):
        # Create temp directories for isolated testing
        self.test_dir = tempfile.mkdtemp()
        self.cases_dir = os.path.join(self.test_dir, "cases")
        self.decisions_dir = os.path.join(self.test_dir, "decisions")
        os.makedirs(self.cases_dir, exist_ok=True)
        os.makedirs(self.decisions_dir, exist_ok=True)

        # Seed a test case
        seed_case = {
            "case_id": "test_case_seed_001",
            "topic": "اثربخشی درمان مبتنی بر پذیرش و تعهد بر فرسودگی شغلی کادر درمان",
            "design": "pre_post_control",
            "sample_size": 30,
            "statistical_analysis": "One-Way ANCOVA",
            "confidence_score": 0.90,
            "reinforcement_count": 0
        }
        with open(os.path.join(self.cases_dir, "test_case_seed_001.json"), "w", encoding="utf-8") as f:
            json.dump(seed_case, f, ensure_ascii=False, indent=2)

        self.engine = ContinuousLearningEngine(cases_dir=self.cases_dir, decisions_dir=self.decisions_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_01_process_new_case(self):
        case_spec = {
            "title": "اثربخشی درمان متمرکز بر شفقت بر شرم و خودانتقادی دانشجویان",
            "objective": "difference",
            "design": "pre_post_control",
            "sample_size": 30,
            "has_pretest": True
        }
        res = self.engine.process_new_case(case_spec)
        self.assertIn("decision_id", res)
        self.assertIn("recommendation", res)
        self.assertEqual(res["learning_stage"], "RECOMMENDATION_GENERATED")
        candidates = res["recommendation"]["candidates_evaluated"]
        self.assertEqual(len(candidates), 3)

        # Verify journal status
        did = res["decision_id"]
        dec = next((d for d in self.engine.decision_journal.decisions if d["decision_id"] == did), None)
        self.assertIsNotNone(dec)
        self.assertEqual(dec.get("learning_cycle_stage"), "PENDING_HUMAN_OUTCOME")

    def test_02_record_human_outcome_agree(self):
        case_spec = {
            "title": "نقش میانجی خودتنظیمی هیجانی در رابطه بین تروما و اضطراب",
            "objective": "mediation",
            "has_mediator": True,
            "sample_size": 150
        }
        res = self.engine.process_new_case(case_spec)
        did = res["decision_id"]

        outcome = self.engine.record_human_outcome(did, {
            "action": "AGREE",
            "supervisor_accepted": True,
            "notes": "Approved standard Hayes PROCESS Model 4 recommendation."
        })

        self.assertEqual(outcome["alignment_status"], "PERFECT_CONGRUENCE (AGREED)")
        self.assertEqual(outcome["congruence_score"], 1.0)
        self.assertEqual(outcome["knowledge_update"]["type"], "REINFORCEMENT")

    def test_03_record_human_outcome_divergence_synthesizes_case(self):
        initial_cases_count = self.engine.case_memory.count()

        case_spec = {
            "title": "بررسی مقایسه‌ای اثربخشی واقعیت‌درمانی و طرحواره‌درمانی بر خودکنترلی نوجوانان بزهکار",
            "objective": "difference",
            "design": "quasi_experimental",
            "sample_size": 36,
            "has_pretest": True
        }
        res = self.engine.process_new_case(case_spec)
        did = res["decision_id"]

        # Simulate Human Saber override due to slope heterogeneity
        outcome = self.engine.record_human_outcome(did, {
            "action": "ADJUST",
            "chosen_method": "Johnson-Neyman Floodlight Technique + Mixed Split-Plot ANOVA",
            "supervisor_accepted": True,
            "divergence_rationale": "Pre-test variance differed significantly between groups, violating ANCOVA slope homogeneity.",
            "lessons_learned": "When youth offender pre-tests show high variance, use Johnson-Neyman."
        })

        self.assertEqual(outcome["alignment_status"], "PARTIAL_ADJUSTMENT (REFINED)")
        self.assertEqual(outcome["knowledge_update"]["type"], "NEW_CASE_SYNTHESIZED")

        # Verify a new case was created and indexed in memory
        new_cases_count = self.engine.case_memory.count()
        self.assertEqual(new_cases_count, initial_cases_count + 1)

        # Query precedents to verify the newly learned case is searchable
        precedents = self.engine.case_memory.search_precedents("نوجوانان بزهکار", top_k=1)
        self.assertGreater(len(precedents), 0)
        self.assertIn("Johnson-Neyman", precedents[0]["case"]["statistical_analysis"])

    def test_04_dynamic_similarity_evaluator_and_rubric(self):
        evaluator = SaberSimilarityEvaluator()
        comp = evaluator.run_comparative_benchmark()

        self.assertIn("generic_baseline_score", comp)
        self.assertIn("digital_saber_score", comp)
        self.assertIn("saber_cognitive_advantage_delta", comp)

        # Digital Saber cognitive reasoners must substantially outperform the generic baseline
        self.assertGreater(comp["digital_saber_score"], comp["generic_baseline_score"])
        self.assertGreater(comp["saber_cognitive_advantage_delta"], 50.0)

        # Verify all 7 core dimensions are present in rubric
        rubric = comp["digital_saber_details"]["itemized_qualitative_rubric"]
        dimensions = [r["dimension"] for r in rubric]
        expected = [
            "statistical_decisions", "research_methodology", "psychometric_decisions",
            "quality_control", "academic_writing", "client_communication", "literature_judgment"
        ]
        for exp in expected:
            self.assertIn(exp, dimensions)


if __name__ == "__main__":
    unittest.main()
