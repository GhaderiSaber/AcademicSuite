#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
.agents/contracts/canonical_pipelines.py

Authoritative, deterministic pipeline validator enforcing the Micro-Stage Sequences
codified in MICRO_STAGE_SEQUENCES.md for all 7 academic pipelines:
1. Chapter 4 Empirical Findings (Stages 4.0 – 4.12)
2. Chapter 5 Discussion & Conclusion (Stages 5.1 – 5.10)
3. Chapter 2 Literature Review (Stages 2.1 – 2.8)
4. Research Proposal (Stages P.1 – P.8)
5. Psychometric Scale Validation (Stages V.1 – V.9)
6. Academic Defense Presentation (Stages D.0 – D.7)
7. Empirical Data Generation & Simulation (Stages DS.0 – DS.5)

Enforces Directive 3 (Artifact-Gated Stage Execution, Micro-Stage Granularity &
Triad Artifact Invariant):
1. Jumping stages without physical checkpoint files existing on disk is strictly prohibited.
2. Every stage must verify that its mandatory prerequisite stage deliverables physically
   exist on disk before authorization.
"""

import os
import re
from typing import Dict, Any, List, Optional, Tuple


CANONICAL_STAGE_PREREQUISITES: Dict[str, Dict[str, Any]] = {
    # ─── 1. Chapter 4 Pipeline (Empirical Findings: Stages 4.0 – 4.12) ───
    r"4\.0": {
        "name": "Stage 4.0: Data Curation & Preprocessing",
        "pipeline": "chapter4",
        "required_prerequisites": []
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
    r"4\.9": {
        "name": "Stage 4.9: Statistical QC & MSAI Anomaly Audit",
        "pipeline": "chapter4",
        "required_prerequisites": [
            r"06_hypothesis_1\.(?:docx|md|json)"
        ]
    },
    r"4\.10": {
        "name": "Stage 4.10: Results QC & APA 7 Typography Audit",
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
    r"4\.12": {
        "name": "Stage 4.12: Committee Defense Viva Voce Simulation",
        "pipeline": "chapter4",
        "required_prerequisites": [
            r"Chapter_4_Results\.(?:docx|md)"
        ]
    },

    # ─── 2. Chapter 5 Pipeline (Discussion & Conclusion: Stages 5.1 – 5.10) ───
    r"5\.1": {
        "name": "Stage 5.1: Findings Overview & Purpose Recap",
        "pipeline": "chapter5",
        "required_prerequisites": [
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
    r"5\.3": {
        "name": "Stage 5.3: Unexpected / Non-Significant Findings Analysis",
        "pipeline": "chapter5",
        "required_prerequisites": [
            r"01_findings_recap\.(?:docx|md|json)"
        ]
    },
    r"5\.4": {
        "name": "Stage 5.4: Theoretical, Clinical & Practical Implications",
        "pipeline": "chapter5",
        "required_prerequisites": [
            r"02_hypothesis_1_discussion\.(?:docx|md|json)"
        ]
    },
    r"5\.5": {
        "name": "Stage 5.5: Methodological & Instrument Limitations",
        "pipeline": "chapter5",
        "required_prerequisites": [
            r"02_hypothesis_1_discussion\.(?:docx|md|json)"
        ]
    },
    r"5\.6": {
        "name": "Stage 5.6: Future Research & Recommendations",
        "pipeline": "chapter5",
        "required_prerequisites": [
            r"02_hypothesis_1_discussion\.(?:docx|md|json)"
        ]
    },
    r"5\.7": {
        "name": "Stage 5.7: Statistical Claim & Number Fidelity Audit",
        "pipeline": "chapter5",
        "required_prerequisites": [
            r"02_hypothesis_1_discussion\.(?:docx|md|json)"
        ]
    },
    r"5\.8": {
        "name": "Stage 5.8: Evidence Concordance & Citation Integrity Audit",
        "pipeline": "chapter5",
        "required_prerequisites": [
            r"02_hypothesis_1_discussion\.(?:docx|md|json)"
        ]
    },
    r"5\.9": {
        "name": "Stage 5.9: Chapter 5 Consolidation & Assembly",
        "pipeline": "chapter5",
        "required_prerequisites": [
            r"02_hypothesis_1_discussion\.(?:docx|md|json)"
        ]
    },
    r"5\.10": {
        "name": "Stage 5.10: Doctoral Defense Viva Voce Discussion Brief",
        "pipeline": "chapter5",
        "required_prerequisites": [
            r"Chapter_5_Discussion\.(?:docx|md)"
        ]
    },

    # ─── 3. Chapter 2 Pipeline (Literature Review: Stages 2.1 – 2.8) ───
    r"2\.1": {
        "name": "Stage 2.1: Theoretical Foundations & Conceptual Framework",
        "pipeline": "chapter2",
        "required_prerequisites": []
    },
    r"2\.2": {
        "name": "Stage 2.2: Bibliometric Network Analysis",
        "pipeline": "chapter2",
        "required_prerequisites": [
            r"01_theoretical_foundations\.(?:docx|md|json)"
        ]
    },
    r"2\.3": {
        "name": "Stage 2.3: International Empirical Studies",
        "pipeline": "chapter2",
        "required_prerequisites": [
            r"01_theoretical_foundations\.(?:docx|md|json)"
        ]
    },
    r"2\.4": {
        "name": "Stage 2.4: Iranian Empirical Studies",
        "pipeline": "chapter2",
        "required_prerequisites": [
            r"03_international_literature\.(?:docx|md|json)"
        ]
    },
    r"2\.5": {
        "name": "Stage 2.5: Epistemic Evidence Weighting & Synthesis",
        "pipeline": "chapter2",
        "required_prerequisites": [
            r"04_iranian_literature\.(?:docx|md|json)"
        ]
    },
    r"2\.6": {
        "name": "Stage 2.6: Summary Matrix Table",
        "pipeline": "chapter2",
        "required_prerequisites": [
            r"05_epistemic_synthesis\.(?:docx|md|json)"
        ]
    },
    r"2\.7": {
        "name": "Stage 2.7: Conceptual Model & Hypothesis Grounding",
        "pipeline": "chapter2",
        "required_prerequisites": [
            r"06_literature_matrix_table\.(?:docx|md|json)"
        ]
    },
    r"2\.8": {
        "name": "Stage 2.8: Chapter 2 OpenXML Assembly",
        "pipeline": "chapter2",
        "required_prerequisites": [
            r"07_conceptual_model_grounding\.(?:docx|md|json)"
        ]
    },

    # ─── 4. Research Proposal Pipeline (Stages P.1 – P.8) ───
    r"[Pp]\.1": {
        "name": "Stage P.1: Problem Statement & Background",
        "pipeline": "proposal",
        "required_prerequisites": []
    },
    r"[Pp]\.2": {
        "name": "Stage P.2: Research Significance & Objectives",
        "pipeline": "proposal",
        "required_prerequisites": [
            r"01_problem_statement\.(?:docx|md|json)"
        ]
    },
    r"[Pp]\.3": {
        "name": "Stage P.3: Research Questions & Hypotheses",
        "pipeline": "proposal",
        "required_prerequisites": [
            r"02_significance_and_objectives\.(?:docx|md|json)"
        ]
    },
    r"[Pp]\.4": {
        "name": "Stage P.4: Research Methodology & Design",
        "pipeline": "proposal",
        "required_prerequisites": [
            r"03_questions_and_hypotheses\.(?:docx|md|json)"
        ]
    },
    r"[Pp]\.5": {
        "name": "Stage P.5: Population, Sampling & Power (G*Power)",
        "pipeline": "proposal",
        "required_prerequisites": [
            r"04_methodology_and_design\.(?:docx|md|json)"
        ]
    },
    r"[Pp]\.6": {
        "name": "Stage P.6: Measurement Instruments & Psychometrics",
        "pipeline": "proposal",
        "required_prerequisites": [
            r"05_sampling_and_power\.(?:docx|md|json)"
        ]
    },
    r"[Pp]\.7": {
        "name": "Stage P.7: Implementation Procedure & Ethics",
        "pipeline": "proposal",
        "required_prerequisites": [
            r"06_measurement_instruments\.(?:docx|md|json)"
        ]
    },
    r"[Pp]\.8": {
        "name": "Stage P.8: Proposal Compilation & Assembly",
        "pipeline": "proposal",
        "required_prerequisites": [
            r"07_procedure_and_ethics\.(?:docx|md|json)"
        ]
    },

    # ─── 5. Psychometric Scale Validation (Stages V.1 – V.9) ───
    r"[Vv]\.1": {
        "name": "Stage V.1: Content & Face Validity (CVR / CVI)",
        "pipeline": "scale_validation",
        "required_prerequisites": []
    },
    r"[Vv]\.2": {
        "name": "Stage V.2: Item Analysis & Screening",
        "pipeline": "scale_validation",
        "required_prerequisites": [
            r"01_content_validity\.(?:docx|md|json)"
        ]
    },
    r"[Vv]\.3": {
        "name": "Stage V.3: Exploratory Factor Analysis (EFA)",
        "pipeline": "scale_validation",
        "required_prerequisites": [
            r"02_item_analysis\.(?:docx|md|json)"
        ]
    },
    r"[Vv]\.4": {
        "name": "Stage V.4: Confirmatory Factor Analysis (CFA)",
        "pipeline": "scale_validation",
        "required_prerequisites": [
            r"03_efa_analysis\.(?:docx|md|json)"
        ]
    },
    r"[Vv]\.5": {
        "name": "Stage V.5: Construct Validity (AVE, CR, HTMT)",
        "pipeline": "scale_validation",
        "required_prerequisites": [
            r"04_cfa_analysis\.(?:docx|md|json)"
        ]
    },
    r"[Vv]\.6": {
        "name": "Stage V.6: Measurement Invariance",
        "pipeline": "scale_validation",
        "required_prerequisites": [
            r"05_construct_validity\.(?:docx|md|json)"
        ]
    },
    r"[Vv]\.7": {
        "name": "Stage V.7: Reliability Analysis",
        "pipeline": "scale_validation",
        "required_prerequisites": [
            r"05_construct_validity\.(?:docx|md|json)"
        ]
    },
    r"[Vv]\.8": {
        "name": "Stage V.8: Item Response Theory (IRT) & ROC Curves",
        "pipeline": "scale_validation",
        "required_prerequisites": [
            r"07_reliability_analysis\.(?:docx|md|json)"
        ]
    },
    r"[Vv]\.9": {
        "name": "Stage V.9: Validation Report Assembly & Test Manual",
        "pipeline": "scale_validation",
        "required_prerequisites": [
            r"08_irt_and_roc\.(?:docx|md|json)"
        ]
    },

    # ─── 6. Defense Presentation Pipeline (Stages D.0 – D.7) ───
    r"[Dd]\.0": {
        "name": "Stage D.0: Findings Ingestion & Verification",
        "pipeline": "defense_presentation",
        "required_prerequisites": []
    },
    r"[Dd]\.1": {
        "name": "Stage D.1: Storyboard & 14-Slide Architecture",
        "pipeline": "defense_presentation",
        "required_prerequisites": [
            r"00_defense_findings_payload\.json"
        ]
    },
    r"[Dd]\.2": {
        "name": "Stage D.2: Dedicated Statistical & Hypothesis Triads",
        "pipeline": "defense_presentation",
        "required_prerequisites": [
            r"01_defense_storyboard\.(?:docx|md|json)"
        ]
    },
    r"[Dd]\.3": {
        "name": "Stage D.3: Deterministic Deck Compilation",
        "pipeline": "defense_presentation",
        "required_prerequisites": [
            r"02_hypothesis_slides\.(?:docx|md|json)"
        ]
    },
    r"[Dd]\.4": {
        "name": "Stage D.4: Publication Structural Diagram",
        "pipeline": "defense_presentation",
        "required_prerequisites": [
            r"02_hypothesis_slides\.(?:docx|md|json)"
        ]
    },
    r"[Dd]\.5": {
        "name": "Stage D.5: Candidate Defense Script & Q&A Guide",
        "pipeline": "defense_presentation",
        "required_prerequisites": [
            r"02_hypothesis_slides\.(?:docx|md|json)"
        ]
    },
    r"[Dd]\.6": {
        "name": "Stage D.6: Geometry Collision & Typography Audit",
        "pipeline": "defense_presentation",
        "required_prerequisites": [
            r"(?:Defense_Presentation\.pptx|presentation\.html)"
        ]
    },
    r"[Dd]\.7": {
        "name": "Stage D.7: Committee Viva Voce Oral Defense Simulation",
        "pipeline": "defense_presentation",
        "required_prerequisites": [
            r"05_presentation_qa_audit\.(?:json|md)"
        ]
    },

    # ─── 7. Empirical Data Generation & Simulation (Stages DS.0 – DS.5) ───
    r"[Dd][Ss]\.0": {
        "name": "Stage DS.0: Pre-Execution Model Blueprint & Confirmation Gate",
        "pipeline": "data_simulation",
        "required_prerequisites": []
    },
    r"[Dd][Ss]\.1": {
        "name": "Stage DS.1: Simulation Specification & Power Analysis",
        "pipeline": "data_simulation",
        "required_prerequisites": [
            r"00_model_blueprint\.(?:docx|md|json)"
        ]
    },
    r"[Dd][Ss]\.2": {
        "name": "Stage DS.2: Instrument Grounding & Factor Weights",
        "pipeline": "data_simulation",
        "required_prerequisites": [
            r"01_simulation_spec\.(?:docx|md|json)"
        ]
    },
    r"[Dd][Ss]\.3": {
        "name": "Stage DS.3: Monte Carlo Simulation & Model Synthesis",
        "pipeline": "data_simulation",
        "required_prerequisites": [
            r"02_scales_codebook\.(?:docx|md|json)"
        ]
    },
    r"[Dd][Ss]\.4": {
        "name": "Stage DS.4: Data Quality & Anomaly Screening",
        "pipeline": "data_simulation",
        "required_prerequisites": [
            r"(?:primary_data\.xlsx|final_data\.xlsx|03_simulation_results\.json)"
        ]
    },
    r"[Dd][Ss]\.5": {
        "name": "Stage DS.5: Data Curation, Codebook & Provenance Handoff",
        "pipeline": "data_simulation",
        "required_prerequisites": [
            r"04_data_audit_report\.(?:docx|md|json)"
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
    """Matches a stage string to canonical stage prerequisites across all 7 pipelines."""
    if not stage_str or not isinstance(stage_str, str):
        return None

    # Match stage numbers (e.g. 'DS.1', 'D.3', 'V.4', 'P.2', '4.6.1', '2.3', '5.2')
    m = re.search(r'\b(DS\.\d+|D\.\d+|V\.\d+|P\.\d+|[245]\.\d+(?:\.\d+)?)\b', stage_str, re.IGNORECASE)
    if not m:
        return None

    stage_num = m.group(1).upper()
    for pattern, spec in CANONICAL_STAGE_PREREQUISITES.items():
        if re.fullmatch(pattern, stage_num, re.IGNORECASE):
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
        return True, f"Initial stage {spec.get('name')} requires no prior stage artifacts."

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
        # Test Stage DS.3 without Stage DS.2 codebook
        ok, reason = verify_pipeline_stage_prerequisites("Stage DS.3: Monte Carlo Simulation", [td])
        print("Stage DS.3 without prereq:", ok)
        assert not ok

        # Test Stage P.5 without Stage P.4 design
        ok, reason = verify_pipeline_stage_prerequisites("Stage P.5: G*Power Sampling", [td])
        print("Stage P.5 without prereq:", ok)
        assert not ok

        # Create prerequisite for P.5
        with open(os.path.join(td, "04_methodology_and_design.json"), "w") as f:
            f.write("{}")

        ok2, reason2 = verify_pipeline_stage_prerequisites("Stage P.5: G*Power Sampling", [td])
        print("Stage P.5 with prereq:", ok2)
        assert ok2
