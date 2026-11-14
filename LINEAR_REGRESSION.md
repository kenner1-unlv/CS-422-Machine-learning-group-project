# Linear and Ridge Regression: primary 393 counties

Russell Kennedy's baseline contribution to the shared corn-yield forecasting
comparison. This report collects the regression findings previously embedded
in the project README; no models, predictions or frozen results were changed.
For the team comparison and pending models, see [Readme.md](Readme.md).
Alex's corresponding method report is [GRADIENT_BOOSTING.md](GRADIENT_BOOSTING.md).

## Why Linear and Ridge fit this problem

Linear Regression is an interpretable additive baseline: each weather predictor
contributes a fitted slope, and their contributions are added to an intercept.
It cannot learn thresholds or interactions unless those features are supplied.
Ridge uses the same form with an L2 penalty to reduce sensitivity to correlated
predictors. The monthly and cumulative features overlap, so individual
coefficients should not be interpreted as stable causal weather effects.

## How it works and how settings are selected

1. Build the shared forecast-cutoff feature allowlists in
   [FEATURE_PLAN.md](FEATURE_PLAN.md): 21/27/33/39 weather features for
   May/June/July/August, plus one year-trend feature in the named secondary variant.
2. Fit a separate `StandardScaler` and regression pipeline on 2000-2016 only
   (6,681 primary county-years). Fit Linear by least squares; fit Ridge with
   the configured penalty grid.
3. Select Ridge alpha using 2017-2020 validation MAE (1,572 rows), breaking
   ties by RMSE then smaller alpha. Grid:
   `0.001, 0.01, 0.1, 1, 10, 100, 1000, 10000, 100000`.
   Do not refit on validation years.
4. Save selection decisions, then evaluate the frozen models on 2021-2025
   (1,965 rows per cutoff). The training-mean predictor is the simple reference.

The target stays in bushels per acre; there is no target standardization,
imputation or prediction clipping. County ID, raw year, partition and target
are excluded from predictors. Only `weather_plus_trend` includes
`year_since_2000`. Training-only scaling and model selection are documented in
[BASELINE_RUN.md](BASELINE_RUN.md) and [config/baselines.json](config/baselines.json).

Unlike a tree's year splits, a fitted linear year term can extrapolate beyond
the training years. That is an assumption about continuation of a trend, not
proof of its cause or future stability.

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
errors; exploratory weather-group results are now reported below.

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
transparently. Larger coverage-set regression runs are complete; Gradient Boosting is reported separately; Random Forest and Neural Network remain pending.


## What we have learned so far

These are preliminary findings from Linear and Ridge Regression, evaluated on
2021-2025 after training on 2000-2016 and tuning on 2017-2020. They describe
forecasting performance under our current feature recipe, not causes of yield
changes. All errors below are MAE in bushels per acre unless stated otherwise.

1. **The time-trend feature materially improved the initial forecasts.** For
   July on the primary 393 counties, Linear Regression improved from
   **37.04 to 24.75**, a **33.2% reduction in MAE**. Weather alone
   misses important changes over time in this experiment. Year is a proxy for
   multiple possible influences, including agricultural practices and changing
   conditions; this does not attribute the improvement to climate. A trend-only
   comparator has not been run, so we cannot isolate weather's incremental
   predictive contribution beyond the time trend from this comparison alone.

2. **More training counties did not improve these regressions on the primary
   population.** On the same 1,965 held-out county-years, July Linear Regression
   with the trend had MAE **24.75** using primary-cohort training versus
   **29.23** using the largest training set. The broader runs had higher
   shared-population MAE at every cutoff for both algorithms and both feature
   variants. This supports retaining the preselected primary experiment; it
   does not prove that missing reporting years caused the difference. Broader
   sets change geographic and yield distributions as well as sample size.

3. **Dry conditions exposed a forecasting weakness.** The primary July Linear
   model with trend had MAE **28.16** in the dry group (380 county-years)
   versus **24.37** in the normal group (1261 county-years), about
   **15.6% higher error**. Dry-group MAE exceeded normal-group MAE at
   every cutoff for both primary trend models. Hot and wet groups did not
   consistently have higher errors. The combined extreme group was slightly
   easier than normal in May and harder in June-August, so the findings do not
   support saying every unusual-weather group is harder to predict.

4. **Later forecasts helped up to a point.** Primary Linear Regression with
   trend improved from **27.00 in May** to **24.75 in July**,
   then had **24.82 in August**. More late-season weather did not guarantee
   lower error. These are separately fitted cutoff models with different
   feature counts, not an isolated causal test of adding one month's weather.

5. **Ridge added little over ordinary Linear Regression for this recipe.**
   July primary trend-model MAE was **24.75 for Linear** and
   **24.77 for Ridge**. Similar results across the cutoffs suggest
   regularization alone did not substantially improve prediction here; this
   is not evidence that the algorithms are generally equivalent.

**Interpretation:** These baselines capture useful patterns relative to the
training-mean reference, but their predictions retain substantial errors,
especially in dry groups. MAE is an average absolute forecasting error, not
crop loss or an accuracy percentage. A lower test MAE on a broader set's own
counties is not directly comparable with a score on the primary population.

