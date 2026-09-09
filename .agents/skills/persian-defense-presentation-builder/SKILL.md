---
name: persian-defense-presentation-builder
version: 3.5.0
description: Build professional Persian academic thesis/dissertation defense PowerPoint decks in 16:9. Treat the presentation as a visual argument, not a document conversion. Features Ghost Deck Action-Titles, pure-Python OMML native math injection, 300-DPI Matplotlib diagram engine (Mediation/CONSORT/Timeline), element overlap & geometry collision auditor, template context extractor, and dual-mode interactive HTML + native PowerPoint generation with 100/100 automated QA compliance.
---

# Persian Defense Presentation Builder v3.5

## Mission

Create a Persian academic defense presentation that works in a real room with a speaker, a projector, and a faculty audience.

The deck must communicate the research argument quickly, show the strongest evidence visually, remain faithful to the source material, and be readable from the back of the room.

The presentation is **not** a thesis pasted into PowerPoint.

The presentation is **not** a collection of UI cards.

The presentation is **not** a design exercise that sacrifices statistical accuracy.

The output must be:

- source-grounded and academically faithful;
- visually structured around a clear research narrative;
- substantially more visual than textual;
- readable at presentation distance;
- typographically stable in Persian/RTL;
- visually varied without becoming stylistically inconsistent;
- editable in PowerPoint wherever practical;
- supported by useful Persian speaker notes;
- rendered and inspected before delivery;
- rejected and repaired when measurable or visible quality thresholds are violated.

---

# 0. PRIME DIRECTIVE

The system must solve this problem in this order:

```text
SOURCE
  ↓
RESEARCH TRUTH MODEL
  ↓
SLIDE STORY
  ↓
MESSAGE
  ↓
VISUAL ENCODING
  ↓
LAYOUT
  ↓
TYPOGRAPHY
  ↓
POWERPOINT
  ↓
RENDER
  ↓
VISUAL + STRUCTURAL QA
  ↓
REPAIR
  ↓
FINAL PPTX
```

Never reverse this order by starting with a favorite template and forcing the research into it.

The generator must be able to explain internally, for every slide:

> "What does the audience need to understand here, and what is the fastest visual way to communicate it?"

If that answer is not clear, the slide is not ready to render.

---

# 1. HARD NON-NEGOTIABLE RULES

## 1.1 One slide = one primary message

Every content slide must have one dominant takeaway.

Before rendering, create an internal record:

```json
{
  "slide_number": 12,
  "section": "یافته‌ها",
  "message": "اثر غیرمستقیم تروما از طریق دو میانجی معنادار است.",
  "evidence": ["table_24", "bootstrap_5000"],
  "visual_encoding": "mediation_diagram",
  "speaker_goal": "interpret rather than read",
  "priority": "high"
}
```

If a slide has two equally important messages, split it unless the relationship itself is the point.

## 1.2 The deck must be message-first, not component-first

Do not begin from:

- cards;
- rounded rectangles;
- generic 3-column grids;
- badge collections;
- repeated pills;
- arbitrary decorative panels.

Begin from the communication problem.

Choose the visual form that best communicates that problem.

## 1.3 Cards are not the default

A generic card/grid composition may be used only when cards are semantically appropriate.

Hard limit:

> No more than **25% of content slides** may use a generic card-grid layout as their primary visual structure.

A repeated card composition on consecutive slides is a QA failure unless the slides are explicitly designed as a comparison pair and the repeated structure is necessary.

Never use cards merely because the renderer already supports them.

## 1.4 Never use the same layout family twice in a row

Each content slide must belong to a layout family.

Do not use the same family on consecutive content slides.

Do not allow one family to dominate more than 30% of the deck.

Recommended families include:

1. Cover / title
2. Section divider
3. Big-idea statement
4. Problem funnel
5. Inverted pyramid
6. Cause → mechanism → outcome
7. Research-gap comparison
8. Before / after conceptual comparison
9. Conceptual / SEM path model
10. Research-process flow
11. Sample / participant flow
12. Instrument comparison
13. Timeline
14. Numeric result spotlight
15. KPI panel
16. Bar chart
17. Dot plot
18. Slope / comparison chart
19. Distribution / box / violin-style conceptual graphic where appropriate
20. Correlation / relationship visualization
21. Statistical result table
22. Hypothesis matrix
23. Mediation diagram
24. Discussion mechanism diagram
25. Implication map
26. Limitation / boundary map
27. Recommendation roadmap
28. Closing / Q&A

## 1.5 Never shrink text to make content fit

For a 16:9 defense deck, target minimums:

- slide title: 28–36 pt;
- section label: 14–18 pt;
- body text: 20–26 pt;
- chart labels: 16–20 pt;
- important number: 34–52 pt;
- table text: 17–20 pt where technically possible;
- footnote/source text: 13–15 pt maximum, used sparingly.

Hard rule:

> If content cannot fit at readable size, the slide must be rewritten, split, re-encoded, or simplified.

Never solve overflow by silently reducing body text to 12–14 pt.

## 1.6 Never invent research facts

Do not invent, estimate, normalize, or silently correct:

- sample size;
- means or standard deviations;
- p-values;
- effect sizes;
- confidence intervals;
- fit indices;
- coefficients;
- reliability values;
- citations;
- participant demographics;
- hypotheses;
- study design;
- theoretical claims;
- names of people or institutions;
- intervention content;
- dates.

