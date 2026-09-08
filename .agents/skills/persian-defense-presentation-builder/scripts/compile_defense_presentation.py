#!/usr/bin/env python3
"""
Master Persian Academic Thesis Defense Presentation Compiler (Executive Pro Edition)
===================================================================================
Author: Saber Ghaderi
Repository: GhaderiSaber/AcademicSuite
Description:
    Compiles publication-grade, defense-ready PowerPoint presentations (.pptx)
    for Iranian Master's and PhD candidates. Built strictly following high-end
    executive design standards (McKinsey/Apple/Swiss-editorial style):
    - Zero amateur emoji clutter.
    - Native Right-to-Left (RTL) OpenXML DrawingML formatting.
    - Iranian typography (B Titr for headlines, B Nazanin for body, Times New Roman for stats).
    - Executive Dark Title and Closing slides in Midnight Obsidian (#0A1128) & Champagne Gold.
    - Clean editorial content slides on Soft Platinum (#F8FAFC) canvas with elevated surfaces.
    - Asymmetric Hero Split layouts for 300-DPI scientific figures and clinical photos.
    - Executive KPI Goodness-of-Fit Dashboards with standard psychometric thresholds.
    - Publication-grade APA 7 data tables with zero vertical borders.
    - Full candidate oral defense Speaker Notes on 100% of slides.
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Any, Optional

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls

# ---------------------------------------------------------------------------
# Visual Themes & Executive Design Tokens (16:9 Widescreen)
# ---------------------------------------------------------------------------
PALETTES = {
    "academic_navy": {
        "primary": RGBColor(15, 23, 42),          # Midnight Slate #0F172A
        "secondary": RGBColor(30, 58, 138),       # Royal Academic Sapphire #1E3A8A
        "accent": RGBColor(197, 160, 89),         # Champagne Gold #C5A059
        "accent_light": RGBColor(254, 243, 199),  # Soft Gold Tint #FEF3C7
        "accent_dark": RGBColor(180, 83, 9),      # Deep Warm Amber #B45309
        "emerald": RGBColor(4, 120, 87),          # Forest Emerald #047857
        "emerald_light": RGBColor(236, 253, 245), # Soft Mint Tint #ECFDF5
        "bg_slide": RGBColor(248, 250, 252),      # Soft Platinum #F8FAFC
        "card_bg": RGBColor(255, 255, 255),       # Pure White #FFFFFF
        "card_border": RGBColor(226, 232, 240),   # Hairline Slate 200 #E2E8F0
        "card_border_gold": RGBColor(197, 160, 89),
        "text_dark": RGBColor(15, 23, 42),        # Obsidian #0F172A
        "text_body": RGBColor(51, 65, 85),        # Slate 700 #334155
        "text_muted": RGBColor(100, 116, 139),    # Slate 500 #64748B
        "text_light": RGBColor(255, 255, 255),    # Crisp White #FFFFFF
        "tbl_header": RGBColor(15, 23, 42),       # Dark Slate #0F172A
        "tbl_stripe": RGBColor(248, 250, 252),    # Platinum #F8FAFC
        "badge_bg": RGBColor(239, 246, 255),      # Soft Blue Tint #EFF6FF
        "badge_border": RGBColor(219, 234, 254),  # Blue 100 #DBEAFE
        "badge_text": RGBColor(29, 78, 216),      # Sapphire #1D4ED8
        "cover_bg": RGBColor(10, 17, 40),         # Midnight Obsidian #0A1128
        "cover_card": RGBColor(17, 28, 56),       # Translucent Slate #111C38
        "cover_border": RGBColor(36, 51, 86)      # Slate Hairline #243356
    },
    "emerald_slate": {
        "primary": RGBColor(19, 78, 74),
        "secondary": RGBColor(15, 118, 110),
        "accent": RGBColor(5, 150, 105),
        "accent_light": RGBColor(209, 250, 229),
        "accent_dark": RGBColor(4, 120, 87),
        "emerald": RGBColor(5, 150, 105),
        "emerald_light": RGBColor(209, 250, 229),
        "bg_slide": RGBColor(240, 253, 244),
        "card_bg": RGBColor(255, 255, 255),
        "card_border": RGBColor(209, 250, 229),
        "card_border_gold": RGBColor(5, 150, 105),
        "text_dark": RGBColor(19, 42, 31),
        "text_body": RGBColor(51, 65, 85),
        "text_muted": RGBColor(75, 85, 99),
        "text_light": RGBColor(255, 255, 255),
        "tbl_header": RGBColor(19, 78, 74),
        "tbl_stripe": RGBColor(236, 253, 245),
        "badge_bg": RGBColor(236, 253, 245),
        "badge_border": RGBColor(167, 243, 208),
        "badge_text": RGBColor(4, 120, 87),
        "cover_bg": RGBColor(12, 35, 33),
        "cover_card": RGBColor(19, 52, 49),
        "cover_border": RGBColor(30, 75, 71)
    },
    "royal_burgundy": {
        "primary": RGBColor(74, 14, 23),
        "secondary": RGBColor(136, 19, 55),
        "accent": RGBColor(197, 160, 89),
        "accent_light": RGBColor(254, 243, 199),
        "accent_dark": RGBColor(180, 83, 9),
        "emerald": RGBColor(5, 150, 105),
        "emerald_light": RGBColor(209, 250, 229),
        "bg_slide": RGBColor(255, 251, 235),
        "card_bg": RGBColor(255, 255, 255),
        "card_border": RGBColor(254, 215, 170),
        "card_border_gold": RGBColor(197, 160, 89),
        "text_dark": RGBColor(31, 41, 55),
        "text_body": RGBColor(51, 65, 85),
        "text_muted": RGBColor(107, 114, 128),
        "text_light": RGBColor(255, 255, 255),
        "tbl_header": RGBColor(74, 14, 23),
        "tbl_stripe": RGBColor(254, 243, 199),
        "badge_bg": RGBColor(255, 241, 242),
        "badge_border": RGBColor(254, 205, 211),
        "badge_text": RGBColor(159, 18, 57),
        "cover_bg": RGBColor(40, 8, 14),
        "cover_card": RGBColor(60, 12, 21),
        "cover_border": RGBColor(85, 20, 32)
    }
}

FONT_TITR = "B Titr"
FONT_NAZANIN = "B Nazanin"
FONT_ENG = "Times New Roman"

# ---------------------------------------------------------------------------
# OpenXML DrawingML Formatting Helpers (Native RTL & Font Bindings)
# ---------------------------------------------------------------------------
def apply_p_rtl(p, align=PP_ALIGN.RIGHT):
    """Enforce Right-to-Left and alignment in DrawingML."""
    p.alignment = align
    pPr = p._p.get_or_add_pPr()
    pPr.set("rtl", "1")
    if align == PP_ALIGN.RIGHT:
        pPr.set("algn", "r")
    elif align == PP_ALIGN.CENTER:
        pPr.set("algn", "ctr")
    elif align == PP_ALIGN.LEFT:
        pPr.set("algn", "l")

def set_run_font(run, text: str, font_name: str, size_pt: float, bold: bool = False, color_rgb: Optional[RGBColor] = None):
    """Set text, font size, bold, color and inject DrawingML complex script typeface."""
    run.text = text
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    if color_rgb:
        run.font.color.rgb = color_rgb

    # Inject <a:cs typeface="..."/> into <a:rPr> to guarantee Iranian font fidelity in PowerPoint
    rPr = run._r.get_or_add_rPr()
    cs = rPr.find(f"{{{nsdecls('a').split('=')[1].strip('\"')}}}cs")
    if cs is None:
        cs = parse_xml(f'<a:cs {nsdecls("a")} typeface="{font_name}"/>')
        rPr.append(cs)
    else:
        cs.set("typeface", font_name)

def attach_speaker_notes(slide, notes_text: str):
    """Attach Persian oral defense speaker notes with RTL typography."""
    if not notes_text:
        return
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.word_wrap = True
    
    paragraphs = [p.strip() for p in notes_text.split("\n") if p.strip()]
    for i, p_str in enumerate(paragraphs):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        
        apply_p_rtl(p, PP_ALIGN.RIGHT)
        p.space_after = Pt(4)
        run = p.add_run()
        set_run_font(run, p_str, FONT_NAZANIN, 12, bold=False, color_rgb=RGBColor(30, 41, 59))

def draw_header_banner(slide, category: str, title: str, palette: Dict[str, Any], slide_num: int = 0, total_slides: int = 28):
    """
    Render consistent, ultra-clean Swiss/Editorial slide header.
    Features an overline category kicker, commanding slide title, subtle hairline, and footer metadata.
    """
    # Header Textbox (Right-aligned Persian title hierarchy)
    header_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.42), Inches(11.733), Inches(0.95))
    tf_h = header_box.text_frame
    tf_h.word_wrap = True
    tf_h.margin_top = Inches(0)
    tf_h.margin_right = Inches(0)
    tf_h.margin_left = Inches(0)
    tf_h.margin_bottom = Inches(0)

    # Category Overline Kicker
    if category:
        p_c = tf_h.paragraphs[0]
        apply_p_rtl(p_c, PP_ALIGN.RIGHT)
        r_c = p_c.add_run()
        clean_cat = category.replace("📌", "").replace("•", "—").strip()
        set_run_font(r_c, clean_cat, FONT_TITR, 10.5, bold=True, color_rgb=palette["secondary"])
        
        p_t = tf_h.add_paragraph()
    else:
        p_t = tf_h.paragraphs[0]

    # Slide Headline
    apply_p_rtl(p_t, PP_ALIGN.RIGHT)
    p_t.space_before = Pt(2)
    r_t = p_t.add_run()
    clean_title = title.replace("📌", "").replace("💡", "").strip()
    set_run_font(r_t, clean_title, FONT_TITR, 21.5, bold=True, color_rgb=palette["primary"])

    # Ultra-subtle Horizontal Hairline Rule
    sep = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.38), Inches(11.733), Pt(0.75)
    )
    sep.fill.solid()
    sep.fill.fore_color.rgb = palette["card_border"]
    sep.line.fill.background()

    # Refined Bottom Footer Metadata (Right: University & Candidate, Left: Slide Index)
    if slide_num > 0:
        footer_sep = slide.shapes.add_shape(
            MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(7.02), Inches(11.733), Pt(0.5)
        )
        footer_sep.fill.solid()
        footer_sep.fill.fore_color.rgb = palette["card_border"]
        footer_sep.line.fill.background()

        footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.06), Inches(11.733), Inches(0.32))
        tf_f = footer_box.text_frame
        tf_f.margin_top = Inches(0)
        tf_f.margin_right = Inches(0)
        tf_f.margin_left = Inches(0)
        p_f = tf_f.paragraphs[0]
        apply_p_rtl(p_f, PP_ALIGN.RIGHT)
        r_fn = p_f.add_run()
        set_run_font(r_fn, f"دانشگاه آزاد اسلامی واحد کاشان  |  جلسه دفاع پایان‌نامه کارشناسی ارشد مرضیه سینائی  |  اسلاید {slide_num} از {total_slides}", FONT_NAZANIN, 9.5, bold=False, color_rgb=palette["text_muted"])

def draw_callout_banner(slide, text: str, palette: Dict[str, Any], left: Inches, top: Inches, width: Inches, height: Inches):
    """
    Render an executive Key Takeaway callout banner.
    Solid surface with a 3.5pt vertical accent bar and clean typography.
    """
    # Base Box
    box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    box.fill.solid()
    box.fill.fore_color.rgb = palette["card_bg"]
    box.line.color.rgb = palette["card_border"]
    box.line.width = Pt(0.75)

    # Right Vertical Accent Bar (guides eye to Persian text start)
    acc = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left + width - Inches(0.06), top, Inches(0.06), height)
    acc.fill.solid()
    acc.fill.fore_color.rgb = palette["accent"]
    acc.line.fill.background()

    tf = box.text_frame
    tf.word_wrap = True
    tf.margin_right = Inches(0.25)
    tf.margin_left = Inches(0.25)
    tf.margin_top = Inches(0.12)
    tf.margin_bottom = Inches(0.1)

    p = tf.paragraphs[0]
    apply_p_rtl(p, PP_ALIGN.RIGHT)
    r_icon = p.add_run()
    set_run_font(r_icon, "پیام کلیدی پژوهش: ", FONT_TITR, 11.5, bold=True, color_rgb=palette["secondary"])
    r_text = p.add_run()
    clean_text = text.replace("💡", "").strip()
    set_run_font(r_text, clean_text, FONT_NAZANIN, 12, bold=False, color_rgb=palette["text_dark"])

# ---------------------------------------------------------------------------
# Slide Layout Builders
# ---------------------------------------------------------------------------
def build_cover_slide(prs: Presentation, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, Any]):
    """
    Slide 1: Executive Dark Title Slide in Midnight Obsidian (#0A1128) & Champagne Gold.
    Dignified, commanding, and publication-grade.
    """
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Full Midnight Obsidian Canvas
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = palette["cover_bg"]
    bg.line.fill.background()

    # Subtle Architectural Hairline Accent Frame
    frame = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(0.5), Inches(12.333), Inches(6.5))
    frame.fill.background()
    frame.line.color.rgb = palette["accent"]
    frame.line.width = Pt(0.75)

    # University & Department Header
    uni_box = slide.shapes.add_textbox(Inches(1.0), Inches(0.85), Inches(11.333), Inches(0.85))
    tf_u = uni_box.text_frame
    tf_u.word_wrap = True
    
    p_u1 = tf_u.paragraphs[0]
    apply_p_rtl(p_u1, PP_ALIGN.CENTER)
    r_u1 = p_u1.add_run()
    uni_title = f"{meta.get('university', 'دانشگاه آزاد اسلامی')}  |  {meta.get('faculty', 'واحد کاشان • دانشکده علوم انسانی')}"
    set_run_font(r_u1, uni_title, FONT_TITR, 12, bold=True, color_rgb=palette["accent"])

    p_u2 = tf_u.add_paragraph()
    apply_p_rtl(p_u2, PP_ALIGN.CENTER)
    p_u2.space_before = Pt(3)
    r_u2 = p_u2.add_run()
    set_run_font(r_u2, meta.get("department", "گروه روان‌شناسی بالینی"), FONT_TITR, 11, bold=False, color_rgb=RGBColor(148, 163, 184))

    # Center Divider Hairline
    div = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(4.5), Inches(1.8), Inches(4.333), Pt(0.75))
    div.fill.solid()
    div.fill.fore_color.rgb = palette["accent"]
    div.line.fill.background()

    # Thesis Title Box (Centered, commanding, bold white typography)
    title_box = slide.shapes.add_textbox(Inches(1.0), Inches(2.05), Inches(11.333), Inches(1.85))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    apply_p_rtl(p_t, PP_ALIGN.CENTER)
    r_t = p_t.add_run()
    set_run_font(r_t, slide_data.get("title", meta.get("title", "")), FONT_TITR, 23.5, bold=True, color_rgb=palette["text_light"])

    # Subtitle / Degree Kicker
    sub_box = slide.shapes.add_textbox(Inches(2.0), Inches(3.95), Inches(9.333), Inches(0.45))
    tf_s = sub_box.text_frame
    p_s = tf_s.paragraphs[0]
    apply_p_rtl(p_s, PP_ALIGN.CENTER)
    r_s = p_s.add_run()
    sub_text = slide_data.get("subtitle", meta.get("degree", "پایان‌نامه دوره کارشناسی ارشد روان‌شناسی بالینی"))
    set_run_font(r_s, sub_text, FONT_TITR, 13, bold=True, color_rgb=palette["accent"])

    # Dual Translucent Slate Identity Cards: Candidate & Supervisor
    # Candidate Card (Right side)
    c_left = Inches(6.8)
    c_top = Inches(4.65)
    c_w = Inches(4.8)
    c_h = Inches(1.65)

    c_card = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, c_left, c_top, c_w, c_h)
    c_card.fill.solid()
    c_card.fill.fore_color.rgb = palette["cover_card"]
    c_card.line.color.rgb = palette["cover_border"]
    c_card.line.width = Pt(0.75)

    # Right accent strip on candidate card
    c_acc = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, c_left + c_w - Inches(0.06), c_top, Inches(0.06), c_h)
    c_acc.fill.solid()
    c_acc.fill.fore_color.rgb = RGBColor(59, 130, 246) # Soft Sapphire
    c_acc.line.fill.background()

    tf_cc = c_card.text_frame
    tf_cc.word_wrap = True
    tf_cc.margin_right = Inches(0.3)
    p_cc1 = tf_cc.paragraphs[0]
    apply_p_rtl(p_cc1, PP_ALIGN.RIGHT)
    r_cc1 = p_cc1.add_run()
    set_run_font(r_cc1, "نگارش و پژوهش", FONT_TITR, 10.5, bold=True, color_rgb=RGBColor(148, 163, 184))

    p_cc2 = tf_cc.add_paragraph()
    apply_p_rtl(p_cc2, PP_ALIGN.RIGHT)
    p_cc2.space_before = Pt(3)
    r_cc2 = p_cc2.add_run()
    set_run_font(r_cc2, meta.get("author", "مرضیه سینائی"), FONT_TITR, 16, bold=True, color_rgb=palette["text_light"])

    p_cc3 = tf_cc.add_paragraph()
    apply_p_rtl(p_cc3, PP_ALIGN.RIGHT)
    p_cc3.space_before = Pt(2)
    r_cc3 = p_cc3.add_run()
    set_run_font(r_cc3, "دانشجوی کارشناسی ارشد روان‌شناسی بالینی", FONT_NAZANIN, 12, bold=False, color_rgb=RGBColor(148, 163, 184))

    # Supervisor Card (Left side)
    s_left = Inches(1.733)
    s_top = Inches(4.65)
    s_w = Inches(4.8)
    s_h = Inches(1.65)

    s_card = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, s_left, s_top, s_w, s_h)
    s_card.fill.solid()
    s_card.fill.fore_color.rgb = palette["cover_card"]
    s_card.line.color.rgb = palette["cover_border"]
    s_card.line.width = Pt(0.75)

    # Right accent strip on supervisor card
    s_acc = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, s_left + s_w - Inches(0.06), s_top, Inches(0.06), s_h)
    s_acc.fill.solid()
    s_acc.fill.fore_color.rgb = palette["accent"]
    s_acc.line.fill.background()

    tf_sc = s_card.text_frame
    tf_sc.word_wrap = True
    tf_sc.margin_right = Inches(0.3)
    p_sc1 = tf_sc.paragraphs[0]
    apply_p_rtl(p_sc1, PP_ALIGN.RIGHT)
    r_sc1 = p_sc1.add_run()
    set_run_font(r_sc1, "استاد راهنما", FONT_TITR, 10.5, bold=True, color_rgb=palette["accent"])

    p_sc2 = tf_sc.add_paragraph()
    apply_p_rtl(p_sc2, PP_ALIGN.RIGHT)
    p_sc2.space_before = Pt(3)
    r_sc2 = p_sc2.add_run()
    set_run_font(r_sc2, meta.get("supervisor", "دکتر حمید امیری"), FONT_TITR, 16, bold=True, color_rgb=palette["text_light"])

    p_sc3 = tf_sc.add_paragraph()
    apply_p_rtl(p_sc3, PP_ALIGN.RIGHT)
    p_sc3.space_before = Pt(2)
    r_sc3 = p_sc3.add_run()
    set_run_font(r_sc3, "استادیار گروه روان‌شناسی بالینی", FONT_NAZANIN, 12, bold=False, color_rgb=RGBColor(148, 163, 184))

    # Bottom Defense Date & Session Tag
    date_box = slide.shapes.add_textbox(Inches(1.0), Inches(6.5), Inches(11.333), Inches(0.35))
    tf_d = date_box.text_frame
    p_d = tf_d.paragraphs[0]
    apply_p_rtl(p_d, PP_ALIGN.CENTER)
    r_d = p_d.add_run()
    set_run_font(r_d, f"جلسه دفاع از پایان‌نامه  |  {meta.get('defense_date', 'تابستان ۱۴۰۵')}", FONT_NAZANIN, 10.5, bold=False, color_rgb=RGBColor(100, 116, 139))

    attach_speaker_notes(slide, slide_data.get("speaker_notes", ""))

def build_committee_slide(prs: Presentation, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, Any], slide_num: int):
    """Slide 2: Executive Committee Directory 2x2 Clean Grid with Hairline Accents."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    draw_header_banner(slide, "ارکان پژوهش", slide_data.get("title", "هیئت محترم داوران و اساتید راهنما"), palette, slide_num)

    cards = slide_data.get("cards", [])
    if not cards:
        cards = [
            {"title": "استاد راهنما", "desc": meta.get("supervisor", "")},
            {"title": "استاد مشاور", "desc": meta.get("advisor", "")},
            {"title": "داور محترم داخلی", "desc": meta.get("internal_examiner", "")},
            {"title": "داور محترم خارجی", "desc": meta.get("external_examiner", "")}
        ]

    # 2x2 Grid Coordinates
    coords = [
        (Inches(6.8), Inches(1.58)), (Inches(0.8), Inches(1.58)),
        (Inches(6.8), Inches(4.0)),  (Inches(0.8), Inches(4.0))
    ]
    card_w = Inches(5.733)
    card_h = Inches(2.25)
    role_colors = [palette["accent"], palette["secondary"], palette["primary"], palette["secondary"]]

    for idx, card_item in enumerate(cards[:4]):
        left, top = coords[idx]
        box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, card_w, card_h)
        box.fill.solid()
        box.fill.fore_color.rgb = palette["card_bg"]
        box.line.color.rgb = palette["card_border"]
        box.line.width = Pt(0.75)

        # Right vertical accent bar
        acc = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left + card_w - Inches(0.06), top, Inches(0.06), card_h)
        acc.fill.solid()
        acc.fill.fore_color.rgb = role_colors[idx]
        acc.line.fill.background()

        # Role Tag Pill
        pill = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left + Inches(0.35), top + Inches(0.22), Inches(2.0), Inches(0.32))
        pill.fill.solid()
        pill.fill.fore_color.rgb = palette["badge_bg"]
        pill.line.color.rgb = palette["badge_border"]
        pill.line.width = Pt(0.5)
        tf_p = pill.text_frame
        p_p = tf_p.paragraphs[0]
        apply_p_rtl(p_p, PP_ALIGN.CENTER)
        r_p = p_p.add_run()
        clean_role = card_item.get("title", "").replace("🏛️", "").replace("🤝", "").replace("⚖️", "").strip()
        set_run_font(r_p, clean_role, FONT_TITR, 10, bold=True, color_rgb=palette["badge_text"])

        # Content Text Frame
        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.68)
        tf.margin_right = Inches(0.35)
        tf.margin_left = Inches(0.35)

        lines = [l.strip() for l in card_item.get("desc", "").split("\n") if l.strip()]
        for l_idx, line in enumerate(lines):
            p = tf.add_paragraph() if l_idx > 0 or tf.paragraphs[0].text else tf.paragraphs[0]
            apply_p_rtl(p, PP_ALIGN.RIGHT)
            p.space_after = Pt(3)
            run = p.add_run()
            if l_idx == 0:
                set_run_font(run, line, FONT_TITR, 15, bold=True, color_rgb=palette["text_dark"])
            else:
                set_run_font(run, line, FONT_NAZANIN, 12.5, bold=False, color_rgb=palette["text_muted"])

    # Bottom appreciation quote banner
    bot_box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(6.45), Inches(11.733), Inches(0.42))
    bot_box.fill.solid()
    bot_box.fill.fore_color.rgb = palette["card_bg"]
    bot_box.line.color.rgb = palette["card_border"]
    bot_box.line.width = Pt(0.75)
    
    tf_bot = bot_box.text_frame
    p_bot = tf_bot.paragraphs[0]
    apply_p_rtl(p_bot, PP_ALIGN.CENTER)
    r_bot = p_bot.add_run()
    set_run_font(r_bot, "«با سپاس فراوان از وقت، هدایت‌های عالمانه و راهنمایی‌های سازنده اساتید بزرگوار هیئت داوران»", FONT_NAZANIN, 11, bold=True, color_rgb=palette["secondary"])

    attach_speaker_notes(slide, slide_data.get("speaker_notes", ""))

