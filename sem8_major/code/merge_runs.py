"""Merge downloaded Kaggle session results into the repo CSVs (implemented at A1).

    python code/merge_runs.py <incoming.csv> [--kind runs|crossgen] [--into path]
    python code/merge_runs.py --selfcheck

Union by key — runs: run_id; crossgen: (run_id, generator, condition). Refuses duplicate
keys (both against the existing file and within the incoming file) and refuses mismatched
headers, so a re-downloaded or already-merged file cannot silently double rows
(implementation_plan.md §7a A1.6). Nothing is ever retyped by hand.
"""

import argparse
import csv
import sys
from pathlib import Path

KEYS = {"runs": ("run_id",), "crossgen": ("run_id", "generator", "condition")}
DEFAULT_TARGET = {"runs": "results/runs.csv", "crossgen": "results/crossgen.csv"}


def _read(path):
    with open(path, newline="", encoding="utf-8") as f:
        rows = list(csv.reader(f))
    if not rows:
        return None, []
    return rows[0], rows[1:]


def merge(incoming_path, kind, into_path):
    key_cols = KEYS[kind]
    in_header, in_rows = _read(incoming_path)
    if in_header is None:
        raise SystemExit(f"REFUSED: {incoming_path} is empty")

    # smoke side-door guards: smoke_runs.csv shares runs.csv's header, so grabbing the wrong
    # downloaded file is a one-keystroke mistake — refuse it here too (§7a A1.8)
    if kind == "runs" and Path(into_path).name == "runs.csv":
        if Path(incoming_path).name == "smoke_runs.csv":
            raise SystemExit("REFUSED: smoke_runs.csv is quarantined and never merges "
                             "into runs.csv")
        if "n_train_images" in in_header:
            idx = in_header.index("n_train_images")
            rid = in_header.index("run_id")
            short = [r[rid] for r in in_rows if r[idx] and int(r[idx]) < 90000]
            if short:
                raise SystemExit(f"REFUSED: {len(short)} row(s) with n_train_images < 90000 "
                                 f"(smoke/subset rows): {short[:3]}")
    try:
        key_idx = [in_header.index(k) for k in key_cols]
    except ValueError as e:
        raise SystemExit(f"REFUSED: {incoming_path} lacks a key column: {e}")

    def key(row):
        return tuple(row[i] for i in key_idx)

    seen_in = set()
    for r in in_rows:
        if key(r) in seen_in:
            raise SystemExit(f"REFUSED: duplicate key inside {incoming_path}: {key(r)}")
        seen_in.add(key(r))

    into_path = Path(into_path)
    ex_header, ex_rows = _read(into_path) if into_path.exists() else (None, [])
    if ex_header is not None and ex_header != in_header:
        raise SystemExit(f"REFUSED: header mismatch between {incoming_path} and {into_path}")
    existing = {key(r) for r in ex_rows}
    clash = sorted(existing & seen_in)
    if clash:
        raise SystemExit(f"REFUSED: {len(clash)} key(s) already present in {into_path}: "
                         f"{clash[:5]}{'...' if len(clash) > 5 else ''}")

    into_path.parent.mkdir(parents=True, exist_ok=True)
    write_header = ex_header is None
    with into_path.open("a", newline="") as f:
        w = csv.writer(f)
        if write_header:
            w.writerow(in_header)
        w.writerows(in_rows)
    print(f"merged {len(in_rows)} row(s) from {incoming_path} into {into_path}")
    return len(in_rows)


def _selfcheck():
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        target = tmp / "runs.csv"
        (tmp / "a.csv").write_text("run_id,x\nr1,1\nr2,2\n")
        (tmp / "b.csv").write_text("run_id,x\nr3,3\n")
        (tmp / "dup.csv").write_text("run_id,x\nr2,9\n")
        (tmp / "bad.csv").write_text("run_id,y\nr9,9\n")
        assert merge(tmp / "a.csv", "runs", target) == 2
        assert merge(tmp / "b.csv", "runs", target) == 1
        assert target.read_text() == "run_id,x\nr1,1\nr2,2\nr3,3\n"
        for bad in ("dup.csv", "bad.csv"):
            try:
                merge(tmp / bad, "runs", target)
            except SystemExit as e:
                assert "REFUSED" in str(e)
            else:
                raise AssertionError(f"{bad} was accepted")
        # crossgen composite key: same run_id, different cell -> accepted
        cg = tmp / "crossgen.csv"
        (tmp / "c1.csv").write_text("run_id,generator,condition,acc\nr1,adm,down32,.9\n")
        (tmp / "c2.csv").write_text("run_id,generator,condition,acc\nr1,adm,direct224,.8\n")
        assert merge(tmp / "c1.csv", "crossgen", cg) == 1
        assert merge(tmp / "c2.csv", "crossgen", cg) == 1
        # smoke side doors: wrong-file-by-name, and subset rows by n_train_images
        target2 = tmp / "repo" / "runs.csv"  # fresh target; basename must be runs.csv for the guard
        (tmp / "smoke_runs.csv").write_text("run_id,n_train_images\ns1,400\n")
        (tmp / "subset.csv").write_text("run_id,n_train_images\nr9,400\n")
        (tmp / "full.csv").write_text("run_id,n_train_images\nr8,90000\n")
        for bad2 in ("smoke_runs.csv", "subset.csv"):
            try:
                merge(tmp / bad2, "runs", target2)
            except SystemExit as e:
                assert "REFUSED" in str(e), (bad2, e)
            else:
                raise AssertionError(f"{bad2} was merged into runs.csv")
        assert merge(tmp / "full.csv", "runs", target2) == 1
    print("merge selfcheck OK")


if __name__ == "__main__":
    if "--selfcheck" in sys.argv:
        _selfcheck()
        sys.exit(0)
    p = argparse.ArgumentParser()
    p.add_argument("incoming")
    p.add_argument("--kind", choices=["runs", "crossgen"], default="runs")
    p.add_argument("--into")
    a = p.parse_args()
    merge(a.incoming, a.kind, a.into or DEFAULT_TARGET[a.kind])
