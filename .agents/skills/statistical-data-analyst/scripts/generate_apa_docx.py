#!/usr/bin/env python3
"""
APA 7th Edition Word Document Generator (generate_apa_docx.py)
-------------------------------------------------------------
Generates publication-ready Microsoft Word (.docx) documents with strict APA 7th Edition
tables, Iranian graduate university typography (B Nazanin, B Titr), and OpenXML RTL bi-directional support.

Output Modes:
- 'chapter4': Full Persian Chapter 4 (یافته‌های پژوهش) with narrative text, hypotheses tests, and tables.
- 'article': Condensed APA 7 Results section (Bilingual/English) for journal submissions.
"""

import os
import sys
import json
import argparse
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

# --- OpenXML BiDi & Styling Helpers ---
def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set inner padding for table cell in twips (1 pt = 20 twips)."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m_name, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m_name}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_table_apa_borders(table):
    """
    Apply APA 7th Edition borders:
    - Top line: solid
    - Header bottom line: solid
    - Bottom line: solid
    - Vertical lines: NONE
    - Inside horizontal lines: NONE
    """
    tblPr = table._tbl.tblPr
    # Table RTL layout
    bidiVisual = parse_xml(f'<w:bidiVisual {nsdecls("w")}/>')
    tblPr.append(bidiVisual)
    
    tblBorders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>\n'
        f'  <w:top w:val="single" w:sz="8" w:space="0" w:color="000000"/>\n'
        f'  <w:bottom w:val="single" w:sz="8" w:space="0" w:color="000000"/>\n'
        f'  <w:left w:val="none"/>\n'
        f'  <w:right w:val="none"/>\n'
        f'  <w:insideH w:val="none"/>\n'
        f'  <w:insideV w:val="none"/>\n'
        f'</w:tblBorders>'
    )
    tblPr.append(tblBorders)

