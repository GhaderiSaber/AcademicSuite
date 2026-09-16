import os
import json
import docx
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import nsdecls, qn

def set_cell_borders(cell, top=None, bottom=None, left=None, right=None):
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    
    borders = {'top': top, 'bottom': bottom, 'left': left, 'right': right}
    for edge, border in borders.items():
        if border is not None:
            element = OxmlElement(f'w:{edge}')
            element.set(qn('w:val'), border.get('val', 'single'))
            element.set(qn('w:sz'), str(border.get('sz', 4)))
            element.set(qn('w:space'), '0')
            element.set(qn('w:color'), border.get('color', 'auto'))
            tcBorders.append(element)
        else:
            element = OxmlElement(f'w:{edge}')
            element.set(qn('w:val'), 'none')
            tcBorders.append(element)
    tcPr.append(tcBorders)

def set_cell_rtl(cell):
    tcPr = cell._tc.get_or_add_tcPr()
    # Cell direction RTL
    tcMar = OxmlElement('w:tcMar')
    tcPr.append(tcMar)

def apply_p_rtl(p, justify=True):
    pPr = p._p.get_or_add_pPr()
    bidi = OxmlElement('w:bidi')
    bidi.set(qn('w:val'), '1')
    pPr.append(bidi)
    if justify:
        jc = OxmlElement('w:jc')
        jc.set(qn('w:val'), 'both')
        pPr.append(jc)

def apply_run_font(run, font_name="B Nazanin", size_pt=13, bold=False, italic=False, color_rgb=None):
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    if color_rgb:
        run.font.color.rgb = color_rgb
    
    rPr = run._r.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), font_name)
    rFonts.set(qn('w:hAnsi'), font_name)
    rFonts.set(qn('w:cs'), font_name)
    rFonts.set(qn('w:hint'), 'cs')
    rPr.append(rFonts)
    
    rtl = OxmlElement('w:rtl')
    rtl.set(qn('w:val'), '1')
    rPr.append(rtl)

def apply_run_latin(run, size_pt=11, bold=False, italic=True):
    run.font.name = "Times New Roman"
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    rPr = run._r.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), "Times New Roman")
    rFonts.set(qn('w:hAnsi'), "Times New Roman")
    rFonts.set(qn('w:cs'), "Times New Roman")
    rPr.append(rFonts)

def format_apa_table(table, col_widths=None):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    # Enforce BiDi table
    tblPr = table._tbl.tblPr
    bidiVisual = OxmlElement('w:bidiVisual')
    tblPr.append(bidiVisual)
    
    # 3 borders: Top row top border 0.75pt, header bottom border 0.5pt, last row bottom border 0.75pt
    num_rows = len(table.rows)
    for r_idx, row in enumerate(table.rows):
        for c_idx, cell in enumerate(row.cells):
            cell.vertical_alignment = WD_ALIGN_VERTICAL.CENTER
            top_b = None
            bottom_b = None
            if r_idx == 0:
                top_b = {'val': 'single', 'sz': 6, 'color': '000000'} # 0.75 pt
                bottom_b = {'val': 'single', 'sz': 4, 'color': '000000'} # 0.5 pt
            elif r_idx == num_rows - 1:
                bottom_b = {'val': 'single', 'sz': 6, 'color': '000000'} # 0.75 pt
            set_cell_borders(cell, top=top_b, bottom=bottom_b, left=None, right=None)
            
            # Set col width if provided
            if col_widths and c_idx < len(col_widths):
                cell.width = Inches(col_widths[c_idx])

def to_fa_num(val):
    if val is None:
        return ""
    trans = str.maketrans('0123456789', '۰۱۲۳۴۵۶۷۸۹')
    return str(val).translate(trans)