If the source does not provide something, omit it or mark it as unavailable.

## 1.7 Never hard-code identity metadata

University, faculty, department, program, student, advisor, co-advisor, examiners, defense date, thesis title, degree, and footer information must come from the current source payload.

Never embed sample identities or fallback identities inside the renderer.

Bad:

```text
دانشگاه آزاد اسلامی واحد کاشان
مرضیه سینائی
```

Good:

```text
{meta.university}
{meta.author}
{meta.department}
{meta.advisor}
```

When a metadata field is absent, omit it.

Do not substitute data from a previous project.

## 1.8 Never silently fall back to sample data

If the source payload is missing, malformed, incomplete, or invalid:

1. stop compilation;
2. report the missing input;
3. do not generate a plausible unrelated presentation;
4. do not silently load a sample thesis.

Sample/demo payloads must only be used by an explicit demo command.

## 1.9 Never claim completion before QA

"PPTX created successfully" is not equivalent to "presentation complete".

The final status may be:

- `PASS`
- `PASS_WITH_WARNINGS`
- `FAIL`

Only `PASS` may be described as final.

---

# 2. SOURCE INGESTION

## 2.1 Accept source materials

Possible source inputs include:

- thesis/dissertation text;
- proposal;
- Word/PDF export;
- statistical tables;
- CSV/Excel result exports;
- SPSS/R/lavaan output;
- existing figures;
- researcher-provided notes;
- structured JSON payload.

## 2.2 Build a Research Truth Model

Before slide planning, normalize the source into an internal `research_truth_model`.

Minimum structure:

```json
{
  "meta": {
    "title": null,
    "author": null,
    "degree": null,
    "university": null,
    "faculty": null,
    "department": null,
    "advisor": null,
    "co_advisor": null,
    "examiner": null,
    "date": null
  },
  "problem": [],
  "significance": [],
  "gap": [],
  "objectives": [],
  "questions": [],
  "hypotheses": [],
  "theory": [],
  "variables": [],
  "design": {},
  "sample": {},
  "instruments": [],
  "procedure": [],
  "assumptions": [],
  "descriptives": [],
  "fit_indices": [],
  "direct_effects": [],
  "indirect_effects": [],
  "total_effects": [],
  "effect_sizes": [],
  "discussion_claims": [],
  "implications": [],
  "limitations": [],
  "recommendations": [],
  "references": []
}
```

## 2.3 Preserve provenance

Every displayed numeric value must have an internal provenance pointer.

Example:

```json
{
  "value": 0.456,
  "display": "β = 0.456",
  "unit": null,
  "source": "chapter4/table24/row3",
  "source_text": "مجموع اثرات غیرمستقیم مدل"
}
```

For derived values, record the derivation explicitly.

Never derive or recalculate a scientific value unless the user/source authorizes that operation and the derivation is mathematically unambiguous.

## 2.4 Maintain a statistics ledger

Create an internal ledger for:

- N;
- means;
- SD;
- min/max;
- skewness/kurtosis;
- reliability;
- beta coefficients;
- SE;
- z/t/F;
- p;
- confidence intervals;
- R²;
- χ²;
- df;
- χ²/df;
- RMSEA;
- CFI;
- TLI;
- GFI/AGFI;
- AIC/BIC;
- effect sizes;
- bootstrap settings.

The same statistic must not appear with contradictory values across slides.

---

# 3. CONTENT SAFETY AND ACADEMIC FIDELITY

## 3.1 Preserve source claims

Do not upgrade weak source wording into stronger causal claims.

For example:

- a cross-sectional correlation is not causal evidence;
- an association is not a treatment effect;
- statistical significance is not clinical significance;
- model fit is not proof of a theory;
- mediation in observational data does not automatically prove a causal mechanism.

When the source itself contains an overclaim, preserve the source wording only if it is explicitly presented as the author's claim; otherwise use academically cautious wording.

## 3.2 Do not fabricate references

Only show references that exist in the supplied material.

Never invent author names, years, journal titles, URLs, DOIs, or page numbers.

## 3.3 Avoid unnecessary text transcription

Do not copy long thesis paragraphs into slides.

Convert prose into:

- short statements;
- relationships;
- diagrams;
- quantitative highlights;
- comparisons;
- timelines;
- evidence summaries.

Retain important qualifiers in speaker notes when appropriate.

---

# 4. STORYBOARD BEFORE DESIGN

## 4.1 Determine narrative architecture

A normal defense should generally contain:

1. Opening / identity
2. Why this problem matters
3. What is missing in existing knowledge
4. What this study asks
5. Conceptual framework
6. How the study was conducted
7. Who/what was studied
8. Measurement / instruments
9. Model / analytic strategy
10. Model fit / prerequisites
11. Main findings
12. Hypothesis results
13. Mediation / mechanism results
14. Interpretation
15. Comparison with prior work
16. Practical implications
17. Limitations / boundaries
18. Recommendations
19. Closing / Q&A

Do not force every item into its own slide. Combine or split based on the research evidence.

## 4.2 Recommended slide count

Typical range:

- 18–26 slides for a conventional 20–30 minute defense;
- shorter when the thesis is narrow;
- longer only when the evidence genuinely requires it.

Never pad the presentation merely to hit a slide count.

## 4.3 Allocate visual weight to the findings

Recommended narrative weight:

