#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/skills/persian-literature-review-builder/scripts/literature_synthesis_matrix_engine.py
Chapter 2 Literature Review Thematic Synthesis Matrix Engine (موتور جامع ماتریس سنتز و تلفیق پیشینه پژوهش)

Satisfies Stage 2.6 of the Chapter 2 Literature Review Pipeline (MICRO_STAGE_SEQUENCES.md):
- Produces synchronized triad deliverables on disk:
  1. 06_literature_matrix_table.docx (OpenXML BiDi RTL, authentic Persian typography, APA 7 borderless table)
  2. 06_literature_matrix_table.md   (Scholarly markdown narrative + thematic synthesis tables)
  3. 06_literature_matrix_table.json (Machine-readable structured parameters & gap matrix)
  4. Literature_Synthesis_Matrix.xlsx (4-sheet professional Excel workbook)

Constitutional Compliance:
- Directive 3: Micro-Stage Granularity & Triad Artifact Invariant (.docx + .md + .json)
- Directive 4: Strict APA 7th Edition & Persian Leading Zero Standard (۰.۰۰۱ > p)
- Directive 5: Persian Academic Typography & OpenXML BiDi Standards (B Nazanin / B Titr / Times New Roman)
- Directive 6: English-Only Filenames on disk
- Directive 14: Zero Ghost Citations (verifiable empirical metadata)
- Directive 15: Temporal Reality Anchor: 2021–2026 / 1400–1405 SH
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional, Tuple

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
EXAMPLES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "examples"))
if EXAMPLES_DIR not in sys.path:
    sys.path.insert(0, EXAMPLES_DIR)

for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

try:
    import docx
    from docx.shared import Pt, Inches, RGBColor
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.enum.table import WD_TABLE_ALIGNMENT
    from docx.oxml import parse_xml, OxmlElement
    from docx.oxml.ns import nsdecls, qn
    HAS_DOCX = True
except ImportError:
    HAS_DOCX = False

try:
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter
    HAS_OPENPYXL = True
except ImportError:
    HAS_OPENPYXL = False


# ==============================================================================
# OpenXML XML Helper Utilities for Word Documents (Directives 4 & 5)
# ==============================================================================

def set_run_font(
    run,
    font_name: str = "B Nazanin",
    size_pt: float = 13,
    bold: bool = False,
    italic: bool = False,
    is_latin: bool = False
):
    """Binds ASCII, High-ANSI, and Complex Script fonts strictly adhering to OpenXML standards."""
    run.bold = bold
    run.italic = italic
    run.font.size = Pt(size_pt)

    rPr = run._r.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)

    sz_val = int(size_pt * 2)
    if is_latin:
        rFonts.set(qn("w:ascii"), "Times New Roman")
        rFonts.set(qn("w:hAnsi"), "Times New Roman")
        rFonts.set(qn("w:cs"), "Times New Roman")
    else:
        rFonts.set(qn("w:ascii"), font_name)
        rFonts.set(qn("w:hAnsi"), font_name)
        rFonts.set(qn("w:cs"), font_name)
        rFonts.set(qn("w:eastAsia"), font_name)
        rFonts.set(qn("w:hint"), "cs")

        # Inject RTL run marker
        rtl = rPr.find(qn("w:rtl"))
        if rtl is None:
            rtl = parse_xml(f'<w:rtl {nsdecls("w")} w:val="1"/>')
            rPr.append(rtl)

        # Inject fa-IR proofing
        lang = rPr.find(qn("w:lang"))
        if lang is None:
            lang = parse_xml(f'<w:lang {nsdecls("w")} w:val="fa-IR" w:bidi="fa-IR"/>')
            rPr.append(lang)

    szCs = parse_xml(f'<w:szCs {nsdecls("w")} w:val="{sz_val}"/>')
    rPr.append(szCs)
    if bold:
        bCs = parse_xml(f'<w:bCs {nsdecls("w")} w:val="1"/>')
        rPr.append(bCs)


def set_p_bidi(
    p,
    align=WD_ALIGN_PARAGRAPH.JUSTIFY,
    space_before: float = 0,
    space_after: float = 6,
    line_spacing: float = 1.25,
    is_right_heading: bool = False
):
    """
    Enforces BiDi RTL directionality and strict child element ordering (<w:pPr>).
    For right-aligned Persian headings, omits <w:jc> under <w:bidi w:val='1'/> to avoid alignment flip.
    """
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing

    pPr = p._p.get_or_add_pPr()
    bidi = pPr.find(qn("w:bidi"))
    if bidi is None:
        bidi = parse_xml(f'<w:bidi {nsdecls("w")} w:val="1"/>')
        pPr.append(bidi)

    if is_right_heading:
        # Golden Rule: omit w:jc for RTL right-aligned text so Word natively aligns RIGHT
        jc = pPr.find(qn("w:jc"))
        if jc is not None:
            pPr.remove(jc)
    else:
        p.alignment = align


def set_table_apa7_borders_and_bidi(table):
    """
    Enforces Right-to-Left visual layout (<w:bidiVisual/>) and APA 7th Edition 3-line borders:
    - Top horizontal border: 0.75 pt (w:sz="6")
    - Bottom of header row: 0.50 pt (w:sz="4")
    - Table bottom border: 0.75 pt (w:sz="6")
    - Zero vertical borders.
    """
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    tblPr = table._tbl.tblPr

    # RTL Table visual layout
    bidiVisual = tblPr.find(qn("w:bidiVisual"))
    if bidiVisual is None:
        bidiVisual = parse_xml(f'<w:bidiVisual {nsdecls("w")}/>')
        tblPr.append(bidiVisual)

    # APA 7 3-line borders
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
        f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
        f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>\n'
        f'  <w:left w:val="none"/>\n'
        f'  <w:right w:val="none"/>\n'
        f'  <w:insideV w:val="none"/>\n'
        f'</w:tblBorders>'
    )
    old_borders = tblPr.find(qn("w:tblBorders"))
    if old_borders is not None:
        tblPr.remove(old_borders)
    tblPr.append(borders)


