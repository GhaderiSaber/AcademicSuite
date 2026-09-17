#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
recovery/recovery_engine.py — Core Failure Recovery Engine ("The Hands")

Coordinates diagnostic evaluation, targeted routing, incident logging,
and verification certification without whole-task restarts.
"""

import os
import sys
import json
from datetime import datetime, timezone
from typing import Dict, Any, Optional

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

from recovery.taxonomy import IncidentStatus
from recovery.diagnostics import diagnose_failure
from recovery.router import route_failure

SCHEMA_PATH = os.path.join(ROOT_DIR, "recovery", "incident_schema.json")


def load_incident_schema() -> Optional[Dict[str, Any]]:
    if os.path.exists(SCHEMA_PATH):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def create_incident(
    stage_id: str,
    error_message: str,
    context: Optional[Dict[str, Any]] = None,
    project_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Creates, validates, and records a structured Failure Incident.
    """
    context = context or {}
    if project_path:
        context["project_path"] = project_path

    # 1. Diagnose
    diag = diagnose_failure(error_message, context)
    ftype = diag["failure_type"]
    sev = diag["severity"]
    summary = diag["diagnostic_summary"]

    # 2. Route
    routed = route_failure(ftype, stage_id, error_message, context)
    routing_plan = routed["routing_plan"]
    preserved = routed["preserved_upstream_stages"]

    # 3. Generate Incident ID
    now = datetime.now(timezone.utc)
    ts_str = now.strftime("%Y%m%d_%H%M%S")
    incident_id = f"INC-{ftype}-{ts_str}"

    incident = {
        "incident_id": incident_id,
        "failure_type": ftype,
        "severity": sev,
        "stage_id": stage_id,
        "status": IncidentStatus.ROUTED.value,
        "error_message": error_message,
        "diagnostic_summary": summary,
        "preserved_upstream_stages": preserved,
        "routing_plan": routing_plan,
        "timestamp": now.isoformat()
    }

    # 4. Schema Validation
    schema = load_incident_schema()
    if schema and jsonschema:
        jsonschema.validate(instance=incident, schema=schema)

    # 5. Persist if project_path provided
    if project_path:
        state_dir = os.path.join(project_path, "academic-state")
        if os.path.isdir(state_dir):
            inc_dir = os.path.join(state_dir, "incidents")
            os.makedirs(inc_dir, exist_ok=True)
            inc_file = os.path.join(inc_dir, f"{incident_id}.json")
            with open(inc_file, "w", encoding="utf-8") as f:
                json.dump(incident, f, indent=2, ensure_ascii=False)

    return incident


def resolve_incident(
    incident: Dict[str, Any],
    verification_verdict: str,
    resolved_by: str = "recovery-engine",
    notes: str = "",
    project_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Resolves an incident following verified remediation.
    """
    now = datetime.now(timezone.utc)
    is_success = verification_verdict.upper() == "PASS"

    incident["status"] = IncidentStatus.RECOVERED.value if is_success else IncidentStatus.FAILED.value
    incident["resolution_details"] = {
        "resolved_at": now.isoformat(),
        "resolved_by": resolved_by,
        "verification_verdict": verification_verdict,
        "notes": notes
    }

    # Schema Validation
    schema = load_incident_schema()
    if schema and jsonschema:
        jsonschema.validate(instance=incident, schema=schema)

    # Persist update
    if project_path:
        state_dir = os.path.join(project_path, "academic-state")
        inc_dir = os.path.join(state_dir, "incidents")
        inc_file = os.path.join(inc_dir, f"{incident['incident_id']}.json")
        if os.path.isdir(inc_dir):
            with open(inc_file, "w", encoding="utf-8") as f:
                json.dump(incident, f, indent=2, ensure_ascii=False)

    return incident


def format_incident_markdown(incident: Dict[str, Any]) -> str:
    """
    Renders an executive markdown summary of the failure and its targeted remediation plan.
    """
    rp = incident.get("routing_plan", {})
    preserved = incident.get("preserved_upstream_stages", [])
    preserved_str = ", ".join(f"`{s}`" for s in preserved) if preserved else "None (Stage 0)"

    lines = [
        f"### ⚠️ Failure Incident Diagnosed: `{incident['incident_id']}`",
        f"- **Failure Type**: **`{incident['failure_type']}`** (Severity: `{incident['severity']}`)",
        f"- **Failed Micro-Stage**: `{incident['stage_id']}`",
        f"- **Diagnostic Summary**: {incident['diagnostic_summary']}",
        f"- **Preserved Upstream Stages**: {preserved_str} *(Zero Whole-Task Restart Enforced)*",
        "",
        "#### 🎯 Targeted Remediation Plan",
        f"- **Assigned Handler**: `{rp.get('assigned_handler')}` ({rp.get('handler_type')})",
        f"- **Recovery Strategy**: `{rp.get('strategy')}`",
        f"- **Remediation Action**: {rp.get('remediation_action')}",
        f"- **Verification Gate**: `{rp.get('verification_gate')}`",
        ""
    ]
    return "\n".join(lines)
