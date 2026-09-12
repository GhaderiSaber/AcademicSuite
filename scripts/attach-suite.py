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
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
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
    """Checks whether a path is a symlink or Windows directory junction."""
    if not p.exists() and not p.is_symlink():
        return False
    if p.is_symlink():
        return True
    if IS_WINDOWS:
        try:
            return os.path.islink(str(p))
        except Exception:
            pass
    return False


def copy_dir_tree(src: Path, dst: Path):
    """Copies an entire directory tree, cleanly replacing any existing destination."""
    if dst.exists():
        if is_link_path(dst):
            remove_link(dst)
        elif dst.is_dir():
            shutil.rmtree(dst)
        else:
            dst.unlink()
    shutil.copytree(src, dst)


def sync_newer_files(src_root: Path, dst_root: Path) -> list:
    """Syncs files from src_root to dst_root if they are newer or missing in dst_root."""
    synced = []
    if not src_root.exists():
        return synced
    for p in src_root.rglob("*"):
        if p.is_file():
            # Skip python caches and git files
            if "__pycache__" in p.parts or ".git" in p.parts:
                continue
            rel = p.relative_to(src_root)
            dst_p = dst_root / rel
            should_copy = False
            if not dst_p.exists():
                should_copy = True
            else:
                try:
                    if p.stat().st_mtime > dst_p.stat().st_mtime + 1.0:
                        should_copy = True
                except Exception:
                    pass
            if should_copy:
                dst_p.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(p, dst_p)
                synced.append(str(rel))
    return synced


def create_dir_link(target: Path, link_path: Path, allow_fallback_copy: bool = True) -> str:
    """
    Creates a directory symlink (macOS/Linux) or Directory Junction (Windows 11).
    Returns link type: 'junction', 'symlink', or 'copy'.
    """
    if is_link_path(link_path):
        remove_link(link_path)

    target_str = str(target.resolve())
    link_str = str(link_path.resolve())

    if IS_WINDOWS:
        # On Windows 11, Directory Junctions (mklink /J) require NO Admin or Developer Mode
        res = subprocess.run(["cmd", "/c", "mklink", "/J", link_str, target_str], capture_output=True, text=True)
        if res.returncode == 0:
            return "junction"

        # Fallback to python os.symlink
        try:
            os.symlink(target_str, link_str, target_is_directory=True)
            return "symlink"
        except OSError as e:
            drive = link_path.drive or str(link_path)[:2]
            if allow_fallback_copy:
                print(f"{YELLOW}Notice: Filesystem on '{drive}' (Google Drive File Stream / FAT32) does not support NTFS Junctions or Symlinks.{RESET}")
                print(f"{CYAN}Engaging Antigravity Pointer Link (linking via skills.json without copying files)...{RESET}")
                link_path.mkdir(parents=True, exist_ok=True)
                skills_json = link_path / "skills.json"
                target_skills = target / "skills" if (target / "skills").exists() else target
                with open(skills_json, "w", encoding="utf-8") as f:
                    json.dump({"entries": [{"path": str(target_skills).replace("\\", "/")}]}, f, indent=2)
                return "pointer"
            else:
                print(f"\n{RED}{BOLD}Error: Filesystem on '{drive}' does not support NTFS Directory Junctions or Symlinks.{RESET}")
                print(f"{YELLOW}Root Cause:{RESET} Drive '{drive}' is a virtual streamed volume (Google Drive File Stream / FAT32),")
                print(f"            which rejects NTFS reparse points: {e}")
                sys.exit(1)
    else:
        try:
            os.symlink(target_str, link_str)
            return "symlink"
        except OSError as e:
            if allow_fallback_copy:
                print(f"{YELLOW}Notice: Could not create symlink ({e}). Falling back to Copy Mode...{RESET}")
                copy_dir_tree(target, link_path)
                return "copy"
            else:
                print(f"\n{RED}Error: Could not create symlink on this filesystem: {e}{RESET}\n", file=sys.stderr)
                sys.exit(1)


def create_file_link(target: Path, link_path: Path):
    """Creates a file symlink, hard link, or fallback copy."""
    if is_link_path(link_path) or link_path.exists():
        remove_link(link_path)

    target_str = str(target.resolve())
    link_str = str(link_path.resolve())

    if IS_WINDOWS:
        # Try NTFS hard link first (mklink /H)
        res = subprocess.run(["cmd", "/c", "mklink", "/H", link_str, target_str], capture_output=True, text=True)
        if res.returncode != 0:
            # Cross-volume / FAT32 fallback: copy file
            shutil.copy2(target, link_path)
    else:
        try:
            os.symlink(target_str, link_str)
        except OSError:
            shutil.copy2(target, link_path)


