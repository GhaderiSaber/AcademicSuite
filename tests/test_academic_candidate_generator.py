#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_academic_candidate_generator.py — Unit Tests for GEPA-Inspired Reflective Candidate Generator

Verifies:
1. Multiple candidate improvements generated from a single failure/diagnostic.
2. Canonical active Skill is NEVER modified by the candidate generator.
3. Every candidate contains an empirical testable hypothesis.
4. All required candidate fields exist and strictly satisfy improvement_candidate.schema.json.
5. Reflective diagnosis captures root cause, failure mechanism, and generalizability.
6. Replaceable EvaluationAdapter evaluates candidate mutations without hard external dependencies.
7. All 9 mutation types are supported across the taxonomy.
8. Candidates are staged under learning/candidates/ with an index log.
"""

import os
import sys
import json
import shutil
import hashlib
import tempfile
import unittest
from datetime import datetime, timezone

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from contracts.contract_validator import validate_improvement_candidate
from scripts.academic_candidate_generator import (
    AcademicCandidateGenerator,
    EvaluationAdapter,
    CandidateGenerationError
)


class TestAcademicCandidateGenerator(unittest.TestCase):
    """Authoritative test suite for the Reflective Candidate Generator."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="agy_candidate_gen_test_")
        self.generator = AcademicCandidateGenerator(base_dir=self.temp_dir)

        # Create a mock target skill
        self.target_skill = "statistical-data-analyst"
        self.skill_dir = os.path.join(self.temp_dir, ".agents", "skills", self.target_skill)
        os.makedirs(self.skill_dir, exist_ok=True)
        self.skill_path = os.path.join(self.skill_dir, "SKILL.md")

        self.initial_skill_content = (
            f"---\nname: {self.target_skill}\nversion: 1.0.0\ndescription: Execute statistical analyses.\n---\n\n"
            f"# {self.target_skill}\n\n"
            "## Baseline Procedures\n"
            "1. Ingest dataset and run hypothesis tests.\n"
            "2. Report test statistics and p-values.\n"
        )
        with open(self.skill_path, "w", encoding="utf-8") as f:
            f.write(self.initial_skill_content)

        self.initial_skill_hash = hashlib.sha256(self.initial_skill_content.encode("utf-8")).hexdigest()

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_multiple_candidates_generated_from_single_failure(self):
        """Acceptance Criterion 1: Multiple candidate improvements can be generated from one failure."""
        lesson = {
            "lesson_id": "LSN-20260918-MODEL-COMP",
            "target_capability": self.target_skill,
            "what_happened": "Repeated-measures ANOVA was used despite missing waves across timepoints.",
            "what_behavior_caused_outcome": "Selected RM-ANOVA blindly without comparing against LMM.",
            "what_should_have_happened": "Compare LMM vs RM-ANOVA against missingness, imbalance, covariance, and estimand."
        }
        diagnostic = {
            "failure_type": "unjustified_model_selection_without_comparison",
            "evidence": "Selected analytical model without explicit comparative evaluation of candidate models."
        }

        candidates = self.generator.run_reflective_evolution(
            target_skill=self.target_skill,
            relevant_lessons=[lesson],
            evaluation_diagnostics=[diagnostic],
            parent_version="v1.0.0"
        )

        self.assertGreaterEqual(len(candidates), 3, "Must generate at least 3 distinct candidate improvements.")
        mutation_types = [c["mutation_type"] for c in candidates]
        self.assertEqual(len(mutation_types), len(set(mutation_types)), "Candidate mutation types must be distinct.")

    def test_02_canonical_skill_never_directly_modified(self):
        """Acceptance Criterion 2: The canonical Skill is never directly modified by the proposer."""
        lesson = {
            "lesson_id": "LSN-20260918-IMMUTABLE",
            "what_happened": "Homogeneity of slopes test omitted.",
            "what_behavior_caused_outcome": "Interpreted ANCOVA under slope violation."
        }

        self.generator.run_reflective_evolution(
            target_skill=self.target_skill,
            relevant_lessons=[lesson]
        )

        # Invariant: Skill on disk must have identical content and hash
        with open(self.skill_path, "r", encoding="utf-8") as f:
            current_content = f.read()

        current_hash = hashlib.sha256(current_content.encode("utf-8")).hexdigest()
        self.assertEqual(
            current_hash,
            self.initial_skill_hash,
            "Canonical Skill was mutated! Proposer must NEVER directly modify active Skill files."
        )

    def test_03_every_candidate_contains_testable_hypothesis(self):
        """Acceptance Criterion 3: Every candidate contains a testable hypothesis."""
        lesson = {
            "lesson_id": "LSN-20260918-HYP",
            "what_happened": "Blind model selection.",
            "what_behavior_caused_outcome": "Omitted model comparison."
        }

        candidates = self.generator.run_reflective_evolution(
            target_skill=self.target_skill,
            relevant_lessons=[lesson]
        )

        for cand in candidates:
            hyp = cand.get("testable_hypothesis", "")
            self.assertTrue(len(hyp.strip()) > 20, f"Candidate {cand['candidate_id']} lacks substantial hypothesis.")
            self.assertTrue(
                "if" in hyp.lower() and "will" in hyp.lower(),
                f"Hypothesis must formulate an 'If ... then ... will' empirical prediction: {hyp}"
            )

    def test_04_candidate_schema_contract_compliance(self):
        """Candidates must contain all required fields and pass improvement_candidate.schema.json."""
        lesson = {
            "lesson_id": "LSN-20260918-SCHEMA",
            "what_happened": "Missingness omitted.",
            "what_behavior_caused_outcome": "Omitted MCAR test."
        }

        candidates = self.generator.run_reflective_evolution(
            target_skill=self.target_skill,
            relevant_lessons=[lesson]
        )

        for cand in candidates:
            # Check mandatory fields
            self.assertIn("candidate_id", cand)
            self.assertIn("parent_version", cand)
            self.assertIn("target_skill", cand)
            self.assertIn("mutation", cand)
            self.assertEqual(cand["mutation"]["diff_type"], "UNIFIED_DIFF")
            self.assertIn("rationale", cand)
            self.assertIn("source_lessons", cand)
            self.assertIn("expected_benefit", cand)
            self.assertIn("possible_downside", cand)
            self.assertIn("reflective_diagnosis", cand)

            # Contract validation
            val_res = validate_improvement_candidate(cand)
            self.assertTrue(
                val_res["valid"],
                f"Candidate {cand['candidate_id']} failed contract validation: {val_res.get('errors')}"
            )

    def test_05_candidates_persisted_to_learning_candidates_directory(self):
        """Candidates must be written to learning/candidates/<candidate_id>.json."""
        lesson = {
            "lesson_id": "LSN-20260918-DIR",
            "what_happened": "Missing model comparison.",
            "what_behavior_caused_outcome": "Omitted RM-ANOVA vs LMM evaluation."
        }

        candidates = self.generator.run_reflective_evolution(
            target_skill=self.target_skill,
            relevant_lessons=[lesson]
        )

        for cand in candidates:
            cand_path = os.path.join(self.generator.candidates_dir, f"{cand['candidate_id']}.json")
            self.assertTrue(os.path.isfile(cand_path), f"Candidate file {cand_path} must exist on disk.")

        # Index file must record all candidates
        self.assertTrue(os.path.isfile(self.generator.index_file))
        with open(self.generator.index_file, "r", encoding="utf-8") as f:
            lines = [json.loads(l) for l in f if l.strip()]
        self.assertEqual(len(lines), len(candidates))

    def test_06_reflective_diagnosis_captures_root_cause_and_mechanism(self):
        """Reflective diagnosis must capture root cause, failure mechanism, and generalizability."""
        diagnostics = [
            {"failure_type": "missing_reasoning_property", "evidence": "Failed to consider candidate model comparison."},
            {"failure_type": "unjustified_model_selection_without_comparison", "evidence": "Selected RM-ANOVA without checking LMM."}
        ]
        lessons = [
            {
                "lesson_id": "LSN-20260918-REFL",
                "what_happened": "Selected RM-ANOVA blindly.",
                "what_behavior_caused_outcome": "Did not compare LMM."
            }
        ]

        reflection = self.generator.reflect_on_evidence(
            target_skill=self.target_skill,
            relevant_lessons=lessons,
            failed_trajectories=[],
            evaluation_diagnostics=diagnostics,
            anti_patterns=[]
        )

        self.assertIn("root_cause", reflection)
        self.assertIn("failure_mechanism", reflection)
        self.assertIn("generalizability", reflection)
        self.assertIn("evidence_sources", reflection)
        self.assertTrue(len(reflection["root_cause"]) > 15)

    def test_07_all_nine_mutation_types_supported(self):
        """Engine must support generating candidates across all 9 specified mutation types."""
        reflection = {
            "root_cause": "Methodological gap in longitudinal modeling",
            "failure_mechanism": "Default model selection without comparative verification",
            "generalizability": "Applies across all repeated measures studies"
        }

        candidates = self.generator.generate_candidate_mutations(
            target_skill=self.target_skill,
            current_skill_content=self.initial_skill_content,
            parent_version="v1.0.0",
            reflection=reflection,
            source_lessons=[{"lesson_id": "LSN-TEST-ALL-9"}],
            mutation_types=AcademicCandidateGenerator.MUTATION_TYPES
        )

        self.assertEqual(len(candidates), 9)
        generated_types = [c["mutation_type"] for c in candidates]
        for mt in AcademicCandidateGenerator.MUTATION_TYPES:
            self.assertIn(mt, generated_types)

    def test_08_replaceable_evaluation_adapter(self):
        """EvaluationAdapter must evaluate candidate mutations against the evaluation lab."""
        adapter = EvaluationAdapter(base_dir=self.temp_dir)
        mock_cand = {
            "candidate_id": "CAND-ADAPTER-TEST",
            "target_skill": self.target_skill,
            "mutation_type": "DECISION_TREE_ADDITION",
            "mutation": {"diff_type": "UNIFIED_DIFF", "content": "--- a +++ b"},
            "expected_improvement": {"target_metric": "diagnostic_pass_rate"}
        }

        result = adapter.evaluate_candidate(mock_cand)
        self.assertIn("verdict", result)
        self.assertIn("pass_rate", result)


if __name__ == "__main__":
    unittest.main()
