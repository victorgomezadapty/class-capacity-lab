# Dataset B verification

Completed 12 October 2026. Initial analysis began 11 October 2026.

## Source and analysis

- 1,000 source rows, 1,000 unique IDs, zero duplicate rows.
- Group participation: 503 yes, 497 no. PT participation: 518 yes, 482 no. Both: 258.
- All group participants have favorites; all nonparticipants have blank favorites. These 497 blanks are structural absence, not missing preference lists for participating members.
- Favorite lists contain 1, 2 or 3 classes. Names are whitespace-trimmed and deduplicated per member, preserving source labels.
- Class counts, exact unordered combinations and pairs are calculated separately. A pair can occur in a three-class preference set.
- Member and booking populations are independent. No linkage, pooled rates or unified class taxonomy is inferred.

## Browser checks

- **90** membership / weekly-frequency / check-in-band filter combinations compared with direct calculations from the CSV, in six blocks of 15: no failures.
- **990** class-preference percentages checked across those 90 cohorts.
- Mutually exclusive usage-profile totals reconcile to the selected member count for every cohort.
- Displayed pair counts, support, confidence and lift match independently calculated source rules at minimum counts 1 and 10. A cutoff of 503 produces no pair rules. Invalid cutoff 0 produces a validation message.
- The expected source reference contains all **110** directed pair rules. The dashboard deliberately displays up to 20 ranked rules, not all rows.
- Empty Night cohort shows unavailable rates rather than 0% participation.
- Selected-cohort CSV export tested; direct identifiers, birthdays, supplied age, gender and trainer names are absent.
- Dataset switching shows one panel at a time. Returning to GoalZone preserves its population and attendance metrics.
- GoalZone's **168** original filter combinations, four schedule views, empty cohort and CSV export rechecked after the second tab was added: no failures.
- A 15-cohort block, exports, empty cohorts and tab switching additionally verified at 390px width, with no page-level horizontal overflow.

## Visual and accessibility review

Desktop and mobile reviewed. Wide matrices and detailed tables intentionally scroll within keyboard-focusable regions.

axe-core 4.12.1, WCAG 2 A / AA tags: zero detected violations on the B tab in desktop and mobile views. Color contrast required manual review for the logo and some offscreen scroll content. Dark text on pale table cells and light navigation text on a dark background were reviewed visually. This is not a full WCAG conformance claim.

The browser test session expired during the pause and reopened at about:blank; those attempted checks were discarded. The dashboard was reopened and all final checks above completed against the actual page.

## Interpretation

Participation is a profile-level flag, not a session attendance outcome. Favorite-class associations describe co-preference. The strongest pair lift with at least 10 members is only approximately 1.12 (Pilates / Yoga, 19 members). This is weak exploratory evidence; no causal complementarity, competitive effect or cross-sell uplift is established.

Source provenance, license, sampling, collection period and real-versus-synthetic status remain unverified.
