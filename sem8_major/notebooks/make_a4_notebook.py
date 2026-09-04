"""Generate (and optionally push) the A4 Kaggle notebook: cross-generator sweep + Grad-CAM
galleries, evaluation only (implementation_plan.md 7a A4; placement amendment of 4 Sep 2026).

    python notebooks/make_a4_notebook.py
    python notebooks/make_a4_notebook.py --push --token KGAT_xxx

Checkpoints are never uploaded: the eight A3 session notebooks' outputs (which hold every
run dir with its best.pt and config_used.yaml) are attached as kernel data sources, next to
CIFAKE and tiny-genimage. The notebook autodetects all three mounts and refuses to run if any
canonical checkpoint (results/canonical_runs.txt) is missing.
"""

import argparse
import json
from pathlib import Path

from make_a3_notebook import push_payload

SLUG = "yaduvxnshi/authentiscan-a4-crossgen-and-gradcam"
TITLE = "AuthentiScan A4 crossgen and gradcam"
DATASETS = ["birdy654/cifake-real-and-ai-generated-synthetic-images",
            "yangsangtai/tiny-genimage"]
SESSION_KERNELS = [f"yaduvxnshi/authentiscan-a3-session-{n}" for n in range(1, 9)]


def build():
    md = [
        "# AuthentiScan — A4: cross-generator sweep + Grad-CAM galleries\n",
        "\n",
        "**First run of this notebook?** Kaggle Secrets attach per notebook: open Add-ons →\n",
        "Secrets and toggle `GITHUB_PAT` ON for this notebook first, or cell 1 fails with\n",
        "'No user secrets exist'.\n",
        "\n",
        "Evaluation only — no training. Inputs: CIFAKE, `yangsangtai/tiny-genimage`, and the\n",
        "outputs of A3 sessions 1–8 (every canonical checkpoint). Cross-generator: 10 canonical\n",
        "checkpoints × 4 generators × 2 conditions = 80 `crossgen.csv` rows. Grad-CAM: five\n",
        "better checkpoints, shared correct set. Estimated wall-clock 1–2 h (an estimate — image\n",
        "decoding dominates, not the GPU); any GPU is fine here, results do not depend on it.\n",
        "\n",
        "**After it finishes:** download `results_a4.zip` from the Output tab and send it\n",
        "back — `crossgen.csv` merges with `code/merge_runs.py --kind crossgen`, never retyped.\n",
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
        "# 2. Extras (never upgrade Kaggle's torch/torchvision), then find the three mounts.\n",
        "!pip install -q timm grad-cam\n",
        "\n",
        "import os, sys, torch\n",
        "print(\"GPU:\", torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"NO GPU\")\n",
        "# Evaluation only: metrics do not depend on the GPU model, so no T4 assertion here.\n",
        "\n",
        "DATA = GEN = None\n",
        "for root, dirs, _ in os.walk(\"/kaggle/input\"):\n",
        "    if DATA is None and os.path.isdir(os.path.join(root, \"train\", \"REAL\")):\n",
        "        DATA = root\n",
        "    if GEN is None and any(d.lower() == \"imagenet_midjourney\" or\n",
        "                           d.lower().startswith(\"imagenet_ai_\") for d in dirs):\n",
        "        GEN = root\n",
        "    if root.count(os.sep) > 5:   # don't descend into image folders\n",
        "        dirs.clear()\n",
        "assert DATA, \"CIFAKE not found under /kaggle/input - is the dataset attached?\"\n",
        "assert GEN, \"tiny-genimage not found under /kaggle/input - is the dataset attached?\"\n",
        "print(\"CIFAKE:      \", DATA)\n",
        "print(\"tiny-genimage:\", GEN)\n",
        "\n",
        "sys.path.insert(0, \"code\")\n",
        "from eval import find_checkpoints, read_manifest\n",
        "CK = find_checkpoints(\"/kaggle/input\")\n",
        "IDS = read_manifest(\"results/canonical_runs.txt\")\n",
        "for rid in IDS:\n",
        "    print((\"OK      \" if rid in CK else \"MISSING \") + rid, CK.get(rid, \"\"))\n",
        "missing = [r for r in IDS if r not in CK]\n",
        "assert not missing, f\"attach the A3 session outputs that hold: {missing}\"\n",
    ])
    code([
        "# 3. Cross-generator sweep: verifies tiny-genimage contents first, then 80 cells.\n",
        "# One eval.py subprocess per cell; a failure does not stop the rest.\n",
        "!python code/run_crossgen.py --checkpoint-root /kaggle/input \\\n",
        "    --genimage-root \"{GEN}\" --results-dir /kaggle/working/results\n",
    ])
    code([
        "# 4. Grad-CAM galleries: five better checkpoints, shared correct set (plan 7a A1.5/A4).\n",
        "!python code/make_galleries.py --checkpoint-root /kaggle/input \\\n",
        "    --data-root \"{DATA}\" --results-dir /kaggle/working/results \\\n",
        "    --out-root /kaggle/working/figures/gradcam\n",
    ])
    code([
        "# 5. What this session produced\n",
        "import pandas as pd\n",
        "cg = pd.read_csv(\"/kaggle/working/results/crossgen.csv\")\n",
        "print(len(cg), \"crossgen rows (expected 80)\")\n",
        "display(cg.pivot_table(index=\"run_id\", columns=[\"condition\", \"generator\"],\n",
        "                       values=\"acc\").round(4))\n",
        "display(pd.read_csv(\"/kaggle/working/results/genimage_verification.csv\"))\n",
        "print(\"galleries:\", sorted(os.listdir(\"/kaggle/working/figures/gradcam\")))\n",
    ])
    code([
        "# 6. Package for download: crossgen rows + per-cell artefacts + galleries (no checkpoints)\n",
        "!cd /kaggle/working && zip -qr results_a4.zip results figures && ls -lh results_a4.zip\n",
    ])
    return {"cells": cells,
            "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python",
                                        "name": "python3"},
                         "language_info": {"name": "python", "version": "3.12"}},
            "nbformat": 4, "nbformat_minor": 4}


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--push", action="store_true")
    ap.add_argument("--token", help="Kaggle API token (not stored on disk)")
    a = ap.parse_args()

    nb = build()
    out = Path(__file__).parent / "phase_a4_crossgen_gradcam.ipynb"
    text = json.dumps(nb, indent=1)
    out.write_text(text, encoding="utf-8")
    print(f"wrote {out}  ({len(nb['cells'])} cells)")
    if a.push:
        if not a.token:
            raise SystemExit("--push needs --token")
        push_payload({
            "slug": SLUG, "newTitle": TITLE, "text": text, "language": "python",
            "kernelType": "notebook", "isPrivate": True, "enableGpu": True,
            "enableInternet": True, "datasetDataSources": DATASETS,
            "kernelDataSources": SESSION_KERNELS, "competitionDataSources": [],
            "categoryIds": [],
        }, a.token)
