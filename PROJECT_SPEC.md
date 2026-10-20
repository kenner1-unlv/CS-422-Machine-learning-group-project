# Project Specification: Early-Season County-Level Corn Yield Forecasting

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
Chronological split boundaries are fixed below; feature definitions and model results remain pending. Coverage experiments must report both their own evaluation populations
and comparable shared held-out county-years.


## 1. Purpose

Build and evaluate reproducible machine-learning models that estimate annual
county-level corn-grain yield from weather information available before the
growing season is over. The project will test whether forecasts improve as more
in-season weather becomes available and how performance varies across
conditions.

This is a historical forecasting study, not a causal analysis or a deployed
agricultural decision system. Weather is only one influence on yield; results
must be presented with that limitation.

## 2. Research questions

1. How accurately can county corn yield be forecast by the end of May, June,
   July, and August?
2. Does forecast error change as each later cutoff provides more weather data?
3. How do models compare on the same held-out county-years and cutoffs?
4. How does performance vary in unusually hot, dry, or wet conditions, when
   sample size permits a meaningful comparison?

Prediction intervals or other uncertainty estimates are a stretch goal, not a
requirement for the core comparison.

## 3. Data and prediction unit

- **Target:** USDA NASS county-level corn-grain yield, in bushels per acre, for
  a harvest year.
- **Weather source:** NOAA nClimGrid-Daily county area averages for
  precipitation and average, maximum, and minimum temperature.
- **Study period available:** 1951–2025.
- **Prediction unit:** one county, harvest year, and forecast cutoff. Each
  county-year with usable data can therefore contribute up to four forecast
  examples.
- **Forecast cutoffs:** end of May, June, July, and August. Features for a
  cutoff may use only observations through that month. The dataset contains
  January–August weather; feature selection will decide which earlier months
  are relevant, without allowing post-cutoff weather into that forecast.
- **Geographic scope:** not fixed in advance. First profile usable county-year
  coverage by county, state, and year; then record and justify the scope used
  for modeling. Do not silently treat unmatched or absent observations as
  zero.

The current alignment audit found 151,288 of 151,310 USDA county-year records
matched to a NOAA location (99.99%). The 22 unmatched records are all for
Washabaugh, South Dakota. The prepared monthly panel has 1,210,480 rows, with
1,210,304 county-months matched. These are join-coverage results, not evidence
of predictive accuracy.

## 4. Data preparation and feature rules

1. Rebuild the validated yield and monthly weather tables using
   `scripts/prepare_data.py`; preserve the QC report with each data refresh.
2. Keep canonical county FIPS for joins and retain original USDA county IDs
   for traceability, including the Ste. Genevieve historical alias.
3. Use physical units: precipitation in millimeters, temperature in degrees
   Celsius, and yield in bushels per acre.
4. Derive cutoff-specific features from daily NOAA data or validated monthly
   summaries. Candidate features include cumulative precipitation, mean and
   extreme temperature summaries, and heat/cold exposure measures. Document
   definitions and ensure no feature uses weather after its cutoff.
5. Keep valid zero precipitation and zero yield values. Treat documented
   sentinels as missing, not as measurements. Do not impute during source
   normalization.
6. The 22 unmatched USDA county-years cannot have weather-only predictions
   under this source pairing. Report their exclusion from weather-model
   results; do not fabricate weather values.
7. Any imputation, scaling, feature selection, anomaly thresholds, or other
   learned preprocessing must be fitted on training data only and applied to
   validation/test data without refitting.
8. Historical yield may be considered as a predictor only when it is strictly
   from years before the prediction year and is available under the chosen
   evaluation design. Compare weather-only and weather-plus-history features
   separately if used.

## 5. Modeling and evaluation

- Compare against at least one simple, clearly defined baseline before
  interpreting machine-learning scores. Candidate baselines include a
  training-set mean and a previous-yield baseline where prior yield is
  available.
- Evaluate linear and Ridge Regression, Random Forest Regression, Gradient
  Boosting Regression, and Neural Network Regression, subject to implementation
  feasibility and the course schedule. Every model must use the same target,
  data scope, cutoffs, and held-out examples for a fair comparison.
- Split by **harvest year chronologically**, never by randomly assigning
  county-year rows. Decide the train/validation/test year boundaries only after
  profiling coverage; document the boundaries before comparing test results.
- Use validation data for model and hyperparameter choices. Keep the final
  test period untouched until the comparison is finalized.
- **Primary metric:** MAE in bushels per acre. **Secondary metric:** RMSE in
  bushels per acre. Report sample counts and coverage alongside every score.
- Report results separately for each cutoff, and include an aggregate only if
  its weighting across counties/years is explicit.
- Examine hot, dry, and wet subgroups only with a predeclared, reproducible
  definition and their sample counts. Do not overstate conclusions for small
  groups.
- Compare optional prediction intervals only after the core point-forecast
  evaluation is complete; report coverage and interval width if implemented.

## 6. Deliverables

1. Reproducible source-data validation and feature-generation steps.
2. A documented coverage and missingness analysis that justifies the final
   geographic scope and temporal splits.
3. A leakage-safe evaluation pipeline and a simple baseline.
4. Comparable results for the selected models at each cutoff, with MAE, RMSE,
   sample counts, and subgroup results where supported.
5. A concise final report describing methods, results, limitations, and
   recommendations for future work.

## 7. Completion criteria

The core project is complete when:

- the feature-generation process can be rerun from the available source files;
- each cutoff has a documented, leakage-checked feature set;
- the chosen geographic scope and chronological splits are justified by
  coverage analysis and held fixed for model comparison;
- all required model results are evaluated on the same test examples against a
  baseline;
- missingness, exclusions, sample sizes, and metric units are reported; and
- conclusions distinguish data alignment from actual predictive performance
  and avoid causal claims.

## 8. Decisions to resolve during the roadmap

- Geographic scope and any minimum county/year coverage rule.
- Exact train, validation, and final test year boundaries.
- Final feature definitions and whether historical yield is included.
- Reproducible definitions for unusual weather.
- Whether uncertainty estimates fit the time and course requirements.

Resolve these from the coverage audit and course constraints, record the
decisions in the README or final report, and avoid changing them after test
performance is examined.
