# Execution details fixed locally before new outcomes

**Publication correction:** the attempted remote freeze was incomplete. See [FREEZE_DEVIATION.md](FREEZE_DEVIATION.md). Statements below about the complete published freeze describe the intended procedure and are superseded by that notice; the eight-file hash record is a local snapshot, not proof of a complete public freeze.

The published definition/scenario freeze is commit `0053954a94baec9545e6f2e0c88fe43438456d3b` (2026-10-29 05:32:34 UTC). No label file was read for this extension before that commit was published. `freeze-manifest.json` records its eight file hashes.

R's seed interface accepts signed 32-bit integers. The larger seed labels in the frozen plan are converted deterministically with `seed_label %% 2147483647`, without drawing or inspecting results. Simulation cells use `20261029042 + 10000 * finding_index + scenario_index` before that reduction; indices follow the frozen tables. The bootstrap uses `20261029041` before reduction. Synthetic software tests have a separate seed, 814.

Bootstrap samples draw study indices jointly across findings; pairwise calculations then restrict to the fixed old/new-known sample within each finding. This preserves cross-finding resampling dependence and lets its sample count fluctuate as in a cohort bootstrap. Unknown values never become negatives.

For computational efficiency AUCs against both references use the same score ranks. No per-replicate optimization or model fitting is performed. Common-subset identity is checked before using the same computed AUC for both identical reference labels. A reference-versus-oracle ranking disagreement requires non-tied orderings for both; ties and unavailable orderings are reported separately.

Primary and sensitivity cells use their fixed replicate counts. All individual-level inputs and replicate arrays are stored outside this repository. Scripts are run from this directory with `RSNA_PUBLIC_DATA` pointing to the existing allowed label files and `RSNA_V14_WORK` to a separate scratch directory. See `RUN.md` for commands and output definitions.
