#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/academic_independent_evaluator.py — Independent Blinded A/B Multi-Task Evaluator

Architectural Mandate (Phase 23):
Do not let the candidate generate its own evidence.
Bad:
  candidate -> candidate says "improved" -> promotion
Better:
  Baseline Agent  --> [Task A, Task B, Task C]
  Candidate Agent --> [Task A, Task B, Task C]
  Independent Evaluator (Blinded A/B) -> Compare

Key Invariants:
1. Multi-Task Benchmark Panel: Both Baseline and Candidate execute the exact same tasks.
2. Blinded A/B Grading: Evaluator grades 'Submission A' and 'Submission B' without knowing
   which output is the candidate and which is the baseline.
3. Payload Sanitization: Strips candidate IDs, version strings, sandbox paths, and self-assertions.
4. Objective 8-Dimensional Verification: Grades correctness, methodology, statistical validity,
   evidence grounding, integrity, robustness, consistency, and efficiency.
5. Post-Evaluation Unblinding: Decodes mapping and computes authentic comparative metrics
   (defect_resolved, candidate_outperformed_baseline, zero_regressions_verified).
"""

import os
import sys
import json
import uuid
import copy
import random
import hashlib
import argparse
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple, Set

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

# Fallback to system dist-packages
for p in ["/usr/lib/python3/dist-packages", "/usr/local/lib/python3/dist-packages"]:
    if os.path.exists(p) and p not in sys.path:
        sys.path.append(p)

from contracts.contract_validator import (
    validate_independent_evaluation,
    validate_evaluation_case
)
from scripts.academic_evaluation_lab import AcademicEvaluationLab, HeldoutTamperingError


class SelfEvaluationBlockedError(Exception):
    """Raised when a candidate attempts to self-evaluate, self-declare improvement, or bypass independent evaluation."""
    pass


class IndependentEvaluationError(Exception):
    """Raised when independent evaluation encounters an invalid state or execution failure."""
    pass


class AcademicIndependentEvaluator:
    """
    Independent Evaluator conducting blinded A/B comparisons between Baseline and Candidate agents
    across standardized multi-task benchmark panels.
    """

    DIMENSIONS = AcademicEvaluationLab.DIMENSIONS

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = os.path.abspath(base_dir or ROOT_DIR)
        self.eval_root = os.path.join(self.base_dir, "learning", "evaluations")
        self.independent_dir = os.path.join(self.eval_root, "independent")
        self.lab = AcademicEvaluationLab(base_dir=self.base_dir)

        os.makedirs(self.independent_dir, exist_ok=True)

    # -------------------------------------------------------------------------
    # 1. Multi-Task Benchmark Panel Assembly
    # -------------------------------------------------------------------------

    def build_task_panel(
        self,
        capability: str,
        failure_signature: Optional[str] = None,
        custom_cases: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Assembles a standardized multi-task benchmark panel:
        - Task A: TARGET_DEFECT (the motivating failure scenario)
        - Task B: RELATED_CAPABILITY (generalization test on the same capability)
        - Task C: REGRESSION_GUARD (permanent regression scenario protecting baseline capabilities)
        """
        if custom_cases and len(custom_cases) >= 2:
            panel = []
            for i, c in enumerate(custom_cases):
                task_type = "TARGET_DEFECT" if i == 0 else ("RELATED_CAPABILITY" if i == 1 else "REGRESSION_GUARD")
                panel.append({
                    "task_id": c.get("case_id", f"TASK-{chr(65 + i)}"),
                    "name": c.get("name", f"Benchmark Task {chr(65 + i)}"),
                    "type": c.get("task_type", task_type),
                    "description": c.get("description", f"Evaluation benchmark task {chr(65 + i)} for {capability}"),
                    "expected_properties": c.get("expected_properties", {}),
                    "forbidden_behaviors": c.get("forbidden_behaviors", ["p_equals_point_zero_zero_zero"]),
                    "inputs": c.get("inputs", {})
                })
            return panel

        # Discover existing cases from evaluation lab
        all_cases = self.lab.load_cases(include_retired=False)
        rel_cases = [c for c in all_cases if c.get("capability", "").lower() == capability.lower()]
        reg_cases = [c for c in all_cases if c.get("suite_type") == "regression"]

        panel = []

        # Task A: Motivating defect
        target_case = None
        if failure_signature:
            for c in rel_cases + all_cases:
                if failure_signature.lower() in str(c.get("forbidden_behaviors", [])).lower() or \
                   failure_signature.lower() in str(c.get("tags", [])).lower():
                    target_case = c
                    break
        if not target_case:
            target_case = rel_cases[0] if rel_cases else (all_cases[0] if all_cases else None)

        panel.append({
            "task_id": "TASK-A",
            "name": f"Target Defect Resolution: {failure_signature or 'Primary Task'}",
            "type": "TARGET_DEFECT",
            "description": f"Verifies whether candidate eliminates defect '{failure_signature or 'target_defect'}' without error.",
            "expected_properties": target_case.get("expected_properties", {
                "required_metrics": {"effect_size_type": "partial_eta_squared"}
            }) if target_case else {},
            "forbidden_behaviors": target_case.get("forbidden_behaviors", [
                "p_equals_point_zero_zero_zero", "omitting_homogeneity_of_slopes_test"
            ]) if target_case else ["p_equals_point_zero_zero_zero"],
            "inputs": target_case.get("inputs", {}) if target_case else {}
        })

        # Task B: Related capability generalization
        related_case = None
        for c in rel_cases:
            if target_case and c.get("case_id") != target_case.get("case_id"):
                related_case = c
                break
        if not related_case and all_cases:
            related_case = all_cases[1] if len(all_cases) > 1 else all_cases[0]

        panel.append({
            "task_id": "TASK-B",
            "name": f"Related Capability Generalization: {capability}",
            "type": "RELATED_CAPABILITY",
            "description": f"Evaluates whether candidate generalizes correctly to secondary tasks within '{capability}'.",
            "expected_properties": related_case.get("expected_properties", {
                "required_metrics": {"bca_confidence_interval_reported": True}
            }) if related_case else {},
            "forbidden_behaviors": related_case.get("forbidden_behaviors", [
                "failing_to_report_ci"
            ]) if related_case else ["failing_to_report_ci"],
            "inputs": related_case.get("inputs", {}) if related_case else {}
        })

        # Task C: Permanent regression guard
        reg_case = reg_cases[0] if reg_cases else (all_cases[0] if all_cases else None)
        panel.append({
            "task_id": "TASK-C",
            "name": "Regression Guard: Core Baseline Capabilities",
            "type": "REGRESSION_GUARD",
            "description": "Verifies that core baseline capabilities, assumption checks, and typography remain unregressed.",
            "expected_properties": reg_case.get("expected_properties", {
                "required_reasoning_properties": ["repeated_measures_structure", "missingness"]
            }) if reg_case else {},
            "forbidden_behaviors": reg_case.get("forbidden_behaviors", [
                "unjustified_model_selection_without_comparison"
            ]) if reg_case else ["unjustified_model_selection_without_comparison"],
            "inputs": reg_case.get("inputs", {}) if reg_case else {}
        })

        return panel

    # -------------------------------------------------------------------------
    # 2. Blinded Token Assignment & Payload Sanitization
    # -------------------------------------------------------------------------

    def _sanitize_output_payload(self, raw_output: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deeply sanitizes an agent's output payload to eliminate all self-identifying markers:
        - candidate_id, sandbox_id, version, git_commit, patch_id
        - self-asserted verdicts ('improved': True, 'verdict': 'PASS', 'recommendation': 'PROMOTE')
        - absolute directory paths referencing sandbox or candidate directories
        """
        sanitized = copy.deepcopy(raw_output)

        # Prohibited self-asserted keys
        prohibited_meta_keys = [
            "candidate_id", "candidate", "sandbox_id", "sandbox_path",
            "version", "parent_version", "git_hash", "git_commit",
            "patch_id", "agent_type", "is_candidate", "is_baseline",
            "self_verdict", "self_evaluation", "improved", "recommendation"
        ]

        def _clean_dict(d: Dict[str, Any]):
            for k in list(d.keys()):
                if k.lower() in prohibited_meta_keys:
                    del d[k]
                elif isinstance(d[k], dict):
                    _clean_dict(d[k])
                elif isinstance(d[k], list):
                    for item in d[k]:
                        if isinstance(item, dict):
                            _clean_dict(item)
                elif isinstance(d[k], str):
                    # Sanitize any paths referencing candidate/sandbox
                    if "learning/candidates" in d[k] or "isolated_agent" in d[k]:
                        d[k] = "sanitized_task_output.json"

        if isinstance(sanitized, dict):
            _clean_dict(sanitized)

        return sanitized

    def blind_submissions(
        self,
        baseline_outputs: Dict[str, Any],
        candidate_outputs: Dict[str, Any],
        salt: Optional[str] = None
    ) -> Tuple[Dict[str, Any], Dict[str, str], str]:
        """
        Blinds baseline and candidate outputs into 'Submission_A' and 'Submission_B'.
        Returns:
          - blinded_submissions: Dict[str, Dict[str, Any]] keyed by Submission_A / Submission_B
          - token_mapping: Dict[str, str] mapping 'candidate' and 'baseline' to tokens
          - salt_hash: SHA-256 hash of the blinding salt
        """
        blinding_salt = salt or uuid.uuid4().hex
        salt_hash = hashlib.sha256(blinding_salt.encode("utf-8")).hexdigest()

        # Deterministic but pseudo-random assignment based on salt
        coin_flip = int(salt_hash[:2], 16) % 2 == 0

        if coin_flip:
            token_candidate = "Submission_A"
            token_baseline = "Submission_B"
        else:
            token_candidate = "Submission_B"
            token_baseline = "Submission_A"

        token_mapping = {
            "candidate": token_candidate,
            "baseline": token_baseline
        }

        # Sanitize both payloads
        clean_cand = self._sanitize_output_payload(candidate_outputs)
        clean_base = self._sanitize_output_payload(baseline_outputs)

        blinded_submissions = {
            token_candidate: clean_cand,
            token_baseline: clean_base
        }

        return blinded_submissions, token_mapping, salt_hash

    # -------------------------------------------------------------------------
    # 3. Independent Blinded Evaluation Execution
    # -------------------------------------------------------------------------

    def evaluate_blinded_panel(
        self,
        task_panel: List[Dict[str, Any]],
        blinded_submissions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        The Independent Evaluator grades Submission_A and Submission_B across each task in task_panel.
        CRITICAL: The evaluator has ZERO knowledge of which submission is the candidate.
        """
        blinded_evaluations: Dict[str, Any] = {}

        for token in ["Submission_A", "Submission_B"]:
            submission_payload = blinded_submissions.get(token, {})
            tasks_results = {}
            passed_tasks_count = 0
            all_diagnostics = []

            for task in task_panel:
                task_id = task["task_id"]
                # Extract task-specific output from submission if nested by task_id, otherwise use whole payload
                task_output = submission_payload.get(task_id, submission_payload)

                # Convert task to evaluation case format for AcademicEvaluationLab
                eval_case = {
                    "case_id": task_id,
                    "expected_properties": task.get("expected_properties", {}),
                    "forbidden_behaviors": task.get("forbidden_behaviors", []),
                    "inputs": task.get("inputs", {})
                }

                # Evaluate using deterministic domain verifiers
                res = self.lab.evaluate_candidate_on_case(
                    candidate_id=token,  # Evaluator evaluates the blinded token
                    case=eval_case,
                    candidate_artifacts=task_output
                )

                verdict = res["verdict"]
                if verdict == "PASS":
                    passed_tasks_count += 1

                failed_checks = [d["failure_type"] for d in res["diagnostics"]]
                passed_checks = [
                    dim for dim, dim_res in res.get("dimensional_evaluations", {}).items()
                    if dim_res.get("verdict") == "PASS"
                ]

                tasks_results[task_id] = {
                    "verdict": verdict,
                    "passed_checks": passed_checks,
                    "failed_checks": failed_checks,
                    "diagnostics": res["diagnostics"]
                }
                all_diagnostics.extend(res["diagnostics"])

            # Compute 8-dimensional evaluation for this submission
            dimensional_results = {}
            for dim in self.DIMENSIONS:
                dim_diags = [d for d in all_diagnostics if d.get("dimension") == dim]
                dimensional_results[dim] = {
                    "verdict": "PASS" if len(dim_diags) == 0 else "FAIL",
                    "failures_count": len(dim_diags),
                    "failure_types": [d["failure_type"] for d in dim_diags]
                }

            overall_verdict = "PASS" if passed_tasks_count == len(task_panel) else "FAIL"

            blinded_evaluations[token] = {
                "tasks": tasks_results,
                "overall_verdict": overall_verdict,
                "passed_tasks_count": passed_tasks_count,
                "total_tasks_count": len(task_panel),
                "dimensional_evaluations": dimensional_results
            }

        return blinded_evaluations

    # -------------------------------------------------------------------------
    # 4. Post-Evaluation Unblinding & Comparative Analysis
    # -------------------------------------------------------------------------

    def unblind_and_compare(
        self,
        candidate_id: str,
        baseline_version: str,
        capability: str,
        task_panel: List[Dict[str, Any]],
        blinded_evaluations: Dict[str, Any],
        token_mapping: Dict[str, str],
        salt_hash: str
    ) -> Dict[str, Any]:
        """
        Unblinds the evaluation results and computes objective comparative metrics:
        - defect_resolved
        - candidate_outperformed_baseline
        - zero_regressions_verified
        - independent_verdict ('PASS' | 'FAIL')
        """
        cand_tok = token_mapping["candidate"]
        base_tok = token_mapping["baseline"]

        cand_eval = blinded_evaluations.get(cand_tok, {})
        base_eval = blinded_evaluations.get(base_tok, {})

        cand_tasks = cand_eval.get("tasks", {})
        base_tasks = base_eval.get("tasks", {})

        tasks_summary = {}
        defect_resolved = False
        new_regressions = []
        resolved_defects = []

        for task in task_panel:
            tid = task["task_id"]
            ttype = task.get("type")

            b_res = base_tasks.get(tid, {})
            c_res = cand_tasks.get(tid, {})

            b_verdict = b_res.get("verdict", "FAIL")
            c_verdict = c_res.get("verdict", "FAIL")

            cand_improved = (b_verdict == "FAIL" and c_verdict == "PASS")
            cand_regressed = (b_verdict == "PASS" and c_verdict == "FAIL")

            if cand_improved:
                resolved_defects.append(tid)
                if ttype == "TARGET_DEFECT" or tid == "TASK-A":
                    defect_resolved = True

            if cand_regressed:
                new_regressions.append(tid)

            tasks_summary[tid] = {
                "name": task.get("name"),
                "type": ttype,
                "baseline_verdict": b_verdict,
                "candidate_verdict": c_verdict,
                "candidate_improved": cand_improved,
                "candidate_regressed": cand_regressed
            }

        candidate_passes = cand_eval.get("passed_tasks_count", 0)
        baseline_passes = base_eval.get("passed_tasks_count", 0)

        # Candidate outperforms baseline if it passed strictly more tasks,
        # or passed equal tasks but resolved the target defect without new regressions
        candidate_outperformed = (candidate_passes > baseline_passes) or (
            candidate_passes == baseline_passes and defect_resolved and len(new_regressions) == 0
        )
        zero_regressions = (len(new_regressions) == 0)

        # Final independent verdict: PASS requires defect_resolved, zero regressions, and candidate >= baseline
        independent_verdict = "PASS" if (defect_resolved and zero_regressions and candidate_passes >= baseline_passes) else "FAIL"
        recommendation = "PROMOTE" if independent_verdict == "PASS" else "REJECT"

        eval_id = f"INDEP-EVL-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"

        report_data = {
            "contract_version": "1.0.0",
            "evaluation_id": eval_id,
            "candidate_id": candidate_id,
            "baseline_version": baseline_version,
            "capability": capability,
            "tasks": task_panel,
            "blinding": {
                "is_blinded": True,
                "blinded_tokens": ["Submission_A", "Submission_B"],
                "salt_hash": salt_hash
            },
            "blinded_evaluations": blinded_evaluations,
            "unblinded_comparison": {
                "candidate_token": cand_tok,
                "baseline_token": base_tok,
                "candidate_passes": candidate_passes,
                "baseline_passes": baseline_passes,
                "tasks_summary": tasks_summary,
                "defect_resolved": defect_resolved,
                "candidate_outperformed_baseline": candidate_outperformed,
                "zero_regressions_verified": zero_regressions,
                "independent_verdict": independent_verdict,
                "recommendation": recommendation,
                "resolved_defects": resolved_defects,
                "new_regressions": new_regressions
            },
            "evaluated_at": datetime.now(timezone.utc).isoformat()
        }

        # Validate against schema
        val_res = validate_independent_evaluation(report_data)
        if not val_res["valid"]:
            print(f"Independent evaluation schema warning: {val_res.get('errors')}", file=sys.stderr)

        # Persist report
        report_file = os.path.join(self.independent_dir, f"{eval_id}.json")
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        return report_data

    # -------------------------------------------------------------------------
    # 5. Full End-to-End Orchestrator
    # -------------------------------------------------------------------------

    def execute_independent_evaluation(
        self,
        candidate_id: str,
        baseline_version: str,
        capability: str,
        baseline_outputs: Dict[str, Any],
        candidate_outputs: Dict[str, Any],
        task_panel: Optional[List[Dict[str, Any]]] = None,
        failure_signature: Optional[str] = None,
        salt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes the complete independent evaluation pipeline:
        1. Assembles multi-task benchmark panel (Task A, Task B, Task C).
        2. Blinds outputs into Submission A and Submission B (sanitizing metadata).
        3. Grades Submission A and Submission B independently across the 8 dimensions.
        4. Unblinds results and compiles comparative findings.
        """
        # Anti-Self-Evaluation Guard
        if "improved" in candidate_outputs and candidate_outputs["improved"] is True and not baseline_outputs:
            raise SelfEvaluationBlockedError(
                "Candidate attempted to self-declare improvement without baseline comparison! Independent evaluation required."
            )

        # 1. Build Task Panel
        panel = task_panel or self.build_task_panel(capability, failure_signature)

        # 2. Blind Submissions
        blinded_submissions, token_mapping, salt_hash = self.blind_submissions(
            baseline_outputs=baseline_outputs,
            candidate_outputs=candidate_outputs,
            salt=salt
        )

        # 3. Independent Blinded Evaluation
        blinded_evaluations = self.evaluate_blinded_panel(
            task_panel=panel,
            blinded_submissions=blinded_submissions
        )

        # 4. Unblind and Compare
        report = self.unblind_and_compare(
            candidate_id=candidate_id,
            baseline_version=baseline_version,
            capability=capability,
            task_panel=panel,
            blinded_evaluations=blinded_evaluations,
            token_mapping=token_mapping,
            salt_hash=salt_hash
        )

        return report


def main():
    parser = argparse.ArgumentParser(description="AcademicSuite Independent Blinded A/B Evaluator CLI")
    parser.add_argument("--candidate", required=True, help="Candidate ID")
    parser.add_argument("--baseline", default="git-baseline", help="Baseline Version")
    parser.add_argument("--capability", required=True, help="Target Capability")
    parser.add_argument("--candidate-file", help="Path to JSON file containing candidate outputs")
    parser.add_argument("--baseline-file", help="Path to JSON file containing baseline outputs")
    parser.add_argument("--failure-signature", help="Motivating defect signature")
    args = parser.parse_args()

    evaluator = AcademicIndependentEvaluator()

    cand_out = {}
    if args.candidate_file and os.path.isfile(args.candidate_file):
        with open(args.candidate_file, "r", encoding="utf-8") as f:
            cand_out = json.load(f)

    base_out = {}
    if args.baseline_file and os.path.isfile(args.baseline_file):
        with open(args.baseline_file, "r", encoding="utf-8") as f:
            base_out = json.load(f)

    report = evaluator.execute_independent_evaluation(
        candidate_id=args.candidate,
        baseline_version=args.baseline,
        capability=args.capability,
        baseline_outputs=base_out,
        candidate_outputs=cand_out,
        failure_signature=args.failure_signature
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
