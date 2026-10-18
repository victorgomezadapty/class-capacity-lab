# Verification

Prepared 11 October 2026.

## Data checks

- Canonical author-referenced CSV: 1,500 rows, 1,500 unique booking IDs, 454 attendance outcomes equal to 1, 1,046 equal to 0.
- All seven shared fields reconcile with the Parquet as multisets after normalization. Ordering is not required to match; repeated profiles retain their multiplicity.
- The preview CSV matches the first 15 Parquet rows. It is not combined as additional data.
- Required attendance, weekday, AM/PM and lead-time values pass validation.
- Source file SHA-256 values were recorded; all source files remain unchanged.

## Browser checks

Verified both direct offline file opening and the local HTTP preview.

- **168** combinations of category, weekday and time filters compared against counts calculated independently from the original CSV: no mismatches.
- All four schedule views reconcile to the same 1,500-record population after resetting filters.
- Empty cohort: zero records, unavailable attendance rate, no fabricated lead-time points.
- Export check: Aqua / Thu / PM produces seven records and excludes member weight.
- Percentage display uses conventional rounding to one decimal place. Verification accommodates the difference between Python's default ties-to-even formatting and JavaScript's display rounding.
- No JavaScript runtime errors found during the initial browser review.
- Visual review: desktop (1,262px browser width) and mobile (390px). No page-level horizontal overflow. The mobile matrix intentionally scrolls within its keyboard-focusable region.

## Accessibility

axe-core 4.12.1, WCAG 2 A / AA tags: zero detected violations after fixes. One incomplete color-contrast rule remains for SVG text, the logo and offscreen scroll content; these were visually reviewed. The chart text, navigation and matrix use readable dark/pale or light/dark color pairs. This automated check is not a claim of full WCAG conformance.

Scrollable matrices and data regions are keyboard-focusable. Chart points expose text labels and data tables provide an alternative to the SVG.

## Scope limits

No predictions, capacity utilization estimates, cancellation/no-show split, causal inference, overbooking simulation or Optimo-specific validation. The illustrative 82% probability is labeled as hypothetical. The collection period is unknown.
