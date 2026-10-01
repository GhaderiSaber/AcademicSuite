with open('02_analysis_code/compile_gold_standard_chapter4.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()
for i, line in enumerate(lines):
    if 'post_process_openxml' in line:
        print(f"Line {i+1}: {line.strip()}")