# ==============================================================================
# Thematic Clustering & Synthesis Metric Engine
# ==============================================================================

class ThematicClusteringEngine:
    """
    Clusters empirical studies around theoretical themes, evaluates concordance / discordance,
    computes sample metrics, and maps research gaps.
    """

    DESIGN_LABELS_FA = {
        "rct": "کارآزمایی بالینی تصادفی‌شده (RCT)",
        "quasi_experimental": "نیمه‌آزمایشی (پیش‌آزمون-پس‌آزمون با گروه کنترل)",
        "longitudinal": "طولی چندموجی (Longitudinal Panel)",
        "sem": "مدل‌سازی معادلات ساختاری (SEM)",
        "correlational": "توصیفی-همبستگی",
        "meta_analysis": "فراتحلیل (Meta-Analysis)",
        "qualitative": "کیفی (تحلیل مضمون / گراندد تئوری)"
    }

    @classmethod
    def analyze_payload(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Performs cross-study statistical analysis and synthesis across all themes."""
        themes = payload.get("themes", [])
        total_studies = 0
        all_sample_sizes = []
        design_counts = {}
        region_counts = {"iranian": 0, "international": 0}
        direction_counts = {"supporting": 0, "conflicting": 0, "non_significant": 0}
        analyzed_themes = []

        for th in themes:
            th_id = th.get("theme_id", "")
            th_title_fa = th.get("title", "")
            th_title_en = th.get("title_en", "")
            mechanism = th.get("theoretical_mechanism", "")
            hypothesized_path = th.get("hypothesized_path", "")
            studies = th.get("studies", [])

            theme_n_list = []
            theme_directions = {"supporting": 0, "conflicting": 0, "non_significant": 0}
            theme_studies_processed = []

            for idx, s in enumerate(studies, 1):
                total_studies += 1
                n = int(s.get("sample_size", 0))
                if n > 0:
                    all_sample_sizes.append(n)
                    theme_n_list.append(n)

                reg = str(s.get("region", "international")).lower()
                if "iran" in reg or "داخلی" in reg:
                    region_counts["iranian"] += 1
                    region_tag = "داخلی (ایران)"
                else:
                    region_counts["international"] += 1
                    region_tag = "بین‌المللی"

                design = str(s.get("design", "correlational")).lower()
                design_counts[design] = design_counts.get(design, 0) + 1

                direction = str(s.get("finding_direction", "supporting")).lower()
                if "support" in direction or "موافق" in direction:
                    direction_key = "supporting"
                    direction_badge = "همسو (مؤید رابطه)"
                elif "conflict" in direction or "مخالف" in direction:
                    direction_key = "conflicting"
                    direction_badge = "ناهمسو (متعارض)"
                else:
                    direction_key = "non_significant"
                    direction_badge = "فاقد رابطه معنادار"

                direction_counts[direction_key] = direction_counts.get(direction_key, 0) + 1
                theme_directions[direction_key] = theme_directions.get(direction_key, 0) + 1

                # Format statistics string with APA 7 + Persian standards
                stats = s.get("statistical_results", {})
                stat_str = cls._format_statistical_findings(stats, s.get("key_findings_fa", ""))

                # Build processed study entry
                proc_study = dict(s)
                proc_study["row_num"] = idx
                proc_study["region_badge"] = region_tag
                proc_study["design_badge_fa"] = s.get("design_fa") or cls.DESIGN_LABELS_FA.get(design, design)
                proc_study["direction_badge"] = direction_badge
                proc_study["formatted_stats_fa"] = stat_str
                theme_studies_processed.append(proc_study)

            # Determine theme concordance status
            total_th = len(studies)
            sup_count = theme_directions["supporting"]
            con_count = theme_directions["conflicting"]
            ns_count = theme_directions["non_significant"]

            if total_th == 0:
                concordance_verdict = "INSUFFICIENT_EVIDENCE"
                concordance_text_fa = "شواهد تجربی ناکافی"
            elif sup_count == total_th:
                concordance_verdict = "UNANIMOUS_SUPPORT"
                concordance_text_fa = "همگرایی قاطع و کامل شواهد در تأیید رابطه"
            elif sup_count > con_count and con_count == 0:
                concordance_verdict = "STRONG_SUPPORT"
                concordance_text_fa = "شواهد قدرتمند همسو بدون تضاد مستقیم"
            elif con_count > 0:
                concordance_verdict = "MIXED_OR_DISCORDANT"
                concordance_text_fa = "یافته‌های ناهمخوان و متناقض نیازمند آزمون تعدیل‌گر"
            else:
                concordance_verdict = "MODERATE_EVIDENCE"
                concordance_text_fa = "شواهد متوسط و مشروط"

            analyzed_themes.append({
                "theme_id": th_id,
                "title_fa": th_title_fa,
                "title_en": th_title_en,
                "theoretical_mechanism": mechanism,
                "hypothesized_path": hypothesized_path,
                "studies_count": total_th,
                "mean_sample_size": round(sum(theme_n_list) / len(theme_n_list), 1) if theme_n_list else 0,
                "concordance_verdict": concordance_verdict,
                "concordance_text_fa": concordance_text_fa,
                "direction_counts": theme_directions,
                "studies": theme_studies_processed,
                "synthesis_narrative": cls._generate_thematic_narrative(
                    th_title_fa, mechanism, hypothesized_path, theme_studies_processed, concordance_text_fa
                )
            })

        summary_metrics = {
            "total_studies_reviewed": total_studies,
            "total_sample_size": sum(all_sample_sizes),
            "mean_sample_size": round(sum(all_sample_sizes) / len(all_sample_sizes), 1) if all_sample_sizes else 0,
            "min_sample_size": min(all_sample_sizes) if all_sample_sizes else 0,
            "max_sample_size": max(all_sample_sizes) if all_sample_sizes else 0,
            "iranian_studies_count": region_counts["iranian"],
            "international_studies_count": region_counts["international"],
            "domestic_percentage": round((region_counts["iranian"] / total_studies) * 100, 1) if total_studies else 0.0,
            "design_distribution": design_counts,
            "direction_distribution": direction_counts,
            "themes_count": len(themes)
        }

        return {
            "contract_version": "1.0.0",
            "stage_id": "06_literature_matrix_table",
            "project_id": payload.get("project_id", "academic_project"),
            "topic_fa": payload.get("topic", ""),
            "topic_en": payload.get("topic_en", ""),
            "review_period": payload.get("review_period", "2021–2026"),
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "summary_metrics": summary_metrics,
            "analyzed_themes": analyzed_themes,
            "master_research_gaps": payload.get("master_research_gaps", cls._extract_master_gaps(analyzed_themes))
        }

    @staticmethod
    def _format_statistical_findings(stats: Dict[str, Any], raw_findings: str) -> str:
        """Formats statistical metrics into strict APA 7th Persian notation."""
        if not stats:
            return raw_findings or "یافته آماری ذکر نشده است."

        parts = []
        test_type = stats.get("test_type", "")
        test_stat = stats.get("test_statistic", "")
        if test_stat:
            parts.append(test_stat)
        elif test_type:
            parts.append(test_type)

        p_fa = stats.get("p_value_formatted_fa")
        if not p_fa and "p_value" in stats:
            pv = float(stats["p_value"])
            if pv < 0.001:
                p_fa = "۰.۰۰۱ > p"
            else:
                p_fa = f"p = {pv:.3f}".replace("0.", "۰.")
        if p_fa:
            parts.append(p_fa)

        es_val = stats.get("effect_size_value")
        es_type = stats.get("effect_size_type", "")
        if es_val is not None:
            es_name = {
                "partial_eta_squared": "η²p",
                "cohen_d": "d",
                "r": "r",
                "beta": "β",
                "r_squared": "R²"
            }.get(es_type, es_type or "ES")
            es_str = f"{es_name} = {es_val:.2f}".replace("0.", "۰.")
            parts.append(es_str)

        stat_summary = "، ".join(parts)
        if raw_findings:
            return f"{raw_findings} ({stat_summary})" if parts else raw_findings
        return stat_summary

    @staticmethod
    def _generate_thematic_narrative(
        theme_title: str,
        mechanism: str,
        path: str,
        studies: List[Dict[str, Any]],
        concordance_text: str
    ) -> str:
        """
        Synthesizes an authentic 5-part scholarly Persian narrative for the theme without clichés.
        Follows Saber's epistemic paragraph structure:
        1. Theoretical Premise
        2. Empirical Concordance & Pooled Evidence
        3. Discordance / Inconsistency Analysis
        4. Domestic vs International Nuances
        5. Epistemic Gap & Transition to Hypotheses
        """
        if not studies:
            return "پژوهش تجربی مستقیمی در این حوزه شناسایی نشد."

        cits_fa = [s.get("citation_fa", "") for s in studies if s.get("citation_fa")]
        cits_str = "، ".join(cits_fa[:4])
        if len(cits_fa) > 4:
            cits_str += f" و {len(cits_fa) - 4} مطالعه دیگر"

        # 1. Premise & Mechanism
        p1 = (
            f"بررسی پیشینه تجربی مرتبط با «{theme_title}» نشان می‌دهد که در چارچوب {mechanism}، "
            f"تبیین ارتباط میان متغیرهای مسیر ({path}) از کانون‌های توجه پژوهش‌های معاصر بوده است. "
            f"مطالعات تجربی واکاوی‌شده ({cits_str}) بر این فرض بنیادین متمرکز بوده‌اند که تغییرات در این سازه، "
            f"پیامدهای مستقیم و معناداری بر شاخص‌های عملکردی و روان‌شناختی جامعه هدف تحمیل می‌کند."
        )

        # 2. Concordance
        supporting_studies = [s for s in studies if "همسو" in s.get("direction_badge", "")]
        p2 = (
            f"از حیث همگرایی یافته‌ها، تحلیل پیشینه بیانگر {concordance_text} است؛ به‌گونه‌ای که "
            f"در {len(supporting_studies)} مورد از مجموع {len(studies)} پژوهش ارزیابی‌شده، جهت رابطه مفروض "
            f"در سطوح آماری معنادار (۰.۰۵ > p) به اثبات رسیده است."
        )

        # 3. Discordance & Methodological Factors
        conflicting = [s for s in studies if "ناهمسو" in s.get("direction_badge", "") or "فاقد" in s.get("direction_badge", "")]
        if conflicting:
            c_cits = "، ".join([c.get("citation_fa", "") for c in conflicting])
            p3 = (
                f"با وجود این همسویی غالب، یافته‌های گزارش‌شده در مطالعات {c_cits} نشان‌دهنده برخی ناهمخوانی‌هاست. "
                f"واکاوی روش‌شناختی این تفاوت‌ها حاکی از آن است که ناهمگونی در ابزارهای اندازه‌گیری، تفاوت‌های جمعیت‌شناختی "
                f"و عدم کنترل متغیرهای تعدیل‌کننده محیطی می‌تواند در ایجاد ضرایب ناهمسو یا ضعیف نقش داشته باشد."
            )
        else:
            p3 = (
                "همسویی بالای مطالعات مؤید پایایی و تکرارپذیری نیرومند این سازوکار تبیینی در بسترهای تجربی گوناگون است "
                "و فرضیه وجود رابطه قوی را در میان نمونه‌های متعدد تقویت می‌کند."
            )

        # 4. Domestic vs International
        iranian_studies = [s for s in studies if "داخلی" in s.get("region_badge", "")]
        foreign_studies = [s for s in studies if "بین‌المللی" in s.get("region_badge", "")]
        p4 = (
            f"مقایسه تطبیقی شواهد داخلی ({len(iranian_studies)} پژوهش) با دستاوردهای محققان بین‌المللی ({len(foreign_studies)} پژوهش) "
            f"نشان می‌دهد که الگوهای اصلی رابطه در هر دو بافت فرهنگی از همسویی معناداری برخوردار است؛ هرچند در مطالعات داخلی "
            f"به‌دلیل متغیرهای زمینه‌ای و ویژگی‌های شغلی-آموزشی ویژه، اندازه‌های اثر با نوسانات بومی همراه بوده است."
        )

        # 5. Gap & Hypothesis Grounding
        p5 = (
            "مجموع شواهد گردآوری‌شده، ضمن تأیید ضرورت بررسی همزمان این مسیر با متغیرهای میانجی، "
            "بر وجود شکاف پژوهشی در تبیین چندبعدی این پدیده تأکید ورزیده و زمینه استنادی لازم را برای تدوین فرضیات پژوهش حاضر فراهم می‌آورد."
        )

        return f"{p1} {p2} {p3} {p4} {p5}"

    @staticmethod
    def _extract_master_gaps(analyzed_themes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Synthesizes comprehensive research gaps from the thematic analysis."""
        gaps = []
        for idx, th in enumerate(analyzed_themes, 1):
            gaps.append({
                "gap_id": f"GAP-0{idx}",
                "theme_title": th.get("title_fa", ""),
                "theoretical_gap": f"فقدان الگوی تبیینی جامع برای مسیر {th.get('hypothesized_path', '')} با در نظر گرفتن متغیرهای واسطه‌ای",
                "methodological_gap": "غالب بودن طرح‌های مقطعی همبستگی و محدودیت در استنباط علّی بلندمدت در پژوهش‌های پیشین",
                "sampling_gap": "تمرکز عمده مطالعات بر نمونه‌های در دسترس و ضرورت آزمون مدل بر جامعه هدف با نمونه‌گیری احتمالی",
                "implication_for_current_thesis": "آزمون تجربی مستقیم مدل مفهومی فرضیات حاضر برای پوشش این کمبودها"
            })
        return gaps


# ==============================================================================
# OpenXML Word Table & Document Builder (Stage 2.6 Triad Deliverable)
# ==============================================================================

class OpenXmlMatrixDocxBuilder:
    """Builds 06_literature_matrix_table.docx conforming strictly to OpenXML typography."""

    @classmethod
    def build_docx(cls, analysis_data: Dict[str, Any], output_filepath: str) -> None:
        """Assembles the complete institutional Word document."""
        if not HAS_DOCX:
            raise RuntimeError("python-docx is not installed in the environment.")

        doc = docx.Document()

        # Page Setup: A4, 1-inch margins
        for section in doc.sections:
            section.page_width = Inches(8.27)
            section.page_height = Inches(11.69)
            section.top_margin = Inches(1.0)
            section.bottom_margin = Inches(1.0)
            section.left_margin = Inches(1.0)
            section.right_margin = Inches(1.0)

            # Enforce Section-Level BiDi
            sectPr = section._sectPr
            if sectPr.find(qn("w:bidi")) is None:
                sectPr.append(parse_xml(f'<w:bidi {nsdecls("w")}/>'))

        # 1. Main Heading (B Titr 15pt, RTL Right-aligned, omit w:jc)
        h1 = doc.add_paragraph()
        set_p_bidi(h1, is_right_heading=True, space_before=12, space_after=8)
        r_h1 = h1.add_run("۲-۳-۳. جدول خلاصه و ماتریس تحلیلی پیشینه پژوهش‌های تجربی (APA 7)")
        set_run_font(r_h1, font_name="B Titr", size_pt=15, bold=True)

        # 2. Executive Synthesis Overview (Justified continuous narrative)
        metrics = analysis_data.get("summary_metrics", {})
        topic_fa = analysis_data.get("topic_fa", "")
        p_intro = doc.add_paragraph()
        set_p_bidi(p_intro, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=4, space_after=8)
        intro_text = (
            f"به‌منظور سازمان‌دهی روش‌مند و فراهم آوردن نگاهی جامع و تطبیقی به پیشینه تجربی معاصر ({analysis_data.get('review_period', '۲۰۲۱–۲۰۲۶')}) "
            f"در ارتباط با موضوع «{topic_fa}»، مجموعاً {metrics.get('total_studies_reviewed', 0)} مطالعه معتبر تجربی "
            f"شامل {metrics.get('iranian_studies_count', 0)} پژوهش داخلی و {metrics.get('international_studies_count', 0)} پژوهش بین‌المللی "
            f"با مجموع حجم نمونه {metrics.get('total_sample_size', 0)} نفر (میانگین N = {metrics.get('mean_sample_size', 0)}) "
            f"مورد تحلیل و سنتز تماتیک قرار گرفت. ساختار این واکاوی، مطالعات را ذیل محورها و سازوکارهای نظری فرضیات پژوهش دسته‌بندی نموده "
            f"و ویژگی‌های کلیدی جامعه، ابزارها، طرح تحقیق و ضرایب اثر را به تفکیک ارائه داده است."
        )
        r_intro = p_intro.add_run(intro_text)
        set_run_font(r_intro, font_name="B Nazanin", size_pt=13)

        # 3. Iterate through Themes: Narrative followed by Table
        themes = analysis_data.get("analyzed_themes", [])
        for t_idx, th in enumerate(themes, 1):
            # Theme Sub-heading (B Titr 13pt Bold)
            h_th = doc.add_paragraph()
            set_p_bidi(h_th, is_right_heading=True, space_before=14, space_after=4)
            r_th = h_th.add_run(f"محور تماتیک {t_idx}: {th.get('title_fa', '')}")
            set_run_font(r_th, font_name="B Titr", size_pt=13, bold=True)

            # Thematic Narrative (B Nazanin 13pt Regular, Justified)
            p_narr = doc.add_paragraph()
            set_p_bidi(p_narr, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=2, space_after=6)
            r_narr = p_narr.add_run(th.get("synthesis_narrative", ""))
            set_run_font(r_narr, font_name="B Nazanin", size_pt=13)

            # Table Caption Precedes Table: B Nazanin 12pt Non-bold (OpenXML standard)
            p_cap = doc.add_paragraph()
            set_p_bidi(p_cap, is_right_heading=True, space_before=6, space_after=4)
            r_cap = p_cap.add_run(f"جدول ۲-{t_idx}: ماتریس سنتز شواهد تجربی برای {th.get('title_fa', '')}")
            set_run_font(r_cap, font_name="B Nazanin", size_pt=12, bold=False)

            # Generate APA 7 Table
            cls._create_theme_table(doc, th.get("studies", []))

            # Table Note
            p_note = doc.add_paragraph()
            set_p_bidi(p_note, is_right_heading=True, space_before=3, space_after=12)
            r_note_lbl = p_note.add_run("یادداشت: ")
            set_run_font(r_note_lbl, font_name="B Nazanin", size_pt=10, bold=True)
            r_note_txt = p_note.add_run("N: حجم نمونه؛ SEM: مدل‌سازی معادلات ساختاری؛ RCT: کارآزمایی بالینی تصادفی؛ ضرایب اثر با دو رقم اعشار و مقادیر p با سه رقم اعشار گزارش شده‌اند.")
            set_run_font(r_note_txt, font_name="B Nazanin", size_pt=10)

        # 4. Master Research Gaps Section
        h_gaps = doc.add_paragraph()
        set_p_bidi(h_gaps, is_right_heading=True, space_before=16, space_after=6)
        r_hgaps = h_gaps.add_run("۲-۴. جمع‌بندی سنتز پیشینه و شکاف‌های پژوهشی شناسایی‌شده (Research Gaps)")
        set_run_font(r_hgaps, font_name="B Titr", size_pt=14, bold=True)

        gaps = analysis_data.get("master_research_gaps", [])
        for g_idx, gap in enumerate(gaps, 1):
            p_gap = doc.add_paragraph()
            set_p_bidi(p_gap, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=3, space_after=4)
            r_gap_title = p_gap.add_run(f"شکاف {g_idx} ({gap.get('theme_title', '')}): ")
            set_run_font(r_gap_title, font_name="B Nazanin", size_pt=13, bold=True)
            gap_desc = (
                f"{gap.get('theoretical_gap', '')}. از بعد روش‌شناختی، {gap.get('methodological_gap', '')} "
                f"و در زمینه نمونه‌گیری، {gap.get('sampling_gap', '')}. {gap.get('implication_for_current_thesis', '')}."
            )
            r_gap_desc = p_gap.add_run(gap_desc)
            set_run_font(r_gap_desc, font_name="B Nazanin", size_pt=13)

        doc.save(output_filepath)

    @classmethod
    def _create_theme_table(cls, doc: docx.Document, studies: List[Dict[str, Any]]) -> None:
        """Creates an APA 7 table with BiDi Visual, 3 horizontal borders, and decoupled stats."""
        headers = [
            ("ردیف", 0.6),
            ("پژوهشگر(ان) و سال", 2.2),
            ("جامعه و نمونه (N)", 1.8),
            ("طرح پژوهش", 1.8),
            ("ابزارهای سنجش", 2.0),
            ("یافته‌های آماری کلیدی", 3.0),
            ("جهت اثر", 1.2)
        ]

        table = doc.add_table(rows=len(studies) + 1, cols=len(headers))
        set_table_apa7_borders_and_bidi(table)

        # Header Row
        hdr_row = table.rows[0]
        tblHeader = parse_xml(f'<w:tblHeader {nsdecls("w")}/>')
        hdr_row._tr.get_or_add_trPr().append(tblHeader)

        for col_idx, (hdr_text, col_width) in enumerate(headers):
            cell = hdr_row.cells[col_idx]
            cell.width = Inches(col_width)
            p = cell.paragraphs[0]
            set_p_bidi(p, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=3, space_after=3)
            run = p.add_run(hdr_text)
            set_run_font(run, font_name="B Nazanin", size_pt=11, bold=True)

        # Data Rows
        for r_idx, s in enumerate(studies, 1):
            row = table.rows[r_idx]
            tools_list = s.get("instruments", [])
            tools_str = "، ".join([t.get("name", "") for t in tools_list if t.get("name")]) or s.get("iv", "")

            # Row Data Mapping
            row_data = [
                (str(r_idx), WD_ALIGN_PARAGRAPH.CENTER, False),
                (s.get("citation_fa", ""), WD_ALIGN_PARAGRAPH.RIGHT, False),
                (f"{s.get('population', '')} (N = {s.get('sample_size', '')})", WD_ALIGN_PARAGRAPH.JUSTIFY, False),
                (s.get("design_badge_fa", ""), WD_ALIGN_PARAGRAPH.RIGHT, False),
                (tools_str, WD_ALIGN_PARAGRAPH.JUSTIFY, False),
                (s.get("formatted_stats_fa", ""), WD_ALIGN_PARAGRAPH.JUSTIFY, False),
                (s.get("direction_badge", ""), WD_ALIGN_PARAGRAPH.CENTER, True)
            ]

            for col_idx, (val, cell_align, is_badge) in enumerate(row_data):
                cell = row.cells[col_idx]
                cell.width = Inches(headers[col_idx][1])
                p = cell.paragraphs[0]
                set_p_bidi(p, align=cell_align, space_before=2, space_after=2)
                run = p.add_run(val)
                set_run_font(run, font_name="B Nazanin", size_pt=10.5, bold=is_badge)


# ==============================================================================
# Multi-Sheet Excel Workbook Builder (openpyxl)
# ==============================================================================

class ExcelMatrixWorkbookBuilder:
    """Generates Literature_Synthesis_Matrix.xlsx across 4 professional academic sheets."""

    @classmethod
    def build_workbook(cls, analysis_data: Dict[str, Any], output_filepath: str) -> None:
        """Assembles the Excel workbook with Navy/Gold academic styling."""
        if not HAS_OPENPYXL:
            raise RuntimeError("openpyxl is not installed in the environment.")

        wb = openpyxl.Workbook()

        # Styles
        header_fill = PatternFill(start_color="1B365D", end_color="1B365D", fill_type="solid")  # Navy
        header_font = Font(name="B Nazanin", size=11, bold=True, color="FFFFFF")
        title_font = Font(name="B Titr", size=14, bold=True, color="1B365D")
        sub_font = Font(name="B Nazanin", size=11, bold=True, color="333333")
        regular_font = Font(name="B Nazanin", size=10, bold=False, color="000000")
        accent_fill = PatternFill(start_color="F2F5F9", end_color="F2F5F9", fill_type="solid")

        thin_side = Side(border_style="thin", color="D0D7DE")
        thin_border = Border(top=thin_side, bottom=thin_side, left=thin_side, right=thin_side)

        center_align = Alignment(horizontal="center", vertical="center", wrap_text=True)
        right_align = Alignment(horizontal="right", vertical="center", wrap_text=True)
        left_align = Alignment(horizontal="left", vertical="center", wrap_text=True)

        # ---------------------------------------------------------------------
        # Sheet 1: Synthesis Overview
        # ---------------------------------------------------------------------
        ws1 = wb.active
        ws1.title = "Overview & Metrics"
        ws1.views.sheetView[0].rightToLeft = True

        ws1.cell(row=1, column=1, value="شناسنامه و شاخص‌های آماری ماتریس سنتز پیشینه پژوهش").font = title_font
        ws1.cell(row=2, column=1, value=f"موضوع: {analysis_data.get('topic_fa', '')}").font = sub_font
        ws1.cell(row=3, column=1, value=f"افق زمانی بررسی: {analysis_data.get('review_period', '2021-2026')} | تاریخ تولید: {analysis_data.get('generated_at', '')[:10]}").font = regular_font

        metrics = analysis_data.get("summary_metrics", {})
        metric_rows = [
            ("کل مقالات و پژوهش‌های تجربی واکاوی‌شده", metrics.get("total_studies_reviewed", 0)),
            ("مجموع حجم نمونه در مطالعات ارزیابی‌شده (Total N)", metrics.get("total_sample_size", 0)),
            ("میانگین حجم نمونه هر مطالعه (Mean N)", metrics.get("mean_sample_size", 0)),
            ("دامنه حجم نمونه (Min - Max N)", f"{metrics.get('min_sample_size', 0)} - {metrics.get('max_sample_size', 0)}"),
            ("تعداد پژوهش‌های داخلی (ایران)", metrics.get("iranian_studies_count", 0)),
            ("تعداد پژوهش‌های بین‌المللی", metrics.get("international_studies_count", 0)),
            ("نسبت مطالعات داخلی به کل پیشینه (%)", f"{metrics.get('domestic_percentage', 0)}%"),
            ("تعداد محورهای تماتیک استخراج‌شده", metrics.get("themes_count", 0))
        ]

        ws1.cell(row=5, column=1, value="شاخص آماری").font = header_font
        ws1.cell(row=5, column=1).fill = header_fill
        ws1.cell(row=5, column=1).alignment = right_align

        ws1.cell(row=5, column=2, value="مقدار محاسبه‌شده").font = header_font
        ws1.cell(row=5, column=2).fill = header_fill
        ws1.cell(row=5, column=2).alignment = center_align

        for r_idx, (lbl, val) in enumerate(metric_rows, 6):
            c1 = ws1.cell(row=r_idx, column=1, value=lbl)
            c2 = ws1.cell(row=r_idx, column=2, value=val)
            c1.font = sub_font
            c2.font = regular_font
            c1.border = thin_border
            c2.border = thin_border
            c1.alignment = right_align
            c2.alignment = center_align
            if r_idx % 2 == 0:
                c1.fill = accent_fill
                c2.fill = accent_fill

        ws1.column_dimensions["A"].width = 45
        ws1.column_dimensions["B"].width = 25

        # ---------------------------------------------------------------------
        # Sheet 2: Thematic Synthesis Matrix
        # ---------------------------------------------------------------------
        ws2 = wb.create_sheet(title="Thematic Matrix")
        ws2.views.sheetView[0].rightToLeft = True

        th_headers = [
            "کد تم",
            "عنوان محور تماتیک",
            "سازوکار نظری تبیین‌کننده",
            "مسیر مفروض رابطه",
            "تعداد پژوهش‌ها",
            "میانگین N",
            "وضعیت همگرایی شواهد (Concordance)"
        ]
        for c_idx, th_h in enumerate(th_headers, 1):
            cell = ws2.cell(row=1, column=c_idx, value=th_h)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center_align
            cell.border = thin_border

        for r_idx, th in enumerate(analysis_data.get("analyzed_themes", []), 2):
            vals = [
                th.get("theme_id", ""),
                th.get("title_fa", ""),
                th.get("theoretical_mechanism", ""),
                th.get("hypothesized_path", ""),
                th.get("studies_count", 0),
                th.get("mean_sample_size", 0),
                th.get("concordance_text_fa", "")
            ]
            for c_idx, v in enumerate(vals, 1):
                c = ws2.cell(row=r_idx, column=c_idx, value=v)
                c.font = regular_font
                c.border = thin_border
                c.alignment = center_align if c_idx in [1, 5, 6, 7] else right_align
                if r_idx % 2 == 1:
                    c.fill = accent_fill

        cls._auto_adjust_col_widths(ws2)

        # ---------------------------------------------------------------------
        # Sheet 3: Empirical Parameters Detail
        # ---------------------------------------------------------------------
        ws3 = wb.create_sheet(title="Empirical Studies Detail")
        ws3.views.sheetView[0].rightToLeft = True

        param_headers = [
            "ردیف",
            "محور تماتیک",
            "پژوهشگر(ان) و سال",
            "DOI / منبع",
            "منطقه",
            "جامعه آماری",
            "حجم نمونه (N)",
            "طرح پژوهش",
            "متغیر مستقل (IV)",
            "متغیر وابسته (DV)",
            "ابزار سنجش",
            "آزمون آماری",
            "شاخص آماری",
            "مقدار p",
            "اندازه اثر (Effect Size)",
            "جهت یافته"
        ]
        for c_idx, ph in enumerate(param_headers, 1):
            cell = ws3.cell(row=1, column=c_idx, value=ph)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center_align
            cell.border = thin_border

        row_counter = 2
        global_row = 1
        for th in analysis_data.get("analyzed_themes", []):
            th_title = th.get("title_fa", "")
            for s in th.get("studies", []):
                stats = s.get("statistical_results", {})
                instruments = "، ".join([i.get("name", "") for i in s.get("instruments", []) if i.get("name")])
                p_val_str = stats.get("p_value_formatted_fa") or str(stats.get("p_value", ""))
                es_val_str = f"{stats.get('effect_size_type', '')}: {stats.get('effect_size_value', '')}" if "effect_size_value" in stats else ""

                s_vals = [
                    global_row,
                    th_title,
                    s.get("citation_fa", ""),
                    s.get("doi", ""),
                    s.get("region_badge", ""),
                    s.get("population", ""),
                    s.get("sample_size", ""),
                    s.get("design_badge_fa", ""),
                    s.get("iv", ""),
                    s.get("dv", ""),
                    instruments,
                    stats.get("test_type", ""),
                    stats.get("test_statistic", ""),
                    p_val_str,
                    es_val_str,
                    s.get("direction_badge", "")
                ]

                for c_idx, val in enumerate(s_vals, 1):
                    c = ws3.cell(row=row_counter, column=c_idx, value=val)
                    c.font = regular_font
                    c.border = thin_border
                    c.alignment = center_align if c_idx in [1, 5, 7, 12, 13, 14, 15, 16] else right_align
                    if row_counter % 2 == 1:
                        c.fill = accent_fill

                row_counter += 1
                global_row += 1

        cls._auto_adjust_col_widths(ws3)

        # ---------------------------------------------------------------------
        # Sheet 4: Methodological Critique & Gaps
        # ---------------------------------------------------------------------
        ws4 = wb.create_sheet(title="Research Gaps & Critique")
        ws4.views.sheetView[0].rightToLeft = True

        gap_headers = [
            "کد شکاف",
            "محور تماتیک مربوطه",
            "شکاف نظری (Theoretical Gap)",
            "شکاف روش‌شناختی (Methodological Gap)",
            "شکاف نمونه‌گیری و جامعه (Sampling Gap)",
            "دلالت برای فرضیات پژوهش حاضر"
        ]
        for c_idx, gh in enumerate(gap_headers, 1):
            cell = ws4.cell(row=1, column=c_idx, value=gh)
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center_align
            cell.border = thin_border

        for r_idx, gap in enumerate(analysis_data.get("master_research_gaps", []), 2):
            g_vals = [
                gap.get("gap_id", ""),
                gap.get("theme_title", ""),
                gap.get("theoretical_gap", ""),
                gap.get("methodological_gap", ""),
                gap.get("sampling_gap", ""),
                gap.get("implication_for_current_thesis", "")
            ]
            for c_idx, val in enumerate(g_vals, 1):
                c = ws4.cell(row=r_idx, column=c_idx, value=val)
                c.font = regular_font
                c.border = thin_border
                c.alignment = center_align if c_idx == 1 else right_align
                if r_idx % 2 == 1:
                    c.fill = accent_fill

        cls._auto_adjust_col_widths(ws4)

        wb.save(output_filepath)

    @staticmethod
    def _auto_adjust_col_widths(ws):
        """Automatically scales Excel column widths based on cell text lengths."""
        for col in ws.columns:
            max_len = 0
            col_letter = get_column_letter(col[0].column)
            for cell in col:
                val_str = str(cell.value or "")
                # Persian characters count roughly double byte width
                val_len = len(val_str)
                if val_len > max_len:
                    max_len = val_len
            ws.column_dimensions[col_letter].width = min(50, max(12, max_len + 3))


# ==============================================================================
# Markdown Triad Deliverable Builder
# ==============================================================================

class MarkdownMatrixBuilder:
    """Builds 06_literature_matrix_table.md conforming to Stage 2.6 Triad Invariant."""

    @classmethod
    def build_markdown(cls, analysis_data: Dict[str, Any], output_filepath: str) -> None:
        """Generates scholarly Markdown document with tables and narrative."""
        metrics = analysis_data.get("summary_metrics", {})
        topic_fa = analysis_data.get("topic_fa", "")
        review_period = analysis_data.get("review_period", "2021–2026")

        lines = [
            f"# ۲-۳-۳. ماتریس سنتز و جدول جامع پیشینه پژوهش‌های تجربی (Stage 2.6)",
            f"",
            f"> **موضوع پژوهش**: {topic_fa}  ",
            f"> **افق زمانی پیشینه**: {review_period} | **تعداد مطالعات**: {metrics.get('total_studies_reviewed', 0)} ({metrics.get('iranian_studies_count', 0)} داخلی، {metrics.get('international_studies_count', 0)} بین‌المللی) | **مجموع حجم نمونه**: N = {metrics.get('total_sample_size', 0)}",
            f"",
            f"---",
            f"",
            f"## ۱. مرور کلی و شاخص‌های آماری پیشینه واکاوی‌شده",
            f"",
            f"به‌منظور سازمان‌دهی روش‌مند پیشینه تجربی، کلیه پژوهش‌های واکاوی‌شده ذیل محورهای تماتیک و سازوکارهای نظری مستخرج از فرضیات پژوهش دسته‌بندی گردیده‌اند. میانگین حجم نمونه مطالعات ارزیابی‌شده معادل {metrics.get('mean_sample_size', 0)} نفر و دامنه آن از {metrics.get('min_sample_size', 0)} تا {metrics.get('max_sample_size', 0)} شرکت‌کننده متغیر بوده است. {metrics.get('domestic_percentage', 0)} درصد مطالعات را پژوهش‌های داخلی تشکیل می‌دهند که امکان بررسی ویژگی‌های بافت‌محور جامعه هدف را فراهم می‌سازد.",
            f"",
            f"---",
            f""
        ]

        themes = analysis_data.get("analyzed_themes", [])
        for t_idx, th in enumerate(themes, 1):
            lines.extend([
                f"## ۲.{t_idx}. محور تماتیک {t_idx} ({th.get('theme_id', '')}): {th.get('title_fa', '')}",
                f"",
                f"**سازوکار نظری**: {th.get('theoretical_mechanism', '')} | **مسیر مفروض**: `{th.get('hypothesized_path', '')}`  ",
                f"**وضعیت همگرایی شواهد**: {th.get('concordance_text_fa', '')}",
                f"",
                f"### روایت سنتز تماتیک:",
                f"",
                f"{th.get('synthesis_narrative', '')}",
                f"",
                f"#### جدول ۲-{t_idx}: خلاصه شواهد تجربی برای {th.get('title_fa', '')}",
                f"",
                f"| ردیف | پژوهشگر(ان) و سال | جامعه و نمونه (N) | طرح پژوهش | ابزارهای سنجش | یافته‌های آماری کلیدی | جهت اثر |",
                f"| :---: | :--- | :--- | :--- | :--- | :--- | :---: |"
            ])

            for s in th.get("studies", []):
                tools = "، ".join([i.get("name", "") for i in s.get("instruments", []) if i.get("name")]) or s.get("iv", "")
                row = (
                    f"| {s.get('row_num', '')} "
                    f"| {s.get('citation_fa', '')} "
                    f"| {s.get('population', '')} (N = {s.get('sample_size', '')}) "
                    f"| {s.get('design_badge_fa', '')} "
                    f"| {tools} "
                    f"| {s.get('formatted_stats_fa', '')} "
                    f"| **{s.get('direction_badge', '')}** |"
                )
                lines.append(row)

            lines.extend([
                f"",
                f"> *یادداشت جدول*: N: حجم نمونه؛ مقادیر آماری بر اساس استاندارد APA 7th با حفظ صفر قبل از ممیز در زبان فارسی درج گردیده‌اند.",
                f"",
                f"---",
                f""
            ])

        # Research Gaps Section
        lines.extend([
            f"## ۳. سنتز نهایی و شکاف‌های پژوهشی شناسایی‌شده (Research Gaps)",
            f"",
            f"بررسی یکپارچه ماتریس پیشینه تجربی، وجود شکاف‌های مطالعاتی زیر را آشکار می‌سازد که توجیه‌کننده ضرورت انجام پژوهش حاضر است:",
            f""
        ])

        for g_idx, gap in enumerate(analysis_data.get("master_research_gaps", []), 1):
            gap_code = gap.get("gap_id", f"GAP-0{g_idx}")
            lines.extend([
                f"### شکاف ۳.{g_idx} ({gap_code}): {gap.get('theme_title', '')}",
                f"- **شکاف نظری**: {gap.get('theoretical_gap', '')}",
                f"- **شکاف روش‌شناختی**: {gap.get('methodological_gap', '')}",
                f"- **شکاف جامعه و نمونه**: {gap.get('sampling_gap', '')}",
                f"- **دلالت بر فرضیات رساله**: {gap.get('implication_for_current_thesis', '')}",
                f""
            ])

        with open(output_filepath, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))


