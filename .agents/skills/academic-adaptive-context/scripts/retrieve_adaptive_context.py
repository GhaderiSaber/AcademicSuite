#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/skills/academic-adaptive-context/scripts/retrieve_adaptive_context.py

Deterministic CLI tool to query the persistent learning repository and output
a targeted, compact behavioral briefing for an agent prior to executing a task.
Zero mental calculations, zero orchestration, anti-dump filtering.
"""

import os
import sys
import json
import argparse
from typing import Dict, Any, List, Optional

# Auto-discovery of root directory
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

from scripts.academic_knowledge_manager import AcademicKnowledgeManager


def format_markdown_briefing(briefing: Dict[str, Any]) -> str:
    """Format the retrieved pre-task context into a concise, actionable markdown block."""
    ctx = briefing.get("query_context", {})
    cap = ctx.get("capability") or "General"
    task = ctx.get("task") or "Unspecified"
    proj = ctx.get("project_id") or "Cross-Project"
    agent = ctx.get("agent") or "General"

    lines = []
    lines.append(f"### 🧠 Active Learned Behavioral Context ({cap.upper()})")
    lines.append(f"- **Target Capability**: `{cap}` | **Task**: `{task}` | **Agent**: `{agent}` | **Project Scope**: `{proj}`")
    lines.append("")

    # 1. Critical Anti-Patterns to Avoid
    anti_patterns = briefing.get("anti_patterns", [])
    lines.append("#### ⚠️ Critical Anti-Patterns to Avoid:")
    if anti_patterns:
        for ap in anti_patterns:
            ap_id = ap.get("anti_pattern_id", "AP")
            defect = ap.get("defective_pattern", "")
            remedy = ap.get("corrective_remedy", "")
            lines.append(f"- **[{ap_id}] Avoid**: {defect}")
            if remedy:
                lines.append(f"  *Approved Remedy*: {remedy}")
    else:
        lines.append("- *None recorded for this capability/task. Observe standard methodological rigor.*")
    lines.append("")

    # 2. Active Learned Lessons
    lessons = briefing.get("lessons", [])
    lines.append("#### 💡 Active Learned Lessons:")
    if lessons:
        for lsn in lessons:
            lid = lsn.get("lesson_id", "LSN")
            desired = lsn.get("desired_behavior", "")
            gen = lsn.get("generalization", "")
            why = lsn.get("diagnosis", {}).get("rationale_why", "")
            lines.append(f"- **[{lid}] Mandate**: {desired}")
            if gen:
                lines.append(f"  *Generalization*: {gen}")
            if why:
                lines.append(f"  *Rationale*: {why}")
    else:
        lines.append("- *No specialized lessons flagged. Standard pipeline rules apply.*")
    lines.append("")

    # 3. Verified Exemplars
    exemplars = briefing.get("exemplars", [])
    lines.append("#### 🏆 Verified Gold-Standard Exemplars to Emulate:")
    if exemplars:
        for ex in exemplars:
            eid = ex.get("exemplar_id", "EXM")
            why_ex = ex.get("why_exemplary", "")
            ttype = ex.get("task_type", "")
            lines.append(f"- **[{eid}] ({ttype})**: {why_ex}")
    else:
        lines.append("- *No specific exemplar registered for this task.*")
    lines.append("")

    # 4. Capability Telemetry & Calibrated Defaults
    cap_sum = briefing.get("capability_summary")
    if cap_sum and cap_sum.get("total_invocations", 0) > 0:
        lines.append("#### 🎯 Calibrated Parameter Defaults & Known Operational Bounds:")
        defaults = cap_sum.get("calibrated_parameter_defaults", {})
        if defaults:
            lines.append(f"- **Learned Parameter Defaults**: `{json.dumps(defaults)}`")
        else:
            lines.append("- **Learned Parameter Defaults**: Standard CLI defaults.")
        lines.append(f"- **Historical Telemetry**: {cap_sum.get('total_invocations', 0)} total runs | {cap_sum.get('success_count', 0)} passed | {cap_sum.get('failure_count', 0)} failed.")
        lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Retrieve targeted active behavioral context for an academic task.")
    parser.add_argument("--capability", help="Capability identifier (e.g. mediation, SEM, longitudinal-analysis)")
    parser.add_argument("--task", default="general_task", help="Specific task type (e.g. bootstrap_mediation)")
    parser.add_argument("--agent", help="Actor agent role name")
    parser.add_argument("--skill", help="Implicated skill name")
    parser.add_argument("--domain", help="Methodological or substantive domain")
    parser.add_argument("--tags", nargs="*", help="Topical tags")
    parser.add_argument("--project-id", help="Active project ID for strict scope containment")
    parser.add_argument("--limit", type=int, default=3, help="Max items per section")
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown", help="Output format")
    parser.add_argument("--base-dir", help="Base repository directory override")
    args = parser.parse_args()

    km = AcademicKnowledgeManager(base_dir=args.base_dir)

    briefing = km.retrieve_pre_task_context(
        task=args.task,
        agent=args.agent,
        skill=args.skill,
        capability=args.capability,
        domain=args.domain,
        tags=args.tags,
        project_id=args.project_id,
        limit_per_category=args.limit
    )

    if args.format == "json":
        print(json.dumps(briefing, indent=2, ensure_ascii=False))
    else:
        print(format_markdown_briefing(briefing))


if __name__ == "__main__":
    main()
