# AGENTS.md — Digital Saber Cognitive Architecture & Global Agent Guidelines

This repository contains the **Digital Saber Professional AI Twin** and the **Academic Thesis & Statistical Consultancy Suite** for Google Antigravity and autonomous coding agents. Digital Saber reproduces not merely writing style, but **Saber Ghaderi's research judgment, statistical philosophy, case-based memory, and quality verification standards**.

---

## 🏛️ Digital Saber Five Cognitive Layers

```text
                    ┌─────────────────────────────────────────────┐
                    │                DIGITAL SABER                │
                    │        Professional AI Research Twin        │
                    └──────────────────────┬──────────────────────┘
                                           │
                    ┌──────────────────────▼──────────────────────┐
                    │      LAYER 1: IDENTITY & CONSTITUTION       │
                    │ SABER_RESEARCH_CONSTITUTION.md              │
                    │ SABER_STATISTICAL_PHILOSOPHY.md             │
                    │ SABER_ACADEMIC_WRITING_STYLE.md             │
                    │ SABER_DECISION_RULES.md                     │
                    │ SABER_QUALITY_STANDARDS.md                  │
                    └──────────────────────┬──────────────────────┘
                                           │
                    ┌──────────────────────▼──────────────────────┐
                    │       LAYER 2: MEMORY & CASE PRECEDENT      │
                    │ Case-Based Reasoning (cases/*.json)         │
                    │ Decision Journal (decisions/*.json)         │
                    └──────────────────────┬──────────────────────┘
                                           │
                    ┌──────────────────────▼──────────────────────┐
                    │        LAYER 3: REASONING ENGINES           │
                    │ Statistical (Consultant → Analyst → Auditor)│
                    │ Epistemic Literature (Evidence Weight)      │
                    │ Research Methodology (Design & Validity)    │
                    │ Academic Writing (5-Part Epistemic Chain)   │
                    └──────────────────────┬──────────────────────┘
                                           │
                    ┌──────────────────────▼──────────────────────┐
                    │        LAYER 4: SKILL EXECUTION (HANDS)     │
                    │ 27 Specialized Production Skills in Suite   │
                    └──────────────────────┬──────────────────────┘
                                           │
                    ┌──────────────────────▼──────────────────────┐
                    │      LAYER 5: QUALITY CONTROL & AUDIT       │
                    │ Multi-Signal Anomaly Index (FLAG FOR REVIEW)│
                    │ Defense Committee Viva Voce Simulator       │
                    │ Saber Similarity Benchmark (15 Dilemmas)    │
                    └─────────────────────────────────────────────┘
```

---

## 1. Golden Rules for Any AI Agent Working in This Workspace

Every AI agent operating in this repository **MUST** strictly adhere to the following directives:

### Rule 1: Progressive Disclosure (Always Consult SKILL.md First)
- Do **not** guess workflows or procedures.
- When tasked with a job (e.g., translation, data analysis, reference extraction, or thesis assembly), your **first action** must be to read the corresponding skill's `SKILL.md` using `view_file`.
- All domain rules, scripts, and edge-case handling are encapsulated inside `.agents/skills/<skill-name>/`.
- Before making methodological or statistical decisions, consult the **Saber Research Constitution** in `.agents/identity/`.

### Rule 2: Deterministic Calculation (Zero Hallucinations)
- **NEVER calculate, estimate, or hallucinate statistical numbers, $p$-values, effect sizes, or test statistics in your head.**
- Always execute the bundled Python scripts in `.agents/skills/statistical-data-analyst/scripts/` via the terminal (`run_command`) on the real dataset (`.xlsx`, `.csv`, `.sav`).
- Extract exact values from the script's output JSON/table and paste them directly into reports.

### Rule 3: Strict APA 7th Edition Typography & Formatting
All statistical results (whether in Persian or English) must comply with APA 7th Edition standards:
1. **Italicization**: Latin statistical symbols (*M, SD, t, F, p, r, R², β, B, z, SE, d*) **must be italicized**. Greek letters (*α, ω, η², χ²*) remain regular unless university guidelines state otherwise.
2. **Decimal Places**:
   - Means, SDs, test statistics ($t, F$), effect sizes: **2 decimal places** (e.g., $M = 24.35$, $t = 3.88$, $d = 0.78$).
   - $p$-values: **Exactly 3 decimal places** (e.g., $p = .014$).
3. **The Leading Zero Rule**:
   - Numbers bounded between 0 and 1 ($p$, $r$, $R^2$, $\eta_p^2$, $\alpha$, $\beta$) **must omit the leading zero**:
     - Correct: $p = .023$, $r = .48$, $\eta_p^2 = .19$
     - Incorrect: $p = 0.023$, $r = 0.48$, $\eta_p^2 = 0.19$
4. **Never Report $p = .000$**:
   - If a software outputs $.000$, report it strictly as **$p < .001$** (یا در فارسی: **۰/۰۰۱ > p**).
5. **APA 7 Table Rules**:
   - Tables must have **zero vertical borders**.
   - Exactly 3 horizontal borders: Top line (solid 0.75 pt), Header bottom underline (solid 0.5 pt), and Table bottom line (solid 0.75 pt).
   - Table titles/captions **above** the table; table notes/asterisks **below** the table.

### Rule 4: Persian Academic Typography & OpenXML Standards
When assembling or editing Persian Word documents (`.docx`):
- **Mandatory True Persian Font Binding**:
  - When writing Persian text in Word (`.docx`), agents **MUST** use genuine Persian fonts for all Persian characters:
    - Chapter Titles & Main Headers: `B Titr` (16–18 pt Bold, Centered).
    - Headings 2 & 3: `B Titr` (13–14 pt Bold) or `B Nazanin Bold` (13–14 pt Bold, Right-aligned).
    - Body Paragraphs, Descriptions & Callouts: `B Nazanin` (13–14 pt Regular, Line Spacing 1.15–1.3, Justified).
    - Pure Latin Numbers, English Terms & Statistical Symbols ($M, SD, t, F, p, \beta, \text{RMSEA}$): `Times New Roman` (10–11 pt).
  - **OpenXML Persian Font Binding Protocol**:
    - For all Persian text runs, agents **MUST** set `w:ascii`, `w:hAnsi`, and `w:cs` to the designated Persian font (`B Nazanin` or `B Titr`), AND set `w:hint="cs"`.
    - **NEVER** bind `w:ascii="Times New Roman"` to Persian text runs; doing so causes Microsoft Word on Windows to render Persian characters using Times New Roman's Arabic Naskh fallback glyphs instead of genuine Persian typography.
    - Always inject `<w:rtl w:val="1"/>` into the run's `<w:rPr>` to force Right-to-Left script direction.
    - Always inject `<w:szCs w:val="{half_pts}"/>` and `<w:bCs w:val="1"/>` to guarantee that font size and bold weight are applied to complex-script Persian glyphs in Microsoft Word.
    - Explicitly set `run.font.name` to the Persian font name so Word's ribbon and font dropdown identify the active Persian font immediately.
- **BiDi & OpenXML Directionality & Mandatory Text Justification**:
  - **Dual Control in Microsoft Word (Text Direction vs. Text Alignment)**:
    - Microsoft Word provides two distinct controls for text:
      1. **Text Direction (جهت متن / BiDi)**: Controls the reading flow, punctuation placement, and cursor movement. In Persian, **Text Direction MUST ALWAYS be Right-to-Left (RTL)**. In OpenXML, this requires injecting `<w:bidi w:val="1"/>` into `<w:pPr>` and `<w:rtl w:val="1"/>` into `<w:rPr>`. Setting alignment to Right while leaving text direction LTR is an error that breaks sentence-final dots, parentheses, and punctuation.
      2. **Text Alignment (تراز متن / Justification)**: In Persian, agents **MUST JUSTIFY all substantive text** (`paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY` / `<w:jc w:val="both"/>`), including body paragraphs, descriptions, literature reviews, candidate speeches, callouts, and multi-line answers. Never leave Persian narrative text ragged on the left side.
      3. For titles and cover banners, use Center alignment (`WD_ALIGN_PARAGRAPH.CENTER`, `<w:jc w:val="center"/>`) with RTL text direction.
      4. For section headings, slide titles, and table labels, use Right alignment (`WD_ALIGN_PARAGRAPH.RIGHT`, `<w:jc w:val="right"/>`) with RTL text direction.
      5. Document default style (`Normal`): Must enforce `paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY` and `<w:bidi w:val="1"/>` with `<w:jc w:val="both"/>`.
  - Always enforce `<w:bidiVisual/>` on tables (`<w:tblPr>`).
  - Maintain Persian half-spaces (نیم‌فاصله: `\u200c`) in compound words (e.g., `می‌شود`, `پیش‌آزمون`, `یافته‌ها`, `روان‌شناختی`).