### Limits on these findings

- **Only five test years:** counties share weather and other influences within
  years. Thousands of county-years are not thousands of independent weather
  events. We have not established statistical significance or formal confidence
  intervals; small numerical differences should not be treated as decisive.
- **Exploratory weather subgroups:** definitions were fixed before subgroup
  errors were computed, but after overall test scores were inspected. They
  are statistical flags rather than official drought, flood or heat-wave
  declarations. Thresholds use only 10-17 available training years, and groups
  can overlap and change across forecast cutoffs. Their differences can reflect
  county/year composition, not only weather severity. Insufficient-history
  records are unclassified rather than silently treated as normal.
- **Selected population:** the 393 complete counties are a retrospective
  reporting-continuity cohort, not a representative sample of every US corn
  county. They were selected using coverage across the full study period;
  results should not be presented as real-time county eligibility or national
  production forecasts. Actual county production errors require acreage data.
- **Limited predictors:** no soil, management, irrigation, pests or seed
  information is modeled. The first recipe uses monthly summaries and a common
  April start, not local planting calendars or daily heat/drought-duration
  measures. County averages hide within-county variation. Monthly/cumulative
  predictors overlap, so individual regression coefficients may be unstable.
- **Retrospective inputs and exposed test results:** historical weather may
  have been revised after the forecast dates. Restricting dates prevents
  post-cutoff observations entering features, but does not establish real-time
  data availability. Test outcomes are now visible; subsequent changes must be
  described transparently, rather than treated as another untouched test.
- **Scope of completed work:** these findings concern Linear and Ridge under
  the current protocol. Random
  Forest and Neural Network comparisons, formal uncertainty analysis, and the
  final synthesis remain unfinished. No causal or statistical-significance claims are established.

Supporting results: [primary regressions](results/primary_100_baselines/README.md),
[coverage comparisons](results/coverage_comparison/README.md), and
[weather groups](results/weather_groups/README.md). The linked folders contain
full-precision metrics, sample counts, yearly results and reproduction details.


## Hot, dry and wet conditions: regression results

Weather-group evaluation is complete for Linear and Ridge across all four
coverage sets and May/June/July/August cutoffs. Thresholds use only training
weather (2000-2016), fitted once per county and cutoff from the largest set
and applied consistently across the coverage stages:

- **Hot:** April-to-cutoff mean daily maximum temperature above the county
  training 90th percentile.
- **Dry:** April-to-cutoff rainfall below the county training 10th percentile.
- **Wet:** April-to-cutoff rainfall above the county training 90th percentile.
- **Normal:** none of those flags. Hot can overlap dry or wet.
- **Unclassified:** fewer than 10 available training years; kept separate.

These are statistical weather flags, not official drought/flood/heat-wave
classifications. Membership changes with the cutoff. The original models and
predictions were not modified or retrained.

**July, primary 393-county test set, weather plus year trend:**
MAE is in bushels per acre. Groups overlap, so their counts are not additive.

| Group | County-years | Linear MAE | Ridge MAE |
|---|---:|---:|---:|
| normal | 1261 | 24.37 | 24.41 |
| extreme_any | 704 | 25.42 | 25.42 |
| hot | 158 | 23.08 | 23.11 |
| dry | 380 | 28.16 | 28.25 |
| wet | 231 | 22.85 | 22.70 |
| hot_dry | 53 | 26.24 | 26.37 |

For the primary models with year trend, dry-group MAE exceeds normal-group
MAE at every cutoff. The combined extreme group is not uniformly harder:
its MAE is slightly lower than normal in May and higher in June-August.
Hot and wet groups do not consistently have larger errors. These are
descriptive differences; county/year composition and yield distributions
differ across groups. No significance or causal conclusions are claimed.

The [full weather-group report](results/weather_groups/README.md) includes
primary and expanded sets, shared-393 and own-population comparisons,
weather-only and trend variants, the mean baseline, validation/test scores,
yearly MAE/RMSE, bias, thresholds, labels and sample counts. The largest set
has 402 unclassified test county-years; these remain in overall scores.

**Exploratory follow-up:** group definitions were fixed before subgroup
errors were computed, but after the overall test results had been inspected.
They are not a predeclared confirmation on an untouched test set. Thresholds
are estimated from only 10-17 available training years, with no minimum
consecutive-year requirement. Missing reporting years can affect the reference.
Small groups (fewer than 30 records or three represented years) are flagged.
County-years are not independent weather events; formal uncertainty estimates
and the remaining team models remain unfinished.

### Reproduce weather-group evaluation

After generating features and all four baseline runs, run:

```powershell
python scripts/evaluate_weather_groups.py
```

Definitions are recorded in [config/weather_groups.json](config/weather_groups.json).
Outputs are saved in `results/weather_groups/`. Tests check that held-out
weather cannot affect fitted thresholds, compound labels are correct, and
insufficient-history cases are not classified as normal. The evaluator checks
population accounting, shared-label consistency and agreement with baseline
overall metrics.


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
Exploratory weather-group analysis is complete for these regressions; formal uncertainty analysis and Random Forest and Neural Network remain pending.


