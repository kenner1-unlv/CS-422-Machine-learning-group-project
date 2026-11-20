# Neural Network Regression — primary cohort

## Method and reproducibility

The shared primary cohort contains 393 complete counties. Each cutoff has 6,681 training county-years (2000–2016), 1,572 validation rows (2017–2020), and 1,965 test rows (2021–2025). Separate single-hidden-layer scikit-learn `MLPRegressor` models use the manifest's weather-only or weather-plus-trend predictor lists for each May–August cutoff. A `StandardScaler` is fitted to training predictors inside the pipeline, and a second training-fitted scaler standardizes yield during optimization; predictions are converted back to bushels per acre before scoring. No county ID, target, raw year, partition or cutoff metadata enters as a predictor.

The fixed validation comparison uses 32 or 64 ReLU hidden units, one linear regression output, Adam, learning rate 0.001, L2 `alpha=0.001`, batch size 256, 250 iterations, seed 42, and no early stopping. Settings are selected separately for each cutoff/variant by validation MAE, then RMSE, then candidate order. The saved training model is used for test predictions without refitting on validation. All selected networks reached the deliberately fixed 250-iteration cap and scikit-learn emitted convergence warnings; the `tol=0` configuration made the warning expected, so it is not proof of a practical optimization failure. The full candidate scores, chosen widths, input hashes, versions and split policy are in [selection.json](results/primary_100_neural_network/selection.json) and [tuning.csv](results/primary_100_neural_network/tuning.csv). The test scores did not inform this model's settings.

Run from this folder after shared feature generation:

```powershell
py -3.13 scripts/run_remaining_models.py neural_network
```

The run used scikit-learn 1.9.0, NumPy 2.2.6 and pandas 3.1.0. Exact row-level outputs, [overall metrics](results/primary_100_neural_network/metrics.csv), [yearly metrics](results/primary_100_neural_network/metrics_by_year.csv), [weather-group metrics](results/primary_100_neural_network/subgroup_metrics.csv), and fitted pipelines are saved in the results folder. MAE and RMSE are bushels per acre.

## Results

| Cutoff | Variant | Chosen hidden units | Validation MAE | Test MAE | Test RMSE |
|---|---|---:|---:|---:|---:|
| May | Weather only | 32 | 39.74 | 37.49 | 44.89 |
| June | Weather only | 64 | 28.68 | 39.49 | 47.37 |
| July | Weather only | 32 | 29.85 | 38.46 | 45.94 |
| August | Weather only | 32 | 27.91 | 37.13 | 44.86 |
| May | Weather plus trend | 32 | 26.23 | 27.35 | 34.18 |
| June | Weather plus trend | 32 | 26.50 | 27.03 | 34.71 |
| July | Weather plus trend | 64 | 23.63 | 26.43 | 33.28 |
| August | Weather plus trend | 64 | 23.29 | 25.99 | 32.53 |

Each test score uses 1,965 rows. The weather-plus-trend variant generally has lower error than weather alone, but the network does not consistently beat the simpler models on this shared test. July weather-plus-trend test MAE is 26.43, compared with 24.75 for Linear and 26.01 for Random Forest. The July network has a 28.18 MAE in 2023 but 32.88 in 2024; one year's relative strength did not persist into the next. For the exploratory July weather groups, the network has MAE 25.96 on 1,261 normal rows and 30.41 on 380 dry rows. The [team comparison](results/team_model_comparison/README.md) keeps these results alongside the same-row baselines.

## Limits

The fixed 250-iteration cap and convergence warnings reflect this run's deliberate `tol=0` fixed-budget setting; a warning alone does not establish a practical training failure. A separate [stopping study](SUPPLEMENTAL_ANALYSES.md) compared longer training and training-only early stopping on validation. Its new candidates met stopping rules, but test changes were mixed. Neither run establishes the best achievable neural network result or shows that neural networks are generally unsuitable. The results also depend on one seed, one chronological split, a small validation search and only five test years. County errors within a year are correlated; weather-group labels are exploratory; the complete-county cohort, retrospective weather revisions and omitted farm variables limit generalization.
