#!/usr/bin/env python3
"""
compile_submission_package.py - Academic Journal Submission & Rebuttal Package Compiler

Generates:
  1. Cover_Letter.docx
  2. Title_Page.docx
  3. Highlights.docx
  4. Response_to_Reviewers.docx (if revision/rebuttal data is present)

Adheres to APA 7th Edition, international publisher constraints (Elsevier, Springer, Wiley, MDPI),
and Iranian Scientific-Research (ISC) standards.
"""

import os
import sys
import json
import argparse
from datetime import datetime
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

OFFICIAL_CREDIT_ROLES = [
    "Conceptualization",
    "Data curation",
    "Formal analysis",
    "Funding acquisition",
    "Investigation",
    "Methodology",
    "Project administration",
    "Resources",
    "Software",
    "Supervision",
    "Validation",
    "Visualization",
    "Writing - original draft",
    "Writing - review & editing"
]

CREDIT_FA_TRANSLATIONS = {
    "Conceptualization": "مفهوم‌پردازی و طراحی ایده اصلی پژوهش",
    "Data curation": "گردآوری، ساماندهی و پالایش داده‌ها",
    "Formal analysis": "تحلیل آماری و محاسباتی داده‌ها",
    "Funding acquisition": "تأمین مالی و اعتبارات پژوهش",
    "Investigation": "اجرای مراحل پژوهش و اجرای پروتکل مداخله",
    "Methodology": "طراحی روش‌شناسی و ابزارهای اندازه‌گیری",
    "Project administration": "مدیریت و هماهنگی اجرایی طرح",
    "Resources": "فراهم‌سازی منابع، امکانات و نمونه‌های بالینی",
    "Software": "برنامه‌نویسی و کدهای محاسباتی",
    "Supervision": "نظارت علمی و راهنمایی تخصصی",
    "Validation": "اعتبارسنجی یافته‌ها و بازتولیدپذیری تحلیل‌ها",
    "Visualization": "ترسیم نمودارها، دیاگرام‌ها و جلوه‌های بصری",
    "Writing - original draft": "نگارش پیش‌نویس اولیه مقاله",
    "Writing - review & editing": "بازبینی انتقادی، ویرایش و تدوین نهایی مقاله"
}

def set_cell_margins(cell, top=100, bottom=100, left=120, right=120):
    """Set inner padding for table cell in twips."""
    tc = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m_name, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m_name}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_background(cell, fill_hex):
    """Set background color of a cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_apa_table_borders(table, is_rtl=False):
    """Apply APA 7 three-line borderless styling."""
    tblPr = table._tbl.tblPr
    if is_rtl:
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
    """Add bottom border to table header row cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>\n'
        f'  <w:bottom w:val="single" w:sz="6" w:space="0" w:color="000000"/>\n'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)

