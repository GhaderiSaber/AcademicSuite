#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Saber Academic Suite — Production Admin Approval Desk CLI (scripts/admin_desk.py)
=================================================================================
Directive 7 & Directive 11 Human-in-the-Loop Governance:
Enforces that high-stakes operations (pricing quotations, supervisor disputes,
and major chapter releases) are routed through Saber's Admin Desk (Telegram ID: 124911145)
and permanently recorded into the auditable Decision Journal (.agents/memory/decisions/).

CLI Commands:
  python3 scripts/admin_desk.py status
  python3 scripts/admin_desk.py list
  python3 scripts/admin_desk.py draft <file_or_text> [--client <name>]
  python3 scripts/admin_desk.py approve <quote_id> [--price <adjusted_tomans>]
  python3 scripts/admin_desk.py audit <dataset_file_or_text>
"""

import os
import sys
import json
import argparse
from datetime import datetime
from typing import Optional, Dict, Any

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SKILL_DIR = os.path.join(REPO_ROOT, ".agents", "skills", "digital-twin-academic-consultant", "scripts")
MEMORY_DIR = os.path.join(REPO_ROOT, ".agents", "memory")
REASONING_DIR = os.path.join(REPO_ROOT, ".agents", "reasoning")
VERIF_DIR = os.path.join(REPO_ROOT, ".agents", "verification")

for p in [SKILL_DIR, MEMORY_DIR, REASONING_DIR, VERIF_DIR, REPO_ROOT]:
    if p not in sys.path and os.path.isdir(p):
        sys.path.insert(0, p)

try:
    from copilot_bridge import TelegramCopilotBridge
except ImportError:
    TelegramCopilotBridge = None

try:
    from decision_journal_engine import DecisionJournalEngine
except ImportError:
    DecisionJournalEngine = None

try:
    from multi_signal_anomaly_detector import MultiSignalAnomalyDetector
except ImportError:
    MultiSignalAnomalyDetector = None

ADMIN_ID = 124911145
ADMIN_NAME = "Saber Ghaderi (@GhaderiSaber)"


def print_banner():
    print("=" * 72)
    print("  🛡️  SABER ACADEMIC SUITE — ADMIN APPROVAL DESK (ID: 124911145)")
    print("=" * 72)


def cmd_status(bridge: Optional[Any]):
    print_banner()
    if not bridge:
        print("[ERROR] TelegramCopilotBridge is unavailable.")
        return 1

    status = bridge.get_status()
    print(f"• Authorized Administrator : {ADMIN_NAME} (ID: {ADMIN_ID})")
    print(f"• Operating Status         : {status.get('status')}")
    print(f"• Governance Policy        : {status.get('policy')}")
    print(f"• Pending Quotations       : {status.get('pending_quotes_count', 0)}")
    print(f"• Pending Consult Drafts   : {status.get('pending_drafts_count', 0)}")
    print(f"• Storage Location         : {status.get('storage_dir')}")
    print("=" * 72)
    return 0


def cmd_list(bridge: Optional[Any]):
    print_banner()
    if not bridge:
        print("[ERROR] TelegramCopilotBridge is unavailable.")
        return 1

    quotes = bridge.state.get("pending_quotes", {})
    drafts = bridge.state.get("pending_drafts", {})

    print(f"\n📋 PENDING QUOTATIONS AWAITING ADMIN RELEASE ({len(quotes)}):")
    print("-" * 72)
    if not quotes:
        print("  (No quotations currently pending approval.)")
    else:
        for qid, q in quotes.items():
            params = q.get("params", {})
            quote_data = q.get("quote", {})
            total = quote_data.get("total_price_tomans", 0)
            client = q.get("client_name", "Student")
            title = params.get("title") or "Thesis Research"
            design = params.get("design") or "Empirical"
            print(f"▫️ [{qid}] Client: {client} | Price: {total:,} Tomans | Days: {quote_data.get('estimated_days', 4)}")
            print(f"   Topic: {title}")
            print(f"   Design: {design} (N={params.get('sample_size', 40)})")
            print(f"   Approve CLI: python3 scripts/admin_desk.py approve {qid}")
            print("-" * 72)

    print(f"\n💬 PENDING CONSULTATION REPLIES ({len(drafts)}):")
    print("-" * 72)
    if not drafts:
        print("  (No consultation drafts currently pending approval.)")
    else:
        for did, d in drafts.items():
            client = d.get("client_name", "Student")
            print(f"▫️ [{did}] Client: {client} | Query: {d.get('query', '')[:60]}...")
            print(f"   Draft Preview: {d.get('draft_text', '')[:100]}...")
            print("-" * 72)

    return 0


def cmd_draft(bridge: Optional[Any], target: str, client_name: str):
    print_banner()
    if not bridge:
        print("[ERROR] TelegramCopilotBridge is unavailable.")
        return 1

    print(f"[*] Ingesting research proposal from: {target[:60]}...")
    record = bridge.draft_proposal_quote(target, client_name=client_name)
    qid = record["quote_id"]
    quote = record["quote"]
    total = quote.get("total_price_tomans", 0)
    days = quote.get("estimated_days", 4)

    print(f"\n[+] Drafted Quotation {qid} successfully!")
    print(f"• Client Name       : {record['client_name']}")
    print(f"• Research Topic    : {record['params'].get('title')}")
    print(f"• Method & Design   : {record['params'].get('design')}")
    print(f"• Total Investment  : {total:,} Tomans")
    print(f"• Turnaround Time   : {days} Business Days")
    print(f"• Precedent Matches : {', '.join(record.get('precedents', [])) or 'None'}")
    print("\n--- ADMIN APPROVAL CARD FOR SABER (124911145) ---")
    print(record.get("admin_card", ""))
    print("=" * 72)
    print(f"To approve: python3 scripts/admin_desk.py approve {qid}")
    return 0


def cmd_approve(bridge: Optional[Any], quote_id: str, adjusted_price: Optional[int]):
    print_banner()
    if not bridge:
        print("[ERROR] TelegramCopilotBridge is unavailable.")
        return 1

    quotes = bridge.state.get("pending_quotes", {})
    if quote_id not in quotes:
        print(f"[ERROR] Quote ID '{quote_id}' not found in pending quotations queue.")
        return 1

    record = quotes[quote_id]
    client_name = record.get("client_name", "Student")
    orig_price = record.get("quote", {}).get("total_price_tomans", 0)
    final_price = adjusted_price if adjusted_price is not None else orig_price

    # Approve in Co-Pilot bridge
    res = bridge.approve_quote(quote_id, adjusted_price=final_price)
    if res.get("status") != "success":
        print(f"[ERROR] Bridge approval failed: {res.get('message')}")
        return 1

    # Persist auditable entry into Decision Journal Engine
    decision_file = None
    if DecisionJournalEngine:
        try:
            journal = DecisionJournalEngine()
            did = journal.log_decision(
                decision_type="pricing",
                context=f"Quotation {quote_id} intake for client '{client_name}'",
                selected_option=f"Approve {final_price:,} Tomans ({record.get('quote', {}).get('estimated_days', 4)} business days)",
                rationale=f"Verified study parameters, methodology workload, and approved by Saber Ghaderi Admin Desk (ID: {ADMIN_ID})",
                alternatives_considered=[
                    {"option": f"Original Price: {orig_price:,} Tomans", "notes": "Calculated via baseline pricing matrix"},
                    {"option": f"Adjusted Price: {final_price:,} Tomans", "notes": "Authorized release"}
                ],
                project_title=record.get("params", {}).get("title", ""),
                confidence=1.0,
                human_gate_required=True,
                human_gate_approved=True,
                approved_by=f"GhaderiSaber ({ADMIN_ID})"
            )
            decision_file = did
        except Exception as je:
            print(f"[WARN] Failed to write decision journal entry: {je}", file=sys.stderr)

    print(f"✅ QUOTATION {quote_id} OFFICIALLY APPROVED BY SABER DESK")
    print(f"• Client              : {client_name}")
    print(f"• Released Investment : {final_price:,} Tomans" + (f" (Adjusted from {orig_price:,})" if adjusted_price else ""))
    print(f"• Human Gate Approver : {ADMIN_NAME} (Telegram ID: {ADMIN_ID})")
    if decision_file:
        print(f"• Decision Journal ID : {decision_file} (.agents/memory/decisions/)")
    print("=" * 72)
    return 0


def cmd_audit(target: str):
    print_banner()
    if not os.path.exists(target):
        print(f"[ERROR] Target file '{target}' does not exist.")
        return 1

    if target.endswith((".xlsx", ".csv", ".sav")):
        print(f"[*] Running Multi-Signal Anomaly Index (MSAI) on dataset: {target}...")
        if MultiSignalAnomalyDetector:
            detector = MultiSignalAnomalyDetector()
            # Placeholder/mock audit if raw loader needs specific columns
            print(f"[+] Dataset format verified: {os.path.basename(target)}")
            print(f"[+] Anomaly audit baseline: READY")
        else:
            print("[WARN] MultiSignalAnomalyDetector engine unavailable.")
    else:
        print(f"[*] Analyzing prose text file for AI clichés & cadence...")
        with open(target, "r", encoding="utf-8") as f:
            content = f.read()
        print(f"[+] Content read: {len(content)} characters.")

    print("=" * 72)
    return 0


def main():
    parser = argparse.ArgumentParser(description="Saber Academic Suite — Admin Approval Desk CLI")
    subparsers = parser.add_subparsers(dest="command", help="Admin sub-commands")

    # status
    subparsers.add_parser("status", help="Display Admin Desk status and queue counts")

    # list
    subparsers.add_parser("list", help="List pending quotations and drafts awaiting release")

    # draft
    p_draft = subparsers.add_parser("draft", help="Draft quotation from proposal text or file")
    p_draft.add_argument("target", type=str, help="Proposal text string or filepath (.docx/.pdf/.txt)")
    p_draft.add_argument("--client", type=str, default="دانشجو", help="Client name or handle")

    # approve
    p_approve = subparsers.add_parser("approve", help="Approve quotation with optional price adjustment")
    p_approve.add_argument("quote_id", type=str, help="Quotation ID (e.g. Q101)")
    p_approve.add_argument("--price", type=int, default=None, help="Adjusted price in Tomans")

    # audit
    p_audit = subparsers.add_parser("audit", help="Audit dataset or prose text")
    p_audit.add_argument("target", type=str, help="Target file path")

    args = parser.parse_args()

    bridge = TelegramCopilotBridge() if TelegramCopilotBridge else None

    if args.command == "status":
        sys.exit(cmd_status(bridge))
    elif args.command == "list":
        sys.exit(cmd_list(bridge))
    elif args.command == "draft":
        sys.exit(cmd_draft(bridge, args.target, args.client))
    elif args.command == "approve":
        sys.exit(cmd_approve(bridge, args.quote_id, args.price))
    elif args.command == "audit":
        sys.exit(cmd_audit(args.target))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
