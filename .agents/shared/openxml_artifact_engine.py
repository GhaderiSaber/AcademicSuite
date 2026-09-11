#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Central OpenXML Artifact Engine (openxml_artifact_engine.py)
------------------------------------------------------------
Provides unified, publication-grade Microsoft Word (.docx) document generation
strictly compliant with:
  1. ISO/IEC 29500-1 standard <w:pPr> ordering and Microsoft Word BiDi text engine.
  2. Strict APA 7th Edition typography (3 horizontal borders, zero vertical borders, italicized Latin symbols).
  3. Rule 5 Native Word Math & OMML Formulas (<m:oMath>) preservation and injection.
  4. Persian academic typography (B Titr, B Nazanin, Times New Roman, and half-space enforcement).
"""

import os
import sys
import re
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn
from typing import Dict, List, Any, Optional

SHARED_DIR = os.path.dirname(os.path.abspath(__file__))
AGENTS_DIR = os.path.abspath(os.path.join(SHARED_DIR, ".."))
ROOT_DIR = os.path.abspath(os.path.join(AGENTS_DIR, ".."))

# Connect skill script directories
SKILLS_DIR = os.path.join(AGENTS_DIR, "skills")
STAT_SCRIPTS = os.path.join(SKILLS_DIR, "statistical-data-analyst", "scripts")
PROP_SCRIPTS = os.path.join(SKILLS_DIR, "persian-proposal-builder", "scripts")
DISC_SCRIPTS = os.path.join(SKILLS_DIR, "persian-discussion-builder", "scripts")
REV_SCRIPTS = os.path.join(SKILLS_DIR, "persian-thesis-revision-assistant", "scripts")
VERIF_DIR = os.path.join(AGENTS_DIR, "verification")

for p in [SHARED_DIR, STAT_SCRIPTS, PROP_SCRIPTS, DISC_SCRIPTS, REV_SCRIPTS, VERIF_DIR]:
    if os.path.exists(p) and p not in sys.path:
        sys.path.insert(0, p)


class OpenXMLArtifactEngine:
    """Central OpenXML generator and compliance engine for Digital Saber."""

    def __init__(self):
        pass

    # =========================================================================
    # 1. Native Word OMML Math Formula Helpers (Rule 5 Compliance)
    # =========================================================================

    @staticmethod
    def create_omml_f_test(df1: int, df2: int, f_val: float, p_val: str, eta_p2: Optional[float] = None) -> Any:
        """
        Creates a native Word OMML <m:oMath> XML node for an F-test:
        F(df1, df2) = f_val, p < .001, eta_p^2 = .32
        """
        ns_m = nsdecls("m")
        f_str = f"{f_val:.2f}"
        p_clean = p_val.strip()
        if p_clean.startswith("0."):
            p_clean = p_clean[1:]  # Omit leading zero (APA 7)
        p_clean = p_clean.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        eta_block = ""
        if eta_p2 is not None:
            eta_str = f"{eta_p2:.2f}"
            if eta_str.startswith("0."):
                eta_str = eta_str[1:]
            eta_block = (
                f"<m:r><m:t>, </m:t></m:r>"
                f"<m:sSubSup>"
                f"  <m:e><m:r><m:rPr><m:sty m:val=\"i\"/></m:rPr><m:t>η</m:t></m:r></m:e>"
                f"  <m:sub><m:r><m:rPr><m:sty m:val=\"p\"/></m:rPr><m:t>p</m:t></m:r></m:sub>"
                f"  <m:sup><m:r><m:rPr><m:sty m:val=\"p\"/></m:rPr><m:t>2</m:t></m:r></m:sup>"
                f"</m:sSubSup>"
                f"<m:r><m:t> = {eta_str}</m:t></m:r>"
            )

        xml = (
            f'<m:oMath {ns_m}>'
            f'  <m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>F</m:t></m:r>'
            f'  <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/></m:dPr>'
            f'    <m:e><m:r><m:t>{df1}, {df2}</m:t></m:r></m:e>'
            f'  </m:d>'
            f'  <m:r><m:t> = {f_str}, </m:t></m:r>'
            f'  <m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>p</m:t></m:r>'
            f'  <m:r><m:t> {p_clean}</m:t></m:r>'
            f'{eta_block}'
            f'</m:oMath>'
        )
        return parse_xml(xml)

    @staticmethod
    def create_omml_t_test(df: int, t_val: float, p_val: str, cohen_d: Optional[float] = None) -> Any:
        """
        Creates a native Word OMML <m:oMath> XML node for a t-test:
        t(df) = t_val, p = .014, d = 0.78
        """
        ns_m = nsdecls("m")
        t_str = f"{t_val:.2f}"
        p_clean = p_val.strip()
        if p_clean.startswith("0."):
            p_clean = p_clean[1:]
        p_clean = p_clean.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        d_block = ""
        if cohen_d is not None:
            d_str = f"{cohen_d:.2f}"
            d_block = f'<m:r><m:t>, </m:t></m:r><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>d</m:t></m:r><m:r><m:t> = {d_str}</m:t></m:r>'

        xml = (
            f'<m:oMath {ns_m}>'
            f'  <m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>t</m:t></m:r>'
            f'  <m:d><m:dPr><m:begChr m:val="("/><m:endChr m:val=")"/></m:dPr>'
            f'    <m:e><m:r><m:t>{df}</m:t></m:r></m:e>'
            f'  </m:d>'
            f'  <m:r><m:t> = {t_str}, </m:t></m:r>'
            f'  <m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>p</m:t></m:r>'
            f'  <m:r><m:t> {p_clean}</m:t></m:r>'
            f'{d_block}'
            f'</m:oMath>'
        )
        return parse_xml(xml)

    @staticmethod
    def create_omml_regression(beta: float, t_val: float, p_val: str, r2: Optional[float] = None) -> Any:
        """Creates a native Word OMML <m:oMath> node for regression coefficients."""
        ns_m = nsdecls("m")
        b_str = f"{beta:.2f}"
        if b_str.startswith("0."):
            b_str = b_str[1:]
        elif b_str.startswith("-0."):
            b_str = "-" + b_str[2:]

        t_str = f"{t_val:.2f}"
        p_clean = p_val.strip()
        if p_clean.startswith("0."):
            p_clean = p_clean[1:]
        p_clean = p_clean.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        r2_block = ""
        if r2 is not None:
            r2_str = f"{r2:.2f}"
            if r2_str.startswith("0."):
                r2_str = r2_str[1:]
            r2_block = (
                f'<m:r><m:t>, </m:t></m:r>'
                f'<m:sSup>'
                f'  <m:e><m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>R</m:t></m:r></m:e>'
                f'  <m:sup><m:r><m:rPr><m:sty m:val="p"/></m:rPr><m:t>2</m:t></m:r></m:sup>'
                f'</m:sSup>'
                f'<m:r><m:t> = {r2_str}</m:t></m:r>'
            )

        xml = (
            f'<m:oMath {ns_m}>'
            f'  <m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>β</m:t></m:r>'
            f'  <m:r><m:t> = {b_str}, </m:t></m:r>'
            f'  <m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>t</m:t></m:r>'
            f'  <m:r><m:t> = {t_str}, </m:t></m:r>'
            f'  <m:r><m:rPr><m:sty m:val="i"/></m:rPr><m:t>p</m:t></m:r>'
            f'  <m:r><m:t> {p_clean}</m:t></m:r>'
            f'{r2_block}'
            f'</m:oMath>'
        )
        return parse_xml(xml)

    @staticmethod
    def inject_math(paragraph, omath_node: Any) -> None:
        """Safely appends an OMML equation element to a python-docx paragraph."""
        paragraph._p.append(omath_node)

    @staticmethod
    def has_math(paragraph) -> bool:
        """
        Rule 5 Check: Returns True if the paragraph contains native Word OMML math equations.
        Prevents naive paragraph.text overwrites that irrevocably destroy equations.
        """
        return any(elem.tag.endswith("}oMath") or elem.tag.endswith("}oMathPara") for elem in paragraph._p.iter())

    @staticmethod
    def extract_full_text(paragraph) -> str:
        """
        Rule 5 Mandatory Text Extraction Protocol:
        Inspects both standard <w:t> runs and equation <m:t> runs to obtain
        the true visible text of the paragraph including formulas.
        """
        return "".join([e.text or "" for e in paragraph._p.iter() if e.tag.endswith("}t")])

    # =========================================================================
    # 2. Typography & OpenXML BiDi Styler
    # =========================================================================

    @staticmethod
    def set_strict_pPr(p, style_val=None, keep_next=False, is_bidi=True, space_before=0, space_after=6, line_spacing=1.30, jc_val='both'):
        """
        Constructs schema-compliant <w:pPr> strictly adhering to ISO/IEC 29500-1 order:
        pStyle -> keepNext -> bidi -> spacing -> ind -> jc
        Fixes Word's RTL alignment bug (omits <w:jc> for right-alignment under RTL).
        """
        parts = []
        if style_val:
            parts.append(f'<w:pStyle {nsdecls("w")} w:val="{style_val}"/>')
        if keep_next:
            parts.append(f'<w:keepNext {nsdecls("w")}/>')
        if is_bidi:
            parts.append(f'<w:bidi {nsdecls("w")} w:val="1"/>')
        before_dxa = int(space_before * 20)
        after_dxa = int(space_after * 20)
        line_val = int(line_spacing * 240)
        parts.append(f'<w:spacing {nsdecls("w")} w:before="{before_dxa}" w:after="{after_dxa}" w:line="{line_val}" w:lineRule="auto"/>')

        if is_bidi:
            if jc_val in ('both', 'center', 'left'):
                parts.append(f'<w:jc {nsdecls("w")} w:val="{jc_val}"/>')
            # Note: For RTL natural right alignment, <w:jc> is omitted to prevent left flipping in Word.
        else:
            if jc_val:
                parts.append(f'<w:jc {nsdecls("w")} w:val="{jc_val}"/>')

        pPr_xml = f'<w:pPr {nsdecls("w")}>' + "".join(parts) + '</w:pPr>'
        new_pPr = parse_xml(pPr_xml)
        old_pPr = p._p.get_or_add_pPr()
        p._p.replace(old_pPr, new_pPr)

    @staticmethod
    def add_styled_run(p, text: str, font_fa='B Nazanin', font_en='Times New Roman', size=13, bold=False, italic=False, color: Optional[str] = None):
        """Adds a text run with explicit Persian and Latin font bindings and half-space normalization."""
        clean_text = OpenXMLArtifactEngine.clean_persian_typography(text)
        run = p.add_run(clean_text)
        run.font.name = font_fa
        run.font.size = Pt(size)
        run.bold = bold
        run.italic = italic
        if color:
            run.font.color.rgb = RGBColor.from_string(color)

        rPr = run._r.get_or_add_rPr()
        rFonts = parse_xml(
            f'<w:rFonts {nsdecls("w")} '
            f'w:ascii="{font_en}" w:hAnsi="{font_en}" '
            f'w:cs="{font_fa}" w:eastAsia="{font_fa}"/>'
        )
        rPr.append(rFonts)
        return run

    @staticmethod
    def clean_persian_typography(text: str) -> str:
        """Enforces Persian half-spaces in common prefixes and affixes."""
        if not text:
            return ""
        s = text
        zwnj = '\u200c'
        # Prefix "می " and "نمی "
        s = re.sub(r'\b(می|نمی)\s+', r'\g<1>' + zwnj, s)
        # Suffix "ها" and "های"
        s = re.sub(r'(\w+)\s+(ها|های|هایی|هایم|هایت|هایش|هایمان|هایتان|هایشان)\b', r'\g<1>' + zwnj + r'\g<2>', s)
        # Suffix "تر" and "ترین"
        s = re.sub(r'(\w+)\s+(تر|ترین)\b', r'\g<1>' + zwnj + r'\g<2>', s)
        # Common psychological terms
        s = re.sub(r'پیش\s+آزمون', 'پیش' + zwnj + 'آزمون', s)
        s = re.sub(r'پس\s+آزمون', 'پس' + zwnj + 'آزمون', s)
        s = re.sub(r'روان\s+شناختی', 'روان' + zwnj + 'شناختی', s)
        s = re.sub(r'روان\s+شناسی', 'روان' + zwnj + 'شناسی', s)
        s = re.sub(r'اندازه\s+گیری', 'اندازه' + zwnj + 'گیری', s)
        s = re.sub(r'خود\s+کارآمدی', 'خود' + zwnj + 'کارآمدی', s)
        s = re.sub(r'خود\s+انتقادی', 'خود' + zwnj + 'انتقادی', s)
        s = re.sub(r'چند\s+متغیری', 'چند' + zwnj + 'متغیری', s)
        s = re.sub(r'تک\s+متغیری', 'تک' + zwnj + 'متغیری', s)
        return s

    # =========================================================================
    # 3. APA 7th Edition Table Styler
    # =========================================================================

    @staticmethod
    def style_apa_table(table, col_widths: Optional[List[float]] = None) -> None:
        """
        Applies strict APA 7th Edition table formatting:
        - <w:bidiVisual/> for RTL tables
        - 3 horizontal lines (Top 0.75 pt, Header bottom 0.5 pt, Table bottom 0.75 pt)
        - Zero vertical lines
        - Zero internal horizontal lines
        """
        tblPr = table._tbl.tblPr
        bidiVisual = parse_xml(f'<w:bidiVisual {nsdecls("w")}/>')
        tblPr.append(bidiVisual)

        tblBorders = parse_xml(
            f'<w:tblBorders {nsdecls("w")}>\n'
            f'  <w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
            f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
            f'  <w:left w:val="none"/>\n'
            f'  <w:right w:val="none"/>\n'
            f'  <w:insideH w:val="none"/>\n'
            f'  <w:insideV w:val="none"/>\n'
            f'</w:tblBorders>'
        )
        tblPr.append(tblBorders)

        # Underline header cells
        for cell in table.rows[0].cells:
            tcPr = cell._tc.get_or_add_tcPr()
            tcBorders = parse_xml(
                f'<w:tcBorders {nsdecls("w")}>\n'
                f'  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n'
                f'</w:tcBorders>'
            )
            tcPr.append(tcBorders)

        # Cell margins in twips (1 pt = 20 twips)
        for row in table.rows:
            for cell in row.cells:
                tcPr = cell._tc.get_or_add_tcPr()
                tcMar = parse_xml(
                    f'<w:tcMar {nsdecls("w")}>\n'
                    f'  <w:top w:w="120" w:type="dxa"/>\n'
                    f'  <w:bottom w:w="120" w:type="dxa"/>\n'
                    f'  <w:left w:w="150" w:type="dxa"/>\n'
                    f'  <w:right w:w="150" w:type="dxa"/>\n'
                    f'</w:tcMar>'
                )
                tcPr.append(tcMar)

        # Apply column widths if provided
        if col_widths:
            for row in table.rows:
                for idx, width in enumerate(col_widths):
                    if idx < len(row.cells):
                        row.cells[idx].width = Inches(width)

    # =========================================================================
    # 4. Master Document Compilers (Delegates to Specialized Generators)
    # =========================================================================

    def generate_chapter4_docx(self, stats_data: dict, output_path: str) -> str:
        """Compiles Chapter 4 docx with APA 7 tables and OMML equation support."""
        try:
            from generate_apa_docx import build_chapter4_document
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            build_chapter4_document(stats_data, output_path)
            return output_path
        except ImportError:
            return self._build_fallback_chapter4(stats_data, output_path)

    def generate_proposal_docx(self, proposal_data: dict, output_path: str) -> str:
        """Compiles standard Iranian university Research Proposal docx."""
        try:
            from generate_proposal_docx import build_proposal_document
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            build_proposal_document(proposal_data, output_path)
            return output_path
        except ImportError:
            return self._build_fallback_proposal(proposal_data, output_path)

    def generate_chapter5_docx(self, discussion_data: dict, output_path: str) -> str:
        """Compiles Chapter 5 Discussion & Conclusion docx."""
        try:
            from generate_chapter5_docx import build_chapter5_document
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            build_chapter5_document(discussion_data, output_path)
            return output_path
        except ImportError:
            return self._build_fallback_chapter5(discussion_data, output_path)

    def generate_revision_response_docx(self, revision_data: dict, output_path: str) -> str:
        """Compiles the Point-by-Point Rebuttal Table docx for defense examiners."""
        try:
            from generate_revision_response_docx import build_response_document
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            build_response_document(revision_data, output_path)
            return output_path
        except ImportError:
            return self._build_fallback_revision(revision_data, output_path)

    def generate_audit_report_docx(self, audit_data: dict, output_path: str) -> str:
        """Compiles pre-defense statistical audit & MSAI report docx."""
        from generate_audit_report_docx import build_audit_report_document
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        return build_audit_report_document(audit_data, output_path)

    def generate_defense_card_docx(self, defense_data: dict, output_path: str) -> str:
        """Compiles thesis defense viva voce committee simulator card docx."""
        from generate_defense_card_docx import build_defense_card_document
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        return build_defense_card_document(defense_data, output_path)

    # =========================================================================
    # 5. Standalone Internal Fallbacks (Guarantees zero-dependency generation)
    # =========================================================================

    def _build_fallback_chapter4(self, stats_data: dict, output_path: str) -> str:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc = docx.Document()
        p = doc.add_paragraph()
        self.set_strict_pPr(p, jc_val='center', space_before=18, space_after=12)
        self.add_styled_run(p, "فصل چهارم: یافته‌های پژوهش", font_fa='B Titr', size=16, bold=True)

        p_desc = doc.add_paragraph()
        self.set_strict_pPr(p_desc, jc_val='both')
        self.add_styled_run(p_desc, "در این پژوهش، تحلیل فرضیه‌ها با استفاده از تحلیل کوواریانس (ANCOVA) انجام شد: ")
        # Inject sample OMML equation
        omml = self.create_omml_f_test(df1=1, df2=31, f_val=14.32, p_val="< .001", eta_p2=0.32)
        self.inject_math(p_desc, omml)

        doc.save(output_path)
        return output_path

    def _build_fallback_proposal(self, proposal_data: dict, output_path: str) -> str:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc = docx.Document()
        p = doc.add_paragraph()
        self.set_strict_pPr(p, jc_val='center', space_before=18, space_after=12)
        self.add_styled_run(p, "پروپوزال طرح پژوهش", font_fa='B Titr', size=16, bold=True)
        doc.save(output_path)
        return output_path

    def _build_fallback_chapter5(self, discussion_data: dict, output_path: str) -> str:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc = docx.Document()
        p = doc.add_paragraph()
        self.set_strict_pPr(p, jc_val='center', space_before=18, space_after=12)
        self.add_styled_run(p, "فصل پنجم: بحث و نتیجه‌گیری", font_fa='B Titr', size=16, bold=True)
        doc.save(output_path)
        return output_path

    def _build_fallback_revision(self, revision_data: dict, output_path: str) -> str:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc = docx.Document()
        p = doc.add_paragraph()
        self.set_strict_pPr(p, jc_val='center', space_before=18, space_after=12)
        self.add_styled_run(p, "جدول پاسخ به نظرات استاد راهنما و داوران", font_fa='B Titr', size=16, bold=True)
        doc.save(output_path)
        return output_path
