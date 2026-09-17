---
name: sem
description: Execute Structural Equation Modeling (SEM), evaluating latent structural paths and 11 Goodness-of-Fit indices against Hu & Bentler (1999) cutoffs.
---

# SEM Skill (مدل‌یابی معادلات ساختاری)

Evaluates full structural equation models:
- 11 Goodness-of-Fit indices
- Structural path coefficients
- Hu & Bentler (1999) benchmark compliance

## CLI Execution
```bash
python3 .agents/skills/sem/scripts/run_sem.py --data data_cleaned.xlsx --spec sem_model.json --output 05_macro_model.json
```

