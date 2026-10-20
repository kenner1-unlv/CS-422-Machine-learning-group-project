# Linear and Ridge baselines: primary cohort

The initial run uses 393 complete counties and the shared cutoff features. Both weather-only and weather-plus-trend are reported separately. Linear Regression and Ridge each use a StandardScaler inside the saved model pipeline. The target remains in bushels per acre.

Create a Python 3.12 environment and install `pip install -r requirements-modeling.txt`. After generating features, run `python scripts/run_baselines.py`. Outputs go to `results/primary_100_baselines/`: README results table, metrics, annual metrics, predictions, Ridge tuning, selection decisions, scaler parameters, coefficients, and saved model pipelines. Configuration is in `config/baselines.json`.

Training 2000-2016 supplies all fitted model and scaler parameters. Ridge uses the fixed alpha grid in the configuration and selects by validation MAE on 2017-2020 (RMSE then smaller alpha break ties). Validation data are not added to training. All selection decisions are saved before test metrics are calculated on 2021-2025. Each cutoff has 6,681 training, 1,572 validation, and 1,965 test examples. The training-mean predictor is the common simple reference.

Use the feature manifest's predictor allowlists. A saved pipeline expects its selected numeric feature columns in exactly that order. County FIPS, target, raw year and partition metadata do not enter its predictor matrix. Year-minus-2000 is included only in the named trend variant. Scaling uses training means and population standard deviations; constant columns are handled by StandardScaler. The yield target is not standardized, no data are imputed, and predictions are not clipped.

All held-out results from this run are now visible. Preserve them as the initial baseline. Any later feature changes or tuning must be labeled as a subsequent exploratory experiment; do not repeatedly inspect these same test years while claiming they remain untouched.

Time trend is not a causal measure of climate change. These initial primary-cohort runs do not evaluate extreme-weather groups or other team models. Broader coverage regression runs are now documented in COVERAGE_BASELINE_RUNS.md and results/coverage_comparison/README.md. Monthly/cumulative feature redundancy can destabilize ordinary-regression coefficients; prediction metrics do not establish meaningful individual coefficients. Save and report both feature variants rather than selecting a winner from test error.

The fixed dependency versions record this run's environment; environment metadata and input hashes are also in selection.json. Tests can be run with `python -m unittest discover -s tests -v` after installing the modeling requirements.
