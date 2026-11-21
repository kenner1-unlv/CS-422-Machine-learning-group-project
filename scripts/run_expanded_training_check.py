"""Train the four model families on expanded_90, score fixed held-out rows.

The settings selected on the primary cohort are reused unchanged. This tests
the effect of adding training counties, not a new hyperparameter search.
Scores are reported on both the common 393-county rows and the larger set's
own held-out population.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.compare_remaining_models import load_predictions
from scripts.gradient_boosting_model import make_model as make_gb
from scripts.run_baselines import make_pipeline as make_linear
from scripts.run_remaining_models import make_model as make_other, score


OUT = ROOT / "results/expanded_90_four_model_check"
MODELS = ("linear", "gradient_boosting", "random_forest", "neural_network")
VARIANTS = ("weather_only", "weather_plus_trend")
KEYS = ["county_fips", "year"]


def get_model(kind: str, cutoff: int, variant: str, settings: dict):
    if kind == "linear":
        return make_linear("linear")
    if kind == "gradient_boosting":
        chosen = settings["gradient_boosting"]["decisions"][str(cutoff)][variant]["chosen"]
        params = {key: chosen[key] for key in
                  ("n_estimators", "learning_rate", "max_depth", "subsample",
                   "min_samples_leaf")}
        return make_gb(variant, params, 42, "squared_error")
    return make_other(kind, settings[kind]["choices"][str(cutoff)][variant]["setting"])


def validate_common_rows(primary: pd.DataFrame, expanded: pd.DataFrame, names: list[str]) -> None:
    common = expanded.merge(primary[KEYS + ["partition", "yield_bu_per_acre"] + names],
                            on=KEYS, how="inner", suffixes=("_expanded", "_primary"),
                            validate="one_to_one")
    if len(common) != len(primary):
        raise ValueError("Expanded cohort does not contain every primary row")
    for field in ["partition", "yield_bu_per_acre", *names]:
        left, right = common[field + "_expanded"], common[field + "_primary"]
        if field == "partition":
            if not left.equals(right):
                raise ValueError("Partition mismatch on shared rows")
        elif not np.allclose(left.to_numpy(), right.to_numpy(), atol=0, rtol=0):
            raise ValueError(f"Shared target or feature differs: {field}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((ROOT / "data/features/feature_manifest.json").read_text())
    splits = json.loads((ROOT / "config/splits.json").read_text())
    settings = {
        "gradient_boosting": json.loads((ROOT / "results/primary_100_gradient_boosting/selection.json").read_text()),
        "random_forest": json.loads((ROOT / "results/primary_100_random_forest/selection.json").read_text()),
        "neural_network": json.loads((ROOT / "results/primary_100_neural_network/selection.json").read_text()),
    }
    original = load_predictions()
    original = original[original["model"].isin(MODELS)]
    data, hashes = {}, {}
    for cutoff in splits["forecast_cutoff_months"]:
        expanded_path = ROOT / "data/features/expanded_90" / f"cutoff_{cutoff:02}.csv"
        primary_path = ROOT / "data/features/primary_100" / f"cutoff_{cutoff:02}.csv"
        expanded = pd.read_csv(expanded_path, dtype={"county_fips": str})
        primary = pd.read_csv(primary_path, dtype={"county_fips": str})
        if expanded.duplicated(KEYS).any() or primary.duplicated(KEYS).any():
            raise ValueError("Duplicate county-year")
        for variant in VARIANTS:
            names = manifest["features_by_cutoff"][str(cutoff)][variant]
            validate_common_rows(primary, expanded, names)
        train = expanded["partition"].eq("train")
        if int(train.sum()) != 14801 or int(primary["partition"].eq("test").sum()) != 1965:
            raise ValueError("Unexpected expanded/primary row count")
        data[cutoff] = (expanded, primary)
        hashes[expanded_path.name] = hashlib.sha256(expanded_path.read_bytes()).hexdigest()

    fitted, validation_rows = {}, []
    for cutoff, (expanded, primary) in data.items():
        train = expanded["partition"].eq("train")
        for variant in VARIANTS:
            names = manifest["features_by_cutoff"][str(cutoff)][variant]
            x_train = expanded.loc[train, names].to_numpy(dtype=float)
            y_train = expanded.loc[train, "yield_bu_per_acre"].to_numpy(dtype=float)
            for kind in MODELS:
                model = get_model(kind, cutoff, variant, settings)
                model.fit(x_train, y_train)
                fitted[(cutoff, variant, kind)] = model
                for population, frame in (("shared_primary", primary),
                                          ("own_expanded_90", expanded)):
                    use = frame["partition"].eq("validation")
                    result = score(frame.loc[use, "yield_bu_per_acre"],
                                   model.predict(frame.loc[use, names].to_numpy(dtype=float)))
                    validation_rows.append({"cutoff_month": cutoff, "variant": variant,
                                            "model": kind, "population": population,
                                            "partition": "validation", **result})
                print(f"Expanded train {cutoff:02} {variant} {kind}: "
                      f"shared validation MAE {validation_rows[-2]['mae']:.3f}",
                      flush=True)

    # All settings and validation scores are recorded before test scoring.
    design = {
        "training_cohort": "expanded_90", "training_rows_per_cutoff": 14801,
        "models": MODELS, "variants": VARIANTS,
        "settings_source": "Frozen primary_100 selections; Linear has no tuned setting",
        "no_validation_refit": True, "no_test_tuning": True,
        "input_sha256": hashes,
        "feature_manifest_sha256": hashlib.sha256((ROOT / "data/features/feature_manifest.json").read_bytes()).hexdigest(),
    }
    (OUT / "design.json").write_text(json.dumps(design, indent=2) + "\n",
                                     encoding="utf-8")
    pd.DataFrame(validation_rows).to_csv(OUT / "validation_metrics.csv", index=False)

    metrics, all_predictions = list(validation_rows), []
    for cutoff, (expanded, primary) in data.items():
        for variant in VARIANTS:
            names = manifest["features_by_cutoff"][str(cutoff)][variant]
            for kind in MODELS:
                model = fitted[(cutoff, variant, kind)]
                for population, frame in (("shared_primary", primary),
                                          ("own_expanded_90", expanded)):
                    use = frame["partition"].eq("test")
                    rows = frame.loc[use, ["county_fips", "year", "cutoff_month", "partition"]].copy()
                    rows["variant"] = variant
                    rows["model"] = kind
                    rows["population"] = population
                    rows["observed_yield"] = frame.loc[use, "yield_bu_per_acre"]
                    rows["predicted_yield"] = model.predict(frame.loc[use, names].to_numpy(dtype=float))
                    if not np.isfinite(rows["predicted_yield"]).all():
                        raise ValueError("Nonfinite prediction")
                    all_predictions.append(rows)
                    metrics.append({"cutoff_month": cutoff, "variant": variant,
                                    "model": kind, "population": population,
                                    "partition": "test",
                                    **score(rows["observed_yield"], rows["predicted_yield"])})
    predictions = pd.concat(all_predictions, ignore_index=True)
    predictions.to_csv(OUT / "predictions.csv.gz", index=False, compression="gzip")
    metric_frame = pd.DataFrame(metrics)
    metric_frame.to_csv(OUT / "metrics.csv", index=False)

    # Compare both training scopes on exactly the primary held-out rows.
    reference = original.groupby(["cutoff_month", "variant", "model", "partition"]).apply(
        lambda rows: pd.Series(score(rows["observed_yield"], rows["predicted_yield"])),
        include_groups=False).reset_index()
    shared = metric_frame[metric_frame["population"] == "shared_primary"]
    comparison = shared.merge(reference, on=["cutoff_month", "variant", "model", "partition"],
                              suffixes=("_expanded_training", "_primary_training"),
                              validate="one_to_one")
    comparison["mae_expanded_minus_primary"] = (
        comparison["mae_expanded_training"] - comparison["mae_primary_training"])
    comparison.to_csv(OUT / "shared_primary_comparison.csv", index=False)
    print(comparison[comparison["partition"] == "test"][
        ["cutoff_month", "variant", "model", "mae_primary_training",
         "mae_expanded_training", "mae_expanded_minus_primary"]].to_string(index=False))


if __name__ == "__main__":
    main()
