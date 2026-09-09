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
from datetime import datetime
from typing import Dict, List, Any, Optional

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

    def find_existing_project_by_client(
        self, client_name: str, client_id: Optional[int] = None, username: Optional[str] = None
    ) -> Optional[str]:
        """
        Check if a project folder already exists for this client by folder name,
        Telegram ID, or Telegram username inside project_meta.json.
        """
        if not os.path.exists(self.work_dir):
            return None

        clean_name = sanitize_filename(client_name)
        exact_path = os.path.join(self.work_dir, clean_name)
        if os.path.isdir(exact_path):
            return exact_path

        # Scan all directories in work_dir for matching metadata
        for folder in os.listdir(self.work_dir):
            folder_path = os.path.join(self.work_dir, folder)
            if not os.path.isdir(folder_path):
                continue

            # Prefix match e.g. "Sepehr Rahimi - Chronic Shame"
            if folder.startswith(clean_name):
                return folder_path

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
                except Exception:
                    pass

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
        Returns dictionary of paths.
        """
        clean_name = sanitize_filename(client_name)
        existing_dir = self.find_existing_project_by_client(clean_name, client_id, username)

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

            # Check and download media/file
            if msg.file and hasattr(msg.file, "name") and msg.file.name:
                fname = sanitize_filename(msg.file.name)
                entry["file_name"] = fname
                entry["file_size"] = getattr(msg.file, "size", 0)

                if download_files and not is_saber:
                    target_file = os.path.join(raw_dir, fname)
                    if not os.path.exists(target_file):
                        print(f"    📥 Downloading client file: {fname} ({entry['file_size']:,} bytes)...")
                        try:
                            await msg.download_media(file=target_file)
                            downloaded_files.append({
                                "file_name": fname,
                                "file_path": target_file,
                                "size_bytes": entry["file_size"],
                                "date": entry["date"]
                            })
                        except Exception as e:
                            print(f"    [-] Failed to download {fname}: {e}")
                    else:
                        downloaded_files.append({
                            "file_name": fname,
                            "file_path": target_file,
                            "size_bytes": entry["file_size"],
                            "status": "already_exists"
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
                transcript_lines.append(f"> 📎 **فایل ضمیمه:** [{m['file_name']}]({m['file_name']}) ({m.get('file_size', 0):,} بایت)")
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
        paths = self.provision_project(client_name, client_id=client_id, username=username)
        raw_dir = paths["raw"]
        fname = sanitize_filename(msg.file.name or "document")
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
