#!/usr/bin/env python3
"""
consolidate_client_umbrella.py
------------------------------
Consolidates all projects and folders for repeat VIP client 'Şəhram Əmiri'
into a unified Master Client Umbrella architecture under Google Drive 'My Work'.
Generates:
  1. Master Umbrella Directory with standard 4-tier subprojects (P01, P02, P03...).
  2. 00_general_communications/ with unified chat transcripts and dossiers.
  3. master_projects_index.json cataloging all 40+ historical and active projects.
  4. CLIENT_LEDGER.xlsx multi-sheet tracking and accounting workbook.
  5. client_profile.md executive VIP dossier.
  6. project_meta.json master umbrella metadata.
"""

import os
import sys
import json
import shutil
import glob
from datetime import datetime
import pandas as pd

MY_WORK = "/Users/saber/Library/CloudStorage/GoogleDrive-ghaderi.sabir@gmail.com/My Drive/My Work"
MY_DRIVE = "/Users/saber/Library/CloudStorage/GoogleDrive-ghaderi.sabir@gmail.com/My Drive"
PENDING = os.path.join(MY_DRIVE, "Pending Works")
FINISHED = os.path.join(MY_DRIVE, "Finished Works")

UMBRELLA_DIR = os.path.join(MY_WORK, "Şəhram Əmiri")
CURRENT_PROJECT = os.path.join(MY_WORK, "Shahram Amiri Soldiers Data")
CASE_STUDY_DIR = os.path.join(MY_WORK, "Shahram Case Study 1")
REFS_DIR = os.path.join(MY_WORK, "Shahram Article References")

CLIENT_NAME = "Şəhram Əmiri"
CLIENT_FA = "شهرام امیری"
CLIENT_ID = 5819750724
PHONE = "989165535654"

def scan_all_shahram_projects():
    """Scan Pending, My Work, and Finished for all projects matching Shahram/Amiri."""
    locations = [
        ("My Work", MY_WORK),
        ("Pending Works", PENDING),
        ("Finished Works", FINISHED)
    ]
    catalog = []
    for loc_name, loc_path in locations:
        if not os.path.exists(loc_path):
            continue
        for item in sorted(os.listdir(loc_path)):
            if any(k in item.lower() for k in ["shahram", "şəhram"]) and "hamid" not in item.lower():
                full_p = os.path.join(loc_path, item)
                if os.path.isdir(full_p):
                    # Count files
                    try:
                        f_count = len([f for f in os.listdir(full_p) if not f.startswith(".")])
                    except Exception:
                        f_count = 0
                    
                    # Detect research type
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
                    if item == "Shahram Amiri Soldiers Data":
                        status = "Completed & Verified (نهایی‌شده با پیش‌فرض‌ها)"

                    catalog.append({
                        "Project Name": item,
                        "Lifecycle Location": loc_name,
                        "Research Type": p_type,
                        "File Count": f_count,
                        "Status": status,
                        "Path": full_p
                    })
    return catalog

