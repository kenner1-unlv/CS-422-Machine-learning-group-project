# not applicable (Group 2): upload and reproduction guide

Upload the report PDF, Figma presentation PDF, `.py.txt` source files, and reproduction support files separately to WebCampus. Do not upload a ZIP or notebooks. This upload set includes 30 source mirrors: 21 scripts and nine tests.

The team is Russell Kennedy, Tylie Anderson, Alexander Aquiningoc and Lester Iwuajoku. The team name is “not applicable”; upload filenames use `Not_Applicable_`.

The manifest maps upload filenames to development paths. To run a source file, restore its mapped directory/filename, remove the final `.txt`, and use the data/config/result layout described below. Do not execute prefixed modules without restoring their original names.

For the simplest reproducible starting point, clone the public project and use the frozen analysis snapshot:

```powershell
git clone https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project.git
cd CS-422-Machine-learning-group-project
git checkout 89c882f48b3cbcf872b18d970d34ad95c5dc162d
py -3.13 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-remaining-models.txt
.\.venv\Scripts\python.exe scripts/build_study_sets.py
.\.venv\Scripts\python.exe scripts/build_splits.py
.\.venv\Scripts\python.exe scripts/build_features.py
.\.venv\Scripts\python.exe scripts/verify_final_results.py
```

On macOS/Linux use `python3.13 -m venv .venv` and `.venv/bin/python` for the commands. These commands rebuild deterministic inputs and audit retained predictions; they do not train new models. The processed data and saved row predictions are in the public repository, not duplicated in this small text-source packet. Original raw downloads are not bundled.

Seed 42 and shared train/validation/test years are recorded in the submitted configs and selection JSON. Keep the three requirements files in their original separate environments; they contain different historic pins. Current main CI passed all 30 tests using Python 3.13 and the remaining-model pins. Lester's original fit versions were not recorded and remain unavailable; the current environment does not certify an identical NN refit. NN validation summaries are author-reported, and test metrics are checked from retained prediction rows.

`Not_Applicable_Final_Report.pdf` and `Not_Applicable_Presentation.pdf` contain the final discussion, model responsibilities, results, limitations and AI disclosures. Neither a deployment nor a private repository is required by the instructor. All required uploads are separate files; a WebCampus receipt is the evidence of actual submission.
