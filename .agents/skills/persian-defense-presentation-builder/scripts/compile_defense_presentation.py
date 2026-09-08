#!/usr/bin/env python3
"""
Master Persian Academic Thesis Defense Presentation Compiler
============================================================
Author: Saber Ghaderi
Repository: GhaderiSaber/AcademicSuite
Description:
    Compiles graduate thesis and dissertation defense presentations (.pptx)
    for Iranian Master's and PhD candidates with native Right-to-Left (RTL)
    OpenXML formatting, Iranian typography (B Titr, B Nazanin), container
    card layouts, APA 7 data tables, and oral candidate Speaker Notes.
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Any, Optional

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls

# ---------------------------------------------------------------------------
# Visual Themes & Palettes (16:9 Widescreen)
# ---------------------------------------------------------------------------
PALETTES = {
    "academic_navy": {
        "primary": RGBColor(26, 54, 93),       # Deep Navy #1A365D
        "secondary": RGBColor(43, 108, 176),   # Mid Blue #2B6CB0
        "accent": RGBColor(214, 158, 46),      # Warm Gold #D69E2E
        "accent_dark": RGBColor(183, 121, 31), # Dark Gold #B7791F
        "bg_slide": RGBColor(248, 250, 252),   # Off-white / Platinum #F8FAFC
        "card_bg": RGBColor(255, 255, 255),    # Pure White #FFFFFF
        "card_border": RGBColor(226, 232, 240),# Border Slate #E2E8F0
        "text_dark": RGBColor(30, 41, 59),     # Slate Dark #1E293B
        "text_muted": RGBColor(100, 116, 139), # Slate Muted #64748B
        "text_light": RGBColor(255, 255, 255), # Pure White
        "tbl_header": RGBColor(26, 54, 93),
        "tbl_stripe": RGBColor(241, 245, 249)
    },
    "emerald_slate": {
        "primary": RGBColor(19, 78, 74),       # Deep Forest Teal #134E4A
        "secondary": RGBColor(15, 118, 110),   # Teal #0F766E
        "accent": RGBColor(5, 150, 105),       # Emerald #059669
        "accent_dark": RGBColor(4, 120, 87),
        "bg_slide": RGBColor(240, 253, 244),   # Soft Mint Ice #F0FDF4
        "card_bg": RGBColor(255, 255, 255),
        "card_border": RGBColor(209, 250, 229),
        "text_dark": RGBColor(19, 42, 31),
        "text_muted": RGBColor(75, 85, 99),
        "text_light": RGBColor(255, 255, 255),
        "tbl_header": RGBColor(19, 78, 74),
        "tbl_stripe": RGBColor(236, 253, 245)
    },
    "royal_burgundy": {
        "primary": RGBColor(74, 14, 23),       # Imperial Maroon #4A0E17
        "secondary": RGBColor(136, 19, 55),    # Rose Maroon #881337
        "accent": RGBColor(217, 119, 6),       # Warm Amber #D97706
        "accent_dark": RGBColor(180, 83, 9),
        "bg_slide": RGBColor(255, 251, 235),   # Soft Warm Pearl #FFFBEB
        "card_bg": RGBColor(255, 255, 255),
        "card_border": RGBColor(254, 215, 170),
        "text_dark": RGBColor(31, 41, 55),
        "text_muted": RGBColor(107, 114, 128),
        "text_light": RGBColor(255, 255, 255),
        "tbl_header": RGBColor(74, 14, 23),
        "tbl_stripe": RGBColor(254, 243, 199)
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

    # Inject <a:cs typeface="..."/> into <a:rPr>
    rPr = run._r.get_or_add_rPr()
    cs = rPr.find(f"{{{nsdecls('a').split('=')[1].strip('\"')}}}cs")
    if cs is None:
        cs = parse_xml(f'<a:cs {nsdecls("a")} typeface="{font_name}"/>')
        rPr.append(cs)
    else:
        cs.set("typeface", font_name)

def attach_speaker_notes(slide, notes_text: str):
    """Attach Persian oral speaker notes with RTL typography."""
    if not notes_text:
        return
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.word_wrap = True
    
    # Split paragraphs by newline
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

def draw_header_banner(slide, category: str, title: str, palette: Dict[str, Any]):
    """Render consistent modern slide header with accent pill and category tag."""
    # Top thin accent line
    top_bar = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.1)
    )
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = palette["accent"]
    top_bar.line.fill.background()

    # Category Pill
    if category:
        cat_box = slide.shapes.add_shape(
            MSO_SHAPE.ROUNDED_RECTANGLE, Inches(10.5), Inches(0.3), Inches(2.3), Inches(0.4)
        )
        cat_box.fill.solid()
        cat_box.fill.fore_color.rgb = palette["primary"]
        cat_box.line.color.rgb = palette["accent"]
        cat_box.line.width = Pt(1)
        tf_c = cat_box.text_frame
        tf_c.word_wrap = True
        p_c = tf_c.paragraphs[0]
        apply_p_rtl(p_c, PP_ALIGN.CENTER)
        r_c = p_c.add_run()
        set_run_font(r_c, category, FONT_TITR, 11, bold=True, color_rgb=palette["text_light"])

    # Slide Title
    title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.35), Inches(9.5), Inches(0.8))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    apply_p_rtl(p_t, PP_ALIGN.RIGHT)
    r_t = p_t.add_run()
    set_run_font(r_t, title, FONT_TITR, 22, bold=True, color_rgb=palette["primary"])

    # Subtle horizontal separator
    sep = slide.shapes.add_shape(
        MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.2), Inches(11.733), Inches(0.02)
    )
    sep.fill.solid()
    sep.fill.fore_color.rgb = palette["card_border"]
    sep.line.fill.background()

# ---------------------------------------------------------------------------
# Slide Generators
# ---------------------------------------------------------------------------
def build_cover_slide(prs: Presentation, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, Any]):
    """Phase 1: Title Slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # Background full fill
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = palette["primary"]
    bg.line.fill.background()

    # Inner Gold Border Card
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.8), Inches(0.6), Inches(11.733), Inches(6.3))
    card.fill.solid()
    card.fill.fore_color.rgb = palette["card_bg"]
    card.line.color.rgb = palette["accent"]
    card.line.width = Pt(2.5)

    # University & Faculty Header
    header_box = slide.shapes.add_textbox(Inches(1.5), Inches(0.9), Inches(10.333), Inches(0.8))
    tf_h = header_box.text_frame
    tf_h.word_wrap = True
    p_uni = tf_h.paragraphs[0]
    apply_p_rtl(p_uni, PP_ALIGN.CENTER)
    r_uni = p_uni.add_run()
    uni_text = f"{meta.get('university', 'دانشگاه سراسری')} • {meta.get('faculty', 'دانشکده روان‌شناسی و علوم تربیتی')}"
    set_run_font(r_uni, uni_text, FONT_TITR, 14, bold=True, color_rgb=palette["secondary"])

    # Main Title Box
    title_box = slide.shapes.add_textbox(Inches(1.2), Inches(1.8), Inches(10.933), Inches(1.8))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    apply_p_rtl(p_t, PP_ALIGN.CENTER)
    r_t = p_t.add_run()
    set_run_font(r_t, slide_data.get("title", meta.get("title", "")), FONT_TITR, 24, bold=True, color_rgb=palette["primary"])

    # Subtitle / Degree
    sub_box = slide.shapes.add_textbox(Inches(1.5), Inches(3.7), Inches(10.333), Inches(0.5))
    tf_s = sub_box.text_frame
    p_s = tf_s.paragraphs[0]
    apply_p_rtl(p_s, PP_ALIGN.CENTER)
    r_s = p_s.add_run()
    deg_text = slide_data.get("subtitle", meta.get("degree", "پایان‌نامه دوره کارشناسی ارشد"))
    set_run_font(r_s, deg_text, FONT_NAZANIN, 16, bold=True, color_rgb=palette["accent_dark"])

    # Candidate & Faculty Directory Table in Card Bottom
    info_table_shape = slide.shapes.add_table(2, 2, Inches(2.2), Inches(4.5), Inches(8.933), Inches(1.5))
    info_tbl = info_table_shape.table
    info_tbl.columns[0].width = Inches(4.466)
    info_tbl.columns[1].width = Inches(4.466)

    # Row 0: Author & Supervisor
    cell_00 = info_tbl.cell(0, 0)
    cell_00.text = ""
    p_00 = cell_00.text_frame.paragraphs[0]
    apply_p_rtl(p_00, PP_ALIGN.CENTER)
    r_00 = p_00.add_run()
    set_run_font(r_00, f"نگارش و پژوهش: {meta.get('author', 'دانشجو')}", FONT_NAZANIN, 14, bold=True, color_rgb=palette["text_dark"])

    cell_01 = info_tbl.cell(0, 1)
    cell_01.text = ""
    p_01 = cell_01.text_frame.paragraphs[0]
    apply_p_rtl(p_01, PP_ALIGN.CENTER)
    r_01 = p_01.add_run()
    set_run_font(r_01, f"استاد راهنما: {meta.get('supervisor', 'استاد راهنما')}", FONT_NAZANIN, 14, bold=True, color_rgb=palette["text_dark"])

    # Row 1: Advisor & Defense Date
    cell_10 = info_tbl.cell(1, 0)
    cell_10.text = ""
    p_10 = cell_10.text_frame.paragraphs[0]
    apply_p_rtl(p_10, PP_ALIGN.CENTER)
    r_10 = p_10.add_run()
    advisor_text = f"استاد مشاور: {meta.get('advisor', 'استاد مشاور')}" if meta.get("advisor") else ""
    set_run_font(r_10, advisor_text, FONT_NAZANIN, 13, bold=False, color_rgb=palette["text_muted"])

    cell_11 = info_tbl.cell(1, 1)
    cell_11.text = ""
    p_11 = cell_11.text_frame.paragraphs[0]
    apply_p_rtl(p_11, PP_ALIGN.CENTER)
    r_11 = p_11.add_run()
    set_run_font(r_11, f"تاریخ دفاع: {meta.get('defense_date', 'شهریور ۱۴۰۵')}", FONT_NAZANIN, 13, bold=False, color_rgb=palette["text_muted"])

    # Speaker notes
    attach_speaker_notes(slide, slide_data.get("speaker_notes", ""))

