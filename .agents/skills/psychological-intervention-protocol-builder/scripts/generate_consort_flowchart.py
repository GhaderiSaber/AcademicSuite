#!/usr/bin/env python3
"""
CONSORT 2010 Participant Flowchart Generator (generate_consort_flowchart.py)
==========================================================================
Author: Saber Ghaderi
Repository: GhaderiSaber/AcademicSuite
Description:
    Renders publication-grade 300-DPI CONSORT 2010 (Schulz et al., 2010)
    flow diagrams for randomized controlled trials (RCTs) and psychological interventions.
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, Optional

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

def draw_box(ax, x: float, y: float, w: float, h: float, text: str,
             bg_color: str = "#F8FAFC", border_color: str = "#4338CA",
             fontsize: float = 8.5):
    """Draw a styled rounded rectangle box with centered multi-line text."""
    box = FancyBboxPatch((x, y), w, h,
                         boxstyle="round,pad=0.02,rounding_size=0.03",
                         facecolor=bg_color, edgecolor=border_color,
                         linewidth=1.3, zorder=3)
    ax.add_patch(box)
    ax.text(x + w / 2, y + h / 2, text,
            ha='center', va='center', fontsize=fontsize,
            color='#0F172A', wrap=True, zorder=4)

def draw_arrow(ax, x1: float, y1: float, x2: float, y2: float):
    """Draw clean directional connector arrow."""
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color="#475569", lw=1.3),
                zorder=2)

def draw_phase_banner(ax, x: float, y: float, w: float, h: float, label: str):
    """Draw left-side vertical category header banner."""
    box = FancyBboxPatch((x, y), w, h,
                         boxstyle="round,pad=0.01,rounding_size=0.02",
                         facecolor="#312E81", edgecolor="#312E81",
                         zorder=3)
    ax.add_patch(box)
    ax.text(x + w / 2, y + h / 2, label,
            ha='center', va='center', rotation=90,
            fontsize=10, fontweight='bold', color='white', zorder=4)

def generate_consort_diagram(counts: Dict[str, Any], output_path: str, dpi: int = 300):
    """Render full CONSORT 2010 4-stage participant diagram to 300-DPI PNG."""
    fig, ax = plt.subplots(figsize=(10.0, 11.5), dpi=dpi)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Data defaults
    assessed = counts.get("assessed_for_eligibility", 75)
    excl_not_meeting = counts.get("excluded_not_meeting", 15)
    excl_declined = counts.get("excluded_declined", 12)
    excl_other = counts.get("excluded_other", 3)
    total_excl = excl_not_meeting + excl_declined + excl_other
    randomized = counts.get("randomized", assessed - total_excl)
    n_group = randomized // 2

    # 1. Phase Banners (Left column)
    draw_phase_banner(ax, 2, 74, 4, 21, "ثبت‌نام و غربالگری (Enrollment)")
    draw_phase_banner(ax, 2, 51, 4, 20, "تخصیص تصادفی (Allocation)")
    draw_phase_banner(ax, 2, 28, 4, 20, "پیگیری مداخله (Follow-Up)")
    draw_phase_banner(ax, 2, 6, 4, 19, "تحلیل نهایی (Analysis)")

    # 2. Stage 1: Enrollment
    box_enroll_txt = f"غربالگری اولیه و ارزیابی ملاک‌های ورود:\n(N = {assessed})"
    draw_box(ax, 16, 85, 36, 9, box_enroll_txt, bg_color="#EEF2FF", border_color="#4F46E5")

    box_excl_txt = (
        f"مشارکت‌کنندگان خارج‌شده از مطالعه:\n"
        f"(مجموع N = {total_excl})\n"
        f"• عدم احراز ملاک‌های ورود (N = {excl_not_meeting})\n"
        f"• عدم تمایل یا انصراف داوطلبانه (N = {excl_declined})\n"
        f"• سایر دلایل (مشکلات رفت‌وآمد) (N = {excl_other})"
    )
    draw_box(ax, 56, 80, 40, 15, box_excl_txt, bg_color="#FEF2F2", border_color="#DC2626", fontsize=8.0)

    draw_arrow(ax, 34, 85, 34, 76)
    draw_arrow(ax, 34, 87.5, 56, 87.5)

    box_rand_txt = f"تخصیص تصادفی خوشه‌ای به گروه‌ها (Randomized):\n(N = {randomized})"
    draw_box(ax, 16, 68, 36, 8, box_rand_txt, bg_color="#EEF2FF", border_color="#4F46E5")

    draw_arrow(ax, 34, 68, 34, 62)

    # 3. Stage 2: Allocation
    box_alloc_exp = (
        f"تخصیص‌یافته به گروه مداخله (ACT):\n(n = {n_group})\n"
        f"• دریافت مداخله طبق پروتکل ۸ جلسه‌ای (n = {n_group})\n"
        f"• عدم دریافت مداخله (n = 0)"
    )
    box_alloc_ctrl = (
        f"تخصیص‌یافته به گروه کنترل / لیست انتظار:\n(n = {n_group})\n"
        f"• دریافت شرایط کنترل عادی (n = {n_group})\n"
        f"• عدم تمایل به ادامه حضور (n = 0)"
    )
    draw_box(ax, 10, 50, 38, 12, box_alloc_exp, bg_color="#F8FAFC", border_color="#0284C7")
    draw_box(ax, 54, 50, 38, 12, box_alloc_ctrl, bg_color="#F8FAFC", border_color="#0284C7")

    draw_arrow(ax, 34, 62, 29, 62)
    draw_arrow(ax, 29, 62, 29, 62)
    ax.plot([29, 73], [62, 62], lw=1.3, c="#475569")
    draw_arrow(ax, 29, 62, 29, 62)
    draw_arrow(ax, 73, 62, 73, 62)
    draw_arrow(ax, 29, 62, 29, 62)

    # Down arrows from horizontal split
    draw_arrow(ax, 29, 62, 29, 62)
    ax.annotate("", xy=(29, 62), xytext=(29, 62), arrowprops=dict(arrowstyle="->", color="#475569", lw=1.3))

    # 4. Stage 3: Follow-up
    box_fu_exp = (
        f"ریزش یا پیگیری گروه مداخله:\n"
        f"• از دست رفتن پیگیری (غیبت > ۲ جلسه) (n = 1)\n"
        f"• قطع مداخله به دلایل شخصی (n = 0)"
    )
    box_fu_ctrl = (
        f"ریزش یا پیگیری گروه کنترل:\n"
        f"• از دست رفتن پیگیری در پس‌آزمون (n = 1)\n"
        f"• انتقال به شهر دیگر (n = 0)"
    )
    draw_box(ax, 10, 29, 38, 10, box_fu_exp, bg_color="#F8FAFC", border_color="#0D9488")
    draw_box(ax, 54, 29, 38, 10, box_fu_ctrl, bg_color="#F8FAFC", border_color="#0D9488")

    draw_arrow(ax, 29, 50, 29, 39)
    draw_arrow(ax, 73, 50, 73, 39)

    # 5. Stage 4: Analysis
    box_ana_exp = (
        f"تحلیل نهایی گروه آزمایش:\n(n = {n_group - 1})\n"
        f"• خارج‌شده از تحلیل به دلیل داده‌های مفقود (n = 0)"
    )
    box_ana_ctrl = (
        f"تحلیل نهایی گروه کنترل:\n(n = {n_group - 1})\n"
        f"• خارج‌شده از تحلیل به دلیل داده‌های مفقود (n = 0)"
    )
    draw_box(ax, 10, 8, 38, 9, box_ana_exp, bg_color="#F0FDF4", border_color="#16A34A")
    draw_box(ax, 54, 8, 38, 9, box_ana_ctrl, bg_color="#F0FDF4", border_color="#16A34A")

    draw_arrow(ax, 29, 29, 29, 17)
    draw_arrow(ax, 73, 29, 73, 17)

    # Title header
    ax.text(50, 98, "نمودار جریان شرکت‌کنندگان کارآزمایی بالینی بر پایه استانداردهای CONSORT 2010",
            ha='center', va='top', fontsize=12.5, fontweight='bold', color='#0F172A')

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    plt.close()
    print(f"[✓] CONSORT 2010 Flowchart successfully exported at: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="CONSORT 2010 Participant Flowchart Generator")
    parser.add_argument("--json", help="Path to JSON file containing CONSORT enrollment counts.")
    parser.add_argument("--output", default="./consort_2010_flowchart.png", help="Output PNG path.")
    parser.add_argument("--dpi", type=int, default=300, help="Output DPI resolution.")
    args = parser.parse_args()

    counts = {}
    if args.json and os.path.exists(args.json):
        with open(args.json, 'r', encoding='utf-8') as f:
            counts = json.load(f)

    generate_consort_diagram(counts, args.output, dpi=args.dpi)

if __name__ == "__main__":
    main()