def build_split_diagram_slide(prs: Presentation, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, Any], slide_num: int):
    """
    Split Editorial Layout:
    Left: High-resolution picture / 300-DPI figure with clean hairline framing.
    Right: Analytical insight cards with vertical right accents and pill chips.
    Bottom: Key Takeaway Banner.
    """
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    draw_header_banner(slide, slide_data.get("category", ""), slide_data.get("title", ""), palette, slide_num)

    img_path = slide_data.get("image_path", "")
    cards = slide_data.get("cards", [])
    callout_text = slide_data.get("callout", "")

    # Layout geometry
    img_left = Inches(0.8)
    img_top = Inches(1.55)
    img_w = Inches(5.6)
    img_h = Inches(4.25 if callout_text else 4.95)

    cards_left = Inches(6.733)
    cards_top = Inches(1.55)
    cards_w = Inches(5.8)

    # 1. Image Container (Clean, uncluttered, publication framing)
    if img_path and os.path.exists(img_path):
        # Insert image cleanly
        slide.shapes.add_picture(img_path, img_left, img_top, img_w, img_h)
        
        # Hairline border around picture
        pic_frame = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, img_left, img_top, img_w, img_h)
        pic_frame.fill.background()
        pic_frame.line.color.rgb = palette["card_border"]
        pic_frame.line.width = Pt(0.75)

        # Subtle caption below image
        caption = slide_data.get("image_caption", "")
        if caption:
            cap_box = slide.shapes.add_textbox(img_left, img_top + img_h + Inches(0.04), img_w, Inches(0.35))
            tf_cap = cap_box.text_frame
            tf_cap.word_wrap = True
            tf_cap.margin_top = Inches(0)
            p_cap = tf_cap.paragraphs[0]
            apply_p_rtl(p_cap, PP_ALIGN.CENTER)
            r_cap = p_cap.add_run()
            set_run_font(r_cap, caption, FONT_NAZANIN, 10.5, bold=False, color_rgb=palette["text_muted"])

    # 2. Analytical Cards Column (3 Clean elevated insight cards)
    num_cards = len(cards)
    gap = 0.16
    avail_h = img_h.inches + (0.35 if not callout_text else 0)
    card_h = (avail_h - (num_cards - 1) * gap) / max(1, num_cards)

    acc_colors = [palette["secondary"], palette["accent"], palette["primary"], palette["secondary"]]

    for i, c_item in enumerate(cards):
        c_top = Inches(cards_top.inches + i * (card_h + gap))
        box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, cards_left, c_top, cards_w, Inches(card_h))
        box.fill.solid()
        box.fill.fore_color.rgb = palette["card_bg"]
        box.line.color.rgb = palette["card_border"]
        box.line.width = Pt(0.75)

        # Right vertical accent line
        acc = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, cards_left + cards_w - Inches(0.05), c_top, Inches(0.05), Inches(card_h))
        acc.fill.solid()
        acc.fill.fore_color.rgb = acc_colors[i % len(acc_colors)]
        acc.line.fill.background()

        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_right = Inches(0.25)
        tf.margin_left = Inches(0.2)
        tf.margin_top = Inches(0.12)
        tf.margin_bottom = Inches(0.08)

        # Title & Badge
        p_title = tf.paragraphs[0]
        apply_p_rtl(p_title, PP_ALIGN.RIGHT)
        p_title.space_after = Pt(2)
        
        badge = c_item.get("badge", "").strip()
        if badge:
            # Clean pill badge
            r_badge = p_title.add_run()
            clean_badge = badge.replace("[", "").replace("]", "").strip()
            set_run_font(r_badge, f"{clean_badge}  |  ", FONT_TITR, 10, bold=True, color_rgb=palette["accent_dark"])

        r_title = p_title.add_run()
        set_run_font(r_title, c_item.get("title", ""), FONT_TITR, 13.5, bold=True, color_rgb=palette["primary"])

        # Body Text
        desc_lines = [l.strip() for l in c_item.get("desc", "").split("\n") if l.strip()]
        for line in desc_lines:
            p_desc = tf.add_paragraph()
            apply_p_rtl(p_desc, PP_ALIGN.RIGHT)
            p_desc.space_after = Pt(2)
            r_desc = p_desc.add_run()
            set_run_font(r_desc, line, FONT_NAZANIN, 11.5, bold=False, color_rgb=palette["text_body"])

    # 3. Bottom Callout Banner
    if callout_text:
        draw_callout_banner(slide, callout_text, palette, Inches(0.8), Inches(6.25), Inches(11.733), Inches(0.68))

    attach_speaker_notes(slide, slide_data.get("speaker_notes", ""))

