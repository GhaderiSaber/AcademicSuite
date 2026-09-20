#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/academic_teamwork_patterns.py — Academic Domain Teamwork Patterns Engine

Provides authoritative academic collaboration patterns utilizing Antigravity's
conceptual roles:
- Explorer: Solution space discovery, candidate methods, literature exploration
- Critic: Methodological vetting, identification assumptions, design critique
- Worker: Deterministic computation and draft narrative synthesis ('The Hands')
- Challenger: Adversarial red-team stress-testing against assumptions and fragility
- Auditor: Statistical concordance, degrees of freedom, MSAI score, typography
- Success Auditor: Final release gatekeeper and Viva Voce defense committee simulation

Does NOT recreate Antigravity's platform control plane (Directive 12.1).
Supplies the domain patterns, role sequences, and handoff contracts.
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, List, Optional

_CURR_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(os.path.dirname(_CURR_DIR)) == ".agents":
    ROOT_DIR = os.path.abspath(os.path.join(_CURR_DIR, "..", ".."))
else:
    ROOT_DIR = os.path.abspath(os.path.join(_CURR_DIR, ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from contracts.contract_validator import validate_teamwork_pattern

CONCEPTUAL_ROLES = [
    "Explorer",
    "Worker",
    "Critic",
    "Challenger",
    "Auditor",
    "Success Auditor"
]

PATTERNS_JSON_PATH = os.path.join(ROOT_DIR, "evals", "teamwork", "academic_teamwork_patterns.json")


def _load_patterns_registry() -> Dict[str, Dict[str, Any]]:
    if not os.path.exists(PATTERNS_JSON_PATH):
        return {}
    with open(PATTERNS_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


PATTERNS_REGISTRY: Dict[str, Dict[str, Any]] = _load_patterns_registry()


class AcademicTeamworkPatterns:
    """
    Catalog and utility engine for Academic Suite's domain-specific teamwork patterns.
    Enforces role separation, handoff schemas, and exit criteria across academic workflows.
    """

    @classmethod
    def list_patterns(cls) -> List[Dict[str, Any]]:
        return list(PATTERNS_REGISTRY.values())

    @classmethod
    def get_pattern(cls, pattern_id: str) -> Optional[Dict[str, Any]]:
        return PATTERNS_REGISTRY.get(pattern_id)

    @classmethod
    def validate_all_patterns(cls) -> Dict[str, Any]:
        errors = []
        for pid, pat in PATTERNS_REGISTRY.items():
            res = validate_teamwork_pattern(pat)
            if not res["valid"]:
                errors.append(f"[{pid}] {res['errors']}")
        return {
            "total": len(PATTERNS_REGISTRY),
            "passed": len(PATTERNS_REGISTRY) - len(errors),
            "failed": len(errors),
            "errors": errors,
            "verdict": "PASS" if not errors else "FAIL"
        }

    @classmethod
    def format_antigravity_dispatch_plan(cls, pattern_id: str) -> Dict[str, Any]:
        """
        Formats structured subagent dispatch specifications for Antigravity's invoke_subagent.
        Does NOT execute Python threads (Directive 12.1); provides deterministic parameters.
        """
        pat = cls.get_pattern(pattern_id)
        if not pat:
            raise ValueError(f"Pattern '{pattern_id}' not found.")

        stages = pat["workflow_stages"]
        subagent_steps = []

        for idx, stg in enumerate(stages, start=1):
            subagent_steps.append({
                "sequence_index": idx,
                "stage_id": stg["stage_id"],
                "conceptual_role": stg["conceptual_role"],
                "invoke_subagent_params": {
                    "TypeName": stg["assigned_agent"],
                    "Role": stg["domain_specialization"],
                    "Prompt": (
                        f"Execute {stg['stage_name']} ({stg['domain_specialization']}). "
                        f"Input deliverables: {', '.join(stg['input_artifacts'])}. "
                        f"Produce output artifacts: {', '.join(stg['output_artifacts'])}. "
                        f"Verify exit criteria: {'; '.join(stg['exit_criteria'])}."
                    ),
                    "Model": "inherit",
                    "Workspace": stg.get("workspace_mode", "inherit")
                },
                "required_skills": stg["required_skills"],
                "exit_criteria": stg["exit_criteria"]
            })

        return {
            "pattern_id": pat["pattern_id"],
            "pattern_name": pat["pattern_name"],
            "target_pipeline": pat["target_pipeline"],
            "orchestrator": "Google Antigravity (Native invoke_subagent)",
            "total_stages": len(subagent_steps),
            "subagent_sequence": subagent_steps
        }


def main():
    parser = argparse.ArgumentParser(description="Academic Domain Teamwork Patterns Engine")
    parser.add_argument("--list-patterns", action="store_true", help="List registered academic teamwork patterns")
    parser.add_argument("--pattern", type=str, help="View a specific pattern JSON")
    parser.add_argument("--format-antigravity-plan", type=str, help="Format Antigravity subagent invocation sequence")
    parser.add_argument("--validate-all", action="store_true", help="Validate all patterns against schema")
    args = parser.parse_args()

    engine = AcademicTeamworkPatterns()

    if args.list_patterns:
        print("Authoritative Academic Domain Teamwork Patterns:")
        for p in engine.list_patterns():
            roles_str = " -> ".join(p["conceptual_roles"])
            print(f"  [{p['pattern_id']}] {p['pattern_name']}")
            print(f"      Pipeline: {p['target_pipeline']} | Stages: {len(p['workflow_stages'])}")
            print(f"      Roles: {roles_str}\n")
        return

    if args.validate_all:
        res = engine.validate_all_patterns()
        print(f"Validation Verdict: {res['verdict']} | Total: {res['total']} | Passed: {res['passed']} | Failed: {res['failed']}")
        if res["errors"]:
            for e in res["errors"]:
                print(f"  ERROR: {e}", file=sys.stderr)
            sys.exit(1)
        return

    if args.pattern:
        pat = engine.get_pattern(args.pattern)
        if not pat:
            print(f"Pattern '{args.pattern}' not found.", file=sys.stderr)
            sys.exit(1)
        print(json.dumps(pat, indent=2, ensure_ascii=False))
        return

    if args.format_antigravity_plan:
        try:
            plan = engine.format_antigravity_dispatch_plan(args.format_antigravity_plan)
            print(json.dumps(plan, indent=2, ensure_ascii=False))
        except Exception as ex:
            print(f"Error: {ex}", file=sys.stderr)
            sys.exit(1)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
