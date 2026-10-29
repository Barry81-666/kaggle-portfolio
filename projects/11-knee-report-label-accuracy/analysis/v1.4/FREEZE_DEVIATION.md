# Publication deviation: incomplete remote freeze

**The full SAP v1.4 was not successfully published before the new outcomes were computed.** The earlier statement that all eight files had been publicly frozen was incorrect. This deviation limits the public evidence for prospective specification and must accompany the exploratory results.

## What happened and what can be verified

1. The complete eight-file plan and mapping were prepared locally before label loading. The local byte hashes in `freeze-manifest.json` were checked before alignment and simulation. Planned rules have not been changed in response to outcomes.
2. The intended publication at commit `0053954a94baec9545e6f2e0c88fe43438456d3b`, 2026-10-29 05:32:34 UTC, was incomplete. A large shell-output transfer was truncated inside a JSON content string. The remaining JSON was still parseable and was mistakenly accepted. Its SAP.md blob contains a literal truncation marker and joins part of the old SAP to part of the definition-map CSV. The readable mapping, full SAP v1.4, readable scenario table and standalone definition-map file were absent.
3. The scenario CSV and source-document CSV were published with their intended textual contents (line endings normalized). DECISIONS.md states that two sources qualify for any-affirmed, one for moderate-or-greater, and no new latent model is planned. The malformed SAP blob contains 113 of the intended 120 mapping rows. It does **not** provide a complete, intact freeze of the new protocol or map. The full simulation generator was not publicly frozen there.
4. Alignment started at 05:36:31 UTC and simulation at 05:37:57 UTC. Only local hashes had been verified at that stage. The remote mismatch was found in the final recursive Git-tree comparison after the results commit and draft PR were created.
5. The repair restores SAP.md to its intended original text plus extension link, adds missing planned files unchanged, restores exact CSV bytes, and corrects review/PR claims. It preserves the defective commit and all subsequent history. It is a **post-result publication repair**, not a new pre-outcome freeze. Rerunning the same data after repair would not recover prospective status, so results are not relabeled on that basis.

## Interpretation and checks

The mapping and scenarios were followed as prepared locally. Original code/results/pages are preserved in the repaired final tree. A reader cannot use the initial commit as proof that the entire protocol was publicly fixed before analysis. Review this as an exploratory extension with a documented protocol-publication deviation.

`alignment-run.json`'s `all_frozen_hashes_pass` and the original run's freeze-commit fields refer to the **local intended snapshot and attempted publication**, not successful full remote verification. The current validation distinguishes these scopes. Planned files' original wording is retained as a record of intent; this deviation notice governs their actual publication status.

Subsequent upload transfers are bounded below truncation limits, reject truncation markers, and are compared against local Git blob hashes. Remote verification must occur before claiming publication completeness. No outcomes or encoding rules are changed to conceal the failure.
