# AcademicSuite Agent Inventory & Forensic Audit (01_CURRENT_AGENT_INVENTORY.md)

**Document Version:** 1.0.0  
**Status:** READ-ONLY BASELINE AUDIT COMPLETE  
**Operative Temporal Reality:** 2026 (1405 SH)  
**Total Agents Analyzed:** 22 Existing Roles + 1 Planned Role (`academic-challenger`)  

---

## 1. Inventory Summary Table

| Index | Agent Identifier | Operational Tier (Contract) | mainAgent | subagent | model | Frontmatter Tools | Frontmatter Skills | Proposed Classification |
| :---: | :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| 1 | `academic-orchestrator` | Tier 1 Conductor | True | False | pro | 10 | 3 | **DURABLE AGENT** (Co-Lead Conductor) |
| 2 | `academic-writer` | Tier 2 Specialist | *MISSING* | *MISSING* | *MISSING* | 0 | 7 | **DURABLE AGENT** (Absorbs `writing-agent`) |
| 3 | `data-agent` | Tier 2 Specialist | False | True | flash | 6 | 4 | **SUBAGENT** (Absorbs `data-curator`) |
| 4 | `data-curator` | Tier 2 Specialist | *MISSING* | *MISSING* | *MISSING* | 0 | 2 | **MERGED** (Merge into `data-agent`) |
| 5 | `digital-saber` | Tier 1 Master Lead | *MISSING* | *MISSING* | *MISSING* | 0 | 5 | **DURABLE AGENT** (Principal / Twin) |
| 6 | `evidence-auditor` | Tier 2 Specialist | *MISSING* | *MISSING* | *MISSING* | 0 | 2 | **DURABLE AGENT** (Adversarial Critic) |
| 7 | `final-judge` | Tier 1 Gatekeeper | *MISSING* | *MISSING* | *MISSING* | 0 | 3 | **DURABLE AGENT** (Viva Voce Committee) |
| 8 | `intervention-designer` | Tier 2 Specialist | *MISSING* | *MISSING* | *MISSING* | 0 | 2 | **SUBAGENT** (Clinical / Protocol) |
| 9 | `journal-strategist` | Tier 2 Specialist | *MISSING* | *MISSING* | *MISSING* | 0 | 4 | **SUBAGENT** (Publication Packaging) |
| 10 | `literature-expert` | Tier 2 Specialist | *MISSING* | *MISSING* | *MISSING* | 0 | 5 | **SUBAGENT** (Harvesting / Mapping) |
| 11 | `longitudinal-modmed-expert` | Tier 2 Specialist | *MISSING* | *MISSING* | *MISSING* | 0 | 3 | **SUBAGENT** (Longitudinal SEM) |
| 12 | `meta-analyst` | Tier 2 Specialist | *MISSING* | *MISSING* | *MISSING* | 0 | 2 | **SUBAGENT** (PRISMA / Meta-Analysis) |
| 13 | `methodology-expert` | Tier 2 Specialist | *MISSING* | *MISSING* | *MISSING* | 0 | 4 | **DURABLE AGENT** (Research Methodology) |
| 14 | `psychometric-expert` | Tier 2 Specialist | *MISSING* | *MISSING* | *MISSING* | 0 | 4 | **SUBAGENT** (Scale Standardization) |
| 15 | `qualitative-analyst` | Tier 2 Specialist | *MISSING* | *MISSING* | *MISSING* | 0 | 1 | **SUBAGENT** (Thematic / Grounded Theory)|
| 16 | `research-agent` | Tier 2 Specialist | False | True | pro | 8 | 8 | **SUBAGENT** (Broad Research Worker) |
| 17 | `results-auditor` | Tier 2 Specialist | *MISSING* | *MISSING* | *MISSING* | 0 | 3 | **SUBAGENT** (APA 7 / OMML Critic) |
| 18 | `statistical-auditor` | Tier 2 Specialist | *MISSING* | *MISSING* | *MISSING* | 0 | 3 | **SUBAGENT** (Assumptions / MSAI Critic) |
| 19 | `statistical-expert` | Tier 2 Specialist | *MISSING* | *MISSING* | *MISSING* | 0 | 4 | **DURABLE AGENT** (Absorbs `statistics-agent`)|
| 20 | `statistics-agent` | Tier 2 Specialist | False | True | pro | 6 | 4 | **MERGED** (Merge into `statistical-expert`)|
| 21 | `validation-agent` | Tier 2 Critic | False | True | pro | 6 | 4 | **SUBAGENT** (Integrity / Artifact Gate) |
| 22 | `writing-agent` | Tier 2 Specialist | False | True | pro | 7 | 7 | **MERGED** (Merge into `academic-writer`) |
| 23 | `academic-challenger` | *PLANNED* | *PLANNED* | *PLANNED* | *PLANNED* | *PLANNED* | *PLANNED* | **SUBAGENT** (New Adversarial Critic) |

---

## 2. Granular Agent-by-Agent Profiles

### 1. `academic-orchestrator`
1. **File Location**:
   - Runtime Prompt: `.agents/agents/academic-orchestrator/agent.md`
   - Contract: `.agents/agents/academic-orchestrator/contract.md`
   - Flat Symlink: `.agents/agents/academic-orchestrator.md -> academic-orchestrator/agent.md`
2. **Current Frontmatter**:
   ```yaml
   name: academic-orchestrator
   description: Primary academic master conductor and research project lead...
   role: Master Academic Orchestrator & Research Project Lead
   mainAgent: true
   subagent: false
   model: pro
   command_execution_policy: deterministic_hands_only
   tools:
     - invoke_subagent
     - manage_subagents
     - send_message
     - view_file
     - list_dir
     - grep_search
     - find_by_name
     - run_command
     - write_to_file
     - ask_question
   skills:
     - academic-suite-orchestrator
     - digital-twin-academic-consultant
     - thesis-integrity-auditor
   ```
