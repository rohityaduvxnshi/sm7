"""Generate (and optionally push) one Kaggle notebook per A3 matrix session.

    python notebooks/make_a3_notebook.py --session 1
    python notebooks/make_a3_notebook.py --session 1 --push --token KGAT_xxx

One notebook per session, each with its own Kaggle slug (`authentiscan-a3-s<N>`), so A4 can
attach several finished sessions' outputs as data sources — attaching multiple *versions* of
one notebook is the uncertain path (plan §7a A2.4 [VERIFY]); attaching several *notebooks* is
ordinary. Sessions are sized from the measured calibration in `results/calibration.csv`
(fe times estimated at 60% of ft — fe skips the backbone backward pass).

Budgets are worst case, i.e. all 30 epochs. Early stopping (patience 5) normally ends runs
around epoch 10-15, so real sessions should finish well inside them.
"""

import argparse
import json
from pathlib import Path

# (configs, worst-case hours, time budget in minutes passed to train.py)
SESSIONS = {
    1: (["resnet50_fe", "resnet50_ft"], 4.32, 330),
    2: (["densenet121_fe", "densenet121_ft"], 5.20, 330),
    3: (["efficientnet_b0_fe", "efficientnet_b0_ft", "vit_base_patch16_224_fe"], 6.11, 340),
    4: (["vgg19_fe"], 3.85, 330),
    5: (["vgg19_ft"], 6.42, 330),          # heaviest run; alone by rule
    6: (["vit_base_patch16_224_ft"], 5.43, 330),  # alone by rule
}
DATA = "/kaggle/input/cifake-real-and-ai-generated-synthetic-images"


def build(session):
    configs, hours, budget = SESSIONS[session]
    cfg_args = " ".join(f"configs/{c}.yaml" for c in configs)
    md = [
        f"# AuthentiScan — A3 session {session} of {len(SESSIONS)}\n",
        "\n",
        f"Runs: **{', '.join(configs)}** | worst-case (30 epochs) ~{hours:.1f} h | "
        f"per-run time budget {budget} min\n",
        "\n",
        "Plan: `sem8_major/implementation_plan.md` §7a A3. Each config runs as its own\n",
        "subprocess and a failure does not stop the session. Before running, check the\n",
        "quota page shows enough GPU hours left for the worst case above.\n",
        "\n",
        "**After it finishes:** download `results_a3_s{}.zip` from the Output tab and send\n".format(session),
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
        "# 2. Extras only - never upgrade Kaggle's torch/torchvision (CUDA build is matched)\n",
        "!pip install -q timm grad-cam\n",
        "!nvidia-smi --query-gpu=name,memory.total --format=csv,noheader\n",
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
        "          f\"bs={c['batch_size']} max_epochs={c['max_epochs']}\")\n",
    ])
    code([
        "# 4. The session. One subprocess per config; a failure does not stop the rest.\n",
        f"!python code/run_session.py {cfg_args} \\\n",
        f"    --data-root {DATA} --results-dir /kaggle/working/results\n",
    ])
    code([
        "# 5. What this session produced\n",
        "import pandas as pd\n",
        "df = pd.read_csv(\"/kaggle/working/results/runs.csv\")\n",
        "cols = [\"run_id\", \"model\", \"mode\", \"best_epoch\", \"stop_reason\", \"train_time_min\",\n",
        "        \"val_acc\", \"test_acc\", \"test_auc\"]\n",
        "display(df[cols])\n",
        "print(\"\\nSanity (gate G3): fine-tuned CNN val_acc should be mid-90s; anything near\")\n",
        "print(\"0.50 means a pipeline bug - stop and debug rather than spending more quota.\")\n",
    ])
    code([
        "# 6. Package for download: results (incl. checkpoints) + nothing else\n",
        f"!cd /kaggle/working && zip -qr results_a3_s{session}.zip results && "
        f"ls -lh results_a3_s{session}.zip\n",
    ])
    return {"cells": cells,
            "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python",
                                        "name": "python3"},
                         "language_info": {"name": "python", "version": "3.12"}},
            "nbformat": 4, "nbformat_minor": 4}


def push(session, nb_text, token):
    import subprocess, tempfile, os
    payload = {
        # slug must match what Kaggle derives from the title, or a re-push creates a second
        # kernel instead of updating this one
        "slug": f"yaduvxnshi/authentiscan-a3-session-{session}",
        "newTitle": f"AuthentiScan A3 session {session}",
        "text": nb_text, "language": "python", "kernelType": "notebook",
        "isPrivate": True, "enableGpu": True, "enableInternet": True,
        "datasetDataSources": ["birdy654/cifake-real-and-ai-generated-synthetic-images"],
        "competitionDataSources": [], "kernelDataSources": [], "categoryIds": [],
    }
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
    a = ap.parse_args()

    nb = build(a.session)
    out = Path(__file__).parent / f"phase_a3_s{a.session}.ipynb"
    text = json.dumps(nb, indent=1)
    out.write_text(text, encoding="utf-8")
    configs, hours, budget = SESSIONS[a.session]
    print(f"wrote {out}  ({len(nb['cells'])} cells) — {', '.join(configs)}, "
          f"worst case {hours:.1f} h, budget {budget} min")
    if a.push:
        if not a.token:
            raise SystemExit("--push needs --token")
        push(a.session, text, a.token)
