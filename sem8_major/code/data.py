"""CIFAKE / GenImage data pipeline (implemented at A1; see implementation_plan.md §7a).

Label convention everywhere in this project: 0 = real, 1 = fake (fake is the positive class).
Run from sem8_major/ so the relative paths in configs resolve.

    make_split(cfg)          one-off, Phase 0 (done 18 Aug 2026; split file is committed)
    get_loaders(cfg)         -> (train_loader, val_loader, test_loader) for CIFAKE
    get_genimage_loader(cfg, generator, condition) -> DataLoader, cross-generator test only

    python code/data.py configs/<name>.yaml   regenerate a split (never for the committed one)
    python code/data.py --selfcheck           dataset-free checks (make_split: stdlib only;
                                              loader checks need the venv: torch + PIL)
"""

import csv
import functools
import random
from pathlib import Path

IMG_EXTS = {".jpg", ".jpeg", ".png"}  # extension filter keeps strays like Thumbs.db out
LABELS = {"real": 0, "fake": 1}
IMAGENET_MEAN = (0.485, 0.456, 0.406)
IMAGENET_STD = (0.229, 0.224, 0.225)
GENERATORS = ("midjourney", "adm", "biggan", "vqdm")


def _class_dirs(split_dir):
    """Label -> class directory. Matched case-insensitively: CIFAKE's exact REAL/FAKE
    casing was a [VERIFY] item (confirmed uppercase 18 Aug 2026), kept tolerant."""
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


def make_split(cfg, force=False):
    out = Path(cfg["data"]["split_file"])
    if out.exists() and not force:
        raise SystemExit(f"REFUSED: {out} already exists. The committed split is never "
                         "regenerated (plan 8.5) - pass --force only for a genuinely new file")
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

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
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


# --------------------------------------------------------------------------- loaders

def _read_split(split_file, smoke_subset):
    """Split name -> list of (relative_path, label). smoke_subset = images PER CLASS PER
    SPLIT, stratified first-N of the (already sorted) split file, identical everywhere."""
    rows = {"train": [], "val": [], "test": []}
    with open(split_file, newline="", encoding="utf-8") as f:
        for rec in csv.DictReader(f):
            rows[rec["split"]].append((rec["relative_path"], int(rec["label"])))
    if smoke_subset:
        for split, recs in rows.items():
            per_class = {0: [], 1: []}
            for rel, label in recs:  # recs are in sorted-path order from the committed file
                if len(per_class[label]) < smoke_subset:
                    per_class[label].append((rel, label))
            rows[split] = per_class[0] + per_class[1]
    for split, recs in rows.items():
        n0 = sum(1 for _, l in recs if l == 0)
        print(f"  {split:5s}: {n0} real / {len(recs) - n0} fake")
    return rows


class _ImageList:
    """Minimal torch Dataset over (relative_path, label) records."""

    def __init__(self, root, records, transform):
        from PIL import Image  # noqa: F401  (import check at construction, not first __getitem__)
        self.root, self.records, self.transform = Path(root), records, transform

    def __len__(self):
        return len(self.records)

    def __getitem__(self, idx):
        from PIL import Image
        rel, label = self.records[idx]
        img = Image.open(self.root / rel).convert("RGB")
        return self.transform(img), label


def _transforms(resolution, augment, force_down32=False):
    from torchvision import transforms as T
    steps = []
    if force_down32:  # cross-generator primary condition: match CIFAKE's 32px provenance
        steps.append(T.Resize((32, 32)))
    steps.append(T.Resize((resolution, resolution)))
    if augment == "hflip":
        steps.append(T.RandomHorizontalFlip())
    elif augment not in (None, "none"):
        raise ValueError(f"unknown augment: {augment!r}")
    steps += [T.ToTensor(), T.Normalize(IMAGENET_MEAN, IMAGENET_STD)]
    return T.Compose(steps)


def _seed_worker(seed, worker_id):
    # module-level (not a closure): Windows spawn pickles worker_init_fn, and closures
    # cannot be pickled — partials of module-level functions can
    import numpy as np
    random.seed(seed + worker_id)
    np.random.seed(seed + worker_id)


