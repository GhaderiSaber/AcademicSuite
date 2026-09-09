#!/usr/bin/env python3
"""OMML formula injection: replace {{MATH:id}} or {{MATH:latex}} in .pptx with native Office Math.

Pipeline:
  1. PowerPoint slides contain placeholder text: {{MATH:formula-id}} or {{MATH:latex_expr}}
  2. This script converts LaTeX -> MathML -> OMML (pure Python via latex2mathml + lxml)
     or LaTeX -> OMML via pandoc if available.
  3. It replaces the placeholders in ppt/slides/slide*.xml with native PowerPoint math
     elements (<a14:m><m:oMath>...</m:oMath></a14:m>).

Usage:
  python inject_omml.py input.pptx formulas.json output.pptx
  python inject_omml.py input.pptx --auto output.pptx
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from copy import deepcopy
from pathlib import Path
from typing import Any, Dict, Optional

try:
    from lxml import etree
except ImportError:
    print("ERROR: lxml required. Install: pip install lxml", file=sys.stderr)
    sys.exit(1)

try:
    import latex2mathml.converter
    HAS_LATEX2MATHML = True
except ImportError:
    HAS_LATEX2MATHML = False

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "m": "http://schemas.openxmlformats.org/officeDocument/2006/math",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "a14": "http://schemas.microsoft.com/office/drawing/2010/main",
}
for prefix, uri in NS.items():
    etree.register_namespace(prefix, uri)

PLACEHOLDER_RE = re.compile(r"\{\{MATH:([^}]+)\}\}")
A_NS = NS["a"]
M_NS = NS["m"]
A14_NS = NS["a14"]
MC_NS = NS["mc"]


# ---------------------------------------------------------------------------
# Pure-Python MathML -> OMML Recursive Converter
# ---------------------------------------------------------------------------
def _create_omml_run(text: str, italic: bool = False) -> etree._Element:
    """Build an <m:r> element with <m:t>text</m:t>."""
    r_elem = etree.Element(f"{{{M_NS}}}r")
    if italic:
        rpr = etree.SubElement(r_elem, f"{{{M_NS}}}rPr")
        lit = etree.SubElement(rpr, f"{{{M_NS}}}lit")
    t_elem = etree.SubElement(r_elem, f"{{{M_NS}}}t")
    t_elem.text = text
    t_elem.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    return r_elem


def mathml_node_to_omml(node: etree._Element) -> list[etree._Element]:
    """Recursively converts a MathML XML node into a list of OMML elements."""
    tag = etree.QName(node).localname
    text = (node.text or "").strip()
    results: list[etree._Element] = []

    if tag in ("math", "mrow", "mstyle", "semantics"):
        for child in node:
            results.extend(mathml_node_to_omml(child))
        return results

    if tag in ("mi", "mn", "mo", "mtext"):
        val = node.text or ""
        if val:
            # Common MathML entities or symbols
            val = val.replace("\u2061", "")  # Invisible function application
            is_var = tag == "mi" and len(val) == 1 and val.isalpha()
            results.append(_create_omml_run(val, italic=is_var))
        return results

    if tag == "mfrac":
        # Fraction: <m:f><m:num>...</m:num><m:den>...</m:den></m:f>
        children = list(node)
        if len(children) >= 2:
            f_elem = etree.Element(f"{{{M_NS}}}f")
            num_elem = etree.SubElement(f_elem, f"{{{M_NS}}}num")
            for c in mathml_node_to_omml(children[0]):
                num_elem.append(c)
            den_elem = etree.SubElement(f_elem, f"{{{M_NS}}}den")
            for c in mathml_node_to_omml(children[1]):
                den_elem.append(c)
            results.append(f_elem)
        return results

    if tag == "msup":
        # Superscript: <m:sSup><m:e>...</m:e><m:sup>...</m:sup></m:sSup>
        children = list(node)
        if len(children) >= 2:
            sup_elem = etree.Element(f"{{{M_NS}}}sSup")
            e_elem = etree.SubElement(sup_elem, f"{{{M_NS}}}e")
            for c in mathml_node_to_omml(children[0]):
                e_elem.append(c)
            sp_elem = etree.SubElement(sup_elem, f"{{{M_NS}}}sup")
            for c in mathml_node_to_omml(children[1]):
                sp_elem.append(c)
            results.append(sup_elem)
        return results

    if tag == "msub":
        # Subscript: <m:sSub><m:e>...</m:e><m:sub>...</m:sub></m:sSub>
        children = list(node)
        if len(children) >= 2:
            sub_elem = etree.Element(f"{{{M_NS}}}sSub")
            e_elem = etree.SubElement(sub_elem, f"{{{M_NS}}}e")
            for c in mathml_node_to_omml(children[0]):
                e_elem.append(c)
            sb_elem = etree.SubElement(sub_elem, f"{{{M_NS}}}sub")
            for c in mathml_node_to_omml(children[1]):
                sb_elem.append(c)
            results.append(sub_elem)
        return results

    if tag == "msubsup":
        # Sub-Superscript: <m:sSubSup><m:e>...</m:e><m:sub>...</m:sub><m:sup>...</m:sup></m:sSubSup>
        children = list(node)
        if len(children) >= 3:
            subsup_elem = etree.Element(f"{{{M_NS}}}sSubSup")
            e_elem = etree.SubElement(subsup_elem, f"{{{M_NS}}}e")
            for c in mathml_node_to_omml(children[0]):
                e_elem.append(c)
            sb_elem = etree.SubElement(subsup_elem, f"{{{M_NS}}}sub")
            for c in mathml_node_to_omml(children[1]):
                sb_elem.append(c)
            sp_elem = etree.SubElement(subsup_elem, f"{{{M_NS}}}sup")
            for c in mathml_node_to_omml(children[2]):
                sp_elem.append(c)
            results.append(subsup_elem)
        return results

    if tag == "msqrt":
        # Square Root: <m:rad><m:radPr><m:degHide m:val="1"/></m:radPr><m:deg/><m:e>...</m:e></m:rad>
        rad_elem = etree.Element(f"{{{M_NS}}}rad")
        radpr = etree.SubElement(rad_elem, f"{{{M_NS}}}radPr")
        deghide = etree.SubElement(radpr, f"{{{M_NS}}}degHide")
        deghide.set(f"{{{M_NS}}}val", "1")
        etree.SubElement(rad_elem, f"{{{M_NS}}}deg")
        e_elem = etree.SubElement(rad_elem, f"{{{M_NS}}}e")
        for child in node:
            for c in mathml_node_to_omml(child):
                e_elem.append(c)
        results.append(rad_elem)
        return results

    if tag == "mroot":
        # Nth Root: <m:rad><m:deg>n</m:deg><m:e>base</m:e></m:rad>
        children = list(node)
        if len(children) >= 2:
            rad_elem = etree.Element(f"{{{M_NS}}}rad")
            deg_elem = etree.SubElement(rad_elem, f"{{{M_NS}}}deg")
            for c in mathml_node_to_omml(children[1]):
                deg_elem.append(c)
            e_elem = etree.SubElement(rad_elem, f"{{{M_NS}}}e")
            for c in mathml_node_to_omml(children[0]):
                e_elem.append(c)
            results.append(rad_elem)
        return results

    if tag == "mfenced":
        # Delimiters (brackets, parentheses)
        open_chr = node.get("open", "(")
        close_chr = node.get("close", ")")
        d_elem = etree.Element(f"{{{M_NS}}}d")
        dpr = etree.SubElement(d_elem, f"{{{M_NS}}}dPr")
        beg = etree.SubElement(dpr, f"{{{M_NS}}}begChr")
        beg.set(f"{{{M_NS}}}val", open_chr)
        end = etree.SubElement(dpr, f"{{{M_NS}}}endChr")
        end.set(f"{{{M_NS}}}val", close_chr)
        e_elem = etree.SubElement(d_elem, f"{{{M_NS}}}e")
        for child in node:
            for c in mathml_node_to_omml(child):
                e_elem.append(c)
        results.append(d_elem)
        return results

    # Fallback for unhandled tags: process children or text
    if text:
        results.append(_create_omml_run(text))
    for child in node:
        results.extend(mathml_node_to_omml(child))

    return results


def latex_to_omml_pure_python(latex: str) -> Optional[etree._Element]:
    """Converts LaTeX string to native OMML <m:oMath> using latex2mathml and lxml."""
    if not HAS_LATEX2MATHML:
        return None
    try:
        mml_str = latex2mathml.converter.convert(latex)
        mml_tree = etree.fromstring(mml_str.encode("utf-8"))
        omath = etree.Element(f"{{{M_NS}}}oMath")
        omml_elements = mathml_node_to_omml(mml_tree)
        for elem in omml_elements:
            omath.append(elem)
        return omath
    except Exception as exc:
        print(f"  [latex2mathml->omml] Error converting '{latex}': {exc}", file=sys.stderr)
        return None


def latex_to_omml_pandoc(latex: str) -> Optional[etree._Element]:
    """Fallback: Convert LaTeX math to OMML via pandoc -> docx -> extract oMath."""
    with tempfile.NamedTemporaryFile(suffix=".tex", mode="w", delete=False, encoding="utf-8") as f:
        f.write(f"$${latex}$$\n")
        tex_path = f.name
    docx_path = tex_path.replace(".tex", ".docx")
    try:
        r = subprocess.run(
            ["pandoc", tex_path, "-f", "latex", "-t", "docx", "-o", docx_path],
            capture_output=True, text=True, timeout=10,
        )
        if r.returncode != 0:
            return None
        with zipfile.ZipFile(docx_path, "r") as zf:
            doc_xml = zf.read("word/document.xml")
        tree = etree.fromstring(doc_xml)
        omaths = tree.findall(f".//{{{M_NS}}}oMathPara")
        if not omaths:
            omaths = tree.findall(f".//{{{M_NS}}}oMath")
        return deepcopy(omaths[0]) if omaths else None
    except Exception:
        return None
    finally:
        Path(tex_path).unlink(missing_ok=True)
        Path(docx_path).unlink(missing_ok=True)


def latex_to_omml(latex: str) -> Optional[etree._Element]:
    """Dual-engine converter: pure-Python first, pandoc fallback."""
    # First try pure Python
    res = latex_to_omml_pure_python(latex)
    if res is not None:
        return res
    # Fallback to pandoc
    return latex_to_omml_pandoc(latex)


# ---------------------------------------------------------------------------
# XML Manipulation & Injection
# ---------------------------------------------------------------------------
def _merge_paragraph_runs(p_elem):
    """Merge all <a:r> run texts in a paragraph to reconstruct split placeholders."""
    runs = []
    for child in p_elem:
        tag = child.tag
        if tag == f"{{{A_NS}}}r":
            t_elem = child.find(f"{{{A_NS}}}t")
            text = t_elem.text if t_elem is not None and t_elem.text else ""
            runs.append((child, text))
    full_text = "".join(t for _, t in runs)
    return full_text, runs


def _make_text_run(text: str, rpr_template=None) -> etree._Element:
    """Create an <a:r> element with optional run properties."""
    r = etree.Element(f"{{{A_NS}}}r")
    if rpr_template is not None:
        r.append(deepcopy(rpr_template))
    t = etree.SubElement(r, f"{{{A_NS}}}t")
    t.text = text
    t.set("{http://www.w3.org/XML/1998/namespace}space", "preserve")
    return r


def _rebuild_paragraph(p_elem, full_text: str, runs, omml_cache: Dict[str, etree._Element]) -> int:
    """Replace placeholders in merged text, rebuild run structure with OMML."""
    matches = list(PLACEHOLDER_RE.finditer(full_text))
    if not matches:
        return 0

    first_run = runs[0][0] if runs else None
    rpr_template = first_run.find(f"{{{A_NS}}}rPr") if first_run is not None else None

    # Remove all existing runs from paragraph
    for run, _ in runs:
        p_elem.remove(run)

    insert_idx = 0
    for i, child in enumerate(p_elem):
        if child.tag == f"{{{A_NS}}}pPr":
            insert_idx = i + 1
            break

    replaced = 0
    last_end = 0

    for match in matches:
        expr = match.group(1)
        before = full_text[last_end:match.start()]
        if before:
            r_elem = _make_text_run(before, rpr_template)
            p_elem.insert(insert_idx, r_elem)
            insert_idx += 1

        # Check omml_cache or try converting directly
        omml_elem = omml_cache.get(expr)
        if omml_elem is None:
            omml_elem = latex_to_omml(expr)
            if omml_elem is not None:
                omml_cache[expr] = omml_elem

        if omml_elem is not None:
            a14_m = etree.Element(f"{{{A14_NS}}}m")
            a14_m.append(deepcopy(omml_elem))
            p_elem.insert(insert_idx, a14_m)
            insert_idx += 1
            replaced += 1
        else:
            r_elem = _make_text_run(match.group(0), rpr_template)
            p_elem.insert(insert_idx, r_elem)
            insert_idx += 1

        last_end = match.end()

    after = full_text[last_end:]
    if after:
        r_elem = _make_text_run(after, rpr_template)
        p_elem.insert(insert_idx, r_elem)

    return replaced


def _ensure_namespaces(tree) -> etree._Element:
    """Ensure root element declares mc: and a14: namespaces."""
    root = tree
    nsmap = root.nsmap if hasattr(root, "nsmap") else {}
    need_mc = "mc" not in nsmap and MC_NS not in nsmap.values()
    need_a14 = "a14" not in nsmap and A14_NS not in nsmap.values()

    if not (need_mc or need_a14):
        return tree

    xml_str = etree.tostring(tree, encoding="unicode")
    ns_decls = ""
    if need_mc:
        ns_decls += f' xmlns:mc="{MC_NS}"'
    if need_a14:
        ns_decls += f' xmlns:a14="{A14_NS}"'

    gt_pos = xml_str.index(">")
    xml_str = xml_str[:gt_pos] + ns_decls + xml_str[gt_pos:]
    return etree.fromstring(xml_str.encode("utf-8"))


def process_presentation(
    pptx_in: str,
    formulas: Dict[str, str],
    pptx_out: str,
) -> int:
    """Process a PPTX file, replacing {{MATH:id}} with native OMML. Returns total replacements."""
    # Pre-render OMML elements
    omml_cache: Dict[str, etree._Element] = {}
    print(f"[*] Pre-rendering {len(formulas)} formula(s) to native OMML...")
    for fid, latex in formulas.items():
        elem = latex_to_omml(latex)
        if elem is not None:
            omml_cache[fid] = elem
        else:
            print(f"  [!] Failed to convert formula '{fid}': {latex}", file=sys.stderr)

    total_replaced = 0
    with tempfile.TemporaryDirectory(prefix="pptx_omml_") as tmpdir:
        tmp_zip = os.path.join(tmpdir, "archive.zip")
        shutil.copy2(pptx_in, tmp_zip)

        extract_dir = os.path.join(tmpdir, "extracted")
        with zipfile.ZipFile(tmp_zip, "r") as zf:
            zf.extractall(extract_dir)

        slides_dir = Path(extract_dir) / "ppt" / "slides"
        if slides_dir.exists():
            for slide_path in sorted(slides_dir.glob("slide*.xml")):
                tree = etree.parse(str(slide_path))
                slide_replaced = 0
                for p_elem in tree.findall(f".//{{{A_NS}}}p"):
                    full_text, runs = _merge_paragraph_runs(p_elem)
                    if PLACEHOLDER_RE.search(full_text):
                        slide_replaced += _rebuild_paragraph(p_elem, full_text, runs, omml_cache)

                if slide_replaced > 0:
                    total_replaced += slide_replaced
                    tree = _ensure_namespaces(tree)
                    tree.write(str(slide_path), xml_declaration=True, encoding="utf-8", standalone=True)
                    print(f"  [+] Slide {slide_path.stem}: injected {slide_replaced} native math expression(s)")

        # Re-pack the PPTX
        out_dir = os.path.dirname(os.path.abspath(pptx_out))
        if out_dir:
            os.makedirs(out_dir, exist_ok=True)

        with zipfile.ZipFile(pptx_out, "w", zipfile.ZIP_DEFLATED) as zout:
            for root, _, files in os.walk(extract_dir):
                for f in files:
                    full_path = os.path.join(root, f)
                    rel_path = os.path.relpath(full_path, extract_dir)
                    zout.write(full_path, rel_path)

    print(f"[SUCCESS] Native OMML injection complete. Replaced {total_replaced} formula(s). Output: {pptx_out}")
    return total_replaced


def main():
    parser = argparse.ArgumentParser(description="OMML Native Formula Injector for PowerPoint")
    parser.add_argument("input_pptx", help="Path to input .pptx")
    parser.add_argument("formulas_json", nargs="?", help="Path to formulas JSON dictionary (id -> latex)")
    parser.add_argument("output_pptx", help="Path to output .pptx")
    parser.add_argument("--auto", action="store_true", help="Auto-convert raw LaTeX inside {{MATH:latex}}")
    args = parser.parse_args()

    formulas = {}
    if args.formulas_json and os.path.exists(args.formulas_json):
        with open(args.formulas_json, "r", encoding="utf-8") as f:
            formulas = json.load(f)

    process_presentation(args.input_pptx, formulas, args.output_pptx)


if __name__ == "__main__":
    main()
