# Time Series Validation for Tactical Allocation

My published notebook records a historical rolling-window experiment that fits models and searches training-window lengths and allocation multipliers using time-ordered validation. It illustrates how validation choices enter model selection; the title alone does not establish absence of leakage.

## Source and Contribution

[Original Kaggle notebook](https://www.kaggle.com/code/handudu/base-noleak-val-local), version ID `279919839`. Published from my Kaggle account; credits to other authors inside the source are kept intact.

## Running and Interpreting the Archive

The source contains a commented-out pipeline followed by an active version. Window length and allocation multiplier are selected using the same validation grid; the reported maximum is not an independent test estimate or evidence of investment performance.

Data and model weights are not included.
