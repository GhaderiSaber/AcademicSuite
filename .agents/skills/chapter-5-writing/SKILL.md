---
name: chapter-5-writing
description: End-to-end orchestration for Chapter 5 discussion, enforcing One-Hypothesis-One-Stage micro-stages, 4-element psychological model, Triad Artifact Invariant (.docx, .md, .json), and article text enrichment without verbatim copying.
---

# Chapter 5 Writing Skill (تدوین فصل پنجم بحث و نتیجه‌گیری)

Orchestrates the Chapter 5 micro-stage discussion pipeline:
- Ingests empirical findings (`stats_results.json`) and parsed article evidence cards (`article_enrichment_cards.json`).
- Enforces One-Hypothesis-One-Stage deep discussion using the 4-Element Psychological Model (Verdict $\to$ Article Concordance $\to$ Mechanisms $\to$ Nuances).
- **Chapter 5 Prose-Only Invariant**: Chapter 5 must strictly contain **zero tables** (`|---|` or Word `<w:tbl>`). It is 100% continuous narrative prose. Tables belong exclusively to Chapter 4.
- **Academic Sobriety & Anti-Hyperbole**: Maintain strict academic sobriety and neutral prose. Zero tolerance for emotional padding, dramatic rhetoric, or hyperbolic adjectives/adverbs to inflate word counts.
- The agent produces the scholarly Persian narrative dynamically without prewritten templates or canned text.
- Compiles the synchronized Triad Artifact Invariant (`.docx` + `.md` + `.json`).
- Assembles verified stages into the final `Chapter_5_Discussion.docx` and `Chapter_5_Discussion.md`.

## CLI Execution

```bash
# 1. Parse Reference Articles for Evidence Cards
python3 .agents/skills/persian-discussion-builder/scripts/article_enrichment_engine.py \
  --papers-dir 04_references_and_lit/papers/ \
  --out-file academic-state/data/article_enrichment_cards.json

# 2. Compile Agent-Authored Triad for Stage 5.2.1
python3 .agents/skills/persian-discussion-builder/scripts/scaffold_chapter5_triad.py \
  --stage "02_hypothesis_discussion" \
  --base "02_hypothesis_1_discussion" \
  --outdir "03_deliverables/stage_02_hypo_1" \
  --title "بحث و بررسی فرضیه اول پژوهش" \
  --narrative-file "03_deliverables/stage_02_hypo_1/draft.md" \
  --articles "academic-state/data/article_enrichment_cards.json"

# 3. Assemble Verified Stages into Final Chapter 5 Deliverables
python3 .agents/skills/persian-discussion-builder/scripts/assemble_chapter5.py \
  --stages-dir 03_deliverables/ \
  --out-dir 03_deliverables/
```

## 🧠 Active Learned Behavioral Invariants
- **Lesson (LSN-2026-ACADEMIC-SOBRIETY-AND-ANTI-HYPERBOLE-001)**: Maintain strict academic sobriety and neutral academic prose. Do not use emotional, dramatic, or hyperbolic wording to inflate word counts. [Enforcement: academic_writer_guard.py]
- **Lesson (LSN-2026-EXHAUSTIVE-FOOTNOTE-TOKENIZATION-AND-PARITY-QC-001)**: Exhaustive loop tokenization for all footnote markers [^X] in text nodes; assert zero literal '[^' substrings in document.xml and 1:1 parity between footnoteReference tags and definitions. [Enforcement: academic_writer_guard.py]
- **Lesson (LSN-2026-CHAPTER-5-PROSE-ONLY-INVARIANT-001)**: Enforce a rigid Chapter 5 Prose-Only Invariant: generate zero tables in Chapter 5. Tables belong exclusively to Chapter 4. [Enforcement: academic_writer_guard.py]