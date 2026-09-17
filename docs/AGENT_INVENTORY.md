# Agent Inventory & Cognitive Role Audit

**Document Version:** 1.0.0 (Phase 1 Audit)  
**Total Agents Defined:** 15  
**Runtime Architecture:** Antigravity Native Multi-Agent System (`invoke_subagent`)  

---

## 1. Executive Summary

In the Academic Suite architecture, agents are specialized cognitive roles that reason, plan, draft, and audit academic research. The system strictly decouples **Cognitive Agents ("The Brains")** from **Deterministic Scripts ("The Hands")** and enforces an **Adversarial Critic Model** separating content generation from quality auditing.

---

## 2. Agent Taxonomy & Classification

| Tier | Role Category | Agent Name | Primary Responsibility |
|---|---|---|---|
| **Tier 1** | **Sole Conductor & Digital Twin** | `digital-saber` | Master Research Project Lead, Cognitive Architect, Case-Based Memory Retriver, Client Gatekeeper |
| **Tier 2** | **Design & Methodological Brains** | `methodology-expert` | Research methodology, experimental design, sampling power determination (G*Power) |
| | | `statistical-expert` | Statistical analysis planning, parametric assumption trees, inferential test mapping |
| | | `psychometric-expert` | Scale resolution (4,880 questionnaires), CTT/IRT validation, EFA/CFA, psychometric simulation |
| | | `intervention-designer` | Standardized psychological intervention protocols (ACT, CBT, Schema), CONSORT diagrams |
| | | `qualitative-analyst` | Reflexive Thematic Analysis (Braun & Clarke), Grounded Theory, qualitative coding |
| | | `data-curator` | Data hygiene, Little's MCAR test, unengaged response screening, Mahalanobis $D^2$ outliers |
| **Tier 3** | **Literature & Evidence Brains** | `literature-expert` | Multi-database literature harvesting (CrossRef, PubMed, SID), Chapter 2 theoretical synthesis |
| | | `meta-analyst` | PRISMA 2020 systematic reviews, Cochrane RoB 2 risk of bias, quantitative meta-analysis |
| **Tier 4** | **Drafting & Packaging Brains** | `academic-writer` | Chapter drafting (Ch 1–5), authentic Persian rhetoric, 5-part epistemic paragraph structure |
| | | `journal-strategist` | Extraction of journal manuscripts, journal matchmaking (WoS/Scopus/ISC), rebuttal triage |
| **Tier 5** | **Adversarial Auditors & Critics** | `statistical-auditor` | Adversarial statistical QC, degrees of freedom check, Multi-Signal Anomaly Index (MSAI) |
| | | `results-auditor` | APA 7 typography enforcement, leading zero rule (`۰.۰۰۱`), OMML math preservation |
| | | `evidence-auditor` | In-text citation reconciliation, Irandoc plagiarism risk screening, AI cliché elimination |
| | | `final-judge` | Dissertation committee defense simulation (5 examiner personas), viva voce gatekeeper |

---

## 3. Comprehensive Agent Profile Registry

### 1. `digital-saber`
- **File:** `.agents/agents/digital-saber.md`
- **Classification:** Primary Orchestrator & Project Lead (Lead Agent Twin)
- **Role:** Master Research Project Lead & Cognitive Orchestrator
- **Modern Skills Assigned:** `academic-suite-orchestrator`, `digital-twin-academic-consultant`, `thesis-integrity-auditor`
- **Legacy Skills Listed:** `chapter4`, `thesis_revision`
- **Tools Assigned:** Full Antigravity Agent toolset (`invoke_subagent`, `run_command`, `write_to_file`, `view_file`, etc.)
- **MCP Usage:** None (0 MCP servers active)
- **Core Responsibilities:** Ingests research problem, retrieves historical precedents via `case_memory_engine.py`, records major milestones in `decision_journal_engine.py`, coordinates subagents across pipeline stages, enforces the Interactive Stage-Gate Protocol (Directive 11).

### 2. `methodology-expert`
- **File:** `.agents/agents/methodology-expert.md`
- **Classification:** Specialist Subagent (Methodology Brain)
- **Role:** Research Methodology & Experimental Design Specialist
- **Modern Skills Assigned:** `gpower-sample-size-calculator`, `persian-proposal-builder`, `psychological-intervention-protocol-builder`
- **Legacy Skills Listed:** `proposal`
- **Tools Assigned:** Antigravity read tools + `run_command`
- **MCP Usage:** None
- **Core Responsibilities:** Classifies study designs (pretest-posttest control group, Solomon four-group, cross-sectional, SEM), calculates statistical power ($1-\beta \ge .80$), formulates directional hypotheses, guards against internal/external validity threats.

