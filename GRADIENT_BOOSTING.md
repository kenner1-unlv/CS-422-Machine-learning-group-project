# Gradient Boosting Regression: primary 393 counties

Gradient Boosting contribution to the shared corn-yield forecasting comparison.
It uses the same data, features, chronological split, cutoffs and test rows as
the Linear/Ridge baselines in [BASELINE_RUN.md](BASELINE_RUN.md), so the scores
can be compared directly.

## Why Gradient Boosting fits this problem

- **Non-linear weather effects.** Yield does not respond to weather in a
  straight line: some rain helps, a lot of rain or none at all hurts, and heat
  matters more once it passes a threshold. Linear Regression can only fit one
  slope per feature. Trees can learn thresholds and curves directly.
- **Interactions.** Heat is worse when it is also dry. A tree split on
  temperature followed by a split on rainfall captures that without us having
  to build a `heat x dry` feature by hand.
- **Overlapping features.** The recipe has monthly and season-to-date versions
  of the same weather. That makes linear coefficients unstable. Trees just pick
  whichever version splits best, so overlap mainly affects interpretation, not
  fitting.
- **No scaling needed.** Trees split on thresholds, so feature units don't
  matter. There is no learned preprocessing that could leak validation or test
  information.

## How it works (conceptually)

1. Start with a constant prediction: the training mean yield.
2. Compute each training row's residual (observed minus current prediction).
3. Fit a small regression tree (depth 2-4) to those residuals.
4. Add that tree's prediction, scaled down by the learning rate (0.05-0.1),
   to the running prediction.
5. Repeat for `n_estimators` rounds. Each tree corrects what the previous
   trees got wrong.

The learning rate and number of trees trade off: smaller steps need more trees
but usually generalise better. `subsample < 1` fits each tree on a random
fraction of the rows (stochastic gradient boosting), which adds randomness and
reduces overfitting. `min_samples_leaf` stops a tree from carving out tiny
groups of county-years. Too many trees overfit the training years, which is
why the tree count is chosen on validation years.

## Features

Exactly the shared manifest allowlists from [FEATURE_PLAN.md](FEATURE_PLAN.md),
one model per cutoff:

| Cutoff | Weather-only | Weather + trend |
|---|---:|---:|
| End of May | 21 | 22 |
| End of June | 27 | 28 |
| End of July | 33 | 34 |
| End of August | 39 | 40 |

- January-March preseason precipitation, mean temperature and coldest day.
- Each month April through the cutoff: precipitation and mean/max/min
  temperature, hottest and coldest day (six values per month).
- April-to-cutoff season totals and averages (six values).
- `year_since_2000` in the trend variant only.

No weather after the cutoff, no county ID, no raw year (outside the trend
column), and no target-derived features. Historical yields, heat-day counts and
growing-degree days are **not** included: they are not part of the shared
recipe (lagged yields need a separately defined leakage-safe variant, and
heat-day counts need the raw daily NOAA files).

### Three variants

| Variant | Status | Predictors |
|---|---|---|
| `weather_only` | Shared core comparison | weather allowlist |
| `weather_plus_trend` | Shared secondary variant | weather + `year_since_2000` |
| `trend_residual` | **Exploratory, Gradient Boosting only** | same as weather + trend |

**Why `trend_residual` exists.** Trees cannot extrapolate. Training years are
`year_since_2000` = 0-16, validation 17-20 and test 21-25. Every split on the
year column is a threshold inside 0-16, so the model treats 2017-2025 exactly
like 2016 and cannot continue an upward yield trend. `trend_residual` fits a
one-variable LinearRegression `yield ~ year_since_2000` on training years only,
then boosts the weather features on what the trend leaves over. Prediction =
trend line + boosted weather adjustment. It is reported separately and does
not replace the shared variants. `tests/test_gradient_boosting.py` includes a
synthetic check of this extrapolation behaviour.

## Training and hyperparameter selection

Configured in [config/gradient_boosting.json](config/gradient_boosting.json).

- **Train 2000-2016 (6,681 county-years), validation 2017-2020 (1,572), test
  2021-2025 (1,965)**, from `config/splits.json`. No refit on validation years,
  matching the baseline protocol.
