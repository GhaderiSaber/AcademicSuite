#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
recovery/taxonomy.py — Failure Recovery Taxonomy & Enums

Defines the 7 canonical failure types, severity levels, recovery strategies,
and incident lifecycle states for the Academic Suite.
"""

from enum import Enum


class FailureType(str, Enum):
    """The 7 canonical failure types in Academic Suite."""
    DATA = "DATA"
    TOOL = "TOOL"
    STATISTICAL = "STATISTICAL"
    METHODOLOGICAL = "METHODOLOGICAL"
    VALIDATION = "VALIDATION"
    PERMISSION = "PERMISSION"
    AGENT = "AGENT"


class FailureSeverity(str, Enum):
    """Failure severity grading."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RecoveryStrategy(str, Enum):
    """Actionable recovery strategies for targeted remediation."""
    RETRY_TOOL_FALLBACK = "RETRY_TOOL_FALLBACK"
    DELEGATE_DATA_AGENT = "DELEGATE_DATA_AGENT"
    DELEGATE_STATISTICS_AGENT = "DELEGATE_STATISTICS_AGENT"
    DELEGATE_METHODOLOGY_AGENT = "DELEGATE_METHODOLOGY_AGENT"
    DELEGATE_WRITING_AGENT = "DELEGATE_WRITING_AGENT"
    DELEGATE_VALIDATION_AGENT = "DELEGATE_VALIDATION_AGENT"
    HUMAN_GATE_APPROVAL = "HUMAN_GATE_APPROVAL"
    SUBAGENT_RETRY = "SUBAGENT_RETRY"


class IncidentStatus(str, Enum):
    """Lifecycle states of a failure incident."""
    DETECTED = "DETECTED"
    DIAGNOSED = "DIAGNOSED"
    ROUTED = "ROUTED"
    IN_REMEDIATION = "IN_REMEDIATION"
    RECOVERED = "RECOVERED"
    FAILED = "FAILED"
    ESCALATED = "ESCALATED"
