#!/usr/bin/env python3
"""
Regression test for ATK-14: Factory Regeneration of Deprecated Architecture.

Verifies that factory/agent_factory.py maintains an explicit blocklist of retired agents
and raises AgentValidationError if generation of a retired agent is attempted.
"""

import os
import sys
import shutil
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from factory.agent_factory import create_agent, validate_agent_spec, AgentSpec, AgentValidationError, RETIRED_AGENTS


class TestRetiredAgentFactory(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="test_factory_retired_")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_writing_agent_creation_is_blocked(self):
        """Attempting to create retired 'writing-agent' raises AgentValidationError (ATK-14)."""
        with self.assertRaises(AgentValidationError) as ctx:
            create_agent(
                name="writing-agent",
                description="Legacy Chapter Writer Agent",
                role="Legacy Chapter Writer",
                skills=["chapter-4-writing"],
                target_dir=self.temp_dir,
                validate=True
            )
        self.assertIn("retired", str(ctx.exception).lower())

    def test_retired_agents_in_validate_spec(self):
        """Validating any retired agent spec directly raises AgentValidationError."""
        for retired in RETIRED_AGENTS:
            spec = AgentSpec(
                name=retired,
                description=f"Retired agent spec for {retired}",
                role="Retired Agent Role",
                tools=["view_file"]
            )
            with self.assertRaises(AgentValidationError) as ctx:
                validate_agent_spec(spec)
            self.assertIn("retired", str(ctx.exception).lower())

    def test_active_agent_spec_passes(self):
        """Valid non-retired agent passes validation successfully."""
        spec = AgentSpec(
            name="new-analyst",
            description="Specialized Statistical Analyst Subagent",
            role="Specialized Statistical Analyst",
            tools=["view_file", "write_to_file"],
            skills=["sem"]
        )
        # Should not raise
        validate_agent_spec(spec)


if __name__ == "__main__":
    unittest.main()
