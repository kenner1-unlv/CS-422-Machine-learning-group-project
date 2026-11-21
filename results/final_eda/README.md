# Fixed-cohort exploratory diagnostics

Rebuild without fitting models or editing standard predictions from the `Project` root:

```powershell
py -3.13 scripts/final_eda.py
```

The script uses tracked processed yield data, generated `primary_100` study sets and July feature table, and existing frozen prediction files. The primary cohort, 2000–2016 training, 2017–2020 validation, 2021–2025 test, and fixed feature lists are unchanged. All weather–yield and feature-correlation diagnostics below use **training rows only**. Test prediction diagnostics are **descriptive follow-up analysis after test outcomes were visible**, not a new validation or model-selection step. County rows within a year are correlated.

| Figure | Caption and numerical source |
|---|---|
| `yield_distribution.png` | Density of county yield by chronological partition on the fixed 393-county cohort. It shows overlap, a higher later-period center, and extreme tails without changing the cohort. `yield_distribution.csv` records n, quartiles, range, mean and SD. |
| `yield_trend.png` | Annual mean and median yield, 2000–2025, with train/validation/test boundaries. It displays the temporal shift motivating the year-trend comparator but cannot identify its cause. `annual_yield.csv` contains yearly values. |
| `state_coverage.png` | Primary-cohort county counts by state and their share of counties with **any** reported yield during 2000–2025. The denominator does not require complete weather, so the chart describes selection from yield-reporting counties, not national corn acreage. `state_coverage.csv` contains counts and shares. |
| `training_weather_distributions.png` | April–July precipitation and mean-temperature histograms over training county-years only. They show the variable ranges used for descriptive analysis; county-years are not independent weather events. `training_weather_summary.csv` has percentiles and tails. |
| `training_weather_yield.png` | Training-only pooled hexbin plots of yield against April–July precipitation and temperature. These unadjusted associations are confounded by region, time, and management and are not causal effects. `training_correlations.csv` gives selected Pearson correlations. |
| `training_feature_correlations.png` | Training-only Pearson correlation matrix for selected monthly, cumulative, and year features. It makes redundancy among engineered weather summaries visible. `training_feature_correlation_matrix.csv` and `top_feature_correlations.csv` retain full numerical detail. The fixed model feature lists were not changed in response. |
| `july_test_residuals.png` | Observed versus predicted yield and predicted-minus-observed error distributions for four saved standard families on identical July weather-plus-trend test rows. The one-to-one line and zero-error reference expose tail misses and bias. This is post-test descriptive analysis. `july_high_error_examples.csv` lists the largest absolute misses per family for grounded case interpretation. |

Existing figures remain under `results/team_model_comparison/`, `results/gradient_boosting_comparison/figures/`, and `results/supplemental_figures/`. Those already cover error by cutoff/year, weather subgroup, ensemble, and Gradient Boosting-specific residuals. This suite adds only missing shared-data and common-row diagnostics.
