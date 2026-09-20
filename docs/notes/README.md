# Google Antigravity Agent & Subagent Architecture Guide
**The Definitive Reference for Agent Design, Subagent Delegation, and Cutting-Edge Multi-Agent Patterns**  
*Document Version: 2026.09.17 | Operative Date: September 17, 2026*

---

## 📖 Overview

This documentation suite provides a comprehensive, deep-dive reference for creating, configuring, delegating, and orchestrating **Primary Agents** and **Subagents** within the **Google Antigravity (AGY)** ecosystem. 

Antigravity is an agent-first software development and research platform engineered around an autonomous **Plan → Execute → Verify** cognitive loop. By combining declarative configuration, runtime dynamic delegation, fine-grained workspace isolation, and deterministic lifecycle hooks, Antigravity enables resilient multi-agent systems that avoid context window saturation ("context bankruptcy") and execute complex workloads with surgical precision.

---

## 🗺️ Documentation Sitemap

| Document | Description | Key Topics |
| :--- | :--- | :--- |
| **[01. Overview & Agent Architecture](01_overview_and_agent_architecture.md)** | Core agent architecture and foundations | Cognitive loop, Agent-Conversation-Connection pillars, execution modes (Autonomous vs. Interactive), token budget ceilings, security sandboxing. |
| **[02. Subagent Paradigms & Creation](02_subagent_paradigms_and_creation.md)** | The 3 paradigms for defining subagents | Declarative workspace subagents (`.agents/agents/*.md`), runtime dynamic subagents (`define_subagent`), programmatic SDK subagents (`SubagentConfig`), Execution Symmetry. |
| **[03. Workspace Isolation & Execution Modes](03_workspace_isolation_and_execution_modes.md)** | Filesystem sandboxing & model selection | Workspace modes (`inherit`, `branch` Git worktree, `share`), model tier allocation (`flash_lite`, `flash`, `pro`), asynchronous event loops & reactive wakeups. |
| **[04. Cutting-Edge Multi-Agent Patterns (2026)](04_cutting_edge_multi_agent_patterns_2026.md)** | Advanced architectural patterns | Orchestrator-Worker, Parallel Fan-Out/Fan-In, Generator-Critic / Viva Voce Committee, Dynamic Swarms, "Hands vs. Brains" invariant, Artifact-Gated pipelines. |
| **[05. Lifecycle Hooks & Governance](05_lifecycle_hooks_and_governance.md)** | Deterministic policy enforcement | `hooks.json` engine, `PreToolUse`, `PostToolUse`, `PreInvocation`, `Stop` gates, argument rewriting, least-privilege scoping. |
| **[06. Practical Blueprints & Templates](06_practical_blueprints_and_templates.md)** | Ready-to-use production configurations | Declarative YAML agent templates, Python SDK multi-tier scripts, dynamic tool invocation schemas, automated CI hook configurations. |
| **[07. AcademicSuite Repo Structure Guide](07_academic_suite_repo_structure_guide.md)** | AcademicSuite specific implementation standards | 5 Cognitive Layers, dual-entry agents (`.agents/agents/<name>/agent.md`), deterministic skills in `.agents/skills/`, Triad Invariant, and Hands vs Brains separation. |

---

## 🚀 Quick Reference: Custom Agent Frontmatter Spec

```yaml
---
name: code-auditor
description: Audits code changes for security vulnerabilities, OWASP Top 10, and code quality regressions.
role: Security & Code Quality Auditor
model: flash
subagent: true
mainAgent: false
tools:
  - view_file
  - grep_search
  - find_by_name
skills:
  - security-scanner
---

# Instructions
You are a specialized code quality and security auditor...
```

---

## ⚖️ Customization Taxonomy

| Component | Scope | Entrypoint | Key Role |
| :--- | :--- | :--- | :--- |
| **Primary Agent** | Session | CLI / IDE / SDK | Orchestrates the top-level mission, delegates to subagents, and interacts with the user. |
| **Subagent** | Isolated Subtask | `.agents/agents/*.md` or `invoke_subagent` | Executes focused subtasks in an isolated context window with dedicated tools and workspace. |
| **Skill** | Procedural Knowledge | `.agents/skills/<name>/SKILL.md` | Modular runbook with progressive disclosure and deterministic helper scripts ("The Hands"). |
| **Rule** | Behavioral Directives | `AGENTS.md` / `GEMINI.md` | Universal constraints, coding standards, and invariant policies loaded contextually. |
| **Hook** | Lifecycle Events | `.agents/hooks.json` | External deterministic shell scripts that intercept tools and govern turn completion. |
| **Plugin** | Bundled Distribution | `.agents/plugins/<name>/` | Distributable package bundling skills, rules, hooks, and MCP server configurations. |
