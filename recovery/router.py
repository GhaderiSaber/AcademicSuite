#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
recovery/router.py — Targeted Failure Router & Remediation Plan Generator

Implements the targeted dispatch matrix mapping each failure type to its
specialist recovery handler or subagent, enforcing the Zero Whole-Task Restart invariant.
"""

from typing import Dict, Any, List, Optional
from recovery.taxonomy import FailureType, RecoveryStrategy


STAGE_ORDER: List[str] = [
    "00_data_curation",
    "01_demographics",
    "02_descriptives_and_reliability",
    "03_parametric_assumptions",
    "04_bivariate_correlations",
    "05_macro_model",
    "06_hypothesis_1",
    "07_hypothesis_2",
    "08_hypothesis_3",
    "09_chapter_summary",
    "10_defense_brief"
]


def calculate_preserved_stages(current_stage_id: str, completed_stages: Optional[List[str]] = None) -> List[str]:
    """
    Computes all upstream stages that must be preserved on disk.
    Enforces the Core Anti-Regression Rule: Zero Whole-Task Restart.
    """
    if completed_stages:
        return [s for s in completed_stages if s != current_stage_id]

    # Find position in canonical STAGE_ORDER
    matched_idx = -1
    for i, s in enumerate(STAGE_ORDER):
        if current_stage_id.startswith(s) or s.startswith(current_stage_id):
            matched_idx = i
            break

    if matched_idx > 0:
        return STAGE_ORDER[:matched_idx]
    return []


def route_failure(
    failure_type: str,
    stage_id: str,
    error_message: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Routes a diagnosed failure to its targeted recovery agent or tool handler.
    Does NOT restart previous completed stages.
    """
    context = context or {}
    model_type = context.get("model_type", "general").lower()
    project_path = context.get("project_path", "")
    completed_stages = context.get("completed_stages")
    
    preserved_stages = calculate_preserved_stages(stage_id, completed_stages)
    ft = failure_type.upper()

    if ft == FailureType.DATA.value:
        plan = {
            "assigned_handler": "data-agent",
            "handler_type": "subagent",
            "strategy": RecoveryStrategy.DELEGATE_DATA_AGENT.value,
            "target_stage": "00_data_curation",
            "remediation_action": (
                f"Data Agent must inspect raw dataset, handle missingness (imputation or listwise deletion), "
                f"screen unengaged straight-lining responses, and re-export verified 'data_cleaned.xlsx'. "
                f"Preserve all other stage specifications."
            ),
            "remediation_command": f"python3 .agents/skills/data-audit/scripts/audit_dataset.py --data {project_path}/01_raw_inputs/data_raw.xlsx --output {project_path}/academic-state/data/data_quality.json" if project_path else None,
            "verification_gate": f"python3 validators/data_integrity/validator.py --report {project_path}/academic-state/data/data_quality.json" if project_path else "python3 validators/data_integrity/validator.py"
        }

    elif ft == FailureType.TOOL.value:
        # Tool execution fallback: e.g. R lavaan failure -> Python semopy / statsmodels fallback
        fallback_desc = (
            "Switch to deterministic Python fallback engine (e.g. semopy / statsmodels) "
            "or verify virtualenv dependencies without touching data curation."
            if "sem" in model_type or "r " in error_message.lower() or "lavaan" in error_message.lower()
            else "Re-run tool command with corrected CLI parameters and verified environment path."
        )
        plan = {
            "assigned_handler": "tool_recovery_runner",
            "handler_type": "tool",
            "strategy": RecoveryStrategy.RETRY_TOOL_FALLBACK.value,
            "target_stage": stage_id,
            "remediation_action": fallback_desc,
            "remediation_command": None,
            "verification_gate": f"python3 validators/numerical_consistency/validator.py"
        }

    elif ft == FailureType.STATISTICAL.value:
        plan = {
            "assigned_handler": "statistics-agent",
            "handler_type": "subagent",
            "strategy": RecoveryStrategy.DELEGATE_STATISTICS_AGENT.value,
            "target_stage": stage_id,
            "remediation_action": (
                f"Statistics Agent must adjust estimation hyperparameters: switch from standard ML to robust MLR/MLM estimator, "
                f"constrain error variance boundaries (θ >= 0.001) to prevent Heywood cases, or add correlated residual covariances."
            ),
            "remediation_command": None,
            "verification_gate": f"python3 validators/numerical_consistency/validator.py"
        }

    elif ft == FailureType.METHODOLOGICAL.value:
        plan = {
            "assigned_handler": "methodology-expert",
            "handler_type": "subagent",
            "strategy": RecoveryStrategy.DELEGATE_METHODOLOGY_AGENT.value,
            "target_stage": stage_id,
            "remediation_action": (
                f"Methodology Expert must audit research design alignment, correct degrees of freedom calculations (df = N - k - c), "
                f"and ensure hypothesis testing matches sample grouping and measurement occasions."
            ),
            "remediation_command": None,
            "verification_gate": f"python3 validators/reporting_consistency/validator.py"
        }

    elif ft == FailureType.VALIDATION.value:
        plan = {
            "assigned_handler": "writing-agent",
            "handler_type": "subagent",
            "strategy": RecoveryStrategy.DELEGATE_WRITING_AGENT.value,
            "target_stage": stage_id,
            "remediation_action": (
                f"Writing Agent must repair formatting/typography errors: eliminate prohibited 'p = .000' (enforce '۰.۰۰۱ > p'), "
                f"restore Persian leading zero ('۰.۰۵'), or format missing tables according to the 3-Table Standard without re-estimating statistics."
            ),
            "remediation_command": None,
            "verification_gate": f"python3 validators/reporting_consistency/validator.py"
        }

    elif ft == FailureType.PERMISSION.value:
        plan = {
            "assigned_handler": "digital-saber",
            "handler_type": "human_gate",
            "strategy": RecoveryStrategy.HUMAN_GATE_APPROVAL.value,
            "target_stage": stage_id,
            "remediation_action": (
                f"Escalate to Saber Admin Desk (ID: 124911145) for filesystem permission clearance "
                f"or approval of override decision before proceeding."
            ),
            "remediation_command": None,
            "verification_gate": "python3 scripts/academic_state_manager.py validate"
        }

    elif ft == FailureType.AGENT.value:
        plan = {
            "assigned_handler": "digital-saber",
            "handler_type": "subagent",
            "strategy": RecoveryStrategy.SUBAGENT_RETRY.value,
            "target_stage": stage_id,
            "remediation_action": (
                f"Antigravity Lead Orchestrator must re-synthesize the delegation envelope with a refined, "
                f"deterministic task prompt, or fall back to an active idle subagent."
            ),
            "remediation_command": None,
            "verification_gate": "python3 scripts/academic_state_manager.py validate"
        }

    else:
        plan = {
            "assigned_handler": "digital-saber",
            "handler_type": "subagent",
            "strategy": RecoveryStrategy.RETRY_TOOL_FALLBACK.value,
            "target_stage": stage_id,
            "remediation_action": "General recovery fallback: retry isolated stage.",
            "remediation_command": None,
            "verification_gate": "python3 validators/run_all_validators.py"
        }

    return {
        "routing_plan": plan,
        "preserved_upstream_stages": preserved_stages
    }
