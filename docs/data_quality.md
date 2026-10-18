# Data quality report

- Source: original author-referenced CSV, 1,500 rows × 8 fields; 1,500 unique booking IDs.
- Target: 1 = 454; 0 = 1046; missing = 0.
- Missing weight: 20. No imputation performed; weight is not used in the dashboard.
- Unknown category (`-`): 13; retained as Unknown.
- Fully identical rows including booking ID: 0. One pair of identical feature/outcome profiles has distinct booking IDs; both reservations are retained.
- Lead-time text normalized: 25 rows. Weekday labels normalized: 71 rows.
- Lead time: integers 1–29 days; no zero-day bookings. Gaps in observed lead times are not filled with invented records.
- Tenure: 1–148 months.
- Valid scheduled weekdays: Mon–Sun. Time labels: AM, PM.
- CSV preview rows: 15. Exact value reconciliation against first Parquet rows: True.
- Notebook: third-party analysis with its own cleaning and modeling choices. Not executed and not merged.
- Parquet reconciliation: all 1,500 records match the original CSV on all seven shared fields after label normalization, retaining multiplicities. Booking IDs were dropped and row order changed in the Parquet.

## Source preservation

All supplied files remain unchanged. SHA-256 hashes and byte sizes are recorded in `data/processed/analysis.json` for reproducibility. No records are excluded from attendance metrics.
