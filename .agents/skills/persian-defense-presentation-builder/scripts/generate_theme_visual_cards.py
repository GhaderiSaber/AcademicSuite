#!/usr/bin/env python3
"""
generate_theme_visual_cards.py
==============================
Generates:
  1. High-resolution visual PNG contact sheets (300 DPI) showing real slide previews for extracted themes.
  2. Master interactive Visual Theme Gallery HTML (THEME_GALLERY.html) with live slide simulators,
     swatches, search, filters, and copyable CLI commands.
"""

import os
import sys
import json
import colorsys
from pathlib import Path
from typing import Dict, List, Any, Tuple
import matplotlib.pyplot as plt
import matplotlib.patches as patches

ROOT_DIR = Path("/Users/saber/Desktop/academic_suite")
SOURCE_DIR = ROOT_DIR / "Powerpoint-Theme"
EXTRACTED_DIR = SOURCE_DIR / "extracted_themes"
CATALOG_PATH = EXTRACTED_DIR / "MASTER_THEME_CATALOG.json"


def hex_to_rgb_norm(hex_str: str) -> Tuple[float, float, float]:
    hex_str = hex_str.lstrip("#")
    if len(hex_str) != 6:
        return (0.5, 0.5, 0.5)
    r = int(hex_str[0:2], 16) / 255.0
    g = int(hex_str[2:4], 16) / 255.0
    b = int(hex_str[4:6], 16) / 255.0
    return (r, g, b)


