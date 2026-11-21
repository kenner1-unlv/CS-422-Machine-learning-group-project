"""Make presentation figures for the fixed supplemental analyses."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results/supplemental_figures"
MONTHS = {5: "May", 6: "June", 7: "July", 8: "August"}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    standard = pd.read_csv(ROOT / "results/team_model_comparison/comparison.csv")
    standard = standard[(standard["variant"] == "weather_plus_trend") &
                        (standard["partition"] == "test")]
    blend = pd.read_csv(ROOT / "results/primary_100_diagnostic_additions/four_model_mean_original_metrics.csv")
    blend = blend[(blend["variant"] == "weather_plus_trend") &
                  (blend["partition"] == "test")]
    trend = pd.read_csv(ROOT / "results/primary_100_diagnostic_additions/trend_only_metrics.csv")
    trend = trend[trend["partition"] == "test"]

    fig, ax = plt.subplots(figsize=(8, 4.8))
    for model, label, color in [
        ("linear", "Linear", "#2f6aab"),
        ("gradient_boosting", "Gradient Boosting", "#d66a32"),
        ("random_forest", "Random Forest", "#208b75"),
        ("neural_network", "Neural Network", "#a94e7d"),
    ]:
        rows = standard[standard["model"] == model].sort_values("cutoff_month")
        ax.plot([MONTHS[c] for c in rows["cutoff_month"]], rows["mae"],
                marker="o", linewidth=1.4, alpha=0.7, label=label, color=color)
    ax.plot([MONTHS[c] for c in blend.sort_values("cutoff_month")["cutoff_month"]],
            blend.sort_values("cutoff_month")["mae"], marker="D", linewidth=2.5,
            color="#171717", label="Equal mean of four")
    ax.axhline(trend["mae"].iloc[0], color="#777777", linestyle="--",
               label="Trend only")
    ax.set(xlabel="Forecast cutoff", ylabel="Test MAE (bu/acre)",
           title="Primary 393 counties: weather plus year trend")
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(OUT / "ensemble_and_trend_test_mae.png", dpi=160)
    plt.close(fig)

    expanded = pd.read_csv(ROOT / "results/expanded_90_four_model_check/shared_primary_comparison.csv")
    expanded = expanded[(expanded["partition"] == "test") &
                        (expanded["variant"] == "weather_plus_trend")]
    models = ["linear", "gradient_boosting", "random_forest", "neural_network"]
    colors = ["#2f6aab", "#d66a32", "#208b75", "#a94e7d"]
    fig, ax = plt.subplots(figsize=(8, 4.7))
    x = np.arange(4)
    width = 0.2
    for i, (model, color) in enumerate(zip(models, colors)):
        rows = expanded[expanded["model"] == model].sort_values("cutoff_month")
        ax.bar(x + (i - 1.5) * width, rows["mae_expanded_minus_primary"],
               width=width, color=color, label=model.replace("_", " ").title())
    ax.axhline(0, color="#555555", linewidth=1)
    ax.set(xticks=x, xticklabels=list(MONTHS.values()), xlabel="Forecast cutoff",
           ylabel="Expanded-training MAE minus primary-training MAE (bu/acre)",
           title="Same primary test rows; positive means expanded training was worse")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(fontsize=8, ncol=2)
    fig.tight_layout()
    fig.savefig(OUT / "expanded_training_effect.png", dpi=160)
    plt.close(fig)
    print(f"Saved supplemental figures to {OUT}")


if __name__ == "__main__":
    main()
