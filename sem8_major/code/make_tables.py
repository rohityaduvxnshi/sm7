"""Generate every Paper 2 table from the result CSVs (implementation_plan.md 7a A6).

    python code/make_tables.py                 # writes results/tables/*.csv and .md twins
    python code/make_tables.py --selfcheck

Inputs, and nothing else: results/runs.csv filtered through results/canonical_runs.txt,
results/crossgen.csv, the per-run artefact files (learning_curve.csv, confusion_matrix.csv,
config_used.yaml, genimage_<gen>_<cond>/confusion_matrix.csv), results/genimage_verification.csv
and the config YAMLs. No number is typed by hand: every value in results/tables/ is read from
those files and rounded by the ONE function below (rnd), whose rule is printed in each table's
footer. Fails loudly (plan 7a A6) if a manifest run_id is missing from runs.csv, a (model, mode)
in runs.csv has no manifest entry, any runs.csv row lacks its config_used.yaml, a config YAML no
longer says what its run actually used, or crossgen.csv is not the exact manifest x generator x
condition product.

Rows in runs.csv that are not in the manifest are classified from their config_used.yaml:
identical to the canonical (model, mode) row except the epoch budget -> a superseded rerun
(listed only in t1b, plan 10); any other difference -> an ablation variant (t6, plan 4).

Tables: t1 CIFAKE test metrics, t1b convergence reruns, t2 model size and cost, t3a/t3b
cross-generator accuracy/AUC, t3c cross-generator summary statistics (the numbers Paper 2's
cross-generator paragraph quotes), t4 hyperparameters (values and one-line justifications from
the YAML comments, one row per distinct value), t5 tiny-genimage composition, t6 ablations
(only once variant rows exist).
"""

import argparse
import re
import sys
import tempfile
from decimal import Decimal, ROUND_HALF_EVEN
from pathlib import Path

import pandas as pd
import yaml

from data import GENERATORS
from eval import read_manifest
from run_crossgen import CONDITIONS

MODES = ("fe", "ft")
MODEL_LABEL = {"resnet50": "ResNet50", "densenet121": "DenseNet121",
               "efficientnet_b0": "EfficientNet-B0", "vgg19": "VGG19",
               "vit_base_patch16_224": "ViT-B/16"}
MODE_NOTE = ("fe = feature extraction (backbone frozen, new 2-class head trained); "
             "ft = fine-tuning (every parameter updated)")
ROUNDING_RULE = ("a value is the string logged in the CSV (runs.csv metrics carry six decimals, "
                 "crossgen.csv the full float repr), rounded half-to-even on that decimal value - "
                 "e.g. test_acc 0.928650 -> 92.86 %, 0.934850 -> 93.48 %, AUC 0.980733 -> 0.9807")
# config_used.yaml keys a rerun may legitimately change (plan 10: only the epoch budget) or that
# are run metadata; any OTHER key differing from the canonical row marks an ablation variant
_RUN_META = {"run_id", "cli_overrides", "n_train_images", "device", "output", "max_epochs",
             "time_budget_min", "tag", "smoke_subset"}
_DATA_META = {"root", "num_workers"}
_HPARAM_KEYS = ("resolution", "batch_size", "augment", "optimizer", "lr", "momentum",
                "weight_decay", "max_epochs", "early_stopping_patience", "amp", "checkpoint",
                "seed")


def rnd(x, nd):
    """The one rounding function. x: CSV string, Decimal or number. Returns a string so that
    trailing zeros survive (0.9800 stays 0.9800) and the same value always prints the same."""
    d = x if isinstance(x, Decimal) else Decimal(str(x))
    return str(d.quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_EVEN))


def pct(x, nd=2):
    return rnd(Decimal(str(x)) * 100, nd)


def _mean(values):
    values = [Decimal(str(v)) for v in values]
    return sum(values) / len(values)


def _read_csv(path):
    return pd.read_csv(path, dtype=str, keep_default_na=False)