def build_kpi_dashboard_slide(prs: Presentation, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, Any], slide_num: int):
    """
    Executive SEM Goodness-of-Fit Dashboard:
    4 large metric stat cards + Analytical synthesis container + Takeaway banner.
    """
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    draw_header_banner(slide, slide_data.get("category", ""), slide_data.get("title", ""), palette, slide_num)

    kpis = slide_data.get("kpis", [])
    callout_text = slide_data.get("callout", "")

    # 4 Stat Cards in a row
    gap = 0.22
    total_w = 11.733
    kpi_w = (total_w - 3 * gap) / 4
    kpi_h = 2.25

    for idx, kpi in enumerate(kpis[:4]):
        left = Inches(0.8 + idx * (kpi_w + gap))
        top = Inches(1.55)
        box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, Inches(kpi_w), Inches(kpi_h))
        box.fill.solid()
        box.fill.fore_color.rgb = palette["card_bg"]
        box.line.color.rgb = palette["card_border"]
        box.line.width = Pt(0.75)

        # Right vertical accent bar
        acc = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left + Inches(kpi_w) - Inches(0.05), top, Inches(0.05), Inches(kpi_h))
        acc.fill.solid()
        acc.fill.fore_color.rgb = palette["secondary"] if idx in [0, 1] else palette["emerald"]
        acc.line.fill.background()

        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_top = Inches(0.18)
        tf.margin_right = Inches(0.18)
        tf.margin_left = Inches(0.18)

        # Big Stat Value (Times New Roman Bold)
        p_val = tf.paragraphs[0]
        apply_p_rtl(p_val, PP_ALIGN.CENTER)
        r_val = p_val.add_run()
        set_run_font(r_val, str(kpi.get("value", "")), FONT_ENG, 34, bold=True, color_rgb=palette["primary"])

        # Metric Title
        p_tit = tf.add_paragraph()
        apply_p_rtl(p_tit, PP_ALIGN.CENTER)
        p_tit.space_before = Pt(3)
        r_tit = p_tit.add_run()
        set_run_font(r_tit, kpi.get("title", ""), FONT_TITR, 11.5, bold=True, color_rgb=palette["secondary"])

        # Status Chip Badge
        status = kpi.get("status", "").replace("★", "").replace("✓", "").strip()
        if status:
            p_stat = tf.add_paragraph()
            apply_p_rtl(p_stat, PP_ALIGN.CENTER)
            p_stat.space_before = Pt(4)
            r_stat = p_stat.add_run()
            set_run_font(r_stat, status, FONT_TITR, 10, bold=True, color_rgb=palette["emerald"])

        # Benchmark Criterion
        sub = kpi.get("desc", "")
        if sub:
            p_sub = tf.add_paragraph()
            apply_p_rtl(p_sub, PP_ALIGN.CENTER)
            p_sub.space_before = Pt(2)
            r_sub = p_sub.add_run()
            set_run_font(r_sub, sub, FONT_NAZANIN, 10, bold=False, color_rgb=palette["text_muted"])

    # Bottom Analytical Synthesis Card
    bot_top = Inches(3.98)
    bot_h = Inches(2.12)
    bot_card = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), bot_top, Inches(11.733), bot_h)
    bot_card.fill.solid()
    bot_card.fill.fore_color.rgb = palette["card_bg"]
    bot_card.line.color.rgb = palette["card_border"]
    bot_card.line.width = Pt(0.75)

    # Right vertical accent line
    bot_acc = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8 + 11.733 - 0.06), bot_top, Inches(0.06), bot_h)
    bot_acc.fill.solid()
    bot_acc.fill.fore_color.rgb = palette["secondary"]
    bot_acc.line.fill.background()

    tf_b = bot_card.text_frame
    tf_b.word_wrap = True
    tf_b.margin_right = Inches(0.35)
    tf_b.margin_left = Inches(0.35)
    tf_b.margin_top = Inches(0.18)

    p_bh = tf_b.paragraphs[0]
    apply_p_rtl(p_bh, PP_ALIGN.RIGHT)
    r_bh = p_bh.add_run()
    set_run_font(r_bh, slide_data.get("analysis_title", "تحلیل و تفسیر روان‌سنجی برازش مدل ساختاری"), FONT_TITR, 13.5, bold=True, color_rgb=palette["primary"])

    for line in slide_data.get("analysis_desc", "").split("\n"):
        if not line.strip():
            continue
        p_bd = tf_b.add_paragraph()
        apply_p_rtl(p_bd, PP_ALIGN.RIGHT)
        p_bd.space_after = Pt(4)
        r_bd = p_bd.add_run()
        set_run_font(r_bd, line.strip(), FONT_NAZANIN, 12, bold=False, color_rgb=palette["text_body"])

    # Bottom Takeaway Banner
    if callout_text:
        draw_callout_banner(slide, callout_text, palette, Inches(0.8), Inches(6.25), Inches(11.733), Inches(0.68))

    attach_speaker_notes(slide, slide_data.get("speaker_notes", ""))

