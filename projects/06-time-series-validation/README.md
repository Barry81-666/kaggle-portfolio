# Time Series Validation for Tactical Allocation

A historical rolling-window experiment that fits models and searches training-window lengths and allocation multipliers using time-ordered validation. It illustrates how validation choices enter model selection; the title alone does not establish absence of leakage.

## Source and Contribution

[Original Kaggle notebook](https://www.kaggle.com/code/handudu/base-noleak-val-local), version ID `279919839`. The public inventory did not mark this as a fork; that is not an independent-authorship audit. Publication under the handudu account is recorded; task-specific personal contributions have not been independently established.

## Running and Interpreting the Archive

The source contains a commented-out pipeline followed by an active version. Window length and allocation multiplier are selected using the same validation grid; the reported maximum is not an independent test estimate or evidence of investment performance.

Inspect [notebook.ipynb](notebook.ipynb) and the original Kaggle Input list before configuring data and dependencies. Historical names, input dependencies and source hashes are retained in [provenance](../../meta/projects/06-time-series-validation/provenance.json); shared handling details are in [archive notes](../../docs/ARCHIVE_NOTES.md).
