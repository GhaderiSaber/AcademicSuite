#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/capability_resolver.py — AcademicSuite Deterministic Capability Resolver CLI

Constitutional Invariant (Directive 12.1 & 19):
Python scripts are strictly deterministic tools ("The Hands").
Antigravity is the sole agent conductor. This script computes empirical research design,
required capability matrices, and dynamically assembled native subagent teams without
running or emulating agents.

Usage:
    python3 scripts/capability_resolver.py "Analyze whether ACT affects anxiety and psychological distress across post-test and two-month follow-up"
    python3 scripts/capability_resolver.py "..." --json
    python3 scripts/capability_resolver.py "..." --strict
"""

import sys
import os
import json
import argparse
from typing import Dict, Any

# Add current scripts directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from academic_task_router import CapabilityResolver, derive_research_design, resolve_capability_matrix, assemble_antigravity_team


def format_human_report(res: Dict[str, Any]) -> str:
    lines = []
    lines.append("=" * 80)
    lines.append("ACADEMIC SUITE DYNAMIC CAPABILITY RESOLVER (Hands / Capability Engine)")
    lines.append("=" * 80)
    lines.append(f"Prompt: {res.get('task_prompt', '')}")
    lines.append(f"Status: {res.get('status', 'UNKNOWN')}")
    lines.append(f"Complexity: {res.get('complexity_level', 'N/A')}")
    lines.append("")

    if res.get("status") == "BLOCKED":
        lines.append("-" * 80)
        lines.append("RESOLUTION BLOCKED (Fail-Closed Gate)")
        lines.append("-" * 80)
        lines.append(f"Reason: {res.get('reason', '')}")
        lines.append(f"Escalation Required: {res.get('escalation_required', False)}")
        lines.append("=" * 80)
        return "\n".join(lines)

    if res.get("status") == "AMBIGUOUS":
        lines.append("-" * 80)
        lines.append("RESOLUTION AMBIGUOUS (Clarification Required)")
        lines.append("-" * 80)
        lines.append(f"Reason: {res.get('reason', '')}")
        lines.append(f"Clarification: {res.get('clarification_prompt', '')}")
        lines.append("Candidate Capabilities:")
        for c in res.get("candidate_capabilities", []):
            lines.append(f"  • {c}")
        lines.append("=" * 80)
        return "\n".join(lines)

    # Design
    design = res.get("design", {})
    lines.append("-" * 80)
    lines.append("1. EMPIRICAL RESEARCH DESIGN")
    lines.append("-" * 80)
    lines.append(f"  Study Type:        {design.get('study_type', 'N/A')}")
    if "confidence" in design:
        lines.append(f"  Confidence:        {design.get('confidence')}")
    if "evidence" in design:
        ev = design["evidence"]
        ev_str = ", ".join(f"{k}={v}" for k, v in ev.items())
        lines.append(f"  Evidence:          {ev_str}")
    lines.append(f"  Group Structure:   {design.get('group_structure', 'N/A')}")
    lines.append(f"  Temporal Dynamics: {design.get('temporal_dynamics', 'N/A')}")
    lines.append(f"  Waves:             {design.get('waves', 'N/A')}")
    lines.append(f"  Design Factors:    {', '.join(design.get('factors', []))}")
    if design.get("interventions"):
        lines.append(f"  Interventions:     {', '.join(design.get('interventions', []))}")
    if design.get("outcomes"):
        lines.append(f"  Outcomes / DVs:    {', '.join(design.get('outcomes', []))}")
    lines.append("")

    # Capabilities
    lines.append("-" * 80)
    lines.append("2. REQUIRED CAPABILITIES (Capability Matrix)")
    lines.append("-" * 80)
    for idx, cap in enumerate(res.get("capability_matrix", []), 1):
        lines.append(f"  [{idx}] {cap}")
    lines.append("")

    # Dynamic Team Assembly
    team = res.get("assembled_team", {})
    subagents = team.get("assembled_subagents", [])
    pruned = team.get("pruned_agents", {})
    lines.append("-" * 80)
    lines.append(f"3. DYNAMICALLY ASSEMBLED ANTIGRAVITY TEAM ({len(subagents)} Subagents)")
    lines.append("-" * 80)
    lines.append(f"  Lead Orchestrator: {team.get('lead_orchestrator', 'academic-orchestrator')}")
    lines.append("  Assembled Native Subagents:")
    for sa in subagents:
        lines.append(f"    • {sa}")
    lines.append("")
    lines.append(f"  Pruned Agents ({len(pruned)} excluded with deterministic rationale):")
    for pa, rationale in sorted(pruned.items()):
        lines.append(f"    - {pa}: {rationale}")
    lines.append("")

    # Skills & Artifacts
    lines.append("-" * 80)
    lines.append("4. DETERMINISTIC SKILLS & ARTIFACT CONTRACTS")
    lines.append("-" * 80)
    lines.append(f"  Required Skills:   {', '.join(res.get('required_skills', []))}")
    lines.append(f"  Output Artifacts:  {len(res.get('output_artifacts', []))} contracts defined")
    for oa in res.get("output_artifacts", [])[:5]:
        lines.append(f"    • {oa}")
    if len(res.get("output_artifacts", [])) > 5:
        lines.append(f"    ... and {len(res.get('output_artifacts', [])) - 5} more")
    lines.append(f"  Validation Gates:  {', '.join(res.get('validation_requirements', []))}")
    lines.append("=" * 80)

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="AcademicSuite Deterministic Capability Resolver — Derives research design, capability matrix, and dynamic team assembly."
    )
    parser.add_argument("prompt", type=str, help="Research task prompt or query to resolve.")
    parser.add_argument("--json", action="store_true", help="Output full resolution as structured JSON.")
    parser.add_argument("--strict", action="store_true", help="Exit with code 1 if status is not RESOLVED.")

    args = parser.parse_args()

    resolver = CapabilityResolver()
    res = resolver.resolve(args.prompt)

    if args.json:
        print(json.dumps(res, indent=2, ensure_ascii=False))
    else:
        print(format_human_report(res))

    if args.strict and res.get("status") != "RESOLVED":
        sys.exit(1)


if __name__ == "__main__":
    main()
