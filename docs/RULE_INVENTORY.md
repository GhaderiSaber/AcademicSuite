# Rule Inventory & Constitutional Governance Audit

**Document Version:** 1.0.0 (Phase 1 Audit)  
**Governance Hierarchy:** Global Constitutional Directives -> Domain Rules -> Plugin Rules -> Machine Enforcement Hooks  

---

## 1. Executive Summary

Rules in the Academic Suite are non-negotiable architectural invariants designed to prevent LLM hallucinations, enforce authentic academic rigor, protect client deliverables, and guarantee reproducible research.

Governance operates on three levels:
1. **Constitutional Directives (`AGENTS.md`)**: 19 global principles binding on all agents.
2. **Modular Domain Rule Specifications (`.agents/rules/`)**: Detailed technical guidelines for typography, file naming, Git automation, honesty, and statistical reporting.
3. **Machine Enforcement Hooks (`.agents/hooks.json`)**: Real-time lifecycle intercepts (`PreToolUse`, `PostToolUse`, `PreInvocation`, `Stop`) backed by `transcript_and_rule_guard.py`.

---

## 2. Global Constitutional Directives (`AGENTS.md`)

| Directive | Name | Core Mandate |
|---|---|---|
| **Directive 0** | **Radical Honesty, Anti-Deception & Binary Honesty Protocol** | Zero defensive excuses. Whenever asked a compliance question ("Did you check X?", "Did you follow the rules?"), the response **MUST BEGIN WITH "Yes" OR "No"** as the very first word. Never claim a multi-agent workflow unless physical calls to `invoke_subagent` exist in transcripts. |
| **Directive 1** | **Mandatory Pre-Flight Gate & Progressive Disclosure** | Before executing capabilities or analyses, agents must view the skill specification (`view_file` on `SKILL.md`) and emit a formal Pre-Flight Pipeline Declaration. |
| **Directive 2** | **Deterministic Calculation (Zero Mental Hallucinations)** | Never calculate statistical numbers, $p$-values, or test statistics in LLM memory. Run deterministic scripts via `run_command` on physical datasets. |
| **Directive 3** | **Micro-Stage Granularity, Triad Artifact Invariant & One-Hypothesis-One-Stage** | Monolithic drafting is strictly prohibited. Every micro-stage and individual hypothesis must produce a synchronized triad of artifacts on disk: `.docx` (Word), `.md` (Markdown), and `.json` (Data/Stats). Every individual hypothesis has its own dedicated stage. |
| **Directive 4** | **Strict APA 7th Edition Typography & Persian Leading Zero Standard** | Statistical symbols italicized (*M, SD, t, F, p*); 2 decimals for test statistics, exactly 3 decimals for $p$-values. In Persian deliverables, **preserve the leading zero** (`۰.۰۰۱`, `۰.۰۵`), using dots not slashes. Prohibition of $p = .000$. Exactly 3 horizontal table borders. |
| **Directive 4.1** | **Presentation Visual Standards & Academic Sobriety** | Zero emojis in academic deliverables. Zero English words on Persian slides. Native RTL SmartArt (`Reverse = 1`), decoupled LTR numbers. |
| **Directive 5** | **Persian Academic Typography & OpenXML Standards** | RTL paragraph properties (`<w:bidi w:val="1"/>`), justified text (`<w:jc w:val="both"/>`), genuine Persian font bindings (`B Nazanin` 13–14 pt body, `B Titr` 12–18 pt headings, `Times New Roman` for stats). Zero manual line breaks (`<w:br/>`). Preservation of native Word OMML math (`<m:oMath>`). |
| **Directive 6** | **English Primary Interaction & Mandatory English-Only File Naming** | Default interaction language with the user is **English**. All files, directories, datasets, and scripts on disk **MUST BE NAMED STRICTLY IN ASCII ENGLISH** (`a-z`, `0-9`, `_`, `-`, `.`). Zero Persian/non-ASCII filenames on disk. |
| **Directive 7** | **Digital Twin Persona & Pricing Rules** | Authentic academic Persian without AI clichés (*«شایان ذکر است که»*). Deterministic pricing via `proposal_price_estimator.py` in Tomans. High-stakes proposals submitted to Saber's Admin Desk (`124911145`). |
| **Directive 8** | **Mandatory Git Lifecycle (Clean Working Tree)** | Automatically stage changed files, generate conventional semantic commit messages (`feat:`, `fix:`, `docs:`, `refactor:`), and keep the working tree clean. |
| **Directive 9** | **Realistic Decimal Noise in Psychometric Simulation** | Zero synthetic whole-integer means. In simulated datasets, inject bounded empirical decimal noise ($\delta \sim \text{Uniform}(\pm 0.08, \pm 0.25)$). Discrete integer Likert items. |
| **Directive 10** | **Multi-Signal Anomaly Scoring (MSAI)** | Never accuse data fabrication on a single indicator. Evaluate Multi-Signal Anomaly Index (MSAI) combining effect size, variance deflation, group overlap, and alpha. Issue `FLAG FOR REVIEW` with diagnostic guidance. |
| **Directive 11** | **Dual-Track Autonomy & Interactive Stage-Gate Protocol** | At the completion of each micro-stage, emit the Stage Completion Report (What Was Done + What Will Be Done Next), then **HALT and wait for user confirmation**. Autonomous runaway across stages is strictly forbidden. |
| **Directive 12** | **Hybrid Multi-Agent Deliberation Architecture (Hands vs. Brains)** | 15 persistent cognitive roles (`.agents/agents/`) invoked via Antigravity `invoke_subagent`. Deterministic scripts (`.agents/skills/`) executed by agents for statistical calculation and OpenXML generation. |
| **Directive 12.1** | **Sole Orchestrator Mandate & Prohibition of Python Agent Emulation** | Antigravity is the sole agent orchestrator. Agents must never write or execute Python agent emulators or autonomous dispatch loops. Python scripts are strictly deterministic tools ("The Hands"). |
| **Directive 13** | **Uncompromising Epistemic Honesty & Anti-Sycophancy** | Zero flattery. Report non-significant findings ($p > .05$), assumption violations, and high AI detection risks candidly. |
| **Directive 14** | **Anti-Hallucination & Zero Ghost Citations** | Never invent citations. Verify all external bibliographic claims against CrossRef/PubMed/SID and download references to `04_references_and_lit/papers/`. |
| **Directive 15** | **Temporal Reality Anchor: 2026 (1405 SH)** | Operative calendar year is 2026 (1405 SH). Recent empirical literature window is 2021–2026. |
| **Directive 16** | **EndNote CWYW Compatibility** | English journal manuscripts require `.enw`/`.ris` libraries and native OpenXML `ADDIN EN.CITE` field codes. |
| **Directive 17** | **Antigravity Lifecycle Hook Machine Gate (`.agents/hooks.json`)** | System integrity mechanically enforced by hook guards. |
| **Directive 18** | **Skill Modularity & Context Budget Standard (Single-View Invariant)** | Every `SKILL.md` must fit within a single view without truncation: maximum **500 lines** and maximum **40,000 bytes**. |

