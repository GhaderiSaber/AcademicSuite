#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
contracts/contract_validator.py — Authoritative Contract Validation Engine

Provides schema loading, validation utilities, and structural invariants enforcement
for all 9 AcademicSuite contract schemas.
"""

import os
import sys
import json
from typing import Dict, Any, List, Optional, Union

# Auto-discovery of virtualenv and system python dist-packages
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

# Fallback to system dist-packages if jsonschema not in venv
try:
    import jsonschema
except ImportError:
    for p in ["/usr/lib/python3/dist-packages", "/usr/local/lib/python3/dist-packages"]:
        if os.path.exists(p) and p not in sys.path:
            sys.path.append(p)
    try:
        import jsonschema
    except ImportError:
        jsonschema = None

CONTRACTS_DIR = os.path.dirname(os.path.abspath(__file__))

SCHEMA_FILES = {
    "analysis_plan": "analysis_plan.schema.json",
    "artifact_manifest": "artifact_manifest.schema.json",
    "event": "event.schema.json",
    "milestone_state": "milestone_state.schema.json",
    "approval": "approval.schema.json",
    "validation_report": "validation_report.schema.json",
    "handoff": "handoff.schema.json",
    "pitfall": "pitfall.schema.json",
    "execution_manifest": "execution_manifest.schema.json",
    "methodology_decision_record": "methodology_decision_record.schema.json",
    "statistical_executor_contract": "statistical_executor_contract.schema.json",
    "statistical_execution_result": "statistical_execution_result.schema.json",
    "teamwork_boundary": "teamwork_boundary.schema.json",
    # Evolution & Continuous Self-Improvement Contracts
    "experience": "evolution/experience.schema.json",
    "trajectory": "evolution/trajectory.schema.json",
    "feedback": "evolution/feedback.schema.json",
    "lesson": "evolution/lesson.schema.json",
    "knowledge_item": "evolution/knowledge_item.schema.json",
    "exemplar": "evolution/exemplar.schema.json",
    "anti_pattern": "evolution/anti_pattern.schema.json",
    "skill_memory_record": "evolution/skill_memory_record.schema.json",
    "improvement_candidate": "evolution/improvement_candidate.schema.json",
    "evaluation_case": "evolution/evaluation_case.schema.json",
    "evaluation_result": "evolution/evaluation_result.schema.json",
    "promotion_decision": "evolution/promotion_decision.schema.json",
    "capability_profile": "evolution/capability_profile.schema.json",
    "curriculum_task": "evolution/curriculum_task.schema.json",
    "contradiction_record": "evolution/contradiction_record.schema.json",
    "behavioral_profile": "evolution/behavioral_profile.schema.json",
    "drift_report": "evolution/drift_report.schema.json",
    "behavior_analysis": "evolution/behavior_analysis.schema.json",
    "three_way_evaluation": "evolution/three_way_evaluation.schema.json",
    "component_version": "evolution/component_version.schema.json"
}


def load_schema(schema_key_or_filename: str) -> Dict[str, Any]:
    """Loads a contract schema by key (e.g. 'approval') or filename."""
    fname = SCHEMA_FILES.get(schema_key_or_filename, schema_key_or_filename)
    if not fname.endswith(".json"):
        fname += ".schema.json"
    
    path = os.path.join(CONTRACTS_DIR, fname)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Contract schema not found: {path}")
        
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def validate_contract(instance: Dict[str, Any], schema_key: str) -> Dict[str, Any]:
    """
    Validates a data instance against the target contract schema.
    Returns a structured verdict report.
    """
    if jsonschema is None:
        return {
            "valid": False,
            "verdict": "UNKNOWN",
            "errors": ["jsonschema library is not available in python environment."]
        }

    try:
        schema = load_schema(schema_key)
    except Exception as e:
        return {
            "valid": False,
            "verdict": "FAIL",
            "errors": [f"Failed to load schema for '{schema_key}': {str(e)}"]
        }

    validator = jsonschema.Draft7Validator(schema)
    errors = []
    for err in validator.iter_errors(instance):
        path_str = " -> ".join([str(p) for p in err.path]) if err.path else "root"
        errors.append(f"[{path_str}] {err.message}")

    return {
        "valid": len(errors) == 0,
        "verdict": "PASS" if len(errors) == 0 else "FAIL",
        "errors": errors,
        "contract_schema": SCHEMA_FILES.get(schema_key, schema_key)
    }


def validate_analysis_plan(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "analysis_plan")


def validate_artifact_manifest(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "artifact_manifest")


def validate_event(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "event")


def validate_milestone_state(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "milestone_state")


def validate_approval(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "approval")


def validate_validation_report(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "validation_report")


def validate_handoff(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "handoff")


def validate_pitfall(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "pitfall")


def validate_execution_manifest(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "execution_manifest")


def validate_analysis_candidate(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "analysis_candidate")


def validate_experience(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "experience")


def validate_trajectory(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "trajectory")


def validate_feedback(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "feedback")


def validate_lesson(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "lesson")


def validate_knowledge_item(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "knowledge_item")


def validate_exemplar(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "exemplar")


def validate_anti_pattern(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "anti_pattern")


def validate_skill_memory_record(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "skill_memory_record")


def validate_improvement_candidate(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "improvement_candidate")


def validate_evaluation_case(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "evaluation_case")


def validate_evaluation_result(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "evaluation_result")


def validate_promotion_decision(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "promotion_decision")


def validate_capability_profile(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "capability_profile")


def validate_curriculum_task(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "curriculum_task")


def validate_contradiction_record(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "contradiction_record")


def validate_behavioral_profile(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "behavioral_profile")


def validate_drift_report(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "drift_report")


def validate_methodology_decision_record(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "methodology_decision_record")


def validate_statistical_executor_contract(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "statistical_executor_contract")


def validate_statistical_execution_result(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "statistical_execution_result")


def validate_behavior_analysis(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "behavior_analysis")


def validate_three_way_evaluation(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "three_way_evaluation")


def validate_component_version(instance: Dict[str, Any]) -> Dict[str, Any]:
    return validate_contract(instance, "component_version")

