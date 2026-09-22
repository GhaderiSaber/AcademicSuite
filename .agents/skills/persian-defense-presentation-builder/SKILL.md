---
name: persian-defense-presentation-builder
description: Build 16:9 thesis and dissertation defense presentations (HTML, PPTX,
  Google Slides) with native SmartArt RTL, decoupled LTR stats, and dedicated hypothesis
  slides.
---

# Persian Defense Presentation Builder (طراحی اسلایدهای پیشرفته جلسه دفاع)

This skill produces defense-ready, high-retention graduate defense presentations (کارشناسی ارشد و دکتری) adhering to Iranian university standards, supervisor template branding, and strict psychometric/statistical rigor.

---

## 1. When to Activate This Skill
Activate this skill when:
1. The user requests a **defense presentation (ارائه دفاع پایان‌نامه یا رساله)** from completed thesis chapters (Chapters 1–5), proposals, or statistical results.
2. The user needs to convert a dissertation or empirical findings into **16:9 widescreen PowerPoint (`.pptx`)**, **interactive HTML**, or **Google Slides**.
3. The user needs to audit an existing defense deck for **bounding-box overlap, typography compliance, or layout variety**.
4. The user needs **300-DPI publication diagrams** (Mediation models, CONSORT flowcharts, clinical timelines).

---

## 2. Hard Non-Negotiable Directives
- **Mandatory 8-Stage Presentation Sequence (Directive 3)**: Monolithic slide generation in a single prompt is strictly forbidden. The agent MUST execute the 8-stage sequence producing verified physical artifacts on disk:
  - *Stage D.0*: Findings Ingestion & Payload Verification (`00_defense_findings_payload.json`)
  - *Stage D.1*: Storyboard & 14-Slide Architecture (`01_defense_storyboard.docx`, `.md`, `.json`)
  - *Stage D.2*: Dedicated Statistical & Hypothesis Slide Triads (`02_hypothesis_slides.docx`, `.md`, `.json`)
  - *Stage D.3*: Deterministic Deck Compilation (`Defense_Presentation.pptx` + `presentation.html`)
  - *Stage D.4*: High-Resolution 300-DPI Publication Diagram (`structural_model_diagram.png`)
  - *Stage D.5*: Candidate 20-Minute Defense Script & Q&A Guide (`04_defense_script.docx`, `.md`, `.json`)
  - *Stage D.6*: Geometry Collision, Font Dual-Slot & Typography Audit (`05_presentation_qa_audit.json`, `.md`)
  - *Stage D.7*: Committee Viva Voce Oral Defense Simulation (`06_defense_committee_simulation.docx`, `.md`, `.json`)
- **Interactive Path Selection**: Prompt the user to choose an execution path before compiling (see Section 3).
- **Zero Emojis in Academic Slides (Directive 4.1)**: Strictly prohibited across all slides, tables, and candidate speaker notes.
- **Zero English Words in Persian Slides (Directive 4.1)**: All text, headings, and labels must be Persian. Latin characters are restricted to standardized statistical symbols ($M, SD, t, F, p, \beta, z$) and fit indices in `Times New Roman` italic.
- **Academic Tone Sobriety (Directive 4.2)**: Eliminate colloquial jargon (e.g. "نقشه راه") and evaluative puffery («عالی»، «فوق‌العاده»). Maintain neutral, dignified scholarly prose.
- **Decoupled LTR Runs for Fit Indices (Directive 4.2)**: Emit Latin acronyms ($\chi^2/df, \text{RMSEA}, \text{CFI}, \text{TLI}, \text{SRMR}$) with `lang="en-US"` to prevent BiDi word reversal.
- **Left-Side Minus Sign Invariant (Directive 4.2)**: Enforce LTR numeric cells (`rtl="0"`) so minus signs precede numbers ($-0.32$, never $0.32-$).
- **Dedicated Hypothesis Slides (Directive 4.3)**: Every hypothesis ($H_1$ to $H_n$) receives its own dedicated slide in both Results (یافته‌ها) and Discussion (بحث و نتیجه‌گیری).
- **Native SmartArt with RTL Reverse (Directive 4.3)**: Set `SmartArt.Reverse = 1` for Right-to-Left arrows and bind Persian fonts (`B Titr` / `B Nazanin`) to all nodes.
- **Dual-Slot Font Binding (Directive 5.2)**: Bind `<a:cs>` to `B Nazanin` / `B Titr` and `<a:latin>` to `Times New Roman` to prevent box glyph rendering (`□□□`).
- **Standard Persian Decimals (Directive 4)**: Standard dot format (`۰.۰۰۱`, `۰.۰۵`); mandatory preservation of leading zero (`۰.۰۰۱`, never `.۰۰۱`).

