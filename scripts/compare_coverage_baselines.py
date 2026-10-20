"""Compare fixed baseline runs on own test rows and shared primary test rows."""
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SETS = ['primary_100', 'expanded_90', 'expanded_80', 'largest_available']


def summarize_errors(errors):
    n = len(errors)
    if not n:
        raise ValueError('Empty evaluation population')
    return {'mae': math.fsum(abs(e) for e in errors) / n, 'rmse': math.sqrt(math.fsum(e * e for e in errors) / n), 'n': n}


def main():
    root = ROOT / 'results'
    out = root / 'coverage_comparison'
    out.mkdir(exist_ok=True)
    primary = {}
    with (ROOT / 'data/features/primary_100/cutoff_05.csv').open(newline='') as f:
        for r in csv.DictReader(f):
            if r['partition'] == 'test':
                primary[(r['county_fips'], int(r['year']))] = float(r['yield_bu_per_acre'])
    if len(primary) != 1965:
        raise ValueError('Primary test population changed')
    records, annual, hashes = [], [], {}
    reference_selection = json.loads((root / 'primary_100_baselines/selection.json').read_text())
    for name in SETS:
        folder = root / (name + '_baselines')
        selection = json.loads((folder / 'selection.json').read_text())
        for field in ('variants', 'ridge_alphas', 'refit_on_validation', 'selection_metric'):
            if selection['config'][field] != reference_selection['config'][field]:
                raise ValueError('Baseline protocol changed across sets')
        path = folder / 'predictions.csv'
        h = hashlib.sha256()
        with path.open('rb') as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b''):
                h.update(chunk)
        hashes[str(path.relative_to(ROOT))] = h.hexdigest()
        errors, by_year = defaultdict(list), defaultdict(list)
        shared_keys, full_keys = defaultdict(set), defaultdict(set)
        with path.open(newline='') as f:
            for r in csv.DictReader(f):
                if r['partition'] != 'test':
                    continue
                year, cutoff = int(r['year']), int(r['cutoff_month'])
                if not 2021 <= year <= 2025:
                    raise ValueError('Test years changed')
                key = (r['county_fips'], year)
                group = (cutoff, r['variant'], r['model'])
                if key in full_keys[group]:
                    raise ValueError('Duplicate test prediction')
                full_keys[group].add(key)
                actual, pred = float(r['observed_yield']), float(r['predicted_yield'])
                if not math.isfinite(actual) or not math.isfinite(pred):
                    raise ValueError('Nonfinite prediction')
                error = actual - pred
                errors[('own_test', *group)].append(error)
                by_year[('own_test', *group, year)].append(error)
                if key in primary:
                    if actual != primary[key]:
                        raise ValueError('Shared target changed')
                    errors[('shared_393_test', *group)].append(error)
                    by_year[('shared_393_test', *group, year)].append(error)
                    shared_keys[group].add(key)
        if len(full_keys) != 20 or any(v != set(primary) for v in shared_keys.values()) or len(shared_keys) != 20:
            raise ValueError('Incomplete models, cutoffs or shared population')
        for (population, cutoff, variant, model), e in sorted(errors.items()):
            records.append({'coverage_set': name, 'population': population, 'cutoff_month': cutoff, 'variant': variant, 'model': model, **summarize_errors(e)})
        for (population, cutoff, variant, model, year), e in sorted(by_year.items()):
            annual.append({'coverage_set': name, 'population': population, 'cutoff_month': cutoff, 'variant': variant, 'model': model, 'year': year, **summarize_errors(e)})
        own_metrics = list(csv.DictReader((folder / 'metrics.csv').open()))
        for r in records:
            if r['coverage_set'] == name and r['population'] == 'own_test':
                original = next(m for m in own_metrics if m['partition'] == 'test' and int(m['cutoff_month']) == r['cutoff_month'] and m['variant'] == r['variant'] and m['model'] == r['model'])
                if not math.isclose(r['mae'], float(original['mae']), abs_tol=1e-9) or r['n'] != int(original['n']):
                    raise ValueError('Recomputed scores disagree with saved metrics')
    baseline = {(r['population'], r['cutoff_month'], r['variant'], r['model']): r['mae'] for r in records if r['coverage_set'] == 'primary_100'}
    for r in records:
        r['mae_minus_primary_same_model'] = r['mae'] - baseline[(r['population'], r['cutoff_month'], r['variant'], r['model'])]
    for filename, rows in [('comparison.csv', records), ('comparison_by_year.csv', annual)]:
        with (out / filename).open('w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    (out / 'provenance.json').write_text(json.dumps({'predictions_sha256': hashes, 'years': [2021, 2025], 'shared_county_years': len(primary), 'note': 'Same feature recipe, years, scaling procedure and tuning grid; scalers and coefficients fit separately to each training population. Ridge alpha selected within each set using its validation rows. Existing primary results are read-only.'}, indent=2) + '\n')
    lines = ['# Coverage comparison: Linear and Ridge', '', 'Fixed train 2000-2016, validation 2017-2020, test 2021-2025. Units: bushels per acre. No retraining on validation years; no test-based hyperparameter selection. Primary results are preserved.', '', 'The same-row comparison evaluates every trained model on the original 393 counties (1,965 county-years). It isolates a common test population, while each model still has its own training scaler and validation-selected Ridge alpha. The own-population comparison changes both training and tested counties; differences are descriptive, not proof that more training data caused better/worse predictions.', '']
    for population, heading in [('shared_393_test', 'Shared 393-county test population'), ('own_test', 'Each coverage set on its own test population')]:
        lines += ['## ' + heading, '', '| Variant | Model | Cutoff | Primary MAE | 90% MAE | 80% MAE | Largest MAE |', '|---|---|---|---:|---:|---:|---:|']
        for variant in ('weather_only', 'weather_plus_trend'):
            for model in ('linear', 'ridge'):
                for cutoff in (5, 6, 7, 8):
                    values = [next(r['mae'] for r in records if r['population'] == population and r['coverage_set'] == s and r['cutoff_month'] == cutoff and r['variant'] == variant and r['model'] == model) for s in SETS]
                    lines.append(f'| {variant} | {model} | {cutoff:02} | ' + ' | '.join(f'{v:.2f}' for v in values) + ' |')
        lines.append('')
    lines += ['All metrics, including RMSE, sample sizes, baseline scores, deltas and yearly results, are in the CSVs. A negative delta indicates lower MAE than the corresponding primary model, not statistical significance. No confidence intervals or extreme-weather subgroup conclusions are claimed. The initial primary test outcomes were already inspected before these planned coverage runs; these comparisons are not a new untouched holdout. Do not select coverage, features or hyperparameters by test results.']
    (out / 'README.md').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