---

## 3. Modular Domain Rules Directory (`.agents/rules/`)

### 1. `radical_honesty_and_pipeline_enforcement.md`
- **Scope:** Universal across all agents and sessions.
- **Directives Codified:** Directives 0, 1, 3, 11, 12.1.
- **Key Invariants:** Binary Honesty Protocol ("Yes"/"No" first word), Pre-Flight Pipeline Declaration, Micro-Stage Triad generation, Interactive Stage-Gate halt, Sole Orchestrator Mandate.

### 2. `file_naming_rules.md`
- **Scope:** Universal across all created, modified, or exported files.
- **Directives Codified:** Directive 6.
- **Key Invariants:** Strict English ASCII naming (`[a-zA-Z0-9_.-]+`). Non-ASCII / Persian characters prohibited in filenames to avoid Windows CP1252 codepage crashes and terminal encoding corruptions.

### 3. `git_lifecycle_rules.md`
- **Scope:** Version control management.
- **Directives Codified:** Directive 8.
- **Key Invariants:** Automatic staging of modified project files, conventional semantic commits (`feat:`, `fix:`, `docs:`, `refactor:`), maintaining a clean working tree at the end of every turn.

### 4. `persian_font_rules.md`
- **Scope:** Document compilation and formatting (`.docx`, `.pptx`).
- **Directives Codified:** Directives 4, 4.1, 5.
- **Key Invariants:** Persian body text bound to `B Nazanin` (13–14 pt), headings bound to `B Titr` (12–18 pt), numbers and stats bound to `Times New Roman`. OpenXML BiDi flags `<w:bidi w:val="1"/>`, `<w:bidiVisual/>`. Decoupled LTR numbers so minus signs precede numbers ($-0.32$). Zero manual line breaks.

