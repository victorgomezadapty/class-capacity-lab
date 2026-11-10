# Kaggle publication plan (not yet published)

Nothing in this folder has been pushed to Kaggle. The previous notebook version used a source without a clear license and must be replaced, not kept.

## 1. Dataset to create first

| Field | Value |
|---|---|
| Folder | `delivery/kaggle/dataset/` |
| Slug | `vctorandrsgmezlpez/madrid-group-class-sessions-2022-2026` |
| Title | Madrid Group Class Sessions 2022-2026 |
| File | `madrid_class_slots.csv.gz` (202,625 rows, 1.8 MB; built by `src/build_sessions.py`) |
| License | CC BY 4.0, attribution to Ayuntamiento de Madrid, dataset 300076 |

Suggested description: source, license and attribution as in `docs/source_provenance.md`, columns as in `docs/data_dictionary.md`, exclusions as in `docs/data_quality.md`, and the note that "booked" is not attendance.

## 2. Notebook

| Field | Value |
|---|---|
| Folder | `delivery/kaggle/` (`kernel-metadata.json` + `class-capacity-lab.ipynb`) |
| Kernel id | `vctorandrsgmezlpez/class-capacity-lab-group-class-attendance-study` (existing; a new title may change the visible slug) |
| Title | Class Capacity Lab: Madrid Group Class Occupancy (48 characters) |
| Inputs | Exactly one dataset: `vctorandrsgmezlpez/madrid-group-class-sessions-2022-2026`. No other inputs. |
| Internet | Off. GPU off. |

The notebook looks for `madrid_class_slots.csv*` under `/kaggle/input` and runs the code of `src/analysis.py` verbatim. It was executed locally (`notebooks/class_capacity_madrid.ipynb`) and its checks passed. After a Kaggle run, compare the printed `overall`, `latest`, AUC and bootstrap values with `data/processed/results.json`.