3. **Role Intent**: Main / User-Facing Conductor.
4. **Current Tools**:
   - Frontmatter: 10 tools (`invoke_subagent`, `manage_subagents`, `send_message`, `view_file`, `list_dir`, `grep_search`, `find_by_name`, `run_command`, `write_to_file`, `ask_question`).
   - Contract: `invoke_subagent`, `manage_subagents`, `send_message`, `view_file`, `write_to_file`, `replace_file_content`, `run_command`, `list_dir`, `grep_search`, `find_by_name`, `ask_question`.
5. **Current Skills**:
   - Frontmatter: `academic-suite-orchestrator`, `digital-twin-academic-consultant`, `thesis-integrity-auditor`.
   - Contract: `academic-suite-orchestrator`, `digital-twin-academic-consultant`, `thesis-integrity-auditor`.
6. **MCP Access**: None (0 configured).
7. **Ability to Invoke Agents**: Full native ability (`invoke_subagent`, `manage_subagents`, `send_message` declared in frontmatter).
8. **Inbound Dependencies**:
   - Scripts: `scripts/orchestrator_dependency_resolver.py`, `scripts/academic_state_manager.py`.
   - Contracts: `validation-agent/contract.md` (hands off back to `academic-orchestrator`).
   - Tests: `tests/test_orchestrator.py`, `tests/test_agent_contracts.py`.
9. **Outbound Invocations**:
   - Invokes `research-agent`, `data-agent`, `statistics-agent`, `writing-agent`, `validation-agent`.
10. **Responsibility Classification**: Orchestration.
11. **Overlap**: Partially overlaps with `digital-saber` in pipeline planning and stage coordination.
12. **Target Classification**: **DURABLE AGENT** (Co-Lead Execution Conductor).
13. **Migration Risks**: Low risk; already has native Antigravity frontmatter. Changing its API could break `academic_state_manager.py` and `test_orchestrator.py`.

---

### 2. `academic-writer`
1. **File Location**:
   - Runtime Prompt: `.agents/agents/academic-writer/agent.md`
   - Contract: `.agents/agents/academic-writer/contract.md`
   - Flat Symlink: `.agents/agents/academic-writer.md -> academic-writer/agent.md`
2. **Current Frontmatter**:
   ```yaml
   name: academic-writer
   description: Master academic chapter drafter and Persian rhetoric specialist...
   role: Persian Academic Chapter Drafter & Rhetoric Specialist
   skills:
     - persian-thesis-builder
     - persian-discussion-builder
     - academic-article-writer
     - ai-academic-tone-polisher
     - chapter-4-writing
     - persian-discussion-builder
     - persian-thesis-builder
   ```
3. **Role Intent**: Worker / Specialist Drafter (intended in Phase 4 to be master drafter).
4. **Current Tools**:
   - Frontmatter: **MISSING (0 tools)** -> Falls back to read-only in Antigravity!
   - Contract: `view_file`, `write_to_file`, `replace_file_content`, `run_command`, `list_dir`, `grep_search`, `find_by_name`.
5. **Current Skills**:
   - Frontmatter: `persian-thesis-builder`, `persian-discussion-builder`, `academic-article-writer`, `ai-academic-tone-polisher`, `chapter-4-writing` (contains duplicate entries).
   - Contract: Same 5 unique skills.
6. **MCP Access**: None.
7. **Ability to Invoke Agents**: None in frontmatter; Contract specifies no invocation tools.
8. **Inbound Dependencies**:
   - Contracts: `digital-saber/contract.md`.
   - Tests: `tests/test_agent_contracts.py`.
9. **Outbound Invocations**: None (hands off drafts to `results-auditor` and `evidence-auditor`).
10. **Responsibility Classification**: Writing & Formatting.
11. **Overlap**: **100% duplicate of `writing-agent`**. Both share the exact role title, system prompt structure, and skill sets.
12. **Target Classification**: **DURABLE AGENT** (Master Academic Drafter, absorbing `writing-agent`).
13. **Migration Risks**: High risk of silent failure if frontmatter tools are not added (cannot write `.docx` or `.md` files without `write_to_file`). Merging `writing-agent` requires updating `scripts/academic_task_router.py` to point to `academic-writer`.

---

### 3. `data-agent`
1. **File Location**:
   - Runtime Prompt: `.agents/agents/data-agent/agent.md`
   - Contract: `.agents/agents/data-agent/contract.md`
   - Flat Symlink: `.agents/agents/data-agent.md -> data-agent/agent.md`
2. **Current Frontmatter**:
   ```yaml
   name: data-agent
   description: Specialized domain subagent for raw dataset ingestion...
   role: Data Hygiene, Missingness & Psychometric Screening Specialist
   mainAgent: false
   subagent: true
   model: flash
   command_execution_policy: deterministic_hands_only
   tools:
     - view_file
     - list_dir
     - grep_search
     - find_by_name
     - run_command
     - write_to_file
   skills:
     - statistical-data-analyst
     - psychometric-scale-resolver
     - psychometric-scale-validator
     - psychometric-data-simulator
   ```
3. **Role Intent**: Worker (Domain Subagent).
4. **Current Tools**:
   - Frontmatter: `view_file`, `list_dir`, `grep_search`, `find_by_name`, `run_command`, `write_to_file`.
   - Contract: Matches frontmatter.