def setup_umbrella_directory(catalog):
    """Build the physical 4-tier subprojects and master structure."""
    os.makedirs(UMBRELLA_DIR, exist_ok=True)

    # 1. 00_general_communications
    comm_dir = os.path.join(UMBRELLA_DIR, "00_general_communications")
    os.makedirs(comm_dir, exist_ok=True)
    
    # Copy transcripts and history from current project
    src_hist = os.path.join(CURRENT_PROJECT, "01_raw_inputs", "chat_history.json")
    src_trans = os.path.join(CURRENT_PROJECT, "01_raw_inputs", "chat_transcript.md")
    src_prof = os.path.join(CURRENT_PROJECT, "01_raw_inputs", "client_profile.md")
    
    if os.path.exists(src_hist):
        shutil.copy2(src_hist, os.path.join(comm_dir, "chat_history.json"))
    if os.path.exists(src_trans):
        shutil.copy2(src_trans, os.path.join(comm_dir, "chat_transcript.md"))
    if os.path.exists(src_prof):
        shutil.copy2(src_prof, os.path.join(comm_dir, "client_profile.md"))
    print("[+] Initialized 00_general_communications/")

    # 2. Subproject P01: Soldiers Variance Data
    p01_dir = os.path.join(UMBRELLA_DIR, "P01_Soldiers_Variance_Data")
    for sub in ["01_raw_inputs", "02_analysis_code", "03_deliverables", "03_deliverables/drafts_archive", "04_references_and_lit"]:
        os.makedirs(os.path.join(p01_dir, sub), exist_ok=True)
    
    # Copy key artifacts into P01
    shutil.copy2(os.path.join(CURRENT_PROJECT, "soldiers_variance_dataset.sav"), os.path.join(p01_dir, "03_deliverables", "soldiers_variance_dataset.sav"))
    shutil.copy2(os.path.join(CURRENT_PROJECT, "soldiers_variance_dataset.xlsx"), os.path.join(p01_dir, "03_deliverables", "soldiers_variance_dataset.xlsx"))
    shutil.copy2(os.path.join(CURRENT_PROJECT, "DATASET_VERIFICATION_REPORT.md"), os.path.join(p01_dir, "03_deliverables", "DATASET_VERIFICATION_REPORT.md"))
    shutil.copy2(os.path.join(CURRENT_PROJECT, "soldiers_variance_analysis.sps"), os.path.join(p01_dir, "02_analysis_code", "soldiers_variance_analysis.sps"))
    shutil.copy2(os.path.join(CURRENT_PROJECT, "scripts", "generate_soldiers_dataset.py"), os.path.join(p01_dir, "02_analysis_code", "generate_soldiers_dataset.py"))
    if os.path.exists(os.path.join(CURRENT_PROJECT, "01_raw_inputs", "Output3.spv")):
        shutil.copy2(os.path.join(CURRENT_PROJECT, "01_raw_inputs", "Output3.spv"), os.path.join(p01_dir, "01_raw_inputs", "Output3.spv"))
    
    # P01 metadata
    p01_meta = {
        "subproject_id": "P01",
        "title_fa": "تحلیل واریانس چندمتغیره داده‌های سربازان سالم و خودجرحی",
        "title_en": "Multivariate Analysis of Variance of Healthy vs. Self-Harm Soldiers",
        "status": "done",
        "sample_size": {"total": 495, "healthy": 297, "self_harm": 198},
        "deliverables": [
            "03_deliverables/soldiers_variance_dataset.sav",
            "03_deliverables/soldiers_variance_dataset.xlsx",
            "03_deliverables/DATASET_VERIFICATION_REPORT.md",
            "02_analysis_code/soldiers_variance_analysis.sps"
        ],
        "created_at": "2026-09-02T15:59:00",
        "completed_at": datetime.now().isoformat()
    }
    with open(os.path.join(p01_dir, "project_meta.json"), "w", encoding="utf-8") as f:
        json.dump(p01_meta, f, ensure_ascii=False, indent=2)
    print("[+] Provisioned P01_Soldiers_Variance_Data/")

    # 3. Subproject P02: Case Study 1
    p02_dir = os.path.join(UMBRELLA_DIR, "P02_Case_Study_1")
    for sub in ["01_raw_inputs", "02_analysis_code", "03_deliverables", "04_references_and_lit"]:
        os.makedirs(os.path.join(p02_dir, sub), exist_ok=True)
    if os.path.exists(CASE_STUDY_DIR):
        for it in os.listdir(CASE_STUDY_DIR):
            src = os.path.join(CASE_STUDY_DIR, it)
            if os.path.isfile(src):
                if it.endswith(".xlsx") or "report" in it.lower():
                    shutil.copy2(src, os.path.join(p02_dir, "03_deliverables", it))
                elif it.endswith(".ipynb") or it.endswith(".py"):
                    shutil.copy2(src, os.path.join(p02_dir, "02_analysis_code", it))
                else:
                    shutil.copy2(src, os.path.join(p02_dir, "01_raw_inputs", it))
            elif os.path.isdir(src) and it == "sced_plots":
                shutil.copytree(src, os.path.join(p02_dir, "03_deliverables", "sced_plots"), dirs_exist_ok=True)
    p02_meta = {
        "subproject_id": "P02",
        "title_fa": "تحلیل طرح‌های تک‌آزمودنی و موردپژوهی بالینی (Case Study)",
        "status": "completed",
        "completed_at": "2026-09-05T12:00:00"
    }
    with open(os.path.join(p02_dir, "project_meta.json"), "w", encoding="utf-8") as f:
        json.dump(p02_meta, f, ensure_ascii=False, indent=2)
    print("[+] Provisioned P02_Case_Study_1/")

    # 4. Subproject P03: Article References
    p03_dir = os.path.join(UMBRELLA_DIR, "P03_Article_References")
    for sub in ["01_raw_inputs", "02_analysis_code", "03_deliverables", "04_references_and_lit"]:
        os.makedirs(os.path.join(p03_dir, sub), exist_ok=True)
    if os.path.exists(REFS_DIR):
        for it in os.listdir(REFS_DIR):
            src = os.path.join(REFS_DIR, it)
            if it.endswith(".docx") or it.endswith(".pdf"):
                shutil.copy2(src, os.path.join(p03_dir, "01_raw_inputs", it))
            elif it.endswith(".enl"):
                shutil.copy2(src, os.path.join(p03_dir, "04_references_and_lit", it))
            elif os.path.isdir(src) and it.endswith(".Data"):
                shutil.copytree(src, os.path.join(p03_dir, "04_references_and_lit", it), dirs_exist_ok=True)
    p03_meta = {
        "subproject_id": "P03",
        "title_fa": "استخراج کتاب‌شناختی و پایگاه EndNote منابع مقاله",
        "status": "completed",
        "completed_at": "2026-09-08T14:00:00"
    }
    with open(os.path.join(p03_dir, "project_meta.json"), "w", encoding="utf-8") as f:
        json.dump(p03_meta, f, ensure_ascii=False, indent=2)
    print("[+] Provisioned P03_Article_References/")

    # 5. Master Umbrella project_meta.json
    now_iso = datetime.now().isoformat()
    umbrella_meta = {
        "is_umbrella_client_folder": True,
        "client_name": CLIENT_NAME,
        "client_name_fa": CLIENT_FA,
        "telegram_id": CLIENT_ID,
        "phone": PHONE,
        "vip_tier": "tier_1_collaborator",
        "pricing_discount_percent": 15,
        "total_historical_projects": len(catalog),
        "active_subprojects": [
            {"id": "P01", "folder": "P01_Soldiers_Variance_Data", "status": "done", "title": "تحلیل واریانس داده‌های سربازان"},
            {"id": "P02", "folder": "P02_Case_Study_1", "status": "completed", "title": "موردپژوهی بالینی SCED"},
            {"id": "P03", "folder": "P03_Article_References", "status": "completed", "title": "استخراج منابع اندنوت"}
        ],
        "created_at": "2026-09-02T15:59:00",
        "updated_at": now_iso
    }
    with open(os.path.join(UMBRELLA_DIR, "project_meta.json"), "w", encoding="utf-8") as f:
        json.dump(umbrella_meta, f, ensure_ascii=False, indent=2)
    print("[+] Created Master Umbrella project_meta.json")

    # 6. Master Projects Index JSON
    index_file = os.path.join(UMBRELLA_DIR, "master_projects_index.json")
    with open(index_file, "w", encoding="utf-8") as f:
        json.dump({
            "client": {"name": CLIENT_NAME, "id": CLIENT_ID, "phone": PHONE},
            "total_count": len(catalog),
            "projects": catalog
        }, f, ensure_ascii=False, indent=2)
    print(f"[+] Wrote {index_file} ({len(catalog)} projects cataloged)")

    # 7. Master Excel Ledger
    ledger_path = os.path.join(UMBRELLA_DIR, "CLIENT_LEDGER.xlsx")
    df_cat = pd.DataFrame(catalog)
    
    with pd.ExcelWriter(ledger_path, engine="openpyxl") as writer:
        # Sheet 1: Active Projects
        df_active = df_cat[df_cat["Lifecycle Location"] == "My Work"]
        df_active.to_excel(writer, sheet_name="Active_Projects", index=False)
        
        # Sheet 2: Pending Projects
        df_pending = df_cat[df_cat["Lifecycle Location"] == "Pending Works"]
        df_pending.to_excel(writer, sheet_name="Pending_Projects", index=False)
        
        # Sheet 3: Finished Projects
        df_finished = df_cat[df_cat["Lifecycle Location"] == "Finished Works"]
        df_finished.to_excel(writer, sheet_name="Historical_Finished", index=False)
        
        # Sheet 4: Summary
        summary_df = pd.DataFrame([
            {"Metric": "نام کلاینت", "Value": f"{CLIENT_FA} ({CLIENT_NAME})"},
            {"Metric": "شناسه تلگرام", "Value": CLIENT_ID},
            {"Metric": "شماره تماس", "Value": f"+{PHONE}"},
            {"Metric": "سطح همکاری (VIP Tier)", "Value": "همکار دائمی و ارشد (Tier 1 Collaborator)"},
            {"Metric": "تخفیف ویژه همکار", "Value": "15%"},
            {"Metric": "تعداد کل پروژه‌ها در درایو", "Value": len(catalog)},
            {"Metric": "پروژه‌های فعال در پوشه تجمیعی (My Work)", "Value": len(df_active)},
            {"Metric": "پروژه‌های در انتظار بررسی (Pending Works)", "Value": len(df_pending)},
            {"Metric": "پروژه‌های نهایی‌شده قبلی (Finished Works)", "Value": len(df_finished)},
            {"Metric": "آخرین پروژه تکمیل‌شده", "Value": "P01_Soldiers_Variance_Data (N=495, MANOVA)"},
            {"Metric": "تاریخ آخرین به‌روزرسانی", "Value": datetime.now().strftime("%Y-%m-%d %H:%M")}
        ])
        summary_df.to_excel(writer, sheet_name="Client_Dossier_Summary", index=False)
    print(f"[+] Created {ledger_path}")

    # 8. Client Profile Markdown
    prof_md = os.path.join(UMBRELLA_DIR, "client_profile.md")
    with open(prof_md, "w", encoding="utf-8") as f:
        f.write(f"# شناسنامه جامع همکار VIP: {CLIENT_FA} ({CLIENT_NAME})\n\n")
        f.write(f"این سند مرجع مدیریت و نظارت بر کلیه پروژه‌ها، تعاملات تلگرام و سوابق مالی **{CLIENT_FA}** در سامانه اکادمیک سوئیت است.\n\n")
        f.write(f"### اطلاعات هویتی و ارتباطی:\n")
        f.write(f"- **نام کامل:** {CLIENT_FA} ({CLIENT_NAME})\n")
        f.write(f"- **شناسه عددی تلگرام:** `{CLIENT_ID}`\n")
        f.write(f"- **شماره تلفن:** `+{PHONE}`\n")
        f.write(f"- **رده کلاینت:** 🌟 **VIP Tier 1 Collaborator (همکار دائمی و سفارش‌دهنده پرتکرار)**\n")
        f.write(f"- **حفاظت در برابر نادیده‌گیری خودکار (Anti-Ignoral):** 🟢 **فعال (همیشه محافظت‌شده)**\n")
        f.write(f"- **تخفیف همکاری:** ۱۵ درصد روی کلیه پیش‌فاکتورها\n")
        f.write(f"- **پوشه چتر تجمیعی در درایو:** `My Work/Şəhram Əmiri/`\n\n")
        
        f.write(f"## ۱. زیرپروژه‌های فعال تحت پوشه چتر:\n\n")
        f.write(f"| شناسه | نام زیرپروژه | نوع پژوهش | حجم نمونه | وضعیت | مسیر فایل‌های نهایی |\n")
        f.write(f"| :---: | :--- | :--- | :---: | :---: | :--- |\n")
        f.write(f"| **P01** | `P01_Soldiers_Variance_Data` | شبیه‌سازی و مانوا (MANOVA) | ۴۹۵ نفر | 🟢 **تکمیل (Done)** | `03_deliverables/soldiers_variance_dataset.sav` |\n")
        f.write(f"| **P02** | `P02_Case_Study_1` | تحلیل بالینی SCED | نمونه انفرادی | 🟢 **تکمیل (Completed)** | `03_deliverables/sced_comprehensive_report.xlsx` |\n")
        f.write(f"| **P03** | `P03_Article_References` | استخراج منابع و EndNote | ۵۰+ منبع | 🟢 **تکمیل (Completed)** | `04_references_and_lit/` |\n\n")
        
        f.write(f"## ۲. آمار کل پروژه‌ها در گوگل درایو ({len(catalog)} پروژه شناسایی‌شده):\n\n")
        f.write(f"- **پروژه‌های جاری در پوشه کاری (My Work):** {len(df_active)} مورد\n")
        f.write(f"- **پروژه‌های در انتظار بررسی/پیشنهاد (Pending Works):** {len(df_pending)} مورد\n")
        f.write(f"- **پروژه‌های تحویل‌شده قبلی (Finished Works):** {len(df_finished)} مورد\n\n")
        
        f.write(f"### فهرست پروژه‌ها بر اساس وضعیت:\n\n")
        f.write(f"| رديف | نام پروژه در درایو | محل در درایو | نوع تحلیل آماری | تعداد فایل | وضعیت |\n")
        f.write(f"| :---: | :--- | :---: | :--- | :---: | :---: |\n")
        for i, row in enumerate(catalog, 1):
            f.write(f"| {i} | `{row['Project Name']}` | {row['Lifecycle Location']} | {row['Research Type']} | {row['File Count']} | {row['Status']} |\n")
    print(f"[+] Created {prof_md}")

def main():
    print("=" * 80)
    print("EXECUTING CLIENT UMBRELLA CONSOLIDATION FOR ŞƏHRAM ƏMİRI")
    print("=" * 80)
    cat = scan_all_shahram_projects()
    print(f"[+] Total Shahram Amiri projects discovered across Drive: {len(cat)}")
    setup_umbrella_directory(cat)
    print("=" * 80)
    print("CONSOLIDATION COMPLETED SUCCESSFULLY!")
    print(f"Master Umbrella Directory: {UMBRELLA_DIR}")
    print("=" * 80)

if __name__ == "__main__":
    main()
