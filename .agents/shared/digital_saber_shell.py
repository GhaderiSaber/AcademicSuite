#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Interactive Digital Saber Shell (digital_saber_shell.py)
--------------------------------------------------------
Terminal REPL environment for interacting directly with Digital Saber:
- Direct execution of Antigravity multi-agent workflows (chapter4, proposal, chapter5, thesis_revision)
- Instant psychometric instrument lookup across 4,880 scales in Questionnaires.xlsx
- Proposal analysis and itemized pricing quotation in Tomans
- Case-Based Reasoning precedent search across 23 historical cases
- Writing cadence and AI-cliche prose auditing
- Multi-Signal Anomaly Index (MSAI) statistical data auditing
- Telegram Co-Pilot administrative desk management and status monitoring
- Free-form natural language consultation in authentic academic Persian and English
"""

import os
import sys
import cmd
import shlex
import json
import textwrap
from typing import Dict, List, Any, Optional

# Ensure repository root is on sys.path
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from digital_saber import DigitalSaber

# Try importing questionnaire resolver
try:
    RESOLVER_DIR = os.path.join(ROOT_DIR, ".agents", "skills", "psychometric-scale-resolver", "scripts")
    if RESOLVER_DIR not in sys.path:
        sys.path.insert(0, RESOLVER_DIR)
    import questionnaire_resolver
except Exception:
    questionnaire_resolver = None

# Try importing copilot bridge
try:
    COPILOT_DIR = os.path.join(ROOT_DIR, ".agents", "skills", "digital-twin-academic-consultant", "scripts")
    if COPILOT_DIR not in sys.path:
        sys.path.insert(0, COPILOT_DIR)
    from copilot_bridge import TelegramCopilotBridge
except Exception:
    TelegramCopilotBridge = None


class DigitalSaberShell(cmd.Cmd):
    """Interactive Scholarly REPL Shell for Digital Saber."""

    intro = ""
    prompt = "Saber❯ "

    def __init__(self, saber_instance: Optional[DigitalSaber] = None, output_dir: str = "output"):
        super().__init__()
        self.saber = saber_instance or DigitalSaber()
        self.output_dir = output_dir
        self.copilot_bridge = TelegramCopilotBridge(self.saber) if TelegramCopilotBridge else None
        self._setup_terminal_formatting()

    def _setup_terminal_formatting(self):
        """Configure ANSI colors and prompt styling if terminal supports it."""
        is_tty = hasattr(sys.stdin, "isatty") and sys.stdin.isatty()
        if is_tty:
            self.c_cyan = "\033[1;36m"
            self.c_green = "\033[1;32m"
            self.c_yellow = "\033[1;33m"
            self.c_blue = "\033[1;34m"
            self.c_magenta = "\033[1;35m"
            self.c_bold = "\033[1m"
            self.c_reset = "\033[0m"
            self.prompt = f"{self.c_cyan}Saber{self.c_reset}{self.c_green}❯{self.c_reset} "
        else:
            self.c_cyan = ""
            self.c_green = ""
            self.c_yellow = ""
            self.c_blue = ""
            self.c_magenta = ""
            self.c_bold = ""
            self.c_reset = ""
            self.prompt = "Saber❯ "

    def print_banner(self):
        """Prints the scholarly startup banner."""
        cases_count = len(self.saber.case_memory.cases)
        banner = f"""
{self.c_cyan}╔═══════════════════════════════════════════════════════════════════════════════════════╗
║   🎓 DIGITAL SABER — Professional AI Research Twin (Terminal REPL)                    ║
║   Memory: {cases_count} Real Precedents  |  Skills: 27 Specialized  |  Workflows: 5 Core         ║
║   Cognitive Layers: Constitution • Case Memory • Reasoners • OpenXML • QC Audit       ║
╚═══════════════════════════════════════════════════════════════════════════════════════╝{self.c_reset}

