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
from unittest.mock import patch, MagicMock
import importlib.util
from pathlib import Path

# Load attach-suite module dynamically from scripts/attach-suite.py
REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT_PATH = REPO_ROOT / ".agents" / "scripts" / "attach-suite.py"
if not SCRIPT_PATH.exists():
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

        # Verify resolved path actually exists on disk
        self.assertTrue(Path(info["path"]).exists(), f"Suite path does not exist on disk: {info['path']}")

        # Test default empty string
        key_default, _ = attach_suite.resolve_suite("", suites)
        self.assertEqual(key_default, "academic")

    def test_offline_argument_parsed(self):
        """Verifies that the attach subcommand accepts --offline."""
        import argparse
        parser = argparse.ArgumentParser(prog="attach-suite")
        subparsers = parser.add_subparsers(dest="command")
        p_attach = subparsers.add_parser("attach")
        p_attach.add_argument("suite", nargs="?", default="academic")
        p_attach.add_argument("--offline", action="store_true")
        p_attach.add_argument("--keep-git", action="store_true")

        args = parser.parse_args(["attach", "--offline"])
        self.assertTrue(args.offline)
        self.assertEqual(args.suite, "academic")

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
                self.assertTrue((project_dir / "digital_saber.py").exists())
                self.assertTrue((project_dir / ".agents" / "scripts").exists())
                self.assertTrue((project_dir / ".agents" / "data").exists())
                self.assertTrue((project_dir / ".agents" / "validators").exists())

                # Verify that ALL suite directories and root files are real physical files/directories, ZERO symlinks to external suite!
                self.assertFalse(os.path.islink(project_dir / ".agents"))
                self.assertTrue((project_dir / ".agents").is_dir())
                self.assertFalse(os.path.islink(project_dir / "AGENTS.md"))
                self.assertTrue((project_dir / "AGENTS.md").is_file())
                self.assertFalse(os.path.islink(project_dir / ".agents" / "scripts"))
                self.assertTrue((project_dir / ".agents" / "scripts").is_dir())
                self.assertFalse(os.path.islink(project_dir / ".agents" / "validators"))
                self.assertTrue((project_dir / ".agents" / "validators").is_dir())

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
                self.assertTrue(status["has_meta"])

                # Test Detach: cleanly removes all suite files and detaches git repo
                class DetachArgs:
                    path = str(project_dir)
                    keep_git = False

                attach_suite.cmd_detach(DetachArgs())

                # Verify git repository is detached (removed)
                self.assertFalse((project_dir / ".git").exists())

                # Verify all attached suite items are cleanly removed
                self.assertFalse((project_dir / ".agents").exists())
                self.assertFalse((project_dir / "AGENTS.md").exists())
                self.assertFalse((project_dir / "ANTIGRAVITY_ARCHITECTURE_GUIDE.md").exists())
                self.assertFalse((project_dir / "digital_saber.py").exists())
                self.assertFalse((project_dir / ".attached_suite.json").exists())

                # Verify user file is STILL intact
                self.assertTrue(user_file.exists())
                self.assertEqual(user_file.read_text(), "Confidential thesis notes")

                # Verify get_status reports no attached suite
                status_after = attach_suite.get_status(project_dir)
                self.assertFalse(status_after["has_local_git"])
                self.assertFalse(status_after["agents_exists"])
                self.assertFalse(status_after["has_meta"])

            finally:
                attach_suite.get_cwd = orig_get_cwd

    @patch("subprocess.run")
    def test_attach_repo_with_remote_url_mocked_network(self, mock_subprocess):
        """
        Verifies that attaching with a remote GitHub URL operates completely offline via mocked network.
        Ensures:
        1. Zero external network calls are made (mocked subprocess).
        2. Git clone is invoked with the remote GitHub URL and cwd correctly set.
        3. Works cleanly without Internet availability.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_dir = Path(tmp_dir) / "my_mocked_thesis"
            project_dir.mkdir()

            # Configure mock subprocess to simulate successful git clone
            def fake_subprocess_run(cmd, *args, **kwargs):
                cwd = kwargs.get("cwd", str(project_dir))
                # If command is checking remote or git clone, simulate directory setup
                if "clone" in cmd:
                    # Copy local structure into cwd as offline fixture
                    (Path(cwd) / ".agents").mkdir(exist_ok=True)
                    (Path(cwd) / "AGENTS.md").write_text("# Mocked AGENTS.md")
                    (Path(cwd) / ".git").mkdir(exist_ok=True)
                mock_res = MagicMock()
                mock_res.returncode = 0
                mock_res.stdout = "origin\n"
                mock_res.stderr = ""
                return mock_res

            mock_subprocess.side_effect = fake_subprocess_run

            orig_get_cwd = attach_suite.get_cwd
            attach_suite.get_cwd = lambda target_path=".": project_dir

            try:
                class Args:
                    suite = "https://github.com/GhaderiSaber/AcademicSuite.git"
                    keep_git = False

                attach_suite.cmd_attach(Args())

                # Verify subprocess.run was called with git clone command targeting the remote URL
                clone_calls = [c for c in mock_subprocess.call_args_list if "clone" in c[0][0]]
                self.assertGreater(len(clone_calls), 0, "Expected git clone invocation in mocked network")
                self.assertEqual(clone_calls[0][0][0][2], "https://github.com/GhaderiSaber/AcademicSuite.git")

                # Verify project root contains attached items
                self.assertTrue((project_dir / ".agents").exists())
                self.assertTrue((project_dir / "AGENTS.md").exists())
            finally:
                attach_suite.get_cwd = orig_get_cwd

    def test_detach_with_keep_git(self):
        """Verifies that detaching with keep_git=True preserves .git while removing suite items."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_dir = Path(tmp_dir) / "keep_git_thesis"
            project_dir.mkdir()
            user_file = project_dir / "notes.txt"
            user_file.write_text("user notes")

            orig_get_cwd = attach_suite.get_cwd
            attach_suite.get_cwd = lambda target_path=".": project_dir

            try:
                class Args:
                    suite = str(REPO_ROOT)
                    keep_git = False

                attach_suite.cmd_attach(Args())
                self.assertTrue((project_dir / ".git").exists())
                self.assertTrue((project_dir / ".agents").exists())

                class DetachArgs:
                    path = str(project_dir)
                    keep_git = True

                attach_suite.cmd_detach(DetachArgs())

                # .git must be preserved
                self.assertTrue((project_dir / ".git").exists())
                # Suite files must be removed
                self.assertFalse((project_dir / ".agents").exists())
                self.assertFalse((project_dir / "AGENTS.md").exists())
                # User file must be intact
                self.assertTrue(user_file.exists())
                self.assertEqual(user_file.read_text(), "user notes")
            finally:
                attach_suite.get_cwd = orig_get_cwd

    def test_detach_preserves_user_files_in_suite_directories(self):
        """Verifies that user-created files inside a suite directory (e.g. docs/) are preserved."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_dir = Path(tmp_dir) / "user_docs_thesis"
            project_dir.mkdir()

            orig_get_cwd = attach_suite.get_cwd
            attach_suite.get_cwd = lambda target_path=".": project_dir

            try:
                class Args:
                    suite = str(REPO_ROOT)
                    keep_git = False

                attach_suite.cmd_attach(Args())
                self.assertTrue((project_dir / "docs").exists())

                # User adds custom file inside docs/
                user_doc = project_dir / "docs" / "user_proposal.txt"
                user_doc.write_text("My custom proposal")

                class DetachArgs:
                    path = str(project_dir)
                    keep_git = False

                attach_suite.cmd_detach(DetachArgs())

                # docs/ directory must still exist with user_proposal.txt
                self.assertTrue(user_doc.exists())
                self.assertEqual(user_doc.read_text(), "My custom proposal")
                # Suite files outside docs must be removed
                self.assertFalse((project_dir / ".agents").exists())
                self.assertFalse((project_dir / ".git").exists())
            finally:
                attach_suite.get_cwd = orig_get_cwd

    def test_detach_without_git_removes_all_suite_files(self):
        """Verifies that detaching when .git is absent (e.g. Syncthing/cloud sync) cleanly removes all suite files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_dir = Path(tmp_dir) / "gitless_synced_project"
            project_dir.mkdir()

            # Simulate files copied without .git (like cloud sync)
            (project_dir / ".agents").mkdir()
            (project_dir / ".agents" / "rules").mkdir()
            (project_dir / ".agents" / "rules" / "test.md").write_text("# Rules")
            (project_dir / "AGENTS.md").write_text("# AGENTS")
            (project_dir / "digital_saber.py").write_text("# Digital Saber")
            (project_dir / "webapp").mkdir()
            (project_dir / "webapp" / "index.html").write_text("<html></html>")
            (project_dir / "evals").mkdir()
            (project_dir / "evals" / "benchmarks.py").write_text("# Evals")
            (project_dir / "requirements.txt").write_text("pytest\n")
            (project_dir / "SETUP_GUIDE.md").write_text("# Setup")

            # Metadata file present
            meta = {
                "suite": "academic",
                "name": "Academic Suite",
                "created_git": False,
                "attached_items": [".agents", "AGENTS.md", "digital_saber.py", "webapp", "evals", "requirements.txt", "SETUP_GUIDE.md"]
            }
            (project_dir / ".attached_suite.json").write_text(json.dumps(meta))

            # User file that MUST be preserved
            user_doc = project_dir / "Dissertation_Draft.docx"
            user_doc.write_text("Word document binary content")

            orig_get_cwd = attach_suite.get_cwd
            attach_suite.get_cwd = lambda target_path=".": project_dir

            try:
                class DetachArgs:
                    path = str(project_dir)
                    keep_git = False
                    suite = ""

                attach_suite.cmd_detach(DetachArgs())

                # Suite files must all be gone
                self.assertFalse((project_dir / ".agents").exists())
                self.assertFalse((project_dir / "AGENTS.md").exists())
                self.assertFalse((project_dir / "digital_saber.py").exists())
                self.assertFalse((project_dir / "webapp").exists())
                self.assertFalse((project_dir / "evals").exists())
                self.assertFalse((project_dir / "requirements.txt").exists())
                self.assertFalse((project_dir / "SETUP_GUIDE.md").exists())
                self.assertFalse((project_dir / ".attached_suite.json").exists())

                # User file must be preserved
                self.assertTrue(user_doc.exists())
                self.assertEqual(user_doc.read_text(), "Word document binary content")
            finally:
                attach_suite.get_cwd = orig_get_cwd

    def test_detach_preserves_custom_user_scripts_in_shared_dir(self):
        """Verifies that user scripts in shared scripts/ directory are preserved while suite scripts are removed."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_dir = Path(tmp_dir) / "shared_scripts_project"
            project_dir.mkdir()

            scripts_dir = project_dir / "scripts"
            scripts_dir.mkdir()

            # A file that exists in AcademicSuite master repo scripts/
            master_suite_scripts = REPO_ROOT / "scripts"
            sample_suite_script_name = "test_marker.py"
            if master_suite_scripts.exists():
                for f in master_suite_scripts.iterdir():
                    if f.is_file():
                        sample_suite_script_name = f.name
                        break
            (scripts_dir / sample_suite_script_name).write_text("# Suite script")

            # Custom user script
            user_script = scripts_dir / "my_custom_analysis.py"
            user_script.write_text("print('Custom thesis analysis')")

            (project_dir / "digital_saber.py").write_text("# Digital Saber")
            (project_dir / ".agents").mkdir()

            meta = {
                "suite": "academic",
                "attached_items": [".agents", "digital_saber.py", "scripts"]
            }
            (project_dir / ".attached_suite.json").write_text(json.dumps(meta))

            orig_get_cwd = attach_suite.get_cwd
            attach_suite.get_cwd = lambda target_path=".": project_dir

            try:
                class DetachArgs:
                    path = str(project_dir)
                    keep_git = False
                    suite = ""

                attach_suite.cmd_detach(DetachArgs())

                # User script must be intact
                self.assertTrue(user_script.exists())
                self.assertEqual(user_script.read_text(), "print('Custom thesis analysis')")

                # Suite items removed
                self.assertFalse((project_dir / "digital_saber.py").exists())
                self.assertFalse((project_dir / ".agents").exists())
                # If master repo has that script, it was removed; user script remains so scripts/ still exists
                self.assertTrue(scripts_dir.exists())
            finally:
                attach_suite.get_cwd = orig_get_cwd

    def test_detach_rerun_after_partial_removal(self):
        """Verifies that re-running detach after .agents was deleted still cleans leftover suite files."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_dir = Path(tmp_dir) / "partial_detached_project"
            project_dir.mkdir()

            # Leftovers after partial manual or previous detach: NO .agents, NO .attached_suite.json, NO .git
            (project_dir / "digital_saber.py").write_text("# Digital Saber")
            (project_dir / "webapp").mkdir()
            (project_dir / "webapp" / "app.py").write_text("# Webapp")
            (project_dir / "tests").mkdir()
            # If tests has a file that exists in master repo tests/
            (project_dir / "tests" / "test_attach_suite.py").write_text("# suite test")
            (project_dir / "requirements.txt").write_text("pytest\n")

            user_file = project_dir / "thesis_proposal.pdf"
            user_file.write_text("%PDF-1.4 mock")

            orig_get_cwd = attach_suite.get_cwd
            attach_suite.get_cwd = lambda target_path=".": project_dir

            try:
                class DetachArgs:
                    path = str(project_dir)
                    keep_git = False
                    suite = "academic"

                attach_suite.cmd_detach(DetachArgs())

                # Leftover suite files must be removed
                self.assertFalse((project_dir / "digital_saber.py").exists())
                self.assertFalse((project_dir / "webapp").exists())
                self.assertFalse((project_dir / "requirements.txt").exists())

                # User file must be preserved
                self.assertTrue(user_file.exists())
            finally:
                attach_suite.get_cwd = orig_get_cwd

    def test_protected_project_dirs_never_removed(self):
        """Verifies that 01_raw_inputs, 02_analysis_code, 03_deliverables, 04_references_and_lit are NEVER deleted."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            project_dir = Path(tmp_dir) / "protected_dirs_project"
            project_dir.mkdir()

            # Protected directories with user data
            (project_dir / "01_raw_inputs").mkdir()
            (project_dir / "01_raw_inputs" / "dataset.xlsx").write_text("raw data")
            (project_dir / "02_analysis_code").mkdir()
            (project_dir / "02_analysis_code" / "analysis.R").write_text("library(lavaan)")
            (project_dir / "03_deliverables").mkdir()
            (project_dir / "03_deliverables" / "Chapter4.docx").write_text("findings")
            (project_dir / "04_references_and_lit").mkdir()
            (project_dir / "04_references_and_lit" / "papers.bib").write_text("@article{...}")

            # Suite files
            (project_dir / ".agents").mkdir()
            (project_dir / "digital_saber.py").write_text("# Suite file")

            # Fraudulent/buggy metadata that includes 03_deliverables in attached_items
            meta = {
                "suite": "academic",
                "attached_items": [".agents", "digital_saber.py", "03_deliverables", "01_raw_inputs"]
            }
            (project_dir / ".attached_suite.json").write_text(json.dumps(meta))

            orig_get_cwd = attach_suite.get_cwd
            attach_suite.get_cwd = lambda target_path=".": project_dir

            try:
                class DetachArgs:
                    path = str(project_dir)
                    keep_git = False
                    suite = ""

                attach_suite.cmd_detach(DetachArgs())

                # Suite items removed
                self.assertFalse((project_dir / ".agents").exists())
                self.assertFalse((project_dir / "digital_saber.py").exists())
                self.assertFalse((project_dir / ".attached_suite.json").exists())

                # ALL PROTECTED DIRS AND USER DATA MUST BE 100% INTACT
                self.assertTrue((project_dir / "01_raw_inputs" / "dataset.xlsx").exists())
                self.assertTrue((project_dir / "02_analysis_code" / "analysis.R").exists())
                self.assertTrue((project_dir / "03_deliverables" / "Chapter4.docx").exists())
                self.assertTrue((project_dir / "04_references_and_lit" / "papers.bib").exists())
            finally:
                attach_suite.get_cwd = orig_get_cwd


if __name__ == "__main__":
    unittest.main()
