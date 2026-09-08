---
name: irandoc-plagiarism-reducer
description: Expert academic paraphrasing and similarity reduction skill for Iranian graduate theses and dissertations submitted to Irandoc (همانندجو / سمیم‌نور). Executes deep syntactic clause inversion, thematic literature synthesis, and scientific synonym substitution to reduce similarity scores below university defense thresholds (typically < 20% or < 30%) while strictly preserving APA 7 in-text citations, scientific terminology, Persian half-spaces (نیم‌فاصله), and OpenXML typography. Generates both a revised Word document (.docx) and a side-by-side comparison report.
---

# Irandoc Plagiarism Reducer (کاهش همانندجویی و بازنویسی آکادمیک ایرانداک)

## Overview
This skill provides systematic, publication-grade academic paraphrasing to reduce similarity percentages in Iranian Master's theses and Doctoral dissertations flagged by the **Irandoc SamimNoor / همانندجو** system. Rather than engaging in shallow or robotic word swapping (which distorts scientific meaning and ruins academic flow), this skill employs deep structural reorganization, thematic background clustering, and syntactic inversion to shatter matching n-gram chains while strictly preserving APA 7 in-text citations and academic Persian rigor.

---

## 🔍 How Irandoc (همانندجو) Operates

The Irandoc engine scans submitted documents against a centralized corpus of Iranian theses, dissertations, and academic journals (SID, Magiran, Noormags, University Repositories). It flags:
1. **N-Gram Matching**: Continuous sequences of 4 to 7 identical or near-identical words.
2. **Formulaic Academic Cliches**: Repetitive framing phrases (e.g. *«در پژوهشی تحت عنوان ... به بررسی ... پرداختند و به این نتیجه رسیدند که ...»*).
3. **Unsynthesized Literature Reviews**: Paragraphs where each study is summarized in an isolated, sequential sentence.
4. **False Positives**: Bibliographies, cover pages, tables of contents, and questionnaires that were mistakenly left in the uploaded document.

---

## 🛡️ The 4-Pillar Deep Paraphrasing Methodology

To guarantee that similarity falls safely below the mandatory threshold (typically **under 20%** or **under 30%**) while elevating the scholarly quality of the text, the agent must execute four core transformations:

### 1. Syntactic Clause Inversion (تغییر ساختار نحوی و تقدم/تاخر بندها)
- Transform simple active constructions into passive or impersonal scientific voice, or vice versa:
  - *قبل*: «محققان متغیر خودتنظیمی هیجانی را به عنوان عامل واسطه‌ای مهم در مهار علائم درد معرفی کرده‌اند.»
  - *بعد*: «از منظر چارچوب‌های روان‌شناختی نوین، خودتنظیمی هیجانی جایگاهی واسطه‌ای در تعدیل بار هیجانی نشانه‌های درد ایفا می‌کند.»
- Pre-position dependent clauses and conditions (برعکس کردن ترتیب جملات پیرو و پایه):
  - *قبل*: «میزان اضطراب پس از مداخله به شدت کاهش یافت زیرا بیماران تکنیک‌های گسلش را فرا گرفتند.»
  - *بعد*: «با فراگیری راهبردهای گسلش شناختی توسط بیماران، افول محسوسی در تراز اضطراب پس از اعمال مداخله پدیدار گشت.»

### 2. Thematic Literature Synthesis (ادغام و خوشه‌بندی پیشینه‌ها)
Never leave isolated study-by-study listings. Combine 3 to 5 related studies into a single integrated thematic sentence:
- *قبل (شبیه ۳۰٪ تا ۵۰٪)*:
  > «رضایی (۱۴۰۰) در پژوهشی نشان داد که مداخله پذیرش و تعهد بر تاب‌آوری بیماران موثر است. محمدی (۱۴۰۱) نیز نشان داد که این درمان باعث بهبود کیفیت زندگی می‌شود. همچنین احمدی (۱۴۰۲) دریافت که درمان پذیرش و تعهد افسردگی بیماران را کاهش می‌دهد.»
- *بعد (همانندجویی زیر ۱۰٪ + ارتقای سطح آکادمیک)*:
  > «شواهد تجربی چندگانه در جامعه پژوهشی داخل کشور بر کارآمدی پایدار پروتکل‌های مبتنی بر پذیرش در ابعاد گوناگون سلامت روان، از جمله ارتقای تاب‌آوری و کیفیت زندگی و نیز مهار نشانگان افسردگی صحه گذاشته‌اند (احمدی، ۱۴۰۲؛ محمدی، ۱۴۰۱؛ رضایی، ۱۴۰۰).»

### 3. Scientific Synonym & Cliche Transformation (جایگزینی تعابیر کلیشه‌ای)
Systematically replace high-risk repetitive verbs and connectors:
- «نشان دادند که» $\to$ *«حاکی از آن بود که» / «گواهی می‌دهد بر» / «مبین آن است که» / «موید این واقعیت است که»*
- «به بررسی ... پرداختند» $\to$ *«کارآمدی ... را مورد سنجش قرار دادند» / «پدیدارشناسی ... را به آزمون گذاشتند»*
- «بنابراین / در نتیجه» $\to$ *«بر همین اساس» / «از این رو» / «بدین ترتیب» / «در پرتو این شواهد»*
- «اثربخش بود / تاثیر معناداری داشت» $\to$ *«بهبود چشمگیری حاصل نمود» / «تغییرات معناداری را رقم زد» / «نقش تعدیل‌کننده نیرومندی به همراه داشت»*

### 4. Strict Citation & Typography Preservation (حفظ ارجاعات و نیم‌فاصله)
- **Citations**: All in-text citations (e.g. `(Beck, 2011)` or `(محمدی، ۱۴۰۱)`) must be preserved without altering names, dates, or parenthetical conventions.
- **Half-spaces**: All compound Persian verbs and plurals must maintain correct نیم‌فاصله (`\u200c`): `می‌شود`, `پیش‌آزمون`, `یافته‌ها`.

---

## 📋 Irandoc Upload Hygiene Protocol

Before advising the student to upload their document to Irandoc:
1. **Remove the Title Page & Preliminary Matter**: Cover page, approval sheet, dedication, and Persian/English abstracts often contain institutional templates that match thousands of university documents.
2. **Remove the Table of Contents & Lists**: TOC and Table/Figure lists cause extensive false-positive n-gram matches.
3. **Remove Chapter 4 Full Statistical Tables**: Numbers and standard table headers match other theses. Keep only the narrative text.
4. **Remove References & Questionnaires**: Bibliographies and questionnaire items trigger 70–90% similarity. Submit strictly the body text of Chapters 1, 2, 3, 4 (narrative), and 5.

---

## 🛠️ CLI Engine Usage

The skill provides [`paraphrase_engine.py`](scripts/paraphrase_engine.py) to analyze and rewrite text:

```bash
# 1. Paraphrase a Word document and generate a side-by-side comparison report
python3 .agents/skills/irandoc-plagiarism-reducer/scripts/paraphrase_engine.py \
  --input "فصل_دوم_ادبیات_پژوهش.docx" \
  --output-docx "فصل_دوم_بازنویسی_ایرانداک.docx" \
  --output-report "گزارش_مقایسه‌ای_کاهش_همانندجویی.docx"

# 2. Analyze raw text string or file and view estimated similarity reduction
python3 .agents/skills/irandoc-plagiarism-reducer/scripts/paraphrase_engine.py \
  --input "problem_statement.txt" \
  --mode text \
  --output-docx "problem_statement_rewritten.docx"
```
