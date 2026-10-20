# Coverage comparison: Linear and Ridge

Fixed train 2000-2016, validation 2017-2020, test 2021-2025. Units: bushels per acre. No retraining on validation years; no test-based hyperparameter selection. Primary results are preserved.

The same-row comparison evaluates every trained model on the original 393 counties (1,965 county-years). It isolates a common test population, while each model still has its own training scaler and validation-selected Ridge alpha. The own-population comparison changes both training and tested counties; differences are descriptive, not proof that more training data caused better/worse predictions.

## Shared 393-county test population

| Variant | Model | Cutoff | Primary MAE | 90% MAE | 80% MAE | Largest MAE |
|---|---|---|---:|---:|---:|---:|
| weather_only | linear | 05 | 40.28 | 42.78 | 44.67 | 49.11 |
| weather_only | linear | 06 | 40.02 | 42.06 | 43.71 | 47.40 |
| weather_only | linear | 07 | 37.04 | 38.41 | 40.31 | 44.57 |
| weather_only | linear | 08 | 37.40 | 38.69 | 40.66 | 44.87 |
| weather_only | ridge | 05 | 40.28 | 42.78 | 44.67 | 49.96 |
| weather_only | ridge | 06 | 40.01 | 42.07 | 43.72 | 47.76 |
| weather_only | ridge | 07 | 37.19 | 38.48 | 40.35 | 44.68 |
| weather_only | ridge | 08 | 37.53 | 39.06 | 40.89 | 44.97 |
| weather_plus_trend | linear | 05 | 27.00 | 28.81 | 30.04 | 31.48 |
| weather_plus_trend | linear | 06 | 26.05 | 27.50 | 28.72 | 30.20 |
| weather_plus_trend | linear | 07 | 24.75 | 25.86 | 27.29 | 29.23 |
| weather_plus_trend | linear | 08 | 24.82 | 26.20 | 27.86 | 30.15 |
| weather_plus_trend | ridge | 05 | 26.99 | 28.81 | 30.04 | 31.52 |
| weather_plus_trend | ridge | 06 | 26.18 | 27.95 | 29.11 | 30.98 |
| weather_plus_trend | ridge | 07 | 24.77 | 25.85 | 27.40 | 29.53 |
| weather_plus_trend | ridge | 08 | 25.01 | 26.82 | 28.40 | 30.77 |

## Each coverage set on its own test population

| Variant | Model | Cutoff | Primary MAE | 90% MAE | 80% MAE | Largest MAE |
|---|---|---|---:|---:|---:|---:|
| weather_only | linear | 05 | 40.28 | 40.91 | 41.31 | 44.27 |
| weather_only | linear | 06 | 40.02 | 40.44 | 40.63 | 43.41 |
| weather_only | linear | 07 | 37.04 | 36.88 | 37.87 | 41.78 |
| weather_only | linear | 08 | 37.40 | 36.91 | 37.91 | 41.78 |
| weather_only | ridge | 05 | 40.28 | 40.91 | 41.31 | 44.53 |
| weather_only | ridge | 06 | 40.01 | 40.45 | 40.64 | 43.70 |
| weather_only | ridge | 07 | 37.19 | 36.94 | 37.90 | 41.89 |
| weather_only | ridge | 08 | 37.53 | 37.27 | 38.15 | 41.88 |
| weather_plus_trend | linear | 05 | 27.00 | 29.43 | 30.57 | 33.14 |
| weather_plus_trend | linear | 06 | 26.05 | 28.27 | 29.42 | 32.25 |
| weather_plus_trend | linear | 07 | 24.75 | 26.62 | 28.24 | 31.82 |
| weather_plus_trend | linear | 08 | 24.82 | 26.83 | 28.59 | 32.38 |
| weather_plus_trend | ridge | 05 | 26.99 | 29.43 | 30.58 | 33.22 |
| weather_plus_trend | ridge | 06 | 26.18 | 28.58 | 29.66 | 32.66 |
| weather_plus_trend | ridge | 07 | 24.77 | 26.62 | 28.30 | 31.99 |
| weather_plus_trend | ridge | 08 | 25.01 | 27.27 | 28.94 | 32.64 |

All metrics, including RMSE, sample sizes, baseline scores, deltas and yearly results, are in the CSVs. A negative delta indicates lower MAE than the corresponding primary model, not statistical significance. No confidence intervals or extreme-weather subgroup conclusions are claimed. The initial primary test outcomes were already inspected before these planned coverage runs; these comparisons are not a new untouched holdout. Do not select coverage, features or hyperparameters by test results.
