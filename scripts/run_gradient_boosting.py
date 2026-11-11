import hashlib
import itertools
import json
import platform
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from joblib import Parallel, delayed
from sklearn.inspection import permutation_importance
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

ROOT = Path(__file__).resolve().parents[1] # project folder
sys.path.insert(0, str(ROOT)) # so scripts/ can be imported
from scripts.gradient_boosting_model import make_model, score_setting, best_tree_count

# Gradient Boosting: train on 2000-2016, pick settings on 2017-2020, then score the frozen models.
# Same rules as run_baselines.py (Linear/Ridge): manifest feature lists only, no refit on validation,
# and selection.json is saved BEFORE any test prediction is made.

config_path = ROOT / 'config/gradient_boosting.json' # change to a smaller config for a quick test run
out = ROOT / 'results/primary_100_gradient_boosting' # where results are saved
n_jobs = -1 # CPU cores for tuning, -1 = all

config = json.loads(config_path.read_text()) # grid, seed, variants
splits = json.loads((ROOT / 'config/splits.json').read_text()) # shared split years
manifest = json.loads((ROOT / 'data/features/feature_manifest.json').read_text()) # shared feature lists
split_summary = json.loads((ROOT / 'data/study_sets/split_summary.json').read_text()) # expected row counts

if config['refit_on_validation']:
	raise ValueError('This protocol requires training-only fits')

coverage_set = config['coverage_set']
seed = config['random_state']
loss = config['loss']
max_trees = config['max_n_estimators']
variants = config['shared_variants'] + config['exploratory_variants']
expected_counts = {p: s['county_years'] for p, s in split_summary['sets'][coverage_set].items()}
(out / 'models').mkdir(parents=True, exist_ok=True)

# every combination of the grid (n_estimators is picked separately from 1 to max_trees)
grid_keys = sorted(config['grid'])
grid = []
for values in itertools.product(*[config['grid'][k] for k in grid_keys]):
	grid.append(dict(zip(grid_keys, values)))
print(f'Grid size: {len(grid)} settings x up to {max_trees} trees')


def file_hash(path):
	return hashlib.sha256(Path(path).read_bytes()).hexdigest() # fingerprint of an input file


def get_metrics(actual, predicted):
	mae = mean_absolute_error(actual, predicted)
	rmse = np.sqrt(mean_squared_error(actual, predicted)) # use library mse
	r2 = r2_score(actual, predicted)
	return {'mae': float(mae), 'rmse': float(rmse), 'r2': float(r2), 'n': len(actual)}


def get_features(cutoff, variant):
	lists = manifest['features_by_cutoff'][str(cutoff)]
	if variant == 'weather_only':
		names = lists['weather_only']
	else:
		names = lists['weather_plus_trend'] # trend_residual uses this too (year is the last column)
	for name in names:
		if name in manifest['metadata_not_predictors']: # no county id, target, raw year, partition
			raise ValueError(f'{name} is not allowed as a predictor')
	if variant == 'trend_residual' and names[-1] != 'year_since_2000':
		raise ValueError('trend_residual needs year_since_2000 as the last column')
	return names


#Data Audit
print('Data Audit')
data = {}
hashes = {}
for cutoff in splits['forecast_cutoff_months']:
	path = ROOT / 'data/features' / coverage_set / f'cutoff_{cutoff:02}.csv'
	df = pd.read_csv(path, dtype={'county_fips': str}) # keep FIPS as text (leading zeros)
	hashes[str(path.relative_to(ROOT))] = file_hash(path)

	if df.duplicated(['county_fips', 'year']).any(): # one row per county-year
		raise ValueError('Duplicate feature keys')
	for p, (lo, hi) in splits['partitions'].items(): # partition has to match the shared years
		in_years = df['year'].between(lo, hi)
		if not (in_years == (df['partition'] == p)).all():
			raise ValueError(f'Partition {p} does not match years {lo}-{hi}')
	counts = df['partition'].value_counts().to_dict()
	if counts != expected_counts: # same rows as the Linear/Ridge run
		raise ValueError(f'Split counts changed: {counts}')
	print(f'Cutoff {cutoff:02}: {df.shape[0]} rows {counts}')
	data[cutoff] = df
