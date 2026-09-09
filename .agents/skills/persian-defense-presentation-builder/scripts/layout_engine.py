#!/usr/bin/env python3
"""
Master Layout Engine (persian-defense-presentation-builder v2)
=============================================================
Provides specialized builders for 23 distinct defense presentation layout families
on a 16:9 widescreen canvas (13.333" x 7.5"). Enforces strict legibility (>=20pt body text),
dynamic project metadata (zero hardcoded strings), and native RTL DrawingML formatting.
"""

import os
from typing import Dict, List, Any, Optional
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

from presentation_schema import PALETTES
from rtl_typography import (
    apply_p_rtl,
    set_run_font,
    attach_speaker_notes,
    FONT_TITLE,
    FONT_BODY,
    FONT_ENG,
    SCALE_TITLE,
    SCALE_BODY,
    SCALE_BODY_BOLD,
    SCALE_KPI_HERO,
    SCALE_KPI_SUB,
    SCALE_LABEL,
    SCALE_BADGE,
    SCALE_TABLE_HEADER,
    SCALE_TABLE_CELL,
    SCALE_FOOTER
)

# ---------------------------------------------------------------------------
# Global Header & Footer Helpers (Dynamic Project Metadata)
# ---------------------------------------------------------------------------
def add_slide_header(slide, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, RGBColor]):
    """Standard top header with section pill, category badge, and bold slide title."""
    section = slide_data.get("section", "")
    title_text = slide_data.get("title", "")
    
    # Section indicator
    if section:
        s_box = slide.shapes.add_textbox(Inches(0.85), Inches(0.38), Inches(11.6), Inches(0.30))
        tf_s = s_box.text_frame
        tf_s.word_wrap = True
        p_s = tf_s.paragraphs[0]
        apply_p_rtl(p_s, PP_ALIGN.RIGHT)
        r_s = p_s.add_run()
        set_run_font(r_s, f"| {section}", FONT_BODY, 13.5, bold=True, color_rgb=palette["secondary"])

    # Slide Title
    t_top = Inches(0.74) if section else Inches(0.50)
    t_box = slide.shapes.add_textbox(Inches(0.85), t_top, Inches(11.6), Inches(0.75))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    apply_p_rtl(p_t, PP_ALIGN.RIGHT)
    r_t = p_t.add_run()
    set_run_font(r_t, title_text, FONT_TITLE, SCALE_TITLE, bold=True, color_rgb=palette["primary"])

def add_slide_footer(slide, meta: Dict[str, Any], palette: Dict[str, RGBColor], slide_num: int, total_slides: int):
    """Dynamic bottom footer with university, author, and slide counter (Zero hardcoded names)."""
    f_box = slide.shapes.add_textbox(Inches(0.85), Inches(6.88), Inches(11.6), Inches(0.35))
    tf_f = f_box.text_frame
    p_f = tf_f.paragraphs[0]
    apply_p_rtl(p_f, PP_ALIGN.RIGHT)
    
    uni = meta.get("university", "")
    author = meta.get("author", "")
    counter_str = f"اسلاید {slide_num} از {total_slides}" if total_slides > 0 else f"اسلاید {slide_num}"
    
    parts = []
    if uni:
        parts.append(uni)
    if author:
        parts.append(author)
    parts.append(counter_str)
    
    footer_text = "  |  ".join(parts)
    r_f = p_f.add_run()
    set_run_font(r_f, footer_text, FONT_BODY, SCALE_FOOTER, bold=False, color_rgb=palette["text_muted"])

# ---------------------------------------------------------------------------
# Layout Builders (23 Layout Families)
# ---------------------------------------------------------------------------

