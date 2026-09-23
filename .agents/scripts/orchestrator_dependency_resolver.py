#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/orchestrator_dependency_resolver.py — Authoritative Orchestrator Dependency & State Bridge Engine ("The Hands")

[DEPRECATED DIRECT INVOCATION NOTICE]:
Direct orchestrator script execution is deprecated in favor of native Antigravity lifecycle hooks
and Model B deterministic pre-flight routing (scripts/academic_task_router.py).
This module serves as the authoritative orchestrator dependency resolver, state machine transition
gatekeeper (academic_state_manager.py StrictStateMachine), and delegation envelope generator
for backward compatibility across orchestrator tests and legacy execution bridges.
"""

import os
import sys
import re
import json
import argparse
from typing import Dict, Any, List, Optional

# Virtualenv and Root discovery shim
_CURR_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(os.path.dirname(_CURR_DIR)) == ".agents":
    ROOT_DIR = os.path.abspath(os.path.join(_CURR_DIR, "..", ".."))
else:
    ROOT_DIR = os.path.abspath(os.path.join(_CURR_DIR, ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

# Capability to Skill & Agent Mapping Matrix
CAPABILITY_REGISTRY = {
    "data_simulation": {
        "description": "Monte Carlo psychometric data generation, SEM/CFA latent simulation, Likert quantization",
        "skill": "psychometric-data-simulator",
        "agent": "data-agent",
        "tools": ["run_command", "view_file", "write_to_file"]
    },
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

# Synchronize with authoritative capabilities.yaml via academic_task_router if available
try:
    from academic_task_router import _GLOBAL_REGISTRY
    _auth_caps = _GLOBAL_REGISTRY.all_capabilities()
    for _cid, _cdata in _auth_caps.items():
        if _cid not in CAPABILITY_REGISTRY:
            _skills = _cdata.get("required_skills", ["academic-suite-orchestrator"])
            _agent = _cdata.get("primary_agent", "statistics-agent")
            _tools = ["view_file", "write_to_file"] if _agent == "academic-writer" else ["run_command", "view_file", "write_to_file"]
            CAPABILITY_REGISTRY[_cid] = {
                "description": _cdata.get("description", f"Authoritative capability {_cid}"),
                "skill": _skills[0] if _skills else "academic-suite-orchestrator",
                "agent": _agent,
                "tools": _tools
            }
except Exception:
    pass

# Micro-Stage Prerequisite Graph
STAGE_DEPENDENCIES = {
    "00_data_generation": {
        "title": "Monte Carlo Psychometric Simulation & Data Making",
        "capability": "data_simulation",
        "required_files": ["project.json", "requirements.json"],
        "required_stage": None
    },
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

# Canonical Micro-Stage Sequence Order for progression comparison
STAGE_ORDER: Dict[str, int] = {
    "00_data_curation": 0,
    "01_demographics": 1,
    "02_reliability": 2,
    "03_parametric_assumptions": 3,
    "04_statistical_deliberation": 4,
    "04_bivariate_correlations": 4,
    "05_macro_model": 5,
    "06_hypothesis_testing": 6,
    "07_mediation_analysis": 7,
    "08_chapter_summary": 8,
    "09_validation_audit": 9,
    "10_chapter_assembly": 10
}


def resolve_capability(query: str) -> Dict[str, Any]:
    """Finds the best matching capability, skill, and specialist agent for a task description."""
    q_lower = query.lower()
    best_match = None
    best_score = 0

    keywords_map = {
        "data_simulation": ["simulate", "simulation", "monte carlo", "synthetic data", "create data", "generate data", "make data", "simdat", "data making"],
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
    """
    Checks whether all disk artifacts and state machine transitions are satisfied before delegation.
    Enforces Directive 19: State machine authorizes transition & Artifact manifest defines completion.
    """
    state_dir = os.path.abspath(state_dir)
    if not os.path.exists(state_dir):
        err = f"State directory not found: {state_dir}"
        return {
            "status": "BLOCKED",
            "stage_id": stage_id,
            "errors": [err],
            "missing_prerequisites": [err],
            "missing_files": [err],
            "unmet_stages": []
        }

    if stage_id not in STAGE_DEPENDENCIES:
        return {
            "status": "READY",
            "stage_id": stage_id,
            "notes": "Unregistered micro-stage; proceeding without strict DAG constraints."
        }

    meta = STAGE_DEPENDENCIES[stage_id]
    missing_files: List[str] = []
    unmet_stages: List[str] = []

    # 1. Physical artifact prerequisites verification
    for rel_file in meta["required_files"]:
        f_path = os.path.join(state_dir, rel_file)
        if not os.path.exists(f_path):
            proj_root = os.path.dirname(state_dir)
            alt_path = os.path.join(proj_root, rel_file)
            if not os.path.exists(alt_path):
                missing_files.append(rel_file)

    # 2. Authoritative State Machine Transition Verification (Directive 19)
    req_stage = meta.get("required_stage")
    if req_stage:
        curr_state_path = os.path.join(state_dir, "current_state.json")
        events_path = os.path.join(state_dir, "events.jsonl")
        proj_file = os.path.join(state_dir, "project.json")
        state_machine_checked = False

        # Source A: Check StrictStateMachine ledger (current_state.json)
        if os.path.exists(curr_state_path):
            try:
                with open(curr_state_path, "r", encoding="utf-8") as f:
                    cs = json.load(f)
                stages = cs.get("stages", {})
                if req_stage in stages:
                    state_machine_checked = True
                    dep_st = stages[req_stage].get("status", "").upper()
                    if dep_st not in ("STAGE_APPROVED", "NEXT_STAGE", "COMPLETED", "APPROVED"):
                        unmet_stages.append(
                            f"Prerequisite stage '{req_stage}' state machine status is '{dep_st}' (must be STAGE_APPROVED)"
                        )
            except Exception:
                pass

        # Source B: Check project.json (completed_stages list or progressive current_stage)
        if not state_machine_checked and os.path.exists(proj_file):
            try:
                with open(proj_file, "r", encoding="utf-8") as f:
                    proj = json.load(f)
                completed_stages = proj.get("completed_stages", [])
                if completed_stages:
                    if req_stage not in completed_stages:
                        unmet_stages.append(
                            f"Prerequisite stage '{req_stage}' not found in project completed_stages: {completed_stages}"
                        )
                else:
                    curr_stage = proj.get("current_stage", "")
                    proj_status = proj.get("status", "")
                    if curr_stage:
                        req_order = STAGE_ORDER.get(req_stage)
                        curr_stage_clean = curr_stage.lower()
                        curr_order = None
                        for s_name, s_idx in STAGE_ORDER.items():
                            if s_name in curr_stage_clean or s_name.split("_")[0] in curr_stage_clean:
                                curr_order = s_idx
                                break

                        if curr_order is not None and req_order is not None:
                            if curr_order < req_order:
                                unmet_stages.append(
                                    f"Project current stage '{curr_stage}' (order {curr_order}) is earlier than prerequisite stage '{req_stage}' (order {req_order})"
                                )
                            elif curr_order == req_order and proj_status not in ("stage_completed", "completed", "approved", "STAGE_APPROVED"):
                                unmet_stages.append(
                                    f"Project is at prerequisite stage '{curr_stage}' but status is '{proj_status}' (must be stage_completed)"
                                )
            except Exception:
                pass

        # Source C: Check events.jsonl for rejection or blockage
        if os.path.exists(events_path) and not unmet_stages:
            try:
                with open(events_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if not line.strip():
                            continue
                        ev = json.loads(line)
                        if ev.get("stage_id") == req_stage:
                            ev_type = ev.get("event_type", "").upper()
                            if ev_type in ("STAGE_FAILED", "STAGE_REJECTED", "STAGE_BLOCKED"):
                                unmet_stages.append(
                                    f"Event ledger recorded '{ev_type}' for prerequisite stage '{req_stage}'"
                                )
                                break
            except Exception:
                pass

    all_missing = missing_files + unmet_stages
    if all_missing:
        return {
            "status": "BLOCKED",
            "stage_id": stage_id,
            "title": meta["title"],
            "assigned_agent": CAPABILITY_REGISTRY[meta["capability"]]["agent"],
            "required_skill": CAPABILITY_REGISTRY[meta["capability"]]["skill"],
            "missing_prerequisites": all_missing,
            "missing_files": missing_files,
            "unmet_stages": unmet_stages,
            "remedy": f"Satisfy prerequisite requirements before delegating {stage_id}: {all_missing}"
        }

    return {
        "status": "READY",
        "stage_id": stage_id,
        "title": meta["title"],
        "assigned_agent": CAPABILITY_REGISTRY[meta["capability"]]["agent"],
        "required_skill": CAPABILITY_REGISTRY[meta["capability"]]["skill"],
        "skill_path": f".agents/skills/{CAPABILITY_REGISTRY[meta['capability']]['skill']}/SKILL.md",
        "missing_prerequisites": [],
        "satisfied_stage": req_stage
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


def generate_data_blueprint(
    requirements_or_prompt: Any = "SEM model with 3 latents",
    model_family: Optional[str] = None,
    sample_size: Optional[int] = None,
    seed: Optional[int] = None,
    scale_bounds: Optional[List[int]] = None,
    estimator: Optional[str] = None,
    include_latents: Optional[bool] = None,
    latents: Optional[List[Dict[str, Any]]] = None,
    structural_paths: Optional[List[str]] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Generates a formal, structured Pre-Execution Data Blueprint (Stage DS.0).
    Allows the academic-orchestrator to present the exact model specification,
    dataset parameters, and micro-stage roadmap to the user prior to execution.
    """
    req_dict: Dict[str, Any] = {}
    prompt_str = ""

    if isinstance(requirements_or_prompt, dict):
        req_dict = dict(requirements_or_prompt)
        prompt_str = req_dict.get("description", "") or req_dict.get("prompt", "")
    elif isinstance(requirements_or_prompt, str):
        if os.path.isfile(requirements_or_prompt):
            try:
                with open(requirements_or_prompt, "r", encoding="utf-8") as f:
                    req_dict = json.load(f)
                    prompt_str = req_dict.get("description", "") or req_dict.get("prompt", "")
            except Exception:
                prompt_str = requirements_or_prompt
        elif requirements_or_prompt.strip().startswith("{") and requirements_or_prompt.strip().endswith("}"):
            try:
                req_dict = json.loads(requirements_or_prompt)
                prompt_str = req_dict.get("description", "") or req_dict.get("prompt", "")
            except Exception:
                prompt_str = requirements_or_prompt
        else:
            prompt_str = requirements_or_prompt

    # Extract sample size
    if sample_size is None:
        if "sample_size" in req_dict:
            sample_size = int(req_dict["sample_size"])
        elif "N" in req_dict:
            sample_size = int(req_dict["N"])
        elif "n" in req_dict:
            sample_size = int(req_dict["n"])
        elif prompt_str:
            m = re.search(r'\b(?:n\s*=\s*|sample\s*size\s*(?:of\s*)?|(\d{2,4})\s*(?:participants|samples|cases|subjects|respondents))\b', prompt_str, re.IGNORECASE)
            if m:
                val = m.group(1) or re.search(r'\b(\d{2,4})\b', m.group(0)).group(1)
                sample_size = int(val)
    if sample_size is None:
        sample_size = 250

    # Extract model family
    prompt_lower = (prompt_str or "").lower()
    if model_family is None:
        if "model_family" in req_dict:
            model_family = req_dict["model_family"]
        elif "model" in req_dict:
            model_family = req_dict["model"]
        elif "cfa" in prompt_lower or "confirmatory factor" in prompt_lower:
            model_family = "cfa"
        elif any(k in prompt_lower for k in ["rct", "pre-post", "trial", "intervention", "control group"]):
            model_family = "rct"
        elif "regression" in prompt_lower or "hierarchical" in prompt_lower:
            model_family = "regression"
        else:
            model_family = "sem"

    model_family = model_family.lower()

    # Seed
    if seed is None:
        seed = int(req_dict.get("seed", 42))

    # Scale bounds
    if scale_bounds is None:
        scale_bounds = req_dict.get("scale_bounds", [1, 5])

    # Estimator
    if estimator is None:
        estimator = req_dict.get("estimator", "WLSMV" if model_family in ("sem", "cfa") else "ML")

    # Include latents
    if include_latents is None:
        include_latents = req_dict.get("include_latents", True)

    # Latents & Structural Specification
    if latents is None and "latents" in req_dict:
        latents = req_dict["latents"]
    if structural_paths is None and "structural_paths" in req_dict:
        structural_paths = req_dict["structural_paths"]

    if latents is None:
        if model_family == "sem":
            latents = [
                {
                    "name": "F1_Predictor",
                    "label": "Exogenous Predictor Construct",
                    "indicator_count": 4,
                    "indicators": ["x1", "x2", "x3", "x4"],
                    "target_loadings": [0.72, 0.78, 0.81, 0.75],
                    "target_mean": 3.45,
                    "target_sd": 0.82
                },
                {
                    "name": "F2_Mediator",
                    "label": "Intervening Mediator Construct",
                    "indicator_count": 4,
                    "indicators": ["m1", "m2", "m3", "m4"],
                    "target_loadings": [0.70, 0.84, 0.79, 0.73],
                    "target_mean": 3.60,
                    "target_sd": 0.78
                },
                {
                    "name": "F3_Criterion",
                    "label": "Endogenous Criterion Construct",
                    "indicator_count": 4,
                    "indicators": ["y1", "y2", "y3", "y4"],
                    "target_loadings": [0.76, 0.82, 0.85, 0.69],
                    "target_mean": 3.30,
                    "target_sd": 0.85
                }
            ]
            structural_paths = structural_paths or [
                "F2_Mediator ~ 0.42 * F1_Predictor",
                "F3_Criterion ~ 0.48 * F2_Mediator + 0.28 * F1_Predictor"
            ]
        elif model_family == "cfa":
            latents = [
                {
                    "name": "F1_Factor1",
                    "label": "Latent Dimension 1",
                    "indicator_count": 4,
                    "indicators": ["item1", "item2", "item3", "item4"],
                    "target_loadings": [0.70, 0.75, 0.80, 0.72],
                    "target_mean": 3.50,
                    "target_sd": 0.80
                },
                {
                    "name": "F2_Factor2",
                    "label": "Latent Dimension 2",
                    "indicator_count": 4,
                    "indicators": ["item5", "item6", "item7", "item8"],
                    "target_loadings": [0.68, 0.82, 0.76, 0.71],
                    "target_mean": 3.40,
                    "target_sd": 0.85
                }
            ]
            structural_paths = structural_paths or [
                "F1_Factor1 ~~ 0.38 * F2_Factor2"
            ]
        elif model_family == "rct":
            latents = [
                {
                    "name": "Control_Group",
                    "label": "Control Group Pre/Post Measures",
                    "indicator_count": 2,
                    "indicators": ["pre_test", "post_test"],
                    "target_loadings": [1.0, 1.0],
                    "target_mean": 24.50,
                    "target_sd": 4.20
                },
                {
                    "name": "Intervention_Group",
                    "label": "Intervention Group Pre/Post Measures",
                    "indicator_count": 2,
                    "indicators": ["pre_test", "post_test"],
                    "target_loadings": [1.0, 1.0],
                    "target_mean": 31.20,
                    "target_sd": 4.10
                }
            ]
            structural_paths = structural_paths or [
                "post_test ~ 0.65 * pre_test + group_effect (d = 0.75)"
            ]
        else:
            latents = [
                {
                    "name": "Predictors",
                    "label": "Independent Predictor Set",
                    "indicator_count": 3,
                    "indicators": ["x1", "x2", "x3"],
                    "target_loadings": [1.0, 1.0, 1.0],
                    "target_mean": 0.0,
                    "target_sd": 1.0
                }
            ]
            structural_paths = structural_paths or [
                "y ~ 0.35 * x1 + 0.28 * x2 - 0.20 * x3"
            ]

    # Pipeline Roadmap
    pipeline_roadmap = [
        {
            "stage": "DS.0",
            "name": "Pre-Execution Model Blueprint & Confirmation Gate",
            "assigned_agent": "academic-orchestrator",
            "capability": "orchestrator_dependency_resolver.py data-blueprint",
            "deliverables": ["00_model_blueprint.docx", "00_model_blueprint.md", "00_model_blueprint.json"]
        },
        {
            "stage": "DS.1",
            "name": "Simulation Specification & Power Analysis",
            "assigned_agent": "methodology-expert",
            "capability": "gpower_engine.py / methodology-review",
            "deliverables": ["01_simulation_spec.docx", "01_simulation_spec.md", "01_simulation_spec.json"]
        },
        {
            "stage": "DS.2",
            "name": "Instrument Grounding & Factor Weights",
            "assigned_agent": "data-agent",
            "capability": "questionnaire_resolver.py / psychometric-scale-resolver",
            "deliverables": ["02_scales_codebook.docx", "02_scales_codebook.md", "02_scales_codebook.json"]
        },
        {
            "stage": "DS.3",
            "name": "Monte Carlo Simulation & Model Synthesis",
            "assigned_agent": "data-agent",
            "capability": "simdat_engine.py / sem_data_maker.R",
            "deliverables": ["03_simulation_report.docx", "03_simulation_report.md", "03_simulation_results.json", "primary_data.xlsx", "final_data.xlsx"]
        },
        {
            "stage": "DS.4",
            "name": "Data Quality, Distribution & Anomaly Screening",
            "assigned_agent": "statistical-auditor",
            "capability": "data-audit / assumption-testing",
            "deliverables": ["04_data_audit_report.docx", "04_data_audit_report.md", "04_data_audit_report.json"]
        },
        {
            "stage": "DS.5",
            "name": "Data Curation, Codebook & Provenance Handoff",
            "assigned_agent": "data-curator",
            "capability": "data_curation_pipeline.py / data-cleaning",
            "deliverables": ["05_dataset_codebook.docx", "05_dataset_codebook.md", "05_data_provenance.json", "data_curated.xlsx"]
        }
    ]

    confirmation_prompt = (
        "⚠️ Confirmation Gate (Directive 11): Please review this data generation blueprint. "
        "Confirm whether you approve this model specification and pipeline roadmap, or specify any modifications "
        "(e.g. sample size N, indicator counts, target means, factor loadings, structural paths) before Stage DS.1 execution begins."
    )

    return {
        "status": "BLUEPRINT_GENERATED",
        "pipeline": "data_generation",
        "stage": "DS.0",
        "model_family": model_family.upper(),
        "dataset_parameters": {
            "sample_size": sample_size,
            "seed": seed,
            "scale_bounds": scale_bounds,
            "noise_injection": "Uniform(±0.08, ±0.25)",
            "estimator": estimator,
            "include_latents": include_latents
        },
        "structural_specification": {
            "latent_count": len(latents),
            "latents": latents,
            "structural_paths": structural_paths
        },
        "pipeline_roadmap": pipeline_roadmap,
        "expected_artifacts_on_disk": [
            "00_model_blueprint.json",
            "01_simulation_spec.json",
            "primary_data.xlsx",
            "final_data.xlsx",
            "03_simulation_results.json",
            "04_data_audit_report.json",
            "data_curated.xlsx",
            "05_dataset_codebook.docx"
        ],
        "confirmation_prompt": confirmation_prompt
    }


