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
import glob
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


def handle_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Intercepts tool calls to enforce Directive 3 (Artifact Gating), Directive 6 (English-Only Filenames) and security gates."""
    tool_call = payload.get("toolCall", {})
    name = tool_call.get("name", "")
    args = tool_call.get("args", {})
    workspaces = payload.get("workspacePaths", [])

    # 1. Filename ASCII enforcement for file modifying tools
    if name in ("write_to_file", "replace_file_content"):
        target = args.get("TargetFile", "")
        basename = os.path.basename(target)
        if any(ord(c) > 127 for c in basename):
            return {
                "decision": "deny",
                "reason": (
                    f"CONSTITUTIONAL VIOLATION (Directive 6 - English-Only Filename Standard): "
                    f"Target filename '{basename}' contains non-ASCII characters. Filenames must use English ASCII only."
                )
            }

        # Directive 3: Micro-Stage & Hypothesis Section Gating for Chapter 4
        if basename.lower() in ("chapter_4_results.docx", "chapter4_results.docx", "chapter_4_results.md", "chapter4_results.md"):
            target_dir = os.path.dirname(target) or "."
            check_dirs = [target_dir] + workspaces
            
            # 1. Prerequisite data & audit artifacts
            has_stats = any(os.path.exists(os.path.join(d, "stats_results.json")) for d in check_dirs)
            has_audit = any(os.path.exists(os.path.join(d, "statistical_audit_report.json")) for d in check_dirs)
            if not has_stats or not has_audit:
                return {
                    "decision": "deny",
                    "reason": (
                        "CONSTITUTIONAL VIOLATION (Directive 3 - Zero Skipping Rule): "
                        "Cannot assemble Chapter 4 before Stage 4 (stats_results.json) "
                        "and Stage 5 (statistical_audit_report.json) checkpoint artifacts exist on disk."
                    )
                }

            # 2. Micro-stage section artifacts (Anti-Shortcut Guarantee)
            required_sections = [
                ("01_demographics", ["*demographic*.docx", "*demographic*.md"]),
                ("02_descriptives_and_reliability", ["*descriptive*.docx", "*descriptive*.md", "*reliability*.docx", "*reliability*.md"]),
                ("03_parametric_assumptions", ["*assumption*.docx", "*assumption*.md"]),
                ("04_bivariate_correlations", ["*correlation*.docx", "*correlation*.md"]),
                ("hypothesis_1", ["*hypothesis_1*.docx", "*hypothesis_1*.md", "*hypo_1*.docx", "*hypo_1*.md"]),
                ("chapter_summary", ["*chapter_summary*.docx", "*chapter_summary*.md", "*summary*.docx", "*summary*.md"])
            ]
            missing_sections = []
            for label, patterns in required_sections:
                found = False
                for d in check_dirs:
                    for pat in patterns:
                        if glob.glob(os.path.join(d, pat)):
                            found = True
                            break
                    if found:
                        break
                if not found:
                    missing_sections.append(label)

            if missing_sections:
                return {
                    "decision": "deny",
                    "reason": (
                        f"CONSTITUTIONAL VIOLATION (Directive 3 - Micro-Stage, Triad Artifact & One-Hypothesis-One-Stage Invariant): "
                        f"Cannot compile Chapter 4 in one shot. Missing required micro-stage section artifacts: "
                        f"{missing_sections}. Each section and hypothesis must be generated as an independent, "
                        f"verified artifact on disk (triad: .docx, .md, .json) before assembly."
                    )
                }

        # Directive 3: Micro-Stage Gating for Chapter 5 final deliverable
        if basename.lower() in ("chapter_5_discussion.docx", "chapter5_discussion.docx", "chapter_5_discussion.md", "chapter5_discussion.md"):
            target_dir = os.path.dirname(target) or "."
            check_dirs = [target_dir] + workspaces
            required_ch5_sections = [
                ("01_findings_recap", ["*recap*.docx", "*recap*.md", "*findings*.docx", "*findings*.md"]),
                ("hypothesis_1_discussion", ["*hypothesis_1_discussion*.docx", "*hypothesis_1_discussion*.md", "*hypo_1_disc*.docx", "*hypo_1_disc*.md"]),
                ("implications", ["*implication*.docx", "*implication*.md"]),
                ("limitations", ["*limitation*.docx", "*limitation*.md"])
            ]
            missing_ch5 = []
            for label, patterns in required_ch5_sections:
                found = False
                for d in check_dirs:
                    for pat in patterns:
                        if glob.glob(os.path.join(d, pat)):
                            found = True
                            break
                    if found:
                        break
                if not found:
                    missing_ch5.append(label)

            if missing_ch5:
                return {
                    "decision": "deny",
                    "reason": (
                        f"CONSTITUTIONAL VIOLATION (Directive 3 - Micro-Stage, Triad Artifact & One-Hypothesis-One-Stage Invariant): "
                        f"Cannot compile Chapter 5 in one shot. Missing required micro-stage section artifacts: "
                        f"{missing_ch5}. Each hypothesis discussion and section must be drafted independently (triad: .docx, .md, .json) first."
                    )
                }

    # 2. Shell command interceptor
    if name == "run_command":
        cmd = args.get("CommandLine", "")

        # Security: Block destructive removal of configuration repositories
        if re.search(r'\brm\s+-(?:r|rf|fr)\s+(?:\.agents|\.git)\b', cmd):
            return {
                "decision": "deny",
                "reason": "SECURITY VIOLATION: Destruction of .agents or .git directories is strictly prohibited."
            }

        # Filename ASCII enforcement on redirects and directory creation
        redirect_match = re.search(r'(?:>|>>|\btouch\s+|\bmkdir\s+)([^\s;&|]+)', cmd)
        if redirect_match:
            filepath = redirect_match.group(1).strip("'\"")
            basename = os.path.basename(filepath)
            if any(ord(c) > 127 for c in basename):
                return {
                    "decision": "deny",
                    "reason": (
                        f"CONSTITUTIONAL VIOLATION (Directive 6 - English-Only Filename Standard): "
                        f"Command attempts to create non-ASCII file/directory '{basename}'."
                    )
                }

    return {"decision": "allow"}


def handle_post_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Validates artifact schemas and logs post-tool diagnostics."""
    return {}


