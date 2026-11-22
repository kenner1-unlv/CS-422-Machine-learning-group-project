"""Validate and normalize the USDA yield and NOAA county-weather inputs."""

from __future__ import annotations

import calendar
import csv
import gzip
import json
import math
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from statistics import fmean
from typing import TextIO


PROJECT_ROOT = Path(__file__).resolve().parents[1]
FIRST_YEAR = 1951
LAST_YEAR = 2025
MONTHS = range(1, 9)
VARIABLES = ("prcp", "tavg", "tmax", "tmin")
NOAA_MISSING_VALUES = {"", "-999.99", "-9999", "NA", "NAN"}
# USDA's older Ste. Genevieve records use the county code retired in 1987.
COUNTY_FIPS_ALIASES = {"29193": "29186"}
NOAA_FILENAME = re.compile(
    r"(prcp|tavg|tmax|tmin)-(\d{4})(\d{2})-cty-scaled\.csv\.gz"
)

YIELD_PATH = PROJECT_ROOT / "data/processed/usda_county_corn_yield_1951_2025.csv"
CROSSWALK_PATH = PROJECT_ROOT / "data/processed/usda_noaa_county_crosswalk.csv"
WEATHER_ROOT = PROJECT_ROOT / "data/raw/noaa/averages"
PANEL_PATH = PROJECT_ROOT / "data/processed/usda_noaa_monthly_weather_1951_2025.csv.gz"
REPORT_PATH = PROJECT_ROOT / "data/processed/data_quality_report.json"

YIELD_FIELDS = [
    "county_fips",
    "source_county_fips",
    "state_fips",
    "state_alpha",
    "state_name",
    "county_ansi",
    "county_name",
    "year",
    "yield_bu_per_acre",
    "cv_pct",
]

CROSSWALK_FIELDS = [
    "county_fips",
    "source_county_fips",
    "state_fips",
    "state_alpha",
    "state_name",
    "county_ansi",
    "county_name",
    "noaa_county_id",
    "noaa_county_name",
    "match_status",
]

WEATHER_FIELDS = [
    "county_fips",
    "source_county_fips",
    "noaa_county_id",
    "state_alpha",
    "county_name",
    "year",
    "month",
    "expected_days",
    "weather_match_status",
    "precipitation_total_mm",
    "prcp_days_observed",
    "prcp_days_missing",
    "tavg_mean_c",
    "tavg_days_observed",
    "tavg_days_missing",
    "tmax_mean_c",
    "tmax_max_c",
    "tmax_days_observed",
    "tmax_days_missing",
    "tmin_mean_c",
    "tmin_min_c",
    "tmin_days_observed",
    "tmin_days_missing",
]


def normalize_county_name(name: str) -> str:
    """Normalize USDA and NOAA county labels for a state-scoped name match."""
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    name = name.upper()
    name = re.sub(r"\([^)]*\)", " ", name)
    name = re.sub(
        r"\b(COUNTY|PARISH|BOROUGH|CENSUS AREA|MUNICIPALITY|CITY AND BOROUGH|CITY|MUNICIPIO)\b",
        " ",
        name,
    )
    name = re.sub(r"\bSAINT\b", "ST", name)
    return re.sub(r"[^A-Z0-9]", "", name)


def parse_weather_value(value: str) -> float | None:
    """Return a numeric NOAA value, mapping missing markers to None."""
    value = value.strip()
    if value.upper() in NOAA_MISSING_VALUES:
        return None
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"non-finite NOAA value: {value!r}")
    if number <= -900:
        raise ValueError(f"unrecognized NOAA missing sentinel: {value!r}")
    return number


def summarize_days(values: list[float | None], variable: str) -> dict[str, float | int | str]:
    observed = [value for value in values if value is not None]
    missing = len(values) - len(observed)
    summary: dict[str, float | int | str] = {
        f"{variable}_days_observed": len(observed),
        f"{variable}_days_missing": missing,
    }
    if not observed:
        if variable == "prcp":
            summary["precipitation_total_mm"] = ""
        elif variable == "tavg":
            summary["tavg_mean_c"] = ""
        elif variable == "tmax":
            summary["tmax_mean_c"] = ""
            summary["tmax_max_c"] = ""
        else:
            summary["tmin_mean_c"] = ""
            summary["tmin_min_c"] = ""
        return summary

    if variable == "prcp":
        if min(observed) < 0:
            raise ValueError("negative precipitation is not physically valid")
        summary["precipitation_total_mm"] = round(sum(observed), 4)
    elif variable == "tavg":
        summary["tavg_mean_c"] = round(fmean(observed), 4)
    elif variable == "tmax":
        summary["tmax_mean_c"] = round(fmean(observed), 4)
        summary["tmax_max_c"] = round(max(observed), 4)
    elif variable == "tmin":
        summary["tmin_mean_c"] = round(fmean(observed), 4)
        summary["tmin_min_c"] = round(min(observed), 4)
    else:
        raise ValueError(f"unsupported NOAA variable: {variable}")
    return summary


