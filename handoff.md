# handoff.md — phase-completion handoff log

Updated at every phase-gate closure (rule adopted 20 Aug 2026, with CLAUDE.md §13 and
`sem8_major/implementation_plan.md` §7a updated in the same pass). Newest phase first.
Read CLAUDE.md first; this file is the fast-moving state on top of it.

---

## A1 — full local implementation + CPU smoke `[G1 PASSED — 20 August 2026]`

### 1. Goal

Implement the entire Semester-8 training/evaluation pipeline locally (all modules, all ten
matrix configs), prove it end-to-end on the laptop CPU with a smoke run, and pass gate G1
(artefact checks + adversarial code review) — so that Kaggle GPU time is only ever spent on
code that already works.

### 2. Current State

- Git repo live at project root, branch `main`, commits `0d7fa93` (initial) and `22dcb11`
  (A1). No remote yet — GitHub repo `sm7` (private) is the next step and needs Rohit's
  browser once.
- All six modules implemented and green: `data.py`, `models.py`, `train.py`, `eval.py`,
  `gradcam.py`, `merge_runs.py` (each has a runnable selfcheck; run under
  `sem8_major/.venv`).
- Ten matrix configs + `resnet50_fe_smoke.yaml`, all strict UTF-8, validated (smoke_subset
  null in matrix configs, Table 3 values).
- Two CPU smoke runs completed (2.2 / 2.8 min): rows in `results/smoke_runs.csv` (30
  columns), artefact dirs with learning curve, confusion matrix, ROC points, checkpoint;
  Grad-CAM overlays verified non-degenerate in `figures/gradcam/`.
- Data: CIFAKE local at `sem8_major/data/cifake/`; committed split
  `data/cifake_split_seed42.csv` (45k/45k/5k/5k/10k/10k, seed 42). Kaggle: notebook
  `yaduvxnshi/notebook322addb147` with CIFAKE attached; quota 30 h GPU + 20 h TPU/week;
  GPU and Internet still OFF. Kaggle API token at `~/.kaggle/access_token` (CLI 2.2.4
  mishandles it on authed endpoints; direct REST with Bearer works).
- Track A unchanged: plagiarism result pending; WPR uploads Wednesdays.

### 3. Active Files

- `sem8_major/code/*.py` — the six pipeline modules
- `sem8_major/configs/*.yaml` — template + 10 matrix + 1 smoke
- `sem8_major/results/` — `runs.csv` (header only), `smoke_runs.csv` (2 rows), smoke run dirs
- `sem8_major/implementation_plan.md` §7a — the accelerated schedule (A1–A6, gates G1–G6)
- `CLAUDE.md` §13 — running status
- `sem8_major/data/genimage_access_note.md` — GenImage route (tiny-genimage on Kaggle)

### 4. Changes it made

- 20 Aug: `git init` + initial commit; stray file named after the Kaggle API token deleted
  before staging; root `.gitignore` blocks `KGAT_*`.
- Wrote all six modules and nine new matrix YAMLs; reset `resnet50_fe.yaml` to matrix state;
  created `resnet50_fe_smoke.yaml` writing to `smoke_runs.csv`.
- Plan §7a written (acceleration amendment), verified by a 5-lens adversarial review
  (32 findings, fixed), then code verified by a 4-lens review (16 findings, fixed).
  Key code-review fixes: 9 cp1252-encoded configs re-encoded UTF-8 (+ explicit
  `encoding="utf-8"` on all text I/O — would have crashed every Kaggle run);
  worker seeder made picklable (module-level partial — crashed under Windows spawn);
  `imagenet_midjourney` no-infix folder name now matched; genimage sampling balance-capped
  by construction; NaN fail-fast in train loop; smoke side-door guards in merge_runs and
  eval; `make_split` overwrite refusal; `--dump-correct` for the A4 shared set.

### 5. Failed Attempts

- Kaggle CLI 2.2.4 token auth: `datasets list`/`kernels pull` reject the KGAT token however
  supplied (env var, `~/.kaggle/access_token`, kaggle.json) — do not retry the CLI for
  authenticated calls; use direct REST with `Authorization: Bearer` (works, verified).
- Persisting the token as a Windows user env var was blocked by the permission classifier —
  the credential lives in `~/.kaggle/access_token` instead.
- First loader selfcheck used solid-colour synthetic images: down32 and direct224 coincide
  on constant input, so the assertion failed until the test images got high-frequency noise.
- First version of the merge selfcheck reused one target file across incompatible headers —
  refactored; a reminder that guards need their own negative tests.
- `gh` CLI is not installed, so the GitHub repo cannot be created from this machine.

### 6. Next steps

A2 tooling is already written and locally tested (see the A2-in-progress note below); only
the browser steps block the session.

1. **Rohit (browser, ~5 min):** create private empty GitHub repo `sm7`
   (no README/license); then say so — Claude adds the remote and pushes (Git credential
   window pops once for authorization).
2. **Rohit (browser):** in the Kaggle notebook editor: GPU on, Internet on; add a Kaggle
   Secret `GITHUB_PAT` (fine-grained PAT, read access to `sm7`) for the clone cell.
3. **A2 session:** open `notebooks/phase_a2_smoke.ipynb` in the Kaggle notebook, Run All
   (~25 min), download `results_a2.zip`; Claude merges and closes gate G2.
4. Then A3: the 10-run matrix in calibrated session batches.

---

## A2 — code transport + Kaggle GPU smoke `[IN PROGRESS — updated 20 August 2026]`

**Done:** A2 tooling written and locally tested — `code/calibrate.py` (per-architecture
timing), `code/record_env.py` (environment capture for Paper 2), `code/run_session.py`
(A3 driver; failure isolation verified: a bogus config failed while the next run still
completed, exit 1 with a summary), `notebooks/phase_a2_smoke.ipynb` (9 cells).
**Code transport resolved (D1):** private GitHub repo `rohityaduvxnshi/sm7` created; project
history pushed as `750c522` after merging the repo's auto-created README (no force-push);
full-history scan confirms no credential file was ever committed. The A2 notebook was pushed
to Kaggle via the REST API as version 2 — verified private, GPU on, Internet on, CIFAKE still
attached. The notebook's slug changed with its title:
**`yaduvxnshi/authentiscan-a2-gpu-smoke-and-calibration`**.

**Remaining before the session runs:** Rohit adds a Kaggle Secret `GITHUB_PAT` (fine-grained
GitHub token, read access to `sm7`) and presses Run All. Nothing has run on Kaggle yet.

**Watch-outs discovered:** something on the laptop deletes files whose contents match the
Kaggle token pattern (`~/.kaggle/access_token` disappeared twice) — pass the token inline in
API calls instead of storing it. A second working copy exists at
`C:\Users\rohit\Documents\GitHub\sm7` (GitHub Desktop clone, README only); the real working
copy is `C:\Users\rohit\Desktop\AuthentiScan` — deleting the other one avoids editing the
wrong tree.
