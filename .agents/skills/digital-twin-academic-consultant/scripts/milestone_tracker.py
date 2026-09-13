"""
milestone_tracker.py — Scope-Adaptive Dynamic Milestone Checklists Engine

Manages live academic research milestones for graduate theses and statistical consulting:
1. Scope-Adaptive Taxonomies:
   - 'chapter4_only': Empirical Statistical Analysis (Data Screening -> Assumptions -> Descriptives -> Inferential -> APA 7 Narrative)
   - 'proposal_only': Institutional Proposal (Title/Problem -> Objectives/Hypotheses -> Lit Review -> Methodology/G*Power -> Definitions)
   - 'full_thesis': Complete 5-Chapter Thesis (Proposal -> Ch2 Lit -> Ch3 Method -> Ch4 Stats -> Ch5 Defense)
   - 'supervisor_revisions': Revision & Defense Rebuttal (Feedback Triage -> Recalculations -> Narrative -> Rebuttal Table -> Submissions)
2. Automated Google Drive Deliverable Scanner:
   - Discovers matching deliverables in 03_deliverables/, 01_raw_inputs/, 02_analysis_code/
3. Visual Progress Bar & Telegram Box-Drawing Card Formatter:
   - Modern 2026 box-drawing container with expandable checklist blockquote and 2-row action buttons.
4. Interactive State Management:
   - Advance milestone stage, refresh from Drive, and cycle project scope dynamically.
"""

import os
import re
import json
import html
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Standard Subfolder Definitions matching project_drive_manager
SUBFOLDERS = {
    "deliverables": "03_deliverables",
    "raw": "01_raw_inputs",
    "code": "02_analysis_code",
    "references": "04_references_and_lit"
}