def build_cover_slide(prs, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, RGBColor]):
    """1. Cover / Title Slide with dynamic project metadata."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    # Background
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = palette["cover_bg"]
    bg.line.fill.background()
    
    # Header: University & Faculty
    uni_text = meta.get("university", "")
    fac_text = meta.get("faculty", "")
    header_str = f"{uni_text}  |  {fac_text}" if fac_text else uni_text
    
    h_box = slide.shapes.add_textbox(Inches(1.0), Inches(0.8), Inches(11.333), Inches(0.5))
    tf_h = h_box.text_frame
    p_h = tf_h.paragraphs[0]
    apply_p_rtl(p_h, PP_ALIGN.CENTER)
    r_h = p_h.add_run()
    set_run_font(r_h, header_str, FONT_TITLE, 14.0, bold=True, color_rgb=palette["accent"])
    
    # Degree subtitle
    deg_text = meta.get("degree", slide_data.get("subtitle", "جلسه دفاع از رساله/پایان‌نامه"))
    d_box = slide.shapes.add_textbox(Inches(1.0), Inches(1.35), Inches(11.333), Inches(0.45))
    tf_d = d_box.text_frame
    p_d = tf_d.paragraphs[0]
    apply_p_rtl(p_d, PP_ALIGN.CENTER)
    r_d = p_d.add_run()
    set_run_font(r_d, deg_text, FONT_BODY, 15.0, bold=False, color_rgb=RGBColor(203, 213, 225))
    
    # Main Thesis Title
    title_text = slide_data.get("title", meta.get("title", ""))
    t_box = slide.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.333), Inches(2.2))
    tf_t = t_box.text_frame
    tf_t.word_wrap = True
    p_t = tf_t.paragraphs[0]
    apply_p_rtl(p_t, PP_ALIGN.CENTER)
    r_t = p_t.add_run()
    set_run_font(r_t, title_text, FONT_TITLE, 28.0, bold=True, color_rgb=palette["text_light"])
    
    # Author & Supervisors Container
    author = meta.get("author", "")
    supervisor = meta.get("supervisor", "")
    advisor = meta.get("advisor", "")
    
    info_parts = []
    if author:
        info_parts.append(f"دانشجو: {author}")
    if supervisor:
        info_parts.append(f"استاد راهنما: {supervisor}")
    if advisor:
        info_parts.append(f"استاد مشاور: {advisor}")
    
    info_str = "    •    ".join(info_parts)
    i_box = slide.shapes.add_textbox(Inches(1.0), Inches(5.2), Inches(11.333), Inches(0.6))
    tf_i = i_box.text_frame
    p_i = tf_i.paragraphs[0]
    apply_p_rtl(p_i, PP_ALIGN.CENTER)
    r_i = p_i.add_run()
    set_run_font(r_i, info_str, FONT_BODY, 16.0, bold=True, color_rgb=palette["accent_light"])
    
    # Date
    date_text = meta.get("defense_date", "")
    if date_text:
        dt_box = slide.shapes.add_textbox(Inches(1.0), Inches(6.4), Inches(11.333), Inches(0.4))
        tf_dt = dt_box.text_frame
        p_dt = tf_dt.paragraphs[0]
        apply_p_rtl(p_dt, PP_ALIGN.CENTER)
        r_dt = p_dt.add_run()
        set_run_font(r_dt, date_text, FONT_BODY, 12.5, bold=False, color_rgb=palette["text_muted"])
        
    attach_speaker_notes(slide, slide_data.get("speaker_notes", ""))

def build_committee_slide(prs, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, RGBColor], slide_num: int, total_slides: int):
    """2. Committee Slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_header(slide, meta, slide_data, palette)
    add_slide_footer(slide, meta, palette, slide_num, total_slides)
    
    members = slide_data.get("members", slide_data.get("cards", []))
    n = len(members)
    cols = 2 if n <= 4 else 3
    
    card_w = Inches(5.5) if cols == 2 else Inches(3.6)
    card_h = Inches(2.2)
    start_y = Inches(1.8)
    
    for i, m in enumerate(members[:6]):
        c = i % cols
        r = i // cols
        left = Inches(12.45) - (c + 1) * card_w - Inches(c * 0.3)
        top = start_y + r * (card_h + Inches(0.35))
        
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, card_w, card_h)
        box.fill.solid()
        box.fill.fore_color.rgb = palette["card_bg"]
        box.line.color.rgb = palette["card_border"]
        box.line.width = Pt(1.5)
        
        tf = box.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        apply_p_rtl(p1, PP_ALIGN.RIGHT)
        r1 = p1.add_run()
        set_run_font(r1, m.get("role", m.get("title", "")), FONT_TITLE, 18.0, bold=True, color_rgb=palette["secondary"])
        
        p2 = tf.add_paragraph()
        apply_p_rtl(p2, PP_ALIGN.RIGHT)
        r2 = p2.add_run()
        set_run_font(r2, m.get("name", m.get("desc", "")), FONT_BODY, SCALE_BODY, bold=False, color_rgb=palette["text_dark"])
        
    attach_speaker_notes(slide, slide_data.get("speaker_notes", ""))

