"""Exploratory weather-group evaluation of frozen baseline predictions."""
import csv
import hashlib
import json
import math
from collections import defaultdict
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
GROUPS = ('all', 'normal', 'extreme_any', 'hot', 'dry', 'wet', 'hot_dry', 'hot_wet', 'unclassified')


def fit_thresholds(rows, config):
    counties = defaultdict(list)
    for r in rows:
        if r['partition'] == 'train':
            if not 2000 <= int(r['year']) <= 2016:
                raise ValueError('Threshold reference outside training years')
            counties[r['county_fips']].append(r)
    result = {}
    for county, records in counties.items():
        if len({r['year'] for r in records}) != len(records):
            raise ValueError('Duplicate training year in threshold reference')
        if len(records) < config['minimum_training_years_per_county']:
            continue
        heat = [float(r[config['hot_feature']]) for r in records]
        rain = [float(r[config['precipitation_feature']]) for r in records]
        result[county] = {'training_years': len(records), 'hot_threshold_c': float(np.quantile(heat, config['hot_quantile'], method=config['quantile_method'])), 'dry_threshold_mm': float(np.quantile(rain, config['dry_quantile'], method=config['quantile_method'])), 'wet_threshold_mm': float(np.quantile(rain, config['wet_quantile'], method=config['quantile_method']))}
    return result


def classify(row, thresholds, config):
    threshold = thresholds.get(row['county_fips'])
    if threshold is None:
        return ['all', 'unclassified']
    rain = float(row[config['precipitation_feature']])
    hot = float(row[config['hot_feature']]) > threshold['hot_threshold_c']
    dry, wet = rain < threshold['dry_threshold_mm'], rain > threshold['wet_threshold_mm']
    groups = ['all']
    groups += ['hot'] if hot else []
    groups += ['dry'] if dry else []
    groups += ['wet'] if wet else []
    groups += ['hot_dry'] if hot and dry else []
    groups += ['hot_wet'] if hot and wet else []
    groups += ['extreme_any'] if hot or dry or wet else ['normal']
    return groups


