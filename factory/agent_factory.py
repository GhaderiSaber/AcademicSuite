#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
factory/agent_factory.py — Autonomous Subagent Specification Factory

Generates fully-specified, constitutional Antigravity subagents in .agents/agents/
with persistent cognitive roles, skill bindings, and decision-tree architectures.
"""

import os
import sys
from typing import Dict, Any, List, Optional

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents", "agents")


CONSTITUTIONAL_DIRECTIVES = """## 🛑 Mandatory Constitutional Directives (AGENTS.md Compliance)
All subagents in this workspace operate under strict adherence to `AGENTS.md`:
1. **Directive 0 (Binary Honesty & Anti-Deception)**: Zero defensive rationalization. Never fabricate numbers, citations, or compliance claims. If asked a compliance question, start with an unambiguous "Yes" or "No".
2. **Directive 2 (Deterministic Calculations)**: Never calculate statistics, p-values, or effect sizes mentally. Execute deterministic Python scripts in `.agents/skills/<skill>/scripts/` on the actual dataset.
3. **Directive 4 (APA 7 & Persian Leading Zero Standard)**: Italicize Latin statistical symbols (*M, SD, t, F, p, r, R², β, z*). NEVER omit leading zeros in Persian (`۰.۰۵`, `۰.۰۰۱`). Report p < .001 or ۰.۰۰۱ > p (never .000). Zero emojis in academic text or slides.
4. **Directive 5 (BiDi OpenXML & Persian Font Binding)**: Enforce RTL paragraph `<w:bidi/>`. Bind Persian fonts to `B Nazanin` (body) and `B Titr` (headings), with Latin in `Times New Roman`. Preserve Word OMML math equations (`<m:oMath>`).
5. **Directive 6 (English-Only Filenames)**: Every file and directory on disk MUST use English ASCII characters only (`[a-zA-Z0-9_.-]`).
6. **Directive 14 (Anti-Hallucination & Zero Ghost Citations)**: Never invent bibliographic references. All citations must be verified against real academic databases.
7. **Directive 15 (Temporal Anchor: 2026)**: Current operative year is 2026 (1405 SH).
"""


def generate_agent_markdown(
    name: str,
    role: str,
    description: str,
    skills: List[str],
    mission: str,
    decision_rules: List[str],
    anti_patterns: Optional[List[str]] = None
) -> str:
    """
    Generates the complete, standardized Markdown text for an Antigravity agent definition.
    """
    anti_patterns = anti_patterns or [
        "Never calculate statistics in your head (violates Directive 2).",
        "Never omit the Persian leading zero before decimals (violates Directive 4).",
        "Never skip the Pre-Flight Pipeline Declaration (violates Directive 1)."
    ]

    skills_yaml = "\n".join([f"- {s}" for s in skills])
    rules_md = "\n".join([f"{i+1}. {r}" for i, r in enumerate(decision_rules)])
    anti_md = "\n".join([f"- ❌ {ap}" for ap in anti_patterns])

    content = f"""---
name: {name}
description: >-
  {description}
role: {role}
skills:
{skills_yaml}
---

# {role}

{CONSTITUTIONAL_DIRECTIVES}

---

## 🏛️ Identity & Domain Mission

You are the **{role}** in Digital Saber's cognitive architecture.
{mission}

---

## ⚙️ Foundational Decision Sequences & Methodological Philosophy

Always execute the following domain procedures:

{rules_md}

---

## 🚫 Prohibited Anti-Patterns

{anti_md}

---

## 📦 Deliverables & Artifact Hand-off

1. Output must be saved as structured, machine-readable JSON checkpoints and OpenXML Word artifacts on disk.
2. Every output must be certified by independent validators prior to handoff.
3. Handoff to the next pipeline stage must reference the exact physical disk path.
"""
    return content


def generate_contract_markdown(
    name: str,
    role: str,
    mission: str,
    skills: List[str],
    responsibilities: Optional[List[str]] = None,
    non_responsibilities: Optional[List[str]] = None,
    forbidden_actions: Optional[List[str]] = None
) -> str:
    """
    Generates the formal 12-section contract Markdown adhering to Phase 4 & Option 1 standards.
    """
    can_items = responsibilities or [
        f"Execute domain analytical workflows for {role}.",
        "Generate structured analysis results and machine-readable JSON checkpoints.",
        "Produce verified tables and narrative drafts adhering to APA 7 standards."
    ]
    cannot_items = non_responsibilities or [
        "Calculate, estimate, or hallucinate statistical numbers mentally (Directive 2).",
        "Modify raw empirical datasets or overwrite files in place.",
        "Self-validate deliverables without independent review by validation-agent."
    ]
    forbidden = forbidden_actions or [
        "Zero Mental Math: Never guess or estimate parameters mentally (Directive 2).",
        "Zero Non-ASCII Filenames: Strictly use English ASCII characters for all disk files (Directive 6).",
        "Zero Unverified Citations: Never invent bibliographic data (Directive 14)."
    ]

    can_md = "\n".join([f"- {item}" for item in can_items])
    cannot_md = "\n".join([f"- {item}" for item in cannot_items])
    skills_md = "\n".join([f"- `{s}`" for s in skills])
    forbidden_md = "\n".join([f"- **{f.split(':')[0]}:**{':'.join(f.split(':')[1:])}" if ':' in f else f"- {f}" for f in forbidden])

    return f"""# Agent Contract: {role}