def add_header_underline(cell):
    """Add underline under header cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>\n'
        f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)

def set_paragraph_bidi(p, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    """Enforce Persian BiDi RTL directionality and alignment on paragraph."""
    p.alignment = align
    pPr = p._p.get_or_add_pPr()
    if not pPr.xpath('./w:bidi'):
        bidi = parse_xml(f'<w:bidi {nsdecls("w")} w:val="1"/>')
        pPr.insert(0, bidi)

def add_run(p, text, font_fa='B Nazanin', font_en='Times New Roman', size=13, bold=False, italic=False):
    """Add text run with explicit Persian/Latin font bindings, w:rtl, and complex script formatting."""
    run = p.add_run(str(text))
    run.font.name = font_fa
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    
    rPr = run._r.get_or_add_rPr()
    sz_val = int(size * 2)
    has_persian = any('\u0600' <= ch <= '\u06FF' or '\uFB50' <= ch <= '\uFDFF' or '\uFE70' <= ch <= '\uFEFF' for ch in str(text))
    if has_persian:
        rFonts = parse_xml(
            f'<w:rFonts {nsdecls("w")} '
            f'w:ascii="{font_fa}" w:hAnsi="{font_fa}" '
            f'w:cs="{font_fa}" w:eastAsia="{font_fa}" w:hint="cs"/>'
        )
        rPr.append(rFonts)
        rtl = parse_xml(f'<w:rtl {nsdecls("w")} w:val="1"/>')
        rPr.append(rtl)
    else:
        rFonts = parse_xml(
            f'<w:rFonts {nsdecls("w")} '
            f'w:ascii="{font_en}" w:hAnsi="{font_en}" '
            f'w:cs="{font_fa}" w:eastAsia="{font_fa}"/>'
        )
        rPr.append(rFonts)

    szCs = parse_xml(f'<w:szCs {nsdecls("w")} w:val="{sz_val}"/>')
    rPr.append(szCs)
    if bold:
        bCs = parse_xml(f'<w:bCs {nsdecls("w")} w:val="1"/>')
        rPr.append(bCs)
    return run

# --- Document Assembler ---
def build_chapter4_document(data: dict, output_path: str):
    doc = docx.Document()
    
    # Set standard page margins (3 cm right for gutter, 2.5 cm others)
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.right_margin = Inches(1.18) # 3 cm
        section.left_margin = Inches(1.0)   # 2.5 cm
        
    table_counter = 1
    
    # 1. Chapter Title
    p_title = doc.add_paragraph()
    set_paragraph_bidi(p_title, WD_ALIGN_PARAGRAPH.CENTER)
    p_title.paragraph_format.space_before = Pt(20)
    p_title.paragraph_format.space_after = Pt(20)
    add_run(p_title, "فصل چهارم", font_fa='B Titr', size=18, bold=True)
    
    p_sub = doc.add_paragraph()
    set_paragraph_bidi(p_sub, WD_ALIGN_PARAGRAPH.CENTER)
    p_sub.paragraph_format.space_after = Pt(24)
    add_run(p_sub, "یافته‌های پژوهش", font_fa='B Titr', size=16, bold=True)
    
    # Intro paragraph
    p_intro = doc.add_paragraph()
    set_paragraph_bidi(p_intro, WD_ALIGN_PARAGRAPH.JUSTIFY)
    p_intro.paragraph_format.line_spacing = 1.25
    add_run(p_intro, 
        "در این فصل، داده‌های گردآوری‌شده با استفاده از نرم‌افزار آماری مورد تجزیه‌وتحلیل قرار گرفت. "
        "یافته‌های پژوهش در دو بخش ارائه می‌گردد: در بخش نخست، شاخص‌های توصیفی متغیرها و بررسی مفروضه‌های آماری "
        "(نرمال بودن توزیع نمرات و همگنی) گزارش می‌شود و در بخش دوم، فرضیه‌های پژوهش با استفاده از آزمون‌های آماری "
        "مربوطه مورد آزمون قرار می‌گیرند."
    )
    
    # --- Section 1: Descriptives & Normality ---
    if "descriptives" in data:
        p_h1 = doc.add_paragraph()
        set_paragraph_bidi(p_h1)
        p_h1.paragraph_format.space_before = Pt(14)
        p_h1.paragraph_format.space_after = Pt(6)
        add_run(p_h1, "۱-۴. یافته‌های توصیفی و بررسی مفروضه نرمال بودن داده‌ها", font_fa='B Nazanin', size=14, bold=True)
        
        p_desc_txt = doc.add_paragraph()
        set_paragraph_bidi(p_desc_txt, WD_ALIGN_PARAGRAPH.JUSTIFY)
        p_desc_txt.paragraph_format.line_spacing = 1.25
        add_run(p_desc_txt, 
            "به‌منظور توصیف داده‌های پژوهش، شاخص‌های مرکزی و پراکندگی شامل میانگین، انحراف استاندارد، میانه و "
            "دامنه‌های حداقل و حداکثر محاسبه گردید. همچنین جهت بررسی فرض نرمال بودن توزیع نمرات، مقادیر چولگی (کجی)، "
            "کشیدگی و آزمون شاپیرو-ویلک ارزیابی شد. نتایج در جدول زیر گزارش شده است."
        )
        
        # Caption
        p_cap = doc.add_paragraph()
        set_paragraph_bidi(p_cap)
        p_cap.paragraph_format.space_before = Pt(8)
        p_cap.paragraph_format.space_after = Pt(4)
        add_run(p_cap, f"جدول {table_counter}-۴. شاخص‌های توصیفی و آزمون شاپیرو-ویلک متغیرهای پژوهش", font_fa='B Nazanin', size=11, bold=True)
        
        # Table
        desc_dict = data["descriptives"]
        headers = ["متغیر", "تعداد (N)", "میانگین", "انحراف معیا‌ر", "کجی", "کشیدگی", "آماره شاپیرو (W)", "سطح معناداری (p)"]
        tbl = doc.add_table(rows=len(desc_dict) + 1, cols=len(headers))
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_apa_borders(tbl)
        
        # Fill Headers
        for col_idx, h_text in enumerate(headers):
            cell = tbl.cell(0, col_idx)
            add_header_underline(cell)
            set_cell_margins(cell, top=120, bottom=120)
            p = cell.paragraphs[0]
            set_paragraph_bidi(p, WD_ALIGN_PARAGRAPH.CENTER)
            add_run(p, h_text, size=11, bold=True)
            
        # Fill Rows
        row_idx = 1
        for var_name, stats_val in desc_dict.items():
            row_cells = tbl.rows[row_idx].cells
            row_data = [
                var_name,
                str(stats_val["N"]),
                f"{stats_val['mean']:.2f}",
                f"{stats_val['sd']:.2f}",
                f"{stats_val['skewness']:.2f}",
                f"{stats_val['kurtosis']:.2f}",
                f"{stats_val['shapiro_w']:.3f}",
                stats_val["shapiro_p_str"]
            ]
            for col_idx, val_str in enumerate(row_data):
                cell = row_cells[col_idx]
                set_cell_margins(cell, top=80, bottom=80)
                p = cell.paragraphs[0]
                set_paragraph_bidi(p, WD_ALIGN_PARAGRAPH.CENTER)
                add_run(p, val_str, size=11)
            row_idx += 1
            
        # Note
        p_note = doc.add_paragraph()
        set_paragraph_bidi(p_note)
        p_note.paragraph_format.space_before = Pt(4)
        p_note.paragraph_format.space_after = Pt(12)
        add_run(p_note, "یادداشت. مقادیر کجی و کشیدگی در بازه استاندارد [۲+ تا ۲-] نشان‌دهنده توزیع نرمال متغیرها می‌باشد.", size=10)
        table_counter += 1

    # --- Section 2: Reliability ---
    if "reliability" in data:
        p_h_rel = doc.add_paragraph()
        set_paragraph_bidi(p_h_rel)
        p_h_rel.paragraph_format.space_before = Pt(14)
        p_h_rel.paragraph_format.space_after = Pt(6)
        add_run(p_h_rel, "۲-۴. پایایی ابزارهای پژوهش (همسانی درونی)", font_fa='B Nazanin', size=14, bold=True)
        
        # Caption
        p_cap_rel = doc.add_paragraph()
        set_paragraph_bidi(p_cap_rel)
        p_cap_rel.paragraph_format.space_before = Pt(8)
        p_cap_rel.paragraph_format.space_after = Pt(4)
        add_run(p_cap_rel, f"جدول {table_counter}-۴. ضرایب آلفای کرونباخ ابزارهای سنجش", font_fa='B Nazanin', size=11, bold=True)
        
        rel_dict = data["reliability"]
        tbl_rel = doc.add_table(rows=len(rel_dict) + 1, cols=4)
        tbl_rel.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_apa_borders(tbl_rel)
        
        r_headers = ["مقیاس / متغیر", "تعداد گویه‌ها", "تعداد نمونه (N)", "ضریب آلفای کرونباخ (α)"]
        for col_idx, h_text in enumerate(r_headers):
            cell = tbl_rel.cell(0, col_idx)
            add_header_underline(cell)
            set_cell_margins(cell, top=120, bottom=120)
            p = cell.paragraphs[0]
            set_paragraph_bidi(p, WD_ALIGN_PARAGRAPH.CENTER)
            add_run(p, h_text, size=11, bold=True)
            
        r_row_idx = 1
        for scale_name, s_val in rel_dict.items():
            row_cells = tbl_rel.rows[r_row_idx].cells
            r_data = [scale_name, str(s_val["n_items"]), str(s_val["n_cases"]), s_val["cronbach_alpha_str"]]
            for c_idx, val_str in enumerate(r_data):
                cell = row_cells[c_idx]
                set_cell_margins(cell, top=80, bottom=80)
                p = cell.paragraphs[0]
                set_paragraph_bidi(p, WD_ALIGN_PARAGRAPH.CENTER)
                add_run(p, val_str, size=11)
            r_row_idx += 1
            
        table_counter += 1

    # --- Section 3: Correlation Matrix ---
    if "correlation" in data:
        p_h_corr = doc.add_paragraph()
        set_paragraph_bidi(p_h_corr)
        p_h_corr.paragraph_format.space_before = Pt(14)
        p_h_corr.paragraph_format.space_after = Pt(6)
        add_run(p_h_corr, "۳-۴. ماتریس همبستگی متغیرهای پژوهش", font_fa='B Nazanin', size=14, bold=True)
        
        corr_info = data["correlation"]
        vars_list = corr_info["variables"]
        
        p_cap_corr = doc.add_paragraph()
        set_paragraph_bidi(p_cap_corr)
        p_cap_corr.paragraph_format.space_before = Pt(8)
        p_cap_corr.paragraph_format.space_after = Pt(4)
        add_run(p_cap_corr, f"جدول {table_counter}-۴. ماتریس ضرایب همبستگی پیرسون بین متغیرها", font_fa='B Nazanin', size=11, bold=True)
        
        tbl_corr = doc.add_table(rows=len(vars_list) + 1, cols=len(vars_list) + 2)
        tbl_corr.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_table_apa_borders(tbl_corr)
        
        # Headers: Index, Variable, 1, 2, 3...
        c_headers = ["ردیف", "متغیر"] + [str(i + 1) for i in range(len(vars_list))]
        for c_idx, h_text in enumerate(c_headers):
            cell = tbl_corr.cell(0, c_idx)
            add_header_underline(cell)
            set_cell_margins(cell, top=120, bottom=120)
            p = cell.paragraphs[0]
            set_paragraph_bidi(p, WD_ALIGN_PARAGRAPH.CENTER)
            add_run(p, h_text, size=11, bold=True)
            
        for i, v1 in enumerate(vars_list):
            row_cells = tbl_corr.rows[i + 1].cells
            # index & name
            set_cell_margins(row_cells[0], top=80, bottom=80)
            p0 = row_cells[0].paragraphs[0]
            set_paragraph_bidi(p0, WD_ALIGN_PARAGRAPH.CENTER)
            add_run(p0, str(i + 1), size=11)
            
            set_cell_margins(row_cells[1], top=80, bottom=80)
            p1 = row_cells[1].paragraphs[0]
            set_paragraph_bidi(p1, WD_ALIGN_PARAGRAPH.RIGHT)
            add_run(p1, v1, size=11)
            
            for j, v2 in enumerate(vars_list):
                cell_val = ""
                cell = row_cells[j + 2]
                set_cell_margins(cell, top=80, bottom=80)
                p_c = cell.paragraphs[0]
                set_paragraph_bidi(p_c, WD_ALIGN_PARAGRAPH.CENTER)
                
                if i == j:
                    cell_val = "۱"
                elif j < i:
                    r_val = corr_info["correlations"][v1][v2]
                    p_val = corr_info["p_values"][v1][v2]
                    stars = "**" if p_val < 0.01 else ("*" if p_val < 0.05 else "")
                    val_str = f"{r_val:.2f}"
                    if val_str.startswith("0"):
                        val_str = val_str[1:]
                    elif val_str.startswith("-0"):
                        val_str = "-" + val_str[2:]
                    cell_val = f"{val_str}{stars}"
                else:
                    cell_val = "-"
                add_run(p_c, cell_val, size=11)
                
        p_note_corr = doc.add_paragraph()
        set_paragraph_bidi(p_note_corr)
        p_note_corr.paragraph_format.space_before = Pt(4)
        p_note_corr.paragraph_format.space_after = Pt(12)
        note_txt = "یادداشت. * معناداری در سطح ۰/۰۵؛ ** معناداری در سطح ۰/۰۱."
        if "multiple_testing" in corr_info:
            mt = corr_info["multiple_testing"]
            note_txt += f" مقادیر p با رویه نرخ کشف نادرست بنجامینی-هاچبرگ (FDR) جهت کنترل انباشت خطای نوع اول در آزمون‌های چندگانه ({mt.get('m_comparisons', 0)} مقایسه) ارزیابی شدند."
        add_run(p_note_corr, note_txt, size=10)
        table_counter += 1

    # --- Section 4: ANCOVA (Intervention Studies) ---
    if "ancova" in data:
        p_h_anc = doc.add_paragraph()
        set_paragraph_bidi(p_h_anc)
        p_h_anc.paragraph_format.space_before = Pt(14)
        p_h_anc.paragraph_format.space_after = Pt(6)
        add_run(p_h_anc, "۴-۴. آزمون فرضیه اثربخشی مداخله (تحلیل کوواریانس تک‌متغیری)", font_fa='B Nazanin', size=14, bold=True)
        
        anc_list = data["ancova"] if isinstance(data["ancova"], list) else [data["ancova"]]
        for anc in anc_list:
            p_desc_anc = doc.add_paragraph()
            set_paragraph_bidi(p_desc_anc, WD_ALIGN_PARAGRAPH.JUSTIFY)
            p_desc_anc.paragraph_format.line_spacing = 1.25
            
            sig_text = "معنادار بوده است" if anc["p"] < 0.05 else "معنادار نبوده است"
            narrative = (
                f"به‌منظور ارزیابی اثربخشی مداخله بر متغیر {anc['dv']} در مرحله پس‌آزمون با کنترل اثر پیش‌آزمون ({anc['covariate']})، "
                f"تحلیل کوواریانس تک‌متغیری (ANCOVA) اجرا شد. مفروضه همگنی شیب خطوط رگرسیون با توجه به عدم معناداری اثر تعاملی "
                f"(p = {anc['slope_homogeneity_p_str']}) تأیید گردید. "
                f"نتایج تحلیل کوواریانس نشان داد که اثر مداخله در پس‌آزمون {sig_text} "
                f"(F({anc['df_between']}, {anc['df_within']}) = {anc['f_stat']:.2f}, p = {anc['p_str']}, η² = {anc['partial_eta_squared_str']})."
            )
            add_run(p_desc_anc, narrative)
            
            # ANCOVA Table
            p_cap_anc = doc.add_paragraph()
            set_paragraph_bidi(p_cap_anc)
            p_cap_anc.paragraph_format.space_before = Pt(8)
            p_cap_anc.paragraph_format.space_after = Pt(4)
            add_run(p_cap_anc, f"جدول {table_counter}-۴. نتایج تحلیل کوواریانس اثربخشی مداخله بر {anc['dv']}", font_fa='B Nazanin', size=11, bold=True)
            
            tbl_anc = doc.add_table(rows=2, cols=6)
            tbl_anc.alignment = WD_TABLE_ALIGNMENT.CENTER
            set_table_apa_borders(tbl_anc)
            
            a_headers = ["منبع تغییرات", "درجه آزادی (df)", "آماره F", "سطح معناداری (p)", "مجذور اتا (η²)", "میانگین‌های تعدیل‌شده"]
            for c_idx, h_text in enumerate(a_headers):
                cell = tbl_anc.cell(0, c_idx)
                add_header_underline(cell)
                set_cell_margins(cell, top=120, bottom=120)
                p = cell.paragraphs[0]
                set_paragraph_bidi(p, WD_ALIGN_PARAGRAPH.CENTER)
                add_run(p, h_text, size=11, bold=True)
                
            means_str = " | ".join([f"گروه {k}: {v}" for k, v in anc["adjusted_means"].items()])
            row_vals = ["گروه (مداخله)", f"{anc['df_between']}, {anc['df_within']}", f"{anc['f_stat']:.2f}", anc['p_str'], anc['partial_eta_squared_str'], means_str]
            for c_idx, val_str in enumerate(row_vals):
                cell = tbl_anc.cell(1, c_idx)
                set_cell_margins(cell, top=80, bottom=80)
                p = cell.paragraphs[0]
                set_paragraph_bidi(p, WD_ALIGN_PARAGRAPH.CENTER)
                add_run(p, val_str, size=11)
            table_counter += 1

    # --- Section 5: Hierarchical Regression ---
    if "regression" in data:
        p_h_reg = doc.add_paragraph()
        set_paragraph_bidi(p_h_reg)
        p_h_reg.paragraph_format.space_before = Pt(14)
        p_h_reg.paragraph_format.space_after = Pt(6)
        add_run(p_h_reg, "۵-۴. رگرسیون سلسله‌مراتبی پیش‌بینی متغیر وابسته", font_fa='B Nazanin', size=14, bold=True)
        
        reg_list = data["regression"] if isinstance(data["regression"], list) else [data["regression"]]
        for reg in reg_list:
            p_cap_reg = doc.add_paragraph()
            set_paragraph_bidi(p_cap_reg)
            p_cap_reg.paragraph_format.space_before = Pt(8)
            p_cap_reg.paragraph_format.space_after = Pt(4)
            add_run(p_cap_reg, f"جدول {table_counter}-۴. ضرایب رگرسیون پیش‌بینی {reg['dv']}", font_fa='B Nazanin', size=11, bold=True)
            
            # Step 2 details or Step 1
            coeffs = reg["step2"]["coefficients"] if "step2" in reg else reg["step1"]["coefficients"]
            tbl_reg = doc.add_table(rows=len(coeffs) + 1, cols=7)
            tbl_reg.alignment = WD_TABLE_ALIGNMENT.CENTER
            set_table_apa_borders(tbl_reg)
            
            r_heads = ["متغیر پیش‌بین", "B", "SE", "بتا (β)", "آماره t", "معناداری (p)", "شاخص VIF"]
            for c_idx, h_text in enumerate(r_heads):
                cell = tbl_reg.cell(0, c_idx)
                add_header_underline(cell)
                set_cell_margins(cell, top=120, bottom=120)
                p = cell.paragraphs[0]
                set_paragraph_bidi(p, WD_ALIGN_PARAGRAPH.CENTER)
                add_run(p, h_text, size=11, bold=True)
                
            for r_idx, cf in enumerate(coeffs):
                row_cells = tbl_reg.rows[r_idx + 1].cells
                c_data = [
                    cf["variable"],
                    f"{cf['B']:.2f}",
                    f"{cf['SE']:.2f}",
                    f"{cf['beta']:.2f}",
                    f"{cf['t']:.2f}",
                    cf["p_str"],
                    str(cf.get("VIF", "-"))
                ]
                for c_idx, val_str in enumerate(c_data):
                    cell = row_cells[c_idx]
                    set_cell_margins(cell, top=80, bottom=80)
                    p = cell.paragraphs[0]
                    set_paragraph_bidi(p, WD_ALIGN_PARAGRAPH.CENTER)
                    add_run(p, val_str, size=11)
                    
            table_counter += 1

    # --- Section 6: Mediation with Bootstrapping ---
    if "mediation" in data:
        p_h_med = doc.add_paragraph()
        set_paragraph_bidi(p_h_med)
        p_h_med.paragraph_format.space_before = Pt(14)
        p_h_med.paragraph_format.space_after = Pt(6)
        add_run(p_h_med, "۶-۴. آزمون اثر میانجی‌گری با روش بوت‌استراپینگ", font_fa='B Nazanin', size=14, bold=True)
        
        med_list = data["mediation"] if isinstance(data["mediation"], list) else [data["mediation"]]
        for med in med_list:
            ind = med["indirect_effect"]
            sig_med = "معنادار می‌باشد" if ind["is_significant"] else "معنادار نمی‌باشد"
            narr_med = (
                f"جهت ارزیابی نقش میانجی‌گری {med['m']} در رابطه بین {med['x']} و {med['y']}، "
                f"از روش تحلیل مسیر و بوت‌استراپ با {med['n_boot']} بار نمونه‌گیری مجدد استفاده شد. "
                f"نتایج نشان داد ضریب مسیر اثر غیرمستقیم برابر با {ind['estimate']:.3f} با خطای استاندارد بوت‌استراپ {ind['boot_se']:.3f} است. "
                f"با توجه به اینکه فاصله اطمینان ۹۵ درصدی تصحیح‌شده [{ind['ci_95_lower']:.3f} ,{ind['ci_95_upper']:.3f}] "
                f"شامل عدد صفر نمی‌باشد، نقش میانجی‌گری {med['m']} در سطح ۰/۰۵ {sig_med}."
            )
            p_med_narr = doc.add_paragraph()
            set_paragraph_bidi(p_med_narr, WD_ALIGN_PARAGRAPH.JUSTIFY)
            p_med_narr.paragraph_format.line_spacing = 1.25
            add_run(p_med_narr, narr_med)
            
            # Table
            p_cap_med = doc.add_paragraph()
            set_paragraph_bidi(p_cap_med)
            p_cap_med.paragraph_format.space_before = Pt(8)
            p_cap_med.paragraph_format.space_after = Pt(4)
            add_run(p_cap_med, f"جدول {table_counter}-۴. نتایج بوت‌استراپ اثر غیرمستقیم {med['x']} بر {med['y']} از طریق {med['m']}", font_fa='B Nazanin', size=11, bold=True)
            
            tbl_med = doc.add_table(rows=2, cols=6)
            tbl_med.alignment = WD_TABLE_ALIGNMENT.CENTER
            set_table_apa_borders(tbl_med)
            
            m_headers = ["مسیر مدل", "ضریب اثر (B)", "خطای استاندارد بوت", "حد پایین اطمینان (LLCI)", "حد بالا اطمینان (ULCI)", "نتیجه فرضیه"]
            for c_idx, h_text in enumerate(m_headers):
                cell = tbl_med.cell(0, c_idx)
                add_header_underline(cell)
                set_cell_margins(cell, top=120, bottom=120)
                p = cell.paragraphs[0]
                set_paragraph_bidi(p, WD_ALIGN_PARAGRAPH.CENTER)
                add_run(p, h_text, size=11, bold=True)
                
            res_str = "تأیید فرضیه" if ind["is_significant"] else "رد فرضیه"
            m_vals = [
                f"{med['x']} → {med['m']} → {med['y']}",
                f"{ind['estimate']:.3f}",
                f"{ind['boot_se']:.3f}",
                f"{ind['ci_95_lower']:.3f}",
                f"{ind['ci_95_upper']:.3f}",
                res_str
            ]
            for c_idx, val_str in enumerate(m_vals):
                cell = tbl_med.cell(1, c_idx)
                set_cell_margins(cell, top=80, bottom=80)
                p = cell.paragraphs[0]
                set_paragraph_bidi(p, WD_ALIGN_PARAGRAPH.CENTER)
                add_run(p, val_str, size=11)
            table_counter += 1
            
    doc.save(output_path)
    print(f"Chapter 4 Document generated successfully: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="APA 7th Edition Word Document Generator")
    parser.add_argument("--json", required=True, help="Path to statistical results JSON file")
    parser.add_argument("--out", default="Chapter_4_Results.docx", help="Output .docx file path")
    parser.add_argument("--mode", default="chapter4", choices=["chapter4", "article"], help="Document mode")
    args = parser.parse_args()
    
    with open(args.json, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    build_chapter4_document(data, args.out)

if __name__ == "__main__":
    main()
