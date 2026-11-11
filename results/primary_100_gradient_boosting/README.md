# primary_100 Gradient Boosting

Train 2000-2016, validation 2017-2020, test 2021-2025. Hyperparameters selected by validation MAE only; no refit on validation years. `gbr_default` uses scikit-learn defaults; `gbr_tuned` is the validation-selected model. `trend_residual` is an exploratory variant (linear year trend + boosted weather residual), not part of the shared comparison. MAE/RMSE in bushels per acre.

| Cutoff | Variant | Model | Trees | LR | Depth | Subsample | Min leaf | Train MAE | Validation MAE | Test MAE | Test RMSE | Test R² | Test n |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 05 | weather_only | gbr_default | 100 | 0.1 | 3 | 1.0 | 1 | 18.19 | 33.74 | 36.86 | 42.41 | -0.519 | 1965 |
| 05 | weather_only | gbr_tuned | 39 | 0.05 | 3 | 0.8 | 20 | 21.58 | 31.29 | 37.75 | 43.11 | -0.569 | 1965 |
| 05 | weather_plus_trend | gbr_default | 100 | 0.1 | 3 | 1.0 | 1 | 16.74 | 24.08 | 25.59 | 31.25 | 0.175 | 1965 |
| 05 | weather_plus_trend | gbr_tuned | 198 | 0.1 | 2 | 0.8 | 20 | 17.46 | 22.93 | 25.90 | 31.77 | 0.148 | 1965 |
| 05 | trend_residual | gbr_default | 100 | 0.1 | 3 | 1.0 | 1 | 17.58 | 23.66 | 22.49 | 28.90 | 0.295 | 1965 |
| 05 | trend_residual | gbr_tuned | 84 | 0.05 | 2 | 0.8 | 1 | 20.61 | 22.00 | 23.27 | 29.67 | 0.257 | 1965 |
| 06 | weather_only | gbr_default | 100 | 0.1 | 3 | 1.0 | 1 | 16.96 | 28.98 | 36.58 | 42.62 | -0.534 | 1965 |
| 06 | weather_only | gbr_tuned | 134 | 0.05 | 4 | 0.8 | 20 | 16.03 | 28.22 | 36.31 | 42.39 | -0.517 | 1965 |
| 06 | weather_plus_trend | gbr_default | 100 | 0.1 | 3 | 1.0 | 1 | 15.96 | 20.83 | 25.80 | 32.32 | 0.118 | 1965 |
| 06 | weather_plus_trend | gbr_tuned | 266 | 0.05 | 4 | 1.0 | 1 | 12.86 | 20.21 | 25.46 | 32.10 | 0.130 | 1965 |
| 06 | trend_residual | gbr_default | 100 | 0.1 | 3 | 1.0 | 1 | 16.01 | 20.40 | 22.44 | 28.64 | 0.307 | 1965 |
| 06 | trend_residual | gbr_tuned | 77 | 0.1 | 4 | 1.0 | 20 | 15.03 | 19.75 | 22.37 | 28.67 | 0.306 | 1965 |
| 07 | weather_only | gbr_default | 100 | 0.1 | 3 | 1.0 | 1 | 15.64 | 28.10 | 34.44 | 40.77 | -0.404 | 1965 |
| 07 | weather_only | gbr_tuned | 414 | 0.05 | 4 | 0.8 | 1 | 10.51 | 26.90 | 33.87 | 41.19 | -0.432 | 1965 |
| 07 | weather_plus_trend | gbr_default | 100 | 0.1 | 3 | 1.0 | 1 | 14.68 | 20.90 | 25.65 | 31.94 | 0.139 | 1965 |
| 07 | weather_plus_trend | gbr_tuned | 228 | 0.1 | 4 | 0.8 | 1 | 9.88 | 19.44 | 25.26 | 32.69 | 0.098 | 1965 |
| 07 | trend_residual | gbr_default | 100 | 0.1 | 3 | 1.0 | 1 | 14.82 | 18.93 | 21.84 | 28.79 | 0.300 | 1965 |
| 07 | trend_residual | gbr_tuned | 163 | 0.1 | 3 | 0.8 | 1 | 13.48 | 18.38 | 21.79 | 28.75 | 0.302 | 1965 |
| 08 | weather_only | gbr_default | 100 | 0.1 | 3 | 1.0 | 1 | 15.50 | 26.55 | 33.96 | 40.37 | -0.376 | 1965 |
| 08 | weather_only | gbr_tuned | 304 | 0.1 | 4 | 1.0 | 20 | 9.52 | 25.40 | 33.69 | 40.85 | -0.409 | 1965 |
| 08 | weather_plus_trend | gbr_default | 100 | 0.1 | 3 | 1.0 | 1 | 14.75 | 20.67 | 25.93 | 32.00 | 0.136 | 1965 |
| 08 | weather_plus_trend | gbr_tuned | 458 | 0.1 | 2 | 0.8 | 20 | 13.19 | 19.75 | 25.26 | 31.80 | 0.146 | 1965 |
| 08 | trend_residual | gbr_default | 100 | 0.1 | 3 | 1.0 | 1 | 14.82 | 18.88 | 21.81 | 28.35 | 0.321 | 1965 |
| 08 | trend_residual | gbr_tuned | 346 | 0.05 | 4 | 0.8 | 20 | 11.04 | 18.19 | 21.53 | 28.21 | 0.328 | 1965 |

See GRADIENT_BOOSTING.md for method, comparison with Linear Regression, weather groups and limitations. selection.json records every decision, input hashes and package versions. Saved models load from the repository root (they need `scripts/gradient_boosting_model.py`); use only trusted local model files.
