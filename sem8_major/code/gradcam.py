"""Grad-CAM visualisation. Stub — Phase 1 proves it on one batch, Phase 3 builds the galleries.

CLI:
    python code/gradcam.py --run-id <run_id> --n 8

Uses the pytorch-grad-cam library (`grad-cam` in requirements.txt) rather than a hand-rolled
implementation. Loads results/<run_id>/best.pt with results/<run_id>/config_used.yaml, samples
n correctly classified and n misclassified test images with cfg["seed"], and writes the
overlays to figures/gradcam/<run_id>/{correct,incorrect}/.

Target layer per backbone (one entry per locked model, fixed in Phase 3):
    resnet50 / densenet121 / efficientnet_b0 / vgg19 — the last convolutional block.
    vit_base_patch16_224 — the final transformer block's norm layer, with the
    reshape_transform that pytorch-grad-cam requires for token-sequence activations.

The gallery covers the five backbones, each via its better-performing checkpoint from the
matrix, so Paper 2 can compare where each model looks and what it looks at when it is wrong.
"""


def make_gallery(run_id, n=8):
    raise NotImplementedError("Phase 0/1 implements this — see implementation_plan.md")


def main():
    raise NotImplementedError("Phase 0/1 implements this — see implementation_plan.md")


if __name__ == "__main__":
    main()
