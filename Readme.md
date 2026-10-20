# Early-Season County-Level Corn Yield Forecasting

## Completed coverage comparisons: Linear and Ridge

All four coverage stages have now been run using the same features, train
2000-2016, validation 2017-2020, training-only scaling, and Ridge tuning grid.
Each set selects its own Ridge alpha using its own validation rows. The
published 393-county baseline is unchanged.

**Shared 393-county test population, July forecasts with year trend:**
Every row below evaluates the same 1,965 county-years from 2021-2025.
MAE is in bushels per acre; lower is better.

| Training cohort | Training county-years | Linear MAE | Ridge MAE |
|---|---:|---:|---:|
| Primary: 393 complete counties | 6,681 | 24.75 | 24.77 |
| 90% coverage | 14,801 | 25.86 | 25.85 |
| 80% coverage | 21,087 | 27.29 | 27.40 |
| Largest available | 30,108 | 29.23 | 29.53 |

On these fixed primary test rows, broader training increased MAE at every
cutoff for both regression models and both feature variants. This observation
does not establish statistical significance or prove why performance changed.
More observations did not automatically improve these models on the primary
population. The complete-county cohort remains the preselected main experiment.

The [full comparison](results/coverage_comparison/README.md) reports all four
cutoffs and both variants on two populations:

- **Shared 393-county test rows:** holds the evaluated examples constant.
- **Each set's own test rows:** describes performance across that broader
  population; its scores are not directly comparable as evidence of a training
  improvement because the tested counties also change.

Own test counts are 1,965 (primary), 4,084 (90%), 5,517 (80%), and 6,891
(largest), each across 2021-2025. Full-precision MAE, RMSE, deltas, yearly
comparisons and prediction-file hashes are included in the comparison folder.

Individual results, predictions, scalers and fitted models:

- [90% coverage results](results/expanded_90_baselines/README.md)
- [80% coverage results](results/expanded_80_baselines/README.md)
- [Largest-available results](results/largest_available_baselines/README.md)

### Reproduce the broader runs

After generating the shared feature tables and installing modeling requirements:

```powershell
python scripts/run_baselines.py --coverage-set expanded_90
python scripts/run_baselines.py --coverage-set expanded_80
python scripts/run_baselines.py --coverage-set largest_available
python scripts/compare_coverage_baselines.py
```

See [COVERAGE_BASELINE_RUNS.md](COVERAGE_BASELINE_RUNS.md) for the protocol.
These commands preserve the primary result files. The original test period was
already inspected before these follow-up coverage runs; the comparisons are
not a fresh untouched holdout. No test outcomes are used for Ridge tuning.
Extreme-weather subgroup analysis and the other team algorithms remain pending.


## Initial Linear and Ridge results: 393 complete counties

These are the first completed model runs, using train 2000-2016, validation
2017-2020, and final test 2021-2025. Every cutoff has 1,965 test county-years.
Scaling and model fitting use training years only. Ridge alpha is selected
by validation MAE; there is no refit on validation years.

**Test MAE in bushels per acre (lower is better):**

| Forecast cutoff | Linear: weather only | Ridge: weather only | Linear: weather + trend | Ridge: weather + trend |
|---|---:|---:|---:|---:|
| May | 40.28 | 40.28 | 27.00 | 26.99 |
| June | 40.02 | 40.01 | 26.05 | 26.18 |
| July | 37.04 | 37.19 | 24.75 | 24.77 |
| August | 37.40 | 37.53 | 24.82 | 25.01 |

The training-mean reference has test MAE **42.29** and RMSE **48.02** at
every cutoff. Linear and Ridge produce very similar errors. The time-trend
variant improves these forecasts substantially, while later cutoffs do not
uniformly improve accuracy. The year trend does not establish a causal climate
effect or isolate weather from changes in farming practices. These are overall
errors; extreme-weather subgroup evaluation has not been completed.

See the [full results](results/primary_100_baselines/README.md) for validation
scores, selected Ridge alphas, test RMSE, and sample counts. The result folder
also includes annual metrics, row-level predictions, coefficients, scaling
parameters, recorded validation decisions, input hashes, and fitted pipelines.

### Reproduce the regression run

Use Python 3.12 and install the recorded modeling dependencies:

