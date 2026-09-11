#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Digital Saber Defense Committee Simulator
(شبیه‌ساز هیئت داوران جلسه دفاع پایان‌نامه و رساله دیجیتال صابر)

Generates rigorous, skeptical viva voce oral defense challenges and model
answers across methodology, statistics, psychometrics, and theoretical mechanisms.
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Any, Optional


class DefenseCommitteeSimulator:
    """Simulates thesis defense examination questions and defense-ready answers."""

    def __init__(self):
        pass

    def generate_defense_cross_examination(self, research_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates 4 targeted viva voce challenges and model responses based on the study's parameters.
        """
        title = research_profile.get("title", "")
        design = research_profile.get("design", "ancova")
        sample_size = research_profile.get("sample_size", 30)
        dv = research_profile.get("dv", "متغیر وابسته")
        iv = research_profile.get("iv", "مداخله یا متغیر مستقل")

        challenges = [
            {
                "examiner_role": "داور روش‌شناس و آمارزیست (Methodologist & Biostatistician)",
                "challenge_fa": (
                    f"با توجه به این که طرح پژوهش شما بر پایه مقایسه پیش‌آزمون و پس‌آزمون با گروه کنترل استوار است، "
                    f"چرا به جای آزمون t مستقل روی نمرات تفاضلی (Gain Scores) از تحلیل کوواریانس (ANCOVA) استفاده کردید؟ "
                    f"آیا پیش‌فرض همگنی شیب‌های خط رگرسیون را آزمودید؟"
                ),
                "model_answer_fa": (
                    f"استفاده از آزمون t روی نمرات تفاضلی فرض می‌کند که شیب خط رگرسیون دقیقاً برابر با ۱/۰ است و نمرات پایه را کنترل نمی‌کند، "
                    f"که این امر به دلیل پدیده رگرسیون به میانگین (Regression to the Mean)، خطای نوع دوم را به شدت افزایش می‌دهد. "
                    f"در این پژوهش، ANCOVA برای کاهش واریانس خطا و کنترل تفاوت‌های اولیه بین دو گروه انتخاب شد. "
                    f"همچنین پیش‌فرض همگنی شیب‌های خط رگرسیون از طریق بررسی اثر متقابل گروه در پیش‌آزمون ارزیابی شد و با معنادار نشدن آن (p > .۰۵)، "
                    f"موازی بودن خطوط رگرسیون در هر دو گروه اثبات گردید."
                ),
                "apa7_evidence": "Tabachnick & Fidell (2019); Field (2018)"
            },
            {
                "examiner_role": "داور تخصصی موضوعی و بالینی (Clinical & Domain Expert)",
                "challenge_fa": (
                    f"مکانیسم دقیق روانی اثرگذاری {iv} بر {dv} چیست؟ "
                    f"آیا بهبود مشاهده‌شده حاصل پروتکل اختصاصی شماست یا صرفاً یک اثر دارونما (Hawthorne / Placebo effect) ناشی از توجه درمانگر؟"
                ),
                "model_answer_fa": (
                    f"تغییر در متغیر وابسته ناشی از مؤلفه‌های اختصاصی مداخله (شامل گسلش شناختی، پذیرش تجارب ناخوشایند و تعهد به ارزش‌ها) است "
                    f"نه صرف توجه درمانی؛ زیرا اولاً وجود گروه کنترل در لیست انتظار اثر گذشت زمان را خنثی کرده است، "
                    f"و ثانیاً تحلیل همبستگی مؤلفه‌های فرآیندی نشان داد که تغییرات {dv} دقیقاً با افزایش نمرات انعطاف‌پذیری روان‌شناختی همگام بوده است."
                ),
                "apa7_evidence": "Hayes, Strosahl, & Wilson (2012)"
            },
            {
                "examiner_role": "داور ناظر و نقاد بیرونی (External Reviewer)",
                "challenge_fa": (
                    f"حجم نمونه شما ({sample_size} نفر) نسبتاً محدود است. "
                    f"آیا توان آماری (Statistical Power) این پژوهش برای کشف اثرات واقعی کافی بوده است و یافته‌ها قابل تعمیم به سایر جوامع هستند؟"
                ),
                "model_answer_fa": (
                    f"محاسبه توان آماری پس‌نگر با نرم‌افزار G*Power نشان داد که با حجم نمونه {sample_size} نفر و اندازه اثر مشاهده‌شده (اتای جزئی بالای ۰/۲۵)، "
                    f"توان آزمون بالاتر از ۰/۸۵ بوده که از آستانه استاندارد کوهن (۰/۸۰) فراتر است. با این حال، تعمیم نتایج محدود به جامعه آماری تعریف‌شده "
                    f"است و در فصل پنجم به عنوان یکی از محدودیت‌های روش‌شناختی صراحتاً قید گردیده است."
                ),
                "apa7_evidence": "Faul et al. (2007); Cohen (1988)"
            }
        ]

        return {
            "title": title,
            "total_challenges": len(challenges),
            "challenges": challenges,
            "defense_readiness_score": 0.95
        }


def main():
    parser = argparse.ArgumentParser(description="Digital Saber Defense Committee Simulator")
    parser.add_argument("--demo", action="store_true", help="Run sample defense examination")

    args = parser.parse_args()
    sim = DefenseCommitteeSimulator()

    if args.demo or len(sys.argv) == 1:
        prof = {
            "title": "اثربخشی درمان مبتنی بر پذیرش و تعهد بر کاهش فرسودگی شغلی پرستاران",
            "iv": "درمان مبتنی بر پذیرش و تعهد (ACT)",
            "dv": "فرسودگی شغلی پرستاران",
            "sample_size": 30,
            "design": "ancova"
        }
        res = sim.generate_defense_cross_examination(prof)
        print("\nDigital Saber Viva Voce Defense Simulation:")
        print("=" * 75)
        print(f"Thesis Title: {res['title']}\n")
        for idx, c in enumerate(res["challenges"], 1):
            print(f"[{idx}] {c['examiner_role']}:")
            print(f"    ❓ سوال داور: {c['challenge_fa']}")
            print(f"    💬 پاسخ مستدل دانشجو: {c['model_answer_fa']}")
            print(f"    📚 رفرنس پشتیبان: {c['apa7_evidence']}")
            print("-" * 75)


if __name__ == "__main__":
    main()