def read_yield_panel(path: Path) -> tuple[list[dict[str, str]], dict[str, int]]:
    required = set(YIELD_FIELDS) - {"source_county_fips"}
    cleaned_rows: list[dict[str, str]] = []
    counts: Counter[str] = Counter()
    keys: set[tuple[str, int]] = set()
    with path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError(f"yield file is missing required columns: {sorted(required)}")
        for line_number, original in enumerate(reader, start=2):
            row = {
                key: (value or "").replace("\x00", "").strip()
                for key, value in original.items()
                if key is not None
            }
            source_county_fips = row.get("source_county_fips") or row["county_fips"]
            county_ansi = row["county_ansi"].zfill(3)
            state_fips = row["state_fips"].zfill(2)
            county_fips = COUNTY_FIPS_ALIASES.get(
                source_county_fips, source_county_fips
            )
            try:
                year = int(row["year"])
                yield_value = float(row["yield_bu_per_acre"])
            except (ValueError, TypeError) as exc:
                raise ValueError(f"invalid yield or year on line {line_number}") from exc
            if (
                len(source_county_fips) != 5
                or not source_county_fips.isdigit()
                or source_county_fips != state_fips + county_ansi
                or len(county_fips) != 5
                or not county_fips.isdigit()
            ):
                raise ValueError(f"invalid county FIPS on line {line_number}: {county_fips!r}")
            if not FIRST_YEAR <= year <= LAST_YEAR:
                raise ValueError(f"year outside retained overlap on line {line_number}: {year}")
            if not math.isfinite(yield_value) or yield_value < 0:
                raise ValueError(f"invalid yield on line {line_number}: {yield_value}")
            key = (county_fips, year)
            if key in keys:
                raise ValueError(f"duplicate county-year yield on line {line_number}: {key}")
            keys.add(key)
            if row["cv_pct"]:
                try:
                    cv = float(row["cv_pct"])
                except ValueError as exc:
                    raise ValueError(f"invalid CV on line {line_number}") from exc
                if not math.isfinite(cv) or cv < 0:
                    raise ValueError(f"invalid CV on line {line_number}: {cv}")
                row["cv_pct"] = str(cv)
            else:
                row["cv_pct"] = ""
                counts["missing_cv_pct"] += 1
            row.update(
                county_fips=county_fips,
                source_county_fips=source_county_fips,
                state_fips=state_fips,
                county_ansi=county_ansi,
                year=str(year),
                yield_bu_per_acre=str(yield_value),
            )
            if yield_value == 0:
                counts["zero_yield_values_retained"] += 1
            counts[f"year_{year}"] += 1
            cleaned_rows.append(row)
    counts["records"] = len(cleaned_rows)
    counts["unique_counties"] = len({row["county_fips"] for row in cleaned_rows})
    counts["unique_source_counties"] = len(
        {row["source_county_fips"] for row in cleaned_rows}
    )
    return cleaned_rows, dict(counts)


def normalize_crosswalk_file(path: Path) -> None:
    rows: list[dict[str, str]] = []
    with path.open(encoding="utf-8-sig", newline="") as source:
        for row in csv.DictReader(source):
            source_fips = row.get("source_county_fips", row.get("county_fips", "")).strip()
            row["source_county_fips"] = source_fips
            row["county_fips"] = (
                row.get("canonical_county_fips", "").strip()
                or COUNTY_FIPS_ALIASES.get(source_fips, source_fips)
            )
            rows.append(row)
    temporary_path = path.with_suffix(path.suffix + ".tmp")
    with temporary_path.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=CROSSWALK_FIELDS)
        writer.writeheader()
        writer.writerows({field: row.get(field, "") for field in CROSSWALK_FIELDS} for row in rows)
    os.replace(temporary_path, path)


