# CS 422 Group 2 — final submission checklist

Team name: **not applicable**. Final formats: report PDF and PDF exported from the selected Figma deck. Files use the `Not_Applicable_` upload prefix. **Not submitted:** no WebCampus receipt has been observed.

## Current status: READY TO UPLOAD — not submitted

Final artifact checks passed. There are no outstanding requests for Lester's original software versions. The only remaining submission actions are the team's WebCampus upload and receipt check.

1. Complete: refreshed and visually inspected the 19-page version 2 report PDF with the discussion and all four disclosure dispositions.
2. Complete: repaired Figma, included slide 14, kept slide 18 hidden, and exported/inspected the native 17-page presentation PDF.
3. Complete artifact verification: 30 exact source mirrors, 18 support mirrors, no broken local links, 51 substantive upload files plus one restore/hash manifest. Final publication target is the branch linked below; GitHub publication is separate from WebCampus submission.

## Decisions and evidence already settled

- [x] Both contribution PRs are merged: [Tylie #18](https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/pull/18) and [Lester #19](https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/pull/19). Original author commits are retained.
- [x] Official NN comparison uses Lester's eight 500-iteration runs. July/August weather-plus-trend test MAE: 23.73 / 22.95. No backup or separate 1,500-iteration check is substituted.
- [x] Tylie's Mac reproduction retains 81,744 identical keys/targets and unchanged rounded RF metrics; maximum prediction difference is 8.53e-14 bu/acre.
- [x] Discussion recorded for November 11, 16 and 18, 2026, mainly in person after class, from Russell's recollection. Do not invent per-date attendance or quantitative trial-NN comparisons.
- [x] Russell's approved Codex CLI/GitHub/Figma disclosure is recorded; Alex's exact Gemini AI Overview statement is recorded; Lester supplied both ChatGPT and convergence-warning paragraphs; Russell confirms Tylie did not use AI.
- [x] Lester's original NN Python/library versions were unrecorded and are unavailable. This is a declared reproducibility limitation, not an unanswered collection task. Do not request them again, invent versions or run a replacement fit. Missing same-run validation rows remain an explicitly stated evidence limitation.
- [x] Current public main `89c882f48b3cbcf872b18d970d34ad95c5dc162d` CI rebuilt inputs and passed all 30 tests using pinned Python 3.13. Local frozen verification passes 72 row-derived metric groups and eight author-reported NN validation summaries. Alex additionally reports Python 3.13.17 matching hashes, passing verifier and 24/24 non-fitting tests; that report is distinct from inspected GitHub CI.
- [x] The repository is public for grader access. Original processed data and frozen outputs are accessible there; original raw source downloads and historical as-of-date weather are not bundled. Public visibility is accepted by Russell; making the repository private is not a required task.
- [x] Speaking plan accepted: each member covers their model; Russell leads shared material/opening and can share the closing. Remaining coordination may occur tomorrow. No completed rehearsal is asserted or required as an additional hand-in artifact.
- [x] Final deck source is [Figma](https://www.figma.com/slides/KwpvYD1aHge2d3QM57WU6U). Slide 14 contains the actual discussion; slide 18 remains an excluded editing checklist. Final target: 17 visible slides.
- [x] Final report and slides are both PDF. Editable DOCX/PPTX remain records, not required uploads. Team name and filename prefix are confirmed.

## Required uploads — instructor PDF pages 3–4

1. `Not_Applicable_Final_Report_v2.pdf`: unified problem/data/methods/results/discussion/contributions/application/limitations/conclusion/references and AI disclosure.
2. Executable Python source as separate `.py.txt` files, organized by model and shared utilities. Restore the original `.py` paths/names to run them; no notebooks.
3. README/instructions plus necessary dependency/version lists, seeds, data access, reproduction commands, saved configs and result tables. Use the upload manifest to restore original paths after removing upload prefixes.
4. `Not_Applicable_Presentation.pdf`: the final Figma export, all four names, discussion slide included and editor checklist excluded. Each member speaks and participates in questions.

One member uploads for the team. Use the team name in filenames; upload required materials separately. No ZIP. The instructor specifies four material groups, not a fixed count of files. A deployment, private repo or particular GitHub PR workflow is not required. The team has authorized a final push after the artifacts pass verification.

## Final checks and actual submission

- [x] Inspect the refreshed report PDF and final Figma PDF for complete text, readable figures/tables, correct NN scores and all four names.
- [x] Confirm all source mirrors and configs/results match, all local links resolve, and the final upload manifest matches the actual bytes.
- [x] Apply final upload prefixes and keep restoration instructions usable; retain public data access.
Final package branch: [submission/final-group2](https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/tree/submission/final-group2). Verify the published branch/commit or PR from GitHub; do not confuse publication with WebCampus submission.
- [ ] The submitting member uploads the required files separately to WebCampus, opens them to check contents and retains the submission receipt. Final submission remains with the user/team.

The team-discussion dates and individual disclosures are reported by the participant/user, not independently reconstructed meeting attendance. Original NN environment metadata remains a declared limitation. The final report and presentation must not imply confirmed convergence.
## Open these final files

- [Final report PDF](Not_Applicable_Final_Report_v2.pdf)
- [Final native Figma PDF](slides/Not_Applicable_Presentation.pdf)
- [Separate upload files](upload/)
- [Upload filename / restore path / SHA-256 manifest](UPLOAD_MANIFEST.tsv)
- [Final verification record](../review/FINAL_PACKET_VERIFICATION.json)

## Alex audit follow-up and version 2

- [x] Documented that standalone uploads omit processed inputs/predictions and require the frozen public repository for reproduction.
- [x] Documented Windows CRLF/macOS LF differences and exact upload-manifest versus normalized text comparison.
- [x] Selected the separately named 19-page version 2 report; version 1 is preserved. All scientific table rows and input hashes remain unchanged.
- [x] Refreshed upload README and byte manifest for the selected report.
- [x] Selected all 52 attachments in the actual Canvas form, including the 52.9 MiB presentation, with no visible rejection. The Submit Assignment button is available. Selection alone does not confirm server upload acceptance or provide a submission receipt; the submitting member must finish and check the receipt.
