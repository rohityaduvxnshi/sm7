// Builds the Semester 7 final report (Amity "Project Plan" format) as DOCX.
// Inputs : ../chapters/*.md (markup described in README.md), ../tables/t10_1.json, ../tables/t12_1.json,
//          ../figures/*.png, bib.json (from prep_bib.py)
// Output : argv[2] (default ../out/report.docx). Word (export_pdf.ps1) then updates the TOC/list fields
//          and exports the PDF.
const fs = require('fs');
const path = require('path');
const {
  Document, Packer, Paragraph, TextRun, ImageRun, Table, TableRow, TableCell, WidthType, AlignmentType,
  TableOfContents, StyleLevel, Header, Footer, PageNumber, NumberFormat, PageOrientation, BorderStyle,
  ShadingType, LevelFormat, TabStopType, LeaderType, VerticalAlign, TableLayoutType,
  Math: OMath, MathRun, MathFraction, MathIntegral, MathSum, MathSubScript,
} = require('docx');

const FR = path.resolve(process.env.REPORT_DIR || path.join(__dirname, '..'));
const CH = path.join(FR, 'chapters');
const OUT = path.resolve(process.argv[2] || path.join(FR, 'out', 'report.docx'));
const bib = JSON.parse(fs.readFileSync(path.join(__dirname, 'bib.json'), 'utf8'));

// ------------------------------------------------------------------ page geometry (twips)
const IN = 1440;
const A4 = { width: 11906, height: 16838 };
const TEXT_W = A4.width - 2.5 * IN;                    // portrait: 1.25" side margins
const LAND_W = A4.height - 2 * IN;                     // landscape: 1.0" left/right
const PORTRAIT = { size: A4, margin: { top: IN, bottom: IN, left: 1.25 * IN, right: 1.25 * IN, header: 0.5 * IN, footer: 0.5 * IN } };
// landscape pages: the top edge sits at the binding side, so it keeps the wide 1.25" margin
const LANDSCAPE = { size: { ...A4, orientation: PageOrientation.LANDSCAPE }, margin: { top: 1.25 * IN, bottom: 1.25 * IN, left: IN, right: IN, header: 0.6 * IN, footer: 0.5 * IN } };

// ------------------------------------------------------------------ citations
const labelName = (k) => {
  const a = bib[k].authors;
  if (a.length === 1) return a[0][0];
  if (a.length === 2) return `${a[0][0]} and ${a[1][0]}`;
  return `${a[0][0]} et al.`;
};
const CITE_RE = /\[(C\d{2}(?:\s*,\s*C\d{2})*)\]|\{(C\d{2})\}/g;
const citedKeys = new Set();
function collectKeys(text) {
  for (const m of text.matchAll(CITE_RE)) (m[1] || m[2]).split(',').forEach((k) => citedKeys.add(k.trim()));
}
let suffix = {};
function computeSuffixes() {
  for (const k of citedKeys) if (!bib[k]) throw new Error(`citation key ${k} not in references.bib`);
  const groups = {};
  for (const k of [...citedKeys].sort(refOrder)) {
    const g = `${labelName(k)}|${bib[k].year}`;
    (groups[g] = groups[g] || []).push(k);
  }
  suffix = {};
  for (const ks of Object.values(groups)) if (ks.length > 1) ks.forEach((k, i) => { suffix[k] = 'abcdefgh'[i]; });
}
const yearOf = (k) => bib[k].year + (suffix[k] || '');
// grouped citations in chronological order (Harvard convention), then by author within a year
const paren = (keys) => '(' + keys.sort((x, y) => yearOf(x).localeCompare(yearOf(y)) || labelName(x).localeCompare(labelName(y)))
  .map((k) => `${labelName(k)}, ${yearOf(k)}`).join('; ') + ')';
const narrative = (k) => `${labelName(k)} (${yearOf(k)})`;
function renderCites(text) {
  return text.replace(CITE_RE, (_, grp, one) => (one ? narrative(one) : paren(grp.split(',').map((s) => s.trim()))));
}
function refOrder(x, y) {
  const kx = [bib[x].authors[0][0].toLowerCase(), labelName(x).toLowerCase(), bib[x].year, bib[x].title.toLowerCase()];
  const ky = [bib[y].authors[0][0].toLowerCase(), labelName(y).toLowerCase(), bib[y].year, bib[y].title.toLowerCase()];
  for (let i = 0; i < kx.length; i++) { const c = kx[i].localeCompare(ky[i]); if (c) return c; }
  return 0;
}

// ------------------------------------------------------------------ inline text -> runs
function runs(text, opts = {}) {
  const out = [];
  const src = renderCites(text);
  for (const part of src.split(/(\*\*[^*]+\*\*|\*[^*\s][^*]*\*)/)) {
    if (!part) continue;
    if (part.startsWith('**')) out.push(new TextRun({ text: part.slice(2, -2), bold: true, ...opts }));
    else if (part.startsWith('*') && part.length > 2) out.push(new TextRun({ text: part.slice(1, -1), italics: true, ...opts }));
    else out.push(new TextRun({ text: part, ...opts }));
  }
  return out;
}

