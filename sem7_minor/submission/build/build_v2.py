# Build manuscript_v2.html from manuscript.html (v1).
# Content is unchanged except: numeric -> author-year citations, figure/table
# renumbering, one "(Fig. 1)" parenthetical, caption cleanups.
import csv, re, sys, io, html, unicodedata
from pathlib import Path

ROOT = Path(r"C:\Users\rohit\Desktop\AuthentiScan\sem7_minor")
V1 = ROOT / "submission" / "manuscript.html"
OUT = ROOT / "submission" / "manuscript_v2.html"

# ---------------------------------------------------------------- bib parsing
def detex(s):
    reps = [(r'\{\\"([aouAOUe])\}', {'a':'ä','o':'ö','u':'ü','A':'Ä','O':'Ö','U':'Ü','e':'ë'}),
            (r"\{\\'([aeiouAEIOU])\}", {'a':'á','e':'é','i':'í','o':'ó','u':'ú','A':'Á','E':'É','I':'Í','O':'Ó','U':'Ú'}),
            (r'\{\\`([aeiouAEIOU])\}', {'a':'à','e':'è','i':'ì','o':'ò','u':'ù','A':'À','E':'È','I':'Ì','O':'Ò','U':'Ù'})]
    for pat, table in reps:
        s = re.sub(pat, lambda m: table[m.group(1)], s)
    s = s.replace(r'{\ss}', 'ß').replace(r'\&', '&').replace('$^2$', '\u00b2')
    s = s.replace('{', '').replace('}', '')
    return s

def parse_bib(path):
    txt = path.read_text(encoding='utf-8')
    entries = {}
    for m in re.finditer(r'@(\w+)\s*\{\s*(C\d+)\s*,', txt):
        etype, key = m.group(1).lower(), m.group(2)
        i = m.end()
        depth = 1
        while depth:
            if txt[i] == '{': depth += 1
            elif txt[i] == '}': depth -= 1
            i += 1
        body = txt[m.end():i-1]
        fields = {}
        j = 0
        while True:
            fm = re.compile(r'(\w+)\s*=\s*').search(body, j)
            if not fm: break
            k = fm.end()
            if body[k] == '{':
                d, s = 1, k+1
                k += 1
                while d:
                    if body[k] == '{': d += 1
                    elif body[k] == '}': d -= 1
                    k += 1
                val = body[s:k-1]
            else:
                e = body.find(',', k)
                e = len(body) if e < 0 else e
                val = body[k:e].strip()
                k = e
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
    given = toks[:i+1]
    inits = []
    for g in given:
        parts = g.split('-')
        inits.append('-'.join(p[0] + '.' for p in parts if p))
    return ' '.join(surname), ''.join(inits)

def authors_of(e):
    return [split_name(a.strip()) for a in e['author'].split(' and ')]

# ---------------------------------------------------------------- label build
bib = parse_bib(ROOT / "references" / "references.bib")
num2cid = {}
with open(ROOT / "submission" / "citation_map.csv", newline='', encoding='utf-8') as f:
    for row in csv.DictReader(f):
        num2cid[int(row['number'])] = row['cid']

v1 = V1.read_text(encoding='utf-8')

# first-appearance order check
first_pos = {}
for m in re.finditer(r'\[(\d+(?:\s*,\s*\d+)*)\]', v1):
    for n in [int(x) for x in m.group(1).split(',')]:
        first_pos.setdefault(n, m.start())
order = [n for n, _ in sorted(first_pos.items(), key=lambda kv: kv[1])]
mono = order == sorted(order)
print("citation numbers appear in first-appearance order:", mono)
missing = sorted(set(num2cid) - set(first_pos))
print("numbers never cited in text:", missing)

# collisions
key_of = {}
for n, cid in num2cid.items():
    e = bib[cid]
    sur = authors_of(e)[0][0]
    key_of[cid] = (sur, e['year'])
groups = {}
for n in sorted(num2cid):
    groups.setdefault(key_of[num2cid[n]], []).append(num2cid[n])
suffix = {}
collisions = []
for k, cids in groups.items():
    if len(cids) > 1:
        collisions.append((k, cids))
        for i, cid in enumerate(cids):
            suffix[cid] = chr(ord('a') + i)
print("COLLISIONS:")
for (sur, yr), cids in collisions:
    print("   %s %s -> %s" % (sur, yr, ', '.join('%s=%s%s' % (c, yr, suffix[c]) for c in cids)))

