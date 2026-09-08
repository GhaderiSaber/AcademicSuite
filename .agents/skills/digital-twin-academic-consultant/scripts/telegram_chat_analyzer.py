#!/usr/bin/env python3
"""
Telegram Chat History Analyzer & Persona Calibrator (telegram_chat_analyzer.py)
-------------------------------------------------------------------------------
Part of the Digital Twin Academic Consultant skill for AcademicSuite.
Analyzes Telegram Desktop chat exports (JSON or HTML) and conversation transcripts:
1. Distinguishes client requests from Saber's responses (Telegram ID: 124911145).
2. Categorizes discussions into:
   - Pricing & Invoicing (استعلام قیمت)
   - Questionnaires & Measurement Tools (درخواست پرسشنامه)
   - Proposals & Study Design (پروپوزال و متدولوژی)
   - Statistical Analysis & Chapter 4 (تحلیل آماری و SPSS/AMOS)
   - Examiner Feedback & Chapter 5/Defense (اصلاحات، بحث و دفاع)
3. Extracts real Q&A pairs (FAQs) to calibrate the Digital Twin persona.
4. Identifies files exchanged (.docx, .pdf, .sav, .xlsx) and project scopes.
5. Exports calibrated_knowledge.json and Markdown executive summaries.
"""

import os
import re
import sys
import json
import argparse
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime

DEFAULT_SABER_ID = 124911145
DEFAULT_PERSONA_PATH = os.path.join(
    os.path.dirname(__file__), "..", "references", "saber_persona.json"
)


def extract_plain_text(text_field: Any) -> str:
    """Normalize Telegram message text which can be a str or list of entity dicts/strings."""
    if isinstance(text_field, str):
        return text_field
    elif isinstance(text_field, list):
        parts = []
        for part in text_field:
            if isinstance(part, str):
                parts.append(part)
            elif isinstance(part, dict) and "text" in part:
                parts.append(part["text"])
        return "".join(parts)
    return ""


def parse_telegram_json_export(file_path: str) -> List[Dict[str, Any]]:
    """Parse messages array from Telegram Desktop result.json."""
    with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
        data = json.load(f)

    messages = []
    if "messages" in data and isinstance(data["messages"], list):
        messages = data["messages"]
    elif isinstance(data, list):
        messages = data
    return messages


def classify_message_intent(text: str) -> str:
    """Categorize academic consulting intent based on keywords."""
    clean = text.lower()
    
    # 1. Pricing / Invoicing
    if any(k in clean for k in ["هزینه", "قیمت", "چقدر میشه", "تعرفه", "فاکتور", "پیش‌فاکتور", "مبلغ", "تومان", "واریز", "شماره کارت", "شماره شبا"]):
        return "pricing_inquiry"
    
    # 2. Questionnaire / Scale lookup
    if any(k in clean for k in ["پرسشنامه", "مقیاس", "نمره‌گذاری", "روایی", "پایایی", "کلید", "آزمون", "خرده‌مقیاس", "گویه"]):
        return "questionnaire_request"
    
    # 3. Proposal / Methodology
    if any(k in clean for k in ["پروپوزال", "طرح تحقیق", "روش تحقیق", "حجم نمونه", "g*power", "متغیر مستقل", "متغیر وابسته", "میانجی"]):
        return "proposal_methodology"
    
    # 4. Statistical analysis / Chapter 4
    if any(k in clean for k in ["تحلیل آماری", "فصل ۴", "فصل چهار", "spss", "amos", "smartpls", "pls", "رگرسیون", "معادلات ساختاری", "کوواریانس", "تحلیل عاملی"]):
        return "statistical_analysis"
    
    # 5. Examiner comments / Thesis revision / Defense
    if any(k in clean for k in ["اصلاحات", "کامنت", "استاد راهنما", "داور", "جلسه دفاع", "پاورپوینت", "اسلاید", "ایران‌داک", "همانندجویی"]):
        return "revision_and_defense"
    
    return "general_academic_inquiry"


