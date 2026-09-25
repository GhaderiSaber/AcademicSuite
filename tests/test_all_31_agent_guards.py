#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_all_31_agent_guards.py — Verification of 1:1 Dedicated Lifecycle Hook Guards for all 31 Agents.

Validates:
1. Completeness: All 31 agents have dedicated <snake>_guard.py and <snake>_hook.json.
2. Native CLI Execution: All 31 agents' guard.py files execute cleanly via CLI.
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
HOOKS_DIR = os.path.join(ROOT_DIR, ".agents", "hooks")

for p in (ROOT_DIR, AGENTS_DIR, HOOKS_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)


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

# Pre-populate sys.modules directly from canonical ASAM guard files
for agent_kebab in ALL_31_AGENTS:
    guard_path = os.path.join(AGENTS_DIR, agent_kebab, "guard.py")
    if os.path.exists(guard_path):
        snake = agent_kebab.replace("-", "_")
        mod_name = f"{snake}_guard"
        spec = importlib.util.spec_from_file_location(mod_name, guard_path)
        if spec and spec.loader:
            mod = importlib.util.module_from_spec(spec)
            sys.modules[mod_name] = mod
            spec.loader.exec_module(mod)


class TestDedicatedGuardsCompleteness(unittest.TestCase):
    """Verifies that all 31 agents have dedicated 1:1 guards, hook JSONs, and frontmatter."""

    def test_total_agents_count(self):
        self.assertEqual(len(ALL_31_AGENTS), 31)

    def test_all_guard_python_modules_exist_and_importable(self):
        for agent_kebab in ALL_31_AGENTS:
            py_file = os.path.join(AGENTS_DIR, agent_kebab, "guard.py")
            self.assertTrue(os.path.exists(py_file), f"Missing guard file: {py_file}")
            
            snake = agent_kebab.replace("-", "_")
            mod_name = f"{snake}_guard"
            mod = sys.modules.get(mod_name)
            self.assertIsNotNone(mod, f"{mod_name} not loaded")
            self.assertTrue(hasattr(mod, "handle_pre_tool_use"), f"{mod_name} missing handle_pre_tool_use")
            self.assertTrue(hasattr(mod, "handle_stop"), f"{mod_name} missing handle_stop")

    def test_all_hook_json_files_exist_and_valid(self):
        for agent_kebab in ALL_31_AGENTS:
            json_file = os.path.join(AGENTS_DIR, agent_kebab, "hooks.json")
            self.assertTrue(os.path.exists(json_file), f"Missing hook json: {json_file}")
            
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            guard_key = f"{agent_kebab}-guard"
            self.assertIn(guard_key, data, f"{json_file} missing key {guard_key}")
            self.assertIn("PreToolUse", data[guard_key])
            self.assertIn("Stop", data[guard_key])
            
            # Verify command points to its dedicated guard using full canonical path
            cmd = data[guard_key]["PreToolUse"][0]["hooks"][0]["command"]
            expected_cmd = f"python3 .agents/agents/{agent_kebab}/guard.py --event PreToolUse"
            self.assertEqual(
                cmd,
                expected_cmd,
                f"Command in {json_file} is not canonical non-shortpath: {cmd}"
            )

    def test_all_agent_md_frontmatter_references_dedicated_hook(self):
        for agent_kebab in ALL_31_AGENTS:
            md_path = os.path.join(AGENTS_DIR, agent_kebab, "agent.md")
            self.assertTrue(os.path.exists(md_path), f"Missing agent.md: {md_path}")
            
            with open(md_path, "r", encoding="utf-8") as f:
                content = f.read()
            parts = content.split("---", 2)
            self.assertGreaterEqual(len(parts), 3, f"{agent_kebab}/agent.md missing frontmatter")
            fm = parts[1]
            expected_ref = f".agents/agents/{agent_kebab}/hooks.json"
            self.assertIn(
                expected_ref,
                fm,
                f"{agent_kebab}/agent.md frontmatter does not reference canonical hook path: {expected_ref}"
            )

    def test_co_located_agent_module_integrity(self):
        """Verifies each agent directory contains agent.md, contract.md, guard.py, and hooks.json."""
        for agent_kebab in ALL_31_AGENTS:
            agent_dir = os.path.join(AGENTS_DIR, agent_kebab)
            self.assertTrue(os.path.isdir(agent_dir), f"Missing agent dir: {agent_dir}")
            for required_file in ("agent.md", "contract.md", "guard.py", "hooks.json"):
                fpath = os.path.join(agent_dir, required_file)
                self.assertTrue(os.path.exists(fpath), f"Agent {agent_kebab} missing {required_file} at {fpath}")

    def test_co_located_guards_direct_import_and_docstring(self):
        """Verifies each agent's guard.py is directly importable from its folder and has correct docstring."""
        import importlib.util
        for agent_kebab in ALL_31_AGENTS:
            guard_path = os.path.join(AGENTS_DIR, agent_kebab, "guard.py")
            self.assertTrue(os.path.exists(guard_path), f"Missing {guard_path}")

            # Verify docstring header matches .agents/agents/<agent>/guard.py
            with open(guard_path, "r", encoding="utf-8") as f:
                lines = [f.readline() for _ in range(6)]
            expected_header = f".agents/agents/{agent_kebab}/guard.py"
            self.assertIn(expected_header, lines[3], f"Docstring header mismatch in {guard_path}")

            # Verify direct importability
            spec = importlib.util.spec_from_file_location(f"direct_guard_{agent_kebab}", guard_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            self.assertTrue(hasattr(mod, "handle_pre_tool_use"), f"{guard_path} missing handle_pre_tool_use")
            self.assertTrue(hasattr(mod, "handle_stop"), f"{guard_path} missing handle_stop")

    def test_co_located_hooks_json_validity(self):
        """Verifies each hooks.json defines valid PreToolUse and Stop events referencing guard.py."""
        for agent_kebab in ALL_31_AGENTS:
            hpath = os.path.join(AGENTS_DIR, agent_kebab, "hooks.json")
            with open(hpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            guard_key = f"{agent_kebab}-guard"
            self.assertIn(guard_key, data, f"{hpath} missing {guard_key}")
            self.assertIn("PreToolUse", data[guard_key])
            self.assertIn("Stop", data[guard_key])
            cmd = data[guard_key]["PreToolUse"][0]["hooks"][0]["command"]
            self.assertIn("guard.py", cmd, f"Command does not reference guard.py in {hpath}")

    def test_all_31_agents_native_cli_execution(self):
        """Verifies each agent's guard.py can be invoked via CLI as defined in its hooks.json."""
        import subprocess
        for agent_kebab in ALL_31_AGENTS:
            guard_path = os.path.join(AGENTS_DIR, agent_kebab, "guard.py")
            payload = json.dumps({"toolCall": {"name": "view_file", "args": {"AbsolutePath": "/test"}}})
            proc = subprocess.run(
                ["python3", guard_path, "--event", "PreToolUse"],
                input=payload,
                capture_output=True,
                text=True,
                cwd=ROOT_DIR
            )
            self.assertEqual(proc.returncode, 0, f"CLI execution failed for {agent_kebab}: {proc.stderr}")
            res = json.loads(proc.stdout.strip())
            self.assertIn("decision", res, f"Invalid output from {agent_kebab}: {proc.stdout}")


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