def year_of(cid):
    return bib[cid]['year'] + suffix.get(cid, '')

def label(cid):
    a = authors_of(bib[cid])
    if len(a) == 1: name = a[0][0]
    elif len(a) == 2: name = '%s and %s' % (a[0][0], a[1][0])
    else: name = '%s et al.' % a[0][0]
    return '%s, %s' % (name, year_of(cid))

LBL = {cid: label(cid) for cid in num2cid.values()}

# ---------------------------------------------------------------- prose edits
def P(old, new):
    return (old, new)

PAIRS = [
 # 3.1
 P("Durall et al. reduced", "Durall et al. (2019) reduced"),
 P("assembled Faces-HQ set from as few as 20 labelled samples [29]. A follow-up",
   "assembled Faces-HQ set from as few as 20 labelled samples. A follow-up"),
 P("Frank et al. moved the analysis", "Frank et al. (2020) moved the analysis"),
 P("rather than by holding one out of training [22].", "rather than by holding one out of training."),
 P("Dzanic et al. fitted", "Dzanic et al. (2020) fitted"),
 P("reaching 99.2% on uncompressed 1024\u00d71024 images [28].", "reaching 99.2% on uncompressed 1024\u00d71024 images."),
 P("Chandrasegaran et al. retrained generators", "Chandrasegaran et al. (2021) retrained generators"),
 P("not from CNN-generated images as such [16].", "not from CNN-generated images as such."),
 P("Zhang et al. had met a version of this", "Zhang et al. (2019) had met a version of this"),
 P("yet failed on GauGAN, which uses a different upsampler [9].", "yet failed on GauGAN, which uses a different upsampler."),
 P("Nataraj et al. passed pixel", "Nataraj et al. (2019) passed pixel"),
 P("but only two families were covered [35].", "but only two families were covered."),
 P("Marra et al. averaged denoising residuals over images from one source",
   "Marra et al. (2019) averaged denoising residuals over images from one source"),
 P("90.3% accuracy uncompressed and 90.1% after JPEG at quality 95 [25];",
   "90.3% accuracy uncompressed and 90.1% after JPEG at quality 95;"),
 P("Yu et al. learned the fingerprint instead", "Yu et al. (2019) learned the fingerprint instead"),
 P("against 86.61% for a PRNU-style baseline [24].", "against 86.61% for a PRNU-style baseline."),
 P("Corvi et al. compare artefacts across thirteen", "Corvi et al. (2023b) compare artefacts across thirteen"),
 P("warn that post-processing may modify and hide them [26];", "warn that post-processing may modify and hide them;"),
 # 3.2
 P("Wang et al. set the family's baseline", "Wang et al. (2020) set the family's baseline"),
 P("test sets, against 90.1 without it [12].", "test sets, against 90.1 without it."),
 P("Chai et al. restricted the receptive field", "Chai et al. (2020) restricted the receptive field"),
 P("hence its return in Section 3.5 [41].", "hence its return in Section 3.5."),
 P("Gragnaniello et al. benchmarked seven detectors", "Gragnaniello et al. (2021) benchmarked seven detectors"),
 P("yet they judged the field far from reliable tools [42].", "yet they judged the field far from reliable tools."),
 P("Cozzolino et al. added contrastive training", "Cozzolino et al. (2021) added contrastive training"),
 P("0.997 AUC over seven unseen GAN architectures [19].", "0.997 AUC over seven unseen GAN architectures."),
 P("Corvi et al. ran GAN-trained detectors", "Corvi et al. (2023a) ran GAN-trained detectors"),
 P("falling to about 50\u201361% under compression and resizing [14].", "falling to about 50\u201361% under compression and resizing."),
 P("Ricker et al. measured the same collapse", "Ricker et al. (2024a) measured the same collapse"),
 P("a GAN-trained detector 26.34% on diffusion images [13].", "a GAN-trained detector 26.34% on diffusion images."),
 # 3.3
 P("is by Coccomini et al., who trained a ViT-Base", "is by Coccomini et al. (2022), who trained a ViT-Base"),
 P("all fifteen manipulation methods in that dataset [54].", "all fifteen manipulation methods in that dataset."),
 P("Only Coccomini et al. hold the rest of the setup fixed [54].", "Only Coccomini et al. (2022) hold the rest of the setup fixed."),
 # 3.4
 P("Ojha et al. established the result [33].", "Ojha et al. (2023) established the result."),
 P("Cozzolino et al. take next-to-last-layer CLIP features", "Cozzolino et al. (2024b) take next-to-last-layer CLIP features"),
 P("6% AUC out of distribution and 13% on impaired images [59].", "6% AUC out of distribution and 13% on impaired images."),
 P("the prompt tuning that Khan and Dang-Nguyen compare against", "the prompt tuning that Khan and Dang-Nguyen (2024) compare against"),
 P("89.45% average accuracy over eighteen unseen generators [61].", "89.45% average accuracy over eighteen unseen generators."),
 # 3.5
 P("Bird and Lotfi trained a small custom CNN", "Bird and Lotfi (2024) trained a small custom CNN"),
 P("Stable Diffusion v1.4, reaching 92.98% accuracy [17].", "Stable Diffusion v1.4, reaching 92.98% accuracy."),
 P("Chai et al. reach localisation from the other direction [41].", "Chai et al. (2020) reach localisation from the other direction."),
 P("Aghasanli et al. take the interpretable-by-construction route", "Aghasanli et al. (2023) take the interpretable-by-construction route"),
 P("as prototypes a decision can be referred back to [56].", "as prototypes a decision can be referred back to."),
 P("Tsigos et al. propose an evaluation framework", "Tsigos et al. (2024) propose an evaluation framework"),
 P("the single segment each method ranks most important [71].", "the single segment each method ranks most important."),
 # 4.2
 P("released with the CNN detector of Wang et al. [12].", "released with the CNN detector of Wang et al. (2020)."),
 P("Ojha et al. extended the same design on the test side", "Ojha et al. (2023) extended the same design on the test side"),
 P("are now the standard suite for CLIP-feature detectors [33, 62, 63].",
   "are now the standard suite for CLIP-feature detectors (Tan et al., 2025; Yan et al., 2025b)."),
 # 4.3
 P("Grommelt et al. examined GenImage", "Grommelt et al. (2024) examined GenImage"),
 P("by reading those properties instead of any forensic trace [72].", "by reading those properties instead of any forensic trace."),
 P("and Aghasanli et al. state the reason plainly, that open datasets for their setting did not exist [56].",
   "and Aghasanli et al. (2023) state the reason plainly, that open datasets for their setting did not exist."),
 # 5.2
 P("Ricker et al. report Pd@1%FAR", "Ricker et al. (2024a) report Pd@1%FAR"),
 P("against 26.34% for the reverse direction [13].", "against 26.34% for the reverse direction."),
 P("the spectrum classifier of Zhang et al. averages 97.2% accuracy under leave-one-out testing yet fails on GauGAN [9],",
   "the spectrum classifier of Zhang et al. (2019) averages 97.2% accuracy under leave-one-out testing yet fails on GauGAN,"),
 # 6.2
 P("Gragnaniello et al. evaluated seven such detectors together and judged the field far from reliable tools [42].",
   "Gragnaniello et al. (2021) evaluated seven such detectors together and judged the field far from reliable tools."),
 P("Ojha et al. established the result with a nearest-neighbour rule", "Ojha et al. (2023) established the result with a nearest-neighbour rule"),
 P("accuracy on unseen diffusion and autoregressive models [33].", "accuracy on unseen diffusion and autoregressive models."),
 # 6.5
 P("Bird and Lotfi apply Grad-CAM", "Bird and Lotfi (2024) apply Grad-CAM"),
 P("finding the decision rests on background imperfections [17];", "finding the decision rests on background imperfections;"),
 P("Chai et al. obtain a map of which patches are detectable by restricting the receptive field [41];",
   "Chai et al. (2020) obtain a map of which patches are detectable by restricting the receptive field;"),
 P("Aghasanli et al. build interpretability in", "Aghasanli et al. (2023) build interpretability in"),
 P("fine-tuned ViT features as prototypes [56];", "fine-tuned ViT features as prototypes;"),
 P("and Tsigos et al. compare five explanation methods", "and Tsigos et al. (2024) compare five explanation methods"),
 P("a top-1 segment accuracy drop of 0.245 to 0.579 [71].", "a top-1 segment accuracy drop of 0.245 to 0.579."),
 P("only Chai et al. carries a cross-generator test [41];", "only Chai et al. (2020) carries a cross-generator test;"),
 # 6.6
 P("and Grommelt et al. run a ResNet50 and a Swin-T through the same bias-correction procedure [72].",
   "and Grommelt et al. (2024) run a ResNet50 and a Swin-T through the same bias-correction procedure."),
 P("Coccomini et al. come closest to isolating the architecture itself", "Coccomini et al. (2022) come closest to isolating the architecture itself"),
 P("against the ViT's roughly 62.0% [54].", "against the ViT's roughly 62.0%."),
 # 7.3
 P("Grommelt et al. found that real and generated images in GenImage", "Grommelt et al. (2024) found that real and generated images in GenImage"),
 P("by over eleven points for a ResNet50 and a Swin-T [72].", "by over eleven points for a ResNet50 and a Swin-T."),
 # 7.6
 P("Coccomini et al. vary the architecture on fixed training data [54],", "Coccomini et al. (2022) vary the architecture on fixed training data,"),
 # Table 1 "Introduced by" column
 P("<td>Wang et al. [12]</td>", "<td>Wang et al. (2020)</td>"),
 P("<td>Ojha et al. [33]</td>", "<td>Ojha et al. (2023)</td>"),
 P("<td>Wang et al. [47]</td>", "<td>Wang et al. (2023b)</td>"),
 P("<td>Zhu et al. [15]</td>", "<td>Zhu et al. (2023)</td>"),
 P("<td>Rahman et al. [18]</td>", "<td>Rahman et al. (2023)</td>"),
 P("<td>Chen et al. [5]</td>", "<td>Chen and Zou (2023)</td>"),
 P("<td>Bird &amp; Lotfi [17]</td>", "<td>Bird and Lotfi (2024)</td>"),
 P("<td>Baraldi et al. [57]</td>", "<td>Baraldi et al. (2024)</td>"),
 P("<td>Yan et al. [11]</td>", "<td>Yan et al. (2025a)</td>"),
 P("<td>Park &amp; Owens [53]</td>", "<td>Park and Owens (2025)</td>"),
 P("<td>Hong et al. [73]</td>", "<td>Hong et al. (2025)</td>"),
]