- 10–15%: opening and orientation;
- 15–20%: problem, gap, objectives, hypotheses;
- 15–20%: framework and methodology;
- 30–40%: results and hypothesis testing;
- 15–20%: interpretation, implications, limitations, recommendations;
- 1 closing slide.

The results should normally have the highest visual prominence.

## 4.4 Storyboard schema

Each slide must have:

```json
{
  "id": "s14",
  "section": "یافته‌ها",
  "title": "اثرهای مستقیم مدل",
  "message": "تروما هم آگاهی هیجانی و هم احساس انسجام را به‌طور معنادار کاهش می‌دهد.",
  "evidence": ["direct_effects"],
  "visual_encoding": "coefficient_path_diagram",
  "layout_family": "path_diagram",
  "density": "medium",
  "priority": "high",
  "notes_goal": "interpret coefficients and direction"
}
```

## 4.5 Title is a communication device

Whenever appropriate, prefer conclusion-oriented titles over labels.

Weak:

`ضرایب مسیر`

Stronger:

`تروما بیشترین اثر منفی را بر احساس انسجام نشان داد`

However, do not convert neutral reporting slides into unjustified conclusions. The title must remain supported by the source.

---

# 5. VISUAL ENCODING RULES

Choose one primary encoding per slide.

## 5.1 Use diagrams for relationships

Use diagrams when the information expresses:

- cause/mechanism;
- mediation;
- sequence;
- hierarchy;
- process;
- conceptual model;
- decision flow.

Do not explain a relationship with a paragraph if a diagram can show it clearly.

## 5.2 Use charts for quantitative comparison

When the audience must compare numbers, prefer:

- bars;
- dots;
- slopes;
- lollipop-style marks;
- compact KPI comparisons;
- confidence-interval visuals when data exist.

Do not use decorative charts that add no analytical information.

## 5.3 Use tables only when exact lookup matters

A table is appropriate when the audience needs exact values or multiple statistical fields simultaneously.

A table is not appropriate merely because the source contains a table.

When a table is required:

- show only decision-relevant columns;
- highlight important rows;
- remove redundant words;
- avoid dense paragraph cells;
- use readable typography;
- split large tables across slides rather than shrinking them.

## 5.4 Use large-number result spotlights for key findings

For important statistics, prefer:

```text
β = 0.456
Total indirect effect

p < .001
95% CI excludes zero
```

with concise supporting interpretation.

Do not surround a single important number with unnecessary decorative cards.

## 5.5 Use comparison structures for research gaps

A gap slide should make the missing knowledge obvious.

Prefer:

```text
What prior studies show
        ↓
What remains missing
        ↓
What this study contributes
```

or a three-column comparison when the columns represent meaningful categories.

## 5.6 Use a process flow for methodology

Methodology usually reads better as:

```text
Population → Sampling → Measures → Data Collection → SEM → Bootstrap
```

than as six paragraphs.

## 5.7 Use explicit mediation diagrams for mediation

For mediation findings, the visual should clearly distinguish:

- predictor;
- mediator(s);
- outcome;
- direct path;
- indirect paths;
- coefficient values;
- significance where useful.

A mediation table may supplement the diagram, but should not replace it when the mechanism is the main story.

## 5.8 Visualize model fit as evidence, not decoration

For SEM fit indices, a compact evidence panel is acceptable:

```text
χ²/df     1.118    ✓
RMSEA     0.021    ✓
CFI       0.988    ✓
AGFI      0.905    ✓
```

The slide should also explain, in one line, what this means for the model.

Do not use gauges or fake speedometers unless specifically requested.

---

# 6. DESIGN SYSTEM

## 6.1 Overall aesthetic

Use a restrained scholarly editorial aesthetic:

- strong grid;
- generous whitespace;
- limited palette;
- clear typographic contrast;
- one primary accent color and optional secondary accent;
- simple geometric shapes;
- subtle borders;
- minimal shadows;
- no gratuitous gradients;
- no generic corporate clip art;
- no visual noise.

## 6.2 Color

Recommended:

- light neutral background OR deep neutral background;
- one research accent color;
- one semantic positive/negative pair for statistical direction;
- neutral grays for secondary information.

Do not use a rainbow palette.

Do not assign a different accent color to every card.

## 6.3 Repeated design anchors are allowed

Consistency should come from:

- typography;
- spacing;
- page geometry;
- footer system;
- section color cue;
- small chapter marker;
- recurring number style.

Consistency must not come from repeating the exact same content container layout.

## 6.4 Whitespace

Every slide must have intentional breathing room.

Do not fill empty space simply because it exists.

Do not create oversized blank regions that make a slide feel unfinished.

Aim for balanced visual mass, not maximum occupancy.

---

# 7. PERSIAN / RTL TYPOGRAPHY

## 7.1 RTL is structural

Persian is not correctly implemented by merely right-aligning Latin text.

Ensure:

- Persian paragraphs are RTL;
- alignment is context-appropriate;
- punctuation is visually stable;
- mixed Persian/English statistical expressions remain legible;
- numbers and Latin acronyms do not jump unpredictably;
- arrows preserve intended semantic direction;
- table columns have deliberate order;
- title blocks do not mirror incorrectly.

## 7.2 Mixed-language statistical notation

Examples such as:

`β = −0.50, p < .001`

should remain stable and readable.

Keep statistical notation in a consistent direction and isolate it from long Persian sentences when necessary.

