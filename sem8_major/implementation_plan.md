# Implementation Plan — Semester 8 Track (Paper 2)

## 1. Purpose and status

This document is the build plan for the experimental work behind Paper 2 (the implementation paper) and the Semester 8 major project report. It covers environment, data, the experiment matrix, training defaults, the results pipeline, and a dated build schedule.

Status: `[CONFIRMED]` — written 18 August 2026 in response to Dr. Richa Gupta's instruction of 15 August 2026 that implementation code preparation begins now, during Semester 7, rather than at the start of Semester 8 (see CLAUDE.md §3 amendment and §13 Track B). This session produces the plan and the repository skeleton only. No training code is written yet, and no experiment has been run.

**Integrity statement:** no number produced by any run described here goes into Paper 1. Paper 1 is a review, it was submitted for the department plagiarism check on 15 August 2026, and it stays result-free. Everything generated under `sem8_major/results/` belongs to Paper 2 and the major project report.

## 2. Hardware and environment

Open item 7 (hardware) was resolved by Rohit on 18 August 2026. Two machines are used, with a clean split of duties, summarised in Table 1.

**Table 1. Hardware split.**

| Role | Machine | Specification | Used for |
|---|---|---|---|
| Development | Local laptop | Windows 10 Home, Intel i5-1135G7 (4 cores), 16 GB RAM, Intel Iris Xe integrated graphics, no CUDA GPU | Writing code, unit checks, CPU smoke tests on small subsets |
| Training | Kaggle notebooks, free tier | T4/P100-class GPU; weekly quota confirmed 30 h GPU + 20 h TPU (account screenshot, 20 Aug 2026) | All real training, evaluation, Grad-CAM, cross-generator runs |

The laptop cannot train these models in any useful time; nothing beyond a few-hundred-image smoke test should ever be attempted on it. CIFAKE is hosted on Kaggle, so it attaches directly to a Kaggle notebook without a manual download, which is the main reason for choosing that platform. During the B1 smoke run, record the Kaggle VM's exact GPU model and VRAM (from `nvidia-smi`), CPU and RAM once — Paper 2 must report exact hardware, as all three reference papers do.

Environment: Python 3.12.10 is already installed locally, so the local setup is a plain `venv` plus `requirements.txt` with loose floor pins — `torch>=2.2`, `torchvision`, `timm`, `scikit-learn`, `matplotlib`, `pandas`, `pyyaml`, `grad-cam`. Deviation noted: CLAUDE.md §13 Track B suggested Miniconda with `environment.yml`; venv is the equivalent with less installation work given Python is already present, and it changes nothing downstream.

Version-freezing rule: at the end of Phase 0, run `pip freeze > requirements.lock` locally, and separately record the versions Kaggle actually provides (they differ from local and change without notice). Every run additionally logs `torch_version` and `timm_version` into its results row.

All five backbones come from `timm` with `pretrained=True`, so one `create_model` call covers every architecture: `resnet50`, `densenet121`, `efficientnet_b0`, `vgg19`, `vit_base_patch16_224`.

## 3. Data plan

**CIFAKE** is the primary dataset (cited as C51 in the review; Bird and Lotfi). It contains 120,000 images at 32x32: 100,000 training images (50,000 real / 50,000 fake) and 20,000 test images (10,000 / 10,000). The fake images are generated with Stable Diffusion v1.4.

Split specification, fixed at Phase 0 and never changed afterwards:

- The official 20,000-image test set is left untouched and used only for final evaluation.
- A 10,000-image stratified validation set (5,000 real / 5,000 fake) is carved out of the 100,000 training images using seed 42, leaving 90,000 for training.
- The split is written to a committed split file at `data/cifake_split_seed42.csv` — **relative filenames, one line per image** (`relative_path,label,split`). Indices are not allowed: index order depends on directory enumeration, which differs between the local Windows machine and Kaggle's Linux filesystem and would silently select different images per environment.

**GenImage** provides the cross-generator test set only — no training, no fine-tuning on it. Four generators unseen during training are used: Midjourney, ADM, BigGAN, VQDM. Stable Diffusion v1.4/1.5 subsets are excluded because they are the same family CIFAKE was generated with. Target size is roughly 2,000–3,000 balanced images per generator, which is enough for a cross-generator table without a large download. The real half of each generator subset is drawn from GenImage's paired ImageNet real images and passes through the same preprocessing condition as the fakes, so real and fake are treated identically.

Access path resolved 18 Aug 2026 (see `data/genimage_access_note.md`): primary route is the Tiny-GenImage Hugging Face mirror, fallback the official Google Drive release; SD-family and Wukong subsets excluded either way. Per-generator counts and real-image provenance remain `[VERIFY at download]`.

Preprocessing confound and how it is handled: CIFAKE is 32x32 upscaled to 224x224 for the ImageNet-pretrained backbones, while GenImage images are much higher resolution. If GenImage images were fed in at native resolution, a drop in accuracy could be caused by resolution rather than by the generator. Two conditions are therefore run:

- **Primary condition** (`down32`) — downsample GenImage to 32x32, then push it through the identical 32→224 pipeline used for CIFAKE. This matches the resolution and preprocessing between datasets; it does **not** make the generator the only varying factor.
- **Secondary condition** (`direct224`) — resize directly to 224x224, reported as a sensitivity check.

Two confounds survive either condition and are stated as limitations in Paper 2 rather than papered over: (i) domain shift — CIFAKE's real images are CIFAR-10-derived (10 coarse classes) while GenImage's reals are ImageNet, so a cross-dataset accuracy drop mixes content shift with generator shift; (ii) evidence destruction — downsampling high-resolution GenImage fakes to 32x32 removes much of the high-frequency artefact signal detectors rely on (CIFAKE fakes were natively released at 32x32, so theirs survives), which makes a near-chance `down32` result ambiguous. The two conditions bracket the truth; neither isolates the generator. Both are reported in Paper 2 with this framing.

## 4. Experiment matrix

The core matrix is 5 backbones x 2 transfer-learning modes = 10 runs, listed in Table 2 in build order. Feature extraction (`fe`) means the backbone is frozen and only a new binary head is trained; fine-tuning (`ft`) means the whole network is updated. Every run has its own config file in `sem8_major/configs/`, named `<timm model>_<mode>.yaml`; run ids are stamped at launch as `<model>_<mode>_<YYYYMMDD-HHMM>`.

**Table 2. Core experiment matrix (10 runs).**

| # | Backbone | Mode | Config file | Build week |
|---|---|---|---|---|
| 1 | ResNet50 | fe | `resnet50_fe.yaml` | B2 |
| 2 | ResNet50 | ft | `resnet50_ft.yaml` | B2 |
| 3 | DenseNet121 | fe | `densenet121_fe.yaml` | B2 |
| 4 | DenseNet121 | ft | `densenet121_ft.yaml` | B2 |
| 5 | EfficientNet-B0 | fe | `efficientnet_b0_fe.yaml` | B3 |
| 6 | EfficientNet-B0 | ft | `efficientnet_b0_ft.yaml` | B3 |
| 7 | VGG19 | fe | `vgg19_fe.yaml` | B3 |
| 8 | VGG19 | ft | `vgg19_ft.yaml` | B3 |
| 9 | ViT-B/16 | fe | `vit_base_patch16_224_fe.yaml` | B4 |
| 10 | ViT-B/16 | ft | `vit_base_patch16_224_ft.yaml` | B4 |

After the matrix is complete, in this order:

- **Grad-CAM galleries (B5).** For each of the 5 backbones, using its better-performing checkpoint: heatmaps for a fixed sample of correctly classified and misclassified images, real and fake. Fixed sample indices, so the figures are reproducible.
- **Cross-generator evaluation (B5).** Evaluation only, no training. Each of the 10 checkpoints is scored on each of the 4 GenImage generator subsets, under both preprocessing conditions. This is driven by `eval.py` CLI flags (`--generator`, `--condition`) against existing checkpoints — no new configs — and appends to `results/crossgen.csv`.
- **Ablations (B6, only if time allows).** Augmentation off — `resnet50_ft_noaug.yaml`. Input resolution 64 and 128, ResNet50 fine-tuning only (224 is already covered by run 2) — `resnet50_ft_res64.yaml`, `resnet50_ft_res128.yaml`. Feature extraction versus fine-tuning needs no extra run; it falls out of the matrix.

