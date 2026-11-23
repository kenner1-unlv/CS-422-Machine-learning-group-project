# Neural Network Model — CS 422

Lester Iwuajoku's [PR #16](https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/pull/16), commit `4ac9f596901f9b93a0e1f23b7464cddf90d33ce8`, provides the Neural Network used in the primary team comparison. It replaces the temporary backup because it is the model assigned to Lester, not because of the held-out ranking. Integration reused his saved predictions without fitting another model.

## 1. Overview

This project uses a neural network to predict U.S. county-level corn yields (bushels per acre) using weather data and a calendar-year trend feature.

## 2. Dataset

The model uses the `primary_100` dataset containing 393 counties and 10,218 county-year observations from 2000–2025.

Data is split chronologically:

| Partition | Years | Observations | Share |
|---|---|---:|---:|
| Training | 2000–2016 | 6,681 | 65.38% |
| Validation | 2017–2020 | 1,572 | 15.38% |
| Testing | 2021–2025 | 1,965 | 19.23% |

Two feature configurations are evaluated:

- `weather_only`: Weather measurements and seasonal summaries.
- `weather_plus_trend`: Weather features plus `year_since_2000`.

Predictions are evaluated at four seasonal cutoffs: May, June, July, and August.

## 3. Neural Network Architecture

The model uses scikit-learn's `MLPRegressor`.

| Parameter | Value |
|---|---|
| Hidden layers | 1 |
| Neurons | 32 |
| Activation | ReLU |
| Optimizer | Adam |
| Maximum iterations | 500 |
| Random seed | 42 |
| Feature scaling | StandardScaler |

The model is implemented using a scikit-learn pipeline that fits `StandardScaler` on training data and applies the same transformation to validation and test data.

## 4. Training and Evaluation

Eight configurations were evaluated using four cutoff months and two feature sets.

Validation mean absolute error (MAE) was used to compare the eight fixed configurations; no architecture or hyperparameter search was performed. Root mean squared error (RMSE) was also reported. The script does not refit on validation data.

The test partition was reserved for final evaluation.

## 5. Results

Pooled MAE and RMSE weigh each county-year equally and are in bu/acre. Test scores were independently recomputed from 1,965 saved predictions per run and checked against the shared county/year keys and observed yields. Validation MAE and RMSE are Lester's reported summaries for the shared 1,572-row partition, not independently recalculated; no validation predictions were supplied.

| Cutoff | Features | Validation MAE | Test MAE | Test RMSE |
|---|---|---:|---:|---:|
| May | Weather only | 33.26 | 38.59 | 44.57 |
| May | Weather + trend | 27.05 | 28.91 | 37.34 |
| June | Weather only | 27.78 | 38.78 | 45.40 |
| June | Weather + trend | 24.49 | 29.58 | 37.49 |
| July | Weather only | 25.43 | 32.19 | 39.23 |
| July | Weather + trend | 22.82 | 23.73 | 30.96 |
| August | Weather only | 23.49 | 31.92 | 39.67 |
| August | Weather + trend | **21.16** | **22.95** | **29.84** |

All error values are measured in bushels per acre.

**Best configuration:** August weather + trend, with a test MAE of 22.95 and RMSE of 29.84.

## 6. Limitations

- All eight models reached the 500-iteration training limit, so convergence was not confirmed.
- The architecture was fixed rather than optimized through hyperparameter tuning.
- Convergence warnings were suppressed, and the original software versions were not recorded. A fresh fit does not establish identity with the saved run.
- Some unusually low-yield observations were substantially overestimated.
- Results may not generalize equally well to counties excluded from the primary dataset.

## 7. How to Run

To deliberately train fresh models, use a disposable checkout with generated feature tables and the required dependencies. From that project root, execute:

```powershell
python scripts/neural_network_model.py
```

The script evaluates the neural network configurations and saves results under `results/neural_network/`.

## 8. Conclusion

The August weather + trend configuration achieved the lowest validation MAE and the best test performance among the eight neural network configurations.

Adding the calendar-year trend feature generally improved prediction accuracy. Future improvements could include convergence testing, hyperparameter tuning, and additional analysis of large prediction errors.

Adding trend lowers this model's test MAE at every cutoff. It leads standard-model test MAE at July and August for both feature lists, whereas Gradient Boosting leads validation MAE for the trend variant at every cutoff. These are results for the fixed 393 counties and five test years, not evidence of universal or statistically significant superiority.

## 9. Audit and Source

The [authored script](scripts/neural_network_model.py) and [source result files](results/neural_network/) are retained; a redundant August export with missing county-ID zero padding is omitted. [Canonical NN results](results/primary_100_neural_network/) feed the [common comparison](results/team_model_comparison/README.md). Use `python scripts/import_lester_neural_network.py` to rebuild the normalized NN outputs and `python scripts/verify_final_results.py` to audit the saved results without retraining. Running the original authored script will fit fresh models, so use a disposable checkout if deliberately reproducing training. Without the original software versions a fresh fit does not establish identity with the saved run.