// ------------------------------------------------------------------ styles
const TNR = 'Times New Roman';
const styles = {
  default: { document: { run: { font: TNR, size: 24 } } },
  paragraphStyles: [
    { id: 'Normal', name: 'Normal', run: { font: TNR, size: 24 },
      paragraph: { alignment: AlignmentType.JUSTIFIED, spacing: { line: 360, before: 0, after: 120 }, indent: { firstLine: 720 } } },
    { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: TNR, size: 32, bold: true },
      paragraph: { alignment: AlignmentType.LEFT, spacing: { before: 0, after: 360, line: 276 }, indent: { firstLine: 0 }, keepNext: true, keepLines: true,
        pageBreakBefore: true, outlineLevel: 0, border: { bottom: { style: BorderStyle.SINGLE, size: 12, color: '000000', space: 4 } } } },
    { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true, run: { font: TNR, size: 28, bold: true },
      paragraph: { alignment: AlignmentType.LEFT, spacing: { before: 240, after: 120, line: 276 }, indent: { firstLine: 0 }, keepNext: true, keepLines: true, outlineLevel: 1 } },
    { id: 'PreHeading', name: 'PreHeading', basedOn: 'Normal', next: 'Normal', run: { font: TNR, size: 28, bold: true },
      paragraph: { alignment: AlignmentType.CENTER, spacing: { before: 0, after: 480, line: 276 }, indent: { firstLine: 0 }, keepNext: true } },
    { id: 'PreTitle', name: 'PreTitle', basedOn: 'PreHeading', next: 'Normal', run: { font: TNR, size: 28, bold: true } },
    { id: 'Plain', name: 'Plain', basedOn: 'Normal', paragraph: { indent: { firstLine: 0 } } },
    { id: 'Center', name: 'Center', basedOn: 'Normal', paragraph: { alignment: AlignmentType.CENTER, indent: { firstLine: 0 }, spacing: { line: 276, after: 120 } } },
    { id: 'ListPara', name: 'ListPara', basedOn: 'Normal', paragraph: { indent: { firstLine: 0 }, spacing: { after: 80 } } },
    { id: 'TableCaption', name: 'TableCaption', basedOn: 'Normal', next: 'Normal', run: { font: TNR, size: 22 },
      paragraph: { alignment: AlignmentType.CENTER, indent: { firstLine: 0 }, spacing: { before: 200, after: 100, line: 240 }, keepNext: true, keepLines: true } },
    { id: 'FigureCaption', name: 'FigureCaption', basedOn: 'Normal', next: 'Normal', run: { font: TNR, size: 22 },
      paragraph: { alignment: AlignmentType.CENTER, indent: { firstLine: 0 }, spacing: { before: 80, after: 280, line: 240 }, keepLines: true } },
    { id: 'TableText', name: 'TableText', basedOn: 'Normal', run: { font: TNR, size: 20 },
      paragraph: { alignment: AlignmentType.LEFT, indent: { firstLine: 0 }, spacing: { before: 0, after: 0, line: 240 } } },
    { id: 'TableTextSmall', name: 'TableTextSmall', basedOn: 'TableText', run: { font: TNR, size: 17 } },
    { id: 'TableNote', name: 'TableNote', basedOn: 'Normal', run: { font: TNR, size: 19 },
      paragraph: { alignment: AlignmentType.JUSTIFIED, indent: { firstLine: 0 }, spacing: { before: 80, after: 200, line: 240 } } },
    { id: 'Equation', name: 'Equation', basedOn: 'Normal', paragraph: { alignment: AlignmentType.LEFT, indent: { firstLine: 0 }, spacing: { before: 120, after: 160 },
      tabStops: [{ type: TabStopType.CENTER, position: Math.round(TEXT_W / 2) }, { type: TabStopType.RIGHT, position: TEXT_W }] } },
    { id: 'Reference', name: 'Reference', basedOn: 'Normal', paragraph: { alignment: AlignmentType.LEFT, indent: { left: 720, hanging: 720 }, spacing: { after: 120, line: 360 } } },
    { id: 'FigurePara', name: 'FigurePara', basedOn: 'Normal', paragraph: { alignment: AlignmentType.CENTER, indent: { firstLine: 0 }, spacing: { before: 200, after: 0, line: 240 }, keepNext: true } },
    { id: 'TOC1', name: 'toc 1', basedOn: 'Normal', next: 'Normal', run: { font: TNR, size: 24 },
      paragraph: { alignment: AlignmentType.LEFT, indent: { firstLine: 0, left: 0, right: 600 }, spacing: { before: 100, after: 0, line: 276 },
        tabStops: [{ type: TabStopType.RIGHT, position: TEXT_W, leader: LeaderType.DOT }] } },
    { id: 'TOC2', name: 'toc 2', basedOn: 'Normal', next: 'Normal', run: { font: TNR, size: 24 },
      paragraph: { alignment: AlignmentType.LEFT, indent: { firstLine: 0, left: 480, right: 600 }, spacing: { before: 0, after: 0, line: 276 },
        tabStops: [{ type: TabStopType.RIGHT, position: TEXT_W, leader: LeaderType.DOT }] } },
  ],
};
const numbering = {
  config: [
    { reference: 'num', levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '%1.', alignment: AlignmentType.LEFT,
      style: { paragraph: { indent: { left: 720, hanging: 360 } } } }] },
    { reference: 'bul', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT,
      style: { run: { font: TNR }, paragraph: { indent: { left: 720, hanging: 360 } } } }] },
  ],
};
let listInstance = 0;