# ----------------------------------------------------------------------------- loading
def load_runs(results):
    """(all runs.csv rows, canonical rows in paper order). Fails loudly per plan 7a A6."""
    runs = _read_csv(results / "runs.csv")
    ids = read_manifest(results / "canonical_runs.txt")
    missing = sorted(set(ids) - set(runs["run_id"]))
    if missing:
        raise SystemExit(f"manifest run_id(s) missing from runs.csv: {missing}")
    canon = runs[runs["run_id"].isin(ids)].copy()
    pairs = canon.groupby(["model", "mode"]).size()
    dups = [k for k, n in pairs.items() if n > 1]
    if dups:
        raise SystemExit(f"manifest lists more than one run for (model, mode): {dups}")
    no_entry = sorted(set(map(tuple, runs[["model", "mode"]].values)) - set(pairs.index))
    if no_entry:
        raise SystemExit(f"(model, mode) in runs.csv without a manifest entry: {no_entry}")
    unknown = sorted(set(canon["model"]) - set(MODEL_LABEL))
    if unknown:
        raise SystemExit(f"model(s) without a paper label in MODEL_LABEL: {unknown}")
    order = {(m, md): i for i, (m, md) in enumerate((m, md) for m in MODEL_LABEL for md in MODES)}
    canon["_order"] = [order[(m, md)] for m, md in zip(canon["model"], canon["mode"])]
    canon = canon.sort_values("_order").drop(columns="_order").reset_index(drop=True)
    return runs, canon


def _used_cfg(results, run_id):
    """The resolved config the run actually trained with (written by train.py)."""
    p = results / run_id / "config_used.yaml"
    if not p.exists():
        raise SystemExit(f"{p} missing: every runs.csv row needs its artefact dir")
    return yaml.safe_load(p.read_text(encoding="utf-8"))


def _hparams(results, run_id):
    cfg = _used_cfg(results, run_id)
    cfg["data"] = {k: v for k, v in cfg["data"].items() if k not in _DATA_META}
    return {k: v for k, v in cfg.items() if k not in _RUN_META}


def classify_extra_rows(results, runs, canon):
    """run_id -> ('superseded' | 'variant', description) for every non-manifest row."""
    by_pair = {(r["model"], r["mode"]): r for _, r in canon.iterrows()}
    out = {}
    for _, r in runs[~runs["run_id"].isin(canon["run_id"])].iterrows():
        c = by_pair[(r["model"], r["mode"])]
        a, b = _hparams(results, c["run_id"]), _hparams(results, r["run_id"])
        diff = {k: (a.get(k), b.get(k)) for k in sorted(set(a) | set(b)) if a.get(k) != b.get(k)}
        if diff:
            out[r["run_id"]] = ("variant", "; ".join(f"{k}: {x} -> {y}" for k, (x, y) in diff.items()))
        elif r["max_epochs"] != c["max_epochs"]:
            out[r["run_id"]] = ("superseded", f"max_epochs {r['max_epochs']} -> {c['max_epochs']}")
        else:
            raise SystemExit(f"{r['run_id']} is identical to canonical {c['run_id']} (same config, "
                             "same epoch budget): list it in the manifest or remove it")
    return out


def load_crossgen(results, canon):
    """crossgen.csv rows for the manifest checkpoints; must be the exact product, once each."""
    cg = _read_csv(results / "crossgen.csv")
    cg = cg[cg["run_id"].isin(canon["run_id"])].reset_index(drop=True)
    key = ["run_id", "generator", "condition"]
    dup = cg[cg.duplicated(key)]
    if len(dup):
        raise SystemExit(f"crossgen.csv has duplicate cell row(s): {sorted(map(tuple, dup[key].values))}")
    expected = {(rid, g, c) for rid in canon["run_id"] for g in GENERATORS for c in CONDITIONS}
    have = set(map(tuple, cg[key].values))
    if have != expected:
        raise SystemExit("crossgen.csv is not the manifest x generator x condition product; "
                         f"missing {sorted(expected - have)}, unexpected {sorted(have - expected)}")
    sizes = set(zip(cg["n_real"], cg["n_fake"]))
    if len(sizes) != 1:
        raise SystemExit(f"cross-generator cells differ in size: {sizes}")
    (n_real, n_fake), = sizes
    return cg, int(n_real), int(n_fake)


def cell(cg, run_id, generator, condition):
    rows = cg[(cg["run_id"] == run_id) & (cg["generator"] == generator) & (cg["condition"] == condition)]
    return rows.iloc[0]


def read_cm(path):
    """2x2 confusion matrix as written by eval.py: rows true real/fake, cols pred real/fake."""
    cm = pd.read_csv(path, index_col=0)
    if list(cm.index) != ["true_real", "true_fake"] or list(cm.columns) != ["pred_real", "pred_fake"]:
        raise SystemExit(f"unexpected confusion-matrix layout in {path}")
    return cm.values.astype(int)


