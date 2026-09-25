# -*- coding: utf-8 -*-
"""
tests/test_fail_closed_validation_phase9.py — Phase 9 Fail-Closed Validation Test Suite

Validates the sequential gate cascade:
- Gate 0: Manifest Existence (No manifest -> UNVERIFIED)
- Gate 1: Manifest Schema Validity (Schema invalid -> FAIL)
- Gate 2: Artifact Existence, Non-Empty, Hashes & Triad Invariant (Missing -> BLOCKED, Hash mismatch -> FAIL)
- Gate 3: Numerical Consistency (Invalid statistics -> FAIL, Zero numbers -> UNKNOWN)
- Gate 4: Narrative & Cross-Artifact Concordance (Clichés/Contradictions -> FAIL)
- Gate 5: Upstream Dependency Integrity (Missing dep -> BLOCKED, Hash mismatch -> FAIL)
- Gate 6: Composite Fail-Closed Verdict Resolution (PASS only if all gates pass with >= 1 positive evidence)
"""

import os
import sys
import json
import shutil
import hashlib
import tempfile
import unittest
import zipfile

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from validators.run_all_validators import run_suite, compute_sha256
from validators.numerical_consistency.validator import validate_numbers
from validators.reporting_consistency.validator import validate_reporting
from validators.result_consistency.validator import validate_cross_artifacts


class TestFailClosedValidationPhase9(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="phase9_val_test_")

    def tearDown(self):
        shutil.rmtree(self.test_dir, ignore_errors=True)

    def _create_minimal_docx(self, path: str, text: str = "Test deliverable content", body_xml: str = None):
        if body_xml:
            xml_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    {body_xml}
  </w:body>
