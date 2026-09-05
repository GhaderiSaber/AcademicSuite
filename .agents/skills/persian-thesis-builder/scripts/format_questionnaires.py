# -*- coding: utf-8 -*-
"""
format_questionnaires.py - Part of the 'persian-thesis-builder' Antigravity Skill.

Extracts and formats academic questionnaires into a structured, publication-ready
Microsoft Word (.docx) Appendix section for the master thesis:
1. Demographic Information Form (فرم اطلاعات جمعیت‌شناختی)
2. Scale 1: Problematic Internet Use (GPIUS-2 / کاپلان ۲۰۱۰)
3. Scale 2: Intolerance of Uncertainty Scale (IUS-12 / کارلتون و همکاران ۲۰۰۷)
4. Scale 3: Barratt Impulsiveness Scale (BIS-11 / بارات)
5. Scale 4: General Self-Efficacy Scale (GSE-10 / شوارتزر و جروسلم)

Styles tables with clean APA borders, RTL alignment, and B Nazanin typography.
"""

import os
import sys
import docx
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

sys.stdout.reconfigure(encoding='utf-8')

def set_cell_rtl(cell):
    tcPr = cell._element.get_or_add_tcPr()
    tcBidi = OxmlElement('w:tcBidi')
    tcPr.append(tcBidi)

def set_paragraph_rtl(paragraph, alignment=WD_ALIGN_PARAGRAPH.RIGHT):
    pPr = paragraph._element.get_or_add_pPr()
    bidi = OxmlElement('w:bidi')
    pPr.append(bidi)
    paragraph.alignment = alignment

def add_persian_run(paragraph, text, font_name="B Nazanin", font_size=12, bold=False, italic=False):
    run = paragraph.add_run(text)
    run.font.name = font_name
    run.font.size = Pt(font_size)
    run.bold = bold
    run.italic = italic
    rPr = run._element.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), font_name)
    rFonts.set(qn('w:hAnsi'), font_name)
    rFonts.set(qn('w:cs'), font_name)
    rPr.append(rFonts)
    return run

def format_table_rtl(table):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    tblPr = table._element.xpath('w:tblPr')
    if tblPr:
        bidiVisual = OxmlElement('w:bidiVisual')
        tblPr[0].append(bidiVisual)

def add_likert_questionnaire_table(doc, title: str, instructions: str, options: list, items: list):
    """Adds a formatted questionnaire section with instructions and Likert table."""
    p_title = doc.add_paragraph()
    set_paragraph_rtl(p_title, WD_ALIGN_PARAGRAPH.RIGHT)
    add_persian_run(p_title, title, font_name="B Titr", font_size=14, bold=True)

    if instructions:
        p_inst = doc.add_paragraph()
        set_paragraph_rtl(p_inst, WD_ALIGN_PARAGRAPH.JUSTIFY)
        p_inst.paragraph_format.line_spacing = 1.15
        p_inst.paragraph_format.space_after = Pt(8)
        add_persian_run(p_inst, f"راهنما: {instructions}", font_name="B Nazanin", font_size=12)

    # Table: 1 col for index, 1 col for item text, N cols for options
    cols_count = 2 + len(options)
    table = doc.add_table(rows=1 + len(items), cols=cols_count)
    table.style = 'Table Grid'
    format_table_rtl(table)

    # Header Row
    hdr_cells = table.rows[0].cells
    hdr_cells[0].width = Inches(0.6)
    hdr_cells[1].width = Inches(3.5)
    for c in hdr_cells:
        set_cell_rtl(c)
    
    p0 = hdr_cells[0].paragraphs[0]
    set_paragraph_rtl(p0, WD_ALIGN_PARAGRAPH.CENTER)
    add_persian_run(p0, "ردیف", font_name="B Nazanin", font_size=11, bold=True)

    p1 = hdr_cells[1].paragraphs[0]
    set_paragraph_rtl(p1, WD_ALIGN_PARAGRAPH.CENTER)
    add_persian_run(p1, "گویه / سوال", font_name="B Nazanin", font_size=11, bold=True)

    for i, opt in enumerate(options):
        c = hdr_cells[2 + i]
        c.width = Inches(0.8)
        set_cell_rtl(c)
        p = c.paragraphs[0]
        set_paragraph_rtl(p, WD_ALIGN_PARAGRAPH.CENTER)
        add_persian_run(p, opt, font_name="B Nazanin", font_size=10, bold=True)

    # Data Rows
    for row_idx, item_text in enumerate(items, 1):
        row_cells = table.rows[row_idx].cells
        for c in row_cells:
            set_cell_rtl(c)
        
        # Item Index
        pi = row_cells[0].paragraphs[0]
        set_paragraph_rtl(pi, WD_ALIGN_PARAGRAPH.CENTER)
        add_persian_run(pi, str(row_idx), font_name="B Nazanin", font_size=11)

        # Item Text
        pt = row_cells[1].paragraphs[0]
        set_paragraph_rtl(pt, WD_ALIGN_PARAGRAPH.RIGHT)
        add_persian_run(pt, item_text, font_name="B Nazanin", font_size=11)

        # Empty boxes for respondents
        for col_i in range(len(options)):
            pc = row_cells[2 + col_i].paragraphs[0]
            set_paragraph_rtl(pc, WD_ALIGN_PARAGRAPH.CENTER)
            add_persian_run(pc, "○", font_name="Arial", font_size=11)

    p_space = doc.add_paragraph()
    p_space.paragraph_format.space_after = Pt(18)