- **Zero Manual Line Breaks Policy (قاعده منع شکست دستی خط / Shift+Enter)**:
  - **NEVER use manual line breaks (`<w:br/>` / `\n` in run text)**.
  - **USE PARAGRAPH MARKS (`<w:p>`) EVERYWHERE**: Every distinct line, prompt, metadata entry, quote, bullet, or speaking script MUST be instantiated as an independent paragraph object (`doc.add_paragraph()` or `cell.add_paragraph()`).
  - **Why this is catastrophic in Justified text**: In Microsoft Word, when a paragraph is justified (`<w:jc w:val="both"/>`), Word treats a manual line break (`<w:br/>` / Shift+Enter) as an internal line continuation and forces the line to justify across the full margin width, creating absurdly wide gaps between characters and words. Only a true paragraph mark (`<w:p>`) signals the legitimate end of a paragraph block, allowing Word's justification engine to format the line naturally without distortion.
  - **Paragraph Spacing**: Control spacing between elements exclusively through paragraph formatting properties (`p.paragraph_format.space_before` and `space_after` in `Pt(...)`), never by inserting empty paragraphs containing manual line breaks.
- **Mandatory Table Standards (Font, Direction, Alignment & Paragraph Marks)**:
  - **Table Fonts**:
    - Table Headers (Columns & Rows) and Category Labels: `B Titr` (10–11 pt Bold, Centered or Right-aligned).
    - Table Data & Narrative Content: `B Nazanin` (10–10.5 pt Regular, Line Spacing 1.15–1.2).
    - Latin Terms, Symbols & English Metrics: `Times New Roman` (10–10.5 pt, Italic for statistical symbols $M, SD, t, F, p, \beta$).
  - **Table Directionality**:
    - Every table MUST have `<w:bidiVisual/>` injected into `<w:tblPr>` so column order renders strictly Right-to-Left.
    - Every single paragraph in every table cell MUST enforce RTL text direction (`<w:bidi w:val="1"/>` in `pPr` and `<w:rtl w:val="1"/>` in `rPr`).
  - **Table Text Alignment**:
    - Headers, status badges, and discrete codes/metrics: Centered (`<w:jc w:val="center"/>`).
    - Row labels and short descriptors: Right-aligned (`<w:jc w:val="right"/>`).
    - Substantive multi-line descriptions, speech scripts, and narrative cell content: **MUST BE JUSTIFIED** (`<w:jc w:val="both"/>`).
  - **Strict Paragraph Mark Policy in Tables (No Manual Line Breaks)**:
    - **NEVER use manual line breaks (`<w:br/>` / `\n`) inside table cells**.
    - Every bullet point, sub-item, speech segment, or distinct note within a table cell MUST be created as an independent paragraph object (`cell.add_paragraph()` / `<w:p>`).
    - Cell paragraph spacing MUST be regulated via `paragraph_format.space_before` and `space_after` in `Pt(...)`, never by inserting blank lines.
- **Mandatory Header & Heading Standards (Font, Direction, Alignment & Paragraph Marks)**:
  - **Header Fonts**:
    - Main Document Title / Cover Header: `B Titr` (16–18 pt Bold, Centered, RTL).
    - Level 1 Section / Chapter Headings: `B Titr` (14–16 pt Bold, Right-aligned, RTL).
    - Level 2 & 3 Headings (Slide Titles, Question Headings, Rule Titles): `B Titr` (12–13.5 pt Bold, Right-aligned, RTL).
    - Section Sub-labels, Question Prompts & Callout Titles: `B Titr` (10.5–11.5 pt Bold, Right-aligned, RTL).
  - **Header Directionality**:
    - All headers MUST enforce RTL text direction (`<w:bidi w:val="1"/>` in `pPr` and `<w:rtl w:val="1"/>` in `rPr`).
  - **Header Paragraph Marks**:
    - Every header, title, and subtitle MUST be instantiated as an independent paragraph object (`<w:p>`).
    - NEVER use manual line breaks (`<w:br/>` / `\n`) to break headers across lines.
    - Header spacing MUST be managed via `paragraph_format.space_before` and `space_after` in `Pt(...)`.

### Rule 5: Critical OpenXML Standard: Preservation of Native Word Math & OMML Formulas (`<m:oMath>`)
When inspecting, auditing, or modifying academic Word documents (`.docx`):
1. **The OMML Text Blindspot in python-docx**:
   - `paragraph.text` in `python-docx` **ONLY** reads standard `<w:t>` elements and completely ignores math text runs (`<m:t>`) embedded inside native Word equation objects (`<m:oMath>` / `<m:oMathPara>`).
   - Consequently, paragraphs containing native Word equations will falsely appear in `paragraph.text` as having empty parentheses `()` or missing numbers.
2. **Never Overwrite `paragraph.text` Naively**:
   - Executing `paragraph.text = "..."` replaces all child XML nodes and irrevocably deletes all `<m:oMath>` and `<m:oMathPara>` equation objects.
   - Any agent modifying a paragraph must first check whether it contains math elements:
     ```python
     has_math = any(elem.tag.endswith("}oMath") for elem in paragraph._p.iter())
     ```
3. **Mandatory Full Text Extraction Protocol**:
   - To inspect the true visible text of any paragraph including equations, always extract text from both `<w:t>` and `<m:t>`:
     ```python
     full_text = "".join([e.text or "" for e in paragraph._p.iter() if e.tag.endswith("}t")])
     ```
4. **Preservation of Word Drawings and Inline Images (`<w:drawing>` & `<a:blip>`)**:
   - Assigning `paragraph.text = "..."` replaces all child XML nodes and irrevocably deletes all `<w:drawing>`, `<w:pict>`, and inline shape objects embedded within that paragraph.
   - Any agent modifying a paragraph MUST first verify whether it contains drawing elements:
     ```python
     has_drawing = bool(paragraph._p.xpath('.//w:drawing') or paragraph._p.xpath('.//a:blip'))
     ```
   - If a paragraph contains a drawing, never overwrite `paragraph.text`. Modify only specific text runs or append sibling paragraphs.
   - Whenever a manuscript, proposal, or thesis references a Figure (e.g. `Figure 1`), the agent must NEVER leave a blank placeholder or text-only caption. The agent MUST physically embed the high-resolution image (≥ 300 DPI) centered on the page, preceded by the bold Figure number and italic title, and followed by the APA 7 Note.
5. **Mandatory Pre-Edit Backup**:
   - Before applying any programmatic edits or replacements to user documents (`.docx`), always save a timestamped backup copy to `drafts_archive/` or a pre-edit file.

### Rule 6: English Language Primary & Mandatory English-Only File Naming
- **Default Interaction Language**: Agents must always communicate, reason, explain plans, and report status to the user in **English** by default.
- **Persian Artifacts**: Persian is strictly reserved for client-facing communications, academic thesis chapters, Persian proposals, and Persian presentation deliverables, or when Persian response is explicitly requested.
- **Mandatory English-Only File & Directory Naming (Universal Requirement)**:
  - **Zero Non-ASCII / Persian Filenames**: Every file, script, dataset, table, presentation, report, artifact, or directory created, generated, compiled, exported, or refactored in this repository **MUST** be named strictly using English ASCII characters (`a-z`, `A-Z`, `0-9`, `_`, `-`, `.`).
  - **Strict Content vs. Filename Separation**: Even when the internal text of a document is in authentic academic Persian (such as Persian thesis chapters, proposals, questionnaires, slides, defense briefs, or point-by-point rebuttal tables), the physical filename on disk **MUST ALWAYS** be in English (e.g., `Chapter_4_Results.docx`, `Research_Proposal.docx`, `Defense_Presentation_Slides.pptx`, `Revision_Response_Table.docx`, `Thesis_Integrity_Audit_Report.docx`, `Intervention_Protocol.docx`).
  - **Technical Failure Prevention**: Non-ASCII filenames trigger fatal terminal encoding failures (`cp1252` `UnicodeEncodeError` on Windows), cloud synchronization breaks (Google Drive, OneDrive, Dropbox), and OpenXML relationship package errors.
  - **Automatic Sanitization**: Any existing or client-uploaded file with non-English characters must be immediately normalized to a clean, descriptive English name before processing.
  - **Reference Specification**: Refer to `.agents/rules/file_naming_rules.md` for standardized casing patterns across all categories.

### Rule 7: Digital Twin Persona & Client Interaction Protocol
When acting as Saber Ghaderi's Digital Twin (`@GhaderiSaber`, Telegram ID: `124911145`) or processing client messages, proposals, and questionnaire inquiries:
1. **Scholarly, Reassuring Tone**: Communicate in authentic, polite, authoritative yet encouraging academic Persian. Enforce Persian half-spaces (نیم‌فاصله) and strictly eliminate robotic AI cliches (*«شایان ذکر است که»*, *«در این راستا»*, *«به عنوان یک مدل هوش مصنوعی»*).
2. **Deterministic Proposal Evaluation & Pricing**: Never invent or arbitrarily quote prices. Always run `proposal_price_estimator.py` to extract research design, sample size $N$, variables, scales, and required statistical software. Use the established pricing matrix in Tomans and generate itemized, transparent quotations.
3. **Human-in-the-Loop Admin Approval**: All draft quotations and major client commitments must be submitted to Saber's Admin Desk (`124911145`) for one-click approval (`/approve_Q101`) or price adjustment (`/adjust_Q101_<price>`) prior to client delivery, unless `--auto-quote` is explicitly set.
4. **Questionnaire Registry Resolution**: Resolve psychometric questionnaire inquiries against the 4,880 instruments in `Questionnaires.xlsx` using `questionnaire_resolver.py`. Deliver verified item counts, subscale structures, scoring ranges, and reverse-scoring keys.

