#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/scripts/generate_literature_matrix_triad.py
CLI runner for Chapter 2 Literature Review Thematic Synthesis Matrix Engine (Stage 2.6).

Satisfies Stage 2.6 of the Chapter 2 Literature Review Pipeline (MICRO_STAGE_SEQUENCES.md):
- Produces synchronized triad deliverables on disk:
  1. 06_literature_matrix_table.docx
  2. 06_literature_matrix_table.md
  3. 06_literature_matrix_table.json
  4. Literature_Synthesis_Matrix.xlsx

Usage:
  python3 .agents/scripts/generate_literature_matrix_triad.py --json path/to/payload.json --out-dir projects/my_study/06_literature_matrix
  python3 .agents/scripts/generate_literature_matrix_triad.py --generate-sample --out-dir /tmp/sample_lit_matrix
"""

import os
import sys
import json
import argparse

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

# Add skill script directory to sys.path
SKILL_SCRIPTS_DIR = os.path.join(ROOT_DIR, ".agents", "skills", "persian-literature-review-builder", "scripts")
SKILL_EXAMPLES_DIR = os.path.join(ROOT_DIR, ".agents", "skills", "persian-literature-review-builder", "examples")
for p in [ROOT_DIR, SKILL_SCRIPTS_DIR, SKILL_EXAMPLES_DIR]:
    if p not in sys.path:
        sys.path.insert(0, p)

from literature_synthesis_matrix_engine import LiteratureSynthesisMatrixEngine


def main():
    parser = argparse.ArgumentParser(
        description="Generate Chapter 2 Literature Review Thematic Synthesis Matrix Triad (Stage 2.6)"
    )
    parser.add_argument("--json", type=str, help="Path to input literature payload JSON file")
    parser.add_argument("--out-dir", type=str, required=True, help="Target directory for Stage 2.6 triad deliverables")
    parser.add_argument("--lang", type=str, default="fa", choices=["fa", "en"], help="Primary document language (default: fa)")
    parser.add_argument("--generate-sample", action="store_true", help="Generate and run reference sample payload")

    args = parser.parse_args()

    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)

    if args.generate_sample:
        from sample_synthesis_matrix_payload import get_sample_payload
        payload = get_sample_payload()
        print("[INFO] Generating sample reference payload for Chapter 2 Thematic Synthesis Matrix...")
    elif args.json:
        if not os.path.isfile(args.json):
            sys.stderr.write(f"Error: Input JSON file not found: {args.json}\n")
            sys.exit(1)
        with open(args.json, "r", encoding="utf-8") as f:
            payload = json.load(f)
    else:
        sys.stderr.write("Error: Either --json <file.json> or --generate-sample must be specified.\n")
        sys.exit(1)

    artifacts = LiteratureSynthesisMatrixEngine.process_and_export(
        payload=payload,
        out_dir=out_dir,
        lang=args.lang
    )

    print("\n[SUCCESS] Chapter 2 Stage 2.6 Thematic Synthesis Matrix Triad generated:")
    print(f"  - Word Document (.docx): {artifacts['docx']}")
    print(f"  - Markdown Summary (.md): {artifacts['md']}")
    print(f"  - Data / Parameters (.json): {artifacts['json']}")
    print(f"  - Multi-sheet Excel (.xlsx): {artifacts['xlsx']}\n")


if __name__ == "__main__":
    main()
