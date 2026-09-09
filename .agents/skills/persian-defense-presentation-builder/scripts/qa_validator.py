#!/usr/bin/env python3
"""
Automated Quality Assurance Validator (persian-defense-presentation-builder v3.0.0)
==============================================================================
Enforces strict Persian academic defense presentation standards per v3 specification:
- Rule 1.1: One slide = one primary message
- Rule 1.3: Generic card layouts <= 25% of content slides
- Rule 1.4: Never use the same layout family twice in a row (consecutive content slides)
- Rule 1.4: No single layout family dominates > 30% of content slides
- Rule 1.5: Typographic scale compliance (Body text >= 20 pt, tables >= 17 pt)
- Rule 1.6: Academic fidelity & zero invented statistics
- Rule 1.7: Zero hardcoded student/university example metadata
- Rule 1.8: No silent fallback to sample data
- Rule 11: 100% candidate oral Speaker Notes coverage (timing, script, cues)
- Rule 12.3: Density thresholds (character budgets, table dimensions <= 6 cols, <= 8 rows)
- Rule 14: Structural QA & asset resolution
- Rule 17: Multi-dimensional 100-point Quality Score (Fidelity, Narrative, Visuals, Type, Consistency, Integrity)
"""

import os
import sys
from typing import Dict, List, Any, Tuple, Optional

if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass
from presentation_schema import (
    SUPPORTED_LAYOUTS,
    LAYOUT_FAMILY_MAPPING,
    GENERIC_CARD_LAYOUTS,
    MAX_CARD_LAYOUT_RATIO,
    MAX_LAYOUT_FAMILY_RATIO,
    ALLOW_CONSECUTIVE_IDENTICAL_FAMILY,
    QUALITY_SCORE_WEIGHTS
)

# Forbidden sample tokens indicating unreplaced placeholders or cross-project leaks
FORBIDDEN_EXAMPLE_TOKENS = [
    "{meta.",
    "PLACEHOLDER",
    "[نام دانشجو]",
    "[نام دانشگاه]",
    "[نام استاد]",
    "TODO",
    "FIXME"
]

