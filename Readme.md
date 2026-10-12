# Early-Season County-Level Corn Yield Forecasting

CS 422 machine learning group project, Fall 2026

## Project overview

This project investigates how accurately machine learning can forecast annual
county-level corn yields (bushels per acre) before the growing season ends. We
will focus on forecasts made at multiple points during the season and ask how
prediction accuracy changes as more weather information becomes available,
particularly in unusually hot, dry, or wet seasons.

The intended users include farmers and agricultural producers, crop insurers,
agricultural researchers, and government agencies. Forecasts and uncertainty
estimates could inform planning and risk assessment; this project evaluates
predictive reliability and does not claim that weather alone causes yield
changes.

## Questions and objectives

- How does forecast error change across growing-season cutoffs, such as the end
  of May, June, July, and August?
- How well do models perform in normal seasons compared with unusually hot,
  dry, or wet seasons?
- How reliably can we estimate forecast uncertainty, including calibrated
  prediction intervals if feasible?

We will compare models using a shared target, preprocessing rules, chronological
evaluation design, and metrics. Primary metrics are mean absolute error (MAE)
and root mean squared error (RMSE).

See [PROJECT_SPEC.md](./PROJECT_SPEC.md) for the agreed project requirements
and open decisions, and [ROADMAP.md](./ROADMAP.md) for the phased implementation
plan.

## Data sources

- **USDA National Agricultural Statistics Service (NASS) Quick Stats**:
  historical county-level corn yields and related agricultural statistics.
  [Quick Stats](https://data.nass.usda.gov/Quick_Stats/)
- **NOAA nClimGrid-Daily**: daily temperature and precipitation data used to
  derive county-level weather features.
  [Dataset information](https://www.ncei.noaa.gov/products/land-based-station/nclimgrid-daily)

Records will be aligned by county, year, and forecast cutoff date. Candidate
features include cumulative rainfall, temperature summaries, heat exposure,
weather anomalies, and past yields. The available sources overlap from 1951
through 2025; the final modeling period and geographic scope will be selected
after auditing usable county-year coverage.

## Initial data feasibility check

The sources have overlapping coverage from **1951 through 2025**. An initial
local extract is available for that full period; this establishes feasibility
but does not decide the final modeling scope.

- **USDA yield panel**: `data/processed/usda_county_corn_yield_1951_2025.csv`
  contains 151,310 county-year records across 2,821 canonical county identities
  in 41 states (2,822 distinct historical USDA county codes).
  It was filtered from the USDA Quick Stats crop bulk file dated October 10,
  2026, to survey estimates for county-level corn-grain yield in bushels per
  acre. USDA "other/combined counties" aggregates were excluded because they
  do not identify an individual county. The full 1.13 GB compressed source
  archive was removed after extraction.
- **NOAA weather source files**: `data/raw/noaa/averages/` contains 2,400
  gzip-compressed county area-average CSVs for January through August, 1951
  through 2025, for precipitation, average temperature, maximum temperature,
  and minimum temperature. The files total about 541 MB compressed. They
  retain daily values so features can be derived using only weather available
  at each forecast cutoff.
- **County crosswalk**: `data/processed/usda_noaa_county_crosswalk.csv` maps
  historical USDA county identifiers to canonical county FIPS and NOAA's
  county-area identifiers. NOAA IDs are not necessarily county FIPS, so
  records were matched by state and normalized county name. Historical USDA
  code `29193` for Ste. Genevieve County is normalized to current FIPS `29186`;
  the source code is retained for traceability. The crosswalk matched 151,288
  of 151,310 USDA county-year records (99.99%); the remaining 22 records all
  refer to South Dakota's `WASHABAUGH` entry, which has no corresponding NOAA
  county name.

## Validation and normalization

Run `python scripts/prepare_data.py` from the project root to validate the
yield panel, county crosswalk, and all downloaded NOAA files, then regenerate
the normalized files below. The script uses the Python standard library only
and fails explicitly on malformed input, duplicate county-year targets,
inconsistent NOAA monthly files, or invalid weather values.

- The yield panel is checked for valid years, county identifiers, numeric
  nonnegative yields, and duplicate canonical county-year rows. NUL bytes in
  NASS's optional CV field are converted to missing values. Zero yields are
  retained as observations.
- NOAA's daily area-average values are normalized to monthly summaries:
  precipitation totals in millimeters and mean/minimum/maximum temperatures in
  degrees Celsius. The source uses `-999.99` for non-calendar padding and may
  use missing sentinels within calendar days; sentinels become missing values,
  never numeric extremes. Zero precipitation remains valid. Monthly summary
  columns are accompanied by observed- and missing-day counts; no values are
  imputed at this stage.
- `data/processed/usda_noaa_monthly_weather_1951_2025.csv.gz` contains one row
  for each USDA county-year and month (January through August), with NOAA
  weather summaries where a county match exists. Historical source county
  codes are preserved alongside canonical county FIPS.
- `data/processed/data_quality_report.json` records the validation counts,
  value ranges, missingness, and matched/unmatched county-month counts.

The NOAA source describes its area averages as weighted aggregates and notes
that preliminary daily values are revised as additional observations arrive;
see the [nClimGrid-Daily documentation](https://www.ncei.noaa.gov/products/land-based-station/nclimgrid-daily).

Sources: [USDA Quick Stats bulk downloads](https://www.nass.usda.gov/datasets/)
and [NOAA nClimGrid-Daily documentation](https://www.ncei.noaa.gov/metadata/geoportal/rest/metadata/item/gov.noaa.ncdc:C01589/html).
The final modeling period and geographic scope will be selected after auditing
year-by-year coverage and defining the evaluation sample.

## Evaluation approach

To simulate genuine early-season forecasting, each forecast cutoff will use
only information available by that date. We will use chronological
train/validation/test splits by year rather than randomly mixing years, and
compare the models on consistent held-out years. Preprocessing and feature
selection must be fit using training data only to avoid leakage.

We will report errors by forecast cutoff and examine results across weather
conditions. Extreme-weather cases may be uncommon, so subgroup results should
be interpreted with their sample sizes and uncertainty in mind.

## Preliminary model assignments

These assignments are preliminary and subject to team confirmation:

- **Russell Kennedy**: Linear and Ridge Regression baselines
- **Tylie Anderson**: Random Forest Regression
- **Alexander Aquiningoc**: Gradient Boosting Regression
- **Lester Iwuajoku**: Neural Network Regression

The team will jointly develop the dataset, preprocessing rules, chronological
splits, and evaluation protocol.

## Anticipated challenges and limitations

- Combining county-level sources across years may require reconciling missing
  records, geographic identifiers, and differing coverage.
- Yield also depends on factors not captured by weather data, including soil,
  management, irrigation, pests, and seed varieties.
- Extreme weather can be rare, limiting the strength of comparisons on those
  seasons.
- County-level averages can hide local variation.

We will document these limitations and avoid interpreting predictive
relationships as causal effects.