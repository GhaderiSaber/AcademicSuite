"""
voice_transcriber.py — Persian Voice Note Auto-Transcription & Executive Audio Digesting Engine

Processes incoming student voice notes (.oga, .ogg, .mp3, .wav) with Persian acoustic precision
using Gemini's multimodal audio API with resilient multi-model cascading (3.8 -> 3.7 -> 3.6 -> 2.5).
Distills long rambling audio into a crisp 3-bullet Persian executive digest:
1. 🎯 چالش اصلی پژوهشگر (The Core Research Dilemma)
2. 📌 خواسته مشخص از مشاور (Actionable Request)
3. 🔬 متغیرها و آزمون‌های ذکرشده (Mentioned Variables, Scales & Statistical Tests)
"""

import os
import re
import json
import base64
import html
import subprocess
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

AUDIO_MODELS_CASCADE = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
    "gemini-2.5-flash"
]


class AcademicVoiceTranscriber:
    """Multimodal audio transcriber and executive digest synthesizer for Iranian graduate voice notes."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get("gemini_api_key")
        self.proxy_addr = "127.0.0.1"
        self.proxy_port = 3066
        if config.get("proxy"):
            self.proxy_addr = config["proxy"].get("addr", "127.0.0.1")
            self.proxy_port = int(config["proxy"].get("port", 3066))

    def transcribe_and_digest(
        self,
        audio_path: str,
        client_name: str = "پژوهشگر",
        is_vip: bool = False,
        duration: int = 0
    ) -> Optional[Dict[str, Any]]:
        """
        Transcribes Persian voice note from disk, summarizes research intent,
        and generates an authoritative response draft using Gemini audio multimodal API.
        """
        if not self.api_key or not os.path.exists(audio_path):
            return None

        # Determine MIME type
        ext = os.path.splitext(audio_path)[1].lower()
        mime_type = "audio/ogg"
        if ext in [".oga", ".ogg"]:
            mime_type = "audio/ogg"
        elif ext == ".mp3":
            mime_type = "audio/mp3"
        elif ext == ".wav":
            mime_type = "audio/wav"
        elif ext == ".m4a":
            mime_type = "audio/m4a"

        try:
            with open(audio_path, "rb") as af:
                audio_b64 = base64.b64encode(af.read()).decode("utf-8")
        except Exception as e:
            print(f"[-] Error reading audio file {audio_path}: {e}")
            return None

        first_name = client_name.split()[0] if client_name else "پژوهشگر"

        system_prompt = f"""
You are the AI Research Twin of Saber Ghaderi (@GhaderiSaber), an elite statistical consultant and psychometrician in Iran.
Your task is to listen to this Persian voice message from a student/researcher ({client_name}, first name: {first_name}),
transcribe their exact spoken words into authentic Persian with proper punctuation and نیم‌فاصله,
extract their core research dilemma and actionable request, and synthesize a master-class, polite, authoritative response draft in Persian.

### CLIENT CONTEXT:
- Client Name: {client_name}
- VIP Status: {is_vip}
- Approximate Duration: {duration} seconds

### ANALYSIS REQUIREMENTS:
1. `transcript_fa`: Exact, complete transcription of everything said in Persian. Use correct Persian punctuation, half-spaces (نیم‌فاصله), and technical terminology (e.g. آزمون سوبل, آنکووا, پایایی, آلفای کرونباخ, بارون و کنی, برازش مدل).
2. `core_dilemma_fa`: 1 clear, professional sentence summarizing the student's problem, confusion, or supervisor's comment.
3. `actionable_request_fa`: 1 concise sentence summarizing what the client explicitly or implicitly wants Saber to do.
4. `variables_and_tools_fa`: Exact statistical tests, psychological scales, variables, or software mentioned (or 'ذکر نشده' if none).
5. `inquiry_type`: One of:
   - `supervisor_defense_question` (if asking how to defend or justify to supervisor/examiner)
   - `supervisor_revision_feedback` (if reporting supervisor correction requests)
   - `statistical_consulting` (if asking about stats tests, models, or data)
   - `scale_inquiry` (if asking about questionnaires or psychometrics)
   - `progress_and_reports` (if asking about university portal or reports)
   - `client_burst_inquiry` (general academic inquiry)
6. `topic_key`: `supervisor_reviews` if related to supervisor comments/defense; `drafts` for general consulting; `scales` for questionnaires.
7. `thinking_points_en`: Exactly 3 bullet points:
   - "Methodology: <assessment of research design or issue>"
   - "Epistemic Rule: <statistical/academic rule to apply>"
   - "Consulting Strategy: <how Saber should address the dilemma>"
8. `suggested_draft_fa`: The exact, polished Persian message for Saber to send to the student with 1-click. Reassuring, authoritative, eliminating AI cliches.

