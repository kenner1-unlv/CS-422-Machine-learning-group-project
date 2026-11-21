"""Regression checks for the two shared-protocol model contributions."""

import json
import sys
import unittest
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import TransformedTargetRegressor
from sklearn.ensemble import RandomForestRegressor


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.run_remaining_models import candidate_settings, load_inputs, make_model, score
from scripts.compare_remaining_models import load_predictions


class RemainingModelChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.splits, cls.manifest, cls.features, cls.hashes = load_inputs()
        cls.baseline = pd.read_csv(ROOT / "results/primary_100_baselines/predictions.csv",
                                   dtype={"county_fips": str})

    def test_candidate_design(self):
        self.assertEqual(len(candidate_settings("random_forest")), 4)
        self.assertEqual(len(candidate_settings("neural_network")), 2)
        self.assertIsInstance(make_model("random_forest", candidate_settings("random_forest")[0]),
                              RandomForestRegressor)
        network = make_model("neural_network", candidate_settings("neural_network")[0])
        self.assertIsInstance(network, TransformedTargetRegressor)
        self.assertFalse(network.regressor.steps[-1][1].early_stopping)
        self.assertEqual(network.regressor.steps[-1][1].hidden_layer_sizes, (32,))

    def test_saved_selections_are_validation_only(self):
        for kind in ("random_forest", "neural_network"):
            out = ROOT / "results" / f"primary_100_{kind}"
            selection = json.loads((out / "selection.json").read_text())
            tuning = pd.read_csv(out / "tuning.csv")
            self.assertFalse(selection["refit_on_validation"])
            self.assertEqual(selection["input_sha256"], self.hashes)
            self.assertEqual(len(tuning), 4 * 2 * len(candidate_settings(kind)))
            for cutoff in self.splits["forecast_cutoff_months"]:
                for variant in ("weather_only", "weather_plus_trend"):
                    rows = tuning[(tuning["cutoff_month"] == cutoff) &
                                  (tuning["variant"] == variant)]
                    best = rows.sort_values(["mae", "rmse", "candidate"]).iloc[0]
                    choice = selection["choices"][str(cutoff)][variant]
                    self.assertEqual(choice["candidate"], int(best["candidate"]))
                    self.assertAlmostEqual(choice["validation"]["mae"], best["mae"])
                    self.assertEqual(choice["predictors"],
                                     self.manifest["features_by_cutoff"][str(cutoff)][variant])

    def test_predictions_match_baseline_rows_and_metrics(self):
        keys = ["county_fips", "year", "cutoff_month", "partition"]
        columns = keys + ["observed_yield"]
        reference = self.baseline[(self.baseline["model"] == "linear") &
                                  (self.baseline["variant"] == "weather_only")]
        reference = reference[columns].sort_values(keys).reset_index(drop=True)
        for kind in ("random_forest", "neural_network"):
            out = ROOT / "results" / f"primary_100_{kind}"
            predictions = pd.read_csv(out / "predictions.csv.gz", dtype={"county_fips": str})
            metrics = pd.read_csv(out / "metrics.csv")
            yearly = pd.read_csv(out / "metrics_by_year.csv")
            groups = pd.read_csv(out / "subgroup_metrics.csv")
            for _, variant in predictions.groupby("variant"):
                pd.testing.assert_frame_equal(
                    variant[columns].sort_values(keys).reset_index(drop=True), reference)
            self.assertEqual(len(metrics), 4 * 2 * 3)
            self.assertTrue(np.isfinite(predictions["predicted_yield"]).all())
            for row in metrics.itertuples():
                section = predictions[(predictions["cutoff_month"] == row.cutoff_month) &
                                      (predictions["variant"] == row.variant) &
                                      (predictions["partition"] == row.partition)]
                expected = score(section["observed_yield"], section["predicted_yield"])
                self.assertEqual(row.n, expected["n"])
                self.assertAlmostEqual(row.mae, expected["mae"], places=8)
                self.assertAlmostEqual(row.rmse, expected["rmse"], places=8)
            self.assertEqual(len(yearly), 4 * 2 * 26)
            all_group = groups[groups["group"] == "all"]
            self.assertEqual(len(all_group), 4 * 2 * 2)
            self.assertEqual(set(all_group["n"]), {1572, 1965})

    def test_network_scalers_fit_training_rows_only(self):
        out = ROOT / "results/primary_100_neural_network/models"
        for cutoff in self.splits["forecast_cutoff_months"]:
            frame = self.features[cutoff]
            training = frame["partition"].eq("train")
            for variant in ("weather_only", "weather_plus_trend"):
                names = self.manifest["features_by_cutoff"][str(cutoff)][variant]
                model = joblib.load(out / f"{variant}_{cutoff:02}.joblib")
                scaler = model.regressor_["standardscaler"]
                network = model.regressor_["mlpregressor"]
                self.assertEqual(int(scaler.n_samples_seen_), int(training.sum()))
                np.testing.assert_allclose(scaler.mean_, frame.loc[training, names].mean().to_numpy())
                np.testing.assert_allclose(model.transformer_.mean_,
                                           [frame.loc[training, "yield_bu_per_acre"].mean()])
                self.assertEqual(network.n_iter_, 250)

    def test_five_model_comparison_recomputes_frozen_scores(self):
        predictions = load_predictions()
        out = ROOT / "results/team_model_comparison"
        comparison = pd.read_csv(out / "comparison.csv")
        self.assertEqual(len(comparison), 5 * 2 * 4 * 2)
        self.assertEqual(len(predictions), 5 * 2 * 4 * (1572 + 1965))
        for row in comparison.itertuples():
            section = predictions[(predictions["model"] == row.model) &
                                  (predictions["variant"] == row.variant) &
                                  (predictions["cutoff_month"] == row.cutoff_month) &
                                  (predictions["partition"] == row.partition)]
            expected = score(section["observed_yield"], section["predicted_yield"])
            self.assertEqual(row.n, expected["n"])
            self.assertAlmostEqual(row.mae, expected["mae"], places=8)
        for name in ("comparison_by_year.csv", "subgroup_comparison.csv",
                     "year_omission_sensitivity.csv", "test_mae_by_cutoff.png",
                     "july_test_mae_by_year.png"):
            self.assertTrue((out / name).is_file(), name)
        sensitivity = pd.read_csv(out / "year_omission_sensitivity.csv")
        self.assertEqual(len(sensitivity), 4 * 2 * 5 * 5)
        self.assertEqual(set(sensitivity["years_retained"]), {4})
        self.assertEqual(set(sensitivity["n"]), {4 * 393})


if __name__ == "__main__":
    unittest.main()
