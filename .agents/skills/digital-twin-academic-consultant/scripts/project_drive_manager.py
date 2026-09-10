#!/usr/bin/env python3
"""
Academic Google Drive Project Manager (project_drive_manager.py)
----------------------------------------------------------------
Automates project folder provisioning, live chat archival, and artifact
management for clients interacting with Saber Ghaderi's Telethon Userbot.

Key Responsibilities:
1. Dynamically discovers Google Drive 'My Work' / 'My Works' operational root.
2. Provisions standard 4-tier project folders (01_raw_inputs, 02_analysis_code,
   03_deliverables, 04_references_and_lit) matching academic-drive-project-organizer.
3. Automatically downloads and stores client files/attachments into 01_raw_inputs/.
4. Formats and persists chat history (chat_history.json & chat_transcript.md).
5. Synthesizes client profile dossiers (client_profile.md) and project_meta.json.
"""

import os
import re
import sys
import glob
import json
import html
import shutil
import difflib
import unicodedata
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

# Standard 4-Tier Subfolder Taxonomy
SUBFOLDERS = {
    "raw": "01_raw_inputs",
    "code": "02_analysis_code",
    "deliverables": "03_deliverables",
    "deliverables_archive": "03_deliverables/drafts_archive",
    "references": "04_references_and_lit"
}

DEFAULT_MACOS_DRIVE_CANDIDATES = [
    "/Users/saber/Library/CloudStorage/GoogleDrive-ghaderi.sabir@gmail.com/My Drive/My Work",
    "/Users/saber/Library/CloudStorage/GoogleDrive-ghaderi.sabir@gmail.com/My Drive/My Works",
    "/Users/saber/Desktop/academic_suite/projects"
]


def sanitize_filename(name: str) -> str:
    """Remove unsafe filesystem characters from name."""
    if not name:
        return "Unnamed_Client"
    cleaned = re.sub(r'[\\/*?:"<>|]', "", name).strip()
    return cleaned or "Unnamed_Client"


def clean_drive_display_path(full_path: str) -> str:
    """
    Convert full local CloudStorage or filesystem path into a clean, concise Google Drive display path.
    Example:
      '/Users/saber/Library/CloudStorage/GoogleDrive-ghaderi.sabir@gmail.com/My Drive/My Work/Zəhra Cəlalı'
      -> 'My Work/Zəhra Cəlalı'
    """
    if not full_path:
        return ""
    normalized = full_path.replace("\\", "/")
    
    # Strip everything up to "My Drive/"
    marker = "My Drive/"
    idx = normalized.find(marker)
    if idx != -1:
        rel = normalized[idx + len(marker):].strip("/")
        if rel:
            return rel

    # Strip CloudStorage account prefix if present
    cloud_marker = "CloudStorage/"
    c_idx = normalized.find(cloud_marker)
    if c_idx != -1:
        parts = normalized[c_idx + len(cloud_marker):].split("/")
        if len(parts) > 2:
            return "/".join(parts[2:]).strip("/")

    # Fallback to last two directories (e.g. "My Work/Client Folder")
    parts = [p for p in normalized.split("/") if p]
    if len(parts) >= 2:
        return f"{parts[-2]}/{parts[-1]}"
    return parts[-1] if parts else full_path


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
    """
    Check if two client names match across Azerbaijani, English, or Persian transliterations.
    Returns (is_match, similarity_score).
    """
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