Compute budget, **estimate only**: 15–30 GPU-hours for the 10 core runs and roughly 5 GPU-hours for Grad-CAM, cross-generator evaluation and ablations combined. That fits inside one to two weeks of the Kaggle free-tier quota, assuming the quota is what is stated above.

## 5. Training defaults

These are plan-level defaults, tunable in Phase 2 once the smoke run reveals real timings. Each carries a one-line justification, following the Cengel et al. convention. They are recorded in Table 3 and copied verbatim into every config file, so no hyperparameter is ever hardcoded in a script.

**Table 3. Default training configuration and justification.**

| Setting | Value | Why |
|---|---|---|
| Input size | 224x224 | ImageNet-pretrained weights expect it; CIFAKE 32x32 images are upscaled |
| Optimiser (CNNs) | SGD, momentum 0.9 | Matches the transfer-learning setup in the reference papers and is stable for CNN fine-tuning |
| Learning rate (CNN, fe) | 0.01 | Only a fresh head is trained, so a larger rate converges quickly |
| Learning rate (CNN, ft) | 0.001 | Pretrained weights need small updates or the features are destroyed |
| Optimiser (ViT, fe) | AdamW, lr 1e-3 | Only the fresh head trains, so a higher rate is safe; AdamW is the standard transformer optimiser |
| Optimiser (ViT, ft) | AdamW, lr 3e-5 | Full ViT-B/16 updates need a small rate or the pretrained features degrade |
| Weight decay | 0 (baseline) | No explicit regularisation at baseline; early stopping and flip augmentation guard overfitting — revisit only if learning curves show it |
| Batch size | 128 CNNs; 64 for VGG19 and ViT | 128 fits a T4 for the lighter backbones; VGG19 and ViT need the smaller batch for memory |
| Mixed precision | On | Roughly halves memory and shortens wall-clock time on T4/P100 with no accuracy cost expected |
| Max epochs | 30 | Enough for convergence on 90k images; early stopping usually ends it sooner |
| Early stopping | Patience 5, on validation loss | Stops wasted GPU time once validation loss stops improving |
| Augmentation (baseline) | Random horizontal flip only | Keeps the baseline simple; heavier augmentation can destroy the generation artefacts the detector relies on |
| Seed | 42, everywhere | One seed across split, initialisation and shuffling makes runs reproducible |
| Checkpointing | Best validation loss kept | The reported model is the best one, not the last one |

## 6. Metrics and results pipeline

The metrics module implements exactly the suite defined in Paper 1 Section 5, so Paper 2 reports against the standard the review itself set: accuracy, precision, recall, F1, AUC, average precision, plus confusion matrix, ROC curve and learning curves. All of these come from scikit-learn — the formulas are not hand-rolled, because a hand-rolled metric is one more thing that can be silently wrong. Grad-CAM uses the `pytorch-grad-cam` library rather than a hand-written implementation.

Every finished run appends exactly one row to the runs CSV named in the config's `output` block (default `sem8_major/results/runs.csv`), with the schema in Table 4.

**Table 4. `runs.csv` schema.**

| Field | Content |
|---|---|
| run_id | `<model>_<mode>_<YYYYMMDD-HHMM>`; matches the artefact directory name |
| date | Run date |
| config_path | Path to the config YAML used |
| model | timm model name |
| mode | `fe` (feature extraction) or `ft` (fine-tuning) |
| seed | Random seed |
| split_file | Path to the committed split file (`data/cifake_split_seed42.csv`) |
| n_train_images | Realised training-image count (90,000 full; smaller only in smoke rows — makes any subset run self-evident) |
| resolution | Input size |
| batch_size | Mini-batch size |
| optimizer | Optimiser name |
| lr | Initial learning rate |
| weight_decay | Weight decay |
| max_epochs | Epoch cap |
| best_epoch | Epoch of the kept checkpoint |
| early_stopped | Whether early stopping triggered |
| stop_reason | `max_epochs` / `early_stopping` / `time_budget` — the last means the run stopped cleanly against a session-time budget rather than converging; disclosed in Paper 2 for any run carrying it |
| train_time_min | Wall-clock training time, minutes |
| total_params | Total parameter count of the model |
| trainable_params | Trainable parameter count (differs by mode; Paper 2 reports it per the Karki et al. table) |
| hardware | GPU model + VRAM as reported by the notebook (e.g. `Tesla T4, 16 GB`), or the local CPU string for smoke runs |
| torch_version | Exact torch version |
| timm_version | Exact timm version |
| val_acc, val_loss | Validation accuracy and loss at the best epoch |
| test_acc, test_precision, test_recall, test_f1, test_auc, test_ap | Test-set metrics on the untouched 20k CIFAKE test set |

Each run also writes an artefact directory `sem8_major/results/<run_id>/` containing `config_used.yaml`, `learning_curve.csv`, `confusion_matrix.csv`, `roc_points.csv`, and the best checkpoint.

Cross-generator evaluations append one row per (checkpoint, generator, condition) cell to `results/crossgen.csv` with the schema: `run_id, generator, condition, n_real, n_fake, acc, precision, recall, f1, auc, ap`.

**No hand transcription, ever.** Every table and figure in Paper 2 is generated from these CSVs by a script. A number typed by hand into a manuscript is a number nobody can check.

## 7. Build schedule

Weeks run Monday–Sunday. Table 5 gives the Semester 7 portion with exact 2026 dates; Semester 8 calendar dates are unknown, so those phases are listed as relative weeks only.

The hard Semester 7 commitment is **B0 and B1** — environment, data, split, results schema, and one working end-to-end run. That is what the guide asked for. B2 onward is planned work that may slip into Semester 8 without damaging anything, because Semester 7's graded deliverable is still the review paper.

**Table 5. Build schedule.**

| Week | Dates (2026) | Objective | Deliverable artefact | Status |
|---|---|---|---|---|
| B0 | 17–23 Aug | Phase 0 — local venv + requirements; Kaggle account and notebook set up; CIFAKE attached and loading; split file written and committed; `runs.csv` schema created; GenImage access path verified | `requirements.txt`, `requirements.lock`, `data/cifake_split_seed42.csv`, empty `results/runs.csv`, GenImage access note | DONE 20 Aug (split 45k/45k/5k/5k/10k/10k; quota 30 h/week confirmed; notebook `yaduvxnshi/notebook322addb147` with CIFAKE attached — GPU and Internet still to enable at B1) |
| B1 | 24–30 Aug | Phase 1 — end-to-end smoke run: ResNet50 feature extraction on a small subset, CPU locally first, then one short Kaggle GPU run. Proves data → train → eval → CSV append → Grad-CAM on one batch. Nothing else starts until this passes | Smoke-run row in `smoke_runs.csv` (isolation rule, §7a A1.8), one Grad-CAM image | superseded by §7a A1–A2 |
| B2 | 31 Aug–6 Sep | ResNet50 + DenseNet121, both modes (runs 1–4) | 4 rows in `runs.csv` + 4 artefact dirs | NOT STARTED |
| B3 | 7–13 Sep | EfficientNet-B0 + VGG19, both modes (runs 5–8) | 4 rows + 4 artefact dirs | NOT STARTED |
| B4 | 14–20 Sep | ViT-B/16, both modes (runs 9–10); 10-run matrix complete | 2 rows + 2 artefact dirs | NOT STARTED |
| B5 | 21–27 Sep | Grad-CAM galleries; cross-generator GenImage evaluation, both preprocessing conditions | `figures/gradcam/`, `results/crossgen.csv` | NOT STARTED |
| B6 | 28 Sep–4 Oct | Ablations (augmentation, resolution); buffer for reruns | Ablation rows in `runs.csv` | NOT STARTED |
| B7 | 5–9 Oct | Consolidation only — result tables and figures generated from the CSVs. Deliberately light: this is Semester 7 guide-review week for the paper | `results/tables/`, `figures/` | NOT STARTED |
| S8-1 | relative | Re-verification runs; any ablations not finished | Updated `runs.csv` | NOT STARTED |
| S8-2 | relative | Paper 2 draft following the Karki et al. schema (= §10 phase P1; feeds both the major report and the merged publication) | Paper 2 sections | NOT STARTED |
| S8-3 | relative | Major project report, viva and demo preparation | Report DOCX → PDF | NOT STARTED |

## 7a. Acceleration amendment `[CONFIRMED — adopted 20 August 2026 at Rohit's request; verified by a 5-lens adversarial review the same day, 32 findings fixed]`

