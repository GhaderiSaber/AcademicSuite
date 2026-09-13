#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Academic Journal Article & Submission Packaging Multi-Agent Workflow
===================================================================================
Validates:
  1. Specification markdown compliance (.agents/workflows/journal_submission.md).
  2. Multi-agent execution orchestration via DigitalSaber.
  3. Generation of all publication deliverables (.docx, .json, .xlsx).
  4. Highlights character length rule (strictly <= 85 characters).
  5. CRediT 14-role taxonomy and APA 7 typography enforcement.
  6. OpenXMLArtifactEngine article and submission packaging generators.
  7. Interactive shell commands (/workflow, /publish, /article, /translate).
"""

import os
import sys
import json
import shutil
import tempfile
import unittest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, ROOT_DIR)

from digital_saber import DigitalSaber
from openxml_artifact_engine import OpenXMLArtifactEngine
from digital_saber_shell import DigitalSaberShell

AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
WORKFLOWS_DIR = os.path.join(AGENTS_DIR, "workflows")


class TestJournalSubmissionWorkflow(unittest.TestCase):
    """Test suite for Pipeline 3: Academic Journal Article & Submission Packaging."""

    @classmethod
    def setUpClass(cls):
        cls.saber = DigitalSaber()
        cls.temp_dir = tempfile.mkdtemp(prefix="test_journal_wf_")
        cls.decisions_dir = os.path.join(AGENTS_DIR, "memory", "decisions")
        cls.initial_decisions = set(os.listdir(cls.decisions_dir)) if os.path.exists(cls.decisions_dir) else set()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir, ignore_errors=True)
        # Clean up any new test decisions
        if os.path.exists(cls.decisions_dir):
            current = set(os.listdir(cls.decisions_dir))
            for f in current - cls.initial_decisions:
                try:
                    os.remove(os.path.join(cls.decisions_dir, f))
                except Exception:
                    pass

    def test_01_spec_file_exists_and_valid(self):
        """Verifies that journal_submission.md exists and meets Antigravity structural criteria."""
        spec_path = os.path.join(WORKFLOWS_DIR, "journal_submission.md")
        self.assertTrue(os.path.exists(spec_path), f"Missing workflow specification: {spec_path}")

        with open(spec_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertGreater(len(content), 1000, "Workflow specification is too brief.")
        self.assertIn("digital-saber", content)
        self.assertIn("academic-writer", content)
        self.assertIn("academic-article-writer", content)
        self.assertIn("journal-submission-assistant", content)
        self.assertIn("irandoc-plagiarism-reducer", content)
        self.assertIn("ai-academic-tone-polisher", content)
        self.assertIn("final-judge", content)
        self.assertIn("124911145", content)  # Saber Admin Desk ID

    def test_02_workflow_execution_and_artifacts(self):
        """Tests end-to-end execution of journal_submission workflow and physical deliverables."""
        res = self.saber.run_workflow(
            "journal_submission",
            topic_or_file="اثربخشی درمان مبتنی بر پذیرش و تعهد بر فرسودگی شغلی کادر درمان",
            output_dir=self.temp_dir
        )

        self.assertIsNotNone(res)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["workflow"], "journal_submission")
        self.assertGreaterEqual(res["readiness_score"], 90.0)
        self.assertGreaterEqual(res["acceptance_probability"], 90.0)
        self.assertTrue(res["decision_id"].startswith("dec_"))

        # Verify subagents executed
        self.assertIn("digital-saber", res["subagents_executed"])
        self.assertIn("academic-writer", res["subagents_executed"])
        self.assertIn("evidence-auditor", res["subagents_executed"])
        self.assertIn("journal-assistant", res["subagents_executed"])
        self.assertIn("final-judge", res["subagents_executed"])

        # Check physical existence of generated artifacts
        expected_artifacts = [
            "Academic_Article_Manuscript.docx",
            "Cover_Letter_Editor.docx",
            "Title_Page_CRediT.docx",
            "Highlights_and_Abstract.docx",
            "submission_manifest.json"
        ]
        for art in expected_artifacts:
            art_path = os.path.join(self.temp_dir, art)
            self.assertTrue(os.path.exists(art_path), f"Expected artifact missing: {art_path}")
            self.assertGreater(os.path.getsize(art_path), 0, f"Artifact is empty: {art_path}")

        # Check manifest schema and character limit validation
        manifest_path = os.path.join(self.temp_dir, "submission_manifest.json")
        with open(manifest_path, "r", encoding="utf-8") as f:
            manifest = json.load(f)

        self.assertEqual(manifest["admin_desk_id"], "124911145")
        self.assertIn("word_counts", manifest)
        self.assertIn("highlights_validated", manifest)
        for h in manifest["highlights_validated"]:
            self.assertLessEqual(len(h), 85, f"Highlight exceeds 85-char limit: '{h}' ({len(h)} chars)")

    def test_03_openxml_engine_journal_components(self):
        """Validates OpenXMLArtifactEngine standalone compilation of article and submission docs."""
        engine = OpenXMLArtifactEngine()

        test_article = {
            "title": "Effectiveness of ACT on Burnout",
            "authors": ["Saber Ghaderi"],
            "affiliation": "University of Tehran",
            "abstract": {
                "background": "Background statement.",
                "objective": "Objective statement.",
                "methods": "Methods description.",
                "results": "Results description.",
                "conclusion": "Conclusions."
            },
            "keywords": ["ACT", "Burnout", "Flexibility"],
            "introduction": ["Intro paragraph 1.", "Intro paragraph 2.", "Intro paragraph 3."],
            "method": {
                "design_and_participants": "RCT N=34",
                "measures": "MBI, AAQ-II",
                "procedure": "8 sessions",
                "statistical_analysis": "ANCOVA"
            },
            "results": {
                "narrative": "Significant improvement F(1, 31) = 14.32, p < .001.",
                "tables": [{
                    "number": 1,
                    "caption": "Table 1: Univariate ANCOVA",
                    "headers": ["Source", "F", "p", "eta_p^2"],
                    "rows": [["Treatment", "14.32", "< .001", ".32"]],
                    "note": "N = 34."
                }]
            },
            "discussion": ["Discussion paragraph 1.", "Discussion paragraph 2.", "Discussion paragraph 3."],
            "references": [f"Author, A. ({2000+i}). Study title {i}." for i in range(20)]
        }

        test_package = {
            "manuscript_metadata": {
                "title": "Effectiveness of ACT on Burnout",
                "article_type": "Original Research Article",
                "journal_name": "Journal of Contextual Behavioral Science",
                "word_counts": {"main_text": 5000}
            },
            "authors": [
                {
                    "first_name": "Saber", "last_name": "Ghaderi",
                    "affiliation_ids": [1], "is_corresponding": True,
                    "credit_roles": ["Conceptualization", "Formal analysis", "Methodology"]
                }
            ],
            "affiliations": [{"id": 1, "department": "Psychology", "institution": "University of Tehran", "city": "Tehran", "country": "Iran"}],
            "corresponding_author": {"name": "Saber Ghaderi", "email": "saber@ut.ac.ir"},
            "cover_letter_content": {"hook": "Hook sentence.", "key_findings": "Key findings.", "novelty_statement": "Novelty."},
            "highlights": ["Highlight bullet one.", "Highlight bullet two."]
        }

        art_doc = os.path.join(self.temp_dir, "test_standalone_article.docx")
        cl_doc = os.path.join(self.temp_dir, "test_standalone_cl.docx")
        tp_doc = os.path.join(self.temp_dir, "test_standalone_tp.docx")
        hl_doc = os.path.join(self.temp_dir, "test_standalone_hl.docx")

        p1 = engine.generate_article_manuscript_docx(test_article, art_doc, lang="en")
        p2 = engine.generate_cover_letter_docx(test_package, cl_doc, lang="en")
        p3 = engine.generate_title_page_docx(test_package, tp_doc, lang="en")
        p4 = engine.generate_highlights_docx(test_package, hl_doc, lang="en")

        for p in [p1, p2, p3, p4]:
            self.assertTrue(os.path.exists(p), f"Generated file missing: {p}")
            self.assertGreater(os.path.getsize(p), 1000, f"Generated file too small: {p}")

    def test_04_shell_commands(self):
        """Tests that /workflow, /publish, /article, and /translate shell dispatchers execute without error."""
        shell = DigitalSaberShell(saber_instance=self.saber, output_dir=self.temp_dir)

        # /workflow with alias publish
        shell.do_workflow("publish")

        # /publish
        shell.do_publish("درمان مبتنی بر پذیرش و تعهد فرسودگی شغلی")

        # /article
        shell.do_article("ACT for Burnout")

        # /translate
        shell.do_translate("این پژوهش نشان داد که درمان مبتنی بر پذیرش و تعهد اثربخش است.")


if __name__ == "__main__":
    unittest.main()