def resolve_media_details(msg) -> Tuple[Optional[str], Optional[str], int, int]:
    """
    Extract (file_name, media_type, file_size, duration) for a Telegram message.
    Returns (None, None, 0, 0) if message has no media or is an animated/static sticker.
    media_type is one of: 'document', 'voice', 'photo', 'video_note', 'sticker', None.
    """
    if not msg or not msg.file:
        return None, None, 0, 0

    # 1. Filter out stickers
    if getattr(msg, "sticker", None):
        return None, "sticker", getattr(msg.file, "size", 0), 0
    mime = getattr(msg.file, "mime_type", "") or ""
    if "tgsticker" in mime or mime == "image/webp":
        raw_n = getattr(msg.file, "name", "") or ""
        if raw_n.endswith(".tgs") or not raw_n:
            return None, "sticker", getattr(msg.file, "size", 0), 0

    size = getattr(msg.file, "size", 0)
    msg_date = msg.date.strftime("%Y%m%d_%H%M%S") if getattr(msg, "date", None) else "date"

    # 2. Voice note
    if getattr(msg, "voice", None):
        duration = 0
        attrs = getattr(msg.voice, "attributes", []) or getattr(msg.file, "attrs", []) or []
        for attr in attrs:
            if hasattr(attr, "duration"):
                duration = attr.duration
                break
        ext = getattr(msg.file, "ext", None) or ".ogg"
        fname = f"voice_{msg.id}_{msg_date}{ext}"
        return sanitize_filename(fname), "voice", size, duration

    # 3. Photo
    if getattr(msg, "photo", None):
        ext = getattr(msg.file, "ext", None) or ".jpg"
        fname = f"photo_{msg.id}_{msg_date}{ext}"
        return sanitize_filename(fname), "photo", size, 0

    # 4. Video note
    if getattr(msg, "video_note", None):
        duration = 0
        attrs = getattr(msg.file, "attrs", []) or []
        for attr in attrs:
            if hasattr(attr, "duration"):
                duration = attr.duration
                break
        ext = getattr(msg.file, "ext", None) or ".mp4"
        fname = f"videonote_{msg.id}_{msg_date}{ext}"
        return sanitize_filename(fname), "video_note", size, duration

    # 5. Named file document
    raw_name = getattr(msg.file, "name", None)
    if raw_name:
        fname = sanitize_filename(raw_name)
        if fname.lower().endswith(".tgs"):
            return None, "sticker", size, 0
        return fname, "document", size, 0

    # 6. Unnamed document fallback
    ext = getattr(msg.file, "ext", None) or ""
    fname = f"attachment_{msg.id}_{msg_date}{ext}"
    return sanitize_filename(fname), "document", size, 0


def format_client_mention_html(client_name: str, username: Optional[str] = None, client_id: Optional[int] = None) -> str:
    """
    Format a clean, clickable Telegram HTML mention for a client.
    When tapped, Telegram directly opens the DM chat with that client.
    Eliminates raw ID noise.
    """
    safe_name = html.escape(client_name or "Client")
    clean_username = (username or "").lstrip("@").strip()
    
    if clean_username:
        return f'<a href="https://t.me/{clean_username}"><b>{safe_name}</b></a> (@{clean_username})'
    elif client_id:
        return f'<a href="tg://user?id={client_id}"><b>{safe_name}</b></a>'
    else:
        return f'<b>{safe_name}</b>'


def resolve_google_drive_work_dir(config: Optional[Dict[str, Any]] = None) -> str:
    """
    Locate Google Drive 'My Work' operational directory.
    Checks config -> environment variable -> macOS CloudStorage -> fallback.
    """
    if config and config.get("google_drive_work_dir"):
        custom_dir = config["google_drive_work_dir"]
        if os.path.exists(custom_dir):
            return custom_dir

    env_dir = os.environ.get("GOOGLE_DRIVE_WORK_DIR")
    if env_dir and os.path.exists(env_dir):
        return env_dir

    # Check known candidates
    for cand in DEFAULT_MACOS_DRIVE_CANDIDATES:
        if os.path.exists(cand):
            return cand

    # Pattern search in CloudStorage
    cloud_storage_root = "/Users/saber/Library/CloudStorage"
    if os.path.exists(cloud_storage_root):
        matches = glob.glob(os.path.join(cloud_storage_root, "*", "My Drive", "My Work*"))
        if matches:
            return matches[0]

    # Fallback to local userbot_storage/projects
    fallback_dir = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "userbot_storage", "projects")
    )
    os.makedirs(fallback_dir, exist_ok=True)
    return fallback_dir


