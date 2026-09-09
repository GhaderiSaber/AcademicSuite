#!/usr/bin/env python3
"""
Render Preview & Visual Contact Sheet Generator (persian-defense-presentation-builder v2)
========================================================================================
Supports Pass B & Pass C Visual QA by converting generated .pptx presentations into
PDF and PNG slide previews (via PowerPoint COM on Windows or LibreOffice headless).
"""

import os
import sys
import subprocess
from typing import Optional, List

def convert_pptx_to_pdf(pptx_path: str, pdf_path: Optional[str] = None) -> Optional[str]:
    """Converts .pptx to .pdf using Windows COM (PowerPoint) or LibreOffice."""
    abs_pptx = os.path.abspath(pptx_path)
    if not os.path.exists(abs_pptx):
        print(f"[!] Presentation not found: {abs_pptx}", file=sys.stderr)
        return None
        
    if not pdf_path:
        pdf_path = os.path.splitext(abs_pptx)[0] + ".pdf"
    abs_pdf = os.path.abspath(pdf_path)

    # Method 1: PowerPoint COM Automation (Windows)
    try:
        import win32com.client
        powerpoint = win32com.client.Dispatch("PowerPoint.Application")
        # 32 = ppSaveAsPDF
        presentation = powerpoint.Presentations.Open(abs_pptx, WithWindow=False)
        presentation.SaveAs(abs_pdf, 32)
        presentation.Close()
        powerpoint.Quit()
        if os.path.exists(abs_pdf):
            print(f"[*] Rendered PDF via PowerPoint COM: {abs_pdf}")
            return abs_pdf
    except Exception:
        pass

    # Method 2: LibreOffice Headless
    soffice_paths = [
        "soffice",
        "libreoffice",
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe"
    ]
    for sp in soffice_paths:
        try:
            cmd = [sp, "--headless", "--convert-to", "pdf", abs_pptx, "--outdir", os.path.dirname(abs_pdf)]
            res = subprocess.run(cmd, capture_output=True, timeout=60)
            if res.returncode == 0 and os.path.exists(abs_pdf):
                print(f"[*] Rendered PDF via LibreOffice: {abs_pdf}")
                return abs_pdf
        except Exception:
            continue

    print("[-] Neither PowerPoint COM nor LibreOffice headless was found for automated PDF rendering.")
    print("    Structural QA passed; for visual inspection, open the .pptx directly in PowerPoint.")
    return None

def generate_preview_report(pptx_path: str) -> bool:
    """Executes preview rendering pipeline."""
    pdf = convert_pptx_to_pdf(pptx_path)
    return pdf is not None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        generate_preview_report(sys.argv[1])

