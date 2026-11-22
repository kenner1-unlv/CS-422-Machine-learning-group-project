"""Fixed trend-only and equal-weight ensemble checks on the primary cohort.

The ensemble averages four saved test predictions without fitting weights.
It is an exploratory post-test diagnostic, not a validation-selected model.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.compare_remaining_models import load_predictions
from scripts.run_remaining_models import score
from scripts.import_lester_neural_network import LESTER_COMMIT


OUT = ROOT / "results/primary_100_diagnostic_additions"
MODEL_FAMILIES = ("linear", "gradient_boosting", "random_forest", "neural_network")
KEYS = ["county_fips", "year", "cutoff_month", "partition", "variant"]


def summarize(predictions: pd.DataFrame, stem: str) -> pd.DataFrame:
    predictions.to_csv(OUT / f"{stem}_predictions.csv.gz", index=False,
                       compression={"method": "gzip", "mtime": 0})
    metrics = []
    annual = []
    for (cutoff, variant, partition), rows in predictions.groupby(
        ["cutoff_month", "variant", "partition"]
    ):
        metrics.append({"cutoff_month": cutoff, "variant": variant,
                        "partition": partition,
                        **score(rows["observed_yield"], rows["predicted_yield"])})
        for year, by_year in rows.groupby("year"):
            annual.append({"cutoff_month": cutoff, "variant": variant,
                           "partition": partition, "year": year,
                           **score(by_year["observed_yield"], by_year["predicted_yield"])})
    result = pd.DataFrame(metrics)
    result.to_csv(OUT / f"{stem}_metrics.csv", index=False)
    pd.DataFrame(annual).to_csv(OUT / f"{stem}_metrics_by_year.csv", index=False)
    return result


def trend_only(datasets: dict[int, pd.DataFrame]) -> pd.DataFrame:
    rows = []
    coefficients = []
    for cutoff, frame in datasets.items():
        training = frame["partition"].eq("train")
        model = LinearRegression().fit(
            frame.loc[training, ["year_since_2000"]],
            frame.loc[training, "yield_bu_per_acre"],
        )
        joblib.dump(model, OUT / "models" / f"trend_only_{cutoff:02}.joblib")
        coefficients.append({"cutoff_month": cutoff, "intercept": model.intercept_,
                             "slope_bu_per_acre_per_year": model.coef_[0],
                             "training_n": int(training.sum())})
        heldout = frame[frame["partition"].isin(["validation", "test"])].copy()
        prediction = model.predict(heldout[["year_since_2000"]])
        part = heldout[["county_fips", "year", "cutoff_month", "partition"]].copy()
        part["variant"] = "trend_only"
        part["observed_yield"] = heldout["yield_bu_per_acre"]
        part["predicted_yield"] = prediction
        rows.append(part)
    details = pd.DataFrame(coefficients)
    if details[["intercept", "slope_bu_per_acre_per_year"]].nunique().max() != 1:
        raise ValueError("Trend-only fits differ across cutoffs")
    details.to_csv(OUT / "trend_only_coefficients.csv", index=False)
    return summarize(pd.concat(rows, ignore_index=True), "trend_only")


def four_model_mean() -> pd.DataFrame:
    predictions = load_predictions()
    # Lester supplied row-level test forecasts only. A validation mean cannot
    # be reconstructed from pooled MAE/RMSE; never mix in the historical NN.
    selected = predictions[(predictions["partition"] == "test") &
                           predictions["model"].isin(MODEL_FAMILIES)].copy()
    if selected.duplicated(KEYS + ["model"]).any():
        raise ValueError("Duplicate ensemble member prediction")
    pivot = selected.pivot(index=KEYS, columns="model", values="predicted_yield")
    if set(pivot.columns) != set(MODEL_FAMILIES) or pivot.isna().any().any():
        raise ValueError("Incomplete four-model ensemble")
    expected = selected[selected["model"] == "linear"][KEYS + ["observed_yield"]]
    ensemble = expected.merge(pivot.mean(axis=1).rename("predicted_yield").reset_index(),
                              on=KEYS, validate="one_to_one")
    return summarize(ensemble, "four_model_mean_lester")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    design = {
        "ensemble": "Unweighted mean of Linear, tuned GB, RF and Lester's NN saved predictions",
        "neural_source_commit": LESTER_COMMIT,
        "partition": "test",
        "validation_ensemble_available": False,
        "validation_reason": "No Lester per-row validation predictions in PR #16.",
        "post_test_exploratory": True,
        "weights_fit_using_test": False,
        "other_diagnostics": "Trend-only uses existing frozen artifacts, not refit here.",
    }
    (OUT / "design_lester.json").write_text(
        json.dumps(design, indent=2) + "\n", encoding="utf-8")
    blend = four_model_mean()
    print("Four-model mean, exploratory test only:")
    print(blend.to_string(index=False))


if __name__ == "__main__":
    main()