## 7.3 Font strategy

Choose fonts that are actually available in the target environment.

Do not assume a Persian font exists merely because it is declared in XML.

Preferred strategy:

1. verify the intended Persian font is installed;
2. otherwise use a verified fallback;
3. render the deck;
4. inspect Persian shaping and line breaks;
5. fail QA if the fallback visibly damages readability.

Never bundle or expose font files as output artifacts unless explicitly requested and legally permitted.

---

# 8. SLIDE-SPECIFIC COMPOSITION RULES

## 8.1 Cover slide

Must include only essential identity:

- thesis title;
- author;
- degree/program;
- advisor(s) when available;
- institution;
- date.

Use one strong visual motif, not a collage of cards.

## 8.2 Problem slide

Prefer:

- one dominant problem statement;
- a visual funnel / causal chain;
- 2–4 concise evidence points.

Never place five long prose blocks across the slide.

## 8.3 Research gap slide

Show the contrast between:

- established knowledge;
- missing evidence;
- this study's contribution.

## 8.4 Conceptual model

The central model must be one of the largest objects on the slide.

Do not make the diagram tiny so that explanatory text can dominate.

For path models:

- use readable node labels;
- minimize line crossings;
- place coefficients next to their paths;
- keep directionality obvious;
- distinguish direct and indirect paths when needed.

## 8.5 Method slide

Use a process, timeline, or compact method map.

Use text only for details that cannot be encoded visually.

## 8.6 Sample slide

The sample size should be visually dominant.

Example structure:

```text
N = 256

Girls aged 13–19
Secondary schools
Multi-stage cluster sampling
```

Avoid a generic four-card layout unless the sample genuinely has four independent components.

## 8.7 Instruments slide

If there are multiple questionnaires, use a concise comparison table.

Suggested columns:

- construct;
- instrument;
- items;
- scale;
- reliability.

Omit methodological details that are not necessary for oral defense.

## 8.8 Model-fit slide

Use 3–5 large KPI-style figures with criterion comparison.

Do not drown the audience in secondary fit indices.

## 8.9 Descriptive-statistics slide

Prefer a chart when the task is comparison.

Use a table only when exact M/SD/min/max/skewness/kurtosis lookup matters.

If a table is used, visually emphasize the key statistic rather than every cell equally.

## 8.10 Direct-effects slide

Use:

- coefficient path diagram;
- coefficient ranking chart;
- or a compact hypothesis table.

Prefer to show direction and magnitude visually.

## 8.11 Mediation slide

This is normally one of the most important slides in a SEM thesis.

Use a large mediation diagram as the primary visual.

Emphasize:

- mediator paths;
- indirect effects;
- total indirect effect;
- significance.

## 8.12 Discussion slide

Translate statistical findings into a mechanism.

Example structure:

```text
Trauma
  ↓
Reduced emotional awareness
  +
Reduced sense of coherence
  ↓
Higher risky behavior
```

Then state the theoretical interpretation in 1–3 concise statements.

## 8.13 Implications slide

Use an actionable pathway:

```text
Finding → Clinical implication → School implication → Policy implication
```

Do not turn implications into a 10-item bullet list.

## 8.14 Limitations slide

Show each limitation paired with its consequence.

Example:

```text
Cross-sectional design
→ limits causal inference

Self-report measures
→ risk of reporting bias

Female-only sample
→ limits generalizability
```

## 8.15 Closing slide

Use:

- 2–3 major takeaways;
- concise thank-you;
- Q&A invitation.

Do not end with a dense bibliography or paragraph.

---

# 9. TABLE RULES

Tables are a frequent source of poor academic decks.

## 9.1 Reduce columns

Only retain columns needed for the oral argument.

## 9.2 Reduce rows

If 10 rows are not necessary, show 5 and explain the rest verbally or in notes.

## 9.3 Highlight signal

Use visual emphasis for:

- largest coefficient;
- significant paths;
- key fit indices;
- critical assumptions.

Do not highlight everything.

## 9.4 Never use tiny text

If the table cannot remain readable, split it.

## 9.5 Avoid prose inside cells

Replace long phrases with concise labels.

---

# 10. CHART RULES

## 10.1 Every chart must answer a question

Before drawing a chart, define:

> "What comparison or relationship should the audience see immediately?"

## 10.2 No decorative charts

Do not create charts that merely make a slide look scientific.

## 10.3 Use direct labeling

Whenever practical, label marks directly rather than forcing the audience to inspect a distant legend.

## 10.4 Keep axes honest

Do not truncate an axis in a way that exaggerates a scientific effect unless the truncation is explicitly justified and clearly marked.

## 10.5 Use consistent semantics

For example:

- negative coefficients always use one semantic treatment;
- positive coefficients another;
- non-significant results neutral.

Do not change the meaning of visual encodings from slide to slide.

---

# 11. SPEAKER NOTES

Every substantive slide should include Persian speaker notes.

Notes should:

- explain the slide rather than repeat it;
- contain transitions;
- clarify statistical interpretation;
- preserve important caveats;
- support a natural spoken narrative.

Recommended note structure:

```text
هدف اسلاید:
...

نکته کلیدی:
...

تفسیر:
...

گذار به اسلاید بعد:
...
```

Do not simply paste the slide bullets into notes.

Do not invent spoken claims absent from the source.

---

# 12. VISUAL QA: MANDATORY

