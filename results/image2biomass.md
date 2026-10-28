# Image2Biomass: Historical Validation Results

Source: [my public notebook](https://www.kaggle.com/code/handudu/1-train-baseline-demo), version ID **277387301**. The retrieved file matches original SHA-256 `032d6713463e7c0088ade4923bf21ec781c6b2b4cda14435c1094592387a26fa`. Values below are copied from its existing output, not newly computed. Cell and output indices are zero-based.

The notebook uses `eva02_base_patch14_448`, 448-pixel images, batch size 8, initial learning rate 0.0001 and up to 20 epochs with early stopping. Five biomass targets are log1p-transformed for training; validation weighted R² is calculated after transforming predictions back to the original scale. The weights are 0.1 / 0.1 / 0.1 / 0.2 / 0.5 in the notebook's target order. An EMA class is defined, but the main loop shown here trains the base model.

| Fold setting | Input fold CSV | Reported mean of five best-fold weighted R² | Summary output in cell 5 |
| --- | --- | --- | --- |
| Random | `folds_by_random.csv` | 0.6820 | 265 |
| NDVI | `folds_by_Pre_GSHH_NDVI.csv` | 0.6697 | 489 |
| Sampling date | `folds_by_Sampling_Date.csv` | 0.5774 | 699 |
| Species | `folds_by_Species.csv` | 0.4881 | 871 |

## Per-Fold Record

| Setting | Fold | Best weighted R² | Selected epoch | Output in cell 5 |
| --- | --- | --- | --- | --- |
| random | 0 | 0.7329 | 20 | 57 |
| random | 1 | 0.5653 | 18 | 111 |
| random | 2 | 0.6499 | 7 | 143 |
| random | 3 | 0.7865 | 19 | 203 |
| random | 4 | 0.6751 | 15 | 263 |
| NDVI | 0 | 0.6827 | 11 | 307 |
| NDVI | 1 | 0.6226 | 9 | 349 |
| NDVI | 2 | 0.7179 | 13 | 401 |
| NDVI | 3 | 0.6334 | 10 | 439 |
| NDVI | 4 | 0.6919 | 12 | 487 |
| Date | 0 | 0.6696 | 18 | 543 |
| Date | 1 | 0.4645 | 8 | 579 |
| Date | 2 | 0.6651 | 17 | 637 |
| Date | 3 | 0.4763 | 3 | 657 |
| Date | 4 | 0.6115 | 10 | 697 |
| Species | 0 | 0.5344 | 10 | 743 |
| Species | 1 | 0.4750 | 4 | 767 |
| Species | 2 | 0.7025 | 18 | 821 |
| Species | 3 | 0.5363 | 5 | 851 |
| Species | 4 | 0.1926 | 2 | 869 |

## Interpretation

The logs show lower selected validation scores under the date/species settings than random splitting. That observation motivates checking the split-generation policy; it does not establish a causal effect of grouping or performance on unseen dates/species. The CSV names describe the settings, but their private contents and generation code were not available to verify group separation, fold sizes or sample overlap.

Best epochs are chosen on the same validation folds whose scores are summarized, so these are selected validation values, not unbiased final-test estimates. The mean of fold R² values is not a pooled OOF R². No confidence interval is reported, and no leaderboard score or final submission is inferred. Training was not rerun.

[Structured values and source locations](image2biomass.json) · [Selected log lines](image2biomass-selected-log.txt) · [Project source and limitations](../projects/03-image2biomass/)
