"""Audit every number in the assembled Paper 2 draft against the files it must come from.

    python paper2/check_numbers.py [paper2/paper2_draft_v1.md]      (run from sem8_major/)
    python paper2/check_numbers.py --selfcheck

Rule (CLAUDE.md s6, implementation_plan.md s6): no result reaches the paper by hand. The tables are
inserted from results/tables/ by build_paper.py, so this script audits the PROSE: every numeric
token must be (a) a value in a generated table or a committed results CSV (smoke_runs.csv and
calibration.csv excluded), any half-to-even rounding of it, or its percent form if it is a
fraction, (b) a quantity derived from those files in this script, with the formula in code, or
(c) an allow-listed external fact whose source is written beside it. Anything else is printed
with its line and the run exits 1. Skipped on purpose: inserted tables, the reference list,
headings, HTML comments, code spans, citation keys, Table/Figure/Section references, equation
labels, the project's citation years 2019-2026, dates, version strings (checked separately
against the logged versions) and identifiers such as ViT-B/16 or CIFAR-10.

ponytail: a regex scan, not a parser. A pass means every token coincides with some logged value or
a rounding of one, not that it is the right value for its sentence. Not caught: integers 0-10
(exempt), integers up to 50 (they coincide with epoch indices) and most one- or two-decimal
fractions and percentages (the learning curves and confusion matrices supply hundreds of values).
Caught: a table-specific value wrong in its last printed digit, e.g. 324.4 for 323.4 min, 18,663
for 18,662 images, 23.4 for 23.3 GPU-hours. Those other classes stay a reading check against
results/tables/.
"""

import csv
import math
import re
import sys
from decimal import Decimal, ROUND_HALF_EVEN, InvalidOperation
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]          # sem8_major/
RES = ROOT / "results"
DRAFT = ROOT / "paper2" / "paper2_draft_v1.md"

LOOSE = re.compile(r"\d+(?:\.\d+)?")                 # harvesting known values from files
VERSION = re.compile(r"\b\d+\.\d+\.\d+(?:\+\w+)?\b")  # 2.10.0+cu128, 1.0.26, 3.12.13
# prose: a number not glued to letters, '-', '/', '_' or '.' (ViT-B/16, CIFAR-10, seed42, v1.4)
STRICT = re.compile(r"(?<![A-Za-z0-9_./\-])(\d[\d,]*(?:\.\d+)?)(?![A-Za-z0-9_])")
REFLIKE = re.compile(r"\b(?:Sections?|Tables?|Figures?|Fig\.)\s+\d+(?:\.\d+)?(?:\([a-z]\))?"
                     r"(?:(?:,|\s+and|\s*[–-])\s*\d+(?:\.\d+)?(?:\([a-z]\))?)*")
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"

# (c) external facts: token -> source. Everything else must come from a file or a formula.
ALLOW = {
    "0.5": "chance level and the decision threshold (code/eval.py)",
    "32": "CIFAKE native resolution [C51]; plan s3",
    "16": "ViT-B/16 patch size [C70]; also the dev laptop's 16 GB RAM (plan Table 1)",
    "2000": "planned images per generator, plan s3", "3000": "planned images per generator, plan s3",
    "1250": "genimage_per_class default, code/data.py",
    "2.3": "thirteen best.pt files, 2,286,294,747 bytes, measured 17 Oct 2026 (derived when the files are present)",
    "2.1": "ten canonical best.pt files, 2,081,276,892 bytes, measured 17 Oct 2026 (derived when present)",
    "4.0": "CC BY-NC-SA licence version, data/genimage_access_note.md",
    "48": "companion review s6.1: primary studies", "36": "companion review s6.1: cross-generator tested",
    "90.8": "[C01]", "15.2": "[C23]", "99.9": "[C52]", "54.9": "[C52]", "92.77": "[C36]", "65.77": "[C36]",
    "95.6": "[C11]", "0.9": "[C03] AUC above 0.9 (also SGD momentum in the configs)",
    "60": "[C24]", "76": "[C24]", "50": "[C24]", "61": "[C24]",
    "81.1": "[C44]", "47.0": "[C44]", "57.0": "[C44]", "62.0": "[C44]", "71.68": "[C31]", "82.74": "[C31]",
}

known, versions = set(), set()


def fmt(d):
    s = format(d, "f")
    return s.rstrip("0").rstrip(".") if "." in s else s


