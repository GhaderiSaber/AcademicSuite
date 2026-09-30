"""Admin command dispatcher for Telegram Userbot."""

from __future__ import annotations

import asyncio
from datetime import datetime
import html
import json
import os
import re
import sys
from typing import Any, Optional

USERBOT_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.abspath(os.path.join(USERBOT_DIR, ".."))
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

from telethon import events

try:
    from telethon.tl.custom import Button
except ImportError:
    Button = None

from project_drive_manager import (
    clean_drive_display_path,
    format_client_mention_html,
    resolve_media_details,
)
from financial_ledger import format_toman
from userbot.utils import is_valid_telegram_button_url

try:
    from proposal_price_estimator import format_telegram_card
except ImportError:
    format_telegram_card = None


class AdminCommandDispatcher:
    """Dispatches Telegram commands sent to Academic Desk or Admin Private Chat."""

    def __init__(self, bot: Any):
        self.bot = bot

    def __getattr__(self, name: str) -> Any:
        return getattr(self.bot, name)

    def __setattr__(self, name: str, value: Any) -> None:
        if name == "bot":
            super().__setattr__(name, value)
        else:
            setattr(self.bot, name, value)

    async def dispatch(self, event: Any) -> None:
        txt = (event.message.message or "").strip()

        # Forum Topics status: /topics or /topic_status
        if txt in ["/topics", "/topic_status"]:
            summary = self.topic_manager.format_topics_summary()
            await event.reply(summary, parse_mode="html")
            return

        # Refresh & sync topics: /sync_topics
        if txt in ["/sync_topics", "/refresh_topics"]:
            await event.reply("🔄 Synchronizing forum topics with Academic Desk...", parse_mode="html")
            vip_reg = self.project_manager.load_vip_registry()
            await self.topic_manager.sync_and_ensure_topics(
                self.client,
                self.admin_desk_chat_id,
                vip_clients=vip_reg.get("vip_clients", [])
            )
            summary = self.topic_manager.format_topics_summary()
            await event.reply(f"✅ <b>Topics successfully synchronized:</b>\n\n{summary}", parse_mode="html")
            return

        # Promote client to VIP and create dedicated forum topic: /make_vip <client_name or id>
        m_vip = re.match(r"^/make_vip(?:\s+(.+))?", txt)
        if m_vip:
            q = (m_vip.group(1) or "").strip()
            if not q:
                await event.reply("⚠️ Usage: <code>/make_vip &lt;client_name or telegram_id&gt;</code>", parse_mode="html")
                return
            matched_id = int(q) if q.isdigit() else None
            matched_name = q if not q.isdigit() else f"Client {q}"
            if not matched_id:
                for p in self.project_manager.list_all_projects():
                    if q.lower() in (p.get("client_name") or "").lower() or q.lower() in (p.get("client_name_fa") or "").lower():
                        matched_id = p.get("client_id")
                        matched_name = p.get("client_name_fa") or p.get("client_name")
                        break
            if not matched_id:
                await event.reply(f"❌ Could not find client matching <code>{html.escape(q)}</code> with a known Telegram ID.", parse_mode="html")
                return

            self.project_manager.add_vip_client(client_name=matched_name, telegram_id=matched_id)
            t_id = await self.topic_manager.create_vip_topic(self.client, self.admin_desk_chat_id, matched_name, matched_id)
            await event.reply(
                f"⭐ <b>VIP Client Configured!</b>\n"
                f"• <b>Client:</b> {html.escape(matched_name)} (ID: <code>{matched_id}</code>)\n"
                f"• <b>Dedicated Forum Topic ID:</b> <code>{t_id}</code>\n"
                f"All future messages and draft cards for this client will route to their dedicated topic thread.",
                parse_mode="html"
            )
            return

        # Unread messages re-scan: /unread or /scan
        if txt in ["/unread", "/scan"]:
            await event.reply("🔍 Scanning unread client messages and synchronizing Google Drive projects...", parse_mode="html")
            await self.scan_and_process_unread_messages()
            return

        # WebApp / Mini App Dashboard: /webapp or /dashboard
        if txt in ["/webapp", "/dashboard", "/app"]:
            projs = self.project_manager.list_all_projects()
            webapp_url = self.config.get("webapp_url", "")
            has_web_btn = is_valid_telegram_button_url(webapp_url)
            dash_url_display = webapp_url if has_web_btn else "http://localhost:8080"
            dash_text = (
                f"📱 <b>Saber Academic Suite — Mini App & Dashboard</b>\n\n"
                f"• <b>Live Projects:</b> {len(projs)} active client projects\n"
                f"• <b>Web Dashboard URL:</b> <code>{dash_url_display}</code>\n"
                f"• <b>Features:</b> Visual Kanban pipeline, live pricing calculator, psychometric scales explorer"
            )
            btn = None
            if Button is not None:
                if has_web_btn:
                    btn = [[Button.url("📱 Open Mini App Dashboard", webapp_url)]]
                else:
                    btn = [[Button.inline("📂 Project Catalog", b"cmd_projects", style="primary"),
                            Button.inline("🔄 Rescan Messages", b"cmd_unread", style="primary")]]
            await event.reply(dash_text, buttons=btn, parse_mode="html")
            return

        # List Google Drive projects: /projects or /list_projects [query]
        m_proj = re.match(r"^/(?:projects|list_projects)(?:\s+(.+))?", txt)
        if m_proj:
            filter_term = (m_proj.group(1) or "").strip().lower()
            projs = self.project_manager.list_all_projects()
            if filter_term:
                projs = [p for p in projs if filter_term in (p.get("client_name") or "").lower() 
                         or filter_term in (p.get("client_name_fa") or "").lower()
                         or filter_term in (p.get("folder_name") or "").lower()]
            if not projs:
                await event.reply("📂 No matching project folders found in Google Drive.", parse_mode="html")
                return
            header = f"📂 <b>Client Projects in Google Drive ({len(projs)} found):</b>\n" if filter_term else f"📂 <b>Active Client Projects in Google Drive ({len(projs)} projects):</b>\n"
            lines = [header]
            display_limit = 20 if not filter_term else len(projs)
            for p in projs[:display_limit]:
                cname = p.get("client_name_fa") or p.get("client_name") or p.get("folder_name")
                fc = p.get("file_count", 0)
                mc = p.get("message_count", 0)
                st = p.get("status", "pending")
                clean_p = clean_drive_display_path(p['folder_path'])
                lines.append(
                    f"• <b>{html.escape(cname)}</b> (<i>{html.escape(st)}</i>) | {mc} msgs, {fc} files\n"
                    f"  ▫️ <code>{html.escape(clean_p)}</code>"
                )
            if len(projs) > display_limit:
                lines.append(f"\n<i>... and {len(projs) - display_limit} more projects. Use <code>/projects &lt;name&gt;</code> to filter.</i>")
            await event.reply("\n".join(lines), parse_mode="html")
            return

        # Triage inactive projects: /triage or /triage_run [days]
        m_triage = re.match(r"^/triage(?:_(run|execute))?(?:\s+(\d+))?", txt)
        if m_triage:
            is_run = bool(m_triage.group(1))
            days_arg = int(m_triage.group(2)) if m_triage.group(2) else 30
            mode_str = "اجرای قطعی جابجایی" if is_run else "پیش‌نمایش (Dry Run)"
            await event.reply(f"🧹 <b>در حال غربالگری پروژه‌های غیرفعال ({mode_str} — آستانه: {days_arg} روز)...</b>", parse_mode="html")
            report = self.project_manager.triage_inactive_projects(inactivity_days=days_arg, dry_run=not is_run)

            resp_lines = [
                f"🧹 <b>گزارش مدیریت چرخه عمر پروژه‌ها ({mode_str})</b>\n",
                f"⏱ <b>آستانه عدم فعالیت:</b> {days_arg} روز",
                f"🟢 <b>پروژه‌های فعال نگه‌داشته‌شده:</b> {len(report['active_retained'])} مورد",
                f"📦 <b>انتقال به پوشه معلق (Pending Works):</b> {len(report['moved_to_pending'])} مورد",
                f"🏁 <b>انتقال به پوشه خاتمه‌یافته (Finished Works):</b> {len(report['moved_to_finished'])} مورد",
                f"⭐ <b>پروژه‌های معاف/VIP:</b> {len(report['pinned_exempt'])} مورد\n"
            ]
            if report['moved_to_pending']:
                resp_lines.append("<b>نمونه پروژه‌های انتقال‌یافته به Pending Works:</b>")
                for p in report['moved_to_pending'][:10]:
                    resp_lines.append(f"• <code>{p['folder']}</code> ({p['days_inactive']} روز)")
                if len(report['moved_to_pending']) > 10:
                    resp_lines.append(f"• <i>... و {len(report['moved_to_pending']) - 10} پروژه دیگر</i>")

            if not is_run and (report['moved_to_pending'] or report['moved_to_finished']):
                resp_lines.append("\n💡 <i>برای اجرای قطعی جابجایی، دستور <code>/triage_run</code> را ارسال فرمایید.</i>")
            elif is_run:
                resp_lines.append("\n✅ <b>پوشه My Work با موفقیت پاکسازی و خلوت گردید.</b>")

            await event.reply("\n".join(resp_lines), parse_mode="html")
            return

        # Manual Save / Archive Project: /save_project <name_or_id>
        m_save = re.match(r"^/(?:save_project|archive_project)(?:\s+(.+))?", txt)
        if m_save:
            target = m_save.group(1).strip() if m_save.group(1) else None
            if not target:
                await event.reply("⚠️ Please specify client name, username, or Telegram ID:\nExample: <code>/save_project @username</code>", parse_mode="html")
                return

            await event.reply(f"🔍 Searching chat and archiving project folder in Google Drive for: <code>{html.escape(target)}</code>...", parse_mode="html")
            target_dialog = None
            dialogs = await self.client.get_dialogs(limit=100)
            clean_target = target.lstrip("@").lower()

            for dlg in dialogs:
                if not dlg.is_user or dlg.entity.is_self or dlg.entity.bot:
                    continue
                uname = (getattr(dlg.entity, "username", None) or "").lower()
                dname = (dlg.name or "").lower()
                did_str = str(dlg.id)

                if clean_target == uname or clean_target in dname or clean_target == did_str:
                    target_dialog = dlg
                    break

            if not target_dialog:
                try:
                    ent = await self.client.get_entity(target)
                    client_name = f"{getattr(ent, 'first_name', '')} {getattr(ent, 'last_name', '') or ''}".strip() or str(ent.id)
                    res = await self.project_manager.save_client_chat_and_files(
                        client=self.client,
                        entity=ent,
                        client_name=client_name,
                        client_id=ent.id,
                        username=getattr(ent, "username", None),
                        limit_messages=200,
                        download_files=True
                    )
                    clean_p = clean_drive_display_path(res['project_dir'])
                    await event.reply(
                        f"✅ <b>Project synchronized in Google Drive:</b>\n"
                        f"👤 Client: <b>{html.escape(client_name)}</b>\n"
                        f"📁 Drive Folder: <code>{html.escape(clean_p)}</code>\n"
                        f"📊 Stats: {res['messages_count']} messages | {res['files_count']} files",
                        parse_mode="html"
                    )
                    return
                except Exception as err:
                    await event.reply(f"❌ Client with identifier <code>{html.escape(target)}</code> not found: {err}", parse_mode="html")
                    return

            res = await self.project_manager.save_client_chat_and_files(
                client=self.client,
                entity=target_dialog.entity,
                client_name=target_dialog.name,
                client_id=target_dialog.id,
                username=getattr(target_dialog.entity, "username", None),
                limit_messages=200,
                download_files=True
            )
            clean_p = clean_drive_display_path(res['project_dir'])
            await event.reply(
                f"✅ <b>Project synchronized in Google Drive:</b>\n"
                f"👤 Client: <b>{html.escape(target_dialog.name)}</b>\n"
                f"📁 Drive Folder: <code>{html.escape(clean_p)}</code>\n"
                f"📊 Stats: {res['messages_count']} messages | {res['files_count']} files",
                parse_mode="html"
            )
            return

        # Sync all recent projects: /sync_projects
        if txt in ["/sync_projects", "/sync_all"]:
            await event.reply("🔄 Synchronizing and provisioning Google Drive project folders for recent clients...", parse_mode="html")
            dialogs = await self.client.get_dialogs(limit=30)
            client_dialogs = [d for d in dialogs if d.is_user and not d.entity.is_self and not d.entity.bot]
            synced_count = 0
            for cd in client_dialogs:
                try:
                    await self.project_manager.save_client_chat_and_files(
                        client=self.client,
                        entity=cd.entity,
                        client_name=cd.name,
                        client_id=cd.id,
                        username=getattr(cd.entity, "username", None),
                        limit_messages=60,
                        download_files=True
                    )
                    synced_count += 1
                except Exception as e:
                    print(f"[-] Error syncing dialog {cd.name}: {e}")

            await event.reply(
                f"✅ Synchronization complete. {synced_count} client project folders updated in Google Drive.\n"
                "Use <code>/projects</code> to view the catalog.",
                parse_mode="html"
            )
            return

        # Send quote command: /send_Q101
        m_send = re.match(r"^/send_(Q\d+)", txt)
        if m_send:
            qid = m_send.group(1)
            if qid in self.pending_quotes:
                entry = self.pending_quotes[qid]
                # Client message is authentic Persian with clean HTML
                card = format_telegram_card(entry["quote"], lang="fa")
                target_client = entry.get("client_source") or self.client
                await target_client.send_message(entry["chat_id"], card, parse_mode="html")
                await event.reply(f"✅ Quotation {qid} was successfully dispatched to {entry['sender_name']}.", parse_mode="html")
                del self.pending_quotes[qid]
            else:
                await event.reply(f"❌ Quotation ID {qid} not found.", parse_mode="html")

        # Adjust price command: /adjust_Q101_8500000
        m_adj = re.match(r"^/adjust_(Q\d+)_(\d+)", txt)
        if m_adj:
            qid = m_adj.group(1)
            new_price = int(m_adj.group(2))
            if qid in self.pending_quotes:
                entry = self.pending_quotes[qid]
                entry["quote"]["total_price_tomans"] = new_price
                entry["quote"]["total_price_formatted"] = f"{new_price:,.0f} تومان"
                # Client message is authentic Persian with clean HTML
                card = format_telegram_card(entry["quote"], lang="fa")
                target_client = entry.get("client_source") or self.client
                await target_client.send_message(entry["chat_id"], card, parse_mode="html")
                await event.reply(f"✅ Quotation {qid} adjusted to {new_price:,.0f} Tomans and dispatched to {entry['sender_name']}.", parse_mode="html")
                del self.pending_quotes[qid]
            else:
                await event.reply(f"❌ Quotation ID {qid} not found.", parse_mode="html")

        # Ignore quote command: /ignore_Q101
        m_ign = re.match(r"^/ignore_(Q\d+)", txt)
        if m_ign:
            qid = m_ign.group(1)
            if qid in self.pending_quotes:
                del self.pending_quotes[qid]
                await event.reply(f"🗑️ Quotation {qid} was dismissed.", parse_mode="html")

        # Send co-pilot draft command: /send_msg_D101 or /send_msg_D101 <custom text>
        m_draft = re.match(r"^/send_msg_(D\d+)(?:\s+(.+))?", txt, flags=re.DOTALL)
        if m_draft:
            did = m_draft.group(1)
            custom_text = (m_draft.group(2) or "").strip()
            if did in self.pending_drafts:
                entry = self.pending_drafts[did]
                msg_to_send = custom_text if custom_text else entry["draft_reply"]
                target_client = entry.get("client_source") or self.client
                await target_client.send_message(entry["chat_id"], msg_to_send)
                await event.reply(
                    f"✅ Response {did} was successfully dispatched to {entry['sender_name']} via {entry['account_label']}.",
                    parse_mode="html"
                )
                del self.pending_drafts[did]
            else:
                await event.reply(f"❌ Draft ID {did} not found or already sent.", parse_mode="html")
            return

        # Ignore co-pilot draft command: /ignore_D101
        m_ign_draft = re.match(r"^/ignore_(D\d+)", txt)
        if m_ign_draft:
            did = m_ign_draft.group(1)
            if did in self.pending_drafts:
                cname = self.pending_drafts[did]["sender_name"]
                del self.pending_drafts[did]
                await event.reply(f"🗑️ Draft {did} for {cname} was dismissed.", parse_mode="html")
            else:
                await event.reply(f"❌ Draft ID {did} not found.", parse_mode="html")
            return

        # Health check & Follow-Up Reminders command: /health, /reminders, /followup
        if txt in ["/health", "/reminders", "/followup", "/project_health"]:
            await event.reply("🔍 Auditing project health and scanning for follow-up reminders...", parse_mode="html")
            await self.scan_and_report_project_health(trigger_event=event)
            return

        # Send follow-up command: /send_fu_F101 or /send_fu_F101 <custom text>
        m_fu = re.match(r"^/send_fu_(F\d+)(?:\s+(.+))?", txt, flags=re.DOTALL)
        if m_fu:
            fuid = m_fu.group(1)
            custom_text = (m_fu.group(2) or "").strip()
            if fuid in self.pending_followups:
                entry = self.pending_followups[fuid]
                msg_to_send = custom_text if custom_text else entry["draft_reply"]
                target_dest = entry.get("telegram_id") or entry.get("username") or entry.get("client_name")
                try:
                    await self.client.send_message(target_dest, msg_to_send)
                    if entry.get("folder_path"):
                        self.project_manager.record_followup_dispatched(entry["folder_path"], entry["followup_type"], msg_to_send)
                    await event.reply(
                        f"✅ Follow-up {fuid} was successfully dispatched to <b>{entry['client_name']}</b> via Saber's personal account.",
                        parse_mode="html"
                    )
                    del self.pending_followups[fuid]
                except Exception as send_err:
                    await event.reply(f"❌ Failed to send follow-up {fuid}: {send_err}", parse_mode="html")
            else:
                await event.reply(f"❌ Follow-up ID {fuid} not found or already sent.", parse_mode="html")
            return

        # Ignore follow-up command: /ignore_fu_F101
        m_ign_fu = re.match(r"^/ignore_fu_(F\d+)", txt)
        if m_ign_fu:
            fuid = m_ign_fu.group(1)
            if fuid in self.pending_followups:
                cname = self.pending_followups[fuid]["client_name"]
                del self.pending_followups[fuid]
                await event.reply(f"🗑️ Follow-up reminder {fuid} for {cname} was dismissed.", parse_mode="html")
            else:
                await event.reply(f"❌ Follow-up ID {fuid} not found.", parse_mode="html")
            return

        # Deliverables inspection command: /deliverables [client_query] or /files [client_query]
        m_deliv = re.match(r"^/(?:deliverables|files)(?:\s+(.+))?", txt)
        if m_deliv:
            c_query = (m_deliv.group(1) or "").strip()
            if not c_query:
                # Overview of all projects with deliverables
                projs = self.project_manager.list_all_projects()
                ready_list = []
                for p in projs:
                    d_files = self.project_manager.list_project_deliverables(p["folder_path"])
                    if d_files:
                        ready_list.append((p, d_files))
                if not ready_list:
                    await event.reply("📦 No completed deliverables currently waiting in Google Drive <code>03_deliverables/</code>.", parse_mode="html")
                    return
                lines = [f"📦 <b>Client Projects with Ready Deliverables ({len(ready_list)} clients):</b>\n"]
                for p, dfs in ready_list[:15]:
                    cname = p.get("client_name_fa") or p.get("client_name") or p.get("folder_name")
                    files_str = ", ".join([f"<code>{f['filename']}</code> ({f['size_str']})" for f in dfs[:3]])
                    if len(dfs) > 3:
                        files_str += f" and {len(dfs)-3} more"
                    lines.append(
                        f"• <b>{html.escape(cname)}</b> ({len(dfs)} files):\n"
                        f"  ▫️ {files_str}\n"
                        f"  👉 <code>/deliverables {html.escape(cname)}</code>"
                    )
                await event.reply("\n".join(lines), parse_mode="html")
                return
            else:
                # Find project for specific client
                clean_q = c_query.lstrip("@").lower()
                matched_pdir = self.project_manager.find_existing_project_by_client(clean_q)
                target_meta = {}
                if not matched_pdir and clean_q.isdigit():
                    matched_pdir = self.project_manager.find_existing_project_by_client("Client", client_id=int(clean_q))
                if not matched_pdir:
                    projs = self.project_manager.list_all_projects()
                    for p in projs:
                        if clean_q in (p.get("client_name") or "").lower() or \
                           clean_q in (p.get("client_name_fa") or "").lower() or \
                           clean_q in (p.get("folder_name") or "").lower() or \
                           clean_q in (p.get("username") or "").lower():
                            matched_pdir = p["folder_path"]
                            target_meta = p
                            break
                if not matched_pdir:
                    await event.reply(f"❌ No project folder found for client <code>{html.escape(c_query)}</code>.", parse_mode="html")
                    return

                if not target_meta and os.path.exists(os.path.join(matched_pdir, "project_meta.json")):
                    try:
                        with open(os.path.join(matched_pdir, "project_meta.json"), "r", encoding="utf-8") as f:
                            target_meta = json.load(f)
                    except Exception:
                        pass

                cname = target_meta.get("client_name_fa") or target_meta.get("client_name") or os.path.basename(matched_pdir)
                d_files = self.project_manager.list_project_deliverables(matched_pdir)
                clean_p = clean_drive_display_path(matched_pdir)
                if not d_files:
                    await event.reply(
                        f"📦 Project folder found for <b>{html.escape(cname)}</b>, but <code>03_deliverables/</code> is empty.\n"
                        f"📁 Folder: <code>{html.escape(clean_p)}</code>",
                        parse_mode="html"
                    )
                    return

                lines = [
                    f"📦 <b>Deliverables for {html.escape(cname)} ({len(d_files)} files):</b>",
                    f"📁 <code>{html.escape(clean_p)}</code>\n"
                ]
                for idx, df in enumerate(d_files[:10], start=1):
                    lines.append(
                        f"{idx}. 📄 <b>{html.escape(df['filename'])}</b>\n"
                        f"   ▫️ Size: <code>{df['size_str']}</code> | Modified: <code>{df['modified_at']}</code>\n"
                        f"   👉 Dispatch draft: <code>/send_file {html.escape(cname)} {html.escape(df['filename'])}</code>"
                    )
                await event.reply("\n".join(lines), parse_mode="html")
                return

        # Morning Executive Briefing: /briefing or /morning
        if re.match(r"^/(?:briefing|morning)\b", txt):
            await self.post_morning_executive_briefing(trigger_event=event)
            return

        # Mathematical formula & defense command: /math [test_type] [optional client or dilemma] or /formula
        m_math = re.match(r"^/(?:math|formula)(?:\s+([^\s]+))?(?:\s+(.+))?", txt)
        if m_math:
            t_type = (m_math.group(1) or "").strip()
            extra = (m_math.group(2) or "").strip()
            if not t_type:
                help_msg = (
                    "📐 <b>Digital Saber — Native Mathematical Formula Engine</b>\n\n"
                    "Generates APA 7th statistical test formulations, LaTeX code blocks, and viva voce oral defense scripts.\n\n"
                    "📌 <b>Available Statistical Test Families:</b>\n"
                    "• <code>/math ancova</code> — ANCOVA pre-test covariate & effect size (η<sub>p</sub>²)\n"
                    "• <code>/math sem</code> — SEM/CFA fit indices (χ², RMSEA, CFI, TLI, SRMR)\n"
                    "• <code>/math regression</code> — Multiple regression model (<i>R</i>², <i>F</i>, β, <i>t</i>)\n"
                    "• <code>/math gpower</code> — G*Power 3.1 sample size & non-centrality (λ = <i>f</i>² × <i>N</i>)\n"
                    "• <code>/math ttest</code> — Student's <i>t</i>-test & Cohen's <i>d</i>\n"
                    "• <code>/math mediation</code> — Hayes PROCESS 5,000 bootstrap BCa CI\n\n"
                    "👉 <i>Example:</i> <code>/math ancova چرا از آنکووا استفاده کردی؟</code>"
                )
                await event.reply(help_msg, parse_mode="html")
                return

            await self.generate_and_post_math_defense(test_type=t_type, supervisor_dilemma_fa=extra or None, trigger_event=event)
            return

        # Voice transcription command: /transcribe [client_query] or /voice
        m_trans = re.match(r"^/(?:transcribe|voice)(?:\s+(.+))?", txt)
        if m_trans:
            c_query = (m_trans.group(1) or "").strip()
            if not c_query:
                await event.reply(
                    "🎙️ <b>Digital Saber — Persian Voice Note Transcriber</b>\n\n"
                    "Transcribe and analyze any client voice note from Google Drive.\n"
                    "Usage: <code>/transcribe &lt;client_name&gt;</code>\n"
                    "Example: <code>/transcribe Zahra Jalali</code>",
                    parse_mode="html"
                )
                return
            clean_q = c_query.lstrip("@").lower()
            matched_pdir = self.project_manager.find_existing_project_by_client(clean_q)
            if not matched_pdir and clean_q.isdigit():
                matched_pdir = self.project_manager.find_existing_project_by_client("Client", client_id=int(clean_q))
            if not matched_pdir:
                projs = self.project_manager.list_all_projects()
                for p in projs:
                    if clean_q in (p.get("client_name") or "").lower() or \
                       clean_q in (p.get("client_name_fa") or "").lower() or \
                       clean_q in (p.get("folder_name") or "").lower():
                        matched_pdir = p["folder_path"]
                        break
            if not matched_pdir:
                await event.reply(f"❌ No project folder found for <code>{html.escape(c_query)}</code>.", parse_mode="html")
                return

            raw_dir = os.path.join(matched_pdir, "01_raw_inputs")
            v_files = []
            if os.path.exists(raw_dir):
                for fn in os.listdir(raw_dir):
                    if fn.lower().endswith((".oga", ".ogg", ".mp3", ".wav")):
                        f_path = os.path.join(raw_dir, fn)
                        v_files.append((f_path, os.path.getmtime(f_path)))
            v_files.sort(key=lambda x: x[1], reverse=True)

            if not v_files:
                await event.reply(f"🎙️ No voice notes found in <code>01_raw_inputs/</code> for {os.path.basename(matched_pdir)}.", parse_mode="html")
                return

            target_voice = v_files[0][0]
            await event.reply(f"⏳ Transcribing latest voice note (<code>{os.path.basename(target_voice)}</code>) via Gemini Audio...", parse_mode="html")

            cname = os.path.basename(matched_pdir)
            vd = self.voice_transcriber.transcribe_and_digest(target_voice, client_name=cname)
            if vd:
                self.draft_counter += 1
                draft_id = f"D{self.draft_counter}"
                self.pending_drafts[draft_id] = {
                    "draft_id": draft_id,
                    "chat_id": event.chat_id,
                    "sender_id": 0,
                    "sender_name": cname,
                    "username": None,
                    "inquiry_type": vd.get("inquiry_type", "supervisor_defense_question"),
                    "client_message": vd.get("transcript_fa", ""),
                    "draft_reply": vd.get("suggested_draft_fa", ""),
                    "client_source": self.client,
                    "account_label": "Manual /transcribe",
                    "thinking_points": vd.get("thinking_points_en", []),
                    "voice_digest": vd,
                    "created_at": datetime.now().isoformat()
                }
                self._save_pending_drafts()
                self.voice_registry[draft_id] = {
                    "client_name": cname,
                    "voice_digest": vd,
                    "topic_key": "drafts",
                }
                card_html, _ = self.voice_transcriber.build_voice_card(
                    voice_digest=vd,
                    client_name=cname,
                    client_link=cname,
                    sender_id=0,
                    draft_id=draft_id,
                    account_label="Manual Inspection"
                )
                btns = self.build_approval_keyboard(
                    approve_label=f"🚀 Approve & Send ({draft_id})",
                    approve_data=f"send_draft_{draft_id}",
                    edit_label="✏️ Edit & Reply",
                    edit_query=f"/send_msg_{draft_id} ",
                    dismiss_label="🗑️ Dismiss",
                    dismiss_data=f"ignore_draft_{draft_id}"
                )
                if btns and len(btns) >= 2 and Button is not None:
                    btns[1].insert(0, Button.inline("📝 Full Transcript", f"voice_transcript_{draft_id}".encode("utf-8")))

                t_key = vd.get("topic_key", "supervisor_reviews")
                await self.send_to_desk(card_html, buttons=btns, topic_key=t_key, parse_mode="html")
                await event.reply(f"✅ Voice note digest card ({draft_id}) posted to Topic {t_key}!", parse_mode="html")
            else:
                await event.reply(f"❌ Failed to transcribe voice note for {cname}.", parse_mode="html")
            return

        # Milestone & Progress tracker: /milestone [client_query] or /milestones or /progress
        m_ms = re.match(r"^/(?:milestone|milestones|progress)(?:\s+(.+))?", txt)
        if m_ms:
            c_query = (m_ms.group(1) or "").strip()
            if not c_query:
                projs = self.project_manager.list_all_projects()
                if not projs:
                    await event.reply("📋 No active projects found in Google Drive.", parse_mode="html")
                    return
                lines = [f"📋 <b>Active Research Projects & Milestones ({len(projs)} clients):</b>\n"]
                for p in projs[:12]:
                    p_dir = p["folder_path"]
                    state = self.milestone_tracker.evaluate_milestones(p_dir)
                    cname = state.get("client_name") or p.get("folder_name")
                    bar = state["progress_bar"]
                    pct = state["progress_pct"]
                    scope_badge = state["scope_badge"]
                    lines.append(
                        f"• <b>{html.escape(cname)}</b>: <code>[{bar}] {pct}%</code> ({scope_badge})\n"
                        f"  👉 View card: <code>/milestone {html.escape(os.path.basename(p_dir))}</code>"
                    )
                if len(projs) > 12:
                    lines.append(f"\n<i>... and {len(projs) - 12} more projects. Use <code>/milestone &lt;client&gt;</code> to inspect.</i>")
                await event.reply("\n".join(lines), parse_mode="html")
                return
            else:
                clean_q = c_query.lstrip("@").lower()
                matched_pdir = self.project_manager.find_existing_project_by_client(clean_q)
                if not matched_pdir and clean_q.isdigit():
                    matched_pdir = self.project_manager.find_existing_project_by_client("Client", client_id=int(clean_q))
                if not matched_pdir:
                    projs = self.project_manager.list_all_projects()
                    for p in projs:
                        if clean_q in (p.get("client_name") or "").lower() or \
                           clean_q in (p.get("client_name_fa") or "").lower() or \
                           clean_q in (p.get("folder_name") or "").lower() or \
                           clean_q in (p.get("username") or "").lower():
                            matched_pdir = p["folder_path"]
                            break
                if not matched_pdir:
                    await event.reply(f"❌ No project folder found for client <code>{html.escape(c_query)}</code>.", parse_mode="html")
                    return

                state = self.milestone_tracker.evaluate_milestones(matched_pdir)
                card = self.milestone_tracker.format_milestone_card(state)
                btns = self.build_milestone_keyboard(matched_pdir, state)
                await self.send_to_desk(
                    card,
                    buttons=btns,
                    topic_key="health",
                    client_id=state.get("client_id"),
                    client_name=state.get("client_name"),
                    parse_mode="html"
                )
                await event.reply("📋 Milestone card posted to Desk!", parse_mode="html")
                return

        # Financial commands: /pay, /ledger, /invoice, /contract, /receipt, /finance
        m_pay = re.match(r"^/pay(?:\s+([^\s]+))?(?:\s+([^\s]+))?(?:\s+([^\s]+))?(?:\s+(.+))?", txt)
        if m_pay:
            c_query = (m_pay.group(1) or "").strip()
            amt_str = (m_pay.group(2) or "").strip()
            code_str = (m_pay.group(3) or "").strip()
            notes_str = (m_pay.group(4) or "").strip()

            if not c_query or not amt_str:
                await event.reply(
                    "💳 <b>Digital Saber — Record Payment</b>\n\n"
                    "Usage: <code>/pay &lt;client_name&gt; &lt;amount_tomans&gt; [tracking_code] [notes]</code>\n"
                    "Example: <code>/pay Zahra 4000000 482910 قسط_اول</code>",
                    parse_mode="html"
                )
                return

            clean_q = c_query.lstrip("@").lower()
            matched_pdir = self.project_manager.find_existing_project_by_client(clean_q)
            if not matched_pdir and clean_q.isdigit():
                matched_pdir = self.project_manager.find_existing_project_by_client("Client", client_id=int(clean_q))
            if not matched_pdir:
                projs = self.project_manager.list_all_projects()
                for p in projs:
                    if clean_q in (p.get("client_name") or "").lower() or \
                       clean_q in (p.get("client_name_fa") or "").lower() or \
                       clean_q in (p.get("folder_name") or "").lower():
                        matched_pdir = p["folder_path"]
                        break
            if not matched_pdir:
                await event.reply(f"❌ No project folder found for <code>{html.escape(c_query)}</code>.", parse_mode="html")
                return

            fa_to_en = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
            clean_amt = re.sub(r"[,\s]", "", amt_str.translate(fa_to_en))
            if not clean_amt.isdigit():
                await event.reply("❌ Invalid amount. Please enter a valid number in Tomans.", parse_mode="html")
                return
            amt_int = int(clean_amt)

            tx = self.financial_ledger.record_transaction(
                matched_pdir,
                amount_tomans=amt_int,
                tracking_code=code_str,
                notes=notes_str
            )
            rec_card = self.financial_ledger.format_receipt_card(tx, matched_pdir)
            cname = os.path.basename(matched_pdir)
            clean_cname = cname.replace(" ", "_")[:20]

            rec_btns = [
                [Button.inline("🚀 Send Receipt to Client", f"pay_sendrec_{tx['receipt_id']}_{clean_cname}".encode("utf-8"), style="success")],
                [Button.inline("💳 View Full Ledger", f"pay_ledger_{clean_cname}".encode("utf-8"), style="primary")]
            ] if Button is not None else None

            await self.send_to_desk(rec_card, buttons=rec_btns, topic_key="health", parse_mode="html")
            await event.reply(f"✅ Payment of {format_toman(amt_int)} Tomans recorded ({tx['receipt_id']})!", parse_mode="html")
            return

        m_ledger = re.match(r"^/(?:ledger|invoice)(?:\s+(.+))?", txt)
        if m_ledger:
            c_query = (m_ledger.group(1) or "").strip()
            if not c_query:
                await event.reply(
                    "📊 <b>Client Financial Ledger</b>\n\n"
                    "Usage: <code>/ledger &lt;client_name&gt;</code>\n"
                    "Example: <code>/ledger Zahra Jalali</code>",
                    parse_mode="html"
                )
                return
            clean_q = c_query.lstrip("@").lower()
            matched_pdir = self.project_manager.find_existing_project_by_client(clean_q)
            if not matched_pdir and clean_q.isdigit():
                matched_pdir = self.project_manager.find_existing_project_by_client("Client", client_id=int(clean_q))
            if not matched_pdir:
                projs = self.project_manager.list_all_projects()
                for p in projs:
                    if clean_q in (p.get("client_name") or "").lower() or \
                       clean_q in (p.get("client_name_fa") or "").lower() or \
                       clean_q in (p.get("folder_name") or "").lower():
                        matched_pdir = p["folder_path"]
                        break
            if not matched_pdir:
                await event.reply(f"❌ No project folder found for <code>{html.escape(c_query)}</code>.", parse_mode="html")
                return

            l_card, l_btns = self.financial_ledger.format_ledger_card(matched_pdir)
            await self.send_to_desk(l_card, buttons=l_btns, topic_key="health", parse_mode="html")
            await event.reply("💳 Financial ledger card posted to Topic Health!", parse_mode="html")
            return

        m_contract = re.match(r"^/contract(?:\s+([^\s]+))?(?:\s+([^\s]+))?(?:\s+(.+))?", txt)
        if m_contract:
            c_query = (m_contract.group(1) or "").strip()
            tot_str = (m_contract.group(2) or "").strip()
            scope_str = (m_contract.group(3) or "full_thesis").strip()

            if not c_query or not tot_str:
                await event.reply(
                    "📝 <b>Initialize / Update Contract</b>\n\n"
                    "Usage: <code>/contract &lt;client_name&gt; &lt;total_tomans&gt; [scope]</code>\n"
                    "Example: <code>/contract Zahra 12000000 chapter4_only</code>",
                    parse_mode="html"
                )
                return

            clean_q = c_query.lstrip("@").lower()
            matched_pdir = self.project_manager.find_existing_project_by_client(clean_q)
            if not matched_pdir and clean_q.isdigit():
                matched_pdir = self.project_manager.find_existing_project_by_client("Client", client_id=int(clean_q))
            if not matched_pdir:
                projs = self.project_manager.list_all_projects()
                for p in projs:
                    if clean_q in (p.get("client_name") or "").lower() or \
                       clean_q in (p.get("client_name_fa") or "").lower() or \
                       clean_q in (p.get("folder_name") or "").lower():
                        matched_pdir = p["folder_path"]
                        break
            if not matched_pdir:
                await event.reply(f"❌ No project folder found for <code>{html.escape(c_query)}</code>.", parse_mode="html")
                return

            fa_to_en = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
            clean_tot = re.sub(r"[,\s]", "", tot_str.translate(fa_to_en))
            if not clean_tot.isdigit():
                await event.reply("❌ Invalid contract total amount.", parse_mode="html")
                return
            tot_int = int(clean_tot)

            cname = os.path.basename(matched_pdir)
            self.financial_ledger.initialize_contract(
                matched_pdir,
                total_tomans=tot_int,
                client_name=cname,
                scope=scope_str,
                installment_count=3
            )
            l_card, l_btns = self.financial_ledger.format_ledger_card(matched_pdir)
            await self.send_to_desk(l_card, buttons=l_btns, topic_key="health", parse_mode="html")
            await event.reply(f"✅ Contract initialized for {cname} ({format_toman(tot_int)} Toman)!", parse_mode="html")
            return

        m_receipt = re.match(r"^/receipt(?:\s+(.+))?", txt)
        if m_receipt:
            c_query = (m_receipt.group(1) or "").strip()
            if not c_query:
                await event.reply("Usage: <code>/receipt &lt;client_name&gt;</code>", parse_mode="html")
                return
            clean_q = c_query.lstrip("@").lower()
            matched_pdir = self.project_manager.find_existing_project_by_client(clean_q)
            if not matched_pdir:
                projs = self.project_manager.list_all_projects()
                for p in projs:
                    if clean_q in (p.get("client_name") or "").lower() or clean_q in (p.get("folder_name") or "").lower():
                        matched_pdir = p["folder_path"]
                        break
            if not matched_pdir:
                await event.reply(f"❌ No project folder found for <code>{html.escape(c_query)}</code>.", parse_mode="html")
                return

            ld = self.financial_ledger.load_ledger(matched_pdir)
            txs = ld.get("transactions", [])
            if not txs:
                await event.reply("❌ No payment transactions recorded yet for this client.", parse_mode="html")
                return

            rec_card = self.financial_ledger.format_receipt_card(txs[-1], matched_pdir)
            cname = os.path.basename(matched_pdir)
            clean_cname = cname.replace(" ", "_")[:20]
            rec_btns = [
                [Button.inline("🚀 Send Receipt to Client", f"pay_sendrec_{txs[-1]['receipt_id']}_{clean_cname}".encode("utf-8"), style="success")],
                [Button.inline("💳 View Full Ledger", f"pay_ledger_{clean_cname}".encode("utf-8"), style="primary")]
            ] if Button is not None else None
            await self.send_to_desk(rec_card, buttons=rec_btns, topic_key="health", parse_mode="html")
            await event.reply("🧾 Official receipt card posted to Topic Health!", parse_mode="html")
            return

        if txt.strip() in ["/finance", "/fin", "/financials"]:
            f_card = self.financial_ledger.format_global_summary_card()
            btns = [[Button.inline("🔄 Refresh Financials", b"cmd_finance", style="primary")]] if Button is not None else None
            await self.send_to_desk(f_card, buttons=btns, topic_key="health", parse_mode="html")
            await event.reply("💰 Executive financial portfolio card posted to Topic Health!", parse_mode="html")
            return

        # Prepare deliverable dispatch: /send_file <client_query> [filename_query]
        m_send_file = re.match(r"^/(?:send_file|deliver)(?:\s+([^\s]+))?(?:\s+(.+))?", txt)
        if m_send_file and not txt.startswith("/send_del_"):
            c_query = (m_send_file.group(1) or "").strip()
            file_query = (m_send_file.group(2) or "").strip()
            if not c_query:
                await event.reply(
                    "⚠️ Please specify client identifier and optional filename:\n"
                    "Example: <code>/send_file @username</code> or <code>/send_file Zahra فصل_چهارم</code>",
                    parse_mode="html"
                )
                return

            clean_q = c_query.lstrip("@").lower()
            matched_pdir = self.project_manager.find_existing_project_by_client(clean_q)
            target_meta = {}
            if not matched_pdir and clean_q.isdigit():
                matched_pdir = self.project_manager.find_existing_project_by_client("Client", client_id=int(clean_q))
            if not matched_pdir:
                projs = self.project_manager.list_all_projects()
                for p in projs:
                    if clean_q in (p.get("client_name") or "").lower() or \
                       clean_q in (p.get("client_name_fa") or "").lower() or \
                       clean_q in (p.get("folder_name") or "").lower() or \
                       clean_q in (p.get("username") or "").lower():
                        matched_pdir = p["folder_path"]
                        target_meta = p
                        break
            if not matched_pdir:
                await event.reply(f"❌ No project folder found for client <code>{html.escape(c_query)}</code>.", parse_mode="html")
                return

            if not target_meta and os.path.exists(os.path.join(matched_pdir, "project_meta.json")):
                try:
                    with open(os.path.join(matched_pdir, "project_meta.json"), "r", encoding="utf-8") as f:
                        target_meta = json.load(f)
                except Exception:
                    pass

            cname = target_meta.get("client_name_fa") or target_meta.get("client_name") or os.path.basename(matched_pdir)
            cid = target_meta.get("telegram_id")
            uname = target_meta.get("telegram_username") or target_meta.get("username")

            # Locate deliverable file
            if file_query:
                chosen_file = self.project_manager.find_deliverable_file(matched_pdir, file_query)
                if not chosen_file:
                    await event.reply(f"❌ File matching <code>{html.escape(file_query)}</code> not found in <code>03_deliverables/</code> for <b>{html.escape(cname)}</b>.", parse_mode="html")
                    return
            else:
                d_files = self.project_manager.list_project_deliverables(matched_pdir)
                if not d_files:
                    await event.reply(f"📦 <code>03_deliverables/</code> is empty for <b>{html.escape(cname)}</b>.", parse_mode="html")
                    return
                if len(d_files) == 1:
                    chosen_file = d_files[0]
                else:
                    files_str = "\n".join([f"• <code>{f['filename']}</code> — <code>/send_file {html.escape(c_query)} {html.escape(f['filename'])}</code>" for f in d_files[:10]])
                    await event.reply(
                        f"📦 Multiple deliverables found for <b>{html.escape(cname)}</b>. Please specify which file to send:\n\n{files_str}",
                        parse_mode="html"
                    )
                    return

            self.deliverable_counter += 1
            del_id = f"DEL{self.deliverable_counter}"
            card_text, card_btns, caption_text = self.deliverable_dispatcher.format_dispatch_card(
                del_id=del_id,
                client_name=cname,
                username=uname,
                telegram_id=cid,
                project_dir=matched_pdir,
                chosen_file=chosen_file,
                all_files=d_files if "d_files" in locals() else [chosen_file]
            )

            self.pending_deliverables[del_id] = {
                "del_id": del_id,
                "client_name": cname,
                "telegram_id": cid,
                "username": uname,
                "folder_path": matched_pdir,
                "file_path": chosen_file["file_path"],
                "filename": chosen_file["filename"],
                "size_str": chosen_file.get("size_str", "N/A"),
                "caption": caption_text,
                "all_files": d_files if "d_files" in locals() else [chosen_file],
                "created_at": datetime.now().isoformat()
            }

            await self.send_to_desk(card_text, buttons=card_btns, topic_key="health", client_name=cname, parse_mode="html")
            print(f"[+] Prepared Deliverable dispatch card {del_id} for {cname}: {chosen_file['filename']}")
            return

        # Bundle all deliverables into .zip: /bundle <client_query>
        m_bundle = re.match(r"^/bundle(?:\s+(.+))?", txt)
        if m_bundle:
            c_query = (m_bundle.group(1) or "").strip()
            if not c_query:
                await event.reply("📦 <b>Bundle Deliverables</b>\nUsage: <code>/bundle &lt;client_name&gt;</code>\nExample: <code>/bundle Zahra Jalali</code>", parse_mode="html")
                return
            clean_q = c_query.lstrip("@").lower()
            matched_pdir = self.project_manager.find_existing_project_by_client(clean_q)
            if not matched_pdir:
                projs = self.project_manager.list_all_projects()
                for p in projs:
                    if clean_q in (p.get("client_name") or "").lower() or clean_q in (p.get("folder_name") or "").lower():
                        matched_pdir = p["folder_path"]
                        break
            if not matched_pdir:
                await event.reply(f"❌ No project folder found for <code>{html.escape(c_query)}</code>.", parse_mode="html")
                return

            d_files = self.project_manager.list_project_deliverables(matched_pdir)
            if not d_files:
                await event.reply("📦 <code>03_deliverables/</code> is empty for this project.", parse_mode="html")
                return

            file_paths = [f["file_path"] for f in d_files if not f["file_path"].endswith(".zip")]
            if not file_paths:
                await event.reply("❌ No uncompressed files found to bundle.", parse_mode="html")
                return

            zip_path = self.deliverable_dispatcher.bundle_deliverables_zip(matched_pdir, file_paths)
            z_size = os.path.getsize(zip_path)
            z_size_str = f"{z_size / (1024*1024):.1f} MB" if z_size > 1024*1024 else f"{z_size / 1024:.1f} KB"
            z_file_info = {
                "filename": os.path.basename(zip_path),
                "file_path": zip_path,
                "size_str": z_size_str
            }

            self.deliverable_counter += 1
            del_id = f"DEL{self.deliverable_counter}"
            cname = os.path.basename(matched_pdir)
            card_text, card_btns, caption_text = self.deliverable_dispatcher.format_dispatch_card(
                del_id=del_id,
                client_name=cname,
                username=None,
                telegram_id=None,
                project_dir=matched_pdir,
                chosen_file=z_file_info,
                all_files=[z_file_info]
            )

            self.pending_deliverables[del_id] = {
                "del_id": del_id,
                "client_name": cname,
                "folder_path": matched_pdir,
                "file_path": zip_path,
                "filename": os.path.basename(zip_path),
                "size_str": z_size_str,
                "caption": caption_text,
                "created_at": datetime.now().isoformat()
            }

            await self.send_to_desk(card_text, buttons=card_btns, topic_key="health", parse_mode="html")
            await event.reply(f"📦 Zipped {len(file_paths)} files into <code>{os.path.basename(zip_path)}</code> ({z_size_str}) and staged dispatch card ({del_id})!", parse_mode="html")
            return

        # Approve & Send deliverable file: /send_del_DEL101 or /send_del_DEL101 <custom caption>
        m_send_del = re.match(r"^/send_del_(DEL\d+)(?:\s+(.+))?", txt, flags=re.DOTALL)
        if m_send_del:
            del_id = m_send_del.group(1)
            custom_caption = (m_send_del.group(2) or "").strip()
            if del_id in self.pending_deliverables:
                entry = self.pending_deliverables[del_id]
                caption_to_send = custom_caption if custom_caption else entry["caption"]
                target_dest = entry.get("telegram_id")
                if target_dest is None:
                    if entry.get("username"):
                        target_dest = entry["username"].lstrip("@")
                    else:
                        target_dest = entry.get("client_name")
                elif isinstance(target_dest, str) and target_dest.isdigit():
                    target_dest = int(target_dest)

                file_path = entry["file_path"]
                if not os.path.exists(file_path):
                    await event.reply(f"❌ Deliverable file not found on disk: <code>{html.escape(file_path)}</code>", parse_mode="html")
                    return

                target_client = entry.get("client_source") or self.client
                try:
                    try:
                        ent = await target_client.get_entity(target_dest)
                    except Exception:
                        ent = target_dest
                    await target_client.send_file(ent, file=file_path, caption=caption_to_send)
                    if entry.get("folder_path"):
                        self.project_manager.record_deliverable_dispatched(
                            entry["folder_path"],
                            entry["filename"],
                            entry["client_name"]
                        )
                    await event.reply(
                        f"✅ Deliverable <b>{html.escape(entry['filename'])}</b> was successfully dispatched to <b>{html.escape(entry['client_name'])}</b> via Saber's personal account and archived in drafts_archive.",
                        parse_mode="html"
                    )
                    del self.pending_deliverables[del_id]
                except Exception as send_err:
                    await event.reply(f"❌ Failed to send deliverable {del_id}: {send_err}", parse_mode="html")
            else:
                await event.reply(f"❌ Deliverable ID {del_id} not found or already sent.", parse_mode="html")
            return

        # Ignore deliverable draft: /ignore_del_DEL101
        m_ign_del = re.match(r"^/ignore_del_(DEL\d+)", txt)
        if m_ign_del:
            del_id = m_ign_del.group(1)
            if del_id in self.pending_deliverables:
                cname = self.pending_deliverables[del_id]["client_name"]
                del self.pending_deliverables[del_id]
                await event.reply(f"🗑️ Deliverable draft {del_id} for {cname} was dismissed.", parse_mode="html")
            else:
                await event.reply(f"❌ Deliverable ID {del_id} not found.", parse_mode="html")
            return
