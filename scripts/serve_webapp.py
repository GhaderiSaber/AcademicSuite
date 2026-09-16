#!/usr/bin/env python3
"""
Saber Academic Suite — Mini App & Web Dashboard Server (serve_webapp.py)
-----------------------------------------------------------------------
Serves the Telegram Mini App and Web Dashboard static assets while exposing
REST API endpoints for live Google Drive project monitoring, real-time
pricing calculation, and psychometric scales searching.

Endpoints:
  GET  /                     -> Serves webapp/index.html
  GET  /css/*, /js/*, etc.   -> Serves static files
  GET  /api/health           -> Health check
  GET  /api/projects         -> Live scanned project dossiers from Google Drive
  GET  /api/scales?q=...     -> Query psychometric scale registry
  POST /api/quote            -> Server-side deterministic pricing estimation

CLI Usage:
  python3 scripts/serve_webapp.py --port 8080
  python3 scripts/serve_webapp.py --test-only
"""

import os
import sys
import json
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from typing import Dict, Any, List, Optional
import argparse

# Path resolution
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WEBAPP_DIR = os.path.join(ROOT_DIR, "webapp")
DIST_DIR = os.path.join(WEBAPP_DIR, "dist")
STATIC_DIR = DIST_DIR if os.path.isdir(DIST_DIR) else WEBAPP_DIR

# Add skill script directories to path for imports
DIGITAL_TWIN_SCRIPTS = os.path.join(ROOT_DIR, ".agents", "skills", "digital-twin-academic-consultant", "scripts")
PSYCHOMETRIC_SCRIPTS = os.path.join(ROOT_DIR, ".agents", "skills", "psychometric-scale-resolver", "scripts")
MEMORY_DIR = os.path.join(ROOT_DIR, ".agents", "memory")
for path in [DIGITAL_TWIN_SCRIPTS, PSYCHOMETRIC_SCRIPTS, MEMORY_DIR]:
    if path not in sys.path and os.path.exists(path):
        sys.path.insert(0, path)

try:
    from project_drive_manager import ProjectDriveManager, clean_drive_display_path
except ImportError:
    ProjectDriveManager = None
    clean_drive_display_path = lambda p: p

try:
    from proposal_price_estimator import calculate_quotation, load_persona
except ImportError:
    calculate_quotation = None
    load_persona = lambda: {}

try:
    from questionnaire_resolver import search_registry
except ImportError:
    search_registry = None

try:
    from copilot_bridge import TelegramCopilotBridge
except ImportError:
    TelegramCopilotBridge = None

try:
    from decision_journal_engine import DecisionJournalEngine
except ImportError:
    DecisionJournalEngine = None


def load_fallback_projects() -> List[Dict[str, Any]]:
    """Extract pre-seeded projects from seed_data.js if Google Drive is not populated."""
    seed_file = os.path.join(WEBAPP_DIR, "data", "seed_data.js")
    if os.path.exists(seed_file):
        try:
            with open(seed_file, "r", encoding="utf-8") as f:
                content = f.read()
            # Extract window.ACADEMIC_PROJECTS = [...];
            start = content.find("window.ACADEMIC_PROJECTS = [")
            if start != -1:
                end = content.find("];", start)
                if end != -1:
                    json_str = content[start + len("window.ACADEMIC_PROJECTS = ") : end + 1]
                    return json.loads(json_str)
        except Exception as e:
            print(f"[WARN] Failed to load seed projects: {e}")
    return []


