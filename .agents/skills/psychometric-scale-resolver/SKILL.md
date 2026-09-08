---
name: psychometric-scale-resolver
description: >-
  Expert psychometric measurement and scale resolution skill for psychology and behavioral research. Searches and
  extracts questionnaire specifications, factor subscale structures, scoring methods (Likert ranges), theoretical means,
  and reverse-scoring keys from Questionnaires.xlsx (4,880 entries) and the Google Drive master library (2,206 documents).
  Automatically inverts negatively keyed items and computes subscale and total composite scores on raw survey response datasets.
---

# Psychometric Scale Resolver & Factor Scoring Skill (روان‌سنجی و نمره‌گذاری ابزارهای پژوهش)

This skill equips Antigravity with specialized **psychometric measurement and scale resolution** capabilities for academic research in psychology, counseling, educational sciences, and behavioral health.

It bridges the gap between raw, unstandardized survey item responses (`Q1..Q40`) and psychometrically validated constructs. By referencing the master **Questionnaire Registry** (`Questionnaires.xlsx`, 4,880 entries) and the **Google Drive Master Questionnaire Library** (2,206 original documents), it deterministically extracts factor structures, identifies reverse-scored items, applies inversion algebra, and computes subscale and composite scores.

---

## 1. When to Activate This Skill

Activate this skill when:
1. The user or another agent needs to **identify or verify a psychological questionnaire** (e.g. number of items, subscales, author, Likert response scale, theoretical mean).
2. The user has raw survey item data (`.xlsx`, `.csv`, `.sav`) and needs to **reverse negatively worded items** and **calculate subscale and total composite scores**.
3. Drafting the **"ابزارهای پژوهش" (Research Instruments)** section of a proposal (`persian-proposal-builder`) or the **Method $\to$ Measures** section of a journal article (`academic-article-writer`).
4. Generating questionnaire appendices (پیوست‌ها) for full thesis compilation (`persian-thesis-builder`).

---

## 2. The 3-Tier Questionnaire Resolution Hierarchy

Never guess item assignments or reverse-scoring keys. Follow this strict 3-tier lookup hierarchy:

```
[Target Psychological Variable / Scale Name]
                     │
                     ▼
       ┌───────────────────────────┐
       │ Tier 1: Project Folder    │ ──► Search local project questionnaires & proposal text
       └───────────────────────────┘
                     │ (If missing, incomplete, or unstandardized)
                     ▼
       ┌───────────────────────────┐
       │ Tier 2: Excel Registry    │ ──► Questionnaires.xlsx (4,880 rows)
       │                           │     ├── English & Persian names, Abbreviation
       │                           │     ├── Subscale names & Item lists (e.g. 10-12, 16-17, 23-25)
       │                           │     ├── Likert scoring range (1 to 5, 0 to 4, etc.)
       │                           │     ├── Min / Max / Theoretical mean
       │                           │     └── Reverse-scoring item keys (e.g. 1, 3, 8, 10, 11)
       └───────────────────────────┘
                     │ (If original instrument, item texts, or cutoffs needed)
                     ▼
       ┌───────────────────────────┐
       │ Tier 3: GDrive Library    │ ──► 2,206 original documents (.docx, .pdf, .doc)
       │                           │     └── /Pending Works/Questionnaire(s)/
       └───────────────────────────┘
```

---

## 3. Reverse-Scoring Formula & Linear Transformation

Negatively keyed items (e.g., "I feel hopeless" on a positive affect scale) must be reversed prior to computing subscale sums, means, and Cronbach's alpha.

### General Reversal Formula:
$$Item_{\text{reversed}} = (Min_{\text{item}} + Max_{\text{item}}) - Item_{\text{original}}$$

### Standard Likert Inversions:
| Scale Range | $Min$ | $Max$ | Transformation Formula | Example: Raw $1$ | Example: Raw $5$ |
| :---: | :---: | :---: | :--- | :---: | :---: |
| **1 to 5** | 1 | 5 | $Item_{\text{rev}} = 6 - Item$ | $6 - 1 = 5$ | $6 - 5 = 1$ |
| **0 to 4** | 0 | 4 | $Item_{\text{rev}} = 4 - Item$ | $4 - 0 = 4$ | $4 - 4 = 0$ |
| **1 to 7** | 1 | 7 | $Item_{\text{rev}} = 8 - Item$ | $8 - 1 = 7$ | $8 - 7 = 1$ |
| **0 to 3** | 0 | 3 | $Item_{\text{rev}} = 3 - Item$ | $3 - 0 = 3$ | $3 - 3 = 0$ |
| **0 to 1** | 0 | 1 | $Item_{\text{rev}} = 1 - Item$ | $1 - 0 = 1$ | $1 - 1 = 0$ |

---

## 4. CLI Command Reference

The calculation engine is located at `.agents/skills/psychometric-scale-resolver/scripts/questionnaire_resolver.py`.

### A. Search for a Scale:
```bash
# Search by Persian title, English title, abbreviation, or subscale
python3 .agents/skills/psychometric-scale-resolver/scripts/questionnaire_resolver.py search "ساراسون"
python3 .agents/skills/psychometric-scale-resolver/scripts/questionnaire_resolver.py search "Connor-Davidson"
python3 .agents/skills/psychometric-scale-resolver/scripts/questionnaire_resolver.py search "DASS"
```

### B. Inspect Full Psychometric Profile:
```bash
python3 .agents/skills/psychometric-scale-resolver/scripts/questionnaire_resolver.py profile "Penn State Worry Questionnaire"
```
Outputs:
- Official English and Persian titles, abbreviation, and source reference.
- Likert anchor boundaries ($Min$, $Max$).
- Subscale factor names with exact integer item lists.
- Reverse-scored item numbers.
- Theoretical mean and score ranges.
- Matching `.docx` / `.pdf` instruments from Google Drive.

### C. Score Raw Survey Dataset:
Given raw item columns (`Q1..Q25` or `R1..R25`):
```bash
python3 .agents/skills/psychometric-scale-resolver/scripts/questionnaire_resolver.py score \
  --data "data_raw.xlsx" \
  --scale "Connor-Davidson Resilience Scale" \
  --prefix "Q" \
  --out "data_scored.xlsx" \
  --summary "scoring_summary.json"
```
Automatically:
1. Reverses specified negative items into `Q_rev` columns.
2. Calculates sum and mean columns for every factor/subscale (`Sub_<Name>_Sum`, `Sub_<Name>_Mean`).
3. Calculates total composite sum and mean (`<Scale>_Total_Sum`, `<Scale>_Total_Mean`).
4. Computes Cronbach's $\alpha$ for each subscale and total scale.
5. Saves the scored dataset, ready for `statistical-data-analyst` to run ANCOVA, regression, or mediation.

---

## 5. Bundled Resources

- [Questionnaire Scoring & Factor Guide](file:///Users/saber/Desktop/academic_suite/.agents/skills/psychometric-scale-resolver/references/questionnaire_scoring_and_factor_guide.md) — Complete psychometric reference guide and reporting sentences.
- [questionnaire_resolver.py](file:///Users/saber/Desktop/academic_suite/.agents/skills/psychometric-scale-resolver/scripts/questionnaire_resolver.py) — Core resolution and scoring engine.
- [Questionnaires.xlsx](file:///Users/saber/Desktop/academic_suite/Questionnaires.xlsx) — Master registry of 4,880 psychometric scales and subscales.
