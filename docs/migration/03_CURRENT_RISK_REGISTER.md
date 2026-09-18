# AcademicSuite Architectural & Operational Risk Register (03_CURRENT_RISK_REGISTER.md)

**Document Version:** 1.0.0  
**Status:** READ-ONLY BASELINE AUDIT COMPLETE  
**Operative Temporal Reality:** 2026 (1405 SH)  

---

## 1. Executive Summary

This Risk Register documents all architectural defects, fail-open paths, silent data fallbacks, security and hook gaps, and factory limitations discovered during the read-only migration baseline audit. 

Each finding is categorized with an **Urgency Tier** (CRITICAL, HIGH, MEDIUM, LOW) and assigned an actionable migration remediation recommendation.

---

## 2. Comprehensive Risk Matrix

| Risk ID | Risk Category | Severity | Description | File(s) Impacted |
| :--- | :--- | :---: | :--- | :--- |
| **RISK-01** | Fail-Open Validation | **CRITICAL** | Master validator returns `PASS` on empty or unpopulated directories | `validators/run_all_validators.py` |
| **RISK-02** | Silent Fallback | **CRITICAL** | Batch orchestrator silently uses sample/fake data if payload path is omitted | `.agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py` |
| **RISK-03** | Fail-Open Validation | **HIGH** | Individual validators issue `PASS` on empty JSON `{}` or missing test metrics | `validators/*/validator.py` |
| **RISK-04** | Validator Omission | **HIGH** | `longitudinal_modmed` validator exists but is omitted from master validator runner | `validators/run_all_validators.py` |
| **RISK-05** | Permissions / Antigravity | **HIGH** | 16 of 22 agents have 0 frontmatter tools declared, causing read-only restriction | `.agents/agents/*/agent.md` |
| **RISK-06** | State Management | **HIGH** | `set_stage` permits arbitrary stage transitions without verifying prerequisites | `scripts/academic_state_manager.py` |
| **RISK-07** | Governance / Ethics | **HIGH** | `record_decision` and `init_state` default `supervisor_approval` to `True` | `scripts/academic_state_manager.py` |
| **RISK-08** | Hook Coverage Gap | **MEDIUM** | Assembly gate only protects Chapter 4 & 5; Proposals, Ch 2, and Scales are ungated | `.agents/verification/transcript_and_rule_guard.py` |
| **RISK-09** | Hook Coverage Gap | **MEDIUM** | PreToolUse raw-data regex can be bypassed by compound bash or python commands | `.agents/verification/transcript_and_rule_guard.py` |
| **RISK-10** | Architecture Leak | **MEDIUM** | Orchestration logic incorrectly placed inside a Skill (`orchestrator_cli.py`) | `.agents/skills/academic-suite-orchestrator/` |
| **RISK-11** | Factory Limitations | **MEDIUM** | Agent factory creates incomplete frontmatter and hardcodes Tier 2 | `factory/agent_factory.py`, `factory/meta_factory.py` |
| **RISK-12** | Environment Disparity | **MEDIUM** | Local `.venv` is missing `jsonschema`, failing 6 unit tests | `.venv` vs host `/usr/bin/python3` |
| **RISK-13** | Redundant Architecture | **LOW** | 3 duplicate agent pairs and 10 orphaned skills without frontmatter bindings | Multiple agent and skill files |

---

## 3. Deep-Dive Risk Analyses

### RISK-01: Master Validator Returns PASS on Empty Directories (CRITICAL)
- **File**: `validators/run_all_validators.py:73-78`
- **Vulnerability**:
  ```python
  if overall_fail:
      report["overall_verdict"] = "FAIL"
  elif overall_review:
      report["overall_verdict"] = "NEEDS_REVIEW"
  else:
      report["overall_verdict"] = "PASS"
  ```
- **Mechanism**: If `stage_dir` contains no `.json` or `.md` files (or is completely empty), zero validator checks are triggered. `overall_fail` remains `False` and `overall_review` remains `False`. The runner emits an overall verdict of **`PASS`** with zero evidence checked.
- **Remediation**: Require that at least one required stage artifact exists and was affirmatively validated. If zero checks execute, the verdict must be `FAIL` or `INCOMPLETE`.

