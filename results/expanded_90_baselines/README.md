# expanded_90 regression baselines

Train 2000-2016, validation 2017-2020, test 2021-2025.

Scaling and models fit only training data. Ridge alpha selected by validation MAE. No refit on validation years. Weather-only is the core comparison; time trend is a named secondary variant. MAE and RMSE are in bushels per acre.

| Cutoff | Variant | Model | Alpha | Validation MAE | Test MAE | Test RMSE | Test n |
|---|---|---|---:|---:|---:|---:|---:|
| 05 | reference | training_mean | - | 35.97 | 41.94 | 48.17 | 4084 |
| 05 | weather_only | linear | - | 31.73 | 40.91 | 46.91 | 4084 |
| 05 | weather_only | ridge | 0.001 | 31.73 | 40.91 | 46.91 | 4084 |
| 05 | weather_plus_trend | linear | - | 25.61 | 29.43 | 35.86 | 4084 |
| 05 | weather_plus_trend | ridge | 0.001 | 25.61 | 29.43 | 35.86 | 4084 |
| 06 | reference | training_mean | - | 35.97 | 41.94 | 48.17 | 4084 |
| 06 | weather_only | linear | - | 30.52 | 40.44 | 46.55 | 4084 |
| 06 | weather_only | ridge | 0.001 | 30.52 | 40.45 | 46.55 | 4084 |
| 06 | weather_plus_trend | linear | - | 25.29 | 28.27 | 34.66 | 4084 |
| 06 | weather_plus_trend | ridge | 100 | 25.24 | 28.58 | 34.86 | 4084 |
| 07 | reference | training_mean | - | 35.97 | 41.94 | 48.17 | 4084 |
| 07 | weather_only | linear | - | 32.01 | 36.88 | 43.23 | 4084 |
| 07 | weather_only | ridge | 10 | 32.00 | 36.94 | 43.28 | 4084 |
| 07 | weather_plus_trend | linear | - | 25.39 | 26.62 | 33.44 | 4084 |
| 07 | weather_plus_trend | ridge | 0.001 | 25.40 | 26.62 | 33.44 | 4084 |
| 08 | reference | training_mean | - | 35.97 | 41.94 | 48.17 | 4084 |
| 08 | weather_only | linear | - | 30.94 | 36.91 | 43.27 | 4084 |
| 08 | weather_only | ridge | 100 | 30.89 | 37.27 | 43.67 | 4084 |
| 08 | weather_plus_trend | linear | - | 25.39 | 26.83 | 33.58 | 4084 |
| 08 | weather_plus_trend | ridge | 100 | 25.34 | 27.27 | 33.85 | 4084 |

These are initial results, not extreme-weather subgroup results. County-level errors within the same year are correlated. Overlapping monthly/cumulative predictors can make linear coefficients unstable; interpret predictive scores rather than causal coefficients. Predictions are not clipped to zero. Do not use these test results to retune or redefine features and still describe this test as untouched.

selection.json records validation decisions, input hashes and environment versions. Other files retain full precision, annual metrics, predictions, scaling parameters and coefficients. Saved model pipelines include their fitted scalers; use only trusted local model files.
