"""
group_topics.py — Academic Desk Forum Topics Management Engine

Manages Telegram Supergroup Forum Topics for the Academic Desk:
1. 5 Permanent Core Functional Topics (Proposals, Drafts, Scales, Health, System).
2. Dedicated VIP Client Topics for high-volume collaborators (e.g. Shahram Amiri).
3. Persistent caching in userbot_storage/group_topics.json.
4. Auto-routing based on client ID / VIP status or functional category.
"""

import os
import json
import random
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

try:
    from telethon.tl.functions.messages import (
        CreateForumTopicRequest,
        GetForumTopicsRequest,
        EditForumTopicRequest
    )
except ImportError:
    CreateForumTopicRequest = None
    GetForumTopicsRequest = None
    EditForumTopicRequest = None

CORE_TOPICS = {
    "proposals": {
        "title": "📑 Proposals & Quotes",
        "color": 7322096,      # Blue
        "description": "Incoming proposals, G*Power sample sizes, and quotation cards"
    },
    "drafts": {
        "title": "💡 Co-Pilot Drafts",
        "color": 16766590,     # Yellow
        "description": "Debounced client inquiries, voice note digests, and suggested Persian drafts"
    },
    "scales": {
        "title": "📊 Scales & Psychometrics",
        "color": 13338331,     # Violet
        "description": "Questionnaire lookups, 4,880 scale database search results"
    },
    "health": {
        "title": "🩺 Pipeline & Health",
        "color": 9367192,      # Green
        "description": "Daily briefings, stalled project follow-ups, and health checks"
    },
    "supervisor_reviews": {
        "title": "🎓 Supervisor Feedback & Defense",
        "color": 16478047,     # Red/Coral
        "description": "Supervisor comments, committee revisions, and viva voce defense questions"
    },
    "system": {
        "title": "⚙️ System & Drive Sync",
        "color": 16749490,     # Rose
        "description": "Drive folder provisioning logs, daemon status, and system alerts"
    }
}


