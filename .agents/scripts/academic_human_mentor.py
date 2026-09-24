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

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from scripts.academic_knowledge_manager import AcademicKnowledgeManager, ContractValidationError
from scripts.academic_graduation_compiler import AcademicGraduationCompiler

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
        self.compiler = AcademicGraduationCompiler(base_dir=self.base_dir)

    def teach(
        self,
        category: str,
        statement: str,
        rationale: Optional[str] = None,
        capability: Optional[str] = None,
        skills: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        scope: str = "cross-project",
        agent: Optional[str] = None,
        defective_pattern: Optional[str] = None,
        corrective_remedy: Optional[str] = None,
        observed_symptoms: Optional[List[str]] = None,
        exclusions: Optional[List[str]] = None,
        track: str = "auto",
        auto_commit: bool = True,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Validate and store human-taught knowledge as a persistent artifact."""
        clean_cat = category.strip().lower().replace("-", "_")
        clean_cap = self.km.normalize_capability(capability)
        clean_agent = agent.strip().lower() if agent else None
        eff_tags = list(tags or [])
        if clean_cap and clean_cap.lower() not in [t.lower() for t in eff_tags]:
            eff_tags.append(clean_cap.lower())
        eff_skills = list(skills or ([clean_cap] if clean_cap else ["general_research"]))

        if clean_cat in ["principle", "rule", "standard", "pattern", "workflow", "procedure"]:
            is_principle = clean_cat in ["principle", "rule", "standard"]
            default_crit = "Foundational rule established by research mentor" if is_principle else "Approved methodological workflow procedure"
            app_dict: Dict[str, Any] = {
                "criteria": [rationale.strip()] if rationale else [default_crit],
                "target_skills": eff_skills
            }
            if clean_agent:
                app_dict["target_agents"] = [clean_agent]
            item_dict: Dict[str, Any] = {
                "statement": statement.strip(),
                "scope": scope,
                "domain": clean_cap or "general",
                "capability": clean_cap,
                "tags": eff_tags,
                "applicability": app_dict,
                "exclusions": exclusions or [],
                "source_lessons": ["LSN-HUMAN-MENTOR-DIRECT"],
                "supporting_evaluations": [],
                "contradictions": [],
                "status": "ACCEPTED_ACTIVE",
                "version": "1.0.0"
            }
            if clean_agent:
                item_dict["target_agent"] = clean_agent
                item_dict["target_agents"] = [clean_agent]
            if is_principle:
                item_id = self.km.add_principle(item_dict)
                item_kind = "Principle"
            else:
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
            if clean_agent:
                item_dict["target_agent"] = clean_agent
                item_dict["target_agents"] = [clean_agent]
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
            if clean_agent:
                item_dict["target_agent"] = clean_agent
                item_dict["target_agents"] = [clean_agent]
            item_id = self.km.add_lesson(item_dict)
            item_kind = "Lesson"
        else:
            raise ValueError(f"Unsupported knowledge category: '{category}'. Use principle, pattern, anti_pattern, or lesson.")

        # Directive 21 Dual-Track Ingestion & Graduation (The Hands)
        clean_track = str(track).strip().lower()
        if clean_track in ("1", "track1", "track_1"):
            eff_track = 1
        elif clean_track in ("2", "track2", "track_2"):
            eff_track = 2
        else:
            eff_track = 1 if (scope == "cross-project" and clean_cat in ["principle", "pattern", "anti_pattern"]) else 2

        grad_info = None
        if eff_track == 1:
            json_file = None
            for d in [self.km.principles_dir, self.km.patterns_dir, self.km.anti_patterns_dir, self.km.lessons_dir]:
                cand = os.path.join(d, f"{item_id}.json")
                if os.path.isfile(cand):
                    json_file = cand
                    break

            grad_info = self.compiler.graduate_item(
                item_id=item_id,
                statement=statement,
                category=item_kind,
                capability=clean_cap,
                skills=eff_skills,
                json_artifact_path=json_file,
                is_global=(clean_cap is None or clean_cap.lower() in ("general", "universal")),
                auto_commit=auto_commit,
                dry_run=dry_run
            )

        badge = self.format_confirmation_badge(
            item_id, item_kind, statement, clean_cap, scope, agent=clean_agent,
            grad_info=grad_info, track=eff_track
        )
        return {
            "item_id": item_id,
            "item_kind": item_kind,
            "statement": statement,
            "capability": clean_cap,
            "agent": clean_agent,
            "scope": scope,
            "track": eff_track,
            "grad_info": grad_info,
            "badge": badge
        }

    def teach_from_natural_language(
        self,
        text: str,
        default_capability: Optional[str] = None,
        scope: str = "cross-project",
        agent: Optional[str] = None,
        track: str = "auto",
        auto_commit: bool = True,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """Extract category, capability, target agent, and statement from natural language (EN or FA)."""
        raw = text.strip()
        cleaned = re.sub(r"^(remember that|learn this|from now on|note that|یادت باشه|به یاد داشته باش)[:,\s]+", "", raw, flags=re.I)

        # Check for Track 2 indicators (case-specific, supervisor-specific, dataset-specific)
        is_case_specific = bool(re.search(
            r"\b(items?\s+\d+|dataset\s+[a-z0-9]|variable\s+[a-z0-9]|dr\.\s+[a-z]|university\s+[a-z]|دانشگاه|آیتم‌های|گویه‌های|پرسشنامه|استاد|داده‌های این پروژه)\b",
            raw, re.I
        ))
        eff_track = track
        if track == "auto" and is_case_specific:
            eff_track = "2"

        # 1. Infer Capability
        detected_cap = default_capability
        text_lower = raw.lower()
        if not detected_cap:
            for cap, kw_list in CAPABILITY_KEYWORDS.items():
                if any(kw in text_lower for kw in kw_list):
                    detected_cap = cap
                    break

        # 2. Infer Target Subagent Role
        detected_agent = agent.strip().lower() if agent else None
        if not detected_agent:
            m_agent = re.search(r"(?:for|target agent:?|agent:?)\s+([a-z0-9_-]+)", raw, re.I)
            if m_agent:
                cand = m_agent.group(1).lower()
                if cand in self.km.retriever.AGENT_EQUIVALENCES or cand in [
                    "academic-writer", "statistics-agent", "data-agent", "validation-agent",
                    "methodology-expert", "academic-orchestrator", "research-agent"
                ]:
                    detected_agent = cand
            if not detected_agent:
                fa_map = {"نویسنده": "academic-writer", "آمار": "statistics-agent", "داده": "data-agent", "داور": "validation-agent"}
                for kw, ag in fa_map.items():
                    if kw in raw or ag in text_lower:
                        detected_agent = ag
                        break

        # 3. Infer Category
        is_anti_pattern = bool(re.search(r"\b(never|avoid|don't|do not|prohibit|prohibited|نباید|پرهیز|اجتناب|غلط است|اشتباه است)\b", raw, re.I))
        is_pattern = bool(re.search(r"\b(workflow|process|steps|pipeline|sequence|مراحل|فرآیند|گام|چرخه)\b", raw, re.I))
        is_principle = bool(re.search(r"\b(always|must|mandatory|invariant|rule|principle|همیشه|باید|الزامی|اصل|قانون)\b", raw, re.I))

        if is_anti_pattern:
            cat = "anti_pattern"
            rem_m = re.split(r"\b(instead|use|approved remedy|در عوض|به جای آن|استفاده کنید)\b", cleaned, maxsplit=1, flags=re.I)
            if len(rem_m) >= 3:
                defective, remedy = rem_m[0].strip(), rem_m[2].strip()
            else:
                defective, remedy = cleaned, f"Avoid {cleaned}"
            return self.teach(
                category=cat, statement=cleaned, rationale="Direct mentorship guidance from research supervisor.",
                capability=detected_cap, scope=scope, agent=detected_agent,
                defective_pattern=defective, corrective_remedy=remedy,
                track=eff_track, auto_commit=auto_commit, dry_run=dry_run
            )
        elif is_pattern:
            cat = "pattern"
        elif is_principle:
            cat = "principle"
        else:
            cat = "lesson"

        return self.teach(
            category=cat, statement=cleaned, rationale="Direct mentorship guidance from research supervisor.",
            capability=detected_cap, scope=scope, agent=detected_agent,
            track=eff_track, auto_commit=auto_commit, dry_run=dry_run
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
        scope: str,
        agent: Optional[str] = None,
        grad_info: Optional[Dict[str, Any]] = None,
        track: int = 1
    ) -> str:
        """Format clean scholarly confirmation badge for chat and CLI."""
        cap_str = f"`{capability}`" if capability else "General Academic"
        agent_line = f"- **Target Agent**: `{agent}`\n" if agent else ""
        track_str = "Track 1: Immediate Invariant Graduation Active" if track == 1 else "Track 2: Scoped Episodic Memory Stored"
        badge = (
            f"✅ **Knowledge Codified & Persisted**:\n"
            f"- **Protocol**: `{track_str}`\n"
            f"- **ID**: `{item_id}` ({item_kind})\n"
            f"- **Scope**: `{scope}` (Shared Learning Active)\n"
            f"- **Target Capability**: {cap_str}\n"
            f"{agent_line}"
            f"- **Instruction**: \"{statement}\""
        )
        if grad_info and grad_info.get("all_passed"):
            targets = grad_info.get("targets", [])
            target_names = [os.path.basename(os.path.dirname(t)) or os.path.basename(t) for t in targets]
            targets_str = ", ".join(f"`{t}`" for t in target_names) or "`rules/AGENTS.md`"
            git_info = grad_info.get("git", {})
            commit_str = git_info.get("commit_hash", "local")
            pushed_str = " & Pushed to remote" if git_info.get("pushed") else ""
            badge += (
                f"\n\n🚀 **Track 1 Full Graduation Applied (The Hands)**:\n"
                f"- **Compiled Targets**: {targets_str}\n"
                f"- **Directive 18 Size Guard**: ✅ Verified (< 500 lines / 40 KB)\n"
                f"- **Git Lifecycle**: ✅ Committed (`{commit_str}`){pushed_str}"
            )
        elif grad_info and not grad_info.get("all_passed"):
            badge += "\n\n⚠️ **Track 1 Graduation Overflow**: Rolled back due to Directive 18 ceiling; retained in JSON store."
        return badge


def main():
    parser = argparse.ArgumentParser(description="AcademicSuite Proactive Human Mentorship CLI")
    subparsers = parser.add_subparsers(dest="subcommand")

    # teach
    p_teach = subparsers.add_parser("teach", help="Teach a new rule or procedure")
    p_teach.add_argument("--category", choices=["principle", "pattern", "anti_pattern", "lesson"], default="principle")
    p_teach.add_argument("--statement", required=True, help="Instruction or rule statement")
    p_teach.add_argument("--rationale", help="Reasoning or empirical justification")
    p_teach.add_argument("--capability", help="Target capability (e.g. mediation, sem, chapter4)")
    p_teach.add_argument("--agent", help="Target subagent role (e.g. academic-writer, statistics-agent, data-agent)")
    p_teach.add_argument("--scope", default="cross-project", help="Scope containment (default: cross-project)")
    p_teach.add_argument("--skills", nargs="*", help="Target skills")
    p_teach.add_argument("--tags", nargs="*", help="Tags")
    p_teach.add_argument("--track", choices=["auto", "1", "2"], default="auto", help="Dual-track ingestion mode")
    p_teach.add_argument("--dry-run", action="store_true", help="Simulate without writing or committing")
    p_teach.add_argument("--no-git", action="store_true", help="Skip git commit/push")

    # ingest-text
    p_ingest = subparsers.add_parser("ingest-text", help="Parse and learn from natural language text")
    p_ingest.add_argument("text", help="Natural language instruction (EN or FA)")
    p_ingest.add_argument("--capability", help="Default capability if not in text")
    p_ingest.add_argument("--agent", help="Explicit target agent override")
    p_ingest.add_argument("--scope", default="cross-project", help="Scope containment")
    p_ingest.add_argument("--track", choices=["auto", "1", "2"], default="auto", help="Dual-track ingestion mode")
    p_ingest.add_argument("--dry-run", action="store_true", help="Simulate without writing or committing")
    p_ingest.add_argument("--no-git", action="store_true", help="Skip git commit/push")

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
            scope=args.scope,
            agent=args.agent,
            track=args.track,
            auto_commit=not args.no_git,
            dry_run=args.dry_run
        )
        print(res["badge"])

    elif args.subcommand == "ingest-text":
        res = mentor.teach_from_natural_language(
            text=args.text,
            default_capability=args.capability,
            scope=args.scope,
            agent=args.agent,
            track=args.track,
            auto_commit=not args.no_git,
            dry_run=args.dry_run
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
