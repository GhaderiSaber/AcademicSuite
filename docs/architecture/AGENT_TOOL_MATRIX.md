# AGENT_TOOL_MATRIX.md — Complete Agent Tool & Capability Matrix

**Document Version:** 1.0.0 (Phase 0 Architecture Freeze)  
**Status:** Canonical V0 Baseline  
**Scope:** All 28 Discovered Workspace Agents  
**Operative Date:** September 2026 (1405 SH)  

---

## 1. Executive Summary

This document freezes and records the exact tool access, skill bindings, execution privileges, and delegation permissions across all 28 agents in AcademicSuite. 

### Key Privilege Metrics (N = 28 Agents)
- **Can Delegate (`invoke_subagent`):** 4 agents (14.3%) — `academic-orchestrator`, `digital-saber`, `methodology-expert`, `statistical-expert`
- **Can Execute Code (`run_command`):** 20 agents (71.4%)
- **Can Write Files (`write_to_file` / `replace_file_content`):** 27 agents (96.4%) — Only `trajectory-analyzer` is strictly read-only
- **Can Act as Main Agent (`mainAgent: true`):** 5 agents (17.9%) — `academic-orchestrator`, `digital-saber`, `methodology-expert`, `statistical-expert`, `evidence-auditor`
- **Can Act as Subagent (`subagent: true`):** 28 agents (100.0%)

---

## 2. High-Level Agent Tool Summary Table

| # | Agent Name | Tier | Main | Sub | Code Exec (`run_command`) | Write Files | Delegate (`invoke_subagent`) | Primary Bound Skills |
|---|---|---|:---:|:---:|:---:|:---:|:---:|---|
| 1 | `academic-challenger` | Tier 4 (Critic) | No | Yes | Yes | Yes | No | `academic-adaptive-context`, `thesis-integrity-auditor` |
| 2 | `academic-orchestrator` | Tier 1 (Lead) | Yes | Yes | **Yes** | **Yes** | **Yes** | `academic-suite-orchestrator`, `academic-adaptive-context`, `digital-twin-academic-consultant`, `thesis-integrity-auditor` |
| 3 | `academic-writer` | Tier 2 (Domain) | No | Yes | Yes | Yes | No | `chapter-4-writing`, `persian-literature-review-builder`, `persian-discussion-builder`, `persian-thesis-builder`, `academic-article-writer`, `ai-academic-tone-polisher`, `apa-reporting`, `psychological-intervention-protocol-builder`, `journal-submission-assistant`, `persian-defense-presentation-builder` |
| 4 | `behavior-analyst` | Tier 5 (Learning) | No | Yes | No | Yes | No | `academic-adaptive-context`, `thesis-integrity-auditor` |
| 5 | `curriculum-builder` | Tier 5 (Learning) | No | Yes | No | Yes | No | `academic-adaptive-context`, `thesis-integrity-auditor` |
| 6 | `data-agent` | Tier 3 (Worker) | No | Yes | Yes | Yes | No | `data-cleaning`, `data-audit`, `psychometric-scale-resolver`, `psychometric-data-simulator` |
| 7 | `data-curator` | Tier 3 (Worker) | No | Yes | Yes | Yes | No | `data-audit`, `data-cleaning`, `psychometric-scale-resolver` |
| 8 | `digital-saber` | Tier 1 (Lead) | Yes | Yes | Yes | Yes | Yes | `academic-suite-orchestrator`, `digital-twin-academic-consultant`, `thesis-integrity-auditor`, `chapter-4-writing`, `persian-thesis-revision-assistant` |
| 9 | `evaluation-agent` | Tier 5 (Learning) | No | Yes | Yes | Yes | No | `academic-adaptive-context`, `thesis-integrity-auditor` |
| 10 | `evidence-auditor` | Tier 2 (Domain) | Yes | Yes | Yes | Yes | No | `thesis-integrity-auditor`, `irandoc-plagiarism-reducer`, `academic-reference-extractor` |
| 11 | `final-judge` | Tier 2 (Domain) | Yes | Yes | Yes | Yes | No | `thesis-integrity-auditor`, `persian-defense-presentation-builder` |
| 12 | `intervention-designer` | Tier 3 (Worker) | No | Yes | No | Yes | No | `psychological-intervention-protocol-builder`, `persian-proposal-builder` |
| 13 | `journal-strategist` | Tier 4 (Critic) | No | Yes | Yes | Yes | No | `journal-submission-assistant`, `academic-article-writer` |
| 14 | `knowledge-curator` | Tier 5 (Learning) | No | Yes | No | Yes | No | `academic-adaptive-context`, `thesis-integrity-auditor` |
| 15 | `literature-expert` | Tier 3 (Worker) | No | Yes | Yes | Yes | No | `literature-harvester`, `literature-review`, `bibliometric-network-analyst` |
| 16 | `longitudinal-modmed-expert` | Tier 4 (Critic) | No | Yes | Yes | Yes | No | `longitudinal-moderated-mediation`, `mediation`, `apa-reporting` |
| 17 | `meta-analyst` | Tier 4 (Critic) | No | Yes | Yes | Yes | No | `systematic-review-meta-analyst`, `gpower-sample-size-calculator` |
| 18 | `methodology-expert` | Tier 2 (Domain) | Yes | Yes | Yes | Yes | Yes | `methodology-review`, `academic-adaptive-context`, `gpower-sample-size-calculator`, `persian-proposal-builder` |
| 19 | `psychometric-expert` | Tier 3 (Worker) | No | Yes | Yes | Yes | No | `psychometric-scale-validator`, `academic-adaptive-context`, `cfa`, `psychometric-scale-resolver`, `reliability-analysis` |
| 20 | `qualitative-analyst` | Tier 3 (Worker) | No | Yes | Yes | Yes | No | `qualitative-data-analyst` |
| 21 | `research-agent` | Tier 3 (Worker) | No | Yes | Yes | Yes | No | `literature-review`, `literature-harvester`, `gpower-sample-size-calculator` |
| 22 | `results-auditor` | Tier 4 (Critic) | No | Yes | No | Yes | No | `apa-reporting`, `academic-adaptive-context`, `thesis-integrity-auditor` |
| 23 | `skill-evolver` | Tier 5 (Learning) | No | Yes | No | Yes | No | `academic-adaptive-context`, `thesis-integrity-auditor` |
| 24 | `statistical-auditor` | Tier 4 (Critic) | No | Yes | Yes | Yes | No | `thesis-integrity-auditor`, `academic-adaptive-context`, `data-audit` |
| 25 | `statistical-expert` | Tier 2 (Domain) | Yes | Yes | **No** | **Yes** | **Yes** | `sem`, `cfa`, `mediation`, `moderation`, `regression`, `statistical-data-analyst` |
| 26 | `statistics-agent` | Tier 3 (Worker) | No | Yes | Yes | Yes | No | `statistical-data-analyst`, `academic-adaptive-context`, `regression`, `mediation`, `moderation`, `descriptive-statistics`, `reliability-analysis` |
| 27 | `trajectory-analyzer` | Tier 5 (Learning) | No | Yes | No | No | No | `academic-adaptive-context`, `thesis-integrity-auditor` |
| 28 | `validation-agent` | Tier 4 (Critic) | No | Yes | Yes | Yes | No | `thesis-integrity-auditor`, `academic-adaptive-context`, `apa-reporting` |

