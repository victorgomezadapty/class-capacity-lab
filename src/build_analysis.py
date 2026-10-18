"""Reproduce Milestone 1 from the author-referenced CSV. Never modify source files."""
from pathlib import Path
import sys, json, hashlib, math
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / '.python-deps'))
import pandas as pd

for folder in ['data/processed', 'docs', 'reports/figures', 'handoff']:
    (ROOT / folder).mkdir(parents=True, exist_ok=True)

raw = pd.read_csv(ROOT / 'autores refieren/fitness_class_2212.csv')
parquet = pd.read_parquet(ROOT / 'dataset.parquet')
sample = pd.read_csv(ROOT / 'fitness-club.csv').rename(columns={'attended ★': 'attended'})
df = raw.copy()
df['category'] = df['category'].astype(str).replace({'-': 'Unknown'})
df['days_before'] = df['days_before'].astype(str).str.extract(r'^(\d+)(?: days)?$')[0]
assert df['days_before'].notna().all(), 'Unexpected lead-time encoding'
df['days_before'] = df['days_before'].astype(int)
df['day_of_week'] = df['day_of_week'].replace({'Monday':'Mon','Wednesday':'Wed','Fri.':'Fri'})
assert set(df['attended']) == {0,1}
assert raw.booking_id.is_unique
assert df['attended'].notna().all(), 'Unexpected target label'
assert (df['days_before'] >= 0).all()
assert set(df['day_of_week'].astype(str)) <= {'Mon','Tue','Wed','Thu','Fri','Sat','Sun'}
assert set(df['time'].astype(str)) <= {'AM','PM'}

def summary(frame):
    n = len(frame)
    a = int(frame.attended.sum())
    p = a/n if n else None
    if n:
        z = 1.959963984540054
        den = 1+z*z/n
        mid = (p+z*z/(2*n))/den
        half = z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
        ci = [mid-half, mid+half]
    else:
        ci = [None, None]
    return {'n': n, 'attended': a, 'non_attendance': n-a, 'rate': p, 'ci': ci}

def group(column):
    return [{'label': str(k), **summary(g)} for k,g in df.groupby(column, observed=True, sort=True)]

sample_match = True
for col in sample.columns:
    a = parquet.iloc[:len(sample)][col].astype(str).reset_index(drop=True)
    b = sample[col].astype(str).reset_index(drop=True)
    if col in ['weight', 'months_as_member', 'days_before']:
        same = pd.to_numeric(a).equals(pd.to_numeric(b))
        # Integer / float dtype differences are irrelevant for source reconciliation.
        same = (pd.to_numeric(a).to_numpy() == pd.to_numeric(b).to_numpy()).all()
    else:
        same = a.equals(b)
    sample_match = sample_match and bool(same)

pc = parquet.copy()
pc['attended'] = pc['attended'].astype(str).map({'Yes':1,'No':0})
pc['category'] = pc['category'].astype(str).replace({'-':'Unknown'})
cols = list(parquet.columns)
def row_counter(frame):
    return Counter(tuple('NULL' if pd.isna(v) else str(v) for v in row)
                   for row in frame[cols].itertuples(index=False,name=None))
reconciled = row_counter(df) == row_counter(pc)
assert reconciled, 'Original CSV and Parquet differ after normalization'
manifest = {name: {'sha256': hashlib.sha256((ROOT/name).read_bytes()).hexdigest(),
                   'bytes': (ROOT/name).stat().st_size}
            for name in ['autores refieren/fitness_class_2212.csv','autores refieren/archive.zip','dataset.parquet','fitness-club.csv','kaggle goalzone-predicting-gym-attendance.ipynb']}
quality = {'rows': len(raw), 'columns': len(raw.columns), 'missing': raw.isna().sum().to_dict(),
           'unknown_category': int((df.category == 'Unknown').sum()),
           'identical_rows': int(raw.duplicated().sum()), 'identical_profiles': int(df.drop(columns='booking_id').duplicated().sum()),
           'unique_booking_ids': int(raw.booking_id.nunique()), 'parquet_reconciled': reconciled,
           'lead_time_text_normalized': int(raw.days_before.str.contains('days').sum()),
           'weekday_labels_normalized': int(raw.day_of_week.isin(['Monday','Wednesday','Fri.']).sum()),
           'csv_rows': len(sample),
           'csv_matches_first_rows': sample_match, 'source_files': manifest,
           'days_before_min': int(df.days_before.min()), 'days_before_max': int(df.days_before.max()),
           'tenure_min': int(df.months_as_member.min()), 'tenure_max': int(df.months_as_member.max())}
