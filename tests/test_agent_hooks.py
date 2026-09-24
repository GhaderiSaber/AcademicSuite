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
import auditor_agents_guard
import project_organizer_guard
import psychometric_expert_guard
import research_literature_guard
import domain_specialists_guard
import advisory_agents_guard


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

    def test_blocks_simulation_pipeline_stage_skipping(self):
        cde_prompt = """
        Execute Stage DS.3:
        ```json
        {
          "task_id": "TSK-2026-SIM-001",
          "stage": "Stage DS.3: Monte Carlo Simulation",
          "worker_agent": "data-agent",
          "objective": "Run Monte Carlo psychometric simulation",
          "inputs": ["02_scales_codebook.json"],
          "required_artifacts": ["primary_data.xlsx", "final_data.xlsx"]
        }
        ```
        """
        with tempfile.TemporaryDirectory() as empty_ws:
            payload = {
                "toolCall": {
                    "name": "invoke_subagent",
                    "args": {"Subagents": [{"TypeName": "data-agent", "Prompt": cde_prompt}]}
                },
                "workspacePaths": [empty_ws]
            }
            res = academic_orchestrator_guard.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "deny")
            self.assertIn("Directive 3", res.get("reason", ""))

        with tempfile.TemporaryDirectory() as valid_ws:
            with open(os.path.join(valid_ws, "02_scales_codebook.json"), "w") as f:
                f.write("{}")
            payload = {
                "toolCall": {
                    "name": "invoke_subagent",
                    "args": {"Subagents": [{"TypeName": "data-agent", "Prompt": cde_prompt}]}
                },
                "workspacePaths": [valid_ws]
            }
            res = academic_orchestrator_guard.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "allow")

    def test_blocks_computational_statistics_to_academic_writer(self):
        cde_prompt = """
        Execute Stage 4.6:
        ```json
        {
          "task_id": "TSK-2026-CH4-H1",
          "worker_agent": "academic-writer",
          "objective": "Run multiple regression modeling",
          "target_script": "python3 .agents/skills/regression/scripts/run_regression.py --data cleaned.xlsx",
          "inputs": ["cleaned.xlsx"],
          "required_artifacts": ["06_hypothesis_1.docx"]
        }
        ```
        """
        payload = {
            "toolCall": {
                "name": "invoke_subagent",
                "args": {
                    "Subagents": [{"TypeName": "academic-writer", "Prompt": cde_prompt}]
                }
            }
        }
        res = academic_orchestrator_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("CAPABILITY MISROUTING", res.get("reason", ""))
        self.assertIn("statistics-agent", res.get("reason", ""))

    def test_blocks_data_simulation_to_statistics_agent(self):
        cde_prompt = """
        Execute Stage DS.3:
        ```json
        {
          "task_id": "TSK-2026-SIM-001",
          "worker_agent": "statistics-agent",
          "objective": "Run Monte Carlo psychometric simulation",
          "target_script": "python3 .agents/skills/psychometric-data-simulator/scripts/simulate_psychometric_data.py",
          "inputs": ["02_scales_codebook.json"],
          "required_artifacts": ["primary_data.xlsx"]
        }
        ```
        """
        payload = {
            "toolCall": {
                "name": "invoke_subagent",
                "args": {
                    "Subagents": [{"TypeName": "statistics-agent", "Prompt": cde_prompt}]
                }
            }
        }
        res = academic_orchestrator_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("CAPABILITY MISROUTING", res.get("reason", ""))
        self.assertIn("data-agent", res.get("reason", ""))

    def test_blocks_thesis_assembly_to_statistics_agent(self):
        cde_prompt = """
        Execute Final Assembly:
        ```json
        {
          "task_id": "TSK-2026-ASM-001",
          "worker_agent": "statistics-agent",
          "objective": "Assemble master thesis via persian-thesis-builder",
          "inputs": ["Chapter_1.docx", "Chapter_2.docx"],
          "required_artifacts": ["Thesis_Compiled.docx"]
        }
        ```
        """
        payload = {
            "toolCall": {
                "name": "invoke_subagent",
                "args": {
                    "Subagents": [{"TypeName": "statistics-agent", "Prompt": cde_prompt}]
                }
            }
        }
        res = academic_orchestrator_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("CAPABILITY MISROUTING", res.get("reason", ""))
        self.assertIn("academic-writer", res.get("reason", ""))

    def test_blocks_adversarial_validation_to_authoring_agent(self):
        cde_prompt = """
        Execute Stage 4.9:
        ```json
        {
          "task_id": "TSK-2026-QC-001",
          "worker_agent": "academic-writer",
          "objective": "Run verify_thesis_integrity.py and produce validation_report.json",
          "inputs": ["Chapter_4.docx"],
          "required_artifacts": ["validation_report.json"]
        }
        ```
        """
        payload = {
            "toolCall": {
                "name": "invoke_subagent",
                "args": {
                    "Subagents": [{"TypeName": "academic-writer", "Prompt": cde_prompt}]
                }
            }
        }
        res = academic_orchestrator_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("CAPABILITY MISROUTING", res.get("reason", ""))
        self.assertIn("validation-agent", res.get("reason", ""))

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

    def test_stop_blocks_flattery_sycophancy(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({
                "type": "PLANNER_RESPONSE",
                "content": "Great question! We will now proceed with the statistical verification."
            }) + "\n")
            tpath = tf.name

        try:
            payload = {"transcriptPath": tpath}
            res = academic_orchestrator_guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Directive 13", res.get("reason", ""))
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)

    def test_stop_blocks_missing_triad_disk_artifacts(self):
        cde = {
            "task_id": "STAGE_4_1",
            "worker_agent": "statistics-agent",
            "inputs": ["02_analysis/clean_data.xlsx"],
            "required_artifacts": ["stage4_1_summary.docx", "stage4_1_results.md", "stage4_1_stats.json"],
            "objective": "Run descriptive statistics"
        }
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({
                "type": "PLANNER_RESPONSE",
                "tool_calls": [{
                    "name": "invoke_subagent",
                    "args": {
                        "Subagents": [{
                            "TypeName": "statistics-agent",
                            "Prompt": f"Please execute task:\n```json\n{json.dumps(cde)}\n```"
                        }]
                    }
                }]
            }) + "\n")
            tf.write(json.dumps({
                "type": "PLANNER_RESPONSE",
                "content": "Stage 4.1 completed. What was done: calculated descriptives. What will be done next: assumptions. Please confirm."
            }) + "\n")
            tpath = tf.name

        try:
            with tempfile.TemporaryDirectory() as temp_ws:
                payload = {"transcriptPath": tpath, "workspacePaths": [temp_ws]}
                res = academic_orchestrator_guard.handle_stop(payload)
                self.assertEqual(res.get("decision"), "continue")
                self.assertIn("Directive 3", res.get("reason", ""))
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)

    def test_stop_enforces_strict_english_dialogue(self):
        persian_speech = "مرحله قبلی با موفقیت به پایان رسید و اکنون باید داده‌ها را تحلیل کنیم تا به نتایج دقیق دست یابیم."
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({
                "type": "PLANNER_RESPONSE",
                "content": f"Status: {persian_speech}"
            }) + "\n")
            tpath = tf.name

        try:
            payload = {"transcriptPath": tpath}
            res = academic_orchestrator_guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Directive 6", res.get("reason", ""))
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)

    def test_stop_enforces_temporal_reality_anchor(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({
                "type": "PLANNER_RESPONSE",
                "content": "Since we are currently in 2024, the literature review covers up to 2023."
            }) + "\n")
            tpath = tf.name

        try:
            payload = {"transcriptPath": tpath}
            res = academic_orchestrator_guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Directive 15", res.get("reason", ""))
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)

    def test_stop_enforces_orchestrator_chapter_5_table_ban(self):
        import zipfile
        with tempfile.TemporaryDirectory() as temp_ws:
            docx_path = os.path.join(temp_ws, "Chapter_5_Discussion.docx")
            xml_content = (
                b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                b'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                b'<w:body><w:p><w:r><w:t>Prose</w:t></w:r></w:p>'
                b'<w:tbl><w:tr><w:tc><w:p><w:r><w:t>Cell</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'
                b'</w:body></w:document>'
            )
            with zipfile.ZipFile(docx_path, "w") as zf:
                zf.writestr("word/document.xml", xml_content)

            with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
                tf.write(json.dumps({
                    "type": "PLANNER_RESPONSE",
                    "tool_calls": [{"name": "invoke_subagent", "args": {}}]
                }) + "\n")
                tf.write(json.dumps({
                    "type": "PLANNER_RESPONSE",
                    "content": "Stage Chapter 5 completed. What was done: drafted discussion. What will be done next: conclusion. Please confirm."
                }) + "\n")
                tpath = tf.name

            try:
                payload = {"transcriptPath": tpath, "workspacePaths": [temp_ws]}
                res = academic_orchestrator_guard.handle_stop(payload)
                self.assertEqual(res.get("decision"), "continue")
                self.assertIn("Directive 3.1", res.get("reason", ""))
            finally:
                if os.path.exists(tpath):
                    os.unlink(tpath)

    def test_stop_verifies_native_openxml_footnotes(self):
        import zipfile
        with tempfile.TemporaryDirectory() as temp_ws:
            docx_path = os.path.join(temp_ws, "Chapter_2_LitReview.docx")
            xml_content = (
                b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                b'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                b'<w:body><w:p><w:r><w:t>Some text</w:t><w:footnoteReference w:id="2"/></w:r></w:p>'
                b'</w:body></w:document>'
            )
            with zipfile.ZipFile(docx_path, "w") as zf:
                zf.writestr("word/document.xml", xml_content)

            with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
                tf.write(json.dumps({
                    "type": "PLANNER_RESPONSE",
                    "tool_calls": [{"name": "invoke_subagent", "args": {}}]
                }) + "\n")
                tf.write(json.dumps({
                    "type": "PLANNER_RESPONSE",
                    "content": "Stage 2.1 completed. What was done: drafted review. What will be done next: synthesis. Please confirm."
                }) + "\n")
                tpath = tf.name

            try:
                payload = {"transcriptPath": tpath, "workspacePaths": [temp_ws]}
                res = academic_orchestrator_guard.handle_stop(payload)
                self.assertEqual(res.get("decision"), "continue")
                self.assertIn("Directive 5", res.get("reason", ""))
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

    def test_blocks_root_script_target_in_statistics_agent(self):
        with tempfile.TemporaryDirectory() as temp_ws:
            payload = {
                "toolCall": {
                    "name": "write_to_file",
                    "args": {"TargetFile": os.path.join(temp_ws, "run_anova.py")}
                },
                "workspacePaths": [temp_ws]
            }
            res = statistics_agent_guard.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "deny")
            self.assertIn("Directive 23", res.get("reason", ""))

    def test_blocks_cli_script_without_view_file(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({
                "type": "PLANNER_RESPONSE",
                "tool_calls": [{"name": "some_other_tool", "args": {}}]
            }) + "\n")
            tpath = tf.name

        try:
            payload = {
                "toolCall": {
                    "name": "run_command",
                    "args": {"CommandLine": "python3 .agents/skills/descriptive-statistics/scripts/descriptive_statistics.py"}
                },
                "transcriptPath": tpath
            }
            res = statistics_agent_guard.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "deny")
            self.assertIn("Directive 1", res.get("reason", ""))
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)

    def test_allows_cli_script_after_view_file(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({
                "type": "PLANNER_RESPONSE",
                "tool_calls": [{
                    "name": "view_file",
                    "args": {"AbsolutePath": "/workspace/.agents/skills/descriptive-statistics/SKILL.md"}
                }]
            }) + "\n")
            tpath = tf.name

        try:
            payload = {
                "toolCall": {
                    "name": "run_command",
                    "args": {"CommandLine": "python3 .agents/skills/descriptive-statistics/scripts/descriptive_statistics.py"}
                },
                "transcriptPath": tpath
            }
            res = statistics_agent_guard.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "allow")
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)

    def test_blocks_regex_on_openxml_commands(self):
        payload = {
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": "python3 -c \"import re; re.sub(r'<w:r>', '', open('word/document.xml').read())\""}
            }
        }
        res = statistics_agent_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Directive 5", res.get("reason", ""))

    def test_stop_blocks_sem_heywood_cases(self):
        with tempfile.TemporaryDirectory() as temp_ws:
            stats_json_path = os.path.join(temp_ws, "sem_fit_results.json")
            with open(stats_json_path, "w", encoding="utf-8") as jf:
                json.dump({"has_heywood_case": True, "converged": True}, jf)

            with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
                tf.write(json.dumps({
                    "type": "PLANNER_RESPONSE",
                    "content": "SEM analysis was conducted using lavaan."
                }) + "\n")
                tpath = tf.name

            try:
                payload = {"transcriptPath": tpath, "workspacePaths": [temp_ws]}
                res = statistics_agent_guard.handle_stop(payload)
                self.assertEqual(res.get("decision"), "continue")
                self.assertIn("Mathematical Admissibility Gate", res.get("reason", ""))
            finally:
                if os.path.exists(tpath):
                    os.unlink(tpath)

    def test_stop_enforces_three_table_regression_standard_in_stats(self):
        content = "نتایج تحلیل رگرسیون برای فرضیه ۱:\n| متغیر | بتا | p |\n|---|---|---|\n| استرس | ۰.۴۵ | ۰.۰۱ |"
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({
                "type": "PLANNER_RESPONSE",
                "content": content
            }) + "\n")
            tpath = tf.name

        try:
            payload = {"transcriptPath": tpath}
            res = statistics_agent_guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("3-Table Regression Standard", res.get("reason", ""))
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

    def test_stop_blocks_synthetic_whole_integer_means(self):
        import pandas as pd
        with tempfile.TemporaryDirectory() as temp_ws:
            sim_path = os.path.join(temp_ws, "simulated_burnout_dataset.xlsx")
            df = pd.DataFrame({
                "burnout": [10, 20, 30],
                "stress": [20, 30, 40]
            })
            df.to_excel(sim_path, index=False)

            payload = {"workspacePaths": [temp_ws]}
            res = data_agent_guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Directive 9", res.get("reason", ""))


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

    def test_blocks_deliverables_script_target_in_writer(self):
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {"TargetFile": "03_deliverables/generate_chapter.py"}
            }
        }
        res = academic_writer_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Directive 23", res.get("reason", ""))

    def test_blocks_emojis_in_writer_deliverables(self):
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": "03_deliverables/Chapter_4.docx",
                    "CodeContent": "فصل چهارم: یافته‌های پژوهش 📊"
                }
            }
        }
        res = academic_writer_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Directive 4.1", res.get("reason", ""))

    def test_blocks_chapter_5_docx_with_tables(self):
        import zipfile
        with tempfile.TemporaryDirectory() as temp_ws:
            docx_path = os.path.join(temp_ws, "Chapter_5_Discussion.docx")
            xml_content = (
                b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                b'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                b'<w:body><w:p><w:r><w:t>Prose text</w:t></w:r></w:p>'
                b'<w:tbl><w:tr><w:tc><w:p><w:r><w:t>Cell</w:t></w:r></w:p></w:tc></w:tr></w:tbl>'
                b'</w:body></w:document>'
            )
            with zipfile.ZipFile(docx_path, "w") as zf:
                zf.writestr("word/document.xml", xml_content)

            with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
                tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "Completed chapter 5 drafting."}) + "\n")
                tpath = tf.name

            try:
                payload = {"transcriptPath": tpath, "workspacePaths": [temp_ws]}
                res = academic_writer_guard.handle_stop(payload)
                self.assertEqual(res.get("decision"), "continue")
                self.assertIn("Directive 3.1", res.get("reason", ""))
            finally:
                if os.path.exists(tpath):
                    os.unlink(tpath)

    def test_blocks_inline_latin_in_persian_deliverables(self):
        payload = {
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": "03_deliverables/Chapter_2_Review.md",
                    "CodeContent": "طبق یافته‌های اخیر Smith (2022) سطح فرسودگی شغلی افزایش می‌یابد."
                }
            }
        }
        res = academic_writer_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Directive 5", res.get("reason", ""))
        self.assertIn("Smith", res.get("reason", ""))

    def test_stop_blocks_empty_or_corrupted_docx_body(self):
        import zipfile
        with tempfile.TemporaryDirectory() as temp_ws:
            docx_path = os.path.join(temp_ws, "Chapter_4_Findings.docx")
            xml_empty = (
                b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                b'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                b'<w:body></w:body></w:document>'
            )
            with zipfile.ZipFile(docx_path, "w") as zf:
                zf.writestr("word/document.xml", xml_empty)

            with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
                tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "Done drafting findings."}) + "\n")
                tpath = tf.name

            try:
                payload = {"transcriptPath": tpath, "workspacePaths": [temp_ws]}
                res = academic_writer_guard.handle_stop(payload)
                self.assertEqual(res.get("decision"), "continue")
                self.assertIn("Directive 5", res.get("reason", ""))
                self.assertIn("corrupted", res.get("reason", "").lower())
            finally:
                if os.path.exists(tpath):
                    os.unlink(tpath)

    def test_stop_blocks_manual_br_in_justified_runs(self):
        import zipfile
        with tempfile.TemporaryDirectory() as temp_ws:
            docx_path = os.path.join(temp_ws, "Chapter_4_Findings.docx")
            xml_content = (
                b'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                b'<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
                b'<w:body><w:p><w:pPr><w:jc w:val="both"/></w:pPr>'
                b'<w:r><w:t>' + (b'Text ' * 30) + b'</w:t><w:br/><w:t>More text</w:t></w:r>'
                b'</w:p></w:body></w:document>'
            )
            with zipfile.ZipFile(docx_path, "w") as zf:
                zf.writestr("word/document.xml", xml_content)

            with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
                tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "Done drafting findings."}) + "\n")
                tpath = tf.name

            try:
                payload = {"transcriptPath": tpath, "workspacePaths": [temp_ws]}
                res = academic_writer_guard.handle_stop(payload)
                self.assertEqual(res.get("decision"), "continue")
                self.assertIn("Directive 5", res.get("reason", ""))
                self.assertIn("manual line break", res.get("reason", "").lower())
            finally:
                if os.path.exists(tpath):
                    os.unlink(tpath)

    def test_stop_enforces_three_table_regression_in_writer(self):
        content = "تحلیل فرضیه رگرسیون چندگانه:\n| متغیر | ضریب بتا |\n|---|---|\n| استرس | ۰.۳۵ |"
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": content}) + "\n")
            tpath = tf.name

        try:
            payload = {"transcriptPath": tpath}
            res = academic_writer_guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("3-Table Regression Standard", res.get("reason", ""))
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)

    def test_writer_flags_p_zero_and_naked_persian_decimals(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "ضریب رگرسیون معنادار بود (p = .000)."}) + "\n")
            tpath = tf.name

        try:
            payload = {"transcriptPath": tpath}
            res = academic_writer_guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Directive 4", res.get("reason", ""))
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)

        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "سطح معناداری برابر با .۰۵ گزارش شد."}) + "\n")
            tpath = tf.name

        try:
            payload = {"transcriptPath": tpath}
            res = academic_writer_guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Directive 4", res.get("reason", ""))
            self.assertIn("Leading Zero", res.get("reason", ""))
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