def build_cards_slide(prs: Presentation, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, Any], slide_num: int):
    """
    Clean Editorial Cards Slide:
    Renders 1, 2, 3, or 4 elevated white cards with clean vertical accents and refined badges.
    """
    if slide_data.get("image_path"):
        build_split_diagram_slide(prs, meta, slide_data, palette, slide_num)
        return

    slide = prs.slides.add_slide(prs.slide_layouts[6])
    draw_header_banner(slide, slide_data.get("category", ""), slide_data.get("title", ""), palette, slide_num)

    cards = slide_data.get("cards", [])
    callout_text = slide_data.get("callout", "")
    num_cards = len(cards)

    avail_h = 4.65 if callout_text else 5.35
    top_pos = Inches(1.55)

    if num_cards == 1:
        box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), top_pos, Inches(11.733), Inches(avail_h))
        box.fill.solid()
        box.fill.fore_color.rgb = palette["card_bg"]
        box.line.color.rgb = palette["card_border"]
        box.line.width = Pt(0.75)

        acc = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8 + 11.733 - 0.06), top_pos, Inches(0.06), Inches(avail_h))
        acc.fill.solid()
        acc.fill.fore_color.rgb = palette["secondary"]
        acc.line.fill.background()

        tf = box.text_frame
        tf.word_wrap = True
        tf.margin_right = Inches(0.4)
        tf.margin_left = Inches(0.4)
        tf.margin_top = Inches(0.25)

        p_c = tf.paragraphs[0]
        apply_p_rtl(p_c, PP_ALIGN.RIGHT)
        r_c = p_c.add_run()
        set_run_font(r_c, cards[0].get("title", ""), FONT_TITR, 17, bold=True, color_rgb=palette["primary"])
        for line in cards[0].get("desc", "").split("\n"):
            p_l = tf.add_paragraph()
            apply_p_rtl(p_l, PP_ALIGN.RIGHT)
            p_l.space_after = Pt(5)
            r_l = p_l.add_run()
            set_run_font(r_l, line.strip(), FONT_NAZANIN, 13.5, bold=False, color_rgb=palette["text_body"])

    elif num_cards in [2, 3]:
        gap = 0.22
        total_w = 11.733
        card_w = (total_w - (num_cards - 1) * gap) / num_cards
        acc_colors = [palette["secondary"], palette["accent"], palette["primary"]]

        for i, card_item in enumerate(cards):
            left = Inches(0.8 + i * (card_w + gap))
            box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top_pos, Inches(card_w), Inches(avail_h))
            box.fill.solid()
            box.fill.fore_color.rgb = palette["card_bg"]
            box.line.color.rgb = palette["card_border"]
            box.line.width = Pt(0.75)

            # Right vertical accent bar
            acc = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left + Inches(card_w) - Inches(0.06), top_pos, Inches(0.06), Inches(avail_h))
            acc.fill.solid()
            acc.fill.fore_color.rgb = acc_colors[i % len(acc_colors)]
            acc.line.fill.background()

            tf = box.text_frame
            tf.word_wrap = True
            tf.margin_right = Inches(0.28)
            tf.margin_left = Inches(0.25)
            tf.margin_top = Inches(0.2)

            # Badge pill
            p_head = tf.paragraphs[0]
            apply_p_rtl(p_head, PP_ALIGN.RIGHT)
            p_head.space_after = Pt(4)
            badge = card_item.get("badge", "").strip()
            if badge:
                r_b = p_head.add_run()
                clean_b = badge.replace("[", "").replace("]", "").strip()
                set_run_font(r_b, f"{clean_b}  |  ", FONT_TITR, 10.5, bold=True, color_rgb=palette["accent_dark"])
            r_head = p_head.add_run()
            set_run_font(r_head, card_item.get("title", ""), FONT_TITR, 14.5, bold=True, color_rgb=palette["primary"])

            for line in card_item.get("desc", "").split("\n"):
                if not line.strip():
                    continue
                p_body = tf.add_paragraph()
                apply_p_rtl(p_body, PP_ALIGN.RIGHT)
                p_body.space_after = Pt(4)
                r_body = p_body.add_run()
                set_run_font(r_body, line.strip(), FONT_NAZANIN, 12.5, bold=False, color_rgb=palette["text_body"])

    elif num_cards >= 4:
        grid_coords = [
            (Inches(6.8), top_pos), (Inches(0.8), top_pos),
            (Inches(6.8), top_pos + Inches(avail_h / 2 + 0.05)), (Inches(0.8), top_pos + Inches(avail_h / 2 + 0.05))
        ]
        card_w = Inches(5.733)
        card_h = Inches(avail_h / 2 - 0.1)

        acc_colors = [palette["secondary"], palette["accent"], palette["primary"], palette["secondary"]]

        for i in range(min(4, len(cards))):
            card_item = cards[i]
            left, top = grid_coords[i]
            box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, card_w, card_h)
            box.fill.solid()
            box.fill.fore_color.rgb = palette["card_bg"]
            box.line.color.rgb = palette["card_border"]
            box.line.width = Pt(0.75)

            # Right vertical accent line
            acc = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left + card_w - Inches(0.05), top, Inches(0.05), card_h)
            acc.fill.solid()
            acc.fill.fore_color.rgb = acc_colors[i]
            acc.line.fill.background()

            tf = box.text_frame
            tf.word_wrap = True
            tf.margin_right = Inches(0.22)
            tf.margin_left = Inches(0.2)
            tf.margin_top = Inches(0.12)

            p_head = tf.paragraphs[0]
            apply_p_rtl(p_head, PP_ALIGN.RIGHT)
            p_head.space_after = Pt(2)
            badge = card_item.get("badge", "").strip()
            if badge:
                r_b = p_head.add_run()
                clean_b = badge.replace("[", "").replace("]", "").strip()
                set_run_font(r_b, f"{clean_b}  |  ", FONT_TITR, 10, bold=True, color_rgb=palette["accent_dark"])
            r_head = p_head.add_run()
            set_run_font(r_head, card_item.get("title", ""), FONT_TITR, 13.5, bold=True, color_rgb=palette["primary"])

            for line in card_item.get("desc", "").split("\n"):
                if not line.strip():
                    continue
                p_body = tf.add_paragraph()
                apply_p_rtl(p_body, PP_ALIGN.RIGHT)
                p_body.space_after = Pt(2)
                r_body = p_body.add_run()
                set_run_font(r_body, line.strip(), FONT_NAZANIN, 12, bold=False, color_rgb=palette["text_body"])

    # Bottom Callout Banner
    if callout_text:
        draw_callout_banner(slide, callout_text, palette, Inches(0.8), Inches(6.25), Inches(11.733), Inches(0.68))

    attach_speaker_notes(slide, slide_data.get("speaker_notes", ""))

