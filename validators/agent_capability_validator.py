#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validators/agent_capability_validator.py — Specialized Agent Capability Validator CLI

Phase 13: Audits agent capability boundaries and least-privilege tool allocations.
Checks:
- Every agent: frontmatter valid, tools recognized, mainAgent valid, subagent valid, skills valid, MCP references valid.
- Academic-Orchestrator: NO run_command, NO write_to_file, NO edit_file, NO replace_file_content, YES invoke_subagent.
- Execution workers: run_command allowed and required.
- Read-only agents: no write tools, no execution tools.
- Auditors: no execution unless explicitly justified.
"""

import os
import sys
import argparse
import json

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from validators.agent_integrity import (
    AgentCapabilityValidator,
    AgentIntegrityValidator,
    AGENTS_DIR,
    SKILLS_DIR,
)


def main():
    parser = argparse.ArgumentParser(description="AcademicSuite Agent Capability Validator (Phase 13)")
    parser.add_argument("--agents-dir", default=AGENTS_DIR, help="Path to .agents/agents directory")
    parser.add_argument("--skills-dir", default=SKILLS_DIR, help="Path to .agents/skills directory")
    parser.add_argument("--policy-path", default=None, help="Path to agent capability policy YAML")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print detailed report")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    validator = AgentCapabilityValidator(
        agents_dir=args.agents_dir,
        skills_dir=args.skills_dir,
        policy_path=args.policy_path,
        enforce_capability_policy=True,
    )
    result = validator.run_validation()

    if args.json:
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["overall_verdict"] == "PASS" else 1)

    print("=" * 70)
    print("🛡️ AcademicSuite Agent Capability Validator (Phase 13)")
    print("=" * 70)
    print(f"Directory:        {args.agents_dir}")
    print(f"Agents Scanned:   {result['agents_validated']}")
    print(f"Errors:           {result['errors']}")
    print(f"Warnings:         {result['warnings']}")
    print(f"Overall Verdict:  {result['overall_verdict']}")
    print("=" * 70)

    if result["issues"]:
        print("\nIdentified Capability Violations:")
        for issue in result["issues"]:
            prefix = "❌" if issue["severity"] in ("ERROR", "FATAL") else "⚠️"
            print(f"  {prefix} [{issue['severity']}] {issue['agent']}: ({issue['check']}) {issue['message']}")
        print()

    if result["overall_verdict"] == "PASS":
        print("✅ ALL AGENTS VALIDATED: 100% capability boundaries and least-privilege contracts satisfied.")
        sys.exit(0)
    else:
        print("❌ CAPABILITY VALIDATION FAILED: See violations above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
