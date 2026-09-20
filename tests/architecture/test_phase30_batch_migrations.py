#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/architecture/test_phase30_batch_migrations.py — Phase 30 Complete Agent Set Migration Verification

Verifies all 5 batches of migrated agents:
- Batch 1: academic-orchestrator, methodology-expert, statistical-expert
- Batch 2: statistics-agent, data-agent, data-curator
- Batch 3: academic-writer, research-agent, literature-expert
- Batch 4: auditors (statistical-auditor, results-auditor), challenger (academic-challenger), final-judge, evidence-auditor, journal-strategist
- Batch 5: learning agents (behavior-analyst, trajectory-analyzer, evaluation-agent), curriculum-builder, knowledge-curator, skill-evolver
"""

import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from validators.agent_integrity import (
    parse_yaml_frontmatter,
    AGENTS_DIR,
)
from contracts.agents.capability_policy import (
    load_capability_policy,
    get_agent_policy,
    validate_agent_against_policy,
)
from scripts.immutable_capability_boundary_guard import NON_EXECUTING_AGENTS


class TestPhase30BatchMigrations(unittest.TestCase):
    """Systematic verification of all 5 batches of migrated agents."""

    @classmethod
    def setUpClass(cls):
        cls.policy = load_capability_policy()

    def get_agent_frontmatter(self, agent_name: str) -> dict:
        agent_file = os.path.join(AGENTS_DIR, agent_name, "agent.md")
        self.assertTrue(os.path.isfile(agent_file), f"Agent file missing: {agent_file}")
        with open(agent_file, "r", encoding="utf-8") as f:
            fm, _, err = parse_yaml_frontmatter(f.read())
            self.assertIsNone(err, f"Frontmatter error for {agent_name}: {err}")
            return fm

    def get_agent_tools(self, agent_name: str) -> set:
        fm = self.get_agent_frontmatter(agent_name)
        return set(fm.get("tools", []))

    # =========================================================================
    # Batch 1: Conductor & Methodological Planners
    # =========================================================================
    def test_01_batch1_academic_orchestrator(self):
        """Batch 1: academic-orchestrator has invoke_subagent, zero execution tools, zero write tools."""
        tools = self.get_agent_tools("academic-orchestrator")
        self.assertIn("invoke_subagent", tools)
        self.assertNotIn("run_command", tools)
        self.assertNotIn("write_to_file", tools)
        self.assertNotIn("replace_file_content", tools)
        self.assertNotIn("edit_file", tools)

        fm = self.get_agent_frontmatter("academic-orchestrator")
        self.assertTrue(fm.get("mainAgent", False))
        self.assertIn("statistical-expert", fm.get("agents", []))
        self.assertIn("methodology-expert", fm.get("agents", []))
        self.assertIn("statistics-agent", fm.get("agents", []))
        self.assertIn("academic-writer", fm.get("agents", []))

    def test_02_batch1_methodology_expert(self):
        """Batch 1: methodology-expert is a planner with no run_command, delegates to statistics-agent."""
        tools = self.get_agent_tools("methodology-expert")
        self.assertIn("invoke_subagent", tools)
        self.assertNotIn("run_command", tools)
        self.assertIn("write_to_file", tools)

        fm = self.get_agent_frontmatter("methodology-expert")
        self.assertIn("statistics-agent", fm.get("agents", []))
        self.assertIn("methodology-expert", NON_EXECUTING_AGENTS)

    def test_03_batch1_statistical_expert(self):
        """Batch 1: statistical-expert is a planner with no run_command, delegates to statistics-agent."""
        tools = self.get_agent_tools("statistical-expert")
        self.assertIn("invoke_subagent", tools)
        self.assertNotIn("run_command", tools)
        self.assertIn("write_to_file", tools)

        fm = self.get_agent_frontmatter("statistical-expert")
        self.assertIn("statistics-agent", fm.get("agents", []))
        self.assertIn("statistical-expert", NON_EXECUTING_AGENTS)

    # =========================================================================
    # Batch 2: Statistics & Data Execution Workers
    # =========================================================================
    def test_04_batch2_statistics_agent(self):
        """Batch 2: statistics-agent is an execution worker with run_command, cannot delegate."""
        tools = self.get_agent_tools("statistics-agent")
        self.assertIn("run_command", tools)
        self.assertIn("write_to_file", tools)
        self.assertNotIn("invoke_subagent", tools)

        fm = self.get_agent_frontmatter("statistics-agent")
        self.assertEqual(fm.get("agents", []), [])

    def test_05_batch2_data_agent(self):
        """Batch 2: data-agent is an execution worker with run_command, cannot delegate."""
        tools = self.get_agent_tools("data-agent")
        self.assertIn("run_command", tools)
        self.assertIn("write_to_file", tools)
        self.assertNotIn("invoke_subagent", tools)

        fm = self.get_agent_frontmatter("data-agent")
        self.assertEqual(fm.get("agents", []), [])

    def test_06_batch2_data_curator(self):
        """Batch 2: data-curator is an execution worker with run_command, cannot delegate."""
        tools = self.get_agent_tools("data-curator")
        self.assertIn("run_command", tools)
        self.assertIn("write_to_file", tools)
        self.assertNotIn("invoke_subagent", tools)

        fm = self.get_agent_frontmatter("data-curator")
        self.assertEqual(fm.get("agents", []), [])

    # =========================================================================
    # Batch 3: Academic Writer, Research Agent, Literature Expert
    # =========================================================================
    def test_07_batch3_academic_writer(self):
        """Batch 3: academic-writer is a docgen execution worker, cannot delegate."""
        tools = self.get_agent_tools("academic-writer")
        self.assertIn("run_command", tools)
        self.assertIn("write_to_file", tools)
        self.assertIn("replace_file_content", tools)
        self.assertNotIn("invoke_subagent", tools)

        fm = self.get_agent_frontmatter("academic-writer")
        self.assertEqual(fm.get("agents", []), [])

    def test_08_batch3_research_agent(self):
        """Batch 3: research-agent has search tools and run_command for G*Power power calculations."""
        tools = self.get_agent_tools("research-agent")
        self.assertIn("run_command", tools)
        self.assertIn("write_to_file", tools)
        self.assertIn("search_web", tools)
        self.assertNotIn("invoke_subagent", tools)

        fm = self.get_agent_frontmatter("research-agent")
        self.assertEqual(fm.get("agents", []), [])

    def test_09_batch3_literature_expert(self):
        """Batch 3: literature-expert has bibliometric analysis execution and search tools."""
        tools = self.get_agent_tools("literature-expert")
        self.assertIn("run_command", tools)
        self.assertIn("write_to_file", tools)
        self.assertIn("search_web", tools)
        self.assertNotIn("invoke_subagent", tools)

        fm = self.get_agent_frontmatter("literature-expert")
        self.assertEqual(fm.get("agents", []), [])

    # =========================================================================
    # Batch 4: Auditors, Challenger, Final Judge, Strategist
    # =========================================================================
    def test_10_batch4_results_auditor(self):
        """Batch 4: results-auditor is a non-executing critic (no run_command, no invoke_subagent)."""
        tools = self.get_agent_tools("results-auditor")
        self.assertNotIn("run_command", tools)
        self.assertNotIn("invoke_subagent", tools)
        self.assertIn("write_to_file", tools)
        self.assertIn("results-auditor", NON_EXECUTING_AGENTS)

    def test_11_batch4_academic_challenger(self):
        """Batch 4: academic-challenger is a non-executing critic (no run_command, no invoke_subagent)."""
        tools = self.get_agent_tools("academic-challenger")
        self.assertNotIn("run_command", tools)
        self.assertNotIn("invoke_subagent", tools)
        self.assertIn("write_to_file", tools)
        self.assertIn("academic-challenger", NON_EXECUTING_AGENTS)

    def test_12_batch4_final_judge(self):
        """Batch 4: final-judge is a non-executing release gatekeeper (no run_command, no invoke_subagent)."""
        tools = self.get_agent_tools("final-judge")
        self.assertNotIn("run_command", tools)
        self.assertNotIn("invoke_subagent", tools)
        self.assertIn("write_to_file", tools)
        self.assertIn("final-judge", NON_EXECUTING_AGENTS)

    def test_13_batch4_evidence_auditor(self):
        """Batch 4: evidence-auditor is a non-executing auditor (no run_command, no invoke_subagent)."""
        tools = self.get_agent_tools("evidence-auditor")
        self.assertNotIn("run_command", tools)
        self.assertNotIn("invoke_subagent", tools)
        self.assertIn("write_to_file", tools)
        self.assertIn("evidence-auditor", NON_EXECUTING_AGENTS)

    def test_14_batch4_journal_strategist(self):
        """Batch 4: journal-strategist is a non-executing critic (no run_command, no invoke_subagent)."""
        tools = self.get_agent_tools("journal-strategist")
        self.assertNotIn("run_command", tools)
        self.assertNotIn("invoke_subagent", tools)
        self.assertIn("write_to_file", tools)
        self.assertIn("journal-strategist", NON_EXECUTING_AGENTS)

    def test_15_batch4_statistical_auditor(self):
        """Batch 4: statistical-auditor has justified run_command for MSAI anomaly calculations."""
        tools = self.get_agent_tools("statistical-auditor")
        self.assertIn("run_command", tools)
        self.assertIn("write_to_file", tools)
        self.assertNotIn("invoke_subagent", tools)

    # =========================================================================
    # Batch 5: Learning System Agents
    # =========================================================================
    def test_16_batch5_behavior_analyst(self):
        """Batch 5: behavior-analyst is strictly read-only (no run_command, no write_to_file)."""
        tools = self.get_agent_tools("behavior-analyst")
        self.assertNotIn("run_command", tools)
        self.assertNotIn("write_to_file", tools)
        self.assertNotIn("invoke_subagent", tools)
        self.assertIn("behavior-analyst", NON_EXECUTING_AGENTS)

    def test_17_batch5_trajectory_analyzer(self):
        """Batch 5: trajectory-analyzer is strictly read-only (no run_command, no write_to_file)."""
        tools = self.get_agent_tools("trajectory-analyzer")
        self.assertNotIn("run_command", tools)
        self.assertNotIn("write_to_file", tools)
        self.assertNotIn("invoke_subagent", tools)
        self.assertIn("trajectory-analyzer", NON_EXECUTING_AGENTS)

    def test_18_batch5_curriculum_builder(self):
        """Batch 5: curriculum-builder writes curriculum tasks, has no run_command."""
        tools = self.get_agent_tools("curriculum-builder")
        self.assertNotIn("run_command", tools)
        self.assertIn("write_to_file", tools)
        self.assertNotIn("invoke_subagent", tools)
        self.assertIn("curriculum-builder", NON_EXECUTING_AGENTS)

    def test_19_batch5_knowledge_curator(self):
        """Batch 5: knowledge-curator stages lessons/exemplars, has no run_command."""
        tools = self.get_agent_tools("knowledge-curator")
        self.assertNotIn("run_command", tools)
        self.assertIn("write_to_file", tools)
        self.assertNotIn("invoke_subagent", tools)
        self.assertIn("knowledge-curator", NON_EXECUTING_AGENTS)

    def test_20_batch5_skill_evolver(self):
        """Batch 5: skill-evolver stages candidate diffs, has no run_command."""
        tools = self.get_agent_tools("skill-evolver")
        self.assertNotIn("run_command", tools)
        self.assertIn("write_to_file", tools)
        self.assertNotIn("invoke_subagent", tools)
        self.assertIn("skill-evolver", NON_EXECUTING_AGENTS)

    def test_21_batch5_evaluation_agent(self):
        """Batch 5: evaluation-agent is an execution test runner with run_command."""
        tools = self.get_agent_tools("evaluation-agent")
        self.assertIn("run_command", tools)
        self.assertIn("write_to_file", tools)
        self.assertNotIn("invoke_subagent", tools)

    # =========================================================================
    # Universal Invariants across All Batches
    # =========================================================================
    def test_22_zero_command_execution_policy(self):
        """Verifies zero agent frontmatters contain forbidden commandExecutionPolicy."""
        for item in sorted(os.listdir(AGENTS_DIR)):
            folder = os.path.join(AGENTS_DIR, item)
            if os.path.isdir(folder):
                agent_file = os.path.join(folder, "agent.md")
                if os.path.isfile(agent_file):
                    with open(agent_file, "r", encoding="utf-8") as f:
                        fm, _, _ = parse_yaml_frontmatter(f.read())
                    self.assertNotIn(
                        "commandExecutionPolicy",
                        fm,
                        f"Agent {item} contains forbidden commandExecutionPolicy"
                    )
                    self.assertNotIn(
                        "command_execution_policy",
                        fm,
                        f"Agent {item} contains forbidden command_execution_policy"
                    )

    def test_23_all_symlinks_resolve_canonically(self):
        """Verifies all agent symlinks resolve to <agent>/agent.md."""
        for item in sorted(os.listdir(AGENTS_DIR)):
            folder = os.path.join(AGENTS_DIR, item)
            if os.path.isdir(folder):
                symlink = os.path.join(AGENTS_DIR, f"{item}.md")
                self.assertTrue(os.path.islink(symlink), f"Missing symlink for {item}: {symlink}")
                self.assertEqual(
                    os.readlink(symlink),
                    f"{item}/agent.md",
                    f"Invalid symlink target for {symlink}"
                )


if __name__ == "__main__":
    unittest.main()
