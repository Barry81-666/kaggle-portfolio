# Bacterial Flagellar Motor Localization

An inference notebook combining YOLO-family detections across tomogram slices, model fusion and three-dimensional distance-based suppression. Several augmentation branches are commented out; their presence is not evidence they were used.

## Source and Contribution

[Original Kaggle notebook](https://www.kaggle.com/code/handudu/p1-1-0-65-74d43e), version ID `243588125`. Fork of parent kernel `84148436`; the parent's author and public URL were unavailable in the source snapshot. 

**My role in the competition:** Prepared slice-level training data and local validation, trained YOLO-family detectors, and built multi-model fusion with 3D non-maximum suppression. The archived inference fork's relationship to the selected final submission remains separate from this contribution statement.

## Running and Interpreting the Archive

Inference requires multiple model checkpoints and three inputs marked private in the source snapshot. The archived fork has not been matched to the selected final competition submission.

Inspect [notebook.ipynb](notebook.ipynb) and the original Kaggle Input list before configuring data and dependencies. Historical names, input dependencies and source hashes are retained in [provenance](../../meta/projects/02-bacterial-motor-detection/provenance.json); shared handling details are in [archive notes](../../docs/ARCHIVE_NOTES.md).
