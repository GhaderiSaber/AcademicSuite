#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
multi_agent_orchestrator.py — Antigravity Native Multi-Agent Deliberation Driver

Connects the deterministic statistical engines with Antigravity's native `invoke_subagent`
orchestration layer per `.agents/architecture/HYBRID_MULTI_AGENT_SPEC.md`.

Provides:
  1. Subagent Task Packet Generators (`generate_subagent_task_packet`)
  2. Critique & Defense Schema Validation
  3. Viva Voce Committee Cross-Examination Protocol Scaffolding
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
AGENTS_DIR = os.path.join(ROOT_DIR, '.agents')


class MultiAgentOrchestrator:
    """Manages task packets, contracts, and schema validation for native Antigravity subagents."""

    ROLES = [
        "methodology-expert",
        "statistical-expert",
        "statistical-auditor",
        "results-auditor",
        "academic-writer",
        "evidence-auditor",
        "final-judge",
        "digital-saber"
    ]

    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = workspace_root or ROOT_DIR
        self.agents_dir = os.path.join(self.workspace_root, '.agents')

    def generate_task_packet(self, workflow: str, role: str, context_dir: str = "output") -> Dict[str, Any]:
        """
        Generates the actionable task packet for an Antigravity subagent invocation.
        This provides the subagent with its bounded scope, input artifacts to view_file,
        and expected JSON return schema.
        """
        context_path = os.path.abspath(os.path.join(self.workspace_root, context_dir))
        stats_results_file = os.path.join(context_path, "stats_results.json")
        ch4_docx = os.path.join(context_path, "Chapter_4_Results.docx")
        study_config_file = os.path.join(context_path, "study_config.json")

        base_packet = {
            "workflow": workflow,
            "target_role": role,
            "generated_at": datetime.now().isoformat(),
            "workspace_root": self.workspace_root,
            "context_dir": context_path
        }

        # Handle Thesis Revision & Examiner Rebuttal Workflow
        if workflow.lower() in ("thesis_revision", "revision"):
            triaged_file = os.path.join(context_path, "triaged_comments.json")
            resolved_file = os.path.join(context_path, "resolved_comments.json")
            stats_audit_file = os.path.join(context_path, "revision_stats_audit.json")
            clearance_file = os.path.join(context_path, "committee_clearance_report.json")
            rebuttal_docx = os.path.join(context_path, "Revision_Response_Table.docx")

            if role == "results-auditor":
                return {
                    **base_packet,
                    "role_title": "Format & APA 7 Revision Auditor",
                    "mandate": "Audit Tier 1 formatting comments, table borders (3 horizontal lines, 0 vertical lines), Persian leading zeros (۰.۰۰۱), and OpenXML BiDi RTL.",
                    "artifacts_to_inspect": [triaged_file, rebuttal_docx],
                    "instructions": [
                        f"Call view_file on {triaged_file} and verify all Tier 1 comments.",
                        "Confirm that all revised tables follow APA 7 (zero vertical borders, exactly 3 horizontal borders).",
                        "Verify Persian leading zero rule: always '۰.۰۰۱' or '۰.۰۵', never '.۰۰۱'.",
                        "Confirm OpenXML BiDi RTL (<w:bidiVisual/>) on the response table.",
                        "Return a JSON QC checklist."
                    ],
                    "expected_return_schema": {
                        "format_audit_passed": True,
                        "leading_zero_concordance": True,
                        "table_borders_apa7": True,
                        "defects_found": []
                    }
                }

            elif role == "statistical-auditor":
                return {
                    **base_packet,
                    "role_title": "Statistical Recalculation & Assumption Auditor",
                    "mandate": "Audit Tier 2 statistical recalculations (regression slope homogeneity, normality, degrees of freedom, effect sizes) against stats_results.json.",
                    "artifacts_to_inspect": [stats_results_file, stats_audit_file],
                    "instructions": [
                        f"Inspect calculated metrics in {stats_audit_file} and {stats_results_file}.",
                        "Verify degrees of freedom concordance and slope homogeneity test (F, df, p-value).",
                        "Audit Multi-Signal Anomaly Index (MSAI) score.",
                        "Return a JSON statistical recalculation audit report."
                    ],
                    "expected_return_schema": {
                        "audit_verdict": "string",
                        "degrees_of_freedom_verified": True,
                        "slope_homogeneity_verified": True,
                        "recalculation_fidelity": True
                    }
                }

            elif role == "academic-writer":
                return {
                    **base_packet,
                    "role_title": "Academic Rebuttal Drafter & Etiquette Specialist",
                    "mandate": "Draft and audit polite, respectful Persian academic responses (academic_rebuttal_etiquette_fa.md) with exact thesis page references.",
                    "artifacts_to_inspect": [resolved_file],
                    "instructions": [
                        f"Inspect resolved comments in {resolved_file}.",
                        "Verify that responses strictly adhere to academic etiquette (e.g., «با تشکر و امتنان فراوان از دقت نظر استاد محترم...»).",
                        "Confirm exact page and table references are provided for every single comment.",
                        "Return a JSON evaluation with rebuttal_etiquette_approved and comments_audited."
                    ],
                    "expected_return_schema": {
                        "rebuttal_etiquette_approved": True,
                        "all_pages_referenced": True,
                        "persian_typography_valid": True,
                        "comments_audited": 14
                    }
                }

            elif role == "final-judge":
                return {
                    **base_packet,
                    "role_title": "Thesis Defense Committee Clearance Judge",
                    "mandate": "Evaluate supervisor and examiner comment resolution completeness, compute committee clearance score (0-100), and issue sign-off verdict.",
                    "artifacts_to_inspect": [clearance_file, resolved_file],
                    "instructions": [
                        f"Inspect {clearance_file} and {resolved_file}.",
                        "Verify 100% resolution coverage across all tiers (Format, Stats, Theory).",
                        "Confirm committee sign-off readiness score (0-100%).",
                        "Issue clearance verdict: APPROVED_FOR_SIGN_OFF or FURTHER_REVISIONS_REQUIRED."
                    ],
                    "expected_return_schema": {
                        "verdict": "APPROVED_FOR_SIGN_OFF",
                        "readiness_score": 99.0,
                        "resolution_rate": 100.0,
                        "clearance_summary": "string"
                    }
                }

        # Default / Chapter 4 Workflow Handling
        if role == "methodology-expert":
            return {
                **base_packet,
                "role_title": "Methodology Reviewer & Power Auditor",
                "mandate": "Evaluate research design classification, internal validity threats, and G*Power sample size adequacy.",
                "artifacts_to_inspect": [study_config_file],
                "instructions": [
                    f"Call view_file on {study_config_file} to examine design parameters.",
                    "Verify whether the sample size satisfies Cohen's power threshold (1 - beta >= 0.80).",
                    "Audit baseline equivalence and threats such as regression to the mean or history effects.",
                    "Return a JSON summary with 'methodology_approved', 'threats_identified', and 'recommendations'."
                ],
                "expected_return_schema": {
                    "methodology_approved": True,
                    "design_classification": "string",
                    "power_adequate": True,
                    "threats_identified": ["string"],
                    "recommendations": ["string"]
                }
            }

        elif role == "statistical-auditor":
            return {
                **base_packet,
                "role_title": "Adversarial Statistical Auditor & MSAI Checker",
                "mandate": "Audit statistical assumptions, degrees of freedom concordance, and Multi-Signal Anomaly Index.",
                "artifacts_to_inspect": [stats_results_file],
                "instructions": [
                    f"Call view_file on {stats_results_file} to inspect real calculated metrics.",
                    "Verify degrees of freedom concordance: df_between + df_within == N - 1.",
                    "Check regression slope homogeneity test and variance inflation ratio.",
                    "Compute MSAI anomaly verdict (NORMAL_EMPIRICAL, FLAG_FOR_REVIEW, or ANOMALOUS).",
                    "Return a JSON audit report."
                ],
                "expected_return_schema": {
                    "audit_verdict": "string",
                    "degrees_of_freedom_verified": True,
                    "slope_homogeneity_verified": True,
                    "anomaly_index": 0,
                    "audit_notes": ["string"]
                }
            }

        elif role == "results-auditor":
            return {
                **base_packet,
                "role_title": "APA 7 & OpenXML Quality Control Auditor",
                "mandate": "Audit APA 7th Edition numerical precision, Persian leading zero rule, and Word OMML math preservation.",
                "artifacts_to_inspect": [stats_results_file, ch4_docx],
                "instructions": [
                    f"Call view_file on {stats_results_file} and verify concordance with {ch4_docx}.",
                    "Check for Persian leading zero rule: always '۰.۰۰۱' or '۰.۰۵', never '.۰۰۱'.",
                    "Ensure zero instances of 'p = .000'; must be 'p < .001' (یا '۰.۰۰۱ > p').",
                    "Verify 3-line borderless table format and native OMML math equation preservation.",
                    "Return a JSON QC checklist."
                ],
                "expected_return_schema": {
                    "qc_passed": True,
                    "leading_zero_concordance": True,
                    "p_value_formatting_valid": True,
                    "omml_math_preserved": True,
                    "defects_found": []
                }
            }

        elif role == "final-judge":
            return {
                **base_packet,
                "role_title": "Viva Voce Defense Examiner & Release Gatekeeper",
                "mandate": "Simulate adversarial defense committee cross-examination and evaluate dissertation readiness score (0-100).",
                "artifacts_to_inspect": [stats_results_file, ch4_docx],
                "instructions": [
                    f"Inspect findings in {stats_results_file}.",
                    "Formulate 3 sharp, challenging Viva Voce defense questions attacking potential design limitations.",
                    "Evaluate the candidate's model answers against academic literature standards.",
                    "Calculate dissertation defense readiness score (0-100).",
                    "Issue release clearance verdict: APPROVED_FOR_DEFENSE or REVISIONS_REQUIRED."
                ],
                "expected_return_schema": {
                    "verdict": "APPROVED_FOR_DEFENSE",
                    "defense_readiness_score": 95.0,
                    "viva_voce_challenges": [
                        {"question": "string", "focus": "string", "model_defense": "string"}
                    ],
                    "examiner_remarks": "string"
                }
            }

        elif role == "academic-writer":
            return {
                **base_packet,
                "role_title": "Master Academic Prose Drafter & Persian Rhetorician",
                "mandate": "Draft or refine defense-ready Persian academic narrative using 5-part epistemic paragraph structure.",
                "artifacts_to_inspect": [stats_results_file],
                "instructions": [
                    f"Inspect exact values from {stats_results_file}.",
                    "Ensure every paragraph strictly follows: 1) Claim, 2) Empirical Evidence, 3) Statistical Binding, 4) Theoretical Mechanism, 5) Epistemic Nuance.",
                    "Enforce Persian half-spaces (\\u200c) and authentic scholarly tone.",
                    "Never hallucinate numbers; copy exact statistics from JSON."
                ],
                "expected_return_schema": {
                    "draft_complete": True,
                    "epistemic_paragraphs_count": 5,
                    "cadence_variance_cv": 0.68,
                    "cliches_purged": True
                }
            }

        else:
            return {
                **base_packet,
                "role_title": f"Subagent {role}",
                "mandate": f"Execute specialized cognitive assessment for role {role}.",
                "artifacts_to_inspect": [stats_results_file],
                "instructions": ["Inspect context artifacts and return structured feedback."]
            }

    def validate_critique_payload(self, role: str, payload: Dict[str, Any], workflow: str = "chapter4") -> Tuple[bool, List[str]]:
        """Validates that a subagent returned the required schema fields."""
        errors = []
        is_rev = workflow.lower() in ("thesis_revision", "revision")
        if role == "methodology-expert":
            for k in ["methodology_approved", "power_adequate"]:
                if k not in payload:
                    errors.append(f"Missing required key '{k}' in methodology critique.")
        elif role == "statistical-auditor":
            for k in ["audit_verdict", "degrees_of_freedom_verified"]:
                if k not in payload:
                    errors.append(f"Missing required key '{k}' in statistical auditor critique.")
        elif role == "results-auditor":
            if is_rev:
                for k in ["format_audit_passed", "leading_zero_concordance"]:
                    if k not in payload:
                        errors.append(f"Missing required key '{k}' in results auditor revision checklist.")
            else:
                for k in ["qc_passed", "leading_zero_concordance"]:
                    if k not in payload:
                        errors.append(f"Missing required key '{k}' in results auditor QC checklist.")
        elif role == "academic-writer":
            if is_rev:
                for k in ["rebuttal_etiquette_approved", "all_pages_referenced"]:
                    if k not in payload:
                        errors.append(f"Missing required key '{k}' in academic writer rebuttal audit.")
            else:
                for k in ["draft_complete"]:
                    if k not in payload:
                        errors.append(f"Missing required key '{k}' in academic writer draft status.")
        elif role == "final-judge":
            if is_rev:
                for k in ["verdict", "readiness_score"]:
                    if k not in payload:
                        errors.append(f"Missing required key '{k}' in final judge clearance verdict.")
            else:
                for k in ["verdict", "defense_readiness_score"]:
                    if k not in payload:
                        errors.append(f"Missing required key '{k}' in final judge defense verdict.")
        return len(errors) == 0, errors


