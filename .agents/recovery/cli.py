#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
recovery/cli.py — Academic Suite Failure Recovery CLI Interface

Enables command-line diagnosis, routing, incident creation, and resolution.
"""

import os
import sys
import json
import argparse

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

for venv_name in [".venv", "venv"]:
    venv_lib = os.path.join(ROOT_DIR, venv_name, "lib")
    if os.path.isdir(venv_lib):
        for entry in os.listdir(venv_lib):
            sp = os.path.join(venv_lib, entry, "site-packages")
            if os.path.isdir(sp) and sp not in sys.path:
                sys.path.insert(0, sp)

from recovery.diagnostics import diagnose_failure
from recovery.router import route_failure
from recovery.recovery_engine import create_incident, resolve_incident, format_incident_markdown


def main():
    parser = argparse.ArgumentParser(description="Academic Suite Failure Recovery CLI")
    subparsers = parser.add_subparsers(dest="command", help="Recovery action to perform")

    # 1. diagnose
    p_diag = subparsers.add_parser("diagnose", help="Diagnose an error string")
    p_diag.add_argument("--error", required=True, help="Error message or exception trace")

    # 2. route
    p_route = subparsers.add_parser("route", help="Route a diagnosed failure type")
    p_route.add_argument("--type", required=True, help="FailureType (DATA, TOOL, STATISTICAL, etc.)")
    p_route.add_argument("--stage-id", required=True, help="Failing micro-stage ID")
    p_route.add_argument("--error", default="", help="Error message context")

    # 3. create-incident
    p_create = subparsers.add_parser("create-incident", help="Create and record a structured incident")
    p_create.add_argument("--stage-id", required=True, help="Failing micro-stage ID")
    p_create.add_argument("--error", required=True, help="Error message or exception trace")
    p_create.add_argument("--project", help="Optional project directory path")
    p_create.add_argument("--markdown", action="store_true", help="Print executive markdown summary")

    args = parser.parse_args()

    if args.command == "diagnose":
        res = diagnose_failure(args.error)
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.command == "route":
        res = route_failure(args.type, args.stage_id, args.error)
        print(json.dumps(res, indent=2, ensure_ascii=False))

    elif args.command == "create-incident":
        inc = create_incident(args.stage_id, args.error, project_path=args.project)
        if args.markdown:
            print(format_incident_markdown(inc))
        else:
            print(json.dumps(inc, indent=2, ensure_ascii=False))

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
