# Initial operational findings

## 1. Bookings overstate realized attendance

454 of 1,500 bookings attended (30.3%). The remaining 1,046 are recorded as non-attendance; cancellation status is unavailable.

Next check: Track attendance alongside booking volume before discussing capacity changes.

## 2. Compare class categories

Aqua has the highest observed rate (32.9%, n=76); Strength has the lowest (26.6%, n=233). This is an unadjusted comparison.

Next check: Check whether the category differences persist across session schedules and member tenure.

## 3. Review the schedule with evidence

Sun records 33.3% (n=213) versus 20.7% on Wed (n=116). AM is 31.6%; PM is 26.2%.

Next check: Validate repeated sessions before changing the timetable.

## 4. Lead time is a pattern to investigate

Bookings 1–7 days ahead attend at 28.0% (n=542); bookings 8+ days ahead at 31.5% (n=958). The file has no same-day bookings.

Next check: Test confirmation reminders with real booking and cancellation timestamps. Association alone does not establish an effect.

## 5. Member tenure adds operational context

Members with up to 12 months of tenure attend at 11.2% (n=779); those above 12 months at 50.9% (n=721).

Next check: Keep tenure as a candidate operational variable, and validate it on local data.

## Variables that transfer to another gym

Booking lead time, class category, weekday, time period and membership tenure can usually be derived from operational records. Attendance status must be defined consistently. Historical member attendance would be useful only when actual stable member IDs and chronological records exist.

## Variables that should not become core requirements

Member weight; GoalZone's particular category vocabulary; AM/PM as the only available time resolution; arbitrary tenure bands. A production system should accept the gym's own class taxonomy and actual timestamps.

## Proposed next step

Review this milestone, then obtain a class-level booking and attendance export from Optimo. Link booking events to sessions and record cancellations separately. Measure booked places, cancellations, attendance, no-shows and empty capacity per session. Only after the definitions and event history are validated should calibrated attendance probabilities be evaluated on future sessions.
