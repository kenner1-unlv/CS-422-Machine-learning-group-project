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

`Not_Applicable_Final_Report_v2.pdf` and `Not_Applicable_Presentation.pdf` contain the final discussion, model responsibilities, results, limitations and AI disclosures. Neither a deployment nor a private repository is required by the instructor. All required uploads are separate files; a WebCampus receipt is the evidence of actual submission.


## Submission format and reproducibility boundary

Following the instructor's final-project instructions (pages 3–4), upload each required file separately: the version 2 report PDF, presentation PDF, each Python source as `.py.txt`, and README, requirements, configurations and result tables. No ZIP or notebook substitutes for those source files. One member uploads for the team. All upload filenames begin `Not_Applicable_`; the manifest supplies the original paths. To execute a source copy, restore its mapped directory and filename and remove the final `.txt`. Restore the configuration and result paths as well; do not run the prefixed copies as though their imports and relative paths were unchanged.

**The 52-file Canvas packet is not a standalone reproduction environment.** It contains the source and reported result tables, but omits approximately 48 MB of processed data and 41 MB of retained predictions. Rebuilding features and verifying the saved model scores requires the public repository's processed inputs and frozen predictions. The clone-and-verify commands above use the frozen analysis commit `89c882f48b3cbcf872b18d970d34ad95c5dc162d`, whose scientific results are unchanged by the version 2 formatting. The repository must stay public through grading. Original raw downloads are not bundled. The submitted tables can be cross-checked without fitting models; regenerating predictions requires the corresponding model environment and training commands, and identical refitting of Lester's original NN cannot be certified because his original versions were not recorded.

## Windows/macOS line endings and hash checks

Windows checkouts commonly use CRLF line endings; macOS/Linux and Git blobs commonly use LF. Alex found 45 text upload copies with Windows line endings while the corresponding GitHub blobs used LF. Those byte differences change SHA-256 hashes even when the restored Python source or table text is otherwise identical. They do not change the reported rounded RF metrics; the separate Mac RF reproduction showed prediction differences no larger than 8.53e-14 bu/acre, which should not be confused with text-file line endings.

The upload manifest records **exact submitted bytes**, not normalized text or GitHub blob hashes. Check downloaded/uploaded files against that manifest before editing, re-saving or converting line endings. PDFs and all other binary files must be compared byte-for-byte. The upload directory is marked `-text` in `.gitattributes` so Git preserves its manifest-recorded bytes. Development sources outside that directory may be converted by Git's checkout settings.

On Windows, use `Get-FileHash -Algorithm SHA256 -LiteralPath .\Not_Applicable_build_features.py.txt`; on macOS, use `shasum -a 256 Not_Applicable_build_features.py.txt`. Compare the result with the same filename's manifest row. When comparing a restored text file against a development checkout, first compare exact hashes. If they differ, compare content after replacing CRLF with LF on both sides; claim a line-ending-only difference only if that normalized comparison matches. Do not normalize binaries or dismiss other differences as line endings.
