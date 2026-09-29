import os
import zipfile
import re

def edit_docx(input_path, output_clean_path, output_tracked_path):
    # 1. Read all entries from zip
    with zipfile.ZipFile(input_path, 'r') as zf:
        entries = {name: zf.read(name) for name in zf.namelist()}
        
    xml_str = entries['word/document.xml'].decode('utf-8')
    
    # 2. Reconstruct the hypotheses and C3 in xml string
    
    # Text replacements. OpenXML spreads text across multiple <w:t> tags often, but for simple docs it might be in one.
    # To handle cross-run splits, the previous ElementTree approach or Regex is tricky, but let's assume standard output where sentences are usually in a few blocks.
    # Actually, if we just remove the xml tags to find matches, it's hard to put them back.
    # Let's use simple string replacements on the xml content if it's contiguous, otherwise we'll use a regex that ignores tags.
    
    # A simple regex that matches the old text even if there are <w:whatever> tags in between characters!
    def make_xml_regex(text):
        # Allow any XML tags (like </w:t><w:r><w:t>) between characters
        pattern = r'(?:<[^>]+>)*'.join(re.escape(c) for c in text)
        return re.compile(pattern)
        
    def replace_xml_text(xml_content, old_text, new_text, track=False):
        pattern = make_xml_regex(old_text)
        
        def replacer(match):
            matched_str = match.group(0)
            # We want to replace the text but keep the tags? 
            # Actually, the easiest is to just wipe the matched string and replace it with:
            # new_text. But what if it contains formatting tags like <w:b/>?
            # A safer way is to just put new_text inside a single <w:t> new_text </w:t> and maybe lose inner formatting,
            # but since it's just plain text being replaced, it's fine.
            # Wait, if we replace `matched_str` with new_text, we might delete paragraph tags if they were somehow in between? No, `text` won't span paragraphs.
            
            # Let's extract all XML tags from the matched string to preserve them
            tags = "".join(re.findall(r'<[^>]+>', matched_str))
            
            if track:
                # Add yellow highlight formatting
                # This requires finding the enclosing <w:rPr> or inserting one.
                # A quick hack: just use a <w:r><w:rPr><w:highlight w:val="yellow"/></w:rPr><w:t>new_text</w:t></w:r>
                return f'{tags}<w:r><w:rPr><w:highlight w:val="yellow"/></w:rPr><w:t>{new_text}</w:t></w:r>'
            else:
                return f'{tags}<w:r><w:t>{new_text}</w:t></w:r>'
                
        return pattern.sub(replacer, xml_content)

    clean_xml = xml_str
    tracked_xml = xml_str
    
    # C3
    old_c3_1 = "و تاثیر آن بر همدلی"
    old_c3_2 = "و تأثیر آن بر همدلی"
    new_c3 = "و نقش آن در ارتقای همدلی"
    
    clean_xml = replace_xml_text(clean_xml, old_c3_1, new_c3, False)
    clean_xml = replace_xml_text(clean_xml, old_c3_2, new_c3, False)
    
    tracked_xml = replace_xml_text(tracked_xml, old_c3_1, new_c3, True)
    tracked_xml = replace_xml_text(tracked_xml, old_c3_2, new_c3, True)
    
    # Hypotheses
    hypotheses = {
        "۱. بین سبک های دلبستگی و همدلی در دانشجویان پزشکی دانشگاه علوم پزشکی قم رابطه معنی داری وجود دارد.": "۱. بین سبکهای دلبستگی و همدلی در دانشجویان پزشکی دانشگاه علوم پزشکی قم رابطه معناداری وجود دارد (سبکهای دلبستگی پیشبینیکننده معنادار همدلی است).",
        "۲. بین سبک های دلبستگی و تنظیم هیجان در دانشجویان پزشکی دانشگاه علوم پزشکی قم رابطه معنی داری وجود دارد.": "۲. بین سبکهای دلبستگی و تنظیم هیجان در دانشجویان پزشکی دانشگاه علوم پزشکی قم رابطه معناداری وجود دارد (سبکهای دلبستگی پیشبینیکننده معنادار تنظیم هیجان است).",
        "۳. بین سبک های دلبستگی و خود شفقتی در دانشجویان پزشکی دانشگاه علوم پزشکی قم رابطه معنی داری وجود دارد.": "۳. بین سبکهای دلبستگی و خودشفقتی در دانشجویان پزشکی دانشگاه علوم پزشکی قم رابطه معناداری وجود دارد (سبکهای دلبستگی پیشبینیکننده معنادار خودشفقتی است).",
        "۴. بین تنظیم هیجان و همدلی در دانشجویان پزشکی دانشگاه علوم پزشکی قم رابطه معنی داری وجود دارد.": "۴. بین تنظیم هیجان و همدلی در دانشجویان پزشکی دانشگاه علوم پزشکی قم رابطه معناداری وجود دارد (تنظیم هیجان پیشبینیکننده معنادار همدلی است).",
        "۵. بین خود شفقتی و همدلی در دانشجویان پزشکی دانشگاه علوم پزشکی قم رابطه معنی داری وجود دارد.": "۵. بین خودشفقتی و همدلی در دانشجویان پزشکی دانشگاه علوم پزشکی قم رابطه معناداری وجود دارد (خودشفقتی پیشبینیکننده معنادار همدلی است)."
    }
    
    for old_h, new_h in hypotheses.items():
        # normalize spaces
        old_h_no_space = old_h.replace(" ", "")
        
        # A regex that matches the text ignoring spaces and xml tags
        pattern = r'(?:<[^>]+>|\s)*'.join(re.escape(c) for c in old_h_no_space)
        regex = re.compile(pattern)
        
        def replacer_clean(match):
            tags = "".join(re.findall(r'<[^>]+>', match.group(0)))
            return f'{tags}<w:r><w:t>{new_h}</w:t></w:r>'
            
        def replacer_track(match):
            tags = "".join(re.findall(r'<[^>]+>', match.group(0)))
            return f'{tags}<w:r><w:rPr><w:highlight w:val="yellow"/></w:rPr><w:t>{new_h}</w:t></w:r>'
            
        clean_xml = regex.sub(replacer_clean, clean_xml)
        tracked_xml = regex.sub(replacer_track, tracked_xml)
        
    entries_clean = entries.copy()
    entries_clean['word/document.xml'] = clean_xml.encode('utf-8')
    
    entries_tracked = entries.copy()
    entries_tracked['word/document.xml'] = tracked_xml.encode('utf-8')
    
    with zipfile.ZipFile(output_clean_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for name, data in entries_clean.items():
            zf.writestr(name, data)
            
    with zipfile.ZipFile(output_tracked_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for name, data in entries_tracked.items():
            zf.writestr(name, data)

if __name__ == "__main__":
    input_file = "/home/saber-ghaderi/My Work/Mehrane/01_raw_inputs/فایل پروپوزال.docx"
    output_c = "/home/saber-ghaderi/My Work/Mehrane/03_deliverables/Proposal_Revised_Clean.docx"
    output_t = "/home/saber-ghaderi/My Work/Mehrane/03_deliverables/Proposal_Revised_Tracked.docx"
    
    os.makedirs(os.path.dirname(output_c), exist_ok=True)
    edit_docx(input_file, output_c, output_t)
