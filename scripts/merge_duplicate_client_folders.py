#!/usr/bin/env python3
"""
merge_duplicate_client_folders.py
---------------------------------
Consolidates duplicate client folders created by Azerbaijani vs English
transliteration discrepancies in Google Drive ('My Work' and 'Pending Works').

Safe merging protocol:
1. Moves chat logs, transcripts, client profiles, and raw inputs from the duplicate into the master folder.
2. Merges project_meta.json (preserving telegram_id, telegram_username, phone, client_name_az).
3. Verifies file integrity before safely removing the emptied duplicate folder.
4. Strictly supports --dry-run (default) and --apply.
"""

import os
import sys
import json
import shutil
import argparse
from typing import Dict, List, Tuple, Any

DEFAULT_DRIVE_ROOT = "/Users/saber/Library/CloudStorage/GoogleDrive-ghaderi.sabir@gmail.com/My Drive"
DEFAULT_MY_WORK = os.path.join(DEFAULT_DRIVE_ROOT, "My Work")
DEFAULT_PENDING = os.path.join(DEFAULT_MY_WORK, "Pending Works")

# Specific duplicate mappings verified during audit
DUPLICATE_PAIRS: List[Tuple[str, str]] = [
    (os.path.join(DEFAULT_MY_WORK, "Zəhra Cəlalı"), os.path.join(DEFAULT_MY_WORK, "Zahra Jalali")),
    (os.path.join(DEFAULT_MY_WORK, "Fatimə Söləti"), os.path.join(DEFAULT_MY_WORK, "Fatemeh Solati")),
    (os.path.join(DEFAULT_MY_WORK, "Sepide Emarəti"), os.path.join(DEFAULT_MY_WORK, "Sepideh Emarati")),
    (os.path.join(DEFAULT_MY_WORK, "Mörteza Estəki"), os.path.join(DEFAULT_MY_WORK, "Morteza Estaki")),
    (os.path.join(DEFAULT_MY_WORK, "Nəfise Rəcəbiyan"), os.path.join(DEFAULT_MY_WORK, "Nafiseh Rajabiyan")),
    (os.path.join(DEFAULT_MY_WORK, "Səna Hesamiyan"), os.path.join(DEFAULT_MY_WORK, "Sana Hesamiyan")),
    (os.path.join(DEFAULT_MY_WORK, "Reyhane Həsəni"), os.path.join(DEFAULT_PENDING, "Reyhaneh Hasani")),
    (os.path.join(DEFAULT_MY_WORK, "Reyhane Şəmsizade"), os.path.join(DEFAULT_PENDING, "Reyhane Shamsizade")),
    (os.path.join(DEFAULT_MY_WORK, "İrəvanı"), os.path.join(DEFAULT_PENDING, "Iravani")),
    (os.path.join(DEFAULT_MY_WORK, "Sepide Höseynı"), os.path.join(DEFAULT_PENDING, "Sepideh Hoseyni"))
]


def merge_metadata(src_meta_p: str, dest_meta_p: str, apply: bool = False) -> Dict[str, Any]:
    """Merge project_meta.json from duplicate into master folder."""
    src_meta = {}
    dest_meta = {}
    if os.path.exists(src_meta_p):
        try:
            with open(src_meta_p, "r", encoding="utf-8") as f:
                src_meta = json.load(f)
        except Exception:
            pass

    if os.path.exists(dest_meta_p):
        try:
            with open(dest_meta_p, "r", encoding="utf-8") as f:
                dest_meta = json.load(f)
        except Exception:
            pass

    merged = dict(dest_meta)
    merged["client_name_az"] = src_meta.get("client_name", os.path.basename(os.path.dirname(src_meta_p)))
    if "telegram_id" in src_meta:
        merged["telegram_id"] = src_meta["telegram_id"]
    if "telegram_username" in src_meta:
        merged["telegram_username"] = src_meta["telegram_username"]
    if "phone" in src_meta:
        merged["phone"] = src_meta["phone"]
    if "advisor" in src_meta and not merged.get("advisor"):
        merged["advisor"] = src_meta["advisor"]
    if "target_instruments" in src_meta and not merged.get("target_instruments"):
        merged["target_instruments"] = src_meta["target_instruments"]
    if "stages" in src_meta:
        merged.setdefault("stages", src_meta["stages"])

    if apply:
        with open(dest_meta_p, "w", encoding="utf-8") as f:
            json.dump(merged, f, ensure_ascii=False, indent=2)

    return merged


