#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/orchestrator_dependency_resolver.py — [DEPRECATED INTERFACE]

DEPRECATION NOTICE (Phase 35):
This module has been superseded by:
- scripts/academic_task_router.py (Dynamic task routing and capability sequencing)
- scripts/capability_resolver.py (Capability-to-Skill resolution)
- scripts/stage_manifest_engine.py (Stage manifest dependency gating)

Maintained as a backward-compatibility layer for legacy orchestrator tests.
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, List, Optional

# Virtualenv auto-discovery shim
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

# Capability to Skill & Agent Mapping Matrix
CAPABILITY_REGISTRY = {
    "data_cleaning": {
        "description": "Reverse-coding, scoring instruments, missing value diagnostics",
        "skill": "data-cleaning",
        "agent": "data-agent",
        "tools": ["run_command", "view_file", "write_to_file"]
    },
    "data_audit": {
        "description": "Screening unengaged responses, Little's MCAR, Mahalanobis D2",
        "skill": "data-audit",
        "agent": "data-agent",
        "tools": ["run_command", "view_file", "write_to_file"]
    },
    "descriptive_statistics": {
        "description": "Univariate sample parameters (M, SD, Skew, Kurtosis) & frequencies",
        "skill": "descriptive-statistics",
        "agent": "statistics-agent",
        "tools": ["run_command", "view_file", "write_to_file"]
    },
    "reliability_analysis": {
        "description": "Cronbach's alpha, McDonald's omega, item-total correlations",
        "skill": "reliability-analysis",
        "agent": "statistics-agent",
        "tools": ["run_command", "view_file", "write_to_file"]
    },
    "assumption_testing": {
        "description": "Levene variance homogeneity, Shapiro-Wilk, VIF multicollinearity",
        "skill": "assumption-testing",
        "agent": "statistics-agent",
        "tools": ["run_command", "view_file", "write_to_file"]
    },
    "sem": {
        "description": "Structural Equation Modeling, latent paths, 11 Hu & Bentler fit indices",
        "skill": "sem",
        "agent": "statistics-agent",
        "tools": ["run_command", "view_file", "write_to_file"]
    },
    "cfa": {
        "description": "Confirmatory Factor Analysis, factor loadings (lambda), AVE, CR",
        "skill": "cfa",
        "agent": "statistics-agent",
        "tools": ["run_command", "view_file", "write_to_file"]
    },
    "mediation": {
        "description": "Preacher & Hayes bootstrap mediation (5,000 resamples, 95% BCa CI)",
        "skill": "mediation",
        "agent": "statistics-agent",
        "tools": ["run_command", "view_file", "write_to_file"]
    },
    "moderation": {
        "description": "PROCESS Model 1 moderation, simple slopes (-1 SD, Mean, +1 SD)",
        "skill": "moderation",
        "agent": "statistics-agent",
        "tools": ["run_command", "view_file", "write_to_file"]
    },
    "regression": {
        "description": "Hierarchical multiple regression, R2 change, F-test, standardized beta",
        "skill": "regression",
        "agent": "statistics-agent",
        "tools": ["run_command", "view_file", "write_to_file"]
    },
    "apa_reporting": {
        "description": "APA 7 3-line tables, statistical symbol italicization, Persian leading zero",
        "skill": "apa-reporting",
        "agent": "academic-writer",
        "tools": ["view_file", "write_to_file"]
    },
    "chapter_4_writing": {
        "description": "Chapter 4 findings narration, One-Hypothesis-One-Stage micro-stages",
        "skill": "chapter-4-writing",
        "agent": "academic-writer",
        "tools": ["view_file", "write_to_file"]
    },
    "literature_review": {
        "description": "Multi-database query formulation, inverted-triangle narrative, synthesis",
        "skill": "literature-review",
        "agent": "research-agent",
        "tools": ["view_file", "write_to_file", "read_url_content", "search_web"]
    },
    "methodology_review": {
        "description": "Design validity, internal/external validity, G*Power statistical power",
        "skill": "methodology-review",
        "agent": "research-agent",
        "tools": ["view_file", "write_to_file"]
    },
    "validation_audit": {
        "description": "Independent adversarial verification of data, stats, df, and reporting",
        "skill": "thesis-integrity-auditor",
        "agent": "validation-agent",
        "tools": ["run_command", "view_file"]
    },
    "statistical_deliberation": {
        "description": "Multi-candidate methodology deliberation, Academic Challenger falsification, pitfall memory, and AnalysisPlan synthesis",
        "skill": "academic-suite-orchestrator",
        "agent": "statistical-expert",
        "tools": ["run_command", "view_file", "write_to_file"]
    }
}

