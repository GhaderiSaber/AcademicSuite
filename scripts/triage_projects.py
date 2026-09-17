#!/usr/bin/env python3
"""
triage_projects.py — Academic Google Drive Project Lifecycle Triage CLI
------------------------------------------------------------------------
Scans client project directories in Google Drive / 'My Work', identifies
inactive projects (> 30 days without messages), and moves them to
'Pending Works/' (or 'Finished Works/' if marked done).
Also supports restoring archived projects back to active 'My Work/'.
"""

import os
import sys
import argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
SKILL_DIR = os.path.join(ROOT_DIR, ".agents/skills/digital-twin-academic-consultant/scripts")
if SKILL_DIR not in sys.path:
    sys.path.insert(0, SKILL_DIR)

from project_drive_manager import ProjectDriveManager, resolve_google_drive_work_dir

def parse_args():
    parser = argparse.ArgumentParser(
        description="Academic Google Drive 30-Day Project Lifecycle & Triage Manager"
    )
    parser.add_argument(
        "--days", "-d",
        type=int,
        default=30,
        help="Inactivity threshold in days (default: 30)"
    )
    parser.add_argument(
        "--execute", "-x",
        action="store_true",
        help="Execute moves (by default, runs in dry-run mode)"
    )
    parser.add_argument(
        "--restore", "-r",
        type=str,
        default=None,
        help="Restore a specific archived project folder back to active 'My Work/'"
    )
    parser.add_argument(
        "--work-dir", "-w",
        type=str,
        default=None,
        help="Custom operational workspace directory (overrides default)"
    )
    return parser.parse_args()

def main():
    args = parse_args()
    cfg = {}
    if args.work_dir:
        cfg["google_drive_work_dir"] = args.work_dir
    else:
        # Load local telethon_config.json if available
        cfg_file = os.path.join(SKILL_DIR, "telethon_config.json")
        if os.path.exists(cfg_file):
            import json
            try:
                with open(cfg_file, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
            except Exception:
                pass

    pdm = ProjectDriveManager(config=cfg)
    print("=" * 70)
    print("ACADEMIC DRIVE PROJECT LIFECYCLE TRIAGE")
    print(f"Operational Root: {pdm.work_dir}")
    print("=" * 70)

    # Manual restore mode
    if args.restore:
        target_name = args.restore.strip()
        print(f"[*] Searching for archived project matching '{target_name}'...")
        existing = pdm.find_existing_project_by_client(target_name)
        if not existing:
            # Check direct path in Pending Works
            cand = os.path.join(pdm.work_dir, "Pending Works", target_name)
            if os.path.isdir(cand):
                existing = cand

        if not existing:
            print(f"[-] Could not find project '{target_name}' in Pending or Finished Works.")
            sys.exit(1)

        print(f"[+] Found project: {existing}")
        restored_path, was_restored, days_dormant = pdm.restore_project_to_active(existing)
        if was_restored:
            print(f"[✓] Project successfully restored to active workspace:")
            print(f"    -> {restored_path} (was dormant for {days_dormant} days)")
        else:
            print(f"[-] Project was not moved (already active or move error): {restored_path}")
        return

    # Triage mode
    is_dry = not args.execute
    mode_str = "DRY RUN (Preview Only)" if is_dry else "EXECUTION (Moving Folders)"
    print(f"Mode:              {mode_str}")
    print(f"Inactivity Window: {args.days} days")
    print("-" * 70)

    report = pdm.triage_inactive_projects(inactivity_days=args.days, dry_run=is_dry)

    print(f"\n🟢 ACTIVE PROJECTS (Retained in My Work: {len(report['active_retained'])}):")
    for p in report["active_retained"]:
        print(f"  • {p['folder']} | Inactive: {p['days_inactive']}d ({p['last_date']}) | Status: {p['status']}")

    if report["pinned_exempt"]:
        print(f"\n⭐ EXEMPT / PINNED PROJECTS ({len(report['pinned_exempt'])}):")
        for p in report["pinned_exempt"]:
            print(f"  • {p['folder']} ({p['reason']})")

    print(f"\n📦 INACTIVE PROJECTS -> PENDING WORKS ({len(report['moved_to_pending'])}):")
    for p in report["moved_to_pending"]:
        print(f"  • {p['folder']} | Inactive: {p['days_inactive']}d ({p['last_date']}) | Status: {p['status']}")

    if report["moved_to_finished"]:
        print(f"\n🏁 COMPLETED PROJECTS -> FINISHED WORKS ({len(report['moved_to_finished'])}):")
        for p in report["moved_to_finished"]:
            print(f"  • {p['folder']} | Inactive: {p['days_inactive']}d ({p['last_date']}) | Status: {p['status']}")

    if report["errors"]:
        print(f"\n⚠️ ERRORS ENCOUNTERED ({len(report['errors'])}):")
        for err in report["errors"]:
            print(f"  • {err['folder']}: {err['error']}")

    print("\n" + "=" * 70)
    print(f"SUMMARY: {len(report['active_retained'])} active retained, "
          f"{len(report['moved_to_pending'])} -> Pending Works, "
          f"{len(report['moved_to_finished'])} -> Finished Works, "
          f"{len(report['pinned_exempt'])} exempt.")

    if is_dry and (report["moved_to_pending"] or report["moved_to_finished"]):
        print("\n💡 To execute this move, run:")
        print(f"   python3 scripts/triage_projects.py --execute --days {args.days}")
    elif not is_dry:
        print("\n✅ My Work folder has been cleaned up and active projects organized.")
    print("=" * 70)

if __name__ == "__main__":
    main()
