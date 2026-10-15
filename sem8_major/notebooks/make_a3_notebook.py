"""Generate (and optionally push) one Kaggle notebook per training session: A3 matrix
sessions 1-8 and, with the same pipeline and round-trip, the A5 ablation sessions 9-10.

    python notebooks/make_a3_notebook.py --session 1
    python notebooks/make_a3_notebook.py --session 1 --push --token KGAT_xxx

Since A5 (15 Oct 2026) cell 4 passes the session's per-run time budget to run_session.py, so
train.py stops a run cleanly at the budget instead of dying at the Kaggle cap. The committed
phase_a3_s1..s8.ipynb files ran before that flag existed and are the record of those runs -
do not regenerate them.

One notebook per session, each with its own Kaggle slug (`authentiscan-<a3|a5>-session-<N>`), so A4 can
attach several finished sessions' outputs as data sources — attaching multiple *versions* of
one notebook is the uncertain path (plan §7a A2.4 [VERIFY]); attaching several *notebooks* is
ordinary. Sessions are sized from the measured calibration in `results/calibration.csv`
(fe times estimated at 60% of ft — fe skips the backbone backward pass).

Hours are worst case, i.e. every run goes to its max_epochs (30 for sessions 1-6, 50 for
7-10). Early stopping (patience 5) normally ends runs earlier. From session 9 the per-run
budget is enforced, so a session's worst case is bounded by its budgets plus overheads.
"""

import argparse
import json
from pathlib import Path

# (configs, worst-case hours, per-run time budget in minutes - enforced from session 9,
#  advisory for sessions 1-8, which ran before run_session.py forwarded it)
# Hours = calibration x 1.25: session 1 measured ~20% over the batch-timing estimates
# (per-epoch validation adds cost), and neither run early-stopped, so worst case is the
# planning number. Sessions stay >=30% under the 12 h Save & Run All cap (Kaggle docs, 14 Oct 2026).
SESSIONS = {
    1: (["resnet50_fe", "resnet50_ft"], 5.2, 330),   # DONE 22 Aug: 120 + 190 min, G3 passed
    2: (["densenet121_fe", "densenet121_ft"], 6.5, 330),
    3: (["efficientnet_b0_fe", "efficientnet_b0_ft", "vit_base_patch16_224_fe"], 7.6, 340),
    4: (["vgg19_fe"], 4.8, 330),
    5: (["vgg19_ft"], 8.0, 460),           # heaviest run; alone by rule, tight vs the cap
    6: (["vit_base_patch16_224_ft"], 6.8, 400),  # alone by rule
    # Sessions 7-8: the lower-bound reruns (plan 10). resnet50_fe, resnet50_ft and
    # efficientnet_b0_fe stopped at the 30-epoch ceiling with val loss still improving, so
    # they are rerun at max_epochs 50 - only the epoch BUDGET changes, no hyperparameter -
    # keeping them comparable to the rest of the matrix. Projections from measured
    # per-epoch times x 50: resnet50_fe 200 min, resnet50_ft 317 min, effnet_fe 163 min.
    # All three in one session would be 11.3 h, over the ~9 h cap, so the A3 batching rule
    # (>=30% margin under the cap) forces the split below.
    7: (["resnet50_fe_e50", "efficientnet_b0_fe_e50"], 6.1, 220),  # 363 min, 33% margin
    8: (["resnet50_ft_e50"], 5.3, 340),                            # 317 min, 41% margin
    # A5 ablations (plan 4, 7a A5): the canonical resnet50_ft_e50 recipe with ONE factor
    # changed per config - augmentation off (224 px), input 64 px, input 128 px; 50-epoch
    # ceiling like the baseline. Hours are the budget-bounded worst case (budgets + ~15 min
    # overhead), because the time budget is enforced from session 9 on. Session 9 repeats
    # session 8's cost (323 min measured for 50 epochs at 224 px; 317 projected): 420 min
    # tolerates a +27% slower epoch before the guard acts, so a full 50-epoch run is not
    # truncated by a tight budget. No calibration exists below 224 px (the 64/128 px runs
    # are loader-bound rather than GPU-bound), so session 10 gives each a generous 230 min.
    # Margins under the 12 h cap: 9 -> 40%, 10 -> 34%.
    9: (["resnet50_ft_noaug"], 7.2, 420),
    10: (["resnet50_ft_res64", "resnet50_ft_res128"], 7.9, 230),
}
PHASE = {9: "A5", 10: "A5"}   # every other session is A3


def phase_of(session):
    return PHASE.get(session, "A3")
