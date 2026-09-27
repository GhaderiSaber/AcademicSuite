#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
critique_detection_contract.py — Unified High-Precision User Critique & Defect Detection Engine

This module provides authoritative, high-precision detection of genuine human user
critiques, defect reports, and corrective guidance directed at AI agent performance.

Key Invariants:
1. Immunity for Subagents & Machine Envelopes: Subagent conversations and internal delegation
   envelopes or adaptive context markers NEVER constitute human user feedback.
2. Complete Tag & Metadata Stripping: Strips IDE metadata such as <USER_SETTINGS_CHANGE>
   and <ADDITIONAL_METADATA> completely (including their inner contents) to prevent
   words like 'changed' or 'setting' from leaking into critique detection.
3. Domain Term Masking: Protects legitimate academic and statistical terminology
   ('standard error', 'missing data', 'reject null hypothesis', 'R-squared change',
   'problem statement', 'modification indices', 'repeated measures', 'خطای استاندارد',
   'داده‌های گمشده', 'رد فرض صفر', 'بیان مسئله', 'نرمال نیست', 'معنادار نیست') from
   triggering false-positive defect classifications.
4. Questions & Inquiries vs Assertive Accusations: Interrogatives ending with '?' or '؟'
   are recognized as informational inquiries unless accompanied by explicit accusatory markers.
