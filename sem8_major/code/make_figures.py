"""Generate every CSV-derived Paper 2 figure plus the Grad-CAM contact sheets
(implementation_plan.md 7a A6).

    python code/make_figures.py        # writes figures/f1_* ... f5_*.png

Reads only results/runs.csv (through results/canonical_runs.txt), results/crossgen.csv, the
per-run artefact CSVs, and the committed gallery PNGs under figures/gradcam/<canonical run_id>/.
Headless (Agg); PNG metadata stripped so a regenerated figure is byte-identical on the same
library versions. Every printed number goes through make_tables.rnd, the one rounding rule.
Figures are drawn at COL_IN inches wide with 8 pt text, i.e. at the size they are printed, so
nothing has to be shrunk; suptitles are short and the full description belongs in the caption.

F1 learning curves (loss, accuracy; 5 x 2 grids, y-axis scaled per panel), F2 ROC overlays on
the CIFAKE test set (fe panel, ft panel), F3 confusion matrices (10), F4 cross-generator heatmaps
(accuracy and AUC; one file per condition), F5 Grad-CAM contact sheets (correct: the shared 8
images across the five galleries; incorrect: each gallery's own 8). Only galleries whose run_id
is in the manifest are used, so a smoke gallery can never reach a contact sheet, and the code
checks that each gallery is its backbone's better checkpoint by validation loss.
"""

import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.ticker import MaxNLocator  # noqa: E402
from PIL import Image  # noqa: E402

from data import GENERATORS  # noqa: E402
from gradcam import overlay_name  # noqa: E402
from make_tables import (CONDITIONS, MODEL_LABEL, MODES, cell, load_crossgen,  # noqa: E402
                         load_runs, pct, read_cm, rnd, test_set_size)

plt.rcParams.update({"font.size": 8, "axes.titlesize": 8, "axes.labelsize": 8,
                     "legend.fontsize": 7, "xtick.labelsize": 7, "ytick.labelsize": 7,
                     "figure.titlesize": 9})
COL_IN = 7.0   # printed width in inches (A4 text column / double journal column); P4 may change it once
MODE_LABEL = {"fe": "feature extraction", "ft": "fine-tuning"}
GEN_LABEL = {"midjourney": "Midjourney", "adm": "ADM", "biggan": "BigGAN", "vqdm": "VQDM"}
SAVE = dict(dpi=300, bbox_inches="tight", metadata={"Software": None})


def _grid_axes(canon, height):
    """5 x 2 panel grid in paper order: rows = models, columns = modes."""
    fig, axes = plt.subplots(len(MODEL_LABEL), len(MODES), figsize=(COL_IN, height),
                             constrained_layout=True)
    models = list(MODEL_LABEL)
    return fig, axes, {r["run_id"]: axes[models.index(r["model"]), MODES.index(r["mode"])]
                       for _, r in canon.iterrows()}


def learning_curves(results, canon, out, metric):
    fig, axes, ax_of = _grid_axes(canon, 9.0)
    name = {"loss": "cross-entropy loss", "acc": "accuracy"}[metric]
    for _, r in canon.iterrows():
        ax, c = ax_of[r["run_id"]], pd.read_csv(results / r["run_id"] / "learning_curve.csv")
        ax.plot(c["epoch"], c[f"train_{metric}"], label="train")
        ax.plot(c["epoch"], c[f"val_{metric}"], label="validation")
        ax.axvline(int(r["best_epoch"]), ls=":", color="grey", label="kept epoch (best val loss)")
        ax.set_title(f"{MODEL_LABEL[r['model']]} - {r['mode']}")
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    for i in range(len(MODEL_LABEL)):
        axes[i, 0].set_ylabel(name)
    for j in range(len(MODES)):
        axes[-1, j].set_xlabel("epoch")
    axes[0, 0].legend()
    fig.suptitle(f"Learning curves on CIFAKE, {name} per epoch (y-axis scaled per panel; "
                 "fe = frozen backbone, ft = fine-tuned)")
    path = out / f"f1_learning_curves_{metric}.png"
    fig.savefig(path, **SAVE)
    plt.close(fig)
    return path


