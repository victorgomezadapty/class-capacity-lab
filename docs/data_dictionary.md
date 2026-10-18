# Data dictionary

Canonical source: `autores refieren/fitness_class_2212.csv`, 1,500 booking records with unique booking IDs. The Parquet is a normalized, reordered version: all seven shared fields match as a multiset after normalization. The root CSV is a 15-row Parquet preview. These files are not independent datasets. The notebook is an external analytical reference, not a data source to execute or combine.

| Field | Source type | Meaning | Processing and product use |
| --- | --- | --- | --- |
| booking_id | int64 | Unique reservation identifier | 1,500 unique IDs. Not a member or session identifier. |
| months_as_member | int64 | Membership tenure in months | Retained; operational candidate. Not a unique member identifier. |
| weight | float64 | Member weight in kg, per source description | 20 nulls retained. Excluded from dashboard and core operational inputs. |
| days_before | string | Days between booking and class, per source description | 25 values with a ` days` suffix normalized to integers; observed range 1–29. No same-day observations. Exact timestamps unavailable. |
| day_of_week | string | Scheduled weekday | Monday → Mon, Wednesday → Wed, Fri. → Fri (71 rows). Not a class date. |
| time | string | Class time period | AM / PM; no exact clock time. |
| category | string | Class discipline | HIIT, Strength, Cycling, Yoga, Aqua. `-` becomes Unknown only in processed data. |
| attended | int64 | Recorded attendance outcome | 1 = attended; 0 = did not attend, consistent with the reconciled Parquet Yes/No labels. 0 does not independently identify cancellation or no-show. |
| tenure_band | derived | Descriptive tenure bands | 1–6, 7–12, 13–24, 25–48, 49+ months. Presentation bands, not validated behavioral thresholds. |

Grain: one booking record. No member ID, session ID, class date, capacity, cancellation or waitlist data. Category × weekday × AM/PM is a booking cohort, never a reconstructed class session.