Track B no longer waits for calendar build weeks. Phases A1–A6 below replace the B1–B7
calendar rows of Table 5 as the working schedule; the B labels are kept in brackets so older
references stay readable. Rules that survive acceleration unchanged:

- Every phase passes a review gate (G1–G6) before the next starts. **Closing a gate updates
  three documents in the same pass, dated: `CLAUDE.md` §13, this plan, and `handoff.md` at
  the repo root (sections: Goal / Current State / Active Files / Changes it made / Failed
  Attempts / Next steps)** `[rule added 20 Aug 2026 at Rohit's request]`.
- **WPRs:** Minor Project WPRs continue to report Track A literature work only, uploaded on
  their scheduled Wednesdays. No Track B artefact appears in ANY Minor WPR (5 through 12)
  unless the guide answers D3 yes — acceleration moves implementation work into
  literature-review calendar weeks, so this now applies to every remaining WPR, not just
  WPR 12. §8.7 is widened accordingly.
- **Track A preempts Track B.** The plagiarism result, Rohit's rewrite pass, guide requests,
  and Week 12 always outrank D4 Kaggle actions; acceleration absorbs the slip without
  penalty (B2+ was always allowed to slip into Semester 8). **No new Kaggle session is
  launched during 5–9 Oct** (guide-review week); any phase unfinished then pauses until
  after submission.
- The Paper 1 firewall (§8.6) is absolute.

### A1 [was B1] — full local implementation + CPU smoke run. Start: 20 Aug, immediately.