doc = v1
for old, new in PAIRS:
    c = doc.count(old)
    if c != 1:
        print("PROSE PAIR NOT UNIQUE (%d): %r" % (c, old[:70])); sys.exit(1)
    doc = doc.replace(old, new)

# ------------------------------------------------------- numeric -> authoryear
def cite_sub(m):
    nums = [int(x) for x in m.group(1).split(',')]
    return '(' + '; '.join(LBL[num2cid[n]] for n in nums) + ')'

doc, nsub = re.subn(r'\[(\d+(?:\s*,\s*\d+)*)\]', cite_sub, doc)
print("numeric citation groups converted:", nsub)

# ------------------------------------------------------------ figure / tables
doc = doc.replace("Figure 4.1 sets out the flow.", "Fig. 2 sets out the flow.")
doc = doc.replace("Figure 5.1 summarises the confusion matrix", "Fig. 3 summarises the confusion matrix")
doc = doc.replace("Table 4.1 summarises the datasets", "Table 1 summarises the datasets")
doc = doc.replace("the generator lists recorded in Table 4.1", "the generator lists recorded in Table 1")
for old, new in [("Table 6.1 lists all 48 primary studies", "Table 2 lists all 48 primary studies"),
                 ("the rightmost columns of Table 6.1 qualify", "the rightmost columns of Table 2 qualify"),
                 ("the other three are marked No in Table 6.1", "the other three are marked No in Table 2"),
                 ("No row in Table 6.1 therefore combines", "No row in Table 2 therefore combines"),
                 ("No row of Table 6.1 combines four things", "No row of Table 2 combines four things")]:
    assert doc.count(old) == 1, old
    doc = doc.replace(old, new)

