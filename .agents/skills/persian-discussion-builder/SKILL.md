---
name: persian-discussion-builder
description: >-
  Expert Chapter 5 (بحث و نتیجه‌گیری / Discussion & Conclusion) synthesis and drafting skill for psychology,
  counseling, and behavioral sciences graduate theses. Ingests Chapter 4 statistical findings (stats_results.json),
  evaluates confirmed/rejected hypotheses, compares results against Iranian and foreign empirical literature,
  provides in-depth psychological and theoretical mechanisms (Beck, Bandura, Gross, Bowlby, Mindfulness),
  and generates defense-ready Word (.docx) documents complete with clinical implications, methodological limitations,
  and research recommendations.
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
- Read [discussion_framework_guide.md](file:///Users/saber/Desktop/AntigravitySkills/.agents/skills/persian-discussion-builder/references/discussion_framework_guide.md) for structural rules and standard Persian academic phrasing.
- Read [psychology_theoretical_mechanisms.md](file:///Users/saber/Desktop/AntigravitySkills/.agents/skills/persian-discussion-builder/references/psychology_theoretical_mechanisms.md) for ready-to-use psychological explanations across CBT, Emotion Regulation, Attachment, Mindfulness, and Self-Efficacy.

---

## 4. Execution Workflow

1. **Review Chapter 4 Results**:
   Inspect `stats_results.json` or `فصل چهارم: یافته‌های پژوهش.docx` to identify confirmed and rejected hypotheses, test statistics ($F, t, \beta, \eta_p^2, R^2$), and effect sizes.
2. **Review Chapter 2 Literature**:
   Identify the primary domestic and foreign researchers cited in Chapter 2 for each construct.
3. **Formulate Discussion Content JSON**:
   Prepare a structured JSON file mapping each hypothesis, its empirical comparisons, theoretical explanations, implications, and limitations.
4. **Generate Word Document**:
   Execute the document generation script:
   ```bash
   python3 .agents/skills/persian-discussion-builder/scripts/generate_chapter5_docx.py \
     --json "chapter5_input.json" \
     --out "فصل پنجم: بحث و نتیجه‌گیری.docx"
   ```
5. **Quality Review**:
   Ensure Persian half-spaces (نیم‌فاصله) are preserved, font styles match university templates (*B Titr* 14–18 pt Bold, *B Nazanin* 13 pt Regular, Line spacing 1.25), and OpenXML RTL tags are set.
