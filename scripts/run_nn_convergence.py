"""Validation-only NN stopping study; keep the original 250-iteration run.

Run ``select`` first. It fits two widths under each of two stopping rules and
compares their chronological validation scores with the original frozen NN.
The choice and fitted models are saved before ``score`` reads test outcomes.
"""

from __future__ import annotations

import argparse
import json
import sys
import warnings
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import TransformedTargetRegressor
from sklearn.exceptions import ConvergenceWarning
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.run_remaining_models import (SEED, VARIANTS, add_weather_groups,
                                          load_inputs, score, validate_against_baseline)


OUT = ROOT / "results/primary_100_neural_network_stopping_study"
ORIGINAL = ROOT / "results/primary_100_neural_network"
MAX_ITER = 1500
TOL = 0.0001
PATIENCE = 30
WIDTHS = (32, 64)


def make_network(width: int, internal_early_stopping: bool = False):
    network = MLPRegressor(
        hidden_layer_sizes=(width,), activation="relu", solver="adam",
        alpha=0.001, batch_size=256, learning_rate_init=0.001,
        max_iter=MAX_ITER, tol=TOL, n_iter_no_change=PATIENCE,
        early_stopping=internal_early_stopping, validation_fraction=0.15,
        random_state=SEED,
    )
    return TransformedTargetRegressor(
        regressor=make_pipeline(StandardScaler(), network),
        transformer=StandardScaler(),
    )


def select() -> None:
    _, manifest, datasets, hashes = load_inputs()
    original = json.loads((ORIGINAL / "selection.json").read_text())
    (OUT / "models").mkdir(parents=True, exist_ok=True)
    (OUT / "loss_curves").mkdir(exist_ok=True)
    decisions, rows = {}, []
    for cutoff, frame in datasets.items():
        decisions[str(cutoff)] = {}
        train = frame["partition"].eq("train")
        validation = frame["partition"].eq("validation")
        for variant in VARIANTS:
            names = manifest["features_by_cutoff"][str(cutoff)][variant]
            x_train = frame.loc[train, names].to_numpy(dtype=float)
            y_train = frame.loc[train, "yield_bu_per_acre"].to_numpy(dtype=float)
            x_val = frame.loc[validation, names].to_numpy(dtype=float)
            y_val = frame.loc[validation, "yield_bu_per_acre"].to_numpy(dtype=float)
            prior = original["choices"][str(cutoff)][variant]
            prior_score = prior["validation"]
            prior_model = joblib.load(ORIGINAL / "models" / f"{variant}_{cutoff:02}.joblib")
            prior_network = prior_model.regressor_["mlpregressor"]
            prior_validation = score(y_val, prior_model.predict(x_val))
            if not np.isclose(prior_validation["mae"], prior_score["mae"]):
                raise ValueError("Original validation score changed")
            rows.append({"cutoff_month": cutoff, "variant": variant,
                         "source": "original_fixed_250",
                         "hidden_units": prior["setting"]["hidden_layer_sizes"][0],
                         "iterations": prior_network.n_iter_, "met_stopping_rule": False,
                         "last_scaled_training_loss": prior_network.loss_curve_[-1],
                         **prior_validation})
            candidates = [(prior_score["mae"], prior_score["rmse"], 0,
                           "original_fixed_250", prior["setting"]["hidden_layer_sizes"][0],
                           None, 250, False)]
            for internal_stop in (False, True):
                source = ("internal_training_validation_stop" if internal_stop
                          else "training_loss_stop")
                for width in WIDTHS:
                    index = 1 + 2 * int(internal_stop) + WIDTHS.index(width)
                    model = make_network(width, internal_stop)
                    with warnings.catch_warnings(record=True) as caught:
                        warnings.simplefilter("always", ConvergenceWarning)
                        model.fit(x_train, y_train)
                    network = model.regressor_["mlpregressor"]
                    stopped = network.n_iter_ < MAX_ITER and not any(
                        issubclass(w.category, ConvergenceWarning) for w in caught)
                    val_score = score(y_val, model.predict(x_val))
                    if not np.isfinite(val_score["mae"]):
                        raise ValueError("Nonfinite validation score")
                    pd.DataFrame({"iteration": np.arange(1, len(network.loss_curve_) + 1),
                                  "scaled_training_loss": network.loss_curve_}).to_csv(
                        OUT / "loss_curves" /
                        f"{variant}_{cutoff:02}_{source}_{width}.csv.gz",
                        index=False, compression="gzip")
                    rows.append({"cutoff_month": cutoff, "variant": variant,
                                 "source": source, "hidden_units": width,
                                 "iterations": network.n_iter_, "met_stopping_rule": stopped,
                                 "last_scaled_training_loss": network.loss_curve_[-1],
                                 **val_score})
                    candidates.append((val_score["mae"], val_score["rmse"], index,
                                       source, width, model, network.n_iter_, stopped))
                    print(f"{cutoff:02} {variant} {source} width={width}: validation MAE "
                          f"{val_score['mae']:.3f}; iterations={network.n_iter_}; "
                          f"stopped={stopped}", flush=True)
            best = min(candidates, key=lambda candidate: candidate[:3])
            _, _, _, source, width, model, iterations, stopped = best
            if source == "original_fixed_250":
                model = prior_model
            joblib.dump(model, OUT / "models" / f"{variant}_{cutoff:02}.joblib")
            decisions[str(cutoff)][variant] = {
                "source": source, "hidden_units": width, "iterations": iterations,
                "met_stopping_rule": stopped,
                "validation_mae": best[0], "validation_rmse": best[1],
                "predictors": names,
            }
    selection = {
        "objective": "Compare original fixed-250 NN to two stopping-rule widths using validation only",
        "cohort": "primary_100", "seed": SEED,
        "stopping_rule": {"max_iter": MAX_ITER, "tol": TOL,
                          "n_iter_no_change": PATIENCE,
                          "strategies": ["training loss", "internal training-only validation"],
                          "validation_fraction_for_internal_stopping": 0.15},
        "widths": WIDTHS,
        "selection_rule": "chronological validation MAE, RMSE, then original/training-loss/internal-validation order",
        "input_sha256": hashes, "decisions": decisions,
        "test_note": "Selection was saved before test outcomes were scored in this study.",
    }
    (OUT / "selection.json").write_text(json.dumps(selection, indent=2) + "\n",
                                        encoding="utf-8")
    pd.DataFrame(rows).to_csv(OUT / "candidate_validation.csv", index=False)
    print("Selection saved. Run the score stage after reviewing stopping diagnostics.")


