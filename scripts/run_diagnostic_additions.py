"""Fixed trend-only and equal-weight ensemble checks on the primary cohort.

Neither analysis tunes a setting against test outcomes. The ensemble averages
four already fitted model families without learned stacking weights.
"""

from __future__ import annotations

import argparse
import hashlib
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
from scripts.run_remaining_models import load_inputs, score


OUT = ROOT / "results/primary_100_diagnostic_additions"
MODEL_FAMILIES = ("linear", "gradient_boosting", "random_forest", "neural_network")
KEYS = ["county_fips", "year", "cutoff_month", "partition", "variant"]


def summarize(predictions: pd.DataFrame, stem: str) -> pd.DataFrame:
    predictions.to_csv(OUT / f"{stem}_predictions.csv", index=False)
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


def four_model_mean(neural_source: str) -> pd.DataFrame:
    original = load_predictions()
    if neural_source == "stopping_study":
        replacement = pd.read_csv(
            ROOT / "results/primary_100_neural_network_stopping_study/predictions.csv",
            dtype={"county_fips": str},
        )
        replacement = replacement[replacement["partition"].isin(["validation", "test"])].copy()
        replacement["model"] = "neural_network"
        other = original[original["model"] == "neural_network"]
        columns = KEYS + ["observed_yield"]
        if not replacement[columns].sort_values(KEYS).reset_index(drop=True).equals(
            other[columns].sort_values(KEYS).reset_index(drop=True)
        ):
            raise ValueError("Stopping-study NN uses different held-out rows")
        original = pd.concat([original[original["model"] != "neural_network"], replacement],
                             ignore_index=True)
    selected = original[original["model"].isin(MODEL_FAMILIES)].copy()
    if selected.duplicated(KEYS + ["model"]).any():
        raise ValueError("Duplicate ensemble member prediction")
    pivot = selected.pivot(index=KEYS, columns="model", values="predicted_yield")
    if set(pivot.columns) != set(MODEL_FAMILIES) or pivot.isna().any().any():
        raise ValueError("Incomplete four-model ensemble")
    expected = selected[selected["model"] == "linear"][KEYS + ["observed_yield"]]
    ensemble = expected.merge(pivot.mean(axis=1).rename("predicted_yield").reset_index(),
                              on=KEYS, validate="one_to_one")
    return summarize(ensemble, f"four_model_mean_{neural_source}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--neural-source", choices=("original", "stopping_study"),
                        default="original")
    args = parser.parse_args()
    _, manifest, datasets, hashes = load_inputs()
    if any("year_since_2000" not in frame.columns for frame in datasets.values()):
        raise ValueError("Missing declared trend predictor")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "models").mkdir(exist_ok=True)
    design = {
        "trend_only": "LinearRegression with intercept on year_since_2000; training rows only",
        "ensemble": "Unweighted mean of Linear, tuned GB, RF and NN saved predictions",
        "neural_source": args.neural_source,
        "cutoffs": sorted(datasets), "variants": list(manifest["features_by_cutoff"]["5"]),
        "input_sha256": hashes,
        "split_sha256": hashlib.sha256((ROOT / "config/splits.json").read_bytes()).hexdigest(),
        "no_test_selection": True,
    }
    (OUT / f"design_{args.neural_source}.json").write_text(
        json.dumps(design, indent=2) + "\n", encoding="utf-8")
    trend = trend_only(datasets)
    blend = four_model_mean(args.neural_source)
    comparison = load_predictions()
    full_linear = comparison[(comparison["model"] == "linear") &
                             (comparison["variant"] == "weather_plus_trend")]
    joined = trend.merge(
        full_linear.groupby(["cutoff_month", "partition"]).apply(
            lambda rows: pd.Series(score(rows["observed_yield"], rows["predicted_yield"])),
            include_groups=False).reset_index(),
        on=["cutoff_month", "partition"], suffixes=("_trend_only", "_weather_plus_trend"),
        validate="one_to_one",
    )
    joined["mae_trend_only_minus_full_linear"] = (
        joined["mae_trend_only"] - joined["mae_weather_plus_trend"])
    joined.to_csv(OUT / "weather_increment_over_trend.csv", index=False)
    print("Trend-only MAE:")
    print(trend.to_string(index=False))
    print("Four-model mean MAE:")
    print(blend[blend["variant"] == "weather_plus_trend"].to_string(index=False))


if __name__ == "__main__":
    main()
