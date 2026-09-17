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
IS_LINUX = sys.platform.startswith("linux")
IS_MACOS = sys.platform == "darwin"


def get_os_name() -> str:
    """Returns a clean display name of the current operating system."""
    if IS_WINDOWS:
        return "Windows 11"
    elif IS_MACOS:
        return "macOS"
    elif IS_LINUX:
        return "Linux"
    return sys.platform


def get_cwd(target_path: str = ".") -> Path:
    """
    Safely retrieves the current working directory or resolves a target path.
    Handles FUSE cloud mounts (e.g. rclone / Google Drive) where os.getcwd()
    can raise FileNotFoundError: [Errno 2] No such file or directory due to
    stale dentry inodes or FUSE parent directory lookup disconnects.
    """
    if target_path and target_path != ".":
        p = Path(target_path).expanduser()
        try:
            return p.resolve()
        except Exception:
            return p

    # 1. Try standard Path.cwd()
    try:
        return Path.cwd().resolve()
    except (FileNotFoundError, OSError):
        pass

    # 2. Fallback to PWD environment variable (standard in bash/zsh shells)
    pwd_env = os.environ.get("PWD")
    if pwd_env:
        p = Path(pwd_env)
        if p.exists():
            try:
                os.chdir(pwd_env)
            except Exception:
                pass
            try:
                return p.resolve()
            except Exception:
                return p

    # 3. Fallback to /bin/pwd command
    try:
        res = subprocess.run(["pwd"], capture_output=True, text=True)
        if res.returncode == 0 and res.stdout.strip():
            p_str = res.stdout.strip()
            p = Path(p_str)
            if p.exists():
                try:
                    os.chdir(p_str)
                except Exception:
                    pass
                try:
                    return p.resolve()
                except Exception:
                    return p
    except Exception:
        pass

    return Path(".").absolute()


CONFIG_DIR = Path.home() / ".config" / "attach-suite"
CONFIG_FILE = CONFIG_DIR / "suites.json"

DEFAULT_SUITES = {
    "academic": {
        "name": "Academic Thesis & Statistical Consultancy Suite",
        "aliases": ["thesis", "saber", "academic_suite", "academicsuite"],
        "path": str(Path.home() / "Desktop" / "AcademicSuite"),
        "repo_url": "https://github.com/GhaderiSaber/AcademicSuite.git",
        "description": "Digital Saber, 27 academic & statistical skills, APA 7, psychometrics"
    },
    "brokerage": {
        "name": "Freight Brokerage & Logistics Suite",
        "aliases": ["freight", "freight_brokerage", "broker", "freightbrokerage"],
        "path": str(Path.home() / "Desktop" / "freight_brokerage"),
        "repo_url": "",
        "description": "Digital Broker, CMR manifests, freight orders, logistics workflows"
    },
    "epsilonstat": {
        "name": "EpsilonStat WebApp Suite",
        "aliases": ["webapp", "epsilon"],
        "path": str(Path.home() / "Desktop" / "EpsilonStat"),
        "repo_url": "",
        "description": "Full-stack React/Node statistical analysis web application"
    },
    "zarcloud": {
        "name": "ZarCloud Project Suite",
        "aliases": ["zar"],
        "path": str(Path.home() / "Desktop" / "ZarCloud"),
        "repo_url": "",
        "description": "Cloud services & financial pricing dashboard"
    },
    "duzen": {
        "name": "Duzen Workflow Suite",
        "aliases": [],
        "path": str(Path.home() / "Desktop" / "Duzen"),
        "repo_url": "",
        "description": "Automation and project organizer workflows"
    },
    "leveltrader": {
        "name": "LevelTrader Trading Suite",
        "aliases": ["trader"],
        "path": str(Path.home() / "Desktop" / "LevelTrader"),
        "repo_url": "",
        "description": "Algorithmic trading & market level analysis"
    }
}

# Items in the master suite repository that must NEVER be attached to user project folders
EXCLUDED_SUITE_ITEMS = {
    ".git",
    ".github",
    ".gitignore",
    ".venv",
    "venv",
    "env",
    "projects",
    "scratch",
    "academic-state",
    ".attached_suite.json",
    ".agents_backup_pre_attach",
    "__pycache__",
    ".pytest_cache",
    ".DS_Store",
    "Thumbs.db",
}


