"""Regression checks for RF provenance and Lester NN import/metrics."""

import json
import sys
import unittest
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.run_remaining_models import candidate_settings, load_inputs, make_model, score
from scripts.compare_remaining_models import load_predictions
from scripts.import_lester_neural_network import VALIDATION_SUMMARY, load_lester, provenance


class RemainingModelChecks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.splits, cls.manifest, cls.features, cls.hashes = load_inputs()
        cls.baseline = pd.read_csv(ROOT / "results/primary_100_baselines/predictions.csv",
                                   dtype={"county_fips": str})

    def test_candidate_design(self):
        self.assertEqual(len(candidate_settings("random_forest")), 4)
        self.assertIsInstance(make_model("random_forest", candidate_settings("random_forest")[0]),
                              RandomForestRegressor)
    def test_saved_selections_are_validation_only(self):
        for kind in ("random_forest",):
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
        for kind in ("random_forest",):
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

    def test_lester_canonical_output_preserves_exact_test_rows(self):
        out = ROOT / "results/primary_100_neural_network"
        reference = self.baseline[(self.baseline["model"] == "linear") &
                                  (self.baseline["variant"] == "weather_only")]
        expected, metrics = load_lester(reference)
        saved = pd.read_csv(out / "predictions.csv.gz", dtype={"county_fips": str})
        pd.testing.assert_frame_equal(saved, expected)
        self.assertEqual(len(saved), 15720)
        self.assertEqual(set(saved["partition"]), {"test"})
        actual = pd.read_csv(out / "metrics.csv")
        pd.testing.assert_frame_equal(actual, metrics)
        reported = actual[actual["metric_source"] == VALIDATION_SUMMARY]
        self.assertEqual(len(reported), 8)
        self.assertTrue(reported["bias_predicted_minus_observed"].isna().all())
        self.assertEqual(json.loads((out / "selection.json").read_text()), provenance())
        self.assertEqual(set(pd.read_csv(out / "metrics_by_year.csv")["partition"]), {"test"})
        self.assertEqual(set(pd.read_csv(out / "subgroup_metrics.csv")["partition"]), {"test"})

    def test_five_model_comparison_recomputes_frozen_scores(self):
        predictions = load_predictions()
        out = ROOT / "results/team_model_comparison"
        comparison = pd.read_csv(out / "comparison.csv")
        self.assertEqual(len(comparison), 5 * 2 * 4 * 2)
        self.assertEqual(len(predictions), 4 * 2 * 4 * 1572 + 5 * 2 * 4 * 1965)
        for row in comparison.itertuples():
            if row.metric_source == VALIDATION_SUMMARY:
                self.assertEqual((row.model, row.partition), ("neural_network", "validation"))
                self.assertTrue(np.isnan(row.bias_predicted_minus_observed))
                continue
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
