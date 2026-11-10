# Data dictionary: `madrid_class_slots.csv.gz`

One row per season x month x centre x activity x weekday x start time. Built by `src/build_sessions.py` from the Madrid 300076 "Clases abiertas y uso libre" files, directed activities only.

| Column | Type | Meaning |
|---|---|---|
| season | text | Season, September to August (2022-23 to 2025-26) |
| month | int | Calendar month of the sessions (1 to 12) |
| centre | text | Municipal sports centre ("Centro deportivo"), trimmed |
| activity | text | Activity name as published ("Actividad"), trimmed |
| family | text | One of 11 activity families assigned by keyword rules in `src/build_sessions.py` |
| weekday | text | Mon to Sun, from "Día de la semana" |
| start | text | Start time HH:MM ("Hora inicial") |
| slot | text | Morning (before 12:00), Midday (12:00 to 14:59), Afternoon (15:00 to 17:59), Evening (18:00 on) |
| sessions | int | Number of sessions in the group |
| places | int | Sum of places offered ("Plazas") |
| booked | int | Sum of places booked ("Ocupadas"). Not attendance. |
| full | int | Sessions where booked = places |
| empty | int | Sessions with zero bookings |

Derived metrics: occupancy = booked / places; full rate = full / sessions; empty rate = empty / sessions.
