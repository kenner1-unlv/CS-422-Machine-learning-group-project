# Contribution evidence matrix

The final submission includes contributions from all four members in their assigned model areas. The matrix credits each observable contribution and the reused shared implementation. Assignment alone is not used as coding evidence. No hours, equal-effort, rehearsal or individual AI-use claims are inferred.

| Member | Assigned model | Completed work and authored evidence | Verification |
|---|---|---|---|
| Russell Kennedy | Linear / Ridge | Implementation and evaluation; shared preprocessing, comparison, EDA and packaging. [commit 9e27aaa](https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/commit/9e27aaad33e7e919549dc5f67c4fc7dfc047ae0b) | Saved rows, selections and metrics checked |
| Alexander Aquiningoc | Gradient Boosting | Implementation, validation search, evaluation and method report. [commit 77a3edb](https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/commit/77a3edb045078099cc2627ba6ccbb0598bab9c3a) | Saved rows, selections and metrics checked; hybrid separate |
| Tylie Anderson | Random Forest | Mac reproduction and evaluation using the shared RF runner; models, predictions and summaries. [commit bd92250](https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/commit/bd9225064552899174a278a658eaceef7568a489) | 81,744 rows; keys/targets match; max prediction delta 8.53e-14; rounded scores unchanged |
| Lester Iwuajoku | Neural Network | Implementation, eight test-prediction exports, aggregate validation/test scores and method documentation. [commit 4ac9f59](https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/commit/4ac9f596901f9b93a0e1f23b7464cddf90d33ce8); [commit 8e4e763](https://github.com/kenner1-unlv/CS-422-Machine-learning-group-project/commit/8e4e763c52a277e6544b76b0462860eed58bbfc6) | 15,720 test rows checked; validation summaries author-reported |

Russell introduced the shared RF runner and integrated the submitted artifacts. Tylie reproduced and evaluated the assigned RF experiment using that runner. Lester authored the primary NN implementation and later documentation; importing, checking and packaging his outputs are separate integration work.

All four use the primary 393-county chronological protocol: 6,681 training rows (65.38%), 1,572 validation rows (15.38%), and 1,965 test rows (19.23%) per cutoff. Standard-model rankings and the validation-supported recommendation are unchanged by the RF reproduction. The discussion and supplied disclosures are incorporated in the final report. The final Figma deck includes discussion slide 14 and excludes editing slide 18; the speaking plan is accepted. Original NN software versions remain an explicit unavailable-record limitation.