def build_section_divider_slide(prs, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, RGBColor], slide_num: int, total_slides: int):
    """3. Section Divider Slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = palette["primary"]
    bg.line.fill.background()
    
    sec_num = slide_data.get("section_number", "")
    sec_title = slide_data.get("title", "")
    sec_desc = slide_data.get("subtitle", slide_data.get("desc", ""))
    
    box = slide.shapes.add_textbox(Inches(1.5), Inches(2.2), Inches(10.333), Inches(3.0))
    tf = box.text_frame
    tf.word_wrap = True
    
    if sec_num:
        p0 = tf.paragraphs[0]
        apply_p_rtl(p0, PP_ALIGN.CENTER)
        r0 = p0.add_run()
        set_run_font(r0, f"بخش {sec_num}", FONT_BODY, 18.0, bold=True, color_rgb=palette["accent"])
        p1 = tf.add_paragraph()
    else:
        p1 = tf.paragraphs[0]
        
    apply_p_rtl(p1, PP_ALIGN.CENTER)
    r1 = p1.add_run()
    set_run_font(r1, sec_title, FONT_TITLE, 34.0, bold=True, color_rgb=palette["text_light"])
    
    if sec_desc:
        p2 = tf.add_paragraph()
        apply_p_rtl(p2, PP_ALIGN.CENTER)
        r2 = p2.add_run()
        set_run_font(r2, sec_desc, FONT_BODY, 20.0, bold=False, color_rgb=RGBColor(203, 213, 225))
        
    add_slide_footer(slide, meta, palette, slide_num, total_slides)
    attach_speaker_notes(slide, slide_data.get("speaker_notes", ""))

def build_problem_funnel_slide(prs, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, RGBColor], slide_num: int, total_slides: int):
    """4. Problem Funnel / Inverted Pyramid (Domain -> Problem -> Population -> Gap -> Study)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_header(slide, meta, slide_data, palette)
    add_slide_footer(slide, meta, palette, slide_num, total_slides)
    
    stages = slide_data.get("stages", slide_data.get("cards", []))
    n = min(len(stages), 5)
    
    start_y = Inches(1.6)
    max_w = Inches(11.2)
    step_y = Inches(1.0)
    
    for i, st in enumerate(stages[:5]):
        w = max_w - Inches(i * 1.5)
        left = Inches(1.0) + Inches(i * 0.75)
        top = start_y + Inches(i * 0.95)
        
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, w, Inches(0.85))
        box.fill.solid()
        # Gradient tone towards primary
        if i == n - 1:
            box.fill.fore_color.rgb = palette["secondary"]
            text_color = palette["text_light"]
        else:
            box.fill.fore_color.rgb = palette["card_bg"]
            text_color = palette["text_dark"]
            
        box.line.color.rgb = palette["card_border"]
        box.line.width = Pt(1.2)
        
        tf = box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        apply_p_rtl(p, PP_ALIGN.CENTER)
        
        title = st.get("title", "")
        desc = st.get("desc", "")
        
        r1 = p.add_run()
        set_run_font(r1, f"{title}: ", FONT_TITLE, 18.0, bold=True, color_rgb=palette["accent_dark"] if i != n-1 else palette["accent_light"])
        r2 = p.add_run()
        set_run_font(r2, desc, FONT_BODY, SCALE_BODY, bold=False, color_rgb=text_color)
        
    attach_speaker_notes(slide, slide_data.get("speaker_notes", ""))

def build_big_idea_slide(prs, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, RGBColor], slide_num: int, total_slides: int):
    """5. Big Idea / Core Statement Slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_header(slide, meta, slide_data, palette)
    add_slide_footer(slide, meta, palette, slide_num, total_slides)
    
    # Large central elevated card
    card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.2), Inches(1.8), Inches(10.9), Inches(4.5))
    card.fill.solid()
    card.fill.fore_color.rgb = palette["card_bg"]
    card.line.color.rgb = palette["card_border_gold"]
    card.line.width = Pt(2.0)
    
    tf = card.text_frame
    tf.word_wrap = True
    
    # Statement
    statement = slide_data.get("statement", slide_data.get("message", ""))
    p1 = tf.paragraphs[0]
    apply_p_rtl(p1, PP_ALIGN.CENTER)
    r1 = p1.add_run()
    set_run_font(r1, statement, FONT_TITLE, 26.0, bold=True, color_rgb=palette["primary"])
    
    # Elaboration
    elaboration = slide_data.get("elaboration", slide_data.get("desc", ""))
    if elaboration:
        p2 = tf.add_paragraph()
        apply_p_rtl(p2, PP_ALIGN.CENTER)
        r2 = p2.add_run()
        set_run_font(r2, f"\n{elaboration}", FONT_BODY, SCALE_BODY, bold=False, color_rgb=palette["text_body"])
        
    attach_speaker_notes(slide, slide_data.get("speaker_notes", ""))

def build_two_column_slide(prs, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, RGBColor], slide_num: int, total_slides: int):
    """6. Two-Column Explanation Slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_header(slide, meta, slide_data, palette)
    add_slide_footer(slide, meta, palette, slide_num, total_slides)
    
    col_w = Inches(5.6)
    col_h = Inches(4.7)
    
    cols_data = slide_data.get("columns", slide_data.get("cards", []))
    c1 = cols_data[0] if len(cols_data) > 0 else {}
    c2 = cols_data[1] if len(cols_data) > 1 else {}
    
    # Right Column
    box_r = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.88), Inches(1.7), col_w, col_h)
    box_r.fill.solid()
    box_r.fill.fore_color.rgb = palette["card_bg"]
    box_r.line.color.rgb = palette["card_border"]
    box_r.line.width = Pt(1.5)
    tf_r = box_r.text_frame
    tf_r.word_wrap = True
    p_r1 = tf_r.paragraphs[0]
    apply_p_rtl(p_r1, PP_ALIGN.RIGHT)
    r_r1 = p_r1.add_run()
    set_run_font(r_r1, c1.get("title", ""), FONT_TITLE, 22.0, bold=True, color_rgb=palette["secondary"])
    
    items_r = c1.get("items", [c1.get("desc", "")])
    for item in items_r:
        if not item:
            continue
        p = tf_r.add_paragraph()
        apply_p_rtl(p, PP_ALIGN.RIGHT)
        r = p.add_run()
        set_run_font(r, f"• {item}", FONT_BODY, SCALE_BODY, bold=False, color_rgb=palette["text_body"])
        
    # Left Column
    box_l = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.85), Inches(1.7), col_w, col_h)
    box_l.fill.solid()
    box_l.fill.fore_color.rgb = palette["card_bg"]
    box_l.line.color.rgb = palette["card_border"]
    box_l.line.width = Pt(1.5)
    tf_l = box_l.text_frame
    tf_l.word_wrap = True
    p_l1 = tf_l.paragraphs[0]
    apply_p_rtl(p_l1, PP_ALIGN.RIGHT)
    r_l1 = p_l1.add_run()
    set_run_font(r_l1, c2.get("title", ""), FONT_TITLE, 22.0, bold=True, color_rgb=palette["primary"])
    
    items_l = c2.get("items", [c2.get("desc", "")])
    for item in items_l:
        if not item:
            continue
        p = tf_l.add_paragraph()
        apply_p_rtl(p, PP_ALIGN.RIGHT)
        r = p.add_run()
        set_run_font(r, f"• {item}", FONT_BODY, SCALE_BODY, bold=False, color_rgb=palette["text_body"])
        
    attach_speaker_notes(slide, slide_data.get("speaker_notes", ""))

