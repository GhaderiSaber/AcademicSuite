#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_agent_capability_validator.py — Acceptance Suite for Agent Capability Validator (Phase 13)

Verifies:
1. Every Agent checks: frontmatter valid, tools recognized, mainAgent valid, subagent valid, skills valid, MCP references valid.
2. Academic-Orchestrator: NO run_command, NO write_to_file, NO edit_file, NO replace_file_content, YES invoke_subagent.
3. Execution Workers: run_command allowed and required.
4. Read-Only Agents: no write tools, no execution tools.
5. Auditors: no execution unless explicitly justified.
"""

import os
import sys
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from validators.agent_integrity import (
    AgentIntegrityValidator,
    AgentCapabilityValidator,
    parse_yaml_frontmatter,
    AGENTS_DIR,
    SKILLS_DIR,
)


class TestAgentCapabilityValidator(unittest.TestCase):
    """Phase 13 Capability Boundaries & Least-Privilege Enforcement Suite."""

    def test_01_all_workspace_agents_satisfy_capability_boundaries(self):
        """All 28 workspace agents must satisfy 100% of capability boundary rules."""
        validator = AgentCapabilityValidator(agents_dir=AGENTS_DIR, skills_dir=SKILLS_DIR)
        result = validator.run_validation()
        self.assertEqual(result["overall_verdict"], "PASS")
        self.assertEqual(result["errors"], 0)
        self.assertEqual(result["agents_validated"], 28)

    def test_02_orchestrator_forbids_run_command(self):
        """Academic-Orchestrator must fail if run_command is present."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_agents = os.path.join(tmpdir, "agents")
            tmp_skills = os.path.join(tmpdir, "skills")
            orch_dir = os.path.join(tmp_agents, "academic-orchestrator")
            os.makedirs(orch_dir, exist_ok=True)
            os.makedirs(tmp_skills, exist_ok=True)

            content = (
                "---\n"
                "name: academic-orchestrator\n"
                "description: Master academic conductor.\n"
                "mainAgent: true\n"
                "subagent: true\n"
                "tools:\n"
                "  - invoke_subagent\n"
                "  - view_file\n"
                "  - run_command\n"  # FORBIDDEN
                "---\n"
            )
            with open(os.path.join(orch_dir, "agent.md"), "w") as f:
                f.write(content)

            validator = AgentCapabilityValidator(agents_dir=tmp_agents, skills_dir=tmp_skills, enforce_capability_policy=False)
            res = validator.run_validation()
            self.assertEqual(res["overall_verdict"], "FAIL")
            self.assertTrue(any(i["check"] == "orchestrator_capabilities" and "run_command" in i["message"] for i in res["issues"]))

    def test_03_orchestrator_forbids_file_modification(self):
        """Academic-Orchestrator must fail if write_to_file, replace_file_content, or edit_file is present."""
        for forbidden_tool in ["write_to_file", "replace_file_content", "edit_file"]:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_agents = os.path.join(tmpdir, "agents")
                tmp_skills = os.path.join(tmpdir, "skills")
                orch_dir = os.path.join(tmp_agents, "academic-orchestrator")
                os.makedirs(orch_dir, exist_ok=True)
                os.makedirs(tmp_skills, exist_ok=True)

                content = (
                    "---\n"
                    "name: academic-orchestrator\n"
                    "description: Master academic conductor.\n"
                    "mainAgent: true\n"
                    "subagent: true\n"
                    "tools:\n"
                    "  - invoke_subagent\n"
                    "  - view_file\n"
                    f"  - {forbidden_tool}\n"
                    "---\n"
                )
                with open(os.path.join(orch_dir, "agent.md"), "w") as f:
                    f.write(content)

                validator = AgentCapabilityValidator(agents_dir=tmp_agents, skills_dir=tmp_skills, enforce_capability_policy=False)
                res = validator.run_validation()
                self.assertEqual(res["overall_verdict"], "FAIL")
                self.assertTrue(
                    any(i["check"] == "orchestrator_capabilities" and forbidden_tool in i["message"] for i in res["issues"]),
                    f"Expected orchestrator_capabilities violation for {forbidden_tool}"
                )

    def test_04_orchestrator_requires_invoke_subagent(self):
        """Academic-Orchestrator must declare invoke_subagent."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_agents = os.path.join(tmpdir, "agents")
            tmp_skills = os.path.join(tmpdir, "skills")
            orch_dir = os.path.join(tmp_agents, "academic-orchestrator")
            os.makedirs(orch_dir, exist_ok=True)
            os.makedirs(tmp_skills, exist_ok=True)

            content = (
                "---\n"
                "name: academic-orchestrator\n"
                "description: Master academic conductor.\n"
                "mainAgent: true\n"
                "subagent: true\n"
                "tools:\n"
                "  - view_file\n"
                "  - list_dir\n"
                "---\n"
            )
            with open(os.path.join(orch_dir, "agent.md"), "w") as f:
                f.write(content)

            validator = AgentCapabilityValidator(agents_dir=tmp_agents, skills_dir=tmp_skills, enforce_capability_policy=False)
            res = validator.run_validation()
            self.assertEqual(res["overall_verdict"], "FAIL")
            self.assertTrue(any(i["check"] == "orchestrator_capabilities" and "invoke_subagent" in i["message"] for i in res["issues"]))

    def test_05_execution_worker_must_have_run_command(self):
        """Execution worker missing run_command must fail validation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_agents = os.path.join(tmpdir, "agents")
            tmp_skills = os.path.join(tmpdir, "skills")
            worker_dir = os.path.join(tmp_agents, "statistics-agent")
            os.makedirs(worker_dir, exist_ok=True)
            os.makedirs(tmp_skills, exist_ok=True)

            # statistics-agent missing run_command
            content = (
                "---\n"
                "name: statistics-agent\n"
                "description: Statistical execution worker.\n"
                "mainAgent: false\n"
                "subagent: true\n"
                "tools:\n"
                "  - view_file\n"
                "  - write_to_file\n"
                "---\n"
            )
            with open(os.path.join(worker_dir, "agent.md"), "w") as f:
                f.write(content)

            validator = AgentCapabilityValidator(agents_dir=tmp_agents, skills_dir=tmp_skills, enforce_capability_policy=False)
            res = validator.run_validation()
            self.assertEqual(res["overall_verdict"], "FAIL")
            self.assertTrue(any(i["check"] == "execution_workers_capabilities" for i in res["issues"]))

    def test_06_read_only_agents_forbid_write_and_execution(self):
        """Read-only agent (e.g. behavior-analyst) must fail if given write tools or execution."""
        for illegal_tool in ["write_to_file", "replace_file_content", "edit_file", "run_command"]:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_agents = os.path.join(tmpdir, "agents")
                tmp_skills = os.path.join(tmpdir, "skills")
                agent_dir = os.path.join(tmp_agents, "behavior-analyst")
                os.makedirs(agent_dir, exist_ok=True)
                os.makedirs(tmp_skills, exist_ok=True)

                content = (
                    "---\n"
                    "name: behavior-analyst\n"
                    "description: Read-only diagnostic agent.\n"
                    "mainAgent: false\n"
                    "subagent: true\n"
                    "tools:\n"
                    "  - view_file\n"
                    f"  - {illegal_tool}\n"
                    "---\n"
                )
                with open(os.path.join(agent_dir, "agent.md"), "w") as f:
                    f.write(content)

                validator = AgentCapabilityValidator(agents_dir=tmp_agents, skills_dir=tmp_skills, enforce_capability_policy=False)
                res = validator.run_validation()
                self.assertEqual(res["overall_verdict"], "FAIL")
                self.assertTrue(
                    any(i["check"] == "read_only_agents_capabilities" for i in res["issues"]),
                    f"Expected read_only_agents_capabilities violation for {illegal_tool}"
                )

    def test_07_auditors_forbid_execution_without_justification(self):
        """Auditors (e.g. results-auditor, evidence-auditor) cannot declare run_command without justification."""
        for auditor_name in ["results-auditor", "evidence-auditor", "academic-challenger", "final-judge"]:
            with tempfile.TemporaryDirectory() as tmpdir:
                tmp_agents = os.path.join(tmpdir, "agents")
                tmp_skills = os.path.join(tmpdir, "skills")
                aud_dir = os.path.join(tmp_agents, auditor_name)
                os.makedirs(aud_dir, exist_ok=True)
                os.makedirs(tmp_skills, exist_ok=True)

                content = (
                    f"---\n"
                    f"name: {auditor_name}\n"
                    f"description: Auditor inspecting artifacts.\n"
                    f"mainAgent: false\n"
                    f"subagent: true\n"
                    f"tools:\n"
                    f"  - view_file\n"
                    f"  - write_to_file\n"
                    f"  - run_command\n"  # FORBIDDEN for auditor without justification
                    f"---\n"
                )
                with open(os.path.join(aud_dir, "agent.md"), "w") as f:
                    f.write(content)

                validator = AgentCapabilityValidator(agents_dir=tmp_agents, skills_dir=tmp_skills, enforce_capability_policy=False)
                res = validator.run_validation()
                self.assertEqual(res["overall_verdict"], "FAIL")
                self.assertTrue(
                    any(i["check"] == "auditors_capabilities" for i in res["issues"]),
                    f"Expected auditors_capabilities violation for {auditor_name}"
                )

    def test_08_universal_agent_checks(self):
        """All 6 universal checks (frontmatter, tools, mainAgent, subagent, skills, MCP) must function."""
        # 1. Invalid tools recognized
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_agents = os.path.join(tmpdir, "agents")
            os.makedirs(os.path.join(tmp_agents, "test-agent"), exist_ok=True)
            with open(os.path.join(tmp_agents, "test-agent", "agent.md"), "w") as f:
                f.write("---\nname: test-agent\ndescription: Test agent description.\ntools:\n  - bogus_tool_xyz\n---\n")
            v = AgentCapabilityValidator(agents_dir=tmp_agents, skills_dir=tmpdir, enforce_capability_policy=False)
            res = v.run_validation()
            self.assertEqual(res["overall_verdict"], "FAIL")
            self.assertTrue(any(i["check"] == "valid_tool_names" for i in res["issues"]))

        # 2. Invalid skills
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_agents = os.path.join(tmpdir, "agents")
            os.makedirs(os.path.join(tmp_agents, "test-agent"), exist_ok=True)
            with open(os.path.join(tmp_agents, "test-agent", "agent.md"), "w") as f:
                f.write("---\nname: test-agent\ndescription: Test agent description.\nskills:\n  - nonexistent_skill\n---\n")
            v = AgentCapabilityValidator(agents_dir=tmp_agents, skills_dir=tmpdir, enforce_capability_policy=False)
            res = v.run_validation()
            self.assertEqual(res["overall_verdict"], "FAIL")
            self.assertTrue(any(i["check"] == "valid_skill_references" for i in res["issues"]))

        # 3. Competing mainAgent: true
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_agents = os.path.join(tmpdir, "agents")
            os.makedirs(os.path.join(tmp_agents, "academic-orchestrator"), exist_ok=True)
            os.makedirs(os.path.join(tmp_agents, "competing-orchestrator"), exist_ok=True)
            with open(os.path.join(tmp_agents, "academic-orchestrator", "agent.md"), "w") as f:
                f.write("---\nname: academic-orchestrator\ndescription: Master orchestrator.\nmainAgent: true\nsubagent: true\ntools:\n  - invoke_subagent\n---\n")
            with open(os.path.join(tmp_agents, "competing-orchestrator", "agent.md"), "w") as f:
                f.write("---\nname: competing-orchestrator\ndescription: Competing orchestrator.\nmainAgent: true\nsubagent: true\n---\n")
            v = AgentCapabilityValidator(agents_dir=tmp_agents, skills_dir=tmpdir, enforce_capability_policy=False)
            res = v.run_validation()
            self.assertEqual(res["overall_verdict"], "FAIL")
            self.assertTrue(any(i["check"] == "canonical_mainAgent_entry_point" for i in res["issues"]))


if __name__ == "__main__":
    unittest.main()
