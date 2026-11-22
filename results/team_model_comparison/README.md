# Shared primary-cohort model comparison

The [comparison script](../../scripts/compare_remaining_models.py) reads frozen prediction CSVs from Linear, Ridge, validation-tuned Gradient Boosting, Random Forest and Neural Network. It verifies identical county/year/cutoff/partition keys and observed yield for all five standard methods and both shared variants. Each cutoff has 1,572 validation and 1,965 test rows, from the same 393 counties. MAE and RMSE are in bushels per acre. The exploratory Gradient Boosting `trend_residual` hybrid stays outside this standard ranking.

## Test MAE

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

The full-precision [comparison.csv](comparison.csv) contains validation and test MAE, RMSE, bias and counts. [comparison_by_year.csv](comparison_by_year.csv) gives each test year's scores; [subgroup_comparison.csv](subgroup_comparison.csv) applies the same saved exploratory hot/dry/wet labels. The [cutoff figure](test_mae_by_cutoff.png) and [July yearly figure](july_test_mae_by_year.png) visualize these numbers.

The year term often matters more than the model choice: July Linear falls from 37.04 MAE with weather alone to 24.75 with weather plus trend. Random Forest is strongest among the standard models in weather-only May and June test results, while Gradient Boosting leads weather-only July and August. With the trend, Gradient Boosting leads May and June and Linear leads July and August. This is descriptive test ranking, not test-based model selection. Every model's settings were selected by validation under the shared protocol.

July 2023 is difficult for the tree methods: Gradient Boosting MAE 40.36 and Random Forest 35.74, compared with Linear 29.08 and Neural Network 28.18. July dry-group MAE is 36.02 for Gradient Boosting, 31.54 for Random Forest, 30.41 for Neural Network and 28.16 for Linear, with 380 rows from five years. The groups overlap and were chosen after earlier overall test results were visible; county-years are correlated. No statistical significance or general superiority is claimed.

Rebuild the tables and figures from saved predictions with `py -3.13 scripts/compare_remaining_models.py` after generating the two new model results. See [Random Forest](../../RANDOM_FOREST.md) and [Neural Network](../../NEURAL_NETWORK.md) for training commands, settings, and limitations.

The [supplemental analysis](../../SUPPLEMENTAL_ANALYSES.md) adds a trend-only baseline, a fixed equal-weight ensemble, an NN stopping study, an expanded_90 training check, and a leave-one-year-out sensitivity table. These are reported separately from the standard-model comparison above.
