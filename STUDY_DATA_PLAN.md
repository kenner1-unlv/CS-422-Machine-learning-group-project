# Study datasets: 2000-2025

## Shared chronological split

The same harvest-year boundaries apply to all four coverage sets and all models:

| Partition | Years (inclusive) | Purpose | Primary county-years |
|---|---|---|---:|
| Training | 2000-2016 | Fit models and learned preprocessing | 6,681 |
| Validation | 2017-2020 | Select features, models, and hyperparameters | 1,572 |
| Final test | 2021-2025 | Final evaluation after choices are frozen | 1,965 |

`config/splits.json` is the authoritative split configuration. After building
study sets, run `python scripts/build_splits.py`. It writes
`split_assignments.csv` inside each study-set folder and a shared
`data/study_sets/split_summary.json`. Join assignments onto features by county
FIPS and harvest year, preserving FIPS as text. Every forecast cutoff for the
same county-year inherits the same partition. Never randomly split rows or
hold out every fifth year for the forecasting experiment.

These 17/4/5 year blocks simulate predicting later seasons from earlier data
and test performance under temporal changes. No model scores informed this
choice. The initial comparison fits models and preprocessing on 2000-2016,
selects settings on 2017-2020, then freezes that fitted pipeline for the final
2021-2025 test. Do not refit on validation or test years for this protocol.
Any later expanding-window or train-plus-validation refit experiment must be
declared separately and applied consistently to every model and coverage set.

Use only weather through each May/June/July/August cutoff. Report test MAE and
RMSE both overall and by harvest year, with sample counts. Compare broader
sets on both their own test rows and the primary cohort's shared test rows.
Fit anomaly thresholds and other learned transformations on training years
only. Missing-year reconstruction remains a separate future experiment.


The primary experiment uses the 393 counties with complete observed yield and January-August weather in every year from 2000 through 2025. All original datasets remain unchanged.

| Set | Minimum reporting continuity | Counties | Observed county-years |
|---|---|---:|---:|
| primary_100 | 26 of 26 years | 393 | 10,218 |
| expanded_90 | At least 24 of 26 years | 883 | 22,254 |
| expanded_80 | At least 21 of 26 years | 1,287 | 31,207 |
| largest_available | At least one usable year | 2,321 | 42,750 |

The sets are nested. Continuity is the only rule that changes. Every retained county-year must have an observed finite nonnegative USDA yield, a county match, and complete January-August weather for precipitation and mean/maximum/minimum temperature. Valid zeros are retained. No missing records are filled. These sets use CSV and compressed CSV files rather than requiring a database server.

Run `python scripts/build_study_sets.py` to regenerate `data/study_sets/`. Each set has an observed-yield table, county membership table, and monthly weather table. The manifest records rules, per-year counts, and source hashes. The script checks expected counts, nesting, weather-row counts, and unchanged source files.

## Evaluation

All algorithms must share the same chronological split years, forecast cutoffs, and evaluated examples within each set. Split boundaries are fixed in `config/splits.json`. Cutoff-specific features must omit later weather; preprocessing is fitted only on training data. The monthly tables are inputs for feature generation, not model-ready cutoff tables.

Use the primary set for the core comparison. Broader sets are additional experiments under the same data-quality rules. Their scores are not directly equivalent because they include different counties. Also compare models on their shared held-out county-years to distinguish changes in training coverage from changes in test population. Define both views before looking at test scores. Reusing four forecast cutoffs does not create four independent annual targets.

The complete-county selection uses reporting availability across the study period and therefore describes a retrospective cohort. It may favor consistently reporting counties; do not claim this cohort represents every US corn county or real-time eligibility.

## Missing-year prediction: separate future experiment

`missing_year_prediction_candidates.csv` lists years with no target in our retained USDA extract, among counties with at least one usable record during 2000-2025. It does not establish why a record is absent: it could reflect nonproduction, reporting changes, suppression, or extraction coverage. Check those reasons and corn production eligibility before making predictions. The inventory does not include every geographic county or years outside 2000-2025.

The daily NOAA sources cover the period, but weather for these absent-target years must still be extracted and checked before inference; the current monthly panel contains only years with retained yield targets.

Later, models can estimate eligible missing yields using available weather and strictly prior yield history. Save estimates separately with their model, feature cutoff, uncertainty where feasible, and `label_origin=predicted`. Never replace the observed target table or score a model against its own estimates. Do not feed estimates into later lagged-yield features in the main experiment.

Evaluate that extension by hiding known targets under a declared chronological protocol and comparing predictions with the withheld observations. Artificial masking cannot prove accuracy for genuinely unreported years, whose reasons for absence may differ. Predicting an old gap using later years is retrospective reconstruction; it must be labeled separately from early-season forecasting using only information available at that date.

Washabaugh's 22 unmatched historical records remain in source data and are excluded from weather-model sets. They precede this 2000-2025 study window.
