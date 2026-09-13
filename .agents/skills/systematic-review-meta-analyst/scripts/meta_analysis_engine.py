#!/usr/bin/env python3
"""
meta_analysis_engine.py - PRISMA 2020 & Cochrane Quantitative Meta-Analysis Engine

Performs:
  1. Deterministic effect size calculation (Cohen's d, Hedges' g, SE, 95% CI).
  2. Fixed-effect and DerSimonian-Laird Random-effects pooling.
  3. Heterogeneity quantification (Cochran's Q, Higgins' I², Tau², Tau).
  4. Publication bias evaluation (Egger's linear regression test).
  5. Publication-grade Forest Plot & Funnel Plot generation (PNG, 300 DPI).
  6. Comprehensive APA 7 Systematic Review & Meta-Analysis Word Report (.docx).

Supports both English and Persian (BiDi RTL, B Nazanin/B Titr) reporting.
"""

import os
import sys
import json
import math
import argparse
from datetime import datetime
import numpy as np
import scipy.stats as stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

# ==============================================================================
# 1. MATHEMATICAL META-ANALYSIS CORE
# ==============================================================================
def calculate_study_effect(study):
    """
    Computes Cohen's d, Hedges' g (with small sample correction J),
    variance v_g, standard error, and 95% CI.
    Convention: Higher effect size means greater therapeutic benefit (favors intervention).
    """
    n1 = float(study["n_intervention"])
    m1 = float(study["mean_intervention"])
    s1 = float(study["sd_intervention"])
    
    n2 = float(study["n_control"])
    m2 = float(study["mean_control"])
    s2 = float(study["sd_control"])
    
    # Degrees of freedom
    df = n1 + n2 - 2.0
    
    # Pooled standard deviation
    s_pooled = math.sqrt(((n1 - 1.0) * (s1 ** 2) + (n2 - 1.0) * (s2 ** 2)) / df)
    
    # Cohen's d (Control - Intervention so positive d favors treatment symptom reduction)
    d = (m2 - m1) / s_pooled if s_pooled > 0 else 0.0
    
    # Small-sample bias correction factor J
    j = 1.0 - (3.0 / (4.0 * df - 1.0))
    
    # Hedges' g
    g = d * j
    
    # Variance of g
    v_g = ((n1 + n2) / (n1 * n2) + (d ** 2) / (2.0 * (n1 + n2))) * (j ** 2)
    se_g = math.sqrt(v_g)
    
    # 95% Confidence Interval
    ci_lower = g - 1.96 * se_g
    ci_upper = g + 1.96 * se_g
    
    # Fixed effect weight (inverse variance)
    w_fixed = 1.0 / v_g if v_g > 0 else 0.0
    
    return {
        "id": study.get("id"),
        "authors_year": study.get("authors_year"),
        "n_intervention": n1,
        "n_control": n2,
        "n_total": n1 + n2,
        "s_pooled": s_pooled,
        "cohens_d": d,
        "j_correction": j,
        "hedges_g": g,
        "variance": v_g,
        "se": se_g,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "w_fixed": w_fixed,
        "intervention_label": study.get("intervention_label", ""),
        "control_label": study.get("control_label", ""),
        "outcome_scale": study.get("outcome_scale", ""),
        "country": study.get("country", ""),
        "rob2": study.get("rob2", {})
    }

