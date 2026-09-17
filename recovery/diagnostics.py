#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
recovery/diagnostics.py — Automated Failure Diagnostics & Root-Cause Classifier

Analyzes error messages, tracebacks, validator outputs, and execution logs
to categorize failures into one of the 7 canonical types with high fidelity.
"""

import re
from typing import Dict, Any, Optional, List
from recovery.taxonomy import FailureType, FailureSeverity


# Diagnostic signature patterns mapped to FailureType
SIGNATURE_PATTERNS: List[Dict[str, Any]] = [
    # 1. PERMISSION signatures (high priority)
    {
        "type": FailureType.PERMISSION,
        "patterns": [
            r"permission\s*denied",
            r"permissionerror",
            r"errno\s*13",
            r"read-only\s*file\s*system",
            r"access\s*is\s*denied",
            r"admin\s*approval\s*required",
            r"human\s*gate"
        ],
        "severity": FailureSeverity.HIGH,
        "summary": "File system access restriction or admin approval gate requirement detected."
    },
    # 2. AGENT signatures
    {
        "type": FailureType.AGENT,
        "patterns": [
            r"failed_precondition.*user location is not supported",
            r"subagent\s*(timeout|timed\s*out)",
            r"conversationid.*not\s*found",
            r"rate\s*limit\s*exceeded",
            r"token\s*limit",
            r"unrecognized\s*subagent",
            r"invalid\s*delegation\s*envelope"
        ],
        "severity": FailureSeverity.HIGH,
        "summary": "Agent communication, delegation envelope, or subagent runtime infrastructure failure."
    },
    # 3. TOOL signatures (environment, missing scripts, runtime exceptions)
    {
        "type": FailureType.TOOL,
        "patterns": [
            r"rscript.*(not\s*found|failed)",
            r"command\s*not\s*found",
            r"modulenotfounderror",
            r"importerror",
            r"syntaxerror",
            r"calledprocesserror",
            r"exit\s*code\s*(127|126)",
            r"filenotfounderror:\s*\[errno\s*2\]",
            r"r\s*error",
            r"lavaan.*package.*missing",
            r"timeout\s*expired",
            r"connection\s*refused"
        ],
        "severity": FailureSeverity.HIGH,
        "summary": "Execution script failure, missing package/dependency, or CLI runtime environment error."
    },
    # 4. STATISTICAL signatures (estimation, non-convergence, matrix issues)
    {
        "type": FailureType.STATISTICAL,
        "patterns": [
            r"did\s*not\s*converge",
            r"convergence\s*failed",
            r"maximum\s*iterations\s*exceeded",
            r"non-positive\s*definite",
            r"singular\s*matrix",
            r"negative\s*(error\s*)?variance",
            r"heywood\s*case",
            r"vif\s*>\s*10",
            r"extreme\s*multicollinearity",
            r"cov_matrix.*not\s*invertible",
            r"negative\s*eigenvalue",
            r"optimizer\s*failed"
        ],
        "severity": FailureSeverity.MEDIUM,
        "summary": "Inferential/structural model estimation failure, non-convergence, or boundary violation."
    },
    # 5. METHODOLOGICAL signatures (design, degrees of freedom, hypothesis mismatch)
    {
        "type": FailureType.METHODOLOGICAL,
        "patterns": [
            r"degrees\s*of\s*freedom\s*mismatch",
            r"df\s*error",
            r"underpowered\s*sample",
            r"inappropriate\s*statistical\s*test",
            r"untested\s*hypothesis",
            r"orphan\s*hypothesis",
            r"paired\s*design\s*violation",
            r"sample\s*size\s*breakdown\s*discrepancy"
        ],
        "severity": FailureSeverity.HIGH,
        "summary": "Research design mismatch, degrees of freedom error, or hypothesis-test divergence."
    },
    # 6. VALIDATION signatures (reporting consistency, typography, schema conformance)
    {
        "type": FailureType.VALIDATION,
        "patterns": [
            r"reporting_consistency",
            r"prohibited\s*p\s*=\s*\.?000",
            r"persian\s*leading\s*zero",
            r"3-table\s*standard",
            r"sem\s*macro\s*reporting",
            r"forbidden\s*robotic\s*ai\s*cliché",
            r"numerical_consistency",
            r"result_consistency",
            r"schema\s*validation\s*error"
        ],
        "severity": FailureSeverity.MEDIUM,
        "summary": "Quality control, typography, or reporting standard verification failure."
    },
    # 7. DATA signatures (raw inputs, unengaged responses, missing values)
    {
        "type": FailureType.DATA,
        "patterns": [
            r"missing\s*rate\s*>\s*0",
            r"data_integrity",
            r"unengaged\s*responses?",
            r"straight-lining",
            r"multivariate\s*outliers?",
            r"mahalanobis",
            r"column\s*['\"].*['\"]\s*not\s*found",
            r"cannot\s*convert\s*string\s*to\s*float",
            r"zero\s*variance\s*item",
            r"empty\s*dataset"
        ],
        "severity": FailureSeverity.HIGH,
        "summary": "Dataset screening failure: unengaged responses, excessive missingness, or corrupted schema."
    }
]


def diagnose_failure(error_text: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Diagnoses an error and returns failure classification, severity, and root-cause summary.
    """
    error_clean = error_text.strip()
    matched_type = None
    matched_severity = FailureSeverity.MEDIUM
    matched_summary = "Unclassified failure encountered during execution."

    # Heuristic pattern search
    for sig in SIGNATURE_PATTERNS:
        for p in sig["patterns"]:
            if re.search(p, error_clean, re.IGNORECASE):
                matched_type = sig["type"]
                matched_severity = sig["severity"]
                matched_summary = sig["summary"]
                break
        if matched_type:
            break

    # Contextual overrides (if validator output was passed directly)
    if not matched_type and context:
        val_name = context.get("validator")
        if val_name in ["reporting_consistency", "result_consistency", "numerical_consistency"]:
            matched_type = FailureType.VALIDATION
            matched_severity = FailureSeverity.MEDIUM
            matched_summary = f"Verification failure raised by validator '{val_name}'."
        elif val_name == "data_integrity":
            matched_type = FailureType.DATA
            matched_severity = FailureSeverity.HIGH
            matched_summary = "Data integrity audit failure."

    # Default fallback if unknown
    if not matched_type:
        matched_type = FailureType.TOOL
        matched_severity = FailureSeverity.MEDIUM
        matched_summary = "General execution or tool script failure."

    return {
        "failure_type": matched_type.value if hasattr(matched_type, "value") else str(matched_type),
        "severity": matched_severity.value if hasattr(matched_severity, "value") else str(matched_severity),
        "diagnostic_summary": matched_summary,
        "raw_error": error_clean
    }