---

### RISK-02: Silent Fallback to Default Sample Data (CRITICAL)
- **File**: `.agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py` (lines 50, 56, 62, 69, 80, 86, 92, 103, 114, 120, 126, 132, 138, 149, 155, 161, 167, 173, 179, 431, 442, 453, 465, 476, etc.)
- **Vulnerability**:
  ```python
  json_payload = step_conf.get("payload_path") or info["default_sample"]
  # In step 'statistics':
  json_payload = info["default_sample"]  # line 465: completely hardcoded!
  ```
- **Mechanism**: When running an automated pipeline preset, if the user or caller fails to supply a valid `payload_path`, the script does not raise an error or halt. Instead, it quietly loads packaged example datasets (`sample_stats_results.json`, `sample_ch5_payload.json`, etc.) and generates deliverables based on synthetic demo data without user awareness.
- **Remediation**: Remove silent fallbacks. Require explicit `payload_path`. If missing, raise `StageDependencyError` immediately.

---

### RISK-03: Sub-Validators Pass on Missing Metrics (HIGH)
- **Files**:
  - `validators/data_integrity/validator.py`: `missing_rate = data.get("missing_rate", 0.0)`. If `{}` is passed, missing rate defaults to 0.0 and MCAR p-value defaults to 1.0, issuing `PASS`.
  - `validators/numerical_consistency/validator.py`: Only checks `sample_size` if `fit_indices` is present. If `{}` is passed, issues `PASS`.
  - `validators/statistical_assumptions/validator.py`: `levene.get("homogeneous", True)` and `slope.get("homogeneous", True)`. Missing assumption tests default to `True`, issuing `PASS`.
  - `validators/result_consistency/validator.py`: Only checks `f_stat` and `r2`. If `{}` is passed, issues `PASS`.
- **Mechanism**: All sub-validators practice optimistic default attribution rather than mandatory schema enforcement.
- **Remediation**: Enforce strict input validation schema. If required metric keys are missing, fail validation immediately.

---

### RISK-04: Omission of `longitudinal_modmed` from Unified Validator Runner (HIGH)
- **File**: `validators/run_all_validators.py`
- **Vulnerability**: Although `validators/longitudinal_modmed/validator.py` was created and certified by `factory/meta_factory.py`, it was never imported or added to `run_all_validators.py`.
- **Impact**: Any longitudinal moderated mediation analysis executed in the workspace bypasses automated validation during master pipeline sweeps.
- **Remediation**: Import and register `validate_longitudinal_modmed` in `run_all_validators.py`.

---

### RISK-05: Frontmatter Tool Disconnection Crippling 16 Specialists (HIGH)
- **Files**: `.agents/agents/<16-specialist-roles>/agent.md`
- **Vulnerability**: 16 out of 22 agents lack a `tools: [...]` YAML list in their frontmatter.
- **Mechanism**: In Google Antigravity, subagents inherit least-privilege defaults (read-only tools) unless specific tools (`run_command`, `write_to_file`, etc.) are declared in YAML frontmatter. Because these 16 agents have no declared tools in their frontmatter, invoking them via `invoke_subagent` will fail when they attempt to write deliverables or execute deterministic CLI scripts.
- **Remediation**: Upgrade all agent frontmatter files to include explicit, least-privilege `tools: [...]` lists matching their contracts.

---

### RISK-06: Arbitrary State Transitions (HIGH)
- **File**: `scripts/academic_state_manager.py:414-434` (`set_stage`)
- **Vulnerability**:
  ```python
  def set_stage(project_path: str, stage: str, status: Optional[str] = None):
      ...
      data["current_stage"] = stage
  ```
- **Mechanism**: Any caller can mutate `current_stage` to any arbitrary string (e.g. `set_stage(path, "10_chapter_assembly")`) without verifying whether prerequisite files exist, whether upstream stages passed validation, or whether the stage name is recognized in the methodology DAG.
- **Remediation**: Implement strict state machine validation in `set_stage` checking prerequisites against `STAGE_DEPENDENCIES` before allowing state transitions.

---

### RISK-07: Implicit Approval Defaults (HIGH)
- **File**: `scripts/academic_state_manager.py:382` & `scripts/academic_state_manager.py:179`
- **Vulnerability**:
  ```python
  def record_decision(..., supervisor_approval: bool = True)
  ```