"""

import re
from typing import Dict, Any, List, Optional, Tuple


# Known machine / agent context markers that must never be treated as human critiques
MACHINE_CONTEXT_MARKERS = (
    "🧠 DETERMINISTIC ADAPTIVE CONTEXT",
    "### Contractual Delegation Envelope",
    "🚨 CONSTITUTIONAL ENFORCEMENT",
    "### 🛫 Pre-Flight Pipeline Declaration",
    "🧠 CONTINUOUS LEARNING TRIGGER ACTIVE",
    "### Contractual Delegation Envelope (CDE)"
)

# Collocations of domain and statistical terms to mask out before critique scanning
DOMAIN_COLLOCATION_EXCLUSIONS = [
    # English statistical terms
    r"\bstandard error(?:s)?\b",
    r"\bse of measurement\b",
    r"\btype\s+[12i]+\s+error(?:s)?\b",
    r"\b(?:mean|sum of)?\s*squared error(?:s)?\b",
    r"\berror\s+variance\b",
    r"\berror\s+term(?:s)?\b",
    r"\bmissing (?:data|values|cases|completely at random)\b",
    r"\blittle\x27?s mcar\b",
    r"\bmcar test\b",
    r"\breject(?:ed|ing)? (?:the )?(?:null )?hypothesis\b",
    r"\bfail(?:ed|ure)? to reject\b",
    r"\bhypothesis (?:was|is) rejected\b",
    r"\b(?:r[- ]?squared|r2|f)[- ]change\b",
    r"\bdelta r2\b",
    r"\bmodification indic(?:es|ex)\b",
    r"\bmodel modification\b",
    r"\b(?:problem statement|statement of the problem|research problem)\b",
    r"\brepeated measures\b",
    r"\brepeated-measures\b",
    r"\bbonferroni correction\b",
    r"\byates correction\b",
    r"\bcorrection for attenuation\b",
    # Persian statistical terms
    r"خطای استاندارد",
    r"خطای برآورد",
    r"خطای نوع اول",
    r"خطای نوع دوم",
    r"واریانس خطا",
    r"جمله خطا",
    r"داده‌های گمشده",
    r"داده‌های مفقود",
    r"مقادیر گمشده",
    r"آزمون ام‌کار",
    r"رد فرض صفر",
    r"فرض صفر رد شد",
    r"فرضیه(?:[‌ ])?ها رد شد",
    r"فرضیه رد شد",
    r"شاخص‌های اصلاح",
    r"شاخص اصلاح",
    r"اصلاح مدل",
    r"تغییر ضریب تعیین",
    r"تغییر r2",
    r"تغییر f",
    r"بیان مسئله",
    r"مسئله پژوهش",
    r"مشکل پژوهش",
    r"اندازه‌گیری‌های مکرر",
    r"اندازه‌گیری مکرر",
    r"طرح با سنجش مکرر",
    r"تصحیح بن‌فرونی",
    r"تعدیل بن‌فرونی",
    r"معنادار نیست",
    r"نرمال نیست",
    r"خطی نیست",
    r"تفاوت معناداری وجود ندارد",
    r"رابطه(?:[‌ ])?ای وجود ندارد",
    r"رابطه معناداری وجود ندارد",
    r"تفاوتی وجود ندارد",
    r"اثری وجود ندارد"
]

# High-precision patterns asserting a defect in agent deliverable, output, or execution
HIGH_PRECISION_CRITIQUE_PATTERNS = [
    # Explicit omission / mistake accusation against the agent
    r"\byou (?:forgot|left out|omitted|missed|didn\x27?t include|failed to include)\b",
    r"\byou (?:made an error|made a mistake|got this wrong|did this wrong)\b",
    r"\byou (?:should have|ought to have) (?:included|calculated|checked|run|used|had|put|added|set|created|\w+)\b",
    r"\byou (?:must|need to) fix\b",
    r"\byou need to (?:compare these two models|verify the effect size)\b",
    r"\bdon\x27?t say the treatment caused\b",

    # Explicit defect in deliverables / calculations / tables
    r"\b(?:problem|defect|bug|flaw):\s*",
    r"\bthere (?:is|are) (?:a |an )?(?:bug|defect|flaw|error|discrepancy|mismatch|problem)(?::|\b|\s+in\s+(?:the|your|this))",
    r"\b(?:the |this |your )?(?:tables?|calculations?|results?|outputs?|statistics?|numbers?|scripts?|code|models?|figures?|documents?|drafts?|effect sizes?|parameters?|values?) (?:in [^,\.\n]+ )?(?:is wrong|is incorrect|is flawed|is invalid|are wrong|are incorrect|are flawed|are invalid|has an error|have an error|failed|does not match|doesn\x27?t match|do not match|don\x27?t match)\b",
    r"\b(?:numbers?|results?|tables?|data) (?:in [^,\.\n]+ )?(?:don\x27?t|do not|doesn\x27?t|does not) match\b",
    r"\b(?:wrong|incorrect|flawed|erroneous) (?:tables?|calculations?|results?|numbers?|statistics?|outputs?|estimators?|models?|values?|formatting)\b",
    r"\b(?:redo|re-run|re-execute) (?:this|the|stage) because (?:it failed|it is wrong|there was an error)\b",
    r"\bthis is (?:completely )?(?:wrong|incorrect|flawed|erroneous|invalid)\b",
    r"\bwriting is too (?:superficial|shallow|robotic)\b",
    r"\b(?:missing|forgot) (?:the )?(?:table|section|demographic|limitations|implications|appendix)\b",
    r"\bthis method is not appropriate\b",
    r"\bso we have a problem\b",

    # Persian high-precision patterns
    r"اشتباه (?:[^\s]+ )?(?:کردی|شد|است|محاسبه کردی|حساب کردی)|غلط انجام دادی|جا انداختی|فراموش کردی|حذف کردی|از قلم انداختی",
    r"(?:خروجی|جدول|محاسبه|محاسبات|عدد|ارقام|گزارش|متن|فایل) (?:اشتباه|غلط|نادرست|دارای ایراد|دارای نقص|دارای خطا) است",
    r"ارقام با خروجی همخوانی ندارند|اعداد همخوانی ندارند|جدول با خروجی همخوانی ندارد",
    r"(?:این )?(?:خروجی|بخش|فصل|جدول|تحلیل) (?:ایراد دارد|ناقص است|اشتباه است)",
    r"این (?:روش|نگارش|جدول) (?:مناسب|درست|صحیح) نیست"
]


def extract_clean_user_message(raw_text: str) -> str:
    """
    Extracts the genuine user instruction text, safely stripping IDE metadata,
    settings change announcements, and system/machine context wrappers.
    """
    if not raw_text:
        return ""
    text = str(raw_text)

    # Check for machine context markers; if present at start, it is not a human user input
    for marker in MACHINE_CONTEXT_MARKERS:
        if marker in text:
            # If the text is purely machine context, return empty
            if text.strip().startswith(marker):
                return ""

    # If wrapped in <USER_REQUEST>, extract strictly what is inside
    m_req = re.search(r"<USER_REQUEST>(.*?)</USER_REQUEST>", text, re.DOTALL)
    if m_req:
        text = m_req.group(1)
    else:
        # Strip known Antigravity metadata blocks with their entire inner text
        text = re.sub(r"<ADDITIONAL_METADATA>.*?</ADDITIONAL_METADATA>", "", text, flags=re.DOTALL)
        text = re.sub(r"<USER_SETTINGS_CHANGE>.*?</USER_SETTINGS_CHANGE>", "", text, flags=re.DOTALL)
        # Strip any remaining XML/HTML tags
        text = re.sub(r"<[^>]+>", "", text)

    return text.strip()


def is_meaningful_user_critique(
    user_text: str,
    is_subagent: bool = False,
    caller: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Evaluates whether user_text represents a meaningful human user critique,
    defect report, or correction directed at the agent.

    Returns:
        (is_critique: bool, matched_term: Optional[str])
    """
    # Invariant 1: Subagents never receive human user critiques
    if is_subagent:
        return False, None

    caller_norm = (caller or "").lower().strip()
    if caller_norm and caller_norm not in ("", "unspecified", "academic-orchestrator", "orchestrator", "main", "default", "digital-saber"):
        # Specialized worker subagents (statistics-agent, academic-writer, etc.)
        return False, None

    clean = extract_clean_user_message(user_text)
    if not clean or len(clean) < 8:
        return False, None

    # Check for machine markers that survived extraction
    if any(m in clean for m in MACHINE_CONTEXT_MARKERS):
        return False, None

    # Mask known domain and statistical terminology to prevent false positives
    masked = clean
    for d_pat in DOMAIN_COLLOCATION_EXCLUSIONS:
        masked = re.sub(d_pat, " [DOMAIN_TERM] ", masked, flags=re.IGNORECASE)

    # Invariant 4: Questions and interrogatives are not critiques unless accusatory
    if clean.endswith("?") or clean.endswith("؟"):
        strong_accusations = [
            r"\byou made an error\b",
            r"\byou forgot\b",
            r"\bwhy did you fail\b",
            r"اشتباه کردی",
            r"چرا غلط انجام دادی"
        ]
        if not any(re.search(pat, clean, re.IGNORECASE) for pat in strong_accusations):
            return False, None

    # Evaluate against high-precision critique patterns
    for pat in HIGH_PRECISION_CRITIQUE_PATTERNS:
        m = re.search(pat, masked, re.IGNORECASE)
        if m:
            matched_term = m.group(0)
            return True, matched_term

    return False, None