def roc_overlays(results, canon, out):
    fig, axes = plt.subplots(1, 2, figsize=(COL_IN, 4.4), constrained_layout=True)
    for ax, md in zip(axes, MODES):
        ins = ax.inset_axes([0.5, 0.1, 0.47, 0.5])
        for _, r in canon[canon["mode"] == md].iterrows():
            roc = pd.read_csv(results / r["run_id"] / "roc_points.csv")
            ax.plot(roc["fpr"], roc["tpr"],
                    label=f"{MODEL_LABEL[r['model']]} (AUC {rnd(r['test_auc'], 4)})")
            ins.plot(roc["fpr"], roc["tpr"])
        ax.plot([0, 1], [0, 1], ls="--", color="grey", lw=0.8, zorder=0)
        ins.set_xlim(0, 0.2)
        ins.set_ylim(0.8, 1.0)
        ins.tick_params(labelsize=6)
        ins.set_xlabel("fpr", fontsize=6, labelpad=1)
        ins.set_ylabel("tpr", fontsize=6, labelpad=1)
        ax.indicate_inset_zoom(ins, edgecolor="grey")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xlabel("false positive rate")
        ax.set_ylabel("true positive rate")
        ax.set_title(f"CIFAKE test ROC - {MODE_LABEL[md]}")
        # below the axes: inside, a legend box hides the inset's tick labels and the zoom lines
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.14), ncol=2, frameon=False)
    path = out / "f2_roc_cifake_test.png"
    fig.savefig(path, **SAVE)
    plt.close(fig)
    return path


def confusion_matrices(results, canon, out):
    n = test_set_size(results, canon)
    fig, axes, ax_of = _grid_axes(canon, 10.0)
    for _, r in canon.iterrows():
        ax, m = ax_of[r["run_id"]], read_cm(results / r["run_id"] / "confusion_matrix.csv")
        ax.imshow(m, cmap="Blues", vmin=0, vmax=m.sum() / 2)
        for i in range(2):
            for j in range(2):
                ax.text(j, i, f"{m[i, j]:,}", ha="center", va="center",
                        color="white" if m[i, j] > m.sum() / 4 else "black")
        ax.set_xticks([0, 1], ["real", "fake"])
        ax.set_yticks([0, 1], ["real", "fake"])
        ax.set_xlabel("predicted")
        ax.set_ylabel("true")
        ax.set_title(f"{MODEL_LABEL[r['model']]} - {r['mode']}: accuracy {pct(r['test_acc'])} %")
    fig.suptitle(f"Confusion matrices on the CIFAKE test set ({n:,} images; "
                 "fe = frozen backbone, ft = fine-tuned)")
    path = out / "f3_confusion_matrices.png"
    fig.savefig(path, **SAVE)
    plt.close(fig)
    return path


def crossgen_heatmaps(cg, canon, n_cell, out):
    ylabels = [f"{MODEL_LABEL[m]} {md}" for m, md in zip(canon["model"], canon["mode"])]
    paths = []
    for cond in CONDITIONS:
        fig, axes = plt.subplots(1, 2, figsize=(COL_IN, 4.6), sharey=True, constrained_layout=True)
        for ax, metric, title in zip(axes, ("acc", "auc"), ("accuracy", "ROC-AUC")):
            vals = [[cell(cg, rid, g, cond)[metric] for g in GENERATORS] for rid in canon["run_id"]]
            im = ax.imshow(np.array(vals, dtype=float), cmap="coolwarm", vmin=0.2, vmax=0.8)
            for i, row in enumerate(vals):
                for j, v in enumerate(row):
                    far = abs(float(v) - 0.5) > 0.2   # saturated cells get white text
                    ax.text(j, i, rnd(v, 3), ha="center", va="center", fontsize=7,
                            color="white" if far else "black")
            ax.set_xticks(range(len(GENERATORS)), [GEN_LABEL[g] for g in GENERATORS])
            ax.set_yticks(range(len(ylabels)), ylabels)
            ax.set_title(f"{title}, condition {cond}")
            fig.colorbar(im, ax=ax, shrink=0.7).set_label(title)
        fig.suptitle(f"Cross-generator evaluation ({cond}), n = {n_cell:,} per cell; "
                     "colour centred at chance (0.5)")
        path = out / f"f4_crossgen_{cond}.png"
        fig.savefig(path, **SAVE)
        plt.close(fig)
        paths.append(path)
    return paths


