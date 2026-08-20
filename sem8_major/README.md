# sem8_major — implementation track (Paper 2)

Code, configs and results for the Semester 8 experimental work: transfer-learning detectors for
real vs AI-generated images, trained on CIFAKE and tested cross-generator on a GenImage subset.
Started early on the guide's 15 Aug 2026 instruction (CLAUDE.md §3 amendment).

Phase plan, schedule and training defaults: **`implementation_plan.md`** — read it before running anything.

```
code/       data.py, models.py, train.py, eval.py, gradcam.py (stubs until Phase 0/1)
configs/    one YAML per experiment, <model>_<mode>.yaml; template.yaml documents every field
data/       dataset root — gitignored; on Kaggle the datasets attach natively instead
results/    runs.csv (one row per run) + results/<run_id>/ per-run artefacts
figures/    plots generated from the result CSVs, never drawn by hand
notebooks/  Kaggle notebooks, one per phase
```

**Paper 1 firewall:** no number produced in this directory enters the Semester 7 review paper.
Paper 1 reports no experimental results and is already at the plagiarism check. Everything here
belongs to Paper 2 and the Semester 8 major report.

**Run workflow:**
1. Edit or copy a config in `configs/` — no hyperparameter is ever hardcoded in a script.
2. Run it on Kaggle: `python code/train.py --config configs/<name>.yaml`.
3. Download `results/runs.csv` and `results/<run_id>/` back into the repo; Paper 2 tables build from those files.
