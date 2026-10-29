# Knee Diagnostic Labels Without a Gold Standard

How can I assess diagnoses extracted from radiology reports without an independent reference standard? Medical AI is increasingly trained and evaluated on labels extracted from radiology reports by language models. I compare five public label sources on **4,349 knee studies and 12 findings**, then simulate how label errors can distort AUC evaluation—even when the sources appear to agree.

## Three findings

**1. Five sources form two stable similarity groups.** I found that Steven/Pilkwang/Lixin cluster together, while Dread/Yunus form the other group; this pattern persists across three agreement summaries and 1,000 study-bootstrap resamples. For effusion, within-group kappa is **0.894–0.989**, compared with **0.311–0.377** between groups. The sources' documented differences in severity and mention conventions offer a plausible explanation for this separation.

![Source similarity groups](figures/F5c_source_clusters.png)

**2. Model checking changes how I interpret apparent consensus.** I fitted a two-class model that treats the sources as conditionally independent. In each of 11 converged fits, none of 2,000 posterior predictive replicates reproduced a discrepancy as large as the observed one; synovitis also failed to converge. These findings challenge the model's combined assumptions about a common binary target and conditional independence.

**3. More observations can make a misspecified correction more precisely wrong.** In simulations with score-dependent label errors, known-parameter AUC correction at n=977 produced bias of **+0.1274**, with nominal 95% intervals covering the truth only **12.4%** of the time. With score-independent errors, the same correction removed most bias. I also compared small-sample interval methods; the [full report](report.md) explains why simply increasing bootstrap repetitions helped little.

![AUC bias under two error mechanisms](figures/F7_auc_bias.png)

## Limitations

I measure agreement between report-derived labels, not accuracy against MRI findings. Shared reporting errors, differing definitions and incomplete source provenance limit what I can infer about accuracy or dependence; the clusters do not establish copying or an effective number of independent sources. Missing labels change the comparison samples, and I cannot identify repeated patients. The AUC findings come from specified simulations rather than actual model predictions or expert-panel validation. I added clustering and interval-method comparisons after inspecting the primary results and report them as exploratory analyses.

## Reproduction and sources

I froze the [analysis plan](analysis/SAP.md) before examining label agreement, latent-model fits or AUC simulation outcomes. The [research decisions](analysis/DECISIONS.md), [R guide](analysis/README.md), [aggregate results](results/) and [checks](analysis/CHECKS.md) document the work. I publish aggregate tables and figures; raw labels, study identifiers and simulation draws remain external. The [source audit](analysis/SOURCE_AUDIT.md) credits the dataset authors and distinguishes original extractions from later blends.
