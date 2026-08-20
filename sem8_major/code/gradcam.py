"""Grad-CAM galleries via pytorch-grad-cam (implemented at A1; galleries built at A4).

CLI:
    python code/gradcam.py --run-id <run_id> [--n 8] [--checkpoint path]
        [--results-dir results] [--data-root path] [--out-root figures/gradcam]
        [--shared-list file]

Selection rule (implementation_plan.md §7a A1.5): a seeded stratified random sample from the
test split — n/2 real + n/2 fake among correctly classified, same among misclassified.
--shared-list (one relative_path per line) replaces the correct-panel sample with a shared
image set that all five better checkpoints classify correctly, so A4's cross-model comparison
is on identical images; misclassification panels are per-model by necessity.

Writes individual overlays to <out_root>/<run_id>/{correct,incorrect}/*.png and one
grid.png per category (A6 contact sheets assemble from these committed PNGs).

Target layers: resnet50 layer4[-1]; densenet121 last features child; efficientnet_b0
conv_head; vgg19 features[-1]; vit_base_patch16_224 blocks[-1].norm1 + reshape_transform.
"""

import argparse
import random
import re
from pathlib import Path

import numpy as np
import torch

import data
from eval import load_run


def target_layer(model, name):
    if name == "resnet50":
        return model.layer4[-1]
    if name == "densenet121":
        return list(model.features.children())[-1]
    if name == "efficientnet_b0":
        return model.conv_head
    if name == "vgg19":
        return model.features[-1]
    if name == "vit_base_patch16_224":
        return model.blocks[-1].norm1
    raise ValueError(f"no target layer registered for {name!r}")


def vit_reshape(tensor, h=14, w=14):
    # (B, 1+HW, C) token sequence -> (B, C, H, W) spatial map; drop the class token
    r = tensor[:, 1:, :].reshape(tensor.size(0), h, w, tensor.size(2))
    return r.permute(0, 3, 1, 2)


def denormalize(x):
    mean = torch.tensor(data.IMAGENET_MEAN).view(3, 1, 1)
    std = torch.tensor(data.IMAGENET_STD).view(3, 1, 1)
    return (x * std + mean).clamp(0, 1).permute(1, 2, 0).numpy()


@torch.no_grad()
def _predict_all(model, records, cfg, device):
    tf = data._transforms(cfg["resolution"], "none")
    ds = data._ImageList(cfg["data"]["root"], records, tf)
    loader = torch.utils.data.DataLoader(ds, batch_size=cfg["batch_size"], shuffle=False,
                                         num_workers=0)
    model.eval()
    preds = []
    for xb, _ in loader:
        preds += model(xb.to(device)).argmax(1).cpu().tolist()
    return preds


