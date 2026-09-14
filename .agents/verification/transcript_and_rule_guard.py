#!/usr/bin/env python3
"""
transcript_and_rule_guard.py — Antigravity Lifecycle Hook Gatekeeper

Enforces Digital Saber Constitutional Directives at the machine layer:
- PreInvocation: Injects un-bypassable ephemeral system instructions.
- Stop: Forensic inspection of transcript.jsonl before allowing execution termination.
  Blocks termination if the agent claims multi-agent execution without invoking subagents,
  or fails the Binary Honesty Protocol on compliance inquiries.
"""

import sys
import os
import json
import re
from typing import Dict, Any, List, Optional


def load_transcript(transcript_path: str) -> List[Dict[str, Any]]:
    """Loads and parses transcript.jsonl safely."""
    if not transcript_path or not os.path.exists(transcript_path):
        return []
    records = []
    try:
        with open(transcript_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    except Exception as e:
        sys.stderr.write(f"[transcript_and_rule_guard] Error reading transcript: {e}\n")
    return records


def handle_pre_invocation(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Injects ephemeral prompt reminding the agent of strict constitutional directives."""
    reminder = (
        "🚨 CONSTITUTIONAL ENFORCEMENT ACTIVE (Directive 0 & Directive 3):\n"
        "1. Binary Honesty Protocol: If the user asks whether a workflow, rule, check, package, "
        "or guideline was followed (or asks if you fooled them), your response MUST begin with an "
        "unambiguous 'Yes' or 'No' as the very first word.\n"
        "2. Multi-Agent Integrity: Under NO circumstance may you claim a 'multi-agent workflow' was "
        "executed unless you physically invoked subagents via the 'invoke_subagent' tool. Workflows must "
        "be orchestrated through Antigravity subagents.\n"
        "3. Zero Skipping Rule: All Directive 3 checkpoint artifacts (JSON specs, audit reports, QC checklists) "
        "must physically exist on disk before declaring workflow completion.\n"
        "4. Sole Orchestrator Mandate (Directive 12.1): Antigravity is the sole agent runtime and multi-agent "
        "conductor. Subagents are invoked via 'invoke_subagent'. Never write, import, or run standalone Python "
        "classes that simulate subagents, dispatch agents, or claim multi-agent execution. Python scripts are "
        "strictly deterministic execution tools ('The Hands')."
    )
    return {
        "injectSteps": [
            {
                "ephemeralMessage": reminder
            }
        ]
    }


def handle_stop(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Inspects transcript and workspace disk, blocking turn completion if deceptive claims or rule breaches occurred."""
    # 1. Physical Disk Check for Forbidden Python Orchestrators (Directive 12.1)
    workspaces = payload.get("workspacePaths", [])
    for ws in workspaces:
        forbidden_file = os.path.join(ws, ".agents", "skills", "academic-suite-orchestrator", "scripts", "multi_agent_orchestrator.py")
        if os.path.exists(forbidden_file):
            return {
                "decision": "continue",
                "reason": (
                    "CONSTITUTIONAL VIOLATION (Directive 12.1 - Sole Orchestrator Mandate): "
                    f"Forbidden file '{forbidden_file}' detected on disk. Standalone Python multi-agent "
                    "orchestrators are prohibited. Antigravity is the sole agent conductor. Delete this file immediately."
                )
            }

    transcript_path = payload.get("transcriptPath")
    cid = payload.get("conversationId")
    if not transcript_path:
        if cid:
            cand = os.path.expanduser(f"~/.gemini/antigravity/brain/{cid}/.system_generated/logs/transcript.jsonl")
            if os.path.exists(cand):
                transcript_path = cand
            else:
                sys.stderr.write(
                    f"[transcript_and_rule_guard WARNING] conversationId '{cid}' provided but transcript.jsonl "
                    f"not found at '{cand}'. Guard cannot audit conversation transcript.\n"
                )

    records = load_transcript(transcript_path) if transcript_path else []
    if not records:
        if transcript_path and not os.path.exists(transcript_path):
            sys.stderr.write(f"[transcript_and_rule_guard WARNING] transcript_path '{transcript_path}' does not exist on disk.\n")
        return {"decision": "allow"}

    subagent_calls_count = 0
    for r in records:
        for tc in r.get("tool_calls", []):
            name = tc.get("name") if isinstance(tc, dict) else getattr(tc, "name", str(tc))
            if name == "invoke_subagent":
                subagent_calls_count += 1

    last_assistant_msg = ""
    last_user_msg = ""
    for r in reversed(records):
        stype = r.get("type")
        content = r.get("content", "")
        if not last_assistant_msg and stype == "PLANNER_RESPONSE" and content:
            last_assistant_msg = content.strip()
        elif not last_user_msg and stype == "USER_INPUT" and content:
            last_user_msg = content.strip()
        if last_assistant_msg and last_user_msg:
            break

    clean_user = re.sub(r"<[^>]+>", "", last_user_msg).strip()

    compliance_keywords = [
        "did you", "did the agent", "is the agent do correct", "did it follow",
        "fool me", "fooled me", "were the rules followed", "did you check",
        "did you use the workflow", "was the check performed"
    ]
    is_compliance_query = any(k in clean_user.lower() for k in compliance_keywords)

    if is_compliance_query and last_assistant_msg:
        cleaned_first_text = re.sub(r"^[#\*\s\>`_]+", "", last_assistant_msg)
        first_word = cleaned_first_text.split()[0].rstrip(".,:;!?*").capitalize() if cleaned_first_text.split() else ""
        if first_word not in ("Yes", "No"):
            return {
                "decision": "continue",
                "reason": (
                    f"CONSTITUTIONAL VIOLATION (Directive 0 - Binary Honesty Protocol): The user asked a compliance "
                    f"or honesty question ('{clean_user[:60]}...'). Your response must begin with an unambiguous "
                    f"'Yes' or 'No' as the very first word. Got: '{first_word}'. You must revise your response immediately."
                )
            }

    claim_patterns = [
        r"we (?:have )?(?:successfully )?executed (?:a )?(?:complete, )?multi[- ]agent",
        r"executed (?:an )?antigravity multi[- ]agent workflow",
        r"multi[- ]agent workflow [\"']?\w+[\"']? completed",
        r"completed,? multi[- ]agent [a-zA-Z0-9_-]+ (?:empirical )?pipeline",
        r"subagents executed:\s*\[",
        r"subagents? (?:were|have been|are) (?:invoked|executed|run|deliberated|coordinated)",
        r"delegated to (?:our|the)? subagents?",
        r"subagent deliberation completed",
        r"orchestrated (?:the )?(?:14|15 )?subagents",
        r"autonomous agents? (?:executed|deliberated|coordinated)",
        r"multi[- ]agent team (?:has )?(?:completed|executed|deliberated|analyzed)",
        r"pipeline run by (?:the )?subagents",
        r"ساب[‌ ]?ایجنت[‌ ]?ها (?:اجرا|بررسی|فراخوانی)",
        r"فرایند چند[‌ ]?عاملی"
    ]
    asst_lower = last_assistant_msg.lower()
    claims_multiagent = any(re.search(pat, asst_lower) for pat in claim_patterns)
    is_negated_review = any(neg in asst_lower for neg in [
        "did not execute", "was not a multi-agent", "called exactly zero",
        "called 0 times", "never invoked", "bypassed the multi-agent",
        "no subagents were invoked", "zero subagents were invoked"
    ])

    if claims_multiagent and not is_negated_review and subagent_calls_count == 0:
        return {
            "decision": "continue",
            "reason": (
                "CONSTITUTIONAL VIOLATION (Directive 0 & Directive 12): Your response claims a 'multi-agent' execution "
                "or subagent pipeline, but 'invoke_subagent' was called 0 times in this transcript! "
                "Workflows in interactive sessions must be orchestrated through Antigravity subagents. "
                "You must state factually that no subagents were invoked and correct your claim."
            )
        }

    return {"decision": "allow"}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Antigravity Lifecycle Hook Guard")
    parser.add_argument("--event", type=str, choices=["PreInvocation", "PostInvocation", "Stop", "PreToolUse", "PostToolUse"], default="Stop")
    args, unknown = parser.parse_known_args()

    payload = {}
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read().strip()
            if raw:
                payload = json.loads(raw)
    except Exception as e:
        sys.stderr.write(f"[transcript_and_rule_guard] Error parsing stdin JSON: {e}\n")

    event = args.event or payload.get("event", "Stop")

    if event == "PreInvocation":
        res = handle_pre_invocation(payload)
    elif event == "Stop":
        res = handle_stop(payload)
    else:
        res = {"decision": "allow"}

    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