5. **Current Skills**:
   - Frontmatter: `statistical-data-analyst`, `psychometric-scale-resolver`, `psychometric-scale-validator`, `psychometric-data-simulator`.
   - Contract: `data-cleaning`, `data-audit`, `psychometric-scale-resolver`, `psychometric-data-simulator`. (Notice discrepancy: contract references `data-cleaning` and `data-audit`, while frontmatter references `statistical-data-analyst` and `psychometric-scale-validator`).
6. **MCP Access**: None.
7. **Ability to Invoke Agents**: None.
8. **Inbound Dependencies**:
   - Scripts: `scripts/academic_task_router.py`, `scripts/orchestrator_dependency_resolver.py`.
   - Contracts: `statistics-agent/contract.md`.
   - Tests: 5 vertical slice test files (`test_vertical_slice_experimental.py`, `test_vertical_slice_sem.py`, etc.).
9. **Outbound Invocations**: Hands off cleaned data to `statistics-agent` and `validation-agent`.
10. **Responsibility Classification**: Execution & Data Ingestion.
11. **Overlap**: Directly overlaps with `data-curator`.
12. **Target Classification**: **SUBAGENT** (Absorbs `data-curator`).
13. **Migration Risks**: Medium. Deeply wired into `academic_task_router.py` and test suites. Must preserve tool whitelisting and skill bindings.

---

### 4. `data-curator`
1. **File Location**:
   - Runtime Prompt: `.agents/agents/data-curator/agent.md`
   - Contract: `.agents/agents/data-curator/contract.md`
   - Flat Symlink: `.agents/agents/data-curator.md -> data-curator/agent.md`
2. **Current Frontmatter**:
   ```yaml
   name: data-curator
   description: Specialist subagent for raw dataset ingestion, missing data...
   role: Data Hygiene, Missing Value Diagnostics & Screening Specialist
   skills:
     - statistical-data-analyst
     - psychometric-scale-resolver
   ```
3. **Role Intent**: Worker / Specialist.
4. **Current Tools**: Frontmatter MISSING (0 tools). Contract specifies `view_file`, `write_to_file`, `run_command`, `list_dir`, `grep_search`, `find_by_name`.
5. **Current Skills**: `statistical-data-analyst`, `psychometric-scale-resolver`.
6. **MCP Access**: None.
7. **Ability to Invoke Agents**: None.
8. **Inbound Dependencies**:
   - Contracts: `digital-saber/contract.md`.
   - Tests: `tests/test_agent_contracts.py`.
9. **Outbound Invocations**: Hands off to `statistical-expert` and `validation-agent`.
10. **Responsibility Classification**: Execution / Data Hygiene.
11. **Overlap**: Complete subset of `data-agent`.
12. **Target Classification**: **MERGED** (Merge into `data-agent`).
13. **Migration Risks**: Minimal. No scripts in `scripts/` depend on `data-curator`. `test_agent_contracts.py` verifies its existence, so test suite will need updating when merged.

---

### 5. `digital-saber`
1. **File Location**:
   - Runtime Prompt: `.agents/agents/digital-saber/agent.md`
   - Contract: `.agents/agents/digital-saber/contract.md`
   - Flat Symlink: `.agents/agents/digital-saber.md -> digital-saber/agent.md`
2. **Current Frontmatter**:
   ```yaml
   name: digital-saber
   description: Master Research Project Lead, Cognitive Architect, and Digital Twin of Saber Ghaderi...
   role: Master Research Project Lead & Cognitive Orchestrator
   skills:
     - academic-suite-orchestrator
     - digital-twin-academic-consultant
     - thesis-integrity-auditor
     - chapter-4-writing
     - persian-thesis-revision-assistant
   ```
3. **Role Intent**: Main / User-Facing Principal & Cognitive Twin.
4. **Current Tools**:
   - Frontmatter: **MISSING (0 tools)**.
   - Contract: `view_file`, `write_to_file`, `replace_file_content`, `run_command`, `invoke_subagent`, `send_message`, `manage_subagents`, `list_dir`, `grep_search`, `find_by_name`.
5. **Current Skills**:
   - Frontmatter: `academic-suite-orchestrator`, `digital-twin-academic-consultant`, `thesis-integrity-auditor`, `chapter-4-writing`, `persian-thesis-revision-assistant`.
   - Contract: Same 5 skills plus `persian-discussion-builder`.
6. **MCP Access**: None.
7. **Ability to Invoke Agents**: Contract states it invokes 9 specialist roles via `invoke_subagent`, but **frontmatter lacks `invoke_subagent` and `tools` entirely!**
8. **Inbound Dependencies**:
   - Standalone Scripts: `digital_saber.py` (CLI runner), `scripts/attach_telegram_client.py`, `scripts/login_second_account.py`.
   - Tests: `tests/test_agent_contracts.py`.
9. **Outbound Invocations**: Designed to orchestrate `methodology-expert`, `statistical-expert`, `data-curator`, `statistical-auditor`, `results-auditor`, `evidence-auditor`, `academic-writer`, `final-judge`.
10. **Responsibility Classification**: Orchestration, Reasoning & Human Gatekeeping.
11. **Overlap**: Overlaps with `academic-orchestrator` in orchestration intent.
12. **Target Classification**: **DURABLE AGENT** (The Primary User-Facing Principal Agent).
13. **Migration Risks**: High. Must be updated to include `mainAgent: true`, `model: pro`, and native `tools` whitelist (`invoke_subagent`, `manage_subagents`, `ask_question`, etc.) without disrupting external telegram bot bindings.

---

### 6. `evidence-auditor`
1. **File Location**:
   - Runtime Prompt: `.agents/agents/evidence-auditor/agent.md`
   - Contract: `.agents/agents/evidence-auditor/contract.md`
   - Flat Symlink: `.agents/agents/evidence-auditor.md -> evidence-auditor/agent.md`