def _true_class(overlay):
    """Class of a committed overlay from its CIFAKE path (REAL/FAKE directory), checked."""
    is_real, is_fake = "_REAL_" in overlay, "_FAKE_" in overlay
    if is_real == is_fake:
        raise SystemExit(f"cannot read the class of {overlay}")
    return "real" if is_real else "fake"


def gradcam_sheets(results, canon, gradcam_root, out):
    shared = [l.strip() for l in (results / "gradcam_shared_list.txt").read_text(encoding="utf-8")
              .splitlines() if l.strip()]
    galleries = {}
    for _, r in canon.iterrows():
        if (gradcam_root / r["run_id"]).is_dir():
            if r["model"] in galleries:
                raise SystemExit(f"two manifest galleries for {r['model']}")
            galleries[r["model"]] = (r["run_id"], r["mode"])
    missing = [m for m in MODEL_LABEL if m not in galleries]
    if missing:
        raise SystemExit(f"no gallery under {gradcam_root} for a manifest run of: {missing}")
    # the A4 rule (make_galleries.better_checkpoints): each gallery is its backbone's lower
    # val_loss checkpoint - checked here so the figure never asserts it by hand
    for m, (rid, _) in galleries.items():
        sub = canon[canon["model"] == m]
        best = sub.loc[sub["val_loss"].astype(float).idxmin(), "run_id"]
        if best != rid:
            raise SystemExit(f"gallery {rid} is not {m}'s better checkpoint by val_loss ({best})")
    paths = []
    for kind in ("correct", "incorrect"):
        fig, axes = plt.subplots(len(MODEL_LABEL), len(shared), figsize=(COL_IN, 4.9),
                                 constrained_layout=True)
        for i, m in enumerate(MODEL_LABEL):
            rid, md = galleries[m]
            kind_dir = gradcam_root / rid / kind
            if kind == "correct":
                names = [overlay_name(rel) for rel in shared]
            else:
                names = sorted((p.name for p in kind_dir.glob("*.png")),
                               key=lambda n: (_true_class(n) != "real", n))
            if len(names) != len(shared):
                raise SystemExit(f"{kind_dir}: {len(names)} overlays, expected {len(shared)}")
            for j, n in enumerate(names):
                p = kind_dir / n
                if not p.exists():
                    raise SystemExit(f"{p} missing (shared correct set not honoured?)")
                ax = axes[i, j]
                ax.imshow(Image.open(p))
                ax.set_xticks([])
                ax.set_yticks([])
                true = _true_class(n)
                pred = true if kind == "correct" else {"real": "fake", "fake": "real"}[true]
                if kind == "incorrect" or i == 0:
                    ax.set_title(f"{true} / {pred}", fontsize=6.5, pad=2)
                if j == 0:
                    ax.set_ylabel(f"{MODEL_LABEL[m]} ({md})", fontsize=7)
        what = ("the same 8 CIFAKE test images in every row" if kind == "correct"
                else "8 CIFAKE test images per checkpoint")
        fig.suptitle(f"Grad-CAM, {kind}ly classified: {what} (panel title = true / predicted class)")
        path = out / f"f5_gradcam_{kind}.png"
        fig.savefig(path, **SAVE)
        plt.close(fig)
        paths.append(path)
    return paths


def main(results, gradcam_root, out):
    out.mkdir(parents=True, exist_ok=True)
    _, canon = load_runs(results)
    cg, n_real, n_fake = load_crossgen(results, canon)
    written = [learning_curves(results, canon, out, "loss"),
               learning_curves(results, canon, out, "acc"),
               roc_overlays(results, canon, out),
               confusion_matrices(results, canon, out),
               *crossgen_heatmaps(cg, canon, n_real + n_fake, out),
               *gradcam_sheets(results, canon, gradcam_root, out)]
    for p in written:
        if not p.exists() or p.stat().st_size == 0:
            raise SystemExit(f"{p} was not written")
        print(f"  wrote {p} ({p.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--results", default="results")
    p.add_argument("--gradcam", default="figures/gradcam")
    p.add_argument("--out", default="figures")
    a = p.parse_args()
    main(Path(a.results), Path(a.gradcam), Path(a.out))
