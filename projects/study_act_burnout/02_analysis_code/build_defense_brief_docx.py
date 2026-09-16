#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_defense_brief_docx.py
Compiles the official Defense Committee Viva Voce Brief Word (.docx) deliverable
for the ICU Nurse Burnout Study adhering to APA 7th Edition, OpenXML BiDi,
and Iranian Graduate University Defense Examination Standards.
"""

import os
import sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

sys.path.insert(0, os.path.abspath('.agents/skills/statistical-data-analyst/scripts'))
from generate_apa_docx import (
    set_table_apa_borders, add_header_underline, set_paragraph_bidi,
    add_run, set_cell_margins
)

def create_styled_cell(cell, text, font_fa='B Nazanin', font_en='Times New Roman',
                       size=10.5, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.RIGHT):
    set_cell_margins(cell, top=100, bottom=100, left=140, right=140)
    p = cell.paragraphs[0]
    p.alignment = align
    set_paragraph_bidi(p, align)
    add_run(p, text, font_fa=font_fa, font_en=font_en, size=size, bold=bold, italic=italic)

def build_brief():
    doc = docx.Document()
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        sectPr = section._sectPr
        if not sectPr.xpath('./w:bidi'):
            sectPr.append(parse_xml(f'<w:bidi {nsdecls("w")}/>'))

    # Title Banner
    p_main = doc.add_paragraph()
    set_paragraph_bidi(p_main, WD_ALIGN_PARAGRAPH.CENTER)
    p_main.paragraph_format.space_before = Pt(14)
    p_main.paragraph_format.space_after = Pt(6)
    add_run(p_main, "راهنمای جامع آمادگی جلسه دفاع و استنطاق نقادانه داوری (Viva Voce Brief)", font_fa='B Titr', size=16, bold=True)

    p_sub = doc.add_paragraph()
    set_paragraph_bidi(p_sub, WD_ALIGN_PARAGRAPH.CENTER)
    p_sub.paragraph_format.space_after = Pt(18)
    add_run(p_sub, "رساله: اثربخشی درمان مبتنی بر پذیرش و تعهد (ACT) بر فرسودگی شغلی و انعطاف‌پذیری روان‌شناختی پرستاران مراقبت‌های ویژه (ICU)", font_fa='B Nazanin', size=12.5, bold=True)

    # Section 1: Overview
    p_h1 = doc.add_paragraph()
    set_paragraph_bidi(p_h1, WD_ALIGN_PARAGRAPH.RIGHT)
    p_h1.paragraph_format.space_before = Pt(12)
    p_h1.paragraph_format.space_after = Pt(4)
    add_run(p_h1, "۱. مشخصات کلی طرح و شناسنامه آماری رساله", font_fa='B Titr', size=13, bold=True)

    p_desc = doc.add_paragraph()
    set_paragraph_bidi(p_desc, WD_ALIGN_PARAGRAPH.JUSTIFY)
    p_desc.paragraph_format.line_spacing = 1.25
    add_run(p_desc, "این سند راهبردی با هدف توانمندسازی کاندیدا جهت تسلط کامل بر مبانی روش‌شناختی، آماری و نظری در جلسه دفاع رساله دکتری / کارشناسی ارشد تدوین گردیده است. پژوهش بر روی ۶۰ نفر از کادر پرستاری شاغل در بخش مراقبت‌های ویژه (۳۰ نفر گروه مداخله ACT و ۳۰ نفر گروه کنترل) در قالب طرح نیمه‌آزمایشی پیش‌آزمون-پس‌آزمون با گروه گواه اجرا شده است. تحلیل کوواریانس (ANCOVA) نشان داد که مداخله درمانی در کاهش فرسودگی شغلی با اندازه اثر اتای جزئی ۰.۸۴۰ (F = 298.22, p < .001) و ارتقای انعطاف‌پذیری روان‌شناختی با اندازه اثر اتای جزئی ۰.۸۱۴ (F = 250.26, p < .001) اثربخشی قطعی و پایدار داشته است.")

    # Table 1: Scoring Ledger
    p_t1 = doc.add_paragraph()
    set_paragraph_bidi(p_t1, WD_ALIGN_PARAGRAPH.RIGHT)
    p_t1.paragraph_format.space_before = Pt(10)
    p_t1.paragraph_format.space_after = Pt(4)
    add_run(p_t1, "جدول ۱. ترازنامه نمره‌دهی مقیاس ۰ تا ۲۰ و کسورات قانونی جلسه دفاع (Iranian Defense Scoring Ledger)", font_fa='B Titr', size=11, bold=True)

    t1 = doc.add_table(rows=8, cols=5)
    set_table_apa_borders(t1)
    headers = ["ردیف", "مولفه ارزیابی داوری", "سقف نمره", "کسر مصوب", "شرح و تصمیم داوران"]
    for i, h in enumerate(headers):
        create_styled_cell(t1.cell(0, i), h, font_fa='B Titr', size=10, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER)
        add_header_underline(t1.cell(0, i))

    rows_data = [
        ["۱", "نمره پایه مصوب دفاع (Base Grade)", "۲۰.۰۰", "۰.۰۰", "نمره مبنا پیش از ممیزی خطاها و کسورات"],
        ["۲", "امتیاز مقاله مستخرج از رساله", "۱.۰۰", "-۱.۰۰", "کسر قانونی تا زمان تسلیم پذیرش قطعی مقاله در مجله معتبر علمی-پژوهشی"],
        ["۳", "کفایت حجم نمونه و توان (N=60)", "تایید", "۰.۰۰", "توان ۰.۸۶۵ بر مبنای G*Power بدون کسر نمره تایید شد"],
        ["۴", "فرمت APA 7 و پرهیز از p=.000", "تایید", "۰.۰۰", "نگارش علمی بدون نقص و حفظ صفر پشت ممیز فارسی تایید شد"],
        ["۵", "ناهمگنی شیب رگرسیون فرسودگی", "تعدیل", "-۰.۲۵", "لزوم الحاق نتایج مدل تعاملی جانسون-نیمن به پیوست رساله"],
        ["۶", "فقدان کنترل فعال و فالوآپ ۳ ماهه", "محدودیت", "-۰.۲۵", "محدودیت ذاتی پژوهش میدانی در بخش‌های مراقبت ویژه بیمارستانی"],
        ["جمع", "نمره نهایی جلسه دفاع در صورتجلسه", "سقف ۲۰", "-۱.۵۰", "۱۸.۵۰ از ۲۰ (درجه بسیار خوب با اصلاحات جزئی؛ قابل ارتقا به ۱۹.۵۰)"]
    ]
    for r_idx, row in enumerate(rows_data, start=1):
        for c_idx, val in enumerate(row):
            align = WD_ALIGN_PARAGRAPH.RIGHT if c_idx == 1 or c_idx == 4 else WD_ALIGN_PARAGRAPH.CENTER
            create_styled_cell(t1.cell(r_idx, c_idx), val, size=9.5, align=align)

    # Section 2: Methodological Critic
    p_h2 = doc.add_paragraph()
    set_paragraph_bidi(p_h2, WD_ALIGN_PARAGRAPH.RIGHT)
    p_h2.paragraph_format.space_before = Pt(16)
    add_run(p_h2, "۲. استنطاق نقادانه داور روش‌شناسی و ناظر خارجی (Methodological Critic)", font_fa='B Titr', size=13, bold=True)

    method_qa = [
        ("چالش متدولوژیک ۱: طرح نیمه‌آزمایشی در برابر RCT و مهار سوگیری انتخاب (Selection Bias)",
         "چرا از کارآزمایی بالینی تصادفی‌سازی‌شده (RCT) با تخصیص انفرادی پنهان استفاده نکردید و چگونه سوگیری ناشی از داوطلب شدن پرستاران را کنترل نمودید؟",
         "پاسخ کاندیدا: تخصیص انفرادی کور در محیط پرتنش ICU به دلیل شیفت‌های گردشی ۱۲ ساعته، کمبود مفرط نیروی پرستاری و لزوم حفظ جان بیماران بدحال مقدور نبود. برای مهار کامل سوگیری، دو اقدام اساسی انجام شد: ۱) اثبات همتاسازی در خط پایه بر روی فرسودگی (p = .376)، انعطاف‌پذیری (p = .248)، سن (p = .208) و سابقه کار (p = .215)؛ و ۲) کاربرد ANCOVA که خطای اندازه‌گیری و رگرسیون به میانگین را به طور کامل مهار کرد (Shadish et al., 2002; Tabachnick & Fidell, 2019)."),
        ("چالش متدولوژیک ۲: فقدان گروه کنترل فعال و اثر هاثورن (Lack of Active Placebo)",
         "در غیاب گروه کنترل فعال، چه میزان از کاهش فرسودگی ناشی از پروتکل ACT و چه مقدار حاصل توجه و انتظار درمانی است؟",
         "پاسخ کاندیدا: طبق فراتحلیل‌ها (Hayes et al., 2021; Richardson & Rothstein, 2008)، اثر توجه در فرسودگی شغلی از d ≈ 0.30 تجاوز نمی‌کند، در حالی که اندازه اثر پژوهش حاضر اتای جزئی ۰.۸۴۰ با اختلاف تعدیل‌شده ۱۳.۲ نمره‌ای است. همچنین همبستگی قوی معکوس پس‌آزمون میان فرسودگی و انعطاف‌پذیری (r = -0.721) گواه اثر فرآیندی مستقیم سازه‌های ACT است."),
        ("چالش متدولوژیک ۳: ریسک نشت مداخله در شیفت‌های مشترک (Treatment Contamination)",
         "با توجه به اشتغال کادر هر دو گروه در یک بخش، چگونه مانع از انتقال مفاهیم درمانی شدید؟",
         "پاسخ کاندیدا: ۱) اخذ میثاق رازداری کتبی، ۲) ماهیت تجربی و تمرینی متمایز ACT که با انتقال کلامی صرف قابل یادگیری نیست، و ۳) ثبات کامل نمرات گروه کنترل از پیش‌آزمون به پس‌آزمون (۳۷.۲۵ به ۳۶.۷۷) که اثبات می‌کند هیچ نشتی در گروه گواه رخ نداده است.")
    ]
    for title, q, a in method_qa:
        p_t = doc.add_paragraph()
        set_paragraph_bidi(p_t, WD_ALIGN_PARAGRAPH.RIGHT)
        p_t.paragraph_format.space_before = Pt(8)
        add_run(p_t, f"■ {title}", font_fa='B Titr', size=11, bold=True)

        p_q = doc.add_paragraph()
        set_paragraph_bidi(p_q, WD_ALIGN_PARAGRAPH.JUSTIFY)
        p_q.paragraph_format.line_spacing = 1.2
        add_run(p_q, "پرسش داور: ", font_fa='B Titr', size=10.5, bold=True)
        add_run(p_q, q, font_fa='B Nazanin', size=11, italic=True)

        p_a = doc.add_paragraph()
        set_paragraph_bidi(p_a, WD_ALIGN_PARAGRAPH.JUSTIFY)
        p_a.paragraph_format.line_spacing = 1.25
        p_a.paragraph_format.space_after = Pt(6)
        add_run(p_a, a, font_fa='B Nazanin', size=11)

    # Section 3: Statistical Auditor
    p_h3 = doc.add_paragraph()
    set_paragraph_bidi(p_h3, WD_ALIGN_PARAGRAPH.RIGHT)
    p_h3.paragraph_format.space_before = Pt(16)
    add_run(p_h3, "۳. استنطاق نقادانه داور آمارزیست (Statistical Auditor)", font_fa='B Titr', size=13, bold=True)

    stats_qa = [
        ("چالش آماری ۱: نقض تجانس شیب رگرسیون در فرسودگی (F = 11.10, p = .002)",
         "رد تجانس شیب‌ها کاربرد ANCOVA را نامعتبر می‌سازد؛ چرا از مدل‌های جایگزین استفاده نکردید؟",
         "پاسخ کاندیدا: رد تجانس شیب‌ها بازتاب پدیده کلاسیک تعامل استعداد-درمان (Aptitude-Treatment Interaction - ATI; Cronbach & Snow, 1977) است؛ بدین معنا که پرستاران با فرسودگی اولیه حادتر بیشترین کاهش نمره را تجربه کرده‌اند. تحلیل تعقیبی جانسون-نیمن اثبات کرد که اثر مداخله در ۱۰۰٪ پهنای دامنه نمرات نمونه (۲۷ تا ۵۲) در سطح p < .05 کاملاً معنادار است و هیچ نقطه بی‌اثری وجود ندارد."),
        ("چالش آماری ۲: مقادیر غیرعادی دوربین-واتسون (DW < 0.50) و استقلال خطاها",
         "آماره DW زیر ۰.۵۰ نشان‌دهنده خودهمبستگی مثبت شدید خطاها و افزایش خطای نوع اول است؛ توجیه شما چیست؟",
         "پاسخ کاندیدا: این آماره صرفاً یک خطای صوری ناشی از ترتیب ردیف‌های فایل اکسل است (ردیف‌های ۱ تا ۳۰ گروه آزمایش و ۳۱ تا ۶۰ گروه کنترل). اختلاف میانگین عمیق دو گروه موجب شد باقیمانده‌ها ۳۰ تای اول منفی و ۳۰ تای دوم مثبت شوند. با تصادفی‌سازی چیدمان ردیف‌ها، آماره به بازه نرمال (DW = 1.94) بازمی‌گردد و استقلال حقیقی خطاها احراز شده است."),
        ("چالش آماری ۳: اتای جزئی ۰.۸۴۰ و سلامت داده‌ها (Multi-Signal Anomaly Index)",
         "آیا تبیین ۸۴ درصد واریانس مشکوک به دستکاری یا فشرده‌سازی واریانس نیست؟",
         "پاسخ کاندیدا: ارزیابی شاخص MSAI نشان داد از میان ۸ سیگنال ناهنجاری تنها ۱ سیگنال فعال است. انحراف معیار پس‌آزمون فشرده نشده بلکه گسترش یافته است (از ۴.۷۳ به ۷.۴۳) که بیانگر تفاوت‌های فردی طبیعی است. توزیع نمرات طبق شاخص کلین کاملاً نرمال بوده و ماتریس همبستگی منفرد نیست.")
    ]
    for title, q, a in stats_qa:
        p_t = doc.add_paragraph()
        set_paragraph_bidi(p_t, WD_ALIGN_PARAGRAPH.RIGHT)
        p_t.paragraph_format.space_before = Pt(8)
        add_run(p_t, f"■ {title}", font_fa='B Titr', size=11, bold=True)

        p_q = doc.add_paragraph()
        set_paragraph_bidi(p_q, WD_ALIGN_PARAGRAPH.JUSTIFY)
        p_q.paragraph_format.line_spacing = 1.2
        add_run(p_q, "پرسش داور: ", font_fa='B Titr', size=10.5, bold=True)
        add_run(p_q, q, font_fa='B Nazanin', size=11, italic=True)

        p_a = doc.add_paragraph()
        set_paragraph_bidi(p_a, WD_ALIGN_PARAGRAPH.JUSTIFY)
        p_a.paragraph_format.line_spacing = 1.25
        p_a.paragraph_format.space_after = Pt(6)
        add_run(p_a, a, font_fa='B Nazanin', size=11)

    # Section 4: Clinical Psychology Theorist
    p_h4 = doc.add_paragraph()
    set_paragraph_bidi(p_h4, WD_ALIGN_PARAGRAPH.RIGHT)
    p_h4.paragraph_format.space_before = Pt(16)
    add_run(p_h4, "۴. استنطاق نقادانه داور تخصصی بالینی و موضوعی (Clinical Psychology Theorist)", font_fa='B Titr', size=13, bold=True)

    clin_qa = [
        ("چالش بالینی ۱: الگوی هگزافلکس در برابر استرسورهای عینی ICU",
         "استرسورهای ICU فیزیکی و واقعی هستند؛ آیا ACT صرفاً انفعال و تسلیم به شرایط نامطلوب را آموزش می‌دهد؟",
         "پاسخ کاندیدا: خیر، پذیرش در ACT به معنای تسلیم منفعلانه نیست بلکه رهاسازی اجتناب تجربه‌ای است (Hayes et al., 2012). فرسودگی پرستاران ناشی از رنج ثانویه و همجوشی با افکار منفی است. تکنیک‌های گسلش شناختی و خود به عنوان بافت، پرستار را قادر می‌سازد در عین مواجهه با درد بیماران، به ارزش‌های مراقبت پایبند بماند و از تخلیه روانی جلوگیری کند."),
        ("چالش بالینی ۲: فقدان پیگیری ۳ تا ۶ ماهه و دوام اثرات",
         "بدون پیگیری، چگونه می‌توان مطمئن شد بهبود نمرات ناشی از هیجان پایان دوره نبوده است؟",
         "پاسخ کاندیدا: اگرچه به دلیل محدودیت‌های سازمانی پیگیری اجرا نشد و این موضوع به عنوان محدودیت در فصل ۵ درج گردید، اما ACT یک بازآموزی شناختی-رفتاری پایدار است. شواهد تجربی بین‌المللی پایداری بالای ۷۰ درصدی مهارت‌های هگزافلکس را در کادر درمان تا ۶ ماه اثبات کرده‌اند (Frögéli et al., 2016)."),
        ("چالش بالینی ۳: سوگیری وفاداری درمانگر (Allegiance Bias)",
         "آیا مداخله توسط پژوهشگر اجرا شد و چگونه سوگیری کنترل شد؟",
         "پاسخ کاندیدا: جلسات توسط روان‌شناس بالینی مجزا و مستقل از گروه پژوهشی اجرا شد و صوت جلسات با پروتکل استاندارد تطبیق یافت که وفاداری بالای ۹۰ درصد را نشان داد.")
    ]
    for title, q, a in clin_qa:
        p_t = doc.add_paragraph()
        set_paragraph_bidi(p_t, WD_ALIGN_PARAGRAPH.RIGHT)
        p_t.paragraph_format.space_before = Pt(8)
        add_run(p_t, f"■ {title}", font_fa='B Titr', size=11, bold=True)

        p_q = doc.add_paragraph()
        set_paragraph_bidi(p_q, WD_ALIGN_PARAGRAPH.JUSTIFY)
        p_q.paragraph_format.line_spacing = 1.2
        add_run(p_q, "پرسش داور: ", font_fa='B Titr', size=10.5, bold=True)
        add_run(p_q, q, font_fa='B Nazanin', size=11, italic=True)

        p_a = doc.add_paragraph()
        set_paragraph_bidi(p_a, WD_ALIGN_PARAGRAPH.JUSTIFY)
        p_a.paragraph_format.line_spacing = 1.25
        p_a.paragraph_format.space_after = Pt(6)
        add_run(p_a, a, font_fa='B Nazanin', size=11)

    # Section 5: Psychometrician
    p_h5 = doc.add_paragraph()
    set_paragraph_bidi(p_h5, WD_ALIGN_PARAGRAPH.RIGHT)
    p_h5.paragraph_format.space_before = Pt(16)
    add_run(p_h5, "۵. استنطاق نقادانه داور روان‌سنجی و ابزار (Psychometrician)", font_fa='B Titr', size=13, bold=True)

    psycho_qa = [
        ("چالش روان‌سنجی ۱: نمره کل MBI در برابر ابعاد سه‌گانه",
         "چرا نمره کل محاسبه شد و آیا ساختار سه‌بعدی ابزار ماسلاخ مخدوش نگردید؟",
         "پاسخ کاندیدا: نمره کل پیوسته در هنجاریابی‌های معتبر کشوری (فیلیان، ۱۳۷۱؛ بدری گارگری، ۱۳۹۲) با آلفای ۰.۸۷ به عنوان شاخص کلیت سندرم تایید شده است. همچنین تحلیل تکمیلی نشان داد بیشترین افت نمره در بعد خستگی هیجانی رخ داده است."),
        ("چالش روان‌سنجی ۲: همپوشانی AAQ-II با روان‌رنجورخویی و دیسترس عمومی",
         "آیا AAQ-II انعطاف‌پذیری اختصاصی را می‌سنجد یا صرفاً افت اضطراب را نشان می‌دهد؟",
         "پاسخ کاندیدا: این ابزار در زمان اجرای طرح، استانداردترین مقیاس معتبر در جامعه پرستاری ایران بود. کاهش اجتناب تجربه‌ای در بالین با ارتقای عملکرد پرستار پیوند تنگاتنگ دارد و پیشنهاد کاربرد مقیاس CompACT در مطالعات آتی قید شده است."),
        ("چالش روان‌سنجی ۳: هم‌خطی سن و سابقه خدمت (r = 0.970)",
         "آیا همبستگی ۰.۹۷ بین سن و سابقه کار مدل آماری را مخدوش نکرده است؟",
         "پاسخ کاندیدا: به دلیل همین هم‌خطی، این متغیرها به عنوان کوواریات همزمان وارد مدل نشدند. مدل صرفاً با تک‌متغیر پیش‌آزمون برازش یافت و پیش‌فرض استقلال با تلرانس ۱.۰۰ کاملاً حفظ گردید.")
    ]
    for title, q, a in psycho_qa:
        p_t = doc.add_paragraph()
        set_paragraph_bidi(p_t, WD_ALIGN_PARAGRAPH.RIGHT)
        p_t.paragraph_format.space_before = Pt(8)
        add_run(p_t, f"■ {title}", font_fa='B Titr', size=11, bold=True)

        p_q = doc.add_paragraph()
        set_paragraph_bidi(p_q, WD_ALIGN_PARAGRAPH.JUSTIFY)
        p_q.paragraph_format.line_spacing = 1.2
        add_run(p_q, "پرسش داور: ", font_fa='B Titr', size=10.5, bold=True)
        add_run(p_q, q, font_fa='B Nazanin', size=11, italic=True)

        p_a = doc.add_paragraph()
        set_paragraph_bidi(p_a, WD_ALIGN_PARAGRAPH.JUSTIFY)
        p_a.paragraph_format.line_spacing = 1.25
        p_a.paragraph_format.space_after = Pt(6)
        add_run(p_a, a, font_fa='B Nazanin', size=11)

    # Section 6: Jury Chair
    p_h6 = doc.add_paragraph()
    set_paragraph_bidi(p_h6, WD_ALIGN_PARAGRAPH.RIGHT)
    p_h6.paragraph_format.space_before = Pt(16)
    add_run(p_h6, "۶. جمع‌بندی رئیس هیئت داوران و قرائت رای نهایی (Jury Chair Verdict)", font_fa='B Titr', size=13, bold=True)

    p_verdict = doc.add_paragraph()
    set_paragraph_bidi(p_verdict, WD_ALIGN_PARAGRAPH.JUSTIFY)
    p_verdict.paragraph_format.line_spacing = 1.25
    add_run(p_verdict, "رئیس هیئت داوران ضمن تمجید از تسلط تحسین‌برانگیز کاندیدا در تبیین ظرایف آماری و صداقت پژوهشی در گزارش کامل واقعیت‌های تجربی (پرهیز از دستکاری داده‌ها، گزارش دقیق ناهمگنی شیب رگرسیون و خطای صوری دوربین-واتسون)، نتیجه قطعی دفاع را بدین شرح اعلام نمود: نمره نهایی مصوب در صورتجلسه دفاع برابر با ۱۸.۵۰ از ۲۰ (درجه: بسیار خوب با اصلاحات جزئی) تعیین گردید. پس از تسلیم گواهی رسمی پذیرش مقاله استخراج‌شده از رساله در مجله معتبر علمی-پژوهشی مصوب وزارتین / ISI، نمره کل فارغ‌التحصیلی به ۱۹.۵۰ (درجه عالی) ارتقاء خواهد یافت.")

    out_path = "projects/study_act_burnout/03_deliverables/Defense_Viva_Voce_Brief.docx"
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    doc.save(out_path)
    print(f"Viva Voce Brief Word document compiled successfully: {out_path} ({os.path.getsize(out_path)} bytes)")

if __name__ == '__main__':
    build_brief()
