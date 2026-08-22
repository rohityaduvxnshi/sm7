"""Record the exact runtime environment (A2/G2; Paper 2 must report hardware and versions).

    python code/record_env.py [--out results/kaggle_env.md]

Run once in the first Kaggle GPU session. Captures GPU model + VRAM, CPU, RAM, and the
versions Kaggle actually provides (they differ from the local requirements.lock and change
without notice), plus CUDA/cuDNN. Commit the output; Paper 2's setup section quotes it.
"""

import argparse
import platform
import subprocess
from datetime import datetime
from pathlib import Path


def _run(cmd):
    try:
        return subprocess.run(cmd, shell=True, capture_output=True, text=True,
                              timeout=60).stdout.strip()
    except Exception as e:  # noqa: BLE001 - a missing tool must not abort the recording
        return f"(unavailable: {e})"


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--out", default="results/kaggle_env.md")
    args = p.parse_args()

    import torch
    lines = [f"# Runtime environment — recorded {datetime.now():%Y-%m-%d %H:%M}", ""]

    lines += ["## Hardware", ""]
    if torch.cuda.is_available():
        pr = torch.cuda.get_device_properties(0)
        lines += [f"- GPU: {pr.name}, {round(pr.total_memory / 2**30)} GB VRAM, "
                  f"CC {pr.major}.{pr.minor}, {pr.multi_processor_count} SMs",
                  f"- CUDA runtime: {torch.version.cuda}, cuDNN: {torch.backends.cudnn.version()}"]
    else:
        lines.append("- GPU: none visible to torch (CPU session)")
    lines += [f"- Platform: {platform.platform()}",
              f"- Processor: {platform.processor() or '(not reported)'}",
              f"- Python: {platform.python_version()}"]
    cpu = _run("lscpu | grep -E 'Model name|^CPU\\(s\\):'")
    mem = _run("free -h | head -2")
    if cpu and not cpu.startswith("(unavailable"):
        lines += ["", "```", cpu, mem, "```"]

    lines += ["", "## Package versions (as provided by this environment)", ""]
    import timm
    import numpy
    import sklearn
    import PIL
    mods = {"torch": torch.__version__, "timm": timm.__version__,
            "numpy": numpy.__version__, "scikit-learn": sklearn.__version__,
            "pillow": PIL.__version__}
    try:
        import torchvision
        mods["torchvision"] = torchvision.__version__
    except ImportError:
        pass
    try:
        import pytorch_grad_cam
        mods["pytorch-grad-cam"] = getattr(pytorch_grad_cam, "__version__", "(no __version__)")
    except ImportError:
        pass
    lines += [f"- {k}: {v}" for k, v in sorted(mods.items())]

    lines += ["", "## nvidia-smi", "", "```", _run("nvidia-smi"), "```", ""]
    lines += ["## Still to record by hand (browser-only facts)", "",
              "- Maximum single-session GPU duration: [VERIFY in session]",
              "- Weekly quota reset day: [VERIFY on the quota page]",
              "- Can outputs of multiple versions of one notebook be attached at once? "
              "[VERIFY — A4 depends on it; fallback is forward-copying artefact dirs]", ""]

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    print("\n".join(lines))
    print(f"\nwrote {out}")


if __name__ == "__main__":
    main()