print(f"Target: yield_bu_per_acre, missing: {data[5]['yield_bu_per_acre'].isna().sum()}")


#Task 1: tuning on validation only (test rows are never used here)
print('Tuning')
decisions = {}
tuning_rows = []
models = {}
for cutoff, df in data.items():
	decisions[str(cutoff)] = {}
	train = df[df['partition'] == 'train'] # 2000-2016
	val = df[df['partition'] == 'validation'] # 2017-2020
	Y_train = train['yield_bu_per_acre'].values
	Y_val = val['yield_bu_per_acre'].values

	for variant in variants:
		names = get_features(cutoff, variant)
		X_train = train[names].values
		X_val = val[names].values

		# baseline GBR with scikit-learn default settings
		default = make_model(variant, config['default_model'], seed, loss)
		default.fit(X_train, Y_train)

		# each grid setting is fit in parallel, then every tree count is scored on validation
		results = Parallel(n_jobs=n_jobs)(delayed(score_setting)(variant, params, max_trees, seed, loss, X_train, Y_train, X_val, Y_val) for params in grid)
		candidates = []
		for params, (mae_list, rmse_list) in zip(grid, results):
			n = best_tree_count(mae_list, rmse_list) # best tree count for this setting
			row = dict(params)
			row['n_estimators'] = n
			row['validation_mae'] = mae_list[n - 1]
			row['validation_rmse'] = rmse_list[n - 1]
			row['validation_mae_at_max_trees'] = mae_list[-1]
			candidates.append(row)
			tuning_rows.append({'cutoff_month': cutoff, 'variant': variant, **row})

		# best setting: lowest validation MAE, ties -> RMSE, shallower trees, fewer trees
		candidates.sort(key=lambda c: (c['validation_mae'], c['validation_rmse'], c['max_depth'], c['n_estimators']))
		chosen = candidates[0]
		params = {}
		for k in ['n_estimators', 'learning_rate', 'max_depth', 'subsample', 'min_samples_leaf']:
			params[k] = chosen[k]
		tuned = make_model(variant, params, seed, loss)
		tuned.fit(X_train, Y_train)

		# refitting with the chosen tree count has to give the same validation score
		refit_mae = mean_absolute_error(Y_val, tuned.predict(X_val))
		if not np.isclose(refit_mae, chosen['validation_mae'], atol=1e-9):
			raise ValueError('Refit does not reproduce staged validation score')

		models[(cutoff, variant, 'gbr_default')] = (default, names, config['default_model'])
		models[(cutoff, variant, 'gbr_tuned')] = (tuned, names, params)
		decisions[str(cutoff)][variant] = {'chosen': chosen, 'default_validation': get_metrics(Y_val, default.predict(X_val)), 'train_rows': len(train), 'validation_rows': len(val), 'predictors': names}
		print(f"Cutoff {cutoff:02} {variant}: validation MAE {chosen['validation_mae']:.2f} with {params}", flush=True)

# save every decision BEFORE making any test prediction
selection = {'config': config, 'config_sha256': file_hash(config_path), 'decisions': decisions, 'input_sha256': hashes, 'python': platform.python_version(), 'numpy': np.__version__, 'pandas': pd.__version__, 'sklearn': sklearn.__version__, 'note': 'All fits use training years only; hyperparameters chosen by validation MAE. Written before any test prediction was computed.'}
(out / 'selection.json').write_text(json.dumps(selection, indent=2) + '\n')
pd.DataFrame(tuning_rows).to_csv(out / 'tuning.csv', index=False)


