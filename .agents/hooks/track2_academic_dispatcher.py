#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/hooks/track2_academic_dispatcher.py — Track 2 Academic Governance Hook Dispatcher

Dedicated multi-event lifecycle governance dispatcher for the Academic Orchestrator
and specialist academic subagents (Track 2).

Enforces:
1. Fast-Path Developer Bypass: If caller is Main Developer Agent, immediately allows (< 2ms).
2. Directive 20 (Orchestrator Non-Execution Invariant): Blocks mutation and CLI tools for academic-orchestrator.
3. Directive 12 & CDE Protocol: Enforces structured Contractual Delegation Envelopes for subagents.
4. Directive 0 & 3 & 22: Enforces Binary Honesty Protocol, on-disk Triad artifacts (.docx, .md, .json),
   and Fail-Closed mechanical validation reports on Stop.
5. Continuous Learning & Self-Evolution: Captures trajectories, user feedback, and executes auto-graduation.
"""

import os
import sys
import json
import argparse
from typing import Dict, Any

HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(HOOKS_DIR, "..", ".."))
AGENTS_DIR = os.path.abspath(os.path.join(HOOKS_DIR, ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
if AGENTS_DIR not in sys.path:
    sys.path.insert(0, AGENTS_DIR)
if HOOKS_DIR not in sys.path:
    sys.path.insert(0, HOOKS_DIR)

try:
    from safety_hooks import SafetyHooks
    from integrity_hooks import IntegrityHooks
    from learning_hooks import LearningHooks
    from hook_seen import emit_hook_seen
    from dynamic_invariant_guard import DynamicInvariantGuard
except ImportError:
    from .safety_hooks import SafetyHooks
    from .integrity_hooks import IntegrityHooks
    from .learning_hooks import LearningHooks
    from .hook_seen import emit_hook_seen
    from .dynamic_invariant_guard import DynamicInvariantGuard

try:
    from contracts.hook_identity_contract import (
        resolve_hook_identity,
        is_main_agent_developer
    )
except ImportError:
    try:
        from .contracts.hook_identity_contract import (
            resolve_hook_identity,
            is_main_agent_developer
        )
    except ImportError:
        def is_main_agent_developer(p: Dict[str, Any]) -> bool:
            return False
        def resolve_hook_identity(p: Dict[str, Any]):
            return None


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


def load_agent_guard_module(agent_name: str):
    """Loads dedicated lifecycle guard directly from .agents/agents/<agent_name>/guard.py."""
    if not agent_name:
        return None
    guard_path = os.path.join(ROOT_DIR, ".agents", "agents", agent_name, "guard.py")
    if not os.path.exists(guard_path):
        return None
    mod_name = f"asam_guard_{agent_name.replace('-', '_')}"
    if mod_name in sys.modules:
        return sys.modules[mod_name]
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(mod_name, guard_path)
        if not spec or not spec.loader:
            return None
        mod = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = mod
        spec.loader.exec_module(mod)
        return mod
    except Exception as e:
        sys.stderr.write(f"[track2_academic_dispatcher] Error loading guard from {guard_path}: {e}\n")
        return None


def dispatch_track2_event(event: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dispatches lifecycle events for Track 2 Academic Agents.
    Fast-paths Track 1 Main Developer Agent immediately with decision: allow.
    """
    event_upper = event.strip()
    is_main = is_main_agent_developer(payload)

    # FAST PATH: If this is the Main Developer Agent, bypass all academic constraints immediately
    if is_main:
        if event_upper == "Stop":
            return {"decision": "allow"}
        if event_upper == "PreInvocation":
            return {}
        if event_upper == "PostInvocation":
            return {"injectSteps": [], "terminationBehavior": ""}
        return {"decision": "allow"}

    # =========================================================================
    # Track 2 Academic Lifecycle Governance
    # =========================================================================
    if event_upper == "PreToolUse":
        emit_hook_seen(payload, event="PreToolUse")
        # Class A: Safety Hooks (base raw data protection, dangerous commands)
        safety_res = SafetyHooks.handle_pre_tool_use(payload)
        if safety_res.get("decision") == "deny":
            return safety_res

        # Agent-Specific Guard Check (e.g. academic_orchestrator_guard strips mutation tools)
        caller = resolve_agent_caller(payload)
        guard_mod = load_agent_guard_module(caller)
        if guard_mod and hasattr(guard_mod, "handle_pre_tool_use"):
            try:
                agent_res = guard_mod.handle_pre_tool_use(payload)
                if isinstance(agent_res, dict) and agent_res.get("decision") == "deny":
                    return agent_res
            except Exception as e_agent:
                sys.stderr.write(f"[track2_academic_dispatcher] Agent guard error ({caller}): {e_agent}\n")

        # Dynamic Learned Invariant Guard Check
        try:
            dynamic_res = DynamicInvariantGuard.evaluate_pre_tool_use(caller, payload)
            if isinstance(dynamic_res, dict) and dynamic_res.get("decision") == "deny":
                return dynamic_res
        except Exception as e_dyn:
            sys.stderr.write(f"[track2_academic_dispatcher] Dynamic invariant guard error: {e_dyn}\n")

        # Class C: Learning Hooks (context enrichment)
        learning_res = LearningHooks.handle_pre_tool_use(payload)
        if learning_res and isinstance(learning_res, dict) and "overwrite" in learning_res:
            res = dict(safety_res) if isinstance(safety_res, dict) else {"decision": "allow"}
            res["decision"] = "allow"
            res["overwrite"] = learning_res["overwrite"]
            return res

        return safety_res

    elif event_upper == "PostToolUse":
        emit_hook_seen(payload, event="PostToolUse")
        learning_res = LearningHooks.capture_agent_trajectory(payload)
        return learning_res

    elif event_upper == "PreInvocation":
        pre_res = LearningHooks.handle_pre_invocation(payload)
        return pre_res

    elif event_upper == "PostInvocation":
        post_res = IntegrityHooks.handle_post_invocation(payload)
        return post_res

    elif event_upper == "Stop":
        # Class B: Integrity Hooks (Triad artifact check, manifest check, validation gate, honesty protocol)
        stop_res = IntegrityHooks.handle_stop(payload)
        if stop_res.get("decision") == "continue":
            return stop_res

        # Agent-Specific Stop Guard Check (e.g. academic_orchestrator_guard, validation_agent_guard)
        caller = resolve_agent_caller(payload)
        guard_mod = load_agent_guard_module(caller)
        if guard_mod and hasattr(guard_mod, "handle_stop"):
            try:
                agent_stop_res = guard_mod.handle_stop(payload)
                if isinstance(agent_stop_res, dict) and agent_stop_res.get("decision") == "continue":
                    return agent_stop_res
            except Exception as e_agent_stop:
                sys.stderr.write(f"[track2_academic_dispatcher] Agent stop guard error ({caller}): {e_agent_stop}\n")

        # Dynamic Learned Invariant Stop Check
        try:
            dynamic_stop_res = DynamicInvariantGuard.evaluate_stop(caller, payload)
            if isinstance(dynamic_stop_res, dict) and dynamic_stop_res.get("decision") == "continue":
                return dynamic_stop_res
        except Exception as e_dyn_stop:
            sys.stderr.write(f"[track2_academic_dispatcher] Dynamic invariant stop guard error: {e_dyn_stop}\n")

        # Class C: Learning Hooks (Scan for user corrections)
        LearningHooks.capture_user_correction(payload)

        # Class C: Automated Graduation Safety Net (Directive 21)
        try:
            from scripts.academic_graduation_compiler import AcademicGraduationCompiler
            compiler = AcademicGraduationCompiler(base_dir=ROOT_DIR)
            ws_paths = payload.get("workspacePaths", [])
            compiler.compile_all_pending(workspaces=ws_paths, auto_commit=True, dry_run=False)
        except Exception as e_grad:
            sys.stderr.write(f"[track2_academic_dispatcher] Auto-graduation note: {e_grad}\n")

        return stop_res

    return {"decision": "allow"}


def main():
    parser = argparse.ArgumentParser(description="Antigravity Track 2 Academic Governance Dispatcher")
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
        sys.stderr.write(f"[track2_academic_dispatcher] Error reading stdin JSON: {e}\n")

    event = args.event or payload.get("event", "Stop")
    result = dispatch_track2_event(event=event, payload=payload)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