# Micro-Stage Prerequisite Graph
STAGE_DEPENDENCIES = {
    "00_data_curation": {
        "title": "Raw Data Ingestion & Scoring",
        "capability": "data_cleaning",
        "required_files": ["project.json", "requirements.json"],
        "required_stage": None
    },
    "01_demographics": {
        "title": "Demographic Profiling & Frequencies",
        "capability": "descriptive_statistics",
        "required_files": ["project.json", "data/data_dictionary.json"],
        "required_stage": "00_data_curation"
    },
    "02_reliability": {
        "title": "Scale Internal Consistency Reliability",
        "capability": "reliability_analysis",
        "required_files": ["data/data_dictionary.json"],
        "required_stage": "00_data_curation"
    },
    "03_parametric_assumptions": {
        "title": "Parametric Assumptions Verification",
        "capability": "assumption_testing",
        "required_files": ["data/data_dictionary.json"],
        "required_stage": "00_data_curation"
    },
    "04_bivariate_correlations": {
        "title": "Bivariate Correlation Matrix",
        "capability": "descriptive_statistics",
        "required_files": ["analysis/descriptive.json"],
        "required_stage": "01_demographics"
    },
    "05_macro_model": {
        "title": "Macro SEM / Primary Statistical Model",
        "capability": "sem",
        "required_files": ["analysis/descriptive.json", "validation/statistical_validation.json"],
        "required_stage": "03_parametric_assumptions"
    },
    "06_hypothesis_testing": {
        "title": "Individual Hypotheses Testing & Triad Generation",
        "capability": "chapter_4_writing",
        "required_files": ["analysis/sem.json", "requirements.json"],
        "required_stage": "05_macro_model"
    },
    "07_mediation_analysis": {
        "title": "Indirect Mediation Paths (Bootstrap 5,000 BCa)",
        "capability": "mediation",
        "required_files": ["analysis/sem.json"],
        "required_stage": "05_macro_model"
    },
    "08_chapter_summary": {
        "title": "Master Hypotheses Decision Matrix & Summary",
        "capability": "chapter_4_writing",
        "required_files": ["requirements.json"],
        "required_stage": "06_hypothesis_testing"
    },
    "09_validation_audit": {
        "title": "Deterministic Quality & Integrity Audit",
        "capability": "validation_audit",
        "required_files": ["project.json"],
        "required_stage": "08_chapter_summary"
    },
    "04_statistical_deliberation": {
        "title": "Methodological Candidate Deliberation & Challenger Invalidation",
        "capability": "statistical_deliberation",
        "required_files": ["project.json"],
        "required_stage": "00_data_curation"
    },
    "10_chapter_assembly": {
        "title": "Chapter 4 OpenXML Compilation",
        "capability": "chapter_4_writing",
        "required_files": ["validation/statistical_validation.json", "validation/writing_validation.json"],
        "required_stage": "09_validation_audit"
    }
}


