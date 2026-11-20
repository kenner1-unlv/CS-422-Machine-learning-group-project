# Presentation brief: four corn-yield model families

## Opening example: why forecast quality matters

In October 2026, USDA NASS corrected its **September** corn forecast after finding that incorrect acreage weights had been used to combine irrigated and non-irrigated objective-yield observations in Kansas and Nebraska. Corrected September yields were 118 bu/acre for Kansas (down 3), 182 for Nebraska (up 5), and 178.8 for the United States (up 0.3). NASS reviewed its **October** forecast separately and left it unchanged. [USDA NASS correction](https://www.nass.usda.gov/newsroom/notices/2026/10-24-2026).

**Suggested opening line:** “Corn-yield estimates inform consequential decisions. A 2026 USDA correction shows why even the weighting used to combine observations needs careful checks. Our project asks how reproducible county-level models perform when they use the same forecasting dates and held-out rows.” USDA Economic Research Service research finds that USDA corn production forecasts influence corn futures prices and daily price variation. That establishes market relevance; it does **not** establish that the September correction itself caused a particular price move. [USDA ERS market-impact study](https://ers.usda.gov/sites/default/files/_laserfiche/publications/101815/ERR-293.pdf).

The USDA incident concerns a processing step in an objective-yield estimate. This project predicts county-average annual yield from historical weather and year features; it does not separately combine irrigated and non-irrigated field observations. Use the incident as motivation for data provenance and quality control, not as an error we reproduced.

## Main message

On the same 393 counties and held-out county-years, no model family wins every forecast cutoff. Adding the declared year-trend feature changes error much more than most switches between algorithms. Gradient Boosting has the lowest validation MAE for the weather-plus-trend variant at all four cutoffs, but the test results are mixed: it leads in May and June, while the simpler Linear model leads in July and August. Each model used the fixed chronological protocol; the newer Random Forest and Neural Network fits did not train or select settings on test rows.

## What was compared

- **Four model families:** Linear/Ridge Regression, Gradient Boosting, Random Forest, and a single-hidden-layer Neural Network. Ridge is included with Linear because their test scores are very close; the table below displays Linear's number and the [full table](results/team_model_comparison/comparison.csv) retains Ridge.
- **Same evaluation rows:** 393 complete counties; 6,681 training county-years from 2000–2016, 1,572 validation rows from 2017–2020, and 1,965 test rows from 2021–2025 at each May, June, July, and August cutoff. Saved predictions were checked for identical county/year/cutoff/partition keys and observed targets.
- **Two comparable predictor sets:** weather available through the cutoff, and the same weather plus the declared `year_since_2000` trend. Learned scaling and model fits use training rows only; candidate settings use validation MAE. The Gradient Boosting trend-residual hybrid is a separate exploratory design and is outside this four-family comparison.
- **Metric:** mean absolute error (MAE) in bushels per acre; lower is better. The [comparison results](results/team_model_comparison/README.md) also include RMSE, yearly scores, bias, and exploratory weather-group slices.

## Did test data enter training?

No. The new model code passes only 2000–2016 predictors and targets to `fit`, scores candidates only on 2017–2020 validation rows, writes the selected settings, and then scores 2021–2025. Tests check the Neural Network's fitted scaling statistics against training rows and verify identical held-out rows across methods. The four methods did not need to run simultaneously; they needed to follow the same fixed protocol without test-based tuning.

## Test results to put on a slide

Weather plus year trend, 1,965 shared test rows per cutoff:

| Cutoff | Linear | Gradient Boosting | Random Forest | Neural Network |
|---|---:|---:|---:|---:|
| May | 27.00 | **25.90** | 26.09 | 27.35 |
| June | 26.05 | **25.46** | 25.47 | 27.03 |
| July | **24.75** | 25.26 | 26.01 | 26.43 |
| August | **24.82** | 25.26 | 25.89 | 25.99 |

The differences between the best standard models are modest at several cutoffs. In June, Gradient Boosting and Random Forest differ by 0.01 MAE after rounding. Ridge differs from Linear by less than 0.20 MAE on every trend-variant test cutoff. Show the [cutoff figure](results/team_model_comparison/test_mae_by_cutoff.png) beside this table so the weather-only results are visible too: Random Forest leads weather-only May and June; Gradient Boosting leads weather-only July and August.

## Balanced rundown of the four families

| Family | What looks good | What the evidence does not establish |
|---|---|---|
| **Linear/Ridge** | Transparent reference; Linear has the lowest standard-model trend-variant test MAE in July and August. A linear year term can extend beyond training years. Ridge yields almost the same scores, so regularization did not materially change this comparison. | Additive terms may miss weather interactions and nonlinear thresholds. The new trend-only comparator shows weather's added predictive value is modest and varies by cutoff. |
| **Gradient Boosting** | Lowest weather-plus-trend validation MAE at all four cutoffs. Lowest standard-model test MAE in May and June with trend, and July/August with weather alone. | Its July 2023 MAE rises to 40.36, versus 29.08 for Linear. It underpredicts the July trend-variant test rows by 14.42 bu/acre on average. Trees cannot extrapolate the supplied year trend past training values. The lower-error trend-residual hybrid changes the method and stays exploratory. |
| **Random Forest** | Lowest weather-only test MAE in May (36.96) and June (35.77). With trend, its May/June test MAE is close to Gradient Boosting. The compact grid and fixed seed make the run easy to reproduce. | Its July/August trend-variant test MAE trails Linear. July mean underprediction is 15.08 bu/acre; July 2023 MAE is 35.74. The small validation grid and one seed do not identify its best possible configuration. |
| **Neural Network** | Fits the shared rows and predictor lists with training-only scaling. Its July 2023 trend-variant MAE of 28.18 is lower than both tree methods in that one year. | It has no consistent pooled test advantage; July 2024 MAE is 32.88. A separate stopping study met its stopping rules and improved validation in five of eight settings, but test changes were mixed. One seed and a narrow architecture search remain limits. |

The [July yearly figure](results/team_model_comparison/july_test_mae_by_year.png) is a useful second chart: it shows why a five-year pooled score can conceal a bad year or a reversal in ordering.

## Findings to explain aloud

1. **The trend feature is central.** July Linear MAE is 37.04 with weather alone, 26.97 with trend alone, and 24.75 with weather plus trend. Weather adds about 2.22 bu/acre beyond the trend in July on these test years; it adds essentially nothing in May.
2. **Model complexity is not a reliable ranking rule.** Gradient Boosting is strongest on validation for the trend variant, yet Linear has lower July/August test MAE. Random Forest sometimes beats boosting on weather alone; the Neural Network does not consistently beat the simpler models.
3. **Performance varies by year and conditions.** July 2023 is much worse for both tree methods than their five-year averages. In the exploratory July dry group (380 rows), MAE is 28.16 Linear, 36.02 Gradient Boosting, 31.54 Random Forest, and 30.41 Neural Network. The group labels overlap and were defined after earlier overall test results were visible, so this is a diagnostic slice, not proof of drought robustness.
4. **The result is a historical comparison.** Five test years, correlated counties, a complete-county cohort, retrospectively revised weather, and missing soil/management information limit claims about future seasons or real-time use.

## New high-value checks

- **Fixed four-model average:** Equal weights, with no fitted stacking coefficients, give weather-plus-trend test MAE 24.10 / 23.14 / 23.06 / 23.26 from May to August. Validation improves versus the best individual in May and June but not July and August. Present this as an exploratory ensemble result, alongside the original standard-model table.
- **More training counties:** The expanded_90 run uses 883 counties for fitting and scores the unchanged primary test rows. Linear, Gradient Boosting and Random Forest get worse at all eight cutoff/variant combinations; Neural Network is mixed. More rows are not automatically more useful when the county mix changes.
- **Stopping the NN properly:** The original `tol=0` setting made a 250-iteration cap warning expected. New runs with training-only stopping rules stop before 1,500 iterations; validation selects new fits in five of eight settings, but test error is mixed. Do not say the new NN is globally optimal.
- **Year sensitivity:** July's descriptive winner switches from Linear to Gradient Boosting if 2023 is omitted. The [year-omission table](results/team_model_comparison/year_omission_sensitivity.csv) is a sensitivity check, not a confidence interval.

The [supplemental report](SUPPLEMENTAL_ANALYSES.md) includes exact methods, validation/test scores and the [ensemble figure](results/supplemental_figures/ensemble_and_trend_test_mae.png).

## What is still missing

- **Formal uncertainty analysis:** five years are the meaningful temporal units; ordinary row-level confidence intervals would overstate precision. No cluster-aware interval or significance claim is currently supported.
- **Full broader-cohort parity:** all four families now have an expanded_90 check; expanded_80 and largest-available training remain untested for Gradient Boosting, Random Forest and Neural Network.
- **Neural Network stability:** the stopping study uses one seed. Repeated seeds would test how much its result depends on initialization, but would be a separate analysis.
- **Operational validation:** revised historical inputs are not evidence of what would have been available on each original cutoff date. A true as-of-data backtest and an independent later-year evaluation would be needed for deployment claims.

## Suggested presentation sequence

1. Open with the 2026 USDA correction and why accurate crop estimates matter to decision-makers and markets.
2. Research question, data sources, primary cohort, and chronological split.
3. Four model families and the shared weather-only versus weather-plus-trend feature sets.
4. Same-row test MAE table and cutoff figure; state the validation choice separately from the descriptive test ranking.
5. July yearly figure and the exploratory dry-group example to show instability.
6. Show the supplemental trend-only and equal-mean ensemble results, with the broader-training negative result and year sensitivity.
7. Balanced conclusion: Gradient Boosting is validation-favored among standard individual models, Linear remains competitive on later test cutoffs, and the exploratory ensemble needs independent confirmation.

Detailed methods and limitations are in [FINAL_REPORT.md](FINAL_REPORT.md), [SUPPLEMENTAL_ANALYSES.md](SUPPLEMENTAL_ANALYSES.md), [LINEAR_REGRESSION.md](LINEAR_REGRESSION.md), [GRADIENT_BOOSTING.md](GRADIENT_BOOSTING.md), [RANDOM_FOREST.md](RANDOM_FOREST.md), and [NEURAL_NETWORK.md](NEURAL_NETWORK.md). Original comparison numbers come from [comparison.csv](results/team_model_comparison/comparison.csv), [comparison_by_year.csv](results/team_model_comparison/comparison_by_year.csv), and [subgroup_comparison.csv](results/team_model_comparison/subgroup_comparison.csv); supplemental numbers are linked from the supplemental report.
