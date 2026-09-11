#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Digital Saber Academic Writing Reasoner
(موتور ساختاربندی و تحلیل نوشتار دانشگاهی دیجیتال صابر)

Structures academic prose according to the 5-step epistemic chain:
  Claim -> Evidence -> Interpretation -> Qualification -> Implication
Audits and refines text against robotic AI cliches and Persian half-spaces.
"""

import os
import sys
import re
import argparse
from typing import Dict, List, Any, Optional

ROBOTIC_AI_CLICHES = [
    "شایان ذکر است که",
    "شایان ذکر است",
    "در این راستا",
    "لازم به ذکر است که",
    "لازم به ذکر است",
    "به عنوان یک مدل هوش مصنوعی",
    "در جهان پرشتاب امروز",
    "در دنیای پرتلاطم کنونی",
    "می‌توان گفت که",
    "می توان گفت که",
    "به بررسی ... می‌پردازیم",
    "بدون شک",
    "واضح و مبرهن است",
    "همانطور که می‌دانیم"
]


class AcademicWritingReasoner:
    """Constructs and polishes high-impact scholarly prose for theses and journal articles."""

    def __init__(self):
        pass

    def build_epistemic_paragraph(self, components: Dict[str, str]) -> str:
        """
        Assembles a coherent academic paragraph from the 5 epistemic components.
        components: {
          "claim": "...",
          "evidence": "...",
          "interpretation": "...",
          "qualification": "...",
          "implication": "..."
        }
        """
        claim = components.get("claim", "").strip()
        evidence = components.get("evidence", "").strip()
        interp = components.get("interpretation", "").strip()
        qual = components.get("qualification", "").strip()
        impl = components.get("implication", "").strip()

        # Connect logically with authentic scholarly transitions
        parts = [claim]
        if evidence:
            parts.append(evidence)
        if interp:
            parts.append(interp)
        if qual:
            parts.append(qual)
        if impl:
            parts.append(impl)

        paragraph = " ".join(parts)
        return self.enforce_typography(paragraph)

    def audit_prose(self, text: str) -> Dict[str, Any]:
        """Audits text for robotic AI boilerplate, half-spaces, and cadence."""
        detected_cliches = []
        for c in ROBOTIC_AI_CLICHES:
            if c in text:
                detected_cliches.append(c)

        # Check half-spaces
        half_space_issues = []
        patterns = [
            (r"\bمی ([آ-ی]+)", "می \\1 -> می‌\\1"),
            (r"\bنمی ([آ-ی]+)", "نمی \\1 -> نمی‌\\1"),
            (r"([آ-ی]+) ها\b", "\\1 ها -> \\1‌ها"),
            (r"پیش آزمون", "پیش آزمون -> پیش‌آزمون"),
            (r"پس آزمون", "پس آزمون -> پس‌آزمون"),
            (r"روان شناسی", "روان شناسی -> روان‌شناسی"),
            (r"روان شناختی", "روان شناختی -> روان‌شناختی")
        ]
        for pat, rule in patterns:
            if re.search(pat, text):
                half_space_issues.append(rule)

        # Compute sentence length variability (cadence / burstiness)
        sentences = [s.strip() for s in re.split(r"[.!\?؛\n]", text) if len(s.strip()) > 5]
        lengths = [len(s.split()) for s in sentences]
        burstiness_cv = 0.0
        if lengths and len(lengths) > 1:
            mean_len = sum(lengths) / len(lengths)
            var_len = sum((x - mean_len) ** 2 for x in lengths) / (len(lengths) - 1)
            sd_len = var_len ** 0.5
            burstiness_cv = sd_len / mean_len if mean_len > 0 else 0.0

        is_human_grade = len(detected_cliches) == 0 and len(half_space_issues) == 0 and (burstiness_cv >= 0.35 or len(lengths) <= 1)

        return {
            "sentence_count": len(sentences),
            "mean_sentence_length_words": round(sum(lengths) / len(lengths), 1) if lengths else 0,
            "burstiness_cv": round(burstiness_cv, 2),
            "cliches_detected": detected_cliches,
            "half_space_defects": half_space_issues,
            "academic_cadence_verdict": "HUMAN_SCHOLARLY" if is_human_grade else "REQUIRES_POLISHING",
            "quality_score": max(0, 100 - len(detected_cliches) * 20 - len(half_space_issues) * 10)
        }

    def enforce_typography(self, text: str) -> str:
        """Applies strict Persian half-spaces and eliminates robotic clichés."""
        out = text
        # Remove clichés
        for c in ROBOTIC_AI_CLICHES:
            out = out.replace(c, "")

        # Enforce half-spaces
        out = re.sub(r"\bمی ([آ-ی]+)", "می‌\\1", out)
        out = re.sub(r"\bنمی ([آ-ی]+)", "نمی‌\\1", out)
        out = re.sub(r"([آ-ی]+) ها\b", "\\1‌ها", out)
        out = re.sub(r"([آ-ی]+) هایی\b", "\\1‌هایی", out)
        out = out.replace("پیش آزمون", "پیش‌آزمون")
        out = out.replace("پس آزمون", "پس‌آزمون")
        out = out.replace("روان شناسی", "روان‌شناسی")
        out = out.replace("روان شناختی", "روان‌شناختی")
        out = out.replace("خرده مقیاس", "خرده‌مقیاس")
        out = out.replace("خود کارآمدی", "خودکارآمدی")
        out = out.replace("فراتحلیل", "فرا-تحلیل")

        # Clean spaces
        out = re.sub(r"[ ]{2,}", " ", out).strip()
        return out


def main():
    parser = argparse.ArgumentParser(description="Digital Saber Academic Writing Reasoner")
    parser.add_argument("--demo", action="store_true", help="Run sample paragraph synthesis")

    args = parser.parse_args()
    reasoner = AcademicWritingReasoner()

    if args.demo or len(sys.argv) == 1:
        comp = {
            "claim": "مداخله مبتنی بر پذیرش و تعهد توانست مؤلفه خستگی هیجانی فرسودگی شغلی را در مرحله پس‌آزمون به طور معناداری تعدیل نماید.",
            "evidence": "یافته‌های تحلیل کوواریانس حاکی از تفاوت معنادار آماری بین دو گروه آزمایش و کنترل بود (F(1, 27) = 18.42, p < .001, η_p² = .41).",
            "interpretation": "این یافته با مدل هگزافلکس هیز و همکاران (۲۰۱۲) همگرایی نظری نشان می‌دهد؛ بدین معنا که تقویت گسلش شناختی و گسترش پذیرش هیجانی، نشخوار ذهنی پیرامون استرسورهای محیط بیمارستان را تقلیل داده است.",
            "qualification": "با این حال، به دلیل حجم نمونه محدود (N = 30)، تعمیم این دستاورد به سایر کادرهای بالینی نیازمند احتیاط روش‌شناختی است.",
            "implication": "پیشنهاد می‌شود مدیران بیمارستانی کارگاه‌های دوره‌ای مبتنی بر ACT را در برنامه‌های بازآموزی سلامت روان پرسنل ادغام نمایند."
        }
        res = reasoner.build_epistemic_paragraph(comp)
        audit = reasoner.audit_prose(res)

        print("\nDigital Saber Epistemic Paragraph:")
        print("=" * 75)
        print(res)
        print("\nProse Audit Metrics:")
        print(f"  Cadence Verdict:  {audit['academic_cadence_verdict']}")
        print(f"  Burstiness CV:    {audit['burstiness_cv']}")
        print(f"  Quality Score:    {audit['quality_score']} / 100")
        print("=" * 75)


if __name__ == "__main__":
    main()
