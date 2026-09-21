#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/skills/persian-literature-review-builder/examples/sample_synthesis_matrix_payload.py
Reference schema and sample data for Chapter 2 Literature Review Thematic Synthesis Matrix.

Features:
- Multi-theme clustering (Direct effects, Mediating mechanisms, Moderating interactions)
- Iranian empirical literature (1400–1405 SH) and International empirical literature (2021–2026)
- Standardized statistical reporting (ANCOVA, SEM, PROCESS bootstrap mediation, hierarchical regression)
- Rigorous APA 7 and Persian leading zero compliance (۰.۰۰۱ > p)
"""

from typing import Dict, Any


def get_sample_payload() -> Dict[str, Any]:
    """Returns a defense-ready sample payload for Chapter 2 Literature Review Synthesis Matrix."""
    return {
        "project_id": "dissertation_burnout_act_2026",
        "topic": "اثربخشی درمان مبتنی بر پذیرش و تعهد بر فرسودگی شغلی معلمان با میانجی‌گری انعطاف‌پذیری روان‌شناختی",
        "topic_en": "Effectiveness of Acceptance and Commitment Therapy on Teacher Burnout with the Mediating Role of Psychological Flexibility",
        "review_period": "2021–2026 / ۱۴۰۰–۱۴۰۵",
        "themes": [
            {
                "theme_id": "THEME_1",
                "title": "اثربخشی مداخلات مبتنی بر پذیرش و تعهد بر کاهش فرسودگی شغلی و ابعاد آن",
                "title_en": "Effectiveness of ACT Interventions on Reducing Teacher Burnout and Its Sub-dimensions",
                "theoretical_mechanism": "نظریه حفاظت از منابع (COR) و فرایندهای شش‌گانه هگزافلکس (Hexaflex)",
                "hypothesized_path": "ACT -> Occupational Burnout (Direct Effect)",
                "studies": [
                    {
                        "citation_fa": "احمدی و رضایی (۱۴۰۲)",
                        "citation_en": "Ahmadi & Rezaei (2023)",
                        "doi": "10.1016/j.burn.2023.101234",
                        "year": 1402,
                        "year_gregorian": 2023,
                        "region": "iranian",
                        "population": "معلمان دوره متوسطه شهر تهران",
                        "sample_size": 40,
                        "sampling_method": "نمونه‌گیری تصادفی خوشه‌ای چندمرحله‌ای",
                        "design": "quasi_experimental",
                        "design_fa": "نیمه‌آزمایشی با پیش‌آزمون-پس‌آزمون و گروه کنترل (همراه با پیگیری دوماهه)",
                        "iv": "درمان مبتنی بر پذیرش و تعهد (۸ جلسه ۹۰ دقیقه‌ای)",
                        "dv": "فرسودگی شغلی (خستگی عاطفی، مسخ شخصیت، احساس عدم کارایی فردی)",
                        "mediators": [],
                        "moderators": [],
                        "instruments": [
                            {
                                "name": "پرسشنامه فرسودگی شغلی مسلش (MBI-ES)",
                                "reliability_alpha": 0.88,
                                "reliability_omega": 0.89
                            }
                        ],
                        "key_findings_fa": "کاهش معنادار نمرات خستگی هیجانی و مسخ شخصیت در گروه آزمایش در مقایسه با گروه کنترل در مراحل پس‌آزمون و پیگیری",
                        "statistical_results": {
                            "test_type": "ANCOVA",
                            "test_statistic": "F(1, 37) = 18.45",
                            "p_value": 0.0008,
                            "p_value_formatted_fa": "۰.۰۰۱ > p",
                            "p_value_formatted_en": "p < .001",
                            "effect_size_type": "partial_eta_squared",
                            "effect_size_value": 0.33,
                            "effect_size_label": "بزرگ (Large)"
                        },
                        "finding_direction": "supporting",
                        "theoretical_contribution": "تأیید نقش گسلش شناختی و پذیرش تجربی در جلوگیری از تخلیه منابع انرژی روانی معلمان",
                        "limitations_and_gaps": "حجم نمونه محدود به مدارس دولتی و عدم پایش بلندمدت بیش از دو ماه"
                    },
                    {
                        "citation_fa": "ویلیامز و همکاران (۲۰۲۴)",
                        "citation_en": "Williams et al. (2024)",
                        "doi": "10.1037/edu0000812",
                        "year": 1403,
                        "year_gregorian": 2024,
                        "region": "international",
                        "population": "معلمان مدارس دولتی انگلستان",
                        "sample_size": 112,
                        "sampling_method": "کارآزمایی تصادفی‌شده کنترل‌دار با تخصیص پنهان (RCT)",
                        "design": "rct",
                        "design_fa": "کارآزمایی بالینی تصادفی‌شده کنترل‌دار (RCT دوگروهی)",
                        "iv": "پروتکل آنلاین گروهی درمان پذیرش و تعهد (۶ هفته)",
                        "dv": "خستگی هیجانی معلمان و فرسودگی شغلی کلی",
                        "mediators": ["انعطاف‌پذیری روان‌شناختی"],
                        "moderators": [],
                        "instruments": [
                            {
                                "name": "پرسشنامه فرسودگی شغلی کریستنسن (CBI)",
                                "reliability_alpha": 0.91,
                                "reliability_omega": 0.92
                            }
                        ],
                        "key_findings_fa": "کاهش بارز و پایدار نشانه‌های فرسودگی شغلی در پیگیری‌های ۳ و ۶ ماهه",
                        "statistical_results": {
                            "test_type": "Repeated Measures Mixed ANOVA",
                            "test_statistic": "F(2, 109) = 14.12",
                            "p_value": 0.0001,
                            "p_value_formatted_fa": "۰.۰۰۱ > p",
                            "p_value_formatted_en": "p < .001",
                            "effect_size_type": "partial_eta_squared",
                            "effect_size_value": 0.21,
                            "effect_size_label": "متوسط به بالا"
                        },
                        "finding_direction": "supporting",
                        "theoretical_contribution": "اثبات پایداری ۶ ماهه اثرات آموزش مهارت‌های حضور در لحظه اکنون و ارزش‌گذاری رفتاری",
                        "limitations_and_gaps": "نرخ ریزش ۱۵ درصدی در مرحله پیگیری شش‌ماهه"
                    },
                    {
                        "citation_fa": "حسینی و فراهانی (۱۴۰۱)",
                        "citation_en": "Hosseini & Farahani (2022)",
                        "doi": "10.22059/jpsych.2022.987654",
                        "year": 1401,
                        "year_gregorian": 2022,
                        "region": "iranian",
                        "population": "معلمان مدارس استثنایی استان البرز",
                        "sample_size": 34,
                        "sampling_method": "نمونه‌گیری هدفمند با گمارش تصادفی",
                        "design": "quasi_experimental",
                        "design_fa": "پیش‌آزمون-پس‌آزمون با گروه کنترل",
                        "iv": "مداخله ACT مبتنی بر شفقت خود",
                        "dv": "فرسودگی شغلی و تاب‌آوری روانی",
                        "mediators": [],
                        "moderators": [],
                        "instruments": [
                            {
                                "name": "پرسشنامه فرسودگی شغلی مسلش (MBI)",
                                "reliability_alpha": 0.86,
                                "reliability_omega": 0.87
                            }
                        ],
                        "key_findings_fa": "بهبود ابعاد عملکرد فردی و کاهش خستگی عاطفی در پس‌آزمون با پایداری در پیگیری ۴۵ روزه",
                        "statistical_results": {
                            "test_type": "MANCOVA",
                            "test_statistic": "Wilks' Lambda = 0.42, F(3, 30) = 13.81",
                            "p_value": 0.0002,
                            "p_value_formatted_fa": "۰.۰۰۱ > p",
                            "p_value_formatted_en": "p < .001",
                            "effect_size_type": "partial_eta_squared",
                            "effect_size_value": 0.58,
                            "effect_size_label": "بزرگ (Large)"
                        },
                        "finding_direction": "supporting",
                        "theoretical_contribution": "هم‌افزایی مؤلفه‌های ذهن‌آگاهی ACT با راهبردهای شفقت‌ورزی در بسترهای پرتنش کاری",
                        "limitations_and_gaps": "محدودیت به معلمان استثنایی و تعمیم‌پذیری نامشخص به معلمان مدارس عادی"
                    }
                ]
            },
            {
                "theme_id": "THEME_2",
                "title": "نقش میانجی‌گری انعطاف‌پذیری روان‌شناختی در رابطه میان استرسورهای شغلی و فرسودگی معلمان",
                "title_en": "Mediating Role of Psychological Flexibility in the Relationship Between Occupational Stressors and Burnout",
                "theoretical_mechanism": "مدل فرایند استرس-واکنش لازاروس و فولکمن همراه با چارچوب هگزافلکس هیز",
                "hypothesized_path": "Occupational Stressors -> Psychological Flexibility -> Burnout (Indirect Effect)",
                "studies": [
                    {
                        "citation_fa": "صادقی، مرادی و افشار (۱۴۰۲)",
                        "citation_en": "Sadeghi, Moradi & Afshar (2023)",
                        "doi": "10.30495/jedu.2023.765432",
                        "year": 1402,
                        "year_gregorian": 2023,
                        "region": "iranian",
                        "population": "معلمان مقطع ابتدایی استان اصفهان",
                        "sample_size": 280,
                        "sampling_method": "نمونه‌گیری تصادفی طبقه‌ای متناسب",
                        "design": "sem",
                        "design_fa": "همبستگی از نوع مدل‌سازی معادلات ساختاری (SEM)",
                        "iv": "فشارهای شغلی معلمان (Teacher Occupational Stress)",
                        "dv": "فرسودگی شغلی معلمان",
                        "mediators": ["انعطاف‌پذیری روان‌شناختی"],
                        "moderators": [],
                        "instruments": [
                            {
                                "name": "پرسشنامه پذیرش و عمل نسخه دوم (AAQ-II)",
                                "reliability_alpha": 0.89,
                                "reliability_omega": 0.90
                            },
                            {
                                "name": "پرسشنامه فرسودگی شغلی مسلش (MBI)",
                                "reliability_alpha": 0.90,
                                "reliability_omega": 0.91
                            }
                        ],
                        "key_findings_fa": "تأیید برازش مدل ساختاری و معناداری مسیر غیرمستقیم از طریق انعطاف‌پذیری روان‌شناختی",
                        "statistical_results": {
                            "test_type": "Bootstrap Mediation (PROCESS Model 4, 5000 resamples)",
                            "test_statistic": "β_indirect = 0.28, z = 4.35",
                            "p_value": 0.0004,
                            "p_value_formatted_fa": "۰.۰۰۱ > p",
                            "p_value_formatted_en": "p < .001",
                            "effect_size_type": "beta",
                            "effect_size_value": 0.28,
                            "effect_size_label": "متوسط (Medium)"
                        },
                        "finding_direction": "supporting",
                        "theoretical_contribution": "اثبات نقش حفاظتی گسلش و پذیرش در خنثی‌سازی اثرات فرسایش‌دهنده تنش‌های کلاسی",
                        "limitations_and_gaps": "طرح مقطعی و عدم گردآوری داده‌های طولی چندموجی"
                    },
                    {
                        "citation_fa": "مارتینز و رودریگز (۲۰۲۲)",
                        "citation_en": "Martinez & Rodriguez (2022)",
                        "doi": "10.1016/j.tate.2022.103756",
                        "year": 1401,
                        "year_gregorian": 2022,
                        "region": "international",
                        "population": "معلمان شاغل در مناطق محروم اسپانیا",
                        "sample_size": 345,
                        "sampling_method": "نمونه‌گیری تصادفی چندمرحله‌ای",
                        "design": "longitudinal",
                        "design_fa": "طراحی طولی سه موجی (۳ زمان سنجش به فاصله ۴ ماه)",
                        "iv": "فشارهای شغلی معلمان در موج اول (T1)",
                        "dv": "فرسودگی شغلی معلمان در موج سوم (T3)",
                        "mediators": ["انعطاف‌پذیری روان‌شناختی در موج دوم (T2)"],
                        "moderators": [],
                        "instruments": [
                            {
                                "name": "پرسشنامه انعطاف‌پذیری روان‌شناختی کاری (WAAQ)",
                                "reliability_alpha": 0.88,
                                "reliability_omega": 0.88
                            }
                        ],
                        "key_findings_fa": "انعطاف‌پذیری روان‌شناختی در موج ۲ به‌طور کامل میانجی اثر فشارهای شغلی موج ۱ بر فرسودگی موج ۳ بود",
                        "statistical_results": {
                            "test_type": "Cross-Lagged Panel Mediation",
                            "test_statistic": "β_indirect = 0.24, 95% BCa CI [0.14, 0.35]",
                            "p_value": 0.001,
                            "p_value_formatted_fa": "۰.۰۰۱ > p",
                            "p_value_formatted_en": "p < .001",
                            "effect_size_type": "beta",
                            "effect_size_value": 0.24,
                            "effect_size_label": "متوسط (Medium)"
                        },
                        "finding_direction": "supporting",
                        "theoretical_contribution": "تأیید تقدم زمانی متغیر واسطه‌ای و کنترل اثرات خودهمبسته پایه‌ای در طول زمان",
                        "limitations_and_gaps": "محدودیت تعمیم به جوامع شرقی با ساختارهای متمرکز آموزشی"
                    }
                ]
            }
        ],
        "master_research_gaps": [
            {
                "gap_id": "GAP-01",
                "theme_title": "مداخله‌های ACT بر فرسودگی شغلی معلمان",
                "theoretical_gap": "تمرکز عمده مطالعات بر خستگی هیجانی منفرد و غفلت از تحلیل همزمان سازوکارهای مسخ شخصیت و باورهای ناکارآمدی حرفه‌ای",
                "methodological_gap": "غلبه طرح‌های نیمه‌آزمایشی فاقد گروه کنترل فعال و پیگیری‌های کوتاه‌مدت کمتر از ۳ ماه",
                "sampling_gap": "فقدان بررسی اثرات مداخله در بافت آموزشی مدارس دولتی پرتراکم ایران با حجم نمونه استاندارد",
                "implication_for_current_thesis": "استفاده از طرح آزمایشی دقیق با پیگیری فصلی و اندازه‌گیری ابعاد سه‌گانه فرسودگی شغلی"
            },
            {
                "gap_id": "GAP-02",
                "theme_title": "نقش واسطه‌ای انعطاف‌پذیری روان‌شناختی",
                "theoretical_gap": "ابهام در میزان تمایز میان مؤلفه‌های ذهن‌آگاهی و تعهد عملی در کاهش بار فرسودگی شغلی",
                "methodological_gap": "اتکای حداکثری به طرح‌های همبستگی همزمان و عدم استفاده از بوت‌استراپینگ ۵۰۰۰ نمونه‌ای با کنترل مخدوش‌کننده‌های جمعیت‌شناختی",
                "sampling_gap": "عدم تفکیک معلمان بر حسب سابقه تدریس و سطح مقطع تحصیلی در تحلیل مسیرهای میانجی",
                "implication_for_current_thesis": "آزمون بوت‌استراپ با ۵۰۰۰ نمونه‌گیری مجدد در چارچوب مدل PROCESS هیز با کنترل سن و سابقه"
            }
        ]
    }


if __name__ == "__main__":
    import json
    print(json.dumps(get_sample_payload(), indent=2, ensure_ascii=False))