def is_excluded_suite_item(item_path: Path) -> bool:
    """Checks if a repository item should be excluded from being attached to a project folder."""
    name = item_path.name
    if name in EXCLUDED_SUITE_ITEMS:
        return True
    if name.endswith(".session") or name.endswith(".session-journal"):
        return True
    if name.endswith(".pyc") or name.endswith(".pyo"):
        return True
    if name.endswith(" 2") or " 2." in name:
        return True
    return False


def find_existing_suite_path(configured_path: str, key: str = "", aliases: list = None) -> Path:
    """
    Intelligently finds the suite path on disk.
    Handles case-sensitive Linux filesystems and alternate naming conventions
    (e.g., AcademicSuite vs academic_suite, FreightBrokerage vs freight_brokerage).
    """
    p = Path(configured_path).expanduser()
    try:
        p_resolved = p.resolve()
        if p_resolved.exists() and (p_resolved / ".agents").exists():
            return p_resolved
    except Exception:
        pass

    # 1. Check if the script itself is running from or installed from inside the target suite repo
    try:
        current_script_repo = Path(__file__).resolve().parent.parent
        if (current_script_repo / ".agents").exists():
            repo_norm = current_script_repo.name.lower().replace("_", "").replace("-", "")
            target_norm = key.lower().replace("_", "").replace("-", "")
            if repo_norm == target_norm or (aliases and any(repo_norm == a.lower().replace("_", "").replace("-", "") for a in aliases)):
                return current_script_repo
    except Exception:
        pass

    # 2. Check candidate directories in parent (e.g. ~/Desktop)
    parent_dir = p.parent
    if parent_dir.exists() and parent_dir.is_dir():
        all_names = [key] + (aliases or [])
        clean_targets = {name.lower().replace("_", "").replace("-", "") for name in all_names if name}
        clean_targets.add(p.name.lower().replace("_", "").replace("-", ""))

        try:
            for item in parent_dir.iterdir():
                if item.is_dir() and (item / ".agents").exists():
                    item_norm = item.name.lower().replace("_", "").replace("-", "")
                    if item_norm in clean_targets:
                        return item.resolve()
        except Exception:
            pass

    return p.resolve() if p.is_absolute() else p


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
    """Loads configured suites combining defaults and custom registrations, resolving active paths."""
    suites = dict(DEFAULT_SUITES)
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                custom = json.load(f)
                suites.update(custom)
        except Exception as e:
            print(f"{YELLOW}Warning: Could not read {CONFIG_FILE}: {e}{RESET}", file=sys.stderr)

    # Dynamically resolve existing suite paths (essential on Linux for case differences)
    for key, info in suites.items():
        found = find_existing_suite_path(info.get("path", ""), key, info.get("aliases", []))
        if found.exists():
            info["path"] = str(found)

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