def build_committee_slide(prs: Presentation, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, Any]):
    """Slide 2: Committee Directory Cards."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    draw_header_banner(slide, "ارکان پژوهش", slide_data.get("title", "هیئت محترم داوران و اساتید راهنما"), palette)

    cards = slide_data.get("cards", [])
    if not cards:
        cards = [
            {"title": "استاد راهنما", "desc": meta.get("supervisor", "")},
            {"title": "استاد مشاور", "desc": meta.get("advisor", "")},
            {"title": "داور داخلی", "desc": meta.get("internal_examiner", "هیات داوران دانشگاه")},
            {"title": "داور خارجی", "desc": meta.get("external_examiner", "هیات داوران خارجی")}
        ]

    card_count = len(cards)
    if card_count == 4:
        # 2x2 Grid
        coords = [
            (Inches(1.0), Inches(1.6)), (Inches(6.8), Inches(1.6)),
            (Inches(1.0), Inches(4.3)), (Inches(6.8), Inches(4.3))
        ]
        card_w = Inches(5.5)
        card_h = Inches(2.4)
    else:
        # Horizontal stack
        w_avail = 11.733
        card_w = Inches(w_avail / max(1, card_count) - 0.2)
        card_h = Inches(4.5)
        coords = [(Inches(0.8 + i * (card_w.inches + 0.2)), Inches(1.8)) for i in range(card_count)]

    for idx, card_item in enumerate(cards):
        if idx >= len(coords):
            break
        left, top = coords[idx]
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, card_w, card_h)
        box.fill.solid()
        box.fill.fore_color.rgb = palette["card_bg"]
        box.line.color.rgb = palette["secondary"]
        box.line.width = Pt(1.5)

        tf = box.text_frame
        tf.word_wrap = True
        p_title = tf.paragraphs[0]
        apply_p_rtl(p_title, PP_ALIGN.RIGHT)
        p_title.space_after = Pt(8)
        r_title = p_title.add_run()
        set_run_font(r_title, card_item.get("title", ""), FONT_TITR, 16, bold=True, color_rgb=palette["primary"])

        for line in card_item.get("desc", "").split("\n"):
            if not line.strip():
                continue
            p_desc = tf.add_paragraph()
            apply_p_rtl(p_desc, PP_ALIGN.RIGHT)
            p_desc.space_after = Pt(4)
            r_desc = p_desc.add_run()
            set_run_font(r_desc, line.strip(), FONT_NAZANIN, 14, bold=False, color_rgb=palette["text_dark"])

    attach_speaker_notes(slide, slide_data.get("speaker_notes", ""))

def build_cards_slide(prs: Presentation, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, Any]):
    """Standard Cards Slide (2, 3, or 4 visual container boxes)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    draw_header_banner(slide, slide_data.get("category", ""), slide_data.get("title", ""), palette)

    cards = slide_data.get("cards", [])
    num_cards = len(cards)

    if num_cards == 1:
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(1.6), Inches(10.933), Inches(5.0))
        box.fill.solid()
        box.fill.fore_color.rgb = palette["card_bg"]
        box.line.color.rgb = palette["card_border"]
        box.line.width = Pt(1.5)
        tf = box.text_frame
        tf.word_wrap = True
        p_c = tf.paragraphs[0]
        apply_p_rtl(p_c, PP_ALIGN.RIGHT)
        r_c = p_c.add_run()
        set_run_font(r_c, cards[0].get("title", ""), FONT_TITR, 18, bold=True, color_rgb=palette["primary"])
        for line in cards[0].get("desc", "").split("\n"):
            p_l = tf.add_paragraph()
            apply_p_rtl(p_l, PP_ALIGN.RIGHT)
            p_l.space_after = Pt(6)
            r_l = p_l.add_run()
            set_run_font(r_l, line.strip(), FONT_NAZANIN, 15, bold=False, color_rgb=palette["text_dark"])

    elif num_cards in [2, 3]:
        # Horizontal columns
        gap = 0.3
        total_w = 11.733
        card_w = Inches((total_w - (num_cards - 1) * gap) / num_cards)
        card_h = Inches(5.2)

        for i, card_item in enumerate(cards):
            left = Inches(0.8 + i * (card_w.inches + gap))
            box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(1.6), card_w, card_h)
            box.fill.solid()
            box.fill.fore_color.rgb = palette["card_bg"]
            box.line.color.rgb = palette["card_border"]
            box.line.width = Pt(1.5)

            # Colored accent header top on card
            acc = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(1.6), card_w, Inches(0.12))
            acc.fill.solid()
            acc.fill.fore_color.rgb = palette["accent"] if i == 0 else palette["secondary"]
            acc.line.fill.background()

            tf = box.text_frame
            tf.word_wrap = True
            p_head = tf.paragraphs[0]
            apply_p_rtl(p_head, PP_ALIGN.RIGHT)
            p_head.space_after = Pt(8)
            r_head = p_head.add_run()
            set_run_font(r_head, card_item.get("title", ""), FONT_TITR, 16, bold=True, color_rgb=palette["primary"])

            for line in card_item.get("desc", "").split("\n"):
                if not line.strip():
                    continue
                p_body = tf.add_paragraph()
                apply_p_rtl(p_body, PP_ALIGN.RIGHT)
                p_body.space_after = Pt(6)
                r_body = p_body.add_run()
                set_run_font(r_body, line.strip(), FONT_NAZANIN, 14, bold=False, color_rgb=palette["text_dark"])

    elif num_cards >= 4:
        # 2x2 Grid
        grid_coords = [
            (Inches(0.8), Inches(1.5)), (Inches(6.8), Inches(1.5)),
            (Inches(0.8), Inches(4.3)), (Inches(6.8), Inches(4.3))
        ]
        card_w = Inches(5.7)
        card_h = Inches(2.6)

        for i in range(min(4, len(cards))):
            card_item = cards[i]
            left, top = grid_coords[i]
            box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, card_w, card_h)
            box.fill.solid()
            box.fill.fore_color.rgb = palette["card_bg"]
            box.line.color.rgb = palette["card_border"]
            box.line.width = Pt(1.5)

            tf = box.text_frame
            tf.word_wrap = True
            p_head = tf.paragraphs[0]
            apply_p_rtl(p_head, PP_ALIGN.RIGHT)
            p_head.space_after = Pt(4)
            r_head = p_head.add_run()
            set_run_font(r_head, card_item.get("title", ""), FONT_TITR, 15, bold=True, color_rgb=palette["primary"])

            for line in card_item.get("desc", "").split("\n"):
                if not line.strip():
                    continue
                p_body = tf.add_paragraph()
                apply_p_rtl(p_body, PP_ALIGN.RIGHT)
                p_body.space_after = Pt(3)
                r_body = p_body.add_run()
                set_run_font(r_body, line.strip(), FONT_NAZANIN, 13, bold=False, color_rgb=palette["text_dark"])

    attach_speaker_notes(slide, slide_data.get("speaker_notes", ""))

