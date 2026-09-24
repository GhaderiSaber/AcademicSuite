---
name: persian-discussion-builder
description: Draft Chapter 5 (Discussion and Conclusion) synthesizing statistical
  findings, psychological mechanisms, literature concordance, implications, and limitations.
---

# Persian Discussion Builder Skill (فصل پنجم: بحث و نتیجه‌گیری)

This skill guides the agent in drafting a defense-ready, theoretically profound **Chapter 5 (بحث و نتیجه‌گیری / Discussion & Conclusion)** for graduate theses and dissertations in Psychology, Counseling, Educational Sciences, and Behavioral Health.

It connects the quantitative findings of Chapter 4 (`stats_results.json`) with the theoretical and empirical literature of Chapter 2, ensuring that every hypothesis is thoroughly explained at the psychological, cognitive, and systemic levels.

---

## 1. When to Activate This Skill

Activate this skill when:
1. The user asks to write **Chapter 5 (فصل پنجم)** or the **Discussion section (بخش بحث)** of a thesis, dissertation, or journal article.
2. Statistical results from Chapter 4 are available and need to be interpreted, compared with literature, and theoretically explained.
3. The user needs to draft research implications (پیامدهای بالینی و کاربردی), limitations (محدودیت‌ها), or future recommendations (پیشنهادها).

---

## 2. Standard 6-Part Chapter 5 Architecture

Chapter 5 must be structured strictly according to Iranian graduate university guidelines:

| Section | Title in Persian | Purpose & Content |
| :--- | :--- | :--- |
| **5-1** | **مقدمه** | Brief recap of research problem, objectives, target population, and chapter outline. |
| **5-2** | **بحث پیرامون یافته‌ها** | Hypothesis-by-hypothesis deep discussion using the **4-Element Psychological Model**. |
| **5-3** | **پیامدهای کاربردی و بالینی** | Practical implications for therapists, counselors, educators, clinics, or policymakers. |
| **5-4** | **محدودیت‌های پژوهش** | Honest methodological limitations (sampling, self-report instruments, lack of longitudinal follow-up). |
| **5-5** | **پیشنهادهای پژوهش** | Split strictly into: **A) پیشنهادهای پژوهشی** (for researchers) and **B) پیشنهادهای کاربردی** (for practitioners). |
| **5-6** | **نتیجه‌گیری نهایی** | Holistic concluding synthesis highlighting the unique scientific contribution of the study. |

### 2.1 Core Invariants for Chapter 5
- **Chapter 5 Prose-Only Invariant (اصل متن پیوسته بدون جدول)**: Chapter 5 must strictly contain **zero tables** (Markdown `|---|` or Word `<w:tbl>`). It is 100% continuous narrative prose, theoretical synthesis, and psychological mechanism explanation. All statistical and empirical tables belong exclusively in Chapter 4.
- **Strict Academic Sobriety & Anti-Hyperbole (اصل متانت علمی و پرهیز از اغراق)**: Maintain strictly objective, neutral, and sober academic prose. Zero tolerance for emotional padding, dramatic rhetoric, intense adjectives, or hyperbolic phrasing to inflate word counts or narrative volume.

---

## 3. The 4-Element Psychological Discussion Protocol

For each research hypothesis or question, the agent must synthesize the text using these 4 elements:

```
[Hypothesis Findings from Chapter 4]
                 │
                 ▼
┌────────────────────────────────────────────────────────┐
│ 1. Statistical Verdict (بیان فرضیه و یافته آماری)     │
│    State exact test statistic, p-value, effect size,   │
│    and whether confirmed or rejected.                  │
├────────────────────────────────────────────────────────┤
│ 2. Empirical Literature Comparison (مقایسه با پیشینه) │
│    Cite 3-5 domestic (Iranian) and foreign studies     │
│    that are aligned (همسو) or conflicting (ناهمسو).     │
├────────────────────────────────────────────────────────┤
│ 3. Psychological Mechanism Explanation (تبیین نظری)   │
│    Explain *why* and *how* at the cognitive, emotional,│
│    or behavioral level using established theories.     │
├────────────────────────────────────────────────────────┤
│ 4. Methodological Reasoning for Unexpected Findings    │
│    If non-significant, explain why (sample traits,     │
│    cultural context, self-report sensitivity).         │
└────────────────────────────────────────────────────────┘
```