The first generated PPTX is never automatically final.

## 12.1 Render the deck

After compilation:

1. render the PPTX to PDF and/or slide images;
2. generate a contact sheet or montage;
3. inspect the entire deck visually;
4. inspect representative slides individually;
5. run structural checks.

## 12.2 Inspect every slide for

- text overflow;
- clipping;
- element collisions;
- footer overlap;
- title collisions;
- illegible tables;
- tiny labels;
- broken Persian shaping;
- broken mixed RTL/LTR text;
- misdirected arrows;
- disconnected diagrams;
- inconsistent alignment;
- excessive empty space;
- excessive density;
- weak visual hierarchy;
- repeated layouts;
- orphaned elements;
- accidental sample metadata;
- inconsistent numeric formatting.

## 12.3 Density thresholds

Flag a slide as `DENSE` when any of the following is true:

- body text falls below 18 pt;
- more than ~90–110 words of visible prose are present on a normal content slide;
- more than 7 independent text blocks exist without a strong visual relationship;
- a table requires more than 6–8 columns in the available space;
- more than 2 large paragraphs are visible;
- the primary visual occupies less than roughly 30% of the usable canvas on a visual-results slide.

These thresholds are heuristics, not mathematical laws. Use them to trigger review.

## 12.4 Layout repetition threshold

Fail the deck when:

- the same layout family appears on consecutive content slides;
- a single generic card layout exceeds 25% of content slides;
- more than 30% of all slides share essentially the same geometry;
- section dividers are used merely to avoid designing content slides.

## 12.5 Typography threshold

Fail the slide if:

- body text is below the minimum target without a documented reason;
- Persian shaping is visibly broken;
- line breaks create unreadable mixed-language strings;
- numeric notation becomes visually ambiguous.

## 12.6 Visual hierarchy test

For each slide ask:

1. What is the first thing I see?
2. What is the second thing I see?
3. Can I state the slide's message in one sentence?

If the answer to #3 is unclear, redesign.

## 12.7 Five-second test

A reviewer should understand the topic and primary message of a slide within roughly five seconds before reading the detail.

If the slide requires reading every line to discover what matters, it fails the five-second test.

---

# 13. REPAIR LOOP

When QA finds problems, do not immediately shrink typography.

Use this repair order:

```text
1. Remove unnecessary content
2. Rewrite content more concisely
3. Change the visual encoding
4. Split the slide
5. Rebalance the layout
6. Adjust spacing
7. Only then make minor type-size adjustments
```

After repair:

```text
render → inspect → validate again
```

A maximum of three repair passes should be attempted automatically before the system reports unresolved issues.

---

# 14. STRUCTURAL QA

Validate the PPTX programmatically where possible.

Check:

- slide count;
- slide dimensions = 16:9;
- expected slide titles present;
- notes present on substantive slides;
- no placeholder text remains;
- no sample metadata remains;
- all referenced assets exist;
- all charts/figures have valid sources;
- no duplicate statistics contradict the truth model;
- no accidental blank slides;
- no unsupported external dependencies.

If the renderer has a known sample payload, ensure it is inaccessible unless demo mode is explicitly requested.

---

# 15. IMPLEMENTATION ARCHITECTURE

Do not put all behavior into one giant compiler file.

Recommended architecture:

```text
presentation_schema.py
research_truth_model.py
storyboard.py
content_selector.py
layout_engine.py
visual_encodings.py
chart_renderer.py
rtl_typography.py
notes_builder.py
powerpoint_renderer.py
qa_rules.py
render_preview.py
compile_presentation.py
```

Responsibilities:

### `research_truth_model.py`
Normalize source evidence and provenance.

### `storyboard.py`
Create the narrative sequence and slide messages.

### `content_selector.py`
Decide what material belongs on each slide.

### `layout_engine.py`
Choose layout families and place objects.

### `visual_encodings.py`
Provide reusable diagrams and visual patterns.

### `chart_renderer.py`
Generate data-driven charts.

### `rtl_typography.py`
Handle Persian/RTL-specific formatting and mixed-language strings.

### `notes_builder.py`
Generate source-grounded speaker notes.

### `powerpoint_renderer.py`
Render the visual specification to PPTX.

### `qa_rules.py`
Run structural and heuristic visual validations.

### `render_preview.py`
Render PPTX to PDF/images and produce inspection artifacts.

### `compile_presentation.py`
Orchestrate the pipeline; do not contain every layout implementation.

---

# 16. VISUAL SPECIFICATION CONTRACT

Before PowerPoint rendering, every slide should exist as a structured visual specification.

Example:

```json
{
  "slide_id": "s16",
  "size": "16:9",
  "background": "light",
  "section": "یافته‌ها",
  "title": "دو مسیر میانجی هر دو معنادار هستند",
  "message": "اثر غیرمستقیم از هر دو مسیر آگاهی هیجانی و احساس انسجام عبور می‌کند.",
  "layout_family": "mediation_diagram",
  "elements": [
    {
      "type": "node",
      "id": "trauma",
      "label": "ترومای دوران کودکی"
    },
    {
      "type": "node",
      "id": "ea",
      "label": "آگاهی هیجانی"
    },
    {
      "type": "node",
      "id": "soc",
      "label": "احساس انسجام"
    },
    {
      "type": "node",
      "id": "risk",
      "label": "رفتارهای پرخطر"
    },
    {
      "type": "path",
      "from": "trauma",
      "to": "ea",
      "label": "β = −0.50"
    },
    {
      "type": "path",
      "from": "trauma",
      "to": "soc",
      "label": "β = −0.59"
    },
    {
      "type": "path",
      "from": "ea",
      "to": "risk",
      "label": "β = −0.44"
    },
    {
      "type": "path",
      "from": "soc",
      "to": "risk",
      "label": "β = −0.40"
    },
    {
      "type": "kpi",
      "label": "Total indirect",
      "value": "β = 0.456"
    }
  ],
  "source_refs": ["chapter4/table23", "chapter4/table24"]
}
```

