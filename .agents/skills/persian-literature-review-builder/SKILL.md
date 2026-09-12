---
name: persian-literature-review-builder
description: >-
  Expert Chapter 2 (فصل دوم: مبانی نظری و پیشینه پژوهش) synthesis and compilation skill for graduate theses and
  dissertations in psychology, counseling, behavioral sciences, and education. Translates and integrates English
  theoretical foundations (strictly avoiding copying from Persian theses to prevent cliches and high Irandoc similarity),
  structures multi-variable conceptual models, synthesizes recent Iranian (Magiran, SID, ISC) and international
  (Scopus, PubMed, WoS) empirical literature using a standardized 5-part reporting formula, embeds APA 7 borderless
  empirical summary tables, identifies empirical research gaps, and compiles defense-ready Word (.docx) documents
  formatted with authentic Iranian typography (B Titr, B Nazanin, Times New Roman, and OpenXML BiDi RTL) alongside
  multi-sheet Excel literature matrices.
---

# Persian Literature Review & Chapter 2 Builder Skill (نگارش و تدوین فصل دوم: مبانی نظری و پیشینه پژوهش)

This skill empowers Antigravity to act as an elite academic literature review architect and Chapter 2 compiler for Master's and Doctoral theses in Psychology, Counseling, Behavioral Sciences, and Education.

---

## 1. When to Activate This Skill

Activate this skill when:
1. The user requests drafting or compiling **Chapter 2 of a graduate thesis/dissertation (فصل دوم پایان‌نامه یا رساله)**.
2. The user needs to structure and write the **Theoretical Foundations (مبانی نظری)** for multiple research variables (Independent, Dependent, Mediator, Moderator).
3. The user has foreign/English dissertations, theses, or literature and wants to translate and integrate their theoretical chapters into academic Persian.
4. The user needs to review, organize, and report **Recent Empirical Studies (پیشینه پژوهش‌های تجربی)** divided into **Iranian Studies (پیشینه داخلی)** and **International Studies (پیشینه خارجی)**.
5. The user needs a formal **APA 7th Edition Empirical Summary Table (جدول خلاصه پیشینه پژوهش‌های تجربی)**.
6. The user needs to formulate the **Research Gap (شناسایی شکاف پژوهشی)** and construct the **Conceptual Model (چارچوب و مدل مفهومی پژوهش)** based on theoretical and empirical synthesis.

---

## 2. Core Architectural Directives

### Directive 1: Translation of Foreign Theses vs. Persian Thesis Avoidance
> [!IMPORTANT]
> **قانون بنیادین عدم استفاده از پایان‌نامه‌های فارسی برای مبانی نظری**:
> - در نگارش بخش مبانی نظری، **هرگز** نباید از متن پایان‌نامه‌های فارسی کپی یا بازنویسی شود (زیرا سبب تکرار کلیشه‌های قدیمی، خطاهای استنادی، و درصد همانندجویی بسیار بالا در سامانه ایرانداک می‌شود).
> - **روش اجرایی**: رساله‌ها و پایان‌نامه‌های دکتری انگلیسی مرتبط با متغیرهای پژوهش دانلود شده و فصول مبانی نظری آن‌ها بر اساس اصول مهندسی ترجمه (`persian-academic-translation`)، واژگان تخصصی مصوب و نیم‌فاصله‌های استاندارد (`\u200c`) ترجمه و بازآرایی می‌شوند.

### Directive 2: Standard 5-Part Empirical Reporting Formula
هر پاراگراف معرفی پیشینه تجربی (داخلی و خارجی) باید دقیقاً شامل ۵ جزء باشد:
1. **پژوهشگر(ان) و سال**: با رعایت دقیق APA 7 (مانند *رضوانی و همکاران (۱۳۹۹)* یا *گونزالز-بوسو و همکاران (۲۰۲۰)*).
2. **هدف / عنوان پژوهش**: هدف مشخص مطالعه در سنجش متغیرها.
3. **جامعه و نمونه**: مشخصات شرکت‌کنندگان و حجم نمونه ($N$).
4. **طرح پژوهش و ابزارها**: روش تحقیق (SEM، همبستگی، آزمایشی) و پرسشنامه‌ها.
5. **یافته‌های کلیدی**: جهت روابط، ضرایب معناداری ($p < .05$)، و اندازه‌های اثر.

