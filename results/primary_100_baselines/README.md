# Primary cohort regression baselines

393 complete counties; train 2000-2016, validation 2017-2020, test 2021-2025.

Scaling and models fit only training data. Ridge alpha selected by validation MAE. No refit on validation years. Weather-only is the core comparison; time trend is a named secondary variant. MAE and RMSE are in bushels per acre.

| Cutoff | Variant | Model | Alpha | Validation MAE | Test MAE | Test RMSE | Test n |
|---|---|---|---:|---:|---:|---:|---:|
| 05 | reference | training_mean | - | 35.02 | 42.29 | 48.02 | 1965 |
| 05 | weather_only | linear | - | 30.32 | 40.28 | 46.00 | 1965 |
| 05 | weather_only | ridge | 0.001 | 30.32 | 40.28 | 46.01 | 1965 |
| 05 | weather_plus_trend | linear | - | 24.30 | 27.00 | 32.98 | 1965 |
| 05 | weather_plus_trend | ridge | 0.01 | 24.30 | 26.99 | 32.98 | 1965 |
| 06 | reference | training_mean | - | 35.02 | 42.29 | 48.02 | 1965 |
| 06 | weather_only | linear | - | 28.88 | 40.02 | 45.88 | 1965 |
| 06 | weather_only | ridge | 0.01 | 28.88 | 40.01 | 45.88 | 1965 |
| 06 | weather_plus_trend | linear | - | 23.89 | 26.05 | 31.74 | 1965 |
| 06 | weather_plus_trend | ridge | 10 | 23.84 | 26.18 | 31.85 | 1965 |
| 07 | reference | training_mean | - | 35.02 | 42.29 | 48.02 | 1965 |
| 07 | weather_only | linear | - | 30.38 | 37.04 | 42.93 | 1965 |
| 07 | weather_only | ridge | 10 | 30.38 | 37.19 | 43.10 | 1965 |
| 07 | weather_plus_trend | linear | - | 23.89 | 24.75 | 31.20 | 1965 |
| 07 | weather_plus_trend | ridge | 1 | 23.90 | 24.77 | 31.22 | 1965 |
| 08 | reference | training_mean | - | 35.02 | 42.29 | 48.02 | 1965 |
| 08 | weather_only | linear | - | 29.78 | 37.40 | 43.25 | 1965 |
| 08 | weather_only | ridge | 10 | 29.73 | 37.53 | 43.38 | 1965 |
| 08 | weather_plus_trend | linear | - | 23.90 | 24.82 | 31.28 | 1965 |
| 08 | weather_plus_trend | ridge | 10 | 23.86 | 25.01 | 31.37 | 1965 |

These are initial results, not extreme-weather subgroup results. County-level errors within the same year are correlated. Overlapping monthly/cumulative predictors can make linear coefficients unstable; interpret predictive scores rather than causal coefficients. Predictions are not clipped to zero. Do not use these test results to retune or redefine features and still describe this test as untouched.

selection.json records validation decisions, input hashes and environment versions. Other files retain full precision, annual metrics, predictions, scaling parameters and coefficients. Saved model pipelines include their fitted scalers; use only trusted local model files.