// ------------------------------------------------------------------ building blocks
const P = (text, style = 'Normal', extra = {}) => new Paragraph({ style, children: runs(text), ...extra });
const cellBorders = { top: { style: BorderStyle.SINGLE, size: 4, color: '000000' }, bottom: { style: BorderStyle.SINGLE, size: 4, color: '000000' },
  left: { style: BorderStyle.SINGLE, size: 4, color: '000000' }, right: { style: BorderStyle.SINGLE, size: 4, color: '000000' } };
function makeTable(header, rows, widths, textStyle = 'TableText') {
  const total = widths.reduce((a, b) => a + b, 0);
  const cell = (txt, w, head) => new TableCell({
    width: { size: w, type: WidthType.DXA }, borders: cellBorders, verticalAlign: VerticalAlign.TOP,
    margins: { top: 50, bottom: 50, left: 80, right: 80 },
    shading: head ? { type: ShadingType.CLEAR, color: 'auto', fill: 'D9D9D9' } : undefined,
    children: [new Paragraph({ style: textStyle, children: runs(String(txt), head ? { bold: true } : {}) })],
  });
  return new Table({
    width: { size: total, type: WidthType.DXA }, columnWidths: widths, layout: TableLayoutType.FIXED,
    rows: [new TableRow({ tableHeader: true, cantSplit: true, children: header.map((h, i) => cell(h, widths[i], true)) }),
      ...rows.map((r) => new TableRow({ cantSplit: true, children: r.map((c, i) => cell(c, widths[i], false)) }))],
  });
}
// Column widths for the small portrait tables: every column is at least as wide as its longest word
// (so nothing wraps mid-word), and the remaining width is shared in proportion to how much text a
// column holds. ponytail: character widths are estimated (~100 twips per character at 10 pt), not measured.
function autoWidths(header, rows, total) {
  const n = header.length;
  const plain = (s) => renderCites(String(s)).replace(/\*\*|\*/g, '');
  const longest = (s) => Math.max(...plain(s).split(/\s+/).map((w) => w.length), 1);
  const minW = [], weight = [];
  for (let i = 0; i < n; i++) {
    const body = rows.map((r) => r[i] || '');
    const need = Math.max(longest(header[i]) * 112, ...body.map((c) => longest(c) * 100));
    minW.push(need + 220);
    const lens = [header[i], ...body].map((c) => plain(c).length);
    weight.push(Math.max(4, lens.reduce((a, b) => a + b, 0) / lens.length));
  }
  const fix = (o) => { o[n - 1] += total - o.reduce((a, b) => a + b, 0); return o; };
  const sumMin = minW.reduce((a, b) => a + b, 0);
  if (sumMin >= total) return fix(minW.map((w) => Math.floor((w * total) / sumMin)));
  const wsum = weight.reduce((a, b) => a + b, 0);
  return fix(minW.map((m, i) => m + Math.floor(((total - sumMin) * weight[i]) / wsum)));
}
const tableCaption = (num, text) => new Paragraph({ style: 'TableCaption', children: [new TextRun({ text: `Table ${num}. `, bold: true }), ...runs(text)] });
const figureCaption = (num, text) => new Paragraph({ style: 'FigureCaption', children: [new TextRun({ text: `Figure ${num}. `, bold: true }), ...runs(text)] });

const FIGS = {
  prisma: { file: 'prisma_flow.png', widthIn: 5.5 },
  taxonomy: { file: 'taxonomy_overview.png', widthIn: 5.6 },
  metrics: { file: 'metrics_overview.png', widthIn: 4.9 },
};
function pngSize(buf) { return { w: buf.readUInt32BE(16), h: buf.readUInt32BE(20) }; }
function image(file, widthIn) {
  const data = fs.readFileSync(path.join(FR, 'figures', file));
  const { w, h } = pngSize(data);
  const pw = Math.round(widthIn * 96);
  return new ImageRun({ type: 'png', data, transformation: { width: pw, height: Math.round((pw * h) / w) } });
}

