# Final Figma presentation speaking cues

## Slide 1

Suggested speaker: Russell Kennedy

- Introduce the approved corn-yield problem and the four model responsibilities.
- Frame this as a retrospective county-level comparison, with MAE in bushels per acre.
- Suggested total presentation time is about 12 minutes plus questions.

Sources:
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/PROJECT_SPEC.md
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/FINAL_REPORT.md

Final combined project: Tylie RF reproduction bd92250 and Lester NN documentation 8e4e763 are incorporated. All reported rounded scores remain unchanged.

## Slide 2

Suggested speaker: Russell Kennedy

- Explain the county/year join, missing-record exclusions and primary complete-county scope.
- Each cutoff reuses the same county-years. Full completeness may select a different population from counties with missing reports.
- Weather uses retrospective revised values. Calendar cutoffs alone do not prove original real-time availability.

Sources:
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/data/processed/data_quality_report.json
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/STUDY_DATA_PLAN.md
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/FEATURE_PLAN.md
https://www.nass.usda.gov/datasets/
https://www.ncei.noaa.gov/products/land-based-station/nclimgrid-daily

Final combined project: Tylie RF reproduction bd92250 and Lester NN documentation 8e4e763 are incorporated. All reported rounded scores remain unchanged.

## Slide 3

Suggested speaker: Russell Kennedy

- 17 training years, four validation years and five final-test years preserve time order.
- MAE is the primary metric. RMSE is supporting evidence and penalizes larger misses.
- The current audit recomputed 72 metric groups and checked eight author-reported NN validation summaries.
- Transition: the four families answer the same question on these same rows.

Sources:
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/config/splits.json
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/scripts/verify_final_results.py
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/FINAL_REPORT.md

Final combined project: Tylie RF reproduction bd92250 and Lester NN documentation 8e4e763 are incorporated. All reported rounded scores remain unchanged.

## Slide 4

Suggested speaker: All four members

- Each member should explain their assigned family and its evaluation.
- Tylie reproduced and evaluated the RF experiment using the shared runner. Russell authored the shared RF implementation.
- Lester authored the primary NN in 4ac9f59. Russell integrated it and independently audited saved predictions in af2602b.

Sources:
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/FINAL_REPORT.md
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/Readme.md
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/NEURAL_NETWORK.md
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/RANDOM_FOREST.md

Final combined project: Tylie RF reproduction bd92250 and Lester NN documentation 8e4e763 are incorporated. All reported rounded scores remain unchanged.

## Slide 5

Suggested speaker: Russell Kennedy

- Contrast weather-only 37.04 with trend-only 26.97 and combined 24.75.
- The association with year may reflect technology, management and other changing factors. It does not identify a causal explanation.
- Linear uses training-fitted scaling. Ridge selects alpha using validation data.
- The trend-only comparator is a later diagnostic, separate from the original standard-model selection.

Sources:
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/LINEAR_REGRESSION.md
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/results/primary_100_diagnostic_additions/trend_only_metrics.csv
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/results/team_model_comparison/comparison.csv

Final combined project: Tylie RF reproduction bd92250 and Lester NN documentation 8e4e763 are incorporated. All reported rounded scores remain unchanged.

## Slide 6

Suggested speaker: Alexander Aquiningoc

- Explain the declared grid over learning rate, depth, subsample and leaf size, with staged tree-count selection.
- The standard comparison uses tuned gradient boosting. The trend-residual hybrid changes the method and stays exploratory.
- Validation leadership is distinct from the held-out ranking. With trend, GB has the lowest standard test MAE in May and June.
- Trees cannot extrapolate a numeric year feature beyond training values.

Sources:
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/GRADIENT_BOOSTING.md
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/results/primary_100_gradient_boosting/selection.json
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/results/team_model_comparison/comparison.csv

Final combined project: Tylie RF reproduction bd92250 and Lester NN documentation 8e4e763 are incorporated. All reported rounded scores remain unchanged.

## Slide 7

Suggested speaker: Tylie Anderson

- Explain bootstrap averaging, max_features 0.7, and the depth/leaf grid.
- Tylie’s Mac reproduction matches all 81,744 keys/targets and preserves two-decimal scores. It is same-seed cross-platform reproduction, not a multi-seed study.
- The year trend helps RF but trees cannot extend the numeric trend beyond the training years.
- Tylie should explain her reproduced RF run and its interpretation during team review. Her authored result commit is bd9225064552899174a278a658eaceef7568a489.

Sources:
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/RANDOM_FOREST.md
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/results/primary_100_random_forest/selection.json
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/results/team_model_comparison/comparison.csv

Final combined project: Tylie RF reproduction bd92250 and Lester NN documentation 8e4e763 are incorporated. All reported rounded scores remain unchanged.

## Slide 8

Suggested speaker: Lester Iwuajoku