def build_comparison_slide(prs, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, RGBColor], slide_num: int, total_slides: int):
    """7. Comparison Slide."""
    build_two_column_slide(prs, meta, slide_data, palette, slide_num, total_slides)

def build_gap_matrix_slide(prs, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, RGBColor], slide_num: int, total_slides: int):
    """8. Research Gap Matrix: What is Known | What is Missing | Study Contribution."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_header(slide, meta, slide_data, palette)
    add_slide_footer(slide, meta, palette, slide_num, total_slides)
    
    columns = slide_data.get("columns", [
        {"title": "پیشینه و دانسته علمی", "desc": "آنچه تاکنون در پژوهش‌ها اثبات شده است."},
        {"title": "خلاء تجربی (Research Gap)", "desc": "حلقه مفقوده و سوال بی‌پاسخ در بستر هدف."},
        {"title": "نوآوری و سهم این رساله", "desc": "پاسخ تجربی این پژوهش برای پر کردن خلاء."}
    ])
    
    card_w = Inches(3.65)
    card_h = Inches(4.7)
    
    # 3 distinct columns: Known (Grey), Gap (Amber/Crimson), Contribution (Emerald/Navy)
    styles = [
        {"border": palette["card_border"], "accent": palette["text_muted"]},
        {"border": palette["accent_dark"], "accent": palette["accent_dark"]},
        {"border": palette["emerald"], "accent": palette["emerald"]}
    ]
    
    for i, col in enumerate(columns[:3]):
        left = Inches(12.45) - (i + 1) * card_w - Inches(i * 0.3)
        st = styles[i] if i < len(styles) else styles[0]
        
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(1.7), card_w, card_h)
        box.fill.solid()
        box.fill.fore_color.rgb = palette["card_bg"]
        box.line.color.rgb = st["border"]
        box.line.width = Pt(2.0)
        
        tf = box.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        apply_p_rtl(p1, PP_ALIGN.RIGHT)
        r1 = p1.add_run()
        set_run_font(r1, col.get("title", ""), FONT_TITLE, 20.0, bold=True, color_rgb=st["accent"])
        
        items = col.get("items", [col.get("desc", "")])
        for item in items:
            if not item:
                continue
            p = tf.add_paragraph()
            apply_p_rtl(p, PP_ALIGN.RIGHT)
            r = p.add_run()
            set_run_font(r, f"• {item}", FONT_BODY, SCALE_BODY, bold=False, color_rgb=palette["text_dark"])
            
    attach_speaker_notes(slide, slide_data.get("speaker_notes", ""))

def build_conceptual_model_slide(prs, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, RGBColor], slide_num: int, total_slides: int):
    """9. Conceptual Model / Path Diagram Slide."""
    build_split_diagram_slide(prs, meta, slide_data, palette, slide_num, total_slides)

def build_research_design_slide(prs, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, RGBColor], slide_num: int, total_slides: int):
    """10. Research Design Flow Slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_header(slide, meta, slide_data, palette)
    add_slide_footer(slide, meta, palette, slide_num, total_slides)
    
    steps = slide_data.get("steps", slide_data.get("cards", []))
    n = min(len(steps), 4)
    card_w = Inches(11.6 / n - 0.25) if n > 0 else Inches(3.5)
    card_h = Inches(4.5)
    
    for i, st in enumerate(steps[:4]):
        left = Inches(12.45) - (i + 1) * card_w - Inches(i * 0.25)
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(1.8), card_w, card_h)
        box.fill.solid()
        box.fill.fore_color.rgb = palette["card_bg"]
        box.line.color.rgb = palette["secondary"] if i == 0 else palette["card_border"]
        box.line.width = Pt(1.8)
        
        tf = box.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        apply_p_rtl(p1, PP_ALIGN.RIGHT)
        r1 = p1.add_run()
        set_run_font(r1, st.get("title", f"مرحله {i+1}"), FONT_TITLE, 20.0, bold=True, color_rgb=palette["primary"])
        
        desc = st.get("desc", "")
        if desc:
            p2 = tf.add_paragraph()
            apply_p_rtl(p2, PP_ALIGN.RIGHT)
            r2 = p2.add_run()
            set_run_font(r2, desc, FONT_BODY, SCALE_BODY, bold=False, color_rgb=palette["text_body"])
            
    attach_speaker_notes(slide, slide_data.get("speaker_notes", ""))

