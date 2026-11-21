import copy
import json
import unittest
from pathlib import Path
from scripts.build_splits import partition_for_year, validate_config


class SplitTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((Path(__file__).resolve().parents[1] / 'config/splits.json').read_text())

    def test_all_years_have_the_agreed_partition(self):
        validate_config(self.config)
        for year in range(2000, 2026):
            expected = 'train' if year <= 2016 else 'validation' if year <= 2020 else 'test'
            self.assertEqual(partition_for_year(year, self.config), expected)

    def test_rejects_years_outside_study(self):
        for year in (1999, 2026):
            with self.assertRaises(ValueError):
                partition_for_year(year, self.config)

    def test_rejects_overlap_and_gap(self):
        for start in (2016, 2018):
            bad = copy.deepcopy(self.config)
            bad['partitions']['validation'][0] = start
            with self.assertRaises(ValueError):
                validate_config(bad)