def build_table_slide(prs: Presentation, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, Any]):
    """APA 7 Academic Table Slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    draw_header_banner(slide, slide_data.get("category", ""), slide_data.get("title", ""), palette)

    tbl_data = slide_data.get("table", {})
    headers = tbl_data.get("headers", [])
    rows = tbl_data.get("rows", [])

    if not headers or not rows:
        return

    num_rows = len(rows) + 1
    num_cols = len(headers)

    table_left = Inches(0.8)
    table_top = Inches(1.6)
    table_width = Inches(11.733)
    table_height = Inches(min(5.2, 0.45 * num_rows))

    table_shape = slide.shapes.add_table(num_rows, num_cols, table_left, table_top, table_width, table_height)
    tbl = table_shape.table

    # Format Header Row
    for c_idx, h_text in enumerate(headers):
        cell = tbl.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = palette["tbl_header"]
        cell.text = ""
        p = cell.text_frame.paragraphs[0]
        apply_p_rtl(p, PP_ALIGN.CENTER)
        run = p.add_run()
        set_run_font(run, h_text, FONT_TITR, 13, bold=True, color_rgb=palette["text_light"])

    # Format Data Rows with Zebra Striping
    for r_idx, row_vals in enumerate(rows):
        is_even = (r_idx % 2 == 0)
        row_num = r_idx + 1
        for c_idx, val in enumerate(row_vals):
            if c_idx >= num_cols:
                break
            cell = tbl.cell(row_num, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = palette["tbl_stripe"] if is_even else palette["card_bg"]
            cell.text = ""
            p = cell.text_frame.paragraphs[0]
            apply_p_rtl(p, PP_ALIGN.CENTER)
            run = p.add_run()
            # If numerical / English term, use English font
            val_str = str(val).strip()
            font_to_use = FONT_ENG if any(char.isdigit() or char in "<>=.±" for char in val_str) else FONT_NAZANIN
            set_run_font(run, val_str, font_to_use, 12, bold=False, color_rgb=palette["text_dark"])

    attach_speaker_notes(slide, slide_data.get("speaker_notes", ""))

def build_closing_slide(prs: Presentation, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, Any]):
    """Final Slide: Acknowledgments & Committee Q&A."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # Background full fill
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = palette["primary"]
    bg.line.fill.background()

    # Inner Gold Border Card
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.5), Inches(1.2), Inches(10.333), Inches(5.1))
    card.fill.solid()
    card.fill.fore_color.rgb = palette["card_bg"]
    card.line.color.rgb = palette["accent"]
    card.line.width = Pt(2.5)

    # Title Box
    title_box = slide.shapes.add_textbox(Inches(2.0), Inches(1.8), Inches(9.333), Inches(1.2))
    tf_t = title_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    apply_p_rtl(p_t, PP_ALIGN.CENTER)
    r_t = p_t.add_run()
    set_run_font(r_t, slide_data.get("title", "سپاس و قدردانی"), FONT_TITR, 28, bold=True, color_rgb=palette["primary"])

    # Subtitle / Statement
    sub_box = slide.shapes.add_textbox(Inches(2.2), Inches(3.2), Inches(8.933), Inches(2.2))
    tf_s = sub_box.text_frame
    tf_s.word_wrap = True
    for line in slide_data.get("subtitle", "").split("\n"):
        p_s = tf_s.add_paragraph() if tf_s.paragraphs[0].text else tf_s.paragraphs[0]
        apply_p_rtl(p_s, PP_ALIGN.CENTER)
        p_s.space_after = Pt(8)
        r_s = p_s.add_run()
        set_run_font(r_s, line.strip(), FONT_NAZANIN, 16, bold=False, color_rgb=palette["text_dark"])

    attach_speaker_notes(slide, slide_data.get("speaker_notes", ""))

