import numpy as np
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.linear_model import LinearRegression

# Gradient Boosting models used by run_gradient_boosting.py and the tests.
# Kept in its own file so the saved .joblib models can be loaded again later.


def make_gbr(params, random_state, loss='squared_error'):
	return GradientBoostingRegressor(loss=loss, random_state=random_state, **params) # trees don't need scaling


# Exploratory model: straight-line year trend + Gradient Boosting on the weather.
# The LAST column of X has to be year_since_2000, the rest are the weather features.
# Trees can't predict past the years they were trained on (2000-2016), a straight line can.
class TrendResidualRegressor(BaseEstimator, RegressorMixin):
	def __init__(self, n_estimators=100, learning_rate=0.1, max_depth=3, subsample=1.0, min_samples_leaf=1, random_state=None, loss='squared_error'):
		self.n_estimators = n_estimators
		self.learning_rate = learning_rate
		self.max_depth = max_depth
		self.subsample = subsample
		self.min_samples_leaf = min_samples_leaf
		self.random_state = random_state
		self.loss = loss

	def fit(self, X, Y):
		X = np.asarray(X, dtype=float)
		Y = np.asarray(Y, dtype=float)
		year = X[:, -1:] # last column
		weather = X[:, :-1] # everything else
		self.trend_ = LinearRegression().fit(year, Y) # step 1: fit the year trend
		leftover = Y - self.trend_.predict(year) # what the trend didn't explain
		params = {'n_estimators': self.n_estimators, 'learning_rate': self.learning_rate, 'max_depth': self.max_depth, 'subsample': self.subsample, 'min_samples_leaf': self.min_samples_leaf}
		self.boost_ = make_gbr(params, self.random_state, self.loss).fit(weather, leftover) # step 2: boost on the leftover
		self.n_features_in_ = X.shape[1]
		return self

	def predict(self, X):
		X = np.asarray(X, dtype=float)
		return self.trend_.predict(X[:, -1:]) + self.boost_.predict(X[:, :-1]) # trend + weather adjustment

	def staged_predict(self, X):
		X = np.asarray(X, dtype=float)
		trend = self.trend_.predict(X[:, -1:])
		for stage in self.boost_.staged_predict(X[:, :-1]): # prediction after 1 tree, 2 trees, ...
			yield trend + stage


def make_model(variant, params, random_state, loss='squared_error'):
	if variant == 'trend_residual':
		return TrendResidualRegressor(random_state=random_state, loss=loss, **params)
	return make_gbr(params, random_state, loss)


# Fits one setting with the max number of trees, then scores every tree count on VALIDATION only.
# Only train and validation data are passed in, so test data can't affect tuning.
def score_setting(variant, params, max_trees, random_state, loss, X_train, Y_train, X_val, Y_val):
	settings = dict(params)
	settings['n_estimators'] = max_trees
	model = make_model(variant, settings, random_state, loss)
	model.fit(X_train, Y_train)
	mae_list = []
	rmse_list = []
	for predicted in model.staged_predict(X_val): # one prediction per tree count
		error = Y_val - predicted
		mae_list.append(float(np.mean(np.abs(error))))
		rmse_list.append(float(np.sqrt(np.mean(error ** 2))))
	return np.array(mae_list), np.array(rmse_list)


# best tree count: lowest validation MAE, then RMSE, then fewer trees
def best_tree_count(mae_list, rmse_list):
	order = list(range(len(mae_list)))
	order.sort(key=lambda i: (mae_list[i], rmse_list[i], i)) # sort by mae, rmse, tree count
	return order[0] + 1 # index 0 = 1 tree
