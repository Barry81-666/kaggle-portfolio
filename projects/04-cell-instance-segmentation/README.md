# Cell Instance Segmentation with MMDetection

An MMDetection/CBNetV2 inference workflow with class-specific score thresholds, mask-size filtering, overlap removal and run-length encoding. It is related code for the Sartorius competition, not a verified record of the final team solution.

## Observed Changes Relative to the Public Upstream

The archive adds concrete config/checkpoint paths, inference and submission cells, class-specific thresholds and mask postprocessing relative to the currently accessible parent version. The [comparison](../../docs/CELL_UPSTREAM_COMPARISON.md) records the precise version boundary. These are observed source differences, not an assertion that Barry Wang independently authored each change or that they explain the team rank.

## Source and Contribution

[Original Kaggle notebook](https://www.kaggle.com/code/handudu/how-to-use-mmdectetion), version ID `83951341`. Fork of [KUGAI CHEN](https://www.kaggle.com/code/kugaichen/how-to-use-mmdectetion). Personal modifications and the relationship to the final team submission remain to be confirmed.

## Running and Interpreting the Archive

The notebook uses a 2021 PyTorch 1.7 / CUDA 11 environment, MMDetection/CBNetV2, local wheels and private model inputs. Review installation and cleanup cells before running. The archived fork is not verified as the final competition submission.

Inspect [notebook.ipynb](notebook.ipynb) and the original Kaggle Input list before configuring data and dependencies. Historical names, input dependencies and source hashes are retained in [provenance](../../meta/projects/04-cell-instance-segmentation/provenance.json); shared handling details are in [archive notes](../../docs/ARCHIVE_NOTES.md).
