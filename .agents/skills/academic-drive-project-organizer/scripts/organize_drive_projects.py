#!/usr/bin/env python3
"""
Academic Drive Project Organizer & Lifecycle Manager (organize_drive_projects.py)
---------------------------------------------------------------------------------
Automates the structural reorganization and lifecycle management of academic research
projects across Google Drive ('My Work', 'Pending Works', 'Finished Works'):
1. Audits existing project folders, detecting loose files, fragmented client directories,
   and unorganized assets.
2. Restructures project files into a deterministic 4-tier taxonomy:
   - 01_raw_inputs/        (proposals, questionnaires, raw .sav/.csv/.xlsx, screenshots)
   - 02_analysis_code/     (syntax .sps, R scripts, Jupyter .ipynb, SimDat models)
   - 03_deliverables/      (final chapters .docx, presentations .pptx, APA tables, drafts archive)
   - 04_references_and_lit/(EndNote .enl, RIS files, downloaded literature PDFs)
3. Synchronizes with Duzen backup (duzen_backup_*.json) to build a master financial
   and milestone tracking catalog (MASTER_PROJECT_CATALOG.xlsx & .md).
4. Provisions clean, standardized new project folders on demand with metadata.
5. Safely handles project lifecycle transitions between Pending, Active, and Finished stages.
6. Strictly safety-first: defaults to dry-run mode, creates undo manifests, and supports --undo.
"""

import os
import re
import sys
import json
import shutil
import argparse
import difflib
import unicodedata
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

# Default Google Drive paths for Saber Ghaderi
DEFAULT_DRIVE_ROOT = "/Users/saber/Library/CloudStorage/GoogleDrive-ghaderi.sabir@gmail.com/My Drive"
DEFAULT_MY_WORK_DIR = os.path.join(DEFAULT_DRIVE_ROOT, "My Work")


def resolve_pending_dir(drive_root: str = DEFAULT_DRIVE_ROOT) -> str:
    """Dynamically locate Pending Works either inside My Work or at root."""
    cand1 = os.path.join(drive_root, "My Work", "Pending Works")
    cand2 = os.path.join(drive_root, "Pending Works")
    if os.path.exists(cand1):
        return cand1
    if os.path.exists(cand2):
        return cand2
    return cand1


DEFAULT_PENDING_DIR = resolve_pending_dir(DEFAULT_DRIVE_ROOT)
DEFAULT_FINISHED_DIR = os.path.join(DEFAULT_DRIVE_ROOT, "Finished Works")
DEFAULT_DUZEN_BACKUP = os.path.join(DEFAULT_MY_WORK_DIR, "duzen_backup_2026-08-29.json")

SUBFOLDERS = {
    "raw": "01_raw_inputs",
    "code": "02_analysis_code",
    "deliverables": "03_deliverables",
    "deliverables_archive": os.path.join("03_deliverables", "drafts_archive"),
    "references": "04_references_and_lit"
}

STAGE_DIR_MAP = {
    "pending": DEFAULT_PENDING_DIR,
    "my_work": DEFAULT_MY_WORK_DIR,
    "active": DEFAULT_MY_WORK_DIR,
    "finished": DEFAULT_FINISHED_DIR,
}


def normalize_az_phonetic(text: str) -> str:
    """
    Normalize Azerbaijani Latin, Persian, and English names to a canonical phonetic key.
    Handles Azerbaijani characters (c -> j, ş -> sh, ç -> ch, ı/İ -> i, ə -> a, ö -> o, ü -> u, q -> gh, x -> kh),
    Persian alphabet transliteration, double consonants, and silent terminal letters.
    """
    if not text:
        return ""
    text = unicodedata.normalize("NFC", text).lower()

    char_map = {
        # Azerbaijani Latin
        "ə": "a", "ş": "sh", "ç": "ch", "c": "j", "ı": "i", "i̇": "i", "İ": "i",
        "ö": "o", "ü": "u", "ğ": "gh", "q": "gh", "x": "kh", "w": "v", "y": "i",
        # Persian Alphabet
        "ا": "a", "آ": "a", "ب": "b", "پ": "p", "ت": "t", "ث": "s",
        "ج": "j", "چ": "ch", "ح": "h", "خ": "kh", "د": "d", "ذ": "z",
        "ر": "r", "ز": "z", "ژ": "zh", "س": "s", "ش": "sh", "ص": "s",
        "ض": "z", "ط": "t", "ظ": "z", "ع": "a", "غ": "gh", "ف": "f",
        "ق": "gh", "ک": "k", "ك": "k", "گ": "g", "ل": "l", "م": "m",
        "ن": "n", "و": "v", "ه": "h", "ة": "h", "ی": "i", "ي": "i",
        "ئ": "i", "ء": ""
    }
    for k, v in char_map.items():
        text = text.replace(k, v)

    text = re.sub(r'\b(?:article|thesis|data|model|dissertation|disssertation)\b', '', text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"(.)\1+", r"\1", text)

    words = text.split()
    clean_words = []
    for w in words:
        if w.endswith("h"):
            w = w[:-1]
        if w.endswith("e"):
            w = w[:-1] + "a"
        clean_words.append(w)

    return " ".join(clean_words)


