"""Build observed-label study sets; retain all source files unchanged."""
import csv
import gzip
import hashlib
import json
import math
from collections import Counter, defaultdict
from contextlib import ExitStack
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'processed'
OUT = ROOT / 'data' / 'study_sets'
YEARS = range(2000, 2026)
RULES = {'primary_100': 100, 'expanded_90': 90, 'expanded_80': 80, 'largest_available': 0}


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def save_csv(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


def main():
    sources = [DATA / n for n in ('usda_county_corn_yield_1951_2025.csv', 'usda_noaa_county_crosswalk.csv', 'usda_noaa_monthly_weather_1951_2025.csv.gz')]
    before = {p.name: digest(p) for p in sources}
    with sources[0].open(newline='', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        yield_fields = reader.fieldnames
        targets = {}
        for r in reader:
            key = (r['county_fips'], int(r['year']))
            if key[1] in YEARS:
                assert key not in targets
                assert math.isfinite(float(r['yield_bu_per_acre'])) and float(r['yield_bu_per_acre']) >= 0
                targets[key] = r
    complete = defaultdict(set)
    with gzip.open(sources[2], 'rt', newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        weather_fields = reader.fieldnames
        seen = set()
        for r in reader:
            key = (r['county_fips'], int(r['year']))
            if key not in targets:
                continue
            month = int(r['month'])
            assert (*key, month) not in seen
            seen.add((*key, month))
            if r['weather_match_status'] == 'matched' and all(int(r[v + '_days_missing']) == 0 and int(r[v + '_days_observed']) == int(r['expected_days']) for v in ('prcp', 'tavg', 'tmax', 'tmin')):
                complete[key].add(month)
    usable = {k for k in targets if complete[k] == set(range(1, 9))}
    by_county = defaultdict(set)
    for c, y in usable:
        by_county[c].add(y)
    selected = {name: {k for k in usable if len(by_county[k[0]]) * 100 >= pct * len(YEARS)} for name, pct in RULES.items()}
    expected = {'primary_100': (393, 10218), 'expanded_90': (883, 22254), 'expanded_80': (1287, 31207), 'largest_available': (2321, 42750)}
    manifest = {'period': [2000, 2025], 'primary_set': 'primary_100', 'source_sha256': before, 'common_rules': ['Observed finite nonnegative USDA yield; zero is valid.', 'Matched county and complete January-August weather in all four variables.', 'No missing targets or weather are imputed.', 'Preserve canonical and original county identifiers.', 'Thresholds measure county reporting continuity across the 26 years.', 'Same scope rules apply to every algorithm; chronological splits remain to be chosen.', 'No training or test scores were used to select these sets.'], 'sets': {}}
    for name, keys in selected.items():
        counts = (len({c for c, y in keys}), len(keys))
        assert counts == expected[name], (name, counts)
        folder = OUT / name
        save_csv(folder / 'observed_yields.csv', yield_fields, (targets[k] for k in sorted(keys)))
        membership = [{'county_fips': c, 'state': targets[next(k for k in keys if k[0] == c)]['state_alpha'], 'usable_years': len(by_county[c]), 'possible_years': 26} for c in sorted({c for c, y in keys})]
        save_csv(folder / 'counties.csv', list(membership[0]), membership)
        manifest['sets'][name] = {'minimum_coverage_pct': RULES[name], 'counties': counts[0], 'observed_county_years': counts[1], 'monthly_rows': counts[1] * 8, 'records_retained_pct': round(100 * counts[1] / len(usable), 2), 'observations_by_year': dict(sorted(Counter(y for c, y in keys).items()))}
    written = Counter()
    with ExitStack() as stack:
        writers = {}
        for name in RULES:
            f = stack.enter_context(gzip.open(OUT / name / 'monthly_weather.csv.gz', 'wt', newline='', encoding='utf-8'))
            writers[name] = csv.DictWriter(f, fieldnames=weather_fields)
            writers[name].writeheader()
        source = stack.enter_context(gzip.open(sources[2], 'rt', newline='', encoding='utf-8'))
        for r in csv.DictReader(source):
            key = (r['county_fips'], int(r['year']))
            for name, keys in selected.items():
                if key in keys:
                    writers[name].writerow(r)
                    written[name] += 1
    for name in RULES:
        assert written[name] == manifest['sets'][name]['monthly_rows']
    assert selected['primary_100'] <= selected['expanded_90'] <= selected['expanded_80'] <= selected['largest_available']
    with sources[1].open(newline='', encoding='utf-8-sig') as f:
        crosswalk = {}
        for r in csv.DictReader(f):
            if r['match_status'] == 'matched':
                crosswalk[r['county_fips']] = r
    missing = []
    for county in sorted(by_county):
        r = crosswalk.get(county)
        if not r:
            continue
        for year in YEARS:
            if (county, year) not in targets:
                missing.append({'county_fips': county, 'state': r['state_alpha'], 'county': r['county_name'], 'year': year, 'noaa_county_id': r['noaa_county_id'], 'status': 'no_retained_usda_target', 'label_origin': 'missing', 'predicted_yield_bu_per_acre': '', 'weather_status': 'raw_daily_data_available_not_exported_for_this_year'})
    save_csv(OUT / 'missing_year_prediction_candidates.csv', ['county_fips', 'state', 'county', 'year', 'noaa_county_id', 'status', 'label_origin', 'predicted_yield_bu_per_acre', 'weather_status'], missing)
    manifest['missing_year_candidates'] = len(missing)
    assert len(missing) + len(targets) == len(by_county) * len(YEARS)
    assert before == {p.name: digest(p) for p in sources}, 'Source files changed'
    manifest['source_files_unchanged'] = True
    (OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(manifest, indent=2))


if __name__ == '__main__':
    main()