def test_set_size(results, canon):
    """Number of CIFAKE test images, from the confusion matrices; must agree across the runs."""
    n = {int(read_cm(results / rid / "confusion_matrix.csv").sum()) for rid in canon["run_id"]}
    if len(n) != 1:
        raise SystemExit(f"canonical runs evaluated different test-set sizes: {n}")
    return n.pop()


# ----------------------------------------------------------------------------- writing
def _md(df):
    cols = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "|".join(["---"] * len(cols)) + "|"]
    lines += ["| " + " | ".join(str(v).replace("|", "/") for v in row) + " |"
              for row in df.itertuples(index=False)]
    return "\n".join(lines)


def write_table(out, name, df, notes):
    out.mkdir(parents=True, exist_ok=True)
    foot = [f"Rounding: {ROUNDING_RULE}.",
            "Generated by code/make_tables.py from the files named above; nothing typed by hand."]
    body = "\n".join(f"- {n}" for n in list(notes) + foot)
    # newline="\n": byte-identical output on Windows and Linux (gate G6 compares bytes)
    (out / f"{name}.csv").write_text(df.to_csv(index=False, lineterminator="\n"), encoding="utf-8",
                                     newline="\n")
    (out / f"{name}.md").write_text(f"**{name}**\n\n{_md(df)}\n\n{body}\n", encoding="utf-8",
                                    newline="\n")
    print(f"  wrote {name}.csv / .md ({len(df)} rows)")


# ----------------------------------------------------------------------------- tables
def t1(results, canon):
    n = test_set_size(results, canon)
    # accuracy = correct / n is a multiple of 100/n %, so exact ties at the third decimal are
    # structural, not rare; count them so the footer says how many rows the rule decided
    ties = sum((Decimal(v) * 100 * 100) % 1 == Decimal("0.5") for v in canon["test_acc"])
    patience = {_used_cfg(results, rid)["early_stopping_patience"] for rid in canon["run_id"]}
    if len(patience) != 1:
        raise SystemExit(f"canonical runs used different early-stopping patience: {patience}")
    df = pd.DataFrame({
        "model": canon["model"].map(MODEL_LABEL), "mode": canon["mode"],
        "run_id": canon["run_id"], "best_epoch": canon["best_epoch"],
        "max_epochs": canon["max_epochs"], "stop_reason": canon["stop_reason"],
        "val_acc_pct": canon["val_acc"].map(pct), "test_acc_pct": canon["test_acc"].map(pct),
        "precision_pct": canon["test_precision"].map(pct),
        "recall_pct": canon["test_recall"].map(pct), "f1_pct": canon["test_f1"].map(pct),
        "auc": canon["test_auc"].map(lambda v: rnd(v, 4)),
        "ap": canon["test_ap"].map(lambda v: rnd(v, 4))})
    notes = [f"Source: results/runs.csv rows listed in results/canonical_runs.txt; CIFAKE test "
             f"split of {n:,} images (from each run's confusion_matrix.csv), never used "
             "for training or model selection; val_acc is at the kept (best validation-loss) epoch.",
             f"On {n:,} test images accuracy is an exact multiple of {rnd(Decimal(100) / n, 3)} %, "
             f"so ties at the third decimal are structural: {ties} of {len(canon)} test_acc values "
             "here are exact ties, decided by the half-to-even rule below (a half-up rule would "
             "print some of them 0.01 higher).",
             "precision, recall and F1 take fake as the positive class; AUC = ROC-AUC, AP = average "
             "precision.", MODE_NOTE,
             "stop_reason max_epochs = the epoch ceiling was reached without early stopping "
             f"(patience {patience.pop()} on validation loss, from config_used.yaml) - see "
             "t1b_convergence_reruns for the reruns."]
    return df, notes


def _env_cols(x):
    return {"hardware": x["hardware"], "torch_version": x["torch_version"],
            "timm_version": x["timm_version"]}