def resolve_capability(query: str) -> Dict[str, Any]:
    """Finds the best matching capability, skill, and specialist agent for a task description."""
    q_lower = query.lower()
    best_match = None
    best_score = 0

    keywords_map = {
        "data_cleaning": ["clean", "score", "reverse", "missing", "curation", "dataset"],
        "data_audit": ["unengaged", "straight", "mcar", "mahalanobis", "outlier"],
        "descriptive_statistics": ["descriptive", "mean", "sd", "skew", "kurtosis", "demographic", "frequency"],
        "reliability_analysis": ["reliability", "alpha", "omega", "cronbach", "internal consistency"],
        "assumption_testing": ["assumption", "levene", "normality", "shapiro", "vif", "collinearity", "homogeneity"],
        "sem": ["sem", "structural equation", "path model", "lavaan", "fit indices", "cfi", "rmsea"],
        "cfa": ["cfa", "confirmatory factor", "factor loading", "ave", "convergent", "discriminant"],
        "mediation": ["mediation", "indirect", "bootstrap", "bca", "process model 4", "sobel"],
        "moderation": ["moderation", "interaction", "simple slopes", "process model 1", "johnson-neyman"],
        "regression": ["regression", "hierarchical", "r2", "stepwise", "f-change"],
        "apa_reporting": ["table", "apa", "border", "italic", "typography", "b nazanin"],
        "chapter_4_writing": ["chapter 4", "findings", "hypothesis", "results", "narrative"],
        "literature_review": ["literature", "chapter 2", "pubmed", "crossref", "background", "citations"],
        "methodology_review": ["methodology", "chapter 3", "g*power", "sample size", "validity"],
        "validation_audit": ["validate", "audit", "check", "df", "consistency", "qc"],
        "statistical_deliberation": ["deliberat", "falsif", "candidate", "competing", "challenger", "analysis plan", "estimand"]
    }

    for cap_key, keywords in keywords_map.items():
        score = sum(1 for kw in keywords if kw in q_lower)
        if score > best_score:
            best_score = score
            best_match = cap_key

    if not best_match:
        best_match = "descriptive_statistics"

    entry = CAPABILITY_REGISTRY[best_match]
    return {
        "capability": best_match,
        "skill": entry["skill"],
        "skill_path": f".agents/skills/{entry['skill']}/SKILL.md",
        "agent": entry["agent"],
        "agent_spec": f".agents/agents/{entry['agent']}.md",
        "description": entry["description"],
        "allowed_tools": entry["tools"]
    }


def check_prerequisites(stage_id: str, state_dir: str) -> Dict[str, Any]:
    """Checks whether all disk and stage dependencies are satisfied before delegation."""
    state_dir = os.path.abspath(state_dir)
    if not os.path.exists(state_dir):
        return {"status": "BLOCKED", "stage_id": stage_id, "errors": [f"State directory not found: {state_dir}"]}

    if stage_id not in STAGE_DEPENDENCIES:
        return {"status": "READY", "stage_id": stage_id, "notes": "Unregistered micro-stage; proceeding without strict DAG constraints."}

    meta = STAGE_DEPENDENCIES[stage_id]
    missing_files = []
    for rel_file in meta["required_files"]:
        f_path = os.path.join(state_dir, rel_file)
        if not os.path.exists(f_path):
            missing_files.append(rel_file)

    # Check prior stage if required
    req_stage = meta["required_stage"]
    stage_satisfied = True
    stage_error = None
    if req_stage:
        proj_file = os.path.join(state_dir, "project.json")
        if os.path.exists(proj_file):
            try:
                with open(proj_file, "r", encoding="utf-8") as f:
                    proj = json.load(f)
                curr = proj.get("current_stage", "")
                # If current stage is earlier than required stage, flag error
                # In academic pipeline, check if output files of required stage exist
            except Exception:
                pass

    if missing_files:
        return {
            "status": "BLOCKED",
            "stage_id": stage_id,
            "title": meta["title"],
            "assigned_agent": CAPABILITY_REGISTRY[meta["capability"]]["agent"],
            "required_skill": CAPABILITY_REGISTRY[meta["capability"]]["skill"],
            "missing_prerequisites": missing_files,
            "remedy": f"Generate missing prerequisite artifacts: {missing_files} before delegating {stage_id}."
        }

    return {
        "status": "READY",
        "stage_id": stage_id,
        "title": meta["title"],
        "assigned_agent": CAPABILITY_REGISTRY[meta["capability"]]["agent"],
        "required_skill": CAPABILITY_REGISTRY[meta["capability"]]["skill"],
        "skill_path": f".agents/skills/{CAPABILITY_REGISTRY[meta['capability']]['skill']}/SKILL.md",
        "missing_prerequisites": []
    }