def analyze_chat_history(
    messages: List[Dict[str, Any]],
    saber_id: int = DEFAULT_SABER_ID
) -> Dict[str, Any]:
    """Extract Q&A pairs, pricing discussions, questionnaires requested, and files."""
    qa_pairs = []
    pricing_discussions = []
    questionnaire_requests = []
    files_received = []
    
    client_counts = 0
    saber_counts = 0
    intent_stats = {
        "pricing_inquiry": 0,
        "questionnaire_request": 0,
        "proposal_methodology": 0,
        "statistical_analysis": 0,
        "revision_and_defense": 0,
        "general_academic_inquiry": 0
    }

    # Group messages into conversational threads
    # Simple heuristic: sequence of client messages followed by Saber's reply
    pending_client_msgs = []

    for msg in messages:
        if msg.get("type") != "message":
            continue

        text = extract_plain_text(msg.get("text", "")).strip()
        from_id_str = str(msg.get("from_id", ""))
        from_name = str(msg.get("from", ""))

        # Check if message is from Saber
        is_saber = (
            str(saber_id) in from_id_str or
            "saber" in from_name.lower() or
            "صابر" in from_name or
            "ghaderi" in from_name.lower()
        )

        # Check if file attached
        file_name = msg.get("file_name") or msg.get("file")
        if file_name:
            files_received.append({
                "date": msg.get("date"),
                "file_name": file_name,
                "sender": "Saber" if is_saber else "Client",
                "media_type": msg.get("media_type", "document")
            })

        if not text:
            continue

        if not is_saber:
            client_counts += 1
            intent = classify_message_intent(text)
            intent_stats[intent] = intent_stats.get(intent, 0) + 1
            pending_client_msgs.append({
                "date": msg.get("date"),
                "sender": from_name or "Client",
                "text": text,
                "intent": intent
            })
        else:
            saber_counts += 1
            # If we had pending client messages, pair the last one with Saber's answer
            if pending_client_msgs:
                last_q = pending_client_msgs[-1]
                qa_pairs.append({
                    "date": msg.get("date"),
                    "client_question": last_q["text"],
                    "intent": last_q["intent"],
                    "saber_reply": text
                })
                if last_q["intent"] == "pricing_inquiry":
                    pricing_discussions.append({
                        "date": msg.get("date"),
                        "client": last_q["text"],
                        "saber_quote": text
                    })
                elif last_q["intent"] == "questionnaire_request":
                    questionnaire_requests.append({
                        "date": msg.get("date"),
                        "request": last_q["text"],
                        "saber_reply": text
                    })
                pending_client_msgs = []

    # Extract common patterns in Saber's greetings and sign-offs
    greetings_found = set()
    for pair in qa_pairs:
        reply = pair["saber_reply"]
        first_line = reply.splitlines()[0].strip() if reply.splitlines() else ""
        if any(g in first_line.lower() for g in ["سلام", "درود", "وقت بخیر", "وقتتون بخیر"]):
            greetings_found.add(first_line)

    return {
        "summary": {
            "total_messages": len(messages),
            "client_messages_count": client_counts,
            "saber_messages_count": saber_counts,
            "qa_threads_extracted": len(qa_pairs),
            "pricing_quotes_detected": len(pricing_discussions),
            "questionnaire_requests_detected": len(questionnaire_requests),
            "files_exchanged_count": len(files_received)
        },
        "intent_distribution": intent_stats,
        "frequent_greetings": sorted(list(greetings_found))[:5],
        "qa_knowledge_base": qa_pairs,
        "pricing_samples": pricing_discussions,
        "questionnaire_samples": questionnaire_requests,
        "files_exchanged": files_received[:50]
    }


