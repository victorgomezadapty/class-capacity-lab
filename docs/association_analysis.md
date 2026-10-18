# Association analysis and tenure sensitivity

Prepared 13 October 2026. No predictive model is trained.

| Relationship | Measure | Estimate | Descriptive 95% range | n |
| --- | --- | --- | --- | --- |
| Membership tenure & attendance | r | 0.486 | 0.452 to 0.525 | 1500 |
| Booking lead time & attendance | r | 0.024 | -0.022 to 0.074 | 1500 |
| Class category & attendance | V | 0.053 | 0.035 to 0.114 | 1500 |
| Weekday & attendance | V | 0.068 | 0.050 to 0.132 | 1500 |
| AM/PM & attendance | V | 0.050 | 0.004 to 0.098 | 1500 |
| Membership tier & group participation | V | 0.004 | 0.001 to 0.070 | 1000 |
| Visit frequency & group participation | V | 0.054 | 0.031 to 0.135 | 1000 |
| PT use & group participation | V | 0.010 | 0.001 to 0.077 | 1000 |
| Usual check-in & group participation | V | 0.041 | 0.012 to 0.111 | 1000 |

## Interpretations

### Membership tenure & attendance

Longer-standing members tend to attend more often in this sample. This is the clearest of the operational variables examined.

Operational implication: Include membership tenure when testing attendance estimates. This does not mean longer tenure causes attendance.

### Booking lead time & attendance

Bookings made further ahead do not show a clear straight-line increase or decrease in attendance. A value near zero is a weak linear relationship, not a quality score.

Operational implication: Lead time alone is a poor basis for a capacity decision here. Nonlinear patterns remain possible.

### Class category & attendance

Attendance differs only slightly across class categories overall. A higher category rate does not automatically justify more places.

Operational implication: Check member composition and actual session demand before changing the programme.

### Weekday & attendance

The overall association between weekday and attendance is small. Some visible rate differences may reflect which members book those days.

Operational implication: Validate repeated class sessions before changing the timetable.

### AM/PM & attendance

AM and PM attendance rates are not identical, but the overall association is small.

Operational implication: Compare similar members and sessions before treating time of day as a driver.

### Membership tier & group participation

Premium and Standard profiles participate at almost the same rate. Membership tier barely separates group participation in this synthetic sample.

Operational implication: Do not design different class programmes solely from this tier comparison.

### Visit frequency & group participation

Profiles reporting more gym visits are not consistently much more likely to report group participation.

Operational implication: Use actual class booking histories to test frequency-based targeting.

### PT use & group participation

PT and group classes overlap, but PT users are not clearly more likely to join group classes in these profiles.

Operational implication: The overlap identifies an audience to investigate; it does not prove a cross-sell effect.

### Usual check-in & group participation

Habitual check-in bands have only a small association with reported group participation.

Operational implication: A usual gym check-in time is not a class booking time or a timetable constraint.

## Adjusted findings

Lead time, linear adjustment for tenure: partial r = 0.026, interval -0.026 to 0.076.

AM–PM observed gap = 5.4 percentage points; standardized gap = 4.0; range -0.6 to 8.5.

Pilates / Yoga lift = 1.12, range 0.71 to 1.53, pair n = 19.

## Limitations

- Unadjusted associations do not identify causal effects.
- Confidence intervals are descriptive percentile bootstrap intervals, not proof of generalization.
- Resampling assumes independent rows; GoalZone has no member ID to check repeated-member dependence.
- Cramér’s V is uncorrected, nonnegative and upward-biased in finite samples. Its percentile interval can stay above zero even under independence. Do not interpret that as a significance test.
- Tenure adjustment uses five coarse descriptive bands; residual confounding and nonlinear effects remain possible.
- Standardized intervals hold the observed tenure weights fixed and resample within group × tenure cells. Intervals are withheld if any group × tenure cell has fewer than 5 records; this is a reporting guard, not a universal statistical minimum.
- Membership is synthetic. Statistical uncertainty describes that artificial sample, not real gym members.
- Association exploration has no adjusted multiple-testing significance claims.
