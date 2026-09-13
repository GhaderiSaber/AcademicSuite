#!/usr/bin/env python3
"""
qualitative_engine.py - Advanced Qualitative Data Analysis & Chapter 4 Reporting Engine

Specialized for Psychology, Counseling, and Behavioral Sciences graduate research.
Supports:
  1. Braun & Clarke (2006/2019/2021) Reflexive Thematic Analysis (Basic, Organizing, Global Themes).
  2. Strauss & Corbin (1990/1998) Grounded Theory Paradigmatic Model (Causal, Core, Context, Intervening, Strategies, Consequences).
  3. Guba & Lincoln (1985) Trustworthiness Audit & Inter-Coder Reliability (Holsti's Index PAO, Cohen's Kappa, % Agreement).
  4. Complete Defense-Ready Chapter 4 Word Document (.docx) with authentic Persian OpenXML typography, APA 7 borderless tables, and verbatim blockquotes.
  5. 5-Sheet Master Coding Excel Workbook (.xlsx).
  6. High-Resolution 300-DPI Visual Thematic Network Diagram (.png).
  7. Structured JSON Summary Archive.
"""

import os
import sys
import json
import math
import argparse
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as patches

import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# ==============================================================================
# 1. OPENXML & WORD STYLING UTILITIES (BIDI & IRANIAN TYPOGRAPHY)
# ==============================================================================
def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_shading(cell, color_hex="F2F4F7"):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement('w:shd')
    shd.set(qn('w:val'), 'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'), color_hex)
    tcPr.append(shd)

def apply_apa7_table_borders(table):
    """
    Applies APA 7th Edition borderless style:
    Exactly 3 horizontal borders: Top line, Header bottom underline, and Table bottom line.
    Zero vertical borders.
    """
    tblPr = table._tbl.tblPr
    tblBorders = OxmlElement('w:tblBorders')
    
    top = OxmlElement('w:top')
    top.set(qn('w:val'), 'single')
    top.set(qn('w:sz'), '8')
    top.set(qn('w:space'), '0')
    top.set(qn('w:color'), '222222')
    tblBorders.append(top)
    
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '8')
    bottom.set(qn('w:space'), '0')
    bottom.set(qn('w:color'), '222222')
    tblBorders.append(bottom)
    
    for b_name in ['left', 'right', 'insideV']:
        b = OxmlElement(f'w:{b_name}')
        b.set(qn('w:val'), 'none')
        tblBorders.append(b)
        
    insideH = OxmlElement('w:insideH')
    insideH.set(qn('w:val'), 'none')
    tblBorders.append(insideH)
    
    tblPr.append(tblBorders)

def set_table_header_underline(row):
    for cell in row.cells:
        tcPr = cell._tc.get_or_add_tcPr()
        tcBorders = OxmlElement('w:tcBorders')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '6')
        bottom.set(qn('w:space'), '0')
        bottom.set(qn('w:color'), '333333')
        tcBorders.append(bottom)
        tcPr.append(tcBorders)

def set_paragraph_bidi(p, is_rtl=True):
    pPr = p._p.get_or_add_pPr()
    if is_rtl:
        bidi = OxmlElement('w:bidi')
        bidi.set(qn('w:val'), '1')
        pPr.append(bidi)

def set_table_bidi(table, is_rtl=True):
    if is_rtl:
        tblPr = table._tbl.tblPr
        tblBidi = OxmlElement('w:bidiVisual')
        tblPr.append(tblBidi)

def add_persian_run(paragraph, text, font_name="B Nazanin", size_pt=13, bold=False, italic=False, color_rgb=(0, 0, 0)):
    run = paragraph.add_run(text)
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor(*color_rgb)
    
    rPr = run._r.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), "Times New Roman")
    rFonts.set(qn('w:hAnsi'), "Times New Roman")
    rFonts.set(qn('w:cs'), font_name)
    rPr.append(rFonts)
    
    rtl_el = OxmlElement('w:rtl')
    rtl_el.set(qn('w:val'), '1')
    rPr.append(rtl_el)
    return run

def add_blockquote(doc, quote_text, participant_tag, is_rtl=True):
    """
    Adds a formatted APA 7 qualitative verbatim blockquote.
    """
    p = doc.add_paragraph()
    set_paragraph_bidi(p, is_rtl=is_rtl)
    p.paragraph_format.left_indent = Inches(0.4)
    p.paragraph_format.right_indent = Inches(0.4)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(6)
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY if is_rtl else WD_ALIGN_PARAGRAPH.LEFT
    
    lead_run = add_persian_run(p, f"«{quote_text}» ", font_name="B Nazanin", size_pt=12, italic=True, color_rgb=(40, 40, 40))
    tag_run = add_persian_run(p, f"({participant_tag})", font_name="B Nazanin", size_pt=11, bold=True, color_rgb=(20, 50, 90))

# ==============================================================================
# 2. COMPUTATIONAL & RELIABILITY ENGINE
# ==============================================================================
def calculate_holsti_reliability(total_c1, total_c2, agreed):
    """
    Computes Holsti's Coefficient: PAO = 2M / (N1 + N2)
    """
    if (total_c1 + total_c2) <= 0:
        return 1.0, 100.0
    pao = (2.0 * agreed) / (total_c1 + total_c2)
    pct = pao * 100.0
    return round(float(pao), 3), round(float(pct), 1)

