# Example Thesis Assembly Workflow
## Benchmark Execution Walkthrough

This document demonstrates a concrete end-to-end scenario executing the `persian-thesis-builder` skill on an academic thesis project, detailing the input files, commands, and intermediate/final outputs at each stage.

---

## 1. Project Directory Structure

The workspace environment is structured as follows:

```
Fada Talebi/
├── Example Thesis.docx                     # Institutional Master Template (Cover, Styles, TOC)
├── Proposal-Mrs Talebian.pdf               # Approved University Research Proposal
├── Chapter 4.docx                          # Statistical Results, APA Tables & SEM Models
├── Chapter 5.docx                          # Psychological Discussion & Hypothesis Testing
├── Translate/                              # Translated Literature & Citation Files
│   ├── PIU_Pages_13-44_fa.docx
│   ├── PIU_Pages_13-44_References_APA.txt
│   ├── Intolerance_of_Uncertainty_Pages_1-26_fa.docx
│   ├── Intolerance_of_Uncertainty_Pages_1-26_References_APA.txt
│   ├── Impulsivity_Pages_1-10_fa.docx
│   ├── Impulsivity_Pages_1-10_References_APA.txt
│   ├── Self_Efficacy_Pages_24-42_fa.docx
│   └── Self_Efficacy_Pages_24-42_References_APA.txt
└── Questionnaire/                          # Raw Psychometric Measurement Scales
    ├── GPIUS-2 (Caplan, 2010).pdf
    ├── IUS-12 (Carleton et al., 2007).doc
    ├── BIS-11 (Patton et al., 1995).doc
    └── GSE-10 (Schwarzer & Jerusalem, 1995).doc
```

---

## 2. Step-by-Step Execution Scenario

### Stage 1: Proposal Extraction
Command:
```bash
python scripts/extract_proposal_data.py \
    --proposal-pdf "g:\My Drive\My Work\Fada Talebi\Proposal-Mrs Talebian.pdf" \
    --output-dir "g:\My Drive\My Work\Fada Talebi\Proposal_Extracted"
```
Generated Outputs:
- `Chapter1_from_Proposal.md`: Contains Problem Statement (1-1), Significance (1-2), Objectives (1-3), Hypotheses (1-4), Definitions (1-5).
- `Chapter2_Empirical_from_Proposal.md`: Domestic and international empirical research.
- `Chapter3_from_Proposal.md`: Research design, 350-student sample, cluster sampling, 4 psychometric scales, SEM analysis plan in AMOS.
- `Proposal_References.txt`: Persian and English proposal reference list.

### Stage 2: Questionnaire Appendix Formatting
Command:
```bash
python scripts/format_questionnaires.py
```
Generated Output:
- `Questionnaires_Appendix.docx`: Formatted Word document containing the demographic questionnaire and 4 standard Likert-scale test tables with scoring guidelines.

### Stage 3: Bilingual Reference Aggregation
Command:
```bash
python scripts/compile_references.py \
    --translate-dir "g:\My Drive\My Work\Fada Talebi\Translate" \
    --proposal-refs "g:\My Drive\My Work\Fada Talebi\Proposal_Extracted\Proposal_References.txt" \
    --output-txt "g:\My Drive\My Work\Fada Talebi\References_Compiled_APA.txt" \
    --output-docx "g:\My Drive\My Work\Fada Talebi\References_Compiled.docx"
```
Generated Outputs:
- Produces bilingual bibliography separated into:
  - Part A: Persian References (الف) منابع فارسی) sorted alphabetically by Persian collation.
  - Part B: English References (References - English Sources) formatted according to APA 7th Edition, sorted A–Z.

### Stage 4: Master Thesis Compilation
Command:
```bash
python scripts/build_full_thesis.py
```
Generated Output:
- `Thesis_Compiled.docx`: Complete merged thesis containing all 5 chapters, bilingual references, questionnaires appendix, and English back matter, with institutional headers, styles, fonts (`B Titr`, `B Nazanin`), justified RTL text alignment, native Word footnotes with Persian numbers, and modern `compatibilityMode = 15`.
