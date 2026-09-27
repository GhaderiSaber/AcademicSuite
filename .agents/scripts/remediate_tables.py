import json
import os
import re
import zipfile
import tempfile
import shutil
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def set_rtl(paragraph):
    pPr = paragraph._element.get_or_add_pPr()
    bidi = OxmlElement('w:bidi')
    bidi.set(qn('w:val'), '1')
    pPr.append(bidi)

def set_font(run, name='B Nazanin', size=12):
    rPr = run._r.get_or_add_rPr()
    rFonts = OxmlElement('w:rFonts')
    rFonts.set(qn('w:ascii'), name)
    rFonts.set(qn('w:hAnsi'), name)
    rFonts.set(qn('w:cs'), name)
    rPr.append(rFonts)
    
    sz = OxmlElement('w:sz')
    sz.set(qn('w:val'), str(size * 2))
    rPr.append(sz)
    szCs = OxmlElement('w:szCs')
    szCs.set(qn('w:val'), str(size * 2))
    rPr.append(szCs)

def replace_acronyms(text):
    if not isinstance(text, str):
        return text
    replacements = {
        r'\(\*Tol\*\)': '',
        r'\(\*VIF\*\)': '',
        r'\(\*DW\*\)': '',
        r'Tol': 'رواداری',
        r'VIF': 'عامل تورم واریانس',
        r'DW': 'آماره دوربین-واتسون',
        r'IUS-FA': 'اضطراب آینده‌نگر',
        r'IUS-RA': 'اضطراب بازدارنده',
        r'IUS-T': 'تحمل‌ناپذیری عدم‌قطعیت',
        r'IUS_FA': 'اضطراب آینده‌نگر',
        r'IUS_RA': 'اضطراب بازدارنده',
        r'IUS_T': 'تحمل‌ناپذیری عدم‌قطعیت',
        r'SCI-T': 'کنترل ادراک‌شده',
        r'SCI_T': 'کنترل ادراک‌شده',
        r'Ru_Ref': 'تأمل روان‌شناختی',
        r'Ru_Bro': 'غوطه‌وری فکورانه',
        r'Ru_Dep': 'نشخوار مرتبط با افسردگی',
        r'RRS-T': 'نشخوار فکری',
        r'RRS_T': 'نشخوار فکری',
        r'PANAS-NA': 'عاطفه منفی',
        r'PA_Negative': 'عاطفه منفی',
        r'BSSI-T': 'افکار خودکشی',
        r'BSSI_T': 'افکار خودکشی',
        r'\(اضطراب آینده‌نگر\)': '',
        r'\(اضطراب بازدارنده\)': '',
        r'\(تحمل‌ناپذیری عدم‌قطعیت\)': '',
        r'\(کنترل ادراک‌شده\)': '',
        r'\(تأمل روان‌شناختی\)': '',
        r'\(غوطه‌وری فکورانه\)': '',
        r'\(نشخوار مرتبط با افسردگی\)': '',
        r'\(نشخوار فکری\)': '',
        r'\(عاطفه منفی\)': '',
        r'\(افکار خودکشی\)': ''
    }
    for k, v in replacements.items():
        text = re.sub(k, v, text)
    
    text = re.sub(r'[ \t]+', ' ', text).replace('()', '').strip()
    return text

def fix_note(note, is_correlation=False):
    if not isinstance(note, str): return note
    
    if is_correlation:
        # Only remove leading/trailing asterisks (markdown italics)
        note = re.sub(r'^\*|\*$', '', note).strip()
    else:
        # Remove all asterisks
        note = note.replace('*', '').strip()
        
    if note.startswith('یادداشت.'):
        note = note.replace('یادداشت.', 'یادداشت: ', 1)
    elif note.startswith('یادداشت:'):
        pass
    else:
        note = 'یادداشت: ' + note
    
    # Also apply acronym replacements to notes
    note = replace_acronyms(note)
    return note

