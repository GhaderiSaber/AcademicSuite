#!/usr/bin/env python3
"""
Restructure Zahra Jalali project files into the standard 4-tier taxonomy:
- 01_raw_inputs
- 02_analysis_code
- 03_deliverables (and 03_deliverables/drafts_archive)
- 04_references_and_lit

Saves an undo manifest to reorganize_manifest.json and updates project_meta.json.
"""

import os
import sys
import json
import shutil
from datetime import datetime

# Enforce UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.abspath("g:/My Drive/My Work/Zahra Jalali")

SUBFOLDERS = {
    "raw": os.path.join(ROOT_DIR, "01_raw_inputs"),
    "questionnaires": os.path.join(ROOT_DIR, "01_raw_inputs", "Questionnaires"),
    "code": os.path.join(ROOT_DIR, "02_analysis_code"),
    "code_archive": os.path.join(ROOT_DIR, "02_analysis_code", "archive_old"),
    "deliverables": os.path.join(ROOT_DIR, "03_deliverables"),
    "drafts_archive": os.path.join(ROOT_DIR, "03_deliverables", "drafts_archive"),
    "references": os.path.join(ROOT_DIR, "04_references_and_lit")
}

def main():
    print(f"Starting reorganization in: {ROOT_DIR}")
    for sub in SUBFOLDERS.values():
        os.makedirs(sub, exist_ok=True)

    manifest_records = []

    def safe_move(src, dest):
        if not os.path.exists(src):
            print(f"Skipping (not found): {src}")
            return
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if os.path.exists(dest):
            if os.path.isdir(dest) and os.path.isdir(src):
                # merge dir
                for item in os.listdir(src):
                    safe_move(os.path.join(src, item), os.path.join(dest, item))
                try:
                    os.rmdir(src)
                except Exception:
                    pass
                return
            else:
                base, ext = os.path.splitext(dest)
                dest = f"{base}_reorg{ext}"
        print(f"Moving: {os.path.basename(src)} -> {dest}")
        shutil.move(src, dest)
        manifest_records.append({
            "original_path": src,
            "new_path": dest
        })

    # 1. 01_raw_inputs
    raw_root_files = [
        "Sampling.xlsx",
        "الگوی نگارش پایان نامه.docx",
        "راهنمای نگارش پایان نامه_2.pdf"
    ]
    for rf in raw_root_files:
        src = os.path.join(ROOT_DIR, rf)
        dest = os.path.join(SUBFOLDERS["raw"], rf)
        safe_move(src, dest)

    # Move Questionaire contents into 01_raw_inputs/Questionnaires
    questionaire_dir = os.path.join(ROOT_DIR, "Questionaire")
    if os.path.exists(questionaire_dir):
        for qf in os.listdir(questionaire_dir):
            safe_move(os.path.join(questionaire_dir, qf), os.path.join(SUBFOLDERS["questionnaires"], qf))
        try:
            os.rmdir(questionaire_dir)
            print("Removed empty Questionaire directory")
        except Exception as e:
            print(f"Could not remove Questionaire dir: {e}")

    # Move raw datasets and screenshots from Data Analysis
    data_analysis_dir = os.path.join(ROOT_DIR, "Data Analysis")
    raw_from_analysis = [
        "primary_data.xlsx",
        "Whole Data.xlsx",
        "Data Main.csv",
        "Data Main.sav",
        "Data.sav",
        "Fianl_data_number.csv",
        "Final_data.sav",
        "final_data.xlsx",
        "final_data_number.csv",
        "Screenshot 2025-02-28 at 4.53.09 PM.png",
        "Screenshot 2025-03-19 at 12.51.31 PM.png",
        "Screenshot 2025-03-19 at 12.51.39 PM.png"
    ]
    # Check for unicode matching in Screenshot files
    if os.path.exists(data_analysis_dir):
        analysis_items = os.listdir(data_analysis_dir)
        for item in analysis_items:
            for target in raw_from_analysis:
                if item.replace(" ", "").replace(" ", "") == target.replace(" ", "").replace(" ", ""):
                    safe_move(os.path.join(data_analysis_dir, item), os.path.join(SUBFOLDERS["raw"], item))
                    break

    # 2. 02_analysis_code
    code_files = [
        "Create Main Data.ipynb",
        "Data Making.ipynb",
        "Data Preprocessing.ipynb",
        "Model Analysis (Thesis).ipynb",
        "Model Analysis.ipynb",
        "Regression.ipynb",
        "Syntax1.sps"
    ]
    if os.path.exists(data_analysis_dir):
        for cf in code_files:
            safe_move(os.path.join(data_analysis_dir, cf), os.path.join(SUBFOLDERS["code"], cf))
        
        # Move Old folder into code_archive
        old_dir = os.path.join(data_analysis_dir, "Old")
        if os.path.exists(old_dir):
            safe_move(old_dir, SUBFOLDERS["code_archive"])

    # 3. 03_deliverables
    # Main deliverables from root
    main_deliverables_root = [
        "Chapter 4.docx",
        "Dissertation.docx",
        "FINALJALALIword.docx",
        "نهایی-پایان نامه.docx",
        "نهایی-پایان نامه.pdf",
        "پایان نامه-جلالی-کامل.docx",
        "مقاله-نهایی-جلالی.docx",
        "Article 2-نهایی.docx",
        "Article.docx",
        "Article.pdf"
    ]
    for mdf in main_deliverables_root:
        safe_move(os.path.join(ROOT_DIR, mdf), os.path.join(SUBFOLDERS["deliverables"], mdf))

    # Deliverables & results from Data Analysis
    if os.path.exists(data_analysis_dir):
        remaining_analysis_items = [
            "Results.spv",
            "Article 2.xlsx",
            "Frequency.xlsx",
            "Model Results.xlsx",
            "Regression New.xlsx",
            "Regression Results.xlsx",
            "Correlation.png",
            "Model MAIA.jpg",
            "Model Main.jpg",
            "Model SCS.jpg",
            "semPlot.png"
        ]
        for rf in remaining_analysis_items:
            safe_move(os.path.join(data_analysis_dir, rf), os.path.join(SUBFOLDERS["deliverables"], rf))
        
        # Check if any remaining files in Data Analysis
        remaining = os.listdir(data_analysis_dir)
        if remaining:
            print(f"Remaining in Data Analysis: {remaining}")
            for r in remaining:
                safe_move(os.path.join(data_analysis_dir, r), os.path.join(SUBFOLDERS["deliverables"], r))
        
        try:
            os.rmdir(data_analysis_dir)
            print("Removed empty Data Analysis directory")
        except Exception as e:
            print(f"Could not remove Data Analysis dir: {e}")

    # Deliverables from Article 2 folder
    article2_dir = os.path.join(ROOT_DIR, "Article 2")
    if os.path.exists(article2_dir):
        for a2f in os.listdir(article2_dir):
            safe_move(os.path.join(article2_dir, a2f), os.path.join(SUBFOLDERS["deliverables"], a2f))
        try:
            os.rmdir(article2_dir)
            print("Removed empty Article 2 directory")
        except Exception as e:
            print(f"Could not remove Article 2 dir: {e}")

    # Drafts archive from root
    drafts_root = [
        "Article (New).docx",
        "Article 2.docx",
        "FINALJALALIword-.docx",
        "FINALJALALIword-.gdoc",
        "Main Ducument- jalali zahra.docx",
        "Ms Jalali-new - Copy.docx",
        "Thesis-04-02-24.docx",
        "Thesis.docx",
        "سه فصل در حال ویرایش (1).pdf",
        "سه فصل در حال ویرایش.pdf",
        "ویرایش نهایی-جلالی زهرا.docx",
        "پایان نامه-جلالی.docx",
        "پایان_نامه_جلالی_ویرایش_رفرنس_ها_3.docx"
    ]
    for df in drafts_root:
        safe_move(os.path.join(ROOT_DIR, df), os.path.join(SUBFOLDERS["drafts_archive"], df))

    # 4. 04_references_and_lit
    ref_root = [
        "Zahra Jalali References.enl",
        "Zahra Jalali References.Data"
    ]
    for rf in ref_root:
        safe_move(os.path.join(ROOT_DIR, rf), os.path.join(SUBFOLDERS["references"], rf))

    # 5. Save reorganize_manifest.json
    manifest_path = os.path.join(ROOT_DIR, "reorganize_manifest.json")
    manifest_data = {
        "project_name": "Zahra Jalali",
        "timestamp": datetime.now().isoformat(),
        "total_records": len(manifest_records),
        "records": manifest_records
    }
    with open(manifest_path, "w", encoding="utf-8") as mf:
        json.dump(manifest_data, mf, ensure_ascii=False, indent=2)
    print(f"Created manifest with {len(manifest_records)} records at: {manifest_path}")

    # 6. Update project_meta.json
    meta_path = os.path.join(ROOT_DIR, "project_meta.json")
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                meta = json.load(f)
        except Exception:
            meta = {}
    else:
        meta = {}

    meta.update({
        "project_name": "Zahra Jalali",
        "reorganized_at": datetime.now().isoformat(),
        "taxonomy": "4-tier-standard",
        "subfolders": [
            "01_raw_inputs",
            "02_analysis_code",
            "03_deliverables",
            "04_references_and_lit"
        ]
    })
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print("Updated project_meta.json successfully.")

if __name__ == "__main__":
    main()
