# Image2Biomass: Validation Across Split Designs

My published notebook contains an EVA02/timm image-regression baseline for five biomass targets, trained with log-transformed targets and a weighted loss. The same notebook loops through four predefined fold designs and reports weighted R² on the original target scale.

## Historical Validation Results

| Fold CSV setting | Mean of five best-fold weighted R² values |
| --- | --- |
| Random | 0.6820 |
| NDVI | 0.6697 |
| Sampling date | 0.5774 |
| Species | 0.4881 |

These values are printed in the original Kaggle run, not recomputed. Each fold selects its best epoch on that same validation fold. Differences motivate a closer look at split design, but do not establish out-of-group performance because the fold CSVs are private. [Per-fold values, epochs and exact log locations](../../results/image2biomass.md).

## Source and Contribution

[Original Kaggle notebook](https://www.kaggle.com/code/handudu/1-train-baseline-demo), version ID `277387301`. Fork of parent kernel `99732107`; the parent's author and public URL were unavailable in the source snapshot. I adapted this notebook from an upstream baseline and designed some of its validation splits.

## Running and Interpreting the Archive

The four sets of fold assignments come from a private input. Historical logs are available, but split membership, grouped independence and generalization cannot be independently verified. Best epochs were selected on the reported validation folds.

Data and model weights are not included.
