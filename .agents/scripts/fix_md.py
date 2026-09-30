import re

def fix_markdown(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Normalize Arabic characters and digits
    ARABIC_TO_PERSIAN = {
        'ك': 'ک', 'ي': 'ی', 'ة': 'ه', 'ى': 'ی',
        '٠': '۰', '١': '۱', '٢': '۲', '٣': '۳', '٤': '۴', '٥': '۵', '٦': '۶', '٧': '۷', '٨': '۸', '٩': '۹'
    }
    for a, p in ARABIC_TO_PERSIAN.items():
        content = content.replace(a, p)

    # 2. Eliminate raw inline Latin acronyms
    acronyms = {
        '(Suicidal Ideation)': '(افکار خودکشی)',
        '(IUS-12)': '(تحمل‌ناپذیری عدم‌قطعیت-۱۲)',
        '(SCI-16)': '(کنترل ادراک‌شده-۱۶)',
        '(RRS-22)': '(نشخوار فکری-۲۲)',
        '(PANAS-NA)': '(عاطفه منفی)',
        '(Negative Affect)': '(عاطفه منفی)',
        '(Rumination)': '(نشخوار فکری)',
        'IUS-FA': 'اضطراب آینده‌نگر',
        'IUS-RA': 'اضطراب بازدارنده',
        'IUS-T': 'نمره کل تحمل‌ناپذیری عدم‌قطعیت',
        'SCI-T': 'کنترل ادراک‌شده',
        'Ru-Ref': 'بازتابشگری',
        'Ru-Bro': 'غرولند',
        'Ru-Dep': 'نشخوار افسرده‌وار',
        'RRS-T': 'نمره کل نشخوار فکری',
        'PA-Negative': 'عاطفه منفی',
        'BSSI-T': 'نمره کل افکار خودکشی',
        'BSSI': 'افکار خودکشی',
        'SCI': 'کنترل ادراک‌شده'
    }
    for k, v in acronyms.items():
        content = content.replace(k, v)

    # 3. Eliminate generative AI cliché
    content = content.replace('در این راستا', 'در همین ارتباط')

    # 4. Standardize numbers (remove the weird 00000 insertion)
    content = content.replace('۰۰۰۰۰', '')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

fix_markdown('03_deliverables/Chapter_4_Results.md')
print("Fixed Markdown!")
