# Victus setup guide — local GPU training machine (written 22 Aug 2026)

Target: HP Victus, Ryzen 7 8845HS, 32 GB RAM, RTX 4070 laptop (8 GB VRAM), brand-new
Windows. Goal: take over the A3 matrix (and A4–A6) from Kaggle. Everything here is
run by Rohit; steps are in order and each says what it is for. Total time ≈ 45–60 min,
most of it downloads.

**The decision gate is step 8 (VRAM probe).** Until it passes, Kaggle remains the plan
of record — do not cancel anything there.

---

## 1. Windows + GPU driver

1. Settings → Windows Update → install everything, reboot.
2. Install the NVIDIA driver: https://www.nvidia.com/drivers → RTX 4070 Laptop GPU →
   **Studio driver** (more stable than Game Ready for compute). Reboot.
3. Verify in PowerShell: `nvidia-smi` — must show "NVIDIA GeForce RTX 4070 Laptop GPU, 8188MiB".
4. HP Omen/Victus software: set the performance mode to its highest fan/TGP profile —
   the 4070's speed depends directly on how much power the chassis allows it.
5. Settings → System → Power: set "Best performance" while plugged in; **training only
   happens on mains power**, never battery.

## 2. Core tools

1. **Git for Windows**: https://git-scm.com/download/win — defaults are fine
   (Credential Manager included; it handles the private-repo login via browser).
2. **Python 3.12.x**: https://www.python.org/downloads/ — pick the latest 3.12 (the
   project was built on 3.12.10; stay on 3.12, not 3.13/3.14). In the installer, tick
   **"Add python.exe to PATH"**.
3. Verify in a NEW PowerShell: `git --version` and `python --version` (3.12.x).

## 3. Clone the repo — ONE working copy

```powershell
cd $env:USERPROFILE\Desktop
git clone https://github.com/rohityaduvxnshi/sm7.git AuthentiScan
```

A browser window pops up for GitHub sign-in on first contact (private repo). The folder
is `Desktop\AuthentiScan`, same as the old laptop. Do not make a second clone anywhere
else, and do not let GitHub Desktop create one.

## 4. Python environment with CUDA torch

```powershell
cd $env:USERPROFILE\Desktop\AuthentiScan\sem8_major
python -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu128
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m pip freeze > requirements_victus.lock
```

Notes: the cu128 index gives the CUDA build (~2.5 GB download — the plain
`pip install torch` on Windows would give the CPU build, which wastes the GPU). If the
cu128 URL ever 404s, try cu126. `requirements_victus.lock` is a NEW lock file — this is
a new training environment and Paper 2 reports exact versions per environment; do not
overwrite `requirements.lock` (the old laptop's CPU environment).

Verify:

```powershell
.venv\Scripts\python.exe -c "import torch; print(torch.__version__, torch.cuda.is_available(), torch.cuda.get_device_name(0))"
```

Must print a `+cu…` version, `True`, and the 4070.

## 5. CIFAKE data (~110 MB download, unzips to 120k images)

```powershell
python -m pip install kaggle
$env:KAGGLE_API_TOKEN = "<Kaggle API token — from kaggle.com/settings, rotate the old one>"
kaggle datasets download birdy654/cifake-real-and-ai-generated-synthetic-images -p data\cifake --unzip
```

(From `sem8_major\`. The token goes in the env var for this shell only — never into a
file in the repo. If `kaggle` isn't recognised, call it as
`$env:LOCALAPPDATA\Programs\Python\Python312\Scripts\kaggle.exe`.)

**Do NOT regenerate the split file.** `data/cifake_split_seed42.csv` came with the clone
and is the committed, immutable split every run shares. `make_split` refuses to
overwrite it anyway; leave it alone.

## 6. Self-checks (2 min — proves the clone + env before any GPU time)

```powershell
.venv\Scripts\python.exe code\data.py --selfcheck
.venv\Scripts\python.exe code\merge_runs.py --selfcheck
.venv\Scripts\python.exe code\models.py
```

All three must end with "OK". (`models.py` downloads ResNet50 weights, ~100 MB, once.)

## 7. GPU smoke run (~2 min — full pipeline on the 4070)

```powershell
.venv\Scripts\python.exe code\train.py --config configs\resnet50_fe_smoke.yaml --amp true
```

Expect: `run … on cuda (amp=True)`, two epochs, a row appended to
`results\smoke_runs.csv`, val_acc ≈ 0.71, test_acc ≈ 0.79 (the same figures the CPU
and T4 smokes produced — three-way reproducibility evidence for Paper 2).

## 8. THE DECISION GATE — VRAM probe (~1 min)

```powershell
.venv\Scripts\python.exe code\vram_probe.py
```

One forward+backward step of every backbone at its exact matrix batch size, reporting
peak VRAM against the 4070's 8 GB.

- **All five OK** → the Victus takes over everything. Tell Claude; the plan is then:
  rerun resnet50 fe/ft locally (hardware-consistent 4070 set), run the remaining matrix
  overnight, `canonical_runs.txt` points Paper 2 at the 4070 rows, T4 rows stay as
  history.
- **VGG19 or ViT OOM/TIGHT** → tell Claude the exact table; options are a documented
  batch-size cut for that model or leaving just the heavy runs on Kaggle. Decide then,
  not now.

## 9. Claude Code on the Victus — new session, not a continuation

Install Claude Code (https://claude.com/claude-code — native installer or VS Code
extension), sign in with the same account, open `Desktop\AuthentiScan`, and start the
first session with exactly this:

> Read CLAUDE.md in full, then handoff.md. Continue from the current phase. My
> execution rules in CLAUDE.md §1 apply: you change files and verify locally, I run
> every commit/push/launch myself after you hand me the commands.

Chat history does not move between machines — CLAUDE.md and handoff.md are the memory,
and they carry everything: schedule, gates, status, rules, and the failure log.

## 10. What stays true after migration

- Kaggle session 2 (densenet) finishes on its own — download `results_a3_s2.zip` and
  merge it as usual; its rows become a cross-hardware sanity check.
- The Kaggle notebooks and quota remain the fallback if the Victus surprises us.
- The old laptop stays valid for docs/paper work; its repo clone syncs via git as
  always. One rule: **pull before working, push after committing, on both machines** —
  two laptops editing without syncing is how histories fork.
