---
name: literature-review
description: Multi-database query formulation (PubMed, CrossRef, SID), empirical parameter extraction, and inverted-triangle Chapter 2 review structuring. Consolidated alias pointing to persian-literature-review-builder and literature-harvester.
---

# Literature Review Skill (Consolidated Alias)

> [!NOTE]
> **Skill Consolidation Notice**:
> This capability has been consolidated into two specialized skills:
> 1. **`persian-literature-review-builder`**: For synthesizing theoretical foundations, empirical background tables, and complete Chapter 2 thesis/dissertation chapters.
> 2. **`literature-harvester`**: For automated multi-database search queries across PubMed, CrossRef, Semantic Scholar, SID, and Magiran.

---

## 1. WHEN TO USE (Activation Criteria)
Activate this skill or its parent consolidated skills when:
- Synthesizing empirical literature into an inverted-triangle Chapter 2 narrative.
- Extracting study parameters (sample sizes, instruments, findings) into structured matrices.

## 2. PRIMARY ALTERNATIVES
- For Chapter 2 compilation $\to$ use `persian-literature-review-builder`.
- For database harvesting $\to$ use `literature-harvester`.

## 3. DETERMINISTIC CLI RUNNER
Legacy CLI command retained for backward compatibility:
```bash
python3 .agents/skills/literature-review/scripts/harvest_and_synthesize.py \
  --spec "query_spec.json" \
  --output "literature_matrix.json"
```
