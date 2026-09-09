#!/usr/bin/env python3
"""
Master Persian Academic Thesis Defense Presentation Builder v3.5
================================================================
Unified CLI supporting both browser-grade HTML presentations (slide-creator)
and native Microsoft PowerPoint (.pptx) presentations with:
  - 100% Pure Python Microsoft Office Math (OMML) equation injection
  - 300-DPI theme-adaptive diagram engine (Mediation, CONSORT, Timeline)
  - Geometric bounding box & overlap collision auditor
  - Template context & asset extractor (pptx-skills)
  - Ghost Deck Action-Title academic narrative synthesis (academic-pptx-skill)
  - Automated 100-point defense QA gate
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

# Slide-creator HTML engine
from low_context import (  # noqa: E402
    BriefExtractionError,
    BriefValidationError,
    RenderError,
    load_brief,
    render_from_brief,
    render_from_context_path,
    stamp_validation_status,
    validate_brief_path,
)
from generation_eval import (  # noqa: E402
    build_generation_eval_report,
    default_eval_output_path,
    write_generation_eval_report,
)

# Native PPTX & Analysis engines
from compile_defense_presentation import compile_presentation  # noqa: E402
from presentation_schema import ProjectMeta, ResearchTruthModel  # noqa: E402
from content_planner import synthesize_storyboard_from_truth_model  # noqa: E402
from extract_template import extract_template  # noqa: E402
from check_overlaps import audit_presentation  # noqa: E402
from render_diagrams import render_diagram  # noqa: E402
from academic_brief_adapter import adapt_academic_payload_to_brief  # noqa: E402

PLAN_HELP = """\
PLAN STEP REQUIRES SKILL INVOCATION

`/slide-creator --plan` is a Claude/OpenClaw slash-skill step, not a raw bash/python command.

In a bare sandbox:
1. Read `references/brief-template.json`
2. Write `BRIEF.json` yourself (or extract one valid BRIEF from context)
3. Run `python3 main.py --validate-brief --brief BRIEF.json`
4. Run `python3 main.py --generate --brief BRIEF.json --output presentation.html`

