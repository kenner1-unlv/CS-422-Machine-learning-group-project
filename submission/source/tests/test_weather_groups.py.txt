import json
import unittest
from pathlib import Path
from scripts.evaluate_weather_groups import fit_thresholds, classify


class WeatherGroupTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((Path(__file__).resolve().parents[1] / 'config/weather_groups.json').read_text())
        self.rows = [{'county_fips': '01001', 'year': str(2000+i), 'partition': 'train', 'season_tmax_mean_c': str(i), 'season_precipitation_total_mm': str(i*10)} for i in range(17)]

    def test_heldout_weather_does_not_change_thresholds(self):
        original = fit_thresholds(self.rows, self.config)
        future = {**self.rows[0], 'partition': 'test', 'year': '2025', 'season_tmax_mean_c': '1000'}
        self.assertEqual(original, fit_thresholds(self.rows + [future], self.config))

    def test_overlap_and_normal_are_correct(self):
        thresholds = fit_thresholds(self.rows, self.config)
        row = {**self.rows[0], 'season_tmax_mean_c': '20', 'season_precipitation_total_mm': '0'}
        groups = classify(row, thresholds, self.config)
        self.assertEqual(set(groups), {'all', 'hot', 'dry', 'hot_dry', 'extreme_any'})
        row.update(season_tmax_mean_c='8', season_precipitation_total_mm='80')
        self.assertEqual(classify(row, thresholds, self.config), ['all', 'normal'])

    def test_short_history_is_unclassified_not_normal(self):
        thresholds = fit_thresholds(self.rows[:9], self.config)
        self.assertEqual(classify(self.rows[0], thresholds, self.config), ['all', 'unclassified'])
