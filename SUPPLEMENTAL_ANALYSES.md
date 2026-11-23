# Supplemental model checks for the corn-yield project

These exploratory checks were added after initial model results were visible. They retain the primary 393-county chronology: training 2000–2016, validation 2017–2020, and test 2021–2025. They do not replace the standard model results in [FINAL_REPORT.md](FINAL_REPORT.md). The fixed four-model mean and broader-cohort check are exploratory additions; their observed test gains or losses should not be treated as a new independent model-selection exercise.

## 1. Does weather add information beyond the year trend?

A new ordinary linear baseline fits only `year_since_2000` on the 6,681 primary training rows, with an intercept and no weather inputs. Its validation MAE is **25.09** and test MAE is **26.97** bu/acre; the same forecast is used at every cutoff because no weather enters the model. The comparison below keeps the exact same 1,965 test county-years at every cutoff.

| Cutoff | Trend-only test MAE | Linear weather + trend test MAE | Trend-only minus full Linear |
|---|---:|---:|---:|
| May | 26.97 | 27.00 | -0.03 |
| June | 26.97 | 26.05 | +0.93 |
| July | 26.97 | 24.75 | +2.22 |
| August | 26.97 | 24.82 | +2.16 |

Weather adds little to this Linear May forecast on the test years, while later weather lowers its July and August MAE by about 2.2 bu/acre. The validation-year improvements are 0.79–1.21 bu/acre across the four cutoffs. This is an incremental predictive comparison, not a causal estimate of weather's effect on yield. The fitted slope and intercept, predictions, annual scores, and exact differences are in [primary_100_diagnostic_additions/](results/primary_100_diagnostic_additions).

## 2. Does a fixed ensemble help?

The arithmetic mean uses saved predictions from Linear, validation-tuned Gradient Boosting, Random Forest, and Lester's Neural Network, each with weight 0.25. Ridge is omitted because its predictions are similar to Linear. No weights were fitted. The blend was evaluated on the identical 1,965 test rows per cutoff; no NN validation rows are available, so no validation ensemble score is reported.

| Cutoff | Weather + trend test MAE | Weather + trend test RMSE | Best standard individual test MAE | Weather-only blend test MAE |
|---|---:|---:|---:|---:|
| May | 22.83 | 28.87 | 25.90 | 38.11 |
| June | 22.73 | 28.89 | 25.46 | 37.21 |
| July | 22.02 | 28.45 | 23.73 | 33.64 |
| August | 22.60 | 28.66 | 22.95 | 33.75 |

With trend, the blend scores below each individual model at every cutoff on these five years. Without trend, it does not lead at any cutoff. This is a post-initial-results diagnostic on the same test years, not independent evidence of future gains. The [ensemble figure](results/supplemental_figures/ensemble_and_trend_test_mae.png) and [saved outputs](results/primary_100_diagnostic_additions) provide the full-precision results.

## 3. Does adding training counties help on the same test population?

The original Linear/Ridge coverage analysis already ran the 90%, 80%, and largest-available sets. This check trains Linear, Gradient Boosting, and Random Forest on the **expanded_90** set (883 counties; 14,801 training county-years per cutoff), reusing the hyperparameters selected on the primary cohort. It then scores both the unchanged 393-county primary validation/test rows and the broader cohort's own 3,369 validation and 4,084 test rows. Lester’s Neural Network was not run on this broader cohort. The broader own-population scores answer a different question and are not directly ranked against primary-population scores.

On the **same primary test rows**, expanded training raises MAE for Linear, Gradient Boosting, and Random Forest in every cutoff/variant combination (8 of 8 each). The same three families also worsen in all eight shared-primary validation comparisons. The weather-plus-trend test examples show the direction and size of the change:

| Cutoff | Linear change | Gradient Boosting change | Random Forest change |
|---|---:|---:|---:|
| May | +1.81 | +1.08 | +1.54 |
| June | +1.46 | +0.83 | +0.88 |
| July | +1.11 | +0.58 | +0.80 |
| August | +1.39 | +0.59 | +0.64 |

Positive means higher error after adding training counties. The [expanded-training figure](results/supplemental_figures/expanded_training_effect.png) visualizes the shared-row comparison. The fixed primary settings may not be best for the broader training population, so this isolates one particular training-scope change rather than proving that broader data is harmful in general. Full validation, test, own-population, and row-level outputs are in [expanded_90_three_model_check/](results/expanded_90_three_model_check).

## Test-year sensitivity

Removing one full test year at a time changes the descriptive July weather-plus-trend leader. Neural Network has the lowest MAE when 2021, 2022, 2024, or 2025 is omitted; Gradient Boosting leads when 2023 is omitted. That is a concrete warning against declaring a general winner from five years. The complete [year-omission table](results/team_model_comparison/year_omission_sensitivity.csv) covers every cutoff and variant. This is a sensitivity check, not a confidence interval or significance test.

## Reproduce

From this project folder with [requirements-remaining-models.txt](requirements-remaining-models.txt) installed and the shared feature tables rebuilt, run:

```powershell
py -3.13 scripts/run_diagnostic_additions.py
py -3.13 scripts/compare_remaining_models.py
py -3.13 scripts/plot_supplemental.py
py -3.13 -m unittest discover -s tests -v
```

The trend baseline and equal blend have fixed formulas. The preserved expanded check used primary-selected settings and identical primary targets and predictors across cohort tables; rerun its training script only if deliberately reproducing fits. The ensemble rebuild reads saved predictions and does not refit its four members. No formal cluster-aware confidence interval or significance claim is made.
