#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
transcript_and_rule_guard.py — Antigravity Lifecycle Hook Gatekeeper (Facade)

Refactored in Phase 14 to delegate to the three specialized hook classes:
- Class A: Safety Hooks (.agents/hooks/safety_hooks.py)
- Class B: Integrity Hooks (.agents/hooks/integrity_hooks.py)
- Class C: Learning Hooks (.agents/hooks/learning_hooks.py)

Maintains 100% backward compatibility with existing tests and scripts.
INVARIANT: Hooks strictly intercept, enforce, diagnose, and audit.
Hooks must NEVER act as the academic orchestrator.
"""

import sys
import os
import json
import argparse
from typing import Dict, Any, List, Optional, Tuple

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
HOOKS_DIR = os.path.join(ROOT_DIR, ".agents", "hooks")
for p in (ROOT_DIR, HOOKS_DIR):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from safety_hooks import (
        SafetyHooks,
        MUTATION_TOOLS,
        extract_target_paths,
        is_raw_data_path,
        is_raw_data_command,
        is_state_ledger_command,
        is_dangerous_command,
        is_outside_workspace,
        is_ascii_filename
    )
    from integrity_hooks import IntegrityHooks, load_transcript
    from learning_hooks import LearningHooks
    from track1_developer_dispatcher import dispatch_track1_event
    from track2_academic_dispatcher import dispatch_track2_event
    from contracts.hook_identity_contract import is_main_agent_developer
except ImportError:
    from .safety_hooks import (
        SafetyHooks,
        MUTATION_TOOLS,
        extract_target_paths,
        is_raw_data_path,
        is_raw_data_command,
        is_state_ledger_command,
        is_dangerous_command,
        is_outside_workspace,
        is_ascii_filename
    )
    from .integrity_hooks import IntegrityHooks, load_transcript
    from .learning_hooks import LearningHooks
    from .track1_developer_dispatcher import dispatch_track1_event
    from .track2_academic_dispatcher import dispatch_track2_event
    from .contracts.hook_identity_contract import is_main_agent_developer


def handle_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Delegates to Class A SafetyHooks."""
    return SafetyHooks.handle_pre_tool_use(payload)


def handle_post_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Delegates to Class C LearningHooks (trajectory capture)."""
    return LearningHooks.capture_agent_trajectory(payload)


def handle_pre_invocation(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Delegates to Class C LearningHooks (user correction scan & reminder injection)."""
    return LearningHooks.handle_pre_invocation(payload)


def handle_post_invocation(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Delegates to Class B IntegrityHooks (post-analysis advisory)."""
    return IntegrityHooks.handle_post_invocation(payload)


def handle_stop(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Delegates to Class B IntegrityHooks (artifact, manifest, validation, honesty checks)."""
    stop_res = IntegrityHooks.handle_stop(payload)
    if stop_res.get("decision") == "continue":
        return stop_res
    # Also scan for user corrections
    LearningHooks.capture_user_correction(payload)
    # Automated Graduation Safety Net (Directive 21)
    if not os.environ.get("UNITTEST_MODE"):
        try:
            from scripts.academic_graduation_compiler import AcademicGraduationCompiler
            compiler = AcademicGraduationCompiler(base_dir=ROOT_DIR)
            ws_paths = payload.get("workspacePaths", [])
            compiler.compile_all_pending(workspaces=ws_paths, auto_commit=True, dry_run=False)
        except Exception as e_grad:
            sys.stderr.write(f"[transcript_and_rule_guard] Auto-graduation note: {e_grad}\n")
    return stop_res


def main():
    parser = argparse.ArgumentParser(description="Antigravity Lifecycle Hook Guard Facade")
    parser.add_argument(
        "--event",
        type=str,
        choices=["PreInvocation", "PostInvocation", "Stop", "PreToolUse", "PostToolUse"],
        default="Stop"
    )
    args, _ = parser.parse_known_args()

    payload = {}
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read().strip()
            if raw:
                payload = json.loads(raw)
    except Exception as e:
        sys.stderr.write(f"[transcript_and_rule_guard] Error reading stdin JSON: {e}\n")

    event = args.event or payload.get("event", "Stop")
    if is_main_agent_developer(payload):
        result = dispatch_track1_event(event=event, payload=payload)
    else:
        result = dispatch_track2_event(event=event, payload=payload)
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
