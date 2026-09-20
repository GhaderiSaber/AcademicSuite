#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
recovery package — Academic Suite Failure Recovery & Targeted Routing Architecture
"""

from recovery.taxonomy import (
    FailureType,
    FailureSeverity,
    RecoveryStrategy,
    IncidentStatus
)
from recovery.diagnostics import diagnose_failure
from recovery.router import route_failure, calculate_preserved_stages
from recovery.recovery_engine import (
    create_incident,
    resolve_incident,
    format_incident_markdown
)

__all__ = [
    "FailureType",
    "FailureSeverity",
    "RecoveryStrategy",
    "IncidentStatus",
    "diagnose_failure",
    "route_failure",
    "calculate_preserved_stages",
    "create_incident",
    "resolve_incident",
    "format_incident_markdown"
]