- Lester’s original source commit is 4ac9f596901f9b93a0e1f23b7464cddf90d33ce8. Distinguish authorship from Russell’s normalization, comparison and independent saved-row checks.
- The input scaler fits training rows only. The yield target remains unscaled. Architecture is fixed, not selected from a tuning grid.
- All eight runs reached 500 iterations. Warnings were suppressed, so reaching the cap does not establish convergence.
- Eight pooled NN validation scores are author-reported. Same-run validation rows are not supplied; original software versions were not recorded and remain unavailable. No further metadata collection is planned.
- This network leads July and August test MAE in both feature variants. This descriptive test ranking does not replace validation-based selection.

Sources:
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/85e84a9f3fac1250b19cad362904219559e774aa/NEURAL_NETWORK.md
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/85e84a9f3fac1250b19cad362904219559e774aa/scripts/neural_network_model.py
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/85e84a9f3fac1250b19cad362904219559e774aa/results/neural_network/model_comparison.csv

Final combined project: Tylie RF reproduction bd92250 and Lester NN documentation 8e4e763 are incorporated. All reported rounded scores remain unchanged.

Lester AI disclosure:
The neural network was implemented using Python and scikit-learn. ChatGPT assisted with understanding and configuring MLPRegressor, StandardScaler, Pipeline, model.fit, and model.predict. It also helped explain how to calculate evaluation metrics using mean_absolute_error and mean_squared_error. I reviewed the AI-assisted suggestions and tested the implementation by running the model and examining MAE and RMSE.

I did not accept the suggestion that the absence of convergence warnings meant the models had converged. The code suppressed ConvergenceWarning, and all eight models reached the 500-iteration limit. I reported the MAE and RMSE results without claiming convergence.

## Slide 9

Suggested speaker: All four members

- Identify each model’s responsible member from slide 4. This is one frozen chronological test split, not a repeated-run average.
- June GB and RF differ by 0.01 MAE after rounding. Avoid treating such differences as convincing without independent uncertainty analysis.
- Baseline test MAE is 42.29. Supporting RMSE and validation metrics are in the appendix.

Sources:
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/results/team_model_comparison/comparison.csv
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/FINAL_REPORT.md

Final combined project: Tylie RF reproduction bd92250 and Lester NN documentation 8e4e763 are incorporated. All reported rounded scores remain unchanged.

## Slide 10

Suggested speaker: Russell Kennedy

- Both panels use a fixed 20–45 MAE range, intentionally truncated from zero to show trends across the cutoffs.
- Adding the declared year feature substantially lowers error. More weather does not monotonically improve every model at every cutoff.
- County rows within harvest years are correlated. The five years matter more for independence than the raw row count.

Sources:
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/results/team_model_comparison/comparison.csv

Final combined project: Tylie RF reproduction bd92250 and Lester NN documentation 8e4e763 are incorporated. All reported rounded scores remain unchanged.

## Slide 11

Suggested speaker: Alexander Aquiningoc and Tylie Anderson

- Ask what changes between the pooled average and this single year. NN’s 2023 result does not establish universal drought robustness.
- Dry-group MAE in July with trend is 28.16 Linear, 36.02 GB, 31.54 RF and 23.31 NN.
- Group thresholds use training weather, but the group-analysis design followed inspection of earlier overall test scores. Keep the exploratory label.
- Transition: choose a recommendation using validation and state the limits of five held-out years.

Sources:
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/results/team_model_comparison/comparison_by_year.csv
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/results/team_model_comparison/subgroup_comparison.csv
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/results/weather_groups/README.md

Final combined project: Tylie RF reproduction bd92250 and Lester NN documentation 8e4e763 are incorporated. All reported rounded scores remain unchanged.

## Slide 12

Suggested speaker: Russell Kennedy

- GB leads validation MAE for the trend variant at all cutoffs. NN leads later test cutoffs, which is descriptive rather than a new test-based selection rule.
- A crop insurer or regional analyst could use county yield estimates as one input to planning, with human review.
- A real workflow would require original source vintages, input validation, cohort checks and later-season monitoring. No deployed or financial-decision performance is claimed.

Sources:
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/FINAL_REPORT.md
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/results/team_model_comparison/comparison.csv

Final combined project: Tylie RF reproduction bd92250 and Lester NN documentation 8e4e763 are incorporated. All reported rounded scores remain unchanged.

## Slide 13

Suggested speaker: Lester Iwuajoku and Russell Kennedy

- Do not claim statistical significance or universal model superiority.
- Future work can include more independent years, original NOAA release vintages, broader geography and missing agronomic variables.
- NN original software versions are missing. Validation row exports are pending, so those summaries remain author-reported.
- No holdout change, new fitting or retuning is part of tonight’s preparation.

Sources:
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/FINAL_REPORT.md
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/NEURAL_NETWORK.md

Final combined project: Tylie RF reproduction bd92250 and Lester NN documentation 8e4e763 are incorporated. All reported rounded scores remain unchanged.

