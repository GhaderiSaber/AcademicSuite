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
except ImportError:
    from .safety_hooks import SafetyHooks
    from .integrity_hooks import IntegrityHooks
    from .learning_hooks import LearningHooks


def dispatch_event(event: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dispatches lifecycle events strictly to Safety, Integrity, and Learning hooks.
    """
    event_upper = event.strip()

    if event_upper == "PreToolUse":
        # Class A: Safety Hooks
        safety_res = SafetyHooks.handle_pre_tool_use(payload)
        return safety_res

    elif event_upper == "PostToolUse":
        # Class C: Learning Hooks (Trajectory capture)
        learning_res = LearningHooks.capture_agent_trajectory(payload)
        return learning_res

    elif event_upper == "PreInvocation":
        # Class C: Learning Hooks (User correction capture & constitutional reminder)
        pre_res = LearningHooks.handle_pre_invocation(payload)
        return pre_res

    elif event_upper == "PostInvocation":
        # Class B: Integrity Hooks (Validation advisory)
        post_res = IntegrityHooks.handle_post_invocation(payload)
        return post_res

    elif event_upper == "Stop":
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
