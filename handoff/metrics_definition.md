# Metrics

| Metric | Definition | Availability |
| --- | --- | --- |
| Booking records | Count of supplied booking rows | Observed |
| Attended bookings | Count where attended = 1 | Observed |
| Attendance rate | Attended bookings / booking records | Observed |
| Non-attendance rate | Count where attended = 0 / booking records | Observed; cancellation / no-show split unknown |
| Cancelled bookings | Distinct bookings with a cancellation event before the session | Unavailable |
| Confirmed no-shows | Active, non-cancelled bookings at session cutoff with no attendance | Unavailable |
| Empty capacity | Session capacity − actual attendees | Unavailable; investigate any negative values as overcapacity |
| Actual occupancy rate | Session attendees / session capacity | Unavailable |
| Expected attendance | Sum of calibrated per-booking attendance probabilities at a stated prediction cutoff | Future concept |
| Expected occupancy rate | Expected attendance / session capacity | Future concept |

For real data, bookings must have a stable ID and an explicit snapshot cutoff. Booked → Cancelled → Attended is a lifecycle view, not an additive funnel: cancelled members may rebook and attendance may include walk-ins. Reconcile the session population before deriving residuals.