{self.c_bold}Available Commands:{self.c_reset}
  {self.c_green}/workflow <name>{self.c_reset}    Execute dissertation workflow ({self.c_yellow}chapter2_literature, chapter4, proposal, chapter5, thesis_revision{self.c_reset})
  {self.c_green}/literature <topic>{self.c_reset} Multi-database search, parameter extraction (N, instruments) & Chapter 2
  {self.c_green}/biblio <topic>{self.c_reset}     VOSviewer keyword mapping & HistCite citation chronomap
  {self.c_green}/consult <query>{self.c_reset}    Statistical and methodological consultation with Case Precedents
  {self.c_green}/scale <name>{self.c_reset}       Search 4,880 psychometric instruments in Questionnaires.xlsx
  {self.c_green}/quote <text/file>{self.c_reset}  Extract proposal parameters, compute pricing in Tomans & Admin Card
  {self.c_green}/audit <text/file>{self.c_reset}  Prose cadence audit (anti-AI cliches) or dataset anomaly check
  {self.c_green}/cases [query]{self.c_reset}      Search & inspect 23 authenticated research precedents in Case Memory
  {self.c_green}/decisions{self.c_reset}          View high-stakes decision logs in Decision Journal
  {self.c_green}/copilot [subcmd]{self.c_reset}   Telegram Co-Pilot ({self.c_yellow}status, drafts, sim, approve{self.c_reset})
  {self.c_green}/benchmark{self.c_reset}          Run 15-dilemma Saber Similarity Benchmark
  {self.c_green}/clear, /help, /exit{self.c_reset} Terminal utilities

