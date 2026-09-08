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

### 1. Slide Canvas & Layout
- **Aspect Ratio**: 16:9 Widescreen (`13.333` inches $\times$ `7.5` inches).
- **Structure**: Visual cards and content containers with subtle shadow borders instead of dense bulleted text walls.
- **Density Rule**: Maximum 4–6 lines per text container; bold keywords for visual scannability.

### 2. Iranian Academic Typography
To ensure flawless presentation without OpenXML font degradation:
- **Slide Headings**: `B Titr` (Bold, 22–26 pt).
- **Body & Bullet Text**: `B Nazanin` or `B Lotus` (Regular/Bold, 16–18 pt).
- **Statistical Numbers & Terms**: `Times New Roman` or `Calibri` (14–16 pt).
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
The compiler supports 3 refined academic color schemes:
1. **`academic_navy` (Default)**:
   - Primary: Deep Academic Navy (`#1A365D`)
   - Accent: Warm Gold (`#D69E2E` / `#C59B27`)
   - Surface/Card: Pure White (`#FFFFFF`) with Slate Border (`#E2E8F0`)
   - Background: Soft Platinum Tint (`#F8FAFC`)
2. **`emerald_slate`**:
   - Primary: Deep Forest Teal (`#134E4A`)
   - Accent: Bright Emerald (`#059669`)
   - Surface/Card: Crisp Cream (`#FFFFFF`)
   - Background: Soft Mint Ice (`#F0FDF4`)
3. **`royal_burgundy`**:
   - Primary: Imperial Maroon (`#4A0E17`)
   - Accent: Warm Amber (`#D97706`)
   - Surface/Card: Crisp White (`#FFFFFF`)
   - Background: Soft Pearl (`#FFFBEB`)

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