def _stratified_sample(pool, n, rng):
    """n/2 per class from (relative_path, label) records, fewer if the pool is short."""
    out = []
    for label in (0, 1):
        cands = sorted(r for r in pool if r[1] == label)
        out += rng.sample(cands, min(n // 2, len(cands)))
    return out


def make_gallery(run_id, n=8, checkpoint=None, results_dir="results", data_root=None,
                 out_root="figures/gradcam", shared_list=None, dump_correct=None):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from pytorch_grad_cam import GradCAM
    from pytorch_grad_cam.utils.image import show_cam_on_image
    from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget

    device = "cuda" if torch.cuda.is_available() else "cpu"
    cfg, model = load_run(run_id, results_dir, checkpoint)
    if data_root:
        cfg["data"]["root"] = data_root
    model.to(device)
    # fe checkpoints have frozen backbones: without gradients no autograd graph reaches the
    # target conv layer and the CAM would be silently empty. Eval-only, so unfreezing is safe.
    for p in model.parameters():
        p.requires_grad_(True)

    rows = data._read_split(cfg["data"]["split_file"], cfg.get("smoke_subset"))["test"]
    preds = _predict_all(model, rows, cfg, device)
    correct_pool = [r for r, p in zip(rows, preds) if p == r[1]]
    wrong_pool = [r for r, p in zip(rows, preds) if p != r[1]]

    if dump_correct:
        # A4 shared-set builder: dump each better checkpoint's correct set, intersect the
        # five files, feed the intersection sample back via --shared-list
        Path(dump_correct).parent.mkdir(parents=True, exist_ok=True)
        Path(dump_correct).write_text("\n".join(r for r, _ in correct_pool) + "\n",
                                      encoding="utf-8")
        print(f"  dumped {len(correct_pool)} correctly classified paths -> {dump_correct}")
        return None

    rng = random.Random(cfg["seed"])
    if shared_list:
        wanted = [l.strip() for l in
                  Path(shared_list).read_text(encoding="utf-8").splitlines() if l.strip()]
        by_path = dict(correct_pool)
        missing = [w for w in wanted if w not in by_path]
        if missing:
            raise SystemExit(f"shared-list images not correctly classified by {run_id}: "
                             f"{missing[:5]}{'...' if len(missing) > 5 else ''}")
        picks = {"correct": [(w, by_path[w]) for w in wanted]}
    else:
        picks = {"correct": _stratified_sample(correct_pool, n, rng)}
    picks["incorrect"] = _stratified_sample(wrong_pool, n, rng)

    cam = GradCAM(model=model, target_layers=[target_layer(model, cfg["model"])],
                  reshape_transform=vit_reshape if cfg["model"].startswith("vit") else None)
    tf = data._transforms(cfg["resolution"], "none")

    out_base = Path(out_root) / run_id
    for kind, records in picks.items():
        if not records:
            print(f"  {kind}: nothing to show (empty pool)")
            continue
        kind_dir = out_base / kind
        kind_dir.mkdir(parents=True, exist_ok=True)
        ds = data._ImageList(cfg["data"]["root"], records, tf)
        panels = []
        for i, (rel, label) in enumerate(records):
            x, _ = ds[i]
            xb = x.unsqueeze(0).to(device)
            pred = int(model(xb).argmax(1))
            heat = cam(input_tensor=xb, targets=[ClassifierOutputTarget(pred)])[0]
            overlay = show_cam_on_image(denormalize(x), heat, use_rgb=True)
            fname = re.sub(r"[^A-Za-z0-9_.-]", "_", rel) + ".png"
            plt.imsave(kind_dir / fname, overlay)
            panels.append((overlay, rel, label, pred))
        cols = min(4, len(panels))
        rows_n = (len(panels) + cols - 1) // cols
        fig, axes = plt.subplots(rows_n, cols, figsize=(3 * cols, 3.2 * rows_n), squeeze=False)
        names = {0: "real", 1: "fake"}
        for ax in axes.flat:
            ax.axis("off")
        for ax, (overlay, rel, label, pred) in zip(axes.flat, panels):
            ax.imshow(overlay)
            ax.set_title(f"true {names[label]} / pred {names[pred]}", fontsize=8)
        fig.suptitle(f"{run_id} — {kind}", fontsize=10)
        fig.tight_layout()
        fig.savefig(out_base / f"{kind}_grid.png", dpi=150)
        plt.close(fig)
        print(f"  {kind}: {len(panels)} overlays -> {kind_dir}")
    return out_base


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--run-id", required=True)
    p.add_argument("--n", type=int, default=8)
    p.add_argument("--checkpoint")
    p.add_argument("--results-dir", default="results")
    p.add_argument("--data-root")
    p.add_argument("--out-root", default="figures/gradcam")
    p.add_argument("--shared-list")
    p.add_argument("--dump-correct", help="write this run's correctly classified test paths "
                                          "to a file and exit (A4 shared-set builder)")
    args = p.parse_args()
    make_gallery(args.run_id, args.n, args.checkpoint, args.results_dir, args.data_root,
                 args.out_root, args.shared_list, args.dump_correct)


if __name__ == "__main__":
    main()
