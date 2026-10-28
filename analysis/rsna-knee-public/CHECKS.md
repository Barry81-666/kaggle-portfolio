# Foundation checks

Executed 2026-10-28 with R 4.5.1 and the foundation versions in renv.lock.

- All new R sources parse.
- Rank AUC agrees with pROC on synthetic tied scores; undefined single-class AUC is retained as missing.
- Kappa handles perfect/opposite agreement, missing pairs and degenerate margins.
- Leave-one-source-out majority votes handle ties without treating a source as its own reference.
- Public top-n strata retain boundary ties; Deming recovers a known synthetic line.
- Corrected AUC is not silently clipped; a near-zero mixture factor is rejected.
- The conditionally independent mixture identity passed 100 synthetic replicates (10,000 observations each). Monte Carlo mean error: 0.000351; Monte Carlo SE: 0.000593. These numbers assess software against a known answer, not any participant or dataset.
- A score-dependent-error synthetic case does not satisfy the independence identity.
- Schema validation rejects report-text columns. Nine selected label-table schemas passed the final allowlist check; counts/columns only were inspected.

The DuckDB full-table scan, empirical inference, Bayesian fitting and Quarto rendering have not run. No SAP approval or study result is implied by these tests. See the PR for repository link and publication-scan checks.