def t1b(runs, canon, extra):
    rows = []
    for rid, (kind, desc) in extra.items():
        if kind != "superseded":
            continue
        r = runs[runs["run_id"] == rid].iloc[0]
        c = canon[(canon["model"] == r["model"]) & (canon["mode"] == r["mode"])].iloc[0]
        for status, x in (("superseded", r), ("canonical", c)):
            rows.append({"model": MODEL_LABEL[x["model"]], "mode": x["mode"], "run_id": x["run_id"],
                         "status": status, "max_epochs": x["max_epochs"],
                         "best_epoch": x["best_epoch"], "stop_reason": x["stop_reason"],
                         "val_loss": rnd(x["val_loss"], 4), "val_acc_pct": pct(x["val_acc"]),
                         "test_acc_pct": pct(x["test_acc"]), "auc": rnd(x["test_auc"], 4),
                         "train_time_min": rnd(x["train_time_min"], 1), **_env_cols(x)})
    df = pd.DataFrame(rows, columns=["model", "mode", "run_id", "status", "max_epochs", "best_epoch",
                                     "stop_reason", "val_loss", "val_acc_pct", "test_acc_pct",
                                     "auc", "train_time_min", "hardware", "torch_version",
                                     "timm_version"])
    notes = ["Source: results/runs.csv rows NOT in results/canonical_runs.txt whose config_used.yaml "
             "matches the canonical row of the same (model, mode) in every field except the epoch "
             "budget (verified by this script), paired with the canonical row that replaces them.",
             "These superseded rows appear in no other table or figure. Same seed, split and "
             "hyperparameters; only max_epochs differs (plan 10, sessions 7-8); the environment "
             "columns show the hardware and library versions of each row.", MODE_NOTE]
    return df, notes


def t2(results, canon):
    rows = []
    for _, r in canon.iterrows():
        n_ep = len(pd.read_csv(results / r["run_id"] / "learning_curve.csv"))
        if n_ep < int(r["best_epoch"]):
            raise SystemExit(f"{r['run_id']}: learning curve shorter than best_epoch")
        rows.append({"model": MODEL_LABEL[r["model"]], "mode": r["mode"],
                     "total_params": int(r["total_params"]),
                     "trainable_params": int(r["trainable_params"]),
                     "batch_size": int(r["batch_size"]), "max_epochs": int(r["max_epochs"]),
                     "epochs_trained": n_ep, "train_time_min": rnd(r["train_time_min"], 1),
                     "min_per_epoch": rnd(Decimal(r["train_time_min"]) / n_ep, 2), **_env_cols(r)})
    notes = ["Source: results/runs.csv (canonical rows); epochs_trained = rows in the run's "
             "learning_curve.csv (early stopping ends a run before max_epochs); min_per_epoch = "
             "train_time_min / epochs_trained; train_time_min is wall-clock training time "
             "including per-epoch validation.", MODE_NOTE]
    return pd.DataFrame(rows), notes


def t3_wide(cg, canon, metric):
    cols, rows = {}, []
    for _, r in canon.iterrows():
        row = {"model": MODEL_LABEL[r["model"]], "mode": r["mode"]}
        for c in CONDITIONS:
            vals = []
            for g in GENERATORS:
                v = Decimal(cell(cg, r["run_id"], g, c)[metric])
                vals.append(v)
                row[f"{c}_{g}"] = rnd(v, 3)
                cols.setdefault(f"{c}_{g}", []).append(v)
            m = _mean(vals)
            row[f"{c}_mean"] = rnd(m, 3)
            cols.setdefault(f"{c}_mean", []).append(m)
        rows.append(row)
    rows.append({"model": f"mean ({len(canon)} checkpoints)", "mode": "",
                 **{k: rnd(_mean(v), 3) for k, v in cols.items()}})
    return pd.DataFrame(rows)


def t3_notes(results, n_real, n_fake):
    ver = _read_csv(results / "genimage_verification.csv")
    ver = ver[ver["target"].isin(GENERATORS)]
    ai, nat = sorted(set(ver["ai_ext"])), sorted(set(ver["nature_ext"]))
    return [f"Source: results/crossgen.csv (manifest checkpoints only), n = {n_real + n_fake:,} per "
            f"cell ({n_real} real + {n_fake} fake, tiny-genimage val split); <condition>_mean is the "
            "mean over the four generators for that checkpoint; the last row is the column mean "
            "over the checkpoints.",
            "down32 = GenImage image downsampled to 32x32 then upscaled through the identical "
            "32->224 CIFAKE pipeline (primary); direct224 = resized straight to 224x224 "
            "(sensitivity check). Neither isolates the generator (plan 3).",
            "Caveat 1 - content shift: CIFAKE reals are CIFAR-10-derived, GenImage reals are "
            "ImageNet, so a drop mixes content shift with generator shift.",
            "Caveat 2 - evidence destruction: down32 removes most high-frequency artefact signal "
            "from high-resolution GenImage fakes, so a near-chance down32 result is ambiguous.",
            "Caveat 3 - format asymmetry: across the generators used, the ai (fake) files are "
            f"{', '.join(ai)} and the nature (real) files {', '.join(nat)} (extension:count per "
            "generator, results/genimage_verification.csv) - a detectable cue under direct224 in "
            "particular. The sweep is reported as a bracketed negative result, not a measured "
            "generator effect.",
            "An AUC below 0.5 means the score ordering is inverted on that cell, not merely "
            "uninformative; threshold shift is reported in t3c_crossgen_summary.", MODE_NOTE]