# Scope Taxonomies with Granular Milestones
SCOPE_TAXONOMIES: Dict[str, Dict[str, Any]] = {
    "chapter4_only": {
        "title_en": "EMPIRICAL STATISTICAL ANALYSIS (Chapter 4)",
        "title_fa": "مراحل تحلیل آماری و تدوین فصل چهارم",
        "badge": "📊 Chapter 4 Only",
        "short_name": "Ch 4 Only",
        "milestones": [
            {
                "code": "S1",
                "title_en": "Data Screening & Cleaning",
                "title_fa": "غربالگری داده‌ها، کدهای معکوس و داده‌های پرت",
                "patterns": [r"data", r"frequency", r"clean", r"codebook", r"خام", r"غربالگری", r"کدگذاری", r"\.sav$", r"\.xlsx$"],
                "default_note": "Variable coding & survey data verification"
            },
            {
                "code": "S2",
                "title_en": "Statistical Assumption Testing",
                "title_fa": "آزمون مفروضه‌های آماری (نرمال، لون، باکس)",
                "patterns": [r"normality", r"levene", r"boxm", r"assumptions", r"مفروض", r"نرمال", r"لون", r"باکس", r"\.spv$"],
                "default_note": "Univariate & multivariate assumption verification"
            },
            {
                "code": "S3",
                "title_en": "Descriptive Statistics & Demographics",
                "title_fa": "آمار توصیفی، میانگین و ماتریس همبستگی APA 7",
                "patterns": [r"descriptive", r"correlation", r"demographic", r"توصیفی", r"همبستگی", r"جمعیت", r"matrix"],
                "default_note": "Mean, SD, and APA 7 correlation matrix"
            },
            {
                "code": "S4",
                "title_en": "Inferential Hypothesis Testing",
                "title_fa": "آزمون استنباطی فرضیات (کوواریانس، رگرسیون، SEM)",
                "patterns": [r"ancova", r"regression", r"sem", r"model", r"results", r"کوواریانس", r"رگرسیون", r"معادلات", r"آزمون"],
                "default_note": "Primary hypothesis evaluation & effect sizes"
            },
            {
                "code": "S5",
                "title_en": "APA 7 Table Compilation & Chapter 4 Narrative",
                "title_fa": "تدوین جداول سه خطی استاندارد و گزارش دفاعی فصل ۴",
                "patterns": [r"chapter 4", r"chapter_4", r"chapter4", r"فصل 4", r"فصل چهار", r"گزارش نهایی", r"نتایج نهایی"],
                "default_note": "Three-line APA 7 tables & defense narrative"
            }
        ]
    },
    "proposal_only": {
        "title_en": "RESEARCH PROPOSAL DEVELOPMENT",
        "title_fa": "مراحل تدوین و تصویب طرح پژوهش (پروپوزال)",
        "badge": "📑 Proposal Only",
        "short_name": "Proposal",
        "milestones": [
            {
                "code": "P1",
                "title_en": "Title Scoping & Problem Statement",
                "title_fa": "تحدید عنوان و تدوین بیان مسئله (مدل قیف وارونه)",
                "patterns": [r"problem", r"statement", r"title", r"بیان مسئله", r"عنوان", r"مقدمه"],
                "default_note": "Inverted-triangle problem formulation"
            },
            {
                "code": "P2",
                "title_en": "Objectives, Questions & Hypotheses",
                "title_fa": "اهداف، سوالات و فرمول‌بندی فرضیات جهت‌دار",
                "patterns": [r"objective", r"hypothesis", r"question", r"اهداف", r"فرضیه", r"سوالات"],
                "default_note": "Directional hypotheses & research questions"
            },
            {
                "code": "P3",
                "title_en": "Empirical Literature Background",
                "title_fa": "پیشینه پژوهشی داخلی و خارجی ۲۰۲۰-۲۰۲۶",
                "patterns": [r"literature", r"background", r"review", r"پیشینه", r"ادبیات", r"سوابق"],
                "default_note": "5-part narrative empirical synthesis"
            },
            {
                "code": "P4",
                "title_en": "Methodology, G*Power & Instruments",
                "title_fa": "روش پژوهش، توان‌آزمایی G*Power و مقیاس‌های روا",
                "patterns": [r"methodology", r"gpower", r"scale", r"sample", r"روش", r"جی پاور", r"ابزار", r"نمونه"],
                "default_note": "Sample size justification (80% power) & psychometrics"
            },
            {
                "code": "P5",
                "title_en": "Definitions & Institutional Synthesis",
                "title_fa": "تعاریف مفهومی/عملیاتی و آماده‌سازی نهایی تصویب",
                "patterns": [r"proposal", r"طرح", r"پروپوزال", r"نهایی", r"approval", r"approved"],
                "default_note": "Approved institutional Word proposal format"
            }
        ]
    },
    "full_thesis": {
        "title_en": "MASTER / DOCTORAL DISSERTATION (Full Thesis)",
        "title_fa": "مراحل کامل پایان‌نامه / رساله ۵ فصلی",
        "badge": "🎓 Full Thesis",
        "short_name": "Full Thesis",
        "milestones": [
            {
                "code": "M1",
                "title_en": "Research Proposal & Institutional Approval",
                "title_fa": "پروپوزال، بیان مسئله و تصویب طرح تحقیق",
                "patterns": [r"proposal", r"پروپوزال", r"طرح پژوهش", r"فصل 1", r"chapter 1"],
                "default_note": "Proposal defense & institutional approval"
            },
            {
                "code": "M2",
                "title_en": "Theoretical Foundations & Literature Review",
                "title_fa": "فصل دوم: مبانی نظری و پیشینه تجربی داخلی/خارجی",
                "patterns": [r"chapter 2", r"chapter_2", r"chapter2", r"فصل 2", r"فصل دو", r"مبانی نظری", r"پیشینه"],
                "default_note": "Thematic synthesis & theoretical framework"
            },
            {
                "code": "M3",
                "title_en": "Methodology & Statistical Power Protocol",
                "title_fa": "فصل سوم: روش‌شناسی، ابزارهای روا و G*Power",
                "patterns": [r"chapter 3", r"chapter_3", r"chapter3", r"فصل 3", r"فصل سه", r"روش تحقیق", r"gpower"],
                "default_note": "G*Power 3.1 protocol, sampling, & instrumentation"
            },
            {
                "code": "M4",
                "title_en": "Statistical Data Analysis & APA 7 Tables",
                "title_fa": "فصل چهارم: تحلیل آماری، آزمون فرضیات و جداول",
                "patterns": [r"chapter 4", r"chapter_4", r"chapter4", r"فصل 4", r"فصل چهار", r"یافته", r"results"],
                "default_note": "Hypothesis testing & APA 7th empirical tables"
            },
            {
                "code": "M5",
                "title_en": "Discussion, Synthesis & Viva Voce Defense Deck",
                "title_fa": "فصل پنجم: تبیین روان‌شناختی، محدودیت‌ها و اسلاید دفاع",
                "patterns": [r"chapter 5", r"chapter_5", r"chapter5", r"فصل 5", r"فصل پنج", r"بحث", r"defense", r"dissertation", r"پایان نامه"],
                "default_note": "Mechanisms, clinical implications & defense deck"
            }
        ]
    },
    "supervisor_revisions": {
        "title_en": "SUPERVISOR & EXAMINER REVISIONS",
        "title_fa": "مراحل اعمال اصلاحات اساتید راهنما و داوران",
        "badge": "📝 Supervisor Revisions",
        "short_name": "Revisions",
        "milestones": [
            {
                "code": "R1",
                "title_en": "Feedback Extraction & Triaged Audit",
                "title_fa": "استخراج کامنت‌های Word و تریاژ اصلاحات داوری",
                "patterns": [r"feedback", r"comments", r"اصلاح", r"کامنت", r"نظرات", r"داور", r"راهنما"],
                "default_note": "Structural, statistical, & formatting categorization"
            },
            {
                "code": "R2",
                "title_en": "Methodological & Statistical Recalculations",
                "title_fa": "اعمال اصلاحات آماری و اجرای آزمون‌های تکمیلی",
                "patterns": [r"recalc", r"additional", r"آمار اصلاح", r"تحلیل مجدد", r"مدل جدید"],
                "default_note": "Additional statistical models requested by committee"
            },
            {
                "code": "R3",
                "title_en": "Literature & Textual Enhancements",
                "title_fa": "اصلاح مبانی نظری، منابع APA 7 و متن فصول",
                "patterns": [r"text_rev", r"revised", r"اصلاح متن", r"منابع جدید"],
                "default_note": "Theoretical gaps closed & citations updated"
            },
            {
                "code": "R4",
                "title_en": "Point-by-Point Rebuttal Table",
                "title_fa": "تدوین جدول رسمی پاسخ به نظرات استاد راهنما و داوران",
                "patterns": [r"rebuttal", r"response_table", r"جدول پاسخ", r"پاسخ به داوران"],
                "default_note": "Formal academic compliance table with line references"
            },
            {
                "code": "R5",
                "title_en": "Final Marked & Clean Deliverables",
                "title_fa": "آماده‌سازی نسخه با Track Changes و نسخه نهایی پاکیزه",
                "patterns": [r"final", r"clean", r"tracked", r"نهایی", r"تایید", r"آماده تحویل"],
                "default_note": "Final approved package ready for institutional signoff"
            }
        ]
    }
}

