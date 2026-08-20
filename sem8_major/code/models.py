"""Backbone construction via timm (implemented at A1).

All five backbones come from timm's uniform create_model API with pretrained=True:
resnet50, densenet121, efficientnet_b0, vgg19, vit_base_patch16_224.
Binary task with a 2-class head and CrossEntropyLoss; the fake-class probability used for
AUC/AP is softmax(logits)[:, 1].

    build_model(cfg) -> torch.nn.Module
        cfg["mode"]: "fe" freezes every parameter except the fresh classifier head;
        "ft" leaves everything trainable.

    set_train_mode(model, mode)
        Call instead of model.train() each epoch. For "fe" the backbone stays in eval mode so
        BatchNorm running statistics keep their ImageNet values — otherwise "frozen backbone"
        would be false: requires_grad=False does not stop BN stats from adapting
        (implementation_plan.md §7a A1.2). Only the head is put in train mode.

    trainable_parameters(model) -> (n_trainable, n_total)
        Logged into the trainable_params / total_params columns of runs.csv.
"""

import timm


def build_model(cfg):
    model = timm.create_model(cfg["model"], pretrained=True, num_classes=2)
    if cfg["mode"] == "fe":
        head_params = set(id(p) for p in model.get_classifier().parameters())
        for p in model.parameters():
            p.requires_grad = id(p) in head_params
    elif cfg["mode"] != "ft":
        raise ValueError(f"mode must be fe or ft, got {cfg['mode']!r}")
    return model


def set_train_mode(model, mode):
    if mode == "fe":
        model.eval()                      # backbone: BN stats and dropout frozen
        model.get_classifier().train()    # head: trains normally
    else:
        model.train()


def trainable_parameters(model):
    n_trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    n_total = sum(p.numel() for p in model.parameters())
    return n_trainable, n_total


if __name__ == "__main__":
    # selfcheck: fe freezes everything but the head, and the head really trains
    cfg = {"model": "resnet50", "mode": "fe"}
    m = build_model(cfg)
    tr, tot = trainable_parameters(m)
    head = sum(p.numel() for p in m.get_classifier().parameters())
    assert tr == head and tot > tr, (tr, head, tot)
    set_train_mode(m, "fe")
    assert not m.layer1.training and m.get_classifier().training
    m2 = build_model({"model": "resnet50", "mode": "ft"})
    tr2, tot2 = trainable_parameters(m2)
    assert tr2 == tot2 == tot
    print(f"models selfcheck OK (resnet50: total {tot:,}, fe-trainable {tr:,})")
