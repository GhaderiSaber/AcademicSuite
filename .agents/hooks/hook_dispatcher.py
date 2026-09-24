#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/hooks/hook_dispatcher.py — Unified Tripartite Hook Dispatcher

Routes Antigravity lifecycle events strictly across the three hook classes:
1. Class A: Safety Hooks (safety_hooks.py)
   - PreToolUse: Raw-data protection, dangerous command protection, outside-workspace protection.
2. Class B: Integrity Hooks (integrity_hooks.py)
   - Stop / PostInvocation: Triad artifact verification, state consistency, manifest verification, post-analysis validation, honesty protocol.
3. Class C: Learning Hooks (learning_hooks.py)
   - PreInvocation / PostToolUse / Stop: Capture user corrections, capture validation failures, capture agent trajectory.

INVARIANT (Directive 19): Hooks strictly intercept, enforce, diagnose, and audit.
Hooks must NEVER act as the academic orchestrator.
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, Set

HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(HOOKS_DIR, "..", ".."))
AGENTS_DIR = os.path.abspath(os.path.join(HOOKS_DIR, ".."))
AGENTS_HOOKS_DIR = os.path.join(HOOKS_DIR, "agents")
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if AGENTS_DIR not in sys.path:
    sys.path.insert(0, AGENTS_DIR)
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)
if AGENTS_HOOKS_DIR not in sys.path:
    sys.path.insert(0, AGENTS_HOOKS_DIR)

try:
    from safety_hooks import SafetyHooks
    from integrity_hooks import IntegrityHooks
    from learning_hooks import LearningHooks
    from hook_seen import emit_hook_seen
except ImportError:
    from .safety_hooks import SafetyHooks
    from .integrity_hooks import IntegrityHooks
    from .learning_hooks import LearningHooks
    from .hook_seen import emit_hook_seen


try:
    from contracts.hook_identity_contract import (
        resolve_hook_identity,
        is_main_agent_developer as contract_is_main_agent_developer,
        get_canonical_academic_agents
    )
except ImportError:
    try:
        from .contracts.hook_identity_contract import (
            resolve_hook_identity,
            is_main_agent_developer as contract_is_main_agent_developer,
            get_canonical_academic_agents
        )
    except ImportError:
        def contract_is_main_agent_developer(p): return False
        def resolve_hook_identity(p): return None
        def get_canonical_academic_agents(): return set()


def is_main_agent_developer(payload: Dict[str, Any]) -> bool:
    """
    Detects if the current lifecycle event belongs to the Built-In Main Developer Agent
    (Track 1: Software Engineering, Code Modification, Maintenance) as opposed to
    the Custom Academic Orchestrator or custom specialist subagents (Track 2).

    SECURITY INVARIANT (Fail-Closed Authorization):
    Delegates authoritatively to the multi-signal resolution engine in contracts.hook_identity_contract.
    """
    return contract_is_main_agent_developer(payload)


AGENT_GUARD_MAP = {
    "academic-challenger": "academic_challenger_guard",
    "academic-orchestrator": "academic_orchestrator_guard",
    "academic-writer": "academic_writer_guard",
    "behavior-analyst": "behavior_analyst_guard",
    "curriculum-builder": "curriculum_builder_guard",
    "data-agent": "data_agent_guard",
    "data-curator": "data_curator_guard",
    "digital-saber": "digital_saber_guard",
    "evaluation-agent": "evaluation_agent_guard",
    "evidence-auditor": "evidence_auditor_guard",
    "final-judge": "final_judge_guard",
    "intervention-designer": "intervention_designer_guard",
    "journal-strategist": "journal_strategist_guard",
    "knowledge-curator": "knowledge_curator_guard",
    "literature-expert": "literature_expert_guard",
    "longitudinal-modmed-expert": "longitudinal_modmed_expert_guard",
    "meta-analyst": "meta_analyst_guard",
    "methodology-expert": "methodology_expert_guard",
    "project-organizer": "project_organizer_guard",
    "psychometric-expert": "psychometric_expert_guard",
    "qualitative-analyst": "qualitative_analyst_guard",
    "research-agent": "research_agent_guard",
    "results-auditor": "results_auditor_guard",
    "skill-evolver": "skill_evolver_guard",
    "statistical-auditor": "statistical_auditor_guard",
    "statistical-expert": "statistical_expert_guard",
    "statistics-agent": "statistics_agent_guard",
    "test-orchestrator": "test_orchestrator_guard",
    "test-worker": "test_worker_guard",
    "trajectory-analyzer": "trajectory_analyzer_guard",
    "validation-agent": "validation_agent_guard",
}


def resolve_agent_caller(payload: Dict[str, Any]) -> str:
    caller = (payload.get("caller") or payload.get("agentName") or "").strip().lower()
    if not caller:
        try:
            ident = resolve_hook_identity(payload)
            if ident and ident.agent_name and ident.agent_name != "unknown":
                caller = ident.agent_name.strip().lower()
        except Exception:
            pass
    return caller


