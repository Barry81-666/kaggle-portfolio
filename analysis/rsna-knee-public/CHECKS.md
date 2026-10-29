# Execution and release checks

Executed 2026-10-28; post-hoc additions and release checks 2026-10-29 using R 4.5.1 and the versions pinned in `renv.lock`.

## Statistical software

- All R sources parse; the full synthetic test suite passes.
- Rank AUC agrees with pROC, including tied scores and undefined single-class cases.
- Kappa handles missing pairs and degenerate margins; majority votes exclude the source being compared and leave ties missing.
- Compressed response-pattern bootstrap statistics match directly expanded observations for paired agreement, Cohen kappa, PABAK and Fleiss kappa.
- The native latent sampler's prior predictive probabilities normalize; all draws satisfy the stated orientation. Under a correctly specified synthetic model, all parameters recover within 0.00695 of truth, with R-hat <1.01 and bulk ESS >400. This validates that test, not real-data model adequacy.
- Weighted paired bootstrap AUCs match literal resampling with tied scores.
- The independent-error AUC identity passes an independent paired-DGM check (error -0.000205 in 300,000 synthetic observations) and the original 100-replicate test (mean error 0.000351; MCSE 0.000593). A score-dependent counterexample fails the identity as expected.
- Correction is never clipped; a near-zero correction factor is rejected. Every misclassification simulation run verifies that a common positive correction leaves model order unchanged.

## Completed analyses and diagnostics

- Agreement between label sources: five sources × 12 findings on a 4,349-study intersection; 2,000 joint bootstrap resamples; threshold/unknown sensitivities.
- Independent LCM: 36 four-chain fits, with one allowed extension where needed. Eleven of 12 primary fits pass chain diagnostics; synovitis does not. All 11 converged primary fits show severe response-pattern predictive misfit. Results are diagnostic, not accepted diagnostic-accuracy estimates.
- How label errors bias AUC: all four baseline scenarios completed 2,000 replicates and 399 paired bootstrap draws. All achieve bias MCSE <0.005. Output tables include estimation/interval failures, out-of-range corrections and Monte Carlo uncertainty.
- Seven figures were rendered and visually inspected. The English report was rendered with knitr from `report.qmd`; the Quarto CLI was not used. Narrative numbers agree with the frozen aggregate outputs.
- Analysis wall time, including the earlier exploratory work and post-hoc additions, is approximately 4.55 minutes; the approved cap is 120 minutes. Raw draws and labels remain external.

## Exploratory clustering and interval-method checks

- Average-linkage clustering uses the original paired kappa estimates, verified to numerical tolerance against the original agreement summaries. Median-kappa and five-source-complete-case sensitivities produce the same partition; 1,000 joint study resamples retain it. This is a descriptive stability result, not an independence test.
- Four interval methods were compared on the same 4,000 synthetic samples; 399 bootstrap draws are a prefix of 1,999. DeLong AUC, variance and normal intervals match pROC, including tied scores. Boundary AUC produces the expected pROC warning; logit intervals are explicitly undefined there.
- Aggregate outputs include failures, conditional and all-attempt coverage, paired difference MCSEs and interval widths. No real expert panel was used. All original agreement, latent-model and misclassification result files are byte-identical to the pre-review branch.
- The full R test suite passes after the additions. Both new figures were visually checked; all report tables render from the aggregate CSVs.

## Repository and source checks

At the preceding release, the repository validator passed 192 local links/anchors after the directory rename and post-hoc additions, exact aggregate-table schemas and credential/file-type checks. Nine archived notebooks (148 code cells) still pass the original token-equivalence checks, including 88 previously documented display-string exceptions; two non-Python cells remain source-identical. The new study does not change archived project code.

The five primary inputs passed ID uniqueness, column allowlist and score-range checks. Published source hashes identify the selected files. The current release scan found no primary-cohort study identifier in 57 research text artifacts. At the original analysis release, four of five primary public metadata APIs were rechecked successfully and matched pinned versions/licenses. Dread's live metadata refresh was unresolved; its public dataset page resolves, and the earlier audited v3 metadata remains the version/license evidence. These checks verify accessible source records, not every scientific claim or archive file. Existing unchanged Kaggle links retain their previous recorded checks; authenticated or generic-shell links are not described as newly verified.

I did not fit a dependence-aware latent model, validate against expert labels, analyze personal predictions, train models or run MRI inference. The source audit and model limitations remain separate from software-test success.
