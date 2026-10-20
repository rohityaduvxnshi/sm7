"""Compare a rewritten chapter (or table JSON) against its source files.

Reports, for the person or agent doing the rewrite:
  1. runs of >= N identical words shared with any source (wording to change),
  2. numbers in the new text that appear in no source (possible drift),
  3. citation keys in the new text that appear in no source,
  4. citation keys in the sources that the new text no longer cites (info only).

Usage:
  python chapter_check.py --new chapters/09_taxonomy.md --src ../sections/03_approaches.md [more ...] [--n 7]
"""
import argparse, re, sys
from pathlib import Path

PLACEHOLDER = re.compile(r'\[\[[^\]]*\]\]')
CITE = re.compile(r'\[(C\d{2}(?:\s*,\s*C\d{2})*)\]|\{(C\d{2})\}')
XREF = re.compile(r'\b(?:Chapters?|Sections?|Tables?|Figures?|Equations?|Eq\.|Appendix|Week|Weeks|WPR|WPRs)\s+'
                  r'\(?[\dA-Z][\d.]*\)?(?:\s*(?:–|-|to|and|,|&)\s*\(?\d[\d.]*\)?)*')
NUM = re.compile(r'\d+(?:[.,]\d+)*')


def read(p):
    return Path(p).read_text(encoding='utf-8')


def words(text):
    text = PLACEHOLDER.sub(' ', text)
    text = CITE.sub(' ', text)
    text = re.sub(r'[*_`#|>]', ' ', text)
    return re.findall(r"[a-z0-9]+(?:[-'][a-z0-9]+)*", text.lower())


def keys(text):
    out = set()
    for m in CITE.finditer(text):
        grp = m.group(1) or m.group(2)
        out.update(k.strip() for k in grp.split(','))
    return out


def numbers(text):
    text = PLACEHOLDER.sub(' ', text)
    text = CITE.sub(' ', text)
    text = re.sub(r'C\d{2}', ' ', text)
    text = XREF.sub(' ', text)
    return {n.replace(',', '') for n in NUM.findall(text)}


def shared_spans(new_words, src_words, n):
    grams = set()
    for sw in src_words:
        grams.update(tuple(sw[i:i + n]) for i in range(len(sw) - n + 1))
    hit = [False] * len(new_words)
    for i in range(len(new_words) - n + 1):
        if tuple(new_words[i:i + n]) in grams:
            for j in range(i, i + n):
                hit[j] = True
    spans, i = [], 0
    while i < len(new_words):
        if hit[i]:
            j = i
            while j < len(new_words) and hit[j]:
                j += 1
            spans.append(' '.join(new_words[i:j]))
            i = j
        else:
            i += 1
    return spans, sum(hit)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--new', required=True)
    ap.add_argument('--src', nargs='+', required=True)
    ap.add_argument('--n', type=int, default=7)
    a = ap.parse_args()
    new = read(a.new)
    srcs = [read(s) for s in a.src]
    nw = words(new)
    spans, covered = shared_spans(nw, [words(s) for s in srcs], a.n)
    print(f'new text: {len(nw)} words; {covered} words ({100 * covered / max(1, len(nw)):.1f}%) '
          f'inside runs of >= {a.n} words shared with the sources')
    for s in spans:
        print(f'  SHARED ({len(s.split())} words): {s}')
    src_nums = set().union(*(numbers(s) for s in srcs))
    extra = sorted(numbers(new) - src_nums, key=lambda x: (len(x), x))
    print('numbers not found in any source:', extra if extra else 'none')
    src_keys = set().union(*(keys(s) for s in srcs))
    nk = keys(new)
    print('citation keys not in any source:', sorted(nk - src_keys) or 'none')
    print('source keys not cited in new text (info):', sorted(src_keys - nk) or 'none')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