def format_markdown_analysis(analysis: Dict[str, Any]) -> str:
    """Format chat analysis as a clean Persian Markdown report."""
    summ = analysis["summary"]
    dist = analysis["intent_distribution"]

    lines = []
    lines.append("# گزارش تحلیل تاریخچه تعاملات تلگرام (کالیبراسیون همزاد دیجیتال صابر)")
    lines.append(f"**تاریخ تحلیل:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append("## ۱. آمار کلی گفتگوها")
    lines.append(f"- **کل پیام‌های پردازش‌شده:** {summ['total_messages']}")
    lines.append(f"- **پیام‌های ارسالی مراجعان/دانشجویان:** {summ['client_messages_count']}")
    lines.append(f"- **پاسخ‌های تخصصی صابر:** {summ['saber_messages_count']}")
    lines.append(f"- **جفت‌های پرسش و پاسخ استخراج‌شده (Q&A):** {summ['qa_threads_extracted']}")
    lines.append(f"- **استعلام‌های قیمت و صدور پیش‌فاکتور:** {summ['pricing_quotes_detected']}")
    lines.append(f"- **درخواست‌های ابزار و پرسشنامه:** {summ['questionnaire_requests_detected']}")
    lines.append(f"- **فایل‌های پژوهشی مبادله‌شده:** {summ['files_exchanged_count']}")
    lines.append("")
    lines.append("## ۲. توزیع موضوعی درخواست‌های مراجعان")
    lines.append("| ردیف | دسته‌بندی موضوعی | تعداد پیام‌ها | درصد |")
    lines.append("| :---: | :--- | :---: | :---: |")
    total_intent = sum(dist.values()) or 1
    intent_fa_map = {
        "pricing_inquiry": "استعلام قیمت، هزینه و زمان‌بندی",
        "questionnaire_request": "درخواست پرسشنامه، کلید و روایی/پایایی",
        "proposal_methodology": "بررسی پروپوزال، روش‌شناسی و G*Power",
        "statistical_analysis": "تحلیل آماری، فصل چهارم (SPSS/SEM)",
        "revision_and_defense": "اعمال اصلاحات داوران، فصل پنجم و دفاع",
        "general_academic_inquiry": "پرسش‌های عمومی تحصیلی و دانشگاهی"
    }
    for idx, (k, count) in enumerate(dist.items(), 1):
        pct = (count / total_intent) * 100
        lines.append(f"| {idx} | {intent_fa_map.get(k, k)} | {count} | {pct:.1f}% |")

    if analysis.get("frequent_greetings"):
        lines.append("")
        lines.append("## ۳. الگوهای کلامی پرتکرار صابر")
        for g in analysis["frequent_greetings"]:
            lines.append(f"- «{g}»")

    if analysis.get("qa_knowledge_base"):
        lines.append("")
        lines.append("## ۴. نمونه جفت‌های پرسش و پاسخ استخراج‌شده (FAQs)")
        for idx, qa in enumerate(analysis["qa_knowledge_base"][:10], 1):
            lines.append(f"### {idx}. موضوع: {intent_fa_map.get(qa['intent'], qa['intent'])}")
            lines.append(f"**پرسش مراجع:** {qa['client_question']}")
            lines.append(f"**پاسخ صابر:** {qa['saber_reply']}")
            lines.append("")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Telegram Chat History Analyzer for Digital Saber")
    parser.add_argument("--input", "-i", type=str, required=True, help="Path to Telegram export JSON file (result.json)")
    parser.add_argument("--saber-id", type=int, default=DEFAULT_SABER_ID, help="Saber's Telegram User ID (default: 124911145)")
    parser.add_argument("--output-dir", "-o", type=str, default=".", help="Output directory for knowledge base")
    parser.add_argument("--update-persona", action="store_true", help="Merge extracted FAQs into saber_persona.json")

    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"[-] File not found: {args.input}")
        sys.exit(1)

    messages = parse_telegram_json_export(args.input)
    analysis = analyze_chat_history(messages, saber_id=args.saber_id)

    os.makedirs(args.output_dir, exist_ok=True)

    # Save JSON knowledge base
    json_path = os.path.join(args.output_dir, "calibrated_knowledge.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    # Save Markdown report
    md_report = format_markdown_analysis(analysis)
    md_path = os.path.join(args.output_dir, "chat_analysis_summary.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_report)

    # Optionally update persona
    if args.update_persona and os.path.exists(DEFAULT_PERSONA_PATH):
        try:
            with open(DEFAULT_PERSONA_PATH, "r", encoding="utf-8") as pf:
                persona = json.load(pf)
            persona["calibrated_faqs"] = analysis["qa_knowledge_base"][:30]
            with open(DEFAULT_PERSONA_PATH, "w", encoding="utf-8") as pf:
                json.dump(persona, pf, ensure_ascii=False, indent=2)
            print(f"[+] Successfully merged calibrated FAQs into {DEFAULT_PERSONA_PATH}")
        except Exception as e:
            print(f"[-] Error updating persona: {e}")

    print(f"[+] Chat history analyzed successfully.")
    print(f"    Messages: {analysis['summary']['total_messages']}")
    print(f"    Q&A pairs extracted: {analysis['summary']['qa_threads_extracted']}")
    print(f"    Pricing inquiries: {analysis['summary']['pricing_quotes_detected']}")
    print(f"    Files exchanged: {analysis['summary']['files_exchanged_count']}")
    print(f"    Outputs generated at: {args.output_dir}")


if __name__ == "__main__":
    main()
