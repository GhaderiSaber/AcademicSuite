---
name: psychological-intervention-protocol-builder
description: Expert psychological and educational intervention protocol drafting skill for experimental and quasi-experimental graduate theses in psychology, counseling, and behavioral sciences. Generates standardized Chapter 3 APA 7 session summary tables and comprehensive Appendix session-by-session clinical manuals (ACT, CBT, Schema Therapy, CFT, MBSR, Positive Psychotherapy, Mindful Parenting) complete with theoretical rationale, experiential techniques, clinical metaphors, in-session worksheets, and behavioral homework assignments in Word (.docx) and structured JSON format.
---

# Psychological Intervention Protocol Builder (طراحی و تدوین پروتکل مداخله و بسته آموزشی/درمانی)

## Overview
This skill automates the formulation, structuring, and compilation of evidence-based psychological and educational intervention protocols for Master's and Doctoral theses in Psychology, Counseling, and Behavioral Sciences. It produces two critical academic deliverables:
1. **Chapter 3 Summary Table (جدول خلاصه جلسات مداخله)**: A concise, defense-grade APA 7 table summarizing the objectives, topics, techniques, and homework for every session, designed for direct insertion into Chapter 3 (Methodology / روش‌شناسی) and proposals.
2. **Appendix Detailed Clinical Manual (پروتکل تفصیلی بسته درمانی/آموزشی)**: A comprehensive, publication-ready clinical manual in Microsoft Word (`.docx`) for the thesis Appendix (پیوست), detailing each session's psychoeducation, experiential exercises, clinical metaphors, worksheets, and inter-session homework.

---

## 🧩 Protocol Architecture & Session Components

In Iranian universities and international clinical research, defense examiners evaluate experimental protocols against strict fidelity criteria. Every session must include the following 6 pedagogical and clinical phases:

```
[Phase 1: Review & Mood Check] (10-15 min)
  ├── برقراری ارتباط حمایتی و سنجش خط پایه خلقی مراجعان در آغاز جلسه
  └── بازبینی تکالیف خانگی جلسه قبل و رفع چالش‌های شناختی/رفتاری مراجعان
       │
[Phase 2: Psychoeducation & Conceptual Rationale] (15-20 min)
  ├── معرفی موضوع محوری جلسه و مفهوم‌بندی روان‌شناختی آن
  └── پیوند موضوع جدید با چارچوب نظری کلی درمان (هگزافلکس، طرحواره‌ها، سیستم‌های هیجانی)
       │
[Phase 3: Experiential Technique or Metaphor] (20-25 min)
  ├── اجرای تمرین تجربی درون‌جلسه‌ای (Experiential Exercise: ذهن‌آگاهی، صندلی خالی، خودشفقت‌ورزی)
  └── ارائه استعاره‌های بالینی ملموس (Clinical Metaphors: شن روان، مسافران اتوبوس، قطب‌نما)
       │
[Phase 4: In-Session Worksheet / Group Practice] (15-20 min)
  ├── کاربست عملی تکنیک توسط مراجعان در قالب کاربرگ‌های کتبی (Worksheets)
  └── اشتراک‌گذاری تجارب و مفهوم‌بندی موقعیت‌های اختصاصی زندگی مراجعان
       │
[Phase 5: Behavioral Homework Assignment] (10 min)
  ├── تعیین تمرین‌های خانگی ساختاریافته بین‌جلسه‌ای (Self-monitoring, Diary, Behavioral Experiments)
  └── پیش‌بینی موانع احتمالی اجرای تکالیف در طول هفته
       │
[Phase 6: Session Summary & Feedback] (5 min)
  ├── جمع‌بندی نکات کلیدی جلسه توسط درمانگر یا مراجعان
  └── دریافت بازخورد پایانی و ایجاد تعهد برای جلسه بعد
```

---

## 📚 Standard Supported Clinical Presets

The skill comes pre-loaded with evidence-based frameworks adhering to standard clinical manuals:

1. **`act` (Acceptance & Commitment Therapy - هیز و استروسال)**:
   - 8 or 10 sessions focusing on the Hexaflex: Creative Hopelessness $\to$ Defusion $\to$ Present Moment & Mindfulness $\to$ Self-as-Context $\to$ Values Clarification $\to$ Committed Action.
2. **`cbt` (Cognitive Behavioral Therapy - بک و هائوتون)**:
   - 8 to 12 sessions: Cognitive Conceptualization $\to$ Identifying Automatic Thoughts $\to$ Cognitive Distortions $\to$ Evidence Gathering $\to$ Behavioral Activation $\to$ Core Beliefs Modification $\to$ Relapse Prevention.