def extract_thematic_metrics(payload):
    """
    Computes frequencies and hierarchical summaries for Thematic Analysis.
    """
    global_themes = payload.get("global_themes", [])
    total_participants = len(payload.get("participants", [])) or int(payload.get("sample_size", 15))
    
    flat_codes = []
    summary_hierarchy = []
    
    for gt in global_themes:
        gt_name = gt["name"]
        gt_desc = gt.get("description", "")
        gt_orgs = gt.get("organizing_themes", [])
        
        gt_entry = {
            "global_theme": gt_name,
            "description": gt_desc,
            "organizing_themes": []
        }
        
        for ot in gt_orgs:
            ot_name = ot["name"]
            ot_basics = ot.get("basic_themes", [])
            ot_entry = {
                "organizing_theme": ot_name,
                "basic_themes": []
            }
            
            for bt in ot_basics:
                code_text = bt["code"]
                freq = int(bt.get("frequency", 1))
                pct = float(bt.get("percentage", round((freq / max(1, total_participants)) * 100, 1)))
                quotes = bt.get("quotes", [])
                
                flat_codes.append({
                    "Global_Theme": gt_name,
                    "Organizing_Theme": ot_name,
                    "Basic_Theme_Code": code_text,
                    "Frequency_N": freq,
                    "Percentage": pct,
                    "Quotes_Count": len(quotes)
                })
                
                ot_entry["basic_themes"].append({
                    "code": code_text,
                    "frequency": freq,
                    "percentage": pct,
                    "quotes": quotes
                })
                
            gt_entry["organizing_themes"].append(ot_entry)
        summary_hierarchy.append(gt_entry)
        
    return flat_codes, summary_hierarchy