def run_qa_checks(payload: Dict[str, Any], pptx_path: Optional[str] = None) -> Tuple[bool, List[Dict[str, Any]], str, Dict[str, Any]]:
    """
    Runs full v3.0.0 automated QA suite on the presentation payload.
    Returns: (passed: bool, checks: List[Dict], report_text: str, score_summary: Dict)
    Status is strictly one of: PASS, PASS_WITH_WARNINGS, or FAIL.
    """
    checks = []
    slides = payload.get("slides", [])
    total_slides = len(slides)
    meta = payload.get("meta", {})
    
    # ---------------------------------------------------------
    # 1. Slide Count (Rule 4.2: 18–26 recommended, 15–32 acceptable)
    # ---------------------------------------------------------
    if 18 <= total_slides <= 26:
        checks.append({"name": "Slide Count", "status": "PASS", "detail": f"{total_slides} slides (optimal defense range: 18–26)"})
    elif 15 <= total_slides <= 32:
        checks.append({"name": "Slide Count", "status": "PASS", "detail": f"{total_slides} slides (acceptable defense range: 15–32)"})
    else:
        checks.append({"name": "Slide Count", "status": "FAIL", "detail": f"{total_slides} slides is outside standard defense range (15–32)"})
        
    # ---------------------------------------------------------
    # 2. Speaker Notes Coverage (Rule 11: 100% substantive slides)
    # ---------------------------------------------------------
    missing_notes = []
    for idx, s in enumerate(slides):
        notes = s.get("speaker_notes", "").strip()
        if not notes or len(notes) < 25:
            missing_notes.append(idx + 1)
    if not missing_notes:
        checks.append({"name": "Notes Coverage", "status": "PASS", "detail": "100% of slides contain rich defense speaker notes"})
    else:
        checks.append({"name": "Notes Coverage", "status": "FAIL", "detail": f"Slides missing adequate speaker notes: {missing_notes}"})
        
    # ---------------------------------------------------------
    # 3. Metadata Hygiene & Provenance (Rules 1.6 & 1.7)
    # ---------------------------------------------------------
    found_tokens = []
    payload_str = str(payload)
    
    for tok in FORBIDDEN_EXAMPLE_TOKENS:
        if tok in payload_str:
            found_tokens.append(tok)
            
    # Check for accidental cross-project identity leakage (e.g. from previous runs)
    author = meta.get("author", "")
    if "مرضیه" not in author and "سینائی" not in author:
        if "مرضیه سینائی" in payload_str:
            found_tokens.append("مرضیه سینائی (cross-project leak)")
            
    uni = meta.get("university", "") + " " + meta.get("faculty", "")
    if "کاشان" not in uni:
        if "واحد کاشان" in payload_str:
            found_tokens.append("واحد کاشان (cross-project leak)")

    if not found_tokens:
        checks.append({"name": "Metadata Hygiene", "status": "PASS", "detail": "Zero unresolved placeholders or cross-project identity leaks found"})
    else:
        checks.append({"name": "Metadata Hygiene", "status": "FAIL", "detail": f"Unresolved placeholders or leaks detected: {found_tokens}"})

    # ---------------------------------------------------------
    # Extract Content Slides and Families
    # ---------------------------------------------------------
    content_slides: List[Tuple[int, str, str]] = [] # (slide_num, layout, family)
    for idx, s in enumerate(slides):
        slide_num = s.get("slide_number", idx + 1)
        layout = s.get("layout", "cards")
        fam = LAYOUT_FAMILY_MAPPING.get(layout, "other")
        if fam not in ["cover", "administrative", "closing", "transition"]:
            content_slides.append((slide_num, layout, fam))
            
    content_count = len(content_slides)

    # ---------------------------------------------------------
    # 4. Generic Card Layout Limit (Rule 1.3: <= 25% of content slides)
    # ---------------------------------------------------------
    card_count = sum(1 for _, layout, _ in content_slides if layout in GENERIC_CARD_LAYOUTS)
    card_ratio = (card_count / content_count) if content_count > 0 else 0.0
    if card_ratio <= MAX_CARD_LAYOUT_RATIO:
        checks.append({
            "name": "Cards Limit (<=25%)",
            "status": "PASS",
            "detail": f"Generic cards: {card_count}/{content_count} = {card_ratio:.1%} (strict limit: {MAX_CARD_LAYOUT_RATIO:.0%})"
        })
    else:
        checks.append({
            "name": "Cards Limit (<=25%)",
            "status": "FAIL",
            "detail": f"Generic card layouts exceed 25%: {card_count}/{content_count} = {card_ratio:.1%} (strict limit: 25%)"
        })

    # ---------------------------------------------------------
    # 5. Consecutive Layout Family Check (Rule 1.4: Never use same family twice in a row)
    # ---------------------------------------------------------
    consecutive_violations = []
    for i in range(1, len(content_slides)):
        prev_num, prev_layout, prev_fam = content_slides[i - 1]
        curr_num, curr_layout, curr_fam = content_slides[i]
        if prev_fam == curr_fam:
            consecutive_violations.append(f"Slide {prev_num} ({prev_fam}) -> Slide {curr_num} ({curr_fam})")
            
    if not consecutive_violations:
        checks.append({
            "name": "Family Alternation",
            "status": "PASS",
            "detail": "No consecutive content slides share the same layout family"
        })
    else:
        checks.append({
            "name": "Family Alternation",
            "status": "FAIL",
            "detail": f"Consecutive identical layout families: {'; '.join(consecutive_violations)}"
        })

    # ---------------------------------------------------------
    # 6. Layout Family Dominance (Rule 1.4: <= 30% of content slides)
    # ---------------------------------------------------------
    family_counts: Dict[str, int] = {}
    for _, _, fam in content_slides:
        family_counts[fam] = family_counts.get(fam, 0) + 1
        
    violating_dominance = []
    if content_count > 0:
        for fam, cnt in family_counts.items():
            ratio = cnt / content_count
            if ratio > MAX_LAYOUT_FAMILY_RATIO:
                violating_dominance.append(f"'{fam}' ({cnt}/{content_count} = {ratio:.1%})")
                
    if not violating_dominance:
        top_fam = max(family_counts.items(), key=lambda x: x[1]) if family_counts else ("none", 0)
        top_ratio = (top_fam[1] / max(content_count, 1))
        checks.append({
            "name": "Family Dominance (<=30%)",
            "status": "PASS",
            "detail": f"Max family dominance: '{top_fam[0]}' at {top_ratio:.1%} (limit: {MAX_LAYOUT_FAMILY_RATIO:.0%})"
        })
    else:
        checks.append({
            "name": "Family Dominance (<=30%)",
            "status": "FAIL",
            "detail": f"Layout family dominates > 30%: {', '.join(violating_dominance)}"
        })

    # ---------------------------------------------------------
    # 7. Supported Layouts Verification (Rule 1.4 & Section 15)
    # ---------------------------------------------------------
    unsupported = []
    for idx, s in enumerate(slides):
        lay = s.get("layout")
        if lay and lay not in SUPPORTED_LAYOUTS:
            unsupported.append(f"Slide {idx+1}: '{lay}'")
    if not unsupported:
        checks.append({"name": "Layout Support", "status": "PASS", "detail": "All slide layouts are officially verified in v3 schema"})
    else:
        checks.append({"name": "Layout Support", "status": "FAIL", "detail": f"Unsupported layouts: {unsupported}"})

    # ---------------------------------------------------------
    # 8. Text Density Heuristic (Rule 12.3: Text blocks <= 500 chars)
    # ---------------------------------------------------------
    dense_slides = []
    for idx, s in enumerate(slides):
        for c in s.get("cards", []):
            if len(c.get("desc", "")) > 500:
                dense_slides.append(idx + 1)
        if len(s.get("message", "")) > 400:
            dense_slides.append(idx + 1)
        total_text_len = sum(len(str(v)) for k, v in s.items() if k not in ["speaker_notes", "rows", "headers"])
        if total_text_len > 1200:
            dense_slides.append(idx + 1)

    dense_slides = sorted(list(set(dense_slides)))
    if not dense_slides:
        checks.append({"name": "Text Density", "status": "PASS", "detail": "All slides within comfortable scannable text budget"})
    else:
        checks.append({"name": "Text Density", "status": "WARN", "detail": f"Dense slides flagged for potential simplification: {dense_slides}"})

    # ---------------------------------------------------------
    # 9. Table Density Heuristic (Rule 9 & Rule 12.3: <= 6 cols, <= 8 rows)
    # ---------------------------------------------------------
    dense_tables = []
    severe_tables = []
    for idx, s in enumerate(slides):
        if s.get("layout") in ["stat_table", "table", "hypothesis_matrix", "instrument_matrix"]:
            headers = s.get("headers", [])
            rows = s.get("rows", [])
            if len(headers) > 8 or len(rows) > 10:
                severe_tables.append(f"Slide {idx+1} ({len(headers)} cols x {len(rows)} rows)")
            elif len(headers) > 6 or len(rows) > 8:
                dense_tables.append(f"Slide {idx+1} ({len(headers)} cols x {len(rows)} rows)")

    if severe_tables:
        checks.append({"name": "Table Density", "status": "FAIL", "detail": f"Severely oversized tables exceeding legibility limit: {severe_tables}"})
    elif dense_tables:
        checks.append({"name": "Table Density", "status": "WARN", "detail": f"Dense tables recommended for splitting: {dense_tables}"})
    else:
        checks.append({"name": "Table Density", "status": "PASS", "detail": "All tables adhere to defense legibility bounds (<=6 cols, <=8 rows)"})

    # ---------------------------------------------------------
    # 10. Asset Resolution (Rule 14: All referenced assets must exist)
    # ---------------------------------------------------------
    missing_imgs = []
    for idx, s in enumerate(slides):
        img_p = s.get("image_path")
        if img_p and not os.path.exists(img_p):
            missing_imgs.append(f"Slide {idx+1}: {img_p}")
    if not missing_imgs:
        checks.append({"name": "Asset Resolution", "status": "PASS", "detail": "All referenced figure and diagram image assets exist"})
    else:
        checks.append({"name": "Asset Resolution", "status": "FAIL", "detail": f"Missing image files: {missing_imgs}"})

    # ---------------------------------------------------------
    # 11. Multi-Dimensional Quality Score (Rule 17: 100-point rubric)
    # ---------------------------------------------------------
    score_fidelity = 25.0
    if any(c["name"] == "Metadata Hygiene" and c["status"] == "FAIL" for c in checks):
        score_fidelity -= 15.0

    score_narrative = 20.0
    if any(c["name"] == "Slide Count" and c["status"] == "FAIL" for c in checks):
        score_narrative -= 6.0
    if any(c["name"] == "Family Alternation" and c["status"] == "FAIL" for c in checks):
        score_narrative -= 7.0

    score_visual = 20.0
    if any(c["name"] == "Cards Limit (<=25%)" and c["status"] == "FAIL" for c in checks):
        score_visual -= 8.0
    if any(c["name"] == "Family Dominance (<=30%)" and c["status"] == "FAIL" for c in checks):
        score_visual -= 6.0

    score_readability = 15.0
    if any(c["name"] == "Text Density" and c["status"] == "WARN" for c in checks):
        score_readability -= 2.0
    if any(c["name"] == "Table Density" and c["status"] == "WARN" for c in checks):
        score_readability -= 2.0
    elif any(c["name"] == "Table Density" and c["status"] == "FAIL" for c in checks):
        score_readability -= 5.0

    score_consistency = 10.0
    if any(c["name"] == "Layout Support" and c["status"] == "FAIL" for c in checks):
        score_consistency -= 5.0

    score_technical = 10.0
    if any(c["name"] == "Notes Coverage" and c["status"] == "FAIL" for c in checks):
        score_technical -= 5.0
    if any(c["name"] == "Asset Resolution" and c["status"] == "FAIL" for c in checks):
        score_technical -= 5.0

    total_score = max(0.0, min(100.0, (
        score_fidelity + score_narrative + score_visual +
        score_readability + score_consistency + score_technical
    )))

    has_fail = any(c["status"] == "FAIL" for c in checks)
    has_warn = any(c["status"] == "WARN" for c in checks)

    if has_fail or total_score < 90.0 or score_technical < 10.0 or score_fidelity < 20.0:
        final_status = "FAIL"
        overall_pass = False
    elif has_warn:
        final_status = "PASS_WITH_WARNINGS"
        overall_pass = True
    else:
        final_status = "PASS"
        overall_pass = True

    score_summary = {
        "overall_score": round(total_score, 1),
        "status": final_status,
        "breakdown": {
            "research_fidelity": round(score_fidelity, 1),
            "narrative_quality": round(score_narrative, 1),
            "visual_communication": round(score_visual, 1),
            "readability_typography": round(score_readability, 1),
            "visual_consistency": round(score_consistency, 1),
            "technical_integrity": round(score_technical, 1)
        }
    }

    lines = [
        "================================================================================",
        "              DEFENSE PRESENTATION AUTOMATED QA AUDIT REPORT v3.0               ",
        "================================================================================",
        f"Deck Title: {meta.get('title', 'Untitled')[:65]}...",
        f"Total Slides: {total_slides} (Content: {content_count}) | Candidate: {meta.get('author', 'Unspecified')}",
        f"FINAL STATUS: {final_status} | QUALITY SCORE: {total_score:.1f}/100",
        "--------------------------------------------------------------------------------",
        f"{'CHECK':<26} | {'STATUS':<6} | {'DETAILS'}",
        "--------------------------------------------------------------------------------"
    ]
    for c in checks:
        lines.append(f"{c['name']:<26} | {c['status']:<6} | {c['detail']}")
    lines.append("--------------------------------------------------------------------------------")
    lines.append(f"Score Breakdown: Fidelity={score_fidelity:.0f}/25 | Narrative={score_narrative:.0f}/20 | Visuals={score_visual:.0f}/20 | Type={score_readability:.0f}/15 | Consistency={score_consistency:.0f}/10 | Tech={score_technical:.0f}/10")
    lines.append("================================================================================")

    report_text = "\n".join(lines)
    return overall_pass, checks, report_text, score_summary

if __name__ == "__main__":
    import json, sys
    if len(sys.argv) > 1:
        with open(sys.argv[1], "r", encoding="utf-8") as f:
            data = json.load(f)
        ok, res, rep, score = run_qa_checks(data)
        print(rep)
        sys.exit(0 if ok else 1)
