"""Backbone construction via timm. Stub — Phase 1 implements it.

All five backbones come from timm's uniform create_model API with pretrained=True, so no
per-architecture special-casing is needed: resnet50, densenet121, efficientnet_b0, vgg19,
vit_base_patch16_224.

Contract:

    build_model(cfg) -> torch.nn.Module
        timm.create_model(cfg["model"], pretrained=True, num_classes=2). Binary task with a
        2-class head and CrossEntropyLoss; the fake-class probability used for AUC/AP is
        softmax(logits)[:, 1].

        cfg["mode"] selects the transfer-learning configuration:
          "fe" — feature extraction: every backbone parameter frozen (requires_grad=False),
                 only the freshly initialised classifier head trains.
          "ft" — fine-tuning: all parameters trainable.

    trainable_parameters(model) -> (n_trainable, n_total)
        Logged into the total_params / trainable_params columns of runs.csv for each run;
        Paper 2 reports trainable parameter counts per model alongside training time,
        following the Karki et al. table.
"""


def build_model(cfg):
    raise NotImplementedError("Phase 0/1 implements this — see implementation_plan.md")


def trainable_parameters(model):
    raise NotImplementedError("Phase 0/1 implements this — see implementation_plan.md")
