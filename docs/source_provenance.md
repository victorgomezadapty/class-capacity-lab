# Source provenance and publication scope

Checked 13 October 2026.

## Dataset A — GoalZone

Local canonical file: `autores refieren/fitness_class_2212.csv`. All 1,500 records reconcile with the supplied Parquet on the seven shared columns after normalization. The local source hashes are recorded in `data/processed/analysis.json`.

The supplied [Kaggle notebook](https://www.kaggle.com/code/adeforte/goalzone-predicting-gym-attendance) is a reference analysis; [Carla HQ](https://carlahq.eu/datasets/fitness-club) describes DataCamp / Kaggle as origin. Those references do not independently establish the redistribution terms for this precise local CSV. Raw GoalZone data is excluded from the proposed GitHub source package until its exact redistribution rights are confirmed. The notebook accepts user-attached source data.

## Dataset B — Gym Membership

Primary source: [Gym Membership Dataset, Tarek Adam / ka66ledata](https://www.kaggle.com/datasets/ka66ledata/gym-membership-dataset).

The primary data card was inspected in a rendered browser on 13 October 2026. It identifies the dataset as simulated/mock gym membership data intended for EDA practice and lists **CC0: Public Domain**. The 17-field schema, 1,000 IDs, group participation counts (503 true, 497 false), subscription counts, weekly-frequency distribution and displayed record sample correspond to the local CSV. A full remote download and byte-hash identity comparison were not performed.

This source is **synthetic**. It has no verified real-gym collection period and cannot validate real member behavior, timetable competition or incremental cross-sell effects. Weak associations may reflect the artificial generation process; the precise generation code and mechanism were not established.

The source discovery trail includes a [2025 research paper](https://ejournal.unama.ac.id/index.php/mediasisfo/article/download/2090/1565), which cites the original Kaggle URL and the same 17 fields. The publication is a discovery aid, not authority for declaring the data real. Source status is based on the original author's card.

Local file SHA-256: `0d114e1f197226e60b8e59b5b50c3bb2160438cc6d312f51ba53c941f3707d34`.

## Artifact audiences

- Kaggle: self-contained technical notebook, code, reproducible seeds, measures and explicit limitations.
- GitHub: reproducible source, technical README and an explanation of the business question, data grain and method choices.
- Portfolio: the same numerical evidence with visible plain-language interpretation and expandable technical details. Simplifying presentation must not strengthen the claim.

The dashboard is a public-data laboratory artifact, not an Optimo implementation. No real operational data or live capacity recommendation is claimed.
