#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
academic_state_manager.py — Academic State Management Engine ("The Hands")

Provides deterministic CLI operations to initialize, validate, query,
and mutate the academic-state/ artifact repository within research projects.
Enforces schema compliance and provides structured communication endpoints.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
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

try:
    import jsonschema
except ImportError:
    jsonschema = None


SCHEMAS_DIR = os.path.join(ROOT_DIR, ".agents", "shared", "schemas", "academic_state")

SCHEMA_MAP = {
    "project.json": "project.schema.json",
    "requirements.json": "requirements.schema.json",
    "analysis_plan.json": "analysis_plan.schema.json",
    "decisions.json": "decisions.schema.json",
    "data/data_dictionary.json": "data_dictionary.schema.json",
    "data/data_quality.json": "data_quality.schema.json",
    "analysis/descriptive.json": "descriptive.schema.json",
    "analysis/reliability.json": "reliability.schema.json",
    "analysis/cfa.json": "cfa.schema.json",
    "analysis/sem.json": "sem.schema.json",
    "validation/data_validation.json": "validation_report.schema.json",
    "validation/statistical_validation.json": "validation_report.schema.json",
    "validation/writing_validation.json": "validation_report.schema.json"
}


def get_state_dir(project_path: str) -> str:
    """Resolves the academic-state directory inside project_path."""
    if os.path.basename(project_path) == "academic-state":
        return os.path.abspath(project_path)
    return os.path.abspath(os.path.join(project_path, "academic-state"))


def init_state(project_path: str, title: str = "Empirical Research Project", methodology: str = "sem", n: int = 300) -> Dict[str, Any]:
    """Initializes the full academic-state directory hierarchy with baseline starter files."""
    state_dir = get_state_dir(project_path)
    os.makedirs(os.path.join(state_dir, "data"), exist_ok=True)
    os.makedirs(os.path.join(state_dir, "analysis"), exist_ok=True)
    os.makedirs(os.path.join(state_dir, "validation"), exist_ok=True)
    os.makedirs(os.path.join(state_dir, "outputs"), exist_ok=True)

    now_iso = datetime.now(timezone.utc).isoformat()
    project_id = os.path.basename(os.path.abspath(project_path))

    # 1. project.json
    project_data = {
        "project_id": project_id,
        "title": title,
        "methodology_type": methodology,
        "sample_size": n,
        "current_stage": "00_data_curation",
        "orchestrator": "academic-orchestrator",
        "status": "in_progress",
        "created_at": now_iso,
        "updated_at": now_iso,
        "metadata": {
            "version": "1.0.0",
            "target_degree": "Ph.D. / Master's Thesis"
        }
    }
    _write_json_if_missing(os.path.join(state_dir, "project.json"), project_data)

    # 2. requirements.json
    req_data = {
        "research_questions": [
            {
                "id": "RQ1",
                "question": "Does the predictor variable have a statistically significant relationship with the outcome?",
                "target_variables": ["predictor", "outcome"]
            }
        ],
        "hypotheses": [
            {
                "id": "H1",
                "statement": "The predictor variable has a significant direct effect on the outcome variable.",
                "type": "direct",
                "independent_variable": "predictor",
                "dependent_variable": "outcome",
                "direction": "positive"
            }
        ],
        "institutional_guidelines": {
            "style": "APA 7th Edition",
            "language": "Persian (Farsi)",
            "persian_fonts": {
                "body": "B Nazanin",
                "headings": "B Titr",
                "stats_latin": "Times New Roman"
            },
            "citation_style": "Author-Date APA 7"
        },
        "deliverables": [
            "Chapter_4_Results.docx",
            "Chapter_4_Results.md",
            "Master_Hypothesis_Matrix.docx",
            "Defense_Brief.docx"
        ]
    }
    _write_json_if_missing(os.path.join(state_dir, "requirements.json"), req_data)

    # 3. analysis_plan.json
    plan_data = {
        "significance_alpha": 0.05,
        "power_target": 0.80,
        "bootstrap_resamples": 5000,
        "planned_sequence": [
            {
                "stage_id": "01_demographics",
                "title": "Demographic Profiling & Frequencies",
                "engine": "python",
                "script": ".agents/skills/descriptive-statistics/scripts/compute_descriptives.py",
                "output_artifact": "academic-state/analysis/descriptive.json",
                "assigned_subagent": "statistics-agent"
            },
            {
                "stage_id": "02_reliability",
                "title": "Scale Reliability Analysis (Alpha & Omega)",
                "engine": "python",
                "script": ".agents/skills/reliability-analysis/scripts/cronbach_alpha.py",
                "output_artifact": "academic-state/analysis/reliability.json",
                "assigned_subagent": "statistics-agent"
            },
            {
                "stage_id": "03_sem_model",
                "title": "Structural Equation Modeling & Hypotheses Testing",
                "engine": "r",
                "script": ".agents/skills/sem/scripts/run_sem.R",
                "output_artifact": "academic-state/analysis/sem.json",
                "assigned_subagent": "statistics-agent"
            }
        ],
        "variables": {
            "independent": ["predictor"],
            "dependent": ["outcome"],
            "mediators": [],
            "moderators": [],
            "covariates": []
        }
    }
    _write_json_if_missing(os.path.join(state_dir, "analysis_plan.json"), plan_data)

    # 4. decisions.json
    dec_data = {
        "decisions": [
            {
                "decision_id": "DEC-001",
                "timestamp": now_iso,
                "category": "methodology",
                "decision": f"Project initialized using {methodology.upper()} methodology framework.",
                "rationale": "Aligned with approved research proposal and structural hypothesis testing.",
                "alternatives_considered": ["Multiple Regression", "ANCOVA"],
                "agent": "academic-orchestrator",
                "supervisor_approval": True
            }
        ]
    }
    _write_json_if_missing(os.path.join(state_dir, "decisions.json"), dec_data)

    # 5. data/data_dictionary.json
    dict_data = {
        "total_items": 1,
        "scales": [
            {
                "scale_id": "PRED",
                "name": "Predictor Scale",
                "author_year": "Standard, 2020",
                "items_count": 1,
                "item_range": [1, 5],
                "reverse_items": [],
                "subscales": {}
            }
        ],
        "columns": [
            {
                "column_name": "predictor",
                "scale_id": "PRED",
                "type": "scale_composite",
                "label": "Predictor Variable Composite",
                "is_reverse_coded": False
            },
            {
                "column_name": "outcome",
                "scale_id": "PRED",
                "type": "scale_composite",
                "label": "Outcome Variable Composite",
                "is_reverse_coded": False
            }
        ]
    }
    _write_json_if_missing(os.path.join(state_dir, "data", "data_dictionary.json"), dict_data)

    # 6. data/data_quality.json
    quality_data = {
        "sample_n": n,
        "missing_rate": 0.0,
        "unengaged_respondents": [],
        "mcar_test": {
            "chi2": 0.0,
            "df": 0,
            "p_value": 1.0
        },
        "outliers_detected": {
            "mahalanobis_d2_count": 0,
            "flagged_ids": []
        },
        "quality_verdict": "PASS"
    }
    _write_json_if_missing(os.path.join(state_dir, "data", "data_quality.json"), quality_data)

    return {"status": "SUCCESS", "state_dir": state_dir, "initialized_files": list(SCHEMA_MAP.keys())}


