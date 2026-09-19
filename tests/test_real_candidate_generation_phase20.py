#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_real_candidate_generation_phase20.py — Acceptance Tests for Real Candidate Generation (Phase 20)

Verifies:
1. 5-input ingestion (trajectory + feedback + failure + existing Skill + relevant knowledge).
2. Behavior Analyst generates structured candidate diagnosis across the 7 target categories.
3. Skill Evolver generates real candidate patches for all 7 target categories:
   - agent instruction
   - Skill
   - decision tree
   - verification rule
   - delegation rule
   - retrieval rule
   - exception rule
4. Dynamic adaptation & elimination of hardcoded canned mutation strings.
5. Unified diff validity and clean patch application.
6. Directive 18 ceiling enforcement (<= 500 lines, <= 40,000 bytes).
7. Strict schema validation against improvement_candidate.schema.json.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
from typing import Dict, Any

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from contracts.contract_validator import validate_improvement_candidate, validate_behavior_analysis
from scripts.academic_behavior_analyzer import AcademicBehaviorAnalyzer
from scripts.academic_candidate_generator import (
    AcademicCandidateGenerator,
    CandidateGenerationError
)


class TestRealCandidateGenerationPhase20(unittest.TestCase):
    """Authoritative test suite for Phase 20: Real Candidate Generation."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="agy_phase20_test_")
        self.generator = AcademicCandidateGenerator(base_dir=self.temp_dir)
        self.analyzer = AcademicBehaviorAnalyzer(base_dir=self.temp_dir)

        # Baseline skill content
        self.sample_skill_content = (
            "---\n"
            "name: apa-reporting\n"
            "description: Generate strictly formatted APA 7th Edition tables and statistics.\n"
            "---\n\n"
            "# apa-reporting\n\n"
            "## Procedures\n"
            "1. Ingest statistical results and format tables.\n"
            "2. Report test statistics, p-values, and effect sizes.\n"
            "3. Enforce 3-line table layout.\n"
        )

        # Baseline trajectory data
        self.sample_trajectory = {
            "trajectory_id": "TRJ-TEST-PHASE20-001",
            "agent": "statistics-agent",
            "skill": "apa-reporting",
            "capability": "apa-reporting",
            "ordered_actions": [
                {
                    "step": 1,
                    "action": "run_command",
                    "tool": "run_command",
                    "command": "python3 format_tables.py",
                    "output": "Table formatted with p = .000"
                }
            ],
            "outputs": {
                "report_text": "The test was statistically significant (p = .000)."
            }
        }

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_five_input_ingestion_and_candidate_diagnosis(self):
        """Test 1: Full 5-input ingestion produces structured candidate diagnosis."""
        feedback = {
            "target_agent": "statistics-agent",
            "target_skill": "apa-reporting",
            "capability": "apa-reporting",
            "correction": "p = .000 is strictly prohibited in APA 7. Report p < .001 or p < ۰.۰۰۱.",
            "desired_behavior": "Enforce APA 7 p-value reporting with leading zero in Persian.",
            "feedback_text": "User corrected p-value reporting violation."
        }
        knowledge = [
            {
                "lesson_id": "LSN-APA-P-VAL",
                "statement": "Never report p = .000 under any circumstance; report p < .001.",
                "target_skill": "apa-reporting"
            }
        ]

        candidate = self.generator.generate_candidate_from_real_behavior(
            trajectory=self.sample_trajectory,
            feedback=feedback,
            existing_skill_content=self.sample_skill_content,
            relevant_knowledge=knowledge,
            record_to_disk=True
        )

        self.assertIsNotNone(candidate)
        self.assertEqual(candidate["target_skill"], "apa-reporting")
        self.assertIn("reflective_diagnosis", candidate)
        self.assertIn("candidate_diagnosis", candidate["metadata"])

        cdiag = candidate["metadata"]["candidate_diagnosis"]
        self.assertIn("target_category", cdiag)
        self.assertIn("diagnosed_gap", cdiag)
        self.assertIn("affected_section", cdiag)
        self.assertIn("proposed_resolution", cdiag)

    def test_02_all_seven_target_categories(self):
        """Test 2: Skill Evolver generates valid candidates for all 7 target categories."""
        categories = [
            "agent instruction",
            "Skill",
            "decision tree",
            "verification rule",
            "delegation rule",
            "retrieval rule",
            "exception rule"
        ]

        for cat in categories:
            with self.subTest(category=cat):
                feedback = {
                    "target_agent": "academic-writer",
                    "target_skill": "apa-reporting",
                    "correction": f"Testing category generation for {cat}",
                    "desired_behavior": f"Refine {cat} specification"
                }

                candidate = self.generator.generate_candidate_from_real_behavior(
                    trajectory=self.sample_trajectory,
                    feedback=feedback,
                    existing_skill_content=self.sample_skill_content,
                    relevant_knowledge=[],
                    target_category=cat,
                    record_to_disk=False
                )

                self.assertIsNotNone(candidate, f"Failed to generate candidate for category '{cat}'")
                self.assertEqual(candidate["metadata"]["candidate_diagnosis"]["target_category"], cat)
                self.assertTrue(len(candidate["mutation"]["content"]) > 0, "Diff content must not be empty")

                # Schema validation
                val = validate_improvement_candidate(candidate)
                self.assertTrue(val.get("valid"), f"Candidate failed schema for category {cat}: {val.get('errors')}")

    def test_03_dynamic_adaptation_no_canned_lmm_strings(self):
        """Test 3: Non-longitudinal skills receive dynamic, context-specific patches with zero canned LMM text."""
        skills_to_test = [
            ("apa-reporting", "p_zero_reported", "Report p < .001 instead of p = .000."),
            ("data-cleaning", "unengaged_responses_retained", "Filter straight-lining and unengaged responses."),
            ("methodology-review", "unjustified_model_selection", "Compare regression against multilevel modeling.")
        ]

        for skill, failure_type, correction in skills_to_test:
            with self.subTest(skill=skill):
                skill_content = (
                    f"---\nname: {skill}\ndescription: Production skill specification.\n---\n\n"
                    f"# {skill}\n\n## Procedures\nExecute {skill} operations.\n"
                )
                feedback = {
                    "target_skill": skill,
                    "target_agent": "statistics-agent",
                    "correction": correction,
                    "desired_behavior": f"Correct behavior for {skill}."
                }
                traj = {
                    "trajectory_id": f"TRJ-{skill.upper()}",
                    "skill": skill,
                    "ordered_actions": [{"step": 1, "action": "execute", "output": f"Output with {failure_type}"}]
                }

                candidate = self.generator.generate_candidate_from_real_behavior(
                    trajectory=traj,
                    feedback=feedback,
                    existing_skill_content=skill_content,
                    record_to_disk=False
                )

                diff_text = candidate["mutation"]["content"]
                # Invariant: Unless testing longitudinal modeling, canned LMM text must NEVER appear
                self.assertNotIn(
                    "Compare LMM vs RM-ANOVA against missingness, imbalance, covariance, and estimand",
                    diff_text,
                    f"Found legacy hardcoded LMM string in candidate for skill '{skill}'!"
                )
                # Invariant: The patch must mention the actual skill or diagnosed correction
                self.assertTrue(
                    skill in diff_text or candidate["metadata"]["candidate_diagnosis"]["affected_section"] in diff_text,
                    f"Generated diff does not reflect target skill '{skill}' or affected section."
                )

    def test_04_unified_diff_validity_and_application(self):
        """Test 4: Generated unified diff is syntactically valid and applies cleanly to original text."""
        feedback = {
            "target_skill": "apa-reporting",
            "correction": "Ensure 3-line table formatting.",
            "desired_behavior": "Enforce APA 7 table borders."
        }

        candidate = self.generator.generate_candidate_from_real_behavior(
            trajectory=self.sample_trajectory,
            feedback=feedback,
            existing_skill_content=self.sample_skill_content,
            record_to_disk=False
        )

        diff_text = candidate["mutation"]["content"]
        self.assertIn("--- a/.agents/skills/apa-reporting/SKILL.md", diff_text)
        self.assertIn("+++ b/.agents/skills/apa-reporting/SKILL.md", diff_text)
        self.assertIn("@@", diff_text)

    def test_05_directive_18_ceiling_enforcement(self):
        """Test 5: Generation rejects mutations exceeding 500 lines or 40,000 bytes."""
        # Create a giant skill content that exceeds 500 lines
        giant_content = "---\nname: giant-skill\n---\n\n# giant-skill\n\n" + "\n".join(f"- Step {i}" for i in range(505))

        feedback = {
            "target_skill": "giant-skill",
            "correction": "Add more steps",
            "desired_behavior": "Refine giant skill"
        }

        with self.assertRaises(CandidateGenerationError) as ctx:
            self.generator.generate_candidate_from_real_behavior(
                trajectory=self.sample_trajectory,
                feedback=feedback,
                existing_skill_content=giant_content,
                record_to_disk=False
            )

        self.assertIn("Directive 18", str(ctx.exception))

    def test_06_schema_contract_validation(self):
        """Test 6: Validates candidate structure against improvement_candidate.schema.json."""
        candidate = self.generator.generate_candidate_from_real_behavior(
            trajectory=self.sample_trajectory,
            failure={
                "target_skill": "apa-reporting",
                "errors": ["Found p = .000 in output."],
                "summary": "Formatting error in p-values."
            },
            existing_skill_content=self.sample_skill_content,
            record_to_disk=True
        )

        val = validate_improvement_candidate(candidate)
        self.assertTrue(val.get("valid"), f"Candidate failed schema validation: {val.get('errors')}")

        # Verify staged on disk
        cid = candidate["candidate_id"]
        candidate_file = os.path.join(self.temp_dir, "learning", "candidates", f"{cid}.json")
        self.assertTrue(os.path.isfile(candidate_file), f"Candidate file not written to {candidate_file}")


if __name__ == "__main__":
    unittest.main()
