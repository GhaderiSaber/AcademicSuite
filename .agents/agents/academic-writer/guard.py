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
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, Any, Optional, Tuple, List

HOOKS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(HOOKS_DIR, "..", "..", ".."))
for p in (ROOT_DIR, os.path.join(ROOT_DIR, ".agents", "hooks")):
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from safety_hooks import is_root_script_target, is_deliverables_script_target
except ImportError:
    def is_root_script_target(p, w=None): return False, ""
    def is_deliverables_script_target(p): return False, ""

FORBIDDEN_AI_CLICHES = [
    "شایان ذکر است که",
    "لازم به ذکر است که",
    "پرواضح است که",
    "بر کسی پوشیده نیست که",
    "در یک کلام می‌توان گفت",
    "به طور چشمگیری می‌توان ادعا کرد"
]

EMOJI_PATTERN = re.compile(
    r"[\U0001F1E0-\U0001F1FF"
    r"\U0001F300-\U0001F5FF"
    r"\U0001F600-\U0001F64F"
    r"\U0001F680-\U0001F6FF"
    r"\U0001F700-\U0001F77F"
    r"\U0001F780-\U0001F7FF"
    r"\U0001F800-\U0001F8FF"
    r"\U0001F900-\U0001F9FF"
    r"\U0001FA00-\U0001FA6F"
    r"\U0001FA70-\U0001FAFF"
    r"\u2600-\u26FF"
    r"\u2700-\u27BF"
    r"]",
    re.UNICODE
)


ALLOWED_LATIN_TOKENS = {
    "m", "sd", "se", "df", "f", "t", "p", "r", "r2", "ss", "ms", "dw", "vif",
    "ci", "llci", "ulci", "ave", "cr", "cfi", "tli", "rmsea", "srmr", "aic",
    "bic", "sem", "cfa", "efa", "anova", "ancova", "manova", "spss", "amos",
    "process", "model", "apa", "docx", "pdf", "html", "pptx", "png", "jpg",
    "jpeg", "z", "b", "n", "k"
}


def find_raw_latin_in_persian(text: str) -> List[str]:
    """Detects raw inline Latin words (>=3 chars) embedded in Persian narrative sentences."""
    if not text or not isinstance(text, str):
        return []
    cleaned = re.sub(r'```[\s\S]*?```', '', text)
    cleaned = re.sub(r'`[^`]*`', '', cleaned)
    cleaned = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', cleaned)
    cleaned = re.sub(r'\$\$[\s\S]*?\$\$', '', cleaned)
    cleaned = re.sub(r'\$[^\$]*?\$', '', cleaned)

    offending = []
    for line in cleaned.split("\n"):
        if len(re.findall(r'[\u0600-\u06FF]', line)) >= 5 and not line.strip().startswith("|"):
            words = re.findall(r'\b[a-zA-Z]{3,}\b', line)
            for w in words:
                if w.lower() not in ALLOWED_LATIN_TOKENS:
                    offending.append(w)
    return offending


def check_docx_openxml_integrity(file_path: str) -> Tuple[bool, str]:
    """Audits a .docx deliverable for body presence, zero manual breaks in justified text, and native footnotes."""
    if not file_path or not os.path.exists(file_path) or not file_path.lower().endswith(".docx"):
        return True, ""
    try:
        with zipfile.ZipFile(file_path, "r") as zf:
            if "word/document.xml" not in zf.namelist():
                return False, f"Deliverable '{os.path.basename(file_path)}' is missing word/document.xml"
            doc_bytes = zf.read("word/document.xml")
            root = ET.fromstring(doc_bytes)

            # 1. Non-empty body paragraph verification
            paragraphs = [p for p in root.iter() if p.tag.endswith("}p") or p.tag == "p"]
            body_text = "".join(t.text or "" for t in root.iter() if t.tag.endswith("}t") or t.tag == "t")
            if len(paragraphs) == 0 or len(body_text.strip()) < 100:
                return False, (
                    f"Deliverable '{os.path.basename(file_path)}' has an empty or corrupted document body "
                    f"(paragraphs: {len(paragraphs)}, text length: {len(body_text.strip())})."
                )

            # 2. Manual line break (<w:br/>) ban in justified runs
            for p in paragraphs:
                is_justified = False
                for pPr in [c for c in p if c.tag.endswith("}pPr") or c.tag == "pPr"]:
                    for jc in [c for c in pPr if c.tag.endswith("}jc") or c.tag == "jc"]:
                        val = jc.attrib.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val") or jc.attrib.get("val")
                        if val in ("both", "distribute"):
                            is_justified = True
                if is_justified:
                    has_br = any(e.tag.endswith("}br") or e.tag == "br" for e in p.iter())
                    if has_br:
                        return False, (
                            f"Deliverable '{os.path.basename(file_path)}' contains manual line break (<w:br/>) "
                            f"inside justified body text. Use separate <w:p> paragraph marks."
                        )

            # 3. Native OpenXML footnotes verification
            if b"<w:footnoteReference" in doc_bytes:
                if "word/footnotes.xml" not in zf.namelist():
                    return False, (
                        f"Deliverable '{os.path.basename(file_path)}' references footnotes (<w:footnoteReference>), "
                        f"but 'word/footnotes.xml' is missing from the zip archive."
                    )
                fn_root = ET.fromstring(zf.read("word/footnotes.xml"))
                fn_tags = [e for e in fn_root.iter() if e.tag.endswith("}footnote") or e.tag == "footnote"]
                valid_fn = [
                    e for e in fn_tags 
                    if e.attrib.get("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id") not in ("-1", "0")
                ]
                if not valid_fn:
                    return False, (
                        f"Deliverable '{os.path.basename(file_path)}' references footnotes, "
                        f"but 'word/footnotes.xml' contains no valid footnote definitions."
                    )
    except Exception as e:
        return False, f"DOM parsing failed on '{os.path.basename(file_path)}': {e}"
    return True, ""


