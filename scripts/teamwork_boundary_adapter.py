#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/teamwork_boundary_adapter.py — AcademicSuite & Native Antigravity Teamwork Boundary Adapter

Defines and enforces the integration boundary between AcademicSuite domain governance
and Antigravity native Teamwork runtime:
- AcademicSuite owns: research contracts, analysis plans, artifact schemas, provenance,
  statistical execution contracts, validation, academic acceptance criteria, and human approval.
- Antigravity Teamwork owns: dynamic team formation, concurrent worker management,
  isolated team execution, and runtime task orchestration.

Codifies:
- 5 Complexity Levels (L0 to L4)
- 6 Teamwork-style abstract role mappings (Explorer, Worker, Critic, Challenger, Auditor, Success Auditor)
- Dynamic subagent allocation (zero hard-coded worker counts)
- Schema-validated boundary packages conforming to contracts/teamwork_boundary.schema.json
"""

import os
import sys
import re
import json
import argparse
from typing import Dict, Any, List, Optional, Set

# Virtualenv and package discovery
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

# Add scripts and contracts to sys.path
SCRIPTS_DIR = os.path.join(ROOT_DIR, "scripts")
CONTRACTS_DIR = os.path.join(ROOT_DIR, "contracts")
for d in [SCRIPTS_DIR, CONTRACTS_DIR, ROOT_DIR]:
    if d not in sys.path:
        sys.path.insert(0, d)

try:
    from contracts.contract_validator import validate_contract
except ImportError:
    validate_contract = None


# Canonical Complexity Level Definitions
COMPLEXITY_LEVELS = {
    "L0": {
        "label": "Simple Question",
        "description": "Informational query, terminology definition, or APA formatting check without empirical calculation.",
        "team_formation_mode": "none",
        "isolated_workspaces": False,
        "recommended_slash_command": None,
        "analysis_plan_required": False,
        "provenance_required": False,
        "human_approval_required": False
    },
    "L1": {
        "label": "Single Analysis",
        "description": "Single bounded statistical or psychometric calculation on an approved dataset.",
        "team_formation_mode": "bounded_single",
        "isolated_workspaces": False,
        "recommended_slash_command": None,
        "analysis_plan_required": True,
        "provenance_required": True,
        "human_approval_required": False
    },
    "L2": {
        "label": "Multi-Analysis Project",
        "description": "Multi-stage empirical sequence requiring coordinated methodology, statistics, adversarial challenge, and audit.",
        "team_formation_mode": "sequential_audited",
        "isolated_workspaces": False,
        "recommended_slash_command": None,
        "analysis_plan_required": True,
        "provenance_required": True,
        "human_approval_required": False
    },
    "L3": {
        "label": "Thesis/Paper Milestone",
        "description": "Full chapter milestone workflow (e.g. Chapter 4 Findings, Scale Validation study, PRISMA Review, Proposal).",
        "team_formation_mode": "full_milestone_pipeline",
        "isolated_workspaces": False,
        "recommended_slash_command": None,
        "analysis_plan_required": True,
        "provenance_required": True,
        "human_approval_required": True
    },
    "L4": {
        "label": "Full Research Project",
        "description": "Repository-wide multi-chapter thesis overhaul, 20-chapter monograph restructuring, or longitudinal multi-wave panel across thousands of files.",
        "team_formation_mode": "dynamic_teamwork",
        "isolated_workspaces": True,
        "recommended_slash_command": "/teamwork-preview",
        "analysis_plan_required": True,
        "provenance_required": True,
        "human_approval_required": True
    }
}

# Mapping abstract Teamwork roles to AcademicSuite cognitive specializations
TEAMWORK_ROLE_MAPPINGS = {
    "Explorer": {
        "description": "Domain exploration, data screening, literature harvesting, and methodology scoping.",
        "default_agents": ["data-agent", "research-agent", "methodology-expert", "data-curator", "literature-expert"],
        "default_skills": ["data-audit", "methodology-review", "literature-harvester", "literature-review"]
    },
    "Worker": {
        "description": "Deterministic calculation of statistical parameters and draft generation ('The Hands').",
        "default_agents": ["statistics-agent", "academic-writer", "psychometric-expert", "qualitative-analyst", "meta-analyst"],
        "default_skills": ["statistical-data-analyst", "chapter-4-writing", "cfa", "sem", "regression", "mediation"]
    },
    "Critic": {
        "description": "Structural review, APA 7 typography enforcement, degrees-of-freedom verification, table checks.",
        "default_agents": ["results-auditor", "validation-agent", "evidence-auditor"],
        "default_skills": ["apa-reporting", "thesis-integrity-auditor"]
    },
    "Challenger": {
        "description": "Adversarial red-teaming, sample leakage probing, and pitfall registry auditing.",
        "default_agents": ["academic-challenger"],
        "default_skills": ["assumption-testing"]
    },
    "Auditor": {
        "description": "Mathematical integrity, Multi-Signal Anomaly Index (MSAI), and effect size deflation auditing.",
        "default_agents": ["statistical-auditor", "thesis-integrity-auditor"],
        "default_skills": ["data-audit", "apa-reporting"]
    },
    "Success Auditor": {
        "description": "Final acceptance evaluation, Viva Voce defense simulation, and doctoral committee criteria.",
        "default_agents": ["final-judge"],
        "default_skills": ["thesis-integrity-auditor", "persian-defense-presentation-builder"]
    }
}


def classify_complexity(
    task_description: str,
    file_count: int = 1,
    chapter_count: int = 1,
    resolved_capabilities: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Classifies a task into graduated complexity levels L0 through L4.
    Evaluates query semantics, quantitative scope, and capability signatures.
    """
    desc_lower = task_description.lower().strip()
    resolved_set = set(resolved_capabilities or [])

    # Check for L4 (Full Research Project / Huge Long-Running Monograph)
    l4_keywords = [
        "20-chapter", "twenty chapter", "multi-chapter monograph",
        "entire dissertation", "full thesis overhaul", "thousands of source files",
        "repository-wide", "multi-study repository", "longitudinal multi-wave overhaul",
        "large project", "complex multi-year", "full research project",
        "across multiple volumes", "complete institutional overhaul"
    ]
    is_l4 = (
        chapter_count >= 10
        or file_count >= 100
        or any(k in desc_lower for k in l4_keywords)
    )
    if is_l4:
        meta = COMPLEXITY_LEVELS["L4"]
        return {
            "complexity_level": "L4",
            "label": meta["label"],
            "description": meta["description"],
            "team_formation_mode": meta["team_formation_mode"],
            "isolated_workspaces": meta["isolated_workspaces"],
            "recommended_slash_command": meta["recommended_slash_command"],
            "analysis_plan_required": meta["analysis_plan_required"],
            "provenance_required": meta["provenance_required"],
            "human_approval_required": meta["human_approval_required"],
            "rationale": "Task encompasses massive repository-wide scope, multi-chapter restructuring, or longitudinal waves requiring native Antigravity Teamwork with isolated workspaces."
        }

    # Check for L3 (Full AcademicSuite Milestone Workflow)
    l3_capabilities = {
        "thesis_chapter4", "thesis_chapter5", "scale_validation",
        "meta_analysis", "literature_review", "research_proposal",
        "defense_presentation", "grounded_theory"
    }
    l3_keywords = [
        "chapter 4", "chapter 5", "chapter 2", "chapter 3",
        "scale validation", "validate scale", "meta-analysis", "systematic review",
        "research proposal", "defense presentation", "thesis milestone",
        "full chapter", "complete study", "grounded theory study"
    ]
    is_l3 = (
        chapter_count >= 2
        or file_count >= 15
        or bool(resolved_set.intersection(l3_capabilities))
        or any(k in desc_lower for k in l3_keywords)
    )
    if is_l3:
        meta = COMPLEXITY_LEVELS["L3"]
        return {
            "complexity_level": "L3",
            "label": meta["label"],
            "description": meta["description"],
            "team_formation_mode": meta["team_formation_mode"],
            "isolated_workspaces": meta["isolated_workspaces"],
            "recommended_slash_command": meta["recommended_slash_command"],
            "analysis_plan_required": meta["analysis_plan_required"],
            "provenance_required": meta["provenance_required"],
            "human_approval_required": meta["human_approval_required"],
            "rationale": "Task represents a full institutional thesis or empirical paper milestone requiring the complete AcademicSuite micro-stage sequence, triad artifacts (.docx, .md, .json), and multi-agent peer review."
        }

    # Check for L0 (Simple Question / Informational Lookup)
    l0_keywords = [
        r"^(?:what\s+is|what\s+are)\b",
        r"^define\b",
        r"^explain\b",
        r"^difference\s+between\b",
        r"^how\s+to\s+interpret\b",
        r"^what\s+is\s+the\s+apa\b",
        r"^summarize\s+concept\b",
        r"formula\s+for\b"
    ]
    is_l0 = (
        len(resolved_set) == 0
        and (
            any(re.search(pat, desc_lower) for pat in l0_keywords)
            or ("?" in desc_lower and not any(w in desc_lower for w in ["run", "compute", "calculate", "analyze", "test", "audit", "estimate"]))
        )
    )
    if is_l0:
        meta = COMPLEXITY_LEVELS["L0"]
        return {
            "complexity_level": "L0",
            "label": meta["label"],
            "description": meta["description"],
            "team_formation_mode": meta["team_formation_mode"],
            "isolated_workspaces": meta["isolated_workspaces"],
            "recommended_slash_command": meta["recommended_slash_command"],
            "analysis_plan_required": meta["analysis_plan_required"],
            "provenance_required": meta["provenance_required"],
            "human_approval_required": meta["human_approval_required"],
            "rationale": "Task is an informational or conceptual academic query that requires no empirical computation or multi-agent delegation."
        }

    # Check for L2 (Multi-Analysis Project)
    # If multiple capabilities resolved or multi-model keywords present
    multi_indicators = [
        "moderated mediation", "ancova and mediation", "sem and cfa",
        "cfa and sem", "regression and assumption", "mediation and moderation",
        "efa and cfa", "cfa and efa", "multivariate", "mixed model",
        "multi-step analysis", "multiple analyses", "multi-analysis",
        "assumption test and", "assumption testing and", "along with bootstrap"
    ]
    # Check if multiple analysis families are combined
    analysis_families = ["descriptive", "reliability", "assumption", "regression", "ancova", "mediation", "moderation", "sem", "cfa"]
    matched_families = sum(1 for f in analysis_families if f in desc_lower)

    is_l2 = (
        len(resolved_set) >= 2
        or any(ind in desc_lower for ind in multi_indicators)
        or matched_families >= 2
        or "longitudinal_moderated_mediation" in resolved_set
    )
    if is_l2:
        meta = COMPLEXITY_LEVELS["L2"]
        return {
            "complexity_level": "L2",
            "label": meta["label"],
            "description": meta["description"],
            "team_formation_mode": meta["team_formation_mode"],
            "isolated_workspaces": meta["isolated_workspaces"],
            "recommended_slash_command": meta["recommended_slash_command"],
            "analysis_plan_required": meta["analysis_plan_required"],
            "provenance_required": meta["provenance_required"],
            "human_approval_required": meta["human_approval_required"],
            "rationale": "Task involves multiple interdependent statistical models or assumption checks, requiring coordinated methodology, execution, challenger, and auditor subagents."
        }

    # Default to L1 (Single Bounded Analysis)
    meta = COMPLEXITY_LEVELS["L1"]
    return {
        "complexity_level": "L1",
        "label": meta["label"],
        "description": meta["description"],
        "team_formation_mode": meta["team_formation_mode"],
        "isolated_workspaces": meta["isolated_workspaces"],
        "recommended_slash_command": meta["recommended_slash_command"],
        "analysis_plan_required": meta["analysis_plan_required"],
        "provenance_required": meta["provenance_required"],
        "human_approval_required": meta["human_approval_required"],
        "rationale": "Task is a single bounded empirical analysis executing on real approved data with deterministic scripts."
    }


