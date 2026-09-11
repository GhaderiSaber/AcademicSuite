#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit Tests for OpenXML Artifact Engine, OMML Equation Builder, and Workflow Compilation
"""

import os
import sys
import unittest
import tempfile
import shutil
import docx

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
SHARED_DIR = os.path.abspath(os.path.join(TESTS_DIR, ".."))
AGENTS_DIR = os.path.abspath(os.path.join(SHARED_DIR, ".."))
ROOT_DIR = os.path.abspath(os.path.join(AGENTS_DIR, ".."))

for p in [ROOT_DIR, AGENTS_DIR, SHARED_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from openxml_artifact_engine import OpenXMLArtifactEngine
from generate_audit_report_docx import build_audit_report_document
from generate_defense_card_docx import build_defense_card_document
from digital_saber import DigitalSaber


class TestOpenXMLArtifactEngine(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.engine = OpenXMLArtifactEngine()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_01_omml_equation_generation(self):
        """Validates that OMML equation generators construct valid <m:oMath> nodes."""
        omml_f = self.engine.create_omml_f_test(df1=1, df2=31, f_val=14.32, p_val="< .001", eta_p2=0.316)
        self.assertTrue(omml_f.tag.endswith("}oMath"))

        omml_t = self.engine.create_omml_t_test(df=28, t_val=3.45, p_val=".014", cohen_d=0.78)
        self.assertTrue(omml_t.tag.endswith("}oMath"))

        omml_reg = self.engine.create_omml_regression(beta=0.42, t_val=3.12, p_val=".002", r2=0.38)
        self.assertTrue(omml_reg.tag.endswith("}oMath"))

    def test_02_rule5_omml_text_extraction(self):
        """Verifies Rule 5: dual-node extraction captures OMML math text invisible to paragraph.text."""
        doc = docx.Document()
        p = doc.add_paragraph("نتایج آزمون تحلیل کوواریانس: ")
        omml = self.engine.create_omml_f_test(df1=1, df2=31, f_val=14.32, p_val="< .001", eta_p2=0.32)
        self.engine.inject_math(p, omml)

        # Check equation detection
        self.assertTrue(self.engine.has_math(p))

        # Standard paragraph.text blindspot
        self.assertNotIn("14.32", p.text)

        # Rule 5 mandatory extraction protocol
        full_text = self.engine.extract_full_text(p)
        self.assertIn("14.32", full_text)
        self.assertIn("1, 31", full_text)
        self.assertIn("< .001", full_text)

    def test_03_apa_table_formatting(self):
        """Verifies strict APA 7 table formatting with <w:bidiVisual/> and 3 horizontal lines."""
        doc = docx.Document()
        table = doc.add_table(rows=3, cols=3)
        self.engine.style_apa_table(table)

        # Verify <w:bidiVisual/>
        xml_str = table._tbl.tblPr.xml
        self.assertIn("bidiVisual", xml_str)
        self.assertIn('w:val="single"', xml_str)
        self.assertIn('w:left w:val="none"', xml_str)
        self.assertIn('w:right w:val="none"', xml_str)

    def test_04_persian_typography_halfspaces(self):
        """Verifies that clean_persian_typography inserts half-spaces in prefixes and compound words."""
        raw = "درمان می شود و در پیش آزمون و پس آزمون بر فرسودگی شغلی و متغیر های روان شناختی بررسی گردید."
        cleaned = self.engine.clean_persian_typography(raw)
        self.assertIn("می\u200cشود", cleaned)
        self.assertIn("پیش\u200cآزمون", cleaned)
        self.assertIn("پس\u200cآزمون", cleaned)
        self.assertIn("روان\u200cشناختی", cleaned)
        self.assertIn("متغیر\u200cهای", cleaned)

    def test_05_generate_audit_report_docx(self):
        """Verifies generation of official pre-defense audit report."""
        out_path = os.path.join(self.test_dir, "گزارش_ممیزی_و_کنترل_کیفیت_آماری.docx")
        payload = {
            "title": "اثربخشی درمان مبتنی بر شفقت بر خودانتقادی دانشجویان",
            "anomaly_index": 12,
            "verdict": "CLEAN / NORMAL",
            "active_signals_count": 0
        }
        res_path = build_audit_report_document(payload, out_path)
        self.assertTrue(os.path.exists(res_path))
        self.assertGreater(os.path.getsize(res_path), 5000)

        # Open with python-docx
        loaded_doc = docx.Document(res_path)
        self.assertGreaterEqual(len(loaded_doc.paragraphs), 5)
        self.assertGreaterEqual(len(loaded_doc.tables), 2)

    def test_06_generate_defense_card_docx(self):
        """Verifies generation of viva voce defense committee simulator card."""
        out_path = os.path.join(self.test_dir, "کارت_جلسه_دفاع_و_سوالات_داوران.docx")
        payload = {
            "topic": "اثربخشی طرحواره‌درمانی بر اختلالات خوردن",
            "readiness_score": 96.5
        }
        res_path = build_defense_card_document(payload, out_path)
        self.assertTrue(os.path.exists(res_path))
        self.assertGreater(os.path.getsize(res_path), 5000)

        loaded_doc = docx.Document(res_path)
        self.assertGreaterEqual(len(loaded_doc.paragraphs), 10)
        self.assertGreaterEqual(len(loaded_doc.tables), 1)

    def test_07_all_workflows_end_to_end_artifact_compilation(self):
        """Executes all 4 multi-agent workflows and verifies that physical .docx files are created."""
        saber = DigitalSaber()

        # 1. Chapter 4 Workflow
        ch4_res = saber.run_workflow("chapter4", output_dir=self.test_dir)
        self.assertEqual(ch4_res["status"], "SUCCESS")
        for f in ch4_res["artifacts_generated"]:
            self.assertTrue(os.path.exists(f), f"File {f} not generated")
            self.assertGreater(os.path.getsize(f), 0, f"File {f} is empty")

        # 2. Proposal Workflow
        prop_res = saber.run_workflow("proposal", output_dir=self.test_dir)
        self.assertEqual(prop_res["status"], "SUCCESS")
        for f in prop_res["artifacts_generated"]:
            self.assertTrue(os.path.exists(f), f"File {f} not generated")
            self.assertGreater(os.path.getsize(f), 0, f"File {f} is empty")

        # 3. Chapter 5 Workflow
        ch5_res = saber.run_workflow("chapter5", output_dir=self.test_dir)
        self.assertEqual(ch5_res["status"], "SUCCESS")
        for f in ch5_res["artifacts_generated"]:
            self.assertTrue(os.path.exists(f), f"File {f} not generated")
            self.assertGreater(os.path.getsize(f), 0, f"File {f} is empty")

        # 4. Thesis Revision Workflow
        rev_res = saber.run_workflow("thesis_revision", output_dir=self.test_dir)
        self.assertEqual(rev_res["status"], "SUCCESS")
        for f in rev_res["artifacts_generated"]:
            self.assertTrue(os.path.exists(f), f"File {f} not generated")
            self.assertGreater(os.path.getsize(f), 0, f"File {f} is empty")


if __name__ == "__main__":
    unittest.main()
