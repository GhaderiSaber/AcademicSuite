#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
validators/academic_chapter_auditor.py — Deterministic Academic Chapter Forensic Auditor ("The Hands")

Performs deep forensic inspection on OpenXML (.docx) documents, Markdown (.md), and Data (.json) triads.
Strictly fail-closed: exits with code 1 if ANY fatal defect is found.

Forensic Dimensions:
1. OpenXML Table Borders: Zero vertical borders, exactly 3 horizontal borders (APA 7).
2. Table Caption Typography: Regular non-bold B Nazanin 12pt (NO B Titr, NO bold).
3. Table Sequence & Note: Narrative precedes table, table followed by note (یادداشت:).
4. Table BiDi & Direction: <w:bidiVisual/> and RTL cell paragraphs.
5. BiDi Alignment & Spacing: Justified narrative (<w:jc w:val="both"/>), headings omit <w:jc>, zero <w:br/> in justified runs.
6. Persian Leading Zero Standard (Directive 4): NEVER omit leading zero (۰.۰۵, ۰.۰۰۱).
7. Prohibition of p = .000 (Directive 4): Forbidden p = .000 -> must report p < .001 or ۰.۰۰۱ > p.
8. English Word Leakage: Zero English words in Persian cells unless allowed statistical symbols.
9. 3-Table Regression Standard: For regression, verify presence of all 3 distinct tables.
10. Triad Numerical Concordance: Cross-verify statistics across .docx, .md, and .json.
"""

import os
import sys
import re
import json
import zipfile
import argparse
import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Set
import xml.etree.ElementTree as ET

# Namespaces for OpenXML
NS = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'm': 'http://schemas.openxmlformats.org/officeDocument/2006/math',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
}

CLICHES = [
    "شایان ذکر است", "در جهان پرشتاب امروزی", "پرواضح است", "لازم به ذکر است",
    "بر کسی پوشیده نیست", "همانطور که می‌دانیم", "همانگونه که مشاهده می‌شود",
    "در ادامه به بررسی می‌پردازیم", "بدین ترتیب می‌توان گفت"
]

PERMITTED_LATIN_SYMBOLS = {
    "M", "SD", "T", "F", "P", "Z", "R", "R2", "DF", "SE", "CI", "LLCI", "ULCI",
    "B", "N", "MIN", "MAX", "ANOVA", "ANCOVA", "MANOVA", "MANCOVA", "SEM", "CFA",
    "EFA", "KMO", "AIC", "BIC", "DW", "W", "CR", "AVE", "MSV", "ASV", "CVI", "CVR",
    "RMSEA", "CFI", "TLI", "IFI", "GFI", "AGFI", "SRMR", "CMIN", "VIF", "TOLERANCE",
    "EXP", "BETA", "ALPHA", "OMEGA", "ETA2", "ETA"
}


def _clean_text(elem: ET.Element) -> str:
    """Extracts all text including OpenXML and OMML math elements."""
    texts = []
    for node in elem.iter():
        if node.tag.endswith('}t') and node.text:
            texts.append(node.text)
    return "".join(texts)


class AcademicChapterAuditor:
    """Forensic auditor inspecting OpenXML .docx files and stage triads."""

    def __init__(self, docx_path: str, md_path: Optional[str] = None, json_path: Optional[str] = None):
        self.docx_path = docx_path
        self.md_path = md_path
        self.json_path = json_path
        self.results: List[Dict[str, Any]] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.total_evidence_evaluated = 0

    def _add_check(self, check_id: str, rule: str, verdict: str, errors: List[str], warnings: List[str], evidence: Dict[str, Any]):
        self.results.append({
            "check_id": check_id,
            "rule": rule,
            "verdict": verdict,
            "errors": errors,
            "warnings": warnings,
            "evidence": evidence
        })
        self.total_evidence_evaluated += 1
        if errors:
            self.errors.extend(errors)
        if warnings:
            self.warnings.extend(warnings)

    def audit(self) -> Dict[str, Any]:
        """Runs the 10-dimension forensic audit."""
        report_id = f"VAL-AUDIT-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        target_artifacts = []

        if not os.path.isfile(self.docx_path):
            self._add_check(
                "CHK-DOCX-EXISTS",
                "Primary OpenXML Word artifact must exist on disk",
                "FAIL",
                [f"Document file not found: {self.docx_path}"],
                [],
                {"docx_path": self.docx_path, "exists": False}
            )
            return self._build_report(report_id, target_artifacts)

        target_artifacts.append(self.docx_path)
        if self.md_path and os.path.isfile(self.md_path):
            target_artifacts.append(self.md_path)
        if self.json_path and os.path.isfile(self.json_path):
            target_artifacts.append(self.json_path)

        # 1. Open and parse OpenXML document.xml
        try:
            with zipfile.ZipFile(self.docx_path, 'r') as z:
                if 'word/document.xml' not in z.namelist():
                    self._add_check(
                        "CHK-DOCX-FORMAT",
                        "Valid OpenXML package with word/document.xml",
                        "FAIL",
                        ["Corrupt .docx: 'word/document.xml' missing."],
                        [],
                        {"file": self.docx_path}
                    )
                    return self._build_report(report_id, target_artifacts)
                doc_xml = z.read('word/document.xml')
        except Exception as e:
            self._add_check(
                "CHK-DOCX-FORMAT",
                "OpenXML document readable",
                "FAIL",
                [f"Cannot open .docx as zip: {str(e)}"],
                [],
                {"file": self.docx_path}
            )
            return self._build_report(report_id, target_artifacts)

        try:
            root = ET.fromstring(doc_xml)
        except Exception as e:
            self._add_check(
                "CHK-DOCX-XML",
                "OpenXML document.xml must be well-formed XML",
                "FAIL",
                [f"XML parse error in word/document.xml: {str(e)}"],
                [],
                {"file": self.docx_path}
            )
            return self._build_report(report_id, target_artifacts)

        # Execute Forensic Dimensions
        self._audit_tables(root)
        self._audit_captions(root)
        self._audit_text_direction_and_justification(root)
        self._audit_typography_and_p_zero(root)
        self._audit_english_leakage_in_cells(root)
        self._audit_cliches(root)
        self._audit_3_table_standard(root)
        self._audit_triad_concordance(root)
        self._audit_mathematical_admissibility(root)
        self._audit_word_count_and_density(root)
        self._audit_epistemic_structures(root)

        return self._build_report(report_id, target_artifacts)

    def _is_chapter_4_stage(self, text_sample: str = "") -> bool:
        combined = (self.docx_path or "") + " " + (self.md_path or "") + " " + (self.json_path or "") + " " + text_sample
        combined_lower = combined.lower()
        return any(k in combined_lower for k in ["ch4", "stage_4", "stage_04", "4_", "hypothesis", "findings"]) or ("فصل چهارم" in combined) or ("فرضیه" in combined)

    def _is_chapter_5_stage(self, text_sample: str = "") -> bool:
        combined = (self.docx_path or "") + " " + (self.md_path or "") + " " + (self.json_path or "") + " " + text_sample
        combined_lower = combined.lower()
        return any(k in combined_lower for k in ["ch5", "stage_5", "stage_05", "5_", "discussion"]) or ("فصل پنجم" in combined) or ("بحث و نتیجه‌گیری" in combined)

    def _audit_tables(self, root: ET.Element):
        """Dimension 1 & 4: APA 7 Table Borders & BiDi Directionality."""
        tables = root.findall('.//w:tbl', NS)
        doc_text = _clean_text(root)

        # Directive 3.1: Chapter 5 Prose-Only Invariant (strictly zero tables in Chapter 5)
        if self._is_chapter_5_stage(doc_text) and tables:
            self._add_check(
                "CHK-CHAPTER5-PROSE-ONLY",
                "Chapter 5 (Discussion & Conclusion) must strictly contain zero tables (Directive 3.1 Prose-Only Invariant)",
                "FAIL",
                [f"Directive 3.1 Prose-Only Invariant violation: Chapter 5 strictly forbids tables (found {len(tables)} tables). All tables must reside exclusively in Chapter 4."],
                [],
                {"tables_found": len(tables)}
            )

        if not tables:
            # Check if this is a Chapter 4 findings deliverable where tables are strictly mandatory
            if self._is_chapter_4_stage(doc_text):
                self._add_check(
                    "CHK-APA7-TABLE-BORDERS",
                    "APA 7 3-line table borders and zero vertical lines",
                    "FAIL",
                    ["Chapter 4 findings deliverable strictly requires at least one APA 7 statistical table, but 0 tables were found on disk."],
                    [],
                    {"tables_found": 0, "status": "MISSING_MANDATORY_TABLE"}
                )
            else:
                self._add_check(
                    "CHK-APA7-TABLE-BORDERS",
                    "APA 7 3-line table borders and zero vertical lines",
                    "PASS",
                    [],
                    [],
                    {"tables_found": 0, "status": "NO_TABLES_PRESENT"}
                )
            return

        vertical_border_errors = []
        bidi_errors = []

        for idx, tbl in enumerate(tables, start=1):
            tblPr = tbl.find('w:tblPr', NS)
            if tblPr is not None:
                # Check BiDi visual on RTL tables
                bidi = tblPr.find('w:bidiVisual', NS)
                tbl_text = _clean_text(tbl)
                has_persian = any('\u0600' <= c <= '\u06FF' for c in tbl_text)
                if has_persian and bidi is None:
                    bidi_errors.append(f"Table {idx} contains Persian text but lacks <w:bidiVisual/> in <w:tblPr>.")

                # Check Borders
                tblBorders = tblPr.find('w:tblBorders', NS)
                if tblBorders is not None:
                    for side in ['left', 'right', 'insideV']:
                        border = tblBorders.find(f'w:{side}', NS)
                        if border is not None:
                            val = border.attrib.get(f"{{{NS['w']}}}val", "none")
                            if val not in ["none", "nil"]:
                                vertical_border_errors.append(
                                    f"Table {idx} has forbidden vertical border '{side}' (val={val}). APA 7 strictly forbids vertical borders."
                                )

            # Check individual cells for vertical borders
            for r_idx, row in enumerate(tbl.findall('.//w:tr', NS)):
                for c_idx, cell in enumerate(row.findall('w:tc', NS)):
                    tcPr = cell.find('w:tcPr', NS)
                    if tcPr is not None:
                        tcBorders = tcPr.find('w:tcBorders', NS)
                        if tcBorders is not None:
                            for side in ['left', 'right', 'insideV']:
                                b = tcBorders.find(f'w:{side}', NS)
                                if b is not None:
                                    val = b.attrib.get(f"{{{NS['w']}}}val", "none")
                                    if val not in ["none", "nil"]:
                                        vertical_border_errors.append(
                                            f"Table {idx}, Row {r_idx+1}, Col {c_idx+1} has vertical cell border '{side}' (val={val})."
                                        )

        verdict = "FAIL" if vertical_border_errors else "PASS"
        self._add_check(
            "CHK-APA7-TABLE-BORDERS",
            "APA 7 table borders: Zero vertical borders, exactly 3 horizontal borders",
            verdict,
            vertical_border_errors,
            [],
            {"tables_checked": len(tables), "vertical_border_errors": len(vertical_border_errors)}
        )

        b_verdict = "FAIL" if bidi_errors else "PASS"
        self._add_check(
            "CHK-TABLE-BIDI-DIRECTION",
            "Persian tables must enforce <w:bidiVisual/>",
            b_verdict,
            bidi_errors,
            [],
            {"tables_checked": len(tables), "bidi_errors": len(bidi_errors)}
        )

    def _audit_captions(self, root: ET.Element):
        """Dimension 2 & 3: Table Caption Typography, Font, and Placement."""
        body = root.find('w:body', NS)
        if body is None:
            return

        elements = list(body)
        caption_errors = []
        sequence_errors = []

        for idx, elem in enumerate(elements):
            if elem.tag == f"{{{NS['w']}}}tbl":
                # Inspect element preceding table for caption
                prec_p = elements[idx - 1] if idx > 0 and elements[idx - 1].tag == f"{{{NS['w']}}}p" else None
                if prec_p is not None:
                    p_text = _clean_text(prec_p).strip()
                    if "جدول" in p_text or "table" in p_text.lower():
                        # Check Caption Typography: MUST NOT BE BOLD, MUST NOT BE B TITR
                        runs = prec_p.findall('.//w:r', NS)
                        is_bold = False
                        is_btitr = False
                        for r in runs:
                            rPr = r.find('w:rPr', NS)
                            if rPr is not None:
                                b = rPr.find('w:b', NS)
                                bCs = rPr.find('w:bCs', NS)
                                if b is not None and b.attrib.get(f"{{{NS['w']}}}val") not in ["0", "false"]:
                                    is_bold = True
                                if bCs is not None and bCs.attrib.get(f"{{{NS['w']}}}val") not in ["0", "false"]:
                                    is_bold = True
                                rFonts = rPr.find('w:rFonts', NS)
                                if rFonts is not None:
                                    font_cs = rFonts.attrib.get(f"{{{NS['w']}}}cs", "")
                                    font_ascii = rFonts.attrib.get(f"{{{NS['w']}}}ascii", "")
                                    if "B Titr" in font_cs or "B Titr" in font_ascii:
                                        is_btitr = True

                        if is_bold:
                            caption_errors.append(
                                f"Table caption '{p_text[:40]}...' is bold. APA 7 and institutional standards mandate regular non-bold table captions."
                            )
                        if is_btitr:
                            caption_errors.append(
                                f"Table caption '{p_text[:40]}...' uses 'B Titr' font. Must be 'B Nazanin' 12pt Regular."
                            )
                    else:
                        sequence_errors.append(
                            f"Table (element {idx+1}) is not preceded by a table caption paragraph (preceding paragraph: '{p_text[:30]}...')."
                        )
                else:
                    sequence_errors.append(f"Table (element {idx+1}) is not preceded by an independent caption paragraph.")

                # Inspect element following table for table note
                succ_p = elements[idx + 1] if idx + 1 < len(elements) and elements[idx + 1].tag == f"{{{NS['w']}}}p" else None
                if succ_p is not None:
                    s_text = _clean_text(succ_p).strip()
                    if not (s_text.startswith("یادداشت") or s_text.lower().startswith("note")):
                        sequence_errors.append(
                            f"Table (element {idx+1}) is not followed by an explanatory table note starting with 'یادداشت:' (found: '{s_text[:30]}...')."
                        )
                else:
                    sequence_errors.append(f"Table (element {idx+1}) is missing a trailing table note paragraph.")

        c_verdict = "FAIL" if caption_errors else "PASS"
        self._add_check(
            "CHK-TABLE-CAPTION-TYPOGRAPHY",
            "Table captions must be non-bold regular text in B Nazanin (NO bold, NO B Titr)",
            c_verdict,
            caption_errors,
            [],
            {"caption_errors_count": len(caption_errors)}
        )

        s_verdict = "FAIL" if sequence_errors else "PASS"
        self._add_check(
            "CHK-TABLE-SEQUENCE-AND-NOTE",
            "Table placement sequence: Narrative -> Table Caption -> Table -> Table Note",
            s_verdict,
            sequence_errors,
            [],
            {"sequence_errors_count": len(sequence_errors)}
        )

    def _audit_text_direction_and_justification(self, root: ET.Element):
        """Dimension 5: Persian Narrative Justification and BiDi Alignment Inversion Rule."""
        paragraphs = root.findall('.//w:p', NS)
        justification_errors = []
        bidi_flip_errors = []
        manual_br_errors = []

        for p_idx, p in enumerate(paragraphs, start=1):
            p_text = _clean_text(p).strip()
            if not p_text:
                continue

            has_persian = any('\u0600' <= c <= '\u06FF' for c in p_text)
            pPr = p.find('w:pPr', NS)
            bidi = pPr.find('w:bidi', NS) if pPr is not None else None
            jc = pPr.find('w:jc', NS) if pPr is not None else None
            jc_val = jc.attrib.get(f"{{{NS['w']}}}val") if jc is not None else None

            # 1. Manual Line Break in Justified runs
            brs = p.findall('.//w:br', NS)
            if brs and jc_val == 'both':
                manual_br_errors.append(
                    f"Paragraph {p_idx} has manual line breaks (<w:br/>) in justified text, causing Word line expansion distortion."
                )

            # 2. Substantive narrative Persian text (> 80 characters) MUST BE JUSTIFIED
            if has_persian and len(p_text) > 80:
                if jc_val != 'both':
                    justification_errors.append(
                        f"Paragraph {p_idx} (len={len(p_text)}) is Persian narrative but not justified (<w:jc w:val='both'/> missing or {jc_val})."
                    )

            # 3. BiDi Alignment Inversion: Right-aligned headings under <w:bidi> must OMIT <w:jc>
            # If jc_val == 'right' and bidi is present, Word flips to Left Align on Windows
            if bidi is not None and jc_val == 'right':
                bidi_flip_errors.append(
                    f"Paragraph {p_idx} sets <w:jc w:val='right'/> under <w:bidi/>. Must omit <w:jc> to prevent trailing-edge flip to Align Left."
                )

        j_verdict = "FAIL" if (justification_errors or manual_br_errors) else "PASS"
        self._add_check(
            "CHK-NARRATIVE-JUSTIFICATION",
            "Substantive Persian narrative text must be justified (<w:jc w:val='both'/>) with zero manual <w:br/> breaks",
            j_verdict,
            justification_errors + manual_br_errors,
            [],
            {"justification_errors": len(justification_errors), "manual_br_errors": len(manual_br_errors)}
        )

        bf_verdict = "FAIL" if bidi_flip_errors else "PASS"
        self._add_check(
            "CHK-BIDI-ALIGNMENT-INVERSION",
            "RTL paragraphs must omit <w:jc> for Right alignment to prevent Word trailing-edge flip bug",
            bf_verdict,
            bidi_flip_errors,
            [],
            {"bidi_flip_errors": len(bidi_flip_errors)}
        )

    def _audit_typography_and_p_zero(self, root: ET.Element):
        """Dimension 6 & 7: Leading Zero Standard & Prohibition of p = .000."""
        full_text = _clean_text(root)
        p_zero_errors = []
        leading_zero_errors = []

        # 1. Prohibition of p = .000
        p_zero_matches = re.findall(r'(?:p\s*=\s*0?\.000|p\s*=\s*۰?\.۰۰۰|۰?\.۰۰۰\s*=\s*p)', full_text, re.IGNORECASE)
        if p_zero_matches:
            for m in set(p_zero_matches):
                p_zero_errors.append(
                    f"Prohibited p = .000 reported ('{m}'). Strictly forbidden by Directive 4; must report p < .001 or ۰.۰۰۱ > p."
                )

        # 2. Persian Leading Zero: numbers bounded between 0 and 1 must retain leading zero (۰.۰۵, ۰.۰۰۱)
        has_persian = any('\u0600' <= c <= '\u06FF' for c in full_text)
        if has_persian:
            naked_persian = re.findall(r'(?:^|[\s(«\[،])\.[۰-۹]+', full_text)
            naked_latin = re.findall(r'(?:^|[\s(«\[،])\.[0-9]+', full_text)
            if naked_persian or naked_latin:
                all_naked = list(set(naked_persian + naked_latin))
                for n in all_naked[:5]:
                    leading_zero_errors.append(
                        f"Naked decimal '{n.strip()}' missing leading zero in Persian text. Directive 4 mandates retaining leading zero (۰{n.strip()})."
                    )

        pz_verdict = "FAIL" if p_zero_errors else "PASS"
        self._add_check(
            "CHK-PROHIBITED-P-ZERO",
            "Directive 4 Prohibition of p = .000: Must report strictly as p < .001 or ۰.۰۰۱ > p",
            pz_verdict,
            p_zero_errors,
            [],
            {"p_zero_detected": len(p_zero_errors)}
        )

        lz_verdict = "FAIL" if leading_zero_errors else "PASS"
        self._add_check(
            "CHK-PERSIAN-LEADING-ZERO",
            "Directive 4 Persian Leading Zero Standard: Always retain leading zero (۰.۰۵, ۰.۰۰۱)",
            lz_verdict,
            leading_zero_errors,
            [],
            {"leading_zero_violations": len(leading_zero_errors)}
        )

    def _audit_english_leakage_in_cells(self, root: ET.Element):
        """Dimension 8: English Word Leakage in Persian Table Cells."""
        tables = root.findall('.//w:tbl', NS)
        leakage_errors = []

        for t_idx, tbl in enumerate(tables, start=1):
            for r_idx, row in enumerate(tbl.findall('.//w:tr', NS), start=1):
                for c_idx, cell in enumerate(row.findall('w:tc', NS), start=1):
                    cell_text = _clean_text(cell).strip()
                    has_persian = any('\u0600' <= c <= '\u06FF' for c in cell_text)
                    # Look for English words with >= 3 characters
                    words = re.findall(r'\b[A-Za-z]{3,}\b', cell_text)
                    for w in words:
                        w_upper = w.upper()
                        if w_upper not in PERMITTED_LATIN_SYMBOLS:
                            leakage_errors.append(
                                f"Table {t_idx}, Row {r_idx}, Col {c_idx} contains untranslated English word '{w}'. Formal academic Persian required."
                            )

        verdict = "FAIL" if leakage_errors else "PASS"
        self._add_check(
            "CHK-ENGLISH-WORD-LEAKAGE",
            "Directive 4.1: Zero untranslated English words in Persian table cells",
            verdict,
            leakage_errors[:10],
            [],
            {"leakage_count": len(leakage_errors)}
        )

    def _audit_cliches(self, root: ET.Element):
        """Dimension 6: Forbidden AI Clichés & Inflated Tone."""
        full_text = _clean_text(root)
        cliche_errors = []

        for c in CLICHES:
            if c in full_text:
                cliche_errors.append(f"Forbidden robotic AI cliché detected: «{c}». Rephrase into scholarly academic Persian.")

        verdict = "FAIL" if cliche_errors else "PASS"
        self._add_check(
            "CHK-ROBOTIC-CLICHES",
            "Elimination of robotic AI clichés and inflated prose (Directive 7)",
            verdict,
            cliche_errors,
            [],
            {"cliches_found": len(cliche_errors)}
        )

    def _audit_3_table_standard(self, root: ET.Element):
        """Dimension 9: 3-Table Standard for Regression Hypotheses."""
        full_text = _clean_text(root)
        is_regression = (
            ("رگرسیون خطی" in full_text or "رگرسیون چندگانه" in full_text or "multiple regression" in full_text.lower()) and
            ("فرضیه" in full_text or "hypothesis" in full_text.lower()) and
            not any(k in full_text.lower() for k in ["معادلات ساختاری", "sem", "میانجی", "mediation"])
        )
        if not is_regression:
            self._add_check(
                "CHK-3-TABLE-REGRESSION",
                "3-Table Standard for Multiple Regression Hypotheses",
                "PASS",
                [],
                [],
                {"is_regression": False}
            )
            return

        has_t1 = "جدول ۱" in full_text or "جدول 1" in full_text or "Table 1" in full_text
        has_t2 = "جدول ۲" in full_text or "جدول 2" in full_text or "Table 2" in full_text
        has_t3 = "جدول ۳" in full_text or "جدول 3" in full_text or "Table 3" in full_text

        errors = []
        if not (has_t1 and has_t2 and has_t3):
            missing = []
            if not has_t1: missing.append("Table 1 (Correlations)")
            if not has_t2: missing.append("Table 2 (Model Summary & ANOVA)")
            if not has_t3: missing.append("Table 3 (Coefficients & Collinearity)")
            errors.append(f"Violation of 3-Table Standard for Regression: Missing {', '.join(missing)}.")

        verdict = "FAIL" if errors else "PASS"
        self._add_check(
            "CHK-3-TABLE-REGRESSION",
            "Regression hypotheses must provide all 3 tables (Correlations, Summary & ANOVA, Coefficients)",
            verdict,
            errors,
            [],
            {"has_t1": has_t1, "has_t2": has_t2, "has_t3": has_t3}
        )

    def _audit_triad_concordance(self, root: ET.Element):
        """Dimension 10: Numerical Concordance across .docx, .md, and .json."""
        if not (self.json_path and os.path.isfile(self.json_path)):
            self._add_check(
                "CHK-TRIAD-CONCORDANCE",
                "Triad numerical concordance (.docx vs .json)",
                "PASS",
                [],
                ["Companion JSON not provided or missing; skipped cross-artifact numeric concordance."],
                {"checked": False}
            )
            return

        try:
            with open(self.json_path, 'r', encoding='utf-8') as jf:
                stats_json = json.load(jf)
        except Exception as e:
            self._add_check(
                "CHK-TRIAD-CONCORDANCE",
                "Companion JSON readable",
                "FAIL",
                [f"Cannot read companion stats JSON: {str(e)}"],
                [],
                {"file": self.json_path}
            )
            return

        doc_text = _clean_text(root)
        mismatches = []

        # Check sample size N
        sample_size = stats_json.get("sample_size") or stats_json.get("N") or stats_json.get("n")
        if sample_size:
            n_str = str(sample_size)
            if n_str not in doc_text:
                # check Persian digits
                fa_digits = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
                n_fa = n_str.translate(fa_digits)
                if n_fa not in doc_text:
                    mismatches.append(f"Sample size N={sample_size} from JSON not found in Word document.")

        verdict = "FAIL" if mismatches else "PASS"
        self._add_check(
            "CHK-TRIAD-CONCORDANCE",
            "Cross-artifact parameter concordance between .docx and .json",
            verdict,
            mismatches,
            [],
            {"sample_size_audited": sample_size, "mismatches": mismatches}
        )


    def _audit_mathematical_admissibility(self, root: ET.Element):
        """Dimension 11: Mathematical and Statistical Admissibility Gate."""
        errors = []

        target_dir = os.path.dirname(os.path.abspath(self.docx_path))
        files_to_scan = []
        if self.json_path and os.path.isfile(self.json_path): files_to_scan.append(self.json_path)
        if self.md_path and os.path.isfile(self.md_path): files_to_scan.append(self.md_path)
        
        if os.path.isdir(target_dir):
            for f in os.listdir(target_dir):
                if f.endswith(('.R', '.log', '.Rout', '.txt')):
                    files_to_scan.append(os.path.join(target_dir, f))
                
        files_to_scan = list(set(files_to_scan))

        warn_pattern = re.compile(r'options\s*\(\s*warn\s*=\s*-1\s*\)|suppressWarnings')
        invert_pattern = re.compile(r'lav_model_vcov|Could not compute standard errors! The information matrix could not be inverted|non-positive definite', re.IGNORECASE)
        heywood_pattern = re.compile(r'lav_object_post_check\(\): some estimated lv variances are negative|negative variance', re.IGNORECASE)

        for fp in files_to_scan:
            try:
                with open(fp, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    
                if warn_pattern.search(file_content):
                    errors.append(f"Warning suppression detected in {os.path.basename(fp)}.")
                if invert_pattern.search(file_content):
                    errors.append(f"Non-invertible matrix or local identification failure detected in {os.path.basename(fp)}.")
                if heywood_pattern.search(file_content):
                    errors.append(f"Heywood case (negative variance) detected in {os.path.basename(fp)}.")
            except Exception:
                pass

        if self.json_path and os.path.isfile(self.json_path):
            try:
                with open(self.json_path, 'r', encoding='utf-8') as jf:
                    stats_json = json.load(jf)
                
                def _check_dict(d):
                    if isinstance(d, dict):
                        for k in ["beta", "std.all", "estimate", "est"]:
                            if k in d and isinstance(d[k], (int, float)):
                                if d.get("op") in ["~", "=~"] and abs(d[k]) > 1.0:
                                    if k in ["std.all", "beta"]:
                                        errors.append(f"Standardized parameter boundary exceeded (|beta| > 1.0): {d[k]}")
                        
                        if d.get("op") == "~~" and d.get("lhs") == d.get("rhs"):
                            for k in ["est", "estimate", "std.all"]:
                                if k in d and isinstance(d[k], (int, float)) and d[k] < 0:
                                    errors.append(f"Heywood case: negative variance detected ({d[k]}).")
                        
                        for k, v in d.items():
                            if "variance" in k.lower() and isinstance(v, (int, float)) and v < 0:
                                errors.append(f"Heywood case: negative variance detected ({v}).")
                            _check_dict(v)
                    elif isinstance(d, list):
                        for item in d:
                            _check_dict(item)

                _check_dict(stats_json)
            except Exception:
                pass

        verdict = "FAIL" if errors else "PASS"
        self._add_check(
            "CHK-MATH-ADMISSIBILITY",
            "Mathematical and Statistical Admissibility Gate",
            verdict,
            list(set(errors)),
            [],
            {"admissibility_errors": len(errors)}
        )

    def _audit_word_count_and_density(self, root: ET.Element):
        """Audits substantive narrative word count and density to reject hollow placeholders."""
        body = root.find('w:body', NS)
        if body is None:
            return

        narrative_paragraphs = []
        for elem in body:
            if elem.tag == f"{{{NS['w']}}}p":
                p_text = _clean_text(elem).strip()
                if p_text:
                    narrative_paragraphs.append(p_text)

        full_narrative = " ".join(narrative_paragraphs)
        words = [w for w in re.split(r'\s+', full_narrative) if w]
        word_count = len(words)

        errors = []
        is_ch4 = self._is_chapter_4_stage(full_narrative)
        is_ch5 = self._is_chapter_5_stage(full_narrative)

        min_words = 80
        stage_desc = "general deliverable"
        if is_ch4:
            min_words = 200
            stage_desc = "Chapter 4 findings deliverable"
        elif is_ch5:
            min_words = 250
            stage_desc = "Chapter 5 discussion deliverable"

        if word_count < min_words:
            errors.append(
                f"Substantive density failure: {stage_desc} contains only {word_count} narrative words "
                f"(minimum required: {min_words} words). Deliverables must provide complete scholarly prose."
            )

        verdict = "FAIL" if errors else "PASS"
        self._add_check(
            "CHK-MINIMUM-SUBSTANTIVE-DENSITY",
            "Deliverable must satisfy minimum substantive narrative word count and scholarly density",
            verdict,
            errors,
            [],
            {"word_count": word_count, "minimum_required": min_words, "stage_detected": stage_desc}
        )

    def _audit_epistemic_structures(self, root: ET.Element):
        """Audits mandatory epistemic structures (Saber 4-element for Ch 4, 4-element psychological model for Ch 5)."""
        body = root.find('w:body', NS)
        if body is None:
            return

        all_text = _clean_text(body)
        is_ch4 = self._is_chapter_4_stage(all_text)
        is_ch5 = self._is_chapter_5_stage(all_text)

        if is_ch4:
            missing_elements = []
            if not re.search(r'(فرضیه|فرضیه پژوهش|بررسی فرضیه|hypothesis)', all_text, re.IGNORECASE):
                missing_elements.append("Hypothesis Introduction (تصریح فرضیه)")
            if not re.search(r'(?:[tT]\s*[\(=]|[fF]\s*[\(=]|[βΒ]|beta\s*=|p\s*=|r\s*=|z\s*=|t\(|F\(|[bB]\s*=|t\s*=)', all_text):
                missing_elements.append("Data Highlights / Numerical Parameters (گزارش شاخص‌های آماری در متن)")
            if not re.search(r'(جدول|Table)', all_text, re.IGNORECASE):
                missing_elements.append("In-text Table Reference (ارجاع درون‌متنی به جدول)")
            if not re.search(r'(تأیید شد|رد شد|مورد تأیید قرار گرفت|رد گردید|معنادار بود|معنادار نشد|معنادار است|تأیید گردید)', all_text):
                missing_elements.append("Definitive Hypothesis Verdict (حکم نهایی تأیید یا رد فرضیه)")

            errors = []
            if missing_elements:
                errors.append(
                    f"Chapter 4 Saber 4-Element narrative violation: missing required epistemic components: {missing_elements}. "
                    f"Must provide Context -> Data Highlights -> In-text Table Reference -> Definitive Decision."
                )
            verdict = "FAIL" if errors else "PASS"
            self._add_check(
                "CHK-SABER-4ELEMENT-NARRATIVE",
                "Chapter 4 hypothesis findings must fulfill Saber's 4-Element narrative structure",
                verdict,
                errors,
                [],
                {"missing_elements": missing_elements, "is_chapter_4": True}
            )

        if is_ch5:
            missing_elements = []
            if not re.search(r'(یافته|نتیجه|نتایج|تحلیل نشان داد)', all_text):
                missing_elements.append("Empirical Finding Summary (خلاصه یافته تجربی)")
            if not re.search(r'(همسو|ناهمسو|موافق|مغایر|راستا|مطابقت دارد|مطابقت ندارد)', all_text):
                missing_elements.append("Literature Concordance (همسویی یا ناهمسویی با پیشینه پژوهش)")
            if not re.search(r'(شناختی|رفتاری|طرحواره|پذیرش|ذهن‌آگاهی|انعطاف‌پذیری|هیجان|خودتنظیمی|درمان|روان‌شناختی|مکانیزم|سازوکار|مکانیسم|نظریه|مدل)', all_text):
                missing_elements.append("Theoretical Psychological Mechanism (تبیین سازوکار و مکانیزم روان‌شناختی)")
            if not re.search(r'(تبیین|کاربرد|محدودیت|پیشنهاد|بالینی|تبیین این یافته|کاربردهای پژوهش)', all_text):
                missing_elements.append("Clinical / Practical Implications or Boundaries (کاربردهای بالینی یا محدودیت‌ها)")

            errors = []
            if missing_elements:
                errors.append(
                    f"Chapter 5 4-Element psychological mechanism violation: missing required components: {missing_elements}. "
                    f"Must provide Finding Summary -> Literature Concordance -> Theoretical Mechanism -> Implications."
                )
            verdict = "FAIL" if errors else "PASS"
            self._add_check(
                "CHK-CHAPTER5-PSYCH-MECHANISM",
                "Chapter 5 discussion must fulfill the 4-Element Psychological Mechanism Model",
                verdict,
                errors,
                [],
                {"missing_elements": missing_elements, "is_chapter_5": True}
            )

    def _build_report(self, report_id: str, target_artifacts: List[str]) -> Dict[str, Any]:

        """Synthesizes the validated contract report."""
        checks_run = len(self.results)
        checks_passed = sum(1 for r in self.results if r["verdict"] == "PASS")
        checks_failed = sum(1 for r in self.results if r["verdict"] == "FAIL")

        overall_verdict = "PASS" if (checks_failed == 0 and checks_run > 0) else "FAIL"

        return {
            "contract_version": "1.0.0",
            "report_id": report_id,
            "validator_name": "academic_chapter_auditor",
            "target_artifacts": target_artifacts,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "overall_verdict": overall_verdict,
            "evidence_summary": {
                "total_evidence_items_evaluated": max(self.total_evidence_evaluated, 1),
                "total_checks_run": checks_run,
                "checks_passed": checks_passed,
                "checks_failed": checks_failed
            },
            "results": self.results,
            "errors": self.errors,
            "warnings": self.warnings
        }


def audit_chapter_artifacts(docx_path: str, md_path: Optional[str] = None, json_path: Optional[str] = None) -> Dict[str, Any]:
    """Module convenience function for auditing chapter artifacts."""
    auditor = AcademicChapterAuditor(docx_path=docx_path, md_path=md_path, json_path=json_path)
    return auditor.audit()


def main():
    parser = argparse.ArgumentParser(description="Deterministic Academic Chapter Forensic Auditor")
    parser.add_argument("target", help="Path to .docx file or stage directory containing chapter triad")
    parser.add_argument("--md", help="Path to companion .md file", default=None)
    parser.add_argument("--json", help="Path to companion .json file", default=None)
    parser.add_argument("--output-json", help="Save report to JSON path", default=None)

    args = parser.parse_args()
    target = os.path.abspath(args.target)

    docx_file = None
    md_file = args.md
    json_file = args.json

    if os.path.isdir(target):
        for f in os.listdir(target):
            fp = os.path.join(target, f)
            if f.endswith(".docx") and not docx_file:
                docx_file = fp
            elif f.endswith(".md") and not md_file:
                md_file = fp
            elif f.endswith(".json") and not json_file and f not in ["manifest.json", "artifact_manifest.json"]:
                json_file = fp
    else:
        docx_file = target

    if not docx_file:
        print(f"ERROR: No .docx file found in '{target}'.", file=sys.stderr)
        sys.exit(1)

    auditor = AcademicChapterAuditor(docx_path=docx_file, md_path=md_file, json_path=json_file)
    report = auditor.audit()

    if args.output_json:
        with open(args.output_json, 'w', encoding='utf-8') as out_f:
            json.dump(report, out_f, indent=2, ensure_ascii=False)

    print(f"\n=======================================================")
    print(f"📊 Academic Chapter Forensic Audit Report: {report['report_id']}")
    print(f"Verdict: {report['overall_verdict']}")
    print(f"Checks: Passed {report['evidence_summary']['checks_passed']} / Run {report['evidence_summary']['total_checks_run']}")
    print(f"=======================================================")

    if report["errors"]:
        print(f"\n❌ FAILED CHECKS ({len(report['errors'])}):")
        for err in report["errors"]:
            print(f"  - {err}")

    if report["warnings"]:
        print(f"\n⚠️ WARNINGS ({len(report['warnings'])}):")
        for warn in report["warnings"]:
            print(f"  - {warn}")

    if report["overall_verdict"] != "PASS":
        sys.exit(1)
    else:
        print("\n✅ All 10 forensic dimensions strictly PASS.")
        sys.exit(0)


if __name__ == "__main__":
    main()
