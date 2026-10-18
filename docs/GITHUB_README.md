# OGDT Class Capacity Lab

**Group Class Capacity & Attendance Intelligence** is an independent research module for the Open Gym Digital Twin maturity path: Observe → Connect → Predict → Simulate → Decide.

The business problem is that a booked place is not necessarily an occupied place. The companion question is how stated member preferences can inform programming hypotheses. This milestone is descriptive EDA; no probability model or capacity automation is implemented.

## Evidence

- GoalZone: 1,500 bookings, 454 attended, attendance rate 30.3%.
- Membership tenure: point-biserial r ≈ 0.486; lead time r ≈ 0.024.
- Lead-time partial correlation after linear tenure adjustment remains near zero.
- AM–PM attendance gap changes from 5.4 to 4.0 percentage points under common tenure weights; the adjusted range includes zero.
- Gym Membership: 1,000 synthetic profiles, 503 reporting group participation, 518 reporting PT use, 258 reporting both.
- Strongest displayed pair lift with n ≥ 10 is only about 1.12 (Pilates / Yoga). The bootstrap range includes 1.

## Method choices

Binary-target numerical associations use point-biserial Pearson correlation. Categorical associations use uncorrected Cramér’s V, not arbitrary numeric category codes. Descriptive uncertainty uses deterministic 1,000-resample percentile bootstrap intervals. Tenure sensitivity uses linear partial correlation and direct standardization over five descriptive tenure strata. Favorite lists form unordered sets, with support/confidence/lift computed at member grain.

No causal effects or adjusted multiple-testing significance claims are reported. V's bootstrap interval is not a test of independence. Unknown categories are retained; raw records are unchanged. Body weight, demographics and trainer names are not central operational inputs.

## Reproduce

Install `requirements.txt` in your own environment. Place authorized source files at the documented local paths, then run:

```text
python src/build_analysis.py
python src/package_research.py
```

Open `dashboard.html` offline. The notebook `notebooks/03_associations_and_tenure.ipynb` is self-contained and resolves attached source CSVs under `/kaggle/input` when run on Kaggle. Local execution looks in the project source folder. Notebook outputs go to `/kaggle/working` or `reports/notebook-output`.

## Repository contents

- `src/`: reproducible data analysis, association functions and dashboard templates.
- `notebooks/`: technical notebook for the two independent populations.
- `docs/`: dictionaries, quality reports, association methods and provenance.
- `handoff/`: metrics, limitations and a concrete local-data pilot request.
- `reports/`: verification evidence.
- `dashboard.html`: portfolio view with numerical evidence, plain-language explanations and expandable methods.

## Source and rights

Gym Membership is synthetic data by Tarek Adam, [Kaggle source](https://www.kaggle.com/datasets/ka66ledata/gym-membership-dataset), licensed CC0. Its generated patterns are not evidence about real gym members. GoalZone is a public educational dataset supplied locally; exact redistribution terms for the raw CSV have not been established. Do not include raw GoalZone files in a public repository until those terms are confirmed. The supplied external Kaggle notebook belongs to its author and is not this project's notebook.

## Next stage

Review Milestone 1, obtain session-level local data, define booking cutoffs and reconcile cancellations, attended bookings, no-shows and walk-ins against session capacity. Then evaluate calibrated attendance probabilities against future sessions. Raw public datasets cannot establish Optimo capacity or timetable effects.