def match_client_names(name1: str, name2: str, threshold: float = 0.85) -> Tuple[bool, float]:
    """Check if two client names match across Azerbaijani, English, or Persian transliterations."""
    k1 = normalize_az_phonetic(name1)
    k2 = normalize_az_phonetic(name2)
    if not k1 or not k2:
        return False, 0.0
    if len(k1) < 3 or len(k2) < 3:
        return False, 0.0
    if k1 == k2:
        return True, 1.0

    # Substring match only if both keys are sufficiently long
    if len(k1) >= 5 and len(k2) >= 5:
        if k1 in k2 or k2 in k1:
            return True, 0.95

    words1 = [w for w in k1.split() if len(w) >= 3]
    words2 = [w for w in k2.split() if len(w) >= 3]
    if len(words1) >= 2 and all(w in k2 for w in words1):
        return True, 0.90
    if len(words2) >= 2 and all(w in k1 for w in words2):
        return True, 0.90

    ratio = difflib.SequenceMatcher(None, k1, k2).ratio()
    return (ratio >= threshold), ratio


def sanitize_filename(name: str) -> str:
    """Strip illegal filesystem characters."""
    if not name:
        return ""
    clean = re.sub(r'[\\/*?:"<>|]', "", name).strip()
    return clean


def classify_file_destination(filename: str, parent_folder_name: str = "") -> str:
    """Classify a single file into one of the 4 standard project subfolders."""
    lower = filename.lower()
    ext = os.path.splitext(lower)[1]

    # Ignore system / lock files / manifests / repository root files
    WORKSPACE_ROOT_FILES = {
        "agents.md", "readme.md", "setup_guide.md", "requirements.txt",
        "questionnaires.xlsx", ".gitignore", "license", "license.md", "license.txt"
    }
    if filename.startswith("~$") or filename in [".DS_Store", "Thumbs.db"]:
        return "temp_junk"
    if filename in ["project_meta.json", "reorganize_manifest.json"] or lower in WORKSPACE_ROOT_FILES:
        return "meta_file"

    # Already categorized folders
    if any(sub in parent_folder_name for sub in ["01_raw_inputs", "02_analysis_code", "03_deliverables", "04_references_and_lit"]):
        return "already_categorized"

    # 1. References & Literature
    if ext in [".enl", ".data", ".ris", ".enw", ".bib"]:
        return SUBFOLDERS["references"]
    if lower.startswith("articles") or lower.startswith("literature") or lower.startswith("references"):
        return SUBFOLDERS["references"]
    if "journals" in lower:
        return SUBFOLDERS["references"]
    if ext == ".pdf" and any(k in lower for k in ["article", "paper", "journal", "review", "springer", "elsevier", "wiley", "201", "202", "199"]):
        return SUBFOLDERS["references"]

    # 2. Analysis Code & Syntax (SPSS syntax, models, scripts, and SPSS outputs)
    if ext in [".sps", ".spv", ".ipynb", ".r", ".py", ".splscb", ".dim", ".m", ".sas"]:
        return SUBFOLDERS["code"]
    if ext == ".pdf" and any(k in lower for k in ["output", "syntax", "model", "analysis"]):
        return SUBFOLDERS["code"]

    # 3. Deliverables (Final Word docs, slides, templates, summaries)
    if "template" in lower:
        return SUBFOLDERS["deliverables"]
    if ext in [".pptx", ".ppt"]:
        return SUBFOLDERS["deliverables"]

    is_word_doc = ext in [".docx", ".doc", ".gdoc"]
    if is_word_doc:
        # Check if it is a draft archive
        if any(k in lower for k in ["(1)", "(2)", "(3)", "copy", "draft", "edit", "old", "backup", "نسخه قبلی", "-7199749465999597821", "(review)"]):
            return SUBFOLDERS["deliverables_archive"]
        # Deliverable keywords
        if any(k in lower for k in ["chapter", "فصل", "article", "مقاله", "نهایی", "final", "پایان", "رساله", "thesis", "report", "گزارش", "descriptive"]):
            return SUBFOLDERS["deliverables"]

    # 4. Raw Inputs
    if ext in [".sav", ".csv"]:
        return SUBFOLDERS["raw"]
    if ext in [".xlsx", ".xls"] and not any(k in lower for k in ["result", "table", "جدول", "خروجی"]):
        return SUBFOLDERS["raw"]
    if any(k in lower for k in ["proposal", "پروپوزال", "طرح", "questionnaire", "پرسشنامه", "مقیاس", "آزمون", "scales", "1_27463758866"]):
        return SUBFOLDERS["raw"]
    if ext in [".jpg", ".jpeg", ".png"] and ("photo_" in lower or "screenshot" in lower or "screen" in lower):
        return SUBFOLDERS["raw"]

    # Fallback by extension
    if ext in [".xlsx", ".xls"]:
        return SUBFOLDERS["deliverables"]
    if is_word_doc:
        return SUBFOLDERS["deliverables"]
    if ext == ".pdf":
        return SUBFOLDERS["raw"]

    return SUBFOLDERS["raw"]