def run_meta_analysis(studies_data):
    """
    Executes Fixed-Effect and Random-Effects (DerSimonian-Laird) pooling,
    heterogeneity testing (Q, I^2, Tau^2), and Egger's regression test.
    """
    k = len(studies_data)
    if k < 2:
        raise ValueError("At least 2 studies are required for meta-analysis.")
        
    study_effects = [calculate_study_effect(s) for s in studies_data]
    
    # -------------------------------------------------------------
    # Fixed-Effect Model (Inverse Variance)
    # -------------------------------------------------------------
    sum_w_fixed = sum(s["w_fixed"] for s in study_effects)
    sum_wg_fixed = sum(s["w_fixed"] * s["hedges_g"] for s in study_effects)
    pooled_g_fixed = sum_wg_fixed / sum_w_fixed
    se_fixed = math.sqrt(1.0 / sum_w_fixed)
    ci_lower_fixed = pooled_g_fixed - 1.96 * se_fixed
    ci_upper_fixed = pooled_g_fixed + 1.96 * se_fixed
    z_fixed = pooled_g_fixed / se_fixed if se_fixed > 0 else 0.0
    p_fixed = 2.0 * (1.0 - stats.norm.cdf(abs(z_fixed)))
    
    # -------------------------------------------------------------
    # Heterogeneity Statistics (Cochran's Q, I^2, Tau^2)
    # -------------------------------------------------------------
    q = sum(s["w_fixed"] * ((s["hedges_g"] - pooled_g_fixed) ** 2) for s in study_effects)
    df_q = k - 1
    p_q = 1.0 - stats.chi2.cdf(q, df_q)
    
    sum_w_sq = sum(s["w_fixed"] ** 2 for s in study_effects)
    c_denom = sum_w_fixed - (sum_w_sq / sum_w_fixed)
    tau_sq = max(0.0, (q - df_q) / c_denom) if c_denom > 0 else 0.0
    tau = math.sqrt(tau_sq)
    i_sq = max(0.0, ((q - df_q) / q) * 100.0) if q > 0 else 0.0
    
    # -------------------------------------------------------------
    # Random-Effects Model (DerSimonian-Laird)
    # -------------------------------------------------------------
    for s in study_effects:
        v_rand = s["variance"] + tau_sq
        s["w_random"] = 1.0 / v_rand if v_rand > 0 else 0.0
        
    sum_w_rand = sum(s["w_random"] for s in study_effects)
    sum_wg_rand = sum(s["w_random"] * s["hedges_g"] for s in study_effects)
    pooled_g_rand = sum_wg_rand / sum_w_rand
    se_rand = math.sqrt(1.0 / sum_w_rand)
    ci_lower_rand = pooled_g_rand - 1.96 * se_rand
    ci_upper_rand = pooled_g_rand + 1.96 * se_rand
    z_rand = pooled_g_rand / se_rand if se_rand > 0 else 0.0
    p_rand = 2.0 * (1.0 - stats.norm.cdf(abs(z_rand)))
    
    # Relative weights (%)
    for s in study_effects:
        s["weight_pct_fixed"] = (s["w_fixed"] / sum_w_fixed) * 100.0
        s["weight_pct_random"] = (s["w_random"] / sum_w_rand) * 100.0
        
    # -------------------------------------------------------------
    # Publication Bias (Egger's Linear Regression Test)
    # SND_i = g_i / SE_i on Precision_i = 1 / SE_i
    # -------------------------------------------------------------
    x_prec = np.array([1.0 / s["se"] for s in study_effects])
    y_snd = np.array([s["hedges_g"] / s["se"] for s in study_effects])
    
    # Ordinary Least Squares regression
    n_pts = len(x_prec)
    mean_x = np.mean(x_prec)
    mean_y = np.mean(y_snd)
    ss_xx = np.sum((x_prec - mean_x) ** 2)
    ss_xy = np.sum((x_prec - mean_x) * (y_snd - mean_y))
    slope = ss_xy / ss_xx if ss_xx > 0 else 0.0
    intercept = mean_y - slope * mean_x
    
    residuals = y_snd - (intercept + slope * x_prec)
    s_err = np.sqrt(np.sum(residuals ** 2) / (n_pts - 2)) if n_pts > 2 else 0.0
    se_intercept = s_err * np.sqrt(1.0 / n_pts + (mean_x ** 2) / ss_xx) if ss_xx > 0 and n_pts > 2 else 0.0
    t_stat = intercept / se_intercept if se_intercept > 0 else 0.0
    egger_p = 2.0 * (1.0 - stats.t.cdf(abs(t_stat), df=n_pts - 2)) if n_pts > 2 else 1.0
    
    return {
        "k": k,
        "studies": study_effects,
        "fixed_effect": {
            "pooled_g": pooled_g_fixed,
            "se": se_fixed,
            "ci_lower": ci_lower_fixed,
            "ci_upper": ci_upper_fixed,
            "z": z_fixed,
            "p": p_fixed
        },
        "random_effects": {
            "pooled_g": pooled_g_rand,
            "se": se_rand,
            "ci_lower": ci_lower_rand,
            "ci_upper": ci_upper_rand,
            "z": z_rand,
            "p": p_rand
        },
        "heterogeneity": {
            "q": q,
            "df": df_q,
            "p_value": p_q,
            "i_squared": i_sq,
            "tau_squared": tau_sq,
            "tau": tau
        },
        "publication_bias": {
            "egger_intercept": float(intercept),
            "egger_slope": float(slope),
            "egger_se_intercept": float(se_intercept),
            "egger_t": float(t_stat),
            "egger_p": float(egger_p),
            "has_bias": bool(egger_p < 0.05)
        }
    }