2. **Current Frontmatter**:
   ```yaml
   name: evidence-auditor
   description: Epistemic integrity and citation verification subagent...
   role: Epistemic Integrity & Citation Verification Auditor
   skills:
     - academic-reference-extractor
     - irandoc-plagiarism-reducer
   ```
3. **Role Intent**: Worker / Critic Gatekeeper.
4. **Current Tools**: Frontmatter MISSING (0 tools). Contract specifies `view_file`, `write_to_file`, `run_command`, `list_dir`, `grep_search`, `find_by_name`.
5. **Current Skills**: `academic-reference-extractor`, `irandoc-plagiarism-reducer`.
6. **MCP Access**: None.
7. **Ability to Invoke Agents**: None.
8. **Inbound Dependencies**:
   - Contracts: `digital-saber/contract.md`, `literature-expert/contract.md`.
   - Architecture: Core member of the Adversarial Critic Protocol (`ADVERSARIAL_CRITIC_PROTOCOL.md`).
9. **Outbound Invocations**: None (issues audit certificates to `digital-saber`).
10. **Responsibility Classification**: Validation (Epistemic & Citational Integrity).
11. **Overlap**: Overlaps with `validation-agent` (which also binds `academic-reference-extractor` and `irandoc-plagiarism-reducer`).
12. **Target Classification**: **DURABLE AGENT** (Durable Epistemic Critic).
13. **Migration Risks**: Must receive explicit frontmatter tools (`run_command`, `view_file`, `write_to_file`) to execute reference extraction scripts.

---

### 7. `final-judge`
1. **File Location**:
   - Runtime Prompt: `.agents/agents/final-judge/agent.md`
   - Contract: `.agents/agents/final-judge/contract.md`
   - Flat Symlink: `.agents/agents/final-judge.md -> final-judge/agent.md`
2. **Current Frontmatter**:
   ```yaml
   name: final-judge
   description: Final dissertation defense committee simulator...
   role: Defense Committee Viva Voce Simulator & Release Gatekeeper
   skills:
     - thesis-integrity-auditor
     - persian-thesis-revision-assistant
     - persian-defense-presentation-builder
   ```
3. **Role Intent**: Gatekeeper / Committee Simulator.
4. **Current Tools**: Frontmatter MISSING (0 tools). Contract specifies `view_file`, `write_to_file`, `run_command`, `list_dir`, `grep_search`, `find_by_name`.
5. **Current Skills**: `thesis-integrity-auditor`, `persian-thesis-revision-assistant`, `persian-defense-presentation-builder`.
6. **MCP Access**: None.
7. **Ability to Invoke Agents**: None.
8. **Inbound Dependencies**:
   - Contracts: `digital-saber/contract.md`.
   - Tests: `tests/test_agent_contracts.py`, `tests/test_vertical_slice_scale_validation.py`.
9. **Outbound Invocations**: None (issues clearance verdict to `digital-saber`).
10. **Responsibility Classification**: Validation & Institutional Clearance.
11. **Overlap**: Partially overlaps with `validation-agent`.
12. **Target Classification**: **DURABLE AGENT** (Viva Voce Committee Simulator & Release Gatekeeper).
13. **Migration Risks**: Low risk if frontmatter tools are added. Essential for viva voce defense simulation.

---

### 8. `intervention-designer`
1. **File Location**:
   - Runtime Prompt: `.agents/agents/intervention-designer/agent.md`
   - Contract: `.agents/agents/intervention-designer/contract.md`
   - Flat Symlink: `.agents/agents/intervention-designer.md -> intervention-designer/agent.md`
2. **Current Frontmatter**:
   ```yaml
   name: intervention-designer
   description: Specialist subagent for designing standardized evidence-based psychological...
   role: Psychological Intervention Protocol Architect
   skills:
     - psychological-intervention-protocol-builder
     - academic-article-writer
   ```
3. **Role Intent**: Worker (Specialist Designer).
4. **Current Tools**: Frontmatter MISSING (0 tools). Contract specifies `view_file`, `write_to_file`, `run_command`, `list_dir`, `grep_search`, `find_by_name`.
5. **Current Skills**: `psychological-intervention-protocol-builder`, `academic-article-writer`.
6. **MCP Access**: None.
7. **Ability to Invoke Agents**: None.
8. **Inbound Dependencies**: Contracts: None; Tests: `tests/test_agent_contracts.py`.
9. **Outbound Invocations**: Hands off protocol tables to `validation-agent`.
10. **Responsibility Classification**: Reasoning & Domain Content Generation.
11. **Overlap**: None; unique clinical domain capability.
12. **Target Classification**: **SUBAGENT** (Clinical Intervention Specialist).
13. **Migration Risks**: Low. Needs frontmatter tools.

---

### 9. `journal-strategist`
1. **File Location**:
   - Runtime Prompt: `.agents/agents/journal-strategist/agent.md`
   - Contract: `.agents/agents/journal-strategist/contract.md`
   - Flat Symlink: `.agents/agents/journal-strategist.md -> journal-strategist/agent.md`
2. **Current Frontmatter**:
   ```yaml
   name: journal-strategist
   description: Specialist subagent for academic journal article packaging...
   role: Publication Packaging & Peer-Review Rebuttal Strategist
   skills:
     - journal-submission-assistant
     - academic-article-writer
     - persian-academic-translation
     - ai-academic-tone-polisher
   ```