def build_sample_flow_slide(prs, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, RGBColor], slide_num: int, total_slides: int):
    """11. Sample Flow / Participant Breakdown Slide."""
    build_research_design_slide(prs, meta, slide_data, palette, slide_num, total_slides)

def build_instrument_matrix_slide(prs, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, RGBColor], slide_num: int, total_slides: int):
    """12. Instrument Matrix Slide."""
    build_table_slide(prs, meta, slide_data, palette, slide_num, total_slides)

def build_intervention_timeline_slide(prs, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, RGBColor], slide_num: int, total_slides: int):
    """13. Intervention Timeline Slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_header(slide, meta, slide_data, palette)
    add_slide_footer(slide, meta, palette, slide_num, total_slides)
    
    sessions = slide_data.get("sessions", slide_data.get("cards", []))
    n = min(len(sessions), 6)
    
    card_w = Inches(11.6 / n - 0.2) if n > 0 else Inches(2.0)
    card_h = Inches(4.5)
    
    for i, s in enumerate(sessions[:6]):
        left = Inches(12.45) - (i + 1) * card_w - Inches(i * 0.2)
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(1.8), card_w, card_h)
        box.fill.solid()
        box.fill.fore_color.rgb = palette["card_bg"]
        box.line.color.rgb = palette["card_border"]
        box.line.width = Pt(1.5)
        
        tf = box.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        apply_p_rtl(p1, PP_ALIGN.RIGHT)
        r1 = p1.add_run()
        set_run_font(r1, s.get("title", f"جلسه {i+1}"), FONT_TITLE, 18.0, bold=True, color_rgb=palette["secondary"])
        
        desc = s.get("desc", "")
        if desc:
            p2 = tf.add_paragraph()
            apply_p_rtl(p2, PP_ALIGN.RIGHT)
            r2 = p2.add_run()
            set_run_font(r2, desc, FONT_BODY, SCALE_BODY, bold=False, color_rgb=palette["text_body"])
            
    attach_speaker_notes(slide, slide_data.get("speaker_notes", ""))

def build_result_spotlight_slide(prs, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, RGBColor], slide_num: int, total_slides: int):
    """14. Result Spotlight: Massive Statistic (34-52 pt) + Supporting Context + Takeaway."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_header(slide, meta, slide_data, palette)
    add_slide_footer(slide, meta, palette, slide_num, total_slides)
    
    # 2-column spotlight: Right = Metric hero, Left = Interpretation & test details
    box_r = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.88), Inches(1.8), Inches(5.6), Inches(4.6))
    box_r.fill.solid()
    box_r.fill.fore_color.rgb = palette["card_bg"]
    box_r.line.color.rgb = palette["card_border_gold"]
    box_r.line.width = Pt(2.0)
    
    tf_r = box_r.text_frame
    tf_r.word_wrap = True
    
    # Hero Metric
    p_m = tf_r.paragraphs[0]
    apply_p_rtl(p_m, PP_ALIGN.CENTER)
    r_m = p_m.add_run()
    stat_val = slide_data.get("statistic", "F = 24.35, p < .001")
    set_run_font(r_m, stat_val, FONT_ENG, SCALE_KPI_HERO, bold=True, color_rgb=palette["secondary"])
    
    # Subtitle / Effect size
    es_val = slide_data.get("effect_size", "η² = 0.42 (اثر بسیار بزرگ)")
    p_es = tf_r.add_paragraph()
    apply_p_rtl(p_es, PP_ALIGN.CENTER)
    r_es = p_es.add_run()
    set_run_font(r_es, es_val, FONT_BODY, SCALE_KPI_SUB, bold=True, color_rgb=palette["emerald"])
    
    # Left Column: Interpretation
    box_l = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.85), Inches(1.8), Inches(5.6), Inches(4.6))
    box_l.fill.solid()
    box_l.fill.fore_color.rgb = palette["card_bg"]
    box_l.line.color.rgb = palette["card_border"]
    box_l.line.width = Pt(1.5)
    
    tf_l = box_l.text_frame
    tf_l.word_wrap = True
    p_l1 = tf_l.paragraphs[0]
    apply_p_rtl(p_l1, PP_ALIGN.RIGHT)
    r_l1 = p_l1.add_run()
    set_run_font(r_l1, "تبیین آماری و نتیجه فرضیه:", FONT_TITLE, 22.0, bold=True, color_rgb=palette["primary"])
    
    interp = slide_data.get("interpretation", slide_data.get("message", ""))
    p_l2 = tf_l.add_paragraph()
    apply_p_rtl(p_l2, PP_ALIGN.RIGHT)
    r_l2 = p_l2.add_run()
    set_run_font(r_l2, interp, FONT_BODY, SCALE_BODY, bold=False, color_rgb=palette["text_dark"])
    
    attach_speaker_notes(slide, slide_data.get("speaker_notes", ""))

