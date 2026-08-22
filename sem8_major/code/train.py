"""Training entry point (implemented at A1).

CLI:
    python code/train.py --config configs/resnet50_fe.yaml
        [--data-root path] [--results-dir path] [--amp true|false]
        [--batch-size N] [--max-epochs N] [--num-workers N]

Every hyperparameter comes from the YAML (fields documented in configs/template.yaml).
The CLI overrides exist so committed configs keep local paths and Kaggle sessions pass
/kaggle/... paths without editing YAMLs by hand; every override is recorded in the run's
config_used.yaml (implementation_plan.md §7a A1.3).

Guard: refuses to run when smoke_subset is non-null while output.runs_csv ends in runs.csv —
smoke rows are quarantined in smoke_runs.csv and can never reach a Paper 2 table.

Writes, as the run proceeds, into <results_dir>/<run_id>/:
    config_used.yaml     resolved config incl. overrides, run_id, realised dataset sizes
    learning_curve.csv   epoch,train_loss,train_acc,val_loss,val_acc
    best.pt              best-by-validation-loss checkpoint (gitignored)
On completion it evaluates the test split via eval.evaluate() and appends one row to
<runs_csv> (schema: results/README.md). run_id: <model>_<mode>_<YYYYMMDD-HHMM>.
"""

import argparse
import csv
import math
import platform
import random
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import torch
import yaml

import data
import models
from eval import append_row, evaluate

RUNS_COLUMNS = ["run_id", "date", "config_path", "model", "mode", "seed", "split_file",
                "n_train_images", "resolution", "batch_size", "optimizer", "lr",
                "weight_decay", "max_epochs", "best_epoch", "early_stopped", "stop_reason",
                "train_time_min", "total_params", "trainable_params", "hardware",
                "torch_version", "timm_version", "val_acc", "val_loss", "test_acc",
                "test_precision", "test_recall", "test_f1", "test_auc", "test_ap"]


def hardware_string():
    if torch.cuda.is_available():
        p = torch.cuda.get_device_properties(0)
        return f"{p.name}, {round(p.total_memory / 2**30)} GB"
    import os
    return "CPU: " + (os.environ.get("PROCESSOR_IDENTIFIER") or platform.processor()
                      or platform.machine())


def make_optimizer(cfg, model):
    params = [p for p in model.parameters() if p.requires_grad]
    if cfg["optimizer"] == "sgd":
        return torch.optim.SGD(params, lr=cfg["lr"], momentum=cfg.get("momentum", 0.9),
                               weight_decay=cfg["weight_decay"])
    if cfg["optimizer"] == "adamw":
        return torch.optim.AdamW(params, lr=cfg["lr"], weight_decay=cfg["weight_decay"])
    raise ValueError(f"unknown optimizer {cfg['optimizer']!r}")


def run_epoch_train(model, loader, optimizer, device, scaler, amp, mode):
    models.set_train_mode(model, mode)
    loss_fn = torch.nn.CrossEntropyLoss()
    total_loss, correct, seen = 0.0, 0, 0
    for xb, yb in loader:
        xb, yb = xb.to(device, non_blocking=True), yb.to(device, non_blocking=True)
        optimizer.zero_grad(set_to_none=True)
        with torch.amp.autocast(device_type=device, enabled=amp):
            logits = model(xb)
            loss = loss_fn(logits, yb)
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
        total_loss += loss.item() * yb.size(0)
        correct += (logits.argmax(1) == yb).sum().item()
        seen += yb.size(0)
    return total_loss / seen, correct / seen