Step 0: `git init` in the project root and commit everything, including the split file and
`requirements.lock` (`.gitignore` is ready; §8.8's recommendation is now a scheduled step).
Until a remote exists (D1), end each working day by zipping `code/` + `configs/` + the split
file to an off-machine location (cloud drive, or a private Kaggle dataset via the direct REST
API) — one laptop must never hold the only copy.

Modules, all CPU-testable (the CIFAKE path is proven locally end-to-end; the GenImage path is
proven locally only against a synthetic folder tree — its real-data verification happens at
A4, first access to tiny-genimage):

1. `data.py` — `get_loaders`: reads the committed split file, resizes 32→`resolution` with
   ImageNet normalisation, hflip on train only when `augment: hflip`, honours `smoke_subset`
   (**unit: images per class per split**, stratified first-N of the sorted split file, so the
   subset is identical everywhere; the loader prints realised per-class counts). 
   `get_genimage_loader`: maps tiny-genimage's official folder convention
   `imagenet_ai_<date>_<generator>/val/{ai,nature}` to our four generators, caps at
   2,000–3,000 balanced images per generator (deterministic: sorted paths, seeded sample),
   implements `down32` and `direct224`; ships a synthetic-tree `--selfcheck` mirroring
   `make_split`'s. Real folder names and per-generator counts remain
   `[VERIFY at first tiny-genimage access, A4]`.
2. `models.py` — one `timm.create_model(name, pretrained=True, num_classes=2)` call for all
   five backbones; `fe` freezes everything except the classifier head **and keeps the
   backbone in eval mode during training so BatchNorm running statistics stay at their
   ImageNet values** (otherwise "frozen backbone" is false — BN stats would silently adapt);
   `ft` updates everything in train mode. Two-logit head with cross-entropy everywhere;
   softmax index 1 (fake) feeds AUC/AP. Returns total/trainable parameter counts.
3. `train.py` — config-driven: seeds (`random`, `numpy`, `torch`, CUDA) from `cfg.seed`;
   optimiser per config; optional AMP; early stopping on validation loss; best-checkpoint
   keeping; `learning_curve.csv` per epoch; one CSV append on completion with every Table 4
   field including the new `n_train_images` column. **Guard: refuses to run if
   `smoke_subset` is non-null while `output.runs_csv` ends in `runs.csv`** — config
   discipline already failed once here, so the leak is made impossible in code. CLI accepts
   `--data-root` and `--results-dir` overrides (logged into `config_used.yaml`) so committed
   configs keep local paths and the Kaggle driver passes `/kaggle/...` paths without editing
   YAMLs by hand.
4. `eval.py` — loads a checkpoint via an explicit `--checkpoint` argument (checkpoint source
   and output directory are separate paths, because on Kaggle prior outputs mount read-only
   under `/kaggle/input/`); computes the §6 metric suite via scikit-learn (positive class =
   fake = 1); writes `confusion_matrix.csv`, `roc_points.csv`; `--generator`/`--condition`
   flags append cross-generator rows to `crossgen.csv`.
5. `gradcam.py` — `pytorch-grad-cam`; per-architecture target layers (ViT via the reshape
   transform). Sample selection (aligned with the gradcam.py contract): a **seeded stratified
   random sample** from the test split. For the "correct" panels, one shared image set that
   all five better checkpoints classify correctly, so cross-model comparisons are on
   identical images; misclassification panels are per-model by necessity.
6. `merge_runs.py` — merges downloaded session results into the repo copies: `runs.csv`
   keyed by `run_id`, `crossgen.csv` keyed by `(run_id, generator, condition)`; refuses
   duplicate keys; carries a selfcheck like `data.py`'s.
7. The nine remaining matrix YAMLs (Table 2 runs 2–10; Table 3 values; ViT on AdamW at its
   two rates; VGG19 and ViT at batch 64). `resnet50_fe.yaml` was reset to matrix state
   (smoke_subset: null) and `resnet50_fe_smoke.yaml` created on 20 Aug.
8. **Smoke-run isolation rule:** smoke runs use `*_smoke.yaml` configs writing to
   `results/smoke_runs.csv`, never `results/runs.csv`. Paper 2 table scripts read only
   `runs.csv`/`crossgen.csv`. Enforced by the train.py guard (item 3) and visible in-row via
   `n_train_images`.
9. Local CPU smoke via `resnet50_fe_smoke.yaml` (200 images per class per split, 2 epochs):
   data → train → eval → `smoke_runs.csv` append → one Grad-CAM image.

**Gate G1:** smoke artefacts exist and are well-formed (row parses, all columns filled,
checkpoint reloads, Grad-CAM PNG opens, realised subset counts match the config); all ten
matrix configs exist with `smoke_subset: null` and Table 3 values; genimage-loader selfcheck
passes; review pass over all modules (incl. merge_runs.py) against §8 rules.

**G1 PASSED 20 Aug 2026.** All six modules implemented; selfchecks green; CPU smoke ran
end-to-end twice (incl. once with the shipped num_workers: 2 through Windows spawn); guard
negative-tests refuse correctly; Grad-CAM overlays verified non-degenerate. A 4-lens
adversarial code review returned 16 findings, all fixed — notably: 9 configs were cp1252-
encoded and would have crashed every A3 run at load on Kaggle (re-encoded UTF-8 + explicit
encoding= on all text I/O); the DataLoader worker seeder was an unpicklable closure (broken
under spawn; now a module-level partial); `imagenet_midjourney` (official no-infix naming)
would not have been found at A4; genimage sampling now balance-capped by construction;
NaN divergence fails fast; merge_runs and eval got smoke side-door guards; make_split
refuses to overwrite the committed split without --force; gradcam gained --dump-correct for
the A4 shared-set build.

### A2 [was B1 second half] — code transport + Kaggle GPU smoke. Needs Rohit once.

1. **Code transport (D1): RESOLVED 20 Aug 2026** — private GitHub repo
   `rohityaduvxnshi/sm7` created by Rohit; project history pushed (its auto-created README
   merged in rather than force-overwritten). The notebook clones it with a Kaggle Secret
   `GITHUB_PAT`; later code changes flow automatically via `git pull`. Fallback if the PAT
   route ever fails: zip `code/` + `configs/` into a private Kaggle dataset via the REST API.
   **Working copy warning:** `C:\Users\rohit\Documents\GitHub\sm7` is a second clone created
   by GitHub Desktop — the real working copy is `C:\Users\rohit\Desktop\AuthentiScan`; do not
   edit in the other one.
2. Kaggle GPU smoke in `yaduvxnshi/notebook322addb147`: enable GPU + Internet, pip-install
   `timm`/`grad-cam` (never touch the preinstalled torch), fetch code, run
   `resnet50_fe_smoke.yaml` on GPU (AMP on via override). Record once into the repo: exact
   GPU model + VRAM from `nvidia-smi`, CPU, RAM, Kaggle torch/torchvision/timm versions.
3. **Per-architecture calibration (replaces single-number extrapolation):** in the same short
   session, time 20–50 full-size batches (forward+backward, ft mode) for each of the five
   backbones and derive per-epoch estimates as per-batch time × batches per epoch. A
   ResNet50-fe subset number transfers badly to VGG19-ft/ViT-ft (different batch size,
   backward cost, per-image cost); mis-sizing a session against the cap can lose finished
   work.
4. Session facts, recorded in this file: free-tier maximum single-session GPU duration
   `[VERIFY in the session — believed ~9 h, changes over time]`; quota-reset day
   `[VERIFY on the quota page]`; whether outputs of multiple versions of the same notebook
   can be attached simultaneously `[VERIFY — A4 depends on it; fallback in A4]`.

**Tooling prepared locally 20 Aug (ready before the session opens):** `code/calibrate.py`
(times all five backbones, projects epochs), `code/record_env.py` (hardware + versions →
`results/kaggle_env.md`), `code/run_session.py` (A3 driver: subprocess per config, continues
on failure), and `notebooks/phase_a2_smoke.ipynb` (the eight-cell session: clone → deps →
env → GPU smoke → Grad-CAM → calibrate → session plan → zip). Calibrate and the driver's
failure isolation were tested locally on CPU.

**Gate G2:** GPU smoke row complete and coherent (hardware string, versions, timing);
smoke val_acc well above 50% (coarse pipeline check before any quota is spent on the
matrix); Grad-CAM works on GPU; calibration table for all five backbones recorded; the three
session facts resolved or explicitly still-open with fallbacks.

**G2 PASSED 22 Aug 2026.** Session ran on a **Tesla T4 (15 GB)**, 4-core Xeon @ 2.00 GHz,
31 GB RAM, CUDA 12.8, **torch 2.10.0+cu128, timm 1.0.26** (local lock is torch 2.13.0+cpu /
timm 1.0.28 — logged per run, exactly why). Full capture in `results/kaggle_env.md`. GPU
smoke: val_acc 0.7175, test_acc 0.7925 — **bit-identical to the CPU smoke**, and 0.09 min vs
2.8 min wall clock. Grad-CAM verified on GPU. Calibration in `results/calibration.csv`.
Of the three session facts, only the multi-version-attach question mattered, and A3's
one-notebook-per-session design removes the dependency entirely (A4 attaches several
*notebooks'* outputs, which is ordinary); session cap and quota-reset day stay `[VERIFY]`
and are handled by time budgets instead of assumptions.

**Measured 30-epoch worst case** (fe estimated at 60% of ft; ft measured):

| Backbone | ft | fe (est) | Backbone | ft | fe (est) |
|---|---|---|---|---|---|
| EfficientNet-B0 | 1.78 h | 1.07 h | ViT-B/16 | 5.43 h | 3.26 h |
| ResNet50 | 2.70 h | 1.62 h | VGG19 | 6.42 h | 3.85 h |
| DenseNet121 | 3.25 h | 1.95 h | **Total** | **19.6 h** | **11.8 h** |

**31.3 GPU-h worst case exceeds the 30 h weekly quota**, so the matrix is planned defensively:
early stopping at a realistic ~12 epochs brings it to ≈12.5 h, and every run carries a
`--time-budget-min` guard (new `time_budget_min` config field / CLI flag, `stop_reason`
column) that stops cleanly with the best checkpoint kept rather than being killed at the
session cap. Any run stopped that way is disclosed as such in Paper 2.

**A3 session plan** (`notebooks/make_a3_notebook.py` is the single source of truth; one
Kaggle notebook per session, generated and pushed by API):

| Session | Runs | Worst case | Budget/run |
|---|---|---|---|
| 1 | resnet50 fe + ft | 4.3 h | 330 min |
| 2 | densenet121 fe + ft | 5.2 h | 330 min |
| 3 | efficientnet_b0 fe + ft, vit fe | 6.1 h | 340 min |
| 4 | vgg19 fe | 3.9 h | 330 min |
| 5 | vgg19 ft (alone by rule) | 6.4 h | 330 min |
| 6 | vit ft (alone by rule) | 5.4 h | 330 min |

Session 1 pushed 22 Aug as `yaduvxnshi/authentiscan-a3-session-1` (private, GPU + Internet
on, CIFAKE attached). G3 fires after it.

**Session 1 COMPLETE + G3 PASSED (22 Aug 2026),** after two false starts (a Kaggle
notebook-storage glitch, then Kaggle's new namespaced dataset mounts — both documented in
`handoff.md`; notebooks now autodetect the mount and hard-abort on non-T4 GPUs):

| run | best epoch | stop | time | val_acc | test_acc | test_auc |
|---|---|---|---|---|---|---|
| resnet50_fe | 30 | max_epochs | 120 min | 0.9301 | 0.9283 | 0.9807 |
| resnet50_ft | 30 | max_epochs | 190 min | **0.9566** | 0.9593 | 0.9925 |

G3 read on val_acc: ft in the mid-90s and above the CIFAKE-paper small-CNN baseline (≈93%,
C51); fe sensibly below ft; curves clean. Planning consequences, applied to the session
table in `make_a3_notebook.py`: measured times ran ~1.25x the batch calibration and neither
run early-stopped (val loss still improving at epoch 30), so remaining sessions are budgeted
at 1.25x worst case (~34 h remaining total) — the matrix **will** spill into the next quota
week as §7a already allows. Quota used this week so far: ≈6.5 h of 30.

### A3 amendment 2 — Kaggle-first `[CONFIRMED — Rohit, 23 Aug 2026; supersedes the carve-out below for run placement]`

With the T4 already holding 4 of 10 rows, Rohit decided to **exhaust the Kaggle quota on the
remaining six runs before touching the Victus for training**. If all six complete on the T4,
the matrix is BOTH hardware-consistent and config-faithful — the carve-out's trade-off
dissolves and Paper 2's training-time table needs no per-GPU caveat. Session 2's early
stopping (~35% of worst case) makes the six fit a realistic 11–16 GPU-h. Placement now:

- **Kaggle sessions 3–6** (as originally designed in `make_a3_notebook.py`): session 3
  effnet fe+ft + vit fe (7.6 h worst), session 4 vgg fe (4.8 h), session 5 vgg ft (8.0 h,
  alone), session 6 vit ft (6.8 h, alone). Launch sequentially; check remaining quota
  before session 5 (the heaviest).
- **Victus**: A4–A6 machine (Grad-CAM, cross-generator, consolidation — its CUDA env is
  validated and stays) and training fallback: any run the quota cannot absorb, or any
  failed session, runs there per the carve-out rules below (densenet-only batch caveat
  still applies if it ever reruns locally).

The carve-out below is retained for the record and for the fallback rules.

### A3 amendment — Victus carve-out `[CONFIRMED — Rohit, 22 Aug 2026; run placement superseded 23 Aug by amendment 2 above]`

An RTX 4070 laptop (8 GB VRAM, HP Victus, Ryzen 7 8845HS, 32 GB RAM) replaced Kaggle for
most of the remaining matrix. Victus environment (third environment Paper 2 reports, in
`requirements_victus.lock`): Python 3.12.10, torch 2.11.0+cu128, torchvision 0.26.0+cu128,
timm 1.0.28, driver 592.82/CUDA 13.1.

**Reproducibility milestone:** the smoke run is bit-identical across all four environments —
laptop CPU (torch 2.13.0+cpu), Kaggle T4 (2.10.0+cu128, timm 1.0.26), and Victus 4070
(2.11.0+cu128, timm 1.0.28) all produce val_acc 0.7175 / test_acc 0.7925. Different
hardware, torch and timm versions; same seed, same split, same numbers.

`code/vram_probe.py` verdicts at committed batch sizes: resnet50 5.51 GB OK,
efficientnet_b0 5.42 GB OK, vgg19 3.96 GB OK, vit 4.63 GB OK — and **densenet121 at batch
128: 8.05 GB, which does not OOM but silently spills into driver system-memory fallback,
measured at 14.60 ms/img vs 3.13 at batch 96 — 4.7x slower, i.e. unusable** (a ~6.5 h run
would silently become ~30 h). At batch 96: 6.10 GB / 3.13 ms; at batch 64: 4.10 GB /
3.04 ms. Measured compute reference: resnet50-ft 2.73 ms/img pure compute on the 4070 vs
4.23 ms/img end-to-end on the T4.

The split, and the trade-off it settles: **config fidelity beats hardware uniformity.**
Batch size feeds the accuracy columns the four-CNN comparison rests on; hardware feeds only
the training-time column, which `runs.csv` discloses per row.

- **Local on the Victus (6 runs):** efficientnet_b0 fe/ft, vgg19 fe/ft, vit fe/ft — no
  quota, no session caps, no 5–9 Oct blackout. Environment: `requirements_victus.lock`
  (CUDA build; a third environment Paper 2 reports).
- **Kept as-is:** resnet50 fe/ft T4 rows. Once densenet stays on the T4, a fully
  hardware-consistent set is unachievable, so re-running resnet50 locally buys nothing.
- **Kaggle:** densenet121 finishes in the already-running session 2 at its committed batch
  128. Fallback if that session fails: densenet locally at batch 64 (4.10 GB peak),
  recorded as a documented deviation.
- Kaggle sessions 3–6 were never launched and are no longer needed; Kaggle stays available
  as fallback. `make_a3_notebook.py` is retained for that fallback only.
- **Paper 2 obligation created here:** the training-time table is annotated per GPU (T4
  vs RTX 4070 laptop rows are not directly comparable); accuracy columns are unaffected.
- A4 venue (tiny-genimage locally vs a Kaggle eval notebook) is decided when the matrix
  completes; all checkpoints will be local either way.

**Kaggle session 2 COMPLETE (merged 23 Aug 2026) — the Kaggle portion of the matrix is
finished.** Early stopping fired this time (~2.3 h total vs 6.5 h worst case):

| run | best epoch | stopped at | time | val_acc | test_acc | test_auc |
|---|---|---|---|---|---|---|
| densenet121_fe | 4 | 9 (early) | 41 min | 0.9359 | 0.9349 | 0.9848 |
| densenet121_ft | 7 | 12 (early) | 95 min | **0.9764** | **0.9760** | 0.9972 |

DenseNet121-ft is the matrix leader so far, ahead of ResNet50-ft (0.9593). G3-style check
passes (val-based, mid-90s, clean curves). **Matrix status: 4 of 10 rows in `runs.csv`**
(resnet50 + densenet121, both modes, all T4 at committed batch sizes). Run placement for the
remaining six was reopened the same day by amendment 2 above (Kaggle-first).

**Kaggle session 3 COMPLETE (merged 23 Aug 2026).** Three runs, all on T4 at committed batch
sizes, 4.2 h against a 7.6 h worst case:

| run | best epoch | stopped at | time | val_acc | test_acc | test_auc |
|---|---|---|---|---|---|---|
| efficientnet_b0_fe | 29 | 30 (max_epochs) | 98 min | 0.9267 | 0.9287 | 0.9802 |
| efficientnet_b0_ft | 15 | 20 (early) | 85 min | **0.9750** | 0.9756 | 0.9971 |
| vit_base_patch16_224_fe | 6 | 11 (early) | 69 min | 0.9462 | 0.9475 | 0.9881 |

G3-style check passes: ft in the mid-to-high 90s, fe sensibly below it, confusion matrices
balanced (no collapsed class), curves clean. EfficientNet-B0-ft lands 0.0004 test-accuracy
behind DenseNet121-ft — close enough that Paper 2 should treat the two as tied rather than
ranked on a single seed. ViT feature extraction (0.9462) beats every CNN feature-extraction
row, which is the expected shape: a frozen ViT gives a stronger linear-probe representation
than a frozen CNN, and the gap closes once the CNNs are fine-tuned.

**Matrix status at the close of session 3: 7 of 10 rows, every row Tesla T4 at its committed
batch size, seed 42 and the same split file throughout.** Remaining then: vgg19 fe
(session 4, since completed — see below), vgg19 ft (session 5), vit ft (session 6). Measured GPU time for the seven rows is 11.6 h; the three remaining are
19.6 h worst case but early stopping has fired on four of the last five runs, so the
realistic figure is far lower and amendment 2's goal — a fully T4 matrix with no per-GPU
caveat in Paper 2 — is on track.

**Kaggle session 4 COMPLETE (merged 24 Aug 2026).** `vgg19_fe` ran on T4 at its committed
batch size of 64, early-stopped at epoch 13 (best epoch 8), 76 min against a 4.8 h worst case:

| run | best epoch | stopped at | time | val_acc | test_acc | test_auc |
|---|---|---|---|---|---|---|
| vgg19_fe | 8 | 13 (early) | 76 min | 0.9054 | 0.9055 | 0.9669 |

**This is the weakest row in the matrix, and it is a real architectural result rather than a
fault.** The evidence that it is sound: AUC 0.9669 is nowhere near chance, the confusion
matrix is balanced (9090/910 real, 981/9019 fake), `trainable_params` is 8194 — the classifier
head alone, correct for feature-extraction mode — and the learning curve shows genuine
learning from 86% to 90.5%. VGG19 is the oldest backbone in the set, without residual
connections, and its frozen penultimate features are simply less linearly separable than
those of ResNet, DenseNet or ViT. The feature-extraction ranking now reads
vgg19 (90.55) < resnet50 (92.83) ≈ efficientnet_b0 (92.86) < densenet121 (93.48) <
vit (94.75), which is a coherent story for Paper 2's discussion: representation quality under
a frozen backbone tracks architectural generation.

One honest caveat to carry into the write-up: epoch 7 shows a val_loss spike to 0.4426 against
a ~0.26 neighbourhood, with val_acc dropping to 85.15% before recovering at epoch 8. That is
SGD instability at lr 0.01 over a large frozen feature space, not divergence — the run
recovered and its best epoch came after the spike. Report it; do not smooth it away.

**Matrix status at the close of session 4: 8 of 10 rows**, every row Tesla T4, seed 42,
`cifake_split_seed42.csv`, 90,000 training images, each at its committed batch size.

**Kaggle session 5 COMPLETE (merged 25 Aug 2026) — `vgg19_ft` is the new matrix leader.**
216 min against an 8.0 h worst case, early-stopped at epoch 14 (best epoch 9):

| run | best epoch | stopped at | time | val_acc | test_acc | test_auc |
|---|---|---|---|---|---|---|
| vgg19_ft | 9 | 14 (early) | 216 min | **0.9819** | **0.9791** | **0.9979** |

**The headline finding of the matrix is an inversion, and it belongs in Paper 2's discussion.**
VGG19 is *last* under feature extraction (90.55%, the weakest row in the whole matrix) and
*first* under fine-tuning (97.91%, the strongest). Its fe→ft gain of +7.36 points is nearly
double the next largest:

| backbone | fe | ft | gain |
|---|---|---|---|
| vgg19 | 90.55 | **97.91** | **+7.36** |
| efficientnet_b0 | 92.86 | 97.56 | +4.69 |
| densenet121 | 93.48 | 97.60 | +4.11 |
| resnet50 | 92.83 | 95.93 | +3.10 |

The reading that fits the evidence: VGG19's *frozen* ImageNet features encode object-level
semantics that transfer poorly to CIFAKE, where the discriminative signal is low-level
generative texture and frequency artefact. Once all 139 M parameters are unfrozen, its plain
stacked-convolution design has both the capacity and the inductive bias to relearn exactly
those low-level filters. This is a claim about *this dataset at 32→224 upsampling*, not a
general statement that VGG19 beats modern backbones — say so explicitly.

**A limitation that must be disclosed, not buried.** Three runs stopped at `max_epochs` with
their best epoch at or adjacent to the ceiling — `resnet50_fe` (best 30/30), `resnet50_ft`
(best 30/30) and `efficientnet_b0_fe` (best 29/30). Their validation loss was still improving
when the 30-epoch budget ended, so **those three numbers are lower bounds, not converged
results.** This matters most for `resnet50_ft`: it is the weakest fine-tuned row (95.93%) and
it is also the only fine-tuned run that never early-stopped, so its last-place ranking among
the ft configurations is partly an artefact of the epoch budget. Paper 2 must either say this
plainly wherever the ft ranking appears, or rerun those three at a higher ceiling. The
remaining six runs converged and early-stopped on their own, so they are directly comparable.

**Matrix status at the close of session 5: 9 of 10 rows**, 16.5 h measured GPU time, every
row Tesla T4 / seed 42 / same split / 90,000 train images / committed batch size. Only
`vit_base_patch16_224_ft` (session 6) remained at that point.

Two process notes attach to this launch. First, the push was executed by Claude rather than
Rohit, on Rohit's explicit instruction with the token supplied inline; **the standing
execution split in CLAUDE.md §1 is unchanged** and this is recorded as a one-off override, not
a precedent. Second, two credentials were exposed during the session and await rotation — a
GitHub fine-grained PAT that had been pasted into `.gitignore` (never committed; confirmed by
a full-history `git log -S` scan) and the Kaggle API token used for this push. Details and
rotation steps are in `handoff.md`.

**Kaggle session 6 COMPLETE (merged 26 Aug 2026) — THE MATRIX IS CLOSED AT 10 OF 10, and
`vit_base_patch16_224_ft` is the final leader.** 204 min against a 6.8 h worst case,
early-stopped at epoch 15 (best epoch 10):

| run | best epoch | stopped at | time | val_acc | test_acc | test_auc |
|---|---|---|---|---|---|---|
| vit_base_patch16_224_ft | 10 | 15 (early) | 204 min | **0.9898** | **0.9889** | **0.9994** |

**The completed matrix.** Every row: Tesla T4 15 GB, seed 42, `cifake_split_seed42.csv`,
90,000 training images, committed batch size. Total measured GPU time **19.89 h**.

| backbone | fe | ft | fe→ft gain |
|---|---|---|---|
| ViT-B/16 | **94.75** | **98.89** | +4.14 |
| VGG19 | 90.55 | 97.91 | **+7.36** |
| DenseNet121 | 93.48 | 97.60 | +4.11 |
| EfficientNet-B0 | 92.86 | 97.56 | +4.69 |
| ResNet50 | 92.83 | 95.93 | +3.10 |

**Three findings the discussion should be built on, in order of strength.**

1. **ViT wins both modes outright** — best frozen representation (94.75, above every CNN) and
   best fine-tuned model (98.89). On 20,000 test images the standard error of a proportion at
   this accuracy is about 0.1 pp, so ViT-ft's ~1 pp lead over VGG19-ft is roughly 7 standard
   errors: a real separation, not seed noise. This is the cleanest headline in the matrix and
   it directly answers the CNN-vs-transformer question the project set out to ask.
2. **The VGG19 inversion survives completion** — last under feature extraction, second under
   fine-tuning, the largest fe→ft gain in the matrix at +7.36. Interpretation unchanged (see
   the session-5 note); scope it to this dataset.
3. **The 97.5–97.9 band is a three-way tie, not a ranking.** VGG19-ft 97.91, DenseNet121-ft
   97.60 and EfficientNet-B0-ft 97.56 sit within 0.35 pp — at ~0.1 pp standard error, only
   VGG19-ft is even marginally separable from the other two, and DenseNet vs EfficientNet
   (0.04 pp apart) is pure noise. Paper 2 must report these three as statistically
   indistinguishable on one seed rather than ordering them.

**The lower-bound disclosure is now confirmed against the complete matrix.** Exactly three of
the ten runs stopped at `max_epochs` with the best epoch at or next to the ceiling —
`resnet50_fe` (30/30), `resnet50_ft` (30/30), `efficientnet_b0_fe` (29/30). All seven other
runs early-stopped on their own. Session 7 (§10) reruns those three at `max_epochs: 50`.

**Gate G3 is fully closed:** all ten rows sane on validation accuracy, every confusion matrix
balanced, no collapsed class, fe below ft in every backbone pair, one hardware string across
the whole matrix. **A4 (Grad-CAM galleries + cross-generator evaluation) is now unblocked**,
with the checkpoint transfer as its practical gate.

**Quota position after session 6 (estimate, not a reading).** 19.89 h measured training time
× the observed ~1.25 session overhead ≈ **24.9 h of the 30 h weekly allowance**, leaving
roughly 5 h. **Session 7's 7–11 h worst case does not fit what remains** — it waits for the
quota reset unless the week has already rolled over. Check the quota page before launching.

### A3 [was B2–B4] — the 10-run matrix, batched into GPU sessions.

- Run order = Table 2 (runs 1–10). Before any session: assert every matrix config has
  `smoke_subset: null` and `runs_csv: results/runs.csv`.
- **Batching:** sessions sized from the A2 per-architecture calibration with **at least 30%
  margin under the session cap**. Light CNN runs may pair two to a session; **VGG19-ft and
  ViT-ft run one per session** (rule, not preference — a killed session then costs one run).
  The driver cell invokes `train.py` as a subprocess per config and **continues on failure**,
  so one crashed run cannot sink the session's other runs.
- **Interruption policy (explicit):** restart-from-scratch is the accepted recovery for a
  killed run — no resume-from-checkpoint machinery; the long runs are isolated per session
  to cap the loss. Before launching any session, confirm remaining weekly quota covers its
  calibrated estimate; if quota runs dry, remaining runs queue for the reset in Table 2
  order.
- **Results round-trip:** every session's `runs.csv` rows, artefact directories, and **all
  produced `best.pt` checkpoints** are downloaded and merged (via `merge_runs.py`) **before
  the next session launches** — all ten checkpoints get archived locally, not just the better
  five; the Kaggle account must not be a single point of failure for anything. Checkpoints
  additionally stay in the notebook's versioned output; each session also copies the prior
  sessions' **whole `<run_id>/` artefact directories** forward into its own output (not just
  `best.pt` — `config_used.yaml` must travel with the checkpoint or `eval.py`/`gradcam.py`
  cannot load it), so the latest version always carries the full set (this also neutralises
  the multi-version-attach uncertainty).
- **Sanity gate G3 (after the FIRST session, runs 1–2):** read `val_acc` — not the test
  columns, which stay untouched until numbers are final (§8.4). Fine-tuned CNN validation
  accuracy on CIFAKE is expected in the mid-90s (the CIFAKE paper's small-CNN baseline is
  ≈93%, C51); a value near 50% means a pipeline bug (label mapping, normalisation,
  frozen-everything) — stop, debug locally, do not spend quota.
- Budget, corrected to match §4 and CLAUDE.md §12: 15–30 GPU-h for the core matrix plus
  ~5 GPU-h for A4/A5 → **20–35 GPU-h total**. At 30 h/week the matrix worst-case spills into
  a second quota week; that is the accepted plan, not a failure.

### A4 [was B5] — Grad-CAM galleries + cross-generator evaluation.

- Grad-CAM: for each backbone's better checkpoint (by val_loss), galleries per the A1.5
  selection rule → `figures/gradcam/` (committed — contact sheets in A6 assemble from these
  PNGs, since a clean checkout has no checkpoints).
- Cross-generator, in order: (i) attach `yangsangtai/tiny-genimage` and verify per-generator
  val counts, the `nature` real images' provenance, **and the file format / compression
  history of `ai` vs `nature` images per generator** (a JPEG-vs-PNG asymmetry is itself a
  detectable cue — record it; if present it is a stated caveat in Paper 2); (ii) run 10
  checkpoints × 4 generators × 2 conditions = 80 `crossgen.csv` rows, evaluation only,
  checkpoints from the forward-copied notebook output (or CPU sessions if quota is tight).
- Round-trip applies here too: `crossgen.csv` rows (merge key `(run_id, generator,
  condition)`), per-cell `genimage_<generator>_<condition>/` artefact dirs, and the gallery
  PNGs are downloaded and merged before the next session.

**Gate G4:** 80 crossgen rows merged into the repo, spot-checked against two manually
recomputed cells; galleries committed and reproducible from the seeded selection; the three
tiny-genimage verifications recorded (closing the A1 `[VERIFY]`).

### A5 [was B6] — ablations (if the matrix behaved).

Write the three ablation YAMLs (`resnet50_ft_noaug.yaml`, `resnet50_ft_res64.yaml`,
`resnet50_ft_res128.yaml`) — they do not exist yet — then three short runs, same pipeline,
same round-trip. **Gate G5:** 3 coherent rows + artefact dirs merged into the repo.

### A6 [was B7] — consolidation.

`code/make_tables.py` + `code/make_figures.py` generate every Paper 2 table (per-run metrics,
params/time, crossgen matrix) and every CSV-derived figure (learning curves, ROC overlays,
confusion matrices) from `runs.csv`/`crossgen.csv` and the per-run artefact CSVs alone;
Grad-CAM contact sheets assemble from the committed `figures/gradcam/` PNGs. **Canonical-run
rule:** reruns produce new timestamped run_ids, so `runs.csv` may legitimately hold several
rows per (model, mode); a committed manifest `results/canonical_runs.txt` lists the exact
run_ids the tables use, and `make_tables.py` fails loudly if a manifest id is missing or a
(model, mode) has no manifest entry. **Gate G6:** regenerating tables and CSV-derived figures
from a clean checkout reproduces them; every Paper 2 table/figure file exists under
`results/tables/` and `figures/`. After G6, Paper 2 drafting can begin whenever Semester 8
(or the guide) allows.

### Decisions/dependencies on Rohit under acceleration

| # | Item | Blocks |
|---|---|---|
| D1 | Code transport — default: private GitHub + Kaggle Secrets PAT, applies unless Rohit objects by 22 Aug | A2 onward |
| D2 | Role split (CLAUDE.md item 4) — required before per-member task claims in any WPR | WPR content only |
| D3 | Guide's answer on early code work appearing in the Minor WPR track — now covers ANY Minor WPR (5–12), not just WPR 12 | Any Minor WPR mentioning Track B |
| D4 | Browser-side Kaggle actions: enabling GPU/Internet, launching sessions, downloading outputs | A2–A5 |

### What acceleration does NOT change

No result touches Paper 1 or any Semester 7 report section. Minor WPRs report literature work
only (see preamble) and upload on their Wednesdays. Guide-review Week 12 stays real-time and
Kaggle-session-free. The split file is never regenerated. The 20k test set is touched only
for final evaluation; even sanity gates read validation numbers. Bitwise reproducibility
across different hardware is not claimed anywhere; what is claimed is protocol
reproducibility: same seed, same split, same config, logged versions.

## 8. Reproducibility and integrity rules

Concrete form of the CLAUDE.md §6 rules:

1. One YAML config per experiment in `sem8_major/configs/`, named `<model>_<mode>.yaml` with mode `fe` or `ft`. Scripts read the config; no hyperparameter is written inside a script.
2. Every run logs seed, split file path, epochs, learning rate, optimiser, batch size, hardware string (GPU model + VRAM), parameter counts, torch and timm versions, and wall-clock training time into its `runs.csv` row.
3. Results are written to CSV as they are produced. No hand transcription into any document.
4. The 20,000-image CIFAKE test set is touched only for final evaluation. Model selection uses the validation split.
5. The split file is committed and never regenerated. Regenerating it invalidates every earlier run.
6. **Paper 1 firewall.** No result, figure or number from this track appears in Paper 1 or in any Semester 7 report section. Results live under `sem8_major/results/` only.
7. **WPR question for the guide.** Semester 7 WPRs are the Minor Project track and cover literature work. Whether the early code work may be reported in the Minor track is the guide's decision — under acceleration (§7a) this applies to **every** remaining Minor WPR (5–12), not just WPR 12. Ask before writing it into any of them. If the answer is no, the work is still recorded here and carries into the Major Project WPR track.
8. **Git.** The project folder is not currently a git repository. `git init` is now a scheduled step: §7a A1 step 0, with `sem8_major/data/` and checkpoint files gitignored, so config and split changes are traceable.
9. Role assignment is deliberately absent from this plan. Open item 4 (role split between the three team members) is unresolved, and tasks are not assigned to individuals until Rohit defines it.

## 9. Open points

| # | Item | Needed by |
|---|---|---|
| 1 | GenImage access path — RESOLVED 18 Aug 2026, see `data/genimage_access_note.md`: primary route is the Tiny-GenImage Hugging Face mirror (35k images, all four target generators, CC-BY-NC-SA-4.0), fallback is the official Google Drive release; per-generator counts and real-image provenance still `[VERIFY at download]` | — |
| 2 | Kaggle GPU quota — RESOLVED 20 Aug 2026: 30 h GPU + 20 h TPU per week, confirmed from the account quota page | — |
| 3 | Role split between Rohit, Vishal and Hardik (CLAUDE.md open item 4) — no task in this plan is assigned until it is settled | Before B2 |
| 4 | Semester 8 calendar dates are unknown, so phases S8-1 to S8-3 carry relative weeks only; convert to dates when the calendar is published | Start of Semester 8 |
| 5 | Guide's decision on whether early implementation work may be reported in the Minor Project WPR track | Before WPR 12 |

## 10. Publication merge plan `[CONFIRMED — Rohit, 25 Aug 2026; guide-approved]`

The publication goal changed on 25 August 2026, with Dr. Richa Gupta's approval: **one
published research paper**, merging the Semester 7 review (Paper 1) and this track's
experimental work (Paper 2), instead of two separate submissions. Nothing changes on the
Amity side — two semester projects, two reports, two WPR tracks — and nothing changes in
phases A4–A6 or the §8 rules. Paper 2 is still drafted in full: it is the core of the
Semester 8 major project report and the experimental half of the merged paper. Neither
paper is submitted to a venue on its own.

### Session 7 — rerun session (slots between session 6 and A6 consolidation)

Three matrix rows are lower bounds, not converged results: `resnet50_fe`, `resnet50_ft`
and `efficientnet_b0_fe` stopped at the 30-epoch ceiling with validation loss still
improving (§7a session-5 note). For a published paper Rohit decided on 25 Aug to rerun
them rather than carry the disclosure:

- **Kaggle T4 only**, preserving the all-T4 matrix (amendment 2's goal); the Victus is
  not used for these.
- Launched only after session 6's results are downloaded and merged.
- The three configs at `max_epochs: 50`; early stopping patience 5 and every other
  hyperparameter unchanged.
- **Split into TWO sessions (decided 26 Aug, forced by the A3 batching rule).** Projected
  from measured per-epoch times × 50 epochs: resnet50_fe 200 min, resnet50_ft 317 min,
  efficientnet_b0_fe 163 min — **11.3 h for all three, which exceeds the ~9 h session cap
  outright**, and A3 requires at least 30% margin under it. Therefore:

  | Session | Runs | Projected | Margin under 9 h |
  |---|---|---|---|
  | 7 | `resnet50_fe_e50` + `efficientnet_b0_fe_e50` | 363 min (6.04 h) | 33% |
  | 8 | `resnet50_ft_e50` | 317 min (5.28 h) | 41% |

  Both are worst cases at the full 50-epoch ceiling; early stopping (patience 5, unchanged)
  should end them sooner. Check remaining weekly quota first — after session 6 roughly 5 h
  of the 30 h allowance remains, so **neither session fits until the quota resets**.
- **Configs:** `resnet50_fe_e50.yaml`, `resnet50_ft_e50.yaml`, `efficientnet_b0_fe_e50.yaml`,
  each generated from its original with **only `max_epochs` changed (30 → 50)** — verified by
  diff against the originals, no other line differs. Because only the epoch *budget* changes
  and no hyperparameter does, the reruns stay directly comparable to the other seven matrix
  rows; this is a convergence fix, not an ablation.
- Reruns get new timestamped run_ids; the old rows stay in `runs.csv` untouched, and
  A6's `results/canonical_runs.txt` manifest selects which rows the tables use — the
  mechanism §7a A6 already defines.
- Generated via `notebooks/make_a3_notebook.py` (new session entry); Claude prepares,
  Rohit pushes/launches per the execution split.

### Session 7 result `[COMPLETE — merged 26 Aug 2026; session 8 result follows]`

Both session-7 runs finished; the outcome splits into a genuine fix and a genuine
confirmation, and the two must not be described the same way.

| run | original (30 ep) | rerun (50 ep) | delta |
|---|---|---|---|
| resnet50_fe | best 30/30, `max_epochs`, val 93.01, test 92.83, AUC 0.9807 | best 49/50, `max_epochs`, val 93.17, test 92.98, AUC 0.9815 | +0.16pp val, +0.15pp test |
| efficientnet_b0_fe | best 29/30, `max_epochs`, val 92.67, test 92.86, AUC 0.9802 | best 29/50, **`early_stopping`**, val 92.67, test 92.86, AUC 0.9802 | +0.00pp — identical |

**`efficientnet_b0_fe` is now CONFIRMED CONVERGED, and its lower-bound flag is retracted.**
Given 20 more epochs of room, training found the same best epoch (29) and produced bit-for-
bit identical validation and test numbers, this time with `stop_reason=early_stopping`
instead of `max_epochs`. The original number was never a lower bound — it was the converged
result; the 30-epoch ceiling simply cut off the run one epoch before the patience-5 window
could formally close. This row needs no further disclosure in Paper 2 beyond noting the
confirmation.

**`resnet50_fe` improved, but the epoch-ceiling problem is NOT fully resolved — say so
plainly.** It ran the full 50 epochs and `best_epoch` landed at 49 of 50: by the strict
`stop_reason=max_epochs` criterion, it is technically still not converged. The learning curve
tells the practical story, though: `val_loss` moves only 0.1775 → 0.1740 across the final ten
epochs and `val_acc` sits in a 93.04–93.24% noise band with no clear upward trend. This is
diminishing returns, not an open trajectory — the model has, for practical purposes, plateaued
even though patience-5 never formally triggered. **Recommendation: do not chase this further
with another epoch-ceiling increase.** The gain from 30→50 epochs was +0.15pp test accuracy;
a further extension would cost more GPU-hours for a return this analysis expects to be smaller
still. Paper 2 reports the 50-epoch number and states the epoch-ceiling caveat narrowly for
this one row, rather than implying it applies to the matrix broadly.

**Consequence for `resnet50_ft` (session 8, not yet run):** no inference is drawn about it
from this result. It is the heaviest of the three original lower-bound rows and the only
fine-tuned one — session 8 stands on its own evidence when it lands.

**Matrix status: unchanged, still closed at 10 canonical rows** (`runs.csv` now holds 12 —
the 10 matrix rows plus these two 50-epoch reruns as additional, separately timestamped rows,
per the plan's rerun-and-manifest design). No `canonical_runs.txt` exists yet (created at A6);
when it is, it should point at the 50-epoch `resnet50_fe` row (the confirmed-better number)
and either the 50-epoch or 30-epoch `efficientnet_b0_fe` row (now provably identical, so the
choice is immaterial) — recorded here so A6 does not have to re-derive this reasoning.

### Session 8 result `[COMPLETE — merged 4 Sep 2026; rerun phase closed, 3 of 3]`

| run | original (30 ep) | rerun (50 ep) | delta |
|---|---|---|---|
| resnet50_ft | best 30/30, `max_epochs`, val 95.66, test 95.93, AUC 0.9925, 190 min | best 48/50, `max_epochs`, val 96.32, test 96.51, AUC 0.9941, 323 min | +0.66pp val, +0.58pp test |

Run `resnet50_ft_20260827-0206`: Tesla T4 15 GB, torch 2.10.0+cu128, timm 1.0.26, seed 42,
`cifake_split_seed42.csv`, 90,000 train images, batch 128 — identical to the matrix row in
every logged field except `max_epochs`, `best_epoch`, time and the metrics (config diff:
only `max_epochs` and `run_id`). Wall-clock 323 min against the 317 min projection (1.02×),
inside the 340 min session budget.

**Reproducibility evidence — record it in Paper 2:** the rerun's `learning_curve.csv`
matches the original run epoch-for-epoch across all 30 shared epochs (verified by diff,
4 September 2026). Same seed, same hardware and same library versions reproduced the same
trajectory, so the 30-epoch row is a strict prefix of the 50-epoch row and the whole
improvement is attributable to the extra 20 epochs.

**Convergence verdict: improved, still formally at the ceiling, not worth a third run.**
`best_epoch` 48 of 50 with `stop_reason=max_epochs` — the same outcome as `resnet50_fe`. The
tail is diminishing returns: `val_loss` fell 0.0143 over epochs 31–40 but only 0.0042 over
41–50 (0.1004 → 0.0962, band 0.096–0.104); `val_acc` sat in a 95.99–96.35% band; train
accuracy 97.17% vs validation 96.32% at epoch 50 — a 0.9 pp gap, no overfitting. A further
20 epochs would be expected to buy well under the +0.58 pp this one did, for another ~5 GPU-h.
**Decision recorded: the epoch ceiling is not extended again for either ResNet50 row.**

**How Paper 2 words it:** one architecture-level caveat rather than two row caveats —
ResNet50 under the committed SGD learning rates (0.01 fe, 0.001 ft) converges more slowly
than the other four backbones and did not trigger patience-5 within 50 epochs in either
mode; both ResNet50 rows are therefore reported at the 50-epoch ceiling with a flat tail,
while the seven other matrix rows early-stopped on their own and EfficientNet-B0-fe is
confirmed converged (session 7).

**The 25 Aug concern is settled: resnet50_ft's last place among the ft rows is NOT an
epoch-budget artefact.** Twenty extra epochs closed 0.58 pp of the 1.63 pp gap to the
three-way tie band (vgg19 / densenet121 / efficientnet_b0, 97.56–97.91); 1.05 pp remains,
about 8 standard errors on the 20,000-image test set (SE ≈ 0.13 pp at 96.5%). Canonical ft
ranking: vit 98.89 > vgg19 97.91 > densenet121 97.60 ≈ efficientnet_b0 97.56 > resnet50
96.51. Canonical fe ranking: vit 94.75 > densenet121 93.48 > resnet50 92.98 ≈
efficientnet_b0 92.86 > vgg19 90.55. ResNet50's fe→ft gain becomes +3.53 (was +3.10 on the
30-epoch rows), still the smallest of the five; the VGG19 inversion (+7.36) and the ViT lead
are unaffected.

**Matrix status after session 8:** `runs.csv` holds 13 rows — the 10 matrix rows plus three
separately timestamped 50-epoch reruns, nothing overwritten. Every row: `Tesla T4, 15 GB`,
torch 2.10.0+cu128, timm 1.0.26. Measured GPU training time 19.89 h (matrix) + 10.23 h
(reruns) = 30.12 h. **`canonical_runs.txt` (created at A6) should list
`resnet50_fe_20260826-0457`, `resnet50_ft_20260827-0206`, either `efficientnet_b0_fe` row
(metrics identical), and the seven original rows for the remaining (model, mode) pairs.**
No Kaggle run is pending; the next phase is A4 (§7a), whose practical gate is getting all
canonical checkpoints onto one machine (the complete 2.2 GB pile is on the old laptop).

### P-phases (after A6/G6; replaces the two-paper endpoint of S8-2)

| Phase | Content |
|---|---|
| P1 | **Paper 2 draft** (was S8-2, unchanged in content): full experimental paper per the Karki et al. schema; every number generated from `runs.csv`/`crossgen.csv` by the A6 scripts, never hand-transcribed. Feeds the Sem 8 major report and the merge. |
| P2 | **Shape + venue gate**, with the guide, in one sitting: (a) merged-paper shape — hybrid review+experiment (review survives as condensed taxonomy + 48-study table + gap analysis; ~12–14k words; needs a length-tolerant venue) vs experimental paper with deep related work (review compressed to 2–3 pages; 48-row table trimmed or moved to supplementary); (b) venue (CLAUDE.md open item 5); (c) authorship order; (d) AI-assistance disclosure requirement (CLAUDE.md open item 18). The shape decision is deliberately deferred to here — Rohit, 25 Aug: decide from how the results turn out. |
| P3 | **Content map**: Paper 1 §§0–8 × Paper 2 sections → merged outline, keep/condense/drop per block, with an explicit dedupe list. Known duplications to resolve: CIFAKE/GenImage described in both papers (once, in Methods); metrics equations in both (once, in Methods); Paper 1's gap analysis rewritten from future tense into the merged paper's contributions; conclusions merged. Gate: Rohit approves the map before any prose is assembled. |
| P4 | **Merged draft assembly** in a new top-level `publication/` directory (created then, not before): sections from the Sem 7 section files + P1's sections; reuse `sem7_minor/submission/build/build_v2.py` (citation conversion, figure/table renumbering) and the `make_docx.ps1` export path, retargeted at the merged manuscript. References = union of the C-keyed sets, trimmed to venue norms; every kept reference re-verified in `verification_log.md` fashion. |
| P5 | **Integrity pass**: Rohit's own-voice rewrite over all prose (mandatory regardless of any checker result); citation re-verification after the rewrite; every number traced to its CSV; terminology consistency; no duplicated tables or figures. |
| P6 | **Venue formatting + similarity check.** Known risk, handled by disclosure: the Sem 7 report went through the department plagiarism check and the final reports are submitted to Amity — if those land in a Turnitin-style repository, the merged paper will self-match Rohit's own coursework. Standard handling is disclosure to the venue (prior coursework/thesis reuse); ask the department whether submissions are stored. Never any rewording/humanizer tool. |
| P7 | **Guide sign-off → submission.** All portal and submission actions are Rohit's, per the execution split. |

All P-phases are relative until the Semester 8 calendar is known. Risks carried openly:
venue length limit if the hybrid shape wins (mitigation: supplementary material, decided
at P2); review staleness by submission time (a bounded literature refresh at P3 only if
the guide asks; default is no new literature); self-similarity with Amity submissions
(P6 disclosure route).
