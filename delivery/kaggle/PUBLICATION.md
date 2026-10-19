# Kaggle publication record

**Notebook:** [Class Capacity Lab: Group Class Attendance EDA](https://www.kaggle.com/code/vctorandrsgmezlpez/class-capacity-lab-group-class-attendance-eda), public, version 1, pushed 2026-10-18 with `kaggle kernels push -p delivery/kaggle`. Kaggle status: `COMPLETE`.

**Source notebook:** `notebooks/03_associations_and_tenure.ipynb`. The published copy (`delivery/kaggle/class-capacity-lab.ipynb`) adds links to the companion site and repository in the first cell and names the attached GoalZone input. Code cells are unchanged. Internet is disabled; no GPU.

## Attached inputs (not redistributed by this project)

| File | Kaggle dataset | Check against local source |
|---|---|---|
| `fitness_class_2212.csv` | [ddosad/datacamps-data-science-associate-certification](https://www.kaggle.com/datasets/ddosad/datacamps-data-science-associate-certification) | 48.04 kB vs 48,039 bytes locally; same first rows; 1,500 records |
| `gym_membership.csv` | [ka66ledata/gym-membership-dataset](https://www.kaggle.com/datasets/ka66ledata/gym-membership-dataset) (synthetic, CC0) | 115.41 kB vs 115,405 bytes locally |

GoalZone redistribution terms remain unconfirmed, so this project attaches an existing public Kaggle copy rather than uploading the CSV.

## Verification of the Kaggle run

- The notebook's own assertions printed `Analytical consistency checks passed.`
- Outputs downloaded with `kaggle kernels output` were compared with `reports/notebook-output/data/processed/`:
  - `tenure_standardized_rates.csv` and `tenure_stratified_rates.csv`: identical values.
  - `association_effect_sizes.csv`: maximum numeric difference 8.9e-16 (floating-point representation only).
- Key values on Kaggle: tenure r = 0.4855, lead time r = 0.0241, Cramér's V for category / weekday / AM-PM = 0.0529 / 0.0681 / 0.0498, Pilates → Yoga lift = 1.1178, tenure-standardized AM–PM gap = 0.0402.

To republish after changes, regenerate the notebook (`python src/package_research.py`), copy it to this folder with the same first-cell links, then run `kaggle kernels push -p delivery/kaggle`. Each push creates a new Kaggle version.
