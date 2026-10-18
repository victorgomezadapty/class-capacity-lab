# Methodology

This milestone describes historical bookings. No machine learning model is trained.

Attendance rate = attended bookings / all bookings with a valid attendance outcome. Rates use counts, not the average of subgroup percentages. Non-attendance rate = 1 − attendance rate; it is not a verified cancellation or no-show rate.

Dashboard filters select a booking cohort by category, weekday and AM/PM. All KPI values and charts recompute from that cohort. Overall dataset attendance remains available for comparison. Unknown category is retained. Empty cohorts display unavailable rates, never 0%.

Lead-time chart: empirical attendance proportion for each observed lead-time value. Descriptive 95% Wilson binomial intervals show sampling uncertainty. No smoothing, probability model or causal interpretation is used. Intervals assume independent booking outcomes; repeated members cannot be identified, so dependence could invalidate that assumption. Groups with fewer than 30 bookings are flagged for caution; 30 is a display heuristic, not a statistical validity threshold.

Heatmap: category × weekday cohorts, optionally filtered by AM/PM. These cells are not individual sessions. Tenure bands are descriptive. Findings are unadjusted, dataset-wide observations and do not change with the cohort filters.

There are no dates, so the collection period, temporal trends and train/test chronology cannot be established. Results cannot be claimed to describe Optimo.

Expected attendance = sum of calibrated individual probabilities is a future framework concept. Expected occupancy = expected attendance / session capacity requires actual capacity. The displayed 20 bookings, 20 capacity, 16.4 expected attendees is an explicitly hypothetical example using an assumed 82% probability. It is not inferred from this dataset and supports no overbooking recommendation.