# ==============================================================================
# 2. HIGH-RESOLUTION VISUALIZATION ENGINE (FOREST & FUNNEL PLOTS)
# ==============================================================================
def plot_forest(meta_res, out_path, title="Forest Plot of Treatment Efficacy (Hedges' g)"):
    """
    Generates a publication-grade Forest Plot with study-level CIs,
    marker sizes proportional to random-effects weight, and pooled diamond.
    """
    studies = meta_res["studies"]
    k = len(studies)
    rand = meta_res["random_effects"]
    het = meta_res["heterogeneity"]
    
    plt.figure(figsize=(11, max(6.5, k * 0.48 + 3.0)), dpi=300)
    ax = plt.gca()
    
    # Reverse study order so top study appears at top
    reversed_studies = list(reversed(studies))
    y_positions = np.arange(k)
    
    # Plot individual studies
    for i, s in enumerate(reversed_studies):
        y = y_positions[i]
        g = s["hedges_g"]
        ci_l = s["ci_lower"]
        ci_u = s["ci_upper"]
        wt = s["weight_pct_random"]
        
        # Horizontal error bar for 95% CI
        ax.plot([ci_l, ci_u], [y, y], color="#1f4e78", lw=1.5, zorder=2)
        # Point estimate square sized by weight
        msize = 4.0 + (wt / 100.0) * 20.0
        ax.plot(g, y, marker="s", markersize=msize, color="#1f4e78", zorder=3)
        
    # Vertical line of no effect
    ax.axvline(0, color="gray", linestyle="-", lw=1.0, alpha=0.7, zorder=1)
    
    # Vertical dashed line at pooled random effect
    ax.axvline(rand["pooled_g"], color="#c00000", linestyle="--", lw=1.2, alpha=0.8, zorder=1)
    
    # Pooled summary diamond at y = -1.2
    y_diamond = -1.2
    diamond_h = 0.35
    poly_pts = [
        (rand["ci_lower"], y_diamond),
        (rand["pooled_g"], y_diamond + diamond_h),
        (rand["ci_upper"], y_diamond),
        (rand["pooled_g"], y_diamond - diamond_h)
    ]
    diamond = patches.Polygon(poly_pts, closed=True, facecolor="#c00000", edgecolor="#800000", lw=1.2, zorder=4)
    ax.add_patch(diamond)
    
    # Set y limits and ticks
    ax.set_ylim(-2.2, k + 0.8)
    study_labels = [f"{s['authors_year']} (N={int(s['n_total'])})" for s in reversed_studies]
    study_labels.insert(0, "Random Effects Model (Pooled)")
    
    all_y = [-1.2] + list(y_positions)
    ax.set_yticks(all_y)
    ax.set_yticklabels(study_labels, fontsize=10, fontweight="bold")
    
    # Set x limits with margin
    min_x = min(min(s["ci_lower"] for s in studies), rand["ci_lower"]) - 0.4
    max_x = max(max(s["ci_upper"] for s in studies), rand["ci_upper"]) + 0.4
    ax.set_xlim(min_x, max_x)
    
    # Annotate values and weights on the right
    text_x = max_x - 0.05
    for i, s in enumerate(reversed_studies):
        y = y_positions[i]
        txt = f"{s['hedges_g']:.2f} [{s['ci_lower']:.2f}, {s['ci_upper']:.2f}]  ({s['weight_pct_random']:.1f}%)"
        ax.text(text_x, y, txt, va="center", ha="right", fontsize=9, fontfamily="monospace")
        
    # Diamond text
    dia_txt = f"{rand['pooled_g']:.2f} [{rand['ci_lower']:.2f}, {rand['ci_upper']:.2f}]  (100.0%)"
    ax.text(text_x, y_diamond, dia_txt, va="center", ha="right", fontsize=9.5, fontweight="bold", fontfamily="monospace", color="#800000")
    
    # Header column labels
    ax.text(min_x + 0.05, k + 0.3, "Study (Sample)", fontweight="bold", fontsize=10, va="bottom", ha="left")
    ax.text(text_x, k + 0.3, "Hedges' g [95% CI]  Weight", fontweight="bold", fontsize=10, va="bottom", ha="right")
    
    # Direction labels
    ax.text(-0.05, -2.0, "◄ Favors Control", ha="right", va="center", fontsize=9, style="italic", color="#555555")
    ax.text(0.05, -2.0, "Favors Intervention ►", ha="left", va="center", fontsize=9, style="italic", color="#555555")
    
    # Heterogeneity note at bottom
    het_text = (
        f"Heterogeneity: Q = {het['q']:.2f} (df = {het['df']}, p = {het['p_value']:.3f}), "
        f"I² = {het['i_squared']:.1f}%, τ² = {het['tau_squared']:.3f}\n"
        f"Overall Test: Z = {rand['z']:.2f} (p < .001)" if rand['p'] < 0.001 else f"Overall Test: Z = {rand['z']:.2f} (p = {rand['p']:.3f})"
    )
    ax.text(min_x + 0.05, -1.8, het_text, fontsize=8.5, va="top", ha="left", bbox=dict(boxstyle="round,pad=0.4", facecolor="#f8f9fa", edgecolor="#dcdcdc"))
    
    ax.set_xlabel("Effect Size: Hedges' g (Standardized Mean Difference)", fontsize=10, fontweight="bold")
    ax.set_title(title, fontsize=12, fontweight="bold", pad=20)
    
    # Clean spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    return out_path

def plot_funnel(meta_res, out_path, title="Funnel Plot of Publication Bias (Pseudo 95% CI)"):
    """
    Generates a high-resolution Funnel Plot with inverted SE on the y-axis,
    pseudo 95% confidence bounds, and Egger's regression inset.
    """
    studies = meta_res["studies"]
    rand = meta_res["random_effects"]
    bias = meta_res["publication_bias"]
    
    g_vals = [s["hedges_g"] for s in studies]
    se_vals = [s["se"] for s in studies]
    
    plt.figure(figsize=(8, 6), dpi=300)
    ax = plt.gca()
    
    pooled_g = rand["pooled_g"]
    max_se = max(se_vals) * 1.25
    
    # Shaded pseudo 95% confidence triangle
    se_grid = np.linspace(0, max_se, 200)
    ci_left = pooled_g - 1.96 * se_grid
    ci_right = pooled_g + 1.96 * se_grid
    
    ax.fill_betweenx(se_grid, ci_left, ci_right, color="#e9ecef", alpha=0.5, label="Pseudo 95% CI Region")
    ax.plot(ci_left, se_grid, color="#adb5bd", linestyle="--", lw=1.0)
    ax.plot(ci_right, se_grid, color="#adb5bd", linestyle="--", lw=1.0)
    
    # Centerline at pooled effect
    ax.axvline(pooled_g, color="#c00000", linestyle="-", lw=1.2, label=f"Pooled Effect (g = {pooled_g:.2f})")
    
    # Scatter of individual studies
    ax.scatter(g_vals, se_vals, color="#1f4e78", s=60, edgecolors="black", lw=0.8, zorder=3, label="Included Studies (k = %d)" % len(studies))
    
    # Invert y-axis: 0 (highest precision) at top, large SE at bottom
    ax.set_ylim(max_se, 0)
    ax.set_ylabel("Standard Error (SE)", fontsize=10, fontweight="bold")
    ax.set_xlabel("Effect Size: Hedges' g", fontsize=10, fontweight="bold")
    ax.set_title(title, fontsize=12, fontweight="bold", pad=14)
    
    # Egger's test results inset box
    bias_verdict = "Significant Asymmetry (Publication Bias Detected)" if bias["has_bias"] else "Symmetric Distribution (No Major Publication Bias)"
    box_txt = (
        f"Egger's Linear Regression Test:\n"
        f"Intercept = {bias['egger_intercept']:.2f} (SE = {bias['egger_se_intercept']:.2f})\n"
        f"t = {bias['egger_t']:.2f}, p = {bias['egger_p']:.3f}\n"
        f"Status: {bias_verdict}"
    )
    ax.text(0.04, 0.06, box_txt, transform=ax.transAxes, fontsize=8.5, va="bottom", ha="left",
            bbox=dict(boxstyle="round,pad=0.5", facecolor="#ffffff", edgecolor="#ced4da", alpha=0.9))
            
    ax.legend(loc="upper right", fontsize=8.5, framealpha=0.9)
    ax.grid(True, linestyle=":", alpha=0.5)
    
    plt.tight_layout()
    plt.savefig(out_path, dpi=300)
    plt.close()
    return out_path

