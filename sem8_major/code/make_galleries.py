"""A4 Grad-CAM galleries for the five better checkpoints (implementation_plan.md 7a A4).

    python code/make_galleries.py --checkpoint-root results --data-root data/cifake \
        [--results-dir results] [--out-root figures/gradcam] [--n 8] [--seed 42] \
        [--manifest results/canonical_runs.txt] [--runs-csv results/runs.csv] \
        [--split-file data/cifake_split_seed42.csv]

Better checkpoint per backbone = the manifest row with the lower val_loss in runs.csv.
Pass 1 dumps each one's correctly classified test paths (<results-dir>/gradcam_correct/);
the intersection is sampled (seeded, n/2 real + n/2 fake) into
<results-dir>/gradcam_shared_list.txt; pass 2 builds each gallery from that shared list
(gradcam.py --shared-list), so the correct panels compare all five models on identical
images. Incorrect panels are per model - gradcam.py's own seeded sample.
"""

import argparse
import csv
import random
from pathlib import Path

import data
from eval import find_checkpoints, read_manifest
from gradcam import make_gallery


def better_checkpoints(manifest, runs_csv):
    """model -> run_id with the lower val_loss among the manifest rows."""
    ids = read_manifest(manifest)
    with open(runs_csv, newline="", encoding="utf-8") as f:
        rows = {r["run_id"]: r for r in csv.DictReader(f) if r["run_id"] in ids}
    missing = [i for i in ids if i not in rows]
    if missing:
        raise SystemExit(f"manifest ids missing from {runs_csv}: {missing}")
    best = {}
    for r in rows.values():
        m = r["model"]
        if m not in best or float(r["val_loss"]) < float(best[m]["val_loss"]):
            best[m] = r
    return {m: r["run_id"] for m, r in sorted(best.items())}


def _read_paths(path):
    return {l.strip() for l in Path(path).read_text(encoding="utf-8").splitlines() if l.strip()}


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--checkpoint-root", required=True)
    p.add_argument("--data-root", required=True)
    p.add_argument("--results-dir", default="results")
    p.add_argument("--out-root", default="figures/gradcam")
    p.add_argument("--n", type=int, default=8)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--manifest", default="results/canonical_runs.txt")
    p.add_argument("--runs-csv", default="results/runs.csv")
    p.add_argument("--split-file", default="data/cifake_split_seed42.csv")
    a = p.parse_args()

    picks = better_checkpoints(a.manifest, a.runs_csv)
    ckpts = find_checkpoints(a.checkpoint_root)
    missing = [r for r in picks.values() if r not in ckpts]
    if missing:
        raise SystemExit(f"checkpoints not found under {a.checkpoint_root}: {missing}")
    print("better checkpoint per backbone (lower val_loss):")
    for m, rid in picks.items():
        print(f"  {m:22s} {rid}")

    results_dir = Path(a.results_dir)
    dump_dir = results_dir / "gradcam_correct"
    sets = []
    for m, rid in picks.items():
        dump = dump_dir / f"{rid}.txt"
        print(f"\n=== pass 1 (correct set): {m} -> {rid}", flush=True)
        make_gallery(rid, checkpoint=ckpts[rid], results_dir=str(results_dir),
                     data_root=a.data_root, dump_correct=str(dump))
        sets.append(_read_paths(dump))
    shared = set.intersection(*sets)

    # labels from the committed split file, never parsed out of the path
    labels = dict(data._read_split(a.split_file, None)["test"])
    rng = random.Random(a.seed)
    chosen = []
    for label in (0, 1):
        cands = sorted(s for s in shared if labels[s] == label)
        chosen += rng.sample(cands, min(a.n // 2, len(cands)))
    shared_list = results_dir / "gradcam_shared_list.txt"
    shared_list.write_text("\n".join(chosen) + "\n", encoding="utf-8")
    print(f"\nshared correct set: {len(shared)} test images classified correctly by all "
          f"{len(picks)} models; sampled {len(chosen)} -> {shared_list}")

    for m, rid in picks.items():
        print(f"\n=== pass 2 (gallery): {m} -> {rid}", flush=True)
        make_gallery(rid, n=a.n, checkpoint=ckpts[rid], results_dir=str(results_dir),
                     data_root=a.data_root, out_root=a.out_root, shared_list=str(shared_list))
    print("\ndone:", ", ".join(picks.values()))


if __name__ == "__main__":
    main()
