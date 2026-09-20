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
from typing import Dict, Any

HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(HOOKS_DIR, "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
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


def is_main_agent_developer(payload: Dict[str, Any]) -> bool:
    """
    Detects if the current lifecycle event belongs to the Built-In Main Developer Agent
    (Track 1: Software Engineering, Code Modification, Maintenance) as opposed to
    the Custom Academic Orchestrator or custom specialist subagents (Track 2).

    ARCHITECTURAL INVARIANT:
    - Built-in Main Agent: UNRESTRICTED. Full developer freedom, no academic Stop gates.
    - Custom Agents & Subagents: STRICTLY CONTROLLED. Bound to role tools, triad gates, contracts.
    """
    caller = (
        payload.get("agentName") or
        payload.get("agentRole") or
        payload.get("agent") or
        payload.get("caller") or
        ""
    ).lower().strip()

    # All 22 persistent custom roles + domain aliases
    academic_custom_names = {
        # Core Custom Orchestrators & Lead Roles
        "academic-orchestrator", "orchestrator", "digital-saber", "test-orchestrator",
        # Specialist Domain Workers
        "statistics-agent", "data-agent", "academic-writer", "research-agent",
        "validation-agent", "data-curator", "longitudinal-modmed-expert",
        "qualitative-analyst", "meta-analyst", "intervention-designer",
        "psychometric-expert", "journal-strategist",
        # Advisory & Adversarial Audit Authorities
        "methodology-expert", "statistical-expert", "statistical-auditor",
        "results-auditor", "evidence-auditor", "academic-challenger", "final-judge",
        "literature-expert",
        # Self-Improvement & Meta-Learning Subagents
        "behavior-analyst", "curriculum-builder", "evaluation-agent",
        "knowledge-curator", "skill-evolver", "trajectory-analyzer",
        "test-worker"
    }

    # 1. If explicitly identified as any custom agent or academic orchestrator -> False (Strictly Controlled)
    for ac in academic_custom_names:
        if ac == caller or ac in caller:
            return False

    # 2. Check Antigravity 2.0 subagent flags
    is_subagent = bool(payload.get("isSubagent") or payload.get("subagent") or payload.get("parentConversationId"))
    if is_subagent:
        # If Antigravity marks this execution as a delegated subagent, it is NOT the root main agent
        return False

    # 3. Explicit main developer indicators
    main_indicators = (
        "main", "main-agent", "mainagent", "default",
        "antigravity", "developer", "coding", "software-engineer", "code-agent"
    )
    for ind in main_indicators:
        if ind == caller or ind in caller:
            return True

    if payload.get("agent_type") == "main" or payload.get("track") == 1:
        return True

    # 4. Inverted Default: If not identified as a custom subagent/orchestrator,
    # it is the Built-in Main Agent operating in Track 1.
    # This guarantees the Built-in Main Agent is NEVER accidentally blocked by academic Stop gates.
    return True


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