### STRICT JSON OUTPUT SCHEMA:
{{
  "transcript_fa": "<exact Persian transcription>",
  "core_dilemma_fa": "<main problem in Persian>",
  "actionable_request_fa": "<actionable request in Persian>",
  "variables_and_tools_fa": "<variables or tests in Persian>",
  "inquiry_type": "<one of the categories above>",
  "topic_key": "<drafts | supervisor_reviews | scales>",
  "thinking_points_en": [
    "Methodology: ...",
    "Epistemic Rule: ...",
    "Consulting Strategy: ..."
  ],
  "suggested_draft_fa": "<polished Persian response>"
}}
"""

        payload = json.dumps({
            "contents": [
                {
                    "parts": [
                        {"text": system_prompt},
                        {
                            "inlineData": {
                                "mimeType": mime_type,
                                "data": audio_b64
                            }
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 4096,
                "responseMimeType": "application/json"
            }
        })

        for model in AUDIO_MODELS_CASCADE:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            cmd = [
                "curl", "-s", "-k",
                "-x", f"socks5h://{self.proxy_addr}:{self.proxy_port}",
                "-H", "Content-Type: application/json",
                "-d", payload,
                url
            ]

            try:
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=90)
                if res.returncode == 0 and res.stdout:
                    data = json.loads(res.stdout)
                    candidates = data.get("candidates", [])
                    if candidates:
                        raw_text = candidates[0].get("content", {}).get("parts", [])[0].get("text", "")
                        match = re.search(r"\{.*\}", raw_text, re.DOTALL)
                        json_str = match.group(0) if match else raw_text.strip()
                        parsed = json.loads(json_str)
                        parsed["audio_file"] = os.path.basename(audio_path)
                        parsed["audio_path"] = audio_path
                        parsed["audio_model"] = model
                        parsed["duration"] = duration
                        print(f"[+] Audio successfully transcribed via {model} ({os.path.basename(audio_path)})")
                        return parsed
                    elif "error" in data:
                        err_msg = data.get("error", {}).get("message", "")
                        print(f"[!] {model} audio error: {err_msg}. Cascading to next model...")
            except Exception as e:
                print(f"[-] Gemini API audio call error with {model}: {e}")

        print("[-] All Gemini multimodal audio models failed for this voice note.")
        return None

    @staticmethod
    def build_voice_card(
        voice_digest: Dict[str, Any],
        client_name: str,
        client_link: str,
        sender_id: int,
        draft_id: str = "D101",
        account_label: str = "Main Account (@GhaderiSaber)"
    ) -> Tuple[str, List[List[Dict[str, str]]]]:
        """
        Builds a 2026 Box-drawing Voice Note Executive Digest Card with:
        - Box-drawing header frame and duration badge.
        - 3-point Persian executive digest.
        - Collapsible full transcript in <blockquote expandable>.
        - Collapsible Epistemic Reasoning block in <blockquote expandable>.
        - Suggested scholar response draft.
        - 2026 Action Keyboard.
        """
        duration = voice_digest.get("duration", 0)
        dur_str = f"{duration} ثانیه" if duration > 0 else "پیام صوتی"
        fname = voice_digest.get("audio_file", "voice_note.oga")
        model = voice_digest.get("audio_model", "Gemini Audio")

        dilemma = voice_digest.get("core_dilemma_fa", "بررسی محتوای پیام صوتی پژوهشگر")
        request = voice_digest.get("actionable_request_fa", "پاسخ تخصصی و راهنمایی روش‌شناختی")
        tools = voice_digest.get("variables_and_tools_fa", "ذکر نشده")
        transcript = voice_digest.get("transcript_fa", "")
        draft_reply = voice_digest.get("suggested_draft_fa", "")
        thinking_points = voice_digest.get("thinking_points_en", [])

        header_lines = [
            "╭─ <b>🎙️ VOICE NOTE EXECUTIVE DIGEST</b> ─────────────",
            f"│ 👤 <b>Client:</b> {client_link}  •  <code>#{sender_id}</code>",
            f"│ ⏱️ <b>Audio:</b> <code>{html.escape(fname)}</code> ({dur_str})",
            f"│ 📱 <b>Routing:</b> <code>{html.escape(account_label)}</code>",
            f"│ ⚡ <b>AI Engine:</b> <code>{html.escape(model)}</code>",
            f"│ 🆔 <b>Draft ID:</b> <code>{draft_id}</code>",
            "╰──────────────────────────────────────────────────"
        ]

        body = [
            "\n".join(header_lines),
            "\n📊 <b>خلاصه تحلیلی پیام صوتی مراجع (3-Point Digest):</b>",
            f"🎯 <b>چالش اصلی پژوهشگر:</b> {html.escape(dilemma)}",
            f"📌 <b>خواسته مشخص از مشاور:</b> {html.escape(request)}",
            f"🔬 <b>متغیرها و ابزارهای ذکرشده:</b> <code>{html.escape(tools)}</code>",
            f"\n📜 <b>متن کامل پیاده‌سازی‌شده صوت (Persian Audio Transcript):</b>\n"
            f"<blockquote expandable>«{html.escape(transcript)}»</blockquote>"
        ]

        if thinking_points:
            t_bullets = []
            for pt in thinking_points:
                clean_pt = pt.strip().lstrip("•-").strip()
                if ":" in clean_pt:
                    k, v = clean_pt.split(":", 1)
                    t_bullets.append(f"• <b>{html.escape(k.strip())}:</b> {html.escape(v.strip())}")
                else:
                    t_bullets.append(f"• {html.escape(clean_pt)}")
            body.append(
                f"\n🧠 <b>AI EPISTEMIC REASONING PROCESS</b>\n"
                f"<blockquote expandable>{chr(10).join(t_bullets)}</blockquote>"
            )

        body.append(
            f"\n📝 <b>SUGGESTED SCHOLAR RESPONSE DRAFT</b>\n"
            f"<blockquote expandable>{html.escape(draft_reply)}</blockquote>"
        )

        body.append(
            f"\n<i>Tap button below to dispatch, or tap to copy command:</i> <code>/send_msg_{draft_id}</code>"
        )

        alert_text = "\n".join(body)

        buttons = [
            [
                {"text": f"🚀 Approve & Send ({draft_id})", "callback_data": f"send_draft_{draft_id}"}
            ],
            [
                {"text": "📝 Full Transcript", "callback_data": f"voice_transcript_{draft_id}"},
                {"text": "✏️ Edit & Reply", "query": f"/send_msg_{draft_id} "}
            ],
            [
                {"text": "🗑️ Dismiss", "callback_data": f"ignore_draft_{draft_id}"}
            ]
        ]

        return alert_text, buttons
