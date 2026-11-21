"""Audit local yield/weather coverage without modifying source datasets."""
import calendar
import csv
import gzip
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data' / 'processed'
OUT = ROOT / 'reports' / 'coverage'


def write_csv(name, rows):
    rows = list(rows)
    with (OUT / name).open('w', newline='', encoding='utf-8') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    with (DATA / 'usda_county_corn_yield_1951_2025.csv').open(newline='', encoding='utf-8-sig') as f:
        targets = {(r['county_fips'], int(r['year'])): r for r in csv.DictReader(f)}
    assert len(targets) == 151310, 'Unexpected yield count; review scope assumptions'
    seen = set()
    complete_months = defaultdict(set)
    matched_months = Counter()
    missing_days = Counter()
    with gzip.open(DATA / 'usda_noaa_monthly_weather_1951_2025.csv.gz', 'rt', newline='', encoding='utf-8') as f:
        for r in csv.DictReader(f):
            key = (r['county_fips'], int(r['year']))
            month = int(r['month'])
            assert key in targets and 1 <= month <= 8
            record_key = (*key, month)
            assert record_key not in seen, f'Duplicate weather row {record_key}'
            seen.add(record_key)
            if r['weather_match_status'] == 'matched':
                matched_months[key] += 1
            expected = calendar.monthrange(key[1], month)[1]
            complete = r['weather_match_status'] == 'matched'
            for var in ('prcp', 'tavg', 'tmax', 'tmin'):
                observed, missing = int(r[var + '_days_observed']), int(r[var + '_days_missing'])
                assert observed + missing == expected
                missing_days[var] += missing
                complete = complete and missing == 0 and observed == expected
            if complete:
                complete_months[key].add(month)
    assert len(seen) == len(targets) * 8, 'Missing monthly records'
    usable = {k for k in targets if complete_months[k] == set(range(1, 9))}
    county_years = defaultdict(set)
    counties = {}
    for key, r in targets.items():
        counties[key[0]] = r
        if key in usable:
            county_years[key[0]].add(key[1])
    years = []
    for year in range(1951, 2026):
        keys = [k for k in targets if k[1] == year]
        row = {'year': year, 'yield_records': len(keys), 'complete_jan_aug': sum(k in usable for k in keys)}
        for cutoff in (5, 6, 7, 8):
            row[f'complete_through_{cutoff:02}'] = sum(set(range(1, cutoff + 1)).issubset(complete_months[k]) for k in keys)
        years.append(row)
    write_csv('by_year.csv', years)
    state_rows = []
    for state in sorted({r['state_alpha'] for r in targets.values()}):
        keys = [k for k, r in targets.items() if r['state_alpha'] == state]
        state_rows.append({'state': state, 'counties_with_yield': len({k[0] for k in keys}), 'yield_records': len(keys), 'complete_jan_aug': sum(k in usable for k in keys), 'first_year': min(k[1] for k in keys), 'last_year': max(k[1] for k in keys)})
    write_csv('by_state.csv', state_rows)
    write_csv('by_county.csv', ({'county_fips': c, 'state': counties[c]['state_alpha'], 'county': counties[c]['county_name'], 'yield_years': sum(k[0] == c for k in targets), 'complete_weather_years': len(county_years[c]), 'first_complete_year': min(county_years[c], default=''), 'last_complete_year': max(county_years[c], default=''), 'complete_years_2000_2025': sum(y >= 2000 for y in county_years[c])} for c in sorted(counties)))
    write_csv('excluded_county_years.csv', ({'county_fips': k[0], 'state': targets[k]['state_alpha'], 'county': targets[k]['county_name'], 'year': k[1], 'matched_months': matched_months[k], 'complete_months': len(complete_months[k])} for k in sorted(set(targets) - usable)))
    regions = {'all_states': None, 'IA_IL_IN': {'IA', 'IL', 'IN'}, 'ten_state_corn_region': {'IA', 'IL', 'IN', 'NE', 'MN', 'OH', 'SD', 'WI', 'MO', 'KS'}}
    candidates = []
    for region, states in regions.items():
        for start in (1951, 1981, 2000, 2010):
            total_years = 2026 - start
            available = {c: {y for y in ys if y >= start} for c, ys in county_years.items() if states is None or counties[c]['state_alpha'] in states}
            for pct in (80, 90, 100):
                eligible = {c: ys for c, ys in available.items() if len(ys) * 100 >= pct * total_years}
                counts = [sum(y in ys for ys in eligible.values()) for y in range(start, 2026)]
                candidates.append({'region': region, 'start_year': start, 'end_year': 2025, 'minimum_coverage_pct': pct, 'counties': len(eligible), 'county_years': sum(map(len, eligible.values())), 'min_counties_in_any_year': min(counts), 'max_counties_in_any_year': max(counts)})
    write_csv('candidate_scopes.csv', candidates)
    summary = {'yield_county_years': len(targets), 'counties': len(counties), 'states': len(state_rows), 'complete_jan_aug_county_years': len(usable), 'excluded_county_years': len(targets) - len(usable), 'monthly_rows_checked': len(seen), 'missing_days_including_unmatched': dict(missing_days)}
    (OUT / 'summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    lines = ['# Local data coverage audit', '', 'Coverage describes records available for analysis, not prediction accuracy.', '', '## Overall', '', *[f'- {k}: {v}' for k, v in summary.items()], '', '## Candidate scopes', '', 'A usable county-year has a yield target and complete January-August weather for all four variables. Thresholds measure the fraction of years with usable records; missing years are never filled with zero.', '', '| Region | Years | Minimum coverage | Counties | County-years | Annual county range |', '|---|---|---:|---:|---:|---|']
    for r in candidates:
        lines.append(f"| {r['region']} | {r['start_year']}-2025 | {r['minimum_coverage_pct']}% | {r['counties']} | {r['county_years']} | {r['min_counties_in_any_year']}-{r['max_counties_in_any_year']} |")
    lines += ['', '## Interpretation', '', 'Compare recent and longer windows before choosing scope. A balanced panel (100% coverage) simplifies county comparisons but can select counties with more consistent reporting. Less restrictive panels retain more observations but change county composition over time. These counts describe reporting continuity, not a complete geographic inventory of all counties.', '', 'Do not choose scope based on held-out prediction scores. Record scope and chronological splits before model comparison. Final-year publication timing and historical weather revisions still require documentation.', '', 'Files: by_year.csv, by_state.csv, by_county.csv, excluded_county_years.csv, candidate_scopes.csv, summary.json. No train/test split or modeling scope has been imposed.']
    (OUT / 'README.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(json.dumps(summary, indent=2))
    print('SELECTED CANDIDATES')
    for r in candidates:
        if r['start_year'] == 2000:
            print(json.dumps(r))


if __name__ == '__main__':
    main()
