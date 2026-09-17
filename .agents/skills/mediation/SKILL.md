---
name: mediation
description: Execute Preacher & Hayes bootstrap mediation (PROCESS Model 4) with 5,000 resamples, generating 95% BCa confidence intervals for indirect effects.
---

# Mediation Skill (تحلیل میانجی‌گری با روش بوت‌استرپ)

Executes modern bootstrap mediation (PROCESS Model 4):
- 5,000 bootstrap resamples
- 95% BCa Confidence Interval for indirect paths ($a \times b$)
- Total, direct, and indirect effect decompositions

## CLI Execution
```bash
python3 .agents/skills/mediation/scripts/run_mediation.py --data data_cleaned.xlsx --iv X --mediator M --dv Y --bootstrap 5000 --output XX_mediation_1.json
```

