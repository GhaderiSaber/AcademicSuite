#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Chapter 2 Literature Review & Science Mapping Multi-Agent Workflow
================================================================================
Validates:
  1. Specification markdown compliance (.agents/workflows/chapter2_literature.md).
  2. Multi-agent execution orchestration via DigitalSaber.
  3. Generation of all 8 primary artifacts (.docx, .png, .ris, .enw, .json, .txt).
  4. OpenXMLArtifactEngine.generate_chapter2_docx functionality.
  5. Interactive shell commands (/workflow, /literature, /biblio).
"""

import os
import sys
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


class TestChapter2LiteratureWorkflow(unittest.TestCase):
    """Test suite for Pipeline 2: Chapter 2 Literature Review & Science Mapping."""

    @classmethod
    def setUpClass(cls):
        cls.saber = DigitalSaber()
        cls.temp_dir = tempfile.mkdtemp(prefix="test_ch2_wf_")
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
        """Verifies that chapter2_literature.md exists and meets Antigravity structural criteria."""
        spec_path = os.path.join(WORKFLOWS_DIR, "chapter2_literature.md")
        self.assertTrue(os.path.exists(spec_path), f"Missing workflow specification: {spec_path}")

        with open(spec_path, "r", encoding="utf-8") as f:
            content = f.read()

        self.assertGreater(len(content), 1000, "Workflow specification is too brief.")
        self.assertIn("digital-saber", content)
        self.assertIn("literature-expert", content)
        self.assertIn("academic-writer", content)
        self.assertIn("final-judge", content)
        self.assertIn("evidence-auditor", content)
        self.assertIn("124911145", content)  # Saber Admin Desk ID

    def test_02_workflow_execution_and_artifacts(self):
        """Tests end-to-end execution of chapter2_literature workflow and artifact creation."""
        res = self.saber.run_workflow(
            "chapter2_literature",
            topic_or_file="اثربخشی درمان مبتنی بر پذیرش و تعهد بر فرسودگی شغلی و انعطاف‌پذیری شناختی",
            output_dir=self.temp_dir
        )

        self.assertIsNotNone(res)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertEqual(res["workflow"], "chapter2_literature")
        self.assertGreaterEqual(res["readiness_score"], 80.0)
        self.assertTrue(res["decision_id"].startswith("dec_"))

        # Verify subagents executed
        self.assertIn("digital-saber", res["subagents_executed"])
        self.assertIn("literature-expert", res["subagents_executed"])
        self.assertIn("academic-writer", res["subagents_executed"])
        self.assertIn("final-judge", res["subagents_executed"])

        # Check physical existence of generated artifacts
        expected_artifacts = [
            "Chapter_2_Literature_Review.docx",
            "literature_synthesis.json",
            "bibliometric_network_map.png",
            "thematic_strategic_map.png",
            "citation_chronomap.png",
            "main_path_trajectory.png",
            "literature_references.ris",
            "literature_references.enw"
        ]
        for art in expected_artifacts:
            art_path = os.path.join(self.temp_dir, art)
            self.assertTrue(os.path.exists(art_path), f"Expected artifact missing: {art_path}")
            self.assertGreater(os.path.getsize(art_path), 0, f"Artifact is empty: {art_path}")

    def test_03_openxml_engine_chapter2(self):
        """Validates OpenXMLArtifactEngine.generate_chapter2_docx standalone compilation."""
        engine = OpenXMLArtifactEngine()
        out_doc = os.path.join(self.temp_dir, "test_standalone_ch2.docx")

        payload = {
            "chapter_title": "فصل دوم: مبانی نظری و پیشینه پژوهش",
            "introduction": "مقدمه تست پیشینه تجربی و مبانی نظری پژوهش.",
            "theoretical_sections": [
                {
                    "section_number": "۲-۲-۱",
                    "variable_name": "انعطاف‌پذیری روان‌شناختی",
                    "variable_name_en": "Psychological Flexibility",
                    "content_paragraphs": ["این متغیر نشان‌دهنده توانایی گسلش از افکار ناکارآمد است."]
                }
            ],
            "theoretical_integration": "پیوند متغیرها در بستر مدل هگزاگفلکس ACT تبیین می‌گردد.",
            "iranian_studies": [
                {
                    "authors": "قادری و همکاران",
                    "year": "۱۴۰۲",
                    "title": "اثربخشی ACT بر فرسودگی",
                    "sample": "۴۰ نفر",
                    "methodology": "نیمه‌آزمایشی",
                    "variables": "ACT، فرسودگی",
                    "key_findings": "کاهش معنادار فرسودگی"
                }
            ],
            "international_studies": [
                {
                    "authors": "Hayes et al.",
                    "year": "2019",
                    "title": "Acceptance and Commitment Therapy",
                    "sample": "N = 120",
                    "methodology": "RCT",
                    "variables": "ACT, Burnout",
                    "key_findings": "Significant symptom reduction"
                }
            ]
        }

        generated_path = engine.generate_chapter2_docx(payload, out_doc)
        self.assertTrue(os.path.exists(generated_path))
        self.assertGreater(os.path.getsize(generated_path), 1000)

    def test_04_shell_commands(self):
        """Tests that /workflow, /literature, and /biblio shell dispatchers work without exception."""
        shell = DigitalSaberShell(saber_instance=self.saber, output_dir=self.temp_dir)

        # /workflow with alias chapter2
        shell.do_workflow("chapter2 ACT burnout")

        # /literature
        shell.do_literature("درمان مبتنی بر پذیرش و تعهد")

        # /biblio
        shell.do_biblio("درمان مبتنی بر پذیرش و تعهد")


if __name__ == "__main__":
    unittest.main()