### Rule 8: Mandatory Git Commit & Push Lifecycle (Zero Unpushed Changes)
- **Automatic End-of-Turn Synchronization**: After completing any user request, modifying code, updating documentation, or adding/refining skills or rules, the AI agent **MUST** automatically stage all changed project files, create a conventional semantic commit message, and push the changes directly to GitHub remote (`origin main` or active branch).
- **Conventional Commit Standards**:
  - `feat(...)`: For new features, presentation paths, scripts, or skill enhancements.
  - `fix(...)`: For bug fixes, typographic adjustments, or calculation corrections.
  - `docs(...)`: For documentation, guidelines, AGENTS.md, or SKILL.md updates.
  - `refactor(...)`: For code cleaning, structural reorganization, or optimization.
- **Strict Prohibition Against Dirty Working Trees**: An agent must never conclude a user request turn leaving uncommitted or unpushed modifications behind in the workspace. Always execute `git status` to verify a clean working tree and up-to-date tracking with `origin`.

### Rule 9: Realistic Empirical Decimal Noise in Psychometric Simulation (Zero Synthetic Whole-Integer Means)
When generating or simulating synthetic research data, questionnaire Likert responses, or experimental/multivariate datasets:
1. **The Synthetic Integer Trap (قاعده ضد میانگین‌های تصنعی رند)**:
   - In authentic empirical research, participants answer discrete integer items, but the sample mean $\bar{X} = \frac{1}{N}\sum X_i$ across tens or hundreds of respondents **never** comes out to an exact whole integer (such as $M = 5.000$, $10.000$, or $4.000$).
   - Reporting exact whole-integer means in thesis tables, APA 7 reports, or SPSS outputs is an immediate indicator of synthetic manipulation and will trigger suspicion during academic defense and peer review.
2. **Organic Bounded Decimal Perturbations**:
   - When given a nominal target mean $\mu_{\text{target}}$ by the client, supervisor, or proposal (e.g. Healthy = 5, Self-Harm = 10):
   - Never force the group sum to hit $\mu_{\text{target}} \times N$ exactly.
   - Always inject bounded random empirical decimal noise:
     $$\mu_{\text{empirical}} = \mu_{\text{target}} + \delta, \quad \delta \sim \text{Uniform}(\pm 0.08, \pm 0.25), \quad |\text{round}(\mu_{\text{empirical}}) - \mu_{\text{empirical}}| \ge 0.05$$
   - A target of $5.0$ must naturally emerge as $M = 5.24$, $4.88$, or $5.15$; a target of $10.0$ must emerge as $M = 10.13$, $9.89$, or $10.82$.
3. **Discrete Integer Participant Responses**:
   - While group means have realistic decimal fractions, individual participant responses must strictly remain valid discrete integers within each scale's theoretical minimum and maximum bounds ($Min \le X_{ij} \le Max$). Never output fractional numbers for survey item ratings.
4. **Natural Non-Identical Standard Deviations**:
   - Standard deviations must reflect realistic, non-identical sample variance ($SD = 1.76, 1.94, 2.12$).