class TestAuditorAgentsGuard(unittest.TestCase):
    """Tests for auditor_agents_guard (auditors and challengers)."""

    def test_blocks_subagent_delegation(self):
        for auditor in ("evidence-auditor", "results-auditor", "statistical-auditor", "academic-challenger", "final-judge"):
            payload = {
                "caller": auditor,
                "toolCall": {"name": "invoke_subagent", "args": {"TypeName": "statistics-agent"}}
            }
            res = auditor_agents_guard.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "deny", f"Failed for {auditor}")
            self.assertIn("Directive 12", res.get("reason", ""))

    def test_blocks_mutation_for_read_only_auditors(self):
        for auditor in ("evidence-auditor", "results-auditor", "academic-challenger", "final-judge"):
            payload = {
                "caller": auditor,
                "toolCall": {"name": "write_to_file", "args": {"TargetFile": "03_deliverables/report.docx"}}
            }
            res = auditor_agents_guard.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "deny", f"Failed for {auditor}")
            self.assertIn("Read-Only", res.get("reason", ""))

    def test_blocks_shell_execution_for_read_only_auditors(self):
        for auditor in ("evidence-auditor", "results-auditor", "academic-challenger", "final-judge"):
            payload = {
                "caller": auditor,
                "toolCall": {"name": "run_command", "args": {"CommandLine": "ls -la"}}
            }
            res = auditor_agents_guard.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "deny", f"Failed for {auditor}")
            self.assertIn("Execution Revocation", res.get("reason", ""))

    def test_allows_read_tools_for_auditors(self):
        payload = {
            "caller": "results-auditor",
            "toolCall": {"name": "view_file", "args": {"AbsolutePath": "03_deliverables/ch4.docx"}}
        }
        res = auditor_agents_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "allow")

    def test_statistical_auditor_blocks_deliverables_mutation(self):
        payload = {
            "caller": "statistical-auditor",
            "toolCall": {"name": "write_to_file", "args": {"TargetFile": "03_deliverables/findings.docx"}}
        }
        res = auditor_agents_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Auditor Mutation Boundary", res.get("reason", ""))

    def test_results_auditor_flags_p_zero_and_naked_persian_decimals(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "یافته‌ها حاکی از معناداری است (p = .000 و .۰۵)."}) + "\n")
            tpath = tf.name

        try:
            payload = {"caller": "results-auditor", "transcriptPath": tpath}
            res = auditor_agents_guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Directive 4", res.get("reason", ""))
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)

    def test_academic_challenger_blocks_rubber_stamp_approvals(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "Everything looks great! No methodology flaws detected, approved without questions."}) + "\n")
            tpath = tf.name

        try:
            payload = {"caller": "academic-challenger", "transcriptPath": tpath}
            res = auditor_agents_guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Anti-Sycophancy", res.get("reason", ""))
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)

    def test_final_judge_blocks_naive_20_grade(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "ارزیابی پایان‌نامه: نمره ۲۰ از ۲۰ بدون قید و شرط."}) + "\n")
            tpath = tf.name

        try:
            payload = {"caller": "final-judge", "transcriptPath": tpath}
            res = auditor_agents_guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Zero Grade Inflation", res.get("reason", ""))
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)

    def test_final_judge_requires_human_gate_card(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "Verdict: CLEARANCE_GRANTED with grade 18.5/20."}) + "\n")
            tpath = tf.name

        try:
            payload = {"caller": "final-judge", "transcriptPath": tpath}
            res = auditor_agents_guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Human Gate Card Required", res.get("reason", ""))
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)

    def test_evidence_auditor_flags_ghost_citations(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "Concordance verified, but found 1 ghost citation in Chapter 2."}) + "\n")
            tpath = tf.name

        try:
            payload = {"caller": "evidence-auditor", "transcriptPath": tpath}
            res = auditor_agents_guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Directive 14", res.get("reason", ""))
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)

    def test_statistical_auditor_flags_heywood_case(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "Audit check: error variance = -0.15 in CFA indicator."}) + "\n")
            tpath = tf.name

        try:
            payload = {"caller": "statistical-auditor", "transcriptPath": tpath}
            res = auditor_agents_guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Heywood case", res.get("reason", ""))
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)


