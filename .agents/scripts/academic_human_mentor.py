#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/academic_human_mentor.py — AcademicSuite Proactive Human Mentorship Engine

Enables direct, proactive knowledge injection from the research mentor (Saber Ghaderi)
into AcademicSuite persistent memory. Transforms human guidance, methodology standards,
and statistical rules into validated knowledge artifacts (principles, patterns, anti-patterns, lessons)
that are immediately indexed, shared across projects (via Git), and budgeted into agent pre-flight briefings.

Strictly adheres to:
- Directive 6: English-only filenames on disk.
- Directive 18: <= 500 lines, <= 40,000 bytes.
- Directive 19: Agent decides, Skill instructs, Script computes.
"""

import os
import sys
import json
import uuid
import re
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.academic_knowledge_manager import AcademicKnowledgeManager, ContractValidationError

CAPABILITY_KEYWORDS = {
    "mediation": ["mediation", "indirect effect", "bootstrap", "sobel", "میانجی", "اثر غیرمستقیم"],
    "moderation": ["moderation", "interaction", "johnson-neyman", "simple slopes", "تعدیل", "اثر تعاملی"],
    "SEM": ["sem", "structural equation", "lisrel", "amos", "mplus", "معادلات ساختاری", "برازش"],
    "psychometrics": ["cfa", "efa", "reliability", "validity", "omega", "cronbach", "scale", "روانسنجی", "عاملی", "پایایی", "روایی"],
    "chapter4": ["chapter 4", "chapter4", "findings", "یافته‌ها", "فصل چهار", "فصل ۴"],
    "chapter5": ["chapter 5", "chapter5", "discussion", "بحث و نتیجه‌گیری", "فصل پنج", "فصل ۵"],
    "evidence": ["literature", "synthesis", "review", "citation", "پیشینه", "ادبیات", "مرور"],
    "ancova": ["ancova", "covariate", "homogeneity of regression", "کوواریانس", "آنکوا"],
    "regression": ["regression", "vif", "collinearity", "رگرسیون", "همخطی"]
}


class AcademicHumanMentor:
    """Proactive knowledge ingestion, parsing, and curation engine."""

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = os.path.abspath(base_dir or os.environ.get("ACADEMIC_SUITE_BASE_DIR") or ROOT_DIR)
        self.km = AcademicKnowledgeManager(base_dir=self.base_dir)

    def teach(
        self,
        category: str,
        statement: str,
        rationale: Optional[str] = None,
        capability: Optional[str] = None,
        skills: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        scope: str = "cross-project",
        defective_pattern: Optional[str] = None,
        corrective_remedy: Optional[str] = None,
        observed_symptoms: Optional[List[str]] = None,
        exclusions: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Validate and store human-taught knowledge as a persistent artifact."""
        clean_cat = category.strip().lower().replace("-", "_")
        clean_cap = self.km.normalize_capability(capability)
        eff_tags = list(tags or [])
        if clean_cap and clean_cap.lower() not in [t.lower() for t in eff_tags]:
            eff_tags.append(clean_cap.lower())
        eff_skills = list(skills or ([clean_cap] if clean_cap else ["general_research"]))

        if clean_cat in ["principle", "rule", "standard"]:
            item_dict = {
                "statement": statement.strip(),
                "scope": scope,
                "domain": clean_cap or "general",
                "capability": clean_cap,
                "tags": eff_tags,
                "applicability": {
                    "criteria": [rationale.strip()] if rationale else ["Foundational rule established by research mentor"],
                    "target_skills": eff_skills
                },
                "exclusions": exclusions or [],
                "source_lessons": ["LSN-HUMAN-MENTOR-DIRECT"],
                "supporting_evaluations": [],
                "contradictions": [],
                "status": "ACCEPTED_ACTIVE",
                "version": "1.0.0"
            }
            item_id = self.km.add_principle(item_dict)
            item_kind = "Principle"

        elif clean_cat in ["pattern", "workflow", "procedure"]:
            item_dict = {
                "statement": statement.strip(),
                "scope": scope,
                "domain": clean_cap or "general",
                "capability": clean_cap,
                "tags": eff_tags,
                "applicability": {
                    "criteria": [rationale.strip()] if rationale else ["Approved methodological workflow procedure"],
                    "target_skills": eff_skills
                },
                "exclusions": exclusions or [],
                "source_lessons": ["LSN-HUMAN-MENTOR-DIRECT"],
                "supporting_evaluations": [],
                "contradictions": [],
                "status": "ACCEPTED_ACTIVE",
                "version": "1.0.0"
            }
            item_id = self.km.add_pattern(item_dict)
            item_kind = "Pattern"

        elif clean_cat in ["anti_pattern", "pitfall", "prohibited"]:
            cat_domain = "statistical" if clean_cap in ["mediation", "moderation", "SEM", "ancova", "regression"] else "methodological"
            item_dict = {
                "category": cat_domain,
                "defective_pattern": defective_pattern.strip() if defective_pattern else statement.strip(),
                "why_defective": rationale.strip() if rationale else "Prohibited defective approach flagged by research mentor.",
                "observed_symptoms": observed_symptoms or ["Identified and flagged during supervision."],
                "corrective_remedy": corrective_remedy.strip() if corrective_remedy else statement.strip(),
                "detection_heuristic": {
                    "trigger_rule": f"Inspect for '{statement.strip()[:40]}'"
                },
                "reusable": True
            }
            item_id = self.km.add_anti_pattern(item_dict)
            item_kind = "Anti-Pattern"

        elif clean_cat in ["lesson", "insight"]:
            is_negative = bool(re.search(r"\b(avoid|never|prohibit|don't|do not|نباید|پرهیز)\b", statement, re.I))
            item_dict = {
                "source_experience_id": "EXP-HUMAN-MENTOR-DIRECT",
                "desired_behavior": statement.strip(),
                "generalization": rationale.strip() if rationale else statement.strip(),
                "scope": scope,
                "confidence": 0.98,
                "evidence": {
                    "evaluation_case_id": "EVAL-HUMAN-MENTOR",
                    "benchmark_fidelity": 1.0,
                    "empirical_support": True,
                    "summary": "Direct instructional mentorship from research supervisor."
                },
                "related_skills": eff_skills,
                "is_active_behavior": True,
                "status": "VALIDATED",
                "trigger_source": "USER_FEEDBACK",
                "lesson_type": "WHAT_NOT_TO_DO" if is_negative else "WHAT_WORKED_WELL"
            }
            item_id = self.km.add_lesson(item_dict)
            item_kind = "Lesson"
        else:
            raise ValueError(f"Unsupported knowledge category: '{category}'. Use principle, pattern, anti_pattern, or lesson.")

        badge = self.format_confirmation_badge(item_id, item_kind, statement, clean_cap, scope)
        return {
            "item_id": item_id,
            "item_kind": item_kind,
            "statement": statement,
            "capability": clean_cap,
            "scope": scope,
            "badge": badge
        }

    def teach_from_natural_language(
        self,
        text: str,
        default_capability: Optional[str] = None,
        scope: str = "cross-project"
    ) -> Dict[str, Any]:
        """Extract category, capability, and statement from natural language (EN or FA)."""
        raw = text.strip()
        cleaned = re.sub(r"^(remember that|learn this|from now on|note that|یادت باشه|به یاد داشته باش)[:,\s]+", "", raw, flags=re.I)

        # 1. Infer Capability
        detected_cap = default_capability
        text_lower = raw.lower()
        if not detected_cap:
            for cap, kw_list in CAPABILITY_KEYWORDS.items():
                if any(kw in text_lower for kw in kw_list):
                    detected_cap = cap
                    break

        # 2. Infer Category
        is_anti_pattern = bool(re.search(r"\b(never|avoid|don't|do not|prohibit|prohibited|نباید|پرهیز|اجتناب|غلط است|اشتباه است)\b", raw, re.I))
        is_pattern = bool(re.search(r"\b(workflow|process|steps|pipeline|sequence|مراحل|فرآیند|گام|چرخه)\b", raw, re.I))
        is_principle = bool(re.search(r"\b(always|must|mandatory|invariant|rule|principle|همیشه|باید|الزامی|اصل|قانون)\b", raw, re.I))

        if is_anti_pattern:
            cat = "anti_pattern"
            rem_m = re.split(r"\b(instead|use|approved remedy|در عوض|به جای آن|استفاده کنید)\b", cleaned, maxsplit=1, flags=re.I)
            if len(rem_m) >= 3:
                defective = rem_m[0].strip()
                remedy = rem_m[2].strip()
            else:
                defective = cleaned
                remedy = f"Avoid {cleaned}"
            return self.teach(
                category=cat,
                statement=cleaned,
                rationale="Direct mentorship guidance from research supervisor.",
                capability=detected_cap,
                scope=scope,
                defective_pattern=defective,
                corrective_remedy=remedy
            )
        elif is_pattern:
            cat = "pattern"
        elif is_principle:
            cat = "principle"
        else:
            cat = "lesson"

        return self.teach(
            category=cat,
            statement=cleaned,
            rationale="Direct mentorship guidance from research supervisor.",
            capability=detected_cap,
            scope=scope
        )

    def list_knowledge(
        self,
        category: Optional[str] = None,
        capability: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """List active learned knowledge items with status and summaries."""
        res = self.km.query(
            capability=self.km.normalize_capability(capability),
            limit=limit
        )
        if category:
            clean_cat = category.strip().lower().replace("-", "_")
            res = [it for it in res if it.get("item_type", "").lower() == clean_cat or clean_cat in it.get("knowledge_id", "").lower()]
        return res[:limit]

    def search_knowledge(
        self,
        query: str,
        category: Optional[str] = None,
        capability: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Search learned knowledge across statement, tags, and remedies."""
        all_items = self.list_knowledge(category=category, capability=capability, limit=100)
        q_clean = query.strip().lower()
        matches = []
        for item in all_items:
            blob = (
                item.get("statement", "") + " " +
                item.get("defective_pattern", "") + " " +
                item.get("corrective_remedy", "") + " " +
                item.get("desired_behavior", "") + " " +
                " ".join(item.get("tags", []))
            ).lower()
            if q_clean in blob:
                matches.append(item)
        return matches

    def supersede(
        self,
        old_id: str,
        new_statement: str,
        rationale: str = "Updated based on modern supervisory guidance."
    ) -> Dict[str, Any]:
        """Retire an obsolete rule and register its updated successor."""
        old_item = self.km.get_item(old_id)
        if not old_item:
            raise FileNotFoundError(f"Knowledge item '{old_id}' not found.")

        item_type = old_item.get("item_type", "principle")
        new_data = dict(old_item)
        new_data.pop("knowledge_id", None)
        new_data.pop("anti_pattern_id", None)
        new_data.pop("exemplar_id", None)
        new_data.pop("lesson_id", None)
        new_data.pop("item_id", None)
        new_data["statement"] = new_statement
        new_data["updated_at"] = datetime.now(timezone.utc).isoformat()
        new_id = self.km.supersede_item(old_id, new_data, rationale=rationale)
        badge = f"🔄 Superseded [{old_id}] with [{new_id}]: {new_statement[:80]}"
        return {
            "old_id": old_id,
            "new_id": new_id,
            "item_type": item_type,
            "statement": new_statement,
            "badge": badge
        }

    def format_confirmation_badge(
        self,
        item_id: str,
        item_kind: str,
        statement: str,
        capability: Optional[str],
        scope: str
    ) -> str:
        """Format clean scholarly confirmation badge for chat and CLI."""
        cap_str = f"`{capability}`" if capability else "General Academic"
        return (
            f"✅ **Knowledge Codified & Persisted**:\n"
            f"- **ID**: `{item_id}` ({item_kind})\n"
            f"- **Scope**: `{scope}` (Shared Learning Active)\n"
            f"- **Target Capability**: {cap_str}\n"
            f"- **Instruction**: \"{statement}\""
        )


def main():
    parser = argparse.ArgumentParser(description="AcademicSuite Proactive Human Mentorship CLI")
    subparsers = parser.add_subparsers(dest="subcommand")

    # teach
    p_teach = subparsers.add_parser("teach", help="Teach a new rule or procedure")
    p_teach.add_argument("--category", choices=["principle", "pattern", "anti_pattern", "lesson"], default="principle")
    p_teach.add_argument("--statement", required=True, help="Instruction or rule statement")
    p_teach.add_argument("--rationale", help="Reasoning or empirical justification")
    p_teach.add_argument("--capability", help="Target capability (e.g. mediation, sem, chapter4)")
    p_teach.add_argument("--scope", default="cross-project", help="Scope containment (default: cross-project)")
    p_teach.add_argument("--skills", nargs="*", help="Target skills")
    p_teach.add_argument("--tags", nargs="*", help="Tags")

    # ingest-text
    p_ingest = subparsers.add_parser("ingest-text", help="Parse and learn from natural language text")
    p_ingest.add_argument("text", help="Natural language instruction (EN or FA)")
    p_ingest.add_argument("--capability", help="Default capability if not in text")
    p_ingest.add_argument("--scope", default="cross-project", help="Scope containment")

    # list
    p_list = subparsers.add_parser("list", help="List learned knowledge items")
    p_list.add_argument("--category", help="Category filter")
    p_list.add_argument("--capability", help="Capability filter")
    p_list.add_argument("--limit", type=int, default=20, help="Max results")

    # search
    p_search = subparsers.add_parser("search", help="Search learned knowledge")
    p_search.add_argument("query", help="Keyword or phrase to search")
    p_search.add_argument("--category", help="Category filter")
    p_search.add_argument("--capability", help="Capability filter")

    # supersede
    p_sup = subparsers.add_parser("supersede", help="Supersede an obsolete rule")
    p_sup.add_argument("--old-id", required=True, help="ID of old item")
    p_sup.add_argument("--statement", required=True, help="New instruction statement")
    p_sup.add_argument("--rationale", default="Supervisory update", help="Superseding rationale")

    args = parser.parse_args()
    mentor = AcademicHumanMentor()

    if args.subcommand == "teach":
        res = mentor.teach(
            category=args.category,
            statement=args.statement,
            rationale=args.rationale,
            capability=args.capability,
            skills=args.skills,
            tags=args.tags,
            scope=args.scope
        )
        print(res["badge"])

    elif args.subcommand == "ingest-text":
        res = mentor.teach_from_natural_language(
            text=args.text,
            default_capability=args.capability,
            scope=args.scope
        )
        print(res["badge"])

    elif args.subcommand == "list":
        items = mentor.list_knowledge(category=args.category, capability=args.capability, limit=args.limit)
        print(json.dumps(items, indent=2, ensure_ascii=False))

    elif args.subcommand == "search":
        items = mentor.search_knowledge(query=args.query, category=args.category, capability=args.capability)
        print(json.dumps(items, indent=2, ensure_ascii=False))

    elif args.subcommand == "supersede":
        res = mentor.supersede(old_id=args.old_id, new_statement=args.statement, rationale=args.rationale)
        print(res["badge"])

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