def sha(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def write_csv(path, rows, fields=None):
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields or list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    config_path = ROOT / 'config/weather_groups.json'
    cfg = json.loads(config_path.read_text())
    splits = json.loads((ROOT / 'config/splits.json').read_text())
    if splits['partitions'] != {'train': [2000, 2016], 'validation': [2017, 2020], 'test': [2021, 2025]}:
        raise ValueError('Review threshold protocol after split change')
    out = ROOT / 'results/weather_groups'
    out.mkdir(exist_ok=True)
    provenance = {'definition': cfg, 'config_sha256': sha(config_path), 'input_sha256': {}, 'status': 'Exploratory follow-up specified after aggregate test results were visible. Thresholds fit only training weather; no baseline models retrained.'}
    # Complete all threshold fitting before evaluating any held-out errors.
    thresholds, threshold_rows = {}, []
    for cutoff in splits['forecast_cutoff_months']:
        path = ROOT / 'data/features' / cfg['reference_coverage_set'] / f'cutoff_{cutoff:02}.csv'
        provenance['input_sha256'][str(path.relative_to(ROOT))] = sha(path)
        with path.open(newline='') as f:
            thresholds[cutoff] = fit_thresholds(csv.DictReader(f), cfg)
        threshold_rows += [{'cutoff_month': cutoff, 'county_fips': c, **v} for c, v in sorted(thresholds[cutoff].items())]
    write_csv(out / 'training_weather_thresholds.csv', threshold_rows)
    keys = {}
    with (ROOT / 'data/features/primary_100/cutoff_05.csv').open(newline='') as f:
        primary_keys = {(r['county_fips'], int(r['year'])) for r in csv.DictReader(f) if r['partition'] in ('validation', 'test')}
    if len(primary_keys) != 3537:
        raise ValueError('Primary reference count changed')
    metrics, annual_metrics, coverage_rows, labels_output = [], [], [], []
    primary_labels = {}
    for name in splits['coverage_sets']:
        labels = {}
        population_keys = defaultdict(set)
        for cutoff in splits['forecast_cutoff_months']:
            path = ROOT / 'data/features' / name / f'cutoff_{cutoff:02}.csv'
            provenance['input_sha256'][str(path.relative_to(ROOT))] = sha(path)
            with path.open(newline='') as f:
                for r in csv.DictReader(f):
                    if r['partition'] not in ('validation', 'test'):
                        continue
                    key = (r['county_fips'], int(r['year']), cutoff)
                    if key in labels:
                        raise ValueError('Duplicate feature key')
                    labels[key] = classify(r, thresholds[cutoff], cfg)
                    if name == 'primary_100':
                        primary_labels[key] = labels[key]
                    elif key in primary_labels and labels[key] != primary_labels[key]:
                        raise ValueError('Shared weather labels changed across populations')
                    populations = ['own_test_population'] if r['partition'] == 'test' else ['own_validation_population']
                    if (key[0], key[1]) in primary_keys:
                        populations.append('shared_393')
                    labels_output.append({'coverage_set': name, 'county_fips': key[0], 'year': key[1], 'cutoff_month': cutoff, 'partition': r['partition'], 'groups': '|'.join(labels[key]), 'threshold_training_years': thresholds[cutoff].get(key[0], {}).get('training_years', 0)})
                    for population in populations:
                        for group in labels[key]:
                            population_keys[(population, r['partition'], cutoff, group)].add((key[0], key[1]))
        for (population, partition, cutoff, group), kk in sorted(population_keys.items()):
            coverage_rows.append({'coverage_set': name, 'population': population, 'partition': partition, 'cutoff_month': cutoff, 'group': group, 'county_years': len(kk), 'counties': len({k[0] for k in kk}), 'years': len({k[1] for k in kk})})
        errors, annual = defaultdict(list), defaultdict(list)
        seen = set()
        path = ROOT / 'results' / (name + '_baselines') / 'predictions.csv'
        provenance['input_sha256'][str(path.relative_to(ROOT))] = sha(path)
        with path.open(newline='') as f:
            for r in csv.DictReader(f):
                if r['partition'] not in ('validation', 'test'):
                    continue
                county, year, cutoff = r['county_fips'], int(r['year']), int(r['cutoff_month'])
                key = (county, year, cutoff)
                full_key = (*key, r['variant'], r['model'])
                if full_key in seen or key not in labels:
                    raise ValueError('Duplicate or unmatched prediction')
                seen.add(full_key)
                error = float(r['observed_yield']) - float(r['predicted_yield'])
                if not math.isfinite(error):
                    raise ValueError('Nonfinite error')
                populations = ['own_test_population'] if r['partition'] == 'test' else ['own_validation_population']
                if (county, year) in primary_keys:
                    populations.append('shared_393')
                for population in populations:
                    for group in labels[key]:
                        k = (population, r['partition'], cutoff, r['variant'], r['model'], group)
                        errors[k].append((county, year, error))
                        annual[(*k, year)].append((county, year, error))
        if len(seen) != len(labels) * 5:
            raise ValueError('Missing held-out predictions')
        for key, values in sorted(errors.items()):
            population, partition, cutoff, variant, model, group = key
            e = [v[2] for v in values]
            n, years = len(e), len({v[1] for v in values})
            metrics.append({'coverage_set': name, 'population': population, 'partition': partition, 'cutoff_month': cutoff, 'variant': variant, 'model': model, 'group': group, 'n': n, 'counties': len({v[0] for v in values}), 'years': years, 'mae': math.fsum(abs(v) for v in e) / n, 'rmse': math.sqrt(math.fsum(v * v for v in e) / n), 'bias_predicted_minus_observed': -math.fsum(e) / n, 'small_sample': n < cfg['small_sample_count'] or years < cfg['small_sample_years']})
        for key, values in sorted(annual.items()):
            population, partition, cutoff, variant, model, group, year = key
            e = [v[2] for v in values]
            annual_metrics.append({'coverage_set': name, 'population': population, 'partition': partition, 'cutoff_month': cutoff, 'variant': variant, 'model': model, 'group': group, 'year': year, 'n': len(e), 'mae': math.fsum(abs(v) for v in e) / len(e), 'rmse': math.sqrt(math.fsum(v * v for v in e) / len(e))})
    all_groups = defaultdict(dict)
    for r in metrics:
        key = tuple(r[k] for k in ('coverage_set', 'population', 'partition', 'cutoff_month', 'variant', 'model'))
        all_groups[key][r['group']] = r
    for key, groups in all_groups.items():
        if groups['all']['n'] != sum(groups.get(g, {}).get('n', 0) for g in ('normal', 'extreme_any', 'unclassified')):
            raise ValueError('Weather groups do not partition the evaluated rows')
        name, population, partition, cutoff, variant, model = key
        if population != 'shared_393':
            with (ROOT / 'results' / (name + '_baselines') / 'metrics.csv').open(newline='') as f:
                original = next(r for r in csv.DictReader(f) if r['partition'] == partition and int(r['cutoff_month']) == cutoff and r['variant'] == variant and r['model'] == model)
            if not math.isclose(groups['all']['mae'], float(original['mae']), abs_tol=1e-9) or groups['all']['n'] != int(original['n']):
                raise ValueError('Overall subgroup evaluation differs from original baseline metrics')
    normal = {(r['coverage_set'], r['population'], r['partition'], r['cutoff_month'], r['variant'], r['model']): r['mae'] for r in metrics if r['group'] == 'normal'}
    for r in metrics:
        reference = normal.get(tuple(r[k] for k in ('coverage_set', 'population', 'partition', 'cutoff_month', 'variant', 'model')))
        r['mae_minus_normal'] = r['mae'] - reference if reference is not None else ''
    write_csv(out / 'subgroup_metrics.csv', metrics)
    write_csv(out / 'subgroup_metrics_by_year.csv', annual_metrics)
    write_csv(out / 'group_coverage.csv', coverage_rows)
    write_csv(out / 'heldout_weather_labels.csv', labels_output)
    (out / 'provenance.json').write_text(json.dumps(provenance, indent=2) + '\n')
    lines = ['# Exploratory weather-group analysis', '', 'Thresholds use only county-specific weather observed in training years 2000-2016 from the largest coverage set. Same thresholds apply to every coverage stage. At least 10 training years are required. Hot: April-to-cutoff mean daily maximum temperature above the county training 90th percentile. Dry/wet: April-to-cutoff precipitation below the 10th / above the 90th percentile. Comparisons are strict; quantiles use linear interpolation.', '', 'These are statistical weather groups, not official drought, flood or heat-wave declarations. Groups reflect weather through each forecast cutoff, so memberships change across cutoffs. Hot can overlap dry or wet. Normal has none of these flags; unclassified lacks sufficient training history and is not treated as normal. All = normal + extreme_any + unclassified. Original predictions and models are unchanged.', '', 'Subgroup definitions were chosen after overall test results were visible; this is exploratory follow-up, not a predeclared untouched test. The 17-year reference is short and quantile estimates are uncertain. Counties and years are correlated; five test years do not supply thousands of independent weather events. No significance or causal claims are made. Sample warnings flag fewer than 30 county-years or fewer than three represented years.', '']
    for population, heading in [('shared_393', 'Common 393-county test rows'), ('own_test_population', 'Each set on its own test rows')]:
        lines += ['## ' + heading, '', 'Linear and Ridge with year trend, July cutoff (all other variants/cutoffs are in the CSVs). MAE units: bushels per acre.', '', '| Training set | Group | n | Years | Linear MAE | Ridge MAE |', '|---|---|---:|---:|---:|---:|']
        for name in splits['coverage_sets']:
            for group in ('normal', 'extreme_any', 'hot', 'dry', 'wet', 'hot_dry', 'unclassified'):
                found = [r for r in metrics if r['coverage_set'] == name and r['population'] == population and r['partition'] == 'test' and r['cutoff_month'] == 7 and r['variant'] == 'weather_plus_trend' and r['group'] == group and r['model'] in ('linear', 'ridge')]
                if found:
                    a, b = next(r for r in found if r['model'] == 'linear'), next(r for r in found if r['model'] == 'ridge')
                    lines.append(f"| {name} | {group} | {a['n']} | {a['years']} | {a['mae']:.2f} | {b['mae']:.2f} |")
        lines.append('')
    lines += ['Absent groups have zero observations and no defined score; they are omitted rather than reported as zero error. CSVs include validation and test, weather-only and trend variants, the mean baseline, all four cutoffs, bias, RMSE, differences from normal, sample sizes and yearly metrics. Unknown groups remain in overall performance but are excluded from normal/extreme comparisons.', '', 'Own-population scores change evaluated counties. Shared-row results keep the primary population fixed. Lower subgroup MAE than normal is possible and does not mean weather improves yield or that the group has been mislabeled. Different groups differ in county/year composition and yield distribution. Small/rare groups require cautious interpretation.']
    (out / 'README.md').write_text('\n'.join(lines) + '\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
