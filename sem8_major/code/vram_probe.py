"""VRAM probe — the go/no-go test for training this matrix on an 8 GB GPU.

    python code/vram_probe.py

For each of the five backbones at its configured batch size (Table 3: 128 light CNNs,
64 VGG19/ViT), runs ONE forward+backward step of synthetic 224px data in ft mode with AMP
and reports peak VRAM. Takes under a minute total on any modern GPU. A backbone that OOMs
here cannot train at that batch size on this GPU — decide batch-size cuts (documented) or
keep that run on Kaggle BEFORE starting the matrix locally.
"""

import torch

import models

CASES = [  # (timm model, batch size from its matrix config)
    ("resnet50", 128),
    ("densenet121", 128),
    ("efficientnet_b0", 128),
    ("vgg19", 64),
    ("vit_base_patch16_224", 64),
]


def probe(name, batch):
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    model = models.build_model({"model": name, "mode": "ft"}).cuda()
    model.train()
    opt = torch.optim.SGD(model.parameters(), lr=0.001, momentum=0.9)
    scaler = torch.amp.GradScaler("cuda")
    x = torch.randn(batch, 3, 224, 224, device="cuda")
    y = torch.randint(0, 2, (batch,), device="cuda")
    with torch.amp.autocast("cuda"):
        loss = torch.nn.functional.cross_entropy(model(x), y)
    scaler.scale(loss).backward()
    scaler.step(opt)
    scaler.update()
    torch.cuda.synchronize()
    peak = torch.cuda.max_memory_allocated() / 2**30
    del model, opt, x, y
    return peak


if __name__ == "__main__":
    assert torch.cuda.is_available(), "no CUDA GPU visible - wrong torch build or driver?"
    total = torch.cuda.get_device_properties(0).total_memory / 2**30
    print(f"GPU: {torch.cuda.get_device_name(0)} ({total:.1f} GB)")
    print(f"{'model':24s} {'batch':>5s} {'peak GB':>8s}  verdict")
    for name, batch in CASES:
        try:
            peak = probe(name, batch)
            # >90% of VRAM at step one leaves no headroom for fragmentation over 30 epochs
            verdict = "OK" if peak < total * 0.9 else "TIGHT - expect OOM over a long run"
            print(f"{name:24s} {batch:5d} {peak:8.2f}  {verdict}")
        except torch.cuda.OutOfMemoryError:
            torch.cuda.empty_cache()
            print(f"{name:24s} {batch:5d} {'OOM':>8s}  does NOT fit - cut batch or keep on Kaggle")
