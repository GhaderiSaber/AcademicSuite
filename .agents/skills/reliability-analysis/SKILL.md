---
name: reliability-analysis
description: Calculate scale internal consistency reliability including Cronbach's alpha, McDonald's omega, item-total correlations, and alpha-if-item-deleted.
---

# Reliability Analysis Skill (تحلیل پایایی ابزارها)

Computes internal consistency metrics for psychometric batteries:
- Cronbach's alpha ($\alpha$)
- McDonald's omega ($\omega$)
- Item-total correlation diagnostic tables

## CLI Execution
```bash
python3 .agents/skills/reliability-analysis/scripts/compute_reliability.py --data data_cleaned.xlsx --items "item1,item2,item3,item4" --scale-name "Anxiety" --output 02_reliability.json
```

