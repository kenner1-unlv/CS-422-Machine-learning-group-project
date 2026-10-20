# Forecast features: first reproducible version

Use the same recipe for all four coverage sets and all algorithms. Start model comparisons with the 393-county primary cohort. There are separate tables for end-of-May, June, July, and August forecasts. No feature uses weather after its cutoff.

## Feature groups

1. **Preseason, January-March:** total precipitation (mm), calendar-day-weighted mean temperature (C), and the lowest daily county-average minimum temperature (C).
2. **Individual months, April through the cutoff:** precipitation total; mean average, maximum, and minimum temperature; highest daily county-average maximum temperature; lowest daily county-average minimum temperature. Six values per month.
3. **Season to date, April through the cutoff:** precipitation total; day-weighted mean average, maximum, and minimum temperature; highest daily county-average maximum temperature; lowest daily county-average minimum temperature. Six cumulative values.
4. **Optional time trend:** year minus 2000. This is available at forecast time. Compare weather-only and weather-plus-trend variants explicitly; do not assume adding it resolves climate or agricultural changes.

April is a common calendar window, not an assertion about each county's planting date. It keeps the protocol consistent across locations; planting-date or regional windows are possible later extensions. The January-March group retains early-year conditions without making each winter month an individual feature.

| Forecast | Monthly window | Weather predictors | With time trend |
|---|---|---:|---:|
| End of May | April-May | 21 | 22 |
| End of June | April-June | 27 | 28 |
| End of July | April-July | 33 | 34 |
| End of August | April-August | 39 | 40 |

Temperature averages are weighted by actual calendar days, including leap years. Monthly source summaries are already rounded, so aggregated features are approximations to averages calculated directly from the original daily values. Extremes describe NOAA county averages, not the hottest/coldest individual field or station.

Monthly and cumulative features overlap. Ridge can address correlated predictors; ordinary linear-regression coefficients may be unstable. Use validation years to compare feature variants; do not interpret coefficients as causal effects. More features and later cutoffs do not guarantee lower test error.

## Reproduce and train

Run `python scripts/build_features.py` after `build_study_sets.py` and `build_splits.py`. Outputs are in `data/features/<coverage_set>/cutoff_05.csv` through `cutoff_08.csv`. `data/features/feature_manifest.json` contains exact predictor allowlists for each cutoff and variant, partition counts, and configuration hashes.

**Only columns in the chosen predictor allowlist enter the model.** `yield_bu_per_acre` is the target. County FIPS, year, cutoff month, and partition are metadata; county identifiers must not be treated as numeric predictors. The optional trend has its own explicit feature column. Do not infer predictor columns by simply dropping the target.

Fit a separate model for each cutoff, keeping the existing train 2000-2016, validation 2017-2020, test 2021-2025 assignments. All four forecasts for a county-year stay in the same partition. Use weather-only as the shared core comparison and weather-plus-trend as a named secondary variant across algorithms. Any decision to prefer a variant must use validation data only. Fit scaling and any other learned preprocessing on training data only. Weather tables are complete, so this initial recipe needs no imputation.

No learned anomaly thresholds, county target encodings, lagged yields, or outcome-based county features are included in version 1. No targets are used in feature construction. Historical yield and geographic effects need separately defined, leakage-safe variants.

## Later daily-weather extension

Heat-day counts, growing-degree days, frost counts, and consecutive dry days must be calculated from daily weather with documented thresholds. Monthly extremes and totals cannot reconstruct them. Add these in a separate version once raw daily files and definitions are shared. Anomaly baselines must use training information only; fitting them over the full 2000-2025 period would use held-out information.

These retrospective weather sources include revisions; a cutoff restriction prevents future-date weather from entering features but does not establish that the final revised values were available in real time.
