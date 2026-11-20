# Supplemental model checks for the corn-yield project

These checks address four questions raised after the original four-family comparison. They retain the primary 393-county chronology: training 2000–2016, validation 2017–2020, and test 2021–2025. They do not replace the original model results in [FINAL_REPORT.md](FINAL_REPORT.md). The fixed four-model mean and broader-cohort check are exploratory additions; their observed test gains or losses should not be treated as a new independent model-selection exercise.

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

An unweighted average combines the saved predictions from four families: Linear, validation-tuned Gradient Boosting, Random Forest, and the original Neural Network. Each receives weight 0.25. Ridge is omitted because it is nearly identical to Linear. There are no fitted stacking weights or test-based choices. The same-row, weather-plus-trend scores are:

| Cutoff | Blend validation MAE | Blend test MAE | Blend test RMSE | Best individual standard-model test MAE |
|---|---:|---:|---:|---:|
| May | 22.72 | 24.10 | 29.96 | 25.90 |
| June | 20.08 | 23.14 | 29.18 | 25.46 |
| July | 20.00 | 23.06 | 29.54 | 24.75 |
| August | 20.10 | 23.26 | 29.47 | 24.82 |

The fixed blend has lower test MAE than every individual standard model at all four trend-variant cutoffs. Its validation MAE is lower than the best individual in May and June, but **higher** than Gradient Boosting in July and August (19.44 and 19.75). The weather-only blend does not lead the individual models: its test MAE is 37.56, 37.20, 35.08, and 34.67 from May through August. This result supports including complementary models in a discussion, but the idea was added after the original model comparison. It is exploratory evidence on the same five test years, not a promised future gain. The [ensemble figure](results/supplemental_figures/ensemble_and_trend_test_mae.png) and saved predictions show the full result.

The convergence-study NN can also be inserted into the same fixed average. That version ties the original blend in May and August, but has worse validation MAE in June (20.30 versus 20.08) and July (20.07 versus 20.00). The original NN blend is therefore the validation-preferred version of these two fixed ensembles; both are retained in [primary_100_diagnostic_additions/](results/primary_100_diagnostic_additions). No ensemble member or weight was chosen from test scores.

## 3. Would a converged Neural Network generalize better?

The original `MLPRegressor` deliberately used `tol=0` and a 250-iteration budget, so its cap warning was expected from that configuration and did not by itself prove optimization failure. A separate study compared that frozen model with 32- and 64-unit networks under two stopping strategies: training-loss patience and an internal 15% validation slice randomly drawn from training rows (2000–2016), not held out by year. Both strategies used Adam, learning rate 0.001, L2 `alpha=0.001`, batch size 256, a maximum of 1,500 iterations, `tol=0.0001`, and patience 30. The outer 2017–2020 chronological validation MAE selected among the original and four new candidates for each cutoff/variant before the test-score stage. The internal early-stopping monitor is separate from the outer chronological validation set.

All new candidates met their declared stopping rule before 1,500 iterations. A new candidate won validation in five of eight cutoff/variant combinations; the original 250-iteration model remained preferred in three. The table shows the four weather-plus-trend comparisons:

| Cutoff | Original NN validation MAE | Selected stopping-study validation MAE | Original NN test MAE | Selected stopping-study test MAE |
|---|---:|---:|---:|---:|
| May | 26.23 | 26.23 | 27.35 | 27.35 |
| June | 26.50 | 24.71 | 27.03 | 27.32 |
| July | 23.63 | 22.84 | 26.43 | 26.87 |
| August | 23.29 | 23.29 | 25.99 | 25.99 |

The stopping study improves outer validation in June and July but has slightly worse test MAE there. The selected weather-only versions improve test MAE slightly in May, June, and July. A training stopping rule is not a guarantee of stronger later-year generalization, and this bounded study cannot identify a globally optimal network. Candidate iteration counts, loss curves, the saved validation decision, and both sets of test scores are in [primary_100_neural_network_stopping_study/](results/primary_100_neural_network_stopping_study).

## 4. Does adding training counties help on the same test population?

The original Linear/Ridge coverage analysis already ran the 90%, 80%, and largest-available sets. Gradient Boosting, Random Forest, and Neural Network previously used only the primary cohort. This check trains all four families on the **expanded_90** set (883 counties; 14,801 training county-years per cutoff), reusing the hyperparameters selected on the primary cohort. It then scores both the unchanged 393-county primary validation/test rows and the broader cohort's own 3,369 validation and 4,084 test rows. The broader own-population scores answer a different question and are not directly ranked against primary-population scores.

On the **same primary test rows**, expanded training raises MAE for Linear, Gradient Boosting, and Random Forest in every cutoff/variant combination (8 of 8 each). The same three families also worsen in all eight shared-primary validation comparisons. Neural Network is mixed, improving in 4 of 8 test comparisons and 2 of 8 validation comparisons. The weather-plus-trend test examples show the direction and size of the change:

| Cutoff | Linear change | Gradient Boosting change | Random Forest change | Neural Network change |
|---|---:|---:|---:|---:|
| May | +1.81 | +1.08 | +1.54 | -0.63 |
| June | +1.46 | +0.83 | +0.88 | -2.28 |
| July | +1.11 | +0.58 | +0.80 | +0.04 |
| August | +1.39 | +0.59 | +0.64 | +1.14 |

Positive means higher error after adding training counties. The [expanded-training figure](results/supplemental_figures/expanded_training_effect.png) visualizes the shared-row comparison. The fixed primary settings may not be best for the broader training population, so this isolates one particular training-scope change rather than proving that broader data is harmful in general. Full validation, test, own-population, and row-level outputs are in [expanded_90_four_model_check/](results/expanded_90_four_model_check).

## Test-year sensitivity

Removing one full test year at a time changes the descriptive July weather-plus-trend leader. Linear has the lowest MAE when 2021, 2022, 2024, or 2025 is omitted; Gradient Boosting leads when 2023 is omitted. That is a concrete warning against declaring a general winner from five years. The complete [year-omission table](results/team_model_comparison/year_omission_sensitivity.csv) covers every cutoff and variant. This is a sensitivity check, not a confidence interval or significance test.

## Reproduce

From this project folder with [requirements-remaining-models.txt](requirements-remaining-models.txt) installed and the shared feature tables rebuilt, run:

```powershell
py -3.13 scripts/run_nn_convergence.py select
py -3.13 scripts/run_nn_convergence.py score
py -3.13 scripts/run_diagnostic_additions.py --neural-source original
py -3.13 scripts/run_diagnostic_additions.py --neural-source stopping_study
py -3.13 scripts/run_expanded_training_check.py
py -3.13 scripts/compare_remaining_models.py
py -3.13 scripts/plot_supplemental.py
py -3.13 -m unittest discover -s tests -v
```

The stopping study saves its outer-validation choice before test scoring. The trend baseline and equal blend have fixed formulas; the expanded-training check freezes primary-selected settings and verifies identical primary targets and predictors across cohort tables. These supplemental results do not alter the original five-standard-model table. No formal cluster-aware confidence interval or significance claim is made.
