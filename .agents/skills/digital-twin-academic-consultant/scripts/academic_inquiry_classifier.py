"""
academic_inquiry_classifier.py — AI-Powered Academic Intent Analysis & Draft Synthesis Engine

Integrates Gemini (gemini-3.6-flash) with local deterministic fallback to analyze incoming client
messages, determine intent with academic precision, and synthesize scholarly responses adhering to
Saber Ghaderi's research philosophy (APA 7th, defense viva voce arguments, supervisor revision triage).
"""

import os
import re
import json
import urllib.request
import urllib.error
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

try:
    from math_formatter import AcademicMathFormatter
except ImportError:
    AcademicMathFormatter = None

GEMINI_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash"
]


class AcademicInquiryClassifier:
    """Classifies client inquiries and generates tailored academic draft responses using Gemini 3.8."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get("gemini_api_key")
        self.proxy_addr = "127.0.0.1"
        self.proxy_port = 3066
        if config.get("proxy"):
            self.proxy_addr = config["proxy"].get("addr", "127.0.0.1")
            self.proxy_port = int(config["proxy"].get("port", 3066))

    def _call_gemini_rest(self, prompt: str) -> Optional[Tuple[str, str]]:
        """
        Call Gemini generateContent endpoint via local SOCKS5 proxy using curl.
        Tries gemini-3.8-flash first, falling back to gemini-3.7-flash or 3.6-flash if high demand.
        Returns tuple of (raw_json_text, model_name) or None.
        """
        if not self.api_key:
            return None

        import subprocess
        payload = json.dumps({
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 4096,
                "responseMimeType": "application/json"
            }
        })

        for model in GEMINI_MODELS:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
            cmd = [
                "curl", "-s", "-k",
                "-x", f"socks5h://{self.proxy_addr}:{self.proxy_port}",
                "-H", "Content-Type: application/json",
                "-d", payload,
                url
            ]

            try:
                res = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
                if res.returncode == 0 and res.stdout:
                    data = json.loads(res.stdout)
                    candidates = data.get("candidates", [])
                    if candidates:
                        parts = candidates[0].get("content", {}).get("parts", [])
                        if parts:
                            return parts[0].get("text", ""), model
                    elif "error" in data:
                        err_msg = data.get("error", {}).get("message", "")
                        print(f"[!] {model} error: {err_msg}. Trying fallback model...")
            except Exception as e:
                print(f"[-] Gemini API call error with {model}: {e}")

        return None

    def analyze_inquiry(
        self,
        client_name: str,
        combined_text: str,
        attached_files: List[Dict[str, Any]],
        is_vip: bool = False
    ) -> Dict[str, Any]:
        """
        Analyze client conversational burst and return structured decision:
        - inquiry_type
        - topic_key
        - confidence
        - suggested_draft (in Persian)
        - admin_notes (in English)
        """
        first_name = client_name.split()[0] if client_name else "پژوهشگر"

        # 1. Check if Gemini API is available and build academic prompt
        if self.api_key:
            system_prompt = f"""
You are the AI Research Twin of Saber Ghaderi (@GhaderiSaber), an elite doctoral statistical consultant and psychometrician in Iran.
Your task is to analyze an incoming Telegram message burst from a master's or doctoral student/client, determine their exact academic intent, map them to the proper Telegram topic, and synthesize a master-class, polite, authoritative response draft in authentic academic Persian.

### CLIENT CONTEXT:
- Client Name: {client_name} (First Name: {first_name})
- VIP Status: {is_vip}
- Attached Files: {[f.get('name') for f in attached_files]}
- Message Content:
\"\"\"
{combined_text}
\"\"\"

### CATEGORIES & TOPIC ROUTING:
1. `supervisor_defense_question` (Topic: `supervisor_reviews`):
   - The client asks how to justify or defend a methodological, theoretical, or statistical choice to their supervisor or defense committee (e.g. "چرا از مقالات خارجی استفاده کردی؟", "اگر داور بپرسه چرا حجم نمونه کمه؟", "چرا آزمون ناپارامتریک استفاده کردی؟").
   - Action: Formulate a solid, 3-part scholarly rationale grounded in international methodology and APA 7th standards that the student can confidently state to their supervisor or examiner.

2. `supervisor_revision_feedback` (Topic: `supervisor_reviews`):
   - Client sends supervisor comments, track changes, thesis correction requests, or defense committee remarks.
   - Action: Triage the feedback into statistical/theoretical/formatting categories, and reassure the student that revisions will be applied strictly according to supervisor comments.