---

## 3. Authoritative YAML Tool Matrix (All 28 Agents)

```yaml
agent:
  name: academic-challenger
  mainAgent: false
  subagent: true
  tools:
    - view_file
    - list_dir
    - grep_search
    - find_by_name
    - write_to_file
    - run_command
  skills:
    - academic-adaptive-context
    - thesis-integrity-auditor
  mcpServers: []
  can_execute_code: true
  can_write: true
  can_delegate: false
  intended_role: "Adversarial Methodological, Statistical & Publication Bias Challenger"

agent:
  name: academic-orchestrator
  mainAgent: true
  subagent: true
  tools:
    - invoke_subagent
    - manage_subagents
    - send_message
    - view_file
    - list_dir
    - grep_search
    - find_by_name
    - write_to_file
    - run_command
    - ask_question
  skills:
    - academic-suite-orchestrator
    - academic-adaptive-context
    - digital-twin-academic-consultant
    - thesis-integrity-auditor
  mcpServers: []
  can_execute_code: true
  can_write: true
  can_delegate: true
  intended_role: "Master Academic Orchestrator & Research Project Lead"

agent:
  name: academic-writer
  mainAgent: false
  subagent: true
  tools:
    - view_file
    - list_dir
    - grep_search
    - find_by_name
    - write_to_file
    - run_command
  skills:
    - chapter-4-writing
    - persian-literature-review-builder
    - persian-discussion-builder
    - persian-thesis-builder
    - academic-article-writer
    - ai-academic-tone-polisher
    - apa-reporting
    - psychological-intervention-protocol-builder
    - journal-submission-assistant
    - persian-defense-presentation-builder
  mcpServers: []
  can_execute_code: true
  can_write: true
  can_delegate: false
  intended_role: "Master Academic Chapter Drafter & Persian Rhetoric Specialist"

agent:
  name: behavior-analyst
  mainAgent: false
  subagent: true
  tools:
    - view_file
    - list_dir
    - grep_search
    - find_by_name
    - write_to_file
  skills:
    - academic-adaptive-context
    - thesis-integrity-auditor
  mcpServers: []
  can_execute_code: false
  can_write: true
  can_delegate: false
  intended_role: "Causal Behavioral Defect & Root Cause Analyst"

agent:
  name: curriculum-builder
  mainAgent: false
  subagent: true
  tools:
    - view_file
    - list_dir
    - grep_search
    - find_by_name
    - write_to_file
  skills:
    - academic-adaptive-context
    - thesis-integrity-auditor
  mcpServers: []
  can_execute_code: false
  can_write: true
  can_delegate: false
  intended_role: "Graduated Curriculum & Challenge Benchmark Designer"

agent:
  name: data-agent
  mainAgent: false
  subagent: true
  tools:
    - view_file
    - list_dir
    - grep_search
    - find_by_name
    - write_to_file
    - run_command
  skills:
    - data-cleaning
    - data-audit
    - psychometric-scale-resolver
    - psychometric-data-simulator
  mcpServers: []
  can_execute_code: true
  can_write: true
  can_delegate: false
  intended_role: "Raw Dataset Ingestion, Quality Screening & Psychometric Specialist"

agent:
  name: data-curator
  mainAgent: false
  subagent: true
  tools:
    - view_file
    - list_dir
    - grep_search
    - find_by_name
    - write_to_file
    - run_command
  skills:
    - data-audit
    - data-cleaning
    - psychometric-scale-resolver
  mcpServers: []
  can_execute_code: true
  can_write: true
  can_delegate: false
  intended_role: "Dataset Curation, Outlier Screening & Missing Pattern Specialist"

agent:
  name: digital-saber
  mainAgent: true
  subagent: true
  tools:
    - invoke_subagent
    - manage_subagents
    - send_message
    - view_file
    - list_dir
    - grep_search
    - find_by_name
    - write_to_file
    - run_command
    - ask_question
  skills:
    - academic-suite-orchestrator
    - digital-twin-academic-consultant
    - thesis-integrity-auditor
    - chapter-4-writing
    - persian-thesis-revision-assistant
  mcpServers: []
  can_execute_code: true
  can_write: true
  can_delegate: true
  intended_role: "Master Research Project Lead, Cognitive Architect & Digital Twin of Saber Ghaderi"

agent:
  name: evaluation-agent
  mainAgent: false
  subagent: true
  tools:
    - view_file
    - list_dir
    - grep_search
    - find_by_name
    - write_to_file
    - run_command
  skills:
    - academic-adaptive-context
    - thesis-integrity-auditor
  mcpServers: []
  can_execute_code: true
  can_write: true
  can_delegate: false
  intended_role: "Independent Counterfactual Benchmark & Evaluation Lab Tester"

agent:
  name: evidence-auditor
  mainAgent: true
  subagent: true
  tools:
    - view_file
    - list_dir
    - grep_search
    - find_by_name
    - write_to_file
    - run_command
  skills:
    - thesis-integrity-auditor
    - irandoc-plagiarism-reducer
    - academic-reference-extractor
  mcpServers: []
  can_execute_code: true
  can_write: true
  can_delegate: false
  intended_role: "Epistemic Evidence, Bibliographic Reconciliation & Anti-Plagiarism Authority"

agent:
  name: final-judge
  mainAgent: true
  subagent: true
  tools:
    - view_file
    - list_dir
    - grep_search
    - find_by_name
    - write_to_file
    - run_command
  skills:
    - thesis-integrity-auditor
    - persian-defense-presentation-builder
  mcpServers: []
  can_execute_code: true
  can_write: true
  can_delegate: false
  intended_role: "Viva Voce Defense Simulator, Institutional Gatekeeper & Release Authority"

agent:
  name: intervention-designer
  mainAgent: false
  subagent: true
  tools:
    - view_file
    - list_dir
    - grep_search
    - find_by_name
    - write_to_file
  skills:
    - psychological-intervention-protocol-builder
    - persian-proposal-builder
  mcpServers: []
  can_execute_code: false
  can_write: true
  can_delegate: false
  intended_role: "Clinical Protocol, Manualization & Fidelity Sheet Specialist"

agent:
  name: journal-strategist
  mainAgent: false
  subagent: true
  tools:
    - view_file
    - list_dir
    - grep_search
    - find_by_name
    - write_to_file
    - run_command
  skills:
    - journal-submission-assistant
    - academic-article-writer
  mcpServers: []
  can_execute_code: true
  can_write: true
  can_delegate: false
  intended_role: "Academic Journal Matching & Peer-Review Rebuttal Specialist"

agent:
  name: knowledge-curator
  mainAgent: false
  subagent: true
  tools:
    - view_file
    - list_dir
    - grep_search
    - find_by_name
    - write_to_file
  skills:
    - academic-adaptive-context
    - thesis-integrity-auditor
  mcpServers: []
  can_execute_code: false
  can_write: true
  can_delegate: false
  intended_role: "Epistemic Knowledge Distiller & Anti-Pattern Cataloger"

agent:
  name: literature-expert
  mainAgent: false
  subagent: true
  tools:
    - view_file
    - list_dir
    - grep_search
    - find_by_name
    - write_to_file
    - run_command
  skills:
    - literature-harvester
    - literature-review
    - bibliometric-network-analyst
  mcpServers: []
  can_execute_code: true
  can_write: true
  can_delegate: false
  intended_role: "Literature Synthesis & Bibliometric Matrix Specialist"

agent:
  name: longitudinal-modmed-expert
  mainAgent: false
  subagent: true
  tools:
    - view_file
    - list_dir
    - grep_search
    - find_by_name
    - write_to_file
    - run_command
  skills:
    - longitudinal-moderated-mediation
    - mediation
    - apa-reporting
  mcpServers: []
  can_execute_code: true
  can_write: true
  can_delegate: false
  intended_role: "3-Wave Longitudinal Moderated Mediation Specialist"

agent:
  name: meta-analyst
  mainAgent: false
  subagent: true
  tools:
    - view_file
    - list_dir
    - grep_search
    - find_by_name
    - write_to_file
    - run_command
  skills:
    - systematic-review-meta-analyst
    - gpower-sample-size-calculator
  mcpServers: []
  can_execute_code: true
  can_write: true
  can_delegate: false
  intended_role: "PRISMA 2020 Systematic Review & Quantitative Meta-Analyst"

agent:
  name: methodology-expert
  mainAgent: true
  subagent: true
  tools:
    - invoke_subagent
    - manage_subagents
    - send_message
    - view_file
    - list_dir
    - grep_search
    - find_by_name
    - write_to_file
    - run_command
  skills:
    - methodology-review
    - academic-adaptive-context
    - gpower-sample-size-calculator
    - persian-proposal-builder
  mcpServers: []
  can_execute_code: true
  can_write: true
  can_delegate: true
  intended_role: "Research Methodology, Experimental Design & Power Authority"

agent:
  name: psychometric-expert
  mainAgent: false
  subagent: true
  tools:
    - view_file
    - list_dir
    - grep_search
    - find_by_name
    - write_to_file
    - run_command
  skills:
    - psychometric-scale-validator
    - academic-adaptive-context
    - cfa
    - psychometric-scale-resolver
    - reliability-analysis
  mcpServers: []
  can_execute_code: true
  can_write: true
  can_delegate: false
  intended_role: "Psychometric Resolution, Classical Test Theory & IRT Specialist"

agent:
  name: qualitative-analyst
  mainAgent: false
  subagent: true
  tools:
    - view_file
    - list_dir
    - grep_search
    - find_by_name
    - write_to_file
    - run_command
  skills:
    - qualitative-data-analyst
  mcpServers: []
  can_execute_code: true
  can_write: true
  can_delegate: false
  intended_role: "Reflexive Thematic Analysis & Grounded Theory Specialist"

agent:
  name: research-agent
  mainAgent: false
  subagent: true
  tools:
    - view_file
    - list_dir
    - grep_search
    - find_by_name
    - write_to_file
    - run_command
  skills:
    - literature-review
    - literature-harvester
    - gpower-sample-size-calculator
  mcpServers: []
  can_execute_code: true
  can_write: true
  can_delegate: false
  intended_role: "Scientific Literature Harvester & Research Question Architect"

agent:
  name: results-auditor
  mainAgent: false
  subagent: true
  tools:
    - view_file
    - list_dir
    - grep_search
    - find_by_name
    - write_to_file
  skills:
    - apa-reporting
    - academic-adaptive-context
    - thesis-integrity-auditor
  mcpServers: []
  can_execute_code: false
  can_write: true
  can_delegate: false
  intended_role: "APA 7 Formatting, Mathematical Precision & Typography Auditor"

agent:
  name: skill-evolver
  mainAgent: false
  subagent: true
  tools:
    - view_file
    - list_dir
    - grep_search
    - find_by_name
    - write_to_file
  skills:
    - academic-adaptive-context
    - thesis-integrity-auditor
  mcpServers: []
  can_execute_code: false
  can_write: true
  can_delegate: false
  intended_role: "Skill Mutation Synthesizer & Behavioral Candidate Designer"

agent:
  name: statistical-auditor
  mainAgent: false
  subagent: true
  tools:
    - view_file
    - list_dir
    - grep_search
    - find_by_name
    - write_to_file
    - run_command
  skills:
    - thesis-integrity-auditor
    - academic-adaptive-context
    - data-audit
  mcpServers: []
  can_execute_code: true
  can_write: true
  can_delegate: false
  intended_role: "Parametric Assumptions, Degrees of Freedom & MSAI Anomaly Auditor"

agent:
  name: statistical-expert
  mainAgent: true
  subagent: true
  tools:
    - invoke_subagent
    - manage_subagents
    - send_message
    - view_file
    - list_dir
    - grep_search
    - find_by_name
    - write_to_file
  skills:
    - sem
    - cfa
    - mediation
    - moderation
    - regression
    - statistical-data-analyst
  mcpServers: []
  can_execute_code: false
  can_write: true
  can_delegate: true
  intended_role: "Statistical Modeling, Parametric Estimation & Inference Authority"

agent:
  name: statistics-agent
  mainAgent: false
  subagent: true
  tools:
    - view_file
    - list_dir
    - grep_search
    - find_by_name
    - write_to_file
    - run_command
  skills:
    - statistical-data-analyst
    - academic-adaptive-context
    - regression
    - mediation
    - moderation
    - descriptive-statistics
    - reliability-analysis
  mcpServers: []
  can_execute_code: true
  can_write: true
  can_delegate: false
  intended_role: "Inferential Modeling, Parametric Hypothesis Testing & SEM Specialist"

agent:
  name: trajectory-analyzer
  mainAgent: false
  subagent: true
  tools:
    - view_file
    - list_dir
    - grep_search
    - find_by_name
  skills:
    - academic-adaptive-context
    - thesis-integrity-auditor
  mcpServers: []
  can_execute_code: false
  can_write: false
  can_delegate: false
  intended_role: "Observable Trajectory Reconstructor & Execution Chronologist"

agent:
  name: validation-agent
  mainAgent: false
  subagent: true
  tools:
    - view_file
    - list_dir
    - grep_search
    - find_by_name
    - write_to_file
    - run_command
  skills:
    - thesis-integrity-auditor
    - academic-adaptive-context
    - apa-reporting
  mcpServers: []
  can_execute_code: true
  can_write: true
  can_delegate: false
  intended_role: "Independent Quality Assurance & Pre-Flight Release Gatekeeper"
```

---

## 4. Architectural Analysis & Structural Contradictions

### Contradiction 1: The Orchestrator's Code Execution Hazard
- `academic-orchestrator` frontmatter declares `tools: [..., run_command, write_to_file]`.
- Its contract states: *"CANNOT Calculate, estimate, or hallucinate statistical numbers mentally... Delegates to data-agent, statistics-agent, academic-writer."*
- **Empirical Baseline Defect:** Because the orchestrator possesses `run_command`, it executed bash scripts and Python calculations directly during Task 1 and Task 2, completely bypassing worker agents (`data-agent`, `statistics-agent`).
- **Contrast with `statistical-expert`:** By contrast, `statistical-expert` has `can_execute_code: false` (no `run_command`), forcing it to delegate all computation to `statistics-agent`.

### Contradiction 2: Delegation Concentration
- Only 4 agents possess `invoke_subagent`. All worker subagents (`statistics-agent`, `data-agent`, `academic-writer`) have `can_delegate: false`.
- While worker isolation is desirable, Domain Authorities such as `academic-writer` cannot invoke `results-auditor` directly, requiring all cross-checking to cycle back through the orchestrator.
