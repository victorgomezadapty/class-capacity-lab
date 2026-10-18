"""Generate technical notebook, statistical report and GitHub-facing README."""
from pathlib import Path
import json

ROOT=Path(__file__).resolve().parents[1]

def md(text):return {'cell_type':'markdown','metadata':{},'source':text.splitlines(keepends=True)}
def code(text):return {'cell_type':'code','execution_count':None,'metadata':{},'outputs':[],'source':text.splitlines(keepends=True)}

def package_research():
    p=json.loads((ROOT/'data/processed/associations.json').read_text(encoding='utf-8'))
    (ROOT/'notebooks').mkdir(exist_ok=True)
    sources='''from pathlib import Path
import pandas as pd
import numpy as np

# On Kaggle, attach both source datasets. Locally, run from the project folder.
def locate(filename):
    kaggle = Path('/kaggle/input')
    if kaggle.exists():
        candidates = list(kaggle.rglob(filename))
    else:
        start = Path.cwd()
        project = start.parent if start.name == 'notebooks' else start
        canonical = project / 'autores refieren' / ('data set/' + filename if filename == 'gym_membership.csv' else filename)
        candidates = [canonical] if canonical.exists() else []
    if len(candidates) != 1:
        raise RuntimeError(f'Expected one {filename}; found {len(candidates)}. Set the source path explicitly.')
    return candidates[0]

A_PATH = locate('fitness_class_2212.csv')
B_PATH = locate('gym_membership.csv')
raw_a = pd.read_csv(A_PATH)
raw_b = pd.read_csv(B_PATH)
a = raw_a.copy()
a['days_before'] = a.days_before.astype(str).str.extract(r'^(\\d+)(?: days)?$')[0].astype(int)
a['day_of_week'] = a.day_of_week.replace({'Monday':'Mon','Wednesday':'Wed','Fri.':'Fri'})
a['category'] = a.category.replace({'-':'Unknown'})
assert a.booking_id.is_unique and raw_b.id.is_unique
assert set(a.attended) == {0,1}
assert len(a) == 1500 and int(a.attended.sum()) == 454
assert len(raw_b) == 1000 and int(raw_b.attend_group_lesson.sum()) == 503
assert int(raw_b.personal_training.sum()) == 518
print({'GoalZone_rows':len(a),'Membership_rows':len(raw_b),'Attendance_rate':a.attended.mean()})
'''
    module=(ROOT/'src/associations.py').read_text(encoding='utf-8').split("\nif __name__=='__main__':")[0]
    module=module.replace('ROOT=Path(__file__).resolve().parents[1]','ROOT=Path.cwd()')
    run='''OUTPUT_ROOT = Path('/kaggle/working') if Path('/kaggle/working').exists() else Path.cwd() / 'reports' / 'notebook-output'
result = build_associations(a=a, b=raw_b, output_root=OUTPUT_ROOT)
effects = pd.DataFrame(result['attendance'] + result['membership'])
effects[['label','method','value','ci','n','valid_resamples']]
'''
    cells=[md('''# Group Class Capacity & Attendance Intelligence

## Technical EDA: effect sizes, uncertainty and tenure sensitivity

Dataset A: GoalZone booking-level outcomes. Dataset B: synthetic Gym Membership member profiles. The populations are independent and are never joined. No predictive model is trained.

Membership source: [Tarek Adam / Kaggle](https://www.kaggle.com/datasets/ka66ledata/gym-membership-dataset), synthetic, CC0. GoalZone's exact redistribution terms are not established here: attach an authorized source copy instead of republishing raw records.

Question: which operational variables are associated with attendance, and how much do descriptive schedule comparisons change under a common membership-tenure mix?
'''),md('## 1. Locate sources and validate the analysis population\n\nRaw files are never overwritten. GoalZone lead-time strings and weekday labels are normalized explicitly.'),code(sources),
      md('## 2. Operational numeric correlation matrix\n\nPearson against a binary outcome is point-biserial correlation. Ordinal numeric coding is not used for class categories or weekdays.'),
      code("a[['months_as_member','days_before','attended']].corr()"),
      md('''## 3. Statistical functions and reproducible resampling

Point-biserial Pearson r and uncorrected Cramér’s V. 1,000 percentile bootstrap resamples; deterministic seed family 20261013. No p-value or corrected multiple-comparison significance claim.

Uncorrected V has finite-sample upward bias. Its bootstrap lower bound can remain above zero under independence and is not a significance test. Row-level resampling assumes independence; repeated GoalZone members cannot be identified. Synthetic member data supports methodological demonstration, not real-gym generalization.
'''),code(module),code(run),
      md('''## 4. Membership-tenure sensitivity

Partial Pearson residualizes lead time and binary attendance on an intercept and continuous tenure. Schedule standardization uses five tenure strata and the full GoalZone tenure weights. Cell-resampled intervals hold those weights fixed. Intervals are withheld if any group × tenure cell has fewer than five records; this is a reporting guard, not a universal minimum.
'''),code("print('Partial lead-time correlation:', result['partial_lead_time'])\nprint('AM–PM gap:', result['am_pm_difference'])\npd.DataFrame(result['standardized_rates'])"),
      md('''## 5. Exploratory favorite-class association

Pilates / Yoga is a displayed example selected during pair exploration. Support, confidence and lift use the 503 group participants. Lift 1.12 does not mean 12% more attendance or revenue. The interval is not adjusted for pair selection and contains the independence reference of 1.
'''),code("result['pair_example']"),
      md('''## 6. Verification and handoff

AM–PM standardized gap must reconcile with the separately standardized group rates. Weights must sum to 1. Synthetic pairs must reconcile with source preference sets. No claims are made about actual capacity, cancellations or Optimo.
'''),code("weights = [x['weight'] for x in result['tenure_weights']]\nassert np.isclose(sum(weights), 1)\nrates = {x['group']:x['standardized'] for x in result['standardized_rates'] if x['dimension']=='time'}\nassert np.isclose(rates['AM'] - rates['PM'], result['am_pm_difference']['standardized'])\nassert result['pair_example']['pair_n'] == 19\nassert np.isclose(result['pair_example']['value'], 19*503/(95*90))\nassert result['partial_lead_time']['valid_resamples'] == 1000\nprint('Analytical consistency checks passed.')"),
      md('''## Interpretation and next stage

Tenure has the clearest unadjusted linear association among the tested operational inputs. Lead-time correlation remains near zero after a linear tenure adjustment. The raw category ranking changes under common tenure weights. The adjusted AM–PM gap has a range that includes zero. Synthetic member preference relationships are weak and cannot establish real programming effects.

Before modeling: review this EDA; request local session IDs, capacity, chronological booking/cancellation events and verified attendance; define prediction and booking snapshot cutoffs; then evaluate calibrated probabilities on future sessions. No overbooking recommendation is made.
''')]
    notebook={'cells':cells,'metadata':{'kernelspec':{'display_name':'Python 3','language':'python','name':'python3'},'language_info':{'name':'python','version':'3.12'}},'nbformat':4,'nbformat_minor':5}
    for i,c in enumerate(cells):c['id']=f'capacity-eda-{i:02d}'
    (ROOT/'notebooks/03_associations_and_tenure.ipynb').write_text(json.dumps(notebook,indent=2,ensure_ascii=False),encoding='utf-8')
    report='# Association analysis and tenure sensitivity\n\nPrepared 13 October 2026. No predictive model is trained.\n\n'
    report+='| Relationship | Measure | Estimate | Descriptive 95% range | n |\n| --- | --- | --- | --- | --- |\n'
    for e in p['attendance']+p['membership']:
        report+=f"| {e['label']} | {e['metric']} | {e['value']:.3f} | {e['ci'][0]:.3f} to {e['ci'][1]:.3f} | {e['n']} |\n"
    report+='\n## Interpretations\n\n'+'\n\n'.join(f"### {e['label']}\n\n{e['meaning']}\n\nOperational implication: {e['decision']}" for e in p['attendance']+p['membership'])
    partial=p['partial_lead_time'];diff=p['am_pm_difference'];pair=p['pair_example']
    report+=f"\n\n## Adjusted findings\n\nLead time, linear adjustment for tenure: partial r = {partial['value']:.3f}, interval {partial['ci'][0]:.3f} to {partial['ci'][1]:.3f}.\n\nAM–PM observed gap = {diff['observed']*100:.1f} percentage points; standardized gap = {diff['standardized']*100:.1f}; range {diff['ci'][0]*100:.1f} to {diff['ci'][1]*100:.1f}.\n\nPilates / Yoga lift = {pair['value']:.2f}, range {pair['ci'][0]:.2f} to {pair['ci'][1]:.2f}, pair n = 19.\n\n"
    report+='## Limitations\n\n'+'\n'.join('- '+v for v in p['limitations'])
    (ROOT/'docs/association_analysis.md').write_text(report+'\n',encoding='utf-8')
    (ROOT/'docs/GITHUB_README.md').write_text('''# OGDT Class Capacity Lab

**Group Class Capacity & Attendance Intelligence** is an independent research module for the Open Gym Digital Twin maturity path: Observe → Connect → Predict → Simulate → Decide.

The business problem is that a booked place is not necessarily an occupied place. The companion question is how stated member preferences can inform programming hypotheses. This milestone is descriptive EDA; no probability model or capacity automation is implemented.

## Evidence

- GoalZone: 1,500 bookings, 454 attended, attendance rate 30.3%.
- Membership tenure: point-biserial r ≈ 0.486; lead time r ≈ 0.024.
- Lead-time partial correlation after linear tenure adjustment remains near zero.
- AM–PM attendance gap changes from 5.4 to 4.0 percentage points under common tenure weights; the adjusted range includes zero.
- Gym Membership: 1,000 synthetic profiles, 503 reporting group participation, 518 reporting PT use, 258 reporting both.
- Strongest displayed pair lift with n ≥ 10 is only about 1.12 (Pilates / Yoga). The bootstrap range includes 1.

## Method choices

Binary-target numerical associations use point-biserial Pearson correlation. Categorical associations use uncorrected Cramér’s V, not arbitrary numeric category codes. Descriptive uncertainty uses deterministic 1,000-resample percentile bootstrap intervals. Tenure sensitivity uses linear partial correlation and direct standardization over five descriptive tenure strata. Favorite lists form unordered sets, with support/confidence/lift computed at member grain.

No causal effects or adjusted multiple-testing significance claims are reported. V's bootstrap interval is not a test of independence. Unknown categories are retained; raw records are unchanged. Body weight, demographics and trainer names are not central operational inputs.

## Reproduce

Install `requirements.txt` in your own environment. Place authorized source files at the documented local paths, then run:

```text
python src/build_analysis.py
python src/package_research.py
```

Open `dashboard.html` offline. The notebook `notebooks/03_associations_and_tenure.ipynb` is self-contained and resolves attached source CSVs under `/kaggle/input` when run on Kaggle. Local execution looks in the project source folder. Notebook outputs go to `/kaggle/working` or `reports/notebook-output`.

## Repository contents

- `src/`: reproducible data analysis, association functions and dashboard templates.
- `notebooks/`: technical notebook for the two independent populations.
- `docs/`: dictionaries, quality reports, association methods and provenance.
- `handoff/`: metrics, limitations and a concrete local-data pilot request.
- `reports/`: verification evidence.
- `dashboard.html`: portfolio view with numerical evidence, plain-language explanations and expandable methods.

## Source and rights

Gym Membership is synthetic data by Tarek Adam, [Kaggle source](https://www.kaggle.com/datasets/ka66ledata/gym-membership-dataset), licensed CC0. Its generated patterns are not evidence about real gym members. GoalZone is a public educational dataset supplied locally; exact redistribution terms for the raw CSV have not been established. Do not include raw GoalZone files in a public repository until those terms are confirmed. The supplied external Kaggle notebook belongs to its author and is not this project's notebook.

## Next stage

Review Milestone 1, obtain session-level local data, define booking cutoffs and reconcile cancellations, attended bookings, no-shows and walk-ins against session capacity. Then evaluate calibrated attendance probabilities against future sessions. Raw public datasets cannot establish Optimo capacity or timetable effects.
''',encoding='utf-8')
    (ROOT/'docs/PORTFOLIO_CASE_STUDY.md').write_text('''# From class bookings to capacity intelligence

I built a research lab that separates booked demand from realized attendance, and pairs that analysis with a demonstration of member preference patterns.

## What I built

An offline interactive dashboard with two independent datasets, cohort filters, attendance patterns, favorite-class combinations, transparent usage profiles and association rules. Each statistical result includes the numerical measure, a plain-language interpretation, an operational implication and a technical method.

## What the evidence changed

GoalZone recorded only 454 attended bookings out of 1,500. Membership tenure carried the clearest association with attendance. Booking lead time alone had a near-zero linear correlation. Adjusting schedule comparisons for tenure reduced the AM–PM gap and changed the category ranking, illustrating why raw percentages need context.

The second dataset is synthetic. It demonstrates techniques for exploring participation and shared class interests, while explicitly separating those techniques from claims about real gym behavior.

## Technical skills demonstrated

Source reconciliation, data cleaning, set-based preference analysis, point-biserial correlation, categorical effect sizes, bootstrap uncertainty, direct standardization, linear partial correlation, reproducible notebooks, accessible interactive visualization and operational data contracts.

## Decision boundary

The lab identifies questions to test. It does not measure Optimo occupancy, predict individual attendance, prove causal effects or recommend automatic overbooking. The next milestone requires actual session capacity, chronological booking/cancellation events and verified attendance.
''',encoding='utf-8')
    print('Prepared technical notebook, association report, GitHub README and portfolio case study.')

if __name__=='__main__':package_research()
