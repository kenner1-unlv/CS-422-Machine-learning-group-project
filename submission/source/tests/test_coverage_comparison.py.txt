import unittest
from scripts.compare_coverage_baselines import summarize_errors


class CoverageComparisonTests(unittest.TestCase):
    def test_mae_and_rmse_use_selected_population(self):
        result = summarize_errors([-2., 4.])
        self.assertEqual(result['mae'], 3.)
        self.assertAlmostEqual(result['rmse'], 10 ** .5)
        self.assertEqual(result['n'], 2)

    def test_empty_population_rejected(self):
        with self.assertRaises(ValueError):
            summarize_errors([])
