# Project Roadmap

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


## Selected data scope (October 20, 2026)

The primary cohort is the 393 counties with complete observed yield and
January-August weather for every year in 2000-2025 (10,218 county-years).
Secondary experiments use the nested 90%, 80%, and largest-available sets under
the same per-record completeness rules. See [STUDY_DATA_PLAN.md](STUDY_DATA_PLAN.md)
and the README for counts and reproduction commands. This decision supersedes
references below to geographic scope and modeling period being undecided.
Chronological split boundaries are fixed below; the initial feature recipe is fixed in [FEATURE_PLAN.md](FEATURE_PLAN.md); model results and extreme-weather subgroup definitions remain pending. Coverage experiments must report both their own evaluation populations
and comparable shared held-out county-years.


This roadmap is organized as phases that can be transferred into GitHub Issues.
The task order protects the evaluation from data leakage and premature scope
choices. Geographic scope and split years are decision gates, not assumptions.

## Phase 1 — Audit coverage and lock the evaluation plan

### Profile county-year coverage

- [ ] Summarize yield and NOAA-match counts by year, state, and county.
- [ ] Identify counties with short/intermittent histories and quantify the
  impact of candidate inclusion rules.
- [x] Recommend and document the geographic scope and minimum coverage rule: primary complete-county cohort plus staged secondary sets.

**Acceptance:** A coverage summary supports the chosen scope, reports the
Washabaugh exclusion, and records the number of eligible county-years by year.

### Set chronological splits and forecasting protocol

- [x] Select shared year ranges: train 2000-2016, validation 2017-2020, test 2021-2025.
- [ ] Confirm that every cutoff uses only weather available on or before that
  cutoff.
- [ ] Define how each cutoff's examples and aggregate scores will be counted.

**Acceptance:** The year boundaries, cutoff definitions, sample rules, and
primary/secondary metrics are documented before test scores are generated.

## Phase 2 — Build the modeling table

### Create cutoff-specific features

- [ ] Generate one row per eligible county-year-cutoff.
- [ ] Define precipitation and temperature summaries for each cutoff.
- [ ] Add heat/cold or anomaly features only with documented definitions.
- [ ] Optionally build a separate weather-plus-prior-yield feature set with
  strictly lagged yield values.

**Acceptance:** Feature rows have the expected keys, no post-cutoff weather,
and documented units and missingness. Automated checks detect duplicate keys
and target leakage risks.

### Add reproducible modeling and preprocessing

- [ ] Implement chronological train/validation/test selection.
- [ ] Fit imputation, scaling, feature selection, and other learned
  preprocessing on training data only.
- [ ] Save the feature-generation and split configuration with results.

**Acceptance:** The process reruns deterministically and validation/test data
do not affect training transformations.

## Phase 3 — Establish baselines and compare models

### Evaluate simple baselines

- [ ] Implement the training-mean baseline.
- [ ] Evaluate a previous-yield baseline if prior yield is available under the
  selected split design.
- [ ] Report baseline MAE, RMSE, sample counts, and cutoff.

**Acceptance:** Baselines use precisely the same test rows as the candidate
models where applicable.

### Train and compare assigned models

- [ ] Linear and Ridge Regression — Russell Kennedy.
- [ ] Random Forest Regression — Tylie Anderson.
- [ ] Gradient Boosting Regression — Alexander Aquiningoc.
- [ ] Neural Network Regression — Lester Iwuajoku.
- [ ] Tune only against training/validation data, not the final test set.

**Acceptance:** All feasible models are evaluated on identical test examples
for each cutoff, with model settings and random seeds recorded.

## Phase 4 — Analyze and communicate results

### Evaluate errors and weather subgroups

- [ ] Report MAE and RMSE by cutoff, with sample counts.
- [ ] Compare cutoff performance and explain any changes.
- [ ] Define unusual hot, dry, or wet conditions before subgroup comparison;
  report subgroup sizes and uncertainty.
- [ ] Add calibrated prediction intervals only if time permits after the core
  comparison.

**Acceptance:** Tables/figures clearly distinguish test results, subgroup
results, and sample sizes; small-sample limitations are explicit.

### Finalize report and reproducibility

- [ ] Summarize data sources, scope, preprocessing, split years, and models.
- [ ] Discuss limitations, including non-weather influences and county-level
  averages.
- [ ] Include commands and dependencies needed to reproduce the analysis.
- [ ] Confirm README and final report agree with the executed pipeline.

**Acceptance:** Another team member can follow the documented steps and
reproduce the reported test metrics.

## Suggested GitHub labels

- `data`
- `features`
- `modeling`
- `evaluation`
- `documentation`
- `decision`

## GitHub tracking

The project specification and roadmap are published on the `main` branch.
Work is tracked in [GitHub Issues](https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/issues)
and grouped by these milestones:

- [Phase 1 — Coverage and evaluation plan](https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/milestone/1)
- [Phase 2 — Modeling table and pipeline](https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/milestone/2)
- [Phase 3 — Baselines and model comparison](https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/milestone/3)
- [Phase 4 — Analysis and final report](https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/milestone/4)
