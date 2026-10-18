# Dataset B — Gym Membership Dataset

## Grain, provenance and separation

One member profile per row; 1,000 unique IDs, 17 original fields. The file was supplied by the user. The primary Kaggle card identifies Tarek Adam as author, CC0: Public Domain as license, and describes simulated/mock data for EDA. Verified 13 October 2026. There is no documented real-world collection period. The schema, row count, outcome counts and displayed sample match the local file; full remote byte identity was not checked. Source: https://www.kaggle.com/datasets/ka66ledata/gym-membership-dataset. Do not describe it as representative of Optimo. It has no booking events, session IDs or capacity.

GoalZone remains Dataset A, at booking grain. Dataset B is not joined to it. Similar class names are not grounds for linking people, aggregating populations or harmonizing categories automatically. `HIT`, `LesMiles` and `Kickboxen` are preserved exactly as supplied.

## Data dictionary

| Source field | Meaning / processing | Product use |
| --- | --- | --- |
| id | Unique profile ID | Source uniqueness check; excluded from dashboard payload |
| gender | Supplied gender category | Not used in operational profiles |
| birthday | Supplied date of birth | Excluded from dashboard and export |
| Age | Supplied age | Not recalculated; snapshot date unknown; excluded |
| abonoment_type | Standard / Premium | Renamed membership in processed operational profiles |
| visit_per_week | Reported weekly visit frequency, 1–5 | Descriptive frequency, not visit logs |
| days_per_week | Comma-separated usual visit weekdays | Split, whitespace trimmed; counts reconcile with visit_per_week |
| attend_group_lesson | Boolean group participation | Member-level report; not a realized attendance event |
| fav_group_lesson | Comma-separated favorite classes | Split, sorted, unique per member. Null for all 497 nonparticipants. All 503 participants have a nonempty list |
| avg_time_check_in | Average check-in clock time | Parsed to minutes; Morning 05:00–11:59, Afternoon 12:00–16:59, Evening 17:00–21:59, Night otherwise |
| avg_time_check_out | Average check-out clock time | Retained only in source, not interpreted as actual visit log |
| avg_time_in_gym | Supplied average time in gym, interpreted as minutes per source naming | Descriptive duration; unit interpretation should be confirmed with creator |
| drink_abo / fav_drink | Drink subscription and favorites | Outside this analysis; conditional missing drink preferences retained |
| personal_training | Boolean PT use | Member-level reported use |
| name_personal_trainer | Trainer name, missing for non-PT members | Excluded from dashboard and exports |
| uses_sauna | Boolean sauna use | Context in transparent usage profiles |

## Methods and denominators

Participation = group participants / all member profiles in the selected cohort. Class preference share = members naming that class / group participants in the selected cohort. Lists are multi-select; percentages can sum above 100%.

Exact combinations are unordered complete preference sets. The combination table lists sets of at least two classes; a pair inside a three-class set is not the same as an exact two-class set. Pair overlap counts include a pair even when the member names a third class.

Membership and check-in preference matrices use participating members within each row as their denominator, with the row n displayed. Frequency comparisons use all members at that frequency. Timing means typical gym check-in, not the time of a booked class or an availability constraint.

Usage profiles are mutually exclusive rules: Group + PT, Group only, PT only, Neither group nor PT. They are not fitted clusters. Duration and sauna use summarize those profiles; neither group nor PT does not mean no gym use.

For pair A → B, support = n(A and B) / group participants; confidence = n(A and B) / n(A); lift = confidence / (n(B) / group participants). Lift > 1 suggests positive co-preference relative to this selected population. It is not causal evidence or conversion probability. The data supports association of two classes, not observed sequence or direction of behavior.

The rules show pairs with at least 10 members by default. The count cutoff is editable and is a display heuristic, not statistical validation. Rankings are exploratory, with no adjusted significance claim. Favorite-list lengths are limited in this file to 1–3 classes, which can itself influence the apparent co-preference relationships. Even high lift can rest on a small number of profiles. Absence of co-selection does not demonstrate scheduling competition.

## Operational implications

Use frequent favorites and shared-interest sets to propose hypotheses about scheduling, bundles and targeted surveys. Check timetable collisions, actual booking demand, attendance and capacity before acting. Compare check-in bands with actual class schedules only when those schedules exist. A cross-sell test needs a measured outcome and comparison group.

The intended business concept is: “Class demand is not only volume. Member preferences reveal which classes compete, complement or cross-sell each other.” In this dashboard it is framed as a hypothesis: preferences identify shared interest; actual competition, complementarity and cross-sell effects require operational validation.

## Next data request

Member IDs linked to chronological gym visits and class bookings; class/session IDs, exact schedule, capacity, attendance and cancellations; timestamped preference capture; PT participation and opt-in offer outcomes. Use separate source contracts and keep public laboratory populations independent.

## Initial findings

### Participation is a member-level measure

503 of 1000 profiles report group-class participation (50.3%). This is not a class attendance or occupancy rate.

Next check: Validate reported participation against local member and session histories.

### Preference ranking is multi-select

BodyPump is named by 112 group participants (22.3%). A member can name multiple classes; shares do not sum to 100%.

Next check: Use stated preferences to frame a demand survey, then compare with bookings.

### PT and group classes overlap

258 profiles report both PT and group classes; 245 group only, 260 PT only and 237 neither. PT users report group participation at 49.8%, compared with 50.8% among non-PT profiles.

Next check: Explore relevant cross-program offers, without assuming a conversion uplift.

### Membership tier barely separates participation

Premium: 247/493 participate in groups (50.1%); Standard: 256/507 (50.5%). These unadjusted proportions are similar.

Next check: Avoid designing a class strategy around membership tier alone.

### Co-preferences need careful interpretation

The largest lift among pair rules with at least 10 members is Pilates → Yoga: lift 1.12, n=19. This is a descriptive association.

Next check: Test shared interest with actual class schedules, attendance and opt-in offers. Do not infer competition from preferences.

## Source quality

{
  "rows": 1000,
  "fields": 17,
  "unique_ids": 1000,
  "duplicate_rows": 0,
  "missing": {
    "id": 0,
    "gender": 0,
    "birthday": 0,
    "Age": 0,
    "abonoment_type": 0,
    "visit_per_week": 0,
    "days_per_week": 0,
    "attend_group_lesson": 0,
    "fav_group_lesson": 497,
    "avg_time_check_in": 0,
    "avg_time_check_out": 0,
    "avg_time_in_gym": 0,
    "drink_abo": 0,
    "fav_drink": 504,
    "personal_training": 0,
    "name_personal_trainer": 482,
    "uses_sauna": 0
  },
  "favorite_consistency": true,
  "day_frequency_mismatches": 0,
  "favorite_count_distribution": {
    "1": 169,
    "2": 168,
    "3": 166
  },
  "checkin_min": "08:00:00",
  "checkin_max": "20:58:00",
  "sha256": "0d114e1f197226e60b8e59b5b50c3bb2160438cc6d312f51ba53c941f3707d34",
  "source": "autores refieren/data set/gym_membership.csv",
  "source_url": "https://www.kaggle.com/datasets/ka66ledata/gym-membership-dataset",
  "author": "Tarek Adam",
  "license": "CC0: Public Domain",
  "is_synthetic": true,
  "verified_on": "2026-10-13",
  "provenance": "Primary Kaggle data card inspected on 2026-10-13. Author describes simulated/mock data. The schema, 1,000-row count, outcome counts and displayed record sample correspond to the local file; full remote byte identity was not tested. No real gym collection period exists."
}
