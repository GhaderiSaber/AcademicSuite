import os
import json
import zipfile
import re

def check_validation():
    report = {
        "overall_verdict": "FAIL",
        "checks_failed": 0,
        "checks_blocked": 0,
        "details": [],
        "prescriptions": []
    }
    
    # 1. Document Conservation Invariant
    raw_docx = "01_raw_inputs/1_29925780864 (1).docx"
    rev_docx = "03_deliverables/Article_Revised.docx"
    
    if not os.path.exists(raw_docx) or not os.path.exists(rev_docx):
        report["details"].append("Missing input files for size comparison.")
        report["checks_blocked"] += 1
    else:
        raw_size = os.path.getsize(raw_docx)
        rev_size = os.path.getsize(rev_docx)
        if rev_size < 200000 or rev_size < (raw_size * 0.9):
            report["details"].append(f"Size check failed: Revised ({rev_size}) vs Raw ({raw_size})")
            report["checks_failed"] += 1
            report["prescriptions"].append("Conserve entire original document text.")
        else:
            report["details"].append(f"Size check passed: Revised ({rev_size}) >= 200000 and >= 90% of Raw ({raw_size})")

    # 2. Highlights check
    if os.path.exists(rev_docx):
        with zipfile.ZipFile(rev_docx, 'r') as docx_zip:
            xml_content = docx_zip.read('word/document.xml').decode('utf-8')
            if 'w:val="green"' not in xml_content or 'w:val="yellow"' not in xml_content:
                report["details"].append("Missing green or yellow highlights in document.xml.")
                report["checks_failed"] += 1
                report["prescriptions"].append("Ensure supervisor yellow highlights and client green highlights are present.")
            else:
                report["details"].append("Highlights (green and yellow) preserved.")
    
    # 3. Revision_Response_Table borders check
    rev_table = "03_deliverables/Revision_Response_Table.docx"
    if os.path.exists(rev_table):
        with zipfile.ZipFile(rev_table, 'r') as table_zip:
            xml_content = table_zip.read('word/document.xml').decode('utf-8')
            has_border = re.search(r'<w:insideV[^>]*w:val="([^"]+)"', xml_content)
            if has_border and has_border.group(1) != "none":
                report["details"].append("Revision_Response_Table.docx contains vertical borders.")
                report["checks_failed"] += 1
                report["prescriptions"].append("Remove <w:insideV> or set to 'none' in Response Table.")
            else:
                report["details"].append("Revision_Response_Table.docx vertical border check passed.")
    
    # 4. Persian leading zeros in Article_Revised.md
    rev_md = "03_deliverables/Article_Revised.md"
    if os.path.exists(rev_md):
        with open(rev_md, 'r', encoding='utf-8') as f:
            content = f.read()
            # check for Western dots that don't have Persian leading zero
            if re.search(r'\.[0-9]+', content):
                report["details"].append("Western decimal dot without Persian leading zero found in Markdown (e.g. .05).")
                report["checks_failed"] += 1
                report["prescriptions"].append("Convert all decimals to Persian numbers with leading zeros (e.g., ۰.۰۵).")
            else:
                report["details"].append("Persian leading zeros validated in Markdown.")
                
            # AP-2026-VALIDATOR-REGRESSION-TABLE-BLINDSPOT Check
            # Check for regression tables
            if 'Regression' in content or 'regression' in content:
                # Basic adversarial check: if "Correlations" and "ANOVA" and "Coefficients"
                if not ("Correlations" in content and "ANOVA" in content and "Coefficients" in content):
                    report["details"].append("Missing mandatory 3-table regression structure in Markdown.")
                    report["checks_failed"] += 1
                    report["prescriptions"].append("Ensure regression has exactly 3 tables: Correlations, ANOVA (11-col), Coefficients (8-col).")

    # 5. 22 Supervisor Rebuttals
    rev_table_md = "03_deliverables/Revision_Response_Table.md"
    if os.path.exists(rev_table_md):
        with open(rev_table_md, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = len(content.splitlines())
            if lines < 22:
                report["details"].append(f"Not enough lines in Revision_Response_Table.md to cover 22 rebuttals (found {lines}).")
                report["checks_failed"] += 1
                report["prescriptions"].append("Include exactly 22 supervisor rebuttals in the table.")
            else:
                report["details"].append("22 Supervisor rebuttals check passed (proxy).")

    if report["checks_failed"] == 0 and report["checks_blocked"] == 0:
        report["overall_verdict"] = "PASS"
        
    os.makedirs("03_deliverables", exist_ok=True)
    with open("03_deliverables/validation_report.json", "w") as f:
        json.dump(report, f, indent=4)
        
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    check_validation()