#Task 2: scoring the frozen models (train, validation, test)
print('Scoring')
metric_rows = []
yearly_rows = []
prediction_frames = []
importance_rows = []
for (cutoff, variant, model_name), (model, names, params) in models.items():
	df = data[cutoff]
	joblib.dump(model, out / 'models' / f'{variant}_{model_name}_{cutoff:02}.joblib') # save fitted model
	predicted = model.predict(df[names].values) # predict every row once
	actual = df['yield_bu_per_acre'].values

	for p in splits['partitions']: # train, validation, test
		mask = (df['partition'] == p).values
		metric_rows.append({'cutoff_month': cutoff, 'variant': variant, 'model': model_name, 'partition': p, **get_metrics(actual[mask], predicted[mask]), 'params': json.dumps(params, sort_keys=True)})
		for year in sorted(df.loc[mask, 'year'].unique()): # scores per year
			year_mask = mask & (df['year'] == year).values
			yearly_rows.append({'cutoff_month': cutoff, 'variant': variant, 'model': model_name, 'partition': p, 'year': int(year), **get_metrics(actual[year_mask], predicted[year_mask])})

	# row-level predictions, same columns as the Linear/Ridge predictions.csv
	prediction_frames.append(pd.DataFrame({'county_fips': df['county_fips'], 'year': df['year'], 'cutoff_month': cutoff, 'partition': df['partition'], 'variant': variant, 'model': model_name, 'observed_yield': actual, 'predicted_yield': predicted, 'residual_observed_minus_predicted': actual - predicted}))

	# feature importance for the tuned model
	# permutation: how much validation MAE goes up when one column is shuffled (validation, not test)
	# impurity: scikit-learn's built-in split importance from training
	if model_name == 'gbr_tuned':
		val = df[df['partition'] == 'validation']
		perm = permutation_importance(model, val[names].values, val['yield_bu_per_acre'].values, scoring='neg_mean_absolute_error', n_repeats=config['permutation_repeats'], random_state=seed, n_jobs=n_jobs)
		if variant == 'trend_residual':
			impurity = model.boost_.feature_importances_ # trees only see weather, so year has none
		else:
			impurity = model.feature_importances_
		for i, feature in enumerate(names):
			impurity_value = impurity[i] if i < len(impurity) else np.nan
			importance_rows.append({'cutoff_month': cutoff, 'variant': variant, 'model': model_name, 'feature': feature, 'permutation_mae_increase_validation': perm.importances_mean[i], 'permutation_std': perm.importances_std[i], 'impurity_importance_train': impurity_value})

metrics = pd.DataFrame(metric_rows)
metrics.to_csv(out / 'metrics.csv', index=False)
pd.DataFrame(yearly_rows).to_csv(out / 'metrics_by_year.csv', index=False)
pd.concat(prediction_frames).to_csv(out / 'predictions.csv', index=False)
pd.DataFrame(importance_rows).to_csv(out / 'feature_importance.csv', index=False)


#results table
lines = [f'# {coverage_set} Gradient Boosting', '', 'Train 2000-2016, validation 2017-2020, test 2021-2025. Hyperparameters selected by validation MAE only; no refit on validation years. `gbr_default` uses scikit-learn defaults; `gbr_tuned` is the validation-selected model. `trend_residual` is an exploratory variant (linear year trend + boosted weather residual), not part of the shared comparison. MAE/RMSE in bushels per acre.', '', '| Cutoff | Variant | Model | Trees | LR | Depth | Subsample | Min leaf | Train MAE | Validation MAE | Test MAE | Test RMSE | Test R² | Test n |', '|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|']
for (cutoff, variant, model_name), (model, names, params) in models.items():
	rows = metrics[(metrics['cutoff_month'] == cutoff) & (metrics['variant'] == variant) & (metrics['model'] == model_name)].set_index('partition')
	t = rows.loc['test']
	lines.append(f"| {cutoff:02} | {variant} | {model_name} | {params['n_estimators']} | {params['learning_rate']} | {params['max_depth']} | {params['subsample']} | {params['min_samples_leaf']} | {rows.loc['train', 'mae']:.2f} | {rows.loc['validation', 'mae']:.2f} | {t['mae']:.2f} | {t['rmse']:.2f} | {t['r2']:.3f} | {t['n']} |")
lines += ['', 'See GRADIENT_BOOSTING.md for method, comparison with Linear Regression, weather groups and limitations. selection.json records every decision, input hashes and package versions. Saved models load from the repository root (they need `scripts/gradient_boosting_model.py`); use only trusted local model files.']
(out / 'README.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print(f'Saved results to {out}')