def remove_link(link_path: Path, allow_delete_dir: bool = False):
    """Safely removes a symlink, directory junction, or pointer without deleting target contents."""
    if not link_path.exists() and not is_link_path(link_path):
        return

    if is_link_path(link_path):
        if IS_WINDOWS:
            # For Windows Junctions, use os.rmdir or rmdir command (does NOT delete target directory contents)
            try:
                os.rmdir(link_path)
            except OSError:
                subprocess.run(["cmd", "/c", "rmdir", str(link_path)], capture_output=True)
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
        return os.readlink(p)
    except Exception:
        return None


def is_foreign_os_link(target_str: str) -> bool:
    """Detects if a link target was created on a different OS (e.g. Mac path on Windows)."""
    if not target_str:
        return False
    if IS_WINDOWS:
        # On Windows, if link starts with /Users/ or /home/, it's from Mac/Linux
        return target_str.startswith("/Users/") or target_str.startswith("/home/")
    else:
        # On Mac/Linux, if link starts with C:\ or G:\, it's from Windows
        return len(target_str) > 2 and target_str[1] == ":"


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
    cwd = Path.cwd()
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
            link_type = "Junction" if IS_WINDOWS else "Symlink"
            print(f"  {BOLD}.agents:{RESET}          {CYAN}{link_type} ──► {target}{RESET} [{color}{'Valid' if valid else 'Broken'}{RESET}]")
    elif status["agents_exists"]:
        print(f"  {BOLD}.agents:{RESET}          {YELLOW}Physical Directory (Not a link){RESET}")
    else:
        print(f"  {BOLD}.agents:{RESET}          {GRAY}Not present{RESET}")

    # Check AGENTS.md
    if status["agents_md_is_link"]:
        print(f"  {BOLD}AGENTS.md:{RESET}        {CYAN}Link ──► {status['agents_md_target']}{RESET}")
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
    cwd = Path.cwd()
    print(f"\n{BOLD}Detaching suite from:{RESET} {cwd}")

    removed = []
    for item_name in [".agents", "AGENTS.md", "scripts", "digital_saber.py", "digital_broker.py"]:
        p = cwd / item_name
        if is_link_path(p) or p.is_symlink():
            remove_link(p)
            removed.append(item_name)

    meta_file = cwd / ".attached_suite.json"
    if meta_file.exists():
        meta_file.unlink()
        removed.append(".attached_suite.json")

    if removed:
        print(f"{GREEN}✓ Successfully detached links:{RESET} {', '.join(removed)}")
    else:
        print(f"{YELLOW}No active suite links found to detach.{RESET}")
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
    force_copy = getattr(args, "copy", False)
    link_type = create_dir_link(agents_src, existing_agents, allow_fallback_copy=True)
    if force_copy and link_type != "copy":
        copy_dir_tree(agents_src, existing_agents)
        link_type = "copy"
    link_label = "Directory Junction" if link_type == "junction" else ("Symlink" if link_type == "symlink" else "Copied Folder (Fallback)")
    print(f"{GREEN}✓ Attached .agents ({link_label}) ──► {agents_src}{RESET}")

    agents_md_src = suite_path / "AGENTS.md"
    if agents_md_src.exists():
        create_file_link(agents_md_src, existing_agents_md)
        print(f"{GREEN}✓ Attached AGENTS.md ──► {agents_md_src}{RESET}")

    # Optionally link scripts
    scripts_src = suite_path / "scripts"
    scripts_dest = cwd / "scripts"
    if scripts_src.exists():
        if is_link_path(scripts_dest):
            remove_link(scripts_dest, allow_delete_dir=True)
            scripts_type = create_dir_link(scripts_src, scripts_dest)
            print(f"{GREEN}✓ Attached scripts/ ({scripts_type}) ──► {scripts_src}{RESET}")
        elif not scripts_dest.exists():
            scripts_type = create_dir_link(scripts_src, scripts_dest)
            print(f"{GREEN}✓ Attached scripts/ ({scripts_type}) ──► {scripts_src}{RESET}")

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
    meta_file = cwd / ".attached_suite.json"
    if meta_file.exists():
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                meta = json.load(f)
            if meta.get("link_type") == "copy":
                agents_dir = cwd / ".agents"
                if agents_dir.exists() and (suite_path / ".agents").exists():
                    synced = sync_newer_files(agents_dir, suite_path / ".agents")
                    if synced:
                        print(f"{CYAN}Synced {len(synced)} updated file(s) from project back to master suite.{RESET}")
        except Exception as e:
            print(f"{YELLOW}Warning during copy sync: {e}{RESET}")

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
    p_attach.add_argument("--copy", action="store_true", help="Force direct copy mode instead of directory links")

    # fix command
    subparsers.add_parser("fix", help="Automatically repair cross-OS links (Mac <-> Windows)")

    # status command
    subparsers.add_parser("status", help="Show current attached suite status")

    # list command
    subparsers.add_parser("list", help="List all available suites on this OS")

    # detach command
    subparsers.add_parser("detach", help="Detach the current suite from the directory")

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
