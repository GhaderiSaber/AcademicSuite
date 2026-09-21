# -*- coding: utf-8 -*-
"""
tests/test_dynamic_fixtures_healing.py — Regression Test for Self-Healing Test Fixture Generation

Verifies:
1. scripts.generate_scale_validation_benchmark_data exports generate_scale_validation_data.
2. ensure_fixtures_present() completely and reliably heals a clean, empty fixture directory.
3. All 9 required vertical-slice fixture studies are generated with non-empty files.
4. Fixture generation is fully idempotent.
"""

import os
import sys
import tempfile
import unittest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)
AGENTS_DIR = os.path.join(ROOT_DIR, ".agents")
if AGENTS_DIR not in sys.path:
    sys.path.insert(0, AGENTS_DIR)
SCRIPTS_DIR = os.path.join(AGENTS_DIR, "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from scripts.generate_test_fixtures import (
    check_fixtures_status,
    ensure_fixtures_present,
    generate_all_benchmark_datasets,
    REQUIRED_FIXTURE_STUDIES,
)


class TestDynamicFixturesHealing(unittest.TestCase):

    def test_01_scale_validation_generator_exports(self):
        """Verify that generate_scale_validation_benchmark_data exports generate_scale_validation_data."""
        from scripts import generate_scale_validation_benchmark_data as sv_mod

        self.assertTrue(hasattr(sv_mod, "generate_scale_validation_data"), "Must export generate_scale_validation_data")
        self.assertTrue(hasattr(sv_mod, "generate_benchmark_data"), "Must export generate_benchmark_data")
        self.assertTrue(callable(sv_mod.generate_scale_validation_data))
        self.assertTrue(callable(sv_mod.generate_benchmark_data))

    def test_02_self_healing_fixture_generation_in_clean_directory(self):
        """Verify that ensure_fixtures_present generates all 9 studies in a clean environment."""
        with tempfile.TemporaryDirectory(prefix="test_fixtures_clean_") as tmpdir:
            initial_status = check_fixtures_status(tmpdir)
            self.assertFalse(initial_status["all_present"], "Clean directory should initially lack fixtures")

            healed = ensure_fixtures_present(tmpdir)
            self.assertTrue(healed, "ensure_fixtures_present must return True on completion")

            final_status = check_fixtures_status(tmpdir)
            self.assertTrue(final_status["all_present"], f"All 9 fixtures must be present, got: {final_status}")

            for study in REQUIRED_FIXTURE_STUDIES:
                self.assertTrue(final_status["studies"].get(study), f"Study {study} must be marked present")

    def test_03_all_nine_fixtures_integrity(self):
        """Verify that all 9 generated fixture studies contain required, non-empty files."""
        with tempfile.TemporaryDirectory(prefix="test_fixtures_integrity_") as tmpdir:
            generate_all_benchmark_datasets(tmpdir)

            expected_files = {
                "study_vertical_slice_regression": ["01_raw_inputs/data_raw.csv", "01_raw_inputs/data_raw.xlsx"],
                "study_vertical_slice_experimental": ["01_raw_inputs/data_raw.xlsx"],
                "study_vertical_slice_mediation": ["01_raw_inputs/data_raw.xlsx", "01_raw_inputs/data_raw.csv"],
                "study_vertical_slice_moderation": ["01_raw_inputs/data_raw.xlsx"],
                "study_vertical_slice_scale_validation": ["01_raw_inputs/data_raw.xlsx", "01_raw_inputs/data_raw.csv"],
                "study_vertical_slice_sem": ["01_raw_inputs/data_raw.xlsx", "01_raw_inputs/data_raw.csv"],
                "study_vertical_slice_presentation": ["01_raw_inputs/00_defense_findings_payload.json"],
                "study_act_burnout": ["01_raw_inputs/data_raw.xlsx", "academic-state/project.json"],
                "test_study_e2e": ["01_raw_inputs/test_academic_study_data.csv", "academic-state/project.json"],
            }

            for study_name, rel_paths in expected_files.items():
                study_dir = os.path.join(tmpdir, study_name)
                self.assertTrue(os.path.isdir(study_dir), f"Directory {study_name} must exist")
                for rel in rel_paths:
                    file_path = os.path.join(study_dir, rel)
                    self.assertTrue(os.path.isfile(file_path), f"Required file {rel} missing in {study_name}")
                    self.assertGreater(os.path.getsize(file_path), 0, f"File {file_path} must not be empty")

    def test_04_idempotent_regeneration(self):
        """Verify that ensure_fixtures_present does not re-generate or corrupt already present fixtures."""
        with tempfile.TemporaryDirectory(prefix="test_fixtures_idempotent_") as tmpdir:
            ensure_fixtures_present(tmpdir)
            status_1 = check_fixtures_status(tmpdir)
            self.assertTrue(status_1["all_present"])

            # Second call should be instantaneous and preserve all_present
            ensure_fixtures_present(tmpdir)
            status_2 = check_fixtures_status(tmpdir)
            self.assertTrue(status_2["all_present"])


if __name__ == "__main__":
    unittest.main()