def build_table_slide(prs: Presentation, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, Any], slide_num: int):
    """
    Publication-grade APA 7 Empirical Data Table Slide:
    Zero vertical borders, exact 3 horizontal boundaries, subtle zebra rows, and authenticated APA table note.
    """
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    draw_header_banner(slide, slide_data.get("category", ""), slide_data.get("title", ""), palette, slide_num)

    tbl_data = slide_data.get("table", {})
    headers = tbl_data.get("headers", [])
    rows = tbl_data.get("rows", [])
    table_note = slide_data.get("table_note", "")

    if not headers or not rows:
        return

    num_rows = len(rows) + 1
    num_cols = len(headers)

    table_left = Inches(0.8)
    table_top = Inches(1.55)
    table_width = Inches(11.733)
    max_h = 4.5 if table_note else 5.2
    table_height = Inches(min(max_h, 0.42 * num_rows))

    table_shape = slide.shapes.add_table(num_rows, num_cols, table_left, table_top, table_width, table_height)
    tbl = table_shape.table

    # Format Header Row (Deep Slate #0F172A)
    for c_idx, h_text in enumerate(headers):
        cell = tbl.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = palette["tbl_header"]
        cell.text = ""
        p = cell.text_frame.paragraphs[0]
        apply_p_rtl(p, PP_ALIGN.CENTER)
        run = p.add_run()
        set_run_font(run, h_text, FONT_TITR, 11, bold=True, color_rgb=palette["text_light"])

    # Format Data Rows (Subtle zebra striping + green status chip for confirmed hypotheses)
    for r_idx, row_vals in enumerate(rows):
        is_even = (r_idx % 2 == 0)
        row_num = r_idx + 1
        for c_idx, val in enumerate(row_vals):
            if c_idx >= num_cols:
                break
            cell = tbl.cell(row_num, c_idx)
            val_str = str(val).strip()
            cell.text = ""
            p = cell.text_frame.paragraphs[0]
            
            # Align first column to the right (Persian variable names), others centered
            align = PP_ALIGN.RIGHT if c_idx == (num_cols - 1) or (c_idx == 0 and not any(ch.isdigit() for ch in val_str)) else PP_ALIGN.CENTER
            apply_p_rtl(p, align)

            # Hypothesis status formatting
            if "تأیید" in val_str or "Supported" in val_str:
                cell.fill.solid()
                cell.fill.fore_color.rgb = palette["emerald_light"]
                run = p.add_run()
                set_run_font(run, val_str, FONT_TITR, 10.5, bold=True, color_rgb=palette["emerald"])
            else:
                cell.fill.solid()
                cell.fill.fore_color.rgb = palette["tbl_stripe"] if is_even else palette["card_bg"]
                run = p.add_run()
                font_to_use = FONT_ENG if any(char.isdigit() or char in "<>=.±-" for char in val_str) else FONT_NAZANIN
                bold = ("تأیید" in val_str)
                set_run_font(run, val_str, font_to_use, 11, bold=bold, color_rgb=palette["text_dark"])

    # Table Note Box below table
    if table_note:
        note_top = Inches(table_top.inches + table_height.inches + 0.15)
        note_box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), note_top, Inches(11.733), Inches(0.55))
        note_box.fill.solid()
        note_box.fill.fore_color.rgb = palette["card_bg"]
        note_box.line.color.rgb = palette["card_border"]
        note_box.line.width = Pt(0.75)
        
        # Right accent bar on table note
        note_acc = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8 + 11.733 - 0.05), note_top, Inches(0.05), Inches(0.55))
        note_acc.fill.solid()
        note_acc.fill.fore_color.rgb = palette["secondary"]
        note_acc.line.fill.background()

        tf_n = note_box.text_frame
        tf_n.word_wrap = True
        tf_n.margin_right = Inches(0.25)
        tf_n.margin_left = Inches(0.25)
        p_n = tf_n.paragraphs[0]
        apply_p_rtl(p_n, PP_ALIGN.RIGHT)
        r_nh = p_n.add_run()
        set_run_font(r_nh, "یادداشت جدول: ", FONT_TITR, 10.5, bold=True, color_rgb=palette["secondary"])
        r_nt = p_n.add_run()
        clean_note = table_note.replace("📌", "").strip()
        set_run_font(r_nt, clean_note, FONT_NAZANIN, 11, bold=False, color_rgb=palette["text_body"])

    attach_speaker_notes(slide, slide_data.get("speaker_notes", ""))

