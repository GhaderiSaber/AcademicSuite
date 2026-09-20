# CAPABILITY_TAXONOMY.md — Formal Capability Taxonomy & Categorical Model

**Document Version:** 1.0.0 (Phase 1 Architecture Specification)  
**Status:** Canonical V1 Capability Specification  
**Operative Date:** September 2026 (1405 SH)  
**Governance:** AcademicSuite Constitutional Architecture (Directive 12, Directive 12.1, Directive 19)  

---

## 1. Executive Summary & Objective

Phase 1 formalizes the **Capability Model** for the AcademicSuite multi-agent system before modifying any agent configurations. In the V0 baseline ([AGENT_BEHAVIOR_BASELINE.md](file:///home/ghaderi-saber/Desktop/AcademicSuite/docs/architecture/AGENT_BEHAVIOR_BASELINE.md)), delegation failures occurred because managerial orchestrators possessed execution and writing privileges ("Hands"). This architectural defect tempted the orchestrator into running ad-hoc Python commands and authoring scripts directly rather than delegating to specialist workers.

To permanently resolve this structural contradiction and enforce Directive 12.1 (*Sole Orchestrator Mandate*) and Directive 19 (*The Six-Part Functional Separation Invariant*), this document defines:
1. The **Formal Capability Taxonomy** (10 discrete capabilities).
2. The **Four Functional Categories** (Brain, Eyes, Hands, Delegation).
3. The **Capability Allocation Policy** for `academic-orchestrator` (Brain + Eyes + Delegation, **NO Hands**).
4. The **Full Agent Category Allocation Matrix** across all 28 workspace agents.

---

## 2. Formal Capability Taxonomy

The system defines 10 discrete, auditable capabilities spanning cognitive reasoning, environmental sensing, state mutation, and distributed coordination:

```text
┌──────────────────────────────────────────────────────────────────────────────────┐
│                           FORMAL CAPABILITY TAXONOMY                             │
├────────────────────┬──────────────┬──────────────────┬───────────────────────────┤
│ Capability         │ Category     │ Tool / Process   │ Purpose & Invariant       │
├────────────────────┼──────────────┼──────────────────┼───────────────────────────┤
│ 1. READ_PROJECT    │ Eyes         │ view_file,       │ Read workspace configs,   │
│                    │              │ list_dir, fd     │ structures, guidelines.   │
├────────────────────┼──────────────┼──────────────────┼───────────────────────────┤
│ 2. READ_DATA       │ Eyes         │ view_file, grep  │ Read datasets (.csv,      │
│                    │              │                  │ .sav, .xlsx, .json).      │
├────────────────────┼──────────────┼──────────────────┼───────────────────────────┤
│ 3. SEARCH_WEB      │ Eyes / MCP   │ search_web,      │ External bibliometrics,   │
│                    │              │ read_url_content │ CrossRef/PubMed lookups.  │
├────────────────────┼──────────────┼──────────────────┼───────────────────────────┤
│ 4. EXECUTE_CODE    │ Hands        │ run_command      │ Deterministic Python/R    │
│                    │              │                  │ script & tool execution.  │
├────────────────────┼──────────────┼──────────────────┼───────────────────────────┤
│ 5. WRITE_ARTIFACT  │ Hands        │ write_to_file    │ Create new files on disk  │
│                    │              │                  │ (.py, .docx, .md, .json). │
├────────────────────┼──────────────┼──────────────────┼───────────────────────────┤
│ 6. EDIT_ARTIFACT   │ Hands        │ replace_content, │ Mutate and patch existing │
│                    │              │ edit_file        │ files on disk.            │
├────────────────────┼──────────────┼──────────────────┼───────────────────────────┤
│ 7. DELEGATE        │ Delegation   │ invoke_subagent  │ Spawn specialist worker   │
│                    │              │                  │ subagents with envelopes. │
├────────────────────┼──────────────┼──────────────────┼───────────────────────────┤
│ 8. MANAGE_SUBAGENTS│ Delegation   │ manage_subagents │ Inspect subagent status & │
│                    │              │                  │ lifecycle state.          │
├────────────────────┼──────────────┼──────────────────┼───────────────────────────┤
│ 9. COMMUNICATE     │ Delegation   │ send_message     │ Direct inter-agent        │
│                    │              │                  │ message dispatching.      │
├────────────────────┼──────────────┼──────────────────┼───────────────────────────┤
│ 10. AUDIT          │ Brain + Eyes │ Model reasoning  │ Adversarial verification, │
│                    │              │ + view_file      │ df checks, MSAI scoring.  │
└────────────────────┴──────────────┴──────────────────┴───────────────────────────┘
```

### Detailed Capability Specifications

1. **`READ_PROJECT`**
   - **Definition**: The capability to inspect repository organization, configurations, documentation, architectural standards, and skill instructions.
   - **Mechanisms**: `view_file`, `list_dir`, `find_by_name`.
   - **Permissible Tiers**: Tier 1 (Lead), Tier 2 (Authorities), Tier 3 (Workers), Tier 4 (Critics), Tier 5 (Learning).

2. **`READ_DATA`**
   - **Definition**: The capability to examine raw or processed empirical datasets, codebooks, and metadata schemas.
   - **Mechanisms**: `view_file`, `grep_search`.
   - **Permissible Tiers**: Tier 1, Tier 2, Tier 3, Tier 4.

3. **`SEARCH_WEB`**
   - **Definition**: The capability to harvest external literature, bibliometric citation counts, and DOI records from scholarly indices (CrossRef, PubMed, Google Scholar).
   - **Mechanisms**: `search_web`, `read_url_content`, MCP citation servers.
   - **Permissible Tiers**: Tier 2 (`methodology-expert`), Tier 3 (`research-agent`, `literature-expert`).

4. **`EXECUTE_CODE`**
   - **Definition**: The capability to run terminal processes, invoke deterministic Python/R statistical engines, and run test suites.
   - **Mechanisms**: `run_command`.
   - **Permissible Tiers**: Tier 3 (Specialist Workers) and Tier 5 (`evaluation-agent`). Strictly **FORBIDDEN** to Tier 1 Orchestrators.

5. **`WRITE_ARTIFACT`**
   - **Definition**: The capability to write new physical files to disk, including Triad deliverables (`.docx`, `.md`, `.json`) and scripts.
   - **Mechanisms**: `write_to_file`.
   - **Permissible Tiers**: Tier 3 (Specialist Workers) and Tier 5 (`skill-evolver`). Strictly **FORBIDDEN** to Tier 1 Orchestrators.

6. **`EDIT_ARTIFACT`**
   - **Definition**: The capability to perform surgical, in-place textual modifications on existing workspace files.
   - **Mechanisms**: `replace_file_content`, `edit_file`.
   - **Permissible Tiers**: Tier 3 (Specialist Workers). Strictly **FORBIDDEN** to Tier 1 Orchestrators and Tier 2/4 Critics (prevents silent rewriting).

7. **`DELEGATE`**
   - **Definition**: The capability to partition complex academic workflows into bounded stages and dispatch isolated subagents via contractual envelopes.
   - **Mechanisms**: `invoke_subagent`.
   - **Permissible Tiers**: Tier 1 (`academic-orchestrator`, `digital-saber`) and selected Tier 2 Authorities (`methodology-expert`, `statistical-expert`). Strictly **FORBIDDEN** to Tier 3 Workers.

8. **`MANAGE_SUBAGENTS`**
   - **Definition**: The capability to query subagent lifecycle states (`list`, `status`, `kill`).
   - **Mechanisms**: `manage_subagents`.
   - **Permissible Tiers**: Tier 1 (`academic-orchestrator`, `digital-saber`) and Tier 2 Authorities.

9. **`COMMUNICATE`**
   - **Definition**: The capability to exchange structured messages, peer reviews, and critique feedback between active agents.
   - **Mechanisms**: `send_message`.
   - **Permissible Tiers**: Tier 1 and Tier 2 Authorities.

10. **`AUDIT`**
    - **Definition**: The cognitive and perceptual capability to cross-check outputs against empirical ground truths, degrees of freedom, APA 7 rules, and Multi-Signal Anomaly Index (MSAI) criteria without mutating files.
    - **Mechanisms**: Brain cognitive reasoners + `view_file` + verification scripts.
    - **Permissible Tiers**: Tier 2 Authorities and Tier 4 Adversarial Critics.

---

## 3. The Four Functional Categories

All agent capabilities are classified into four mutually exclusive categories based on their ontological nature:

```text
       ┌─────────────────────────────────────────────────────────┐
       │                   THE FOUR CATEGORIES                   │
       └────────────────────────────┬────────────────────────────┘
                                    │
         ┌──────────────────────────┼──────────────────────────┐
         ▼                          ▼                          ▼
  ┌──────────────┐           ┌──────────────┐           ┌──────────────┐
  │   1. BRAIN   │           │   2. EYES    │           │   3. HANDS   │
  │ (Cognition)  │           │ (Perception) │           │  (Mutation)  │
  └──────────────┘           └──────────────┘           └──────────────┘
         ▲                                                     ▲
         │                     ┌──────────────┐                │
         └─────────────────────┤4. DELEGATION ├────────────────┘
                               │(Coordination)│
                               └──────────────┘
```

### Category 1: Brain Capabilities (Inherent Model Cognition)
Brain capabilities are intrinsic to the underlying Large Language Model (LLM) weights and reasoning tokens. They **cannot be removed or stripped by tool configurations**:
- `reason`: Epistemic reasoning, causal analysis, scientific deduction, synthesis.
- `plan`: Multi-stage decomposition, dependency scheduling, invariant checking.
- `classify`: Categorization of methodology, research designs, statistical families, data anomalies.
- `select_method`: Selecting appropriate statistical tests, psychometric models, or qualitative frameworks according to established epistemic trees.
- `interpret`: Analyzing effect sizes, model fit statistics, parameter estimates, and literature alignment.
- `decide`: Gating stage transitions, issuing pass/fail verdicts, approving delegations.

### Category 2: Eye Capabilities (Passive Environmental Perception)
Eye capabilities provide passive, read-only sensing of the environment with **zero mutation and zero side-effects**:
- `view_file`: Read file contents.
- `list_dir`: Inspect directory structure.
- `grep_search`: Fast pattern matching across text files.
- `find_by_name`: Locate files and paths matching glob expressions.

### Category 3: Hand Capabilities (Active Mutation & Computation)
Hand capabilities grant the power to modify disk state, execute arbitrary code, run calculations, and transform files. They are the **computational instruments ("The Hands")**:
- `run_command`: Execute shell commands, launch Python/R scripts, run benchmarks.
- `write_to_file`: Create new files on disk.
- `replace_file_content`: Modify existing lines within files.
- `edit_file`: Patch text blocks.

### Category 4: Delegation Capabilities (Multi-Agent Coordination)
Delegation capabilities allow an agent to orchestrate other agents, distribute workloads across isolated context spaces, and manage subagent lifecycles:
- `invoke_subagent`: Spawn subordinate worker subagents with task envelopes.
- `manage_subagents`: List, inspect, or terminate subordinate tasks.
- `send_message`: Communicate directly with another active agent.

---

## 4. Academic-Orchestrator Allocation Profile

The fundamental design flaw identified in Phase 0 was that `academic-orchestrator` possessed Hand capabilities (`run_command`, `write_to_file`), allowing it to calculate statistics and write scripts directly instead of orchestrating.

Under the V1 Capability Model, `academic-orchestrator` receives:

```yaml
academic-orchestrator:
  allocated_categories:
    - BRAIN       # Full cognitive planning, reasoning, method selection, and decision gating
    - EYES        # Full read-only perception (view_file, list_dir, grep_search, find_by_name)
    - DELEGATION  # Full multi-agent coordination (invoke_subagent, manage_subagents, send_message)
  
  forbidden_categories:
    - HANDS       # STRICTLY FORBIDDEN (NO run_command, NO write_to_file, NO replace_file_content)
```

```text
┌────────────────────────────────────────────────────────────────────────┐
│                   ACADEMIC-ORCHESTRATOR PROFILE                        │
├────────────────────────────────────────────────────────────────────────┤
│  ✅ BRAIN:       reason, plan, classify, select_method, interpret,     │
│                  decide                                                │
│  ✅ EYES:        view_file, list_dir, grep_search, find_by_name        │
│  ✅ DELEGATION:  invoke_subagent, manage_subagents, send_message       │
│                                                                        │
│  ❌ HANDS:       run_command            (REVOKED)                      │
│                  write_to_file          (REVOKED)                      │
│                  replace_file_content   (REVOKED)                      │
│                  edit_file              (REVOKED)                      │
└────────────────────────────────────────────────────────────────────────┘
```

### Why Stripping Hands Enforces Delegation
1. **Architectural Impossibility of Direct Computation**:
   When the user commands *"Calculate the repeated-measures analysis"*, the orchestrator cannot execute Python Pingouin or write `run_rm_anova.py` because it lacks `run_command` and `write_to_file`. It has no physical means to perform the calculation itself.
2. **Deterministic Delegation Forcing**:
   The only path to completion is to formulate a Contractual Delegation Envelope and dispatch `invoke_subagent` to a worker with Hands (`statistics-agent`).
3. **Purity of Managerial Role (Directive 19)**:
   The orchestrator remains purely managerial, maintaining macro-level context without polluting its token window with computational trace logs, pandas DataFrames, or low-level bash syntax.

---

## 4.1 Worker Classes: Class A — Execution Workers

Under the AcademicSuite capability model, agents possessing **Hands** are formalized into discrete worker classes. **Class A: Execution Workers** are the computational and verification engines that directly execute deterministic code, run statistical models, transform datasets, or audit evidence.

### Granted Capabilities:
- **READ (Eyes)**: `view_file`, `list_dir`, `grep_search`, `find_by_name`
- **WRITE (Hands)**: `write_to_file`
- **RUN_COMMAND (Hands)**: `run_command`

### Canonical Execution Workers:
1. `data-agent` (Raw data ingestion, screening, reverse-coding, psychometric simulation)
2. `data-curator` (Missingness diagnostics, outlier screening, demographic curation)
3. `statistics-agent` (Inferential statistics, pingouin, SEM, bootstrap mediation)
4. `psychometric-expert` (CTT, IRT, CFA, Lawshe CVR, scale validation)
5. `longitudinal-modmed-expert` (3-wave autoregressive panel modeling, PROCESS 7/14 over time)
6. `qualitative-analyst` (Reflexive Thematic Analysis, Grounded Theory, inter-coder reliability)
7. `meta-analyst` (PRISMA 2020, Cochrane RoB 2, quantitative effect size pooling)
8. `evaluation-agent` (Independent counterfactual benchmarks, regression testing)
9. `validation-agent` (Pre-flight master validator suite, Triad Invariant verification)
10. `statistical-auditor` (MSAI anomaly detector, degrees-of-freedom concordance)

### Mandatory Contractual Mandate:
Every Class A Execution Worker must state in its contract:
> **"You are an execution worker. Perform the requested deterministic work and return artifacts/evidence."**

---

## 5. Global Agent Allocation Matrix ($N = 28$ Agents)

| # | Agent Name | Tier | Category 1: BRAIN | Category 2: EYES | Category 3: HANDS | Category 4: DELEGATION | Primary Role |
|---|---|---|:---:|:---:|:---:|:---:|---|
| 1 | `academic-orchestrator` | Tier 1 (Lead) | ✅ **Yes** | ✅ **Yes** | ❌ **NO** | ✅ **Yes** | Master Orchestration & Stage Gating |
| 2 | `digital-saber` | Tier 1 (Lead) | ✅ **Yes** | ✅ **Yes** | ❌ **NO** | ✅ **Yes** | Executive Persona & Release Gate |
| 3 | `methodology-expert` | Tier 2 (Domain) | ✅ **Yes** | ✅ **Yes** | ❌ **NO** | ✅ **Yes** | Research Design & Power Authority |
| 4 | `statistical-expert` | Tier 2 (Domain) | ✅ **Yes** | ✅ **Yes** | ❌ **NO** | ✅ **Yes** | Statistical Modeling & Inference Authority |
| 5 | `academic-writer` | Tier 2 (Domain) | ✅ **Yes** | ✅ **Yes** | ✅ **Yes** | ❌ **NO** | Persian Academic Rhetoric & Triad Drafter |
| 6 | `evidence-auditor` | Tier 2 (Domain) | ✅ **Yes** | ✅ **Yes** | ❌ **NO** | ❌ **NO** | Citation Concordance & Irandoc Auditor |
| 7 | `final-judge` | Tier 2 (Domain) | ✅ **Yes** | ✅ **Yes** | ❌ **NO** | ❌ **NO** | Defense Simulator & Institutional Gate |
| 8 | `data-agent` | Tier 3 (Worker) | ✅ **Yes** | ✅ **Yes** | ✅ **Yes** | ❌ **NO** | Data Cleaning, Scaling & Imputation |
| 9 | `data-curator` | Tier 3 (Worker) | ✅ **Yes** | ✅ **Yes** | ✅ **Yes** | ❌ **NO** | Missing Patterns & Outlier Curation |
| 10 | `statistics-agent` | Tier 3 (Worker) | ✅ **Yes** | ✅ **Yes** | ✅ **Yes** | ❌ **NO** | Inferential Models, SEM & Bootstrap |
| 11 | `psychometric-expert` | Tier 3 (Worker) | ✅ **Yes** | ✅ **Yes** | ✅ **Yes** | ❌ **NO** | CTT, IRT, CFA & Scale Validation |
| 12 | `research-agent` | Tier 3 (Worker) | ✅ **Yes** | ✅ **Yes** | ✅ **Yes** | ❌ **NO** | Literature Harvester & Scaffolding |
| 13 | `literature-expert` | Tier 3 (Worker) | ✅ **Yes** | ✅ **Yes** | ✅ **Yes** | ❌ **NO** | Science Mapping & Bibliometrics |
| 14 | `intervention-designer` | Tier 3 (Worker) | ✅ **Yes** | ✅ **Yes** | ✅ **Yes** | ❌ **NO** | Clinical Protocols & Manualization |
| 15 | `qualitative-analyst` | Tier 3 (Worker) | ✅ **Yes** | ✅ **Yes** | ✅ **Yes** | ❌ **NO** | Thematic Analysis & Grounded Theory |
| 16 | `longitudinal-modmed-expert` | Tier 4 (Critic) | ✅ **Yes** | ✅ **Yes** | ✅ **Yes** | ❌ **NO** | 3-Wave Autoregressive Modeling |
| 17 | `meta-analyst` | Tier 4 (Critic) | ✅ **Yes** | ✅ **Yes** | ✅ **Yes** | ❌ **NO** | PRISMA 2020 & Quantitative Pooling |
| 18 | `statistical-auditor` | Tier 4 (Critic) | ✅ **Yes** | ✅ **Yes** | ✅ **Yes** | ❌ **NO** | Assumptions, df Concordance & MSAI |
| 19 | `results-auditor` | Tier 4 (Critic) | ✅ **Yes** | ✅ **Yes** | ❌ **NO** | ❌ **NO** | APA 7 Precision & Typography Auditor |
| 20 | `academic-challenger` | Tier 4 (Critic) | ✅ **Yes** | ✅ **Yes** | ❌ **NO** | ❌ **NO** | Adversarial Method & Bias Challenger |
| 21 | `journal-strategist` | Tier 4 (Critic) | ✅ **Yes** | ✅ **Yes** | ❌ **NO** | ❌ **NO** | Journal Scope Matching & Rebuttal |
| 22 | `validation-agent` | Tier 4 (Critic) | ✅ **Yes** | ✅ **Yes** | ✅ **Yes** | ❌ **NO** | Triad Artifact & Release Verification |
| 23 | `trajectory-analyzer` | Tier 5 (Learning) | ❌ **NO** | ✅ **Yes** | ❌ **NO** | ❌ **NO** | Observable Trajectory Reconstructor |
| 24 | `behavior-analyst` | Tier 5 (Learning) | ✅ **Yes** | ✅ **Yes** | ❌ **NO** | ❌ **NO** | Causal Defect & Root Cause Analyst |
| 25 | `knowledge-curator` | Tier 5 (Learning) | ✅ **Yes** | ✅ **Yes** | ❌ **NO** | ❌ **NO** | Anti-Pattern & Lesson Synthesizer |
| 26 | `curriculum-builder` | Tier 5 (Learning) | ✅ **Yes** | ✅ **Yes** | ❌ **NO** | ❌ **NO** | Graduated Benchmark Designer |
| 27 | `skill-evolver` | Tier 5 (Learning) | ✅ **Yes** | ✅ **Yes** | ✅ **Yes** | ❌ **NO** | Staging Sandbox Mutation Synthesizer |
| 28 | `evaluation-agent` | Tier 5 (Learning) | ✅ **Yes** | ✅ **Yes** | ✅ **Yes** | ❌ **NO** | Deterministic Benchmark Tester |

---

## 6. Implementation & Enforcement Strategy for Future Phases

The capability model defined herein will be enacted across three distinct layers:

1. **Declarative Tool Boundaries (`agent.md` Frontmatter)**:
   The `tools` array of `academic-orchestrator` will contain strictly:
   ```yaml
   tools:
     - invoke_subagent
     - manage_subagents
     - send_message
     - view_file
     - list_dir
     - grep_search
     - find_by_name
     - ask_question
   ```
   `run_command`, `write_to_file`, and `replace_file_content` will be omitted entirely.

2. **Mechanical Interception (`PreToolUse` Lifecycle Hook)**:
   In the event of prompt injection or model hallucination attempting to invoke Hand tools, the Antigravity `PreToolUse` hook will intercept the invocation and mechanically deny execution:
   ```python
   # Enforced in .agents/hooks/safety_hooks.py
   if "academic-orchestrator" in caller:
       if tool_name in ("run_command", "write_to_file", "replace_file_content", "edit_file"):
           return {
               "decision": "deny",
               "reason": (
                   f"CAPABILITY VIOLATION: Academic-Orchestrator has no Hand capabilities. "
                   f"Tool '{tool_name}' is forbidden. Delegate to a specialist worker subagent."
               )
           }
   ```

3. **Factory Contract Schema Validation (`agent_factory.py`)**:
   The specification compiler will assert that any agent with `role: orchestrator` strictly satisfies:
   `can_execute_code == False` and `can_write == False`.