def format_delegation_envelope(stage_id: str, state_dir: str, task_instructions: str) -> Dict[str, Any]:
    """Generates an isolated context delegation envelope ready for invoke_subagent."""
    prereq = check_prerequisites(stage_id, state_dir)
    if prereq["status"] == "BLOCKED":
        return prereq

    agent_name = prereq["assigned_agent"]
    skill_name = prereq["required_skill"]
    skill_path = prereq["skill_path"]

    try:
        from scripts.delegation_contract_engine import create_delegation_contract, format_delegation_prompt
    except ImportError:
        from delegation_contract_engine import create_delegation_contract, format_delegation_prompt

    contract = create_delegation_contract(
        task_id=f"TSK-{stage_id}",
        parent_agent="academic-orchestrator",
        worker_agent=agent_name,
        objective=f"Execute stage '{stage_id}' ({prereq['title']}) using skill '{skill_name}': {task_instructions}",
        inputs=[os.path.join(state_dir, "project.json")] if os.path.exists(os.path.join(state_dir, "project.json")) else [state_dir],
        required_artifacts=[
            f"{state_dir}/outputs/{stage_id}.docx",
            f"{state_dir}/outputs/{stage_id}.md",
            f"{state_dir}/outputs/{stage_id}.json"
        ],
        acceptance_criteria=[
            "Generate synchronized triad artifacts on disk in outputs/: .docx, .md, .json",
            "Extract exact empirical statistics without mental calculation",
            "Verify complete consistency across all reporting formats"
        ],
        constraints=[
            "Never calculate statistics in LLM memory. Run deterministic scripts via run_command.",
            "Strictly use ASCII English filenames (Directive 6).",
            f"Required Skill: `{skill_name}` (Call `view_file` on `{skill_path}` first)."
        ],
        verification_method="statistical-auditor" if "stat" in agent_name else "validation-agent",
        deadline="STAGE_EXECUTION_MILESTONE"
    )

    prompt = format_delegation_prompt(contract)

    return {
        "status": "READY",
        "stage_id": stage_id,
        "agent": agent_name,
        "contract": contract,
        "subagent_invocation": {
            "TypeName": agent_name,
            "Role": f"{agent_name.replace('-', ' ').title()} Specialist",
            "Prompt": prompt
        }
    }