// ------------------------------------------------------------------ equations (Chapter 11)
const mr = (t) => new MathRun(t);
const sub = (base, s) => new MathSubScript({ children: [mr(base)], subScript: [mr(s)] });
const frac = (n, d) => new MathFraction({ numerator: n, denominator: d });
const EQ = {
  '11.1': [mr('Accuracy = '), frac([mr('TP + TN')], [mr('TP + FP + FN + TN')])],
  '11.2': [mr('Precision = '), frac([mr('TP')], [mr('TP + FP')])],
  '11.3': [mr('Recall = TPR = '), frac([mr('TP')], [mr('TP + FN')])],
  '11.4': [mr('F1 = '), frac([mr('2 · Precision · Recall')], [mr('Precision + Recall')])],
  '11.5': [mr('FPR = '), frac([mr('FP')], [mr('FP + TN')])],
  '11.6': [mr('AUC = '), new MathIntegral({ children: [mr('TPR(FPR) d(FPR)')], subScript: [mr('0')], superScript: [mr('1')] })],
  '11.7': [mr('AP = '), new MathSum({ children: [mr('('), sub('Recall', 'k'), mr(' − '), sub('Recall', 'k−1'), mr(') · '), sub('Precision', 'k')], subScript: [mr('k')] })],
  '11.8': [mr('mAP = '), frac([mr('1')], [mr('N')]), new MathSum({ children: [sub('AP', 'i')], subScript: [mr('i')] })],
};
const equation = (num) => {
  if (!EQ[num]) throw new Error(`unknown equation ${num}`);
  return new Paragraph({ style: 'Equation', children: [new TextRun('\t'), new OMath({ children: EQ[num] }), new TextRun(`\t(${num})`)] });
};

// ------------------------------------------------------------------ landscape tables
const landCache = {};
function landscapeTable(key) {
  if (landCache[key]) return landCache[key];
  const t = JSON.parse(fs.readFileSync(path.join(FR, 'tables', key + '.json'), 'utf8'));
  const W = (arr) => { const s = arr.reduce((a, b) => a + b, 0); const o = arr.map((x) => Math.floor((x / s) * LAND_W)); o[o.length - 1] += LAND_W - o.reduce((a, b) => a + b, 0); return o; };
  let header, rows, widths;
  if (key === 't12_1') {
    header = ['Study', 'Detection approach', 'Model / architecture', 'Dataset used', 'Generator(s) covered', 'Reported accuracy / AUC', 'Cross-generator tested?', 'Key limitation'];
    rows = t.rows.map((r) => [`{${r.cid}}`, r.approach, r.model, r.dataset, r.generators, r.result, r.crossgen, r.limitation]);
    widths = W([0.95, 1.2, 1.2, 1.25, 1.4, 1.35, 1.0, 1.34]);
  } else {
    header = ['Dataset', 'Introduced by', 'Year', 'Scale', 'Real-image source', 'Generators covered', 'Notes / stated limitation'];
    rows = t.rows.map((r) => [r.dataset, r.introduced_by, r.year, r.scale, r.real_source, r.generators, r.notes]);
    widths = W([1.2, 1.05, 0.45, 1.45, 1.1, 1.85, 2.59]);
  }
  rows.forEach((r) => r.forEach((c) => collectKeys(String(c))));
  collectKeys(t.caption); collectKeys(t.note);
  return (landCache[key] = { num: t.number, caption: t.caption, note: t.note, header, rows, widths });
}

