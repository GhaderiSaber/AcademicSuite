#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_all_31_agent_guards.py — Verification of 1:1 Dedicated Lifecycle Hook Guards for all 31 Agents.

Validates:
1. Completeness: All 31 agents have dedicated <snake>_guard.py and <snake>_hook.json.
2. Hook Dispatcher: hook_dispatcher.py AGENT_GUARD_MAP contains all 31 agents.
3. Frontmatter: All 31 agent.md files declare their dedicated hook in YAML frontmatter.
4. Functional Verification: Specific invariant enforcement across individual guards.
"""

import os
import sys
import json
import tempfile
import unittest
import importlib

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents", "agents")
AGENTS_HOOKS_DIR = os.path.join(ROOT_DIR, ".agents", "hooks", "agents")
HOOKS_DIR = os.path.join(ROOT_DIR, ".agents", "hooks")

for p in (ROOT_DIR, AGENTS_DIR, AGENTS_HOOKS_DIR, HOOKS_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

import hook_dispatcher

ALL_31_AGENTS = [
    "academic-challenger",
    "academic-orchestrator",
    "academic-writer",
    "behavior-analyst",
    "curriculum-builder",
    "data-agent",
    "data-curator",
    "digital-saber",
    "evaluation-agent",
    "evidence-auditor",
    "final-judge",
    "intervention-designer",
    "journal-strategist",
    "knowledge-curator",
    "literature-expert",
    "longitudinal-modmed-expert",
    "meta-analyst",
    "methodology-expert",
    "project-organizer",
    "psychometric-expert",
    "qualitative-analyst",
    "research-agent",
    "results-auditor",
    "skill-evolver",
    "statistical-auditor",
    "statistical-expert",
    "statistics-agent",
    "test-orchestrator",
    "test-worker",
    "trajectory-analyzer",
    "validation-agent",
]


class TestDedicatedGuardsCompleteness(unittest.TestCase):
    """Verifies that all 31 agents have dedicated 1:1 guards, hook JSONs, and frontmatter."""

    def test_total_agents_count(self):
        self.assertEqual(len(ALL_31_AGENTS), 31)

    def test_all_guard_python_modules_exist_and_importable(self):
        for agent_kebab in ALL_31_AGENTS:
            snake = agent_kebab.replace("-", "_")
            mod_name = f"{snake}_guard"
            py_file = os.path.join(AGENTS_HOOKS_DIR, f"{mod_name}.py")
            self.assertTrue(os.path.exists(py_file), f"Missing guard file: {py_file}")
            
            # Module must import and have handle_pre_tool_use and handle_stop
            mod = importlib.import_module(mod_name)
            self.assertTrue(hasattr(mod, "handle_pre_tool_use"), f"{mod_name} missing handle_pre_tool_use")
            self.assertTrue(hasattr(mod, "handle_stop"), f"{mod_name} missing handle_stop")

    def test_all_hook_json_files_exist_and_valid(self):
        for agent_kebab in ALL_31_AGENTS:
            snake = agent_kebab.replace("-", "_")
            json_file = os.path.join(AGENTS_HOOKS_DIR, f"{snake}_hook.json")
            self.assertTrue(os.path.exists(json_file), f"Missing hook json: {json_file}")
            
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            guard_key = f"{agent_kebab}-guard"
            self.assertIn(guard_key, data, f"{json_file} missing key {guard_key}")
            self.assertIn("PreToolUse", data[guard_key])
            self.assertIn("Stop", data[guard_key])
            
            # Verify command points to its dedicated guard
            cmd = data[guard_key]["PreToolUse"][0]["hooks"][0]["command"]
            self.assertIn(f"{snake}_guard.py", cmd)

    def test_all_agent_md_frontmatter_references_dedicated_hook(self):
        for agent_kebab in ALL_31_AGENTS:
            snake = agent_kebab.replace("-", "_")
            md_path = os.path.join(AGENTS_DIR, agent_kebab, "agent.md")
            self.assertTrue(os.path.exists(md_path), f"Missing agent.md: {md_path}")
            
            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read()
            parts = content.split("---", 2)
            self.assertGreaterEqual(len(parts), 3, f"{agent_kebab}/agent.md missing frontmatter")
            fm = parts[1]
            expected_ref = f".agents/hooks/agents/{snake}_hook.json"
            self.assertIn(expected_ref, fm, f"{agent_kebab}/agent.md frontmatter does not reference {expected_ref}")

    def test_hook_dispatcher_guard_map_contains_all_31_agents(self):
        guard_map = hook_dispatcher.AGENT_GUARD_MAP
        self.assertEqual(len(guard_map), 31, f"Expected 31 mappings in AGENT_GUARD_MAP, got {len(guard_map)}")
        for agent_kebab in ALL_31_AGENTS:
            snake = agent_kebab.replace("-", "_")
            expected_mod = f"{snake}_guard"
            self.assertEqual(guard_map.get(agent_kebab), expected_mod, f"Mismatch for {agent_kebab}")


class TestIndividualDedicatedGuardsBehavior(unittest.TestCase):
    """Tests functional invariant enforcement for newly created dedicated guards."""

    def test_research_agent_guard(self):
        import research_agent_guard
        # Blocks invoke_subagent
        res = research_agent_guard.handle_pre_tool_use({"toolCall": {"name": "invoke_subagent", "args": {}}})
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Directive 12", res.get("reason", ""))
        
        # Blocks script without view_file
        res = research_agent_guard.handle_pre_tool_use({
            "toolCall": {"name": "run_command", "args": {"CommandLine": "python3 .agents/skills/gpower/scripts/calc.py"}}
        })
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Directive 1", res.get("reason", ""))

        # Stop blocks temporal hallucination
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "The year is 2023."}) + "\n")
            tpath = tf.name
        try:
            res = research_agent_guard.handle_stop({"transcriptPath": tpath})
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Directive 15", res.get("reason", ""))
        finally:
            if os.path.exists(tpath): os.unlink(tpath)

    def test_literature_expert_guard(self):
        import literature_expert_guard
        # Blocks invoke_subagent
        res = literature_expert_guard.handle_pre_tool_use({"toolCall": {"name": "invoke_subagent", "args": {}}})
        self.assertEqual(res.get("decision"), "deny")
        
        # Blocks mutating 03_deliverables
        res = literature_expert_guard.handle_pre_tool_use({
            "toolCall": {"name": "write_to_file", "args": {"TargetFile": "03_deliverables/Chapter_2.docx"}}
        })
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Literature Source Boundary", res.get("reason", ""))

        # Stop flags ghost citations
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "Article doi: 10.1234/ghost"}) + "\n")
            tpath = tf.name
        try:
            res = literature_expert_guard.handle_stop({"transcriptPath": tpath})
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Directive 14", res.get("reason", ""))
        finally:
            if os.path.exists(tpath): os.unlink(tpath)

    def test_data_curator_guard(self):
        import data_curator_guard
        # Blocks mutating raw data
        res = data_curator_guard.handle_pre_tool_use({
            "toolCall": {"name": "write_to_file", "args": {"TargetFile": "01_raw_inputs/data.xlsx"}}
        })
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Raw Data Protection", res.get("reason", ""))

        # Blocks creating scripts in root
        with tempfile.TemporaryDirectory() as ws:
            res = data_curator_guard.handle_pre_tool_use({
                "toolCall": {"name": "write_to_file", "args": {"TargetFile": os.path.join(ws, "clean.py")}},
                "workspacePaths": [ws]
            })
            self.assertEqual(res.get("decision"), "deny")
            self.assertIn("Directive 23", res.get("reason", ""))

    def test_qualitative_analyst_guard(self):
        import qualitative_analyst_guard
        # Blocks invoke_subagent
        res = qualitative_analyst_guard.handle_pre_tool_use({"toolCall": {"name": "invoke_subagent", "args": {}}})
        self.assertEqual(res.get("decision"), "deny")

        # Blocks creating root scripts
        with tempfile.TemporaryDirectory() as ws:
            res = qualitative_analyst_guard.handle_pre_tool_use({
                "toolCall": {"name": "write_to_file", "args": {"TargetFile": os.path.join(ws, "analyze.py")}},
                "workspacePaths": [ws]
            })
            self.assertEqual(res.get("decision"), "deny")

    def test_intervention_designer_guard(self):
        import intervention_designer_guard
        # Blocks invoke_subagent
        res = intervention_designer_guard.handle_pre_tool_use({"toolCall": {"name": "invoke_subagent", "args": {}}})
        self.assertEqual(res.get("decision"), "deny")
        
        # Blocks run_command
        res = intervention_designer_guard.handle_pre_tool_use({"toolCall": {"name": "run_command", "args": {"CommandLine": "ls"}}})
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Capability Boundary", res.get("reason", ""))

    def test_journal_strategist_guard(self):
        import journal_strategist_guard
        # Blocks invoke_subagent
        res = journal_strategist_guard.handle_pre_tool_use({"toolCall": {"name": "invoke_subagent", "args": {}}})
        self.assertEqual(res.get("decision"), "deny")
        
        # Blocks run_command
        res = journal_strategist_guard.handle_pre_tool_use({"toolCall": {"name": "run_command", "args": {"CommandLine": "ls"}}})
        self.assertEqual(res.get("decision"), "deny")

    def test_meta_analyst_guard(self):
        import meta_analyst_guard
        # Blocks invoke_subagent
        res = meta_analyst_guard.handle_pre_tool_use({"toolCall": {"name": "invoke_subagent", "args": {}}})
        self.assertEqual(res.get("decision"), "deny")

        # Stop flags p = .000
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "Meta analysis found p = .000."}) + "\n")
            tpath = tf.name
        try:
            res = meta_analyst_guard.handle_stop({"transcriptPath": tpath})
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Directive 4", res.get("reason", ""))
        finally:
            if os.path.exists(tpath): os.unlink(tpath)

    def test_longitudinal_modmed_expert_guard(self):
        import longitudinal_modmed_expert_guard
        # Blocks invoke_subagent
        res = longitudinal_modmed_expert_guard.handle_pre_tool_use({"toolCall": {"name": "invoke_subagent", "args": {}}})
        self.assertEqual(res.get("decision"), "deny")

        # Stop flags naked decimal
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "ضریب میانجیگری برابر .۳۵ است."}) + "\n")
            tpath = tf.name
        try:
            res = longitudinal_modmed_expert_guard.handle_stop({"transcriptPath": tpath})
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Directive 4", res.get("reason", ""))
        finally:
            if os.path.exists(tpath): os.unlink(tpath)

    def test_digital_saber_guard(self):
        import digital_saber_guard
        # Blocks file mutations and shell
        res = digital_saber_guard.handle_pre_tool_use({"toolCall": {"name": "write_to_file", "args": {"TargetFile": "a.txt"}}})
        self.assertEqual(res.get("decision"), "deny")
        res = digital_saber_guard.handle_pre_tool_use({"toolCall": {"name": "run_command", "args": {"CommandLine": "ls"}}})
        self.assertEqual(res.get("decision"), "deny")

        # Stop blocks sycophancy
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "Great question! That is wonderful."}) + "\n")
            tpath = tf.name
        try:
            res = digital_saber_guard.handle_stop({"transcriptPath": tpath})
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Directive 13", res.get("reason", ""))
        finally:
            if os.path.exists(tpath): os.unlink(tpath)

        # Stop requires human gate for pricing
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "هزینه این پایان‌نامه ۲۰ میلیون تومان است."}) + "\n")
            tpath = tf.name
        try:
            res = digital_saber_guard.handle_stop({"transcriptPath": tpath})
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Human Gate Required", res.get("reason", ""))
        finally:
            if os.path.exists(tpath): os.unlink(tpath)

    def test_methodology_expert_guard(self):
        import methodology_expert_guard
        res = methodology_expert_guard.handle_pre_tool_use({"toolCall": {"name": "write_to_file", "args": {"TargetFile": "a.txt"}}})
        self.assertEqual(res.get("decision"), "deny")
        res = methodology_expert_guard.handle_pre_tool_use({"toolCall": {"name": "run_command", "args": {"CommandLine": "ls"}}})
        self.assertEqual(res.get("decision"), "deny")

    def test_statistical_expert_guard(self):
        import statistical_expert_guard
        res = statistical_expert_guard.handle_pre_tool_use({"toolCall": {"name": "write_to_file", "args": {"TargetFile": "a.txt"}}})
        self.assertEqual(res.get("decision"), "deny")
        res = statistical_expert_guard.handle_pre_tool_use({"toolCall": {"name": "run_command", "args": {"CommandLine": "ls"}}})
        self.assertEqual(res.get("decision"), "deny")

    def test_behavior_analyst_guard(self):
        import behavior_analyst_guard
        res = behavior_analyst_guard.handle_pre_tool_use({"toolCall": {"name": "run_command", "args": {"CommandLine": "ls"}}})
        self.assertEqual(res.get("decision"), "deny")
        res = behavior_analyst_guard.handle_pre_tool_use({"toolCall": {"name": "write_to_file", "args": {"TargetFile": "03_deliverables/doc.docx"}}})
        self.assertEqual(res.get("decision"), "deny")

    def test_curriculum_builder_guard(self):
        import curriculum_builder_guard
        res = curriculum_builder_guard.handle_pre_tool_use({"toolCall": {"name": "write_to_file", "args": {"TargetFile": "03_deliverables/ch.docx"}}})
        self.assertEqual(res.get("decision"), "deny")

    def test_evaluation_agent_guard(self):
        import evaluation_agent_guard
        res = evaluation_agent_guard.handle_pre_tool_use({"toolCall": {"name": "write_to_file", "args": {"TargetFile": "03_deliverables/ch.docx"}}})
        self.assertEqual(res.get("decision"), "deny")
        
        # Stop blocks unverified success claims
        with tempfile.NamedTemporaryFile("w+", delete=False, suffix=".jsonl") as tf:
            tf.write(json.dumps({"type": "PLANNER_RESPONSE", "content": "Improvement verified without issues."}) + "\n")
            tpath = tf.name
        try:
            res = evaluation_agent_guard.handle_stop({"transcriptPath": tpath})
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Evaluator Integrity", res.get("reason", ""))
        finally:
            if os.path.exists(tpath): os.unlink(tpath)

    def test_knowledge_curator_guard(self):
        import knowledge_curator_guard
        res = knowledge_curator_guard.handle_pre_tool_use({"toolCall": {"name": "write_to_file", "args": {"TargetFile": "03_deliverables/ch.docx"}}})
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Scoped Knowledge Invariant", res.get("reason", ""))

    def test_skill_evolver_guard(self):
        import skill_evolver_guard
        res = skill_evolver_guard.handle_pre_tool_use({"toolCall": {"name": "write_to_file", "args": {"TargetFile": ".agents/skills/sem/SKILL.md"}}})
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Candidate Safety Invariant", res.get("reason", ""))

    def test_trajectory_analyzer_guard(self):
        import trajectory_analyzer_guard
        res = trajectory_analyzer_guard.handle_pre_tool_use({"toolCall": {"name": "run_command", "args": {"CommandLine": "ls"}}})
        self.assertEqual(res.get("decision"), "deny")
        res = trajectory_analyzer_guard.handle_pre_tool_use({"toolCall": {"name": "write_to_file", "args": {"TargetFile": "a.txt"}}})
        self.assertEqual(res.get("decision"), "deny")

    def test_test_orchestrator_guard(self):
        import test_orchestrator_guard
        # Blocks run_command and write_to_file
        res = test_orchestrator_guard.handle_pre_tool_use({"toolCall": {"name": "run_command", "args": {"CommandLine": "ls"}}})
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Directive 20", res.get("reason", ""))
        res = test_orchestrator_guard.handle_pre_tool_use({"toolCall": {"name": "write_to_file", "args": {"TargetFile": "a.txt"}}})
        self.assertEqual(res.get("decision"), "deny")
        # Allows invoke_subagent
        res = test_orchestrator_guard.handle_pre_tool_use({"toolCall": {"name": "invoke_subagent", "args": {}}})
        self.assertEqual(res.get("decision"), "allow")

    def test_test_worker_guard(self):
        import test_worker_guard
        # Blocks invoke_subagent
        res = test_worker_guard.handle_pre_tool_use({"toolCall": {"name": "invoke_subagent", "args": {}}})
        self.assertEqual(res.get("decision"), "deny")
        self.assertIn("Directive 12", res.get("reason", ""))
        # Allows execution tools
        res = test_worker_guard.handle_pre_tool_use({"toolCall": {"name": "run_command", "args": {"CommandLine": "ls"}}})
        self.assertEqual(res.get("decision"), "allow")


if __name__ == "__main__":
    unittest.main()
