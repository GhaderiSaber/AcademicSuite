"""
morning_briefing.py — Daily Scheduled Morning Academic Executive Briefing Engine

Aggregates:
1. Fleet Project Health: Total managed projects, Active/Healthy, Attention Needed, Stalled, Completed.
2. Scope-Adaptive Milestone Progress: Real-time progress bars for top active clients.
3. Pending Deliverables in Google Drive: Completed files sitting in 03_deliverables/ awaiting dispatch.
4. Stalled Client Inactivity Alerts: Clients silent > 3 days requiring gentle check-ins.
5. Commercial Quotations Status: Pending vs approved proposals and fees.

Formats modern 2026 Telegram box-drawing container cards with expandable sections and styled action buttons.
"""

import os
import json
import html
from datetime import datetime, date
from typing import Dict, List, Any, Optional

try:
    from telethon import Button
except ImportError:
    Button = None

try:
    from financial_ledger import format_toman
except ImportError:
    def format_toman(amount, lang="fa"):
        return f"{amount:,}"


class AcademicMorningBriefing:
    """Compiles and formats the daily morning executive briefing for Topic 116 (Health)."""

    def __init__(self, project_manager, milestone_tracker, financial_ledger=None, storage_dir: Optional[str] = None):
        self.pm = project_manager
        self.mt = milestone_tracker
        self.fl = financial_ledger
        self.storage_dir = storage_dir or os.path.join(os.path.dirname(__file__), "userbot_storage")
        os.makedirs(self.storage_dir, exist_ok=True)
        self.date_lock_file = os.path.join(self.storage_dir, "last_briefing_date.txt")

    def should_fire_today(self, target_time_str: str = "08:30") -> bool:
        """
        Check if briefing should fire at the current local time today.
        Guarantees firing only once per calendar day.
        """
        now = datetime.now()
        today_str = now.strftime("%Y-%m-%d")

        # Check if already fired today
        if os.path.exists(self.date_lock_file):
            try:
                with open(self.date_lock_file, "r", encoding="utf-8") as f:
                    last_date = f.read().strip()
                if last_date == today_str:
                    return False
            except Exception:
                pass

        # Check time match (within a 2-minute window)
        try:
            target_hour, target_minute = map(int, target_time_str.split(":"))
            if now.hour == target_hour and 0 <= (now.minute - target_minute) <= 2:
                return True
        except Exception:
            pass

        return False

    def mark_fired_today(self):
        """Record today's date in lock file to prevent duplicate daily briefings."""
        today_str = datetime.now().strftime("%Y-%m-%d")
        try:
            with open(self.date_lock_file, "w", encoding="utf-8") as f:
                f.write(today_str)
        except Exception as e:
            print(f"[-] Error saving briefing date lock: {e}")

    def compile_briefing_data(self, pending_quotes: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Compile full briefing data model from Google Drive projects and milestone tracker.
        """
        # 1. Health Audit
        audit = self.pm.audit_all_projects_health()

        # 2. Milestones for top active/stalled projects
        projects = self.pm.list_all_projects()
        milestone_states = []
        ready_deliverables = []

        for p in projects:
            p_dir = p["folder_path"]
            # Check deliverables
            dfs = self.pm.list_project_deliverables(p_dir)
            if dfs:
                cname = p.get("client_name_fa") or p.get("client_name") or p.get("folder_name")
                ready_deliverables.append({
                    "client_name": cname,
                    "folder_path": p_dir,
                    "files": dfs
                })

            # Check milestones for non-completed projects
            if p.get("status") != "completed":
                try:
                    m_state = self.mt.evaluate_milestones(p_dir)
                    milestone_states.append(m_state)
                except Exception:
                    pass

        # Sort milestone states: highest progress first
        milestone_states.sort(key=lambda s: s["progress_pct"], reverse=True)

        # 3. Follow-up candidates (>3 days silent)
        follow_ups = audit.get("follow_ups", [])

        # 4. Quotations
        pending_q_list = list((pending_quotes or {}).values())

        # 5. Financial Pulse
        fin_summary = None
        if self.fl:
            try:
                fin_summary = self.fl.get_global_financial_summary()
            except Exception as e:
                print(f"[-] Error getting financial summary for briefing: {e}")

        return {
            "timestamp": datetime.now().isoformat(),
            "date_str": datetime.now().strftime("%A, %d %B %Y"),
            "time_str": datetime.now().strftime("%H:%M"),
            "total_projects": audit["total_projects"],
            "healthy_count": audit["healthy_count"],
            "attention_count": audit["attention_count"],
            "stalled_count": audit["stalled_count"],
            "completed_count": audit["completed_count"],
            "milestone_states": milestone_states,
            "ready_deliverables": ready_deliverables,
            "follow_ups": follow_ups,
            "pending_quotes_count": len(pending_q_list),
            "financial_summary": fin_summary
        }

    def format_briefing_card(self, data: Dict[str, Any]) -> str:
        """
        Format briefing data into an executive 2026 box-drawing Telegram card.
        """
        date_str = data["date_str"]
        time_str = data["time_str"]
        total = data["total_projects"]
        healthy = data["healthy_count"]
        attention = data["attention_count"]
        stalled = data["stalled_count"]
        completed = data["completed_count"]
        m_states = data["milestone_states"]
        deliverables = data["ready_deliverables"]
        follow_ups = data["follow_ups"]
        pending_quotes = data["pending_quotes_count"]
        fin_summary = data.get("financial_summary")

        lines = [
            "╭─ 🌅 <b>MORNING ACADEMIC EXECUTIVE BRIEFING</b> ────────",
            f"│ 📅 <b>Date:</b> <code>{date_str}</code>  •  <code>{time_str}</code>",
            f"│ 🏛️ <b>Workspace:</b> <code>Google Drive / My Work</code>",
            f"│ 📊 <b>Total Clients:</b> <b>{total} Projects Managed</b>",
            f"│ 🩺 <b>Fleet Health:</b> 🟢 {healthy} Active  •  🟡 {attention} Review  •  🔴 {stalled} Stalled",
            "╰──────────────────────────────────────────────────",
            ""
        ]

        # Section 1: Dynamic Active Milestones Digest
        if m_states:
            lines.append("📋 <b>ACTIVE RESEARCH MILESTONES DIGEST</b>")
            lines.append("<blockquote expandable>")
            for idx, ms in enumerate(m_states[:6]):
                is_last = (idx == min(len(m_states), 6) - 1)
                pfx = "└" if is_last else "├"
                cname = html.escape(ms.get("client_name", "Client"))
                bar = ms["progress_bar"]
                pct = ms["progress_pct"]
                curr = ms["current_stage_code"]
                badge = ms["scope_badge"]
                lines.append(f"{pfx} 🔹 <b>{cname}</b>: <code>[{bar}] {pct}%</code> ({badge})")
                lines.append(f"│   └ <i>Current Phase: <b>{curr}</b> • {ms['completed_count']}/{ms['total_count']} Completed</i>")
            if len(m_states) > 6:
                lines.append(f"└ <i>... and {len(m_states) - 6} more active projects. Tap /milestones for full catalog.</i>")
            lines.append("</blockquote>\n")

        # Section 2: Ready Deliverables in Drive
        if deliverables:
            lines.append(f"📦 <b>READY DELIVERABLES IN GOOGLE DRIVE ({len(deliverables)} Clients)</b>")
            lines.append("<blockquote expandable>")
            for idx, d in enumerate(deliverables[:5]):
                is_last = (idx == min(len(deliverables), 5) - 1)
                pfx = "└" if is_last else "├"
                cname = html.escape(d["client_name"])
                f_count = len(d["files"])
                top_f = d["files"][0]
                fname = html.escape(top_f["filename"])
                fsz = top_f.get("size_str", "")
                extra = f" <i>(+{f_count - 1} more)</i>" if f_count > 1 else ""
                lines.append(f"{pfx} 📁 <b>{cname}:</b> <code>{fname}</code> ({fsz}){extra}")
            lines.append("</blockquote>\n")

        # Section 3: Financial Pulse & Receivables
        if fin_summary and fin_summary.get("total_portfolio_tomans", 0) > 0:
            coll_str = format_toman(fin_summary["total_collected_tomans"])
            rec_str = format_toman(fin_summary["total_receivables_tomans"])
            lines.append("💰 <b>FINANCIAL PULSE & RECEIVABLES</b>")
            lines.append("<blockquote expandable>")
            lines.append(f"├ 💵 <b>مجموع وصولی‌ها:</b> <code>{coll_str}</code> تومان")
            lines.append(f"├ ⏳ <b>مطالبات در جریان:</b> <code>{rec_str}</code> تومان ({fin_summary['active_installment_count']} پرونده)")
            if fin_summary.get("overdue_count", 0) > 0:
                lines.append(f"└ ⚠️ <b>اقساط معوقه:</b> <b>{fin_summary['overdue_count']}</b> مورد نیازمند پیگیری")
            else:
                lines.append("└ ✅ <b>وضعیت اقساط:</b> منظم و بدون تاخیر سررسید")
            lines.append("</blockquote>\n")

        # Section 4: Stalled Client Inactivity Alerts
        if follow_ups:
            lines.append(f"⚠️ <b>CLIENTS REQUIRING ATTENTION & FOLLOW-UP ({len(follow_ups)} Clients)</b>")
            lines.append("<blockquote expandable>")
            for idx, fu in enumerate(follow_ups[:5]):
                is_last = (idx == min(len(follow_ups), 5) - 1)
                pfx = "└" if is_last else "├"
                cname = html.escape(fu["client_name"])
                days = fu.get("days_silent", 0)
                reason = html.escape(fu.get("reason", "Inactivity"))
                badge = fu.get("health_badge", "🟡")
                lines.append(f"{pfx} {badge} <b>{cname}</b> — <b>{days} days silent</b>")
                lines.append(f"│   └ <i>Reason: {reason}</i>")
            lines.append("</blockquote>\n")
        else:
            lines.append("✨ <b>CLIENT ENGAGEMENT:</b> All active projects are within healthy interaction windows.\n")

        # Section 5: Quotations status
        if pending_quotes > 0:
            lines.append(f"📑 <b>COMMERCIAL QUOTATIONS:</b> <code>{pending_quotes} proposal(s)</code> pending client approval.\n")

        lines.append("<i>Tap <b>Dispatch Follow-ups</b> to review stalled clients, or <b>Refresh</b> to rescan Google Drive.</i>")

        return "\n".join(lines)

    def build_briefing_keyboard(self, data: Dict[str, Any]) -> Optional[List[List[Any]]]:
        """Build 2026 styled action keyboard for morning briefing card."""
        if Button is None:
            return None

        fu_count = len(data.get("follow_ups", []))
        d_count = len(data.get("ready_deliverables", []))

        # Row 1: Primary action (Dispatch follow-ups if available)
        if fu_count > 0:
            row1 = [Button.inline(f"⚡ Review Follow-ups ({fu_count})", b"cmd_briefing_followups", style="success")]
        else:
            row1 = [Button.inline("✅ All Clients In Sync", b"noop", style="success")]

        # Row 2: Secondary tools
        row2 = [
            Button.inline(f"📦 Deliverables ({d_count})", b"cmd_deliverables", style="primary"),
            Button.inline("💰 Financials", b"cmd_finance", style="primary"),
            Button.inline("🔄 Refresh", b"cmd_briefing_refresh", style="primary")
        ]
        return [row1, row2]
