"""A3 session driver: run a list of configs unattended in one Kaggle session.

    python code/run_session.py configs/resnet50_fe.yaml configs/resnet50_ft.yaml \
        --data-root /kaggle/input/cifake-real-and-ai-generated-synthetic-images \
        --results-dir /kaggle/working/results

Each config runs as a SEPARATE subprocess and a failure does not stop the session
(implementation_plan.md §7a A3): one crashed run must never cost the other runs in the same
"Save & Run All". Prints a summary table at the end and exits non-zero if any run failed, so
the notebook output makes the outcome obvious.
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path


def main():
    p = argparse.ArgumentParser()
    p.add_argument("configs", nargs="+")
    p.add_argument("--data-root")
    p.add_argument("--results-dir")
    p.add_argument("--python", default=sys.executable)
    args = p.parse_args()

    code_dir = Path(__file__).resolve().parent
    results = []
    for cfg in args.configs:
        cmd = [args.python, str(code_dir / "train.py"), "--config", cfg]
        if args.data_root:
            cmd += ["--data-root", args.data_root]
        if args.results_dir:
            cmd += ["--results-dir", args.results_dir]
        print(f"\n{'=' * 70}\nRUN {cfg}\n{'=' * 70}", flush=True)
        t0 = time.time()
        rc = subprocess.call(cmd)
        results.append((cfg, rc, (time.time() - t0) / 60))
        print(f"--- {cfg}: {'OK' if rc == 0 else f'FAILED (exit {rc})'} "
              f"in {results[-1][2]:.1f} min", flush=True)

    print(f"\n{'=' * 70}\nSESSION SUMMARY\n{'=' * 70}")
    for cfg, rc, mins in results:
        print(f"  {'OK    ' if rc == 0 else 'FAILED'}  {mins:6.1f} min  {cfg}")
    failed = [c for c, rc, _ in results if rc != 0]
    if failed:
        print(f"\n{len(failed)} run(s) failed: {failed}")
        print("Completed runs above are still valid - download their rows and artefact dirs.")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
