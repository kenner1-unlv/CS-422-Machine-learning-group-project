# Project Roadmap

## Status as of October 20, 2026

- Completed: validated sources, coverage audit, four staged datasets, fixed splits, cutoff features, Linear/Ridge and training-mean runs, shared-population comparisons, and exploratory hot/dry/wet evaluation.
- Results: [regression coverage comparison](results/coverage_comparison/README.md) and [weather groups](results/weather_groups/README.md).
- Remaining core work: Random Forest, Gradient Boosting, Neural Network, their shared-protocol comparisons and subgroup evaluation, uncertainty discussion/analysis, final figures and report.
- Optional extensions: daily heat metrics, prior-yield predictors, calibrated prediction intervals and missing-year reconstruction.
- Overall test results are already visible. Preserve the baseline and label subsequent changes transparently. No inference of statistical significance has been completed.


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
Chronological split boundaries are fixed below; the initial feature recipe is fixed in [FEATURE_PLAN.md](FEATURE_PLAN.md); Linear/Ridge results and exploratory weather-group definitions/results are complete; other team models, formal uncertainty and final reporting remain pending. Coverage experiments must report both their own evaluation populations
and comparable shared held-out county-years.


This roadmap is organized as phases that can be transferred into GitHub Issues.
The task order protects the evaluation from data leakage and premature scope
choices. Geographic scope and split years are decision gates, not assumptions.

## Phase 1 — Audit coverage and lock the evaluation plan

### Profile county-year coverage

- [x] Summarize yield and NOAA-match counts by year, state, and county.
- [x] Identify counties with short/intermittent histories and quantify the
  impact of candidate inclusion rules.
- [x] Recommend and document the geographic scope and minimum coverage rule: primary complete-county cohort plus staged secondary sets.

**Acceptance:** A coverage summary supports the chosen scope, reports the
Washabaugh exclusion, and records the number of eligible county-years by year.

### Set chronological splits and forecasting protocol

- [x] Select shared year ranges: train 2000-2016, validation 2017-2020, test 2021-2025.
- [x] Confirm that every cutoff uses only weather dated on or before that
  cutoff.
- [x] Define cutoff-specific county-year counts, equal-row MAE/RMSE, and yearly scores.

**Acceptance:** The year boundaries, cutoff definitions, sample rules, and
primary/secondary metrics are documented before test scores are generated.

## Phase 2 — Build the modeling table

### Create cutoff-specific features

- [x] Generate one row per eligible county-year-cutoff for all four coverage sets.
- [x] Define precipitation and temperature summaries for each cutoff.
- [ ] Add heat/cold or anomaly features only with documented definitions.
- [ ] Optionally build a separate weather-plus-prior-yield feature set with
  strictly lagged yield values.

**Acceptance:** Feature rows have the expected keys, no post-cutoff weather,
and documented units and missingness. Automated checks detect duplicate keys
and target leakage risks.

### Add reproducible modeling and preprocessing

- [x] Implement chronological train/validation/test selection.
- [x] Fit Linear/Ridge scaling on training data only; no imputation is needed for this feature version.
- [ ] Verify training-only preprocessing in the remaining team model pipelines.
- [x] Save feature/split configuration and baseline input hashes with results.

**Acceptance:** The process reruns deterministically and validation/test data
do not affect training transformations.

## Phase 3 — Establish baselines and compare models

### Evaluate simple baselines

- [x] Implement the training-mean baseline on every coverage set and cutoff.
- [ ] Evaluate a previous-yield baseline if prior yield is available under the
  selected split design.
- [x] Report baseline MAE, RMSE, sample counts, and cutoff.

**Acceptance:** Baselines use precisely the same test rows as the candidate
models where applicable.

### Train and compare assigned models

- [x] Linear and Ridge Regression — Russell Kennedy: all four coverage sets, both feature variants, all cutoffs.
- [ ] Random Forest Regression — Tylie Anderson.
- [ ] Gradient Boosting Regression — Alexander Aquiningoc.
- [ ] Neural Network Regression — Lester Iwuajoku.
- [x] Select Ridge alpha using validation MAE; preserve training-only fits.
- [ ] Apply the same no-test-tuning rule to the remaining team algorithms.

**Acceptance:** All feasible models are evaluated on identical test examples
for each cutoff, with model settings and random seeds recorded.

## Phase 4 — Analyze and communicate results

### Evaluate errors and weather subgroups

- [x] Report Linear/Ridge MAE and RMSE by cutoff and year, with sample counts.
- [x] Compare Linear/Ridge cutoffs and coverage sets, including shared-primary test rows.
- [ ] Integrate other model results and develop final explanations.
- [x] Define training-only county hot/dry/wet thresholds before computing subgroup errors.
- [x] Evaluate frozen Linear/Ridge predictions for every cutoff and coverage set; report sample sizes, bias, MAE/RMSE and yearly errors.
- [x] Label the analysis exploratory: overall test scores were already visible when subgroup definitions were chosen.
- [ ] Develop formal uncertainty estimates that account for correlated county/year observations; no significance claims yet.
- [ ] Evaluate the other team models using the same saved weather labels.
- [ ] Add calibrated prediction intervals only if time permits after the core
  comparison.

**Acceptance:** Tables/figures clearly distinguish test results, subgroup
results, and sample sizes; small-sample limitations are explicit.

### Finalize report and reproducibility

- [ ] Summarize data sources, scope, preprocessing, split years, and models.
- [ ] Discuss limitations, including non-weather influences and county-level
  averages.
- [x] Include commands and dependencies for the completed data and regression analyses.
- [ ] Include reproduction instructions for the remaining team algorithms and final report.
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
