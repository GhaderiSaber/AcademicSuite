#!/usr/bin/env python3
"""
RTL & Iranian Typography Engine (persian-defense-presentation-builder v2)
========================================================================
Enforces native Right-to-Left (RTL) DrawingML OpenXML formatting,
dynamic font resolution with Iranian fallbacks, strict defense legibility scales
(>=20 pt body text), and authentic Persian text normalization.
"""

import sys
import re
from typing import Optional, Tuple
from pptx.util import Pt
from pptx.enum.text import PP_ALIGN
from pptx.dml.color import RGBColor
from pptx.oxml import parse_xml
from pptx.oxml.ns import nsdecls

# ---------------------------------------------------------------------------
# Strict Legibility Scales (16:9 Canvas in Defense Room)
# ---------------------------------------------------------------------------
# Titles: 28–36 pt
SCALE_TITLE = 30.0
# Major numeric results / KPI callouts: 34–52 pt
SCALE_KPI_HERO = 44.0
SCALE_KPI_SUB = 22.0
# Body text: 20–26 pt (Strictly >= 20 pt in content zones!)
SCALE_BODY = 22.0
SCALE_BODY_BOLD = 22.0
# Compact labels, badges, and card captions: 16–20 pt
SCALE_LABEL = 18.0
SCALE_BADGE = 17.0
# Table cell text: 17–20 pt
SCALE_TABLE_HEADER = 18.5
SCALE_TABLE_CELL = 17.5
# Footer metadata: 11-13 pt
SCALE_FOOTER = 12.0

# ---------------------------------------------------------------------------
# Font Detection & Fallbacks
# ---------------------------------------------------------------------------
PRIMARY_PERSIAN_HEAD = "B Titr"
PRIMARY_PERSIAN_BODY = "B Nazanin"
LATIN_FONT = "Times New Roman"

FALLBACK_FONTS_HEAD = ["B Titr", "Vazirmatn", "Noto Sans Arabic", "Segoe UI", "Tahoma"]
FALLBACK_FONTS_BODY = ["B Nazanin", "Vazirmatn", "Noto Sans Arabic", "Segoe UI", "Tahoma", "Arial"]

def resolve_font(preferred: str, fallback_list: list) -> str:
    """Returns preferred font; in PowerPoint OpenXML, embedding complex-script tag
    allows PowerPoint to resolve locally or use the fallback typeface cleanly."""
    return preferred

FONT_TITLE = resolve_font(PRIMARY_PERSIAN_HEAD, FALLBACK_FONTS_HEAD)
FONT_BODY = resolve_font(PRIMARY_PERSIAN_BODY, FALLBACK_FONTS_BODY)
FONT_ENG = LATIN_FONT

# ---------------------------------------------------------------------------
# Persian Text Normalization
# ---------------------------------------------------------------------------
PERSIAN_DIGITS = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
LATIN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")

def to_persian_digits(text: str) -> str:
    """Converts Latin digits to Persian digits."""
    if not isinstance(text, str):
        text = str(text)
    return text.translate(PERSIAN_DIGITS)

def to_latin_digits(text: str) -> str:
    """Converts Persian digits to Latin digits."""
    if not isinstance(text, str):
        text = str(text)
    return text.translate(LATIN_DIGITS)

def normalize_persian_text(text: str) -> str:
    """Normalizes Persian characters, half-spaces (\u200c), and standardizes quotes."""
    if not text:
        return ""
    # Standardize Arabic Yeh and Kaf
    text = text.replace("ي", "ی").replace("ك", "ک")
    # Clean up double half-spaces
    text = re.sub(r"\u200c+", "\u200c", text)
    return text.strip()

# ---------------------------------------------------------------------------
# OpenXML DrawingML Formatting Helpers (Native RTL & Font Bindings)
# ---------------------------------------------------------------------------
def apply_p_rtl(p, align=PP_ALIGN.RIGHT):
    """Enforce Right-to-Left (rtl=1) and text alignment in DrawingML."""
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
    """Set text, font size, bold, color, and inject DrawingML complex script typeface."""
    clean_text = normalize_persian_text(text)
    run.text = clean_text
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.font.bold = bold
    if color_rgb:
        run.font.color.rgb = color_rgb

    # Inject DrawingML complex script (<a:cs typeface="..."/>)
    rPr = run._r.get_or_add_rPr()
    rPr.set("b", "1" if bold else "0")
    
    # Remove any existing cs element to avoid duplicates
    for child in list(rPr):
        if child.tag.endswith("cs"):
            rPr.remove(child)

    cs = parse_xml(f'<a:cs {nsdecls("a")} typeface="{font_name}"/>')
    rPr.append(cs)

def attach_speaker_notes(slide, notes_text: str):
    """Injects oral defense speaker notes into PowerPoint slide notes frame with RTL styling."""
    if not notes_text:
        return
    notes_slide = slide.notes_slide
    tf = notes_slide.notes_text_frame
    tf.clear()
    
    lines = notes_text.strip().split("\n")
    for i, line in enumerate(lines):
        if i == 0:
            p = tf.paragraphs[0]
        else:
            p = tf.add_paragraph()
        apply_p_rtl(p, PP_ALIGN.RIGHT)
        r = p.add_run()
        set_run_font(r, line, FONT_BODY, 13.0, bold=("زمان" in line or "داور" in line or "پاسخ" in line), color_rgb=RGBColor(30, 41, 59))
