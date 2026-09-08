# Questionnaire Scoring, Subscale Resolution & Factor Guide

This guide establishes the standard operating procedure for discovering questionnaires, extracting subscale factor structures, applying reverse-scoring keys, and computing psychometric composites in the **Antigravity Academic Suite**.

---

## 1. The 3-Tier Questionnaire Resolution Hierarchy

When analyzing raw survey data or writing Chapter 3/Methodology instruments, never guess item assignments or reverse-scoring keys. Follow this strict 3-tier lookup hierarchy:

```
[Target Psychological Variable / Scale Name]
                     │
                     ▼
       ┌───────────────────────────┐
       │ Tier 1: Project Folder    │ ──► Found local instrument or proposal description?
       └───────────────────────────┘     ├── YES ──► Ingest local scoring keys
                     │ NO                └── NO  ──► Proceed to Tier 2
                     ▼
       ┌───────────────────────────┐
       │ Tier 2: Excel Registry    │ ──► Search Questionnaires.xlsx (4,880 entries)
       │ (Questionnaires.xlsx)     │     ├── Scale name (EN & FA), Abbreviation
       └───────────────────────────┘     ├── Subscale item ranges & lists (e.g. 1-5, 6-10)
                     │                   ├── Scoring method (1 to 5, 0 to 4) & Min/Max/Mean
                     │                   └── Reverse-scoring item keys
                     │
                     ▼ (Need full document, normative cutoffs, or item texts)
       ┌───────────────────────────┐
       │ Tier 3: GDrive Library    │ ──► Search 2,206 Master Instruments (.docx/.pdf)
       │ (Pending Works/           │     └── /Pending Works/Questionnaire(s)/
       │  Questionnaire)           │
       └───────────────────────────┘
```

---

## 2. Key Psychometric Columns in `Questionnaires.xlsx`

The master registry at `Questionnaires.xlsx` contains 12 columns across 4,880 rows:

1. **`Scale name`**: Formal English title (e.g., *Connor-Davidson Resilience Scale*, *Penn State Worry Questionnaire*, *Beck Depression Inventory*).
2. **`Scale Persian Name`**: Standard Iranian academic translation (e.g., *مقیاس تاب‌آوری کانر و دیویدسون*, *پرسشنامه نگرانی ایالتی پن*).
3. **`Subscale name`**: Factor or dimension title (e.g., *Personal Competence*, *Control*, or *Overall / Total Scale*).
4. **`Abbreviation`**: Standard acronym (*CD-RISC*, *PSWQ*, *DASS-21*, *BDI-II*).
5. **`Items of each subscale`**: Item assignments (e.g., `1-5`, `6, 12`, `10, 11, 12, 16, 17, 23, 24, 25`).
6. **`Scoring method`**: Likert response anchors (e.g., `1 to 5`, `0 to 4`, `Dichotomous (0-1)`).
7. **`Min score` / `Max score`**: Theoretical range boundaries for the factor or scale.
8. **`Theoretical mean`**: Midpoint $\frac{Min + Max}{2}$ for normative baseline comparisons.
9. **`Reverse scoring item`**: Comma-separated list of negatively worded items requiring inversion (e.g., `1, 3, 8, 10, 11`).
10. **`Source`**: Numeric citation ID linking to the `Source References` sheet.

---

## 3. Reverse-Scoring Formula & Algebra

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

## 4. CLI & Programmatic Tool Usage

### A. Search for a Questionnaire:
```bash
# Search by English name, Persian name, abbreviation, or subscale
python3 .agents/skills/statistical-data-analyst/scripts/questionnaire_resolver.py search "Connor-Davidson"
python3 .agents/skills/statistical-data-analyst/scripts/questionnaire_resolver.py search "اضطراب امتحان"
python3 .agents/skills/statistical-data-analyst/scripts/questionnaire_resolver.py search "PSWQ"
```

### B. Inspect Full Psychometric Profile:
```bash
python3 .agents/skills/statistical-data-analyst/scripts/questionnaire_resolver.py profile "Penn State Worry Questionnaire"
```

### C. Automatically Score Raw Item Responses:
Given a dataset where items are named `Q1..Q16` or `R1..R25`:
```bash
python3 .agents/skills/statistical-data-analyst/scripts/questionnaire_resolver.py score \
  --data "raw_survey_responses.xlsx" \
  --scale "Penn State Worry Questionnaire" \
  --prefix "Q" \
  --out "scored_dataset.xlsx" \
  --summary "scoring_summary.json"
```

### D. Direct Execution via `psychology_stats.py`:
```bash
# 1. Standalone CLI score task:
python3 .agents/skills/statistical-data-analyst/scripts/psychology_stats.py \
  --data "survey_data.xlsx" \
  --task score_scale \
  --scale "Connor-Davidson Resilience Scale" \
  --prefix "Q" \
  --out-scored "data_with_resilience_subscales.xlsx"

# 2. Automated multi-step analysis via study_config.json:
{
  "questionnaires": [
    {
      "scale": "Connor-Davidson Resilience Scale",
      "prefix": "R_",
      "save_scored_as": "scored_study_data.xlsx"
    }
  ],
  "descriptives": {
    "vars": ["CD-RISC_Total_Sum", "Sub_Personal_Competence_Sum"]
  },
  "ancova": [
    {
      "dv": "CD-RISC_Total_Sum",
      "group": "Group",
      "covar": "Pre_Resilience"
    }
  ]
}
```

---

## 5. Defense & Publication Best Practices

1. **Explicit Reporting of Scoring Range**: Always state in Chapter 3/Methodology:
   > «نمره‌گذاری این پرسشنامه بر روی یک طیف لیکرت ۵ درجه‌ای (از ۱ = کاملاً مخالفم تا ۵ = کاملاً موافقم) انجام شد. نمرات گویه‌های ۱، ۳، ۸، ۱۰ و ۱۱ به صورت معکوس نمره‌گذاری شدند و دامنه نمرات کل بین ۱۶ تا ۸۰ با میانگین نظری ۴۸ قرار دارد.»
2. **Internal Consistency Verification**: Always report Cronbach's alpha for both the overall scale and each constituent subscale in the sample. If $\alpha < .70$, inspect item-deleted alpha diagnostics.