def map_teamwork_roles(
    complexity_level: str,
    capabilities: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Dynamically maps abstract Antigravity Teamwork roles (Explorer, Worker, Critic,
    Challenger, Auditor, Success Auditor) to AcademicSuite cognitive roles.
    
    CRITICAL: Worker counts and team membership are NOT hard-coded.
    They adapt dynamically to the resolved capability requirements and complexity level.
    """
    roster: List[Dict[str, Any]] = []
    caps = capabilities or []

    # Aggregate required skills, workers, reviewers, challengers from resolved capabilities
    aggregated_skills: Set[str] = set()
    aggregated_workers: Set[str] = set()
    aggregated_reviewers: Set[str] = set()
    aggregated_challengers: Set[str] = set()

    for cap in caps:
        aggregated_skills.update(cap.get("required_skills", []))
        worker = cap.get("execution_worker")
        if worker:
            aggregated_workers.add(worker)
        reviewer = cap.get("reviewer")
        if reviewer:
            aggregated_reviewers.add(reviewer)
        challenger = cap.get("challenger")
        if challenger:
            aggregated_challengers.add(challenger)

    # Defaults if capabilities were empty
    if not aggregated_workers:
        aggregated_workers.add("statistics-agent")
    if not aggregated_reviewers:
        aggregated_reviewers.add("validation-agent")
    if not aggregated_challengers:
        aggregated_challengers.add("academic-challenger")

    workspace_mode = "branch" if complexity_level == "L4" else "inherit"

    if complexity_level == "L0":
        # L0 requires no subagent roster
        return []

    elif complexity_level == "L1":
        # L1: Bounded single worker
        primary_worker = sorted(list(aggregated_workers))[0]
        worker_skills = [s for s in aggregated_skills if s in [
            "descriptive-statistics", "reliability-analysis", "assumption-testing",
            "regression", "ancova", "data-cleaning", "data-audit"
        ]] or ["statistical-data-analyst"]
        roster.append({
            "teamwork_role": "Worker",
            "academicsuite_agent": primary_worker,
            "purpose": "Execute bounded deterministic calculation on real approved dataset.",
            "required_skills": worker_skills,
            "workspace_mode": "inherit"
        })

    elif complexity_level == "L2":
        # L2: Explorer (Data/Methodology) + Worker (Stats) + Challenger + Critic/Auditor
        # 1. Explorer (if data preparation or audit required)
        if any("data" in s for s in aggregated_skills) or "data_cleaning" in [c.get("capability_id") for c in caps]:
            roster.append({
                "teamwork_role": "Explorer",
                "academicsuite_agent": "data-agent",
                "purpose": "Audit raw dataset provenance, screen missing data, and verify schema fingerprint.",
                "required_skills": ["data-audit", "data-cleaning"],
                "workspace_mode": "inherit"
            })

        # 2. Worker (Statistical execution)
        for w in sorted(list(aggregated_workers)):
            roster.append({
                "teamwork_role": "Worker",
                "academicsuite_agent": w,
                "purpose": "Execute multi-stage statistical models and compile numerical outputs.",
                "required_skills": sorted(list(aggregated_skills)),
                "workspace_mode": "inherit"
            })

        # 3. Challenger (Red-team assumptions)
        roster.append({
            "teamwork_role": "Challenger",
            "academicsuite_agent": "academic-challenger",
            "purpose": "Adversarially probe parametric assumptions and check pitfall registry (state/pitfalls.jsonl).",
            "required_skills": ["assumption-testing"],
            "workspace_mode": "inherit"
        })

        # 4. Auditor / Critic
        roster.append({
            "teamwork_role": "Auditor",
            "academicsuite_agent": "statistical-auditor",
            "purpose": "Compute Multi-Signal Anomaly Index (MSAI) and verify statistical degrees of freedom.",
            "required_skills": ["data-audit", "apa-reporting"],
            "workspace_mode": "inherit"
        })

    elif complexity_level in ("L3", "L4"):
        # L3/L4: Full AcademicSuite Role Suite
        # 1. Explorer
        roster.append({
            "teamwork_role": "Explorer",
            "academicsuite_agent": "data-agent",
            "purpose": "Verify raw dataset provenance, schema integrity, and explore variable distributions.",
            "required_skills": ["data-audit", "data-cleaning"],
            "workspace_mode": workspace_mode
        })

        # 2. Worker (Execution)
        for w in sorted(list(aggregated_workers)):
            roster.append({
                "teamwork_role": "Worker",
                "academicsuite_agent": w,
                "purpose": "Execute deterministic statistical engines and OpenXML triad compilation.",
                "required_skills": sorted(list(aggregated_skills)),
                "workspace_mode": workspace_mode
            })

        # 3. Critic (APA & Reporting Reviewer)
        for r in sorted(list(aggregated_reviewers)):
            roster.append({
                "teamwork_role": "Critic",
                "academicsuite_agent": r,
                "purpose": "Audit APA 7 typography, 3-table standard compliance, and citation reconciliation.",
                "required_skills": ["apa-reporting", "thesis-integrity-auditor"],
                "workspace_mode": workspace_mode
            })

        # 4. Challenger
        roster.append({
            "teamwork_role": "Challenger",
            "academicsuite_agent": "academic-challenger",
            "purpose": "Adversarially challenge methodological validity, detect sample leakage, and log to state/pitfalls.jsonl.",
            "required_skills": ["assumption-testing"],
            "workspace_mode": workspace_mode
        })

        # 5. Auditor (Statistical Auditor)
        roster.append({
            "teamwork_role": "Auditor",
            "academicsuite_agent": "statistical-auditor",
            "purpose": "Forensic audit of effect sizes, variance deflation, and Multi-Signal Anomaly Index (MSAI).",
            "required_skills": ["data-audit", "apa-reporting"],
            "workspace_mode": workspace_mode
        })

        # 6. Success Auditor (Final Judge)
        roster.append({
            "teamwork_role": "Success Auditor",
            "academicsuite_agent": "final-judge",
            "purpose": "Simulate doctoral Viva Voce defense committee and issue institutional acceptance verdict.",
            "required_skills": ["thesis-integrity-auditor", "persian-defense-presentation-builder"],
            "workspace_mode": workspace_mode
        })

    return roster


def build_teamwork_boundary_package(
    task_description: str,
    task_id: Optional[str] = None,
    file_count: int = 1,
    chapter_count: int = 1,
    resolved_capabilities: Optional[List[Dict[str, Any]]] = None,
    output_directory: Optional[str] = None
) -> Dict[str, Any]:
    """
    Builds an authoritative, schema-valid boundary exchange package governing
    the handoff between AcademicSuite domain governance and Antigravity Teamwork runtime.
    
    Enforces that AcademicSuite owns research contracts, validation, schemas, and acceptance criteria,
    while Antigravity Teamwork owns runtime team formation and concurrent worker management.
    """
    clean_desc = task_description.strip()
    if not task_id:
        # Generate clean ASCII task_id
        safe_str = re.sub(r'[^a-zA-Z0-9]+', '_', clean_desc[:40]).strip('_').lower()
        task_id = f"task_{safe_str}" if safe_str else "task_academic_suite"

    cap_ids = [c.get("capability_id") for c in (resolved_capabilities or []) if isinstance(c, dict)]
    complexity_meta = classify_complexity(
        task_description=clean_desc,
        file_count=file_count,
        chapter_count=chapter_count,
        resolved_capabilities=cap_ids
    )
    c_level = complexity_meta["complexity_level"]

    role_roster = map_teamwork_roles(
        complexity_level=c_level,
        capabilities=resolved_capabilities
    )

    out_dir = output_directory or f"projects/{task_id}/03_deliverables"

    package = {
        "boundary_version": "1.0.0",
        "task_id": task_id,
        "task_description": clean_desc,
        "complexity_level": c_level,
        "governance": {
            "research_contracts": [
                "analysis_plan",
                "execution_manifest",
                "validation_report",
                "milestone_state"
            ] if complexity_meta["analysis_plan_required"] else ["event"],
            "analysis_plan_required": complexity_meta["analysis_plan_required"],
            "artifact_schemas": [
                "artifact_manifest",
                "validation_report",
                "pitfall"
            ],
            "provenance_required": complexity_meta["provenance_required"],
            "statistical_execution_contract": "deterministic_hands_only",
            "validation_rules": [
                "directive_0_binary_honesty",
                "directive_3_triad_invariant",
                "directive_6_english_filenames",
                "msai_anomaly_threshold",
                "three_table_standard"
            ],
            "academic_acceptance_criteria": [
                "Strict APA 7th edition table formatting (zero vertical borders)",
                "Persian leading zero retention (۰.۰۰۱)",
                "Decoupled LTR numeric values with Times New Roman",
                "Multi-Signal Anomaly Index (MSAI) < 0.60",
                "Zero synthetic sample leakage into production deliverables"
            ],
            "human_approval_required": complexity_meta["human_approval_required"]
        },
        "teamwork_runtime": {
            "team_formation_mode": complexity_meta["team_formation_mode"],
            "isolated_workspaces": complexity_meta["isolated_workspaces"],
            "recommended_slash_command": complexity_meta["recommended_slash_command"],
            "role_roster": role_roster,
            "max_concurrent_workers": None  # Dynamic concurrency managed by Antigravity runtime
        },
        "deliverables": {
            "expected_triads": [".docx", ".md", ".json"] if c_level in ("L2", "L3", "L4") else [".json"],
            "output_directory": out_dir
        }
    }

    # Contract validation check if contract validator is present
    if validate_contract:
        val_result = validate_contract(package, "teamwork_boundary")
        if not val_result.get("valid", False):
            errors = val_result.get("errors", [])
            raise ValueError(f"Teamwork boundary package failed schema validation: {errors}")

    return package


def main():
    parser = argparse.ArgumentParser(description="AcademicSuite & Antigravity Teamwork Boundary Adapter CLI")
    subparsers = parser.add_subparsers(dest="subcommand", help="Available subcommands")

    # Subcommand: classify
    p_classify = subparsers.add_parser("classify", help="Classify task complexity (L0 to L4)")
    p_classify.add_argument("--description", "-d", required=True, help="Task description")
    p_classify.add_argument("--file-count", type=int, default=1, help="Expected file count")
    p_classify.add_argument("--chapter-count", type=int, default=1, help="Expected chapter count")

    # Subcommand: package
    p_pkg = subparsers.add_parser("package", help="Build Teamwork boundary manifest package")
    p_pkg.add_argument("--description", "-d", required=True, help="Task description")
    p_pkg.add_argument("--task-id", "-t", default=None, help="Task identifier")
    p_pkg.add_argument("--file-count", type=int, default=1, help="Expected file count")
    p_pkg.add_argument("--chapter-count", type=int, default=1, help="Expected chapter count")
    p_pkg.add_argument("--output", "-o", default=None, help="Optional output JSON file")

    args = parser.parse_args()

    if args.subcommand == "classify":
        res = classify_complexity(
            task_description=args.description,
            file_count=args.file_count,
            chapter_count=args.chapter_count
        )
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.subcommand == "package":
        pkg = build_teamwork_boundary_package(
            task_description=args.description,
            task_id=args.task_id,
            file_count=args.file_count,
            chapter_count=args.chapter_count
        )
        out_json = json.dumps(pkg, indent=2, ensure_ascii=False)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(out_json)
            print(f"✅ Teamwork boundary package written to: {args.output}")
        else:
            print(out_json)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
