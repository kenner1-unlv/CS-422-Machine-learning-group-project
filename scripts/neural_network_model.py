
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.neural_network import MLPRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.exceptions import ConvergenceWarning


# Load approved feature lists
with open("data/features/feature_manifest.json", "r") as file:
    manifest = json.load(file)

output_dir = Path("results/neural_network")
output_dir.mkdir(parents=True, exist_ok=True)

all_results = []

# Cutoffs are forecast months: May through August
for cutoff in [5, 6, 7, 8]:
    df = pd.read_csv(
        f"data/features/primary_100/cutoff_{cutoff:02d}.csv",
        dtype={"county_fips": str}
    )

    # Use the saved partitions; do not reshuffle
    train = df[df["partition"] == "train"]
    val = df[df["partition"] == "validation"]
    test = df[df["partition"] == "test"]

    # Compare weather alone against weather plus a yield trend
    for feature_type in ["weather_only", "weather_plus_trend"]:
        features = manifest["features_by_cutoff"][str(cutoff)][feature_type]

        # Target is county yield in bushels per acre
        X_train = train[features]
        y_train = train["yield_bu_per_acre"]

        X_val = val[features]
        y_val = val["yield_bu_per_acre"]

        X_test = test[features]
        y_test = test["yield_bu_per_acre"]

        # Build the neural network
        model = Pipeline([
            ("scaler", StandardScaler()),  # MLP is sensitive to feature scale
            ("neural_network", MLPRegressor(
                hidden_layer_sizes=(32,),  # one hidden layer, 32 units
                activation="relu",  # standard hidden-layer activation
                max_iter=500,
                random_state=42  # fixed seed so reruns match
            ))
        ])

        # Train using training data only
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", ConvergenceWarning)
            model.fit(X_train, y_train)

        # How many passes the network actually ran
        iterations = model.named_steps["neural_network"].n_iter_

        # Validation evaluation
        val_predictions = model.predict(X_val)

        # MAE is typical error; RMSE penalizes large misses more
        val_mae = mean_absolute_error(y_val, val_predictions)
        val_rmse = np.sqrt(
            mean_squared_error(y_val, val_predictions)
        )

        print(
            f"VALIDATION | Month: {cutoff} | "
            f"Features: {feature_type} | "
            f"MAE: {val_mae:.2f} | "
            f"RMSE: {val_rmse:.2f}"
        )

        # Test evaluation: reporting only, never tuning
        test_predictions = model.predict(X_test)

        # Same two scores as validation, on held-out years
        test_mae = mean_absolute_error(y_test, test_predictions)
        test_rmse = np.sqrt(
            mean_squared_error(y_test, test_predictions)
        )

        print(
            f"TEST | Month: {cutoff} | "
            f"Features: {feature_type} | "
            f"MAE: {test_mae:.2f} | "
            f"RMSE: {test_rmse:.2f}"
        )

        # Save summary metrics
        all_results.append({
            "cutoff": cutoff,
            "feature_type": feature_type,
            "iterations": iterations,
            "validation_mae": val_mae,
            "validation_rmse": val_rmse,
            "test_mae": test_mae,
            "test_rmse": test_rmse
        })

        # Keep county, year, and actual yield with each prediction
        results = test[
            ["county_fips", "year", "yield_bu_per_acre"]
        ].copy()

        results["predicted_yield"] = test_predictions
        # Error in bushels per acre for each county-year
        results["absolute_error"] = abs(
            results["yield_bu_per_acre"] -
            results["predicted_yield"]
        )

        # One predictions file per configuration
        results.to_csv(
            output_dir / f"cutoff_{cutoff:02d}_{feature_type}_predictions.csv",
            index=False
        )

# Four months times two feature sets
summary = pd.DataFrame(all_results)

# Table of MAE and RMSE across all eight runs
summary.to_csv(
    output_dir / "model_comparison.csv",
    index=False
)

print("\nFINAL MODEL COMPARISON")
print(summary.to_string(index=False))

print("\nAll results saved to results/neural_network/")
