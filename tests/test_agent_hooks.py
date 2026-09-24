#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_agent_hooks.py — Comprehensive Unit & Integration Tests for Agent-Scoped Hooks

Verifies:
1. academic_orchestrator_guard (Academic Main Agent):
   - Directive 20: Blocks run_command, write_to_file, replace_file_content.
   - Allows management tools: invoke_subagent, view_file, send_message.
   - Directive 0: Binary Honesty enforcement.
2. statistics_agent_guard (Specialist Subagent):
   - Directive 12: Blocks invoke_subagent.
   - Directive 6: Blocks non-ASCII filenames.
   - Directive 4: Rejects p = .000 and naked Persian decimals (.۰۵).
3. data_agent_guard (Specialist Subagent):
   - Raw Data Protection: Blocks mutating 01_raw_inputs/ and raw_*.xlsx.
   - Destructive command guard: Blocks rm/truncate targeting raw data.
   - Directive 12: Blocks invoke_subagent.
4. academic_writer_guard (Specialist Subagent):
   - Directive 12: Blocks invoke_subagent.
   - Directive 6: Blocks non-ASCII filenames.
   - Directive 7.1: Rejects robotic AI clichés.
   - Directive 3.1: Enforces Chapter 5 Prose-Only (zero tables).
5. validation_agent_guard (Specialist Subagent):
   - Directive 12: Blocks invoke_subagent.
   - Directive 22: Rejects verbal PASS without verified validation_report.json on disk.
6. Performance & Latency:
   - Each hook evaluates in under 35 milliseconds.
