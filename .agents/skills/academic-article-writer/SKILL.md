---
name: academic-article-writer
description: >-
  Expert academic journal article drafting and compilation skill for psychology, behavioral sciences, and social sciences.
  Harvests heterogeneous research artifacts from the project folder (full thesis, proposal, translated literature,
  SPSS/Excel statistical results, psychometric scales, and Questionnaires.xlsx) to compose publication-ready,
  high-impact peer-reviewed journal manuscripts adhering to international IMRaD and APA 7th Edition standards
  for both International English journals (ISI, Scopus Q1/Q2, Web of Science) and Iranian Scientific-Research
  journals (علمی-پژوهشی / ISC).
---

# Academic Journal Article Writer Skill (نگارش و تدوین مقالات علمی-پژوهشی و ISI)

This skill empowers Antigravity to act as an elite academic author and peer-reviewed journal strategist. It synthesizes modular thesis chapters, translated theoretical literature, and statistical findings into **high-impact, publication-grade academic journal articles (15–25 pages, 4,500–6,500 words)**.

It adheres strictly to **IMRaD architecture (Introduction, Method, Results, and Discussion)**, **APA 7th Edition**, and **JARS (Journal Article Reporting Standards)**, supporting both **International English journals (ISI / Scopus)** and **Iranian Scientific-Research journals (علمی-پژوهشی / ISC)**.

---

## 1. When to Activate This Skill

Activate this skill when:
1. The user asks to **write a journal article (مقاله پژوهشی / مقاله ISI / ISC)** based on a completed thesis, dissertation, or raw project data.
2. The user has **Chapter 4 statistical data (`stats_results.json`)** and source literature and wants to compose an empirical research paper.
3. The user needs to condense an exhaustive 150-page thesis into a high-density, peer-review-ready manuscript.
4. The user needs a structured abstract (Background, Objective, Method, Results, Conclusion), MeSH keywords, or APA 7 borderless tables for a journal submission.

---

## 2. Multi-Source Project Ingestion Architecture

The agent systematically scans the active project folder to harvest and condense inputs into the IMRaD framework:

```
┌──────────────────────────────────────┐     ┌────────────────────────────────────┐
│      Proposal / Chapters 1 & 3       │     │     Translated Literature (Ch 2)   │
│ - Societal & clinical problem burden │     │ - Conceptual & theoretical models  │
│ - Specific objectives & hypotheses   │     │ - Recent (2021-2026) empirical lit │
│ - Population, G*Power, instruments   │     │ - International & Iranian studies  │
└──────────────────┬───────────────────┘     └─────────────────┬──────────────────┘
                   │                                           │
                   ▼                                           ▼
          [1. INTRODUCTION]                           [4. DISCUSSION]
          - 4-Paragraph Funnel                        - Theoretical mechanisms
          - Critical research gap                     - Global lit comparison
          - Explicit hypotheses                       - Practical implications
                   │                                           ▲
                   ▼                                           │
             [2. METHOD]                                       │
          - G*Power sample size                                │
          - Psychometric properties                            │
          - Statistical analysis plan                          │
                   │                                           │
                   ▼                                           │
            [3. RESULTS] ──────────────────────────────────────┘
          - Descriptives & Normality
          - 3-4 High-Information APA Tables (ANCOVA / Regression / SEM)
          - Bootstrap 95% Confidence Intervals
```

---

## 3. Dual Publication Tracks

| Feature | **Track A: International English (ISI / Scopus)** | **Track B: Iranian ISC (علمی-پژوهشی)** |
| :--- | :--- | :--- |
| **Language & Tone** | Formal Academic English (C1/C2 vocabulary). | Polished Academic Persian (ادبیات فاخر علمی). |
| **Typography** | `Times New Roman` 12 pt, 1.5/Double-spaced, 1-inch margins. | `B Titr` 14 pt Bold (Headings), `B Nazanin` 12 pt Regular. |
| **Abstract** | English Structured Abstract (200–250 words) + Keywords. | Bilingual: Persian چکیده + Latin Abstract page. |
| **Target Journals** | Elsevier, Springer, Frontiers, Wiley, Taylor & Francis. | مجلات علمی-پژوهشی دانشگاه تهران، شهید بهشتی، خوارزمی و... |

---

## 4. Execution Workflow

