# Neural Network Regression

Lester Iwuajoku's [PR #16](https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/pull/16), commit `4ac9f596901f9b93a0e1f23b7464cddf90d33ce8`, provides the Neural Network used in the primary team comparison. It replaces the temporary backup because it is the model assigned to Lester, not because of the held-out ranking. Integration reused his saved predictions without fitting another model.

## Method

For each May through August cutoff, the script uses the shared `primary_100` county cohort and manifest feature lists: weather only and weather plus `year_since_2000`. The model is a scikit-learn `MLPRegressor` with one 32-unit ReLU hidden layer, seed 42 and a 500-iteration limit. Other estimator settings use the library defaults. The pipeline fits its feature StandardScaler and the regressor only on 2000–2016 rows; the yield target remains in bushels per acre. Validation is 2017–2020, and test is 2021–2025. The script does not tune architecture or refit on validation. All eight runs reached 500 iterations and warnings were suppressed, so convergence was not established. The original package versions were not recorded.

## Primary-cohort scores

Pooled MAE and RMSE weigh each county-year equally and are in bu/acre. Test scores were independently recomputed from 1,965 saved predictions per run and checked against the shared county/year keys and observed yields. Validation MAE and RMSE are Lester's reported summaries for the shared 1,572-row partition, not independently recalculated; no validation predictions were supplied.

| Cutoff | Inputs | Validation MAE | Test MAE | Test RMSE |
|---|---|---:|---:|---:|
| May | Weather | 33.26 | 38.59 | 44.57 |
| May | Weather + trend | 27.05 | 28.91 | 37.34 |
| June | Weather | 27.78 | 38.78 | 45.40 |
| June | Weather + trend | 24.49 | 29.58 | 37.49 |
| July | Weather | 25.43 | 32.19 | 39.23 |
| July | Weather + trend | 22.82 | 23.73 | 30.96 |
| August | Weather | 23.49 | 31.92 | 39.67 |
| August | Weather + trend | 21.16 | 22.95 | 29.84 |

Adding trend lowers this model's test MAE at every cutoff. It leads standard-model test MAE at July and August for both feature lists, whereas Gradient Boosting leads validation MAE for the trend variant at every cutoff. These are results for the fixed 393 counties and five test years, not evidence of universal or statistically significant superiority.

## Audit and source

The [authored script](scripts/neural_network_model.py) and [source result files](results/neural_network/) are retained; a redundant August export with missing county-ID zero padding is omitted. [Canonical NN results](results/primary_100_neural_network/) feed the [common comparison](results/team_model_comparison/README.md). Use `python scripts/import_lester_neural_network.py` to rebuild the normalized NN outputs and `python scripts/verify_final_results.py` to audit the saved results without retraining. Running the original authored script will fit fresh models, so use a disposable checkout if deliberately reproducing training. Without the original software versions a fresh fit does not establish identity with the saved run.
