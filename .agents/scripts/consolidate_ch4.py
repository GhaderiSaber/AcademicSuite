import os
import re

files = [
    "01_demographics.md",
    "02_descriptives_and_reliability.md",
    "03_parametric_assumptions.md",
    "04_correlations.md",
    "05_macro_model.md",
    "06_hypothesis_1.md",
    "07_hypothesis_2.md",
    "08_hypothesis_3.md",
    "09_hypothesis_4.md",
    "10_hypothesis_5.md",
    "11_hypothesis_6.md",
    "12_hypothesis_7.md",
    "13_hypothesis_8.md",
    "14_master_decision_matrix.md"
]

base_dir = "/home/saber-ghaderi/My Work/Mohtasham Valiyanpur/03_deliverables"

intro = """# فصل چهارم: تجزیه و تحلیل داده‌ها و یافته‌های پژوهش

## مقدمه فصل چهارم
در این فصل، یافته‌های به‌دست‌آمده از تحلیل داده‌های پژوهش ارائه می‌گردد. ابتدا ویژگی‌های جمعیت‌شناختی و بالینی شرکت‌کنندگان و توصیف آماری متغیرها بررسی می‌شود. سپس پیش‌فرض‌های پارامتریک و ماتریس همبستگی ارزیابی می‌گردد. در ادامه، مدل‌یابی معادلات ساختاری کلان ارائه شده و در نهایت، هشت فرضیه پژوهش به‌صورت مجزا آزمون و در ماتریس جامع تصمیم‌گیری خلاصه می‌شوند.

"""

outro = """## 4.9 خلاصه و جمع‌بندی فصل چهارم
در این فصل، داده‌های حاصل از پژوهش با استفاده از روش‌های آمار توصیفی و استنباطی (مدل‌یابی معادلات ساختاری و آزمون‌های همبستگی و میانجی‌گری) تجزیه و تحلیل شدند. نتایج نشان داد که مدل ساختاری پژوهش از برازش مطلوبی برخوردار است و روابط مستقیم و غیرمستقیم متغیرها بر اساس فرضیه‌های تدوین‌شده تأیید گردید. این یافته‌ها، بستر لازم را برای بحث و نتیجه‌گیری در فصل پنجم فراهم می‌آورد.
"""

content = intro

for fname in files:
    path = os.path.join(base_dir, fname)
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            content += f.read() + "\n\n"
    else:
        print(f"Missing {fname}")

content += outro

lines = content.split('\n')
new_lines = []
for line in lines:
    if line.strip().startswith('|'):
        # inside a table cell
        line = re.sub(r'[pP]\s*=\s*', '', line)
        line = re.sub(r'<\s*[pP]', '<', line)
        line = re.sub(r'>\s*[pP]', '>', line)
        line = re.sub(r'[pP]\s*<', '<', line)
        line = re.sub(r'[pP]\s*>', '>', line)
    new_lines.append(line)

content = '\n'.join(new_lines)

out_md = os.path.join(base_dir, "Chapter_4_Results.md")
with open(out_md, "w", encoding="utf-8") as f:
    f.write(content)

print(f"Successfully wrote {out_md}")
