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

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
for p in [ROOT_DIR, AGENTS_DIR, os.path.join(AGENTS_DIR, "scripts")]:
    if os.path.isdir(p) and p not in sys.path:
        sys.path.insert(0, p)

try:
    from scripts.academic_knowledge_manager import AcademicKnowledgeManager
except ImportError:
    from academic_knowledge_manager import AcademicKnowledgeManager


def format_markdown_briefing(briefing: Dict[str, Any]) -> str:
    """Format the retrieved pre-task context into a concise, actionable markdown block."""
    ctx = briefing.get("query_context", {})
    cap = ctx.get("capability") or "General"
    task = ctx.get("task") or "Unspecified"
    proj = ctx.get("project_id") or "Cross-Project"
    agent = ctx.get("agent") or "General"
    telem = briefing.get("budget_telemetry")
    badge = ""
    if telem and telem.get("max_token_budget"):
        used = telem.get("estimated_tokens_used", 0)
        budget = telem.get("max_token_budget", 800)
        pct = round(telem.get("budget_utilization_ratio", 0) * 100, 1)
        badge = f" [Budget: ~{used}/{budget} tokens ({pct}%)]"

    lines = []
    lines.append(f"### 🧠 Active Learned Behavioral Context ({cap.upper()}){badge}")
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

    # 4. Reconciled Methodological Contradictions & Applicability Bounds
    contradictions = briefing.get("contradictions", [])
    if contradictions:
        lines.append("#### ⚖️ Reconciled Methodological Contradictions & Applicability Bounds:")
        for ctd in contradictions:
            cid = ctd.get("contradiction_id", "CTD")
            ctype = ctd.get("conflict_type", "CONFLICT")
            desc = ctd.get("description", "")
            conds = ctd.get("applicability_conditions", {})
            lines.append(f"- **[{cid}] {ctype}**: {desc}")
            if conds.get("condition_for_a"):
                lines.append(f"  *When Rule A applies*: {conds.get('condition_for_a')}")
            if conds.get("condition_for_b"):
                lines.append(f"  *When Rule B applies*: {conds.get('condition_for_b')}")
        lines.append("")

    # 5. Capability Telemetry & Calibrated Defaults
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

    # 6. Dynamic Budget Telemetry (Phase 41)
    if telem and telem.get("max_token_budget"):
        lines.append("#### 📊 Budget Telemetry & Quota Audit:")
        used = telem.get("estimated_tokens_used", 0)
        budget = telem.get("max_token_budget", 800)
        pct = telem.get("budget_utilization_ratio", 0) * 100
        mode = telem.get("compression_mode", "STANDARD")
        lines.append(f"- **Max Budget**: {budget} tokens | **Estimated Tokens**: {used} ({pct:.1f}%) | **Mode**: `{mode}`")
        if telem.get("items_pruned_by_budget", 0) > 0:
            lines.append(f"- **Pruned for Budget**: {telem['items_pruned_by_budget']} items pruned to preserve context economy.")
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
    parser.add_argument("--max-tokens", type=int, default=800, help="Maximum token budget for pre-task briefing (Phase 41)")
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
        limit_per_category=args.limit,
        max_token_budget=args.max_tokens
    )

    if args.format == "json":
        print(json.dumps(briefing, indent=2, ensure_ascii=False))
    else:
        print(format_markdown_briefing(briefing))


if __name__ == "__main__":
    main()
