#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_pitfall_registry.py — Comprehensive Unit Tests for Academic Pitfall Registry

Verifies:
1. create: Record creation with all 11 fields conforming to contracts/pitfall.schema.json.
2. read: Reading and parsing from JSONL storage.
3. query: Deterministic query filtering across category, project, milestone, detected_by, reusable, keywords.
4. duplicate: Detection of duplicate pitfall_id on creation and during reading.
5. resolution: Resolution lifecycle tracking and schema validation updates.
6. reuse: Surfacing rejected approaches across workflows and preventing invalid recurrence.
7. invalid record: Schema violations fail closed (PitfallSchemaValidationError).
8. malformed jsonl: Corrupted lines fail closed (MalformedPitfallError).
9. five defect categories: Methodological, statistical, execution, evidence, and validation.
10. academic challenger integration: Challenger records findings and queries registry to invalidate recurring candidates.
11. state machine integration: StrictStateMachine delegates pitfall operations seamlessly.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
from datetime import datetime, timezone

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT_DIR, ".agents", "scripts"))
sys.path.insert(0, os.path.join(ROOT_DIR, "scripts"))

from academic_pitfall_registry import (
    AcademicPitfallRegistry,
    PitfallError,
    PitfallSchemaValidationError,
    DuplicatePitfallError,
    MalformedPitfallError,
    InvalidPitfallQueryError,
    PitfallNotFoundError,
    VALID_CATEGORIES,
)
from candidate_falsifier_engine import (
    AcademicChallenger,
    CanonicalPitfallRegistry,
)
from academic_state_manager import StrictStateMachine