## Slide 14

Suggested speaker: Russell Kennedy, with participants adding their own recollections.

Discussion series: November 11, 16 and 18, 2026, mainly in person after class, recalled by Russell. Individual exchanges are not assigned to specific dates and no claim is made that all four attended a single meeting.

Russell and Alexander discussed which results to prepare and how honestly to acknowledge weaknesses and oversights. Their interpretation was that no single model clearly won across all settings. The report separates validation-supported recommendations from cutoff/year-specific test rankings.

Tylie proposed checking RF numbers on Mac. Her later retained run (commit bd9225064552899174a278a658eaceef7568a489, dated November 22) reproduces 81,744 row keys/targets with unchanged rounded scores. That is a concrete experimental follow-up to the discussion.

Russell also recalls Lester comparing the NN with an earlier trial and obtaining similar numbers. The trial is not retained; no quantitative or implementation-superiority claim is made from it.

Discussion record: https://docs.google.com/spreadsheets/d/1lhPMqn3DQDZXlgQLka2vUtC4NYIjcRMNtwSHZQVWptc/edit#gid=140541277&range=A4:G4

## Slide 15

Suggested speaker: All four members

- Return to the approved objective: how reliability changes across cutoffs and weather conditions.
- Invite questions about the chronological split, feature availability, metrics and limitations. Each member should answer about their own contribution.
- Avoid turning the pooled ranking into a universal or operational claim.

Sources:
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/FINAL_REPORT.md
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/results/team_model_comparison/comparison.csv

Final combined project: Tylie RF reproduction bd92250 and Lester NN documentation 8e4e763 are incorporated. All reported rounded scores remain unchanged.

## Slide 16

Suggested speaker: Russell Kennedy.

Russell used Codex CLI, GitHub integrations, and Figma for planning, implementation, organization, presentation design and detailed verification: tests, repository inspection, hash comparison, artifact reconciliation and adversarial checks. He retains responsibility for final decisions and review.

Alexander's exact statement, relayed by Russell: “i use gemini ai overview to help explain methods and fix broken code”. Russell reports his manual checks, presentation editing, requirements auditing and shared comparison analysis separately.

Lester's supplied disclosure:
The neural network was implemented using Python and scikit-learn. ChatGPT assisted with understanding and configuring MLPRegressor, StandardScaler, Pipeline, model.fit, and model.predict. It also helped explain how to calculate evaluation metrics using mean_absolute_error and mean_squared_error. I reviewed the AI-assisted suggestions and tested the implementation by running the model and examining MAE and RMSE.

I did not accept the suggestion that the absence of convergence warnings meant the models had converged. The code suppressed ConvergenceWarning, and all eight models reached the 500-iteration limit. I reported the MAE and RMSE results without claiming convergence.

Russell confirms that Tylie did not use AI; she executed the reproduction through terminal commands. The shared RF runner's prior authorship remains credited separately.

Verification boundary: 72 metric groups recomputed from retained rows; eight NN validation summaries author-reported. Original NN software versions are unrecorded and unavailable. No exact original-fit environment reproduction or convergence is claimed. Current main CI passed all 30 tests on pinned Python 3.13; that is distinct from original NN fit metadata.

Disclosure: https://docs.google.com/spreadsheets/d/1lhPMqn3DQDZXlgQLka2vUtC4NYIjcRMNtwSHZQVWptc/edit#gid=180000001&range=E5
Data: https://www.nass.usda.gov/datasets/
https://www.ncei.noaa.gov/products/land-based-station/nclimgrid-daily
https://doi.org/10.25921/c4gt-r169
Libraries: https://scikit-learn.org/stable/

## Slide 17

Suggested speaker: All four members

- Validation has 1,572 rows and test has 1,965 rows. All figures are pooled county-year metrics.
- The NN validation summary is only checked against Lester’s supplied aggregate, not reproduced from rows.
- The equal-weight four-family ensemble is exploratory and has no available validation score. It does not replace the selected standard-model recommendation.

Sources:
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/results/team_model_comparison/comparison.csv
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/results/primary_100_diagnostic_additions/four_model_mean_lester_metrics.csv

Final combined project: Tylie RF reproduction bd92250 and Lester NN documentation 8e4e763 are incorporated. All reported rounded scores remain unchanged.

## Slide 18 (excluded editing slide)

Suggested speaker: Team

- All four contributions and disclosure dispositions are incorporated. This excluded slide is retained only as an editing record.
- Do not replace Lester’s missing same-run validation data with a reconstructed run.
- Preserve the frozen holdout and separate author/integrator attribution during final review.

Sources:
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/review/TRACKER_UPDATES.md
https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/blob/89c882f48b3cbcf872b18d970d34ad95c5dc162d/SUBMISSION_AUDIT.md

Final combined project: Tylie RF reproduction bd92250 and Lester NN documentation 8e4e763 are incorporated. All reported rounded scores remain unchanged.
