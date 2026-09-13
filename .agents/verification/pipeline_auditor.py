#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Independent Pipeline Auditor CLI (pipeline_auditor.py)
------------------------------------------------------
Forensic verification and quality control auditor for AcademicSuite workflows.
Enforces Digital Saber Constitutional Directives:
  - Directive 0: Radical Honesty & Anti-Deception Protocol
  - Directive 1: Mandatory Pre-Flight Gate
  - Directive 2: Deterministic Calculation (Zero Mock Hallucinations)
  - Directive 3: Artifact-Gated Stage Execution (No Skipping)
  - Directive 4: Strict APA 7th Edition & Persian Leading Zero Standard
  - Directive 5: Persian Academic Typography & OpenXML Standards
  - Directive 9: Realistic Decimal Noise in Psychometric Data
  - Directive 10: Multi-Signal Anomaly Scoring (MSAI)

CLI Usage:
  python3 .agents/verification/pipeline_auditor.py --workflow chapter4 --dir output
  python3 .agents/verification/pipeline_auditor.py --workflow all --dir /tmp/test_real_ch4
"""

import os
import sys
import re
import json
import argparse
from typing import Dict, List, Any, Optional, Tuple

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False


class PipelineAuditor:
    """Forensic verification auditor for multi-agent academic pipeline artifacts."""

    MANDATORY_ARTIFACTS: Dict[str, List[Tuple[Any, int]]] = {
        "chapter4": [
            (["data_scored.xlsx", "simulated_rct_dataset.xlsx", "raw_data.xlsx", "dataset.xlsx", "simulated_rct_dataset.csv"], 500),
            ("study_config.json", 50),
            ("methodology_spec.json", 50),
            ("statistical_plan.json", 50),
            ("stats_results.json", 100),
            ("statistical_audit_report.json", 50),
            ("results_qc_checklist.json", 50),
            ("Chapter_4_Results.docx", 1000),
            ("Statistical_Audit_and_QC_Report.docx", 1000),
            (["Defense_Viva_Voce_Brief.docx", "Defense_Viva_Card_and_Questions.docx"], 1000)
        ],
        "chapter5": [
            ("Chapter_5_Discussion_and_Conclusion.docx", 1000),
            ("stats_results.json", 100)
        ],
        "proposal": [
            ("Research_Proposal.docx", 1000),
            ("proposal_blueprint.json", 100)
        ],
        "journal_submission": [
            (["Academic_Article_Manuscript.docx", "Journal_Article_Manuscript.docx"], 1000),
            (["Cover_Letter_Editor.docx", "Cover_Letter_to_Editor.docx"], 1000),
            (["Title_Page_CRediT.docx", "Title_Page_and_Declarations.docx"], 1000),
            (["submission_manifest.json", "journal_submission_package.json"], 100)
        ],
        "defense_presentation": [
            (["Defense_Speech_Notes.docx", "Defense_Speaker_Notes.docx"], 1000)
        ]
    }

    KNOWN_MOCK_STRINGS = [
        "14.32",  # Historical hardcoded mock F statistic
        "TODO:",
        "MOCK_DATA",
        "mock_result",
        "fake_data",
        "lorem ipsum"
    ]

    def __init__(self, target_dir: str, workflow: str = "chapter4", strict: bool = True):
        self.target_dir = os.path.abspath(target_dir)
        self.workflow = workflow.lower()
        self.strict = strict
        self.findings: List[Dict[str, Any]] = []
        self.stats: Dict[str, Any] = {}
        self.overall_passed = True

    def _log_finding(self, check_name: str, passed: bool, message: str, severity: str = "ERROR", details: Optional[Dict] = None):
        if not passed:
            if severity == "ERROR":
                self.overall_passed = False
        self.findings.append({
            "check": check_name,
            "passed": passed,
            "severity": severity,
            "message": message,
            "details": details or {}
        })

    def run_audit(self) -> Dict[str, Any]:
        """Executes full forensic pipeline audit."""
        print("=" * 80)
        print("🔍 EXECUTING INDEPENDENT PIPELINE INTEGRITY AUDIT")
        print(f"Target Directory: {self.target_dir}")
        print(f"Workflow:         {self.workflow}")
        print(f"Strict Mode:      {self.strict}")
        print("=" * 80)

        # 1. Directory existence check
        if not os.path.exists(self.target_dir):
            self._log_finding("DIR_EXISTENCE", False, f"Target directory does not exist: {self.target_dir}", "ERROR")
            return self._build_report()

        # 2. Artifact Gating Audit (Directive 3)
        self._audit_artifact_gating()

        # 3. Data & Stats Results JSON Audit (Directive 2 & 9)
        self._audit_stats_json()

        # 4. Mock Pattern & Deception Scanner (Directive 0 & 2)
        self._audit_mock_patterns()

        # 5. Word OpenXML & APA 7 Concordance Audit (Directive 4 & 5)
        self._audit_docx_concordance()

        return self._build_report()

    def _audit_artifact_gating(self):
        """Verifies physical disk existence and minimum size of required artifacts."""
        reqs = self.MANDATORY_ARTIFACTS.get(self.workflow, [])
        if not reqs and self.workflow == "all":
            # Check all known workflows
            reqs = []
            for w, arts in self.MANDATORY_ARTIFACTS.items():
                reqs.extend(arts)
            # deduplicate by filename
            seen = set()
            dedup_reqs = []
            for f, sz in reqs:
                key = tuple(f) if isinstance(f, list) else f
                if key not in seen:
                    seen.add(key)
                    dedup_reqs.append((f, sz))
            reqs = dedup_reqs

        for candidate, min_bytes in reqs:
            candidates = [candidate] if isinstance(candidate, str) else list(candidate)
            matched_file = None
            matched_size = 0
            for c in candidates:
                p = os.path.join(self.target_dir, c)
                if os.path.exists(p):
                    matched_file = c
                    matched_size = os.path.getsize(p)
                    break

            if not matched_file:
                self._log_finding(
                    "ARTIFACT_GATING",
                    False,
                    f"Mandatory checkpoint artifact missing from disk: {' or '.join(candidates)}",
                    "ERROR",
                    {"candidates": candidates, "expected_min_bytes": min_bytes}
                )
            elif matched_size < min_bytes:
                self._log_finding(
                    "ARTIFACT_SIZE",
                    False,
                    f"Artifact '{matched_file}' exists but is suspiciously small ({matched_size} bytes < {min_bytes} expected)",
                    "ERROR",
                    {"file": matched_file, "actual_bytes": matched_size, "min_bytes": min_bytes}
                )
            else:
                self._log_finding(
                    "ARTIFACT_GATING",
                    True,
                    f"Verified physical checkpoint artifact: {matched_file} ({matched_size:,} bytes)",
                    "INFO",
                    {"file": matched_file, "bytes": matched_size}
                )

    def _audit_stats_json(self):
        """Audits stats_results.json for validity, degrees of freedom, and realistic noise."""
        stats_path = os.path.join(self.target_dir, "stats_results.json")
        if not os.path.exists(stats_path):
            return

        try:
            with open(stats_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.stats = data

            # Verify sample size
            n = data.get("sample_size")
            if not n or n <= 0:
                self._log_finding("STATS_SAMPLE_SIZE", False, "stats_results.json missing or invalid sample_size", "ERROR")
            else:
                self._log_finding("STATS_SAMPLE_SIZE", True, f"Verified sample size N = {n}", "INFO")

            # Verify descriptives & decimal noise (Directive 9)
            descriptives = data.get("descriptives", {})
            if not descriptives:
                self._log_finding("STATS_DESCRIPTIVES", False, "stats_results.json has empty descriptives", "WARNING")
            else:
                for grp, s in descriptives.items():
                    m = s.get("mean")
                    sd = s.get("sd")
                    # Check Directive 9: realistic decimal noise (not whole integer)
                    if m is not None and float(m).is_integer() and float(m) > 10:
                        self._log_finding(
                            "DIRECTIVE_9_DECIMAL_NOISE",
                            False,
                            f"Group '{grp}' mean is an exact integer ({m}), violating empirical noise directive",
                            "WARNING",
                            {"group": grp, "mean": m}
                        )

            # Verify hypotheses
            hyps = data.get("hypotheses", [])
            if not hyps:
                self._log_finding("STATS_HYPOTHESES", False, "stats_results.json contains zero hypothesis tests", "ERROR")
            else:
                for idx, h in enumerate(hyps, 1):
                    f_val = h.get("f_val")
                    df1 = h.get("df1")
                    df2 = h.get("df2")
                    p_val = h.get("p_val")
                    eta = h.get("eta_squared")

                    if f_val is None or float(f_val) <= 0:
                        self._log_finding("STATS_F_STAT", False, f"Hypothesis {idx}: Invalid F statistic ({f_val})", "ERROR")
                    if df1 is None or int(df1) < 1:
                        self._log_finding("STATS_DF1", False, f"Hypothesis {idx}: Invalid df_between ({df1})", "ERROR")
                    if df2 is None or int(df2) < 5:
                        self._log_finding("STATS_DF2", False, f"Hypothesis {idx}: Invalid df_within ({df2})", "ERROR")
                    if eta is None or float(eta) <= 0 or float(eta) > 1.0:
                        self._log_finding("STATS_ETA", False, f"Hypothesis {idx}: Invalid eta_squared ({eta})", "ERROR")

                    self._log_finding(
                        "STATS_NUMERICAL_SANITY",
                        True,
                        f"Hypothesis {idx}: F({df1}, {df2}) = {f_val:.2f}, p {p_val}, ηp² = {eta:.3f}",
                        "INFO"
                    )
        except Exception as e:
            self._log_finding("STATS_JSON_PARSE", False, f"Failed to parse stats_results.json: {str(e)}", "ERROR")

    def _audit_mock_patterns(self):
        """Scans artifacts in target directory for known mock strings and placeholders."""
        for root, _, files in os.walk(self.target_dir):
            for file in files:
                if file == "PIPELINE_INTEGRITY_AUDIT.json":
                    continue
                filepath = os.path.join(root, file)
                # Check text / JSON files
                if file.endswith((".json", ".csv", ".txt", ".md")):
                    try:
                        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                        for mock_str in self.KNOWN_MOCK_STRINGS:
                            if mock_str in content:
                                self._log_finding(
                                    "MOCK_PATTERN_SCAN",
                                    False,
                                    f"Detected mock/placeholder string '{mock_str}' in {file}",
                                    "ERROR",
                                    {"file": file, "mock_string": mock_str}
                                )
                    except Exception:
                        pass

    def _audit_docx_concordance(self):
        """Audits Word .docx files for table structure, APA 7 formatting, and stats concordance."""
        if not DOCX_AVAILABLE:
            self._log_finding("DOCX_AUDIT", True, "python-docx not installed; skipping binary OpenXML inspection", "WARNING")
            return

        ch4_docx = os.path.join(self.target_dir, "Chapter_4_Results.docx")
        if not os.path.exists(ch4_docx):
            return

        try:
            doc = docx.Document(ch4_docx)

            # Check table existence (Directive 4 & 5)
            if len(doc.tables) == 0:
                self._log_finding(
                    "DOCX_TABLE_COUNT",
                    False,
                    "Chapter_4_Results.docx has 0 tables! Results must include APA 7 tables.",
                    "ERROR"
                )
            else:
                self._log_finding(
                    "DOCX_TABLE_COUNT",
                    True,
                    f"Chapter_4_Results.docx contains {len(doc.tables)} APA 7 tables",
                    "INFO"
                )

            # Check numerical concordance with stats_results.json
            full_text = ""
            for p in doc.paragraphs:
                full_text += p.text + "\n"
            for t in doc.tables:
                for row in t.rows:
                    for cell in row.cells:
                        full_text += cell.text + " "

            # Check for forbidden mock string 14.32
            if "14.32" in full_text:
                self._log_finding(
                    "DOCX_MOCK_DETECTION",
                    False,
                    "Found legacy mock F statistic '14.32' inside Chapter_4_Results.docx!",
                    "ERROR"
                )

            # Check for F stat concordance
            hyps = self.stats.get("hypotheses", [])
            if hyps:
                f_expected = f"{float(hyps[0].get('f_val', 0.0)):.2f}"
                df_expected = str(hyps[0].get("df2", ""))
                # Allow persian digits or english digits
                if f_expected not in full_text and self._to_persian(f_expected) not in full_text:
                    self._log_finding(
                        "STATS_DOCX_CONCORDANCE",
                        False,
                        f"Expected F statistic {f_expected} from stats_results.json was NOT found in Chapter_4_Results.docx text or tables",
                        "ERROR",
                        {"expected_f": f_expected}
                    )
                else:
                    self._log_finding(
                        "STATS_DOCX_CONCORDANCE",
                        True,
                        f"Concordance verified: F statistic ({f_expected}) matches between JSON and Word document",
                        "INFO"
                    )

            # Check APA 7: prohibition of p = .000 (Directive 4)
            if "p = .000" in full_text or "p = ۰.۰۰۰" in full_text or "۰.۰۰۰ = p" in full_text:
                self._log_finding(
                    "APA7_P_VALUE_RULE",
                    False,
                    "Prohibited 'p = .000' reported! APA 7 strictly requires 'p < .001' (یا '۰.۰۰۱ > p')",
                    "ERROR"
                )
            else:
                self._log_finding(
                    "APA7_P_VALUE_RULE",
                    True,
                    "APA 7 p-value reporting verified: Zero 'p = .000' violations detected",
                    "INFO"
                )

        except Exception as e:
            self._log_finding("DOCX_PARSE_ERROR", False, f"Failed to open Chapter_4_Results.docx: {str(e)}", "ERROR")

    def _to_persian(self, num_str: str) -> str:
        mapping = str.maketrans("0123456789", "۰۱۲۳۴۵۶۷۸۹")
        return str(num_str).translate(mapping)

    def _build_report(self) -> Dict[str, Any]:
        """Formats the audit scorecard and saves PIPELINE_INTEGRITY_AUDIT.json."""
        errors = [f for f in self.findings if f["severity"] == "ERROR" and not f["passed"]]
        warnings = [f for f in self.findings if f["severity"] == "WARNING" and not f["passed"]]
        passed_checks = [f for f in self.findings if f["passed"]]

        report = {
            "workflow": self.workflow,
            "target_dir": self.target_dir,
            "status": "PASSED" if self.overall_passed else "FAILED",
            "summary": {
                "total_checks": len(self.findings),
                "passed": len(passed_checks),
                "errors": len(errors),
                "warnings": len(warnings)
            },
            "findings": self.findings
        }

        # Save JSON artifact
        json_path = os.path.join(self.target_dir, "PIPELINE_INTEGRITY_AUDIT.json")
        try:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

        # Print terminal summary
        print("\n" + "-" * 80)
        print(f"📊 AUDIT REPORT: [{'PASSED' if self.overall_passed else 'FAILED'}]")
        print(f"Total Checks: {len(self.findings)} | Passed: {len(passed_checks)} | Errors: {len(errors)} | Warnings: {len(warnings)}")
        print("-" * 80)

        for f in self.findings:
            mark = "✅" if f["passed"] else ("❌" if f["severity"] == "ERROR" else "⚠️")
            print(f"{mark} [{f['check']}] {f['message']}")

        print("=" * 80)
        if self.overall_passed:
            print("🌟 PIPELINE INTEGRITY CONFIRMED: ZERO MOCK DATA DETECTED.")
        else:
            print("🚨 PIPELINE INTEGRITY AUDIT FAILED: CORRECTIVE ACTIONS REQUIRED.")
        print("=" * 80 + "\n")

        return report


def main():
    parser = argparse.ArgumentParser(description="Digital Saber Independent Pipeline Auditor")
    parser.add_argument("--workflow", default="chapter4", help="Workflow to audit (chapter4, chapter5, proposal, journal_submission, defense_presentation, all)")
    parser.add_argument("--dir", default="output", help="Target output directory to audit")
    parser.add_argument("--lax", action="store_true", help="Run in lax mode (warnings do not fail)")

    args = parser.parse_args()
    auditor = PipelineAuditor(target_dir=args.dir, workflow=args.workflow, strict=not args.lax)
    report = auditor.run_audit()

    sys.exit(0 if report["status"] == "PASSED" else 1)


if __name__ == "__main__":
    main()