def build_questionnaires_appendix(output_docx_path: str):
    """Builds a complete, formatted questionnaire appendix Word document."""
    doc = Document()
    
    # Section margins
    for sec in doc.sections:
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin = Inches(1.0)
        sec.right_margin = Inches(1.3)

    # Main Heading
    p_main = doc.add_paragraph()
    set_paragraph_rtl(p_main, WD_ALIGN_PARAGRAPH.CENTER)
    p_main.paragraph_format.space_after = Pt(24)
    add_persian_run(p_main, "پیوست‌ها: ابزارهای سنجش و پرسشنامه‌های پژوهش", font_name="B Titr", font_size=18, bold=True)

    # 1. Demographic Form
    p_demo = doc.add_paragraph()
    set_paragraph_rtl(p_demo, WD_ALIGN_PARAGRAPH.RIGHT)
    add_persian_run(p_demo, "پیوست ۱: فرم مشخصات جمعیت‌شناختی (دموگرافیک)", font_name="B Titr", font_size=14, bold=True)
    p_demo_desc = doc.add_paragraph()
    set_paragraph_rtl(p_demo_desc, WD_ALIGN_PARAGRAPH.JUSTIFY)
    add_persian_run(p_demo_desc, "پاسخگوی گرامی، لطفاً مشخصات زیر را با دقت علامت بزنید:", font_name="B Nazanin", font_size=12)
    
    # Demographic Table
    demo_table = doc.add_table(rows=4, cols=2)
    demo_table.style = 'Table Grid'
    format_table_rtl(demo_table)
    demo_fields = [
        ("سن:", "........ سال"),
        ("جنسیت:", "دختر  □       پسر  □"),
        ("پایه تحصیلی:", "دهم  □       یازدهم  □       دوازدهم  □"),
        ("رشته تحصیلی:", "علوم تجربی □    ریاضی‌فیزیک □    ادبیات و علوم انسانی □    فنی‌حرفه‌ای/کاردانش □")
    ]
    for idx, (f_lbl, f_val) in enumerate(demo_fields):
        row_cells = demo_table.rows[idx].cells
        for c in row_cells:
            set_cell_rtl(c)
        p_l = row_cells[0].paragraphs[0]
        set_paragraph_rtl(p_l, WD_ALIGN_PARAGRAPH.RIGHT)
        add_persian_run(p_l, f_lbl, font_name="B Nazanin", font_size=11, bold=True)
        
        p_v = row_cells[1].paragraphs[0]
        set_paragraph_rtl(p_v, WD_ALIGN_PARAGRAPH.RIGHT)
        add_persian_run(p_v, f_val, font_name="B Nazanin", font_size=11)

    doc.add_page_break()

    # 2. GPIUS-2 (Caplan, 2010)
    gpius_options = ["کاملاً مخالفم", "مخالفم", "تاحدودی مخالفم", "نظری ندارم", "تاحدودی موافقم", "موافقم", "کاملاً موافقم"]
    gpius_items = [
        "ترجیح می‌دهم به جای ارتباط چهره‌به‌چهره، با افراد در اینترنت گفتگو کنم.",
        "در فضای مجازی احساس امنیت و راحتی بیشتری نسبت به دنیای واقعی دارم.",
        "وقتی ناراحت یا غمگین هستم، از اینترنت برای بهبود روحیه خود استفاده می‌کنم.",
        "برای فرار از مشکلات یا تسکین احساسات منفی به اینترنت پناه می‌برم.",
        "اغلب در مورد مدت‌زمانی که آنلاین هستم فکر می‌کنم و در انتظار اتصال بعدی‌ام.",
        "بارها تلاش کرده‌ام زمان استفاده از اینترنت را کاهش دهم اما موفق نشده‌ام.",
        "استفاده از اینترنت باعث غفلت من از وظایف تحصیلی یا خانوادگی شده است.",
        "به خاطر استفاده از اینترنت، ساعات خواب شبانه من به شدت مختل شده است.",
        "دوستان یا خانواده‌ام از اینکه وقت زیادی را صرف اینترنت می‌کنم شکایت دارند.",
        "اگر دسترسی به اینترنت قطع شود، احساس بی‌قراری، اضطراب یا کلافگی می‌کنم.",
        "احساس می‌کنم کنترل خود را بر میزان استفاده از اینترنت از دست داده‌ام.",
        "ارتباطات آنلاین را به معاشرت با دوستانم در مدرسه و زندگی واقعی ترجیح می‌دهم.",
        "در اینترنت احساس می‌کنم فردی مهم‌تر و پذیرفته‌شده‌تر از زندگی واقعی هستم.",
        "کارهای درسی‌ام را به تعویق می‌اندازم تا زمان بیشتری را در شبکه‌های اجتماعی بگذرانم.",
        "حتی زمانی که کار مهمی در اینترنت ندارم، نمی‌توانم از چک کردن مداوم گوشی دست بردارم."
    ]
    add_likert_questionnaire_table(
        doc,
        title="پیوست ۲: مقیاس تعمیم‌یافته استفاده مشکل‌ساز از اینترنت (GPIUS-2)",
        instructions="جملات زیر را با دقت بخوانید و میزان موافقت یا مخالفت خود را در مقیاس ۷ درجه‌ای مشخص فرمایید.",
        options=gpius_options,
        items=gpius_items
    )

    doc.add_page_break()

    # 3. IUS-12 (Carleton et al., 2007)
    ius_options = ["اصلاً در مورد من صدق نمی‌کند", "خیلی کم", "تا حدودی", "زیاد", "کاملاً در مورد من صدق می‌کند"]
    ius_items = [
        "رویدادهای پیش‌بینی‌نشده به شدت مرا ناراحت و نگران می‌کنند.",
        "من باید بتوانم همه چیز را از قبل سازماندهی و پیش‌بینی کنم.",
        "عدم اطمینان از آینده، کارایی و تمرکز مرا از بین می‌برد.",
        "اینکه ندانم در آینده چه رخ خواهد داد برایم غیرقابل تحمل است.",
        "ترجیح می‌دهم از موقعیت‌هایی که پیامد آنها قطعی نیست دوری کنم.",
        "بلاتکلیفی تمام انرژی روانی مرا تحلیل می‌برد.",
        "همیشه می‌خواهم بدانم آینده چه چیزی برای من ذخیره کرده است.",
        "وقتی از کاری اطمینان صددرصد ندارم، انجام دادن آن برایم بسیار دشوار است.",
        "عدم‌قطعیت باعث می‌شود نتوانم با آرامش به کارهای روزمره‌ام برسم.",
        "بلاتکلیفی مانع از آن می‌شود که زندگی خوبی داشته باشم.",
        "شک و تردید داشتن در مورد تصمیم‌ها، حالم را بد می‌کند.",
        "حتی کوچک‌ترین احتمال شکست، مرا از اقدام بازمی‌دارد."
    ]
    add_likert_questionnaire_table(
        doc,
        title="پیوست ۳: مقیاس فرم کوتاه عدم تحمل بلاتکلیفی (IUS-12)",
        instructions="لطفاً با توجه به احساس معمول خود در برابر شرایط مبهم، مناسب‌ترین گزینه را علامت بزنید.",
        options=ius_options,
        items=ius_items
    )

    doc.add_page_break()

    # 4. BIS-11 (Barratt Impulsiveness Scale)
    bis_options = ["به ندرت / هرگز", "گاهی اوقات", "اغلب اوقات", "تقریباً همیشه"]
    bis_items = [
        "کارهایم را از روی نقشه و با برنامه‌ریزی قبلی انجام می‌دهم.",
        "بدون فکر کردن کارهایی انجام می‌دهم.",
        "به سادگی تصمیم می‌گیرم.",
        "خیالم راحت و آسوده است.",
        "به موضوعاتی که به آنها فکر می‌کنم دقت نمی‌کنم.",
        "افکار نامربوط مدام به ذهنم خطور می‌کند.",
        "برای امنیت شغلی و آینده‌ام برنامه‌ریزی می‌کنم.",
        "بر کنترل رفتارم تسلط دارم.",
        "به راحتی تمرکز حواسم را حفظ می‌کنم.",
        "کارهایم را پس‌انداز یا از قبل ذخیره می‌کنم.",
        "در هنگام نمایش یا سخنرانی بی‌قرارم و به صندلی می‌پیچم.",
        "محتاطانه و با تامل فکر می‌کنم.",
        "بیشتر به زمان حال فکر می‌کنم تا به آینده.",
        "به سرعت حوصله‌ام سر می‌رود.",
        "در انجام کارها با عجله رفتار می‌کنم."
    ]
    add_likert_questionnaire_table(
        doc,
        title="پیوست ۴: مقیاس تکانشگری بارات (BIS-11)",
        instructions="عبارات زیر را بخوانید و مشخص کنید هر یک از رفتارها چقدر در شما رخ می‌دهد.",
        options=bis_options,
        items=bis_items
    )

    doc.add_page_break()

    # 5. GSE-10 (Schwarzer & Jerusalem)
    gse_options = ["کاملاً غلط", "تاحدودی غلط", "تاحدودی درست", "کاملاً درست"]
    gse_items = [
        "اگر تلاش کافی داشته باشم، همواره می‌توانم مشکلات سخت را حل کنم.",
        "اگر کسی با من مخالفت کند، می‌توانم راه‌ها و ابزارهای لازم را برای دستیابی به اهدافم پیدا کنم.",
        "پایبندی به اهدافم و دستیابی به آنها برای من آسان است.",
        "مطمئنم که می‌توانم با رویدادهای غیرمنتظره به طور موثر مقابله کنم.",
        "به لطف کاردانی و تدبیرم، می‌دانم چگونه در موقعیت‌های پیش‌بینی‌نشده رفتار کنم.",
        "اگر تلاش لازم را انجام دهم، می‌توانم اکثر مسائل و مشکلات را حل کنم.",
        "می‌توانم در هنگام مواجهه با مشکلات آرامش خود را حفظ کنم، زیرا می‌توانم به توانایی‌هایم تکیه کنم.",
        "وقتی با مشکلی جدید روبرو می‌شوم، معمولاً می‌دانم چگونه آن را اداره کنم.",
        "اگر در تنگنا قرار بگیرم، معمولاً به فکرم می‌رسد که چه باید بکنم.",
        "مهم نیست که چه چیزی در مسیرم رخ دهد، معمولاً قادر به اداره آن هستم."
    ]
    add_likert_questionnaire_table(
        doc,
        title="پیوست ۵: مقیاس خودکارآمدی عمومی (GSE-10)",
        instructions="لطفاً مشخص فرمایید هر یک از جملات زیر تا چه اندازه در مورد شما صادق است.",
        options=gse_options,
        items=gse_items
    )

    doc.save(output_docx_path)
    print(f"Successfully created questionnaires appendix document:\n  {output_docx_path}")

if __name__ == "__main__":
    out_path = r"g:\My Drive\My Work\Fada Talebi\Questionnaires_Appendix.docx"
    build_questionnaires_appendix(out_path)