---

## 3. Mandatory Interactive Path Selection Protocol
Before generating presentation artifacts, the Agent **MUST** prompt the user to confirm their desired format:
- **Path 1: Interactive HTML Slide Deck** — Browser-based, responsive, CSS animations, ideal for instant visual review.
- **Path 2: Native Microsoft PowerPoint (.pptx)** — Complete DrawingML presentation with native SmartArt, 3D elevation, and automatic transitions.
- **Path 3: Google Drive @Document Bridge for Google Slides** — Generates `Defense_Presentation_Brief.docx` and syncs Gemini prompt for Google Slides.
- **Path 4: Full Suite** — Generates all three formats simultaneously.

---

## 4. Deterministic CLI Command Reference
All operations execute via `main.py` in `.agents/skills/persian-defense-presentation-builder/`:

```bash
# 1. Compile Native PowerPoint (.pptx) Presentation (Path 2)
python3 main.py --path pptx --json examples/sample_defense_payload.json --output Defense_Presentation.pptx --theme academic_navy

# 2. Compile Interactive HTML Deck (Path 1)
python3 main.py --path html --json examples/sample_defense_payload.json --output presentation.html --theme academic_navy

# 3. Generate Google Drive / Google Slides Bridge (Path 3)
python3 main.py --path google_slides --json examples/sample_defense_payload.json

# 4. Audit Slide Overlaps & Bounding-Box Collisions
python3 main.py --audit-pptx Defense_Presentation.pptx --audit-json /tmp/audit_report.json

# 5. Render 300-DPI Publication Diagram (Mediation / CONSORT)
python3 main.py --render-diagram examples/test_diagram_spec.json --output diagram.png --theme academic_navy

# 6. Extract University PPTX Template Context & Styles
python3 main.py --extract-template university_template.pptx --template-out extracted_template/

# 7. Adapt Research Truth Payload to Canonical BRIEF.json
python3 main.py --adapt-brief --json examples/sample_defense_payload.json --theme academic_navy --output BRIEF.json

# 8. Automated Planning Mode (Generates Storyboard from Topic/RQ)
python3 main.py --plan "بررسی اثربخشی درمان ACT بر انعطاف‌پذیری روان‌شناختی"
```

---

## 5. Input Artifacts & Verification Checkpoints
- **Input Artifacts**:
  - Research findings (`stats_results.json`, `Chapter_4_Results.docx`, or `sample_defense_payload.json`).
  - Institutional PowerPoint template (`.pptx`) for exact style extraction.
- **Mandatory Checkpoint Deliverables**:
  - `BRIEF.json`: Canonical storyboard specification validated against `visual_spec_contract.md`.
  - `Defense_Presentation.pptx` or `presentation.html`: Finished 16:9 widescreen presentation deck.
  - `audit_report.json`: Zero-collision geometry verification report.
  - Candidate Speaker Notes: 100% Persian notes attached to every substantive slide.

---

## 6. Modular References Directory
Detailed guidelines, schemas, and engine architectures are modularized in `references/`:
1. [PowerPoint Advanced Creative Engine](.agents/skills/persian-defense-presentation-builder/references/powerpoint_creative_engine.md): COM automation, native SmartArt RTL, 3D shapes, and automatic motion.
2. [Slide Composition Rules](.agents/skills/persian-defense-presentation-builder/references/slide_composition_rules.md): Slide-specific composition hierarchy (Cover, Problem, Gap, Method, Mediation, Discussion).
3. [Visual Specification Contract](.agents/skills/persian-defense-presentation-builder/references/visual_spec_contract.md): Canonical `BRIEF.json` schema and layout families.
4. [Quality Score & Rubric](.agents/skills/persian-defense-presentation-builder/references/quality_score_rubric.md): 100-point defense presentation evaluation criteria.
5. [Diagram Patterns](.agents/skills/persian-defense-presentation-builder/references/diagram-patterns.md): Statistical path models and CONSORT flowcharts.
6. [Design System](.agents/skills/persian-defense-presentation-builder/references/design-system.md): Light academic color schemes, typography grids, and contrast ratios.
7. [Review Checklist](.agents/skills/persian-defense-presentation-builder/references/review-checklist.md): Pre-delivery QA checklist.
