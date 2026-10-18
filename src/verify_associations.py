"""Check statistical definitions, source invariants and notebook execution."""
from pathlib import Path
import json,hashlib,ast,io
from contextlib import redirect_stdout
import numpy as np
from associations import pearson,cramers_v,partial_pearson

ROOT=Path(__file__).resolve().parents[1]
assert np.isclose(pearson([0,0,1,1],[0,0,1,1]),1)
assert np.isclose(pearson([0,0,1,1],[1,1,0,0]),-1)
assert np.isclose(cramers_v(['a','a','b','b'],[0,1,0,1]),0)
assert np.isclose(cramers_v(['a','a','b','b'],[0,0,1,1]),1)
p=json.loads((ROOT/'data/processed/associations.json').read_text(encoding='utf-8'))
assert np.isclose(p['attendance'][0]['value'],0.48552622327526257)
assert np.isclose(p['attendance'][1]['value'],0.02406815573312008)
assert np.isclose(p['pair_example']['value'],19*503/(95*90))
assert p['pair_example']['ci'][0]<1<p['pair_example']['ci'][1]
assert p['am_pm_difference']['ci'][0]<0<p['am_pm_difference']['ci'][1]
rates={r['group']:r['standardized'] for r in p['standardized_rates'] if r['dimension']=='time'}
assert np.isclose(rates['AM']-rates['PM'],p['am_pm_difference']['standardized'])
assert len(p['standardized_rates'])==15
assert all(r['ci']==[None,None] for r in p['standardized_rates'] if r['minimum_stratum_n']<5)
a=json.loads((ROOT/'data/processed/analysis.json').read_text(encoding='utf-8'))
b=json.loads((ROOT/'data/processed/membership_analysis.json').read_text(encoding='utf-8'))
assert all(hashlib.sha256((ROOT/k).read_bytes()).hexdigest()==v['sha256'] for k,v in a['quality']['source_files'].items())
assert hashlib.sha256((ROOT/b['quality']['source']).read_bytes()).hexdigest()==b['quality']['sha256']
assert b['quality']['is_synthetic'] is True
assert b['quality']['license']=='CC0: Public Domain'
nb=json.loads((ROOT/'notebooks/03_associations_and_tenure.ipynb').read_text(encoding='utf-8'))
scope={'__name__':'notebook_verification'}
execution_count=0
for i,cell in enumerate(nb['cells']):
    if cell['cell_type']=='code':
        execution_count+=1
        parsed=ast.parse(''.join(cell['source']))
        last=parsed.body.pop() if parsed.body and isinstance(parsed.body[-1],ast.Expr) else None
        stream=io.StringIO();value=None
        with redirect_stdout(stream):
            exec(compile(parsed,f'notebook-cell-{i}','exec'),scope)
            if last is not None:value=eval(compile(ast.Expression(last.value),f'notebook-cell-{i}','eval'),scope)
        outputs=[]
        if stream.getvalue():outputs.append({'output_type':'stream','name':'stdout','text':stream.getvalue().splitlines(keepends=True)})
        if value is not None:
            data={'text/plain':repr(value).splitlines(keepends=True)}
            if hasattr(value,'to_html'):data['text/html']=value.to_html().splitlines(keepends=True)
            outputs.append({'output_type':'execute_result','execution_count':execution_count,'metadata':{},'data':data})
        cell['execution_count']=execution_count;cell['outputs']=outputs
assert np.isclose(scope['result']['attendance'][0]['value'],p['attendance'][0]['value'])
assert scope['result']['pair_example']['ci']==p['pair_example']['ci']
(ROOT/'notebooks/03_associations_and_tenure.ipynb').write_text(json.dumps(nb,indent=2,ensure_ascii=False),encoding='utf-8')
print('Statistical reference checks, source preservation and all notebook code cells passed.')
