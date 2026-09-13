#!/usr/bin/env python3
"""
Publication-Grade Scientific Visualization Engine (visualize_stats.py)
======================================================================
Author: Saber Ghaderi
Repository: GhaderiSaber/AcademicSuite
Description:
    Generates 300-DPI, colorblind-safe publication-ready scientific figures
    with automated statistical significance brackets (* p < .05, ** p < .01, *** p < .001, ns),
    pre-post experimental interaction plots, and correlation heatmaps for ISI/Scopus manuscripts
    and graduate thesis Chapter 4 defenses.
"""

import os
import sys
import argparse
from typing import List, Dict, Optional, Tuple, Union

import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Publication visual defaults (Nature / APA 7 aesthetic)
plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial', 'Helvetica']
plt.rcParams['axes.edgecolor'] = '#334155'
plt.rcParams['axes.linewidth'] = 1.0
plt.rcParams['grid.color'] = '#E2E8F0'
plt.rcParams['grid.linestyle'] = '--'
plt.rcParams['grid.alpha'] = 0.6

# Colorblind-safe palette (Wong / Tol inspired)
COLOR_PALETTE = ["#2563EB", "#059669", "#D97706", "#7C3AED", "#DC2626", "#0D9488"]

def get_p_annotation(p_val: float) -> str:
    """Format p-value into APA standard significance stars or 'ns'."""
    if p_val < 0.001:
        return "***\n(p < .001)"
    elif p_val < 0.01:
        return f"**\n(p = {p_val:.3f})"[0:2] + f"\n(p = {p_val:.3f})"[2:].replace(' 0.', ' .')
    elif p_val < 0.05:
        return f"*\n(p = {p_val:.3f})"[0:1] + f"\n(p = {p_val:.3f})"[1:].replace(' 0.', ' .')
    else:
        return f"ns\n(p = {p_val:.3f})".replace(' 0.', ' .')

def add_significance_bracket(ax, x1: float, x2: float, y: float, h: float, p_val: float, custom_text: Optional[str] = None):
    """
    Draw publication significance bracket over compared groups.
    x1, x2: horizontal centers of compared bars
    y: vertical baseline height
    h: vertical height of bracket ticks
    p_val: p-value to determine stars
    """
    text = custom_text if custom_text else get_p_annotation(p_val)

    # Bracket line: (x1, y) -> (x1, y+h) -> (x2, y+h) -> (x2, y)
    ax.plot([x1, x1, x2, x2], [y, y + h, y + h, y], lw=1.2, c='#1E293B')

    # Asterisk/text placement
    ax.text((x1 + x2) * 0.5, y + h + (h * 0.25), text, ha='center', va='bottom',
            color='#0F172A', fontsize=9.5, fontweight='bold')

def plot_group_comparison(groups: List[str], means: List[float], sds: List[float],
                           p_val: float, title: str, ylabel: str,
                           output_path: str, effect_size_str: Optional[str] = None,
                           xlabel: str = "گروه / شرایط آزمایشی", dpi: int = 300):
    """Generate publication bar chart with SE error bars and significance bracket."""
    fig, ax = plt.subplots(figsize=(6.5, 5.0), dpi=dpi)

    x_pos = np.arange(len(groups))
    colors = COLOR_PALETTE[:len(groups)]

    bars = ax.bar(x_pos, means, yerr=sds, align='center', alpha=0.88,
                  ecolor='#334155', capsize=5, color=colors, edgecolor='#1E293B',
                  linewidth=1.2, width=0.55)

    # Values on top of bars
    for bar, m in zip(bars, means):
        y_text = bar.get_height() * 0.5
        ax.text(bar.get_x() + bar.get_width() / 2, y_text, f"M = {m:.2f}",
                ha='center', va='center', color='white', fontweight='bold', fontsize=10)

    # Bracket height calculation
    max_y = max([m + s for m, s in zip(means, sds)])
    y_bracket = max_y * 1.08
    h_bracket = max_y * 0.05

    if len(groups) == 2:
        add_significance_bracket(ax, 0, 1, y_bracket, h_bracket, p_val)

    # Effect size badge if provided
    if effect_size_str:
        ax.text(0.98, 0.04, effect_size_str, transform=ax.transAxes,
                ha='right', va='bottom', fontsize=10, fontweight='semibold',
                bbox=dict(boxstyle='round,pad=0.5', facecolor='#F1F5F9', edgecolor='#CBD5E1', alpha=0.9))

    ax.set_xticks(x_pos)
    ax.set_xticklabels(groups, fontsize=11, fontweight='bold', color='#1E293B')
    ax.set_ylabel(ylabel, fontsize=11, fontweight='semibold', color='#1E293B')
    ax.set_title(title, fontsize=13, fontweight='bold', pad=18, color='#0F172A')
    ax.set_ylim(0, max_y * 1.35)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', linestyle='--', alpha=0.5)

    plt.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    plt.close()
    print(f"[✓] Publication group comparison figure exported: {output_path}")