### Step 1: Ingest Project Data, Literature Corpus & Select Track
Inspect the project directory to locate:
- Statistical output: `stats_results.json` or `فصل چهارم: یافته‌های پژوهش.docx`.
- Methodological details: `پروپوزال_طرح_پژوهش.docx` or Chapter 3.
- **Physical Research Papers & Anti-Hallucination Protocol (`04_references_and_lit/papers/`)**:
  - **MANDATORY DIRECTIVE (Zero Ghost Citations / قاعده ضد استناد توهمی)**: If the agent uses generative memory to reference an article or author in the manuscript, the agent **MUST NOT** leave it as an ungrounded citation. The agent must execute `verify_and_download_citation.py` or `paper_downloader.py` to:
    1. Confirm the authentic existence of the paper in scientific registries (CrossRef / OpenAlex / Europe PMC).
    2. Download the legal, full-text Open-Access PDF directly into `04_references_and_lit/papers/`.
    3. Cross-validate the drafted manuscript sentence against the paper's actual abstract and empirical findings to ensure 100% directional and statistical alignment.
    ```bash
    python3 .agents/skills/academic-article-writer/scripts/verify_and_download_citation.py \
      --query "Author Year Title" \
      --claim "The drafted sentence to be verified against the abstract" \
      --out-dir "04_references_and_lit/papers"
    ```
  - Run `python3 .agents/skills/academic-reference-extractor/scripts/local_paper_extractor.py --dir "04_references_and_lit/papers"` to generate `ingested_papers_corpus.json`.
  - Ground all external citations and mechanism comparisons strictly in these physical, verified PDFs.
- Theoretical literature: `Translate/` folder or Chapter 2.
- Psychometric instruments: Ingest from project files or query `Questionnaires.xlsx` and the Google Drive master library via `questionnaire_resolver.py search "<scale_name>"` for verified item counts, subscale factors, and Likert anchors.
- Discussion points: Chapter 5.

Confirm the target language track (`--lang en` for International ISI/Scopus, or `--lang fa` for Iranian ISC).