def t3c(results, cg, canon, n_real, n_fake):
    n = n_real + n_fake
    acc = [Decimal(v) for v in cg["acc"]]
    auc = [Decimal(v) for v in cg["auc"]]
    rec = [Decimal(v) for v in cg["recall"]]
    half = Decimal("0.5")

    def where(col, target):   # tie-aware: every cell holding that value
        return "; ".join(f"{r['run_id']}/{r['generator']}/{r['condition']}"
                         for _, r in cg.iterrows() if Decimal(r[col]) == target)

    stats = [("cells", len(cg)), ("images_per_cell", n),
             ("acc_min", rnd(min(acc), 3)), ("acc_max", rnd(max(acc), 3)),
             ("acc_max_cells", where("acc", max(acc))),
             ("cells_acc_le_0.55", sum(a <= Decimal("0.55") for a in acc)),
             ("cells_acc_lt_0.70", sum(a < Decimal("0.70") for a in acc)),
             ("auc_min", rnd(min(auc), 3)), ("auc_max", rnd(max(auc), 3)),
             ("auc_max_cells", where("auc", max(auc))),
             ("cells_auc_lt_0.5", sum(a < half for a in auc))]
    for c in CONDITIONS:
        stats.append((f"cells_auc_lt_0.5_{c}",
                      sum(Decimal(v) < half for v in cg[cg["condition"] == c]["auc"])))
    for md in MODES:
        ids = set(canon[canon["mode"] == md]["run_id"])
        stats.append((f"mean_acc_{md}_checkpoints_all_cells",
                      rnd(_mean(cg[cg["run_id"].isin(ids)]["acc"]), 3)))
    ckpt_means = [_mean(cg[(cg["run_id"] == rid) & (cg["condition"] == c)]["acc"])
                  for rid in canon["run_id"] for c in CONDITIONS]
    stats += [("per_checkpoint_condition_mean_acc_min", rnd(min(ckpt_means), 3)),
              ("per_checkpoint_condition_mean_acc_max", rnd(max(ckpt_means), 3))]
    for g in GENERATORS:
        sub = cg[cg["generator"] == g]
        stats += [(f"mean_acc_{g}", rnd(_mean(sub["acc"]), 3)),
                  (f"mean_auc_{g}", rnd(_mean(sub["auc"]), 3))]
    frac_fake = []
    for _, r in cg.iterrows():
        cm = read_cm(results / r["run_id"] / f"genimage_{r['generator']}_{r['condition']}"
                     / "confusion_matrix.csv")
        if int(cm.sum()) != n:
            raise SystemExit(f"{r['run_id']} {r['generator']} {r['condition']}: confusion matrix "
                             f"total {cm.sum()} != n_real + n_fake {n}")
        frac_fake.append(Decimal(int(cm[:, 1].sum())) / n)
    stats += [("cells_predicted_fake_gt_80pct", sum(f > Decimal("0.8") for f in frac_fake)),
              ("cells_predicted_fake_lt_20pct", sum(f < Decimal("0.2") for f in frac_fake)),
              ("cells_fake_recall_gt_80pct", sum(r > Decimal("0.8") for r in rec)),
              ("cells_fake_recall_lt_20pct", sum(r < Decimal("0.2") for r in rec))]
    df = pd.DataFrame(stats, columns=["statistic", "value"])
    notes = ["Source: results/crossgen.csv (manifest checkpoints) and each cell's "
             "genimage_<generator>_<condition>/confusion_matrix.csv; counts are over the "
             f"{len(cg)} cells.",
             "cells_predicted_fake_* = fraction of ALL images in the cell predicted fake (the "
             "predicted-positive rate, the threshold-shift measure); cells_fake_recall_* = fraction "
             "of the fake half detected (crossgen.csv recall) - a different statistic. "
             "*_max_cells lists every cell (run_id/generator/condition) holding the maximum.",
             "Headline statistics for the cross-generator paragraph of Paper 2 (plan 7a A4 result "
             "block), regenerated here so none of them is typed by hand; where this table and the "
             "paragraph disagree, the table is authoritative."]
    return df, notes


