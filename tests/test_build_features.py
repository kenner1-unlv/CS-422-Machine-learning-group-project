import calendar
import copy
import json
import unittest
from pathlib import Path
from scripts.build_features import compute_features, feature_names


class FeatureTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((Path(__file__).resolve().parents[1] / 'config/features.json').read_text())
        self.months = {m: (calendar.monthrange(2000, m)[1], (10.0 * m, float(m), float(m + 10), float(m - 5), float(m + 20), float(m - 10))) for m in range(1, 9)}

    def test_future_weather_cannot_change_earlier_forecast(self):
        original = compute_features(self.months, 2000, 5, self.config)
        changed = copy.deepcopy(self.months)
        for m in (6, 7, 8):
            changed[m] = (0, (float('nan'),) * 6)
        self.assertEqual(original, compute_features(changed, 2000, 5, self.config))
        self.assertEqual(original, compute_features({m: v for m, v in self.months.items() if m <= 5}, 2000, 5, self.config))

    def test_current_month_and_leap_day_weighting(self):
        result = compute_features(self.months, 2000, 5, self.config)
        self.assertEqual(result['season_precipitation_total_mm'], 90)
        self.assertAlmostEqual(result['season_tavg_mean_c'], (4 * 30 + 5 * 31) / 61, places=6)
        self.assertAlmostEqual(result['preseason_tavg_mean_c'], (31 + 2 * 29 + 3 * 31) / 91, places=6)
        changed = copy.deepcopy(self.months)
        changed[5] = (31, (0, 5, 15, 0, 25, -5))
        self.assertNotEqual(result, compute_features(changed, 2000, 5, self.config))

    def test_each_cutoff_schema_and_missing_month_rejection(self):
        for cutoff, count in ((5, 21), (6, 27), (7, 33), (8, 39)):
            names = feature_names(cutoff, self.config)
            self.assertEqual(len(names), count)
            self.assertEqual(set(compute_features(self.months, 2000, cutoff, self.config)), set(names) | {'year_since_2000'})
        del self.months[4]
        with self.assertRaises(ValueError):
            compute_features(self.months, 2000, 5, self.config)
