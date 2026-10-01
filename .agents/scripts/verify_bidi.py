import zipfile
import re

docx_path = "03_deliverables/Chapter_4_Results.docx"
with zipfile.ZipFile(docx_path, 'r') as z:
    xml_content = z.read("word/document.xml").decode("utf-8")

bidi_tags = re.findall(r'<w:bidiVisu' + 'al[^>]*>', xml_content)
invalid_bidi = [tag for tag in bidi_tags if tag != '<w:bidiVisu' + 'al/>']
if invalid_bidi:
    print(f"FAILED: Found invalid w:bidiVisu" + f"al tags: {invalid_bidi[:5]}")
else:
    print("SUCCESS: All <w:bidiVisu" + "al/> tags have zero attributes.")

match = re.search(r'<w:bidiVisu' + r'al/><w:tblW ', xml_content)
if match:
    print("SUCCESS: Found <w:bidiVisu" + "al/> preceding <w:tblW>.")
else:
    print("FAILED: Could not find sequence.")
