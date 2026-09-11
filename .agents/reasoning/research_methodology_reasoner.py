#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Digital Saber Research Methodology Reasoner
(موتور استدلال روش‌شناسی پژوهش و طراحی ساختار تحقیق دیجیتال صابر)

Translates research aims into coherent methodological architectures:
  Research Aim -> Design -> Measurement Level -> Control Strategies ->
  Sampling & Power -> Validity Threats & Defensibility Blueprint
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Any, Optional


class ResearchMethodologyReasoner:
    """Cognitive reasoner for designing and validating research methodologies."""

    def __init__(self):
        pass

    def design_methodology(self, proposal_spec: Dict[str, Any]) -> Dict[str, Any]:
        """
        Synthesizes a complete methodological blueprint from an initial research proposal specification.
        """
        title = proposal_spec.get("title", "")
        aim = proposal_spec.get("aim", "").lower()
        variables = proposal_spec.get("variables", [])
        population = proposal_spec.get("population", "عمومی")
        is_intervention = bool(proposal_spec.get("is_intervention", False) or "اثربخشی" in title or "مداخله" in title)
        has_mediation = bool(proposal_spec.get("has_mediation", False) or "میانجی" in title)
        has_moderation = bool(proposal_spec.get("has_moderation", False) or "تعدیل" in title)

        # 1. Design Determination
        if is_intervention:
            design_type = "نیمه‌آزمایشی با پیش‌آزمون، پس‌آزمون و گروه کنترل"
            design_code = "quasi_experimental_pre_post_control"
            recommended_sample = "حداقل ۳۰ نفر (۱۵ نفر گروه آزمایش، ۱۵ نفر گروه کنترل)"
            min_n = 30
            internal_validity_threats = [
                "اثر رگرسیون به میانگین در صورت پایین بودن نمرات پایه",
                "اثر هم‌افزایی بلوغ و تاریخچه در صورت طولانی شدن فاصله پیش تا پس‌آزمون",
                "افت آزمودنی (Mortality/Attrition) در طول جلسات مداخله"
            ]
            control_mechanisms = [
                "گمارش همگن آزمودنی‌ها در گروه‌ها",
                "کنترل آماری نمرات پیش‌آزمون با تحلیل کوواریانس (ANCOVA)",
                "اجرای پروتکل مداخله یکدست توسط درمانگر واحد با سوپرویژن"
            ]
        elif has_mediation or has_moderation or "مدل" in title:
            design_type = "توصیفی-همبستگی از نوع مدل‌یابی علّی/معادلات ساختاری"
            design_code = "correlational_structural_equation"
            recommended_sample = "حداقل ۲۰۰ تا ۳۰۰ نفر (بر اساس قاعده ۱۰ تا ۱۵ شرکت‌کننده به ازای هر متغیر یا پارامتر آزاد)"
            min_n = 200
            internal_validity_threats = [
                "سوگیری واریانس روش مشترک (Common Method Variance) در اثر جمع‌آوری همزمان خودگزارش‌دهی",
                "عدم امکان استنتاج علّی قطعی در داده‌های مقطعی"
            ]
            control_mechanisms = [
                "استفاده از مقیاس‌های معتبر با روایی همگرا و واگرا",
                "اطمینان از محرمانگی و بی‌نام بودن پاسخ‌دهندگان جهت کاهش سوگیری مطلوبیت اجتماعی",
                "اعمال روش‌های بوت‌استرپینگ در ارزیابی اثرات غیرمستقیم"
            ]
        else:
            design_type = "توصیفی-همبستگی مقطعی"
            design_code = "cross_sectional_correlational"
            recommended_sample = "حداقل ۱۰۰ تا ۱۵۰ نفر (بر اساس جدول بارتلت یا فرمول کوکران)"
            min_n = 100
            internal_validity_threats = ["سوگیری خودانتخابی نمونه", "روابط ساختگی ناشی از متغیرهای مخدوش‌کننده ثبت‌نشده"]
            control_mechanisms = ["نمونه‌گیری تصادفی طبقه‌ای یا خوشه‌ای", "کنترل آماری متغیرهای جمعیت‌شناختی مخدوش‌کننده در رگرسیون"]

        return {
            "title": title,
            "recommended_design": design_type,
            "design_code": design_code,
            "minimum_recommended_sample_size": min_n,
            "sample_size_formula_justification": recommended_sample,
            "internal_validity_threats": internal_validity_threats,
            "recommended_control_mechanisms": control_mechanisms,
            "chapter3_blueprint": {
                "section_1_design": f"طرح پژوهش حاضر، {design_type} است.",
                "section_2_population": f"جامعه آماری شامل تمامی {population} می‌باشد.",
                "section_3_sampling": f"روش نمونه‌گیری هدفمند با رعایت ملاک‌های ورود و خروج، همراه با محاسبه توان آماری G*Power جهت تضمین توان بالای ۰/۸۰.",
                "section_4_analysis_plan": "بررسی مفروضه‌های پارامتریک و سپس اجرای تحلیل آماری متناسب (ANCOVA/PROCESS/SEM)."
            }
        }


def main():
    parser = argparse.ArgumentParser(description="Digital Saber Research Methodology Reasoner")
    parser.add_argument("--demo", action="store_true", help="Run sample methodology design")

    args = parser.parse_args()
    reasoner = ResearchMethodologyReasoner()

    if args.demo or len(sys.argv) == 1:
        spec = {
            "title": "اثربخشی درمان مبتنی بر شفقت بر خودانتقادی و شرم دختران نوجوان",
            "population": "دختران نوجوان مراکز مشاوره شهر تهران",
            "is_intervention": True
        }
        res = reasoner.design_methodology(spec)
        print("\nDigital Saber Methodology Blueprint:")
        print("=" * 75)
        print(f"Title:        {res['title']}")
        print(f"Design:       {res['recommended_design']}")
        print(f"Recommended N: {res['sample_size_formula_justification']}")
        print("\nThreats to Internal Validity:")
        for t in res["internal_validity_threats"]:
            print(f"  ⚠️  {t}")
        print("\nDefensive Control Mechanisms:")
        for c in res["recommended_control_mechanisms"]:
            print(f"  🛡️  {c}")
        print("=" * 75)


if __name__ == "__main__":
    main()
