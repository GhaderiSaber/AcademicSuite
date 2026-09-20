# AcademicSuite — Codebase Inventory Audit & Status Registry (Phase 35)

**Document Version:** 1.0.0 (Phase 35 Codebase Clean-Up)  
**Operative Date:** September 2026 (1405 SH)  
**Status:** Approved & Implemented  

---

## 1. Executive Summary & Governance Standard

Following the successful establishment, stabilization, and formal verification of the new multi-agent cognitive architecture and continuous self-improvement engine (Phases 1 through 34), Phase 35 executes a repository-wide legacy code cleanup.

Every audited file across `scripts/`, `tools/`, `factory/`, `recovery/`, `legacy/`, `.agents/agents/`, and top-level entrypoints is assigned **exactly one mutually exclusive status**:

```text
+----------------+--------------------------------------+------------------------------------------+
| Status         | Architectural Definition             | Mandatory Phase 35 Action                |
+----------------+--------------------------------------+------------------------------------------+
| 1. LEGACY      | Historical component from earlier    | ISOLATED: Archived in legacy/ or bounded |
|                | architecture superseded by new engine| with explicit historical markers.        |
+----------------+--------------------------------------+------------------------------------------+
| 2. DUPLICATE   | Redundant script or entrypoint       | CONSOLIDATED: Unified into canonical     |
|                | performing overlapping functions     | implementation with compat wrapper.      |
+----------------+--------------------------------------+------------------------------------------+
| 3. DEPRECATED  | Operational component scheduled for  | DOCUMENTED: Formal deprecation notice,   |
|                | sunset with modern replacement       | migration path, and sunset timeline.     |
+----------------+--------------------------------------+------------------------------------------+
| 4. UNUSED      | Dead code with proven zero external  | REMOVED: Deleted from disk ONLY after    |
|                | callers, imports, or test usage      | proving zero dependencies.               |
+----------------+--------------------------------------+------------------------------------------+
| 5. COMPATIBILITY| Shim, wrapper, or discovery mirror  | PRESERVED & ANNOTATED: Maintained for    |
|                | bridging platforms or legacy callers | backward compatibility.                  |
+----------------+--------------------------------------+------------------------------------------+
| 6. EXPERIMENTAL| Sandbox prototype, benchmark tool,   | TAGGED & ISOLATED: Marked with           |
|                | or non-production demonstration CLI  | [EXPERIMENTAL] header and bounded scope. |
+----------------+--------------------------------------+------------------------------------------+
```

---

## 2. Zero-Dependency Proof for Removed Files (`UNUSED` → Removed)

In accordance with the constitutional mandate (*"Do not delete first. First prove that nothing depends on it"*), all 7,102 text files across the repository were exhaustively scanned for imports, subprocess calls, CLI invocations, and test references. The following 5 files were proven to have **exactly zero dependencies** and were safely removed:

| # | Removed File Path | Lines | Proof of Zero Dependency | Replacement / Rationale |
|---|---|---|---|---|---|
| 1 | `tools/python/openxml_helpers.py` | 61 | 0 imports, 0 test references, 0 CLI references across 7,102 files | Superseded by `scripts/structured_docx_generator.py` and skills OpenXML engines. |
| 2 | `scripts/generate_scale_validation_package.py` | 353 | 0 imports, 0 test references across 7,102 files | One-off mock package generator for vertical slice fixture directory. |
| 3 | `scripts/assemble_master_scale_validation_docx.py` | 239 | 0 imports, 0 test references across 7,102 files | Hardcoded CAV-S scale compiler superseded by `scripts/build_scale_validation_triad_docx.py`. |
| 4 | `scripts/generate_experimental_master_package.py` | 424 | 0 imports, 0 test references across 7,102 files | One-off mock package generator for experimental vertical slice fixture directory. |
| 5 | `scripts/multi_account_scanner.py` | 407 | 0 imports, 0 test references, 0 skill references across 7,102 files | Unreferenced standalone Telegram utility not part of core suite. |

---

## 3. Comprehensive Master File Status Inventory

