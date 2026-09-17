#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
academic_task_router.py — Deterministic Academic Task Router Engine ("The Hands")

Parses academic task descriptions, recognizes required capabilities,
and deterministically constructs the minimum sufficient ordered pipeline
of specialist subagents, Skills, and artifact handoffs.
"""

import os
import sys
import json
import re
import argparse
from typing import Dict, Any, List, Optional, Set

# Virtualenv auto-discovery shim
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

# Capability definitions & metadata
CAPABILITY_METADATA = {
    "RESEARCH": {
        "agent": "research-agent",
        "primary_skill": "literature-review",
        "skill_path": ".agents/skills/literature-review/SKILL.md",
        "input_artifact": "academic-state/requirements.json",
        "output_artifact": "academic-state/requirements.json",
        "description": "Scientific literature harvesting, theoretical foundations, and research question formulation"
    },
    "METHODOLOGY": {
        "agent": "research-agent",
        "primary_skill": "methodology-review",
        "skill_path": ".agents/skills/methodology-review/SKILL.md",
        "input_artifact": "academic-state/requirements.json",
        "output_artifact": "academic-state/analysis_plan.json",
        "description": "Research design formulation, G*Power sampling determination, and validity safeguards"
    },
    "DATA": {
        "agent": "data-agent",
        "primary_skill": "data-cleaning",
        "skill_path": ".agents/skills/data-cleaning/SKILL.md",
        "input_artifact": "projects/*/01_raw_inputs/*",
        "output_artifact": "academic-state/data/data_quality.json",
        "description": "Raw dataset ingestion, scale reverse-coding, missing value screening, and quality auditing"
    },
    "NETWORK-ANALYSIS": {
        "agent": "statistics-agent",
        "primary_skill": "network-analysis",
        "skill_path": ".agents/skills/network-analysis/SKILL.md",
        "input_artifact": "academic-state/data/data_dictionary.json",
        "output_artifact": "academic-state/analysis/network_results.json",
        "description": "Bibliometric network mapping, keyword co-occurrence, and citation centrality analysis"
    },
    "STATISTICS": {
        "agent": "statistics-agent",
        "primary_skill": "sem",
        "skill_path": ".agents/skills/sem/SKILL.md",
        "input_artifact": "academic-state/data/data_quality.json",
        "output_artifact": "academic-state/analysis/sem.json",
        "description": "Deterministic inferential modeling (SEM, CFA, ANCOVA, regression, mediation, reliability)"
    },
    "WRITING": {
        "agent": "writing-agent",
        "primary_skill": "chapter-4-writing",
        "skill_path": ".agents/skills/chapter-4-writing/SKILL.md",
        "input_artifact": "academic-state/analysis/sem.json",
        "output_artifact": "academic-state/outputs/Chapter_4_Results.docx",
        "description": "Scholarly narrative formulation, APA 7 3-line tables, and OpenXML institutional typography"
    },
    "VALIDATION": {
        "agent": "validation-agent",
        "primary_skill": "thesis-integrity-auditor",
        "skill_path": ".agents/skills/thesis-integrity-auditor/SKILL.md",
        "input_artifact": "academic-state/outputs/*",
        "output_artifact": "academic-state/validation/statistical_validation.json",
        "description": "Independent adversarial verification of df, numerical consistency, and APA reporting rules"
    }
}

# Strict Pipeline Ordering Invariant:
# RESEARCH -> METHODOLOGY -> DATA -> NETWORK-ANALYSIS -> STATISTICS -> WRITING -> VALIDATION
EXECUTION_ORDER = [
    "RESEARCH",
    "METHODOLOGY",
    "DATA",
    "NETWORK-ANALYSIS",
    "STATISTICS",
    "WRITING",
    "VALIDATION"
]


def detect_capabilities(prompt: str) -> List[str]:
    """Detects and returns the minimal sufficient ordered list of capabilities needed for a prompt."""
    p = prompt.lower()
    capabilities: Set[str] = set()

    # Explicit Pattern Rules

    # 1. "Analyze this dataset" / "clean dataset" / "prepare data"
    if re.search(r'\banalyz(?:e|ing)\s+(?:this\s+|the\s+|these\s+)?(?:data|dataset)\b', p) or \
       re.search(r'\bexplore\s+(?:this\s+|the\s+|these\s+)?(?:data|dataset)\b', p):
        capabilities.add("DATA")
        capabilities.add("STATISTICS")

    # 2. "Write Chapter 4" / "draft results chapter" / "chapter 4 findings"
    if re.search(r'\b(?:write|draft|generate)\s+chapter\s*4\b', p) or \
       re.search(r'\bchapter\s*4\s+findings\b', p) or \
       re.search(r'\bresults\s+chapter\b', p):
        capabilities.add("STATISTICS")
        capabilities.add("WRITING")
        capabilities.add("VALIDATION")

    # 3. "Find research gaps" / "literature review gaps" / "identify research questions"
    if re.search(r'\b(?:find|identify|explore)\s+(?:research\s+)?gaps\b', p) or \
       re.search(r'\bresearch\s+gap\b', p) or \
       re.search(r'\bformulate\s+research\s+questions\b', p):
        capabilities.add("RESEARCH")
        capabilities.add("METHODOLOGY")

    # 4. "Perform CFA and SEM" / "cfa and sem" / "structural equation modeling"
    if re.search(r'\b(?:perform|run|execute)\s+cfa\s+(?:and\s+)?sem\b', p) or \
       re.search(r'\bcfa\s+and\s+sem\b', p) or \
       re.search(r'\bsem\s+and\s+cfa\b', p):
        capabilities.add("DATA")
        capabilities.add("STATISTICS")
        capabilities.add("VALIDATION")

    # 5. "Analyze these network data" / "network analysis" / "bibliometric network"
    if re.search(r'\banalyz(?:e|ing)\s+(?:these\s+|the\s+|this\s+)?network\s+data\b', p) or \
       re.search(r'\bnetwork\s+analysis\b', p) or \
       re.search(r'\bbibliometric\s+network\b', p) or \
       re.search(r'\bco-occurrence\s+network\b', p):
        capabilities.add("DATA")
        capabilities.add("NETWORK-ANALYSIS")
        capabilities.add("STATISTICS")
        capabilities.add("VALIDATION")

    # Domain Specific Keyword Heuristics if no macro pattern triggered
    if not capabilities:
        # Data keywords
        if any(w in p for w in ["data", "dataset", "clean", "reverse code", "missingness", "mcar", "score", "curation"]):
            capabilities.add("DATA")

        # Network Analysis keywords
        if any(w in p for w in ["network", "bibliometric", "vosviewer", "callon", "co-occurrence"]):
            capabilities.add("NETWORK-ANALYSIS")

        # Statistics keywords
        if any(w in p for w in ["stat", "sem", "cfa", "regression", "ancova", "anova", "t-test", "descriptive", "reliability", "correlation", "mediation", "moderation"]):
            capabilities.add("STATISTICS")

        # Research / Literature keywords
        if any(w in p for w in ["literature", "pubmed", "crossref", "gap", "background", "theoretical framework", "citation"]):
            capabilities.add("RESEARCH")

        # Methodology keywords
        if any(w in p for w in ["methodology", "g*power", "sample size", "experimental design", "validity"]):
            capabilities.add("METHODOLOGY")

        # Writing keywords
        if any(w in p for w in ["write", "writing", "draft", "chapter", "apa", "narrative", "discussion", "prose"]):
            capabilities.add("WRITING")

        # Validation keywords
        if any(w in p for w in ["validate", "validation", "audit", "verify", "check", "qc", "df"]):
            capabilities.add("VALIDATION")

    # Contextual Invariant Complements
    # Invariant A: If Writing Chapter 4/Results, must include Statistics and Validation
    if "WRITING" in capabilities and any(w in p for w in ["chapter 4", "results", "findings"]):
        capabilities.add("STATISTICS")
        capabilities.add("VALIDATION")

    # Invariant B: If Statistics or SEM/CFA requested from scratch, data must be verified
    if "STATISTICS" in capabilities and any(w in p for w in ["cfa", "sem", "model", "from scratch"]):
        capabilities.add("DATA")
        capabilities.add("VALIDATION")

    # Sort capabilities strictly by canonical EXECUTION_ORDER
    ordered_caps = [c for c in EXECUTION_ORDER if c in capabilities]

    # Default fallback if empty
    if not ordered_caps:
        ordered_caps = ["DATA", "STATISTICS"]

    return ordered_caps


def build_pipeline(prompt: str) -> Dict[str, Any]:
    """Generates the full execution pipeline specification for a prompt."""
    caps = detect_capabilities(prompt)
    steps = []

    for idx, cap_name in enumerate(caps, 1):
        meta = CAPABILITY_METADATA[cap_name]
        steps.append({
            "step": idx,
            "capability": cap_name,
            "agent": meta["agent"],
            "skill": meta["primary_skill"],
            "skill_path": meta["skill_path"],
            "description": meta["description"],
            "input_artifact": meta["input_artifact"],
            "output_artifact": meta["output_artifact"]
        })

    capabilities_formula = " + ".join(caps)

    return {
        "task_prompt": prompt,
        "capabilities_formula": capabilities_formula,
        "capabilities": caps,
        "total_steps": len(steps),
        "pipeline": steps,
        "orchestration_directive": (
            f"The Academic Orchestrator will execute {len(steps)} sequential stages: "
            f"{' ──► '.join([s['agent'] for s in steps])}. "
            "Unneeded agents are pruned to preserve context bandwidth."
        )
    }


def main():
    parser = argparse.ArgumentParser(description="Academic Task Router Engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # route
    p_route = subparsers.add_parser("route", help="Determine minimum sufficient capability pipeline for a user task")
    p_route.add_argument("prompt", help="User task instruction prompt")

    # explain
    p_exp = subparsers.add_parser("explain", help="Print human-readable routing summary")
    p_exp.add_argument("prompt", help="User task instruction prompt")

    # list-patterns
    subparsers.add_parser("list-patterns", help="List canonical recognized academic routing patterns")

    args = parser.parse_args()

    if args.command == "route":
        res = build_pipeline(args.prompt)
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.command == "explain":
        res = build_pipeline(args.prompt)
        print(f"\nTask: \"{res['task_prompt']}\"")
        print(f"Formula: {res['capabilities_formula']}")
        print(f"Total Steps: {res['total_steps']}\n")
        for s in res["pipeline"]:
            print(f"  Step {s['step']}: [{s['capability']}] -> {s['agent']} (Skill: {s['skill']})")
            print(f"          Input:  {s['input_artifact']}")
            print(f"          Output: {s['output_artifact']}\n")

    elif args.command == "list-patterns":
        print("Canonical Academic Routing Patterns:")
        print("  1. 'Analyze this dataset'         -> DATA + STATISTICS")
        print("  2. 'Write Chapter 4'              -> STATISTICS + WRITING + VALIDATION")
        print("  3. 'Find research gaps'           -> RESEARCH + METHODOLOGY")
        print("  4. 'Perform CFA and SEM'          -> DATA + STATISTICS + VALIDATION")
        print("  5. 'Analyze these network data'   -> DATA + NETWORK-ANALYSIS + STATISTICS + VALIDATION")


if __name__ == "__main__":
    main()
