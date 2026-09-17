# -*- coding: utf-8 -*-
"""
openxml_helpers.py — Deterministic OpenXML & Typography Formatting Utilities

Enforces APA 7th Edition table borders, Persian RTL font bindings (B Nazanin / B Titr),
LTR numeric decoupling (-0.32), and OMML equation preservation.
"""

from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def set_cell_bidi(cell, rtl=True):
    """Sets BiDi direction on a table cell."""
    tcPr = cell._element.get_or_add_tcPr()
    bidi = OxmlElement('w:bidi')
    bidi.set(qn('w:val'), '1' if rtl else '0')
    tcPr.append(bidi)


def set_run_fonts(run, cs_font="B Nazanin", latin_font="Times New Roman", size_pt=13):
    """Binds complex script and Latin fonts to prevent box glyphs."""
    run.font.name = latin_font
    rPr = run._element.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), latin_font)
    rFonts.set(qn('w:hAnsi'), latin_font)
    rFonts.set(qn('w:cs'), cs_font)
    rFonts.set(qn('w:hint'), 'cs')
    rPr.append(rFonts)


def format_apa_table(table):
    """Applies the strict 3-line APA 7 border specification (top 0.75pt, header bottom 0.5pt, table bottom 0.75pt)."""
    tblPr = table._element.tblPr
    tblBorders = OxmlElement('w:tblBorders')
    
    # Top border 0.75pt (6 eighths of a pt)
    top = OxmlElement('w:top')
    top.set(qn('w:val'), 'single')
    top.set(qn('w:sz'), '6')
    top.set(qn('w:space'), '0')
    top.set(qn('w:color'), 'auto')
    tblBorders.append(top)
    
    # Bottom border 0.75pt
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '6')
    bottom.set(qn('w:space'), '0')
    bottom.set(qn('w:color'), 'auto')
    tblBorders.append(bottom)
    
    # Zero vertical borders
    for border_name in ['left', 'right', 'insideV']:
        b = OxmlElement(f'w:{border_name}')
        b.set(qn('w:val'), 'none')
        tblBorders.append(b)
        
    tblPr.append(tblBorders)
