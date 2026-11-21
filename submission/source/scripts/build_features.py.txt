"""Create cutoff-safe weather features from complete monthly county records."""
import calendar
import csv
import gzip
import hashlib
import json
import math
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MONTHLY = ('precipitation_total_mm', 'tavg_mean_c', 'tmax_mean_c', 'tmin_mean_c', 'tmax_max_c', 'tmin_min_c')
META = ['county_fips', 'year', 'cutoff_month', 'partition', 'yield_bu_per_acre']


def feature_names(cutoff, config):
    names = ['preseason_precipitation_total_mm', 'preseason_tavg_mean_c', 'preseason_tmin_min_c']
    for month in range(config['growing_window_start_month'], cutoff + 1):
        names.extend(f'm{month:02}_{name}' for name in MONTHLY)
    names.extend('season_' + name for name in MONTHLY)
    return names


def compute_features(months, year, cutoff, config):
    """Read only January through cutoff, including calendar-day weighting."""
    if cutoff not in config['cutoffs']:
        raise ValueError('Unsupported cutoff')
    for month in range(1, cutoff + 1):
        if month not in months:
            raise ValueError(f'Missing month {year}-{month:02}')
        days, values = months[month]
        if days != calendar.monthrange(year, month)[1] or len(values) != 6:
            raise ValueError('Invalid calendar or monthly schema')
        if not all(math.isfinite(v) for v in values) or values[0] < 0:
            raise ValueError('Invalid weather value')

    def weighted_mean(window, index):
        return sum(months[m][0] * months[m][1][index] for m in window) / sum(months[m][0] for m in window)

    pre = config['preseason_months']
    result = {
        'preseason_precipitation_total_mm': sum(months[m][1][0] for m in pre),
        'preseason_tavg_mean_c': weighted_mean(pre, 1),
        'preseason_tmin_min_c': min(months[m][1][5] for m in pre),
    }
    window = range(config['growing_window_start_month'], cutoff + 1)
    for month in window:
        result.update({f'm{month:02}_{name}': value for name, value in zip(MONTHLY, months[month][1])})
    result['season_precipitation_total_mm'] = sum(months[m][1][0] for m in window)
    for index, name in ((1, 'tavg_mean_c'), (2, 'tmax_mean_c'), (3, 'tmin_mean_c')):
        result['season_' + name] = weighted_mean(window, index)
    result['season_tmax_max_c'] = max(months[m][1][4] for m in window)
    result['season_tmin_min_c'] = min(months[m][1][5] for m in window)
    result['year_since_2000'] = year - config['trend_reference_year']
    return {name: round(value, 6) for name, value in result.items()}


def main():
    config_path = ROOT / 'config/features.json'
    config = json.loads(config_path.read_text())
    split_config = json.loads((ROOT / 'config/splits.json').read_text())
    if config['cutoffs'] != split_config['forecast_cutoff_months'] or tuple(config['monthly_features']) != MONTHLY:
        raise ValueError('Feature configuration disagrees with supported schema or split cutoffs')
    if config['preseason_months'] != [1, 2, 3] or config['growing_window_start_month'] != 4 or config['trend_reference_year'] != 2000:
        raise ValueError('Unsupported feature window or trend reference')
    out = ROOT / 'data/features'
    out.mkdir(parents=True, exist_ok=True)
    manifest = {'feature_config_sha256': hashlib.sha256(config_path.read_bytes()).hexdigest(), 'split_config_sha256': hashlib.sha256((ROOT / 'config/splits.json').read_bytes()).hexdigest(), 'metadata_not_predictors': META, 'features_by_cutoff': {}, 'sets': {}}
    for cutoff in config['cutoffs']:
        weather = feature_names(cutoff, config)
        manifest['features_by_cutoff'][str(cutoff)] = {'weather_only': weather, 'weather_plus_trend': weather + ['year_since_2000']}
    shared = {}
    for name in split_config['coverage_sets']:
        source = ROOT / 'data/study_sets' / name
        targets, assignments = {}, {}
        for filename, dest in [('observed_yields.csv', targets), ('split_assignments.csv', assignments)]:
            with (source / filename).open(newline='', encoding='utf-8-sig') as f:
                for row in csv.DictReader(f):
                    key = (row['county_fips'], int(row['year']))
                    if key in dest:
                        raise ValueError('Duplicate target or assignment')
                    dest[key] = row
        if targets.keys() != assignments.keys():
            raise ValueError('Target and assignment keys differ')
        months = defaultdict(dict)
        with gzip.open(source / 'monthly_weather.csv.gz', 'rt', newline='', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                key, month = (row['county_fips'], int(row['year'])), int(row['month'])
                if key not in targets or month not in range(1, 9) or month in months[key]:
                    raise ValueError('Unexpected or duplicate weather row')
                if row['weather_match_status'] != 'matched' or any(int(row[v + '_days_missing']) != 0 or int(row[v + '_days_observed']) != int(row['expected_days']) for v in ('prcp', 'tavg', 'tmax', 'tmin')):
                    raise ValueError('Incomplete weather')
                months[key][month] = (int(row['expected_days']), tuple(float(row[field]) for field in MONTHLY))
        folder = out / name
        folder.mkdir(exist_ok=True)
        counts = {}
        for cutoff in config['cutoffs']:
            fields = META + feature_names(cutoff, config) + ['year_since_2000']
            partition_counts = Counter()
            with (folder / f'cutoff_{cutoff:02}.csv').open('w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                for key in sorted(targets):
                    county, year = key
                    partition = assignments[key]['partition']
                    valid = [p for p, (lo, hi) in split_config['partitions'].items() if lo <= year <= hi]
                    if valid != [partition]:
                        raise ValueError('Assignment violates shared split')
                    features = compute_features(months[key], year, cutoff, config)
                    values = tuple(features.items())
                    check_key = (key, cutoff)
                    if name == 'primary_100':
                        shared[check_key] = values
                    elif check_key in shared and values != shared[check_key]:
                        raise ValueError('Shared primary cohort has inconsistent features')
                    writer.writerow({'county_fips': county, 'year': year, 'cutoff_month': cutoff, 'partition': partition, 'yield_bu_per_acre': targets[key]['yield_bu_per_acre'], **features})
                    partition_counts[partition] += 1
            counts[str(cutoff)] = dict(partition_counts)
        manifest['sets'][name] = {'county_years_per_cutoff': len(targets), 'partition_counts_by_cutoff': counts}
    (out / 'feature_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'rows_per_cutoff': {k: v['county_years_per_cutoff'] for k, v in manifest['sets'].items()}, 'weather_feature_counts': {k: len(v['weather_only']) for k, v in manifest['features_by_cutoff'].items()}}, indent=2))


if __name__ == '__main__':
    main()
