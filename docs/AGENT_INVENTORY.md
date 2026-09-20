# Agent Inventory & Cognitive Role Audit

**Document Version:** 2.2.0 (Continuous Learning Subagents Integrated)  
**Total Agents Defined:** 28 (22 Domain & Research Roles + 6 Continuous Learning Subagents)  
**Runtime Architecture:** Antigravity Native Multi-Agent System (`invoke_subagent`)  
**Behavioral Contracts:** 100% of agents possess a verified 12-section `contract.md`  

---

## 1. Executive Summary

In the Academic Suite architecture, agents are specialized cognitive roles that reason, plan, draft, and audit academic research. The system strictly decouples **Cognitive Agents ('The Brains')** from **Deterministic Scripts ('The Hands')** and enforces an **Adversarial Critic Model** separating content generation from quality auditing.

Every agent is packaged as an **Option 1 Directory Package** containing:

- `agent.md`: Antigravity runtime system prompt, YAML frontmatter, and skill declarations.
- `contract.md`: 12-section non-negotiable behavioral contract (`MISSION`, `CAN`, `CANNOT`, `INPUTS`, `OUTPUTS`, `ALLOWED TOOLS`, `REQUIRED SKILLS`, `FORBIDDEN ACTIONS`, `HANDOFF FORMAT`, `VALIDATION REQUIREMENTS`, `COMPLETION CRITERIA`, `FAILURE CONDITIONS`).
- `<role>.md`: Symlink for backward-compatible flat discovery by Antigravity.

---

## 2. Agent Taxonomy & Classification

| Category | Agent Name | Primary Mandate | Behavioral Contract |
| :--- | :--- | :--- | :--- |
| Domain Specialist Subagent | `academic-challenger` | Adversarial methodology, bias & statistical challenger | [contract.md](../.agents/agents/academic-challenger/contract.md) |
| Core Primary Agent (Phase 3) | `academic-orchestrator` | Specialized academic/statistical mandate | [contract.md](../.agents/agents/academic-orchestrator/contract.md) |
| Core Primary Agent (Phase 3) | `academic-writer` | Master academic chapter drafter, Persian rhetoric specialist & durable writing authority | [contract.md](../.agents/agents/academic-writer/contract.md) |
| Core Primary Agent (Phase 3) | `data-agent` | Specialized academic/statistical mandate | [contract.md](../.agents/agents/data-agent/contract.md) |
| Domain Specialist Subagent | `data-curator` | Specialized academic/statistical mandate | [contract.md](../.agents/agents/data-curator/contract.md) |
| Domain Specialist Subagent | `digital-saber` | Specialized academic/statistical mandate | [contract.md](../.agents/agents/digital-saber/contract.md) |
| Domain Specialist Subagent | `evidence-auditor` | Specialized academic/statistical mandate | [contract.md](../.agents/agents/evidence-auditor/contract.md) |
| Domain Specialist Subagent | `final-judge` | Specialized academic/statistical mandate | [contract.md](../.agents/agents/final-judge/contract.md) |
| Domain Specialist Subagent | `intervention-designer` | Specialized academic/statistical mandate | [contract.md](../.agents/agents/intervention-designer/contract.md) |
| Domain Specialist Subagent | `journal-strategist` | Specialized academic/statistical mandate | [contract.md](../.agents/agents/journal-strategist/contract.md) |
| Domain Specialist Subagent | `literature-expert` | Specialized academic/statistical mandate | [contract.md](../.agents/agents/literature-expert/contract.md) |
| Domain Specialist Subagent | `longitudinal-modmed-expert` | Specialized academic/statistical mandate | [contract.md](../.agents/agents/longitudinal-modmed-expert/contract.md) |
| Domain Specialist Subagent | `meta-analyst` | Specialized academic/statistical mandate | [contract.md](../.agents/agents/meta-analyst/contract.md) |
| Domain Specialist Subagent | `methodology-expert` | Specialized academic/statistical mandate | [contract.md](../.agents/agents/methodology-expert/contract.md) |
| Domain Specialist Subagent | `psychometric-expert` | Specialized academic/statistical mandate | [contract.md](../.agents/agents/psychometric-expert/contract.md) |
| Domain Specialist Subagent | `qualitative-analyst` | Specialized academic/statistical mandate | [contract.md](../.agents/agents/qualitative-analyst/contract.md) |
| Core Primary Agent (Phase 3) | `research-agent` | Specialized academic/statistical mandate | [contract.md](../.agents/agents/research-agent/contract.md) |
| Domain Specialist Subagent | `results-auditor` | Specialized academic/statistical mandate | [contract.md](../.agents/agents/results-auditor/contract.md) |
| Domain Specialist Subagent | `statistical-auditor` | Specialized academic/statistical mandate | [contract.md](../.agents/agents/statistical-auditor/contract.md) |
| Domain Specialist Subagent | `statistical-expert` | Specialized academic/statistical mandate | [contract.md](../.agents/agents/statistical-expert/contract.md) |
| Core Primary Agent (Phase 3) | `statistics-agent` | Specialized academic/statistical mandate | [contract.md](../.agents/agents/statistics-agent/contract.md) |
| Core Primary Agent (Phase 3) | `validation-agent` | Specialized academic/statistical mandate | [contract.md](../.agents/agents/validation-agent/contract.md) |
| Continuous Learning Subagent | `behavior-analyst` | Causal root-cause analysis and diagnosis of agent behavior | [contract.md](../.agents/agents/behavior-analyst/contract.md) |
| Continuous Learning Subagent | `curriculum-builder` | Graduated complexity benchmark scenarios and practice tasks | [contract.md](../.agents/agents/curriculum-builder/contract.md) |
| Continuous Learning Subagent | `evaluation-agent` | Deterministic evaluation lab harness and counterfactual tests | [contract.md](../.agents/agents/evaluation-agent/contract.md) |
| Continuous Learning Subagent | `knowledge-curator` | Synthesis of episodic experiences into reusable knowledge | [contract.md](../.agents/agents/knowledge-curator/contract.md) |
| Continuous Learning Subagent | `skill-evolver` | Candidate Skill mutations and behavioral instructions diffs | [contract.md](../.agents/agents/skill-evolver/contract.md) |
| Continuous Learning Subagent | `trajectory-analyzer` | Reconstructs observable tool calls, exit codes, and artifacts | [contract.md](../.agents/agents/trajectory-analyzer/contract.md) |