_YAML_LINE = re.compile(r"^(\w+):\s*([^#]*?)\s*(?:#\s*(.*))?$")


def _yaml_top_level(path):
    """Top-level key -> (value text as written, comment or None), from the YAML text itself."""
    out = {}
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        m = _YAML_LINE.match(line)
        if m and m.group(2) != "":
            out[m.group(1)] = (m.group(2), (m.group(3) or "").strip() or None)
    return out


def t4(results, configs, canon):
    template = _yaml_top_level(configs / "template.yaml")
    parsed = {}
    for _, r in canon.iterrows():
        p = configs / Path(r["config_path"]).name
        if not p.exists():
            raise SystemExit(f"{p} (config_path of {r['run_id']}) missing")
        parsed[p.stem] = _yaml_top_level(p)
        # the live YAML must still say what the run actually used, or the table would describe
        # a config that never ran (every number traces to the run)
        used = _used_cfg(results, r["run_id"])
        for key in _HPARAM_KEYS:
            live = yaml.safe_load(parsed[p.stem][key][0]) if key in parsed[p.stem] else None
            if live != used.get(key):
                raise SystemExit(f"{p}: {key} = {live!r} but {r['run_id']} ran with "
                                 f"{used.get(key)!r} - the config drifted after the run")
    rows = []
    for key in _HPARAM_KEYS:
        groups = {}   # (value text, justification) -> config names carrying it
        for name, kv in parsed.items():
            value, comment = kv.get(key, ("-", None))
            comment = comment or (template[key][1] if key in template else None)
            groups.setdefault((value, comment), []).append(name)
        for (value, comment), names in groups.items():
            rows.append({"setting": key,
                         "value": value if len(groups) == 1 else f"{value} ({', '.join(names)})",
                         "justification": comment or "-"})
    notes = ["Source: the config YAML of each canonical run (config_path in results/runs.csv), "
             "cross-checked field by field against the run's config_used.yaml, and "
             "configs/template.yaml; values are quoted as written in the file; the justification is "
             "the inline comment on that line, falling back to template.yaml's comment; one row per "
             "distinct (value, justification), with the config files carrying it in brackets when "
             "a setting has more than one row.",
             "A value shown as '-' means the key is absent in that config (momentum is unused by "
             "AdamW)."]
    return pd.DataFrame(rows), notes


def t5(results):
    df = _read_csv(results / "genimage_verification.csv")
    used = df["target"].isin(GENERATORS)
    unused = ", ".join(df.loc[~used, "dir_name"])
    df = df.assign(generator=df["target"].where(used, "-"),
                   used_in_sweep=used.map({True: "yes", False: "no"}))
    df = df[["dir_name", "generator", "used_in_sweep", "n_ai", "n_nature", "ai_ext", "nature_ext",
             "ai_size_first20", "nature_size_first20"]]
    notes = ["Source: results/genimage_verification.csv, recorded by code/run_crossgen.py from the "
             "attached yangsangtai/tiny-genimage val split before the sweep; ai = generated, nature = "
             "real; *_ext = extension histogram; *_size_first20 = pixel sizes of the first 20 files.",
             f"Generators used in the sweep: {', '.join(GENERATORS)} - four generators unseen in "
             "training (plan 3; Stable Diffusion folders are excluded because CIFAKE's fakes are SD "
             f"v1.4). Folders present but not used: {unused}."]
    return df, notes