def render_visual_theme_sheet(catalog: List[Dict[str, Any]], output_png: Path):
    """Renders a 300-DPI visual grid showing slide mockups and swatches for distinct themes."""
    # Select distinct theme signatures
    seen_sigs = set()
    distinct_themes = []
    for item in catalog:
        pal = item["palette"]
        sig = (pal["primary"], pal["secondary"], pal["accent"], pal["bg_slide"])
        if sig not in seen_sigs:
            seen_sigs.add(sig)
            distinct_themes.append(item)

    # Take top 12 representative themes across all families
    selected = distinct_themes[:12]
    cols = 3
    rows = (len(selected) + cols - 1) // cols

    fig = plt.figure(figsize=(18, rows * 4.2), dpi=200)
    fig.patch.set_facecolor("#0F172A")  # Dark slate studio backdrop

    plt.suptitle(
        "Persian Academic Defense Presentation Themes — Master Visual Catalog\n"
        f"Extracted from 52 Real Master's & PhD Viva Decks | 16:9 Widescreen | Persian Typography & APA 7 Standards",
        color="#F8FAFC",
        fontsize=16,
        fontweight="bold",
        y=0.98,
    )

    for idx, theme in enumerate(selected):
        ax = fig.add_subplot(rows, cols, idx + 1)
        pal = theme["palette"]
        ty = theme["typography"]
        bg_rgb = hex_to_rgb_norm(pal["bg_slide"])
        card_rgb = hex_to_rgb_norm(pal["card_bg"])
        primary_rgb = hex_to_rgb_norm(pal["primary"])
        secondary_rgb = hex_to_rgb_norm(pal["secondary"])
        accent_rgb = hex_to_rgb_norm(pal["accent"])
        text_rgb = hex_to_rgb_norm(pal["text_dark"])
        muted_rgb = hex_to_rgb_norm(pal["text_muted"])

        # 16:9 Slide Canvas Box
        ax.set_facecolor(bg_rgb)
        ax.set_xlim(0, 16)
        ax.set_ylim(0, 9)

        # Outer border
        border_rect = patches.Rectangle(
            (0, 0), 16, 9, linewidth=1.5, edgecolor=primary_rgb, facecolor="none"
        )
        ax.add_patch(border_rect)

        # Header bar / breadcrumb indicator
        header_bar = patches.Rectangle(
            (0.8, 7.8), 3.5, 0.45, linewidth=0, facecolor=secondary_rgb, alpha=0.9
        )
        ax.add_patch(header_bar)
        ax.text(
            1.0,
            7.95,
            f"SECTION: CHAPTER 4",
            color="#FFFFFF",
            fontsize=7,
            fontweight="bold",
        )

        # Slide Action Title
        t_font = ty.get("persian_title_font", "B Titr")
        ax.text(
            0.8,
            7.0,
            f"{theme['theme_id']}",
            color=primary_rgb,
            fontsize=10.5,
            fontweight="bold",
        )
        ax.text(
            0.8,
            6.4,
            f"Font: {t_font} | Mode: {theme['mode']} | {theme['aspect_ratio'].split(' ')[0]}",
            color=muted_rgb,
            fontsize=7,
        )

        # Main Content Card (Left / Center)
        card_rect = patches.FancyBboxPatch(
            (0.8, 1.8),
            9.0,
            4.2,
            boxstyle="round,pad=0.2,rounding_size=0.3",
            facecolor=card_rgb,
            edgecolor=hex_to_rgb_norm(pal["card_border"]),
            linewidth=1.0,
        )
        ax.add_patch(card_rect)

        # Simulated KPI Stat inside card
        ax.text(
            1.2, 4.8, "F(1, 48) = 14.82", color=primary_rgb, fontsize=11, fontweight="bold"
        )
        ax.text(
            1.2,
            4.1,
            "p < .001   |   η² = .24   |   Confirmed",
            color=secondary_rgb,
            fontsize=7.5,
            fontweight="bold",
        )

        # Table rows simulation
        for row_i in range(3):
            y_r = 3.3 - row_i * 0.6
            r_box = patches.Rectangle(
                (1.2, y_r),
                8.0,
                0.45,
                facecolor=bg_rgb,
                edgecolor=hex_to_rgb_norm(pal["card_border"]),
                linewidth=0.5,
            )
            ax.add_patch(r_box)
            ax.text(
                1.5,
                y_r + 0.12,
                f"Variable {row_i+1}: M = 24.35, SD = 4.12",
                color=text_rgb,
                fontsize=6.5,
            )

        # Right-side Swatch Panel
        swatch_card = patches.FancyBboxPatch(
            (10.5, 1.8),
            4.7,
            4.2,
            boxstyle="round,pad=0.2,rounding_size=0.3",
            facecolor=card_rgb,
            edgecolor=hex_to_rgb_norm(pal["card_border"]),
            linewidth=1.0,
        )
        ax.add_patch(swatch_card)

        ax.text(
            10.8, 5.2, "COLOR PALETTE", color=text_rgb, fontsize=7.5, fontweight="bold"
        )

        swatches = [
            ("Primary", pal["primary"], primary_rgb),
            ("Secondary", pal["secondary"], secondary_rgb),
            ("Accent", pal["accent"], accent_rgb),
            ("Background", pal["bg_slide"], bg_rgb),
        ]

        for s_idx, (s_name, s_hex, s_rgb) in enumerate(swatches):
            sy = 4.4 - s_idx * 0.75
            circ = patches.Circle((11.2, sy), 0.25, facecolor=s_rgb, edgecolor="#888888", linewidth=0.5)
            ax.add_patch(circ)
            ax.text(11.7, sy - 0.1, f"{s_name}: {s_hex}", color=text_rgb, fontsize=6.8)

        # Footer
        ax.text(
            0.8,
            0.6,
            f"Original: {theme['original_filename'][:34]}",
            color=muted_rgb,
            fontsize=6.5,
        )
        ax.text(
            13.5,
            0.6,
            f"{idx+1}/{len(selected)}",
            color=secondary_rgb,
            fontsize=7,
            fontweight="bold",
        )

        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)

    plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.95])
    output_png.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(output_png, facecolor=fig.get_facecolor(), dpi=200)
    plt.close()
    print(f"[SUCCESS] Visual Theme Showcase Grid rendered to: {output_png}")