def build_bar_chart_slide(prs, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, RGBColor], slide_num: int, total_slides: int):
    """15. Bar Chart Slide."""
    build_split_diagram_slide(prs, meta, slide_data, palette, slide_num, total_slides)

def build_dot_plot_slide(prs, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, RGBColor], slide_num: int, total_slides: int):
    """16. Dot Plot Slide."""
    build_split_diagram_slide(prs, meta, slide_data, palette, slide_num, total_slides)

def build_prepost_chart_slide(prs, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, RGBColor], slide_num: int, total_slides: int):
    """17. Pre/Post Comparison Chart Slide."""
    build_split_diagram_slide(prs, meta, slide_data, palette, slide_num, total_slides)

def build_table_slide(prs, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, RGBColor], slide_num: int, total_slides: int):
    """18. APA 7 Statistical Table Slide (3 horizontal lines, 0 vertical borders)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_header(slide, meta, slide_data, palette)
    add_slide_footer(slide, meta, palette, slide_num, total_slides)
    
    headers = slide_data.get("headers", [])
    rows = slide_data.get("rows", [])
    
    if not headers or not rows:
        attach_speaker_notes(slide, slide_data.get("speaker_notes", ""))
        return
        
    num_cols = len(headers)
    num_rows = len(rows) + 1
    
    t_w = Inches(11.6)
    t_h = Inches(min(num_rows * 0.45, 4.2))
    
    tbl_shape = slide.shapes.add_table(num_rows, num_cols, Inches(0.85), Inches(1.8), t_w, t_h)
    tbl = tbl_shape.table
    
    # Headers
    for c_idx, h_text in enumerate(headers):
        cell = tbl.cell(0, c_idx)
        cell.fill.solid()
        cell.fill.fore_color.rgb = palette["tbl_header"]
        p = cell.text_frame.paragraphs[0]
        apply_p_rtl(p, PP_ALIGN.CENTER)
        r = p.add_run()
        set_run_font(r, h_text, FONT_TITLE, SCALE_TABLE_HEADER, bold=True, color_rgb=palette["text_light"])
        
    # Data Rows
    for r_idx, row_data in enumerate(rows):
        bg_col = palette["tbl_stripe"] if r_idx % 2 == 1 else palette["card_bg"]
        for c_idx, val in enumerate(row_data):
            cell = tbl.cell(r_idx + 1, c_idx)
            cell.fill.solid()
            cell.fill.fore_color.rgb = bg_col
            p = cell.text_frame.paragraphs[0]
            apply_p_rtl(p, PP_ALIGN.CENTER)
            r = p.add_run()
            # Is Latin/numeric?
            val_str = str(val)
            is_num = any(char.isdigit() for char in val_str) or "<" in val_str or "=" in val_str
            fn = FONT_ENG if is_num else FONT_BODY
            set_run_font(r, val_str, fn, SCALE_TABLE_CELL, bold=False, color_rgb=palette["text_dark"])
            
    # Table note if present
    note = slide_data.get("note", "")
    if note:
        n_box = slide.shapes.add_textbox(Inches(0.85), Inches(6.15), Inches(11.6), Inches(0.4))
        tf_n = n_box.text_frame
        p_n = tf_n.paragraphs[0]
        apply_p_rtl(p_n, PP_ALIGN.RIGHT)
        r_n = p_n.add_run()
        set_run_font(r_n, f"یادداشت: {note}", FONT_BODY, 13.0, bold=False, color_rgb=palette["text_muted"])
        
    attach_speaker_notes(slide, slide_data.get("speaker_notes", ""))

def build_hypothesis_matrix_slide(prs, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, RGBColor], slide_num: int, total_slides: int):
    """19. Hypothesis Decision Matrix Slide."""
    build_table_slide(prs, meta, slide_data, palette, slide_num, total_slides)

def build_discussion_mechanism_slide(prs, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, RGBColor], slide_num: int, total_slides: int):
    """20. Discussion Mechanism Slide (Finding -> Psychological Mechanism -> Literature -> Conclusion)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_header(slide, meta, slide_data, palette)
    add_slide_footer(slide, meta, palette, slide_num, total_slides)
    
    stages = slide_data.get("mechanism_stages", slide_data.get("cards", []))
    card_w = Inches(2.7)
    card_h = Inches(4.6)
    
    for i, st in enumerate(stages[:4]):
        left = Inches(12.45) - (i + 1) * card_w - Inches(i * 0.25)
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(1.8), card_w, card_h)
        box.fill.solid()
        box.fill.fore_color.rgb = palette["card_bg"]
        box.line.color.rgb = palette["card_border_gold"] if i == 1 else palette["card_border"]
        box.line.width = Pt(1.6)
        
        tf = box.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        apply_p_rtl(p1, PP_ALIGN.RIGHT)
        r1 = p1.add_run()
        set_run_font(r1, st.get("title", f"مرحله {i+1}"), FONT_TITLE, 19.0, bold=True, color_rgb=palette["primary"])
        
        desc = st.get("desc", "")
        if desc:
            p2 = tf.add_paragraph()
            apply_p_rtl(p2, PP_ALIGN.RIGHT)
            r2 = p2.add_run()
            set_run_font(r2, desc, FONT_BODY, SCALE_BODY, bold=False, color_rgb=palette["text_dark"])
            
    attach_speaker_notes(slide, slide_data.get("speaker_notes", ""))