### Reference Guides to Consult:
- Read [discussion_framework_guide.md](.agents/skills/persian-discussion-builder/references/discussion_framework_guide.md) for structural rules and standard Persian academic phrasing.
- Read [psychology_theoretical_mechanisms.md](.agents/skills/persian-discussion-builder/references/psychology_theoretical_mechanisms.md) for ready-to-use psychological explanations across CBT, Emotion Regulation, Attachment, Mindfulness, and Self-Efficacy.

---

## 4. Execution Workflow & Micro-Stage CLI Commands

Follow the 10-stage sequence from [MICRO_STAGE_SEQUENCES.md](../../references/MICRO_STAGE_SEQUENCES.md):

### Step 0: Ingest & Parse Reference Articles (PDF/DOCX/TXT)
Extract empirical findings, sample traits, and theoretical mechanisms from local papers into an enrichment corpus:
```bash
python3 .agents/skills/persian-discussion-builder/scripts/article_enrichment_engine.py \
  --papers-dir 04_references_and_lit/papers/ \
  --out-file academic-state/data/article_enrichment_cards.json
```

### Step 1: Scaffold Micro-Stage Triads (`.docx` + `.md` + `.json`)
For every micro-stage (Recap, Hypothesis $k$, Unexpected Findings, Implications, Limitations, Recommendations), scaffold the physical triad:
```bash
# Example: Stage 5.1 Recap
python3 .agents/skills/persian-discussion-builder/scripts/scaffold_chapter5_triad.py \
  --stage "01_findings_recap" \
  --base "01_findings_recap" \
  --outdir "03_deliverables/stage_01_recap" \
  --articles "academic-state/data/article_enrichment_cards.json"

# Example: Stage 5.2.1 Hypothesis 1 Discussion (with 4-element psychological model)
python3 .agents/skills/persian-discussion-builder/scripts/scaffold_chapter5_triad.py \
  --stage "02_hypothesis_discussion" \
  --base "02_hypothesis_1_discussion" \
  --outdir "03_deliverables/stage_02_hypo_1" \
  --keyword "burnout" \
  --articles "academic-state/data/article_enrichment_cards.json"
```

### Step 2: Assemble Verified Stages into Final Deliverables
Once all stage triads pass validation and human gate approval, assemble them into the master chapter:
```bash
python3 .agents/skills/persian-discussion-builder/scripts/assemble_chapter5.py \
  --stages-dir 03_deliverables/ \
  --out-dir 03_deliverables/
```

### Step 3: Quality Review & Epistemic Honesty
- **Anti-Plagiarism & Paraphrasing Invariant**: Synthesize and paraphrase concepts from parsed articles into authentic academic Persian with formal APA citations. Direct string copying of English or source text is prohibited.
- **Persian Typography**: Heading 1 in *B Titr* 14–16 pt Bold, body in *B Nazanin* 13 pt Regular, line spacing 1.25, OpenXML RTL `<w:bidi w:val="1"/>`.
- **Persian Number & Decimal Standards**: Standard dot (`.`) with mandatory leading zero (`۰.۰۰۱`, `۰.۰۵`, `۰.۸۵`). Exact 3 decimal places for $p$-values (`p < ۰.۰۰۱` یا `۰.۰۰۱ > p`).
- **Epistemic Honesty on Null Findings**: Candidly discuss non-significant findings without defensive rationalization.

## 🧠 Active Learned Behavioral Invariants
- **Principle (PRN-20260924-D1DAA0)**: Chapter 5 discussion must strictly contain zero tables and maintain 100% continuous narrative prose.
- **Lesson (LSN-2026-NATIVE-OPENXML-WORD-FOOTNOTES-001)**: Mandate automated zip verification in orchestrator gates to physically validate the presence of OpenXML native footnotes (word/footnotes.xml and <w:footnoteReference>) before approving .docx deliverables. Implement mandatory OpenXML footnote injection.
- **Lesson (LSN-2026-EXHAUSTIVE-HEADING-ALIGNMENT-AND-DOM-QC-001)**: 1) Apply universal right-alignment enforcement on ALL headings, titles, and captions (<w:jc w:val='right'/> + <w:bidi w:val='1'/>); 2) Perform per-paragraph DOM validation confirming that EVERY heading element has explicit <w:jc w:val='right'/>, strictly forbidding document-wide string containment checks.