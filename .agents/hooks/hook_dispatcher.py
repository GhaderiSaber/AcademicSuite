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
except ImportError:
    from .safety_hooks import SafetyHooks
    from .integrity_hooks import IntegrityHooks
    from .learning_hooks import LearningHooks
    from .hook_seen import emit_hook_seen


def get_canonical_academic_agents() -> Set[str]:
    """Dynamically loads all canonical agent names from the capability policy SSOT."""
    try:
        from contracts.agents.capability_policy import get_all_policy_agents
        return set(get_all_policy_agents())
    except Exception:
        try:
            from .contracts.agents.capability_policy import get_all_policy_agents
            return set(get_all_policy_agents())
        except Exception:
            return set()


def is_main_agent_developer(payload: Dict[str, Any]) -> bool:
    """
    Detects if the current lifecycle event belongs to the Built-In Main Developer Agent
    (Track 1: Software Engineering, Code Modification, Maintenance) as opposed to
    the Custom Academic Orchestrator or custom specialist subagents (Track 2).

    SECURITY INVARIANT (Fail-Closed Authorization):
    - Explicit Developer Track / Main Agent: UNRESTRICTED developer execution.
    - Custom Agents & Subagents: STRICTLY CONTROLLED. Bound to role tools, triad gates, contracts.
    - Unknown or Missing Caller: STRICTLY CONTROLLED (Fail-Closed). Never unrestricted by default.
    """
    if not isinstance(payload, dict):
        return False

    # 1. Explicit track or developer mode flags take precedence
    if payload.get("track") == 1 or payload.get("mode") == "developer" or payload.get("agent_type") == "main":
        return True

    # 2. Check Antigravity subagent flags - subagents are never the root main agent
    is_subagent = bool(payload.get("isSubagent") or payload.get("subagent") or payload.get("parentConversationId"))
    if is_subagent:
        return False

    caller = (
        payload.get("agentName") or
        payload.get("agentRole") or
        payload.get("agent") or
        payload.get("caller") or
        ""
    ).lower().strip()

    if not caller:
        # FAIL-CLOSED: Missing or empty caller is strictly governed / not unrestricted.
        return False

    # 3. Check against canonical policy agents from SSOT (all 30 registered custom agents)
    canonical_agents = get_canonical_academic_agents()
    for ac in canonical_agents:
        if ac == caller or ac in caller:
            return False

    # Domain role keywords fallback
    academic_role_keywords = ("orchestrator", "auditor", "expert", "challenger", "judge")
    if any(k in caller for k in academic_role_keywords):
        return False

    # 4. Explicit main developer indicators
    main_indicators = (
        "main", "main-agent", "mainagent", "default",
        "antigravity", "developer", "coding", "software-engineer", "code-agent"
    )
    for ind in main_indicators:
        if ind == caller or ind in caller:
            return True

    # 5. Fail-Closed Default: Any unknown caller is strictly controlled (not unrestricted).
    return False


def dispatch_event(event: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dispatches lifecycle events strictly to Safety, Integrity, and Learning hooks.
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

        # Class C: Learning Hooks (Factual trajectory capture)
        LearningHooks.handle_pre_tool_use(payload)
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

        # Class C: Learning Hooks (Scan for user corrections)
        LearningHooks.capture_user_correction(payload)
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