# the one permitted in-text addition
old = "The surveyed work is grouped into five families:"
assert doc.count(old) == 1
doc = doc.replace(old, "The surveyed work is grouped into five families (Fig. 1):")

# ----------------------------------------------------------------- extraction
def between(start, end, s=None):
    s = s if s is not None else doc
    i = s.index(start) + len(start)
    j = s.index(end, i)
    return s[i:j]

abstract = between('<h1>Abstract</h1>\n<p>', '</p>').strip()
keywords = [k.strip() for k in
            between('<p><strong>Keywords:</strong>', '</p>').strip().split(';')]
body = doc[doc.index('<h1>Section 1 \u2014 Introduction</h1>'):doc.index('<h1>References</h1>')]

# headings
body = re.sub(r'<h1>Section (\d+) \u2014 ([^<]+)</h1>', lambda m: '<h1>%s. %s</h1>' % (m.group(1), m.group(2)), body)
body = re.sub(r'<h2>(\d+\.\d+) ([^<]+)</h2>', lambda m: '<h2>%s. %s</h2>' % (m.group(1), m.group(2)), body)

# figure blocks
prisma_old = between('<p class="fig"><img src="../figures/prisma_flow.png"', '</p>\n<h2>4.2', body)
body = body.replace('<p class="fig"><img src="../figures/prisma_flow.png"' + prisma_old + '</p>\n',
 '<figure class="fw fig"><img src="../figures/prisma_flow.png" alt="Fig. 2">\n'
 '<figcaption><strong>Fig. 2.</strong> Flow of records through the review, from database searches to the '
 'included set. Counts follow the screening record: 101 identified, 26 duplicates removed, 75 screened by '
 'title and abstract, 74 included (48 primary, 11 secondary, 15 background) and 1 excluded.</figcaption></figure>\n')

