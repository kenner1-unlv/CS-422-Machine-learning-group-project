"""Checks for the trend, ensemble, NN stopping and broader-training studies."""

import json
import sys
import unittest
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.compare_remaining_models import load_predictions
from scripts.run_remaining_models import score


class SupplementalChecks(unittest.TestCase):
    def test_trend_only_is_training_fitted_and_reports_original_scale(self):
        out = ROOT / "results/primary_100_diagnostic_additions"
        metrics = pd.read_csv(out / "trend_only_metrics.csv")
        coefficients = pd.read_csv(out / "trend_only_coefficients.csv")
        self.assertEqual(len(coefficients), 4)
        self.assertEqual(set(coefficients["training_n"]), {6681})
        self.assertEqual(coefficients["intercept"].nunique(), 1)
        self.assertEqual(coefficients["slope_bu_per_acre_per_year"].nunique(), 1)
        predictions = pd.read_csv(out / "trend_only_predictions.csv",
                                  dtype={"county_fips": str})
        for cutoff in (5, 6, 7, 8):
            frame = pd.read_csv(ROOT / "data/features/primary_100" /
                                f"cutoff_{cutoff:02}.csv", dtype={"county_fips": str})
            training = frame["partition"].eq("train")
            model = joblib.load(out / "models" / f"trend_only_{cutoff:02}.joblib")
            self.assertEqual(model.n_features_in_, 1)
            np.testing.assert_allclose(model.coef_, coefficients[
                coefficients["cutoff_month"] == cutoff
            ]["slope_bu_per_acre_per_year"].to_numpy())
            # A fresh training-only fit must agree with the saved coefficient.
            x = frame.loc[training, "year_since_2000"].to_numpy()
            y = frame.loc[training, "yield_bu_per_acre"].to_numpy()
            self.assertAlmostEqual(model.coef_[0], np.cov(x, y, bias=True)[0, 1] / np.var(x))
        for row in metrics.itertuples():
            section = predictions[(predictions["cutoff_month"] == row.cutoff_month) &
                                  (predictions["variant"] == row.variant) &
                                  (predictions["partition"] == row.partition)]
            self.assertAlmostEqual(row.mae,
                                   score(section["observed_yield"], section["predicted_yield"])["mae"])

    def test_four_model_means_are_exact_equal_weight_averages(self):
        out = ROOT / "results/primary_100_diagnostic_additions"
        original = load_predictions()
        for source in ("original", "stopping_study"):
            design = json.loads((out / f"design_{source}.json").read_text())
            self.assertTrue(design["no_test_selection"])
            predictions = pd.read_csv(out / f"four_model_mean_{source}_predictions.csv",
                                      dtype={"county_fips": str})
            if source == "stopping_study":
                revised = pd.read_csv(
                    ROOT / "results/primary_100_neural_network_stopping_study/predictions.csv",
                    dtype={"county_fips": str})
                revised = revised[revised["partition"].isin(["validation", "test"])].copy()
                revised["model"] = "neural_network"
                members = pd.concat([original[original["model"] != "neural_network"], revised])
            else:
                members = original
            members = members[members["model"].isin(
                ["linear", "gradient_boosting", "random_forest", "neural_network"])]
            keys = ["county_fips", "year", "cutoff_month", "partition", "variant"]
            expected = members.groupby(keys)["predicted_yield"].mean().rename("expected")
            check = predictions.join(expected, on=keys, validate="many_to_one")
            np.testing.assert_allclose(check["predicted_yield"], check["expected"])
            self.assertEqual(len(predictions), 4 * 2 * (1572 + 1965))

    def test_stopping_study_selects_on_validation(self):
        out = ROOT / "results/primary_100_neural_network_stopping_study"
        selection = json.loads((out / "selection.json").read_text())
        candidates = pd.read_csv(out / "candidate_validation.csv")
        metrics = pd.read_csv(out / "metrics.csv")
        for cutoff in (5, 6, 7, 8):
            for variant in ("weather_only", "weather_plus_trend"):
                rows = candidates[(candidates["cutoff_month"] == cutoff) &
                                  (candidates["variant"] == variant)]
                self.assertEqual(len(rows), 5)
                chosen = selection["decisions"][str(cutoff)][variant]
                self.assertAlmostEqual(chosen["validation_mae"], rows["mae"].min())
                actual = metrics[(metrics["cutoff_month"] == cutoff) &
                                 (metrics["variant"] == variant) &
                                 (metrics["partition"] == "validation")].iloc[0]
                self.assertAlmostEqual(actual["mae"], chosen["validation_mae"])
                if chosen["source"] != "original_fixed_250":
                    self.assertTrue(chosen["met_stopping_rule"])
                    self.assertLess(chosen["iterations"], 1500)
                model = joblib.load(out / "models" / f"{variant}_{cutoff:02}.joblib")
                self.assertEqual(int(model.regressor_["standardscaler"].n_samples_seen_), 6681)

    def test_expanded_training_keeps_shared_primary_test_rows(self):
        out = ROOT / "results/expanded_90_four_model_check"
        design = json.loads((out / "design.json").read_text())
        self.assertEqual(design["training_rows_per_cutoff"], 14801)
        self.assertTrue(design["no_test_tuning"])
        comparison = pd.read_csv(out / "shared_primary_comparison.csv")
        self.assertEqual(len(comparison), 4 * 2 * 4 * 2)
        self.assertEqual(set(comparison["n_expanded_training"]), {1572, 1965})
        self.assertEqual(set(comparison["n_primary_training"]), {1572, 1965})
        np.testing.assert_allclose(comparison["mae_expanded_minus_primary"],
                                   comparison["mae_expanded_training"] -
                                   comparison["mae_primary_training"])
        metrics = pd.read_csv(out / "metrics.csv")
        own = metrics[(metrics["population"] == "own_expanded_90") &
                      (metrics["partition"] == "test")]
        self.assertEqual(set(own["n"]), {4084})


if __name__ == "__main__":
    unittest.main()
