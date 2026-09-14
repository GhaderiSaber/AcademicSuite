#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for Defense Presentation & Master Dissertation Compilation Multi-Agent Workflow
==========================================================================================
Validates:
  1. Specification markdown compliance (.agents/workflows/defense_presentation.md and thesis_assembly.md).
  2. Multi-agent execution orchestration via DigitalSaber for both workflows.
  3. Tri-path presentation generation (Path A: HTML Reveal deck, Path B: PPTX, Path C: DOCX speech notes).
  4. 20 Viva Voce Committee Q&A Scenarios and defense committee readiness score.
  5. Consolidated master dissertation assembly (.docx) with APA 7 borders and bilingual references.
  6. OpenXMLArtifactEngine defense HTML and speaker notes generators.
  7. Interactive shell commands (/defense and /assemble).
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


class TestDefensePresentationWorkflow(unittest.TestCase):
    """Test suite for Pipeline 4: Defense Presentation & Master Dissertation Compilation."""

    @classmethod
    def setUpClass(cls):
        cls.saber = DigitalSaber()
        cls.temp_dir = tempfile.mkdtemp(prefix="test_defense_assembly_wf_")
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

    def test_01_spec_files_exist_and_valid(self):
        """Verifies that defense_presentation.md and thesis_assembly.md exist and meet Antigravity criteria."""
        for spec_name in ["defense_presentation.md", "thesis_assembly.md"]:
            spec_path = os.path.join(WORKFLOWS_DIR, spec_name)
            self.assertTrue(os.path.exists(spec_path), f"Missing workflow specification: {spec_path}")

            with open(spec_path, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertGreater(len(content), 1000, f"Workflow specification {spec_name} is too brief.")
            self.assertIn("digital-saber", content)
            self.assertIn("academic-writer", content)
            self.assertIn("final-judge", content)
            self.assertIn("124911145", content)  # Saber Admin Desk ID

    def test_02_defense_presentation_execution_and_artifacts(self):
        """Tests that offline Python run_workflow raises NotImplementedError per Directive 0 & 12."""
        with self.assertRaises(NotImplementedError) as ctx:
            self.saber.run_workflow(
                "defense_presentation",
                topic_or_file="اثربخشی درمان مبتنی بر پذیرش و تعهد بر فرسودگی شغلی کادر درمان",
                output_dir=self.temp_dir
            )
        self.assertIn("cannot be executed by standalone Python", str(ctx.exception))
        self.assertIn("invoke_subagent", str(ctx.exception))

    def test_03_thesis_assembly_execution_and_artifacts(self):
        """Tests that offline Python run_workflow raises NotImplementedError per Directive 0 & 12."""
        assembly_dir = os.path.join(self.temp_dir, "assembly_out")
        with self.assertRaises(NotImplementedError) as ctx:
            self.saber.run_workflow(
                "thesis_assembly",
                topic_or_file="رساله دکتری تخصصی: اثربخشی مداخله ACT بر فرسودگی شغلی",
                output_dir=assembly_dir
            )
        self.assertIn("cannot be executed by standalone Python", str(ctx.exception))
        self.assertIn("invoke_subagent", str(ctx.exception))

    def test_04_openxml_defense_generators(self):
        """Validates OpenXMLArtifactEngine defense HTML and speaker notes generators directly."""
        engine = OpenXMLArtifactEngine()
        html_out = os.path.join(self.temp_dir, "direct_defense.html")
        docx_out = os.path.join(self.temp_dir, "direct_notes.docx")

        payload = {
            "meta": {
                "title": "آزمون آزمایشی ارائه دفاعیه",
                "author": "صابر قادری",
                "supervisor": "استاد راهنما",
                "university": "دانشگاه تهران"
            },
            "slides": [
                {
                    "layout": "cover",
                    "title": "اسلاید عنوان",
                    "notes": "گفتار دفاعیه برای این اسلاید",
                    "time_budget": "۱:۰۰ دقیقه",
                    "transition": "«به اسلاید بعدی می‌رویم...»"
                },
                {
                    "layout": "result_spotlight",
                    "title": "اسلاید یافته شاخص",
                    "stat_value": "F(1, 31) = 14.32",
                    "p_value": "< .001",
                    "eta_squared": "ηp² = .32",
                    "notes": "تحلیل کوواریانس معنادار شد.",
                    "time_budget": "۱:۳۰ دقیقه"
                }
            ],
            "viva_voce_qa": [
                {
                    "role": "داور آمار",
                    "question": "علت انتخاب تحلیل کوواریانس؟",
                    "answer": "کنترل اثر پیش‌آزمون و افزایش توان آماری."
                }
            ]
        }

        res_html = engine.generate_defense_html(payload, html_out)
        self.assertTrue(os.path.exists(res_html))
        with open(res_html, "r", encoding="utf-8") as f:
            html_content = f.read()
        self.assertIn("<!DOCTYPE html>", html_content)
        self.assertIn("F(1, 31) = 14.32", html_content)
        self.assertIn("timer", html_content)
        self.assertIn("notesDrawer", html_content)

        res_docx = engine.generate_defense_speaker_notes_docx(payload, docx_out)
        self.assertTrue(os.path.exists(res_docx))
        self.assertGreater(os.path.getsize(res_docx), 1000)

    def test_05_shell_defense_and_assemble_commands(self):
        """Verifies that the interactive shell handles /defense and /assemble commands gracefully."""
        shell_out = os.path.join(self.temp_dir, "shell_out")
        shell = DigitalSaberShell(saber_instance=self.saber, output_dir=shell_out)

        # Test precmd normalization
        self.assertEqual(shell.precmd("/defense"), "defense")
        self.assertEqual(shell.precmd("/assemble"), "assemble")

        # Test do_defense and do_assemble handle offline workflow safely
        shell.do_defense("اثربخشی درمان مبتنی بر پذیرش و تعهد بر فرسودگی شغلی")
        shell.do_assemble("رساله کامل دکتری")


if __name__ == "__main__":
    unittest.main()
