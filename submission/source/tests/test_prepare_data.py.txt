import unittest

from scripts.prepare_data import normalize_county_name, parse_weather_value, summarize_days


class PrepareDataTests(unittest.TestCase):
    def test_normalizes_state_and_county_label_suffixes(self):
        self.assertEqual(normalize_county_name("Baldwin County"), "BALDWIN")
        self.assertEqual(normalize_county_name("St. Landry Parish"), "STLANDRY")

    def test_maps_noaa_missing_sentinels_to_none(self):
        self.assertIsNone(parse_weather_value("-999.99"))
        self.assertIsNone(parse_weather_value(""))
        self.assertEqual(parse_weather_value("0.00"), 0)

    def test_summarizes_without_imputing_missing_days(self):
        result = summarize_days([0.0, 10.0, None], "prcp")
        self.assertEqual(result["precipitation_total_mm"], 10)
        self.assertEqual(result["prcp_days_observed"], 2)
        self.assertEqual(result["prcp_days_missing"], 1)

    def test_all_missing_month_stays_missing(self):
        result = summarize_days([None, None], "tavg")
        self.assertEqual(result["tavg_mean_c"], "")
        self.assertEqual(result["tavg_days_observed"], 0)
        self.assertEqual(result["tavg_days_missing"], 2)


if __name__ == "__main__":
    unittest.main()
