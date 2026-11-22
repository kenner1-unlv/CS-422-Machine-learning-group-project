"""Validate and normalize Lester's saved PR #16 output; this never trains a model."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.run_remaining_models import score

SOURCE = ROOT / "results/neural_network"
OUT = ROOT / "results/primary_100_neural_network"
LESTER_COMMIT = "4ac9f596901f9b93a0e1f23b7464cddf90d33ce8"
FALLBACK_COMMIT = "a92ed69ac8e66e175294949881d87e49b30a0d7e"
CUTOFFS = (5, 6, 7, 8)
VARIANTS = ("weather_only", "weather_plus_trend")
KEYS = ["county_fips", "year", "cutoff_month", "partition"]
GROUP = ["cutoff_month", "variant", "partition"]
RECOMPUTED = "saved_predictions_recomputed"
VALIDATION_SUMMARY = "lester_reported_pooled_validation"


def measured(rows: pd.DataFrame) -> dict:
    return {**score(rows["observed_yield"], rows["predicted_yield"]),
            "metric_source": RECOMPUTED}


def load_lester(reference: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return normalized test predictions and metrics, validating against frozen keys/targets."""
    summary = pd.read_csv(SOURCE / "model_comparison.csv", float_precision="round_trip")
    combinations = {(cutoff, variant) for cutoff in CUTOFFS for variant in VARIANTS}
    if (len(summary) != len(combinations) or
            set(zip(summary["cutoff"], summary["feature_type"])) != combinations):
        raise ValueError("Unexpected cutoff/variant manifest in Lester's summary")
    reference = reference[reference["partition"].isin(["validation", "test"])]
    if reference.duplicated(KEYS).any():
        raise ValueError("Duplicate comparison reference keys")
    predictions, metrics = [], []
    for row in summary.itertuples(index=False):
        cutoff, variant = row.cutoff, row.feature_type
        if row.iterations != 500 or not np.isfinite(
            [row.validation_mae, row.validation_rmse, row.test_mae, row.test_rmse]
        ).all() or not 0 <= row.validation_mae <= row.validation_rmse:
            raise ValueError(f"Unexpected frozen diagnostics for {cutoff}/{variant}")
        part = pd.read_csv(SOURCE / f"cutoff_{cutoff:02}_{variant}_predictions.csv",
                           dtype={"county_fips": str}, float_precision="round_trip")
        if not part["county_fips"].str.fullmatch(r"[0-9]{5}").fillna(False).all():
            raise ValueError(f"Invalid FIPS for {cutoff}/{variant}")
        part = part.rename(columns={"yield_bu_per_acre": "observed_yield"})
        part = part.assign(cutoff_month=cutoff, partition="test", variant=variant,
                           model="neural_network")
        expected = reference[(reference["cutoff_month"] == cutoff) &
                             (reference["partition"] == "test")]
        columns = KEYS + ["observed_yield"]
        expected = expected[columns].sort_values(KEYS).reset_index(drop=True)
        observed = part[columns].sort_values(KEYS).reset_index(drop=True)
        if len(expected) != 1965 or not observed.equals(expected):
            raise ValueError(f"Lester row/target mismatch for {cutoff}/{variant}")
        part["residual_observed_minus_predicted"] = part["observed_yield"] - part["predicted_yield"]
        if not np.isfinite(part["predicted_yield"]).all() or not np.allclose(
            part["residual_observed_minus_predicted"].abs(), part["absolute_error"],
            atol=1e-10, rtol=0,
        ):
            raise ValueError(f"Invalid saved prediction/error for {cutoff}/{variant}")
        test = measured(part)
        if not np.allclose([test["mae"], test["rmse"]], [row.test_mae, row.test_rmse],
                           atol=1e-10, rtol=0):
            raise ValueError(f"Test summary mismatch for {cutoff}/{variant}")
        validation_n = int(((reference["cutoff_month"] == cutoff) &
                            (reference["partition"] == "validation")).sum())
        if validation_n != 1572:
            raise ValueError(f"Unexpected frozen validation cohort at {cutoff}")
        common = {"cutoff_month": cutoff, "variant": variant}
        metrics.extend([
            {**common, "partition": "test", **test},
            {**common, "partition": "validation", "n": validation_n,
             "mae": row.validation_mae, "rmse": row.validation_rmse,
             "bias_predicted_minus_observed": None, "metric_source": VALIDATION_SUMMARY},
        ])
        predictions.append(part[KEYS + ["variant", "model", "observed_yield",
                                        "predicted_yield", "residual_observed_minus_predicted"]])
    return (pd.concat(predictions, ignore_index=True),
            pd.DataFrame(metrics).sort_values(GROUP).reset_index(drop=True))


def provenance() -> dict:
    files = [SOURCE / "model_comparison.csv", ROOT / "scripts/neural_network_model.py"]
    files += [SOURCE / f"cutoff_{cutoff:02}_{variant}_predictions.csv"
              for cutoff in CUTOFFS for variant in VARIANTS]
    # Hash canonical LF text so Git's platform checkout line endings do not change provenance.
    hashes = {f.relative_to(ROOT).as_posix():
              hashlib.sha256(f.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
              for f in files}
    return {
        "model": "neural_network",
        "coverage_set": "primary_100",
        "author": "Lester Iwuajoku",
        "source_commit": LESTER_COMMIT,
        "source_pull_request": 16,
        "historical_fallback_commit": FALLBACK_COMMIT,
        "training": "Fixed width 32, ReLU, training-only StandardScaler for X, raw yield, "
                    "max_iter=500, seed=42; other MLP parameters use library defaults.",
        "selection_rule": "Fixed configuration; no tuning in the source script. "
                          "Substituted as the primary NN by author attribution after holdout inspection.",
        "refit_on_validation": False,
        "fit_environment": None,
        "convergence_verified": False,
        "test_metrics": "Recomputed from saved predictions on verified common county-year/target rows.",
        "validation_metrics": "Lester's pooled MAE/RMSE as supplied, with expected design n=1572. "
                              "No prediction rows, bias, by-year metrics, or weather-group scores supplied.",
        "ignored_duplicate": "august_test_predictions.csv duplicates August weather plus trend "
                             "and drops leading FIPS zeros.",
        "source_hashes_sha256_normalized_lf": hashes,
    }


def main() -> None:
    original = pd.read_csv(ROOT / "results/primary_100_baselines/predictions.csv",
                           dtype={"county_fips": str})
    reference = original[(original["model"] == "linear") &
                         (original["variant"] == "weather_only")]
    predictions, metrics = load_lester(reference)
    OUT.mkdir(exist_ok=True)
    predictions.to_csv(OUT / "predictions.csv.gz", index=False,
                       compression={"method": "gzip", "mtime": 0})
    metrics.to_csv(OUT / "metrics.csv", index=False)
    grouped = predictions.groupby(GROUP + ["year"], sort=True)
    annual = [{**dict(zip(GROUP + ["year"], key)), **measured(rows)}
              for key, rows in grouped]
    pd.DataFrame(annual).to_csv(OUT / "metrics_by_year.csv", index=False)
    (OUT / "selection.json").write_text(json.dumps(provenance(), indent=2) + "\n",
                                        encoding="utf-8")
    print(f"Verified and normalized {len(predictions):,} Lester test predictions; "
          "validation retained as author-reported pooled metrics.")


if __name__ == "__main__":
    main()