# ==============================================================================
# 3. OPENXML APA 7 DOCUMENT COMPILER
# ==============================================================================
def set_cell_margins(cell, top=100, bottom=100, left=120, right=120):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m_name, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m_name}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_apa_table_borders(table, is_rtl=False):
    tblPr = table._tbl.tblPr
    if is_rtl:
        bidiVisual = parse_xml(f'<w:bidiVisual {nsdecls("w")}/>')
        tblPr.append(bidiVisual)
    tblBorders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>\n'
        f'  <w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>\n'
        f'  <w:left w:val="none"/>\n'
        f'  <w:right w:val="none"/>\n'
        f'  <w:insideH w:val="none"/>\n'
        f'  <w:insideV w:val="none"/>\n'
        f'</w:tblBorders>'
    )
    tblPr.append(tblBorders)

def add_header_underline(cell):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>\n'
        f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)

def add_row_bottom_border(cell, color="E0E0E0"):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>\n'
        f'  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="{color}"/>\n'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)

def set_paragraph_bidi(p, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    p.alignment = align
    pPr = p._p.get_or_add_pPr()
    if not any(child.tag.endswith('}bidi') for child in pPr):
        bidi = OxmlElement('w:bidi')
        bidi.set(qn('w:val'), '1')
        pPr.insert(0, bidi)

def add_run(p, text, lang='en', size=11, bold=False, italic=False, color=None):
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = color
        
    font_fa = 'B Titr' if (bold and size >= 13) else 'B Nazanin'
    font_en = 'Times New Roman'
    
    if lang == 'fa':
        run.font.name = font_fa
        rPr = run._r.get_or_add_rPr()
        rFonts = parse_xml(
            f'<w:rFonts {nsdecls("w")} '
            f'w:ascii="{font_fa}" w:hAnsi="{font_fa}" '
            f'w:cs="{font_fa}" w:eastAsia="{font_fa}" w:hint="cs"/>'
        )
        rPr.append(rFonts)
        rPr.append(parse_xml(f'<w:rtl {nsdecls("w")} w:val="1"/>'))
        sz_half_pts = int(size * 2)
        rPr.append(parse_xml(f'<w:szCs {nsdecls("w")} w:val="{sz_half_pts}"/>'))
        if bold:
            rPr.append(parse_xml(f'<w:bCs {nsdecls("w")} w:val="1"/>'))
    else:
        run.font.name = font_en
    return run

def compile_meta_analysis_report(payload, meta_res, forest_img_path, funnel_img_path, out_docx_path, lang='en'):
    doc = docx.Document()
    is_fa = (lang == 'fa')
    
    # 1-inch margins
    for sec in doc.sections:
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin = Inches(1.0)
        sec.right_margin = Inches(1.0)
        
    meta = payload.get("meta_analysis_metadata", {})
    prisma = payload.get("prisma_flow", {})
    pico = meta.get("pico", {})
    studies = meta_res["studies"]
    rand = meta_res["random_effects"]
    fixed = meta_res["fixed_effect"]
    het = meta_res["heterogeneity"]
    bias = meta_res["publication_bias"]
    
    title = meta.get("title", "Systematic Review and Meta-Analysis")
    outcome = meta.get("primary_outcome", "Clinical Outcome")
    
    # Document Header
    p_title = doc.add_paragraph()
    if is_fa:
        set_paragraph_bidi(p_title, WD_ALIGN_PARAGRAPH.CENTER)
        add_run(p_title, "گزارش جامع مرور سیستماتیک و فراتحلیل (PRISMA 2020)\n", lang='fa', size=16, bold=True)
        add_run(p_title, title, lang='fa', size=14, bold=True)
    else:
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_run(p_title, "Systematic Review & Quantitative Meta-Analysis Report\n", lang='en', size=16, bold=True)
        add_run(p_title, f'"{title}"', lang='en', size=13, italic=True)
    p_title.paragraph_format.space_after = Pt(14)
    
    # PICOS Box
    p_pico_h = doc.add_paragraph()
    if is_fa:
        set_paragraph_bidi(p_pico_h, WD_ALIGN_PARAGRAPH.RIGHT)
        add_run(p_pico_h, "۱. چارچوب مفهومی پژوهش (معیارهای PICOS):", lang='fa', size=12, bold=True)
    else:
        add_run(p_pico_h, "1. Evidence Synthesis Protocol (PICOS Framework)", lang='en', size=12, bold=True)
    p_pico_h.paragraph_format.space_after = Pt(4)
    
    pico_items = [
        ("جامعه هدف (Population)" if is_fa else "Population (P)", pico.get("population", "N/A")),
        ("مداخله (Intervention)" if is_fa else "Intervention (I)", pico.get("intervention", "N/A")),
        ("گروه مقایسه (Comparator)" if is_fa else "Comparator (C)", pico.get("comparator", "N/A")),
        ("پیامد اولیه (Outcomes)" if is_fa else "Outcomes (O)", pico.get("outcomes", outcome)),
        ("طرح پژوهش (Study Design)" if is_fa else "Study Design (S)", pico.get("study_design", "Randomized Controlled Trials (RCTs)"))
    ]
    for lbl, val in pico_items:
        p = doc.add_paragraph()
        if is_fa:
            set_paragraph_bidi(p, WD_ALIGN_PARAGRAPH.JUSTIFY)
            add_run(p, f"• {lbl}: ", lang='fa', size=10, bold=True)
            add_run(p, val, lang='fa', size=10)
        else:
            p.paragraph_format.left_indent = Inches(0.2)
            add_run(p, f"• {lbl}: ", lang='en', size=10, bold=True)
            add_run(p, val, lang='en', size=10)
        p.paragraph_format.space_after = Pt(2)
        
    doc.add_paragraph().paragraph_format.space_after = Pt(8)
    
    # -------------------------------------------------------------
    # 2. PRISMA 2020 Flow Numbers Table
    # -------------------------------------------------------------
    p_pr_h = doc.add_paragraph()
    if is_fa:
        set_paragraph_bidi(p_pr_h, WD_ALIGN_PARAGRAPH.RIGHT)
        add_run(p_pr_h, "۲. نتایج مراحل غربالگری بر اساس دیاگرام جریان PRISMA 2020:", lang='fa', size=12, bold=True)
    else:
        add_run(p_pr_h, "2. Study Selection Flow & Attrition (PRISMA 2020 Statement)", lang='en', size=12, bold=True)
    p_pr_h.paragraph_format.space_after = Pt(4)
    
    tbl_prisma = doc.add_table(rows=1, cols=3)
    tbl_prisma.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_apa_table_borders(tbl_prisma, is_rtl=is_fa)
    
    pr_headers = ["مرحله PRISMA 2020", "شرح و پایگاه‌های اطلاعاتی", "تعداد اسناد"] if is_fa else ["PRISMA Phase", "Operational Description & Database Sources", "Records (n)"]
    for idx, h in enumerate(pr_headers):
        c = tbl_prisma.rows[0].cells[idx]
        set_cell_background(c, "F2F2F2")
        add_header_underline(c)
        set_cell_margins(c, top=100, bottom=100)
        p = c.paragraphs[0]
        if is_fa:
            set_paragraph_bidi(p, WD_ALIGN_PARAGRAPH.CENTER)
            add_run(p, h, lang='fa', size=10, bold=True)
        else:
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            add_run(p, h, lang='en', size=10, bold=True)
            
    ident = prisma.get("identification", {})
    screen = prisma.get("screening", {})
    elig = prisma.get("eligibility", {})
    inc = prisma.get("inclusion", {})
    
    db_breakdown = ", ".join(f"{k}: {v}" for k, v in ident.get("database_counts", {}).items())
    pr_rows = [
        ("۱. شناسایی (Identification)" if is_fa else "Identification", f"Total records identified from databases ({db_breakdown})", str(ident.get("total_identified", 0))),
        ("حذف موارد تکراری" if is_fa else "Deduplication", "Duplicate records removed before screening", str(ident.get("duplicates_removed", 0))),
        ("۲. غربالگری (Screening)" if is_fa else "Screening", "Records screened based on title and abstract", str(screen.get("records_screened", 0))),
        ("موارد کنارگذاشته شده" if is_fa else "Screening Exclusion", "Irrelevant records excluded based on title/abstract", str(screen.get("records_excluded", 0))),
        ("۳. ارزیابی جامع (Eligibility)" if is_fa else "Eligibility", "Full-text reports retrieved and assessed for eligibility", str(elig.get("reports_assessed", 0))),
        ("مقالات حذف شده با دلیل" if is_fa else "Eligibility Exclusion", f"Excluded with reasons: {', '.join(f'{k} (n={v})' for k, v in elig.get('exclusion_reasons', {}).items())}", str(elig.get("reports_excluded", 0))),
        ("۴. گنجانده‌شده نهایی (Included)" if is_fa else "Included Studies", "Eligible RCTs included in qualitative synthesis and quantitative meta-analysis", str(inc.get("quantitative_meta_analysis_count", len(studies))))
    ]
    for phase_txt, desc_txt, count_txt in pr_rows:
        row_c = tbl_prisma.add_row().cells
        for idx, cell in enumerate(row_c):
            set_cell_margins(cell, top=80, bottom=80)
            add_row_bottom_border(cell)
        
        row_c[0].paragraphs[0].text = ""
        row_c[1].paragraphs[0].text = ""
        row_c[2].paragraphs[0].text = ""
        
        if is_fa:
            set_paragraph_bidi(row_c[0].paragraphs[0], WD_ALIGN_PARAGRAPH.RIGHT)
            add_run(row_c[0].paragraphs[0], phase_txt, lang='fa', size=9.5, bold=True)
            set_paragraph_bidi(row_c[1].paragraphs[0], WD_ALIGN_PARAGRAPH.JUSTIFY)
            add_run(row_c[1].paragraphs[0], desc_txt, lang='fa', size=9)
            set_paragraph_bidi(row_c[2].paragraphs[0], WD_ALIGN_PARAGRAPH.CENTER)
            add_run(row_c[2].paragraphs[0], count_txt, lang='fa', size=9.5, bold=True)
        else:
            add_run(row_c[0].paragraphs[0], phase_txt, lang='en', size=9.5, bold=True)
            add_run(row_c[1].paragraphs[0], desc_txt, lang='en', size=9)
            row_c[2].paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_run(row_c[2].paragraphs[0], count_txt, lang='en', size=9.5, bold=True)
            
    doc.add_paragraph().paragraph_format.space_after = Pt(12)
    
    # -------------------------------------------------------------
    # 3. Characteristics of Included Studies Table
    # -------------------------------------------------------------
    p_ch_h = doc.add_paragraph()
    if is_fa:
        set_paragraph_bidi(p_ch_h, WD_ALIGN_PARAGRAPH.RIGHT)
        add_run(p_ch_h, "۳. ویژگی‌های مطالعات منتخب کارآزمایی بالینی تصادفی (RCTs):", lang='fa', size=12, bold=True)
    else:
        add_run(p_ch_h, "3. Characteristics of Included Randomized Controlled Trials (RCTs)", lang='en', size=12, bold=True)
    p_ch_h.paragraph_format.space_after = Pt(4)
    
    tbl_studies = doc.add_table(rows=1, cols=6)
    tbl_studies.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_apa_table_borders(tbl_studies, is_rtl=is_fa)
    
    st_headers = ["مطالعه (سال)", "کشور", "حجم نمونه (مداخله/کنترل)", "گروه مداخله", "گروه مقایسه", "مقیاس سنجش"] if is_fa else ["Study (Year)", "Country", "N (Int / Ctrl)", "Intervention Protocol", "Control Condition", "Outcome Scale"]
    for idx, h in enumerate(st_headers):
        c = tbl_studies.rows[0].cells[idx]
        set_cell_background(c, "F2F2F2")
        add_header_underline(c)
        set_cell_margins(c, top=100, bottom=100)
        p = c.paragraphs[0]
        if is_fa:
            set_paragraph_bidi(p, WD_ALIGN_PARAGRAPH.CENTER)
            add_run(p, h, lang='fa', size=9, bold=True)
        else:
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            add_run(p, h, lang='en', size=9, bold=True)
            
    for s in studies:
        row_c = tbl_studies.add_row().cells
        for cell in row_c:
            set_cell_margins(cell, top=70, bottom=70)
            add_row_bottom_border(cell)
            
        n_str = f"{int(s['n_intervention'])} / {int(s['n_control'])}"
        vals = [s["authors_year"], s["country"], n_str, s["intervention_label"], s["control_label"], s["outcome_scale"]]
        for idx, val in enumerate(vals):
            p = row_c[idx].paragraphs[0]
            p.text = ""
            if is_fa:
                set_paragraph_bidi(p, WD_ALIGN_PARAGRAPH.CENTER if idx in [1, 2] else WD_ALIGN_PARAGRAPH.RIGHT)
                add_run(p, val, lang='fa', size=9)
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER if idx in [1, 2] else WD_ALIGN_PARAGRAPH.LEFT
                add_run(p, val, lang='en', size=9)
                
    doc.add_paragraph().paragraph_format.space_after = Pt(12)
    
    # -------------------------------------------------------------
    # 4. Cochrane RoB 2 Risk of Bias Table
    # -------------------------------------------------------------
    p_rob_h = doc.add_paragraph()
    if is_fa:
        set_paragraph_bidi(p_rob_h, WD_ALIGN_PARAGRAPH.RIGHT)
        add_run(p_rob_h, "۴. ارزیابی ریسک تورش بر اساس ابزار Cochrane RoB 2:", lang='fa', size=12, bold=True)
    else:
        add_run(p_rob_h, "4. Methodological Quality & Risk of Bias Assessment (Cochrane RoB 2)", lang='en', size=12, bold=True)
    p_rob_h.paragraph_format.space_after = Pt(4)
    
    tbl_rob = doc.add_table(rows=1, cols=7)
    tbl_rob.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_apa_table_borders(tbl_rob, is_rtl=is_fa)
    
    rob_headers = ["مطالعه", "توالی تصادفی (D1)", "انحراف مداخله (D2)", "داده‌های مفقود (D3)", "سنجش پیامد (D4)", "سوگیری گزارش (D5)", "تورش کلی (Overall)"] if is_fa else ["Study", "Randomization (D1)", "Deviations (D2)", "Missing Data (D3)", "Measurement (D4)", "Reporting (D5)", "Overall Risk of Bias"]
    for idx, h in enumerate(rob_headers):
        c = tbl_rob.rows[0].cells[idx]
        set_cell_background(c, "F2F2F2")
        add_header_underline(c)
        set_cell_margins(c, top=100, bottom=100)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_run(p, h, lang='fa' if is_fa else 'en', size=8.5, bold=True)
        
    for s in studies:
        row_c = tbl_rob.add_row().cells
        for cell in row_c:
            set_cell_margins(cell, top=60, bottom=60)
            add_row_bottom_border(cell)
            
        r = s.get("rob2", {})
        vals = [
            s["authors_year"],
            r.get("D1_randomization", "Low"),
            r.get("D2_deviations", "Low"),
            r.get("D3_missing_data", "Low"),
            r.get("D4_measurement", "Low"),
            r.get("D5_reporting", "Low"),
            r.get("overall", "Low")
        ]
        for idx, val in enumerate(vals):
            p = row_c[idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if idx == 0 and not is_fa else WD_ALIGN_PARAGRAPH.CENTER
            
            # Badge styling
            if val == "Low":
                color = RGBColor(0, 128, 0)
                txt = "پایین (Low)" if is_fa else "Low Risk"
            elif val == "Some concerns":
                color = RGBColor(180, 120, 0)
                txt = "تاحدی مبهم (Some concerns)" if is_fa else "Some concerns"
            elif val == "High":
                color = RGBColor(200, 0, 0)
                txt = "بالا (High)" if is_fa else "High Risk"
            else:
                color = None
                txt = val
                
            add_run(p, txt, lang='fa' if is_fa else 'en', size=8.5, bold=(idx == 6 or idx == 0), color=color if idx > 0 else None)
            
    doc.add_paragraph().paragraph_format.space_after = Pt(12)
    
    # -------------------------------------------------------------
    # 5. Quantitative Synthesis & Forest Plot
    # -------------------------------------------------------------
    p_meta_h = doc.add_paragraph()
    if is_fa:
        set_paragraph_bidi(p_meta_h, WD_ALIGN_PARAGRAPH.RIGHT)
        add_run(p_meta_h, "۵. یافته‌های کمی فراتحلیل و نمودار انباشت (Forest Plot):", lang='fa', size=12, bold=True)
    else:
        add_run(p_meta_h, "5. Quantitative Meta-Analysis & Forest Plot Synthesis", lang='en', size=12, bold=True)
    p_meta_h.paragraph_format.space_after = Pt(4)
    
    # Synthesis Summary Table
    tbl_res = doc.add_table(rows=1, cols=6)
    tbl_res.alignment = WD_TABLE_ALIGNMENT.CENTER
    set_apa_table_borders(tbl_res, is_rtl=is_fa)
    
    res_headers = ["مدل تجمیع / شاخص", "اندازه اثر (Hedges' g)", "خطای استاندارد (SE)", "فاصله اطمینان ۹۵٪", "آماره Z (مقدار p)", "وزن کلی"] if is_fa else ["Pooling Model / Statistic", "Effect Size (Hedges' g)", "Std. Error (SE)", "95% CI", "Z-Value (p-value)", "Total Weight"]
    for idx, h in enumerate(res_headers):
        c = tbl_res.rows[0].cells[idx]
        set_cell_background(c, "F2F2F2")
        add_header_underline(c)
        set_cell_margins(c, top=100, bottom=100)
        p = c.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_run(p, h, lang='fa' if is_fa else 'en', size=9, bold=True)
        
    p_val_fixed = "p < .001" if fixed["p"] < 0.001 else f"p = {fixed['p']:.3f}"
    p_val_rand = "p < .001" if rand["p"] < 0.001 else f"p = {rand['p']:.3f}"
    
    summary_rows = [
        ("مدل اثرات ثابت (Fixed-Effect)" if is_fa else "Fixed-Effect Model (Inverse Variance)", f"{fixed['pooled_g']:.3f}", f"{fixed['se']:.3f}", f"[{fixed['ci_lower']:.3f}, {fixed['ci_upper']:.3f}]", f"Z = {fixed['z']:.2f} ({p_val_fixed})", "100.0%"),
        ("مدل اثرات تصادفی (Random-Effects)" if is_fa else "Random-Effects Model (DerSimonian-Laird)", f"{rand['pooled_g']:.3f}", f"{rand['se']:.3f}", f"[{rand['ci_lower']:.3f}, {rand['ci_upper']:.3f}]", f"Z = {rand['z']:.2f} ({p_val_rand})", "100.0%")
    ]
    for m_label, g_txt, se_txt, ci_txt, z_txt, wt_txt in summary_rows:
        row_c = tbl_res.add_row().cells
        for cell in row_c:
            set_cell_margins(cell, top=80, bottom=80)
            add_row_bottom_border(cell)
        for idx, val in enumerate([m_label, g_txt, se_txt, ci_txt, z_txt, wt_txt]):
            p = row_c[idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if idx == 0 and not is_fa else (WD_ALIGN_PARAGRAPH.RIGHT if idx == 0 else WD_ALIGN_PARAGRAPH.CENTER)
            add_run(p, val, lang='fa' if is_fa else 'en', size=9.5, bold=(idx == 0 or idx == 1))
            
    # Embed Forest Plot Image
    if os.path.exists(forest_img_path):
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_before = Pt(12)
        p_img.paragraph_format.space_after = Pt(4)
        run = p_img.add_run()
        run.add_picture(forest_img_path, width=Inches(6.2))
        
        p_cap = doc.add_paragraph()
        p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_cap.paragraph_format.space_after = Pt(14)
        cap_text = (
            "نمودار ۱. نمودار انباشت (Forest Plot) اندازه اثر تجمیعی درمان مبتنی بر پذیرش و تعهد (ACT) بر شدت اضطراب"
            if is_fa else
            "Figure 1. Forest Plot of the Pooled Effect Size of Acceptance and Commitment Therapy on Anxiety"
        )
        add_run(p_cap, cap_text, lang='fa' if is_fa else 'en', size=9.5, italic=True)
        
    # -------------------------------------------------------------
    # 6. Publication Bias & Funnel Plot
    # -------------------------------------------------------------
    p_bias_h = doc.add_paragraph()
    if is_fa:
        set_paragraph_bidi(p_bias_h, WD_ALIGN_PARAGRAPH.RIGHT)
        add_run(p_bias_h, "۶. ارزیابی سوگیری انتشار و نمودار قیفی (Funnel Plot):", lang='fa', size=12, bold=True)
    else:
        add_run(p_bias_h, "6. Publication Bias & Funnel Plot Asymmetry Diagnostics", lang='en', size=12, bold=True)
    p_bias_h.paragraph_format.space_after = Pt(4)
    
    p_bias_narrative = doc.add_paragraph()
    if is_fa:
        set_paragraph_bidi(p_bias_narrative, WD_ALIGN_PARAGRAPH.JUSTIFY)
        b_txt = (
            f"جهت بررسی سوگیری انتشار (Publication Bias)، از آزمون رگرسیون خطی اگـر (Egger's Linear Regression Test) و نمودار قیفی استفاده شد. "
            f"عرض از مبدأ به دست آمده در آزمون اگر برابر با {bias['egger_intercept']:.2f} (خطای استاندارد = {bias['egger_se_intercept']:.2f}) و مقدار t = {bias['egger_t']:.2f} با سطح معناداری p = {bias['egger_p']:.3f} می‌باشد. "
            f"با توجه به این‌که مقدار p بزرگتر از ۰/۰۵ است (p > .05)، فرضیه وجود سوگیری انتشار ناشی از اثر مطالعات کوچک (Small-Study Effects) رد شده و تقارن نمودار قیفی تایید می‌گردد."
            if not bias["has_bias"] else
            f"با توجه به سطح معناداری آزمون اگر (p = {bias['egger_p']:.3f} < .05)، شواهدی از عدم تقارن نمودار قیفی و وجود سوگیری انتشار احتمالی در پیشینه پژوهشی مشاهده می‌شود."
        )
        add_run(p_bias_narrative, b_txt, lang='fa', size=10.5)
    else:
        p_bias_narrative.paragraph_format.line_spacing = 1.15
        b_txt = (
            f"Publication bias was evaluated using Egger's linear regression test and funnel plot visual inspection. "
            f"The regression intercept was estimated at {bias['egger_intercept']:.2f} (SE = {bias['egger_se_intercept']:.2f}, t = {bias['egger_t']:.2f}, p = {bias['egger_p']:.3f}). "
            f"Because p > .05, there is no statistically significant evidence of funnel plot asymmetry or small-study effects, indicating that publication bias did not materially distort the pooled findings."
            if not bias["has_bias"] else
            f"Because Egger's regression test indicated statistically significant asymmetry (t = {bias['egger_t']:.2f}, p = {bias['egger_p']:.3f} < .05), evidence of potential small-study publication bias is noted."
        )
        add_run(p_bias_narrative, b_txt, lang='en', size=10.5)
    p_bias_narrative.paragraph_format.space_after = Pt(8)
    
    # Embed Funnel Plot Image
    if os.path.exists(funnel_img_path):
        p_fimg = doc.add_paragraph()
        p_fimg.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_fimg.paragraph_format.space_before = Pt(8)
        p_fimg.paragraph_format.space_after = Pt(4)
        run_f = p_fimg.add_run()
        run_f.add_picture(funnel_img_path, width=Inches(5.4))
        
        p_fcap = doc.add_paragraph()
        p_fcap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_fcap.paragraph_format.space_after = Pt(14)
        fcap_text = (
            "نمودار ۲. نمودار قیفی (Funnel Plot) توزیع خطای استاندارد و اندازه اثر مطالعات جهت بررسی سوگیری انتشار"
            if is_fa else
            "Figure 2. Funnel Plot of Standard Error by Hedges' g with Pseudo 95% Confidence Bounds"
        )
        add_run(p_fcap, fcap_text, lang='fa' if is_fa else 'en', size=9.5, italic=True)
        
    doc.save(out_docx_path)
    return out_docx_path

# ==============================================================================
# MAIN DRIVER
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(description="PRISMA 2020 & Cochrane Meta-Analysis Computational Engine")
    parser.add_argument("--json", required=True, help="Path to input JSON payload")
    parser.add_argument("--out-dir", default="./meta_analysis_results", help="Directory to save generated artifacts")
    parser.add_argument("--lang", choices=["en", "fa"], default="en", help="Language mode (en or fa)")
    
    args = parser.parse_args()
    
    with open(args.json, "r", encoding="utf-8") as f:
        payload = json.load(f)
        
    studies = payload.get("studies", [])
    if not studies:
        print("[ERROR] No studies found in the provided payload JSON.")
        sys.exit(1)
        
    os.makedirs(args.out_dir, exist_ok=True)
    
    # 1. Run Quantitative Meta-Analysis
    meta_res = run_meta_analysis(studies)
    
    # Save quantitative results JSON
    stats_json_path = os.path.join(args.out_dir, "meta_analysis_statistics.json")
    with open(stats_json_path, "w", encoding="utf-8") as f:
        json.dump(meta_res, f, indent=2, ensure_ascii=False)
    print(f"[SUCCESS] Meta-analysis calculations completed: {stats_json_path}")
    
    # 2. Generate Visual Plots
    forest_path = os.path.join(args.out_dir, "forest_plot.png")
    plot_forest(meta_res, forest_path, title="Forest Plot: Pooled Treatment Efficacy (Hedges' g)" if args.lang == "en" else "نمودار انباشت (Forest Plot) اندازه اثر تجمیعی درمان")
    print(f"[SUCCESS] Generated Forest Plot: {forest_path}")
    
    funnel_path = os.path.join(args.out_dir, "funnel_plot.png")
    plot_funnel(meta_res, funnel_path, title="Funnel Plot: Publication Bias Assessment (Pseudo 95% CI)" if args.lang == "en" else "نمودار قیفی (Funnel Plot) بررسی سوگیری انتشار")
    print(f"[SUCCESS] Generated Funnel Plot: {funnel_path}")
    
    # 3. Generate Word Report
    report_name = "Systematic_Review_and_Meta_Analysis_Report.docx"
    report_path = os.path.join(args.out_dir, report_name)
    compile_meta_analysis_report(payload, meta_res, forest_path, funnel_path, report_path, lang=args.lang)
    print(f"[SUCCESS] Generated APA 7 Manuscript: {report_path}")
    
    # Console Summary
    rand = meta_res["random_effects"]
    het = meta_res["heterogeneity"]
    bias = meta_res["publication_bias"]
    print("\n" + "="*70)
    print(f" META-ANALYSIS SUMMARY (k = {meta_res['k']} Studies)")
    print("="*70)
    print(f" Pooled Effect (Hedges' g): {rand['pooled_g']:.3f} (95% CI: [{rand['ci_lower']:.3f}, {rand['ci_upper']:.3f}])")
    print(f" Test of Null (Z):          {rand['z']:.2f} (p = {rand['p']:.4f})")
    print(f" Heterogeneity:             Q = {het['q']:.2f} (p = {het['p_value']:.4f}), I² = {het['i_squared']:.1f}%, τ² = {het['tau_squared']:.3f}")
    print(f" Egger's Publication Bias:  t = {bias['egger_t']:.2f} (p = {bias['egger_p']:.4f}) -> Bias: {bias['has_bias']}")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
