# Cell Instance Segmentation with MMDetection

My inference and submission notebook for the Sartorius competition (team silver medal, 26 / 1505) uses MMDetection and a CBNetV2-Swin configuration.

## My Role

Trained MMDetection instance segmentation models and tuned class-specific score thresholds, minimum mask sizes and overlap removal.

Compared with the public MMDetection tutorial it builds on, by [KUGAI CHEN](https://www.kaggle.com/code/kugaichen/how-to-use-mmdectetion), this version adds:

- A CBNetV2-Swin configuration and checkpoint.
- Class-specific score thresholds (0.25 / 0.65 / 0.35) and minimum mask areas (75 / 75 / 150), selected according to the dominant predicted cell type in each image.
- Overlapping-mask pixel removal, RLE encoding and a complete test-set submission workflow.

It is not presented as the team's final submission.

## Running the Notebook

My published notebook uses a 2021 environment with PyTorch 1.7, CUDA 11, MMDetection/CBNetV2 and local wheels. The checkpoint and two private inputs are not included. Review the installation and cleanup cells before running.

Source: [Kaggle notebook](https://www.kaggle.com/code/handudu/how-to-use-mmdectetion?scriptVersionId=83951341) (version 83951341). Data and model weights are not included.