def plot_pre_post_interaction(groups: List[str], pre_means: List[float], post_means: List[float],
                              pre_sds: List[float], post_sds: List[float],
                              p_interaction: float, title: str, ylabel: str,
                              output_path: str, dpi: int = 300):
    """Generate RCT / Quasi-Experimental pre-post interaction trajectory plot."""
    fig, ax = plt.subplots(figsize=(7.0, 5.2), dpi=dpi)

    x_points = [0, 1]
    time_labels = ["پیش‌آزمون (Pre-test)", "پس‌آزمون (Post-test)"]
    markers = ['o', 's', '^', 'D']

    for idx, grp in enumerate(groups):
        m_vals = [pre_means[idx], post_means[idx]]
        sd_vals = [pre_sds[idx], post_sds[idx]]
        color = COLOR_PALETTE[idx % len(COLOR_PALETTE)]

        ax.errorbar(x_points, m_vals, yerr=sd_vals, label=grp,
                    color=color, marker=markers[idx % len(markers)], markersize=8,
                    linewidth=2.4, capsize=4, capthick=1.2, alpha=0.9)

        # Labels next to points
        for xp, y_val in zip(x_points, m_vals):
            ax.annotate(f"{y_val:.2f}", (xp, y_val), textcoords="offset points",
                        xytext=(0, 10), ha='center', fontsize=9.5, fontweight='bold', color=color)

    ax.set_xticks(x_points)
    ax.set_xticklabels(time_labels, fontsize=11, fontweight='bold')
    ax.set_ylabel(ylabel, fontsize=11, fontweight='semibold')
    ax.set_title(title, fontsize=13, fontweight='bold', pad=15)

    # Interaction note
    p_str = get_p_annotation(p_interaction).replace('\n', ' ')
    ax.text(0.5, 0.05, f"اثر تعاملی گروه × زمان: {p_str}", transform=ax.transAxes,
            ha='center', va='bottom', fontsize=10, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#FEF3C7', edgecolor='#FCD34D', alpha=0.9))

    ax.legend(frameon=True, facecolor='white', edgecolor='#E2E8F0', fontsize=10, loc='best')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(True, linestyle='--', alpha=0.5)

    plt.tight_layout()
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    plt.close()
    print(f"[✓] Pre-post interaction trajectory figure exported: {output_path}")

def plot_regression_residual_diagnostics(zresiduals: Union[List[float], np.ndarray],
                                         output_prefix: str,
                                         dv_name: str = "DV",
                                         title_fa: Optional[str] = None,
                                         dpi: int = 300) -> Tuple[str, str]:
    """
    Generate APA 7 / SPSS standard diagnostic plots for regression standardized residuals:
    1. Histogram of Standardized Residuals with fitted Theoretical Normal Distribution Curve.
    2. Normal P-P Plot (Observed Cumulative Probability vs. Expected Cumulative Probability).
    
    Returns tuple of filepaths: (hist_path, pp_path)
    """
    zres = np.array(zresiduals, dtype=float)
    zres = zres[~np.isnan(zres)]
    n = len(zres)
    if n < 5:
        raise ValueError("Insufficient data points for residual diagnostic plots.")

    os.makedirs(os.path.dirname(os.path.abspath(output_prefix)), exist_ok=True)
    hist_path = f"{output_prefix}_hist.png"
    pp_path = f"{output_prefix}_pp.png"

    # -------------------------------------------------------------
    # 1. SPSS-Style Histogram with Fitted Normal Curve
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7.2, 4.8), dpi=dpi)
    mean_val = float(np.mean(zres))
    sd_val = float(np.std(zres, ddof=1))

    # Plot histogram bars (SPSS blue style)
    bins_range = np.linspace(-3.5, 3.5, 21)
    counts, bins, patches = ax.hist(zres, bins=bins_range, density=False, color='#0288D1',
                                    edgecolor='white', alpha=0.95, linewidth=0.8)

    # Overlay scaled normal curve
    x_axis = np.linspace(-3.5, 3.5, 250)
    bin_width = bins[1] - bins[0]
    normal_curve = stats.norm.pdf(x_axis, mean_val, sd_val) * n * bin_width
    ax.plot(x_axis, normal_curve, color='#000000', linewidth=2.2)

    # SPSS-style top right stats text
    info_text = f"Mean = {mean_val:.2e}\nStd. Dev. = {sd_val:.3f}\nN = {n}"
    ax.text(0.96, 0.94, info_text, transform=ax.transAxes, ha='right', va='top',
            fontsize=9.5, family='sans-serif', color='#000000')

    ax.set_title("Histogram\n", fontsize=13, fontweight='bold', pad=2, color='#000000')
    ax.text(0.5, 1.02, f"Dependent Variable: {dv_name}", transform=ax.transAxes,
            ha='center', va='bottom', fontsize=11, fontweight='bold', color='#000000')
    ax.set_xlabel("Regression Standardized Residual", fontsize=11, fontweight='bold', color='#000000', labelpad=10)
    ax.set_ylabel("Frequency", fontsize=11, fontweight='bold', color='#000000', labelpad=8)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', linestyle='-', color='#CCCCCC', alpha=0.7)
    ax.set_xlim(-3.8, 3.8)
    ax.set_ylim(0, max(counts) * 1.25)

    plt.tight_layout()
    plt.savefig(hist_path, dpi=dpi, bbox_inches='tight')
    plt.close()

    # -------------------------------------------------------------
    # 2. SPSS-Style Normal P-P Plot of Standardized Residuals
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.2, 5.2), dpi=dpi)

    sorted_res = np.sort(zres)
    # Observed cumulative probabilities
    obs_cum_prob = (np.arange(1, n + 1) - 0.5) / n
    # Expected cumulative probabilities under normal distribution
    exp_cum_prob = stats.norm.cdf(sorted_res, loc=mean_val, scale=sd_val)

    # 45-degree diagonal reference line
    ax.plot([0, 1], [0, 1], color='#000000', linewidth=1.5, linestyle='-')
    # Scatter points (SPSS style: cyan circles with thin black outline)
    ax.scatter(exp_cum_prob, obs_cum_prob, facecolor='#29B6F6', edgecolor='#000000',
               s=22, alpha=0.9, linewidth=0.6)

    ax.set_title("Normal P-P Plot of Regression Standardized Residual\n", fontsize=11.5, fontweight='bold', pad=2, color='#000000')
    ax.text(0.5, 1.02, f"Dependent Variable: {dv_name}", transform=ax.transAxes,
            ha='center', va='bottom', fontsize=10.5, fontweight='bold', color='#000000')
    ax.set_xlabel("Observed Cum Prob", fontsize=10.5, fontweight='bold', color='#000000', labelpad=8)
    ax.set_ylabel("Expected Cum Prob", fontsize=10.5, fontweight='bold', color='#000000', labelpad=8)

    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.set_aspect('equal', adjustable='box')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', linestyle='-', color='#CCCCCC', alpha=0.7)

    plt.tight_layout()
    plt.savefig(pp_path, dpi=dpi, bbox_inches='tight')
    plt.close()

    print(f"[✓] Residual diagnostics exported: {hist_path} and {pp_path}")
    return hist_path, pp_path