@torch.no_grad()
def run_epoch_eval(model, loader, device):
    model.eval()
    loss_fn = torch.nn.CrossEntropyLoss()
    total_loss, correct, seen = 0.0, 0, 0
    for xb, yb in loader:
        xb, yb = xb.to(device, non_blocking=True), yb.to(device, non_blocking=True)
        logits = model(xb)
        total_loss += loss_fn(logits, yb).item() * yb.size(0)
        correct += (logits.argmax(1) == yb).sum().item()
        seen += yb.size(0)
    return total_loss / seen, correct / seen


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--config", required=True)
    p.add_argument("--data-root")
    p.add_argument("--results-dir")
    p.add_argument("--amp", choices=["true", "false"])
    p.add_argument("--batch-size", type=int)
    p.add_argument("--max-epochs", type=int)
    p.add_argument("--num-workers", type=int)
    p.add_argument("--time-budget-min", type=float,
                   help="stop cleanly before this wall-clock budget is exhausted, keeping the "
                        "best checkpoint and writing the row (a session killed at the Kaggle "
                        "cap would lose the whole run instead)")
    args = p.parse_args()

    with open(args.config, encoding="utf-8") as f:  # explicit: Kaggle is UTF-8, Windows is not
        cfg = yaml.safe_load(f)
    overrides = {}
    if args.data_root:
        overrides["data.root"] = cfg["data"]["root"] = args.data_root
    if args.results_dir:
        overrides["output.results_dir"] = cfg["output"]["results_dir"] = args.results_dir
        # runs_csv follows results_dir, keeping its basename (runs.csv or smoke_runs.csv)
        cfg["output"]["runs_csv"] = str(Path(args.results_dir) / Path(cfg["output"]["runs_csv"]).name)
        overrides["output.runs_csv"] = cfg["output"]["runs_csv"]
    if args.amp:
        overrides["amp"] = cfg["amp"] = (args.amp == "true")
    if args.batch_size:
        overrides["batch_size"] = cfg["batch_size"] = args.batch_size
    if args.max_epochs:
        overrides["max_epochs"] = cfg["max_epochs"] = args.max_epochs
    if args.num_workers is not None:
        overrides["data.num_workers"] = cfg["data"]["num_workers"] = args.num_workers
    if args.time_budget_min:
        overrides["time_budget_min"] = cfg["time_budget_min"] = args.time_budget_min

    # smoke isolation guard — config discipline already failed once, so enforce in code
    if cfg.get("smoke_subset") and Path(cfg["output"]["runs_csv"]).name == "runs.csv":
        raise SystemExit("REFUSED: smoke_subset is set but runs_csv points at runs.csv; "
                         "smoke rows belong in smoke_runs.csv (see plan 7a A1.8)")

    seed = cfg["seed"]
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    amp = bool(cfg.get("amp")) and device == "cuda"

    run_id = f"{cfg['model']}_{cfg['mode']}_{datetime.now():%Y%m%d-%H%M}"
    run_dir = Path(cfg["output"]["results_dir"]) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"run {run_id} on {device} (amp={amp})")
    train_loader, val_loader, test_loader = data.get_loaders(cfg)
    model = models.build_model(cfg).to(device)
    n_trainable, n_total = models.trainable_parameters(model)
    optimizer = make_optimizer(cfg, model)
    scaler = torch.amp.GradScaler(device, enabled=amp)

    with (run_dir / "config_used.yaml").open("w", encoding="utf-8") as f:
        yaml.safe_dump({**cfg, "run_id": run_id, "cli_overrides": overrides,
                        "n_train_images": len(train_loader.dataset),
                        "device": device}, f, sort_keys=False)

    curve_path = run_dir / "learning_curve.csv"
    with curve_path.open("w", newline="") as f:
        csv.writer(f).writerow(["epoch", "train_loss", "train_acc", "val_loss", "val_acc"])

    best = {"val_loss": float("inf"), "val_acc": 0.0, "epoch": 0}
    patience = cfg["early_stopping_patience"]
    budget_min = cfg.get("time_budget_min")
    stop_reason = "max_epochs"
    since_best = 0
    t0 = time.time()
    for epoch in range(1, cfg["max_epochs"] + 1):
        tr_loss, tr_acc = run_epoch_train(model, train_loader, optimizer, device, scaler,
                                          amp, cfg["mode"])
        va_loss, va_acc = run_epoch_eval(model, val_loader, device)
        if math.isnan(tr_loss) or math.isnan(va_loss):
            # fail fast: NaN never recovers, and waiting out the patience epochs would only
            # burn GPU quota before crashing on a missing best.pt
            raise SystemExit(f"run diverged: NaN loss at epoch {epoch} ({run_id})")
        with curve_path.open("a", newline="") as f:
            csv.writer(f).writerow([epoch, f"{tr_loss:.6f}", f"{tr_acc:.6f}",
                                    f"{va_loss:.6f}", f"{va_acc:.6f}"])
        print(f"  epoch {epoch:2d}: train loss {tr_loss:.4f} acc {tr_acc:.4f} | "
              f"val loss {va_loss:.4f} acc {va_acc:.4f}")
        if va_loss < best["val_loss"]:
            best = {"val_loss": va_loss, "val_acc": va_acc, "epoch": epoch}
            since_best = 0
            torch.save(model.state_dict(), run_dir / "best.pt")
        else:
            since_best += 1
            if since_best >= patience:
                print(f"  early stop at epoch {epoch} (no val-loss gain for {patience})")
                stop_reason = "early_stopping"
                break
        if budget_min:
            elapsed = (time.time() - t0) / 60
            # 1.15 covers epoch-time jitter plus the final test evaluation still to come
            if elapsed + (elapsed / epoch) * 1.15 > budget_min:
                print(f"  time budget: stopping after epoch {epoch} "
                      f"({elapsed:.1f} of {budget_min:.0f} min used); best checkpoint kept")
                stop_reason = "time_budget"
                break
    train_time_min = (time.time() - t0) / 60
    early_stopped = stop_reason == "early_stopping"

    # final evaluation: the untouched test split, on the best checkpoint
    model.load_state_dict(torch.load(run_dir / "best.pt", map_location=device,
                                     weights_only=True))
    test_metrics = evaluate(model, test_loader, run_dir, device=device)

    import timm
    row = {
        "run_id": run_id, "date": f"{datetime.now():%Y-%m-%d}", "config_path": args.config,
        "model": cfg["model"], "mode": cfg["mode"], "seed": seed,
        "split_file": cfg["data"]["split_file"],
        "n_train_images": len(train_loader.dataset),
        "resolution": cfg["resolution"], "batch_size": cfg["batch_size"],
        "optimizer": cfg["optimizer"], "lr": cfg["lr"], "weight_decay": cfg["weight_decay"],
        "max_epochs": cfg["max_epochs"], "best_epoch": best["epoch"],
        "early_stopped": early_stopped, "stop_reason": stop_reason,
        "train_time_min": f"{train_time_min:.2f}",
        "total_params": n_total, "trainable_params": n_trainable,
        "hardware": hardware_string(), "torch_version": torch.__version__,
        "timm_version": timm.__version__,
        "val_acc": f"{best['val_acc']:.6f}", "val_loss": f"{best['val_loss']:.6f}",
        "test_acc": f"{test_metrics['acc']:.6f}",
        "test_precision": f"{test_metrics['precision']:.6f}",
        "test_recall": f"{test_metrics['recall']:.6f}",
        "test_f1": f"{test_metrics['f1']:.6f}",
        "test_auc": f"{test_metrics['auc']:.6f}",
        "test_ap": f"{test_metrics['ap']:.6f}",
    }
    append_row(cfg["output"]["runs_csv"], RUNS_COLUMNS, row)
    print(f"done: {run_id} -> {cfg['output']['runs_csv']} "
          f"(val_acc {best['val_acc']:.4f}, test_acc {test_metrics['acc']:.4f}, "
          f"{train_time_min:.1f} min)")


if __name__ == "__main__":
    main()