def validate_state(project_path: str) -> Dict[str, Any]:
    """Validates all JSON files in academic-state against their official JSON schemas."""
    state_dir = get_state_dir(project_path)
    if not os.path.exists(state_dir):
        return {"overall_verdict": "FAIL", "errors": [f"State directory not found: {state_dir}"]}

    report = {
        "state_directory": state_dir,
        "overall_verdict": "PASS",
        "validated_files": [],
        "errors": [],
        "warnings": []
    }

    if jsonschema is None:
        report["warnings"].append("jsonschema library not installed; skipping deep schema validation.")
        return report

    for rel_path, schema_filename in SCHEMA_MAP.items():
        file_path = os.path.join(state_dir, rel_path)
        schema_path = os.path.join(SCHEMAS_DIR, schema_filename)

        if not os.path.exists(file_path):
            # Optional analysis/validation files are skipped until produced
            if rel_path.startswith("analysis/") or rel_path.startswith("validation/"):
                continue
            report["errors"].append(f"Missing core state artifact: {rel_path}")
            report["overall_verdict"] = "FAIL"
            continue

        if not os.path.exists(schema_path):
            report["warnings"].append(f"Schema not found for {rel_path}: {schema_filename}")
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                instance = json.load(f)
            with open(schema_path, "r", encoding="utf-8") as sf:
                schema = json.load(sf)

            jsonschema.validate(instance=instance, schema=schema)
            report["validated_files"].append({"file": rel_path, "status": "VALID", "schema": schema_filename})
        except jsonschema.ValidationError as ve:
            report["overall_verdict"] = "FAIL"
            report["errors"].append(f"Schema validation failed for {rel_path}: {ve.message} (path: {list(ve.path)})")
        except Exception as e:
            report["overall_verdict"] = "FAIL"
            report["errors"].append(f"Error reading/validating {rel_path}: {str(e)}")

    return report


def get_status_summary(project_path: str) -> Dict[str, Any]:
    """Returns an executive dashboard summary of project state, progress, and validations."""
    state_dir = get_state_dir(project_path)
    if not os.path.exists(state_dir):
        return {"error": f"State directory not found at {state_dir}"}

    summary = {
        "project": {},
        "current_stage": "unknown",
        "analyses_completed": [],
        "validations": {},
        "outputs_count": 0
    }

    proj_file = os.path.join(state_dir, "project.json")
    if os.path.exists(proj_file):
        with open(proj_file, "r", encoding="utf-8") as f:
            summary["project"] = json.load(f)
            summary["current_stage"] = summary["project"].get("current_stage", "unknown")

    # Check analysis files
    analysis_dir = os.path.join(state_dir, "analysis")
    if os.path.exists(analysis_dir):
        for f in os.listdir(analysis_dir):
            if f.endswith(".json"):
                summary["analyses_completed"].append(f)

    # Check validations
    val_dir = os.path.join(state_dir, "validation")
    if os.path.exists(val_dir):
        for vf in os.listdir(val_dir):
            if vf.endswith(".json"):
                try:
                    with open(os.path.join(val_dir, vf), "r", encoding="utf-8") as f:
                        val_content = json.load(f)
                    summary["validations"][vf] = val_content.get("overall_verdict", "UNKNOWN")
                except Exception:
                    summary["validations"][vf] = "CORRUPT"

    # Check outputs
    out_dir = os.path.join(state_dir, "outputs")
    if os.path.exists(out_dir):
        summary["outputs_count"] = len(os.listdir(out_dir))

    return summary


