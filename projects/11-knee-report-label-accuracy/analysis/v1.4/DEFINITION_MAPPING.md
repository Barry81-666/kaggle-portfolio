# Document-only definition mapping (SAP v1.4)

Frozen before calculating any newly encoded outcome. All v1.2/v1.3 findings had already been seen; this extension is exploratory. The mapping is based solely on the cached public publisher descriptions audited on 2026-10-28. Live Kaggle page reads on 2026-10-29 returned no description text, so they do not constitute a fresh content verification. Document versions, hashes, URLs and paraphrases are in [source-documents.csv](source-documents.csv).

The target is **an explicitly affirmed abnormality in the report**, including mild/trace findings. Mere mention, explicit denial, and uncertainty are not interchangeable. This is a report-assertion target, not image-confirmed disease. The documents specify source-wide rules rather than twelve separate diagnostic criteria, so the same mapping is applied to all twelve findings. Fracture, tears and effusion may still have different clinical meanings; no undocumented finding-specific interpretation is introduced.

| Source | Any explicitly affirmed abnormality | Moderate or greater | Role |
| --- | --- | --- | --- |
| Pilkwang | YES=positive; NO=negative; UNK=missing | Numeric severity cut not documented | Primary any-affirmed alignment only |
| Yunus | 0.25, 0.55, 0.90–1=positive; 0=negative; 0.05/0.50=missing | 0.55, 0.90–1=positive; 0/0.25=negative; 0.05/0.50=missing | Both documented targets |
| Steven full/v1 | 0.5 identifies unaddressed findings, but the positive threshold for this target is not documented | Not documented | Sensitivity only |
| Dread | Not documented sufficiently | Not documented sufficiently | Sensitivity only |
| Lixin | Description empty | Description empty | Sensitivity only |

The machine-readable [definition-map.csv](definition-map.csv) has one row per target, finding and source. Numeric equality uses tolerance 1e-8. Undocumented Yunus codes are missing and their counts are reported; no cutoff is inferred from outcomes. Unexpected Pilkwang verdict strings stop the run.

There are two document-alignable sources for any-affirmed and one for moderate-or-greater for each finding. **No new latent-class fit is permitted for either target.** Three binary sources would be a necessary count screen under the simple conditional-independence model, not sufficient evidence of identifiability or adequate fit; three-source models are just identified and cannot establish goodness of fit from overall response-pattern degrees of freedom.

The actual comparisons are changes in paired agreement, positive fractions, retained sample size and discordance on fixed samples. No finding is designated safe or accurate merely because sources agree. The three incompletely documented sources retain their v1.2 operational coding only in a clearly labeled five-source sensitivity/context analysis; this is not claimed to harmonize their definitions.
