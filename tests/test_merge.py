import re

files = [
    '03_deliverables/stage_01_demographics/01_demographics.md',
    '03_deliverables/stage_02_descriptives_reliability/02_descriptives_reliability.md',
    '03_deliverables/stage_03_q1_suicidal_ideation/03_q1_suicidal_ideation.md',
    '03_deliverables/stage_04_q2_self_harm/04_q2_self_harm.md',
    '03_deliverables/stage_05_correlations_assumptions/05_correlations_assumptions.md',
    '03_deliverables/stage_06_hypothesis_1_depression/06_hypothesis_1_depression.md',
    '03_deliverables/stage_07_hypothesis_2_anxiety/07_hypothesis_2_anxiety.md',
    '03_deliverables/stage_08_hypothesis_3_bici/08_hypothesis_3_bici.md',
    '03_deliverables/stage_09_multivariate_synthesis/09_multivariate_synthesis.md'
]

for file in files:
    with open('/home/ghaderi-saber/My Work/Narjes/' + file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    first_h2_idx = -1
    for i, line in enumerate(lines):
        if line.startswith('## '):
            first_h2_idx = i
            break
            
    print(f"{file} -> first H2 at line {first_h2_idx}")
    if first_h2_idx != -1:
        print(f"H2 text: {lines[first_h2_idx].strip()}")