def format_data_blueprint_markdown(blueprint: Dict[str, Any]) -> str:
    """
    Renders a structured Pre-Execution Data Blueprint into clean Markdown
    for conversational display or on-disk documentation (00_model_blueprint.md).
    """
    p = blueprint["dataset_parameters"]
    s = blueprint["structural_specification"]
    lines = [
        "### 📋 Pre-Execution Data Blueprint & Pipeline Roadmap (Stage DS.0)",
        "",
        f"- **Proposed Pipeline**: `{blueprint.get('pipeline', 'data_generation')}`",
        f"- **Target Model Family**: **{blueprint.get('model_family', 'SEM')}**",
        f"- **Sample Size ($N$)**: `{p.get('sample_size', 250)}` participants (Deterministic Seed: `{p.get('seed', 42)}`)",
        f"- **Scale Bounds & Decimals**: Discrete Likert integers `{p.get('scale_bounds', [1, 5])}` with empirical decimal noise ({p.get('noise_injection', 'Uniform(±0.08, ±0.25)')})",
        f"- **Estimator & True Latents**: Estimator `{p.get('estimator', 'WLSMV')}`, True Latent Columns: `{'Yes' if p.get('include_latents') else 'No'}`",
        "",
        "#### 📐 Measurement Model Specification:",
        "| Latent Construct | Manifest Indicators | Target Loadings ($\\lambda$) | Target Mean $\\pm$ SD |",
        "| :--- | :--- | :--- | :--- |"
    ]

    for lat in s.get("latents", []):
        name = lat.get("name", "Latent")
        ind_names = ", ".join(lat.get("indicators", []))
        loadings = ", ".join(str(l) for l in lat.get("target_loadings", []))
        m = lat.get("target_mean", 0.0)
        sd = lat.get("target_sd", 1.0)
        lines.append(f"| **{name}** | `{ind_names}` | `{loadings}` | ${m:.2f} \\pm {sd:.2f}$ |")

    lines.append("")
    lines.append("#### 🔗 Structural Model Paths:")
    for path in s.get("structural_paths", []):
        lines.append(f"- `{path}`")

    lines.append("")
    lines.append("#### 🗺️ Execution Roadmap (Stages DS.0 – DS.5):")
    lines.append("| Stage | Stage Name | Assigned Specialist | Capability / Tool | Required Physical Deliverables |")
    lines.append("| :--- | :--- | :--- | :--- | :--- |")

    for st in blueprint.get("pipeline_roadmap", []):
        st_id = st.get("stage", "")
        st_name = st.get("name", "")
        agent = st.get("assigned_agent", "")
        cap = st.get("capability", "")
        delivs = ", ".join(f"`{d}`" for d in st.get("deliverables", []))
        lines.append(f"| **{st_id}** | {st_name} | `{agent}` | `{cap}` | {delivs} |")

    lines.append("")
    lines.append("---")
    lines.append(f"> {blueprint.get('confirmation_prompt', '')}")
    return "\n".join(lines)


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

    # data-blueprint
    p_blue = subparsers.add_parser("data-blueprint", help="Generate and display pre-execution data blueprint (Stage DS.0)")
    p_blue.add_argument("query", nargs="?", default="SEM model with 3 latents", help="Description or requirements for data generation")
    p_blue.add_argument("--sample-size", type=int, default=None, help="Sample size N")
    p_blue.add_argument("--model", default=None, help="Model family (sem, cfa, regression, rct)")
    p_blue.add_argument("--seed", type=int, default=42, help="Random seed")
    p_blue.add_argument("--format", choices=["json", "markdown", "both"], default="both", help="Output format")

    args = parser.parse_args()

    if args.command == "capability-map":
        res = resolve_capability(args.query)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.command == "check-prerequisites":
        res = check_prerequisites(args.stage_id, args.state_dir)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.command == "format-delegation":
        res = format_delegation_envelope(args.stage_id, args.state_dir, args.instructions)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.command == "route-task":
        res = route_task(args.description, args.file_count, args.chapter_count)
        print(json.dumps(res, indent=2, ensure_ascii=False))
    elif args.command == "data-blueprint":
        bp = generate_data_blueprint(
            args.query,
            model_family=args.model,
            sample_size=args.sample_size,
            seed=args.seed
        )
        if args.format == "json":
            print(json.dumps(bp, indent=2, ensure_ascii=False))
        elif args.format == "markdown":
            print(format_data_blueprint_markdown(bp))
        else:
            # both
            print(format_data_blueprint_markdown(bp))
            print("\n<!-- JSON PAYLOAD -->")
            print(json.dumps(bp, indent=2, ensure_ascii=False))
    else:
        print(json.dumps({"error": f"Unknown command {args.command}"}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
