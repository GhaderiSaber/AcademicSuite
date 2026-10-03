# Behavioral Root Cause Analysis: Agent Role Bleed & Document Compilation Boundary Violation

- **Analysis ID**: `BAN-20261003-AGENT-ROLE-BLEED-001`
- **Trajectory ID**: `TRJ-20261003-AGENT-ROLE-BLEED-001`
- **Target Agent**: `academic-orchestrator`
- **Failure Signature**: `AGENT_ROLE_BOUNDARY_VIOLATION`
- **Trigger**: `USER_FEEDBACK` (`FDB-20261003-AGENT-ROLE-BLEED-001`)

## 1. Description of the Failure
During Chapter 4 execution, `academic-orchestrator` collapsed the two-phase pipeline (`STATISTICS ──► WRITING`) into a single monolithic task. It delegated the creation of both analytical data (`.json`) and final narrative documents (`.docx`, `.md`) to the `statistics-agent`. The `statistics-agent`, violating Directive 12 and Directive 19, accepted the task and authored OpenXML documents. A subsequent mechanical validation falsely passed because it lacked author provenance checks.

## 2. Root Cause Diagnosis
The root cause involves failures across three architectural layers:
1. **Orchestrator Capability Router**: A coarse string pattern match on stage title keywords ('parametric assumptions') incorrectly mapped the entire drafting micro-stage to `STATISTICS`, collapsing the pipeline.
2. **Worker Guard Blindspot**: `statistics-agent` lacked fail-closed assertions on incoming Contractual Delegation Envelopes (CDEs) to reject tasks demanding narrative drafting or `.docx`/`.md` compilation.
3. **Validator Author-Provenance Blindspot**: `validation-agent` evaluated only file sizes and stats, but lacked assertions verifying which agent authored the files, resulting in a false-negative mechanical pass.

## 3. Prescribed Behavior (Counterfactual)
1. **Orchestrator Two-Tier Decomposition Guard**: `academic-orchestrator` must always decompose `.docx`/`.md` tasks into Phase A (Calculation -> `statistics-agent`) and Phase B (Synthesis -> `academic-writer`).
2. **Worker Fail-Closed Input Boundary**: `statistics-agent` must assert on its incoming CDE to strictly reject tasks with `.docx`, `.doc`, or `.md` outputs.
3. **Validator Provenance Assertion**: Validation checks must include verification of agent authorship, guaranteeing that `academic-writer` authored narrative deliverables.
