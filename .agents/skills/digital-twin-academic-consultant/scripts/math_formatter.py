"""
math_formatter.py — Native Mathematical Formula Formatting Engine for Academic Desk

Adheres strictly to APA 7th Edition statistical reporting standards and Persian academic conventions:
1. Italicization: Latin statistical symbols (M, SD, t, F, p, r, R², β, B, z, SE, d, f) MUST be italicized.
   Greek letters (α, β, η², χ², ω, λ, Δ) remain regular.
2. Decimals:
   - 2 decimal places for test statistics, effect sizes, and means.
   - Exactly 3 decimal places for p-values.
3. Leading zero:
   - Omitted in English text for bounded metrics: p = .014, r = .48, ηp² = .24, R² = .38.
   - Strictly preserved in Persian text: ۰.۰۱۴, ۰.۰۰۱ > p, ۰.۴۸, ۰.۲۴. Never write .۰۵ or .۰۰۱.
   - Never report p = .000 -> English: p < .001, Persian: ۰.۰۰۱ > p (or p < ۰.۰۰۱).
4. Telegram Dual-Tier Rendering:
   - Universal Telegram HTML: <i>, <sub>, <sup>, and Unicode math glyphs (η, χ, β, α, Δ, λ, ±, ≠, ≤, ≥, √, ∑).
   - LaTeX Monospaced Blocks: <pre><code class="language-latex">...</code></pre>.
   - Viva Voce Defense Card Layout: Box-drawing card with oral defense speaking script for Topic 122.
"""

import html
from typing import Dict, Any, Optional, List, Tuple


def to_persian_digits(text: str) -> str:
    """Convert ASCII digits to authentic Persian digits (۰-۹)."""
    fa_digits = "۰۱۲۳۴۵۶۷۸۹"
    en_digits = "0123456789"
    trans = str.maketrans(en_digits, fa_digits)
    return str(text).translate(trans)


def format_stat_value(val: float, decimals: int = 2, lang: str = "en", omit_leading_zero: bool = False) -> str:
    """
    Format a statistical number according to APA 7th and language rules.
    - If lang == 'fa': Always preserve leading zero, use standard dot ('.'), convert digits to Persian.
    - If lang == 'en': If omit_leading_zero is True (for metrics bounded [0, 1] like p, r, R²), drop leading '0'.
    """
    if val is None:
        return "N/A"
    
    formatted = f"{val:.{decimals}f}"
    
    if lang == "fa":
        # Rule: Persian strictly preserves leading zero: e.g. ۰.۰۵, ۰.۰۰۱
        return to_persian_digits(formatted)
    else:
        if omit_leading_zero and formatted.startswith("0."):
            formatted = formatted[1:]  # .014
        elif omit_leading_zero and formatted.startswith("-0."):
            formatted = "-" + formatted[2:]
        return formatted


def format_p_value(p: float, lang: str = "en") -> Tuple[str, str]:
    """
    Format p-value complying with APA 7th:
    - Never write p = .000 or p = 0.000.
    - If p < .001:
        English: "p < .001", Telegram HTML: "<i>p</i> &lt; .001"
        Persian: "p < ۰.۰۰۱" (or "۰.۰۰۱ > p"), Telegram HTML: "<i>p</i> &lt; ۰.۰۰۱"
    - Otherwise 3 decimal places.
    Returns tuple: (raw_text, telegram_html).
    """
    if p is None:
        return ("p = N/A", "<i>p</i> = N/A")
    
    if p < 0.001:
        if lang == "fa":
            raw = "۰.۰۰۱ > p"
            t_html = "<i>p</i> &lt; ۰.۰۰۱"
        else:
            raw = "p < .001"
            t_html = "<i>p</i> &lt; .001"
        return (raw, t_html)
    
    val_str = format_stat_value(p, decimals=3, lang=lang, omit_leading_zero=(lang == "en"))
    if lang == "fa":
        raw = f"p = {val_str}"
        t_html = f"<i>p</i> = {val_str}"
    else:
        raw = f"p = {val_str}"
        t_html = f"<i>p</i> = {val_str}"
    return (raw, t_html)


