> **Final packet verification supersedes older pending statements below:** report/disclosures/discussion refreshed; native Figma PDF has 17 pages, slide 14 included and 18 excluded; all 30 source and 18 support mirrors match; all local links resolve. Original NN versions are unrecorded/unavailable and no longer requested. See FINAL_PACKET_VERIFICATION.json and the current submission checklist.

# Contribution and result verification

## Candidate and provenance

The final-submission candidate combines base `85e84a9f3fac1250b19cad362904219559e774aa`, Tylie's unchanged RF artifacts from `bd9225064552899174a278a658eaceef7568a489`, and Lester's method documentation from `8e4e763c52a277e6544b76b0462860eed58bbfc6` as integrated in PR #19. Report and slide prose describe this intended combined final project. Actual outstanding merge/publish tasks live in the [submission checklist](../submission/SUBMISSION_CHECKLIST.md).

## Random Forest artifact audit

- 14 supplied result files copied byte-for-byte from Tylie's commit; [file hashes](RF_REPRODUCTION_FILES.tsv).
- 81,744 prediction rows. County FIPS, year, cutoff, partition, variant, model and observed yield match the preceding run in the same row order.
- Maximum predicted-yield/residual delta: `8.526512829121202e-14` bu/acre.
- Maximum pooled MAE delta: `7.105427357601002e-15` bu/acre. All two-decimal metrics, selected hyperparameters and standard-model rankings remain unchanged.
- Original feature-input hashes and predictor lists match. Split-config hash matches LF-normalized config bytes. Manifest-byte identity remains unverified because her original manifest file is absent and the local regenerated manifest hash differs.
- Audited CSV/JSON artifacts only; no joblib model loading and no fitting. The 72-group saved-result verifier passes with Tylie's files. Eight NN validation summaries remain author-reported.

## Attribution

Tylie receives experiment reproduction/evaluation credit for RF. The shared RF runner remains Russell's implementation. Lester receives NN implementation/evaluation and method-report credit; his existing original source remains byte-identical, with separate integration utilities credited to Russell. Alexander's GB and Russell's Linear/Ridge implementation/results retain their authored commit evidence.

This repeat uses seed 42 and the same saved feature input hashes. It is cross-platform reproducibility evidence, not multi-seed variance estimation. No scores, rows, settings, cohort, recommendation or holdout were changed to improve results.

## Package verification

The refreshed no-fitting audit discovers 30 tests: 25 passed and five fit-dependent tests were skipped. All 30 source mirrors remain byte-identical, including Lester's original NN source. All 18 config/requirements/comparison/selection/diagnostic mirrors match their sources. Local Markdown links resolve and packaged report prose matches the canonical source after reversing relative-link adjustments.

The Google tracker now includes the four-member Contribution Matrix, corrected 40-model comparison rows, 72 recomputed/eight author-reported boundary, and 30-source count. Native values/validation were re-read; an exported workbook was rendered for visual checks because browser access was unavailable. The editable Figma presentation and its 18 presenter-note blocks were updated and changed slides visually checked.

The local PPTX retains 18 slides, six editable charts and three native tables; slides 14 and 18 remain hidden and the PDF has 16 visible slides. Original chart XML, relationship and embedded-workbook parts were preserved byte-for-byte after the importer's workbook omission was detected. Package, geometry, font, table/chart ownership and first-party import checks passed. PowerPoint opened and exported the local deck successfully.

The report Markdown, editable DOCX and PDF were refreshed. The packaged DOCX renderer could not run because LibreOffice is absent; native Word conversion stalled and its task-owned helper was stopped. The report PDF was instead typeset directly from the same canonical Markdown with ReportLab and rendered through Poppler for visual inspection. The editable DOCX content was checked, but native Word pagination is not certified. No complete pinned-environment/model retraining or final team sign-off is claimed.

The parent-folder CS422_Final_Project_Tracker.xlsx is an older three-tab workbook (Master checklist, Figure plan, Discussion log), distinct from the seven-tab live tracker updated here. Its contents were inspected and left unchanged; the current matrix is the linked Google Sheet.
