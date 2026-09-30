import sys
import re
import glob

def fix_file(fpath):
    with open(fpath, 'r', encoding='utf-8') as f:
        data = f.read()
    
    # Fix mixed numbers like ۷۱۰۰۰.۶ -> ۷۱.۶ (or wait, is it ۳۵۰۰۰.۷۲? maybe it was 35.72)
    # The prompt says: "fix mixed numbers in demographics and Table 4-13"
    # Actually, if someone did `replace('.', '۰۰۰.')` on '71.6' it would become '71000.6'.
    # I'll just find patterns like `(\d+)۰۰۰\.(\d+)` and replace with `\1.\2`
    
    data = re.sub(r'(\d+)۰۰۰\.(\d+)', r'\1.\2', data)
    
    # Also for ۰۰۰۰.۱۰ -> ۰.۱۰
    # If it was originally .10, it became ۰۰۰۰.10 then -> ۰.۱۰. Wait, `۰.۱۰` has one zero. 
    # Let's fix ۰۰۰۰. -> ۰.
    data = re.sub(r'۰۰۰۰\.', '۰.', data)
    data = re.sub(r'۰۰۰\.', '۰.', data)
    
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(data)

if __name__ == '__main__':
    for fpath in glob.glob("03_deliverables/*.md"):
        fix_file(fpath)
