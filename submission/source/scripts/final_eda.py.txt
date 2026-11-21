"""Rebuild descriptive EDA for the fixed primary_100 cohort.

Run from the Project root: python scripts/final_eda.py
All weather/yield associations and feature correlations use training years only.
Held-out residual examples are explicitly post-test descriptive diagnostics.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "final_eda"
OUT.mkdir(parents=True, exist_ok=True)


def save(name: str) -> None:
    plt.tight_layout()
    plt.savefig(OUT / name, dpi=170, bbox_inches="tight")
    plt.close()


def main() -> None:
    yields = pd.read_csv(ROOT / "data/study_sets/primary_100/observed_yields.csv", dtype={"county_fips": str})
    counties = pd.read_csv(ROOT / "data/study_sets/primary_100/counties.csv", dtype={"county_fips": str})
    features = pd.read_csv(ROOT / "data/features/primary_100/cutoff_07.csv", dtype={"county_fips": str})
    split = np.select([yields.year <= 2016, yields.year <= 2020], ["Train", "Validation"], default="Test")
    yields["partition"] = split
    summary = yields.groupby("partition").yield_bu_per_acre.agg(["count", "mean", "median", "std", "min", "max", lambda x: x.quantile(.25), lambda x: x.quantile(.75)])
    summary.columns = ["n", "mean", "median", "sd", "min", "max", "q25", "q75"]
    summary.to_csv(OUT / "yield_distribution.csv")
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for part in ["Train", "Validation", "Test"]:
        ax.hist(yields.loc[yields.partition == part, "yield_bu_per_acre"], bins=np.arange(0, 351, 10), density=True, alpha=.45, label=part)
    ax.set(xlabel="County yield (bu/acre)", ylabel="Density", title="Primary cohort yield distribution by chronological partition")
    ax.legend()
    save("yield_distribution.png")

    annual = yields.groupby(["year", "partition"]).yield_bu_per_acre.agg(["mean", "median", "std", "count"]).reset_index()
    annual.to_csv(OUT / "annual_yield.csv", index=False)
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(annual.year, annual["mean"], marker="o", ms=3, label="Mean")
    ax.plot(annual.year, annual["median"], label="Median")
    ax.axvline(2016.5, color="gray", ls="--"); ax.axvline(2020.5, color="gray", ls="--")
    ax.set(xlabel="Harvest year (train | validation | test)", ylabel="Yield (bu/acre)", title="Annual yield in the fixed 393-county cohort")
    ax.legend()
    save("yield_trend.png")

    source_yields = pd.read_csv(ROOT / "data/processed/usda_county_corn_yield_1951_2025.csv",
                                usecols=["county_fips", "state_alpha", "year"], dtype={"county_fips": str})
    available = source_yields[source_yields.year.between(2000, 2025)].groupby("state_alpha").county_fips.nunique().rename("yield_reporting_counties")
    coverage = counties.groupby("state").size().rename("primary_counties").to_frame().join(available, how="left")
    coverage["primary_share_of_yield_reporting"] = coverage.primary_counties / coverage.yield_reporting_counties
    coverage = coverage.reset_index().sort_values("primary_counties", ascending=False)
    coverage.to_csv(OUT / "state_coverage.csv", index=False)
    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    axes[0].bar(coverage.state, coverage.primary_counties)
    axes[0].set(ylabel="Primary counties", title="Geographic coverage of the fixed primary cohort")
    axes[1].bar(coverage.state, coverage.primary_share_of_yield_reporting * 100)
    axes[1].set(xlabel="State", ylabel="Share of reporting\ncounties (%)")
    axes[1].tick_params(axis="x", rotation=70)
    save("state_coverage.png")

    train = features.loc[features.partition == "train"].copy()
    weather = ["season_precipitation_total_mm", "season_tavg_mean_c", "season_tmax_max_c", "season_tmin_min_c"]
    train[weather].describe(percentiles=[.01, .1, .25, .5, .75, .9, .99]).T.to_csv(OUT / "training_weather_summary.csv")
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, column, label in zip(axes, weather[:2], ["April–July precipitation (mm)", "April–July mean temperature (°C)"]):
        ax.hist(train[column], bins=35)
        ax.set(xlabel=label, ylabel="Training county-years")
    fig.suptitle("Training-period weather distributions; July cutoff")
    save("training_weather_distributions.png")

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for ax, column, label in zip(axes, weather[:2], ["April–July precipitation (mm)", "April–July mean temperature (°C)"]):
        ax.hexbin(train[column], train.yield_bu_per_acre, gridsize=35, mincnt=1, cmap="viridis")
        ax.set(xlabel=label, ylabel="Yield (bu/acre)")
    fig.suptitle("Training-period weather–yield associations; descriptive, unadjusted")
    save("training_weather_yield.png")
    train[[*weather, "yield_bu_per_acre", "year_since_2000"]].corr().to_csv(OUT / "training_correlations.csv")
    numeric_features = [c for c in train.columns if c not in
                        {"county_fips", "year", "cutoff_month", "partition", "yield_bu_per_acre"}]
    correlations = train[numeric_features].corr()
    correlations.to_csv(OUT / "training_feature_correlation_matrix.csv")
    pairs = correlations.where(np.triu(np.ones(correlations.shape), 1).astype(bool)).stack().rename("pearson_r")
    pairs.reindex(pairs.abs().sort_values(ascending=False).index).head(30).to_csv(OUT / "top_feature_correlations.csv")
    selected = ["preseason_precipitation_total_mm", "m05_precipitation_total_mm",
                "m06_precipitation_total_mm", "m07_precipitation_total_mm",
                "season_precipitation_total_mm", "m05_tavg_mean_c", "m06_tavg_mean_c",
                "m07_tavg_mean_c", "season_tavg_mean_c", "year_since_2000"]
    fig, ax = plt.subplots(figsize=(8, 7))
    im = ax.imshow(correlations.loc[selected, selected], vmin=-1, vmax=1, cmap="coolwarm")
    ax.set_xticks(range(len(selected)), [s.replace("precipitation_total_mm", "precip").replace("tavg_mean_c", "temp") for s in selected], rotation=75, ha="right", fontsize=8)
    ax.set_yticks(range(len(selected)), [s.replace("precipitation_total_mm", "precip").replace("tavg_mean_c", "temp") for s in selected], fontsize=8)
    fig.colorbar(im, ax=ax, label="Pearson correlation")
    ax.set_title("Training-only July feature correlations")
    save("training_feature_correlations.png")

    # The saved standard-model predictions are read only; no model is fitted here.
    paths = {
        "linear": ROOT / "results/primary_100_baselines/predictions.csv",
        "gradient_boosting": ROOT / "results/primary_100_gradient_boosting/predictions.csv",
        "random_forest": ROOT / "results/primary_100_random_forest/predictions.csv.gz",
        "neural_network": ROOT / "results/primary_100_neural_network/predictions.csv.gz",
    }
    rows = []
    for family, path in paths.items():
        if not path.exists():
            continue
        p = pd.read_csv(path, dtype={"county_fips": str})
        p = p[(p.partition == "test") & (p.cutoff_month == 7) & (p.variant == "weather_plus_trend")]
        if family == "gradient_boosting":
            p = p[p.model == "gbr_tuned"]
        elif family == "linear":
            p = p[p.model == "linear"]
        p = p.assign(family=family)
        rows.append(p)
    preds = pd.concat(rows, ignore_index=True)
    preds["error"] = preds.predicted_yield - preds.observed_yield
    worst = preds.assign(abs_error=lambda x: x.error.abs()).sort_values("abs_error", ascending=False).groupby("family").head(10)
    county_context = yields[["county_fips", "year", "state_alpha", "county_name", "cv_pct"]]
    weather_context = features[["county_fips", "year", "season_precipitation_total_mm", "season_tavg_mean_c", "season_tmax_max_c"]]
    worst = worst.merge(county_context, on=["county_fips", "year"], validate="many_to_one")
    worst = worst.merge(weather_context, on=["county_fips", "year"], validate="many_to_one")
    worst[["family", "county_fips", "state_alpha", "county_name", "year", "observed_yield",
           "predicted_yield", "error", "abs_error", "cv_pct", "season_precipitation_total_mm",
           "season_tavg_mean_c", "season_tmax_max_c"]].to_csv(OUT / "july_high_error_examples.csv", index=False)
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.5))
    for family, g in preds.groupby("family"):
        axes[0].scatter(g.observed_yield, g.predicted_yield, s=4, alpha=.14, label=family)
        axes[1].hist(g.error, bins=np.arange(-150, 151, 10), histtype="step", density=True, label=family)
    axes[0].plot([0, 350], [0, 350], color="black", ls="--", lw=1)
    axes[0].set(xlabel="Observed (bu/acre)", ylabel="Predicted (bu/acre)")
    axes[1].axvline(0, color="black", ls="--", lw=1)
    axes[1].set(xlabel="Predicted minus observed (bu/acre)", ylabel="Density")
    axes[1].legend(fontsize=8)
    fig.suptitle("July test predictions and residuals; post-test descriptive")
    save("july_test_residuals.png")
    print(f"Saved EDA to {OUT}")


if __name__ == "__main__":
    main()
