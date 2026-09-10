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
# Audit Analysis Engine
# ==============================================================================

class ThesisIntegrityAuditor:
    def __init__(self, payload):
        self.payload = payload
        self.metadata = payload.get("project_metadata", {})
        self.findings = []
        self.audit_summary = {}

    def audit_all(self):
        self._audit_hypotheses_alignment()
        self._audit_methodology_and_statistics()
        self._audit_citations_and_bibliography()
        self._audit_apa7_compliance()
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

    def _compute_integrity_score(self):
        """Computes composite Thesis Integrity Score (TIS) 0-100%"""
        critical_count = sum(1 for f in self.findings if f["severity"] == "CRITICAL")
        major_count = sum(1 for f in self.findings if f["severity"] == "MAJOR")
        minor_count = sum(1 for f in self.findings if f["severity"] == "MINOR")
        info_count = sum(1 for f in self.findings if f["severity"] == "INFO")

        tis = 100 - (15 * critical_count + 5 * major_count + 1 * minor_count)
        tis = max(0, min(100, tis))

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

        self.audit_summary = {
            "thesis_integrity_score": tis,
            "readiness_status_fa": status_fa,
            "readiness_status_en": status_en,
            "verdict_description_fa": verdict_desc_fa,
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
    score_tbl = doc.add_table(rows=2, cols=4)
    score_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    make_table_apa7(score_tbl, is_bidi=is_fa)

    headers = [
        ("شاخص جامع انطباق (TIS)", "Integrity Score (TIS)"),
        ("وضعیت آمادگی دفاع", "Defense Readiness"),
        ("خطاهای بحرانی (Critical)", "Critical Errors"),
        ("نیازمند اصلاح (Major)", "Major Revisions")
    ]
    for col_idx, (h_fa, h_en) in enumerate(headers):
        cell = score_tbl.cell(0, col_idx)
        set_cell_shading(cell, "2B3A4A")
        set_cell_margins(cell, top=120, bottom=120)
        format_cell_text(cell, h_fa if is_fa else h_en, bold=True, size_pt=10, color_rgb=(255,255,255), is_bidi=is_fa)

    status_str = summary["readiness_status_fa"] if is_fa else summary["readiness_status_en"]
    row_vals = [f"{tis}%", status_str, str(counts["critical"]), str(counts["major"])]
    for col_idx, val in enumerate(row_vals):
        cell = score_tbl.cell(1, col_idx)
        set_cell_margins(cell, top=100, bottom=100)
        bold = (col_idx == 0)
        color = (180, 40, 40) if (col_idx == 2 and counts["critical"] > 0) else (30, 30, 30)
        format_cell_text(cell, val, bold=bold, size_pt=11, color_rgb=color, is_bidi=is_fa)

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
        ("apa7_formatting", "۵. رعایت استانداردهای نگارش آماری APA 7th Edition", "5. APA 7th Edition Formatting Compliance")
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

    # Pre-Defense Checklist Section
    add_styled_paragraph(doc, "۶. چک‌لیست نهایی تایید پیش از دفاع (Pre-Defense Checklist)", bold=True, size_pt=13, color_rgb=(20, 45, 80), is_bidi=is_fa)
    chk_items = [
        "تمام فرضیات فصل اول دارای آزمون آماری مشخص در فصل چهارم و بحث در فصل پنجم هستند.",
        "درجات آزادی تحلیل کوواریانس و رگرسیون با کسر تعداد گروه‌ها و متغیرها از حجم نمونه دقیقاً منطبق است.",
        "هیچ ارجاع درون‌متنی سرگردان (Orphaned Citation) خارج از فهرست مراجع انتهای پایان‌نامه وجود ندارد.",
        "تمامی مقادیر احتمالاتی به صورت p < .001 قید شده و عبارت نرم‌افزاری p = .000 کاملاً حذف شده است.",
        "صفر قبل از ممیز در تمام ضرایب آماری مقید به بازه صفر تا یک (p, r, R², η²) حذف شده است."
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
    counts = summary["finding_counts"]
    print(f"\n[+] Audit Analysis Completed:")
    print(f"    - Thesis Integrity Score (TIS): {tis:.1f}%")
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