{self.c_magenta}💡 Or simply ask any research question in Persian or English!{self.c_reset}
"""
        print(banner)

    def precmd(self, line: str) -> str:
        """Strip leading slash from commands if present for seamless ergonomics."""
        line = line.strip()
        if line.startswith("/"):
            return line[1:]
        return line

    # -------------------------------------------------------------------------
    # Command: /workflow
    # -------------------------------------------------------------------------
    def do_workflow(self, arg: str):
        """Execute an Antigravity multi-agent workflow: /workflow <chapter2_literature|chapter4|proposal|chapter5|thesis_revision> [topic]"""
        parts = shlex.split(arg) if arg else []
        if not parts:
            print(f"{self.c_yellow}Usage: /workflow <chapter2_literature|chapter4|proposal|chapter5|thesis_revision> [optional_topic_or_file]{self.c_reset}")
            return

        wf_name = parts[0].lower()
        topic = " ".join(parts[1:]) if len(parts) > 1 else None

        valid_wfs = ["chapter2_literature", "chapter4", "proposal", "chapter5", "thesis_revision", "chapter2", "literature"]
        if wf_name not in valid_wfs:
            print(f"{self.c_yellow}Unknown workflow '{wf_name}'. Valid workflows: chapter2_literature, chapter4, proposal, chapter5, thesis_revision{self.c_reset}")
            return

        print(f"\n{self.c_cyan}[*] Launching workflow: {wf_name}...{self.c_reset}")
        res = self.saber.run_workflow(wf_name, topic_or_file=topic, output_dir=self.output_dir)
        if res and res.get("status") == "SUCCESS":
            print(f"\n{self.c_green}✅ Workflow '{wf_name}' completed successfully!{self.c_reset}")
            print(f"  • Readiness Score: {res.get('readiness_score', 'N/A')}%")
            print(f"  • Decision ID:     {res.get('decision_id', 'N/A')}")
            print(f"  • Artifacts Generated in '{self.output_dir}':")
            for a in res.get("artifacts_generated", []):
                print(f"    - {a}")

    def complete_workflow(self, text, line, begidx, endidx):
        wfs = ["chapter2_literature", "chapter4", "proposal", "chapter5", "thesis_revision"]
        if text:
            return [w for w in wfs if w.startswith(text)]
        return wfs

    # -------------------------------------------------------------------------
    # Command: /literature
    # -------------------------------------------------------------------------
    def do_literature(self, arg: str):
        """Harvest empirical studies across scientific databases and extract parameters: /literature <topic>"""
        topic = arg.strip()
        if not topic:
            print(f"{self.c_yellow}Usage: /literature <research_topic_or_keywords> (e.g. /literature درمان مبتنی بر پذیرش و تعهد فرسودگی شغلی){self.c_reset}")
            return

        print(f"\n{self.c_cyan}[*] Querying multi-database literature engine for: '{topic}'...{self.c_reset}")
        res = self.saber.run_workflow("chapter2_literature", topic_or_file=topic, output_dir=self.output_dir)
        if res and res.get("status") == "SUCCESS":
            print(f"\n{self.c_green}✅ Literature synthesis & Chapter 2 compiled successfully!{self.c_reset}")
            print(f"  • Readiness Score: {res.get('readiness_score')}%")
            print(f"  • Artifacts Generated in '{self.output_dir}':")
            for a in res.get("artifacts_generated", []):
                print(f"    - {a}")

    # -------------------------------------------------------------------------
    # Command: /biblio
    # -------------------------------------------------------------------------
    def do_biblio(self, arg: str):
        """Generate VOSviewer science mapping & HistCite chronomap: /biblio <topic>"""
        topic = arg.strip()
        if not topic:
            print(f"{self.c_yellow}Usage: /biblio <research_topic_or_keywords> (e.g. /biblio درمان مبتنی بر پذیرش و تعهد){self.c_reset}")
            return

        print(f"\n{self.c_cyan}[*] Constructing bibliometric co-occurrence & citation networks for: '{topic}'...{self.c_reset}")
        res = self.saber.run_workflow("chapter2_literature", topic_or_file=topic, output_dir=self.output_dir)
        if res and res.get("status") == "SUCCESS":
            print(f"\n{self.c_green}✅ Science mapping & chronomaps generated!{self.c_reset}")
            for a in res.get("artifacts_generated", []):
                if a.endswith(".png") or a.endswith(".txt"):
                    print(f"  • Science Map: {a}")

    # -------------------------------------------------------------------------
    # Command: /scale
    # -------------------------------------------------------------------------
    def do_scale(self, arg: str):
        """Search 4,880 psychometric instruments in Questionnaires.xlsx: /scale <name_or_abbrev>"""
        query = arg.strip()
        if not query:
            print(f"{self.c_yellow}Usage: /scale <scale_name_or_abbreviation> (e.g. /scale اضطراب کتل or /scale DASS){self.c_reset}")
            return

        if not questionnaire_resolver:
            print(f"{self.c_yellow}questionnaire_resolver module is not available.{self.c_reset}")
            return

        print(f"{self.c_cyan}[*] Searching Questionnaires.xlsx for: '{query}'...{self.c_reset}")
        try:
            results = questionnaire_resolver.search_registry(query)
            if not results:
                print(f"{self.c_yellow}موردی برای '{query}' در بانک مقیاس‌ها یافت نشد.{self.c_reset}")
                return

            print(f"\n{self.c_green}📋 نتایج جستجو در بانک جامع مقیاس‌ها ({len(results)} مقیاس یافت شد):{self.c_reset}")
            for idx, s in enumerate(results[:5], 1):
                print(f"\n{self.c_bold}{idx}. {s.get('scale_name')} ({s.get('scale_persian_name')}){self.c_reset}")
                if s.get('abbreviation'):
                    print(f"   ▫️ اختصار: {s.get('abbreviation')}")
                print(f"   ▫️ شیوه نمره‌گذاری: {s.get('scoring_method') or 'لیکرت استاندارد'}")
                subscales = s.get('subscales', [])
                if subscales:
                    print(f"   ▫️ خرده‌مقیاس‌ها ({len(subscales)} بعد):")
                    for sub in subscales[:6]:
                        sub_name = sub.get('subscale_name') or 'نمره کل'
                        items = sub.get('items_raw') or ''
                        print(f"      • {sub_name}: سوالات {items}")
        except Exception as e:
            print(f"{self.c_yellow}Error searching questionnaires: {e}{self.c_reset}")

    # -------------------------------------------------------------------------
    # Command: /consult
    # -------------------------------------------------------------------------
    def do_consult(self, arg: str):
        """Methodological & statistical consultation with Case Precedents: /consult <query>"""
        query = arg.strip()
        if not query:
            print(f"{self.c_yellow}Usage: /consult <research question, design, or hypothesis>{self.c_reset}")
            return

        print(f"\n{self.c_cyan}[*] Consulting Digital Saber Reasoning Engine & Case Precedents...{self.c_reset}")
        
        # 1. Retrieve Precedents
        precedents = self.saber.case_memory.search_precedents(query, top_k=2)
        
        # 2. Run statistical consultation
        stat_res = self.saber.stat_reasoner.consult({
            "topic": query,
            "objective": "general_inference",
            "variables": ["متغیر مستقل", "متغیر وابسته"]
        })

        rec = stat_res.get("recommendation", {})
        print(f"\n{self.c_bold}🎓 تحلیل روش‌شناختی و راهبرد آماری صابر قادری:{self.c_reset}")
        print(f"▫️ {self.c_bold}روش آماری پیشنهادی:{self.c_reset} {rec.get('method_fa')} ({rec.get('selected_method')})")
        print(f"▫️ {self.c_bold}علت انتخاب:{self.c_reset} {rec.get('rationale')}")
        print(f"▫️ {self.c_bold}پیش‌فرض‌های حیاتی:{self.c_reset} {', '.join(rec.get('assumptions_required', []))}")
        print(f"▫️ {self.c_bold}گزارش APA 7:{self.c_reset} {rec.get('apa7_reporting_template')}")

        if precedents:
            print(f"\n{self.c_cyan}📚 سابقه‌های مشابه در حافظه تجربی صابر (Case-Based Memory):{self.c_reset}")
            for p in precedents:
                c = p["case"]
                title = c.get("title_fa") or c.get("topic") or c.get("research_title") or c.get("case_id")
                design = c.get("design") or c.get("research_design") or "N/A"
                defense = c.get("defense_guidance") or c.get("defense_strategy") or "N/A"
                sim_score = p.get("similarity_score") or p.get("relevance_score") or 0.0
                print(f"  • [{c.get('case_id')}] {title}")
                print(f"    طرح: {design} | حجم نمونه: N = {c.get('sample_size')} | نمره انطباق: {sim_score:.2f}")
                print(f"    راهبرد دفاعی: {defense}")

    # -------------------------------------------------------------------------
    # Command: /quote
    # -------------------------------------------------------------------------
    def do_quote(self, arg: str):
        """Extract proposal parameters, compute pricing in Tomans & Admin Card: /quote <text or file>"""
        target = arg.strip()
        if not target:
            print(f"{self.c_yellow}Usage: /quote <proposal_text_or_filepath>{self.c_reset}")
            return

        if not self.copilot_bridge:
            print(f"{self.c_yellow}Copilot bridge is not available.{self.c_reset}")
            return

        print(f"{self.c_cyan}[*] Analyzing proposal and computing deterministic quotation...{self.c_reset}")
        record = self.copilot_bridge.draft_proposal_quote(target)
        quote = record.get("quote", {})
        total_price = quote.get("total_price_tomans", 0)

        print(f"\n{self.c_green}💰 پیش‌فاکتور تفکیکی و ارزیابی طرح پژوهش ({record['quote_id']}):{self.c_reset}")
        print(f"▫️ عنوان شناسایی‌شده: {record['params'].get('title')}")
        print(f"▫️ طرح پژوهش: {record['params'].get('design')}")
        print(f"▫️ مقطع تحصیلی: {record['params'].get('degree')}")
        print(f"▫️ حجم نمونه: N = {record['params'].get('sample_size')}")
        print(f"▫️ نرم‌افزار مورد نیاز: {record['params'].get('software')}")
        print(f"\n{self.c_bold}تفکیک مراحل و هزینه‌ها:{self.c_reset}")
        for item in quote.get("line_items", []):
            item_title = item.get("title_fa") or item.get("title_en") or item.get("title") or "مرحله پژوهش"
            price = item.get("price") or item.get("fee_tomans") or 0
            days = item.get("days") or 0
            print(f"  • {item_title}: {price:,} تومان ({days} روز)")
        print(f"\n{self.c_bold}💎 کل سرمایه‌گذاری: {total_price:,} تومان{self.c_reset} | زمان تحویل: {quote.get('estimated_days')} روز کاری")
        print(f"\n{self.c_cyan}📲 کارت تایید مدیریت برای صابر (ID: 124911145) ایجاد شد.{self.c_reset}")
        print(f"  دستور تایید مستقیم: /copilot approve {record['quote_id']}")

    # -------------------------------------------------------------------------
    # Command: /audit
    # -------------------------------------------------------------------------
    def do_audit(self, arg: str):
        """Prose cadence audit (anti-AI cliches) or dataset anomaly check: /audit <text or file>"""
        target = arg.strip()
        if not target:
            print(f"{self.c_yellow}Usage: /audit <prose_text_or_dataset_filepath>{self.c_reset}")
            return

        # Check if argument is a dataset file
        if os.path.isfile(target) and target.endswith((".xlsx", ".csv", ".sav")):
            print(f"{self.c_cyan}[*] Running Multi-Signal Anomaly Index (MSAI) statistical audit on: {target}...{self.c_reset}")
            audit_res = self.saber.stat_auditor.audit_dataset(target)
            score = audit_res.get("anomaly_score", 0.0)
            verdict = audit_res.get("verdict", "UNKNOWN")
            print(f"\n{self.c_bold}📊 نتیجه ممیزی آماری دیتاست:{self.c_reset}")
            print(f"▫️ امتیاز آنومالی (MSAI): {score:.1f}/100")
            print(f"▫️ وضعیت ممیزی: {verdict}")
            for sig in audit_res.get("flagged_signals", []):
                print(f"  ⚠️ {sig.get('signal')}: {sig.get('details')}")
        else:
            # Audit prose
            prose = target
            if os.path.isfile(target):
                try:
                    with open(target, "r", encoding="utf-8") as f:
                        prose = f.read()
                except Exception:
                    pass

            print(f"{self.c_cyan}[*] Auditing prose for academic cadence and AI cliches...{self.c_reset}")
            audit_res = self.saber.writing_reasoner.audit_prose(prose)
            print(f"\n{self.c_bold}📝 ارزیابی سبک نگارش و اصالت متن:{self.c_reset}")
            print(f"▫️ امتیاز کیفیت نگارش: {audit_res.get('quality_score')}/100")
            print(f"▫️ لحن علمی: {audit_res.get('academic_cadence_verdict')}")
            print(f"▫️ خطر کلیشه‌های هوش مصنوعی: {audit_res.get('ai_cliche_risk')}")
            cliches = audit_res.get("flagged_cliches", [])
            if cliches:
                print(f"▫️ عبارات کلیشه‌ای شناسایی‌شده:")
                for c in cliches:
                    print(f"  ❌ {c}")
            else:
                print(f"▫️ تبریک! هیچ عبارت کلیشه‌ای ماشینی شناسایی نشد.")

    # -------------------------------------------------------------------------
    # Command: /cases
    # -------------------------------------------------------------------------
    def do_cases(self, arg: str):
        """Query & inspect 23 authenticated research precedents in Case Memory: /cases [keyword]"""
        query = arg.strip()
        all_cases = self.saber.case_memory.cases

        if query:
            precedents = self.saber.case_memory.search_precedents(query, top_k=5)
            print(f"\n{self.c_green}📚 نتایج جستجو در پرونده‌های تاریخی برای '{query}' ({len(precedents)} مورد):{self.c_reset}")
            for p in precedents:
                c = p["case"]
                title = c.get("title_fa") or c.get("topic") or c.get("research_title") or c.get("case_id")
                design = c.get("design") or c.get("research_design") or "N/A"
                defense = c.get("defense_guidance") or c.get("defense_strategy") or "N/A"
                print(f"\n{self.c_bold}• [{c.get('case_id')}] {title}{self.c_reset}")
                print(f"  حوزه: {c.get('domain')} | طرح: {design} | حجم نمونه: N = {c.get('sample_size')}")
                sim_score = p.get("similarity_score") or p.get("relevance_score") or 0.0
                print(f"  انطباق: {sim_score:.2f} | ضریب اطمینان: {c.get('confidence_score')}")
                print(f"  راهبرد دفاعی: {defense}")
        else:
            print(f"\n{self.c_green}📚 فهرست پرونده‌های حافظه تجربی صابر قادری ({len(all_cases)} مورد):{self.c_reset}")
            for c in all_cases:
                title = c.get("title_fa") or c.get("topic") or c.get("research_title") or c.get("case_id")
                print(f"  • [{c.get('case_id')}] {title[:70]}... (N={c.get('sample_size')})")

    # -------------------------------------------------------------------------
    # Command: /decisions
    # -------------------------------------------------------------------------
    def do_decisions(self, arg: str):
        """View recent high-stakes decision records in Decision Journal: /decisions"""
        journal = getattr(self.saber, "decision_journal", None) or getattr(self.saber, "journal", None)
        all_decs = journal.decisions if journal else []
        recent = list(reversed(all_decs[-8:]))
        print(f"\n{self.c_green}📖 دفتر ثبت تصمیمات تخصصی (Decision Journal) - {len(recent)} تصمیم اخیر:{self.c_reset}")
        if not recent:
            print("  (هیچ ثبتی هنوز ذخیره نشده است)")
            return

        for d in recent:
            did = d.get("decision_id", "N/A")
            dt = d.get("timestamp", "N/A")[:19]
            dtype = d.get("decision_type", "N/A")
            desc = d.get("context", "") or d.get("description", "")
            rec = d.get("selected_option", "") or d.get("recommendation", "")
            print(f"\n{self.c_bold}• [{did}] {dtype} ({dt}){self.c_reset}")
            print(f"  مسئله: {desc[:80]}")
            print(f"  تصمیم صابر: {rec[:80]}")

    # -------------------------------------------------------------------------
    # Command: /copilot
    # -------------------------------------------------------------------------
    def do_copilot(self, arg: str):
        """Telegram Co-Pilot desk management: /copilot <status|drafts|sim|approve <qid>>"""
        parts = shlex.split(arg) if arg else []
        subcmd = parts[0].lower() if parts else "status"

        if not self.copilot_bridge:
            print(f"{self.c_yellow}Copilot bridge is not available.{self.c_reset}")
            return

        if subcmd == "status":
            status = self.copilot_bridge.get_status()
            print(f"\n{self.c_green}🛡️ وضعیت دستیار هوشمند و کوپایلوت تلگرام صابر قادری:{self.c_reset}")
            print(f"▫️ وضعیت سیستم: {status['status']}")
            print(f"▫️ خط‌مشی اجرایی: {status['policy']} (عدم ارسال خودکار به کلاینت)")
            print(f"▫️ شناسه ادمین (صابر): {status['admin_id']}")
            print(f"▫️ اتصالات بیزینس تلگرام: {status['active_business_connections']} فعال")
            print(f"▫️ پیش‌فاکتورهای منتظر تایید: {status['pending_quotes_count']}")
            print(f"▫️ پیش‌نویس‌های پیام منتظر تایید: {status['pending_drafts_count']}")
            print(f"▫️ چت‌های با مداخله انسانی (Muted): {status['muted_chats_count']}")

        elif subcmd == "drafts":
            quotes = self.copilot_bridge.state.get("pending_quotes", {})
            drafts = self.copilot_bridge.state.get("pending_drafts", {})
            print(f"\n{self.c_cyan}📋 کارتابل تایید مدیریت صابر (Admin Approval Queue):{self.c_reset}")
            if not quotes and not drafts:
                print("  (هیچ پیش‌نویس یا پیش‌فاکتوری منتظر تایید نیست)")
                return

            for qid, q in quotes.items():
                print(f"\n{self.c_bold}💰 پیش‌فاکتور [{qid}] برای: {q.get('client_name')}{self.c_reset}")
                print(f"   مبلغ: {q['quote'].get('total_price_tomans', 0):,} تومان | زمان: {q['quote'].get('estimated_days')} روز")
                print(f"   دستور تایید: /copilot approve {qid}")

            for did, d in drafts.items():
                print(f"\n{self.c_bold}💬 پیش‌نویس پاسخ [{did}] برای: {d.get('client_name')}{self.c_reset}")
                print(f"   متن: {d.get('draft_text')[:100]}...")

        elif subcmd == "approve":
            if len(parts) < 2:
                print(f"{self.c_yellow}Usage: /copilot approve <quote_id> [optional_price]{self.c_reset}")
                return
            qid = parts[1].upper()
            adj_price = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else None
            res = self.copilot_bridge.approve_quote(qid, adj_price)
            if res.get("status") == "success":
                print(f"{self.c_green}✅ {res.get('message')}{self.c_reset}")
            else:
                print(f"{self.c_yellow}❌ {res.get('message')}{self.c_reset}")

        elif subcmd == "sim":
            print(f"{self.c_cyan}[*] Executing end-to-end Co-Pilot client-admin simulation...{self.c_reset}")
            sim_res = self.copilot_bridge.run_simulation()
            if sim_res.get("status") == "success":
                print(f"\n{self.c_green}✅ تمام ۶ سناریوی شبیه‌سازی کوپایلوت تلگرام با موفقیت اجرا شد!{self.c_reset}")
        else:
            print(f"{self.c_yellow}Unknown copilot subcommand '{subcmd}'. Valid: status, drafts, sim, approve{self.c_reset}")

    # -------------------------------------------------------------------------
    # Command: /benchmark
    # -------------------------------------------------------------------------
    def do_benchmark(self, arg: str):
        """Run 15-dilemma Saber Similarity Benchmark: /benchmark"""
        print(f"\n{self.c_cyan}[*] Running 15-Dilemma Saber Benchmark against Baseline LLM...{self.c_reset}")
        self.saber.run_benchmark(compare_baseline=True)

    # -------------------------------------------------------------------------
    # Command: /clear, /exit, /help
    # -------------------------------------------------------------------------
    def do_clear(self, arg: str):
        """Clear terminal screen: /clear"""
        os.system("clear" if os.name != "nt" else "cls")

    def do_exit(self, arg: str):
        """Exit Digital Saber Shell: /exit"""
        print(f"\n{self.c_green}خدانگهدار! با آرزوی موفقیت در پژوهش‌های دانشگاهی.{self.c_reset}")
        return True

    def do_quit(self, arg: str):
        """Exit Digital Saber Shell: /quit"""
        return self.do_exit(arg)

    def do_EOF(self, arg: str):
        """Exit on EOF (Ctrl+D)"""
        print()
        return self.do_exit(arg)

    # -------------------------------------------------------------------------
    # Free-Form Natural Language Fallback
    # -------------------------------------------------------------------------
    def default(self, line: str):
        """Handles conversational natural language inputs in Persian or English."""
        text = line.strip()
        if not text:
            return

        # Check if line looks like an unrecognized slash command
        if text.startswith("/"):
            print(f"{self.c_yellow}دستور '{text}' شناخته نشد. برای مشاهده راهنما دستور /help را وارد کنید.{self.c_reset}")
            return

        print(f"\n{self.c_cyan}[*] پردازش استعلام علمی در حافظه تجربی و موتورهای استدلال صابر قادری...{self.c_reset}")

        # 1. Search Case Precedents
        precedents = self.saber.case_memory.search_precedents(text, top_k=2)

        # 2. Check intent: Psychometrics vs Methodology/Stats vs Proposal
        import re
        cleaned_for_scale = re.sub(r"(پیش‌آزمون|پس‌آزمون|پیش آزمون|پس آزمون|آزمون آماری|آزمون فرضیه|آزمون تفاوت)", "", text)
        is_scale = any(k in cleaned_for_scale for k in ["پرسشنامه", "مقیاس", "ابزار اندازه‌گیری", "scale", "questionnaire"]) or (
            "آزمون" in cleaned_for_scale and any(k in cleaned_for_scale for k in ["روانسنجی", "نمره‌گذاری", "روایی", "پایایی", "خرده‌مقیاس"])
        )
        is_proposal = any(k in text for k in ["عنوان:", "جامعه:", "طرح:", "پروپوزال", "پیش فاکتور", "هزینه"])

        if is_scale and questionnaire_resolver:
            # Extract possible scale name
            search_query = text
            for prefix in ["پرسشنامه", "مقیاس", "ابزار"]:
                if prefix in search_query:
                    search_query = search_query.split(prefix)[-1].strip()
            print(f"  • جستجوی خودکار در ۴,۸۸۰ پرسشنامه برای: '{search_query[:30]}'")
            self.do_scale(search_query[:30])
            return

        if is_proposal and self.copilot_bridge:
            print(f"  • تشخیص خودکار طرح پژوهش و ارزیابی هزینه...")
            self.do_quote(text)
            return

        # Default scholarly academic consultation
        stat_plan = self.saber.stat_reasoner.consult({
            "topic": text,
            "objective": "general_inference",
            "variables": ["متغیر اول", "متغیر دوم"]
        })
        rec = stat_plan.get("recommendation", {})

        print(f"\n{self.c_bold}🎓 پاسخ تحلیلی صابر قادری:{self.c_reset}")
        response = (
            f"سلام وقتتون بخیر، در خصوص مسئله مطرح‌شده؛ بر اساس اصول روش تحقیق تجربی و استانداردهای "
            f"آماری APA 7، رویکرد پیشنهادی عبارت است از استفاده از {rec.get('method_fa')} ({rec.get('selected_method')}).\n"
            f"علت این انتخاب: {rec.get('rationale')}\n"
            f"نکته کلیدی که در جلسه دفاع حتماً باید مستند شود، بررسی پیش‌فرض‌های {', '.join(rec.get('assumptions_required', []))} است."
        )
        print(textwrap.fill(response, width=80))

        if precedents:
            print(f"\n{self.c_cyan}📚 سابقه مرتبط در پرونده‌های واقعی صابر (CBR):{self.c_reset}")
            top_case = precedents[0]["case"]
            title = top_case.get("title_fa") or top_case.get("topic") or top_case.get("research_title") or top_case.get("case_id")
            defense = top_case.get("defense_guidance") or top_case.get("defense_strategy") or "N/A"
            print(f"  • پرونده: {title}")
            print(f"    راهبرد موفق دفاع: {defense}")


def run_shell(saber: Optional[DigitalSaber] = None, output_dir: str = "output"):
    """Launches the interactive shell."""
    shell = DigitalSaberShell(saber_instance=saber, output_dir=output_dir)
    shell.print_banner()
    try:
        shell.cmdloop()
    except KeyboardInterrupt:
        print("\n\nخدانگهدار!")
    except Exception as e:
        print(f"\nShell error: {e}")


if __name__ == "__main__":
    run_shell()
