# Linear and Ridge across coverage sets

These follow-up runs keep the original 393-county baseline unchanged. They use the same feature allowlists, train 2000-2016, validation 2017-2020, final test 2021-2025, training-only StandardScaler, and the original Ridge alpha grid. Each set selects its own Ridge alpha using only its own validation rows. The scaling procedure stays fixed, while fitted means and standard deviations appropriately change with the training population.

After generating study sets, splits and features, run:

```powershell
python scripts/run_baselines.py --coverage-set expanded_90
python scripts/run_baselines.py --coverage-set expanded_80
python scripts/run_baselines.py --coverage-set largest_available
python scripts/compare_coverage_baselines.py
```

The runner defaults to `primary_100` for compatibility; it only replaces the selected set's result directory. The commands above do not retrain or replace the published primary models. Outputs are in `results/<coverage_set>_baselines/` and `results/coverage_comparison/`.

| Set | Train county-years | Validation county-years | Test county-years |
|---|---:|---:|---:|
| Primary 100% | 6,681 | 1,572 | 1,965 |
| Expanded 90% | 14,801 | 3,369 | 4,084 |
| Expanded 80% | 21,087 | 4,603 | 5,517 |
| Largest available | 30,108 | 5,751 | 6,891 |

Report both own-population and shared-393-county test results. All models in the shared comparison predict exactly the same 1,965 county-years, with checked target consistency. The comparison script recomputes scores from saved predictions, checks them against each run's original metrics, and saves yearly comparisons and input hashes. Shared-population scores avoid confusing a change in test composition with a change in predictive performance. They do not prove a causal effect of sample size or statistical significance.

The largest set may include test counties absent from training. This is allowed by the agreed population rule and the weather-based predictor recipe, which does not use county ID as a predictor. It differs from the consistent-county primary experiment and must be described as such. No missing targets or missing weather are filled.

Both weather-only and weather-plus-trend variants are retained. Coverage thresholds and the tuning grid were specified before these broader runs. The initial primary test results were already visible, so these follow-up comparisons must not be described as evaluating an entirely new untouched time period. No test scores are used to select Ridge alpha or refit models.