### Directive 3: APA 7 Empirical Summary Table
- نام جدول: `جدول ۲-۱: خلاصه پیشینه پژوهش‌های تجربی داخلی و خارجی`
- ستون‌ها: `ردیف`، `پژوهشگر(ان) و سال`، `جامعه و نمونه`، `روش و ابزار`، `متغیرها`، `یافته‌های کلیدی`
- خطوط جدول: **فقط ۳ خط افقی** (بالای جدول، زیر سرستون، انتهای جدول)، **بدون هرگونه خط عمودی**، همراه با صفت جهت‌داری راست‌به‌چپ (`<w:bidiVisual/>`).

### Directive 4: Synthesis, Research Gap & Conceptual Model
- شناسایی دقیق تضادها یا کمبودهای مطالعات پیشین (شکاف پژوهشی).
- پیوند مکانیسم‌های نظری با فرضیات پژوهش و ارائه دیاگرام یا تبیین مدل مفهومی.

### Directive 5: Zero Ghost Citations & Mandatory Source Ingestion (قاعده ضد رفرنس‌های ارواح و الزام دانلود فیزیکی منابع در 04_references_and_lit)
> [!IMPORTANT]
> **ممنوعیت مطلق ارجاع از حافظه بدون استناد به منبع فیزیکی**:
> ۱. چنانچه ایجنت از حافظه زایشی خود به پژوهشگری ارجاع دهد، **الزاماً** باید منبع مربوطه از طریق CrossRef، OpenAlex، PubMed یا پایگاه‌های داخلی (SID / Magiran) اعتبارسنجی شده و فایل مقاله (PDF) در پوشه `04_references_and_lit/papers/` بارگیری شود.
> ۲. **انطباق متن با یافته‌های واقعی**: متغیرها، جهت اثر (مثبت/منفی)، حجم نمونه ($N$) و نتایج گزارش‌شده در پاراگراف‌های فصل دوم باید با چکیده و متن مقاله دانلودشده کاملاً همخوان باشد. نگارش ادعاهای توهمی یا انتساب نتایج غیرواقعی به نویسندگان اکیداً ممنوع است.
> ۳. ثبت متادیتای مقاله در `Literature_Synthesis_Matrix.xlsx` و فایل‌های خروجی کتابشناختی (`.ris` / `.enw`) الزامی است.

### Directive 6: Contemporary Empirical Horizon (افق زمانی پیشینه تجربی معاصر: ۲۰۲۱–۲۰۲۶ / ۱۴۰۰–۱۴۰۵)
- در تدوین بخش پیشینه تجربی (داخلی و خارجی)، تمرکز اصلی باید بر مقالات منتشرشده در ۳ تا ۵ سال اخیر یعنی بازه **۲۰۲۱ تا ۲۰۲۶ میلادی** و **۱۴۰۰ تا ۱۴۰۵ هجری شمسی** باشد.
- مطالعات کلاسیک و بنیادین در بخش مبانی نظری (نظریه‌ها و الگوهای مفهومی) محفوظ می‌مانند، اما پیشینه تجربی مؤید روابط متغیرها باید تازه‌ترین شواهد پژوهشی موجود را منعکس کند.

---

## 3. Chapter 2 Hierarchical Outline

```text
فصل دوم: مبانی نظری و پیشینه پژوهش
├── ۲-۱. مقدمه (پیوند متغیرهای پژوهش با اهداف کلی)
├── ۲-۲. مبانی نظری متغیرهای پژوهش
│   ├── ۲-۲-۱. مبانی نظری متغیر اول (تعاریف، ابعاد، مدل‌ها و نظریه‌ها)
│   ├── ۲-۲-۲. مبانی نظری متغیر دوم (تعاریف، ابعاد، مدل‌ها و نظریه‌ها)
│   ├── ۲-۲-۳. مبانی نظری متغیر سوم (تعاریف، ابعاد، مدل‌ها و نظریه‌ها)
│   ├── ۲-۲-۴. مبانی نظری متغیر میانجی / تعدیل‌کننده
│   └── ۲-۲-۵. تبیین نظری پیوند و روابط متقابل میان متغیرها
├── ۲-۳. پیشینه تجربی پژوهش
│   ├── ۲-۳-۱. پیشینه پژوهش‌های خارجی (International Studies)
│   ├── ۲-۳-۲. پیشینه پژوهش‌های داخلی (Iranian Studies)
│   └── ۲-۳-۳. جدول ۲-۱: خلاصه پیشینه پژوهش‌های تجربی داخلی و خارجی (APA 7)
├── ۲-۴. جمع‌بندی پیشینه پژوهش و شناسایی شکاف پژوهشی (Research Gap)
└── ۲-۵. مدل مفهومی و فرضیات پژوهش (Conceptual Model)
```