class TestProjectOrganizerGuard(unittest.TestCase):
    """Tests for project_organizer_guard."""

    def test_blocks_subagent_delegation(self):
        payload = {"toolCall": {"name": "invoke_subagent", "args": {"TypeName": "statistics-agent"}}}
        res = project_organizer_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Directive 12", res.get("reason", ""))

    def test_blocks_raw_data_modification(self):
        with tempfile.NamedTemporaryFile("w+", delete=False) as f:
            f.write("raw data")
            raw_path = f.name

        try:
            payload = {
                "toolCall": {
                    "name": "write_to_file",
                    "args": {"TargetFile": os.path.join(os.path.dirname(raw_path), "01_raw_inputs", os.path.basename(raw_path)), "Overwrite": True}
                }
            }
            # Simulate target in 01_raw_inputs
            res = project_organizer_guard.handle_pre_tool_use(payload)
            # Will be allowed if target file doesn't exist yet, but if it exists:
            os.makedirs(os.path.join(os.path.dirname(raw_path), "01_raw_inputs"), exist_ok=True)
            real_target = os.path.join(os.path.dirname(raw_path), "01_raw_inputs", "test.xlsx")
            with open(real_target, "w") as rf:
                rf.write("dummy")
            payload["toolCall"]["args"]["TargetFile"] = real_target
            res = project_organizer_guard.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "deny")
            self.assertIn("Raw Data Protection", res.get("reason", ""))
        finally:
            if os.path.exists(raw_path):
                os.unlink(raw_path)

    def test_blocks_destructive_shell_command(self):
        payload = {"toolCall": {"name": "run_command", "args": {"CommandLine": "rm -rf 01_raw_inputs/data.xlsx"}}}
        res = project_organizer_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Raw Data Protection", res.get("reason", ""))

    def test_blocks_root_script_targets(self):
        with tempfile.TemporaryDirectory() as ws:
            payload = {
                "toolCall": {"name": "write_to_file", "args": {"TargetFile": os.path.join(ws, "organize.py")}},
                "workspacePaths": [ws]
            }
            res = project_organizer_guard.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "deny")
            self.assertIn("Directive 23", res.get("reason", ""))

    def test_blocks_non_ascii_filenames(self):
        payload = {"toolCall": {"name": "write_to_file", "args": {"TargetFile": "02_code/کد_پروژه.py"}}}
        res = project_organizer_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Directive 6", res.get("reason", ""))

    def test_stop_verifies_4_tier_taxonomy_scaffolding(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "Project scaffolded successfully for new client."}) + "\n")
            tpath = tf.name

        try:
            with tempfile.TemporaryDirectory() as ws:
                # Without tiers created, stop hook should flag violation
                payload = {"transcriptPath": tpath, "workspacePaths": [ws]}
                res = project_organizer_guard.handle_stop(payload)
                self.assertEqual(res.get("decision"), "continue")
                self.assertIn("4-Tier", res.get("reason", ""))

                # Now create tiers + project_meta.json
                for t in ("01_raw_inputs", "02_analysis_code", "03_deliverables", "04_references_and_lit"):
                    os.makedirs(os.path.join(ws, t), exist_ok=True)
                with open(os.path.join(ws, "project_meta.json"), "w") as mf:
                    json.dump({"client": "test"}, mf)

                res2 = project_organizer_guard.handle_stop(payload)
                self.assertEqual(res2.get("decision"), "allow")
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)