- **Mechanism**: Methodological choices recorded in `decisions.json` default to `supervisor_approval = True` unless explicitly set to `False`. This violates Directive 7 and Directive 11 (Human-in-the-Loop Gate), creating the false illusion of human clearance in audit logs.
- **Remediation**: Default `supervisor_approval` to `False` or require explicit confirmation payload.

---

### RISK-08: Hook Coverage Gap on Non-Chapter Deliverables (MEDIUM)
- **File**: `.agents/verification/transcript_and_rule_guard.py:129-211`
- **Vulnerability**: The PreToolUse hook intercepts writes targeting `chapter_4_results.docx` and `chapter_5_discussion.docx` to enforce micro-stage prerequisites. However, it does NOT intercept writes targeting:
  - `Research_Proposal.docx` (can be assembled without Stage P.1-P.7 checks)
  - `Chapter_2_Literature_Review.docx` (can be assembled without Stage 2.1-2.7 checks)
  - `Scale_Validation_Report.docx` (can be assembled without Stage V.1-V.8 checks)
  - `Defense_Presentation.pptx` (can be compiled without Stage D.0-D.6 checks)
- **Remediation**: Extend `handle_pre_tool_use` to gate all composite deliverables across proposals, literature reviews, scale validation, and defense presentations.

---

### RISK-09: Bypassable Raw Data Protection Regex (MEDIUM)
- **File**: `.agents/verification/transcript_and_rule_guard.py:71-83`
- **Vulnerability**: The hook regex catches common bash patterns like `rm ... raw_inputs`, `mv ...`, and `> ...`. However, bash constructs like `cat << EOF > projects/study_act_burnout/01_raw_inputs/raw.xlsx` or inline Python scripts (`python3 -c "open('.../raw.xlsx', 'w').write('')"`) can evade regex detection.
- **Remediation**: Complement command-line regex parsing with filesystem permission locks (e.g. `chmod 444` on raw input directories) and comprehensive path matching.

---

### RISK-10: Orchestration Logic Inside Skills (MEDIUM)
- **File**: `.agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py`
- **Vulnerability**: A 49 KB script defining multi-step pipelines resides inside `.agents/skills/`. This breaks the fundamental architectural separation: Skills must be execution instruments ("The Hands"), while orchestration must reside in Agents ("The Brains").
- **Remediation**: Refactor pipeline presets into Antigravity durable agents / workflows, reducing the skill to a simple deterministic runner.

---

### RISK-11: Agent Factory Limitations (MEDIUM)
- **Files**: `factory/agent_factory.py`, `factory/meta_factory.py`
- **Vulnerabilities**:
  1. `agent_factory.py` only emits `name`, `description`, `role`, and `skills`. It omits `model`, `mainAgent`, `subagent`, and `tools`.
  2. Operational tier is hardcoded to `Tier 2 — Domain Specialist` in contract generation.
  3. `meta_factory.py` only has benchmark fixtures for longitudinal moderation-mediation; it cannot scaffold or test qualitative, bibliometric, or SEM agents.
- **Remediation**: Update `agent_factory.py` to support full Antigravity frontmatter generation, multi-tier contracts, and arbitrary specialist scaffolding.

---

### RISK-12: Environment Disparity (Virtualenv missing `jsonschema`) (MEDIUM)
- **Files**: `.venv/`
- **Vulnerability**: Running `run_tests.py` using `.venv/bin/python3` fails 6 tests because `jsonschema` is not installed inside the virtualenv, even though it exists in system python `/usr/bin/python3`.
- **Remediation**: Update virtualenv bootstrap script or install `jsonschema` inside `.venv` during post-migration setup.

---

### RISK-13: Redundant & Orphaned Components (LOW)
- **Findings**:
  - 3 agent pairs are functional duplicates (`writing-agent` / `academic-writer`, `data-agent` / `data-curator`, `statistics-agent` / `statistical-expert`).
  - 10 skills are orphaned (not declared in any agent's frontmatter YAML).
- **Remediation**: Execute planned mergers to eliminate duplication and establish 100% skill binding coverage across active agents.
