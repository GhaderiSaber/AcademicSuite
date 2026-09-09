#!/usr/bin/env python3
"""
Master Persian Academic Thesis Defense Presentation Compiler v3.0.0
===================================================================
Repository: GhaderiSaber/AcademicSuite
Skill: persian-defense-presentation-builder

Compiles publication-grade, defense-ready PowerPoint presentations (.pptx)
for Iranian Master's and PhD candidates strictly adhering to v3 standards:
- Prime Directive: Source -> Research Truth Model -> Storyboard -> Encodings -> PPTX -> Visual QA.
- Rule 1.3: Generic card layouts strictly <= 25% of content slides.
- Rule 1.4: Never use the same layout family twice in a row; dominance <= 30%.
- Rule 1.5: Strict defense legibility (>= 20 pt Persian body text; 28–36 pt titles; 34–52 pt KPI heroes).
- Native Right-to-Left (RTL) OpenXML DrawingML formatting.
- Dynamic project metadata with zero hardcoded student or university strings.
- Automated QA validation gates with 100-point quality rubric (zero silent sample fallback).
- Full candidate oral defense Speaker Notes on 100% of slides.
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Any, Optional

if sys.stdout.encoding != "utf-8":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from pptx import Presentation
from pptx.util import Inches

from presentation_schema import (
    PALETTES,
    validate_presentation_payload,
    ResearchTruthModel,
    ProjectMeta
)
from content_planner import synthesize_storyboard_from_truth_model
from layout_engine import (
    build_cover_slide,
    build_committee_slide,
    build_section_divider_slide,
    build_problem_funnel_slide,
    build_big_idea_slide,
    build_two_column_slide,
    build_comparison_slide,
    build_gap_matrix_slide,
    build_conceptual_model_slide,
    build_research_design_slide,
    build_sample_flow_slide,
    build_instrument_matrix_slide,
    build_intervention_timeline_slide,
    build_result_spotlight_slide,
    build_bar_chart_slide,
    build_dot_plot_slide,
    build_prepost_chart_slide,
    build_table_slide,
    build_hypothesis_matrix_slide,
    build_discussion_mechanism_slide,
    build_implications_slide,
    build_limitations_slide,
    build_recommendations_slide,
    build_closing_slide,
    build_split_diagram_slide,
    build_kpi_dashboard_slide,
    build_cards_slide
)
from qa_validator import run_qa_checks
from render_preview import generate_preview_report

# ---------------------------------------------------------------------------
# Slide Builder Dispatch Table
# ---------------------------------------------------------------------------
LAYOUT_DISPATCH = {
    "cover": build_cover_slide,
    "committee": build_committee_slide,
    "section_divider": build_section_divider_slide,
    "problem_funnel": build_problem_funnel_slide,
    "big_idea": build_big_idea_slide,
    "two_column": build_two_column_slide,
    "comparison": build_comparison_slide,
    "gap_matrix": build_gap_matrix_slide,
    "conceptual_model": build_conceptual_model_slide,
    "research_design": build_research_design_slide,
    "sample_flow": build_sample_flow_slide,
    "instrument_matrix": build_instrument_matrix_slide,
    "intervention_timeline": build_intervention_timeline_slide,
    "result_spotlight": build_result_spotlight_slide,
    "bar_chart": build_bar_chart_slide,
    "dot_plot": build_dot_plot_slide,
    "prepost_chart": build_prepost_chart_slide,
    "stat_table": build_table_slide,
    "table": build_table_slide,
    "hypothesis_matrix": build_hypothesis_matrix_slide,
    "discussion_mechanism": build_discussion_mechanism_slide,
    "implications": build_implications_slide,
    "limitations": build_limitations_slide,
    "recommendations": build_recommendations_slide,
    "closing": build_closing_slide,
    "split_diagram": build_split_diagram_slide,
    "path_diagram": build_split_diagram_slide,
    "mediation_diagram": build_split_diagram_slide,
    "kpi_dashboard": build_kpi_dashboard_slide,
    "kpi_panel": build_kpi_dashboard_slide,
    "timeline": build_intervention_timeline_slide,
    "process_flow": build_research_design_slide,
    "before_after": build_comparison_slide,
    "cards": build_cards_slide
}

def compile_presentation(payload: Dict[str, Any], output_path: str, theme_name: str = "academic_navy", run_qa: bool = True) -> bool:
    """Compiles structured presentation dictionary into high-end publication-grade .pptx file."""
    # Validate payload schema
    schema_errors = validate_presentation_payload(payload)
    if schema_errors:
        print("[!] Payload schema validation failed:", file=sys.stderr)
        for err in schema_errors:
            print(f"    - {err}", file=sys.stderr)
        return False

    prs = Presentation()
    prs.slide_width = Inches(13.333)  # 16:9 Widescreen standard
    prs.slide_height = Inches(7.5)

    palette = PALETTES.get(theme_name, PALETTES["academic_navy"])
    meta = payload.get("meta", {})
    slides = payload.get("slides", [])
    total_slides = len(slides)

    print(f"[*] Compiling {total_slides} defense slides with theme: '{theme_name}' (16:9 Canvas)...")

    for idx, slide_item in enumerate(slides):
        slide_num = idx + 1
        layout = slide_item.get("layout", "cards")
        builder_fn = LAYOUT_DISPATCH.get(layout, build_cards_slide)
        
        # Build slide
        if layout == "cover":
            builder_fn(prs, meta, slide_item, palette)
        else:
            builder_fn(prs, meta, slide_item, palette, slide_num, total_slides)

    out_dir = os.path.dirname(os.path.abspath(output_path))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    prs.save(output_path)
    print(f"[SUCCESS] Presentation successfully written to: {output_path}")

    # Run Automated QA Validator
    if run_qa:
        print("\n[*] Executing Automated Quality Assurance Gate (v3.0.0 Rubric & Quality Gates)...")
        passed, results, report_str, score_summary = run_qa_checks(payload, output_path)
        print(report_str)
        if not passed:
            print(f"[!] WARNING: QA audit resulted in '{score_summary.get('status', 'FAIL')}'. Review the report above.", file=sys.stderr)
            return False

    return True

def main():
    parser = argparse.ArgumentParser(description="Master Persian Academic Thesis Defense Presentation Compiler v3.0.0")
    parser.add_argument("--json", type=str, help="Path to structured presentation payload JSON")
    parser.add_argument("--output", type=str, default="Defense_Presentation.pptx", help="Path to output .pptx file")
    parser.add_argument("--theme", type=str, default="academic_navy", choices=["academic_navy", "emerald_slate", "royal_burgundy"], help="Color theme")
    
    # Metadata Overrides
    parser.add_argument("--title", type=str, help="Thesis title")
    parser.add_argument("--author", type=str, help="Candidate name")
    parser.add_argument("--supervisor", type=str, help="Supervisor name")
    parser.add_argument("--advisor", type=str, help="Advisor name")
    parser.add_argument("--university", type=str, help="University name")
    parser.add_argument("--faculty", type=str, help="Faculty name")
    parser.add_argument("--department", type=str, help="Department name")
    parser.add_argument("--degree", type=str, help="Degree name (e.g. پایان‌نامه کارشناسی ارشد)")
    parser.add_argument("--defense-date", type=str, help="Defense session date")
    
    # Direct Synthesis Inputs
    parser.add_argument("--stats-json", type=str, help="Path to statistical results JSON")
    parser.add_argument("--ch1", type=str, help="Path to Chapter 1 DOCX")
    parser.add_argument("--ch3", type=str, help="Path to Chapter 3 DOCX")
    parser.add_argument("--ch5", type=str, help="Path to Chapter 5 DOCX")
    
    # QA & Preview Controls
    parser.add_argument("--skip-qa", action="store_true", help="Skip automated QA validation")
    parser.add_argument("--preview", action="store_true", help="Generate PDF / visual preview")
    
    args = parser.parse_args()

    payload = None

    # Option 1: Load from JSON
    if args.json:
        if not os.path.exists(args.json):
            print(f"[ERROR] Specified JSON payload file does not exist: {args.json}", file=sys.stderr)
            print("In accordance with Rule 1.7, the compiler will never silently fall back to sample decks.", file=sys.stderr)
            sys.exit(1)
        try:
            with open(args.json, "r", encoding="utf-8") as f:
                payload = json.load(f)
        except Exception as e:
            print(f"[ERROR] Failed to parse JSON payload at {args.json}: {e}", file=sys.stderr)
            sys.exit(1)

    # Option 2: Synthesize from direct arguments or chapters
    elif any([args.title, args.author, args.stats_json, args.ch1, args.ch3, args.ch5]):
        print("[*] Direct synthesis requested. Building Research Truth Model from source parameters...")
        meta_obj = ProjectMeta(
            title=args.title or "عنوان رساله / پایان‌نامه",
            degree=args.degree or "پایان‌نامه کارشناسی ارشد / رساله دکتری",
            university=args.university or "",
            faculty=args.faculty or "",
            department=args.department or "",
            author=args.author or "",
            supervisor=args.supervisor or "",
            advisor=args.advisor or "",
            defense_date=args.defense_date or "",
            theme=args.theme
        )
        truth = ResearchTruthModel(meta=meta_obj)
        payload = synthesize_storyboard_from_truth_model(truth)

    # Missing Input: Strict Non-Zero Exit (Rule 1.7: Zero Silent Fallback)
    else:
        print("[ERROR] No input provided. You must provide either --json <path> or direct synthesis parameters (--title, --author, etc.).", file=sys.stderr)
        print("In accordance with Rule 1.7, the compiler will never silently fall back to sample decks in production.", file=sys.stderr)
        print("Usage:", file=sys.stderr)
        print("  python scripts/compile_defense_presentation.py --json defense_payload.json --output Defense.pptx", file=sys.stderr)
        sys.exit(1)

    # Apply any CLI metadata overrides
    meta = payload.setdefault("meta", {})
    if args.title:
        meta["title"] = args.title
    if args.author:
        meta["author"] = args.author
    if args.supervisor:
        meta["supervisor"] = args.supervisor
    if args.advisor:
        meta["advisor"] = args.advisor
    if args.university:
        meta["university"] = args.university
    if args.faculty:
        meta["faculty"] = args.faculty
    if args.department:
        meta["department"] = args.department
    if args.degree:
        meta["degree"] = args.degree
    if args.defense_date:
        meta["defense_date"] = args.defense_date
    if args.theme:
        meta["theme"] = args.theme

    # Compile presentation
    success = compile_presentation(payload, args.output, args.theme, run_qa=not args.skip_qa)

    # Visual Preview Generation
    if success and args.preview:
        print("\n[*] Generating visual preview...")
        generate_preview_report(args.output)

    if not success:
        sys.exit(2)

if __name__ == "__main__":
    main()
