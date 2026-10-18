"""Build the public, bilingual dashboard in site/ from the local dashboard.html.

The local dashboard embeds GoalZone row-level records. Redistribution terms for that
CSV are unconfirmed, so the public build replaces them with a contingency table of
counts (category x weekday x AM/PM x lead time x tenure band) and disables the
attendance cohort export. Run after `python src/build_analysis.py`.
"""
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / 'dashboard.html'
OUT = ROOT / 'site' / 'dashboard.html'
PUBLIC = ROOT / 'src' / 'public'

# Lower bound of each tenure band used by the dashboard's tenure table.
TENURE_BANDS = [(1, 6), (7, 12), (13, 24), (25, 48), (49, 10**6)]


def band_floor(months):
    for lo, hi in TENURE_BANDS:
        if lo <= months <= hi:
            return lo
    raise ValueError(f'months_as_member out of range: {months}')


def to_cube(records):
    cells = Counter()
    for r in records:
        key = (r['category'], r['day_of_week'], r['time'], r['days_before'], band_floor(r['months_as_member']))
        cells[key + ('n',)] += 1
        cells[key + ('a',)] += int(r['attended'])
    keys = sorted({k[:-1] for k in cells})
    return [{'c': c, 'w': w, 't': t, 'd': d, 'm': m, 'n': cells[(c, w, t, d, m, 'n')], 'a': cells[(c, w, t, d, m, 'a')]}
            for c, w, t, d, m in keys]


def replace_once(html, old, new):
    if html.count(old) != 1:
        raise SystemExit(f'Expected exactly one occurrence of: {old[:80]}')
    return html.replace(old, new)


def main():
    html = SRC.read_text(encoding='utf-8')
    m = re.search(r'(<script id="analysis" type="application/json">)(.*?)(</script>)', html, re.S)
    data = json.loads(m.group(2))
    records = data.pop('records')
    data['cube'] = to_cube(records)
    data['public'] = True
    assert sum(c['n'] for c in data['cube']) == len(records) == data['overall']['n']
    payload = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
    html = html[:m.start(2)] + payload + html[m.end(2):]

    # Expand counts back into unit rows in the browser so the existing analysis code runs unchanged.
    html = replace_once(html, "const DATA=JSON.parse(document.getElementById('analysis').textContent);",
        "const DATA=(d=>{if(d.cube&&!d.records){d.records=d.cube.flatMap(c=>Array.from({length:c.n},(_,i)=>"
        "({months_as_member:c.m,days_before:c.d,day_of_week:c.w,time:c.t,category:c.c,attended:i<c.a?1:0})));}return d;})"
        "(JSON.parse(document.getElementById('analysis').textContent));")
    html = replace_once(html, "if(activeDataset==='membership'){exportMembership();return;}",
        "if(activeDataset==='membership'){exportMembership();return;}"
        "if(DATA.public){$('status').textContent='Row-level booking export is disabled in the public build. Aggregated tables are in the GitHub repository.';return;}")

    # Site chrome: back link, language switch, metadata.
    html = replace_once(html, '<span>RESEARCH LAB / GROUP CLASS OPERATIONS</span>',
        '<span class="site-nav"><a href="index.html" data-keep-lang>← Case study</a> · <a href="evidence.html" data-keep-lang>Evidence &amp; discussion</a></span>')
    html = replace_once(html, '<button class="btn" id="print">Print / Save PDF</button>',
        '<button class="btn" id="print">Print / Save PDF</button>'
        '<span class="lang-switch" data-no-i18n role="group" aria-label="Language">'
        '<button type="button" class="btn" data-set-lang="en" aria-pressed="true">EN</button>'
        '<button type="button" class="btn" data-set-lang="es" aria-pressed="false">ES</button></span>')
    head_extra = (PUBLIC / 'dashboard_head.html').read_text(encoding='utf-8')
    html = replace_once(html, '</head>', head_extra + '</head>')
    es = json.loads((PUBLIC / 'dashboard_es.json').read_text(encoding='utf-8'))
    i18n = ('<script id="i18n-es" type="application/json">' + json.dumps(es, ensure_ascii=False).replace('</', '<\\/') + '</script>'
            '<script>' + (PUBLIC / 'dashboard_i18n.js').read_text(encoding='utf-8') + '</script>')
    html = html[:html.rindex('</body>')] + i18n + html[html.rindex('</body>'):]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding='utf-8')
    print(json.dumps({'rows_replaced': len(records), 'cube_cells': len(data['cube']),
                      'singleton_cells': sum(c['n'] == 1 for c in data['cube']), 'es_entries': len(es['strings']),
                      'bytes': OUT.stat().st_size}))


if __name__ == '__main__':
    main()
