"""Generate shared county-year assignments without copying or imputing targets."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate_config(config):
    if config['split_unit'] != 'harvest_year':
        raise ValueError('Split unit must be harvest_year')
    partitions = config['partitions']
    if list(partitions) != ['train', 'validation', 'test']:
        raise ValueError('Expected ordered train, validation, test partitions')
    previous = None
    for start, end in partitions.values():
        if start > end or (previous is not None and start != previous + 1):
            raise ValueError('Year ranges must be contiguous and disjoint')
        previous = end


def partition_for_year(year, config):
    matches = [name for name, (start, end) in config['partitions'].items() if start <= year <= end]
    if len(matches) != 1:
        raise ValueError(f'Year has no unique partition: {year}')
    return matches[0]


def main():
    config_path = ROOT / 'config/splits.json'
    config = json.loads(config_path.read_text())
    validate_config(config)
    folder = ROOT / 'data/study_sets'
    summary = {'config': 'config/splits.json', 'config_sha256': hashlib.sha256(config_path.read_bytes()).hexdigest(), 'partitions': config['partitions'], 'sets': {}}
    memberships = {}
    for name in config['coverage_sets']:
        source = folder / name / 'observed_yields.csv'
        rows = []
        seen = set()
        with source.open(newline='', encoding='utf-8-sig') as f:
            for r in csv.DictReader(f):
                key = (r['county_fips'], int(r['year']))
                if key in seen:
                    raise ValueError(f'Duplicate county-year in {name}: {key}')
                seen.add(key)
                rows.append({'county_fips': key[0], 'year': key[1], 'partition': partition_for_year(key[1], config)})
        memberships[name] = seen
        with (folder / name / 'split_assignments.csv').open('w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['county_fips', 'year', 'partition'])
            writer.writeheader()
            writer.writerows(sorted(rows, key=lambda r: (r['county_fips'], r['year'])))
        summary['sets'][name] = {p: {'county_years': sum(r['partition'] == p for r in rows), 'counties': len({r['county_fips'] for r in rows if r['partition'] == p})} for p in config['partitions']}
        if name == 'primary_100':
            expected = {'train': 6681, 'validation': 1572, 'test': 1965}
            if any(summary['sets'][name][p]['county_years'] != n for p, n in expected.items()):
                raise ValueError('Primary cohort split counts changed')
    ordered = [memberships[n] for n in config['coverage_sets']]
    if not all(a <= b for a, b in zip(ordered, ordered[1:])):
        raise ValueError('Coverage sets are not nested')
    (folder / 'split_summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps(summary, indent=2))


if __name__ == '__main__':
    main()
