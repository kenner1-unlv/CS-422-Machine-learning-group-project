# Early-season county corn-yield forecasting: final model comparison

## Question and data

We studied how well county corn-grain yield can be estimated at the end of May, June, July and August, and whether additional weather data and different regression methods improve later-year forecasts. The target is USDA NASS corn-grain yield in bushels per acre. Weather predictors come from NOAA nClimGrid-Daily county area averages, aggregated only through the applicable forecast cutoff. The analysis is historical and predictive, not causal or a live forecast service. Source preparation and cohort rules are detailed in [PROJECT_SPEC.md](PROJECT_SPEC.md), [STUDY_DATA_PLAN.md](STUDY_DATA_PLAN.md), and [FEATURE_PLAN.md](FEATURE_PLAN.md).

The primary comparable cohort has 393 counties with complete observed yield and January–August weather for every year from 2000 through 2025: 10,218 county-years. A fixed harvest-year split uses 6,681 training rows (2000–2016), 1,572 validation rows (2017–2020), and 1,965 test rows (2021–2025) **at each cutoff**. The four forecasts for any county-year share a partition. The weather-only and weather-plus-trend feature lists come directly from the generated manifest. County FIPS, raw year, cutoff, partition and target are never inferred as predictors. The extra trend feature in the secondary variant is the explicitly declared `year_since_2000`. Source weather is retrospectively revised; limiting its calendar cutoff alone does not prove that these exact values existed on the original forecast date.

## Methods

Five standard regression methods were compared: ordinary Linear Regression, Ridge Regression, Gradient Boosting, Random Forest and a single-hidden-layer Neural Network. The training-mean reference is separate. Every algorithm uses the same primary county-year rows, observed targets and predictor allowlists for each cutoff and variant. Learned scaling is fit on training data only for Linear/Ridge and Neural Network; tree models use original feature units. Ridge, Gradient Boosting, Random Forest and Neural Network settings were chosen by validation MAE. No fit was expanded to validation or test rows. The Gradient Boosting trend-residual hybrid uses a different architecture and is excluded from the shared standard ranking. Method details and settings are in [LINEAR_REGRESSION.md](LINEAR_REGRESSION.md), [GRADIENT_BOOSTING.md](GRADIENT_BOOSTING.md), [RANDOM_FOREST.md](RANDOM_FOREST.md), and [NEURAL_NETWORK.md](NEURAL_NETWORK.md).

## Results on identical test rows

Each cell is MAE in bushels per acre on the same 1,965 test county-years. Lower is better. [Full-precision metrics](results/team_model_comparison/comparison.csv) also include validation MAE, RMSE and bias; [annual metrics](results/team_model_comparison/comparison_by_year.csv) and [weather-group metrics](results/team_model_comparison/subgroup_comparison.csv) expose variation hidden by pooled scores.

| Cutoff | Variant | Linear | Ridge | Gradient Boosting | Random Forest | Neural Network |
|---|---|---:|---:|---:|---:|---:|
| May | Weather only | 40.28 | 40.28 | 37.75 | 36.96 | 37.49 |
| June | Weather only | 40.02 | 40.01 | 36.31 | 35.77 | 39.49 |
| July | Weather only | 37.04 | 37.19 | 33.87 | 34.37 | 38.46 |
| August | Weather only | 37.40 | 37.53 | 33.69 | 34.67 | 37.13 |
| May | Weather plus trend | 27.00 | 26.99 | 25.90 | 26.09 | 27.35 |
| June | Weather plus trend | 26.05 | 26.18 | 25.46 | 25.47 | 27.03 |
| July | Weather plus trend | 24.75 | 24.77 | 25.26 | 26.01 | 26.43 |
| August | Weather plus trend | 24.82 | 25.01 | 25.26 | 25.89 | 25.99 |

The secondary metric is RMSE in bushels per acre, on those same 1,965 rows per cutoff:

| Cutoff | Variant | Linear | Ridge | Gradient Boosting | Random Forest | Neural Network |
|---|---|---:|---:|---:|---:|---:|
| May | Weather only | 46.00 | 46.01 | 43.11 | 42.54 | 44.89 |
| June | Weather only | 45.88 | 45.88 | 42.39 | 41.85 | 47.37 |
| July | Weather only | 42.93 | 43.10 | 41.19 | 40.98 | 45.94 |
| August | Weather only | 43.25 | 43.38 | 40.85 | 41.03 | 44.86 |
| May | Weather plus trend | 32.98 | 32.98 | 31.77 | 31.56 | 34.18 |
| June | Weather plus trend | 31.74 | 31.85 | 32.10 | 31.84 | 34.71 |
| July | Weather plus trend | 31.20 | 31.22 | 32.69 | 32.56 | 33.28 |
| August | Weather plus trend | 31.28 | 31.37 | 31.80 | 31.89 | 32.53 |

RMSE can change the descriptive ordering: Gradient Boosting has the lowest June weather-plus-trend MAE, while Linear has the lowest RMSE. Complete by-year MAE, RMSE and row counts are in [comparison_by_year.csv](results/team_model_comparison/comparison_by_year.csv).

