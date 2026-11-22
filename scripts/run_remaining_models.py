"""Fit Random Forest on the project's shared primary cohort.

Each cutoff and feature variant gets an independent training-only fit. Candidate
settings are compared on 2017-2020; selections are saved before 2021-2025 is
scored. The planned model additions follow the project's shared chronological
protocol; test outcomes are never used to choose their settings.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import platform
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error


ROOT = Path(__file__).resolve().parents[1]
COHORT = "primary_100"
VARIANTS = ("weather_only", "weather_plus_trend")
SEED = 42


def candidate_settings(model_kind: str) -> list[dict]:
    """Keep the validation search small, fixed, and easy to reproduce."""
    if model_kind == "random_forest":
        return [
            {"n_estimators": 150, "max_depth": depth, "min_samples_leaf": leaf,
             "max_features": 0.7, "bootstrap": True}
            for depth, leaf in itertools.product((12, None), (5, 20))
        ]
    raise ValueError(f"Unknown model: {model_kind}")


def make_model(model_kind: str, setting: dict):
    if model_kind == "random_forest":
        return RandomForestRegressor(**setting, random_state=SEED, n_jobs=4)
    raise ValueError(model_kind)


def score(actual: np.ndarray, predicted: np.ndarray) -> dict:
    error = np.asarray(predicted) - np.asarray(actual)
    return {"n": len(error), "mae": float(mean_absolute_error(actual, predicted)),
            "rmse": float(np.sqrt(mean_squared_error(actual, predicted))),
            "bias_predicted_minus_observed": float(error.mean())}


def load_inputs() -> tuple[dict, dict, dict[int, pd.DataFrame], dict[str, str]]:
    splits = json.loads((ROOT / "config/splits.json").read_text())
    manifest = json.loads((ROOT / "data/features/feature_manifest.json").read_text())
    summary = json.loads((ROOT / "data/study_sets/split_summary.json").read_text())
    prior = json.loads((ROOT / "results/primary_100_gradient_boosting/selection.json").read_text())
    expected_hashes = {Path(key.replace("\\", "/")).name: value
                       for key, value in prior["input_sha256"].items()}
    expected_counts = {part: group["county_years"]
                       for part, group in summary["sets"][COHORT].items()}
    datasets, hashes = {}, {}
    for cutoff in splits["forecast_cutoff_months"]:
        path = ROOT / "data/features" / COHORT / f"cutoff_{cutoff:02}.csv"
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != expected_hashes[path.name]:
            raise ValueError(f"Feature input differs from earlier model: {path.name}")
        hashes[path.name] = digest
        frame = pd.read_csv(path, dtype={"county_fips": str})
        if frame.duplicated(["county_fips", "year"]).any():
            raise ValueError(f"Duplicate county-year: {path.name}")
        if frame["partition"].value_counts().to_dict() != expected_counts:
            raise ValueError(f"Split count mismatch: {path.name}")
        for part, (start, end) in splits["partitions"].items():
            if not (frame["year"].between(start, end) == frame["partition"].eq(part)).all():
                raise ValueError(f"Year partition mismatch: {path.name}")
        for variant in VARIANTS:
            names = manifest["features_by_cutoff"][str(cutoff)][variant]
            if set(names) & set(manifest["metadata_not_predictors"]):
                raise ValueError("Metadata in predictor allowlist")
            if not np.isfinite(frame[names].to_numpy(dtype=float)).all():
                raise ValueError(f"Nonfinite predictors: {path.name}")
        datasets[cutoff] = frame
    return splits, manifest, datasets, hashes


def validate_against_baseline(predictions: pd.DataFrame) -> None:
    """Ensure every model/variant predicts the same observed county-years."""
    reference = pd.read_csv(ROOT / "results/primary_100_baselines/predictions.csv",
                            dtype={"county_fips": str})
    reference = reference[(reference["model"] == "linear") &
                          (reference["variant"] == "weather_only")]
    keys = ["county_fips", "year", "cutoff_month", "partition"]
    columns = keys + ["observed_yield"]
    expected = reference[columns].sort_values(keys).reset_index(drop=True)
    for variant, group in predictions.groupby("variant"):
        actual = group[columns].sort_values(keys).reset_index(drop=True)
        if not actual.equals(expected):
            raise ValueError(f"{variant} rows or targets differ from Linear")


def add_weather_groups(predictions: pd.DataFrame, out: Path) -> None:
    labels = pd.read_csv(ROOT / "results/weather_groups/heldout_weather_labels.csv",
                         dtype={"county_fips": str})
    labels = labels[labels["coverage_set"] == COHORT].copy()
    labels["group"] = labels["groups"].str.split("|")
    labels = labels.explode("group")[["county_fips", "year", "cutoff_month", "partition", "group"]]
    heldout = predictions[predictions["partition"].isin(["validation", "test"])]
    joined = heldout.merge(labels, on=["county_fips", "year", "cutoff_month", "partition"],
                           validate="many_to_many")
    if len(joined[joined["group"] == "all"]) != len(heldout):
        raise ValueError("Weather labels do not cover every held-out row")
    rows = []
    for (cutoff, variant, part, group), section in joined.groupby(
        ["cutoff_month", "variant", "partition", "group"]
    ):
        result = score(section["observed_yield"], section["predicted_yield"])
        years = int(section["year"].nunique())
        rows.append({"cutoff_month": cutoff, "variant": variant, "partition": part,
                     "group": group, "years": years,
                     "small_sample": bool(result["n"] < 30 or years < 3), **result})
    pd.DataFrame(rows).to_csv(out / "subgroup_metrics.csv", index=False)


def run(model_kind: str) -> None:
    splits, manifest, datasets, hashes = load_inputs()
    out = ROOT / "results" / f"{COHORT}_{model_kind}"
    (out / "models").mkdir(parents=True, exist_ok=True)
    settings = candidate_settings(model_kind)
    choices, tuning, fitted = {}, [], {}

    # Selection stage uses only training and validation rows and labels.
    for cutoff, frame in datasets.items():
        choices[str(cutoff)] = {}
        train = frame["partition"].eq("train")
        validation = frame["partition"].eq("validation")
        for variant in VARIANTS:
            names = manifest["features_by_cutoff"][str(cutoff)][variant]
            x_train = frame.loc[train, names].to_numpy(dtype=float)
            y_train = frame.loc[train, "yield_bu_per_acre"].to_numpy(dtype=float)
            x_val = frame.loc[validation, names].to_numpy(dtype=float)
            y_val = frame.loc[validation, "yield_bu_per_acre"].to_numpy(dtype=float)
            candidates = []
            for index, setting in enumerate(settings):
                model = make_model(model_kind, setting)
                model.fit(x_train, y_train)
                prediction = model.predict(x_val)
                if not np.isfinite(prediction).all():
                    raise ValueError("Nonfinite validation prediction")
                result = score(y_val, prediction)
                row = {"cutoff_month": cutoff, "variant": variant, "candidate": index,
                       "setting": json.dumps(setting, sort_keys=True), **result}
                tuning.append(row)
                candidates.append((result["mae"], result["rmse"], index, model, row))
                print(f"{model_kind} cutoff {cutoff:02} {variant} candidate {index}: "
                      f"validation MAE {result['mae']:.3f}", flush=True)
            _, _, index, best, row = min(candidates, key=lambda item: item[:3])
            fitted[(cutoff, variant)] = best
            choices[str(cutoff)][variant] = {
                "candidate": index, "setting": settings[index],
                "validation": {key: row[key] for key in ("n", "mae", "rmse")},
                "predictors": names,
            }

    selection = {
        "model": model_kind, "coverage_set": COHORT, "variants": list(VARIANTS),
        "seed": SEED, "selection_metric": "validation MAE, then RMSE, then candidate order",
        "refit_on_validation": False, "candidates": settings,
        "choices": choices, "input_sha256": hashes,
        "split_config_sha256": hashlib.sha256((ROOT / "config/splits.json").read_bytes()).hexdigest(),
        "feature_manifest_sha256": hashlib.sha256((ROOT / "data/features/feature_manifest.json").read_bytes()).hexdigest(),
        "python": platform.python_version(), "numpy": np.__version__,
        "pandas": pd.__version__, "sklearn": sklearn.__version__,
        "test_note": "Test outcomes did not enter fitting or validation-based setting selection.",
    }
    (out / "selection.json").write_text(json.dumps(selection, indent=2) + "\n", encoding="utf-8")
    pd.DataFrame(tuning).to_csv(out / "tuning.csv", index=False)

    # Only now score the frozen training fits on the common test rows.
    prediction_frames, metrics_rows, yearly_rows = [], [], []
    for cutoff, frame in datasets.items():
        for variant in VARIANTS:
            names = manifest["features_by_cutoff"][str(cutoff)][variant]
            model = fitted[(cutoff, variant)]
            joblib.dump(model, out / "models" / f"{variant}_{cutoff:02}.joblib",
                        compress=3)
            predicted = model.predict(frame[names].to_numpy(dtype=float))
            if not np.isfinite(predicted).all():
                raise ValueError("Nonfinite model prediction")
            rows = frame[["county_fips", "year", "cutoff_month", "partition"]].copy()
            rows["variant"] = variant
            rows["model"] = model_kind
            rows["observed_yield"] = frame["yield_bu_per_acre"]
            rows["predicted_yield"] = predicted
            rows["residual_observed_minus_predicted"] = rows["observed_yield"] - predicted
            prediction_frames.append(rows)
            for part, section in rows.groupby("partition"):
                metrics_rows.append({"cutoff_month": cutoff, "variant": variant,
                                     "partition": part, **score(section["observed_yield"],
                                                                  section["predicted_yield"])})
                for year, annual in section.groupby("year"):
                    yearly_rows.append({"cutoff_month": cutoff, "variant": variant,
                                        "partition": part, "year": year,
                                        **score(annual["observed_yield"], annual["predicted_yield"])})
    predictions = pd.concat(prediction_frames, ignore_index=True)
    validate_against_baseline(predictions)
    predictions.to_csv(out / "predictions.csv.gz", index=False, compression="gzip")
    pd.DataFrame(metrics_rows).to_csv(out / "metrics.csv", index=False)
    pd.DataFrame(yearly_rows).to_csv(out / "metrics_by_year.csv", index=False)
    add_weather_groups(predictions, out)
    print(pd.DataFrame(metrics_rows).query("partition == 'test'").to_string(index=False))
    print(f"Saved {model_kind} outputs to {out}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("model", choices=("random_forest",))
    run(parser.parse_args().model)


if __name__ == "__main__":
    main()
