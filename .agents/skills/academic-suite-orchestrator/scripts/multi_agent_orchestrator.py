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
        "literature-expert",
        "evidence-auditor",
        "final-judge",
        "digital-saber",
        "psychometric-expert",
        "qualitative-analyst",
        "meta-analyst",
        "journal-strategist",
        "intervention-designer"
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
            "task_id": f"{workflow}-{role}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "role": role,
            "target_role": role,
            "workflow": workflow,
            "stage": workflow,
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

        elif role == "psychometric-expert":
            psychometrics_report = os.path.join(context_path, "psychometric_validation_report.json")
            return {
                **base_packet,
                "role_title": "Psychometrician & Construct Validation Specialist",
                "mandate": "Audit psychometric construct validity, CFA factor loadings, CTT reliability (alpha/omega), and CVR/CVI content validity.",
                "artifacts_to_inspect": [psychometrics_report],
                "instructions": [
                    f"Call view_file on {psychometrics_report} to verify psychometric properties.",
                    "Verify item factor loadings (lambda >= 0.40) and global fit indices (CFI >= 0.90, RMSEA <= 0.08).",
                    "Confirm convergent validity (AVE >= 0.50, CR >= 0.70) and reliability (alpha >= 0.70, omega >= 0.70).",
                    "Return a JSON summary with 'psychometrics_valid', 'cfa_fit_adequate', and 'reliability_verified'."
                ],
                "expected_return_schema": {
                    "psychometrics_valid": True,
                    "cfa_fit_adequate": True,
                    "reliability_verified": True,
                    "flagged_items": []
                }
            }

        elif role == "qualitative-analyst":
            qual_findings = os.path.join(context_path, "Chapter_4_Qualitative_Findings.docx")
            return {
                **base_packet,
                "role_title": "Qualitative Research & Thematic Analysis Specialist",
                "mandate": "Audit 6-phase reflexive thematic analysis, 3-tier theme hierarchy, inter-coder reliability, and Lincoln & Guba trustworthiness.",
                "artifacts_to_inspect": [qual_findings],
                "instructions": [
                    f"Inspect qualitative findings in {qual_findings}.",
                    "Verify 3-tier thematic hierarchy (Basic -> Organizing -> Global Themes).",
                    "Audit inter-coder reliability (Holsti PAO >= 80%, Cohen's Kappa >= 0.70).",
                    "Verify Lincoln & Guba 4-pillar trustworthiness audit (Credibility, Transferability, Dependability, Confirmability).",
                    "Return a JSON qualitative audit report."
                ],
                "expected_return_schema": {
                    "thematic_structure_valid": True,
                    "inter_coder_agreement_percent": 85.0,
                    "trustworthiness_audit_passed": True,
                    "themes_count": {"basic": 24, "organizing": 6, "global": 2}
                }
            }

        elif role == "meta-analyst":
            meta_report = os.path.join(context_path, "meta_analysis_report.json")
            return {
                **base_packet,
                "role_title": "Systematic Review & Quantitative Meta-Analyst",
                "mandate": "Audit PRISMA 2020 study flow, Cochrane RoB 2 risk of bias assessments, pooled effect sizes, heterogeneity (I^2), and publication bias.",
                "artifacts_to_inspect": [meta_report],
                "instructions": [
                    f"Call view_file on {meta_report} to examine pooled effect estimates.",
                    "Verify Cochrane RoB 2 domain assessments across included trials.",
                    "Audit heterogeneity indices (Cochran's Q, I^2, tau^2) and random-effects pooling.",
                    "Verify publication bias diagnostics (Egger's regression, Funnel plot asymmetry).",
                    "Return a JSON meta-analysis audit report."
                ],
                "expected_return_schema": {
                    "prisma_flow_compliant": True,
                    "pooled_effect_significant": True,
                    "heterogeneity_level": "moderate",
                    "publication_bias_detected": False
                }
            }

        elif role == "journal-strategist":
            submission_manifest = os.path.join(context_path, "submission_manifest.json")
            return {
                **base_packet,
                "role_title": "Publication Packaging & Peer-Review Rebuttal Strategist",
                "mandate": "Audit IMRaD manuscript packaging, 14 CRediT roles, character-capped highlights (<= 85 chars), and journal scope fit.",
                "artifacts_to_inspect": [submission_manifest],
                "instructions": [
                    f"Call view_file on {submission_manifest} to verify submission collateral.",
                    "Verify Editor-in-Chief Cover Letter and 14 CRediT authorship declarations.",
                    "Check highlights bullet points: each must strictly be <= 85 characters.",
                    "Confirm target journal alignment (ISI/Scopus Q1/Q2 or Persian ISC).",
                    "Return a JSON journal packaging clearance report."
                ],
                "expected_return_schema": {
                    "imrad_structure_compliant": True,
                    "credit_roles_assigned": 14,
                    "highlights_within_limit": True,
                    "target_journal_aligned": True
                }
            }

        elif role == "intervention-designer":
            protocol_spec = os.path.join(context_path, "intervention_protocol_spec.json")
            return {
                **base_packet,
                "role_title": "Psychological Intervention Protocol Architect",
                "mandate": "Verify 8-12 session evidence-based intervention manual, standardized session anatomy, and treatment fidelity checklists.",
                "artifacts_to_inspect": [protocol_spec],
                "instructions": [
                    f"Inspect protocol specifications in {protocol_spec}.",
                    "Verify standardized 6-part session anatomy (Objective, Rationale, Metaphor, Exercise, Worksheet, Homework).",
                    "Confirm Chapter 3 APA 7 borderless session summary table.",
                    "Audit treatment adherence and therapist fidelity checklists.",
                    "Return a JSON protocol architecture audit report."
                ],
                "expected_return_schema": {
                    "protocol_sessions_count": 8,
                    "session_anatomy_complete": True,
                    "treatment_fidelity_verified": True,
                    "apa7_summary_table": True
                }
            }

        elif role == "literature-expert":
            lit_notes = os.path.join(context_path, "literature_summary.json")
            return {
                **base_packet,
                "role_title": "Literature & Epistemic Evidence Synthesizer",
                "mandate": "Conduct multi-database literature search, extract empirical parameters (N, design, scales), and synthesize theoretical mechanisms.",
                "artifacts_to_inspect": [lit_notes],
                "instructions": [
                    "Examine empirical literature harvested across PubMed, Scopus, SID, and Magiran.",
                    "Ensure anti-cherry-picking covenant: synthesize both domestic and international trials.",
                    "Synthesize psychological mechanisms for Chapter 2 and Chapter 5.",
                    "Return a JSON literature synthesis report."
                ],
                "expected_return_schema": {
                    "studies_harvested": 10,
                    "epistemic_evidence_weight": "STRONG",
                    "mechanisms_synthesized": True
                }
            }

        elif role == "evidence-auditor":
            audit_matrix = os.path.join(context_path, "citation_reconciliation_matrix.xlsx")
            return {
                **base_packet,
                "role_title": "Epistemic Integrity & Citation Auditor",
                "mandate": "Audit bidirectional in-text to reference concordance, verify DOIs/PMIDs, and predict Irandoc similarity (< 20%).",
                "artifacts_to_inspect": [audit_matrix],
                "instructions": [
                    "Reconcile in-text citations against bibliography (zero ghost references or orphaned citations).",
                    "Check Irandoc similarity estimation (< 20%).",
                    "Ensure AI cliches and robotic translationese are purged.",
                    "Return a JSON evidence audit report."
                ],
                "expected_return_schema": {
                    "citation_concordance_rate": 100.0,
                    "irandoc_similarity_predicted": 12.5,
                    "ghost_citations_detected": 0
                }
            }

        elif role == "statistical-expert":
            return {
                **base_packet,
                "role_title": "Statistical Analysis Planner & Hypothesis Evaluator",
                "mandate": "Formulate statistical analysis strategy, evaluate parametric assumptions, and report test statistics.",
                "artifacts_to_inspect": [stats_results_file, study_config_file],
                "instructions": [
                    f"Call view_file on {stats_results_file} and {study_config_file}.",
                    "Verify statistical hypothesis testing plan (ANCOVA, Repeated Measures, SEM, t-tests).",
                    "Verify assumption checks (Normality, Homogeneity of Variance, Slope Homogeneity).",
                    "Return a JSON summary with 'primary_analysis_type', 'assumptions_met', and 'hypotheses_evaluated'."
                ],
                "expected_return_schema": {
                    "primary_analysis_type": "ANCOVA",
                    "assumptions_met": True,
                    "hypotheses_evaluated": True
                }
            }

        elif role == "digital-saber":
            return {
                **base_packet,
                "role_title": "Master Cognitive Architect & Research Lead",
                "mandate": "Oversee end-to-end dissertation pipeline, arbitrate inter-agent deliberations, and gate final release.",
                "artifacts_to_inspect": [stats_results_file, ch4_docx],
                "instructions": [
                    "Oversee stage progression and verify Directive 3 artifact checkpoints.",
                    "Arbitrate disputes between authors and adversarial auditors.",
                    "Enforce APA 7 typography and OpenXML Persian styling standards.",
                    "Return orchestration verdict and milestone sign-off."
                ],
                "expected_return_schema": {
                    "orchestration_status": "COMPLETED",
                    "workflow_verdict": "APPROVED"
                }
            }

        else:
            return {
                **base_packet,
                "role_title": f"Subagent {role}",
                "mandate": f"Execute specialized cognitive assessment for role {role}.",
                "artifacts_to_inspect": [stats_results_file],
                "instructions": ["Inspect context artifacts and return structured feedback."],
                "expected_return_schema": {
                    "verdict": "string",
                    "evaluation_summary": "string"
                }
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
        elif role == "psychometric-expert":
            for k in ["psychometrics_valid", "reliability_verified"]:
                if k not in payload:
                    errors.append(f"Missing required key '{k}' in psychometric expert audit.")
        elif role == "qualitative-analyst":
            for k in ["thematic_structure_valid", "trustworthiness_audit_passed"]:
                if k not in payload:
                    errors.append(f"Missing required key '{k}' in qualitative analyst audit.")
        elif role == "meta-analyst":
            for k in ["prisma_flow_compliant", "pooled_effect_significant"]:
                if k not in payload:
                    errors.append(f"Missing required key '{k}' in meta-analyst audit.")
        elif role == "journal-strategist":
            for k in ["imrad_structure_compliant", "highlights_within_limit"]:
                if k not in payload:
                    errors.append(f"Missing required key '{k}' in journal strategist report.")
        elif role == "intervention-designer":
            for k in ["protocol_sessions_count", "session_anatomy_complete"]:
                if k not in payload:
                    errors.append(f"Missing required key '{k}' in intervention protocol audit.")
        elif role == "literature-expert":
            for k in ["epistemic_evidence_weight"]:
                if k not in payload:
                    errors.append(f"Missing required key '{k}' in literature expert report.")
        elif role == "evidence-auditor":
            for k in ["citation_concordance_rate"]:
                if k not in payload:
                    errors.append(f"Missing required key '{k}' in evidence auditor report.")
        elif role == "statistical-expert":
            for k in ["primary_analysis_type", "assumptions_met"]:
                if k not in payload:
                    errors.append(f"Missing required key '{k}' in statistical expert report.")
        elif role == "digital-saber":
            for k in ["orchestration_status", "workflow_verdict"]:
                if k not in payload:
                    errors.append(f"Missing required key '{k}' in digital saber orchestration status.")
        else:
            for k in ["verdict"]:
                if k not in payload:
                    errors.append(f"Missing required key '{k}' in {role} critique.")
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
