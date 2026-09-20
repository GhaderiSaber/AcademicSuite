#!/usr/bin/env python3
"""
permission_manager.py — AcademicSuite Native Permission & Least Privilege Architecture

Enforces operating system filesystem permissions as the primary security boundary:
- RAW DATA: Strictly read-only (0444 / S_IREAD)
- DERIVED DATA: Read-write for owner (0644 / S_IWRITE)
- STATE: Read-write for owner (0644)
- ARTIFACTS: Read-write during drafting (0644), read-only when sealed (0444)
- SOURCE CODE: Read-write for owner, protected (0644)
- SCRIPTS: Executable deterministic tools (0755)
- CONFIGURATION: Read-only or protected read-write (0644 / 0444)

Handles platform differences between POSIX (Linux/macOS) and Windows (NT).
"""

import os
import sys
import stat
import json
import argparse
import re
from typing import Dict, Any, List, Optional, Tuple

# Categories
CAT_RAW_DATA = "raw_data"
CAT_DERIVED_DATA = "derived_data"
CAT_STATE = "state"
CAT_ARTIFACTS = "artifacts"
CAT_SOURCE_CODE = "source_code"
CAT_SCRIPTS = "scripts"
CAT_CONFIGURATION = "configuration"

CATEGORIES = [
    CAT_RAW_DATA,
    CAT_DERIVED_DATA,
    CAT_STATE,
    CAT_ARTIFACTS,
    CAT_SOURCE_CODE,
    CAT_SCRIPTS,
    CAT_CONFIGURATION
]

# POSIX permission masks
POSIX_PERMS = {
    CAT_RAW_DATA: {"file": 0o444, "dir": 0o555},
    CAT_DERIVED_DATA: {"file": 0o644, "dir": 0o755},
    CAT_STATE: {"file": 0o644, "dir": 0o755},
    CAT_ARTIFACTS: {"file": 0o644, "dir": 0o755},
    CAT_SOURCE_CODE: {"file": 0o644, "dir": 0o755},
    CAT_SCRIPTS: {"file": 0o755, "dir": 0o755},
    CAT_CONFIGURATION: {"file": 0o644, "dir": 0o755},
}