</w:document>"""
        else:
            xml_content = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p><w:r><w:t>{text}</w:t></w:r></w:p>
  </w:body>
</w:document>"""
        with zipfile.ZipFile(path, "w") as zf:
            zf.writestr("word/document.xml", xml_content)
            zf.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"/>')

    def test_01_no_manifest_returns_unverified(self):
        stage_name = "06_hypothesis_1"
        json_path = os.path.join(self.test_dir, f"{stage_name}.json")
        md_path = os.path.join(self.test_dir, f"{stage_name}.md")
        docx_path = os.path.join(self.test_dir, f"{stage_name}.docx")

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"stage_id": stage_name, "sample_size": 100, "f_stat": 4.5}, f)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Findings\n\nF = 4.50, p < .001.\n")
        self._create_minimal_docx(docx_path, "F = 4.50")

        report = run_suite(self.test_dir, stage_id=stage_name, require_manifest=True)
        self.assertEqual(report["overall_verdict"], "UNVERIFIED")
        self.assertGreaterEqual(report["evidence_summary"]["checks_unverified"], 1)
        self.assertTrue(any("unverified" in e.lower() or "missing" in e.lower() for e in report["errors"]))

    def test_02_manifest_schema_invalid_returns_fail(self):
        stage_name = "06_hypothesis_1"
        json_path = os.path.join(self.test_dir, f"{stage_name}.json")
        md_path = os.path.join(self.test_dir, f"{stage_name}.md")
        docx_path = os.path.join(self.test_dir, f"{stage_name}.docx")
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"stage_id": stage_name, "sample_size": 100, "f_stat": 4.5}, f)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Findings\n\nF = 4.50, p < .001.\n")
        self._create_minimal_docx(docx_path)

        manifest_path = os.path.join(self.test_dir, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as mf:
            json.dump({
                "stage_id": stage_name,
                "status": "ILLEGAL_STATUS_VALUE",
                "producer": "not_an_object"
            }, mf)

        report = run_suite(self.test_dir, stage_id=stage_name, require_manifest=True)
        self.assertEqual(report["overall_verdict"], "FAIL")
        self.assertTrue(any("schema validation" in e.lower() for e in report["errors"]))

    def test_03_missing_required_artifact_returns_blocked(self):
        stage_name = "06_hypothesis_1"
        md_path = os.path.join(self.test_dir, f"{stage_name}.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Hypothesis 1 Findings\n\nF = 4.50, p < .001.\n")

        manifest_path = os.path.join(self.test_dir, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as mf:
            json.dump({
                "contract_version": "1.0.0",
                "stage_id": stage_name,
                "project_id": "test_project",
                "producer": {"agent": "statistics-agent", "script_or_generator": "stats.py"},
                "inputs": [],
                "required_artifacts": [
                    {"path": f"{stage_name}.json", "type": "stats_json", "required": True},
                    {"path": f"{stage_name}.md", "type": "narrative_markdown", "required": True},
                    {"path": f"{stage_name}.docx", "type": "openxml_word", "required": True}
                ],
                "hashes": {f"{stage_name}.md": compute_sha256(md_path)},
                "status": "GENERATED",
                "timestamps": {"created_at": "2026-09-19T00:00:00Z", "completed_at": "2026-09-19T00:00:00Z"}
            }, mf)

        report = run_suite(self.test_dir, stage_id=stage_name, require_manifest=True)
        self.assertEqual(report["overall_verdict"], "BLOCKED")
        self.assertGreaterEqual(report["evidence_summary"]["checks_blocked"], 1)

    def test_04_artifact_hash_mismatch_returns_fail(self):
        stage_name = "06_hypothesis_1"
        json_path = os.path.join(self.test_dir, f"{stage_name}.json")
        md_path = os.path.join(self.test_dir, f"{stage_name}.md")
        docx_path = os.path.join(self.test_dir, f"{stage_name}.docx")

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"stage_id": stage_name, "sample_size": 100, "f_stat": 4.5}, f)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Findings\n\nF = 4.50, p < .001.\n")
        self._create_minimal_docx(docx_path, "F = 4.50")

        manifest_path = os.path.join(self.test_dir, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as mf:
            json.dump({
                "contract_version": "1.0.0",
                "stage_id": stage_name,
                "project_id": "test_project",
                "producer": {"agent": "statistics-agent", "script_or_generator": "stats.py"},
                "inputs": [],
                "required_artifacts": [
                    {"path": f"{stage_name}.json", "type": "stats_json", "required": True},
                    {"path": f"{stage_name}.md", "type": "narrative_markdown", "required": True},
                    {"path": f"{stage_name}.docx", "type": "openxml_word", "required": True}
                ],
                "hashes": {
                    f"{stage_name}.json": "0000000000000000000000000000000000000000000000000000000000000000",
                    f"{stage_name}.md": compute_sha256(md_path),
                    f"{stage_name}.docx": compute_sha256(docx_path)
                },
                "status": "GENERATED",
                "timestamps": {"created_at": "2026-09-19T00:00:00Z", "completed_at": "2026-09-19T00:00:00Z"}
            }, mf)

        report = run_suite(self.test_dir, stage_id=stage_name, require_manifest=True)
        self.assertEqual(report["overall_verdict"], "FAIL")
        self.assertTrue(any("hash mismatch" in e.lower() for e in report["errors"]))

    def test_05_zero_numerical_parameters_returns_unknown(self):
        empty_stats_path = os.path.join(self.test_dir, "empty_stats.json")
        with open(empty_stats_path, "w", encoding="utf-8") as f:
            json.dump({"unrelated_metadata": "no_numbers_here"}, f)

        res = validate_numbers(empty_stats_path)
        self.assertEqual(res["verdict"], "UNKNOWN")
        self.assertEqual(res["evidence_items_audited"], 0)

    def test_06_prohibited_statistical_reporting_returns_fail(self):
        bad_md_path = os.path.join(self.test_dir, "bad_reporting.md")
        with open(bad_md_path, "w", encoding="utf-8") as f:
            f.write("# Findings\n\nStatistical significance was p = .000 and effect was .۰۵.\n")

        res = validate_reporting(bad_md_path)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertGreater(len(res["errors"]), 0)
        self.assertTrue(any("p = .000" in e or "leading zero" in e.lower() for e in res["errors"]))

    def test_07_cross_artifact_contradiction_returns_fail(self):
        stage_name = "06_hypothesis_1"
        json_path = os.path.join(self.test_dir, f"{stage_name}.json")
        md_path = os.path.join(self.test_dir, f"{stage_name}.md")
        docx_path = os.path.join(self.test_dir, f"{stage_name}.docx")

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"stage_id": stage_name, "sample_size": 100, "f_stat": 45.2}, f)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Findings\n\nContradictory statistic: F = 12.10, p < .001.\n")
        self._create_minimal_docx(docx_path, "F = 12.10")

        res = validate_cross_artifacts(json_path=json_path, md_path=md_path, docx_path=docx_path)
        self.assertEqual(res["verdict"], "FAIL")
        self.assertTrue(any("contradiction" in e.lower() for e in res["errors"]))

    def test_08_missing_dependency_manifest_returns_blocked(self):
        stage_name = "06_hypothesis_1"
        json_path = os.path.join(self.test_dir, f"{stage_name}.json")
        md_path = os.path.join(self.test_dir, f"{stage_name}.md")
        docx_path = os.path.join(self.test_dir, f"{stage_name}.docx")

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"stage_id": stage_name, "sample_size": 100, "f_stat": 4.5}, f)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Findings\n\nF = 4.50, p < .001.\n")
        self._create_minimal_docx(docx_path, "F = 4.50")

        manifest_path = os.path.join(self.test_dir, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as mf:
            json.dump({
                "contract_version": "1.0.0",
                "stage_id": stage_name,
                "project_id": "test_project",
                "producer": {"agent": "statistics-agent", "script_or_generator": "stats.py"},
                "inputs": [],
                "required_artifacts": [
                    {"path": f"{stage_name}.json", "type": "stats_json", "required": True},
                    {"path": f"{stage_name}.md", "type": "narrative_markdown", "required": True},
                    {"path": f"{stage_name}.docx", "type": "openxml_word", "required": True}
                ],
                "dependencies": [
                    {
                        "stage_id": "04_assumptions",
                        "manifest_path": "nonexistent_upstream/manifest.json",
                        "manifest_hash": "deadbeef"
                    }
                ],
                "hashes": {
                    f"{stage_name}.json": compute_sha256(json_path),
                    f"{stage_name}.md": compute_sha256(md_path),
                    f"{stage_name}.docx": compute_sha256(docx_path)
                },
                "status": "GENERATED",
                "timestamps": {"created_at": "2026-09-19T00:00:00Z", "completed_at": "2026-09-19T00:00:00Z"}
            }, mf)

        report = run_suite(self.test_dir, stage_id=stage_name, require_manifest=True)
        self.assertEqual(report["overall_verdict"], "BLOCKED")
        self.assertTrue(any("dependency manifest" in e.lower() for e in report["errors"]))

    def test_09_dependency_manifest_hash_mismatch_returns_fail(self):
        stage_name = "06_hypothesis_1"
        json_path = os.path.join(self.test_dir, f"{stage_name}.json")
        md_path = os.path.join(self.test_dir, f"{stage_name}.md")
        docx_path = os.path.join(self.test_dir, f"{stage_name}.docx")

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"stage_id": stage_name, "sample_size": 100, "f_stat": 4.5}, f)
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Findings\n\nF = 4.50, p < .001.\n")
        self._create_minimal_docx(docx_path, "F = 4.50")

        upstream_dir = os.path.join(self.test_dir, "upstream")
        os.makedirs(upstream_dir, exist_ok=True)
        dep_manifest_path = os.path.join(upstream_dir, "manifest.json")
        with open(dep_manifest_path, "w", encoding="utf-8") as df:
            json.dump({"contract_version": "1.0.0", "stage_id": "04_assumptions"}, df)

        manifest_path = os.path.join(self.test_dir, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as mf:
            json.dump({
                "contract_version": "1.0.0",
                "stage_id": stage_name,
                "project_id": "test_project",
                "producer": {"agent": "statistics-agent", "script_or_generator": "stats.py"},
                "inputs": [],
                "required_artifacts": [
                    {"path": f"{stage_name}.json", "type": "stats_json", "required": True},
                    {"path": f"{stage_name}.md", "type": "narrative_markdown", "required": True},
                    {"path": f"{stage_name}.docx", "type": "openxml_word", "required": True}
                ],
                "dependencies": [
                    {
                        "stage_id": "04_assumptions",
                        "manifest_path": "upstream/manifest.json",
                        "manifest_hash": "0000000000000000000000000000000000000000000000000000000000000000"
                    }
                ],
                "hashes": {
                    f"{stage_name}.json": compute_sha256(json_path),
                    f"{stage_name}.md": compute_sha256(md_path),
                    f"{stage_name}.docx": compute_sha256(docx_path)
                },
                "status": "GENERATED",
                "timestamps": {"created_at": "2026-09-19T00:00:00Z", "completed_at": "2026-09-19T00:00:00Z"}
            }, mf)

        report = run_suite(self.test_dir, stage_id=stage_name, require_manifest=True)
        self.assertEqual(report["overall_verdict"], "FAIL")
        self.assertTrue(any("dependency manifest hash mismatch" in e.lower() for e in report["errors"]))

    def test_10_complete_cascade_affirmative_pass(self):
        stage_name = "06_hypothesis_1"
        json_path = os.path.join(self.test_dir, f"{stage_name}.json")
        md_path = os.path.join(self.test_dir, f"{stage_name}.md")
        docx_path = os.path.join(self.test_dir, f"{stage_name}.docx")

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({"stage_id": stage_name, "sample_size": 100, "f_stat": 4.5, "p_value": 0.001, "f": 4.5}, f)

        element_1 = "فرضیه اول پژوهش به بررسی اثربخشی مداخله بر متغیر وابسته با نمونه ۱۰۰ نفر اختصاص داشت. "
        element_2 = "همان‌طور که در جدول ۱ مشاهده می‌شود، نتایج تحلیل واریانس نشان داد که تفاوت معنادار است. "
        element_3 = "یافته‌های تجربی حاصل از آزمون آماری نشان داد که F = 4.50 و سطح معناداری کمتر از ۰.۰۰۱ است. " * 5
        element_4 = "بنابراین، فرضیه پژوهش تأیید شد و مداخله توانست تغییرات معناداری ایجاد کند. "
        full_text = (element_1 + element_2 + element_3 + element_4) * 2

        with open(md_path, "w", encoding="utf-8") as f:
            f.write(f"# یافته‌های فرضیه اول\n\nSample N = 100, F = 4.50, p < 0.001.\n\n{full_text}\n\n| متغیر | میانگین | F | p |\n|---|---|---|---|\n| متغیر | 24.50 | 4.50 | 0.001 |\n")

        body_xml = f"""
        <w:p>
          <w:pPr><w:jc w:val="both"/><w:bidi w:val="1"/></w:pPr>
          <w:r><w:t>{full_text}</w:t></w:r>
        </w:p>
        <w:p>
          <w:pPr><w:bidi w:val="1"/></w:pPr>
          <w:r>
            <w:rPr><w:rFonts w:ascii="B Nazanin" w:cs="B Nazanin"/><w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr>
            <w:t>جدول ۱. نتایج آزمون تحلیل واریانس فرضیه اول</w:t>
          </w:r>
        </w:p>
        <w:tbl>
          <w:tblPr>
            <w:bidiVisual/>
            <w:tblBorders>
              <w:top w:val="single" w:sz="6"/>
              <w:bottom w:val="single" w:sz="6"/>
              <w:left w:val="none"/><w:right w:val="none"/>
              <w:insideV w:val="none"/><w:insideH w:val="none"/>
            </w:tblBorders>
          </w:tblPr>
          <w:tr>
            <w:tc><w:p><w:r><w:t>متغیر</w:t></w:r></w:p></w:tc>
            <w:tc><w:p><w:r><w:t>میانگین</w:t></w:r></w:p></w:tc>
            <w:tc><w:p><w:r><w:t>آماره F</w:t></w:r></w:p></w:tc>
            <w:tc><w:p><w:r><w:t>سطح معناداری (p)</w:t></w:r></w:p></w:tc>
          </w:tr>
          <w:tr>
            <w:tc><w:p><w:r><w:t>نمره کل</w:t></w:r></w:p></w:tc>
            <w:tc><w:p><w:r><w:t>۲۴.۵۰</w:t></w:r></w:p></w:tc>
            <w:tc><w:p><w:r><w:t>۴.۵۰</w:t></w:r></w:p></w:tc>
            <w:tc><w:p><w:r><w:t>۰.۰۰۱ > p</w:t></w:r></w:p></w:tc>
          </w:tr>
        </w:tbl>
        <w:p>
          <w:pPr><w:jc w:val="both"/><w:bidi w:val="1"/></w:pPr>
          <w:r><w:t>یادداشت: مقادیر آماره F در سطح معناداری کمتر از ۰.۰۰۱ گزارش شده است.</w:t></w:r>
        </w:p>
        """
        self._create_minimal_docx(docx_path, body_xml=body_xml)

        upstream_dir = os.path.join(self.test_dir, "upstream")
        os.makedirs(upstream_dir, exist_ok=True)
        dep_manifest_path = os.path.join(upstream_dir, "manifest.json")
        with open(dep_manifest_path, "w", encoding="utf-8") as df:
            json.dump({"contract_version": "1.0.0", "stage_id": "04_assumptions"}, df)
        dep_h = compute_sha256(dep_manifest_path)

        manifest_path = os.path.join(self.test_dir, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as mf:
            json.dump({
                "contract_version": "1.0.0",
                "stage_id": stage_name,
                "project_id": "test_project",
                "producer": {"agent": "statistics-agent", "script_or_generator": "stats.py"},
                "inputs": [],
                "required_artifacts": [
                    {"path": f"{stage_name}.json", "type": "stats_json", "required": True},
                    {"path": f"{stage_name}.md", "type": "narrative_markdown", "required": True},
                    {"path": f"{stage_name}.docx", "type": "openxml_word", "required": True}
                ],
                "dependencies": [
                    {
                        "stage_id": "04_assumptions",
                        "manifest_path": "upstream/manifest.json",
                        "manifest_hash": dep_h
                    }
                ],
                "validation_requirements": {
                    "validator_suite_required": True,
                    "expected_verdict": "PASS",
                    "cross_agreement_required": True
                },
                "hashes": {
                    f"{stage_name}.json": compute_sha256(json_path),
                    f"{stage_name}.md": compute_sha256(md_path),
                    f"{stage_name}.docx": compute_sha256(docx_path)
                },
                "status": "VALIDATED",
                "timestamps": {"created_at": "2026-09-19T00:00:00Z", "completed_at": "2026-09-19T00:00:00Z"}
            }, mf)

        report = run_suite(self.test_dir, stage_id=stage_name, require_manifest=True)
        self.assertEqual(report["overall_verdict"], "PASS", f"Validation failed: {report.get('errors')}")
        self.assertGreaterEqual(report["evidence_summary"]["total_evidence_items_evaluated"], 1)
        self.assertEqual(report["evidence_summary"]["checks_failed"], 0)
        self.assertEqual(report["evidence_summary"]["checks_blocked"], 0)
        self.assertEqual(report["evidence_summary"]["checks_unverified"], 0)


if __name__ == "__main__":
    unittest.main()