# ==============================================================================
# Master Synthesis Matrix Engine Runner
# ==============================================================================

class LiteratureSynthesisMatrixEngine:
    """Master engine orchestrating analysis, OpenXML Word, Markdown, JSON, and Excel export."""

    @classmethod
    def process_and_export(
        cls,
        payload: Dict[str, Any],
        out_dir: str,
        lang: str = "fa"
    ) -> Dict[str, str]:
        """
        Processes the input literature payload and generates the synchronized quad deliverables:
        1. 06_literature_matrix_table.docx
        2. 06_literature_matrix_table.md
        3. 06_literature_matrix_table.json
        4. Literature_Synthesis_Matrix.xlsx
        """
        out_dir = os.path.abspath(out_dir)
        os.makedirs(out_dir, exist_ok=True)

        # 1. Statistical & Thematic Analysis
        analysis_data = ThematicClusteringEngine.analyze_payload(payload)

        # 2. Triad JSON Artifact
        json_path = os.path.join(out_dir, "06_literature_matrix_table.json")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)

        # 3. Triad Markdown Artifact
        md_path = os.path.join(out_dir, "06_literature_matrix_table.md")
        MarkdownMatrixBuilder.build_markdown(analysis_data, md_path)

        # 4. Triad Word Document (.docx)
        docx_path = os.path.join(out_dir, "06_literature_matrix_table.docx")
        OpenXmlMatrixDocxBuilder.build_docx(analysis_data, docx_path)

        # 5. Multi-sheet Excel Workbook (.xlsx)
        xlsx_path = os.path.join(out_dir, "Literature_Synthesis_Matrix.xlsx")
        ExcelMatrixWorkbookBuilder.build_workbook(analysis_data, xlsx_path)

        return {
            "json": json_path,
            "md": md_path,
            "docx": docx_path,
            "xlsx": xlsx_path
        }


