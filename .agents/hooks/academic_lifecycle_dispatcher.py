#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/hooks/academic_lifecycle_dispatcher.py — Academic Lifecycle Governance Dispatcher

Dedicated multi-event lifecycle governance dispatcher for the Academic Suite Plugin
(governing academic-orchestrator and specialist academic subagents).

Enforces:
1. Native Developer Fast-Path: If caller is the native Antigravity coding agent, immediately allows (< 2ms).
2. Directive 20 (Orchestrator Zero-Hands Invariant): Blocks mutation and CLI execution tools for academic-orchestrator.
3. Directive 12 & CDE Protocol: Enforces structured Contractual Delegation Envelopes for subagents.
4. Directives 0, 3 & 22: Enforces Binary Honesty Protocol, on-disk Triad artifacts (.docx, .md, .json),
   and Fail-Closed mechanical validation reports on Stop.
5. Continuous Learning: Captures trajectories, user corrections, and executes auto-graduation.
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, Optional

HOOKS_DIR = os.path.dirname(os.path.realpath(__file__))
AGENTS_DIR = os.path.dirname(HOOKS_DIR)
ROOT_DIR = os.path.dirname(AGENTS_DIR)
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
except Exception:
    try:
        from .safety_hooks import SafetyHooks
        from .integrity_hooks import IntegrityHooks
        from .learning_hooks import LearningHooks
        from .hook_seen import emit_hook_seen
        from .dynamic_invariant_guard import DynamicInvariantGuard
    except Exception as e_imp:
        sys.stderr.write(f"[academic_lifecycle_dispatcher] Hook module import note: {e_imp}\n")
        class SafetyHooks:
            @staticmethod
            def handle_pre_tool_use(p): return {"decision": "allow"}
        class IntegrityHooks:
            @staticmethod
            def handle_stop(p): return {"decision": "allow"}
            @staticmethod
            def handle_post_invocation(p): return {}
        class LearningHooks:
            @staticmethod
            def handle_pre_tool_use(p): return {}
            @staticmethod
            def capture_agent_trajectory(p): return {}
            @staticmethod
            def handle_pre_invocation(p): return {}
            @staticmethod
            def capture_user_correction(p): return {"is_critique": False}
        class DynamicInvariantGuard:
            @staticmethod
            def evaluate_pre_tool_use(c, p): return {"decision": "allow"}
            @staticmethod
            def evaluate_stop(c, p): return {"decision": "allow"}
        def emit_hook_seen(p, **kw): pass

try:
    from contracts.hook_identity_contract import (
        resolve_hook_identity,
        is_main_agent_developer,
        extract_subagent_info
    )
except ImportError:
    try:
        from .contracts.hook_identity_contract import (
            resolve_hook_identity,
            is_main_agent_developer,
            extract_subagent_info
        )
    except ImportError:
        def is_main_agent_developer(p: Dict[str, Any]) -> bool:
            return False
        def resolve_hook_identity(p: Dict[str, Any]):
            return None
        def extract_subagent_info(p: Dict[str, Any]):
            return False, None


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