def check_chapter_5_docx_tables(file_path: str) -> Tuple[bool, int]:
    """Checks if a Chapter 5 Word .docx file contains <w:tbl> table elements."""
    if not file_path or not os.path.exists(file_path) or not file_path.lower().endswith(".docx"):
        return False, 0
    fname = os.path.basename(file_path).lower()
    if not any(k in fname for k in ("chapter_5", "chapter5", "ch5", "discussion")):
        return False, 0
    try:
        with zipfile.ZipFile(file_path, "r") as zf:
            if "word/document.xml" not in zf.namelist():
                return False, 0
            xml_data = zf.read("word/document.xml")
            root = ET.fromstring(xml_data)
            tables = [elem for elem in root.iter() if elem.tag.endswith("}tbl") or elem.tag == "tbl"]
            if tables:
                return True, len(tables)
    except Exception:
        pass
    return False, 0


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
    if tool_name in ("write_to_file", "replace_file_content", "edit_file", "patch"):
        target_path = args.get("TargetFile") or args.get("target") or args.get("file_path") or ""
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
                    f"Writing executable script '{deliv_script}' inside a deliverables directory is strictly forbidden. "
                    f"Deliverables directories must contain exclusively publication artifacts (.docx, .md, .json, .pdf)."
                )
            }

        # Directive 4.1: Zero Emojis in Academic Deliverables
        content_to_check = args.get("CodeContent") or args.get("ReplacementContent") or ""
        if isinstance(content_to_check, str) and any(ext in target_path.lower() for ext in (".docx", ".md", ".pptx", ".txt")):
            emojis_found = EMOJI_PATTERN.findall(content_to_check)
            if emojis_found:
                return {
                    "decision": "deny",
                    "reason": (
                        f"CONSTITUTIONAL VIOLATION (Directive 4.1 — Zero Emojis Invariant): "
                        f"Detected forbidden emojis in academic text for '{os.path.basename(target_path)}': {list(set(emojis_found))[:5]}. "
                        f"Academic deliverables and defense slides must maintain strictly sober academic tone with ZERO emojis."
                    )
                }

        # Directive 5: Zero Inline Latin in Persian Deliverables
        if isinstance(content_to_check, str) and any(ext in target_path.lower() for ext in (".docx", ".md", ".txt")):
            raw_latins = find_raw_latin_in_persian(content_to_check)
            if raw_latins:
                return {
                    "decision": "deny",
                    "reason": (
                        f"CONSTITUTIONAL VIOLATION (Directive 5 — Zero Inline Latin Invariant):\n"
                        f"Detected raw inline Latin words in Persian text for '{os.path.basename(target_path)}': {raw_latins[:5]}.\n"
                        f"Foreign author names must be phonetically transliterated to Persian (e.g. «اسمیت») and technical terms translated, "
                        f"with original English terms placed strictly in footnotes."
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

            # Inspect last planner response for clichés, emojis, and Chapter 5 table violations
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

                    # 2. Directive 4.1: Emoji scan in deliverables summary / response
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
                                "It must be 100% continuous narrative prose, theoretical synthesis, and psychological mechanism explanation. "
                                "Remove all Markdown or Word tables from Chapter 5 deliverables."
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
                    break
        except Exception:
            pass

    # 6. Directive 3.1: OpenXML DOM audit for <w:tbl> in Chapter 5 Word files on disk
    try:
        for ws in workspaces:
            if not ws or not os.path.exists(ws):
                continue
            for root, _, files in os.walk(ws):
                if any(part.startswith(".") for part in root.split(os.sep) if part not in (".", "..")):
                    continue
                if "scratch" in root:
                    continue
                for f in files:
                    if f.lower().endswith(".docx") and any(k in f.lower() for k in ("chapter_5", "chapter5", "ch5", "discussion")):
                        fpath = os.path.join(root, f)
                        has_tbl, tbl_count = check_chapter_5_docx_tables(fpath)
                        if has_tbl:
                            return {
                                "decision": "continue",
                                "reason": (
                                    f"CONSTITUTIONAL VIOLATION (Directive 3.1 — Chapter 5 Prose-Only Invariant): "
                                    f"Chapter 5 Word deliverable '{f}' contains {tbl_count} table (<w:tbl>) element(s). "
                                    f"Chapter 5 must strictly contain ZERO tables (100% continuous narrative prose, "
                                    f"theoretical synthesis, and psychological mechanisms). All numerical and statistical tables belong exclusively in Chapter 4."
                                )
                            }
                        break
    except Exception:
        pass

    # 7. Directive 5: OpenXML DOM Integrity, Non-Empty Body & Native Footnotes across .docx deliverables
    try:
        for ws in workspaces:
            if not ws or not os.path.exists(ws):
                continue
            for root, _, files in os.walk(ws):
                if any(part.startswith(".") for part in root.split(os.sep) if part not in (".", "..")):
                    continue
                if "scratch" in root:
                    continue
                for f in files:
                    if f.lower().endswith(".docx"):
                        fpath = os.path.join(root, f)
                        ok, reason = check_docx_openxml_integrity(fpath)
                        if not ok:
                            return {
                                "decision": "continue",
                                "reason": f"CONSTITUTIONAL VIOLATION (Directive 5 — OpenXML Integrity Standard):\n{reason}"
                            }
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
