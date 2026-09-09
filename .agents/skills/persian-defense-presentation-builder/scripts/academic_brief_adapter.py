#!/usr/bin/env python3
"""
academic_brief_adapter.py — Academic Defense Presentation Adapter for slide-creator

Adapts academic research artifacts (thesis metadata, statistical analysis results,
sample defense payloads, and oral defense speaker notes) into a valid BRIEF.json
contract compliant with kaisersong/slide-creator's generation-brief.schema.json.

Preserves:
  - 100% of candidate oral defense speaker notes (data-notes)
  - Examination committee roles & affiliations
  - Problem statement inverted-funnel stages
  - Conceptual frameworks & SEM path models
  - APA 7th Edition statistical tables & effect sizes
  - Directional hypothesis verification matrices (accepted / rejected badges)
  - Theoretical discussion mechanisms & clinical implications
"""

import json
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional


def load_academic_payload(path: Path) -> Dict[str, Any]:
    """Loads an academic presentation JSON payload or stats_results.json."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def adapt_academic_payload_to_brief(
    payload: Dict[str, Any],
    preset: str = "Academic Defense",
    language: str = "fa",
) -> Dict[str, Any]:
    """
    Transforms an academic defense payload (meta + slides) into a strictly valid BRIEF.json.
    """
    meta = payload.get("meta", {})
    slides_raw = payload.get("slides", [])

    title = meta.get("title") or "جلسه دفاع از رساله دکتری / پایان‌نامه کارشناسی ارشد"
    author = meta.get("author", "پژوهشگر")
    degree = meta.get("degree", "پایان‌نامه دوره تحصیلات تکمیلی")
    university = meta.get("university", "دانشگاه")
    supervisor = meta.get("supervisor", "استاد راهنما")

    # Map preset name
    normalized_preset = preset
    if preset in ["academic_navy", "academic-navy", "academic_defense", "academic-defense"]:
        normalized_preset = "Academic Defense"

    brief_id = f"defense-{uuid.uuid4().hex[:8]}"

    brief_slides = []
    page_roles = []

    for i, slide in enumerate(slides_raw):
        s_num = i + 1
        s_title = slide.get("title") or f"اسلاید {s_num}"
        layout = slide.get("layout", "content")
        notes = slide.get("speaker_notes", "")

        # Precise role & layout mapping for academic defense
        if layout == "cover" or s_num == 1:
            role = "cover"
            layout_id = "defense_cover"
            preferred_family = "hero"
            visual = "academic thesis hero cover"
            visual_intent = "authoritative academic title card with university crest"
        elif layout == "committee":
            role = "committee"
            layout_id = "defense_committee"
            preferred_family = "team"
            visual = "examination committee matrix"
            visual_intent = "committee roster with supervisory and examiner roles"
        elif layout in ["problem_funnel", "problem"]:
            role = "problem"
            layout_id = "defense_problem"
            preferred_family = "flow"
            visual = "inverted problem funnel"
            visual_intent = "stepped funnel from global burden to target research gap"
        elif layout == "gap_matrix":
            role = "gap"
            layout_id = "defense_gap"
            preferred_family = "comparison"
            visual = "empirical gap matrix"
            visual_intent = "three-tier research gap and innovation matrix"
        elif layout == "big_idea":
            role = "callout"
            layout_id = "defense_callout"
            preferred_family = "callout"
            visual = "core thesis premise"
            visual_intent = "central research proposition and theoretical claim"
        elif layout == "section_divider":
            role = "divider"
            layout_id = "defense_divider"
            preferred_family = "divider"
            visual = "chapter transition divider"
            visual_intent = "clean academic chapter roadmap divider"
        elif layout == "conceptual_model":
            role = "framework"
            layout_id = "defense_framework"
            preferred_family = "process"
            visual = "theoretical framework and variable pathways"
            visual_intent = "hexaflex or SEM conceptual interaction model"
        elif layout in ["research_design", "sample_flow"]:
            role = "methodology"
            layout_id = "defense_methodology"
            preferred_family = "process"
            visual = "CONSORT trial methodology and participant flow"
            visual_intent = "rigorous experimental design flow and G*Power justification"
        elif layout == "intervention_timeline":
            role = "intervention"
            layout_id = "defense_intervention"
            preferred_family = "timeline"
            visual = "intervention protocol roadmap"
            visual_intent = "session-by-session clinical protocol progression"
        elif layout == "stat_table":
            # Differentiate consecutive tables to prevent layout stagnation
            sec = str(slide.get("section", ""))
            tit = str(s_title)
            if "روش" in sec or "ابزار" in tit:
                role = "instruments"
                layout_id = "defense_instruments"
                preferred_family = "evidence"
                visual = "psychometric instrument validation table"
                visual_intent = "scale specifications, item counts, and Cronbach alpha"
            elif "توصیفی" in tit:
                role = "descriptive"
                layout_id = "defense_descriptive"
                preferred_family = "evidence"
                visual = "descriptive statistics summary table"
                visual_intent = "pre-test, post-test, and follow-up mean and SD matrix"
            elif "مانکوا" in tit or "کوواریانس" in tit:
                role = "table"
                layout_id = "defense_table"
                preferred_family = "evidence"
                visual = "inferential MANCOVA APA 7 table"
                visual_intent = "degrees of freedom, F statistics, p-values, and partial eta squared"
            else:
                role = "table_alt"
                layout_id = "defense_table_alt"
                preferred_family = "evidence"
                visual = "statistical hypothesis test table"
                visual_intent = "multivariate statistics and effect size documentation"
        elif layout == "result_spotlight":
            role = "spotlight"
            layout_id = "defense_spotlight"
            preferred_family = "stat"
            visual = "hero statistical finding"
            visual_intent = "focal hypothesis test statistic and clinical effect size"
        elif layout == "hypothesis_matrix":
            role = "verification"
            layout_id = "defense_matrix"
            preferred_family = "evidence"
            visual = "hypothesis outcome matrix"
            visual_intent = "verdict badges for all research hypotheses"
        elif layout == "discussion_mechanism":
            role = "discussion"
            layout_id = "defense_discussion"
            preferred_family = "comparison"
            visual = "psychological mechanism synthesis"
            visual_intent = "theoretical mechanisms underpinning statistical findings"
        elif layout == "two_column":
            role = "comparison"
            layout_id = "defense_split"
            preferred_family = "comparison"
            visual = "bilingual or comparative empirical literature"
            visual_intent = "alignment with international and domestic literature"
        elif layout == "implications":
            role = "implications"
            layout_id = "defense_implications"
            preferred_family = "cards"
            visual = "clinical and translational implications"
            visual_intent = "practical applications in clinical psychology and healthcare"
        elif layout == "limitations":
            role = "limitations"
            layout_id = "defense_limitations"
            preferred_family = "cards"
            visual = "methodological limitations and directions"
            visual_intent = "threats to internal/external validity and future research"
        elif layout == "closing" or s_num == len(slides_raw):
            role = "closing"
            layout_id = "defense_closing"
            preferred_family = "close"
            visual = "academic defense closing and Q&A"
            visual_intent = "authoritative academic close and jury Q&A invitation"
        else:
            role = "content"
            layout_id = "defense_cards"
            preferred_family = "cards"
            visual = "structured academic content"
            visual_intent = "card grid with scientific evidence"

        page_roles.append(role)

        # Supporting facts / bullet distillation
        supporting_facts = []
        if "stages" in slide:
            for st in slide["stages"]:
                supporting_facts.append(f"{st.get('title', '')}: {st.get('desc', '')}")
        elif "members" in slide:
            for m in slide["members"]:
                supporting_facts.append(f"{m.get('role', '')}: {m.get('name', '')}")
        elif "columns" in slide:
            for col in slide["columns"]:
                col_items = ", ".join(col.get("items", []))
                supporting_facts.append(f"{col.get('title', '')}: {col_items}")
        elif "hypotheses" in slide:
            for h in slide["hypotheses"]:
                supporting_facts.append(f"{h.get('statement', '')} -> {h.get('status', '')}")
        elif "rows" in slide:
            for row in slide["rows"][:4]:
                if isinstance(row, list):
                    supporting_facts.append(" | ".join(str(c) for c in row[:3]))

        # Include meta in slide 1
        slide_academic_data = dict(slide)
        if s_num == 1:
            slide_academic_data["meta"] = meta

        slide_entry = {
            "slide_number": s_num,
            "role": role,
            "title": s_title,
            "key_point": slide.get("subtitle") or slide.get("section") or s_title,
            "visual": visual,
            "claim": s_title,
            "explanation": notes[:250] if notes else s_title,
            "visual_intent": visual_intent,
            "preferred_layout_family": preferred_family,
            "supporting_facts": supporting_facts[:5] if supporting_facts else [s_title],
            "notes": notes,
            "speaker_note": notes,
            "layout": layout_id,
            "academic_data": slide_academic_data,
        }
        brief_slides.append(slide_entry)

    page_count = len(brief_slides)

    brief = {
        "schema_version": 1,
        "brief_id": brief_id,
        "mode": "auto",
        "language": language,
        "title": title,
        "audience": "هیئت محترم داوران، استادان راهنما و مشاور، و پژوهشگران تحصیلات تکمیلی",
        "desired_action": "دفاع موفق، پاسخگویی به پرسش‌های داوران، و اخذ درجه عالی در جلسه دفاع",
        "deck": {
            "deck_type": "user-content",
            "page_count": page_count,
            "output_format": "html-slides",
        },
        "style": {
            "preset": normalized_preset,
            "tone": "آکادمیک، مستدل، فاخر و منطبق بر هنجارهای دفاع پایان‌نامه و رساله دکتری",
            "visual_density": "medium",
        },
        "content": {
            "source_policy": "distill-only",
            "must_include": [
                f"عنوان رساله: {title}",
                f"پژوهشگر: {author}",
                f"استاد راهنما: {supervisor}",
                "یافته‌های آماری دقیق و ضرایب اثر",
                "وضعیت فرضیه‌ها و تبیین نظری",
            ],
            "must_avoid": [
                "متون طولانی و خسته‌کننده کتابی",
                "ادعاهای بدون استناد آماری",
                "به‌کارگیری رنگ‌های غیرعلمی و ناموزون",
            ],
            "global_facts": [
                f"دانشگاه: {university} - مقطع: {degree}",
                "فرضیه‌ها با آزمون‌های استنباطی متناسب تحلیل شده‌اند",
                "تمام اسلایدها واجد یادداشت‌های شفاهی ارائه (Speaker Notes) هستند",
            ],
            "optional_support": [
                "پشتیبانی از حالت ارائه Presenter Mode با کلید P یا F5",
                "ویرایش زنده متن در مرورگر با کلید E",
                "قابلیت چاپ و خروجی مستقیم به PDF و PPTX",
            ],
        },
        "narrative": {
            "thesis": f"دفاع مستدل و آکادمیک از رساله «{title}» با تکیه بر شواهد تجربی و مبانی نظری معتبر.",
            "page_roles": page_roles,
            "slides": brief_slides,
        },
        "runtime": {
            "editing_mode": True,
            "presenter_mode": True,
            "watermark_mode": "injected-last-slide",
            "export_intent": "none",
        },
        "plan_view": {
            "emit_planning_view": False,
            "planning_view_path": "PLANNING.md",
        },
        "timing": {
            "estimate": {
                "plan": "1 min",
                "generate": "1 min",
                "validate": "<1 min",
                "polish": "0 min",
                "total": "2 min",
            },
            "actual": {
                "plan": "0m 00s",
                "generate": "0m 00s",
                "validate": "0m 00s",
                "polish": "0m 00s",
                "total": "0m 00s",
            },
        },
        "notes": f"ارائه دفاع رساله: {author} ({university})"[:400],
    }

    return brief


def convert_academic_json_file_to_brief(
    input_path: Path,
    output_path: Optional[Path] = None,
    preset: str = "Academic Defense",
    language: str = "fa",
) -> Path:
    """Reads an academic JSON file and writes out a compliant BRIEF.json."""
    payload = load_academic_payload(input_path)
    brief = adapt_academic_payload_to_brief(payload, preset=preset, language=language)

    if output_path is None:
        output_path = input_path.with_name("BRIEF.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(brief, f, ensure_ascii=False, indent=2)

    return output_path


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Academic Payload to BRIEF.json Adapter")
    parser.add_argument("input", type=Path, help="Path to academic payload JSON")
    parser.add_argument("-o", "--output", type=Path, default=None, help="Output BRIEF.json path")
    parser.add_argument("--preset", default="Academic Defense", help="Design preset name")
    parser.add_argument("--lang", default="fa", help="Language code (fa/en)")
    args = parser.parse_args()

    out = convert_academic_json_file_to_brief(args.input, args.output, preset=args.preset, language=args.lang)
    print(f"Successfully adapted {args.input} to {out}")
