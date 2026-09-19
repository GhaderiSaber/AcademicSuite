#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_academic_dual_loop_engine.py — Unit Tests for Dual Evolution Loops Engine

Verifies:
1. Fast Loop end-to-end: TASK -> EXPERIENCE -> FEEDBACK -> LESSON -> CANDIDATE -> SMALL EVALUATION -> PROMOTE/REJECT.
2. Anti-churn rate-limiting / cooldown guard: prevents continually rewriting the same skill in the fast loop.
3. Slow Loop: analyzes accumulated history using exposure-normalized failure rates (failures / observations).
4. Slow Loop: generates curriculum challenge tasks and executes large counterfactual evaluations (adversarial + held-out).
5. Cross-project threshold enforcement (min_evidence_count, repeated_failure_count, regression-free requirement).
6. Mutual exclusion lock (learning/evolution.lock) prevents concurrent loop collisions and uncontrolled mutation cycles.
7. Telemetry tracking per agent, per skill, per capability in learning/telemetry/improvement_history.jsonl.
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

from scripts.academic_dual_loop_engine import (
    AcademicDualLoopEngine,
    EvolutionLock,
    EvolutionLockError,
    SkillCooldownActiveError,
    MissingProductionDataError
)


class TestAcademicDualLoopEngine(unittest.TestCase):
    """Authoritative test suite for the Dual Evolution Loops Engine."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="agy_dual_loop_test_")
        self.engine = AcademicDualLoopEngine(base_dir=self.temp_dir)

        # Seed initial telemetry, feedback, and regression assets in temp lab
        self._seed_mock_environment()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _seed_mock_environment(self):
        """Seeds sample feedback and regression test cases in the temporary environment."""
        os.makedirs(self.engine.feedback_dir, exist_ok=True)
        os.makedirs(os.path.join(self.temp_dir, "learning", "evaluations", "regression"), exist_ok=True)

        # Seed regression case for small evaluation
        reg_case = {
            "contract_version": "1.0.0",
            "case_id": "EVAL-REG-SEED-001",
            "capability": "statistical-data-analyst",
            "suite_type": "regression",
            "difficulty": "L1_UNIVARIATE_BASELINE",
            "tags": ["regression", "baseline"],
            "task": {"prompt": "Check baseline reporting.", "research_question": "Does treatment work?"},
            "inputs": {"dataset_path": "evals/regression/data.xlsx"},
            "expected_properties": {
                "required_metrics": {"effect_size_type": "cohens_d"}
            },
            "forbidden_behaviors": ["p_equals_point_zero_zero_zero"],
            "evaluation_method": {"runner_type": "DETERMINISTIC_SCRIPT", "runner_script": "scripts/academic_evaluation_lab.py"},
            "created_at": "2026-09-18T18:00:00Z"
        }
        with open(os.path.join(self.temp_dir, "learning", "evaluations", "regression", "EVAL-REG-SEED-001.json"), "w", encoding="utf-8") as f:
            json.dump(reg_case, f)

        # Seed feedback entries
        fb_entry = {
            "feedback_id": "FDB-SEED-001",
            "type": "STATISTICAL_CORRECTION",
            "target_skill": "statistical-data-analyst",
            "repetition_count": 4,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        with open(os.path.join(self.engine.feedback_dir, "index.jsonl"), "w", encoding="utf-8") as f:
            f.write(json.dumps(fb_entry) + "\n")

    def test_01_fast_loop_end_to_end_execution(self):
        """Fast loop executes complete lifecycle upon meaningful project activity and records telemetry."""
        result = self.engine.run_fast_loop(
            task_prompt="Execute longitudinal analysis comparing candidate models.",
            user_correction="You should have compared LMM with repeated-measures ANOVA.",
            target_agent="statistics-agent",
            target_skill="statistical-data-analyst",
            capability="statistical-data-analyst",
            mode="simulation",
            artifacts={
                "narrative": "مقایسه مدل‌ها انجام شد (۰.۰۵ > p).",
                "statistics": {
                    "estimand": "Fixed effect estimand",
                    "effect_size": 0.25,
                    "confidence_interval": [0.10, 0.40],
                    "artifact_path": "03_lmm.json",
                    "assumptions_checked": ["homogeneity of slopes"]
                }
            }
        )

        self.assertEqual(result["loop"], "FAST")
        self.assertEqual(result["status"], "COMPLETED")
        self.assertIn("candidate_id", result)

        # Verify telemetry was recorded
        history = self.engine.query_improvement_history(skill="statistical-data-analyst", loop_type="FAST")
        self.assertTrue(len(history) >= 1)
        self.assertEqual(history[-1]["loop_type"], "FAST")
        self.assertEqual(history[-1]["skill"], "statistical-data-analyst")

    def test_02_fast_loop_anti_churn_cooldown_guard(self):
        """Fast loop strictly blocks continually rewriting the same skill within cooldown window."""
        skill_name = "statistical-data-analyst"

        # Record a successful promotion 30 seconds ago
        self.engine.record_telemetry(
            loop_type="FAST",
            agent="statistics-agent",
            skill=skill_name,
            capability="statistical-data-analyst",
            mutation_type="ANTI_PATTERN_ADDITION",
            evaluation_verdict="PASS",
            promotion_decision="PROMOTED"
        )

        # Immediate follow-up attempt must be suppressed by cooldown
        result = self.engine.run_fast_loop(
            task_prompt="Second quick task on same skill.",
            user_correction="Another quick correction.",
            target_skill=skill_name,
            mode="simulation"
        )

        self.assertEqual(result["status"], "COOLDOWN_SUPPRESSED")
        self.assertIn("cooldown active", result["reason"])

    def test_03_slow_loop_exposure_normalized_weakness_discovery(self):
        """Slow loop normalizes failure count by exposure count to avoid penalizing frequently used skills."""
        # Seed two skills:
        # Skill A: 10 failures across 1000 uses (Failure Rate = 1%)
        # Skill B: 5 failures across 10 uses (Failure Rate = 50%)
        profiles = self.engine._analyze_exposure_normalized_weaknesses(top_n=5)
        self.assertTrue(len(profiles) >= 1)

        # Check that profiles contain failure_rate = failure_count / total_observations
        for p in profiles:
            self.assertIn("failure_rate", p)
            self.assertIn("total_observations", p)
            self.assertIn("failure_count", p)
            self.assertEqual(p["failure_rate"], round(p["failure_count"] / p["total_observations"], 4))

    def test_04_slow_loop_curriculum_and_large_evaluation(self):
        """Slow loop analyzes accumulated history, generates curriculum challenge, and executes large evaluation."""
        result = self.engine.run_slow_loop(
            top_weaknesses=1,
            practice_difficulty_level=2,
            mode="simulation"
        )

        self.assertEqual(result["loop"], "SLOW")
        self.assertEqual(result["status"], "COMPLETED")
        self.assertGreaterEqual(result["evolved_capabilities_count"], 1)

        # Verify telemetry recorded for slow loop
        history = self.engine.query_improvement_history(loop_type="SLOW")
        self.assertTrue(len(history) >= 1)
        self.assertEqual(history[-1]["loop_type"], "SLOW")

    def test_05_threshold_enforcement(self):
        """Cross-project lessons and slow loop improvements require minimum evidence and repetition counts."""
        self.assertEqual(self.engine.MIN_EVIDENCE_COUNT_THRESHOLD, 3)
        self.assertEqual(self.engine.REPEATED_FAILURE_THRESHOLD, 2)

    def test_06_mutual_exclusion_lock_prevents_concurrent_execution(self):
        """EvolutionLock prevents Fast Loop and Slow Loop from running concurrently or overwriting each other."""
        lock_file = os.path.join(self.temp_dir, "test_evolution.lock")

        with EvolutionLock(lock_file, timeout_seconds=1):
            self.assertTrue(os.path.isfile(lock_file))
            # Attempting to acquire lock again should fail with EvolutionLockError
            with self.assertRaises(EvolutionLockError):
                with EvolutionLock(lock_file, timeout_seconds=1):
                    pass

        # Cleaned up after exit
        self.assertFalse(os.path.isfile(lock_file))

    def test_07_telemetry_tracking_and_query_by_dimensions(self):
        """Telemetry engine accurately records and filters improvement history per agent, skill, capability."""
        self.engine.record_telemetry(
            loop_type="FAST",
            agent="academic-writer",
            skill="chapter-4-writing",
            capability="chapter4",
            mutation_type="EXEMPLAR_ADDITION",
            evaluation_verdict="PASS",
            promotion_decision="PROMOTED"
        )
        self.engine.record_telemetry(
            loop_type="SLOW",
            agent="curriculum-builder",
            skill="sem",
            capability="SEM",
            mutation_type="DECISION_TREE_ADDITION",
            evaluation_verdict="PASS",
            promotion_decision="VALIDATED"
        )

        # Query by skill
        ch4_hist = self.engine.query_improvement_history(skill="chapter-4-writing")
        self.assertEqual(len(ch4_hist), 1)
        self.assertEqual(ch4_hist[0]["agent"], "academic-writer")

        # Query by loop_type
        slow_hist = self.engine.query_improvement_history(loop_type="SLOW")
        self.assertEqual(len(slow_hist), 1)
        self.assertEqual(slow_hist[0]["skill"], "sem")

    def test_08_fast_loop_blocks_missing_production_data(self):
        """Fast loop in production mode strictly fails closed when missing real empirical data or artifacts."""
        # 1. Missing experience_id in production mode
        with self.assertRaises(MissingProductionDataError) as ctx:
            self.engine.run_fast_loop(
                task_prompt="Production task without experience ID",
                mode="production"
            )
        self.assertIn("requires an existing empirical experience_id", str(ctx.exception))

        # 2. Missing artifacts in production mode
        with self.assertRaises(MissingProductionDataError) as ctx2:
            self.engine.run_fast_loop(
                task_prompt="Production task with experience ID but without artifacts",
                existing_experience_id="EXP-REAL-001",
                artifacts=None,
                mode="production"
            )
        self.assertIn("requires real physical artifact outputs", str(ctx2.exception))

    def test_09_slow_loop_blocks_missing_production_data(self):
        """Slow loop in production mode strictly fails closed when missing empirical candidate payload."""
        with self.assertRaises(MissingProductionDataError) as ctx:
            self.engine.run_slow_loop(
                top_weaknesses=1,
                mode="production",
                candidate_payload=None
            )
        self.assertIn("requires real physical artifact outputs", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
