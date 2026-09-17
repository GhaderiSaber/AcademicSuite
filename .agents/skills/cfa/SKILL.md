---
name: cfa
description: Execute Confirmatory Factor Analysis (CFA), factor loadings (lambda), construct reliability (CR/omega), convergent validity (AVE), and model fit.
---

# CFA Skill (تحلیل عاملی تأییدی)

Evaluates measurement models and construct validity:
- Factor loadings ($\lambda$)
- Convergent validity ($AVE \ge .50, CR \ge .70$)
- Measurement model fit indices

## CLI Execution
```bash
python3 .agents/skills/cfa/scripts/run_cfa.py --data data_cleaned.xlsx --spec cfa_spec.json --output 05_cfa_results.json
```

