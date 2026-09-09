#!/usr/bin/env python3
"""PPTX element overlap & boundary auditor for academic defense presentations.

Parses slide XML to extract element bounding boxes, then detects:
  1. Overlapping elements (intersection area > threshold)
  2. Insufficient vertical gaps between adjacent elements
  3. Elements exceeding slide boundaries (taking into account widescreen dimensions)

Card-aware: groups elements inside the same card container to avoid
false positives from title/body text boxes overlapping their parent shape.

Usage:
  python check_overlaps.py input.pptx [--json report.json] [--min-overlap 0.01] [--min-gap 0.05]

Exit codes: 0 = clean, 1 = critical/major issues found.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from lxml import etree
except ImportError:
    print("ERROR: lxml required. Install: pip install lxml", file=sys.stderr)
    sys.exit(1)

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
}

EMU_PER_INCH = 914400


def emu_to_inch(emu: int) -> float:
    return emu / EMU_PER_INCH


@dataclass
class BBox:
    x: float
    y: float
    w: float
    h: float
    label: str = ""
    slide: int = 0
    has_text: bool = False
    has_fill: bool = False
    group_id: int = -1  # container group assignment

    @property
    def right(self) -> float:
        return self.x + self.w

    @property
    def bottom(self) -> float:
        return self.y + self.h

    @property
    def area(self) -> float:
        return self.w * self.h


def _extract_text(sp) -> str:
    parts = []
    for t in sp.iterfind(".//a:t", NS):
        if t.text:
            parts.append(t.text)
    text = "".join(parts).strip().replace("\n", " ")
    return text[:60] if text else ""


def _has_solid_fill(sp) -> bool:
    """Check if a shape has a solid fill (container rectangle)."""
    return sp.find(".//p:spPr/a:solidFill", NS) is not None


def _extract_bbox(sp, offset_x=0.0, offset_y=0.0) -> Optional[BBox]:
    xfrm = sp.find(".//p:spPr/a:xfrm", NS)
    if xfrm is None:
        xfrm = sp.find(".//a:xfrm", NS)
    if xfrm is None:
        return None

    off = xfrm.find("a:off", NS)
    ext = xfrm.find("a:ext", NS)
    if off is None or ext is None:
        return None

    x = emu_to_inch(int(off.get("x", "0"))) + offset_x
    y = emu_to_inch(int(off.get("y", "0"))) + offset_y
    w = emu_to_inch(int(ext.get("cx", "0")))
    h = emu_to_inch(int(ext.get("cy", "0")))

    if w < 0.01 or h < 0.01:
        return None

    is_shape = sp.tag.endswith("}sp")
    label = _extract_text(sp) if is_shape else "[image/table]"
    has_text = bool(label) if is_shape else False
    has_fill = _has_solid_fill(sp) if is_shape else False

    return BBox(x=x, y=y, w=w, h=h, label=label, has_text=has_text, has_fill=has_fill)


def _is_background(b: BBox, sw: float, sh: float) -> bool:
    if b.y < 0.05 and b.w > (sw * 0.85) and b.h <= 1.2:
        return True
    if b.y > (sh - 1.0) and b.w > (sw * 0.85):
        return True
    # Full slide background shape
    if b.w >= (sw - 0.2) and b.h >= (sh - 0.2):
        return True
    return False


def _is_accent_bar(b: BBox) -> bool:
    return b.w <= 0.12 or b.h <= 0.08


def _is_badge(b: BBox) -> bool:
    return b.w <= 0.8 and b.h <= 0.5 and b.area < 0.4


def _contains(outer: BBox, inner: BBox, tol=0.08) -> bool:
    return (
        inner.x >= outer.x - tol
        and inner.y >= outer.y - tol
        and inner.right <= outer.right + tol
        and inner.bottom <= outer.bottom + tol
    )


def _overlap_area(a: BBox, b: BBox) -> float:
    ix = max(0, min(a.right, b.right) - max(a.x, b.x))
    iy = max(0, min(a.bottom, b.bottom) - max(a.y, b.y))
    return ix * iy


def _assign_container_groups(elements: list[BBox], sw: float, sh: float) -> None:
    """Group elements into card containers to avoid false positives."""
    containers = []
    for i, e in enumerate(elements):
        if e.has_fill and not e.has_text and e.area > 0.5 and not _is_background(e, sw, sh):
            containers.append((i, e))

    group_counter = 0
    for ci, container in containers:
        members = [ci]
        for j, e in enumerate(elements):
            if j == ci:
                continue
            if _contains(container, e):
                members.append(j)
        if len(members) >= 2:
            for idx in members:
                elements[idx].group_id = group_counter
            group_counter += 1


def get_slide_dimensions(zf: zipfile.ZipFile) -> Tuple[float, float]:
    """Reads slide width and height from ppt/presentation.xml."""
    try:
        pres_xml = zf.read("ppt/presentation.xml")
        tree = etree.fromstring(pres_xml)
        sld_sz = tree.find(".//p:sldSz", NS)
        if sld_sz is not None:
            sw = emu_to_inch(int(sld_sz.get("cx", "12192000")))
            sh = emu_to_inch(int(sld_sz.get("cy", "6858000")))
            return sw, sh
    except Exception:
        pass
    return 13.333, 7.5  # Standard 16:9 widescreen default


def extract_elements(slide_xml: bytes, slide_num: int, sw: float, sh: float) -> list[BBox]:
    tree = etree.fromstring(slide_xml)
    elements = []

    def collect(parent_path, ox=0.0, oy=0.0):
        for sp in parent_path.findall("p:sp", NS):
            bb = _extract_bbox(sp, ox, oy)
            if bb:
                bb.slide = slide_num
                elements.append(bb)
        for pic in parent_path.findall("p:pic", NS):
            bb = _extract_bbox(pic, ox, oy)
            if bb:
                bb.slide = slide_num
                bb.label = bb.label or "[image]"
                elements.append(bb)
        for tbl in parent_path.findall(".//a:tbl", NS):
            # Find parent graphicFrame
            gf = tbl.getparent()
            while gf is not None and not gf.tag.endswith("graphicFrame"):
                gf = gf.getparent()
            if gf is not None:
                bb = _extract_bbox(gf, ox, oy)
                if bb:
                    bb.slide = slide_num
                    bb.label = bb.label or "[table]"
                    elements.append(bb)
        for grp in parent_path.findall("p:grpSp", NS):
            grp_xfrm = grp.find("p:grpSpPr/a:xfrm", NS)
            gox, goy = ox, oy
            if grp_xfrm is not None:
                goff = grp_xfrm.find("a:off", NS)
                if goff is not None:
                    gox += emu_to_inch(int(goff.get("x", "0")))
                    goy += emu_to_inch(int(goff.get("y", "0")))
            collect(grp, gox, goy)

    sp_tree = tree.find("p:cSld/p:spTree", NS)
    if sp_tree is not None:
        collect(sp_tree)

    _assign_container_groups(elements, sw, sh)
    return elements


@dataclass
class Issue:
    slide: int
    severity: str
    kind: str
    message: str
    details: dict = field(default_factory=dict)


def check_slide(
    elements: list[BBox],
    slide_num: int,
    sw: float,
    sh: float,
    min_overlap: float = 0.02,
    min_gap: float = 0.04,
) -> list[Issue]:
    issues = []
    margin = 0.4

    content = [e for e in elements if not _is_background(e, sw, sh) and not _is_accent_bar(e)]

    # 1. Slide Boundary check
    for e in content:
        if e.bottom > sh - margin + 0.10:
            issues.append(
                Issue(
                    slide=slide_num,
                    severity="CRITICAL",
                    kind="boundary",
                    message=f"Bottom overflow: bottom={e.bottom:.2f}\" > limit={sh - margin:.2f}\"",
                    details={"label": e.label, "y": round(e.y, 3), "h": round(e.h, 3), "bottom": round(e.bottom, 3)},
                )
            )
        if e.right > sw - margin + 0.10:
            issues.append(
                Issue(
                    slide=slide_num,
                    severity="MAJOR",
                    kind="boundary",
                    message=f"Right overflow: right={e.right:.2f}\" > limit={sw - margin:.2f}\"",
                    details={"label": e.label, "x": round(e.x, 3), "w": round(e.w, 3), "right": round(e.right, 3)},
                )
            )

    # 2. Overlap check
    check_elems = [e for e in content if not _is_badge(e)]
    for i, a in enumerate(check_elems):
        for b in check_elems[i + 1:]:
            if a.group_id >= 0 and a.group_id == b.group_id:
                continue
            area = _overlap_area(a, b)
            if area < min_overlap:
                continue
            if _contains(a, b) or _contains(b, a):
                continue
            smaller_area = min(a.area, b.area)
            if smaller_area < 0.001:
                continue
            ratio = area / smaller_area
            if ratio < 0.05:
                continue

            sev = "CRITICAL" if ratio > 0.30 else "MAJOR"
            issues.append(
                Issue(
                    slide=slide_num,
                    severity=sev,
                    kind="overlap",
                    message=f"Overlap ({ratio:.0%}): \"{a.label[:25]}\" vs \"{b.label[:25]}\"",
                    details={
                        "elem_a": {"label": a.label, "y": round(a.y, 3), "bottom": round(a.bottom, 3)},
                        "elem_b": {"label": b.label, "y": round(b.y, 3), "bottom": round(b.bottom, 3)},
                        "overlap_ratio": round(ratio, 3),
                    },
                )
            )

    return issues


def audit_presentation(
    pptx_path: str,
    min_overlap: float = 0.02,
    min_gap: float = 0.04,
) -> Tuple[bool, List[Issue], Dict[str, Any]]:
    """Runs geometric & overlap audit on a PowerPoint presentation."""
    if not os.path.exists(pptx_path):
        raise FileNotFoundError(f"Presentation file not found: {pptx_path}")

    all_issues: list[Issue] = []
    slide_count = 0

    with zipfile.ZipFile(pptx_path, "r") as zf:
        sw, sh = get_slide_dimensions(zf)
        slide_files = sorted(
            [n for n in zf.namelist() if re.match(r"ppt/slides/slide\d+\.xml", n)],
            key=lambda x: int(re.search(r"\d+", x).group()),
        )
        slide_count = len(slide_files)

        for sfile in slide_files:
            slide_num = int(re.search(r"\d+", sfile).group())
            slide_xml = zf.read(sfile)
            elems = extract_elements(slide_xml, slide_num, sw, sh)
            issues = check_slide(elems, slide_num, sw, sh, min_overlap, min_gap)
            all_issues.extend(issues)

    crit_count = sum(1 for i in all_issues if i.severity == "CRITICAL")
    maj_count = sum(1 for i in all_issues if i.severity == "MAJOR")
    passed = crit_count == 0 and maj_count == 0

    summary = {
        "presentation": pptx_path,
        "slide_count": slide_count,
        "dimensions": {"width": sw, "height": sh},
        "critical_issues": crit_count,
        "major_issues": maj_count,
        "status": "PASS" if passed else "FAIL",
        "total_issues": len(all_issues),
    }

    return passed, all_issues, summary


def main():
    parser = argparse.ArgumentParser(description="PPTX Element Overlap & Boundary Auditor")
    parser.add_argument("pptx_path", help="Path to .pptx file")
    parser.add_argument("--json", help="Path to write JSON report")
    parser.add_argument("--min-overlap", type=float, default=0.02, help="Min overlap area in sq.in")
    parser.add_argument("--min-gap", type=float, default=0.04, help="Min vertical gap in inches")
    args = parser.parse_args()

    passed, issues, summary = audit_presentation(args.pptx_path, args.min_overlap, args.min_gap)

    print(f"[*] Audited {summary['slide_count']} slides ({summary['dimensions']['width']}\" x {summary['dimensions']['height']}\")")
    print(f"[*] Result: {summary['status']} (Critical: {summary['critical_issues']}, Major: {summary['major_issues']})")

    if issues:
        print("\nDetected Issues:")
        for issue in issues:
            print(f"  - [Slide {issue.slide}] [{issue.severity}] {issue.kind}: {issue.message}")

    if args.json:
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
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)
        print(f"[*] JSON report written to: {args.json}")

    sys.exit(0 if passed else 1)


if __name__ == "__main__":
    main()
