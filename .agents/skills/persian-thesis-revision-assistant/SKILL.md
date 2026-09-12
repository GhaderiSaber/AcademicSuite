---
name: persian-thesis-revision-assistant
description: >-
  Specialized skill for reviewing, resolving, and applying supervisor and defense examiner comments on Iranian
  graduate theses, dissertations, and proposals. Extracts Word (.docx) track changes and margin annotations,
  triages feedback into formatting, statistical, and theoretical categories, coordinates targeted chapter edits,
  and compiles the mandatory formal Point-by-Point Response Table (جدول پاسخ به نظرات استاد راهنما و داوران)
  in polished academic Persian.
---

# Persian Thesis Supervisor Revision Assistant Skill (مدیریت و اعمال اصلاحات اساتید و داوران)

This skill guides the agent in navigating the high-stakes **thesis revision and defense correction cycle (اصلاحات پس از بازبینی استاد راهنما یا جلسه دفاع)** for Iranian master's and doctoral dissertations.

It automates comment extraction from Word documents (`.docx`), plans required text and statistical patches, ensures courteous academic rebuttal etiquette, and produces the official **Point-by-Point Response Table (`جدول_پاسخ_به_نظرات_اساتید.docx`)** required by university graduate councils for final thesis sign-off.

---

## 1. When to Activate This Skill

Activate this skill when:
1. The student receives a reviewed thesis draft or proposal from their supervisor (استاد راهنما), advisor (استاد مشاور), or defense jury (داوران) containing comments, margin notes, or tracked changes.
2. The user needs to extract and list all comments embedded in a Word document (`.docx`).
3. The user needs to draft formal, polite, and academically grounded responses to each professor's comment.
4. The user needs to compile the official **جدول پاسخ به نظرات داوران و استاد راهنما**.
5. Revisions need to be coordinated across specific chapters (e.g., updating Chapter 4 stats and Chapter 5 discussion simultaneously).

---

## 2. The 4-Stage Revision Lifecycle

```
[Supervisor Word (.docx) or Email Feedback]
                     │
                     ▼
       [Stage 1: Comment Ingestion]
       - python3 extract_docx_comments.py --file thesis_reviewed.docx
                     │
                     ▼
       [Stage 2: 3-Tier Triage]
       ├── Tier 1: Format & Typography (نیم‌فاصله، جداول APA، ارجاعات)
       ├── Tier 2: Statistics & Methodology (آزمون مفروضه، تحلیل کمکی)
       └── Tier 3: Theory & Discussion (پیشینه جدید، تبیین‌های تکمیلی)
                     │
                     ▼
       [Stage 3: Chapter Remediation]
       - Apply edits to Chapter 1, 2, 3, 4, or 5
       - Cross-reference with other skills (e.g., statistical-data-analyst)
                     │
                     ▼
       [Stage 4: Response Table Compilation]
       - Formulate polite academic rebuttals (academic_rebuttal_etiquette_fa.md)
       - python3 generate_revision_response_docx.py --json resolved_comments.json
```

---

## 3. Step-by-Step Instructions

### Step 1: Extract Comments
If the feedback is in a Word document (`.docx`):
```bash
python3 .agents/skills/persian-thesis-revision-assistant/scripts/extract_docx_comments.py \
  --file "path/to/reviewed_thesis.docx" \
  --out "supervisor_comments.json"
```
If the feedback was sent as an email, text list, or defense meeting minutes:
```bash
python3 .agents/skills/persian-thesis-revision-assistant/scripts/extract_docx_comments.py \
  --file "path/to/feedback.txt" \
  --out "supervisor_comments.json"
```

### Step 2: Categorize Comments by Domain
Review each extracted comment and tag it:
- **FORMAT**: Issues with margins, fonts, APA 7 table lines, Persian half-spaces (`\u200c`), Latin footnotes.
- **STATS**: Requests for assumption tests (Shapiro-Wilk, Levene), effect sizes ($\eta_p^2$, Cohen's $d$), ANCOVA slope checks, or mediation bootstrap CIs.
  *Delegate to*: `statistical-data-analyst`.
- **THEORY**: Requests for newer 2024–2026 literature, conceptual clarification, or deeper psychological explanations.
  *Delegate to*: `persian-discussion-builder` or `persian-academic-translation`.

### Step 3: Apply Corrections to Thesis Files
- Edit the corresponding chapter file directly.
- Note the exact **page number, section, and paragraph** where the change was introduced.

### Step 4: Draft Polite Academic Responses
In `resolved_comments.json`, fill out `action_taken` and `location` for every comment using the courteous academic templates in [academic_rebuttal_etiquette_fa.md](file:///Users/saber/Desktop/academic_suite/.agents/skills/persian-thesis-revision-assistant/references/academic_rebuttal_etiquette_fa.md):
- Always express gratitude for the professor's insight.
- Clearly describe what was altered, added, or recalculated.
- State the exact page number.

### Step 5: Generate the Response Table Word Document
Compile the formal submission document:
```bash
python3 .agents/skills/persian-thesis-revision-assistant/scripts/generate_revision_response_docx.py \
  --json "resolved_comments.json" \
  --out "جدول_پاسخ_به_نظرات_استاد_راهنما_و_داوران.docx"
```

---

## 4. Final Submission Checklist

Before delivering the revised documents to the student or professor, review [comment_resolution_checklist.md](file:///Users/saber/Desktop/academic_suite/.agents/skills/persian-thesis-revision-assistant/references/comment_resolution_checklist.md):
- [ ] Every single comment has a row in the response table.
- [ ] Page numbers in the table match the final compiled thesis document.
- [ ] Any newly cited study in text is present in the references section.
- [ ] Tone is polite, professional, and academically substantiated.