def audit_projects_directory(dir_path: str) -> Dict[str, Any]:
    """Scan and audit an operational directory (e.g. Pending Works)."""
    if not os.path.exists(dir_path):
        return {"error": f"Directory not found: {dir_path}"}

    items = os.listdir(dir_path)
    folders = []
    loose_files = []
    temp_junk = []

    for it in items:
        if it.startswith("."):
            continue
        full_p = os.path.join(dir_path, it)
        if it.startswith("~$"):
            temp_junk.append(it)
        elif os.path.isdir(full_p):
            folders.append(it)
        else:
            loose_files.append(it)

    # Detect client clustering (e.g. Shahram Amiri, Shahram IRT, Shahram Manova...)
    client_clusters: Dict[str, List[str]] = {}
    for f in folders:
        words = re.split(r"[\s_\-]+", f)
        base_name = words[0]
        if len(words) > 1 and len(words[0]) > 2 and len(words[1]) > 2:
            base_name = f"{words[0]} {words[1]}"
        
        base_clean = base_name.lower().replace("article", "").replace("thesis", "").strip()
        matched_cluster = None
        for cl in client_clusters:
            if base_clean in cl or cl in base_clean:
                matched_cluster = cl
                break

        if matched_cluster:
            client_clusters[matched_cluster].append(f)
        else:
            client_clusters[base_clean] = [f]

    fragmented_clients = {k: v for k, v in client_clusters.items() if len(v) > 1}

    project_audits = []
    for f in sorted(folders):
        fp = os.path.join(dir_path, f)
        p_files = os.listdir(fp) if os.path.isdir(fp) else []
        categorized_counts = {
            SUBFOLDERS["raw"]: 0,
            SUBFOLDERS["code"]: 0,
            SUBFOLDERS["deliverables"]: 0,
            SUBFOLDERS["references"]: 0,
            "already_structured": 0,
            "temp_junk": 0
        }
        for pf in p_files:
            dest = classify_file_destination(pf, f)
            if dest == "already_categorized":
                categorized_counts["already_structured"] += 1
            elif dest == "temp_junk":
                categorized_counts["temp_junk"] += 1
            elif dest in categorized_counts:
                categorized_counts[dest] += 1
            elif SUBFOLDERS["deliverables"] in dest:
                categorized_counts[SUBFOLDERS["deliverables"]] += 1

        is_structured = os.path.isdir(os.path.join(fp, SUBFOLDERS["raw"])) and os.path.isdir(os.path.join(fp, SUBFOLDERS["deliverables"]))

        project_audits.append({
            "folder_name": f,
            "total_files": len(p_files),
            "is_structured": is_structured,
            "file_counts": categorized_counts
        })

    return {
        "directory_path": dir_path,
        "total_items": len(items),
        "total_project_folders": len(folders),
        "loose_files_count": len(loose_files),
        "loose_files": loose_files,
        "temp_junk_count": len(temp_junk),
        "fragmented_clients_count": len(fragmented_clients),
        "fragmented_clients": fragmented_clients,
        "project_audits": project_audits
    }


def reorganize_single_project(
    project_dir: str,
    apply_changes: bool = False,
    clean_junk: bool = False
) -> Dict[str, Any]:
    """Sort and reorganize files inside a project directory into the 4 subfolders."""
    if not os.path.isdir(project_dir):
        return {"error": f"Not a directory: {project_dir}"}

    project_name = os.path.basename(project_dir)
    items = os.listdir(project_dir)

    actions = []
    manifest_records = []
    created_dirs = set()

    for it in items:
        if it.startswith(".") or it in SUBFOLDERS.values() or it == "project_meta.json" or it == "reorganize_manifest.json":
            continue

        src_path = os.path.join(project_dir, it)
        dest_cat = classify_file_destination(it, project_name)

        if dest_cat == "temp_junk":
            if clean_junk and apply_changes:
                try:
                    os.remove(src_path)
                    actions.append({"action": "remove_junk", "file": it})
                except Exception as e:
                    actions.append({"action": "error", "file": it, "error": str(e)})
            else:
                actions.append({"action": "skip_junk", "file": it})
            continue

        if dest_cat in ["already_categorized", "meta_file"]:
            continue

        target_subfolder = os.path.join(project_dir, dest_cat)
        target_file_path = os.path.join(target_subfolder, it)

        action_entry = {
            "action": "move",
            "file": it,
            "source": src_path,
            "destination_folder": dest_cat,
            "target_path": target_file_path
        }
        actions.append(action_entry)

        if apply_changes:
            os.makedirs(target_subfolder, exist_ok=True)
            created_dirs.add(target_subfolder)
            try:
                final_dest = target_file_path
                if os.path.exists(final_dest):
                    base, ext = os.path.splitext(it)
                    final_dest = os.path.join(target_subfolder, f"{base}_reorg{ext}")
                shutil.move(src_path, final_dest)
                manifest_records.append({
                    "original_path": src_path,
                    "new_path": final_dest
                })
            except Exception as e:
                actions.append({"action": "error", "file": it, "error": str(e)})

    # Generate metadata file & undo manifest if applying
    if apply_changes:
        meta_path = os.path.join(project_dir, "project_meta.json")
        meta = {
            "project_name": project_name,
            "reorganized_at": datetime.now().isoformat(),
            "status": "in_progress",
            "subfolders": list(SUBFOLDERS.values())
        }
        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as mf:
                    existing_meta = json.load(mf)
                    existing_meta.update(meta)
                    meta = existing_meta
            except Exception:
                pass
        with open(meta_path, "w", encoding="utf-8") as mf:
            json.dump(meta, mf, ensure_ascii=False, indent=2)

        if manifest_records:
            manifest_path = os.path.join(project_dir, "reorganize_manifest.json")
            manifest_data = {
                "project_name": project_name,
                "timestamp": datetime.now().isoformat(),
                "records": manifest_records
            }
            with open(manifest_path, "w", encoding="utf-8") as mf:
                json.dump(manifest_data, mf, ensure_ascii=False, indent=2)

    return {
        "project_name": project_name,
        "applied": apply_changes,
        "total_planned_actions": len(actions),
        "actions": actions
    }


