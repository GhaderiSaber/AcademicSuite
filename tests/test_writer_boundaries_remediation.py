#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_writer_boundaries_remediation.py

Unit tests verifying the remediation of academic-writer boundaries:
1. Directive 6 Scoped ASCII Filename Guard (academic-writer, statistics-agent, data-agent)
2. Virtualenv auto-discovery and CLI help execution in academic_docgen.py
3. Execution guard refinements in safety_hooks.py (ls, find, --help, uv run python, doc-builders)
4. OpenXML deliverable verification for Stage 4.2 (02_descriptives.docx)
"""

import os
import sys
import json
import zipfile
import subprocess
import unittest
import xml.etree.ElementTree as ET

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for p in (ROOT_DIR, os.path.join(ROOT_DIR, ".agents", "hooks"), os.path.join(ROOT_DIR, ".agents")):
    if p not in sys.path:
        sys.path.insert(0, p)

from safety_hooks import SafetyHooks

# Import specialist guards
import importlib.util

def load_guard_module(agent_name: str):
    guard_path = os.path.join(ROOT_DIR, ".agents", "agents", agent_name, "guard.py")
    spec = importlib.util.spec_from_file_location(f"{agent_name}_guard", guard_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

writer_guard = load_guard_module("academic-writer")
stats_guard = load_guard_module("statistics-agent")
data_guard = load_guard_module("data-agent")


class TestWriterBoundariesRemediation(unittest.TestCase):
    """Verifies that all 4 boundaries are remediated without relaxing safety invariants."""

    def setUp(self):
        self.workspace = os.path.join(ROOT_DIR, "scratch")
        os.makedirs(self.workspace, exist_ok=True)

    # -------------------------------------------------------------
    # 1. Scoped ASCII Filename Guard Tests
    # -------------------------------------------------------------
    def test_01_writer_guard_allows_persian_code_content(self):
        """Writing code containing Persian text and .docx mentions must not trigger ASCII filename violation."""
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": os.path.join(self.workspace, "build_report.py"),
                    "CodeContent": "# Script for 02_descriptives.docx\n# مؤلفه ملامت خویش و نشخوار فکری\nprint('done')",
                    "Description": "Build report"
                }
            },
            "workspacePaths": [ROOT_DIR]
        }
        res = writer_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "allow", f"Failed: {res.get('reason')}")

    def test_02_writer_guard_allows_persian_message_with_docx(self):
        """Sending messages containing Persian text and .docx mentions must not trigger ASCII filename violation."""
        payload = {
            "toolCall": {
                "name": "send_message",
                "args": {
                    "Recipient": "test-orchestrator",
                    "Message": "گزارش نهایی در فایل 02_descriptives.docx آماده شد. مؤلفه‌های نشخوار فکری بررسی گردید."
                }
            },
            "workspacePaths": [ROOT_DIR]
        }
        res = writer_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "allow", f"Failed: {res.get('reason')}")

    def test_03_writer_guard_blocks_persian_targetfile(self):
        """TargetFile with non-ASCII filename must strictly be denied."""
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": os.path.join(self.workspace, "گزارش_تحلیل.docx"),
                    "CodeContent": "dummy",
                    "Description": "Invalid non-ascii filename"
                }
            },
            "workspacePaths": [ROOT_DIR]
        }
        res = writer_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Directive 6", res.get("reason", ""))

    def test_04_writer_guard_run_command_scoped_check(self):
        """run_command with Persian parameters but ASCII deliverable must be allowed; Persian deliverable denied."""
        # Allowed: Persian parameter, ASCII output filename
        allowed_payload = {
            "toolCall": {
                "name": "run_command",
                "args": {
                    "CommandLine": "python3 .agents/scripts/academic_docgen.py render-docx --title 'تحلیل توصیفی' --docx 02_descriptives.docx"
                }
            },
            "workspacePaths": [ROOT_DIR]
        }
        res = writer_guard.handle_pre_tool_use(allowed_payload)
        self.assertEqual(res.get("decision"), "allow", f"Failed: {res.get('reason')}")

        # Denied: Non-ASCII deliverable filename
        denied_payload = {
            "toolCall": {
                "name": "run_command",
                "args": {
                    "CommandLine": "python3 .agents/scripts/academic_docgen.py render-docx --docx توصیفی.docx"
                }
            },
            "workspacePaths": [ROOT_DIR]
        }
        res_denied = writer_guard.handle_pre_tool_use(denied_payload)
        self.assertEqual(res_denied.get("decision"), "deny")
        self.assertIn("Directive 6", res_denied.get("reason", ""))

    def test_05_stats_and_data_agent_scoped_check(self):
        """statistics-agent and data-agent must check only file paths and allow Persian payloads."""
        # Stats agent allows Persian message containing .json
        payload_stats = {
            "toolCall": {
                "name": "send_message",
                "args": {
                    "Recipient": "orchestrator",
                    "Message": "نتایج در فایل stats_results.json ذخیره شد. میانگین احساس کنترل ۴۹.۴۵ است."
                }
            },
            "workspacePaths": [ROOT_DIR]
        }
        res_stats = stats_guard.handle_pre_tool_use(payload_stats)
        self.assertEqual(res_stats.get("decision"), "allow", f"Stats guard failed: {res_stats.get('reason')}")

        # Data agent allows Persian message containing .csv
        payload_data = {
            "toolCall": {
                "name": "send_message",
                "args": {
                    "Recipient": "orchestrator",
                    "Message": "داده‌های تمیزشده در data_cleaned.csv ذخیره شد."
                }
            },
            "workspacePaths": [ROOT_DIR]
        }
        res_data = data_guard.handle_pre_tool_use(payload_data)
        self.assertEqual(res_data.get("decision"), "allow", f"Data guard failed: {res_data.get('reason')}")

    # -------------------------------------------------------------
    # 2. Virtualenv Discovery & Docgen CLI Tests
    # -------------------------------------------------------------
    def test_06_docgen_cli_help(self):
        """academic_docgen.py --help must execute cleanly with code 0 under system python."""
        cmd = [sys.executable, os.path.join(ROOT_DIR, ".agents", "scripts", "academic_docgen.py"), "--help"]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("Dedicated Sealed Academic Document Generation CLI", proc.stdout)

    def test_07_docgen_subcommand_help(self):
        """academic_docgen.py inspect-docx --help must execute cleanly with code 0."""
        cmd = [sys.executable, os.path.join(ROOT_DIR, ".agents", "scripts", "academic_docgen.py"), "inspect-docx", "--help"]
        proc = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("--docx", proc.stdout)

    # -------------------------------------------------------------
    # 3. SafetyHooks Academic Writer Refinements
    # -------------------------------------------------------------
    def _check_cmd(self, cmd: str, caller: str = "academic-writer"):
        payload = {
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": cmd}
            },
            "agentName": caller,
            "workspacePaths": [ROOT_DIR]
        }
        return SafetyHooks.handle_pre_tool_use(payload)

    def test_08_safety_hooks_allows_docgen_help(self):
        """SafetyHooks must permit academic_docgen.py --help for academic-writer."""
        cmd = "python3 .agents/scripts/academic_docgen.py --help"
        res = self._check_cmd(cmd)
        self.assertEqual(res.get("decision"), "allow", f"Failed: {res.get('reason')}")

    def test_09_safety_hooks_allows_safe_inspection_commands(self):
        """SafetyHooks must permit ls, dir, and find for academic-writer."""
        for cmd in ("ls -la 03_deliverables", "find 03_deliverables -name '*.docx'", "dir 03_deliverables"):
            res = self._check_cmd(cmd)
            self.assertEqual(res.get("decision"), "allow", f"Failed for '{cmd}': {res.get('reason')}")

    def test_10_safety_hooks_allows_uv_run_python(self):
        """SafetyHooks must support uv run python for document generation."""
        cmd = "uv run python .agents/scripts/academic_docgen.py render-docx --docx out.docx"
        res = self._check_cmd(cmd)
        self.assertEqual(res.get("decision"), "allow", f"Failed: {res.get('reason')}")

    def test_11_safety_hooks_allows_doc_builder_scripts(self):
        """Scripts with document builder prefixes/suffixes must not be blocked as statistical calculations."""
        cmd = "python3 02_analysis_code/generate_descriptives_docx.py"
        res = self._check_cmd(cmd)
        self.assertEqual(res.get("decision"), "allow", f"Failed: {res.get('reason')}")

    def test_12_safety_hooks_blocks_statistical_skills_for_writer(self):
        """Writer must still be blocked from executing scripts in statistical skills (Directive 12)."""
        cmd = "python3 .agents/skills/descriptive-statistics/scripts/descriptive_statistics.py"
        res = self._check_cmd(cmd)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Academic Writer Execution Guard", res.get("reason", ""))

    # -------------------------------------------------------------
    # 4. Deliverable OpenXML Verification (Stage 4.2)
    # -------------------------------------------------------------
    def test_13_stage_4_2_deliverable_is_genuine_openxml(self):
        """02_descriptives.docx in Mohtasham Valiyanpur project must be a genuine, valid OpenXML document."""
        docx_path = "/home/saber-ghaderi/My Work/Mohtasham Valiyanpur/03_deliverables/02_descriptives.docx"
        if not os.path.exists(docx_path):
            self.skipTest("Mohtasham Valiyanpur deliverable path not found.")

        # Check zip integrity and document.xml presence
        self.assertTrue(zipfile.is_zipfile(docx_path), "Deliverable is not a valid zip archive.")
        with zipfile.ZipFile(docx_path, "r") as zf:
            self.assertIn("word/document.xml", zf.namelist(), "Missing word/document.xml in docx.")
            xml_bytes = zf.read("word/document.xml")
            root = ET.fromstring(xml_bytes)

            paragraphs = [p for p in root.iter() if p.tag.endswith("}p") or p.tag == "p"]
            tables = [t for t in root.iter() if t.tag.endswith("}tbl") or t.tag == "tbl"]

            self.assertGreater(len(paragraphs), 10, "Paragraph count too low.")
            self.assertGreaterEqual(len(tables), 1, "Missing APA 7 table.")

            # Check table bidiVisual for RTL compliance (Directive 5)
            tbl = tables[0]
            bidi_visual = any(elem.tag.endswith("}bidiVisual") or elem.tag == "bidiVisual" for elem in tbl.iter())
            self.assertTrue(bidi_visual, "Table missing <w:bidiVisual/> tag.")


if __name__ == "__main__":
    unittest.main()