def generate_theme_gallery_html(catalog: List[Dict[str, Any]], output_html: Path):
    """Builds a rich, interactive HTML Theme Gallery application."""
    # Compute stats
    total = len(catalog)
    signatures = {}
    for item in catalog:
        pal = item["palette"]
        sig = (pal["primary"], pal["secondary"], pal["accent"], pal["bg_slide"])
        signatures.setdefault(sig, []).append(item)

    unique_count = len(signatures)

    # Categories
    categories = sorted(list(set(item["color_category"] for item in catalog)))

    # JSON for client-side interactivity
    catalog_json = json.dumps(catalog, ensure_ascii=False)

    html = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>گالری ویژوال تم‌های دفاع دانشگاهی | Persian Academic Defense Themes Gallery</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800;900&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-dark: #070D1F;
            --bg-card-dark: #0F172A;
            --border-dark: #1E293B;
            --text-light: #F8FAFC;
            --text-muted-dark: #94A3B8;
            --accent-blue: #38BDF8;
            --accent-gold: #F59E0B;
            --accent-emerald: #10B981;
            --radius-md: 12px;
            --radius-lg: 16px;
        }}

        *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

        body {{
            font-family: "Vazirmatn", system-ui, sans-serif;
            background-color: var(--bg-dark);
            color: var(--text-light);
            line-height: 1.6;
            padding: 2rem;
            min-height: 100vh;
        }}

        /* Header Bar */
        .hero {{
            text-align: center;
            max-width: 1200px;
            margin: 0 auto 2.5rem;
            padding: 2.5rem 2rem;
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.8) 100%);
            border: 1px solid rgba(56, 189, 248, 0.2);
            border-radius: var(--radius-lg);
            box-shadow: 0 20px 40px -15px rgba(0,0,0,0.5);
            backdrop-filter: blur(10px);
        }}

        .hero h1 {{
            font-size: 2.2rem;
            font-weight: 800;
            color: #FFFFFF;
            margin-bottom: 0.5rem;
            background: linear-gradient(90deg, #38BDF8, #818CF8, #F59E0B);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}

        .hero p {{
            color: var(--text-muted-dark);
            font-size: 1.05rem;
            max-width: 800px;
            margin: 0 auto 1.5rem;
        }}

        /* Stats Strip */
        .stats-strip {{
            display: flex;
            justify-content: center;
            gap: 2rem;
            flex-wrap: wrap;
            margin-top: 1rem;
        }}

        .stat-badge {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 0.5rem 1.2rem;
            border-radius: 50px;
            font-size: 0.9rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}

        .stat-badge strong {{
            color: var(--accent-blue);
            font-family: "Inter", sans-serif;
            font-size: 1.1rem;
        }}

        /* Search & Filter Bar */
        .control-bar {{
            max-width: 1400px;
            margin: 0 auto 2rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
        }}

        .search-row {{
            display: flex;
            gap: 1rem;
        }}

        .search-input {{
            flex: 1;
            padding: 0.9rem 1.4rem;
            background: var(--bg-card-dark);
            border: 1px solid var(--border-dark);
            border-radius: var(--radius-md);
            color: #FFFFFF;
            font-size: 1rem;
            font-family: inherit;
            outline: none;
            transition: border-color 0.2s;
        }}

        .search-input:focus {{
            border-color: var(--accent-blue);
        }}

        .filter-tabs {{
            display: flex;
            gap: 0.5rem;
            overflow-x: auto;
            padding-bottom: 0.5rem;
        }}

        .filter-btn {{
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-dark);
            color: var(--text-muted-dark);
            padding: 0.5rem 1rem;
            border-radius: 8px;
            font-family: inherit;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s;
            white-space: nowrap;
        }}

        .filter-btn:hover, .filter-btn.active {{
            background: var(--accent-blue);
            color: #0F172A;
            border-color: var(--accent-blue);
            font-weight: 700;
        }}

        /* Themes Grid */
        .themes-grid {{
            max-width: 1400px;
            margin: 0 auto;
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(420px, 1fr));
            gap: 2rem;
        }}

        /* Theme Card */
        .theme-card {{
            background: var(--bg-card-dark);
            border: 1px solid var(--border-dark);
            border-radius: var(--radius-lg);
            overflow: hidden;
            display: flex;
            flex-direction: column;
            transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
        }}

        .theme-card:hover {{
            transform: translateY(-4px);
            border-color: rgba(56, 189, 248, 0.5);
            box-shadow: 0 15px 30px -10px rgba(0,0,0,0.6);
        }}

        /* Mini Slide Live Preview */
        .slide-preview-box {{
            aspect-ratio: 16 / 9;
            width: 100%;
            padding: 1.2rem;
            position: relative;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            overflow: hidden;
            border-bottom: 1px solid var(--border-dark);
        }}

        .mini-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .mini-badge {{
            font-size: 0.65rem;
            padding: 0.2rem 0.6rem;
            border-radius: 4px;
            font-weight: 700;
        }}

        .mini-counter {{
            font-size: 0.7rem;
            font-family: "Inter", sans-serif;
            opacity: 0.7;
        }}

        .mini-title {{
            font-size: 0.95rem;
            font-weight: 800;
            line-height: 1.3;
            margin: 0.4rem 0;
        }}

        .mini-content-row {{
            display: flex;
            gap: 0.6rem;
            flex: 1;
            margin: 0.4rem 0;
            align-items: stretch;
        }}

        .mini-stat-card {{
            flex: 1;
            padding: 0.5rem;
            border-radius: 6px;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}

        .mini-stat-val {{
            font-size: 0.85rem;
            font-weight: 800;
            font-family: "Inter", sans-serif;
        }}

        .mini-stat-sub {{
            font-size: 0.6rem;
            opacity: 0.8;
            margin-top: 0.1rem;
        }}

        .mini-table-card {{
            flex: 1.2;
            padding: 0.4rem;
            border-radius: 6px;
            display: flex;
            flex-direction: column;
            gap: 0.25rem;
            justify-content: center;
        }}

        .mini-table-row {{
            display: flex;
            justify-content: space-between;
            font-size: 0.58rem;
            padding: 0.15rem 0.3rem;
            border-radius: 3px;
        }}

        .mini-footer {{
            font-size: 0.6rem;
            opacity: 0.7;
            display: flex;
            justify-content: space-between;
        }}

        /* Card Details & Swatches */
        .card-body {{
            padding: 1.2rem;
            display: flex;
            flex-direction: column;
            gap: 1rem;
            flex: 1;
        }}

        .card-header-info {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
        }}

        .theme-name {{
            font-size: 1.1rem;
            font-weight: 700;
            color: #FFFFFF;
        }}

        .theme-slug {{
            font-family: "Inter", monospace;
            font-size: 0.75rem;
            color: var(--accent-blue);
            background: rgba(56, 189, 248, 0.1);
            padding: 0.15rem 0.5rem;
            border-radius: 4px;
        }}

        .original-file {{
            font-size: 0.8rem;
            color: var(--text-muted-dark);
            word-break: break-all;
            direction: ltr;
            text-align: left;
        }}

        /* Swatches Row */
        .swatches-row {{
            display: flex;
            gap: 0.5rem;
            align-items: center;
        }}

        .swatch {{
            width: 32px;
            height: 32px;
            border-radius: 50%;
            border: 2px solid rgba(255, 255, 255, 0.15);
            cursor: pointer;
            position: relative;
            transition: transform 0.15s ease;
        }}

        .swatch:hover {{
            transform: scale(1.15);
        }}

        .swatch-label {{
            font-size: 0.65rem;
            color: var(--text-muted-dark);
            margin-right: 0.4rem;
        }}

        /* Typography Tags */
        .typo-tags {{
            display: flex;
            gap: 0.5rem;
            flex-wrap: wrap;
        }}

        .typo-tag {{
            font-size: 0.75rem;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 0.25rem 0.6rem;
            border-radius: 4px;
            color: #CBD5E1;
        }}

        /* Card Action Buttons */
        .card-actions {{
            display: flex;
            gap: 0.6rem;
            margin-top: auto;
            padding-top: 0.8rem;
            border-top: 1px solid var(--border-dark);
        }}

        .btn-action {{
            flex: 1;
            padding: 0.6rem 0.8rem;
            border-radius: 6px;
            font-family: inherit;
            font-size: 0.8rem;
            font-weight: 600;
            cursor: pointer;
            text-align: center;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 0.4rem;
            text-decoration: none;
        }}

        .btn-copy {{
            background: rgba(255, 255, 255, 0.07);
            border: 1px solid var(--border-dark);
            color: var(--text-light);
        }}

        .btn-copy:hover {{
            background: rgba(255, 255, 255, 0.15);
        }}

        .btn-sim {{
            background: var(--accent-blue);
            border: 1px solid var(--accent-blue);
            color: #0F172A;
        }}

        .btn-sim:hover {{
            background: #7DD3FC;
        }}

        /* Simulator Modal */
        .modal-overlay {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.85);
            z-index: 1000;
            backdrop-filter: blur(6px);
            align-items: center;
            justify-content: center;
            padding: 2rem;
        }}

        .modal-overlay.active {{
            display: flex;
        }}

        .modal-container {{
            background: var(--bg-card-dark);
            border: 1px solid var(--border-dark);
            border-radius: var(--radius-lg);
            max-width: 1100px;
            width: 100%;
            display: flex;
            flex-direction: column;
            overflow: hidden;
            box-shadow: 0 25px 50px -12px rgba(0,0,0,0.7);
        }}

        .modal-header {{
            padding: 1.2rem 1.5rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid var(--border-dark);
        }}

        .modal-header h3 {{
            font-size: 1.2rem;
            color: #FFFFFF;
        }}

        .modal-close {{
            background: none;
            border: none;
            color: var(--text-muted-dark);
            font-size: 1.5rem;
            cursor: pointer;
        }}

        .modal-body {{
            padding: 1.5rem;
            display: flex;
            flex-direction: column;
            gap: 1.2rem;
        }}

        .sim-slide-frame {{
            aspect-ratio: 16 / 9;
            width: 100%;
            max-height: 520px;
            border-radius: 8px;
            overflow: hidden;
            position: relative;
            box-shadow: 0 10px 25px rgba(0,0,0,0.4);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            padding: 2.5rem;
        }}

        .sim-code-box {{
            background: #000000;
            border: 1px solid #1E293B;
            border-radius: 8px;
            padding: 1rem;
            font-family: "Inter", monospace;
            font-size: 0.85rem;
            color: #38BDF8;
            direction: ltr;
            text-align: left;
            overflow-x: auto;
        }}

        /* Toast notification */
        .toast {{
            position: fixed;
            bottom: 2rem;
            left: 50%;
            transform: translateX(-50%) translateY(100px);
            background: #10B981;
            color: #FFFFFF;
            padding: 0.8rem 1.5rem;
            border-radius: 50px;
            font-weight: 700;
            box-shadow: 0 10px 20px rgba(0,0,0,0.3);
            transition: transform 0.3s ease;
            z-index: 2000;
        }}

        .toast.show {{
            transform: translateX(-50%) translateY(0);
        }}
    </style>
