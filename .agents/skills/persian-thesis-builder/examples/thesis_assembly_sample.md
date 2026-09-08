# Example Thesis Assembly Workflow
## Benchmark Execution Walkthrough

This document demonstrates a concrete end-to-end scenario executing the `persian-thesis-builder` skill on an academic thesis project, detailing the input files, commands, and intermediate/final outputs at each stage.

---

## 1. Project Directory Structure

The project environment is structured modularly:

```
Thesis_Project/
├── University_Template.docx                 # Institutional Master Template (Cover, Styles, TOC)
├── Research_Proposal.docx                   # Approved Research Proposal (Chapters 1 & 3)
├── Chapter 4.docx                           # Statistical Results & APA Borderless Tables
├── Chapter 5.docx                           # Psychological Discussion & Hypothesis Testing
├── Translate/                               # Translated Literature & Theoretical Frameworks
│   ├── Construct1_fa.docx
│   ├── Construct2_fa.docx
│   └── References_Translate.txt
├── References_Compiled_APA.txt              # Unified Bilingual References (Persian & English)
└── Scored_Data.xlsx                         # Scored dataset with factor sums/means
```

---

## 2. Compilation Command

Run the consolidated compilation engine:

```bash
python3 .agents/skills/persian-thesis-builder/scripts/compile_full_thesis.py \
  --template "University_Template.docx" \
  --output "Thesis_Compiled.docx" \
  --ch1 "Research_Proposal.docx" \
  --ch2 "Translate/" \
  --ch3 "Research_Proposal.docx" \
  --ch4 "Chapter 4.docx" \
  --ch5 "Chapter 5.docx" \
  --refs "References_Compiled_APA.txt" \
  --scales "Connor-Davidson Resilience Scale, Penn State Worry Questionnaire" \
  --title-en "Effectiveness of Mindfulness on Academic Anxiety and Resilience" \
  --author-en "Student Name" \
  --supervisor-en "Supervisor Name, Ph.D."
```

### Generated Final Output:
- `Thesis_Compiled.docx`: Complete university thesis formatted with:
  1. Preserved front matter (cover, approval signatures, dedication, Persian abstract).
  2. Chapters 1–5 formatted with standard Persian typography (*B Titr*, *B Nazanin*), `<w:bidi>` directionality, and APA 7 borderless tables.
  3. Bilingual References divided into Persian (الف) and English (ب) with hanging indents.
  4. Dynamically generated questionnaire appendices with Likert tables and scoring notes.
  5. English abstract and back cover page.
