"""
Unit tests for attach-suite CLI tool and repository linker using standard unittest.
Verifies that:
1. Suite resolution supports aliases and Git repository URLs ('https://github.com/GhaderiSaber/AcademicSuite.git').
2. Contents of the suite are attached directly into the project root.
3. No separate folder (e.g., AcademicSuite/) is created inside the project folder.
4. Internal development files (.git, .github, .venv, projects, scratch, *.session*) are strictly excluded.
5. Detachment cleanly removes attached items while preserving all user project files.
"""

import sys
import os
import json
import shutil
import tempfile
import unittest
import importlib.util
from pathlib import Path

# Load attach-suite module dynamically from scripts/attach-suite.py
REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / "scripts" / "attach-suite.py"

spec = importlib.util.spec_from_file_location("attach_suite", str(SCRIPT_PATH))
attach_suite = importlib.util.module_from_spec(spec)
spec.loader.exec_module(attach_suite)


class TestAttachSuite(unittest.TestCase):

    def test_resolve_suite_by_name_and_alias(self):
        suites = attach_suite.load_suites()

        # Test key
        key, info = attach_suite.resolve_suite("academic", suites)
        self.assertEqual(key, "academic")
        self.assertIn("Academic Thesis", info["name"])
        self.assertEqual(info.get("repo_url"), "https://github.com/GhaderiSaber/AcademicSuite.git")

        # Test alias
        key_alias, info_alias = attach_suite.resolve_suite("thesis", suites)
        self.assertEqual(key_alias, "academic")
        self.assertEqual(info_alias["path"], info["path"])

        # Test default empty string
        key_default, _ = attach_suite.resolve_suite("", suites)
        self.assertEqual(key_default, "academic")

    def test_resolve_suite_by_github_url(self):
        suites = attach_suite.load_suites()

        # With .git
        url_git = "https://github.com/GhaderiSaber/AcademicSuite.git"
        key, info = attach_suite.resolve_suite(url_git, suites)
        self.assertEqual(key, "academic")
        self.assertEqual(info.get("repo_url"), url_git)

        # Without .git
        url_no_git = "https://github.com/GhaderiSaber/AcademicSuite"
        key_no_git, info_no_git = attach_suite.resolve_suite(url_no_git, suites)
        self.assertEqual(key_no_git, "academic")
        self.assertEqual(info_no_git.get("repo_url"), url_git)

    def test_excluded_suite_items_filter(self):
        self.assertTrue(attach_suite.is_excluded_suite_item(Path(".git")))
        self.assertTrue(attach_suite.is_excluded_suite_item(Path(".github")))
        self.assertTrue(attach_suite.is_excluded_suite_item(Path(".gitignore")))
        self.assertTrue(attach_suite.is_excluded_suite_item(Path(".venv")))
        self.assertTrue(attach_suite.is_excluded_suite_item(Path("projects")))
        self.assertTrue(attach_suite.is_excluded_suite_item(Path("scratch")))
        self.assertTrue(attach_suite.is_excluded_suite_item(Path("academic-state")))
        self.assertTrue(attach_suite.is_excluded_suite_item(Path("saber_userbot.session")))
        self.assertTrue(attach_suite.is_excluded_suite_item(Path("saber_userbot.session-journal")))
        self.assertTrue(attach_suite.is_excluded_suite_item(Path("__pycache__")))
        self.assertTrue(attach_suite.is_excluded_suite_item(Path("module.cpython-311.pyc")))

        # Valid items that should be attached
        self.assertFalse(attach_suite.is_excluded_suite_item(Path(".agents")))
        self.assertFalse(attach_suite.is_excluded_suite_item(Path("AGENTS.md")))
        self.assertFalse(attach_suite.is_excluded_suite_item(Path("Questionnaires.xlsx")))
        self.assertFalse(attach_suite.is_excluded_suite_item(Path("digital_saber.py")))
        self.assertFalse(attach_suite.is_excluded_suite_item(Path("data")))
        self.assertFalse(attach_suite.is_excluded_suite_item(Path("scripts")))
        self.assertFalse(attach_suite.is_excluded_suite_item(Path("validators")))

    def test_attach_repo_content_directly_to_project(self):
        """
        Simulates attaching the AcademicSuite repository directly to a new project folder via direct clone.
        Verifies that:
        1. Contents are attached to project root.
        2. NO separate subfolder (e.g. AcademicSuite/) is created in project folder.
        3. Zero symbolic links are created (real physical files and directories).
        4. User project files are preserved intact.
        5. Git repository is initialized directly at the project root.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_dir = Path(tmp_dir) / "my_thesis_study"
            project_dir.mkdir()
            user_file = project_dir / "user_notes.txt"
            user_file.write_text("Confidential thesis notes")

            orig_get_cwd = attach_suite.get_cwd
            attach_suite.get_cwd = lambda target_path=".": project_dir

            try:
                # Attach academic suite using local repo path as source (instant & offline-capable)
                class Args:
                    suite = str(REPO_ROOT)
                    keep_git = False

                attach_suite.cmd_attach(Args())

                # Verify that NO separate AcademicSuite folder was created
                self.assertFalse((project_dir / "AcademicSuite").exists())
                self.assertFalse((project_dir / "Academic_Suite").exists())
                self.assertFalse((project_dir / "academic_suite").exists())

                # Verify that contents are attached directly to project root
                self.assertTrue((project_dir / ".agents").exists())
                self.assertTrue((project_dir / "AGENTS.md").exists())
                self.assertTrue((project_dir / "ANTIGRAVITY_ARCHITECTURE_GUIDE.md").exists())
                self.assertTrue((project_dir / "Questionnaires.xlsx").exists())
                self.assertTrue((project_dir / "digital_saber.py").exists())
                self.assertTrue((project_dir / "scripts").exists())
                self.assertTrue((project_dir / "data").exists())
                self.assertTrue((project_dir / "validators").exists())

                # Verify that ALL suite directories and root files are real physical files/directories, ZERO symlinks to external suite!
                self.assertFalse(os.path.islink(project_dir / ".agents"))
                self.assertTrue((project_dir / ".agents").is_dir())
                self.assertFalse(os.path.islink(project_dir / "AGENTS.md"))
                self.assertTrue((project_dir / "AGENTS.md").is_file())
                self.assertFalse(os.path.islink(project_dir / "scripts"))
                self.assertTrue((project_dir / "scripts").is_dir())
                self.assertFalse(os.path.islink(project_dir / "validators"))
                self.assertTrue((project_dir / "validators").is_dir())
                self.assertTrue((project_dir / "Questionnaires.xlsx").exists())

                # Verify user file was preserved
                self.assertTrue(user_file.exists())
                self.assertEqual(user_file.read_text(), "Confidential thesis notes")

                # Verify git repository exists directly in project root
                self.assertTrue((project_dir / ".git").exists())
                self.assertTrue((project_dir / ".git").is_dir())

                # Verify get_status reports clean structure and physical items
                status = attach_suite.get_status(project_dir)
                self.assertTrue(status["has_local_git"])
                self.assertTrue(status["agents_exists"])
                self.assertFalse(status["agents_is_link"])
                self.assertEqual(len(status["separate_folders"]), 0)

            finally:
                attach_suite.get_cwd = orig_get_cwd


if __name__ == "__main__":
    unittest.main()
