# Runtime environment — recorded 2026-08-22 04:02

## Hardware

- GPU: Tesla T4, 15 GB VRAM, CC 7.5, 40 SMs
- CUDA runtime: 12.8, cuDNN: 91002
- Platform: Linux-6.12.90+-x86_64-with-glibc2.35
- Processor: x86_64
- Python: 3.12.13

```
CPU(s):                                  4
Model name:                              Intel(R) Xeon(R) CPU @ 2.00GHz
total        used        free      shared  buff/cache   available
Mem:            31Gi       1.3Gi        22Gi       1.0Mi       7.1Gi        29Gi
```

## Package versions (as provided by this environment)

- numpy: 2.0.2
- pillow: 11.3.0
- pytorch-grad-cam: (no __version__)
- scikit-learn: 1.6.1
- timm: 1.0.26
- torch: 2.10.0+cu128
- torchvision: 0.25.0+cu128

## nvidia-smi

```
Sat Aug 22 04:02:20 2026       
+-----------------------------------------------------------------------------------------+
| NVIDIA-SMI 580.159.04             Driver Version: 580.159.04     CUDA Version: 13.0     |
+-----------------------------------------+------------------------+----------------------+
| GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
| Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
|                                         |                        |               MIG M. |
|=========================================+========================+======================|
|   0  Tesla T4                       Off |   00000000:00:04.0 Off |                    0 |
| N/A   42C    P8             11W /   70W |       3MiB /  15360MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+
|   1  Tesla T4                       Off |   00000000:00:05.0 Off |                    0 |
| N/A   40C    P8             13W /   70W |       3MiB /  15360MiB |      0%      Default |
|                                         |                        |                  N/A |
+-----------------------------------------+------------------------+----------------------+

+-----------------------------------------------------------------------------------------+
| Processes:                                                                              |
|  GPU   GI   CI              PID   Type   Process name                        GPU Memory |
|        ID   ID                                                               Usage      |
|=========================================================================================|
|  No running processes found                                                             |
+-----------------------------------------------------------------------------------------+
```

## Still to record by hand (browser-only facts)

- Maximum single-session GPU duration: [VERIFY in session]
- Weekly quota reset day: [VERIFY on the quota page]
- Can outputs of multiple versions of one notebook be attached at once? [VERIFY — A4 depends on it; fallback is forward-copying artefact dirs]