3. **Role Intent**: Worker (Packaging Specialist).
4. **Current Tools**: Frontmatter MISSING (0 tools). Contract specifies standard file tools.
5. **Current Skills**: 4 publication packaging skills.
6. **MCP Access**: None.
7. **Ability to Invoke Agents**: None.
8. **Inbound Dependencies**: Tests: `test_agent_contracts.py`.
9. **Outbound Invocations**: Hands off submission package to `results-auditor`.
10. **Responsibility Classification**: Formatting & Rebuttal Strategy.
11. **Overlap**: None; distinct post-thesis journal capability.
12. **Target Classification**: **SUBAGENT** (Publication & Journal Specialist).
13. **Migration Risks**: Low.

---

### 10. `literature-expert`
1. **File Location**:
   - Runtime Prompt: `.agents/agents/literature-expert/agent.md`
   - Contract: `.agents/agents/literature-expert/contract.md`
   - Flat Symlink: `.agents/agents/literature-expert.md -> literature-expert/agent.md`
2. **Current Frontmatter**:
   ```yaml
   name: literature-expert
   description: Specialist subagent for multi-database literature harvesting...
   role: Literature & Epistemic Evidence Synthesizer
   skills:
     - literature-harvester
     - persian-literature-review-builder
     - bibliometric-network-analyst
     - citation-network-visualizer
     - academic-reference-extractor
   ```
3. **Role Intent**: Worker (Harvesting Specialist).
4. **Current Tools**: Frontmatter MISSING (0 tools). Contract specifies `view_file`, `write_to_file`, `run_command`, `list_dir`, `grep_search`, `find_by_name`.
5. **Current Skills**: 5 literature and network analysis skills.
6. **MCP Access**: None.
7. **Ability to Invoke Agents**: None.
8. **Inbound Dependencies**: Contracts: `academic-writer/contract.md`.
9. **Outbound Invocations**: Hands off literature matrix to `evidence-auditor`.
10. **Responsibility Classification**: Reasoning & Harvesting.
11. **Overlap**: Overlaps with `research-agent` (which also binds `literature-harvester` and `persian-literature-review-builder`).
12. **Target Classification**: **SUBAGENT** (Literature Harvesting Specialist).
13. **Migration Risks**: Low.

---

### 11. `longitudinal-modmed-expert`
1. **File Location**:
   - Runtime Prompt: `.agents/agents/longitudinal-modmed-expert/agent.md`
   - Contract: `.agents/agents/longitudinal-modmed-expert/contract.md`
   - Flat Symlink: `.agents/agents/longitudinal-modmed-expert.md -> longitudinal-modmed-expert/agent.md`
2. **Current Frontmatter**:
   ```yaml
   name: longitudinal-modmed-expert
   description: Specialist subagent for 3-wave longitudinal moderated mediation modeling...
   role: Longitudinal Moderated Mediation Specialist
   skills:
     - longitudinal-moderated-mediation
     - statistical-data-analyst
     - chapter-4-writing
   ```
3. **Role Intent**: Worker (Advanced Modeling Specialist).
4. **Current Tools**: Frontmatter MISSING (0 tools). Contract specifies standard execution tools.
5. **Current Skills**: `longitudinal-moderated-mediation`, `statistical-data-analyst`, `chapter-4-writing`.
6. **MCP Access**: None.
7. **Ability to Invoke Agents**: None.
8. **Inbound Dependencies**: Factory: Generated and registered via `factory/specialist_manifest.json` and `factory/meta_factory.py`. Tests: `test_factory.py`, `test_agent_contracts.py`.
9. **Outbound Invocations**: Hands off model parameters to `validation-agent`.
10. **Responsibility Classification**: Statistical Execution & Modeling.
11. **Overlap**: None; specific to 3-wave panel modeling.
12. **Target Classification**: **SUBAGENT** (Longitudinal SEM Specialist).
13. **Migration Risks**: Must maintain factory manifest compatibility (`factory/specialist_manifest.json`).

---

### 12. `meta-analyst`
1. **File Location**:
   - Runtime Prompt: `.agents/agents/meta-analyst/agent.md`
   - Contract: `.agents/agents/meta-analyst/contract.md`
   - Flat Symlink: `.agents/agents/meta-analyst.md -> meta-analyst/agent.md`
2. **Current Frontmatter**:
   ```yaml
   name: meta-analyst
   description: Specialist subagent for PRISMA 2020 systematic literature reviews...
   role: Systematic Review & Quantitative Meta-Analyst
   skills:
     - systematic-review-meta-analyst
     - academic-article-writer
   ```
3. **Role Intent**: Worker (Meta-Analysis Specialist).
4. **Current Tools**: Frontmatter MISSING (0 tools). Contract specifies standard file and CLI tools.
5. **Current Skills**: `systematic-review-meta-analyst`, `academic-article-writer`.
6. **MCP Access**: None.
7. **Ability to Invoke Agents**: None.
8. **Inbound Dependencies**: Contracts: `research-agent/contract.md`, `statistics-agent/contract.md`.
9. **Outbound Invocations**: Hands off forest/funnel plots to `validation-agent`.
10. **Responsibility Classification**: Statistical Execution & Review Synthesis.
11. **Overlap**: Overlaps with `systematic-review-meta-analyst` skill bound by `research-agent`.
12. **Target Classification**: **SUBAGENT** (Systematic Review & Meta-Analyst).
13. **Migration Risks**: Low.

---

### 13. `methodology-expert`
1. **File Location**:
   - Runtime Prompt: `.agents/agents/methodology-expert/agent.md`
   - Contract: `.agents/agents/methodology-expert/contract.md`
   - Flat Symlink: `.agents/agents/methodology-expert.md -> methodology-expert/agent.md`
2. **Current Frontmatter**:
   ```yaml
   name: methodology-expert
   description: Specialist subagent for research methodology, experimental design...
   role: Research Methodology & Experimental Design Specialist
   skills:
     - gpower-sample-size-calculator
     - persian-proposal-builder
     - methodology-review
     - psychometric-data-simulator
   ```
