#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
tests/test_generate_apa_docx.py — Tests for APA 7 Document Generator (Phase 3)

Validates:
1. Default mode: generates compliant APA 7 .docx and .md with neutral, dataset-derived narratives (zero domain hallucinations).
2. Table-only mode (--table-only / --tables-only): omits narrative explanation paragraphs while preserving tables, captions, and notes.
3. Custom narrative injection (--narrative-json): injects writer-provided narrative blocks into .docx and .md.
4. CLI execution: verifies command-line interface arguments and exit codes.
"""

import os
import sys
import json
import tempfile
import subprocess
import unittest
from docx import Document

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DOCX_GEN_SCRIPT = os.path.join(
    ROOT_DIR, ".agents", "skills", "statistical-data-analyst", "scripts", "generate_apa_docx.py"
)

# Add script directory to sys.path for direct import
sys.path.insert(0, os.path.dirname(DOCX_GEN_SCRIPT))
import generate_apa_docx


def create_sample_payload():
    """Constructs a neutral, multi-section statistical results dictionary."""
    return {
        "demographics": {
            "gender": {
                "مرد": {"count": 45, "percent": 45.0},
                "زن": {"count": 55, "percent": 55.0}
            },
            "education": {
                "کارشناسی": {"count": 60, "percent": 60.0},
                "کارشناسی ارشد": {"count": 40, "percent": 40.0}
            }
        },
        "descriptives": [
            {
                "variable": "تاب‌آوری",
                "mean": 35.40,
                "sd": 6.20,
                "skewness": -0.15,
                "kurtosis": 0.22,
                "min": 18.0,
                "max": 48.0
            },
            {
                "variable": "کیفیت زندگی",
                "mean": 72.80,
                "sd": 11.50,
                "skewness": 0.28,
                "kurtosis": -0.40,
                "min": 45.0,
                "max": 96.0
            }
        ],
        "assumptions_suite": {
            "normality_tests": [
                {
                    "variable": "تاب‌آوری",
                    "ks_stat": 0.065,
                    "ks_p": 0.200,
                    "sw_stat": 0.982,
                    "sw_p": 0.450
                },
                {
                    "variable": "کیفیت زندگی",
                    "ks_stat": 0.071,
                    "ks_p": 0.180,
                    "sw_stat": 0.979,
                    "sw_p": 0.380
                }
            ],
            "multicollinearity_diagnostics": [
                {
                    "variable": "تاب‌آوری",
                    "tolerance": 0.850,
                    "vif": 1.18
                }
            ]
        },
        "correlation": {
            "variables": ["تاب‌آوری", "کیفیت زندگی"],
            "matrix": [
                [1.0, 0.48],
                [0.48, 1.0]
            ]
        },
        "saber_hypotheses": [
            {
                "hypothesis_number": 1,
                "hypothesis_title": "تاب‌آوری توان پیش‌بینی معنادار کیفیت زندگی را دارد.",
                "criterion": "کیفیت زندگی",
                "predictors": ["تاب‌آوری"],
                "tier1_correlation_summary": {
                    "criterion": "کیفیت زندگی",
                    "predictors": [
                        {
                            "name": "تاب‌آوری",
                            "r": 0.48,
                            "p": 0.001,
                            "significance": "معنادار (p < .01)"
                        }
                    ]
                },
                "tier2_anova_summary": {
                    "regression": {
                        "R": 0.48,
                        "R2": 0.23,
                        "Adj_R2": 0.22,
                        "SE_estimate": 10.15,
                        "F": 29.35,
                        "p_anova": 0.0001
                    }
                },
                "tier3_coefficients": [
                    {
                        "variable": "عرض از مبدأ",
                        "B": 41.20,
                        "SE": 5.80,
                        "Beta": None,
                        "t": 7.10,
                        "p": 0.0001,
                        "tolerance": None,
                        "vif": None
                    },
                    {
                        "variable": "تاب‌آوری",
                        "B": 0.89,
                        "SE": 0.16,
                        "Beta": 0.48,
                        "t": 5.42,
                        "p": 0.0001,
                        "tolerance": 1.0,
                        "vif": 1.0
                    }
                ],
                "verdict": "تأیید شد"
            }
        ],
        "repeated_measures": {
            "dv_label": "بهزیستی روان‌شناختی",
            "sample_size": 50,
            "descriptives": [
                {"time_label": "پیش‌آزمون", "mean": 45.2, "sd": 7.1, "se": 1.0, "ci_lower": 43.2, "ci_upper": 47.2},
                {"time_label": "پس‌آزمون", "mean": 58.6, "sd": 6.8, "se": 0.96, "ci_lower": 56.7, "ci_upper": 60.5}
            ],
            "mauchly_sphericity": {"w": 0.65, "chi2": 15.2, "df": 2, "p_value": 0.001},
            "epsilon": {"greenhouse_geisser": 0.74, "huynh_feldt": 0.78},
            "primary_test": {
                "f_statistic": 42.15,
                "df_effect_reported": 1.48,
                "df_error_reported": 72.52,
                "p_reported": 0.0001,
                "partial_eta_squared": 0.46
            },
            "anova_table": [
                {
                    "source": "Time",
                    "model": "Greenhouse-Geisser",
                    "sum_sq": 1250.4,
                    "df": 1.48,
                    "mean_sq": 844.8,
                    "f_stat": 42.15,
                    "p_val": 0.0001,
                    "partial_eta_sq": 0.46
                }
            ],
            "pairwise_contrasts": [
                {
                    "time_a": "Time_1",
                    "time_b": "Time_2",
                    "mean_diff": -13.4,
                    "se_diff": 2.06,
                    "t": -6.5,
                    "df": 49,
                    "p_adj": 0.0001,
                    "cohen_dz": 0.92,
                    "significant_05": True
                }
            ]
        }
    }


class TestGenerateApaDocx(unittest.TestCase):
    """Test suite for generate_apa_docx.py refactor."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.payload = create_sample_payload()

    def tearDown(self):
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)

    def test_01_default_generation_creates_triad_files_with_neutral_narratives(self):
        """Default generation must produce both .docx and .md with zero clinical hallucinations."""
        docx_path = os.path.join(self.temp_dir, "test_default.docx")
        md_path = os.path.join(self.temp_dir, "test_default.md")

        generate_apa_docx.build_chapter4_document(self.payload, docx_path, table_only=False)
        generate_apa_docx.export_markdown_chapter4(self.payload, md_path, table_only=False)

        self.assertTrue(os.path.exists(docx_path), "Default .docx file not generated")
        self.assertTrue(os.path.exists(md_path), "Default .md file not generated")

        # Verify zero clinical anxiety / parenting style hallucinations in text
        doc = Document(docx_path)
        all_doc_text = " ".join(p.text for p in doc.paragraphs)
        with open(md_path, "r", encoding="utf-8") as f:
            md_text = f.read()

        hallucination_terms = [
            "اضطراب فراگیر",
            "عدم تحمل عدم قطعیت",
            "نگرانی بیمارگونه",
            "تجارب خانواده مبدأ",
            "سبک‌های فرزندپروری"
        ]
        for term in hallucination_terms:
            self.assertNotIn(term, all_doc_text, f"Hallucinated clinical term '{term}' found in .docx")
            self.assertNotIn(term, md_text, f"Hallucinated clinical term '{term}' found in .md")

        # Check that actual variable names exist
        self.assertIn("تاب‌آوری", all_doc_text)
        self.assertIn("کیفیت زندگی", all_doc_text)
        self.assertIn("تاب‌آوری", md_text)
        self.assertIn("کیفیت زندگی", md_text)

    def test_02_table_only_mode_omits_narrative_paragraphs_in_docx(self):
        """In table_only=True mode, .docx must contain tables and captions but NO narrative explanation paragraphs."""
        docx_normal = os.path.join(self.temp_dir, "test_normal.docx")
        docx_table_only = os.path.join(self.temp_dir, "test_table_only.docx")

        generate_apa_docx.build_chapter4_document(self.payload, docx_normal, table_only=False)
        generate_apa_docx.build_chapter4_document(self.payload, docx_table_only, table_only=True)

        doc_norm = Document(docx_normal)
        doc_tbl = Document(docx_table_only)

        # Both documents must have the same number of tables
        self.assertEqual(len(doc_norm.tables), len(doc_tbl.tables), "Table count differs in table-only mode")
        self.assertGreater(len(doc_tbl.tables), 0, "No tables created in table-only mode")

        # Table-only document must have significantly fewer paragraphs (only headings and captions/notes)
        self.assertLess(
            len(doc_tbl.paragraphs),
            len(doc_norm.paragraphs),
            "Table-only document should have fewer paragraphs than normal document"
        )

        # Check that standard narrative phrases are absent in table_only
        narrative_phrases = [
            "در این بخش، یافته‌های حاصل از تجزیه‌وتحلیل آماری",
            "به‌منظور بررسی روابط درونی اولیه بین متغیرها",
            "مجموع یافته‌های به‌دست‌آمده از تحلیل آماری داده‌ها در این فصل مؤید آن است",
            "پیش از اجرای آزمون‌های استنباطی، مفروضه‌های نرمال بودن"
        ]
        tbl_text = " ".join(p.text for p in doc_tbl.paragraphs)
        for phrase in narrative_phrases:
            self.assertNotIn(phrase, tbl_text, f"Narrative phrase '{phrase}' found in table-only .docx")

        # Captions must still be present
        self.assertIn("جدول ۱-۴", tbl_text)

    def test_03_table_only_mode_omits_narrative_paragraphs_in_md(self):
        """In table_only=True mode, .md must render clean markdown tables with headers and captions without prose narratives."""
        md_normal = os.path.join(self.temp_dir, "test_normal.md")
        md_table_only = os.path.join(self.temp_dir, "test_table_only.md")

        generate_apa_docx.export_markdown_chapter4(self.payload, md_normal, table_only=False)
        generate_apa_docx.export_markdown_chapter4(self.payload, md_table_only, table_only=True)

        with open(md_normal, "r", encoding="utf-8") as f:
            text_norm = f.read()
        with open(md_table_only, "r", encoding="utf-8") as f:
            text_tbl = f.read()

        # Both must have table separators and pipes
        self.assertIn("| :--- |", text_tbl)
        self.assertIn("### جدول ۱-۴", text_tbl)

        # Normal text contains narrative intro, table-only should not
        self.assertIn("در این فصل، یافته‌های حاصل از تجزیه‌وتحلیل", text_norm)
        self.assertNotIn("در این فصل، یافته‌های حاصل از تجزیه‌وتحلیل", text_tbl)

    def test_04_custom_narrative_injection(self):
        """Injected custom narrative blocks must appear in generated .docx and .md."""
        docx_path = os.path.join(self.temp_dir, "test_custom.docx")
        md_path = os.path.join(self.temp_dir, "test_custom.md")

        custom_narratives = {
            "chapter_intro": "این مقدمه اختصاصی توسط عامل نویسنده دانشگاهی تدوین گردیده است.",
            "demographics": "تحلیل ویژگی‌های جمعیت‌شناختی آزمودنی‌ها نشان‌دهنده توزیع متعادل جنسیتی است.",
            "concluding_transition": "این انتقال پایانی اختصاصی فصل چهارم به پنجم است."
        }

        generate_apa_docx.build_chapter4_document(
            self.payload, docx_path, table_only=False, narratives=custom_narratives
        )
        generate_apa_docx.export_markdown_chapter4(
            self.payload, md_path, table_only=False, narratives=custom_narratives
        )

        doc = Document(docx_path)
        doc_text = " ".join(p.text for p in doc.paragraphs)
        with open(md_path, "r", encoding="utf-8") as f:
            md_text = f.read()

        for key, text_val in custom_narratives.items():
            self.assertIn(text_val, doc_text, f"Custom narrative '{text_val}' not found in .docx")
            self.assertIn(text_val, md_text, f"Custom narrative '{text_val}' not found in .md")

    def test_05_cli_execution_with_flags(self):
        """CLI execution with --table-only and --narrative-json must succeed with exit code 0."""
        json_path = os.path.join(self.temp_dir, "payload.json")
        narr_path = os.path.join(self.temp_dir, "narratives.json")
        out_docx = os.path.join(self.temp_dir, "cli_output.docx")
        out_md = os.path.join(self.temp_dir, "cli_output.md")

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(self.payload, f, ensure_ascii=False)

        custom_narr = {
            "chapter_intro": "مقدمه تست خط فرمان CLI"
        }
        with open(narr_path, "w", encoding="utf-8") as f:
            json.dump(custom_narr, f, ensure_ascii=False)

        cmd = [
            sys.executable,
            DOCX_GEN_SCRIPT,
            "--json", json_path,
            "--out", out_docx,
            "--out-md", out_md,
            "--table-only",
            "--narrative-json", narr_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"CLI command failed with stderr: {result.stderr}")
        self.assertTrue(os.path.exists(out_docx), "CLI failed to generate .docx")
        self.assertTrue(os.path.exists(out_md), "CLI failed to generate .md")


if __name__ == "__main__":
    unittest.main()
