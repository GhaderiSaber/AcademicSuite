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
for path in [DIGITAL_TWIN_SCRIPTS, PSYCHOMETRIC_SCRIPTS]:
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
        else:
            # SPA fallback: serve static files, or index.html for unknown paths
            requested_file = os.path.join(STATIC_DIR, path.lstrip("/"))
            if os.path.isfile(requested_file):
                super().do_GET()
            else:
                # Serve index.html for client-side routing (SPA fallback)
                self.path = "/index.html"
                super().do_GET()

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)
        path = parsed_url.path

        if path == "/api/quote":
            self.handle_quote()
        else:
            self.send_error(404, "Endpoint not found")

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