df['tenure_band'] = pd.cut(df.months_as_member, bins=[0,6,12,24,48,float('inf')],
                           labels=['1–6 months','7–12 months','13–24 months','25–48 months','49+ months'])
overall = summary(df)
groups = {c: group(c) for c in ['category','day_of_week','time','days_before','tenure_band']}
known = [x for x in groups['category'] if x['label'] != 'Unknown']
hi, lo = max(known, key=lambda x:x['rate']), min(known, key=lambda x:x['rate'])
days = groups['day_of_week']
dh,dl = max(days,key=lambda x:x['rate']),min(days,key=lambda x:x['rate'])
times = {x['label']:x for x in groups['time']}
short, long = summary(df[df.days_before <= 7]), summary(df[df.days_before >= 8])
new, established = summary(df[df.months_as_member <= 12]),summary(df[df.months_as_member > 12])
fmt = lambda x:f"{x['rate']*100:.1f}%"
findings = [
    {'title': 'Bookings overstate realized attendance', 'text': f"{overall['attended']:,} of {overall['n']:,} bookings attended ({fmt(overall)}). The remaining {overall['non_attendance']:,} are recorded as non-attendance; cancellation status is unavailable.", 'action':'Track attendance alongside booking volume before discussing capacity changes.'},
    {'title': 'Compare class categories', 'text':f"{hi['label']} has the highest observed rate ({fmt(hi)}, n={hi['n']}); {lo['label']} has the lowest ({fmt(lo)}, n={lo['n']}). This is an unadjusted comparison.", 'action':'Check whether the category differences persist across session schedules and member tenure.'},
    {'title': 'Review the schedule with evidence', 'text':f"{dh['label']} records {fmt(dh)} (n={dh['n']}) versus {fmt(dl)} on {dl['label']} (n={dl['n']}). AM is {fmt(times['AM'])}; PM is {fmt(times['PM'])}.", 'action':'Validate repeated sessions before changing the timetable.'},
    {'title': 'Lead time is a pattern to investigate', 'text':f"Bookings 1–7 days ahead attend at {fmt(short)} (n={short['n']}); bookings 8+ days ahead at {fmt(long)} (n={long['n']}). The file has no same-day bookings.", 'action':'Test confirmation reminders with real booking and cancellation timestamps. Association alone does not establish an effect.'},
    {'title': 'Member tenure adds operational context', 'text':f"Members with up to 12 months of tenure attend at {fmt(new)} (n={new['n']}); those above 12 months at {fmt(established)} (n={established['n']}).", 'action':'Keep tenure as a candidate operational variable, and validate it on local data.'}
]
records = df[['months_as_member','days_before','day_of_week','time','category','attended']].copy()
for c in ['day_of_week','time']:
    records[c] = records[c].astype(str)
payload = {'overall':overall,'groups':groups,'quality':quality,'findings':findings,
           'records':records.to_dict(orient='records'), 'analysis_date':'2026-10-11',
           'sources':[{'label':'Carla HQ dataset reference','url':'https://carlahq.eu/datasets/fitness-club'},
                      {'label':'Kaggle reference notebook','url':'https://www.kaggle.com/code/adeforte/goalzone-predicting-gym-attendance'}]}
