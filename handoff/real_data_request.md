# Request for a class operations pilot export

## Purpose

Measure how booked demand becomes actual attendance and unused class capacity. Validate the public-data framework against local class operations before training an attendance model or changing booking rules.

## Requested coverage

Start with one branch and a continuous 8–12 week period where possible. This is a practical pilot scope, not a statistical guarantee. Include every scheduled session and every booking status in the period, including cancelled sessions and bookings. Document coverage gaps and system definitions. Longer history may be required for seasonality or prediction.

## 1. Class sessions

One row per session, including empty or cancelled sessions.

| Field | Requirement | Meaning |
| --- | --- | --- |
| class_session_id | Required, stable | Unique scheduled occurrence, not just the class category |
| class_category | Required | Local class taxonomy |
| class_start_timestamp | Required | ISO 8601 with timezone |
| class_end_timestamp | Useful | ISO 8601 with timezone |
| capacity | Required | Places available for that particular session |
| session_status | Required | Scheduled, completed or cancelled |
| branch_id | Required | Facility identifier |
| instructor_id | Useful | Pseudonymous stable identifier |
| capacity_effective_timestamp | Useful | Timestamp of capacity changes, or a separate capacity history |

## 2. Booking lifecycle

Prefer an event export with one row per booking event. If only a final booking table is possible, retain separate booking and cancellation timestamps and explain which transitions are missing.

| Field | Requirement | Meaning |
| --- | --- | --- |
| booking_id | Required, stable | Unique reservation; rebooking must have an identifiable lifecycle |
| class_session_id | Required | Link to the exact scheduled session |
| member_id | Required, pseudonymous | Stable across bookings and visits |
| booking_timestamp | Required | Creation time, with timezone |
| event_timestamp | Required for events | Time of status transition |
| booking_status | Required | Active, cancelled, waitlisted, promoted, attended or confirmed no-show, according to system definitions |
| cancellation_timestamp | Required when cancelled | Do not replace absent timestamps with zero or the class date |
| waitlist_status | Useful | Waiting, promoted, declined or expired |
| membership_start_date | Useful | Derive tenure at the class date, not at export date |

## 3. Verified attendance

One row per member attendance at a session, including walk-ins when they are allowed.

| Field | Requirement | Meaning |
| --- | --- | --- |
| class_session_id | Required | Session identifier |
| member_id | Required, pseudonymous | Same identifier as in bookings |
| attendance_status | Required | Confirmed attended or an explicitly defined attendance outcome |
| attendance_timestamp | Useful | Actual check-in or verification time |
| attendance_method | Useful | Instructor roster, class check-in, turnstile proxy, manual entry, etc. |
| booking_id | Useful | Null for true walk-ins, with a documented reason |

Gym entrance alone should not be interpreted as verified class attendance without validation.

## Required definitions from the operation

Please explain the cancellation cutoff, late-cancellation treatment, session cancellation rules, how no-shows are confirmed, how waitlist promotions work, treatment of walk-ins and repeat bookings, capacity changes, and whether instructor roster edits overwrite event history. Supply timezone and the export snapshot timestamp.

## Initial reconciliation

At an agreed pre-class snapshot, count active bookings and waitlist separately. Track later cancellations and additions. At completion, reconcile verified attendance, active bookings that did not attend and walk-ins. Empty capacity = session capacity − actual attendees; investigate negative values as overcapacity rather than silently clipping them.

“Booked → Cancelled → Attended → Empty capacity” is a lifecycle view. The four quantities are not automatically an additive funnel.

## Data minimization

No names, phone numbers, emails, dates of birth, body weight or payment details are needed. Use stable pseudonymous member and instructor IDs and an approved local workspace. Preference and PT fields are optional later-stage inputs.

## Current status

No real session-level export has been supplied to this lab. This document prepares the request; it does not claim that the export was received, that an external message was sent, or that local operational metrics have been measured.
