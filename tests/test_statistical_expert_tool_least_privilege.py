#!/usr/bin/env python3
"""
Regression test for ATK-10: Statistical Expert Executing Arbitrary Code.

Verifies that statistical-expert (Tier 2 Reasoning Authority) does NOT possess
terminal execution tools ('run_command') in its tools whitelist or contract.
"""

import os
import sys
import yaml
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)


class TestStatisticalExpertToolLeastPrivilege(unittest.TestCase):

    def test_statistical_expert_agent_md_lacks_run_command(self):
        """statistical-expert/agent.md must not include run_command in tools (ATK-10)."""
        agent_path = os.path.join(ROOT_DIR, ".agents", "agents", "statistical-expert", "agent.md")
        self.assertTrue(os.path.exists(agent_path), f"File not found: {agent_path}")

        with open(agent_path, "r", encoding="utf-8") as f:
            content = f.read()

        parts = content.split("---")
        self.assertGreaterEqual(len(parts), 3, "YAML frontmatter missing")
        frontmatter = yaml.safe_load(parts[1])
        tools = frontmatter.get("tools", [])

        self.assertNotIn("run_command", tools, "statistical-expert must NOT declare 'run_command' in tools whitelist")

    def test_statistical_expert_contract_lacks_run_command(self):
        """statistical-expert/contract.md must not list run_command under ALLOWED TOOLS."""
        contract_path = os.path.join(ROOT_DIR, ".agents", "agents", "statistical-expert", "contract.md")
        self.assertTrue(os.path.exists(contract_path), f"File not found: {contract_path}")

        with open(contract_path, "r", encoding="utf-8") as f:
            content = f.read()

        if "## ALLOWED TOOLS" in content:
            tools_section = content.split("## ALLOWED TOOLS")[1].split("##")[0]
            self.assertNotIn("run_command", tools_section, "contract.md must not include run_command")


if __name__ == "__main__":
    unittest.main()
