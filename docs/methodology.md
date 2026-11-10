# Methodology

1. **Population.** Directed class sessions ("Actividad dirigida") with at least 5 places, after the exclusions in `docs/data_quality.md`.
2. **Outcomes.** Occupancy (booked / offered places, places-weighted) and full (every place booked). Booked is not attendance.
3. **Descriptive rates** by season, activity family, weekday, time slot, month and centre.
4. **Association size.** Uncorrected Cramér's V between each factor and full / not full, computed from counts. With this sample size every association is statistically detectable, so only the size is reported.
5. **Uncertainty.** Sessions of one centre are not independent, so headline intervals come from 1,000 bootstrap resamples of centres (seed 20261110), percentile 95% intervals.
6. **Season-to-season predictability.** For each pair of consecutive seasons, each test-season session is scored by the previous season's full rate of the same recurring slot (centre, activity, weekday, start time) and, as a coarser comparison, of the same family x weekday x time slot. The session-weighted AUC (ties counted as 0.5) measures ranking; a banded table measures calibration. Only sessions with a matching slot are scored; coverage is reported.
7. **Persistence.** Session-weighted Pearson correlation of slot occupancy across consecutive seasons.

No model is fitted; no causal effect is estimated.