3. **Role Intent**: Main / Authority in Research Design.
4. **Current Tools**: Frontmatter MISSING (0 tools). Contract specifies standard tools.
5. **Current Skills**: 4 methodology and sampling skills.
6. **MCP Access**: None.
7. **Ability to Invoke Agents**: None currently in frontmatter.
8. **Inbound Dependencies**: Contracts: `digital-saber/contract.md`. Tests: `test_agent_contracts.py`.
9. **Outbound Invocations**: Hands off design to `validation-agent`.
10. **Responsibility Classification**: Reasoning, Power Analysis & Design.
11. **Overlap**: Overlaps with `research-agent` (which also executes methodology review and G*Power).
12. **Target Classification**: **DURABLE AGENT** (Methodology & Experimental Authority).
13. **Migration Risks**: High potential if promoted to Durable Agent without defining its relationship to `research-agent`.

---

### 14. `psychometric-expert`
1. **File Location**:
   - Runtime Prompt: `.agents/agents/psychometric-expert/agent.md`
   - Contract: `.agents/agents/psychometric-expert/contract.md`
   - Flat Symlink: `.agents/agents/psychometric-expert.md -> psychometric-expert/agent.md`
2. **Current Frontmatter**:
   ```yaml
   name: psychometric-expert
   description: Specialist subagent for psychometric instrument resolution...
   role: Psychometrician & Construct Validation Specialist
   skills:
     - psychometric-scale-resolver
     - psychometric-scale-validator
     - cfa
     - reliability-analysis
   ```
3. **Role Intent**: Worker (Psychometrics Specialist).
4. **Current Tools**: Frontmatter MISSING (0 tools).
5. **Current Skills**: 4 scale validation and CTT/IRT skills.
6. **MCP Access**: None.
7. **Ability to Invoke Agents**: None.
8. **Inbound Dependencies**: Tests: `test_agent_contracts.py`.
9. **Outbound Invocations**: Hands off CVR/CVI/CFA matrices to `validation-agent`.
10. **Responsibility Classification**: Psychometric Execution & Measurement Modeling.
11. **Overlap**: Overlaps with `cfa` and `psychometric-scale-validator` skills bound by `statistics-agent`.
12. **Target Classification**: **SUBAGENT** (Scale Standardization & Psychometrics Specialist).
13. **Migration Risks**: Low.

---

### 15. `qualitative-analyst`
1. **File Location**:
   - Runtime Prompt: `.agents/agents/qualitative-analyst/agent.md`
   - Contract: `.agents/agents/qualitative-analyst/contract.md`
   - Flat Symlink: `.agents/agents/qualitative-analyst.md -> qualitative-analyst/agent.md`
2. **Current Frontmatter**:
   ```yaml
   name: qualitative-analyst
   description: Specialist subagent for qualitative data analysis...
   role: Qualitative Research & Thematic Analysis Specialist
   skills:
     - qualitative-data-analyst
   ```
3. **Role Intent**: Worker (Qualitative Specialist).
4. **Current Tools**: Frontmatter MISSING (0 tools).
5. **Current Skills**: `qualitative-data-analyst`.
6. **MCP Access**: None.
7. **Ability to Invoke Agents**: None.
8. **Inbound Dependencies**: Tests: `test_agent_contracts.py`.
9. **Outbound Invocations**: Hands off coding matrices to `validation-agent`.
10. **Responsibility Classification**: Qualitative Coding & Reasoning.
11. **Overlap**: Overlaps with `qualitative-data-analyst` skill bound by `research-agent`.
12. **Target Classification**: **SUBAGENT** (Qualitative Research Specialist).
13. **Migration Risks**: Low.

---

### 16. `research-agent`
1. **File Location**:
   - Runtime Prompt: `.agents/agents/research-agent/agent.md`
   - Contract: `.agents/agents/research-agent/contract.md`
   - Flat Symlink: `.agents/agents/research-agent.md -> research-agent/agent.md`
2. **Current Frontmatter**:
   ```yaml
   name: research-agent
   description: Specialized domain subagent for scientific literature harvesting...
   role: Research Methodology & Epistemic Literature Specialist
   mainAgent: false
   subagent: true
   model: pro
   command_execution_policy: deterministic_hands_only
   tools:
     - view_file
     - list_dir
     - grep_search
     - find_by_name
     - read_url_content
     - search_web
     - run_command
     - write_to_file
   skills:
     - literature-harvester
     - persian-literature-review-builder
     - bibliometric-network-analyst
     - citation-network-visualizer
     - gpower-sample-size-calculator
     - persian-proposal-builder
     - systematic-review-meta-analyst
     - qualitative-data-analyst
   ```
3. **Role Intent**: Worker (Broad Umbrella Subagent).
4. **Current Tools**: 8 declared tools (including `read_url_content` and `search_web`).
5. **Current Skills**: 8 skills (broadest binding in workspace).
6. **MCP Access**: None.
7. **Ability to Invoke Agents**: None.
8. **Inbound Dependencies**:
   - Scripts: `scripts/academic_task_router.py`, `scripts/orchestrator_dependency_resolver.py`.
   - Tests: `test_task_router.py`, `test_orchestrator.py`.
9. **Outbound Invocations**: Hands off requirements and analysis plans to `statistics-agent` and `writing-agent`.
10. **Responsibility Classification**: Mixed (Reasoning, Harvesting, Design).
11. **Overlap**: Heavily overlaps with `methodology-expert`, `literature-expert`, `meta-analyst`, and `qualitative-analyst`.
12. **Target Classification**: **SUBAGENT** (Focused Research Worker) or Decomposed across specialists.
13. **Migration Risks**: High. Central to `scripts/academic_task_router.py`. If removed or refactored carelessly, router pipelines break.

