# Retired Legacy Skills Directory (Phase 16)

The skills in this directory are legacy workflow-converted wrappers that have been superseded by canonical production skills in `.agents/skills/`.

## Retirement & Migration Mapping

| Retired Legacy Skill | Reason for Retirement | Modern Canonical Replacement |
| :--- | :--- | :--- |
| `chapter2_literature` | Converted workflow shell | `persian-literature-review-builder` + `literature-harvester` |
| `chapter4` | Converted workflow shell | `chapter-4-writing` + `statistical-data-analyst` |
| `chapter5` | Converted workflow shell | `persian-discussion-builder` |
| `defense_presentation` | Converted workflow shell | `persian-defense-presentation-builder` (48 scripts, DrawingML, RTL SmartArt) |
| `intervention_protocol` | Converted workflow shell | `psychological-intervention-protocol-builder` |
| `journal_submission` | Converted workflow shell | `journal-submission-assistant` + `academic-article-writer` |
| `proposal` | Converted workflow shell | `persian-proposal-builder` + `gpower-sample-size-calculator` |
| `scale_validation` | Converted workflow shell | `psychometric-scale-validator` + `psychometric-scale-resolver` |
| `thesis_assembly` | Converted workflow shell | `persian-thesis-builder` |
| `thesis_revision` | Converted workflow shell | `persian-thesis-revision-assistant` |

All agent definitions in `.agents/agents/` have been re-bound to the canonical production skills.