def check_agent_tool_restrictions(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Enforces agent-specific invariants via its dedicated co-located guard."""
    caller = resolve_agent_caller(payload)
    if not caller:
        return None
    agent_dir_name = caller
    agents_root = os.path.join(ROOT_DIR, ".agents", "agents")
    if os.path.isdir(agents_root):
        for a in os.listdir(agents_root):
            if a == caller or a in caller or caller in a:
                agent_dir_name = a
                break
    guard_path = os.path.join(agents_root, agent_dir_name, "guard.py")
    if os.path.exists(guard_path):
        try:
            import importlib.util
            mod_name = f"asam_guard_{agent_dir_name.replace('-', '_')}"
            if mod_name in sys.modules:
                mod = sys.modules[mod_name]
            else:
                spec = importlib.util.spec_from_file_location(mod_name, guard_path)
                mod = importlib.util.module_from_spec(spec)
                sys.modules[mod_name] = mod
                spec.loader.exec_module(mod)
            if hasattr(mod, "handle_pre_tool_use"):
                return mod.handle_pre_tool_use(payload)
        except Exception as e:
            sys.stderr.write(f"[academic_lifecycle_dispatcher] Error executing {agent_dir_name} guard: {e}\n")
    return None


def check_orchestrator_tool_restrictions(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    return check_agent_tool_restrictions(payload)


def check_agent_stop_restrictions(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Enforces agent-specific stop invariants via its dedicated co-located guard."""
    caller = resolve_agent_caller(payload)
    if not caller:
        return None
    agent_dir_name = caller
    agents_root = os.path.join(ROOT_DIR, ".agents", "agents")
    if os.path.isdir(agents_root):
        for a in os.listdir(agents_root):
            if a == caller or a in caller or caller in a:
                agent_dir_name = a
                break
    guard_path = os.path.join(agents_root, agent_dir_name, "guard.py")
    if os.path.exists(guard_path):
        try:
            import importlib.util
            mod_name = f"asam_guard_{agent_dir_name.replace('-', '_')}"
            if mod_name in sys.modules:
                mod = sys.modules[mod_name]
            else:
                spec = importlib.util.spec_from_file_location(mod_name, guard_path)
                mod = importlib.util.module_from_spec(spec)
                sys.modules[mod_name] = mod
                spec.loader.exec_module(mod)
            if hasattr(mod, "handle_stop"):
                return mod.handle_stop(payload)
        except Exception as e:
            sys.stderr.write(f"[academic_lifecycle_dispatcher] Error executing {agent_dir_name} stop guard: {e}\n")
    return None


def check_orchestrator_stop_restrictions(payload: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    return check_agent_stop_restrictions(payload)


def dispatch_academic_lifecycle_event(event: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dispatches lifecycle events for Academic Suite Agents (academic-orchestrator & subagents).
    Fast-paths the Native Developer Agent immediately with decision: allow.
    """
    event_upper = event.strip()
    is_main = is_main_agent_developer(payload)

    # FAST PATH: If this is the Native Developer Agent, bypass all academic constraints immediately
    if is_main:
        if event_upper == "Stop":
            return {"decision": "allow"}
        if event_upper in ("PostToolUse", "PreInvocation"):
            return {}
        if event_upper == "PostInvocation":
            return {"injectSteps": [], "terminationBehavior": ""}
        return {"decision": "allow"}

    # =========================================================================
    # Academic Lifecycle Governance
    # =========================================================================
    if event_upper == "PreToolUse":
        emit_hook_seen(payload, event="PreToolUse")
        # Class A: Safety Hooks (base raw data protection, dangerous commands)
        safety_res = SafetyHooks.handle_pre_tool_use(payload)
        if safety_res.get("decision") == "deny":
            return safety_res

        # Directive 20: academic-orchestrator execution tool stripping
        orch_res = check_orchestrator_tool_restrictions(payload)
        if orch_res and orch_res.get("decision") == "deny":
            return orch_res

        # Dynamic Learned Invariant Guard Check
        caller = resolve_agent_caller(payload)
        try:
            dynamic_res = DynamicInvariantGuard.evaluate_pre_tool_use(caller, payload)
            if isinstance(dynamic_res, dict) and dynamic_res.get("decision") == "deny":
                return dynamic_res
        except Exception as e_dyn:
            sys.stderr.write(f"[academic_lifecycle_dispatcher] Dynamic invariant guard error: {e_dyn}\n")

        # Class C: Learning Hooks (context enrichment)
        learning_res = LearningHooks.handle_pre_tool_use(payload)
        if learning_res and isinstance(learning_res, dict) and "overwrite" in learning_res:
            res = dict(safety_res) if isinstance(safety_res, dict) else {"decision": "allow"}
            res["decision"] = "allow"
            if "overwrite" in res and isinstance(res["overwrite"], dict) and "args" in res["overwrite"]:
                merged_args = dict(res["overwrite"]["args"])
                if isinstance(learning_res["overwrite"], dict) and "args" in learning_res["overwrite"]:
                    merged_args.update(learning_res["overwrite"]["args"])
                res["overwrite"] = {"args": merged_args}
            else:
                res["overwrite"] = learning_res["overwrite"]
            return res

        return safety_res

    elif event_upper == "PostToolUse":
        emit_hook_seen(payload, event="PostToolUse")
        learning_res = LearningHooks.capture_agent_trajectory(payload)
        return learning_res

    elif event_upper == "PreInvocation":
        cid = str(payload.get("conversationId") or "")
        if cid:
            import time, tempfile, hashlib
            cache_path = os.path.join(tempfile.gettempdir(), f"agy_preinv_{hashlib.md5(cid.encode()).hexdigest()[:12]}.lock")
            try:
                now_ts = time.time()
                if os.path.isfile(cache_path):
                    mtime = os.path.getmtime(cache_path)
                    if (now_ts - mtime) < 2.5:
                        return {}
                with open(cache_path, "w") as f_lock:
                    f_lock.write(str(now_ts))
            except Exception:
                pass
        pre_res = LearningHooks.handle_pre_invocation(payload)
        return pre_res

    elif event_upper == "PostInvocation":
        caller = resolve_agent_caller(payload)
        if caller and "caller" not in payload:
            payload["caller"] = caller
        post_res = IntegrityHooks.handle_post_invocation(payload)
        return post_res

    elif event_upper == "Stop":
        caller = resolve_agent_caller(payload)
        if caller and "caller" not in payload:
            payload["caller"] = caller
        # Class B: Integrity Hooks (Triad artifact check, manifest check, validation gate, honesty protocol)
        stop_res = IntegrityHooks.handle_stop(payload)
        if stop_res.get("decision") == "continue":
            msg = stop_res.get("reason") or ""
            stop_res["reason"] = msg
            stop_res.pop("message", None)
            return stop_res

        # Orchestrator-specific Stop Guard Check
        orch_stop_res = check_orchestrator_stop_restrictions(payload)
        if orch_stop_res and orch_stop_res.get("decision") == "continue":
            msg = orch_stop_res.get("reason") or ""
            orch_stop_res["reason"] = msg
            orch_stop_res.pop("message", None)
            return orch_stop_res

        # Dynamic Learned Invariant Stop Check
        caller = resolve_agent_caller(payload)
        try:
            dynamic_stop_res = DynamicInvariantGuard.evaluate_stop(caller, payload)
            if isinstance(dynamic_stop_res, dict) and dynamic_stop_res.get("decision") == "continue":
                msg = dynamic_stop_res.get("reason") or ""
                dynamic_stop_res["reason"] = msg
                dynamic_stop_res.pop("message", None)
                return dynamic_stop_res
        except Exception as e_dyn_stop:
            sys.stderr.write(f"[academic_lifecycle_dispatcher] Dynamic invariant stop guard error: {e_dyn_stop}\n")

        # Class C: Learning Hooks (Scan for user corrections)
        LearningHooks.capture_user_correction(payload)

        # Class C: Automated Graduation Safety Net (Directive 21)
        if not os.environ.get("UNITTEST_MODE") and "unittest" not in sys.modules:
            try:
                from scripts.academic_graduation_compiler import AcademicGraduationCompiler
                compiler = AcademicGraduationCompiler(base_dir=ROOT_DIR)
                ws_paths = payload.get("workspacePaths", [])
                compiler.compile_all_pending(workspaces=ws_paths, auto_commit=True, dry_run=False)
            except Exception as e_grad:
                sys.stderr.write(f"[academic_lifecycle_dispatcher] Auto-graduation note: {e_grad}\n")

        return stop_res

    return {"decision": "allow"}


def main():
    parser = argparse.ArgumentParser(description="Antigravity Academic Lifecycle Governance Dispatcher")
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
        sys.stderr.write(f"[academic_lifecycle_dispatcher] Error reading stdin JSON: {e}\n")

    event = args.event or payload.get("event", "Stop")
    result = dispatch_academic_lifecycle_event(event=event, payload=payload)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
