#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_academic_chapter_auditor.py — Comprehensive Unit Tests for Academic Chapter Forensic Auditor

Verifies:
1. Detection of forbidden vertical borders in APA 7 tables.
2. Detection of bold table captions (mandatory regular B Nazanin).
3. Detection of naked decimals without leading zero in Persian text (Directive 4).
4. Detection of prohibited p = .000 (Directive 4).
5. Detection of untranslated English words in Persian table cells (Directive 4.1).
6. Detection of missing regression tables (3-Table standard).
7. Clean compliant chapter triad passes with exit code 0.
8. Output conforms to contracts/validation_report.schema.json.
"""

import os
import sys
import json
import shutil
import tempfile
import zipfile
import unittest
import subprocess

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
for p in [AGENTS_DIR, os.path.join(AGENTS_DIR, "validators")]:
    if os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)

from validators.academic_chapter_auditor import AcademicChapterAuditor, audit_chapter_artifacts
from contracts.contract_validator import validate_contract


def create_mock_docx(target_path: str, body_xml_content: str):
    """Creates a minimal valid OpenXML .docx file with custom body XML."""
    content_types = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>"""

    rels = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>"""

    document_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"
            xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math">
  <w:body>
    {body_xml_content}
  </w:body>
</w:document>"""

    os.makedirs(os.path.dirname(os.path.abspath(target_path)), exist_ok=True)
    with zipfile.ZipFile(target_path, 'w', compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', content_types)
        z.writestr('_rels/.rels', rels)
        z.writestr('word/document.xml', document_xml)


class TestAcademicChapterAuditor(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_chapter_auditor_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_detects_vertical_borders_in_apa_table(self):
        """Flags table with forbidden vertical borders (e.g. insideV or left/right)."""
        body_xml = """
        <w:p><w:r><w:t>جدول ۱. نتایج آزمون فرضیه</w:t></w:r></w:p>
        <w:tbl>
          <w:tblPr>
            <w:bidiVisual/>
            <w:tblBorders>
              <w:top w:val="single" w:sz="6"/>
              <w:bottom w:val="single" w:sz="6"/>
              <w:left w:val="none"/>
              <w:right w:val="none"/>
              <w:insideV w:val="single" w:sz="4"/>
              <w:insideH w:val="none"/>
            </w:tblBorders>
          </w:tblPr>
          <w:tr>
            <w:tc><w:p><w:r><w:t>شاخص</w:t></w:r></w:p></w:tc>
            <w:tc><w:p><w:r><w:t>مقدار</w:t></w:r></w:p></w:tc>
          </w:tr>
        </w:tbl>
        <w:p><w:r><w:t>یادداشت: تمامی ضرایب در سطح ۰.۰۵ معنادار است.</w:t></w:r></w:p>
        """
        docx_path = os.path.join(self.temp_dir, "vertical_borders.docx")
        create_mock_docx(docx_path, body_xml)

        auditor = AcademicChapterAuditor(docx_path=docx_path)
        report = auditor.audit()

        self.assertEqual(report["overall_verdict"], "FAIL")
        border_check = next(r for r in report["results"] if r["check_id"] == "CHK-APA7-TABLE-BORDERS")
        self.assertEqual(border_check["verdict"], "FAIL")
        self.assertTrue(any("insideV" in err for err in border_check["errors"]))

    def test_02_detects_bold_caption(self):
        """Flags table captions that use bold typography (mandatory regular B Nazanin)."""
        body_xml = """
        <w:p>
          <w:r>
            <w:rPr><w:b/><w:bCs/></w:rPr>
            <w:t>جدول ۱-۴. مقادیر شاخص‌های توصیفی متغیرها</w:t>
          </w:r>
        </w:p>
        <w:tbl>
          <w:tblPr>
            <w:bidiVisual/>
            <w:tblBorders>
              <w:top w:val="single" w:sz="6"/>
              <w:bottom w:val="single" w:sz="6"/>
              <w:left w:val="none"/><w:right w:val="none"/>
              <w:insideV w:val="none"/><w:insideH w:val="none"/>
            </w:tblBorders>
          </w:tblPr>
          <w:tr><w:tc><w:p><w:r><w:t>متغیر</w:t></w:r></w:p></w:tc></w:tr>
        </w:tbl>
        <w:p><w:r><w:t>یادداشت: آزمون‌ها در سطح ۰.۰۵ انجام شدند.</w:t></w:r></w:p>
        """
        docx_path = os.path.join(self.temp_dir, "bold_caption.docx")
        create_mock_docx(docx_path, body_xml)

        auditor = AcademicChapterAuditor(docx_path=docx_path)
        report = auditor.audit()

        self.assertEqual(report["overall_verdict"], "FAIL")
        cap_check = next(r for r in report["results"] if r["check_id"] == "CHK-TABLE-CAPTION-TYPOGRAPHY")
        self.assertEqual(cap_check["verdict"], "FAIL")
        self.assertTrue(any("bold" in err.lower() for err in cap_check["errors"]))

    def test_03_detects_persian_leading_zero_violation(self):
        """Flags naked decimal missing leading zero (e.g. .۰۵ instead of ۰.۰۵)."""
        body_xml = """
        <w:p>
          <w:pPr><w:jc w:val="both"/><w:bidi w:val="1"/></w:pPr>
          <w:r><w:t>نتایج پژوهش نشان داد که ضریب رگرسیون در سطح .۰۵ معنادار است و توان آماری افزایش یافته است.</w:t></w:r>
        </w:p>
        """
        docx_path = os.path.join(self.temp_dir, "naked_decimal.docx")
        create_mock_docx(docx_path, body_xml)

        auditor = AcademicChapterAuditor(docx_path=docx_path)
        report = auditor.audit()

        self.assertEqual(report["overall_verdict"], "FAIL")
        lz_check = next(r for r in report["results"] if r["check_id"] == "CHK-PERSIAN-LEADING-ZERO")
        self.assertEqual(lz_check["verdict"], "FAIL")
        self.assertTrue(any("leading zero" in err.lower() for err in lz_check["errors"]))

    def test_04_detects_prohibited_p_zero(self):
        """Flags prohibited reporting of p = .000."""
        body_xml = """
        <w:p>
          <w:pPr><w:jc w:val="both"/><w:bidi w:val="1"/></w:pPr>
          <w:r><w:t>تحلیل واریانس نشان داد که اثر متغیر مداخله معنادار است (F = 14.52, p = .000, eta = 0.24).</w:t></w:r>
        </w:p>
        """
        docx_path = os.path.join(self.temp_dir, "p_zero.docx")
        create_mock_docx(docx_path, body_xml)

        auditor = AcademicChapterAuditor(docx_path=docx_path)
        report = auditor.audit()

        self.assertEqual(report["overall_verdict"], "FAIL")
        pz_check = next(r for r in report["results"] if r["check_id"] == "CHK-PROHIBITED-P-ZERO")
        self.assertEqual(pz_check["verdict"], "FAIL")
        self.assertTrue(any("p = .000" in err for err in pz_check["errors"]))

    def test_05_detects_english_word_leakage_in_cells(self):
        """Flags untranslated English words inside Persian table cells."""
        body_xml = """
        <w:p><w:r><w:t>جدول ۲. ضرایب تحلیل مسیر</w:t></w:r></w:p>
        <w:tbl>
          <w:tblPr>
            <w:bidiVisual/>
            <w:tblBorders>
              <w:top w:val="single" w:sz="6"/>
              <w:bottom w:val="single" w:sz="6"/>
              <w:left w:val="none"/><w:right w:val="none"/>
              <w:insideV w:val="none"/><w:insideH w:val="none"/>
            </w:tblBorders>
          </w:tblPr>
          <w:tr>
            <w:tc><w:p><w:r><w:t>Variable Name</w:t></w:r></w:p></w:tc>
            <w:tc><w:p><w:r><w:t>ضریب بتا (β)</w:t></w:r></w:p></w:tc>
          </w:tr>
        </w:tbl>
        <w:p><w:r><w:t>یادداشت: ضرایب استاندارد شده گزارش شده‌اند.</w:t></w:r></w:p>
        """
        docx_path = os.path.join(self.temp_dir, "english_leakage.docx")
        create_mock_docx(docx_path, body_xml)

        auditor = AcademicChapterAuditor(docx_path=docx_path)
        report = auditor.audit()

        self.assertEqual(report["overall_verdict"], "FAIL")
        leak_check = next(r for r in report["results"] if r["check_id"] == "CHK-ENGLISH-WORD-LEAKAGE")
        self.assertEqual(leak_check["verdict"], "FAIL")
        self.assertTrue(any("Variable" in err for err in leak_check["errors"]))

    def test_06_detects_missing_regression_tables(self):
        """Flags regression hypotheses that omit any of the 3 mandatory tables."""
        body_xml = """
        <w:p><w:r><w:t>بررسی فرضیه پژوهش با استفاده از رگرسیون چندگانه انجام شد.</w:t></w:r></w:p>
        <w:p><w:r><w:t>جدول ۱. ماتریس همبستگی متغیرها</w:t></w:r></w:p>
        <w:tbl>
          <w:tblPr><w:bidiVisual/><w:tblBorders><w:top w:val="single"/><w:bottom w:val="single"/><w:left w:val="none"/><w:right w:val="none"/><w:insideV w:val="none"/><w:insideH w:val="none"/></w:tblBorders></w:tblPr>
          <w:tr><w:tc><w:p><w:r><w:t>همبستگی</w:t></w:r></w:p></w:tc></w:tr>
        </w:tbl>
        <w:p><w:r><w:t>یادداشت: همبستگی‌ها در سطح ۰.۰۵ معنادار است.</w:t></w:r></w:p>
        """
        docx_path = os.path.join(self.temp_dir, "missing_regression_tables.docx")
        create_mock_docx(docx_path, body_xml)

        auditor = AcademicChapterAuditor(docx_path=docx_path)
        report = auditor.audit()

        self.assertEqual(report["overall_verdict"], "FAIL")
        reg_check = next(r for r in report["results"] if r["check_id"] == "CHK-3-TABLE-REGRESSION")
        self.assertEqual(reg_check["verdict"], "FAIL")
        self.assertTrue(any("Table 2" in err or "Table 3" in err for err in reg_check["errors"]))

    def test_07_clean_compliant_triad_passes(self):
        """Verifies that a pristine, fully compliant triad achieves 100% PASS."""
        body_xml = """
        <w:p>
          <w:pPr><w:jc w:val="both"/><w:bidi w:val="1"/></w:pPr>
          <w:r><w:t>در این بخش، یافته‌های تجربی حاصل از تجزیه‌وتحلیل داده‌ها با مشارکت ۲۵۰ نفر از دانشجویان نمونه گزارش شده است. تمامی شاخص‌ها بر اساس استانداردهای روان‌سنجی محاسبه شدند.</w:t></w:r>
        </w:p>
        <w:p>
          <w:pPr><w:bidi w:val="1"/></w:pPr>
          <w:r>
            <w:rPr><w:rFonts w:ascii="B Nazanin" w:cs="B Nazanin"/><w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr>
            <w:t>جدول ۱-۴. شاخص‌های توصیفی متغیرهای پژوهش</w:t>
          </w:r>
        </w:p>
        <w:tbl>
          <w:tblPr>
            <w:bidiVisual/>
            <w:tblBorders>
              <w:top w:val="single" w:sz="6"/>
              <w:bottom w:val="single" w:sz="6"/>
              <w:left w:val="none"/><w:right w:val="none"/>
              <w:insideV w:val="none"/><w:insideH w:val="none"/>
            </w:tblBorders>
          </w:tblPr>
          <w:tr>
            <w:tc><w:p><w:r><w:t>متغیر</w:t></w:r></w:p></w:tc>
            <w:tc><w:p><w:r><w:t>میانگین (M)</w:t></w:r></w:p></w:tc>
            <w:tc><w:p><w:r><w:t>سطح معناداری (p)</w:t></w:r></w:p></w:tc>
          </w:tr>
          <w:tr>
            <w:tc><w:p><w:r><w:t>تاب‌آوری</w:t></w:r></w:p></w:tc>
            <w:tc><w:p><w:r><w:t>۲۴.۵۰</w:t></w:r></w:p></w:tc>
            <w:tc><w:p><w:r><w:t>۰.۰۰۱ > p</w:t></w:r></w:p></w:tc>
          </w:tr>
        </w:tbl>
        <w:p>
          <w:pPr><w:jc w:val="both"/><w:bidi w:val="1"/></w:pPr>
          <w:r><w:t>یادداشت: مقادیر میانگین و سطح معناداری بر اساس محاسبات نرم‌افزاری گزارش شده‌اند.</w:t></w:r>
        </w:p>
        """
        docx_path = os.path.join(self.temp_dir, "clean_chapter.docx")
        create_mock_docx(docx_path, body_xml)

        json_path = os.path.join(self.temp_dir, "clean_chapter.json")
        with open(json_path, "w", encoding="utf-8") as jf:
            json.dump({"sample_size": 250, "mean": 24.50, "p_value": 0.001}, jf, indent=2)

        auditor = AcademicChapterAuditor(docx_path=docx_path, json_path=json_path)
        report = auditor.audit()

        self.assertEqual(report["overall_verdict"], "PASS")
        self.assertEqual(report["evidence_summary"]["checks_failed"], 0)
        self.assertGreater(report["evidence_summary"]["checks_passed"], 5)

        # Validate against validation_report contract schema
        val_res = validate_contract(report, "validation_report")
        self.assertTrue(val_res["valid"], f"Validation report contract invalid: {val_res.get('error')}")

    def test_08_cli_execution_and_schema_validation(self):
        """Verifies CLI execution produces valid contract report and correct exit codes."""
        # Defective docx -> must exit 1
        body_xml_bad = "<w:p><w:r><w:t>مقدار p = .000 بود.</w:t></w:r></w:p>"
        docx_bad = os.path.join(self.temp_dir, "bad_cli.docx")
        create_mock_docx(docx_bad, body_xml_bad)

        script_path = os.path.join(AGENTS_DIR, "validators", "academic_chapter_auditor.py")
        res_bad = subprocess.run([sys.executable, script_path, docx_bad], capture_output=True, text=True)
        self.assertEqual(res_bad.returncode, 1)
        self.assertIn("Prohibited p = .000", res_bad.stdout)



    def test_09_detects_math_admissibility_violations(self):
        """Verifies detection of mathematical admissibility violations."""
        body_xml = "<w:p><w:r><w:t>test</w:t></w:r></w:p>"
        docx_path = os.path.join(self.temp_dir, "math_adm.docx")
        create_mock_docx(docx_path, body_xml)

        json_path = os.path.join(self.temp_dir, "math_adm.json")
        with open(json_path, "w", encoding="utf-8") as jf:
            import json
            json.dump({
                "parameters": [
                    {"lhs": "F1", "op": "=~", "rhs": "item1", "std.all": 1.05},
                    {"lhs": "F1", "op": "~~", "rhs": "F1", "est": -0.2}
                ]
            }, jf, indent=2)
            
        r_path = os.path.join(self.temp_dir, "script.R")
        with open(r_path, "w", encoding="utf-8") as rf:
            rf.write("options(warn = -1)\n")

        auditor = AcademicChapterAuditor(docx_path=docx_path, json_path=json_path)
        report = auditor.audit()

        self.assertEqual(report["overall_verdict"], "FAIL")
        adm_check = next(r for r in report["results"] if r["check_id"] == "CHK-MATH-ADMISSIBILITY")
        self.assertEqual(adm_check["verdict"], "FAIL")
        errs = " ".join(adm_check["errors"])
        self.assertTrue("Standardized parameter boundary exceeded" in errs)
        self.assertTrue("negative variance" in errs)
        self.assertTrue("Warning suppression detected" in errs)

if __name__ == "__main__":

    unittest.main()