| Target File / Path | Status | Action Taken | Architectural Rationale & Dependency Proof |
|---|---|---|---|
| `digital_saber.py` | `DEPRECATED` | Documented | Monolithic CLI entrypoint. Documented deprecation in favor of `scripts/suite_cli.py` and Antigravity subagents. |
| `scripts/orchestrator_dependency_resolver.py` | `DEPRECATED` | Documented | Superseded by `scripts/academic_task_router.py` and `scripts/capability_resolver.py`. |
| `scripts/triage_projects.py` | `DEPRECATED` | Documented | Standalone Drive maintenance script superseded by `academic-drive-project-organizer` skill. |
| `scripts/build_hypothesis_1_triad_docx.py` | `DUPLICATE` | Consolidated | Consolidated with `scripts/generate_hypothesis_triad_docx.py` via thin compatibility wrapper. |
| `scripts/attach-suite` | `COMPATIBILITY` | Preserved | Bash launcher wrapper delegating to `scripts/attach-suite.py`. |
| `scripts/attach-suite.bat` | `COMPATIBILITY` | Preserved | Windows cmd launcher wrapper delegating to `scripts/attach-suite.py`. |
| `scripts/attach-suite.py` | `COMPATIBILITY` | Preserved | Core client attachment engine for Telegram consultant twin. |
| `scripts/attach_telegram_client.py` | `COMPATIBILITY` | Preserved | Telegram client attachment session runner. |
| `scripts/login_second_account.py` | `COMPATIBILITY` | Preserved | Telethon authentication session runner for Saber Admin Desk. |
| `scripts/login_second_account.sh` | `COMPATIBILITY` | Preserved | Shell launcher for dual-account Telegram session. |
| `scripts/telethon_service.sh` | `COMPATIBILITY` | Preserved | System service wrapper for persistent Telegram listener. |
| `scripts/bootstrap_env.sh` | `COMPATIBILITY` | Preserved | Virtual environment setup and dependency installer. |
| `scripts/permission_manager.py` | `COMPATIBILITY` | Preserved | PreToolUse security boundary and mode-bit manager. |
| `scripts/script_execution_guard.py` | `COMPATIBILITY` | Preserved | PreToolUse execution guard blocking unsafe shell commands. |
| `scripts/capability_resolver.py` | `COMPATIBILITY` | Preserved | Capability resolution bridge for `scripts/academic_task_router.py`. |
| `tools/r/sem_lavaan_runner.R` | `COMPATIBILITY` | Preserved | R Lavaan runner for SEM micro-stages (`MICRO_STAGE_SEQUENCES.md`). |
| `tools/python/statistical_runner.py` | `COMPATIBILITY` | Preserved | Python runner for parametric models (`test_project_structure.py`). |
| `tools/README.md` | `COMPATIBILITY` | Documented | Documented structure of tools layer. |
| `.agents/agents/*.md` (28 symlinks) | `COMPATIBILITY` | Preserved | Maintained for flat-file discovery compatibility with legacy Antigravity loaders. |
| `legacy/skills/*` (10 directories) | `LEGACY` | Isolated | Historical workflow-converted shells archived under `legacy/skills/`. |
| `legacy/workflows/*.md.bak` (10 files) | `LEGACY` | Isolated | Archived legacy workflow definitions superseded by modern Skills. |
| `scripts/migrate_durable_agents.py` | `LEGACY` | Isolated | Historical migration utility tested by `test_durable_agents_migration.py`. |
| `scripts/migrate_specialist_workers.py` | `LEGACY` | Isolated | Historical migration utility tested by `test_specialist_workers_migration.py`. |
| `scripts/academic_self_improvement_demo.py` | `EXPERIMENTAL` | Tagged | Phase 18 interactive self-improvement demonstration CLI. |
| `scripts/academic_isolated_agent_sandbox.py` | `EXPERIMENTAL` | Tagged | Sandbox utility for candidate mutation testing in isolated workspaces. |
| `scripts/candidate_falsifier_engine.py` | `EXPERIMENTAL` | Tagged | Deliberation engine for adversarial candidate falsification. |
| `tools/python/openxml_helpers.py` | `UNUSED` | Removed | Proven zero references; deleted in Phase 35. |
| `scripts/generate_scale_validation_package.py` | `UNUSED` | Removed | Proven zero references; deleted in Phase 35. |
| `scripts/assemble_master_scale_validation_docx.py` | `UNUSED` | Removed | Proven zero references; deleted in Phase 35. |
| `scripts/generate_experimental_master_package.py` | `UNUSED` | Removed | Proven zero references; deleted in Phase 35. |
| `scripts/multi_account_scanner.py` | `UNUSED` | Removed | Proven zero references; deleted in Phase 35. |

---

## 4. Verification & Non-Regression Invariant

All automated test suites, validators, and guards pass 100% following the removal and consolidation of these files:
- Zero active production scripts or skills import or depend on removed files.
- Consolidated wrappers provide 100% backward-compatible interfaces.
- Agent integrity validator confirms 28/28 discoverable agents.
- Skill size guard confirms 73/73 items within single-view limits.
