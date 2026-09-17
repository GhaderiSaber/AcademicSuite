---
name: apa-reporting
description: Generate strictly formatted APA 7th Edition 3-line tables, enforce statistical symbol italicization, Persian leading zero standard (۰.۰۰۱), and OpenXML LTR numeric decoupling.
---

# APA Reporting Skill (قالب‌بندی جداول و نگارش APA 7)

Transforms raw numerical outputs into institutional APA 7 deliverables:
- Exactly 3 horizontal borders
- Persian leading zero preservation (`۰.۰۰۱`, `۰.۰۵`)
- Italicization of Latin statistical symbols (*M, SD, t, F, p*)

## CLI Execution
```bash
python3 .agents/skills/apa-reporting/scripts/scaffold_apa_tables.py --input 06_hypothesis_1.json --output 06_hypothesis_1_table.md
```

