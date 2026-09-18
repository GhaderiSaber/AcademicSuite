#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_learning_subagents.py — Verification Suite for Bounded Learning Subagents

Verifies:
1. Discoverability: All six subagents exist as directories with agent.md, contract.md, and symlinks.
2. Frontmatter: subagent=true, mainAgent=false, valid model, tools, skills, agents: [].
3. Tool Name Validity: Every tool matches authoritative Antigravity tool names.
4. Least Privilege:
   - trajectory-analyzer and behavior-analyst are strictly read-only.
   - knowledge-curator, skill-evolver, and curriculum-builder cannot run commands.
   - Only evaluation-agent has run_command to execute test harnesses.
5. Non-Orchestrator Invariant: Zero subagent delegation tools or orchestration powers.
6. Contract Completeness: All 12 constitutional sections present in contract.md.
"""

import os
import sys
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents", "agents")

for p in ["/usr/lib/python3/dist-packages", "/usr/local/lib/python3/dist-packages"]:
    if os.path.exists(p) and p not in sys.path:
        sys.path.append(p)

try:
    import yaml
except ImportError:
    yaml = None

LEARNING_SUBAGENTS = [
    "trajectory-analyzer",
    "behavior-analyst",
    "knowledge-curator",
    "skill-evolver",
    "evaluation-agent",
    "curriculum-builder"
]

AUTHORITATIVE_ANTIGRAVITY_TOOLS = {
    "view_file",
    "list_dir",
    "grep_search",
    "find_by_name",
    "write_to_file",
    "replace_file_content",
    "run_command",
    "read_url_content",
    "search_web",
    "send_message",
    "invoke_subagent",
    "manage_subagents",
    "manage_task",
    "schedule",
    "ask_question",
    "call_mcp_tool",
    "list_resources",
    "read_resource",
    "generate_image"
}

REQUIRED_CONTRACT_SECTIONS = [
    "MISSION",
    "RESPONSIBILITIES",
    "NON-RESPONSIBILITIES",
    "INPUTS",
    "OUTPUTS",
    "ALLOWED TOOLS",
    "REQUIRED SKILLS",
    "FORBIDDEN ACTIONS",
    "HANDOFF FORMAT",
    "VALIDATION REQUIREMENTS",
    "COMPLETION CRITERIA",
    "FAILURE CONDITIONS"
]


class TestLearningSubagents(unittest.TestCase):
    """Authoritative test suite for the six continuous improvement learning subagents."""

    def _parse_frontmatter(self, file_path: str):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertTrue(content.startswith("---"), f"{file_path} must start with frontmatter delimiter ---")
        parts = content.split("---", 2)
        self.assertGreaterEqual(len(parts), 3, f"{file_path} must have closing frontmatter delimiter ---")
        raw_yaml = parts[1]

        if yaml is not None:
            data = yaml.safe_load(raw_yaml)
        else:
            # Robust fallback YAML frontmatter parser
            data = {}
            current_key = None
            for line in raw_yaml.splitlines():
                line = line.rstrip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith("  - "):
                    item = line[4:].strip()
                    if current_key and isinstance(data.get(current_key), list):
                        data[current_key].append(item)
                elif ":" in line and not line.startswith(" "):
                    k, v = line.split(":", 1)
                    k = k.strip()
                    v = v.strip()
                    current_key = k
                    if v == "" or v == ">-":
                        data[k] = "" if v == ">-" else []
                    elif v.startswith("[") and v.endswith("]"):
                        items = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
                        data[k] = items
                    elif v.lower() == "true":
                        data[k] = True
                    elif v.lower() == "false":
                        data[k] = False
                    elif v.isdigit():
                        data[k] = int(v)
                    else:
                        data[k] = v.strip("'\"")

        self.assertIsInstance(data, dict, f"Parsed frontmatter in {file_path} must be a dictionary")
        return data, parts[2]

    def test_01_all_six_learning_subagents_discoverable(self):
        """All six subagents must exist with directory, agent.md, contract.md, and symlink."""
        for name in LEARNING_SUBAGENTS:
            agent_dir = os.path.join(AGENTS_DIR, name)
            self.assertTrue(os.path.isdir(agent_dir), f"Subagent directory missing: {agent_dir}")

            agent_md = os.path.join(agent_dir, "agent.md")
            self.assertTrue(os.path.isfile(agent_md), f"agent.md missing for {name}")

            contract_md = os.path.join(agent_dir, "contract.md")
            self.assertTrue(os.path.isfile(contract_md), f"contract.md missing for {name}")

            symlink = os.path.join(AGENTS_DIR, f"{name}.md")
            self.assertTrue(os.path.islink(symlink), f"Symlink missing for {name}: {symlink}")
            target = os.readlink(symlink)
            self.assertEqual(target, f"{name}/agent.md", f"Symlink target incorrect for {name}")
            self.assertTrue(os.path.exists(symlink), f"Symlink for {name} is broken")

    def test_02_frontmatter_schema_validation(self):
        """Frontmatter must declare subagent: true, mainAgent: false, valid model, and non-empty tools/skills."""
        for name in LEARNING_SUBAGENTS:
            agent_md = os.path.join(AGENTS_DIR, name, "agent.md")
            fm, body = self._parse_frontmatter(agent_md)

            self.assertEqual(fm.get("name"), name)
            self.assertTrue(fm.get("subagent") is True, f"{name} must have subagent: true")
            self.assertTrue(fm.get("mainAgent") is False, f"{name} must have mainAgent: false")
            self.assertIn(fm.get("model"), ["flash", "pro"], f"{name} must specify valid model")
            self.assertIsInstance(fm.get("tools"), list, f"{name} tools must be a list")
            self.assertGreater(len(fm.get("tools")), 0, f"{name} must have at least one tool")
            self.assertIsInstance(fm.get("skills"), list, f"{name} skills must be a list")
            self.assertGreater(len(fm.get("skills")), 0, f"{name} must declare skills")
            self.assertEqual(fm.get("agents"), [], f"{name} must have agents: [] (non-orchestrator)")
            self.assertEqual(fm.get("mcpServers"), [], f"{name} must have mcpServers: []")

    def test_03_valid_tool_names_only(self):
        """Every tool declared in frontmatter must be an authoritative Antigravity tool."""
        for name in LEARNING_SUBAGENTS:
            agent_md = os.path.join(AGENTS_DIR, name, "agent.md")
            fm, _ = self._parse_frontmatter(agent_md)
            declared_tools = fm.get("tools", [])

            for t in declared_tools:
                self.assertIn(
                    t,
                    AUTHORITATIVE_ANTIGRAVITY_TOOLS,
                    f"Subagent '{name}' declares invalid/unknown tool: '{t}'"
                )

    def test_04_least_privilege_tool_enforcement(self):
        """Strict least privilege must be maintained across all 6 learning subagents."""
        for name in LEARNING_SUBAGENTS:
            agent_md = os.path.join(AGENTS_DIR, name, "agent.md")
            fm, _ = self._parse_frontmatter(agent_md)
            tools = set(fm.get("tools", []))

            # 1. trajectory-analyzer: strictly read-only
            if name == "trajectory-analyzer":
                self.assertEqual(
                    tools,
                    {"view_file", "list_dir", "grep_search", "find_by_name"},
                    "trajectory-analyzer must be strictly read-only"
                )

            # 2. behavior-analyst: strictly read-only
            elif name == "behavior-analyst":
                self.assertEqual(
                    tools,
                    {"view_file", "list_dir", "grep_search", "find_by_name"},
                    "behavior-analyst must be strictly read-only"
                )

            # 3. knowledge-curator: write_to_file allowed, but NO run_command
            elif name == "knowledge-curator":
                self.assertIn("write_to_file", tools)
                self.assertNotIn("run_command", tools)
                self.assertNotIn("replace_file_content", tools)

            # 4. skill-evolver: write_to_file allowed, but NO run_command and NO replace_file_content
            elif name == "skill-evolver":
                self.assertIn("write_to_file", tools)
                self.assertNotIn("run_command", tools)
                self.assertNotIn("replace_file_content", tools)

            # 5. curriculum-builder: write_to_file allowed, but NO run_command
            elif name == "curriculum-builder":
                self.assertIn("write_to_file", tools)
                self.assertNotIn("run_command", tools)

            # 6. evaluation-agent: ONLY evaluation agent has run_command (to run test runners)
            elif name == "evaluation-agent":
                self.assertIn("run_command", tools)
                self.assertIn("write_to_file", tools)

    def test_05_single_responsibility_and_non_orchestrator(self):
        """None of the learning subagents may act as general-purpose orchestrators."""
        orchestrator_tools = {"invoke_subagent", "manage_subagents", "send_message", "ask_question"}
        for name in LEARNING_SUBAGENTS:
            agent_md = os.path.join(AGENTS_DIR, name, "agent.md")
            fm, body = self._parse_frontmatter(agent_md)
            tools = set(fm.get("tools", []))

            intersection = tools.intersection(orchestrator_tools)
            self.assertEqual(
                len(intersection),
                0,
                f"Learning subagent '{name}' must NOT have orchestration tools: {intersection}"
            )
            self.assertEqual(fm.get("agents"), [], f"{name} must not declare delegatee subagents")
            self.assertIn("Single Primary Responsibility", body, f"{name} must articulate single responsibility")

    def test_06_contract_sections_compliance(self):
        """All 12 constitutional sections must be present in contract.md for each subagent."""
        for name in LEARNING_SUBAGENTS:
            contract_md = os.path.join(AGENTS_DIR, name, "contract.md")
            with open(contract_md, "r", encoding="utf-8") as f:
                content = f.read()

            for section in REQUIRED_CONTRACT_SECTIONS:
                self.assertIn(
                    section,
                    content,
                    f"Contract for '{name}' is missing constitutional section: '{section}'"
                )


if __name__ == "__main__":
    unittest.main()
