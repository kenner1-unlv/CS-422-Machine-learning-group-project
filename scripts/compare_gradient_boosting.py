from pathlib import Path

import matplotlib
matplotlib.use('Agg') # save figures to files without opening a window
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1] # project folder

# Compares saved Gradient Boosting predictions with the team's saved Linear/Ridge predictions.
# Nothing is retrained here, it only reads predictions.csv files and scores them on the same rows.
# Run after scripts/run_gradient_boosting.py.

gb_dir = ROOT / 'results/primary_100_gradient_boosting' # Gradient Boosting results
lr_dir = ROOT / 'results/primary_100_baselines' # team's Linear/Ridge results
out = ROOT / 'results/gradient_boosting_comparison' # where comparison is saved
fig_dir = out / 'figures'
fig_dir.mkdir(parents=True, exist_ok=True)

# chart colors (reference palette slots 1-3, colorblind-safe as a set)
BLUE = '#2a78d6'
ORANGE = '#eb6834'
AQUA = '#1baf7a'
INK = '#0b0b0b'
MUTED = '#52514e'
GRID = '#e4e3df'
plt.rcParams.update({'font.size': 10, 'axes.edgecolor': MUTED, 'axes.labelcolor': INK, 'xtick.color': MUTED, 'ytick.color': MUTED, 'axes.spines.top': False, 'axes.spines.right': False, 'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.8, 'axes.axisbelow': True, 'figure.dpi': 150, 'savefig.bbox': 'tight'})

cutoff_names = {5: 'May', 6: 'June', 7: 'July', 8: 'August'}


# MAE, RMSE, R², bias (bushels per acre) from observed and predicted columns
def score(df):
	error = df['observed_yield'] - df['predicted_yield'] # residual
	ss_res = (error ** 2).sum()
	ss_tot = ((df['observed_yield'] - df['observed_yield'].mean()) ** 2).sum()
	years = df['year'].nunique() if 'year' in df else 1 # yearly tables group by year already
	return pd.Series({'n': len(df), 'years': years, 'mae': error.abs().mean(), 'rmse': np.sqrt((error ** 2).mean()), 'r2': 1 - ss_res / ss_tot, 'bias_predicted_minus_observed': -error.mean()})


#Data Audit
gb = pd.read_csv(gb_dir / 'predictions.csv', dtype={'county_fips': str})
lr = pd.read_csv(lr_dir / 'predictions.csv', dtype={'county_fips': str})
gb['model'] = gb['model'].map({'gbr_default': 'gb_default', 'gbr_tuned': 'gradient_boosting'}) # shorter names
lr = lr[lr['model'].isin(['linear', 'ridge', 'training_mean'])]
preds = pd.concat([lr, gb], ignore_index=True)
preds = preds[preds['partition'].isin(['validation', 'test'])] # held-out years only
print('Data Audit')
print(f'Held-out prediction rows: {len(preds)}')
print(preds.groupby(['model', 'variant']).size())

# every model has to predict exactly the same county-years, with the same observed yield
keys = ['county_fips', 'year', 'cutoff_month', 'partition']
linear_rows = lr[(lr['model'] == 'linear') & (lr['variant'] == 'weather_only') & lr['partition'].isin(['validation', 'test'])]
ref = linear_rows[keys + ['observed_yield']].sort_values(keys).reset_index(drop=True)
for (model, variant), group in preds.groupby(['model', 'variant']):
	rows = group[keys + ['observed_yield']].sort_values(keys).reset_index(drop=True)
	if not rows.equals(ref):
		raise ValueError(f'{model} {variant} does not predict the same rows as Linear')
print('Row check passed: all models scored on identical county-years')


#Task 1: overall comparison
overall = preds.groupby(['cutoff_month', 'variant', 'model', 'partition']).apply(score, include_groups=False).reset_index()

# Linear/Ridge scores recomputed here have to match the team's published metrics.csv
published = pd.read_csv(lr_dir / 'metrics.csv')
check = overall.merge(published, on=['cutoff_month', 'variant', 'model', 'partition'], suffixes=('', '_published'))
if len(check) == 0 or not np.allclose(check['mae'], check['mae_published'], atol=1e-9):
	raise ValueError('Recomputed Linear/Ridge MAE disagrees with published metrics')
print(f'Linear/Ridge recomputation matches published metrics ({len(check)} rows)')
overall.to_csv(out / 'comparison.csv', index=False)

# yearly test scores
test_preds = preds[preds['partition'] == 'test']
yearly = test_preds.groupby(['cutoff_month', 'variant', 'model', 'year']).apply(score, include_groups=False).reset_index()
yearly.to_csv(out / 'comparison_by_year.csv', index=False)


#Task 2: weather groups (dry vs normal etc.)
# uses the team's saved labels: thresholds were fit on training weather only (see config/weather_groups.json)
labels = pd.read_csv(ROOT / 'results/weather_groups/heldout_weather_labels.csv', dtype={'county_fips': str})
labels = labels[labels['coverage_set'] == 'primary_100']
labels['group'] = labels['groups'].str.split('|') # 'all|dry|hot' -> ['all', 'dry', 'hot']
labels = labels.explode('group')[['county_fips', 'year', 'cutoff_month', 'group']] # one row per group
grouped = preds.merge(labels, on=['county_fips', 'year', 'cutoff_month'], how='inner')
if grouped[grouped['group'] == 'all'].shape[0] != len(preds): # every row needs a label
	raise ValueError('Some held-out rows have no weather label')
subgroups = grouped.groupby(['cutoff_month', 'variant', 'model', 'partition', 'group']).apply(score, include_groups=False).reset_index()

# Linear/Ridge subgroup scores have to match the team's published weather-group results
team = pd.read_csv(ROOT / 'results/weather_groups/subgroup_metrics.csv', dtype={'coverage_set': str})
team = team[(team['coverage_set'] == 'primary_100') & (team['population'].str.startswith('own_'))]
check = subgroups.merge(team, on=['cutoff_month', 'variant', 'model', 'partition', 'group'], suffixes=('', '_team'))
if len(check) == 0 or not np.allclose(check['mae'], check['mae_team'], atol=1e-9) or not (check['n'] == check['n_team']).all():
	raise ValueError('Subgroup scores disagree with published weather-group results')
print(f'Weather-group recomputation matches published results ({len(check)} rows)')
subgroups['small_sample'] = (subgroups['n'] < 30) | (subgroups['years'] < 3) # flag small groups
group_keys = ['cutoff_month', 'variant', 'model', 'partition']
normal = subgroups[subgroups['group'] == 'normal'].set_index(group_keys)['mae']
subgroups['mae_minus_normal'] = subgroups['mae'] - subgroups.set_index(group_keys).index.map(normal) # how much worse than normal
subgroups.to_csv(out / 'subgroup_comparison.csv', index=False)


#plot creation
test = overall[overall['partition'] == 'test']
cutoffs = sorted(test['cutoff_month'].unique())
x_labels = [cutoff_names[c] for c in cutoffs]

# 1. test MAE at each forecast cutoff
fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
for ax, variant, title in [(axes[0], 'weather_only', 'Weather only'), (axes[1], 'weather_plus_trend', 'Weather + year trend')]:
	series = [('linear', variant, 'Linear Regression', BLUE, 'o'), ('gradient_boosting', variant, 'Gradient Boosting', ORANGE, 's')]
	if variant == 'weather_plus_trend':
		series.append(('gradient_boosting', 'trend_residual', 'GB on trend residual (exploratory)', AQUA, '^'))
	for model, v, name, color, marker in series:
		s = test[(test['model'] == model) & (test['variant'] == v)].sort_values('cutoff_month')
		ax.plot(x_labels, s['mae'], color=color, marker=marker, markersize=6, linewidth=2, label=name)
	ref_mae = test[test['model'] == 'training_mean']['mae'].iloc[0] # same at every cutoff
	ax.axhline(ref_mae, color=MUTED, linestyle='--', linewidth=1)
	ax.text(len(cutoffs) - 1, ref_mae + 0.4, 'training-mean reference', color=MUTED, ha='right', fontsize=8)
	ax.set_title(title, color=INK)
	ax.set_xlabel('Forecast cutoff (end of month)')
	ax.legend(frameon=False, fontsize=8, loc='upper right', bbox_to_anchor=(1, 0.92)) # under the reference label, above the lines
axes[0].set_ylabel('Test MAE (bu/acre), 2021-2025')
fig.suptitle('Test error by forecast cutoff, 393 primary counties', color=INK)
fig.savefig(fig_dir / 'mae_by_cutoff.png')
plt.close(fig)

# 2. predicted vs actual, July, test years, trend variant
july = preds[(preds['partition'] == 'test') & (preds['cutoff_month'] == 7) & (preds['variant'] == 'weather_plus_trend')]
fig, axes = plt.subplots(1, 2, figsize=(10, 4.6), sharex=True, sharey=True)
min_val = min(july['observed_yield'].min(), july['predicted_yield'].min()) - 5
max_val = max(july['observed_yield'].max(), july['predicted_yield'].max()) + 5
for ax, model, name, color in [(axes[0], 'linear', 'Linear Regression', BLUE), (axes[1], 'gradient_boosting', 'Gradient Boosting', ORANGE)]:
	s = july[july['model'] == model]
	ax.scatter(s['observed_yield'], s['predicted_yield'], s=8, alpha=0.35, color=color, edgecolors='none')
	ax.plot([min_val, max_val], [min_val, max_val], color=MUTED, linewidth=1, linestyle='--') # perfect prediction line
	m = test[(test['model'] == model) & (test['variant'] == 'weather_plus_trend') & (test['cutoff_month'] == 7)].iloc[0]
	ax.set_title(f"{name}: MAE {m['mae']:.1f}, R² {m['r2']:.2f}", color=INK)
	ax.set_xlabel('Observed yield (bu/acre)')
	ax.set_xlim(min_val, max_val)
	ax.set_ylim(min_val, max_val)
axes[0].set_ylabel('Predicted yield (bu/acre)')
fig.suptitle('July forecasts vs observed, test 2021-2025 (weather + trend; dashed = perfect)', color=INK)
fig.savefig(fig_dir / 'predicted_vs_actual_july.png')
plt.close(fig)

# 3. residual distributions, July, test years, trend variant
fig, ax = plt.subplots(figsize=(7, 4))
bins = np.linspace(-150, 100, 51)
for model, name, color in [('linear', 'Linear Regression', BLUE), ('gradient_boosting', 'Gradient Boosting', ORANGE)]:
	residual = july[july['model'] == model]['residual_observed_minus_predicted']
	ax.hist(residual, bins=bins, histtype='step', linewidth=2, color=color, label=f'{name} (median {residual.median():.1f})')
ax.axvline(0, color=MUTED, linewidth=1, linestyle='--')
ax.set_xlabel('Residual: observed minus predicted (bu/acre); negative = over-predicted')
ax.set_ylabel('County-years')
ax.set_title('July residuals, test 2021-2025 (weather + trend)', color=INK)
ax.legend(frameon=False)
fig.savefig(fig_dir / 'residuals_july.png')
plt.close(fig)

# 4. permutation feature importance, July tuned models
importance = pd.read_csv(gb_dir / 'feature_importance.csv')
fig, axes = plt.subplots(1, 2, figsize=(11, 5))
for ax, variant, title in [(axes[0], 'weather_only', 'Weather only'), (axes[1], 'weather_plus_trend', 'Weather + year trend')]:
	s = importance[(importance['cutoff_month'] == 7) & (importance['variant'] == variant)]
	s = s.nlargest(12, 'permutation_mae_increase_validation').iloc[::-1] # top 12, biggest at the top
	ax.barh(s['feature'], s['permutation_mae_increase_validation'], xerr=s['permutation_std'], color=ORANGE, height=0.6, error_kw={'ecolor': MUTED, 'linewidth': 1})
	ax.set_title(title, color=INK)
	ax.set_xlabel('Validation MAE increase when shuffled (bu/acre)')
	ax.tick_params(axis='y', labelsize=8)
	ax.grid(axis='y', visible=False)
fig.suptitle('Gradient Boosting July: top features (permutation importance, validation 2017-2020)', color=INK)
fig.tight_layout()
fig.savefig(fig_dir / 'feature_importance_july.png')
plt.close(fig)

# 5. dry vs normal: test MAE per weather group, July
groups = ['normal', 'dry', 'hot', 'wet', 'hot_dry']
s = subgroups[(subgroups['partition'] == 'test') & (subgroups['cutoff_month'] == 7)]
fig, ax = plt.subplots(figsize=(9, 4.2))
width = 0.27
xs = np.arange(len(groups))
bar_series = [(-width, 'linear', 'weather_plus_trend', 'Linear Regression', BLUE), (0, 'gradient_boosting', 'weather_plus_trend', 'Gradient Boosting', ORANGE), (width, 'gradient_boosting', 'trend_residual', 'GB on trend residual (exploratory)', AQUA)]
for offset, model, variant, name, color in bar_series:
	vals = s[(s['model'] == model) & (s['variant'] == variant)].set_index('group').reindex(groups)
	bars = ax.bar(xs + offset, vals['mae'], width=width - 0.03, color=color, label=name)
	ax.bar_label(bars, fmt='%.1f', fontsize=8, color=INK, padding=2)
counts = s[(s['model'] == 'linear') & (s['variant'] == 'weather_plus_trend')].set_index('group').reindex(groups)['n']
ax.set_xticks(xs, [f'{g}\n(n={int(n)})' for g, n in zip(groups, counts)])
ax.set_ylabel('Test MAE (bu/acre)')
ax.set_title('July test error by weather group, 2021-2025 (weather + trend)', color=INK)
ax.legend(frameon=False, loc='upper right')
ax.grid(axis='x', visible=False)
fig.savefig(fig_dir / 'weather_groups_july.png')
plt.close(fig)
print(f'Saved figures to {fig_dir}')


#summary tables
lines = ['# Gradient Boosting vs Linear Regression: primary 393 counties', '', "All models are scored on the same county-years (checked). Linear/Ridge numbers are recomputed from the team's saved predictions and match the published metrics. MAE/RMSE in bushels per acre. Gradient Boosting = validation-tuned model (`gbr_tuned`).", '']
for partition, heading in [('validation', 'Validation 2017-2020 (used for tuning)'), ('test', 'Test 2021-2025 (scored once after selection)')]:
	lines += [f'## {heading}', '', '| Cutoff | Variant | Linear MAE | Ridge MAE | GB MAE | Linear RMSE | GB RMSE | Linear R² | GB R² | n |', '|---|---|---:|---:|---:|---:|---:|---:|---:|---:|']
	o = overall[overall['partition'] == partition].set_index(['cutoff_month', 'variant', 'model'])
	for c in cutoffs:
		for v in ['weather_only', 'weather_plus_trend']:
			a = o.loc[(c, v, 'linear')]
			r = o.loc[(c, v, 'ridge')]
			g = o.loc[(c, v, 'gradient_boosting')]
			lines.append(f"| {cutoff_names[c]} | {v} | {a['mae']:.2f} | {r['mae']:.2f} | {g['mae']:.2f} | {a['rmse']:.2f} | {g['rmse']:.2f} | {a['r2']:.3f} | {g['r2']:.3f} | {int(a['n'])} |")
		g = o.loc[(c, 'trend_residual', 'gradient_boosting')]
		lines.append(f"| {cutoff_names[c]} | trend_residual (exploratory) | - | - | {g['mae']:.2f} | - | {g['rmse']:.2f} | - | {g['r2']:.3f} | {int(g['n'])} |")
	lines.append('')
lines += ['## Test MAE by weather group (July, weather + trend)', '', '| Group | n | Years | Linear MAE | GB MAE | GB trend_residual MAE | Linear minus normal | GB minus normal |', '|---|---:|---:|---:|---:|---:|---:|---:|']
w = subgroups[(subgroups['partition'] == 'test') & (subgroups['cutoff_month'] == 7)].set_index(['variant', 'model', 'group'])
for group in ['normal', 'extreme_any', 'dry', 'hot', 'wet', 'hot_dry']:
	a = w.loc[('weather_plus_trend', 'linear', group)]
	g = w.loc[('weather_plus_trend', 'gradient_boosting', group)]
	t = w.loc[('trend_residual', 'gradient_boosting', group)]
	flag = ' (small)' if a['small_sample'] else ''
	lines.append(f"| {group}{flag} | {int(a['n'])} | {int(a['years'])} | {a['mae']:.2f} | {g['mae']:.2f} | {t['mae']:.2f} | {a['mae_minus_normal']:+.2f} | {g['mae_minus_normal']:+.2f} |")
lines += ['', '## Dry minus normal test MAE at every cutoff', '', '| Cutoff | Variant | Linear | Gradient Boosting |', '|---|---|---:|---:|']
for c in cutoffs:
	for v in ['weather_only', 'weather_plus_trend', 'trend_residual']:
		dry = subgroups[(subgroups['partition'] == 'test') & (subgroups['cutoff_month'] == c) & (subgroups['variant'] == v) & (subgroups['group'] == 'dry')].set_index('model')['mae_minus_normal']
		lin = f"{dry['linear']:+.2f}" if 'linear' in dry else '-' # no Linear version of trend_residual
		lines.append(f"| {cutoff_names[c]} | {v} | {lin} | {dry['gradient_boosting']:+.2f} |")
lines += ['', "Groups overlap and are exploratory (definitions fixed after the team's overall test scores were visible). Five test years; county-years within a year are correlated. No significance claims. Full numbers: comparison.csv, comparison_by_year.csv, subgroup_comparison.csv. Figures: figures/."]
(out / 'README.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
print('\n'.join(lines))