def read_crosswalk(
    path: Path,
) -> tuple[dict[str, dict[str, str]], dict[str, list[dict[str, str]]]]:
    by_fips: dict[str, dict[str, str]] = {}
    by_noaa_id: dict[str, list[dict[str, str]]] = defaultdict(list)
    with path.open(encoding="utf-8-sig", newline="") as source:
        for line_number, row in enumerate(csv.DictReader(source), start=2):
            fips = row.get("source_county_fips", row.get("county_fips", "")).strip()
            status = row["match_status"].strip()
            if fips in by_fips:
                raise ValueError(f"duplicate county in crosswalk on line {line_number}: {fips}")
            row["source_county_fips"] = fips
            row["county_fips"] = (
                row.get("county_fips", "").strip()
                or COUNTY_FIPS_ALIASES.get(fips, fips)
            )
            by_fips[fips] = row
            noaa_id = row["noaa_county_id"].strip()
            if status == "matched":
                if not noaa_id:
                    raise ValueError(f"missing NOAA county ID on line {line_number}")
                for existing in by_noaa_id[noaa_id]:
                    if (
                        existing["state_alpha"] != row["state_alpha"]
                        or normalize_county_name(existing["noaa_county_name"])
                        != normalize_county_name(row["noaa_county_name"])
                    ):
                        raise ValueError(
                            f"conflicting county aliases for NOAA ID on line {line_number}"
                        )
                by_noaa_id[noaa_id].append(row)
            elif status != "unmatched" or noaa_id:
                raise ValueError(f"invalid crosswalk status on line {line_number}: {status}")
    return by_fips, dict(by_noaa_id)


def open_weather_file(path: Path) -> TextIO:
    return gzip.open(path, "rt", encoding="utf-8-sig", newline="")


def read_weather_month(
    path: Path,
    expected_variable: str,
    expected_year: int,
    expected_month: int,
    by_noaa_id: dict[str, list[dict[str, str]]],
    report: dict[str, object],
) -> dict[str, list[float | None]]:
    match = NOAA_FILENAME.fullmatch(path.name)
    if match is None:
        raise ValueError(f"unexpected NOAA filename: {path.name}")
    variable, year, month = match.groups()
    if (variable, int(year), int(month)) != (
        expected_variable,
        expected_year,
        expected_month,
    ):
        raise ValueError(f"NOAA filename does not match requested period: {path}")

    expected_days = calendar.monthrange(expected_year, expected_month)[1]
    observations: dict[str, list[float | None]] = {}
    missing_in_calendar = 0
    padding_sentinels = 0
    value_min = math.inf
    value_max = -math.inf
    with open_weather_file(path) as source:
        for line_number, row in enumerate(csv.reader(source), start=1):
            if len(row) != 37 or row[0].strip().lower() != "cty":
                raise ValueError(f"unexpected NOAA schema at {path}:{line_number}")
            noaa_id = row[1].strip()
            if len(noaa_id) != 5 or not noaa_id.isdigit():
                raise ValueError(f"invalid NOAA county ID at {path}:{line_number}")
            if noaa_id in observations:
                raise ValueError(f"duplicate NOAA county ID at {path}:{line_number}: {noaa_id}")
            label = row[2].strip()
            if ":" not in label:
                raise ValueError(f"invalid NOAA county label at {path}:{line_number}")
            label_state, _ = label.split(":", 1)
            if len(label_state.strip()) != 2:
                raise ValueError(f"invalid NOAA state label at {path}:{line_number}")
            if int(row[3]) != expected_year or int(row[4]) != expected_month:
                raise ValueError(f"NOAA row period disagrees with filename at {path}:{line_number}")
            if row[5].strip().lower() != expected_variable:
                raise ValueError(f"NOAA row variable disagrees with filename at {path}:{line_number}")

            daily_values: list[float | None] = []
            for day_index, raw_value in enumerate(row[6:], start=1):
                value_text = raw_value.strip()
                if day_index > expected_days:
                    if value_text not in NOAA_MISSING_VALUES:
                        raise ValueError(
                            f"unexpected data after calendar month at {path}:{line_number}"
                        )
                    padding_sentinels += 1
                    continue
                try:
                    value = parse_weather_value(value_text)
                except ValueError as exc:
                    raise ValueError(f"{exc} at {path}:{line_number}, day {day_index}") from exc
                if value is None:
                    missing_in_calendar += 1
                else:
                    if expected_variable == "prcp" and value < 0:
                        raise ValueError(f"negative precipitation at {path}:{line_number}")
                    if expected_variable != "prcp" and not -100 <= value <= 70:
                        raise ValueError(f"temperature outside plausible range at {path}:{line_number}")
                    value_min = min(value_min, value)
                    value_max = max(value_max, value)
                daily_values.append(value)
            if len(daily_values) != expected_days:
                raise ValueError(f"incorrect number of calendar days at {path}:{line_number}")
            observations[noaa_id] = daily_values
            if noaa_id in by_noaa_id:
                crosswalk_rows = report["_crosswalk_by_noaa_id"][noaa_id]  # type: ignore[index]
                if not any(
                    label_state.strip() == row["state_alpha"]
                    and normalize_county_name(label.split(":", 1)[1])
                    == normalize_county_name(row["noaa_county_name"])
                    for row in crosswalk_rows
                ):
                    raise ValueError(f"NOAA county label disagrees with crosswalk for {noaa_id}")

    data_quality = report["weather_variables"][expected_variable]  # type: ignore[index]
    data_quality["files"] += 1
    data_quality["county_rows"] += len(observations)
    data_quality["valid_days"] += sum(
        value is not None for daily_values in observations.values() for value in daily_values
    )
    data_quality["missing_days"] += missing_in_calendar
    data_quality["padding_sentinels"] += padding_sentinels
    if value_min != math.inf:
        data_quality["minimum"] = min(data_quality["minimum"], value_min)
        data_quality["maximum"] = max(data_quality["maximum"], value_max)
    report["noaa_rows_per_file"].add(len(observations))  # type: ignore[union-attr]
    if len(observations) != report["expected_noaa_counties"]:
        raise ValueError(f"unexpected county-row count in {path}: {len(observations)}")
    return observations


