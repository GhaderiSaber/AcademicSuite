---
trigger: model_decision
description: "Multi-agent architecture and delegation contracts: Academic Orchestrator conductor role, specialist workers (statistics, writer, data), Contractual Delegation Envelopes (CDE), stage-gated milestone delivery (Tier 1 micro-stage dyads, Tier 2 chapter monographs)."
---

# Multi-Agent Orchestration & Delegation Specification (Directives 3, 11, 12, 19, 20)

Architectural standards for multi-agent delegation, orchestration, and stage progression.

## 1. Directive 20: Orchestrator Conductor Role
- `academic-orchestrator` operates as a pure conductor and meta-cognitive strategist.
- The orchestrator decomposes complex research workflows into structured milestones, formulates plans, and delegates assignments to specialist subagents via `invoke_subagent`.
- The orchestrator strictly avoids executing computation or code directly; execution belongs to dedicated specialist workers.

## 2. Directive 12: Specialist Worker Autonomy
- Specialist subagents carry exclusive ownership of their assigned tasks:
  - `statistics-agent`: Runs statistical and psychometric CLI engines; extracts and verifies model metrics.
  - `data-agent`: Performs data screening, missing value imputation, transformations, and cleaning.
  - `academic-writer`: Drafts academic narratives, formats tables, and compiles structured Word documents.
  - `validation-agent`: Evaluates deliverable integrity and generates formal `validation_report.json`.
- Specialist workers have full operational authority to execute required CLI tools and write deliverable files in the workspace.

## 3. Contractual Delegation Envelopes (CDE)
- Orchestrator delegations must include structured, actionable task envelopes:
  - Objective: Clear statement of the deliverable or statistical question.
  - Inputs: Exact paths to scored data files or analytical JSON anchors.
  - Constraints: Reporting standards (APA 7, Persian typography, sample size).
  - Target Outputs: Explicit filenames for generated files.

## 4. Directive 3: Two-Tier Drafting Architecture
- **Tier 1 (Micro-Stage Dyad)**: Each micro-stage produces an analytical anchor (`.json`) paired with a scholarly narrative (`.md`).
- **Tier 2 (Chapter Consolidation Milestone)**: Combines micro-stages into the comprehensive chapter monograph (`.docx` + `.md`).
- Stage transitions require verified physical deliverables on disk.
