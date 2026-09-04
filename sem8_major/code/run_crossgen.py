"""A4 cross-generator sweep: every canonical checkpoint x 4 generators x 2 conditions,
evaluation only, no training (implementation_plan.md 7a A4).

    python code/run_crossgen.py --checkpoint-root /kaggle/input --genimage-root <dir> \
        --results-dir /kaggle/working/results [--manifest results/canonical_runs.txt]

Step 1 records what tiny-genimage actually contains - per-generator val counts, file formats
and image sizes -> <results-dir>/genimage_verification.csv - closing the A1 [VERIFY] and
exposing any JPEG-vs-PNG asymmetry between ai and nature (itself a detectable cue; a stated
caveat in Paper 2 if present). Step 2 runs one eval.py subprocess per cell, failure-isolated
like run_session.py; cells already in <results-dir>/crossgen.csv are skipped, so an
interrupted sweep resumes instead of double-appending.
"""

import argparse
import csv
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

import data
from eval import find_checkpoints, read_manifest

CONDITIONS = ("down32", "direct224")
VERIFY_COLUMNS = ["dir_name", "target", "n_ai", "n_nature", "ai_ext", "nature_ext",
                  "ai_size_first20", "nature_size_first20"]


def verify_genimage(genimage_root, out_csv):
    """One row per directory under the GenImage root; 'target' names our generator when the
    directory is one of the four we evaluate on (matched like data._find_generator_dir)."""
    from PIL import Image
    rows = []
    for d in sorted(p for p in Path(genimage_root).iterdir() if p.is_dir()):
        name = d.name.lower()
        row = {"dir_name": d.name,
               "target": next((g for g in data.GENERATORS
                               if name == g or name.endswith("_" + g)), "")}
        class_dirs = data._genimage_class_dirs(d)
        for label, cls in ((1, "ai"), (0, "nature")):
            cd = class_dirs[label]
            files = (sorted(p for p in cd.rglob("*") if p.suffix.lower() in data.IMG_EXTS)
                     if cd.is_dir() else [])
            row[f"n_{cls}"] = len(files)
            row[f"{cls}_ext"] = " ".join(f"{e}:{n}" for e, n in
                                         sorted(Counter(p.suffix.lower() for p in files).items()))
            sizes = Counter()
            for p in files[:20]:
                with Image.open(p) as im:
                    sizes[f"{im.width}x{im.height}"] += 1
            row[f"{cls}_size_first20"] = " ".join(f"{s}:{n}" for s, n in sizes.most_common(3))
        rows.append(row)
    out_csv = Path(out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=VERIFY_COLUMNS)
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print(f"  {r['dir_name']:32s} target={r['target'] or '-':10s} "
              f"ai={r['n_ai']} ({r['ai_ext']}) nature={r['n_nature']} ({r['nature_ext']})")
    return rows


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--checkpoint-root", required=True)
    p.add_argument("--genimage-root", required=True)
    p.add_argument("--results-dir", default="results")
    p.add_argument("--manifest", default="results/canonical_runs.txt")
    p.add_argument("--python", default=sys.executable)
    a = p.parse_args()

    results_dir = Path(a.results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    print("tiny-genimage contents:")
    verify_genimage(a.genimage_root, results_dir / "genimage_verification.csv")

    run_ids = read_manifest(a.manifest)
    ckpts = find_checkpoints(a.checkpoint_root)
    missing = [r for r in run_ids if r not in ckpts]
    if missing:
        raise SystemExit(f"checkpoints not found under {a.checkpoint_root}: {missing}")

    done = set()
    cg = results_dir / "crossgen.csv"
    if cg.exists():
        with cg.open(newline="", encoding="utf-8") as f:
            done = {(r["run_id"], r["generator"], r["condition"]) for r in csv.DictReader(f)}

    code_dir = Path(__file__).resolve().parent
    results = []
    for rid in run_ids:
        for gen in data.GENERATORS:
            for cond in CONDITIONS:
                if (rid, gen, cond) in done:
                    print(f"skip (already in crossgen.csv): {rid} {gen} {cond}")
                    continue
                cmd = [a.python, str(code_dir / "eval.py"), "--run-id", rid,
                       "--dataset", "genimage", "--generator", gen, "--condition", cond,
                       "--checkpoint", str(ckpts[rid]), "--results-dir", str(results_dir),
                       "--genimage-root", a.genimage_root]
                print(f"\n=== {rid} | {gen} | {cond}", flush=True)
                t0 = time.time()
                rc = subprocess.call(cmd)
                results.append((rid, gen, cond, rc, (time.time() - t0) / 60))

    print(f"\n{'=' * 70}\nCROSSGEN SUMMARY ({len(results)} cells run, {len(done)} skipped)\n{'=' * 70}")
    for rid, gen, cond, rc, mins in results:
        print(f"  {'OK    ' if rc == 0 else 'FAILED'}  {mins:5.1f} min  {rid} {gen} {cond}")
    failed = [(r, g, c) for r, g, c, rc, _ in results if rc != 0]
    if failed:
        print(f"\n{len(failed)} cell(s) failed: {failed}")
        print("Completed cells are valid; rerun this command to fill the gaps.")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