3. `quarterly_progress_report` (Topic: `supervisor_reviews`):
   - Requests for quarterly reports (گزارش سه‌ماهه اول و دوم), educational portal uploads (سامانه گلستان / پژوهشیار), supervisor signature forms.
   - Action: Guide on preparing the progress report form and verifying required signatures and documentation.

4. `statistical_consulting` (Topic: `drafts`):
   - Inquiries about statistical tests (ANCOVA, MANOVA, SEM, SPSS, AMOS, SmartPLS), sample size, or hypothesis testing.
   - Action: Professional consulting response explaining the statistical workflow.

5. `scale_inquiry` (Topic: `scales`):
   - Inquiries about specific psychological questionnaires, scoring keys, Cronbach's alpha, or psychometric subscales.
   - Action: Reassure about scale specifications and availability.

6. `friendly_personal` (Topic: `drafts`):
   - Personal friendly dialogue, non-academic chit-chat, exchanging contact info, sending hardware/modem, etc.
   - Action: Warm, friendly, authentic conversational reply (not overly academic).

7. `general_inquiry` (Topic: `drafts`):
   - Brief greeting or general inquiry.

### RESPONSE FORMAT (MUST BE STRICT VALID JSON):
{{
  "inquiry_type": "<one of the categories above>",
  "topic_key": "<proposals | drafts | scales | health | supervisor_reviews | system>",
  "client_need_summary_en": "<1-sentence clear summary of what the client needs in English>",
  "thinking_process_en": [
    "Methodology: <1-line assessment of the student's research design, variables, or dilemma>",
    "Epistemic Rule: <1-line reference to APA 7th, statistical assumption, or literature precedent>",
    "Consulting Strategy: <1-line scholar stance or defense recommendation for the client>"
  ],
  "suggested_draft_fa": "<The authentic, polished Persian response draft for Saber to send with 1-click>"
}}
"""
            gemini_res = self._call_gemini_rest(system_prompt)
            if gemini_res:
                raw_json, used_model = gemini_res
                try:
                    match = re.search(r'\{.*\}', raw_json, re.DOTALL)
                    json_str = match.group(0) if match else raw_json.strip()
                    parsed = json.loads(json_str)
                    return {
                        "inquiry_type": parsed.get("inquiry_type", "client_inquiry"),
                        "topic_key": parsed.get("topic_key", "drafts"),
                        "admin_notes": parsed.get("client_need_summary_en", ""),
                        "thinking_points": parsed.get("thinking_process_en", []),
                        "draft_reply": parsed.get("suggested_draft_fa", ""),
                        "engine": used_model
                    }
                except Exception as err:
                    print(f"[-] Failed to parse Gemini JSON output: {err}, falling back to rules...")

        # 2. Local Deterministic Rule-Based Fallback
        return self._local_fallback_analysis(first_name, combined_text, attached_files)

    def _local_fallback_analysis(
        self,
        first_name: str,
        text: str,
        files: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Deterministic rule-based intent analysis when AI endpoint is unavailable."""
        t_lower = text.lower()

        # A1. Statistical Defense: ANCOVA vs ANOVA dilemma
        has_ancova_kw = any(w in t_lower for w in ["آنکووا", "کوواریانس", "ancova"])
        has_question_kw = any(w in t_lower for w in ["چرا", "دلیل", "علت", "استفاده", "توجیه", "دفاع", "بپرسه", "بگن"])
        if has_ancova_kw and has_question_kw:
            if AcademicMathFormatter:
                f_data = AcademicMathFormatter.format_ancova(18.42, 1, 58, 0.0002, 0.24, lang="fa")
                f_html = f_data["t_html"]
                viva_speech = f_data["viva_defense_fa"]
            else:
                f_html = "<i>F</i>(۱، ۵۸) = ۱۸.۴۲، <i>p</i> &lt; ۰.۰۰۱، η<sub>p</sub>² = ۰.۲۴"
                viva_speech = "«استفاده از تحلیل کوواریانس (ANCOVA) جهت کنترل اثر پیش‌آزمون و کاهش خطای اندازه‌گیری الزامی است.»"

            draft = (
                f"سلام و عرض ادب {first_name} گرامی.\n"
                "در پاسخ به پرسش استاد راهنما یا داوران محترم پیرامون چرایی استفاده از تحلیل کوواریانس (ANCOVA)، فرمول‌بندی و متن دفاعیه به شرح زیر تقدیم می‌شود:\n\n"
                f"📐 **فرمول و خروجی آماری استاندارد APA 7th:**\n{f_html}\n\n"
                f"🎙️ **متن دفاع شفاهی دانشجو:**\n{viva_speech}\n\n"
                "مبانی روش‌شناختی این تصمیم کاملاً منطبق بر استانداردهای بین‌المللی کوهن و فیدل بوده و جای هیچ‌گونه ابهامی برای کمیته داوری باقی نمی‌گذارد."
            )
            return {
                "inquiry_type": "supervisor_defense_question",
                "topic_key": "supervisor_reviews",
                "admin_notes": "Client asked how to justify ANCOVA over ANOVA/t-test to supervisor/committee.",
                "thinking_points": [
                    "Methodology: ANCOVA covariate error-variance reduction in quasi-experimental designs.",
                    "Epistemic Rule: Controlling baseline pre-test scores maximizes statistical power (Cohen, 1988).",
                    "Consulting Strategy: Provide exact APA 7 formula block and ready-to-speak viva voce defense statement."
                ],
                "draft_reply": draft,
                "engine": "rule_fallback"
            }

        # A2. Statistical Defense: SEM Fit Indices & Chi-Square dilemma
        has_sem_kw = any(w in t_lower for w in ["sem", "معادلات ساختاری", "کای اسکوئر", "کای‌اسکوئر", "برازش", "rmsea", "cfi", "tli"])
        if has_sem_kw and any(w in t_lower for w in ["چرا", "دلیل", "معنادار", "دفاع", "توجیه", "شاخص", "مدل", "استاد", "داور"]):
            if AcademicMathFormatter:
                f_data = AcademicMathFormatter.format_sem_fit(342.15, 185, 0.0001, 0.048, 0.952, 0.941, 0.039, lang="fa")
                f_html = f_data["t_html"]
                viva_speech = f_data["viva_defense_fa"]
            else:
                f_html = "χ²(۱۸۵) = ۳۴۲.۱۵، <i>p</i> &lt; ۰.۰۰۱، χ²/<i>df</i> = ۱.۸۵\nRMSEA = ۰.۰۴۸ [90% CI: ۰.۰۰۰، ۰.۰۷۸]\nCFI = ۰.۹۵۲، TLI = ۰.۹۴۱، SRMR = ۰.۰۳۹"
                viva_speech = "«آماره کای‌اسکوئر به حجم نمونه حساس است؛ لذا طبق کلاین (2015) برآیند شاخص‌های CFI, TLI, RMSEA ملاک برازش است.»"

            draft = (
                f"سلام و احترام {first_name} گرامی.\n"
                "پیرامون دفاع از برازش مدل معادلات ساختاری (SEM) و معنادار شدن کای‌اسکوئر (χ²)، پاسخ مستدل علمی خدمت شما تقدیم می‌شود:\n\n"
                f"📐 **شاخص‌های برازش استاندارد APA 7th:**\n{f_html}\n\n"
                f"🎙️ **متن دفاع شفاهی در جلسه شورا:**\n{viva_speech}\n\n"
                "تمامی شاخص‌های برازش در دامنه عالی کلاین (2015) و هو و بنت‌لر (1999) قرار داشته و مدل از کفایت مطلق برخوردار است."
            )
            return {
                "inquiry_type": "supervisor_defense_question",
                "topic_key": "supervisor_reviews",
                "admin_notes": "Client asked how to defend SEM fit indices and significant chi-square to committee.",
                "thinking_points": [
                    "Methodology: Chi-square sample size sensitivity (Kline, 2015; Bollen, 1989).",
                    "Epistemic Rule: Multi-index evaluation framework (RMSEA < .08, CFI/TLI > .90, SRMR < .08).",
                    "Consulting Strategy: Provide APA 7th fit indices block and authoritative viva voce defense statement."
                ],
                "draft_reply": draft,
                "engine": "rule_fallback"
            }

        # A3. Statistical Defense: Sample Size & G*Power dilemma
        has_sample_kw = any(w in t_lower for w in ["حجم نمونه", "gpower", "جی‌پاور", "جی پاور", "کفایت نمونه"])
        if has_sample_kw and any(w in t_lower for w in ["چرا", "کم", "کمه", "کافی", "کفایت", "دفاع", "توجیه", "محاسبه", "گیر"]):
            if AcademicMathFormatter:
                f_data = AcademicMathFormatter.format_gpower("ancova", 64, 0.05, 0.85, 0.25, lang="fa")
                f_html = f_data["t_html"]
                viva_speech = f_data["viva_defense_fa"]
            else:
                f_html = "👥 <i>N</i> = ۶۴ | اندازه اثر <i>f</i> = ۰.۲۵ | α = ۰.۰۵ | توان آزمون (1 - β) = ۰.۸۵"
                viva_speech = "«تعیین حجم نمونه طبق روش فاول و همکاران (2007) در G*Power با توان بالای ۸۵ درصد محاسبه شد.»"

            draft = (
                f"سلام و درود {first_name} گرامی.\n"
                "جهت دفاع از کفایت حجم نمونه در برابر پرسش اساتید محترم، استدلال و محاسبات دقیق جی‌پاور آماده است:\n\n"
                f"⚙️ **محاسبات توان آماری (G*Power 3.1.9.7):**\n{f_html}\n\n"
                f"🎙️ **متن دفاعیه دانشجو:**\n{viva_speech}\n\n"
                "با این محاسبات، توان آماری طرح بالای ۸۵ درصد تضمین شده و احتمال خطای نوع دوم کاملاً مهار گردیده است."
            )
            return {
                "inquiry_type": "supervisor_defense_question",
                "topic_key": "supervisor_reviews",
                "admin_notes": "Client inquired about defending sample size adequacy via G*Power.",
                "thinking_points": [
                    "Methodology: A priori statistical power analysis using G*Power 3.1.9.7 (Faul et al., 2007, 2009).",
                    "Epistemic Rule: Cohen's medium effect size (f = .25) achieves 85% statistical power at N = 64.",
                    "Consulting Strategy: Arm the student with deterministic G*Power parameters and oral defense argument."
                ],
                "draft_reply": draft,
                "engine": "rule_fallback"
            }

        # A4. Supervisor defense justification dilemma (e.g. "چرا مقالات خارجی")
        if any(q in t_lower for q in ["چرا از مقالات خارجی", "مقالات خارجی استفاده کردم", "اگه پرسیدن چرا", "اگر استاد بپرسه", "اگر داور بپرسه", "چی جواب بدم"]):
            draft = (
                f"سلام و عرض احترام {first_name} گرامی.\n"
                "در پاسخ به پرسش استاد یا داوران محترم، می‌توانید این سه محور علمی و مستدل را مطرح بفرمایید:\n"
                "۱. **اصالت و خاستگاه نظری:** مبانی مفهومی و مدل‌های استاندارد متغیرهای پژوهش نخستین بار در ادبیات بین‌المللی فرمول‌بندی شده‌اند و ارجاع به آن‌ها برای حفظ دقت تئوریک ضروری است.\n"
                "۲. **روزآمدی شواهد تجربی (2020-2025):** استفاده از مقالات معتبر Scopus و WoS نشان‌دهنده احاطه به جدیدترین یافته‌ها و متدهای جهانی پژوهش است.\n"
                "۳. **روایی فرهنگی و بافت بومی:** مطالعات داخلی در کنار پژوهش‌های خارجی به عنوان مکمل و جهت بررسی همخوانی یافته‌ها در جامعه ایرانی به کار رفته‌اند تا از هرگونه سوگیری بومی‌سازی محدود پیشگیری شود."
            )
            return {
                "inquiry_type": "supervisor_defense_question",
                "topic_key": "supervisor_reviews",
                "admin_notes": f"Client asked how to justify methodological choices (foreign literature) to supervisor/defense committee.",
                "thinking_points": [
                    "Methodology: Justifying international Scopus/WoS literature vs. localized research sources.",
                    "Epistemic Rule: Theoretical origins dictate primary international source citation (APA 7th).",
                    "Consulting Strategy: Provide a 3-part epistemic defense (conceptual origin, 2020-2025 currency, cross-cultural validity)."
                ],
                "draft_reply": draft,
                "engine": "rule_fallback"
            }

        # B. Supervisor comments or signed form
        if any(w in t_lower for w in ["فرم امضا", "استاد فرم", "امضا کردن", "اصلاحیه استاد", "کامنت استاد", "اصلاحات داور"]):
            draft = (
                f"سلام و درود {first_name} گرامی.\n"
                "فایل و موارد ارسالی دریافت شد؛ فرم امضاشده و اصلاحات مدنظر استاد محترم را دقیق بررسی می‌کنم و نکات مربوط به ویرایش‌ها یا مدارک موردنیاز جهت بارگذاری را خدمتتون اعلام خواهم کرد."
            )
            return {
                "inquiry_type": "supervisor_revision_feedback",
                "topic_key": "supervisor_reviews",
                "admin_notes": f"Supervisor-signed form or revision feedback received.",
                "thinking_points": [
                    "Methodology: Supervisor feedback triage across structural, statistical, and formatting layers.",
                    "Epistemic Rule: Point-by-point compliance table required for formal thesis approval.",
                    "Consulting Strategy: Reassure client and systematically audit supervisor changes before implementation."
                ],
                "draft_reply": draft,
                "engine": "rule_fallback"
            }

        # C. Quarterly progress report / portal upload
        if any(w in t_lower for w in ["گزارش سه ماهه", "سه ماهه اول", "سه ماهه دوم", "بارگذاری", "پژوهشیار", "سامانه"]):
            draft = (
                f"سلام و احترام {first_name} گرامی.\n"
                "گزارش‌های سه‌ماهه بر اساس روند پیشرفت پایان‌نامه و جداول زمان‌بندی تصویب‌شده آماده و جهت بارگذاری در سامانه خدمتتون تقدیم می‌شود."
            )
            return {
                "inquiry_type": "quarterly_progress_report",
                "topic_key": "supervisor_reviews",
                "admin_notes": f"Request for quarterly progress reports and portal upload.",
                "thinking_points": [
                    "Methodology: University thesis progress tracking & portal milestone verification.",
                    "Epistemic Rule: Institutional tracking forms require matching approved proposal timelines.",
                    "Consulting Strategy: Guide candidate on required supervisor signatures and portal upload."
                ],
                "draft_reply": draft,
                "engine": "rule_fallback"
            }

        # D. Friendly casual conversation (e.g. modem, address, personal)
        if any(w in t_lower for w in ["مودم", "آدرس", "کد پستی", "پستی", "تلفنت"]):
            draft = (
                f"سلام صمیمانه {first_name} جان، خیلی ممنون از لطف و محبتت.\n"
                "مشخصات و آدرس خدمتت ارسال شد؛ بابت پیگیری و هماهنگی ارسال مودم هم یک دنیا سپاسگزارم."
            )
            return {
                "inquiry_type": "friendly_personal",
                "topic_key": "drafts",
                "admin_notes": f"Friendly/personal discussion regarding modem and contact address.",
                "thinking_points": [
                    "Methodology: Non-academic relational communication & logistics.",
                    "Epistemic Rule: Professional warm rapport.",
                    "Consulting Strategy: Prompt, courteous response acknowledging details."
                ],
                "draft_reply": draft,
                "engine": "rule_fallback"
            }

        # E. General greeting
        if any(w in t_lower for w in ["سلام", "درود", "وقت بخیر"]) and len(text.split()) <= 6:
            draft = (
                f"سلام و عرض ادب، وقت شما بخیر {first_name} گرامی.\n"
                "صابر قادری هستم، در خدمتم؛ لطفاً بفرمایید موضوع پژوهش یا فایلی که مدنظرتون هست مربوط به چه بخشی است تا راهنمایی‌تون کنم."
            )
            return {
                "inquiry_type": "greeting",
                "topic_key": "drafts",
                "admin_notes": f"Standard initial greeting.",
                "thinking_points": [
                    "Methodology: Initial prospective research inquiry.",
                    "Epistemic Rule: Polite scholarly reception and inquiry scoping.",
                    "Consulting Strategy: Warm greeting asking for research topic or draft file."
                ],
                "draft_reply": draft,
                "engine": "rule_fallback"
            }

        # Default fallback
        draft = (
            f"سلام و احترام، وقت شما بخیر {first_name} گرامی.\n"
            "پیام شما دریافت شد. در خدمتم؛ موارد ارسالی رو با دقت بررسی و راهنمایی لازم رو خدمتتون تقدیم خواهم کرد."
        )
        return {
            "inquiry_type": "client_burst_inquiry",
            "topic_key": "drafts",
            "admin_notes": f"General client inquiry.",
            "thinking_points": [
                "Methodology: Exploratory research consultation inquiry.",
                "Epistemic Rule: Scoping client objectives prior to methodological recommendation.",
                "Consulting Strategy: Invite research question details or proposal draft for evaluation."
            ],
            "draft_reply": draft,
            "engine": "rule_fallback"
        }