class ProjectDriveManager:
    """Manages creation, syncing, and archival of client projects on Google Drive."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.work_dir = resolve_google_drive_work_dir(self.config)
        os.makedirs(self.work_dir, exist_ok=True)

    def load_ignored_registry(self) -> Dict[str, Any]:
        """Load persistent exclusion registry of non-academic contacts."""
        reg_file = os.path.join(os.path.dirname(__file__), "userbot_storage", "ignored_non_projects.json")
        if os.path.exists(reg_file):
            try:
                with open(reg_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"telegram_ids": [], "usernames": [], "folder_names": []}

    def load_vip_registry(self) -> Dict[str, Any]:
        """Load persistent VIP/repeat client registry."""
        vip_file = os.path.join(os.path.dirname(__file__), "userbot_storage", "vip_clients.json")
        if os.path.exists(vip_file):
            try:
                with open(vip_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"vip_clients": []}

    def is_vip_client(self, client_name: str, client_id: Optional[int] = None, username: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Check if contact is a designated VIP/repeat collaborator."""
        vip_reg = self.load_vip_registry()
        for vip in vip_reg.get("vip_clients", []):
            if client_id and vip.get("telegram_id") == client_id:
                return vip
            if username and vip.get("telegram_username") and vip["telegram_username"].lstrip("@").lower() == username.lstrip("@").lower():
                return vip
            if client_name:
                v_name = vip.get("client_name", "")
                v_fa = vip.get("client_name_fa", "")
                m1, _ = match_client_names(client_name, v_name)
                m2, _ = match_client_names(client_name, v_fa)
                if m1 or m2:
                    return vip
        return None

    def is_ignored(self, client_name: str, client_id: Optional[int] = None, username: Optional[str] = None) -> bool:
        """Check if a contact is in the excluded non-academic contacts registry."""
        # VIP clients are NEVER ignored
        if self.is_vip_client(client_name, client_id, username):
            return False

        reg = self.load_ignored_registry()
        if client_id and client_id in reg.get("telegram_ids", []):
            return True
        if username and username.lstrip("@").lower() in reg.get("usernames", []):
            return True
        if client_name:
            for fn in reg.get("folder_names", []):
                matched, _ = match_client_names(client_name, fn)
                if matched:
                    return True
        return False

    def find_existing_project_by_client(
        self, client_name: str, client_id: Optional[int] = None, username: Optional[str] = None
    ) -> Optional[str]:
        """
        Check if a project folder already exists for this client by folder name,
        phonetic match across Azerbaijani/English, Telegram ID, Telegram username,
        or VIP umbrella directory across My Work, Pending Works, and Finished Works.
        """
        # 1. VIP Umbrella Directory check
        vip = self.is_vip_client(client_name, client_id, username)
        if vip and vip.get("umbrella_dir") and os.path.isdir(vip["umbrella_dir"]):
            return vip["umbrella_dir"]

        drive_root = os.path.dirname(self.work_dir)
        search_roots = [
            self.work_dir,
            os.path.join(self.work_dir, "Pending Works"),
            os.path.join(drive_root, "Pending Works"),
            os.path.join(drive_root, "Finished Works")
        ]
        valid_roots = [r for r in search_roots if os.path.isdir(r)]
        if not valid_roots:
            return None

        clean_name = sanitize_filename(client_name)

        # 2. Check exact path in work_dir first
        exact_path = os.path.join(self.work_dir, clean_name)
        if os.path.isdir(exact_path):
            return exact_path

        # 3. Search across all valid roots (My Work, Pending Works, Finished Works)
        best_match = None
        highest_score = 0.0

        for root in valid_roots:
            for folder in os.listdir(root):
                folder_path = os.path.join(root, folder)
                if not os.path.isdir(folder_path) or folder.startswith("."):
                    continue

                if folder == "Pending Works":
                    continue

                meta_file = os.path.join(folder_path, "project_meta.json")
                if os.path.exists(meta_file):
                    try:
                        with open(meta_file, "r", encoding="utf-8") as f:
                            meta = json.load(f)
                        if client_id and meta.get("telegram_id") == client_id:
                            return folder_path
                        if username and meta.get("telegram_username"):
                            cur_user = meta["telegram_username"].lstrip("@").lower()
                            if cur_user == username.lstrip("@").lower():
                                return folder_path
                        if meta.get("client_name_az"):
                            m, s = match_client_names(client_name, meta["client_name_az"])
                            if m and s > highest_score:
                                highest_score = s
                                best_match = folder_path
                        if meta.get("client_name"):
                            m, s = match_client_names(client_name, meta["client_name"])
                            if m and s > highest_score:
                                highest_score = s
                                best_match = folder_path
                    except Exception:
                        pass

                # Phonetic and fuzzy match against folder name
                is_match, score = match_client_names(client_name, folder)
                if is_match and score > highest_score:
                    highest_score = score
                    best_match = folder_path

        if best_match and highest_score >= 0.85:
            return best_match

        return None

    def provision_project(
        self,
        client_name: str,
        client_id: Optional[int] = None,
        username: Optional[str] = None,
        phone: Optional[str] = None,
        topic: Optional[str] = None,
        status: str = "inquiry"
    ) -> Dict[str, str]:
        """
        Create or get standardized 4-tier project folder in Google Drive.
        If the client is a VIP with an Umbrella Directory, automatically routes
        to or provisions subprojects (P01, P02, P03...) under the master umbrella folder.
        Returns dictionary of paths.
        """
        clean_name = sanitize_filename(client_name)
        existing_dir = self.find_existing_project_by_client(clean_name, client_id, username)

        # Check if existing directory is a Master Umbrella Client Folder
        is_umbrella = False
        umbrella_meta = {}
        if existing_dir:
            u_meta_file = os.path.join(existing_dir, "project_meta.json")
            if os.path.exists(u_meta_file):
                try:
                    with open(u_meta_file, "r", encoding="utf-8") as f:
                        umbrella_meta = json.load(f)
                        is_umbrella = bool(umbrella_meta.get("is_umbrella_client_folder"))
                except Exception:
                    pass

        if is_umbrella and existing_dir:
            umbrella_dir = existing_dir
            comm_dir = os.path.join(umbrella_dir, "00_general_communications")
            os.makedirs(comm_dir, exist_ok=True)

            # Determine target subproject under umbrella
            subprojects = umbrella_meta.get("active_subprojects", [])
            target_sub_dir = None

            if topic:
                clean_topic = sanitize_filename(topic)
                # Check if an existing subproject matches topic
                for sp in subprojects:
                    folder = sp.get("folder", "")
                    if clean_topic.lower() in folder.lower() or folder.lower() in clean_topic.lower():
                        target_sub_dir = os.path.join(umbrella_dir, folder)
                        break

                if not target_sub_dir:
                    # Provision new numbered subproject e.g. P04_NewTopic
                    next_idx = len(subprojects) + 1
                    sub_name = f"P{next_idx:02d}_{clean_topic}"
                    target_sub_dir = os.path.join(umbrella_dir, sub_name)
                    os.makedirs(target_sub_dir, exist_ok=True)

                    subprojects.append({
                        "id": f"P{next_idx:02d}",
                        "folder": sub_name,
                        "status": status,
                        "title": topic
                    })
                    umbrella_meta["active_subprojects"] = subprojects
                    umbrella_meta["updated_at"] = datetime.now().isoformat()
                    with open(u_meta_file, "w", encoding="utf-8") as f:
                        json.dump(umbrella_meta, f, ensure_ascii=False, indent=2)
            else:
                # Default to the most recent subproject, or P01
                if subprojects:
                    latest = subprojects[-1]
                    target_sub_dir = os.path.join(umbrella_dir, latest.get("folder", "P01_Default"))
                else:
                    target_sub_dir = os.path.join(umbrella_dir, "P01_Main_Project")
                os.makedirs(target_sub_dir, exist_ok=True)

            # Ensure 4 standard tiers inside subproject
            paths = {
                "root": target_sub_dir,
                "umbrella_root": umbrella_dir,
                "general_comm": comm_dir
            }
            for key, sub in SUBFOLDERS.items():
                sub_path = os.path.join(target_sub_dir, sub)
                os.makedirs(sub_path, exist_ok=True)
                paths[key] = sub_path

            meta_file = os.path.join(target_sub_dir, "project_meta.json")
            if not os.path.exists(meta_file):
                now_iso = datetime.now().isoformat()
                sub_meta = {
                    "client_name": clean_name,
                    "umbrella_dir": umbrella_dir,
                    "topic_fa": topic or "پروژه فعال",
                    "status": status,
                    "created_at": now_iso,
                    "updated_at": now_iso
                }
                with open(meta_file, "w", encoding="utf-8") as f:
                    json.dump(sub_meta, f, ensure_ascii=False, indent=2)
            paths["meta_file"] = meta_file
            return paths

        # Standard non-umbrella project provisioning
        if existing_dir:
            project_dir = existing_dir
        else:
            folder_name = f"{clean_name} - {sanitize_filename(topic)}" if topic else clean_name
            project_dir = os.path.join(self.work_dir, folder_name)
            os.makedirs(project_dir, exist_ok=True)

        # Ensure all 4-tier subdirectories exist
        paths = {"root": project_dir}
        for key, sub in SUBFOLDERS.items():
            sub_path = os.path.join(project_dir, sub)
            os.makedirs(sub_path, exist_ok=True)
            paths[key] = sub_path

        # Load or initialize project_meta.json
        meta_file = os.path.join(project_dir, "project_meta.json")
        meta = {}
        if os.path.exists(meta_file):
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
            except Exception:
                meta = {}

        now_iso = datetime.now().isoformat()
        meta.setdefault("client_name", clean_name)
        meta.setdefault("client_name_fa", clean_name)
        meta["client_name_az"] = client_name
        meta["folder_name"] = os.path.basename(project_dir)
        if client_id:
            meta["telegram_id"] = client_id
        if username:
            meta["telegram_username"] = f"@{username.lstrip('@')}"
        if phone:
            meta["phone"] = phone
        if topic and not meta.get("topic_fa"):
            meta["topic_fa"] = topic
        meta.setdefault("status", status)
        meta.setdefault("created_at", now_iso)
        meta["updated_at"] = now_iso
        meta.setdefault("files", [])
        meta.setdefault("stages", {
            "proposal": "topic_and_scale_selection",
            "methodology_drafting": "pending",
            "data_collection": "pending",
            "analysis": "pending",
            "deliverables": "pending"
        })

        with open(meta_file, "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        paths["meta_file"] = meta_file
        return paths

    async def save_client_chat_and_files(
        self,
        client,
        entity,
        client_name: str,
        client_id: Optional[int] = None,
        username: Optional[str] = None,
        limit_messages: int = 150,
        download_files: bool = True
    ) -> Dict[str, Any]:
        """
        Crawl chat with client, save full history (JSON & Markdown transcript),
        download sent files into 01_raw_inputs/, and extract topic/scale clues.
        """
        # If contact is in ignored registry and has no existing project on disk, verify if there are real research attachments
        if self.is_ignored(client_name, client_id, username):
            existing = self.find_existing_project_by_client(client_name, client_id, username)
            if not existing:
                has_documents = False
                async for msg in client.iter_messages(entity, limit=min(limit_messages, 40)):
                    fn, _, _, _ = resolve_media_details(msg)
                    if fn:
                        ext = os.path.splitext(fn)[1].lower()
                        if ext in [".docx", ".doc", ".pdf", ".sav", ".xlsx", ".xls", ".csv", ".rar", ".zip", ".ogg"]:
                            has_documents = True
                            break
                    if len(msg.message or "") > 80 and any(w in (msg.message or "") for w in ["عنوان", "فرضیه", "پروپوزال", "جامعه", "نمونه", "متغیر"]):
                        has_documents = True
                        break
                if not has_documents:
                    return {"project_dir": "", "messages_count": 0, "files_count": 0, "skipped_non_project": True}

        paths = self.provision_project(client_name, client_id=client_id, username=username)
        raw_dir = paths["raw"]
        me = await client.get_me()

        print(f"[*] Crawling and archiving chat for {client_name} -> {paths['root']}")
        raw_messages = []
        async for msg in client.iter_messages(entity, limit=limit_messages):
            raw_messages.append(msg)

        # Sort chronologically (oldest to newest)
        raw_messages.reverse()

        parsed_messages = []
        downloaded_files = []
        text_corpus = []

        for msg in raw_messages:
            is_saber = (msg.sender_id == me.id)
            sender_label = "صابر قادری" if is_saber else client_name
            sender_tag = "Saber Ghaderi" if is_saber else "Client"
            msg_text = msg.message or ""
            if msg_text.strip():
                text_corpus.append(msg_text)

            entry = {
                "id": msg.id,
                "date": msg.date.isoformat() if msg.date else None,
                "from_id": f"user{msg.sender_id}" if msg.sender_id else "",
                "from": sender_label,
                "sender_tag": sender_tag,
                "text": msg_text
            }

            # Check and download media/file (documents, voice notes, photos, excluding stickers)
            fname, mtype, fsize, duration = resolve_media_details(msg)
            if fname:
                entry["file_name"] = fname
                entry["media_type"] = mtype
                entry["file_size"] = fsize
                if duration:
                    entry["duration"] = duration

                if download_files and not is_saber:
                    target_file = os.path.join(raw_dir, fname)
                    if not os.path.exists(target_file):
                        type_label = "voice note" if mtype == "voice" else ("photo" if mtype == "photo" else "client file")
                        print(f"    📥 Downloading {type_label}: {fname} ({fsize:,} bytes)...")
                        try:
                            await msg.download_media(file=target_file)
                            downloaded_files.append({
                                "file_name": fname,
                                "file_path": target_file,
                                "size_bytes": fsize,
                                "date": entry["date"],
                                "media_type": mtype,
                                "duration": duration
                            })
                        except Exception as e:
                            print(f"    [-] Failed to download {fname}: {e}")
                    else:
                        downloaded_files.append({
                            "file_name": fname,
                            "file_path": target_file,
                            "size_bytes": fsize,
                            "status": "already_exists",
                            "media_type": mtype
                        })

            parsed_messages.append(entry)

        # 1. Save structured chat_history.json
        chat_json_path = os.path.join(raw_dir, "chat_history.json")
        with open(chat_json_path, "w", encoding="utf-8") as f:
            json.dump(parsed_messages, f, ensure_ascii=False, indent=2)

        # 2. Generate human-readable Persian chat_transcript.md
        transcript_md_path = os.path.join(raw_dir, "chat_transcript.md")
        transcript_lines = [
            f"# رونوشت کامل مکالمات تلگرام — {client_name}",
            "",
            f"- **نام مراجع:** {client_name}",
            f"- **شناسه کاربری تلگرام:** @{username or ''} (ID: `{client_id or ''}`)",
            f"- **تاریخ استخراج:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"- **تعداد کل پیام‌ها:** {len(parsed_messages)}",
            "",
            "---",
            ""
        ]

        for m in parsed_messages:
            sender_icon = "👤 **صابر قادری**" if m["sender_tag"] == "Saber Ghaderi" else f"💬 **{m['from']}**"
            date_str = m["date"][:19].replace("T", " ") if m.get("date") else ""
            transcript_lines.append(f"### {sender_icon} — <small>`{date_str}`</small>")
            if m.get("text"):
                transcript_lines.append(m["text"])
            if m.get("file_name"):
                mtype = m.get("media_type")
                dur = m.get("duration", 0)
                fsize = m.get("file_size", 0)
                if mtype == "voice":
                    dur_str = f"{dur} ثانیه, " if dur else ""
                    transcript_lines.append(f"> 🎤 **پیام صوتی (Voice Note):** [{m['file_name']}]({m['file_name']}) ({dur_str}{fsize:,} بایت)")
                elif mtype == "photo":
                    transcript_lines.append(f"> 📷 **تصویر ضمیمه (Photo):** [{m['file_name']}]({m['file_name']}) ({fsize:,} بایت)")
                elif mtype == "video_note":
                    dur_str = f"{dur} ثانیه, " if dur else ""
                    transcript_lines.append(f"> 📹 **پیام ویدیویی (Video Note):** [{m['file_name']}]({m['file_name']}) ({dur_str}{fsize:,} بایت)")
                else:
                    transcript_lines.append(f"> 📎 **فایل ضمیمه:** [{m['file_name']}]({m['file_name']}) ({fsize:,} بایت)")
            transcript_lines.append("\n---\n")

        with open(transcript_md_path, "w", encoding="utf-8") as f:
            f.write("\n".join(transcript_lines))

        # 3. Extract research topics, scales, and advisor clues
        combined_text = "\n".join(text_corpus)
        extracted_advisor = self._extract_advisor(combined_text)
        extracted_scales = self._extract_scales(combined_text, downloaded_files)
        extracted_topic = self._extract_topic(combined_text)

        # 4. Generate/Update client_profile.md if missing or brief
        profile_md_path = os.path.join(raw_dir, "client_profile.md")
        if not os.path.exists(profile_md_path):
            profile_content = self._format_client_profile(
                client_name=client_name,
                client_id=client_id,
                username=username,
                advisor=extracted_advisor,
                topic=extracted_topic,
                scales=extracted_scales,
                files=downloaded_files,
                project_dir=paths["root"]
            )
            with open(profile_md_path, "w", encoding="utf-8") as f:
                f.write(profile_content)

        # 4b. Also mirror transcripts into umbrella general_comm if available
        if paths.get("general_comm") and os.path.isdir(paths["general_comm"]):
            try:
                shutil.copy2(chat_json_path, os.path.join(paths["general_comm"], "chat_history.json"))
                shutil.copy2(transcript_md_path, os.path.join(paths["general_comm"], "chat_transcript.md"))
                if os.path.exists(profile_md_path):
                    shutil.copy2(profile_md_path, os.path.join(paths["general_comm"], "client_profile.md"))
            except Exception as e:
                print(f"[-] Warning: Failed to mirror to general_comm: {e}")

        # 5. Update project_meta.json
        with open(paths["meta_file"], "r", encoding="utf-8") as f:
            meta = json.load(f)

        if extracted_advisor:
            meta["advisor"] = extracted_advisor
        if extracted_topic:
            meta["topic_fa"] = extracted_topic
        if extracted_scales:
            meta["target_instruments"] = extracted_scales

        meta["message_count"] = len(parsed_messages)
        meta["file_count"] = len(downloaded_files)
        meta["last_interaction"] = parsed_messages[-1]["date"] if parsed_messages else None

        with open(paths["meta_file"], "w", encoding="utf-8") as f:
            json.dump(meta, f, ensure_ascii=False, indent=2)

        print(f"[+] Project updated: {paths['root']} ({len(parsed_messages)} msgs, {len(downloaded_files)} files)")
        return {
            "project_dir": paths["root"],
            "messages_count": len(parsed_messages),
            "files_count": len(downloaded_files),
            "advisor": extracted_advisor,
            "topic": extracted_topic,
            "scales": extracted_scales,
            "meta_path": paths["meta_file"],
            "transcript_path": transcript_md_path
        }

    async def save_single_file(self, msg, client_name: str, client_id: Optional[int] = None, username: Optional[str] = None) -> str:
        """Save a single incoming file directly into 01_raw_inputs of the client's project."""
        fname, mtype, _, _ = resolve_media_details(msg)
        if not fname:
            return ""
        paths = self.provision_project(client_name, client_id=client_id, username=username)
        raw_dir = paths["raw"]
        dest_path = os.path.join(raw_dir, fname)
        await msg.download_media(file=dest_path)
        print(f"[+] Saved incoming file directly to project: {dest_path}")
        return dest_path

    def list_all_projects(self) -> List[Dict[str, Any]]:
        """List all managed client project folders in Google Drive."""
        if not os.path.exists(self.work_dir):
            return []

        results = []
        for d in sorted(os.listdir(self.work_dir)):
            full_path = os.path.join(self.work_dir, d)
            if not os.path.isdir(full_path) or d.startswith("."):
                continue

            meta_file = os.path.join(full_path, "project_meta.json")
            if os.path.exists(meta_file):
                try:
                    with open(meta_file, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                except Exception:
                    meta = {"client_name": d}
            else:
                meta = {"client_name": d}

            meta["folder_path"] = full_path
            meta["folder_name"] = d

            # Format umbrella client directories prominently
            if meta.get("is_umbrella_client_folder"):
                sub_count = len(meta.get("active_subprojects", []))
                orig_name = meta.get("client_name_fa") or meta.get("client_name") or d
                meta["client_name_fa"] = f"🌟 {orig_name} [VIP چتر تجمیعی - {sub_count} زیرپروژه]"
                meta["is_umbrella"] = True

            results.append(meta)

        return results

    def _extract_advisor(self, text: str) -> Optional[str]:
        """Extract advisor name from chat text."""
        patterns = [
            r"(?:دکتر|استاد)\s+([\u0600-\u06FF\s]{4,25})",
            r"(?:دانشجوی)\s+([\u0600-\u06FF\s]{4,25})"
        ]
        for pat in patterns:
            m = re.search(pat, text)
            if m:
                match_str = m.group(0).strip()
                # Clean up punctuation and stop words
                cleaned = re.sub(r"(?:گفتن|گفت|پیام|است|هستش|برای|رو|که).*", "", match_str).strip()
                if len(cleaned.split()) >= 2:
                    return cleaned
        return None

    def _extract_scales(self, text: str, files: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify instruments mentioned in text or files."""
        scales = []
        known_instruments = [
            ("Compass of Shame Scale (CoSS)", ["coss", "compass of shame", "قطب‌نمای شرم"]),
            ("SHAME Scale", ["shame scale", "shame assessment", "آزمون شرم"]),
            ("Test of Self-Conscious Affect (TOSCA)", ["tosca", "عاطفه خودآگاه"]),
            ("Self-Compassion Scale (SCS)", ["self-compassion", "شفقت به خود", "شفقت خود"]),
            ("Young Schema Questionnaire (YSQ)", ["طرحواره", "ysq", "طرح‌واره"]),
            ("Internalized Shame Scale (ISS)", ["internalized shame", "شرم درونی"]),
        ]
        text_lower = text.lower()
        file_names_str = " ".join([f.get("file_name", "").lower() for f in files])

        for name, keywords in known_instruments:
            if any(k in text_lower or k in file_names_str for k in keywords):
                scales.append({"name": name, "detected_in": "chat_or_files"})

        return scales

    def _extract_topic(self, text: str) -> Optional[str]:
        """Extract research topic summary from chat text."""
        m = re.search(r"(?:عنوان\s*(?:های)?\s*پیشنهادی|موضوع|درباره|درمورد)\s*[:؛-]?\s*([^\n]{10,80})", text)
        if m:
            return m.group(1).strip()
        # Fallback keywords
        for keyword in ["شرم مزمن", "شرم", "اضطراب", "افسردگی", "وسواس", "طرحواره", "روان‌سنجی"]:
            if keyword in text:
                return f"پژوهش روان‌شناختی در حوزه {keyword}"
        return None

    def _format_client_profile(
        self,
        client_name: str,
        client_id: Optional[int],
        username: Optional[str],
        advisor: Optional[str],
        topic: Optional[str],
        scales: List[Dict[str, Any]],
        files: List[Dict[str, Any]],
        project_dir: str
    ) -> str:
        """Format an executive client profile markdown document."""
        scales_str = "\n".join([f"- **{s.get('name')}**" for s in scales]) if scales else "- ابزارها در حال تعیین و استخراج"
        files_str = "\n".join([f"- 📄 `{f.get('file_name')}`" for f in files]) if files else "- فایلی دریافت نشده است"

        return f"""# شناسنامه پرونده پژوهشی مراجع: {client_name}

## ۱. اطلاعات هویتی و ارتباطی
- **نام مراجع:** {client_name}
- **شناسه تلگرام:** @{username or 'ندارد'}
- **شناسه یکتا (ID):** `{client_id or 'نامشخص'}`
- **استاد راهنما:** {advisor or 'مشخص نشده'}
- **تاریخ ایجاد پرونده:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
- **مسیر پوشه در گوگل درایو:** `{project_dir}`

---

## ۲. موضوع و محورهای پژوهش
- **موضوع استخراج‌شده:** {topic or 'در حال بررسی'}
- **ابزارهای هدف:**
{scales_str}

---

## ۳. فایل‌های دریافتی مراجع
{files_str}

---

## ۴. مراحل کاری پیشنهادی
1. استخراج و بررسی مقیاس‌های پژوهش
2. تدوین بخش متدولوژی و روش پژوهش (Methodology) طبق فرمت APA 7
3. برآورد حجم نمونه با نرم‌افزار G*Power
4. هدایت فرآیند جمع‌آوری داده‌ها
5. اجرای تحلیل‌های آماری و روان‌سنجی (EFA / CFA و پایایی)
"""
