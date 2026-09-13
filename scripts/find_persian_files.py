import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8')

# Match any filename containing Persian characters followed by an extension
pattern = re.compile(r'[\u0600-\u06FF][^"\'\n\r]*\.(?:docx|xlsx|pptx|pdf|html|png|csv|json|txt|md|sav)')

matches = []
for root, dirs, files in os.walk('.'):
    if any(skip in root for skip in ['.git', '.venv', '__pycache__', 'node_modules']):
        continue
    for f in files:
        if f.endswith('.py'):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                for idx, line in enumerate(file, 1):
                    found = pattern.findall(line)
                    if found:
                        matches.append((path, idx, found, line.strip()))

print(f"Total occurrences found: {len(matches)}")
for p, idx, f, l in matches:
    print(f"{p}:{idx}: {f} -> {l}")