def t6(runs, canon, extra):
    variants = [(rid, desc) for rid, (kind, desc) in extra.items() if kind == "variant"]
    if not variants:
        return None, None
    rows = []
    for rid, desc in variants:
        r = runs[runs["run_id"] == rid].iloc[0]
        c = canon[(canon["model"] == r["model"]) & (canon["mode"] == r["mode"])].iloc[0]
        for status, x, d in (("baseline", c, "-"), ("ablation", r, desc)):
            rows.append({"model": MODEL_LABEL[x["model"]], "mode": x["mode"], "run_id": x["run_id"],
                         "status": status, "varied": d, "resolution": x["resolution"],
                         "best_epoch": x["best_epoch"], "max_epochs": x["max_epochs"],
                         "stop_reason": x["stop_reason"], "val_acc_pct": pct(x["val_acc"]),
                         "test_acc_pct": pct(x["test_acc"]), "precision_pct": pct(x["test_precision"]),
                         "recall_pct": pct(x["test_recall"]), "f1_pct": pct(x["test_f1"]),
                         "auc": rnd(x["test_auc"], 4), "train_time_min": rnd(x["train_time_min"], 1),
                         **_env_cols(x)})
    notes = ["Source: results/runs.csv rows NOT in results/canonical_runs.txt whose config_used.yaml "
             "differs from the canonical row of the same (model, mode) in at least one hyperparameter "
             "('varied' lists each difference as canonical -> ablation); the canonical row is repeated "
             "as the baseline above each ablation; the environment columns show whether hardware and "
             "library versions match the baseline.", MODE_NOTE]
    return pd.DataFrame(rows), notes


def main(results, configs, out):
    runs, canon = load_runs(results)
    extra = classify_extra_rows(results, runs, canon)
    print(f"{len(canon)} canonical runs; {len(runs) - len(canon)} other rows: "
          + (", ".join(f"{k} ({v[0]}: {v[1]})" for k, v in extra.items()) or "none"))
    write_table(out, "t1_cifake_test_metrics", *t1(results, canon))
    write_table(out, "t1b_convergence_reruns", *t1b(runs, canon, extra))
    write_table(out, "t2_model_size_and_cost", *t2(results, canon))
    cg, n_real, n_fake = load_crossgen(results, canon)
    notes3 = t3_notes(results, n_real, n_fake)
    write_table(out, "t3a_crossgen_accuracy", t3_wide(cg, canon, "acc"), notes3)
    write_table(out, "t3b_crossgen_auc", t3_wide(cg, canon, "auc"), notes3)
    write_table(out, "t3c_crossgen_summary", *t3c(results, cg, canon, n_real, n_fake))
    write_table(out, "t4_hyperparameters", *t4(results, configs, canon))
    write_table(out, "t5_tiny_genimage_composition", *t5(results))
    df, notes = t6(runs, canon, extra)
    if df is None:
        print("  t6_ablations: no ablation rows in runs.csv yet (A5), not written")
    else:
        write_table(out, "t6_ablations", df, notes)


# ----------------------------------------------------------------------------- selfcheck
def _expect_exit(fn, msg):
    try:
        fn()
    except SystemExit as e:
        assert msg in str(e), (msg, e)
    else:
        raise AssertionError(f"expected a loud failure containing {msg!r}")


