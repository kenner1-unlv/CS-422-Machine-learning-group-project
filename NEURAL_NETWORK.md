# Neural Network Model — CS 422

## 1. Overview

This project uses a neural network to predict U.S. county-level corn yields (bushels per acre) using weather data and a calendar-year trend feature.

## 2. Dataset

The model uses the `primary_100` dataset containing 393 counties and 10,218 county-year observations from 2000–2025.

Data is split chronologically:

| Partition | Years | Observations |
|---|---|---:|
| Training | 2000–2016 | 6,681 |
| Validation | 2017–2020 | 1,572 |
| Testing | 2021–2025 | 1,965 |

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

Model selection was based on validation mean absolute error (MAE). Root mean squared error (RMSE) was also reported.

The test partition was reserved for final evaluation.

## 5. Results

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
- Some unusually low-yield observations were substantially overestimated.
- Results may not generalize equally well to counties excluded from the primary dataset.

## 7. How to Run

From the project root, install the required dependencies and execute:

```powershell
python scripts/neural_network_model.py
```

The script evaluates the neural network configurations and saves results under `results/neural_network/`.

## 8. Conclusion

The August weather + trend configuration achieved the lowest validation MAE and the best test performance among the eight neural network configurations.

Adding the calendar-year trend feature generally improved prediction accuracy. Future improvements could include convergence testing, hyperparameter tuning, and additional analysis of large prediction errors.