```powershell
python -m pip install -r requirements-modeling.txt
python scripts/build_study_sets.py
python scripts/build_splits.py
python scripts/build_features.py
python scripts/run_baselines.py
python -m unittest discover -s tests -v
```

The run is configured by [config/baselines.json](config/baselines.json).
See [BASELINE_RUN.md](BASELINE_RUN.md) for scaling, tuning, and output details.
The modeling dependencies are required for the full test suite; data-preparation
scripts themselves still use only the standard library.

**The final test results have now been inspected.** Keep this run as the initial
baseline. Do not tune against these scores and subsequently describe these test
years as untouched. Further experimental changes must be labeled and reported
transparently. Larger coverage-set regression runs are complete; other team algorithms are still pending.


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


CS 422 machine learning group project, Fall 2026

## Project overview

This project investigates how accurately machine learning can forecast annual
county-level corn yields (bushels per acre) before the growing season ends. We
will focus on forecasts made at multiple points during the season and ask how
prediction accuracy changes as more weather information becomes available,
particularly in unusually hot, dry, or wet seasons.

The intended users include farmers and agricultural producers, crop insurers,
agricultural researchers, and government agencies. Forecasts and uncertainty
estimates could inform planning and risk assessment; this project evaluates
predictive reliability and does not claim that weather alone causes yield
changes.

## Questions and objectives

- How does forecast error change across growing-season cutoffs, such as the end
  of May, June, July, and August?
- How well do models perform in normal seasons compared with unusually hot,
  dry, or wet seasons?
- How reliably can we estimate forecast uncertainty, including calibrated
  prediction intervals if feasible?

We will compare models using a shared target, preprocessing rules, chronological
evaluation design, and metrics. Primary metrics are mean absolute error (MAE)
and root mean squared error (RMSE).

See [PROJECT_SPEC.md](./PROJECT_SPEC.md) for the agreed project requirements
and open decisions, and [ROADMAP.md](./ROADMAP.md) for the phased implementation
plan.

## Staged coverage experiments: team data setup

Our **primary experiment uses 393 counties with complete records in every year
from 2000 through 2025**. We will also run broader coverage sets as secondary
robustness comparisons using the same model pipeline and data-quality rules.

| Stage | Required county reporting continuity | Counties | Observed county-years |
|---|---|---:|---:|
| Primary: `primary_100` | All 26 years | 393 | 10,218 |
| Secondary: `expanded_90` | At least 24 of 26 years | 883 | 22,254 |
| Secondary: `expanded_80` | At least 21 of 26 years | 1,287 | 31,207 |
| Secondary: `largest_available` | At least one usable year | 2,321 | 42,750 |

Every retained county-year has an observed yield and complete January-August
weather. The percentage measures reporting continuity across years, not
measurement reliability. Original data are preserved; missing targets are not
filled. The full 1951-2025 source period remains available for future work.

### Generate the same datasets

From the repository root, with Python 3.10 or newer:

```powershell
python scripts/audit_coverage.py
python scripts/build_study_sets.py
python scripts/build_splits.py
python scripts/build_features.py
```

These commands use only the standard library and the three processed input
tables already tracked in this repository. They do not require the raw daily
NOAA download. Outputs go to `reports/coverage/` and `data/study_sets/`.
Each study set includes `observed_yields.csv`, `counties.csv`, and
`monthly_weather.csv.gz`. The manifest checks expected counts and records source
hashes. Use canonical county FIPS as text to preserve leading zeros.

For daily heat-exposure features or a full raw-data validation, ask Russell for
a ZIP of `data/raw/noaa/averages/` and extract it so that files appear under
`data/raw/noaa/averages/<year>/` in your checkout. Russell can also share a ZIP of
the complete `data/` folder for an offline handoff. After extraction, run the
commands above to check that the study-set counts agree. Run
`python scripts/prepare_data.py` only when all raw weather files are present.
The raw archive and generated study sets are excluded from Git.

### What the extra coverage runs establish

The primary set is the core model comparison. The secondary sets test whether
results change as more counties with intermittent reporting are included.
Every model must share chronological split years, forecast cutoffs, and test
examples within each set; the shared years are fixed below.
Report each set's sample sizes and results, plus a comparison on shared held-out
county-years. A lower error on a different set alone does not establish a better
model. Fit learned preprocessing on training data only.

