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

def _resolve_default_academic_path() -> str:
    for candidate in [
        Path.home() / "Desktop" / "Projects" / "AcademicSuite",
        Path.home() / "Desktop" / "AcademicSuite",
        Path.home() / "Projects" / "AcademicSuite",
    ]:
        if candidate.exists() and (candidate / ".agents").exists():
            return str(candidate)
    return str(Path.home() / "Desktop" / "AcademicSuite")


DEFAULT_SUITES = {
    "academic": {
        "name": "Academic Thesis & Statistical Consultancy Suite",
        "aliases": ["thesis", "saber", "academic_suite", "academicsuite"],
        "path": _resolve_default_academic_path(),
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
        script_file = Path(__file__).resolve()
        for candidate_root in [script_file.parent.parent.parent, script_file.parent.parent]:
            if (candidate_root / ".agents").is_dir() and candidate_root.name != ".agents":
                repo_norm = candidate_root.name.lower().replace("_", "").replace("-", "")
                target_norm = key.lower().replace("_", "").replace("-", "")
                if repo_norm == target_norm or (aliases and any(repo_norm == a.lower().replace("_", "").replace("-", "") for a in aliases)):
                    return candidate_root
    except Exception:
        pass

    # 2. Check candidate directories in parent (e.g. ~/Desktop, ~/Desktop/Projects, ~/Projects)
    parent_dir = p.parent
    if parent_dir.exists() and parent_dir.is_dir():
        all_names = [key] + (aliases or [])
        clean_targets = {name.lower().replace("_", "").replace("-", "") for name in all_names if name}
        clean_targets.add(p.name.lower().replace("_", "").replace("-", ""))

        candidate_parents = [parent_dir]
        for sub in ["Projects", "projects"]:
            sub_p = parent_dir / sub
            if sub_p.is_dir() and sub_p not in candidate_parents:
                candidate_parents.append(sub_p)
        home_projects = Path.home() / "Projects"
        if home_projects.is_dir() and home_projects not in candidate_parents:
            candidate_parents.append(home_projects)

        try:
            for c_dir in candidate_parents:
                for item in c_dir.iterdir():
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
    current_os = get_os_name()

    print(f"\n{BOLD}{CYAN}Project Suite Status ({current_os}):{RESET} {cwd}")
    print("=" * 65)

    git_dir = cwd / ".git"
    agents_dir = cwd / ".agents"
    agents_md = cwd / "AGENTS.md"

    # Check remote origin
    remote_url = None
    if git_dir.exists():
        try:
            res = subprocess.run(["git", "-C", str(cwd), "remote", "get-url", "origin"], capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                remote_url = res.stdout.strip()
        except Exception:
            pass

    if remote_url:
        print(f"  {BOLD}Cloned Repo:{RESET}      {GREEN}{remote_url}{RESET}")
        print(f"  {BOLD}Storage Mode:{RESET}     {GREEN}Direct Cloned Physical Repository (Zero symlinks){RESET}")
    else:
        # Fallback check if attached via legacy metadata
        meta_file = cwd / ".attached_suite.json"
        if meta_file.exists():
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    print(f"  {BOLD}Attached Suite:{RESET}   {YELLOW}{meta.get('suite', 'Unknown')}{RESET} (Legacy)")
            except Exception:
                pass
        else:
            print(f"  {BOLD}Cloned Repo:{RESET}      {YELLOW}None detected in project folder{RESET}")

    # Check if a nested repo folder exists
    nested_folders = [
        d.name for d in cwd.iterdir()
        if d.is_dir() and d.name in ["AcademicSuite", "academic_suite", "Academic_Suite"] and (d / ".git").exists()
    ] if cwd.exists() else []

    if nested_folders:
        print(f"  {BOLD}Folder Structure:{RESET} {RED}Warning: Found nested repo folder: {', '.join(nested_folders)}{RESET}")
    else:
        print(f"  {BOLD}Folder Structure:{RESET} {GREEN}Clean (No separate repo folder; cloned directly to root){RESET}")

    # Check .agents and AGENTS.md
    if agents_dir.exists():
        is_symlink = is_link_path(agents_dir)
        link_type = "Legacy Symlink" if is_symlink else "Physical Cloned Directory"
        color = YELLOW if is_symlink else GREEN
        print(f"  {BOLD}.agents:{RESET}          {color}{link_type}{RESET}")
    else:
        print(f"  {BOLD}.agents:{RESET}          {GRAY}Not present{RESET}")

    if agents_md.exists():
        is_symlink = is_link_path(agents_md)
        link_type = "Legacy Symlink" if is_symlink else "Physical Cloned File"
        color = YELLOW if is_symlink else GREEN
        print(f"  {BOLD}AGENTS.md:{RESET}        {color}{link_type}{RESET}")
    else:
        print(f"  {BOLD}AGENTS.md:{RESET}        {GRAY}Not present{RESET}")

    # Count active skills
    skills_dir = cwd / ".agents" / "skills"
    if skills_dir.exists():
        skills = [s.name for s in skills_dir.iterdir() if s.is_dir()]
        print(f"  {BOLD}Active Skills:{RESET}    {len(skills)} skills available in project")

    # Check Git working tree
    if git_dir.exists():
        try:
            res = subprocess.run(["git", "-C", str(cwd), "status", "-s"], capture_output=True, text=True)
            changes = res.stdout.strip().splitlines() if res.stdout.strip() else []
            if changes:
                print(f"  {BOLD}Git Working Tree:{RESET}{YELLOW} {len(changes)} modified/untracked file(s){RESET}")
            else:
                print(f"  {BOLD}Git Working Tree:{RESET}{GREEN} Clean working tree (Up to date with origin/main){RESET}")
        except Exception:
            pass
    else:
        print(f"\n  {YELLOW}Tip: Run 'attach-suite attach' to clone AcademicSuite directly into this project.{RESET}")

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
    meta_info = {}

    if has_meta:
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                meta_info = json.load(f)
        except Exception:
            pass

    attached_items_from_meta = meta_info.get("attached_items", [])
    created_git = meta_info.get("created_git", True)
    previous_origin = meta_info.get("previous_origin", None)

    git_dir = cwd / ".git"
    has_git = git_dir.exists()

    git_tracked_items = []
    is_suite_git = False
    if has_git:
        try:
            res_remote = subprocess.run(["git", "-C", str(cwd), "remote", "get-url", "origin"], capture_output=True, text=True)
            if res_remote.returncode == 0 and res_remote.stdout.strip():
                remote_url = res_remote.stdout.strip()
                for s_key, s_info in suites.items():
                    s_url = s_info.get("repo_url", "")
                    s_path = s_info.get("path", "")
                    if s_url and (remote_url == s_url or remote_url.rstrip("/").endswith("/" + s_key) or remote_url.rstrip("/").endswith(Path(s_path).name)):
                        is_suite_git = True
                        break
                    if s_path and Path(remote_url).resolve() == Path(s_path).resolve():
                        is_suite_git = True
                        break
                if not is_suite_git and "academicsuite" in remote_url.lower():
                    is_suite_git = True

            ls_res = subprocess.run(["git", "-C", str(cwd), "ls-tree", "--name-only", "HEAD"], capture_output=True, text=True)
            if ls_res.returncode == 0 and ls_res.stdout.strip():
                git_tracked_items = [line.strip() for line in ls_res.stdout.strip().splitlines() if line.strip()]
        except Exception:
            pass

    # Items to check and detach
    items_to_detach = set(attached_items_from_meta)
    if is_suite_git or has_meta:
        items_to_detach.update(git_tracked_items)

    default_candidates = [
        ".agents", "AGENTS.md", "ANTIGRAVITY_ARCHITECTURE_GUIDE.md",
        "Questionnaires.xlsx", "digital_saber.py", "digital_broker.py",
        "agents", "data", "docs", "evals", "factory", "recovery",
        "scripts", "tests", "validators", "webapp", "requirements.txt",
        "run_tests.py", "SETUP_GUIDE.md", "README.md", ".github", ".gemini", ".gitignore"
    ]

    if has_meta or is_suite_git or (cwd / ".agents").exists():
        for candidate in default_candidates:
            if candidate in git_tracked_items or candidate in attached_items_from_meta:
                items_to_detach.add(candidate)
            elif not has_git and (cwd / candidate).exists():
                p = cwd / candidate
                if is_link_path(p):
                    items_to_detach.add(candidate)
                elif candidate in [".agents", "AGENTS.md", "ANTIGRAVITY_ARCHITECTURE_GUIDE.md"]:
                    items_to_detach.add(candidate)

    removed = []

    for item_name in sorted(items_to_detach):
        if item_name in [".git", ".", ".."]:
            continue

        p = cwd / item_name
        if not p.exists() and not is_link_path(p):
            continue

        if is_link_path(p):
            remove_link(p, allow_delete_dir=p.is_dir())
            removed.append(f"{item_name} (link)")
        elif p.is_dir():
            if item_name in [".agents", ".gemini", ".github"]:
                try:
                    shutil.rmtree(p)
                    removed.append(f"{item_name}/ (directory)")
                except Exception as e:
                    print(f"{YELLOW}Could not remove directory {item_name}: {e}{RESET}")
            else:
                # Check if directory has untracked user files
                untracked_user_files = []
                if has_git:
                    try:
                        res_untracked = subprocess.run(
                            ["git", "-C", str(cwd), "ls-files", "--others", "--exclude-standard", item_name],
                            capture_output=True, text=True
                        )
                        if res_untracked.returncode == 0 and res_untracked.stdout.strip():
                            untracked_user_files = res_untracked.stdout.strip().splitlines()
                    except Exception:
                        pass

                if untracked_user_files:
                    # Directory contains user-created untracked files: only remove tracked suite files
                    try:
                        res_tracked = subprocess.run(
                            ["git", "-C", str(cwd), "ls-files", item_name],
                            capture_output=True, text=True
                        )
                        if res_tracked.returncode == 0 and res_tracked.stdout.strip():
                            for tf in res_tracked.stdout.strip().splitlines():
                                tf_path = cwd / tf.strip()
                                if tf_path.is_symlink() or tf_path.is_file():
                                    try:
                                        tf_path.unlink()
                                    except Exception:
                                        pass
                        # Clean up any newly empty subdirectories left
                        for dirpath, dirnames, filenames in os.walk(str(p), topdown=False):
                            if not dirnames and not filenames:
                                try:
                                    os.rmdir(dirpath)
                                except OSError:
                                    pass
                        removed.append(f"{item_name}/ (cleaned suite files, preserved {len(untracked_user_files)} user file(s))")
                    except Exception as e:
                        print(f"{YELLOW}Could not clean suite files in {item_name}: {e}{RESET}")
                else:
                    # Directory contains only suite files: safe to rmtree
                    try:
                        shutil.rmtree(p)
                        removed.append(f"{item_name}/ (directory)")
                    except Exception as e:
                        print(f"{YELLOW}Could not remove directory {item_name}: {e}{RESET}")
        elif p.is_file() or p.is_symlink():
            try:
                p.unlink()
                removed.append(f"{item_name} (file)")
            except Exception as e:
                print(f"{YELLOW}Could not remove file {item_name}: {e}{RESET}")

    # Detach Git repository
    keep_git = getattr(args, "keep_git", False)
    if has_git and not keep_git:
        if created_git or is_suite_git:
            if previous_origin and not created_git:
                try:
                    subprocess.run(["git", "-C", str(cwd), "remote", "set-url", "origin", previous_origin], check=True)
                    removed.append(f"restored original Git remote origin ({previous_origin})")
                except Exception as e:
                    print(f"{YELLOW}Could not restore Git remote: {e}{RESET}")
            else:
                try:
                    if is_link_path(git_dir):
                        remove_link(git_dir, allow_delete_dir=True)
                    else:
                        shutil.rmtree(git_dir)
                    removed.append(".git/ (detached Git repository)")
                except Exception as e:
                    print(f"{YELLOW}Could not remove .git directory: {e}{RESET}")
        elif previous_origin:
            try:
                subprocess.run(["git", "-C", str(cwd), "remote", "set-url", "origin", previous_origin], check=True)
                removed.append(f"restored original Git remote origin ({previous_origin})")
            except Exception as e:
                print(f"{YELLOW}Could not restore Git remote: {e}{RESET}")

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
        print(f"\n{YELLOW}No active suite links, files, or attached Git repositories found to detach in: {cwd}{RESET}")
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

    repo_url = "https://github.com/GhaderiSaber/AcademicSuite.git"
    offline_mode = getattr(args, "offline", False) or os.environ.get("ACADEMIC_SUITE_OFFLINE") == "1"
    if Path(str(suite_arg)).exists() and (Path(str(suite_arg)) / ".git").exists():
        repo_url = str(Path(str(suite_arg)).resolve())
    elif offline_mode and suite_info and suite_info.get("path") and (Path(suite_info["path"]) / ".git").exists():
        repo_url = str(Path(suite_info["path"]).resolve())
    elif suite_info and suite_info.get("repo_url"):
        repo_url = suite_info["repo_url"]
    elif suite_arg.startswith("http://") or suite_arg.startswith("https://") or suite_arg.startswith("git@"):
        repo_url = suite_arg

    suite_title = suite_info["name"] if suite_info else "Academic Thesis & Statistical Consultancy Suite"

    # Guard: Check if cwd is already the master suite repository
    if suite_info and suite_info.get("path"):
        try:
            local_suite_path = Path(suite_info["path"]).resolve()
            if cwd.resolve() == local_suite_path:
                print(f"\n{BOLD}{GREEN}Notice: Current directory is already the master suite repository ({suite_title})!{RESET}")
                print(f"  Location: {cwd}")
                print(f"  Nothing to attach. Checking Git status...\n")
                subprocess.run(["git", "-C", str(cwd), "status", "-s"], check=False)
                return
        except Exception:
            pass

    current_os = get_os_name()
    print(f"\n{BOLD}{CYAN}Cloning Suite Repository into Project ({current_os}):{RESET} {BOLD}{suite_title}{RESET}")
    print(f"  Repo URL:       {repo_url}")
    print(f"  Target Project: {cwd}")
    print(f"  Mode:           Direct Git Clone into project root (zero symlinks, zero subfolders)\n")

    # Step 1: Clean up any previous symbolic links created by attach-suite
    cleaned_symlinks = []
    try:
        for item in cwd.iterdir():
            if is_link_path(item):
                try:
                    remove_link(item, allow_delete_dir=item.is_dir())
                    cleaned_symlinks.append(item.name)
                except Exception:
                    pass
    except Exception:
        pass

    if cleaned_symlinks:
        print(f"{GRAY}Removed {len(cleaned_symlinks)} legacy symbolic links: {', '.join(cleaned_symlinks)}{RESET}")

    # Remove old .attached_suite.json if it was from symlink mode
    old_meta = cwd / ".attached_suite.json"
    if old_meta.exists():
        try:
            old_meta.unlink()
        except Exception:
            pass

    # Step 2: Clean Google Drive lock files if any
    clean_conflicts_and_locks(cwd)

    # Step 3: Clone repository directly into cwd without creating a separate subfolder
    git_dir = cwd / ".git"
    had_existing_git = git_dir.exists()
    existing_origin = None
    if had_existing_git:
        try:
            res_orig = subprocess.run(["git", "-C", str(cwd), "remote", "get-url", "origin"], capture_output=True, text=True)
            if res_orig.returncode == 0 and res_orig.stdout.strip():
                existing_origin = res_orig.stdout.strip()
        except Exception:
            pass

    def _clone_or_update(target_url: str):
        if git_dir.exists():
            print(f"{CYAN}Existing Git repository detected in project. Updating from {target_url}...{RESET}")
            remotes = subprocess.run(["git", "-C", str(cwd), "remote"], capture_output=True, text=True).stdout.split()
            if "origin" in remotes:
                subprocess.run(["git", "-C", str(cwd), "remote", "set-url", "origin", target_url], check=True)
            else:
                subprocess.run(["git", "-C", str(cwd), "remote", "add", "origin", target_url], check=True)
            fetch_res = subprocess.run(["git", "-C", str(cwd), "fetch", "origin", "main"], capture_output=True, text=True)
            if fetch_res.returncode != 0:
                subprocess.run(["git", "-C", str(cwd), "fetch", "--depth", "1", "origin", "main"], check=True)
            subprocess.run(["git", "-C", str(cwd), "checkout", "-f", "-B", "main", "origin/main"], check=True)
            subprocess.run(["git", "-C", str(cwd), "branch", "--set-upstream-to=origin/main", "main"], check=False)
        else:
            items = [f for f in cwd.iterdir() if f.name != ".git"]
            if not items:
                print(f"{CYAN}Cloning repository into empty project directory...{RESET}")
                subprocess.run(["git", "clone", target_url, "."], cwd=str(cwd), check=True)
            else:
                init_res = subprocess.run(["git", "init", "-b", "main", "."], cwd=str(cwd), capture_output=True, text=True)
                if init_res.returncode != 0:
                    subprocess.run(["git", "init", "."], cwd=str(cwd), check=True)
                subprocess.run(["git", "remote", "add", "origin", target_url], cwd=str(cwd), check=True)
                fetch_res = subprocess.run(["git", "fetch", "origin", "main"], cwd=str(cwd), capture_output=True, text=True)
                if fetch_res.returncode != 0:
                    subprocess.run(["git", "fetch", "--depth", "1", "origin", "main"], cwd=str(cwd), check=True)
                subprocess.run(["git", "checkout", "-f", "-B", "main", "origin/main"], cwd=str(cwd), check=True)
                subprocess.run(["git", "branch", "--set-upstream-to=origin/main", "main"], cwd=str(cwd), check=False)

    try:
        _clone_or_update(repo_url)
    except subprocess.CalledProcessError as e:
        local_path = suite_info.get("path") if suite_info else None
        if local_path and (Path(local_path) / ".git").exists() and repo_url != str(Path(local_path).resolve()):
            local_repo = str(Path(local_path).resolve())
            print(f"\n{YELLOW}Warning: Remote git operation failed from {repo_url}.{RESET}")
            print(f"{CYAN}Attempting offline fallback to local suite repository at {local_repo}...{RESET}\n")
            try:
                _clone_or_update(local_repo)
            except subprocess.CalledProcessError as err_local:
                print(f"\n{RED}Error cloning repository from local fallback {local_repo}: {err_local}{RESET}\n", file=sys.stderr)
                sys.exit(err_local.returncode)
        else:
            print(f"\n{RED}Error cloning repository from {repo_url}: {e}{RESET}\n", file=sys.stderr)
            sys.exit(e.returncode)

    # Record attached suite metadata for clean detachment and status inspection
    attached_items = []
    if git_dir.exists():
        try:
            ls_res = subprocess.run(
                ["git", "-C", str(cwd), "ls-tree", "--name-only", "HEAD"],
                capture_output=True, text=True
            )
            if ls_res.returncode == 0 and ls_res.stdout.strip():
                attached_items = [line.strip() for line in ls_res.stdout.strip().splitlines() if line.strip()]
        except Exception:
            pass

    if not attached_items:
        fallback_candidates = [
            ".agents", "AGENTS.md", "ANTIGRAVITY_ARCHITECTURE_GUIDE.md",
            "Questionnaires.xlsx", "digital_saber.py", "digital_broker.py",
            "requirements.txt", "run_tests.py", "SETUP_GUIDE.md", "README.md",
            ".gitignore", ".github", ".gemini", "docs", "evals", "tests", "webapp"
        ]
        attached_items = [name for name in fallback_candidates if (cwd / name).exists()]

    meta = {
        "suite": suite_key or "academic",
        "name": suite_title,
        "repo_url": repo_url,
        "attached_at": datetime.now().isoformat(),
        "created_git": not had_existing_git,
        "previous_origin": existing_origin,
        "attached_items": attached_items
    }
    try:
        with open(cwd / ".attached_suite.json", "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
    except Exception as e:
        print(f"{YELLOW}Warning: Could not save .attached_suite.json: {e}{RESET}")

    # Count active skills
    skills_dir = cwd / ".agents" / "skills"
    skills = [s.name for s in skills_dir.iterdir() if s.is_dir()] if skills_dir.exists() else []

    print(f"\n{BOLD}{GREEN}✓ Successfully cloned GitHub repository directly into project!{RESET}")
    print(f"  {BOLD}Project Location:{RESET} {cwd}")
    print(f"  {BOLD}Active Skills:{RESET}   {len(skills)} skills loaded directly from project")
    print(f"  {BOLD}Structure:{RESET}       Real physical repository files (zero symlinks, zero subfolders)\n")


def get_project_or_suite_repo(cwd: Path) -> Path:
    """Returns cwd if it is a Git repo, otherwise the attached suite repo path."""
    if (cwd / ".git").exists():
        return cwd
    suite = get_attached_suite_path(cwd)
    if suite and (suite / ".git").exists():
        return suite
    return None


def cmd_git_passthrough(args, unknown_args):
    """Runs any arbitrary git command against the project repository (or master suite)."""
    cwd = get_cwd()
    repo_path = get_project_or_suite_repo(cwd)
    if not repo_path:
        print(f"{RED}Error: No Git repository found in {cwd}.{RESET}", file=sys.stderr)
        sys.exit(1)

    cmd = ["git", "-C", str(repo_path)] + unknown_args
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)


def cmd_push(args):
    """Stages changes in the project repository, commits them, and pushes to remote."""
    cwd = get_cwd()
    repo_path = get_project_or_suite_repo(cwd)
    if not repo_path:
        print(f"{RED}Error: No Git repository found in {cwd}.{RESET}", file=sys.stderr)
        sys.exit(1)

    print(f"\n{BOLD}{CYAN}Pushing Updates to GitHub:{RESET} {repo_path}\n")

    st = subprocess.run(["git", "-C", str(repo_path), "status", "-s"], capture_output=True, text=True)
    if not st.stdout.strip():
        print(f"{GREEN}✓ No changes detected. Everything is up to date!{RESET}\n")
        return

    print(f"{GRAY}Changed files:{RESET}")
    for line in st.stdout.strip().splitlines():
        print(f"  {line}")

    print(f"\n{CYAN}Staging changes...{RESET}")
    subprocess.run(["git", "-C", str(repo_path), "add", "-A"], check=True)

    msg = args.message
    if not msg:
        project_name = cwd.name
        msg = f"chore: update project {project_name}"

    print(f"{CYAN}Committing: {RESET}\"{msg}\"")
    subprocess.run(["git", "-C", str(repo_path), "commit", "-m", msg], check=True)

    print(f"{CYAN}Pushing to GitHub (origin main)...{RESET}")
    subprocess.run(["git", "-C", str(repo_path), "push", "origin", "main"], check=True)
    print(f"\n{BOLD}{GREEN}✓ Successfully committed and pushed updates to GitHub!{RESET}\n")


def cmd_pull(args):
    """Pulls latest remote changes from GitHub into the project."""
    cwd = get_cwd()
    repo_path = get_project_or_suite_repo(cwd)
    if not repo_path:
        print(f"{RED}Error: No Git repository found in {cwd}.{RESET}", file=sys.stderr)
        sys.exit(1)

    print(f"\n{BOLD}{CYAN}Pulling Latest Updates from GitHub:{RESET} {repo_path}\n")
    subprocess.run(["git", "-C", str(repo_path), "pull", "origin", "main"], check=True)
    print(f"\n{BOLD}{GREEN}✓ Repository is now up to date with remote!{RESET}\n")


def cmd_diff(args):
    """Shows git diff on the project repository."""
    cwd = get_cwd()
    repo_path = get_project_or_suite_repo(cwd)
    if not repo_path:
        print(f"{RED}Error: No Git repository found in {cwd}.{RESET}", file=sys.stderr)
        sys.exit(1)

    subprocess.run(["git", "-C", str(repo_path), "diff"] + (args.extra or []))


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
    p_attach.add_argument("--offline", action="store_true", help="Attach from local suite repository without network calls")
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
    p_detach.add_argument("--keep-git", action="store_true", help="Do not remove or decouple the .git directory when detaching")

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
