"""Similarity pre-check: what share of the report's words sit inside runs of >= N words that also
occur in a comparison corpus (cited papers' abstracts and full texts, Wikipedia, earlier drafts,
another group's report). A proxy for Turnitin's similarity index, not a replacement: Turnitin
matches against a far larger corpus and tolerates small edits inside a run.

Usage: python -I plag_check.py <report.pdf> <corpus_dir> [--n 8] [--top 40] [--spans-out file.tsv]
"""
import argparse, collections, os, re, subprocess, sys

WORD = re.compile(r"[a-z0-9]+(?:['’-][a-z0-9]+)*")


def tokens(text):
    return WORD.findall(text.lower().replace('ﬁ', 'fi').replace('ﬂ', 'fl'))


def pdf_text(path):
    return subprocess.run(['pdftotext', '-q', '-enc', 'UTF-8', path, '-'], capture_output=True).stdout.decode('utf-8', 'replace')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('report'); ap.add_argument('corpus')
    ap.add_argument('--n', type=int, default=8); ap.add_argument('--top', type=int, default=40)
    ap.add_argument('--spans-out')
    ap.add_argument('--exclude', nargs='*', default=[], help='corpus groups to leave out, e.g. own')
    a = ap.parse_args()
    text = pdf_text(a.report)
    # split off the reference list (between the last 'REFERENCES' heading and 'APPENDIX')
    m = list(re.finditer(r'\n\s*REFERENCES\s*\n', text, re.I))
    body, refs = text, ''
    if m:
        start = m[-1].start()
        app = re.search(r'\n\s*APPENDIX A', text[start:])
        end = start + app.start() if app else len(text)
        body, refs = text[:start] + text[end:], text[start:end]
    rep = tokens(body)
    ref = tokens(refs)
    n = a.n
    # corpus n-gram index: gram -> set(source)
    index = collections.defaultdict(set)
    sources = []
    for group in sorted(os.listdir(a.corpus)):
        gdir = os.path.join(a.corpus, group)
        if not os.path.isdir(gdir) or group in a.exclude:
            continue
        for f in sorted(os.listdir(gdir)):
            if not f.endswith('.txt'):
                continue
            name = f'{group}/{f[:-4]}'
            sources.append(name)
            t = tokens(open(os.path.join(gdir, f), encoding='utf-8', errors='replace').read())
            for i in range(len(t) - n + 1):
                index[tuple(t[i:i + n])].add(name)

    def scan(tok):
        hit = [set() for _ in tok]
        for i in range(len(tok) - n + 1):
            s = index.get(tuple(tok[i:i + n]))
            if s:
                for j in range(i, i + n):
                    hit[j] |= s
        return hit

    hb = scan(rep)
    covered = sum(1 for h in hb if h)
    per_src = collections.Counter()
    per_group = collections.Counter()
    for h in hb:
        for s in h:
            per_src[s] += 1
        for g in {s.split('/')[0] for s in h}:
            per_group[g] += 1
    print(f'report body: {len(rep)} words; inside shared runs of >= {n} words: {covered} ({100 * covered / max(1, len(rep)):.2f}%)')
    for g, c in per_group.most_common():
        print(f'  group {g:10s} {c:6d} words ({100 * c / len(rep):.2f}%)')
    print('top sources:')
    for s, c in per_src.most_common(a.top):
        print(f'  {100 * c / len(rep):5.2f}%  {c:5d}  {s}')
    hr = scan(ref)
    rc = sum(1 for h in hr if h)
    print(f'reference list: {len(ref)} words, {rc} inside shared runs ({100 * rc / max(1, len(ref)):.1f}% of the list; '
          f'{100 * (covered + rc) / max(1, len(rep) + len(ref)):.2f}% of body+references combined)')
    # spans
    spans, i = [], 0
    while i < len(rep):
        if hb[i]:
            j, srcs = i, set()
            while j < len(rep) and hb[j]:
                srcs |= hb[j]; j += 1
            spans.append((j - i, ' '.join(rep[i:j]), sorted(srcs)))
            i = j
        else:
            i += 1
    spans.sort(key=lambda s: -s[0])
    print(f'{len(spans)} shared spans in the body; longest first:')
    for L, s, src in spans[:a.top]:
        print(f'  [{L}] {s[:220]}  <- {", ".join(src[:3])}{" ..." if len(src) > 3 else ""}')
    if a.spans_out:
        with open(a.spans_out, 'w', encoding='utf-8') as f:
            for L, s, src in spans:
                f.write(f'{L}\t{s}\t{"; ".join(src)}\n')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main()
