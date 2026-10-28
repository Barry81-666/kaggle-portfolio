# Image2Biomass: Validation Across Split Designs

An EVA02/timm image-regression baseline for five biomass targets, trained with log-transformed targets and a weighted loss. The same notebook loops through four predefined fold designs and reports weighted R² on the original target scale.

## Historical Validation Results

| Fold CSV setting | Mean of five best-fold weighted R² values |
| --- | --- |
| Random | 0.6820 |
| NDVI | 0.6697 |
| Sampling date | 0.5774 |
| Species | 0.4881 |

These values are printed in the original Kaggle run, not recomputed in this revision. Each fold selects its best epoch on that same validation fold. Differences motivate a closer look at split design, but do not establish out-of-group performance because the fold CSVs are private. [Per-fold values, epochs and exact log locations](../../results/image2biomass.md).

## Source and Contribution

[Original Kaggle notebook](https://www.kaggle.com/code/handudu/1-train-baseline-demo), version ID `277387301`. Fork of parent kernel `99732107`; the parent's author and public URL were unavailable in the source snapshot. Publication under the handudu account is recorded; task-specific personal contributions have not been independently established.

## Running and Interpreting the Archive

The four sets of fold assignments come from a private input. Historical logs are available, but split membership, grouped independence and generalization cannot be independently verified. Best epochs were selected on the reported validation folds.

Inspect [notebook.ipynb](notebook.ipynb) and the original Kaggle Input list before configuring data and dependencies. Historical names, input dependencies and source hashes are retained in [provenance](../../meta/projects/03-image2biomass/provenance.json); shared handling details are in [archive notes](../../docs/ARCHIVE_NOTES.md).
