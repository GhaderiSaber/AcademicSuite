#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_agent_capabilities_policy.py — Machine-Checkable Capability Policy Test Suite

Validates Phase 12 Single Source of Truth (contracts/agents/agent_capabilities.yaml):
1. Manifest Existence & Schema Integrity (validate_policy_schema).
2. 100% Compliance across all 28 canonical agents on disk.
3. Strict enforcement of least-privilege tool allocation (planners, auditors, workers, orchestrator).
4. Deterministic failure behavior on contract violations (forbidden tool, missing required tool, invalid mainAgent/subagent, unauthorized delegation).
5. Integration with AgentIntegrityValidator.
"""

import os
import sys
import copy
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from contracts.agents.capability_policy import (
    load_capability_policy,
    get_agent_policy,
    get_all_policy_agents,
    validate_agent_against_policy,
    validate_policy_schema,
    DEFAULT_POLICY_PATH,
)
from validators.agent_integrity import (
    AgentIntegrityValidator,
    parse_yaml_frontmatter,
    AGENTS_DIR,
)


class TestAgentCapabilitiesPolicy(unittest.TestCase):
    """Verifies that agent_capabilities.yaml serves as the authoritative machine-checkable SSOT."""

    def setUp(self):
        self.policy = load_capability_policy()
        self.policy_agents = get_all_policy_agents(self.policy)

    def test_01_manifest_exists_and_schema_is_valid(self):
        """contracts/agents/agent_capabilities.yaml must exist and pass schema validation."""
        self.assertTrue(os.path.isfile(DEFAULT_POLICY_PATH))
        self.assertEqual(self.policy.get("schema_version"), "1.0.0")
        self.assertIn("agents", self.policy)
        
        schema_issues = validate_policy_schema(self.policy)
        self.assertEqual(schema_issues, [], f"Schema issues found: {schema_issues}")

    def test_02_all_28_agents_registered_in_policy(self):
        """Exactly 28 production agents must be registered in the capability policy."""
        self.assertEqual(len(self.policy_agents), 28)
        expected = [
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
            "psychometric-expert",
            "qualitative-analyst",
            "research-agent",
            "results-auditor",
            "skill-evolver",
            "statistical-auditor",
            "statistical-expert",
            "statistics-agent",
            "trajectory-analyzer",
            "validation-agent",
        ]
        self.assertEqual(sorted(self.policy_agents), sorted(expected))

    def test_03_disk_agents_match_policy_100_percent(self):
        """Every single canonical agent on disk must match its policy specification with 0 issues."""
        for agent_name in self.policy_agents:
            agent_file = os.path.join(AGENTS_DIR, agent_name, "agent.md")
            self.assertTrue(os.path.isfile(agent_file), f"Missing agent.md for: {agent_name}")
            with open(agent_file, "r", encoding="utf-8") as f:
                content = f.read()
            fm, _, parse_err = parse_yaml_frontmatter(content)
            self.assertIsNone(parse_err, f"Frontmatter parse error for {agent_name}: {parse_err}")
            self.assertIsNotNone(fm)

            issues = validate_agent_against_policy(agent_name, fm, self.policy)
            self.assertEqual(issues, [], f"Policy violations for {agent_name}: {issues}")

    def test_04_canonical_entry_point_invariants(self):
        """Only academic-orchestrator may have mainAgent=True; all 27 others must have mainAgent=False."""
        orch = get_agent_policy("academic-orchestrator", self.policy)
        self.assertTrue(orch.get("mainAgent"))
        self.assertTrue(orch.get("subagent"))
        self.assertFalse(orch.get("can_execute_code"))
        self.assertFalse(orch.get("can_write_files"))
        self.assertIn("run_command", orch.get("forbidden", []))
        self.assertIn("write_to_file", orch.get("forbidden", []))
        self.assertIn("replace_file_content", orch.get("forbidden", []))

        for name in self.policy_agents:
            if name != "academic-orchestrator":
                spec = get_agent_policy(name, self.policy)
                self.assertFalse(spec.get("mainAgent"), f"{name} must have mainAgent=False")
                self.assertTrue(spec.get("subagent"), f"{name} must have subagent=True")

    def test_05_planners_and_auditors_lack_run_command(self):
        """Specialist planners and auditors must have can_execute_code=False and run_command in forbidden."""
        non_executors = [
            "methodology-expert",
            "statistical-expert",
            "evidence-auditor",
            "final-judge",
            "results-auditor",
            "academic-challenger",
            "journal-strategist",
            "intervention-designer",
            "curriculum-builder",
            "knowledge-curator",
            "skill-evolver",
            "behavior-analyst",
            "trajectory-analyzer",
        ]
        for name in non_executors:
            spec = get_agent_policy(name, self.policy)
            self.assertFalse(spec.get("can_execute_code"), f"{name} must not have can_execute_code")
            self.assertIn("run_command", spec.get("forbidden", []), f"{name} must forbid run_command")

    def test_06_execution_workers_have_run_command_required(self):
        """Class A execution workers must have can_execute_code=True and run_command in required."""
        execution_workers = [
            "data-agent",
            "data-curator",
            "statistics-agent",
            "psychometric-expert",
            "longitudinal-modmed-expert",
            "qualitative-analyst",
            "meta-analyst",
            "evaluation-agent",
            "validation-agent",
            "statistical-auditor",
            "research-agent",
            "literature-expert",
        ]
        for name in execution_workers:
            spec = get_agent_policy(name, self.policy)
            self.assertTrue(spec.get("can_execute_code"), f"{name} must have can_execute_code=True")
            self.assertIn("run_command", spec.get("required", []), f"{name} must require run_command")

    def test_07_academic_writer_has_bounded_docgen_scope(self):
        """academic-writer retains execution for docgen but is locked to execution_scope: docgen_only."""
        writer = get_agent_policy("academic-writer", self.policy)
        self.assertTrue(writer.get("can_execute_code"))
        self.assertEqual(writer.get("execution_scope"), "docgen_only")
        self.assertIn("run_command", writer.get("required", []))
        self.assertIn("write_to_file", writer.get("required", []))
        self.assertIn("replace_file_content", writer.get("required", []))
        self.assertIn("invoke_subagent", writer.get("forbidden", []))

    def test_08_violation_missing_required_tool_fails(self):
        """Omitting a required tool must trigger policy validation failure."""
        orch = copy.deepcopy(self.policy["agents"]["academic-orchestrator"])
        fm = {
            "name": "academic-orchestrator",
            "mainAgent": True,
            "subagent": True,
            "tools": ["view_file", "list_dir"],  # missing invoke_subagent, ask_question, etc.
        }
        issues = validate_agent_against_policy("academic-orchestrator", fm, self.policy)
        self.assertTrue(any("missing required tools" in i for i in issues))

    def test_09_violation_forbidden_tool_fails(self):
        """Declaring a forbidden tool must trigger policy validation failure."""
        fm = {
            "name": "statistical-expert",
            "mainAgent": False,
            "subagent": True,
            "tools": [
                "invoke_subagent", "manage_subagents", "send_message",
                "view_file", "list_dir", "grep_search", "find_by_name", "write_to_file",
                "run_command"  # FORBIDDEN for statistical-expert
            ],
        }
        issues = validate_agent_against_policy("statistical-expert", fm, self.policy)
        self.assertTrue(any("declares forbidden tools" in i for i in issues))
        self.assertTrue(any("run_command" in i for i in issues))

    def test_10_violation_unauthorized_delegation_fails(self):
        """Worker with can_delegate=False attempting to declare subagents must fail."""
        fm = {
            "name": "statistics-agent",
            "mainAgent": False,
            "subagent": True,
            "tools": [
                "view_file", "list_dir", "grep_search", "find_by_name",
                "write_to_file", "run_command"
            ],
            "agents": ["data-agent"],  # FORBIDDEN: statistics-agent cannot delegate
        }
        issues = validate_agent_against_policy("statistics-agent", fm, self.policy)
        self.assertTrue(any("can_delegate=False" in i for i in issues))

    def test_11_violation_specialist_main_agent_fails(self):
        """Specialist declaring mainAgent=True must fail policy check."""
        fm = {
            "name": "methodology-expert",
            "mainAgent": True,  # FORBIDDEN: only academic-orchestrator may be mainAgent
            "subagent": True,
            "tools": [
                "invoke_subagent", "manage_subagents", "send_message",
                "view_file", "list_dir", "grep_search", "find_by_name", "write_to_file"
            ],
        }
        issues = validate_agent_against_policy("methodology-expert", fm, self.policy)
        self.assertTrue(any("mainAgent=True does not match capability policy" in i for i in issues))

    def test_12_policy_schema_validation_catches_invalid_manifest(self):
        """validate_policy_schema must catch overlapping tools, missing fields, or invalid tool names."""
        bad_policy = {
            "schema_version": "1.0.0",
            "agents": {
                "broken-agent": {
                    "role": "worker",
                    "tier": "Tier 3",
                    "mainAgent": False,
                    "subagent": True,
                    "can_delegate": False,
                    "can_execute_code": False,
                    "can_write_files": True,
                    "required": ["view_file", "fake_nonexistent_tool"],
                    "forbidden": ["fake_nonexistent_tool"],  # Overlap + invalid tool name
                }
            }
        }
        issues = validate_policy_schema(bad_policy)
        self.assertTrue(any("invalid required tool" in i for i in issues))
        self.assertTrue(any("both required and forbidden" in i for i in issues))
        self.assertTrue(any("run_command" in i for i in issues))  # can_execute_code=False but run_command not in forbidden

    def test_13_agent_integrity_validator_runs_with_policy_check(self):
        """AgentIntegrityValidator must pass with 0 errors when capability policy is enforced."""
        validator = AgentIntegrityValidator(
            agents_dir=AGENTS_DIR,
            skills_dir=os.path.join(ROOT_DIR, ".agents", "skills"),
            enforce_capability_policy=True,
        )
        result = validator.run_validation()
        self.assertEqual(result["overall_verdict"], "PASS")
        self.assertEqual(result["errors"], 0)
        self.assertEqual(result["agents_validated"], 28)


if __name__ == "__main__":
    unittest.main()
