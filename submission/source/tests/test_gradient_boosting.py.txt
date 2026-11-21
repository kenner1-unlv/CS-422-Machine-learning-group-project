import unittest

import numpy as np

from scripts.gradient_boosting_model import TrendResidualRegressor, best_tree_count, make_model, score_setting

PARAMS = {'n_estimators': 40, 'learning_rate': 0.1, 'max_depth': 2, 'subsample': 0.8, 'min_samples_leaf': 5}


# small fake dataset: 3 weather columns + year_since_2000 as the last column
def fake_data(years, seed=0):
	rng = np.random.default_rng(seed)
	year = np.repeat(years, 20).astype(float)
	weather = rng.normal(size=(len(year), 3))
	y = 100 + 2 * year + 5 * weather[:, 0] - 3 * weather[:, 1] ** 2 + rng.normal(scale=1, size=len(year))
	return np.column_stack([weather, year]), y


class GradientBoostingTests(unittest.TestCase):
	def test_same_seed_gives_same_predictions(self):
		X, y = fake_data(range(17))
		for variant in ['weather_plus_trend', 'trend_residual']:
			a = make_model(variant, PARAMS, 42).fit(X, y).predict(X)
			b = make_model(variant, PARAMS, 42).fit(X, y).predict(X)
			np.testing.assert_array_equal(a, b)

	def test_refit_with_chosen_trees_matches_staged_score(self):
		# the runner relies on this: scoring tree counts with staged_predict = refitting with that many trees
		X_train, y_train = fake_data(range(17))
		X_val, y_val = fake_data(range(17, 21), seed=1)
		for variant in ['weather_plus_trend', 'trend_residual']:
			mae_list, rmse_list = score_setting(variant, PARAMS, 40, 42, 'squared_error', X_train, y_train, X_val, y_val)
			n = best_tree_count(mae_list, rmse_list)
			refit = make_model(variant, {**PARAMS, 'n_estimators': n}, 42).fit(X_train, y_train)
			self.assertAlmostEqual(np.mean(np.abs(y_val - refit.predict(X_val))), mae_list[n - 1], places=9)

	def test_best_tree_count_ties_go_to_fewer_trees(self):
		self.assertEqual(best_tree_count(np.array([5., 3., 3., 4.]), np.array([5., 2., 2., 4.])), 2)
		self.assertEqual(best_tree_count(np.array([5., 3., 3.]), np.array([5., 2., 1.])), 3)

	def test_trees_cannot_extrapolate_trend_but_hybrid_can(self):
		# why trend_residual exists: train on years 0-16, predict year 25 (true trend value 100 + 2*25 = 150)
		X, y = fake_data(range(17))
		future = np.array([[0., 0., 0., 25.]])
		plain = make_model('weather_plus_trend', PARAMS, 42).fit(X, y).predict(future)[0]
		hybrid = make_model('trend_residual', PARAMS, 42).fit(X, y).predict(future)[0]
		self.assertLess(plain, 140)  # stuck near the last training year (~132)
		self.assertAlmostEqual(hybrid, 150, delta=5)

	def test_hybrid_trend_uses_only_last_column(self):
		X, y = fake_data(range(17))
		model = TrendResidualRegressor(**PARAMS, random_state=42).fit(X, y)
		self.assertEqual(model.boost_.n_features_in_, 3)  # weather only, year excluded from the trees
		self.assertAlmostEqual(model.trend_.coef_[0], 2, delta=0.2)


if __name__ == '__main__':
	unittest.main()
