---
name: ai-academic-tone-polisher
description: Master academic tone polisher, syntactic burstiness optimizer, and anti-AI detection refiner for graduate theses, dissertations, and peer-reviewed journal articles. Eliminates robotic LLM translationese and repetitive cliches (شایان ذکر است که، در این راستا، delve into), elevates sentence length variance (Burstiness CV >= 0.50) to authentic human scholarly standards, and enforces official Persian orthography (نیم‌فاصله) while strictly preserving APA 7 in-text citations and statistical formulas. Exports defense-ready Word reports (.docx), 300-DPI dual-panel diagnostic plots (.png), and 4-sheet Excel audit matrices (.xlsx).
---

# `ai-academic-tone-polisher` — Academic Tone Polisher & Anti-AI Refiner (Skill #22)

`ai-academic-tone-polisher` is the specialized stylistic humanization and anti-AI detection mitigation engine of the **AcademicSuite**. It analyzes graduate thesis chapters (Chapter 1 Introduction, Chapter 2 Theoretical Foundations, Chapter 5 Discussion) and peer-reviewed journal articles in Persian and English to eliminate robotic generative AI markers and restore authentic scholarly eloquence.

---

## 1. When to Activate This Skill

Activate this skill whenever:
- The user asks to **humanize AI-generated text** or **refine academic tone** (بازنویسی به لحن اصیل دانشگاهی و انسان‌محور).
- The user is concerned about **AI text detectors** (Turnitin AI, GPTZero, SamimNoor / همانندجو, CopyLeaks).
- The text exhibits **monotonous sentence cadence** (low burstiness: all sentences are 18–22 words).
- The text contains **robotic AI cliches** in Persian (*«شایان ذکر است که»*, *«در این راستا»*, *«به طور کلی می‌توان گفت که»*, *«این امر نشان‌دهنده آن است که»*, *«همان‌طور که می‌دانیم»*) or English (*"delve into"*, *"multifaceted tapestry"*, *"testament to"*, *"plays a crucial role"*).
- The user requests **orthographic and half-space cleanup** (نیم‌فاصله) for Persian verbs (*می‌/نمی‌*), plurals (*ها/های*), and comparatives (*تر/ترین*).
- The user needs to polish a section while **strictly guaranteeing zero alteration** of APA 7 in-text citations (`(Beck et al., 2020)`, `بک و همکاران، ۱۳۹۹`) and statistical parameter formulas ($F(1, 58) = 14.25, p < .001$).

---

## 2. Theoretical & Metric Benchmarks

1. **Sentence Cadence / Burstiness ($CV_{len}$)**:
   - Evaluates sentence length variance: $CV_{len} = \sigma_{len} / \mu_{len}$.
   - $CV_{len} < 0.35$: Severe robotic homogeneity (Triggers AI detection).
   - $CV_{len} \ge 0.50$: Authentic scholarly cadence (Alternating between crisp thesis statements and complex analytical multi-clause syntheses).
2. **AI Predictability / Uniformity Footprint ($S_{ai} \in [0, 100\%]$)**:
   - Composite penalty based on detected robotic markers per sentence, low burstiness, and Type-Token Ratio (TTR).
   - Target post-polishing threshold: $\mathbf{S_{ai} < 25\%}$.
3. **Stanford SciWrite 5-Pass Editorial Engine (Dr. Kristin Sainani Methodology)**:
   - **Pass 1: Clutter Extraction**: Direct removal of dead-weight phrases (*due to the fact that* $\to$ *because*, *شایان ذکر است که* $\to$ حذف) and empty throat-clearing.
   - **Pass 2: Active Voice & Nominalization Resurrection**: Converting smothered verbs (*provides a review of* $\to$ *reviews*, *مورد بررسی قرار داد* $\to$ *بررسی کرد*) to vigorous direct verbs.
   - **Pass 3: Sentence Architecture & Buried Predicates**: Auditing distance between subject and verb (alert if $>12$ words in EN or $>20$ words in FA) to optimize cognitive ergonomics.
   - **Pass 4: Keyword Consistency ("The Banana Rule")**: Strictly preventing synonym variation for defined psychometric constructs (*Social Anxiety* must never drift to *Social Phobia* without declaration).
   - **Pass 5: Numerical & Citation Integrity**: Cross-checking sample sizes and auditing secondary citations ("The Telephone Game").
4. **Lexical Diversity**:
   - Type-Token Ratio (TTR) and vocabulary enrichment replacing conversational verbs with disciplinary psychological nomenclature.

---

## 3. CLI Command Reference

### Standard Persian Text Polishing with SciWrite 5-Pass Engine:
```bash
python3 .agents/skills/ai-academic-tone-polisher/scripts/tone_polisher_engine.py \
  --json .agents/skills/ai-academic-tone-polisher/examples/sample_ai_text_payload.json \
  --sample persian_draft \
  --out-dir "./academic_tone_output" \
  --lang fa \
  --intensity moderate
```

### Interactive Paragraph-by-Paragraph Review Mode:
```bash
python3 .agents/skills/ai-academic-tone-polisher/scripts/tone_polisher_engine.py \
  --text "شایان ذکر است که این مداخله نقش بسیار مهمی ایفا می‌کند (Beck et al., 2020)." \
  --mode interactive \
  --lang fa
```

### English Targeted SciWrite Pass Review:
```bash
python3 .agents/skills/ai-academic-tone-polisher/scripts/tone_polisher_engine.py \
  --file manuscript_intro.txt \
  --mode targeted \
  --target-pass verbs \
  --lang en
```

---

## 4. Multi-Modal Deliverables Generated

1. **`متن_ویراسته_و_دانشگاهی.docx` / `Polished_Academic_Manuscript.docx`**:
   - Native Right-to-Left OpenXML BiDi document with *B Titr*, *B Nazanin*, and *Times New Roman*.
   - **Section 1**: Executive Anti-AI & Stylistic Scorecard (Pre vs. Post comparison table).
   - **Section 2**: Clean Polished Academic Text (Defense-ready with APA paragraph indents).
   - **Section 3**: Side-by-Side Sentence Transformation Audit (Original vs. Polished with linguistic rationale).
   - **Section 4**: Stanford SciWrite 5-Pass Editorial Report (Top 5 Priority Revisions + Pass-by-Pass breakdown).
2. **`tone_burstiness_plot.png` (300 DPI)**:
   - Dual-panel diagnostic figure:
     - Left Panel: Sentence length histogram comparing narrow AI distribution vs. wide human scholarly distribution.
     - Right Panel: Comparative bar chart of Burstiness, AI Predictability, and Cliche Count.
3. **`academic_tone_audit_matrix.xlsx`**:
   - 5 dedicated sheets:
     - `Executive Scorecard`: Key before/after indices and triage verdict.
     - `Sentence Audit`: Sentence-by-sentence comparison, lengths, and syntactic explanations.
     - `AI Marker Catalog`: Flagged cliches, frequencies, and authentic academic replacements.
     - `SciWrite 5-Pass Review`: Pass-by-pass findings, severity tags (`CRITICAL`, `MAJOR`, `MINOR`), and editorial rationale.
     - `Lexical Diversity`: Type-Token metrics.
4. **`tone_polish_results.json`**:
   - Complete machine-readable data ledger.
