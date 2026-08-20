# notebooks/ — Kaggle notebooks

Project notebook: `yaduvxnshi/notebook322addb147` (private; CIFAKE attached 19 Aug 2026;
retitle it on Kaggle when convenient). GPU and Internet are off — enable both in the editor's
Session options before the B1 GPU smoke run (Internet is needed to pip-install timm/grad-cam).

One thin notebook per phase (`phase0_setup.ipynb`, `phase1_smoke.ipynb`, ...): install, fetch
code, call the CLI. Logic lives in `code/`, not in cells, so runs stay reproducible.

1. `!pip install -q -r requirements.txt` — Kaggle already ships torch/torchvision, do not upgrade them.
2. Get `code/` and `configs/` into the session: clone the repo, or upload them as a Kaggle dataset.
3. Attach CIFAKE from Add Data (`birdy654/cifake-real-and-ai-generated-synthetic-images` —
   verify the owner slug; several same-named re-uploads exist). It mounts at
   `/kaggle/input/cifake-real-and-ai-generated-synthetic-images` (confirmed 19 Aug 2026);
   point `data.root` in the config there.
4. `!python code/train.py --config configs/<name>.yaml`.
5. Download `results/runs.csv` and `results/<run_id>/` from the notebook output and commit them here — results are never retyped by hand.

`reference_thirdparty_y5cy5c_keras_cifake.ipynb` is **someone else's public notebook**
(Kaggle user y5cy5c), pulled 19 Aug 2026 as a reference only: a Keras/keras_tuner small-CNN
example on CIFAKE. Do not copy code or numbers from it — different stack (Keras vs our
PyTorch/timm), and it validates on the official test set, which our plan forbids.
