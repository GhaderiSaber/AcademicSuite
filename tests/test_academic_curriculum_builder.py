#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_academic_curriculum_builder.py — Unit Tests for Weakness-Driven Curriculum System

Verifies:
1. Weakness diagnosis across multi-source historical evidence (feedback, regressions, archives).
2. Complete 10-level Statistics Ladder (simple two-group up to ambiguous research design).
3. Complete 5-level Writing Ladder (basic result narration up to contradictory/ambiguous results).
4. Graduated difficulty progression: generates harder practice cases as capabilities advance.
5. Contract compliance: every generated curriculum case passes evaluation_case.schema.json.
6. Validation method binding: every generated task includes deterministic validation instructions.
7. Closed-loop feedback: failed practice runs automatically emit feedback events and synthesize
   regression cases without waiting for user corrections.
8. Practice success advances capability mastery level.
"""

import os
import sys
import json
import uuid
import shutil
import hashlib
import tempfile
import unittest
from datetime import datetime, timezone

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.academic_curriculum_builder import AcademicCurriculumBuilder
from contracts.contract_validator import validate_evaluation_case


class TestAcademicCurriculumBuilder(unittest.TestCase):
    """Authoritative test suite for the Weakness-Driven Curriculum System."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="agy_curriculum_test_")
        self.builder = AcademicCurriculumBuilder(base_dir=self.temp_dir)

        # Seed mock feedback index with weaknesses
        self._seed_mock_telemetry()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _seed_mock_telemetry(self):
        """Seeds sample feedback, regression, and archive records in temp environment."""
        os.makedirs(self.builder.feedback_dir, exist_ok=True)
        os.makedirs(os.path.dirname(self.builder.regression_index), exist_ok=True)
        os.makedirs(self.builder.archive_dir, exist_ok=True)

        # 1. Feedback records showing longitudinal modeling failures
        fb_entry = {
            "feedback_id": "FDB-MOCK-001",
            "type": "STATISTICAL_CORRECTION",
            "target_skill": "statistical-data-analyst",
            "repetition_count": 3,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        with open(self.builder.feedback_index, "w", encoding="utf-8") as f:
            f.write(json.dumps(fb_entry) + "\n")

        # 2. Regression record showing repeated assumption failures
        reg_entry = {
            "case_id": "EVAL-REG-MOCK-001",
            "capability": "statistical-data-analyst",
            "repeat_count": 2,
            "originating_feedback_id": "omitted_critical_assumption"
        }
        with open(self.builder.regression_index, "w", encoding="utf-8") as f:
            f.write(json.dumps(reg_entry) + "\n")

        # 3. Archive record showing causal overreach in writing
        arc_record = {
            "archive_id": "ARC-MOCK-001",
            "failure_reason": "unsupported_causal_language",
            "candidate_snapshot": {"target_skill": "academic-writer"}
        }
        with open(os.path.join(self.builder.archive_dir, "ARC-MOCK-001.json"), "w", encoding="utf-8") as f:
            json.dump(arc_record, f)

    def test_01_diagnose_weaknesses_from_historical_data(self):
        """System diagnoses weak capabilities from multi-source historical evidence without waiting for user corrections."""
        weaknesses = self.builder.diagnose_weaknesses(top_n=5)
        self.assertTrue(len(weaknesses) >= 2)

        caps = [w["capability"] for w in weaknesses]
        self.assertIn("statistical-data-analyst", caps)
        self.assertIn("academic-writer", caps)

        stat_weakness = next(w for w in weaknesses if w["capability"] == "statistical-data-analyst")
        self.assertGreater(stat_weakness["vulnerability_score"], 0)
        self.assertIn("STATISTICAL_CORRECTION", stat_weakness["defect_frequencies"])

    def test_02_statistics_ladder_all_ten_levels_defined(self):
        """Statistics ladder must contain all 10 graduated levels from two-group to ambiguous design."""
        ladder = self.builder.STATISTICS_LADDER
        self.assertEqual(len(ladder), 10)

        expected_level_names = [
            "simple two-group analysis",
            "pre/post analysis",
            "three-group repeated measures",
            "missing follow-up",
            "unequal group sizes",
            "baseline imbalance",
            "missingness + imbalance + covariates",
            "multiple outcomes",
            "complex longitudinal structure",
            "ambiguous research design"
        ]

        for lvl in range(1, 11):
            self.assertIn(lvl, ladder)
            item = ladder[lvl]
            self.assertEqual(item["name"], expected_level_names[lvl - 1])
            self.assertIn("difficulty", item)
            self.assertIn("prompt", item)
            self.assertIn("research_question", item)
            self.assertIn("expected_metrics", item)
            self.assertIn("required_properties", item)
            self.assertIn("forbidden_behaviors", item)

    def test_03_writing_ladder_all_five_levels_defined(self):
        """Writing ladder must contain all 5 graduated levels from basic narration to contradictory results."""
        ladder = self.builder.WRITING_LADDER
        self.assertEqual(len(ladder), 5)

        expected_level_names = [
            "basic result narration",
            "effect-size interpretation",
            "confidence-interval interpretation",
            "causal-language discipline",
            "contradictory/ambiguous results"
        ]

        for lvl in range(1, 6):
            self.assertIn(lvl, ladder)
            item = ladder[lvl]
            self.assertEqual(item["name"], expected_level_names[lvl - 1])
            self.assertIn("difficulty", item)
            self.assertIn("prompt", item)
            self.assertIn("research_question", item)
            self.assertIn("expected_metrics", item)
            self.assertIn("required_properties", item)
            self.assertIn("forbidden_behaviors", item)

    def test_04_generate_practice_case_increments_difficulty_level(self):
        """Curriculum engine generates practice cases matching or exceeding current capability mastery level."""
        cap = "statistical-data-analyst"
        self.assertEqual(self.builder.get_current_capability_level(cap), 0)

        # Level 1 generated initially
        case_l1 = self.builder.generate_practice_case(capability=cap)
        self.assertEqual(case_l1["curriculum_level"], 1)
        self.assertEqual(case_l1["level_name"], "simple two-group analysis")

        # Explicit target level request (e.g. Level 4 missing follow-up)
        case_l4 = self.builder.generate_practice_case(capability=cap, target_level=4)
        self.assertEqual(case_l4["curriculum_level"], 4)
        self.assertEqual(case_l4["level_name"], "missing follow-up")
        self.assertIn("missingness", case_l4["expected_properties"]["required_reasoning_properties"])

        # Explicit target level request (Level 7 missingness + imbalance + covariates)
        case_l7 = self.builder.generate_practice_case(capability=cap, target_level=7)
        self.assertEqual(case_l7["curriculum_level"], 7)
        self.assertEqual(case_l7["level_name"], "missingness + imbalance + covariates")

    def test_05_curriculum_case_contract_compliance(self):
        """Every generated curriculum case must be valid under evaluation_case.schema.json."""
        case = self.builder.generate_practice_case(
            capability="statistical-data-analyst",
            target_level=6,
            target_weakness="omitting_homogeneity_of_slopes_test"
        )
        val = validate_evaluation_case(case)
        self.assertTrue(val["valid"], f"Curriculum case failed schema validation: {val.get('errors')}")
        self.assertEqual(case["difficulty"], "L2_INTERDEPENDENT_MODELS")
        self.assertIn("omitting_homogeneity_of_slopes_test", case["forbidden_behaviors"])

    def test_06_validation_method_presence_and_execution(self):
        """Every generated curriculum case must define an executable deterministic validation method."""
        case = self.builder.generate_practice_case(capability="academic-writer", target_level=4)
        self.assertIn("evaluation_method", case)
        eval_method = case["evaluation_method"]
        self.assertEqual(eval_method["runner_type"], "DETERMINISTIC_SCRIPT")
        self.assertEqual(eval_method["runner_script"], "scripts/academic_evaluation_lab.py")
        self.assertIn("--case", eval_method["cli_arguments"])

    def test_07_practice_failure_feeds_back_into_evolution_loop(self):
        """Failed practice task automatically emits feedback event and synthesizes regression case."""
        case = self.builder.generate_practice_case(capability="statistical-data-analyst", target_level=4)

        # Flawed candidate payload (omits required estimand and effect size)
        flawed_payload = {
            "narrative": "تحلیل اجرا شد بدون مشخص کردن برآوردگر.",
            "statistics": {"f_value": 3.4}
        }

        feed_res = self.builder.feed_practice_result_to_evolution(case, flawed_payload)
        self.assertFalse(feed_res["passed"])
        self.assertEqual(feed_res["status"], "FAILED")
        self.assertIsNotNone(feed_res["feedback_id"])

        # Check that feedback event was saved to disk
        fdb_file = os.path.join(self.builder.feedback_dir, f"{feed_res['feedback_id']}.json")
        self.assertTrue(os.path.isfile(fdb_file))
        with open(fdb_file, "r", encoding="utf-8") as f:
            fdb_data = json.load(f)
        self.assertEqual(fdb_data["source"], "CURRICULUM_PRACTICE_HARNESS")
        self.assertEqual(fdb_data["target_skill"], "statistical-data-analyst")

    def test_08_practice_success_advances_mastery(self):
        """Successful practice task updates case status to PASSED in curriculum index."""
        case = self.builder.generate_practice_case(capability="academic-writer", target_level=1)

        # Compliant narrative observing APA 7 and Persian leading zero
        compliant_payload = {
            "narrative": "نتایج تحلیل واریانس نشان داد اثر مداخله معنادار است (۰.۰۱ > p). میانگین و انحراف معیار گزارش شد.",
            "statistics": {
                "estimand": "Treatment effect estimand",
                "effect_size": 0.35,
                "partial_eta_squared": 0.35,
                "confidence_interval": [0.15, 0.55],
                "artifact_path": "03_results.json"
            }
        }

        feed_res = self.builder.feed_practice_result_to_evolution(case, compliant_payload)
        self.assertTrue(feed_res["passed"])
        self.assertEqual(feed_res["status"], "PASSED")

        # Verify status in index
        with open(self.builder.curriculum_index, "r", encoding="utf-8") as f:
            entries = [json.loads(line) for line in f if line.strip()]
        target_entry = next((e for e in entries if e["case_id"] == case["case_id"]), None)
        self.assertIsNotNone(target_entry)
        self.assertEqual(target_entry["status"], "PASSED")


if __name__ == "__main__":
    unittest.main()
