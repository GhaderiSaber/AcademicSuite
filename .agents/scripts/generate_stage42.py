import sys
import os

# Add the directory to sys.path to import the module
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(script_dir)

from structured_docx_generator import build_structured_docx

json_path = "/home/ghaderi-saber/My Work/Mohtasham Valiyanpur/03_deliverables/02_descriptives_and_reliability.json"
md_path = "/home/ghaderi-saber/My Work/Mohtasham Valiyanpur/03_deliverables/02_descriptives_and_reliability.md"
docx_path = "/home/ghaderi-saber/My Work/Mohtasham Valiyanpur/03_deliverables/02_descriptives_and_reliability.docx"

try:
    build_structured_docx(json_path, md_path, docx_path)
    print(f"Successfully generated DOCX at {docx_path}")
except Exception as e:
    print(f"Error generating DOCX: {e}")
    sys.exit(1)
