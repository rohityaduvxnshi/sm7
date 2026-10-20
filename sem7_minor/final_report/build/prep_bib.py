"""references/references.bib -> build/bib.json (detexed fields, authors split into surname + initials).

Parser and name handling are carried over unchanged from submission/build/build_v2.py,
which built draft v2's author-year reference list from the same file.
"""
import json, re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]          # sem7_minor
BIB = ROOT / 'references' / 'references.bib'
OUT = Path(__file__).with_name('bib.json')


def detex(s):
    reps = [(r'\{\\"([aouAOUe])\}', {'a': 'ä', 'o': 'ö', 'u': 'ü', 'A': 'Ä', 'O': 'Ö', 'U': 'Ü', 'e': 'ë'}),
            (r"\{\\'([aeiouAEIOU])\}", {'a': 'á', 'e': 'é', 'i': 'í', 'o': 'ó', 'u': 'ú', 'A': 'Á', 'E': 'É', 'I': 'Í', 'O': 'Ó', 'U': 'Ú'}),
            (r'\{\\`([aeiouAEIOU])\}', {'a': 'à', 'e': 'è', 'i': 'ì', 'o': 'ò', 'u': 'ù', 'A': 'À', 'E': 'È', 'I': 'Ì', 'O': 'Ò', 'U': 'Ù'})]
    for pat, table in reps:
        s = re.sub(pat, lambda m: table[m.group(1)], s)
    s = s.replace(r'{\ss}', 'ß').replace(r'\&', '&').replace('$^2$', '²')
    return s.replace('{', '').replace('}', '')


def parse_bib(path):
    txt = path.read_text(encoding='utf-8')
    entries = {}
    for m in re.finditer(r'@(\w+)\s*\{\s*(C\d+)\s*,', txt):
        etype, key = m.group(1).lower(), m.group(2)
        i, depth = m.end(), 1
        while depth:
            if txt[i] == '{': depth += 1
            elif txt[i] == '}': depth -= 1
            i += 1
        body = txt[m.end():i - 1]
        fields, j = {}, 0
        while True:
            fm = re.compile(r'(\w+)\s*=\s*').search(body, j)
            if not fm: break
            k = fm.end()
            if body[k] == '{':
                d, s = 1, k + 1
                k += 1
                while d:
                    if body[k] == '{': d += 1
                    elif body[k] == '}': d -= 1
                    k += 1
                val = body[s:k - 1]
            else:
                e = body.find(',', k)
                e = len(body) if e < 0 else e
                val, k = body[k:e].strip(), e
            fields[fm.group(1).lower()] = detex(val.strip())
            j = k
        fields['_type'] = etype
        entries[key] = fields
    return entries


PARTICLES = {'van', 'der', 'von', 'de', 'del', 'di', 'da', 'la', 'den'}


def split_name(full):
    toks = full.split()
    surname = [toks[-1]]
    i = len(toks) - 2
    while i >= 0 and toks[i].lower() in PARTICLES:
        surname.insert(0, toks[i]); i -= 1
    inits = []
    for g in toks[:i + 1]:
        inits.append('-'.join(p[0] + '.' for p in g.split('-') if p))
    return ' '.join(surname), ' '.join(inits)


bib = parse_bib(BIB)
for key, e in bib.items():
    e['authors'] = [list(split_name(a.strip())) for a in e['author'].split(' and ')]
OUT.write_text(json.dumps(bib, ensure_ascii=False, indent=1), encoding='utf-8')
print(f'{len(bib)} entries -> {OUT}')
