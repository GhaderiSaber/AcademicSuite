#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_academic_writer_scoped_audit.py — Unit Tests for Academic Writer Scoped Audit & Clean Exit

Verifies:
1. Subagent Clean Termination: Subagents terminate cleanly without getting blocked by deliverable scans.
2. Identity Resolution: Subagents detected via hook identity contract or parent conversation cleanly exit.
3. Scoped Deliverable Audit: Untouched historical deliverables with defects do not block unrelated tasks.
4. Target Deliverable Audit: Active deliverables targeted by the writer are still rigorously verified.
5. CLI Tooling: academic_docgen.py patch-docx-dom correctly fixes justified <w:br/> elements.
"""

import os
import sys
import json
import time
import shutil
import tempfile
import unittest
import zipfile
import xml.etree.ElementTree as ET
from argparse import Namespace

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
HOOKS_DIR = os.path.join(ROOT_DIR, ".agents", "hooks")
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
WRITER_DIR = os.path.join(ROOT_DIR, ".agents", "agents", "academic-writer")
for p in (ROOT_DIR, HOOKS_DIR, AGENTS_DIR, WRITER_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

import guard as writer_guard
from academic_lifecycle_dispatcher import enrich_payload_identity
from scripts.academic_docgen import cmd_patch_docx_dom, cmd_inspect_docx


def create_minimal_docx(path: str, paragraphs: list, footnotes: bool = False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    ns_w = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
    
    body_xml_parts = []
    for p_info in paragraphs:
        text = p_info.get("text", "Default test narrative paragraph text in Persian.")
        align = p_info.get("align", "both")
        has_br = p_info.get("has_br", False)
        
        br_xml = "<w:br/>" if has_br else ""
        body_xml_parts.append(f"""
        <w:p>
            <w:pPr>
                <w:bidi w:val="1"/>
                <w:jc w:val="{align}"/>
            </w:pPr>
            <w:r>
                <w:rPr><w:rtl w:val="1"/></w:rPr>
                <w:t>{text}</w:t>
                {br_xml}
            </w:r>
        </w:p>
        """)
        
    doc_xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <w:document xmlns:w="{ns_w}">
        <w:body>
            {''.join(body_xml_parts)}
        </w:body>
    </w:document>
    """
    
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("word/document.xml", doc_xml)
        if footnotes:
            zf.writestr("word/footnotes.xml", f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
            <w:footnotes xmlns:w="{ns_w}">
                <w:footnote w:id="1"><w:p><w:r><w:t>Note</w:t></w:r></w:p></w:footnote>
            </w:footnotes>
            """)


class TestAcademicWriterScopedAudit(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_writer_audit_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_01_subagent_clean_exit_with_is_subagent_flag(self):
        """Subagents with explicit isSubagent: true terminate cleanly without stop blocks."""
        payload = {
            "conversationId": "test-subagent-001",
            "isSubagent": True,
            "workspacePaths": [self.temp_dir]
        }
        res = writer_guard.handle_stop(payload)
        self.assertEqual(res.get("decision"), "allow")

    def test_02_subagent_clean_exit_with_parent_conversation_id(self):
        """Subagents with parentConversationId terminate cleanly."""
        payload = {
            "conversationId": "test-subagent-002",
            "parentConversationId": "parent-orchestrator-123",
            "workspacePaths": [self.temp_dir]
        }
        res = writer_guard.handle_stop(payload)
        self.assertEqual(res.get("decision"), "allow")

    def test_03_enrich_payload_identity_sets_is_subagent(self):
        """academic_lifecycle_dispatcher.enrich_payload_identity resolves subagent status."""
        payload = {
            "conversationId": "3f9a42c9-2f20-4c54-a2f5-6839440e9924",
            "workspacePaths": [self.temp_dir]
        }
        enriched = enrich_payload_identity(payload)
        self.assertTrue(enriched.get("isSubagent"), "Should resolve subagent status from conversation descriptor")

    def test_04_scoped_audit_ignores_untouched_historical_files(self):
        """Untouched historical files in 03_deliverables do not block a non-subagent stop."""
        deliv_dir = os.path.join(self.temp_dir, "03_deliverables")
        os.makedirs(deliv_dir, exist_ok=True)
        
        # 1. Untouched corrupt file with manual br in justified body
        old_corrupt = os.path.join(deliv_dir, "untouched_brief.docx")
        create_minimal_docx(old_corrupt, [
            {"text": "این یک متن آزمایشی قدیمی برای سنجش است که بیش از صد کاراکتر طول دارد و معیوب است.", "align": "both", "has_br": True}
        ])
        # Set mtime back by 4 hours
        old_time = time.time() - 15000
        os.utime(old_corrupt, (old_time, old_time))
        
        # 2. Target file that is clean
        clean_target = os.path.join(deliv_dir, "Chapter_4_Results.docx")
        create_minimal_docx(clean_target, [
            {"text": "یافته‌های فصل چهارم پژوهش حاضر نشان داد که ضرایب مسیر در سطح ۰.۰۰۱ معنادار هستند و بیش از صد کاراکتر متن تحلیلی دارد.", "align": "both", "has_br": False}
        ])
        
        transcript_file = os.path.join(self.temp_dir, "transcript.jsonl")
        with open(transcript_file, "w", encoding="utf-8") as tf:
            tf.write(json.dumps({
                "type": "PLANNER_RESPONSE",
                "content": 'Completed drafting "Chapter_4_Results.docx" successfully.'
            }) + "\n")
            
        payload = {
            "conversationId": "standalone-session",
            "transcriptPath": transcript_file,
            "workspacePaths": [self.temp_dir]
        }
        
        res = writer_guard.handle_stop(payload)
        self.assertEqual(res.get("decision"), "allow", f"Should allow stop because corrupt file was not targeted: {res}")

    def test_05_scoped_audit_catches_targeted_corrupt_file(self):
        """If the targeted deliverable contains <w:br/> in justified body, stop is blocked."""
        deliv_dir = os.path.join(self.temp_dir, "03_deliverables")
        os.makedirs(deliv_dir, exist_ok=True)
        
        target_file = os.path.join(deliv_dir, "Chapter_4_Results.docx")
        create_minimal_docx(target_file, [
            {"text": "یافته‌های فصل چهارم پژوهش حاضر نشان داد که ضرایب مسیر در سطح معنادار هستند و متن بیش از صد کاراکتر دارد.", "align": "both", "has_br": True}
        ])
        
        transcript_file = os.path.join(self.temp_dir, "transcript.jsonl")
        with open(transcript_file, "w", encoding="utf-8") as tf:
            tf.write(json.dumps({
                "type": "PLANNER_RESPONSE",
                "content": 'Compiling "Chapter_4_Results.docx" deliverable.'
            }) + "\n")
            
        payload = {
            "conversationId": "standalone-session",
            "transcriptPath": transcript_file,
            "workspacePaths": [self.temp_dir]
        }
        
        res = writer_guard.handle_stop(payload)
        self.assertEqual(res.get("decision"), "continue")
        self.assertIn("contains manual line break (<w:br/>) inside justified body text", res.get("reason", ""))

    def test_06_patch_docx_dom_fixes_justified_linebreaks(self):
        """academic_docgen.py patch-docx-dom remediates justified linebreaks."""
        target_file = os.path.join(self.temp_dir, "test_doc.docx")
        long_text = "دانشگاه علوم پزشکی کاشان دانشکده پزشکی گروه روان‌پزشکی و روان‌شناسی بالینی پژوهش حاضر در راستای ارزیابی ساختاری مدل انجام گردیده است."
        create_minimal_docx(target_file, [
            {"text": long_text, "align": "both", "has_br": True}
        ])
        
        # Verify it has justified br
        insp_args = Namespace(docx=target_file, file=None)
        # Check inspect runs
        self.assertEqual(cmd_inspect_docx(insp_args), 0)
        
        # Patch linebreaks
        patch_args = Namespace(docx=target_file, file=None, action="fix-linebreaks", sync_root=False)
        self.assertEqual(cmd_patch_docx_dom(patch_args), 0)
        
        # Verify it passes check_docx_openxml_integrity
        ok, reason = writer_guard.check_docx_openxml_integrity(target_file)
        self.assertTrue(ok, f"Expected patched docx to be valid, got: {reason}")


if __name__ == "__main__":
    unittest.main()