### Step 2: Consult Quality Benchmarks
- Read [imrad_quality_benchmarks.md](file:///Users/saber/Desktop/academic_suite/.agents/skills/academic-article-writer/references/imrad_quality_benchmarks.md) for international peer-review standards.
- Read [article_abstract_and_title_guide.md](file:///Users/saber/Desktop/academic_suite/.agents/skills/academic-article-writer/references/article_abstract_and_title_guide.md) for title formulas and structured abstract formatting.

### Step 3: Formulate Article Content JSON
Prepare a structured JSON file containing the condensed, high-density scientific prose for each section:
- `title`: High-impact title without filler words.
- `authors` & `affiliation`: Author names and institutional department.
- `abstract`: Structured dictionary (`background`, `objective`, `methods`, `results`, `conclusion`).
- `keywords`: 4–6 controlled terms (MeSH / APA Thesaurus).
- `introduction`: 4-paragraph funnel.
- `method`: Design, G*Power sample size, measures with sample items and $\alpha$, procedure, analysis plan.
- `results`: Narrative + 3–4 APA 7 tables.
- `discussion`: Theoretical mechanisms, empirical comparisons, implications, limitations, conclusion.
- `claims_matrix` (Optional but Recommended): Structured list of empirical claims adhering to `.agents/shared/schemas/claim_evidence.schema.json`. Each entry contains `claim_id`, `claim_statement`, `evidence_source`, `statistical_support`, `confidence_tier` (`CONFIRMED`, `PROVISIONAL`, `EXPLORATORY`), and `potential_counter_argument`.
- `references`: APA 7th edition bibliography.

### Step 4: Compile Journal-Ready Word Document
Execute the compiler script:
```bash
# For International English Manuscript (ISI / Scopus):
python3 .agents/skills/academic-article-writer/scripts/compile_academic_article.py \
  --json "article_payload.json" \
  --out "Academic_Article_Manuscript.docx" \
  --lang en

# For Iranian Scientific-Research Manuscript (ISC / علمی-پژوهشی):
python3 .agents/skills/academic-article-writer/scripts/compile_academic_article.py \
  --json "article_payload_fa.json" \
  --out "مقاله_علمی_پژوهشی_نهایی.docx" \
  --lang fa
```
*Note: If `claims_matrix` is present, the compiler exports a companion `<output>_claim_evidence_matrix.xlsx`. If `figures` are present, it exports `<output>_figure_planning_matrix.xlsx` and embeds the visual assets with APA 7 captions.*

### Step 5: Visual Assets & Figure-First Embedding Invariant
For every structural equation model, mediation path, or empirical chart:
1. **Crop Excess Margins**: Tightly crop whitespace and margins from raw plots to maximize diagram legibility in Word.
2. **Export 300-DPI Standalone Assets**:
   - `Figure_X.png` (lossless PNG, 300 DPI)
   - `Figure_X.tif` (LZW-compressed TIFF for Elsevier/Springer journal portals)
   - `Figure_X.pdf` (vector/high-res PDF)
3. **Embed Directly into Word Manuscript (Rule 5.4)**:
   - Line 1: **Figure X** (bold, flush left, 12 pt Times New Roman)
   - Line 2: *Figure Title* (italic, title case, flush left, 12 pt Times New Roman)
   - Line 3: Centered image scaled to 6.2 inches wide (leaving 1-inch margins)
   - Line 4: *Note.* Explanatory text, abbreviations, and goodness-of-fit indices (10 pt regular, justified)
4. **OpenXML Preservation**: When revising documents containing figures, never call `paragraph.text = "..."` naively, which permanently destroys `<w:drawing>` and `<a:blip>`. Always check `bool(paragraph._p.xpath('.//w:drawing') or paragraph._p.xpath('.//a:blip'))`.

### Step 6: EndNote 360° Publishing Pipeline (Rule 16)
Every English manuscript prepared for peer-reviewed journal submission must execute `generate_endnote_suite.py` to produce:
1. **`EndNote_Library_Article.enw`**: Structured EndNote tags (`%0`, `%T`, `%A`, `%D`, `%J`, `%V`, `%N`, `%P`, `%R`, `%U`, `%M`) with accent normalization (`strip_accents`).
2. **`EndNote_Library_Article.ris`**: Standard RIS format for universal compatibility (EndNote, Zotero, Mendeley).
3. **`[Manuscript]_EndNote_CWYW.docx`**: Word document containing live dynamic Cite-While-You-Write fields (`ADDIN EN.CITE` with embedded Traveling Library XML) and an `ADDIN EN.REFLIST` bibliography.
4. **`[Manuscript]_EndNote_Unformatted.docx`**: Word document containing temporary `{Author, Year #RecNum}` markers for 1-click bibliographic reformatting.
5. **`[Manuscript].docx`**: Clean APA 7 submission version with styled text citations and borderless tables.

---

## 5. Claim-Evidence Traceability & Figure-First Planning

Inspired by Prof. Sida Peng's research auditing methodology and Nature/MedSci Figure-First publishing standards:
1. **Claim-Evidence Mapping**: Every substantive empirical claim in the Introduction and Discussion must link directly to a specific table, figure, or statistical parameter ($F, t, p, \eta_p^2, \beta$), documented in `claim_evidence_matrix.xlsx`.
2. **Figure-First Visual Evidence Planning**:
   - Science is communicated through figures: every primary hypothesis must have a corresponding visual representation (e.g. CONSORT flowchart, PRISMA flow diagram, pre-post interaction plot, or group comparison with significance brackets).
   - The compiler automatically exports `<output>_figure_planning_matrix.xlsx` mapping Figure ID, Title, Supported Claim, Statistical Parameter, Subpanels, and Asset Disk Status (`VERIFIED & EMBEDDED` vs `PENDING GENERATION`).
3. **Pre-Flight Submission Readiness Score (SRS: 0–100%)**:
   - Evaluates IMRaD completeness (40%), claim backing (25%), figure-first visual evidence (20%), and APA 7 typography (15%).
   - Outputs an editorial grade ($A+, A, B, C$) and diagnosis prior to submission.

---

## 6. Peer-Review Submission Quality Checklist

Before submitting the manuscript to an academic journal, verify:
- [ ] Title contains independent, mediator, and dependent variables without fluff.
- [ ] Abstract word count is strictly between 200 and 250 words.
- [ ] Method section includes a formal G*Power 3.1 sample size justification.
- [ ] For every psychometric instrument, Cronbach's $\alpha$ from the current study and sample items are reported.
- [ ] All tables strictly adhere to APA 7: zero vertical borders, 3 horizontal borders, table captions above, notes below.
- [ ] **Figure Embedding & OpenXML Image Preservation**: Planned figures are physically embedded with APA 7 numbering above and explanatory notes below. Standalone 300-DPI files (`.png`, `.tif`, `.pdf`) are exported in the submission package. All Word document edits verify and preserve `<w:drawing>` and `<a:blip>`.
- [ ] **EndNote 360° Publishing Integration (Rule 16)**: Deliverables include companion `.enw` and `.ris` libraries, live CWYW Word document (`ADDIN EN.CITE` + `ADDIN EN.REFLIST`), and unformatted temporary citation document (`{Author, Year #RecNum}`).
- [ ] Discussion explicitly explains the *psychological and theoretical mechanisms* (e.g., Beck, Bandura, Gross) rather than simply repeating statistical figures.
- [ ] Major empirical claims are mapped to evidence sources via `claim_evidence_matrix.xlsx`.
- [ ] Figure planning matrix (`figure_planning_matrix.xlsx`) confirms all visual evidence files are generated and verified.
- [ ] Pre-flight Submission Readiness Score (SRS) achieves Grade A ($\ge 80\%$) or Grade A+ ($\ge 90\%$).
- [ ] Every in-text citation matches an entry in the References list (and vice versa).
- [ ] **Anti-Hallucination & Physical PDF Verification**: Every cited paper is deposited in `04_references_and_lit/papers/` (or possesses a verified registry DOI), and all narrative claims in the text are verified to strictly align with the paper's genuine empirical findings (zero fabricated conclusions or phantom citations).
- [ ] **Word OMML Math Preservation (Rule 5)**: If editing an existing manuscript, never use naive `p.text = "..."` replacement. Verify native Word math formulas (`<m:oMath>`) are preserved intact and extract visible text using `"".join([e.text or "" for e in p._p.iter() if e.tag.endswith("}t")])`.