class TopicManager:
    """Manages forum topics in Academic Desk supergroup."""

    def __init__(self, config: Dict[str, Any], storage_dir: Optional[str] = None):
        self.config = config
        self.storage_dir = storage_dir or os.path.join(os.path.dirname(__file__), "userbot_storage")
        os.makedirs(self.storage_dir, exist_ok=True)
        self.filepath = os.path.join(self.storage_dir, "group_topics.json")
        self.topics: Dict[str, Any] = self._load()

    def _load(self) -> Dict[str, Any]:
        """Load topic mappings from disk."""
        if os.path.exists(self.filepath):
            try:
                with open(self.filepath, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                print(f"[-] Error reading group_topics.json: {e}")
        return {
            "functional": {},
            "vip": {},
            "last_synced": None
        }

    def save(self):
        """Save topic mappings to disk."""
        self.topics["last_synced"] = datetime.now().isoformat()
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump(self.topics, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[-] Error saving group_topics.json: {e}")

    async def sync_and_ensure_topics(
        self,
        user_client,
        chat_id: int,
        vip_clients: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Query existing forum topics from Telegram supergroup using userbot client,
        create any missing core functional topics, and ensure VIP clients have dedicated topics.
        """
        if user_client is None or GetForumTopicsRequest is None:
            return self.topics

        try:
            peer = await user_client.get_input_entity(chat_id)
            res = await user_client(
                GetForumTopicsRequest(
                    peer=peer,
                    offset_date=None,
                    offset_id=0,
                    offset_topic=0,
                    limit=100
                )
            )
            existing_by_title = {t.title.strip().lower(): t.id for t in res.topics}
            existing_by_id = {t.id: t.title for t in res.topics}
        except Exception as e:
            print(f"[-] Error querying forum topics from Telegram: {e}")
            return self.topics

        # 1. Ensure 5 Permanent Core Functional Topics
        functional_map = self.topics.get("functional", {})
        for key, info in CORE_TOPICS.items():
            expected_title = info["title"]
            expected_lower = expected_title.strip().lower()

            if expected_lower in existing_by_title:
                topic_id = existing_by_title[expected_lower]
                functional_map[key] = topic_id
            else:
                try:
                    r = random.randint(1, 2**63 - 1)
                    upd = await user_client(
                        CreateForumTopicRequest(
                            peer=peer,
                            title=expected_title,
                            icon_color=info["color"],
                            random_id=r
                        )
                    )
                    topic_id = None
                    for u in upd.updates:
                        if hasattr(u, "id"):
                            topic_id = u.id
                            break
                        elif hasattr(u, "message") and hasattr(u.message, "id"):
                            topic_id = u.message.id
                            break
                    if topic_id:
                        functional_map[key] = topic_id
                        existing_by_title[expected_lower] = topic_id
                        print(f"[+] Created functional topic: {expected_title} (ID: {topic_id})")
                except Exception as err:
                    print(f"[-] Error creating topic '{expected_title}': {err}")

        self.topics["functional"] = functional_map

        # 2. Ensure Dedicated VIP Client Topics
        vip_map = self.topics.get("vip", {})
        if vip_clients:
            for vip in vip_clients:
                tid = str(vip.get("telegram_id"))
                cname = vip.get("client_name_fa") or vip.get("client_name") or "VIP Client"
                expected_title = f"⭐ {cname}"
                expected_lower = expected_title.strip().lower()

                # Check if previously saved ID is still valid in Telegram
                if tid in vip_map and vip_map[tid] in existing_by_id:
                    continue

                # Check if any existing topic matches expected title or client names
                matched_id = None
                if expected_lower in existing_by_title:
                    matched_id = existing_by_title[expected_lower]
                else:
                    c_en = (vip.get("client_name") or "").strip().lower()
                    c_fa = (vip.get("client_name_fa") or "").strip().lower()
                    for ex_title, ex_id in existing_by_title.items():
                        if (c_fa and c_fa in ex_title) or (c_en and c_en in ex_title):
                            matched_id = ex_id
                            break

                if matched_id:
                    vip_map[tid] = matched_id
                else:
                    try:
                        r = random.randint(1, 2**63 - 1)
                        upd = await user_client(
                            CreateForumTopicRequest(
                                peer=peer,
                                title=expected_title,
                                icon_color=16478047,  # Red/Coral
                                random_id=r
                            )
                        )
                        topic_id = None
                        for u in upd.updates:
                            if hasattr(u, "id"):
                                topic_id = u.id
                                break
                            elif hasattr(u, "message") and hasattr(u.message, "id"):
                                topic_id = u.message.id
                                break
                        if topic_id:
                            vip_map[tid] = topic_id
                            existing_by_title[expected_lower] = topic_id
                            print(f"[+] Created VIP topic: {expected_title} (ID: {topic_id})")
                    except Exception as err:
                        print(f"[-] Error creating VIP topic '{expected_title}': {err}")

        self.topics["vip"] = vip_map
        self.save()
        return self.topics

    async def create_vip_topic(
        self,
        user_client,
        chat_id: int,
        client_name: str,
        telegram_id: int
    ) -> Optional[int]:
        """Dynamically create a dedicated VIP topic for a client."""
        if user_client is None or CreateForumTopicRequest is None:
            return None

        tid = str(telegram_id)
        if tid in self.topics.get("vip", {}):
            return self.topics["vip"][tid]

        try:
            peer = await user_client.get_input_entity(chat_id)
            expected_title = f"⭐ {client_name}"
            r = random.randint(1, 2**63 - 1)
            upd = await user_client(
                CreateForumTopicRequest(
                    peer=peer,
                    title=expected_title,
                    icon_color=16478047,
                    random_id=r
                )
            )
            topic_id = None
            for u in upd.updates:
                if hasattr(u, "id"):
                    topic_id = u.id
                    break
                elif hasattr(u, "message") and hasattr(u.message, "id"):
                    topic_id = u.message.id
                    break
            if topic_id:
                if "vip" not in self.topics:
                    self.topics["vip"] = {}
                self.topics["vip"][tid] = topic_id
                self.save()
                print(f"[+] Provisioned new VIP topic: {expected_title} (ID: {topic_id})")
                return topic_id
        except Exception as e:
            print(f"[-] Error creating VIP topic for {client_name}: {e}")
        return None

    def is_vip_client(self, client_id: Optional[int]) -> bool:
        """Check if client has a registered VIP topic."""
        if not client_id:
            return False
        return str(client_id) in self.topics.get("vip", {})

    def resolve_topic_id(
        self,
        topic_key: Optional[str] = None,
        client_id: Optional[int] = None,
        client_name: Optional[str] = None
    ) -> Optional[int]:
        """
        Resolve destination message_thread_id:
        1. If client_id matches a registered VIP -> dedicated VIP topic ID.
        2. Else if topic_key in permanent functional topics -> functional topic ID.
        3. Else None (fallback to General topic / main channel).
        """
        # Priority 1: Check VIP topic
        if client_id:
            tid = str(client_id)
            if tid in self.topics.get("vip", {}):
                return self.topics["vip"][tid]

        # Priority 2: Functional topic
        if topic_key and topic_key in self.topics.get("functional", {}):
            return self.topics["functional"][topic_key]

        return None

    def format_topics_summary(self) -> str:
        """Format an HTML table/card of all active topics for the /topics command."""
        lines = [
            "🏛️ <b>Academic Desk — Forum Topics Status</b>\n",
            "📌 <b>Core Functional Topics:</b>"
        ]
        func = self.topics.get("functional", {})
        for k, info in CORE_TOPICS.items():
            t_id = func.get(k)
            status = f"<code>ID: {t_id}</code>" if t_id else "<i>Not bound</i>"
            lines.append(f"• {info['title']}: {status}")

        vips = self.topics.get("vip", {})
        if vips:
            lines.append("\n⭐ <b>Dedicated VIP Client Topics:</b>")
            for tid, t_id in vips.items():
                lines.append(f"• User ID <code>{tid}</code>: <code>Topic ID: {t_id}</code>")

        last_sync = (self.topics.get("last_synced") or "Never")[:19]
        lines.append(f"\n🕒 <i>Last Synced: {last_sync}</i>")
        return "\n".join(lines)