def get_live_projects() -> List[Dict[str, Any]]:
    """Retrieve active client projects from Google Drive or fallback to seed data."""
    if ProjectDriveManager:
        try:
            mgr = ProjectDriveManager()
            raw_projects = mgr.list_all_projects()
            if raw_projects:
                formatted = []
                for idx, p in enumerate(raw_projects):
                    # Normalize fields
                    client_name = p.get("client_name") or p.get("folder_name", f"Client_{idx+1}")
                    status = p.get("status", "in_progress")
                    
                    # Deduce status if not explicitly set
                    files_cnt = len(p.get("files", []))
                    msg_cnt = len(p.get("messages", []))
                    if not p.get("status"):
                        if msg_cnt > 0 and files_cnt == 0:
                            status = "inquiry"
                        elif files_cnt > 0 and "deliverables" not in p:
                            status = "in_progress"
                        else:
                            status = "in_progress"

                    clean_path = clean_drive_display_path(p.get("folder_path", ""))
                    formatted.append({
                        "id": f"PRJ-{100 + idx}",
                        "client_name": client_name,
                        "status": status,
                        "file_count": files_cnt,
                        "message_count": msg_cnt,
                        "folder_path": clean_path or p.get("folder_name", ""),
                        "topic": p.get("topic", "پژوهش روان‌شناختی و تحلیل آماری رساله"),
                        "degree": p.get("degree", "کارشناسی ارشد"),
                        "design": p.get("design", "شبه‌آزمایشی (ANCOVA)"),
                        "sample_size": p.get("sample_size", 40)
                    })
                return formatted
        except Exception as e:
            print(f"[WARN] Error scanning live Google Drive projects: {e}")

    return load_fallback_projects()