class TestPsychometricExpertGuard(unittest.TestCase):
    """Tests for psychometric_expert_guard."""

    def test_blocks_subagent_delegation(self):
        payload = {"toolCall": {"name": "invoke_subagent", "args": {"TypeName": "statistics-agent"}}}
        res = psychometric_expert_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Directive 12", res.get("reason", ""))

    def test_blocks_cli_script_without_view_file(self):
        payload = {"toolCall": {"name": "run_command", "args": {"CommandLine": "python3 .agents/skills/cfa/scripts/run_cfa.py"}}}
        res = psychometric_expert_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Directive 1", res.get("reason", ""))

    def test_allows_cli_script_after_view_file(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({
                "type": "PLANNER_RESPONSE",
                "tool_calls": [{"name": "view_file", "args": {"AbsolutePath": ".agents/skills/cfa/SKILL.md"}}]
            }) + "\n")
            tpath = tf.name

        try:
            payload = {
                "toolCall": {"name": "run_command", "args": {"CommandLine": "python3 .agents/skills/cfa/scripts/run_cfa.py"}},
                "transcriptPath": tpath
            }
            res = psychometric_expert_guard.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "allow")
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)

    def test_stop_blocks_heywood_cases_and_loading_over_one(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "CFA Results: Standardized loading: 1.15 and theta: -0.05."}) + "\n")
            tpath = tf.name

        try:
            payload = {"transcriptPath": tpath}
            res = psychometric_expert_guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Mathematical Admissibility", res.get("reason", ""))
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)

    def test_stop_flags_p_zero_and_naked_persian_decimals(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "شاخص برازش با p = .000 و ضریب .۷۵ گزارش شد."}) + "\n")
            tpath = tf.name

        try:
            payload = {"transcriptPath": tpath}
            res = psychometric_expert_guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Directive 4", res.get("reason", ""))
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)


