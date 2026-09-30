---
trigger: always_on
description: "Universal Git version control and repository standards: Conventional semantic commits, clean working tree, turn completion commit and push."
---

# Git & Workspace Lifecycle Specification (Directive 8)

Universal version control and automation standards across AcademicSuite.

## 1. Directive 8: Mandatory Git Lifecycle
- Every development turn, bug fix, refactor, or deliverable milestone must conclude with clean Git version control operations:
  1. Stage modified and newly created files (`git add <files>`).
  2. Create semantic conventional commit messages (`feat:`, `fix:`, `refactor:`, `docs:`, `test:`).
  3. Push to `origin main` when repository remotes are configured.
- Never conclude an interactive session leaving uncommitted modifications or dangling temporary files.

## 2. Conventional Commit Standards
- `feat:` New agent capabilities, skills, analysis pipelines, or deliverable features.
- `fix:` Bug fixes in scripts, validators, formatting engines, or document generators.
- `refactor:` Code reorganization, modularization, or performance optimization without changing external behavior.
- `docs:` Documentation updates, rule adjustments, manual additions, or architecture notes.
- `test:` Unit tests, regression suites, benchmark definitions, or fixture updates.

## 3. Atomic Working Tree Hygiene
- Keep commits atomic and focused. Do not mix unrelated refactors with deliverable generation.
- Never commit broken test states or malformed syntax.
- Verify that untracked scratch artifacts are either routed to `.gitignore` or properly cataloged.