class PermissionManager:
    """Manages filesystem permissions adhering to least-privilege principles."""

    def __init__(self, repo_root: Optional[str] = None):
        if repo_root:
            self.repo_root = os.path.abspath(repo_root)
        else:
            self.repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        self.is_windows = (sys.platform == "win32")

    def classify_path(self, path: str) -> str:
        """
        Classifies any file or directory path into one of 7 security tiers:
        - raw_data
        - derived_data
        - state
        - artifacts
        - source_code
        - scripts
        - configuration
        """
        norm = os.path.normpath(path).replace("\\", "/")
        basename = os.path.basename(norm).lower()
        parts = norm.split("/")
        parts_lower = [p.lower() for p in parts]

        # 1. Raw Data
        raw_dir_indicators = {
            "raw", "raw_data", "raw_inputs", "01_raw_inputs", "01_raw",
            "raw-data", "raw_dataset", "raw_files"
        }
        for p in parts_lower[:-1]:
            if p in raw_dir_indicators or "raw_input" in p or "raw_data" in p or "raw_dataset" in p:
                return CAT_RAW_DATA

        raw_exact_files = {
            "raw.xlsx", "raw.csv", "raw.sav", "raw.tsv",
            "data_raw.xlsx", "data_raw.csv", "data_raw.sav",
            "dataset_raw.xlsx", "dataset_raw.csv", "dataset_raw.sav",
            "raw_dataset.xlsx", "raw_dataset.csv", "raw_dataset.sav"
        }
        if basename in raw_exact_files:
            return CAT_RAW_DATA
        if any(basename.startswith(pre) for pre in ("raw_", "raw-")):
            return CAT_RAW_DATA
        if "_raw." in basename or "-raw." in basename:
            return CAT_RAW_DATA

        # 2. State
        if "state" in parts_lower or "memory" in parts_lower:
            return CAT_STATE
        state_exact_files = {
            "events.jsonl", "pitfalls.jsonl", "projects.jsonl",
            "audit_log.jsonl", "academic_state.json"
        }
        if basename in state_exact_files:
            return CAT_STATE

        # 3. Derived / Curated Data
        derived_dir_indicators = {
            "02_clean_and_scored", "derived_data", "curated_data",
            "curated", "cleaned_data"
        }
        for p in parts_lower[:-1]:
            if p in derived_dir_indicators:
                return CAT_DERIVED_DATA
        if "curated" in basename or "cleaned" in basename or "scored" in basename:
            if basename.endswith((".xlsx", ".csv", ".sav", ".json")):
                return CAT_DERIVED_DATA

        # 4. Artifacts / Deliverables
        artifact_dir_indicators = {
            "03_deliverables", "artifacts", "deliverables", "stage_deliverables"
        }
        for p in parts_lower[:-1]:
            if p in artifact_dir_indicators or p.startswith("stage_"):
                return CAT_ARTIFACTS
        if basename.endswith((".docx", ".pptx", ".pdf")):
            return CAT_ARTIFACTS

        # 5. Configuration & Contracts
        config_exact_files = {
            "hooks.json", "agents.md", "pyproject.toml", "requirements.txt",
            ".gitignore", ".gitattributes"
        }
        if basename in config_exact_files:
            return CAT_CONFIGURATION
        if "contracts" in parts_lower and basename.endswith(".schema.json"):
            return CAT_CONFIGURATION
        if ".agents" in parts_lower and "rules" in parts_lower:
            return CAT_CONFIGURATION

        # 6. Scripts (Deterministic executable tools)
        if basename.endswith((".sh", ".bat", ".cmd")):
            return CAT_SCRIPTS
        if "scripts" in parts_lower and basename.endswith(".py"):
            return CAT_SCRIPTS

        # 7. Source Code (Default fallback for code & contracts)
        return CAT_SOURCE_CODE

    def get_expected_mode(self, category: str, is_dir: bool = False) -> int:
        """Returns the expected POSIX octal mode for a category and entry type."""
        target = POSIX_PERMS.get(category, POSIX_PERMS[CAT_SOURCE_CODE])
        return target["dir"] if is_dir else target["file"]

    def enforce_file_permission(self, target_path: str, category: Optional[str] = None) -> bool:
        """
        Enforces least privilege permissions on a physical file or directory.
        Handles POSIX vs Windows differences safely.
        """
        if not os.path.exists(target_path):
            return False

        if category is None:
            category = self.classify_path(target_path)

        is_dir = os.path.isdir(target_path)

        try:
            if self.is_windows:
                # Windows permission model via stat attributes
                if category == CAT_RAW_DATA and not is_dir:
                    # Mark read-only
                    os.chmod(target_path, stat.S_IREAD)
                else:
                    # Ensure writable
                    os.chmod(target_path, stat.S_IREAD | stat.S_IWRITE)
                return True
            else:
                # POSIX permission model
                expected_mode = self.get_expected_mode(category, is_dir=is_dir)
                current_mode = stat.S_IMODE(os.lstat(target_path).st_mode)
                if current_mode != expected_mode:
                    os.chmod(target_path, expected_mode)
                return True
        except Exception as e:
            sys.stderr.write(f"[PermissionManager] Error setting perms on '{target_path}': {e}\n")
            return False

    def lock_raw_data_directory(self, dir_path: str) -> int:
        """
        Recursively locks down all files in a raw inputs directory to strictly read-only (0444 / S_IREAD).
        Returns the number of files locked.
        """
        if not os.path.exists(dir_path):
            return 0
        count = 0
        if os.path.isfile(dir_path):
            if self.enforce_file_permission(dir_path, CAT_RAW_DATA):
                count += 1
            return count

        for root, dirs, files in os.walk(dir_path):
            for f in files:
                fp = os.path.join(root, f)
                if self.enforce_file_permission(fp, CAT_RAW_DATA):
                    count += 1
        return count

    def audit_path(self, target_path: str) -> Dict[str, Any]:
        """Audits an individual path and reports whether it satisfies least privilege."""
        if not os.path.exists(target_path):
            return {
                "path": target_path,
                "exists": False,
                "status": "MISSING"
            }

        category = self.classify_path(target_path)
        is_dir = os.path.isdir(target_path)
        mode = stat.S_IMODE(os.lstat(target_path).st_mode)

        if self.is_windows:
            is_readonly = not bool(mode & stat.S_IWRITE)
            expected_readonly = (category == CAT_RAW_DATA and not is_dir)
            compliant = (is_readonly == expected_readonly)
            return {
                "path": target_path,
                "exists": True,
                "is_dir": is_dir,
                "category": category,
                "platform": "windows",
                "is_readonly": is_readonly,
                "expected_readonly": expected_readonly,
                "compliant": compliant,
                "status": "PASS" if compliant else "VIOLATION"
            }
        else:
            expected_mode = self.get_expected_mode(category, is_dir=is_dir)
            compliant = (mode == expected_mode)
            return {
                "path": target_path,
                "exists": True,
                "is_dir": is_dir,
                "category": category,
                "platform": "posix",
                "current_mode": oct(mode),
                "expected_mode": oct(expected_mode),
                "compliant": compliant,
                "status": "PASS" if compliant else "VIOLATION"
            }

    def apply_least_privilege(self, target_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Recursively applies least privilege permissions across the repository.
        Skips .git, __pycache__, and .venv directories to preserve environment integrity.
        """
        scan_dir = target_dir or self.repo_root
        results = {
            "target_dir": scan_dir,
            "processed": 0,
            "updated": 0,
            "errors": 0,
            "categories": {cat: 0 for cat in CATEGORIES}
        }

        skip_dirs = {".git", ".venv", "venv", "__pycache__", "node_modules", ".pytest_cache"}

        for root, dirs, files in os.walk(scan_dir):
            # Prune skipped dirs
            dirs[:] = [d for d in dirs if d not in skip_dirs]

            # Process files
            for f in files:
                file_path = os.path.join(root, f)
                cat = self.classify_path(file_path)
                results["categories"][cat] += 1
                results["processed"] += 1

                audit = self.audit_path(file_path)
                if not audit.get("compliant", True):
                    ok = self.enforce_file_permission(file_path, cat)
                    if ok:
                        results["updated"] += 1
                    else:
                        results["errors"] += 1

        return results

    def audit_repository(self, target_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Audits all repository files against least-privilege baselines and returns violations.
        """
        scan_dir = target_dir or self.repo_root
        violations = []
        total_scanned = 0
        skip_dirs = {".git", ".venv", "venv", "__pycache__", "node_modules", ".pytest_cache"}

        for root, dirs, files in os.walk(scan_dir):
            dirs[:] = [d for d in dirs if d not in skip_dirs]

            for f in files:
                file_path = os.path.join(root, f)
                total_scanned += 1
                audit = self.audit_path(file_path)
                if not audit.get("compliant", True):
                    violations.append(audit)

        return {
            "target_dir": scan_dir,
            "total_scanned": total_scanned,
            "violations_count": len(violations),
            "compliant": len(violations) == 0,
            "violations": violations
        }


def main():
    parser = argparse.ArgumentParser(description="AcademicSuite Filesystem Permission Manager")
    parser.add_argument("--audit", action="store_true", help="Audit repository permissions against least-privilege rules")
    parser.add_argument("--apply", action="store_true", help="Apply least-privilege permissions across repository")
    parser.add_argument("--check-path", type=str, help="Check compliance and classification for a specific path")
    parser.add_argument("--repo-root", type=str, default=None, help="Root directory of the repository")
    parser.add_argument("--json", action="store_true", help="Output results formatted as JSON")
    args = parser.parse_args()

    pm = PermissionManager(repo_root=args.repo_root)

    if args.check_path:
        res = pm.audit_path(args.check_path)
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"Path: {res['path']}")
            print(f"Category: {res.get('category')}")
            print(f"Status: {res.get('status')}")
            if "current_mode" in res:
                print(f"Current Mode: {res['current_mode']} (Expected: {res['expected_mode']})")
            elif "is_readonly" in res:
                print(f"Read-Only: {res['is_readonly']} (Expected: {res['expected_readonly']})")
        sys.exit(0 if res.get("compliant", True) else 1)

    if args.apply:
        res = pm.apply_least_privilege()
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"Applied least privilege across: {res['target_dir']}")
            print(f"Files Processed: {res['processed']}, Updated: {res['updated']}, Errors: {res['errors']}")
            print(f"Category Counts: {res['categories']}")
        sys.exit(0 if res["errors"] == 0 else 1)

    if args.audit or not (args.apply or args.check_path):
        res = pm.audit_repository()
        if args.json:
            print(json.dumps(res, indent=2))
        else:
            print(f"Audit Target: {res['target_dir']}")
            print(f"Total Files Scanned: {res['total_scanned']}")
            print(f"Violations Detected: {res['violations_count']}")
            if res["violations"]:
                for v in res["violations"][:10]:
                    print(f" - [{v.get('category')}] {v['path']}: {v.get('current_mode')} != {v.get('expected_mode')}")
                if len(res["violations"]) > 10:
                    print(f" ... and {len(res['violations']) - 10} more.")
        sys.exit(0 if res["compliant"] else 1)


if __name__ == "__main__":
    main()
