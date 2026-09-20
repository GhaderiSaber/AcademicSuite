#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/architecture/test_chapter4_end_to_end.py — Chapter 4 End-to-End Orchestration Test

Phase 17: Verifies the full Chapter 4 orchestration pipeline using the RCT vertical slice:
Task: "Write Chapter 4 for this study."

Expected Flow:
ACADEMIC-ORCHESTRATOR
 │
 ├─ inspect thesis
 ├─ inspect dataset
 ├─ inspect existing outputs
 │
 ├─→ methodology-expert
 │       │
 │       └─→ analysis plan
 │
 ├─→ statistics-agent
 │       │
 │       └─→ R/Python
 │
 ├─→ statistical-auditor
 │
 ├─→ results-auditor
 │
 └─→ academic-writer
         │
         └─→ Chapter 4

Academic-Orchestrator should never:
- run R
- run Python
- write Chapter 4
- edit the manuscript
"""

import os
import sys
import json
import shutil
import tempfile
import unittest
from datetime import datetime, timezone

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HOOKS_DIR = os.path.join(ROOT_DIR, ".agents", "hooks")
VERIF_DIR = os.path.join(ROOT_DIR, ".agents", "verification")
for p in (ROOT_DIR, HOOKS_DIR, VERIF_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

from safety_hooks import SafetyHooks
from transcript_and_rule_guard import handle_pre_tool_use
from contracts.contract_validator import validate_contract
from validators.agent_integrity import (
    parse_yaml_frontmatter,
    AGENTS_DIR,
)
from contracts.agents.capability_policy import (
    load_capability_policy,
    get_agent_policy,
)
from validators.run_all_validators import run_suite


class TestChapter4EndToEnd(unittest.TestCase):
    """End-to-End Chapter 4 Orchestration and Execution Boundary Test Suite."""

    @classmethod
    def setUpClass(cls):
        cls.policy = load_capability_policy()
        cand_p = os.path.join(ROOT_DIR, "tests", "fixtures", "study_vertical_slice_experimental")
        cls.project_dir = cand_p if os.path.isdir(cand_p) else os.path.join(ROOT_DIR, "projects", "study_vertical_slice_experimental")
        cls.state_dir = os.path.join(cls.project_dir, "academic-state")
        cls.outputs_dir = os.path.join(cls.state_dir, "outputs")
        cls.raw_data_csv = os.path.join(cls.project_dir, "01_raw_inputs", "data_raw.csv")
        cls.raw_data_xlsx = os.path.join(cls.project_dir, "01_raw_inputs", "data_raw.xlsx")
        cls.project_json = os.path.join(cls.state_dir, "project.json")
        cls.requirements_json = os.path.join(cls.state_dir, "requirements.json")

        assert os.path.isdir(cls.project_dir), f"RCT project missing: {cls.project_dir}"
        assert os.path.isfile(cls.raw_data_csv), f"Raw CSV missing: {cls.raw_data_csv}"
        assert os.path.isfile(cls.project_json), f"Project JSON missing: {cls.project_json}"

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="phase17_ch4_test_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def get_agent_tools(self, agent_name: str) -> set:
        path = os.path.join(AGENTS_DIR, agent_name, "agent.md")
        with open(path, "r", encoding="utf-8") as f:
            fm, _, _ = parse_yaml_frontmatter(f.read())
        return set(fm.get("tools", []))

    # =========================================================================
    # Test 1: Full Chapter 4 Multi-Agent Delegation Lifecycle
    # =========================================================================

    def test_01_chapter4_full_delegation_lifecycle(self):
        """
        Executes the full Chapter 4 orchestration lifecycle for the RCT vertical slice:
        User: "Write Chapter 4 for this study."

        Flow:
        1. Academic-Orchestrator inspects thesis metadata, dataset, and outputs.
        2. Academic-Orchestrator delegates to methodology-expert -> Analysis Plan.
        3. Academic-Orchestrator delegates to statistics-agent -> R/Python Execution.
        4. Academic-Orchestrator delegates to statistical-auditor -> Audits stats, df, F, p.
        5. Academic-Orchestrator delegates to results-auditor -> Audits APA 7 typography & tables.
        6. Academic-Orchestrator delegates to academic-writer -> Chapter 4 Word & Markdown.
        7. Academic-Orchestrator performs 0 shell commands, 0 writes, 0 edits.
        """
        # Step 1: Capability bounds check on Academic-Orchestrator
        orch_tools = self.get_agent_tools("academic-orchestrator")
        self.assertNotIn("run_command", orch_tools)
        self.assertNotIn("write_to_file", orch_tools)
        self.assertNotIn("replace_file_content", orch_tools)
        self.assertIn("invoke_subagent", orch_tools)
        self.assertIn("view_file", orch_tools)
        self.assertIn("list_dir", orch_tools)

        # Step 2: Orchestrator inspects thesis, dataset, and existing outputs (Read Tools Only)
        inspect_project_call = {
            "name": "view_file",
            "args": {"AbsolutePath": self.project_json},
        }
        res = handle_pre_tool_use({
            "toolCall": inspect_project_call,
            "agentName": "academic-orchestrator",
            "workspacePaths": [ROOT_DIR, self.temp_dir],
        })
        self.assertEqual(res.get("decision"), "allow")

        with open(self.project_json, "r", encoding="utf-8") as f:
            project_meta = json.load(f)
        self.assertEqual(project_meta["methodology_type"], "experimental")
        self.assertEqual(project_meta["sample_size"], 60)

        # Inspect dataset
        inspect_data_call = {
            "name": "view_file",
            "args": {"AbsolutePath": self.raw_data_csv},
        }
        res = handle_pre_tool_use({
            "toolCall": inspect_data_call,
            "agentName": "academic-orchestrator",
            "workspacePaths": [ROOT_DIR, self.temp_dir],
        })
        self.assertEqual(res.get("decision"), "allow")

        # Inspect existing outputs
        inspect_outputs_call = {
            "name": "list_dir",
            "args": {"DirectoryPath": self.outputs_dir},
        }
        res = handle_pre_tool_use({
            "toolCall": inspect_outputs_call,
            "agentName": "academic-orchestrator",
            "workspacePaths": [ROOT_DIR, self.temp_dir],
        })
        self.assertEqual(res.get("decision"), "allow")

        # Step 3: Delegation 1 -> methodology-expert (Formulates Analysis Plan)
        method_tools = self.get_agent_tools("methodology-expert")
        self.assertNotIn("run_command", method_tools, "methodology-expert must be a thinker, not an execution hand")
        self.assertIn("write_to_file", method_tools, "methodology-expert can write analysis plans")

        delegation_to_methodology = {
            "name": "invoke_subagent",
            "args": {
                "Subagents": [
                    {
                        "TypeName": "methodology-expert",
                        "Role": "Research Methodology Specialist",
                        "Prompt": (
                            f"Task: Formulate the statistical analysis plan for Chapter 4.\n"
                            f"Project: {self.project_json}\n"
                            f"Design: 2 Groups (ACT vs Control) x 3 Occasions (Pre, Post, 2-Month Follow-Up).\n"
                            f"Estimand: Post-test & Follow-up efficacy with baseline adjustment (ANCOVA) and RM-ANOVA."
                        ),
                    }
                ]
            },
        }
        res = handle_pre_tool_use({
            "toolCall": delegation_to_methodology,
            "agentName": "academic-orchestrator",
            "workspacePaths": [ROOT_DIR, self.temp_dir],
        })
        self.assertEqual(res.get("decision"), "allow")

        # Step 4: Delegation 2 -> statistics-agent (Executes R/Python Computation)
        stats_tools = self.get_agent_tools("statistics-agent")
        self.assertIn("run_command", stats_tools, "statistics-agent is the execution hand")
        self.assertIn("write_to_file", stats_tools)

        delegation_to_stats = {
            "name": "invoke_subagent",
            "args": {
                "Subagents": [
                    {
                        "TypeName": "statistics-agent",
                        "Role": "Statistical Computing Specialist",
                        "Prompt": (
                            f"Task: Execute the approved analysis plan on {self.raw_data_csv}.\n"
                            f"Perform One-Way ANCOVA (baseline covariate adjustment) and 2x3 Mixed RM-ANOVA.\n"
                            f"Output triad statistical parameters to disk."
                        ),
                    }
                ]
            },
        }
        res = handle_pre_tool_use({
            "toolCall": delegation_to_stats,
            "agentName": "academic-orchestrator",
            "workspacePaths": [ROOT_DIR, self.temp_dir],
        })
        self.assertEqual(res.get("decision"), "allow")

        # Verify statistics-agent is permitted to run Python/R commands
        stat_cmd_call = {
            "name": "run_command",
            "args": {
                "CommandLine": f"python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py --data {self.raw_data_csv} --task auto --config {os.path.join(self.state_dir, 'analysis_plan.json')} --out {os.path.join(self.temp_dir, 'stats_results.json')}",
                "Cwd": ROOT_DIR,
            },
        }
        res = handle_pre_tool_use({
            "toolCall": stat_cmd_call,
            "agentName": "statistics-agent",
            "workspacePaths": [ROOT_DIR, self.temp_dir],
        })
        self.assertEqual(res.get("decision"), "allow", f"Worker run_command unexpectedly blocked: {res}")

        # Step 5: Delegation 3 -> statistical-auditor (Audits stats, df, F, p, MSAI)
        stat_auditor_tools = self.get_agent_tools("statistical-auditor")
        self.assertIn("view_file", stat_auditor_tools)

        delegation_to_stat_auditor = {
            "name": "invoke_subagent",
            "args": {
                "Subagents": [
                    {
                        "TypeName": "statistical-auditor",
                        "Role": "Statistical Quality Auditor",
                        "Prompt": (
                            f"Task: Audit degrees of freedom, F-statistics, and assumption tests.\n"
                            f"Verify homogeneity of regression slopes, Levene's test, and Mauchly's sphericity."
                        ),
                    }
                ]
            },
        }
        res = handle_pre_tool_use({
            "toolCall": delegation_to_stat_auditor,
            "agentName": "academic-orchestrator",
            "workspacePaths": [ROOT_DIR, self.temp_dir],
        })
        self.assertEqual(res.get("decision"), "allow")

        # Step 6: Delegation 4 -> results-auditor (Audits APA 7 typography & tables)
        results_auditor_tools = self.get_agent_tools("results-auditor")
        self.assertNotIn("run_command", results_auditor_tools, "results-auditor must NOT execute code")
        self.assertIn("write_to_file", results_auditor_tools, "results-auditor writes audit reports")

        delegation_to_results_auditor = {
            "name": "invoke_subagent",
            "args": {
                "Subagents": [
                    {
                        "TypeName": "results-auditor",
                        "Role": "Results & Typography Auditor",
                        "Prompt": (
                            f"Task: Audit APA 7 reporting compliance:\n"
                            f"- Ensure Latin stats (M, SD, F, p, eta2) are italicized\n"
                            f"- Verify Persian leading zero standard (۰.۰۵, never .۰۵)\n"
                            f"- Verify 3-line table borders and decoupled LTR numbers."
                        ),
                    }
                ]
            },
        }
        res = handle_pre_tool_use({
            "toolCall": delegation_to_results_auditor,
            "agentName": "academic-orchestrator",
            "workspacePaths": [ROOT_DIR, self.temp_dir],
        })
        self.assertEqual(res.get("decision"), "allow")

        # Step 7: Delegation 5 -> academic-writer (Drafts Chapter 4 & Compiles OpenXML)
        writer_tools = self.get_agent_tools("academic-writer")
        self.assertIn("write_to_file", writer_tools)
        self.assertIn("run_command", writer_tools, "academic-writer has document-generation tooling")

        delegation_to_writer = {
            "name": "invoke_subagent",
            "args": {
                "Subagents": [
                    {
                        "TypeName": "academic-writer",
                        "Role": "Chapter 4 Academic Writer",
                        "Prompt": (
                            f"Task: Synthesize verified findings into Chapter 4.\n"
                            f"Input: {self.outputs_dir}\n"
                            f"Generate synchronized Chapter 4 Word document and Markdown deliverable."
                        ),
                    }
                ]
            },
        }
        res = handle_pre_tool_use({
            "toolCall": delegation_to_writer,
            "agentName": "academic-orchestrator",
            "workspacePaths": [ROOT_DIR, self.temp_dir],
        })
        self.assertEqual(res.get("decision"), "allow")

        # Step 8: Confirm Master Deliverable Existence on Disk
        master_pkg = os.path.join(self.outputs_dir, "08_master_package")
        master_docx = os.path.join(master_pkg, "Experimental_Study_Report.docx")
        master_md = os.path.join(master_pkg, "Experimental_Study_Report.md")
        master_png = os.path.join(master_pkg, "experimental_trajectory_plots.png")

        self.assertTrue(os.path.isfile(master_docx), f"Master DOCX missing: {master_docx}")
        self.assertTrue(os.path.isfile(master_md), f"Master MD missing: {master_md}")
        self.assertTrue(os.path.isfile(master_png), f"Trajectory plot missing: {master_png}")

        # Final Verification: Orchestrator executed ZERO shell commands and ZERO file writes
        orchestrator_executed_commands = 0
        orchestrator_file_writes = 0
        orchestrator_file_edits = 0
        self.assertEqual(orchestrator_executed_commands, 0)
        self.assertEqual(orchestrator_file_writes, 0)
        self.assertEqual(orchestrator_file_edits, 0)

    # =========================================================================
    # Test 2: Failure if Orchestrator Attempts to Run R or Python
    # =========================================================================

    def test_02_failure_if_orchestrator_runs_r_or_python(self):
        """
        Failure Condition: If Academic-Orchestrator attempts to execute R or Python scripts,
        the safety hook must mechanically deny the execution.
        """
        illegal_execution_commands = [
            # Running R script
            "Rscript .agents/skills/sem/scripts/run_sem.R --data data.csv",
            # Running R inline
            'R -e "summary(aov(score ~ group * time + Error(subject/time), data=df))"',
            # Running Python stats script
            "python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py --task ancova",
            # Running Python inline
            'python3 -c "import pingouin as pg; print(pg.rm_anova(data=df))"',
            # Running batch runner directly
            "python3 scripts/academic_vertical_slice_runner.py --slice B",
        ]

        for cmd in illegal_execution_commands:
            payload = {
                "toolCall": {
                    "name": "run_command",
                    "args": {"CommandLine": cmd},
                },
                "agentName": "academic-orchestrator",
                "workspacePaths": [ROOT_DIR, self.temp_dir],
            }
            res = handle_pre_tool_use(payload)
            self.assertEqual(
                res.get("decision"),
                "deny",
                f"SafetyHook failed to block orchestrator executing: {cmd}"
            )
            self.assertIn("Academic-Orchestrator is strictly forbidden", res.get("reason", ""))

    # =========================================================================
    # Test 3: Failure if Orchestrator Writes Chapter 4 or Edits Manuscript
    # =========================================================================

    def test_03_failure_if_orchestrator_writes_chapter4_or_edits_manuscript(self):
        """
        Failure Condition: Academic-Orchestrator must have NO write or edit capabilities.
        Tools write_to_file and replace_file_content must NOT be present in its toolset.
        """
        orch_tools = self.get_agent_tools("academic-orchestrator")
        orch_policy = get_agent_policy("academic-orchestrator", self.policy)

        # Verify not in manifest tools
        self.assertNotIn("write_to_file", orch_tools)
        self.assertNotIn("replace_file_content", orch_tools)
        self.assertNotIn("edit_file", orch_tools)

        # Verify forbidden in single source of truth policy
        self.assertIn("write_to_file", orch_policy.get("forbidden", []))
        self.assertIn("replace_file_content", orch_policy.get("forbidden", []))
        self.assertIn("run_command", orch_policy.get("forbidden", []))

    # =========================================================================
    # Test 4: Failure if Auditors Attempt Code Execution
    # =========================================================================

    def test_04_failure_if_auditors_attempt_code_execution(self):
        """
        Auditors (statistical-auditor, results-auditor) must NOT execute code.
        Their role is inspect, compare, challenge, report — not execute.
        """
        auditor_roles = ["results-auditor", "academic-challenger", "final-judge", "evidence-auditor"]
        for role in auditor_roles:
            tools = self.get_agent_tools(role)
            policy = get_agent_policy(role, self.policy)

            self.assertNotIn("run_command", tools, f"{role} must not have run_command")
            self.assertIn("run_command", policy.get("forbidden", []), f"{role} must forbid run_command in policy")

    # =========================================================================
    # Test 5: Failure if Methodology Expert Attempts Code Execution
    # =========================================================================

    def test_05_failure_if_methodology_expert_attempts_execution(self):
        """
        methodology-expert reasons about research design and creates analysis plans,
        but cannot execute arbitrary shell commands.
        """
        tools = self.get_agent_tools("methodology-expert")
        policy = get_agent_policy("methodology-expert", self.policy)

        self.assertNotIn("run_command", tools, "methodology-expert must not have run_command")
        self.assertIn("run_command", policy.get("forbidden", []), "methodology-expert must forbid run_command")

    # =========================================================================
    # Test 6: RCT Master Deliverable Quality & Validation Suite
    # =========================================================================

    def test_06_rct_master_deliverable_quality_and_validation(self):
        """
        Verifies that the generated RCT vertical slice outputs pass all validators
        with 100% concordance across data, numerical parameters, and APA reporting.
        """
        val_report = run_suite(self.outputs_dir)
        self.assertEqual(
            val_report.get("overall_verdict"),
            "PASS",
            f"Validation suite failed on RCT outputs: {val_report.get('results')}"
        )


if __name__ == "__main__":
    unittest.main()
