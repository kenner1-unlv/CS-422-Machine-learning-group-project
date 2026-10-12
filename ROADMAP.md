# Project Roadmap

This roadmap is organized as phases that can be transferred into GitHub Issues.
The task order protects the evaluation from data leakage and premature scope
choices. Geographic scope and split years are decision gates, not assumptions.

## Phase 1 — Audit coverage and lock the evaluation plan

### Profile county-year coverage

- [ ] Summarize yield and NOAA-match counts by year, state, and county.
- [ ] Identify counties with short/intermittent histories and quantify the
  impact of candidate inclusion rules.
- [ ] Recommend and document the geographic scope and minimum coverage rule.

**Acceptance:** A coverage summary supports the chosen scope, reports the
Washabaugh exclusion, and records the number of eligible county-years by year.

### Set chronological splits and forecasting protocol

- [ ] Select contiguous train, validation, and final test year ranges using the
  coverage profile.
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

## GitHub setup note

The GitHub repository was empty when this roadmap was prepared and had no
branches or issues. The local project folder is not currently a Git repository,
so these issue-ready phases have not been published to GitHub. Create or connect
the local repository, push the specification and roadmap, then create GitHub
Issues from the phase tasks (or import them into a GitHub Project).