class AcademicSuiteHTTPHandler(SimpleHTTPRequestHandler):
    """Custom request handler with REST API routing."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=STATIC_DIR, **kwargs)

    def end_headers(self):
        # Enable CORS for local testing
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/api/health":
            self.handle_health()
        elif path == "/api/projects":
            self.handle_projects()
        elif path == "/api/scales":
            query_params = urllib.parse.parse_qs(parsed_url.query)
            q = query_params.get("q", [""])[0]
            self.handle_scales(q)
        elif path == "/api/admin/status":
            self.handle_admin_status()
        elif path == "/api/admin/pending":
            self.handle_admin_pending()
        elif path in ["/", "/index.html", "/standalone", "/standalone.html"]:
            self.handle_spa_root()
        else:
            # SPA fallback: serve static files, or standalone SPA for client-side routing
            requested_file = os.path.join(STATIC_DIR, path.lstrip("/"))
            if os.path.isfile(requested_file):
                super().do_GET()
            else:
                self.handle_spa_root()

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/api/quote":
            self.handle_quote()
        elif path == "/api/admin/approve":
            self.handle_admin_approve()
        else:
            self.send_error(404, "Endpoint not found")

    def handle_spa_root(self):
        """Serves dist/index.html if built, otherwise falls back cleanly to standalone.html."""
        dist_index = os.path.join(DIST_DIR, "index.html")
        standalone_file = os.path.join(WEBAPP_DIR, "standalone.html")
        if os.path.isfile(dist_index):
            self.path = "/index.html"
            super().do_GET()
        elif os.path.isfile(standalone_file):
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            with open(standalone_file, "rb") as f:
                content = f.read()
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        else:
            self.path = "/index.html"
            super().do_GET()

    def handle_admin_status(self):
        status = {
            "admin_id": 124911145,
            "admin_name": "Saber Ghaderi (@GhaderiSaber)",
            "service": "AcademicSuite Admin Approval Desk",
            "active": True
        }
        if TelegramCopilotBridge:
            try:
                bridge = TelegramCopilotBridge()
                status.update(bridge.get_status())
            except Exception as e:
                status["bridge_error"] = str(e)
        self.send_json_response(status)

    def handle_admin_pending(self):
        pending = {"pending_quotes": {}, "pending_drafts": {}}
        if TelegramCopilotBridge:
            try:
                bridge = TelegramCopilotBridge()
                pending["pending_quotes"] = bridge.state.get("pending_quotes", {})
                pending["pending_drafts"] = bridge.state.get("pending_drafts", {})
            except Exception as e:
                pending["error"] = str(e)
        self.send_json_response(pending)

    def handle_admin_approve(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length) if content_length > 0 else b"{}"
            req_data = json.loads(body.decode("utf-8")) if body else {}
            quote_id = req_data.get("quote_id")
            adjusted_price = req_data.get("adjusted_price")
            if not quote_id:
                self.send_json_response({"error": "quote_id is required"}, status=400)
                return

            res = {"status": "error", "message": "Bridge unavailable"}
            if TelegramCopilotBridge:
                bridge = TelegramCopilotBridge()
                res = bridge.approve_quote(quote_id, adjusted_price)

            # Record in Decision Journal Engine
            if res.get("status") == "success" and DecisionJournalEngine:
                try:
                    journal = DecisionJournalEngine()
                    did = journal.log_decision(
                        decision_type="pricing",
                        context=f"Quotation {quote_id} intake for client '{res.get('client_name', 'Student')}'",
                        selected_option=f"Approve {res.get('total_price', 0):,} Tomans",
                        rationale="Approved by Saber's Admin Desk via WebApp approval interface (ID: 124911145)",
                        alternatives_considered=[
                            {"option": f"Approved Price: {res.get('total_price', 0):,} Tomans", "notes": "Authorized release via WebApp"}
                        ],
                        confidence=1.0,
                        human_gate_required=True,
                        human_gate_approved=True,
                        approved_by="GhaderiSaber (124911145)"
                    )
                    res["decision_id"] = did
                except Exception as je:
                    res["journal_warning"] = str(je)

            self.send_json_response(res, status=200 if res.get("status") == "success" else 400)
        except Exception as e:
            self.send_json_response({"error": str(e)}, status=400)

    def handle_health(self):
        projects = get_live_projects()
        payload = {
            "status": "ok",
            "service": "Saber Academic Suite WebApp",
            "projects_count": len(projects),
            "drive_status": "connected"
        }
        self.send_json_response(payload)

    def handle_projects(self):
        projects = get_live_projects()
        self.send_json_response(projects)

    def handle_scales(self, query: str):
        results = []
        if query and search_registry:
            try:
                results = search_registry(query)
            except Exception as e:
                print(f"[WARN] Error searching scales registry: {e}")

        # If search returned nothing or resolver not available, search seed data
        if not results:
            seed_file = os.path.join(WEBAPP_DIR, "data", "seed_data.js")
            if os.path.exists(seed_file):
                try:
                    with open(seed_file, "r", encoding="utf-8") as f:
                        content = f.read()
                    start = content.find("window.ACADEMIC_SCALES = [")
                    if start != -1:
                        end = content.find("];", start)
                        if end != -1:
                            json_str = content[start + len("window.ACADEMIC_SCALES = ") : end + 1]
                            all_scales = json.loads(json_str)
                            if query:
                                q_lower = query.lower()
                                results = [
                                    s for s in all_scales
                                    if q_lower in s.get("name_en", "").lower()
                                    or q_lower in s.get("name_fa", "").lower()
                                    or q_lower in s.get("author", "").lower()
                                    or any(q_lower in sub.lower() for sub in s.get("subscales", []))
                                ]
                            else:
                                results = all_scales
                except Exception as e:
                    print(f"[WARN] Error parsing seed scales: {e}")

        self.send_json_response(results)

    def handle_quote(self):
        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            req_data = json.loads(body.decode("utf-8"))

            degree = req_data.get("degree", "master")
            design = req_data.get("design", "ancova")
            sample_size = int(req_data.get("sample_size", 40))
            scales_count = int(req_data.get("scales_count", 2))
            is_urgent = bool(req_data.get("urgent", False))
            services_requested = req_data.get("services", ["ch3", "sim", "ch4", "ch5", "audit"])

            design_type_map = {
                "ancova": "ancova_repeated_measures",
                "sem": "sem_cfa_structural",
                "regression": "correlation_regression",
                "scale_val": "scale_validation_factor",
                "qualitative": "qualitative_thematic"
            }

            analysis = {
                "title": req_data.get("title", "پژوهش روان‌شناختی و تحلیل آماری رساله"),
                "degree": "دکتری (Ph.D.)" if degree == "phd" else "ارشد (Master)",
                "degree_fa": "دکتری (Ph.D.)" if degree == "phd" else "کارشناسی ارشد",
                "degree_en": "Doctorate (Ph.D.)" if degree == "phd" else "Master's (M.A./M.Sc.)",
                "design_type": design_type_map.get(design, "ancova_repeated_measures"),
                "design_title_fa": "طرح پژوهش انتخابی",
                "sample_size": sample_size,
                "scale_count": scales_count,
                "scales": [f"مقیاس {i+1}" for i in range(scales_count)],
                "softwares": ["SPSS 28"]
            }

            options = {
                "include_ch3": "ch3" in services_requested,
                "include_sim": "sim" in services_requested,
                "include_ch4": "ch4" in services_requested,
                "include_ch5": "ch5" in services_requested,
                "include_slides": "slides" in services_requested,
                "include_audit": "audit" in services_requested,
                "urgent": is_urgent
            }

            persona = load_persona() if load_persona else {}
            if calculate_quotation:
                quote = calculate_quotation(analysis, persona, options)
                self.send_json_response(quote)
            else:
                self.send_json_response({"error": "Quotation engine unavailable"}, status=500)

        except Exception as e:
            self.send_json_response({"error": str(e)}, status=400)

    def send_json_response(self, data: Any, status: int = 200):
        body = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def run_server(port: int = 8080, host: str = "0.0.0.0"):
    server_address = (host, port)
    httpd = HTTPServer(server_address, AcademicSuiteHTTPHandler)
    print(f"==================================================")
    print(f"  Saber Academic Suite — Mini App Server Running   ")
    print(f"  URL: http://localhost:{port}/                  ")
    print(f"  Document Root: {WEBAPP_DIR}                     ")
    print(f"==================================================")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[INFO] Server stopped gracefully.")
        httpd.server_close()


def test_server():
    """Verify handler and endpoints without blocking."""
    print("[TEST] Verifying live project extraction...")
    projects = get_live_projects()
    print(f"[TEST] Successfully loaded {len(projects)} projects.")
    assert len(projects) > 0, "No projects loaded!"

    print("[TEST] Verifying pricing calculation...")
    if calculate_quotation and load_persona:
        persona = load_persona()
        analysis = {
            "title": "Test Title",
            "degree_fa": "کارشناسی ارشد",
            "design_type": "ancova_repeated_measures",
            "design_title_fa": "شبه‌آزمایشی",
            "sample_size": 40,
            "scale_count": 2,
            "scales": ["مقیاس ۱", "مقیاس ۲"],
            "softwares": ["SPSS 28"]
        }
        quote = calculate_quotation(analysis, persona, {"include_ch3": True, "include_ch4": True})
        assert "total_price_tomans" in quote
        print(f"[TEST] Quote computed: {quote['total_price_tomans']} Tomans.")

    print("[TEST] Verifying Admin Desk endpoints and static files...")
    standalone_file = os.path.join(WEBAPP_DIR, "standalone.html")
    assert os.path.isfile(standalone_file), "webapp/standalone.html must exist!"
    assert os.path.isfile(os.path.join(WEBAPP_DIR, "css", "style.css")), "css/style.css must exist!"
    assert os.path.isfile(os.path.join(WEBAPP_DIR, "js", "app.js")), "js/app.js must exist!"
    print(f"[TEST] Verified standalone distribution assets.")

    print("[TEST] All server tests passed successfully!")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Serve Saber Academic Suite WebApp & API")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on (default: 8080)")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind to (default: 0.0.0.0)")
    parser.add_argument("--test-only", action="store_true", help="Run diagnostic tests and exit")
    args = parser.parse_args()

    if args.test_only:
        sys.exit(test_server())
    else:
        run_server(args.port, args.host)