---

### 17. `results-auditor`
1. **File Location**:
   - Runtime Prompt: `.agents/agents/results-auditor/agent.md`
   - Contract: `.agents/agents/results-auditor/contract.md`
   - Flat Symlink: `.agents/agents/results-auditor.md -> results-auditor/agent.md`
2. **Current Frontmatter**:
   ```yaml
   name: results-auditor
   description: Quality control subagent enforcing APA 7th Edition numerical precision...
   role: Numerical & APA 7 Quality Control Auditor
   skills:
     - thesis-integrity-auditor
     - statistical-data-analyst
     - chapter-4-writing
   ```
3. **Role Intent**: Worker / Adversarial Critic.
4. **Current Tools**: Frontmatter MISSING (0 tools).
5. **Current Skills**: `thesis-integrity-auditor`, `statistical-data-analyst`, `chapter-4-writing`.
6. **MCP Access**: None.
7. **Ability to Invoke Agents**: None.
8. **Inbound Dependencies**: Contracts: `academic-writer/contract.md`, `digital-saber/contract.md`, `journal-strategist/contract.md`. Tests: `test_agent_contracts.py`.
9. **Outbound Invocations**: Hands off audit clearance to `digital-saber`.
10. **Responsibility Classification**: Validation (APA 7, Precision, Tables).
11. **Overlap**: Overlaps with `validation-agent`.
12. **Target Classification**: **SUBAGENT** (Specialized Formatting/Precision Critic).
13. **Migration Risks**: Low. Needs frontmatter tools.

---

### 18. `statistical-auditor`
1. **File Location**:
   - Runtime Prompt: `.agents/agents/statistical-auditor/agent.md`
   - Contract: `.agents/agents/statistical-auditor/contract.md`
   - Flat Symlink: `.agents/agents/statistical-auditor.md -> statistical-auditor/agent.md`
2. **Current Frontmatter**:
   ```yaml
   name: statistical-auditor
   description: Adversarial quality auditor subagent for statistical assumptions...
   role: Adversarial Statistical Quality Auditor
   skills:
     - thesis-integrity-auditor
     - statistical-data-analyst
     - chapter-4-writing
   ```
3. **Role Intent**: Worker / Adversarial Critic.
4. **Current Tools**: Frontmatter MISSING (0 tools).
5. **Current Skills**: `thesis-integrity-auditor`, `statistical-data-analyst`, `chapter-4-writing`.
6. **MCP Access**: None.
7. **Ability to Invoke Agents**: None.
8. **Inbound Dependencies**: Contracts: `digital-saber/contract.md`, `statistical-expert/contract.md`. Tests: `test_msai_detector.py`, `test_agent_contracts.py`.
9. **Outbound Invocations**: Hands off statistical clearance to `digital-saber`.
10. **Responsibility Classification**: Validation (Statistical Assumptions, df, MSAI).
11. **Overlap**: Overlaps with `validation-agent`.
12. **Target Classification**: **SUBAGENT** (Adversarial Statistical Auditor).
13. **Migration Risks**: Low. Needs frontmatter tools.

---

### 19. `statistical-expert`
1. **File Location**:
   - Runtime Prompt: `.agents/agents/statistical-expert/agent.md`
   - Contract: `.agents/agents/statistical-expert/contract.md`
   - Flat Symlink: `.agents/agents/statistical-expert.md -> statistical-expert/agent.md`
2. **Current Frontmatter**:
   ```yaml
   name: statistical-expert
   description: Specialist subagent for statistical analysis planning...
   role: Statistical Analysis & Hypothesis Testing Architect
   skills:
     - statistical-data-analyst
     - psychometric-scale-resolver
     - psychometric-scale-validator
     - chapter-4-writing
   ```
3. **Role Intent**: Main / Authority in Statistics.
4. **Current Tools**: Frontmatter MISSING (0 tools). Contract specifies standard execution tools.
5. **Current Skills**: 4 statistical modeling and scale skills.
6. **MCP Access**: None.
7. **Ability to Invoke Agents**: None currently in frontmatter.
8. **Inbound Dependencies**: Contracts: `digital-saber/contract.md`. Tests: `test_agent_contracts.py`.
9. **Outbound Invocations**: Hands off analysis to `statistical-auditor`.
10. **Responsibility Classification**: Reasoning & Statistical Architecture.
11. **Overlap**: **100% duplicate of `statistics-agent`**.
12. **Target Classification**: **DURABLE AGENT** (Statistical Modeling Authority, absorbing `statistics-agent`).
13. **Migration Risks**: High. Absorbing `statistics-agent` requires re-routing `scripts/academic_task_router.py`.

---

### 20. `statistics-agent`
1. **File Location**:
   - Runtime Prompt: `.agents/agents/statistics-agent/agent.md`
   - Contract: `.agents/agents/statistics-agent/contract.md`
   - Flat Symlink: `.agents/agents/statistics-agent.md -> statistics-agent/agent.md`
2. **Current Frontmatter**:
   ```yaml
   name: statistics-agent
   description: Specialized domain subagent for inferential statistical analysis planning...
   role: Statistical Modeling & Inferential Analysis Architect
   mainAgent: false
   subagent: true
   model: pro
   command_execution_policy: deterministic_hands_only
   tools:
     - view_file
     - list_dir
     - grep_search
     - find_by_name
     - run_command
     - write_to_file
   skills:
     - statistical-data-analyst
     - psychometric-scale-validator
     - psychometric-data-simulator
     - systematic-review-meta-analyst
   ```
