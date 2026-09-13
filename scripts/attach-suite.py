#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
attach-suite — Cross-Platform Suite Linker for Google Antigravity & AI Agents
Supports macOS, Linux, and Windows 11.
Enables seamless domain isolation for projects in cloud-synced storage (Google Drive, Dropbox, iCloud)
without duplicating Git repositories, hitting customization token limits, or suffering .git/index.lock conflicts.
"""

import sys
import os
import shutil
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

IS_WINDOWS = sys.platform == "win32"

CONFIG_DIR = Path.home() / ".config" / "attach-suite"
CONFIG_FILE = CONFIG_DIR / "suites.json"

DEFAULT_SUITES = {
    "academic": {
        "name": "Academic Thesis & Statistical Consultancy Suite",
        "aliases": ["thesis", "saber", "academic_suite"],
        "path": str(Path.home() / "Desktop" / "academic_suite"),
        "description": "Digital Saber, 27 academic & statistical skills, APA 7, psychometrics"
    },
    "brokerage": {
        "name": "Freight Brokerage & Logistics Suite",
        "aliases": ["freight", "freight_brokerage", "broker"],
        "path": str(Path.home() / "Desktop" / "freight_brokerage"),
        "description": "Digital Broker, CMR manifests, freight orders, logistics workflows"
    },
    "epsilonstat": {
        "name": "EpsilonStat WebApp Suite",
        "aliases": ["webapp", "epsilon"],
        "path": str(Path.home() / "Desktop" / "EpsilonStat"),
        "description": "Full-stack React/Node statistical analysis web application"
    },
    "zarcloud": {
        "name": "ZarCloud Project Suite",
        "aliases": ["zar"],
        "path": str(Path.home() / "Desktop" / "ZarCloud"),
        "description": "Cloud services & financial pricing dashboard"
    },
    "duzen": {
        "name": "Duzen Workflow Suite",
        "aliases": [],
        "path": str(Path.home() / "Desktop" / "Duzen"),
        "description": "Automation and project organizer workflows"
    },
    "leveltrader": {
        "name": "LevelTrader Trading Suite",
        "aliases": ["trader"],
        "path": str(Path.home() / "Desktop" / "LevelTrader"),
        "description": "Algorithmic trading & market level analysis"
    }
}

# ANSI colors & UTF-8 output on Windows
if IS_WINDOWS:
    try:
        if hasattr(sys.stdout, "reconfigure"):
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "reconfigure"):
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        h_out = kernel32.GetStdHandle(-11)
        mode = ctypes.c_ulong()
        if kernel32.GetConsoleMode(h_out, ctypes.byref(mode)):
            kernel32.SetConsoleMode(h_out, mode.value | 0x0004)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
    except Exception:
        pass

RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
BLUE = "\033[34m"
CYAN = "\033[36m"
YELLOW = "\033[33m"
RED = "\033[31m"
GRAY = "\033[90m"


def load_suites():
    """Loads configured suites combining defaults and custom registrations."""
    suites = dict(DEFAULT_SUITES)
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                custom = json.load(f)
                suites.update(custom)
        except Exception as e:
            print(f"{YELLOW}Warning: Could not read {CONFIG_FILE}: {e}{RESET}", file=sys.stderr)
    return suites


def save_custom_suite(key, data):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    custom = {}
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                custom = json.load(f)
        except Exception:
            custom = {}
    custom[key] = data
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(custom, f, indent=2, ensure_ascii=False)


def resolve_suite(query, suites):
    """Resolves a suite name, alias, or path."""
    q = query.strip().lower()
    for key, info in suites.items():
        if key.lower() == q or q in [a.lower() for a in info.get("aliases", [])]:
            return key, info
    p = Path(query).expanduser().resolve()
    if p.exists() and (p / ".agents").exists():
        return p.name.lower(), {
            "name": p.name,
            "path": str(p),
            "description": f"Custom local suite at {p}"
        }
    return None, None


def is_link_path(p: Path) -> bool:
    """Checks whether a path is a symlink, directory junction, or reparse point."""
    if p is None:
        return False
    try:
        if p.is_symlink():
            return True
    except Exception:
        pass
    if IS_WINDOWS:
        try:
            st = os.lstat(str(p))
            FILE_ATTRIBUTE_REPARSE_POINT = 0x400
            if getattr(st, "st_file_attributes", 0) & FILE_ATTRIBUTE_REPARSE_POINT:
                return True
        except Exception:
            pass
        try:
            os.readlink(str(p))
            return True
        except Exception:
            pass
        try:
            return os.path.islink(str(p))
        except Exception:
            pass
    else:
        try:
            return os.path.islink(str(p))
        except Exception:
            pass
    return False


def is_attached_agents_md(p: Path) -> bool:
    """Checks if an AGENTS.md file was placed by a suite."""
    if not p.is_file():
        return False
    try:
        with open(p, "r", encoding="utf-8", errors="ignore") as f:
            header = f.read(500)
            return "AGENTS.md — " in header or "Digital Saber" in header or "Cognitive Architecture" in header or "Freight Brokerage" in header
    except Exception:
        return False




def create_dir_link(target: Path, link_path: Path) -> str:
    """
    Creates a directory symlink (macOS/Linux/Windows Developer Mode) or Directory Junction (Windows fallback).
    Returns link type: 'symlink', 'junction', or 'pointer'.
    """
    if is_link_path(link_path):
        remove_link(link_path)

    target_str = str(target.resolve())
    link_str = str(link_path.resolve())

    if IS_WINDOWS:
        # 1. Prioritize native Directory Symbolic Link (works with Windows Developer Mode enabled or Admin)
        try:
            os.symlink(target_str, link_str, target_is_directory=True)
            return "symlink"
        except OSError:
            pass

        # 2. Fallback to Directory Junction (mklink /J) if Developer Mode is off
        res = subprocess.run(["cmd", "/c", "mklink", "/J", link_str, target_str], capture_output=True, text=True)
        if res.returncode == 0:
            return "junction"

        # 3. Fallback to Antigravity Pointer Link for non-NTFS/virtual filesystems (Google Drive File Stream / FAT32)
        drive = link_path.drive or str(link_path)[:2]
        print(f"{YELLOW}Notice: Filesystem on '{drive}' does not support NTFS Symbolic Links or Junctions.{RESET}")
        print(f"{CYAN}Engaging Antigravity Pointer Link (linking via skills.json without copying files)...{RESET}")
        link_path.mkdir(parents=True, exist_ok=True)
        skills_json = link_path / "skills.json"
        target_skills = target / "skills" if (target / "skills").exists() else target
        with open(skills_json, "w", encoding="utf-8") as f:
            json.dump({"entries": [{"path": str(target_skills).replace("\\", "/")}]}, f, indent=2)
        return "pointer"
    else:
        try:
            os.symlink(target_str, link_str)
            return "symlink"
        except OSError as e:
            print(f"\n{RED}Error: Could not create symlink on this filesystem: {e}{RESET}\n", file=sys.stderr)
            sys.exit(1)


def create_file_link(target: Path, link_path: Path) -> str:
    """Creates a file symlink, hard link, or fallback copy."""
    if is_link_path(link_path) or link_path.exists():
        remove_link(link_path)

    target_str = str(target.resolve())
    link_str = str(link_path.resolve())

    # 1. Prioritize native File Symbolic Link (works on Windows with Developer Mode and on POSIX)
    try:
        os.symlink(target_str, link_str)
        return "symlink"
    except OSError:
        pass

    if IS_WINDOWS:
        # 2. Fallback to NTFS hard link (mklink /H) if Developer Mode is off
        res = subprocess.run(["cmd", "/c", "mklink", "/H", link_str, target_str], capture_output=True, text=True)
        if res.returncode == 0:
            return "hardlink"
        # 3. Cross-volume / FAT32 fallback: copy file
        shutil.copy2(target, link_path)
        return "file"
    else:
        shutil.copy2(target, link_path)
        return "file"


def remove_link(link_path: Path, allow_delete_dir: bool = False):
    """Safely removes a symlink, directory junction, or pointer without deleting target contents."""
    if not link_path.exists() and not is_link_path(link_path):
        return

    if is_link_path(link_path):
        if IS_WINDOWS:
            is_dir = False
            try:
                st = os.lstat(str(link_path))
                FILE_ATTRIBUTE_DIRECTORY = 0x10
                if getattr(st, "st_file_attributes", 0) & FILE_ATTRIBUTE_DIRECTORY:
                    is_dir = True
            except Exception:
                is_dir = link_path.is_dir()

            if is_dir:
                try:
                    os.rmdir(link_path)
                except OSError:
                    subprocess.run(["cmd", "/c", "rmdir", str(link_path)], capture_output=True)
            else:
                try:
                    link_path.unlink()
                except OSError:
                    subprocess.run(["cmd", "/c", "del", "/f", "/q", str(link_path)], capture_output=True)
        else:
            link_path.unlink()
    elif allow_delete_dir:
        if link_path.is_dir():
            shutil.rmtree(link_path)
        else:
            link_path.unlink()
    elif link_path.is_file():
        link_path.unlink()


def read_link_target(p: Path):
    """Safely reads the target of a link or junction."""
    try:
        t = os.readlink(p)
        if t and t.startswith("\\\\?\\"):
            t = t[4:]
        return t
    except Exception:
        return None


def is_foreign_os_link(target_str: str) -> bool:
    """Detects if a link target was created on a different OS (e.g. Mac path on Windows)."""
    if not target_str:
        return False
    clean = target_str[4:] if target_str.startswith("\\\\?\\") else target_str
    if IS_WINDOWS:
        # On Windows, if link starts with /Users/ or /home/, it's from Mac/Linux
        return clean.startswith("/Users/") or clean.startswith("/home/")
    else:
        # On Mac/Linux, if link starts with C:\ or G:\, it's from Windows
        return len(clean) > 2 and clean[1] == ":"


def get_attached_suite_path(target_dir: Path):
    """Returns the resolved Path of the currently attached suite on the CURRENT OS."""
    meta_file = target_dir / ".attached_suite.json"
    if meta_file.exists():
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                info = json.load(f)
                suite_name = info.get("suite")
                if suite_name:
                    suites = load_suites()
                    _, resolved = resolve_suite(suite_name, suites)
                    if resolved:
                        p = Path(resolved["path"]).resolve()
                        if p.exists():
                            return p
        except Exception:
            pass

    # Fallback to .agents link target if valid on current OS
    agents_link = target_dir / ".agents"
    if is_link_path(agents_link):
        target_str = read_link_target(agents_link)
        if target_str and not is_foreign_os_link(target_str):
            target = Path(target_str).resolve()
            if target.name == ".agents":
                return target.parent
            return target
    return None


def clean_conflicts_and_locks(target_dir: Path):
    """Cleans up Google Drive duplicate conflict files and orphaned locks."""
    cleaned = []
    # Clean .git/index.lock if orphaned
    lock_file = target_dir / ".git" / "index.lock"
    if lock_file.exists():
        try:
            lock_file.unlink()
            cleaned.append(".git/index.lock (orphaned)")
        except Exception as e:
            print(f"{YELLOW}Could not remove lock file: {e}{RESET}")

    # Clean ' 2' conflict files
    for item in target_dir.rglob("* 2.*"):
        if "03_deliverables" in str(item) or "01_raw_inputs" in str(item):
            continue
        if item.is_file():
            try:
                item.unlink()
                cleaned.append(str(item.relative_to(target_dir)))
            except Exception:
                pass

    for d in target_dir.rglob("* 2"):
        if "03_deliverables" in str(d) or "01_raw_inputs" in str(d):
            continue
        if d.is_dir() and not is_link_path(d):
            try:
                shutil.rmtree(d)
                cleaned.append(str(d.relative_to(target_dir)))
            except Exception:
                pass

    return cleaned


def get_status(target_dir: Path):
    """Inspects the current working directory for attached suites."""
    meta_file = target_dir / ".attached_suite.json"
    agents_link = target_dir / ".agents"
    agents_md = target_dir / "AGENTS.md"
    git_dir = target_dir / ".git"

    attached_info = None
    if meta_file.exists():
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                attached_info = json.load(f)
        except Exception:
            pass

    agents_is_link = is_link_path(agents_link)
    agents_target = read_link_target(agents_link) if agents_is_link else None
    agents_foreign = is_foreign_os_link(agents_target) if agents_target else False

    return {
        "has_meta": meta_file.exists(),
        "meta": attached_info,
        "agents_is_link": agents_is_link,
        "agents_target": agents_target,
        "agents_foreign": agents_foreign,
        "agents_exists": agents_link.exists(),
        "agents_md_is_link": is_link_path(agents_md),
        "agents_md_target": read_link_target(agents_md) if is_link_path(agents_md) else None,
        "has_local_git": git_dir.exists(),
        "is_git_link": is_link_path(git_dir),
    }


def cmd_list(args):
    suites = load_suites()
    current_os = "Windows 11" if IS_WINDOWS else "macOS / POSIX"
    print(f"\n{BOLD}{CYAN}Available Domain Suites on {current_os}:{RESET}")
    print("=" * 65)
    for key, info in sorted(suites.items()):
        p = Path(info["path"])
        exists = p.exists()
        status_color = GREEN if exists else RED
        status_text = "Ready" if exists else "Path Not Found"
        aliases = f" (aliases: {', '.join(info.get('aliases', []))})" if info.get("aliases") else ""

        print(f"{BOLD}{BLUE}{key}{RESET}{aliases}")
        print(f"  {BOLD}Name:{RESET}        {info['name']}")
        print(f"  {BOLD}Path:{RESET}        {info['path']} [{status_color}{status_text}{RESET}]")
        print(f"  {BOLD}Description:{RESET} {info.get('description', 'N/A')}")
        if exists and (p / ".agents" / "skills").exists():
            skills = [s.name for s in (p / ".agents" / "skills").iterdir() if s.is_dir()]
            print(f"  {BOLD}Skills ({len(skills)}):{RESET}   {GRAY}{', '.join(skills[:8])}{'...' if len(skills) > 8 else ''}{RESET}")
        print("-" * 65)
    print()


def cmd_status(args):
    target_path = getattr(args, "path", ".") or "."
    cwd = Path(target_path).resolve()
    status = get_status(cwd)
    suite_path = get_attached_suite_path(cwd)
    current_os = "Windows 11" if IS_WINDOWS else "macOS"

    print(f"\n{BOLD}{CYAN}Suite Attachment Status ({current_os}):{RESET} {cwd}")
    print("=" * 65)

    if status["meta"]:
        print(f"  {BOLD}Attached Suite:{RESET}   {GREEN}{status['meta'].get('suite', 'Unknown')}{RESET}")
        print(f"  {BOLD}Suite Title:{RESET}      {status['meta'].get('name', 'Unknown')}")
        if suite_path:
            print(f"  {BOLD}Local Path:{RESET}       {GREEN}{suite_path}{RESET}")
        else:
            print(f"  {BOLD}Recorded Path:{RESET}    {YELLOW}{status['meta'].get('path', 'Unknown')}{RESET}")
    else:
        print(f"  {BOLD}Attached Suite:{RESET}   {YELLOW}None recorded in .attached_suite.json{RESET}")

    # Check .agents
    if status["agents_is_link"]:
        target = status["agents_target"]
        if status["agents_foreign"]:
            print(f"  {BOLD}.agents:{RESET}          {YELLOW}Link created on another OS ({target}){RESET}")
            print(f"  {BOLD}Cross-OS Fix:{RESET}     {CYAN}Run 'attach-suite fix' to re-link on this OS{RESET}")
        else:
            valid = Path(target).exists() if target else False
            color = GREEN if valid else RED
            link_type = "Symlink" if (cwd / ".agents").is_symlink() else ("Junction" if IS_WINDOWS else "Symlink")
            print(f"  {BOLD}.agents:{RESET}          {CYAN}{link_type} --> {target}{RESET} [{color}{'Valid' if valid else 'Broken'}{RESET}]")
    elif status["agents_exists"]:
        print(f"  {BOLD}.agents:{RESET}          {YELLOW}Physical Directory (Not a link){RESET}")
    else:
        print(f"  {BOLD}.agents:{RESET}          {GRAY}Not present{RESET}")

    # Check AGENTS.md
    if status["agents_md_is_link"]:
        md_type = "Symlink" if (cwd / "AGENTS.md").is_symlink() else "Link"
        print(f"  {BOLD}AGENTS.md:{RESET}        {CYAN}{md_type} --> {status['agents_md_target']}{RESET}")
    elif (cwd / "AGENTS.md").exists():
        print(f"  {BOLD}AGENTS.md:{RESET}        {YELLOW}Physical File{RESET}")
    else:
        print(f"  {BOLD}AGENTS.md:{RESET}        {GRAY}Not present{RESET}")

    # Check .git
    if status["has_local_git"]:
        print(f"  {BOLD}.git Directory:{RESET}   {YELLOW}Present in working directory (May cause Google Drive lock issues){RESET}")
    else:
        print(f"  {BOLD}.git Directory:{RESET}   {GREEN}None in cloud folder (Clean! Immune to sync locks){RESET}")

    # Check Git status on the master suite if attached
    if suite_path and (suite_path / ".git").exists():
        try:
            res = subprocess.run(
                ["git", "-C", str(suite_path), "status", "-s"],
                capture_output=True, text=True, check=True
            )
            changes = res.stdout.strip()
            if changes:
                lines = changes.splitlines()
                print(f"  {BOLD}Suite Git Status:{RESET} {YELLOW}{len(lines)} uncommitted change(s) in master suite{RESET}")
            else:
                print(f"  {BOLD}Suite Git Status:{RESET} {GREEN}Clean, master repository is up to date{RESET}")
        except Exception:
            pass

    print("=" * 65 + "\n")


def cmd_fix(args):
    """Automatically repairs cross-OS links (e.g. Mac path on Windows or Windows path on Mac)."""
    cwd = Path.cwd()
    meta_file = cwd / ".attached_suite.json"
    if not meta_file.exists():
        print(f"{YELLOW}No attached suite metadata (.attached_suite.json) found in current directory.{RESET}")
        return

    try:
        with open(meta_file, "r", encoding="utf-8") as f:
            info = json.load(f)
            suite_name = info.get("suite")
    except Exception as e:
        print(f"{RED}Error reading metadata: {e}{RESET}")
        return

    print(f"\n{BOLD}{CYAN}Repairing cross-OS link for suite '{suite_name}' on {('Windows 11' if IS_WINDOWS else 'macOS')}...{RESET}")
    # Call attach for this suite
    args.suite = suite_name
    args.keep_git = False
    cmd_attach(args)


def cmd_detach(args):
    target_path = getattr(args, "path", ".") or "."
    cwd = Path(target_path).resolve()
    print(f"\n{BOLD}Detaching suite from:{RESET} {cwd}")

    # Safety check: Never detach the master suite from inside its own root repository!
    suites = load_suites()
    for key, info in suites.items():
        try:
            if Path(info["path"]).resolve() == cwd:
                print(f"\n{RED}Error: Current directory is the master suite '{key}'.{RESET}")
                print(f"{YELLOW}Cannot detach the master suite repository itself.{RESET}\n")
                return
        except Exception:
            pass

    meta_file = cwd / ".attached_suite.json"
    has_meta = meta_file.exists()

    removed = []

    # 1. Detach .agents
    agents_dir = cwd / ".agents"
    if is_link_path(agents_dir):
        remove_link(agents_dir)
        removed.append(".agents (link)")
    elif agents_dir.exists() and (has_meta or (agents_dir / "skills.json").exists()):
        try:
            shutil.rmtree(agents_dir)
            removed.append(".agents (pointer directory)")
        except Exception as e:
            print(f"{YELLOW}Could not remove .agents directory: {e}{RESET}")

    # Restore pre-attach backup if one exists
    backup_agents = cwd / ".agents_backup_pre_attach"
    if backup_agents.exists() and not (cwd / ".agents").exists():
        try:
            backup_agents.rename(cwd / ".agents")
            removed.append("restored original .agents from backup")
        except Exception as e:
            print(f"{YELLOW}Could not restore backup .agents: {e}{RESET}")

    # 2. Detach AGENTS.md
    agents_md = cwd / "AGENTS.md"
    if is_link_path(agents_md):
        remove_link(agents_md)
        removed.append("AGENTS.md (link)")
    elif agents_md.exists() and (has_meta or is_attached_agents_md(agents_md)):
        try:
            agents_md.unlink()
            removed.append("AGENTS.md")
        except Exception as e:
            print(f"{YELLOW}Could not remove AGENTS.md: {e}{RESET}")

    # 3. Detach scripts if linked
    scripts_dir = cwd / "scripts"
    if is_link_path(scripts_dir):
        remove_link(scripts_dir, allow_delete_dir=True)
        removed.append("scripts/ (link)")

    # 4. Detach launcher files
    for item_name in ["digital_saber.py", "digital_broker.py"]:
        p = cwd / item_name
        if is_link_path(p):
            remove_link(p)
            removed.append(f"{item_name} (link)")
        elif p.exists() and has_meta:
            try:
                p.unlink()
                removed.append(item_name)
            except Exception:
                pass

    # 5. Remove metadata file
    if meta_file.exists():
        try:
            meta_file.unlink()
            removed.append(".attached_suite.json")
        except Exception as e:
            print(f"{YELLOW}Could not remove metadata file: {e}{RESET}")

    if removed:
        print(f"\n{GREEN}✓ Successfully detached suite:{RESET}")
        for r in removed:
            print(f"   - {r}")
    else:
        print(f"\n{YELLOW}No active suite links or attached metadata found to detach in: {cwd}{RESET}")
    print()


def cmd_clean(args):
    cwd = Path.cwd()
    print(f"\n{BOLD}Scanning for Google Drive conflict files and stale locks in:{RESET} {cwd}")
    cleaned = clean_conflicts_and_locks(cwd)
    if cleaned:
        print(f"{GREEN}✓ Cleaned {len(cleaned)} conflicting items:{RESET}")
        for item in cleaned:
            print(f"   - {item}")
    else:
        print(f"{GREEN}✓ Directory is clean. No orphaned locks or conflict duplicates found.{RESET}")
    print()


def cmd_attach(args):
    cwd = Path.cwd()
    suites = load_suites()
    suite_key, suite_info = resolve_suite(args.suite, suites)

    if not suite_info:
        print(f"\n{RED}Error: Unknown suite '{args.suite}'.{RESET}")
        print(f"Run {BOLD}attach-suite list{RESET} to see all available suites.\n")
        sys.exit(1)

    suite_path = Path(suite_info["path"]).resolve()
    if not suite_path.exists():
        print(f"\n{RED}Error: Suite directory does not exist on this machine:{RESET} {suite_path}")
        if IS_WINDOWS:
            print(f"{YELLOW}Tip: On Windows 11, please clone {suite_key} to:{RESET} {suite_path}")
        else:
            print(f"{YELLOW}Tip: Please clone or pull {suite_key} to:{RESET} {suite_path}")
        print()
        sys.exit(1)

    agents_src = suite_path / ".agents"
    if not agents_src.exists():
        print(f"\n{RED}Error: Suite does not contain a .agents directory:{RESET} {agents_src}\n")
        sys.exit(1)

    current_os = "Windows 11" if IS_WINDOWS else "macOS"
    print(f"\n{BOLD}{CYAN}Attaching Suite ({current_os}):{RESET} {BOLD}{suite_info['name']}{RESET}")
    print(f"  Source:  {suite_path}")
    print(f"  Target:  {cwd}\n")

    # Step 1: Clean conflicts and stale locks
    cleaned = clean_conflicts_and_locks(cwd)
    if cleaned:
        print(f"{GRAY}Cleaned {len(cleaned)} stale lock/conflict items.{RESET}")

    # Step 2: Handle redundant .git in project folder if it points to the suite repo
    git_dir = cwd / ".git"
    if git_dir.exists() and not is_link_path(git_dir):
        if not getattr(args, 'keep_git', False):
            print(f"{YELLOW}Notice: Found local .git directory in Google Drive folder.{RESET}")
            print(f"{YELLOW}Removing local .git so Google Drive will never lock Git files...{RESET}")
            try:
                shutil.rmtree(git_dir)
                print(f"{GREEN}✓ Removed redundant .git (master repository remains safe at {suite_path}){RESET}")
            except Exception as e:
                print(f"{RED}Could not remove .git: {e}{RESET}")

    # Step 3: Handle existing .agents
    existing_agents = cwd / ".agents"
    if is_link_path(existing_agents):
        remove_link(existing_agents)
    elif existing_agents.is_dir():
        backup_dir = cwd / ".agents_backup_pre_attach"
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        print(f"{YELLOW}Moving physical .agents folder to {backup_dir.name}...{RESET}")
        existing_agents.rename(backup_dir)

    existing_agents_md = cwd / "AGENTS.md"
    if is_link_path(existing_agents_md) or existing_agents_md.exists():
        remove_link(existing_agents_md)

    # Step 4: Create Links
    link_type = create_dir_link(agents_src, existing_agents)
    link_label = "Symbolic Link" if link_type == "symlink" else ("Directory Junction" if link_type == "junction" else "Pointer Link")
    print(f"{GREEN}✓ Attached .agents ({link_label}) --> {agents_src}{RESET}")

    agents_md_src = suite_path / "AGENTS.md"
    if agents_md_src.exists():
        file_type = create_file_link(agents_md_src, existing_agents_md)
        file_label = "Symbolic Link" if file_type == "symlink" else ("Hard Link" if file_type == "hardlink" else "File Copy")
        print(f"{GREEN}✓ Attached AGENTS.md ({file_label}) --> {agents_md_src}{RESET}")

    # Optionally link scripts
    scripts_src = suite_path / "scripts"
    scripts_dest = cwd / "scripts"
    if scripts_src.exists():
        if is_link_path(scripts_dest):
            remove_link(scripts_dest, allow_delete_dir=True)
            scripts_type = create_dir_link(scripts_src, scripts_dest)
            scripts_label = "Symbolic Link" if scripts_type == "symlink" else ("Directory Junction" if scripts_type == "junction" else "Pointer Link")
            print(f"{GREEN}✓ Attached scripts/ ({scripts_label}) --> {scripts_src}{RESET}")
        elif not scripts_dest.exists():
            scripts_type = create_dir_link(scripts_src, scripts_dest)
            scripts_label = "Symbolic Link" if scripts_type == "symlink" else ("Directory Junction" if scripts_type == "junction" else "Pointer Link")
            print(f"{GREEN}✓ Attached scripts/ ({scripts_label}) --> {scripts_src}{RESET}")

    # Save attachment metadata
    meta = {
        "suite": suite_key,
        "name": suite_info["name"],
        "path": str(suite_path),
        "attached_at": datetime.now().isoformat(),
        "attached_os": current_os,
        "link_type": link_type
    }
    with open(cwd / ".attached_suite.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    # Count active skills
    skills = [s.name for s in (agents_src / "skills").iterdir() if s.is_dir()] if (agents_src / "skills").exists() else []

    print(f"\n{BOLD}{GREEN}Successfully attached {suite_key} on {current_os}!{RESET}")
    print(f"Antigravity will now automatically load {len(skills)} {suite_key} skills:")
    print(f"{GRAY}{', '.join(skills[:12])}{'...' if len(skills) > 12 else ''}{RESET}")
    print(f"\n{BOLD}Result:{RESET} Zero Google Drive Git locks. Zero cross-domain token pollution.\n")


def cmd_git_passthrough(args, unknown_args):
    """Runs any arbitrary git command against the master suite repo from current directory."""
    cwd = Path.cwd()
    suite_path = get_attached_suite_path(cwd)
    if not suite_path:
        print(f"{RED}Error: No suite is attached to the current directory.{RESET}", file=sys.stderr)
        sys.exit(1)

    cmd = ["git", "-C", str(suite_path)] + unknown_args
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)


def cmd_push(args):
    """Stages changes in the attached suite, commits them, and pushes to remote."""
    cwd = Path.cwd()
    suite_path = get_attached_suite_path(cwd)
    if not suite_path:
        print(f"{RED}Error: No suite is attached to the current directory.{RESET}", file=sys.stderr)
        sys.exit(1)

    print(f"\n{BOLD}{CYAN}Pushing Suite Updates to GitHub:{RESET}")
    print(f"  Master Suite: {suite_path}")
    print(f"  Working Dir:  {cwd}\n")

    st = subprocess.run(["git", "-C", str(suite_path), "status", "-s"], capture_output=True, text=True)

    st = subprocess.run(["git", "-C", str(suite_path), "status", "-s"], capture_output=True, text=True)
    if not st.stdout.strip():
        print(f"{GREEN}✓ No changes detected in master suite. Everything is up to date!{RESET}\n")
        return

    print(f"{GRAY}Changed files in suite:{RESET}")
    for line in st.stdout.strip().splitlines():
        print(f"  {line}")

    print(f"\n{CYAN}Staging changes...{RESET}")
    subprocess.run(["git", "-C", str(suite_path), "add", "-A"], check=True)

    msg = args.message
    if not msg:
        project_name = cwd.name
        msg = f"refactor(skills): update suite from {project_name}"

    print(f"{CYAN}Committing: {RESET}\"{msg}\"")
    subprocess.run(["git", "-C", str(suite_path), "commit", "-m", msg], check=True)

    print(f"{CYAN}Pushing to GitHub (origin main)...{RESET}")
    subprocess.run(["git", "-C", str(suite_path), "push", "origin", "main"], check=True)
    print(f"\n{BOLD}{GREEN}✓ Successfully committed and pushed suite updates to GitHub!{RESET}\n")


def cmd_pull(args):
    """Pulls latest remote changes into the master suite from GitHub."""
    cwd = Path.cwd()
    suite_path = get_attached_suite_path(cwd)
    if not suite_path:
        print(f"{RED}Error: No suite is attached to the current directory.{RESET}", file=sys.stderr)
        sys.exit(1)

    print(f"\n{BOLD}{CYAN}Pulling Latest Suite Updates from GitHub:{RESET}")
    print(f"  Master Suite: {suite_path}\n")
    subprocess.run(["git", "-C", str(suite_path), "pull", "origin", "main"], check=True)
    print(f"\n{BOLD}{GREEN}✓ Master suite is now up to date with remote!{RESET}\n")


def cmd_diff(args):
    """Shows git diff on the master suite."""
    cwd = Path.cwd()
    suite_path = get_attached_suite_path(cwd)
    if not suite_path:
        print(f"{RED}Error: No suite is attached to the current directory.{RESET}", file=sys.stderr)
        sys.exit(1)

    subprocess.run(["git", "-C", str(suite_path), "diff"] + (args.extra or []))


def main():
    parser = argparse.ArgumentParser(
        prog="attach-suite",
        description="Cross-Platform Domain-Specific Suite Linker & Git Sync for Antigravity & AI Agents."
    )
    subparsers = parser.add_subparsers(dest="command", help="Subcommand to run")

    # attach command
    p_attach = subparsers.add_parser("attach", help="Attach a suite to the current directory")
    p_attach.add_argument("suite", help="Suite name or alias (e.g., academic, brokerage, epsilonstat)")
    p_attach.add_argument("--keep-git", action="store_true", help="Do not remove redundant .git folder in cwd")

    # fix command
    subparsers.add_parser("fix", help="Automatically repair cross-OS links (Mac <-> Windows)")

    # status command
    p_status = subparsers.add_parser("status", help="Show current attached suite status")
    p_status.add_argument("path", nargs="?", default=".", help="Directory to inspect status for (default: current directory)")

    # list command
    subparsers.add_parser("list", help="List all available suites on this OS")

    # detach command
    p_detach = subparsers.add_parser("detach", help="Detach the current suite from the directory")
    p_detach.add_argument("path", nargs="?", default=".", help="Directory to detach suite from (default: current directory)")

    # clean command
    subparsers.add_parser("clean", help="Clean orphaned locks and Google Drive conflict duplicates")

    # push command
    p_push = subparsers.add_parser("push", help="Commit and push changes in master suite to GitHub")
    p_push.add_argument("message", nargs="?", default="", help="Commit message (optional)")

    # pull command
    subparsers.add_parser("pull", help="Pull latest master suite changes from GitHub")

    # diff command
    p_diff = subparsers.add_parser("diff", help="View git diff on the master suite")
    p_diff.add_argument("extra", nargs=argparse.REMAINDER, help="Additional git diff arguments")

    # git command
    p_git = subparsers.add_parser("git", help="Run any git command directly on the master suite")

    args_list = sys.argv[1:]
    known_cmds = ["attach", "fix", "status", "list", "detach", "clean", "push", "pull", "diff", "git", "-h", "--help"]

    if args_list and args_list[0] == "git":
        cmd_git_passthrough(None, args_list[1:])
        return

    if args_list and args_list[0] not in known_cmds:
        args_list = ["attach"] + args_list

    args = parser.parse_args(args_list)

    if not args.command:
        cmd_status(args)
        return

    if args.command == "list":
        cmd_list(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "fix":
        cmd_fix(args)
    elif args.command == "detach":
        cmd_detach(args)
    elif args.command == "clean":
        cmd_clean(args)
    elif args.command == "attach":
        cmd_attach(args)
    elif args.command == "push":
        cmd_push(args)
    elif args.command == "pull":
        cmd_pull(args)
    elif args.command == "diff":
        cmd_diff(args)


if __name__ == "__main__":
    main()
