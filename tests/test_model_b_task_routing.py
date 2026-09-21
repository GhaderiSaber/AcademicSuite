#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_model_b_task_routing.py — Automated Tests for Model B Task Routing Architecture

Verifies:
1. Deterministic task router can persist plan artifacts via Python API and CLI --output flag.
2. PreInvocation lifecycle hook executes task routing for academic-orchestrator,
   persisting academic-state/routing_plan.json and injecting the capability plan into ephemeral context.
3. academic-orchestrator frontmatter contains zero execution tools (run_command absent).
4. academic-orchestrator possesses canonical read (view_file) and delegation (invoke_subagent) tools.
5. Documentation concordance: TASK_ROUTER_SPECIFICATION.md accurately documents Model B.
"""

import os
import sys
import json
import yaml
import tempfile
import subprocess
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if AGENTS_DIR not in sys.path:
    sys.path.insert(0, AGENTS_DIR)

from scripts.academic_task_router import (
    build_pipeline,
    route_and_persist_plan,
)
from hooks.learning_hooks import LearningHooks
from scripts.orchestrator_invariants import (
    FORBIDDEN_ORCHESTRATOR_TOOLS,
    REQUIRED_ORCHESTRATOR_TOOLS,
)


class TestModelBTaskRouting:
    """Validates Model B Preflight & Hook-Assisted Task Routing Architecture."""

    def test_01_route_and_persist_plan_api(self):
        """route_and_persist_plan must compile and write valid plan JSON to disk."""
        with tempfile.TemporaryDirectory() as tmpdir:
            plan_file = os.path.join(tmpdir, "academic-state", "routing_plan.json")
            res = route_and_persist_plan("Analyze this dataset", output_path=plan_file)
            
            assert os.path.isfile(plan_file), "Plan file was not written to disk"
            with open(plan_file, "r", encoding="utf-8") as f:
                saved_plan = json.load(f)

            assert saved_plan["capabilities_formula"] == "DATA + STATISTICS"
            assert saved_plan["capabilities"] == ["DATA", "STATISTICS"]
            assert len(saved_plan["pipeline"]) == 2
            assert saved_plan["pipeline"][0]["agent"] == "data-agent"
            assert saved_plan["pipeline"][1]["agent"] == "statistics-agent"
            assert "capability_resolution" in saved_plan

    def test_02_cli_route_output_flag(self):
        """CLI route command with -o/--output must write JSON plan to specified path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            plan_file = os.path.join(tmpdir, "out_plan.json")
            router_script = os.path.join(ROOT_DIR, ".agents", "scripts", "academic_task_router.py")
            cmd = [sys.executable, router_script, "route", "Perform CFA and SEM", "-o", plan_file]
            
            subprocess.check_call(cmd)
            assert os.path.isfile(plan_file), "CLI did not create output plan file"
            
            with open(plan_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert data["capabilities_formula"] == "DATA + STATISTICS + VALIDATION"
            assert len(data["pipeline"]) == 3

    def test_03_cli_resolve_output_flag(self):
        """CLI resolve command with -o/--output must write resolution manifest to specified path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            plan_file = os.path.join(tmpdir, "resolve_plan.json")
            router_script = os.path.join(ROOT_DIR, ".agents", "scripts", "academic_task_router.py")
            cmd = [sys.executable, router_script, "resolve", "Write Chapter 4", "-o", plan_file]
            
            subprocess.check_call(cmd)
            assert os.path.isfile(plan_file), "CLI did not create output resolve file"
            
            with open(plan_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            assert "status" in data
            assert data["status"] == "RESOLVED"

    def test_04_pre_invocation_hook_executes_task_router_and_injects_context(self):
        """PreInvocation hook must run task router for academic-orchestrator and inject plan."""
        payload = {
            "caller": "academic-orchestrator",
            "userMessage": "Please analyze this dataset and test hypotheses"
        }
        res = LearningHooks.handle_pre_invocation(payload)
        
        assert "injectSteps" in res, "PreInvocation hook must return injectSteps"
        assert len(res["injectSteps"]) >= 1
        msg = res["injectSteps"][0]["ephemeralMessage"]
        
        assert "DETERMINISTIC CAPABILITY ROUTING PLAN" in msg
        assert "DATA + STATISTICS" in msg
        assert "academic-orchestrator is non-executing" in msg
        assert "academic-state/routing_plan.json" in msg

        # Verify physical plan artifact exists
        plan_path = os.path.join(ROOT_DIR, "academic-state", "routing_plan.json")
        assert os.path.isfile(plan_path), "academic-state/routing_plan.json must exist"

    def test_05_orchestrator_frontmatter_non_execution_invariant(self):
        """academic-orchestrator frontmatter MUST NOT possess run_command or any mutation tool."""
        agent_path = os.path.join(ROOT_DIR, ".agents", "agents", "academic-orchestrator", "agent.md")
        with open(agent_path, "r", encoding="utf-8") as f:
            content = f.read()

        parts = content.split("---", 2)
        assert len(parts) >= 3, "Frontmatter not found"
        fm = yaml.safe_load(parts[1])
        tools = set(fm.get("tools", []))

        # Check forbidden tools
        for forbidden in FORBIDDEN_ORCHESTRATOR_TOOLS:
            assert forbidden not in tools, f"academic-orchestrator possesses forbidden tool: {forbidden}"

        # Check required tools
        for required in REQUIRED_ORCHESTRATOR_TOOLS:
            assert required in tools, f"academic-orchestrator missing required tool: {required}"

        # Must have view_file to consume plan artifacts
        assert "view_file" in tools, "academic-orchestrator must possess view_file to read routing plan"

    def test_06_task_router_specification_documentation_concordance(self):
        """TASK_ROUTER_SPECIFICATION.md must document Model B and not claim orchestrator queries router via run_command."""
        spec_path = os.path.join(ROOT_DIR, "docs", "TASK_ROUTER_SPECIFICATION.md")
        assert os.path.isfile(spec_path), "TASK_ROUTER_SPECIFICATION.md missing"
        with open(spec_path, "r", encoding="utf-8") as f:
            doc = f.read()

        assert "Model B" in doc, "TASK_ROUTER_SPECIFICATION.md must mention Model B"
        assert "PreInvocation" in doc, "TASK_ROUTER_SPECIFICATION.md must mention PreInvocation hook"
        # Must not claim the orchestrator directly queries the router via CLI run_command
        assert "The Academic Orchestrator analyzes the prompt using scripts/academic_task_router.py" not in doc
        assert "It queries `scripts/academic_task_router.py route" not in doc