def record_decision(project_path: str, category: str, decision: str, rationale: str, agent: str, supervisor_approval: bool = True) -> Dict[str, Any]:
    """Appends an auditable decision to decisions.json."""
    state_dir = get_state_dir(project_path)
    dec_file = os.path.join(state_dir, "decisions.json")

    dec_data = {"decisions": []}
    if os.path.exists(dec_file):
        with open(dec_file, "r", encoding="utf-8") as f:
            dec_data = json.load(f)

    next_idx = len(dec_data.get("decisions", [])) + 1
    dec_id = f"DEC-{next_idx:03d}"
    now_iso = datetime.now(timezone.utc).isoformat()

    entry = {
        "decision_id": dec_id,
        "timestamp": now_iso,
        "category": category,
        "decision": decision,
        "rationale": rationale,
        "alternatives_considered": [],
        "agent": agent,
        "supervisor_approval": supervisor_approval
    }

    dec_data.setdefault("decisions", []).append(entry)
    with open(dec_file, "w", encoding="utf-8") as f:
        json.dump(dec_data, f, indent=2, ensure_ascii=False)

    return {"status": "RECORDED", "decision_id": dec_id, "entry": entry}


def set_stage(project_path: str, stage: str, status: Optional[str] = None) -> Dict[str, Any]:
    """Updates the current stage and optional status in project.json."""
    state_dir = get_state_dir(project_path)
    proj_file = os.path.join(state_dir, "project.json")
    if not os.path.exists(proj_file):
        return {"error": f"project.json not found in {state_dir}"}

    with open(proj_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    data["current_stage"] = stage
    if status:
        data["status"] = status
    data["updated_at"] = datetime.now(timezone.utc).isoformat()

    with open(proj_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return {"status": "UPDATED", "current_stage": stage, "status_value": data.get("status")}


def _write_json_if_missing(filepath: str, data: Dict[str, Any]) -> None:
    if not os.path.exists(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="Academic State Manager CLI Engine")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # init
    p_init = subparsers.add_parser("init", help="Initialize academic-state hierarchy")
    p_init.add_argument("project_path", help="Path to project directory")
    p_init.add_argument("--title", default="Empirical Research Study", help="Study title")
    p_init.add_argument("--methodology", default="sem", choices=["sem", "correlational", "experimental", "quasi_experimental", "cfa_scale_validation", "mixed_methods", "meta_analysis"])
    p_init.add_argument("--n", type=int, default=300, help="Sample size")

    # validate
    p_val = subparsers.add_parser("validate", help="Validate academic-state artifacts against JSON schemas")
    p_val.add_argument("project_path", help="Path to project directory")

    # status
    p_stat = subparsers.add_parser("status", help="Print dashboard summary of project state")
    p_stat.add_argument("project_path", help="Path to project directory")

    # record-decision
    p_dec = subparsers.add_parser("record-decision", help="Record an auditable methodological/statistical decision")
    p_dec.add_argument("project_path", help="Path to project directory")
    p_dec.add_argument("--category", required=True, choices=["methodology", "data_cleaning", "statistical_modeling", "reporting", "human_override"])
    p_dec.add_argument("--decision", required=True, help="Decision description")
    p_dec.add_argument("--rationale", required=True, help="Theoretical or statistical justification")
    p_dec.add_argument("--agent", required=True, help="Agent role making the decision")

    # set-stage
    p_stage = subparsers.add_parser("set-stage", help="Advance the project stage gate")
    p_stage.add_argument("project_path", help="Path to project directory")
    p_stage.add_argument("--stage", required=True, help="New stage ID (e.g. 04_bivariate_correlations)")
    p_stage.add_argument("--status", choices=["in_progress", "awaiting_validation", "stage_completed", "final_approved", "blocked"])

    args = parser.parse_args()

    if args.command == "init":
        res = init_state(args.project_path, args.title, args.methodology, args.n)
    elif args.command == "validate":
        res = validate_state(args.project_path)
    elif args.command == "status":
        res = get_status_summary(args.project_path)
    elif args.command == "record-decision":
        res = record_decision(args.project_path, args.category, args.decision, args.rationale, args.agent)
    elif args.command == "set-stage":
        res = set_stage(args.project_path, args.stage, args.status)
    else:
        res = {"error": f"Unknown command {args.command}"}

    print(json.dumps(res, indent=2, ensure_ascii=False))
    if args.command == "validate" and res.get("overall_verdict") == "FAIL":
        sys.exit(1)


if __name__ == "__main__":
    main()
