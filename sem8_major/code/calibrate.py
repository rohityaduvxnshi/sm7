"""Per-architecture GPU timing calibration (A2; implementation_plan.md §7a A2.3).

    python code/calibrate.py --data-root /kaggle/input/cifake-real-and-ai-generated-synthetic-images
        [--batches 30] [--out results/calibration.csv] [--configs configs/a.yaml configs/b.yaml]

Times forward+backward on real batches for each of the five backbones in ft mode (the
expensive case), then projects a full-size epoch: per_batch_s x ceil(90000 / batch_size).
A single ResNet50-fe smoke number does not transfer across architectures — different batch
size, different backward cost — and mis-sizing a session against the ~9 h cap can lose
finished runs, so every backbone gets measured.

Writes one row per backbone to <out>: model, mode, batch_size, resolution, amp, device,
batches_timed, per_batch_s, est_epoch_min, est_30_epoch_h. Read est_epoch_min when planning
A3 session batches (keep >=30% margin under the session cap).
"""

import argparse
import csv
import math
import time
from pathlib import Path

import torch
import yaml

import data
import models

MATRIX_FT_CONFIGS = ["configs/resnet50_ft.yaml", "configs/densenet121_ft.yaml",
                     "configs/efficientnet_b0_ft.yaml", "configs/vgg19_ft.yaml",
                     "configs/vit_base_patch16_224_ft.yaml"]
TRAIN_IMAGES = 90000  # full CIFAKE train split, per the committed split file
COLUMNS = ["model", "mode", "batch_size", "resolution", "amp", "device", "batches_timed",
           "per_batch_s", "est_epoch_min", "est_30_epoch_h"]


def time_config(cfg_path, data_root, batches, warmup=3):
    with open(cfg_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    if data_root:
        cfg["data"]["root"] = data_root
    device = "cuda" if torch.cuda.is_available() else "cpu"
    amp = bool(cfg.get("amp")) and device == "cuda"

    # time on real data, but only enough of it: warmup + measured batches
    cfg = {**cfg, "smoke_subset": max(1, (warmup + batches) * cfg["batch_size"] // 2 + 1)}
    train_loader, _, _ = data.get_loaders(cfg)
    model = models.build_model(cfg).to(device)
    optimizer = torch.optim.SGD([p for p in model.parameters() if p.requires_grad],
                                lr=0.001, momentum=0.9)
    scaler = torch.amp.GradScaler(device, enabled=amp)
    loss_fn = torch.nn.CrossEntropyLoss()
    models.set_train_mode(model, cfg["mode"])

    done, t0 = 0, None
    for xb, yb in train_loader:
        if done == warmup:                      # start the clock after warmup batches:
            if device == "cuda":                # cudnn autotune and caches settle first
                torch.cuda.synchronize()
            t0 = time.time()
        xb, yb = xb.to(device, non_blocking=True), yb.to(device, non_blocking=True)
        optimizer.zero_grad(set_to_none=True)
        with torch.amp.autocast(device_type=device, enabled=amp):
            loss = loss_fn(model(xb), yb)
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
        done += 1
        if done >= warmup + batches:
            break
    if device == "cuda":
        torch.cuda.synchronize()
    measured = done - warmup
    if t0 is None or measured <= 0:
        raise SystemExit(f"{cfg_path}: not enough batches to time (got {done})")

    per_batch = (time.time() - t0) / measured
    batches_per_epoch = math.ceil(TRAIN_IMAGES / cfg["batch_size"])
    est_epoch_min = per_batch * batches_per_epoch / 60
    return {
        "model": cfg["model"], "mode": cfg["mode"], "batch_size": cfg["batch_size"],
        "resolution": cfg["resolution"], "amp": amp, "device": device,
        "batches_timed": measured, "per_batch_s": round(per_batch, 4),
        "est_epoch_min": round(est_epoch_min, 2),
        "est_30_epoch_h": round(est_epoch_min * 30 / 60, 2),
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data-root")
    p.add_argument("--batches", type=int, default=30)
    p.add_argument("--out", default="results/calibration.csv")
    p.add_argument("--configs", nargs="*", default=MATRIX_FT_CONFIGS)
    args = p.parse_args()

    rows = []
    for cfg_path in args.configs:
        print(f"timing {cfg_path} ...")
        row = time_config(cfg_path, args.data_root, args.batches)
        rows.append(row)
        print(f"  {row['model']:24s} {row['per_batch_s']:.3f} s/batch -> "
              f"{row['est_epoch_min']:.1f} min/epoch, {row['est_30_epoch_h']:.1f} h for 30 epochs")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    print(f"\nwrote {out}")
    print("Session planning: early stopping usually ends runs well before 30 epochs, but "
          "size sessions on the 30-epoch figure and keep >=30% margin under the cap.")


if __name__ == "__main__":
    main()