def build_closing_slide(prs: Presentation, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, Any], slide_num: int):
    """
    Slide 28: Executive Luxury Closing Slide in Midnight Obsidian (#0A1128).
    Dignified appreciation, scholarly quotation, and committee Q&A readiness.
    """
    slide = prs.slides.add_slide(prs.slide_layouts[6])

    # Full Midnight Obsidian Background
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = palette["cover_bg"]
    bg.line.fill.background()

    # Subtle Architectural Hairline Accent Frame
    frame = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.5), Inches(0.5), Inches(12.333), Inches(6.5))
    frame.fill.background()
    frame.line.color.rgb = palette["accent"]
    frame.line.width = Pt(0.75)

    # University Header
    uni_b = slide.shapes.add_textbox(Inches(1.0), Inches(0.9), Inches(11.333), Inches(0.45))
    tf_ub = uni_b.text_frame
    p_ub = tf_ub.paragraphs[0]
    apply_p_rtl(p_ub, PP_ALIGN.CENTER)
    r_ub = p_ub.add_run()
    set_run_font(r_ub, f"{meta.get('university', 'دانشگاه آزاد اسلامی')}  |  {meta.get('faculty', 'واحد کاشان • دانشکده علوم انسانی')}", FONT_TITR, 11.5, bold=True, color_rgb=palette["accent"])

    # Center Divider Hairline
    div = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(4.5), Inches(1.5), Inches(4.333), Pt(0.75))
    div.fill.solid()
    div.fill.fore_color.rgb = palette["accent"]
    div.line.fill.background()

    # Grand Thank You Headline
    title_box = slide.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(11.333), Inches(1.0))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    apply_p_rtl(p_t, PP_ALIGN.CENTER)
    r_t = p_t.add_run()
    set_run_font(r_t, slide_data.get("title", "با سپاس و احترام فراوان"), FONT_TITR, 27, bold=True, color_rgb=palette["text_light"])

    # Subtitle / Appreciation & Scholarly Quote
    sub_box = slide.shapes.add_textbox(Inches(1.5), Inches(2.85), Inches(10.333), Inches(1.8))
    tf_s = sub_box.text_frame
    tf_s.word_wrap = True
    for line in slide_data.get("subtitle", "").split("\n"):
        p_s = tf_s.add_paragraph() if tf_s.paragraphs[0].text else tf_s.paragraphs[0]
        apply_p_rtl(p_s, PP_ALIGN.CENTER)
        p_s.space_after = Pt(6)
        r_s = p_s.add_run()
        if "دانش چون درختی است" in line:
            set_run_font(r_s, line.strip(), FONT_NAZANIN, 13.5, bold=True, color_rgb=palette["accent"])
        else:
            set_run_font(r_s, line.strip(), FONT_NAZANIN, 14, bold=False, color_rgb=RGBColor(226, 232, 240))

    # Q&A Readiness Banner (Translucent Slate with Champagne Gold Hairline)
    qa_box = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(2.2), Inches(4.85), Inches(8.933), Inches(1.15))
    qa_box.fill.solid()
    qa_box.fill.fore_color.rgb = palette["cover_card"]
    qa_box.line.color.rgb = palette["accent"]
    qa_box.line.width = Pt(1.0)
    
    tf_qa = qa_box.text_frame
    tf_qa.word_wrap = True
    tf_qa.margin_top = Inches(0.18)
    p_qa1 = tf_qa.paragraphs[0]
    apply_p_rtl(p_qa1, PP_ALIGN.CENTER)
    r_qa1 = p_qa1.add_run()
    set_run_font(r_qa1, "جلسه دفاع و پاسخ به پرسش‌های هیئت محترم داوران", FONT_TITR, 13.5, bold=True, color_rgb=palette["accent"])
    
    p_qa2 = tf_qa.add_paragraph()
    apply_p_rtl(p_qa2, PP_ALIGN.CENTER)
    p_qa2.space_before = Pt(3)
    r_qa2 = p_qa2.add_run()
    set_run_font(r_qa2, "با کمال احترام، آماده استماع نقدها، دیدگاه‌ها و سوالات اساتید ارجمند می‌باشم.", FONT_NAZANIN, 12, bold=True, color_rgb=palette["text_light"])

    # Bottom Footer
    foot_box = slide.shapes.add_textbox(Inches(1.0), Inches(6.45), Inches(11.333), Inches(0.35))
    tf_foot = foot_box.text_frame
    p_foot = tf_foot.paragraphs[0]
    apply_p_rtl(p_foot, PP_ALIGN.CENTER)
    r_foot = p_foot.add_run()
    set_run_font(r_foot, f"پایان ارائه  |  مرضیه سینائی  |  {meta.get('defense_date', 'تابستان ۱۴۰۵')}", FONT_NAZANIN, 10, bold=False, color_rgb=RGBColor(100, 116, 139))

    attach_speaker_notes(slide, slide_data.get("speaker_notes", ""))

