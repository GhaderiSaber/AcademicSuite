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


def is_main_agent_developer(payload: Dict[str, Any]) -> bool:
    """
    Detects if the current lifecycle event belongs to the Main Developer Agent
    (Track 1: Software Engineering, Code Modification, Maintenance) as opposed to
    the Academic Orchestrator or academic specialist subagents (Track 2).
    """
    caller = (
        payload.get("agentName") or
        payload.get("agentRole") or
        payload.get("agent") or
        payload.get("caller") or
        ""
    ).lower().strip()

    academic_names = {
        "academic-orchestrator", "orchestrator",
        "digital-saber", "methodology-expert", "statistical-expert",
        "academic-writer", "evidence-auditor", "final-judge",
        "statistics-agent", "data-agent", "data-curator", "results-auditor",
        "statistical-auditor", "psychometric-expert", "qualitative-analyst",
        "meta-analyst", "literature-expert", "research-agent", "validation-agent"
    }

    for ac in academic_names:
        if ac in caller:
            return False

    main_indicators = (
        "main", "main-agent", "mainagent", "default",
        "antigravity", "developer", "coding", "software-engineer", "code-agent"
    )
    for ind in main_indicators:
        if ind == caller or ind in caller:
            return True

    if payload.get("agent_type") == "main" or payload.get("track") == 1:
        return True

    # Check transcript context for coding vs academic intent
    transcript_path = payload.get("transcriptPath")
    cid = payload.get("conversationId")
    if not transcript_path and cid:
        cand = os.path.expanduser(f"~/.gemini/antigravity/brain/{cid}/.system_generated/logs/transcript.jsonl")
        if os.path.exists(cand):
            transcript_path = cand

    if transcript_path and os.path.isfile(transcript_path):
        try:
            with open(transcript_path, "r", encoding="utf-8") as f:
                records = [json.loads(line) for line in f if line.strip()]

            for r in reversed(records):
                # Inspect recent tool calls: code modification tools imply Main Developer Agent
                for tc in r.get("tool_calls", []):
                    tname = tc.get("name", "") if isinstance(tc, dict) else ""
                    targs = tc.get("args", {}) if isinstance(tc, dict) else {}
                    if tname in ("replace_file_content", "apply_diff"):
                        return True
                    if tname == "write_to_file":
                        target = targs.get("TargetFile", "")
                        if target.endswith((".py", ".sh", ".c", ".cpp", ".js", ".ts", ".json", ".yml", ".yaml")):
                            return True

                # Inspect user prompt
                if r.get("type") == "USER_INPUT" and r.get("content"):
                    prompt = r.get("content", "").lower()
                    coding_kws = ("pytest", "git", "test", "bug", "fix", "refactor", "code", "python", "factory", "hook", "lint")
                    if any(k in prompt for k in coding_kws):
                        return True
                    break
        except Exception:
            pass

    return False


def dispatch_event(event: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Dispatches lifecycle events strictly to Safety, Integrity, and Learning hooks.
    Main Developer Agent is exempt from academic stop-gates and stage validation.
    """
    event_upper = event.strip()
    is_main = is_main_agent_developer(payload)

    if event_upper == "PreToolUse":
        # Class A: Safety Hooks
        # Note: safety_hooks.py permits code mutation tools for Main Agent and only blocks them for academic-orchestrator.
        safety_res = SafetyHooks.handle_pre_tool_use(payload)
        if safety_res.get("decision") == "deny":
            return safety_res

        # Class C: Learning Hooks (Factual trajectory capture)
        LearningHooks.handle_pre_tool_use(payload)
        return safety_res

    elif event_upper == "PostToolUse":
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
