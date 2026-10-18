"""Descriptive effect sizes, reproducible uncertainty and tenure sensitivity.

This module performs EDA, not predictive model fitting. NumPy/pandas only.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
SEED=20261013
RESAMPLES=1000

def pearson(x,y):
    x=np.asarray(x,dtype=float);y=np.asarray(y,dtype=float)
    if len(x)<3 or np.std(x)==0 or np.std(y)==0:return np.nan
    return float(np.corrcoef(x,y)[0,1])

def cramers_v(x,y):
    x=np.asarray(x);y=np.asarray(y)
    _,a=np.unique(x,return_inverse=True);_,b=np.unique(y,return_inverse=True)
    rows=int(a.max()+1);cols=int(b.max()+1)
    if min(rows,cols)<2:return np.nan
    o=np.bincount(a*cols+b,minlength=rows*cols).reshape(rows,cols).astype(float)
    e=np.outer(o.sum(axis=1),o.sum(axis=0))/o.sum()
    chi=np.sum(np.divide((o-e)**2,e,out=np.zeros_like(e),where=e>0))
    return float(np.sqrt(chi/(o.sum()*min(rows-1,cols-1))))

def partial_pearson(x,y,z):
    # Linear residualization for descriptive adjustment, not a forecasting model.
    X=np.column_stack([np.ones(len(z)),np.asarray(z,dtype=float)])
    xr=np.asarray(x,dtype=float)-X@np.linalg.lstsq(X,x,rcond=None)[0]
    yr=np.asarray(y,dtype=float)-X@np.linalg.lstsq(X,y,rcond=None)[0]
    return pearson(xr,yr)

def bootstrap(arrays,statistic,seed=SEED):
    arrays=[np.asarray(a) for a in arrays]
    estimate=float(statistic(*arrays));rng=np.random.default_rng(seed)
    values=[]
    for _ in range(RESAMPLES):
        ix=rng.integers(0,len(arrays[0]),len(arrays[0]))
        v=statistic(*(a[ix] for a in arrays))
        if np.isfinite(v):values.append(v)
    lo,hi=np.quantile(values,[.025,.975])
    return {'value':estimate,'ci':[float(lo),float(hi)],'n':len(arrays[0]),'valid_resamples':len(values)}

def effect(frame,x,y,metric,label,meaning,decision,seed):
    method=pearson if metric=='r' else cramers_v
    return {'id':x,'label':label,'metric':metric,**bootstrap([frame[x],frame[y]],method,seed),
            'meaning':meaning,'decision':decision,'method':'Point-biserial Pearson correlation' if metric=='r' else 'Uncorrected Cramér’s V'}

def build_associations(a=None,b=None,output_root=ROOT):
    a=pd.read_csv(ROOT/'data/processed/bookings_clean.csv') if a is None else a.copy()
    b=pd.read_csv(ROOT/'autores refieren/data set/gym_membership.csv') if b is None else b.copy()
    output_root=Path(output_root)
    (output_root/'data/processed').mkdir(parents=True,exist_ok=True)
    b['checkin_band']=pd.to_datetime(b.avg_time_check_in,format='%H:%M:%S').dt.hour.map(lambda h:'Morning' if h<12 else 'Afternoon' if h<17 else 'Evening')
    ae=[
      effect(a,'months_as_member','attended','r','Membership tenure & attendance',
        'Longer-standing members tend to attend more often in this sample. This is the clearest of the operational variables examined.',
        'Include membership tenure when testing attendance estimates. This does not mean longer tenure causes attendance.',SEED),
      effect(a,'days_before','attended','r','Booking lead time & attendance',
        'Bookings made further ahead do not show a clear straight-line increase or decrease in attendance. A value near zero is a weak linear relationship, not a quality score.',
        'Lead time alone is a poor basis for a capacity decision here. Nonlinear patterns remain possible.',SEED+1),
      effect(a,'category','attended','V','Class category & attendance',
        'Attendance differs only slightly across class categories overall. A higher category rate does not automatically justify more places.',
        'Check member composition and actual session demand before changing the programme.',SEED+2),
      effect(a,'day_of_week','attended','V','Weekday & attendance',
        'The overall association between weekday and attendance is small. Some visible rate differences may reflect which members book those days.',
        'Validate repeated class sessions before changing the timetable.',SEED+3),
      effect(a,'time','attended','V','AM/PM & attendance',
        'AM and PM attendance rates are not identical, but the overall association is small.',
        'Compare similar members and sessions before treating time of day as a driver.',SEED+4)
    ]
    be=[
      effect(b,'abonoment_type','attend_group_lesson','V','Membership tier & group participation',
        'Premium and Standard profiles participate at almost the same rate. Membership tier barely separates group participation in this synthetic sample.',
        'Do not design different class programmes solely from this tier comparison.',SEED+5),
      effect(b,'visit_per_week','attend_group_lesson','V','Visit frequency & group participation',
        'Profiles reporting more gym visits are not consistently much more likely to report group participation.',
        'Use actual class booking histories to test frequency-based targeting.',SEED+6),
      effect(b,'personal_training','attend_group_lesson','V','PT use & group participation',
        'PT and group classes overlap, but PT users are not clearly more likely to join group classes in these profiles.',
        'The overlap identifies an audience to investigate; it does not prove a cross-sell effect.',SEED+7),
      effect(b,'checkin_band','attend_group_lesson','V','Usual check-in & group participation',
        'Habitual check-in bands have only a small association with reported group participation.',
        'A usual gym check-in time is not a class booking time or a timetable constraint.',SEED+8)
    ]
    partial=bootstrap([a.days_before,a.attended,a.months_as_member],partial_pearson,SEED+9)
    # Fixed descriptive tenure strata. Standardize each group to the same whole-file mix.
    cut=[0,6,12,24,48,float('inf')];labels=['1–6','7–12','13–24','25–48','49+']
    strata=pd.cut(a.months_as_member,bins=cut,labels=False).to_numpy()
    weights=np.bincount(strata,minlength=5)/len(a)
    standardized=[];stratified=[]
    def standard_rate(ix,selector):
        rates=[]
        for k in range(5):
            mask=(strata[ix]==k)&selector[ix]
            if not mask.any():return np.nan
            rates.append(a.attended.to_numpy()[ix][mask].mean())
        return float(np.dot(weights,rates))
    ix=np.arange(len(a));rng=np.random.default_rng(SEED+10)
    for column,values in [('category',['HIIT','Strength','Cycling','Yoga','Aqua','Unknown']),('time',['AM','PM']),('day_of_week',['Mon','Tue','Wed','Thu','Fri','Sat','Sun'])]:
        for value in values:
            sel=a[column].eq(value).to_numpy();n=int(sel.sum())
            raw=float(a.loc[sel,'attended'].mean());adjusted=standard_rate(ix,sel)
            boot=[]
            if np.isfinite(adjusted):
                pools=[np.where((strata==k)&sel)[0] for k in range(5)]
                for _ in range(RESAMPLES):
                    rates=[a.attended.to_numpy()[rng.choice(p,size=len(p),replace=True)].mean() for p in pools]
                    boot.append(float(np.dot(weights,rates)))
            minimum_cell=min(int(((strata==k)&sel).sum()) for k in range(5))
            interval_supported=minimum_cell>=5
            standardized.append({'dimension':column,'group':value,'n':n,'observed':raw,
                                 'standardized':float(adjusted) if np.isfinite(adjusted) else None,
                                 'ci':[float(v) for v in np.quantile(boot,[.025,.975])] if boot and interval_supported else [None,None],
                                 'minimum_stratum_n':minimum_cell,'interval_supported':interval_supported,
                                 'complete_strata':bool(np.isfinite(adjusted))})
            for k,label in enumerate(labels):
                g=a[(strata==k)&sel];stratified.append({'dimension':column,'group':value,'tenure_band':label,'n':len(g),
                    'attended':int(g.attended.sum()),'rate':float(g.attended.mean()) if len(g) else None})
    # Unadjusted difference and standardized difference, in probability units.
    diff_boot=[];am=a.time.eq('AM').to_numpy();pm=~am
    raw_difference=float(a.loc[am,'attended'].mean()-a.loc[pm,'attended'].mean())
    adjusted_difference=standard_rate(ix,am)-standard_rate(ix,pm)
    pools=[[np.where((strata==k)&mask)[0] for k in range(5)] for mask in [am,pm]]
    y=a.attended.to_numpy()
    for _ in range(RESAMPLES):
        vals=[np.dot(weights,[y[rng.choice(p,len(p),replace=True)].mean() for p in group]) for group in pools]
        diff_boot.append(vals[0]-vals[1])
    # Favorite-pair lift interval at a prespecified displayed example, not a causal effect.
    g=b[b.attend_group_lesson].fav_group_lesson.map(lambda s:[v.strip() for v in s.split(',')])
    py=g.map(lambda f:'Pilates' in f).to_numpy();yy=g.map(lambda f:'Yoga' in f).to_numpy()
    lift=lambda x,y: float(np.mean(x&y)/(np.mean(x)*np.mean(y))) if np.mean(x)*np.mean(y)>0 else np.nan
    pair=bootstrap([py,yy],lift,SEED+11)
    pair.update({'classes':['Pilates','Yoga'],'pair_n':int((py&yy).sum()),'confidence_pilates_yoga':float((py&yy).sum()/py.sum()),
                 'yoga_base_rate':float(yy.mean()),'support':float((py&yy).mean())})
    payload={'analysis_date':'2026-10-13','seed':SEED,'resamples':RESAMPLES,'attendance':ae,'membership':be,
             'partial_lead_time':partial,'tenure_weights':[{'label':l,'weight':float(w)} for l,w in zip(labels,weights)],
             'standardized_rates':standardized,'stratified_rates':stratified,
             'am_pm_difference':{'observed':raw_difference,'standardized':float(adjusted_difference),'ci':[float(v) for v in np.quantile(diff_boot,[.025,.975])]},
             'pair_example':pair,
             'limitations':['Unadjusted associations do not identify causal effects.','Confidence intervals are descriptive percentile bootstrap intervals, not proof of generalization.',
               'Resampling assumes independent rows; GoalZone has no member ID to check repeated-member dependence.',
               'Cramér’s V is uncorrected, nonnegative and upward-biased in finite samples. Its percentile interval can stay above zero even under independence. Do not interpret that as a significance test.',
               'Tenure adjustment uses five coarse descriptive bands; residual confounding and nonlinear effects remain possible.',
               'Standardized intervals hold the observed tenure weights fixed and resample within group × tenure cells. Intervals are withheld if any group × tenure cell has fewer than 5 records; this is a reporting guard, not a universal statistical minimum.',
               'Membership is synthetic. Statistical uncertainty describes that artificial sample, not real gym members.',
               'Association exploration has no adjusted multiple-testing significance claims.']}
    (output_root/'data/processed/associations.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
    pd.DataFrame([{k:v for k,v in e.items() if k not in ['meaning','decision']} for e in ae+be]).to_csv(output_root/'data/processed/association_effect_sizes.csv',index=False)
    pd.DataFrame(standardized).to_csv(output_root/'data/processed/tenure_standardized_rates.csv',index=False)
    pd.DataFrame(stratified).to_csv(output_root/'data/processed/tenure_stratified_rates.csv',index=False)
    return payload

if __name__=='__main__':
    p=build_associations()
    print(json.dumps({'effects':[{k:e[k] for k in ['id','metric','value','ci']} for e in p['attendance']+p['membership']],
                     'partial':p['partial_lead_time'],'am_pm':p['am_pm_difference'],'standardized':p['standardized_rates'],'pair':p['pair_example']},indent=2))
