"""Evaluation and metrics (implemented at A1). Every metric comes from scikit-learn — no
hand-rolled formulas. Fake (label 1) is the positive class.

CLI (re-evaluating a checkpoint train.py produced):
    python code/eval.py --run-id <run_id> [--dataset cifake|genimage]
        [--generator midjourney|adm|biggan|vqdm] [--condition down32|direct224]
        [--checkpoint path] [--results-dir path] [--data-root path] [--genimage-root path]

--checkpoint / the path overrides exist because on Kaggle prior notebook outputs mount
read-only under /kaggle/input/ — checkpoint source and output directory must be separable
(implementation_plan.md §7a A1.4).

Writes into results/<run_id>/ (CIFAKE) or results/<run_id>/genimage_<generator>_<condition>/:
    confusion_matrix.csv   2x2, rows true / columns predicted, label order [real, fake]
    roc_points.csv         fpr,tpr,threshold
Cross-generator evaluations append one row to results/crossgen.csv:
    run_id, generator, condition, n_real, n_fake, acc, precision, recall, f1, auc, ap
"""

import argparse
import csv
from pathlib import Path

import torch
import yaml

CROSSGEN_COLUMNS = ["run_id", "generator", "condition", "n_real", "n_fake",
                    "acc", "precision", "recall", "f1", "auc", "ap"]


@torch.no_grad()
def _predict(model, loader, device):
    model.eval()
    probs, labels = [], []
    for xb, yb in loader:
        logits = model(xb.to(device))
        probs.append(torch.softmax(logits, dim=1)[:, 1].cpu())
        labels.append(yb)
    return torch.cat(labels).numpy(), torch.cat(probs).numpy()


def evaluate(model, loader, out_dir, device=None):
    """Returns the scalar metric dict; writes confusion_matrix.csv and roc_points.csv."""
    from sklearn import metrics as M
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)
    y_true, y_prob = _predict(model, loader, device)
    y_pred = (y_prob >= 0.5).astype(int)

    out = {
        "acc": M.accuracy_score(y_true, y_pred),
        "precision": M.precision_score(y_true, y_pred, pos_label=1, zero_division=0),
        "recall": M.recall_score(y_true, y_pred, pos_label=1, zero_division=0),
        "f1": M.f1_score(y_true, y_pred, pos_label=1, zero_division=0),
        "auc": M.roc_auc_score(y_true, y_prob),
        "ap": M.average_precision_score(y_true, y_prob),
        "n_real": int((y_true == 0).sum()),
        "n_fake": int((y_true == 1).sum()),
    }

    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    cm = M.confusion_matrix(y_true, y_pred, labels=[0, 1])
    with (out_dir / "confusion_matrix.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["", "pred_real", "pred_fake"])
        w.writerow(["true_real", cm[0][0], cm[0][1]])
        w.writerow(["true_fake", cm[1][0], cm[1][1]])
    fpr, tpr, thr = M.roc_curve(y_true, y_prob)
    with (out_dir / "roc_points.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["fpr", "tpr", "threshold"])
        w.writerows(zip(fpr, tpr, thr))
    return out


def append_row(csv_path, columns, row):
    """Append one dict row, writing the header first if the file is new/empty."""
    csv_path = Path(csv_path)
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    new = not csv_path.exists() or csv_path.stat().st_size == 0
    with csv_path.open("a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=columns)
        if new:
            w.writeheader()
        w.writerow({k: row.get(k, "") for k in columns})


def load_run(run_id, results_dir, checkpoint=None):
    """(cfg, model) from a finished run's artefacts. checkpoint may live elsewhere
    (read-only Kaggle mount); config_used.yaml is looked up next to it first."""
    import models
    ckpt = Path(checkpoint) if checkpoint else Path(results_dir) / run_id / "best.pt"
    cfg_path = ckpt.parent / "config_used.yaml"
    fallback = Path(results_dir) / run_id / "config_used.yaml"
    if not cfg_path.exists():
        cfg_path = fallback
    if not cfg_path.exists():
        raise SystemExit(f"config_used.yaml not found next to {ckpt} nor at {fallback} — "
                         "the whole <run_id>/ artefact dir must travel with best.pt (plan 7a A3)")
    with open(cfg_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    model = models.build_model(cfg)
    model.load_state_dict(torch.load(ckpt, map_location="cpu", weights_only=True))
    return cfg, model


def main():
    import data
    p = argparse.ArgumentParser()
    p.add_argument("--run-id", required=True)
    p.add_argument("--dataset", choices=["cifake", "genimage"], default="cifake")
    p.add_argument("--generator", choices=list(data.GENERATORS))
    p.add_argument("--condition", choices=["down32", "direct224"], default="down32")
    p.add_argument("--checkpoint", help="explicit checkpoint path (e.g. a /kaggle/input mount)")
    p.add_argument("--results-dir", default="results")
    p.add_argument("--data-root", help="override cfg data.root")
    p.add_argument("--genimage-root", help="override cfg data.genimage_root")
    args = p.parse_args()

    cfg, model = load_run(args.run_id, args.results_dir, args.checkpoint)
    if args.data_root:
        cfg["data"]["root"] = args.data_root
    if args.genimage_root:
        cfg["data"]["genimage_root"] = args.genimage_root

    run_dir = Path(args.results_dir) / args.run_id
    if args.dataset == "cifake":
        _, _, test = data.get_loaders(cfg)
        m = evaluate(model, test, run_dir)
        print({k: round(v, 4) if isinstance(v, float) else v for k, v in m.items()})
    else:
        if not args.generator:
            p.error("--generator is required for --dataset genimage")
        if cfg.get("smoke_subset"):
            # crossgen.csv is a Paper 2 artefact and crossgen rows carry no smoke marker,
            # so a smoke checkpoint must never write one (mirrors the train.py guard)
            raise SystemExit("REFUSED: smoke checkpoint (smoke_subset set in config_used) "
                             "cannot write to crossgen.csv")
        loader = data.get_genimage_loader(cfg, args.generator, args.condition)
        out_dir = run_dir / f"genimage_{args.generator}_{args.condition}"
        m = evaluate(model, loader, out_dir)
        row = {"run_id": args.run_id, "generator": args.generator,
               "condition": args.condition, **m}
        append_row(Path(args.results_dir) / "crossgen.csv", CROSSGEN_COLUMNS, row)
        print({k: round(v, 4) if isinstance(v, float) else v for k, v in m.items()})


if __name__ == "__main__":
    main()