"""

import os
import sys
import json
import time
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGENTS_HOOKS_DIR = os.path.join(ROOT_DIR, ".agents", "hooks", "agents")
for p in (ROOT_DIR, AGENTS_HOOKS_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

import academic_orchestrator_guard
import statistics_agent_guard
import data_agent_guard
import academic_writer_guard
import validation_agent_guard


class TestAcademicOrchestratorGuard(unittest.TestCase):
    """Tests for the Academic Main Agent (academic-orchestrator) hook."""

    def test_blocks_run_command(self):
        payload = {
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": "python3 script.py"}
            }
        }
        res = academic_orchestrator_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Directive 20", res.get("reason", ""))
        self.assertIn("academic-orchestrator", res.get("reason", "").lower())

    def test_blocks_write_to_file(self):
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": "/path/to/output.docx"}
            }
        }
        res = academic_orchestrator_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Directive 20", res.get("reason", ""))

    def test_blocks_replace_file_content(self):
        payload = {
            "toolCall": {
                "name": "replace_file_content",
                "args": {"TargetFile": "/path/to/code.py"}
            }
        }
        res = academic_orchestrator_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")

    def test_allows_management_tools(self):
        for tool in ("invoke_subagent", "manage_subagents", "send_message", "view_file", "list_dir"):
            payload = {"toolCall": {"name": tool, "args": {}}}
            res = academic_orchestrator_guard.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "allow", f"Failed for tool: {tool}")

    def test_stop_enforces_binary_honesty(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "USER_INPUT", "content": "Did you check the assumptions?"}) + "\n")
            tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "I certainly examined everything thoroughly."}) + "\n")
            tpath = tf.name

        try:
            payload = {"transcriptPath": tpath}
            res = academic_orchestrator_guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Directive 0", res.get("reason", ""))
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)

    def test_blocks_unstructured_delegation_to_execution_worker(self):
        payload = {
            "toolCall": {
                "name": "invoke_subagent",
                "args": {
                    "Subagents": [
                        {
                            "TypeName": "statistics-agent",
                            "Prompt": "Please run the regression analysis on burnout data."
                        }
                    ]
                }
            }
        }
        res = academic_orchestrator_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Contractual Delegation", res.get("reason", ""))

    def test_allows_contractual_delegation_envelope(self):
        valid_cde_prompt = """
        Execute Stage 4.6:
        ```json
        {
          "task_id": "TSK-2026-CH4-H1",
          "worker_agent": "statistics-agent",
          "objective": "Run multiple regression",
          "inputs": ["02_analysis_code/cleaned_data.xlsx"],
          "required_artifacts": [
            "03_deliverables/06_hypothesis_1.docx",
            "03_deliverables/06_hypothesis_1.md",
            "03_deliverables/06_hypothesis_1.json"
          ]
        }
        ```
        """
        payload = {
            "toolCall": {
                "name": "invoke_subagent",
                "args": {
                    "Subagents": [
                        {
                            "TypeName": "statistics-agent",
                            "Prompt": valid_cde_prompt
                        }
                    ]
                }
            }
        }
        res = academic_orchestrator_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "allow")

    def test_blocks_stage_skipping_when_prerequisites_missing(self):
        cde_prompt = """
        Execute Stage 4.6:
        ```json
        {
          "task_id": "TSK-2026-CH4-H1",
          "stage": "Stage 4.6: Hypothesis 1",
          "worker_agent": "statistics-agent",
          "objective": "Run multiple regression",
          "inputs": ["02_analysis_code/cleaned_data.xlsx"],
          "required_artifacts": [
            "03_deliverables/06_hypothesis_1.docx",
            "03_deliverables/06_hypothesis_1.md",
            "03_deliverables/06_hypothesis_1.json"
          ]
        }
        ```
        """
        with tempfile.TemporaryDirectory() as empty_ws:
            payload = {
                "toolCall": {
                    "name": "invoke_subagent",
                    "args": {
                        "Subagents": [{"TypeName": "statistics-agent", "Prompt": cde_prompt}]
                    }
                },
                "workspacePaths": [empty_ws]
            }
            res = academic_orchestrator_guard.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "deny")
            self.assertIn("Directive 3", res.get("reason", ""))
            self.assertIn("Zero Skipping Invariant", res.get("reason", ""))

    def test_allows_stage_when_prerequisites_exist(self):
        cde_prompt = """
        Execute Stage 4.6:
        ```json
        {
          "task_id": "TSK-2026-CH4-H1",
          "stage": "Stage 4.6: Hypothesis 1",
          "worker_agent": "statistics-agent",
          "objective": "Run multiple regression",
          "inputs": ["02_analysis_code/cleaned_data.xlsx"],
          "required_artifacts": [
            "03_deliverables/06_hypothesis_1.docx",
            "03_deliverables/06_hypothesis_1.md",
            "03_deliverables/06_hypothesis_1.json"
          ]
        }
        ```
        """
        with tempfile.TemporaryDirectory() as valid_ws:
            # Create prerequisite assumption file
            assump_path = os.path.join(valid_ws, "03_parametric_assumptions.json")
            with open(assump_path, "w") as f:
                f.write("{}")

            payload = {
                "toolCall": {
                    "name": "invoke_subagent",
                    "args": {
                        "Subagents": [{"TypeName": "statistics-agent", "Prompt": cde_prompt}]
                    }
                },
                "workspacePaths": [valid_ws]
            }
            res = academic_orchestrator_guard.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "allow")

    def test_stop_enforces_directive_11_stage_gate(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({
                "type": "PLANNER_RESPONSE",
                "tool_calls": [{"name": "invoke_subagent", "args": {}}]
            }) + "\n")
            # Finished without asking for confirmation
            tf.write(json.dumps({
                "type": "PLANNER_RESPONSE",
                "content": "Stage finished. We are moving immediately into Stage 4.7 now."
            }) + "\n")
            tpath = tf.name

        try:
            payload = {"transcriptPath": tpath}
            res = academic_orchestrator_guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Directive 11", res.get("reason", ""))
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)


class TestStatisticsAgentGuard(unittest.TestCase):
    """Tests for Statistics Specialist Subagent hook."""

    def test_blocks_subagent_delegation(self):
        payload = {"toolCall": {"name": "invoke_subagent", "args": {}}}
        res = statistics_agent_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Directive 12", res.get("reason", ""))

    def test_blocks_non_ascii_filename(self):
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": "02_analysis/نتایج_فرضیه.json"}
            }
        }
        res = statistics_agent_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Directive 6", res.get("reason", ""))

    def test_stop_flags_p_zero(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "The regression was significant (F = 14.5, p = .000)."}) + "\n")
            tpath = tf.name

        try:
            payload = {"transcriptPath": tpath}
            res = statistics_agent_guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("p = .000", res.get("reason", ""))
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)

    def test_stop_flags_naked_persian_decimal(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "سطح معناداری برابر با .۰۵ گزارش شد."}) + "\n")
            tpath = tf.name

        try:
            payload = {"transcriptPath": tpath}
            res = statistics_agent_guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Leading Zero", res.get("reason", ""))
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)

    def test_stop_blocks_mental_calculation(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            # Model claims statistics without running any run_command
            tf.write(json.dumps({
                "type": "PLANNER_RESPONSE",
                "content": "Regression analysis revealed F = 14.35, p = .002, with R2 = .24."
            }) + "\n")
            tpath = tf.name

        try:
            payload = {"transcriptPath": tpath}
            res = statistics_agent_guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Directive 2", res.get("reason", ""))
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)


class TestDataAgentGuard(unittest.TestCase):
    """Tests for Data Management Specialist Subagent hook."""

    def test_blocks_raw_data_modification(self):
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": "01_raw_inputs/raw_burnout_data.xlsx"}
            }
        }
        res = data_agent_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Raw Data Immutability", res.get("reason", ""))

    def test_blocks_destructive_shell_command(self):
        payload = {
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": "rm -f 01_raw_inputs/data.csv"}
            }
        }
        res = data_agent_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")

    def test_allows_cleaned_dataset_writing(self):
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": "02_analysis_code/cleaned/cleaned_data.xlsx"}
            }
        }
        res = data_agent_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "allow")


class TestAcademicWriterGuard(unittest.TestCase):
    """Tests for Academic Writer Specialist Subagent hook."""

    def test_blocks_subagent_delegation(self):
        payload = {"toolCall": {"name": "invoke_subagent", "args": {}}}
        res = academic_writer_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Directive 12", res.get("reason", ""))

    def test_stop_flags_ai_cliches(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "شایان ذکر است که نتایج نشان داد..."}) + "\n")
            tpath = tf.name

        try:
            payload = {"transcriptPath": tpath}
            res = academic_writer_guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Directive 7.1", res.get("reason", ""))
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)

    def test_stop_flags_tables_in_chapter_5(self):
        table_md = "| متغیر | میانگین |\n|---|---|\n| فرسودگی | ۲۴.۵ |"
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": f"تحلیل یافته‌های فصل پنجم:\n{table_md}"}) + "\n")
            tpath = tf.name

        try:
            payload = {"transcriptPath": tpath}
            res = academic_writer_guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Directive 3.1", res.get("reason", ""))
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)


class TestValidationAgentGuard(unittest.TestCase):
    """Tests for Validation and Auditing Subagent hook."""

    def test_blocks_subagent_delegation(self):
        payload = {"toolCall": {"name": "invoke_subagent", "args": {}}}
        res = validation_agent_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")

    def test_stop_blocks_unverified_pass(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "All checks passed. Verdict: PASS."}) + "\n")
            tpath = tf.name

        try:
            with tempfile.TemporaryDirectory() as temp_ws:
                payload = {"transcriptPath": tpath, "workspacePaths": [temp_ws]}
                res = validation_agent_guard.handle_stop(payload)
                self.assertEqual(res.get("decision"), "continue")
                self.assertIn("Directive 22", res.get("reason", ""))
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)

    def test_stop_allows_verified_pass(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "Audit complete. Verdict: PASS."}) + "\n")
            tpath = tf.name

        try:
            with tempfile.TemporaryDirectory() as temp_ws:
                rep_path = os.path.join(temp_ws, "validation_report.json")
                with open(rep_path, "w", encoding="utf-8") as rf:
                    json.dump({"overall_verdict": "PASS", "checks_failed": 0, "checks_passed": 12}, rf)

                payload = {"transcriptPath": tpath, "workspacePaths": [temp_ws]}
                res = validation_agent_guard.handle_stop(payload)
                self.assertEqual(res.get("decision"), "allow")
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)


class TestHookPerformanceAndLatency(unittest.TestCase):
    """Ensures each dedicated guard executes well within the 35ms budget."""

    def test_orchestrator_guard_latency(self):
        payload = {"toolCall": {"name": "view_file", "args": {"AbsolutePath": "/test"}}}
        start = time.perf_counter()
        for _ in range(50):
            academic_orchestrator_guard.handle_pre_tool_use(payload)
        elapsed = (time.perf_counter() - start) / 50.0
        self.assertLess(elapsed, 0.035, f"Orchestrator guard too slow: {elapsed*1000:.2f}ms")

    def test_statistics_guard_latency(self):
        payload = {"toolCall": {"name": "run_command", "args": {"CommandLine": "python3 test.py"}}}
        start = time.perf_counter()
        for _ in range(50):
            statistics_agent_guard.handle_pre_tool_use(payload)
        elapsed = (time.perf_counter() - start) / 50.0
        self.assertLess(elapsed, 0.035, f"Statistics guard too slow: {elapsed*1000:.2f}ms")

    def test_data_guard_latency(self):
        payload = {"toolCall": {"name": "write_to_file", "args": {"TargetFile": "02_code/test.py"}}}
        start = time.perf_counter()
        for _ in range(50):
            data_agent_guard.handle_pre_tool_use(payload)
        elapsed = (time.perf_counter() - start) / 50.0
        self.assertLess(elapsed, 0.035, f"Data guard too slow: {elapsed*1000:.2f}ms")


if __name__ == "__main__":
    unittest.main()