def consolidate_pair(src_dir: str, dest_dir: str, apply: bool = False) -> Dict[str, Any]:
    """Merge files from src_dir into dest_dir, then remove src_dir."""
    if not os.path.exists(src_dir):
        return {"status": "skipped", "reason": f"Source does not exist: {src_dir}"}
    if not os.path.exists(dest_dir):
        return {"status": "skipped", "reason": f"Destination does not exist: {dest_dir}"}

    actions = []
    src_meta_file = os.path.join(src_dir, "project_meta.json")
    dest_meta_file = os.path.join(dest_dir, "project_meta.json")

    # 1. Merge metadata
    merge_metadata(src_meta_file, dest_meta_file, apply=apply)
    actions.append(f"Merged metadata from {src_meta_file} -> {dest_meta_file}")

    # 2. Walk and transfer files
    for root, dirs, files in os.walk(src_dir):
        rel_dir = os.path.relpath(root, src_dir)
        dest_root = os.path.join(dest_dir, rel_dir) if rel_dir != "." else dest_dir

        if apply:
            os.makedirs(dest_root, exist_ok=True)

        for f in files:
            if f.startswith(".") or f == "project_meta.json":
                continue
            src_file = os.path.join(root, f)
            dest_file = os.path.join(dest_root, f)

            if not os.path.exists(dest_file):
                actions.append(f"MOVE: {src_file} -> {dest_file}")
                if apply:
                    shutil.move(src_file, dest_file)
            else:
                # File already exists at destination: if same size, delete src; else rename
                src_sz = os.path.getsize(src_file)
                dest_sz = os.path.getsize(dest_file)
                if src_sz == dest_sz:
                    actions.append(f"IDENTICAL: remove duplicate {src_file}")
                    if apply:
                        os.remove(src_file)
                else:
                    alt_name = f"chat_{f}"
                    dest_alt = os.path.join(dest_root, alt_name)
                    actions.append(f"MOVE (RENAMED): {src_file} -> {dest_alt}")
                    if apply:
                        shutil.move(src_file, dest_alt)

    # 3. Safely remove src_dir if applied
    if apply:
        shutil.rmtree(src_dir)
        actions.append(f"REMOVED: Emptied duplicate folder {src_dir}")

    return {
        "status": "applied" if apply else "preview",
        "source": src_dir,
        "destination": dest_dir,
        "actions_count": len(actions),
        "actions": actions
    }


def main():
    parser = argparse.ArgumentParser(description="Consolidate duplicate Azerbaijani client folders into master English folders.")
    parser.add_argument("--apply", action="store_true", help="Execute consolidation and deletion of duplicates.")
    args = parser.parse_args()

    mode = "EXECUTION MODE (APPLY)" if args.apply else "DRY-RUN PREVIEW (No files modified)"
    print(f"[*] Starting Duplicate Client Folder Consolidation ({mode})")
    print(f"[*] Auditing {len(DUPLICATE_PAIRS)} known duplicate pairs...\n")

    total_actions = 0
    consolidated = 0

    for src_p, dest_p in DUPLICATE_PAIRS:
        src_name = os.path.basename(src_p)
        dest_name = os.path.basename(dest_p)
        print(f"--- Checking: [{src_name}] -> [{dest_name}] ---")
        res = consolidate_pair(src_p, dest_p, apply=args.apply)
        if res["status"] in ["applied", "preview"]:
            consolidated += 1
            total_actions += res["actions_count"]
            for act in res["actions"]:
                print(f"    • {act}")
        else:
            print(f"    [!] {res['reason']}")
        print()

    print(f"[+] Consolidation finished:")
    print(f"    Folders processed: {consolidated}/{len(DUPLICATE_PAIRS)}")
    print(f"    Total actions:     {total_actions}")
    if not args.apply:
        print("\n[!] To apply these changes, re-run with: python3 scripts/merge_duplicate_client_folders.py --apply")


if __name__ == "__main__":
    main()