class TestResearchLiteratureGuard(unittest.TestCase):
    """Tests for research_literature_guard."""

    def test_blocks_subagent_delegation(self):
        payload = {"toolCall": {"name": "invoke_subagent", "args": {"TypeName": "statistics-agent"}}}
        res = research_literature_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Directive 12", res.get("reason", ""))

    def test_blocks_cli_script_without_view_file(self):
        payload = {"toolCall": {"name": "run_command", "args": {"CommandLine": "python3 .agents/skills/gpower-sample-size-calculator/scripts/power_calc.py"}}}
        res = research_literature_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Directive 1", res.get("reason", ""))

    def test_stop_blocks_temporal_hallucinations(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "Currently in 2024, empirical literature indicates..."}) + "\n")
            tpath = tf.name

        try:
            payload = {"transcriptPath": tpath}
            res = research_literature_guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Directive 15", res.get("reason", ""))
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)

    def test_stop_flags_ghost_dois(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "Paper citation: Smith et al. (2023), doi: 10.1234/ghost"}) + "\n")
            tpath = tf.name

        try:
            payload = {"caller": "literature-expert", "transcriptPath": tpath}
            res = research_literature_guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Directive 14", res.get("reason", ""))
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)


class TestDomainSpecialistsGuard(unittest.TestCase):
    """Tests for domain_specialists_guard."""

    def test_blocks_subagent_delegation(self):
        payload = {"caller": "data-curator", "toolCall": {"name": "invoke_subagent", "args": {"TypeName": "statistics-agent"}}}
        res = domain_specialists_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Directive 12", res.get("reason", ""))

    def test_data_curator_blocks_raw_data_modification(self):
        payload = {
            "caller": "data-curator",
            "toolCall": {"name": "write_to_file", "args": {"TargetFile": "01_raw_inputs/survey.csv"}}
        }
        res = domain_specialists_guard.handle_pre_tool_use(payload)
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Raw Data Protection", res.get("reason", ""))

    def test_blocks_root_script_targets(self):
        with tempfile.TemporaryDirectory() as ws:
            payload = {
                "caller": "meta-analyst",
                "toolCall": {"name": "write_to_file", "args": {"TargetFile": os.path.join(ws, "run_meta.py")}},
                "workspacePaths": [ws]
            }
            res = domain_specialists_guard.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "deny")
            self.assertIn("Directive 23", res.get("reason", ""))

    def test_blocks_shell_for_no_exec_specialists(self):
        for spec in ("journal-strategist", "intervention-designer"):
            payload = {
                "caller": spec,
                "toolCall": {"name": "run_command", "args": {"CommandLine": "python3 script.py"}}
            }
            res = domain_specialists_guard.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "deny", f"Failed for {spec}")
            self.assertIn("Capability Boundary", res.get("reason", ""))

    def test_stop_flags_p_zero_and_naked_persian_decimals(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "فراتحلیل اندازه اثر .۴۵ با p = .000 به دست آمد."}) + "\n")
            tpath = tf.name

        try:
            payload = {"transcriptPath": tpath}
            res = domain_specialists_guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Directive 4", res.get("reason", ""))
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)