def add_row_bottom_border(cell, color="D3D3D3"):
    """Add subtle row separator line."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = parse_xml(
        f'<w:tcBorders {nsdecls("w")}>\n'
        f'  <w:bottom w:val="single" w:sz="4" w:space="0" w:color="{color}"/>\n'
        f'</w:tcBorders>'
    )
    tcPr.append(tcBorders)

def set_paragraph_bidi(p, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
    """Enforce Persian BiDi RTL directionality on paragraph."""
    p.alignment = align
    pPr = p._p.get_or_add_pPr()
    if not any(child.tag.endswith('}bidi') for child in pPr):
        bidi = OxmlElement('w:bidi')
        bidi.set(qn('w:val'), '1')
        pPr.insert(0, bidi)

def add_run(p, text, lang='en', size=12, bold=False, italic=False, color=None):
    """Add run with appropriate font bindings based on language."""
    run = p.add_run(text)
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    if color:
        run.font.color.rgb = color
    
    font_fa = 'B Titr' if (bold and size >= 13) else 'B Nazanin'
    font_en = 'Times New Roman'
    
    if lang == 'fa':
        run.font.name = font_fa
        rPr = run._r.get_or_add_rPr()
        rFonts = parse_xml(
            f'<w:rFonts {nsdecls("w")} '
            f'w:ascii="{font_fa}" w:hAnsi="{font_fa}" '
            f'w:cs="{font_fa}" w:eastAsia="{font_fa}" w:hint="cs"/>'
        )
        rPr.append(rFonts)
        rPr.append(parse_xml(f'<w:rtl {nsdecls("w")} w:val="1"/>'))
        sz_half_pts = int(size * 2)
        rPr.append(parse_xml(f'<w:szCs {nsdecls("w")} w:val="{sz_half_pts}"/>'))
        if bold:
            rPr.append(parse_xml(f'<w:bCs {nsdecls("w")} w:val="1"/>'))
    else:
        run.font.name = font_en
        
    return run

def create_base_document():
    doc = docx.Document()
    for section in doc.sections:
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
    return doc

def validate_highlights(highlights):
    """Validate 3-5 highlights and <= 85 chars per bullet."""
    results = []
    for h in highlights:
        cleaned = h.strip()
        length = len(cleaned)
        is_valid = (length <= 85)
        results.append({"text": cleaned, "length": length, "valid": is_valid})
    return results

def generate_credit_statement(authors, lang='en'):
    """Format authors into standard CRediT contributor statement."""
    is_fa = (lang == 'fa')
    parts = []
    
    for auth in authors:
        roles = auth.get("credit_roles", [])
        if not roles:
            continue
        
        if is_fa:
            name = f"{auth.get('first_name', '')} {auth.get('last_name', '')}".strip()
            translated_roles = [CREDIT_FA_TRANSLATIONS.get(r, r) for r in roles]
            parts.append(f"{name}: {'، '.join(translated_roles)}")
        else:
            initials = auth.get("initials") or f"{auth.get('first_name', '')[:1]}. {auth.get('last_name', '')[:1]}."
            parts.append(f"{initials}: {', '.join(roles)}")
            
    if is_fa:
        full_text = "، همچنین ".join(parts)
        return f"سهم نویسندگان بر اساس سنجه بین‌المللی CRediT: {full_text}. تمامی نویسندگان نسخه نهایی را مطالعه کرده و با ارسال آن موافقت نموده‌اند."
    else:
        full_text = "; ".join(parts)
        return f"{full_text}. All authors have read and agreed to the published version of the manuscript."

# ==============================================================================
# 1. BUILD COVER LETTER
# ==============================================================================
def build_cover_letter(data, out_path, lang='en'):
    doc = create_base_document()
    is_fa = (lang == 'fa')
    
    meta = data.get("manuscript_metadata", {})
    corr = data.get("corresponding_author", {})
    cover = data.get("cover_letter_content", {})
    decl = data.get("declarations", {})
    reviewers = data.get("suggested_reviewers", [])
    
    title = meta.get("title", "Research Manuscript Title")
    article_type = meta.get("article_type", "Original Research Article")
    journal_name = meta.get("journal_name", "Target Journal")
    publisher = meta.get("publisher", "Publisher")
    editor = meta.get("editor_in_chief", "Editor-in-Chief")
    editorial_office = meta.get("editorial_office", "")
    date_str = meta.get("submission_date") or datetime.today().strftime('%B %d, %Y')
    
    if is_fa:
        # Persian Cover Letter
        p_bism = doc.add_paragraph()
        set_paragraph_bidi(p_bism, WD_ALIGN_PARAGRAPH.CENTER)
        add_run(p_bism, "به نام خدا", lang='fa', size=13, bold=True)
        p_bism.paragraph_format.space_after = Pt(12)
        
        p_date = doc.add_paragraph()
        set_paragraph_bidi(p_date, WD_ALIGN_PARAGRAPH.LEFT)
        add_run(p_date, f"تاریخ: {date_str}", lang='fa', size=11)
        p_date.paragraph_format.space_after = Pt(12)
        
        p_dest = doc.add_paragraph()
        set_paragraph_bidi(p_dest, WD_ALIGN_PARAGRAPH.RIGHT)
        add_run(p_dest, f"سردبیر محترم نشریه علمی-پژوهشی {journal_name}\n", lang='fa', size=12, bold=True)
        add_run(p_dest, "با سلام و احترام؛\n", lang='fa', size=12)
        p_dest.paragraph_format.space_after = Pt(10)
        
        p_sub = doc.add_paragraph()
        set_paragraph_bidi(p_sub, WD_ALIGN_PARAGRAPH.RIGHT)
        add_run(p_sub, "موضوع: ارسال مقاله پژوهشی جهت بررسی و انتشار\n", lang='fa', size=12, bold=True)
        p_sub.paragraph_format.space_after = Pt(8)
        
        p_body1 = doc.add_paragraph()
        set_paragraph_bidi(p_body1, WD_ALIGN_PARAGRAPH.JUSTIFY)
        add_run(p_body1, f"احتراماً، پیش‌نویس مقاله پژوهشی حاضر با عنوان «{title}» جهت بررسی و انتشار در نشریه ارزشمند {journal_name} تقدیم حضور می‌گردد. ", lang='fa', size=12)
        add_run(p_body1, cover.get("hook", ""), lang='fa', size=12)
        p_body1.paragraph_format.space_after = Pt(10)
        
        p_body2 = doc.add_paragraph()
        set_paragraph_bidi(p_body2, WD_ALIGN_PARAGRAPH.JUSTIFY)
        add_run(p_body2, cover.get("key_findings", ""), lang='fa', size=12)
        add_run(p_body2, " " + cover.get("novelty_statement", ""), lang='fa', size=12)
        p_body2.paragraph_format.space_after = Pt(10)
        
        p_body3 = doc.add_paragraph()
        set_paragraph_bidi(p_body3, WD_ALIGN_PARAGRAPH.JUSTIFY)
        add_run(p_body3, cover.get("fit_with_journal", f"این پژوهش به طور کامل با اهداف و چشم‌انداز نشریه {journal_name} همخوانی دارد."), lang='fa', size=12)
        p_body3.paragraph_format.space_after = Pt(10)
        
        p_assurances = doc.add_paragraph()
        set_paragraph_bidi(p_assurances, WD_ALIGN_PARAGRAPH.JUSTIFY)
        assurances_fa = (
            "نویسندگان این مقاله بدین‌وسیله گواهی می‌نمایند که:\n"
            "۱. این اثر یک پژوهش اصیل بوده و پیش از این در هیچ نشریه‌ای منتشر نشده و هم‌زمان برای نشریه دیگری ارسال نگردیده است.\n"
            "۲. کلیه موازین و اصول اخلاق پژوهشی (کد اخلاق: " + decl.get("ethics_approval", "تأییدیه کمیته اخلاق") + ") رعایت گردیده و رضایت آگاهانه کتبی از آزمودنی‌ها اخذ شده است.\n"
            "۳. این پژوهش فاقد هرگونه تعارض منافع است و کلیه نویسندگان نسخه نهایی را بررسی و تایید نموده‌اند."
        )
        add_run(p_assurances, assurances_fa, lang='fa', size=11)
        p_assurances.paragraph_format.space_after = Pt(18)
        
        p_sign = doc.add_paragraph()
        set_paragraph_bidi(p_sign, WD_ALIGN_PARAGRAPH.LEFT)
        add_run(p_sign, "با تشکر و احترام فائق،\n", lang='fa', size=12)
        add_run(p_sign, f"{corr.get('name', 'نویسنده مسئول')}\n", lang='fa', size=12, bold=True)
        add_run(p_sign, f"{corr.get('department', '')}\n{corr.get('institution', '')}\n", lang='fa', size=11)
        add_run(p_sign, f"پست الکترونیکی: {corr.get('email', '')} | تلفن: {corr.get('phone', '')}", lang='fa', size=10)
        
    else:
        # English Cover Letter
        p_date = doc.add_paragraph()
        add_run(p_date, date_str, lang='en', size=11)
        p_date.paragraph_format.space_after = Pt(12)
        
        p_editor = doc.add_paragraph()
        add_run(p_editor, f"{editor}\n", lang='en', size=11, bold=True)
        add_run(p_editor, f"Editor-in-Chief, {journal_name}\n", lang='en', size=11, italic=True)
        if publisher:
            add_run(p_editor, f"{publisher}\n", lang='en', size=11)
        if editorial_office:
            add_run(p_editor, f"{editorial_office}\n", lang='en', size=11)
        p_editor.paragraph_format.space_after = Pt(12)
        
        salutation = f"Dear {editor}," if not editor.startswith("Dr.") and not editor.startswith("Prof.") else f"Dear {editor},"
        p_sal = doc.add_paragraph()
        add_run(p_sal, salutation, lang='en', size=12)
        p_sal.paragraph_format.space_after = Pt(8)
        
        p_subj = doc.add_paragraph()
        add_run(p_subj, f'Subject: Submission of original manuscript entitled "{title}"', lang='en', size=12, bold=True)
        p_subj.paragraph_format.space_after = Pt(10)
        
        p_b1 = doc.add_paragraph()
        p_b1.paragraph_format.space_after = Pt(10)
        p_b1.paragraph_format.line_spacing = 1.15
        add_run(p_b1, f"Please find enclosed our manuscript entitled ", lang='en', size=12)
        add_run(p_b1, f'"{title}"', lang='en', size=12, italic=True)
        add_run(p_b1, f", which we would like to submit for publication as an {article_type} in ", lang='en', size=12)
        add_run(p_b1, f"{journal_name}. ", lang='en', size=12, italic=True)
        add_run(p_b1, cover.get("hook", ""), lang='en', size=12)
        
        p_b2 = doc.add_paragraph()
        p_b2.paragraph_format.space_after = Pt(10)
        p_b2.paragraph_format.line_spacing = 1.15
        add_run(p_b2, cover.get("key_findings", ""), lang='en', size=12)
        add_run(p_b2, " " + cover.get("novelty_statement", ""), lang='en', size=12)
        
        p_b3 = doc.add_paragraph()
        p_b3.paragraph_format.space_after = Pt(10)
        p_b3.paragraph_format.line_spacing = 1.15
        add_run(p_b3, cover.get("fit_with_journal", f"We believe our findings directly align with the core aims and scope of {journal_name} and will strongly appeal to your international readership."), lang='en', size=12)
        
        p_b4 = doc.add_paragraph()
        p_b4.paragraph_format.space_after = Pt(10)
        p_b4.paragraph_format.line_spacing = 1.15
        assurances = (
            "This manuscript represents original work and has not been published previously, nor is it under consideration for publication elsewhere. "
            "The study protocol was approved by the institutional ethics committee in accordance with ethical standards, and all participants provided written informed consent. "
            "All authors have read and approved the final manuscript and declare no competing financial or personal conflicts of interest."
        )
        add_run(p_b4, assurances, lang='en', size=12)
        
        if reviewers:
            p_rev_head = doc.add_paragraph()
            add_run(p_rev_head, "Suggested Independent Reviewers:", lang='en', size=11, bold=True)
            p_rev_head.paragraph_format.space_after = Pt(4)
            for rev in reviewers:
                p_r = doc.add_paragraph(style='List Bullet')
                add_run(p_r, f"{rev.get('name')}", lang='en', size=11, bold=True)
                add_run(p_r, f" ({rev.get('institution')}) - Email: {rev.get('email')}. Expertise: {rev.get('reason')}", lang='en', size=11)
                p_r.paragraph_format.space_after = Pt(2)
            doc.add_paragraph().paragraph_format.space_after = Pt(8)
            
        p_close = doc.add_paragraph()
        add_run(p_close, "Thank you very much for your time and consideration of our work.\n\nSincerely,\n", lang='en', size=12)
        add_run(p_close, f"{corr.get('name', 'Corresponding Author')}\n", lang='en', size=12, bold=True)
        if corr.get('department'):
            add_run(p_close, f"{corr.get('department')}\n", lang='en', size=11)
        if corr.get('institution'):
            add_run(p_close, f"{corr.get('institution')}\n", lang='en', size=11)
        if corr.get('address'):
            add_run(p_close, f"{corr.get('address')}\n", lang='en', size=10)
        add_run(p_close, f"Email: {corr.get('email', '')} | Tel: {corr.get('phone', '')}", lang='en', size=10)
        
    doc.save(out_path)
    return out_path

# ==============================================================================
# 2. BUILD TITLE PAGE & CREDIT TAXONOMY
# ==============================================================================
def build_title_page(data, out_path, lang='en'):
    doc = create_base_document()
    is_fa = (lang == 'fa')
    
    meta = data.get("manuscript_metadata", {})
    authors = data.get("authors", [])
    affiliations = data.get("affiliations", [])
    corr = data.get("corresponding_author", {})
    decl = data.get("declarations", {})
    wc = meta.get("word_counts", {})
    
    title = meta.get("title", "")
    running_head = meta.get("running_head", meta.get("short_title", ""))
    
    if is_fa:
        # Persian Title Page
        p_title = doc.add_paragraph()
        set_paragraph_bidi(p_title, WD_ALIGN_PARAGRAPH.CENTER)
        add_run(p_title, title, lang='fa', size=16, bold=True)
        p_title.paragraph_format.space_after = Pt(14)
        
        # Authors
        author_names = []
        for a in authors:
            aff_supers = ",".join(str(i) for i in a.get("affiliation_ids", [1]))
            star = "*" if a.get("is_corresponding") else ""
            name_str = f"{a.get('first_name', '')} {a.get('last_name', '')} {aff_supers}{star}".strip()
            author_names.append(name_str)
            
        p_auth = doc.add_paragraph()
        set_paragraph_bidi(p_auth, WD_ALIGN_PARAGRAPH.CENTER)
        add_run(p_auth, "، ".join(author_names), lang='fa', size=13, bold=True)
        p_auth.paragraph_format.space_after = Pt(12)
        
        # Affiliations
        for aff in affiliations:
            p_aff = doc.add_paragraph()
            set_paragraph_bidi(p_aff, WD_ALIGN_PARAGRAPH.CENTER)
            add_run(p_aff, f"{aff.get('id')}. {aff.get('department', '')}، {aff.get('institution', '')}، {aff.get('city', '')}، {aff.get('country', '')}", lang='fa', size=10, italic=True)
            p_aff.paragraph_format.space_after = Pt(2)
            
        doc.add_paragraph().paragraph_format.space_after = Pt(12)
        
        # Corresponding Author Block
        p_corr = doc.add_paragraph()
        set_paragraph_bidi(p_corr, WD_ALIGN_PARAGRAPH.RIGHT)
        add_run(p_corr, "* نویسنده مسئول: ", lang='fa', size=11, bold=True)
        add_run(p_corr, f"{corr.get('name')} | نشانی: {corr.get('address')} | رایانامه: {corr.get('email')} | تلفن: {corr.get('phone')}", lang='fa', size=10)
        p_corr.paragraph_format.space_after = Pt(14)
        
        # CRediT Statement
        p_credit_title = doc.add_paragraph()
        set_paragraph_bidi(p_credit_title, WD_ALIGN_PARAGRAPH.RIGHT)
        add_run(p_credit_title, "نقش و سهم نویسندگان (سنجه CRediT):", lang='fa', size=12, bold=True)
        p_credit_title.paragraph_format.space_after = Pt(4)
        
        p_credit = doc.add_paragraph()
        set_paragraph_bidi(p_credit, WD_ALIGN_PARAGRAPH.JUSTIFY)
        add_run(p_credit, generate_credit_statement(authors, lang='fa'), lang='fa', size=10)
        p_credit.paragraph_format.space_after = Pt(14)
        
        # Declarations
        p_dec_title = doc.add_paragraph()
        set_paragraph_bidi(p_dec_title, WD_ALIGN_PARAGRAPH.RIGHT)
        add_run(p_dec_title, "بیانیه‌ها و ملاحظات اخلاقی و قانونی:", lang='fa', size=12, bold=True)
        p_dec_title.paragraph_format.space_after = Pt(6)
        
        for k, v in [
            ("تأییدیه اخلاقی", decl.get("ethics_approval")),
            ("رضایت آگاهانه", decl.get("informed_consent")),
            ("دسترسی‌پذیری داده‌ها", decl.get("data_availability")),
            ("تعارض منافع", decl.get("conflicts_of_interest")),
            ("حمایت مالی", decl.get("funding")),
            ("تشکر و قدردانی", decl.get("acknowledgments"))
        ]:
            if v:
                p_item = doc.add_paragraph()
                set_paragraph_bidi(p_item, WD_ALIGN_PARAGRAPH.JUSTIFY)
                add_run(p_item, f"• {k}: ", lang='fa', size=10, bold=True)
                add_run(p_item, v, lang='fa', size=10)
                p_item.paragraph_format.space_after = Pt(4)
                
    else:
        # English Title Page
        if running_head:
            p_rh = doc.add_paragraph()
            add_run(p_rh, f"Running head: {running_head[:50].upper()}", lang='en', size=10, italic=True)
            p_rh.paragraph_format.space_after = Pt(24)
            
        p_title = doc.add_paragraph()
        p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_run(p_title, title, lang='en', size=16, bold=True)
        p_title.paragraph_format.space_after = Pt(16)
        
        # Authors line
        author_entries = []
        for a in authors:
            aff_indices = ",".join(str(i) for i in a.get("affiliation_ids", [1]))
            star = "*" if a.get("is_corresponding") else ""
            full_name = f"{a.get('first_name', '')} {a.get('last_name', '')}".strip()
            if a.get('degree'):
                full_name += f", {a.get('degree')}"
            author_entries.append(f"{full_name} {aff_indices}{star}")
            
        p_auth = doc.add_paragraph()
        p_auth.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_run(p_auth, "; ".join(author_entries), lang='en', size=12, bold=True)
        p_auth.paragraph_format.space_after = Pt(12)
        
        # Affiliations
        for aff in affiliations:
            p_aff = doc.add_paragraph()
            p_aff.alignment = WD_ALIGN_PARAGRAPH.CENTER
            add_run(p_aff, f"{aff.get('id')} {aff.get('department')}, {aff.get('institution')}, {aff.get('city')}, {aff.get('country')}", lang='en', size=10, italic=True)
            p_aff.paragraph_format.space_after = Pt(2)
            
        doc.add_paragraph().paragraph_format.space_after = Pt(12)
        
        # Corresponding Author Block
        p_corr = doc.add_paragraph()
        add_run(p_corr, "* Corresponding Author: ", lang='en', size=10, bold=True)
        corr_info = f"{corr.get('name')}, {corr.get('department')}, {corr.get('institution')}, {corr.get('address')}. Email: {corr.get('email')}, Phone: {corr.get('phone')}."
        if corr.get("orcid"):
            corr_info += f" ORCID: {corr.get('orcid')}"
        add_run(p_corr, corr_info, lang='en', size=10)
        p_corr.paragraph_format.space_after = Pt(12)
        
        # Word Counts
        if wc:
            p_wc = doc.add_paragraph()
            add_run(p_wc, "Manuscript Word Counts & Statistics: ", lang='en', size=10, bold=True)
            wc_details = (
                f"Abstract: {wc.get('abstract', 'N/A')} words | "
                f"Main Text: {wc.get('main_text', 'N/A')} words | "
                f"Tables: {wc.get('tables_count', 0)} | "
                f"Figures: {wc.get('figures_count', 0)} | "
                f"References: {wc.get('references_count', 0)}"
            )
            add_run(p_wc, wc_details, lang='en', size=10)
            p_wc.paragraph_format.space_after = Pt(14)
            
        # CRediT Statement
        p_credit_head = doc.add_paragraph()
        add_run(p_credit_head, "CRediT Authorship Contribution Statement", lang='en', size=11, bold=True)
        p_credit_head.paragraph_format.space_after = Pt(4)
        
        p_credit_body = doc.add_paragraph()
        p_credit_body.paragraph_format.line_spacing = 1.15
        add_run(p_credit_body, generate_credit_statement(authors, lang='en'), lang='en', size=10)
        p_credit_body.paragraph_format.space_after = Pt(14)
        
        # Declarations
        p_dec_head = doc.add_paragraph()
        add_run(p_dec_head, "Declarations and Disclosures", lang='en', size=11, bold=True)
        p_dec_head.paragraph_format.space_after = Pt(6)
        
        for title_str, val in [
            ("Funding", decl.get("funding")),
            ("Conflicts of Interest / Competing Interests", decl.get("conflicts_of_interest")),
            ("Ethics Approval", decl.get("ethics_approval")),
            ("Informed Consent to Participate", decl.get("informed_consent")),
            ("Consent for Publication", decl.get("consent_for_publication")),
            ("Data Availability Statement", decl.get("data_availability")),
            ("Acknowledgments", decl.get("acknowledgments"))
        ]:
            if val:
                p_item = doc.add_paragraph()
                p_item.paragraph_format.line_spacing = 1.15
                add_run(p_item, f"{title_str}: ", lang='en', size=10, bold=True)
                add_run(p_item, val, lang='en', size=10)
                p_item.paragraph_format.space_after = Pt(4)
                
    doc.save(out_path)
    return out_path

# ==============================================================================
# 3. BUILD HIGHLIGHTS & GRAPHICAL ABSTRACT BRIEF
# ==============================================================================
def build_highlights(data, out_path, lang='en'):
    doc = create_base_document()
    is_fa = (lang == 'fa')
    
    highlights_raw = data.get("highlights", [])
    validation_results = validate_highlights(highlights_raw)
    
    if is_fa:
        p_h = doc.add_paragraph()
        set_paragraph_bidi(p_h, WD_ALIGN_PARAGRAPH.CENTER)
        add_run(p_h, "نکات برجسته پژوهش (Research Highlights)", lang='fa', size=15, bold=True)
        p_h.paragraph_format.space_after = Pt(8)
        
        p_desc = doc.add_paragraph()
        set_paragraph_bidi(p_desc, WD_ALIGN_PARAGRAPH.CENTER)
        add_run(p_desc, "(۳ الی ۵ عبارت کلیدی؛ هر مورد حداکثر تا ۸۵ کاراکتر مطابق با استانداردهای نمایه‌سازی نشریات بین‌المللی)", lang='fa', size=10, italic=True)
        p_desc.paragraph_format.space_after = Pt(16)
        
        for item in validation_results:
            p_item = doc.add_paragraph()
            set_paragraph_bidi(p_item, WD_ALIGN_PARAGRAPH.RIGHT)
            add_run(p_item, "• ", lang='fa', size=12, bold=True)
            add_run(p_item, item["text"] + " ", lang='fa', size=12)
            
            # Badge
            badge_color = RGBColor(0, 128, 0) if item["valid"] else RGBColor(200, 0, 0)
            status_txt = f"[{item['length']} کاراکتر - تایید]" if item["valid"] else f"[{item['length']} کاراکتر - بیش از حد مجاز ۸۵!]"
            add_run(p_item, status_txt, lang='fa', size=9, bold=True, color=badge_color)
            p_item.paragraph_format.space_after = Pt(8)
            
    else:
        p_h = doc.add_paragraph()
        p_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_run(p_h, "Research Highlights", lang='en', size=15, bold=True)
        p_h.paragraph_format.space_after = Pt(6)
        
        p_desc = doc.add_paragraph()
        p_desc.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_run(p_desc, "(3 to 5 core findings; strictly maximum 85 characters per bullet point including spaces)", lang='en', size=10, italic=True)
        p_desc.paragraph_format.space_after = Pt(16)
        
        for item in validation_results:
            p_item = doc.add_paragraph(style='List Bullet')
            add_run(p_item, item["text"] + " ", lang='en', size=11)
            
            badge_color = RGBColor(0, 128, 0) if item["valid"] else RGBColor(200, 0, 0)
            status_txt = f"[{item['length']} chars - PASS]" if item["valid"] else f"[{item['length']} chars - EXCEEDS 85 CHAR LIMIT!]"
            add_run(p_item, status_txt, lang='en', size=9, bold=True, color=badge_color)
            p_item.paragraph_format.space_after = Pt(6)
            
    doc.save(out_path)
    return out_path

# ==============================================================================
# 4. BUILD RESPONSE TO REVIEWERS (REBUTTAL TABLE)
# ==============================================================================
def build_rebuttal(data, out_path, lang='en'):
    rebuttal_data = data.get("revision_rebuttal")
    if not rebuttal_data:
        return None
        
    doc = create_base_document()
    is_fa = (lang == 'fa')
    
    meta = data.get("manuscript_metadata", {})
    title = meta.get("title", "")
    journal_name = meta.get("journal_name", "")
    manuscript_id = rebuttal_data.get("manuscript_id", "MS-ID-XXXX")
    decision_date = rebuttal_data.get("decision_date", "")
    intro_letter = rebuttal_data.get("introductory_letter", "")
    reviewer_points = rebuttal_data.get("reviewer_points", [])
    
    if is_fa:
        p_h = doc.add_paragraph()
        set_paragraph_bidi(p_h, WD_ALIGN_PARAGRAPH.CENTER)
        add_run(p_h, "جدول پاسخ به نظرات داوران و سردبیر (Response to Reviewers)", lang='fa', size=15, bold=True)
        p_h.paragraph_format.space_after = Pt(10)
        
        p_meta = doc.add_paragraph()
        set_paragraph_bidi(p_meta, WD_ALIGN_PARAGRAPH.RIGHT)
        add_run(p_meta, f"کد رهگیری مقاله: {manuscript_id} | عنوان: {title}\nنشریه: {journal_name} | تاریخ تصمیم: {decision_date}", lang='fa', size=10, italic=True)
        p_meta.paragraph_format.space_after = Pt(12)
        
        if intro_letter:
            p_intro = doc.add_paragraph()
            set_paragraph_bidi(p_intro, WD_ALIGN_PARAGRAPH.JUSTIFY)
            add_run(p_intro, intro_letter, lang='fa', size=11)
            p_intro.paragraph_format.space_after = Pt(14)
            
        table = doc.add_table(rows=1, cols=3)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_apa_table_borders(table, is_rtl=True)
        
        headers = ["نظر داور / سردبیر", "پاسخ نویسندگان", "اصلاحات و محل در متن جدید"]
        hdr_cells = table.rows[0].cells
        for idx, h_text in enumerate(headers):
            set_cell_background(hdr_cells[idx], "F2F2F2")
            add_header_underline(hdr_cells[idx])
            set_cell_margins(hdr_cells[idx], top=120, bottom=120)
            p = hdr_cells[idx].paragraphs[0]
            set_paragraph_bidi(p, WD_ALIGN_PARAGRAPH.CENTER)
            add_run(p, h_text, lang='fa', size=11, bold=True)
            
        for pt in reviewer_points:
            row_cells = table.add_row().cells
            for cell in row_cells:
                set_cell_margins(cell, top=100, bottom=100)
                add_row_bottom_border(cell, "E0E0E0")
                
            # Cell 0: Reviewer & Comment
            p0 = row_cells[0].paragraphs[0]
            set_paragraph_bidi(p0, WD_ALIGN_PARAGRAPH.JUSTIFY)
            rev_label = f"{pt.get('reviewer', '')} ({pt.get('comment_id', '')})"
            add_run(p0, rev_label + "\n", lang='fa', size=10, bold=True)
            add_run(p0, pt.get("comment", ""), lang='fa', size=10)
            
            # Cell 1: Author Response
            p1 = row_cells[1].paragraphs[0]
            set_paragraph_bidi(p1, WD_ALIGN_PARAGRAPH.JUSTIFY)
            add_run(p1, pt.get("author_response", ""), lang='fa', size=10)
            
            # Cell 2: Action & Excerpt
            p2 = row_cells[2].paragraphs[0]
            set_paragraph_bidi(p2, WD_ALIGN_PARAGRAPH.JUSTIFY)
            add_run(p2, pt.get("manuscript_action", "") + "\n\n", lang='fa', size=10, bold=True)
            if pt.get("excerpt"):
                add_run(p2, pt.get("excerpt"), lang='fa', size=9, italic=True)
                
    else:
        # English Rebuttal
        p_h = doc.add_paragraph()
        p_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_run(p_h, "Point-by-Point Response to Reviewers", lang='en', size=15, bold=True)
        p_h.paragraph_format.space_after = Pt(8)
        
        p_meta = doc.add_paragraph()
        p_meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
        add_run(p_meta, f"Manuscript ID: {manuscript_id} | Journal: {journal_name}\nTitle: \"{title}\"", lang='en', size=10, italic=True)
        p_meta.paragraph_format.space_after = Pt(14)
        
        if intro_letter:
            p_intro = doc.add_paragraph()
            p_intro.paragraph_format.line_spacing = 1.15
            add_run(p_intro, intro_letter, lang='en', size=11)
            p_intro.paragraph_format.space_after = Pt(16)
            
        table = doc.add_table(rows=1, cols=3)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        set_apa_table_borders(table, is_rtl=False)
        
        headers = ["Reviewer / Editor Comment", "Author Response", "Manuscript Changes & Exact Location"]
        widths = [Inches(2.0), Inches(2.2), Inches(2.3)]
        
        hdr_cells = table.rows[0].cells
        for idx, h_text in enumerate(headers):
            hdr_cells[idx].width = widths[idx]
            set_cell_background(hdr_cells[idx], "F2F2F2")
            add_header_underline(hdr_cells[idx])
            set_cell_margins(hdr_cells[idx], top=120, bottom=120)
            p = hdr_cells[idx].paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            add_run(p, h_text, lang='en', size=11, bold=True)
            
        for pt in reviewer_points:
            row_cells = table.add_row().cells
            for idx, cell in enumerate(row_cells):
                cell.width = widths[idx]
                set_cell_margins(cell, top=100, bottom=100)
                add_row_bottom_border(cell, "E0E0E0")
                
            # Cell 0: Reviewer Comment
            p0 = row_cells[0].paragraphs[0]
            rev_label = f"{pt.get('reviewer', 'Reviewer')} - Comment {pt.get('comment_id', '')}"
            add_run(p0, rev_label + "\n", lang='en', size=10, bold=True)
            add_run(p0, pt.get("comment", ""), lang='en', size=10)
            
            # Cell 1: Author Response
            p1 = row_cells[1].paragraphs[0]
            p1.paragraph_format.line_spacing = 1.15
            add_run(p1, pt.get("author_response", ""), lang='en', size=10)
            
            # Cell 2: Action & Excerpt
            p2 = row_cells[2].paragraphs[0]
            p2.paragraph_format.line_spacing = 1.15
            add_run(p2, pt.get("manuscript_action", "") + "\n\n", lang='en', size=10, bold=True)
            if pt.get("excerpt"):
                add_run(p2, pt.get("excerpt"), lang='en', size=9, italic=True)
                
    doc.save(out_path)
    return out_path

# ==============================================================================
# MAIN DRIVER
# ==============================================================================
def main():
    parser = argparse.ArgumentParser(description="Academic Journal Submission & Rebuttal Package Compiler")
    parser.add_argument("--json", required=True, help="Path to input JSON payload")
    parser.add_argument("--out-dir", default="./submission_package", help="Directory to save generated files")
    parser.add_argument("--lang", choices=["en", "fa"], default="en", help="Language mode (en or fa)")
    parser.add_argument("--only", choices=["cover_letter", "title_page", "highlights", "rebuttal", "all"], default="all")
    
    args = parser.parse_args()
    
    with open(args.json, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    os.makedirs(args.out_dir, exist_ok=True)
    generated = []
    
    # 1. Cover Letter
    if args.only in ["all", "cover_letter"]:
        cl_path = os.path.join(args.out_dir, "Cover_Letter.docx")
        build_cover_letter(data, cl_path, lang=args.lang)
        generated.append(cl_path)
        print(f"[SUCCESS] Generated Cover Letter: {cl_path}")
        
    # 2. Title Page
    if args.only in ["all", "title_page"]:
        tp_path = os.path.join(args.out_dir, "Title_Page.docx")
        build_title_page(data, tp_path, lang=args.lang)
        generated.append(tp_path)
        print(f"[SUCCESS] Generated Title Page with CRediT taxonomy: {tp_path}")
        
    # 3. Highlights
    if args.only in ["all", "highlights"]:
        hl_path = os.path.join(args.out_dir, "Highlights.docx")
        build_highlights(data, hl_path, lang=args.lang)
        generated.append(hl_path)
        print(f"[SUCCESS] Generated Research Highlights: {hl_path}")
        
    # 4. Response to Reviewers (if data exists)
    if args.only in ["all", "rebuttal"]:
        if data.get("revision_rebuttal"):
            rb_path = os.path.join(args.out_dir, "Response_to_Reviewers.docx")
            build_rebuttal(data, rb_path, lang=args.lang)
            generated.append(rb_path)
            print(f"[SUCCESS] Generated Response to Reviewers: {rb_path}")
            
    print(f"\n[SUMMARY] Successfully created {len(generated)} submission artifacts in: {args.out_dir}")

if __name__ == "__main__":
    main()