---

## 4. Execution Workflow

### Step 1: Prepare the Structured Chapter 2 Payload
Create a JSON file (`ch2_payload.json`) specifying the variables, translated theoretical paragraphs, international and Iranian empirical studies, research gap, and conceptual model.

### Step 2: Execute the Automated Compilation Engine
Run `literature_review_engine.py` via CLI:
```bash
python3 .agents/skills/persian-literature-review-builder/scripts/literature_review_engine.py \
  --json path/to/ch2_payload.json \
  --out-dir path/to/output_directory \
  --lang fa
```

### Step 3: Inspect Generated Deliverables
The engine deterministically compiles:
1. `فصل_دوم_مبانی_نظری_و_پیشینه_پژوهش.docx`:
   - Authentic Iranian academic typography (*B Titr 16pt Bold* for Chapter title, *B Titr 14pt* for Section headings, *B Nazanin 13pt Regular* for body text, *Times New Roman 11pt* for English citations/numbers).
   - Paragraph formatting: Justified (`JUSTIFY`), line spacing 1.25, BiDi RTL `<w:bidi w:val="1"/>`.
   - Embedded APA 7 borderless empirical summary table (`<w:bidiVisual/>`).
2. `empirical_literature_matrix.xlsx`:
   - 3 professional sheets: `Overview & Metrics`, `International Studies`, and `Iranian Studies` with frozen panes, navy headers, and auto-adjusted column widths.
3. `literature_summary.json`:
   - Machine-readable synthesis of reviewed studies, variables, and research gap status.

---

## 5. Input Schema Guidelines

```json
{
  "chapter_title": "فصل دوم: مبانی نظری و پیشینه پژوهش",
  "study_title": "عنوان پژوهش / رساله",
  "study_title_en": "English Research Title",
  "introduction": "متن مقدمه فصل دوم...",
  "theoretical_sections": [
    {
      "section_number": "۲-۱",
      "variable_name": "نام متغیر اول",
      "variable_name_en": "Variable 1 English",
      "content_paragraphs": [
        "پاراگراف اول ترجمه شده از رساله یا منبع خارجی...",
        "پاراگراف دوم شامل نظریه‌ها و مدل‌ها..."
      ]
    }
  ],
  "theoretical_integration": "تبیین نظری پیوند میان متغیرها...",
  "international_studies": [
    {
      "authors": "نام نویسندگان به فارسی",
      "authors_en": "Authors in English",
      "year": "2022",
      "title": "عنوان پژوهش خارجی",
      "sample": "مشخصات و حجم نمونه",
      "methodology": "روش تحقیق و ابزارها",
      "variables": "متغیرهای مورد بررسی",
      "key_findings": "یافته‌های کلیدی پژوهش"
    }
  ],
  "iranian_studies": [
    {
      "authors": "نام نویسندگان ایرانی",
      "authors_en": "Authors in English",
      "year": "1400",
      "title": "عنوان پژوهش داخلی",
      "sample": "مشخصات و حجم نمونه",
      "methodology": "روش تحقیق و ابزارها",
      "variables": "متغیرهای مورد بررسی",
      "key_findings": "یافته‌های کلیدی پژوهش"
    }
  ],
  "research_gap": "تبیین تفصیلی شکاف پژوهشی نظری و تجربی...",
  "conceptual_model": "تشریح مدل مفهومی و فرضیات برگرفته از پیشینه..."
}
```

---

## 6. Integration with AcademicSuite

- **Input Linkage**:
  - `persian-proposal-builder`: Ingests the variables and research objectives from Chapter 1 and Proposal.
  - `persian-academic-translation`: Translates English theoretical sections from foreign theses into the required JSON paragraphs.
- **Output Linkage**:
  - `academic-reference-extractor`: Scans `فصل_دوم_مبانی_نظری_و_پیشینه_پژوهش.docx` to extract all citations into EndNote (`.enw`), Zotero (`.ris`), and APA 7 (`.txt`).
  - `irandoc-plagiarism-reducer`: Checks similarity if required.
  - `persian-thesis-builder`: Direct input as `--ch2` in `compile_full_thesis.py`.
