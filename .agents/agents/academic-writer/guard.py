#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/agents/academic-writer/guard.py

Dedicated Lifecycle Hook Guard for Academic Writer Specialist Subagent (academic-writer).
Enforces:
1. Directive 3 (Triad Artifact Invariant):
   Ensures both .docx (Word) and .md (Markdown) are produced for drafted chapter sections.
2. Directive 3.1 (Chapter 5 Prose-Only Invariant):
   Chapter 5 must contain strictly zero tables (zero markdown tables |---| and zero Word <w:tbl> tables).
3. Directive 6 (English ASCII Filename Standard):
   All deliverable filenames must be ASCII English (e.g. 06_hypothesis_1.docx).
4. Directive 7.1 (Academic Sobriety & Anti-Hyperbole):
   Eliminates robotic AI clichés and dramatic hyperbole.
5. Directive 12 (Worker Delegation Guard):
   Specialist worker subagent is forbidden from spawning secondary subagents.
6. Directive 5 (Persian Typography & OpenXML Standards):
   Native OpenXML footnotes, justified RTL paragraphs, standard Persian orthography.
"""

import sys
import os
import re
import json
import argparse
from typing import Dict, Any, List

HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(HOOKS_DIR, "..", "..", ".."))
for p in (ROOT_DIR, os.path.join(ROOT_DIR, ".agents", "hooks"), os.path.join(ROOT_DIR, ".agents", "verification")):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from safety_hooks import is_root_script_target, is_deliverables_script_target
except ImportError:
    def is_root_script_target(p, w=None): return False, ""
    def is_deliverables_script_target(p): return False, ""

try:
    from academic_writer_auditor import (
        FORBIDDEN_AI_CLICHES,
        EMOJI_PATTERN,
        ALLOWED_LATIN_TOKENS,
        DISALLOWED_ARABIC_LETTERS,
        find_disallowed_arabic_characters,
        find_raw_latin_in_persian,
        check_docx_openxml_integrity,
        check_chapter_5_docx_tables,
        audit_writer_docx_deliverables
    )
except ImportError:
    from verification.academic_writer_auditor import (
        FORBIDDEN_AI_CLICHES,
        EMOJI_PATTERN,
        ALLOWED_LATIN_TOKENS,
        DISALLOWED_ARABIC_LETTERS,
        find_disallowed_arabic_characters,
        find_raw_latin_in_persian,
        check_docx_openxml_integrity,
        check_chapter_5_docx_tables,
        audit_writer_docx_deliverables
    )


def handle_pre_tool_use(payload: Dict[str, Any]) -> Dict[str, Any]:
    tool_call = payload.get("toolCall", {})
    tool_name = (tool_call.get("name") or "").strip().lower()
    args = tool_call.get("args", {})
    workspaces = payload.get("workspacePaths", [ROOT_DIR])

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

    # Directive 23: Clean Workspace Root & Deliverables Purity Standards
    if tool_name in ("write_to_file", "replace_file_content", "edit_file", "patch", "apply_diff", "multi_file_edit", "batch_replace"):
        target_path = args.get("TargetFile") or args.get("target") or args.get("file_path") or args.get("path") or ""

        # Directive 19 / Directive 2: Statistical Immobility Invariant
        if target_path and target_path.strip().lower().endswith(".json"):
            return {
                "decision": "deny",
                "reason": (
                    f"CONSTITUTIONAL VIOLATION (Directive 19 / Directive 2 — Statistical Immobility Invariant): "
                    f"Specialist subagent 'academic-writer' is strictly 'The Voice' and is forbidden from creating, "
                    f"mutating, or overwriting statistical or analytical results files ('{os.path.basename(target_path)}'). "
                    f"All analytical JSON artifacts in '03_deliverables/' are immutable read-only records produced "
                    f"exclusively by statistics-agent and data-curator during Phases 4A–4C. "
                    f"Academic-Writer must inspect JSON results as read-only inputs via 'view_file' and draft only .docx and .md deliverables."
                )
            }

        is_root, script_name = is_root_script_target(target_path, workspaces)
        if is_root:
            return {
                "decision": "deny",
                "reason": (
                    f"CONSTITUTIONAL VIOLATION (Directive 23 — Clean Workspace Root Standard): "
                    f"Writing script file '{script_name}' directly into the repository root is strictly forbidden.\n"
                    f"Route scripts strictly to: (1) '02_analysis_code/', (2) '.agents/scripts/', (3) 'tests/', or scratch."
                )
            }
        is_deliv, deliv_script = is_deliverables_script_target(target_path)
        if is_deliv:
            return {
                "decision": "deny",
                "reason": (
                    f"CONSTITUTIONAL VIOLATION (Directive 23 — Deliverables Purity Standard): "
                    f"Writing script file '{deliv_script}' into '03_deliverables/' is strictly forbidden.\n"
                    f"Deliverable directories must contain exclusively publication artifacts (.docx, .md, .json, .pdf)."
                )
            }

        # Directive 5: Zero Raw Latin & Disallowed Arabic in Persian Text
        content = args.get("CodeContent") or args.get("ReplacementContent") or args.get("content") or ""
        if content:
            offending = find_raw_latin_in_persian(content)
            if offending:
                return {
                    "decision": "deny",
                    "reason": (
                        f"CONSTITUTIONAL VIOLATION (Directive 5 — Zero Inline Latin Invariant / Script in Persian Narrative):\n"
                        f"Found untransliterated English words in Persian deliverable text: {offending[:5]}.\n"
                        f"All foreign author names, concepts, and technical terminology in Persian sentences must be "
                        f"transliterated phonetically (e.g. «اسمیت»), with the original English term placed strictly in footnotes."
                    )
                }

            arabic_violations = find_disallowed_arabic_characters(content)
            if arabic_violations:
                return {
                    "decision": "deny",
                    "reason": (
                        f"CONSTITUTIONAL VIOLATION (Directive 5 — Zero Arabic Letters Invariant):\n"
                        f"Found disallowed Arabic glyphs or digits in Persian deliverable text: "
                        f"{[v['glyph'] for v in arabic_violations]}.\n"
                        f"Use standard Persian letters (ی U+06CC, ک U+06A9, ه/ت) and Persian digits (۰-۹)."
                    )
                }

    # Directive 19 / Directive 2: Statistical Immobility on Shell Commands
    if tool_name == "run_command":
        cmd = args.get("CommandLine") or args.get("command") or ""
        cmd_tokens = cmd.strip().split()
        if cmd_tokens:
            cmd_lower = cmd.lower()
            if any(sym in cmd_lower for sym in (">", ">>", "tee", "cp", "mv")) and ".json" in cmd_lower:
                if any(k in cmd_lower for k in ("03_deliverables", "deliverables")):
                    return {
                        "decision": "deny",
                        "reason": (
                            f"CONSTITUTIONAL VIOLATION (Directive 19 / Directive 2 — Statistical Immobility Invariant): "
                            f"Academic-Writer is strictly forbidden from executing shell commands that write, copy, move, "
                            f"or redirect into JSON files ('{cmd}'). All analytical JSON results are immutable outputs of Phase 4A–4C."
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
    workspaces = payload.get("workspacePaths", [ROOT_DIR])

    if transcript_path and os.path.exists(transcript_path):
        try:
            with open(transcript_path, "r", encoding="utf-8") as tf:
                records = [json.loads(l) for l in tf if l.strip()]

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

                    # 2. Emoji scan
                    emojis_found = EMOJI_PATTERN.findall(content)
                    if emojis_found and any(k in content.lower() for k in ("فصل", "chapter", "slide", "اسلاید", "deliverable")):
                        return {
                            "decision": "continue",
                            "reason": (
                                f"CONSTITUTIONAL VIOLATION (Directive 4.1 — Zero Emojis Invariant): "
                                f"Detected forbidden emojis in academic presentation/summary: {list(set(emojis_found))[:5]}. "
                                f"Academic deliverables and slides must contain strictly ZERO emojis."
                            )
                        }

                    # 3. Chapter 5 Prose-Only Invariant: zero markdown tables
                    is_ch5 = any(k in content.lower() for k in ("فصل پنجم", "فصل ۵", "chapter 5", "chapter_5", "05_discussion"))
                    if is_ch5 and re.search(r'\|[\s\-:]+\|', content):
                        return {
                            "decision": "continue",
                            "reason": (
                                "CONSTITUTIONAL VIOLATION (Directive 3.1 — Chapter 5 Prose-Only Invariant): "
                                "Chapter 5 (Discussion & Conclusion) must contain strictly ZERO tables. "
                                "It must be 100% continuous narrative prose. Remove all Markdown or Word tables from Chapter 5 deliverables."
                            )
                        }

                    # 4. Directive 4: Prohibition of p = .000 and naked Persian decimals
                    if re.search(r'\bp\s*=\s*\.000\b', content, re.IGNORECASE):
                        return {
                            "decision": "continue",
                            "reason": (
                                "CONSTITUTIONAL VIOLATION (Directive 4 — APA 7th Precision):\n"
                                "Prohibition of 'p = .000'. In academic reporting, report strictly as "
                                "'p < .001' in English and 'p < ۰.۰۰۱' (یا '۰.۰۰۱ > p') in Persian."
                            )
                        }
                    if re.search(r'(?<![۰-۹0-9])\.[۰-۹]+', content):
                        return {
                            "decision": "continue",
                            "reason": (
                                "CONSTITUTIONAL VIOLATION (Directive 4 — Persian Leading Zero Standard):\n"
                                "Detected naked decimal without leading zero in Persian text (e.g. '.۰۵'). "
                                "Never omit the leading zero in Persian. Always report as '۰.۰۵' or '۰.۰۰۱'."
                            )
                        }

                    # 5. Institutional 3-Table Regression Suite (LSN-2026-THREE-TABLE-REGRESSION-STANDARD-001)
                    if any(k in content.lower() for k in ("regression", "رگرسیون")) and any(k in content.lower() for k in ("فرضیه", "hypothesis")):
                        tbl_count = len(re.findall(r'^[ \t]*\|(?:\s*[:-]+[-:]+\s*\|)+[ \t]*$', content, re.MULTILINE))
                        if 1 <= tbl_count < 3:
                            return {
                                "decision": "continue",
                                "reason": (
                                    f"CONSTITUTIONAL VIOLATION (Institutional 3-Table Regression Standard — LSN-2026-THREE-TABLE-REGRESSION-STANDARD-001):\n"
                                    f"Regression hypotheses must be reported via exactly three separate tables: Table 1 (Correlations), "
                                    f"Table 2 (Model Summary & Combined ANOVA), and Table 3 (Coefficients & Collinearity). "
                                    f"Found only {tbl_count} table(s) in markdown deliverable."
                                )
                            }

                    # 6. Directive 5: Zero Arabic Letters in Persian Text
                    arabic_issues = find_disallowed_arabic_characters(content)
                    if arabic_issues:
                        details = "; ".join(
                            f"'{issue['glyph']}' ({issue['codepoint']} -> use {issue['replacement']})"
                            for issue in arabic_issues
                        )
                        return {
                            "decision": "continue",
                            "reason": (
                                f"CONSTITUTIONAL VIOLATION (Directive 5 — Persian Orthography Standard / Zero Arabic Letters Invariant):\n"
                                f"Detected disallowed Arabic character glyphs in response content: {details}.\n"
                                f"Academic deliverables and summaries must use standard Persian letters ('ی' U+06CC, 'ک' U+06A9, 'ه/ت', and digits ۰-۹)."
                            )
                        }
                    break
        except Exception:
            pass

    # 7. Scoped OpenXML Deliverables Audit (03_deliverables/ only)
    try:
        ok, reason = audit_writer_docx_deliverables(workspaces)
        if not ok:
            return {"decision": "continue", "reason": reason}
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