def _make_loader(dataset, cfg, shuffle):
    import torch
    g = torch.Generator()
    g.manual_seed(cfg["seed"])
    return torch.utils.data.DataLoader(
        dataset, batch_size=cfg["batch_size"], shuffle=shuffle,
        num_workers=cfg["data"].get("num_workers", 2),
        generator=g, worker_init_fn=functools.partial(_seed_worker, cfg["seed"]),
        pin_memory=torch.cuda.is_available())


def get_loaders(cfg):
    """(train, val, test) DataLoaders per the config. Augmentation on train only."""
    root = cfg["data"]["root"]
    rows = _read_split(cfg["data"]["split_file"], cfg.get("smoke_subset"))
    res = cfg["resolution"]
    train_tf = _transforms(res, cfg.get("augment", "none"))
    eval_tf = _transforms(res, "none")
    return (_make_loader(_ImageList(root, rows["train"], train_tf), cfg, shuffle=True),
            _make_loader(_ImageList(root, rows["val"], eval_tf), cfg, shuffle=False),
            _make_loader(_ImageList(root, rows["test"], eval_tf), cfg, shuffle=False))


def _find_generator_dir(genimage_root, generator):
    """Accepts the official GenImage conventions — imagenet_ai_<date>_<generator>/ for
    ADM/BigGAN/VQDM etc. AND the no-infix form imagenet_midjourney/ — or a plain
    <generator>/ directory (the data/README target layout). The uniqueness check below
    guards against over-matching."""
    root = Path(genimage_root)
    candidates = [d for d in root.iterdir() if d.is_dir()
                  and (d.name.lower() == generator
                       or d.name.lower().endswith("_" + generator))]
    if len(candidates) != 1:
        raise FileNotFoundError(f"expected exactly one directory for generator {generator!r} "
                                f"under {root}, found {[d.name for d in candidates]}")
    return candidates[0]


def _genimage_class_dirs(gen_dir):
    """Label -> directory. Official layout: val/{ai,nature}; target layout: {real,fake}."""
    if (gen_dir / "val").is_dir():
        return {0: gen_dir / "val" / "nature", 1: gen_dir / "val" / "ai"}
    return {0: gen_dir / "real", 1: gen_dir / "fake"}


def get_genimage_loader(cfg, generator, condition="down32"):
    """Cross-generator test loader. Never used for training. Balanced, deterministic
    (sorted paths, seeded sample), capped at genimage_per_class images per class."""
    if generator not in GENERATORS:
        raise ValueError(f"generator must be one of {GENERATORS}, got {generator!r}")
    if condition not in ("down32", "direct224"):
        raise ValueError(f"condition must be down32 or direct224, got {condition!r}")
    gen_root = cfg["data"].get("genimage_root", "data/genimage")
    per_class = cfg["data"].get("genimage_per_class", 1250)  # 2 x 1250 = 2,500 per generator
    gen_dir = _find_generator_dir(gen_root, generator)
    rng = random.Random(cfg["seed"])
    by_label = {}
    for label, class_dir in sorted(_genimage_class_dirs(gen_dir).items()):
        if not class_dir.is_dir():
            raise FileNotFoundError(f"missing class dir {class_dir}")
        by_label[label] = _list_images(class_dir, gen_dir)
    # balanced by construction: both classes capped at the SAME count, so a short class can
    # never silently skew the accuracy Paper 2's crossgen table reports
    take = min(per_class, len(by_label[0]), len(by_label[1]))
    if take < per_class:
        print(f"  WARNING: {generator} capped at {take}/class "
              f"(real {len(by_label[0])}, fake {len(by_label[1])}) - record this deviation")
    records = []
    for label in (0, 1):
        rels = by_label[label]
        records += [(r, label) for r in (rng.sample(rels, take) if take < len(rels) else rels)]
    n_fake = sum(1 for _, l in records if l == 1)
    print(f"  genimage {generator}/{condition}: {len(records) - n_fake} real / {n_fake} fake "
          f"from {gen_dir.name}")
    tf = _transforms(cfg["resolution"], "none", force_down32=(condition == "down32"))
    return _make_loader(_ImageList(gen_dir, records, tf), cfg, shuffle=False)


# --------------------------------------------------------------------------- selfchecks

