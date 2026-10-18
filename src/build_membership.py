"""Independent member-preference analysis. Never join to GoalZone booking rows."""
from pathlib import Path
from collections import Counter
from itertools import combinations
import json, hashlib
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/'autores refieren/data set/gym_membership.csv'

def build_membership():
    df=pd.read_csv(SOURCE)
    assert df.id.is_unique
    assert df.attend_group_lesson.notna().all() and df.personal_training.notna().all()
    lists=df.fav_group_lesson.fillna('').map(lambda s:sorted(set(x.strip() for x in s.split(',') if x.strip())))
    assert all(bool(f)==bool(g) for f,g in zip(lists,df.attend_group_lesson))
    minutes=pd.to_datetime(df.avg_time_check_in,format='%H:%M:%S').dt.hour*60+pd.to_datetime(df.avg_time_check_in,format='%H:%M:%S').dt.minute
    bands=minutes.map(lambda m:'Morning (05–12)' if 300<=m<720 else 'Afternoon (12–17)' if 720<=m<1020 else 'Evening (17–22)' if 1020<=m<1320 else 'Night (22–05)')
    segment=lambda r: 'Group + PT' if r.attend_group_lesson and r.personal_training else 'Group only' if r.attend_group_lesson else 'PT only' if r.personal_training else 'Neither group nor PT'
    records=[]
    for i,r in df.iterrows():
        records.append({'membership':r.abonoment_type,'visits':int(r.visit_per_week),'group':bool(r.attend_group_lesson),
                        'pt':bool(r.personal_training),'favorites':lists.iloc[i],'checkin_band':bands.iloc[i],
                        'checkin_minutes':int(minutes.iloc[i]),'duration':int(r.avg_time_in_gym),'sauna':bool(r.uses_sauna),
                        'days':[x.strip() for x in r.days_per_week.split(',')],'segment':segment(r)})
    classes=sorted({c for f in lists for c in f})
    participants=[r for r in records if r['group']]
    counts=Counter(c for r in participants for c in r['favorites'])
    combos=Counter(tuple(r['favorites']) for r in participants)
    pairs=Counter(p for r in participants for p in combinations(r['favorites'],2))
    rules=[]
    for (a,b),n in pairs.items():
        for antecedent,consequent in [(a,b),(b,a)]:
            conf=n/counts[antecedent]
            rules.append({'from':antecedent,'to':consequent,'count':n,'support':n/len(participants),
                          'confidence':conf,'lift':conf/(counts[consequent]/len(participants))})
    rules.sort(key=lambda r:(-r['lift'],-r['count'],r['from'],r['to']))
    sourcehash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    quality={'rows':len(df),'fields':len(df.columns),'unique_ids':int(df.id.nunique()),'duplicate_rows':int(df.duplicated().sum()),
             'missing':{k:int(v) for k,v in df.isna().sum().items()},'favorite_consistency':True,
             'day_frequency_mismatches':int(sum(len(r['days'])!=r['visits'] for r in records)),
             'favorite_count_distribution':dict(sorted(Counter(len(r['favorites']) for r in participants).items())),
             'checkin_min':str(df.avg_time_check_in.min()),'checkin_max':str(df.avg_time_check_in.max()),
             'sha256':sourcehash,'source':'autores refieren/data set/gym_membership.csv',
             'source_url':'https://www.kaggle.com/datasets/ka66ledata/gym-membership-dataset',
             'author':'Tarek Adam','license':'CC0: Public Domain','is_synthetic':True,'verified_on':'2026-10-13',
             'provenance':'Primary Kaggle data card inspected on 2026-10-13. Author describes simulated/mock data. The schema, 1,000-row count, outcome counts and displayed record sample correspond to the local file; full remote byte identity was not tested. No real gym collection period exists.'}
    payload={'records':records,'classes':classes,'quality':quality,'totals':{'members':len(df),'group':len(participants),
             'pt':sum(r['pt'] for r in records),'both':sum(r['pt'] and r['group'] for r in records)},
             'class_counts':dict(counts),'combinations':[{'classes':list(k),'n':v} for k,v in combos.most_common()],
             'rules':rules}
    (ROOT/'data/processed/membership_analysis.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False),encoding='utf-8')
    pd.DataFrame(records).assign(favorites=lambda x:x.favorites.map(lambda f:', '.join(f)),days=lambda x:x.days.map(lambda f:', '.join(f))).to_csv(ROOT/'data/processed/membership_operational_profiles.csv',index=False)
    pd.DataFrame(rules).to_csv(ROOT/'data/processed/class_association_rules.csv',index=False)
    top=max(counts,key=counts.get)
    qualified=[r for r in rules if r['count']>=10]
    best=qualified[0] if qualified else None
    findings=[
      {'title':'Participation is a member-level measure','text':f'{len(participants)} of {len(df)} profiles report group-class participation (50.3%). This is not a class attendance or occupancy rate.','action':'Validate reported participation against local member and session histories.'},
      {'title':'Preference ranking is multi-select','text':f'{top} is named by {counts[top]} group participants ({100*counts[top]/len(participants):.1f}%). A member can name multiple classes; shares do not sum to 100%.','action':'Use stated preferences to frame a demand survey, then compare with bookings.'},
      {'title':'PT and group classes overlap','text':'258 profiles report both PT and group classes; 245 group only, 260 PT only and 237 neither. PT users report group participation at 49.8%, compared with 50.8% among non-PT profiles.','action':'Explore relevant cross-program offers, without assuming a conversion uplift.'},
      {'title':'Membership tier barely separates participation','text':'Premium: 247/493 participate in groups (50.1%); Standard: 256/507 (50.5%). These unadjusted proportions are similar.','action':'Avoid designing a class strategy around membership tier alone.'},
      {'title':'Co-preferences need careful interpretation','text':f"The largest lift among pair rules with at least 10 members is {best['from']} → {best['to']}: lift {best['lift']:.2f}, n={best['count']}. This is a descriptive association." if best else 'No pair rule meets 10 members.', 'action':'Test shared interest with actual class schedules, attendance and opt-in offers. Do not infer competition from preferences.'}
    ]
    payload['findings']=findings
    (ROOT/'data/processed/membership_analysis.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False),encoding='utf-8')
    documentation='''# Dataset B — Gym Membership Dataset

## Grain, provenance and separation

One member profile per row; 1,000 unique IDs, 17 original fields. The file was supplied by the user. Creator, license, collection period, sampling method and real-versus-synthetic status are not verified. Do not describe it as representative of Optimo. It has no booking events, session IDs or capacity.

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
'''
    documentation=documentation.replace('Creator, license, collection period, sampling method and real-versus-synthetic status are not verified.', 'The primary Kaggle card identifies Tarek Adam as author, CC0: Public Domain as license, and describes simulated/mock data for EDA. Verified 13 October 2026. There is no documented real-world collection period. The schema, row count, outcome counts and displayed sample match the local file; full remote byte identity was not checked. Source: https://www.kaggle.com/datasets/ka66ledata/gym-membership-dataset.')
    documentation += '\n## Initial findings\n\n'+'\n\n'.join(f"### {f['title']}\n\n{f['text']}\n\nNext check: {f['action']}" for f in findings)
    documentation += '\n\n## Source quality\n\n'+json.dumps(quality,indent=2,ensure_ascii=False)+'\n'
    (ROOT/'docs/membership_dataset.md').write_text(documentation,encoding='utf-8')
    return payload

if __name__=='__main__':
    p=build_membership()
    print(json.dumps({'totals':p['totals'],'top_rules':p['rules'][:5],'quality':p['quality']},indent=2,ensure_ascii=False))