def dispatch_event(event: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dispatches lifecycle events strictly to Safety, Integrity, and Learning hooks,
    and routes to agent-scoped lifecycle guards.
    Main Developer Agent is exempt from academic stop-gates and stage validation.
    """
    event_upper = event.strip()
    is_main = is_main_agent_developer(payload)

    if event_upper == "PreToolUse":
        emit_hook_seen(payload, event="PreToolUse")
        # Class A: Safety Hooks
        # Note: safety_hooks.py permits code mutation tools for Main Agent and only blocks them for academic-orchestrator.
        safety_res = SafetyHooks.handle_pre_tool_use(payload)
        if safety_res.get("decision") == "deny":
            return safety_res

        # Agent-Specific Guard Check (if applicable)
        caller = resolve_agent_caller(payload)
        guard_mod_name = AGENT_GUARD_MAP.get(caller)
        if guard_mod_name and not is_main:
            try:
                import importlib
                guard_mod = importlib.import_module(guard_mod_name)
                if hasattr(guard_mod, "handle_pre_tool_use"):
                    agent_res = guard_mod.handle_pre_tool_use(payload)
                    if isinstance(agent_res, dict) and agent_res.get("decision") == "deny":
                        return agent_res
            except Exception as e_agent:
                sys.stderr.write(f"[hook_dispatcher] Agent guard error ({guard_mod_name}): {e_agent}\n")

        # Class C: Learning Hooks (Factual trajectory capture & context enrichment)
        learning_res = LearningHooks.handle_pre_tool_use(payload)
        if learning_res and isinstance(learning_res, dict) and "overwrite" in learning_res:
            res = dict(safety_res) if isinstance(safety_res, dict) else {"decision": "allow"}
            res["decision"] = "allow"
            res["overwrite"] = learning_res["overwrite"]
            return res

        return safety_res

    elif event_upper == "PostToolUse":
        emit_hook_seen(payload, event="PostToolUse")
        # Class C: Learning Hooks (Trajectory capture)
        learning_res = LearningHooks.capture_agent_trajectory(payload)
        return learning_res

    elif event_upper == "PreInvocation":
        if is_main:
            return {}
        # Class C: Learning Hooks (User correction capture & constitutional reminder)
        pre_res = LearningHooks.handle_pre_invocation(payload)
        return pre_res

    elif event_upper == "PostInvocation":
        if is_main:
            return {"injectSteps": [], "terminationBehavior": ""}
        # Class B: Integrity Hooks (Validation advisory)
        post_res = IntegrityHooks.handle_post_invocation(payload)
        return post_res

    elif event_upper == "Stop":
        if is_main:
            return {"decision": "allow"}
        # Class B: Integrity Hooks (Artifact triad, manifest, post-analysis, honesty)
        stop_res = IntegrityHooks.handle_stop(payload)
        if stop_res.get("decision") == "continue":
            return stop_res

        # Agent-Specific Stop Guard Check (if applicable)
        caller = resolve_agent_caller(payload)
        guard_mod_name = AGENT_GUARD_MAP.get(caller)
        if guard_mod_name:
            try:
                import importlib
                guard_mod = importlib.import_module(guard_mod_name)
                if hasattr(guard_mod, "handle_stop"):
                    agent_stop_res = guard_mod.handle_stop(payload)
                    if isinstance(agent_stop_res, dict) and agent_stop_res.get("decision") == "continue":
                        return agent_stop_res
            except Exception as e_agent_stop:
                sys.stderr.write(f"[hook_dispatcher] Agent stop guard error ({guard_mod_name}): {e_agent_stop}\n")

        # Class C: Learning Hooks (Scan for user corrections)
        LearningHooks.capture_user_correction(payload)

        # Class C: Automated Graduation Safety Net (Directive 21)
        try:
            from scripts.academic_graduation_compiler import AcademicGraduationCompiler
            compiler = AcademicGraduationCompiler(base_dir=ROOT_DIR)
            ws_paths = payload.get("workspacePaths", [])
            compiler.compile_all_pending(workspaces=ws_paths, auto_commit=True, dry_run=False)
        except Exception as e_grad:
            sys.stderr.write(f"[hook_dispatcher] Auto-graduation note: {e_grad}\n")

        return stop_res

    return {"decision": "allow"}


def main():
    parser = argparse.ArgumentParser(description="Antigravity Tripartite Lifecycle Hook Dispatcher")
    parser.add_argument(
        "--event",
        type=str,
        choices=["PreInvocation", "PostInvocation", "Stop", "PreToolUse", "PostToolUse"],
        default="Stop",
        help="Lifecycle event to dispatch"
    )
    args, _ = parser.parse_known_args()

    payload = {}
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read().strip()
            if raw:
                payload = json.loads(raw)
    except Exception as e:
        sys.stderr.write(f"[hook_dispatcher] Error reading stdin JSON: {e}\n")

    event = args.event or payload.get("event", "Stop")
    result = dispatch_event(event=event, payload=payload)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