# ==============================================================================
# 3. VISUAL THEMATIC NETWORK DIAGRAM GENERATOR
# ==============================================================================
def render_thematic_diagram(payload, out_png_path, lang="fa"):
    """
    Generates a clean 300-DPI visual network diagram of Global & Organizing Themes.
    """
    method = payload.get("methodology", "thematic_analysis")
    fig, ax = plt.subplots(figsize=(12, 8), dpi=300)
    ax.axis('off')
    
    # Background styling
    fig.patch.set_facecolor('#F8FAFC')
    ax.set_facecolor('#F8FAFC')
    
    if method == "grounded_theory":
        # Strauss & Corbin Paradigmatic Model Diagram
        ax.set_title("Strauss & Corbin (1998) Grounded Theory Paradigmatic Model\nمدل پارادایمی نظریه داده‌بنیاد", fontsize=14, fontweight='bold', pad=20, color='#0F172A')
        
        boxes = [
            ("Causal Conditions\nشرایط علی", 0.08, 0.65, '#E0F2FE', '#0284C7'),
            ("Core Phenomenon\nپدیده محوری", 0.38, 0.65, '#FEE2E2', '#DC2626'),
            ("Action/Interaction Strategies\nراهبردها و اقدامات", 0.68, 0.65, '#FEF3C7', '#D97706'),
            ("Contextual Conditions\nشرایط زمینه‌ای", 0.08, 0.20, '#F1F5F9', '#475569'),
            ("Intervening Conditions\nشرایط مداخله‌گر", 0.38, 0.20, '#EDE9FE', '#7C3AED'),
            ("Consequences\nپیامدها", 0.68, 0.20, '#DCFCE7', '#16A34A'),
        ]
        
        for title, x, y, bg_c, border_c in boxes:
            rect = patches.FancyBboxPatch((x, y), 0.24, 0.22, boxstyle="round,pad=0.03,rounding_size=0.02", facecolor=bg_c, edgecolor=border_c, linewidth=2)
            ax.add_patch(rect)
            ax.text(x + 0.12, y + 0.11, title, ha='center', va='center', fontsize=10, fontweight='bold', color='#1E293B')
            
        # Arrows linking causal -> core -> strategies -> consequences
        arrow_style = "Simple, tail_width=1.5, head_width=6, head_length=8"
        kw = dict(arrowstyle=arrow_style, color="#64748B")
        ax.annotate("", xy=(0.38, 0.76), xytext=(0.32, 0.76), arrowprops=kw)
        ax.annotate("", xy=(0.68, 0.76), xytext=(0.62, 0.76), arrowprops=kw)
        ax.annotate("", xy=(0.50, 0.65), xytext=(0.50, 0.42), arrowprops=kw)
        ax.annotate("", xy=(0.80, 0.42), xytext=(0.80, 0.65), arrowprops=kw)
        
    else:
        # Thematic Analysis Hierarchy Map
        study_title = payload.get("study_title", "Thematic Network Analysis")
        ax.set_title(f"Reflexive Thematic Network (Braun & Clarke)\n{study_title}", fontsize=13, fontweight='bold', pad=20, color='#0F172A')
        
        # Central Core Node
        core_rect = patches.FancyBboxPatch((0.36, 0.42), 0.28, 0.16, boxstyle="round,pad=0.03,rounding_size=0.03", facecolor='#1E293B', edgecolor='#0F172A', linewidth=2)
        ax.add_patch(core_rect)
        ax.text(0.50, 0.50, "Core Research Phenomenon\nپدیده محوری پژوهش", ha='center', va='center', fontsize=11, fontweight='bold', color='#FFFFFF')
        
        global_themes = payload.get("global_themes", [])
        n_gt = min(4, len(global_themes))
        positions = [(0.12, 0.72), (0.64, 0.72), (0.12, 0.12), (0.64, 0.12)]
        colors = [('#E0F2FE', '#0284C7'), ('#FEE2E2', '#DC2626'), ('#FEF3C7', '#D97706'), ('#DCFCE7', '#16A34A')]
        
        for i in range(n_gt):
            gt = global_themes[i]
            x, y = positions[i]
            bg_c, border_c = colors[i]
            
            rect = patches.FancyBboxPatch((x, y), 0.24, 0.20, boxstyle="round,pad=0.03,rounding_size=0.02", facecolor=bg_c, edgecolor=border_c, linewidth=2)
            ax.add_patch(rect)
            
            gt_title = gt.get("name_en", gt.get("name", f"Theme {i+1}"))
            if len(gt_title) > 28:
                gt_title = gt_title[:26] + "..."
            ax.text(x + 0.12, y + 0.12, f"Global Theme {i+1}\n{gt_title}", ha='center', va='center', fontsize=9, fontweight='bold', color='#1E293B')
            
            # Sub-branches count
            sub_count = len(gt.get("organizing_themes", []))
            ax.text(x + 0.12, y + 0.05, f"({sub_count} Organizing Themes)", ha='center', va='center', fontsize=8, color='#475569')
            
            # Connector lines to core
            core_x = 0.50
            core_y = 0.50
            mid_x = x + 0.12
            mid_y = y + (0.0 if y > core_y else 0.20)
            ax.plot([core_x, mid_x], [core_y, mid_y], color='#94A3B8', linestyle='--', linewidth=1.5, zorder=1)
            
    plt.tight_layout()
    plt.savefig(out_png_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close()
    return out_png_path

# ==============================================================================
# 4. EXCEL MASTER CODING WORKBOOK GENERATOR
# ==============================================================================
def export_thematic_excel(payload, flat_codes, excel_path):
    """
    Generates a 5-sheet master qualitative coding workbook in Excel (.xlsx).
    """
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        # Sheet 1: Participants Profile
        participants = payload.get("participants", [])
        if participants:
            df_part = pd.DataFrame(participants)
            df_part.to_excel(writer, sheet_name="Participants", index=False)
            
        # Sheet 2: Thematic Hierarchy & Codebook
        df_codes = pd.DataFrame(flat_codes)
        df_codes.to_excel(writer, sheet_name="Thematic_Hierarchy", index=False)
        
        # Sheet 3: Quotes Repository
        quotes_rows = []
        for gt in payload.get("global_themes", []):
            gt_name = gt["name"]
            for ot in gt.get("organizing_themes", []):
                ot_name = ot["name"]
                for bt in ot.get("basic_themes", []):
                    code = bt["code"]
                    for q in bt.get("quotes", []):
                        quotes_rows.append({
                            "Global_Theme": gt_name,
                            "Organizing_Theme": ot_name,
                            "Basic_Code": code,
                            "Participant_ID": q.get("participant_id", ""),
                            "Verbatim_Quote": q.get("quote", "")
                        })
        if quotes_rows:
            df_quotes = pd.DataFrame(quotes_rows)
            df_quotes.to_excel(writer, sheet_name="Quotes_Repository", index=False)
            
        # Sheet 4: Grounded Theory (if present)
        if "paradigmatic_model" in payload:
            pm = payload["paradigmatic_model"]
            pm_rows = []
            for comp_key, comp_val in pm.items():
                title = comp_val.get("title", comp_key)
                concept = comp_val.get("concept", "")
                for cat in comp_val.get("categories", []):
                    pm_rows.append({
                        "Dimension": title,
                        "Core_Concept": concept,
                        "Category": cat
                    })
            df_pm = pd.DataFrame(pm_rows)
            df_pm.to_excel(writer, sheet_name="Grounded_Theory_Model", index=False)
            
        # Sheet 5: Trustworthiness & Reliability
        trust_cfg = payload.get("trustworthiness", {})
        rel_cfg = payload.get("inter_coder_reliability", {})
        
        rel_rows = []
        if rel_cfg:
            rel_rows.append({"Metric": "Coder 1 (Primary)", "Value": rel_cfg.get("coder1_name", "")})
            rel_rows.append({"Metric": "Coder 2 (Auditor)", "Value": rel_cfg.get("coder2_name", "")})
            rel_rows.append({"Metric": "Total Decisions (Coder 1)", "Value": rel_cfg.get("total_decisions_coder1", 0)})
            rel_rows.append({"Metric": "Total Decisions (Coder 2)", "Value": rel_cfg.get("total_decisions_coder2", 0)})
            rel_rows.append({"Metric": "Agreed Coding Decisions (M)", "Value": rel_cfg.get("agreed_decisions", 0)})
            rel_rows.append({"Metric": "Holsti's Index (PAO)", "Value": rel_cfg.get("holsti_index", 0.0)})
            rel_rows.append({"Metric": "Percent Agreement (%)", "Value": rel_cfg.get("percent_agreement", 0.0)})
            rel_rows.append({"Metric": "Cohen's Kappa (κ)", "Value": rel_cfg.get("cohens_kappa", 0.0)})
            
        for k, items in trust_cfg.items():
            for it in items:
                rel_rows.append({"Metric": f"Procedure ({k})", "Value": it})
                
        if rel_rows:
            df_rel = pd.DataFrame(rel_rows)
            df_rel.to_excel(writer, sheet_name="Trustworthiness_Reliability", index=False)
            
    return excel_path

# ==============================================================================
# 5. DEFENSE-READY WORD DOCUMENT COMPILER (CHAPTER 4)
# ==============================================================================
def compile_qualitative_chapter4_docx(payload, flat_codes, diagram_png_path, out_docx_path, lang="fa"):
    """
    Compiles full, defense-ready qualitative findings chapter in Word (.docx)
    with strict Persian typography, APA 7 borderless tables, and verbatim quotes.
    """
    doc = docx.Document()
    is_rtl = (lang == "fa")
    
    # Page Margins (Standard Iranian academic 1 inch / 2.54 cm)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
    # --- Chapter Title ---
    p_title = doc.add_paragraph()
    set_paragraph_bidi(p_title, is_rtl=is_rtl)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(12)
    p_title.paragraph_format.space_after = Pt(18)
    
    if is_rtl:
        add_persian_run(p_title, "فصل چهارم: یافته‌های پژوهش کیفی", font_name="B Titr", size_pt=18, bold=True, color_rgb=(20, 30, 55))
        p_sub = doc.add_paragraph()
        set_paragraph_bidi(p_sub, is_rtl=is_rtl)
        p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_persian_run(p_sub, payload.get("study_title", ""), font_name="B Nazanin", size_pt=14, bold=True, color_rgb=(50, 70, 100))
    else:
        add_persian_run(p_title, "Chapter 4: Qualitative Research Findings", font_name="Times New Roman", size_pt=18, bold=True, color_rgb=(20, 30, 55))
        p_sub = doc.add_paragraph()
        set_paragraph_bidi(p_sub, is_rtl=False)
        p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_persian_run(p_sub, payload.get("study_title_en", payload.get("study_title", "")), font_name="Times New Roman", size_pt=14, bold=True, color_rgb=(50, 70, 100))
        
    # --- 1. Introduction Section ---
    p_intro_h = doc.add_paragraph()
    set_paragraph_bidi(p_intro_h, is_rtl=is_rtl)
    p_intro_h.paragraph_format.space_before = Pt(14)
    p_intro_h.paragraph_format.space_after = Pt(6)
    add_persian_run(p_intro_h, "۱-۴. مقدمه و توصیف فرآیند گردآوری داده‌ها" if is_rtl else "4.1. Introduction and Data Collection Overview", font_name="B Titr" if is_rtl else "Times New Roman", size_pt=14, bold=True)
    
    p_intro_text = doc.add_paragraph()
    set_paragraph_bidi(p_intro_text, is_rtl=is_rtl)
    p_intro_text.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_intro_text.paragraph_format.line_spacing = 1.25
    intro_content = payload.get("research_context", "") + " " + payload.get("saturation_point", "")
    add_persian_run(p_intro_text, intro_content, font_name="B Nazanin" if is_rtl else "Times New Roman", size_pt=13)
    
    # --- 2. Demographic Profile of Participants Table (جدول ۱-۴) ---
    participants = payload.get("participants", [])
    if participants:
        p_tbl1_cap = doc.add_paragraph()
        set_paragraph_bidi(p_tbl1_cap, is_rtl=is_rtl)
        p_tbl1_cap.paragraph_format.space_before = Pt(14)
        p_tbl1_cap.paragraph_format.space_after = Pt(4)
        add_persian_run(p_tbl1_cap, "جدول ۱-۴. ویژگی‌های جمعیت‌شناختی و مشخصات بالینی مشارکت‌کنندگان در پژوهش" if is_rtl else "Table 4.1. Demographic and Clinical Characteristics of Participants", font_name="B Titr" if is_rtl else "Times New Roman", size_pt=11, bold=True)
        
        # Dynamically determine columns
        first_p = participants[0]
        col_keys = [k for k in first_p.keys() if k != "id"]
        col_headers_fa = {
            "pseudonym": "کد مشارکت‌کننده",
            "gender": "جنسیت",
            "age": "سن (سال)",
            "education": "سطح تحصیلات",
            "marital_status": "وضعیت تأهل",
            "cancer_type": "نوع بیماری",
            "duration_months": "مدت ابتلا (ماه)",
            "years_married": "طول مدت ازدواج",
            "post_infidelity_months": "مدت پس از بحران (ماه)"
        }
        
        table1 = doc.add_table(rows=len(participants) + 1, cols=len(col_keys))
        table1.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_bidi(table1, is_rtl=is_rtl)
        apply_apa7_table_borders(table1)
        
        # Headers
        hdr_row = table1.rows[0]
        set_table_header_underline(hdr_row)
        for c_idx, k in enumerate(col_keys):
            cell = hdr_row.cells[c_idx]
            set_cell_margins(cell)
            set_cell_shading(cell, "F2F4F7")
            p_cell = cell.paragraphs[0]
            p_cell.alignment = WD_ALIGN_PARAGRAPH.CENTER
            set_paragraph_bidi(p_cell, is_rtl=is_rtl)
            h_text = col_headers_fa.get(k, k.replace("_", " ").title()) if is_rtl else k.replace("_", " ").title()
            add_persian_run(p_cell, h_text, font_name="B Titr" if is_rtl else "Times New Roman", size_pt=10, bold=True)
            
        # Data rows
        for r_idx, part in enumerate(participants):
            row = table1.rows[r_idx + 1]
            for c_idx, k in enumerate(col_keys):
                cell = row.cells[c_idx]
                set_cell_margins(cell)
                p_cell = cell.paragraphs[0]
                p_cell.alignment = WD_ALIGN_PARAGRAPH.CENTER
                set_paragraph_bidi(p_cell, is_rtl=is_rtl)
                val_str = str(part.get(k, ""))
                add_persian_run(p_cell, val_str, font_name="B Nazanin" if is_rtl else "Times New Roman", size_pt=11)
                
    # --- 3. Master Thematic Analysis Section & Table (جدول ۲-۴) ---
    methodology = payload.get("methodology", "thematic_analysis")
    
    if methodology == "thematic_analysis":
        p_theme_h = doc.add_paragraph()
        set_paragraph_bidi(p_theme_h, is_rtl=is_rtl)
        p_theme_h.paragraph_format.space_before = Pt(16)
        p_theme_h.paragraph_format.space_after = Pt(6)
        add_persian_run(p_theme_h, "۲-۴. تحلیل مضامین و شبکه مضامین استخراج‌شده" if is_rtl else "4.2. Extracted Thematic Hierarchy and Network", font_name="B Titr" if is_rtl else "Times New Roman", size_pt=14, bold=True)
        
        p_theme_intro = doc.add_paragraph()
        set_paragraph_bidi(p_theme_intro, is_rtl=is_rtl)
        p_theme_intro.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p_theme_intro.paragraph_format.line_spacing = 1.25
        intro_themes_text = (
            "پس از پیاده‌سازی متنی مصاحبه‌ها و اجرای شش مرحله تحلیل مضمون بازتابی براون و کلارک (۲۰۱۹)، "
            f"در مجموع تعداد {len(payload.get('global_themes', []))} مضمون فراگیر، "
            f"{sum(len(gt.get('organizing_themes', [])) for gt in payload.get('global_themes', []))} مضمون سازمان‌دهنده و "
            f"{len(flat_codes)} مضمون پایه شناسایی و صورتبندی گردید. جدول ۲-۴ ساختار ماتریس شبکه مضامین و فراوانی آن‌ها را نشان می‌دهد."
            if is_rtl else
            "Following reflexive thematic analysis (Braun & Clarke, 2019), "
            f"a total of {len(payload.get('global_themes', []))} global themes, "
            f"{sum(len(gt.get('organizing_themes', [])) for gt in payload.get('global_themes', []))} organizing themes, and "
            f"{len(flat_codes)} basic themes were identified and structured. Table 4.2 presents the thematic network matrix."
        )
        add_persian_run(p_theme_intro, intro_themes_text, font_name="B Nazanin" if is_rtl else "Times New Roman", size_pt=13)
        
        # Table 2-4: Master Thematic Table
        p_tbl2_cap = doc.add_paragraph()
        set_paragraph_bidi(p_tbl2_cap, is_rtl=is_rtl)
        p_tbl2_cap.paragraph_format.space_before = Pt(12)
        p_tbl2_cap.paragraph_format.space_after = Pt(4)
        add_persian_run(p_tbl2_cap, "جدول ۲-۴. ماتریس شبکه مضامین، سطوح طبقه‌بندی و فراوانی و درصد پاسخ‌ها" if is_rtl else "Table 4.2. Master Thematic Network Matrix with Frequencies and Percentages", font_name="B Titr" if is_rtl else "Times New Roman", size_pt=11, bold=True)
        
        table2 = doc.add_table(rows=len(flat_codes) + 1, cols=5)
        table2.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_bidi(table2, is_rtl=is_rtl)
        apply_apa7_table_borders(table2)
        
        hdr_cells = table2.rows[0].cells
        set_table_header_underline(table2.rows[0])
        h_titles = ["مضمون فراگیر (اصلی)", "مضمون سازمان‌دهنده (فرعی)", "مضمون پایه (کد اولیه)", "فراوانی (N)", "درصد (%)"] if is_rtl else ["Global Theme", "Organizing Theme", "Basic Theme (Code)", "Frequency (N)", "Percent (%)"]
        
        for c_i, h_txt in enumerate(h_titles):
            set_cell_margins(hdr_cells[c_i])
            set_cell_shading(hdr_cells[c_i], "F2F4F7")
            p_h = hdr_cells[c_i].paragraphs[0]
            p_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
            set_paragraph_bidi(p_h, is_rtl=is_rtl)
            add_persian_run(p_h, h_txt, font_name="B Titr" if is_rtl else "Times New Roman", size_pt=10, bold=True)
            
        for r_i, fc in enumerate(flat_codes):
            row_cells = table2.rows[r_i + 1].cells
            set_cell_margins(row_cells[0], left=100, right=100)
            set_cell_margins(row_cells[1], left=100, right=100)
            set_cell_margins(row_cells[2], left=100, right=100)
            
            p0 = row_cells[0].paragraphs[0]
            set_paragraph_bidi(p0, is_rtl=is_rtl)
            add_persian_run(p0, fc["Global_Theme"], font_name="B Nazanin" if is_rtl else "Times New Roman", size_pt=10, bold=True)
            
            p1 = row_cells[1].paragraphs[0]
            set_paragraph_bidi(p1, is_rtl=is_rtl)
            add_persian_run(p1, fc["Organizing_Theme"], font_name="B Nazanin" if is_rtl else "Times New Roman", size_pt=10)
            
            p2 = row_cells[2].paragraphs[0]
            set_paragraph_bidi(p2, is_rtl=is_rtl)
            add_persian_run(p2, fc["Basic_Theme_Code"], font_name="B Nazanin" if is_rtl else "Times New Roman", size_pt=10)
            
            p3 = row_cells[3].paragraphs[0]
            p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
            set_paragraph_bidi(p3, is_rtl=is_rtl)
            add_persian_run(p3, str(fc["Frequency_N"]), font_name="Times New Roman", size_pt=10)
            
            p4 = row_cells[4].paragraphs[0]
            p4.alignment = WD_ALIGN_PARAGRAPH.CENTER
            set_paragraph_bidi(p4, is_rtl=is_rtl)
            add_persian_run(p4, f"{fc['Percentage']:.1f}", font_name="Times New Roman", size_pt=10)
            
        # --- 4. In-Depth Narrative Analysis with Verbatim Blockquotes ---
        p_narrative_h = doc.add_paragraph()
        set_paragraph_bidi(p_narrative_h, is_rtl=is_rtl)
        p_narrative_h.paragraph_format.space_before = Pt(18)
        p_narrative_h.paragraph_format.space_after = Pt(6)
        add_persian_run(p_narrative_h, "۳-۴. تبیین تفصیلی مضامین و استناد به بیانات مشارکت‌کنندگان" if is_rtl else "4.3. Detailed Narrative Synthesis and Participant Quotations", font_name="B Titr" if is_rtl else "Times New Roman", size_pt=14, bold=True)
        
        for gt_idx, gt in enumerate(payload.get("global_themes", [])):
            p_gt = doc.add_paragraph()
            set_paragraph_bidi(p_gt, is_rtl=is_rtl)
            p_gt.paragraph_format.space_before = Pt(12)
            p_gt.paragraph_format.space_after = Pt(4)
            gt_num_str = f"۱-۳-۴-{gt_idx+1}" if is_rtl else f"4.3.{gt_idx+1}"
            add_persian_run(p_gt, f"{gt_num_str}. مضمون فراگیر: {gt['name']}", font_name="B Titr" if is_rtl else "Times New Roman", size_pt=13, bold=True, color_rgb=(15, 45, 80))
            
            p_gt_desc = doc.add_paragraph()
            set_paragraph_bidi(p_gt_desc, is_rtl=is_rtl)
            p_gt_desc.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p_gt_desc.paragraph_format.line_spacing = 1.25
            add_persian_run(p_gt_desc, gt.get("description", ""), font_name="B Nazanin" if is_rtl else "Times New Roman", size_pt=13)
            
            for ot in gt.get("organizing_themes", []):
                p_ot = doc.add_paragraph()
                set_paragraph_bidi(p_ot, is_rtl=is_rtl)
                p_ot.paragraph_format.space_before = Pt(8)
                p_ot.paragraph_format.space_after = Pt(4)
                add_persian_run(p_ot, f"• مضمون سازمان‌دهنده: {ot['name']}", font_name="B Nazanin Bold" if is_rtl else "Times New Roman", size_pt=12, bold=True)
                
                for bt in ot.get("basic_themes", []):
                    p_bt = doc.add_paragraph()
                    set_paragraph_bidi(p_bt, is_rtl=is_rtl)
                    p_bt.paragraph_format.space_before = Pt(4)
                    p_bt.paragraph_format.space_after = Pt(2)
                    add_persian_run(p_bt, f"کد: {bt['code']} (تعداد مراجعات: {bt['frequency']} نفر، {bt['percentage']}%)", font_name="B Nazanin" if is_rtl else "Times New Roman", size_pt=12, bold=True)
                    
                    # Direct Quotations
                    for q in bt.get("quotes", []):
                        pid = q.get("participant_id", "")
                        # Find participant profile
                        p_info = next((p for p in participants if p.get("id") == pid), None)
                        if p_info:
                            ptag = f"{p_info.get('pseudonym', pid)}، {p_info.get('gender', '')}، {p_info.get('age', '')} ساله"
                        else:
                            ptag = pid
                        add_blockquote(doc, q.get("quote", ""), ptag, is_rtl=is_rtl)
                        
    elif methodology == "grounded_theory":
        # Strauss & Corbin Grounded Theory Paradigmatic Presentation
        p_gt_h = doc.add_paragraph()
        set_paragraph_bidi(p_gt_h, is_rtl=is_rtl)
        p_gt_h.paragraph_format.space_before = Pt(16)
        p_gt_h.paragraph_format.space_after = Pt(6)
        add_persian_run(p_gt_h, "۲-۴. تدوین مدل پارادایمی و ابعاد نظریه داده‌بنیاد (استراوس و کوربین)" if is_rtl else "4.2. Grounded Theory Paradigmatic Model (Strauss & Corbin)", font_name="B Titr" if is_rtl else "Times New Roman", size_pt=14, bold=True)
        
        pm = payload.get("paradigmatic_model", {})
        for dim_key, dim_val in pm.items():
            p_dim = doc.add_paragraph()
            set_paragraph_bidi(p_dim, is_rtl=is_rtl)
            p_dim.paragraph_format.space_before = Pt(10)
            p_dim.paragraph_format.space_after = Pt(2)
            add_persian_run(p_dim, f"■ {dim_val.get('title', dim_key)}:", font_name="B Titr" if is_rtl else "Times New Roman", size_pt=13, bold=True, color_rgb=(20, 50, 90))
            
            p_conc = doc.add_paragraph()
            set_paragraph_bidi(p_conc, is_rtl=is_rtl)
            p_conc.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            add_persian_run(p_conc, f"مفهوم بنیادین: {dim_val.get('concept', '')}", font_name="B Nazanin" if is_rtl else "Times New Roman", size_pt=12, italic=True)
            
            for cat in dim_val.get("categories", []):
                p_cat = doc.add_paragraph()
                set_paragraph_bidi(p_cat, is_rtl=is_rtl)
                p_cat.paragraph_format.left_indent = Inches(0.25)
                p_cat.paragraph_format.space_after = Pt(2)
                add_persian_run(p_cat, f"- {cat}", font_name="B Nazanin" if is_rtl else "Times New Roman", size_pt=12)

    # --- 5. Thematic Network Visual Diagram Section ---
    if diagram_png_path and os.path.exists(diagram_png_path):
        p_diag_h = doc.add_paragraph()
        set_paragraph_bidi(p_diag_h, is_rtl=is_rtl)
        p_diag_h.paragraph_format.space_before = Pt(16)
        p_diag_h.paragraph_format.space_after = Pt(4)
        diag_caption = "شکل ۱-۴. نمودار مفهومی شبکه مضامین و ساختار روابط مضامین پژوهش" if is_rtl else "Figure 4.1. Conceptual Thematic Network Diagram"
        add_persian_run(p_diag_h, diag_caption, font_name="B Titr" if is_rtl else "Times New Roman", size_pt=11, bold=True)
        
        p_img = doc.add_paragraph()
        p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img.paragraph_format.space_after = Pt(12)
        run_img = p_img.add_run()
        run_img.add_picture(diagram_png_path, width=Inches(6.2))
        
    # --- 6. Trustworthiness & Reliability Section (Guba & Lincoln / Holsti) ---
    p_trust_h = doc.add_paragraph()
    set_paragraph_bidi(p_trust_h, is_rtl=is_rtl)
    p_trust_h.paragraph_format.space_before = Pt(16)
    p_trust_h.paragraph_format.space_after = Pt(6)
    add_persian_run(p_trust_h, "۴-۴. اعتبارسنجی کیفی، معیارهای باورپذیری و پایایی بازآزمون (هولستی)" if is_rtl else "4.4. Qualitative Trustworthiness and Inter-Coder Reliability", font_name="B Titr" if is_rtl else "Times New Roman", size_pt=14, bold=True)
    
    p_trust_text = doc.add_paragraph()
    set_paragraph_bidi(p_trust_text, is_rtl=is_rtl)
    p_trust_text.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    p_trust_text.paragraph_format.line_spacing = 1.25
    trust_narrative = (
        "جهت سنجش دقت علمی و استحکام پژوهش، از معیارهای چهارگانه گوبا و لینکلن (۱۹۸۵) شامل قابلیت اعتماد (باورپذیری)، "
        "قابلیت انتقال، وابستگی (اتکاپذیری) و تأییدپذیری بهره گرفته شد. علاوه بر این، به منظور سنجش پایایی فرآیند کدگذاری، "
        "تعداد معینی از مصاحبه‌ها به طور مستقل توسط دو کدگذار بررسی و ضریب توافق هولستی و کاپای کوهن محاسبه گردید."
        if is_rtl else
        "To establish qualitative rigor, Guba and Lincoln's (1985) four criteria (credibility, transferability, dependability, confirmability) "
        "were systematically implemented, alongside inter-coder reliability assessments using Holsti's index and Cohen's Kappa."
    )
    add_persian_run(p_trust_text, trust_narrative, font_name="B Nazanin" if is_rtl else "Times New Roman", size_pt=13)
    
    # Reliability Table
    rel_cfg = payload.get("inter_coder_reliability", {})
    if rel_cfg:
        p_tbl3_cap = doc.add_paragraph()
        set_paragraph_bidi(p_tbl3_cap, is_rtl=is_rtl)
        p_tbl3_cap.paragraph_format.space_before = Pt(12)
        p_tbl3_cap.paragraph_format.space_after = Pt(4)
        add_persian_run(p_tbl3_cap, "جدول ۳-۴. شاخص‌های پایایی کدگذاری و توافق بین کدگذاران (ضریب هولستی و کاپا)" if is_rtl else "Table 4.3. Inter-Coder Reliability Metrics (Holsti's Index and Cohen's Kappa)", font_name="B Titr" if is_rtl else "Times New Roman", size_pt=11, bold=True)
        
        table3 = doc.add_table(rows=7, cols=2)
        table3.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_bidi(table3, is_rtl=is_rtl)
        apply_apa7_table_borders(table3)
        set_table_header_underline(table3.rows[0])
        
        hdr3 = table3.rows[0].cells
        set_cell_shading(hdr3[0], "F2F4F7")
        set_cell_shading(hdr3[1], "F2F4F7")
        set_cell_margins(hdr3[0])
        set_cell_margins(hdr3[1])
        
        p_h0 = hdr3[0].paragraphs[0]
        set_paragraph_bidi(p_h0, is_rtl=is_rtl)
        add_persian_run(p_h0, "شاخص پایایی / متغیر کدگذاری" if is_rtl else "Reliability Indicator / Parameter", font_name="B Titr" if is_rtl else "Times New Roman", size_pt=10, bold=True)
        
        p_h1 = hdr3[1].paragraphs[0]
        p_h1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_paragraph_bidi(p_h1, is_rtl=is_rtl)
        add_persian_run(p_h1, "مقدار محاسبه‌شده" if is_rtl else "Estimated Value", font_name="B Titr" if is_rtl else "Times New Roman", size_pt=10, bold=True)
        
        metrics_display = [
            ("کدگذار اول (پژوهشگر اصلی)" if is_rtl else "Coder 1", str(rel_cfg.get("coder1_name", ""))),
            ("کدگذار دوم (ارزیاب مستقل)" if is_rtl else "Coder 2", str(rel_cfg.get("coder2_name", ""))),
            ("تعداد کل کدهای استخراج‌شده کدگذار ۱ (N1)" if is_rtl else "Total Decisions Coder 1 (N1)", str(rel_cfg.get("total_decisions_coder1", 0))),
            ("تعداد کل کدهای استخراج‌شده کدگذار ۲ (N2)" if is_rtl else "Total Decisions Coder 2 (N2)", str(rel_cfg.get("total_decisions_coder2", 0))),
            ("تعداد کدهای مورد توافق دو کدگذار (M)" if is_rtl else "Agreed Decisions (M)", str(rel_cfg.get("agreed_decisions", 0))),
            ("ضریب پایایی هولستی (PAO = 2M / [N1+N2])" if is_rtl else "Holsti's Reliability Index (PAO)", f"{rel_cfg.get('holsti_index', 0.0):.3f} ({rel_cfg.get('percent_agreement', 0.0):.1f}%)")
        ]
        
        for r_i, (m_lbl, m_val) in enumerate(metrics_display):
            row = table3.rows[r_i + 1]
            c0, c1 = row.cells[0], row.cells[1]
            set_cell_margins(c0)
            set_cell_margins(c1)
            
            p_c0 = c0.paragraphs[0]
            set_paragraph_bidi(p_c0, is_rtl=is_rtl)
            add_persian_run(p_c0, m_lbl, font_name="B Nazanin" if is_rtl else "Times New Roman", size_pt=10, bold=(r_i == 5))
            
            p_c1 = c1.paragraphs[0]
            p_c1.alignment = WD_ALIGN_PARAGRAPH.CENTER
            set_paragraph_bidi(p_c1, is_rtl=is_rtl)
            add_persian_run(p_c1, m_val, font_name="Times New Roman", size_pt=10, bold=(r_i == 5))
            
    doc.save(out_docx_path)
    return out_docx_path

# ==============================================================================
# 6. MAIN DISPATCHER
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(description="Advanced Qualitative Data Analysis & Chapter 4 Engine")
    parser.add_argument("--json", required=True, help="Path to input qualitative payload JSON")
    parser.add_argument("--out-dir", default="./qualitative_output", help="Directory to save generated artifacts")
    parser.add_argument("--lang", choices=["fa", "en"], default="fa", help="Language for reports (fa=Persian, en=English)")
    parser.add_argument("--method", choices=["thematic_analysis", "grounded_theory"], default=None, help="Qualitative method")
    
    args = parser.parse_args()
    
    with open(args.json, "r", encoding="utf-8") as f:
        payload = json.load(f)
        
    os.makedirs(args.out_dir, exist_ok=True)
    lang = args.lang
    method = args.method or payload.get("methodology", "thematic_analysis")
    
    print(f"[INFO] Initializing Qualitative Engine in mode: '{method.upper()}' (Language: {lang})")
    
    # 1. Process Thematic Metrics & Codes
    flat_codes, summary_hierarchy = extract_thematic_metrics(payload)
    print(f"[INFO] Processed {len(flat_codes)} basic codes across {len(payload.get('global_themes', []))} global themes.")
    
    # 2. Render Visual Thematic Network Diagram
    png_path = os.path.join(args.out_dir, "thematic_network.png")
    render_thematic_diagram(payload, png_path, lang=lang)
    print(f"[SUCCESS] Rendered 300-DPI Diagram: {png_path}")
    
    # 3. Export 5-Sheet Master Coding Workbook
    excel_path = os.path.join(args.out_dir, "thematic_matrix.xlsx")
    export_thematic_excel(payload, flat_codes, excel_path)
    print(f"[SUCCESS] Exported 5-Sheet Coding Matrix: {excel_path}")
    
    # 4. Compile Defense-Ready Chapter 4 Word Document (.docx)
    docx_filename = "Chapter_4_Qualitative_Findings.docx"
    docx_path = os.path.join(args.out_dir, docx_filename)
    compile_qualitative_chapter4_docx(payload, flat_codes, png_path, docx_path, lang=lang)
    print(f"[SUCCESS] Compiled Defense-Ready Chapter 4: {docx_path}")
    
    # 5. Export Summary JSON
    summary_path = os.path.join(args.out_dir, "qualitative_summary.json")
    summary_data = {
        "study_title": payload.get("study_title", ""),
        "methodology": method,
        "language": lang,
        "sample_size": len(payload.get("participants", [])),
        "global_themes_count": len(payload.get("global_themes", [])),
        "total_basic_codes_count": len(flat_codes),
        "inter_coder_reliability": payload.get("inter_coder_reliability", {}),
        "thematic_hierarchy": summary_hierarchy
    }
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2, ensure_ascii=False)
    print(f"[SUCCESS] Exported Structured Summary: {summary_path}")
    
    print("\n" + "="*70)
    print(f" QUALITATIVE ANALYSIS SUMMARY ({method.upper()})")
    print("="*70)
    print(f" Study: {payload.get('study_title', '')}")
    print(f" Sample Size: N = {len(payload.get('participants', []))} participants")
    if method == "thematic_analysis":
        for gt in payload.get("global_themes", []):
            orgs_n = len(gt.get("organizing_themes", []))
            print(f" - Global Theme: '{gt['name']}' ({orgs_n} Organizing Themes)")
    rel = payload.get("inter_coder_reliability", {})
    if rel:
        print(f" Inter-Coder Reliability: Holsti PAO = {rel.get('holsti_index', 0):.3f} (Agreement = {rel.get('percent_agreement', 0)}%)")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
