# Front matter

**Working title:** Transfer Learning for AI-Generated Image Detection: A Matched Comparison of Four CNN Backbones and a Vision Transformer on CIFAKE, with Grad-CAM and Cross-Generator Evaluation

Rohit Yadav, Vishal, Hardik Mehlawat — Amity School of Engineering and Technology, Amity University Uttar Pradesh. Guide: Dr. Richa Gupta.

*[Working title. Author order, the guide's designation and the shape of the merged publication are open items 4, 11 and 19 in CLAUDE.md and are decided at the P2 gate, not here.]*

## Abstract

Detectors of AI-generated images are usually reported one architecture at a time, on one dataset, rarely with an explanation analysis and a test on unseen generators. This paper compares four ImageNet-pretrained convolutional neural network (CNN) backbones (ResNet50, DenseNet121, EfficientNet-B0, VGG19) and a Vision Transformer (ViT-B/16) under one protocol on CIFAKE (120,000 images: CIFAR-10 photographs and Stable Diffusion v1.4 images at 32×32 pixels). Each backbone is trained frozen (feature extraction) and with every parameter updated (fine-tuning), under one seed, a committed split and logged library versions; every reported number is generated from the run logs by script. On the 20,000-image test set, fine-tuning improves every backbone by 3.5 to 7.4 percentage points and changes the ordering: VGG19 is the weakest frozen backbone (90.54%) and the strongest fine-tuned CNN (97.91%). ViT-B/16 leads under both configurations (94.74% and 98.88%), while fine-tuned DenseNet121 and EfficientNet-B0 (97.60% and 97.56%) cannot be separated on one seed. On eight shared test images, Grad-CAM puts the fine-tuned CNNs' highest activations mostly on the subject; on the ViT the method as applied returned an all-zero map on half of them. On 1,000-image subsets of four unseen GenImage generators (Midjourney, ADM, BigGAN, VQDM), every checkpoint falls to chance: per-checkpoint mean accuracy 0.46 to 0.53, and an area under the receiver operating characteristic curve (AUC) below 0.5 in 43 of 80 cells. Content shift, downsampling and a PNG/JPEG asymmetry between the classes prevent attributing the collapse to the generators alone; it is reported as a bracketed negative result.

**Keywords:** AI-generated image detection; transfer learning; convolutional neural networks; vision transformer; Grad-CAM; cross-generator generalisation; CIFAKE