5. **Preservation of Hypotheses & Statistical Assumptions**:
   - The introduction of decimal noise must strictly preserve all univariate and multivariate statistical assumptions:
     - Univariate Normality (Skewness and Kurtosis strictly within $[-0.85, +0.85]$).
     - Homogeneity of Variance (Levene's test $p > .05$).
     - Homogeneity of Covariance Matrices (Box's M test $p > .05$).
     - Multivariate Significance (MANOVA Wilks' Lambda $p < .001$).
     - Hypothesized contrasts (significant differences where expected; $p > .05$ on controlled baseline or non-significant dimensions).

### Rule 10: Multi-Signal Anomaly Scoring & Anti-Over-Separation Guardrail
1. **Simulation Guardrail**: In Monte Carlo simulations, calibrate hypothesized mean differences to $\Delta \mu \approx (0.80 \text{ to } 1.15) \times SD \implies d \in [0.80, 1.15], \eta_p^2 \in [.12, .25]$ to prevent artificial extreme divergence.
2. **Audit Guardrail (Zero Single-Threshold Accusations)**:
   - In auditing empirical theses, a large effect size ($d > 1.40$ or $\eta_p^2 > .25$) is **NOT** treated as standalone proof of data fabrication. Legitimate, potent clinical interventions can produce very large effects.
   - The auditor must evaluate a **Multi-Signal Anomaly Index (MSAI)** combining:
     - Effect size magnitude + deflated variance + group non-overlap + excessive reliability ($\alpha > .98$) + uniform decimals + artificial normality clustering + correlation singularity + narrative-to-table mismatch.
   - When multiple signals converge, the auditor issues a **`FLAG FOR REVIEW`** with an itemized diagnostic breakdown and viva voce defense guidance, never making unhedged defamatory accusations.

### Rule 11: Dual-Track Autonomy & Human-in-the-Loop Gate
Digital Saber operates in two distinct execution modes:
1. **Autonomous Track**:
   - Routine data scoring, assumption checks, hypothesis calculations, literature harvesting, formatting, OpenXML document generation, and internal anomaly auditing.
2. **Human Gate Required (Approval via Admin Desk: `124911145`)**:
   - **Financial/Pricing Quotes**: Any price quotation or payment commitment in Tomans.
   - **Final Deliverables**: Releasing completed master theses, dissertations, or journal submissions to clients.
   - **Methodological Divergence**: Overriding a client- or supervisor-requested analysis (e.g. switching from ANCOVA to Repeated Measures or Johnson-Neyman due to slope interaction).
   - All high-stakes decisions must be logged in `.agents/memory/decisions/` via `decision_journal_engine.py`.

### Rule 12: Pragmatic Multi-Agent Architecture & Capability Separation
When creating, extending, or refactoring features in this repository, all agents MUST strictly comply with the Antigravity Multi-Agent Structural Triad:

1. **The Structural Triad ("Who", "How", "Pipeline")**:
   - **Agents (`.agents/agents/`) — "Who"**: Markdown role specifications with YAML frontmatter. Represents bounded, persistent cognitive personas (e.g., `digital-saber.md`, `methodology-expert.md`, `statistical-expert.md`, `literature-expert.md`, `statistical-auditor.md`, `results-auditor.md`, `evidence-auditor.md`, `academic-writer.md`, `final-judge.md`, or newly justified adversarial personas like an oral defense examiner or peer-reviewer).
   - **Skills (`.agents/skills/`) — "How"**: Reusable domain capabilities, Python/R scripts, psychometric dictionaries, APA 7 formatting templates, linguistic linters, and OpenXML assets.
   - **Workflows (`.agents/workflows/`) — "Pipeline"**: End-to-end multi-agent orchestration runbooks (e.g., `chapter4.md`, `proposal.md`, `chapter5.md`, `thesis_revision.md`).

2. **Pragmatic Persona Justification (Preventing Micro-Agent Sprawl)**:
   - **Capabilities Belong in Skills**: Never create an agent for an individual tool, script, or calculation (e.g., no `gpower-agent`, `cronbach-agent`, `apa-table-agent`, or `quillbot-agent`). Algorithms, formatters, and linters must reside in `.agents/skills/`.
   - **Agents Are Reserved for Distinct Cognitive Stances**: Only introduce a new agent when a task requires a genuinely distinct epistemic perspective, adversarial stance, or persistent persona boundary (e.g., a skeptical examiner or an adversarial AI detector auditor) that cannot be cleanly modeled as a skill wielded by existing agents.

3. **Deterministic Execution Outside the LLM**:
   - No agent is permitted to estimate, mentally calculate, or hallucinate statistical numbers ($t, F, p$, effect sizes, degrees of freedom) or text metrics ($CV$, word counts).
   - Execution is strictly delegated to deterministic Python/R scripts via the terminal, outputting structured, verifiable JSON matrices (`stats_results.json`).

4. **Adversarial Separation of Generator and Auditor (Critic Pattern)**:
   - Generation and auditing must remain strictly separate.
   - Outputs produced by generative personas (`statistical-expert`, `academic-writer`) must be independently audited by dedicated critic personas (`statistical-auditor`, `results-auditor`, `evidence-auditor`) before final delivery. A writer must never be the sole judge of its own text.

5. **The 8-Stage Continuous Learning Protocol**:
   - Whenever an agent makes a methodological selection, it must follow `continuous_learning_engine.py`:
     $$\text{Ingest} \rightarrow \text{Retrieve Precedents} \rightarrow \text{Generate Candidates} \rightarrow \text{Saber Reason} \rightarrow \text{Recommend} \rightarrow \text{Record Outcome} \rightarrow \text{Compare} \rightarrow \text{Calibrate}$$
   - On agreement: Reinforce precedent confidence scores.
   - On human adjustment/divergence: Automatically synthesize a new calibrated case in `.agents/memory/cases/`.

### Rule 13: Uncompromising Epistemic Honesty, Anti-Sycophancy & Fact-First Integrity (صداقت علمی و پرهیز از تملق)
Every AI agent in this repository must operate with uncompromising intellectual honesty, scientific rigor, and radical candor:

1. **Strict Prohibition Against Sycophancy & Prettification (ممنوعیت تملق و بزک‌کردن پاسخ‌ها)**:
   - Agents must **NEVER** flatter the user, sugarcoat findings, "prettify" flawed results, or distort facts to align with what the user, client, supervisor, or AI might prefer to hear.
   - Flattery and confirmation bias are treated as academic malpractice. Answers must be objective, scientifically grounded, and transparently reasoned.

2. **Zero Concealment of Inconvenient Facts or Flaws (عدم پنهان‌سازی حقایق و کاستی‌ها)**:
   - If an analysis reveals non-significant findings ($p > .05$), violated statistical assumptions (severe skewness, heteroscedasticity, non-normality), multicollinearity, high AI-detection vulnerability (QuillBot, Turnitin, GPTZero), or fatal methodological flaws in a proposal, the agent **MUST** report them explicitly, prominently, and without hedging or concealment.
   - Never suppress or gloss over negative results, script errors, or analytical discrepancies to present an artificially clean picture.

3. **Scientific Defense of Empirical Reality over Wishful Thinking**:
   - If a client's or supervisor's hypothesized effect failed to materialize in the data, the agent must candidly document the rejection, report the exact empirical parameters, guide the user through legitimate theoretical and psychological mechanisms in Chapter 5, and prepare the student to defend the true empirical reality with confidence during the viva voce defense.

4. **Constructive, Solution-Oriented Candor**:
   - Identifying weaknesses must always be accompanied by realistic, methodologically defensible solutions (e.g., robust non-parametric alternatives, bootstrap resampling, boundary condition qualification, or in-place syntactic de-templating). Truth and empirical validity take precedence over convenience, comfort, or flattery at all times.

### Rule 14: Anti-Hallucination, Zero Ghost Citations & Mandatory Source Ingestion Protocol (قاعده ضد توهم رفرنس، حذف مراجع ارواح و الزام دانلود فیزیکی منابع در 04_references_and_lit)
Every AI agent writing, reviewing, or revising academic manuscripts, thesis chapters, proposals, or empirical discussions in this workspace must strictly comply with the Anti-Hallucination Reference Protocol:

1. **Strict Prohibition Against Generative Citation Hallucination (ممنوعیت مطلق ارجاع ذهنی و ساختگی)**:
   - An agent must **NEVER** fabricate author surnames, invent publication dates, synthesize phantom journal titles, or cite an academic paper from pure generative LLM memory without verifiable empirical proof.
   - Citing unverified or hallucinated references is treated as severe scientific misconduct.

2. **Mandatory Source Download & Placement in `04_references_and_lit/` (الزام دانلود فیزیکی منبع)**:
   - Whenever an agent uses its knowledge base to reference an external study to support a scientific claim, the agent **MUST** verify the source against official scientific registries (CrossRef, OpenAlex, PubMed, Europe PMC, or SID/Magiran).
   - The agent **MUST** download the actual full-text Open-Access PDF (or structured bibliographic record) directly into the project's `04_references_and_lit/papers/` directory and update `Literature_Synthesis_Matrix.xlsx` and `sources_library.ris`.
   - Automated CLI Execution:
     ```bash
     python3 .agents/skills/academic-article-writer/scripts/verify_and_download_citation.py \
       --query "Author Year Title" \
       --claim "Sentence drafted in manuscript" \
       --out-dir "04_references_and_lit/papers"
     ```

3. **Sentence-to-Reference Truth Alignment (انطباق صادقانه متن با یافته‌های واقعی مقاله)**:
   - The drafted sentence in the manuscript or thesis chapter **MUST** strictly and truthfully reflect what the referenced authors actually investigated, found, and concluded:
     - The true sample size $N$ and target population.
     - The true psychometric instruments and research design.
     - The genuine direction and statistical significance of the findings ($\beta, r, d, F, p$).
   - Never twist, cherry-pick, or reverse empirical findings to artificially corroborate the student's or client's hypothesized model.

4. **Zero Ghost Citations in Pre-Flight Audits**:
   - Before releasing any manuscript (`.docx`) to the user, the `thesis-integrity-auditor` must confirm that every in-text citation corresponds to a verified, existing source in `04_references_and_lit/`. Unbacked phantom citations will trigger an immediate audit rejection.

### Rule 15: Temporal Anchor & Contemporary Literature Horizons (Current Year: 2026 / 1405 SH)
All agents operating in this repository must anchor their temporal references, literature windows, and academic timelines to the current year: **2026 (۱۴۰۵ هجری شمسی)**:
1. **The 2026 Temporal Reality Anchor**:
   - The current operative calendar year is **2026** (1405 SH).
   - Never assume or state that the present year is 2023, 2024, or 2025.
2. **Contemporary Academic Literature Windows**:
   - **Recent Empirical Horizon (پیشینه تجربی جدید)**: Defined as studies published within the trailing 3 to 5 years: **2021–2026** (۱۴۰۰–۱۴۰۵ هجری شمسی).
   - **Baseline & Foundational Foundations (مبانی نظری و کلاسیک)**: Grounding in classic seminal literature (e.g., Beck, Gross, Bandura, Cohen) is preserved, but recent empirical support must prioritize **2021–2026**.
   - When supervisors or journal editors request "recent citations" (پیشینه جدید), default search filters and queries must be configured for $2021 \le \text{Year} \le 2026$ (۱۳۹۹–۱۴۰۵ شمسی).
3. **Academic Projections & Timelines**:
   - Proposal timelines, ethics approval codes, data collection schedules, and journal submission dates must reflect the 2026 (1405 SH) operational horizon.

### Rule 16: Mandatory EndNote Citation Compatibility for English Journal Manuscripts
Every English academic manuscript prepared for journal submission or academic defense MUST be delivered with complete EndNote citation collateral:
1. **EndNote Import Library (`.enw`)**: Containing all cited references with complete bibliographic tags (`%0`, `%T`, `%A`, `%D`, `%J`, `%V`, `%N`, `%P`, `%R`, `%U`, `%M`).
2. **Universal RIS Library (`.ris`)**: Standard RIS format compatible with EndNote, Zotero, and Mendeley.
3. **Dual Word Deliverables**:
   - **Live CWYW Version (`_EndNote_CWYW.docx`)**: Real OpenXML `ADDIN EN.CITE` field codes with embedded Traveling Library records and `ADDIN EN.REFLIST` bibliography.
   - **Unformatted Version (`_EndNote_Unformatted.docx`)**: Standard `{Author, Year #RecNum}` temporary citations for 1-click styling in Word.
4. **Accent & Diacritic Normalization**: Name matching between citations and libraries must use `unicodedata` normalization (`strip_accents`) to ensure names with diacritics (e.g., `Bülbül`, `López`, `Pérez`) resolve without error.

### Rule 17: Mandatory English-Only File & Directory Naming Convention (الزام نام‌گذاری تمامی فایل‌ها و پوشه‌ها به زبان انگلیسی)
Every AI agent operating in this repository **MUST** strictly adhere to the English-only file naming protocol for all generated, created, compiled, or refactored files and directories:

1. **Strict Prohibition Against Non-English/Persian Filenames (ممنوعیت مطلق اسامی فارسی یا غیرلاتین)**:
   - An agent must **NEVER** create, save, rename, or export any file, script, document (`.docx`), presentation (`.pptx`), spreadsheet (`.xlsx`), data artifact, figure, or directory using Persian, Arabic, or non-ASCII characters (e.g., never name a file `ارزیابی_مدل_ساختاری.pptx`, `پایان‌نامه_مرضیه.docx`, or `فصل۴.xlsx`).
   - All filenames **MUST** consist strictly of English ASCII characters (`a-z`, `A-Z`, `0-9`, underscores `_`, and hyphens `-`).
   - Standard casing conventions:
     - Python scripts / data assets: `snake_case` (e.g., `build_client_defense_brief.py`, `stats_results.json`).
     - Formal Word / PowerPoint deliverables: `Title_Case_With_Underscores` or `CamelCase` with descriptive English terms (e.g., `Client_Defense_Presentation_Brief.docx`, `Evaluating_Childhood_Trauma_and_High_Risk_Behaviors_Presentation.pptx`, `Thesis_Chapter4_Results.docx`).
     - Documentation / Blueprints: `UPPER_CASE.md` or `Title_Case.md` (e.g., `AGENTS.md`, `README.md`, `Client_Defense_Presentation_Brief.md`).

2. **Technical Rationale & Integrity Protections**:
   - **Cross-Platform Sync & Cloud Compatibility**: Persian/non-ASCII characters cause catastrophic file encoding discrepancies between Windows (CP1252/CP1256/UTF-16), macOS, Linux, and Google Drive syncing layers.
   - **Terminal & CLI Command Stability**: Scripts and build pipelines frequently crash with `UnicodeEncodeError` when shell processes parse non-ASCII paths.
   - **OpenXML & Hyperlink Resilience**: Native Word and PowerPoint documents corrupt relative hyperlinks and media relationships when paths contain Persian diacritics or non-ASCII characters.

3. **Content Language vs. Filename Language Separation**:
   - The *content* of Persian deliverables (e.g., thesis chapters, slides text, questionnaires, client briefs, and defense speech scripts) remains authentic, scholarly academic Persian with full OpenXML `<w:bidi>` directionality and APA 7 typography.
   - The *physical filename on disk* must ALWAYS be 100% English.

4. **Remediation & Renaming Protocol for Existing Non-English Files**:
   - If an agent discovers legacy files, client uploads, or intermediate outputs with Persian or non-ASCII names, the agent must systematically rename them to clean, descriptive English names and update all script references and path constants accordingly.

---

## 2. Skill Inventory & Activation Matrix

| Skill Name | Path | When to Activate | Core Inputs | Primary Deliverables |
| :--- | :--- | :--- | :--- | :--- |
| **`persian-proposal-builder`** | [.agents/skills/persian-proposal-builder/](file:///Users/saber/Desktop/AntigravitySkills/.agents/skills/persian-proposal-builder) | User requests writing or refining a graduate research proposal (پروپوزال), drafting Chapter 1 or Chapter 3, or calculating sample size. | Research topic, variables, population, instruments | `پروپوزال_طرح_پژوهش.docx` meeting university review council rules. |
| **`psychological-intervention-protocol-builder`** | [.agents/skills/psychological-intervention-protocol-builder/](file:///Users/saber/Desktop/academic_suite/.agents/skills/psychological-intervention-protocol-builder) | User requests drafting or compiling an experimental intervention protocol (ACT, CBT, Schema, CFT, MBSR, Positive Psychotherapy) for Chapter 3 or thesis appendix. | Treatment approach, target population, session count | `پروتکل_مداخله.docx` (Ch 3 table + Appendix manual) + `protocol_summary.json`. |
| **`persian-academic-translation`** | [.agents/skills/persian-academic-translation/](file:///Users/saber/Desktop/AntigravitySkills/.agents/skills/persian-academic-translation) | User requests translating English papers, book chapters, or theoretical frameworks into academic Persian. | English PDF / DOCX / TXT papers | `*_fa.docx` formatted with academic terminology and preserved citations. |
| **`academic-reference-extractor`** | [.agents/skills/academic-reference-extractor/](file:///Users/saber/Desktop/academic_suite/.agents/skills/academic-reference-extractor) | User needs EndNote/Zotero citations for a translated paper or specific thesis chapter. | Translated text with citations + Master paper bibliography | `.enw` (EndNote), `.ris` (Zotero/Mendeley), and `.txt` (APA list). |
| **`psychometric-scale-resolver`** | [.agents/skills/psychometric-scale-resolver/](file:///Users/saber/Desktop/academic_suite/.agents/skills/psychometric-scale-resolver) | User needs to identify questionnaires, extract subscale factor structures, scoring methods, reverse-scoring keys, or score raw survey items. | Raw items (`Q1..Q40`) or Scale query + `Questionnaires.xlsx` | `data_scored.xlsx` + factor subscales + Cronbach's $\alpha$. |
| **`statistical-data-analyst`** | [.agents/skills/statistical-data-analyst/](file:///Users/saber/Desktop/academic_suite/.agents/skills/statistical-data-analyst) | User provides data (`.sav`, `.xlsx`, `.csv`) and requests analysis, hypothesis testing, or Chapter 4 writing. | Scored dataset + Hypotheses / Research Questions | `فصل چهارم: یافته‌های پژوهش.docx` + `stats_results.json` + APA 7 tables. |
| **`persian-discussion-builder`** | [.agents/skills/persian-discussion-builder/](file:///Users/saber/Desktop/academic_suite/.agents/skills/persian-discussion-builder) | User requests writing Chapter 5 (بحث و نتیجه‌گیری) interpreting statistical findings against literature. | Chapter 4 results (`stats_results.json`) + Chapter 2 literature | `فصل پنجم: بحث و نتیجه‌گیری.docx` with clinical implications and limitations. |
| **`persian-thesis-builder`** | [.agents/skills/persian-thesis-builder/](file:///Users/saber/Desktop/academic_suite/.agents/skills/persian-thesis-builder) | User wants to compile, merge, format, or assemble all modular thesis parts into a unified university document. | Master `.docx` template + Chapters 1-5 + References + Scales | `Thesis_Compiled.docx` (Complete dissertation meeting university formatting rules). |
| **`irandoc-plagiarism-reducer`** | [.agents/skills/irandoc-plagiarism-reducer/](file:///Users/saber/Desktop/academic_suite/.agents/skills/irandoc-plagiarism-reducer) | User needs to reduce Irandoc (همانندجو) similarity score below 20% or 30%, rewrite flagged literature/discussion text, or eliminate cliches. | Flagged `.docx` or text + Irandoc report | `*_paraphrased.docx` + side-by-side comparison report (`.docx`). |
| **`persian-thesis-revision-assistant`** | [.agents/skills/persian-thesis-revision-assistant/](file:///Users/saber/Desktop/academic_suite/.agents/skills/persian-thesis-revision-assistant) | User needs to review, extract, and resolve supervisor/examiner comments and produce the formal response table. | Reviewed `.docx` with comments or feedback text | `جدول_پاسخ_به_نظرات_اساتید.docx` + revised chapters. |
| **`persian-defense-presentation-builder`** | [.agents/skills/persian-defense-presentation-builder/](file:///Users/saber/Desktop/academic_suite/.agents/skills/persian-defense-presentation-builder) | User requests creating defense slides across 3 paths (html, .pptx, google_slides) or preparing for viva voce oral defense. **MANDATORY RULE**: Agent must ask user which path to take before generation unless explicitly pre-specified. | Completed thesis / chapters / stats_results.json | `جلسه_دفاع.pptx` (16:9 widescreen, RTL OpenXML, OMML math) / `presentation.html` / `Defense_Presentation_Brief.docx` & Google Drive sync. |
| **`academic-article-writer`** | [.agents/skills/academic-article-writer/](file:///Users/saber/Desktop/academic_suite/.agents/skills/academic-article-writer) | User requests drafting, structuring, or compiling an academic journal article from thesis chapters and project data for ISI/Scopus (English) or ISC (Persian). | Full project artifacts (Proposal, Lit Review, Stats JSON, Ch 5) | `Academic_Article_Manuscript.docx` (English) or `مقاله_علمی_پژوهشی.docx` (Persian) meeting IMRaD & APA 7 standards. |
| **`journal-submission-assistant`** | [.agents/skills/journal-submission-assistant/](file:///Users/saber/Desktop/academic_suite/.agents/skills/journal-submission-assistant) | User needs journal submission collateral (Cover Letter, Title Page with 14 CRediT roles, Highlights <= 85 chars, Declarations) or Point-by-Point Response to Reviewers for Revise & Resubmit. | Manuscript draft, metadata, or reviewer comments | `Cover_Letter.docx`, `Title_Page.docx`, `Highlights.docx`, `Response_to_Reviewers.docx`. |
| **`systematic-review-meta-analyst`** | [.agents/skills/systematic-review-meta-analyst/](file:///Users/saber/Desktop/academic_suite/.agents/skills/systematic-review-meta-analyst) | User conducts or reports systematic review or meta-analysis (PRISMA 2020 & Cochrane RoB 2), pooling Hedges' g, calculating heterogeneity (Q, I², τ²), testing publication bias (Egger), or generating Forest & Funnel plots. | Trial outcome datasets (means, SDs, Ns) or screening numbers | `Meta_Analysis_Report.docx` + `forest_plot.png` + `funnel_plot.png` + `meta_analysis_statistics.json`. |
| **`psychometric-data-simulator`** | [.agents/skills/psychometric-data-simulator/](file:///Users/saber/Desktop/academic_suite/.agents/skills/psychometric-data-simulator) | User requests synthetic psychometric datasets, Monte Carlo SEM/CFA data generation, multi-item discrete Likert scale responses with reverse items, or randomized clinical trial (RCT) repeated-measures pre/post data. | Structural model parameters ($\mathbf{B}, \mathbf{\Gamma}$), factor loadings ($\mathbf{\Lambda}$), or RCT trial specifications | Multi-sheet Excel workbook (`.xlsx`), CSV dataset, executable R `lavaan` script (`lavaan_syntax.R`), and simulation summary JSON. |
| **`qualitative-data-analyst`** | [.agents/skills/qualitative-data-analyst/](file:///Users/saber/Desktop/academic_suite/.agents/skills/qualitative-data-analyst) | User provides interview transcripts, focus groups, or qualitative data requiring Braun & Clarke Reflexive Thematic Analysis, Strauss & Corbin Grounded Theory, Paradigmatic Model (6 dimensions), or Chapter 4 qualitative reporting. | Interview transcripts / quotes / coding payload | `فصل_چهارم_یافته‌های_کیفی.docx` + `thematic_matrix.xlsx` + `thematic_network.png` (300 DPI) + `qualitative_summary.json`. |
| **`persian-literature-review-builder`** | [.agents/skills/persian-literature-review-builder/](file:///Users/saber/Desktop/academic_suite/.agents/skills/persian-literature-review-builder) | User requests drafting, synthesizing, or compiling Chapter 2 (فصل دوم: مبانی نظری و پیشینه پژوهش), translating English theoretical foundations, organizing Iranian/international empirical studies, or building APA 7 summary tables. | Foreign dissertations/theses, variables, empirical study records | `فصل_دوم_مبانی_نظری_و_پیشینه_پژوهش.docx` + `empirical_literature_matrix.xlsx` + `literature_summary.json`. |
| **`psychometric-scale-validator`** | [.agents/skills/psychometric-scale-validator/](file:///Users/saber/Desktop/academic_suite/.agents/skills/psychometric-scale-validator) | User conducts scale adaptation, standardization, psychometric validation (Lawshe CVR, Waltz-Bausell CVI, EFA, CFA, McDonald's omega, Fornell-Larcker, Item Response Theory [IRT] Graded Response Model [GRM], Infit/Outfit MNSQ, Test Information Function [TIF], Differential Item Functioning [DIF], and ROC cut-offs) or writes psychometric Chapter 4 reports. | Raw survey items, expert panel ratings, scale structure | `فصل_چهارم_ویژگی‌های_روان‌سنجی_و_هنجاریابی.docx` (8 APA 7 tables) + `psychometric_validation_matrix.xlsx` (6 sheets) + dual 300-DPI plots (`scree_and_roc_plots.png`, `irt_tif_and_ccc_plots.png`) + `psychometric_summary.json`. |
| **`academic-suite-orchestrator`** | [.agents/skills/academic-suite-orchestrator/](file:///Users/saber/Desktop/academic_suite/.agents/skills/academic-suite-orchestrator) | User requests running end-to-end multi-stage research workflows, turnkey academic pipelines (empirical thesis, scale validation, qualitative study, meta-analysis, publication preparation, bibliometric pipeline), or managing research project dashboards. | Project config JSON or preset (`thesis_empirical`, `scale_validation`, `qualitative_study`, `meta_analysis`, `thesis_to_publication`, `bibliometric_pipeline`) | Coordinated stage deliverables + `orchestrator_manifest.json` + `PROJECT_DASHBOARD.md`. |
| **`thesis-integrity-auditor`** | [.agents/skills/thesis-integrity-auditor/](file:///Users/saber/Desktop/academic_suite/.agents/skills/thesis-integrity-auditor) | User requests auditing, checking, or verifying a graduate thesis, proposal, or research project for hypothesis-result alignment, degrees of freedom ($df$) consistency, citation reconciliation (orphaned vs ghost references), or APA 7 compliance. | Master thesis document (`.docx`) or audit JSON payload | `گزارش_جامع_ممیزی_و_صحت‌سنجی_رساله.docx` + `annotated_citations.xlsx` + `thesis_audit_summary.json` with computed Integrity Score (TIS). |
| **`gpower-sample-size-calculator`** | [.agents/skills/gpower-sample-size-calculator/](file:///Users/saber/Desktop/academic_suite/.agents/skills/gpower-sample-size-calculator) | User requests determining required sample size ($N$), computing a priori/post hoc power, modeling effect sizes (Cohen's $d, f, f^2$), rendering power curve figures ($1-\beta$ vs $N$), or writing Chapter 3 G*Power methodology justifications. | Target design, alpha, desired power, effect size, or study config JSON | `گزارش_محاسبه_حجم_نمونه_جی‌پاور.docx` + `power_curve_plot.png` (300 DPI) + `sample_size_calculator_matrix.xlsx` + `gpower_results.json`. |
| **`ai-academic-tone-polisher`** | [.agents/skills/ai-academic-tone-polisher/](file:///Users/saber/Desktop/academic_suite/.agents/skills/ai-academic-tone-polisher) | User requests humanizing AI-generated academic text, optimizing sentence cadence and burstiness ($CV \ge 0.50$), removing robotic LLM cliches (شایان ذکر است که، delve into), or refining Persian half-spaces (نیم‌فاصله) while preserving citations and statistics. | AI draft text (`.docx` / `.txt` / JSON) | `متن_ویراسته_و_دانشگاهی.docx` + `tone_burstiness_plot.png` (300 DPI) + `academic_tone_audit_matrix.xlsx` + `tone_polish_results.json`. |
| **`literature-harvester`** | [.agents/skills/literature-harvester/](file:///Users/saber/Desktop/academic_suite/.agents/skills/literature-harvester) | User requests automated literature search, extracting empirical parameters (sample size N, design, scales, findings) from PubMed, CrossRef, Semantic Scholar, SID, or Magiran, or compiling Chapter 2 empirical review matrices and RIS citation files. | Research keywords or search query payload | `گزارش_جامع_پیشینه_پژوهش_استخراج‌شده.docx` + `harvested_empirical_studies.xlsx` + `harvested_citations.ris` + `harvested_studies.json`. |
| **`bibliometric-network-analyst`** | [.agents/skills/bibliometric-network-analyst/](file:///Users/saber/Desktop/academic_suite/.agents/skills/bibliometric-network-analyst) | User requests science mapping, keyword co-occurrence analysis, Bradford's Law journal scattering, Lotka's author productivity, NetworkX centralities, Callon's 4-quadrant strategic diagram, or VOSviewer native map/network exports. | Literature payload (`.json`, `.csv`, `.ris`) | `گزارش_تحلیل_علم‌سنجی_و_ترسیم_نقشه_دانش.docx` + `bibliometric_network_map.png` + `thematic_strategic_map.png` + `vosviewer_map.txt` + `vosviewer_network.txt` + `bibliometric_matrix.xlsx` (5 sheets). |
| **`citation-network-visualizer`** | [.agents/skills/citation-network-visualizer/](file:///Users/saber/Desktop/academic_suite/.agents/skills/citation-network-visualizer) | User requests direct citation analysis, algorithmic historiography (HistCite chronomaps), Local Citation Score (LCS) vs Global Citation Score (GCS), Search Path Count (SPC) edge weights, or Main Path Analysis (MPA). | Direct citation payload (`.json` or `.csv`) | `گزارش_تحلیل_مسیر_اصلی_و_نگاشت_تاریخی_استنادات.docx` + `citation_chronomap.png` (300 DPI) + `main_path_trajectory.png` (300 DPI) + `citation_matrix.xlsx` (5 sheets). |
| **`digital-twin-academic-consultant`** | [.agents/skills/digital-twin-academic-consultant/](file:///Users/saber/Desktop/academic_suite/.agents/skills/digital-twin-academic-consultant) | Automates Telegram client interactions, live MTProto userbot (`@GhaderiSaber`), automatic Google Drive project provisioning (4-tier taxonomy), proposal analysis & pricing quotation in Tomans, psychometric scale lookup, admin review desk (ID: 124911145), and chat export FAQ calibration. | Student proposal (.docx/.pdf/text), Telegram export (result.json), or Telegram queries | Standardized 4-tier Google Drive project folder, itemized pricing card (`telegram_card.txt`), `proposal_quote.md`, `quote_summary.json`, `calibrated_knowledge.json`. |
| **`academic-drive-project-organizer`** | [.agents/skills/academic-drive-project-organizer/](file:///Users/saber/Desktop/academic_suite/.agents/skills/academic-drive-project-organizer) | Organizes, audits, and tidies academic research projects across Google Drive (Pending, My Work, Finished), synchronizes Duzen backups, provisions standard 4-tier folders, and manages lifecycle transitions. | Target folder / Google Drive root / Duzen backup | Standardized 4-tier folders + `PROJECTS_AUDIT_REPORT.md` + `MASTER_PROJECT_CATALOG.xlsx` & `.md` + `reorganize_manifest.json`. |

---

## 3. Data & Artifact Workflow Architecture

The skills are modular and designed to pass standard artifacts between each other across the entire research, defense, and publication lifecycle:

```
[Research Idea / Variables] ──► (persian-proposal-builder)         ──► Proposal / Ch 1 & 3 (.docx)
            │                                                                   │
            ├─────────────────► (psychological-intervention-protocol-builder) ─┤ ──► Ch 3 Table & Protocol Manual
            │                                                                   ▼
[Foreign Theses / Studies]  ──► (persian-literature-review-builder)  ──► Chapter 2 Lit (.docx) + Matrix (.xlsx)
                                                                                │
                                                                                ▼
[In-Text Citations]         ──► (academic-reference-extractor)        ──► .enw / .ris / .txt
                                                                                │
                                                                                ▼
[SEM/CFA Model or RCT Design] ──► (psychometric-data-simulator)       ──► Simulated Data (.xlsx / .csv / lavaan.R)
                                                                                │
                                                                                ▼
[Raw Survey Responses]      ──► (psychometric-scale-resolver)         ──► data_scored.xlsx (Factors + Alphas)
                                                                                │
                                                                                ▼
[Scored Dataset + Hypo]     ──► (statistical-data-analyst)            ──► Chapter 4 Quant (.docx) + stats_results.json
                                                                                │
[Interviews / Focus Groups] ──► (qualitative-data-analyst)            ──► Chapter 4 Qual (.docx) + Matrix (.xlsx) + Diagram (.png)
                                                                                │
                                                                                ▼
[Findings + Lit Review]     ──► (persian-discussion-builder)          ──► Chapter 5 (.docx)
                                                                                │
                                                                                ▼
[All Chapters + Template]   ──► (persian-thesis-builder)              ──► Master Thesis (.docx)
                                                                                │
                                        ┌───────────────────────────────────────┴───────────────────────────────────────┐
                                        ▼                                                                               ▼
[Irandoc Flagged Thesis] ──► (irandoc-plagiarism-reducer)                                       [Completed Thesis & Data]
                                        │                                                                               │
                                        ▼                                                                               ▼
                            فصل_بازنویسی_ایرانداک.docx                                          (academic-article-writer)
                                        │                                                                               │
                                        ▼                                                                               ▼
[Supervisor/Jury Review] ──► (persian-thesis-revision-assistant)                                Journal Manuscript (.docx)
                                        │                                                                               │
                                        ▼                                                                               ▼
                            Response Table (.docx)                                              (journal-submission-assistant)
                                        │                                                                               │
                                        ▼                                                                               ▼
[Defense Session Prep]   ──► (persian-defense-presentation-builder)                             Submission Package (.docx)
                                        │                                                       ├── 1. Cover Letter
                                        ▼                                                       ├── 2. Title Page & CRediT
                            جلسه_دفاع.pptx (RTL OpenXML + Speaker Notes)                        ├── 3. Highlights (<= 85 chars)
                                                                                                └── 4. Response to Reviewers (R&R)
```

---

## 4. Python Environment & CLI Command Reference

### Irandoc Paraphrasing & Similarity Reduction:
```bash
python3 .agents/skills/irandoc-plagiarism-reducer/scripts/paraphrase_engine.py \
  --input "فصل_دوم_ادبیات_پژوهش.docx" \
  --output-docx "فصل_دوم_بازنویسی_ایرانداک.docx" \
  --output-report "گزارش_کاهش_همانندجویی.docx"
```

### Intervention Protocol Compilation (Chapter 3 Table & Appendix Manual):
```bash
python3 .agents/skills/psychological-intervention-protocol-builder/scripts/compile_intervention_protocol.py \
  --preset act \
  --target-population "بیماران مبتلا به دردهای مزمن عضلانی-اسکلتی" \
  --output-docx "پروتکل_مداخله_اکت.docx" \
  --output-json "protocol_act.json"
```

### Defense Presentation Compilation (PowerPoint .pptx):
```bash
python3 .agents/skills/persian-defense-presentation-builder/scripts/compile_defense_presentation.py \
  --json "defense_payload.json" \
  --output "جلسه_دفاع_پایان_نامه.pptx" \
  --theme academic_navy
```

### Journal Submission Collateral & Rebuttal Package Compilation:
```bash
# English Submission Package (ISI / Scopus Q1-Q4)
python3 .agents/skills/journal-submission-assistant/scripts/compile_submission_package.py \
  --json "submission_payload.json" \
  --out-dir "./submission_package_en" \
  --lang en

# Persian Submission Package (علمی-پژوهشی / ISC)
python3 .agents/skills/journal-submission-assistant/scripts/compile_submission_package.py \
  --json "submission_payload_fa.json" \
  --out-dir "./submission_package_fa" \
  --lang fa
```

### Systematic Review & Quantitative Meta-Analysis (PRISMA 2020 & Cochrane RoB 2):
```bash
# English Synthesis (Forest Plot, Funnel Plot, APA 7 Manuscript)
python3 .agents/skills/systematic-review-meta-analyst/scripts/meta_analysis_engine.py \
  --json "meta_analysis_payload.json" \
  --out-dir "./meta_analysis_output_en" \
  --lang en

# Persian Synthesis (علمی-پژوهشی / ISC)
python3 .agents/skills/systematic-review-meta-analyst/scripts/meta_analysis_engine.py \
  --json "meta_analysis_payload_fa.json" \
  --out-dir "./meta_analysis_output_fa" \
  --lang fa
```

### Monte Carlo Psychometric & Statistical Data Simulation (All Research Paradigms):
```bash
# 1. Instant Run via Research Presets (No JSON needed!)
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset hierarchical_regression --out-dir "./sim_reg"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset moderation_model1 --out-dir "./sim_mod"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset factorial_anova --out-dir "./sim_anova"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset mixed_split_plot --out-dir "./sim_rm"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset ancova_trial --out-dir "./sim_rct"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset logistic_diagnosis --out-dir "./sim_logistic"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset efa_battery --out-dir "./sim_efa"
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py --preset non_parametric_skewed --out-dir "./sim_np"

# 2. Custom Structural Equation Modeling (SEM) / CFA Mode
python3 .agents/skills/psychometric-data-simulator/scripts/simdat_engine.py \
  --mode sem \
  --json "sem_simulation_payload.json" \
  --out-dir "./simulated_sem_data" \
  --seed 42
```

### Qualitative Data Analysis & Chapter 4 Reporting (Thematic Analysis & Grounded Theory):
```bash
# Reflexive Thematic Analysis (Braun & Clarke 6-phase thematic network)
python3 .agents/skills/qualitative-data-analyst/scripts/qualitative_engine.py \
  --json "thematic_payload.json" \
  --out-dir "./qualitative_output_thematic" \
  --lang fa

# Grounded Theory (Strauss & Corbin 6-dimension paradigmatic model)
python3 .agents/skills/qualitative-data-analyst/scripts/qualitative_engine.py \
  --json "grounded_theory_payload.json" \
  --out-dir "./qualitative_output_gt" \
  --lang fa
```

### Chapter 2 Literature Review & Empirical Matrix Compilation:
```bash
python3 .agents/skills/persian-literature-review-builder/scripts/literature_review_engine.py \
  --json "ch2_payload.json" \
  --out-dir "./chapter2_output" \
  --lang fa
```

### Psychometric Scale Standardization & Validation:
```bash
python3 .agents/skills/psychometric-scale-validator/scripts/psychometric_validator_engine.py \
  --json "validation_payload.json" \
  --out-dir "./psychometric_validation_output" \
  --lang fa
```

### Master Thesis Compilation:
```bash
python3 .agents/skills/persian-thesis-builder/scripts/compile_full_thesis.py \
  --template "path/to/template.docx" \
  --output "Thesis_Compiled.docx" \
  --ch1 "Chapter1.docx" \
  --ch2 "Chapter2.docx" \
  --ch3 "Chapter3.docx" \
  --ch4 "Chapter4.docx" \
  --ch5 "Chapter5.docx" \
  --refs "References_Compiled.docx" \
  --scales "Connor-Davidson Resilience Scale, Penn State Worry Questionnaire"
```

### Questionnaire Lookup & Factor Scoring:
```bash
# Search Registry (Questionnaires.xlsx) & Google Drive Library
python3 .agents/skills/psychometric-scale-resolver/scripts/questionnaire_resolver.py search "Connor-Davidson"

# Inspect Scale Scoring Profile, Subscales, and Reverse Keys
python3 .agents/skills/psychometric-scale-resolver/scripts/questionnaire_resolver.py profile "Penn State Worry Questionnaire"

# Score Raw Survey Item Responses into Factors and Scale Composites
python3 .agents/skills/psychometric-scale-resolver/scripts/questionnaire_resolver.py score \
  --data "survey_raw.xlsx" \
  --scale "Penn State Worry Questionnaire" \
  --prefix "Q" \
  --out "survey_scored.xlsx"
```

### Run Automated Statistical Suite:
```bash
python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py \
  --data "path/to/data.xlsx" \
  --task auto \
  --config "path/to/config.json" \
  --out "stats_results.json"
```

### Run Specific Statistical Tasks:
- **Score Scale & Factors**:
  `python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py --data data_raw.xlsx --task score_scale --scale "Connor-Davidson Resilience Scale" --prefix "Q" --out-scored data_scored.xlsx`
- **Descriptives & Normality**:
  `python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py --data data.xlsx --task descriptives --vars "Pre_Test,Post_Test,Resilience"`
- **Scale Reliability ($\alpha$)**:
  `python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py --data data.xlsx --task reliability --items "Q1,Q2,Q3,Q4,Q5"`
- **Intervention ANCOVA**:
  `python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py --data data.xlsx --task ancova --dv Post_Test --group Group --covar Pre_Test`
- **Hierarchical Regression**:
  `python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py --data data.xlsx --task regression --dv Outcome --step1 "Age,Gender" --step2 "Resilience,Self_Efficacy"`
- **Bootstrap Mediation (Model 4)**:
  `python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py --data data.xlsx --task mediation --x Stress --m Resilience --y Depression --bootstraps 2000`

### Generate APA 7 Persian Word Document:
```bash
python3 .agents/skills/statistical-data-analyst/scripts/generate_apa_docx.py \
  --json "stats_results.json" \
  --out "فصل چهارم: یافته‌های پژوهش.docx" \
  --mode chapter4
```

### End-to-End Academic Pipeline Orchestration:
```bash
# 1. Run turnkey pipeline preset (thesis_empirical, scale_validation, qualitative_study, meta_analysis, thesis_to_publication, bibliometric_pipeline)
python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --pipeline thesis_empirical \
  --out-dir "./my_thesis_project"

# 2. Run turnkey bibliometric preset (harvest -> bibliometrics -> historiography -> article -> submission)
python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --pipeline bibliometric_pipeline \
  --out-dir "./my_bibliometric_project" \
  --lang fa

# 3. Dry-run validation (inspect execution plan and dependency DAG without running)
python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --pipeline bibliometric_pipeline \
  --dry-run

# 4. Custom project configuration with custom step payloads
python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --config "project_config.json" \
  --out-dir "./custom_academic_study"

# 5. Granular checkpointing & step control
python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --pipeline thesis_empirical \
  --out-dir "./my_thesis_project" \
  --resume-from statistics

python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --pipeline thesis_empirical \
  --out-dir "./my_thesis_project" \
  --step discussion
```

### Thesis Integrity & Cross-Chapter Forensic Audit:
```bash
# Persian Audit (گزارش ممیزی رساله، همخوانی فرضیات و درجات آزادی، و تطبیق مراجع)
python3 .agents/skills/thesis-integrity-auditor/scripts/audit_engine.py \
  --json "audit_payload.json" \
  --out-dir "./thesis_audit_results" \
  --lang fa

# English / ISI Audit Mode
python3 .agents/skills/thesis-integrity-auditor/scripts/audit_engine.py \
  --json "audit_payload.json" \
  --out-dir "./thesis_audit_results_en" \
  --lang en
```

### G*Power Sample Size & Statistical Power Calculation:
```bash
# 1. ANCOVA Sample Size Determination (Chapter 3 Methodology Text & Power Curve)
python3 .agents/skills/gpower-sample-size-calculator/scripts/gpower_engine.py \
  --test ancova \
  --groups 2 \
  --covariates 1 \
  --power 0.85 \
  --effect-size 0.25 \
  --out-dir "./sample_size_ancova" \
  --lang fa

# 2. Multiple Linear Regression Sample Size Determination
python3 .agents/skills/gpower-sample-size-calculator/scripts/gpower_engine.py \
  --test regression \
  --predictors 3 \
  --power 0.80 \
  --effect-size 0.15 \
  --out-dir "./sample_size_regression" \
  --lang fa

# 3. Comprehensive Multi-Design & SEM Power Analysis via JSON Payload
python3 .agents/skills/gpower-sample-size-calculator/scripts/gpower_engine.py \
  --json "gpower_payload.json" \
  --out-dir "./gpower_results" \
  --lang fa
```

#### Run Academic Tone Polisher & Anti-AI Refiner (Skill #22):
```bash
python3 .agents/skills/ai-academic-tone-polisher/scripts/tone_polisher_engine.py \
  --json .agents/skills/ai-academic-tone-polisher/examples/sample_ai_text_payload.json \
  --sample persian_draft \
  --out-dir "./tone_results" \
  --lang fa
```

#### Run Literature Harvester & Empirical Metadata Extractor (Skill #23):
```bash
python3 .agents/skills/literature-harvester/scripts/harvester_engine.py \
  --query "درمان مبتنی بر پذیرش و تعهد انعطاف‌پذیری روان‌شناختی فرسودگی شغلی" \
  --out-dir "./harvested_ch2" \
  --limit 10 \
  --lang fa
```

#### Run Bibliometric Science Mapping & Network Analyst (Skill #24):
```bash
python3 .agents/skills/bibliometric-network-analyst/scripts/bibliometric_engine.py \
  --input .agents/skills/bibliometric-network-analyst/examples/sample_bibliometric_payload.json \
  --output-dir "./biblio_results" \
  --language fa \
  --min-freq 1 \
  --top-n 30
```

#### Run Citation Network Visualizer & Main Path Analysis (Skill #25):
```bash
python3 .agents/skills/citation-network-visualizer/scripts/citation_visualizer_engine.py \
  --input .agents/skills/citation-network-visualizer/examples/sample_citation_network_payload.json \
  --output-dir "./historiography_results" \
  --language fa \
  --main-path global
```

#### Run Digital Twin Academic Consultant & Telegram Bot (Skill #26):
```bash
# 1. Analyze proposal and generate itemized quote in Tomans
python3 .agents/skills/digital-twin-academic-consultant/scripts/proposal_price_estimator.py \
  --input /path/to/proposal.docx \
  --telegram-card --admin

# 2. Ingest Telegram export to calibrate consulting FAQs
python3 .agents/skills/digital-twin-academic-consultant/scripts/telegram_chat_analyzer.py \
  --input /path/to/result.json --update-persona

# 3. Run MTProto userbot listener & Google Drive project manager
python3 .agents/skills/digital-twin-academic-consultant/scripts/telethon_userbot.py --listen

# 4. List or sync managed projects in Google Drive
python3 .agents/skills/digital-twin-academic-consultant/scripts/telethon_userbot.py --list-projects
```

#### Run Academic Drive Project Organizer (Skill #27):
```bash
# 1. Audit Pending Works and identify loose files & fragmented folders
python3 .agents/skills/academic-drive-project-organizer/scripts/organize_drive_projects.py \
  --audit -o .agents/skills/academic-drive-project-organizer/references

# 2. Cross-reference Duzen milestones and generate Master Catalog (.xlsx and .md)
python3 .agents/skills/academic-drive-project-organizer/scripts/organize_drive_projects.py \
  --sync-duzen -o .agents/skills/academic-drive-project-organizer/references

# 3. Tidy a project folder into the 4-tier taxonomy (dry-run first, then apply)
python3 .agents/skills/academic-drive-project-organizer/scripts/organize_drive_projects.py \
  --tidy --project "Client Name" --apply --clean-junk

# 4. Provision a new standard project folder
python3 .agents/skills/academic-drive-project-organizer/scripts/organize_drive_projects.py \
  --new-project "Client Name" --topic "Topic"
```

---

## 5. Defense Committee Quality Checklist

Before delivering any Chapter 4 or statistical output to a student, verify:
- [ ] Normality (Shapiro-Wilk) and Homogeneity of Variance (Levene) were formally checked and reported.
- [ ] For experimental studies, ANCOVA slope homogeneity ($Group \times Pretest$, $p > .05$) was tested.
- [ ] For mediation models, 95% bootstrap confidence intervals were reported (not Sobel test).
- [ ] All table numbers in the narrative match the table captions (`جدول ۱-۴`, `جدول ۲-۴`).
- [ ] All tables contain only 3 horizontal lines (no vertical lines).
- [ ] All $p$-values omit the leading zero ($p = .012$, not $p = 0.012$).
- [ ] Every hypothesis has an unambiguous concluding sentence affirming or rejecting it.

---

## 6. Questionnaire Registry & Psychometric Scale Directives

When preparing datasets, writing research proposals, or drafting methodology chapters:
1. **3-Tier Hierarchy**:
   - **Tier 1 (Project Folder)**: Prioritize client-provided questionnaires and project files.
   - **Tier 2 (Excel Registry - `Questionnaires.xlsx`)**: 4,880 rows mapping English/Persian names, subscales, items, Likert anchors, theoretical means, and reverse items.
   - **Tier 3 (Google Drive Library - `Pending Works/Questionnaire`)**: 2,206 original `.pdf`, `.docx`, and `.doc` instruments for item texts and scoring manuals.
2. **Reverse Scoring Formula**:
   - Always transform negatively keyed items using $Item_{\text{rev}} = (Min + Max) - Item$ before computing subscale sums, means, or Cronbach's alpha.
3. **Subscale & Total Composite Reporting**:
   - Report Cronbach's $\alpha$ for each subscale and total scale separately.
   - Confirm theoretical score ranges and midpoints ($Mean_{\text{theor}} = \frac{Min + Max}{2}$) in the narrative.

---

## 7. Digital Twin Academic Consultant & Telegram Operations

When operating the Telegram consultant daemon or handling client interactions:
1. **Proposal Ingestion & Extraction**: Support `.docx`, `.pdf`, and direct text proposals. Deterministically parse the research title, degree level, research design, sample size $N$ (normalizing Persian/Arabic digits), questionnaires, and required statistical packages.
2. **Modular Itemized Pricing**: Pricing quotations must be calculated and itemized in Tomans across standard phases (Chapter 3 Methodology, SimDat Data Simulation, Chapter 4 Statistics, Chapter 5 Discussion, Defense Slides, Integrity Audit) so students can commission individual modules or complete bundles.
3. **Telegram Message Layout**: Always format quotation cards with standard emojis, clear section dividers, itemized breakdowns in Tomans, and candidate guarantees (APA 7 compliance, free revisions for supervisor comments).
4. **Admin Approval Desk**: All draft quotations generated from proposals must be routed to Saber's Admin Desk (`124911145`) with actionable commands (`/approve_<ID>`, `/adjust_<ID>_<price>`) before final delivery.
5. **Persona & FAQ Calibration**: Periodically ingest Telegram Desktop exports (`result.json`) via `telegram_chat_analyzer.py --update-persona` to calibrate FAQs and ensure authentic reflection of Saber's consulting style.

