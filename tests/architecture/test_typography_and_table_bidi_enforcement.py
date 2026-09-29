#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/architecture/test_typography_and_table_bidi_enforcement.py

Regression Test Suite for Directive 5 Persian Academic Typography & Table BiDi Directionality:
1. Zero Inline Latin Invariant: Inline English words in Persian text are mechanically blocked.
2. Transliteration + Footnotes Permitted: Phonetic transliteration with markdown/footnotes is allowed.
3. Whitelisted Statistics Permitted: Standard APA symbols (M, SD, t, F, p, r, etc.) are allowed.
4. Native OpenXML Footnotes Integrity: Missing footnotes.xml with footnoteReferences is blocked.
5. Persian Table BiDi Visual Enforced: Tables with Persian text must have <w:bidiVisual/> (PASS) or trigger FAIL.
6. English Table LTR: Tables with pure English text omit <w:bidiVisual/> and render LTR (PASS).
"""

import os
import sys
import zipfile
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
for p in (ROOT_DIR, AGENTS_DIR, os.path.join(AGENTS_DIR, "hooks"), os.path.join(AGENTS_DIR, "validators")):
    if os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)

import importlib.util
spec = importlib.util.spec_from_file_location("writer_guard", os.path.join(AGENTS_DIR, "agents", "academic-writer", "guard.py"))
writer_guard = importlib.util.module_from_spec(spec)
spec.loader.exec_module(writer_guard)

from validators.academic_chapter_auditor import AcademicChapterAuditor


class TestTypographyAndTableBiDiEnforcement(unittest.TestCase):

    def test_01_raw_inline_latin_in_persian_is_blocked(self):
        """Directive 5: Raw inline English author names or terms in Persian text must be denied."""
        bad_texts = [
            "بر اساس یافته‌های Smith و همکاران فرضیه اول تایید گردید.",
            "متغیر Self-Efficacy به عنوان متغیر میانجی وارد مدل شد.",
            "با استناد به پژوهش Bandura و Johnson رابطه معنادار بود."
        ]
        for txt in bad_texts:
            payload = {
                "toolCall": {
                    "name": "write_to_file",
                    "args": {"TargetFile": "03_deliverables/chapter_4_results.md", "CodeContent": txt}
                },
                "agentName": "academic-writer"
            }
            res = writer_guard.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "deny", f"Failed to block inline Latin in: {txt}")
            self.assertIn("Zero Inline Latin Invariant", res.get("reason", ""))

    def test_02_transliterated_persian_with_footnotes_is_allowed(self):
        """Transliterated foreign names (اسمیت) with footnotes and standard APA stats are allowed."""
        valid_text = (
            "بر اساس یافته‌های اسمیت و همکاران[^1]، میانگین نمرات خودکارآمدی "
            "(M = 14.50, SD = 2.15, t(48) = 3.42, p < 0.001) به طور معناداری بالاتر بود.\n\n"
            "[^1]: Smith et al. (2023)"
        )
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": "03_deliverables/chapter_4_results.md", "CodeContent": valid_text}
            },
            "agentName": "academic-writer"
        }
        res = writer_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "allow", f"Incorrectly blocked valid Persian text: {res}")

    def test_03_native_openxml_footnotes_audit(self):
        """DOCX files with footnote references must contain valid word/footnotes.xml."""
        with tempfile.TemporaryDirectory() as td:
            # Case A: Corrupted - references footnotes but missing footnotes.xml
            corrupt_docx = os.path.join(td, "corrupt.docx")
            doc_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>اسمیت</w:t><w:footnoteReference w:id="1"/></w:r></w:p>
    <w:p><w:r><w:t>Some body text that exceeds one hundred characters to satisfy non-empty body paragraph checks easily.</w:t></w:r></w:p>
  </w:body>
</w:document>'''
            with zipfile.ZipFile(corrupt_docx, "w") as zf:
                zf.writestr("word/document.xml", doc_xml)
            ok, msg = writer_guard.check_docx_openxml_integrity(corrupt_docx)
            self.assertFalse(ok)
            self.assertIn("missing from the zip archive", msg)

            # Case B: Valid - contains footnotes.xml with valid footnote
            valid_docx = os.path.join(td, "valid.docx")
            fn_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<w:footnotes xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:footnote w:id="1"><w:p><w:r><w:t>Smith (2023)</w:t></w:r></w:p></w:footnote>
</w:footnotes>'''
            with zipfile.ZipFile(valid_docx, "w") as zf:
                zf.writestr("word/document.xml", doc_xml)
                zf.writestr("word/footnotes.xml", fn_xml)
            ok_valid, msg_valid = writer_guard.check_docx_openxml_integrity(valid_docx)
            self.assertTrue(ok_valid, f"Valid docx failed footnote check: {msg_valid}")

    def test_04_persian_table_with_bidi_visual_passes(self):
        """Persian tables with <w:bidiVisual/> pass the CHK-TABLE-BIDI-DIRECTION check."""
        xml_persian_good = '''<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:tbl>
      <w:tblPr><w:bidiVisual/></w:tblPr>
      <w:tr><w:tc><w:p><w:r><w:t>جدول توزیع فراوانی متغیرها</w:t></w:r></w:p></w:tc></w:tr>
    </w:tbl>
  </w:body>
</w:document>'''
        root = ET.fromstring(xml_persian_good)
        auditor = AcademicChapterAuditor("dummy.docx")
        auditor._audit_tables(root)
        check = next(c for c in auditor.results if c["check_id"] == "CHK-TABLE-BIDI-DIRECTION")
        self.assertEqual(check["verdict"], "PASS")
        self.assertEqual(len(check["errors"]), 0)

    def test_05_persian_table_without_bidi_visual_fails(self):
        """Persian tables lacking <w:bidiVisual/> strictly fail CHK-TABLE-BIDI-DIRECTION."""
        xml_persian_bad = '''<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:tbl>
      <w:tblPr></w:tblPr>
      <w:tr><w:tc><w:p><w:r><w:t>جدول توزیع فراوانی متغیرها</w:t></w:r></w:p></w:tc></w:tr>
    </w:tbl>
  </w:body>
</w:document>'''
        root = ET.fromstring(xml_persian_bad)
        auditor = AcademicChapterAuditor("dummy.docx")
        auditor._audit_tables(root)
        check = next(c for c in auditor.results if c["check_id"] == "CHK-TABLE-BIDI-DIRECTION")
        self.assertEqual(check["verdict"], "FAIL")
        self.assertIn("lacks <w:bidiVisual/>", check["errors"][0])

    def test_06_english_table_without_bidi_visual_passes_ltr(self):
        """Pure English tables without <w:bidiVisual/> are correctly recognized as LTR and pass."""
        xml_en = '''<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:tbl>
      <w:tblPr></w:tblPr>
      <w:tr><w:tc><w:p><w:r><w:t>Descriptive Statistics Table</w:t></w:r></w:p></w:tc></w:tr>
    </w:tbl>
  </w:body>
</w:document>'''
        root = ET.fromstring(xml_en)
        auditor = AcademicChapterAuditor("dummy.docx")
        auditor._audit_tables(root)
        check = next(c for c in auditor.results if c["check_id"] == "CHK-TABLE-BIDI-DIRECTION")
        self.assertEqual(check["verdict"], "PASS")
        self.assertEqual(len(check["errors"]), 0)


if __name__ == "__main__":
    unittest.main()