(ROOT/'data/processed/analysis.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False),encoding='utf-8')
df.to_csv(ROOT/'data/processed/bookings_clean.csv', index=False)
for c,g in groups.items():
    pd.DataFrame(g).drop(columns='ci').to_csv(ROOT/f'data/processed/attendance_by_{c}.csv',index=False)

dictionary = '''# Data dictionary

Canonical source: `autores refieren/fitness_class_2212.csv`, 1,500 booking records with unique booking IDs. The Parquet is a normalized, reordered version: all seven shared fields match as a multiset after normalization. The root CSV is a 15-row Parquet preview. These files are not independent datasets. The notebook is an external analytical reference, not a data source to execute or combine.

| Field | Source type | Meaning | Processing and product use |
| --- | --- | --- | --- |
| booking_id | int64 | Unique reservation identifier | 1,500 unique IDs. Not a member or session identifier. |
| months_as_member | int64 | Membership tenure in months | Retained; operational candidate. Not a unique member identifier. |
| weight | float64 | Member weight in kg, per source description | 20 nulls retained. Excluded from dashboard and core operational inputs. |
| days_before | string | Days between booking and class, per source description | 25 values with a ` days` suffix normalized to integers; observed range 1–29. No same-day observations. Exact timestamps unavailable. |
| day_of_week | string | Scheduled weekday | Monday → Mon, Wednesday → Wed, Fri. → Fri (71 rows). Not a class date. |
| time | string | Class time period | AM / PM; no exact clock time. |
| category | string | Class discipline | HIIT, Strength, Cycling, Yoga, Aqua. `-` becomes Unknown only in processed data. |
| attended | int64 | Recorded attendance outcome | 1 = attended; 0 = did not attend, consistent with the reconciled Parquet Yes/No labels. 0 does not independently identify cancellation or no-show. |
| tenure_band | derived | Descriptive tenure bands | 1–6, 7–12, 13–24, 25–48, 49+ months. Presentation bands, not validated behavioral thresholds. |

Grain: one booking record. No member ID, session ID, class date, capacity, cancellation or waitlist data. Category × weekday × AM/PM is a booking cohort, never a reconstructed class session.
'''
(ROOT/'docs/data_dictionary.md').write_text(dictionary,encoding='utf-8')
qtext = f'''# Data quality report

- Source: original author-referenced CSV, {len(raw):,} rows × {len(raw.columns)} fields; 1,500 unique booking IDs.
- Target: 1 = {overall['attended']}; 0 = {overall['non_attendance']}; missing = 0.
- Missing weight: 20. No imputation performed; weight is not used in the dashboard.
- Unknown category (`-`): {quality['unknown_category']}; retained as Unknown.
- Fully identical rows including booking ID: {quality['identical_rows']}. One pair of identical feature/outcome profiles has distinct booking IDs; both reservations are retained.
- Lead-time text normalized: {quality['lead_time_text_normalized']} rows. Weekday labels normalized: {quality['weekday_labels_normalized']} rows.
- Lead time: integers {quality['days_before_min']}–{quality['days_before_max']} days; no zero-day bookings. Gaps in observed lead times are not filled with invented records.
- Tenure: {quality['tenure_min']}–{quality['tenure_max']} months.
- Valid scheduled weekdays: Mon–Sun. Time labels: AM, PM.
- CSV preview rows: {len(sample)}. Exact value reconciliation against first Parquet rows: {sample_match}.
- Notebook: third-party analysis with its own cleaning and modeling choices. Not executed and not merged.
- Parquet reconciliation: all 1,500 records match the original CSV on all seven shared fields after label normalization, retaining multiplicities. Booking IDs were dropped and row order changed in the Parquet.

## Source preservation

All supplied files remain unchanged. SHA-256 hashes and byte sizes are recorded in `data/processed/analysis.json` for reproducibility. No records are excluded from attendance metrics.
'''
(ROOT/'docs/data_quality.md').write_text(qtext,encoding='utf-8')
(ROOT/'docs/methodology.md').write_text('''# Methodology

This milestone describes historical bookings. No machine learning model is trained.

Attendance rate = attended bookings / all bookings with a valid attendance outcome. Rates use counts, not the average of subgroup percentages. Non-attendance rate = 1 − attendance rate; it is not a verified cancellation or no-show rate.

Dashboard filters select a booking cohort by category, weekday and AM/PM. All KPI values and charts recompute from that cohort. Overall dataset attendance remains available for comparison. Unknown category is retained. Empty cohorts display unavailable rates, never 0%.

Lead-time chart: empirical attendance proportion for each observed lead-time value. Descriptive 95% Wilson binomial intervals show sampling uncertainty. No smoothing, probability model or causal interpretation is used. Intervals assume independent booking outcomes; repeated members cannot be identified, so dependence could invalidate that assumption. Groups with fewer than 30 bookings are flagged for caution; 30 is a display heuristic, not a statistical validity threshold.

Heatmap: category × weekday cohorts, optionally filtered by AM/PM. These cells are not individual sessions. Tenure bands are descriptive. Findings are unadjusted, dataset-wide observations and do not change with the cohort filters.

There are no dates, so the collection period, temporal trends and train/test chronology cannot be established. Results cannot be claimed to describe Optimo.

Expected attendance = sum of calibrated individual probabilities is a future framework concept. Expected occupancy = expected attendance / session capacity requires actual capacity. The displayed 20 bookings, 20 capacity, 16.4 expected attendees is an explicitly hypothetical example using an assumed 82% probability. It is not inferred from this dataset and supports no overbooking recommendation.
''',encoding='utf-8')
ftext = '# Initial operational findings\n\n'
for i,f in enumerate(findings,1):
    ftext += f"## {i}. {f['title']}\n\n{f['text']}\n\nNext check: {f['action']}\n\n"
ftext += '''## Variables that transfer to another gym

Booking lead time, class category, weekday, time period and membership tenure can usually be derived from operational records. Attendance status must be defined consistently. Historical member attendance would be useful only when actual stable member IDs and chronological records exist.

## Variables that should not become core requirements

Member weight; GoalZone's particular category vocabulary; AM/PM as the only available time resolution; arbitrary tenure bands. A production system should accept the gym's own class taxonomy and actual timestamps.

## Proposed next step

Review this milestone, then obtain a class-level booking and attendance export from Optimo. Link booking events to sessions and record cancellations separately. Measure booked places, cancellations, attendance, no-shows and empty capacity per session. Only after the definitions and event history are validated should calibrated attendance probabilities be evaluated on future sessions.
'''
(ROOT/'handoff/findings.md').write_text(ftext,encoding='utf-8')
(ROOT/'handoff/metrics_definition.md').write_text('''# Metrics

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
''',encoding='utf-8')
(ROOT/'handoff/limitations.md').write_text('''# Limitations

Public laboratory data, not Optimo data. No measured utilization, empty places, cancellations, waitlist pressure, unique members, individual sessions, exact times or collection period. Two identical feature profiles have distinct booking IDs and are retained as separate reservations. The normalized Parquet is reconciled against the original author-referenced CSV. No causal effects, calibrated predictions, capacity recommendations or overbooking simulation are claimed. Weight is excluded from the dashboard. Group sizes and descriptive uncertainty are exposed.
''',encoding='utf-8')
(ROOT/'handoff/data_contract.yaml').write_text('''# Proposed next-stage contract; not implemented in this milestone.
grain: one_booking_event_linked_to_one_class_session
required:
  booking_id: stable_pseudonymous_string
  class_session_id: stable_string
  member_id: stable_pseudonymous_string
  booking_timestamp: ISO8601_with_timezone
  class_timestamp: ISO8601_with_timezone
  capacity: positive_integer_per_session
  attendance_status: [attended, confirmed_no_show, cancelled, pending]
useful:
  cancellation_timestamp: nullable_ISO8601_with_timezone
  class_category: string
  instructor_id: pseudonymous_string
  branch: string
  waitlist_status: string
  membership_start_date: date
policy:
  body_weight_required: false
  prediction_cutoff: must_be_explicit_before_session
  session_capacity_changes: retain_timestamped_history
''',encoding='utf-8')

template = (ROOT/'src/dashboard.template.html').read_text(encoding='utf-8')
html = template.replace('__ANALYSIS_JSON__',json.dumps(payload,ensure_ascii=False).replace('</','<\\/'))
from build_membership import build_membership
membership_payload = build_membership()
html = html.replace('__MEMBERSHIP_PANEL__',(ROOT/'src/membership.panel.html').read_text(encoding='utf-8'))
html = html.replace('__MEMBERSHIP_SCRIPT__','<script>'+ (ROOT/'src/membership.js').read_text(encoding='utf-8') + '</script>')
html = html.replace('__MEMBERSHIP_JSON__',json.dumps(membership_payload,ensure_ascii=False).replace('</','<\\/'))
from associations import build_associations
association_payload=build_associations()
html=html.replace('</main>',(ROOT/'src/association.panels.html').read_text(encoding='utf-8')+'</main>',1)
html=html.replace('__ASSOCIATIONS_JSON__',json.dumps(association_payload,ensure_ascii=False,allow_nan=False).replace('</','<\\/'))
html=html.replace('</body>','<script>'+(ROOT/'src/association.js').read_text(encoding='utf-8')+'</script></body>')
(ROOT/'dashboard.html').write_text(html,encoding='utf-8')
print(json.dumps({'overall':overall,'quality':quality,'findings':findings},indent=2,ensure_ascii=False))