metrics_old = between('<p class="fig"><img src="../figures/metrics_overview.png"', '</p>\n<h2>5.2', body)
body = body.replace('<p class="fig"><img src="../figures/metrics_overview.png"' + metrics_old + '</p>\n',
 '<figure class="fw fig"><img src="../figures/metrics_overview.png" alt="Fig. 3">\n'
 '<figcaption><strong>Fig. 3.</strong> Confusion matrix for real-versus-generated classification and the '
 'metrics derived from it. The positive class is the AI-generated image. AUC and AP summarise performance '
 'over a sweep of decision thresholds rather than at a single operating point.</figcaption></figure>\n')

# taxonomy figure at the section 3 lead
lead_end = body.index('</p>', body.index('The surveyed work is grouped into five families (Fig. 1):')) + 4
taxfig = ('\n<figure class="fw fig"><img src="../figures/taxonomy_overview.png" alt="Fig. 1">\n'
 '<figcaption><strong>Fig. 1.</strong> Taxonomy of detection approaches surveyed in this review, organised '
 'by the origin of the detection signal.</figcaption></figure>')
body = body[:lead_end] + taxfig + body[lead_end:]

# equations: number to the right
body = re.sub(r'<p class="eq"><code>(.*?)</code>\s*\((\d)\)</p>',
              lambda m: '<p class="eq"><span class="eqn">(%s)</span><code>%s</code></p>' % (m.group(2), m.group(1)),
              body)

# ------------------------------------------------------------------ Table 1
cap1_old = between('<p class="caption">Table 4.1:', '</p>\n<table class="data">', body)
body = body.replace('<p class="caption">Table 4.1:' + cap1_old + '</p>\n<table class="data">',
 '<div class="fw"><p class="tabcap"><strong>Table 1</strong><br>Datasets and benchmarks on which the '
 'surveyed detection literature trains and tests, ordered by year of introduction. "\u2014" marks a property '
 'that the review\'s own extraction records do not state; it is not a claim that the dataset lacks that '
 'property.</p>\n<table class="data">')
body = body.replace('</tbody></table>\n<h2>4.3.', '</tbody></table></div>\n<h2>4.3.')

# ------------------------------------------------------------------ Table 2
cap2_old = between('<p class="caption">Table 6.1:', '</p>\n<table class="wide">', body)
body = body.replace('<p class="caption">Table 6.1:' + cap2_old + '</p>\n<table class="wide">',
 '<div class="fw"><p class="tabcap"><strong>Table 2</strong><br>Comparative summary of the 48 primary '
 'studies surveyed in this review, ordered by year of publication and then by screening ID. Each row '
 'compresses one record of the review\'s full-text extraction table; the <code>Cross-Generator Tested?</code> '
 'column records whether the study evaluated its detector on generators absent from its training data, and '
 '<code>Key Limitation</code> records the limitation the study\'s own authors state rather than one attributed '
 'by this review.</p>\n<table class="wide">')
body = body.replace('</tbody></table>\n<h2>6.1.', '</tbody></table></div>\n<h2>6.1.')

