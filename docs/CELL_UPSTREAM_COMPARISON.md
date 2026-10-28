# Cell Segmentation: Comparison with the Public Parent

Compared on **2026-10-28**: [handudu version `83951341`](https://www.kaggle.com/code/handudu/how-to-use-mmdectetion) (2021-12-30) and [KUGAI CHEN's currently accessible notebook](https://www.kaggle.com/code/kugaichen/how-to-use-mmdectetion), kernel `23363385`, **version number 4**, API `lastRunTime` **2026-10-25T10:06:17.6427748Z**. The current parent is not established as the exact historical revision from which the fork was created.

| Observed difference in the handudu archive | Interpretation boundary |
| --- | --- |
| Copies a CBNetV2 Swin config and a timm 0.4.12 wheel from mounted inputs; uses `CBNetV2-main` | Different dependency/configuration setup; private inputs prevent full inspection |
| Provides concrete model config and checkpoint (`0317.pth`) instead of parent placeholders | An inference configuration is present; checkpoint lineage is not recorded |
| Adds repeated RLE/mask helpers and a complete test-image inference loop | Source-level additions relative to current parent; not proof of personal authorship |
| Applies score thresholds 0.25 / 0.65 / 0.35 and minimum mask sizes 75 / 75 / 150 for classes 0 / 1 / 2 | Specific postprocessing settings are observable; their selection process and performance effect are unknown |
| Uses a dominant predicted class to choose thresholds, removes overlapping mask pixels, encodes masks and writes submission rows | Submission construction can be inspected, but is not matched to the final competition submission |
| Includes additional installation and cleanup commands | Review before execution in any new environment |

The archived fork's original download SHA-256 is `917e2e47a3c1b207f62343642e3e85289c6306d9aa7dd0e7198d9e4f80dc7654`. The downloaded current-parent source SHA-256 is `c660778566b303ba79e2cb89af72d56820635a28c0ce3917f82fa793f0de6c84`. Comparisons used cell source text, ignoring output/metadata differences. The user's unchanged source is [here](../projects/04-cell-instance-segmentation/notebook.ipynb); [provenance](../meta/projects/04-cell-instance-segmentation/provenance.json) preserves the fork relationship.

Barry Wang reports training MMDetection models and tuning class thresholds, minimum mask sizes and overlap removal. This statement describes his competition work; the version comparison does not independently establish authorship of every difference or their causal effect on the team's 26 / 1505 result. No private input or additional teammate code was published for this comparison.