- **Baseline model (`gbr_default`):** scikit-learn defaults (100 trees,
  learning rate 0.1, depth 3, no subsampling).
- **Tuned model (`gbr_tuned`):** grid of 24 settings, learning_rate {0.05, 0.1}
  x max_depth {2, 3, 4} x subsample {0.8, 1.0} x min_samples_leaf {1, 20}.
  Each is fit once with 600 trees; `staged_predict` scores every tree count
  1-600 on validation, so `n_estimators` is tuned too without 600 refits.
- **Selection:** lowest validation MAE (the project's primary metric). Ties go
  to lower RMSE, then shallower trees, then fewer trees. The chosen model is
  refit and the script checks it reproduces the staged validation score
  exactly.
- **Test isolation:** the tuning section only ever receives training and
  validation arrays. `selection.json` (all choices, input hashes, package
  versions) is written before any test prediction is computed. Test metrics
  are computed once from the frozen models.
- **Reproducibility:** `random_state = 42` for every model and for permutation
  importance.

## Reproduce

```powershell
python -m pip install -r requirements-gradient-boosting.txt
python scripts/build_study_sets.py
python scripts/build_splits.py
python scripts/build_features.py
python scripts/run_gradient_boosting.py
python scripts/compare_gradient_boosting.py
python -m unittest discover -s tests -v
```

Settings are plain variables at the top of each script: `config_path`, `out`
and `n_jobs` (CPU cores, -1 = all) in `run_gradient_boosting.py`, and the
result folders in `compare_gradient_boosting.py`. For a quick test run, point
`config_path` at a copy of the config with a smaller grid and `out` at a
scratch folder.

`results/primary_100_gradient_boosting/` holds selection.json, tuning.csv,
metrics.csv, metrics_by_year.csv, predictions.csv, feature_importance.csv and
the saved models. `results/gradient_boosting_comparison/` holds the comparison
tables and figures. The comparison script checks that every model is scored on
the same county-years and that its recomputed Linear/Ridge and weather-group
numbers match the team's published results. It does not retrain any
teammate's model.

## Selected hyperparameters

From `results/primary_100_gradient_boosting/selection.json` (validation MAE):

| Cutoff | Variant | Trees | Learning rate | Depth | Subsample | Min leaf | Validation MAE |
|---|---|---:|---:|---:|---:|---:|---:|
| May | weather_only | 39 | 0.05 | 3 | 0.8 | 20 | 31.29 |
| May | weather_plus_trend | 198 | 0.1 | 2 | 0.8 | 20 | 22.93 |
| May | trend_residual | 84 | 0.05 | 2 | 0.8 | 1 | 22.00 |
| June | weather_only | 134 | 0.05 | 4 | 0.8 | 20 | 28.22 |
| June | weather_plus_trend | 266 | 0.05 | 4 | 1.0 | 1 | 20.21 |
| June | trend_residual | 77 | 0.1 | 4 | 1.0 | 20 | 19.75 |
| July | weather_only | 414 | 0.05 | 4 | 0.8 | 1 | 26.90 |
| July | weather_plus_trend | 228 | 0.1 | 4 | 0.8 | 1 | 19.44 |
| July | trend_residual | 163 | 0.1 | 3 | 0.8 | 1 | 18.38 |
| August | weather_only | 304 | 0.1 | 4 | 1.0 | 20 | 25.40 |
| August | weather_plus_trend | 458 | 0.1 | 2 | 0.8 | 20 | 19.75 |
| August | trend_residual | 346 | 0.05 | 4 | 0.8 | 20 | 18.19 |

No choice reached the 600-tree ceiling. Depth 4, the top of the grid, won 6
of 12 times, so deeper trees were not explored (see limitations). May
weather-only stopped at 39 trees: with no trend term, weather patterns from
2000-2016 transfer poorly to 2017-2020, and extra trees made validation worse.

## Results vs Linear Regression

All numbers are from `results/gradient_boosting_comparison/`. MAE/RMSE are in
bushels per acre, on the same 1,965 test county-years (2021-2025) for every
model. GB = validation-tuned Gradient Boosting. Training-mean reference: test
MAE 42.29.

**Test MAE (lower is better)**

| Cutoff | Linear, weather only | GB, weather only | Linear, weather + trend | GB, weather + trend | GB trend_residual (exploratory) |
|---|---:|---:|---:|---:|---:|
| May | 40.28 | **37.75** | 27.00 | 25.90 | **23.27** |
| June | 40.02 | **36.31** | 26.05 | 25.46 | **22.37** |
| July | 37.04 | **33.87** | **24.75** | 25.26 | **21.79** |
| August | 37.40 | **33.69** | **24.82** | 25.26 | **21.53** |

**Test RMSE and R²**

| Cutoff | Variant | Linear RMSE | GB RMSE | Linear R² | GB R² |
|---|---|---:|---:|---:|---:|
| July | weather_only | 42.93 | 41.19 | -0.556 | -0.432 |
| July | weather_plus_trend | 31.20 | 32.69 | 0.178 | 0.098 |
| July | trend_residual | - | 28.75 | - | 0.302 |
| August | weather_plus_trend | 31.28 | 31.80 | 0.174 | 0.146 |
| August | trend_residual | - | 28.21 | - | 0.328 |

All cutoffs are in `comparison.csv`. Negative R² means worse than predicting
the test-set mean: weather-only models miss the upward yield shift after 2016.

### What this shows

1. **Weather only: GB beats Linear at every cutoff**, by 2.5-3.7 bu/acre test
   MAE. The non-linear, interacting weather effects that motivate boosting do
   show up when weather is the only signal.
2. **Weather + trend: GB wins May and June but loses July and August**, by
   about 0.5 bu/acre. On validation GB won by 1.4-4.5 bu/acre. The difference
   is the extrapolation problem. Trees treat every year after 2016 like 2016,
   and test years are further from 2016 than validation years. The year
   feature has 12-23% of the trees' training split importance but exactly
   **0.00** validation permutation importance, because shuffling years
   17-20 among themselves changes no tree prediction.
3. **The trend-residual hybrid is best at every cutoff**: 21.5-23.3 test
   MAE, about 3 bu/acre (12-14%) below Linear + trend. It was proposed and
   configured before any test score was computed, and it also has the best
   validation MAE at every cutoff. However, it is a Gradient Boosting-only
   variant outside the shared protocol, so present it as **exploratory**, not
   as the headline shared comparison.
4. **Later cutoffs help GB more than Linear.** GB weather-only improves
   steadily from May to August. Linear flattens after July.
5. **Tuning helped validation more than test.** Tuned vs default test MAE
   differs by under 1 bu/acre, and May weather-only got worse (36.86 to
   37.75). See overfitting below.

### Yearly view (July, weather + trend, test MAE)

| Year | Linear | GB | GB trend_residual |
|---|---:|---:|---:|
| 2021 | 22.8 | **21.5** | **18.3** |
| 2022 | 24.6 | **20.5** | **20.5** |
| 2023 | **29.1** | 40.4 | **27.3** |
| 2024 | 25.7 | **22.6** | 24.0 |
| 2025 | 21.6 | **21.4** | **18.8** |

GB + trend beats Linear in 4 of 5 test years. **2023 alone** turns the
July/August result around: GB under-predicted by about 38 bu/acre on average
that year.

## Unusual weather: does GB do better?

Weather groups reuse the team's saved labels in
`results/weather_groups/heldout_weather_labels.csv` (county thresholds from
2000-2016 training weather only). Groups overlap.

**July test MAE, weather + trend**

| Group | n | Linear | GB | GB trend_residual |
|---|---:|---:|---:|---:|
| normal | 1261 | 24.37 | 23.30 | 20.59 |
| dry | 380 | 28.16 | **36.02** | 26.77 |
| hot | 158 | 23.08 | 19.93 | 19.28 |
| wet | 231 | 22.85 | 20.89 | 21.46 |
| hot_dry | 53 | 26.24 | 20.78 | 19.92 |
| extreme_any | 704 | 25.42 | 28.78 | 23.94 |

**Answer: GB is better in hot, wet and hot-and-dry seasons, but clearly worse
in dry ones.** Dry minus normal MAE is larger for GB than for Linear at every
cutoff in both shared variants (for example July weather + trend, +12.7 vs
+3.8; see `results/gradient_boosting_comparison/README.md`). The main reason is **2023**:

- 246 of the 380 dry test county-years are from 2023.
- 93 of those 2023 rows were drier than any season that county had in
  training.
- Yields still averaged 178 bu/acre in 2023. In 2012, the big training-period
  drought, the average was 123.
- GB under-predicted dry rows by 31 bu/acre on average (Linear: 15).

Trees learned a sharp "very dry means a yield crash" rule from the
2000-2016 droughts and applied it to 2023, when dry early-season conditions
did not produce a crash. Linear's single gentle slope was less wrong. Part of
the gap is also the trend problem: under-prediction is worse for every model
in 2023. The trend-residual hybrid shrinks the dry penalty (+6.2 in July) but
does not remove it. With five test years, and one dry year making up most of
the dry group, this is one episode, not a general law about droughts.

## Figures

In `results/gradient_boosting_comparison/figures/`:

- `mae_by_cutoff.png`: test MAE at each cutoff, both variants.
- `predicted_vs_actual_july.png`: July test predictions vs observed.
- `residuals_july.png`: July residual distributions.
- `feature_importance_july.png`: top 12 permutation importances
  (validation).
- `weather_groups_july.png`: July test MAE by weather group.

**Feature importance (July).** Preseason January-March precipitation, the
coldest preseason day, and July mean maximum temperature dominate both
variants. Shuffling the top feature raises validation MAE by about 3 bu/acre.
This shows what the model uses for prediction, not what causes yield.
Preseason precipitation may partly stand in for region or soil moisture.
Overlapping monthly and season features share importance, so a feature low on
the list may still matter through its correlated twin.

## Limitations and overfitting

- **Overfitting.** July weather + trend: train MAE 9.9, validation 19.4, test
  25.3. Boosting fits training years closely. Validation-chosen tree counts,
  `min_samples_leaf` and subsampling limit this, but the gap is large. The
  4-year validation block contains no 2023-like season, so it could not warn
  about the dry-year failure.
- **Trees do not extrapolate.** This applies to the trend and also to weather
  more extreme than anything in training (see 2023). The hybrid fixes only the
  trend part.
- **Selection noise.** 24 settings x 600 tree counts were compared on 4
  validation years. The chosen validation scores are optimistic. Test-score
  differences under about 1 bu/acre should not be treated as decisive.
- **Grid boundary.** Depth 4 was the most-selected value. Deeper trees were
  not tried and are a reasonable follow-up (on validation only).
- **Test years are not fresh.** The team's Linear/Ridge test results were
  already published. GB settings were chosen on validation only and GB test
  scores were computed once. Still, the 2021-2025 period has been inspected
  before, so these results are not a fully untouched holdout.
- **Five test years, correlated counties.** No confidence intervals or
  significance tests. Same caveats as the team's README.
- **Primary cohort only.** The broader coverage sets were not run for GB.
- **Same predictors as the baselines.** No soil, management, irrigation, daily
  heat-day counts or prior yields.
- **Environment.** Python 3.14.5, pandas 3.0.5, scikit-learn 1.9.0 (team pin
  1.9.1). Exact versions are recorded in `selection.json`.

## Possible improvements

- Make a trend-handling choice for all team models (for example the
  trend-residual approach) and evaluate it consistently, instead of GB alone.
- Expanding-window validation, so more than four years, including droughts,
  inform tuning. This must be declared and applied to every model.
- Daily heat/drought features (growing-degree days, consecutive dry days) once
  the raw NOAA files are shared, and leakage-safe lagged yields.
- Try deeper trees, `loss="huber"` or `"absolute_error"` (MAE is the primary
  metric), and `HistGradientBoostingRegressor` for speed.
- Run the broader coverage sets and the shared-393 comparison.
- Use quantile loss for prediction intervals (the project's stretch goal).
