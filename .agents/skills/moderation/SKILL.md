---
name: moderation
description: Execute moderation interaction analysis (PROCESS Model 1), mean-centering predictors, simple slopes (-1 SD, Mean, +1 SD), and Johnson-Neyman regions.
---

# Moderation Skill (تحلیل تعدیل‌گری و شیب‌های ساده)

Executes linear moderation models (PROCESS Model 1):
- Predictor mean-centering
- Product interaction terms ($X \times W$)
- Simple slopes conditional effects ($-1 SD, Mean, +1 SD$)

## CLI Execution
```bash
python3 .agents/skills/moderation/scripts/run_moderation.py --data data_cleaned.xlsx --iv X --mod W --dv Y --output XX_moderation_1.json
```

