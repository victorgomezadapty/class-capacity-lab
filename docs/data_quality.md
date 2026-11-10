# Data quality

Source rows in the four season files: 2,701,624 (all types). Rows with "Tipo de actividad" = "Actividad dirigida": 731,918.

| Step | Sessions removed | Reason |
|---|---|---|
| Missing date, weekday, time or counts | 0 | |
| Fewer than 5 places offered | 25,179 | Individual or tiny sessions (often 0 or 1 place) are not group classes |
| More booked than offered | 61 | Inconsistent counts |
| Start before 06:00 or after 22:00 | 4 | Implausible times |
| Centre-month with zero bookings in every session | 10,391 (52 centre-months) | Probable reporting gaps rather than real demand |

Analysed: **696,283 sessions**, 73 centres, 928 activity names, 2022-09-01 to 2026-08-31. The log is regenerated in `data/processed/data_quality.json` on every build.

Known issues kept in the data: activity names vary in spelling and casing (for example "Pádel acondicionamiento" and "Padel acondicionamiento"); the family rules group them, but the season-to-season check uses the raw name, so renamed activities lose their history. About 2.7% of sessions fall in the "Other" family.
