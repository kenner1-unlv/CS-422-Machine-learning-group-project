# Early-Season County-Level Corn Yield Forecasting

CS 422 machine-learning group project, Fall 2026. Predict county corn yield
before the season ends, and compare reliability across forecast dates and
weather conditions. This README is the shared results hub; detailed model
methods and findings live in the linked reports.

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

## Model reports and completion status

| Contribution | Owner | Report | Current scope |
|---|---|---|---|
| Linear and Ridge Regression | Russell Kennedy | [LINEAR_REGRESSION.md](LINEAR_REGRESSION.md) | Primary + three broader coverage sets; weather-group evaluation |
| Gradient Boosting Regression | Alexander Aquiningoc | [GRADIENT_BOOSTING.md](GRADIENT_BOOSTING.md) | Primary cohort; shared variants + separate exploratory trend-residual variant |
| Random Forest Regression | Tylie Anderson | [Submission slot below](#random-forest-regression-pending) | Results pending; not included in a ranking |
| Neural Network Regression | Lester Iwuajoku | [Submission slot below](#neural-network-regression-pending) | Results pending; not included in a ranking |

## Shared comparison: Linear/Ridge versus Gradient Boosting

**Same evaluation population:** 393 complete counties, train 2000-2016
(6,681 county-years), validation 2017-2020 (1,572), test 2021-2025 (1,965 per
cutoff). Models share cutoff feature values and observed targets. Learned
preprocessing is fitted on training data only; Ridge and Gradient Boosting
settings are selected by validation MAE, with no refit on validation years.
Gradient Boosting here means Alex's validation-tuned `gbr_tuned`, not the
default model. MAE and RMSE are in bushels per acre; lower is better.

### Core comparison: weather-only test MAE

| Cutoff | Linear | Ridge | Gradient Boosting | Random Forest | Neural Network |
|---|---:|---:|---:|---|---|
| May | 40.28 | 40.28 | 37.75 | Pending | Pending |
| June | 40.02 | 40.01 | 36.31 | Pending | Pending |
| July | 37.04 | 37.19 | 33.87 | Pending | Pending |
| August | 37.40 | 37.53 | 33.69 | Pending | Pending |

### Shared secondary comparison: weather plus year-trend test MAE

| Cutoff | Linear | Ridge | Gradient Boosting | Random Forest | Neural Network |
|---|---:|---:|---:|---|---|
| May | 27.00 | 26.99 | 25.90 | Pending | Pending |
| June | 26.05 | 26.18 | 25.46 | Pending | Pending |
| July | 24.75 | 24.77 | 25.26 | Pending | Pending |
| August | 24.82 | 25.01 | 25.26 | Pending | Pending |

The training-mean reference is **42.29 MAE / 48.02 RMSE** at every cutoff.
Full validation/test MAE, RMSE, yearly and subgroup results:
[comparison report](results/gradient_boosting_comparison/README.md),
[full-precision comparison CSV](results/gradient_boosting_comparison/comparison.csv).

### What the comparison actually shows

- **Weather alone:** Gradient Boosting has lower test MAE at all four cutoffs.
  July improves from 37.04 to 33.87 (8.6% lower MAE). Trees can represent
  nonlinear thresholds and interactions that the additive baseline cannot;
  the observed gain does not isolate which mechanism caused it.
- **With the year trend:** neither method wins every cutoff. Gradient Boosting
  has lower MAE in May/June; Linear has lower MAE in July/August. July RMSE is
  **31.20 Linear versus 32.69 GB**. Even the metric matters: in June GB has
  lower MAE but higher RMSE (**32.10 versus 31.74 Linear**).
- **Trend handling matters more than the small Linear/Ridge difference.**
  Linear's July MAE drops from 37.04 to 24.75 with the year term. Linear can
  extrapolate that term; tree year splits cannot continue a trend beyond the
  training range. This does not establish a causal climate effect. A common
  trend-only comparator is still needed to isolate weather's added value.
- **Dry-group performance reverses the overall impression.** For July with
  trend, normal-group MAE is **24.37 Linear / 23.30 GB** (1,261 rows), while
  dry-group MAE is **28.16 / 36.02** (380 rows). Of those dry rows, 246 are
  from 2023. These overlapping, exploratory groups do not establish general
  drought performance or statistical significance.
- **Coverage is a separate experiment.** Broader regression training did not
  improve error on the fixed primary test rows. GB has not run those broader
  cohorts, so this is not a cross-model coverage conclusion.

### Exploratory result, outside the shared model ranking

Alex also fitted a training-only linear trend, then boosted its weather
residuals. Test MAE is **23.27 / 22.37 / 21.79 / 21.53** for May through
August. That hybrid is promising, but it changes how the trend is handled and
has not been applied consistently to the other methods. Keep it separate from
the two shared tables; do not call it the confirmed best team model.

### Evidence and limitations

For this documentation comparison, all **132 model/variant/cutoff/partition
metric groups** were recomputed from the frozen prediction CSVs: counts, MAE
and RMSE match their published metrics; there are no duplicate county-year
keys per group, and all models/variants have identical county-year keys and
observed targets within each cutoff and partition. The existing comparison
script also ran successfully, including its baseline and weather-group checks.
This checks saved-result consistency, not an independent retraining or proof
that the original run was leakage-free. No saved predictions or models changed.

Only five test years are available, and counties within a year are correlated.
No confidence intervals or significance tests establish a winner. The test
results are already visible; subsequent design changes are exploratory. The
complete-county cohort is retrospectively selected, not a national sample.
Historical input revisions, missing soil/management predictors and correlated
weather features also limit interpretation. See the method reports for details.

The original environments are recorded in each `selection.json`; GB records
scikit-learn 1.9.0 whereas the shared requirements pin 1.9.1. Do not assume a
fresh fit or loading a saved estimator under different versions is identical.
The comparison above uses saved predictions, not deserialized estimators.

## Remaining model submission slots

### Random Forest Regression (pending)

**Owner: Tylie Anderson.** Add `RANDOM_FOREST.md` following the method-report
structure used by Linear and Gradient Boosting: model rationale, features,
training/validation selection, reproduction, results and limitations. Link the
report here and fill both shared tables only once its held-out rows and metrics
have been verified. No scores are currently claimed.

### Neural Network Regression (pending)

**Owner: Lester Iwuajoku.** Add `NEURAL_NETWORK.md` with the same structure,
including training-only scaling, architecture, seed and stopping/selection
rule. Link the report here and fill both shared tables only after verification.
No scores are currently claimed.

### Common acceptance checklist for both remaining models

- [ ] Use the shared primary cohort, chronological split, feature allowlists
  and a separate model for each cutoff; label weather-only and trend variants.
- [ ] Record training-only preprocessing, validation-only model selection,
  seed, input hashes and package versions; declare any protocol deviation.
- [ ] Save row-level predictions and MAE/RMSE/counts by partition and cutoff;
  check exact county/year keys and observed targets against the baselines.
- [ ] Report yearly and shared weather-group results with sample counts.
- [ ] Keep exploratory variants separate; do not choose or tune from test
  results and call the same years an untouched holdout.
- [ ] Add the method report, reproducible commands and verified summary scores
  to this README. Formal uncertainty analysis and final synthesis remain open.

## Reproducing the completed contributions

Shared data preparation and feature details follow below. Model-specific
commands and environments are in [LINEAR_REGRESSION.md](LINEAR_REGRESSION.md)
and [GRADIENT_BOOSTING.md](GRADIENT_BOOSTING.md). To compare existing frozen
predictions without retraining, run `python scripts/compare_gradient_boosting.py`
with its dependencies installed. It regenerates comparison tables/figures;
use a clean scratch checkout if you want to preserve published artifacts.

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
secondary coverage regression runs are also complete. Gradient Boosting is complete on the primary cohort; Random Forest and Neural Network results are pending. Larger sample size does not by itself guarantee better results.
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
Use training/validation data for all feature and model choices; 2021-2025 was the designated final test. Its results have now been inspected;
further changes must be reported as follow-up experiments, not a fresh holdout. Report the feature variant with every score.
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
validation and test examples. The initial exploratory definitions and results are now recorded in `config/weather_groups.json` and `results/weather_groups/`; formal uncertainty remains unfinished.
Daily heat-day counts, growing-degree days, and prior yields are future
feature extensions, not prerequisites for the first baseline. Linear, Ridge, and training-mean baseline training and metrics are implemented
for the primary cohort. Shared-row comparisons across broader coverage sets are complete for Linear
and Ridge. Gradient Boosting is implemented on the primary cohort;
Random Forest and Neural Network comparisons remain pending.