def main():
    parser = argparse.ArgumentParser(description="Publication-Grade Statistical Visualization Engine")
    parser.add_argument("--demo", action="store_true", help="Generate sample publication demonstration plots.")
    parser.add_argument("--residuals-demo", action="store_true", help="Generate sample regression residual diagnostic plots.")
    parser.add_argument("--out-dir", default="./publication_plots", help="Directory to save generated figures.")
    args = parser.parse_args()

    if args.demo:
        os.makedirs(args.out_dir, exist_ok=True)
        # Demo 1: Group comparison with bracket
        plot_group_comparison(
            groups=["گروه کنترل", "گروه مداخله (ACT)"],
            means=[14.20, 22.85],
            sds=[2.10, 2.45],
            p_val=0.0004,
            title="مقایسه انعطاف‌پذیری روان‌شناختی در پس‌آزمون بین دو گروه",
            ylabel="میانگین نمره انعطاف‌پذیری",
            effect_size_str="Cohen's d = 1.05 | η²p = .216",
            output_path=os.path.join(args.out_dir, "group_comparison_bracket_demo.png")
        )
        # Demo 2: Pre-Post Interaction
        plot_pre_post_interaction(
            groups=["گروه آزمایش (ACT)", "گروه گواه (Control)"],
            pre_means=[14.10, 14.30],
            post_means=[23.40, 14.80],
            pre_sds=[2.20, 2.15],
            post_sds=[2.35, 2.10],
            p_interaction=0.0002,
            title="تعامل زمان × گروه در بهبود بهزیستی روان‌شناختی",
            ylabel="نمره بهزیستی روان‌شناختی",
            output_path=os.path.join(args.out_dir, "pre_post_interaction_demo.png")
        )
        print("[✓] Demo scientific visualization figures successfully generated!")

    if args.residuals_demo:
        os.makedirs(args.out_dir, exist_ok=True)
        rng = np.random.default_rng(42)
        mock_zres = rng.normal(loc=0.0, scale=1.0, size=260)
        h, p = plot_regression_residual_diagnostics(
            mock_zres,
            output_prefix=os.path.join(args.out_dir, "hypothesis_1_residuals"),
            title_fa="سبک‌های فرزندپروری بر اضطراب فراگیر"
        )
        print(f"[✓] Residuals demo plots created: {h}, {p}")

if __name__ == "__main__":
    main()
