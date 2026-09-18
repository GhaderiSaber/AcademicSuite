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
    "teamwork_boundary": "teamwork_boundary.schema.json"
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