def route_task(description: str, file_count: int = 1, chapter_count: int = 1) -> Dict[str, Any]:
    """Determines whether a task should route to Custom Subagents, /boost, or /teamwork-preview, enriched with complexity levels L0-L4."""
    try:
        from teamwork_boundary_adapter import classify_complexity
        c_meta = classify_complexity(description, file_count=file_count, chapter_count=chapter_count)
        complexity_level = c_meta["complexity_level"]
    except Exception:
        complexity_level = "L1"

    desc_lower = description.lower()

    # Tier 3: Huge Long-Running Projects -> /teamwork-preview
    teamwork_keywords = [
        "20-chapter", "twenty chapter", "multi-chapter monograph",
        "entire dissertation", "full thesis overhaul", "thousands of source files",
        "repository-wide", "multi-study repository", "longitudinal multi-wave overhaul",
        "large project", "complex multi-year"
    ]
    is_teamwork = (
        chapter_count >= 10
        or file_count >= 100
        or any(k in desc_lower for k in teamwork_keywords)
        or complexity_level == "L4"
    )

    if is_teamwork:
        return {
            "tier": "tier_3_teamwork",
            "complexity_level": "L4",
            "recommended_mechanism": "/teamwork-preview",
            "slash_command": "/teamwork-preview",
            "primary_conductor": "Antigravity Teamwork Multi-Agent System",
            "rationale": (
                "Task scope involves extensive multi-chapter restructuring, broad repository audits, "
                "or thousands of source documents. Antigravity Teamwork provides persistent task graphs, "
                "autonomous agent dispatching, and independent background verification."
            ),
            "suggested_action": "Recommend the user invoke `/teamwork-preview` to coordinate autonomous multi-agent teamwork."
        }

    # Tier 2: Hard Isolated Reasoning Problem -> /boost
    boost_keywords = [
        "underidentified", "non-converging", "non-recursive", "mathematical proof",
        "identification equation", "singular matrix", "severe multicollinearity",
        "feedback loop", "derivation", "deep reasoning", "hard reasoning",
        "complex 3-way interaction", "heckman selection correction", "instrumental variable dilemma"
    ]
    is_boost = any(k in desc_lower for k in boost_keywords)

    if is_boost:
        return {
            "tier": "tier_2_boost",
            "complexity_level": complexity_level if complexity_level in ("L2", "L3") else "L2",
            "recommended_mechanism": "/boost",
            "slash_command": "/boost",
            "primary_conductor": "Antigravity Multi-Tier Boost Engine",
            "rationale": (
                "Task presents an isolated, highly non-linear statistical, psychometric, or mathematical dilemma. "
                "Antigravity /boost deploys multi-tier, multi-perspective strategic reasoning and adversarial verification."
            ),
            "suggested_action": "Recommend the user invoke `/boost` for deep multi-perspective reasoning and verification."
        }

    # Tier 1: Ordinary Academic Task -> Custom Subagents via invoke_subagent
    cap_info = resolve_capability(description)
    return {
        "tier": "tier_1_custom_subagents",
        "complexity_level": complexity_level,
        "recommended_mechanism": "invoke_subagent",
        "slash_command": None,
        "primary_conductor": "academic-orchestrator",
        "assigned_subagent": cap_info["agent"],
        "assigned_skill": cap_info["skill"],
        "rationale": (
            "Standard bounded research micro-stage. Managed natively by the Academic Orchestrator coordinating "
            f"specialist subagents (`{cap_info['agent']}`) using isolated context envelopes and academic-state/ artifacts."
        ),
        "suggested_action": f"Delegate bounded task to `{cap_info['agent']}` using native `invoke_subagent`."
    }


def main():
    parser = argparse.ArgumentParser(description="Orchestrator Dependency & Capability Resolver Engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # capability-map
    p_cap = subparsers.add_parser("capability-map", help="Map a task query to required capability, skill, and agent")
    p_cap.add_argument("query", help="Natural language task description")

    # check-prerequisites
    p_pre = subparsers.add_parser("check-prerequisites", help="Verify dependencies for a micro-stage")
    p_pre.add_argument("stage_id", help="Stage identifier (e.g. 01_demographics, 05_macro_model)")
    p_pre.add_argument("--state-dir", required=True, help="Path to academic-state directory")

    # format-delegation
    p_del = subparsers.add_parser("format-delegation", help="Format isolated delegation envelope for invoke_subagent")
    p_del.add_argument("stage_id", help="Stage identifier")
    p_del.add_argument("--state-dir", required=True, help="Path to academic-state directory")
    p_del.add_argument("--instructions", default="Execute statistical analysis and output triad.", help="Task instructions")

    # route-task
    p_route = subparsers.add_parser("route-task", help="Classify task into custom_subagents, boost, or teamwork")
    p_route.add_argument("--description", required=True, help="Task description")
    p_route.add_argument("--file-count", type=int, default=1, help="Estimated number of files involved")
    p_route.add_argument("--chapter-count", type=int, default=1, help="Number of thesis chapters")

    args = parser.parse_args()

    if args.command == "capability-map":
        res = resolve_capability(args.query)
    elif args.command == "check-prerequisites":
        res = check_prerequisites(args.stage_id, args.state_dir)
    elif args.command == "format-delegation":
        res = format_delegation_envelope(args.stage_id, args.state_dir, args.instructions)
    elif args.command == "route-task":
        res = route_task(args.description, args.file_count, args.chapter_count)
    else:
        res = {"error": f"Unknown command {args.command}"}

    print(json.dumps(res, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
