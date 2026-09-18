#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_candidate_falsifier_synthesis.py — Unit Tests for Candidate → Falsifier → Synthesis Pattern

Validates:
1. Competing candidates representation conforming to contracts/analysis_candidate.schema.json
2. Challenger rejection of methodologically flawed candidates (returns REJECTED)
3. Challenger conditional acceptance with actionable conditions (returns CONDITIONAL)
4. Synthesis produces schema-valid AnalysisPlan conforming to contracts/analysis_plan.schema.json
5. Pitfall persistence to state/pitfalls.jsonl conforming to contracts/pitfall.schema.json
6. Reuse of previous pitfalls: Challenger detects and rejects candidates matching historical anti-patterns
7. Phase gate enforcement: AnalysisPlan cannot be created without completing challenge/synthesis
"""

import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        try:
            for entry in os.listdir(venv_lib):
                sp = os.path.join(venv_lib, entry, "site-packages")
                if os.path.isdir(sp) and sp not in sys.path:
                    sys.path.insert(0, sp)
        except OSError:
            pass

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import json
import shutil
import tempfile
import unittest

from scripts.candidate_falsifier_engine import (
    AnalysisCandidate,
    CanonicalPitfallRegistry,
    AcademicChallenger,
    StatisticalMethodologySynthesizer,
    PrematureFinalizationError,
    NoDefensibleCandidateError,
    InvalidCandidateError,
    create_unverified_plan_guard
)
from contracts.contract_validator import (
    validate_analysis_candidate,
    validate_analysis_plan,
    validate_pitfall
)


class TestCandidateFalsifierSynthesis(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_cand_falsifier_")
        self.pitfall_file = os.path.join(self.temp_dir, "pitfalls.jsonl")
        self.registry = CanonicalPitfallRegistry(registry_path=self.pitfall_file)
        self.challenger = AcademicChallenger(pitfall_registry=self.registry)
        self.synthesizer = StatisticalMethodologySynthesizer(pitfall_registry=self.registry)

        # Common study context
        self.study_context = {
            "project_id": "study_mindfulness_anxiety",
            "design_type": "experimental",
            "time_structure": "pre_post_repeated_measures",
            "has_baseline": True,
            "is_randomized": True,
            "sample_size": 80,
            "missing_rate": 0.12  # 12% attrition across waves
        }

        # Candidate A: One-Way ANCOVA (Covariate-adjusted posttest)
        self.candidate_a = AnalysisCandidate(
            candidate_id="CAND-ANCOVA-01",
            method="One-Way ANCOVA",
            research_question="Does mindfulness reduce posttest anxiety controlling for pretest baseline anxiety?",
            estimand="Adjusted Average Treatment Effect (ATE) on posttest anxiety",
            assumptions=[
                "Linear relationship between pretest covariate and posttest outcome",
                "Homogeneity of regression slopes across intervention and control",
                "Homogeneity of variance across groups (Levene p > .05)",
                "Normality of model residuals"
            ],
            data_requirements={
                "variables": ["group", "anxiety_pre", "anxiety_post"],
                "minimum_sample_size": 60,
                "time_structure": "pre_post",
                "measurement_level": "continuous"
            },
            diagnostics=[
                "Group × Covariate interaction test for slope homogeneity",
                "Levene test for homoscedasticity",
                "Residual Q-Q plot and Shapiro-Wilk test"
            ],
            strengths=[
                "Reduces error variance by conditioning on baseline scores",
                "Removes potential baseline imbalance bias",
                "Provides greater statistical power than change score when r < .50"
            ],
            limitations=[
                "Assumes parallel regression slopes",
                "Requires linear association between baseline and outcome"
            ],
            expected_interpretation="Mindfulness intervention group exhibits significantly lower posttest anxiety compared to control after conditioning on baseline levels.",
            execution_requirements={
                "assigned_subagent": "statistics-agent",
                "engine": "python",
                "scripts": ["scripts/run_ancova.py"]
            }
        )

        # Candidate B: One-Way Between-Subjects ANOVA (Omits baseline)
        self.candidate_b = AnalysisCandidate(
            candidate_id="CAND-ANOVA-02",
            method="Between-Subjects ANOVA",
            research_question="Is posttest anxiety different between mindfulness and control groups?",
            estimand="Unadjusted mean difference between groups at posttest",
            assumptions=[
                "Independence of observations",
                "Normality of distribution within groups",
                "Homogeneity of variance"
            ],
            data_requirements={
                "variables": ["group", "anxiety_post"],
                "minimum_sample_size": 50,
                "time_structure": "post_only",
                "measurement_level": "continuous"
            },
            diagnostics=[
                "Levene test for equality of variance",
                "Shapiro-Wilk test of normality"
            ],
            strengths=[
                "Computationally straightforward",
                "Standard undergraduate textbook procedure"
            ],
            limitations=[
                "Completely ignores pretest baseline scores",
                "Inflates error variance and loses statistical power",
                "Vulnerable to pre-existing group differences"
            ],
            expected_interpretation="Posttest anxiety differs significantly between groups.",
            execution_requirements={
                "assigned_subagent": "statistics-agent",
                "engine": "python",
                "scripts": ["scripts/run_anova.py"]
            }
        )

        # Candidate C: Repeated Measures ANOVA with listwise deletion
        self.candidate_c = AnalysisCandidate(
            candidate_id="CAND-RMANOVA-03",
            method="Repeated Measures ANOVA",
            research_question="Do groups change differently from pretest to posttest?",
            estimand="Time by group interaction contrast",
            assumptions=[
                "Sphericity (Mauchly test)",
                "Normality of difference scores",
                "Complete case data (MCAR listwise deletion)"
            ],
            data_requirements={
                "variables": ["group", "anxiety_pre", "anxiety_post"],
                "minimum_sample_size": 70,
                "time_structure": "repeated_measures",
                "measurement_level": "continuous",
                "missing_data_strategy": "listwise_deletion"
            },
            diagnostics=[
                "Mauchly sphericity test",
                "Box M test of covariance equality"
            ],
            strengths=[
                "Traditional repeated measures framework",
                "Explicitly models pre-to-post within-person change"
            ],
            limitations=[
                "Discards all participants with missing posttest data via listwise deletion",
                "Violates MAR missingness assumptions causing attrition bias",
                "Strict sphericity requirements"
            ],
            expected_interpretation="Group by time interaction indicates differential change across conditions.",
            execution_requirements={
                "assigned_subagent": "statistics-agent",
                "engine": "python",
                "scripts": ["scripts/run_rm_anova.py"]
            }
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_competing_candidates_schema_validity(self):
        """All competing candidates must strictly conform to contracts/analysis_candidate.schema.json."""
        for cand in [self.candidate_a, self.candidate_b, self.candidate_c]:
            val = cand.validate()
            self.assertTrue(val["valid"], f"Candidate {cand.candidate_id} failed schema: {val.get('errors')}")

    def test_02_challenger_rejects_flawed_candidates(self):
        """Challenger must actively invalidate Candidate B (omitted baseline) and Candidate C (listwise deletion under 12% missingness)."""
        finding_b = self.challenger.challenge_candidate(self.candidate_b, self.study_context)
        self.assertEqual(finding_b["verdict"], "REJECTED")
        self.assertTrue(len(finding_b["rejection_reasons"]) > 0)
        self.assertTrue(any("baseline" in r.lower() for r in finding_b["rejection_reasons"]))

        finding_c = self.challenger.challenge_candidate(self.candidate_c, self.study_context)
        self.assertEqual(finding_c["verdict"], "REJECTED")
        self.assertTrue(len(finding_c["rejection_reasons"]) > 0)
        self.assertTrue(any("missing" in r.lower() or "listwise" in r.lower() for r in finding_c["rejection_reasons"]))

    def test_03_challenger_conditional_acceptance(self):
        """Challenger evaluates Candidate A (ANCOVA) as CONDITIONAL with required slope homogeneity check."""
        finding_a = self.challenger.challenge_candidate(self.candidate_a, self.study_context)
        self.assertIn(finding_a["verdict"], ["CONDITIONAL", "SUPPORTED"])
        self.assertEqual(len(finding_a["rejection_reasons"]), 0)
        if finding_a["verdict"] == "CONDITIONAL":
            self.assertTrue(len(finding_a["conditions_for_acceptance"]) > 0)
            self.assertTrue(any("slope" in c.lower() or "homogeneity" in c.lower() for c in finding_a["conditions_for_acceptance"]))

    def test_04_expert_synthesis_creates_valid_analysis_plan(self):
        """Synthesizer selects Candidate A, incorporates conditions, and produces schema-valid AnalysisPlan."""
        candidates = [self.candidate_a, self.candidate_b, self.candidate_c]
        synth_res = self.synthesizer.synthesize_and_select(
            candidates=candidates,
            study_context=self.study_context,
            project_id="study_mindfulness_anxiety"
        )

        self.assertEqual(synth_res["status"], "SUCCESS")
        self.assertEqual(synth_res["selected_candidate_id"], "CAND-ANCOVA-01")
        self.assertIn("synthesis_rationale", synth_res)
        self.assertIn("CAND-ANOVA-02", synth_res["synthesis_rationale"])

        # Validate synthesized AnalysisPlan against contracts/analysis_plan.schema.json
        plan = synth_res["analysis_plan"]
        val = validate_analysis_plan(plan)
        self.assertTrue(val["valid"], f"Synthesized AnalysisPlan failed schema: {val.get('errors')}")
        self.assertEqual(plan["decided_by"], "statistical-expert")
        self.assertEqual(plan["statistical_models"][0]["family"], "ancova_analysis_of_covariance")

    def test_05_pitfall_persistence_in_jsonl(self):
        """Rejected candidates must be persisted into state/pitfalls.jsonl conforming to contracts/pitfall.schema.json."""
        candidates = [self.candidate_a, self.candidate_b, self.candidate_c]
        synth_res = self.synthesizer.synthesize_and_select(
            candidates=candidates,
            study_context=self.study_context,
            project_id="study_mindfulness_anxiety"
        )

        # Pitfall registry file must exist and contain entries for rejected candidates
        self.assertTrue(os.path.exists(self.pitfall_file))
        pitfalls = self.registry.load_pitfalls()
        self.assertGreaterEqual(len(pitfalls), 2)

        # Validate each persisted pitfall against contracts/pitfall.schema.json
        for p in pitfalls:
            val_p = validate_pitfall(p)
            self.assertTrue(val_p["valid"], f"Persisted pitfall {p.get('pitfall_id')} failed schema: {val_p.get('errors')}")
            self.assertEqual(p["detected_by"], "academic-challenger")
            self.assertTrue(p["reusable"])

    def test_06_reuse_of_previous_pitfalls_in_future_runs(self):
        """On a subsequent run, Challenger must identify previously rejected approach in pitfalls.jsonl and reject it immediately."""
        # 1. First run persists Candidate B pitfall
        _ = self.challenger.challenge_candidate(self.candidate_b, self.study_context)
        pitfalls_initial = self.registry.load_pitfalls()
        self.assertGreaterEqual(len(pitfalls_initial), 1)

        # 2. Second run: A new proposed candidate attempts the same Between-Subjects ANOVA approach
        candidate_b_clone = AnalysisCandidate(
            candidate_id="CAND-ANOVA-CLONE",
            method="Between-Subjects ANOVA",
            research_question="Does posttest anxiety differ between groups?",
            estimand="Unadjusted posttest difference",
            assumptions=["Normality", "Homoscedasticity"],
            data_requirements={
                "variables": ["group", "anxiety_post"],
                "minimum_sample_size": 40
            },
            diagnostics=["Levene test"],
            strengths=["Simple to run"],
            limitations=["Baseline omitted"],
            expected_interpretation="Difference in posttest score.",
            execution_requirements={"assigned_subagent": "statistics-agent", "engine": "python"}
        )

        # Challenger must detect previous pitfall and reject with citation
        finding_clone = self.challenger.challenge_candidate(candidate_b_clone, self.study_context)
        self.assertEqual(finding_clone["verdict"], "REJECTED")
        self.assertIsNotNone(finding_clone["historical_pitfall_match"])
        self.assertIn("Recurring Pitfall", " ".join(finding_clone["rejection_reasons"]))

    def test_07_all_candidates_rejected_raises_fatal_error(self):
        """If all proposed candidates are flawed, Synthesizer raises NoDefensibleCandidateError and halts."""
        flawed_candidates = [self.candidate_b, self.candidate_c]
        with self.assertRaises(NoDefensibleCandidateError):
            self.synthesizer.synthesize_and_select(
                candidates=flawed_candidates,
                study_context=self.study_context
            )

    def test_08_premature_finalization_is_blocked(self):
        """Attempting to bypass the Challenger/Synthesis phase raises PrematureFinalizationError."""
        with self.assertRaises(PrematureFinalizationError):
            create_unverified_plan_guard()


if __name__ == "__main__":
    unittest.main()