def write_monthly_panel(
    output: Path,
    yield_rows: list[dict[str, str]],
    crosswalk: dict[str, dict[str, str]],
    by_noaa_id: dict[str, list[dict[str, str]]],
    report: dict[str, object],
) -> None:
    targets_by_year: dict[int, list[dict[str, str]]] = defaultdict(list)
    for row in yield_rows:
        targets_by_year[int(row["year"])].append(row)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary_output = output.with_name(output.name + ".tmp")
    written = 0
    matched_rows = 0
    unmatched_rows = 0
    with gzip.open(
        temporary_output, "wt", encoding="utf-8", newline="", compresslevel=6
    ) as destination:
        writer = csv.DictWriter(destination, fieldnames=WEATHER_FIELDS)
        writer.writeheader()
        for year in range(FIRST_YEAR, LAST_YEAR + 1):
            yearly_targets = targets_by_year.get(year, [])
            for month in MONTHS:
                variable_data = {
                    variable: read_weather_month(
                        WEATHER_ROOT
                        / str(year)
                        / f"{variable}-{year}{month:02d}-cty-scaled.csv.gz",
                        variable,
                        year,
                        month,
                        by_noaa_id,
                        report,
                    )
                    for variable in VARIABLES
                }
                ids_by_variable = [set(variable_data[var]) for var in VARIABLES]
                if any(ids != ids_by_variable[0] for ids in ids_by_variable[1:]):
                    raise ValueError(f"NOAA county IDs differ by variable in {year}-{month:02d}")

                for target in yearly_targets:
                    fips = target["county_fips"]
                    source_fips = target["source_county_fips"]
                    crosswalk_row = crosswalk.get(source_fips)
                    noaa_id = crosswalk_row["noaa_county_id"].strip() if crosswalk_row else ""
                    status = "matched" if noaa_id and noaa_id in variable_data["prcp"] else "unmatched"
                    expected_days = calendar.monthrange(year, month)[1]
                    row: dict[str, object] = {
                        "county_fips": fips,
                        "source_county_fips": source_fips,
                        "noaa_county_id": noaa_id,
                        "state_alpha": target["state_alpha"],
                        "county_name": target["county_name"],
                        "year": year,
                        "month": month,
                        "expected_days": expected_days,
                        "weather_match_status": status,
                    }
                    if status == "matched":
                        if target["state_alpha"] != crosswalk_row["state_alpha"]:
                            raise ValueError(f"yield/crosswalk state mismatch for {fips}")
                        if target["county_name"] and normalize_county_name(
                            target["county_name"]
                        ) != normalize_county_name(crosswalk_row["county_name"]):
                            raise ValueError(f"yield/crosswalk county mismatch for {fips}")
                        for variable in VARIABLES:
                            row.update(
                                summarize_days(
                                    variable_data[variable][noaa_id],
                                    variable,
                                )
                            )
                        matched_rows += 1
                    else:
                        for variable in VARIABLES:
                            row.update(summarize_days([None] * expected_days, variable))
                        unmatched_rows += 1
                    writer.writerow(row)
                    written += 1

    os.replace(temporary_output, output)
    report["monthly_panel"] = {
        "path": str(output.relative_to(PROJECT_ROOT)),
        "rows": written,
        "matched_county_months": matched_rows,
        "unmatched_county_months": unmatched_rows,
        "rows_per_yield_record": len(MONTHS),
    }