// ------------------------------------------------------------------ markup parser
function parseFile(file) {
  const text = fs.readFileSync(file, 'utf8').replace(/\r\n/g, '\n');
  collectKeys(text);
  const lines = text.split('\n');
  const blocks = [];
  let i = 0;
  while (i < lines.length) {
    const line = lines[i];
    const t = line.trim();
    if (!t) { i++; continue; }
    let m;
    if ((m = t.match(/^# (.+)$/))) { blocks.push({ type: 'h1', text: m[1] }); i++; continue; }
    if ((m = t.match(/^## (.+)$/))) { blocks.push({ type: 'h2', text: m[1] }); i++; continue; }
    if ((m = t.match(/^\[\[FIGURE:(\w+)\|([\d.]+)\|(.+)\]\]$/))) { blocks.push({ type: 'figure', key: m[1], num: m[2], caption: m[3] }); i++; continue; }
    if ((m = t.match(/^\[\[TABLE:(\w+)\]\]$/))) { blocks.push({ type: 'land', key: m[1] }); i++; continue; }
    if ((m = t.match(/^\[\[EQ:([\d.]+)\]\]$/))) { blocks.push({ type: 'eq', num: m[1] }); i++; continue; }
    if ((m = t.match(/^Table:\s*([\dA-Z.]+)\s*\|\s*(.+)$/))) {
      const rows = [];
      i++;
      while (i < lines.length && lines[i].trim().startsWith('|')) {
        const r = lines[i].trim();
        if (!/^\|[\s:|-]+\|$/.test(r)) rows.push(r.replace(/^\||\|$/g, '').split('|').map((c) => c.trim()));
        i++;
      }
      if (rows.length < 2) throw new Error(`${path.basename(file)}: table ${m[1]} has no body rows`);
      blocks.push({ type: 'table', num: m[1], caption: m[2], header: rows[0], rows: rows.slice(1) });
      continue;
    }
    if (/^- /.test(t)) {
      const items = [];
      while (i < lines.length && /^- /.test(lines[i].trim())) { items.push(lines[i].trim().slice(2)); i++; }
      blocks.push({ type: 'bul', items }); continue;
    }
    if (/^\d+\.\s/.test(t)) {
      const items = [];
      while (i < lines.length && /^\d+\.\s/.test(lines[i].trim())) { items.push(lines[i].trim().replace(/^\d+\.\s+/, '')); i++; }
      blocks.push({ type: 'num', items }); continue;
    }
    if (/^(\[\[|Table:)/.test(t)) throw new Error(`${path.basename(file)}: malformed markup line: ${t.slice(0, 80)}`);
    const para = [];
    while (i < lines.length && lines[i].trim() && !/^(#|\[\[|Table:|- |\d+\.\s|\|)/.test(lines[i].trim())) { para.push(lines[i].trim()); i++; }
    if (!para.length) throw new Error(`${path.basename(file)}: stray line ${t.slice(0, 80)}`);
    blocks.push({ type: 'p', text: para.join(' ') });
  }
  return blocks;
}

// ------------------------------------------------------------------ document assembly
const sections = [];
const pageHeader = () => ({ default: new Header({ children: [new Paragraph({ alignment: AlignmentType.RIGHT, indent: { firstLine: 0 }, children: [new TextRun({ children: [PageNumber.CURRENT] })] })] }) });
const emptyFooter = () => ({ default: new Footer({ children: [new Paragraph({ children: [] })] }) });
const emptyHeader = () => ({ default: new Header({ children: [new Paragraph({ children: [] })] }) });
let cur = null;
function openMain(page, first) {
  cur = { properties: { page: { ...page, pageNumbers: first ? { start: 1, formatType: NumberFormat.DECIMAL } : { formatType: NumberFormat.DECIMAL } } },
    headers: pageHeader(), footers: emptyFooter(), children: [] };
  sections.push(cur);
}

const mentions = [];        // [{kind, num, pos}] for order checks
const placements = [];
let order = 0;
function noteMentions(text) {
  for (const m of text.matchAll(/\b(Table|Figure)s?\s+((?:\d+|[A-Z])\.\d+)(?:\s*(?:and|,|–|to)\s*((?:\d+|[A-Z])\.\d+))?/g)) {
    mentions.push({ kind: m[1], num: m[2], pos: order });
    if (m[3]) mentions.push({ kind: m[1], num: m[3], pos: order });
  }
}

function emitBlocks(blocks, file) {
  for (const b of blocks) {
    order++;
    switch (b.type) {
      case 'h1': cur.children.push(new Paragraph({ style: 'Heading1', children: runs(b.text) })); break;
      case 'h2': cur.children.push(new Paragraph({ style: 'Heading2', children: runs(b.text) })); break;
      case 'p': noteMentions(b.text); cur.children.push(P(b.text)); break;
      case 'bul': case 'num': {
        const inst = ++listInstance;
        for (const it of b.items) { noteMentions(it); cur.children.push(new Paragraph({ style: 'ListPara', numbering: { reference: b.type === 'num' ? 'num' : 'bul', level: 0, instance: inst }, children: runs(it) })); }
        break;
      }
      case 'table': {
        placements.push({ kind: 'Table', num: b.num, pos: order, file });
        b.rows.forEach((r) => { if (r.length !== b.header.length) throw new Error(`${path.basename(file)}: table ${b.num} row has ${r.length} cells, header ${b.header.length}`); });
        cur.children.push(tableCaption(b.num, b.caption));
        cur.children.push(makeTable(b.header, b.rows, autoWidths(b.header, b.rows, TEXT_W)));
        cur.children.push(new Paragraph({ style: 'Plain', spacing: { after: 120 }, children: [] }));
        break;
      }
      case 'figure': {
        const f = FIGS[b.key];
        if (!f) throw new Error(`unknown figure key ${b.key}`);
        placements.push({ kind: 'Figure', num: b.num, pos: order, file });
        cur.children.push(new Paragraph({ style: 'FigurePara', children: [image(f.file, f.widthIn)] }));
        cur.children.push(figureCaption(b.num, b.caption));
        break;
      }
      case 'eq': cur.children.push(equation(b.num)); break;
      case 'land': {
        const t = landscapeTable(b.key);
        placements.push({ kind: 'Table', num: t.num, pos: order, file });
        const land = { properties: { page: { ...LANDSCAPE, pageNumbers: { formatType: NumberFormat.DECIMAL } } }, headers: pageHeader(), footers: emptyFooter(),
          children: [tableCaption(t.num, t.caption), makeTable(t.header, t.rows, t.widths, 'TableTextSmall'), new Paragraph({ style: 'TableNote', children: runs(t.note) })] };
        sections.push(land);
        openMain(PORTRAIT, false);
        break;
      }
      default: throw new Error('unknown block ' + b.type);
    }
  }
}

// ---- pre-pages
const TITLE = 'Deep Learning for AI-Generated Image Detection: A Review of CNN, Vision Transformer, and Explainable Approaches';
const STUDENTS = [['Rohit Yadav', 'A2305223472'], ['Vishal', 'A2305223568'], ['Hardik Mehlawat', 'A2305223449']];
const C = (text, size = 28, extra = {}) => new Paragraph({ style: 'Center', spacing: { after: extra.after ?? 120, before: extra.before ?? 0, line: 276 },
  children: [new TextRun({ text, size, bold: !!extra.bold, underline: extra.underline ? {} : undefined })] });
const logo = fs.readFileSync(path.join(FR, 'figures', 'amity_logo.png'));
const ls = pngSize(logo);

const titlePage = [
  C('A Project Plan', 28, { before: 240, after: 80 }), C('On', 28, { after: 280 }),
  C(TITLE.toUpperCase(), 30, { bold: true, after: 400 }),
  C('Submitted to', 28, { after: 80 }), C('Amity University Uttar Pradesh', 28, { after: 320 }),
  new Paragraph({ style: 'Center', spacing: { after: 320 }, children: [new ImageRun({ type: 'png', data: logo, transformation: { width: 145, height: Math.round(145 * ls.h / ls.w) } })] }),
  C('in partial fulfillment of the requirements for the award of the degree of', 26, { after: 200 }),
  C('Bachelor of Technology', 28, { after: 60 }), C('Computer Science and Engineering', 28, { after: 280 }),
  C('by', 26, { after: 160 }),
  ...STUDENTS.map(([n, e]) => C(`${n.toUpperCase()} (${e})`, 26, { bold: true, after: 60 })),
  C('under the guidance of', 26, { before: 220, after: 100 }), C('Dr. Richa Gupta', 28, { bold: true, after: 400 }),
  C('DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING', 26, { after: 60 }),
  C('AMITY SCHOOL OF ENGINEERING AND TECHNOLOGY', 26, { after: 60 }),
  C('AMITY UNIVERSITY UTTAR PRADESH', 26, { after: 60 }), C('NOIDA (U.P.)', 26, { after: 280 }),
  C('October 2026', 26, { after: 0 }),
];

const sig = (lines) => lines.map((l, i) => new Paragraph({ style: 'Plain', alignment: AlignmentType.RIGHT, spacing: { after: 0, line: 300 }, children: [new TextRun({ text: l, bold: i === 0 && l !== '' })] }));
const declaration = [
  new Paragraph({ style: 'PreHeading', pageBreakBefore: true, children: [new TextRun({ text: 'DECLARATION', underline: {} })] }),
  P(`We, ${STUDENTS.map(([n, e]) => `${n} (${e})`).join(', ').replace(/, ([^,]+)$/, ' and $1')}, students of B.Tech (Computer Science and Engineering) hereby declare that the project titled “${TITLE}” which is submitted by us to Department of Computer Science and Engineering, Amity School of Engineering and Technology, Amity University Uttar Pradesh, Noida, in partial fulfillment of requirement for the award of the degree of Bachelor of Technology in Computer Science and Engineering, has not been previously formed the basis for the award of any degree, diploma or other similar title or recognition.`, 'Plain'),
  new Paragraph({ style: 'Plain', spacing: { before: 720, after: 0 }, children: [new TextRun('Noida')] }),
  new Paragraph({ style: 'Plain', spacing: { after: 600 }, children: [new TextRun('Date: ____________________')] }),
  new Paragraph({ style: 'Plain', alignment: AlignmentType.RIGHT, spacing: { after: 360 }, children: [new TextRun({ text: 'Name and signature of Students', bold: true })] }),
  ...STUDENTS.flatMap(([n, e]) => [new Paragraph({ style: 'Plain', alignment: AlignmentType.RIGHT, spacing: { after: 0, line: 276 }, children: [new TextRun('______________________________')] }),
    new Paragraph({ style: 'Plain', alignment: AlignmentType.RIGHT, spacing: { after: 360, line: 276 }, children: [new TextRun(`${n} (${e})`)] })]),
];
const certificate = [
  new Paragraph({ style: 'PreHeading', pageBreakBefore: true, children: [new TextRun({ text: 'CERTIFICATE', underline: {} })] }),
  P(`On the basis of declaration submitted by ${STUDENTS.map(([n]) => n).join(', ').replace(/, ([^,]+)$/, ' and $1')}, students of B. Tech (Computer Science and Engineering), I hereby certify that the project titled “${TITLE}” which is submitted to Department of Computer Science and Engineering, Amity School of Engineering and Technology, Amity University Uttar Pradesh, Noida, in partial fulfillment of the requirement for the award of the degree of Bachelor of Technology in Computer Science and Engineering, is an original contribution with existing knowledge and faithful record of work carried out by them under my guidance and supervision.`, 'Plain'),
  P('To the best of my knowledge this work has not been submitted in part or full for any Degree or Diploma to this University or elsewhere.', 'Plain'),
  new Paragraph({ style: 'Plain', spacing: { before: 720, after: 0 }, children: [new TextRun('Noida')] }),
  new Paragraph({ style: 'Plain', spacing: { after: 720 }, children: [new TextRun('Date: ____________________')] }),
  ...sig(['______________________________', 'Dr. Richa Gupta', '(Guide)', 'Department of Computer Science and Engineering', 'Amity School of Engineering and Technology', 'Amity University Uttar Pradesh, Noida']),
];

function prePage(heading, children, toc = true) {
  return [new Paragraph({ style: toc ? 'PreHeading' : 'PreTitle', pageBreakBefore: true, children: [new TextRun(heading)] }), ...children];
}
const ackText = fs.readFileSync(path.join(CH, '00_acknowledgement.md'), 'utf8').replace(/\r\n/g, '\n').trim().split(/\n\s*\n/);
const ackSign = [];
const ackParas = [];
for (const block of ackText) {
  const ls2 = block.split('\n').map((s) => s.trim()).filter(Boolean);
  if (ls2.every((l) => /\(A\d{10}\)$/.test(l))) ackSign.push(...ls2); else ackParas.push(ls2.join(' '));
}
const absText = fs.readFileSync(path.join(CH, '00_abstract.md'), 'utf8').replace(/\r\n/g, '\n').trim().split(/\n\s*\n/);
const kwLine = absText.find((b) => /^Keywords?:/i.test(b.trim()));
const absParas = absText.filter((b) => b !== kwLine).map((b) => b.replace(/\n/g, ' ').trim());
[...ackParas, ...absParas].forEach(collectKeys);

// ---- pass 1: read every source so all citation keys (and so the a/b year suffixes) are known
// before any text is rendered
const chapterFiles = fs.readdirSync(CH).filter((f) => /^\d\d[a-z]?_.*\.md$/.test(f) && !f.startsWith('00_')).sort();
const appendixFiles = fs.readdirSync(CH).filter((x) => /^A\d_.*\.md$/.test(x)).sort();
const chapterBlocks = chapterFiles.map((f) => [f, parseFile(path.join(CH, f))]);
const appendixBlocks = appendixFiles.map((f) => [f, parseFile(path.join(CH, f))]);
for (const [, bl] of [...chapterBlocks, ...appendixBlocks]) for (const b of bl) if (b.type === 'land') landscapeTable(b.key);
computeSuffixes();

const pre = [
  ...titlePage,
  ...declaration,
  ...certificate,
  ...prePage('ACKNOWLEDGEMENT', [...ackParas.map((t) => P(t)), new Paragraph({ style: 'Plain', spacing: { before: 360 }, children: [] }),
    ...ackSign.map((l) => new Paragraph({ style: 'Plain', alignment: AlignmentType.RIGHT, spacing: { after: 0, line: 300 }, children: [new TextRun(l)] }))]),
  ...prePage('TABLE OF CONTENTS', [new TableOfContents('Table of Contents', { hyperlink: true, headingStyleRange: '1-2', stylesWithLevels: [new StyleLevel('PreHeading', 1)] })], false),
  ...prePage('LIST OF TABLES', [new TableOfContents('List of Tables', { hyperlink: true, stylesWithLevels: [new StyleLevel('TableCaption', 1)] })]),
  ...prePage('LIST OF FIGURES', [new TableOfContents('List of Figures', { hyperlink: true, stylesWithLevels: [new StyleLevel('FigureCaption', 1)] })]),
  ...prePage('ABSTRACT', [...absParas.map((t) => P(t)),
    ...(kwLine ? [new Paragraph({ style: 'Plain', spacing: { before: 240 }, children: [new TextRun({ text: 'Keywords: ', bold: true }), ...runs(kwLine.replace(/^Keywords?:\s*/i, '').trim())] })] : [])]),
];
sections.push({
  properties: { titlePage: true, page: { ...PORTRAIT, pageNumbers: { start: 1, formatType: NumberFormat.LOWER_ROMAN } } },
  headers: { default: new Header({ children: [new Paragraph({ children: [] })] }), first: new Header({ children: [new Paragraph({ children: [] })] }) },
  footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, indent: { firstLine: 0 }, children: [new TextRun({ children: [PageNumber.CURRENT] })] })] }),
    first: new Footer({ children: [new Paragraph({ children: [] })] }) },
  children: pre,
});

// ---- chapters
openMain(PORTRAIT, true);
for (const [f, bl] of chapterBlocks) emitBlocks(bl, f);

// ---- references
function refRuns(k) {
  const e = bib[k];
  const a = e.authors.map(([s, i]) => (i ? `${s}, ${i}` : s));
  const authors = a.length === 1 ? a[0] : `${a.slice(0, -1).join(', ')} and ${a[a.length - 1]}`;
  let title = e.title.trim();
  if (!/[.?!]$/.test(title)) title += '.';
  const out = [new TextRun(`${authors} (${yearOf(k)}). ${title} `)];
  const pages = e.pages ? e.pages.replace(/--/g, '–') : '';
  if (e._type === 'article') {
    out.push(new TextRun({ text: e.journal, italics: true }));
    if (e.volume) out.push(new TextRun({ text: `, ${e.volume}`, italics: true }));
    if (e.number) out.push(new TextRun(`(${e.number})`));
    if (pages) out.push(new TextRun(`, ${pages}`));
    out.push(new TextRun('.'));
  } else if (e._type === 'inproceedings') {
    out.push(new TextRun('In '), new TextRun({ text: e.booktitle, italics: true }));
    const bits = [];
    if (e.volume) bits.push(`Vol. ${e.volume}`);
    if (pages) bits.push(`pp. ${pages}`);
    if (bits.length) out.push(new TextRun(` (${bits.join(', ')})`));
    out.push(new TextRun('.'));
    if (e.publisher) out.push(new TextRun(` ${e.publisher}.`));
  } else {
    out.push(new TextRun({ text: 'arXiv preprint', italics: true }), new TextRun(` arXiv:${e.eprint}.`));
  }
  const link = e.doi ? `https://doi.org/${e.doi}` : e.eprint ? `https://arxiv.org/abs/${e.eprint}` : e.url;
  if (link) out.push(new TextRun(` ${link}`));
  return out;
}
const refKeys = [...citedKeys].sort(refOrder);
cur.children.push(new Paragraph({ style: 'Heading1', children: [new TextRun('REFERENCES')] }));
for (const k of refKeys) cur.children.push(new Paragraph({ style: 'Reference', children: refRuns(k) }));

// ---- appendices (A*.md, placed after the references)
for (const [f, bl] of appendixBlocks) emitBlocks(bl, f);

// ---- order checks: every table/figure mentioned in text before it is placed, numbering consecutive
const problems = [];
for (const p of placements) {
  const first = mentions.filter((m) => m.kind === p.kind && m.num === p.num).map((m) => m.pos).sort((a, b) => a - b)[0];
  if (first === undefined) problems.push(`${p.kind} ${p.num} is never mentioned in the text`);
  else if (first > p.pos) problems.push(`${p.kind} ${p.num} is placed before its first mention`);
}
for (const kind of ['Table', 'Figure']) {
  const nums = placements.filter((p) => p.kind === kind).map((p) => p.num);
  const seen = new Set();
  for (const n of nums) { if (seen.has(n)) problems.push(`${kind} ${n} placed twice`); seen.add(n); }
  const byCh = {};
  for (const n of nums) { const [c, k] = n.split('.'); (byCh[c] = byCh[c] || []).push(+k); }
  for (const [c, ks] of Object.entries(byCh)) ks.forEach((k, i) => { if (k !== i + 1) problems.push(`${kind} numbering in chapter ${c} is not consecutive: ${ks.join(',')}`); });
}
for (const m of mentions) if (!placements.some((p) => p.kind === m.kind && p.num === m.num)) problems.push(`text mentions ${m.kind} ${m.num}, which does not exist`);

const doc = new Document({
  creator: 'Group 148', title: TITLE, description: 'Semester 7 minor project report (NTCC ETMN100)',
  styles, numbering, sections, features: { updateFields: false },
});
fs.mkdirSync(path.dirname(OUT), { recursive: true });
Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(OUT, buf);
  console.log(`wrote ${OUT} (${buf.length} bytes); sections: ${sections.length}; references: ${refKeys.length}`);
  const sx = Object.entries(suffix).map(([k, s]) => `${k}=${labelName(k)} ${bib[k].year}${s}`);
  console.log('year suffixes:', sx.join('; ') || 'none');
  console.log('uncited bib entries:', Object.keys(bib).filter((k) => !citedKeys.has(k)).join(', ') || 'none');
  if (problems.length) { console.log('ORDER/NUMBERING PROBLEMS:\n  ' + [...new Set(problems)].join('\n  ')); process.exitCode = 2; }
});