The initial Linear and Ridge runs on the primary cohort are complete;
secondary coverage regression runs are also complete; other team models are still planned. Larger sample size does not by itself guarantee better results.
See [STUDY_DATA_PLAN.md](STUDY_DATA_PLAN.md) for the selection rules and the
separate future experiment for predicting eligible missing-year yields.

## Data sources

- **USDA National Agricultural Statistics Service (NASS) Quick Stats**:
  historical county-level corn yields and related agricultural statistics.
  [Quick Stats](https://data.nass.usda.gov/Quick_Stats/)
- **NOAA nClimGrid-Daily**: daily temperature and precipitation data used to
  derive county-level weather features.
  [Dataset information](https://www.ncei.noaa.gov/products/land-based-station/nclimgrid-daily)

Records will be aligned by county, year, and forecast cutoff date. Candidate
features include cumulative rainfall, temperature summaries, heat exposure,
weather anomalies, and past yields. The available sources overlap from 1951
through 2025. The current primary study uses the complete-county 2000-2025
cohort below, with broader coverage sets for secondary comparisons.

## Initial data feasibility check

The sources have overlapping coverage from **1951 through 2025**. An initial
local extract is available for that full period; this establishes feasibility
but does not decide the final modeling scope.

- **USDA yield panel**: `data/processed/usda_county_corn_yield_1951_2025.csv`
  contains 151,310 county-year records across 2,821 canonical county identities
  in 41 states (2,822 distinct historical USDA county codes).
  It was filtered from the USDA Quick Stats crop bulk file dated October 10,
  2026, to survey estimates for county-level corn-grain yield in bushels per
  acre. USDA "other/combined counties" aggregates were excluded because they
  do not identify an individual county. The full 1.13 GB compressed source
  archive was removed after extraction.
- **NOAA weather source files**: `data/raw/noaa/averages/` contains 2,400
  gzip-compressed county area-average CSVs for January through August, 1951
  through 2025, for precipitation, average temperature, maximum temperature,
  and minimum temperature. The files total about 541 MB compressed. They
  retain daily values so features can be derived using only weather available
  at each forecast cutoff.
- **County crosswalk**: `data/processed/usda_noaa_county_crosswalk.csv` maps
  historical USDA county identifiers to canonical county FIPS and NOAA's
  county-area identifiers. NOAA IDs are not necessarily county FIPS, so
  records were matched by state and normalized county name. Historical USDA
  code `29193` for Ste. Genevieve County is normalized to current FIPS `29186`;
  the source code is retained for traceability. The crosswalk matched 151,288
  of 151,310 USDA county-year records (99.99%); the remaining 22 records all
  refer to South Dakota's `WASHABAUGH` entry, which has no corresponding NOAA
  county name.

## Validation and normalization

Run `python scripts/prepare_data.py` from the project root to validate the
yield panel, county crosswalk, and all downloaded NOAA files, then regenerate
the normalized files below. The script uses the Python standard library only
and fails explicitly on malformed input, duplicate county-year targets,
inconsistent NOAA monthly files, or invalid weather values.

- The yield panel is checked for valid years, county identifiers, numeric
  nonnegative yields, and duplicate canonical county-year rows. NUL bytes in
  NASS's optional CV field are converted to missing values. Zero yields are
  retained as observations.
- NOAA's daily area-average values are normalized to monthly summaries:
  precipitation totals in millimeters and mean/minimum/maximum temperatures in
  degrees Celsius. The source uses `-999.99` for non-calendar padding and may
  use missing sentinels within calendar days; sentinels become missing values,
  never numeric extremes. Zero precipitation remains valid. Monthly summary
  columns are accompanied by observed- and missing-day counts; no values are
  imputed at this stage.
- `data/processed/usda_noaa_monthly_weather_1951_2025.csv.gz` contains one row
  for each USDA county-year and month (January through August), with NOAA
  weather summaries where a county match exists. Historical source county
  codes are preserved alongside canonical county FIPS.
- `data/processed/data_quality_report.json` records the validation counts,
  value ranges, missingness, and matched/unmatched county-month counts.

The NOAA source describes its area averages as weighted aggregates and notes
that preliminary daily values are revised as additional observations arrive;
see the [nClimGrid-Daily documentation](https://www.ncei.noaa.gov/products/land-based-station/nclimgrid-daily).

Sources: [USDA Quick Stats bulk downloads](https://www.nass.usda.gov/datasets/)
and [NOAA nClimGrid-Daily documentation](https://www.ncei.noaa.gov/metadata/geoportal/rest/metadata/item/gov.noaa.ncdc:C01589/html).
The selected primary period is 2000-2025, with 393 complete counties.
Chronological split boundaries are fixed below and in `config/splits.json`.

## Evaluation approach

To simulate genuine early-season forecasting, each forecast cutoff will use
only information available by that date. We will use chronological
train/validation/test splits by year rather than randomly mixing years, and
compare the models on consistent held-out years. Preprocessing and feature
selection must be fit using training data only to avoid leakage.

We will report errors by forecast cutoff and examine results across weather
conditions. Extreme-weather cases may be uncommon, so subgroup results should
be interpreted with their sample sizes and uncertainty in mind.

## Preliminary model assignments

These assignments are preliminary and subject to team confirmation:

- **Russell Kennedy**: Linear and Ridge Regression baselines
- **Tylie Anderson**: Random Forest Regression
- **Alexander Aquiningoc**: Gradient Boosting Regression
- **Lester Iwuajoku**: Neural Network Regression

The team will jointly develop the dataset, preprocessing rules, chronological
splits, and evaluation protocol.

## Anticipated challenges and limitations

- Combining county-level sources across years may require reconciling missing
  records, geographic identifiers, and differing coverage.
- Yield also depends on factors not captured by weather data, including soil,
  management, irrigation, pests, and seed varieties.
- Extreme weather can be rare, limiting the strength of comparisons on those
  seasons.
- County-level averages can hide local variation.

We will document these limitations and avoid interpreting predictive
relationships as causal effects.

## Cutoff feature tables

The initial shared feature recipe is documented in [FEATURE_PLAN.md](FEATURE_PLAN.md).
After building study sets and splits, run `python scripts/build_features.py`.
Use the predictor allowlists in `data/features/feature_manifest.json`; targets and
county/year/split metadata must not be passed as model predictors. Weather-only
and weather-plus-time-trend variants are available for validation comparison.


### Shared feature contract

All models and coverage sets use [config/features.json](config/features.json)
and the same feature builder. January-March contributes three preseason
features; each month from April through the cutoff contributes six weather
features; April-to-cutoff contributes six cumulative features.

| Cutoff | Weather-only predictors | Weather plus year trend |
|---|---:|---:|
| May | 21 | 22 |
| June | 27 | 28 |
| July | 33 | 34 |
| August | 39 | 40 |

Start with the weather-only variant as the shared core comparison. Evaluate
weather-plus-trend as a named secondary variant consistently across models.
Use training/validation data for all feature and model choices; the final
2021-2025 test remains untouched. Report the feature variant with every score.
Only use the manifest's explicit predictor list. Do not pass target, county ID,
raw year, cutoff month, or partition metadata into a model. Train a separate
model for each cutoff. All models must use identical evaluation rows within a
coverage set and cutoff.

Temperature averages are weighted by calendar days. The tests verify future
weather cannot change earlier-cutoff features; the builder checks that shared
primary-cohort rows have identical features across the larger coverage sets.
After installing `requirements-modeling.txt`, run `python -m unittest discover -s tests -v` to check the shared pipeline.

### Preparation status and remaining work

Source validation, coverage filtering, chronological assignments, and the
initial feature tables are ready for baseline training. No missing-value
imputation is needed in this complete-weather version. Fit any scaling or
other learned preprocessing on training data only inside each model pipeline;
never standardize using the entire table before splitting. Use the same
weather feature values across algorithms, with model-appropriate scaling.

Before reporting extreme-weather reliability, define hot/dry/wet groups and
any thresholds from training information, then apply those fixed rules to
validation and test examples. That evaluation definition remains unfinished.
Daily heat-day counts, growing-degree days, and prior yields are future
feature extensions, not prerequisites for the first baseline. Linear, Ridge, and training-mean baseline training and metrics are implemented
for the primary cohort. Shared-row comparisons across broader coverage sets are complete for Linear
and Ridge; the other team models remain to implement.