def build(session):
    configs, hours, budget = SESSIONS[session]
    phase = phase_of(session)
    cfg_args = " ".join(f"configs/{c}.yaml" for c in configs)
    md = [
        f"# AuthentiScan — {phase} session {session}\n",
        "\n",
        "**First run of this notebook?** Kaggle Secrets attach per notebook: open Add-ons →\n",
        "Secrets and toggle `GITHUB_PAT` ON for this notebook first, or cell 1 fails with\n",
        "'No user secrets exist'. One-time per session notebook.\n",
        "\n",
        f"Runs: **{', '.join(configs)}** | worst case ~{hours:.1f} h | "
        f"per-run time budget {budget} min (enforced: a run stops cleanly at the budget with\n",
        "its best checkpoint and a valid row, stop_reason=time_budget)\n",
        "\n",
        "Library versions: timm is pinned to 1.0.26, the version every logged row used; torch\n",
        "comes from the Kaggle image (2.10.0+cu128 for every logged row) and cannot be pinned -\n",
        "if the new row's torch_version differs at merge, disclose it beside the baseline.\n",
        "\n",
        f"Plan: `sem8_major/implementation_plan.md` §7a {phase}. Each config runs as its own\n",
        "subprocess and a failure does not stop the session. Before running, check the\n",
        "quota page shows enough GPU hours left for the worst case above.\n",
        "\n",
        f"**After it finishes:** download `results_{phase.lower()}_s{session}.zip` from the Output tab and send\n",
        "it back — rows are merged into the repo with `code/merge_runs.py`, never retyped.\n",
    ]
    cells = [{"cell_type": "markdown", "metadata": {}, "source": md}]

    def code(src):
        cells.append({"cell_type": "code", "execution_count": None, "metadata": {},
                      "outputs": [], "source": src})

    code([
        "# 1. Code: clone the private repo (Kaggle Secret GITHUB_PAT) or pull if already there\n",
        "import os, subprocess\n",
        "from kaggle_secrets import UserSecretsClient\n",
        "\n",
        "PAT = UserSecretsClient().get_secret(\"GITHUB_PAT\")\n",
        "REPO_DIR = \"/kaggle/working/sm7\"\n",
        "if not os.path.exists(REPO_DIR):\n",
        "    subprocess.run([\"git\", \"clone\",\n",
        "                    f\"https://{PAT}@github.com/rohityaduvxnshi/sm7.git\", REPO_DIR],\n",
        "                   check=True)\n",
        "else:\n",
        "    subprocess.run([\"git\", \"-C\", REPO_DIR, \"pull\"], check=True)\n",
        "os.chdir(f\"{REPO_DIR}/sem8_major\")\n",
        "print(subprocess.run([\"git\", \"log\", \"--oneline\", \"-1\"],\n",
        "                     capture_output=True, text=True).stdout)\n",
    ])
    code([
        "# 2. Extras only - never upgrade Kaggle's torch/torchvision (CUDA build is matched).\n",
        "# timm is pinned to the version every logged row used, so a row differs from the\n",
        "# baseline only in the factor its config changes (grad-cam is not used by training).\n",
        "!pip install -q timm==1.0.26 grad-cam\n",
        "import timm, torch\n",
        "print(\"torch\", torch.__version__, \"timm\", timm.__version__)\n",
        "assert timm.__version__ == \"1.0.26\", timm.__version__\n",
        "\n",
        "# Accelerator consistency: every matrix run must use the SAME GPU, or Paper 2's\n",
        "# training-time comparison across architectures compares hardware, not models.\n",
        "# Calibration and A2 ran on T4. HARD abort on anything else: an aborted assignment\n",
        "# costs seconds; a P100 run would poison the training-time table. Relaunch (or\n",
        "# re-push) until Kaggle assigns a T4, or pin it in Settings -> Accelerator.\n",
        "gpu = torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"NO GPU\"\n",
        "print(\"GPU:\", gpu)\n",
        "assert \"T4\" in gpu, f\"wrong accelerator: {gpu} - matrix runs are T4-only (plan 7a A3)\"\n",
        "\n",
        "# Dataset root autodetect: Kaggle moved dataset mounts (classic /kaggle/input/<slug>\n",
        "# vs the namespaced /kaggle/input/datasets/<owner>/<slug> seen 22 Aug 2026 in batch\n",
        "# runs), so never hardcode the path - find the dir that holds train/REAL.\n",
        "import os\n",
        "DATA = None\n",
        "for root, dirs, _ in os.walk(\"/kaggle/input\"):\n",
        "    if \"train\" in dirs and os.path.isdir(os.path.join(root, \"train\", \"REAL\")):\n",
        "        DATA = root\n",
        "        break\n",
        "    if root.count(os.sep) > 5:   # don't descend into the dataset's image folders\n",
        "        dirs.clear()\n",
        "assert DATA, \"CIFAKE not found anywhere under /kaggle/input - is the dataset attached?\"\n",
        "print(\"CIFAKE mounted at:\", DATA)\n",
    ])
    code([
        "# 3. Pre-flight: matrix configs must be in matrix state, or a subset run could\n",
        "# silently produce a wrong row in the Paper 2 results table (plan 7a A3).\n",
        "import yaml, pathlib\n",
        f"CONFIGS = {configs!r}\n",
        "for name in CONFIGS:\n",
        "    p = pathlib.Path(f\"configs/{name}.yaml\")\n",
        "    c = yaml.safe_load(p.read_text(encoding=\"utf-8\"))\n",
        "    assert c.get(\"smoke_subset\") is None, f\"{p} has smoke_subset set\"\n",
        "    assert c[\"output\"][\"runs_csv\"].endswith(\"runs.csv\"), p\n",
        "    print(f\"OK {name}: {c['model']} {c['mode']} {c['optimizer']} lr={c['lr']} \"\n",
        "          f\"bs={c['batch_size']} max_epochs={c['max_epochs']} res={c['resolution']} \"\n",
        "          f\"augment={c.get('augment')} tag={c.get('tag')}\")\n",
    ] + (["    assert c.get(\"tag\"), f\"{p}: an ablation config needs a tag (plan 4)\"\n"]
         if phase == "A5" else []))
    code([
        "# 4. The session. One subprocess per config; a failure does not stop the rest.\n",
        "# {DATA} is the autodetected mount from cell 2 (IPython interpolates python vars).\n",
        f"!python code/run_session.py {cfg_args} \\\n",
        f"    --data-root \"{{DATA}}\" --results-dir /kaggle/working/results --time-budget-min {budget}\n",
    ])
    code([
        "# 5. What this session produced\n",
        "import pandas as pd\n",
        "df = pd.read_csv(\"/kaggle/working/results/runs.csv\")\n",
        "cols = [\"run_id\", \"model\", \"mode\", \"best_epoch\", \"stop_reason\", \"train_time_min\",\n",
        "        \"val_acc\", \"test_acc\", \"test_auc\"]\n",
        "display(df[cols])\n",
        f"print(\"\\nSanity (gate {'G5' if phase == 'A5' else 'G3'}): fine-tuned CNN val_acc should be mid-90s; anything near\")\n",
        "print(\"0.50 means a pipeline bug - stop and debug rather than spending more quota.\")\n",
    ])
    code([
        "# 6. Package for download: results (incl. checkpoints) + nothing else\n",
        f"!cd /kaggle/working && zip -qr results_{phase.lower()}_s{session}.zip results && "
        f"ls -lh results_{phase.lower()}_s{session}.zip\n",
    ])
    return {"cells": cells,
            "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python",
                                        "name": "python3"},
                         "language_info": {"name": "python", "version": "3.12"}},
            "nbformat": 4, "nbformat_minor": 4}


