"""Whole-report consistency checks on final_report/chapters and final_report/tables.

1. Table 12.1 / 10.1 cells: numbers in each rewritten cell must equal the numbers of the original
   cell (none added, none dropped); Yes/No of the cross-generator column unchanged; name-like tokens
   of the original cell (capitalised or containing digits) still present.
2. Cross-references: every 'Section N.M', 'Chapter N', 'Table N.M', 'Figure N.M', 'Equation (N.M)'
   points at something that exists.
3. Wording that would break the Semester 7 rules (own-results claims; implementation track outside
   Section 14.3).
Exit code 1 if anything is reported.
"""
import json, re, sys
from pathlib import Path

FR = Path(__file__).resolve().parents[1]
SRC = FR / 'build' / 'sources'
NUM = re.compile(r'\d+(?:[.,]\d+)*')
problems = []


def nums(s):
    return sorted(n.replace(',', '') for n in NUM.findall(re.sub(r'C\d{2}', ' ', s)))


def names(s):
    return {t for t in re.findall(r"[A-Za-z0-9][\w+./-]*", s) if (any(c.isdigit() for c in t) or t[:1].isupper()) and len(t) > 1}


# ---- 1. tables
t12 = json.loads((FR / 'tables' / 't12_1.json').read_text(encoding='utf-8'))
orig12 = {r['cid']: r for r in json.loads((SRC / 't12_1_original.json').read_text(encoding='utf-8'))}
if sorted(r['cid'] for r in t12['rows']) != sorted(orig12) or len(t12['rows']) != len(orig12):
    problems.append('Table 12.1: row set differs from the original 48 studies')
for r in t12['rows']:
    o = orig12[r['cid']]
    for col in ('approach', 'model', 'dataset', 'generators', 'result', 'crossgen', 'limitation'):
        if nums(r[col]) != nums(o[col]):
            problems.append(f"T12 {r['cid']} {col}: numbers {nums(r[col])} vs original {nums(o[col])}")
        lost = {n for n in names(o[col]) - names(r[col]) if n.lower() not in r[col].lower()
                and not all(p.lower() in r[col].lower() for p in re.split(r'-trained|-|x(?=\d)', n) if len(p) > 1)}
        lost -= {'Yes', 'No', 'The', 'A', 'An', 'Only', 'All', 'Both', 'Not', 'For', 'On', 'In', 'At', 'Also'}
        if lost and col not in ('approach', 'limitation'):
            problems.append(f"T12 {r['cid']} {col}: names not carried over: {sorted(lost)}")
    yes_new = r['crossgen'].strip().lower().startswith('yes')
    if yes_new != o['crossgen'].strip().lower().startswith('yes'):
        problems.append(f"T12 {r['cid']}: cross-generator Yes/No changed")
t10 = json.loads((FR / 'tables' / 't10_1.json').read_text(encoding='utf-8'))
orig10 = json.loads((SRC / 't10_1_original.json').read_text(encoding='utf-8'))
for r, o in zip(t10['rows'], orig10):
    for col in ('dataset', 'year', 'scale', 'real_source', 'generators', 'notes'):
        if nums(r[col]) != nums(o[col]):
            problems.append(f"T10 {o['dataset']} {col}: numbers {nums(r[col])} vs original {nums(o[col])}")

# ---- 2. cross-references
chap = sorted(p for p in (FR / 'chapters').glob('*.md'))
text = {p.name: p.read_text(encoding='utf-8') for p in chap}
heads, tabs, figs = set(), set(), set()
for t in text.values():
    heads |= set(re.findall(r'^## (\d+\.\d+) ', t, re.M))
    tabs |= set(re.findall(r'^Table:\s*([\dA-Z]+\.\d+)', t, re.M))
    figs |= set(re.findall(r'^\[\[FIGURE:\w+\|([\d.]+)\|', t, re.M))
tabs |= {'10.1', '12.1'}
chapters = {str(i) for i in range(1, 16)}
for name, t in text.items():
    body = re.sub(r'^(#|Table:|\[\[).*$', '', t, flags=re.M)
    for m in re.finditer(r'\bSections?\s+(\d+\.\d+)((?:\s*(?:,|and|to|–)\s*\d+\.\d+)*)', body):
        for ref in [m.group(1)] + re.findall(r'\d+\.\d+', m.group(2)):
            if ref not in heads:
                problems.append(f'{name}: Section {ref} does not exist')
    for m in re.finditer(r'\bChapters?\s+(\d+)((?:\s*(?:,|and|to|–)\s*\d+)*)', body):
        for ref in [m.group(1)] + re.findall(r'\d+', m.group(2)):
            if ref not in chapters:
                problems.append(f'{name}: Chapter {ref} does not exist')
    for m in re.finditer(r'\bTables?\s+((?:\d+|A)\.\d+)', body):
        if m.group(1) not in tabs:
            problems.append(f'{name}: Table {m.group(1)} does not exist')
    for m in re.finditer(r'\bFigures?\s+(\d+\.\d+)', body):
        if m.group(1) not in figs:
            problems.append(f'{name}: Figure {m.group(1)} does not exist')
    for m in re.finditer(r'Equations?\s*\((\d+\.\d+)\)', body):
        if not re.fullmatch(r'11\.[1-8]', m.group(1)):
            problems.append(f'{name}: Equation ({m.group(1)}) does not exist')

# ---- 3. rule wording
OWN = re.compile(r'\b(we|the team|our team|this project)\s+(trained|tested|measured|evaluated|ran|achieved|obtained|fine-tuned|benchmarked)\b'
                 r'|\bour (results|experiments?|model|accuracy|implementation)\b', re.I)
TRACK = re.compile(r'Kaggle|GPU hours|Tesla|T4|checkpoint|15 August 2026|implementation (code|track|work)|work track', re.I)
for name, t in text.items():
    for m in OWN.finditer(t):
        problems.append(f'{name}: possible own-results wording: "{t[max(0, m.start() - 60):m.end() + 40]}"')
    if not name.startswith('14_'):
        for m in TRACK.finditer(t):
            problems.append(f'{name}: implementation-track wording outside Section 14.3: "{t[max(0, m.start() - 60):m.end() + 40]}"')
t14 = text.get('14_conclusion.md', '')
if len(TRACK.findall(t14)) > 3:
    problems.append('14_conclusion.md: implementation track mentioned more than once?')

print('\n'.join(problems) if problems else 'no problems found')
sys.exit(1 if problems else 0)
