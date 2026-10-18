from pathlib import Path
import itertools, json
from decimal import Decimal, ROUND_HALF_UP
import pandas as pd

root = Path(__file__).resolve().parents[1]
df = pd.read_csv(root / 'autores refieren/fitness_class_2212.csv')
df.category = df.category.replace({'-':'Unknown'})
df.day_of_week = df.day_of_week.replace({'Monday':'Mon','Wednesday':'Wed','Fri.':'Fri'})
cases = []
for c,d,t in itertools.product(['all','HIIT','Strength','Cycling','Yoga','Aqua','Unknown'],
                             ['all','Mon','Tue','Wed','Thu','Fri','Sat','Sun'],['all','AM','PM']):
    mask = df.attended.notna()
    if c != 'all': mask &= df.category.eq(c)
    if d != 'all': mask &= df.day_of_week.eq(d)
    if t != 'all': mask &= df.time.eq(t)
    g = df[mask]
    cases.append({'category':c,'day':d,'time':t,'n':len(g),'a':int(g.attended.sum()),
                  'rate':str((Decimal(int(g.attended.sum()))*100/Decimal(len(g))).quantize(Decimal('0.1'),rounding=ROUND_HALF_UP))+'%' if len(g) else 'n.a.'})
code = (root/'src/verify_browser.js').read_text(encoding='utf-8').replace('__GOLDEN_CASES__',json.dumps(cases))
(root/'reports/browser-check.js').write_text(code,encoding='utf-8')
print(f'Prepared {len(cases)} independent CSV-derived cohort checks')