3. **`schema` (Schema Therapy - جفری یانگ)**:
   - 10 to 12 sessions: Schema Assessment & Education $\to$ Schema Modes (Vulnerable Child, Punitive Parent) $\to$ Experiential Techniques (Imagery Rescripting) $\to$ Chair Dialogue $\to$ Healthy Adult Strengthening.
4. **`cft` (Compassion-Focused Therapy - پاول گیلبرت)**:
   - 8 to 10 sessions: Three Affect Regulation Systems (Threat, Drive, Soothing) $\to$ Evolution of the Tricky Brain $\to$ Compassionate Mind Training (CMT) $\to$ Developing the Compassionate Self $\to$ Addressing Shame and Self-Criticism.
5. **`mbsr` (Mindfulness-Based Stress Reduction - کابات‌زین)**:
   - 8 sessions: Automatic Pilot $\to$ Body Scan Meditation $\to$ Mindful Breathing & Movement $\to$ Stress Appraisal $\to$ Responding vs. Reacting $\to$ Interpersonal Mindfulness $\to$ Daily Practice Integration.
6. **`positive` (Positive Psychotherapy - سلیگمن و رشید)**:
   - 8 to 10 sessions: Signature Strengths (VIA) $\to$ Gratitude Visit $\to$ Forgiveness $\to$ Savoring Positive Experiences $\to$ Optimism $\to$ Hope & Meaning in Life.
7. **`mindful_parenting` (فرزندپروری مبتنی بر ذهن‌آگاهی - بوگلز)**:
   - 8 sessions: Parental Reactivity $\to$ Mindful Listening $\to$ Acceptance of the Child $\to$ Rupture & Repair in Attachment $\to$ Self-Compassion for Parents.

---

## 🛠️ CLI Engine Usage

The skill provides [`compile_intervention_protocol.py`](scripts/compile_intervention_protocol.py) for compiling protocols:

```bash
# 1. Generate an ACT protocol for chronic pain patients using the built-in preset
python3 .agents/skills/psychological-intervention-protocol-builder/scripts/compile_intervention_protocol.py \
  --preset act \
  --target-population "بیماران مبتلا به درد مزمن عضلانی-اسکلتی" \
  --sessions 8 \
  --duration 90 \
  --output-docx "پروتکل_مداخله_اکت_درد_مزمن.docx" \
  --output-json "protocol_act.json"

# 2. Generate a custom protocol from a structured JSON schema
python3 .agents/skills/psychological-intervention-protocol-builder/scripts/compile_intervention_protocol.py \
  --json "custom_protocol_payload.json" \
  --output-docx "پروتکل_مداخله_سفارشی.docx" \
  --output-json "protocol_summary.json"
```

---

## 📐 The Method Triad (چارچوب سه‌گانه روش‌شناختی فنون و جلسات)

Inspired by Prof. Sida Peng's research defense standards, every intervention session and key experiential technique must be defensible against hostile examiner cross-examination via the **Method Triad**:
1. **Motivation (چرایی و ضرورت نظری)**: Why this specific technique or session theme is essential; what psychological vulnerability, avoidance mechanism, or pathology it targets.
2. **Design (چیستی و طراحی عملیاتی)**: Step-by-step procedure of how the technique, metaphor, or in-session exercise is executed and internalized by participants.
3. **Advantage (برتری فنی و مزیت رقابتی)**: Explicit academic justification of why this approach outperforms traditional or alternative techniques (e.g. why ACT acceptance surpasses thought suppression, or why imagery rescripting outperforms verbal disputation).

The compiler script automatically highlights these triads in:
- **Chapter 3 Summary Table**: Condensed comparative advantages in the techniques column.
- **Appendix Manual**: Formatted dual-tone callout boxes detailing Motivation, Design, and Advantage.

---

## 📄 OpenXML Formatting & Typography Standards

When generating the `.docx` manual:
- **Title & Headers**: `B Titr` 16 pt Bold for session titles; `B Titr` 12 pt for phase headers.
- **Body Text**: `B Nazanin` 13 pt Regular, Line Spacing 1.25, Justified.
- **Visual Callouts (کادرهای ویژه)**:
  - Clinical Metaphors and Experiential Exercises are wrapped in light gray/blue container callouts with subtle borders (`#E2E8F0`) and internal margins.
  - Method Triad containers feature a distinct violet/indigo border (`#4F46E5`) with multi-point structured fields.
- **Directionality**: Enforces `<w:bidi w:val="1"/>` on every paragraph and `<w:bidiVisual/>` on all table elements.