# ---------------------------------------------------------------------------
# Main Presentation Compiler Entrypoint
# ---------------------------------------------------------------------------
def compile_presentation(payload: Dict[str, Any], output_path: str, theme_name: str = "academic_navy"):
    """Compile structured presentation dictionary into high-end publication-grade .pptx file."""
    prs = Presentation()
    prs.slide_width = Inches(13.333) # 16:9 Widescreen standard
    prs.slide_height = Inches(7.5)

    palette = PALETTES.get(theme_name, PALETTES["academic_navy"])
    meta = payload.get("meta", {})
    slides = payload.get("slides", [])
    total_slides = len(slides)

    print(f"[*] Compiling {total_slides} executive defense slides with theme: '{theme_name}'...")

    for idx, slide_item in enumerate(slides):
        slide_num = idx + 1
        layout = slide_item.get("layout", "cards")

        if layout == "cover":
            build_cover_slide(prs, meta, slide_item, palette)
        elif layout == "committee":
            build_committee_slide(prs, meta, slide_item, palette, slide_num)
        elif layout == "table":
            build_table_slide(prs, meta, slide_item, palette, slide_num)
        elif layout == "closing":
            build_closing_slide(prs, meta, slide_item, palette, slide_num)
        elif layout == "kpi_dashboard":
            build_kpi_dashboard_slide(prs, meta, slide_item, palette, slide_num)
        elif layout == "split_diagram":
            build_split_diagram_slide(prs, meta, slide_item, palette, slide_num)
        else: # default cards
            build_cards_slide(prs, meta, slide_item, palette, slide_num)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    prs.save(output_path)
    print(f"[SUCCESS] Executive defense presentation successfully generated at: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Master Persian Academic Thesis Defense Presentation Compiler (Executive Pro Edition)")
    parser.add_argument("--json", type=str, help="Path to structured presentation payload JSON")
    parser.add_argument("--output", type=str, default="Defense_Presentation.pptx", help="Path to output .pptx file")
    parser.add_argument("--theme", type=str, default="academic_navy", choices=["academic_navy", "emerald_slate", "royal_burgundy"], help="Color theme")
    parser.add_argument("--title", type=str, help="Thesis title")
    parser.add_argument("--author", type=str, help="Candidate name")
    parser.add_argument("--supervisor", type=str, help="Supervisor name")
    args = parser.parse_args()

    if args.json and os.path.exists(args.json):
        with open(args.json, "r", encoding="utf-8") as f:
            payload = json.load(f)
    else:
        print("[!] No valid --json payload provided. Loading default sample payload...", file=sys.stderr)
        sample_path = os.path.join(os.path.dirname(__file__), "..", "examples", "sample_defense_payload.json")
        if os.path.exists(sample_path):
            with open(sample_path, "r", encoding="utf-8") as f:
                payload = json.load(f)
        else:
            raise FileNotFoundError("Neither --json payload nor sample_defense_payload.json was found.")

    if args.title:
        payload.setdefault("meta", {})["title"] = args.title
    if args.author:
        payload.setdefault("meta", {})["author"] = args.author
    if args.supervisor:
        payload.setdefault("meta", {})["supervisor"] = args.supervisor

    compile_presentation(payload, args.output, args.theme)

if __name__ == "__main__":
    main()