def main():
    json_path = '03_deliverables/Chapter_4_Tables_Only.json'
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    doc = Document()
    md_lines = []
    
    # Sort tables by table_index
    tables = []
    for k, v in data.get('tables', {}).items():
        tables.append(v)
    tables.sort(key=lambda x: x.get('table_index', 0))
    
    for t in tables:
        idx = t.get('table_index', 0)
        
        # Insert image between Table 23-4 and Table 24-4
        if idx == 24:
            # Add image and caption
            p = doc.add_paragraph()
            set_rtl(p)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run('شکل ۴- ۱. مدل میانجی‌گری سریال')
            set_font(r, 'B Nazanin', 12)
            
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p_img.add_run()
            run.add_picture('03_deliverables/fig_serial_mediation_model.png', width=Inches(5.5))
            
            md_lines.append('شکل ۴- ۱. مدل میانجی‌گری سریال')
            md_lines.append('')
            md_lines.append('![مدل میانجی‌گری سریال](fig_serial_mediation_model.png)')
            md_lines.append('')
            
        # Add caption
        title = t.get('table_number_fa', '') + '. ' + t.get('title_fa', '')
        
        # Enforce typography
        p_cap = doc.add_paragraph()
        set_rtl(p_cap)
        # Explicitly NO BOLD, B Nazanin 12pt
        r_cap = p_cap.add_run(title)
        r_cap.bold = False
        set_font(r_cap, 'B Nazanin', 12)
        
        md_lines.append(title)
        md_lines.append('')
        
        # Fix Acronyms for Table 15 & 16 (or all to be safe)
        if idx in [15, 16]:
            if 'headers_fa' in t:
                t['headers_fa'] = [replace_acronyms(h) for h in t['headers_fa']]
            if 'rows_formatted' in t:
                for i, row in enumerate(t['rows_formatted']):
                    t['rows_formatted'][i] = [replace_acronyms(c) for c in row]
            if 'markdown' in t:
                t['markdown'] = replace_acronyms(t['markdown'])

        # Create Table in DOCX
        if 'headers_fa' in t and 'rows_formatted' in t:
            docx_table = doc.add_table(rows=1, cols=len(t['headers_fa']))
            docx_table.style = 'Table Grid'
            hdr_cells = docx_table.rows[0].cells
            for i, h in enumerate(t['headers_fa']):
                hdr_cells[i].text = str(h)
                set_rtl(hdr_cells[i].paragraphs[0])
                set_font(hdr_cells[i].paragraphs[0].runs[0], 'B Nazanin', 11)
            
            for row_data in t['rows_formatted']:
                row_cells = docx_table.add_row().cells
                for i, c in enumerate(row_data):
                    row_cells[i].text = str(c)
                    set_rtl(row_cells[i].paragraphs[0])
                    set_font(row_cells[i].paragraphs[0].runs[0], 'B Nazanin', 11)
            
            # Markdown table from markdown or build
            if 'markdown' in t:
                # We need to apply fix_note on the markdown note part
                md = t['markdown']
                md_split = md.split('\n\n')
                if len(md_split) > 1:
                    md_table = md_split[0]
                    md_note = fix_note(md_split[1], is_correlation=('همبستگی' in title))
                    md_lines.append(md_table)
                    md_lines.append('')
                    md_lines.append(md_note)
                    md_lines.append('')
                else:
                    md_lines.append(md)
                    md_lines.append('')
            else:
                # build markdown table
                md_lines.append('| ' + ' | '.join(t['headers_fa']) + ' |')
                md_lines.append('|' + '|'.join([':---:'] * len(t['headers_fa'])) + '|')
                for r in t['rows_formatted']:
                    md_lines.append('| ' + ' | '.join(str(c) for c in r) + ' |')
                md_lines.append('')
                
        # Note
        note_text = t.get('note_fa', '')
        if note_text:
            note_text = fix_note(note_text, is_correlation=('همبستگی' in title))
            p_note = doc.add_paragraph()
            set_rtl(p_note)
            r_note = p_note.add_run(note_text)
            r_note.italic = False # Ensure no italics
            set_font(r_note, 'B Nazanin', 10)
            
            # if markdown was not generated with note
            if 'markdown' not in t or '\n\n' not in t['markdown']:
                md_lines.append(note_text)
                md_lines.append('')
        
    doc.save('03_deliverables/Chapter_4_Tables_Only.docx')
    
    with open('03_deliverables/Chapter_4_Tables_Only.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_lines))
        
    # Post-process the DOCX to remove <w:jc w:val="right"/>
    with tempfile.TemporaryDirectory() as tmpdir:
        with zipfile.ZipFile('03_deliverables/Chapter_4_Tables_Only.docx', 'r') as zin:
            zin.extractall(tmpdir)
        doc_xml_path = os.path.join(tmpdir, 'word', 'document.xml')
        with open(doc_xml_path, 'r', encoding='utf-8') as f:
            xml_content = f.read()
        # Find all <w:pPr> and remove <w:jc w:val="right"/>
        xml_content = re.sub(r'<w:jc w:val="right"/>', '', xml_content)
        with open(doc_xml_path, 'w', encoding='utf-8') as f:
            f.write(xml_content)
        with zipfile.ZipFile('03_deliverables/Chapter_4_Tables_Only.docx', 'w', zipfile.ZIP_DEFLATED) as zout:
            for root, dirs, files in os.walk(tmpdir):
                for file in files:
                    filepath = os.path.join(root, file)
                    arcname = os.path.relpath(filepath, tmpdir)
                    zout.write(filepath, arcname)

if __name__ == '__main__':
    main()
