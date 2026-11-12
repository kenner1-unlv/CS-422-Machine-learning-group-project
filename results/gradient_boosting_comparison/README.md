# Gradient Boosting vs Linear Regression: primary 393 counties

All models are scored on the same county-years (checked). Linear/Ridge numbers are recomputed from the team's saved predictions and match the published metrics. MAE/RMSE in bushels per acre. Gradient Boosting = validation-tuned model (`gbr_tuned`).

## Validation 2017-2020 (used for tuning)

| Cutoff | Variant | Linear MAE | Ridge MAE | GB MAE | Linear RMSE | GB RMSE | Linear R² | GB R² | n |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| May | weather_only | 30.32 | 30.32 | 31.29 | 36.59 | 36.44 | -0.420 | -0.408 | 1572 |
| May | weather_plus_trend | 24.30 | 24.30 | 22.93 | 30.02 | 28.47 | 0.044 | 0.141 | 1572 |
| May | trend_residual (exploratory) | - | - | 22.00 | - | 27.39 | - | 0.205 | 1572 |
| June | weather_only | 28.88 | 28.88 | 28.22 | 35.43 | 33.24 | -0.331 | -0.172 | 1572 |
| June | weather_plus_trend | 23.89 | 23.84 | 20.21 | 29.84 | 25.34 | 0.056 | 0.319 | 1572 |
| June | trend_residual (exploratory) | - | - | 19.75 | - | 25.22 | - | 0.325 | 1572 |
| July | weather_only | 30.38 | 30.38 | 26.90 | 36.58 | 32.02 | -0.419 | -0.087 | 1572 |
| July | weather_plus_trend | 23.89 | 23.90 | 19.44 | 29.65 | 24.25 | 0.068 | 0.376 | 1572 |
| July | trend_residual (exploratory) | - | - | 18.38 | - | 23.37 | - | 0.421 | 1572 |
| August | weather_only | 29.78 | 29.73 | 25.40 | 36.02 | 30.42 | -0.376 | 0.019 | 1572 |
| August | weather_plus_trend | 23.90 | 23.86 | 19.75 | 29.85 | 24.72 | 0.055 | 0.352 | 1572 |
| August | trend_residual (exploratory) | - | - | 18.19 | - | 23.30 | - | 0.424 | 1572 |

## Test 2021-2025 (scored once after selection)

| Cutoff | Variant | Linear MAE | Ridge MAE | GB MAE | Linear RMSE | GB RMSE | Linear R² | GB R² | n |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| May | weather_only | 40.28 | 40.28 | 37.75 | 46.00 | 43.11 | -0.787 | -0.569 | 1965 |
| May | weather_plus_trend | 27.00 | 26.99 | 25.90 | 32.98 | 31.77 | 0.081 | 0.148 | 1965 |
| May | trend_residual (exploratory) | - | - | 23.27 | - | 29.67 | - | 0.257 | 1965 |
| June | weather_only | 40.02 | 40.01 | 36.31 | 45.88 | 42.39 | -0.777 | -0.517 | 1965 |
| June | weather_plus_trend | 26.05 | 26.18 | 25.46 | 31.74 | 32.10 | 0.149 | 0.130 | 1965 |
| June | trend_residual (exploratory) | - | - | 22.37 | - | 28.67 | - | 0.306 | 1965 |
| July | weather_only | 37.04 | 37.19 | 33.87 | 42.93 | 41.19 | -0.556 | -0.432 | 1965 |
| July | weather_plus_trend | 24.75 | 24.77 | 25.26 | 31.20 | 32.69 | 0.178 | 0.098 | 1965 |
| July | trend_residual (exploratory) | - | - | 21.79 | - | 28.75 | - | 0.302 | 1965 |
| August | weather_only | 37.40 | 37.53 | 33.69 | 43.25 | 40.85 | -0.579 | -0.409 | 1965 |
| August | weather_plus_trend | 24.82 | 25.01 | 25.26 | 31.28 | 31.80 | 0.174 | 0.146 | 1965 |
| August | trend_residual (exploratory) | - | - | 21.53 | - | 28.21 | - | 0.328 | 1965 |

## Test MAE by weather group (July, weather + trend)

| Group | n | Years | Linear MAE | GB MAE | GB trend_residual MAE | Linear minus normal | GB minus normal |
|---|---:|---:|---:|---:|---:|---:|---:|
| normal | 1261 | 5 | 24.37 | 23.30 | 20.59 | +0.00 | +0.00 |
| extreme_any | 704 | 5 | 25.42 | 28.78 | 23.94 | +1.05 | +5.47 |
| dry | 380 | 5 | 28.16 | 36.02 | 26.77 | +3.79 | +12.71 |
| hot | 158 | 5 | 23.08 | 19.93 | 19.28 | -1.29 | -3.37 |
| wet | 231 | 5 | 22.85 | 20.89 | 21.46 | -1.52 | -2.41 |
| hot_dry | 53 | 4 | 26.24 | 20.78 | 19.92 | +1.87 | -2.52 |

## Dry minus normal test MAE at every cutoff

| Cutoff | Variant | Linear | Gradient Boosting |
|---|---|---:|---:|
| May | weather_only | +6.46 | +6.60 |
| May | weather_plus_trend | +1.82 | +4.31 |
| May | trend_residual | - | +0.32 |
| June | weather_only | +3.62 | +10.55 |
| June | weather_plus_trend | +4.01 | +8.30 |
| June | trend_residual | - | +6.38 |
| July | weather_only | +5.37 | +18.68 |
| July | weather_plus_trend | +3.79 | +12.71 |
| July | trend_residual | - | +6.18 |
| August | weather_only | +7.36 | +21.26 |
| August | weather_plus_trend | +5.61 | +13.41 |
| August | trend_residual | - | +9.37 |

Groups overlap and are exploratory (definitions fixed after the team's overall test scores were visible). Five test years; county-years within a year are correlated. No significance claims. Full numbers: comparison.csv, comparison_by_year.csv, subgroup_comparison.csv. Figures: figures/.
