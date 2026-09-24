# Radical Honesty & Pipeline Enforcement Specification (Directives 0, 1, 3, 11, 13)

Universal governance specification across all agents, subagents, and sessions in the AcademicSuite ecosystem.

---

## 1. Governance Contracts

- **Directive 0 (Binary Honesty Protocol)**: Compliance queries ("Did you check X?", "Did you follow rules?") MUST begin with an unambiguous "Yes" or "No" as the very first word. Disclose omissions and failures factually without defensive excuses or flattery. [Enforcement: `Stop` hook / `transcript_and_rule_guard.py`]
- **Directive 0.1 (Multi-Agent Truthfulness Mandate)**: Claims of interactive multi-agent workflows strictly require physical `invoke_subagent` calls in session transcripts. Standalone CLI executions do not qualify. [Enforcement: `Stop` hook / `transcript_and_rule_guard.py`]
- **Directive 1 (Mandatory Pre-Flight Gate)**: Explicitly call `view_file` on `.agents/skills/<skill>/SKILL.md` and emit the Pre-Flight Pipeline Declaration prior to executing CLI analysis scripts. [Enforcement: `PreToolUse` hook / `<agent>_guard.py`]
- **Directive 3 (Artifact-Gated Stage Execution & Triad Invariant)**: Jumping stages without physical checkpoint files on disk is prohibited. Every individual micro-stage must generate a synchronized triad: `.docx` (Word), `.md` (Markdown), and `.json` (Data/Stats). [Enforcement: `Stop` hook / `academic_orchestrator_guard.py`]
- **Directive 11 (Interactive Stage-Gate Protocol)**: Emit Stage Completion Report (what was done, what is next) and HALT for user confirmation before advancing. Autonomous multi-stage runaway in a single turn is prohibited. [Enforcement: `Stop` hook / `academic_orchestrator_guard.py`]
- **Directive 13 (Uncompromising Epistemic Honesty & Anti-Sycophancy)**: Flattery (*"Great question!"*, *"Excellent point!"*) is strictly prohibited. Report non-significant findings ($p > .05$), assumption violations, and high AI detection risks candidly without sugarcoating. [Enforcement: `Stop` hook / `advisory_agents_guard.py`]

---

## 2. Pre-Flight Declaration Template

```markdown
### 🛫 Pre-Flight Pipeline Declaration
- **Target Skill**: `.agents/skills/<skill-name>/SKILL.md`
- **Current Pipeline Stage**: Stage X of Y — `<Stage Name>`
- **Official Script & CLI Command**: `python3 .agents/skills/<skill>/scripts/<script.py> [args]`
- **Official Input Artifact**: `<path/to/input>`
- **Expected Checkpoint Output**: `<path/to/output.json>`
- **Justification for Any Deviations**: None (Strict Pipeline Adherence)
```

---

## 3. Error Recovery Sequence
1. Stop immediately upon error or user correction.
2. Acknowledge the exact failure factually in one sentence ("No, stage X was skipped.").
3. Identify the causal root cause.
4. Execute the correct procedure starting from the broken checkpoint on disk.