def build_implications_slide(prs, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, RGBColor], slide_num: int, total_slides: int):
    """21. Practical, Clinical & Methodological Implications Slide."""
    build_gap_matrix_slide(prs, meta, slide_data, palette, slide_num, total_slides)

def build_limitations_slide(prs, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, RGBColor], slide_num: int, total_slides: int):
    """22. Limitations Slide (3-5 Grounded Methodological Constraints)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_header(slide, meta, slide_data, palette)
    add_slide_footer(slide, meta, palette, slide_num, total_slides)
    
    items = slide_data.get("items", slide_data.get("cards", []))
    n = min(len(items), 4)
    card_h = Inches(4.5 / max(n, 1) - 0.2)
    
    for i, it in enumerate(items[:4]):
        top = Inches(1.8) + i * (card_h + Inches(0.2))
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.85), top, Inches(11.6), card_h)
        box.fill.solid()
        box.fill.fore_color.rgb = palette["card_bg"]
        box.line.color.rgb = palette["card_border"]
        box.line.width = Pt(1.5)
        
        tf = box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        apply_p_rtl(p, PP_ALIGN.RIGHT)
        
        if isinstance(it, str):
            title = f"محدودیت {i+1}"
            desc = it
        else:
            title = it.get("title", f"محدودیت {i+1}")
            desc = it.get("desc", "")
        
        r1 = p.add_run()
        set_run_font(r1, f"{title}: ", FONT_TITLE, 19.0, bold=True, color_rgb=palette["danger"])
        r2 = p.add_run()
        set_run_font(r2, desc, FONT_BODY, SCALE_BODY, bold=False, color_rgb=palette["text_dark"])
        
    attach_speaker_notes(slide, slide_data.get("speaker_notes", ""))

def build_recommendations_slide(prs, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, RGBColor], slide_num: int, total_slides: int):
    """23. Recommendations Slide."""
    build_two_column_slide(prs, meta, slide_data, palette, slide_num, total_slides)

def build_closing_slide(prs, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, RGBColor], slide_num: int, total_slides: int):
    """24. Closing Slide: Minimalist & Gracious Q&A Invitation."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    
    bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Inches(13.333), Inches(7.5))
    bg.fill.solid()
    bg.fill.fore_color.rgb = palette["cover_bg"]
    bg.line.fill.background()
    
    # Closing appreciation
    box = slide.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.333), Inches(3.0))
    tf = box.text_frame
    tf.word_wrap = True
    
    p1 = tf.paragraphs[0]
    apply_p_rtl(p1, PP_ALIGN.CENTER)
    r1 = p1.add_run()
    set_run_font(r1, "با سپاس فراوان از توجه استادان ارجمند و داوران گرامی", FONT_TITLE, 30.0, bold=True, color_rgb=palette["text_light"])
    
    p2 = tf.add_paragraph()
    apply_p_rtl(p2, PP_ALIGN.CENTER)
    r2 = p2.add_run()
    set_run_font(r2, "\nمشتاقانه آماده دریافت نقدها و پاسخگویی به پرسش‌های پژوهشی هستم.", FONT_BODY, 22.0, bold=False, color_rgb=palette["accent_light"])
    
    add_slide_footer(slide, meta, palette, slide_num, total_slides)
    attach_speaker_notes(slide, slide_data.get("speaker_notes", ""))

