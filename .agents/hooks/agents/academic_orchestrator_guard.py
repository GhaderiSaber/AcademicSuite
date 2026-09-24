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
import re
import json
import argparse
from typing import Dict, Any

HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(HOOKS_DIR, "..", "..", ".."))
for p in (ROOT_DIR, os.path.join(ROOT_DIR, ".agents"), os.path.join(ROOT_DIR, ".agents", "hooks"), os.path.join(ROOT_DIR, ".agents", "contracts")):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from contracts.delegation_envelope_parser import validate_delegation_prompt
except ImportError:
    try:
        from delegation_envelope_parser import validate_delegation_prompt
    except ImportError:
        def validate_delegation_prompt(p, expected_worker=None):
            return True, "Validator unavailable", None

try:
    from contracts.canonical_pipelines import (
        verify_pipeline_stage_prerequisites,
        verify_capability_routing,
        find_files_matching
    )
except ImportError:
    try:
        from canonical_pipelines import (
            verify_pipeline_stage_prerequisites,
            verify_capability_routing,
            find_files_matching
        )
    except ImportError:
        def verify_pipeline_stage_prerequisites(s, w):
            return True, "Pipeline validator unavailable"
        def verify_capability_routing(w, p, e=None):
            return True, "Capability validator unavailable"
        def find_files_matching(w, p):
            return []

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

EXECUTION_SUBAGENTS = {
    "statistics-agent",
    "data-agent",
    "academic-writer",
    "validation-agent",
    "psychometric-expert",
    "results-auditor"
}


def handle_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    tool_call = payload.get("toolCall", {})
    tool_name = (tool_call.get("name") or "").strip().lower()
    args = tool_call.get("args", {})

    # Directive 20 / Directive 12.1: Non-Execution Invariant
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

    # Directive 19 / Directive 12: Contractual Delegation Envelope & Capability Routing
    if tool_name == "invoke_subagent":
        subagents = args.get("Subagents", [])
        if isinstance(subagents, list):
            for sub in subagents:
                target_type = sub.get("TypeName", "")
                prompt = sub.get("Prompt", "")

                is_valid, reason, env = (
                    validate_delegation_prompt(prompt, expected_worker=target_type)
                    if target_type in EXECUTION_SUBAGENTS
                    else (True, "", None)
                )

                # Capability Routing Verification (Directive 19 / Directive 12)
                ok_cap, cap_reason = verify_capability_routing(target_type, prompt, env)
                if not ok_cap:
                    return {
                        "decision": "deny",
                        "reason": cap_reason
                    }

                if target_type in EXECUTION_SUBAGENTS:
                    if not is_valid:
                        return {
                            "decision": "deny",
                            "reason": (
                                f"CONSTITUTIONAL VIOLATION (Directive 19 / Directive 12 — Contractual Delegation Invariant): "
                                f"Delegation to execution worker '{target_type}' was rejected: {reason}\n"
                                f"You must embed a structured Contractual Delegation Envelope (CDE) in the prompt "
                                f"specifying 'task_id', 'worker_agent', 'inputs', 'required_artifacts', and 'objective'/'target_script'."
                            )
                        }

                    # Directive 3: Pipeline Stage Prerequisite Invariant (Zero Skipping)
                    stage_label = ""
                    if env:
                        stage_label = env.get("stage") or env.get("task_id") or ""
                    if not stage_label:
                        stage_label = prompt

                    workspaces = payload.get("workspacePaths", [ROOT_DIR])
                    ok_prereq, prereq_reason = verify_pipeline_stage_prerequisites(stage_label, workspaces)
                    if not ok_prereq:
                        return {
                            "decision": "deny",
                            "reason": prereq_reason
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

                # Directive 13: Anti-Sycophancy Invariant
                raw_model_text = (last_record.get("content") or "").strip()
                first_line = raw_model_text.split("\n")[0].strip() if raw_model_text else ""
                flattery_patterns = [
                    r"^(?:that(?:'s| is) a\s+)?(?:great|excellent|fantastic|wonderful|brilliant|insightful)\s+(?:question|point|observation|inquiry)",
                    r"^you(?:'re| are)\s+(?:absolutely\s+|completely\s+|entirely\s+)?right\b",
                    r"^(?:great|excellent|wonderful)\s+choice\b"
                ]
                for fp in flattery_patterns:
                    if re.search(fp, first_line, re.IGNORECASE):
                        return {
                            "decision": "continue",
                            "reason": (
                                "CONSTITUTIONAL VIOLATION (Directive 13 — Anti-Sycophancy Invariant): "
                                "Sycophantic conversational openings ('Great question!', 'You are absolutely right!') are strictly forbidden. "
                                "Academic communication must remain strictly objective, neutral, and fact-based."
                            )
                        }

                # Directive 11: Interactive Stage-Gate Protocol
                # If subagents were invoked in this turn, verify that orchestrator halted and requested user confirmation
                records = [json.loads(l) for l in lines]
                had_delegation = any(
                    any((tc.get("name") or "").lower() == "invoke_subagent" for tc in r.get("tool_calls", []))
                    for r in records
                )
                if had_delegation:
                    model_text = (last_record.get("content") or "").lower()
                    has_confirmation = any(k in model_text for k in ("confirm", "approve", "proceed", "shall we", "تایید", "ادامه", "pause", "wait", "halt"))
                    has_stage_report = any(k in model_text for k in ("what was done", "completed", "executed", "stage", "انجام شد", "مرحله"))
                    has_next_step = any(k in model_text for k in ("what will be done next", "next step", "next stage", "گام بعدی", "مرحله بعد", "next:"))
                    if not (has_confirmation or (has_stage_report and has_next_step)):
                        return {
                            "decision": "continue",
                            "reason": (
                                "CONSTITUTIONAL VIOLATION (Directive 11 — Interactive Stage-Gate Protocol): "
                                "Following subagent execution, the Academic Orchestrator must report what was done, "
                                "what will be done next, and halt to request user confirmation before proceeding."
                            )
                        }

                    # Directive 3: Triad Artifact Completion Audit on Stage Conclusion
                    workspaces = payload.get("workspacePaths", [ROOT_DIR])
                    for r in records:
                        for tc in r.get("tool_calls", []):
                            if (tc.get("name") or "").lower() == "invoke_subagent":
                                sub_list = tc.get("args", {}).get("Subagents", [])
                                for sub in sub_list:
                                    p_text = sub.get("Prompt", "")
                                    is_cde, _, env = validate_delegation_prompt(p_text, expected_worker=sub.get("TypeName"))
                                    if env and env.get("required_artifacts"):
                                        req_arts = env.get("required_artifacts", [])
                                        missing_arts = []
                                        empty_arts = []
                                        for art in req_arts:
                                            art_name = os.path.basename(art)
                                            found = find_files_matching(workspaces, re.escape(art_name))
                                            if not found:
                                                missing_arts.append(art)
                                            elif all(os.path.getsize(f) == 0 for f in found):
                                                empty_arts.append(art)
                                        if missing_arts or empty_arts:
                                            return {
                                                "decision": "continue",
                                                "reason": (
                                                    f"CONSTITUTIONAL VIOLATION (Directive 3 — Triad Artifact Invariant):\n"
                                                    f"Stage declared completion, but required deliverables are missing or empty on disk.\n"
                                                    f"Missing artifacts: {missing_arts}\n"
                                                    f"Empty (0-byte) artifacts: {empty_arts}\n"
                                                    f"Every micro-stage must generate the complete synchronized triad on disk (.docx + .md + .json)."
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