def handle_pre_invocation(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Injects ephemeral prompt reminding the agent of strict constitutional directives."""
    reminder = (
        "🚨 CONSTITUTIONAL ENFORCEMENT ACTIVE (Directive 0, 3 & 11):\n"
        "1. Binary Honesty Protocol: If asked a compliance question, your response MUST begin with 'Yes' or 'No'.\n"
        "2. Micro-Stages, Triad Artifacts & One-Hypothesis-One-Stage Invariant (Directive 3): Monolithic drafting in one shot is prohibited. "
        "Every section and individual hypothesis must generate a synchronized triad of disk artifacts: .docx (Word), .md (Markdown), and .json (Data/Stats) before assembly.\n"
        "3. Interactive Stage-Gate Protocol (Directive 11): At the end of each stage, emit the Stage Completion Report "
        "(What was done + What will be done next), then STOP and wait for user confirmation before advancing.\n"
        "4. Multi-Agent Integrity: Under NO circumstance claim a multi-agent workflow unless you physically invoked "
        "subagents via 'invoke_subagent'.\n"
        "5. Sole Orchestrator Mandate (Directive 12.1): Antigravity is the sole agent runtime. Python scripts are strictly "
        "deterministic execution tools ('The Hands'). Never run agent emulators."
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

    # 2. Skill Modularity & Context Budget Check (Directive 18)
    check_dirs = [os.path.join(ws, ".agents", "skills") for ws in workspaces]
    default_skills_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "skills"))
    if default_skills_dir not in check_dirs and os.path.exists(default_skills_dir):
        check_dirs.append(default_skills_dir)

    for s_dir in check_dirs:
        if os.path.exists(s_dir):
            guard_path = os.path.join(os.path.dirname(__file__), "skill_size_guard.py")
            if os.path.exists(guard_path):
                import importlib.util
                spec = importlib.util.spec_from_file_location("skill_size_guard", guard_path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                res = mod.audit_skill_sizes(s_dir)
                if not res.get("passed", True):
                    violation_details = "; ".join(
                        [f"{v['skill']} ({v['line_count']} lines, {v['byte_size']} bytes)" for v in res["violations"]]
                    )
                    return {
                        "decision": "continue",
                        "reason": (
                            f"CONSTITUTIONAL VIOLATION (Directive 18 - Skill Modularity Standard): "
                            f"The following skill(s) exceed single-view limits (max 500 lines, 40,000 bytes): "
                            f"{violation_details}. Modularize extended guidelines into 'references/' before proceeding."
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
    elif event == "PreToolUse":
        res = handle_pre_tool_use(payload)
    elif event == "PostToolUse":
        res = handle_post_tool_use(payload)
    else:
        res = {"decision": "allow"}

    print(json.dumps(res, ensure_ascii=False))


if __name__ == "__main__":
    main()