### 5. `digital_twin_rules.md`
- **Scope:** Agent persona and user interaction.
- **Directives Codified:** Directives 6, 7, 13.
- **Key Invariants:** Default communication in English; Persian reserved for client deliverables. Scholarly persona representing Saber Ghaderi. Deterministic pricing calculations in Tomans.

### 6. `chapter4_hypothesis_and_sem_structure_rules.md`
- **Scope:** Chapter 4 statistical findings.
- **Directives Codified:** Directives 3, 4, 10.
- **Key Invariants:** Mandatory 3-table format for each hypothesis test (descriptive/correlational, ANOVA/model summary, parameter coefficients). Hu & Bentler (1999) 11-index SEM fit reporting. One-hypothesis-one-stage micro-stage isolation.

---

## 4. Plugin Rules (`.agents/plugins/academic-suite/rules/AGENTS.md`)

The `academic-suite` plugin consolidates domain rules loaded globally across sessions:
1. **Radical Honesty & Pipeline Enforcement**: Directives 0, 1, 3, 11, 12.1.
2. **File Naming Standards**: Directive 6.
3. **Persian Academic Typography & Font Standards**: Directives 4, 5.
4. **Git Lifecycle & Clean Working Tree**: Directive 8.

---

## 5. Machine Enforcement Architecture (`hooks.json`)

Mechanical rule enforcement is handled via `.agents/hooks.json`:

```json
{
  "constitutional-guard": {
    "enabled": true,
    "PreToolUse": [
      {
        "matcher": "run_command|write_to_file|replace_file_content",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .agents/verification/transcript_and_rule_guard.py --event PreToolUse",
            "timeout": 15
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "run_command|write_to_file",
        "hooks": [
          {
            "type": "command",
            "command": "python3 .agents/verification/transcript_and_rule_guard.py --event PostToolUse",
            "timeout": 15
          }
        ]
      }
    ],
    "PreInvocation": [
      {
        "type": "command",
        "command": "python3 .agents/verification/transcript_and_rule_guard.py --event PreInvocation",
        "timeout": 15
      }
    ],
    "Stop": [
      {
        "type": "command",
        "command": "python3 .agents/verification/transcript_and_rule_guard.py --event Stop",
        "timeout": 15
      }
    ]
  }
}
```

### Guard Capabilities (`transcript_and_rule_guard.py` & `skill_size_guard.py`):
1. **PreToolUse:** Intercepts write and command operations to block non-ASCII filenames and dangerous bash patterns.
2. **PostToolUse:** Inspects output paths to verify physical generation of required artifacts.
3. **PreInvocation:** Injects active constitutional constraints before model generation.
4. **Stop:**
   - Inspects `transcript.jsonl` to ensure compliance with the **Binary Honesty Protocol** when questions were asked.
   - Inspects `transcript.jsonl` to confirm subagents were physically invoked via `invoke_subagent` if multi-agent execution was reported.
   - Executes `skill_size_guard.py` to enforce the 500-line / 40 KB ceiling on all `SKILL.md` files.
