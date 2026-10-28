# Execution and release checks

Executed 2026-10-28 using R 4.5.1 and the versions pinned in `renv.lock`.

## Statistical software

- All R sources parse; the full synthetic test suite passes.
- Rank AUC agrees with pROC, including tied scores and undefined single-class cases.
- Kappa handles missing pairs and degenerate margins; majority votes exclude the source being compared and leave ties missing.
- Compressed response-pattern bootstrap statistics match directly expanded observations for paired agreement, Cohen kappa, PABAK and Fleiss kappa.
- The native latent sampler's prior predictive probabilities normalize; all draws satisfy the stated orientation. Under a correctly specified synthetic model, all parameters recover within 0.00695 of truth, with R-hat <1.01 and bulk ESS >400. This validates that test, not real-data model adequacy.
- Weighted paired bootstrap AUCs match literal resampling with tied scores.
- The independent-error AUC identity passes an independent paired-DGM check (error -0.000205 in 300,000 synthetic observations) and the original 100-replicate test (mean error 0.000351; MCSE 0.000593). A score-dependent counterexample fails the identity as expected.
- Correction is never clipped; a near-zero correction factor is rejected. Every C run verifies that a common positive correction leaves model order unchanged.

## Completed analyses and diagnostics

- B: five sources × 12 findings on a 4,349-study intersection; 2,000 joint bootstrap resamples; threshold/unknown sensitivities.
- Independent LCM: 36 four-chain fits, with one allowed extension where needed. Eleven of 12 primary fits pass chain diagnostics; synovitis does not. All 11 converged primary fits show severe response-pattern predictive misfit. Results are diagnostic, not accepted diagnostic-accuracy estimates.
- C: all four baseline scenarios completed 2,000 replicates and 399 paired bootstrap draws. All achieve bias MCSE <0.005. Output tables include estimation/interval failures, out-of-range corrections and Monte Carlo uncertainty.
- Five B/C figures were rendered and visually inspected. The English report was rendered with knitr from `report.qmd`; the Quarto CLI was not used. Narrative numbers agree with the frozen aggregate outputs.
- Analysis wall time, including the earlier A supplement, is approximately 4.22 minutes; the approved cap is 120 minutes. Raw draws and labels remain external.

## Repository and source checks

The repository validator passes 166 local links/anchors, exact aggregate-table schemas and credential/file-type checks. Nine archived notebooks (148 code cells) still pass the original token-equivalence checks, including 88 previously documented display-string exceptions; two non-Python cells remain source-identical. The new study does not change archived project code.

The five primary inputs passed ID uniqueness, column allowlist and score-range checks. Published source hashes identify the selected files. A release scan found no primary-cohort study identifier in 45 new textual artifacts. Four of five primary public metadata APIs were rechecked successfully at release and matched pinned versions/licenses. Dread's live metadata refresh was unresolved; its public dataset page resolves, and the earlier audited v3 metadata remains the version/license evidence. These checks verify accessible source records, not every scientific claim or archive file. Existing unchanged Kaggle links retain their previous recorded checks; authenticated or generic-shell links are not described as newly verified.

No empirical leaderboard analysis, dependent latent model, expert-label validation, personal prediction analysis, training or model inference was executed. The source audit and model limitations remain separate from software-test success.
