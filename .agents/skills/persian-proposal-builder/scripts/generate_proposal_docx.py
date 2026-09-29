import sys
import re
import zipfile
import shutil
import os

def process_docx(input_docx, output_docx, track=False):
    extract_dir = input_docx + "_extracted"
    with zipfile.ZipFile(input_docx, 'r') as docx:
        docx.extractall(extract_dir)
        
    doc_path = os.path.join(extract_dir, 'word', 'document.xml')
    with open(doc_path, 'r', encoding='utf-8') as f:
        xml_content = f.read()
        
    original_xml = xml_content
    replacements_count = 0
    
    searches = [
        ("سبک های دلبستگی بر همدلی در دانشجویان پزشکی دانشگاه علوم پزشکی قم تاثیر دارد.", "بین سبکهای دلبستگی و همدلی در دانشجویان پزشکی دانشگاه علوم پزشکی قم رابطه معناداری وجود دارد (سبکهای دلبستگی پیشبینیکننده معنادار همدلی است)."),
        ("سبک های دلبستگی بر تنظیم هیجان در دانشجویان پزشکی دانشگاه علوم پزشکی قم تاثیر دارد.", "بین سبکهای دلبستگی و تنظیم هیجان در دانشجویان پزشکی دانشگاه علوم پزشکی قم رابطه معناداری وجود دارد (سبکهای دلبستگی پیشبینیکننده معنادار تنظیم هیجان است)."),
        ("سبک های دلبستگی بر خود شفقتی در دانشجویان پزشکی دانشگاه علوم پزشکی قم تاثیر دارد.", "بین سبکهای دلبستگی و خودشفقتی در دانشجویان پزشکی دانشگاه علوم پزشکی قم رابطه معناداری وجود دارد (سبکهای دلبستگی پیشبینیکننده معنادار خودشفقتی است)."),
        ("تنظیم هیجان بر همدلی در دانشجویان پزشکی دانشگاه علوم پزشکی قم تاثیر دارد.", "بین تنظیم هیجان و همدلی در دانشجویان پزشکی دانشگاه علوم پزشکی قم رابطه معناداری وجود دارد (تنظیم هیجان پیشبینیکننده معنادار همدلی است)."),
        ("خود شفقتی بر همدلی در دانشجویان پزشکی دانشگاه علوم پزشکی قم تاثیر دارد.", "بین خودشفقتی و همدلی در دانشجویان پزشکی دانشگاه علوم پزشکی قم رابطه معناداری وجود دارد (خودشفقتی پیشبینیکننده معنادار همدلی است)."),
        ("و تاثیر آن بر همدلی", "و نقش آن در ارتقای همدلی")
    ]
    
    for search_text, replace_text in searches:
        if search_text in xml_content:
            if track:
                pattern = re.compile(rf'(<w:r(?: [^>]*)?>)((?:(?!<w:r(?: [^>]*)?>).)*?{re.escape(search_text)}.*?</w:r>)', re.DOTALL)
                def repl_func(match):
                    r_start = match.group(1)
                    r_inner = match.group(2)
                    r_inner = r_inner.replace(search_text, replace_text)
                    if '<w:rPr>' in r_inner:
                        r_inner = r_inner.replace('<w:rPr>', '<w:rPr><w:highlight w:val="yellow"/>')
                    else:
                        r_start += '<w:rPr><w:highlight w:val="yellow"/></w:rPr>'
                    return r_start + r_inner
                xml_content, subs_made = pattern.subn(repl_func, xml_content)
                if subs_made == 0:
                    xml_content = xml_content.replace(search_text, replace_text)
            else:
                xml_content = xml_content.replace(search_text, replace_text)
                
            replacements_count += 1
            
    assert replacements_count == 6, f"Expected 6 replacements, got {replacements_count}"
    assert xml_content != original_xml, "XML was not modified"
    
    with open(doc_path, 'w', encoding='utf-8') as f:
        f.write(xml_content)
        
    shutil.make_archive(extract_dir, 'zip', extract_dir)
    shutil.move(extract_dir + '.zip', output_docx)
    shutil.rmtree(extract_dir)

if __name__ == '__main__':
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    track = '--track' in sys.argv
    process_docx(input_file, output_file, track)
