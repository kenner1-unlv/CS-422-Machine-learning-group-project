# largest_available regression baselines

Train 2000-2016, validation 2017-2020, test 2021-2025.

Scaling and models fit only training data. Ridge alpha selected by validation MAE. No refit on validation years. Weather-only is the core comparison; time trend is a named secondary variant. MAE and RMSE are in bushels per acre.

| Cutoff | Variant | Model | Alpha | Validation MAE | Test MAE | Test RMSE | Test n |
|---|---|---|---:|---:|---:|---:|---:|
| 05 | reference | training_mean | - | 39.62 | 45.02 | 52.11 | 6891 |
| 05 | weather_only | linear | - | 38.20 | 44.27 | 51.44 | 6891 |
| 05 | weather_only | ridge | 10000 | 37.70 | 44.53 | 51.53 | 6891 |
| 05 | weather_plus_trend | linear | - | 30.23 | 33.14 | 40.70 | 6891 |
| 05 | weather_plus_trend | ridge | 1000 | 29.89 | 33.22 | 40.80 | 6891 |
| 06 | reference | training_mean | - | 39.62 | 45.02 | 52.11 | 6891 |
| 06 | weather_only | linear | - | 36.58 | 43.41 | 50.62 | 6891 |
| 06 | weather_only | ridge | 1000 | 36.51 | 43.70 | 50.89 | 6891 |
| 06 | weather_plus_trend | linear | - | 29.54 | 32.25 | 39.89 | 6891 |
| 06 | weather_plus_trend | ridge | 1000 | 29.38 | 32.66 | 40.16 | 6891 |
| 07 | reference | training_mean | - | 39.62 | 45.02 | 52.11 | 6891 |
| 07 | weather_only | linear | - | 37.46 | 41.78 | 49.43 | 6891 |
| 07 | weather_only | ridge | 100 | 37.43 | 41.89 | 49.53 | 6891 |
| 07 | weather_plus_trend | linear | - | 29.87 | 31.82 | 39.59 | 6891 |
| 07 | weather_plus_trend | ridge | 100 | 29.85 | 31.99 | 39.70 | 6891 |
| 08 | reference | training_mean | - | 39.62 | 45.02 | 52.11 | 6891 |
| 08 | weather_only | linear | - | 35.88 | 41.78 | 49.59 | 6891 |
| 08 | weather_only | ridge | 100 | 35.81 | 41.88 | 49.68 | 6891 |
| 08 | weather_plus_trend | linear | - | 29.64 | 32.38 | 40.20 | 6891 |
| 08 | weather_plus_trend | ridge | 1000 | 29.47 | 32.64 | 40.25 | 6891 |

These are initial results, not extreme-weather subgroup results. County-level errors within the same year are correlated. Overlapping monthly/cumulative predictors can make linear coefficients unstable; interpret predictive scores rather than causal coefficients. Predictions are not clipped to zero. Do not use these test results to retune or redefine features and still describe this test as untouched.

selection.json records validation decisions, input hashes and environment versions. Other files retain full precision, annual metrics, predictions, scaling parameters and coefficients. Saved model pipelines include their fitted scalers; use only trusted local model files.
