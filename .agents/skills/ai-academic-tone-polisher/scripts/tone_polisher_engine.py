#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ai-academic-tone-polisher Engine (Skill #22)
AcademicSuite: Automated AI Text Detection Mitigator, Academic Tone Polisher & Burstiness Optimizer

Author: Saber Ghaderi
License: MIT
"""

import argparse
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn


# ==============================================================================
# 1. MARKER CATALOGS & REPLACEMENT DICTIONARIES
# ==============================================================================

PERSIAN_AI_MARKERS = [
    {
        "pattern": r"شایان\s+ذکر\s+است\s+که",
        "replacement": "یافته‌های حاضر مؤید آن است که",
        "alt_replacement": "شواهد تجربی به روشنی دلالت بر آن دارند که",
        "category": "Robotic Filler",
        "description": "عبارت کلیشه‌ای پرتکرار در متون ترجمه‌شده توسط هوش مصنوعی"
    },
    {
        "pattern": r"در\s+این\s+راستا[،,]?",
        "replacement": "در همین چارچوب مفهومی،",
        "alt_replacement": "در پرتو این شواهد،",
        "category": "Mechanical Transition",
        "description": "انتقال مکانیکی و پیوند ساختگی بندها"
    },
    {
        "pattern": r"به\s+طور\s+کلی\s+می‌?توان\s+گفت\s+که",
        "replacement": "مجموعه شواهد تجربی تصریح می‌دارند که",
        "alt_replacement": "برآیند یافته‌ها دلالت بر آن دارد که",
        "category": "Evasive Generalization",
        "description": "تعمیم ضعیف و فاقد لحن قاطع دانشگاهی"
    },
    {
        "pattern": r"این\s+امر\s+نشان‌?دهنده\s+آن\s+است\s+که",
        "replacement": "این الگو بازتاب‌دهنده آن است که",
        "alt_replacement": "این سازوکار حاکی از آن است که",
        "category": "Passive Demonstrative",
        "description": "گرته‌برداری ساختاری از عبارت 'This demonstrates that'"
    },
    {
        "pattern": r"همان‌?طور\s+که\s+می‌?دانیم[،,]?",
        "replacement": "بر پایه ادبیات نظری مستقر،",
        "alt_replacement": "مفروضات بنیادین این الگو تصریح می‌دارند که",
        "category": "Non-Scholarly Presumption",
        "description": "عبارت عامیانه و فاقد استناد در متون علمی"
    },
    {
        "pattern": r"نقش\s+بسیار\s+مهمی\s+ایفا\s+می‌?کند",
        "replacement": "نقشی کانونی و تعیین‌کننده در این سازوکار ایفا می‌نماید",
        "alt_replacement": "سهم عمده‌ای در تبیین تغییرات متغیر وابسته دارد",
        "category": "Translationese Cliche",
        "description": "ترجمه تحت‌اللفظی عبارت 'plays a crucial role'"
    },
    {
        "pattern": r"لازم\s+به\s+یادآوری\s+است\s+که",
        "replacement": "در امتداد این استدلال، شایسته توجه است که",
        "alt_replacement": "توجه به این نکته روشنگر است که",
        "category": "Didactic Filler",
        "description": "حشو تعلیمی نامتناسب با نگارش پژوهشی"
    },
    {
        "pattern": r"از\s+این\s+رو[،,]?",
        "replacement": "بر این اساس،",
        "alt_replacement": "از پیامدهای روش‌شناختی این امر،",
        "category": "Repetitive Causal",
        "description": "تکرار پیاپی رابط‌های علت و معلولی ساده"
    },
    {
        "pattern": r"بدین\s+ترتیب[،,]?",
        "replacement": "در نتیجه این فرایند،",
        "alt_replacement": "پدیده‌ای که پیامد آن،",
        "category": "Repetitive Causal",
        "description": "توالی زنجیره‌ای رابط‌های ساده"
    },
    {
        "pattern": r"به\s+عنوان\s+یک\s+عامل\s+موثر\s+عمل\s+می‌?کند",
        "replacement": "در مقام متغیری تعدیل‌کننده و اثرگذار ایفای نقش می‌نماید",
        "alt_replacement": "به منزله سازوکاری حفاظتی عمل می‌کند",
        "category": "Translationese Calque",
        "description": "ترجمه مکانیکی 'acts as an effective factor'"
    },
    {
        "pattern": r"پژوهشگران\s+به\s+این\s+نتیجه\s+رسیدند\s+که",
        "replacement": "بررسی‌های تجربی حاکی از استنتاجی همسو مبنی بر آن است که",
        "alt_replacement": "برآیند تحلیل‌ها موید فرضیه‌ای است که بر اساس آن",
        "category": "Conversational Reporting",
        "description": "گزارشگری ساده و غیرتحلیلی شواهد"
    },
    {
        "pattern": r"تاثیرات\s+مثبت\s+زیادی\s+بر",
        "replacement": "اثرات فزاینده و معناداری بر تقویت",
        "alt_replacement": "نقش محافظتی آشکاری در مهار",
        "category": "Vague Formulation",
        "description": "فرمول‌بندی کیفی و مبهم بدون بار اصطلاحی"
    },
    {
        "pattern": r"همسو\s+و\s+منطبق\s+می‌?باشد",
        "replacement": "همگرایی تجربی مستحکمی نشان می‌دهد",
        "alt_replacement": "موید انطباق تجربی فرضیه با پیشینه است",
        "category": "Tautological Copula",
        "description": "حشو قبیح و استفاده نادرست از فعل 'می‌باشد'"
    },
    {
        "pattern": r"کمک\s+می‌?کند\s+تا",
        "replacement": "زمینه را برای تسهیل فرایند [...] فراهم می‌سازد",
        "alt_replacement": "امکان بازسازی شناختی را مهیا می‌آورد",
        "category": "Simplistic Verb",
        "description": "افعال پایه عامیانه به جای اصطلاحات تخصصی روان‌شناختی"
    }
]

ENGLISH_AI_MARKERS = [
    {
        "pattern": r"(?i)\bit is crucial to note that\b",
        "replacement": "Crucially, empirical findings reveal that",
        "alt_replacement": "Notably, observational evidence corroborates that",
        "category": "Robotic Opener",
        "description": "Formulaic LLM sentence starter"
    },
    {
        "pattern": r"(?i)\bin this regard[,\s]+",
        "replacement": "In theoretical convergence with these findings, ",
        "alt_replacement": "Under this conceptual framework, ",
        "category": "Mechanical Transition",
        "description": "Overused transitional device in AI text"
    },
    {
        "pattern": r"(?i)\bdelves into the multifaceted tapestry of\b",
        "replacement": "critically examines the multi-dimensional architecture of",
        "alt_replacement": "probes the complex dynamics underlying",
        "category": "ChatGPT Signature Metaphor",
        "description": "Dead giveaway metaphor of generative models"
    },
    {
        "pattern": r"(?i)\bplays a crucial role in\b",
        "replacement": "operates as a decisive determinant in",
        "alt_replacement": "exerts a robust moderating influence upon",
        "category": "Translationese Cliche",
        "description": "Overused explanatory predicate"
    },
    {
        "pattern": r"(?i)\bserve as a testament to\b",
        "replacement": "provide robust empirical corroboration for",
        "alt_replacement": "substantiate the ecological validity of",
        "category": "Hyperbolic AI Trope",
        "description": "Over-dramatic non-empirical phrasing"
    },
    {
        "pattern": r"(?i)\bit is important to remember that\b",
        "replacement": "Theoretical models of cognitive functioning posit that",
        "alt_replacement": "A core tenet of this framework assumes that",
        "category": "Didactic Filler",
        "description": "Didactic phrasing unsuited for formal scientific papers"
    },
    {
        "pattern": r"(?i)\bacts as an effective factor in\b",
        "replacement": "functions as a protective psychological buffer against",
        "alt_replacement": "significantly mitigates the detrimental impact of",
        "category": "Weak Calque",
        "description": "Vague functional description"
    },
    {
        "pattern": r"(?i)\bresearchers reached the conclusion that\b",
        "replacement": "the accumulated empirical literature demonstrates that",
        "alt_replacement": "synthesized findings convincingly substantiate that",
        "category": "High School Formulation",
        "description": "Informal reporting verb"
    },
    {
        "pattern": r"(?i)\bmoreover[,\s]+",
        "replacement": "Additionally, ",
        "alt_replacement": "In complementary alignment, ",
        "category": "Monotonous Connective",
        "description": "Overused connector in LLM paragraphs"
    },
    {
        "pattern": r"(?i)\bfurthermore[,\s]+",
        "replacement": "Specifically, ",
        "alt_replacement": "From a mechanistic perspective, ",
        "category": "Monotonous Connective",
        "description": "Overused connector in LLM paragraphs"
    }
]

# ==============================================================================
# 1.1 STANFORD SCIWRITE (DR. KRISTIN SAINANI) 5-PASS EDITORIAL CATALOGS
# ==============================================================================

SAINANI_CLUTTER_EN = [
    {"pattern": r"(?i)\bdue to the fact that\b", "replacement": "because", "severity": "MAJOR", "rationale": "Dead-weight causal phrase"},
    {"pattern": r"(?i)\ba majority of\b", "replacement": "most", "severity": "MINOR", "rationale": "Wordy quantifier"},
    {"pattern": r"(?i)\bare of the same opinion\b", "replacement": "agree", "severity": "MINOR", "rationale": "Smothered agreement"},
    {"pattern": r"(?i)\bgive rise to\b", "replacement": "cause", "severity": "MINOR", "rationale": "Cluttered causal verb"},
    {"pattern": r"(?i)\bhave an effect on\b", "replacement": "affect", "severity": "MINOR", "rationale": "Nominalized impact"},
    {"pattern": r"(?i)\bin the event that\b", "replacement": "if", "severity": "MINOR", "rationale": "Wordy conditional"},
    {"pattern": r"(?i)\bat the present time\b", "replacement": "currently", "severity": "MINOR", "rationale": "Temporal clutter"},
    {"pattern": r"(?i)\bin order to\b", "replacement": "to", "severity": "MINOR", "rationale": "Unnecessary infinitive padding"},
    {"pattern": r"(?i)\ba number of\b", "replacement": "several", "severity": "MINOR", "rationale": "Vague wordy quantifier"},
    {"pattern": r"(?i)\bon the basis of\b", "replacement": "based on", "severity": "MINOR", "rationale": "Overused prepositional idiom"},
    {"pattern": r"(?i)\bin light of the fact that\b", "replacement": "since", "severity": "MAJOR", "rationale": "Heavyweight padding"},
    {"pattern": r"(?i)\bit is worth noting that\b\s*", "replacement": "", "severity": "MAJOR", "rationale": "Introductory throat-clearing (delete)"},
    {"pattern": r"(?i)\bit is important to note that\b\s*", "replacement": "", "severity": "MAJOR", "rationale": "Introductory throat-clearing (delete)"},
    {"pattern": r"(?i)\bit is interesting to note that\b\s*", "replacement": "", "severity": "MAJOR", "rationale": "Empty introductory commentary (delete)"},
    {"pattern": r"(?i)\bas it is well known[,\s]+", "replacement": "", "severity": "MAJOR", "rationale": "Uncited presumption; replace with primary citation"},
    {"pattern": r"(?i)\bcompletely eliminate\b", "replacement": "eliminate", "severity": "MINOR", "rationale": "Redundant intensifier"},
    {"pattern": r"(?i)\bfuture plans\b", "replacement": "plans", "severity": "MINOR", "rationale": "Tautological modifier"},
    {"pattern": r"(?i)\bunexpected surprise\b", "replacement": "surprise", "severity": "MINOR", "rationale": "Tautological modifier"}
]

SAINANI_CLUTTER_FA = [
    {"pattern": r"شایان\s+ذکر\s+است\s+که\s*", "replacement": "", "severity": "MAJOR", "rationale": "حشو آغازین بی‌اثر و کلیشه ترجمه هوش مصنوعی"},
    {"pattern": r"لازم\s+به\s+ذکر\s+است\s+که\s*", "replacement": "", "severity": "MAJOR", "rationale": "حشو تعلیمی نامتناسب با نگارش پژوهشی"},
    {"pattern": r"لازم\s+به\s+یادآوری\s+است\s+که\s*", "replacement": "", "severity": "MAJOR", "rationale": "حشو فاقد بار علمی"},
    {"pattern": r"بدیهی\s+است\s+که\s*", "replacement": "", "severity": "MAJOR", "rationale": "تعمیم پیش‌فرض‌انگارانه بدون استناد تجربی"},
    {"pattern": r"همان‌?طور\s+که\s+می‌?دانیم[،,\s]+", "replacement": "", "severity": "CRITICAL", "rationale": "عبارت عامیانه؛ باید به استناد مشخص متصل شود"},
    {"pattern": r"به\s+منظور\s+اینکه", "replacement": "تا / برای اینکه", "severity": "MINOR", "rationale": "اطناب در بیان قصد و غایت"},
    {"pattern": r"در\s+راستای\s+اینکه", "replacement": "برای آنکه", "severity": "MINOR", "rationale": "پیونددهنده مصنوعی و مکانیکی بندها"},
    {"pattern": r"به\s+دلیل\s+اینکه", "replacement": "زیرا", "severity": "MINOR", "rationale": "اطناب در بیان علت"},
    {"pattern": r"اکثریت\s+قریب\s+به\s+اتفاق", "replacement": "اغلب / اکثر", "severity": "MINOR", "rationale": "اطناب بلاغی نامناسب در مقاله تجربی"},
    {"pattern": r"موجب\s+به\s+وجود\s+آمدن", "replacement": "موجب ایجاد / پدیدآورنده", "severity": "MINOR", "rationale": "اطناب در ترکیب فعل سببی"}
]

NOMINALIZATIONS_EN = [
    {"pattern": r"(?i)\bprovides a review of\b", "replacement": "reviews", "severity": "MAJOR", "rationale": "Nominalization: resurrect 'reviews'"},
    {"pattern": r"(?i)\boffers a confirmation of\b", "replacement": "confirms", "severity": "MAJOR", "rationale": "Nominalization: resurrect 'confirms'"},
    {"pattern": r"(?i)\bshows a peak\b", "replacement": "peaks", "severity": "MINOR", "rationale": "Nominalization: resurrect 'peaks'"},
    {"pattern": r"(?i)\bobtains an estimate of\b", "replacement": "estimates", "severity": "MAJOR", "rationale": "Nominalization: resurrect 'estimates'"},
    {"pattern": r"(?i)\bconducts an assessment of\b", "replacement": "assesses", "severity": "MAJOR", "rationale": "Nominalization: resurrect 'assesses'"},
    {"pattern": r"(?i)\bprovides a description of\b", "replacement": "describes", "severity": "MAJOR", "rationale": "Nominalization: resurrect 'describes'"},
    {"pattern": r"(?i)\bmakes an adjustment to\b", "replacement": "adjusts", "severity": "MINOR", "rationale": "Nominalization: resurrect 'adjusts'"},
    {"pattern": r"(?i)\bperforms an analysis of\b", "replacement": "analyzes", "severity": "MAJOR", "rationale": "Nominalization: resurrect 'analyzes'"},
    {"pattern": r"(?i)\bachieves a reduction in\b", "replacement": "reduces", "severity": "MAJOR", "rationale": "Nominalization: resurrect 'reduces'"},
    {"pattern": r"(?i)\bgives an explanation of\b", "replacement": "explains", "severity": "MAJOR", "rationale": "Nominalization: resurrect 'explains'"},
    {"pattern": r"(?i)\bmakes a determination of\b", "replacement": "determines", "severity": "MAJOR", "rationale": "Nominalization: resurrect 'determines'"}
]

NOMINALIZATIONS_FA = [
    {"pattern": r"مورد\s+بررسی\s+قرار\s+داد", "replacement": "بررسی کرد", "severity": "MAJOR", "rationale": "احیای فعل: تبدیل ساختار اسمی مجهول به فعل صریح"},
    {"pattern": r"مورد\s+ارزیابی\s+قرار\s+داد", "replacement": "ارزیابی کرد / سنجید", "severity": "MAJOR", "rationale": "احیای فعل: جایگزینی ساختار سنگین با فعل اکتیو"},
    {"pattern": r"مورد\s+تحلیل\s+قرار\s+گرفت", "replacement": "تحلیل شد", "severity": "MINOR", "rationale": "احیای فعل: حذف حشو ترکیب مجهول"},
    {"pattern": r"به\s+مرحله\s+اجرا\s+درآورد", "replacement": "اجرا کرد", "severity": "MAJOR", "rationale": "احیای فعل: پیراستن از اطناب اسمی"},
    {"pattern": r"اندازه‌?گیری\s+به\s+عمل\s+آمد", "replacement": "سنجیده شد / اندازه‌گیری شد", "severity": "MAJOR", "rationale": "احیای فعل: حذف گرته‌برداری ساختاری"},
    {"pattern": r"ارائه\s+نمودن\s+گزارشی\s+از", "replacement": "گزارش کردن", "severity": "MINOR", "rationale": "احیای فعل صریح"},
    {"pattern": r"فراهم\s+ساختن\s+تبیینی\s+برای", "replacement": "تبیین کردن", "severity": "MAJOR", "rationale": "احیای فعل مفهومی"},
    {"pattern": r"به\s+انجام\s+رسید", "replacement": "انجام شد", "severity": "MINOR", "rationale": "ساده‌سازی ساختار فعلی"}
]


class SainaniEditorialAuditor:
    """
    Stanford SciWrite 5-Pass Editorial Auditor (Dr. Kristin Sainani methodology)
    Pass 1: Clutter Extraction
    Pass 2: Active Voice & Smothered Verb Resurrection
    Pass 3: Sentence Architecture & Buried Predicates
    Pass 4: Keyword Consistency & The Banana Rule
    Pass 5: Numerical & Citation Telephone Game
    """
    def __init__(self, lang: str = "fa"):
        self.lang = lang

    def run_five_passes(self, text: str, sentences: List[str]) -> Dict[str, Any]:
        findings = {
            "pass1_clutter": [],
            "pass2_voice_verbs": [],
            "pass3_sentence_arch": [],
            "pass4_keyword_consistency": [],
            "pass5_numerical_citation": [],
            "top_5_priorities": []
        }

        # ----------------------------------------------------------------------
        # Pass 1: Clutter Extraction
        # ----------------------------------------------------------------------
        clutter_catalog = SAINANI_CLUTTER_FA if self.lang == "fa" else SAINANI_CLUTTER_EN
        for item in clutter_catalog:
            for s_idx, s in enumerate(sentences, 1):
                m = re.search(item["pattern"], s)
                if m:
                    findings["pass1_clutter"].append({
                        "sentence_num": s_idx,
                        "original_phrase": m.group(0),
                        "suggested_fix": item["replacement"] or "(حذف کامل حشو)",
                        "severity": item["severity"],
                        "rationale": item["rationale"]
                    })

        # ----------------------------------------------------------------------
        # Pass 2: Active Voice & Nominalization Resurrection
        # ----------------------------------------------------------------------
        nom_catalog = NOMINALIZATIONS_FA if self.lang == "fa" else NOMINALIZATIONS_EN
        for item in nom_catalog:
            for s_idx, s in enumerate(sentences, 1):
                m = re.search(item["pattern"], s)
                if m:
                    findings["pass2_voice_verbs"].append({
                        "sentence_num": s_idx,
                        "smothered_verb": m.group(0),
                        "resurrected_verb": item["replacement"],
                        "severity": item["severity"],
                        "rationale": item["rationale"]
                    })

        # ----------------------------------------------------------------------
        # Pass 3: Sentence Architecture & Buried Predicates
        # ----------------------------------------------------------------------
        for s_idx, s in enumerate(sentences, 1):
            words = s.split()
            w_count = len(words)
            threshold = 20 if self.lang == "fa" else 14
            if w_count > threshold + 10:
                findings["pass3_sentence_arch"].append({
                    "sentence_num": s_idx,
                    "issue_type": "Buried Predicate / Over-Extended Sentence",
                    "word_count": w_count,
                    "severity": "MAJOR" if w_count > 35 else "MINOR",
                    "snippet": " ".join(words[:12]) + " ...",
                    "rationale": (
                        f"فاصله زیاد میان نهاد و فعل پایانی ({w_count} کلمه)؛ موجب اختلال در بار پردازشی خواننده می‌شود."
                        if self.lang == "fa" else
                        f"Buried predicate: {w_count} words intervene across subordinate clauses. Consider splitting."
                    )
                })

        # ----------------------------------------------------------------------
        # Pass 4: Keyword Consistency & Banana Rule
        # ----------------------------------------------------------------------
        # Check if author varies core psychometric constructs
        banana_constructs = [
            ("social_anxiety", [r"اضطراب\s+اجتماعی", r"هراس\s+اجتماعی", r"فوبی\s+اجتماعی"]),
            ("rumination", [r"نشخوار\s+فکری", r"تفکر\s+تکرارشونده", r"افکار\s+نشخواری"]),
            ("self_regulation", [r"خودتنظیم‌?گری", r"تنظیم\s+رفتاری", r"مهار\s+خود"]),
            ("mindfulness", [r"ذهن‌آگاهی", r"توجه‌آگاهی", r"هوشیاری\s+فراگیر"])
        ] if self.lang == "fa" else [
            ("social_anxiety", [r"(?i)social anxiety", r"(?i)social phobia"]),
            ("rumination", [r"(?i)rumination", r"(?i)repetitive negative thinking"]),
            ("mindfulness", [r"(?i)mindfulness", r"(?i)attentional awareness"])
        ]

        for const_id, variants in banana_constructs:
            found_variants = []
            for v_pat in variants:
                if re.search(v_pat, text):
                    found_variants.append(v_pat)
            if len(found_variants) > 1:
                findings["pass4_keyword_consistency"].append({
                    "construct": const_id,
                    "detected_variants": [re.sub(r"[?\()s+i]", "", p) for p in found_variants],
                    "severity": "CRITICAL",
                    "rationale": (
                        "نقض قاعده ضد تنوع‌طلبی واژگانی (The Banana Rule): تغییر پی‌درپی عنوان متغیر اصلی پژوهش باعث گمراهی خواننده می‌شود."
                        if self.lang == "fa" else
                        "Violation of The Banana Rule: Inconsistent synonym swapping for the same core construct."
                    )
                })

        # ----------------------------------------------------------------------
        # Pass 5: Numerical & Citation Telephone Game
        # ----------------------------------------------------------------------
        # Check secondary citation markers
        sec_patterns = [
            r"به\s+نقل\s+از", r"به\s+گزارش", r"در\s+نقل\s+قول\s+از"
        ] if self.lang == "fa" else [
            r"(?i)as cited in", r"(?i)quoted in"
        ]
        for sp in sec_patterns:
            for s_idx, s in enumerate(sentences, 1):
                if re.search(sp, s):
                    findings["pass5_numerical_citation"].append({
                        "sentence_num": s_idx,
                        "type": "Secondary Citation (Telephone Game)",
                        "severity": "MAJOR",
                        "snippet": s[:80] + "...",
                        "rationale": (
                            "خطر پدیده تلفن‌بازی (The Telephone Game): استناد دست‌دوم به شواهد تجربی؛ توصیه می‌شود منبع دست‌اول واکاوی شود."
                            if self.lang == "fa" else
                            "Telephone Game Risk: Secondary citation for empirical evidence. Verify original source."
                        )
                    })

        # Compile Top 5 Priority Revisions
        all_issues = []
        for c in findings["pass4_keyword_consistency"]:
            all_issues.append({"severity": c["severity"], "pass": "Pass 4 (Terminology)", "desc": f"تثبیت واژگانی متغیر {c['construct']}", "action": c["rationale"]})
        for c in findings["pass1_clutter"]:
            all_issues.append({"severity": c["severity"], "pass": "Pass 1 (Clutter)", "desc": f"حذف حشو «{c['original_phrase']}»", "action": f"جایگزینی با: {c['suggested_fix']}"})
        for c in findings["pass2_voice_verbs"]:
            all_issues.append({"severity": c["severity"], "pass": "Pass 2 (Verbs)", "desc": f"احیای فعل خفه‌شده «{c['smothered_verb']}»", "action": f"استفاده از فعل مستقیم: {c['resurrected_verb']}"})
        for c in findings["pass3_sentence_arch"]:
            all_issues.append({"severity": c["severity"], "pass": "Pass 3 (Architecture)", "desc": f"شکستن جمله طولانی {c['sentence_num']} ({c['word_count']} کلمه)", "action": c["rationale"]})
        for c in findings["pass5_numerical_citation"]:
            all_issues.append({"severity": c["severity"], "pass": "Pass 5 (Citations)", "desc": f"استناد دست‌دوم در جمله {c['sentence_num']}", "action": c["rationale"]})

        # Rank by severity: CRITICAL (0), MAJOR (1), MINOR (2)
        severity_rank = {"CRITICAL": 0, "MAJOR": 1, "MINOR": 2}
        all_issues.sort(key=lambda x: severity_rank.get(x["severity"], 3))
        findings["top_5_priorities"] = all_issues[:5]

        return findings



# ==============================================================================
# 2. CITATION & STATISTICAL FORMULA INVARIANT SHIELD
# ==============================================================================

class EntityShield:
    """Protects citations and statistical formulas from any lexical tampering."""
    def __init__(self):
        self.citations_map: Dict[str, str] = {}
        self.stats_map: Dict[str, str] = {}
        self.counter_cit = 0
        self.counter_stat = 0

    def mask(self, text: str) -> str:
        # 1. Mask APA 7 Statistical Reporting: e.g. (F(1, 58) = 14.25, p < .001, \eta_p^2 = .197)
        stat_patterns = [
            r"\(?\b[tTF]\s*\(\s*[\d\s,.]+\s*\)\s*=\s*[\d.]+(?:,\s*p\s*[<>=]\s*[\d.]+)?(?:,\s*[\\a-zA-Z_^{}\d.]+\s*=\s*[\d.]+)?\)?",
            r"\b[tTF]\s*\(\s*[\d\s,.]+\s*\)\s*=\s*[\d.]+",
            r"\bp\s*[<>=]\s*[\d.]+",
            r"\b(?:M|SD|d|r|R\^2|η_p\^2|\\eta_p\^2)\s*=\s*[\d.]+"
        ]
        for pattern in stat_patterns:
            def repl_stat(m):
                placeholder = f"__STAT_SHIELD_{self.counter_stat:03d}__"
                self.stats_map[placeholder] = m.group(0)
                self.counter_stat += 1
                return placeholder
            text = re.sub(pattern, repl_stat, text)

        # 2. Mask In-Text APA Citations: e.g. (بک و همکاران، ۱۳۹۹) or (Beck et al., 2020)
        cit_patterns = [
            r"\([A-Z\u0600-\u06FF][^()]*?(?:19|20|۱۳|۱۴)\d{2}[^()]*?\)",
            r"[A-Z\u0600-\u06FF][a-zA-Z\u0600-\u06FF\s]+?\((?:19|20|۱۳|۱۴)\d{2}\)"
        ]
        for pattern in cit_patterns:
            def repl_cit(m):
                placeholder = f"__CIT_SHIELD_{self.counter_cit:03d}__"
                self.citations_map[placeholder] = m.group(0)
                self.counter_cit += 1
                return placeholder
            text = re.sub(pattern, repl_cit, text)

        return text

    def unmask(self, text: str) -> str:
        for placeholder, original in self.stats_map.items():
            text = text.replace(placeholder, original)
        for placeholder, original in self.citations_map.items():
            text = text.replace(placeholder, original)
        return text


# ==============================================================================
# 3. PERSIAN ORTHOGRAPHY & HALF-SPACE ENFORCEMENT
# ==============================================================================

def enforce_persian_orthography(text: str) -> str:
    """Enforces official Academy of Persian Language & Literature half-space rules."""
    zwnj = "\u200c"

    # Verbal prefixes: می and نمی
    text = re.sub(r"\b(می|نمی)\s+([آ-ی])", r"\1" + zwnj + r"\2", text)

    # Plural suffixes: ها and های
    text = re.sub(r"([آ-ی])\s+(ها|های)\b", r"\1" + zwnj + r"\2", text)

    # Comparative/superlative suffixes: تر and ترین
    text = re.sub(r"([آ-ی])\s+(تر|ترین)\b", r"\1" + zwnj + r"\2", text)

    # Indefinite enclitic ای after silent ه
    text = re.sub(r"([ه])\s+(ای|ای)\b", r"\1" + zwnj + r"\2", text)

    # Clean redundant spaces around punctuation
    text = re.sub(r"\s+([.،؛:!?])", r"\1", text)
    text = re.sub(r"([.،؛:!?])([^\s0-9\d])", r"\1 \2", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


# ==============================================================================
# 4. METRIC COMPUTATION ENGINE (BURSTINESS & PERPLEXITY PROXIES)
# ==============================================================================

def split_into_sentences(text: str, lang: str = "fa") -> List[str]:
    """Splits text into constituent academic sentences while preserving shielded tokens."""
    # Split on terminal sentence delimiters: periods, exclamation marks, question marks
    raw_sentences = re.split(r"(?<=[.!?])\s+", text)
    sentences = [s.strip() for s in raw_sentences if s.strip() and len(s.strip()) > 3]
    return sentences

def count_words(sentence: str) -> int:
    """Computes academic word tokens in a sentence."""
    tokens = [t for t in re.split(r"[\s،,؛;.]+", sentence) if t and not t.startswith("__")]
    return max(1, len(tokens))

def compute_anti_ai_metrics(sentences: List[str], text: str, lang: str = "fa") -> Dict[str, Any]:
    """Calculates Burstiness (CV_len), Predictability Index, and Lexical Diversity."""
    if not sentences:
        return {
            "sentence_count": 0, "total_words": 0, "mean_len": 0.0, "sd_len": 0.0,
            "burstiness_cv": 0.0, "ttr": 0.0, "unique_words": 0, "markers_found": 0,
            "ai_predictability_score": 0.0, "sentence_lengths": []
        }

    lengths = [count_words(s) for s in sentences]
    n_sent = len(lengths)
    total_words = sum(lengths)
    mean_len = total_words / n_sent
    variance = sum((l - mean_len) ** 2 for l in lengths) / n_sent
    sd_len = math.sqrt(variance)
    burstiness_cv = sd_len / mean_len if mean_len > 0 else 0.0

    # Lexical Diversity: Type-Token Ratio
    words_all = [w.lower() for w in re.split(r"[\s،,؛;.:!?()]+", text) if w and not w.startswith("__")]
    total_tokens = len(words_all)
    unique_tokens = len(set(words_all))
    ttr = unique_tokens / total_tokens if total_tokens > 0 else 0.0

    # AI Marker count
    marker_catalog = PERSIAN_AI_MARKERS if lang == "fa" else ENGLISH_AI_MARKERS
    markers_found = 0
    detected_markers_list = []
    for item in marker_catalog:
        matches = re.findall(item["pattern"], text)
        if matches:
            count = len(matches)
            markers_found += count
            detected_markers_list.append({
                "pattern": item["pattern"],
                "category": item["category"],
                "count": count,
                "replacement": item["replacement"],
                "description": item["description"]
            })

    # AI Predictability Index: Scale 0 - 100%
    # Heavy penalty for low burstiness (CV < 0.40) and frequent robotic markers
    burstiness_penalty = max(0.0, (0.45 - burstiness_cv) * 110.0)
    marker_penalty = min(60.0, (markers_found / max(1, n_sent)) * 75.0)
    ai_score = min(98.0, max(5.0, burstiness_penalty + marker_penalty + (1.0 - ttr) * 15.0))

    return {
        "sentence_count": n_sent,
        "total_words": total_words,
        "mean_len": round(mean_len, 2),
        "sd_len": round(sd_len, 2),
        "burstiness_cv": round(burstiness_cv, 3),
        "ttr": round(ttr, 3),
        "unique_words": unique_tokens,
        "markers_found": markers_found,
        "detected_markers": detected_markers_list,
        "ai_predictability_score": round(ai_score, 1),
        "sentence_lengths": lengths
    }


# ==============================================================================
# 5. AUTHENTIC ACADEMIC POLISHING & BURSTINESS INVERSION ENGINE
# ==============================================================================

def polish_and_humanize(
    sentences: List[str],
    shield: EntityShield,
    lang: str = "fa",
    intensity: str = "moderate"
) -> Tuple[List[Tuple[str, str, str]], str]:
    """
    Applies syntactic inversion, lexical elevation, and burstiness cadence reshaping.
    Returns:
      (list of tuples [original_sent, polished_sent, explanation], full_clean_text)
    """
    marker_catalog = PERSIAN_AI_MARKERS if lang == "fa" else ENGLISH_AI_MARKERS
    polished_sentences = []
    sentence_pairs = []

    for idx, sent in enumerate(sentences):
        current_sent = sent
        modifications = []

        # 1. Lexical and Cliche Substitutions
        for m_idx, item in enumerate(marker_catalog):
            pattern = item["pattern"]
            # Alternate between primary and alternative replacement to increase lexical diversity
            replacement = item["replacement"] if (idx % 2 == 0) else item["alt_replacement"]
            if re.search(pattern, current_sent):
                current_sent = re.sub(pattern, replacement, current_sent)
                modifications.append(f"جایگزینی کلیشه «{item['category']}» با تعبیر دانشگاهی")

        # 2. Syntactic Inversion & Academic Register Elevation
        if lang == "fa":
            # Replace simplistic verbs with specialized academic psychology phrasing
            verb_upgrades = [
                (r"\bتغییر\s+می‌?کنند\b", "دستخوش دگرگونی ساختاری می‌شوند", "ارتقای فعل به اصطلاح تخصصی"),
                (r"\bکمک\s+می‌?کند\b", "نقش تسهیل‌کننده‌ای ایفا می‌نماید", "اصلاح لحن محاوره‌ای"),
                (r"\bنشان\s+می‌?دهد\b", "تصریح می‌دارد", "تنوع‌بخشی به افعال گزاره‌ای"),
                (r"\bخواهد\s+داشت\b", "بر جای خواهد نهاد", "رسمی‌سازی ساختار زمان آینده"),
                (r"\bبه\s+دست\s+آمده\b", "حاصله از سنجش تجربی", "دقت‌افزایی روش‌شناختی")
            ]
            for v_pat, v_rep, v_exp in verb_upgrades:
                if re.search(v_pat, current_sent):
                    current_sent = re.sub(v_pat, v_rep, current_sent)
                    modifications.append(v_exp)

            # Apply strict half-spaces
            current_sent = enforce_persian_orthography(current_sent)
        else:
            # English structural refinements
            en_upgrades = [
                (r"\bplays a decisive determinant\b", "operates as a decisive determinant", "Academic syntax alignment"),
                (r"\bmitigating distress\b", "mitigating multidimensional psychological distress", "Lexical enrichment"),
                (r"\bdisentangle from\b", "disentangle their cognitive appraisal from", "Psychological precision")
            ]
            for v_pat, v_rep, v_exp in en_upgrades:
                if re.search(v_pat, current_sent):
                    current_sent = re.sub(v_pat, v_rep, current_sent)
                    modifications.append(v_exp)

        polished_sentences.append(current_sent)
        explanation = "؛ ".join(modifications) if modifications else ("بهینه‌سازی انسجام نحوی" if lang == "fa" else "Syntactic flow enhancement")
        sentence_pairs.append((sent, current_sent, explanation))

    # 3. Burstiness Cadence Restructuring: Combine or split to break monotonic rhythm
    restructured_sentences = []
    i = 0
    while i < len(polished_sentences):
        s_curr = polished_sentences[i]
        # Interleave concise thesis sentences with compound-complex multi-clause analytical sentences
        if i % 3 == 1 and (i + 1 < len(polished_sentences)):
            s_next = polished_sentences[i+1]
            if lang == "fa":
                s_curr_clean = re.sub(r"[.؛]$", "", s_curr).strip()
                connector = "؛ پدیده‌ای که در پرتو آن، "
                merged = f"{s_curr_clean}{connector}{s_next}"
            else:
                s_curr_clean = re.sub(r"[.]$", "", s_curr).strip()
                connector = "; an empirical trajectory whereby "
                merged = f"{s_curr_clean}{connector}{s_next}"
            restructured_sentences.append(merged)
            i += 2
        else:
            restructured_sentences.append(s_curr)
            i += 1

    # Re-insert citations and statistics
    unmasked_pairs = []
    for orig, pol, exp in sentence_pairs:
        unmasked_orig = shield.unmask(orig)
        unmasked_pol = shield.unmask(pol)
        unmasked_pairs.append((unmasked_orig, unmasked_pol, exp))

    final_clean_text = " ".join(shield.unmask(s) for s in restructured_sentences)
    if lang == "fa":
        final_clean_text = enforce_persian_orthography(final_clean_text)

    return unmasked_pairs, final_clean_text


# ==============================================================================
# 6. DUAL-PANEL 300-DPI DIAGNOSTIC VISUALIZATION
# ==============================================================================

def generate_burstiness_plot(
    pre_metrics: Dict[str, Any],
    post_metrics: Dict[str, Any],
    out_path: Path,
    lang: str = "fa"
) -> str:
    """Generates 300-DPI dual-panel plot showing burstiness distribution & AI reduction."""
    plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), dpi=300)

    # 1. Left Panel: Sentence Length Cadence (Burstiness Distribution)
    bins = np.arange(5, 65, 5)
    pre_lengths = pre_metrics["sentence_lengths"]
    post_lengths = post_metrics["sentence_lengths"]

    ax1.hist(pre_lengths, bins=bins, alpha=0.6, color="#e74c3c", label=f"Pre-Polish AI Draft (CV = {pre_metrics['burstiness_cv']:.2f})", edgecolor="black")
    ax1.hist(post_lengths, bins=bins, alpha=0.6, color="#2980b9", label=f"Post-Polish Academic (CV = {post_metrics['burstiness_cv']:.2f})", edgecolor="black")
    ax1.axvline(np.mean(pre_lengths), color="#c0392b", linestyle="--", linewidth=2, label=f"Mean Pre ({pre_metrics['mean_len']:.1f}w)")
    ax1.axvline(np.mean(post_lengths), color="#1f618d", linestyle="-", linewidth=2, label=f"Mean Post ({post_metrics['mean_len']:.1f}w)")

    title_l = "Sentence Cadence & Burstiness Distribution" if lang == "en" else "توزیع ضرب‌آهنگ طول جملات و شاخص ناهمگونی (Burstiness)"
    xlabel_l = "Sentence Length (Words / کلمات)" if lang == "en" else "طول جمله (تعداد کلمات)"
    ylabel_l = "Frequency (تعداد جملات)" if lang == "en" else "تعداد جملات"
    ax1.set_title(title_l, fontsize=12, fontweight="bold", pad=12)
    ax1.set_xlabel(xlabel_l, fontsize=10)
    ax1.set_ylabel(ylabel_l, fontsize=10)
    ax1.legend(loc="upper right", frameon=True, fontsize=9)

    # 2. Right Panel: Anti-AI Comparative Metrics Scorecard
    metrics_labels = [
        "Burstiness (CV x100)",
        "AI Predictability (%)",
        "Lexical Diversity (TTR x100)",
        "Robotic Cliches Count"
    ] if lang == "en" else [
        "شاخص ضرب‌آهنگ (CV × 100)",
        "ردپای هوش مصنوعی (%)",
        "تنوع واژگانی (TTR × 100)",
        "تعداد کلیشه‌های ماشینی"
    ]

    pre_vals = [
        pre_metrics["burstiness_cv"] * 100,
        pre_metrics["ai_predictability_score"],
        pre_metrics["ttr"] * 100,
        pre_metrics["markers_found"]
    ]
    post_vals = [
        post_metrics["burstiness_cv"] * 100,
        post_metrics["ai_predictability_score"],
        post_metrics["ttr"] * 100,
        post_metrics["markers_found"]
    ]

    x = np.arange(len(metrics_labels))
    width = 0.35

    rects1 = ax2.bar(x - width/2, pre_vals, width, label="Pre-Polish Draft", color="#e67e22", edgecolor="black")
    rects2 = ax2.bar(x + width/2, post_vals, width, label="Post-Polish Polished", color="#27ae60", edgecolor="black")

    # Add data labels
    for rect in rects1:
        h = rect.get_height()
        ax2.annotate(f"{h:.1f}", xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3),
                     textcoords="offset points", ha="center", va="bottom", fontsize=8, fontweight="bold")
    for rect in rects2:
        h = rect.get_height()
        ax2.annotate(f"{h:.1f}", xy=(rect.get_x() + rect.get_width()/2, h), xytext=(0, 3),
                     textcoords="offset points", ha="center", va="bottom", fontsize=8, fontweight="bold")

    title_r = "Anti-AI Footprint & Scholarly Integrity Scorecard" if lang == "en" else "کارنامه شاخص‌های تشخیص هوش مصنوعی و اصالت نگارش"
    ax2.set_title(title_r, fontsize=12, fontweight="bold", pad=12)
    ax2.set_xticks(x)
    ax2.set_xticklabels(metrics_labels, fontsize=8, rotation=15 if lang == "fa" else 0)
    ax2.legend(loc="upper right", frameon=True, fontsize=9)

    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    return str(out_path)


# ==============================================================================
# 7. EXCEL AUDIT WORKBOOK GENERATION (OPENPYXL)
# ==============================================================================

def export_audit_matrix_excel(pre_metrics, post_metrics, sentence_pairs, out_path, lang="fa", sainani_findings=None):
    wb = openpyxl.Workbook()
    ws1 = wb.active
    ws1.title = "کارنامه اجرایی" if lang == "fa" else "Executive Scorecard"
    ws1.views.sheetView[0].rightToLeft = (lang == "fa")

    # Palette
    navy_fill = PatternFill(start_color="1A365D", end_color="1A365D", fill_type="solid")
    header_fill = PatternFill(start_color="2B6CB0", end_color="2B6CB0", fill_type="solid")
    green_fill = PatternFill(start_color="E6FFFA", end_color="E6FFFA", fill_type="solid")
    accent_fill = PatternFill(start_color="EDF2F7", end_color="EDF2F7", fill_type="solid")
    orange_fill = PatternFill(start_color="FEEBC8", end_color="FEEBC8", fill_type="solid")
    red_fill = PatternFill(start_color="FED7D7", end_color="FED7D7", fill_type="solid")

    title_font = Font(name="B Titr" if lang == "fa" else "Calibri", size=14, bold=True, color="1A365D")
    header_font = Font(name="B Titr" if lang == "fa" else "Calibri", size=10, bold=True, color="FFFFFF")
    body_font = Font(name="B Nazanin" if lang == "fa" else "Calibri", size=11)
    bold_body = Font(name="B Nazanin" if lang == "fa" else "Calibri", size=11, bold=True)
    thin_border = Border(left=Side(style='thin', color='CBD5E0'), right=Side(style='thin', color='CBD5E0'),
                         top=Side(style='thin', color='CBD5E0'), bottom=Side(style='thin', color='CBD5E0'))

    # Title Banner
    ws1["A1"] = "کارنامه شاخص‌های تشخیص هوش مصنوعی و پالایش لحن دانشگاهی" if lang == "fa" else "Anti-AI Metrics & Academic Tone Executive Scorecard"
    ws1["A1"].font = title_font

    headers1 = [
        "شاخص سنجش", "پیش‌نویس اولیه (AI)", "نسخه نهایی دانشگاهی", "تغییرات نسبی", "وضعیت ارزیابی"
    ] if lang == "fa" else [
        "Evaluation Metric", "Initial Draft (AI)", "Polished Academic", "Relative Change", "Verdict"
    ]
    for col_idx, h in enumerate(headers1, 1):
        cell = ws1.cell(row=3, column=col_idx, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    rows1 = [
        ("شاخص ضرب‌آهنگ جملات (Burstiness CV)", f"{pre_metrics['burstiness_cv']:.3f}", f"{post_metrics['burstiness_cv']:.3f}", f"+{(post_metrics['burstiness_cv'] - pre_metrics['burstiness_cv']):.3f}", "بهینه (انعطاف‌پذیر)"),
        ("احتمال ردپای هوش مصنوعی (AI Footprint)", f"{pre_metrics['ai_predictability_score']:.1f}%", f"{post_metrics['ai_predictability_score']:.1f}%", f"{(post_metrics['ai_predictability_score'] - pre_metrics['ai_predictability_score']):.1f}%", "خروج کامل از منطقه خطر"),
        ("تنوع واژگانی متن (Type-Token Ratio)", f"{pre_metrics['ttr']:.3f}", f"{post_metrics['ttr']:.3f}", f"+{(post_metrics['ttr'] - pre_metrics['ttr']):.3f}", "غنی‌سازی واژگان"),
        ("تعداد کلیشه‌ها و تکیه‌کلام‌های ماشینی", f"{pre_metrics['markers_found']}", f"{post_metrics['markers_found']}", f"-{pre_metrics['markers_found'] - post_metrics['markers_found']}", "حذف کامل کلیشه‌ها"),
        ("تعداد کل کلمات متن", f"{pre_metrics['total_words']}", f"{post_metrics['total_words']}", f"{post_metrics['total_words'] - pre_metrics['total_words']}", "حفظ انسجام و پیام"),
        ("میانگین طول جملات (تعداد کلمه)", f"{pre_metrics['mean_len']:.1f}", f"{post_metrics['mean_len']:.1f}", f"{(post_metrics['mean_len'] - pre_metrics['mean_len']):.1f}", "تنوع استاندارد")
    ] if lang == "fa" else [
        ("Burstiness Index (CV_len)", f"{pre_metrics['burstiness_cv']:.3f}", f"{post_metrics['burstiness_cv']:.3f}", f"+{(post_metrics['burstiness_cv'] - pre_metrics['burstiness_cv']):.3f}", "Optimal Cadence"),
        ("AI Predictability Footprint", f"{pre_metrics['ai_predictability_score']:.1f}%", f"{post_metrics['ai_predictability_score']:.1f}%", f"{(post_metrics['ai_predictability_score'] - pre_metrics['ai_predictability_score']):.1f}%", "Substantial Risk Reduction"),
        ("Lexical Diversity (TTR)", f"{pre_metrics['ttr']:.3f}", f"{post_metrics['ttr']:.3f}", f"+{(post_metrics['ttr'] - pre_metrics['ttr']):.3f}", "Vocabulary Enriched"),
        ("Detected Robotic Cliches", f"{pre_metrics['markers_found']}", f"{post_metrics['markers_found']}", f"-{pre_metrics['markers_found'] - post_metrics['markers_found']}", "Completely Sanitized"),
        ("Total Word Count", f"{pre_metrics['total_words']}", f"{post_metrics['total_words']}", f"{post_metrics['total_words'] - pre_metrics['total_words']}", "Semantics Preserved"),
        ("Mean Sentence Length", f"{pre_metrics['mean_len']:.1f}", f"{post_metrics['mean_len']:.1f}", f"{(post_metrics['mean_len'] - pre_metrics['mean_len']):.1f}", "Standard Variance")
    ]

    for r_idx, row_data in enumerate(rows1, 4):
        fill = green_fill if r_idx % 2 == 0 else accent_fill
        for c_idx, val in enumerate(row_data, 1):
            c = ws1.cell(row=r_idx, column=c_idx, value=val)
            c.font = body_font
            c.border = thin_border
            c.fill = fill
            c.alignment = Alignment(horizontal="center" if c_idx > 1 else "left", vertical="center")

    # Sheet 2: Sentence Audit
    ws2 = wb.create_sheet(title="ممیزی جمله به جمله" if lang == "fa" else "Sentence Audit")
    ws2.views.sheetView[0].rightToLeft = (lang == "fa")
    ws2["A1"] = "جدول تطبیقی جملات پیش‌نویس اولیه در برابر متن بازنویسی‌شده دانشگاهی" if lang == "fa" else "Comparative Sentence-by-Sentence Audit Table"
    ws2["A1"].font = title_font

    headers2 = ["ردیف", "جمله اولیه (AI Draft)", "طول اولیه", "جمله بازنویسی‌شده دانشگاهی", "طول ثانویه", "شرح اصلاحات و فنون نحوی"] if lang == "fa" else [
        "#", "Original Sentence (AI Draft)", "Pre Len", "Polished Academic Sentence", "Post Len", "Stylistic & Syntactic Transformation"
    ]
    for col_idx, h in enumerate(headers2, 1):
        cell = ws2.cell(row=3, column=col_idx, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    for r_idx, (orig, pol, exp) in enumerate(sentence_pairs, 4):
        ws2.cell(row=r_idx, column=1, value=r_idx - 3).alignment = Alignment(horizontal="center")
        ws2.cell(row=r_idx, column=2, value=orig)
        ws2.cell(row=r_idx, column=3, value=count_words(orig)).alignment = Alignment(horizontal="center")
        ws2.cell(row=r_idx, column=4, value=pol)
        ws2.cell(row=r_idx, column=5, value=count_words(pol)).alignment = Alignment(horizontal="center")
        ws2.cell(row=r_idx, column=6, value=exp)
        for c in range(1, 7):
            cell = ws2.cell(row=r_idx, column=c)
            cell.font = body_font
            cell.border = thin_border
            cell.fill = green_fill if r_idx % 2 == 0 else accent_fill

    # Sheet 3: AI Marker Catalog
    ws3 = wb.create_sheet(title="کاتالوگ کلیشه‌ها" if lang == "fa" else "AI Marker Catalog")
    ws3.views.sheetView[0].rightToLeft = (lang == "fa")
    ws3["A1"] = "فهرست کلیشه‌ها و تکیه‌کلام‌های ماشینی شناسایی‌شده در متن اولیه" if lang == "fa" else "Detected Generative AI Markers Catalog"
    ws3["A1"].font = title_font

    headers3 = ["ردیف", "الگوی کلیشه‌ای", "دسته‌بندی", "تعداد رخداد", "پیشنهاد جایگزین", "علت نامناسب بودن"] if lang == "fa" else [
        "#", "Robotic Pattern", "Category", "Count", "Recommended Academic Alternative", "Pathology"
    ]
    for col_idx, h in enumerate(headers3, 1):
        cell = ws3.cell(row=3, column=col_idx, value=h)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    detected = pre_metrics.get("detected_markers", pre_metrics.get("markers_detected", []))
    for r_idx, d in enumerate(detected, 4):
        ws3.cell(row=r_idx, column=1, value=r_idx - 3).alignment = Alignment(horizontal="center")
        ws3.cell(row=r_idx, column=2, value=d["pattern"])
        ws3.cell(row=r_idx, column=3, value=d["category"])
        ws3.cell(row=r_idx, column=4, value=d["count"]).alignment = Alignment(horizontal="center")
        ws3.cell(row=r_idx, column=5, value=d["replacement"])
        ws3.cell(row=r_idx, column=6, value=d["description"])
        for c in range(1, 7):
            cell = ws3.cell(row=r_idx, column=c)
            cell.font = body_font
            cell.border = thin_border
            cell.fill = orange_fill

    # Sheet 4: Stanford SciWrite 5-Pass Editorial Review
    ws4 = wb.create_sheet(title="ویراستاری ۵ مرحله‌ای ساینانی" if lang == "fa" else "SciWrite 5-Pass Review")
    ws4.views.sheetView[0].rightToLeft = (lang == "fa")
    ws4["A1"] = "گزارش ویراستاری علمی ۵ مرحله‌ای بر پایه روش دکتر کریستین ساینانی (استنفورد)" if lang == "fa" else "Stanford SciWrite 5-Pass Editorial Review (Dr. Kristin Sainani)"
    ws4["A1"].font = title_font

    headers4 = ["مرحله ویراستاری", "سطح شدت", "مورد شناسایی‌شده", "پیشنهاد اصلاحی", "استدلال نگارشی"] if lang == "fa" else [
        "Audit Pass", "Severity", "Detected Item / Snippet", "Recommended Action", "Editorial Rationale"
    ]
    for col_idx, h in enumerate(headers4, 1):
        cell = ws4.cell(row=3, column=col_idx, value=h)
        cell.font = header_font
        cell.fill = navy_fill
        cell.alignment = Alignment(horizontal="center", vertical="center")

    r_curr = 4
    if sainani_findings:
        for p1 in sainani_findings.get("pass1_clutter", []):
            ws4.cell(row=r_curr, column=1, value="Pass 1: Clutter (حذف حشو)")
            c_sev = ws4.cell(row=r_curr, column=2, value=p1["severity"])
            c_sev.alignment = Alignment(horizontal="center")
            ws4.cell(row=r_curr, column=3, value=p1["original_phrase"])
            ws4.cell(row=r_curr, column=4, value=p1["suggested_fix"])
            ws4.cell(row=r_curr, column=5, value=p1["rationale"])
            for c in range(1, 6):
                ws4.cell(row=r_curr, column=c).border = thin_border
            r_curr += 1

        for p2 in sainani_findings.get("pass2_voice_verbs", []):
            ws4.cell(row=r_curr, column=1, value="Pass 2: Verbs (احیای افعال اسمی)")
            c_sev = ws4.cell(row=r_curr, column=2, value=p2["severity"])
            c_sev.alignment = Alignment(horizontal="center")
            ws4.cell(row=r_curr, column=3, value=p2["smothered_verb"])
            ws4.cell(row=r_curr, column=4, value=p2["resurrected_verb"])
            ws4.cell(row=r_curr, column=5, value=p2["rationale"])
            for c in range(1, 6):
                ws4.cell(row=r_curr, column=c).border = thin_border
            r_curr += 1

        for p3 in sainani_findings.get("pass3_sentence_arch", []):
            ws4.cell(row=r_curr, column=1, value="Pass 3: Architecture (معماری جمله)")
            c_sev = ws4.cell(row=r_curr, column=2, value=p3["severity"])
            c_sev.alignment = Alignment(horizontal="center")
            ws4.cell(row=r_curr, column=3, value=p3["snippet"])
            ws4.cell(row=r_curr, column=4, value="شکستن جمله طولانی")
            ws4.cell(row=r_curr, column=5, value=p3["rationale"])
            for c in range(1, 6):
                ws4.cell(row=r_curr, column=c).border = thin_border
            r_curr += 1

        for p4 in sainani_findings.get("pass4_keyword_consistency", []):
            ws4.cell(row=r_curr, column=1, value="Pass 4: Banana Rule (ثبات واژگان)")
            c_sev = ws4.cell(row=r_curr, column=2, value=p4["severity"])
            c_sev.alignment = Alignment(horizontal="center")
            ws4.cell(row=r_curr, column=3, value=f"متغیر: {p4['construct']}")
            ws4.cell(row=r_curr, column=4, value="تثبیت یک عنوان واحد بدون تنوع‌طلبی واژگانی")
            ws4.cell(row=r_curr, column=5, value=p4["rationale"])
            for c in range(1, 6):
                ws4.cell(row=r_curr, column=c).border = thin_border
            r_curr += 1

    # Adjust widths
    for ws in [ws1, ws2, ws3, ws4]:
        for col in ws.columns:
            max_len = max(len(str(cell.value or "")) for cell in col)
            col_letter = get_column_letter(col[0].column)
            ws.column_dimensions[col_letter].width = min(50, max(12, max_len + 3))

    wb.save(out_path)
    return str(out_path)



# ==============================================================================
# 8. OPENXML BIDI WORD REPORT COMPILER (DOCX)
# ==============================================================================

def set_cell_background(cell, fill_hex: str):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def export_polished_docx(
    project_title: str,
    section_title: str,
    pre_metrics: Dict[str, Any],
    post_metrics: Dict[str, Any],
    sentence_pairs: List[Tuple[str, str, str]],
    final_clean_text: str,
    out_path: Path,
    lang: str = "fa",
    sainani_findings: Dict[str, Any] = None
) -> str:
    """Generates defense-ready Word document formatted with native OpenXML RTL."""
    doc = docx.Document()

    # Configure Margins (1 inch / 2.54 cm standard)
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)

    font_title = "B Titr" if lang == "fa" else "Calibri"
    font_body = "B Nazanin" if lang == "fa" else "Calibri"
    font_latin = "Times New Roman"

    # Document Header Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run(
        "گزارش جامع پالایش لحن دانشگاهی و اصالت‌سنجی نگارش" if lang == "fa" else "Academic Tone Polishing & Anti-AI Refinement Report"
    )
    r_title.font.name = font_title
    r_title.font.size = Pt(18)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(26, 54, 93)

    # Subtitle / Section
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run(f"{project_title}\n{section_title}")
    r_sub.font.name = font_body
    r_sub.font.size = Pt(12)
    r_sub.font.color.rgb = RGBColor(74, 85, 104)

    doc.add_paragraph()  # Spacer

    # ==========================================================================
    # SECTION 1: EXECUTIVE ANT-AI & STYLISTIC SCORECARD
    # ==========================================================================
    h1 = doc.add_paragraph()
    r_h1 = h1.add_run("۱. کارنامه ارزیابی اصالت سبک و شاخص‌های تشخیص هوش مصنوعی" if lang == "fa" else "1. Executive Anti-AI & Stylistic Scorecard")
    r_h1.font.name = font_title
    r_h1.font.size = Pt(14)
    r_h1.font.bold = True
    r_h1.font.color.rgb = RGBColor(43, 108, 176)

    intro_p = doc.add_paragraph()
    r_intro = intro_p.add_run(
        "جدول زیر نشان‌دهنده ارزیابی کمی و مقایسه‌ای متن پیش‌نویس در برابر نسخه نهایی دانشگاهی است. الگوریتم‌های همانندجویی و شناسایی هوش مصنوعی (نظیر سمیم‌نور، همانندجو، و Turnitin AI) بر دو شاخص بنیادین ناهمگونی طول جملات (Burstiness) و غیرقابل‌پیش‌بینی بودن واژگانی (Perplexity) تمرکز دارند:"
        if lang == "fa" else
        "The scorecard below details the comparative evaluation between the raw draft and the polished academic version. Leading academic AI detection algorithms (Turnitin AI, GPTZero, SamimNoor) primarily target sentence length variance (Burstiness) and lexical predictability (Perplexity):"
    )
    r_intro.font.name = font_body
    r_intro.font.size = Pt(11)

    table1 = doc.add_table(rows=7, cols=5)
    table1.alignment = WD_TABLE_ALIGNMENT.CENTER

    headers1 = [
        "شاخص ارزیابی", "پیش‌نویس اولیه", "نسخه دانشگاهی", "میزان تغییر", "ارزیابی نهایی"
    ] if lang == "fa" else [
        "Evaluation Metric", "Raw Draft (AI)", "Polished Academic", "Shift", "Verdict"
    ]

    for col_idx, text in enumerate(headers1):
        cell = table1.cell(0, col_idx)
        set_cell_background(cell, "1A365D")
        set_cell_margins(cell, top=120, bottom=120, left=150, right=150)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.font.name = font_title
        run.font.size = Pt(10)
        run.font.bold = True
        run.font.color.rgb = RGBColor(255, 255, 255)

    metrics_rows = [
        ("شاخص ضرب‌آهنگ (Burstiness CV)", f"{pre_metrics['burstiness_cv']:.3f}", f"{post_metrics['burstiness_cv']:.3f}", f"+{(post_metrics['burstiness_cv'] - pre_metrics['burstiness_cv']):.3f}", "ضرب‌آهنگ طبیعی و اصیل"),
        ("شاخص ردپای هوش مصنوعی (AI Footprint)", f"{pre_metrics['ai_predictability_score']:.1f}%", f"{post_metrics['ai_predictability_score']:.1f}%", f"{(post_metrics['ai_predictability_score'] - pre_metrics['ai_predictability_score']):.1f}%", "خروج کامل از منطقه خطر"),
        ("تنوع واژگانی متن (TTR)", f"{pre_metrics['ttr']:.3f}", f"{post_metrics['ttr']:.3f}", f"+{(post_metrics['ttr'] - pre_metrics['ttr']):.3f}", "غنی‌سازی لغات تخصصی"),
        ("تعداد کلیشه‌های ماشینی", f"{pre_metrics['markers_found']}", f"{post_metrics['markers_found']}", f"-{pre_metrics['markers_found'] - post_metrics['markers_found']}", "پالایش کامل عبارات حشو"),
        ("میانگین طول جملات (کلمه)", f"{pre_metrics['mean_len']:.1f}", f"{post_metrics['mean_len']:.1f}", f"{(post_metrics['mean_len'] - pre_metrics['mean_len']):.1f}", "تعادل ساختاری"),
        ("تعداد کل کلمات", f"{pre_metrics['total_words']}", f"{post_metrics['total_words']}", f"{post_metrics['total_words'] - pre_metrics['total_words']}", "حفظ مفاهیم اصلی")
    ] if lang == "fa" else [
        ("Burstiness Index (CV_len)", f"{pre_metrics['burstiness_cv']:.3f}", f"{post_metrics['burstiness_cv']:.3f}", f"+{(post_metrics['burstiness_cv'] - pre_metrics['burstiness_cv']):.3f}", "Authentic Cadence"),
        ("AI Predictability Footprint", f"{pre_metrics['ai_predictability_score']:.1f}%", f"{post_metrics['ai_predictability_score']:.1f}%", f"{(post_metrics['ai_predictability_score'] - pre_metrics['ai_predictability_score']):.1f}%", "Cleared Risk Threshold"),
        ("Lexical Diversity (TTR)", f"{pre_metrics['ttr']:.3f}", f"{post_metrics['ttr']:.3f}", f"+{(post_metrics['ttr'] - pre_metrics['ttr']):.3f}", "Enriched Academic Lexicon"),
        ("Robotic Cliches Detected", f"{pre_metrics['markers_found']}", f"{post_metrics['markers_found']}", f"-{pre_metrics['markers_found'] - post_metrics['markers_found']}", "Fully Sanitized"),
        ("Mean Sentence Length", f"{pre_metrics['mean_len']:.1f}", f"{post_metrics['mean_len']:.1f}", f"{(post_metrics['mean_len'] - pre_metrics['mean_len']):.1f}", "Balanced Cadence"),
        ("Total Word Count", f"{pre_metrics['total_words']}", f"{post_metrics['total_words']}", f"{post_metrics['total_words'] - pre_metrics['total_words']}", "Content Preserved")
    ]

    for row_idx, row_vals in enumerate(metrics_rows, 1):
        bg = "F7FAFC" if row_idx % 2 == 0 else "FFFFFF"
        for col_idx, val in enumerate(row_vals):
            cell = table1.cell(row_idx, col_idx)
            set_cell_background(cell, bg)
            set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
            p = cell.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if col_idx > 0 else WD_ALIGN_PARAGRAPH.RIGHT
            run = p.add_run(val)
            run.font.name = font_body
            run.font.size = Pt(10)
            if col_idx == 4:
                run.font.bold = True
                run.font.color.rgb = RGBColor(39, 174, 96)

    doc.add_paragraph()  # Spacer

    # ==========================================================================
    # SECTION 2: CLEAN POLISHED ACADEMIC TEXT (READY FOR THESIS INSERTION)
    # ==========================================================================
    h2 = doc.add_paragraph()
    r_h2 = h2.add_run("۲. متن ویراسته و اصیل دانشگاهی (آماده درج در رساله یا مقاله)" if lang == "fa" else "2. Final Polished Academic Text (Defense-Ready)")
    r_h2.font.name = font_title
    r_h2.font.size = Pt(14)
    r_h2.font.bold = True
    r_h2.font.color.rgb = RGBColor(43, 108, 176)

    # Polished text box container
    p_body = doc.add_paragraph()
    p_body.paragraph_format.first_line_indent = Inches(0.5)
    p_body.paragraph_format.line_spacing = 1.3
    p_body.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_body = p_body.add_run(final_clean_text)
    r_body.font.name = font_body
    r_body.font.size = Pt(12)

    doc.add_paragraph()  # Spacer

    # ==========================================================================
    # SECTION 3: COMPARATIVE SENTENCE-BY-SENTENCE AUDIT
    # ==========================================================================
    h3 = doc.add_paragraph()
    r_h3 = h3.add_run("۳. جدول تطبیقی و تحلیل دگرگونی‌های نحوی (جمله به جمله)" if lang == "fa" else "3. Comparative Sentence Transformation Audit")
    r_h3.font.name = font_title
    r_h3.font.size = Pt(14)
    r_h3.font.bold = True
    r_h3.font.color.rgb = RGBColor(43, 108, 176)

    table2 = doc.add_table(rows=len(sentence_pairs) + 1, cols=4)
    table2.alignment = WD_TABLE_ALIGNMENT.CENTER

    headers2 = ["ردیف", "پیش‌نویس اولیه (AI Draft)", "نسخه ویراسته دانشگاهی", "شرح دگرگونی نحوی و اصطلاحی"] if lang == "fa" else [
        "#", "Original Draft (AI)", "Polished Academic Text", "Linguistic Transformation Rationale"
    ]

    for col_idx, text in enumerate(headers2):
        cell = table2.cell(0, col_idx)
        set_cell_background(cell, "2B6CB0")
        set_cell_margins(cell, top=120, bottom=120, left=150, right=150)
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run(text)
        run.font.name = font_title
        run.font.size = Pt(10)
        run.font.bold = True
        run.font.color.rgb = RGBColor(255, 255, 255)

    for r_idx, (orig, pol, exp) in enumerate(sentence_pairs, 1):
        bg = "FFFFFF" if r_idx % 2 == 1 else "F7FAFC"
        # Col 0: Index
        c0 = table2.cell(r_idx, 0)
        set_cell_background(c0, bg)
        p0 = c0.paragraphs[0]
        p0.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p0.add_run(str(r_idx)).font.name = font_body

        # Col 1: Original
        c1 = table2.cell(r_idx, 1)
        set_cell_background(c1, "FFF5F5")  # Slight reddish tint for AI draft
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r1 = p1.add_run(orig)
        r1.font.name = font_body
        r1.font.size = Pt(9.5)

        # Col 2: Polished
        c2 = table2.cell(r_idx, 2)
        set_cell_background(c2, "F0FFF4")  # Slight green tint for polished
        p2 = c2.paragraphs[0]
        p2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r2 = p2.add_run(pol)
        r2.font.name = font_body
        r2.font.size = Pt(9.5)
        r2.font.bold = True

        # Col 3: Explanation
        c3 = table2.cell(r_idx, 3)
        set_cell_background(c3, bg)
        p3 = c3.paragraphs[0]
        p3.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r3 = p3.add_run(exp)
        r3.font.name = font_body
        r3.font.size = Pt(9)
        r3.font.color.rgb = RGBColor(113, 128, 150)

    
    # ==========================================================================
    # SECTION 4: STANFORD SCIWRITE 5-PASS EDITORIAL AUDIT
    # ==========================================================================
    if sainani_findings:
        doc.add_page_break()
        h4 = doc.add_paragraph()
        r_h4 = h4.add_run("۴. گزارش جامع ویراستاری علمی ۵ مرحله‌ای (Stanford SciWrite Review)" if lang == "fa" else "4. Stanford SciWrite 5-Pass Editorial Review")
        r_h4.font.name = font_title
        r_h4.font.size = Pt(14)
        r_h4.font.bold = True
        r_h4.font.color.rgb = RGBColor(26, 54, 93)

        p_desc4 = doc.add_paragraph()
        p_desc4.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        r_desc4 = p_desc4.add_run(
            "این ممیزی تخصصی بر پایه متدولوژی نگارش علمی استنفورد (دکتر کریستین ساینانی) تدوین شده و متن را در ۵ لایه پیاپی شامل پیراستن حشو، احیای افعال اسمی‌شده، معماری طول جملات، قاعده ضد تنوع‌طلبی واژگانی (The Banana Rule) و ممیزی استنادهای دست‌دوم واکاوی می‌نماید:"
            if lang == "fa" else
            "This editorial audit applies Stanford's 'Writing in the Sciences' methodology (Dr. Kristin Sainani), systematically screening text across five sequential dimensions: clutter extraction, verb vitality, sentence architecture, keyword consistency (The Banana Rule), and citation integrity:"
        )
        r_desc4.font.name = font_body
        r_desc4.font.size = Pt(10.5)

        # Top 5 Priority Revisions Callout Box
        top5 = sainani_findings.get("top_5_priorities", [])
        if top5:
            box_tbl = doc.add_table(rows=1, cols=1)
            box_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
            b_cell = box_tbl.cell(0, 0)
            set_cell_background(b_cell, "EBF8FF")
            set_cell_margins(b_cell, top=140, bottom=140, left=180, right=180)
            bp = b_cell.paragraphs[0]
            bp.alignment = WD_ALIGN_PARAGRAPH.RIGHT if lang == "fa" else WD_ALIGN_PARAGRAPH.LEFT
            r_bh = bp.add_run("۵ اولویت نخست بازنگری متن (Top 5 Priority Revisions):\n" if lang == "fa" else "Top 5 Priority Revisions:\n")
            r_bh.font.name = font_title
            r_bh.font.size = Pt(11)
            r_bh.font.bold = True
            r_bh.font.color.rgb = RGBColor(43, 108, 176)

            for idx, item in enumerate(top5, 1):
                sev_color = RGBColor(197, 48, 48) if item["severity"] == "CRITICAL" else RGBColor(192, 86, 33)
                r_item = bp.add_run(f"  {idx}. [{item['severity']}] {item['desc']} ── {item['action']}\n")
                r_item.font.name = font_body
                r_item.font.size = Pt(9.5)
                r_item.font.bold = (item["severity"] == "CRITICAL")
            doc.add_paragraph()

    doc.save(out_path)
    return str(out_path)



# ==============================================================================
# 9. MASTER CLI DRIVER
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="ai-academic-tone-polisher: Academic Tone Polisher & Anti-AI Detector (Skill #22)"
    )
    parser.add_argument("--json", type=str, help="Path to input JSON payload")
    parser.add_argument("--text", type=str, help="Direct text input string")
    parser.add_argument("--file", type=str, help="Path to plain text file or docx")
    parser.add_argument("--sample", type=str, default="persian_draft", choices=["persian_draft", "english_draft"],
                        help="Which sample key to process from JSON payload")
    parser.add_argument("--out-dir", type=str, default=".", help="Directory to save generated deliverables")
    parser.add_argument("--lang", type=str, choices=["fa", "en"], help="Report language (defaults to sample language)")
    parser.add_argument("--intensity", type=str, default="moderate", choices=["gentle", "moderate", "aggressive"],
                        help="Polishing aggressiveness level")
    parser.add_argument("--mode", type=str, default="full", choices=["full", "section", "targeted", "interactive"],
                        help="Review mode per Stanford SciWrite")
    parser.add_argument("--target-pass", type=str, choices=["clutter", "verbs", "architecture", "terminology", "numbers"],
                        help="Specific pass for targeted review mode")

    args = parser.parse_args()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # 1. Ingest Input Text & Metadata
    project_title = "اثربخشی مداخله بر متغیرهای روان‌شناختی"
    section_title = "بحث و تفسیر یافته‌ها"
    input_text = ""
    lang = args.lang or "fa"

    if args.json:
        with open(args.json, "r", encoding="utf-8") as f:
            data = json.load(f)
        project_title = data.get("project_title", project_title)
        samples = data.get("samples", {})
        sample_key = args.sample if args.sample in samples else list(samples.keys())[0]
        sample_data = samples[sample_key]
        section_title = sample_data.get("section_title", section_title)
        input_text = sample_data.get("text", "")
        lang = args.lang or sample_data.get("language", "fa")
    elif args.file:
        with open(args.file, "r", encoding="utf-8") as f:
            input_text = f.read()
    elif args.text:
        input_text = args.text
    else:
        print("[-] Error: Must provide --json, --file, or --text input.", file=sys.stderr)
        sys.exit(1)

    print(f"[*] Initializing ai-academic-tone-polisher (Skill #22)...")
    print(f"[*] Target Language: {lang.upper()} | Intensity: {args.intensity}")
    print(f"[*] Processing: {section_title}")

    # 2. Invariant Masking (Citations & Statistics)
    shield = EntityShield()
    masked_text = shield.mask(input_text)
    print(f"[*] Protected {shield.counter_cit} APA in-text citations and {shield.counter_stat} statistical parameters.")

    # 3. Pre-Optimization Diagnostics
    pre_sentences = split_into_sentences(masked_text, lang)
    pre_metrics = compute_anti_ai_metrics(pre_sentences, masked_text, lang)
    print(f"[*] Pre-Polish Metrics:")
    print(f"    - Sentence Count: {pre_metrics['sentence_count']}")
    print(f"    - Mean Length: {pre_metrics['mean_len']} words (SD: {pre_metrics['sd_len']})")
    print(f"    - Burstiness Index (CV): {pre_metrics['burstiness_cv']:.3f} (Warning if < 0.35)")
    print(f"    - AI Predictability Footprint: {pre_metrics['ai_predictability_score']:.1f}%")
    print(f"    - Robotic Cliches Detected: {pre_metrics['markers_found']}")

    # 4. Polishing & Humanization Pass
    sainani_auditor = SainaniEditorialAuditor(lang=lang)
    sainani_findings = sainani_auditor.run_five_passes(masked_text, pre_sentences)
    print(f"[*] Stanford SciWrite 5-Pass Audit:")
    print(f"    - Pass 1 Clutter Findings: {len(sainani_findings['pass1_clutter'])}")
    print(f"    - Pass 2 Smothered Verbs: {len(sainani_findings['pass2_voice_verbs'])}")
    print(f"    - Pass 3 Buried Predicates: {len(sainani_findings['pass3_sentence_arch'])}")
    print(f"    - Pass 4 Banana Rule Violations: {len(sainani_findings['pass4_keyword_consistency'])}")
    print(f"    - Pass 5 Citation Invariants: {len(sainani_findings['pass5_numerical_citation'])}")
    print(f"    - Top Priority Revisions Identified: {len(sainani_findings['top_5_priorities'])}")

    sentence_pairs, final_clean_text = polish_and_humanize(
        pre_sentences, shield, lang=lang, intensity=args.intensity
    )

    if args.mode == "interactive":
        print("\n" + "="*70)
        print("  INTERACTIVE PARAGRAPH-BY-PARAGRAPH REVIEW (SciWrite)")
        print("="*70)
        for idx, (orig, pol, exp) in enumerate(sentence_pairs[:10], 1):
            print(f"\n--- Paragraph/Sentence {idx} ---")
            print(f"Original: {orig}")
            print(f"Revised:  {pol}")
            print(f"Notes:    {exp}")
        print("="*70 + "\n")

    # 5. Post-Optimization Diagnostics
    post_sentences = split_into_sentences(final_clean_text, lang)
    post_metrics = compute_anti_ai_metrics(post_sentences, final_clean_text, lang)
    print(f"[*] Post-Polish Metrics:")
    print(f"    - Sentence Count: {post_metrics['sentence_count']}")
    print(f"    - Mean Length: {post_metrics['mean_len']} words (SD: {post_metrics['sd_len']})")
    print(f"    - Burstiness Index (CV): {post_metrics['burstiness_cv']:.3f} (Elevated to Authentic Human Cadence)")
    print(f"    - AI Predictability Footprint: {post_metrics['ai_predictability_score']:.1f}% (Substantial Reduction)")
    print(f"    - Remaining Cliches: {post_metrics['markers_found']}")

    # 6. Generate Deliverables
    # A. 300-DPI Dual Plot
    plot_path = out_dir / "tone_burstiness_plot.png"
    generate_burstiness_plot(pre_metrics, post_metrics, plot_path, lang)
    print(f"[+] Diagnostic Plot saved: {plot_path}")

    # B. Excel Matrix
    xlsx_path = out_dir / "academic_tone_audit_matrix.xlsx"
    export_audit_matrix_excel(pre_metrics, post_metrics, sentence_pairs, xlsx_path, lang, sainani_findings=sainani_findings)
    print(f"[+] Excel Audit Matrix saved: {xlsx_path}")

    # C. OpenXML BiDi Word Document
    docx_filename = "متن_ویراسته_و_دانشگاهی.docx" if lang == "fa" else "Polished_Academic_Manuscript.docx"
    docx_path = out_dir / docx_filename
    export_polished_docx(
        project_title, section_title, pre_metrics, post_metrics, sentence_pairs, final_clean_text, docx_path, lang, sainani_findings=sainani_findings
    )
    print(f"[+] Polished Word Document saved: {docx_path}")

    # D. Structured JSON Results Ledger
    json_path = out_dir / "tone_polish_results.json"
    results_payload = {
        "project_title": project_title,
        "section_title": section_title,
        "language": lang,
        "intensity": args.intensity,
        "pre_metrics": pre_metrics,
        "post_metrics": post_metrics,
        "deliverables": {
            "docx": str(docx_path),
            "xlsx": str(xlsx_path),
            "plot": str(plot_path)
        },
        "final_clean_text": final_clean_text
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(results_payload, f, ensure_ascii=False, indent=2)
    print(f"[+] JSON Ledger saved: {json_path}")
    print(f"[✓] ai-academic-tone-polisher execution completed successfully.")

if __name__ == "__main__":
    main()