class TestPitfallRegistry(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_pitfalls_")
        self.state_dir = os.path.join(self.temp_dir, "state")
        os.makedirs(self.state_dir, exist_ok=True)
        self.pitfalls_path = os.path.join(self.state_dir, "pitfalls.jsonl")
        self.registry = AcademicPitfallRegistry(self.pitfalls_path, project_id="proj_study_alpha")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_create_pitfall_with_all_11_fields(self):
        """Validates creation of a pitfall record with all 11 required/structured fields."""
        rec = self.registry.create(
            candidate_approach="Repeated-Measures Post-Hoc Only ANOVA",
            problem="Omission of baseline covariate introduces regression to the mean bias.",
            evidence={
                "description": "Baseline pre-test variance accounts for 34% of outcome variance.",
                "metric_or_statistic": "baseline_r2",
                "observed_value": "0.34",
                "threshold_value": "0.10"
            },
            corrective_action="Use Baseline-Adjusted ANCOVA (GLM) with pre-test score as covariate.",
            adapted_approach="ANCOVA with baseline covariate and homogeneity check",
            detected_by="academic-challenger",
            category="methodological",
            stage="06_hypothesis_testing",
            milestone="M_HYPOTHESIS_TESTING",
            project="proj_study_alpha",
            reusable=True,
            pitfall_id="PIT-TEST-001",
            timestamp="2026-09-18T10:00:00Z",
            verification_check="Verify regression slope homogeneity across experimental groups.",
            related_artifacts=["artifacts/results_ancova.json", "tables/table_1.docx"]
        )

        # Verify all 11 attributes
        self.assertEqual(rec["pitfall_id"], "PIT-TEST-001")
        self.assertEqual(rec["project"], "proj_study_alpha")
        self.assertEqual(rec["milestone"], "M_HYPOTHESIS_TESTING")
        self.assertEqual(rec["candidate_approach"], "Repeated-Measures Post-Hoc Only ANOVA")
        self.assertEqual(rec["detected_by"], "academic-challenger")
        self.assertIn("baseline covariate", rec["problem"])
        self.assertIn("baseline_r2", rec["evidence"]["metric_or_statistic"])
        self.assertEqual(rec["resolution"]["corrective_action"], "Use Baseline-Adjusted ANCOVA (GLM) with pre-test score as covariate.")
        self.assertTrue(rec["reusable"])
        self.assertEqual(rec["timestamp"], "2026-09-18T10:00:00Z")
        self.assertEqual(len(rec["related_artifacts"]), 2)
        self.assertEqual(rec["category"], "methodological")

    def test_02_read_pitfalls_from_disk(self):
        """Validates reading and parsing persisted records from disk."""
        self.registry.create(
            candidate_approach="Approach A",
            problem="Issue A",
            evidence="Evidence text A",
            corrective_action="Action A",
            adapted_approach="Adapted A",
            pitfall_id="PIT-READ-01"
        )
        self.registry.create(
            candidate_approach="Approach B",
            problem="Issue B",
            evidence="Evidence text B",
            corrective_action="Action B",
            adapted_approach="Adapted B",
            pitfall_id="PIT-READ-02"
        )

        records = self.registry.read(validate_schema=True)
        self.assertEqual(len(records), 2)
        ids = [r["pitfall_id"] for r in records]
        self.assertIn("PIT-READ-01", ids)
        self.assertIn("PIT-READ-02", ids)

        # Single get
        single = self.registry.get("PIT-READ-01")
        self.assertEqual(single["candidate_approach"], "Approach A")

        with self.assertRaises(PitfallNotFoundError):
            self.registry.get("PIT-NON-EXISTENT")

    def test_03_query_by_category_project_milestone_and_keyword(self):
        """Validates deterministic querying across category, project, milestone, reusable, and keywords."""
        self.registry.create(
            candidate_approach="Pairwise t-tests without correction",
            problem="Family-wise error rate inflation across 10 contrasts.",
            evidence="alpha_inflation > 0.40",
            corrective_action="Apply Holm-Bonferroni stepdown correction.",
            adapted_approach="Corrected contrasts",
            category="statistical",
            project="proj_alpha",
            milestone="M_STATS",
            reusable=True,
            pitfall_id="PIT-Q-01"
        )
        self.registry.create(
            candidate_approach="Complete Case Listwise Deletion",
            problem="15% missingness violates MCAR assumption and drops power.",
            evidence="missingness_pct = 15%",
            corrective_action="Use Multiple Imputation with 20 chained iterations (MICE).",
            adapted_approach="Multiple Imputation (MICE)",
            category="methodological",
            project="proj_beta",
            milestone="M_DATA",
            reusable=True,
            pitfall_id="PIT-Q-02"
        )
        self.registry.create(
            candidate_approach="Ad-hoc Python Emulator Runner",
            problem="Violated Directive 12.1 sole orchestrator mandate.",
            evidence="custom python agent dispatcher found",
            corrective_action="Use native Antigravity invoke_subagent orchestration.",
            adapted_approach="Native orchestration",
            category="execution",
            project="proj_alpha",
            milestone="M_EXEC",
            reusable=False,
            pitfall_id="PIT-Q-03"
        )

        # Query by category
        stat_results = self.registry.query(category="statistical")
        self.assertEqual(len(stat_results), 1)
        self.assertEqual(stat_results[0]["pitfall_id"], "PIT-Q-01")

        # Query by project
        alpha_results = self.registry.query(project="proj_alpha")
        self.assertEqual(len(alpha_results), 2)

        # Query by milestone
        data_results = self.registry.query(milestone="M_DATA")
        self.assertEqual(len(data_results), 1)
        self.assertEqual(data_results[0]["pitfall_id"], "PIT-Q-02")

        # Query by reusable
        reusable_results = self.registry.query(reusable=True)
        self.assertEqual(len(reusable_results), 2)

        # Query by keyword
        missing_results = self.registry.query(keyword="missingness")
        self.assertEqual(len(missing_results), 1)
        self.assertEqual(missing_results[0]["pitfall_id"], "PIT-Q-02")

        # Invalid query category fails closed
        with self.assertRaises(InvalidPitfallQueryError):
            self.registry.query(category="invalid_category_xyz")

    def test_04_duplicate_pitfall_detection(self):
        """Validates that duplicate pitfall IDs are rejected both on create and read."""
        self.registry.create(
            candidate_approach="Method Alpha",
            problem="Issue Alpha",
            evidence="Evidence Alpha",
            corrective_action="Action Alpha",
            adapted_approach="Adapted Alpha",
            pitfall_id="PIT-DUP-01"
        )

        # Duplicate create in same session
        with self.assertRaises(DuplicatePitfallError):
            self.registry.create(
                candidate_approach="Method Alpha 2",
                problem="Issue Alpha 2",
                evidence="Evidence Alpha 2",
                corrective_action="Action Alpha 2",
                adapted_approach="Adapted Alpha 2",
                pitfall_id="PIT-DUP-01"
            )

        # Duplicate manually appended to file
        with open(self.pitfalls_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "contract_version": "1.0.0",
                "pitfall_id": "PIT-DUP-01",
                "project": "proj_other",
                "milestone": "M_TEST",
                "stage": "M_TEST",
                "category": "methodological",
                "candidate_approach": "Manual Dup",
                "detected_by": "tester",
                "problem": "Manual Duplicate",
                "evidence": {"description": "manual"},
                "resolution": {
                    "corrective_action": "none",
                    "adapted_approach": "none",
                    "verification_check": "none",
                    "resolved_at": "2026-09-18T10:00:00Z",
                    "resolved_by": "tester"
                },
                "reusable": True,
                "timestamp": "2026-09-18T10:00:00Z",
                "related_artifacts": []
            }) + "\n")

        # New registry instance reading file with duplicate must fail closed
        fresh_registry = AcademicPitfallRegistry(self.pitfalls_path)
        with self.assertRaises(DuplicatePitfallError):
            fresh_registry.read(validate_schema=False)

    def test_05_resolution_lifecycle_tracking(self):
        """Validates that an existing pitfall can be resolved and updated with resolution audit trail."""
        self.registry.create(
            candidate_approach="Normality Check via Kolmogorov-Smirnov on N=400",
            problem="Excessive power makes test over-sensitive to trivial non-normality.",
            evidence="p = .012 with skewness = 0.15",
            corrective_action="Pending",
            adapted_approach="Pending",
            pitfall_id="PIT-RES-01"
        )

        updated = self.registry.resolve_pitfall(
            pitfall_id="PIT-RES-01",
            corrective_action="Rely on Kline (2023) skewness < 2.0 and kurtosis < 7.0 visual Q-Q plots.",
            adapted_approach="Kline skew/kurtosis thresholds with Q-Q plot diagnostic inspection",
            resolved_by="statistical-expert",
            verification_check="Calculate absolute skewness and kurtosis; verify both within boundaries."
        )

        self.assertEqual(updated["resolution"]["resolved_by"], "statistical-expert")
        self.assertIn("Kline", updated["resolution"]["corrective_action"])

        # Re-read from disk to ensure persistence
        stored = self.registry.get("PIT-RES-01")
        self.assertEqual(stored["resolution"]["resolved_by"], "statistical-expert")

        # Resolving non-existent pitfall fails closed
        with self.assertRaises(PitfallNotFoundError):
            self.registry.resolve_pitfall(
                pitfall_id="PIT-NON-EXISTENT",
                corrective_action="foo",
                adapted_approach="bar",
                resolved_by="baz"
            )

    def test_06_reuse_surfaced_to_new_workflow(self):
        """
        Acceptance Criteria Test:
        A rejected analytical approach from Project 1 is persisted into the registry.
        When Project 2 (a new workflow) proposes the same candidate, the registry flags
        it as previously invalidated and surfaces the past pitfall and corrective action.
        """
        # 1. Project 1 records an invalidated approach
        self.registry.create(
            candidate_approach="Pairwise Repeated Measures Post-Hoc without Baseline Adjustment",
            problem="Omission of pre-test covariate in clinical intervention trial inflates bias.",
            evidence="Pre-test scores accounted for 42% of post-test variance.",
            corrective_action="Mandate ANCOVA with baseline covariate adjustment.",
            adapted_approach="Baseline-Adjusted ANCOVA",
            detected_by="academic-challenger",
            category="methodological",
            project="clinical_trial_study_1",
            milestone="M_INTERVENTION_EVAL",
            reusable=True,
            pitfall_id="PIT-REUSE-001"
        )

        # 2. Project 2 initializes fresh registry pointing to the shared pitfalls file
        proj2_registry = AcademicPitfallRegistry(self.pitfalls_path, project_id="clinical_trial_study_2")

        # Candidate proposed in Project 2
        proposed_candidate = {
            "method": "Pairwise Repeated Measures Post-Hoc without Baseline Adjustment",
            "research_question": "Does mindfulness reduce social anxiety?"
        }

        # Check if invalidated
        is_invalid, matching_pitfalls = proj2_registry.is_approach_invalidated(proposed_candidate)
        self.assertTrue(is_invalid)
        self.assertEqual(len(matching_pitfalls), 1)
        self.assertEqual(matching_pitfalls[0]["pitfall_id"], "PIT-REUSE-001")
        self.assertIn("ANCOVA", matching_pitfalls[0]["resolution"]["corrective_action"])

        # Check surfacing reusable pitfalls for a milestone
        reusable_list = proj2_registry.surface_reusable_pitfalls(milestone="M_INTERVENTION_EVAL")
        self.assertEqual(len(reusable_list), 1)
        self.assertEqual(reusable_list[0]["pitfall_id"], "PIT-REUSE-001")

    def test_07_invalid_record_fails_closed(self):
        """Validates that schema violations fail closed with PitfallSchemaValidationError."""
        # Invalid category
        with self.assertRaises(PitfallSchemaValidationError):
            self.registry.create(
                candidate_approach="Some Approach",
                problem="Some Problem",
                evidence="Evidence",
                corrective_action="Action",
                adapted_approach="Adapted",
                category="not_a_real_category"
            )

        # Missing required problem string
        with self.assertRaises(PitfallSchemaValidationError):
            self.registry.create(
                candidate_approach="Some Approach",
                problem="",  # empty
                evidence="Evidence",
                corrective_action="Action",
                adapted_approach="Adapted"
            )

    def test_08_malformed_jsonl_fails_closed(self):
        """Validates that corrupted lines in pitfalls.jsonl fail closed with MalformedPitfallError."""
        with open(self.pitfalls_path, "w", encoding="utf-8") as f:
            f.write("CORRUPTED NOT JSON LINE\n")

        with self.assertRaises(MalformedPitfallError):
            self.registry.read(validate_schema=False)

        # Non-object JSON
        with open(self.pitfalls_path, "w", encoding="utf-8") as f:
            f.write('"just a string"\n')

        with self.assertRaises(MalformedPitfallError):
            self.registry.read(validate_schema=False)

        # Object missing pitfall_id
        with open(self.pitfalls_path, "w", encoding="utf-8") as f:
            f.write(json.dumps({"candidate_approach": "test", "problem": "test"}) + "\n")

        with self.assertRaises(MalformedPitfallError):
            self.registry.read(validate_schema=False)

    def test_09_five_defect_categories_coverage(self):
        """Verifies coverage across all 5 defect categories: methodological, statistical, execution, evidence, validation."""
        self.assertEqual(len(VALID_CATEGORIES), 5)
        for cat in sorted(list(VALID_CATEGORIES)):
            rec = self.registry.create(
                candidate_approach=f"Candidate for {cat}",
                problem=f"Problem in category {cat}",
                evidence=f"Evidence for {cat}",
                corrective_action=f"Corrective action for {cat}",
                adapted_approach=f"Adapted approach for {cat}",
                category=cat,
                pitfall_id=f"PIT-CAT-{cat.upper()}"
            )
            self.assertEqual(rec["category"], cat)

        all_records = self.registry.read(validate_schema=True)
        self.assertEqual(len(all_records), 5)
        categories_found = {r["category"] for r in all_records}
        self.assertEqual(categories_found, VALID_CATEGORIES)

    def test_10_academic_challenger_integration(self):
        """Validates that AcademicChallenger writes findings into the pitfall registry and rejects invalid candidates."""
        challenger = AcademicChallenger(pitfall_file=self.pitfalls_path)

        # Study context with 14% missing data and randomized pre-post design
        study_context = {
            "design": "pre_post_control",
            "sample_size": 120,
            "missing_percentage": 14.0,
            "repeated_measures": True,
            "baseline_collected": True
        }

        candidate_flawed = {
            "candidate_id": "CAND-POST-ANOVA-TEST",
            "method": "Post-test Only One-Way ANOVA",
            "research_question": "Does the intervention reduce depressive symptoms?",
            "estimand": "Difference in post-test means between groups",
            "assumptions": ["Normality", "Homogeneity of variance"],
            "data_requirements": "Post-test depression inventory scores only",
            "diagnostics": ["Shapiro-Wilk", "Levene test"],
            "strengths": "Simple and computationally trivial",
            "limitations": "Completely ignores pre-test baseline values",
            "expected_interpretation": "Group mean difference",
            "execution_requirements": "R aov or python scipy.stats.f_oneway"
        }

        finding = challenger.challenge_candidate(candidate_flawed, study_context)
        self.assertEqual(finding["verdict"], "REJECTED")

        # Verify that finding was written to pitfalls.jsonl
        stored_pitfalls = self.registry.read(validate_schema=True)
        self.assertGreaterEqual(len(stored_pitfalls), 1)
        flawed_matches = [p for p in stored_pitfalls if "Post-test Only One-Way ANOVA" in p["candidate_approach"]]
        self.assertTrue(len(flawed_matches) >= 1)

    def test_11_state_machine_integration(self):
        """Validates that StrictStateMachine delegates pitfall recording, querying, and checking seamlessly."""
        sm = StrictStateMachine(state_dir=self.state_dir, project_id="proj_integration")

        rec = sm.record_pitfall(
            candidate_approach="Bypassing Mediation Bootstrap",
            problem="Sobel test used instead of 5000 bootstrap resamples on skewed distribution.",
            evidence="Indirect effect distribution skewness = 1.88, kurtosis = 4.10",
            corrective_action="Mandate 5000 bias-corrected accelerated (BCa) bootstrap resamples.",
            adapted_approach="Bootstrap Mediation (PROCESS Model 4)",
            category="statistical",
            milestone_id="M_MEDIATION",
            reusable=True
        )

        self.assertIsNotNone(rec.get("pitfall_id"))
        self.assertEqual(rec["category"], "statistical")

        # Query via state machine
        results = sm.query_pitfalls(category="statistical")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["pitfall_id"], rec["pitfall_id"])

        # Check approach invalidated via state machine
        is_inv, matches = sm.is_approach_invalidated("Bypassing Mediation Bootstrap")
        self.assertTrue(is_inv)
        self.assertEqual(len(matches), 1)

        # Surface reusable pitfalls
        reusable = sm.surface_reusable_pitfalls(milestone="M_MEDIATION")
        self.assertEqual(len(reusable), 1)

        # Resolve pitfall via state machine
        res = sm.resolve_pitfall(
            pitfall_id=rec["pitfall_id"],
            corrective_action="Bootstrap implemented with 5000 resamples.",
            adapted_approach="Bootstrap mediation verified.",
            resolved_by="statistical-auditor"
        )
        self.assertEqual(res["resolution"]["resolved_by"], "statistical-auditor")


if __name__ == "__main__":
    unittest.main()
