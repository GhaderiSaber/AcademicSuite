#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_deliverable_scoping_guard.py — Regression Test Suite for Scoped Deliverable Audits

Verifies:
1. academic-writer Stop hook strictly audits 03_deliverables/ and ignores 01_raw_inputs/ and 04_references_and_lit/.
2. Raw input questionnaires with Arabic letter glyphs in 01_raw_inputs/ do NOT cause hook failures.
3. academic-orchestrator Stop hook strictly audits 03_deliverables/ and ignores non-deliverables.
4. trajectory-analyzer is permitted to write trajectory artifacts to .agents/learning/experience/ while
   being strictly blocked from mutating production deliverables (03_deliverables, 01_raw_inputs).
"""

import os
import sys
import json
import zipfile
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents", "agents")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if AGENTS_DIR not in sys.path:
    sys.path.insert(0, AGENTS_DIR)

import importlib.util

def _load_guard(agent_name):
    gpath = os.path.join(AGENTS_DIR, agent_name, "guard.py")
    spec = importlib.util.spec_from_file_location(f"{agent_name.replace('-', '_')}_guard", gpath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

writer_guard = _load_guard("academic-writer")
orchestrator_guard = _load_guard("academic-orchestrator")
trajectory_guard = _load_guard("trajectory-analyzer")


class TestDeliverableScopingGuard(unittest.TestCase):

    def _create_mock_docx(self, file_path, text_content, has_table=False, is_justified=False, has_br=False):
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        xml_parts = [
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
            '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">',
            '<w:body>'
        ]
        if has_table:
            xml_parts.append('<w:tbl><w:tr><w:tc><w:p><w:r><w:t>Table content</w:t></w:r></w:p></w:tc></w:tr></w:tbl>')

        p_pr = ""
        if is_justified:
            p_pr = '<w:pPr><w:jc w:val="both"/></w:pPr>'
        br_elem = '<w:br/>' if has_br else ''

        xml_parts.append(f'<w:p>{p_pr}<w:r><w:t>{text_content}</w:t>{br_elem}</w:r></w:p>')
        xml_parts.append('</w:body></w:document>')
        doc_xml = "".join(xml_parts).encode("utf-8")

        with zipfile.ZipFile(file_path, "w") as zf:
            zf.writestr("word/document.xml", doc_xml)

    def test_writer_stop_hook_skips_raw_inputs_arabic_glyphs(self):
        """Raw questionnaire in 01_raw_inputs/ with Arabic letters must NOT fail writer Stop hook."""
        with tempfile.TemporaryDirectory() as temp_ws:
            # 1. Raw input questionnaire in 01_raw_inputs containing Arabic letters (ي, ك)
            raw_path = os.path.join(temp_ws, "01_raw_inputs", "intolerance_of_uncertainty_scale_ius12.docx")
            arabic_questionnaire_text = "اين پرسشنامه داراي ۱۲ گويه مي‌باشد كه توسط فلان پژوهشگر تهيه شده است." * 10
            self._create_mock_docx(raw_path, arabic_questionnaire_text)

            # 2. Authentic Persian deliverable in 03_deliverables/
            deliv_path = os.path.join(temp_ws, "03_deliverables", "Chapter_4_Results.docx")
            clean_persian_text = "یافته‌های حاصل از برازش مدل ساختاری نشان داد که متغیرهای پیش‌بین دارای معناداری آماری هستند." * 10
            self._create_mock_docx(deliv_path, clean_persian_text)

            payload = {
                "workspacePaths": [temp_ws],
                "transcriptPath": ""
            }

            res = writer_guard.handle_stop(payload)
            self.assertEqual(
                res.get("decision"), "allow",
                f"Writer Stop hook failed unexpectedly on workspace containing 01_raw_inputs: {res.get('reason')}"
            )

    def test_writer_stop_hook_catches_arabic_glyphs_in_03_deliverables(self):
        """Arabic letters inside 03_deliverables must fail writer Stop hook."""
        with tempfile.TemporaryDirectory() as temp_ws:
            deliv_path = os.path.join(temp_ws, "03_deliverables", "Chapter_4_Results.docx")
            arabic_persian_text = "اين نتايج داراي معناداري آماري است كه بايد اصلاح شود." * 10
            self._create_mock_docx(deliv_path, arabic_persian_text)

            payload = {
                "workspacePaths": [temp_ws],
                "transcriptPath": ""
            }

            res = writer_guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Directive 5", res.get("reason", ""))
            self.assertIn("Arabic letter", res.get("reason", ""))

    def test_orchestrator_stop_hook_skips_raw_inputs_ch5_and_footnotes(self):
        """academic-orchestrator Stop hook must only audit 03_deliverables/ and skip 01_raw_inputs/."""
        with tempfile.TemporaryDirectory() as temp_ws:
            # Chapter 5 draft in 01_raw_inputs (e.g. client proposal input) with table
            raw_ch5 = os.path.join(temp_ws, "01_raw_inputs", "chapter_5_client_input.docx")
            self._create_mock_docx(raw_ch5, "Some proposal chapter 5 text" * 10, has_table=True)

            deliv_path = os.path.join(temp_ws, "03_deliverables", "Chapter_4_Results.docx")
            self._create_mock_docx(deliv_path, "Clean Chapter 4 text" * 10)

            # Create mock transcript
            with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
                tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "Completed chapter 5 review."}) + "\n")
                tpath = tf.name

            try:
                payload = {
                    "workspacePaths": [temp_ws],
                    "transcriptPath": tpath
                }
                res = orchestrator_guard.handle_stop(payload)
                self.assertEqual(res.get("decision"), "allow")
            finally:
                if os.path.exists(tpath):
                    os.unlink(tpath)

    def test_trajectory_analyzer_permissions(self):
        """trajectory-analyzer can write trajectories in .agents/learning/ but not production files."""
        # 1. Allowed: Trajectory in .agents/learning/experience/
        res_ok = trajectory_guard.handle_pre_tool_use({
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": "/path/to/.agents/learning/experience/TRJ-20260930-TEST.json",
                    "CodeContent": "{\"trajectory_id\": \"TRJ-1\"}"
                }
            }
        })
        self.assertEqual(res_ok.get("decision"), "allow")

        # 2. Denied: Production deliverable
        res_deliv = trajectory_guard.handle_pre_tool_use({
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": "/path/to/03_deliverables/Chapter_4.docx",
                    "CodeContent": "binary"
                }
            }
        })
        self.assertEqual(res_deliv.get("decision"), "deny")
        self.assertIn("production files", res_deliv.get("reason", ""))

        # 3. Denied: Raw inputs
        res_raw = trajectory_guard.handle_pre_tool_use({
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": "/path/to/01_raw_inputs/data.xlsx",
                    "CodeContent": "binary"
                }
            }
        })
        self.assertEqual(res_raw.get("decision"), "deny")

        # 4. Denied: Arbitrary root file
        res_root = trajectory_guard.handle_pre_tool_use({
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": "random_script.py",
                    "CodeContent": "print('hello')"
                }
            }
        })
        self.assertEqual(res_root.get("decision"), "deny")


if __name__ == "__main__":
    unittest.main()
