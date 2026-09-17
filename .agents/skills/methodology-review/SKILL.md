---
name: methodology-review
description: Audit research design validity, internal/external validity safeguards, statistical power (G*Power), and Chapter 3 methodology scaffolding.
---

# Methodology Review Skill (ارزیابی روش‌شناسی پژوهش)

Evaluates methodological rigor for Chapter 3 & proposals:
- G*Power statistical power verification ($1-\beta \ge .80$)
- Experimental and quasi-experimental validity safeguards
- Operational variable definitions

## CLI Execution
```bash
python3 .agents/skills/methodology-review/scripts/audit_methodology.py --spec methodology_spec.json --output 01_methodology_audit.json
```

