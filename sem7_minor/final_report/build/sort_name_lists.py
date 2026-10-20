"""Sort the generator-name lists inside the 'generators' cells of the two landscape tables
alphabetically (case-insensitive), segment by segment. Labels such as 'Train:', 'test:',
'8 test models:', '19, among them', 'e.g.' and a closing 'and' are kept in place; lists with fewer
than four items are left alone. The set of names in every cell is unchanged (asserted).
Run once after the table text is final: python sort_name_lists.py
"""
import json, re
from pathlib import Path

T = Path(__file__).resolve().parents[1] / 'tables'
PREFIX = re.compile(r'^(?P<p>.*?(?::\s+|\b(?:e\.g\.|among them|including|incl\.)\s+))(?P<rest>.+)$')


def split_items(s):
    out, depth, cur = [], 0, ''
    for ch in s:
        depth += ch == '('
        depth -= ch == ')'
        if ch == ',' and depth == 0:
            out.append(cur.strip()); cur = ''
        else:
            cur += ch
    out.append(cur.strip())
    return out


def sort_segment(seg):
    # leave prose and qualified lists alone: thousands separators, a qualifier that applies to the
    # whole list ('... each)'), or any item longer than four words
    if re.search(r'\d,\d', seg) or 'each' in seg:
        return seg
    m = PREFIX.match(seg)
    prefix, body = (m.group('p'), m.group('rest')) if m else ('', seg)
    items = split_items(body)
    last_and = False
    if len(items) > 1 and ' and ' in items[-1]:
        a, b = items[-1].rsplit(' and ', 1)
        items[-1:] = [a, b]
        last_and = True
    if len(items) < 4 or any(len(i.split()) > 4 for i in items):
        return seg
    items = sorted(items, key=str.lower)
    joined = ', '.join(items[:-1]) + (' and ' if last_and else ', ') + items[-1]
    return prefix + joined


def sort_cell(cell):
    return '; '.join(sort_segment(s.strip()) for s in cell.split(';'))


def names(cell):
    return sorted(t for t in re.split(r'[,;:]|\band\b|\be\.g\.|\bamong them\b', cell) if t.strip())


if __name__ == '__main__':
    changed = 0
    for fn in ('t12_1.json', 't10_1.json'):
        p = T / fn
        t = json.loads(p.read_text(encoding='utf-8'))
        for r in t['rows']:
            old = r['generators']
            new = sort_cell(old)
            assert sorted(x.strip() for x in names(old)) == sorted(x.strip() for x in names(new)), (old, new)
            if new != old:
                r['generators'] = new
                changed += 1
        p.write_text(json.dumps(t, ensure_ascii=False, indent=1), encoding='utf-8')
    print(f'generator cells re-ordered: {changed}')
