# Random Forest Regression — primary cohort

## Method and reproducibility

The model uses the primary 393 complete counties and the same observed county-year rows as Linear, Ridge and Gradient Boosting: 6,681 training rows (2000–2016), 1,572 validation rows (2017–2020), and 1,965 test rows (2021–2025) at each May–August cutoff. A separate forest is fit for every cutoff and for each shared predictor allowlist, `weather_only` and `weather_plus_trend`, from [FEATURE_PLAN.md](FEATURE_PLAN.md). County ID, raw year, cutoff, partition and yield are excluded from predictors; the secondary variant contains the explicitly allowed `year_since_2000`. The complete weather tables need no imputation. Forests use the original feature units, without learned scaling.

Each fit uses scikit-learn `RandomForestRegressor`, 150 trees, bootstrap sampling, `max_features=0.7`, seed 42, and four CPU workers. The small fixed validation grid crosses maximum depth 12 or unrestricted with minimum leaf size 5 or 20. The choice for each cutoff/variant minimizes validation MAE, then RMSE, then candidate order. Only training rows fit a model; validation rows select settings; selected models are not refit. [selection.json](results/primary_100_random_forest/selection.json) records each choice, predictor list, input hashes and package versions before test scoring. The regenerated feature hashes exactly match the earlier Gradient Boosting run. The test scores did not inform this model's settings.

Run from this folder after generating the shared feature tables:

```powershell
py -3.13 scripts/run_remaining_models.py random_forest
```

The [tuning table](results/primary_100_random_forest/tuning.csv), [compressed row predictions](results/primary_100_random_forest/predictions.csv.gz), [overall metrics](results/primary_100_random_forest/metrics.csv), [yearly metrics](results/primary_100_random_forest/metrics_by_year.csv), [weather-group metrics](results/primary_100_random_forest/subgroup_metrics.csv), and fitted models are reproducible outputs. Scikit-learn 1.9.0, NumPy 2.2.6 and pandas 3.1.0 were used in this run; see the selection file for the full environment. MAE and RMSE are bushels per acre.

## Results

| Cutoff | Variant | Chosen depth | Chosen minimum leaf | Validation MAE | Test MAE | Test RMSE |
|---|---|---:|---:|---:|---:|---:|
| May | Weather only | 12 | 20 | 32.91 | 36.96 | 42.54 |
| June | Weather only | 12 | 20 | 28.56 | 35.77 | 41.85 |
| July | Weather only | Unrestricted | 5 | 27.34 | 34.37 | 40.98 |
| August | Weather only | Unrestricted | 5 | 26.84 | 34.67 | 41.03 |
| May | Weather plus trend | Unrestricted | 20 | 24.33 | 26.09 | 31.56 |
| June | Weather plus trend | 12 | 20 | 20.79 | 25.47 | 31.84 |
| July | Weather plus trend | 12 | 20 | 20.60 | 26.01 | 32.56 |
| August | Weather plus trend | 12 | 20 | 20.89 | 25.89 | 31.89 |

All test rows above have `n=1,965`. Weather-only Random Forest has lower test MAE than Linear in all four cutoffs (for example, May 36.96 versus 40.28), but Gradient Boosting is lower in July and August. Adding the allowed year trend substantially lowers Forest test MAE, yet July Forest MAE 26.01 trails Linear's 24.75. The July Forest also underpredicts by 15.08 bu/acre on average; a forest cannot extrapolate a numeric year trend beyond values seen in training.

The July weather-plus-trend Forest MAE in 2023 is 35.74 versus 29.08 for Linear and 40.36 for Gradient Boosting. With the existing exploratory weather labels, July Forest MAE is 25.30 on 1,261 normal rows and 31.54 on 380 dry rows. Those groups overlap other flags and were defined after earlier overall test results were visible. They are descriptive slices, not evidence of a general drought ranking. The [team comparison](results/team_model_comparison/README.md) gives all model scores on identical rows.

## Limits

Only the primary complete-county cohort was modeled. Five test years and correlated counties give much less independent evidence than the row count suggests. Revised retrospective weather inputs, missing management and soil information, and tree trend extrapolation limits constrain real-time or future-year claims. This fixed grid is a compact comparison, not an exhaustive search or a statistical significance study.

## Reproduction and contributor evidence

Tylie Anderson reproduced the assigned Random Forest experiment on Mac in [authored commit bd92250](https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/commit/bd9225064552899174a278a658eaceef7568a489). The run uses the existing shared implementation introduced by Russell Kennedy, preserving that source attribution. Her artifacts contain eight fitted pipelines, 81,744 row predictions across training/validation/test, the same four-candidate search, and overall, yearly and subgroup summaries.

All row keys and observed targets match the preceding run. The maximum absolute prediction difference is 8.53 × 10⁻¹⁴ bu/acre; the largest pooled metric difference is 7.11 × 10⁻¹⁵. Published two-decimal scores, chosen settings and rankings are unchanged. This reproduces one seed across platforms and does not establish multi-seed variability or performance on new data. No fitted joblib model was loaded during this artifact audit.

Her selection record reports Python 3.13.0, NumPy 2.2.6, pandas 3.1.0 and scikit-learn 1.9.0. The split-config hash matches LF-normalized bytes. Feature-input hashes and predictor lists match the preceding run, but the regenerated local manifest hash differs from her recorded manifest hash; the original manifest bytes were not included in the bundle, so exact manifest-byte reproduction remains unverified. The frozen-row verifier passes with her published result files.
