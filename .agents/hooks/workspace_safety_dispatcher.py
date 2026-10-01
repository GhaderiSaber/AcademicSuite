#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/hooks/workspace_safety_dispatcher.py — Antigravity Workspace Safety Gate Dispatcher

Enforces workspace-wide filesystem and execution safety boundaries:
1. Raw-data protection: Blocks writes and destructive shell commands targeting raw datasets (01_raw_inputs/).
2. Dangerous command protection: Blocks catastrophic bash commands (rm -rf .git, root /, fork bombs).
3. Confinement & English ASCII filenames: Enforces workspace boundaries and ASCII filenames (Directive 6).
4. Clean workspace root standard: Blocks dropping executable scripts directly into repository root (Directive 23).

This dispatcher applies to all operations to safeguard the workspace.
It never checks academic stop-gates, triads, or thesis validation reports.
"""

import os
import sys
import json
import argparse
from typing import Dict, Any

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
    from hook_seen import emit_hook_seen
except ImportError:
    from .safety_hooks import SafetyHooks
    from .hook_seen import emit_hook_seen

try:
    from contracts.hook_identity_contract import is_main_agent_developer
except ImportError:
    try:
        from .contracts.hook_identity_contract import is_main_agent_developer
    except ImportError:
        def is_main_agent_developer(p: Dict[str, Any]) -> bool:
            return True


def dispatch_workspace_safety_event(event: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handles workspace-wide safety events.
    Applies Class A Safety Hooks: raw data protection, dangerous bash commands,
    clean root, and ASCII filenames.
    """
    event_upper = event.strip()

    if event_upper == "PreToolUse":
        emit_hook_seen(payload, event="PreToolUse")
        safety_res = SafetyHooks.handle_pre_tool_use(payload)
        return safety_res

    if event_upper == "PostToolUse":
        emit_hook_seen(payload, event="PostToolUse")
        return {}

    if event_upper == "PreInvocation":
        return {}

    if event_upper == "PostInvocation":
        return {"injectSteps": [], "terminationBehavior": ""}

    if event_upper == "Stop":
        return {"decision": "allow"}

    return {"decision": "allow"}


def main():
    parser = argparse.ArgumentParser(description="Antigravity Workspace Safety Gate Dispatcher")
    parser.add_argument(
        "--event",
        type=str,
        choices=["PreInvocation", "PostInvocation", "Stop", "PreToolUse", "PostToolUse"],
        default="PreToolUse",
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
        sys.stderr.write(f"[workspace_safety_dispatcher] Error reading stdin JSON: {e}\n")

    event = args.event or payload.get("event", "PreToolUse")
    result = dispatch_workspace_safety_event(event=event, payload=payload)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