def main():
    parser = argparse.ArgumentParser(description="Antigravity Native Multi-Agent Deliberation Driver")
    parser.add_argument("--generate-packets", metavar="WORKFLOW", help="Generate subagent task packets for workflow (e.g., chapter4)")
    parser.add_argument("--role", choices=MultiAgentOrchestrator.ROLES, help="Target subagent role")
    parser.add_argument("--context-dir", default="output", help="Directory containing input artifacts")
    args = parser.parse_args()

    orchestrator = MultiAgentOrchestrator()

    if args.generate_packets:
        roles_to_gen = [args.role] if args.role else ["methodology-expert", "statistical-auditor", "results-auditor", "final-judge"]
        print("=" * 80)
        print(f"📦 GENERATING SUBAGENT TASK PACKETS FOR WORKFLOW: [{args.generate_packets.upper()}]")
        print("=" * 80)
        for r in roles_to_gen:
            packet = orchestrator.generate_task_packet(args.generate_packets, r, context_dir=args.context_dir)
            print(f"\n[Role: {r}] -> Title: {packet.get('role_title')}")
            print(f"  • Mandate: {packet.get('mandate')}")
            print(f"  • Artifacts to inspect: {packet.get('artifacts_to_inspect')}")
            print(f"  • Instructions count: {len(packet.get('instructions', []))}")
        print("\n" + "=" * 80)
        print("✅ ALL TASK PACKETS GENERATED SUCCESSFULLY!")
        print("=" * 80)
    else:
        parser.print_help()


if __name__ == "__main__":
    from typing import Tuple
    main()