class AcademicMathFormatter:
    """Formatter engine for statistical formulas and viva voce defense justifications."""

    # ---------------------------------------------------------
    # 1. ANCOVA / ANOVA Test Formatting
    # ---------------------------------------------------------
    @staticmethod
    def format_ancova(
        f_val: float,
        df1: int,
        df2: int,
        p_val: float,
        eta_p2: float,
        covariate: str = "Pre-test",
        dependent_var: str = "Post-test",
        lang: str = "fa"
    ) -> Dict[str, str]:
        """
        Format ANCOVA results:
        F(df1, df2) = f_val, p = p_val, ηp² = eta_p2
        """
        f_str = format_stat_value(f_val, 2, lang)
        eta_str = format_stat_value(eta_p2, 2, lang, omit_leading_zero=(lang == "en"))
        df1_str = to_persian_digits(str(df1)) if lang == "fa" else str(df1)
        df2_str = to_persian_digits(str(df2)) if lang == "fa" else str(df2)
        _, p_html = format_p_value(p_val, lang)
        p_raw, _ = format_p_value(p_val, lang)

        if lang == "fa":
            sep = "، "
            raw_apa = f"F({df1}, {df2}) = {f_val:.2f}, {p_raw}, ηp² = {eta_p2:.2f}"
            t_html = f"<i>F</i>({df1_str}{sep}{df2_str}) = {f_str}{sep}{p_html}{sep}η<sub>p</sub>² = {eta_str}"
            model_eq = "<i>Y</i><sub>ij</sub> = μ + α<sub>i</sub> + β(<i>X</i><sub>ij</sub> - X̄) + ε<sub>ij</sub>"
            latex = f"F({df1}, {df2}) = {f_val:.2f},\\ p < .001,\\ \\eta_p^2 = {eta_p2:.2f}" if p_val < 0.001 else f"F({df1}, {df2}) = {f_val:.2f},\\ p = {p_val:.3f},\\ \\eta_p^2 = {eta_p2:.2f}"
        else:
            sep = ", "
            raw_apa = f"F({df1}, {df2}) = {f_val:.2f}, {p_raw}, ηp² = {eta_str}"
            t_html = f"<i>F</i>({df1_str}{sep}{df2_str}) = {f_str}{sep}{p_html}{sep}η<sub>p</sub>² = {eta_str}"
            model_eq = "<i>Y</i><sub>ij</sub> = μ + α<sub>i</sub> + β(<i>X</i><sub>ij</sub> - X̄) + ε<sub>ij</sub>"
            latex = f"F({df1}, {df2}) = {f_val:.2f},\\ {p_raw},\\ \\eta_p^2 = {eta_p2:.2f}"

        return {
            "test_name": "ANCOVA (Analysis of Covariance)",
            "test_name_fa": "تحلیل کوواریانس تک‌متغیری (ANCOVA)",
            "raw_apa": raw_apa,
            "t_html": t_html,
            "model_equation_html": model_eq,
            "latex": latex,
            "interpretation_fa": (
                f"اثر متغیر مستقل بر {dependent_var} با کنترل آماری اثر متغیر هم‌پراش ({covariate}) معنادار است "
                f"و اندازه اثر (η<sub>p</sub>² = {eta_str}) نشان‌دهنده تبیین واریانس قابل توجه است."
            ),
            "viva_defense_fa": (
                "«استفاده از تحلیل کوواریانس (ANCOVA) به جای ANOVA ساده به این دلیل الزامی بود که در طرح‌های نیمه‌آزمایشی، "
                "گمارش کاملاً تصادفی امکان‌پذیر نبوده و کنترل آماری نمرات پیش‌آزمون به عنوان متغیر هم‌پراش (Covariate)، "
                "خطای اندازه‌گیری (Error Variance) را به حداقل رسانده و توان آزمون (Statistical Power) را ارتقا می‌دهد.»"
            )
        }

    # ---------------------------------------------------------
    # 2. Structural Equation Modeling (SEM) & CFA Fit Indices
    # ---------------------------------------------------------
    @staticmethod
    def format_sem_fit(
        chi2: float,
        df: int,
        p_val: float,
        rmsea: float,
        cfi: float,
        tli: float,
        srmr: float,
        rmsea_ci: Tuple[float, float] = (0.000, 0.078),
        lang: str = "fa"
    ) -> Dict[str, str]:
        """
        Format SEM Model Fit Indices complying with Kline (2015) & Hu & Bentler (1999):
        χ²(df) = chi2, p = p_val, χ²/df = ratio, RMSEA = rmsea [90% CI], CFI = cfi, TLI = tli, SRMR = srmr
        """
        ratio = chi2 / df if df > 0 else 1.0
        chi2_str = format_stat_value(chi2, 2, lang)
        df_str = to_persian_digits(str(df)) if lang == "fa" else str(df)
        ratio_str = format_stat_value(ratio, 2, lang)
        rmsea_str = format_stat_value(rmsea, 3, lang, omit_leading_zero=(lang == "en"))
        cfi_str = format_stat_value(cfi, 3, lang, omit_leading_zero=(lang == "en"))
        tli_str = format_stat_value(tli, 3, lang, omit_leading_zero=(lang == "en"))
        srmr_str = format_stat_value(srmr, 3, lang, omit_leading_zero=(lang == "en"))
        ci_ll_str = format_stat_value(rmsea_ci[0], 3, lang, omit_leading_zero=(lang == "en"))
        ci_ul_str = format_stat_value(rmsea_ci[1], 3, lang, omit_leading_zero=(lang == "en"))
        _, p_html = format_p_value(p_val, lang)
        p_raw, _ = format_p_value(p_val, lang)

        sep = "، " if lang == "fa" else ", "
        raw_apa = (
            f"χ²({df}) = {chi2:.2f}, {p_raw}, χ²/df = {ratio:.2f}, "
            f"RMSEA = {rmsea:.3f} [90% CI: {rmsea_ci[0]:.3f}, {rmsea_ci[1]:.3f}], "
            f"CFI = {cfi:.3f}, TLI = {tli:.3f}, SRMR = {srmr:.3f}"
        )
        t_html = (
            f"χ²({df_str}) = {chi2_str}{sep}{p_html}{sep}χ²/<i>df</i> = {ratio_str}\n"
            f"RMSEA = {rmsea_str} [90% CI: {ci_ll_str}{sep}{ci_ul_str}]\n"
            f"CFI = {cfi_str}{sep}TLI = {tli_str}{sep}SRMR = {srmr_str}"
        )
        latex = (
            f"\\chi^2({df}) = {chi2:.2f},\\ {p_raw},\\ \\chi^2/df = {ratio:.2f},\\\\\n"
            f"\\text{{RMSEA}} = {rmsea:.3f}\\ [90\\%\\ \\text{{CI: }}\\ {rmsea_ci[0]:.3f},\\ {rmsea_ci[1]:.3f}],\\\\\n"
            f"\\text{{CFI}} = {cfi:.3f},\\ \\text{{TLI}} = {tli:.3f},\\ \\text{{SRMR}} = {srmr:.3f}"
        )

        return {
            "test_name": "Structural Equation Modeling (SEM) / CFA Fit",
            "test_name_fa": "شاخص‌های برازش الگویابی معادلات ساختاری (SEM)",
            "raw_apa": raw_apa,
            "t_html": t_html,
            "latex": latex,
            "interpretation_fa": (
                f"شاخص‌های برازش چندگانه بر اساس معیارهای هو و بنت‌لر (1999) و کلاین (2015) در دامنه مطلوب قرار دارند "
                f"(CFI > ۰.۹۰، TLI > ۰.۹۰، RMSEA < ۰.۰۸ و نسبت χ²/df < ۳.۰) که مؤید انطباق الگوی نظری با داده‌های تجربی است."
            ),
            "viva_defense_fa": (
                "«در دفاع از مدل ساختاری، از آنجا که آماره کای‌اسکوئر (χ²) به شدت وابسته به حجم نمونه (Sample Size Sensitive) است "
                "و در نمونه‌های بیش از ۲۰۰ نفر معمولاً معنادار می‌شود، طبق توصیه کلاین (2015) و بایلن (2016)، تصمیم‌گیری نهایی "
                "بر مبنای ترکیبی از شاخص‌های برازش نسبی (CFI, TLI) و شاخص‌های مبتنی بر باقیمانده (RMSEA, SRMR) اتخاذ شده که همگی در حد برازش عالی هستند.»"
            )
        }

    # ---------------------------------------------------------
    # 3. Multiple Linear Regression Model
    # ---------------------------------------------------------
    @staticmethod
    def format_regression(
        y_name: str,
        predictors: List[Dict[str, Any]],
        r2: float,
        adj_r2: float,
        f_val: float,
        df1: int,
        df2: int,
        p_val: float,
        lang: str = "fa"
    ) -> Dict[str, str]:
        """
        Format Multiple Linear Regression:
        R² = r2, Adj. R² = adj_r2, F(df1, df2) = f_val, p = p_val
        Predictor coefficients: β = beta, t = t_val, p = p_val
        """
        r2_str = format_stat_value(r2, 2, lang, omit_leading_zero=(lang == "en"))
        adj_r2_str = format_stat_value(adj_r2, 2, lang, omit_leading_zero=(lang == "en"))
        f_str = format_stat_value(f_val, 2, lang)
        df1_str = to_persian_digits(str(df1)) if lang == "fa" else str(df1)
        df2_str = to_persian_digits(str(df2)) if lang == "fa" else str(df2)
        _, p_html = format_p_value(p_val, lang)
        p_raw, _ = format_p_value(p_val, lang)
        sep = "، " if lang == "fa" else ", "

        raw_apa = f"R² = {r2:.2f}, Adj. R² = {adj_r2:.2f}, F({df1}, {df2}) = {f_val:.2f}, {p_raw}"
        t_html = f"<i>R</i>² = {r2_str}{sep}<i>Adj. R</i>² = {adj_r2_str}{sep}<i>F</i>({df1_str}{sep}{df2_str}) = {f_str}{sep}{p_html}"

        pred_lines_html = []
        pred_lines_raw = []
        pred_terms = []
        for i, pred in enumerate(predictors, 1):
            p_name = pred.get("name", f"X{i}")
            beta = pred.get("beta", 0.0)
            t_v = pred.get("t", 0.0)
            p_v = pred.get("p", 0.001)
            b_str = format_stat_value(beta, 2, lang, omit_leading_zero=(lang == "en"))
            tv_str = format_stat_value(t_v, 2, lang)
            _, pv_html = format_p_value(p_v, lang)
            pv_raw, _ = format_p_value(p_v, lang)

            pred_lines_html.append(f"• <b>{html.escape(p_name)}:</b> β = {b_str}{sep}<i>t</i> = {tv_str}{sep}{pv_html}")
            pred_lines_raw.append(f"{p_name}: β = {b_str}, t = {tv_str}, {pv_raw}")
            sign = "+" if beta >= 0 and i > 1 else ""
            pred_terms.append(f"{sign}{beta:.2f}<i>X</i><sub>{i}</sub>")

        eq_html = f"Ŷ = β₀ + {' + '.join(pred_terms)} + ε"
        latex = (
            f"R^2 = {r2:.2f},\\ \\text{{Adj. }} R^2 = {adj_r2:.2f},\\ F({df1}, {df2}) = {f_val:.2f},\\ {p_raw}\\\\\n"
            f"\\hat{{Y}} = \\beta_0 + " + " + ".join([f"{p.get('beta', 0.0):.2f}X_{i}" for i, p in enumerate(predictors, 1)])
        )

        return {
            "test_name": "Multiple Linear Regression",
            "test_name_fa": "رگرسیون خطی چندگانه",
            "raw_apa": raw_apa + "\n" + "\n".join(pred_lines_raw),
            "t_html": t_html + "\n" + "\n".join(pred_lines_html),
            "model_equation_html": eq_html,
            "latex": latex,
            "interpretation_fa": (
                f"الگوی رگرسیون چندگانه معنادار بوده و متغیرهای پیش‌بین مجموعاً {r2_str} درصد از واریانس {y_name} را تبیین می‌کنند."
            ),
            "viva_defense_fa": (
                "«پیش از اجرای رگرسیون، تمامی مفروضه‌های اساسی از جمله نرمال بودن خطای استاندارد، عدم وجود هم‌خطی چندگانه "
                "(VIF < ۵ و Tolerance > ۰.۲) و استقلال خطاها (آزمون دوربین-واتسون بین ۱.۵ تا ۲.۵) به دقت وارسی و تأیید گردیده‌اند.»"
            )
        }

    # ---------------------------------------------------------
    # 4. G*Power Sample Size Determination
    # ---------------------------------------------------------
    @staticmethod
    def format_gpower(
        test_type: str = "ancova",
        n_total: int = 64,
        alpha: float = 0.05,
        power: float = 0.85,
        effect_size: float = 0.25,
        effect_size_type: str = "f",
        num_groups: int = 2,
        num_covariates: int = 1,
        lang: str = "fa"
    ) -> Dict[str, str]:
        """
        Format G*Power 3.1.9.7 parameter derivation & sample size calculation.
        """
        n_str = to_persian_digits(str(n_total)) if lang == "fa" else str(n_total)
        alpha_str = format_stat_value(alpha, 2, lang, omit_leading_zero=(lang == "en"))
        power_str = format_stat_value(power, 2, lang, omit_leading_zero=(lang == "en"))
        es_str = format_stat_value(effect_size, 2, lang, omit_leading_zero=(lang == "en"))
        sep = "، " if lang == "fa" else ", "

        raw_apa = f"N = {n_total} (G*Power 3.1: Effect size {effect_size_type} = {effect_size:.2f}, α = {alpha:.2f}, Power (1-β) = {power:.2f})"
        t_html = (
            f"👥 <b>حجم نمونه بهینه:</b> <i>N</i> = <b>{n_str}</b>\n"
            f"⚙️ <b>پارامترهای جی‌پاور:</b> اندازه اثر <i>{effect_size_type}</i> = {es_str}{sep}α = {alpha_str}{sep}توان آزمون (1 - β) = {power_str}\n"
            f"📐 <b>پارامتر غیرمرکزی:</b> λ = <i>f</i>² × <i>N</i> = {format_stat_value((effect_size**2)*n_total, 2, lang)}"
        )
        latex = (
            f"N = {n_total},\\ \\alpha = {alpha:.2f},\\ 1-\\beta = {power:.2f},\\ "
            f"\\text{{Effect Size }} {effect_size_type} = {effect_size:.2f},\\ \\lambda = f^2 \\times N"
        )

        return {
            "test_name": "G*Power 3.1 Statistical Power Analysis",
            "test_name_fa": "محاسبه توان آماری و تعیین حجم نمونه با G*Power",
            "raw_apa": raw_apa,
            "t_html": t_html,
            "latex": latex,
            "interpretation_fa": (
                f"حجم نمونه بهینه با نرم‌افزار G*Power بر مبنای توان آماری {power_str} و سطح خطای {alpha_str} تعیین گردید تا خطر خطای نوع دوم (Type II Error) به حداقل برسد."
            ),
            "viva_defense_fa": (
                "«تعیین حجم نمونه بر اساس قاعده سرانگشتی نبوده، بلکه طبق روش‌شناسی فاول و همکاران (Faul et al., 2007, 2009) "
                "و نرم‌افزار G*Power 3.1 محاسبه شد. با در نظر گرفتن اندازه اثر متوسط کوهن (f = ۰.۲۵)، توان آزمون بالای ۰.۸۵ و "
                "احتمال ریزش آزمودنی‌ها، حجم نمونه انتخاب‌شده کفایت آماری مطلق جهت آزمون فرضیه‌ها را داراست.»"
            )
        }

    # ---------------------------------------------------------
    # 5. Independent & Paired t-Tests
    # ---------------------------------------------------------
    @staticmethod
    def format_ttest(
        t_val: float,
        df: int,
        p_val: float,
        cohen_d: float,
        ci: Tuple[float, float] = (0.24, 0.98),
        test_type: str = "independent",
        lang: str = "fa"
    ) -> Dict[str, str]:
        """
        Format Independent or Paired t-Test:
        t(df) = t_val, p = p_val, d = cohen_d, 95% CI [ci[0], ci[1]]
        """
        t_str = format_stat_value(t_val, 2, lang)
        df_str = to_persian_digits(str(df)) if lang == "fa" else str(df)
        d_str = format_stat_value(cohen_d, 2, lang)
        ci_ll_str = format_stat_value(ci[0], 2, lang)
        ci_ul_str = format_stat_value(ci[1], 2, lang)
        _, p_html = format_p_value(p_val, lang)
        p_raw, _ = format_p_value(p_val, lang)
        sep = "، " if lang == "fa" else ", "

        raw_apa = f"t({df}) = {t_val:.2f}, {p_raw}, d = {cohen_d:.2f}, 95% CI [{ci[0]:.2f}, {ci[1]:.2f}]"
        t_html = f"<i>t</i>({df_str}) = {t_str}{sep}{p_html}{sep}<i>d</i> = {d_str}{sep}95% CI [{ci_ll_str}{sep}{ci_ul_str}]"
        latex = f"t({df}) = {t_val:.2f},\\ {p_raw},\\ d = {cohen_d:.2f},\\ 95\\%\\ \\text{{CI}} [{ci[0]:.2f},\\ {ci[1]:.2f}]"

        t_type_fa = "تی مستقل" if test_type == "independent" else "تی وابسته (زوجی)"
        return {
            "test_name": f"Student's t-Test ({test_type.title()})",
            "test_name_fa": f"آزمون t استیودنت ({t_type_fa})",
            "raw_apa": raw_apa,
            "t_html": t_html,
            "latex": latex,
            "interpretation_fa": (
                f"تفاوت میانگین دو گروه معنادار بوده و اندازه اثر کوهن (d = {d_str}) حاکی از تفاوت عملی نیرومند است."
            ),
            "viva_defense_fa": (
                "«پیش‌شرط‌های آزمون t از جمله برابری واریانس‌ها با آزمون لوین (Levene's Test) و توزیع نرمال با آزمون شاپیرو-ویلک "
                "وارسی شده و گزارش هم‌زمان فاصله اطمینان ۹۵ درصد و اندازه اثر کوهن، شفافیت و کفایت روش‌شناختی گزارش را تضمین می‌کند.»"
            )
        }

    # ---------------------------------------------------------
    # 6. Mediation Model (Hayes PROCESS Bootstrap)
    # ---------------------------------------------------------
    @staticmethod
    def format_mediation(
        indirect_effect: float,
        boot_se: float,
        bca_ci: Tuple[float, float],
        predictor: str = "X",
        mediator: str = "M",
        outcome: str = "Y",
        resamples: int = 5000,
        lang: str = "fa"
    ) -> Dict[str, str]:
        """
        Format Hayes PROCESS Macro Bootstrap Mediation Model:
        Indirect effect: ab = val, BootSE = val, 95% BCa CI [LL, UL]
        """
        ab_str = format_stat_value(indirect_effect, 3, lang)
        se_str = format_stat_value(boot_se, 3, lang)
        ci_ll_str = format_stat_value(bca_ci[0], 3, lang)
        ci_ul_str = format_stat_value(bca_ci[1], 3, lang)
        res_str = to_persian_digits(str(resamples)) if lang == "fa" else str(resamples)
        sep = "، " if lang == "fa" else ", "

        raw_apa = f"Indirect Effect (ab) = {indirect_effect:.3f}, BootSE = {boot_se:.3f}, 95% BCa CI [{bca_ci[0]:.3f}, {bca_ci[1]:.3f}]"
        t_html = (
            f"🔗 <b>اثر نامستقیم (<i>ab</i>):</b> {ab_str}\n"
            f"📊 <b>خطای معیار بوت‌استرپ:</b> BootSE = {se_str}\n"
            f"🎯 <b>فاصله اطمینان بوت‌استرپ ({res_str} نمونه):</b> 95% BCa CI [{ci_ll_str}{sep}{ci_ul_str}]"
        )
        latex = f"\\text{{Indirect Effect }} (ab) = {indirect_effect:.3f},\\ \\text{{BootSE}} = {boot_se:.3f},\\ 95\\%\\ \\text{{BCa CI}} [{bca_ci[0]:.3f},\\ {bca_ci[1]:.3f}]"

        is_significant = (bca_ci[0] > 0 and bca_ci[1] > 0) or (bca_ci[0] < 0 and bca_ci[1] < 0)
        sig_text = "معنادار است (عدم شمول صفر)" if is_significant else "معنادار نیست (شامل صفر)"

        return {
            "test_name": "Hayes PROCESS Bootstrap Mediation Analysis",
            "test_name_fa": "تحلیل میانجی‌گری بوت‌استرپ هیز (PROCESS)",
            "raw_apa": raw_apa,
            "t_html": t_html,
            "latex": latex,
            "interpretation_fa": (
                f"اثر نامستقیم متغیر {predictor} بر {outcome} از طریق متغیر میانجی {mediator} {sig_text}، "
                f"زیرا فاصله اطمینان ۹۵ درصدی تصحیح‌شده تورش و شتاب‌یافته (BCa CI) عدد صفر را در بر نمی‌گیرد."
            ),
            "viva_defense_fa": (
                "«طبق متدولوژی جدید هیز (Hayes, 2022) و پریکر و هیز (2008)، استفاده از آزمون قدیمی سوبل (Sobel Test) به دلیل "
                "فرض غیرواقع‌بینانه توزیع نرمال برای حاصل‌ضرب ضرایب (ab) منسوخ است؛ لذا آزمون بازنمونه‌گیری بوت‌استرپ ناپارامتریک "
                "با ۵۰۰۰ نمونه‌گیری مجدد و فاصله اطمینان BCa پیاده‌سازی شده که بالاترین توان آماری را فراهم می‌آورد.»"
            )
        }

    # ---------------------------------------------------------
    # 7. Complete Viva Voce Defense Card Builder
    # ---------------------------------------------------------
    @classmethod
    def build_defense_card(
        cls,
        formula_dict: Dict[str, str],
        supervisor_dilemma_fa: str,
        client_name: str = "پژوهشگر",
        card_id: str = "M1"
    ) -> Tuple[str, List[List[Dict[str, str]]]]:
        """
        Builds a 2026 Box-drawing Viva Voce Defense Card with:
        - Boxed Native Math Formula (Telegram HTML)
        - Monospaced LaTeX block
        - Theoretical explanation & literature citations
        - Ready-to-speak viva voce defense script
        - 2026 Action Buttons for 1-click copying APA / LaTeX
        """
        test_title = formula_dict.get("test_name_fa", "دفاعیه آماری و ریاضی")
        raw_apa = formula_dict.get("raw_apa", "")
        t_html = formula_dict.get("t_html", "")
        latex_code = formula_dict.get("latex", "")
        interp_fa = formula_dict.get("interpretation_fa", "")
        defense_fa = formula_dict.get("viva_defense_fa", "")

        header_lines = [
            "╭─ <b>🎓 VIVA VOCE MATHEMATICAL DEFENSE CARD</b> ───────",
            f"│ 🔬 <b>روش/آزمون:</b> <code>{html.escape(test_title)}</code>",
            f"│ 👤 <b>مخاطب:</b> <code>{html.escape(client_name)}</code>",
            f"│ 🆔 <b>شناسه فرمول:</b> <code>{card_id}</code>",
            "╰──────────────────────────────────────────────────"
        ]

        body = [
            "\n".join(header_lines),
            f"\n❓ <b>چالش یا پرسش احتمالی استاد راهنما / داور:</b>\n"
            f"<blockquote expandable>«{html.escape(supervisor_dilemma_fa)}»</blockquote>",
            f"\n📐 <b>فرمول و نتایج استاندارد APA 7th (رندر بومی تلگرام):</b>\n"
            f"<blockquote>{t_html}</blockquote>",
            f"\n📜 <b>کد خام لاتک (LaTeX Block جهت مقالات بین‌المللی):</b>\n"
            f'<pre><code class="language-latex">{html.escape(latex_code)}</code></pre>',
            f"\n💡 <b>تفسیر روش‌شناختی و شواهد اپیستمیک:</b>\n"
            f"<blockquote expandable>{html.escape(interp_fa)}</blockquote>",
            f"\n🎙️ <b>متن دفاع شفاهی دانشجو در جلسه شورا / پیش‌دفاع:</b>\n"
            f"<blockquote expandable>{html.escape(defense_fa)}</blockquote>",
            f"\n<i>کلیدهای اقدام سریع جهت دریافت متن خام APA یا کد LaTeX:</i>"
        ]

        alert_text = "\n".join(body)

        buttons = [
            [
                {"text": "📋 Copy APA 7 Text", "callback_data": f"math_apa_{card_id}"},
                {"text": "📐 Copy LaTeX Code", "callback_data": f"math_latex_{card_id}"}
            ],
            [
                {"text": "🎙️ Oral Defense Script", "callback_data": f"math_speech_{card_id}"}
            ]
        ]

        return alert_text, buttons
