---
name: data-cleaning
description: Reverse-code items from 4,880 validated questionnaires, aggregate subscale and composite scores, handle imputations, and export analysis-ready datasets.
---

# Data Cleaning Skill (پاک‌سازی و نمره‌گذاری پرسشنامه‌ها)

This skill executes programmatic data transformations:
1. Reverse-coding negative psychometric items.
2. Computing subscale and total composite scores.
3. Exporting immutable `data_cleaned.xlsx`.

## CLI Execution
```bash
python3 .agents/skills/data-cleaning/scripts/clean_and_score.py --data raw_data.xlsx --spec scale_spec.json --output-data data_cleaned.xlsx --output-log cleaning_log.json
```

