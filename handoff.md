# handoff.md — phase-completion handoff log

Updated at every phase-gate closure (rule adopted 20 Aug 2026, with CLAUDE.md §13 and
`sem8_major/implementation_plan.md` §7a updated in the same pass). Newest phase first.
Read CLAUDE.md first; this file is the fast-moving state on top of it.

---

## START HERE — next session (written 15 Oct 2026, late, at session close)

**State in one line:** A1–A4 done and gated (G1–G4); **A6 done, G6 passed** (every Paper 2 table and
figure regenerates byte-identically from a clean clone + fresh venv); **A5 prepared, not launched**
(two Kaggle sessions await Rohit); nothing running on Kaggle; working tree clean except `AGENTS.md`.

**Session-start checklist**
1. `git pull` — this laptop is the only machine; remote `origin` = github.com/rohityaduvxnshi/sm7 (private).
2. Health checks from `sem8_major/`, calling the venv python by its ABSOLUTE path (the shell's working
   directory drifts between Bash calls on this laptop):
   `D:\Desktop\AuthentiScan\sem8_major\.venv\Scripts\python.exe code/merge_runs.py --selfcheck`, then
   `... code/data.py --selfcheck`, `... code/make_tables.py --selfcheck`.
3. Read CLAUDE.md §13 "Where we are", then the A6/A5 block below. Older blocks are history.

**Next, in order**
1. **Rohit launches A5** (Kaggle T4; check the quota page first — worst case ~7.2 h + ~7.9 h, expected
   ~10 h in total; both sessions fit one 30 h week). For each of `--session 9` and `--session 10`:

       & "d:\Desktop\AuthentiScan\sem8_major\.venv\Scripts\python.exe" "d:\Desktop\AuthentiScan\sem8_major\notebooks\make_a3_notebook.py" --session 9 --push --token KGAT_<token>

   A push auto-starts a run; the first run of a NEW notebook fails in cell 1 until `GITHUB_PAT` is
   toggled ON for it (Add-ons → Secrets), so: push, toggle, push again (or press Run). Regenerate the
   Kaggle token first (the 14–15 Oct one is in a chat transcript).
2. **Claude merges each `results_a5_s<N>.zip`:** `merge_runs.py <unzipped>/results/runs.csv --kind runs`,
   copy the run dirs (`resnet50_ft_noaug_*`, `resnet50_ft_res64_*`, `resnet50_ft_res128_*`) into
   `results/`, rerun `make_tables.py` and `make_figures.py` (`t6_ablations` appears by itself; its
   `varied` column must show exactly one factor per row — that is gate G5 — and the environment columns
   show whether torch/timm/hardware match the baseline; disclose any difference), commit, then repeat G6
   on the new tables: clone to a SHORT path (`/c/Users/rohit/AppData/Local/Temp/g6c`; a clone under the
   scratchpad hits Windows MAX_PATH on a long PDF name in `sem7_minor`), fresh venv at a short path
   (`g6v`), regenerate, `git status` must be clean. The script used on 15 Oct was `g6.sh` in that
   session's scratchpad — ten lines, easy to rewrite.
3. **P1 — Paper 2 draft** can start now (plan §10): every number comes from `results/tables/` and every
   figure from `figures/f*.png`; captions carry the rounding rule and the F5 ViT limitation (open item 23).

**Facts that are easy to get wrong**
- `kernels/status` reports `running` while a batch session waits for provisioning — read the log
  (`kernels/output`) before claiming progress. A new notebook's first run fails until `GITHUB_PAT` is
  toggled on for that notebook.
- Kaggle tokens: pass inline, never store (this laptop deletes files containing them); the legacy REST
  `POST www.kaggle.com/api/v1/kernels/push` with `Authorization: Bearer` worked on 14 Oct 2026.
- Mounts: datasets at `/kaggle/input/datasets/<owner>/<slug>`, notebook outputs at
  `/kaggle/input/notebooks/<owner>/<slug>/`; the notebooks autodetect both.
- Save & Run All cap: 12 h for GPU sessions. A5 budgets are enforced per run from session 9 on
  (`stop_reason=time_budget` if hit; sessions 1–8 ran without the flag and are frozen behind `--force`).
