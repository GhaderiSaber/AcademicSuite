---
name: persian-defense-presentation-builder
description: Expert Persian academic thesis and dissertation defense presentation compiler. Ingests full theses (.docx), proposals, statistical results (stats_results.json), and discussion chapters to generate publication-grade, defense-ready PowerPoint presentations (.pptx) with native Right-to-Left (RTL) OpenXML formatting, authentic Iranian academic typography (B Titr, B Nazanin), card/container visual layouts, APA 7 tables, and detailed candidate Speaker Notes (متن گفتار دانشجو) for every slide.
---

# Persian Defense Presentation Builder (طراحی و تدوین اسلایدهای جلسه دفاع)

## Overview
This skill automates the compilation of academic defense slide decks for Iranian graduate students (Master's and PhD) in Psychology, Counseling, and Behavioral Sciences. It extracts core arguments, hypotheses, empirical tables, and theoretical explanations from project artifacts to assemble a 25–35 slide presentation in **Microsoft PowerPoint (`.pptx`)** formatted specifically for high-stakes university defense sessions.

---

## 🏛️ Defense Session Architecture & Timing Protocol

Iranian defense sessions typically allocate **20 to 30 minutes** for the candidate's oral presentation, followed by 30–60 minutes of examiner interrogation. The presentation is organized into 7 distinct phases:

```
[Phase 1: Identification & Title] (1-2 min)
  ├── Slide 1: بسم‌الله، آرم دانشگاه، عنوان مصوب رساله/پایان‌نامه، مقطع، دانشجو، اساتید
  └── Slide 2: اعضای هیئت داوران (استاد راهنما، مشاور، داوران داخلی و خارجی، ناظر تحصیلات تکمیلی)
       │
[Phase 2: Introduction & Justification] (3-4 min)
  ├── Slide 3: بیان مسئله و زمینه پژوهش (Problem Statement via Inverted Triangle)
  ├── Slide 4: ضرورت و اهمیت کاربردی و نظری پژوهش (Significance & Rationale)
  ├── Slide 5: اهداف پژوهش (هدف کلی و اهداف اختصاصی)
  └── Slide 6: فرضیه‌ها یا سوالات پژوهش (Research Hypotheses)
       │
[Phase 3: Theoretical & Empirical Foundations] (3-4 min)
  ├── Slide 7: چارچوب و مبانی نظری (Theoretical Framework: Beck, Bandura, Gross, Bowlby, etc.)
  ├── Slide 8: پیشینه تجربی و خلاء پژوهشی (Empirical Background & Research Gap Matrix)
  └── Slide 9: مدل مفهومی یا الگوی پژوهش (Conceptual Model / Framework)
       │
[Phase 4: Methodology & Design] (4-5 min)
  ├── Slide 10: طرح پژوهش و متغیرها (Research Design: شبه‌آزمایشی پیش‌آزمون-پس‌آزمون، همبستگی، و ...)
  ├── Slide 11: جامعه، حجم نمونه (محاسبه G*Power) و روش نمونه‌گیری
  ├── Slide 12: ابزارهای سنجش و متغیرها (پرسشنامه‌ها با نمره‌گذاری، روایی، پایایی آلفا)
  └── Slide 13: پروتکل جلسات مداخله/درمان (در صورت آزمایشی بودن: خلاصه جلسات در قالب جدول)
       │
[Phase 5: Statistical Findings & Hypotheses Testing] (7-8 min)
  ├── Slide 14: آمار توصیفی متغیرها (میانگین و انحراف معیار به تفکیک گروه‌ها و مراحل)
  ├── Slide 15: بررسی مفروضه‌های آماری (نرمالیتی، همگنی واریانس‌ها/لون، ماتریس کوواریانس/باکس، شیب رگرسیون)
  ├── Slide 16-19: آزمون فرضیه‌ها (جداول مانکوا/کوواریانس تک‌متغیری، رگرسیون سلسله‌مراتبی، میانجی‌گری با بوت‌استرپ)
  └── Slide 20: جمع‌بندی وضعیت فرضیه‌ها (ماتریس خلاصه تایید/رد فرضیه‌ها)
       │
[Phase 6: Discussion & Theoretical Mechanisms] (5-6 min)
  ├── Slide 21-23: بحث و تبیین روان‌شناختی یافته‌ها (Psychological & Neurocognitive Mechanisms)
  ├── Slide 24: همسویی و ناهمسویی با پژوهش‌های داخلی و خارجی (Consistency with Literature)
  ├── Slide 25: کاربردهای بالینی، مشاوره‌ای و سازمانی (Practical & Clinical Implications)
  ├── Slide 26: محدودیت‌های روش‌شناختی و اجرایی پژوهش (Methodological Limitations)
  └── Slide 27: پیشنهادات پژوهشی و کاربردی (Research & Actionable Recommendations)
       │
[Phase 7: Closure & Q&A] (1 min)
  └── Slide 28: سپاسگزاری، ثبت منابع منتخب و اعلام آمادگی برای پاسخ به سوالات داوران محترم
```

---

## 🎨 Visual & Typography Standards

### 1. Slide Canvas & Ultra-Modern Layouts
- **Aspect Ratio**: 16:9 Widescreen (`13.333` inches $\times$ `7.5` inches).
- **Layout Engines**:
  1. `cover`: Executive title layout with midnight navy backdrop, geometric gold framing, university header pills, and distinct candidate/supervisor profile cards.
  2. `committee`: 2x2 directory cards with academic rank badges, role icons, and appreciation headers.
  3. `split_diagram`: Asymmetric dual-column layout embedding high-resolution 300-DPI scientific diagrams (`image_path`), caption badges, and analytical cards.
  4. `kpi_dashboard`: Executive metric cards with 34–40pt bold numbers, status trend badges (`★ بسیار مطلوب`, `✓ کفایت نمونه`), and analytical takeaway container.
  5. `cards`: Enhanced container cards with individual `badge` tags (`[تحلیل عصب‌شناختی]`, `[بتا = -۰/۵۰]`), accent strips, and bottom **Key Takeaway Banners (`callout`)** for examiners.
  6. `table`: APA 7 tables with solid navy headers, zebra-striped data rows, embedded result badges (`✓ تأیید شد` in emerald green, `★ مطلوب`), and table note containers.
  7. `closing`: Executive closing slide with appreciation statement, inspirational quote, and defense Q&A announcement.
- **Scientific Figures Integration**: Generates and embeds 300-DPI figures (`sem_path_model.png`, `dual_systems_infographic.png`, `path_coefficients_chart.png`, `fit_benchmark_chart.png`, `demographics_chart.png`).
- **Density Rule**: Clean scannable hierarchy; maximum 4–6 bullet lines per card with bold keywords.

### 2. Iranian Academic Typography & OpenXML Standards
To ensure flawless presentation without OpenXML font degradation:
- **Slide Headings**: `B Titr` (Bold, 21–24 pt).
- **Body & Bullet Text**: `B Nazanin` (Regular/Bold, 13–15 pt).
- **Statistical Numbers & Terms**: `Times New Roman` or `Calibri` (12–34 pt).
- **OpenXML DrawingML Enforcement**:
  Every paragraph element (`<a:p>`) must include:
  ```xml
  <a:pPr algn="r" rtl="1">
    <a:defRPr>
      <a:cs typeface="B Nazanin"/>
    </a:defRPr>
  </a:pPr>
  ```

### 3. Curated Academic Color Palettes
1. **`academic_navy` (Default Executive)**:
   - Primary: Midnight Dark Navy (`#0F172A`)
   - Secondary: Royal Navy (`#1E3A8A`)
   - Accent: Warm Amber Gold (`#D97706` / `#F59E0B`)
   - Emerald Success: Vibrant Emerald (`#059669`)
   - Surface/Card: Pure White (`#FFFFFF`) with Slate-200 Border (`#E2E8F0`)
   - Background: Soft Platinum Tint (`#F8FAFC`)
2. **`emerald_slate`**:
   - Primary: Deep Forest Teal (`#134E4A`)
   - Secondary: Deep Sea Teal (`#0F766E`)
   - Accent: Bright Emerald (`#059669`)
   - Surface/Card: Crisp Cream (`#FFFFFF`) with Mint Ice Border (`#D1FAE5`)
3. **`royal_burgundy`**:
   - Primary: Imperial Maroon (`#4A0E17`)
   - Secondary: Rose Maroon (`#881337`)
   - Accent: Warm Amber (`#D97706`)

---

## 🎙️ Speaker Notes (متن گفتار و سخنرانی دانشجو)

A core feature of this skill is generating **comprehensive, ready-to-speak Iranian academic Persian speaker notes** attached to the `notes_slide` of every individual slide.

Each slide's notes section must provide:
1. **زمان پیشنهادی**: Suggested duration (e.g. `زمان پیشنهادی: ۴۵ ثانیه`).
2. **متن دقیق سخنرانی (Script)**: What the student should say word-for-word in formal, respectful academic Persian (e.g. *«اساتید گرامی و داوران ارجمند، در این اسلاید به بررسی آزمون فرضیه اول پرداخته شده است...»*).
3. **نکات کلیدی برای داوری (Defense Cues)**: Anticipated questions examiners might ask on this slide and the bullet-point counter-arguments the candidate should have ready.

---

## 🛠️ CLI Engine Usage

The skill provides [`compile_defense_presentation.py`](scripts/compile_defense_presentation.py) for building defense presentations:

```bash
# 1. Generate defense deck from a structured JSON configuration
python3 .agents/skills/persian-defense-presentation-builder/scripts/compile_defense_presentation.py \
  --json "defense_payload.json" \
  --output "جلسه_دفاع_پایان_نامه.pptx" \
  --theme academic_navy

# 2. Synthesize defense deck directly from project chapters & stats_results.json
python3 .agents/skills/persian-defense-presentation-builder/scripts/compile_defense_presentation.py \
  --title "اثربخشی درمان مبتنی بر پذیرش و تعهد بر خودتنظیمی هیجانی" \
  --author "دانشجو: صابر قادری" \
  --supervisor "استاد راهنما: دکتر ..." \
  --advisor "استاد مشاور: دکتر ..." \
  --university "دانشگاه سراسری تبریز - دانشکده علوم تربیتی و روان‌شناسی" \
  --degree "پایان‌نامه کارشناسی ارشد روان‌شناسی بالینی" \
  --stats-json "stats_results.json" \
  --ch1 "فصل_اول.docx" \
  --ch3 "فصل_سوم.docx" \
  --ch5 "فصل_پنجم.docx" \
  --output "جلسه_دفاع.pptx"
```
