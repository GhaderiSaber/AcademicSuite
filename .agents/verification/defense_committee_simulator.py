#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Digital Saber Defense Committee Simulator
(شبیه‌ساز هیئت داوران جلسه دفاع پایان‌نامه و رساله دیجیتال صابر)
-------------------------------------------------------------------------------
Generates rigorous, skeptical viva voce oral defense challenges and model answers
across 5 committee roles (Methodologist, Biostatistician, Clinical Specialist,
Psychometrician, and Jury Chair).

Calculates deterministic Defense Readiness Index (DRI) and an authentic Iranian
20-point defense grade based on explicit itemized deductions, eliminating naive
or sycophantic 20/20 grading.
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Any, Optional


class DefenseCommitteeSimulator:
    """Simulates thesis defense examination questions and defense-ready answers with strict 20-point grading."""

    def __init__(self):
        pass

    def compute_defense_readiness_index(self, metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Computes the deterministic Iranian 20-point academic defense grade and Defense Readiness Index (DRI).
        Base score is 20.00 with itemized deductions across:
          - Publication Point Withholding (-1.0 to -1.5 pts if no accepted journal paper)
          - Sample Size & Statistical Power (-1.0 to -3.5 pts)
          - Statistical Assumptions & Reporting Rigor (-0.5 to -4.5 pts)
          - Data Plausibility & MSAI Anomaly (-1.5 to -5.0 pts)
          - APA 7 & Scientific Persian Typography (-0.5 to -1.5 pts)
          - Literature Concordance & Citations (-0.5 to -2.0 pts)
        """
        metrics = metrics or {}
        deductions: List[Dict[str, Any]] = []

        # 1. Statutory Publication Point Withholding
        # Under official Iranian graduate regulations (وزارت علوم / بهداشت), 1.0 to 1.5 points
        # are legally withheld until an official acceptance letter from an indexed scientific journal is submitted.
        has_publication = bool(
            metrics.get("has_publication_letter", False) or
            metrics.get("has_accepted_paper", False) or
            metrics.get("has_isi_isc_paper", False)
        )
        if not has_publication:
            deductions.append({
                "category": "قوانین آموزشی و مقالات مستخرج",
                "item": "عدم ارائه گواهی پذیرش قطعی مقاله علمی-پژوهشی / ISI (کسر امتیاز قانونی دفاع تا زمان پذیرش)",
                "deduction": 1.00
            })

        # 2. Sample Size & Statistical Power
        sample_size = metrics.get("sample_size")
        if sample_size is not None:
            try:
                n = int(sample_size)
                if n < 20:
                    deductions.append({
                        "category": "حجم نمونه و توان آماری",
                        "item": f"حجم نمونه بسیار بحرانی (N = {n} < ۲۰)؛ توان آزمون ناکافی و خطر خطای نوع دوم شدید",
                        "deduction": 3.00
                    })
                elif n < 30:
                    deductions.append({
                        "category": "حجم نمونه و توان آماری",
                        "item": f"حجم نمونه ناکافی در طرح‌های آزمایشی (N = {n} < ۳۰)؛ عدم کفایت حداقل ۱۵ نفر در هر گروه",
                        "deduction": 2.00
                    })
                elif n < 60:
                    deductions.append({
                        "category": "حجم نمونه و توان آماری",
                        "item": f"حجم نمونه متوسط (N = {n} < ۶۰)؛ توان آماری مرزی برای کشف اندازه‌های اثر متوسط",
                        "deduction": 1.00
                    })
            except (ValueError, TypeError):
                pass

        power = metrics.get("statistical_power")
        if power is not None:
            try:
                p_val = float(power)
                if p_val < 0.70:
                    deductions.append({
                        "category": "حجم نمونه و توان آماری",
                        "item": f"توان آماری برآورد شده کمتر از ۰.۷۰ است (Power = {p_val:.2f})",
                        "deduction": 1.50
                    })
                elif p_val < 0.80:
                    deductions.append({
                        "category": "حجم نمونه و توان آماری",
                        "item": f"توان آماری کمتر از آستانه استاندارد کوهن ۰.۸۰ است (Power = {p_val:.2f})",
                        "deduction": 0.75
                    })
            except (ValueError, TypeError):
                pass

        # 3. Statistical Assumptions & Reporting Rigor
        tot_assumptions = metrics.get("total_assumptions")
        passed_assumptions = metrics.get("assumptions_passed")
        if tot_assumptions is not None and passed_assumptions is not None:
            try:
                tot = int(tot_assumptions)
                passed = int(passed_assumptions)
                if tot > 0 and passed < tot:
                    failed = tot - passed
                    ded = round(min(4.50, failed * 1.50), 2)
                    deductions.append({
                        "category": "پیش‌فرض‌های آماری",
                        "item": f"نقض {failed} پیش‌فرض از {tot} پیش‌فرض آزمون بدون گزارش اصلاح راباست/ناپارامتریک",
                        "deduction": ded
                    })
            except (ValueError, TypeError):
                pass

        assumption_violations = metrics.get("assumption_violations")
        if assumption_violations:
            count = len(assumption_violations) if isinstance(assumption_violations, list) else int(assumption_violations)
            # Only add if not already captured via passed/total
            if tot_assumptions is None and count > 0:
                ded = round(min(4.50, count * 1.50), 2)
                deductions.append({
                    "category": "پیش‌فرض‌های آماری",
                    "item": f"نقض {count} مورد از پیش‌فرض‌های آماری داده‌ها",
                    "deduction": ded
                })

        p_zero_violations = metrics.get("p_zero_violations", 0) or metrics.get("reporting_p_zero", False)
        if p_zero_violations:
            cnt = p_zero_violations if isinstance(p_zero_violations, int) and p_zero_violations is not True else 1
            ded = round(min(1.50, cnt * 0.50), 2)
            deductions.append({
                "category": "استانداردهای گزارش‌نویسی آماری",
                "item": "گزارش نادرست سطح معناداری به صورت p = .000 بر خلاف استاندارد APA 7 (باید p < .001 قید شود)",
                "deduction": ded
            })

        df_mismatch = metrics.get("df_mismatch", False)
        if df_mismatch:
            deductions.append({
                "category": "دقت محاسبات آماری",
                "item": "عدم تطابق درجات آزادی (df) گزارش شده با ابعاد واقعی نمونه و متغیرها",
                "deduction": 1.50
            })

        # 4. Data Plausibility & MSAI Anomaly Index
        msai_count = metrics.get("msai_anomaly_count", 0)
        if msai_count:
            try:
                cnt = int(msai_count)
                if cnt == 1:
                    deductions.append({
                        "category": "سلامت و اصالت داده‌ها (MSAI)",
                        "item": "بروز ۱ ناهنجاری آماری (MSAI)؛ احتمال تحدید ساختگی واریانس یا تورم اندازه اثر",
                        "deduction": 1.50
                    })
                elif cnt == 2:
                    deductions.append({
                        "category": "سلامت و اصالت داده‌ها (MSAI)",
                        "item": "بروز ۲ ناهنجاری همزمان در شاخص چندسیگناله (MSAI)؛ آسیب جدی به روایی داده‌ها",
                        "deduction": 3.00
                    })
                elif cnt >= 3:
                    deductions.append({
                        "category": "سلامت و اصالت داده‌ها (MSAI)",
                        "item": f"هشدار قرمز اصالت داده‌ها با {cnt} سیگنال ناهنجاری؛ ظن جعل یا داده‌سازی (Fabrication Flag)",
                        "deduction": 5.00
                    })
            except (ValueError, TypeError):
                pass

        # 5. Persian Typography & APA 7 Format
        leading_zero_vio = metrics.get("leading_zero_violations", 0)
        if leading_zero_vio:
            try:
                cnt = int(leading_zero_vio)
                if cnt > 0:
                    ded = round(min(1.50, cnt * 0.25), 2)
                    deductions.append({
                        "category": "شیوه‌نامه نگارش فارسی و APA 7",
                        "item": f"حذف صفر قبل از ممیز در متن فارسی ({cnt} مورد؛ مطابق قاعده حفظ حتمی صفر در فارسی)",
                        "deduction": ded
                    })
            except (ValueError, TypeError):
                pass

        apa_violations = metrics.get("apa_format_violations", 0)
        if apa_violations:
            try:
                cnt = int(apa_violations)
                if cnt > 0:
                    ded = round(min(1.00, cnt * 0.25), 2)
                    deductions.append({
                        "category": "شیوه‌نامه نگارش فارسی و APA 7",
                        "item": f"خطاهای نگارشی و ساختار جداول APA 7 ({cnt} مورد؛ خطوط عمودی یا عدم ایتالیک نمادها)",
                        "deduction": ded
                    })
            except (ValueError, TypeError):
                pass

        # 6. Literature Concordance & Citations
        unv_citations = metrics.get("unverified_citations_count", 0)
        if unv_citations:
            try:
                cnt = int(unv_citations)
                if cnt > 0:
                    ded = round(min(2.00, cnt * 0.50), 2)
                    deductions.append({
                        "category": "اصالت منابع و پیشینه",
                        "item": f"ارجاعات بدون منبع در فهرست منابع پایانی ({cnt} مورد منبع شبح یا تطابق‌نیافته)",
                        "deduction": ded
                    })
            except (ValueError, TypeError):
                pass

        mechanism_weak = metrics.get("mechanism_depth_weak", False)
        if mechanism_weak:
            deductions.append({
                "category": "مبانی نظری و تبیین روان‌شناختی",
                "item": "تبیین مکانیسم‌های روان‌شناختی اثر سطحی بوده و فرضیه‌های رقیب بررسی نشده‌اند",
                "deduction": 1.00
            })

        # Calculate final 20-point score
        total_deduction = round(sum(d["deduction"] for d in deductions), 2)
        final_grade = max(0.00, round(20.00 - total_deduction, 2))
        dri_pct = round((final_grade / 20.00) * 100, 1)
        dri_ratio = round(final_grade / 20.00, 3)

        # Standard Iranian defense grading verdicts
        if final_grade >= 19.50:
            verdict = "استثنایی (نمره ۲۰ یا ۱۹/۵ - دفاع بی‌نقص، مشروط به ثبت مقاله معتبر)"
            status = "CLEARANCE_GRANTED_EXCEPTIONAL"
        elif final_grade >= 18.00:
            verdict = "بسیار خوب (نمره ۱۸ تا ۱۹/۲۵ - پذیرش استاندارد با اصلاحات جزئی)"
            status = "CLEARANCE_WITH_MINOR_REVISIONS"
        elif final_grade >= 16.00:
            verdict = "قابل قبول (نمره ۱۶ تا ۱۷/۷۵ - پذیرش مشروط به اصلاحات اساسی متدولوژی و آمار)"
            status = "REVISION_REQUIRED_MAJOR"
        elif final_grade >= 14.00:
            verdict = "مشروط شدید (نمره ۱۴ تا ۱۵/۷۵ - نیازمند بازتحلیل آماری و بازنویسی فصل‌های ۴ و ۵)"
            status = "CONDITIONAL_SUBSTANTIAL_DEFECTS"
        else:
            verdict = "غیرقابل قبول / رد اولیه دفاع (نمره زیر ۱۴ - نقایص بحرانی، عدم کفایت نمونه یا ناهنجاری شدید داده‌ها)"
            status = "DEFENSE_REJECTED"

        # Rubric breakdown normalized for backwards-compatibility
        meth_pen = sum(d["deduction"] for d in deductions if d["category"] == "حجم نمونه و توان آماری")
        stat_pen = sum(d["deduction"] for d in deductions if d["category"] in ["پیش‌فرض‌های آماری", "استانداردهای گزارش‌نویسی آماری", "دقت محاسبات آماری"])
        msai_pen = sum(d["deduction"] for d in deductions if d["category"] == "سلامت و اصالت داده‌ها (MSAI)")
        apa_pen = sum(d["deduction"] for d in deductions if d["category"] == "شیوه‌نامه نگارش فارسی و APA 7")
        lit_pen = sum(d["deduction"] for d in deductions if d["category"] in ["اصالت منابع و پیشینه", "مبانی نظری و تبیین روان‌شناختی", "قوانین آموزشی و مقالات مستخرج"])

        return {
            "defense_readiness_index": dri_ratio,
            "defense_readiness_percentage": dri_pct,
            "final_grade_out_of_20": final_grade,
            "total_deductions": total_deduction,
            "overall_verdict": verdict,
            "clearance_status": status,
            "deductions_ledger": deductions,
            "has_publication_letter": has_publication,
            "rubric_weights": {
                "methodological_soundness": {"weight": 0.25, "score": max(0.0, round(1.0 - (meth_pen / 5.0), 2))},
                "statistical_rigor": {"weight": 0.25, "score": max(0.0, round(1.0 - (stat_pen / 5.0), 2))},
                "apa7_compliance": {"weight": 0.20, "score": max(0.0, round(1.0 - (apa_pen / 4.0), 2))},
                "literature_concordance": {"weight": 0.15, "score": max(0.0, round(1.0 - (lit_pen / 3.0), 2))},
                "defensibility_index": {"weight": 0.15, "score": max(0.0, round(1.0 - (msai_pen / 3.0), 2))}
            }
        }

    def generate_defense_cross_examination(self, research_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates targeted viva voce challenges across 5 distinct faculty roles:
          1. Methodological Critic (داور روش‌شناس - ناظر بیرونی)
          2. Biostatistician (داور آمارزیست و تحلیل‌گر داده)
          3. Domain & Clinical Theorist (داور تخصصی موضوعی و بالینی)
          4. Psychometrician (داور روان‌سنجی و اندازه‌گیری)
          5. Jury Chair (رئیس هیئت داوران)
        """
        title = research_profile.get("title", "")
        design = research_profile.get("design", "ancova")
        sample_size = research_profile.get("sample_size", 30)
        dv = research_profile.get("dv", "متغیر وابسته")
        iv = research_profile.get("iv", "مداخله یا متغیر مستقل")
        scale_name = research_profile.get("scale_name", "پرسشنامه اصلی پژوهش")
        stats_data = research_profile.get("stats_results", {})

        # Dynamic parameter extraction
        f_val = stats_data.get("f_value") or stats_data.get("f_ratio") or 7.84
        p_val = stats_data.get("p_value") or 0.008
        eta2 = stats_data.get("partial_eta2") or stats_data.get("eta_squared") or 0.22
        slope_p = stats_data.get("slope_homogeneity_p") or 0.28
        slope_f = stats_data.get("slope_f") or 1.15
        alpha_val = stats_data.get("cronbach_alpha") or 0.84

        challenges = [
            {
                "role_id": "methodologist",
                "examiner_role": "داور اول: متخصص روش‌شناسی و ناظر خارجی (External Methodologist)",
                "challenge_fa": (
                    f"در طرح پژوهش شما ({design}) با حجم نمونه {sample_size} نفر، اولاً تخصیص تصادفی چگونه تضمین شد تا سوگیری انتخاب (Selection Bias) مخدوش‌کننده نباشد؟ "
                    f"ثانیاً چرا به جای استفاده از گروه کنترل فعال (Active Control) جهت تفکیک اثر دارونما، صرفاً به گروه کنترل در لیست انتظار اکتفا کردید؟"
                ),
                "model_answer_fa": (
                    f"تخصیص شرکت‌کنندگان با استفاده از روش تصادفی‌سازی بلوکی (Block Randomization) انجام شد تا تعادل حجمی دو گروه حفظ شود. "
                    f"در خصوص گروه کنترل فعال، به دلیل محدودیت‌های دسترسی بالینی و ملاحظات اخلاقی، گروه در لیست انتظار انتخاب شد؛ "
                    f"اما برای مهار خطای توجه درمانگر، مدت زمان تماس غیردرمانی بین هر دو گروه همتا گردید و این محدودیت در فصل پنجم به صراحت تحلیل شده است."
                ),
                "apa7_evidence": "Shadish, Cook, & Campbell (2002); Kline (2020)"
            },
            {
                "role_id": "biostatistician",
                "examiner_role": "داور دوم: متخصص آمارزیست و داده‌ها (Biostatistician & Data Auditor)",
                "challenge_fa": (
                    f"شما اندازه اثر جزئی η²={eta2:.2f} را گزارش کرده‌اید که اثری بزرگ محسوب می‌شود. "
                    f"آیا پیش‌فرض همگنی شیب خطوط رگرسیون (Homogeneity of Slopes) و همگنی واریانس‌ها (Levene) را آزمودید؟ "
                    f"اگر شیب‌ها ناهمگن باشند، مدل ANCOVA دچار شکست کامل می‌شود."
                ),
                "model_answer_fa": (
                    f"بله؛ پیش‌فرض همگنی شیب‌های خط رگرسیون از طریق برازش اثر متقابل پیش‌آزمون و متغیر گروه آزموده شد "
                    f"که نتیجه (F = {slope_f}, p = {slope_p}) نشان‌دهنده عدم معناداری اثر متقابل و اثبات موازی بودن خطوط رگرسیون بود. "
                    f"همچنین آزمون لوین برای تجانس واریانس خطای پس‌آزمون بررسی و تأیید شد؛ بنابراین مدل ANCOVA پایدار و معتبر است."
                ),
                "apa7_evidence": "Tabachnick & Fidell (2019); Field (2018)"
            },
            {
                "role_id": "clinical_theorist",
                "examiner_role": "داور سوم: داور تخصصی موضوعی و بالینی (Clinical & Domain Specialist)",
                "challenge_fa": (
                    f"مکانیسم دقیق روانی اثرگذاری {iv} بر {dv} چیست؟ "
                    f"آیا بهبود مشاهده‌شده ناشی از تکنیک‌های اختصاصی مداخله شما بوده است یا صرفاً اثر هاثورن (Hawthorne Effect) و اتحاد درمانی مشترک؟ "
                    f"آیا در مرحله پیگیری (Follow-up) پایداری درمان سنجیده شد؟"
                ),
                "model_answer_fa": (
                    f"تغییر در {dv} به طور مستقیم ناشی از بازسازی شناختی و پذیرش هیجانی پروتکل بوده است. "
                    f"برای تفکیک مؤلفه‌ها، مقیاس فرآیندی حین جلسات اجرا شد که نشان داد انعطاف‌پذیری روان‌شناختی به عنوان متغیر میانجی عمل کرده است. "
                    f"پایداری تغییرات نیز در پیگیری دو ماهه مورد ارزیابی قرار گرفت و ماندگاری اثر به لحاظ آماری تأیید شد."
                ),
                "apa7_evidence": "Beck (2011); Hayes, Strosahl, & Wilson (2012)"
            },
            {
                "role_id": "psychometrician",
                "examiner_role": "داور چهارم: متخصص روان‌سنجی و ابزار پژوهش (Psychometrician & Measurement Expert)",
                "challenge_fa": (
                    f"برای سنجش {dv} از {scale_name} استفاده کرده‌اید. آیا پایایی همسانی درونی (ضریب آلفای کرونباخ) "
                    f"و ساختار عاملی این ابزار در نمونه ایرانی شما بررسی و گزارش شد؟ نمرات وارونه (Reverse Items) چگونه محاسبه شدند؟"
                ),
                "model_answer_fa": (
                    f"پایایی همسانی درونی پرسشنامه در نمونه حاضر محاسبه و ضریب آلفای کرونباخ α = {alpha_val:.2f} حاصل شد که گویای پایایی مطلوب است. "
                    f"تمام گویه‌های معکوس بر اساس شیوه‌نامه استاندارد مقیاس با کدگذاری مجدد معکوس‌سازی شدند و سپس نمره کل استخراج گردید. "
                    f"روایی سازه نیز با تحلیل عاملی تأییدی در پیشینه هنجاریابی ایرانی منطبق بود."
                ),
                "apa7_evidence": "Cronbach (1951); Nunnally & Bernstein (1994)"
            },
            {
                "role_id": "jury_chair",
                "examiner_role": "داور پنجم: رئیس هیئت داوران و ناظر جمع‌بندی (Jury Chair & Synthesis)",
                "challenge_fa": (
                    f"با توجه به جامعه آماری محدود و شیوه نمونه‌گیری در دسترس، تعمیم‌پذیری اکولوژیک (Ecological Generalizability) یافته‌های شما تا چه اندازه معتبر است؟ "
                    f"آیا مجوزهای اخلاقی کد اخلاق بالینی و رضایت آگاهانه قبل از مداخله ثبت گردید؟"
                ),
                "model_answer_fa": (
                    f"پژوهش دارای کد تأییدیه کارگروه اخلاق در پژوهش است و فرم رضایت آگاهانه مکتوب از تمام شرکت‌کنندگان اخذ گردید. "
                    f"در زمینه تعمیم‌پذیری، نتایج مستقیماً به جامعه مشابه تعمیم‌پذیر است و کاربرد آن برای سایر بافت‌ها نیازمند احتیاط بالینی "
                    f"و تکرار تجربی در نمونه‌های چندمرکزی (Multi-center) است که در پیشنهادات پژوهش قید شد."
                ),
                "apa7_evidence": "APA Ethical Principles (2017); World Medical Association Declaration of Helsinki (2013)"
            }
        ]

        # Calculate genuine Defense Readiness Index with itemized deductions
        audit_metrics = dict(research_profile.get("audit_metrics", {}))
        audit_metrics.setdefault("sample_size", sample_size)
        if "has_publication_letter" not in audit_metrics and "has_publication_letter" in research_profile:
            audit_metrics["has_publication_letter"] = research_profile["has_publication_letter"]

        dri_summary = self.compute_defense_readiness_index(audit_metrics)

        return {
            "title": title,
            "total_challenges": len(challenges),
            "challenges": challenges,
            "final_grade_out_of_20": dri_summary["final_grade_out_of_20"],
            "defense_readiness_score": dri_summary["defense_readiness_index"],
            "defense_readiness_percentage": dri_summary["defense_readiness_percentage"],
            "defense_readiness_summary": dri_summary
        }


def main():
    parser = argparse.ArgumentParser(description="Digital Saber Defense Committee Simulator")
    parser.add_argument("--demo", action="store_true", help="Run sample defense examination")
    parser.add_argument("--with-pub", action="store_true", help="Simulate defense with confirmed publication letter")

    args = parser.parse_args()
    sim = DefenseCommitteeSimulator()

    prof = {
        "title": "اثربخشی درمان مبتنی بر پذیرش و تعهد بر کاهش فرسودگی شغلی پرستاران",
        "iv": "درمان مبتنی بر پذیرش و تعهد (ACT)",
        "dv": "فرسودگی شغلی پرستاران",
        "scale_name": "پرسشنامه فرسودگی شغلی مسلش (MBI)",
        "sample_size": 30,
        "design": "ancova",
        "has_publication_letter": args.with_pub,
        "audit_metrics": {
            "sample_size": 30,
            "has_publication_letter": args.with_pub,
            "assumptions_passed": 4,
            "total_assumptions": 4,
            "leading_zero_violations": 0,
            "unverified_citations_count": 0,
            "msai_anomaly_count": 0
        }
    }

    res = sim.generate_defense_cross_examination(prof)
    dri = res["defense_readiness_summary"]

    print("\n" + "=" * 80)
    print(f"🎯 DIGITAL SABER VIVA VOCE DEFENSE SIMULATION: {res['title']}")
    print("=" * 80)
    print(f"🏅 نمره نهایی دفاع از ۲۰:       {dri['final_grade_out_of_20']:.2f} / ۲۰.۰۰")
    print(f"📊 درصد آمادگی دفاع (DRI):    {dri['defense_readiness_percentage']}%  [{dri['clearance_status']}]")
    print(f"⚖️ حکم نهایی هیئت داوران:       {dri['overall_verdict']}")
    print("-" * 80)
    print("📋 صورت‌جلسه کسورات نمره (ITEMIZED DEDUCTIONS LEDGER):")
    if dri["deductions_ledger"]:
        for idx, d in enumerate(dri["deductions_ledger"], 1):
            print(f"  [{idx}] {d['category']}: -{d['deduction']:.2f} نمره ({d['item']})")
    else:
        print("  • هیچ‌گونه نقصی یافت نشد؛ نمره کامل دفاع احراز گردید.")
    print("-" * 80)
    print("5-ROLE VIVA VOCE CROSS-EXAMINATION CHALLENGES:")
    for idx, c in enumerate(res["challenges"], 1):
        print(f"\n[{idx}] {c['examiner_role']}:")
        print(f"    ❓ سوال داور: {c['challenge_fa']}")
        print(f"    💬 پاسخ مستدل دانشجو: {c['model_answer_fa']}")
        print(f"    📚 رفرنس پشتیبان: {c['apa7_evidence']}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()
