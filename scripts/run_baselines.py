"""Train on 2000-2016, select using 2017-2020, evaluate frozen models."""
import csv
import hashlib
import json
import platform
from pathlib import Path

import joblib
import numpy as np
import sklearn
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]


def make_pipeline(model, alpha=None):
    estimator = LinearRegression() if model == 'linear' else Ridge(alpha=alpha, solver='svd')
    return Pipeline([('scale', StandardScaler()), ('regression', estimator)])


def metrics(actual, predicted):
    return {'mae': float(mean_absolute_error(actual, predicted)), 'rmse': float(np.sqrt(mean_squared_error(actual, predicted))), 'n': len(actual)}


def write_csv(path, rows):
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    config = json.loads((ROOT / 'config/baselines.json').read_text())
    if config['coverage_set'] != 'primary_100' or config['refit_on_validation']:
        raise ValueError('This initial experiment requires the primary cohort and training-only fits')
    splits = json.loads((ROOT / 'config/splits.json').read_text())
    manifest = json.loads((ROOT / 'data/features/feature_manifest.json').read_text())
    source = ROOT / 'data/features' / config['coverage_set']
    out = ROOT / 'results' / 'primary_100_baselines'
    (out / 'models').mkdir(parents=True, exist_ok=True)
    tuning, decisions, fitted, datasets, hashes = [], {}, {}, {}, {}
    # Selection stage never evaluates test predictions or test metrics.
    for cutoff in splits['forecast_cutoff_months']:
        path = source / f'cutoff_{cutoff:02}.csv'
        hashes[path.name] = hashlib.sha256(path.read_bytes()).hexdigest()
        with path.open(newline='', encoding='utf-8') as f:
            rows = list(csv.DictReader(f))
        keys = [(r['county_fips'], int(r['year'])) for r in rows]
        if len(set(keys)) != len(keys):
            raise ValueError('Duplicate feature keys')
        masks = {p: np.array([r['partition'] == p for r in rows]) for p in splits['partitions']}
        for r in rows:
            year = int(r['year'])
            if [p for p, (lo, hi) in splits['partitions'].items() if lo <= year <= hi] != [r['partition']]:
                raise ValueError('Invalid partition')
        if {p: int(m.sum()) for p, m in masks.items()} != {'train': 6681, 'validation': 1572, 'test': 1965}:
            raise ValueError('Primary split counts changed')
        y = np.array([float(r['yield_bu_per_acre']) for r in rows])
        datasets[cutoff] = (rows, masks, y)
        choices = []
        for variant in config['variants']:
            names = manifest['features_by_cutoff'][str(cutoff)][variant]
            if set(names) & set(manifest['metadata_not_predictors']):
                raise ValueError('Metadata or target included in predictors')
            X = np.array([[float(r[n]) for n in names] for r in rows])
            if not np.isfinite(X).all() or not np.isfinite(y).all():
                raise ValueError('Nonfinite model input')
            train, val = masks['train'], masks['validation']
            linear = make_pipeline('linear').fit(X[train], y[train])
            score = metrics(y[val], linear.predict(X[val]))
            fitted[(cutoff, variant, 'linear')] = (linear, X, names, None)
            choices.append({'variant': variant, 'model': 'linear', 'alpha': None, **score})
            candidates = []
            for alpha in config['ridge_alphas']:
                pipeline = make_pipeline('ridge', alpha).fit(X[train], y[train])
                s = metrics(y[val], pipeline.predict(X[val]))
                record = {'cutoff_month': cutoff, 'variant': variant, 'alpha': alpha, **s}
                tuning.append(record)
                candidates.append((s['mae'], s['rmse'], alpha, pipeline, s))
            _, _, alpha, ridge, score = min(candidates, key=lambda c: c[:3])
            fitted[(cutoff, variant, 'ridge')] = (ridge, X, names, alpha)
            choices.append({'variant': variant, 'model': 'ridge', 'alpha': alpha, **score})
        decisions[str(cutoff)] = {'ridge_by_variant': {v: next(c for c in choices if c['variant'] == v and c['model'] == 'ridge') for v in config['variants']}, 'preferred_regression_by_validation': min(choices, key=lambda c: (c['mae'], c['rmse'])), 'all_candidates': choices}
    selection = {'config': config, 'ridge_tie_break': 'validation MAE, validation RMSE, then smaller alpha', 'decisions': decisions, 'input_sha256': hashes, 'python': platform.python_version(), 'numpy': np.__version__, 'sklearn': sklearn.__version__, 'note': 'All fits and scalers use training years only. Choices fixed before any test metrics are computed.'}
    (out / 'selection.json').write_text(json.dumps(selection, indent=2) + '\n')
    write_csv(out / 'ridge_tuning.csv', tuning)
    scores, annual, predictions, scales, coefficients = [], [], [], [], []
    for cutoff, (rows, masks, y) in datasets.items():
        mean = float(y[masks['train']].mean())
        experiments = [('reference', 'training_mean', np.full(len(y), mean), None)]
        for (c, variant, model), (pipeline, X, names, alpha) in fitted.items():
            if c != cutoff:
                continue
            scaler, estimator = pipeline['scale'], pipeline['regression']
            if scaler.n_samples_seen_ != int(masks['train'].sum()) or not np.allclose(scaler.mean_, X[masks['train']].mean(axis=0)):
                raise ValueError('Scaling did not use training data exclusively')
            joblib.dump(pipeline, out / 'models' / f'{variant}_{model}_{cutoff:02}.joblib')
            experiments.append((variant, model, pipeline.predict(X), alpha))
            for i, name in enumerate(names):
                scales.append({'cutoff_month': cutoff, 'variant': variant, 'model': model, 'feature': name, 'training_mean': scaler.mean_[i], 'training_scale': scaler.scale_[i]})
                coefficients.append({'cutoff_month': cutoff, 'variant': variant, 'model': model, 'feature': name, 'coefficient_standardized_input': estimator.coef_[i], 'intercept': estimator.intercept_})
        for variant, model, predicted, alpha in experiments:
            for p, mask in masks.items():
                scores.append({'cutoff_month': cutoff, 'variant': variant, 'model': model, 'alpha': alpha, 'partition': p, **metrics(y[mask], predicted[mask])})
                for year in sorted({int(r['year']) for r, use in zip(rows, mask) if use}):
                    ym = mask & np.array([int(r['year']) == year for r in rows])
                    annual.append({'cutoff_month': cutoff, 'variant': variant, 'model': model, 'partition': p, 'year': year, **metrics(y[ym], predicted[ym])})
            for r, actual, pred in zip(rows, y, predicted):
                predictions.append({'county_fips': r['county_fips'], 'year': r['year'], 'cutoff_month': cutoff, 'partition': r['partition'], 'variant': variant, 'model': model, 'observed_yield': actual, 'predicted_yield': float(pred), 'residual_observed_minus_predicted': float(actual - pred)})
    for filename, records in [('metrics.csv', scores), ('metrics_by_year.csv', annual), ('predictions.csv', predictions), ('scaling.csv', scales), ('coefficients.csv', coefficients)]:
        write_csv(out / filename, records)
    lines = ['# Primary cohort regression baselines', '', '393 complete counties; train 2000-2016, validation 2017-2020, test 2021-2025.', '', 'Scaling and models fit only training data. Ridge alpha selected by validation MAE. No refit on validation years. Weather-only is the core comparison; time trend is a named secondary variant. MAE and RMSE are in bushels per acre.', '', '| Cutoff | Variant | Model | Alpha | Validation MAE | Test MAE | Test RMSE | Test n |', '|---|---|---|---:|---:|---:|---:|---:|']
    for r in scores:
        if r['partition'] == 'test':
            v = next(v for v in scores if v['partition'] == 'validation' and all(v[k] == r[k] for k in ('cutoff_month', 'variant', 'model')))
            lines.append(f"| {r['cutoff_month']:02} | {r['variant']} | {r['model']} | {r['alpha'] if r['alpha'] is not None else '-'} | {v['mae']:.2f} | {r['mae']:.2f} | {r['rmse']:.2f} | {r['n']} |")
    lines += ['', 'These are initial results, not extreme-weather subgroup results. County-level errors within the same year are correlated. Overlapping monthly/cumulative predictors can make linear coefficients unstable; interpret predictive scores rather than causal coefficients. Predictions are not clipped to zero. Do not use these test results to retune or redefine features and still describe this test as untouched.', '', 'selection.json records validation decisions, input hashes and environment versions. Other files retain full precision, annual metrics, predictions, scaling parameters and coefficients. Saved model pipelines include their fitted scalers; use only trusted local model files.']
    (out / 'README.md').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
