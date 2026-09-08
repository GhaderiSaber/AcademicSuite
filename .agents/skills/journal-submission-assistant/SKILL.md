---
name: journal-submission-assistant
description: >-
  Expert academic journal submission collateral and peer-review rebuttal packaging skill.
  Prepares comprehensive submission files for international (ISI, Scopus Q1–Q4, Web of Science, PubMed)
  and Iranian (علمی-پژوهشی / ISC) journals. Generates formal Cover Letters to the Editor-in-Chief,
  Title Pages with standard 14 CRediT authorship taxonomy roles and ethical declarations, Highlights strictly
  validated to <= 85 characters, Data Availability Statements, and APA 7 Point-by-Point Response to Reviewers
  rebuttal tables for Revise & Resubmit (R&R) decisions.
---

# Academic Journal Submission Assistant Skill (دستیار ارسال مقاله و پاسخ به داوران ژورنال)

This skill equips Antigravity to act as an elite journal submission coordinator and peer-review strategist. It transforms completed research papers (such as those drafted by `academic-article-writer`) into submission-ready, publisher-compliant collateral packages.

Major international publishers (Elsevier, Springer Nature, Wiley, Taylor & Francis, Frontiers, MDPI, APA, PLOS, SAGE) and Iranian scientific universities (سامانه سیناوب / نشریات وزارت علوم و بهداشت) reject up to 30% of submissions at the initial administrative screening (desk reject / return to author) due to missing or non-compliant collateral. This skill eliminates administrative desk-rejections and maximizes acceptance probability during peer review.

---

## 1. When to Activate This Skill

Activate this skill when:
1. **Initial Journal Submission**:
   - The user has a drafted manuscript (`.docx`) and needs to create the required ancillary submission files: **Cover Letter**, **Title Page**, **Highlights**, **Declarations**, or **Suggested Reviewers**.
   - The user needs to formalize author contributions using the international **CRediT (Contributor Roles Taxonomy)** standard.
   - The user needs 3–5 bulleted **Highlights** strictly conforming to publisher character constraints ($\le 85$ characters per bullet including spaces).
2. **Revised Submission / Revise & Resubmit (R&R)**:
   - The user receives an Editor's decision letter with Reviewer comments (Minor Revision or Major Revision).
   - The user needs to construct a courteous, scholarly, and rigorous **Point-by-Point Response to Reviewers (جدول پاسخ به نظرات داوران ژورنال)**.
   - The user needs to draft the formal Rebuttal Cover Letter to the Editor-in-Chief.

---

## 2. Submission Collateral Architecture

```
                                [Manuscript Draft]
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 ▼                                               ▼
     [Initial Submission Package]                    [Revision / Rebuttal Package]
     ├── 1. Cover Letter to Editor-in-Chief          ├── 1. Rebuttal Letter to Editor
     ├── 2. Title Page & CRediT Taxonomy             ├── 2. Point-by-Point Response Table
     ├── 3. Highlights (<= 85 chars/bullet)          ├── 3. Marked-Up Manuscript (Track Changes)
     ├── 4. Mandatory Declarations (Ethics/Data)     └── 4. Clean Revised Manuscript
     └── 5. Suggested / Excluded Reviewers
```

---

## 3. Core Deliverables & Technical Specifications

### Deliverable A: Cover Letter to the Editor-in-Chief
A persuasive, professional 1-page letter addressed to the journal's Editor-in-Chief.
- **Header**: Institutional affiliation, date, journal title, publisher, Editor-in-Chief name.
- **The Hook**: Clear statement of manuscript title, article type (e.g., Original Research Article), and core clinical/theoretical problem addressed.
- **Key Findings & Novelty**: 2–3 sentences highlighting primary empirical findings (e.g., ANCOVA effect size, mediation path, clinical significance).
- **Fit with Journal Aims & Scope**: Explicitly connects the study's themes to the journal's stated editorial mission and recent published discourse.
- **Mandatory Assurances**:
  1. Original work, not previously published, not under consideration elsewhere.
  2. Institutional Ethics Committee / IRB approval with formal protocol/code.
  3. Written informed consent obtained from all human participants.
  4. All authors have read and approved the final manuscript and agree with submission.
  5. No conflicts of interest to disclose.
