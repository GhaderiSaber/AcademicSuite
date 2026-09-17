---
name: regression
description: Execute standard, hierarchical, and stepwise multiple regression modeling, evaluating R2, delta R2, F-change, standardized beta, and collinearity diagnostics.
---

# Regression Skill (تحلیل رگرسیون چندگانه)

Executes ordinary least squares multiple regression:
- Model fit indices ($R, R^2, \text{Adj } R^2, F$)
- Parameter estimates ($B, SE, \beta, t, p$)
- Collinearity diagnostics (VIF/Tolerance)

## CLI Execution
```bash
python3 .agents/skills/regression/scripts/run_regression.py --data data_cleaned.xlsx --dv outcome --ivs "pred1,pred2,pred3" --output 06_regression.json
```

