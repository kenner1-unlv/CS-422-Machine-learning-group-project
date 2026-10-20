# expanded_80 regression baselines

Train 2000-2016, validation 2017-2020, test 2021-2025.

Scaling and models fit only training data. Ridge alpha selected by validation MAE. No refit on validation years. Weather-only is the core comparison; time trend is a named secondary variant. MAE and RMSE are in bushels per acre.

| Cutoff | Variant | Model | Alpha | Validation MAE | Test MAE | Test RMSE | Test n |
|---|---|---|---:|---:|---:|---:|---:|
| 05 | reference | training_mean | - | 36.50 | 42.06 | 48.65 | 5517 |
| 05 | weather_only | linear | - | 33.13 | 41.31 | 47.74 | 5517 |
| 05 | weather_only | ridge | 0.1 | 33.13 | 41.31 | 47.73 | 5517 |
| 05 | weather_plus_trend | linear | - | 26.68 | 30.57 | 37.25 | 5517 |
| 05 | weather_plus_trend | ridge | 0.001 | 26.68 | 30.58 | 37.25 | 5517 |
| 06 | reference | training_mean | - | 36.50 | 42.06 | 48.65 | 5517 |
| 06 | weather_only | linear | - | 32.12 | 40.63 | 47.21 | 5517 |
| 06 | weather_only | ridge | 10 | 32.12 | 40.64 | 47.21 | 5517 |
| 06 | weather_plus_trend | linear | - | 26.39 | 29.42 | 36.15 | 5517 |
| 06 | weather_plus_trend | ridge | 100 | 26.33 | 29.66 | 36.32 | 5517 |
| 07 | reference | training_mean | - | 36.50 | 42.06 | 48.65 | 5517 |
| 07 | weather_only | linear | - | 33.81 | 37.87 | 44.75 | 5517 |
| 07 | weather_only | ridge | 10 | 33.79 | 37.90 | 44.79 | 5517 |
| 07 | weather_plus_trend | linear | - | 27.00 | 28.24 | 35.31 | 5517 |
| 07 | weather_plus_trend | ridge | 10 | 27.00 | 28.30 | 35.36 | 5517 |
| 08 | reference | training_mean | - | 36.50 | 42.06 | 48.65 | 5517 |
| 08 | weather_only | linear | - | 32.64 | 37.91 | 44.87 | 5517 |
| 08 | weather_only | ridge | 100 | 32.54 | 38.15 | 45.13 | 5517 |
| 08 | weather_plus_trend | linear | - | 27.00 | 28.59 | 35.69 | 5517 |
| 08 | weather_plus_trend | ridge | 100 | 26.92 | 28.94 | 35.94 | 5517 |

These are initial results, not extreme-weather subgroup results. County-level errors within the same year are correlated. Overlapping monthly/cumulative predictors can make linear coefficients unstable; interpret predictive scores rather than causal coefficients. Predictions are not clipped to zero. Do not use these test results to retune or redefine features and still describe this test as untouched.

selection.json records validation decisions, input hashes and environment versions. Other files retain full precision, annual metrics, predictions, scaling parameters and coefficients. Saved model pipelines include their fitted scalers; use only trusted local model files.
