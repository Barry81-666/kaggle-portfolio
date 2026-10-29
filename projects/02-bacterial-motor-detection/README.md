# Bacterial Flagellar Motor Localization

My published inference notebook combines YOLO-family detections across tomogram slices, model fusion and three-dimensional distance-based suppression. Some augmentation branches are commented out in the source.

## Source and Contribution

[Original Kaggle notebook](https://www.kaggle.com/code/handudu/p1-1-0-65-74d43e), version ID `243588125`. Fork of parent kernel `84148436`; the parent's author and public URL were unavailable in the source snapshot.

**My role in the competition:** Prepared slice-level training data and local validation, trained YOLO-family detectors, and built multi-model fusion with 3D non-maximum suppression. This notebook shows the fusion and post-processing stage and is not presented as the team's final submission.

## Running and Interpreting the Archive

Inference requires multiple model checkpoints and three inputs marked private in the source snapshot.

Data and model weights are not included.