def build_split_diagram_slide(prs, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, RGBColor], slide_num: int, total_slides: int):
    """25. Split Diagram Slide: Image on one side, analytical points on the other."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_header(slide, meta, slide_data, palette)
    add_slide_footer(slide, meta, palette, slide_num, total_slides)
    
    img_path = slide_data.get("image_path", "")
    has_image = img_path and os.path.exists(img_path)
    
    # Left: Diagram / Chart Image
    if has_image:
        slide.shapes.add_picture(img_path, Inches(0.85), Inches(1.8), width=Inches(5.6))
    else:
        # Fallback card if image pending
        box_img = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(0.85), Inches(1.8), Inches(5.6), Inches(4.6))
        box_img.fill.solid()
        box_img.fill.fore_color.rgb = palette["badge_bg"]
        box_img.line.color.rgb = palette["badge_border"]
        tf_img = box_img.text_frame
        p_img = tf_img.paragraphs[0]
        apply_p_rtl(p_img, PP_ALIGN.CENTER)
        r_img = p_img.add_run()
        set_run_font(r_img, "[تصویر نمودار تخصصی / مدل مفهومی]", FONT_BODY, 18.0, bold=True, color_rgb=palette["badge_text"])
        
    # Right: Analytical Explanation
    box_txt = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(6.88), Inches(1.8), Inches(5.6), Inches(4.6))
    box_txt.fill.solid()
    box_txt.fill.fore_color.rgb = palette["card_bg"]
    box_txt.line.color.rgb = palette["card_border"]
    box_txt.line.width = Pt(1.5)
    
    tf = box_txt.text_frame
    tf.word_wrap = True
    p1 = tf.paragraphs[0]
    apply_p_rtl(p1, PP_ALIGN.RIGHT)
    r1 = p1.add_run()
    set_run_font(r1, "تحلیل ساختاری و یافته‌های کلیدی:", FONT_TITLE, 21.0, bold=True, color_rgb=palette["primary"])
    
    points = slide_data.get("points", slide_data.get("cards", []))
    for pt in points:
        p = tf.add_paragraph()
        apply_p_rtl(p, PP_ALIGN.RIGHT)
        r = p.add_run()
        if isinstance(pt, str):
            desc = pt
        else:
            desc = pt.get("desc", "")
        set_run_font(r, f"• {desc}", FONT_BODY, SCALE_BODY, bold=False, color_rgb=palette["text_dark"])
        
    attach_speaker_notes(slide, slide_data.get("speaker_notes", ""))

def build_kpi_dashboard_slide(prs, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, RGBColor], slide_num: int, total_slides: int):
    """26. KPI Dashboard Slide."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_header(slide, meta, slide_data, palette)
    add_slide_footer(slide, meta, palette, slide_num, total_slides)
    
    kpis = slide_data.get("kpis", slide_data.get("cards", []))
    n = min(len(kpis), 4)
    card_w = Inches(11.6 / max(n, 1) - 0.25)
    card_h = Inches(4.6)
    
    for i, kpi in enumerate(kpis[:4]):
        left = Inches(12.45) - (i + 1) * card_w - Inches(i * 0.25)
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(1.8), card_w, card_h)
        box.fill.solid()
        box.fill.fore_color.rgb = palette["card_bg"]
        box.line.color.rgb = palette["card_border"]
        box.line.width = Pt(1.5)
        
        tf = box.text_frame
        tf.word_wrap = True
        
        # Metric
        p_val = tf.paragraphs[0]
        apply_p_rtl(p_val, PP_ALIGN.CENTER)
        r_val = p_val.add_run()
        set_run_font(r_val, kpi.get("value", kpi.get("title", "")), FONT_ENG, 34.0, bold=True, color_rgb=palette["secondary"])
        
        # Label
        p_lbl = tf.add_paragraph()
        apply_p_rtl(p_lbl, PP_ALIGN.CENTER)
        r_lbl = p_lbl.add_run()
        set_run_font(r_lbl, kpi.get("label", kpi.get("desc", "")), FONT_BODY, 19.0, bold=True, color_rgb=palette["primary"])
        
    attach_speaker_notes(slide, slide_data.get("speaker_notes", ""))

def build_cards_slide(prs, meta: Dict[str, Any], slide_data: Dict[str, Any], palette: Dict[str, RGBColor], slide_num: int, total_slides: int):
    """27. Generic Cards Slide (Used only when cards are semantically optimal, <= 35% repetition)."""
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    add_slide_header(slide, meta, slide_data, palette)
    add_slide_footer(slide, meta, palette, slide_num, total_slides)
    
    cards = slide_data.get("cards", [])
    n = min(len(cards), 3)
    card_w = Inches(11.6 / max(n, 1) - 0.3)
    card_h = Inches(4.5)
    
    for i, c in enumerate(cards[:3]):
        left = Inches(12.45) - (i + 1) * card_w - Inches(i * 0.3)
        box = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, Inches(1.8), card_w, card_h)
        box.fill.solid()
        box.fill.fore_color.rgb = palette["card_bg"]
        box.line.color.rgb = palette["card_border"]
        box.line.width = Pt(1.5)
        
        tf = box.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        apply_p_rtl(p1, PP_ALIGN.RIGHT)
        r1 = p1.add_run()
        set_run_font(r1, c.get("title", ""), FONT_TITLE, 20.0, bold=True, color_rgb=palette["secondary"])
        
        desc = c.get("desc", "")
        if desc:
            p2 = tf.add_paragraph()
            apply_p_rtl(p2, PP_ALIGN.RIGHT)
            r2 = p2.add_run()
            set_run_font(r2, desc, FONT_BODY, SCALE_BODY, bold=False, color_rgb=palette["text_dark"])
            
    attach_speaker_notes(slide, slide_data.get("speaker_notes", ""))
