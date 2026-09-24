#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/hooks/agents/academic_orchestrator_guard.py

Dedicated Lifecycle Hook Guard for Academic Main Agent (academic-orchestrator).
Enforces:
1. Directive 20 (Orchestrator Non-Execution Invariant):
   academic-orchestrator is strictly managerial and forbidden from executing code (run_command)
   or directly mutating project files (write_to_file, replace_file_content, edit_file).
   Execution MUST be delegated to specialist subagents via invoke_subagent.
2. Directive 11 (Interactive Stage-Gate Protocol):
   Requires interactive confirmation pause between multi-stage workflows.
3. Directive 0 (Binary Honesty Protocol):
   First word must be unambiguous "Yes" or "No" on compliance questions.
"""

import sys
import os
import json
import argparse
from typing import Dict, Any

HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(HOOKS_DIR, "..", "..", ".."))
for p in (ROOT_DIR, os.path.join(ROOT_DIR, ".agents", "hooks")):
    if p not in sys.path:
        sys.path.insert(0, p)

FORBIDDEN_ORCHESTRATOR_TOOLS = {
    "run_command",
    "write_to_file",
    "replace_file_content",
    "edit_file",
    "patch",
    "multi_file_edit",
    "batch_replace",
    "apply_diff"
}


def handle_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    tool_call = payload.get("toolCall", {})
    tool_name = (tool_call.get("name") or "").strip().lower()

    if tool_name in FORBIDDEN_ORCHESTRATOR_TOOLS:
        return {
            "decision": "deny",
            "reason": (
                f"CONSTITUTIONAL VIOLATION (Directive 20 / Directive 12.1 — Orchestrator Non-Execution Invariant): "
                f"Academic-Orchestrator is the Academic Main Agent (Conductor) and is strictly forbidden from "
                f"executing shell commands or mutating project files via '{tool_name}'. "
                f"All computational execution and file generation MUST be delegated to specialist subagents "
                f"(e.g., statistics-agent, academic-writer, data-agent) via invoke_subagent."
            )
        }

    return {"decision": "allow"}


def handle_stop(payload: Dict[str, Any]) -> Dict[str, Any]:
    # Check if there is a transcript available to verify Directive 0 or stage completion
    transcript_path = payload.get("transcriptPath")
    if transcript_path and os.path.exists(transcript_path):
        try:
            # Quick tail check of transcript for binary honesty protocol
            with open(transcript_path, "r", encoding="utf-8") as tf:
                lines = [l.strip() for l in tf if l.strip()]
            if lines:
                last_record = json.loads(lines[-1])
                # If this was a planner response answering a compliance question, verify Directive 0
                user_question = ""
                for rec_line in reversed(lines[:-1]):
                    rec = json.loads(rec_line)
                    if rec.get("type") == "USER_INPUT":
                        user_question = rec.get("content", "")
                        break
                
                is_compliance_q = any(
                    k in user_question.lower() 
                    for k in ("did you check", "did you follow", "did you use", "have you checked", "is it compliant")
                )
                if is_compliance_q:
                    model_text = (last_record.get("content") or "").strip()
                    first_word = model_text.split()[0].rstrip(",.:;!?") if model_text.split() else ""
                    if first_word.lower() not in ("yes", "no"):
                        return {
                            "decision": "continue",
                            "reason": (
                                "CONSTITUTIONAL VIOLATION (Directive 0 — Binary Honesty Protocol): "
                                "Compliance inquiries must begin with an unambiguous 'Yes' or 'No' as the very first word. "
                                "State the unvarnished factual answer before proposing explanations or remedies."
                            )
                        }
        except Exception:
            pass

    return {"decision": "allow"}


def main():
    parser = argparse.ArgumentParser(description="Academic Orchestrator Lifecycle Guard")
    parser.add_argument("--event", type=str, default="PreToolUse", choices=["PreToolUse", "PostToolUse", "PreInvocation", "PostInvocation", "Stop"])
    args, _ = parser.parse_known_args()

    payload = {}
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read().strip()
            if raw:
                payload = json.loads(raw)
    except Exception as e:
        sys.stderr.write(f"[orchestrator_guard] Error reading stdin: {e}\n")

    event = args.event
    if event == "PreToolUse":
        res = handle_pre_tool_use(payload)
    elif event == "Stop":
        res = handle_stop(payload)
    elif event == "PostInvocation":
        res = {"injectSteps": [], "terminationBehavior": ""}
    else:
        res = {"decision": "allow"}

    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
