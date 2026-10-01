#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
contracts/canonical_paths.py — Single Source of Truth for AcademicSuite Canonical Repository & Learning Paths

Ensures all agents and subagents:
1. READ learning/knowledge items from the central AcademicSuite repository, never from individual project workspaces.
2. SAVE newly distilled learning, experiences, and evaluation records directly to the central AcademicSuite repository.
3. Automatically resolves the central AcademicSuite repository root across any environment or client workspace.
"""

import os
import sys
import tempfile
from typing import Optional

KNOWN_LEARNING_SUBDIRS = (
    "knowledge", "experience", "skill-memory", "evaluations",
    "candidates", "promotions", "telemetry", "quarantine",
    "snapshots", "analysis", "versions", "profiles", "reports", "archive"
)


def resolve_canonical_repo_root() -> str:
    """
    Authoritatively resolves the root directory of the AcademicSuite codebase repository.
    Works whether running directly in AcademicSuite, inside a client project workspace,
    or via the globally installed plugin (~/.gemini/config/plugins/academic-suite).
    """
    # 1. Environment variable override (if explicitly set)
    env_dir = os.environ.get("ACADEMIC_SUITE_REPO") or os.environ.get("ACADEMIC_SUITE_BASE_DIR")
    if env_dir and os.path.isdir(os.path.join(env_dir, ".agents", "learning")):
        return os.path.abspath(env_dir)

    # 2. Check if current file's realpath traces back to AcademicSuite
    try:
        real_file = os.path.realpath(__file__)
        cand = os.path.abspath(os.path.join(os.path.dirname(real_file), "..", ".."))
        if os.path.isdir(os.path.join(cand, ".agents", "learning")):
            return cand
    except Exception:
        pass

    # 3. Resolve via global plugin symlink (~/.gemini/config/plugins/academic-suite)
    plugin_path = os.path.expanduser("~/.gemini/config/plugins/academic-suite")
    if os.path.exists(plugin_path):
        try:
            real_plugin = os.path.realpath(plugin_path)
            cand = os.path.abspath(os.path.join(real_plugin, "..", "..", ".."))
            if os.path.isdir(os.path.join(cand, ".agents", "learning")):
                return cand
        except Exception:
            pass

    # 4. Standard Desktop location
    standard_cand = os.path.expanduser("~/Desktop/AcademicSuite")
    if os.path.isdir(os.path.join(standard_cand, ".agents", "learning")):
        return standard_cand

    return os.getcwd()


def get_canonical_learning_dir() -> str:
    """Returns the absolute path to the canonical .agents/learning directory in AcademicSuite."""
    repo_root = resolve_canonical_repo_root()
    return os.path.join(repo_root, ".agents", "learning")


def get_canonical_knowledge_dir() -> str:
    """Returns the absolute path to the canonical .agents/learning/knowledge directory in AcademicSuite."""
    return os.path.join(get_canonical_learning_dir(), "knowledge")


def is_isolated_test_dir(path: Optional[str]) -> bool:
    """
    Checks whether a directory is an isolated temporary test directory
    (e.g., created by tempfile.mkdtemp, pytest tmp_path, or in /tmp).
    """
    if not path or not isinstance(path, str):
        return False
    norm = os.path.abspath(os.path.expanduser(path))
    temp_dir = tempfile.gettempdir()
    if norm.startswith(temp_dir):
        return True
    if "/tmp/" in norm or norm.startswith("/tmp"):
        return True
    base = os.path.basename(norm).lower()
    if any(k in base for k in ("test", "pytest", "fixture", "mock")):
        return True
    return False


def resolve_learning_base_dir(project_root_or_base: Optional[str] = None) -> str:
    """
    Authoritatively returns the base directory for all learning operations.
    If project_root_or_base is a temporary isolated test directory, returns that test dir's learning store.
    Otherwise, returns the canonical AcademicSuite repository learning store (.agents/learning).
    """
    if project_root_or_base and is_isolated_test_dir(project_root_or_base):
        cand = os.path.join(os.path.abspath(project_root_or_base), ".agents", "learning")
        if os.path.isdir(cand):
            return cand
        cand_plain = os.path.join(os.path.abspath(project_root_or_base), "learning")
        if os.path.isdir(cand_plain):
            return cand_plain
        return cand
    return get_canonical_learning_dir()


def is_canonical_learning_path(target_path: str) -> bool:
    """Checks whether a given file path points into the canonical learning or memory store."""
    if not target_path or not isinstance(target_path, str):
        return False
    clean = target_path.strip().replace("\\", "/")
    
    # Exact or relative path targeting .agents/learning or .agents/memory
    if clean in (".agents/learning", ".agents/memory"):
        return True
    if clean.startswith(".agents/learning/") or clean.startswith(".agents/memory/"):
        return True
    if "/.agents/learning/" in clean or "/.agents/memory/" in clean:
        return True

    # Relative path targeting learning/
    if clean == "learning":
        return True
    if clean.startswith("learning/"):
        sub = clean[len("learning/"):].split("/")[0]
        if sub in KNOWN_LEARNING_SUBDIRS or not sub:
            return True
    if "/learning/" in clean:
        for sd in KNOWN_LEARNING_SUBDIRS:
            if f"/learning/{sd}/" in clean or clean.endswith(f"/learning/{sd}"):
                return True
        
    norm = os.path.abspath(os.path.expanduser(target_path))
    learning_dir = os.path.abspath(get_canonical_learning_dir())
    repo_root = os.path.abspath(resolve_canonical_repo_root())
    
    if norm.startswith(learning_dir):
        return True
    if norm.startswith(os.path.join(repo_root, ".agents", "memory")):
        return True

    return False


def redirect_learning_target_to_canonical(target_path: str) -> str:
    """
    If a target path targets .agents/learning, learning/, or .agents/memory,
    redirects it authoritatively to the canonical AcademicSuite repository learning store.
    """
    if not target_path or not isinstance(target_path, str):
        return target_path
    
    clean_target = os.path.expanduser(target_path.strip()).replace("\\", "/")
    canonical_learning = get_canonical_learning_dir()
    canonical_repo = resolve_canonical_repo_root()
    
    # Already targeting canonical repo directly
    if os.path.isabs(clean_target) and clean_target.startswith(canonical_learning):
        return clean_target
        
    # Redirect .agents/learning/...
    if clean_target == ".agents/learning":
        return canonical_learning
    if ".agents/learning/" in clean_target:
        idx = clean_target.find(".agents/learning/")
        subpath = clean_target[idx + len(".agents/learning/"):]
        return os.path.join(canonical_learning, subpath)

    # Redirect learning/...
    if clean_target == "learning":
        return canonical_learning
    if clean_target.startswith("learning/"):
        subpath = clean_target[len("learning/"):]
        return os.path.join(canonical_learning, subpath)
    if "/learning/" in clean_target:
        for sd in KNOWN_LEARNING_SUBDIRS:
            token = f"/learning/{sd}/"
            if token in clean_target:
                idx = clean_target.find(token)
                subpath = clean_target[idx + len("/learning/"):]
                return os.path.join(canonical_learning, subpath)

    # Redirect .agents/memory/...
    if clean_target == ".agents/memory":
        return os.path.join(canonical_repo, ".agents", "memory")
    if ".agents/memory/" in clean_target:
        idx = clean_target.find(".agents/memory/")
        subpath = clean_target[idx + len(".agents/memory/"):]
        return os.path.join(canonical_repo, ".agents", "memory", subpath)
        
    return clean_target