3. **Role Intent**: Worker (Execution Runner).
4. **Current Tools**: 6 declared tools (including `run_command` and `write_to_file`).
5. **Current Skills**: 4 modeling and simulation skills.
6. **MCP Access**: None.
7. **Ability to Invoke Agents**: None.
8. **Inbound Dependencies**:
   - Scripts: `scripts/academic_task_router.py`, `scripts/orchestrator_dependency_resolver.py`, `scripts/academic_state_manager.py`.
   - Tests: 5 vertical slice tests.
9. **Outbound Invocations**: Hands off to `writing-agent` and `validation-agent`.
10. **Responsibility Classification**: Execution & Statistical Modeling.
11. **Overlap**: Complete duplicate of `statistical-expert`.
12. **Target Classification**: **MERGED** (Merge into `statistical-expert` or keep as bounded execution subagent).
13. **Migration Risks**: High. Heavily wired into test suite and state management.

---

### 21. `validation-agent`
1. **File Location**:
   - Runtime Prompt: `.agents/agents/validation-agent/agent.md`
   - Contract: `.agents/agents/validation-agent/contract.md`
   - Flat Symlink: `.agents/agents/validation-agent.md -> validation-agent/agent.md`
2. **Current Frontmatter**:
   ```yaml
   name: validation-agent
   description: Independent adversarial quality auditor, Viva Voce defense simulator...
   role: Independent Adversarial Quality Auditor & Defense Gatekeeper
   mainAgent: false
   subagent: true
   model: pro
   command_execution_policy: deterministic_hands_only
   tools:
     - view_file
     - list_dir
     - grep_search
     - find_by_name
     - run_command
     - write_to_file
   skills:
     - thesis-integrity-auditor
     - academic-reference-extractor
     - irandoc-plagiarism-reducer
     - persian-thesis-revision-assistant
   ```
3. **Role Intent**: Worker / Adversarial Critic.
4. **Current Tools**: 6 declared tools.
5. **Current Skills**: 4 auditing and integrity skills.
6. **MCP Access**: None.
7. **Ability to Invoke Agents**: None.
8. **Inbound Dependencies**:
   - Contracts: Referenced by 13 different contracts as the required validation gate!
   - Scripts: `scripts/academic_task_router.py`, `scripts/orchestrator_dependency_resolver.py`.
   - Tests: 4 vertical slice test files.
9. **Outbound Invocations**: Hands off certified reports to `academic-orchestrator`.
10. **Responsibility Classification**: Validation (All-in-one Quality Gate).
11. **Overlap**: Bundles the duties of `statistical-auditor`, `results-auditor`, `evidence-auditor`, and `final-judge`.
12. **Target Classification**: **SUBAGENT** (Operational Validation Worker under `final-judge` / `evidence-auditor`).
13. **Migration Risks**: High. 13 contracts explicitly name `validation-agent` as their completion gate.

---

### 22. `writing-agent`
1. **File Location**:
   - Runtime Prompt: `.agents/agents/writing-agent/agent.md`
   - Contract: `.agents/agents/writing-agent/contract.md`
   - Flat Symlink: `.agents/agents/writing-agent.md -> writing-agent/agent.md`
2. **Current Frontmatter**:
   ```yaml
   name: writing-agent
   description: Master academic chapter drafter and Persian rhetoric specialist...
   role: Persian Academic Chapter Drafter & Rhetoric Specialist
   mainAgent: false
   subagent: true
   model: pro
   command_execution_policy: deterministic_hands_only
   tools:
     - view_file
     - list_dir
     - grep_search
     - find_by_name
     - run_command
     - write_to_file
     - replace_file_content
   skills:
     - persian-thesis-builder
     - persian-discussion-builder
     - academic-article-writer
     - ai-academic-tone-polisher
     - psychological-intervention-protocol-builder
     - journal-submission-assistant
     - persian-defense-presentation-builder
   ```
3. **Role Intent**: Worker (Drafter).
4. **Current Tools**: 7 declared tools (including `replace_file_content`).
5. **Current Skills**: 7 writing and presentation skills.
6. **MCP Access**: None.
7. **Ability to Invoke Agents**: None.
8. **Inbound Dependencies**:
   - Scripts: `scripts/academic_task_router.py`, `scripts/orchestrator_dependency_resolver.py`.
   - Contracts: `research-agent/contract.md`, `statistics-agent/contract.md`.
   - Tests: 5 vertical slice tests.
9. **Outbound Invocations**: Hands off chapters to `validation-agent`.
10. **Responsibility Classification**: Writing & Formatting.
11. **Overlap**: **100% duplicate of `academic-writer`**.
12. **Target Classification**: **MERGED** (Merge into `academic-writer`).
13. **Migration Risks**: High. Heavily wired into `academic_task_router.py` and test suites.

---

### 23. `academic-challenger` (Planned New Role)
1. **File Location**: Not yet created on disk.
2. **Current Frontmatter**: N/A.
3. **Role Intent**: Worker / Adversarial Stress-Tester.
4. **Current Tools**: Expected tools: `view_file`, `list_dir`, `grep_search`, `find_by_name`, `run_command`.
5. **Current Skills**: `thesis-integrity-auditor`, `methodology-review`, `assumption-testing`.
6. **MCP Access**: None.
7. **Ability to Invoke Agents**: None.
8. **Inbound Dependencies**: None (0 references in code).
9. **Outbound Invocations**: Cross-examines candidate drafts and submits defense interrogation cards to `final-judge`.
10. **Responsibility Classification**: Validation / Adversarial Defense Simulation.
11. **Overlap**: Complements `final-judge` by acting as the aggressive internal examiner during viva voce simulation.
12. **Target Classification**: **BOUNDED SUBAGENT** (Adversarial Critic / Committee Interrogator).
13. **Migration Risks**: Low (greenfield addition).