def main():
    stats_path = "02_processed_data/stats_results.json"
    scoring_path = "02_processed_data/scoring_log.json"
    out_path = "03_deliverables/Chapter_4_Results.docx"
    os.makedirs("03_deliverables", exist_ok=True)
    
    with open(stats_path, "r", encoding="utf-8") as f:
        stats_data = json.load(f)
    with open(scoring_path, "r", encoding="utf-8") as f:
        scoring_data = json.load(f)
        
    doc = Document()
    
    # Page setup (A4, 1 inch margins)
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(1.0)
    section.bottom_margin = Inches(1.0)
    section.left_margin = Inches(1.0)
    section.right_margin = Inches(1.0)
    
    # Document level BiDi
    sectPr = section._sectPr
    bidi_sect = OxmlElement('w:bidi')
    sectPr.append(bidi_sect)
    
    # 1. Main Title
    p_title = doc.add_paragraph()
    apply_p_rtl(p_title, justify=False)
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("فصل چهارم: یافته‌های پژوهش")
    apply_run_font(r_title, font_name="B Titr", size_pt=18, bold=True)
    
    p_sub = doc.add_paragraph()
    apply_p_rtl(p_sub, justify=False)
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_sub = p_sub.add_run("بررسی شیوع رفتارهای خودآسیبی و گرایش به خودکشی و نقش افسردگی، اضطراب و بدشکل‌انگاری بدن در دانش‌آموزان مقطع دبیرستان شهر قم")
    apply_run_font(r_sub, font_name="B Nazanin", size_pt=13, bold=True)
    
    # 2. Introduction Section
    p_h1 = doc.add_paragraph()
    apply_p_rtl(p_h1, justify=False)
    r_h1 = p_h1.add_run("۱-۴. مقدمه و نقشه راه فصل چهارم")
    apply_run_font(r_h1, font_name="B Titr", size_pt=15, bold=True)
    
    p_intro = doc.add_paragraph()
    apply_p_rtl(p_intro, justify=True)
    r_intro = p_intro.add_run(
        "فصل حاضر به تجزیه و تحلیل آماری داده‌های گردآوری‌شده از نمونه پژوهش اختصاص دارد. "
        "هدف اصلی پژوهش حاضر، بررسی شیوع رفتارهای خودآسیبی و گرایش به خودکشی و تعیین نقش متغیرهای روان‌شناختی شامل "
        "افسردگی، اضطراب و نگرانی از بدشکل‌انگاری بدن بر پیش‌بینی این رفتارها در بین ۵۱۲ نفر از دانش‌آموزان دختر و پسر مقطع دبیرستان شهر قم بوده است. "
        "تحلیل داده‌ها در دو بخش آمار توصیفی و آمار استنباطی سازمان‌دهی شده است؛ در گام اول ویژگی‌های جمعیت‌شناختی آزمودنی‌ها، شاخص‌های مرکزی و پراکندگی و وضعیت مفروضه‌های آزمون‌های پارامتریک ارائه می‌گردد و در گام دوم، میزان شیوع اپیدمیولوژیک رفتارهای خودآسیبی و خطر خودکشی گزارش شده و آزمون فرضیه‌های پژوهش با استفاده از الگوهای رگرسیون چندگانه خطی و رگرسیون لجستیک دوتایی به بوته آزمون گذاشته می‌شوند."
    )
    apply_run_font(r_intro, font_name="B Nazanin", size_pt=13)
    
    # 3. Demographics Section
    p_h2 = doc.add_paragraph()
    apply_p_rtl(p_h2, justify=False)
    r_h2 = p_h2.add_run("۲-۴. توصیف ویژگی‌های جمعیت‌شناختی نمونه پژوهش")
    apply_run_font(r_h2, font_name="B Titr", size_pt=15, bold=True)
    
    demo = stats_data["demographics"]
    p_demo_desc = doc.add_paragraph()
    apply_p_rtl(p_demo_desc, justify=True)
    r_demo_desc = p_demo_desc.add_run(
        f"جامعه آماری پژوهش حاضر را کلیه دانش‌آموزان دبیرستانی شهر قم تشکیل دادند که از میان آن‌ها نمونه‌ای به حجم ۵۱۲ نفر با استفاده از روش نمونه‌گیری خوشه‌ای چندمرحله‌ای مورد بررسی قرار گرفتند. "
        f"از مجموع ۵۱۲ آزمودنی، ۳۴۳ نفر ({to_fa_num(demo['gender_pct']['زن'])} درصد) را دختران و ۱۶۶ نفر ({to_fa_num(demo['gender_pct']['مرد'])} درصد) را پسران تشکیل دادند. "
        f"از نظر پایه تحصیلی، ۱۷۶ نفر ({to_fa_num(demo['grade_pct']['دهم'])} درصد) در پایه دهم، ۱۸۷ نفر ({to_fa_num(demo['grade_pct']['یازدهم'])} درصد) در پایه یازدهم و ۱۴۵ نفر ({to_fa_num(demo['grade_pct']['دوازدهم'])} درصد) در پایه دوازدهم مشغول به تحصیل بودند. "
        f"میانگین سنی کل آزمودنی‌ها برابر با {to_fa_num(demo['age_m'])} سال با انحراف استاندارد {to_fa_num(demo['age_sd'])} بود. از لحاظ وضعیت اقتصادی خانواده، بیش از سه چهارم آزمودنی‌ها ({to_fa_num(demo['family_ses_pct']['متوسط'])} درصد) وضعیت مالی خانواده خود را در حد متوسط ارزیابی کرده‌اند. توزیع کامل فراوانی و درصدهای ویژگی‌های جمعیت‌شناختی در جدول (۴-۱) خلاصه شده است."
    )
    apply_run_font(r_demo_desc, font_name="B Nazanin", size_pt=13)
    
    # Table 4-1: Demographics
    p_cap1 = doc.add_paragraph()
    apply_p_rtl(p_cap1, justify=False)
    r_cap1 = p_cap1.add_run("جدول ۴-۱. توزیع فراوانی و درصدی ویژگی‌های جمعیت‌شناختی آزمودنی‌ها (N = ۵۱۲)")
    apply_run_font(r_cap1, font_name="B Titr", size_pt=11, bold=True)
    
    tbl1 = doc.add_table(rows=1, cols=4)
    format_apa_table(tbl1, col_widths=[1.5, 1.8, 1.3, 1.3])
    hdr_cells1 = tbl1.rows[0].cells
    hdr_titles1 = ["متغیر جمعیت‌شناختی", "طبقات متغیر", "فراوانی (n)", "درصد (%)"]
    for i, t in enumerate(hdr_titles1):
        p = hdr_cells1[i].paragraphs[0]
        apply_p_rtl(p, justify=False)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(t)
        apply_run_font(r, font_name="B Titr", size_pt=10, bold=True)
        
    demo_rows = [
        ("جنسیت", "دختر (زن)", to_fa_num(demo['gender']['زن']), to_fa_num(demo['gender_pct']['زن'])),
        ("", "پسر (مرد)", to_fa_num(demo['gender']['مرد']), to_fa_num(demo['gender_pct']['مرد'])),
        ("پایه تحصیلی", "دهم", to_fa_num(demo['grade']['دهم']), to_fa_num(demo['grade_pct']['دهم'])),
        ("", "یازدهم", to_fa_num(demo['grade']['یازدهم']), to_fa_num(demo['grade_pct']['یازدهم'])),
        ("", "دوازدهم", to_fa_num(demo['grade']['دوازدهم']), to_fa_num(demo['grade_pct']['دوازدهم'])),
        ("نوع مدرسه", "دولتی", to_fa_num(demo['school_type']['دولتی']), to_fa_num(demo['school_type_pct']['دولتی'])),
        ("", "فرزانگان (استعدادهای درخشان)", to_fa_num(demo['school_type']['فرزانگان']), to_fa_num(demo['school_type_pct']['فرزانگان'])),
        ("", "نمونه دولتی", to_fa_num(demo['school_type']['نمونه دولتی']), to_fa_num(demo['school_type_pct']['نمونه دولتی'])),
        ("", "شاهد", to_fa_num(demo['school_type']['شاهد']), to_fa_num(demo['school_type_pct']['شاهد'])),
        ("", "سایر مدارس", to_fa_num(demo['school_type']['سایر']), to_fa_num(demo['school_type_pct']['سایر'])),
        ("وضعیت مالی خانواده", "پایین", to_fa_num(demo['family_ses']['پایین']), to_fa_num(demo['family_ses_pct']['پایین'])),
        ("", "متوسط", to_fa_num(demo['family_ses']['متوسط']), to_fa_num(demo['family_ses_pct']['متوسط'])),
        ("", "بالا", to_fa_num(demo['family_ses']['بالا']), to_fa_num(demo['family_ses_pct']['بالا']))
    ]
    for row_data in demo_rows:
        row = tbl1.add_row()
        for idx, val in enumerate(row_data):
            cell = row.cells[idx]
            p = cell.paragraphs[0]
            apply_p_rtl(p, justify=False)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if idx >= 2 else WD_ALIGN_PARAGRAPH.RIGHT
            r = p.add_run(val)
            apply_run_font(r, font_name="B Nazanin", size_pt=11)
            
    format_apa_table(tbl1, col_widths=[1.5, 1.8, 1.3, 1.3])
    doc.add_paragraph() # Spacing
    
    # 4. Descriptives & Normality Section
    p_h3 = doc.add_paragraph()
    apply_p_rtl(p_h3, justify=False)
    r_h3 = p_h3.add_run("۳-۴. شاخص‌های توصیفی متغیرهای پژوهش و بررسی مفروضه‌های آماری")
    apply_run_font(r_h3, font_name="B Titr", size_pt=15, bold=True)
    
    p_desc_narr = doc.add_paragraph()
    apply_p_rtl(p_desc_narr, justify=True)
    desc = stats_data["descriptive_statistics"]
    r_desc_narr = p_desc_narr.add_run(
        "به منظور آگاهی از چگونگی توزیع داده‌ها و برآورد مقدماتی ویژگی‌های آماری متغیرها، شاخص‌های مرکزی (میانگین، میانه) و پراکندگی (انحراف استاندارد، کمترین و بیشترین نمره) به همراه شاخص‌های شکل توزیع (چولگی و کشیدگی) برای متغیرهای افسردگی (CDI)، اضطراب (SCAS)، نگرانی از بدشکل‌انگاری بدن (BICI)، رفتارهای خودآسیبی (SHI) و گرایش به خودکشی (SBQ-R) محاسبه گردید. "
        f"میانگین نمره افسردگی در بین دانش‌آموزان برابر با {to_fa_num(desc['Depression_Total']['mean'])} (انحراف استاندارد {to_fa_num(desc['Depression_Total']['sd'])}؛ دامنه ۰ الی ۴۷)، "
        f"میانگین اضطراب برابر با {to_fa_num(desc['Anxiety_Total']['mean'])} (انحراف استاندارد {to_fa_num(desc['Anxiety_Total']['sd'])}؛ دامنه ۰ الی ۹۶)، "
        f"میانگین نگرانی از بدشکلی بدن برابر با {to_fa_num(desc['BodyDysmorphia_Total']['mean'])} (انحراف استاندارد {to_fa_num(desc['BodyDysmorphia_Total']['sd'])}؛ دامنه ۰ الی ۲۱)، "
        f"میانگین رفتارهای خودآسیبی برابر با {to_fa_num(desc['SHI_Total']['mean'])} (انحراف استاندارد {to_fa_num(desc['SHI_Total']['sd'])}؛ دامنه ۰ الی ۱۷) و "
        f"میانگین گرایش به خودکشی برابر با {to_fa_num(desc['Suicide_Total']['mean'])} (انحراف استاندارد {to_fa_num(desc['Suicide_Total']['sd'])}؛ دامنه ۳ الی ۱۶) به دست آمد. "
        "از آنجا که مقدار شاخص‌های چولگی و کشیدگی تمامی متغیرها در بازه مجاز [۲- الی ۲+] قرار دارند (کلاین، ۲۰۱۶)، فرض نرمال بودن تک‌متغیری داده‌ها جهت اجرای تحلیل‌های رگرسیون چندگانه پارامتریک احراز گردیده است. خلاصه شاخص‌های توصیفی در جدول (۴-۲) منعکس شده است."
    )
    apply_run_font(r_desc_narr, font_name="B Nazanin", size_pt=13)
    
    # Table 4-2: Descriptives
    p_cap2 = doc.add_paragraph()
    apply_p_rtl(p_cap2, justify=False)
    r_cap2 = p_cap2.add_run("جدول ۴-۲. شاخص‌های توصیفی و بررسی توزیع متغیرهای پژوهش (N = ۵۱۲)")
    apply_run_font(r_cap2, font_name="B Titr", size_pt=11, bold=True)
    
    tbl2 = doc.add_table(rows=1, cols=8)
    format_apa_table(tbl2, col_widths=[1.8, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7])
    hdr_titles2 = ["متغیر", "M", "SD", "Mdn", "Min", "Max", "Skew", "Kurt"]
    for i, t in enumerate(hdr_titles2):
        p = tbl2.rows[0].cells[i].paragraphs[0]
        apply_p_rtl(p, justify=False)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(t)
        apply_run_font(r, font_name="B Titr", size_pt=10, bold=True)
        
    for var_key, v_data in desc.items():
        row = tbl2.add_row()
        vals = [
            v_data["name_fa"],
            to_fa_num(v_data["mean"]),
            to_fa_num(v_data["sd"]),
            to_fa_num(v_data["median"]),
            to_fa_num(v_data["min"]),
            to_fa_num(v_data["max"]),
            to_fa_num(v_data["skewness"]),
            to_fa_num(v_data["kurtosis"])
        ]
        for idx, val in enumerate(vals):
            p = row.cells[idx].paragraphs[0]
            apply_p_rtl(p, justify=False)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if idx > 0 else WD_ALIGN_PARAGRAPH.RIGHT
            r = p.add_run(val)
            apply_run_font(r, font_name="B Nazanin", size_pt=11)
            
    format_apa_table(tbl2, col_widths=[1.8, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7])
    doc.add_paragraph() # Spacing
    
    # 5. Epidemiological Prevalence Section
    p_h4 = doc.add_paragraph()
    apply_p_rtl(p_h4, justify=False)
    r_h4 = p_h4.add_run("۴-۴. بررسی شیوع اپیدمیولوژیک رفتارهای خودآسیبی و خطر خودکشی")
    apply_run_font(r_h4, font_name="B Titr", size_pt=15, bold=True)
    
    prev = stats_data["epidemiological_prevalence"]
    p_prev_narr = doc.add_paragraph()
    apply_p_rtl(p_prev_narr, justify=True)
    r_prev_narr = p_prev_narr.add_run(
        f"یکی از اهداف اختصاصی این پژوهش، برآورد میزان شیوع رفتارهای خودآسیبی و خطر خودکشی در بین نوجوانان دبیرستانی شهر قم بوده است. "
        f"یافته‌های اپیدمیولوژیک نشان داد که ۴۰۹ نفر از آزمودنی‌ها ({to_fa_num(prev['self_harm_any_pct'])} درصد) حداقل یک نوع رفتار خودآسیب‌رسان مستقیم یا غیرمستقیم را در طول عمر خود گزارش کرده‌اند. "
        f"علاوه بر این، بر اساس نقطه برش بالینی پرسشنامه سانسون (نمره ۵ و بالاتر)، تعداد ۱۷۹ نفر ({to_fa_num(prev['self_harm_clinical_pct'])} درصد) در منطقه خطر بالای رفتارهای خودآسیبی شدید و صفات شخصیت مرزی قرار دارند. "
        f"میانگین آسیب به خود غیرمستقیم (سوء‌مصرف دارو، روابط پرخطر عاطفی، گرسنگی دادن خود) با مقدار {to_fa_num(prev['self_harm_indirect_mean'])} به مراتب شایع‌تر از رفتارهای آسیب مستقیم فیزیکی (بریدن، سوزاندن، زدن) با میانگین {to_fa_num(prev['self_harm_direct_mean'])} گزارش گردید.\n"
        f"در خصوص گرایش به خودکشی (پرسشنامه SBQ-R)، نتایج حاکی از آن است که ۲۰۸ نفر ({to_fa_num(prev['suicide_ideation_lifetime_pct'])} درصد) سابقه افکار خودکشی در طول زندگی، "
        f"۶۲ نفر ({to_fa_num(prev['suicide_plan_lifetime_pct'])} درصد) سابقه برنامه‌ریزی برای خودکشی و ۳۰ نفر ({to_fa_num(prev['suicide_attempt_lifetime_pct'])} درصد) سابقه حداقل یک‌بار اقدام واقعی به خودکشی را در دوره نوجوانی گزارش کرده‌اند. "
        f"همچنین بر اساس نقطه برش استاندارد عثمان و همکاران (نمره کل ۷ و بالاتر)، ۱۵۳ نفر ({to_fa_num(prev['suicide_risk_pct'])} درصد) از دانش‌آموزان در معرض خطر بالینی بالای رفتارهای خودکشی قرار دارند. جدول (۴-۳) شیوع تفکیکی این شاخص‌ها را نشان می‌دهد."
    )
    apply_run_font(r_prev_narr, font_name="B Nazanin", size_pt=13)
    
    # Table 4-3: Prevalence Table
    p_cap3 = doc.add_paragraph()
    apply_p_rtl(p_cap3, justify=False)
    r_cap3 = p_cap3.add_run("جدول ۴-۳. برآورد شیوع اپیدمیولوژیک رفتارهای خودآسیبی و خطر خودکشی در دانش‌آموزان دبیرستانی (N = ۵۱۲)")
    apply_run_font(r_cap3, font_name="B Titr", size_pt=11, bold=True)
    
    tbl3 = doc.add_table(rows=1, cols=4)
    format_apa_table(tbl3, col_widths=[2.8, 1.2, 1.2, 1.5])
    hdr_titles3 = ["شاخص بالینی و اپیدمیولوژیک", "فراوانی (n)", "درصد شیوع (%)", "معیار تشخیصی / برش"]
    for i, t in enumerate(hdr_titles3):
        p = tbl3.rows[0].cells[i].paragraphs[0]
        apply_p_rtl(p, justify=False)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(t)
        apply_run_font(r, font_name="B Titr", size_pt=10, bold=True)
        
    prev_rows = [
        ("شیوع کل رفتارهای خودآسیبی (حداقل یک رفتار)", to_fa_num(prev['self_harm_any_count']), to_fa_num(prev['self_harm_any_pct']), "SHI ≥ 1"),
        ("خطر بالینی بالای خودآسیبی (آسیب شدید/مرزی)", to_fa_num(prev['self_harm_clinical_count']), to_fa_num(prev['self_harm_clinical_pct']), "نقطه برش SHI ≥ 5"),
        ("افکار خودکشی در طول زندگی (Suicidal Ideation)", to_fa_num(prev['suicide_ideation_lifetime_count']), to_fa_num(prev['suicide_ideation_lifetime_pct']), "گویه ۱ SBQ-R (گزینه ۲ به بالا)"),
        ("برنامه‌ریزی برای خودکشی (Suicidal Planning)", to_fa_num(prev['suicide_plan_lifetime_count']), to_fa_num(prev['suicide_plan_lifetime_pct']), "گویه ۱ SBQ-R (گزینه ۳)"),
        ("سابقه اقدام به خودکشی (Suicide Attempt)", to_fa_num(prev['suicide_attempt_lifetime_count']), to_fa_num(prev['suicide_attempt_lifetime_pct']), "گویه ۱ SBQ-R (گزینه ۴)"),
        ("خطر بالینی بالای رفتارهای خودکشی", to_fa_num(prev['suicide_risk_count']), to_fa_num(prev['suicide_risk_pct']), "نقطه برش SBQ-R ≥ 7")
    ]
    for row_data in prev_rows:
        row = tbl3.add_row()
        for idx, val in enumerate(row_data):
            p = row.cells[idx].paragraphs[0]
            apply_p_rtl(p, justify=False)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if idx in [1, 2, 3] else WD_ALIGN_PARAGRAPH.RIGHT
            r = p.add_run(val)
            apply_run_font(r, font_name="B Nazanin", size_pt=11)
            
    format_apa_table(tbl3, col_widths=[2.8, 1.2, 1.2, 1.5])
    doc.add_paragraph() # Spacing
    
    # 6. Bivariate Correlation Matrix
    p_h5 = doc.add_paragraph()
    apply_p_rtl(p_h5, justify=False)
    r_h5 = p_h5.add_run("۵-۴. ماتریس همبستگی پیرسون بین متغیرهای پژوهش")
    apply_run_font(r_h5, font_name="B Titr", size_pt=15, bold=True)
    
    p_corr_narr = doc.add_paragraph()
    apply_p_rtl(p_corr_narr, justify=True)
    r_corr = stats_data["correlation_matrix"]["r_values"]
    r_corr_narr = p_corr_narr.add_run(
        "پیش از برازش مدل‌های رگرسیونی، جهت بررسی جهت و شدت همبستگی‌های دومتغیره، ماتریس همبستگی پیرسون بین متغیرهای پیش‌بین (افسردگی، اضطراب و بدشکل‌انگاری بدن) و متغیرهای ملاک (رفتارهای خودآسیبی و خودکشی) محاسبه شد. "
        f"نتایج نشان داد که بین افسردگی با رفتارهای خودآسیبی (r = {to_fa_num(r_corr['Depression_Total']['SHI_Total'])}، p < ۰.۰۰۱) و تمایل به خودکشی (r = {to_fa_num(r_corr['Depression_Total']['Suicide_Total'])}، p < ۰.۰۰۱) رابطه مثبت و معنادار آماری در سطح خطای ۰.۰۱ برقرار است. "
        f"همچنین اضطراب با رفتارهای خودآسیبی (r = {to_fa_num(r_corr['Anxiety_Total']['SHI_Total'])}، p < ۰.۰۰۱) و تمایل به خودکشی (r = {to_fa_num(r_corr['Anxiety_Total']['Suicide_Total'])}، p < ۰.۰۰۱) همبستگی مثبت و معناداری دارد. "
        f"نگرانی از بدشکل‌انگاری بدن نیز با رفتارهای خودآسیبی (r = {to_fa_num(r_corr['BodyDysmorphia_Total']['SHI_Total'])}، p < ۰.۰۰۱) و رفتارهای خودکشی (r = {to_fa_num(r_corr['BodyDysmorphia_Total']['Suicide_Total'])}، p < ۰.۰۰۱) رابطه مثبت و نیرومندی نشان داد. "
        f"از سوی دیگر، همبستگی بالایی بین خودآسیبی و رفتارهای خودکشی مشاهده شد (r = {to_fa_num(r_corr['SHI_Total']['Suicide_Total'])}، p < ۰.۰۰۱) که هم‌پوشانی بالینی این دو ساختار پرخطر را تأیید می‌کند. از آنجا که ضرایب همبستگی بین متغیرهای پیش‌بین کمتر از ۰.۸۵ بوده است، روایی تفکیکی احراز و خطر همخطی چندگانه رد می‌گردد. ماتریس همبستگی در جدول (۴-۴) ارائه شده است."
    )
    apply_run_font(r_corr_narr, font_name="B Nazanin", size_pt=13)
    
    # Table 4-4: Correlation Matrix
    p_cap4 = doc.add_paragraph()
    apply_p_rtl(p_cap4, justify=False)
    r_cap4 = p_cap4.add_run("جدول ۴-۴. ماتریس همبستگی پیرسون بین متغیرهای پژوهش (N = ۵۱۲)")
    apply_run_font(r_cap4, font_name="B Titr", size_pt=11, bold=True)
    
    tbl4 = doc.add_table(rows=1, cols=6)
    format_apa_table(tbl4, col_widths=[2.5, 0.8, 0.8, 0.8, 0.8, 0.8])
    hdr_titles4 = ["متغیر", "۱", "۲", "۳", "۴", "۵"]
    for i, t in enumerate(hdr_titles4):
        p = tbl4.rows[0].cells[i].paragraphs[0]
        apply_p_rtl(p, justify=False)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(t)
        apply_run_font(r, font_name="B Titr", size_pt=10, bold=True)
        
    c_vars = stats_data["correlation_matrix"]["variables"]
    c_labels = stats_data["correlation_matrix"]["labels_fa"]
    for i in range(len(c_vars)):
        row = tbl4.add_row()
        p = row.cells[0].paragraphs[0]
        apply_p_rtl(p, justify=False)
        r = p.add_run(f"{to_fa_num(i+1)}. {c_labels[i]}")
        apply_run_font(r, font_name="B Nazanin", size_pt=11)
        
        for j in range(len(c_vars)):
            p_cell = row.cells[j+1].paragraphs[0]
            apply_p_rtl(p_cell, justify=False)
            p_cell.alignment = WD_ALIGN_PARAGRAPH.CENTER
            if i == j:
                r_c = p_cell.add_run("۱")
            elif j < i:
                r_val = r_corr[c_vars[i]][c_vars[j]]
                r_c = p_cell.add_run(f"{to_fa_num(r_val)}**")
            else:
                r_c = p_cell.add_run("-")
            apply_run_font(r_c, font_name="B Nazanin", size_pt=11)
            
    format_apa_table(tbl4, col_widths=[2.5, 0.8, 0.8, 0.8, 0.8, 0.8])
    
    p_note4 = doc.add_paragraph()
    apply_p_rtl(p_note4, justify=False)
    r_n4 = p_note4.add_run("یادداشت. ** معناداری در سطح ۰.۰۱ (۰.۰۱ > p).")
    apply_run_font(r_n4, font_name="B Nazanin", size_pt=10, italic=True)
    doc.add_paragraph() # Spacing
    
    # 7. Multiple Regression Model 1: Self-Harm
    p_h6 = doc.add_paragraph()
    apply_p_rtl(p_h6, justify=False)
    r_h6 = p_h6.add_run("۶-۴. آزمون فرضیه‌های پیش‌بینی رفتارهای خودآسیبی (رگرسیون چندگانه خطی)")
    apply_run_font(r_h6, font_name="B Titr", size_pt=15, bold=True)
    
    m1 = stats_data["regression_self_harm"]["model_summary"]
    c1 = stats_data["regression_self_harm"]["coefficients"]
    
    p_m1_narr = doc.add_paragraph()
    apply_p_rtl(p_m1_narr, justify=True)
    r_m1_narr = p_m1_narr.add_run(
        "جهت سنجش توان پیش‌بینی متغیرهای افسردگی، اضطراب و بدشکل‌انگاری بدن در تبیین واریانس رفتارهای خودآسیبی، تحلیل رگرسیون چندگانه به روش همزمان (Enter) اجرا گردید. "
        "پیش از تفسیر ضرایب، مفروضه‌های استقلال خطاها و همخطی آزموده شد؛ آماره دوربین-واتسون برابر با "
        f"{to_fa_num(m1['durbin_watson'])} به دست آمد که در دامنه مجاز ۱.۵ تا ۲.۵ قرار دارد و گویای استقلال پسماندهاست. همچنین شاخص‌های عامل تورم واریانس (VIF) کمتر از ۱.۹۱ و رواداری بالاتر از ۰.۵۲ بوده که حاکی از عدم وجود همخطی چندگانه است.\n"
        f"نتایج تحلیل واریانس مدل نشان داد که ترکیب خطی متغیرهای پیش‌بین قادر به پیش‌بینی معنادار رفتارهای خودآسیبی است "
        f"(F({to_fa_num(m1['df1'])}، {to_fa_num(m1['df2'])}) = {to_fa_num(m1['F'])}، p < ۰.۰۰۱). "
        f"ضریب همبستگی چندگانه برابر با R = {to_fa_num(m1['R'])} و ضریب تعیین تعدیل‌شده برابر با Adj R² = {to_fa_num(m1['Adj_R2'])} حاصل شد؛ به این معنا که ۳۴.۵ درصد از کل واریانس رفتارهای خودآسیبی در دانش‌آموزان توسط این سه متغیر تبیین می‌گردد.\n"
        f"بررسی ضرایب رگرسیونی نشان داد که متغیر افسردگی قوی‌ترین پیش‌بین رفتارهای خودآسیبی است (β = {to_fa_num(c1['Depression_Total']['Beta'])}، t = {to_fa_num(c1['Depression_Total']['t'])}، p < ۰.۰۰۱). "
        f"همچنین متغیرهای اضطراب (β = {to_fa_num(c1['Anxiety_Total']['Beta'])}، t = {to_fa_num(c1['Anxiety_Total']['t'])}، p = {to_fa_num(c1['Anxiety_Total']['p'])}) و "
        f"بدشکل‌انگاری بدن (β = {to_fa_num(c1['BodyDysmorphia_Total']['Beta'])}، t = {to_fa_num(c1['BodyDysmorphia_Total']['t'])}، p = {to_fa_num(c1['BodyDysmorphia_Total']['p'])}) نیز هر یک سهم مثبت و معناداری در پیش‌بینی رفتارهای خودآسیبی داشتند. جدول (۴-۵) خلاصه مدل و ضرایب استاندارد را منعکس کرده است."
    )
    apply_run_font(r_m1_narr, font_name="B Nazanin", size_pt=13)
    
    # Table 4-5: Regression 1
    p_cap5 = doc.add_paragraph()
    apply_p_rtl(p_cap5, justify=False)
    r_cap5 = p_cap5.add_run("جدول ۴-۵. نتایج رگرسیون چندگانه خطی در پیش‌بینی رفتارهای خودآسیبی (متغیر ملاک: SHI)")
    apply_run_font(r_cap5, font_name="B Titr", size_pt=11, bold=True)
    
    tbl5 = doc.add_table(rows=1, cols=7)
    format_apa_table(tbl5, col_widths=[2.2, 0.7, 0.7, 0.7, 0.7, 0.7, 0.9])
    hdr_titles5 = ["متغیرهای پیش‌بین", "B", "SE", "Beta (β)", "t", "p", "فاصله اطمینان ۹۵%"]
    for i, t in enumerate(hdr_titles5):
        p = tbl5.rows[0].cells[i].paragraphs[0]
        apply_p_rtl(p, justify=False)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(t)
        apply_run_font(r, font_name="B Titr", size_pt=10, bold=True)
        
    for p_var, p_info in c1.items():
        row = tbl5.add_row()
        ci_str = f"[{to_fa_num(p_info['ci_95'][0])} , {to_fa_num(p_info['ci_95'][1])}]"
        p_val_str = "۰.۰۰۱ >" if p_info["p"] < 0.001 else to_fa_num(p_info["p"])
        vals = [
            p_info["name_fa"],
            to_fa_num(p_info["B"]),
            to_fa_num(p_info["SE"]),
            to_fa_num(p_info["Beta"]),
            to_fa_num(p_info["t"]),
            p_val_str,
            ci_str
        ]
        for idx, val in enumerate(vals):
            p = row.cells[idx].paragraphs[0]
            apply_p_rtl(p, justify=False)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if idx > 0 else WD_ALIGN_PARAGRAPH.RIGHT
            r = p.add_run(val)
            apply_run_font(r, font_name="B Nazanin", size_pt=11)
            
    format_apa_table(tbl5, col_widths=[2.2, 0.7, 0.7, 0.7, 0.7, 0.7, 0.9])
    
    p_note5 = doc.add_paragraph()
    apply_p_rtl(p_note5, justify=False)
    r_n5 = p_note5.add_run(f"یادداشت. R = {to_fa_num(m1['R'])}؛ R² = {to_fa_num(m1['R2'])}؛ Adj R² = {to_fa_num(m1['Adj_R2'])}؛ F({to_fa_num(m1['df1'])}، {to_fa_num(m1['df2'])}) = {to_fa_num(m1['F'])}؛ ۰.۰۰۱ > p؛ دوربین-واتسون = {to_fa_num(m1['durbin_watson'])}.")
    apply_run_font(r_n5, font_name="B Nazanin", size_pt=10, italic=True)
    
    # Embed Residual Histogram Figure 1
    plot1_path = "02_processed_data/plots/residual_hist_self_harm.png"
    if os.path.exists(plot1_path):
        p_fig1 = doc.add_paragraph()
        p_fig1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_picture(plot1_path, width=Inches(4.5))
        p_fcap1 = doc.add_paragraph()
        apply_p_rtl(p_fcap1, justify=False)
        p_fcap1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_fc1 = p_fcap1.add_run("نمودار ۴-۱. توزیع نرمال پسماندهای استاندارد مدل رگرسیون پیش‌بینی رفتارهای خودآسیبی")
        apply_run_font(r_fc1, font_name="B Titr", size_pt=10, bold=True)
        
    doc.add_paragraph() # Spacing
    
    # 8. Multiple Regression Model 2: Suicide
    p_h7 = doc.add_paragraph()
    apply_p_rtl(p_h7, justify=False)
    r_h7 = p_h7.add_run("۷-۴. آزمون فرضیه‌های پیش‌بینی تمایل و رفتارهای خودکشی (رگرسیون چندگانه خطی)")
    apply_run_font(r_h7, font_name="B Titr", size_pt=15, bold=True)
    
    m2 = stats_data["regression_suicide"]["model_summary"]
    c2 = stats_data["regression_suicide"]["coefficients"]
    
    p_m2_narr = doc.add_paragraph()
    apply_p_rtl(p_m2_narr, justify=True)
    r_m2_narr = p_m2_narr.add_run(
        "برای آزمون توان متغیرهای پیش‌بین در تبیین تمایل و رفتارهای خودکشی (SBQ-R)، رگرسیون چندگانه به روش همزمان اجرا شد. "
        f"شاخص دوربین-واتسون برابر با {to_fa_num(m2['durbin_watson'])} به دست آمد که عدم وابستگی پسماندها را اثبات نمود.\n"
        f"آزمون معناداری کلی مدل رگرسیونی نشان داد که این الگو در سطح آماری بسیار بالایی معنادار است "
        f"(F({to_fa_num(m2['df1'])}، {to_fa_num(m2['df2'])}) = {to_fa_num(m2['F'])}، p < ۰.۰۰۱). "
        f"ضریب تعیین مدل برابر با R² = {to_fa_num(m2['R2'])} و ضریب تعیین تعدیل‌شده برابر با Adj R² = {to_fa_num(m2['Adj_R2'])} محاسبه شد؛ به این معنا که ۳۶.۷ درصد از تغییرات نمره خودکشی توسط متغیرهای مدل پیش‌بینی می‌شود.\n"
        f"بررسی ضرایب استاندارد شده نشان داد که افسردگی با ضریب بتای فوق‌العاده بالا (β = {to_fa_num(c2['Depression_Total']['Beta'])}، t = {to_fa_num(c2['Depression_Total']['t'])}، p < ۰.۰۰۱) تعیین‌کننده‌ترین پیش‌بین گرایش به خودکشی در نوجوانان است. "
        f"نگرانی از بدشکل‌انگاری بدن نیز با مقدار (β = {to_fa_num(c2['BodyDysmorphia_Total']['Beta'])}، t = {to_fa_num(c2['BodyDysmorphia_Total']['t'])}، p = {to_fa_num(c2['BodyDysmorphia_Total']['p'])}) پیش‌بین مثبت و معنادار تمایل به خودکشی بود. "
        f"با این حال، نقش اضطراب پس از کنترل افسردگی و بدشکلی بدن غیرمعنادار شد (β = {to_fa_num(c2['Anxiety_Total']['Beta'])}، t = {to_fa_num(c2['Anxiety_Total']['t'])}، p = {to_fa_num(c2['Anxiety_Total']['p'])})؛ "
        "این یافته حاکی از آن است که واریانس مشترک اضطراب با خودکشی عمدتاً توسط بار هم‌پوشانی افسردگی جذب شده است. جدول (۴-۶) جزئیات ضرایب را گزارش می‌نماید."
    )
    apply_run_font(r_m2_narr, font_name="B Nazanin", size_pt=13)
    
    # Table 4-6: Regression 2
    p_cap6 = doc.add_paragraph()
    apply_p_rtl(p_cap6, justify=False)
    r_cap6 = p_cap6.add_run("جدول ۴-۶. نتایج رگرسیون چندگانه خطی در پیش‌بینی تمایل و رفتارهای خودکشی (متغیر ملاک: SBQ-R)")
    apply_run_font(r_cap6, font_name="B Titr", size_pt=11, bold=True)
    
    tbl6 = doc.add_table(rows=1, cols=7)
    format_apa_table(tbl6, col_widths=[2.2, 0.7, 0.7, 0.7, 0.7, 0.7, 0.9])
    for i, t in enumerate(hdr_titles5):
        p = tbl6.rows[0].cells[i].paragraphs[0]
        apply_p_rtl(p, justify=False)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(t)
        apply_run_font(r, font_name="B Titr", size_pt=10, bold=True)
        
    for p_var, p_info in c2.items():
        row = tbl6.add_row()
        ci_str = f"[{to_fa_num(p_info['ci_95'][0])} , {to_fa_num(p_info['ci_95'][1])}]"
        p_val_str = "۰.۰۰۱ >" if p_info["p"] < 0.001 else to_fa_num(p_info["p"])
        vals = [
            p_info["name_fa"],
            to_fa_num(p_info["B"]),
            to_fa_num(p_info["SE"]),
            to_fa_num(p_info["Beta"]),
            to_fa_num(p_info["t"]),
            p_val_str,
            ci_str
        ]
        for idx, val in enumerate(vals):
            p = row.cells[idx].paragraphs[0]
            apply_p_rtl(p, justify=False)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if idx > 0 else WD_ALIGN_PARAGRAPH.RIGHT
            r = p.add_run(val)
            apply_run_font(r, font_name="B Nazanin", size_pt=11)
            
    format_apa_table(tbl6, col_widths=[2.2, 0.7, 0.7, 0.7, 0.7, 0.7, 0.9])
    
    p_note6 = doc.add_paragraph()
    apply_p_rtl(p_note6, justify=False)
    r_n6 = p_note6.add_run(f"یادداشت. R = {to_fa_num(m2['R'])}؛ R² = {to_fa_num(m2['R2'])}؛ Adj R² = {to_fa_num(m2['Adj_R2'])}؛ F({to_fa_num(m2['df1'])}، {to_fa_num(m2['df2'])}) = {to_fa_num(m2['F'])}؛ ۰.۰۰۱ > p؛ دوربین-واتسون = {to_fa_num(m2['durbin_watson'])}.")
    apply_run_font(r_n6, font_name="B Nazanin", size_pt=10, italic=True)
    
    # Embed Residual Histogram Figure 2
    plot2_path = "02_processed_data/plots/residual_hist_suicide.png"
    if os.path.exists(plot2_path):
        p_fig2 = doc.add_paragraph()
        p_fig2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        doc.add_picture(plot2_path, width=Inches(4.5))
        p_fcap2 = doc.add_paragraph()
        apply_p_rtl(p_fcap2, justify=False)
        p_fcap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r_fc2 = p_fcap2.add_run("نمودار ۴-۲. توزیع نرمال پسماندهای استاندارد مدل رگرسیون پیش‌بینی گرایش به خودکشی")
        apply_run_font(r_fc2, font_name="B Titr", size_pt=10, bold=True)
        
    doc.add_paragraph() # Spacing
    
    # 9. Binary Logistic Regression Models (Clinical Cut-offs)
    p_h8 = doc.add_paragraph()
    apply_p_rtl(p_h8, justify=False)
    r_h8 = p_h8.add_run("۸-۴. تحلیل رگرسیون لجستیک دوتایی در پیش‌بینی خطر بالینی خودآسیبی و خودکشی")
    apply_run_font(r_h8, font_name="B Titr", size_pt=15, bold=True)
    
    log1 = stats_data["logistic_self_harm"]
    log2 = stats_data["logistic_suicide"]
    
    p_log_narr = doc.add_paragraph()
    apply_p_rtl(p_log_narr, justify=True)
    r_log_narr = p_log_narr.add_run(
        "با توجه به ماهیت پزشکی و روان‌پزشکی این مطالعه، تعیین بخت (نسبت شانس / Odds Ratio) قرارگیری دانش‌آموزان در دسته‌های بالینی پرخطر اهمیت بالینی بسزایی دارد. "
        "بدین منظور دو مدل رگرسیون لجستیک باینری برای پیش‌بینی الف) قرارگیری در گروه بالینی خودآسیبی شدید (SHI ≥ ۵) و ب) قرارگیری در گروه در معرض خطر بالای خودکشی (SBQ-R ≥ ۷) برازش شد.\n"
        f"در مدل اول (پیش‌بینی خطر بالینی خودآسیبی)، آزمون جامع ضرایب (Omnibus Test) معناداری کلی مدل را اثبات نمود (χ²({to_fa_num(log1['omnibus_test']['df'])}) = {to_fa_num(log1['omnibus_test']['chi2'])}، p < ۰.۰۰۱). "
        f"ضریب تعیین ناگلکرکه برابر با {to_fa_num(log1['model_summary']['nagelkerke_r2'])} به دست آمد. بر اساس آماره والد، به ازای هر یک نمره افزایش در افسردگی، شانس قرارگیری در گروه پرخطر خودآسیبی ۱۰.۵ درصد افزایش می‌یابد (OR = {to_fa_num(log1['coefficients']['Depression_Total']['Exp_B_OR'])}، Wald = {to_fa_num(log1['coefficients']['Depression_Total']['Wald'])}، p < ۰.۰۰۱). "
        f"همچنین به ازای هر یک نمره افزایش در بدشکل‌انگاری بدن، شانس قرارگیری در گروه خودآسیبی ۷.۵ درصد بیشتر می‌شود (OR = {to_fa_num(log1['coefficients']['BodyDysmorphia_Total']['Exp_B_OR'])}، Wald = {to_fa_num(log1['coefficients']['BodyDysmorphia_Total']['Wald'])}، p = {to_fa_num(log1['coefficients']['BodyDysmorphia_Total']['p'])}).\n"
        f"در مدل دوم (پیش‌بینی خطر بالینی خودکشی)، آزمون جامع ضرایب حاکی از برازش مطلوب مدل بود (χ²({to_fa_num(log2['omnibus_test']['df'])}) = {to_fa_num(log2['omnibus_test']['chi2'])}، p < ۰.۰۰۱) و ضریب تعیین ناگلکرکه مقدار قابل توجه {to_fa_num(log2['model_summary']['nagelkerke_r2'])} را تبیین نمود. "
        f"به ازای هر یک نمره افزایش در نمره افسردگی، بخت قرارگیری آزمودنی‌ها در منطقه پرخطر خودکشی ۱۷.۲ درصد افزایش می‌یابد (OR = {to_fa_num(log2['coefficients']['Depression_Total']['Exp_B_OR'])}، Wald = {to_fa_num(log2['coefficients']['Depression_Total']['Wald'])}، p < ۰.۰۰۱). "
        f"نگرانی از بدشکلی بدن نیز احتمال خطر خودکشی را به ازای هر واحد افزایش، ۶.۵ درصد ارتقا می‌دهد (OR = {to_fa_num(log2['coefficients']['BodyDysmorphia_Total']['Exp_B_OR'])}، Wald = {to_fa_num(log2['coefficients']['BodyDysmorphia_Total']['Wald'])}، p = {to_fa_num(log2['coefficients']['BodyDysmorphia_Total']['p'])}). جدول (۴-۷) ضرایب رگرسیون لجستیک را خلاصه می‌کند."
    )
    apply_run_font(r_log_narr, font_name="B Nazanin", size_pt=13)
    
    # Table 4-7: Logistic Regression
    p_cap7 = doc.add_paragraph()
    apply_p_rtl(p_cap7, justify=False)
    r_cap7 = p_cap7.add_run("جدول ۴-۷. نتایج رگرسیون لجستیک دوتایی در پیش‌بینی عضویت در گروه‌های پرخطر بالینی (N = ۵۱۲)")
    apply_run_font(r_cap7, font_name="B Titr", size_pt=11, bold=True)
    
    tbl7 = doc.add_table(rows=1, cols=7)
    format_apa_table(tbl7, col_widths=[1.5, 1.8, 0.7, 0.7, 0.7, 0.7, 1.0])
    hdr_titles7 = ["مدل بالینی", "متغیر پیش‌بین", "B", "SE", "Wald", "p", "Exp(B) [۹۵% CI]"]
    for i, t in enumerate(hdr_titles7):
        p = tbl7.rows[0].cells[i].paragraphs[0]
        apply_p_rtl(p, justify=False)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(t)
        apply_run_font(r, font_name="B Titr", size_pt=10, bold=True)
        
    models_logit = [
        ("خطر خودآسیبی (SHI ≥ ۵)", log1["coefficients"]),
        ("خطر خودکشی (SBQ-R ≥ ۷)", log2["coefficients"])
    ]
    for m_label, m_coeffs in models_logit:
        for p_idx, (p_var, p_info) in enumerate(m_coeffs.items()):
            row = tbl7.add_row()
            m_cell_str = m_label if p_idx == 0 else ""
            p_val_str = "۰.۰۰۱ >" if p_info["p"] < 0.001 else to_fa_num(p_info["p"])
            or_ci_str = f"{to_fa_num(p_info['Exp_B_OR'])} [{to_fa_num(p_info['ci_95'][0])}-{to_fa_num(p_info['ci_95'][1])}]"
            vals = [
                m_cell_str,
                p_info["name_fa"],
                to_fa_num(p_info["B"]),
                to_fa_num(p_info["SE"]),
                to_fa_num(p_info["Wald"]),
                p_val_str,
                or_ci_str
            ]
            for idx, val in enumerate(vals):
                p = row.cells[idx].paragraphs[0]
                apply_p_rtl(p, justify=False)
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER if idx >= 2 else WD_ALIGN_PARAGRAPH.RIGHT
                r = p.add_run(val)
                apply_run_font(r, font_name="B Nazanin", size_pt=11)
                
    format_apa_table(tbl7, col_widths=[1.5, 1.8, 0.7, 0.7, 0.7, 0.7, 1.0])
    doc.add_paragraph() # Spacing
    
    # 10. Gender Differences Section
    p_h9 = doc.add_paragraph()
    apply_p_rtl(p_h9, justify=False)
    r_h9 = p_h9.add_run("۹-۴. مقایسه تفاوت‌های جنسیتی در متغیرهای آسیب‌شناسی روانی (آزمون t مستقل)")
    apply_run_font(r_h9, font_name="B Titr", size_pt=15, bold=True)
    
    g_comp = stats_data["gender_comparisons"]
    p_g_narr = doc.add_paragraph()
    apply_p_rtl(p_g_narr, justify=True)
    r_g_narr = p_g_narr.add_run(
        "به منظور بررسی تفاوت نمرات متغیرهای پژوهش بر حسب جنسیت، آزمون t برای گروه‌های مستقل به کار گرفته شد. "
        f"بررسی‌ها نشان داد که دانش‌آموزان دختر در مقایسه با پسران در تمامی متغیرها نمرات بالاتری به دست آورده‌اند. "
        f"نمرات افسردگی دختران (M = {to_fa_num(g_comp['Depression_Total']['girls']['mean'])}) به طور معناداری بالاتر از پسران (M = {to_fa_num(g_comp['Depression_Total']['boys']['mean'])}) بود (t({to_fa_num(g_comp['Depression_Total']['df'])}) = {to_fa_num(g_comp['Depression_Total']['t'])}، p < ۰.۰۰۱، Cohen's d = {to_fa_num(g_comp['Depression_Total']['cohen_d'])}). "
        f"همچنین دختران اضطراب به مراتب بالاتری را نسبت به پسران گزارش کردند (M = {to_fa_num(g_comp['Anxiety_Total']['girls']['mean'])} در برابر M = {to_fa_num(g_comp['Anxiety_Total']['boys']['mean'])}) که دارای اندازه اثر بزرگ بود (t({to_fa_num(g_comp['Anxiety_Total']['df'])}) = {to_fa_num(g_comp['Anxiety_Total']['t'])}، p < ۰.۰۰۱، d = {to_fa_num(g_comp['Anxiety_Total']['cohen_d'])}). "
        f"نگرانی از بدشکلی بدن (p = {to_fa_num(g_comp['BodyDysmorphia_Total']['p'])}، d = {to_fa_num(g_comp['BodyDysmorphia_Total']['cohen_d'])})، "
        f"رفتارهای خودآسیبی (p = {to_fa_num(g_comp['SHI_Total']['p'])}، d = {to_fa_num(g_comp['SHI_Total']['cohen_d'])}) و "
        f"گرایش به خودکشی (p < ۰.۰۰۱، d = {to_fa_num(g_comp['Suicide_Total']['cohen_d'])}) همگی در دختران به طور معناداری بیشتر از پسران به دست آمد. جدول (۴-۸) نتایج این آزمون را نشان می‌دهد."
    )
    apply_run_font(r_g_narr, font_name="B Nazanin", size_pt=13)
    
    # Table 4-8: Gender Comparison
    p_cap8 = doc.add_paragraph()
    apply_p_rtl(p_cap8, justify=False)
    r_cap8 = p_cap8.add_run("جدول ۴-۸. مقایسه میانگین متغیرهای پژوهش در بین دانش‌آموزان دختر و پسر (آزمون t مستقل)")
    apply_run_font(r_cap8, font_name="B Titr", size_pt=11, bold=True)
    
    tbl8 = doc.add_table(rows=1, cols=7)
    format_apa_table(tbl8, col_widths=[2.0, 1.1, 1.1, 0.7, 0.7, 0.7, 0.7])
    hdr_titles8 = ["متغیر", "دختران (n=۳۴۳)", "پسران (n=۱۶۹)", "t", "df", "p", "d کوهن"]
    for i, t in enumerate(hdr_titles8):
        p = tbl8.rows[0].cells[i].paragraphs[0]
        apply_p_rtl(p, justify=False)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(t)
        apply_run_font(r, font_name="B Titr", size_pt=10, bold=True)
        
    for var_key, g_info in g_comp.items():
        row = tbl8.add_row()
        g_str = f"{to_fa_num(g_info['girls']['mean'])} ± {to_fa_num(g_info['girls']['sd'])}"
        b_str = f"{to_fa_num(g_info['boys']['mean'])} ± {to_fa_num(g_info['boys']['sd'])}"
        p_val_str = "۰.۰۰۱ >" if g_info["p"] < 0.001 else to_fa_num(g_info["p"])
        vals = [
            g_info["name_fa"],
            g_str,
            b_str,
            to_fa_num(g_info["t"]),
            to_fa_num(g_info["df"]),
            p_val_str,
            to_fa_num(g_info["cohen_d"])
        ]
        for idx, val in enumerate(vals):
            p = row.cells[idx].paragraphs[0]
            apply_p_rtl(p, justify=False)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if idx > 0 else WD_ALIGN_PARAGRAPH.RIGHT
            r = p.add_run(val)
            apply_run_font(r, font_name="B Nazanin", size_pt=11)
            
    format_apa_table(tbl8, col_widths=[2.0, 1.1, 1.1, 0.7, 0.7, 0.7, 0.7])
    doc.add_paragraph() # Spacing
    
    # 11. Master Hypotheses Decision Matrix & Summary
    p_h10 = doc.add_paragraph()
    apply_p_rtl(p_h10, justify=False)
    r_h10 = p_h10.add_run("۱۰-۴. جدول ماتریس جمع‌بندی نهایی فرضیات و نتیجه‌گیری فصل چهارم")
    apply_run_font(r_h10, font_name="B Titr", size_pt=15, bold=True)
    
    p_h_narr = doc.add_paragraph()
    apply_p_rtl(p_h_narr, justify=True)
    r_h_narr = p_h_narr.add_run(
        "در این بخش، نتایج آزمون فرضیه‌های شش‌گانه پژوهش به صورت یکپارچه گردآوری شده است. "
        "بر این اساس، از مجموع ۶ فرضیه تدوین‌شده در پروپوزال، ۵ فرضیه با اطمینان ۹۵ و ۹۹ درصد مورد تأیید آماری قرار گرفتند و تنها فرضیه مربوط به پیش‌بینی مستقیم تمایل به خودکشی توسط اضطراب رد شد. "
        "جدول (۴-۹) ماتریس تصمیم‌گیری نهایی فرضیات را منعکس می‌نماید."
    )
    apply_run_font(r_h_narr, font_name="B Nazanin", size_pt=13)
    
    # Table 4-9: Master Hypotheses Decision Matrix
    p_cap9 = doc.add_paragraph()
    apply_p_rtl(p_cap9, justify=False)
    r_cap9 = p_cap9.add_run("جدول ۴-۹. ماتریس جمع‌بندی و وضعیت تأیید یا رد فرضیه‌های پژوهش")
    apply_run_font(r_cap9, font_name="B Titr", size_pt=11, bold=True)
    
    tbl9 = doc.add_table(rows=1, cols=6)
    format_apa_table(tbl9, col_widths=[0.6, 2.5, 0.9, 0.8, 0.8, 1.1])
    hdr_titles9 = ["ردیف", "عنوان فرضیه پژوهش", "ضریب استاندارد (β)", "آماره آزمون (t)", "سطح معناداری (p)", "نتیجه آزمون"]
    for i, t in enumerate(hdr_titles9):
        p = tbl9.rows[0].cells[i].paragraphs[0]
        apply_p_rtl(p, justify=False)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(t)
        apply_run_font(r, font_name="B Titr", size_pt=10, bold=True)
        
    for h in stats_data["hypotheses_decision_matrix"]:
        row = tbl9.add_row()
        p_val_str = "۰.۰۰۱ >" if h["p"] < 0.001 else to_fa_num(h["p"])
        vals = [
            to_fa_num(h["num"]),
            h["title_fa"],
            to_fa_num(h["beta"]),
            to_fa_num(h["t"]),
            p_val_str,
            h["verdict"]
        ]
        for idx, val in enumerate(vals):
            p = row.cells[idx].paragraphs[0]
            apply_p_rtl(p, justify=False)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if idx in [0, 2, 3, 4, 5] else WD_ALIGN_PARAGRAPH.RIGHT
            r = p.add_run(val)
            bold_flag = True if idx == 5 else False
            apply_run_font(r, font_name="B Nazanin", size_pt=11, bold=bold_flag)
            
    format_apa_table(tbl9, col_widths=[0.6, 2.5, 0.9, 0.8, 0.8, 1.1])
    
    # 12. Whole Chapter Summary & Bridge to Chapter 5
    p_sum_h = doc.add_paragraph()
    apply_p_rtl(p_sum_h, justify=False)
    r_sum_h = p_sum_h.add_run("۱۱-۴. جمع‌بندی جامع یافته‌ها و پل انتقال به فصل پنجم")
    apply_run_font(r_sum_h, font_name="B Titr", size_pt=15, bold=True)
    
    p_sum = doc.add_paragraph()
    apply_p_rtl(p_sum, justify=True)
    r_sum = p_sum.add_run(
        "یافته‌های تجربی و آماری فصل چهارم نشان داد که رفتارهای خودآسیبی و خطر خودکشی چالش‌های بهداشت روانی چشمگیری در بین نوجوانان دبیرستانی شهر قم به شمار می‌روند. "
        "برآورد شیوع اپیدمیولوژیک نشان داد که حدود ۳۵ درصد از نوجوانان در آستانه خطر بالینی آسیب به خود و نزدیک به ۳۰ درصد در منطقه خطر اقدام به خودکشی قرار دارند. "
        "همچنین متغیرهای افسردگی و بدشکل‌انگاری بدن به عنوان تعیین‌کننده‌ترین متغیرهای پیش‌بین مستقل در افزایش رفتارهای خودآسیبی و تمایل به خودکشی شناخته شدند و دختران در مقایسه با پسران آسیب‌پذیری به مراتب بالاتری در تمامی شاخص‌های آسیب‌شناسی روانی نشان دادند.\n"
        "در فصل بعدی (فصل پنجم: بحث و نتیجه‌گیری)، نتایج آماری حاصل از این فصل در پرتو نظریه‌های روان‌شناختی (نظریه شناختی-رفتاری، نظریه بین‌فردی خودکشی جوینر، و الگوهای تصویر بدنی) و شواهد تجربی و پیشینه پژوهش‌های پیشین در داخل و خارج از کشور به تفکیک هر یک از فرضیات مورد تبیین علمی قرار گرفته و پیامدهای کاربردی و بالینی آن در محیط‌های آموزشی و بهداشتی مورد بحث واقع خواهد شد."
    )
    apply_run_font(r_sum, font_name="B Nazanin", size_pt=13)
    
    doc.save(out_path)
    print(f"Successfully generated full Chapter 4 DOCX deliverable: {out_path}")

if __name__ == "__main__":
    main()
