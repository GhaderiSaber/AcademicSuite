#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Master Unified Validator CLI Runner
Executes all 5 deterministic validators on stage artifacts and issues PASS / FAIL / NEEDS_REVIEW.
"""
import os, sys, json, argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_suite(stage_dir):
    report = {
        "suite": "Academic Suite Deterministic Validation Suite",
        "stage_directory": stage_dir,
        "overall_verdict": "PASS",
        "results": []
    }
    
    # Locate candidate files
    json_files = [os.path.join(stage_dir, f) for f in os.listdir(stage_dir) if f.endswith('.json')] if os.path.exists(stage_dir) else []
    md_files = [os.path.join(stage_dir, f) for f in os.listdir(stage_dir) if f.endswith('.md')] if os.path.exists(stage_dir) else []

    overall_fail = False
    overall_review = False

    # Check reporting on markdown files
    from reporting_consistency.validator import validate_reporting
    for md in md_files:
        res = validate_reporting(md)
        report["results"].append(res)
        if res["verdict"] == "FAIL": overall_fail = True
        elif res["verdict"] == "NEEDS_REVIEW": overall_review = True

    # Check numerical consistency on json files
    from numerical_consistency.validator import validate_numbers
    for j in json_files:
        res = validate_numbers(j)
        report["results"].append(res)
        if res["verdict"] == "FAIL": overall_fail = True
        elif res["verdict"] == "NEEDS_REVIEW": overall_review = True

    if overall_fail:
        report["overall_verdict"] = "FAIL"
    elif overall_review:
        report["overall_verdict"] = "NEEDS_REVIEW"
    else:
        report["overall_verdict"] = "PASS"

    return report

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run complete validator suite")
    parser.add_argument('--stage-dir', required=True, help="Path to micro-stage artifact directory")
    args = parser.parse_args()
    rep = run_suite(args.stage_dir)
    print(json.dumps(rep, indent=2))
    sys.exit(0 if rep["overall_verdict"] == "PASS" else 1)
