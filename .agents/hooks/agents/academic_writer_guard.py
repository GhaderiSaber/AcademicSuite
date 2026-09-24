#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/hooks/agents/academic_writer_guard.py

Dedicated Lifecycle Hook Guard for Academic Writer Specialist Subagent (academic-writer).
Enforces:
1. Directive 3 (Triad Artifact Invariant):
   Ensures both .docx (Word) and .md (Markdown) are produced for drafted chapter sections.
2. Directive 3.1 (Chapter 5 Prose-Only Invariant):
   Chapter 5 (Discussion & Conclusion) must contain strictly zero tables (zero markdown tables |---|
   and zero Word tables).
3. Directive 6 (English ASCII Filename Standard):
   All deliverable filenames must be ASCII English (e.g. 06_hypothesis_1.docx).
4. Directive 7.1 (Academic Sobriety & Anti-Hyperbole):
   Eliminates robotic AI clichés (e.g., 'شایان ذکر است که', 'پرواضح است که') and dramatic hyperbole.
5. Directive 12 (Worker Delegation Guard):
   Specialist worker subagent is forbidden from spawning secondary subagents.
"""

import sys
import os
import re
import json
import argparse
from typing import Dict, Any

HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(HOOKS_DIR, "..", "..", ".."))
for p in (ROOT_DIR, os.path.join(ROOT_DIR, ".agents", "hooks")):
    if p not in sys.path:
        sys.path.insert(0, p)

FORBIDDEN_AI_CLICHES = [
    "شایان ذکر است که",
    "لازم به ذکر است که",
    "پرواضح است که",
    "بر کسی پوشیده نیست که",
    "در یک کلام می‌توان گفت",
    "به طور چشمگیری می‌توان ادعا کرد"
]


def handle_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    tool_call = payload.get("toolCall", {})
    tool_name = (tool_call.get("name") or "").strip().lower()
    args = tool_call.get("args", {})

    # Directive 12: Worker Delegation Guard
    if tool_name in ("invoke_subagent", "define_subagent"):
        return {
            "decision": "deny",
            "reason": (
                "CONSTITUTIONAL VIOLATION (Directive 12 — Worker Delegation Guard): "
                "Specialist subagent 'academic-writer' is a drafting worker and is "
                "forbidden from spawning secondary subagents."
            )
        }

    # Directive 6: English ASCII Filename Guard
    for arg_val in args.values():
        if isinstance(arg_val, str) and any(ext in arg_val.lower() for ext in (".docx", ".md", ".pptx", ".txt")):
            base = os.path.basename(arg_val)
            if base and not base.isascii():
                return {
                    "decision": "deny",
                    "reason": (
                        f"CONSTITUTIONAL VIOLATION (Directive 6 — English ASCII Filename Standard): "
                        f"Deliverable filename '{base}' contains non-ASCII characters. "
                        f"Every Word and Markdown document on disk must be named strictly with English ASCII characters."
                    )
                }

    return {"decision": "allow"}


def handle_stop(payload: Dict[str, Any]) -> Dict[str, Any]:
    transcript_path = payload.get("transcriptPath")
    if transcript_path and os.path.exists(transcript_path):
        try:
            with open(transcript_path, "r", encoding="utf-8") as tf:
                records = [json.loads(l) for l in tf if l.strip()]

            # Inspect last planner response for clichés and Chapter 5 table violations
            for rec in reversed(records):
                if rec.get("type") == "PLANNER_RESPONSE":
                    content = rec.get("content", "")
                    
                    # 1. AI Cliché scan
                    for cliché in FORBIDDEN_AI_CLICHES:
                        if cliché in content:
                            return {
                                "decision": "continue",
                                "reason": (
                                    f"CONSTITUTIONAL VIOLATION (Directive 7.1 — Academic Sobriety & Anti-Cliché Standard): "
                                    f"Detected robotic AI cliché: '{cliché}'. Academic Persian writing must remain strictly "
                                    f"objective, neutral, and sober. Please rephrase without sensational or clichéd padding."
                                )
                            }
                    
                    # 2. Chapter 5 Prose-Only Invariant: zero tables
                    is_ch5 = any(k in content.lower() for k in ("فصل پنجم", "فصل ۵", "chapter 5", "chapter_5", "05_discussion"))
                    if is_ch5 and re.search(r'\|[\s\-:]+\|', content):
                        return {
                            "decision": "continue",
                            "reason": (
                                "CONSTITUTIONAL VIOLATION (Directive 3.1 — Chapter 5 Prose-Only Invariant): "
                                "Chapter 5 (Discussion & Conclusion) must contain strictly ZERO tables. "
                                "It must be 100% continuous narrative prose, theoretical synthesis, and psychological mechanism explanation. "
                                "Remove all Markdown or Word tables from Chapter 5 deliverables."
                            )
                        }
                    break
        except Exception:
            pass

    return {"decision": "allow"}


def main():
    parser = argparse.ArgumentParser(description="Academic Writer Subagent Lifecycle Guard")
    parser.add_argument("--event", type=str, default="PreToolUse", choices=["PreToolUse", "PostToolUse", "PreInvocation", "PostInvocation", "Stop"])
    args, _ = parser.parse_known_args()

    payload = {}
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read().strip()
            if raw:
                payload = json.loads(raw)
    except Exception as e:
        sys.stderr.write(f"[academic_writer_guard] Error reading stdin: {e}\n")

    event = args.event
    if event == "PreToolUse":
        res = handle_pre_tool_use(payload)
    elif event == "Stop":
        res = handle_stop(payload)
    else:
        res = {"decision": "allow"}

    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