def undo_reorganization(manifest_path: str) -> Dict[str, Any]:
    """Reverses file movements based on a reorganize_manifest.json file."""
    if not os.path.exists(manifest_path):
        return {"error": f"Manifest file not found: {manifest_path}"}

    with open(manifest_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    records = data.get("records", [])
    restored = []
    errors = []

    for r in reversed(records):
        new_p = r.get("new_path")
        orig_p = r.get("original_path")
        if new_p and orig_p and os.path.exists(new_p):
            try:
                os.makedirs(os.path.dirname(orig_p), exist_ok=True)
                shutil.move(new_p, orig_p)
                restored.append({"from": new_p, "to": orig_p})
            except Exception as e:
                errors.append({"file": new_p, "error": str(e)})

    return {
        "manifest": manifest_path,
        "total_records": len(records),
        "restored_count": len(restored),
        "restored": restored,
        "errors": errors
    }


def move_project_stage(
    project_name: str,
    target_stage: str,
    drive_root: str = DEFAULT_DRIVE_ROOT,
    apply: bool = False
) -> Dict[str, Any]:
    """Move a project folder between Pending, My Work, and Finished Works."""
    target_stage_clean = target_stage.lower().strip()
    if target_stage_clean not in STAGE_DIR_MAP:
        return {"error": f"Invalid stage '{target_stage}'. Valid options: pending, my_work, active, finished"}

    target_root = STAGE_DIR_MAP[target_stage_clean]

    # Search for project in the 3 standard roots
    found_root = None
    found_folder = None
    for stage_key, root_p in [("Pending Works", DEFAULT_PENDING_DIR), ("My Work", DEFAULT_MY_WORK_DIR), ("Finished Works", DEFAULT_FINISHED_DIR)]:
        if not os.path.exists(root_p):
            continue
        for it in os.listdir(root_p):
            if it.lower() == project_name.lower():
                found_root = root_p
                found_folder = it
                break
        if found_folder:
            break

    if not found_folder:
        return {"error": f"Project folder '{project_name}' not found in Pending, My Work, or Finished Works."}

    src_full_path = os.path.join(found_root, found_folder)
    dest_full_path = os.path.join(target_root, found_folder)

    if src_full_path == dest_full_path:
        return {"message": f"Project '{found_folder}' is already in target stage ({os.path.basename(target_root)})."}

    res = {
        "project_name": found_folder,
        "source_stage": os.path.basename(found_root),
        "target_stage": os.path.basename(target_root),
        "source_path": src_full_path,
        "target_path": dest_full_path,
        "applied": apply
    }

    if apply:
        if os.path.exists(dest_full_path):
            return {"error": f"Destination already exists: {dest_full_path}"}
        shutil.move(src_full_path, dest_full_path)
        # Update project_meta.json
        meta_file = os.path.join(dest_full_path, "project_meta.json")
        meta = {}
        if os.path.exists(meta_file):
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
            except Exception:
                pass
        meta["status"] = target_stage_clean
        meta["last_stage_transition"] = {
            "from": os.path.basename(found_root),
            "to": os.path.basename(target_root),
            "timestamp": datetime.now().isoformat()
        }
        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

    return res


def generate_duzen_cross_reference(
    backup_path: str = DEFAULT_DUZEN_BACKUP,
    drive_folders: Optional[List[str]] = None
) -> Dict[str, Any]:
    """Match Duzen projects with Google Drive folders and build unified catalog."""
    if not os.path.exists(backup_path):
        return {"error": f"Duzen backup not found at {backup_path}"}

    with open(backup_path, "r", encoding="utf-8") as f:
        duzen_data = json.load(f)

    duzen_projects = duzen_data.get("projects", [])
    duzen_steps = duzen_data.get("steps", [])
    duzen_payments = duzen_data.get("payments", [])

    steps_by_proj = {}
    for st in duzen_steps:
        pid = st.get("projectId")
        steps_by_proj.setdefault(pid, []).append(st)

    payments_by_proj = {}
    for pm in duzen_payments:
        pid = pm.get("projectId")
        payments_by_proj.setdefault(pid, []).append(pm)

    catalog = []
    folders_list = drive_folders or []

    for p in duzen_projects:
        pid = p.get("id")
        title = p.get("title", "")
        client = p.get("clientName", "")
        status = p.get("status", "Unknown")
        total_price = p.get("manuallySetTotalPrice")

        p_steps = steps_by_proj.get(pid, [])
        p_payments = payments_by_proj.get(pid, [])
        paid_amount = sum(float(pm.get("amount", 0)) for pm in p_payments if pm.get("amount"))

        matched_folder = None
        best_score = 0.0

        for f in folders_list:
            clean_f = re.sub(r'^\[[^\]]+\]\s*', '', f)

            # Match client name
            if client:
                m_client, s_client = match_client_names(client, clean_f)
                if m_client and s_client > best_score:
                    best_score = s_client
                    matched_folder = f

            # Match project title
            if title:
                m_title, s_title = match_client_names(title, clean_f)
                if m_title and s_title > best_score:
                    best_score = s_title
                    matched_folder = f

            if best_score >= 0.95:
                break

        catalog.append({
            "duzen_id": pid,
            "project_title": title,
            "client_name": client,
            "status": status,
            "total_price": total_price,
            "paid_amount": paid_amount,
            "step_count": len(p_steps),
            "payment_count": len(p_payments),
            "matched_drive_folder": matched_folder or "Not linked",
            "is_linked_to_drive": matched_folder is not None
        })

    return {
        "duzen_total_projects": len(duzen_projects),
        "linked_projects_count": sum(1 for c in catalog if c["is_linked_to_drive"]),
        "catalog": catalog
    }


def format_audit_markdown(audit: Dict[str, Any]) -> str:
    """Format audit results as a readable Markdown dashboard."""
    lines = []
    lines.append("# 📊 Google Drive Academic Projects Audit Report")
    lines.append(f"**Target Directory:** `{audit['directory_path']}`")
    lines.append(f"**Generated At:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append("## 1. Executive Summary")
    lines.append(f"- **Total Items:** {audit['total_items']}")
    lines.append(f"- **Client Project Folders:** {audit['total_project_folders']}")
    lines.append(f"- **Loose Files in Root:** {audit['loose_files_count']}")
    lines.append(f"- **Temporary / Lock Files:** {audit['temp_junk_count']}")
    lines.append(f"- **Fragmented Client Clusters:** {audit['fragmented_clients_count']}")
    lines.append("")

    if audit.get("loose_files"):
        lines.append("## 2. Loose Files in Root (Needs Assignment)")
        for lf in audit["loose_files"]:
            lines.append(f"- 📄 `{lf}`")
        lines.append("")

    if audit.get("fragmented_clients"):
        lines.append("## 3. Fragmented Client Folders (Candidates for Merging)")
        for client, group in audit["fragmented_clients"].items():
            lines.append(f"- 👤 **{client}** ({len(group)} folders):")
            for subf in group:
                lines.append(f"  ▫️ `{subf}`")
        lines.append("")

    lines.append("## 4. Project Folder Status & Restructuring Needs")
    lines.append("| Client Folder | Total Files | Raw Inputs | Code / Syntax | Deliverables | References | Status |")
    lines.append("| :--- | :---: | :---: | :---: | :---: | :---: | :---: |")
    for pa in audit.get("project_audits", [])[:40]:
        fc = pa["file_counts"]
        status = "✅ Structured" if pa["is_structured"] else "⚠️ Needs Tidy"
        lines.append(
            f"| `{pa['folder_name']}` | {pa['total_files']} | {fc.get(SUBFOLDERS['raw'], 0)} | "
            f"{fc.get(SUBFOLDERS['code'], 0)} | {fc.get(SUBFOLDERS['deliverables'], 0)} | "
            f"{fc.get(SUBFOLDERS['references'], 0)} | {status} |"
        )

    return "\n".join(lines)


def format_duzen_catalog_markdown(catalog_res: Dict[str, Any]) -> str:
    """Format Duzen sync catalog as Markdown table."""
    lines = []
    lines.append("# 📑 Master Project Catalog (Duzen & Google Drive Sync)")
    lines.append(f"**Total Duzen Projects:** {catalog_res['duzen_total_projects']}")
    lines.append(f"**Linked to Drive Folders:** {catalog_res['linked_projects_count']}")
    lines.append("")
    lines.append("| Project Title | Client | Status | Price (M Tomans) | Steps | Paid | Drive Folder |")
    lines.append("| :--- | :--- | :---: | :---: | :---: | :---: | :--- |")
    for row in catalog_res.get("catalog", []):
        price_str = f"{row['total_price']}" if row['total_price'] is not None else "-"
        lines.append(
            f"| {row['project_title']} | {row['client_name']} | `{row['status']}` | "
            f"{price_str} | {row['step_count']} | {row['paid_amount']} | `{row['matched_drive_folder']}` |"
        )
    return "\n".join(lines)


def export_duzen_catalog_excel(catalog_res: Dict[str, Any], output_path: str):
    """Export the Duzen and Drive catalog to an Excel workbook with formatting."""
    if not HAS_PANDAS:
        return
    df = pd.DataFrame(catalog_res.get("catalog", []))
    rename_cols = {
        "duzen_id": "Duzen ID",
        "project_title": "Project Title",
        "client_name": "Client Name",
        "status": "Status",
        "total_price": "Total Price (M Tomans)",
        "paid_amount": "Paid (Tomans)",
        "step_count": "Steps",
        "payment_count": "Payments",
        "matched_drive_folder": "Matched Drive Folder",
        "is_linked_to_drive": "Linked to Drive"
    }
    df = df.rename(columns=rename_cols)
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Master Catalog", index=False)


def provision_new_project_folder(parent_dir: str, client_name: str, topic: Optional[str] = None) -> str:
    """Create a standardized new project folder."""
    clean_name = re.sub(r'[\\/*?:"<>|]', "", client_name).strip()
    if topic:
        clean_topic = re.sub(r'[\\/*?:"<>|]', "", topic).strip()
        folder_name = f"{clean_name} - {clean_topic}"
    else:
        folder_name = clean_name

    target_dir = os.path.join(parent_dir, folder_name)
    os.makedirs(target_dir, exist_ok=True)

    for sub in SUBFOLDERS.values():
        os.makedirs(os.path.join(target_dir, sub), exist_ok=True)

    meta = {
        "client_name": clean_name,
        "project_title": topic or clean_name,
        "created_at": datetime.now().isoformat(),
        "status": "pending",
        "subfolders": list(SUBFOLDERS.values())
    }
    with open(os.path.join(target_dir, "project_meta.json"), "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

    return target_dir


def consolidate_vip_client(
    client_query: str,
    drive_root: str = DEFAULT_DRIVE_ROOT,
    apply: bool = True
) -> Dict[str, Any]:
    """
    Consolidates all scattered projects and folders for a high-volume VIP client
    across Pending, My Work, and Finished stages into a unified Umbrella Architecture.
    """
    pending_dir = os.path.join(drive_root, "Pending Works")
    my_work_dir = os.path.join(drive_root, "My Work")
    finished_dir = os.path.join(drive_root, "Finished Works")

    def norm(t: str) -> str:
        t = t.lower()
        t = t.replace("shahram", "sehram").replace("şəhram", "sehram").replace("amiri", "emiri").replace("əmiri", "emiri")
        for c1, c2 in [("ş", "s"), ("ə", "e"), ("ı", "i"), ("ç", "c"), ("ğ", "g"), ("ö", "o"), ("ü", "u"), ("ي", "ی"), ("ك", "ک"), ("\u200c", " ")]:
            t = t.replace(c1, c2)
        return t

    # Check VIP registry for canonical details
    reg_paths = [
        os.path.join(os.path.dirname(__file__), "..", "..", "digital-twin-academic-consultant", "scripts", "userbot_storage", "vip_clients.json"),
        "/Users/saber/Desktop/academic_suite/.agents/skills/digital-twin-academic-consultant/scripts/userbot_storage/vip_clients.json"
    ]
    vip_entry = None
    for rp in reg_paths:
        if os.path.exists(rp):
            try:
                with open(rp, "r", encoding="utf-8") as f:
                    vdata = json.load(f)
                    for v in vdata.get("vip_clients", []):
                        v_name_norm = norm(v.get("client_name", ""))
                        v_fa_norm = norm(v.get("client_name_fa", ""))
                        if any(norm(q) in v_name_norm or norm(q) in v_fa_norm for q in client_query.split() if len(q) > 2):
                            vip_entry = v
                            break
            except Exception:
                pass
        if vip_entry:
            break

    canonical_name = vip_entry.get("client_name", client_query) if vip_entry else client_query
    canonical_fa = vip_entry.get("client_name_fa", canonical_name) if vip_entry else canonical_name
    client_id = vip_entry.get("telegram_id") if vip_entry else None
    phone = vip_entry.get("phone") if vip_entry else ""

    umbrella_dir = vip_entry.get("umbrella_dir") if (vip_entry and vip_entry.get("umbrella_dir")) else os.path.join(my_work_dir, sanitize_filename(canonical_name))

    locations = [
        ("My Work", my_work_dir),
        ("Pending Works", pending_dir),
        ("Finished Works", finished_dir)
    ]

    discovered = []
    for loc_name, loc_path in locations:
        if not os.path.exists(loc_path):
            continue
        for item in sorted(os.listdir(loc_path)):
            full_p = os.path.join(loc_path, item)
            if not os.path.isdir(full_p) or item.startswith("."):
                continue
            # Avoid matching the umbrella directory itself
            if os.path.abspath(full_p) == os.path.abspath(umbrella_dir):
                continue
            # Match query keywords
            query_words = [norm(w) for w in client_query.split() if len(w) > 2]
            item_norm = norm(item)
            if any(w in item_norm for w in query_words) and "hamid" not in item_norm:
                try:
                    f_count = len([f for f in os.listdir(full_p) if not f.startswith(".")])
                except Exception:
                    f_count = 0

                lower = item.lower()
                if "soldier" in lower or "variance" in lower or "manova" in lower:
                    p_type = "Simulation & MANOVA (تحلیل واریانس چندمتغیره)"
                elif "model" in lower or "amos" in lower or "pls" in lower:
                    p_type = "Structural Equation Modeling (مدل‌یابی معادلات ساختاری)"
                elif "case" in lower:
                    p_type = "Single-Case Experimental Design (طرح‌های تک‌آزمودنی)"
                elif "reference" in lower or "ref" in lower:
                    p_type = "Reference & Bibliographic Extraction (استخراج منابع)"
                elif "repeated" in lower:
                    p_type = "Repeated Measures ANCOVA (اندازه‌گیری مکرر)"
                elif "irt" in lower:
                    p_type = "Item Response Theory (نظریه سوال‌پاسخ)"
                elif "questionaire" in lower or "questionnaire" in lower:
                    p_type = "Psychometric Questionnaire Scoring (نمره‌گذاری ابزارها)"
                elif "article" in lower:
                    p_type = "Journal Manuscript Compilation (نگارش و تدوین مقاله)"
                else:
                    p_type = "Statistical Consultation & Thesis Chapter (تحلیل آماری)"

                status = "Completed (انجام‌شده)" if loc_name == "Finished Works" else ("Active (در حال انجام/تحویل)" if loc_name == "My Work" else "Pending (در انتظار تایید/پیشنهاد)")
                if "soldier" in lower:
                    status = "Completed & Verified (نهایی‌شده با پیش‌فرض‌ها)"

                discovered.append({
                    "Project Name": item,
                    "Lifecycle Location": loc_name,
                    "Research Type": p_type,
                    "File Count": f_count,
                    "Status": status,
                    "Path": full_p
                })

    if apply:
        os.makedirs(umbrella_dir, exist_ok=True)
        comm_dir = os.path.join(umbrella_dir, "00_general_communications")
        os.makedirs(comm_dir, exist_ok=True)

        now_iso = datetime.now().isoformat()
        u_meta_file = os.path.join(umbrella_dir, "project_meta.json")
        existing_u_meta = {}
        if os.path.exists(u_meta_file):
            try:
                with open(u_meta_file, "r", encoding="utf-8") as f:
                    existing_u_meta = json.load(f)
            except Exception:
                existing_u_meta = {}

        umbrella_meta = {
            "is_umbrella_client_folder": True,
            "client_name": canonical_name,
            "client_name_fa": canonical_fa,
            "telegram_id": client_id,
            "phone": phone,
            "vip_tier": vip_entry.get("tier", "tier_1_collaborator") if vip_entry else "tier_1_collaborator",
            "pricing_discount_percent": vip_entry.get("pricing_discount_percent", 15) if vip_entry else 15,
            "total_historical_projects": len(discovered),
            "active_subprojects": existing_u_meta.get("active_subprojects", []),
            "created_at": existing_u_meta.get("created_at", now_iso),
            "updated_at": now_iso
        }
        with open(u_meta_file, "w", encoding="utf-8") as f:
            json.dump(umbrella_meta, f, ensure_ascii=False, indent=2)

        idx_file = os.path.join(umbrella_dir, "master_projects_index.json")
        with open(idx_file, "w", encoding="utf-8") as f:
            json.dump({
                "client": {"name": canonical_name, "name_fa": canonical_fa, "id": client_id, "phone": phone},
                "total_count": len(discovered),
                "projects": discovered
            }, f, ensure_ascii=False, indent=2)

        ledger_path = os.path.join(umbrella_dir, "CLIENT_LEDGER.xlsx")
        if HAS_PANDAS and discovered:
            df_cat = pd.DataFrame(discovered)
            with pd.ExcelWriter(ledger_path, engine="openpyxl") as writer:
                df_active = df_cat[df_cat["Lifecycle Location"] == "My Work"]
                df_active.to_excel(writer, sheet_name="Active_Projects", index=False)
                df_pending = df_cat[df_cat["Lifecycle Location"] == "Pending Works"]
                df_pending.to_excel(writer, sheet_name="Pending_Projects", index=False)
                df_finished = df_cat[df_cat["Lifecycle Location"] == "Finished Works"]
                df_finished.to_excel(writer, sheet_name="Historical_Finished", index=False)
                summary_df = pd.DataFrame([
                    {"Metric": "نام کلاینت", "Value": f"{canonical_fa} ({canonical_name})"},
                    {"Metric": "شناسه تلگرام", "Value": client_id},
                    {"Metric": "شماره تماس", "Value": f"+{phone}" if phone else "N/A"},
                    {"Metric": "سطح همکاری (VIP Tier)", "Value": "همکار ارشد (Tier 1 Collaborator)"},
                    {"Metric": "تخفیف ویژه همکار", "Value": "15%"},
                    {"Metric": "تعداد کل پروژه‌ها در درایو", "Value": len(discovered)},
                    {"Metric": "پروژه‌های در حال انجام (My Work)", "Value": len(df_active)},
                    {"Metric": "پروژه‌های در انتظار بررسی (Pending Works)", "Value": len(df_pending)},
                    {"Metric": "پروژه‌های نهایی‌شده (Finished Works)", "Value": len(df_finished)},
                    {"Metric": "تاریخ آخرین به‌روزرسانی", "Value": datetime.now().strftime("%Y-%m-%d %H:%M")}
                ])
                summary_df.to_excel(writer, sheet_name="Client_Dossier_Summary", index=False)

    return {
        "client_name": canonical_name,
        "discovered_count": len(discovered),
        "umbrella_dir": umbrella_dir,
        "ledger_path": os.path.join(umbrella_dir, "CLIENT_LEDGER.xlsx") if HAS_PANDAS else None,
        "projects": discovered
    }


def main():
    parser = argparse.ArgumentParser(description="Academic Drive Project Organizer & Lifecycle Manager")
    parser.add_argument("--dir", "-d", type=str, default=DEFAULT_PENDING_DIR, help="Target directory to audit or reorganize")
    parser.add_argument("--audit", action="store_true", help="Run audit scan on target directory and output Markdown dashboard")
    parser.add_argument("--audit-all", action="store_true", help="Audit all three Google Drive roots: Pending, My Work, Finished")
    parser.add_argument("--tidy", action="store_true", help="Organize files in target project folder(s) into the 4 subfolders")
    parser.add_argument("--project", "-p", type=str, help="Specific project folder name inside target dir to tidy")
    parser.add_argument("--apply", action="store_true", help="Actually move files (without this, runs in dry-run mode)")
    parser.add_argument("--clean-junk", action="store_true", help="Remove temporary lock files (~$*) and .DS_Store")
    parser.add_argument("--sync-duzen", action="store_true", help="Cross-reference Duzen backup against Drive folders")
    parser.add_argument("--duzen-backup", type=str, default=DEFAULT_DUZEN_BACKUP, help="Path to duzen_backup_*.json")
    parser.add_argument("--new-project", type=str, help="Provision a new standardized project folder with this client name")
    parser.add_argument("--topic", type=str, help="Topic for new project")
    parser.add_argument("--move-project", type=str, help="Project name to move across lifecycle stages")
    parser.add_argument("--to", type=str, help="Target lifecycle stage: pending, my_work, active, finished")
    parser.add_argument("--undo", type=str, help="Path to reorganize_manifest.json to undo a previous reorganization")
    parser.add_argument("--consolidate-vip", type=str, help="Consolidate all projects for a repeat VIP client into a master umbrella directory")
    parser.add_argument("--output-dir", "-o", type=str, default=".", help="Output directory for reports")

    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    # 0. Consolidate VIP Client Umbrella
    if args.consolidate_vip:
        res = consolidate_vip_client(
            client_query=args.consolidate_vip,
            drive_root=DEFAULT_DRIVE_ROOT,
            apply=True
        )
        print(f"[+] VIP Client Umbrella Consolidation Completed:")
        print(f"    Client: {res.get('client_name')}")
        print(f"    Discovered Projects Across Drive: {res.get('discovered_count', 0)}")
        print(f"    Umbrella Directory: {res.get('umbrella_dir')}")
        if res.get('ledger_path'):
            print(f"    Consolidated Ledger: {res.get('ledger_path')}")
        sys.exit(0)

    # 1. Undo operation
    if args.undo:
        res = undo_reorganization(args.undo)
        print(f"[+] Undo completed for: {args.undo}")
        print(f"    Restored files: {res.get('restored_count', 0)}")
        if res.get("errors"):
            print(f"    Errors encountered: {len(res['errors'])}")
        sys.exit(0)

    # 2. Lifecycle stage transition
    if args.move_project and args.to:
        res = move_project_stage(args.move_project, args.to, apply=args.apply)
        if "error" in res:
            print(f"[-] Error: {res['error']}")
            sys.exit(1)
        if "message" in res:
            print(f"[i] {res['message']}")
            sys.exit(0)
        mode = "APPLIED" if args.apply else "DRY-RUN"
        print(f"[+] Lifecycle Stage Transition ({mode}):")
        print(f"    Project: {res['project_name']}")
        print(f"    From: {res['source_stage']} -> To: {res['target_stage']}")
        print(f"    Target Path: {res['target_path']}")
        sys.exit(0)

    # 3. Provision new project
    if args.new_project:
        p_dir = provision_new_project_folder(args.dir, args.new_project, args.topic)
        print(f"[+] Successfully provisioned standard project folder:\n    {p_dir}")
        sys.exit(0)

    # 4. Sync with Duzen
    if args.sync_duzen:
        all_drive_folders = []
        seen_roots = set()
        for root_p in [DEFAULT_MY_WORK_DIR, DEFAULT_PENDING_DIR, DEFAULT_FINISHED_DIR]:
            if os.path.exists(root_p) and os.path.abspath(root_p) not in seen_roots:
                seen_roots.add(os.path.abspath(root_p))
                tag = os.path.basename(root_p)
                for f in os.listdir(root_p):
                    if os.path.isdir(os.path.join(root_p, f)) and not f.startswith(".") and f != "Pending Works":
                        all_drive_folders.append(f"[{tag}] {f}")

        res = generate_duzen_cross_reference(args.duzen_backup, all_drive_folders)
        md_content = format_duzen_catalog_markdown(res)
        out_file = os.path.join(args.output_dir, "MASTER_PROJECT_CATALOG.md")
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(md_content)

        out_xlsx = os.path.join(args.output_dir, "MASTER_PROJECT_CATALOG.xlsx")
        export_duzen_catalog_excel(res, out_xlsx)

        print(f"[+] Duzen cross-reference catalog generated across all Google Drive roots:")
        print(f"    Total Duzen Projects: {res['duzen_total_projects']}")
        print(f"    Linked to Drive: {res['linked_projects_count']}")
        print(f"    Markdown: {out_file}")
        if HAS_PANDAS:
            print(f"    Excel:    {out_xlsx}")
        sys.exit(0)

    # 5. Audit all roots
    if args.audit_all:
        print("[+] Running audit across all 3 Google Drive roots...")
        all_reports = []
        for root_p in [DEFAULT_PENDING_DIR, DEFAULT_MY_WORK_DIR, DEFAULT_FINISHED_DIR]:
            if os.path.exists(root_p):
                audit_res = audit_projects_directory(root_p)
                all_reports.append(format_audit_markdown(audit_res))
        full_report = "\n\n---\n\n".join(all_reports)
        out_file = os.path.join(args.output_dir, "ALL_PROJECTS_AUDIT_REPORT.md")
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(full_report)
        print(f"[+] Multi-root audit complete. Report written to:\n    {out_file}")
        sys.exit(0)

    # 6. Tidy specific project or all
    if args.tidy:
        if args.project:
            p_path = os.path.join(args.dir, args.project) if not os.path.isabs(args.project) else args.project
            res = reorganize_single_project(p_path, apply_changes=args.apply, clean_junk=args.clean_junk)
            print(f"[+] Tidy completed for: {args.project} (Applied: {args.apply})")
            print(f"    Actions: {res['total_planned_actions']}")
            for a in res.get("actions", [])[:15]:
                print(f"    • {a.get('action')}: {a.get('file')} -> {a.get('destination_folder')}")
        else:
            print("[-] Please specify a project folder to tidy using --project <FolderName>, or use --audit to view all.")
        sys.exit(0)

    # 7. Default: Audit mode for specified --dir
    audit_res = audit_projects_directory(args.dir)
    md_report = format_audit_markdown(audit_res)
    out_file = os.path.join(args.output_dir, "PROJECTS_AUDIT_REPORT.md")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(md_report)

    json_file = os.path.join(args.output_dir, "audit_summary.json")
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(audit_res, f, ensure_ascii=False, indent=2)

    print(f"[+] Audit completed for: {args.dir}")
    print(f"    Project Folders: {audit_res['total_project_folders']}")
    print(f"    Loose Files: {audit_res['loose_files_count']}")
    print(f"    Fragmented Clients: {audit_res['fragmented_clients_count']}")
    print(f"    Report: {out_file}")


if __name__ == "__main__":
    main()