def push(session, nb_text, token):
    phase = phase_of(session)
    push_payload({
        # slug must match what Kaggle derives from the title, or a re-push creates a second
        # kernel instead of updating this one
        "slug": f"yaduvxnshi/authentiscan-{phase.lower()}-session-{session}",
        "newTitle": f"AuthentiScan {phase} session {session}",
        "text": nb_text, "language": "python", "kernelType": "notebook",
        "isPrivate": True, "enableGpu": True, "enableInternet": True,
        "datasetDataSources": ["birdy654/cifake-real-and-ai-generated-synthetic-images"],
        "competitionDataSources": [], "kernelDataSources": [], "categoryIds": [],
    }, token)


def push_payload(payload, token):
    """POST a kernel push request (also used by make_a4_notebook.py)."""
    import subprocess, tempfile, os
    fd, p = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    Path(p).write_text(json.dumps(payload), encoding="utf-8")
    try:
        r = subprocess.run(["curl", "-s", "-X", "POST",
                            "https://www.kaggle.com/api/v1/kernels/push",
                            "-H", f"Authorization: Bearer {token}",
                            "-H", "Content-Type: application/json",
                            "--data-binary", "@" + p], capture_output=True, text=True)
        print(r.stdout[:600] or r.stderr[:300])
    finally:
        os.remove(p)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", type=int, required=True, choices=sorted(SESSIONS))
    ap.add_argument("--push", action="store_true")
    ap.add_argument("--token", help="Kaggle API token (not stored on disk)")
    ap.add_argument("--force", action="store_true",
                    help="overwrite a frozen session notebook (1-8: the record of completed runs)")
    a = ap.parse_args()
    if a.session <= 8 and not a.force:
        raise SystemExit("sessions 1-8 already ran; their committed notebooks are the record "
                         "(regenerating them would add --time-budget-min). Pass --force to overwrite.")

    nb = build(a.session)
    out = Path(__file__).parent / f"phase_{phase_of(a.session).lower()}_s{a.session}.ipynb"
    text = json.dumps(nb, indent=1)
    out.write_text(text, encoding="utf-8")
    configs, hours, budget = SESSIONS[a.session]
    print(f"wrote {out}  ({len(nb['cells'])} cells) — {', '.join(configs)}, "
          f"worst case {hours:.1f} h, budget {budget} min")
    if a.push:
        if not a.token:
            raise SystemExit("--push needs --token")
        push(a.session, text, a.token)
