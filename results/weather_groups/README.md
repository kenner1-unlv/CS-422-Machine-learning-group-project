# Exploratory weather-group analysis

Thresholds use only county-specific weather observed in training years 2000-2016 from the largest coverage set. Same thresholds apply to every coverage stage. At least 10 training years are required. Hot: April-to-cutoff mean daily maximum temperature above the county training 90th percentile. Dry/wet: April-to-cutoff precipitation below the 10th / above the 90th percentile. Comparisons are strict; quantiles use linear interpolation.

These are statistical weather groups, not official drought, flood or heat-wave declarations. Groups reflect weather through each forecast cutoff, so memberships change across cutoffs. Hot can overlap dry or wet. Normal has none of these flags; unclassified lacks sufficient training history and is not treated as normal. All = normal + extreme_any + unclassified. Original predictions and models are unchanged.

Subgroup definitions were chosen after overall test results were visible; this is exploratory follow-up, not a predeclared untouched test. The 17-year reference is short and quantile estimates are uncertain. Counties and years are correlated; five test years do not supply thousands of independent weather events. No significance or causal claims are made. Sample warnings flag fewer than 30 county-years or fewer than three represented years.

## Common 393-county test rows

Linear and Ridge with year trend, July cutoff (all other variants/cutoffs are in the CSVs). MAE units: bushels per acre.

| Training set | Group | n | Years | Linear MAE | Ridge MAE |
|---|---|---:|---:|---:|---:|
| primary_100 | normal | 1261 | 5 | 24.37 | 24.41 |
| primary_100 | extreme_any | 704 | 5 | 25.42 | 25.42 |
| primary_100 | hot | 158 | 5 | 23.08 | 23.11 |
| primary_100 | dry | 380 | 5 | 28.16 | 28.25 |
| primary_100 | wet | 231 | 5 | 22.85 | 22.70 |
| primary_100 | hot_dry | 53 | 4 | 26.24 | 26.37 |
| expanded_90 | normal | 1261 | 5 | 25.57 | 25.57 |
| expanded_90 | extreme_any | 704 | 5 | 26.38 | 26.36 |
| expanded_90 | hot | 158 | 5 | 23.15 | 23.13 |
| expanded_90 | dry | 380 | 5 | 29.95 | 29.93 |
| expanded_90 | wet | 231 | 5 | 22.84 | 22.82 |
| expanded_90 | hot_dry | 53 | 4 | 26.40 | 26.38 |
| expanded_80 | normal | 1261 | 5 | 27.12 | 27.25 |
| expanded_80 | extreme_any | 704 | 5 | 27.61 | 27.66 |
| expanded_80 | hot | 158 | 5 | 23.97 | 23.98 |
| expanded_80 | dry | 380 | 5 | 31.75 | 31.84 |
| expanded_80 | wet | 231 | 5 | 23.35 | 23.35 |
| expanded_80 | hot_dry | 53 | 4 | 27.63 | 27.59 |
| largest_available | normal | 1261 | 5 | 29.44 | 29.76 |
| largest_available | extreme_any | 704 | 5 | 28.85 | 29.11 |
| largest_available | hot | 158 | 5 | 25.61 | 25.68 |
| largest_available | dry | 380 | 5 | 32.86 | 33.21 |
| largest_available | wet | 231 | 5 | 25.04 | 25.19 |
| largest_available | hot_dry | 53 | 4 | 31.55 | 31.52 |

## Each set on its own test rows

Linear and Ridge with year trend, July cutoff (all other variants/cutoffs are in the CSVs). MAE units: bushels per acre.

| Training set | Group | n | Years | Linear MAE | Ridge MAE |
|---|---|---:|---:|---:|---:|
| primary_100 | normal | 1261 | 5 | 24.37 | 24.41 |
| primary_100 | extreme_any | 704 | 5 | 25.42 | 25.42 |
| primary_100 | hot | 158 | 5 | 23.08 | 23.11 |
| primary_100 | dry | 380 | 5 | 28.16 | 28.25 |
| primary_100 | wet | 231 | 5 | 22.85 | 22.70 |
| primary_100 | hot_dry | 53 | 4 | 26.24 | 26.37 |
| expanded_90 | normal | 2639 | 5 | 26.22 | 26.22 |
| expanded_90 | extreme_any | 1445 | 5 | 27.35 | 27.34 |
| expanded_90 | hot | 327 | 5 | 24.87 | 24.87 |
| expanded_90 | dry | 795 | 5 | 31.46 | 31.44 |
| expanded_90 | wet | 466 | 5 | 22.91 | 22.89 |
| expanded_90 | hot_dry | 121 | 4 | 31.67 | 31.65 |
| expanded_80 | normal | 3592 | 5 | 27.52 | 27.60 |
| expanded_80 | extreme_any | 1925 | 5 | 29.58 | 29.63 |
| expanded_80 | hot | 473 | 5 | 29.14 | 29.18 |
| expanded_80 | dry | 1036 | 5 | 34.24 | 34.36 |
| expanded_80 | wet | 625 | 5 | 24.21 | 24.15 |
| expanded_80 | hot_dry | 176 | 5 | 38.20 | 38.25 |
| largest_available | normal | 4238 | 5 | 30.70 | 30.89 |
| largest_available | extreme_any | 2251 | 5 | 32.26 | 32.45 |
| largest_available | hot | 590 | 5 | 33.83 | 33.85 |
| largest_available | dry | 1177 | 5 | 36.46 | 36.83 |
| largest_available | wet | 744 | 5 | 27.47 | 27.49 |
| largest_available | hot_dry | 218 | 5 | 44.15 | 44.25 |
| largest_available | unclassified | 402 | 5 | 41.14 | 40.98 |

Absent groups have zero observations and no defined score; they are omitted rather than reported as zero error. CSVs include validation and test, weather-only and trend variants, the mean baseline, all four cutoffs, bias, RMSE, differences from normal, sample sizes and yearly metrics. Unknown groups remain in overall performance but are excluded from normal/extreme comparisons.

Own-population scores change evaluated counties. Shared-row results keep the primary population fixed. Lower subgroup MAE than normal is possible and does not mean weather improves yield or that the group has been mislabeled. Different groups differ in county/year composition and yield distribution. Small/rare groups require cautious interpretation.
