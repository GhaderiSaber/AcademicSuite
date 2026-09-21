#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/academic_context_token_budgeter.py — Dynamic Context Token Budgeting Engine

Implements Phase 41: Dynamic Context Token Budgeting for AcademicSuite.
Features:
1. Deterministic token estimation for bilingual (English & Persian) text and Markdown.
2. Priority-weighted knapsack selection allocating token budget across knowledge categories:
   - Pitfalls / Anti-Patterns (1.5x)
   - Calibrated Operational Defaults (1.4x)
   - Relevant Active Lessons (1.2x)
   - Methodology Rules & Contradictions (1.0x)
   - Gold-Standard Exemplars (0.8x)
3. Dual compression modes:
   - STANDARD (>= 500 tokens): Full mandates, remedies, generalizations, exemplars.
   - COMPACT (< 500 tokens): Lean mandates, essential anti-patterns, zero exemplars.
4. Comprehensive budget telemetry and audit logging.

Strictly complies with Directive 18 (<= 500 lines, <= 40,000 bytes) and Directive 12.1.
"""

import re
import json
import math
from typing import Dict, Any, List, Optional, Tuple, Set

try:
    import tiktoken
    _TIKTOKEN_ENC = tiktoken.get_encoding("cl100k_base")
except Exception:
    _TIKTOKEN_ENC = None

PERSIAN_WORD_RE = re.compile(r"[\u0600-\u06FF\uFB50-\uFDFF\uFE70-\uFEFF\u200c]+")
LATIN_WORD_RE = re.compile(r"[A-Za-z0-9_]+")
PUNCT_RE = re.compile(r"[^\w\s\u0600-\u06FF\uFB50-\uFDFF\uFE70-\uFEFF\u200c]")


def estimate_tokens(text: Optional[str]) -> int:
    """Deterministically estimates BPE token count for bilingual English/Persian text."""
    if not text:
        return 0

    if _TIKTOKEN_ENC is not None:
        try:
            return len(_TIKTOKEN_ENC.encode(text))
        except Exception:
            pass

    persian_words = PERSIAN_WORD_RE.findall(text)
    latin_words = LATIN_WORD_RE.findall(text)
    punct_count = len(PUNCT_RE.findall(text))

    token_count = 0.0
    for w in persian_words:
        clean_w = w.replace("\u200c", "")
        token_count += max(1.2, len(clean_w) * 0.40)

    for w in latin_words:
        token_count += max(1.0, len(w) / 3.8)

    token_count += punct_count * 0.85
    token_count += text.count("\n") * 0.5

    return max(1, int(math.ceil(token_count)))


class AcademicContextTokenBudgeter:
    """Priority-weighted knapsack token budgeting engine for adaptive pre-task context."""

    PRIORITY_WEIGHTS = {
        "anti_pattern": 1.50,
        "calibrated_defaults": 1.40,
        "lesson": 1.20,
        "contradiction": 1.00,
        "methodology_rule": 1.00,
        "exemplar": 0.80
    }

    COMPACT_BUDGET_THRESHOLD = 500
    MINIMUM_VIABLE_BUDGET = 150
    DEFAULT_TOKEN_BUDGET = 800
    SUBAGENT_TOKEN_BUDGET = 500

    def __init__(self, default_budget: int = DEFAULT_TOKEN_BUDGET):
        self.default_budget = default_budget

    def budget_context(
        self,
        raw_context: Dict[str, Any],
        max_token_budget: Optional[int] = None,
        target_capability: str = "General",
        task: str = "general_task",
        agent: str = "academic-orchestrator",
        project_id: str = "cross-project"
    ) -> Dict[str, Any]:
        """Applies knapsack selection to fit strictly within max_token_budget."""
        budget = max_token_budget if max_token_budget is not None else self.default_budget
        budget = max(self.MINIMUM_VIABLE_BUDGET, budget)
        mode = "COMPACT" if budget < self.COMPACT_BUDGET_THRESHOLD else "STANDARD"

        # 1. Base Header & Defaults
        header_text = self._build_header(target_capability, task, agent, project_id)
        header_tokens = estimate_tokens(header_text)

        cap_sum = raw_context.get("capability_summary", {})
        defaults = cap_sum.get("calibrated_parameter_defaults", {}) if cap_sum else {}
        defaults_text = f"🎯 Calibrated Defaults: `{json.dumps(defaults)}`\n\n" if defaults else ""
        defaults_tokens = estimate_tokens(defaults_text) if defaults else 0

        overhead_tokens = header_tokens + defaults_tokens + (15 if mode == "COMPACT" else 35)
        content_budget = max(0, budget - overhead_tokens)

        # 2. Knapsack Selection
        candidates = self._prepare_candidate_items(raw_context, mode=mode)
        selected_items, pruned_items = self._select_items_knapsack(candidates, content_budget, mode=mode)

        budgeted_lessons = [item["raw"] for item in selected_items if item["category"] == "lesson"]
        budgeted_anti_patterns = [item["raw"] for item in selected_items if item["category"] == "anti_pattern"]
        budgeted_rules = [item["raw"] for item in selected_items if item["category"] in ["contradiction", "methodology_rule"]]
        budgeted_exemplars = [item["raw"] for item in selected_items if item["category"] == "exemplar"]

        # 3. Format & Strict Ceiling Loop
        formatted_briefing, final_estimated_tokens = self._format_briefing_with_badge(
            header_text, budgeted_anti_patterns, budgeted_lessons,
            budgeted_rules, budgeted_exemplars, defaults_text, budget, mode
        )

        while final_estimated_tokens > budget and (budgeted_exemplars or budgeted_rules or budgeted_lessons or len(budgeted_anti_patterns) > 1):
            if budgeted_exemplars:
                popped = budgeted_exemplars.pop()
                pruned_items.append({"item_id": popped.get("exemplar_id") or "EXM", "category": "exemplar", "reason": "Trimmed to meet budget"})
            elif budgeted_rules:
                popped = budgeted_rules.pop()
                pruned_items.append({"item_id": popped.get("contradiction_id") or "CTD", "category": "contradiction", "reason": "Trimmed to meet budget"})
            elif budgeted_lessons:
                popped = budgeted_lessons.pop()
                pruned_items.append({"item_id": popped.get("lesson_id") or "LSN", "category": "lesson", "reason": "Trimmed to meet budget"})
            elif len(budgeted_anti_patterns) > 1:
                popped = budgeted_anti_patterns.pop()
                pruned_items.append({"item_id": popped.get("anti_pattern_id") or "AP", "category": "anti_pattern", "reason": "Trimmed to meet budget"})

            formatted_briefing, final_estimated_tokens = self._format_briefing_with_badge(
                header_text, budgeted_anti_patterns, budgeted_lessons,
                budgeted_rules, budgeted_exemplars, defaults_text, budget, mode
            )

        if final_estimated_tokens > budget and budgeted_anti_patterns:
            top_ap = dict(budgeted_anti_patterns[0])
            top_ap["corrective_remedy"] = ""
            budgeted_anti_patterns[0] = top_ap
            formatted_briefing, final_estimated_tokens = self._format_briefing_with_badge(
                header_text, budgeted_anti_patterns, budgeted_lessons,
                budgeted_rules, budgeted_exemplars, defaults_text, budget, mode="COMPACT"
            )

        utilization = round(min(1.0, final_estimated_tokens / budget), 3)
        telemetry = {
            "max_token_budget": budget,
            "estimated_tokens_used": final_estimated_tokens,
            "budget_utilization_ratio": utilization,
            "compression_mode": mode,
            "items_selected": {
                "pitfalls": len(budgeted_anti_patterns),
                "lessons": len(budgeted_lessons),
                "methodology_rules": len(budgeted_rules),
                "defaults": 1 if defaults else 0,
                "exemplars": len(budgeted_exemplars)
            },
            "items_pruned_by_budget": len(pruned_items),
            "pruned_details": pruned_items
        }

        return {
            "contract_version": "1.0.0",
            "target_capability": target_capability,
            "task": task,
            "agent": agent,
            "project_id": project_id,
            "compression_mode": mode,
            "budget_telemetry": telemetry,
            "relevant_lessons": budgeted_lessons,
            "known_pitfalls": budgeted_anti_patterns,
            "applicable_methodology_rules": budgeted_rules,
            "calibrated_defaults": defaults if defaults else {},
            "exemplars": budgeted_exemplars,
            "formatted_briefing": formatted_briefing
        }

    def _build_header(self, cap: str, task: str, agent: str, proj: str) -> str:
        return (
            f"🧠 DETERMINISTIC ADAPTIVE CONTEXT (BOUND AT EXECUTION BOUNDARY)\n"
            f"- **Target Capability**: `{cap.upper()}` | **Task**: `{task}` | **Agent**: `{agent}` | **Project**: `{proj}`\n\n"
        )

    def _prepare_candidate_items(self, raw_context: Dict[str, Any], mode: str) -> List[Dict[str, Any]]:
        candidates = []
        for ap in raw_context.get("anti_patterns", []):
            item_id = ap.get("anti_pattern_id") or ap.get("item_id") or "AP"
            score = float(ap.get("score") or ap.get("confidence") or 0.85)
            text_rep = self._render_anti_pattern(ap, mode)
            candidates.append({
                "item_id": item_id, "category": "anti_pattern", "score": score,
                "text": text_rep, "tokens": estimate_tokens(text_rep),
                "priority_weight": self.PRIORITY_WEIGHTS["anti_pattern"], "raw": ap
            })

        for lsn in raw_context.get("lessons", []):
            item_id = lsn.get("lesson_id") or lsn.get("item_id") or "LSN"
            score = float(lsn.get("score") or lsn.get("confidence") or 0.80)
            text_rep = self._render_lesson(lsn, mode)
            candidates.append({
                "item_id": item_id, "category": "lesson", "score": score,
                "text": text_rep, "tokens": estimate_tokens(text_rep),
                "priority_weight": self.PRIORITY_WEIGHTS["lesson"], "raw": lsn
            })

        for ctd in raw_context.get("contradictions", []):
            item_id = ctd.get("contradiction_id") or ctd.get("item_id") or "CTD"
            score = float(ctd.get("score") or 0.75)
            text_rep = self._render_rule(ctd, mode)
            candidates.append({
                "item_id": item_id, "category": "contradiction", "score": score,
                "text": text_rep, "tokens": estimate_tokens(text_rep),
                "priority_weight": self.PRIORITY_WEIGHTS["contradiction"], "raw": ctd
            })

        for prn in raw_context.get("principles", []):
            item_id = prn.get("knowledge_id") or prn.get("item_id") or "PRN"
            score = float(prn.get("score") or prn.get("confidence") or 0.85)
            text_rep = self._render_rule(prn, mode)
            candidates.append({
                "item_id": item_id, "category": "contradiction", "score": score,
                "text": text_rep, "tokens": estimate_tokens(text_rep),
                "priority_weight": self.PRIORITY_WEIGHTS["methodology_rule"], "raw": prn
            })

        for ptr in raw_context.get("patterns", []):
            item_id = ptr.get("knowledge_id") or ptr.get("item_id") or "PTR"
            score = float(ptr.get("score") or ptr.get("confidence") or 0.80)
            text_rep = self._render_rule(ptr, mode)
            candidates.append({
                "item_id": item_id, "category": "contradiction", "score": score,
                "text": text_rep, "tokens": estimate_tokens(text_rep),
                "priority_weight": self.PRIORITY_WEIGHTS["methodology_rule"], "raw": ptr
            })

        if mode == "STANDARD":
            for ex in raw_context.get("exemplars", []):
                item_id = ex.get("exemplar_id") or ex.get("item_id") or "EXM"
                score = float(ex.get("score") or 0.70)
                text_rep = self._render_exemplar(ex)
                candidates.append({
                    "item_id": item_id, "category": "exemplar", "score": score,
                    "text": text_rep, "tokens": estimate_tokens(text_rep),
                    "priority_weight": self.PRIORITY_WEIGHTS["exemplar"], "raw": ex
                })
        return candidates

    def _select_items_knapsack(
        self,
        candidates: List[Dict[str, Any]],
        content_budget: int,
        mode: str
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
        selected, pruned = [], []
        rem_budget = content_budget
        caps = {
            "anti_pattern": 3 if mode == "STANDARD" else 2,
            "lesson": 3 if mode == "STANDARD" else 2,
            "contradiction": 2 if mode == "STANDARD" else 1,
            "exemplar": 1
        }
        counts = {k: 0 for k in caps}

        # Floor: top Anti-Pattern
        pitfalls = [c for c in candidates if c["category"] == "anti_pattern"]
        if pitfalls:
            pitfalls.sort(key=lambda x: x["score"], reverse=True)
            top_ap = pitfalls[0]
            if top_ap["tokens"] <= rem_budget:
                selected.append(top_ap)
                rem_budget -= top_ap["tokens"]
                counts["anti_pattern"] += 1
                candidates = [c for c in candidates if c["item_id"] != top_ap["item_id"]]

        for c in candidates:
            c["density"] = round((c["priority_weight"] * c["score"]) / max(10, c["tokens"]), 5)
        candidates.sort(key=lambda x: (x["density"], x["score"]), reverse=True)

        for c in candidates:
            cat = c["category"]
            if counts.get(cat, 0) >= caps.get(cat, 3):
                pruned.append({"item_id": c["item_id"], "category": cat, "estimated_tokens": c["tokens"], "reason": f"Quota reached for {cat}"})
                continue
            if c["tokens"] <= rem_budget:
                selected.append(c)
                rem_budget -= c["tokens"]
                counts[cat] += 1
            else:
                pruned.append({"item_id": c["item_id"], "category": cat, "estimated_tokens": c["tokens"], "reason": f"Exceeded remaining budget of {rem_budget} tokens"})

        return selected, pruned

    def _render_anti_pattern(self, ap: Dict[str, Any], mode: str) -> str:
        ap_id = ap.get("anti_pattern_id") or ap.get("item_id") or "AP"
        defect = ap.get("defective_pattern") or ap.get("defect") or ""
        remedy = ap.get("corrective_remedy") or ap.get("remedy") or ""
        if mode == "COMPACT" or not remedy:
            return f"- [{ap_id}] Avoid: {defect}"
        return f"- [{ap_id}] Avoid: {defect}\n  Approved Remedy: {remedy}"

    def _render_lesson(self, lsn: Dict[str, Any], mode: str) -> str:
        lid = lsn.get("lesson_id") or lsn.get("item_id") or "LSN"
        desired = lsn.get("desired_behavior") or lsn.get("mandate") or ""
        gen = lsn.get("generalization") or ""
        if mode == "COMPACT" or not gen:
            return f"- [{lid}] Mandate: {desired}"
        return f"- [{lid}] Mandate: {desired}\n  Generalization: {gen}"

    def _render_rule(self, ctd: Dict[str, Any], mode: str) -> str:
        cid = ctd.get("contradiction_id") or ctd.get("knowledge_id") or ctd.get("item_id") or "CTD"
        raw_type = ctd.get("conflict_type") or ctd.get("item_type", "Rule")
        ctype = str(raw_type).replace("_", " ").capitalize()
        desc = ctd.get("description") or ctd.get("statement") or ""
        conds = ctd.get("applicability_conditions") or ctd.get("applicability", {}).get("criteria", {})
        if mode == "COMPACT" or not conds:
            return f"- [{cid}] {ctype}: {desc}"
        cond_lines = []
        if isinstance(conds, dict) and conds.get("condition_for_a"):
            cond_lines = [f"  Condition A: {conds['condition_for_a']}"]
        elif isinstance(conds, list) and conds and conds != ["Foundational rule established by research mentor"]:
            cond_lines = [f"  Criteria: {conds[0]}"]
        return f"- [{cid}] {ctype}: {desc}\n" + "\n".join(cond_lines) if cond_lines else f"- [{cid}] {ctype}: {desc}"

    def _render_exemplar(self, ex: Dict[str, Any]) -> str:
        eid = ex.get("exemplar_id") or ex.get("item_id") or "EXM"
        return f"- [{eid}] ({ex.get('task_type') or 'task'}): {ex.get('why_exemplary') or ''}"

    def _format_briefing_with_badge(
        self,
        header_text: str,
        budgeted_anti_patterns: List[Dict[str, Any]],
        budgeted_lessons: List[Dict[str, Any]],
        budgeted_rules: List[Dict[str, Any]],
        budgeted_exemplars: List[Dict[str, Any]],
        defaults_text: str,
        budget: int,
        mode: str
    ) -> Tuple[str, int]:
        lines = []

        if budgeted_anti_patterns or mode == "STANDARD":
            lines.append("⚠️ Known Pitfalls (Anti-Patterns to Avoid):")
            if budgeted_anti_patterns:
                for ap in budgeted_anti_patterns:
                    lines.append(self._render_anti_pattern(ap, mode))
            else:
                lines.append("- None cataloged. Enforce standard APA 7 & OpenXML rigor.")
            lines.append("")

        if budgeted_lessons or mode == "STANDARD":
            lines.append("💡 Relevant Active Lessons:")
            if budgeted_lessons:
                for lsn in budgeted_lessons:
                    lines.append(self._render_lesson(lsn, mode))
            else:
                lines.append("- No specialized lessons flagged. Standard pipeline rules apply.")
            lines.append("")

        if budgeted_rules or mode == "STANDARD":
            lines.append("⚖️ Applicable Methodology Rules & Boundary Conditions:")
            if budgeted_rules:
                for r in budgeted_rules:
                    lines.append(self._render_rule(r, mode))
            else:
                lines.append("- No conflicting paradigms active. Follow primary statistical decision tree.")
            lines.append("")

        if budgeted_exemplars and mode == "STANDARD":
            lines.append("🏆 Gold-Standard Exemplars to Emulate:")
            for ex in budgeted_exemplars:
                lines.append(self._render_exemplar(ex))
            lines.append("")

        if defaults_text:
            lines.append(defaults_text.strip())
            lines.append("")

        body_text = "\n".join(lines).strip()
        prelim_tokens = estimate_tokens(header_text + body_text)
        pct = round((prelim_tokens / budget) * 100, 1)

        badge = f" [Budget: ~{prelim_tokens}/{budget} tokens ({pct}%)]"
        h_lines = header_text.splitlines()
        if h_lines:
            h_lines[0] = h_lines[0] + badge
        badged_header = "\n".join(h_lines) + "\n\n"

        full_briefing = badged_header + body_text
        return full_briefing, estimate_tokens(full_briefing)