def evaluate() -> None:
    _, manifest, datasets, hashes = load_inputs()
    selection = json.loads((OUT / "selection.json").read_text())
    if selection["input_sha256"] != hashes:
        raise ValueError("Feature inputs changed after selection")
    predictions, metrics, annual = [], [], []
    for cutoff, frame in datasets.items():
        for variant in VARIANTS:
            names = manifest["features_by_cutoff"][str(cutoff)][variant]
            decision = selection["decisions"][str(cutoff)][variant]
            if decision["predictors"] != names:
                raise ValueError("Predictor list changed after selection")
            model = joblib.load(OUT / "models" / f"{variant}_{cutoff:02}.joblib")
            predicted = model.predict(frame[names].to_numpy(dtype=float))
            if not np.isfinite(predicted).all():
                raise ValueError("Nonfinite prediction")
            rows = frame[["county_fips", "year", "cutoff_month", "partition"]].copy()
            rows["variant"] = variant
            rows["model"] = "neural_network_stopping_study"
            rows["observed_yield"] = frame["yield_bu_per_acre"]
            rows["predicted_yield"] = predicted
            rows["residual_observed_minus_predicted"] = rows["observed_yield"] - predicted
            predictions.append(rows)
            for part, group in rows.groupby("partition"):
                metrics.append({"cutoff_month": cutoff, "variant": variant,
                                "partition": part, "source": decision["source"],
                                **score(group["observed_yield"], group["predicted_yield"])})
                for year, year_rows in group.groupby("year"):
                    annual.append({"cutoff_month": cutoff, "variant": variant,
                                   "partition": part, "year": year,
                                   **score(year_rows["observed_yield"],
                                           year_rows["predicted_yield"])})
    all_rows = pd.concat(predictions, ignore_index=True)
    validate_against_baseline(all_rows)
    all_rows.to_csv(OUT / "predictions.csv.gz", index=False, compression="gzip")
    pd.DataFrame(metrics).to_csv(OUT / "metrics.csv", index=False)
    pd.DataFrame(annual).to_csv(OUT / "metrics_by_year.csv", index=False)
    add_weather_groups(all_rows, OUT)
    print(pd.DataFrame(metrics).query("partition == 'test'").to_string(index=False))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("stage", choices=("select", "score"))
    stage = parser.parse_args().stage
    select() if stage == "select" else evaluate()


if __name__ == "__main__":
    main()
