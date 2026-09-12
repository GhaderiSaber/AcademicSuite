#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Antigravity-Native Multi-Agent Dissertation Workflows
Validates the complete 4-workflow graduate dissertation lifecycle:
  1. chapter4.md (Statistical Data Analysis & Findings)
  2. proposal.md (Academic Research Proposal Formulation)
  3. chapter5.md (Discussion, Theoretical Integration & Conclusion)
  4. thesis_revision.md (Supervisor & Examiner Feedback Resolution)
"""

import os
import sys
import unittest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, ROOT_DIR)

from digital_saber import DigitalSaber

AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
WORKFLOWS_DIR = os.path.join(AGENTS_DIR, "workflows")


class TestWorkflowsSuite(unittest.TestCase):
    """Test suite for Antigravity multi-agent workflows."""

    @classmethod
    def setUpClass(cls):
        cls.decisions_dir = os.path.join(AGENTS_DIR, "memory", "decisions")
        cls.initial_decisions = set(os.listdir(cls.decisions_dir)) if os.path.exists(cls.decisions_dir) else set()

    @classmethod
    def tearDownClass(cls):
        # Clean up any new test decisions created during test run
        if os.path.exists(cls.decisions_dir):
            current_decisions = set(os.listdir(cls.decisions_dir))
            for f in current_decisions - cls.initial_decisions:
                try:
                    os.remove(os.path.join(cls.decisions_dir, f))
                except Exception:
                    pass

    def setUp(self):
        self.saber = DigitalSaber()
        self.expected_workflows = [
            "chapter2_literature",
            "chapter4",
            "proposal",
            "chapter5",
            "thesis_revision",
            "journal_submission",
            "defense_presentation",
            "thesis_assembly",
            "intervention_protocol",
            "scale_validation"
        ]

    def test_workflow_spec_files_exist(self):
        """Validates that all 10 core workflow markdown files exist."""
        for wf in self.expected_workflows:
            wf_file = os.path.join(WORKFLOWS_DIR, f"{wf}.md")
            self.assertTrue(os.path.exists(wf_file), f"Missing workflow specification: {wf_file}")
            with open(wf_file, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertGreater(len(content), 500, f"Workflow spec {wf} is too short.")
            self.assertIn("digital-saber", content)
            self.assertIn("academic-writer", content)
            self.assertIn("final-judge", content)
            self.assertIn("124911145", content)  # Saber Human Gate Admin Desk ID

    def test_chapter2_literature_workflow_execution(self):
        """Tests end-to-end execution of Chapter 2 literature and science mapping workflow."""
        res = self.saber.run_workflow("chapter2_literature")
        self.assertIsNotNone(res)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["workflow"], "chapter2_literature")
        self.assertIn("digital-saber", res["subagents_executed"])
        self.assertIn("literature-expert", res["subagents_executed"])
        self.assertIn("academic-writer", res["subagents_executed"])
        self.assertIn("final-judge", res["subagents_executed"])
        self.assertTrue(any("فصل_دوم_پیشینه_پژوهش.docx" in a for a in res["artifacts_generated"]))
        self.assertGreaterEqual(res["readiness_score"], 80.0)
        self.assertTrue(res["decision_id"].startswith("dec_"))

    def test_chapter4_workflow_execution(self):
        """Tests end-to-end execution of Chapter 4 statistical workflow."""
        res = self.saber.run_workflow("chapter4")
        self.assertIsNotNone(res)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["workflow"], "chapter4")
        self.assertIn("digital-saber", res["subagents_executed"])
        self.assertIn("statistical-expert", res["subagents_executed"])
        self.assertIn("statistical-auditor", res["subagents_executed"])
        self.assertIn("academic-writer", res["subagents_executed"])
        self.assertGreaterEqual(res["readiness_score"], 80.0)
        self.assertTrue(res["decision_id"].startswith("dec_"))

    def test_proposal_workflow_execution(self):
        """Tests end-to-end execution of Research Proposal workflow."""
        res = self.saber.run_workflow("proposal")
        self.assertIsNotNone(res)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["workflow"], "proposal")
        self.assertIn("methodology-expert", res["subagents_executed"])
        self.assertIn("literature-expert", res["subagents_executed"])
        self.assertIn("academic-writer", res["subagents_executed"])
        self.assertTrue(any("پروپوزال_طرح_پژوهش.docx" in a for a in res["artifacts_generated"]))
        self.assertGreaterEqual(res["readiness_score"], 80.0)
        self.assertTrue(res["decision_id"].startswith("dec_"))

    def test_chapter5_workflow_execution(self):
        """Tests end-to-end execution of Chapter 5 discussion workflow."""
        res = self.saber.run_workflow("chapter5")
        self.assertIsNotNone(res)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["workflow"], "chapter5")
        self.assertIn("statistical-expert", res["subagents_executed"])
        self.assertIn("literature-expert", res["subagents_executed"])
        self.assertIn("academic-writer", res["subagents_executed"])
        self.assertIn("final-judge", res["subagents_executed"])
        self.assertTrue(any("فصل_پنجم_بحث_و_نتیجه‌گیری.docx" in a for a in res["artifacts_generated"]))
        self.assertGreaterEqual(res["readiness_score"], 80.0)
        self.assertTrue(res["decision_id"].startswith("dec_"))

    def test_thesis_revision_workflow_execution(self):
        """Tests end-to-end execution of Thesis Revision & Rebuttal Table workflow."""
        res = self.saber.run_workflow("thesis_revision")
        self.assertIsNotNone(res)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["workflow"], "thesis_revision")
        self.assertIn("results-auditor", res["subagents_executed"])
        self.assertIn("statistical-auditor", res["subagents_executed"])
        self.assertIn("academic-writer", res["subagents_executed"])
        self.assertIn("final-judge", res["subagents_executed"])
        self.assertTrue(any("جدول_پاسخ_به_نظرات_استاد_راهنما_و_داوران.docx" in a for a in res["artifacts_generated"]))
        self.assertGreaterEqual(res["readiness_score"], 80.0)
        self.assertTrue(res["decision_id"].startswith("dec_"))

    def test_journal_submission_workflow_execution(self):
        """Tests end-to-end execution of Academic Journal Article & Submission Packaging workflow."""
        res = self.saber.run_workflow("journal_submission")
        self.assertIsNotNone(res)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["workflow"], "journal_submission")
        self.assertIn("digital-saber", res["subagents_executed"])
        self.assertIn("academic-writer", res["subagents_executed"])
        self.assertIn("evidence-auditor", res["subagents_executed"])
        self.assertIn("journal-assistant", res["subagents_executed"])
        self.assertIn("final-judge", res["subagents_executed"])
        self.assertTrue(any("Cover_Letter_Editor.docx" in a for a in res["artifacts_generated"]))
        self.assertTrue(any("Title_Page_CRediT.docx" in a for a in res["artifacts_generated"]))
        self.assertTrue(any("Highlights_and_Abstract.docx" in a for a in res["artifacts_generated"]))
        self.assertTrue(any("submission_manifest.json" in a for a in res["artifacts_generated"]))
        self.assertGreaterEqual(res["readiness_score"], 90.0)
        self.assertGreaterEqual(res["acceptance_probability"], 90.0)
        self.assertTrue(res["decision_id"].startswith("dec_"))

    def test_defense_presentation_workflow_execution(self):
        """Tests end-to-end execution of Viva Voce Oral Defense Presentation workflow."""
        res = self.saber.run_workflow("defense_presentation")
        self.assertIsNotNone(res)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["workflow"], "defense_presentation")
        self.assertIn("digital-saber", res["subagents_executed"])
        self.assertIn("results-auditor", res["subagents_executed"])
        self.assertIn("academic-writer", res["subagents_executed"])
        self.assertIn("presentation-expert", res["subagents_executed"])
        self.assertIn("final-judge", res["subagents_executed"])
        self.assertTrue(any("defense_presentation.html" in a for a in res["artifacts_generated"]))
        self.assertTrue(any("اسلایدهای_جلسه_دفاع.pptx" in a for a in res["artifacts_generated"]))
        self.assertTrue(any("متن_نطق_ارائه_دفاع.docx" in a for a in res["artifacts_generated"]))
        self.assertTrue(any("defense_committee_qa_card.json" in a for a in res["artifacts_generated"]))
        self.assertGreaterEqual(res["readiness_score"], 90.0)
        self.assertTrue(res["decision_id"].startswith("dec_"))

    def test_thesis_assembly_workflow_execution(self):
        """Tests end-to-end execution of Master Dissertation Assembly workflow."""
        res = self.saber.run_workflow("thesis_assembly")
        self.assertIsNotNone(res)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["workflow"], "thesis_assembly")
        self.assertIn("digital-saber", res["subagents_executed"])
        self.assertIn("results-auditor", res["subagents_executed"])
        self.assertIn("academic-writer", res["subagents_executed"])
        self.assertIn("evidence-auditor", res["subagents_executed"])
        self.assertIn("final-judge", res["subagents_executed"])
        self.assertTrue(any("پایان‌نامه_کامل_تدوین‌شده.docx" in a for a in res["artifacts_generated"]))
        self.assertGreaterEqual(res["compliance_score"], 90.0)
        self.assertTrue(res["decision_id"].startswith("dec_"))

    def test_intervention_protocol_workflow_execution(self):
        """Tests end-to-end execution of Clinical Intervention Protocol builder workflow."""
        res = self.saber.run_workflow("intervention_protocol")
        self.assertIsNotNone(res)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["workflow"], "intervention_protocol")
        self.assertIn("digital-saber", res["subagents_executed"])
        self.assertIn("methodology-expert", res["subagents_executed"])
        self.assertIn("academic-writer", res["subagents_executed"])
        self.assertIn("final-judge", res["subagents_executed"])
        self.assertTrue(any("پروتکل_مداخله_درمانی.docx" in a for a in res["artifacts_generated"]))
        self.assertTrue(any("جدول_خلاصه_جلسات_مداخله.docx" in a for a in res["artifacts_generated"]))
        self.assertTrue(any("consort_flowchart.png" in a for a in res["artifacts_generated"]))
        self.assertTrue(any("protocol_blueprint.json" in a for a in res["artifacts_generated"]))
        self.assertGreaterEqual(res["fidelity_score"], 90.0)
        self.assertTrue(res["decision_id"].startswith("dec_"))

    def test_scale_validation_workflow_execution(self):
        """Tests end-to-end execution of Psychometric Scale Validation workflow."""
        res = self.saber.run_workflow("scale_validation")
        self.assertIsNotNone(res)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["workflow"], "scale_validation")
        self.assertIn("digital-saber", res["subagents_executed"])
        self.assertIn("statistical-expert", res["subagents_executed"])
        self.assertIn("statistical-auditor", res["subagents_executed"])
        self.assertIn("final-judge", res["subagents_executed"])
        self.assertTrue(any("گزارش_اعتباریابی_روانسنجی.docx" in a for a in res["artifacts_generated"]))
        self.assertTrue(any("psychometric_validation_matrix.xlsx" in a for a in res["artifacts_generated"]))
        self.assertTrue(any("cfa_lavaan_model.R" in a for a in res["artifacts_generated"]))
        self.assertTrue(any("psychometric_validation_report.json" in a for a in res["artifacts_generated"]))
        self.assertGreaterEqual(res["psychometric_score"], 90.0)
        self.assertTrue(res["decision_id"].startswith("dec_"))

    def test_unknown_workflow_returns_none(self):
        """Tests that an unregistered workflow name returns None gracefully."""
        res = self.saber.run_workflow("non_existent_workflow")
        self.assertIsNone(res)


if __name__ == "__main__":
    unittest.main()
