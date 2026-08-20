"""CIFAKE / GenImage data pipeline. make_split is implemented (Phase 0); the loaders are
stubs until Phase 1.

Label convention everywhere in this project: 0 = real, 1 = fake (fake is the positive class).

Contract:

    make_split(cfg)
        One-off, Phase 0. Run directly: python code/data.py configs/template.yaml
        (or --selfcheck for the no-dataset self-test). Carves a 10,000-image stratified
        validation set out of CIFAKE's 100,000-image train set with seed 42 and writes
        cfg["data"]["split_file"] (CSV: relative_path,label,split — relative filenames only,
        never indices, because directory enumeration order differs between Windows and Kaggle
        Linux). The official 20,000-image test set is never touched. The split file is
        committed, so every run uses the identical split.

    get_loaders(cfg) -> (train_loader, val_loader, test_loader)
        Reads cfg: data.root, data.split_file, data.num_workers, resolution, batch_size,
        augment, seed, smoke_subset. CIFAKE images are 32x32; they are resized to
        cfg["resolution"] (224) and normalised with ImageNet statistics, because the
        backbones are ImageNet-pretrained. Augmentation applies to the train split only.

    get_genimage_loader(cfg, generator, condition) -> DataLoader
        Test-only, cross-generator. generator in {midjourney, adm, biggan, vqdm}.
        condition "down32" (primary: resize to 32x32 first, then through the same
        32->224 path as CIFAKE, so the generator is the only varying factor) or
        "direct224" (secondary sensitivity check on resolution artefacts).
"""


import csv
import random
from pathlib import Path

IMG_EXTS = {".jpg", ".jpeg", ".png"}  # extension filter keeps strays like Thumbs.db out
LABELS = {"real": 0, "fake": 1}


def _class_dirs(split_dir):
    """Label -> class directory. Matched case-insensitively: CIFAKE's exact REAL/FAKE
    casing is a [VERIFY] item (see data/README.md), so nothing here assumes it."""
    found = {}
    for d in split_dir.iterdir():
        if d.is_dir() and d.name.lower() in LABELS:
            found[LABELS[d.name.lower()]] = d
    if sorted(found) != [0, 1]:
        raise FileNotFoundError(f"expected one real and one fake dir under {split_dir}, "
                                f"found {[d.name for d in split_dir.iterdir() if d.is_dir()]}")
    return found


def _list_images(class_dir, root):
    rels = [p.relative_to(root).as_posix()  # forward slashes: file must be identical cross-OS
            for p in class_dir.rglob("*") if p.suffix.lower() in IMG_EXTS]
    if not rels:
        raise FileNotFoundError(f"no images under {class_dir}")
    return sorted(rels)  # sorted, never enumeration order


def make_split(cfg):
    root = Path(cfg["data"]["root"])
    val_per_class = cfg["data"].get("val_per_class", 5000)  # 2 x 5000 = the plan's 10k val set
    rng = random.Random(cfg["seed"])
    rows = []
    for label, class_dir in sorted(_class_dirs(root / "train").items()):  # fixed label order:
        rels = _list_images(class_dir, root)             # rng state must not depend on dir order
        if len(rels) <= val_per_class:
            raise ValueError(f"{class_dir}: only {len(rels)} images, need > {val_per_class}")
        rng.shuffle(rels)
        rows += [(r, label, "val") for r in rels[:val_per_class]]
        rows += [(r, label, "train") for r in rels[val_per_class:]]
    for label, class_dir in sorted(_class_dirs(root / "test").items()):
        rows += [(r, label, "test") for r in _list_images(class_dir, root)]
    rows.sort()

    out = Path(cfg["data"]["split_file"])
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["relative_path", "label", "split"])
        w.writerows(rows)

    counts = {}
    for _, label, split in rows:
        counts[(split, label)] = counts.get((split, label), 0) + 1
    print(f"wrote {out} ({len(rows)} rows)")
    for (split, label), n in sorted(counts.items()):
        print(f"  {split:5s} label={label} ({'real' if label == 0 else 'fake'}): {n}")
    print("expected for full CIFAKE: train 45000/45000, val 5000/5000, test 10000/10000")
    return out


def get_loaders(cfg):
    raise NotImplementedError("Phase 0/1 implements this — see implementation_plan.md")


def get_genimage_loader(cfg, generator, condition="down32"):
    raise NotImplementedError("Phase 0/1 implements this — see implementation_plan.md")


def _selfcheck():
    """Runs make_split twice on a synthetic mini-CIFAKE and asserts determinism, stratified
    counts, cross-OS path format, and junk-file exclusion. Needs no dataset and no deps."""
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for split, n in [("train", 6), ("test", 2)]:
            # one upper-case and one lower-case class dir, to exercise the [VERIFY] casing guard
            for cls in ("REAL", "fake"):
                d = tmp / "cifake" / split / cls
                d.mkdir(parents=True)
                for i in range(n):
                    (d / f"img_{i}.jpg").touch()
        (tmp / "cifake" / "train" / "REAL" / "Thumbs.db").touch()  # must be excluded

        outs = []
        for name in ("a.csv", "b.csv"):
            cfg = {"seed": 42, "data": {"root": str(tmp / "cifake"),
                                        "split_file": str(tmp / name), "val_per_class": 2}}
            make_split(cfg)
            outs.append((tmp / name).read_bytes())
        assert outs[0] == outs[1], "same seed produced different splits"

        text = outs[0].decode()
        assert "\\" not in text and "Thumbs.db" not in text
        rows = [line.split(",") for line in text.strip().splitlines()[1:]]
        got = {}
        for _, label, split in rows:
            got[(split, label)] = got.get((split, label), 0) + 1
        assert got == {("train", "0"): 4, ("train", "1"): 4, ("val", "0"): 2, ("val", "1"): 2,
                       ("test", "0"): 2, ("test", "1"): 2}, got
    print("selfcheck OK")


if __name__ == "__main__":
    import sys
    if "--selfcheck" in sys.argv:
        _selfcheck()
    elif len(sys.argv) == 2:
        import yaml
        with open(sys.argv[1]) as f:
            make_split(yaml.safe_load(f))
    else:
        sys.exit("usage: python code/data.py <config.yaml> | --selfcheck")
