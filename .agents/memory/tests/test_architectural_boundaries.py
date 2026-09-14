#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_architectural_boundaries.py — Antigravity Sole Orchestrator & Architectural Boundary Tests
-----------------------------------------------------------------------------------------------
Enforces:
  1. Complete elimination of multi_agent_orchestrator.py from disk.
  2. Prevention of any Python classes or functions mocking Antigravity subagent orchestration.
  3. DigitalSaber.run_workflow unconditionally raises NotImplementedError directing to invoke_subagent.
  4. All 10 workflow specifications declare Antigravity Lead Agent as the sole orchestrator.
  5. All 14 subagent markdown definitions are configured for native invoke_subagent execution.
  6. transcript_and_rule_guard PreInvocation and Stop lifecycle hooks enforce Directive 12.1.
"""

import os
import sys
import ast
import json
import unittest

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.join(ROOT_DIR, ".agents", "verification"))


class TestArchitecturalBoundaries(unittest.TestCase):
    """Rigorous tests ensuring Antigravity is the sole leader and orchestrator."""

    def test_01_monolithic_orchestrator_does_not_exist(self):
        """Assert multi_agent_orchestrator.py is physically absent from the repository."""
        forbidden_path = os.path.join(
            ROOT_DIR, ".agents", "skills", "academic-suite-orchestrator", "scripts", "multi_agent_orchestrator.py"
        )
        self.assertFalse(
            os.path.exists(forbidden_path),
            f"VIOLATION: Forbidden file '{forbidden_path}' exists! Python cannot orchestrate subagents."
        )

    def test_02_no_python_script_implements_mock_orchestrator(self):
        """Scan all Python files to ensure no class or module simulates subagents or mocks Antigravity."""
        prohibited_class_names = [
            "MultiAgentOrchestrator",
            "SubagentOrchestrator",
            "AgentOrchestrator",
            "MockSubagentRunner"
        ]
        
        for root, dirs, files in os.walk(ROOT_DIR):
            if ".git" in root or "__pycache__" in root or ".venv" in root:
                continue
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                        file_content = f.read()

                    try:
                        tree = ast.parse(file_content, filename=file_path)
                        for node in ast.walk(tree):
                            if isinstance(node, ast.ClassDef):
                                self.assertNotIn(
                                    node.name,
                                    prohibited_class_names,
                                    f"Prohibited class '{node.name}' found in {file_path}. Python must not orchestrate agents."
                                )
                    except SyntaxError:
                        pass

                    if "ANTIGRAVITY_MULTI_AGENT" in file_content and "test" not in file and "guard" not in file:
                        self.fail(
                            f"Prohibited string 'ANTIGRAVITY_MULTI_AGENT' found in non-test file {file_path}. "
                            "Do not simulate Antigravity multi-agent execution in Python."
                        )

    def test_03_digital_saber_run_workflow_raises_not_implemented(self):
        """Assert that DigitalSaber.run_workflow cleanly rejects offline Python execution."""
        from digital_saber import DigitalSaber
        saber = DigitalSaber()
        
        workflows_to_test = [
            "chapter4",
            "journal_submission",
            "defense_presentation",
            "proposal",
            "scale_validation"
        ]
        
        for wf in workflows_to_test:
            with self.assertRaises(NotImplementedError) as ctx:
                saber.run_workflow(wf)
            err_msg = str(ctx.exception)
            self.assertIn("invoke_subagent", err_msg)
            self.assertIn("Directive 12", err_msg)

    def test_04_all_10_workflows_declare_antigravity_lead(self):
        """Assert all 10 workflow specifications declare Antigravity Lead Agent as the orchestrator."""
        workflows_dir = os.path.join(ROOT_DIR, ".agents", "workflows")
        expected_workflows = [
            "chapter2_literature.md",
            "chapter4.md",
            "chapter5.md",
            "defense_presentation.md",
            "intervention_protocol.md",
            "journal_submission.md",
            "proposal.md",
            "scale_validation.md",
            "thesis_assembly.md",
            "thesis_revision.md"
        ]

        for wf in expected_workflows:
            path = os.path.join(workflows_dir, wf)
            self.assertTrue(os.path.exists(path), f"Missing workflow file: {wf}")
            with open(path, "r", encoding="utf-8") as f:
                wf_content = f.read()
            self.assertTrue(
                "Antigravity" in wf_content or "invoke_subagent" in wf_content,
                f"Workflow spec {wf} must specify Antigravity-native orchestration."
            )

    def test_05_all_15_subagents_configured_for_native_invocation(self):
        """Assert all 15 subagent definitions exist and have valid YAML frontmatter for invoke_subagent."""
        agents_dir = os.path.join(ROOT_DIR, ".agents", "agents")
        expected_agents = [
            "academic-writer.md",
            "data-curator.md",
            "digital-saber.md",
            "evidence-auditor.md",
            "final-judge.md",
            "intervention-designer.md",
            "journal-strategist.md",
            "literature-expert.md",
            "meta-analyst.md",
            "methodology-expert.md",
            "psychometric-expert.md",
            "qualitative-analyst.md",
            "results-auditor.md",
            "statistical-auditor.md",
            "statistical-expert.md"
        ]
        
        self.assertEqual(len(os.listdir(agents_dir)), 15)
        for agent_file in expected_agents:
            path = os.path.join(agents_dir, agent_file)
            self.assertTrue(os.path.exists(path), f"Missing subagent file: {agent_file}")
            with open(path, "r", encoding="utf-8") as f:
                ag_content = f.read()
            self.assertTrue(ag_content.startswith("---"), f"Subagent {agent_file} missing YAML frontmatter.")
            self.assertIn("name:", ag_content)
            self.assertIn("description:", ag_content)

    def test_06_lifecycle_guard_pre_invocation_enforces_directive_12_1(self):
        """Verify transcript_and_rule_guard injects Directive 12.1 into PreInvocation."""
        import transcript_and_rule_guard
        res = transcript_and_rule_guard.handle_pre_invocation({})
        self.assertIn("injectSteps", res)
        ephemeral = res["injectSteps"][0]["ephemeralMessage"]
        self.assertIn("Sole Orchestrator Mandate", ephemeral)
        self.assertIn("Directive 12.1", ephemeral)
        self.assertIn("invoke_subagent", ephemeral)

    def test_07_lifecycle_guard_stop_blocks_forbidden_orchestrator_file(self):
        """Verify transcript_and_rule_guard Stop blocks turn completion if forbidden file exists."""
        import transcript_and_rule_guard
        fake_ws = os.path.join(ROOT_DIR, "tmp_test_ws")
        forbidden_dir = os.path.join(fake_ws, ".agents", "skills", "academic-suite-orchestrator", "scripts")
        os.makedirs(forbidden_dir, exist_ok=True)
        fake_orch = os.path.join(forbidden_dir, "multi_agent_orchestrator.py")
        with open(fake_orch, "w", encoding="utf-8") as f:
            f.write("# fake orchestrator")

        try:
            payload = {
                "workspacePaths": [fake_ws],
                "transcriptPath": None,
                "conversationId": "test-cid"
            }
            res = transcript_and_rule_guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Directive 12.1", res.get("reason", ""))
        finally:
            if os.path.exists(fake_orch):
                os.remove(fake_orch)
            import shutil
            if os.path.exists(fake_ws):
                shutil.rmtree(fake_ws)

    def test_08_lifecycle_guard_stop_blocks_uninvoked_multiagent_claims(self):
        """Verify transcript_and_rule_guard Stop blocks claims of multiagent execution when invoke_subagent was 0."""
        import transcript_and_rule_guard
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as tf:
            records = [
                {"type": "USER_INPUT", "content": "Run Chapter 4 analysis"},
                {
                    "type": "PLANNER_RESPONSE",
                    "content": "We have successfully executed a complete, multi-agent chapter 4 workflow.",
                    "tool_calls": [{"name": "run_command"}]
                }
            ]
            for r in records:
                tf.write(json.dumps(r) + "\n")
            t_path = tf.name

        try:
            payload = {
                "workspacePaths": [ROOT_DIR],
                "transcriptPath": t_path,
                "conversationId": "test-cid"
            }
            res = transcript_and_rule_guard.handle_stop(payload)
            self.assertEqual(res.get("decision"), "continue")
            self.assertIn("Directive 0 & Directive 12", res.get("reason", ""))
        finally:
            if os.path.exists(t_path):
                os.remove(t_path)


if __name__ == "__main__":
    unittest.main()