def add(value):
    """Register a value with every rounding a careful writer might print (half-to-even, 0-4 dp)
    and, for a fraction in [0, 1], its percent forms at 0-2 dp."""
    try:
        d = Decimal(str(value).replace(",", ""))
    except InvalidOperation:
        return
    if not d.is_finite():
        return
    known.add(fmt(d))
    for p in range(5):
        known.add(fmt(d.quantize(Decimal(1).scaleb(-p), rounding=ROUND_HALF_EVEN)))
    if 0 <= d <= 1:
        for p in range(3):
            known.add(fmt((d * 100).quantize(Decimal(1).scaleb(-p), rounding=ROUND_HALF_EVEN)))


def harvest_text(txt):
    versions.update(VERSION.findall(txt))
    for t in LOOSE.findall(txt):
        add(t)


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def is_num(s):
    try:
        return Decimal(s).is_finite()
    except InvalidOperation:
        return False


def harvest_csv(path, pairwise=False):
    rows = read_csv(path)
    for r in rows:
        for v in r.values():
            versions.update(VERSION.findall(v or ""))
            for t in LOOSE.findall(v or ""):
                add(t)
    if pairwise:                           # differences a reader can form from the printed table
        for col in rows[0].keys():
            vals = [Decimal(r[col]) for r in rows if is_num(r[col] or "")]
            for i in range(len(vals)):
                for j in range(i + 1, len(vals)):
                    add(abs(vals[i] - vals[j]))
    return rows