**Role Identifier:** `{name}`  
**Operational Tier:** Tier 2 — Domain Specialist  
**Contract Version:** 1.0.0  
**Effective Date:** September 2026 (1405 SH)  

---

## MISSION
{mission}

---

## RESPONSIBILITIES

### CAN:
{can_md}

---

## NON-RESPONSIBILITIES

### CANNOT:
{cannot_md}

---

## INPUTS
- Target dataset or input payload checkpoint (`.xlsx`, `.json`, `.docx`).
- Research questions, variable definitions, and model specifications.

---

## OUTPUTS
- Structured JSON checkpoints: `stats_results.json`, `findings.json`.
- APA 7 tables and narrative report files.
- Synchronized micro-stage triads (`.docx`, `.md`, `.json`).

---

## ALLOWED TOOLS
- `view_file` (Inspect input payloads and skill specifications)
- `write_to_file` & `replace_file_content` (Export outputs and draft narrative)
- `run_command` (Execute deterministic scripts in `.agents/skills/`)
- `list_dir`, `grep_search`, `find_by_name` (Search and inspect workspace assets)

---

## REQUIRED SKILLS
{skills_md}

---

## FORBIDDEN ACTIONS
{forbidden_md}

---

## HANDOFF FORMAT
The {role} hands off structured artifacts:
```markdown
### 📦 {role} Handoff
- **Domain:** {name}
- **Artifacts Generated on Disk (Triad):**
  - `<output_dir>/output.docx`
  - `<output_dir>/output.md`
  - `<output_dir>/output.json`
- **Validation Status:** PASS
```

---

## VALIDATION REQUIREMENTS
- Deterministic script execution logs present in workspace.
- Passage through independent validators before handoff.
- Verification of synchronized triad on disk.

---

## COMPLETION CRITERIA
- Domain outputs completely generated and saved on disk.
- Zero validator errors across numerical and reporting consistency.

---

## FAILURE CONDITIONS
- Discrepancy between calculated data and narrative text.
- Missing required outputs or non-ASCII filenames on disk.
- Unhandled model errors or failed validator checks.
"""


def create_agent(
    name: str,
    role: str,
    description: str,
    skills: List[str],
    mission: str,
    decision_rules: List[str],
    anti_patterns: Optional[List[str]] = None,
    target_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Creates and writes a verified agent specification package to disk (Option 1 Standard):
    1. Dedicated directory: target_dir/<name>/
    2. Co-located runtime prompt: target_dir/<name>/agent.md
    3. Co-located 12-section contract: target_dir/<name>/contract.md
    4. Flat discovery symlink: target_dir/<name>.md -> <name>/agent.md
    """
    out_dir = target_dir or AGENTS_DIR
    agent_dir = os.path.join(out_dir, name)
    os.makedirs(agent_dir, exist_ok=True)

    agent_file = os.path.join(agent_dir, "agent.md")
    contract_file = os.path.join(agent_dir, "contract.md")
    symlink_path = os.path.join(out_dir, f"{name}.md")

    md_content = generate_agent_markdown(
        name=name,
        role=role,
        description=description,
        skills=skills,
        mission=mission,
        decision_rules=decision_rules,
        anti_patterns=anti_patterns
    )

    contract_content = generate_contract_markdown(
        name=name,
        role=role,
        mission=mission,
        skills=skills
    )

    with open(agent_file, "w", encoding="utf-8") as f:
        f.write(md_content)

    with open(contract_file, "w", encoding="utf-8") as f:
        f.write(contract_content)

    # Maintain backward-compatible flat discovery symlink
    if os.path.islink(symlink_path) or os.path.exists(symlink_path):
        os.remove(symlink_path)
    os.symlink(f"{name}/agent.md", symlink_path)

    return {
        "status": "SUCCESS",
        "agent_name": name,
        "agent_dir": agent_dir,
        "agent_file": agent_file,
        "contract_file": contract_file,
        "file_path": symlink_path,
        "size_bytes": len(md_content.encode("utf-8"))
    }