def _selfcheck():
    assert pct("0.928650") == "92.86" and pct("0.934850") == "93.48", "half-to-even ties"
    assert pct("0.9655") == "96.55" and rnd("0.980733", 4) == "0.9807" and rnd("0.5", 3) == "0.500"
    assert rnd(Decimal("92.865"), 2) == "92.86" and rnd(_mean(["0.1", "0.2"]), 3) == "0.150"
    assert _md(pd.DataFrame({"a": ["x|y"]})) == "| a |\n|---|\n| x/y |"

    with tempfile.TemporaryDirectory() as tmp:
        res, cfgs = Path(tmp) / "results", Path(tmp) / "configs"
        cfgs.mkdir()
        base = {"model": "resnet50", "mode": "ft", "seed": 42, "data": {"root": "x", "split_file": "s",
                "num_workers": 2}, "resolution": 224, "augment": "hflip", "lr": 0.001,
                "max_epochs": 30, "output": {"results_dir": "r", "runs_csv": "r/runs.csv"}}
        runs = [("resnet50_ft_A", 50, {}), ("resnet50_ft_B", 30, {}),
                ("resnet50_ft_C", 50, {"augment": "none"}), ("resnet50_fe_D", 30, {"mode": "fe"}),
                ("resnet50_ft_E", 50, {})]
        lines = ["run_id,model,mode,max_epochs,config_path"]
        for rid, ep, over in runs:
            cfg = {**base, **over, "max_epochs": ep, "run_id": rid, "data": {**base["data"],
                   "root": "/kaggle/" + rid}, "cli_overrides": {"a": 1}, "device": "cuda"}
            (res / rid).mkdir(parents=True)
            (res / rid / "config_used.yaml").write_text(yaml.safe_dump(cfg), encoding="utf-8")
            lines.append(f"{rid},resnet50,{cfg['mode']},{ep},configs/{rid}.yaml")
        (res / "runs.csv").write_text("\n".join(lines) + "\n", encoding="utf-8")

        # classification: superseded (only max_epochs differs), variant, identical -> loud
        (res / "canonical_runs.txt").write_text("# c\nresnet50_ft_A\nresnet50_fe_D\n", encoding="utf-8")
        all_runs, canon = load_runs(res)
        assert list(canon["run_id"]) == ["resnet50_fe_D", "resnet50_ft_A"], "paper order fe, ft"
        _expect_exit(lambda: classify_extra_rows(res, all_runs, canon), "identical to canonical")
        all_runs = all_runs[all_runs["run_id"] != "resnet50_ft_E"]
        extra = classify_extra_rows(res, all_runs, canon)
        assert extra["resnet50_ft_B"] == ("superseded", "max_epochs 30 -> 50"), extra
        assert extra["resnet50_ft_C"] == ("variant", "augment: hflip -> none"), extra

        # manifest problems are loud
        for manifest, msg in (("resnet50_ft_A\n", "without a manifest entry"),
                              ("resnet50_ft_A\nresnet50_fe_D\nresnet50_ft_Z\n", "missing from runs.csv"),
                              ("resnet50_ft_A\nresnet50_ft_B\nresnet50_fe_D\n", "more than one run")):
            (res / "canonical_runs.txt").write_text(manifest, encoding="utf-8")
            _expect_exit(lambda: load_runs(res), msg)

        # crossgen must be the exact product, once each
        head = "run_id,generator,condition,n_real,n_fake,acc,precision,recall,f1,auc,ap"
        cells = [f"{rid},{g},{c},5,5,0.5,0.5,0.5,0.5,0.5,0.5"
                 for rid in canon["run_id"] for g in GENERATORS for c in CONDITIONS]
        (res / "crossgen.csv").write_text("\n".join([head] + cells + [cells[0]]) + "\n", encoding="utf-8")
        _expect_exit(lambda: load_crossgen(res, canon), "duplicate cell row")
        (res / "crossgen.csv").write_text("\n".join([head] + cells[1:]) + "\n", encoding="utf-8")
        _expect_exit(lambda: load_crossgen(res, canon), "not the manifest x generator x condition")
        (res / "crossgen.csv").write_text("\n".join([head] + cells) + "\n", encoding="utf-8")
        assert load_crossgen(res, canon)[1:] == (5, 5)

        # t4 refuses a config that no longer says what its run used
        (cfgs / "template.yaml").write_text("lr: 0.01   # template comment\n", encoding="utf-8")
        for rid in canon["run_id"]:
            (cfgs / f"{rid}.yaml").write_text("resolution: 224   # why\nlr: 0.001\nmax_epochs: 50\n"
                                              "seed: 42\naugment: hflip\n", encoding="utf-8")
        _expect_exit(lambda: t4(res, cfgs, canon), "drifted after the run")   # fe_D has max_epochs 30
        (cfgs / "resnet50_fe_D.yaml").write_text("resolution: 224   # why\nlr: 0.001\nmax_epochs: 30\n"
                                                 "seed: 42\naugment: hflip\n", encoding="utf-8")
        df, _ = t4(res, cfgs, canon)
        lr = df[df["setting"] == "lr"]
        assert list(lr["value"]) == ["0.001"] and list(lr["justification"]) == ["template comment"], lr
        assert list(df[df["setting"] == "max_epochs"]["value"]) == [
            "30 (resnet50_fe_D)", "50 (resnet50_ft_A)"], df
    print("make_tables selfcheck OK")


if __name__ == "__main__":
    if "--selfcheck" in sys.argv:
        _selfcheck()
        sys.exit(0)
    p = argparse.ArgumentParser()
    p.add_argument("--results", default="results")
    p.add_argument("--configs", default="configs")
    p.add_argument("--out", default="results/tables")
    a = p.parse_args()
    main(Path(a.results), Path(a.configs), Path(a.out))