The [cutoff comparison figure](results/team_model_comparison/test_mae_by_cutoff.png) shows that more months do not guarantee lower error for every method. Adding the declared year trend produces a much larger change than switching between several methods: July Linear MAE falls from 37.04 to 24.75. Weather-only Random Forest has the lowest standard-model test MAE in May and June, while Gradient Boosting leads July and August. With trend, Gradient Boosting leads May and June; Linear leads July and August. These are descriptions of already-viewed test scores, **not** a rule for selecting the deployed model. On validation, weather-plus-trend Gradient Boosting had the lowest MAE among the five standard methods at all four cutoffs (22.93, 20.21, 19.44 and 19.75).

The [July annual figure](results/team_model_comparison/july_test_mae_by_year.png) shows substantial variation. In 2023, July weather-plus-trend MAE was 40.36 for Gradient Boosting, 35.74 for Random Forest, 29.08 for Linear, and 28.18 for Neural Network. In 2024 the Neural Network was at 32.88 while Gradient Boosting was at 22.59. The pooled five-year ordering conceals such reversals. Random Forest and Gradient Boosting year splits cannot extrapolate the supplied numeric year trend beyond training years; their July mean test biases are -15.08 and -14.42 bu/acre, respectively, compared with -5.60 for Linear. That is consistent with a trend-extrapolation limitation, but other data changes may contribute.

The previously defined hot/dry/wet labels are exploratory and can overlap. In July with trend, the 380 dry rows have MAE 28.16 Linear, 36.02 Gradient Boosting, 31.54 Random Forest and 30.41 Neural Network; the 1,261 normal rows have 24.37, 23.30, 25.30 and 25.96, respectively. Dry rows are not independent events, and 2023 contributes heavily to that group. These slices cannot establish a general drought winner. The exploratory Gradient Boosting trend-residual hybrid obtained lower test MAE than the standard variants in the earlier report, but it changes trend treatment and is not a like-for-like method comparison.

## Interpretation and limits

If a single standard individual method had to be selected under the existing validation rule, weather-plus-trend Gradient Boosting is supported at all four cutoffs. The final test comparison is mixed, especially in July and August, so Linear is a credible simpler reference. The Random Forest contribution adds some weather-only gains, but its trend variant does not consistently beat Linear. The Neural Network provides a controlled nonlinear comparison, yet its original fixed 250-iteration budget reached the cap by design and did not show a stable advantage. The supplemental stopping study addresses that budget separately. No claim that these architectures or algorithms are generally superior follows from this one study.

The test period has only five harvest years. Counties within a year share weather and economic shocks, so 1,965 rows are not 1,965 independent future seasons. The complete-county cohort is selective; Linear/Ridge have results across all four coverage sets and the other families have a supplemental expanded_90 check, but full broader-cohort parity remains open. Soil, seed, irrigation, management and pests are absent. Weather inputs may be revised after the original date. No formal cluster-aware uncertainty intervals or statistical significance result was completed. The Random Forest and Neural Network fits and preprocessing used training rows only; their settings were selected from validation scores before test scoring. All four model families followed the documented split and feature protocol. These limits should accompany any presentation of the score table.

## Supplemental checks

The [supplemental analysis](SUPPLEMENTAL_ANALYSES.md) keeps this standard-model comparison intact while addressing four follow-up questions. A trend-only Linear baseline has test MAE 26.97 at every cutoff; adding weather to Linear lowers that to 24.75 in July and 24.82 in August, but does not help in May on these test years. A fixed equal-weight average of the four original model families has weather-plus-trend test MAE 24.10, 23.14, 23.06, and 23.26 from May through August. This exploratory blend was not tuned on test outcomes and does not establish a general advantage. A separate NN stopping study improves validation in five of eight cutoff/variant comparisons, with mixed test changes. Training all four families on the expanded_90 cohort and scoring the same primary test rows worsens all eight Linear, Gradient Boosting, and Random Forest cutoff/variant comparisons; Neural Network changes are mixed. A leave-one-year-out check changes the descriptive July trend-variant leader when 2023 is omitted. Full settings, row counts, figures and caveats are in the supplemental report.

## Reproduce and verify

From this project folder, install the new run's pinned [requirements-remaining-models.txt](requirements-remaining-models.txt) in its own environment (separate from the earlier [requirements-modeling.txt](requirements-modeling.txt) environment), then rebuild ignored derived inputs from the tracked processed data and run the remaining models. The `py -3.13` launcher selects Python 3.13 on Windows; an activated Python 3.13 environment can use `python` instead:

```powershell
py -3.13 scripts/build_study_sets.py
py -3.13 scripts/build_splits.py
py -3.13 scripts/build_features.py
py -3.13 scripts/run_remaining_models.py random_forest
py -3.13 scripts/run_remaining_models.py neural_network
py -3.13 scripts/compare_remaining_models.py
py -3.13 -m unittest discover -s tests -v
```

The new runner checks feature SHA-256 hashes against the earlier Gradient Boosting run, records validation choices before test prediction, saves fitted models and row-level results, and checks rows and observed targets against Linear. The comparison script independently recomputes scores from saved predictions and requires exact shared-row alignment. Package versions for the new fits are in each selection file. Existing model reports contain their original run commands; the comparison script reads their saved predictions rather than retraining them.

The commands for the bounded trend, ensemble, NN stopping and expanded-training checks are in [SUPPLEMENTAL_ANALYSES.md](SUPPLEMENTAL_ANALYSES.md).
