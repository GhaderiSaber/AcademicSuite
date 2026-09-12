---
name: ai-academic-tone-polisher
description: Master academic tone polisher, syntactic burstiness optimizer, and anti-AI detection refiner for graduate theses, dissertations, and peer-reviewed journal articles. Eliminates robotic LLM translationese and repetitive cliches (شایان ذکر است که، در این راستا، delve into), elevates sentence length variance (Burstiness CV >= 0.65-0.70) to authentic human scholarly standards, breaks macro-level section templates, and enforces official Persian orthography (نیم‌فاصله) while strictly preserving APA 7 in-text citations and Word OMML statistical formulas. Features offline diagnostic risk linter (lint_ai_risk.py), invariant entity masker (mask_invariants.py), and cadence balancer (cadence_inverter.py).
---

# `ai-academic-tone-polisher` — Dual-Mode Academic Tone & Anti-AI Refiner (Skill #22)

`ai-academic-tone-polisher` is the specialized stylistic humanization and anti-AI detection mitigation engine of the **AcademicSuite**. It analyzes graduate thesis chapters (Chapter 1 Introduction, Chapter 2 Theoretical Foundations, Chapter 3 Methods, Chapter 4 Results, Chapter 5 Discussion) and peer-reviewed journal articles in Persian and English to eliminate robotic generative AI markers, break section-level template repetitions, and restore authentic scholarly eloquence.

---

## 1. When to Activate This Skill

Activate this skill whenever:
- The user asks to **audit or humanize AI-generated text** or **refine academic tone** (بازنویسی به لحن اصیل دانشگاهی و انسان‌محور).
- The user is concerned about **AI text detectors** (QuillBot, Turnitin AI, GPTZero, SamimNoor / همانندجو, CopyLeaks).
- The text exhibits **monotonous sentence cadence** (low burstiness: $CV < 0.50$, all sentences are 18–24 words).
- The text contains **conversational rhetorical questions** (*"Why do two students...?"*, *"How does self-compassion...?"*).
- The text contains **rigid ordinal enumerations** (*"First,... Second,... Third,... Finally,..."*).
- The text exhibits **section template repetition** (identical structure repeated across measures, results, or limitations).
- The text contains **robotic AI cliches** in Persian (*«شایان ذکر است که»*, *«در این راستا»*, *«به طور کلی می‌توان گفت که»*) or English (*"delve into"*, *"multifaceted tapestry"*, *"testament to"*, *"plays a crucial role"*).
- The user needs to polish a section while **strictly guaranteeing zero alteration** of APA 7 in-text citations (`(Beck et al., 2020)`, `بک و همکاران، ۱۳۹۹`) and Word OMML statistical parameter formulas ($F(1, 58) = 14.25, p < .001$).

---

## 2. Theoretical & Metric Benchmarks

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                       CALIBRATION BENCHMARK TARGETS                         │
├─────────────────────────┬───────────────────────────────────────────────────┤
│ Sentence Burstiness     │ CV = σ / μ >= 0.65 - 0.70                         │
│ (Sentence Cadence)      │ (Alternates staccato claims with periodic clauses)│
├─────────────────────────┼───────────────────────────────────────────────────┤
│ Generic Transitions     │ <= 10.0% of total sentences                       │
│ (Signpost Density)      │ (Bans excessive Moreover, Furthermore, Notably)   │
├─────────────────────────┼───────────────────────────────────────────────────┤
│ Rhetorical Questions    │ Exactly 0 in empirical/literature text            │
├─────────────────────────┼───────────────────────────────────────────────────┤
│ Ordinal Lists           │ <= 1 isolated instance (No First, Second, Third)  │
├─────────────────────────┼───────────────────────────────────────────────────┤
│ AI Cliche Footprint     │ 0 cataloged clichés from the 38-pattern catalog   │
├─────────────────────────┼───────────────────────────────────────────────────┤
│ Invariant Preservation  │ 100% exact match for APA 7 citations & OMML math  │
└─────────────────────────┴───────────────────────────────────────────────────┘
```

---

## 3. The 3 Core Deterministic Scripts

All diagnostic and mathematical tasks run outside the LLM in deterministic Python:

### 1. Pre-Flight Diagnostic Scanner (`lint_ai_risk.py`)
Evaluates text and outputs an immediate audit report with risk score and editorial grade:
```bash
# Audit a draft manuscript file:
python3 .agents/skills/ai-academic-tone-polisher/scripts/lint_ai_risk.py --file scripts/polish_article_human.py

