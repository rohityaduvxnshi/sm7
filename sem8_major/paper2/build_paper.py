"""Assemble paper2_draft_v1.md from paper2/sections/*.md (implementation_plan.md s10, phase P1).

    python paper2/build_paper.py            (run from sem8_major/)
    python paper2/build_paper.py --selfcheck

Placeholders in the section files:
    {{table:<name>|<caption>}}    results/tables/<name>.md (written by make_tables.py) inserted
                                  verbatim minus its bold title line, caption above, the table's
                                  own notes below. A missing table prints a visible PENDING block
                                  (t6_ablations until the A5 rows are merged); nothing is retyped.
    {{figure:<name>|<caption>}}   ![..](../figures/<name>.png); a missing figure fails the build.
    {{refs}}                      every [Cxx] key cited in the assembled text, rendered from
                                  sem7_minor/references/references.bib; an unknown key fails.
Captions must start with "Table N." or "Figure N." / "Figure N(a).". The build fails if a table
or figure is not mentioned in the BODY before it appears (image lines and other captions do not
count; CLAUDE.md writing rule), if caption numbers of a kind are not 1..n, or if first mentions
are not in numeric order. Nothing numeric is produced here; check_numbers.py audits the prose.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]          # sem8_major/
P2 = ROOT / "paper2"
TABLES = ROOT / "results" / "tables"
FIGS = ROOT / "figures"
BIB = ROOT.parent / "sem7_minor" / "references" / "references.bib"
OUT = P2 / "paper2_draft_v1.md"

PLACEHOLDER = re.compile(r"\{\{(table|figure):([A-Za-z0-9_]+)\|(.+?)\}\}", re.S)
CAPTION = re.compile(r"^(Table|Figure) (\d+)(\([a-z]\))?\.\s*")
CITE = re.compile(r"\[(C\d+(?:,\s*C\d+)*)\]")
MENTION = re.compile(r"\b(Table|Figure)s?\s+(\d+(?:\([a-z]\))?(?:(?:,|\s+and|\s*[–-])\s*\d+(?:\([a-z]\))?)*)")
NOT_BODY = re.compile(r"^(!\[.*|\*\*(Table|Figure) \d+(\([a-z]\))?\.\*\*.*)$", re.M)  # image and caption lines


def bold_caption(caption):
    m = CAPTION.match(caption)
    if not m:
        raise SystemExit(f"caption must start with 'Table N.' or 'Figure N.': {caption[:70]!r}")
    return f"**{m.group(0).strip()}** {caption[m.end():].strip()}", m


def table_block(name, caption):
    head, _ = bold_caption(caption)
    src = TABLES / f"{name}.md"
    if not src.exists():
        return (f"<!-- table:start {name} PENDING -->\n{head}\n\n> PENDING: `results/tables/{name}.md` "
                f"does not exist yet; `code/make_tables.py` writes it once the rows are merged.\n"
                f"<!-- table:end -->"), "pending"
    lines = src.read_text(encoding="utf-8").splitlines()
    if lines and lines[0].startswith("**"):
        lines = lines[1:]
    table = [l for l in lines if l.startswith("|")]
    notes = [l for l in lines if l.startswith("- ")]
    if not table:
        raise SystemExit(f"no markdown table found in {src}")
    return (f"<!-- table:start {name} -->\n{head}\n\n" + "\n".join(table) +
            "\n\nNotes:\n" + "\n".join(notes) + "\n<!-- table:end -->"), "ok"


def figure_block(name, caption):
    head, m = bold_caption(caption)
    src = FIGS / f"{name}.png"
    if not src.exists():
        raise SystemExit(f"figure missing: {src}")
    return f"<!-- figure {name} -->\n![{m.group(0).strip()}](../figures/{name}.png)\n\n{head}"


def first_mentions(text):
    """Earliest BODY position of each 'Table N' / 'Figure N' label. Image lines and caption lines
    are blanked to same-length spaces first, so an alt text or another caption never counts as a
    mention; list-style references ("Tables 6 and 7") count for each number."""
    scan = NOT_BODY.sub(lambda m: " " * len(m.group(0)), text)
    first = {}
    for m in MENTION.finditer(scan):
        for n in re.findall(r"\d+", m.group(2)):
            first.setdefault(f"{m.group(1)} {n}", m.start())
    return first


def caption_problems(text, captions):
    """captions: [(label, full)] in document order. Returns a list of problem strings."""
    first = first_mentions(text)
    out = []
    for label, full in captions:
        cap = text.find(f"**{full}.**")
        if first.get(label, cap) >= cap:
            out.append(f"{full} not mentioned in the body before its caption")
    for kind in ("Table", "Figure"):
        nums = sorted({int(l.split()[1]) for l, _ in captions if l.startswith(kind)})
        if nums != list(range(1, len(nums) + 1)):
            out.append(f"{kind} numbers are not 1..n: {nums}")
        pos = [first.get(f"{kind} {n}", -1) for n in nums]
        if any(b < a for a, b in zip(pos, pos[1:])):      # equal = one "Tables 6 and 7" phrase
            out.append(f"{kind}s are not first mentioned in numeric order (positions {pos})")
    return out


# ------------------------------------------------------------------ references (minimal parser)

def _detex(s):
    s = s.replace(r"{\ss}", "ß").replace(r"\&", "&")
    s = re.sub(r'\{\\"([aouAOU])\}', lambda m: {"a": "ä", "o": "ö", "u": "ü", "A": "Ä", "O": "Ö",
                                                  "U": "Ü"}[m.group(1)], s)
    return s.replace("{", "").replace("}", "").strip()


def parse_bib(path):
    txt = path.read_text(encoding="utf-8")
    entries = {}
    for m in re.finditer(r"@(\w+)\s*\{\s*(C\d+)\s*,", txt):
        i, depth = m.end(), 1
        while depth:                      # brace-match the entry body
            depth += {"{": 1, "}": -1}.get(txt[i], 0)
            i += 1
        body = txt[m.end():i - 1]
        fields = {}
        for fm in re.finditer(r"(\w+)\s*=\s*\{", body):
            k, d = fm.end(), 1
            while d:
                d += {"{": 1, "}": -1}.get(body[k], 0)
                k += 1
            fields[fm.group(1).lower()] = _detex(body[fm.end():k - 1])
        entries[m.group(2)] = fields
    return entries


def render_ref(key, e):
    authors = e.get("author", "").replace(" and ", ", ")
    venue = e.get("journal") or e.get("booktitle") or e.get("howpublished") or ""
    bits = [venue]
    if e.get("volume"):
        bits.append("vol. " + e["volume"] + (f"({e['number']})" if e.get("number") else ""))
    if e.get("pages"):
        bits.append("pp. " + e["pages"].replace("--", "–"))
    if e.get("year"):
        bits.append(e["year"])
    ids = []
    if e.get("doi"):
        ids.append("doi:" + e["doi"])
    if e.get("eprint"):
        ids.append("arXiv:" + e["eprint"])
    return f"- **[{key}]** {authors}. {e.get('title', '')}. {', '.join(b for b in bits if b)}. " + " · ".join(ids)


# ------------------------------------------------------------------ build

def selfcheck():
    fig = figure_block("f3_confusion_matrices", "Figure 1. See Table 1.") + "\n\n"
    caps = [("Figure 1", "Figure 1"), ("Table 1", "Table 1")]
    bad = caption_problems("Prose.\n\n" + fig + "**Table 1.** Cap.\n", caps)
    assert len(bad) == 2 and all("not mentioned" in b for b in bad), bad
    assert caption_problems("Figure 1 and Table 1.\n\n" + fig + "**Table 1.** Cap.\n", caps) == []
    # out-of-order first mentions and a numbering gap are both caught
    two = [("Table 1", "Table 1"), ("Table 2", "Table 2")]
    assert caption_problems("Tables 2 and 1.\n\n**Table 1.** A.\n\n**Table 2.** B.\n", two) == []
    assert any("numeric order" in b for b in caption_problems(
        "Table 2 first. Table 1 later.\n\n**Table 1.** A.\n\n**Table 2.** B.\n", two))
    assert any("1..n" in b for b in caption_problems("Table 1 and Table 3.\n\n**Table 1.** A.\n\n**Table 3.** B.\n",
                                                   [("Table 1", "Table 1"), ("Table 3", "Table 3")]))
    print("build_paper selfcheck OK")


def main():
    if "--selfcheck" in sys.argv:
        selfcheck()
        return
    sections = sorted((P2 / "sections").glob("*.md"))
    if not sections:
        raise SystemExit("no section files")
    text = "\n\n".join(p.read_text(encoding="utf-8").strip() for p in sections) + "\n"

    counts = {"table": 0, "pending": 0, "figure": 0}
    captions = []                         # (label, full_label) in document order

    def repl(m):
        kind, name, caption = m.group(1), m.group(2), " ".join(m.group(3).split())
        if kind == "table":
            block, status = table_block(name, caption)
            counts["pending" if status == "pending" else "table"] += 1
        else:
            block = figure_block(name, caption)
            counts["figure"] += 1
        cm = CAPTION.match(caption)
        captions.append((f"{cm.group(1)} {cm.group(2)}", f"{cm.group(1)} {cm.group(2)}{cm.group(3) or ''}"))
        return block

    text = PLACEHOLDER.sub(repl, text)
    if "{{" in text.replace("{{refs}}", ""):
        raise SystemExit("unresolved placeholder: " + text[text.index("{{"):text.index("{{") + 60])

    seen = set()
    for _, full in captions:
        if full in seen:
            raise SystemExit(f"duplicate caption label {full}")
        seen.add(full)
    problems = caption_problems(text, captions)
    if problems:
        raise SystemExit("caption check failed:\n  " + "\n  ".join(problems))

    # references
    keys = sorted({k.strip() for m in CITE.finditer(text) for k in m.group(1).split(",")},
                  key=lambda k: int(k[1:]))
    bib = parse_bib(BIB)
    missing = [k for k in keys if k not in bib]
    if missing:
        raise SystemExit(f"cited keys missing from {BIB.name}: {missing}")
    refs = "<!-- refs:start -->\n" + "\n".join(render_ref(k, bib[k]) for k in keys) + "\n<!-- refs:end -->"
    text = text.replace("{{refs}}", refs)

    header = ("<!-- Generated by paper2/build_paper.py from paper2/sections/*.md, results/tables/*.md, "
              "figures/*.png and sem7_minor/references/references.bib. Do not edit this file; edit the "
              "sections and rebuild. -->\n\n")
    OUT.write_text(header + text, encoding="utf-8", newline="\n")

    abstract = re.search(r"## Abstract\n\n(.+?)\n\n\*\*Keywords", text, re.S)
    n_abs = len(abstract.group(1).split()) if abstract else -1
    prose = re.sub(r"<!-- table:start.*?<!-- table:end -->|<!-- refs:start -->.*?<!-- refs:end -->", "",
                   text, flags=re.S)
    print(f"wrote {OUT.relative_to(ROOT)}: {len(sections)} sections, {counts['table']} tables inserted, "
          f"{counts['pending']} pending, {counts['figure']} figures, {len(keys)} references; "
          f"abstract {n_abs} words; prose+captions ~{len(prose.split()):,} words")


if __name__ == "__main__":
    main()
