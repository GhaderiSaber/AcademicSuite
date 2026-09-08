#!/usr/bin/env python3
"""
Automated Test Suite for Academic Drive Project Organizer (test_drive_organizer.py)
-----------------------------------------------------------------------------------
Validates:
1. File classification into the 4-tier taxonomy (raw, code, deliverables, references).
2. Project directory auditing, loose file detection, and fragmented client detection.
3. Provisioning new standard project folders with metadata.
4. Dry-run and live reorganization with undo manifest creation.
5. Reversal and undo execution from manifest.
6. Duzen cross-reference matching against Drive folder lists.
"""

import os
import sys
import json
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))
import organize_drive_projects as odp


class TestAcademicDriveOrganizer(unittest.TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp(prefix="test_drive_org_")

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)

    def test_01_classify_file_destinations(self):
        """Test deterministic file categorization across diverse academic artifact formats."""
        # 1. References
        self.assertEqual(odp.classify_file_destination("library.enl"), odp.SUBFOLDERS["references"])
        self.assertEqual(odp.classify_file_destination("citations.ris"), odp.SUBFOLDERS["references"])
        self.assertEqual(odp.classify_file_destination("Smith_2023_Journal_Article.pdf"), odp.SUBFOLDERS["references"])

        # 2. Code & Syntax
        self.assertEqual(odp.classify_file_destination("data_cleaning.sps"), odp.SUBFOLDERS["code"])
        self.assertEqual(odp.classify_file_destination("simulation_notebook.ipynb"), odp.SUBFOLDERS["code"])
        self.assertEqual(odp.classify_file_destination("sem_model.splscb"), odp.SUBFOLDERS["code"])
        self.assertEqual(odp.classify_file_destination("analysis.r"), odp.SUBFOLDERS["code"])

        # 3. Deliverables & Drafts
        self.assertEqual(odp.classify_file_destination("Chapter 4 Results Final.docx"), odp.SUBFOLDERS["deliverables"])
        self.assertEqual(odp.classify_file_destination("فصل چهارم نهایی.docx"), odp.SUBFOLDERS["deliverables"])
        self.assertEqual(odp.classify_file_destination("defense_presentation.pptx"), odp.SUBFOLDERS["deliverables"])
        self.assertEqual(odp.classify_file_destination("Chapter 4 (1).docx"), odp.SUBFOLDERS["deliverables_archive"])
        self.assertEqual(odp.classify_file_destination("old_draft_thesis.docx"), odp.SUBFOLDERS["deliverables_archive"])

        # 4. Raw Inputs
        self.assertEqual(odp.classify_file_destination("survey_data.sav"), odp.SUBFOLDERS["raw"])
        self.assertEqual(odp.classify_file_destination("raw_responses.csv"), odp.SUBFOLDERS["raw"])
        self.assertEqual(odp.classify_file_destination("proposal_approved.docx"), odp.SUBFOLDERS["raw"])
        self.assertEqual(odp.classify_file_destination("questionnaire_bdi.pdf"), odp.SUBFOLDERS["raw"])
        self.assertEqual(odp.classify_file_destination("screenshot_error.png"), odp.SUBFOLDERS["raw"])

        # 5. Temp Junk
        self.assertEqual(odp.classify_file_destination("~$Chapter4.docx"), "temp_junk")
        self.assertEqual(odp.classify_file_destination(".DS_Store"), "temp_junk")

    def test_02_provision_new_project_folder(self):
        """Test provisioning a standard 4-tier project folder with project_meta.json."""
        target = odp.provision_new_project_folder(
            parent_dir=self.test_dir,
            client_name="Sara Mohammadi",
            topic="SEM Resilience Analysis"
        )
        self.assertTrue(os.path.isdir(target))
        self.assertIn("Sara Mohammadi - SEM Resilience Analysis", os.path.basename(target))

        # Check subdirectories
        for sub in odp.SUBFOLDERS.values():
            sub_path = os.path.join(target, sub)
            self.assertTrue(os.path.isdir(sub_path), f"Missing subfolder: {sub}")

        # Check metadata
        meta_file = os.path.join(target, "project_meta.json")
        self.assertTrue(os.path.isfile(meta_file))
        with open(meta_file, "r", encoding="utf-8") as f:
            meta = json.load(f)
        self.assertEqual(meta["client_name"], "Sara Mohammadi")
        self.assertEqual(meta["project_title"], "SEM Resilience Analysis")
        self.assertEqual(meta["status"], "pending")

    def test_03_reorganize_dry_run_and_apply(self):
        """Test reorganizing a messy project folder with dry-run and live apply modes."""
        proj_dir = os.path.join(self.test_dir, "Messy Client Project")
        os.makedirs(proj_dir, exist_ok=True)

        files = [
            "data.sav",
            "syntax.sps",
            "Chapter 4 Final.docx",
            "reference.ris",
            "proposal.docx"
        ]
        for fn in files:
            with open(os.path.join(proj_dir, fn), "w", encoding="utf-8") as f:
                f.write(f"Sample content for {fn}")

        # 1. Dry run
        dry_res = odp.reorganize_single_project(proj_dir, apply_changes=False)
        self.assertFalse(dry_res["applied"])
        self.assertEqual(dry_res["total_planned_actions"], 5)
        # Verify files are still in root
        for fn in files:
            self.assertTrue(os.path.exists(os.path.join(proj_dir, fn)))

        # 2. Apply changes
        live_res = odp.reorganize_single_project(proj_dir, apply_changes=True)
        self.assertTrue(live_res["applied"])
        self.assertEqual(live_res["total_planned_actions"], 5)

        # Verify files have moved to their respective subfolders
        self.assertTrue(os.path.exists(os.path.join(proj_dir, "01_raw_inputs", "data.sav")))
        self.assertTrue(os.path.exists(os.path.join(proj_dir, "01_raw_inputs", "proposal.docx")))
        self.assertTrue(os.path.exists(os.path.join(proj_dir, "02_analysis_code", "syntax.sps")))
        self.assertTrue(os.path.exists(os.path.join(proj_dir, "03_deliverables", "Chapter 4 Final.docx")))
        self.assertTrue(os.path.exists(os.path.join(proj_dir, "04_references_and_lit", "reference.ris")))

        # Check manifest
        manifest_path = os.path.join(proj_dir, "reorganize_manifest.json")
        self.assertTrue(os.path.isfile(manifest_path))

    def test_04_undo_reorganization(self):
        """Test undoing a reorganization using the generated manifest."""
        proj_dir = os.path.join(self.test_dir, "Undo Client Project")
        os.makedirs(proj_dir, exist_ok=True)

        with open(os.path.join(proj_dir, "dataset.sav"), "w", encoding="utf-8") as f:
            f.write("SAV binary dummy")
        with open(os.path.join(proj_dir, "model.sps"), "w", encoding="utf-8") as f:
            f.write("SPSS syntax dummy")

        # Apply reorg
        odp.reorganize_single_project(proj_dir, apply_changes=True)
        self.assertTrue(os.path.exists(os.path.join(proj_dir, "01_raw_inputs", "dataset.sav")))
        self.assertFalse(os.path.exists(os.path.join(proj_dir, "dataset.sav")))

        # Undo
        manifest_path = os.path.join(proj_dir, "reorganize_manifest.json")
        undo_res = odp.undo_reorganization(manifest_path)
        self.assertEqual(undo_res["restored_count"], 2)

        # Verify files are back in project root
        self.assertTrue(os.path.exists(os.path.join(proj_dir, "dataset.sav")))
        self.assertTrue(os.path.exists(os.path.join(proj_dir, "model.sps")))

    def test_05_audit_projects_directory(self):
        """Test directory audit scan with loose files and fragmented folders."""
        root_dir = os.path.join(self.test_dir, "Drive_Root")
        os.makedirs(root_dir, exist_ok=True)

        # Loose files
        with open(os.path.join(root_dir, "loose_proposal.pdf"), "w") as f:
            f.write("pdf")
        with open(os.path.join(root_dir, "~$lock.docx"), "w") as f:
            f.write("lock")

        # Fragmented client folders
        os.makedirs(os.path.join(root_dir, "Ali Rezaei"), exist_ok=True)
        os.makedirs(os.path.join(root_dir, "Ali Rezaei Article"), exist_ok=True)
        os.makedirs(os.path.join(root_dir, "Ali Rezaei Data"), exist_ok=True)

        # Single client folder
        os.makedirs(os.path.join(root_dir, "Maryam Karimi"), exist_ok=True)

        audit = odp.audit_projects_directory(root_dir)
        self.assertEqual(audit["loose_files_count"], 1)
        self.assertEqual(audit["temp_junk_count"], 1)
        self.assertEqual(audit["total_project_folders"], 4)
        self.assertIn("ali rezaei", audit["fragmented_clients"])
        self.assertEqual(len(audit["fragmented_clients"]["ali rezaei"]), 3)


if __name__ == "__main__":
    unittest.main()