# Export machine-readable JSON report:
python3 .agents/skills/ai-academic-tone-polisher/scripts/lint_ai_risk.py --file manuscript.txt --out lint_report.json
```

### 2. Invariant Masking Engine (`mask_invariants.py`)
Replaces APA 7 citations and statistical formulas with unique tokens (`__CIT_001__`, `__STAT_001__`) before any rewriting pass and restores them verbatim afterward:
```python
from mask_invariants import mask_invariants, unmask_invariants, audit_masking_fidelity

masked_text, mask_dict = mask_invariants(raw_draft)
# ... apply humanization rewriting pass ...
final_text = unmask_invariants(rewritten_text, mask_dict)
is_valid, missing = audit_masking_fidelity(raw_draft, final_text, mask_dict)
assert is_valid, f"Missing entities: {missing}"
```

### 3. Cadence & Burstiness Inverter (`cadence_inverter.py`)
Diagnoses paragraph rhythm and tests sentence length restructuring to ensure target $CV \ge 0.70$:
```python
from cadence_inverter import diagnose_paragraph_cadence, simulate_cadence_after_edit

diag = diagnose_paragraph_cadence(paragraph_text)
# Provides recommendations on periodic fusion (—, ;) vs staccato assertions
```

---

## 4. Multi-Agent Orchestration Protocol (Rule 12 & Rule 13)

When humanizing or writing an academic article, the existing agents execute in sequence:

```text
                               [User Request]
                                      │
                                      ▼
                               [digital-saber]
                                      │
               ┌──────────────────────┴──────────────────────┐
               ▼                                             ▼
       [results-auditor]                             [academic-writer]
      Runs lint_ai_risk.py                        Applies De-templating
  (Pre-flight Risk Assessment)                   & Cadence Inversion Rules
               │                                             │
               │  High Risk Detected?                        │
               └──────────────────► [Rewrites] ◄─────────────┘
                                           │
                                           ▼
                                   [results-auditor]
                               (Blind Verification Pass)
                                           │
                                           ▼
                                [final-judge & Delivery]
                              0% QuillBot / Turnitin Risk
```

1. **Step 1: Pre-flight Audit**: `results-auditor` executes `lint_ai_risk.py`. If Composite Risk Score $\le 20\%$, the text passes immediately without editing.
2. **Step 2: Entity Masking**: Run `mask_invariants.py` to lock all citations and math.
3. **Step 3: Surgical In-Place Rewriting**: `academic-writer` consults [section_de_templating_guide.md](file:///Users/saber/Desktop/academic_suite/.agents/skills/ai-academic-tone-polisher/references/section_de_templating_guide.md) to restructure flagged sentences, eliminate rhetorical questions, and drive $CV \ge 0.70$.
4. **Step 4: Unmasking & Verification**: Restore masked entities. `results-auditor` re-runs `lint_ai_risk.py` to confirm the text achieves Grade A+ with zero corruptions.

---

## 5. Reference Knowledge Base

- [detection_heuristics.md](file:///Users/saber/Desktop/academic_suite/.agents/skills/ai-academic-tone-polisher/references/detection_heuristics.md) — Mathematical mechanics of QuillBot, Turnitin, and GPTZero.
- [ai_slop_and_cliche_catalog.md](file:///Users/saber/Desktop/academic_suite/.agents/skills/ai-academic-tone-polisher/references/ai_slop_and_cliche_catalog.md) — 38 synthetic academic markers and human scholarly alternatives.
- [section_de_templating_guide.md](file:///Users/saber/Desktop/academic_suite/.agents/skills/ai-academic-tone-polisher/references/section_de_templating_guide.md) — Step-by-step methods for de-templating Methods, Results, and Discussion.
- [academic_tone_and_humanization_standards.md](file:///Users/saber/Desktop/academic_suite/.agents/skills/ai-academic-tone-polisher/references/academic_tone_and_humanization_standards.md) — Stanford SciWrite 5-pass editorial framework and Persian orthography (نیم‌فاصله).