def main():
    parser = argparse.ArgumentParser(description="Chapter 2 Literature Review Thematic Synthesis Matrix Engine")
    parser.add_argument("--json", type=str, help="Path to input literature payload JSON file")
    parser.add_argument("--out-dir", type=str, default="./06_literature_matrix", help="Output directory for triad artifacts")
    parser.add_argument("--lang", type=str, default="fa", choices=["fa", "en"], help="Primary language (default: fa)")
    parser.add_argument("--generate-sample", action="store_true", help="Generate a sample payload and execute demo build")

    args = parser.parse_args()

    if args.generate_sample:
        from sample_synthesis_matrix_payload import get_sample_payload
        payload = get_sample_payload()
    elif args.json:
        with open(args.json, "r", encoding="utf-8") as f:
            payload = json.load(f)
    else:
        sys.stderr.write("Error: Please provide --json <path> or use --generate-sample\n")
        sys.exit(1)

    artifacts = LiteratureSynthesisMatrixEngine.process_and_export(
        payload=payload,
        out_dir=args.out_dir,
        lang=args.lang
    )

    print("[SUCCESS] Stage 2.6 Literature Review Synthesis Matrix Triad generated successfully:")
    for k, p in artifacts.items():
        print(f"  - [{k.upper()}]: {p}")


if __name__ == "__main__":
    main()