### 3. `statistical-expert`
- **File:** `.agents/agents/statistical-expert.md`
- **Classification:** Specialist Subagent (Statistical Brain)
- **Role:** Statistical Analysis & Hypothesis Testing Architect
- **Modern Skills Assigned:** `statistical-data-analyst`, `psychometric-scale-resolver`, `psychometric-scale-validator`
- **Legacy Skills Listed:** `chapter4`
- **Tools Assigned:** Antigravity read tools + `run_command`
- **MCP Usage:** None
- **Core Responsibilities:** Governs the 10-step parametric decision sequence (Shapiro-Wilk, Levene, regression slope homogeneity, sphericity, collinearity), selects appropriate tests (ANCOVA, RM-ANOVA, PROCESS bootstrap mediation), and compiles execution configurations for deterministic scripts.

### 4. `data-curator`
- **File:** `.agents/agents/data-curator.md`
- **Classification:** Specialist Subagent (Data Screening Brain)
- **Role:** Data Hygiene, Missing Value Diagnostics & Screening Specialist
- **Modern Skills Assigned:** `statistical-data-analyst`, `psychometric-scale-resolver`
- **Legacy Skills Listed:** None
- **Tools Assigned:** Antigravity read tools + `run_command`
- **MCP Usage:** None
- **Core Responsibilities:** Executes Stage 4.0 data curation, tests missingness patterns (Little's MCAR), screens unengaged respondents (zero variance, straight-lining), identifies multivariate outliers (Mahalanobis $D^2$, Cook's distance), exports `data_cleaned.xlsx` and `00_data_curation_report.json`.

### 5. `psychometric-expert`
- **File:** `.agents/agents/psychometric-expert.md`
- **Classification:** Specialist Subagent (Psychometrics Brain)
- **Role:** Psychometrician & Construct Validation Specialist
- **Modern Skills Assigned:** `psychometric-scale-resolver`, `psychometric-scale-validator`, `psychometric-data-simulator`
- **Legacy Skills Listed:** `scale_validation`
- **Tools Assigned:** Antigravity read tools + `run_command`
- **MCP Usage:** None
- **Core Responsibilities:** Resolves instruments and reverse-coding keys from `Questionnaires.xlsx`, evaluates scale reliability (Cronbach's $\alpha$, McDonald's $\omega$), validates factor structure (EFA/CFA, convergent/discriminant validity), simulates psychometric distributions with empirical noise.

### 6. `intervention-designer`
- **File:** `.agents/agents/intervention-designer.md`
- **Classification:** Specialist Subagent (Clinical Protocol Brain)
- **Role:** Psychological Intervention Protocol Architect
- **Modern Skills Assigned:** `psychological-intervention-protocol-builder`
- **Legacy Skills Listed:** `intervention_protocol`
- **Tools Assigned:** Antigravity read tools + `run_command` + `write_to_file`
- **MCP Usage:** None
- **Core Responsibilities:** Formulates evidence-based intervention manuals (ACT, CBT, Schema Therapy, Mindfulness), creates Chapter 3 session-by-session clinical protocol tables, and designs CONSORT 2010 participant flowcharts.

### 7. `literature-expert`
- **File:** `.agents/agents/literature-expert.md`
- **Classification:** Specialist Subagent (Literature Brain)
- **Role:** Literature & Epistemic Evidence Synthesizer
- **Modern Skills Assigned:** `literature-harvester`, `persian-literature-review-builder`, `bibliometric-network-analyst`, `citation-network-visualizer`
- **Legacy Skills Listed:** `chapter2_literature`
- **Tools Assigned:** Antigravity read tools, `search_web`, `run_command`
- **MCP Usage:** None
- **Core Responsibilities:** Harvester across CrossRef/PubMed/SID/Magiran, extracts empirical study parameters ($N$, designs, findings), constructs co-citation and bibliometric science maps, synthesizes inverted-triangle Chapter 2 reviews.

