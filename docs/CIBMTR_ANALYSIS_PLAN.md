# Proposed Extension: Post-Transplant Survival Analysis

**Status: proposed, not a completed project.** No CIBMTR source, dataset or experiment record was present in this repository or the recorded 20-public-notebook inventory. An authenticated search of private work was unavailable. This is a conditional plan, not a claim that all of the account's work was searched or that an analysis was run.

The candidate is [CIBMTR — Equity in post-HCT Survival Predictions](https://www.kaggle.com/competitions/equity-post-HCT-survival-predictions). Before starting, obtain authorized data and the official data dictionary, confirm the event definition, time origin and time unit, and verify how `efs`, `efs_time` and `race_group` are encoded. Do not infer the event indicator from the variable name alone, or substitute overall survival for the specified endpoint.

## A Bounded First Analysis

1. **Define the estimand and cohort.** Document the event, right-censoring rule, follow-up window, missingness and exclusions. Assess whether the available data are synthetic, sampled or representative before interpreting any group differences clinically. Audit duplicate records and potential information leakage.
2. **Describe follow-up.** Produce Kaplan–Meier curves with uncertainty and numbers at risk, overall and for prespecified groups. Summarize censoring and group/event counts; do not interpret unadjusted curve differences causally.
3. **Fit one interpretable baseline.** Use a prespecified Cox model with a limited predictor set justified by the data dictionary. Fit imputation and encoding inside each training split. Check functional forms and proportional hazards with scaled Schoenfeld residuals; prespecify a stratified or time-varying alternative only if warranted.
4. **Evaluate held-out predictions.** Freeze a split protocol appropriate to the available patient/site/time information. Report discrimination with a censoring-aware C-index, plus calibration at prespecified horizons supported by follow-up and IPCW Brier scores. Estimate censoring weights using training information and state assumptions. Use nested tuning only if needed; keep the held-out assessment separate.
5. **Compare groups carefully.** Present event/censoring counts, uncertainty, discrimination and calibration by group, with small-sample caveats. A similar C-index across groups does not establish fairness, equal error rates or equitable clinical consequences. Distinguish descriptive disparity from causal explanations.

Use one implementation, preferably R's survival ecosystem if it fits the recovered material; use Python if it better integrates with existing verified code. The deliverable is one reproducible analysis, a data/split manifest without private records, two or three figures, a compact result table and a limitations section. Do not duplicate it merely to demonstrate a second language.

**Start condition:** accessible data and definitions, source history, and permission to publish derived summaries. Until then this page remains a plan and is excluded from completed projects.
