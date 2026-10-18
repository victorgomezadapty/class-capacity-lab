from pathlib import Path
from collections import Counter
from itertools import product,combinations
from decimal import Decimal,ROUND_HALF_UP
import pandas as pd
import json

root=Path(__file__).resolve().parents[1]
d=pd.read_csv(root/'autores refieren/data set/gym_membership.csv')
d['favorites']=d.fav_group_lesson.fillna('').map(lambda s:sorted({c.strip() for c in s.split(',') if c.strip()}))
d['band']=d.avg_time_check_in.map(lambda s:'Morning (05–12)' if 5<=int(s[:2])<12 else 'Afternoon (12–17)' if 12<=int(s[:2])<17 else 'Evening (17–22)' if 17<=int(s[:2])<22 else 'Night (22–05)')
classes=sorted({c for f in d.favorites for c in f})
def rounded(x,n=1):return str(Decimal(x).quantize(Decimal('0.'+'0'*(n-1)+'1'),rounding=ROUND_HALF_UP))
def pct(a,n):return rounded(Decimal(int(a))*100/Decimal(int(n)))+'%' if n else 'n.a.'
cases=[]
for m,v,t in product(['all','Premium','Standard'],['all',1,2,3,4,5],['all','Morning (05–12)','Afternoon (12–17)','Evening (17–22)','Night (22–05)']):
    mask=d.id.notna()
    if m!='all':mask &= d.abonoment_type.eq(m)
    if v!='all':mask &= d.visit_per_week.eq(v)
    if t!='all':mask &= d.band.eq(t)
    g=d[mask];users=g[g.attend_group_lesson];counts=Counter(c for f in users.favorites for c in f)
    cases.append({'membership':m,'visits':v,'time':t,'n':len(g),'both':int((g.attend_group_lesson & g.personal_training).sum()),
                  'groupRate':pct(len(users),len(g)),'ptRate':pct(g.personal_training.sum(),len(g)),
                  'favorites':{c:pct(counts[c],len(users)) for c in classes}})
users=d[d.attend_group_lesson]
counts=Counter(c for f in users.favorites for c in f)
pairs=Counter(p for f in users.favorites for p in combinations(f,2))
rules={}
for (a,b),n in pairs.items():
    for f,t in [(a,b),(b,a)]:
        lift=Decimal(n)*len(users)/(Decimal(counts[f])*counts[t])
        rules[f+'|'+t]=[str(n),pct(n,len(users)),pct(n,counts[f]),rounded(lift,2)]
expected={'cases':cases,'rules':rules}
base=(root/'src/verify_membership.js').read_text(encoding='utf-8')
for chunk in range(6):
    partial={**expected,'cases':cases[chunk*15:(chunk+1)*15]}
    script=base.replace('__MEMBERSHIP_EXPECTED__',json.dumps(partial,ensure_ascii=False))
    (root/f'reports/membership-browser-check-{chunk}.js').write_text(script,encoding='utf-8')
print(f'Prepared {len(cases)} membership cohorts and {len(rules)} directed pair rules')
