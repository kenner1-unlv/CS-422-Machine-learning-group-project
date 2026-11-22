"""Read-only verification of frozen standard-model evidence.

Run from Project root: python scripts/verify_final_results.py
This checks saved rows and validation selections; it does not retrain or write.
"""
from pathlib import Path
import json

import numpy as np
import pandas as pd

from compare_remaining_models import load_predictions

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results"
MANIFEST = json.loads((ROOT / "data/features/feature_manifest.json").read_text())
VARIANTS = ("weather_only", "weather_plus_trend")
CUTOFFS = (5, 6, 7, 8)


def selection(family: str) -> dict:
    return json.loads((RESULTS / f"primary_100_{family}/selection.json").read_text())


def verify_tuning() -> None:
    baseline = selection("baselines")
    ridge = pd.read_csv(RESULTS / "primary_100_baselines/ridge_tuning.csv")
    for cutoff in CUTOFFS:
        for variant in VARIANTS:
            rows = ridge[(ridge.cutoff_month == cutoff) & (ridge.variant == variant)]
            best = rows.sort_values(["mae", "rmse", "alpha"]).iloc[0]
            chosen = baseline["decisions"][str(cutoff)]["ridge_by_variant"][variant]
            assert np.isclose(best.alpha, chosen["alpha"])
            assert np.isclose(best.mae, chosen["mae"])

    gb = selection("gradient_boosting")
    gb_tuning = pd.read_csv(RESULTS / "primary_100_gradient_boosting/tuning.csv")
    for cutoff in CUTOFFS:
        for variant in VARIANTS:
            rows = gb_tuning[(gb_tuning.cutoff_month == cutoff) & (gb_tuning.variant == variant)]
            best = rows.sort_values(["validation_mae", "validation_rmse", "max_depth", "n_estimators"]).iloc[0]
            choice = gb["decisions"][str(cutoff)][variant]
            for key in ("learning_rate", "max_depth", "min_samples_leaf", "subsample", "n_estimators"):
                assert np.isclose(best[key], choice["chosen"][key]), (cutoff, variant, key)
            assert choice["predictors"] == MANIFEST["features_by_cutoff"][str(cutoff)][variant]
    assert gb["config"]["refit_on_validation"] is False

    for family in ("random_forest", "neural_network"):
        saved = selection(family)
        tuning = pd.read_csv(RESULTS / f"primary_100_{family}/tuning.csv")
        assert saved["refit_on_validation"] is False
        for cutoff in CUTOFFS:
            for variant in VARIANTS:
                rows = tuning[(tuning.cutoff_month == cutoff) & (tuning.variant == variant)]
                best = rows.sort_values(["mae", "rmse", "candidate"]).iloc[0]
                choice = saved["choices"][str(cutoff)][variant]
                assert int(best.candidate) == choice["candidate"]
                assert np.isclose(best.mae, choice["validation"]["mae"])
                assert choice["predictors"] == MANIFEST["features_by_cutoff"][str(cutoff)][variant]


def verify_predictions() -> None:
    # The existing loader asserts identical county-year-cutoff-partition keys and
    # observed targets for all five families and both fixed feature variants.
    predictions = load_predictions()
    saved = pd.read_csv(RESULTS / "team_model_comparison/comparison.csv")
    group = ["cutoff_month", "variant", "model", "partition"]
    calculated = predictions.groupby(group).apply(
        lambda x: pd.Series({
            "n": len(x),
            "mae": np.mean(np.abs(x.predicted_yield - x.observed_yield)),
            "rmse": np.sqrt(np.mean((x.predicted_yield - x.observed_yield) ** 2)),
            "bias_predicted_minus_observed": np.mean(x.predicted_yield - x.observed_yield),
        }), include_groups=False).reset_index()
    merged = calculated.merge(saved, on=group, suffixes=("_recomputed", "_saved"), validate="one_to_one")
    assert len(merged) == 80
    for metric in ("n", "mae", "rmse", "bias_predicted_minus_observed"):
        assert np.allclose(merged[f"{metric}_recomputed"], merged[f"{metric}_saved"], atol=1e-9)


if __name__ == "__main__":
    verify_tuning()
    verify_predictions()
    print("PASS: validation selections, feature lists, shared rows and targets, 80 saved metric groups")