# ---------------------------------------------------------------------------
# Main Compiler Entrypoint
# ---------------------------------------------------------------------------
def compile_presentation(payload: Dict[str, Any], output_path: str, theme_name: str = "academic_navy"):
    """Compile structured presentation dictionary into .pptx file."""
    prs = Presentation()
    prs.slide_width = Inches(13.333) # 16:9 Widescreen
    prs.slide_height = Inches(7.5)

    palette = PALETTES.get(theme_name, PALETTES["academic_navy"])
    meta = payload.get("meta", {})
    slides = payload.get("slides", [])

    print(f"[*] Compiling {len(slides)} defense slides with theme: '{theme_name}'...")

    for idx, slide_item in enumerate(slides):
        layout = slide_item.get("layout", "cards")
        if layout == "cover":
            build_cover_slide(prs, meta, slide_item, palette)
        elif layout == "committee":
            build_committee_slide(prs, meta, slide_item, palette)
        elif layout == "table":
            build_table_slide(prs, meta, slide_item, palette)
        elif layout == "closing":
            build_closing_slide(prs, meta, slide_item, palette)
        else: # default cards
            build_cards_slide(prs, meta, slide_item, palette)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    prs.save(output_path)
    print(f"[✓] Defense presentation successfully generated at: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="Master Persian Academic Thesis Defense Presentation Compiler")
    parser.add_argument("--json", type=str, help="Path to structured presentation payload JSON")
    parser.add_argument("--output", type=str, default="Defense_Presentation.pptx", help="Path to output .pptx file")
    parser.add_argument("--theme", type=str, default="academic_navy", choices=["academic_navy", "emerald_slate", "royal_burgundy"], help="Color theme")
    parser.add_argument("--title", type=str, help="Thesis title")
    parser.add_argument("--author", type=str, help="Candidate name")
    parser.add_argument("--supervisor", type=str, help="Supervisor name")
    parser.add_argument("--stats-json", type=str, help="Optional path to stats_results.json for auto-table injection")
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

    # Override meta if passed
    if args.title:
        payload.setdefault("meta", {})["title"] = args.title
    if args.author:
        payload.setdefault("meta", {})["author"] = args.author
    if args.supervisor:
        payload.setdefault("meta", {})["supervisor"] = args.supervisor

    compile_presentation(payload, args.output, args.theme)

if __name__ == "__main__":
    main()
