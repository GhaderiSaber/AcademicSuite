#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
factory/cli.py — Academic Suite Autonomous Agent & Skill Factory CLI

CLI entrypoint to generate new domain specialists, skills, agents, and validators.
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

from factory.meta_factory import (
    create_specialist,
    build_longitudinal_modmed_specialist
)


def main():
    parser = argparse.ArgumentParser(description="Academic Suite Autonomous Specialist Factory CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # generate-specialist
    p_gen = subparsers.add_parser("generate-specialist", help="Generate and test a full domain specialist package")
    p_gen.add_argument("--spec", help="Path to JSON specialist specification file")
    p_gen.add_argument("--name", default="longitudinal-moderated-mediation", help="Specialist domain name or template")
    p_gen.add_argument("--target-root", help="Optional root directory path")
    p_gen.add_argument("--no-sandbox", action="store_true", help="Skip pre-registration sandbox test")

    args = parser.parse_args()

    if args.command == "generate-specialist":
        if args.spec:
            if not os.path.exists(args.spec):
                print(f"❌ Error: Specification file not found: {args.spec}")
                sys.exit(1)
            with open(args.spec, "r", encoding="utf-8") as f:
                spec = json.load(f)
            spec_name = spec.get("name") or spec.get("agent_name", "custom-specialist")
            print(f"🏭 Factory activating: Generating specialist from spec '{args.spec}' ({spec_name})...")
            manifest = create_specialist(
                spec=spec,
                target_root=args.target_root,
                run_sandbox=not args.no_sandbox
            )
        elif args.name in ["longitudinal-moderated-mediation", "longitudinal-modmed", "longitudinal-modmed-expert"]:
            print(f"🏭 Factory activating: Generating specialist for '{args.name}'...")
            manifest = build_longitudinal_modmed_specialist(target_root=args.target_root)
        else:
            print(f"Custom specialist '{args.name}' requested without a --spec file.")
            print("Please provide a JSON specification via `--spec <path/to/spec.json>`.")
            sys.exit(1)

        print(f"✓ Specialist '{manifest['specialist_name']}' generated and certified!")
        print(f"  Agent: {manifest['agent']['file_path']}")
        print(f"  Skill: {manifest['skill']['skill_file']}")
        print(f"  Validator: {manifest['validator']['file_path']}")
        print(f"  Evaluation Case: {manifest.get('evaluation_case')}")
        print(f"  Pre-Registration Test Verdict: {manifest['preregistration_sandbox_test']['overall_verdict']}")
        print(f"  Registration Status: {manifest['registration_status']}")


if __name__ == "__main__":
    main()