def resolve_suite(query: str, suites: dict):
    """Resolves a suite name, alias, local path, or Git repository URL."""
    if not query:
        query = "academic"
    q = str(query).strip()
    q_lower = q.lower()

    # 1. Match against known suite keys and aliases
    for key, info in suites.items():
        if key.lower() == q_lower or q_lower in [a.lower() for a in info.get("aliases", [])]:
            found = find_existing_suite_path(info.get("path", ""), key, info.get("aliases", []))
            if found.exists():
                info["path"] = str(found)
            return key, info

    # 2. Match against Git repository URLs in configured suites
    clean_q_url = q_lower[:-4] if q_lower.endswith(".git") else q_lower
    for key, info in suites.items():
        url = info.get("repo_url", "").lower()
        if url:
            clean_url = url[:-4] if url.endswith(".git") else url
            if clean_q_url == clean_url or clean_q_url.endswith("/" + key.lower()) or clean_q_url.endswith("/" + key.lower().replace("_", "")):
                found = find_existing_suite_path(info.get("path", ""), key, info.get("aliases", []))
                if found.exists():
                    info["path"] = str(found)
                return key, info

    # 3. Handle explicit Git URLs (e.g., https://github.com/... or git@...)
    if q.startswith("http://") or q.startswith("https://") or q.startswith("git@") or q.endswith(".git"):
        # Match AcademicSuite repo specifically
        if "academicsuite" in q_lower.replace("-", "").replace("_", ""):
            info = dict(suites.get("academic", DEFAULT_SUITES["academic"]))
            info["repo_url"] = q
            found = find_existing_suite_path(info.get("path", ""), "academic", info.get("aliases", []))
            if found.exists():
                info["path"] = str(found)
            return "academic", info

        # Derive repo name from generic URL
        repo_name = q.rstrip("/").split("/")[-1]
        if repo_name.endswith(".git"):
            repo_name = repo_name[:-4]
        key = repo_name.lower().replace("-", "_")
        dest_path = Path.home() / "Desktop" / repo_name
        return key, {
            "name": f"{repo_name} Suite",
            "aliases": [],
            "path": str(dest_path),
            "repo_url": q,
            "description": f"Git repository suite from {q}"
        }

    # 4. Check if query is an existing local directory path with .agents
    p = Path(query).expanduser().resolve()
    if p.exists() and (p / ".agents").exists():
        return p.name.lower(), {
            "name": p.name,
            "path": str(p),
            "description": f"Custom local suite at {p}"
        }

    # 5. Default fallback to academic if query == 'academic'
    if "academic" in suites:
        found = find_existing_suite_path(suites["academic"].get("path", ""), "academic", suites["academic"].get("aliases", []))
        if found.exists():
            suites["academic"]["path"] = str(found)
        return "academic", suites["academic"]

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
    Creates a directory symlink (macOS/Linux/Windows Developer Mode),
    Directory Junction (Windows fallback), or Antigravity Pointer Link (Google Drive FUSE/rclone/FAT32).
    Returns link type: 'symlink', 'junction', or 'pointer'.
    """
    if is_link_path(link_path):
        remove_link(link_path)
    elif link_path.exists():
        if (link_path / "skills.json").exists():
            try:
                shutil.rmtree(link_path)
            except Exception:
                remove_link(link_path, allow_delete_dir=True)
        else:
            remove_link(link_path, allow_delete_dir=True)

    target_str = str(target.resolve())
    link_str = str(link_path.absolute())

    # 1. Prioritize native Directory Symbolic Link
    try:
        if IS_WINDOWS:
            os.symlink(target_str, link_str, target_is_directory=True)
        else:
            os.symlink(target_str, link_str)
        return "symlink"
    except OSError:
        pass

    # 2. Fallback to Directory Junction on Windows (mklink /J)
    if IS_WINDOWS:
        res = subprocess.run(["cmd", "/c", "mklink", "/J", link_str, target_str], capture_output=True, text=True)
        if res.returncode == 0:
            return "junction"

    # 3. Universal Fallback: Antigravity Pointer Link for non-NTFS / FUSE / cloud virtual filesystems
    # (e.g. Google Drive FUSE / rclone / FAT32 / network mounts across Linux, macOS, and Windows)
    print(f"{YELLOW}Notice: Filesystem at '{link_path}' does not support symbolic links (e.g. Google Drive FUSE/rclone).{RESET}")
    print(f"{CYAN}Engaging Antigravity Pointer Link (linking via skills.json without copying files)...{RESET}")
    try:
        link_path.mkdir(parents=True, exist_ok=True)
        target_skills = target / "skills" if (target / "skills").exists() else target
        skills_json = link_path / "skills.json"
        with open(skills_json, "w", encoding="utf-8") as f:
            json.dump({"entries": [{"path": str(target_skills).replace("\\", "/")}]}, f, indent=2)

        # Mirror hooks.json and rules/ if present so agent lifecycle guards work
        hooks_src = target / "hooks.json"
        if hooks_src.exists():
            try:
                shutil.copy2(hooks_src, link_path / "hooks.json")
            except Exception:
                pass

        rules_src = target / "rules"
        if rules_src.exists() and rules_src.is_dir():
            rules_dest = link_path / "rules"
            try:
                if rules_dest.exists():
                    shutil.rmtree(rules_dest)
                shutil.copytree(rules_src, rules_dest)
            except Exception:
                pass

        return "pointer"
    except Exception as e:
        print(f"\n{RED}Error: Could not create pointer link on this filesystem: {e}{RESET}\n", file=sys.stderr)
        sys.exit(1)


def create_file_link(target: Path, link_path: Path) -> str:
    """Creates a file symlink, hard link, or fallback copy."""
    if is_link_path(link_path) or link_path.exists():
        remove_link(link_path)

    target_str = str(target.resolve())
    link_str = str(link_path.absolute())

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
        # POSIX fallback: copy file
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
    """Detects if a link target was created on a different OS (e.g. Windows path on Linux/Mac, or vice versa)."""
    if not target_str:
        return False
    clean = target_str[4:] if target_str.startswith("\\\\?\\") else target_str
    if IS_WINDOWS:
        # On Windows, foreign if starting with /Users/ (macOS) or /home/ (Linux)
        return clean.startswith("/Users/") or clean.startswith("/home/")
    elif IS_LINUX:
        # On Linux, foreign if starting with Windows drive (C:\, D:\) or /Users/ (macOS)
        has_win_drive = len(clean) > 1 and clean[1] == ":"
        return has_win_drive or clean.startswith("\\\\") or clean.startswith("/Users/")
    else:
        # On macOS, foreign if starting with Windows drive or /home/ (Linux)
        has_win_drive = len(clean) > 1 and clean[1] == ":"
        return has_win_drive or clean.startswith("\\\\") or clean.startswith("/home/")


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

    ignore_dirs = {".git", ".agents", ".venv", "node_modules"}

    # Clean ' 2' conflict files
    for item in target_dir.rglob("* 2.*"):
        if any(ignored in item.parts for ignored in ignore_dirs):
            continue
        if "03_deliverables" in str(item) or "01_raw_inputs" in str(item):
            continue
        if item.is_file():
            try:
                item.unlink()
                cleaned.append(str(item.relative_to(target_dir)))
            except Exception:
                pass

    for d in target_dir.rglob("* 2"):
        if any(ignored in d.parts for ignored in ignore_dirs):
            continue
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
    """Inspects the current working directory for attached suites and repository items."""
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

    attached_items = []
    if attached_info and "attached_items" in attached_info:
        for item_name in attached_info["attached_items"]:
            p = target_dir / item_name
            is_link = is_link_path(p)
            target = read_link_target(p) if is_link else None
            valid = False
            if is_link and target:
                valid = Path(target).exists()
            elif p.exists():
                valid = True
            attached_items.append({
                "name": item_name,
                "is_dir": p.is_dir(),
                "is_link": is_link,
                "target": target,
                "valid": valid,
                "foreign": is_foreign_os_link(target) if target else False
            })

    # Check if any separate suite subfolder was created in project folder
    separate_folders = [
        name for name in ["AcademicSuite", "Academic_Suite", "academic_suite", "freight_brokerage", "EpsilonStat"]
        if (target_dir / name).is_dir() and not is_link_path(target_dir / name) and ((target_dir / name) / ".git").exists()
    ]

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
        "attached_items": attached_items,
        "separate_folders": separate_folders
    }


def cmd_list(args):
    suites = load_suites()
    current_os = get_os_name()
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
    cwd = get_cwd(target_path)
    status = get_status(cwd)
    suite_path = get_attached_suite_path(cwd)
    current_os = get_os_name()

    print(f"\n{BOLD}{CYAN}Suite Attachment Status ({current_os}):{RESET} {cwd}")
    print("=" * 65)

    if status["meta"]:
        print(f"  {BOLD}Attached Suite:{RESET}   {GREEN}{status['meta'].get('suite', 'Unknown')}{RESET}")
        print(f"  {BOLD}Suite Title:{RESET}      {status['meta'].get('name', 'Unknown')}")
        if suite_path:
            print(f"  {BOLD}Local Path:{RESET}       {GREEN}{suite_path}{RESET}")
        else:
            print(f"  {BOLD}Recorded Path:{RESET}    {YELLOW}{status['meta'].get('path', 'Unknown')}{RESET}")
        if status["meta"].get("repo_url"):
            print(f"  {BOLD}Repo URL:{RESET}         {CYAN}{status['meta']['repo_url']}{RESET}")
    else:
        print(f"  {BOLD}Attached Suite:{RESET}   {YELLOW}None recorded in .attached_suite.json{RESET}")

    # Report if separate subfolder exists
    if status.get("separate_folders"):
        print(f"  {BOLD}Separate Folder:{RESET}  {RED}Warning: Found nested suite folder(s): {', '.join(status['separate_folders'])}{RESET}")
    else:
        print(f"  {BOLD}Project Structure:{RESET}{GREEN} Clean (No separate repo folder; content attached to project root){RESET}")

    # Check attached repo contents
    items = status.get("attached_items", [])
    if items:
        print(f"\n  {BOLD}Attached Repository Contents ({len(items)} items in root):{RESET}")
        for it in items:
            name_str = f"{it['name']}/" if it['is_dir'] else it['name']
            if it["is_link"]:
                if it["foreign"]:
                    print(f"    {YELLOW}! {name_str}{RESET} (Link created on foreign OS: {it['target']})")
                elif it["valid"]:
                    print(f"    {GREEN}✓ {name_str}{RESET} -> {GRAY}{it['target']}{RESET}")
                else:
                    print(f"    {RED}✗ {name_str}{RESET} -> {RED}[Broken link: {it['target']}]{RESET}")
            elif it["valid"]:
                print(f"    {GREEN}✓ {name_str}{RESET} [Physical / Pointer Link]")
            else:
                print(f"    {GRAY}- {name_str} [Missing]{RESET}")
    else:
        # Fallback check for .agents and AGENTS.md
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
            if (cwd / ".agents" / "skills.json").exists():
                print(f"  {BOLD}.agents:{RESET}          {CYAN}Pointer Link (skills.json){RESET} [{GREEN}Valid{RESET}]")
            else:
                print(f"  {BOLD}.agents:{RESET}          {YELLOW}Physical Directory (Not a link){RESET}")
        else:
            print(f"  {BOLD}.agents:{RESET}          {GRAY}Not present{RESET}")

        if status["agents_md_is_link"]:
            md_type = "Symlink" if (cwd / "AGENTS.md").is_symlink() else "Link"
            print(f"  {BOLD}AGENTS.md:{RESET}        {CYAN}{md_type} --> {status['agents_md_target']}{RESET}")
        elif (cwd / "AGENTS.md").exists():
            if is_attached_agents_md(cwd / "AGENTS.md"):
                print(f"  {BOLD}AGENTS.md:{RESET}        {CYAN}Attached File Copy{RESET} [{GREEN}Valid{RESET}]")
            else:
                print(f"  {BOLD}AGENTS.md:{RESET}        {YELLOW}Physical File{RESET}")
        else:
            print(f"  {BOLD}AGENTS.md:{RESET}        {GRAY}Not present{RESET}")

    # Check .git
    if status["has_local_git"]:
        print(f"\n  {BOLD}.git Directory:{RESET}   {YELLOW}Present in project folder (May cause cloud drive sync locks){RESET}")
    else:
        print(f"\n  {BOLD}.git Directory:{RESET}   {GREEN}None in project folder (Clean! Master Git safely centralized){RESET}")

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

    if not status["meta"]:
        print(f"\n  {YELLOW}Tip: Run 'attach-suite attach' to attach AcademicSuite to this project.{RESET}")

    print("=" * 65 + "\n")


def cmd_fix(args):
    """Automatically repairs cross-OS links (e.g. Mac path on Windows or Windows path on Mac)."""
    cwd = get_cwd()
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

    current_os = get_os_name()
    print(f"\n{BOLD}{CYAN}Repairing cross-OS link for suite '{suite_name}' on {current_os}...{RESET}")
    # Call attach for this suite
    args.suite = suite_name
    args.keep_git = False
    cmd_attach(args)


def cmd_detach(args):
    target_path = getattr(args, "path", ".") or "."
    cwd = get_cwd(target_path)
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
    attached_items_from_meta = []

    if has_meta:
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                info = json.load(f)
                attached_items_from_meta = info.get("attached_items", [])
        except Exception:
            pass

    removed = []

    # Items to check and detach
    items_to_detach = set(attached_items_from_meta)
    default_candidates = [
        ".agents", "AGENTS.md", "ANTIGRAVITY_ARCHITECTURE_GUIDE.md",
        "Questionnaires.xlsx", "digital_saber.py", "digital_broker.py",
        "agents", "data", "docs", "evals", "factory", "recovery",
        "scripts", "tests", "validators", "webapp", "requirements.txt",
        "run_tests.py", "SETUP_GUIDE.md"
    ]
    items_to_detach.update(default_candidates)

    for item_name in sorted(items_to_detach):
        p = cwd / item_name
        if not p.exists() and not is_link_path(p):
            continue

        if is_link_path(p):
            remove_link(p, allow_delete_dir=p.is_dir())
            removed.append(f"{item_name} (link)")
        elif p.is_dir():
            if item_name == ".agents" and (has_meta or (p / "skills.json").exists()):
                try:
                    shutil.rmtree(p)
                    removed.append(".agents (pointer directory)")
                except Exception as e:
                    print(f"{YELLOW}Could not remove .agents directory: {e}{RESET}")
        elif p.is_file():
            if item_name == "AGENTS.md" and (has_meta or is_attached_agents_md(p)):
                try:
                    p.unlink()
                    removed.append("AGENTS.md")
                except Exception as e:
                    print(f"{YELLOW}Could not remove AGENTS.md: {e}{RESET}")

    # Restore pre-attach backup if one exists
    backup_agents = cwd / ".agents_backup_pre_attach"
    if backup_agents.exists() and not (cwd / ".agents").exists():
        try:
            backup_agents.rename(cwd / ".agents")
            removed.append("restored original .agents from backup")
        except Exception as e:
            print(f"{YELLOW}Could not restore backup .agents: {e}{RESET}")

    # Remove metadata file
    if meta_file.exists():
        try:
            meta_file.unlink()
            removed.append(".attached_suite.json")
        except Exception as e:
            print(f"{YELLOW}Could not remove metadata file: {e}{RESET}")

    if removed:
        print(f"\n{GREEN}✓ Successfully detached suite repository contents:{RESET}")
        for r in removed:
            print(f"   - {r}")
    else:
        print(f"\n{YELLOW}No active suite links or attached metadata found to detach in: {cwd}{RESET}")
    print()


def cmd_clean(args):
    cwd = get_cwd()
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
    cwd = get_cwd()
    suites = load_suites()
    suite_arg = getattr(args, "suite", "academic") or "academic"
    suite_key, suite_info = resolve_suite(suite_arg, suites)

    if not suite_info:
        print(f"\n{RED}Error: Unknown suite '{suite_arg}'.{RESET}")
        print(f"Run {BOLD}attach-suite list{RESET} to see all available suites.\n")
        sys.exit(1)

    suite_path = Path(suite_info["path"]).resolve()

    # If suite repository does not exist on this machine, automatically clone it
    # CRITICAL: Cloned to suite_path (e.g. ~/Desktop/AcademicSuite), NEVER inside cwd (project folder)!
    if not suite_path.exists():
        repo_url = suite_info.get("repo_url")
        if not repo_url and suite_key == "academic":
            repo_url = "https://github.com/GhaderiSaber/AcademicSuite.git"
            suite_info["repo_url"] = repo_url

        if repo_url:
            current_os = get_os_name()
            print(f"\n{BOLD}{CYAN}Suite '{suite_key}' not found locally at:{RESET} {suite_path}")
            print(f"{BOLD}{CYAN}Automatically cloning suite repository on {current_os}...{RESET}")
            print(f"  Repo URL:    {repo_url}")
            print(f"  Destination: {suite_path} (Centralized Master Suite)\n")
            try:
                suite_path.parent.mkdir(parents=True, exist_ok=True)
                subprocess.run(["git", "clone", repo_url, str(suite_path)], check=True)
                print(f"{GREEN}✓ Successfully cloned {suite_key} repository to {suite_path}!{RESET}\n")
            except Exception as e:
                print(f"\n{RED}Error: Failed to clone repository from {repo_url}: {e}{RESET}\n", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"\n{RED}Error: Suite directory does not exist on this machine:{RESET} {suite_path}")
            if IS_WINDOWS:
                print(f"{YELLOW}Tip: On Windows 11, please clone {suite_key} to:{RESET} {suite_path}")
            else:
                print(f"{YELLOW}Tip: Please clone or pull {suite_key} to:{RESET} {suite_path}")
            print()
            sys.exit(1)

    # Safety check: Never attach a suite to its own repository
    if cwd == suite_path:
        print(f"\n{RED}Error: Current directory is the master suite itself ({suite_path}).{RESET}")
        print(f"{YELLOW}You cannot attach a suite to its own master repository.{RESET}\n")
        sys.exit(1)

    agents_src = suite_path / ".agents"
    if not agents_src.exists():
        print(f"\n{RED}Error: Suite does not contain a .agents directory:{RESET} {agents_src}\n")
        sys.exit(1)

    current_os = get_os_name()
    print(f"\n{BOLD}{CYAN}Attaching Suite Repository ({current_os}):{RESET} {BOLD}{suite_info['name']}{RESET}")
    print(f"  Source Repo:    {suite_path}")
    print(f"  Target Project: {cwd}")
    print(f"  Policy:         Attaching repository content directly to project root (no separate repo folder)\n")

    # Step 1: Clean conflicts and stale locks
    cleaned = clean_conflicts_and_locks(cwd)
    if cleaned:
        print(f"{GRAY}Cleaned {len(cleaned)} stale lock/conflict items.{RESET}")

    # Step 2: Handle redundant .git in project folder if it points to the suite repo
    git_dir = cwd / ".git"
    if git_dir.exists() and not is_link_path(git_dir):
        if not getattr(args, 'keep_git', False):
            has_suite_remote = False
            try:
                res = subprocess.run(["git", "-C", str(cwd), "remote", "-v"], capture_output=True, text=True)
                if "AcademicSuite" in res.stdout or suite_key in res.stdout.lower():
                    has_suite_remote = True
            except Exception:
                pass

            if has_suite_remote:
                print(f"{YELLOW}Notice: Found local .git directory in Google Drive folder pointing to suite.{RESET}")
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
        if (existing_agents / "skills.json").exists() or (cwd / ".attached_suite.json").exists():
            try:
                shutil.rmtree(existing_agents)
            except Exception:
                pass
        else:
            backup_dir = cwd / ".agents_backup_pre_attach"
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            print(f"{YELLOW}Moving physical .agents folder to {backup_dir.name}...{RESET}")
            existing_agents.rename(backup_dir)

    # Step 4: Attach all content of the repository directly to project folder
    attached_items = []
    skipped_items = []

    # Iterate over top-level items in suite_path
    for item in sorted(suite_path.iterdir()):
        if is_excluded_suite_item(item):
            continue

        item_name = item.name
        dest = cwd / item_name

        if item.is_dir():
            if dest.name == ".agents":
                link_type = create_dir_link(item, dest)
                link_label = "Symbolic Link" if link_type == "symlink" else ("Directory Junction" if link_type == "junction" else "Pointer Link")
                print(f"{GREEN}✓ Attached .agents ({link_label}) --> {item}{RESET}")
                attached_items.append(item_name)
            elif is_link_path(dest):
                remove_link(dest, allow_delete_dir=True)
                link_type = create_dir_link(item, dest)
                attached_items.append(item_name)
            elif not dest.exists():
                link_type = create_dir_link(item, dest)
                link_label = "Symbolic Link" if link_type == "symlink" else ("Directory Junction" if link_type == "junction" else "Pointer Link")
                print(f"{GREEN}✓ Attached {item_name}/ ({link_label}) --> {item}{RESET}")
                attached_items.append(item_name)
            else:
                skipped_items.append(f"{item_name}/ (kept existing project directory)")
        elif item.is_file() or item.is_symlink():
            if is_link_path(dest):
                remove_link(dest)
                file_type = create_file_link(item, dest)
                attached_items.append(item_name)
            elif not dest.exists():
                file_type = create_file_link(item, dest)
                file_label = "Symbolic Link" if file_type == "symlink" else ("Hard Link" if file_type == "hardlink" else "File Copy")
                print(f"{GREEN}✓ Attached {item_name} ({file_label}) --> {item}{RESET}")
                attached_items.append(item_name)
            elif dest.name == "AGENTS.md" and is_attached_agents_md(dest):
                remove_link(dest)
                file_type = create_file_link(item, dest)
                attached_items.append(item_name)
            else:
                skipped_items.append(f"{item_name} (kept existing project file)")

    # Save attachment metadata
    meta = {
        "suite": suite_key,
        "name": suite_info["name"],
        "path": str(suite_path),
        "repo_url": suite_info.get("repo_url", "https://github.com/GhaderiSaber/AcademicSuite.git"),
        "attached_at": datetime.now().isoformat(),
        "attached_os": current_os,
        "attached_items": attached_items
    }
    with open(cwd / ".attached_suite.json", "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2)

    # Count active skills
    skills = [s.name for s in (agents_src / "skills").iterdir() if s.is_dir()] if (agents_src / "skills").exists() else []

    print(f"\n{BOLD}{GREEN}Successfully attached repository content of {suite_key} on {current_os}!{RESET}")
    print(f"  {BOLD}Directly attached to project root:{RESET} {len(attached_items)} items")
    print(f"  {GRAY}{', '.join(attached_items)}{RESET}")
    if skipped_items:
        print(f"  {YELLOW}Preserved {len(skipped_items)} existing project items:{RESET} {GRAY}{', '.join(skipped_items)}{RESET}")
    print(f"  Antigravity will load {len(skills)} skills directly in this project.")
    print(f"\n{BOLD}Result:{RESET} Zero nested repo folders. Repo contents directly attached. Zero Git locks.\n")


def cmd_git_passthrough(args, unknown_args):
    """Runs any arbitrary git command against the master suite repo from current directory."""
    cwd = get_cwd()
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
    cwd = get_cwd()
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
    cwd = get_cwd()
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
    cwd = get_cwd()
    suite_path = get_attached_suite_path(cwd)
    if not suite_path:
        print(f"{RED}Error: No suite is attached to the current directory.{RESET}", file=sys.stderr)
        sys.exit(1)

    subprocess.run(["git", "-C", str(suite_path), "diff"] + (args.extra or []))


def cmd_install(args):
    """Installs attach-suite CLI into system/user PATH for direct terminal execution."""
    script_path = Path(__file__).resolve()
    current_os = get_os_name()
    print(f"\n{BOLD}{CYAN}Installing attach-suite for {current_os}...{RESET}")
    print(f"  Source script: {script_path}")

    # Ensure python script is executable on POSIX
    if not IS_WINDOWS:
        try:
            mode = script_path.stat().st_mode
            script_path.chmod(mode | 0o755)
            print(f"  {GREEN}✓ Set executable permission (755) on {script_path.name}{RESET}")
        except Exception as e:
            print(f"  {YELLOW}Warning: Could not chmod {script_path.name}: {e}{RESET}")

    if IS_WINDOWS:
        win_bin = Path.home() / "AppData" / "Local" / "Microsoft" / "WindowsApps"
        bat_dest = win_bin / "attach-suite.bat"
        try:
            win_bin.mkdir(parents=True, exist_ok=True)
            with open(bat_dest, "w", encoding="utf-8") as f:
                f.write(f"@echo off\r\npython \"{script_path}\" %*\r\n")
            print(f"  {GREEN}✓ Created Windows CLI wrapper: {bat_dest}{RESET}")
            print(f"\n{BOLD}{GREEN}Installation successful!{RESET} You can now run {BOLD}{CYAN}attach-suite{RESET} anywhere in your terminal.\n")
        except Exception as e:
            print(f"  {RED}Error: Could not install to {win_bin}: {e}{RESET}")
    else:
        # Linux / macOS
        is_global = getattr(args, "global_install", False) or (hasattr(os, "geteuid") and os.geteuid() == 0)
        dest_dir = Path("/usr/local/bin") if is_global else (Path.home() / ".local" / "bin")
        dest_dir.mkdir(parents=True, exist_ok=True)
        link_dest = dest_dir / "attach-suite"

        if link_dest.is_symlink() or link_dest.exists():
            try:
                link_dest.unlink()
            except Exception:
                pass

        try:
            link_dest.symlink_to(script_path)
            print(f"  {GREEN}✓ Created CLI symlink:{RESET} {link_dest} -> {script_path}")
        except OSError:
            # Fallback wrapper
            with open(link_dest, "w", encoding="utf-8") as f:
                f.write(f"#!/usr/bin/env bash\nexec python3 \"{script_path}\" \"$@\"\n")
            link_dest.chmod(0o755)
            print(f"  {GREEN}✓ Created CLI wrapper script:{RESET} {link_dest}")

        # Check PATH
        path_dirs = os.environ.get("PATH", "").split(os.pathsep)
        in_path = str(dest_dir) in path_dirs or str(dest_dir.resolve()) in path_dirs
        if in_path:
            print(f"  {GREEN}✓ Directory '{dest_dir}' is already in your PATH!{RESET}")
            print(f"\n{BOLD}{GREEN}Installation successful!{RESET} You can now run {BOLD}{CYAN}attach-suite{RESET} anywhere in your terminal.\n")
        else:
            print(f"  {YELLOW}Notice: '{dest_dir}' is not currently in your PATH.{RESET}")
            print(f"  Add it by running:")
            print(f"    echo 'export PATH=\"{dest_dir}:$PATH\"' >> ~/.bashrc && source ~/.bashrc\n")


def main():
    parser = argparse.ArgumentParser(
        prog="attach-suite",
        description="Cross-Platform Domain-Specific Suite Linker & Git Sync for Antigravity & AI Agents."
    )
    subparsers = parser.add_subparsers(dest="command", help="Subcommand to run")

    # attach command
    p_attach = subparsers.add_parser("attach", help="Attach a suite to the current directory")
    p_attach.add_argument("suite", nargs="?", default="academic", help="Suite name, alias, or Git repo URL (default: academic)")
    p_attach.add_argument("--keep-git", action="store_true", help="Do not remove redundant .git folder in cwd")

    # fix command
    subparsers.add_parser("fix", help="Automatically repair cross-OS links (Mac <-> Windows <-> Linux)")

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

    # install command
    p_install = subparsers.add_parser("install", help="Install attach-suite into system/user PATH")
    p_install.add_argument("--global", dest="global_install", action="store_true", help="Install to /usr/local/bin (requires sudo)")

    args_list = sys.argv[1:]
    known_cmds = ["attach", "fix", "status", "list", "detach", "clean", "push", "pull", "diff", "git", "install", "-h", "--help"]

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
    elif args.command == "install":
        cmd_install(args)


if __name__ == "__main__":
    main()
