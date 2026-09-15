# Automated Quality Assurance & Quality Score Rubric

Every academic presentation compiled by the Persian Defense Presentation Builder must achieve a score of $\ge 90/100$ before release.

---

## 1. Quality Score Breakdown (100 Points)

### A. Research Fidelity (25 Points)
- Exact statistical reporting ($M, SD, t, F, p, \beta, R^2$).
- Zero whole-integer fabrication; natural empirical noise.
- Correct variable names and measurement instruments.
- Direct alignment with source dissertation chapters.

### B. Narrative Quality & Ghost Deck Discipline (20 Points)
- Action-titles answering "So what?" on every substantive slide.
- Prohibit generic category titles («بیان مسئله»، «یافته‌ها») as primary headers.
- Logical epistemic sequence and transition fluidity.

### C. Visual Communication & Layout Variety (20 Points)
- No two consecutive slides share the same layout family.
- Generic cards comprise $\le 25\%$ of slides; max single layout dominance $\le 30\%$.
- Purposeful visual encoding (flows for process, spotlights for KPIs, tables only for lookup).

### D. Typography & Persian BiDi Standards (15 Points)
- Triple direction controllers enforced (container, paragraph, run).
- Dual-slot font binding: `B Titr` / `B Nazanin` for Persian; `Times New Roman` for Latin stats.
- Standard dot decimal format (`۰.۰۰۱`, `۰.۰۵`).
- Mandatory preservation of leading zero in Persian (`۰.۰۰۱`, never `.۰۰۱`).
- Left-side minus sign invariant ($-0.32$, never $0.32-$).

### E. Visual Consistency & Clean Geometry (10 Points)
- Strict 16:9 widescreen layout grid.
- Zero element overlap or text frame collisions ($> 0.04$ in vertical separation).
- Coherent academic color palette with WCAG AAA contrast.

### F. Technical Integrity (10 Points)
- Valid OpenXML PowerPoint (`.pptx`) structure.
- 100% substantive slides have rich, colloquial Persian candidate speaker notes.
- Automatic transitions (Fade 0.5s) and automatic sequence entrance animations.

---

## 2. Hard Disqualification Rules
An automatic score of **0** is assigned if:
1. Any empirical finding or statistical value is hallucinated.
2. English words or card category titles appear in Persian deliverables.
3. Emojis appear on any academic presentation slide.
4. Severe overlapping or unreadable clipped text exists.
