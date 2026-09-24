#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/contracts/canonical_pipelines.py

Authoritative, deterministic pipeline validator enforcing the Micro-Stage Sequences
codified in MICRO_STAGE_SEQUENCES.md.

Enforces Directive 3 (Artifact-Gated Stage Execution, Micro-Stage Granularity &
Triad Artifact Invariant):
1. Jumping stages without physical checkpoint files existing on disk is strictly prohibited.
2. Every stage must verify that its mandatory prerequisite stage deliverables physically
   exist on disk before authorization.
"""

import os
import re
from typing import Dict, Any, List, Optional, Tuple


# Definition of canonical pipelines and their prerequisite artifact requirements
# Key: stage identifier (normalized regex pattern)
# Value: dict containing:
#   - name: human readable name
#   - pipeline: pipeline category
#   - required_prerequisites: list of artifact patterns that must exist on disk before this stage can run
CANONICAL_STAGE_PREREQUISITES: Dict[str, Dict[str, Any]] = {
    # Chapter 4 Pipeline
    r"4\.0": {
        "name": "Stage 4.0: Data Curation & Preprocessing",
        "pipeline": "chapter4",
        "required_prerequisites": []  # First stage, requires only raw data
    },
    r"4\.1": {
        "name": "Stage 4.1: Demographics Profiling",
        "pipeline": "chapter4",
        "required_prerequisites": [
            r"(?:data_cleaned\.xlsx|00_data_curation_report\.(?:json|md))"
        ]
    },
    r"4\.2": {
        "name": "Stage 4.2: Descriptives & Reliability",
        "pipeline": "chapter4",
        "required_prerequisites": [
            r"(?:data_cleaned\.xlsx|01_demographics\.(?:docx|md|json))"
        ]
    },
    r"4\.3": {
        "name": "Stage 4.3: Parametric Assumptions Verification",
        "pipeline": "chapter4",
        "required_prerequisites": [
            r"(?:data_cleaned\.xlsx|02_descriptives_and_reliability\.(?:docx|md|json))"
        ]
    },
    r"4\.4": {
        "name": "Stage 4.4: Bivariate Correlation Matrix Analysis",
        "pipeline": "chapter4",
        "required_prerequisites": [
            r"03_parametric_assumptions\.(?:docx|md|json)"
        ]
    },
    r"4\.5": {
        "name": "Stage 4.5: Macro Model Fit / Primary Structural Model",
        "pipeline": "chapter4",
        "required_prerequisites": [
            r"03_parametric_assumptions\.(?:docx|md|json)"
        ]
    },
    r"4\.6(?:\.\d+)?": {
        "name": "Stage 4.6: Hypothesis Testing & Narrative Dissection",
        "pipeline": "chapter4",
        "required_prerequisites": [
            # Parametric assumptions MUST be verified before hypothesis testing!
            r"03_parametric_assumptions\.(?:docx|md|json)"
        ]
    },
    r"4\.7(?:\.\d+)?": {
        "name": "Stage 4.7: Indirect / Mediation Path Testing",
        "pipeline": "chapter4",
        "required_prerequisites": [
            r"03_parametric_assumptions\.(?:docx|md|json)"
        ]
    },
    r"4\.8": {
        "name": "Stage 4.8: Master Decision Matrix & Chapter Summary",
        "pipeline": "chapter4",
        "required_prerequisites": [
            r"06_hypothesis_1\.(?:docx|md|json)"
        ]
    },
    r"4\.11": {
        "name": "Stage 4.11: Chapter 4 Assembly",
        "pipeline": "chapter4",
        "required_prerequisites": [
            r"06_hypothesis_1\.(?:docx|md|json)",
            r"(?:chapter_summary|decision_matrix)\.(?:docx|md|json)"
        ]
    },

    # Chapter 5 Pipeline
    r"5\.1": {
        "name": "Stage 5.1: Findings Overview & Purpose Recap",
        "pipeline": "chapter5",
        "required_prerequisites": [
            # Chapter 5 recap requires Chapter 4 findings to exist
            r"(?:Chapter_4_Results\.docx|06_hypothesis_1\.(?:docx|md|json))"
        ]
    },
    r"5\.2(?:\.\d+)?": {
        "name": "Stage 5.2: Hypothesis Deep Discussion",
        "pipeline": "chapter5",
        "required_prerequisites": [
            r"01_findings_recap\.(?:docx|md|json)"
        ]
    },
    r"5\.9": {
        "name": "Stage 5.9: Chapter 5 Consolidation & Assembly",
        "pipeline": "chapter5",
        "required_prerequisites": [
            r"02_hypothesis_1_discussion\.(?:docx|md|json)"
        ]
    }
}


def find_files_matching(workspaces: List[str], pattern: str) -> List[str]:
    """Scans workspaces for files matching regex pattern."""
    regex = re.compile(pattern, re.IGNORECASE)
    matched = []
    for ws in workspaces:
        if not ws or not os.path.exists(ws):
            continue
        for root, _, files in os.walk(ws):
            # Skip hidden and scratch directories
            if any(part.startswith(".") for part in root.split(os.sep) if part not in (".", "..")):
                continue
            if "scratch" in root:
                continue
            for f in files:
                if regex.search(f):
                    matched.append(os.path.join(root, f))
    return matched


def resolve_stage_spec(stage_str: str) -> Optional[Tuple[str, Dict[str, Any]]]:
    """Matches a stage string (e.g. 'Stage 4.6.1', 'Stage 4.3') to canonical stage prerequisites."""
    if not stage_str or not isinstance(stage_str, str):
        return None

    # Extract stage numbers (e.g. '4.6.1' or '4.3' or '5.2')
    m = re.search(r'\b([45]\.\d+(?:\.\d+)?)\b', stage_str)
    if not m:
        return None

    stage_num = m.group(1)
    for pattern, spec in CANONICAL_STAGE_PREREQUISITES.items():
        if re.fullmatch(pattern, stage_num):
            return stage_num, spec

    return None


def verify_pipeline_stage_prerequisites(stage_str: str, workspaces: List[str]) -> Tuple[bool, str]:
    """
    Mechanically verifies that all required prerequisite artifacts for a stage exist on disk.
    Enforces Directive 3 (Zero Skipping Invariant).
    """
    resolved = resolve_stage_spec(stage_str)
    if not resolved:
        # If not a tracked multi-stage sequence (e.g. custom ad-hoc task), allow with advisory
        return True, "Stage not restricted by strict prerequisite sequence."

    stage_num, spec = resolved
    required_prereqs = spec.get("required_prerequisites", [])

    if not required_prereqs:
        return True, "Initial stage requires no prior stage artifacts."

    missing = []
    for prereq_pat in required_prereqs:
        matches = find_files_matching(workspaces, prereq_pat)
        if not matches:
            missing.append(prereq_pat)

    if missing:
        stage_name = spec.get("name", f"Stage {stage_num}")
        return False, (
            f"CONSTITUTIONAL PIPELINE VIOLATION (Directive 3 — Zero Skipping Invariant):\n"
            f"Cannot authorize delegation for '{stage_name}'.\n"
            f"Mandatory prerequisite artifacts are MISSING on disk: {missing}.\n"
            f"Every stage must follow the strict sequence from MICRO_STAGE_SEQUENCES.md. "
            f"You cannot execute '{stage_name}' until the prerequisite stage completes and generates physical artifacts."
        )

    return True, f"Prerequisites for {spec.get('name')} are satisfied."


if __name__ == "__main__":
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        # Test Stage 4.6 without Stage 4.3 assumptions
        ok, reason = verify_pipeline_stage_prerequisites("Stage 4.6: Hypothesis 1", [td])
        print("Stage 4.6 without prereq:", ok, reason)
        assert not ok, "Should fail without assumptions"

        # Create prerequisite assumption file
        assump_file = os.path.join(td, "03_parametric_assumptions.json")
        with open(assump_file, "w") as f:
            f.write("{}")

        ok2, reason2 = verify_pipeline_stage_prerequisites("Stage 4.6: Hypothesis 1", [td])
        print("Stage 4.6 with prereq:", ok2, reason2)
        assert ok2, "Should pass when assumptions file exists"
