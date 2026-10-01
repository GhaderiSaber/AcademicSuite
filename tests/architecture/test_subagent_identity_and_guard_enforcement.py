#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/architecture/test_subagent_identity_and_guard_enforcement.py — Verification of Subagent Governance & Dual-Track Separation

Verifies:
1. Subagent identity resolution: Subagents are strictly classified as Track 2 (never Track 1 Developer).
2. Subagent payload attempting developer mode/track cannot inherit Track 1 Developer immunity.
3. Fail-Closed Contractual Delegation Envelope (CDE) enforcement on Academic-Orchestrator.
4. Subagent ephemeral context rehydration via PreInvocation hook in learning_hooks.py.
5. Dynamic Invariant Guard enforcement across generic and academic callers.
6. Absolute immunity and unconstrained execution tools for Track 1 Main Developer.
"""

import os
import sys
import json
import importlib.util
import pytest

TESTS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(TESTS_DIR, "..", ".."))
AGENTS_DIR = os.path.abspath(os.path.join(ROOT_DIR, ".agents"))

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if AGENTS_DIR not in sys.path:
    sys.path.insert(0, AGENTS_DIR)

from contracts.hook_identity_contract import (
    HookIdentity,
    resolve_hook_identity,
    is_main_agent_developer,
)
from hooks.workspace_safety_dispatcher import dispatch_workspace_safety_event
from hooks.academic_lifecycle_dispatcher import dispatch_academic_lifecycle_event
from hooks.learning_hooks import handle_pre_invocation
from hooks.dynamic_invariant_guard import DynamicInvariantGuard
from hooks.safety_hooks import SafetyHooks

# Dynamically load academic-orchestrator guard
orch_guard_path = os.path.join(AGENTS_DIR, "agents", "academic-orchestrator", "guard.py")
spec = importlib.util.spec_from_file_location("orchestrator_guard", orch_guard_path)
orchestrator_guard = importlib.util.module_from_spec(spec)
sys.modules["orchestrator_guard"] = orchestrator_guard
spec.loader.exec_module(orchestrator_guard)


class TestSubagentIdentityAndDualTrackSeparation:
    """Verifies that subagents are never misclassified as Track 1 Main Developer."""

    def test_subagent_payload_resolves_to_track2(self):
        """A subagent payload must resolve to Track 2, even when executing shell commands."""
        subagent_payload = {
            "conversationId": "subagent-writer-12345",
            "stepIdx": 5,
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": "python3 script.py"}
            },
            "agentName": "academic-writer",
            "workspacePaths": [ROOT_DIR]
        }
        identity = resolve_hook_identity(subagent_payload)
        assert identity.is_main_developer is False
        assert identity.track == "track_2_academic"
        assert identity.is_subagent is True

    def test_subagent_flag_prevents_main_developer_classification(self):
        """Explicit isSubagent: True must strictly prevent is_main_developer, even if mode=developer."""
        payload = {
            "conversationId": "root-conversation-123",
            "stepIdx": 1,
            "isSubagent": True,
            "agentName": "default",
            "mode": "developer",
            "track": 1,
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": "git status"}
            }
        }
        identity = resolve_hook_identity(payload)
        assert identity.is_main_developer is False
        assert identity.is_subagent is True

    def test_main_developer_payload_retains_full_developer_immunity(self):
        """Native Developer payload must resolve to host_environment with full execution privileges."""
        dev_payload = {
            "conversationId": "main-dev-conv-789",
            "stepIdx": 10,
            "agentName": "default",
            "agentRole": "developer",
            "mode": "developer",
            "track": 1,
            "isSubagent": False,
            "toolCall": {
                "name": "run_command",
                "args": {"CommandLine": "pytest tests/"}
            },
            "workspacePaths": [ROOT_DIR]
        }
        identity = resolve_hook_identity(dev_payload)
        assert identity.is_main_developer is True
        assert identity.track == "track_1_developer"

        # Dispatcher must immediately allow without interference
        result = dispatch_workspace_safety_event("PreToolUse", dev_payload)
        assert result.get("decision") == "allow"


class TestOrchestratorFailClosedCDEEnforcement:
    """Verifies that Academic-Orchestrator cannot invoke workers without a valid CDE."""

    def test_orchestrator_rejects_unstructured_worker_delegation(self):
        """Calling invoke_subagent with an unstructured text prompt must be denied."""
        payload = {
            "conversationId": "orchestrator-conv-001",
            "stepIdx": 2,
            "caller": "academic-orchestrator",
            "agentName": "academic-orchestrator",
            "toolCall": {
                "name": "invoke_subagent",
                "args": {
                    "Subagents": [
                        {
                            "TypeName": "statistics-agent",
                            "Role": "Statistical Analyst",
                            "Prompt": "Please run the regression analysis for hypothesis 1 on the dataset."
                        }
                    ]
                }
            },
            "workspacePaths": [ROOT_DIR]
        }

        result = orchestrator_guard.handle_pre_tool_use(payload)
        assert result.get("decision") == "deny"
        assert "Contractual Delegation" in result.get("reason", "") or "CDE" in result.get("reason", "")

    def test_orchestrator_rejects_writer_delegation_with_json_in_required_artifacts(self):
        """Academic-writer delegation specifying .json in required_artifacts must be denied."""
        cde_prompt = json.dumps({
            "task_id": "CH4_H1_DRAFT",
            "worker_agent": "academic-writer",
            "inputs": ["results.json"],
            "required_artifacts": ["results.json", "chapter4_draft.md"],
            "objective": "Draft scholarly narrative for hypothesis 1"
        })
        payload = {
            "conversationId": "orchestrator-conv-002",
            "stepIdx": 3,
            "caller": "academic-orchestrator",
            "agentName": "academic-orchestrator",
            "toolCall": {
                "name": "invoke_subagent",
                "args": {
                    "Subagents": [
                        {
                            "TypeName": "academic-writer",
                            "Role": "Academic Drafter",
                            "Prompt": cde_prompt
                        }
                    ]
                }
            },
            "workspacePaths": [ROOT_DIR]
        }

        result = orchestrator_guard.handle_pre_tool_use(payload)
        assert result.get("decision") == "deny"
        assert "Statistical Immobility Invariant" in result.get("reason", "")


class TestSubagentPreInvocationContextRehydration:
    """Verifies that subagents receive role-specific invariants at PreInvocation."""

    def test_academic_writer_pre_invocation_injects_typography_directives(self):
        """PreInvocation for academic-writer must inject Persian typography rules."""
        payload = {
            "conversationId": "subagent-writer-999",
            "agentName": "academic-writer",
            "caller": "academic-writer",
            "isSubagent": True,
            "stepIdx": 1,
            "workspacePaths": [ROOT_DIR]
        }
        result = handle_pre_invocation(payload)
        steps = result.get("injectSteps", [])
        assert len(steps) > 0
        instructions = steps[0].get("ephemeralMessage", "")
        assert "Directive 4 & 5" in instructions or "B Nazanin" in instructions
        assert "Directive 3.1" in instructions or "Discussion" in instructions

    def test_statistics_agent_pre_invocation_injects_data_integrity_directives(self):
        """PreInvocation for statistics-agent must inject deterministic calculation invariants."""
        payload = {
            "conversationId": "subagent-stats-888",
            "agentName": "statistics-agent",
            "caller": "statistics-agent",
            "isSubagent": True,
            "stepIdx": 1,
            "workspacePaths": [ROOT_DIR]
        }
        result = handle_pre_invocation(payload)
        steps = result.get("injectSteps", [])
        assert len(steps) > 0
        instructions = steps[0].get("ephemeralMessage", "")
        assert "Directive 2" in instructions or "Deterministic calculation" in instructions
        assert "Directive 9" in instructions or "decimal noise" in instructions

    def test_validation_agent_pre_invocation_injects_fail_closed_gate(self):
        """PreInvocation for validation-agent must inject Directive 22."""
        payload = {
            "conversationId": "subagent-val-777",
            "agentName": "validation-agent",
            "caller": "validation-agent",
            "isSubagent": True,
            "stepIdx": 1,
            "workspacePaths": [ROOT_DIR]
        }
        result = handle_pre_invocation(payload)
        steps = result.get("injectSteps", [])
        assert len(steps) > 0
        instructions = steps[0].get("ephemeralMessage", "")
        assert "Directive 22" in instructions or "Fail-closed" in instructions


class TestDynamicInvariantGuardGenericCaller:
    """Verifies that the dynamic invariant guard monitors generic or unspecified callers."""

    def test_dynamic_invariant_blocks_prohibited_tables_in_chapter5(self):
        """Writing a markdown table into Chapter 5 is blocked by dynamic invariant even for generic caller."""
        payload = {
            "conversationId": "generic-academic-call",
            "caller": "academic-agent",
            "toolCall": {
                "name": "write_to_file",
                "args": {
                    "TargetFile": os.path.join(ROOT_DIR, "03_deliverables", "chapter_5_discussion.md"),
                    "CodeContent": "# Chapter 5 Discussion\n\n| Variable | Beta |\n| - | - |\n| Self-Efficacy | 0.42 |"
                }
            },
            "workspacePaths": [ROOT_DIR]
        }
        result = DynamicInvariantGuard.evaluate_pre_tool_use("academic-agent", payload)
        assert result.get("decision") == "deny"
        assert "CHAPTER-5-PROSE-ONLY" in result.get("reason", "")