ORDERED_SCOPES = ["chapter4_only", "proposal_only", "full_thesis", "supervisor_revisions"]


class AcademicMilestoneTracker:
    """Manages scope-adaptive academic research milestones and deliverable tracking."""

    def __init__(self, drive_root: Optional[str] = None):
        self.drive_root = drive_root or "/Users/saber/Library/CloudStorage/GoogleDrive-ghaderi.sabir@gmail.com/My Drive/My Work"

    def scan_project_deliverables(self, project_dir: str) -> List[Dict[str, Any]]:
        """
        Scan project directory (prioritizing 03_deliverables/) and return list of file dicts.
        """
        found_files = []
        if not os.path.exists(project_dir):
            return found_files

        search_dirs = [
            os.path.join(project_dir, SUBFOLDERS["deliverables"]),
            os.path.join(project_dir, SUBFOLDERS["raw"]),
            os.path.join(project_dir, SUBFOLDERS["code"]),
            project_dir
        ]

        seen_names = set()
        for d in search_dirs:
            if not os.path.exists(d):
                continue
            for fname in os.listdir(d):
                if fname.startswith(".") or fname == "project_meta.json":
                    continue
                fpath = os.path.join(d, fname)
                if os.path.isfile(fpath):
                    f_clean = fname.strip()
                    if f_clean.lower() not in seen_names:
                        seen_names.add(f_clean.lower())
                        sz = os.path.getsize(fpath)
                        found_files.append({
                            "name": fname,
                            "path": fpath,
                            "size": sz,
                            "size_str": self._format_size(sz),
                            "subfolder": os.path.basename(d)
                        })
        return found_files

    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable KB or MB."""
        if size_bytes < 1024:
            return f"{size_bytes} B"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.0f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.1f} MB"

    def infer_scope(self, meta: Dict[str, Any], files: List[Dict[str, Any]]) -> str:
        """Infer or retrieve the appropriate scope for a project."""
        explicit_scope = meta.get("scope")
        if explicit_scope in SCOPE_TAXONOMIES:
            return explicit_scope

        # Check files
        all_names = " ".join([f["name"].lower() for f in files])
        if any(w in all_names for w in ["rebuttal", "اصلاحات", "پاسخ به داوران", "کامنت"]):
            return "supervisor_revisions"
        if any(w in all_names for w in ["proposal", "پروپوزال", "طرح تحقیق"]):
            # If chapter 4 also exists, it might be full thesis
            if any(w in all_names for w in ["chapter 4", "chapter 5", "dissertation", "پایان نامه"]):
                return "full_thesis"
            return "proposal_only"
        if any(w in all_names for w in [".sav", "frequency", "levene", "ancova", "regression", "chapter 4", "همبستگی"]):
            return "chapter4_only"

        # Default to chapter 4 only (most common in Saber's consulting)
        return "chapter4_only"

    def evaluate_milestones(
        self,
        project_dir: str,
        explicit_scope: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Evaluate project milestones against Google Drive deliverables and project_meta.json.
        Returns complete milestone state dictionary.
        """
        meta_file = os.path.join(project_dir, "project_meta.json")
        meta = {}
        if os.path.exists(meta_file):
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
            except Exception:
                meta = {}

        files = self.scan_project_deliverables(project_dir)
        scope = explicit_scope or meta.get("scope") or self.infer_scope(meta, files)
        if scope not in SCOPE_TAXONOMIES:
            scope = "chapter4_only"

        taxonomy = SCOPE_TAXONOMIES[scope]
        milestone_defs = taxonomy["milestones"]
        active_idx = int(meta.get("active_stage_idx", 0))
        if active_idx < 0:
            active_idx = 0
        if active_idx >= len(milestone_defs):
            active_idx = len(milestone_defs) - 1

        evaluated_milestones = []
        completed_count = 0

        for idx, m_def in enumerate(milestone_defs):
            m_code = m_def["code"]
            # Check if matching files exist
            matched_file = None
            for f in files:
                fname_lower = f["name"].lower()
                for pat in m_def["patterns"]:
                    if re.search(pat, fname_lower, re.IGNORECASE):
                        matched_file = f
                        break
                if matched_file:
                    break

            # Determine status
            if matched_file or idx < active_idx:
                status = "completed"
                completed_count += 1
            elif idx == active_idx:
                status = "in_progress"
            else:
                status = "pending"

            evaluated_milestones.append({
                "code": m_code,
                "title_en": m_def["title_en"],
                "title_fa": m_def["title_fa"],
                "status": status,
                "matched_file": matched_file["name"] if matched_file else None,
                "file_size": matched_file["size_str"] if matched_file else None,
                "default_note": m_def["default_note"]
            })

        total_m = len(milestone_defs)
        progress_pct = int((completed_count / total_m) * 100) if total_m > 0 else 0

        # Build progress bar (10 blocks)
        filled_blocks = int(progress_pct / 10)
        empty_blocks = 10 - filled_blocks
        progress_bar = "█" * filled_blocks + "░" * empty_blocks

        # Find current in-progress milestone code
        curr_code = milestone_defs[active_idx]["code"]

        return {
            "scope": scope,
            "scope_badge": taxonomy["badge"],
            "scope_short": taxonomy["short_name"],
            "scope_title_en": taxonomy["title_en"],
            "active_stage_idx": active_idx,
            "current_stage_code": curr_code,
            "completed_count": completed_count,
            "total_count": total_m,
            "progress_pct": progress_pct,
            "progress_bar": progress_bar,
            "milestones": evaluated_milestones,
            "client_name": meta.get("client_name", os.path.basename(project_dir)),
            "client_id": meta.get("telegram_id"),
            "project_name": meta.get("project_name", os.path.basename(project_dir)),
            "project_dir": project_dir,
            "files_found_count": len(files)
        }

    def advance_stage(self, project_dir: str) -> Dict[str, Any]:
        """
        Advance active stage index to the next milestone in project_meta.json.
        """
        meta_file = os.path.join(project_dir, "project_meta.json")
        meta = {}
        if os.path.exists(meta_file):
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
            except Exception:
                meta = {}

        curr_idx = int(meta.get("active_stage_idx", 0))
        scope = meta.get("scope", "chapter4_only")
        total = len(SCOPE_TAXONOMIES.get(scope, SCOPE_TAXONOMIES["chapter4_only"])["milestones"])

        new_idx = min(curr_idx + 1, total - 1)
        meta["active_stage_idx"] = new_idx
        meta["updated_at"] = datetime.now().isoformat()

        # Update history
        history = meta.setdefault("milestone_history", [])
        history.append({
            "advanced_at": datetime.now().isoformat(),
            "from_idx": curr_idx,
            "to_idx": new_idx,
            "scope": scope
        })

        try:
            with open(meta_file, "w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[-] Error updating project_meta.json: {e}")

        return self.evaluate_milestones(project_dir)

    def cycle_scope(self, project_dir: str) -> Dict[str, Any]:
        """
        Cycle project scope: chapter4_only -> proposal_only -> full_thesis -> supervisor_revisions -> chapter4_only.
        """
        meta_file = os.path.join(project_dir, "project_meta.json")
        meta = {}
        if os.path.exists(meta_file):
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
            except Exception:
                meta = {}

        curr_scope = meta.get("scope") or self.infer_scope(meta, self.scan_project_deliverables(project_dir))
        try:
            curr_idx = ORDERED_SCOPES.index(curr_scope)
            next_scope = ORDERED_SCOPES[(curr_idx + 1) % len(ORDERED_SCOPES)]
        except ValueError:
            next_scope = "chapter4_only"

        meta["scope"] = next_scope
        meta["active_stage_idx"] = 0  # reset stage index on scope change
        meta["updated_at"] = datetime.now().isoformat()

        try:
            with open(meta_file, "w", encoding="utf-8") as f:
                json.dump(meta, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[-] Error writing scope to project_meta.json: {e}")

        return self.evaluate_milestones(project_dir)

    def format_milestone_card(self, state: Dict[str, Any]) -> str:
        """
        Format milestone state as an executive 2026 Telegram box-drawing card with expandable checklist.
        """
        c_name = html.escape(state.get("client_name", "Client"))
        c_id = state.get("client_id")
        id_str = f" • <code>#{c_id}</code>" if c_id else ""
        p_dir = state.get("project_dir", "")

        # Clean display path
        norm = p_dir.replace("\\", "/")
        marker = "My Drive/"
        clean_path = norm[norm.find(marker) + len(marker):] if marker in norm else os.path.basename(p_dir)

        bar = state["progress_bar"]
        pct = state["progress_pct"]
        done_cnt = state["completed_count"]
        tot_cnt = state["total_count"]
        scope_badge = state["scope_badge"]
        title_en = state["scope_title_en"]

        lines = [
            f"╭─ 📋 <b>PROJECT MILESTONE TRACKER</b> ───────────────",
            f"│ 👤 <b>Client:</b> <b>{c_name}</b>{id_str}",
            f"│ 🎓 <b>Scope:</b> <code>{scope_badge}</code>",
            f"│ 📊 <b>Progress:</b> <code>[{bar}] {pct}%</code> ({done_cnt}/{tot_cnt} Phases Done)",
            f"│ 📁 <b>Drive:</b> <code>{html.escape(clean_path)}</code>",
            f"╰──────────────────────────────────────────────────",
            "",
            f"📋 <b>{title_en}</b>",
            "<blockquote expandable>"
        ]

        for idx, m in enumerate(state["milestones"]):
            is_last = (idx == len(state["milestones"]) - 1)
            pfx = "└" if is_last else "├"
            st = m["status"]

            if st == "completed":
                icon = "☑️"
                st_label = "Completed"
            elif st == "in_progress":
                icon = "🔄"
                st_label = "In Progress"
            else:
                icon = "⬜"
                st_label = "Pending"

            code = m["code"]
            t_en = html.escape(m["title_en"])
            t_fa = html.escape(m["title_fa"])

            lines.append(f"{pfx} {icon} <b>{code}: {t_en}</b>")
            lines.append(f"│   <i>({t_fa})</i>")

            if m.get("matched_file"):
                f_name = html.escape(m["matched_file"])
                f_sz = m.get("file_size", "")
                sz_tag = f" ({f_sz})" if f_sz else ""
                lines.append(f"│   └ 📄 <code>{f_name}</code>{sz_tag} • <b>{st_label}</b>")
            else:
                d_note = html.escape(m.get("default_note", ""))
                lines.append(f"│   └ ⏳ <i>{d_note}</i> • <b>{st_label}</b>")

        lines.append("</blockquote>")
        lines.append("")
        lines.append("<i>Tap <b>Advance Stage</b> to complete the current phase, or <b>Switch Scope</b> to adapt the taxonomy.</i>")

        return "\n".join(lines)


# Singleton Instance
milestone_tracker = AcademicMilestoneTracker()