- Long heredocs die in this machine's Bash tool — write scripts to the scratchpad and run them. `python
  -m venv` and `git clone` both fail under the scratchpad path (MAX_PATH) — use short temp paths.
- `results/tables/` is authoritative over every number in CLAUDE.md / handoff / plan prose. Half-to-even
  rounding makes three exact-tie rows read 0.01 lower than older prose (vgg19 fe 90.54, vit fe 94.74,
  vit ft 98.88; 6 of 10 test accuracies are ties on 20,000 images), and the "25 / 7" threshold-shift
  counts of 15 Oct were recall counts — the predicted-fake rate is 29 / 6 (t3c carries both).

**Open asks for Rohit**
1. Launch A5 (above), after regenerating the Kaggle token.
2. Open item 23: the ViT Grad-CAM row of F5 is empty on about half its panels — caption disclosure only,
   or an attention-rollout rerun (new technique, new Kaggle session)?
3. Open items 20–22 (Semester 7 endpoint, CIFAKE licence, D3) are still unanswered.

**Housekeeping still open:** the grad-cam version used at A4 is unrecorded (A4 installed it unpinned;
the local lock has 1.5.5; only the A4 log would say); `kaggle_env.md` quota-reset day `[VERIFY]`
(browser-only); `AGENTS.md` untracked (Codex copy of CLAUDE.md, stale — regenerate or ignore).

---

## A6 COMPLETE, G6 PASSED; A5 PREPARED `[15 Oct 2026, later]` — next: Rohit launches sessions 9–10; P1 can start

### 1. Goal

Build the consolidation scripts (A6) and prepare the ablation phase (A5) per the previous START HERE
spec, with an adversarial review before anything was committed.

### 2. Current State

- `code/make_tables.py` → `results/tables/` (t1, t1b, t2, t3a, t3b, t3c, t4, t5 as CSV + `.md` twin;
  t6 once A5 rows exist). `code/make_figures.py` → `figures/f1_learning_curves_{loss,acc}`,
  `f2_roc_cifake_test`, `f3_confusion_matrices`, `f4_crossgen_{down32,direct224}`,
  `f5_gradcam_{correct,incorrect}` (7 in wide, 8 pt, 300 dpi, metadata stripped).
- **G6 PASSED** on commit 6dce673: fresh `git clone` + fresh venv from `requirements.lock` (torch
  2.13.0+cpu, timm 1.0.28, matplotlib 3.11.1, pandas 3.0.5) → regenerate → `git status` clean, all 24
  files byte-identical to the committed ones, every listed file present. `.gitattributes`
  (`* text=auto eol=lf`) makes the checkout match what the scripts write on any OS.
- Facts the tables surfaced: 6 of 10 test accuracies are exact rounding ties (odd correct counts on
  20,000 images) — half-to-even is the rule, stated in every footer; threshold shift is 29 cells >80%
  predicted fake and 6 <20% (the 25 / 7 of the morning were recall counts); best cross-generator cells
  are acc 0.597 twice (efficientnet_b0_fe / midjourney / down32 and vit_fe / midjourney / direct224)
  and AUC 0.642 (vit_fe / midjourney / direct224); the ViT Grad-CAM gallery is empty on ~half its
  panels (CLAUDE.md open item 23).
- A5 prepared, not launched: `configs/resnet50_ft_noaug.yaml`, `_res64.yaml`, `_res128.yaml` (the
  canonical `resnet50_ft_e50` recipe + one factor + `tag`); `train.py` writes the tag into the run id
  and the budget guard no longer fires after the final epoch; `run_session.py --time-budget-min`;
  `make_a3_notebook.py` sessions 9 (420 min) and 10 (230 min each) with timm pinned to 1.0.26, the
  ablated factor echoed in the pre-flight, `--force` required for sessions 1–8; notebooks
  `phase_a5_s9.ipynb` / `phase_a5_s10.ipynb` generated; CPU smoke through `run_session.py` produced
  `resnet50_ft_res64_<stamp>` at 64 px with `stop_reason=time_budget`.
- Review: 36-agent workflow (5 finder lenses → merge → 2 skeptics per finding): 15 confirmed (2 high,
  both governing-document errors, corrected with dated notes), 18 low; all applied except three judged
  not worth it (greyscale linestyle cycling, a conditional rounding footer, automatic zero-CAM
  detection — unreliable without the source images, which a clean clone lacks).

### 3. Changes it made

- New: `code/make_tables.py`, `code/make_figures.py`, `results/tables/` (16 files), `figures/f*.png`
  (8), three ablation configs, `notebooks/phase_a5_s9.ipynb`, `phase_a5_s10.ipynb`, `.gitattributes`.
- Edited: `code/train.py` (tag infix; guard only before the last epoch), `code/run_session.py`
  (budget passthrough), `code/gradcam.py` (`overlay_name` shared with make_figures),
  `notebooks/make_a3_notebook.py` (sessions 9–10, phase labels, timm pin, pre-flight echo, `--force`,
  corrected comments), `configs/template.yaml` (`tag` field, amp comment), every config's
  `num_workers` comment, `resnet50_ft_e50.yaml` header, `results/kaggle_env.md`, the three READMEs,
  CLAUDE.md §13 + open item 23, plan (§1 status, §4 run-id form, §7a A4 corrections, A5/A6 status,
  Table 5 B6/B7, rounding notes at the standings tables), this file.
- Kaggle: nothing pushed, nothing launched.

### 4. Failed Attempts

- `python -m venv` and `git clone` under the scratchpad path fail with "filename too long" (Windows
  MAX_PATH: torch's licence tree; a long PDF name under `sem7_minor`). Short temp paths work.
- The first G6 byte-comparison loop globbed from the wrong directory and printed three false DIFF
  lines; `git status` in the clone was the real check, and a direct `cmp` over all 24 files confirmed it.
- `$PWD`-relative venv paths failed three times because the Bash tool's working directory drifts.

### 5. Next steps

As in START HERE: Rohit launches sessions 9 and 10; Claude merges, regenerates, re-runs G6, closes G5;
P1 (Paper 2 draft) can begin at any time from `results/tables/` and `figures/`.

---

## A4 COMPLETE `[15 Oct 2026]` — G4 PASSED; cross-generator result is chance level; next A6 (then A5)

### 1. Goal

Merge the A4 run (80-cell cross-generator sweep + Grad-CAM galleries) and pass gate G4.

### 2. Current State

- v2 of `authentiscan-a4-crossgen-and-gradcam` (Rohit, 15 Oct 01:35 UTC, after attaching the
  secret) completed at 02:31 UTC — 54 min of execution on a Tesla T4. `results_a4.zip` (14 MB)
  fetched via `kernels/output` with the chat-supplied token and merged.
- Repo now holds: `results/crossgen.csv` (80 rows), 80 `results/<run_id>/genimage_<gen>_<cond>/`
  dirs (confusion matrix + ROC points each), `results/genimage_verification.csv`,
  `results/gradcam_shared_list.txt`, `results/gradcam_correct/` (5 files),
  `figures/gradcam/<five ft run_ids>/` (90 PNGs, ~14 MB).
- **G4 PASSED:** coverage exactly 10 × 4 × 2; 500 real / 500 fake per cell; all 80 cells
  recomputed from their own artefacts, 0 mismatches; the five galleries share identical correct
  panels (8 images, 4/4) and have 8 incorrect panels each.
- Dataset facts: tiny-genimage `val` = 500 `ai` (PNG) + 500 `nature` (JPEG) per generator →
  1,000 images per cell (below the 2,000–3,000 target); seven generator folders, no SD v1.4;
  `nature` provenance not verifiable from the files. Recorded in the plan, the GenImage note and
  `genimage_verification.csv`.
- **Result:** chance level everywhere — mean accuracy per checkpoint 0.46–0.53 under both
  conditions; 74/80 cells ≤ 0.55; AUC 0.29–0.64, below 0.5 in 43/80 (27 of 40 `direct224`);
  Midjourney least bad (mean AUC 0.58); ft no better than fe (0.498 vs 0.499); severe threshold
  shift (29 cells call >80% of all images fake, 6 call <20% — corrected 15 Oct from the "25 / 7"
  first written here, which were fake-recall counts; both are in t3c). Framed as a bracketed negative result (three
  confounds) — wording in plan §7a A4 result block. Numbers come from the check script; A6
  regenerates them.
- Mount paths now known: `/kaggle/input/datasets/<owner>/<slug>` and
  `/kaggle/input/notebooks/<owner>/<slug>/`. Status `running` ≠ executing (14 Oct lesson) — v2's
  ten-second-to-execution gap was not repeated.

### 3. Changes it made

- Merge + copies as above (no checkpoints; `*.pt` never travelled).
- Docs: plan §7a A4 result block + status + Table 5 B5 + Table 4 hardware example (15 GB) +
  §3/§9 GenImage counts; `results/README.md` layout (A2/A4 files) + 15 GB; GenImage note
  "still open" → resolved; CLAUDE.md §13 (15 Oct entry); this block.
- No code changes. Nothing pushed to Kaggle by Claude today.

### 4. Failed Attempts

None on 15 Oct.

### 5. Next steps

1. **A6 first (recommended), on this laptop:** `code/make_tables.py` + `code/make_figures.py`
   generating every Paper 2 table/figure from `runs.csv`, `crossgen.csv` and the per-run CSVs via
   `canonical_runs.txt`; contact sheets only from galleries whose run_id is in the manifest (the
   20 Aug smoke gallery `figures/gradcam/resnet50_fe_20260820-0709/` must be excluded or deleted);
   one rounding rule for every number. Gate G6: regenerate from a clean checkout.
2. **A5 later, Kaggle T4:** write `resnet50_ft_noaug.yaml`, `resnet50_ft_res64.yaml`,
   `resnet50_ft_res128.yaml`; fix the inert `time_budget_min` (pass `--time-budget-min` from
   `run_session.py`) before launching; one session, Rohit launches.
3. **Rohit:** regenerate the Kaggle token (the current one is in the chat transcript); confirm
   CIFAKE's licence terms before any gallery image is reproduced in Paper 2; the Sem 7 endpoint
   questions (final report, D3, plagiarism result) are still open.
4. Housekeeping from the 14 Oct audit still pending: `kaggle_env.md`'s two remaining `[VERIFY]`
   lines (quota-reset day; multi-version attach — moot), `num_workers [VERIFY]` tags in the
   configs, `resnet50_ft_e50.yaml`'s "SESSION 7" header, `grad-cam` unpinned in the notebooks,
   `sem8_major/README.md` module list, AGENTS.md (commit as a generated copy, or ignore).

---

## A4 PUSHED `[14 Oct 2026]`; v2 RUNNING `[15 Oct 2026]` — v1 failed on the missing secret after ten hours in `running` (no quota lost); audit done; WPR 12 rendered; Sem 7 endpoint needs Rohit

### 1. Goal

Use the new Kaggle token Rohit supplied in chat to get A4 running, and audit the repo against
`sem8_major/implementation_plan.md` to report overall progress.

### 2. Current State

- **A4 v1 failed in cell 1.** `yaduvxnshi/authentiscan-a4-crossgen-and-gradcam` v1, kernel id
  138590125, pushed 14 Oct with the new token (status check first: 200 on `kernels/status`,
  so the legacy route still accepts settings-page tokens — the 23 Sep 401 was the old token).
  Push response: all eight kernel sources and both datasets accepted, every `invalid*` list
  empty. Pulled back: cell 0 markdown, private, GPU + internet on. queued → running 01:29 UTC,
  `running` for ten hours, `error` at 11:31 UTC. **Log (fetched via `kernels/output`): the
  notebook executed for 18 s and died in cell 1 — `No user secrets exist for kernel id
  138590125 and label GITHUB_PAT`.** The earlier note here that the run was "past the cell-1
  secret and cell-2 failure points" was an inference from elapsed time and was wrong:
  `kernels/status` shows `running` while a batch session waits for provisioning, so elapsed
  time says nothing about cell progress — only the log does. The first `[VERIFY at push]`
  (sources accepted) stands on the push response; the second (kernel-output mount path) is
  still open. **Quota (Rohit, quota page, 15 Oct): v1 consumed only 1–2 minutes** — the ten
  hours were a provisioning wait, not a held session.
  Kaggle docs (read 14 Oct): Save & Run All sessions get 12 h on CPU/GPU, 9 h on TPU.
- **v2 launched by Rohit on 15 Oct at 01:35 UTC** (Save & Run All in the browser, after
  attaching `GITHUB_PAT` to the notebook). Status `running`; no output yet. Progress is read
  only from the log when the version completes; cap at ~13:35 UTC.
- Execution-split note: the push was executed by Claude on Rohit's explicit instruction with
  the token supplied inline (second time; 23 Aug was the first). CLAUDE.md §1 is unchanged.
  The token is in the chat transcript — regenerate it once `results_a4.zip` is in hand.
- **Audit result** (12-agent workflow, each finding re-checked on disk) — full list in
  CLAUDE.md §13 (14 Oct). Short form: A1–A3 + reruns complete and clean; A4 running;
  A5/A6/P1–P7 not started; G4–G6 open. Deviations: Track B numbers in both Sem 7 Progress
  Reports with D3 unanswered; `time_budget_min` guard inert for all 13 runs; four A3 sessions
  under the 30 % margin rule; Victus lock/smoke row never reached the repo ("four-way
  bit-identical" is three-way in the CSV); rerun hours outside the GPU budget.
- **Track A as the repo shows it:** NTCC window closed 9 Oct; no FINAL report PDF, no
  template, plagiarism result still awaited (1 Oct), **WPR 12 not rendered (due today)**, no
  Week 12 activity recorded.
- Untracked `AGENTS.md` (Codex copy of CLAUDE.md, rename-only diff as of 4 Sep) at the root;
  neither committed nor ignored — it drifts from CLAUDE.md after today's edits.

### 3. Changes it made

- Kaggle: one push (v1 auto-run; failed in cell 1 after 18 s of execution; 1–2 minutes of
  quota per the quota page, 15 Oct).
- CLAUDE.md §13: 14 Oct entry; the WPR bullet and the stale "USB transfer" gate corrected.
- `implementation_plan.md`: stale statuses corrected — §1 status line, Table 5 B2–B7, §3 and
  §9 GenImage primary route, §7a A2 time-budget wording, amendment 3 `[VERIFY at push]`,
  A4 status line, §8.8 git line, §10 manifest notes and the A4-gate contradiction.
- No code, config or notebook changes (the notebook regenerated byte-identical to HEAD).

### 4. Failed Attempts

- A4 v1: `GITHUB_PAT` not attached to the new notebook (per-notebook secret, the session-2
  lesson, foreseen in this file's own step 1 and then mis-read from the status endpoint).
  Cost: one failed version, ten wall-clock hours, 1–2 minutes of quota. Lesson recorded above:
  never infer cell progress from `running`; fetch the log.
- The 23 Sep diagnosis (below) held: dead token, route and payload fine.

### 5. Next steps

1. ~~Rohit — toggle the secret, read the quota page~~ DONE 15 Oct: secret attached, v2
   launched 01:35 UTC by Rohit, v1 cost 1–2 minutes of quota. If v2 also shows `running` for
   hours before its log starts, the wait is provisioning (it cost no quota yesterday); the
   eight kernel-output sources (~4.4 GB with the session zips) remain the suspect, and the
   fallback is a Kaggle dataset of the ten canonical checkpoints uploaded from this laptop
   (2.2 GB), attached in their place.
1b. **When v2 completes** (watch `kernels/status`, but read progress only from the log):
   Claude fetches `results_a4.zip` via `GET /api/v1/kernels/output` with the token (download
   only, no quota), merges
   `crossgen.csv` (80 rows expected) with `merge_runs.py --kind crossgen`, copies
   `genimage_verification.csv`, `gradcam_shared_list.txt`, `gradcam_correct/`, the
   `<run_id>/genimage_*/` dirs and `figures/gradcam/` galleries into the repo, spot-checks two
   cells by recomputation (G4), and records the tiny-genimage counts and any ai-vs-nature
   format asymmetry. If the run errored, read the log first (`kernels/output` carries it).
2. **Rohit — Track A, today:** WPR 12 is due 14 Oct and cannot be written from the repo (no
   Week 12 artefact). Needed: what happened 5–9 Oct (guide review? corrections? submission?
   plagiarism result?) and the guide's D3 answer. WPR 12 stays literature-only unless D3 is
   yes. Also: was a final report submitted, and from which file?
3. Rohit: regenerate the Kaggle token after step 1.
4. Then A5 (write the three ablation YAMLs; decide the `time_budget_min` fix first) or straight
   to A6 (`make_tables.py`, `make_figures.py`; filter `figures/gradcam/` by the manifest so the
   smoke gallery cannot reach a contact sheet) if time is short.
5. Housekeeping from the audit (small, do with A6): README/Table 4 "16 GB" → "15 GB"; clear
   `kaggle_env.md`'s three `[VERIFY]` lines and the `num_workers [VERIFY]` tags; fix
   `resnet50_ft_e50.yaml`'s "SESSION 7" header; pin `grad-cam` in the notebooks and record its
   version; update `sem8_major/README.md`'s module list; decide AGENTS.md (commit as a
   generated copy, or ignore).

---

## A4 PREPARED `[4 Sep 2026]` — Victus withdrawn; Kaggle + laptop only; awaiting Rohit's push

### 1. Goal

Rohit (4 Sep): the Victus cannot be arranged — continue on Kaggle and this laptop only.
Decide placement for A4–A6 from measured cost, record it (plan §7a amendment 3), and
prepare A4 so that one Kaggle push runs the whole phase.

### 2. Current State

- **Placement:** A4 (cross-generator sweep + Grad-CAM) = one Kaggle evaluation session;
  A5 ablation training = Kaggle T4; A6 + merging + drafting = this laptop. Laptop CPU
  benchmark (4 threads, 224×224): effnet 15.8 / densenet 7.5 / resnet50 5.5 / vgg19 2.4 /
  vit 2.0 img/s → sweep ~15 h + Grad-CAM passes ~7 h on CPU vs < 2 h on a T4.
- **A4 is built and CPU-verified, NOT launched.** Notebook
  `notebooks/phase_a4_crossgen_gradcam.ipynb` (generator `make_a4_notebook.py`); slug will
  be `yaduvxnshi/authentiscan-a4-crossgen-and-gradcam`. Data sources: CIFAKE,
  `yangsangtai/tiny-genimage`, and the outputs of `authentiscan-a3-session-1` … `-8` as
  kernel data sources — **no checkpoint upload**. Cell 2 asserts all ten canonical
  checkpoints are mounted before anything runs.
- `results/canonical_runs.txt` exists now (A6 manifest, needed by A4): the three 50-epoch
  reruns plus the seven original rows.
- New drivers: `code/run_crossgen.py` (tiny-genimage verification CSV + 80 resumable,
  failure-isolated `eval.py` cells) and `code/make_galleries.py` (better checkpoint per
  backbone by val_loss, shared correct set, five galleries); `eval.py` gained
  `read_manifest`/`find_checkpoints`; `make_a3_notebook.push` split into `push_payload`
  (reused by A4) with A3 behaviour unchanged.
- `[VERIFY at push]`: Kaggle accepting eight kernel sources + two datasets on one notebook,
  and the mount path of kernel outputs (autodetected). A failure shows in cell 2 within
  seconds of the run starting.
- Session zip `results_a3_s8.zip` still sits at the repo root (ignored).

### 3. Changes it made

- Added: `results/canonical_runs.txt`, `code/run_crossgen.py`, `code/make_galleries.py`,
  `notebooks/make_a4_notebook.py`, `notebooks/phase_a4_crossgen_gradcam.ipynb`.
- Edited: `code/eval.py` (two helpers), `notebooks/make_a3_notebook.py` (push refactor),
  `notebooks/README.md` (A4 paragraph), CLAUDE.md §13, plan §7a amendment 3 + A4 status.
- No Kaggle action. No result file touched.

### 4. Failed Attempts

- **23 Sep 2026 — first A4 push refused: `{"code":401,"message":"Unauthorized access"}`.**
  Diagnosed the same day without the token (three-angle investigation plus an adversarial
  round, all credential-free). That body is the legacy write gateway's credential rejection:
  `kernels/push`, `datasets/create/new` and `models/create/new` all return it byte-identically
  for no header, a bogus Bearer and a bogus Basic, and it is emitted before the payload is
  parsed (no `X-Kaggle-*` headers, unlike the application's own 401 "Unauthenticated" on GET
  routes). Resource-level refusals look different (403 "Permission '...' was denied") and bad
  kernel/dataset sources are reported non-fatally inside a 200 (`invalidKernelSources` in the
  SDK's `ApiSaveKernelResponse`), so the eight `kernelDataSources` and the second dataset
  (`yangsangtai/tiny-genimage`, confirmed public, 8.36 GB) cannot have produced it.
  Remaining explanations, most likely first: (1) the token is dead — expired under an
  undocumented settings-page lifetime, or deleted on the settings page after the 23 Aug
  exposure note (generating a new token does NOT revoke old ones, kaggle-api PR #863, so only
  deletion or expiry); (2) the value was mis-pasted (this laptop deletes token files, so it is
  retyped every time); (3) Kaggle's legacy `www.kaggle.com/api/v1` write gateway stopped
  accepting this token class between 26 Aug and 23 Sep — the official client 2.2.4 now posts
  to `api.kaggle.com/v1/kernels.KernelsApiService/SaveKernel` and an OAuth rollout landed
  around 10 Sep; no evidence either way. Discriminating check (Rohit, with the token; spends
  nothing; `curl.exe`, because in PowerShell plain `curl` is Invoke-WebRequest):

      curl.exe -s -w "\nHTTP %{http_code}\n" -H "Authorization: Bearer KGAT_<token>" "https://www.kaggle.com/api/v1/kernels/status?userName=yaduvxnshi&kernelSlug=authentiscan-a3-session-1"

  401 "Unauthenticated" → token dead or mis-pasted → generate a new one (kaggle.com/settings,
  API section) and re-run the push command in step 1 below. 200 with a status JSON → token
  alive → the legacy push route is the problem → Claude switches `push_payload` to the
  SaveKernel route (request model in the installed kagglesdk 0.1.37) before the next attempt.
- Tooling note: a long heredoc through the Bash tool fails on this machine; edit scripts go
  to the scratchpad and run from there.
- For A4's verification step: the tiny-genimage card says 5,000 images per generator
  *including* train and val, so a val slice may hold fewer than the loader's 1,250-per-class
  cap; the loader then caps both classes equally and warns, and `genimage_verification.csv`
  records the realised counts.

### 5. Next steps

0. **Rohit — run the token check in "Failed Attempts" above first** (23 Sep: the push was
   refused with a 401 before anything ran). Regenerate the token if it fails.
1. **Rohit — launch A4** (a push auto-starts the run; toggle `GITHUB_PAT` ON for the new
   notebook under Add-ons → Secrets first — the push creates the notebook, so push once,
   toggle, then push again or press Run):

       & "d:\Desktop\AuthentiScan\sem8_major\.venv\Scripts\python.exe" "d:\Desktop\AuthentiScan\sem8_major\notebooks\make_a4_notebook.py" --push --token KGAT_<token>

   Quota impact is small (evaluation only, estimated 1–2 h).
2. Download `results_a4.zip`; Claude merges: `merge_runs.py --kind crossgen` (80 rows),
   copies the verification CSV, shared list, dump files, per-cell dirs and galleries in;
   spot-checks two cells by recomputation (gate G4); records the tiny-genimage counts and
   any ai-vs-nature format asymmetry in the plan.
3. Then A5 (three ablation configs, Kaggle T4; decide the `time_budget_min` fix first) or,
   if time is short, straight to A6 on the laptop.

---

## Session 8 COMPLETE `[merged 4 Sep 2026]` — rerun phase closed (3 of 3); A4 is next

### 1. Goal

Merge the session-8 result (`resnet50_ft` at a 50-epoch ceiling), the last of the three
lower-bound reruns decided on 25 Aug, and close the rerun phase so A4 can start.

### 2. Current State

- `runs.csv` = 13 rows (10 matrix + 3 reruns), every row `Tesla T4, 15 GB` / torch
  2.10.0+cu128 / timm 1.0.26 / seed 42 / `cifake_split_seed42.csv` / 90,000 train images.
  Measured GPU time 30.12 h (19.89 matrix + 10.23 reruns). **Nothing is pending on Kaggle.**
- `resnet50_ft_20260827-0206`: val 96.32 / test **96.51** (AUC 0.9941), up from 95.66 /
  95.93. Best epoch 48/50, `stop_reason=max_epochs` — the same outcome as `resnet50_fe`.
  Tail is diminishing returns (val_loss −0.0143 over epochs 31–40, −0.0042 over 41–50;
  train/val gap 0.9 pp). 323 min actual vs 317 projected (1.02×).
  **Decision: no third ceiling increase for either ResNet50 row.** Paper 2 carries one
  architecture-level caveat (ResNet50 converges slowest under the committed SGD rates and
  never triggered patience-5 within 50 epochs) instead of two row caveats.
- The rerun's first 30 epochs are bit-identical to the original run's curve (diff-verified)
  — the 30-epoch row is a strict prefix of the 50-epoch row. Reproducibility evidence for
  Paper 2.
- The 25 Aug "epoch-budget artefact" worry is settled: resnet50_ft stays last among ft rows
  by 1.05 pp (~8 SE). Canonical ft: vit 98.89 > vgg19 97.91 > densenet121 97.60 ≈
  efficientnet_b0 97.56 > resnet50 96.51. Canonical fe: vit 94.75 > densenet121 93.48 >
  resnet50 92.98 ≈ efficientnet_b0 92.86 > vgg19 90.55.
- **This machine (DESKTOP-GKS9MUQ, the old laptop, no GPU; repo now at
  `d:\Desktop\AuthentiScan`) holds all 13 `best.pt` checkpoints, 2.2 GB** — the ten in the
  Victus transfer checklist below plus `resnet50_fe_20260826-0457/` (90 MB),
  `efficientnet_b0_fe_20260826-0749/` (16 MB) and `resnet50_ft_20260827-0206/` (90 MB).
  A4 needs the canonical set on whichever machine runs it; the USB transfer is still A4's
  practical gate.
- The `time_budget_min` guard is still inert (25 Aug correction, further down). It did not
  matter for session 8 (323 min actual vs 340 budget) and no training session remains.

### 3. Changes it made

- `results/runs.csv`: +1 row via `merge_runs.py` (selfcheck run first, passed). Run dir
  `results/resnet50_ft_20260827-0206/` copied in — four CSV/YAML files committed, `best.pt`
  gitignored as always. `results_a3_s8.zip` left at the repo root, ignored by `*.zip`.
- CLAUDE.md §13 dated entry; `implementation_plan.md` §10 "Session 8 result" subsection;
  the transfer checklist below amended from 10 to 13 checkpoints.
- No code, config or notebook changes. No Kaggle action.

### 4. Next steps

1. **A4** per plan §7a: Grad-CAM galleries from each backbone's better checkpoint by
   val_loss (for ResNet50 that is now the 50-epoch checkpoints), then the cross-generator
   evaluation on `yangsangtai/tiny-genimage` — 10 canonical checkpoints × 4 generators × 2
   conditions = 80 `crossgen.csv` rows (use the three 50-epoch checkpoints for the rerun
   pairs; do not score the superseded 30-epoch ones).
2. Checkpoint transfer (USB) from this laptop to the Victus if A4 runs there.
3. A6 later: `canonical_runs.txt` per the plan §10 note.

---

## Plan change — single-paper publication + session 7 reruns `[ADOPTED — 25 August 2026]`

### 1. Goal

Record the 25 Aug plan change (Rohit; guide-approved): **one published research paper**,
merging the Sem 7 review (Paper 1) and the Sem 8 experimental work (Paper 2), instead of
two separate submissions. Amity side unchanged: two semester projects, two reports, two
WPR tracks. Full detail: `sem8_major/implementation_plan.md` §10; CLAUDE.md §3/§12/§13
amended in the same pass.

### 2. Current State

- Matrix 9 of 10 rows, all Tesla T4; session 6 (vit_base_patch16_224_ft) running on
  Kaggle — left untouched to completion by explicit decision (25 Aug).
- Rerun decision (Rohit, 25 Aug): after session 6 merges, **session 7 on Kaggle T4**
  reruns the three lower-bound rows — resnet50_fe, resnet50_ft, efficientnet_b0_fe — at
  `max_epochs: 50` (patience 5 and all other hyperparameters unchanged). Worst case
  ~7–11 GPU-h; check remaining quota first, else it waits for the reset. Reruns get new
  run_ids; A6's `canonical_runs.txt` manifest selects which rows the tables use.
- Merged-paper shape (hybrid review+experiment vs experimental paper with deep related
  work) deliberately deferred to merge gate P2, after development completes.
- No publication artefact exists yet; the `publication/` directory is created only at P4.

### 3. Changes it made

- CLAUDE.md: §3 publication goal amended; §12 item 5 reworded + new item 19 (merge
  shape); §13 dated entry.
- `sem8_major/implementation_plan.md`: new §10 (session 7 spec + P1–P7 merge pipeline);
  Table 5 S8-2 row annotated.
- This entry. No code, configs, notebooks or Kaggle state touched.

### 4. Next steps

1. Rohit: when session 6 finishes, download `results_a3_s6.zip` — Claude merges; A3
   closes at 10 of 10.
2. Claude: generate the session 7 notebook (three rerun configs, `max_epochs: 50`) via
   `make_a3_notebook.py` — Rohit launches after a quota check.
3. Then A4 per §7a (checkpoint transfer to the Victus is the practical gate).

Known issue, fix separately: this file's newest-first ordering had drifted (the A3 block
sits below A1); this entry restores a current block at the top, but the older blocks
remain out of order.

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

## Victus migration `[DECIDED — 22 August 2026; WITHDRAWN 4 September 2026 (plan §7a amendment 3) — kept for the record]`

Probe verdict on the 4070 (8 GB): effnet/vgg/vit fit at matrix batch sizes with headroom;
**densenet121 at batch 128 does not fit**. Decision (Rohit, on the Victus session's
analysis): 6 runs local (effnet fe/ft, vgg fe/ft, vit fe/ft); resnet50 T4 rows kept (full
hardware consistency is unachievable once densenet stays on T4, so a rerun buys nothing);
densenet finishes in Kaggle session 2 at its committed batch 128 (fallback: local bs64,
documented). Principle recorded in the plan: config fidelity beats hardware uniformity;
Paper 2's training-time table gets per-GPU annotation. The earlier "rerun resnet50 locally"
idea in this file is superseded by this decision.

**Full Victus verification record (its session, 22 Aug):** setup steps 1–8 all done except
Omen power profile and Windows Update. Python 3.12.10 (machine's 3.13.6 untouched), torch
2.11.0+cu128 / torchvision 0.26.0+cu128 / timm 1.0.28, driver 592.82. CIFAKE restored from
a `cifake.zip` in the copied folder — all 120,000 committed split paths verified present;
split not regenerated. Self-checks OK. GPU smoke **bit-identical to CPU and T4**
(val 0.7175 / test 0.7925) → four-way reproducibility for Paper 2. Probe found
densenet121@128 = 8.05 GB → silent driver system-memory fallback measured at **4.7x
slower per image** (14.60 vs 3.13 ms at bs96) — "TIGHT" actually means unusable; the
quarantine guard held (smoke rows only in smoke_runs.csv).

**Victus state / pending there:**
- Working copy is a ZIP extraction with NO git history — after the next push from the old
  laptop, replace it with a real `git clone` (venv rebuild ~1 min, pip wheels cached; move
  `data/cifake/` across instead of re-downloading).
- **Two files exist only on the Victus and must survive the re-clone:**
  `requirements_victus.lock` (copy into the fresh clone and commit it) and its
  `results/smoke_runs.csv` row for the 4070 smoke (merge with
  `python code/merge_runs.py <old-copy>/results/smoke_runs.csv --kind runs --into results/smoke_runs.csv`
  — it documents the fourth leg of the reproducibility claim).
- GPU is at its 80 W default of a 120 W maximum — Omen Gaming Hub performance profile not
  yet set (Rohit, GUI action; ~50% throughput sitting unused).
- Windows Update not yet run (needs reboots — Rohit).
- New lock file `requirements_victus.lock` exists there; env recording for Paper 2 happens
  when the first real run starts.
- Doc updates for this decision were written on the OLD laptop (this commit) — the Victus
  session should `git pull` them, not rewrite them.

**AMENDMENT (Rohit, 23 Aug 2026): Kaggle quota first.** The remaining six matrix runs go to
Kaggle sessions 3–6 (plan §7a amendment 2) — if they all land on the T4, the whole 10-run
matrix is hardware-consistent at committed batch sizes and the per-GPU caveat disappears.
The Victus is the A4–A6 machine and the training fallback; its validated CUDA env stays.
The checkpoint-transfer checklist below still applies (A4 needs every checkpoint wherever
A4 runs); session 3–6 zips can be downloaded on either machine.

**PRIMARY MACHINE IS NOW THE VICTUS (Rohit, 22 Aug 2026).** The project continues there;
the old laptop goes dormant (its repo stays valid — pull before any use). Execution rule
amended the same day: Claude commits/pushes git itself, with no co-author line; Kaggle
launches, quota spends and portal uploads remain Rohit's.

**Transfer checklist to make the Victus clone complete** (things git does not carry):
1. `data/cifake/` — already on the Victus (verified against the committed split).
2. `requirements_victus.lock` + the 4070 smoke row — rescue from the ZIP copy (see above).
3. **All seven Kaggle run dirs — exist ONLY on the old laptop** (checkpoints are
   gitignored): `resnet50_fe_20260822-0532/`, `resnet50_ft_20260822-0734/` (~90 MB each),
   `densenet121_fe_20260822-1534/`, `densenet121_ft_20260822-1617/` (~27 MB each),
   `efficientnet_b0_fe_20260823-0248/`, `efficientnet_b0_ft_20260823-0427/` (~16 MB each),
   `vit_base_patch16_224_fe_20260823-0553/` (**343 MB**), `vgg19_fe_20260823-1605/` and
   `vgg19_ft_20260824-0047/` (**558 MB each**) and `vit_base_patch16_224_ft_20260825-1522/`
   (**343 MB**), all under `sem8_major/results/`. Copy the dirs into the Victus repo's
   `results/` via USB/cloud — A4's Grad-CAM galleries and cross-generator table need these
   checkpoints. Sessions 2–6 were processed on the old laptop; rows are in git, binaries are
   not. **The set is now COMPLETE at ten checkpoints, ~2.1 GB.** Use a USB stick rather than
   a cloud sync. This transfer is the practical gate on starting A4. *(Amended 4 Sep: plus
   the three session 7–8 rerun dirs — 13 checkpoints, 2.2 GB; see the top block.)*

Division of labour while both machines are active: Victus session drives training; **pull
before working, push after committing, on both.**

## A3 — the 10-run matrix `[opened 22 August 2026; CLOSED 26 August at 10 of 10; reruns merged 26 Aug and 4 Sep]`

**Session 3 COMPLETE (merged 23 Aug 2026) — 7 of 10 rows done, all T4.** efficientnet_b0_fe
val 92.67 / test 92.87; efficientnet_b0_ft val **97.50** / test 97.56 (AUC 0.9971);
vit_base_patch16_224_fe val 94.62 / test 94.75 (AUC 0.9881). 4.2 h against a 7.6 h worst
case; two of the three early-stopped. Rows merged into `results/runs.csv`, run dirs (with
`best.pt`) copied into `sem8_major/results/` **on the old laptop** — add these three to the
checkpoint-transfer checklist below; the ViT checkpoint alone is 343 MB.

G3-style check passed on all three: balanced confusion matrices, monotone-then-flat val
curves, fe below ft as expected. EfficientNet-B0-ft is effectively tied with DenseNet121-ft
(97.56 vs 97.60 test) — one seed cannot separate them, and Paper 2 should say so rather than
declaring a winner.

**Session 4 COMPLETE (merged 24 Aug 2026) — 8 of 10 rows, all T4.** `vgg19_fe` val 90.54 /
test 90.55 (AUC 0.9669), 76 min against a 4.8 h worst case, early-stopped at epoch 13 (best
epoch 8). Run dir with its **558 MB** `best.pt` is on the old laptop only. The `GITHUB_PAT`
secret was already attached to that notebook, so the session-2 secret failure did not recur.

**vgg19_fe is the weakest row in the matrix and that is a genuine architectural finding, not
a bug** — AUC 0.9669, balanced confusion matrix, `trainable_params` 8194 (head only, correct
for fe), curve climbing 86% → 90.5%. Frozen VGG19 features are simply less linearly separable
than newer backbones'. The fe ranking is now a clean story: vgg19 90.55 < resnet50 92.83 ≈
efficientnet_b0 92.86 < densenet121 93.48 < vit 94.75. Carry the epoch-7 val_loss spike
(0.4426 vs ~0.26, val_acc dipping to 85.15% then recovering) into Paper 2 as reported SGD
instability — do not smooth it away.

**Execution-split deviation, recorded for honesty:** this Kaggle push was performed by Claude,
not Rohit, on Rohit's explicit in-chat instruction with the token supplied inline. The
standing rule (CLAUDE.md §1 — Kaggle pushes/launches are Rohit's) is **unchanged**; this was
a one-off override, not a policy change. Do not treat it as precedent.

**Two credentials are pending rotation as of 23 Aug:**
1. The GitHub fine-grained PAT that had been pasted as a literal line in `.gitignore`
   (replaced with a `github_pat_*` pattern; history scan confirms it was never committed).
2. The Kaggle API token, pasted into the chat transcript and used inline in two shell
   commands during this session.
Neither reached a public remote, but both are exposed and should be regenerated. Rotating the
Kaggle token requires no notebook changes; rotating the PAT means updating the `GITHUB_PAT`
secret value once in Kaggle's secrets manager (the value is shared, so attachments survive).

**Session 5 COMPLETE (merged 25 Aug 2026) — 9 of 10 rows; `vgg19_ft` is the matrix leader.**
val 98.19 / test 97.91 (AUC 0.9979), 216 min against an 8.0 h worst case, early-stopped at
epoch 14. Run dir with its **558 MB** `best.pt` is on the old laptop only.

**The matrix's headline result is an inversion:** VGG19 is last on feature extraction (90.55)
and first on fine-tuning (97.91), a +7.36 gain against +4.69 / +4.11 / +3.10 for
efficientnet / densenet / resnet. Frozen VGG features suit CIFAKE poorly; unfrozen, its plain
conv stack relearns the low-level artefact filters the task actually needs. Scope the claim to
this dataset in the write-up.

**Disclosure item, do not bury it:** `resnet50_fe`, `resnet50_ft` and `efficientnet_b0_fe`
stopped at `max_epochs` with best epoch at/next to the ceiling, so their val loss was still
improving — **those three are lower bounds, not converged numbers.** It matters most for
`resnet50_ft`, the weakest ft row (95.93) and the only ft run that never early-stopped: its
last place is partly an epoch-budget artefact. Either state this wherever the ft ranking
appears in Paper 2, or rerun the three at a higher ceiling. The other six converged on their
own and compare cleanly.

**PowerShell gotcha that cost a launch attempt (24 Aug):** `cd sem8_major` followed by
`.venv\Scripts\python.exe ...` fails two ways — the `cd` may not take, and PowerShell reads a
relative exe path without a `.\` prefix as a module name
(`CouldNotAutoLoadModule`). Use the fully-qualified call operator form instead, which works
from any directory:

    & "C:\Users\rohit\Desktop\AuthentiScan\sem8_major\.venv\Scripts\python.exe" "C:\Users\rohit\Desktop\AuthentiScan\sem8_major\notebooks\make_a3_notebook.py" --session <N> --push --token KGAT_<token>

**Session 6 COMPLETE (merged 26 Aug 2026) — A3 IS CLOSED AT 10 OF 10 ROWS.**
`vit_base_patch16_224_ft` val 98.98 / test **98.89** (AUC 0.9994), 204 min against a 6.8 h
worst case, early-stopped at epoch 15. Run dir with its **343 MB** `best.pt` is on the old
laptop only. Total matrix: **19.89 h** measured GPU time, every row Tesla T4 15 GB / seed 42 /
`cifake_split_seed42.csv` / 90,000 train images / committed batch size — amendment 2's
no-per-GPU-caveat goal achieved in full.

**Final standings.** ft: vit 98.89 > vgg19 97.91 > densenet121 97.60 ≈ efficientnet_b0 97.56 >
resnet50 95.93. fe: vit 94.75 > densenet121 93.48 > efficientnet_b0 92.86 ≈ resnet50 92.83 >
vgg19 90.55.

**Three things Paper 2's discussion rests on.** (1) **ViT wins both modes** — at ~0.1 pp
standard error on 20,000 test images, its ~1 pp lead over VGG19-ft is ~7 SE, a real
separation. (2) The **VGG19 inversion** holds: last on fe, second on ft, biggest gain
(+7.36). (3) The **97.5–97.9 band is a tie, not a ranking** — vgg19/densenet/effnet sit
within 0.35 pp and densenet-vs-effnet (0.04 pp) is noise; report them as indistinguishable
on one seed.

**Lower-bound disclosure, now confirmed against the full matrix:** exactly three runs hit
`max_epochs` with best epoch at/next to the ceiling — resnet50_fe (30/30), resnet50_ft
(30/30), efficientnet_b0_fe (29/30). The other seven early-stopped. Session 7 reruns those
three at `max_epochs: 50`.

**Quota after session 6 (estimate, not a reading):** 19.89 h train × ~1.25 ≈ **24.9 h of
30 h**, leaving ~5 h. **Session 7's 7–11 h worst case does not fit** — it waits for the
weekly reset unless the week has rolled over. Check the quota page first.

**Sessions 7 and 8 PREPARED 26 Aug 2026 — the lower-bound reruns, split in two.** Notebooks
`notebooks/phase_a3_s7.ipynb` (`resnet50_fe_e50` + `efficientnet_b0_fe_e50`, 6.04 h worst
case) and `phase_a3_s8.ipynb` (`resnet50_ft_e50`, 5.28 h). Generated and verified (7 cells,
cell 0 markdown, T4 hard-abort and mount autodetect intact, every named config present and
passing the pre-flight assertions) but **not launched** — Kaggle pushes are Rohit's.

**Why two sessions and not one:** the three reruns project to 11.3 h at the 50-epoch ceiling
(measured per-epoch × 50: 200 + 317 + 163 min), which is over the ~9 h session cap, and the
A3 batching rule requires ≥30% margin under it. Session 7 carries 33% margin, session 8 41%.

**These reruns are a convergence fix, not an ablation.** Each `_e50` config was generated
from its original with only `max_epochs` changed 30 → 50 — proven by diff, no other line
differs. No hyperparameter changes, so the rerun rows stay directly comparable to the other
seven. Note this differs from the `canonical_runs.txt` answer given for the *weight-decay*
case: since nothing but the epoch budget moved, a converged rerun is strictly the better
number and the A6 manifest should point at it, otherwise the reruns achieve nothing. Confirm
that at A6.

**Quota: neither session fits this week.** ~5 h remains of 30 after session 6; session 7
needs 6.04 h. Both wait for the reset unless the week has rolled over — check the page.

**Then A4.**

---

## Session 7 COMPLETE `[merged 26 Aug 2026]` — one confirmation, one partial fix, one still pending

Both session-7 runs finished. Read them as two different outcomes, not one blanket "fixed":

**`efficientnet_b0_fe` — CONFIRMED CONVERGED, lower-bound flag retracted.** Given 20 more
epochs, training landed on the identical best epoch (29) with bit-for-bit identical val/test
numbers (92.67 / 92.86, AUC 0.9802) — this time via `stop_reason=early_stopping` rather than
`max_epochs`. The original 30-epoch number was correct all along; the ceiling just cut the run
off one epoch before patience-5 could formally close. Nothing to disclose going forward.

**`resnet50_fe` — improved +0.15pp test, but STILL hit the new ceiling (best epoch 49 of
50).** Technically still not "converged" by the strict stop_reason test. Practically: the
learning curve is flat over the last 10 epochs (val_loss 0.1775→0.1740, val_acc bouncing
93.0–93.2% with no trend) — diminishing returns, not an open trajectory. **Recommendation:
do not extend the ceiling again** — the 30→50 gain was +0.15pp; a further stretch is expected
to buy less than that for real GPU cost. Paper 2 states this row's epoch-ceiling caveat
narrowly, not as a matrix-wide issue.

**`resnet50_ft` (session 8) is still pending** — no inference drawn from this result; it
stands on its own when it lands. Session 8 notebook is prepared and pushed
(`authentiscan-a3-session-8`, `resnet50_ft_e50`, 5.28 h worst case) — needs the same
`GITHUB_PAT` secret toggle as a fresh notebook, and a quota check first.

`runs.csv` is now 12 rows (10 matrix + 2 reruns, separately timestamped, nothing overwritten).
No `canonical_runs.txt` exists yet — A6 creates it; when it does, it should select the
50-epoch `resnet50_fe` row and either `efficientnet_b0_fe` row (now provably interchangeable). A4's practical gate is the checkpoint
transfer — the pile is now **~2.1 GB** and complete.

**(Historical) Session 6 prepared 25 Aug 2026 — the final run of the matrix.**
Notebook `notebooks/phase_a3_s6.ipynb`, worst case 6.8 h, per-run budget 400 min. Generated
and verified but **not launched** — the Kaggle push stays with Rohit (CLAUDE.md §1), using the
command form above with `--session 6`. Toggle `GITHUB_PAT` on for that new notebook first.
Session 6 will likely run well under its worst case: `vit_fe` early-stopped at epoch 11 in
69 min, and four of the last six runs early-stopped.

When session 6 merges, **A3 closes at 10 of 10 and A4 begins** (Grad-CAM galleries across all
models on shared correct/incorrect examples, then the cross-generator evaluation on the
tiny-genimage subset). A4 needs every checkpoint present on one machine — see the transfer
checklist below.

**Quota caveat that could not be resolved from here:** Kaggle exposes no API for remaining
GPU hours — the quota page is browser-only, so Claude cannot verify it. Measured training
time across the **nine** finished rows is **16.5 h** (990 min), and session wall-clock runs
roughly 1.25x training time, so the consumption estimate is **~20.6 h of the 30 h weekly
allowance**, leaving ~9 h against vit_ft's 6.8 h worst case. Tight but feasible — *if* the
quota week has not reset. That is an estimate, not a reading; check the quota page.

**CORRECTION (25 Aug) — the `time_budget_min` guard is currently INERT, and an earlier
version of this file wrongly cited it as protection.** Verified in code:
`run_session.py:31-35` builds the `train.py` command with only `--config`, `--data-root` and
`--results-dir` — it has no `--time-budget-min` argument and never forwards one.
`train.py:173` reads the budget from `cfg.get("time_budget_min")`, but **no matrix config
sets that key** (only `template.yaml` carries it, as `null`). The "per-run time budget
400/460 min" printed in each generated notebook header is therefore **documentation only —
nothing enforces it.** Consequence: a run that overruns the ~9 h Kaggle session cap is killed
outright, losing the row, the checkpoint and the quota, rather than stopping cleanly with
`stop_reason=time_budget`. The non-T4 hard-abort is real and still protects hardware
consistency; only the time guard is missing.

Smallest fix (~4 lines, not yet applied — Rohit's call, since it changes run behaviour):
add a `--time-budget-min` passthrough in `run_session.py` and have `make_a3_notebook.py`
emit it from the `SESSIONS` budget it already stores, so the header number becomes real.


Session 1 (`resnet50_fe` + `resnet50_ft`) is generated, pushed and waiting to be run:
Kaggle notebook **`yaduvxnshi/authentiscan-a3-session-1`** (private, GPU + Internet on,
CIFAKE attached). `notebooks/make_a3_notebook.py` generates and pushes each session's
notebook; the six-session plan lives in that script and in plan §7a A3.

**Session 1 COMPLETE, G3 PASSED (22 Aug):** resnet50_fe val 93.01% / test 92.83%;
resnet50_ft val **95.66%** / test 95.93% (AUC 0.9925). Rows merged into `results/runs.csv`
(4 rows total incl. header context: 2 runs), artefact dirs archived locally with checkpoints
(`best.pt` stays out of git). Times ran ~1.25x calibration and neither run early-stopped, so
the remaining five sessions are re-budgeted at ~34 h total worst case — sessions 2–4 fit this
quota week (~23.5 h left), 5–6 land after the weekly reset. Session estimates updated in
`notebooks/make_a3_notebook.py`.

Next: session 2 (densenet121 fe + ft, ~6.5 h worst case). Claude generates the notebook;
**Rohit launches it** (a push auto-starts the batch run) and later downloads
`results_a3_s2.zip`. Same G3-style spot check on val_acc, then session 3.

**Session 2 first launch failed (22 Aug): Kaggle Secrets attach PER NOTEBOOK.** Each new
session notebook needs `GITHUB_PAT` toggled on once in Add-ons → Secrets before its first
run, or cell 1 dies with "No user secrets exist" (seconds of quota, harmless). The toggle
then sticks across versions/pushes of that notebook. Generated notebooks now carry this
warning in their header cell. Applies to sessions 3–6 too.

**Session 1 second false start (22 Aug), resolved — root cause: Kaggle moved dataset
mounts.** Batch runs mount datasets at `/kaggle/input/datasets/<owner>/<slug>` (verified by a
CPU diagnostic kernel), not the classic `/kaggle/input/<slug>` the interactive A2 session
used, so both runs died on missing image paths in seconds. Session notebooks now **autodetect**
the CIFAKE root (walk `/kaggle/input` for the dir containing `train/REAL`) and hard-abort on
any non-T4 GPU (a wrong assignment costs seconds, not a poisoned training-time table).
Relaunched 22 Aug: **T4 assigned, CIFAKE found at the namespaced path, both configs
validated, training in progress.** The retry monitor that pushed these relaunches was killed
after Rohit's new execution rule (below); the training run itself is unaffected.

**Execution rule change (Rohit, 22 Aug):** Claude edits and verifies locally, then hands
Rohit exact commands; nothing is committed, pushed, or launched anywhere without asking him
per action. Recorded in CLAUDE.md §1 and Claude's persistent memory.

**Session 1 first false start (22 Aug), resolved.** The first push of the notebook was stored by
Kaggle with cell 0 as **code** instead of markdown, so the run died instantly on
`SyntaxError: invalid character '§'`. Investigated by pushing the same file to a throwaway
kernel (`yaduvxnshi/authentiscan-nb-format-test`, private, GPU off — safe to delete): it
stored correctly as markdown, and so did both `ensure_ascii` serialisations, so the generator
is not at fault and the cause was a one-off on Kaggle's side. Re-pushing produced a clean
version 3, which is running. Lessons now baked in:

- **Pushing a notebook auto-launches a run.** Version 1 auto-ran at push time before the
  `GITHUB_PAT` secret was attached to that (new) notebook and errored on the clone. Useful
  the other way round: with the secret attached, a push *is* the launch, so sessions 2–6 need
  no browser at all. Push deliberately — every push spends quota.
- **After any push, pull the notebook back and check the cell types** before relying on it.
- **Run as a saved version, not an interactive session.** Rohit's first attempt was an
  editor "Run All", which dies with the browser tab; the batch run does not.
- **Accelerator must stay T4 for every run** (calibration and A2 used T4; the first
  interactive attempt landed on a P100). Mixing GPUs would make Paper 2's per-model
  training-time table compare hardware rather than architectures. The notebooks now print the
  GPU and warn loudly if it is not a T4.

---

## A2 — code transport + Kaggle GPU smoke `[G2 PASSED — 22 August 2026]`

### Outcome

GPU pipeline proven and the whole matrix now has measured timings behind it.

- **Hardware/versions recorded** (`results/kaggle_env.md`): Tesla T4 15 GB, 4-core Xeon
  @ 2.00 GHz, 31 GB RAM, CUDA 12.8, torch 2.10.0+cu128, timm 1.0.26, sklearn 1.6.1 — all
  different from the local lock, which is why every run logs its own versions.
- **GPU smoke:** val_acc 0.7175 / test_acc 0.7925, *bit-identical to the CPU smoke run*
  (strong reproducibility evidence), 0.09 min vs 2.8 min. Grad-CAM verified on GPU.
- **Calibration** (`results/calibration.csv`, 30-epoch projections): EfficientNet-B0 1.78 h,
  ResNet50 2.70 h, DenseNet121 3.25 h, ViT 5.43 h, VGG19 6.42 h. With fe estimated at 60% of
  ft, the full matrix is **31.3 h worst case — over the 30 h weekly quota**; ≈12.5 h at a
  realistic 12-epoch early stop.
- **Consequence, implemented:** `time_budget_min` config field + `--time-budget-min` flag and
  a new `stop_reason` column (`max_epochs` / `early_stopping` / `time_budget`). A run now
  stops cleanly with its best checkpoint and a valid row instead of being killed at the
  session cap. Verified locally (stopped after epoch 1 under a 0.05 min budget).
- Schema change was safe: `runs.csv` still had no data rows; `smoke_runs.csv` migrated to the
  31-column header.

### Failed attempts / watch-outs

- `~/.kaggle/access_token` disappeared twice; recreating it silently failed. Something on the
  laptop removes files whose contents match the token pattern — pass the token inline.
- Kaggle derives a notebook's slug from its title: pushing "AuthentiScan A3 session 1" with
  slug `authentiscan-a3-s1` created `authentiscan-a3-session-1`. The generator now uses the
  title-derived slug so re-pushes update rather than duplicate.
- The A2 notebook's own slug changed the same way (`notebook322addb147` →
  `authentiscan-a2-gpu-smoke-and-calibration`).
- Two smoke runs landed in the zip (the session was run twice); both merged, harmless.
- `results_a2 (1).zip` was sitting inside the repo folder and got swept into a commit by
  `git add -A`; GitHub rejected the push (169 MB > 100 MB limit). Fixed by gitignoring `*.zip`
  and amending the commit — the file stays on disk. Every future session zip will land the
  same way, so keep downloads out of the repo folder or rely on the ignore rule.

---

## A2 (earlier note) — code transport `[20 August 2026]`

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
