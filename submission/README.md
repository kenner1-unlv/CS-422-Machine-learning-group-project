# CS 422 final project submission guide

Submit the files separately in WebCampus; do not upload this directory as a ZIP. The four-page instructor `Project Final.pdf` was checked on November 21, 2026. `FINAL_REPORT.pdf` is the formatted report. `source/` contains one `.py.txt` copy of each project script and test, retaining the normal `.py` versions in the development repository. `config/` contains the exact JSON configurations. `results/` contains the saved comparison tables and model selections needed to check reported scores. `PRESENTATION_OUTLINE.md` is a speaking plan, not a completed slide deck. The instructor requires the team name in filenames. The submitted proposal lists “Not Applicable” as the team name, so the team must confirm a filename convention before uploading.

## Data and scope

The analysis uses [USDA NASS Quick Stats bulk downloads](https://www.nass.usda.gov/datasets/) for county corn-grain yield and [NOAA nClimGrid-Daily](https://www.ncei.noaa.gov/products/land-based-station/nclimgrid-daily) county-area weather. The tracked [development repository](https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project) contains processed yield, county crosswalk, monthly weather, and quality-report files in `data/processed/`; provide repository access to the grader if it is private. Original source downloads and as-of-date NOAA vintages are not included. The repository `Readme.md` documents the raw download layout and `scripts/prepare_data.py` rebuild step if the original sources are obtained. The primary cohort has 393 counties and 10,218 county-years, with 6,681 train (2000–2016), 1,572 validation (2017–2020), and 1,965 test (2021–2025) rows per cutoff. Feature cutoffs are May, June, July, and August. `PROJECT_SPEC.md`, `STUDY_DATA_PLAN.md`, and `FEATURE_PLAN.md` in the development repository describe filtering and allowed features.

## Reproduction in a clean development checkout

Use a separate clean copy of the project before rerunning models so existing frozen predictions remain intact. Use Python 3.13 for the original pinned modeling environments. Baseline, Gradient Boosting, and remaining-model requirements were recorded separately because their version pins differ; do not combine the three environments. The remaining-model pins are in `requirements-remaining-models.txt`: NumPy 2.2.6, pandas 3.1.0, SciPy 1.16.3, scikit-learn 1.9.0, Matplotlib 3.10.3, joblib 1.6.0, and threadpoolctl 3.6.0. `requirements-modeling.txt` instead records NumPy 2.5.4 and scikit-learn 1.9.1; `requirements-gradient-boosting.txt` extends it. Saved estimator files should only be loaded from trusted sources and matching package versions. The optional DOCX export script additionally requires `python-docx==1.2.0`.

From the development `Project` root, after installing the pinned dependencies in a fresh environment:

```powershell
py -3.13 -m pip install -r requirements-remaining-models.txt
py -3.13 scripts/build_study_sets.py
py -3.13 scripts/build_splits.py
py -3.13 scripts/build_features.py
py -3.13 scripts/run_remaining_models.py random_forest
py -3.13 scripts/run_remaining_models.py neural_network
py -3.13 scripts/compare_remaining_models.py
py -3.13 scripts/verify_final_results.py
py -3.13 scripts/final_eda.py
py -3.13 -m unittest discover -s tests -v
```

The standard-model results can also be audited **without retraining** with `py -3.13 scripts/verify_final_results.py`. It checks validation-selected settings and feature lists, common row keys and targets, and recomputes MAE, RMSE, and bias for 80 saved metric groups. The submitted comparison tables are in `results/team_model_comparison/`; selection records are in `results/selections/`. Linear/Ridge and Gradient Boosting fit commands and their earlier pinned requirements are documented in `LINEAR_REGRESSION.md` and `GRADIENT_BOOSTING.md` in the development repository. The random seed is 42 in the model configurations. Validation MAE selects tunable settings; the frozen 2021–2025 test rows are scored once per saved run. Do not use test labels to change the feature lists or tuning grid.

The `.py.txt` copies in this submission are readable source for WebCampus. To run a copy outside the development checkout, restore its `.py` extension and the relative `scripts/`, `tests/`, `config/`, and `data/processed/` layout first. The submitted copies do not include the large processed datasets or full saved row predictions; those are tracked or retained in the development repository. Another person needs access to those inputs to execute the main comparison.

## Known limits and handoff

The weather fields are retrospective NOAA values, so these runs verify calendar cutoffs but not original as-of-date availability. Only five test harvest years exist, and county rows within a year are correlated. The team must confirm the dated post-results discussion, each member's contribution wording, AI disclosure, final slides, and team-name filenames before submission. All four members are listed as CS 422 students in the submitted proposal, so the instructor's conditional CS 622 research-paper method requirement appears inapplicable; verify if enrollment changed.