def _selfcheck_split():
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for split, n in [("train", 6), ("test", 2)]:
            # one upper-case and one lower-case class dir, to exercise the casing guard
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
    print("split selfcheck OK")


def _selfcheck_loaders():
    """Needs the venv (torch, torchvision, PIL). Synthetic CIFAKE tree + synthetic
    tiny-genimage tree in the official folder convention."""
    import tempfile
    import torch
    from PIL import Image

    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        # synthetic CIFAKE: 32x32 images through split -> loaders
        for split, n in [("train", 8), ("test", 4)]:
            for cls in ("REAL", "FAKE"):
                d = tmp / "cifake" / split / cls
                d.mkdir(parents=True)
                for i in range(n):
                    Image.new("RGB", (32, 32), (i * 20 % 255, 0, 0)).save(d / f"i{i}.png")
        # num_workers=1 deliberately: proves worker_init_fn survives Windows spawn pickling
        cfg = {"seed": 42, "resolution": 64, "batch_size": 4, "augment": "hflip",
               "smoke_subset": 2,
               "data": {"root": str(tmp / "cifake"), "split_file": str(tmp / "s.csv"),
                        "num_workers": 1, "val_per_class": 3}}
        make_split(cfg)
        try:
            make_split(cfg)
        except SystemExit as e:
            assert "REFUSED" in str(e)
        else:
            raise AssertionError("make_split overwrote an existing split file")
        train, val, test = get_loaders(cfg)
        xb, yb = next(iter(train))
        assert xb.shape == (4, 3, 64, 64) and set(yb.tolist()) <= {0, 1}
        assert len(train.dataset) == 4 and len(val.dataset) == 4 and len(test.dataset) == 4

        # synthetic tiny-genimage, official convention. High-frequency noise content, not a
        # solid colour: down32 and direct224 coincide on constant images, and the selfcheck
        # must prove they differ on realistic (structured) input.
        import numpy as np
        noise = np.random.RandomState(0)

        def _fill(d, n):
            d.mkdir(parents=True)
            for i in range(n):
                arr = noise.randint(0, 255, (300, 300, 3), dtype=np.uint8)
                Image.fromarray(arr).save(d / f"g{i}.png")

        # both official naming conventions: with the ai_<date> infix and without (midjourney)
        for cls in ("ai", "nature"):
            _fill(tmp / "gen" / "imagenet_ai_0419_biggan" / "val" / cls, 4)
        _fill(tmp / "gen" / "imagenet_midjourney" / "val" / "ai", 4)
        _fill(tmp / "gen" / "imagenet_midjourney" / "val" / "nature", 2)  # short class

        cfg["data"]["genimage_root"] = str(tmp / "gen")
        cfg["data"]["genimage_per_class"] = 3
        cfg["data"]["num_workers"] = 0
        a = get_genimage_loader(cfg, "biggan", "down32")
        b = get_genimage_loader(cfg, "biggan", "down32")
        assert [r for r, _ in a.dataset.records] == [r for r, _ in b.dataset.records], \
            "genimage sampling not deterministic"
        assert len(a.dataset) == 6
        xa, _ = next(iter(a))
        xc, _ = next(iter(get_genimage_loader(cfg, "biggan", "direct224")))
        assert xa.shape[-1] == 64 and xc.shape[-1] == 64
        assert not torch.allclose(xa, xc), "down32 must differ from direct224 on high-res input"
        # no-infix dir is found; a short class caps BOTH classes (balance by construction)
        mj = get_genimage_loader(cfg, "midjourney", "down32").dataset.records
        labels = [l for _, l in mj]
        assert labels.count(0) == labels.count(1) == 2, labels
    print("loader selfcheck OK")


if __name__ == "__main__":
    import sys
    if "--selfcheck" in sys.argv:
        _selfcheck_split()
        try:
            import torch  # noqa: F401
        except ImportError:
            print("torch not available - loader selfcheck skipped (run under the venv)")
        else:
            _selfcheck_loaders()
    else:
        args = [a for a in sys.argv[1:] if a != "--force"]
        if len(args) != 1:
            sys.exit("usage: python code/data.py <config.yaml> [--force] | --selfcheck")
        import yaml
        with open(args[0], encoding="utf-8") as f:
            make_split(yaml.safe_load(f), force="--force" in sys.argv)