To generate native PowerPoint (.pptx):
1. Prepare structured payload or stats_results.json
2. Run `python3 main.py --compile-pptx --json payload.json --output presentation.pptx`
"""


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Master Persian Academic Defense Presentation Builder v3.5 (HTML & PPTX)"
    )
    mode = parser.add_mutually_exclusive_group(required=True)
    
    # HTML slide-creator modes
    mode.add_argument(
        "--plan",
        nargs="*",
        metavar="PROMPT",
        help="Explain the planning-step fallback in a raw sandbox",
    )
    mode.add_argument(
        "--generate",
        action="store_true",
        help="Render HTML from BRIEF.json or a context artifact",
    )
    mode.add_argument(
        "--validate-brief",
        action="store_true",
        help="Validate a BRIEF.json artifact",
    )
    
    # Native PPTX & Tool modes
    mode.add_argument(
        "--compile-pptx",
        action="store_true",
        help="Compile native PowerPoint (.pptx) deck with diagrams, OMML math, and QA",
    )
    mode.add_argument(
        "--extract-template",
        type=str,
        metavar="TEMPLATE_PPTX",
        help="Extract context.json, layout metrics, fonts, colors, and images from PPTX template",
    )
    mode.add_argument(
        "--audit-pptx",
        type=str,
        metavar="PPTX_FILE",
        help="Audit PPTX for element overlaps, boundary overflow, and vertical gaps",
    )
    mode.add_argument(
        "--render-diagram",
        type=str,
        metavar="SPEC_JSON",
        help="Render 300-DPI theme-adaptive diagram (mediation, CONSORT, timeline) to an image",
    )
    mode.add_argument(
        "--adapt-brief",
        action="store_true",
        help="Convert academic defense payload / stats JSON to slide-creator BRIEF.json",
    )

    # General / Shared parameters
    parser.add_argument("--brief", help="Path to BRIEF.json (defaults to ./BRIEF.json)")
    parser.add_argument("--context-file", help="Path to a context artifact containing exactly one valid BRIEF")
    parser.add_argument("--output", help="Output path (HTML, PPTX, PNG diagram, or adapted BRIEF.json)")
    parser.add_argument("--json", help="Path to input JSON payload (for --compile-pptx or --adapt-brief)")
    parser.add_argument(
        "--theme",
        default="academic_navy",
        choices=["academic_navy", "academic_dark", "emerald_slate", "royal_burgundy", "persian_teal_rose", "tehran_classic_azure"],
        help="Color theme for PPTX, HTML, and diagrams (default: academic_navy)",
    )
    parser.add_argument(
        "--theme-file",
        help="Path to custom theme JSON file (e.g. from extracted_themes/themes/*.json)",
    )

    # Template Extraction & Geometry Audit options
    parser.add_argument(
        "--template-out",
        default="extracted_template",
        help="Output directory for --extract-template (default: ./extracted_template)",
    )
    parser.add_argument("--audit-json", help="Optional path to write JSON report for --audit-pptx")
    parser.add_argument("--min-overlap", type=float, default=0.02, help="Min overlap area in sq.in for --audit-pptx")
    parser.add_argument("--min-gap", type=float, default=0.04, help="Min vertical gap in inches for --audit-pptx")

    # HTML Eval & Packet options
    parser.add_argument("--eval", action="store_true", help="Write a single-deck eval JSON next to the output HTML")
    parser.add_argument("--eval-out", help="Optional path for the single-deck eval JSON report")
    parser.add_argument("--packet-out", help="Optional path to write the render packet as JSON")
    parser.add_argument("--extract-brief-out", help="Optional path to write the extracted BRIEF as JSON")

    # Direct PPTX Synthesis inputs
    parser.add_argument("--stats-json", help="Path to statistical results JSON for direct synthesis")
    parser.add_argument("--ch1", help="Path to Chapter 1 DOCX")
    parser.add_argument("--ch3", help="Path to Chapter 3 DOCX")
    parser.add_argument("--ch5", help="Path to Chapter 5 DOCX")
    parser.add_argument("--skip-qa", action="store_true", help="Skip automated QA validation during compilation")
    parser.add_argument("--preview", action="store_true", help="Generate PDF / visual preview of presentation")

    return parser


def _default_brief_path(value: str | None) -> Path:
    return Path(value) if value else Path("BRIEF.json")


def run_plan(prompt_parts: list[str] | None) -> int:
    print(PLAN_HELP)
    if prompt_parts:
        print("PROMPT:")
        print(" ".join(prompt_parts))
    return 2


def run_validate_brief(brief_path: Path) -> int:
    is_valid, errors, _brief = validate_brief_path(brief_path)
    if is_valid:
        print(f"VALID: {brief_path.name}")
        return 0

    print(f"INVALID: {brief_path.name}")
    for error in errors:
        print(f"- {error}")
    return 1


def run_generate(
    *,
    brief_path: Path | None,
    context_file: str | None,
    output: Path,
    eval_enabled: bool = False,
    eval_out: str | None = None,
    packet_out: str | None = None,
    extract_brief_out: str | None = None,
    theme: str | None = None,
) -> int:
    def _has_canonical_provenance(html_text: str) -> bool:
        required_markers = (
            'data-generator="kai-slide-creator"',
            'data-generator-version="',
            'data-render-path="',
            'data-brief-hash="',
            'data-runtime-path="',
            'data-validate-strict="pending"',
        )
        return all(marker in html_text for marker in required_markers)

    def _strict_validate_rendered_html(html_text: str) -> bool:
        from validate_html import validate  # noqa: WPS433

        with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as handle:
            handle.write(html_text)
            tmp_path = Path(handle.name)

        try:
            return validate(tmp_path, strict=True)
        finally:
            tmp_path.unlink(missing_ok=True)

    try:
        if context_file:
            brief, html_text, packet, _style_contract = render_from_context_path(context_file)
        else:
            if brief_path is None:
                raise BriefValidationError("A BRIEF path or --context-file is required")
            brief = load_brief(brief_path)
            if theme:
                brief.setdefault("style", {})["theme"] = theme
            html_text, packet, _style_contract = render_from_brief(brief)
    except (BriefExtractionError, BriefValidationError) as exc:
        print(f"BRIEF ERROR: {exc}")
        return 1
    except RenderError as exc:
        print(f"RENDER ERROR: {exc}")
        if exc.payload:
            print("RENDER ERROR PAYLOAD:")
            print(json.dumps(exc.payload, ensure_ascii=False, indent=2))
        return 1

    if not _has_canonical_provenance(html_text):
        print("PROVENANCE ERROR: canonical render markers missing; refusing to write output")
        return 1

    if not _strict_validate_rendered_html(html_text):
        print("VALIDATE ERROR: strict pre-write gate failed; refusing to write output")
        return 1

    final_html = stamp_validation_status(html_text, status="pass")
    output.write_text(final_html, encoding="utf-8")

    if packet_out:
        Path(packet_out).write_text(json.dumps(packet, ensure_ascii=False, indent=2), encoding="utf-8")

    if extract_brief_out:
        Path(extract_brief_out).write_text(json.dumps(brief, ensure_ascii=False, indent=2), encoding="utf-8")

    eval_path: Path | None = None
    if eval_enabled or eval_out:
        eval_path = Path(eval_out) if eval_out else default_eval_output_path(output)
        report = build_generation_eval_report(
            html_text=final_html,
            brief=brief,
            packet=packet,
            html_path=output,
        )
        write_generation_eval_report(eval_path, report)

    print(f"RENDERED: {output}")
    print(f"PRESET: {packet['preset']}")
    print(f"QUALITY TIER: {packet['quality_tier']}")
    print(f"RUNTIME PATH: {packet['runtime_path']}")
    if eval_path is not None:
        print(f"EVAL: {eval_path}")
        print(f"STYLE SCORE: {report['summary']['style_score']}")
    return 0


def run_compile_pptx(args) -> int:
    output_path = args.output or "Defense_Presentation.pptx"
    payload = None

    if args.json:
        if not os.path.exists(args.json):
            print(f"[!] Error: JSON payload file not found: {args.json}", file=sys.stderr)
            return 1
        with open(args.json, "r", encoding="utf-8") as f:
            payload = json.load(f)
    elif args.stats_json:
        print("[*] Synthesizing presentation payload from research source files...")
        meta_obj = ProjectMeta(
            title=getattr(args, "title", None) or "عنوان رساله / پایان‌نامه",
            degree=getattr(args, "degree", None) or "پایان‌نامه کارشناسی ارشد / رساله دکتری",
            university=getattr(args, "university", None) or "",
            author=getattr(args, "author", None) or "",
            theme=args.theme,
        )
        truth = ResearchTruthModel(meta=meta_obj)
        payload = synthesize_storyboard_from_truth_model(truth)
    else:
        print("[!] Error: Either --json <payload.json> or --stats-json <stats.json> is required.", file=sys.stderr)
        return 1

    theme_to_use = args.theme_file if getattr(args, "theme_file", None) else args.theme
    success = compile_presentation(
        payload=payload,
        output_path=output_path,
        theme_name=theme_to_use,
        run_qa=not args.skip_qa,
        preview=args.preview,
    )
    return 0 if success else 1


def run_extract_template(template_pptx: str, out_dir: str) -> int:
    try:
        res = extract_template(template_pptx, out_dir)
        slides_count = len(res.get("slides", []))
        layouts_count = len(res.get("slide_layouts", []))
        images_count = len(res.get("images_manifest", []))
        print(f"[SUCCESS] Template extracted to: {out_dir}")
        print(f"  - Slides extracted: {slides_count}")
        print(f"  - Layout families: {layouts_count}")
        print(f"  - Images saved: {images_count}")
        print(f"  - Context JSON: {os.path.join(out_dir, 'context.json')}")
        return 0
    except Exception as e:
        print(f"[!] Template extraction error: {e}", file=sys.stderr)
        return 1


def run_audit_pptx(pptx_path: str, json_out: str | None, min_overlap: float, min_gap: float) -> int:
    try:
        passed, issues, summary = audit_presentation(
            pptx_path, min_overlap=min_overlap, min_gap=min_gap
        )
        print(f"[*] Audited {summary['slide_count']} slides ({summary['dimensions']['width']:.2f}\" x {summary['dimensions']['height']:.2f}\")")
        print(f"[*] Geometry Audit Result: {summary['status']} (Critical: {summary['critical_issues']}, Major: {summary['major_issues']})")

        if issues:
            print("\nDetected Issues:")
            for iss in issues[:15]:
                print(f"  - [Slide {iss.slide}] [{iss.severity}] {iss.kind}: {iss.message}")
            if len(issues) > 15:
                print(f"  ... and {len(issues) - 15} more issues.")

        if json_out:
            report_data = {
                "summary": summary,
                "issues": [
                    {
                        "slide": i.slide,
                        "severity": i.severity,
                        "kind": i.kind,
                        "message": i.message,
                        "details": i.details,
                    }
                    for i in issues
                ],
            }
            with open(json_out, "w", encoding="utf-8") as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)
            print(f"[*] Detailed JSON report written to: {json_out}")

        return 0 if passed else 1
    except Exception as e:
        print(f"[!] Overlap audit error: {e}", file=sys.stderr)
        return 1


def run_render_diagram(spec_path: str, output_path: str | None, theme_name: str) -> int:
    try:
        if not os.path.exists(spec_path):
            print(f"[!] Error: Diagram spec file not found: {spec_path}", file=sys.stderr)
            return 1
        with open(spec_path, "r", encoding="utf-8") as f:
            spec = json.load(f)

        out_img = output_path or "academic_diagram.png"
        render_diagram(spec, out_img, theme_name=theme_name)
        print(f"[SUCCESS] 300-DPI diagram rendered to: {out_img}")
        return 0
    except Exception as e:
        print(f"[!] Diagram rendering error: {e}", file=sys.stderr)
        return 1


def run_adapt_brief(args) -> int:
    if not args.json:
        print("[!] Error: --json <payload.json> is required with --adapt-brief", file=sys.stderr)
        return 1

    try:
        with open(args.json, "r", encoding="utf-8") as f:
            payload = json.load(f)

        brief = adapt_academic_payload_to_brief(payload, preset="academic_defense", theme=args.theme)
        out_path = args.output or "BRIEF.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(brief, f, ensure_ascii=False, indent=2)

        slide_count = len(brief.get("narrative", {}).get("slides", []))
        print(f"[SUCCESS] Adapted academic payload to BRIEF: {out_path}")
        print(f"  - Slides: {slide_count}")
        print(f"  - Action titles enforced with Ghost Deck methodology")
        return 0
    except Exception as e:
        print(f"[!] Brief adaptation error: {e}", file=sys.stderr)
        return 1


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    # 1. Planning mode
    if args.plan is not None:
        return run_plan(args.plan)

    # 2. BRIEF Validation
    if args.validate_brief:
        brief_path = _default_brief_path(args.brief)
        return run_validate_brief(brief_path)

    # 3. HTML Generation (slide-creator)
    if args.generate:
        if not args.output:
            parser.error("--output is required with --generate")
        brief_path = _default_brief_path(args.brief)
        return run_generate(
            brief_path=None if args.context_file else brief_path,
            context_file=args.context_file,
            output=Path(args.output),
            eval_enabled=args.eval,
            eval_out=args.eval_out,
            packet_out=args.packet_out,
            extract_brief_out=args.extract_brief_out,
            theme=args.theme,
        )

    # 4. Native PPTX Compilation
    if args.compile_pptx:
        return run_compile_pptx(args)

    # 5. Template Extraction
    if args.extract_template:
        return run_extract_template(args.extract_template, args.template_out)

    # 6. PPTX Geometry & Overlap Audit
    if args.audit_pptx:
        return run_audit_pptx(
            args.audit_pptx,
            args.audit_json,
            args.min_overlap,
            args.min_gap,
        )

    # 7. 300-DPI Diagram Rendering
    if args.render_diagram:
        return run_render_diagram(args.render_diagram, args.output, args.theme)

    # 8. Adapt Academic Payload to BRIEF.json
    if args.adapt_brief:
        return run_adapt_brief(args)

    parser.error("No valid action specified.")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