- **Sign-Off**: Corresponding author name, title, department, institution, email, phone.

### Deliverable B: Title Page with CRediT Authorship Taxonomy
Separating the title page from the blinded main text is required for double-anonymous peer review.
- **Metadata**: Full title, running head ($\le 50$ characters), author names, affiliations, superscript mapping.
- **Corresponding Author**: Full contact details, postal address, email, telephone, ORCID.
- **Word Counts**: Abstract word count, main text word count, number of tables, number of figures, number of references.
- **CRediT Contributor Roles**: Evaluates each author across the 14 standard roles:
  - *Conceptualization, Data curation, Formal analysis, Funding acquisition, Investigation, Methodology, Project administration, Resources, Software, Supervision, Validation, Visualization, Writing – original draft, Writing – review & editing*.
- **Declarations & Statements**:
  - *Funding Statement*: Grant number, funding agency, or "This research received no external funding."
  - *Conflicts of Interest*: Explicit disclosure.
  - *Ethics Approval*: Ethics Committee name, institution, approval reference code (e.g., `IR.SBMU.RETECH.REC.1402.045`).
  - *Consent to Participate & Consent for Publication*.
  - *Data Availability Statement*: e.g., "The datasets generated and analyzed during the current study are available from the corresponding author upon reasonable request" or repository DOI.
  - *Acknowledgments*: Non-author contributors, lab assistants, or participating clinical centers.

### Deliverable C: Research Highlights
Bullet points designed for indexing, discoverability, and search engines.
- **Hard Rule**: Exactly 3 to 5 bullet points.
- **Hard Rule**: **Maximum 85 characters per bullet**, including spaces, letters, and punctuation.
- *Tip*: Highlight the population, core intervention, key statistical effect, and clinical mechanism.

### Deliverable D: Point-by-Point Response to Reviewers (Rebuttal Package)
For Revise & Resubmit (R&R) submissions:
- **Tone & Etiquette**: Courteous, appreciative, non-defensive, intellectually humble. Always thank the reviewer for identifying areas of ambiguity.
- **Three-Part Rebuttal Structure**:
  1. *Reviewer Comment*: Quoted verbatim in bold or shaded container.
  2. *Author Response*: Scholarly explanation of the conceptual or empirical reasoning and how the concern was addressed.
  3. *Action & Manuscript Location*: Exact page numbers, line numbers, and excerpted block of modified/added text.

---

## 4. Execution Workflow

### Step 1: Ingest Project Information
Identify whether the task is an **initial submission** or a **revision rebuttal**. Harvest relevant details from:
- Draft manuscript or thesis files (`.docx`)
- Statistical outputs (`stats_results.json`)
- Author details, affiliations, and target journal name
- (If revision) Reviewer comments letter / email

### Step 2: Assemble JSON Payload
Create or update `submission_payload.json` matching the schema in `examples/sample_submission_payload.json`. Ensure:
- All 14 CRediT roles are verified.
- Highlights are tested to be $\le 85$ characters each.
- Ethics codes and data statements are populated.

### Step 3: Compile via Automated CLI
Run the Python compilation engine:
```bash
python3 .agents/skills/journal-submission-assistant/scripts/compile_submission_package.py \
  --json submission_payload.json \
  --out-dir ./submission_files \
  --lang en
```
For Iranian Scientific-Research (ISC) journals, use `--lang fa`:
```bash
python3 .agents/skills/journal-submission-assistant/scripts/compile_submission_package.py \
  --json submission_payload_fa.json \
  --out-dir ./submission_files_fa \
  --lang fa
```

### Step 4: Quality & Compliance Audit
Inspect generated documents:
1. `Cover_Letter.docx`: Check greeting, novelty statement, ethics declaration, and signature block.
2. `Title_Page.docx`: Verify author affiliations, ORCID links, CRediT statements, and word count.
3. `Highlights.docx`: Confirm each bullet does not exceed 85 characters.
4. `Response_to_Reviewers.docx`: Confirm clean APA 7 borders, clear reviewer quotation formatting, and explicit page/line citations.
