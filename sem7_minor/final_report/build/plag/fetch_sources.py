"""Collect a comparison corpus for the similarity pre-check (run once; output stays outside the repo).

Writes plain-text files into OUT_DIR/<group>/<name>.txt:
  abstracts/  arXiv abstracts (export.arxiv.org API) and Semantic Scholar abstracts for DOI-only entries
  fulltext/   arXiv PDFs and open-access PDFs converted with pdftotext
  wiki/       Wikipedia plain-text extracts for the report's core concepts
Usage: python -I fetch_sources.py <bib.json> <OUT_DIR>
"""
import json, os, re, subprocess, sys, time, urllib.error, urllib.parse, urllib.request, xml.etree.ElementTree as ET

UA = {'User-Agent': 'student-report-similarity-precheck/1.0'}
WIKI = ['Generative adversarial network', 'Diffusion model', 'Latent diffusion model', 'Stable Diffusion', 'Vision transformer',
        'Convolutional neural network', 'Transfer learning', 'Residual neural network', 'Contrastive Language-Image Pre-training',
        'Deepfake', 'Precision and recall', 'F-score', 'Receiver operating characteristic', 'Confusion matrix',
        'Evaluation measures (information retrieval)', 'Explainable artificial intelligence', 'Saliency map', 'Discrete cosine transform',
        'JPEG', 'Systematic review', 'Preferred Reporting Items for Systematic Reviews and Meta-Analyses', 'Digital image forensics',
        'Synthetic media', 'Artificial intelligence art', 'Text-to-image model', 'Overfitting', 'Fine-tuning (deep learning)',
        'ImageNet', 'Midjourney', 'DALL-E', 'Data augmentation', 'Autoencoder', 'Variational autoencoder', 'Fourier transform',
        'Support vector machine', 'Media forensics', 'Misinformation', 'Image resolution', 'Benchmark (computing)']


def get(url, timeout=60):
    for wait in (0, 15, 45, 90):
        time.sleep(wait)
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except urllib.error.HTTPError as ex:
            if ex.code not in (429, 503) or wait == 90:
                raise


def save(out, group, name, text):
    os.makedirs(os.path.join(out, group), exist_ok=True)
    with open(os.path.join(out, group, re.sub(r'[^\w.-]+', '_', name) + '.txt'), 'w', encoding='utf-8') as f:
        f.write(text)


def pdf_text(data, out, name):
    tmp = os.path.join(out, '_tmp.pdf')
    with open(tmp, 'wb') as f:
        f.write(data)
    txt = subprocess.run(['pdftotext', '-q', '-enc', 'UTF-8', tmp, '-'], capture_output=True).stdout.decode('utf-8', 'replace')
    os.remove(tmp)
    if len(txt.split()) > 300:
        save(out, 'fulltext', name, txt)
        return True
    return False


def main(bib_path, out):
    bib = json.load(open(bib_path, encoding='utf-8'))
    ids = {k: e['eprint'] for k, e in bib.items() if e.get('eprint')}
    # 1. arXiv abstracts, batched API calls of 20 ids
    ns = {'a': 'http://www.w3.org/2005/Atom'}
    by_id = {}
    vals = list(ids.values())
    for c in range(0, len(vals), 20):
        q = 'https://export.arxiv.org/api/query?' + urllib.parse.urlencode({'id_list': ','.join(vals[c:c + 20]), 'max_results': 50})
        try:
            feed = ET.fromstring(get(q, 120))
            for ent in feed.findall('a:entry', ns):
                aid = ent.find('a:id', ns).text.rsplit('/', 1)[-1].split('v')[0]
                by_id[aid] = ent.find('a:summary', ns).text
        except Exception as ex:
            print('  arXiv API chunk failed', c, ex)
        time.sleep(5)
    for k, aid in ids.items():
        if aid in by_id:
            save(out, 'abstracts', f'{k}_arxiv_{aid}', by_id[aid])
    print(f'arXiv abstracts: {len(by_id)}/{len(ids)}')
    # 2. Semantic Scholar abstracts + open-access PDF links for entries without an arXiv id
    oa = {}
    for k, e in bib.items():
        if e.get('eprint') or not e.get('doi'):
            continue
        try:
            j = json.loads(get('https://api.semanticscholar.org/graph/v1/paper/DOI:' + e['doi'] + '?fields=title,abstract,openAccessPdf'))
            if j.get('abstract'):
                save(out, 'abstracts', f'{k}_s2', j['abstract'])
            if (j.get('openAccessPdf') or {}).get('url'):
                oa[k] = j['openAccessPdf']['url']
        except Exception as ex:
            print('  s2 miss', k, ex)
        time.sleep(3)
    if bib.get('C32', {}).get('url'):
        oa['C32'] = 'https://proceedings.mlr.press/v235/chen24ay/chen24ay.pdf'
    # 3. full texts: arXiv PDFs (polite pacing) and open-access PDFs
    got = 0
    for k, aid in ids.items():
        try:
            if pdf_text(get(f'https://export.arxiv.org/pdf/{aid}', 120), out, f'{k}_arxiv_{aid}'):
                got += 1
        except Exception as ex:
            print('  pdf miss', k, aid, ex)
        time.sleep(3)
    for k, url in oa.items():
        try:
            if pdf_text(get(url, 120), out, f'{k}_oa'):
                got += 1
        except Exception as ex:
            print('  oa miss', k, ex)
        time.sleep(2)
    print(f'full texts: {got}')
    # 4. Wikipedia extracts
    n = 0
    for t in WIKI:
        try:
            u = 'https://en.wikipedia.org/w/api.php?' + urllib.parse.urlencode(
                {'action': 'query', 'prop': 'extracts', 'explaintext': 1, 'redirects': 1, 'titles': t, 'format': 'json'})
            pages = json.loads(get(u))['query']['pages']
            txt = next(iter(pages.values())).get('extract', '')
            if txt:
                save(out, 'wiki', t, txt); n += 1
        except Exception as ex:
            print('  wiki miss', t, ex)
        time.sleep(1)
    print(f'wikipedia pages: {n}/{len(WIKI)}')


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main(sys.argv[1], sys.argv[2])
