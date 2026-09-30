#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/verification/academic_writer_auditor.py

Dedicated verification engine for Academic Writer (academic-writer).
Audits:
1. OpenXML document body presence and non-corruption.
2. Manual line break (<w:br/>) ban in justified Persian paragraphs.
3. True native OpenXML footnotes (<w:footnoteReference> and word/footnotes.xml).
4. Persian academic orthography (zero disallowed Arabic characters: ي, ك, ة, ٠-٩).
5. Zero inline raw Latin script in Persian narrative prose.
6. Chapter 5 prose-only invariant (zero <w:tbl> tables).
"""

import os
import re
import zipfile
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Tuple

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

DISALLOWED_ARABIC_LETTERS = {
    '\u064A': ('ي', 'Persian Yeh "ی" (U+06CC)'),
    '\u0643': ('ك', 'Persian Keheh "ک" (U+06A9)'),
    '\u0629': ('ة', 'Persian Heh "ه" (U+0647) or Teh "ت" (U+062A)'),
}
ARABIC_DIGITS_PATTERN = re.compile(r'[\u0660-\u0669]')


def find_disallowed_arabic_characters(text: str) -> List[Dict[str, str]]:
    """Detects disallowed Arabic letter glyphs (ي, ك, ة) and Arabic digits (٠-٩) in Persian text."""
    if not text or not isinstance(text, str):
        return []
    cleaned = re.sub(r'```[\s\S]*?```', '', text)
    cleaned = re.sub(r'`[^`]*`', '', cleaned)
    cleaned = re.sub(r'\[([^\]]*)\]\([^\)]*\)', r'\1', cleaned)
    cleaned = re.sub(r'\$\$[\s\S]*?\$\$', '', cleaned)
    cleaned = re.sub(r'\$[^\$]*?\$', '', cleaned)

    violations = {}
    for line in cleaned.split("\n"):
        if len(re.findall(r'[\u0600-\u06FF]', line)) >= 3:
            for char, (glyph, replacement) in DISALLOWED_ARABIC_LETTERS.items():
                if char in line and glyph not in violations:
                    violations[glyph] = {
                        "glyph": glyph,
                        "codepoint": f"U+{ord(char):04X}",
                        "replacement": replacement,
                        "sample": line.strip()[:60]
                    }
            arabic_digits = ARABIC_DIGITS_PATTERN.findall(line)
            if arabic_digits and "Arabic Digits" not in violations:
                violations["Arabic Digits"] = {
                    "glyph": "".join(sorted(set(arabic_digits))),
                    "codepoint": "U+0660-U+0669",
                    "replacement": "Persian digits (۰-۹ / U+06F0-U+06F9)",
                    "sample": line.strip()[:60]
                }
    return list(violations.values())


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

            # 1. Non-empty document body check
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

            # 4. Persian orthography: check for disallowed Arabic letters in Persian body text
            has_persian = any('\u0600' <= c <= '\u06FF' for c in body_text)
            if has_persian:
                arabic_chars_found = set()
                for char in DISALLOWED_ARABIC_LETTERS:
                    if char in body_text:
                        arabic_chars_found.add(char)
                if arabic_chars_found:
                    char_desc = ", ".join(
                        f"'{c}' (U+{ord(c):04X} -> use {DISALLOWED_ARABIC_LETTERS[c][1]})"
                        for c in sorted(arabic_chars_found)
                    )
                    return False, (
                        f"Deliverable '{os.path.basename(file_path)}' contains disallowed Arabic letter characters "
                        f"in Persian text: {char_desc}. Directive 5 mandates standard Persian letters."
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


def audit_writer_docx_deliverables(workspaces: List[str]) -> Tuple[bool, str]:
    """
    Audits all .docx deliverables strictly in 03_deliverables/ across workspaces.
    Explicitly skips raw inputs, analysis code, references, and scratch directories.
    """
    cand_dirs = []
    for ws in workspaces:
        if not ws or not os.path.exists(ws):
            continue
        deliv_dir = os.path.join(ws, "03_deliverables")
        if os.path.isdir(deliv_dir):
            cand_dirs.append((deliv_dir, ws))
        else:
            cand_dirs.append((ws, ws))

    for d_dir, ws in cand_dirs:
        for root, _, files in os.walk(d_dir):
            rel = os.path.relpath(root, ws) if ws else root
            parts = rel.split(os.sep)
            if any(p in ("01_raw_inputs", "02_analysis_code", "04_references_and_lit", "scratch") or p.startswith(".") for p in parts):
                continue

            for f in files:
                if not f.lower().endswith(".docx"):
                    continue
                fpath = os.path.join(root, f)

                # Check Chapter 5 tables
                if any(k in f.lower() for k in ("chapter_5", "chapter5", "ch5", "discussion")):
                    has_tbl, tbl_count = check_chapter_5_docx_tables(fpath)
                    if has_tbl:
                        return False, (
                            f"CONSTITUTIONAL VIOLATION (Directive 3.1 — Chapter 5 Prose-Only Invariant): "
                            f"Chapter 5 Word deliverable '{f}' contains {tbl_count} table (<w:tbl>) element(s). "
                            f"Chapter 5 must strictly contain ZERO tables (100% continuous narrative prose). "
                            f"All numerical and statistical tables belong exclusively in Chapter 4."
                        )

                # Check OpenXML integrity
                ok, reason = check_docx_openxml_integrity(fpath)
                if not ok:
                    return False, f"CONSTITUTIONAL VIOLATION (Directive 5 — OpenXML Integrity Standard):\n{reason}"

    return True, ""
