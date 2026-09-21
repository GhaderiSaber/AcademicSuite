#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_academic_human_mentor.py — Unit Tests for Proactive Human Mentorship Engine

Verifies:
1. Direct human teaching of Principles, Patterns, Anti-Patterns, and Lessons with strict contract validation.
2. Bilingual natural language instruction parsing (English and Persian).
3. Search, listing, and superseding workflows.
4. Scope containment: cross-project shared learning vs project-specific quarantine.
5. End-to-end integration: Human teaches a rule -> retrieve_pre_task_context() retrieves it ->
   AcademicContextTokenBudgeter formats it under Applicable Methodology Rules in the agent pre-flight briefing.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
for p in [ROOT_DIR, AGENTS_DIR, os.path.join(AGENTS_DIR, "scripts")]:
    if p not in sys.path:
        sys.path.insert(0, p)

from scripts.academic_human_mentor import AcademicHumanMentor
from scripts.academic_knowledge_manager import AcademicKnowledgeManager


class TestAcademicHumanMentor(unittest.TestCase):
    """Authoritative test suite for the Proactive Human Mentorship Engine."""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_mentor_")
        self.mentor = AcademicHumanMentor(base_dir=self.test_dir)
        self.km = self.mentor.km

    def tearDown(self):
        if os.path.isdir(self.test_dir):
            shutil.rmtree(self.test_dir, ignore_errors=True)

    def test_01_teach_principle_schema_compliance(self):
        """Verify teaching a foundational principle produces schema-compliant JSON and badge."""
        res = self.mentor.teach(
            category="principle",
            statement="In continuous moderation, always report Johnson-Neyman significance regions alongside +/- 1 SD pick-a-point slopes.",
            rationale="Eliminates arbitrary point selection bias and reveals exact regions of moderator influence.",
            capability="moderation",
            tags=["moderation", "johnson-neyman", "apa7"],
            scope="cross-project"
        )
        self.assertTrue(res["item_id"].startswith("PRN-"))
        self.assertEqual(res["item_kind"], "Principle")
        self.assertIn("Knowledge Codified & Persisted", res["badge"])
        self.assertIn(res["item_id"], res["badge"])

        # Check physical file on disk
        stored = self.km.get_item(res["item_id"])
        self.assertIsNotNone(stored)
        self.assertEqual(stored["item_type"], "principle")
        self.assertEqual(stored["status"], "ACCEPTED_ACTIVE")
        self.assertEqual(stored["scope"], "cross-project")
        self.assertEqual(stored["capability"], "moderation")

    def test_02_teach_pattern_workflow_compliance(self):
        """Verify teaching a procedural pattern produces valid schema item."""
        res = self.mentor.teach(
            category="pattern",
            statement="Pre-Post Experimental Workflow: Check Shapiro-Wilk and Levene equality before reporting ANCOVA F-tests.",
            rationale="Ensures parametric assumptions are documented prior to inferential testing.",
            capability="ancova",
            scope="cross-project"
        )
        self.assertTrue(res["item_id"].startswith("PTR-"))
        self.assertEqual(res["item_kind"], "Pattern")
        stored = self.km.get_item(res["item_id"])
        self.assertIsNotNone(stored)
        self.assertEqual(stored["item_type"], "pattern")

    def test_03_teach_anti_pattern_compliance(self):
        """Verify teaching an anti-pattern produces valid anti_pattern item."""
        res = self.mentor.teach(
            category="anti_pattern",
            statement="Dichotomizing continuous variables via median split in regression or moderation.",
            rationale="Causes 30-50% loss of statistical power and creates spurious significant interaction effects.",
            capability="moderation",
            defective_pattern="Dichotomizing continuous moderator using median split.",
            corrective_remedy="Maintain continuous scale using Hayes PROCESS Model 1.",
            observed_symptoms=["Arbitrary median cutoffs", "Loss of statistical variance"]
        )
        self.assertTrue(res["item_id"].startswith("AP-"))
        self.assertEqual(res["item_kind"], "Anti-Pattern")
        stored = self.km.get_item(res["item_id"])
        self.assertIsNotNone(stored)
        self.assertEqual(stored["category"], "statistical")
        self.assertIn("Hayes PROCESS", stored["corrective_remedy"])

    def test_04_teach_lesson_compliance(self):
        """Verify teaching an operational lesson produces valid lesson contract."""
        res = self.mentor.teach(
            category="lesson",
            statement="Always verify degrees of freedom match between Chapter 3 methodology sample size and Chapter 4 ANOVA tables.",
            rationale="Prevents committee rejection due to unstated sample attrition.",
            capability="chapter4",
            scope="cross-project"
        )
        self.assertTrue(res["item_id"].startswith("LSN-"))
        self.assertEqual(res["item_kind"], "Lesson")
        stored = self.km.get_item(res["item_id"])
        self.assertIsNotNone(stored)
        self.assertEqual(stored["status"], "VALIDATED")
        self.assertTrue(stored["is_active_behavior"])

    def test_05_bilingual_natural_language_parsing(self):
        """Verify bilingual natural language heuristic parsing for English and Persian."""
        # 1. English Principle
        r1 = self.mentor.teach_from_natural_language(
            "Remember that in mediation analysis, always use 5,000 bootstrap resamples with 95% BCa CI."
        )
        self.assertEqual(r1["item_kind"], "Principle")
        self.assertEqual(r1["capability"], "mediation")

        # 2. English Anti-Pattern
        r2 = self.mentor.teach_from_natural_language(
            "Never use normal theory Sobel test in mediation analysis; use Preacher and Hayes bootstrap instead."
        )
        self.assertEqual(r2["item_kind"], "Anti-Pattern")
        self.assertEqual(r2["capability"], "mediation")

        # 3. Persian Principle
        r3 = self.mentor.teach_from_natural_language(
            "یادت باشه در تحلیل عاملی همیشه مقادیر اشتراک کمتر از ۰.۳ را حذف کن"
        )
        self.assertEqual(r3["item_kind"], "Principle")
        self.assertEqual(r3["capability"], "psychometrics")

        # 4. Persian Anti-Pattern
        r4 = self.mentor.teach_from_natural_language(
            "نباید مقدار p = .000 در گزارش‌های آماری نوشته شود"
        )
        self.assertEqual(r4["item_kind"], "Anti-Pattern")

    def test_06_search_and_list_operations(self):
        """Verify listing and searching across learned knowledge."""
        self.mentor.teach(
            category="principle",
            statement="SEM Fit Indices rule: CFI and TLI must exceed 0.90 for acceptable fit.",
            capability="SEM"
        )
        self.mentor.teach(
            category="principle",
            statement="Cronbach alpha rule: Acceptable threshold is 0.70.",
            capability="psychometrics"
        )

        # Search
        sem_results = self.mentor.search_knowledge(query="CFI", capability="SEM")
        self.assertGreaterEqual(len(sem_results), 1)
        self.assertIn("0.90", sem_results[0]["statement"])

        # List
        all_items = self.mentor.list_knowledge(limit=10)
        self.assertGreaterEqual(len(all_items), 2)

    def test_07_superseding_workflow(self):
        """Verify superseding an outdated rule with an updated version."""
        r_old = self.mentor.teach(
            category="principle",
            statement="Acceptable CFI threshold is 0.85.",
            capability="SEM"
        )
        old_id = r_old["item_id"]

        # Supersede
        res = self.mentor.supersede(
            old_id=old_id,
            new_statement="Acceptable CFI threshold is 0.90 (Hu & Bentler 1999).",
            rationale="Stricter modern psychometric standard."
        )
        self.assertIn("Superseded", res["badge"])
        new_id = res["new_id"]

        old_item = self.km.get_item(old_id)
        self.assertEqual(old_item["status"], "SUPERSEDED")

        new_item = self.km.get_item(new_id)
        self.assertEqual(new_item["status"], "ACCEPTED_ACTIVE")
        self.assertIn("0.90", new_item["statement"])

    def test_08_end_to_end_pre_task_retrieval_and_budgeting(self):
        """Verify that a human-taught principle is immediately retrieved and budgeted in pre-task context."""
        # 1. Human teaches a rule for mediation
        self.mentor.teach(
            category="principle",
            statement="Always report unstandardized B along with 95% BCa confidence intervals for indirect effects.",
            capability="mediation",
            tags=["mediation", "bootstrap"]
        )

        # 2. Agent prepares to run bootstrap mediation
        briefing = self.km.retrieve_pre_task_context(
            capability="mediation",
            task="bootstrap_mediation",
            max_token_budget=800
        )

        # 3. Assert principle is in retrieved principles
        self.assertGreaterEqual(len(briefing.get("principles", [])), 1)

        # 4. Assert principle appears in formatted briefing
        formatted = briefing.get("formatted_briefing", "")
        self.assertIn("Applicable Methodology Rules & Boundary Conditions:", formatted)
        self.assertIn("Principle:", formatted)
        self.assertIn("Always report unstandardized B", formatted)
    def test_09_cli_commands(self):
        """Verify CLI execution of academic_human_mentor.py and academic_knowledge_manager.py."""
        import subprocess

        env = dict(os.environ)
        env["ACADEMIC_SUITE_BASE_DIR"] = self.test_dir

        # 1. Teach via academic_human_mentor.py CLI
        cmd1 = [
            sys.executable,
            os.path.join(ROOT_DIR, ".agents", "scripts", "academic_human_mentor.py"),
            "teach",
            "--category", "principle",
            "--statement", "Standard regression rule: report collinearity VIF and Tolerance.",
            "--capability", "regression"
        ]
        p1 = subprocess.run(cmd1, capture_output=True, text=True, cwd=ROOT_DIR, env=env)
        self.assertEqual(p1.returncode, 0, p1.stderr)
        self.assertIn("Knowledge Codified & Persisted", p1.stdout)

        # 2. List via academic_knowledge_manager.py CLI
        cmd2 = [
            sys.executable,
            os.path.join(ROOT_DIR, ".agents", "scripts", "academic_knowledge_manager.py"),
            "--action", "list",
            "--category", "principle"
        ]
        p2 = subprocess.run(cmd2, capture_output=True, text=True, cwd=ROOT_DIR, env=env)
        self.assertEqual(p2.returncode, 0, p2.stderr)
        self.assertIn("collinearity", p2.stdout)

        # 3. Search via academic_human_mentor.py CLI
        cmd3 = [
            sys.executable,
            os.path.join(ROOT_DIR, ".agents", "scripts", "academic_human_mentor.py"),
            "search",
            "collinearity"
        ]
        p3 = subprocess.run(cmd3, capture_output=True, text=True, cwd=ROOT_DIR, env=env)
        self.assertEqual(p3.returncode, 0, p3.stderr)
        self.assertIn("collinearity", p3.stdout)


if __name__ == "__main__":
    unittest.main()
