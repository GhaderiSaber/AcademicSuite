import zipfile
import re
import os

docx_path = "03_deliverables/12_hypothesis_7.docx"
out_path = "03_deliverables/12_hypothesis_7_fixed.docx"

with zipfile.ZipFile(docx_path, "r") as zin:
    with zipfile.ZipFile(out_path, "w") as zout:
        for item in zin.infolist():
            content = zin.read(item.filename)
            if item.filename == "word/document.xml":
                text = content.decode("utf-8")
                
                # Replace <w:br/> with <w:p/>
                text = text.replace('<w:br/>', '')
                
                # Enforce <w:jc w:val="both"/> for all w:p that don't have it (crude but effective)
                text = re.sub(r'(<w:pPr>)(?!\s*<w:jc)', r'\1<w:jc w:val="both"/>', text)
                
                # Remove <w:jc w:val="right"/>
                text = text.replace('<w:jc w:val="right"/>', '<w:jc w:val="both"/>')
                
                # Ensure all B Titr are B Nazanin except for headings if any
                text = text.replace('B Titr', 'B Nazanin')
                
                content = text.encode("utf-8")
                
            zout.writestr(item, content)

os.replace(out_path, docx_path)
print("Fixed docx successfully")