# drop C-ID column, apply suffixed study labels
tbl = between('<table class="wide">', '</table>', body)
new_tbl = tbl.replace('<thead><tr><th>C-ID</th>', '<thead><tr>')
rows = re.findall(r'<tr><td>(C\d+)</td><td>([^<]*)</td>(.*?)</tr>', new_tbl, re.S)
print("table 2 rows:", len(rows))
for cid, study, rest in rows:
    want = LBL[cid]
    if study.split()[0].rstrip(',') != want.split()[0].rstrip(','):
        print("  STUDY MISMATCH %s: %r vs %r" % (cid, study, want))
    old_row = '<tr><td>%s</td><td>%s</td>%s</tr>' % (cid, study, rest)
    new_row = '<tr><td>%s</td>%s</tr>' % (want, rest)
    new_tbl = new_tbl.replace(old_row, new_row)
    # word count of the Detection Approach cell (now the 2nd cell)
    approach = re.match(r'<td>([^<]*)</td>', rest.strip()).group(1)
    n = len(approach.split())
    if n > 20:
        print("  LONG APPROACH %s (%d words): %s" % (cid, n, approach))
body = body.replace(tbl, new_tbl)

# ------------------------------------------------------------- reference list
def fmt_ref(cid):
    e = bib[cid]
    auth = authors_of(e)
    names = ', '.join('%s, %s' % (s, i) if i else s for s, i in auth)
    title = e['title'].strip()
    if not title.endswith(('?', '!', '.')):
        title += '.'
    venue = e.get('journal') or e.get('booktitle') or e.get('howpublished', '')
    bits = []
    vol = e.get('volume')
    if vol:
        v = vol + (' (%s)' % e['number'] if e.get('number') else '')
        bits.append(v)
    if e.get('pages'):
        bits.append(e['pages'].replace('--', '\u2013'))
    tail = ''
    if e.get('doi'):
        tail = 'https://doi.org/' + e['doi']
    elif e.get('eprint'):
        tail = 'arXiv:' + e['eprint']
    elif e.get('url'):
        tail = e['url']
    venue_txt = venue
    if bits:
        venue_txt += ' ' + ', '.join(bits)
    out = '%s, %s. %s' % (names, year_of(cid), title)
    if venue_txt and not venue.startswith('arXiv preprint'):
        out += ' %s.' % venue_txt.rstrip('.')
    if tail:
        out += ' %s' % tail
    return html.escape(out, quote=False).replace('&amp;', '&')

cited = sorted(set(num2cid.values()), key=lambda c: (authors_of(bib[c])[0][0].lower(), year_of(c), bib[c]['title']))
refs = '\n'.join('<p class="ref">%s</p>' % fmt_ref(c) for c in cited)
print("reference entries:", len(cited))