This intermediate representation makes the visual system independent from the raw thesis text.

---

# 17. QUALITY SCORE

Score the finished deck on 100 points.

## A. Research fidelity — 25

- exact statistics;
- correct names/metadata;
- source-grounded claims;
- correct methodological wording.

## B. Narrative quality — 20

- coherent sequence;
- one message per slide;
- strong transitions;
- findings have narrative priority.

## C. Visual communication — 20

- appropriate charts/diagrams;
- meaningful visual hierarchy;
- minimal unnecessary prose;
- effective emphasis.

## D. Readability / typography — 15

- sufficient type size;
- Persian shaping;
- mixed RTL/LTR stability;
- legible tables and charts.

## E. Visual consistency — 10

- coherent grid;
- restrained color system;
- consistent typography;
- deliberate recurring anchors.

## F. Technical integrity — 10

- valid PPTX;
- correct 16:9 size;
- notes;
- no missing assets;
- no overflow/collision defects.

Minimum recommended thresholds:

- overall ≥ 90;
- research fidelity ≥ 95;
- readability ≥ 90;
- technical integrity = 100.

Any factual identity error or unresolved severe overflow is an automatic failure regardless of score.

---

# 18. FAILURE MODES TO AVOID

The system must explicitly avoid these common bad outcomes.

## Failure A: "The card deck"

Symptoms:

- title;
- three rounded cards;
- footer;
- repeat 15 times.

Response:

Reclassify the slides by visual encoding and redesign.

## Failure B: "The document slide"

Symptoms:

- paragraphs;
- tiny text;
- no visual hierarchy.

Response:

Convert prose into a visual structure or split the content.

## Failure C: "The table dump"

Symptoms:

- full thesis table copied to slide;
- tiny type;
- every value visually equal.

Response:

Keep only decision-relevant fields and visualize the main comparison.

## Failure D: "The decorative science slide"

Symptoms:

- random circles;
- fake diagrams;
- generic icons;
- no data relationship.

Response:

Replace decoration with evidence-linked visual encoding.

## Failure E: "The tiny model"

Symptoms:

- SEM/path diagram occupies a small corner;
- explanatory bullets dominate.

Response:

Make the model the main visual and move interpretation to a concise annotation or speaker notes.

## Failure F: "The fake completeness"

Symptoms:

- missing source data quietly replaced with example data;
- unsupported citations;
- default institution/person metadata.

Response:

Fail generation instead of inventing or substituting.

## Failure G: "The successful PPTX that looks broken"

Symptoms:

- technically valid file;
- clipped text;
- overlapping boxes;
- unreadable Persian.

Response:

The PPTX is not accepted until render QA passes.

---

# 19. DEFAULT SLIDE DESIGN PATTERNS

Use these as starting patterns, not rigid templates.

## Pattern A — Big Idea

```text
[small section marker]

Large conclusion-oriented title

                 BIG NUMBER / BIG STATEMENT

      1–2 sentence interpretation
```

## Pattern B — Problem Funnel

```text
Broad problem
      ↓
Population/context
      ↓
Specific mechanism
      ↓
Research question
```

## Pattern C — Gap / Contribution

```text
KNOWN              MISSING              THIS STUDY
2–3 findings       one unresolved       integrated model
```

## Pattern D — Method Flow

```text
Population → Sampling → Measures → Collection → SEM → Bootstrap
```

## Pattern E — Result Spotlight

```text
          β = 0.456
      Total indirect effect

Supporting evidence     Supporting evidence
p < .001                 CI excludes zero
```

## Pattern F — Coefficient Map

```text
Predictor → Mediator → Outcome
     β            β

Direct path shown separately
```

## Pattern G — Limitation → Consequence

```text
Limitation                 Consequence
────────────               ─────────────
Cross-sectional            causal inference limited
Self-report                reporting bias possible
Female-only sample         generalizability limited
```

Again: these are patterns, not a license to reuse the same geometry throughout the deck.

---

# 20. FINAL ACCEPTANCE CHECKLIST

Before returning the PPTX, verify all of the following.

### Source integrity

- [ ] every identity field came from the current project;
- [ ] no sample identity remains;
- [ ] no statistic was fabricated;
- [ ] no unsupported citation was added;
- [ ] all critical numerical values have provenance.

### Narrative

- [ ] every slide has one primary message;
- [ ] the deck has a clear beginning, middle, findings, discussion, and close;
- [ ] the findings section has the greatest visual weight;
- [ ] slides do not merely restate the thesis.

### Visual design

- [ ] generic card-grid layout ≤ 25% of content slides;
- [ ] no repeated layout family on consecutive content slides;
- [ ] multiple visual encodings are used appropriately;
- [ ] key findings are visually prominent;
- [ ] major diagrams are large enough to read.

