# CS 422 final presentation outline

Use one shared deck and a common result table. The assignments below follow documented primary model responsibilities; the team should confirm who presents each section and the speaking time.

1. **Russell Kennedy — research question and protocol.** Explain the approved objective, USDA/NOAA sources, 393-county cohort, four forecast cutoffs, and chronological split. Show the target trend and distinguish weather-only from weather-plus-trend.
2. **Alexander Aquiningoc — Gradient Boosting.** Explain the validation grid, tuned standard model, July/yearly errors, and why the separate trend-residual hybrid is exploratory rather than a standard-comparison winner.
3. **Tylie Anderson — Random Forest.** Explain the bounded validation search, common-row comparison, weather-only early-cutoff results, and the limits of tree extrapolation on the year feature.
4. **Lester Iwuajoku — Neural Network.** Explain training-only scaling, original 250-iteration setting, validation choices, and the separate stopping study with mixed held-out effects.
5. **Shared conclusion and questions.** Show one consolidated validation/test MAE and RMSE table, the trend-only 26.97 July comparator, July Linear weather-only 37.04 versus weather-plus-trend 24.75, and the five-year/retrospective-weather limitations. State that Gradient Boosting is the validation-supported individual standard model at all cutoffs, while held-out rankings vary. Label the ensemble and hybrid as later exploratory analyses.

Suggested visual sequence: objective → data/cohort → split and feature cutoff → yield trend → common model comparison → 2023 and dry-group failures → trend-only diagnostic → limitations and future operational backtest. Do not claim an unverified team discussion, statistical significance, or an operational as-of-date forecast.