### 8. `meta-analyst`
- **File:** `.agents/agents/meta-analyst.md`
- **Classification:** Specialist Subagent (Meta-Analysis Brain)
- **Role:** Systematic Review & Quantitative Meta-Analyst
- **Modern Skills Assigned:** `systematic-review-meta-analyst`, `literature-harvester`
- **Legacy Skills Listed:** None
- **Tools Assigned:** Antigravity read tools + `run_command`
- **MCP Usage:** None
- **Core Responsibilities:** Formulates PICO search strings, conducts Cochrane RoB 2 risk of bias assessments, pools standardized mean differences (Hedges' $g$), calculates $I^2$ heterogeneity, runs Egger's regression, and generates PRISMA 2020 flowcharts and Forest/Funnel plots.

### 9. `qualitative-analyst`
- **File:** `.agents/agents/qualitative-analyst.md`
- **Classification:** Specialist Subagent (Qualitative Brain)
- **Role:** Qualitative Research & Thematic Analysis Specialist
- **Modern Skills Assigned:** `qualitative-data-analyst`
- **Legacy Skills Listed:** None
- **Tools Assigned:** Antigravity read tools + `run_command`
- **MCP Usage:** None
- **Core Responsibilities:** Conducts Braun & Clarke Reflexive Thematic Analysis and Strauss & Corbin Grounded Theory (open, axial, selective coding), computes inter-coder reliability (Holsti index, Cohen's $\kappa$), and exports theme hierarchy matrices.

### 10. `academic-writer`
- **File:** `.agents/agents/academic-writer.md`
- **Classification:** Specialist Subagent (Drafting & Rhetoric Brain)
- **Role:** Persian Academic Chapter Drafter & Rhetoric Specialist
- **Modern Skills Assigned:** `persian-thesis-builder`, `persian-discussion-builder`, `academic-article-writer`, `ai-academic-tone-polisher`
- **Legacy Skills Listed:** `chapter4`, `chapter5`, `thesis_assembly`
- **Tools Assigned:** Antigravity read tools + `write_to_file` + `run_command`
- **MCP Usage:** None
- **Core Responsibilities:** Drafts defense-ready thesis chapters adhering to Saber's 5-part epistemic paragraph structure, enforces natural cadence variability ($CV \ge 0.50$), incorporates half-space formatting, decouples LTR statistical numbers, and maintains APA 7 compliance.

### 11. `journal-strategist`
- **File:** `.agents/agents/journal-strategist.md`
- **Classification:** Specialist Subagent (Publication Packaging Brain)
- **Role:** Publication Packaging & Peer-Review Rebuttal Strategist
- **Modern Skills Assigned:** `academic-article-writer`, `journal-submission-assistant`, `ai-academic-tone-polisher`
- **Legacy Skills Listed:** `journal_submission`
- **Tools Assigned:** Antigravity read tools + `run_command`
- **MCP Usage:** None
- **Core Responsibilities:** Extracts stand-alone empirical articles from completed dissertations, screens target WoS/Scopus/ISC journals against author guidelines, prepares submission packages (Title Page, Blind Manuscript, Cover Letter), drafts reviewer rebuttal tables.

### 12. `statistical-auditor`
- **File:** `.agents/agents/statistical-auditor.md`
- **Classification:** Independent Critic / Auditor
- **Role:** Adversarial Statistical Quality Auditor
- **Modern Skills Assigned:** `thesis-integrity-auditor`, `statistical-data-analyst`
- **Legacy Skills Listed:** `chapter4`
- **Tools Assigned:** Antigravity read tools + `run_command`
- **MCP Usage:** None
- **Core Responsibilities:** Adversarial cross-check of statistical calculations. Evaluates the Multi-Signal Anomaly Index (MSAI), checks degrees of freedom concordance ($df_{\text{error}} = N - k - 1$), audits variance deflation ($SD < 0.10 \times Range$), flags synthetic data anomalies, and issues `AUDIT_PASSED` or `FLAG_FOR_REVIEW`.

### 13. `results-auditor`
- **File:** `.agents/agents/results-auditor.md`
- **Classification:** Independent Critic / Auditor
- **Role:** Numerical & APA 7 Quality Control Auditor
- **Modern Skills Assigned:** `thesis-integrity-auditor`, `statistical-data-analyst`
- **Legacy Skills Listed:** `chapter4`
- **Tools Assigned:** Antigravity read tools + `run_command`
- **MCP Usage:** None
- **Core Responsibilities:** Strictly enforces APA 7 typography: preserves Persian leading zeros (`۰.۰۰۱`), eliminates $p = .000$, verifies 3-line table borders, checks italicization of Latin symbols (*M, SD, t, F, p*), and audits preservation of Word OMML math equations (`<m:oMath>`).

### 14. `evidence-auditor`
- **File:** `.agents/agents/evidence-auditor.md`
- **Classification:** Independent Critic / Auditor
- **Role:** Epistemic Integrity & Citation Verification Auditor
- **Modern Skills Assigned:** `academic-reference-extractor`, `irandoc-plagiarism-reducer`
- **Legacy Skills Listed:** None
- **Tools Assigned:** Antigravity read tools + `run_command`
- **MCP Usage:** None
- **Core Responsibilities:** Bidirectional concordance check between in-text citations and the reference list, screens for fabricated / ghost citations via CrossRef/PubMed API, audits Irandoc/SamimNoor similarity risk (< 20%), and purges robotic AI clichés.

### 15. `final-judge`
- **File:** `.agents/agents/final-judge.md`
- **Classification:** Independent Critic & Defense Committee Simulator
- **Role:** Defense Committee Viva Voce Simulator & Release Gatekeeper
- **Modern Skills Assigned:** `thesis-integrity-auditor`, `persian-defense-presentation-builder`
- **Legacy Skills Listed:** `defense_presentation`
- **Tools Assigned:** Antigravity read tools + `run_command`
- **MCP Usage:** None
- **Core Responsibilities:** Acts as mock defense committee chair. Simulates 5 examiner cross-examination questions, evaluates candidate defense readiness, compiles the viva voce brief, and serves as final gatekeeper before client delivery.

---

## 4. Responsibility Overlap Analysis

| Functional Domain | Assigned Agents | Overlap & Boundary Definition | Recommended Refactoring |
|---|---|---|---|
| **Statistical Analysis vs. Quality Control** | `statistical-expert`<br>`statistical-auditor`<br>`results-auditor` | `statistical-expert` plans tests and executes initial scripts; `statistical-auditor` runs adversarial MSAI anomaly checks; `results-auditor` verifies typographical formatting and APA 7 precision. Clean critic separation, but all three share `statistical-data-analyst` scripts. | Maintain strict separation of concerns; update agent frontmatters to remove legacy `chapter4` skill bindings. |
| **Literature Harvesting vs. Meta-Analysis** | `literature-expert`<br>`meta-analyst` | Both invoke `literature-harvester` to query APIs. `literature-expert` focuses on narrative inverted-triangle synthesis for Chapter 2, while `meta-analyst` extracts quantitative effect sizes ($d, r, g$) and evaluates risk of bias. | Distinct analytical goals; share underlying harvesting scripts cleanly. |
| **Methodology vs. Intervention Design** | `methodology-expert`<br>`intervention-designer` | `methodology-expert` designs research design, sampling, and validity controls; `intervention-designer` writes clinical session guides. | `methodology-expert` should focus on Chapter 3 methodology, leaving clinical treatment protocol details to `intervention-designer`. |
| **Text Polishing vs. Plagiarism Auditing** | `academic-writer`<br>`evidence-auditor` | `academic-writer` creates scholarly text; `evidence-auditor` verifies citation integrity and audits Irandoc similarity. | Clean generator-critic relationship. |

---

## 5. Stale / Legacy Skill Bindings in Agent Definitions

The following 11 agents currently reference legacy workflow skill names in their YAML frontmatter:

1. `academic-writer`: Contains `chapter4`, `chapter5`, `thesis_assembly`
2. `digital-saber`: Contains `chapter4`, `thesis_revision`
3. `evidence-auditor`: Clean (no legacy bindings)
4. `final-judge`: Contains `defense_presentation`
5. `intervention-designer`: Contains `intervention_protocol`
6. `journal-strategist`: Contains `journal_submission`
7. `literature-expert`: Contains `chapter2_literature`
8. `meta-analyst`: Clean (no legacy bindings)
9. `methodology-expert`: Contains `proposal`
10. `psychometric-expert`: Contains `scale_validation`
11. `qualitative-analyst`: Clean (no legacy bindings)
12. `results-auditor`: Contains `chapter4`
13. `statistical-auditor`: Contains `chapter4`
14. `statistical-expert`: Contains `chapter4`
15. `data-curator`: Clean (no legacy bindings)