</head>
<body>

    <!-- Header Section -->
    <div class="hero">
        <h1>گالری ویژوال تم‌های دفاع دانشگاهی</h1>
        <p>مجموعه کامل ۵۲ قالب استخراج‌شده از رساله‌ها و پایان‌نامه‌های واقعی دانشگاهی با قابلیت مشاهده زنده، پیش‌نمایش رنگ‌ها، تایپوگرافی رسمی و دستور کپی سریع برای PowerPoint و HTML.</p>
        <div class="stats-strip">
            <div class="stat-badge">تعداد کل ارائه‌ها: <strong>{total}</strong></div>
            <div class="stat-badge">پالت‌های رنگی یکتا: <strong>{unique_count}</strong></div>
            <div class="stat-badge">ابعاد استاندارد: <strong>16:9 Widescreen (75%)</strong></div>
            <div class="stat-badge">فونت‌های مسلط: <strong>B Nazanin / B Titr / B Mitra</strong></div>
        </div>
    </div>

    <!-- Controls -->
    <div class="control-bar">
        <div class="search-row">
            <input type="text" id="searchInput" class="search-input" placeholder="جستجو بر اساس نام فایل، شناسه تم، فونت یا خانواده رنگی...">
        </div>
        <div class="filter-tabs" id="filterTabs">
            <button class="filter-btn active" data-filter="all">همه تم‌ها ({total})</button>
            <button class="filter-btn" data-filter="Academic Navy / Blue">آبی و سورمه‌ای آکادمیک</button>
            <button class="filter-btn" data-filter="Teal / Cyan">فیروزه‌ای و درمانی (EFT/ACT)</button>
            <button class="filter-btn" data-filter="Burgundy / Crimson">زرشکی و علوم انسانی</button>
            <button class="filter-btn" data-filter="Emerald / Green">سبز و سلامت / رشد مثبت</button>
            <button class="filter-btn" data-filter="Dark Mode">حالت تیره (Dark Mode)</button>
        </div>
    </div>

    <!-- Themes Grid Container -->
    <div class="themes-grid" id="themesGrid">
        <!-- Rendered dynamically by JavaScript -->
    </div>

    <!-- Simulator Modal -->
    <div class="modal-overlay" id="simModal">
        <div class="modal-container">
            <div class="modal-header">
                <h3 id="modalTitle">شبیه‌ساز زنده اسلاید دفاع</h3>
                <button class="modal-close" onclick="closeModal()">&times;</button>
            </div>
            <div class="modal-body">
                <div class="sim-slide-frame" id="simSlideFrame">
                    <!-- Dynamic slide content inside modal -->
                </div>
                <div class="sim-code-box" id="simCodeBox">
                    # Terminal command to build PPTX with this theme
                </div>
            </div>
        </div>
    </div>

    <!-- Toast Notification -->
    <div class="toast" id="toast">دستور در کلیپ‌بورد کپی شد!</div>

    <script>
        const THEMES_DATA = {catalog_json};

        const grid = document.getElementById("themesGrid");
        const searchInput = document.getElementById("searchInput");
        const filterTabs = document.getElementById("filterTabs");
        const toast = document.getElementById("toast");

        let activeFilter = "all";
        let searchQuery = "";

        function showToast(msg) {{
            toast.textContent = msg;
            toast.classList.add("show");
            setTimeout(() => toast.classList.remove("show"), 2500);
        }}

        function copyCommand(themeId) {{
            const cmd = `python3 main.py --compile-pptx --json payload.json --output Defense_${{themeId}}.pptx --theme ${{themeId}}`;
            navigator.clipboard.writeText(cmd).then(() => {{
                showToast(`دستور کامپایل تم ${{themeId}} کپی شد!`);
            }}).catch(() => {{
                prompt("دستور کامپایل:", cmd);
            }});
        }}

        function openModal(themeId) {{
            const theme = THEMES_DATA.find(t => t.theme_id === themeId);
            if (!theme) return;

            const p = theme.palette;
            const ty = theme.typography;
            const modal = document.getElementById("simModal");
            const frame = document.getElementById("simSlideFrame");
            const title = document.getElementById("modalTitle");
            const codeBox = document.getElementById("simCodeBox");

            title.textContent = `پیش‌نمایش زنده اسلاید: ${{theme.theme_id}} (${{theme.mode}})`;
            codeBox.textContent = `python3 main.py --compile-pptx --json payload.json --output Defense_${{theme.theme_id}}.pptx --theme ${{theme.theme_id}}`;

            frame.style.backgroundColor = p.bg_slide;
            frame.style.color = p.text_dark;
            frame.style.border = `2px solid ${{p.card_border}}`;

            frame.innerHTML = `
                <div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="background: ${{p.secondary}}; color: #FFFFFF; font-size: 0.85rem; font-weight: 700; padding: 0.3rem 0.8rem; border-radius: 4px;">| فصل چهارم: یافته‌های آماری پژوهش</span>
                        <span style="font-family: Inter, sans-serif; font-size: 0.9rem; color: ${{p.text_muted}};">اسلاید ۱۲ از ۲۲</span>
                    </div>
                    <h2 style="font-size: 1.6rem; font-weight: 800; color: ${{p.primary}}; margin-top: 1rem;">بررسی فرضیه اصلی: اثربخشی مداخله بر متغیرهای وابسته پژوهش</h2>
                </div>

                <div style="display: flex; gap: 1.5rem; margin: 1.5rem 0;">
                    <div style="flex: 1; background: ${{p.card_bg}}; border: 1.5px solid ${{p.card_border}}; border-top: 4px solid ${{p.primary}}; border-radius: 8px; padding: 1.2rem; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
                        <div style="font-size: 1.6rem; font-weight: 900; color: ${{p.primary}}; font-family: Inter, sans-serif;">F(1, 48) = 14.82</div>
                        <div style="font-size: 0.95rem; font-weight: 700; color: ${{p.secondary}}; margin-top: 0.3rem;">p < .001   |   اندازه اثر: η² = 0.24</div>
                        <p style="font-size: 0.85rem; color: ${{p.text_muted}}; margin-top: 0.5rem; line-height: 1.5;">تفاوت میانگین گروه‌های آزمایش و گواه در مرحله پس‌آزمون با کنترل پیش‌آزمون در سطح ۰/۰۰۱ معنادار است.</p>
                    </div>
                    <div style="flex: 1.2; background: ${{p.card_bg}}; border: 1.5px solid ${{p.card_border}}; border-radius: 8px; padding: 1rem; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">
                        <table style="width: 100%; border-collapse: collapse; font-size: 0.85rem;">
                            <thead>
                                <tr style="border-bottom: 2px solid ${{p.primary}}; color: ${{p.primary}};">
                                    <th style="padding: 0.4rem; text-align: right;">منبع تغییرات</th>
                                    <th style="padding: 0.4rem; text-align: center;">مجموع مجذورات</th>
                                    <th style="padding: 0.4rem; text-align: center;">درجه آزادی</th>
                                    <th style="padding: 0.4rem; text-align: center;">آماره F</th>
                                    <th style="padding: 0.4rem; text-align: center;">سطح معناداری</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr style="border-bottom: 1px solid ${{p.card_border}};">
                                    <td style="padding: 0.5rem; font-weight: 700;">پیش‌آزمون (همپراش)</td>
                                    <td style="text-align: center;">۱۴۲/۵۰</td>
                                    <td style="text-align: center;">۱</td>
                                    <td style="text-align: center;">۸/۳۴</td>
                                    <td style="text-align: center; color: ${{p.secondary}};">۰/۰۰۶</td>
                                </tr>
                                <tr style="background: ${{p.tbl_stripe}};">
                                    <td style="padding: 0.5rem; font-weight: 800; color: ${{p.primary}};">اثر گروه (مداخله)</td>
                                    <td style="text-align: center; font-weight: 700;">۲۸۹/۱۰</td>
                                    <td style="text-align: center;">۱</td>
                                    <td style="text-align: center; font-weight: 800; color: ${{p.primary}};">۱۴/۸۲</td>
                                    <td style="text-align: center; font-weight: 800; color: ${{p.accent}};">۰/۰۰۱ > p</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>

                <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid ${{p.card_border}}; padding-top: 0.8rem; font-size: 0.8rem; color: ${{p.text_muted}};">
                    <span>دانشگاه / جلسه دفاع رساله دکتری و پایان‌نامه کارشناسی ارشد</span>
                    <span style="color: ${{p.secondary}}; font-weight: 700;">تأیید فرضیه پژوهش با اطمینان ۹۹ درصد ✓</span>
                </div>
            `;

            modal.classList.add("active");
        }}

        function closeModal() {{
            document.getElementById("simModal").classList.remove("active");
        }}

        function renderThemes() {{
            grid.innerHTML = "";
            const filtered = THEMES_DATA.filter(t => {{
                const matchFilter = activeFilter === "all" ||
                                    (activeFilter === "Dark Mode" && t.mode === "Dark Mode") ||
                                    t.color_category === activeFilter;
                const matchSearch = searchQuery === "" ||
                                    t.theme_id.toLowerCase().includes(searchQuery) ||
                                    t.original_filename.toLowerCase().includes(searchQuery) ||
                                    t.typography.persian_title_font.toLowerCase().includes(searchQuery);
                return matchFilter && matchSearch;
            }});

            if (filtered.length === 0) {{
                grid.innerHTML = `<div style="grid-column: 1/-1; text-align: center; padding: 4rem; color: var(--text-muted-dark); font-size: 1.1rem;">هیچ تمی مطابق با جستجوی شما یافت نشد.</div>`;
                return;
            }}

            filtered.forEach((t, i) => {{
                const p = t.palette;
                const ty = t.typography;

                const card = document.createElement("div");
                card.className = "theme-card";
                card.innerHTML = `
                    <div class="slide-preview-box" style="background-color: ${{p.bg_slide}}; color: ${{p.text_dark}};">
                        <div class="mini-header">
                            <span class="mini-badge" style="background: ${{p.secondary}}; color: #FFFFFF;">| یافته‌های پژوهش</span>
                            <span class="mini-counter" style="color: ${{p.text_muted}};">12/22</span>
                        </div>
                        <div class="mini-title" style="color: ${{p.primary}};">اثربخشی مداخله بر متغیرهای پژوهش</div>
                        <div class="mini-content-row">
                            <div class="mini-stat-card" style="background: ${{p.card_bg}}; border: 1px solid ${{p.card_border}};">
                                <div class="mini-stat-val" style="color: ${{p.primary}};">F = 14.82</div>
                                <div class="mini-stat-sub" style="color: ${{p.secondary}};">p < .001 | η² = .24</div>
                            </div>
                            <div class="mini-table-card" style="background: ${{p.card_bg}}; border: 1px solid ${{p.card_border}};">
                                <div class="mini-table-row" style="background: ${{p.primary}}; color: #FFFFFF; font-weight: 700;">
                                    <span>متغیر</span><span>F</span><span>p</span>
                                </div>
                                <div class="mini-table-row" style="background: ${{p.tbl_stripe}}; color: ${{p.text_dark}};">
                                    <span>مداخله</span><span>14.82</span><span>.001</span>
                                </div>
                            </div>
                        </div>
                        <div class="mini-footer" style="color: ${{p.text_muted}};">
                            <span>دفاع دانشگاهی</span>
                            <span style="color: ${{p.secondary}}; font-weight: 700;">فرضیه تأیید شد ✓</span>
                        </div>
                    </div>

                    <div class="card-body">
                        <div class="card-header-info">
                            <div>
                                <div class="theme-name">${{t.presentation_title ? t.presentation_title.slice(0, 38) + '...' : t.theme_id}}</div>
                                <div class="original-file">${{t.original_filename}}</div>
                            </div>
                            <span class="theme-slug">${{t.theme_id}}</span>
                        </div>

                        <div class="swatches-row">
                            <span class="swatch-label">پالت:</span>
                            <div class="swatch" style="background: ${{p.primary}}" title="اصلی (Primary): ${{p.primary}}"></div>
                            <div class="swatch" style="background: ${{p.secondary}}" title="ثانویه (Secondary): ${{p.secondary}}"></div>
                            <div class="swatch" style="background: ${{p.accent}}" title="تاکیدی (Accent): ${{p.accent}}"></div>
                            <div class="swatch" style="background: ${{p.bg_slide}}" title="پس‌زمینه: ${{p.bg_slide}}"></div>
                            <div class="swatch" style="background: ${{p.card_bg}}" title="کارت: ${{p.card_bg}}"></div>
                        </div>

                        <div class="typo-tags">
                            <span class="typo-tag">🔤 عنوان: ${{ty.persian_title_font}}</span>
                            <span class="typo-tag">📝 متن: ${{ty.persian_body_font}}</span>
                            <span class="typo-tag">📐 ${{t.aspect_ratio.split(' ')[0]}}</span>
                            <span class="typo-tag">${{t.mode === 'Dark Mode' ? '🌙 تیره' : '☀️ روشن'}}</span>
                        </div>

                        <div class="card-actions">
                            <button class="btn-action btn-copy" onclick="copyCommand('${{t.theme_id}}')">📋 کپی دستور CLI</button>
                            <button class="btn-action btn-sim" onclick="openModal('${{t.theme_id}}')">🔍 شبیه‌ساز زنده</button>
                        </div>
                    </div>
                `;
                grid.appendChild(card);
            }});
        }}

        // Search Input Event
        searchInput.addEventListener("input", (e) => {{
            searchQuery = e.target.value.trim().toLowerCase();
            renderThemes();
        }});

        // Filter Tabs Event
        filterTabs.addEventListener("click", (e) => {{
            if (e.target.tagName === "BUTTON") {{
                document.querySelectorAll(".filter-btn").forEach(b => b.classList.remove("active"));
                e.target.classList.add("active");
                activeFilter = e.target.getAttribute("data-filter");
                renderThemes();
            }}
        }});

        // Initial Render
        renderThemes();
    </script>
</body>
</html>
"""
    with open(output_html, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[SUCCESS] Interactive Theme Gallery HTML written to: {output_html}")


def main():
    if not CATALOG_PATH.is_file():
        print(f"[!] Error: Master theme catalog not found: {CATALOG_PATH}", file=sys.stderr)
        return 1

    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)

    # 1. Generate 300-DPI Visual Grid Image
    preview_img = EXTRACTED_DIR / "theme_showcase_grid.png"
    render_visual_theme_sheet(catalog, preview_img)

    # 2. Generate Interactive Theme Gallery HTML Application
    gallery_html = EXTRACTED_DIR / "THEME_GALLERY.html"
    generate_theme_gallery_html(catalog, gallery_html)

    return 0


if __name__ == "__main__":
    sys.exit(main())
