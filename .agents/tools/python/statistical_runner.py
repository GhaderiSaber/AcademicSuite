# -*- coding: utf-8 -*-
"""
statistical_runner.py — Centralized Deterministic Runner for Statistical Computations

Acts as a clean, unified CLI dispatcher ("The Hands") for analytical scripts in .agents/skills/.
Strictly deterministic; zero LLM interpretation.
"""

import sys
import os
import argparse
import subprocess
import json

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

SKILL_MAP = {
    "descriptive": os.path.join(REPO_ROOT, ".agents", "skills", "descriptive-statistics", "scripts", "compute_descriptives.py"),
    "reliability": os.path.join(REPO_ROOT, ".agents", "skills", "reliability-analysis", "scripts", "compute_reliability.py"),
    "regression": os.path.join(REPO_ROOT, ".agents", "skills", "regression", "scripts", "run_regression.py"),
    "mediation": os.path.join(REPO_ROOT, ".agents", "skills", "mediation", "scripts", "run_mediation.py"),
    "moderation": os.path.join(REPO_ROOT, ".agents", "skills", "moderation", "scripts", "run_moderation.py"),
    "cfa": os.path.join(REPO_ROOT, ".agents", "skills", "cfa", "scripts", "run_cfa.py"),
    "sem": os.path.join(REPO_ROOT, ".agents", "skills", "sem", "scripts", "run_sem.py"),
    "audit": os.path.join(REPO_ROOT, ".agents", "skills", "data-audit", "scripts", "audit_dataset.py"),
}


def dispatch(skill_name, forwarded_args):
    script_path = SKILL_MAP.get(skill_name)
    if not script_path or not os.path.exists(script_path):
        print(f"[ERROR] Unknown or missing skill script for '{skill_name}': {script_path}", file=sys.stderr)
        sys.exit(1)
    
    cmd = [sys.executable, script_path] + forwarded_args
    print(f"[RUNNER] Executing deterministic tool: {' '.join(cmd)}")
    res = subprocess.run(cmd)
    sys.exit(res.returncode)


def main():
    parser = argparse.ArgumentParser(description="Centralized deterministic statistical tool runner.")
    parser.add_argument("skill", choices=list(SKILL_MAP.keys()), help="Statistical capability to execute")
    args, unknown = parser.parse_known_args()
    dispatch(args.skill, unknown)


if __name__ == "__main__":
    main()
