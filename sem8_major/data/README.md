# data/ — datasets (gitignored)

Nothing here is committed except this file and `cifake_split_seed42.csv`, the split assignment
written once at Phase 0 (see `.gitignore`). The split file is small and must travel with the
repo, because every run and every reported number depends on the same 10,000-image validation
carve-out from the CIFAKE training set (seed 42).

On Kaggle the datasets are **attached natively** to the notebook from the Add Data sidebar, not
downloaded into this directory; only the local CPU smoke tests need a local copy. Point
`data.root` in the config at whichever path applies.

## Expected layout

```
data/
├── cifake_split_seed42.csv        relative_path,label,split  (split in {train, val, test})
├── cifake/                        120,000 images at 32x32; fakes are Stable Diffusion v1.4
│   ├── train/{REAL,FAKE}/         100,000 images (50k real / 50k fake); 10k carved off as val
│   └── test/{REAL,FAKE}/          20,000 images (10k / 10k), official split, never trained on
└── genimage/                      test-only cross-generator subset, generators unseen in training
    ├── midjourney/{real,fake}/
    ├── adm/{real,fake}/
    ├── biggan/{real,fake}/
    └── vqdm/{real,fake}/          roughly 2,000-3,000 balanced images per generator; the real
                                   half comes from GenImage's paired ImageNet real images
```

Licences: the Kaggle CIFAKE listing reports "License(s): other" — read the exact terms on the
dataset page / in Bird & Lotfi before Paper 2 reproduces any CIFAKE image `[VERIFY at first
gallery]`; Grad-CAM figures showing CIFAKE images must credit C51 (Bird & Lotfi) and CIFAR-10
(Krizhevsky) for the real half. tiny-genimage is CC BY-NC-SA 4.0 (see
`genimage_access_note.md`).

CIFAKE directory names confirmed 18 Aug 2026 against the Kaggle release (downloaded locally):
`train|test / REAL|FAKE`, uppercase, filenames like `0 (10).jpg` (spaces and parentheses).
The GenImage access path is resolved in `genimage_access_note.md` (primary:
`yangsangtai/tiny-genimage` on Kaggle, official `imagenet_ai_<date>_<generator>/{train,val}/{ai,nature}`
layout); SD v1.4/v1.5 generators are excluded from the subset because they are the same
family CIFAKE trains on.