---

## 3. Comprehensive Agent Profile Registry

### 1. `academic-orchestrator`
- **Package Path:** `.agents/agents/academic-orchestrator/`
- **Runtime Prompt:** `.agents/agents/academic-orchestrator/agent.md`
- **Behavioral Contract:** [`.agents/agents/academic-orchestrator/contract.md`](file:///home/ghaderi-saber/Desktop/AcademicSuite/.agents/agents/academic-orchestrator/contract.md) (12 Sections Verified)
- **Classification:** Core Primary Role (Phase 3)
- **Description:** Primary academic master conductor and research project lead. Understands holistic research requirements, decomposes multi-chapter pipelines into bounded micro-stages, maps capabilities to skills and specialist subagents, delegates with strict context isolation, tracks artifact dependencies, coordinates adversarial validation, manages retry loops, and synthesizes final deliverables.
- **Active Skills Bound (10):** `invoke_subagent`, `manage_subagents`, `send_message`, `list_dir`, `grep_search`, `find_by_name`, `ask_question`, `academic-suite-orchestrator`, `digital-twin-academic-consultant`, `thesis-integrity-auditor`
- **Tools Whitelist:** Native Antigravity tools (`invoke_subagent`, `run_command`, `write_to_file`, `view_file`)

### 2. `academic-writer`
- **Package Path:** `.agents/agents/academic-writer/`
- **Runtime Prompt:** `.agents/agents/academic-writer/agent.md`
- **Behavioral Contract:** [`.agents/agents/academic-writer/contract.md`](file:///home/ghaderi-saber/Desktop/AcademicSuite/.agents/agents/academic-writer/contract.md) (12 Sections Verified)
- **Classification:** Core Primary Role (Phase 3) — Durable Academic Writing Authority
- **Description:** Master academic chapter drafter and Persian rhetoric specialist. Formulates defense-ready thesis chapters (Ch 1–5), empirical journal articles, and clinical intervention protocols adhering to Saber's 5-part epistemic paragraph structure, natural cadence variability (CV >= 0.50), strict APA 7 presentation, results narrative, and deep psychological discussion.
- **Active Skills Bound (10):** `chapter-4-writing`, `persian-literature-review-builder`, `persian-discussion-builder`, `persian-thesis-builder`, `academic-article-writer`, `ai-academic-tone-polisher`, `apa-reporting`, `psychological-intervention-protocol-builder`, `journal-submission-assistant`, `persian-defense-presentation-builder`
- **Tools Whitelist:** Native Antigravity tools (`invoke_subagent`, `run_command`, `write_to_file`, `view_file`)

### 3. `data-agent`
- **Package Path:** `.agents/agents/data-agent/`
- **Runtime Prompt:** `.agents/agents/data-agent/agent.md`
- **Behavioral Contract:** [`.agents/agents/data-agent/contract.md`](file:///home/ghaderi-saber/Desktop/AcademicSuite/.agents/agents/data-agent/contract.md) (12 Sections Verified)
- **Classification:** Core Primary Role (Phase 3)
- **Description:** Specialized domain subagent for raw dataset ingestion, data discovery, schema mapping, data quality screening, missing value diagnostics (Little's MCAR), reverse-coding from 4,880 validated instruments, variable transformations, psychometric simulation, and data integrity verification.
- **Active Skills Bound (7):** `list_dir`, `grep_search`, `find_by_name`, `statistical-data-analyst`, `psychometric-scale-resolver`, `psychometric-scale-validator`, `psychometric-data-simulator`
- **Tools Whitelist:** Native Antigravity tools (`invoke_subagent`, `run_command`, `write_to_file`, `view_file`)

### 4. `data-curator`
- **Package Path:** `.agents/agents/data-curator/`
- **Runtime Prompt:** `.agents/agents/data-curator/agent.md`
- **Behavioral Contract:** [`.agents/agents/data-curator/contract.md`](file:///home/ghaderi-saber/Desktop/AcademicSuite/.agents/agents/data-curator/contract.md) (12 Sections Verified)
- **Classification:** Domain Specialist Subagent
- **Description:** Specialist subagent for raw dataset ingestion, missing data pattern diagnosis (MCAR/MAR/MNAR), unengaged response filtering, multivariate outlier screening (Mahalanobis D2, Cook's distance), demographic standardization, and data dictionary compilation.
- **Active Skills Bound (2):** `statistical-data-analyst`, `psychometric-scale-resolver`
- **Tools Whitelist:** Native Antigravity tools (`invoke_subagent`, `run_command`, `write_to_file`, `view_file`)

### 5. `digital-saber`
- **Package Path:** `.agents/agents/digital-saber/`
- **Runtime Prompt:** `.agents/agents/digital-saber/agent.md`
- **Behavioral Contract:** [`.agents/agents/digital-saber/contract.md`](file:///home/ghaderi-saber/Desktop/AcademicSuite/.agents/agents/digital-saber/contract.md) (12 Sections Verified)
- **Classification:** Domain Specialist Subagent
- **Description:** Master Research Project Lead, Cognitive Architect, and Digital Twin of
- **Active Skills Bound (5):** `academic-suite-orchestrator`, `digital-twin-academic-consultant`, `thesis-integrity-auditor`, `chapter-4-writing`, `persian-thesis-revision-assistant`
- **Tools Whitelist:** Native Antigravity tools (`invoke_subagent`, `run_command`, `write_to_file`, `view_file`)

### 6. `evidence-auditor`
- **Package Path:** `.agents/agents/evidence-auditor/`
- **Runtime Prompt:** `.agents/agents/evidence-auditor/agent.md`
- **Behavioral Contract:** [`.agents/agents/evidence-auditor/contract.md`](file:///home/ghaderi-saber/Desktop/AcademicSuite/.agents/agents/evidence-auditor/contract.md) (12 Sections Verified)
- **Classification:** Domain Specialist Subagent
- **Description:** Epistemic integrity and citation verification subagent auditing bidirectional in-text to bibliography concordance, Irandoc similarity compliance (< 20%), and robotic AI cliché elimination.
- **Active Skills Bound (2):** `academic-reference-extractor`, `irandoc-plagiarism-reducer`
- **Tools Whitelist:** Native Antigravity tools (`invoke_subagent`, `run_command`, `write_to_file`, `view_file`)

### 7. `final-judge`
- **Package Path:** `.agents/agents/final-judge/`
- **Runtime Prompt:** `.agents/agents/final-judge/agent.md`
- **Behavioral Contract:** [`.agents/agents/final-judge/contract.md`](file:///home/ghaderi-saber/Desktop/AcademicSuite/.agents/agents/final-judge/contract.md) (12 Sections Verified)
- **Classification:** Domain Specialist Subagent
- **Description:** Final dissertation defense committee simulator, viva voce cross-examiner,
- **Active Skills Bound (3):** `thesis-integrity-auditor`, `persian-defense-presentation-builder`, `persian-defense-presentation-builder`
- **Tools Whitelist:** Native Antigravity tools (`invoke_subagent`, `run_command`, `write_to_file`, `view_file`)

### 8. `intervention-designer`
- **Package Path:** `.agents/agents/intervention-designer/`
- **Runtime Prompt:** `.agents/agents/intervention-designer/agent.md`
- **Behavioral Contract:** [`.agents/agents/intervention-designer/contract.md`](file:///home/ghaderi-saber/Desktop/AcademicSuite/.agents/agents/intervention-designer/contract.md) (12 Sections Verified)
- **Classification:** Domain Specialist Subagent
- **Description:** Specialist subagent for designing standardized evidence-based psychological
- **Active Skills Bound (2):** `psychological-intervention-protocol-builder`, `psychological-intervention-protocol-builder`
- **Tools Whitelist:** Native Antigravity tools (`invoke_subagent`, `run_command`, `write_to_file`, `view_file`)

### 9. `journal-strategist`
- **Package Path:** `.agents/agents/journal-strategist/`
- **Runtime Prompt:** `.agents/agents/journal-strategist/agent.md`
- **Behavioral Contract:** [`.agents/agents/journal-strategist/contract.md`](file:///home/ghaderi-saber/Desktop/AcademicSuite/.agents/agents/journal-strategist/contract.md) (12 Sections Verified)
- **Classification:** Domain Specialist Subagent
- **Description:** Specialist subagent for academic journal article packaging, target journal
- **Active Skills Bound (4):** `academic-article-writer`, `journal-submission-assistant`, `ai-academic-tone-polisher`, `journal-submission-assistant`
- **Tools Whitelist:** Native Antigravity tools (`invoke_subagent`, `run_command`, `write_to_file`, `view_file`)

### 10. `literature-expert`
- **Package Path:** `.agents/agents/literature-expert/`
- **Runtime Prompt:** `.agents/agents/literature-expert/agent.md`
- **Behavioral Contract:** [`.agents/agents/literature-expert/contract.md`](file:///home/ghaderi-saber/Desktop/AcademicSuite/.agents/agents/literature-expert/contract.md) (12 Sections Verified)
- **Classification:** Domain Specialist Subagent
- **Description:** Specialist subagent for multi-database literature harvesting, empirical
- **Active Skills Bound (5):** `literature-harvester`, `persian-literature-review-builder`, `bibliometric-network-analyst`, `citation-network-visualizer`, `persian-literature-review-builder`
- **Tools Whitelist:** Native Antigravity tools (`invoke_subagent`, `run_command`, `write_to_file`, `view_file`)

### 11. `longitudinal-modmed-expert`
- **Package Path:** `.agents/agents/longitudinal-modmed-expert/`
- **Runtime Prompt:** `.agents/agents/longitudinal-modmed-expert/agent.md`
- **Behavioral Contract:** [`.agents/agents/longitudinal-modmed-expert/contract.md`](file:///home/ghaderi-saber/Desktop/AcademicSuite/.agents/agents/longitudinal-modmed-expert/contract.md) (12 Sections Verified)
- **Classification:** Domain Specialist Subagent
- **Description:** >-
- **Active Skills Bound (3):** `longitudinal-moderated-mediation`, `mediation`, `apa-reporting`
- **Tools Whitelist:** Native Antigravity tools (`invoke_subagent`, `run_command`, `write_to_file`, `view_file`)

### 12. `meta-analyst`
- **Package Path:** `.agents/agents/meta-analyst/`
- **Runtime Prompt:** `.agents/agents/meta-analyst/agent.md`
- **Behavioral Contract:** [`.agents/agents/meta-analyst/contract.md`](file:///home/ghaderi-saber/Desktop/AcademicSuite/.agents/agents/meta-analyst/contract.md) (12 Sections Verified)
- **Classification:** Domain Specialist Subagent
- **Description:** Specialist subagent for PRISMA 2020 systematic literature reviews, Cochrane RoB 2 risk of bias evaluations, and quantitative meta-analysis.
- **Active Skills Bound (2):** `systematic-review-meta-analyst`, `literature-harvester`
- **Tools Whitelist:** Native Antigravity tools (`invoke_subagent`, `run_command`, `write_to_file`, `view_file`)

### 13. `methodology-expert`
- **Package Path:** `.agents/agents/methodology-expert/`
- **Runtime Prompt:** `.agents/agents/methodology-expert/agent.md`
- **Behavioral Contract:** [`.agents/agents/methodology-expert/contract.md`](file:///home/ghaderi-saber/Desktop/AcademicSuite/.agents/agents/methodology-expert/contract.md) (12 Sections Verified)
- **Classification:** Domain Specialist Subagent
- **Description:** Specialist subagent for research methodology, experimental design, sampling
- **Active Skills Bound (4):** `gpower-sample-size-calculator`, `persian-proposal-builder`, `psychological-intervention-protocol-builder`, `persian-proposal-builder`
- **Tools Whitelist:** Native Antigravity tools (`invoke_subagent`, `run_command`, `write_to_file`, `view_file`)

### 14. `psychometric-expert`
- **Package Path:** `.agents/agents/psychometric-expert/`
- **Runtime Prompt:** `.agents/agents/psychometric-expert/agent.md`
- **Behavioral Contract:** [`.agents/agents/psychometric-expert/contract.md`](file:///home/ghaderi-saber/Desktop/AcademicSuite/.agents/agents/psychometric-expert/contract.md) (12 Sections Verified)
- **Classification:** Domain Specialist Subagent
- **Description:** Specialist subagent for psychometric instrument resolution, Classical
- **Active Skills Bound (4):** `psychometric-scale-resolver`, `psychometric-scale-validator`, `psychometric-data-simulator`, `psychometric-scale-validator`
- **Tools Whitelist:** Native Antigravity tools (`invoke_subagent`, `run_command`, `write_to_file`, `view_file`)

### 15. `qualitative-analyst`
- **Package Path:** `.agents/agents/qualitative-analyst/`
- **Runtime Prompt:** `.agents/agents/qualitative-analyst/agent.md`
- **Behavioral Contract:** [`.agents/agents/qualitative-analyst/contract.md`](file:///home/ghaderi-saber/Desktop/AcademicSuite/.agents/agents/qualitative-analyst/contract.md) (12 Sections Verified)
- **Classification:** Domain Specialist Subagent
- **Description:** Specialist subagent for qualitative data analysis, Reflexive Thematic Analysis (Braun & Clarke), and Grounded Theory (Strauss & Corbin).
- **Active Skills Bound (1):** `qualitative-data-analyst`
- **Tools Whitelist:** Native Antigravity tools (`invoke_subagent`, `run_command`, `write_to_file`, `view_file`)

### 16. `research-agent`
- **Package Path:** `.agents/agents/research-agent/`
- **Runtime Prompt:** `.agents/agents/research-agent/agent.md`
- **Behavioral Contract:** [`.agents/agents/research-agent/contract.md`](file:///home/ghaderi-saber/Desktop/AcademicSuite/.agents/agents/research-agent/contract.md) (12 Sections Verified)
- **Classification:** Core Primary Role (Phase 3)
- **Description:** Specialized domain subagent for scientific literature harvesting, research question formulation, experimental and quasi-experimental research design, methodology specification, statistical power determination (G*Power), epistemic evidence synthesis, and citation integrity.
- **Active Skills Bound (13):** `list_dir`, `grep_search`, `find_by_name`, `read_url_content`, `search_web`, `literature-harvester`, `persian-literature-review-builder`, `bibliometric-network-analyst`, `citation-network-visualizer`, `gpower-sample-size-calculator`, `persian-proposal-builder`, `systematic-review-meta-analyst`, `qualitative-data-analyst`
- **Tools Whitelist:** Native Antigravity tools (`invoke_subagent`, `run_command`, `write_to_file`, `view_file`)

### 17. `results-auditor`
- **Package Path:** `.agents/agents/results-auditor/`
- **Runtime Prompt:** `.agents/agents/results-auditor/agent.md`
- **Behavioral Contract:** [`.agents/agents/results-auditor/contract.md`](file:///home/ghaderi-saber/Desktop/AcademicSuite/.agents/agents/results-auditor/contract.md) (12 Sections Verified)
- **Classification:** Domain Specialist Subagent
- **Description:** Quality control subagent enforcing APA 7th Edition numerical precision,
- **Active Skills Bound (3):** `thesis-integrity-auditor`, `statistical-data-analyst`, `chapter-4-writing`
- **Tools Whitelist:** Native Antigravity tools (`invoke_subagent`, `run_command`, `write_to_file`, `view_file`)

### 18. `statistical-auditor`
- **Package Path:** `.agents/agents/statistical-auditor/`
- **Runtime Prompt:** `.agents/agents/statistical-auditor/agent.md`
- **Behavioral Contract:** [`.agents/agents/statistical-auditor/contract.md`](file:///home/ghaderi-saber/Desktop/AcademicSuite/.agents/agents/statistical-auditor/contract.md) (12 Sections Verified)
- **Classification:** Domain Specialist Subagent
- **Description:** Adversarial quality auditor subagent for statistical assumptions, degrees
- **Active Skills Bound (3):** `thesis-integrity-auditor`, `statistical-data-analyst`, `chapter-4-writing`
- **Tools Whitelist:** Native Antigravity tools (`invoke_subagent`, `run_command`, `write_to_file`, `view_file`)

### 19. `statistical-expert`
- **Package Path:** `.agents/agents/statistical-expert/`
- **Runtime Prompt:** `.agents/agents/statistical-expert/agent.md`
- **Behavioral Contract:** [`.agents/agents/statistical-expert/contract.md`](file:///home/ghaderi-saber/Desktop/AcademicSuite/.agents/agents/statistical-expert/contract.md) (12 Sections Verified)
- **Classification:** Domain Specialist Subagent
- **Description:** Specialist subagent for statistical analysis planning, hypothesis testing
- **Active Skills Bound (4):** `statistical-data-analyst`, `psychometric-scale-resolver`, `psychometric-scale-validator`, `chapter-4-writing`
- **Tools Whitelist:** Native Antigravity tools (`invoke_subagent`, `run_command`, `write_to_file`, `view_file`)

### 20. `statistics-agent`
- **Package Path:** `.agents/agents/statistics-agent/`
- **Runtime Prompt:** `.agents/agents/statistics-agent/agent.md`
- **Behavioral Contract:** [`.agents/agents/statistics-agent/contract.md`](file:///home/ghaderi-saber/Desktop/AcademicSuite/.agents/agents/statistics-agent/contract.md) (12 Sections Verified)
- **Classification:** Core Primary Role (Phase 3)
- **Description:** Specialized domain subagent for inferential statistical analysis planning, parametric assumption verification sequences, deterministic Python and R execution, advanced statistical modeling (ANCOVA, RM-ANOVA, PROCESS bootstrap mediation, SEM), results extraction, APA 7 tables, and 300-DPI figures.
- **Active Skills Bound (7):** `list_dir`, `grep_search`, `find_by_name`, `statistical-data-analyst`, `psychometric-scale-validator`, `psychometric-data-simulator`, `systematic-review-meta-analyst`
- **Tools Whitelist:** Native Antigravity tools (`invoke_subagent`, `run_command`, `write_to_file`, `view_file`)

### 21. `validation-agent`
- **Package Path:** `.agents/agents/validation-agent/`
- **Runtime Prompt:** `.agents/agents/validation-agent/agent.md`
- **Behavioral Contract:** [`.agents/agents/validation-agent/contract.md`](file:///home/ghaderi-saber/Desktop/AcademicSuite/.agents/agents/validation-agent/contract.md) (12 Sections Verified)
- **Classification:** Core Primary Role (Phase 3)
- **Description:** Independent adversarial quality auditor, Viva Voce defense simulator, and institutional release gatekeeper. Conducts independent checking of draft deliverables, verifies cross-chapter consistency, validates institutional and APA 7 requirements, audits methodological validity, verifies statistical integrity via Multi-Signal Anomaly Index (MSAI), and verifies physical artifact completeness.
- **Active Skills Bound (7):** `list_dir`, `grep_search`, `find_by_name`, `thesis-integrity-auditor`, `academic-reference-extractor`, `irandoc-plagiarism-reducer`, `persian-thesis-revision-assistant`
- **Tools Whitelist:** Native Antigravity tools (`invoke_subagent`, `run_command`, `write_to_file`, `view_file`)

### 22. `academic-challenger`
- **Package Path:** `.agents/agents/academic-challenger/`
- **Runtime Prompt:** `.agents/agents/academic-challenger/agent.md`
- **Behavioral Contract:** [`.agents/agents/academic-challenger/contract.md`](file:///home/ghaderi-saber/Desktop/AcademicSuite/.agents/agents/academic-challenger/contract.md) (12 Sections Verified)
- **Classification:** Domain Specialist Subagent (Adversarial Critic)
- **Description:** Specialist adversarial reviewer identifying methodology flaws, p-hacking, publication bias, unmeasured confounding, and statistical fragility before committee submission.
- **Active Skills Bound (2):** `thesis-integrity-auditor`, `methodology-review`
- **Tools Whitelist:** `view_file`, `list_dir`, `grep_search`, `find_by_name`, `write_to_file`