class TestAdvisoryAgentsGuard(unittest.TestCase):
    """Tests for advisory_agents_guard (digital-saber, methodology-expert, statistical-expert)."""

    def test_blocks_subagent_delegation(self):
        for adv in ("digital-saber", "methodology-expert", "statistical-expert"):
            payload = {"caller": adv, "toolCall": {"name": "invoke_subagent", "args": {"TypeName": "statistics-agent"}}}
            res = advisory_agents_guard.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "deny", f"Failed for {adv}")
            self.assertIn("Directive 12", res.get("reason", ""))

    def test_blocks_mutation_tools(self):
        for adv in ("digital-saber", "methodology-expert", "statistical-expert"):
            payload = {"caller": adv, "toolCall": {"name": "write_to_file", "args": {"TargetFile": "test.txt"}}}
            res = advisory_agents_guard.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "deny", f"Failed for {adv}")
            self.assertIn("Advisor Read-Only", res.get("reason", ""))

    def test_blocks_shell_execution(self):
        for adv in ("digital-saber", "methodology-expert", "statistical-expert"):
            payload = {"caller": adv, "toolCall": {"name": "run_command", "args": {"CommandLine": "ls"}}}
            res = advisory_agents_guard.handle_pre_tool_use(payload)
            self.assertEqual(res.get("decision"), "deny", f"Failed for {adv}")
            self.assertIn("Execution Revocation", res.get("reason", ""))

    def test_stop_blocks_sycophantic_flattery(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "Great question! That is a brilliant research idea."}) + "\n")
            tpath = tf.name

        try:
            payload = {"caller": "digital-saber", "transcriptPath": tpath}
            res = advisory_agents_guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Directive 13", res.get("reason", ""))
        finally:
            if os.path.exists(tpath):
                os.unlink(tpath)

    def test_stop_requires_human_gate_for_digital_saber_pricing(self):
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "برآورد مالی این پروژه ۱۵ میلیون تومان خواهد بود."}) + "\n")
            tpath = tf.name

        try:
            payload = {"caller": "digital-saber", "transcriptPath": tpath}
            res = advisory_agents_guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Human Gate Required", res.get("reason", ""))
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
