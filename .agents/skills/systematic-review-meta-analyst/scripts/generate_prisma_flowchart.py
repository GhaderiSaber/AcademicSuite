#!/usr/bin/env python3
"""
PRISMA 2020 Flow Diagram Generator (generate_prisma_flowchart.py)
================================================================
Author: Saber Ghaderi
Repository: GhaderiSaber/AcademicSuite
Description:
    Renders publication-grade 300-DPI PRISMA 2020 (Page et al., 2021)
    flow diagrams for systematic reviews and meta-analyses.
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
             bg_color: str = "#F8FAFC", border_color: str = "#0284C7",
             title: Optional[str] = None, fontsize: float = 8.5):
    """Draw a styled rounded rectangle box with centered multi-line text."""
    box = FancyBboxPatch((x, y), w, h,
                         boxstyle="round,pad=0.02,rounding_size=0.03",
                         facecolor=bg_color, edgecolor=border_color,
                         linewidth=1.3, zorder=3)
    ax.add_patch(box)
    full_text = f"\\textbf{{{title}}}\n{text}" if title else text
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
                         facecolor="#1E3A8A", edgecolor="#1E3A8A",
                         zorder=3)
    ax.add_patch(box)
    ax.text(x + w / 2, y + h / 2, label,
            ha='center', va='center', rotation=90,
            fontsize=10, fontweight='bold', color='white', zorder=4)

def generate_prisma_diagram(counts: Dict[str, Any], output_path: str, dpi: int = 300):
    """Render full PRISMA 2020 4-phase flowchart to 300-DPI PNG."""
    fig, ax = plt.subplots(figsize=(10.0, 11.5), dpi=dpi)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.axis('off')

    # Data defaults
    db_id = counts.get("databases_identified", 450)
    reg_id = counts.get("registers_identified", 35)
    dup_rem = counts.get("duplicates_removed", 85)
    inelig_auto = counts.get("ineligible_automated", 20)
    screened = counts.get("records_screened", db_id + reg_id - dup_rem - inelig_auto)
    excluded = counts.get("records_excluded", 260)
    retrieval_sought = counts.get("reports_sought", screened - excluded)
    not_retrieved = counts.get("reports_not_retrieved", 12)
    assessed = counts.get("reports_assessed", retrieval_sought - not_retrieved)
    excl_reasons = counts.get("excluded_with_reasons", {
        "جمعیت نامتناسب (Ineligible population)": 42,
        "فقدان گروه کنترل (No control group)": 28,
        "داده‌های آماری ناکافی (Insufficient data)": 18
    })
    total_excl_full = sum(excl_reasons.values())
    included_qual = counts.get("included_qualitative", assessed - total_excl_full)
    included_meta = counts.get("included_quantitative", included_qual)

    # 1. Phase Banners (Left column)
    draw_phase_banner(ax, 2, 75, 4, 20, "شناسایی (Identification)")
    draw_phase_banner(ax, 2, 53, 4, 18, "غربالگری (Screening)")
    draw_phase_banner(ax, 2, 28, 4, 21, "ارزیابی نهایی (Eligibility)")
    draw_phase_banner(ax, 2, 6, 4, 18, "ورود نهایی (Included)")

    # 2. Stage 1: Identification
    box1_txt = f"پیشینه‌های شناسایی‌شده از پایگاه‌های اطلاعاتی:\n(PubMed, Scopus, SID, Magiran)\n(N = {db_id})"
    box2_txt = f"پیشینه‌های شناسایی‌شده از سایر منابع\nیا ثبت کارآزمایی‌ها (IRCT, ClinicalTrials):\n(N = {reg_id})"
    draw_box(ax, 10, 84, 38, 11, box1_txt, bg_color="#EFF6FF", border_color="#2563EB")
    draw_box(ax, 52, 84, 38, 11, box2_txt, bg_color="#EFF6FF", border_color="#2563EB")

    box_dups_txt = f"پیشینه‌های حذف‌شده پیش از غربالگری:\n• مقالات تکراری (N = {dup_rem})\n• حذف‌شده با ابزارهای خودکار (N = {inelig_auto})"
    draw_box(ax, 30, 69, 42, 10, box_dups_txt, bg_color="#FEF2F2", border_color="#DC2626")

    draw_arrow(ax, 29, 84, 45, 79)
    draw_arrow(ax, 71, 84, 55, 79)

    # 3. Stage 2: Screening
    box_screen_txt = f"مجموع عناوین و چکیده‌های غربال‌شده:\n(N = {screened})"
    draw_box(ax, 16, 54, 36, 9, box_screen_txt, bg_color="#F8FAFC", border_color="#0D9488")

    box_excl_screen_txt = f"پیشینه‌های حذف‌شده در مرحله چکیده:\n(N = {excluded})"
    draw_box(ax, 58, 54, 36, 9, box_excl_screen_txt, bg_color="#FEF2F2", border_color="#DC2626")

    draw_arrow(ax, 51, 69, 34, 63)
    draw_arrow(ax, 34, 54, 34, 46)
    draw_arrow(ax, 43, 58.5, 58, 58.5)

    # 4. Stage 3: Retrieval & Full-Text Eligibility
    box_sought_txt = f"گزارش‌های درخواست‌شده برای متن کامل:\n(N = {retrieval_sought})"
    draw_box(ax, 16, 38, 36, 8, box_sought_txt, bg_color="#F8FAFC", border_color="#0D9488")

    box_not_retr_txt = f"گزارش‌های بازیابی‌نشده:\n(N = {not_retrieved})"
    draw_box(ax, 58, 38, 36, 8, box_not_retr_txt, bg_color="#FEF2F2", border_color="#DC2626")

    draw_arrow(ax, 34, 38, 34, 31)
    draw_arrow(ax, 43, 42, 58, 42)

    box_assessed_txt = f"مقالات ارزیابی‌شده بر اساس متن کامل:\n(N = {assessed})"
    draw_box(ax, 16, 23, 36, 8, box_assessed_txt, bg_color="#F8FAFC", border_color="#0D9488")

    reasons_str = "\n".join([f"• {k} (N = {v})" for k, v in excl_reasons.items()])
    box_excl_full_txt = f"مقالات متن کامل حذف‌شده با دلایل مشخص:\n(مجموع N = {total_excl_full})\n{reasons_str}"
    draw_box(ax, 56, 19, 40, 12, box_excl_full_txt, bg_color="#FEF2F2", border_color="#DC2626", fontsize=8.0)

    draw_arrow(ax, 34, 23, 34, 15)
    draw_arrow(ax, 43, 27, 56, 27)

    # 5. Stage 4: Included
    box_qual_txt = f"مطالعات واردشده به سنتز کیفی:\n(N = {included_qual})"
    draw_box(ax, 16, 8, 36, 7, box_qual_txt, bg_color="#F0FDF4", border_color="#16A34A")

    box_meta_txt = f"مطالعات واردشده به فراتحلیل کمّی:\n(N = {included_meta})"
    draw_box(ax, 58, 8, 36, 7, box_meta_txt, bg_color="#F0FDF4", border_color="#16A34A")

    draw_arrow(ax, 43, 11.5, 58, 11.5)

    # Title header
    ax.text(50, 98, "نمودار جریان غربالگری و انتخاب مطالعات بر پایه استانداردهای PRISMA 2020",
            ha='center', va='top', fontsize=12.5, fontweight='bold', color='#0F172A')

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    plt.close()
    print(f"[✓] PRISMA 2020 Flowchart successfully exported at: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="PRISMA 2020 Flowchart Generator")
    parser.add_argument("--json", help="Path to JSON file containing PRISMA screening counts.")
    parser.add_argument("--output", default="./prisma_2020_flowchart.png", help="Output PNG path.")
    parser.add_argument("--dpi", type=int, default=300, help="Output DPI resolution.")
    args = parser.parse_args()

    counts = {}
    if args.json and os.path.exists(args.json):
        with open(args.json, 'r', encoding='utf-8') as f:
            counts = json.load(f)

    generate_prisma_diagram(counts, args.output, dpi=args.dpi)

if __name__ == "__main__":
    main()