def main() -> int:
    yield_rows, yield_quality = read_yield_panel(YIELD_PATH)
    normalize_crosswalk_file(CROSSWALK_PATH)
    crosswalk, by_noaa_id = read_crosswalk(CROSSWALK_PATH)
    for row in yield_rows:
        if row["source_county_fips"] not in crosswalk:
            raise ValueError(
                "yield county is missing from the county crosswalk: "
                f"{row['source_county_fips']}"
            )

    report: dict[str, object] = {
        "period": {"start_year": FIRST_YEAR, "end_year": LAST_YEAR},
        "units": {
            "precipitation": "mm",
            "temperature": "degrees Celsius",
            "yield": "bushels per acre",
        },
        "missing_value_policy": {
            "noaa_sentinels": sorted(NOAA_MISSING_VALUES),
            "zero_precipitation_is_valid": True,
            "missing_weather_values": "Kept missing; no imputation is performed.",
            "yield_cv_nul_bytes": "Removed and treated as missing.",
        },
        "yield_panel": {
            "path": str(YIELD_PATH.relative_to(PROJECT_ROOT)),
            "records": yield_quality["records"],
            "unique_counties": yield_quality["unique_counties"],
            "unique_source_counties": yield_quality["unique_source_counties"],
            "missing_cv_pct": yield_quality["missing_cv_pct"],
            "zero_yield_values_retained": yield_quality["zero_yield_values_retained"],
            "records_by_year": {
                str(year): yield_quality.get(f"year_{year}", 0)
                for year in range(FIRST_YEAR, LAST_YEAR + 1)
            },
        },
        "crosswalk": {
            "path": str(CROSSWALK_PATH.relative_to(PROJECT_ROOT)),
            "source_county_identifiers": len(crosswalk),
            "canonical_counties": len(
                {row["county_fips"] for row in crosswalk.values()}
            ),
            "matched_source_county_identifiers": sum(
                row["match_status"].strip() == "matched"
                for row in crosswalk.values()
            ),
            "matched_noaa_locations": len(by_noaa_id),
            "unmatched_counties": sum(
                row["match_status"].strip() == "unmatched" for row in crosswalk.values()
            ),
        },
        "expected_noaa_files": len(range(FIRST_YEAR, LAST_YEAR + 1))
        * len(MONTHS)
        * len(VARIABLES),
        "expected_noaa_counties": 3107,
        "noaa_files_read": 0,
        "noaa_rows_per_file": set(),
        "weather_variables": {
            variable: {
                "files": 0,
                "county_rows": 0,
                "valid_days": 0,
                "missing_days": 0,
                "padding_sentinels": 0,
                "minimum": math.inf,
                "maximum": -math.inf,
            }
            for variable in VARIABLES
        },
        "_crosswalk_by_fips": crosswalk,
        "_crosswalk_by_noaa_id": {
            noaa_id: rows for noaa_id, rows in by_noaa_id.items()
        },
    }

    write_monthly_panel(PANEL_PATH, yield_rows, crosswalk, by_noaa_id, report)
    temporary_yield = YIELD_PATH.with_suffix(".csv.tmp")
    with temporary_yield.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.DictWriter(destination, fieldnames=YIELD_FIELDS)
        writer.writeheader()
        writer.writerows({field: row[field] for field in YIELD_FIELDS} for row in yield_rows)
    os.replace(temporary_yield, YIELD_PATH)
    report["noaa_files_read"] = sum(
        variable_report["files"]
        for variable_report in report["weather_variables"].values()  # type: ignore[union-attr]
    )
    report["noaa_rows_per_file"] = sorted(report["noaa_rows_per_file"])
    for variable_report in report["weather_variables"].values():  # type: ignore[union-attr]
        if variable_report["minimum"] == math.inf:
            variable_report["minimum"] = None
            variable_report["maximum"] = None
    report.pop("_crosswalk_by_fips")
    report.pop("_crosswalk_by_noaa_id")
    temporary_report = REPORT_PATH.with_suffix(".json.tmp")
    temporary_report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary_report, REPORT_PATH)
    print(f"Validated {report['noaa_files_read']} NOAA files.")
    print(f"Wrote {report['monthly_panel']['rows']} monthly county-weather rows.")
    print(f"Wrote data-quality report to {REPORT_PATH.relative_to(PROJECT_ROOT)}.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, KeyError, csv.Error) as error:
        print(f"Data preparation failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
