---
name: academic-suite-orchestrator
description: >-
  Master research lifecycle CLI pipeline and orchestration engine for AcademicSuite. Coordinates and chains all 18 specialized
  skills into automated, resilient, and reproducible end-to-end research pipelines. Supports standard presets: empirical thesis
  (thesis_empirical: Proposal -> Simulation -> Stats Ch4 -> Discussion Ch5 -> Full Thesis -> Defense Slides), scale standardization
  (scale_validation: CTT/IRT validation -> Article -> Submission), qualitative research (qualitative_study), systematic reviews
  (meta_analysis), and publishing (thesis_to_publication). Manages intermediate data routing, checkpointing (--resume-from),
  dry-run DAG validation (--dry-run), audit logging (orchestrator_manifest.json), and executive dashboards (PROJECT_DASHBOARD.md).
---

# AcademicSuite Master Orchestrator Skill (موتور جامع فرماندهی و اجرای خودکار پایپ‌لاین‌های پژوهشی)

The **AcademicSuite Orchestrator** is the **Master Automation and Execution Engine** for AcademicSuite. It unifies, coordinates, and executes multi-stage academic research workflows by orchestrating the 18 specialized skills into automated, reproducible, and resilient pipelines.

---

## 1. When to Activate This Skill

Activate this skill when:
1. The user requests an **End-to-End Thesis or Dissertation Workflow**:
   - «می‌خواهم پایان‌نامه یا رساله‌ام را به طور کامل از پروپوزال، شبیه‌سازی داده، تحلیل آماری فصل ۴، بحث فصل ۵ تا ادغام کامل رساله و اسلایدهای دفاع بسازی.»
2. The user requests an **End-to-End Scale Standardization Pipeline**:
   - «فرایند اعتباریابی و روان‌سنجی مقیاس را از ارزیابی CTT و IRT تا استخراج مقاله و تدوین کاورلتر سابمیت اجرا کن.»
3. The user requests a **Qualitative Dissertation Workflow**:
   - «اجرای گام‌به‌گام تحلیل کیفی مصاحبه‌ها، تدوین فصل ۴ و ۵، تجمیع رساله و اسلاید دفاع.»
4. The user requests an **Automated Systematic Review & Meta-Analysis Pipeline**:
   - «اجرای فراتحلیل، نمودارهای فارست/فانل، نگارش مقاله و آماده‌سازی پکیج سابمیت به ژورنال.»
5. The user requests **Extracting and Packaging an Academic Publication from a Thesis**:
   - «کاهش همانندجویی ایرانداک، استخراج مقاله علمی-پژوهشی و آماده‌سازی فایل‌های ارسال به ژورنال.»
6. The user needs **Dry-Run Validation, Pipeline Inspection, or Resuming from a Specific Stage**:
   - Inspecting execution plans with `--dry-run`, resuming interrupted pipelines with `--resume-from <step>`, or running a single isolated stage with `--step <step>`.

---

## 2. Built-In Standard Pipelines

| Pipeline Preset | Chained Skills & Sequence | Primary Output Deliverables |
| :--- | :--- | :--- |
| **`thesis_empirical`** | `proposal` $\to$ `simulation` $\to$ `statistics` $\to$ `discussion` $\to$ `thesis` $\to$ `defense` | Proposal (`.docx`), Dataset (`.xlsx`), Ch 4 (`.docx`), Ch 5 (`.docx`), Full Thesis (`.docx`), Defense Slides (`.pptx`). |
| **`scale_validation`** | `scale_validator` $\to$ `article` $\to$ `submission` | Validation Ch 4 (`.docx`), 6-Sheet Matrix (`.xlsx`), Scree/ROC & IRT Plots (`.png`), Article (`.docx`), Submission Package (`.docx`). |
| **`qualitative_study`** | `proposal` $\to$ `qualitative` $\to$ `discussion` $\to$ `thesis` $\to$ `defense` | Proposal (`.docx`), Coding Matrix (`.xlsx`), Thematic Network (`.png`), Ch 4 (`.docx`), Ch 5 (`.docx`), Full Thesis (`.docx`), Slides (`.pptx`). |
| **`meta_analysis`** | `meta_analysis` $\to$ `article` $\to$ `submission` | PRISMA Report (`.docx`), Forest & Funnel Plots (`.png`), Manuscript (`.docx`), Cover Letter & Highlights (`.docx`). |
| **`thesis_to_publication`** | `plagiarism` $\to$ `article` $\to$ `submission` | Rewritten Thesis ($< 20\%$ Irandoc), Journal Manuscript (`.docx`), Cover Letter, Title Page (CRediT), and Highlights (`.docx`). |

---

## 3. CLI Usage & Execution Syntax

### Standard Execution:
```bash
python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --pipeline thesis_empirical \
  --config path/to/project_config.json \
  --out-dir path/to/output_directory \
  --lang fa
```

### Dry-Run DAG Validation:
```bash
python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --pipeline thesis_empirical \
  --config path/to/project_config.json \
  --out-dir path/to/output_directory \
  --dry-run
```

### Checkpointing & Resuming:
```bash
python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --pipeline thesis_empirical \
  --config path/to/project_config.json \
  --out-dir path/to/output_directory \
  --resume-from discussion
```

### Single Step Execution:
```bash
python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --pipeline thesis_empirical \
  --config path/to/project_config.json \
  --out-dir path/to/output_directory \
  --step thesis
```

### Custom Pipeline Sequence:
```bash
python3 .agents/skills/academic-suite-orchestrator/scripts/orchestrator_cli.py \
  --steps proposal,simulation,statistics,article,submission \
  --config path/to/project_config.json \
  --out-dir path/to/output_directory
```

---

## 4. Centralized Tracking & Dashboard

Every orchestrator run generates two executive tracking artifacts in the output directory:
1. **`orchestrator_manifest.json`**:
   - Machine-readable audit trail logging total duration, execution status, step timestamps, exit codes, and resolved artifact file paths.
2. **`PROJECT_DASHBOARD.md`**:
   - Executive markdown report presenting project metadata, tabular stage progress, duration benchmarks, and clickable file links to every produced Word document, Excel matrix, PowerPoint presentation, and visual graphic.
