#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit_engine.py — Academic Thesis & Dissertation Integrity Auditor Engine (Skill #20)
======================================================================================
Automated forensic academic proofreader and cross-chapter consistency verification engine
for graduate theses and dissertations in Psychology, Counseling, and Behavioral Sciences.

Audits:
  1. Hypothesis-Result-Discussion Alignment (Ch 1 Formulation <-> Ch 4 Stats <-> Ch 5 Discussion)
  2. Methodology-Statistics Numerical Consistency (Sample N, groups, degrees of freedom df)
  3. Bidirectional Citation Reconciliation (Orphaned in-text citations vs Ghost bibliography)
  4. APA 7th Edition Statistical Typography Compliance (Leading zeroes, p = .000, effect sizes)

Outputs:
  - گزارش_جامع_ممیزی_و_صحت‌سنجی_رساله.docx (or Thesis_Integrity_Audit_Report.docx)
  - annotated_citations.xlsx (5-sheet comprehensive citation ledger)
  - thesis_audit_summary.json (Machine-readable audit findings)
"""

import os
import sys
import json
import re
import argparse
from datetime import datetime
from difflib import SequenceMatcher

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

# ==============================================================================
# OpenXML BiDi & Typography Helpers
# ==============================================================================

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_shading(cell, color_hex):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{color_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def make_table_apa7(table, is_bidi=True):
    tblPr = table._tbl.tblPr
    if is_bidi:
        bidi_visual = parse_xml(f'<w:bidiVisual {nsdecls("w")}/>')
        tblPr.append(bidi_visual)
    
    table_borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="single" w:sz="6" w:space="0" w:color="2B3A4A"/>'
        f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="2B3A4A"/>'
        f'  <w:left w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'  <w:insideH w:val="single" w:sz="4" w:space="0" w:color="D3D3D3"/>'
        f'  <w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(table_borders)

def format_cell_text(cell, text, bold=False, italic=False, size_pt=10, color_rgb=(40,40,40),
                     align=WD_ALIGN_PARAGRAPH.CENTER, font_fa="B Nazanin", font_en="Times New Roman", is_bidi=True):
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = align
    if is_bidi:
        pPr = p._element.get_or_add_pPr()
        pPr.append(parse_xml(f'<w:bidi {nsdecls("w")} w:val="1"/>'))
    
    run = p.add_run(str(text))
    run.font.name = font_en
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = RGBColor(*color_rgb)
    rPr = run._element.get_or_add_rPr()
    rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="{font_en}" w:hAnsi="{font_en}" w:cs="{font_fa}"/>')
    rPr.append(rFonts)

def add_styled_paragraph(doc, text, bold=False, italic=False, size_pt=12, color_rgb=(30,30,30),
                         align=WD_ALIGN_PARAGRAPH.RIGHT, space_after=6, line_spacing=1.15,
                         font_fa="B Nazanin", font_en="Times New Roman", is_bidi=True):
    p = doc.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = line_spacing
    if is_bidi:
        pPr = p._element.get_or_add_pPr()
        pPr.append(parse_xml(f'<w:bidi {nsdecls("w")} w:val="1"/>'))
    
    run = p.add_run(text)
    run.font.name = font_en
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = RGBColor(*color_rgb)
    rPr = run._element.get_or_add_rPr()
    rFonts = parse_xml(f'<w:rFonts {nsdecls("w")} w:ascii="{font_en}" w:hAnsi="{font_en}" w:cs="{font_fa}"/>')
    rPr.append(rFonts)
    return p

# ==============================================================================
# EQUATOR Network Reporting Checklists (CONSORT 2010, STROBE, PRISMA 2020)
# ==============================================================================

CONSORT_CHECKLIST = [
    {"id": "1a", "name_en": "Title identifying study as randomized trial", "name_fa": "عنوان مشخص‌کننده کارآزمایی تصادفی‌سازی‌شده", "criticality": "MAJOR"},
    {"id": "1b", "name_en": "Structured summary abstract (design, methods, results, conclusion)", "name_fa": "چکیده ساختاریافته (طرح، روش، یافته‌ها، نتیجه‌گیری)", "criticality": "MAJOR"},
    {"id": "2a", "name_en": "Scientific background and rationale", "name_fa": "مبانی نظری، پیشینه و ضرورت پژوهش", "criticality": "MAJOR"},
    {"id": "2b", "name_en": "Specific objectives or directional hypotheses", "name_fa": "اهداف اختصاصی یا فرضیه‌های جهت‌دار پژوهش", "criticality": "MAJOR"},
    {"id": "3a", "name_en": "Trial design (parallel, factorial, allocation ratio)", "name_fa": "شرح طرح کارآزمایی بالینی و نسبت تخصیص گروه‌ها", "criticality": "MAJOR"},
    {"id": "4a", "name_en": "Eligibility criteria for participants", "name_fa": "معیارهای ورود و خروج شرکت‌کنندگان", "criticality": "MAJOR"},
    {"id": "4b", "name_en": "Settings and locations where data were collected", "name_fa": "مکان، جامعه بالینی و بستر گردآوری داده‌ها", "criticality": "MINOR"},
    {"id": "5", "name_en": "Interventions in detail for each group (sessions, protocol)", "name_fa": "شرح تفصیلی پروتکل مداخله و جلسات آموزشی/درمانی", "criticality": "CRITICAL"},
    {"id": "6a", "name_en": "Completely defined primary and secondary outcomes", "name_fa": "تعریف دقیق پیامدهای اولیه و ثانویه", "criticality": "MAJOR"},
    {"id": "7a", "name_en": "Sample size determination & G*Power power analysis", "name_fa": "تعیین حجم نمونه و توجیه توان آماری با G*Power", "criticality": "CRITICAL"},
    {"id": "8a", "name_en": "Method used to generate random allocation sequence", "name_fa": "روش تولید توالی تخصیص تصادفی", "criticality": "MAJOR"},
    {"id": "9", "name_en": "Allocation concealment mechanism", "name_fa": "سازوکار پنهان‌سازی تخصیص (Allocation Concealment)", "criticality": "MAJOR"},
    {"id": "11a", "name_en": "Blinding/masking procedures (single/double blind)", "name_fa": "روش‌های کوربخش‌سازی یا دلایل عدم امکان آن", "criticality": "MINOR"},
    {"id": "12a", "name_en": "Statistical methods used to compare groups (ANCOVA/RM-ANOVA)", "name_fa": "روش‌های آماری مقایسه گروه‌ها و کنترل پیش‌آزمون", "criticality": "CRITICAL"},
    {"id": "13a", "name_en": "Participant flow diagram (CONSORT Flowchart)", "name_fa": "نمودار جریان شرکت‌کنندگان (CONSORT Flowchart)", "criticality": "MAJOR"},
    {"id": "13b", "name_en": "Losses and exclusions after randomization (dropouts)", "name_fa": "مستندسازی ریزش، غیبت و حذف آزمودنی‌ها", "criticality": "MAJOR"},
    {"id": "15", "name_en": "Baseline demographic and clinical characteristics table", "name_fa": "جدول ویژگی‌های جمعیت‌شناختی و بالینی خط پایه", "criticality": "MAJOR"},
    {"id": "16", "name_en": "Numbers analysed in each group (ITT or per-protocol)", "name_fa": "تعداد تحلیل‌شده‌ها در هر گروه (قصد درمان / پروتکل)", "criticality": "MAJOR"},
    {"id": "17a", "name_en": "Outcomes and estimation with effect sizes and 95% CI", "name_fa": "گزارش پیامدها با اندازه اثر (eta_p^2 / d) و فواصل اطمینان", "criticality": "CRITICAL"},
    {"id": "18", "name_en": "Ancillary analyses (assumptions, subgroup adjustments)", "name_fa": "تحلیل‌های فرعی و آزمون‌های پیش‌فرض (لون، نرمالیتی)", "criticality": "MAJOR"},
    {"id": "19", "name_en": "Harms and adverse events reported", "name_fa": "بررسی و گزارش عدم رخداد عوارض جانبی یا آسیب‌های ناخواسته", "criticality": "MINOR"},
    {"id": "20", "name_en": "Trial limitations addressing sources of potential bias", "name_fa": "محدودیت‌های پژوهش و منابع احتمالی سوگیری", "criticality": "MAJOR"},
    {"id": "21", "name_en": "Generalisability (external validity) of the findings", "name_fa": "قابلیت تعمیم‌پذیری یافته‌ها به جامعه هدف", "criticality": "MINOR"},
    {"id": "22", "name_en": "Interpretation consistent with results and clinical evidence", "name_fa": "تفسیر نتایج، تبیین روان‌شناختی و دلالت‌های بالینی", "criticality": "MAJOR"},
    {"id": "23", "name_en": "Registration number and name of trial registry (IRCT / ClinicalTrials)", "name_fa": "کد ثبت کارآزمایی بالینی (سامانه IRCT یا معادل بین‌المللی)", "criticality": "MAJOR"}
]

STROBE_CHECKLIST = [
    {"id": "1", "name_en": "Title and abstract indicating observational study design", "name_fa": "عنوان و چکیده نشان‌دهنده طرح مشاهده‌ای/همبستگی", "criticality": "MAJOR"},
    {"id": "2", "name_en": "Background and scientific rationale", "name_fa": "مبانی نظری و ضرورت پژوهش", "criticality": "MAJOR"},
    {"id": "3", "name_en": "Specific objectives and hypotheses", "name_fa": "اهداف اختصاصی و فرضیه‌های پژوهش", "criticality": "MAJOR"},
    {"id": "4", "name_en": "Key elements of study design", "name_fa": "طرح پژوهش (مقطعی، همبستگی، علّی-مقایسه‌ای)", "criticality": "MAJOR"},
    {"id": "5", "name_en": "Setting, locations, and data collection dates", "name_fa": "مکان، جامعه هدف و بازه زمانی گردآوری داده‌ها", "criticality": "MINOR"},
    {"id": "6", "name_en": "Participants eligibility criteria & sampling strategy", "name_fa": "معیارهای ورود/خروج و شیوه نمونه‌گیری", "criticality": "MAJOR"},
    {"id": "7", "name_en": "Clearly defined variables (predictors, outcomes, covariates)", "name_fa": "تعریف متغیرهای پیش‌بین، ملاک، واسطه‌ای و تعدیل‌کننده", "criticality": "CRITICAL"},
    {"id": "8", "name_en": "Data sources and measurement tools (psychometric validity/reliability)", "name_fa": "ابزارهای اندازه‌گیری و شاخص‌های روان‌سنجی (روایی/پایایی)", "criticality": "CRITICAL"},
    {"id": "9", "name_en": "Efforts to address potential sources of bias", "name_fa": "بررسی و مهار منابع سوگیری (پاسخ‌دهی، همخطی)", "criticality": "MAJOR"},
    {"id": "10", "name_en": "Study size justification (G*Power or N:q ratio for SEM)", "name_fa": "توجیه حجم نمونه بر پایه تحلیل توان G*Power یا نسبت N:q", "criticality": "CRITICAL"},
    {"id": "11", "name_en": "Handling of quantitative continuous variables", "name_fa": "نحوه بررسی و نمره‌گذاری متغیرهای پیوسته", "criticality": "MINOR"},
    {"id": "12", "name_en": "Statistical methods including assumption checks (normality, collinearity)", "name_fa": "روش‌های آماری و آزمون مفروضه‌ها (نرمالیتی، خطی‌بودن)", "criticality": "CRITICAL"},
    {"id": "13", "name_en": "Participant numbers at each stage & response rate", "name_fa": "تعداد شرکت‌کنندگان و نرخ پاسخ‌دهی پرسشنامه‌ها", "criticality": "MAJOR"},
    {"id": "14", "name_en": "Descriptive demographic characteristics", "name_fa": "آمار توصیفی جمعیت‌شناختی (سن، جنسیت، تحصیلات)", "criticality": "MAJOR"},
    {"id": "15", "name_en": "Outcome and predictor descriptive statistics (M, SD)", "name_fa": "شاخص‌های توصیفی متغیرها (میانگین، انحراف معیار، چولگی)", "criticality": "MAJOR"},
    {"id": "16", "name_en": "Main statistical results with parameter estimates and 95% CI", "name_fa": "نتایج اصلی با ضرایب مسیر، بتای رگرسیون و فواصل اطمینان", "criticality": "CRITICAL"},
    {"id": "17", "name_en": "Other analyses (subgroups, model fit indices: CFI, RMSEA)", "name_fa": "شاخص‌های برازش مدل (CFI, TLI, RMSEA, SRMR) یا آزمون‌های فرعی", "criticality": "MAJOR"},
    {"id": "18", "name_en": "Summary of key results mapped to objectives", "name_fa": "خلاصه یافته‌های اصلی متناظر با فرضیه‌ها", "criticality": "MAJOR"},
    {"id": "19", "name_en": "Discussion of limitations and methodological biases", "name_fa": "محدودیت‌های متدولوژیک و تعمیم‌ناپذیری ابزارها", "criticality": "MAJOR"},
    {"id": "20", "name_en": "Interpretation of results in theoretical context", "name_fa": "تفسیر یافته‌ها در پیوند با تئوری‌ها و پیشینه‌های تجربی", "criticality": "MAJOR"},
    {"id": "21", "name_en": "Generalisability of findings", "name_fa": "قابلیت تعمیم به جامعه بیرونی", "criticality": "MINOR"},
    {"id": "22", "name_en": "Funding, ethics approval, and conflict of interest declarations", "name_fa": "کد اخلاق پژوهش، عدم تعارض منافع و تامین مالی", "criticality": "MAJOR"}
]

PRISMA_CHECKLIST = [
    {"id": "1", "name_en": "Title identifying report as systematic review or meta-analysis", "name_fa": "عنوان نشان‌دهنده مرور سیستماتیک یا فرا-تحلیل", "criticality": "MAJOR"},
    {"id": "2", "name_en": "Structured summary abstract (PRISMA format)", "name_fa": "چکیده ساختاریافته مطابق قالب PRISMA", "criticality": "MAJOR"},
    {"id": "3", "name_en": "Rationale in context of existing knowledge", "name_fa": "مبانی نظری و شکاف موجود در ادبیات پژوهش", "criticality": "MAJOR"},
    {"id": "4", "name_en": "Explicit statement of objectives based on PICO", "name_fa": "اهداف مشخص بر پایه ساختار PICO/PECO", "criticality": "MAJOR"},
    {"id": "5", "name_en": "Eligibility criteria (inclusion and exclusion)", "name_fa": "معیارهای ورود و خروج مقالات", "criticality": "CRITICAL"},
    {"id": "6", "name_en": "Information sources and search dates (PubMed, Scopus, SID)", "name_fa": "پایگاه‌های اطلاعاتی و تاریخ‌های جستجو", "criticality": "CRITICAL"},
    {"id": "7", "name_en": "Full search strategy with Boolean operators for at least one database", "name_fa": "استراتژی کامل جستجو با عملگرهای بولی برای حداقل یک پایگاه", "criticality": "MAJOR"},
    {"id": "8", "name_en": "Study selection process (independent double screening)", "name_fa": "فرایند غربالگری مستقل دو پژوهشگر و حل اختلاف", "criticality": "MAJOR"},
    {"id": "9", "name_en": "Data extraction process and coding forms", "name_fa": "فرایند استخراج داده‌ها و فرم‌های کدگذاری", "criticality": "MAJOR"},
    {"id": "10", "name_en": "Data items extracted from studies", "name_fa": "فهرست متغیرها و اطلاعات استخراج‌شده", "criticality": "MAJOR"},
    {"id": "11", "name_en": "Study risk of bias assessment tool (RoB 2, NOS, Newcastle)", "name_fa": "ابزار ارزیابی خطر سوگیری یا کیفیت مقالات", "criticality": "CRITICAL"},
    {"id": "12", "name_en": "Effect measures (Hedges' g, Cohen's d, Odds Ratio)", "name_fa": "شاخص اندازه اثر ترکیبی استانداردشده", "criticality": "CRITICAL"},
    {"id": "13", "name_en": "Synthesis methods & heterogeneity model (I², Q, tau²)", "name_fa": "مدل تلفیق (اثرات تصادفی/ثابت) و شاخص‌های ناهمگنی", "criticality": "CRITICAL"},
    {"id": "14", "name_en": "Reporting bias assessment methods (Egger, Begg, Trim & Fill)", "name_fa": "روش‌های ارزیابی سوگیری انتشار (ایگر، قیفی)", "criticality": "MAJOR"},
    {"id": "15", "name_en": "Certainty of evidence assessment (GRADE framework)", "name_fa": "ارزیابی قطعیت شواهد با رویکرد GRADE", "criticality": "MINOR"},
    {"id": "16", "name_en": "Study selection results: PRISMA 2020 Flow Diagram", "name_fa": "نمودار جریان انتخاب مطالعات (PRISMA 2020 Flowchart)", "criticality": "CRITICAL"},
    {"id": "17", "name_en": "Study characteristics table of included trials", "name_fa": "جدول مشخصات توصیفی مطالعات واردشده به فراتحلیل", "criticality": "MAJOR"},
    {"id": "18", "name_en": "Risk of bias assessment results across studies", "name_fa": "نتایج تفصیلی ارزیابی خطر سوگیری مقالات", "criticality": "MAJOR"},
    {"id": "19", "name_en": "Individual study results and Forest Plot", "name_fa": "نتایج مطالعات منفرد و نمودار انباشت (Forest Plot)", "criticality": "CRITICAL"},
    {"id": "20", "name_en": "Synthesized results and pooled effect size with 95% CI", "name_fa": "اندازه اثر ترکیبی تجمیعی با فاصله اطمینان ۹۵٪ و سطح p", "criticality": "CRITICAL"},
    {"id": "21", "name_en": "Reporting biases evaluation (Funnel Plot & Egger's p)", "name_fa": "نتایج سوگیری انتشار و نمودار قیفی (Funnel Plot)", "criticality": "MAJOR"},
    {"id": "22", "name_en": "Certainty of evidence results summary", "name_fa": "خلاصه شواهد و درجه قطعیت نتایج", "criticality": "MINOR"},
    {"id": "23", "name_en": "Discussion: interpretation in light of evidence", "name_fa": "بحث و تفسیر شواهد سنتزشده", "criticality": "MAJOR"},
    {"id": "24", "name_en": "Limitations of evidence and review process", "name_fa": "محدودیت‌های مطالعات واردشده و فرایند مرور", "criticality": "MAJOR"},
    {"id": "25", "name_en": "Conclusions and practical implications", "name_fa": "نتیجه‌گیری و دلالت‌های بالینی/پژوهشی", "criticality": "MAJOR"},
    {"id": "26", "name_en": "Registration number and protocol (PROSPERO ID)", "name_fa": "کد ثبت پروتکل مرور سیستماتیک در PROSPERO", "criticality": "MAJOR"},
    {"id": "27", "name_en": "Financial support, conflict of interest, and data availability", "name_fa": "حمایت مالی، اعلام عدم تعارض منافع و بیانیه دسترسی به داده", "criticality": "MAJOR"}
]

# ==============================================================================
# Audit Analysis Engine
# ==============================================================================

class ThesisIntegrityAuditor:
    def __init__(self, payload):
        self.payload = payload
        self.metadata = payload.get("project_metadata", {})
        self.findings = []
        self.audit_summary = {}
        self.equator_checklist_results = []
        self.equator_score = 0.0
        self.equator_guideline = ""
        self.submission_readiness_score = 0.0
        self.srs_grade = ""

    def audit_all(self):
        self._audit_hypotheses_alignment()
        self._audit_methodology_and_statistics()
        self._audit_citations_and_bibliography()
        self._audit_apa7_compliance()
        self._audit_adversarial_defense()
        self._audit_equator_reporting()
        self._compute_integrity_score()
        return self.audit_summary

    def _add_finding(self, domain, severity, title_fa, title_en, description_fa, description_en, recommendation_fa, recommendation_en, details=None):
        finding = {
            "domain": domain,
            "severity": severity,  # CRITICAL, MAJOR, MINOR, INFO
            "title_fa": title_fa,
            "title_en": title_en,
            "description_fa": description_fa,
            "description_en": description_en,
            "recommendation_fa": recommendation_fa,
            "recommendation_en": recommendation_en,
            "details": details or {}
        }
        self.findings.append(finding)

    def _audit_hypotheses_alignment(self):
        """Audits Ch 1 Hypotheses <-> Ch 4 Tests <-> Ch 5 Discussions"""
        ch1_hypos = {h["id"]: h for h in self.payload.get("chapter1_hypotheses", [])}
        ch4_tests = {t.get("hypothesis_id"): t for t in self.payload.get("chapter4_statistical_tests", []) if t.get("hypothesis_id")}
        phantom_tests = [t for t in self.payload.get("chapter4_statistical_tests", []) if not t.get("hypothesis_id")]
        ch5_discussions = {d["hypothesis_id"]: d for d in self.payload.get("chapter5_discussions", []) if d.get("hypothesis_id")}

        # 1. Orphan Hypotheses (Ch 1 present, Ch 4 absent)
        for hid, hypo in ch1_hypos.items():
            if hid not in ch4_tests:
                self._add_finding(
                    domain="hypothesis_alignment",
                    severity="CRITICAL",
                    title_fa=f"فرضیه آزمون‌نشده ({hid}): فرضیه در فصل ۱ ذکر شده اما در فصل ۴ تحلیلی برای آن ارائه نشده است",
                    title_en=f"Untested Hypothesis ({hid}): Stated in Chapter 1 but missing from Chapter 4 analysis",
                    description_fa=f"فرضیه '{hypo.get('statement')}' در طرح پژوهش و فصل اول تدوین شده، اما در فصل چهارم هیچ آزمون آماری برای بررسی آن گزارش نشده است.",
                    description_en=f"Hypothesis '{hypo.get('statement')}' was specified in Chapter 1, but no statistical test was conducted in Chapter 4.",
                    recommendation_fa="آزمون آماری مربوط به این فرضیه را در فصل چهارم اجرا و اضافه نمایید، یا در صورت حذف متغیر، فرضیه را از فصل اول و سوم حذف کنید.",
                    recommendation_en="Run and report the corresponding statistical test in Chapter 4, or remove the hypothesis from Chapters 1 and 3.",
                    details={"hypothesis_id": hid, "statement": hypo.get("statement")}
                )

        # 2. Phantom Statistical Tests (Ch 4 test present, Ch 1 hypothesis absent)
        for t in phantom_tests:
            self._add_finding(
                domain="hypothesis_alignment",
                severity="MAJOR",
                title_fa=f"آزمون آماری فرعی فاقد فرضیه مصوب ({t.get('test_id')}): بررسی متغیر بدون فرضیه در فصل اول",
                title_en=f"Phantom Statistical Test ({t.get('test_id')}): Analysis executed without prior hypothesis in Chapter 1",
                description_fa=f"در فصل چهارم آزمون آماری '{t.get('dv')}' ({t.get('method')}) اجرا شده است در حالی که هیچ فرضیه یا پرسش پژوهشی متناظری در فصل اول برای آن تعریف نشده است.",
                description_en=f"Test '{t.get('dv')}' ({t.get('method')}) was reported in Chapter 4 without a corresponding formal hypothesis in Chapter 1.",
                recommendation_fa="در صورتی که هدف بررسی فرضیه بوده است، آن را به اهداف و فرضیه‌های فصل اول بیفزایید؛ در غیر این صورت آن را تحت عنوان 'یافته‌های جانبی' مشخص کنید.",
                recommendation_en="Add the hypothesis to Chapter 1 goals, or explicitly reclassify the test as 'Exploratory / Secondary Findings'.",
                details={"test_id": t.get("test_id"), "method": t.get("method"), "dv": t.get("dv")}
            )

        # 3. Neglected in Chapter 5 Discussion
        for hid in ch4_tests:
            if hid not in ch5_discussions:
                self._add_finding(
                    domain="hypothesis_alignment",
                    severity="MAJOR",
                    title_fa=f"فرضیه فاقد بحث نظری ({hid}): در فصل ۴ تایید/رد شده اما در فصل ۵ تبیین نشده است",
                    title_en=f"Neglected Discussion ({hid}): Tested in Chapter 4 but not discussed in Chapter 5",
                    description_fa=f"فرضیه {hid} در فصل چهارم آزمون آماری شده، اما بخش بحث و نتیجه‌گیری (فصل پنجم) تبیین روان‌شناختی یا مقایسه پیشینه برای آن ارائه نداده است.",
                    description_en=f"Hypothesis {hid} was tested in Chapter 4, but Chapter 5 does not contain theoretical explanations or empirical comparisons.",
                    recommendation_fa="یک بخش مجزا برای تبیین یافته‌های فرضیه {hid} و مقایسه با پیشینه پژوهش به فصل پنجم اضافه نمایید.",
                    recommendation_en="Add a dedicated subsection in Chapter 5 discussing the psychological mechanisms and literature alignment for {hid}.",
                    details={"hypothesis_id": hid}
                )

        # 4. Verdict Contradiction (Ch 4 verdict vs Ch 5 verdict)
        for hid, test in ch4_tests.items():
            disc = ch5_discussions.get(hid)
            if disc:
                ch4_verdict = test.get("verdict")
                ch5_verdict = disc.get("verdict_in_ch5")
                if ch4_verdict and ch5_verdict and ch4_verdict != ch5_verdict:
                    self._add_finding(
                        domain="hypothesis_alignment",
                        severity="CRITICAL",
                        title_fa=f"تناقض در نتیجه فرضیه ({hid}): تضاد بین نتیجه آماری فصل ۴ و متن بحث فصل ۵",
                        title_en=f"Verdict Contradiction ({hid}): Inconsistency between Chapter 4 test result and Chapter 5 discussion",
                        description_fa=f"در فصل چهارم فرضیه به عنوان '{ch4_verdict}' گزارش شده اما در فصل پنجم نتیجه به عنوان '{ch5_verdict}' مورد بحث قرار گرفته است.",
                        description_en=f"Chapter 4 reports outcome as '{ch4_verdict}' whereas Chapter 5 discusses it as '{ch5_verdict}'.",
                        recommendation_fa="متن فصل پنجم را با نتیجه واقعی آزمون آماری فصل چهارم هماهنگ و اصلاح نمایید.",
                        recommendation_en="Harmonize Chapter 5 text to match the exact empirical verdict from Chapter 4.",
                        details={"hypothesis_id": hid, "ch4_verdict": ch4_verdict, "ch5_verdict": ch5_verdict}
                    )

    def _audit_methodology_and_statistics(self):
        """Audits N, group samples, and degrees of freedom consistency"""
        ch3 = self.payload.get("chapter3_methodology", {})
        total_N = ch3.get("total_sample_size", 0)
        groups = ch3.get("groups", [])
        num_groups = len(groups) if groups else 2

        # Sum of groups check
        if groups:
            sum_groups = sum(g.get("n", 0) for g in groups)
            if sum_groups != total_N:
                self._add_finding(
                    domain="methodology_statistics",
                    severity="CRITICAL",
                    title_fa="عدم انطباق حجم نمونه گروه‌ها با حجم نمونه کل در فصل سوم",
                    title_en="Group Sample Size Sum Discrepancy in Chapter 3",
                    description_fa=f"مجموع اعضای گروه‌ها ({sum_groups}) با حجم نمونه کل اعلام‌شده در روش پژوهش ({total_N}) برابر نیست.",
                    description_en=f"Sum of group sample sizes ({sum_groups}) does not equal total declared N ({total_N}).",
                    recommendation_fa="حجم نمونه گروه‌ها یا حجم نمونه کل را در جدول توصیف نمونه و روش‌شناسی اصلاح نمایید.",
                    recommendation_en="Reconcile group sizes or total N in Chapter 3 methodology and descriptive tables.",
                    details={"total_N": total_N, "group_sum": sum_groups}
                )

        # Check Degrees of Freedom in Chapter 4 tests
        ch4_tests = self.payload.get("chapter4_statistical_tests", [])
        for t in ch4_tests:
            method = t.get("method", "")
            stats = t.get("reported_stats", {})

            if "ANCOVA" in method:
                # ANCOVA: df_error = N - k - c (assuming 1 covariate c=1)
                expected_df_error = total_N - num_groups - 1
                reported_df_error = stats.get("df_error")
                if reported_df_error and reported_df_error != expected_df_error:
                    self._add_finding(
                        domain="methodology_statistics",
                        severity="CRITICAL",
                        title_fa=f"خطای درجه آزادی تحلیل کوواریانس در آزمون {t.get('test_id')}",
                        title_en=f"ANCOVA Degrees of Freedom Error in Test {t.get('test_id')}",
                        description_fa=f"برای حجم نمونه N = {total_N} و تعداد {num_groups} گروه با ۱ کوواریانس، درجه آزادی خطا باید {expected_df_error} باشد، اما {reported_df_error} گزارش شده است.",
                        description_en=f"For N = {total_N}, {num_groups} groups and 1 covariate, error df must be {expected_df_error}, but {reported_df_error} was reported.",
                        recommendation_fa=f"درجه آزادی تحلیل کوواریانس را به F(1, {expected_df_error}) در متن و جدول تصحیح فرمایید.",
                        recommendation_en=f"Correct ANCOVA degrees of freedom to F(1, {expected_df_error}) in text and tables.",
                        details={"test_id": t.get("test_id"), "reported_df": reported_df_error, "expected_df": expected_df_error}
                    )

            elif "Regression" in method:
                # Regression: df_residual = N - k - 1 (where k is number of predictors)
                beta_weights = stats.get("beta_weights", {})
                k_pred = len(beta_weights) if beta_weights else stats.get("df_regression", 1)
                expected_df_res = total_N - k_pred - 1
                reported_df_res = stats.get("df_residual")
                if reported_df_res and reported_df_res != expected_df_res:
                    self._add_finding(
                        domain="methodology_statistics",
                        severity="MAJOR",
                        title_fa=f"عدم انطباق درجه آزادی باقیمانده رگرسیون در آزمون {t.get('test_id')}",
                        title_en=f"Regression Residual Degrees of Freedom Mismatch in Test {t.get('test_id')}",
                        description_fa=f"با {k_pred} متغیر پیش‌بین و N = {total_N}، درجه آزادی باقیمانده باید {expected_df_res} باشد، اما {reported_df_res} گزارش شده است.",
                        description_en=f"With {k_pred} predictors and N = {total_N}, residual df must be {expected_df_res}, but {reported_df_res} was reported.",
                        recommendation_fa=f"درجه آزادی رگرسیون را به F({k_pred}, {expected_df_res}) تصحیح کنید.",
                        recommendation_en=f"Correct regression degrees of freedom to F({k_pred}, {expected_df_res}).",
                        details={"test_id": t.get("test_id"), "reported_df": reported_df_res, "expected_df": expected_df_res}
                    )

            elif "t-test" in method:
                # Independent t-test: df = N - 2
                expected_df = total_N - 2
                reported_df = stats.get("df")
                if reported_df and reported_df != expected_df:
                    self._add_finding(
                        domain="methodology_statistics",
                        severity="MAJOR",
                        title_fa=f"خطای درجه آزادی آزمون تی مستقل ({t.get('test_id')})",
                        title_en=f"Independent Samples t-Test Degrees of Freedom Error in Test {t.get('test_id')}",
                        description_fa=f"برای دو گروه مستقل با مجموع N = {total_N}، درجه آزادی آزمون تی باید df = {expected_df} باشد، در حالی که {reported_df} درج گردیده است.",
                        description_en=f"For independent groups totaling N = {total_N}, t-test df must be {expected_df}, but {reported_df} was entered.",
                        recommendation_fa=f"درجه آزادی آزمون تی را به t({expected_df}) تصحیح نمایید.",
                        recommendation_en=f"Correct t-test degrees of freedom to t({expected_df}).",
                        details={"test_id": t.get("test_id"), "reported_df": reported_df, "expected_df": expected_df}
                    )

    def _normalize_name(self, name):
        """Helper to normalize author name for matching"""
        name = re.sub(r'[\.,،]', '', name.lower())
        name = name.replace('et al', '').replace('و همکاران', '').strip()
        return name

    def _audit_citations_and_bibliography(self):
        """Bidirectional citation reconciliation"""
        in_text = self.payload.get("in_text_citations", [])
        bib_refs = self.payload.get("bibliography_references", [])

        # Categorize
        self.matched_citations = []
        self.orphaned_in_text = []
        self.superfluous_bib = []
        self.year_discrepancies = []

        bib_matched_indices = set()

        for cit in in_text:
            c_author = self._normalize_name(cit.get("author", ""))
            c_year = int(cit.get("year", 0)) if str(cit.get("year", "")).isdigit() else 0

            found_exact = False
            best_author_match = None
            best_ratio = 0.0

            for idx, ref in enumerate(bib_refs):
                r_author = self._normalize_name(ref.get("author", ""))
                r_year = int(ref.get("year", 0)) if str(ref.get("year", "")).isdigit() else 0

                ratio = SequenceMatcher(None, c_author, r_author).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_author_match = (idx, ref, r_year)

                if ratio >= 0.85 and c_year == r_year:
                    found_exact = True
                    bib_matched_indices.add(idx)
                    self.matched_citations.append({
                        "in_text": cit,
                        "reference": ref,
                        "status": "MATCHED"
                    })
                    break

            if not found_exact:
                # Check for year discrepancy
                if best_ratio >= 0.85 and best_author_match:
                    idx, ref, r_year = best_author_match
                    bib_matched_indices.add(idx)
                    self.year_discrepancies.append({
                        "in_text": cit,
                        "reference": ref,
                        "year_in_text": c_year,
                        "year_in_bib": r_year,
                        "status": "YEAR_DISCREPANCY"
                    })
                    self._add_finding(
                        domain="citations_bibliography",
                        severity="MINOR",
                        title_fa=f"مغایرت سال انتشار منبع: {cit.get('author')}",
                        title_en=f"Publication Year Mismatch: {cit.get('author')}",
                        description_fa=f"در متن پایان‌نامه سال {c_year} قید شده، اما در فهرست منابع پایان‌نامه سال انتشار {r_year} ثبت گردیده است.",
                        description_en=f"In-text citation cites year {c_year}, but bibliography entry indicates {r_year}.",
                        recommendation_fa="سال انتشار را بین متن و فهرست مراجع مطابقت داده و یکسان نمایید.",
                        recommendation_en="Verify and synchronize the publication year between in-text and bibliography.",
                        details={"author": cit.get("author"), "text_year": c_year, "bib_year": r_year}
                    )
                else:
                    # Orphaned in text
                    self.orphaned_in_text.append(cit)
                    self._add_finding(
                        domain="citations_bibliography",
                        severity="MAJOR",
                        title_fa=f"ارجاع درون‌متنی فاقد مشخصات در فهرست منابع: {cit.get('author')} ({c_year})",
                        title_en=f"Orphaned In-Text Citation: {cit.get('author')} ({c_year})",
                        description_fa=f"منبع '{cit.get('raw')}' در فصل {cit.get('chapter', 'نامشخص')} ارجاع داده شده، اما اطلاعات کتابشناختی آن در فهرست مراجع انتهای پایان‌نامه موجود نیست.",
                        description_en=f"Citation '{cit.get('raw')}' was cited in Chapter {cit.get('chapter', '?')}, but is entirely missing from the reference list.",
                        recommendation_fa="مشخصات کامل کتابشناختی این منبع را طبق الگوی APA 7 به انتهای پایان‌نامه اضافه فرمایید.",
                        recommendation_en="Add the full APA 7 bibliographic reference entry to the References section.",
                        details={"citation": cit}
                    )

        # Superfluous References (In bibliography but never cited in text)
        for idx, ref in enumerate(bib_refs):
            if idx not in bib_matched_indices:
                self.superfluous_bib.append(ref)
                self._add_finding(
                    domain="citations_bibliography",
                    severity="MAJOR",
                    title_fa=f"منبع ذکرشده در کتابشناسی بدون ارجاع درون‌متنی: {ref.get('author')} ({ref.get('year')})",
                    title_en=f"Ghost Reference in Bibliography: {ref.get('author')} ({ref.get('year')})",
                    description_fa=f"منبع '{ref.get('author')}' در فهرست منابع درج شده است، اما در هیچ‌یک از فصول پایان‌نامه به آن استناد نشده است.",
                    description_en=f"Reference '{ref.get('author')}' is listed in the bibliography but is never cited in any thesis chapter.",
                    recommendation_fa="در صورتی که از این منبع استفاده نشده آن را از فهرست منابع حذف کنید، یا محل ارجاع آن را در متن مشخص نمایید.",
                    recommendation_en="Remove this entry from the bibliography, or cite it in the relevant literature section.",
                    details={"reference": ref}
                )

    def _audit_apa7_compliance(self):
        """Scans for APA 7th Edition formatting infractions"""
        ch4_tests = self.payload.get("chapter4_statistical_tests", [])
        sampled_paragraphs = self.payload.get("apa7_formatting_audit", {}).get("sampled_paragraphs", [])

        # 1. p = .000 violation check in tests
        for t in ch4_tests:
            stats = t.get("reported_stats", {})
            raw_p = stats.get("p_value_raw_text", "")
            if raw_p in [".000", "0.000", ".0000", "0.0000"]:
                self._add_finding(
                    domain="apa7_formatting",
                    severity="MINOR",
                    title_fa=f"گزارش مقدار غیرمجاز p = .000 در آزمون {t.get('test_id')}",
                    title_en=f"Illegal Software Output p = .000 Reported in Test {t.get('test_id')}",
                    description_fa="طبق راهنمای APA 7th Edition و استانداردهای دانشگاهی، هیچ مقدار احتمالاتی نباید به صورت p = .000 گزارش شود و باید به صورت p < .001 قید گردد.",
                    description_en="According to APA 7 guidelines, probabilities must never be reported as p = .000; use p < .001 instead.",
                    recommendation_fa="در جداول و متن فصل چهارم، تمام موارد p = .000 را به p < .001 (یا ۰/۰۰۱ > p) تغییر دهید.",
                    recommendation_en="Replace all occurrences of p = .000 with p < .001 in Chapter 4 text and tables.",
                    details={"test_id": t.get("test_id")}
                )

            # 2. Leading zero in p-value
            if raw_p.startswith("0."):
                self._add_finding(
                    domain="apa7_formatting",
                    severity="MINOR",
                    title_fa=f"عدم حذف صفر پیشین (Leading Zero) در مقدار p آزمون {t.get('test_id')}",
                    title_en=f"Leading Zero Violation in p-value for Test {t.get('test_id')}",
                    description_fa=f"مقدار معناداری به صورت '{raw_p}' درج شده است. اعدادی که نمی‌توانند از ۱ تجاوز کنند در APA 7 نباید صفر قبل از ممیز داشته باشند.",
                    description_en=f"p-value reported as '{raw_p}'. Numbers bounded by 1 must omit the leading zero (e.g. .{raw_p.split('.')[1]}).",
                    recommendation_fa=f"صفر پیشین را حذف نمایید: p = .{raw_p.split('.')[1]}",
                    recommendation_en=f"Omit the leading zero: p = .{raw_p.split('.')[1]}",
                    details={"test_id": t.get("test_id"), "reported": raw_p}
                )

        # 3. Check sampled paragraphs for leading zero violations (r, R2, eta)
        for p_idx, text in enumerate(sampled_paragraphs):
            # Check for r = 0.xx
            if re.search(r'[rR]\s*=\s*0\.\d+', text):
                self._add_finding(
                    domain="apa7_formatting",
                    severity="MINOR",
                    title_fa="وجود صفر پیشین در ضریب همبستگی در متن",
                    title_en="Leading Zero Violation in Correlation Coefficient in Text",
                    description_fa="در متن پاراگراف ضریب همبستگی با صفر پیشین (مانند r = 0.xx) درج شده است.",
                    description_en="In-text correlation coefficient reports leading zero (e.g. r = 0.xx).",
                    recommendation_fa="صفر قبل از ممیز ضریب همبستگی را حذف فرمایید (مثال: r = .xx).",
                    recommendation_en="Remove the leading zero from correlation coefficient (e.g., r = .xx).",
                    details={"paragraph_index": p_idx}
                )


    def _audit_adversarial_defense(self):
        """
        Dimension 5: Adversarial Defense & Peer-Review Simulation (from Sida Peng & Rule 10)
        Audits:
          1. Effect size plausibility (Rule 10 anti-over-separation guardrail)
          2. Methodological reproducibility & psychometric transparency
          3. Assumption completeness (Box's M, Levene, Normality)
          4. Hostile referee question simulation
        """
        tests = self.payload.get("chapter4_statistical_tests", [])
        self.adversarial_questions = []

        for t in tests:
            test_id = t.get("test_id", "Test")
            stats = t.get("statistics", {})
            p_val = stats.get("p_value")
            
            # 1. Effect Size Plausibility & Multi-Signal Anomaly Check
            eta_sq = stats.get("partial_eta_squared") or stats.get("eta_squared")
            cohen_d = stats.get("cohen_d")

            if eta_sq is not None:
                try:
                    eta_val = float(eta_sq)
                    if eta_val > 0.40:
                        self._add_finding(
                            domain="adversarial_defense",
                            severity="REVIEW_FLAG",
                            title_fa=f"هشدار بازبینی اندازه اثر بالا در آزمون {test_id} (FLAG FOR REVIEW)",
                            title_en=f"High Effect Size Diagnostic in Test {test_id} (FLAG FOR REVIEW)",
                            description_fa=f"اندازه اثر گزارش‌شده (eta_p^2 = {eta_val:.3f}) از سطح معمول مطالعات روان‌شناختی (۰/۲۵ تا ۰/۴۰) بالاتر است. هرچند مداخلات بالینی عمیق و متمرکز می‌توانند اندازه اثرهای بسیار بزرگ تولید کنند، اما این مقدار در جلسه دفاع و داوری مورد پرسش دقیق قرار خواهد گرفت و نیازمند تبیین مکانیسم بالینی یا بررسی همپوشانی توزیع گروه‌ها است.",
                            description_en=f"Reported partial eta squared ({eta_val:.3f}) is high (> .40). While potent clinical interventions can legitimately produce substantial effects, thesis committees and peer reviewers will closely scrutinize distribution overlap and potential sample variance deflation.",
                            recommendation_fa="در فصل ۴ و ۵، قدرت پروتکل مداخله را تبیین نموده و نمودار توزیع نمرات یا همپوشانی گروه‌ها را جهت اطمینان از کفایت تنوع پاسخ‌ها ارائه فرمایید.",
                            recommendation_en="In Chapters 4 and 5, document the therapeutic potency of the protocol and report distribution overlap/sensitivity checks to address reviewer skepticism.",
                            details={"test_id": test_id, "eta_squared": eta_val, "flag": "FLAG_FOR_REVIEW"}
                        )
                    elif eta_val < 0.01 and p_val is not None and float(p_val) < 0.05:
                        self._add_finding(
                            domain="adversarial_defense",
                            severity="MAJOR",
                            title_fa=f"معناداری آماری کاذب با اندازه اثر ناچیز در آزمون {test_id}",
                            title_en=f"Statistical Significance with Negligible Effect Size in Test {test_id}",
                            description_fa=f"آزمون با مقدار p = {p_val} معنادار شده اما اندازه اثر (eta_p^2 = {eta_val:.3f}) بسیار ناچیز است و داوران پیرامون اثربخشی واقعی بالینی آن تشکیک خواهند کرد.",
                            description_en=f"Test reached significance (p = {p_val}) but effect size is negligible (eta_p^2 = {eta_val:.3f}), raising doubts about clinical relevance.",
                            recommendation_fa="در فصل ۵ تصریح نمایید که معناداری حاصل صرفاً به واسطه توان آزمون بوده و اندازه اثر نیازمند احتیاط بالینی است.",
                            recommendation_en="Clarify in Chapter 5 that statistical significance must be interpreted cautiously due to trivial effect size.",
                            details={"test_id": test_id, "eta_squared": eta_val}
                        )
                except (ValueError, TypeError):
                    pass

            if cohen_d is not None:
                try:
                    d_val = float(cohen_d)
                    if d_val > 1.80:
                        self._add_finding(
                            domain="adversarial_defense",
                            severity="REVIEW_FLAG",
                            title_fa=f"هشدار بازبینی دی کوهن بالا (d = {d_val:.2f}) در آزمون {test_id} (FLAG FOR REVIEW)",
                            title_en=f"Elevated Cohen's d (d = {d_val:.2f}) in Test {test_id} (FLAG FOR REVIEW)",
                            description_fa=f"اندازه اثر دی کوهن d = {d_val:.2f} نشان‌دهنده تفکیک قابل‌توجه دو گروه است. توصیه می‌شود تصحیح سوگیری نمونه‌های کوچک (Hedges' g) نیز گزارش شده و برای دفاع شفاهی آماده شوید.",
                            description_en=f"Cohen's d of {d_val:.2f} reflects substantial group separation. Reporting Hedges' g to correct for small-sample upward bias is recommended for viva voce defensibility.",
                            recommendation_fa="اندازه اثر g هجز را در کنار d گزارش نموده و بر دلالت‌های کاربردی تمرکز کنید.",
                            recommendation_en="Report Hedges' g alongside Cohen's d to account for potential small-sample estimation inflation.",
                            details={"test_id": test_id, "cohen_d": d_val, "flag": "FLAG_FOR_REVIEW"}
                        )
                except (ValueError, TypeError):
                    pass

        # 2. Assumption Check Completeness
        assumptions = self.payload.get("chapter4_assumptions", {})
        if not assumptions.get("homogeneity_of_variance_levene") and any("ANCOVA" in t.get("method", "") or "ANOVA" in t.get("method", "") for t in tests):
            self._add_finding(
                domain="adversarial_defense",
                severity="MAJOR",
                title_fa="عدم گزارش آزمون لون برای همگنی واریانس‌ها",
                title_en="Missing Levene's Test for Homogeneity of Variance",
                description_fa="در تحلیل‌های واریانس یا کوواریانس، پیش‌فرض همگنی واریانس خطا (Levene's Test) گزارش نشده است. داوران روش‌شناس در گام اول عدم نقض این پیش‌فرض را طلب خواهند کرد.",
                description_en="Levene's test for homogeneity of variance is absent in ANOVA/ANCOVA reporting, creating an immediate defense vulnerability.",
                recommendation_fa="جدول نتایج آزمون لون (F و سطح معناداری p > .05) را به ابتدای یافته‌های فصل چهارم اضافه کنید.",
                recommendation_en="Include Levene's test results (F and p > .05) prior to hypothesis testing tables in Chapter 4."
            )

        if not assumptions.get("homogeneity_of_covariance_box_m") and any("MANOVA" in t.get("method", "") for t in tests):
            self._add_finding(
                domain="adversarial_defense",
                severity="MAJOR",
                title_fa="عدم گزارش آزمون ام‌باکس برای همگنی ماتریس‌های کوواریانس",
                title_en="Missing Box's M Test for Covariance Homogeneity",
                description_fa="برای تحلیل واریانس چندمتغیره (مانوا)، آزمون ام‌باکس (Box's M) گزارش نشده است.",
                description_en="Box's M test was not reported for MANOVA multivariate analyses.",
                recommendation_fa="آزمون ام‌باکس (p > .05) را در مقدمه آزمون فرضیه‌ها درج نمایید.",
                recommendation_en="Report Box's M test verifying covariance homogeneity prior to Wilks' Lambda."
            )

        # 3. Simulate Hostile Defense Examiner Probes
        self.adversarial_questions = [
            {
                "probe_fa": "چرا با وجود معناداری آماری، اطمینان دارید که اثر مداخله ناشی از انتظارات مراجع (اثر هاوثورن یا دارونما) نبوده است؟",
                "probe_en": "How can you ensure the significant intervention effect is not merely driven by the Hawthorne or placebo effect?",
                "rebuttal_fa": "استفاده از گروه کنترل فعال/لیست انتظار، همتاسازی پیش‌آزمون، و ارزیابی پیگیری ۱ تا ۲ ماهه جهت اثبات پایداری تغییرات ساختاری.",
                "rebuttal_en": "Use of waitlist/active control, baseline ANCOVA adjustment, and 2-month follow-up confirming sustained behavioral changes."
            },
            {
                "probe_fa": "علت انتخاب این حجم نمونه مشخص و توان آماری حاصل بر مبنای تحلیل G*Power چه بوده است؟",
                "probe_en": "What was the statistical power justification for your sample size according to G*Power?",
                "rebuttal_fa": "محاسبه بر پایه اندازه اثر متوسط f = 0.25، آلفای ۰/۰۵ و توان آزمون ۰/۸۰ که حداقل حجم نمونه مورد نیاز را توجیه می‌نماید.",
                "rebuttal_en": "A priori G*Power analysis with medium effect size f = .25, alpha = .05, and power = .80 justifying sample sufficiency."
            }
        ]

    def _audit_equator_reporting(self):
        """
        Dimension 6: EQUATOR Reporting Checklist Compliance & Submission Readiness
        Audits reporting completeness against international EQUATOR Network checklists:
          - CONSORT 2010 (Randomized Controlled Trials & Interventions)
          - STROBE (Observational, Correlational, Survey Studies)
          - PRISMA 2020 (Systematic Reviews & Meta-Analyses)
        """
        study_type = str(self.payload.get("study_type", "auto")).lower()
        title = (self.metadata.get("title", "") + " " + self.metadata.get("title_en", "")).lower()
        design = str(self.payload.get("chapter3_methodology", {}).get("design", "")).lower()

        if study_type == "auto":
            if any(k in title or k in design for k in ["meta-analysis", "systematic review", "فراتحلیل", "مرور سیستماتیک", "متاآنالیز"]):
                study_type = "prisma"
            elif any(k in title or k in design for k in ["trial", "intervention", "rct", "experimental", "semi-experimental", "آزمایشی", "نیمه‌آزمایشی", "کارآزمایی", "مداخله"]):
                study_type = "consort"
            else:
                study_type = "strobe"

        if study_type == "prisma":
            checklist_def = PRISMA_CHECKLIST
            guideline_name = "PRISMA 2020"
        elif study_type == "consort":
            checklist_def = CONSORT_CHECKLIST
            guideline_name = "CONSORT 2010"
        else:
            checklist_def = STROBE_CHECKLIST
            guideline_name = "STROBE"

        self.equator_guideline = guideline_name
        self.equator_checklist_results = []

        explicit_checklist = self.payload.get("equator_checklist", {})

        ch1_hyps = self.payload.get("chapter1_hypotheses", [])
        ch3_meth = self.payload.get("chapter3_methodology", {})
        ch4_tests = self.payload.get("chapter4_statistical_tests", [])
        ch4_assump = self.payload.get("chapter4_assumptions", {})
        ch5_disc = self.payload.get("chapter5_discussion", {})
        meta = self.metadata

        for item in checklist_def:
            i_id = item["id"]
            name_en = item["name_en"]
            name_fa = item["name_fa"]
            crit = item["criticality"]

            status = explicit_checklist.get(i_id) or explicit_checklist.get(str(i_id))
            note = ""

            if not status:
                if guideline_name == "CONSORT 2010":
                    if i_id in ["1a", "1b"]:
                        status = "PRESENT" if meta.get("title") else "MISSING"
                    elif i_id in ["2a", "2b"]:
                        status = "PRESENT" if ch1_hyps else "MISSING"
                    elif i_id == "3a":
                        status = "PRESENT" if ch3_meth.get("design") else "PARTIAL"
                    elif i_id in ["4a", "4b"]:
                        status = "PRESENT" if (ch3_meth.get("inclusion_criteria") or meta.get("population") or ch3_meth.get("total_sample_size")) else "PARTIAL"
                    elif i_id == "5":
                        status = "PRESENT" if (ch3_meth.get("intervention_protocol") or "intervention" in str(ch3_meth).lower() or ch3_meth.get("groups")) else "PARTIAL"
                    elif i_id == "6a":
                        status = "PRESENT" if ch3_meth.get("instruments") else "PARTIAL"
                    elif i_id == "7a":
                        if ch3_meth.get("sample_size_justification") or "g*power" in str(ch3_meth).lower() or "توان" in str(ch3_meth):
                            status = "PRESENT"
                        elif ch3_meth.get("total_sample_size"):
                            status = "PARTIAL"
                            note = "Sample size reported but lacking formal G*Power justification"
                        else:
                            status = "MISSING"
                    elif i_id in ["8a", "9"]:
                        if "random" in design or "تصادفی" in design:
                            status = "PRESENT" if ch3_meth.get("randomization") else "PARTIAL"
                        else:
                            status = "PARTIAL"
                            note = "Quasi-experimental design; allocation concealment non-applicable or unmasked"
                    elif i_id == "11a":
                        status = "PRESENT" if ch3_meth.get("blinding") else "PARTIAL"
                    elif i_id == "12a":
                        status = "PRESENT" if ch4_tests else "MISSING"
                    elif i_id == "13a":
                        status = "PRESENT" if (self.payload.get("flowchart") or ch3_meth.get("flowchart") or self.payload.get("flowchart_path")) else "MISSING"
                        if status == "MISSING":
                            note = "CONSORT participant flowchart is missing"
                    elif i_id == "13b":
                        status = "PRESENT" if ("dropouts" in ch3_meth or ch3_meth.get("dropouts") is not None) else "PARTIAL"
                    elif i_id == "15":
                        status = "PRESENT" if (ch3_meth.get("demographics") or self.payload.get("baseline_characteristics")) else "PARTIAL"
                    elif i_id == "16":
                        status = "PRESENT" if (ch3_meth.get("groups") and all("n" in g for g in ch3_meth.get("groups", []))) else "PARTIAL"
                    elif i_id == "17a":
                        has_es = any(t.get("reported_stats", {}).get("eta_squared") is not None or t.get("statistics", {}).get("partial_eta_squared") is not None for t in ch4_tests)
                        status = "PRESENT" if has_es else "PARTIAL"
                    elif i_id == "18":
                        status = "PRESENT" if (ch4_assump.get("homogeneity_of_variance_levene") or ch4_assump.get("normality_shapiro")) else "PARTIAL"
                    elif i_id == "19":
                        status = "PRESENT" if ("harms" in str(ch3_meth).lower() or "ملاحظات اخلاقی" in str(ch3_meth) or "ethics" in str(ch3_meth).lower()) else "PARTIAL"
                    elif i_id in ["20", "21", "22"]:
                        status = "PRESENT" if (ch5_disc.get("limitations") or "محدودیت" in str(ch5_disc)) else "PARTIAL"
                    elif i_id == "23":
                        status = "PRESENT" if (meta.get("irct_id") or self.payload.get("trial_registration")) else "PARTIAL"
                        if status == "PARTIAL":
                            note = "IRCT clinical trial registration ID not specified"
                    else:
                        status = "PARTIAL"

                elif guideline_name == "PRISMA 2020":
                    if i_id in ["1", "2", "3", "4"]:
                        status = "PRESENT" if meta.get("title") else "MISSING"
                    elif i_id in ["5", "6"]:
                        status = "PRESENT" if (ch3_meth.get("databases") or ch3_meth.get("eligibility_criteria")) else "PARTIAL"
                    elif i_id == "7":
                        status = "PRESENT" if ch3_meth.get("search_strategy") else "PARTIAL"
                    elif i_id in ["8", "9", "10"]:
                        status = "PRESENT" if (ch3_meth.get("screening_process") or ch3_meth.get("data_extraction")) else "PARTIAL"
                    elif i_id == "11":
                        status = "PRESENT" if (ch3_meth.get("risk_of_bias_tool") or "rob" in str(ch3_meth).lower()) else "PARTIAL"
                    elif i_id in ["12", "13"]:
                        status = "PRESENT" if (ch4_tests or self.payload.get("meta_analysis_results")) else "MISSING"
                    elif i_id == "14":
                        status = "PRESENT" if (self.payload.get("publication_bias") or ch4_assump.get("egger_test")) else "PARTIAL"
                    elif i_id == "15":
                        status = "PRESENT" if self.payload.get("grade_assessment") else "PARTIAL"
                    elif i_id == "16":
                        status = "PRESENT" if (self.payload.get("flowchart") or self.payload.get("prisma_flowchart")) else "MISSING"
                        if status == "MISSING":
                            note = "PRISMA 2020 4-phase flowchart is missing"
                    elif i_id in ["17", "18"]:
                        status = "PRESENT" if self.payload.get("included_studies") else "PARTIAL"
                    elif i_id == "19":
                        status = "PRESENT" if self.payload.get("forest_plot") else "PARTIAL"
                    elif i_id == "20":
                        status = "PRESENT" if (ch4_tests or self.payload.get("pooled_effect_size")) else "PARTIAL"
                    elif i_id == "21":
                        status = "PRESENT" if self.payload.get("funnel_plot") else "PARTIAL"
                    elif i_id in ["23", "24", "25"]:
                        status = "PRESENT" if ch5_disc else "PARTIAL"
                    elif i_id == "26":
                        status = "PRESENT" if meta.get("prospero_id") else "PARTIAL"
                    else:
                        status = "PARTIAL"

                else: # STROBE
                    if i_id in ["1", "2", "3", "4"]:
                        status = "PRESENT" if (meta.get("title") and ch1_hyps) else "PARTIAL"
                    elif i_id in ["5", "6"]:
                        status = "PRESENT" if (ch3_meth.get("total_sample_size") or ch3_meth.get("sampling_method")) else "PARTIAL"
                    elif i_id in ["7", "8"]:
                        status = "PRESENT" if ch3_meth.get("instruments") else "PARTIAL"
                    elif i_id == "9":
                        status = "PRESENT" if (ch4_assump.get("multicollinearity") or "bias" in str(ch3_meth).lower()) else "PARTIAL"
                    elif i_id == "10":
                        status = "PRESENT" if (ch3_meth.get("sample_size_justification") or "g*power" in str(ch3_meth).lower()) else "PARTIAL"
                    elif i_id in ["11", "12"]:
                        status = "PRESENT" if ch4_tests else "MISSING"
                    elif i_id == "13":
                        status = "PRESENT" if (self.payload.get("flowchart") or ch3_meth.get("response_rate")) else "PARTIAL"
                    elif i_id in ["14", "15"]:
                        status = "PRESENT" if ch3_meth.get("demographics") else "PARTIAL"
                    elif i_id == "16":
                        status = "PRESENT" if ch4_tests else "MISSING"
                    elif i_id == "17":
                        status = "PRESENT" if ch4_assump else "PARTIAL"
                    elif i_id in ["18", "19", "20", "21"]:
                        status = "PRESENT" if ch5_disc else "PARTIAL"
                    elif i_id == "22":
                        status = "PRESENT" if (meta.get("ethics_code") or meta.get("conflict_of_interest")) else "PARTIAL"
                    else:
                        status = "PARTIAL"

            status = str(status).upper()
            if status not in ["PRESENT", "PARTIAL", "MISSING"]:
                status = "PARTIAL"

            entry = {
                "item_id": i_id,
                "name_en": name_en,
                "name_fa": name_fa,
                "criticality": crit,
                "status": status,
                "note": note
            }
            self.equator_checklist_results.append(entry)

            if status == "MISSING" or (status == "PARTIAL" and crit == "CRITICAL"):
                sev = "MAJOR" if crit in ["CRITICAL", "MAJOR"] else "MINOR"
                self._add_finding(
                    domain="equator_compliance",
                    severity=sev,
                    title_fa=f"عدم انطباق با بند {i_id} چک‌لیست {guideline_name}: {name_fa}",
                    title_en=f"{guideline_name} Item {i_id} Compliance Deficit: {name_en}",
                    description_fa=f"مطابق استاندارد بین‌المللی {guideline_name}، بند {i_id} ({name_fa}) به صورت {status} ارزیابی شد. {note}",
                    description_en=f"Under international {guideline_name} standards, Item {i_id} ({name_en}) is {status}. {note}",
                    recommendation_fa=f"مستندات و بخش‌های مربوط به '{name_fa}' را قبل از ارسال مقاله/دفاع به پایان‌نامه اضافه نمایید.",
                    recommendation_en=f"Document and include '{name_en}' in the relevant chapter before submission.",
                    details={"item_id": i_id, "guideline": guideline_name, "status": status}
                )

        present_cnt = sum(1 for e in self.equator_checklist_results if e["status"] == "PRESENT")
        partial_cnt = sum(1 for e in self.equator_checklist_results if e["status"] == "PARTIAL")
        total_cnt = len(self.equator_checklist_results)

        self.equator_score = round(((present_cnt * 1.0) + (partial_cnt * 0.5)) / total_cnt * 100.0, 1) if total_cnt > 0 else 100.0

    def _compute_integrity_score(self):
        """Computes composite Thesis Integrity Score (TIS) and Submission Readiness Score (SRS) 0-100%"""
        critical_count = sum(1 for f in self.findings if f["severity"] == "CRITICAL")
        major_count = sum(1 for f in self.findings if f["severity"] == "MAJOR")
        minor_count = sum(1 for f in self.findings if f["severity"] == "MINOR")
        info_count = sum(1 for f in self.findings if f["severity"] == "INFO")

        tis = 100 - (15 * critical_count + 5 * major_count + 1 * minor_count)
        tis = max(0, min(100, tis))

        # Claim-evidence score
        ch1_hyps = self.payload.get("chapter1_hypotheses", [])
        ch4_tests = self.payload.get("chapter4_statistical_tests", [])
        if ch1_hyps:
            tested_ids = set(t.get("hypothesis_id") for t in ch4_tests if t.get("hypothesis_id"))
            hyp_ids = set(h.get("id") for h in ch1_hyps if h.get("id"))
            if hyp_ids:
                claim_evidence_score = round(len(hyp_ids.intersection(tested_ids)) / len(hyp_ids) * 100.0, 1)
            else:
                claim_evidence_score = 100.0
        else:
            claim_evidence_score = 100.0

        # APA 7 score
        apa_count = sum(1 for f in self.findings if f["domain"] == "apa7_formatting")
        apa7_score = max(0.0, min(100.0, 100.0 - (apa_count * 5.0)))

        # Submission Readiness Score (SRS)
        equator_score = getattr(self, "equator_score", 100.0)
        srs = round((0.40 * tis) + (0.30 * equator_score) + (0.15 * claim_evidence_score) + (0.15 * apa7_score), 1)
        srs = max(0.0, min(100.0, srs))
        self.submission_readiness_score = srs

        if srs >= 90:
            srs_grade = "A+"
            srs_status_fa = "آماده دفاع ممتاز و ارسال به مجلات بین‌المللی (A+)"
            srs_status_en = "Defense & Submission Ready (A+)"
        elif srs >= 80:
            srs_grade = "A"
            srs_status_fa = "آماده با اصلاحات ویرایشی جزیی (A)"
            srs_status_en = "Ready with Minor Revisions (A)"
        elif srs >= 70:
            srs_grade = "B"
            srs_status_fa = "نیازمند تکمیل موارد چک‌لیست قبل از سابمیت (B)"
            srs_status_en = "Checklist Revisions Required Before Submission (B)"
        else:
            srs_grade = "C"
            srs_status_fa = "عدم انطباق با استانداردهای گزارش‌دهی (C)"
            srs_status_en = "Critical Deficiencies - Not Submission Ready (C)"

        self.srs_grade = srs_grade

        if tis >= 90:
            status_fa = "آماده جلسه دفاع (Defense Ready)"
            status_en = "Defense Ready"
            verdict_desc_fa = "انطباق ساختاری، محاسباتی و کتابشناختی پایان‌نامه بسیار عالی است. تنها اصلاحات ویرایشی جزیی توصیه می‌شود."
        elif tis >= 75:
            status_fa = "نیازمند بازبینی استاد راهنما (Supervisor Revision Required)"
            status_en = "Supervisor Revision Required"
            verdict_desc_fa = "اصول کلی رعایت شده اما وجود برخی مغایرت‌های آماری یا منابع نیازمند اصلاح قبل از ارسال به داوران است."
        elif tis >= 50:
            status_fa = "نیازمند اصلاحات اساسی (Substantial Revision Required)"
            status_en = "Substantial Revision Required"
            verdict_desc_fa = "وجود فرضیه‌های آزمون‌نشده یا خطاهای محاسباتی در درجات آزادی مانع از برگزاری جلسه دفاع است."
        else:
            status_fa = "عدم تایید و مغایرت بنیادین (Critical Discrepancies)"
            status_en = "Critical Discrepancies"
            verdict_desc_fa = "پایان‌نامه دارای تناقضات جدی در فرضیه‌ها، محاسبات یا ارجاعات است و نیازمند بازنگری ساختاری کامل می‌باشد."

        present_cnt = sum(1 for e in getattr(self, "equator_checklist_results", []) if e["status"] == "PRESENT")
        partial_cnt = sum(1 for e in getattr(self, "equator_checklist_results", []) if e["status"] == "PARTIAL")
        missing_cnt = sum(1 for e in getattr(self, "equator_checklist_results", []) if e["status"] == "MISSING")

        self.audit_summary = {
            "thesis_integrity_score": tis,
            "submission_readiness_score": srs,
            "srs_grade": srs_grade,
            "srs_status_fa": srs_status_fa,
            "srs_status_en": srs_status_en,
            "readiness_status_fa": status_fa,
            "readiness_status_en": status_en,
            "verdict_description_fa": verdict_desc_fa,
            "equator_audit": {
                "guideline": getattr(self, "equator_guideline", "EQUATOR"),
                "equator_score": equator_score,
                "present_count": present_cnt,
                "partial_count": partial_cnt,
                "missing_count": missing_cnt,
                "total_items": len(getattr(self, "equator_checklist_results", [])),
                "items": getattr(self, "equator_checklist_results", [])
            },
            "subscores": {
                "tis": tis,
                "equator_score": equator_score,
                "claim_evidence_score": claim_evidence_score,
                "apa7_score": apa7_score,
                "weights": "TIS: 40%, EQUATOR: 30%, Claim-Evidence: 15%, APA7: 15%"
            },
            "finding_counts": {
                "critical": critical_count,
                "major": major_count,
                "minor": minor_count,
                "info": info_count,
                "total": len(self.findings)
            },
            "findings": self.findings,
            "citation_ledger_counts": {
                "matched": len(getattr(self, "matched_citations", [])),
                "orphaned_in_text": len(getattr(self, "orphaned_in_text", [])),
                "superfluous_bibliography": len(getattr(self, "superfluous_bib", [])),
                "year_discrepancies": len(getattr(self, "year_discrepancies", []))
            }
        }


# ==============================================================================
# Multi-Modal Report Generators (DOCX & Excel)
# ==============================================================================

def generate_audit_docx(auditor, out_path, lang="fa"):
    doc = docx.Document()
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)

    summary = auditor.audit_summary
    meta = auditor.metadata
    findings = auditor.findings
    counts = summary["finding_counts"]
    tis = summary["thesis_integrity_score"]
    is_fa = (lang == "fa")

    # Document Header Title
    title = "گزارش جامع ممیزی، صحت‌سنجی و انطباق درونی رساله" if is_fa else "Comprehensive Thesis Integrity & Cross-Chapter Audit Report"
    add_styled_paragraph(doc, title, bold=True, size_pt=18, color_rgb=(20, 45, 80),
                         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=4, is_bidi=is_fa)

    sub = "بررسی خودکار همخوانی فرضیه‌ها، روش‌شناسی، درجات آزادی، ارجاعات و استانداردهای APA 7" if is_fa else "Automated Audit of Hypotheses, Methodology, Degrees of Freedom, Citations & APA 7 Standards"
    add_styled_paragraph(doc, sub, italic=True, size_pt=11, color_rgb=(100, 110, 120),
                         align=WD_ALIGN_PARAGRAPH.CENTER, space_after=18, is_bidi=is_fa)

    # Executive Summary Box Table
    score_tbl = doc.add_table(rows=2, cols=6)
    score_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    make_table_apa7(score_tbl, is_bidi=is_fa)

    headers = [
        ("شاخص جامع انطباق (TIS)", "Integrity (TIS)"),
        ("شاخص آمادگی سابمیت (SRS)", "Readiness (SRS)"),
        ("چک‌لیست اکواتور", "EQUATOR Audit"),
        ("وضعیت آمادگی دفاع", "Defense Status"),
        ("خطاهای بحرانی (Critical)", "Critical"),
        ("نیازمند اصلاح (Major)", "Major")
    ]
    for col_idx, (h_fa, h_en) in enumerate(headers):
        cell = score_tbl.cell(0, col_idx)
        set_cell_shading(cell, "2B3A4A")
        set_cell_margins(cell, top=120, bottom=120)
        format_cell_text(cell, h_fa if is_fa else h_en, bold=True, size_pt=9.5, color_rgb=(255,255,255), is_bidi=is_fa)

    status_str = summary["readiness_status_fa"] if is_fa else summary["readiness_status_en"]
    srs_val = summary.get("submission_readiness_score", tis)
    srs_grade = summary.get("srs_grade", "A")
    eq_summary = summary.get("equator_audit", {})
    eq_str = f"{eq_summary.get('guideline', 'EQUATOR')} ({eq_summary.get('equator_score', 0)}%)"

    row_vals = [f"{tis}%", f"{srs_val}% ({srs_grade})", eq_str, status_str, str(counts["critical"]), str(counts["major"])]
    for col_idx, val in enumerate(row_vals):
        cell = score_tbl.cell(1, col_idx)
        set_cell_margins(cell, top=100, bottom=100)
        bold = (col_idx in [0, 1])
        color = (180, 40, 40) if (col_idx == 4 and counts["critical"] > 0) else (30, 30, 30)
        format_cell_text(cell, val, bold=bold, size_pt=10, color_rgb=color, is_bidi=is_fa)

    add_styled_paragraph(doc, "", space_after=12)

    # Thesis Metadata Card
    meta_p = add_styled_paragraph(doc, "۱. مشخصات طرح پژوهش و رساله" if is_fa else "1. Project & Dissertation Metadata",
                                  bold=True, size_pt=14, color_rgb=(20, 45, 80), is_bidi=is_fa)
    
    meta_lines = [
        (f"عنوان رساله: {meta.get('title', 'نامشخص')}", f"Title: {meta.get('title_en', meta.get('title', 'N/A'))}"),
        (f"پژوهشگر / دانشجو: {meta.get('student_name', 'نامشخص')} | استاد راهنما: {meta.get('supervisor', 'نامشخص')}",
         f"Candidate: {meta.get('student_name', 'N/A')} | Supervisor: {meta.get('supervisor', 'N/A')}"),
        (f"دانشگاه: {meta.get('university', 'دانشگاه تهران')} | مقطع: {meta.get('degree', 'کارشناسی ارشد')}",
         f"Institution: {meta.get('university', 'N/A')} | Degree: {meta.get('degree', 'N/A')}")
    ]
    for m_fa, m_en in meta_lines:
        add_styled_paragraph(doc, m_fa if is_fa else m_en, size_pt=11, color_rgb=(50, 50, 50),
                             space_after=4, is_bidi=is_fa)

    add_styled_paragraph(doc, "", space_after=12)

    # Domain Findings Tables
    domains = [
        ("hypothesis_alignment", "۲. ممیزی همخوانی فرضیه‌ها، یافته‌ها و بحث", "2. Hypothesis-Result-Discussion Alignment"),
        ("methodology_statistics", "۳. ممیزی انطباق روش‌شناسی و درجات آزادی آماری", "3. Methodology & Statistical Consistency"),
        ("citations_bibliography", "۴. صحت‌سنجی دوطرفه ارجاعات درون‌متنی و منابع", "4. Citation & Bibliography Reconciliation"),
        ("apa7_formatting", "۵. رعایت استانداردهای نگارش آماری APA 7th Edition", "5. APA 7th Edition Formatting Compliance"),
        ("adversarial_defense", "۶. شبیه‌سازی ارزیابی تخاصمی داوران و آمادگی جلسه دفاع", "6. Adversarial Defense & Peer-Review Simulation"),
        ("equator_compliance", "۷. انطباق با راهنماهای گزارش‌دهی استاندارد بین‌المللی (EQUATOR Compliance)", "7. International EQUATOR Reporting Checklist Compliance")
    ]

    for domain_key, domain_title_fa, domain_title_en in domains:
        dom_findings = [f for f in findings if f["domain"] == domain_key]
        add_styled_paragraph(doc, domain_title_fa if is_fa else domain_title_en,
                             bold=True, size_pt=13, color_rgb=(20, 45, 80), space_after=6, is_bidi=is_fa)

        if not dom_findings:
            no_err_msg = "هیچ مغایرت یا خطایی در این بخش مشاهده نشد و انطباق کامل تایید می‌گردد." if is_fa else "No discrepancies found in this domain. Complete consistency verified."
            add_styled_paragraph(doc, f"✓ {no_err_msg}", italic=True, size_pt=10, color_rgb=(30, 120, 60), space_after=10, is_bidi=is_fa)
            continue

        table = doc.add_table(rows=len(dom_findings) + 1, cols=4)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        make_table_apa7(table, is_bidi=is_fa)

        tbl_headers = [
            ("سطح اهمیت", "Severity"),
            ("شرح مغایرت", "Discrepancy Description"),
            ("مستندات و جزئیات", "Diagnostic Details"),
            ("راهکار و اقدام اصلاحی", "Actionable Fix")
        ]
        for col_idx, (h_fa, h_en) in enumerate(tbl_headers):
            cell = table.cell(0, col_idx)
            set_cell_shading(cell, "3A4B5C")
            set_cell_margins(cell, top=100, bottom=100)
            format_cell_text(cell, h_fa if is_fa else h_en, bold=True, size_pt=9.5, color_rgb=(255,255,255), is_bidi=is_fa)

        for row_idx, f in enumerate(dom_findings, start=1):
            sev = f["severity"]
            sev_colors = {
                "CRITICAL": (200, 30, 30),
                "MAJOR": (220, 100, 20),
                "MINOR": (70, 90, 120),
                "INFO": (50, 120, 60)
            }
            c_rgb = sev_colors.get(sev, (50, 50, 50))

            # Cell 0: Severity
            cell_0 = table.cell(row_idx, 0)
            set_cell_margins(cell_0, top=80, bottom=80)
            format_cell_text(cell_0, sev, bold=True, size_pt=9, color_rgb=c_rgb, is_bidi=is_fa)

            # Cell 1: Description
            desc_text = f["title_fa"] if is_fa else f["title_en"]
            cell_1 = table.cell(row_idx, 1)
            set_cell_margins(cell_1, top=80, bottom=80)
            format_cell_text(cell_1, desc_text, size_pt=9, align=WD_ALIGN_PARAGRAPH.RIGHT if is_fa else WD_ALIGN_PARAGRAPH.LEFT, is_bidi=is_fa)

            # Cell 2: Details
            detail_str = f["description_fa"] if is_fa else f["description_en"]
            cell_2 = table.cell(row_idx, 2)
            set_cell_margins(cell_2, top=80, bottom=80)
            format_cell_text(cell_2, detail_str, size_pt=8.5, align=WD_ALIGN_PARAGRAPH.RIGHT if is_fa else WD_ALIGN_PARAGRAPH.LEFT, is_bidi=is_fa)

            # Cell 3: Actionable Fix
            fix_text = f["recommendation_fa"] if is_fa else f["recommendation_en"]
            cell_3 = table.cell(row_idx, 3)
            set_cell_margins(cell_3, top=80, bottom=80)
            format_cell_text(cell_3, fix_text, size_pt=8.5, color_rgb=(20, 80, 40), align=WD_ALIGN_PARAGRAPH.RIGHT if is_fa else WD_ALIGN_PARAGRAPH.LEFT, is_bidi=is_fa)

        add_styled_paragraph(doc, "", space_after=12)

    # Detailed EQUATOR Checklist Table
    eq_items = getattr(auditor, "equator_checklist_results", [])
    if eq_items:
        eq_title = f"۸. ماتریس تفصیلی ارزیابی چک‌لیست {auditor.equator_guideline}" if is_fa else f"8. Detailed {auditor.equator_guideline} Reporting Checklist Matrix"
        add_styled_paragraph(doc, eq_title, bold=True, size_pt=13, color_rgb=(20, 45, 80), space_after=6, is_bidi=is_fa)

        eq_tbl = doc.add_table(rows=len(eq_items) + 1, cols=4)
        eq_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        make_table_apa7(eq_tbl, is_bidi=is_fa)

        eq_tbl_headers = [
            ("بند", "Item"),
            ("عنوان و الزام چک‌لیست", "Requirement Description"),
            ("وضعیت در متن", "Status"),
            ("توضیحات تشخیصی", "Diagnostic Notes")
        ]
        for col_idx, (h_fa, h_en) in enumerate(eq_tbl_headers):
            cell = eq_tbl.cell(0, col_idx)
            set_cell_shading(cell, "2B3A4A")
            set_cell_margins(cell, top=100, bottom=100)
            format_cell_text(cell, h_fa if is_fa else h_en, bold=True, size_pt=9.5, color_rgb=(255,255,255), is_bidi=is_fa)

        for row_idx, item in enumerate(eq_items, start=1):
            st = item["status"]
            status_colors = {
                "PRESENT": (30, 130, 60),
                "PARTIAL": (210, 130, 20),
                "MISSING": (190, 30, 30)
            }
            c_rgb = status_colors.get(st, (50, 50, 50))

            # Cell 0: ID
            c0 = eq_tbl.cell(row_idx, 0)
            set_cell_margins(c0, top=60, bottom=60)
            format_cell_text(c0, item["item_id"], bold=True, size_pt=9, is_bidi=is_fa)

            # Cell 1: Requirement
            req_text = item["name_fa"] if is_fa else item["name_en"]
            c1 = eq_tbl.cell(row_idx, 1)
            set_cell_margins(c1, top=60, bottom=60)
            format_cell_text(c1, req_text, size_pt=8.5, align=WD_ALIGN_PARAGRAPH.RIGHT if is_fa else WD_ALIGN_PARAGRAPH.LEFT, is_bidi=is_fa)

            # Cell 2: Status
            c2 = eq_tbl.cell(row_idx, 2)
            set_cell_margins(c2, top=60, bottom=60)
            format_cell_text(c2, st, bold=True, size_pt=9, color_rgb=c_rgb, is_bidi=is_fa)

            # Cell 3: Note
            note_str = item.get("note") or ("تایید شده" if st == "PRESENT" else "نیاز به درج")
            c3 = eq_tbl.cell(row_idx, 3)
            set_cell_margins(c3, top=60, bottom=60)
            format_cell_text(c3, note_str, size_pt=8, align=WD_ALIGN_PARAGRAPH.RIGHT if is_fa else WD_ALIGN_PARAGRAPH.LEFT, is_bidi=is_fa)

        add_styled_paragraph(doc, "", space_after=12)

    # Pre-Defense Checklist Section
    add_styled_paragraph(doc, "۹. چک‌لیست نهایی تایید پیش از دفاع (Pre-Defense Checklist)", bold=True, size_pt=13, color_rgb=(20, 45, 80), is_bidi=is_fa)
    chk_items = [
        "تمام فرضیات فصل اول دارای آزمون آماری مشخص در فصل چهارم و بحث در فصل پنجم هستند.",
        "درجات آزادی تحلیل کوواریانس و رگرسیون با کسر تعداد گروه‌ها و متغیرها از حجم نمونه دقیقاً منطبق است.",
        "هیچ ارجاع درون‌متنی سرگردان (Orphaned Citation) خارج از فهرست مراجع انتهای پایان‌نامه وجود ندارد.",
        "تمامی مقادیر احتمالاتی به صورت p < .001 قید شده و عبارت نرم‌افزاری p = .000 کاملاً حذف شده است.",
        "صفر قبل از ممیز در تمام ضرایب آماری مقید به بازه صفر تا یک (p, r, R², η²) حذف شده است.",
        f"بندهای الزامی چک‌لیست بین‌المللی {auditor.equator_guideline} به طور کامل در متن لحاظ گردیده است."
    ]
    for chk in chk_items:
        add_styled_paragraph(doc, f"☐  {chk}", size_pt=10, space_after=4, is_bidi=is_fa)

    doc.save(out_path)
    return out_path


def generate_citations_excel(auditor, out_path):
    wb = openpyxl.Workbook()
    # Default sheet
    ws_summary = wb.active
    ws_summary.title = "Overview & Summary"

    header_fill = PatternFill(start_color="2B3A4A", end_color="2B3A4A", fill_type="solid")
    header_font = Font(name="Arial", size=11, bold=True, color="FFFFFF")
    align_center = Alignment(horizontal="center", vertical="center")
    align_left = Alignment(horizontal="left", vertical="center")
    thin_border = Border(
        left=Side(style='thin', color='D0D0D0'),
        right=Side(style='thin', color='D0D0D0'),
        top=Side(style='thin', color='D0D0D0'),
        bottom=Side(style='thin', color='D0D0D0')
    )

    # Summary Sheet
    ws_summary.append(["Metric / Reconciliation Category", "Count", "Audit Status", "Action Required"])
    for col in range(1, 5):
        cell = ws_summary.cell(1, col)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = align_center

    ledger = auditor.audit_summary.get("citation_ledger_counts", {})
    summary_rows = [
        ("Matched Citations (Valid)", ledger.get("matched", 0), "VALID", "No action needed"),
        ("Orphaned In-Text Citations", ledger.get("orphaned_in_text", 0), "CRITICAL/MAJOR", "Add full bibliographic entry to References"),
        ("Ghost References in Bibliography", ledger.get("superfluous_bibliography", 0), "MAJOR/MINOR", "Cite in relevant section or remove"),
        ("Publication Year Mismatches", ledger.get("year_discrepancies", 0), "MINOR", "Harmonize publication year between text and references")
    ]
    for row in summary_rows:
        ws_summary.append(row)

    for r in range(2, 6):
        for c in range(1, 5):
            cell = ws_summary.cell(r, c)
            cell.border = thin_border
            cell.alignment = align_left if c != 2 else align_center

    # Sheet 2: Matched Citations
    ws_matched = wb.create_sheet(title="Matched Citations")
    ws_matched.append(["In-Text Citation", "Author", "Year", "Chapter", "Bibliography Reference"])
    for c in range(1, 6):
        cell = ws_matched.cell(1, c)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = align_center

    for item in getattr(auditor, "matched_citations", []):
        cit = item.get("in_text", {})
        ref = item.get("reference", {})
        ws_matched.append([cit.get("raw"), cit.get("author"), cit.get("year"), cit.get("chapter"), ref.get("raw")])

    # Sheet 3: Orphaned In-Text Citations
    ws_orphan = wb.create_sheet(title="Orphaned In-Text")
    ws_orphan.append(["In-Text Citation", "Author", "Year", "Chapter", "Issue", "Action"])
    for c in range(1, 7):
        cell = ws_orphan.cell(1, c)
        cell.fill = PatternFill(start_color="C0392B", end_color="C0392B", fill_type="solid")
        cell.font = header_font
        cell.alignment = align_center

    for cit in getattr(auditor, "orphaned_in_text", []):
        ws_orphan.append([cit.get("raw"), cit.get("author"), cit.get("year"), cit.get("chapter"),
                          "Missing from Bibliography", "Add full reference to Chapter 5 references"])

    # Sheet 4: Ghost Bibliography
    ws_ghost = wb.create_sheet(title="Ghost Bibliography")
    ws_ghost.append(["Bibliography Reference", "Author", "Year", "Issue", "Action"])
    for c in range(1, 6):
        cell = ws_ghost.cell(1, c)
        cell.fill = PatternFill(start_color="D35400", end_color="D35400", fill_type="solid")
        cell.font = header_font
        cell.alignment = align_center

    for ref in getattr(auditor, "superfluous_bib", []):
        ws_ghost.append([ref.get("raw"), ref.get("author"), ref.get("year"),
                         "Never cited in any chapter", "Cite in literature review or remove"])

    # Sheet 5: Year Discrepancies
    ws_year = wb.create_sheet(title="Year Mismatches")
    ws_year.append(["Author", "In-Text Year", "Bibliography Year", "In-Text Citation", "Bibliography Reference"])
    for c in range(1, 6):
        cell = ws_year.cell(1, c)
        cell.fill = PatternFill(start_color="2980B9", end_color="2980B9", fill_type="solid")
        cell.font = header_font
        cell.alignment = align_center

    for item in getattr(auditor, "year_discrepancies", []):
        cit = item.get("in_text", {})
        ref = item.get("reference", {})
        ws_year.append([cit.get("author"), item.get("year_in_text"), item.get("year_in_bib"), cit.get("raw"), ref.get("raw")])

    # Sheet 6: EQUATOR Reporting Checklist
    ws_eq = wb.create_sheet(title="EQUATOR Checklist")
    ws_eq.append(["Item ID", "Guideline", "Requirement (EN)", "Requirement (FA)", "Status", "Criticality", "Diagnostic Notes"])
    for c in range(1, 8):
        cell = ws_eq.cell(1, c)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = align_center

    eq_status_fills = {
        "PRESENT": PatternFill(start_color="27AE60", end_color="27AE60", fill_type="solid"),
        "PARTIAL": PatternFill(start_color="F39C12", end_color="F39C12", fill_type="solid"),
        "MISSING": PatternFill(start_color="C0392B", end_color="C0392B", fill_type="solid")
    }

    for eq_item in getattr(auditor, "equator_checklist_results", []):
        r_num = ws_eq.max_row + 1
        st = eq_item.get("status", "PARTIAL")
        ws_eq.append([
            eq_item.get("item_id"),
            auditor.equator_guideline,
            eq_item.get("name_en"),
            eq_item.get("name_fa"),
            st,
            eq_item.get("criticality"),
            eq_item.get("note") or ("Verified" if st == "PRESENT" else "Action required")
        ])
        st_cell = ws_eq.cell(r_num, 5)
        st_cell.fill = eq_status_fills.get(st, header_fill)
        st_cell.font = Font(name="Arial", size=10, bold=True, color="FFFFFF")
        st_cell.alignment = align_center

    # Adjust column widths
    for sheet in wb.worksheets:
        for col in sheet.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = get_column_letter(col[0].column)
            sheet.column_dimensions[col_letter].width = max(max_len + 3, 12)

    wb.save(out_path)
    return out_path


# ==============================================================================
# Main CLI Execution
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="Academic Thesis & Dissertation Integrity Auditor (Skill #20)")
    parser.add_argument("--json", required=True, help="Path to structured audit JSON payload")
    parser.add_argument("--out-dir", default="./thesis_audit_output", help="Output directory for reports")
    parser.add_argument("--lang", default="fa", choices=["fa", "en"], help="Output language: fa (Persian) or en (English)")
    parser.add_argument("--threshold", type=float, default=80.0, help="Passing Thesis Integrity Score (default: 80.0)")
    args = parser.parse_args()

    if not os.path.exists(args.json):
        print(f"Error: Payload file '{args.json}' does not exist.", file=sys.stderr)
        sys.exit(1)

    with open(args.json, "r", encoding="utf-8") as f:
        payload = json.load(f)

    os.makedirs(args.out_dir, exist_ok=True)

    print("================================================================================")
    print("           Academic Thesis & Dissertation Integrity Auditor Engine              ")
    print("================================================================================")
    print(f"[*] Ingesting Audit Payload: {args.json}")
    print(f"[*] Target Output Directory: {args.out_dir}")
    print(f"[*] Language Mode: {'Persian (فارسی)' if args.lang == 'fa' else 'English'}")

    auditor = ThesisIntegrityAuditor(payload)
    summary = auditor.audit_all()

    tis = summary["thesis_integrity_score"]
    srs = summary.get("submission_readiness_score", tis)
    counts = summary["finding_counts"]
    eq = summary.get("equator_audit", {})
    print(f"\n[+] Audit Analysis Completed:")
    print(f"    - Thesis Integrity Score (TIS): {tis:.1f}%")
    print(f"    - Submission Readiness Score (SRS): {srs:.1f}% (Grade: {summary.get('srs_grade', 'N/A')})")
    print(f"    - EQUATOR Compliance ({eq.get('guideline', 'EQUATOR')}): {eq.get('equator_score', 0):.1f}% "
          f"({eq.get('present_count', 0)} Present, {eq.get('partial_count', 0)} Partial, {eq.get('missing_count', 0)} Missing)")
    print(f"    - Defense Readiness Status: {summary['readiness_status_en']} / {summary['readiness_status_fa']}")
    print(f"    - Findings: {counts['critical']} Critical, {counts['major']} Major, {counts['minor']} Minor, {counts['info']} Info")
    print(f"    - Citation Reconciliation: {summary['citation_ledger_counts']['matched']} Matched, "
          f"{summary['citation_ledger_counts']['orphaned_in_text']} Orphaned, "
          f"{summary['citation_ledger_counts']['superfluous_bibliography']} Ghost Refs, "
          f"{summary['citation_ledger_counts']['year_discrepancies']} Year Mismatches")

    # Generate JSON summary
    summary_path = os.path.join(args.out_dir, "thesis_audit_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved Machine-Readable Audit Summary: {summary_path}")

    # Generate DOCX report
    docx_filename = "گزارش_جامع_ممیزی_و_صحت‌سنجی_رساله.docx" if args.lang == "fa" else "Thesis_Integrity_Audit_Report.docx"
    docx_path = os.path.join(args.out_dir, docx_filename)
    generate_audit_docx(auditor, docx_path, lang=args.lang)
    print(f"[+] Generated Publication-Grade Audit Report: {docx_path}")

    # Generate Excel ledger
    excel_path = os.path.join(args.out_dir, "annotated_citations.xlsx")
    generate_citations_excel(auditor, excel_path)
    print(f"[+] Generated Citation Reconciliation Matrix: {excel_path}")

    print("================================================================================")
    print(f"[*] Audit Finished. Final Score: {tis:.1f}% (Threshold: {args.threshold}%)")
    if tis >= args.threshold:
        print("[*] STATUS: PASSED - Pre-Defense Integrity Standards Verified.")
    else:
        print("[!] STATUS: ACTION REQUIRED - Discrepancies must be resolved before defense.")
    print("================================================================================")

if __name__ == "__main__":
    main()