def build_known():
    # printed tables; pairwise differences only where the prose forms them (t1 / t1b)
    for p in sorted((RES / "tables").glob("*.csv")):
        harvest_csv(p, pairwise=p.name.startswith(("t1_", "t1b_")))
    runs = harvest_csv(RES / "runs.csv")
    harvest_csv(RES / "crossgen.csv")
    harvest_csv(RES / "genimage_verification.csv")
    # smoke_runs.csv is quarantined (plan s7a): its metrics must never reach the paper, so only its
    # version strings (the laptop's torch/timm builds) count. calibration.csv is not reported at all.
    versions.update(VERSION.findall((RES / "smoke_runs.csv").read_text(encoding="utf-8")))
    versions.update(VERSION.findall((ROOT / "requirements.lock").read_text(encoding="utf-8")))
    # kaggle_env.md: the hardware bullets, lscpu/free lines and package list are quotable facts;
    # the nvidia-smi dump below them (driver, watts, temperature, MiB) has no reporting role.
    harvest_text((RES / "kaggle_env.md").read_text(encoding="utf-8").split("## nvidia-smi")[0])
    for p in sorted((ROOT / "configs").glob("*.yaml")):
        if "smoke" not in p.name:
            harvest_text(p.read_text(encoding="utf-8"))

    # committed split: per (split, label) counts and the totals a reader would form
    split = read_csv(ROOT / "data" / "cifake_split_seed42.csv")
    by = {}
    for r in split:
        by[(r["split"], r["label"])] = by.get((r["split"], r["label"]), 0) + 1
    for n in by.values():
        add(n)
    per_split = {s: sum(n for (sp, _), n in by.items() if sp == s) for s in ("train", "val", "test")}
    for n in per_split.values():
        add(n)
    add(len(split)); add(per_split["train"] + per_split["val"]); add(len(split) // 2)
    add((per_split["train"] + per_split["val"]) // 2)
    n_test = per_split["test"]

    canon = [l.strip() for l in (RES / "canonical_runs.txt").read_text(encoding="utf-8").splitlines()
             if l.strip() and not l.startswith("#")]
    rows = {r["run_id"]: r for r in runs}
    for rid in canon:
        r = rows[rid]
        # derived: binomial standard error of the test accuracy, in percentage points, and the
        # standard error of a difference of two such accuracies treated as independent (x sqrt 2)
        p = float(r["test_acc"])
        se = 100 * math.sqrt(p * (1 - p) / n_test)
        add(round(se, 4)); add(round(se * math.sqrt(2), 4))
        add(round(int(r["total_params"]) / 1e6, 1))               # parameters in millions
        add(int(r["trainable_params"]) // 2 - 1)                   # head input width under fe
        # learning curve: epochs, values, deltas and the train/val gap at the kept epoch
        curve = read_csv(RES / rid / "learning_curve.csv")
        for c in curve:
            for v in c.values():
                add(v)
        vl = [Decimal(c["val_loss"]) for c in curve]
        va = [Decimal(c["val_acc"]) for c in curve]
        if len(curve) >= 50:
            add(vl[29] - vl[39]); add(vl[39] - vl[49])
            add(min(va[40:50])); add(max(va[40:50]))
        b = int(r["best_epoch"]) - 1
        add((Decimal(curve[b]["train_acc"]) - Decimal(curve[b]["val_acc"])) * 100)
        # confusion matrix cells and the number of correct test images
        cm = read_csv(RES / rid / "confusion_matrix.csv")
        for c in cm:
            for v in c.values():
                add(v)
        add(int(cm[0]["pred_real"]) + int(cm[1]["pred_fake"]))
    # derived totals: GPU time of the canonical and the superseded rows, in minutes and hours
    canon_min = sum(Decimal(rows[rid]["train_time_min"]) for rid in canon)
    sup_min = sum(Decimal(r["train_time_min"]) for r in runs if r["run_id"] not in canon)
    for m in (canon_min, sup_min, canon_min + sup_min):
        add(m); add(m / 60)
    # cross-generator bookkeeping and the shared Grad-CAM set
    cg = read_csv(RES / "crossgen.csv")
    add(len(cg)); add(len(cg) // 2); add(sum(int(r["n_real"]) + int(r["n_fake"]) for r in cg))
    sets = [set(p.read_text(encoding="utf-8").split("\n")) - {""} for p in (RES / "gradcam_correct").glob("*.txt")]
    if sets:
        add(len(set.intersection(*sets)))
        for s in sets:
            add(len(s))
    add(Decimal(100) / n_test)                                     # accuracy granularity, pct points
    add(224 // 16); add((224 // 16) ** 2)                          # ViT patch grid
    # checkpoint archive sizes in GB (local files; the ALLOW entries carry the measured values)
    ckpts = list(RES.glob("*/best.pt"))
    if ckpts:
        add(round(sum(p.stat().st_size for p in ckpts) / 1e9, 1))
        add(round(sum(p.stat().st_size for p in ckpts if p.parent.name in canon) / 1e9, 1))


def prose_tokens(text):
    text = re.sub(r"<!-- table:start.*?<!-- table:end -->", "", text, flags=re.S)
    text = re.sub(r"<!-- refs:start -->.*?<!-- refs:end -->", "", text, flags=re.S)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    text = re.sub(r"`[^`\n]*`", "", text)
    text = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(r"\[C\d+(?:,\s*C\d+)*\]", "", text)
    text = REFLIKE.sub("", text)
    text = re.sub(rf"\b\d{{1,2}} (?:{MONTHS})\b(?: (?:2019|202[0-6]))?", "", text)
    text = re.sub(r"\b(?:2019|202[0-6])\b", "", text)            # citation years only
    out = []
    for ln, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("#"):
            continue
        for v in VERSION.findall(line):
            out.append((ln, v, line.strip(), "version"))
        line = VERSION.sub("", line)
        for m in STRICT.finditer(line):
            out.append((ln, m.group(1).replace(",", ""), line.strip(), "number"))
    return out


def audit(text):
    bad = []
    allow = {fmt(Decimal(k)) for k in ALLOW}
    for ln, tok, ctx, kind in prose_tokens(text):
        if kind == "version":
            if tok not in versions:
                bad.append((ln, tok, ctx))
            continue
        tok = fmt(Decimal(tok))             # "97.60" and "97.6" are the same printed value
        if tok in known or tok in allow:
            continue
        if re.fullmatch(r"\d+", tok) and int(tok) <= 10:
            continue
        bad.append((ln, tok, ctx))
    return bad


def main():
    if "--selfcheck" in sys.argv:
        build_known()
        sample = ("ViT-B/16 reached 98.88% while a made-up 12345.678 and torch 9.9.9 must fail; "
                  "Table 3 and Section 3.7 and [C51] and 2026 and `seed42` are skipped.")
        bad = audit(sample)
        assert [b[1] for b in bad] == ["9.9.9", "12345.678"], bad
        assert not audit("fine-tuning added 3.5 to 7.4 points; 18,662 images; 23.3 GPU-hours; "
                         "a pooled feature of 2048 values; 2.3 GB of checkpoints")
        for s in ("18,663 images", "324.4 minutes", "23.4 GPU-hours", "a pooled feature of 2049 values"):
            assert audit(s), f"near miss not caught: {s}"      # the class of error this does catch
        assert audit("the smoke run reached 79.25% test accuracy"), "smoke metrics must not count as a source"
        print("check_numbers selfcheck OK")
        return
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DRAFT
    build_known()
    text = path.read_text(encoding="utf-8")
    bad = audit(text)
    n = len(prose_tokens(text))
    if bad:
        print(f"{len(bad)} of {n} numeric tokens in {path.name} have no source:")
        for ln, tok, ctx in bad:
            print(f"  line {ln}: {tok!r:14s} | {ctx[:110]}")
        sys.exit(1)
    print(f"check_numbers OK: {n} numeric tokens in {path.name}; each coincides with a table or CSV value, "
          f"a rounding of one, a derived quantity or an allow-listed source (what this does not prove: see docstring)")


if __name__ == "__main__":
    main()