### Typography

- [ ] body text generally ≥ 20 pt;
- [ ] tables are readable;
- [ ] Persian shaping is stable;
- [ ] mixed RTL/LTR notation is legible;
- [ ] no text was shrunk merely to fit.

### Technical

- [ ] 16:9 dimensions;
- [ ] no clipping;
- [ ] no collisions;
- [ ] no missing assets;
- [ ] notes exist on substantive slides;
- [ ] output opens successfully.

### QA

- [ ] full deck rendered;
- [ ] contact sheet inspected;
- [ ] representative slides inspected individually;
- [ ] structural QA passed;
- [ ] repair pass completed where necessary;
- [ ] final score meets threshold.

Only after all critical checks pass may the presentation be delivered as final.

---

# 21. OPERATING PRINCIPLE FOR ANTIGRAVITY

When the user asks for a defense presentation, behave as an **academic presentation designer + data visualization designer + PowerPoint engineer**, not as a text-to-slides converter.

Your internal priority order is:

```text
Truth > Message > Visual encoding > Readability > Aesthetic polish > Decoration
```

When two goals conflict:

- choose factual accuracy over style;
- choose readability over density;
- choose meaningful visualization over card decoration;
- choose splitting a slide over shrinking text;
- choose source-grounded uncertainty over invented completeness;
- choose a render/repair cycle over declaring success from file creation alone.

The final deck should make a committee member think:

> "I can immediately see what the study asked, how it was tested, what the evidence shows, and why the result matters."

That is the quality standard for v3.

---

# 22. UNIFIED CLI REFERENCE & EXECUTION WORKFLOW

The skill provides a unified CLI (`main.py`) alongside dedicated modular scripts, offering full end-to-end automation for both **interactive HTML slide decks** and **native Microsoft PowerPoint (`.pptx`) presentations**.

### 22.1 Core CLI Commands

From the skill directory (`.agents/skills/persian-defense-presentation-builder/`):

```bash
# 1. Native PowerPoint Compilation (with Diagram Rendering, OMML Math, and QA Gate)
python3 main.py --compile-pptx --json examples/sample_defense_payload.json --output Defense_Presentation.pptx --theme academic_navy

# 2. Geometric Bounding-Box & Collision Overlap Audit
python3 main.py --audit-pptx Defense_Presentation.pptx --audit-json /tmp/audit_report.json

# 3. 300-DPI Publication Diagram Generation (Mediation, CONSORT, Timeline)
python3 main.py --render-diagram diagram_spec.json --output diagram.png --theme academic_navy

# 4. Extract Template Context, Fonts, Colors, and Layouts from PPTX
python3 main.py --extract-template template.pptx --template-out extracted_template/

# 5. Adapt Academic Payload to Canonical BRIEF.json (Ghost Deck Action Titles)
python3 main.py --adapt-brief --json examples/sample_defense_payload.json --output BRIEF.json

# 6. Validate BRIEF.json against Strict Schema
python3 main.py --validate-brief --brief BRIEF.json

# 7. Generate Interactive Standalone HTML Slide Deck
python3 main.py --generate --brief BRIEF.json --output presentation.html --eval

# 8. Automated Planning Mode (Generates BRIEF from Topic / Research Questions)
python3 main.py --plan "بررسی اثربخشی درمان ACT بر انعطاف‌پذیری روان‌شناختی"
```

---

# 23. SYNTHESIS OF EXTERNAL PRESENTATION ECOSYSTEM

This skill incorporates the proven best practices and innovations from four leading presentation skill frameworks, synthesized into an autonomous, zero-external-dependency, pure-Python architecture:

| External Framework | Core Capability Adapted | Native Implementation in Skill |
| :--- | :--- | :--- |
| **`anyideaz/pptx-skills`** | Template context extraction & element collision/overlap auditing | `scripts/extract_template.py` (extracts fonts, theme colors, layouts, shapes, and images into `context.json`) + `scripts/check_overlaps.py` (bounds calculation, card grouping, and gap verification) |
| **`Noi1r/powerpoint-skill`** | Native Microsoft Office Math (OMML) equation injection | `scripts/inject_omml.py` (pure-Python `latex2mathml` + `lxml` converter replacing LaTeX math with native Office Math `<m:oMath>` DrawingML elements) |
| **`Gabberflast/academic-pptx-skill`** | Ghost Deck Action-Title rule, SCR narrative framing, 300-DPI publication figures | `scripts/academic_brief_adapter.py` (derives informative action-titles answering "So what?", avoiding generic topic labels) + `scripts/render_diagrams.py` (pure-Python 300-DPI Matplotlib vector figures) |
| **`ningzimu/codex-ppt-skill`** | Multi-device layout presets, Data-Dashboard styling, high-density exhibit layouts | Standard 16:9 widescreen layout engine (`scripts/layout_engine.py`) with 22 specialized academic layout builders, KPI panels, split-view diagrams, and WCAG AAA color contrast |

### 23.1 Ghost Deck Action-Title Discipline
Following `academic-pptx-skill`:
- **Forbid Generic Headers**: Slides titled *"بیان مسئله"*, *"فرضیه‌ها"*, or *"یافته‌ها"* are banned in content slides.
- **Enforce Action Titles**: Titles must declare the empirical finding or theoretical core claim:
  - *Generic (Banned)*: «نتایج تحلیل واریانس چندمتغیره»
  - *Action-Title (Required)*: «تأثیر معنادار مداخله بر تنظیم هیجان در پس‌آزمون و پیگیری (F = ۱۲/۴۵, p < .۰۰۱)»
