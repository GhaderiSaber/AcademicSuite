"""Callback query dispatcher for Telegram Bot inline buttons."""

from __future__ import annotations

from datetime import datetime
import html
import json
import os
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

from project_drive_manager import clean_drive_display_path
from financial_ledger import format_toman

try:
    from proposal_price_estimator import format_telegram_card
except ImportError:
    format_telegram_card = None


class CallbackQueryDispatcher:
    """Dispatches inline button callback queries (draft approvals, quotes, deliverables, payments, etc.)."""

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
        """Handle inline button callback query."""
        data = (event.data or b"").decode("utf-8")
        now_str = datetime.now().strftime("%H:%M")

        if data == "noop":
            await event.answer("ℹ️ This item has already been dispatched.", alert=False)
            return

        if data.startswith("send_draft_"):
            did = data.split("send_draft_")[1]
            if did in self.pending_drafts:
                entry = self.pending_drafts[did]
                target_client = entry.get("client_source")
                if not target_client:
                    if "Second Account" in entry.get("account_label", "") and self.client2:
                        target_client = self.client2
                    else:
                        target_client = self.client
                await target_client.send_message(entry["chat_id"], entry["draft_reply"])
                await event.answer(f"🚀 Response {did} dispatched to client!", alert=False)
                try:
                    done_badge = [[Button.inline(f"✅ Dispatched ({did}) at {now_str}", b"noop", style="success")]] if Button is not None else None
                    await event.edit(
                        f"{event.message.text}\n\n✅ <b>Response was approved and dispatched to client at {now_str} via {entry.get('account_label', 'Personal Account')}.</b>",
                        buttons=done_badge,
                        parse_mode="html"
                    )
                except Exception:
                    pass
                del self.pending_drafts[did]
                self._save_pending_drafts()
            else:
                await event.answer(f"❌ Draft ID {did} expired or not found.", alert=True)

        elif data.startswith("ignore_draft_"):
            did = data.split("ignore_draft_")[1]
            if did in self.pending_drafts:
                cname = self.pending_drafts[did].get("sender_name", "Client")
                del self.pending_drafts[did]
                self._save_pending_drafts()
                await event.answer("🗑️ Draft dismissed.", alert=False)
                try:
                    tombstone = (
                        f"╭─ 🗑️ <b>DRAFT DISMISSED</b> ─────────────────────────\n"
                        f"│ 🆔 <b>Draft ID:</b> <code>{did}</code>  •  <code>{now_str}</code>\n"
                        f"│ 👤 <b>Client:</b> {html.escape(cname)}\n"
                        f"╰──────────────────────────────────────────────────"
                    )
                    await event.edit(tombstone, buttons=None, parse_mode="html")
                except Exception:
                    pass
            else:
                await event.answer(f"❌ Draft ID {did} not found.", alert=True)

        elif data.startswith("voice_transcript_"):
            did = data.split("voice_transcript_")[1]
            entry = None
            if did in self.voice_registry:
                entry = self.voice_registry[did]
            elif did in self.pending_drafts and "voice_digest" in self.pending_drafts[did]:
                entry = {
                    "client_name": self.pending_drafts[did].get("sender_name", "Client"),
                    "voice_digest": self.pending_drafts[did]["voice_digest"],
                    "topic_key": self.pending_drafts[did].get("topic_key", "drafts"),
                }
            if entry and "voice_digest" in entry:
                vd = entry["voice_digest"]
                transcript = vd.get("transcript_fa", "")
                cname = entry.get("client_name", "Client")
                await event.answer("📝 Full transcript retrieved!", alert=False)
                msg = (
                    f"📝 <b>Persian Voice Note Transcription</b>\n"
                    f"🆔 <code>{did}</code>  •  👤 <b>{html.escape(cname)}</b>\n\n"
                    f"<blockquote expandable>«{html.escape(transcript)}»</blockquote>"
                )
                t_key = entry.get("topic_key", "drafts")
                await self.send_to_desk(msg, topic_key=t_key, parse_mode="html")
            else:
                await event.answer(f"❌ Voice transcript for {did} not found.", alert=True)

        elif data.startswith("send_fu_"):
            fuid = data.split("send_fu_")[1]
            if fuid in self.pending_followups:
                entry = self.pending_followups[fuid]
                target_dest = entry.get("telegram_id") or entry.get("username") or entry.get("client_name")
                try:
                    await self.client.send_message(target_dest, entry["draft_reply"])
                    if entry.get("folder_path"):
                        self.project_manager.record_followup_dispatched(entry["folder_path"], entry["followup_type"], entry["draft_reply"])
                    await event.answer(f"🚀 Follow-up {fuid} dispatched to {entry['client_name']}!", alert=False)
                    try:
                        done_badge = [[Button.inline(f"✅ Dispatched ({fuid}) at {now_str}", b"noop", style="success")]] if Button is not None else None
                        await event.edit(
                            f"{event.message.text}\n\n✅ <b>Follow-up reminder dispatched to client at {now_str} via Saber's personal account.</b>",
                            buttons=done_badge,
                            parse_mode="html"
                        )
                    except Exception:
                        pass
                    del self.pending_followups[fuid]
                except Exception as e:
                    await event.answer(f"❌ Send failed: {e}", alert=True)
            else:
                await event.answer(f"❌ Follow-up ID {fuid} expired or not found.", alert=True)

        elif data.startswith("ignore_fu_"):
            fuid = data.split("ignore_fu_")[1]
            if fuid in self.pending_followups:
                cname = self.pending_followups[fuid].get("client_name", "Client")
                del self.pending_followups[fuid]
                await event.answer("🗑️ Follow-up reminder dismissed.", alert=False)
                try:
                    tombstone = (
                        f"╭─ 🗑️ <b>FOLLOW-UP DISMISSED</b> ─────────────────────\n"
                        f"│ 🆔 <b>Follow-Up ID:</b> <code>{fuid}</code>  •  <code>{now_str}</code>\n"
                        f"│ 👤 <b>Client:</b> {html.escape(cname)}\n"
                        f"╰──────────────────────────────────────────────────"
                    )
                    await event.edit(tombstone, buttons=None, parse_mode="html")
                except Exception:
                    pass
            else:
                await event.answer(f"❌ Follow-up ID {fuid} not found.", alert=True)

        elif data.startswith("send_del_"):
            del_id = data.split("send_del_")[1]
            if del_id in self.pending_deliverables:
                entry = self.pending_deliverables[del_id]
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
                    await event.answer("❌ File not found on disk!", alert=True)
                    return

                target_client = entry.get("client_source") or self.client
                try:
                    try:
                        ent = await target_client.get_entity(target_dest)
                    except Exception:
                        ent = target_dest
                    await target_client.send_file(ent, file=file_path, caption=entry["caption"])
                    if entry.get("folder_path"):
                        self.project_manager.record_deliverable_dispatched(
                            entry["folder_path"],
                            entry["filename"],
                            entry["client_name"]
                        )
                        try:
                            self.milestone_tracker.advance_stage(entry["folder_path"])
                        except Exception:
                            pass
                    await event.answer(f"🚀 Deliverable {entry['filename']} dispatched to {entry['client_name']}!", alert=False)
                    try:
                        done_badge = [[Button.inline(f"✅ Delivered ({del_id}) at {now_str}", b"noop", style="success")]] if Button is not None else None
                        await event.edit(
                            f"{event.message.text}\n\n✅ <b>Deliverable file dispatched to client at {now_str} via Saber's personal account.</b>",
                            buttons=done_badge,
                            parse_mode="html"
                        )
                    except Exception:
                        pass
                    del self.pending_deliverables[del_id]
                except Exception as e:
                    await event.answer(f"❌ Send failed: {e}", alert=True)
            else:
                await event.answer(f"❌ Deliverable ID {del_id} expired or not found.", alert=True)

        elif data.startswith("bundle_del_"):
            del_id = data.split("bundle_del_")[1]
            if del_id in self.pending_deliverables:
                entry = self.pending_deliverables[del_id]
                folder_p = entry.get("folder_path")
                all_f = entry.get("all_files", [])
                if not all_f and folder_p:
                    all_f = self.project_manager.list_project_deliverables(folder_p)

                file_paths = [f["file_path"] for f in all_f if not f["file_path"].endswith(".zip")]
                if not file_paths:
                    await event.answer("❌ No uncompressed files to bundle!", alert=True)
                    return

                zip_path = self.deliverable_dispatcher.bundle_deliverables_zip(folder_p, file_paths)
                target_dest = entry.get("telegram_id") or entry.get("username") or entry.get("client_name")
                target_client = entry.get("client_source") or self.client

                b_info = {"type_code": "bundled_package", "filename": os.path.basename(zip_path)}
                b_caption = self.deliverable_dispatcher.generate_delivery_manifest_caption(entry["client_name"], b_info)

                try:
                    try:
                        ent = await target_client.get_entity(target_dest)
                    except Exception:
                        ent = target_dest
                    await target_client.send_file(ent, file=zip_path, caption=b_caption)
                    if folder_p:
                        self.project_manager.record_deliverable_dispatched(folder_p, os.path.basename(zip_path), entry["client_name"])
                        try:
                            self.milestone_tracker.advance_stage(folder_p)
                        except Exception:
                            pass
                    await event.answer(f"📦 Bundled package dispatched to {entry['client_name']}!", alert=False)
                    try:
                        done_badge = [[Button.inline(f"✅ Bundled Package Sent at {now_str}", b"noop", style="success")]] if Button is not None else None
                        await event.edit(
                            f"{event.message.text}\n\n✅ <b>Bundled deliverables package ({len(file_paths)} files) was zipped and dispatched to client at {now_str}.</b>",
                            buttons=done_badge,
                            parse_mode="html"
                        )
                    except Exception:
                        pass
                    del self.pending_deliverables[del_id]
                except Exception as e:
                    await event.answer(f"❌ Send failed: {e}", alert=True)
            else:
                await event.answer(f"❌ Deliverable ID {del_id} expired.", alert=True)

        elif data.startswith("ignore_del_"):
            del_id = data.split("ignore_del_")[1]
            if del_id in self.pending_deliverables:
                cname = self.pending_deliverables[del_id].get("client_name", "Client")
                del self.pending_deliverables[del_id]
                await event.answer("🗑️ Deliverable draft dismissed.", alert=False)
                try:
                    tombstone = (
                        f"╭─ 🗑️ <b>DELIVERABLE DISMISSED</b> ───────────────────\n"
                        f"│ 🆔 <b>Deliverable ID:</b> <code>{del_id}</code>  •  <code>{now_str}</code>\n"
                        f"│ 👤 <b>Client:</b> {html.escape(cname)}\n"
                        f"╰──────────────────────────────────────────────────"
                    )
                    await event.edit(tombstone, buttons=None, parse_mode="html")
                except Exception:
                    pass
            else:
                await event.answer(f"❌ Deliverable ID {del_id} not found.", alert=True)

        elif data == "cmd_deliverables":
            projs = self.project_manager.list_all_projects()
            ready_list = []
            for p in projs:
                d_files = self.project_manager.list_project_deliverables(p["folder_path"])
                if d_files:
                    ready_list.append((p, d_files))
            if not ready_list:
                await event.answer("📦 No deliverables currently waiting in Google Drive.", alert=True)
            else:
                await event.answer(f"Found {len(ready_list)} clients with ready deliverables.")
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
                btn = [[Button.inline("❌ Close Catalog", b"cmd_close", style="danger")]] if Button is not None else None
                await self.send_to_desk("\n".join(lines), buttons=btn, topic_key="system", parse_mode="html")

        elif data == "cmd_health":
            await event.answer("🔍 Auditing project health...")
            await self.scan_and_report_project_health(trigger_event=event)

        elif data.startswith("math_apa_"):
            mid = data.split("math_apa_")[1]
            if mid in self.math_registry:
                entry = self.math_registry[mid]
                raw_apa = entry["formula_data"].get("raw_apa", "")
                await event.answer("📋 Copied APA 7 text!", alert=False)
                msg = (
                    f"📋 <b>APA 7th Text Snippet (Ready for Thesis / Paper)</b>\n"
                    f"🆔 <code>{mid}</code> • 🔬 <code>{entry['test_type'].upper()}</code>\n\n"
                    f"<code>{html.escape(raw_apa)}</code>"
                )
                await self.send_to_desk(msg, topic_key="supervisor_reviews", parse_mode="html")
            else:
                await event.answer(f"❌ Formula ID {mid} not found.", alert=True)

        elif data.startswith("math_latex_"):
            mid = data.split("math_latex_")[1]
            if mid in self.math_registry:
                entry = self.math_registry[mid]
                latex_code = entry["formula_data"].get("latex", "")
                await event.answer("📐 Copied LaTeX block!", alert=False)
                msg = (
                    f"📐 <b>LaTeX Mathematical Environment</b>\n"
                    f"🆔 <code>{mid}</code> • 🔬 <code>{entry['test_type'].upper()}</code>\n\n"
                    f'<pre><code class="language-latex">{html.escape(latex_code)}</code></pre>'
                )
                await self.send_to_desk(msg, topic_key="supervisor_reviews", parse_mode="html")
            else:
                await event.answer(f"❌ Formula ID {mid} not found.", alert=True)

        elif data.startswith("math_speech_"):
            mid = data.split("math_speech_")[1]
            if mid in self.math_registry:
                entry = self.math_registry[mid]
                speech = entry["formula_data"].get("viva_defense_fa", "")
                await event.answer("🎙️ Oral defense script retrieved!", alert=False)
                msg = (
                    f"🎙️ <b>متن دفاع شفاهی دانشجو در جلسه شورا / پیش‌دفاع</b>\n"
                    f"🆔 <code>{mid}</code> • 👤 <code>{html.escape(entry['client_name'])}</code>\n\n"
                    f"<blockquote>{html.escape(speech)}</blockquote>"
                )
                await self.send_to_desk(msg, topic_key="supervisor_reviews", parse_mode="html")
            else:
                await event.answer(f"❌ Formula ID {mid} not found.", alert=True)

        elif data.startswith("send_"):
            qid = data.split("send_")[1]
            if qid in self.pending_quotes:
                entry = self.pending_quotes[qid]
                if format_telegram_card:
                    card = format_telegram_card(entry["quote"], lang="fa")
                else:
                    card = str(entry["quote"])
                target_client = entry.get("client_source") or self.client
                await target_client.send_message(entry["chat_id"], card, parse_mode="html")
                await event.answer(f"🚀 Quotation {qid} dispatched to client!", alert=False)
                try:
                    done_badge = [[Button.inline(f"✅ Dispatched ({qid}) at {now_str}", b"noop", style="success")]] if Button is not None else None
                    await event.edit(
                        f"{event.message.text}\n\n✅ <b>Quotation was approved and dispatched to client at {now_str}.</b>",
                        buttons=done_badge,
                        parse_mode="html"
                    )
                except Exception:
                    pass
                del self.pending_quotes[qid]
            else:
                await event.answer(f"❌ Quotation ID {qid} expired or not found.", alert=True)

        elif data.startswith("ignore_"):
            qid = data.split("ignore_")[1]
            if qid in self.pending_quotes:
                del self.pending_quotes[qid]
                await event.answer("🗑️ Quotation dismissed.", alert=False)
                try:
                    tombstone = (
                        f"╭─ 🗑️ <b>QUOTATION DISMISSED</b> ─────────────────────\n"
                        f"│ 🆔 <b>Quotation ID:</b> <code>{qid}</code>  •  <code>{now_str}</code>\n"
                        f"╰──────────────────────────────────────────────────"
                    )
                    await event.edit(tombstone, buttons=None, parse_mode="html")
                except Exception:
                    pass
            else:
                await event.answer(f"❌ Quotation ID {qid} not found.", alert=True)

        elif data.startswith("ms_adv_"):
            p_name = data.split("ms_adv_")[1]
            p_dir = os.path.join(self.project_manager.work_dir, p_name)
            if not os.path.exists(p_dir):
                p_dir = self.project_manager.find_existing_project_by_client(p_name)
            if p_dir and os.path.exists(p_dir):
                new_state = self.milestone_tracker.advance_stage(p_dir)
                card = self.milestone_tracker.format_milestone_card(new_state)
                btns = self.build_milestone_keyboard(p_dir, new_state)
                await event.answer(f"🚀 Advanced to {new_state['current_stage_code']} ({new_state['progress_pct']}%)!", alert=False)
                try:
                    await event.edit(card, buttons=btns, parse_mode="html")
                except Exception:
                    pass
            else:
                await event.answer("❌ Project directory not found.", alert=True)

        elif data.startswith("ms_ref_"):
            p_name = data.split("ms_ref_")[1]
            p_dir = os.path.join(self.project_manager.work_dir, p_name)
            if not os.path.exists(p_dir):
                p_dir = self.project_manager.find_existing_project_by_client(p_name)
            if p_dir and os.path.exists(p_dir):
                new_state = self.milestone_tracker.evaluate_milestones(p_dir)
                card = self.milestone_tracker.format_milestone_card(new_state)
                btns = self.build_milestone_keyboard(p_dir, new_state)
                await event.answer(f"🔄 Milestones refreshed ({new_state['progress_pct']}% complete)", alert=False)
                try:
                    await event.edit(card, buttons=btns, parse_mode="html")
                except Exception:
                    pass
            else:
                await event.answer("❌ Project directory not found.", alert=True)

        elif data.startswith("ms_scp_"):
            p_name = data.split("ms_scp_")[1]
            p_dir = os.path.join(self.project_manager.work_dir, p_name)
            if not os.path.exists(p_dir):
                p_dir = self.project_manager.find_existing_project_by_client(p_name)
            if p_dir and os.path.exists(p_dir):
                new_state = self.milestone_tracker.cycle_scope(p_dir)
                card = self.milestone_tracker.format_milestone_card(new_state)
                btns = self.build_milestone_keyboard(p_dir, new_state)
                await event.answer(f"🔀 Switched scope to {new_state['scope_short']}", alert=False)
                try:
                    await event.edit(card, buttons=btns, parse_mode="html")
                except Exception:
                    pass
            else:
                await event.answer("❌ Project directory not found.", alert=True)

        elif data == "cmd_briefing_refresh":
            data_br = self.morning_briefing.compile_briefing_data(pending_quotes=self.pending_quotes)
            card = self.morning_briefing.format_briefing_card(data_br)
            btns = self.morning_briefing.build_briefing_keyboard(data_br)
            await event.answer("🔄 Morning briefing refreshed!", alert=False)
            try:
                await event.edit(card, buttons=btns, parse_mode="html")
            except Exception:
                pass

        elif data == "cmd_briefing_followups":
            await event.answer("⚡ Preparing follow-up drafts for stalled clients...", alert=False)
            await self.scan_and_report_project_health(trigger_event=event)

        elif data == "cmd_projects":
            projs = self.project_manager.list_all_projects()
            await event.answer(f"Found {len(projs)} active projects in Google Drive.")
            if projs:
                lines = [f"📂 <b>Active Client Projects in Google Drive ({len(projs)} projects):</b>\n"]
                for p in projs[:15]:
                    cname = p.get("client_name_fa") or p.get("client_name") or p.get("folder_name")
                    cpath = clean_drive_display_path(p['folder_path'])
                    st = p.get('status', 'pending')
                    lines.append(f"• <b>{html.escape(cname)}</b> (<i>{html.escape(st)}</i>) | <code>{html.escape(cpath)}</code>")
                if len(projs) > 15:
                    lines.append(f"\n<i>... and {len(projs) - 15} more projects in Google Drive. Use <code>/projects &lt;name&gt;</code> to filter.</i>")
                btn = [[Button.inline("❌ Close Catalog", b"cmd_close", style="danger")]] if Button is not None else None
                await self.send_to_desk("\n".join(lines), buttons=btn, topic_key="system", parse_mode="html")

        elif data == "cmd_unread":
            await event.answer("🔍 Scanning client messages...")
            await self.scan_and_process_unread_messages(trigger_event=event)

        elif data == "cmd_close":
            try:
                await event.delete()
            except Exception:
                pass

        elif data == "cmd_finance":
            await event.answer("💰 Loading portfolio financial summary...", alert=False)
            f_card = self.financial_ledger.format_global_summary_card()
            btns = [[Button.inline("🔄 Refresh Financials", b"cmd_finance", style="primary")]] if Button is not None else None
            try:
                await event.edit(f_card, buttons=btns, parse_mode="html")
            except Exception:
                await self.send_to_desk(f_card, buttons=btns, topic_key="health", parse_mode="html")

        elif data.startswith("pay_confirm_"):
            pid = data.split("pay_confirm_")[1]
            if pid in self.pending_payments:
                entry = self.pending_payments[pid]
                amt = entry.get("detected_amount", 0)
                if amt <= 0:
                    await event.answer("⚠️ Amount is 0 or invalid. Please use /pay to specify amount.", alert=True)
                else:
                    tx = self.financial_ledger.record_transaction(
                        entry["project_dir"],
                        amount_tomans=amt,
                        tracking_code=entry.get("tracking_code", ""),
                        payer_name=entry.get("client_name", "")
                    )
                    await event.answer(f"✅ Recorded {format_toman(amt)} Tomans ({tx['receipt_id']})!", alert=False)
                    try:
                        done_badge = [[Button.inline(f"✅ Payment Recorded ({tx['receipt_id']}) at {now_str}", b"noop", style="success")]] if Button is not None else None
                        await event.edit(
                            f"{event.message.text}\n\n✅ <b>Payment was verified and recorded in Google Drive at {now_str}.</b>",
                            buttons=done_badge,
                            parse_mode="html"
                        )
                    except Exception:
                        pass

                    rec_card = self.financial_ledger.format_receipt_card(tx, entry["project_dir"])
                    clean_cname = entry["client_name"].replace(" ", "_")[:20]
                    rec_btns = [
                        [Button.inline("🚀 Send Receipt to Client", f"pay_sendrec_{tx['receipt_id']}_{clean_cname}".encode("utf-8"), style="success")],
                        [Button.inline("💳 View Full Ledger", f"pay_ledger_{clean_cname}".encode("utf-8"), style="primary")]
                    ] if Button is not None else None
                    await self.send_to_desk(rec_card, buttons=rec_btns, topic_key="health", parse_mode="html")
                    del self.pending_payments[pid]
            else:
                await event.answer(f"❌ Payment notification {pid} expired or not found.", alert=True)

        elif data.startswith("pay_dismiss_"):
            pid = data.split("pay_dismiss_")[1]
            if pid in self.pending_payments:
                del self.pending_payments[pid]
                await event.answer("🗑️ Payment notification dismissed.", alert=False)
                try:
                    await event.edit(f"╭─ 🗑️ <b>PAYMENT NOTIFICATION DISMISSED</b> ───\n│ 🆔 {pid} • {now_str}\n╰──────────────────────────────────────", buttons=None, parse_mode="html")
                except Exception:
                    pass
            else:
                await event.answer("❌ Item expired.", alert=True)

        elif data.startswith("pay_ledger_"):
            c_key = data.split("pay_ledger_")[1].replace("_", " ")
            matched_pdir = self.project_manager.find_existing_project_by_client(c_key)
            if matched_pdir:
                l_card, l_btns = self.financial_ledger.format_ledger_card(matched_pdir)
                await event.answer("💳 Loaded client financial ledger!", alert=False)
                await self.send_to_desk(l_card, buttons=l_btns, topic_key="health", parse_mode="html")
            else:
                await event.answer("❌ Project directory not found.", alert=True)

        elif data.startswith("pay_refresh_"):
            c_key = data.split("pay_refresh_")[1].replace("_", " ")
            matched_pdir = self.project_manager.find_existing_project_by_client(c_key)
            if matched_pdir:
                l_card, l_btns = self.financial_ledger.format_ledger_card(matched_pdir)
                await event.answer("🔄 Ledger refreshed!", alert=False)
                try:
                    await event.edit(l_card, buttons=l_btns, parse_mode="html")
                except Exception:
                    pass
            else:
                await event.answer("❌ Project not found.", alert=True)

        elif data.startswith("pay_sendrec_"):
            parts = data.split("pay_sendrec_")[1].split("_", 1)
            rec_id = parts[0]
            c_key = parts[1].replace("_", " ") if len(parts) > 1 else ""
            matched_pdir = self.project_manager.find_existing_project_by_client(c_key)
            if matched_pdir:
                ld = self.financial_ledger.load_ledger(matched_pdir)
                matched_tx = None
                for t in ld.get("transactions", []):
                    if t.get("receipt_id") == rec_id:
                        matched_tx = t
                        break
                if not matched_tx and ld.get("transactions"):
                    matched_tx = ld["transactions"][-1]

                if matched_tx:
                    rec_text = self.financial_ledger.format_receipt_card(matched_tx, matched_pdir)
                    p_meta = {}
                    meta_path = os.path.join(matched_pdir, "project_meta.json")
                    if os.path.exists(meta_path):
                        with open(meta_path, "r", encoding="utf-8") as f:
                            p_meta = json.load(f)
                    target_dest = p_meta.get("telegram_id") or p_meta.get("telegram_username") or c_key
                    try:
                        await self.client.send_message(target_dest, rec_text, parse_mode="html")
                        await event.answer(f"🚀 Receipt {rec_id} dispatched to client!", alert=False)
                        try:
                            done_btn = [[Button.inline(f"✅ Receipt Sent at {now_str}", b"noop", style="success")]] if Button is not None else None
                            await event.edit(f"{event.message.text}\n\n✅ <b>Official receipt was sent to client via Telegram at {now_str}.</b>", buttons=done_btn, parse_mode="html")
                        except Exception:
                            pass
                    except Exception as e:
                        await event.answer(f"❌ Failed to dispatch receipt: {e}", alert=True)
                else:
                    await event.answer("❌ Receipt not found.", alert=True)
            else:
                await event.answer("❌ Project not found.", alert=True)
