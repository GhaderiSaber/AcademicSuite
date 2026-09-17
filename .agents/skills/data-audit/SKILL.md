---
name: data-audit
description: Audit raw dataset quality, screen unengaged responses (straight-lining), diagnose missingness patterns (Little's MCAR), and detect multivariate outliers (Mahalanobis D2).
---

# Data Audit Skill (ارزیابی و غربالگری سلامت داده‌ها)

This skill provides deterministic auditing of raw datasets:
1. Missingness pattern diagnostics (Little's MCAR test).
2. Unengaged respondent screening (zero-variance straight-lining).
3. Multivariate outlier detection via Mahalanobis Distance ($D^2$).

## 🛫 Pre-Flight Pipeline Declaration
Before running this skill, declare:
```markdown
### 🛫 Pre-Flight Pipeline Declaration
- **Target Skill**: `.agents/skills/data-audit/SKILL.md`
- **Current Pipeline Stage**: Stage 4.0 — Data Audit & Screening
- **Official Script & CLI Command**: `python3 .agents/skills/data-audit/scripts/audit_dataset.py --data <raw_data.xlsx> --output data_audit_report.json`
- **Expected Checkpoint Output**: `data_audit_report.json`
```

## CLI Execution
```bash
python3 .agents/skills/data-audit/scripts/audit_dataset.py --data data/raw_data.xlsx --output 00_data_audit_report.json
```