# --------------------------------------------------------------------- shell
CSS = """
@page { size: A4; margin: 20mm 18mm 18mm 18mm;
  @top-left { content: "R. Yadav et al."; font-family: "Times New Roman", serif; font-size: 8pt; font-style: italic; }
  @top-right { content: "B.Tech Minor Project — Review Paper (Working Draft)"; font-family: "Times New Roman", serif; font-size: 8pt; font-style: italic; }
  @bottom-center { content: counter(page); font-family: "Times New Roman", serif; font-size: 9pt; } }
@page :first { @top-left { content: ""; } @top-right { content: ""; } }
body { font-family: "Times New Roman", Times, serif; font-size: 9.5pt; line-height: 1.20; color: #000; margin: 0; }
.draftlabel { font-size: 7.5pt; letter-spacing: 0.06em; text-transform: uppercase; margin: 0 0 10pt 0; }
h1.title { font-size: 17pt; font-weight: normal; line-height: 1.15; margin: 0 0 12pt 0; }
p.authors { font-size: 11pt; margin: 0 0 6pt 0; }
p.affil { font-size: 8pt; font-style: italic; margin: 0 0 14pt 0; }
sup { font-size: 7pt; vertical-align: super; }
.panel { border-top: 0.7pt solid #000; border-bottom: 0.7pt solid #000; padding: 8pt 0 10pt 0; margin: 0 0 14pt 0;
  display: grid; grid-template-columns: 30% 1fr; column-gap: 6mm; }
.panel h2 { font-size: 8pt; font-weight: normal; letter-spacing: 0.28em; margin: 0 0 8pt 0; }
.panel .kw { font-size: 8.5pt; }
.panel .kw .kwhead { font-style: italic; margin-bottom: 3pt; }
.panel .kw div { line-height: 1.35; }
.panel .abs { font-size: 8.5pt; text-align: justify; hyphens: auto; }
.cols { column-count: 2; column-gap: 6mm; }
h1 { font-size: 9.5pt; font-weight: bold; margin: 9pt 0 3pt 0; break-after: avoid; }
h2 { font-size: 9.5pt; font-weight: bold; font-style: italic; margin: 8pt 0 2pt 0; break-after: avoid; }
p { margin: 0; text-align: justify; hyphens: auto; text-indent: 10pt; orphans: 2; widows: 2; }
h1 + p, h2 + p { text-indent: 0; }
ol { margin: 3pt 0 3pt 14pt; padding: 0; text-align: justify; }
ol li { margin-bottom: 2pt; }
p.eq { text-align: center; text-indent: 0; margin: 4pt 0; }
p.eq .eqn { float: right; }
p.eq code { font-family: "Times New Roman", Times, serif; font-style: italic; }
.fw { column-span: all; break-inside: auto; }
figure.fig { margin: 8pt 0 10pt 0; text-align: center; }
figure.fig img { width: 100%; max-width: 132mm; height: auto; }
figcaption { font-size: 8pt; text-align: justify; margin-top: 4pt; }
p.tabcap { font-size: 8pt; text-align: left; text-indent: 0; margin: 8pt 0 3pt 0; }
table { border-collapse: collapse; width: 100%; font-size: 7.5pt; margin: 0 0 10pt 0;
  border-top: 0.7pt solid #000; border-bottom: 0.7pt solid #000; }
thead { display: table-header-group; }
th, td { padding: 2pt 4pt 2pt 0; vertical-align: top; text-align: left; border: none; }
thead th { border-bottom: 0.5pt solid #000; font-weight: normal; }
table.wide { font-size: 6.2pt; }
table.wide td, table.wide th { padding: 1.5pt 3pt 1.5pt 0; }
tr { break-inside: avoid; }
code { font-family: "Times New Roman", Times, serif; font-style: italic; }
h1.refhead { font-size: 9.5pt; font-weight: bold; margin: 10pt 0 4pt 0; }
p.ref { font-size: 8pt; text-indent: 0; padding-left: 10pt; text-indent: -10pt; margin: 0 0 2pt 0; text-align: left; }
"""

kw_html = '\n'.join('<div>%s</div>' % k for k in keywords)
htmlout = """<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8">
<title>Deep Learning for AI-Generated Image Detection \u2014 draft v2</title>
<style>%s</style></head><body>
<p class="draftlabel">B.Tech Minor Project \u2014 Review Paper (Working Draft, not for distribution)</p>
<h1 class="title">Deep Learning for AI-Generated Image Detection: A Review of CNN, Vision Transformer, and Explainable Approaches</h1>
<p class="authors">Rohit Yadav <sup>a</sup>, Vishal <sup>a</sup>, Hardik Mehlawat <sup>a</sup></p>
<p class="affil"><sup>a</sup> Amity School of Engineering and Technology, Amity University Uttar Pradesh (Group 148; Guide: Dr. Richa Gupta)</p>
<div class="panel">
  <div class="kw"><h2>ARTICLE INFO</h2><div class="kwhead">Keywords:</div>%s</div>
  <div class="abs"><h2>ABSTRACT</h2><p style="text-indent:0">%s</p></div>
</div>
<div class="cols">
%s
<h1 class="refhead">References</h1>
%s
</div>
</body></html>
""" % (CSS, kw_html, abstract, body.strip(), refs)

OUT.write_text(htmlout, encoding='utf-8')

# ------------------------------------------------------------------- sanity
leftover_num = re.findall(r'\[\d+(?:\s*,\s*\d+)*\]', htmlout)
leftover_cid = re.findall(r'\[C\d+\]', htmlout)
print("leftover numeric citations:", len(leftover_num), leftover_num[:5])
print("leftover [Cxx] keys:", len(leftover_cid))
valid = set(LBL.values())
used = set(re.findall(r'\(([A-Z][^()]{1,60}?, \d{4}[ab]?)\)', htmlout))
flat = set()
for u in used:
    for part in u.split('; '):
        flat.add(part.strip())
unknown = sorted(x for x in flat if x not in valid)
print("unresolvable (Author, Year) strings:", unknown)
print("distinct labels used in text:", len(flat & valid), "of", len(valid))
unused = sorted(valid - flat)
print("labels never used in an inline parenthetical:", unused)
print("wrote", OUT, OUT.stat().st_size, "bytes")