- **Dual Title Architecture**: In PPTX and HTML layouts, the section category is displayed as an understated top banner (e.g. `فصل چهارم: یافته‌های پژوهش`), while the primary slide headline carries the full informative action title.

### 23.2 Pure-Python OMML Math Injection
Following `powerpoint-skill` without external binaries:
- Standard python-pptx cannot natively insert mathematical equations.
- `inject_omml.py` parses LaTeX delimiters (`$...$`, `$$...$$`) or explicit equation tags in tables and text boxes.
- It converts LaTeX to MathML using pure-Python `latex2mathml`, then maps MathML XML trees directly into native Microsoft Word/PowerPoint Office Math (`<m:oMathPara>` and `<m:oMath>`).
- Equations render crisply inside Microsoft PowerPoint with native font formatting and math layout, completely eliminating raster image degradation.

### 23.3 300-DPI Publication Diagram Engine
Following `academic-pptx-skill`:
- Statistical and methodological diagrams are generated deterministically in pure Python using Matplotlib with publication-grade 300-DPI resolution.
- Three standard academic diagram types are supported out of the box:
  1. **Mediation Path Models**: 3-variable mediation diagrams showing paths $a, b, c, c'$ with bootstrap indirect effect confidence intervals.
  2. **CONSORT 2010 Flowcharts**: 4-phase participant flow (Assessed $\to$ Excluded $\to$ Randomized $\to$ Analyzed) with trial retention metrics.
  3. **Intervention Protocol Timelines**: Session-by-session clinical timeline with alternating callout badges and milestone objectives.
- Full font fallback configuration ensures clean rendering of Persian characters (`Arial Unicode MS`, `Geeza Pro`, `B Nazanin`, `Tahoma`) without glyph missing errors.

### 23.4 Element Overlap & Collision Geometry Audit
Following `pptx-skills`:
- Automated bounding-box intersection calculations prevent text overlap, caption collisions, and container boundary clipping.
- Recognizes card container grouping to eliminate false positive warnings on nested sub-elements.
- Enforces minimum vertical separation ($> 0.04$ inches) and ensures zero critical collisions across all 16:9 widescreen slides.

---

# 24. SCRIPT INVENTORY & REPOSITORY TAXONOMY

```
.agents/skills/persian-defense-presentation-builder/
├── SKILL.md                             # Master operational instructions & guidelines v3.5.0
├── main.py                              # Unified CLI entrypoint (compile, audit, render, adapt, generate, plan)
├── examples/
│   ├── sample_defense_payload.json      # Complete 22-slide real academic defense dataset
│   └── test_diagram_spec.json           # Sample mediation & CONSORT diagram specifications
└── scripts/
    ├── compile_defense_presentation.py   # Master 16:9 PPTX compiler with automated QA pipeline
    ├── layout_engine.py                 # 22 high-density defense layout builders (tables, charts, spotlights)
    ├── presentation_schema.py           # ResearchTruthModel, ProjectMeta, Color Palettes, and validation
    ├── presentation_qa.py               # 100-point rubric QA gate (Fidelity, Narrative, Visuals, Type, Tech)
    ├── content_planner.py               # Storyboard synthesis from research truth parameters
    ├── academic_brief_adapter.py        # Ghost Deck adapter converting academic JSON to BRIEF.json
    ├── check_overlaps.py                # Geometry bounding-box & collision overlap auditor
    ├── inject_omml.py                   # Pure-Python LaTeX -> MathML -> OMML Office Math injector
    ├── render_diagrams.py               # 300-DPI Matplotlib vector diagram engine (Mediation/CONSORT/Timeline)
    ├── extract_template.py              # PPTX template context, font, color, and layout extractor
    ├── low_context.py                   # slide-creator HTML engine runtime, validator, and evaluator
    └── visual_preview.py                # PDF and image contact-sheet generator for presentation review
```

---

# 25. AUTOMATED QUALITY ASSURANCE RUBRIC (100/100)

Every presentation compiled by this skill must achieve a score of $\ge 90/100$ on the automated QA gate before client delivery:

1. **Slide Count & Timing (10 pts)**: Master's (18–22 slides, 20–25 min), PhD (24–30 slides, 30–45 min).
2. **Speaker Notes Coverage (15 pts)**: 100% of substantive slides must contain rich, conversational candidate defense speaker notes in academic Persian.
3. **Ghost Deck Action-Titles (15 pts)**: Slide titles must state conclusions, not generic labels.
4. **Layout Variety & Alternation (15 pts)**: No two consecutive slides share the same layout family; generic cards $\le 25\%$; maximum layout family dominance $\le 30\%$.
5. **Statistical & Empirical Rigor (15 pts)**: Strict APA 7th Edition formatting, exact $p$-values, effect sizes ($\eta_p^2, d$), and test statistics.
6. **Visual & Diagram Standards (15 pts)**: Clean 300-DPI mediation models, CONSORT flows, and APA tables.
7. **Typography & OpenXML Directionality (15 pts)**: Persian font hierarchy (`B Titr` 28–36 pt titles, `B Nazanin` $\ge 20$ pt body), pure RTL OpenXML DrawingML formatting, and zero element overlaps.


