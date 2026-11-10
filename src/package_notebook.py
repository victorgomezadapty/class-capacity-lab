"""Build and execute the analysis notebook.

Writes notebooks/class_capacity_madrid.ipynb (executed locally) and
delivery/kaggle/class-capacity-lab.ipynb (same code, prepared for Kaggle with the
attached dataset listed in delivery/kaggle/kernel-metadata.json).
The analysis code is copied verbatim from src/analysis.py so every number matches the site.
"""
from __future__ import annotations

import json
from pathlib import Path

import nbformat as nbf
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = (ROOT / "src" / "analysis.py").read_text(encoding="utf-8")

INTRO = """# Class Capacity Lab: Madrid Group Class Occupancy

**Which group classes fill up, when, and how predictable is it?** Four seasons (September 2022 to August 2026) of directed class sessions from Madrid's municipal sports centres.

**Companion site (EN/ES):** [class-capacity-lab.vercel.app](https://class-capacity-lab.vercel.app) · [discussion](https://class-capacity-lab.vercel.app/evidence) · [source on GitHub](https://github.com/victorgomezadapty/class-capacity-lab)

**Data:** Ayuntamiento de Madrid, *Oferta y ocupación de plazas en actividades deportivas dirigidas*, dataset 300076, [datos.madrid.es](https://datos.madrid.es/dataset/300076-0-deportes-ocupacion), licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). This notebook reads `madrid_class_slots.csv.gz`, an aggregation of the four "Clases abiertas y uso libre" season files built by `src/build_sessions.py` in the repository (directed activities only, quality filters logged). The Ayuntamiento does not endorse this work.

**Kaggle input:** one attached dataset, `vctorandrsgmezlpez/madrid-group-class-sessions-2022-2026`, file `madrid_class_slots.csv.gz`. Internet is not needed.

**Read with care.** "Booked" (*ocupadas*) are places taken by a booking, not people counted in the room. No attendance, cancellations or waitlists are in the source. Nothing here is causal."""

CELLS = [
    ("md", INTRO),
    ("md", "## 1. Load the slot table\n\nOne row per season x month x centre x activity x weekday x start time, with session counts, places offered, places booked, full sessions (every place booked) and empty sessions (zero bookings)."),
    ("code", """from pathlib import Path
import pandas as pd
import numpy as np

def locate(name='madrid_class_slots.csv.gz'):
    kaggle = Path('/kaggle/input')
    if kaggle.exists():
        hits = sorted(kaggle.rglob('madrid_class_slots.csv*'))
    else:
        here = Path.cwd()
        roots = [here, *here.parents]
        hits = [r / 'data' / 'processed' / name for r in roots if (r / 'data' / 'processed' / name).exists()]
    if not hits:
        raise FileNotFoundError('Attach the dataset with madrid_class_slots.csv.gz')
    return hits[0]

path = locate()
t = pd.read_csv(path)
print(path.name, t.shape)
t.head()"""),
    ("md", "## 2. Analysis functions\n\nCopied verbatim from `src/analysis.py`. Centre-level bootstrap (1,000 resamples, seed 20261110), uncorrected Cramér's V from counts, and a session-weighted AUC for the season-to-season check."),
    ("code", ANALYSIS),
    ("code", "res = run(t)\nchecks(res, t)\nprint('Analytical checks passed.')\n{k: res[k] for k in ['overall', 'latest', 'centres', 'activities']}"),
    ("md", "## 3. Seasons, activity families, weekday and time slot"),
    ("code", "res['season']"),
    ("code", "res['family']"),
    ("code", "res['weekday_slot'].pivot(index='slot', columns='weekday', values='full_rate').reindex(index=SLOT_ORDER, columns=WEEKDAY_ORDER).round(3)"),
    ("code", """import matplotlib.pyplot as plt
fig, axes = plt.subplots(1, 2, figsize=(13, 4.2))
hm = res['weekday_slot'].pivot(index='slot', columns='weekday', values='full_rate').reindex(index=SLOT_ORDER, columns=WEEKDAY_ORDER)
im = axes[0].imshow(hm.values, cmap='Greens', vmin=0, vmax=0.45)
axes[0].set_xticks(range(7), WEEKDAY_ORDER); axes[0].set_yticks(range(4), SLOT_ORDER)
for i in range(4):
    for j in range(7):
        axes[0].text(j, i, f"{hm.values[i, j]:.0%}", ha='center', va='center', fontsize=9)
axes[0].set_title('Share of sessions fully booked, all seasons')
f = res['family'].sort_values('full_rate')
axes[1].barh(f['family'], f['full_rate'], color='#1f6f50')
axes[1].set_xlabel('Share of sessions fully booked'); axes[1].set_title('By activity family')
plt.tight_layout(); plt.show()"""),
    ("md", "## 4. Strength of association with being full\n\nUncorrected Cramér's V between each factor and full / not full. With hundreds of thousands of sessions every V is 'significant'; read the size, not a p-value."),
    ("code", "pd.Series(res['cramers_v']).sort_values(ascending=False).round(3)"),
    ("code", "res['centre_spread_latest']"),
    ("md", "## 5. Does last season predict this one?\n\nEach season's sessions are ranked by the previous season's full rate of the same recurring slot (centre, activity, weekday, start time), and by a coarser rule (activity family x weekday x time slot). Only sessions with a matching slot in the previous season are scored."),
    ("code", "pd.DataFrame(res['predictability']).round(3)"),
    ("code", "pd.DataFrame(res['persistence']).round(3)"),
    ("code", "res['calibration']"),
    ("code", "res['bootstrap_latest']"),
    ("code", """cal = res['calibration']
plt.figure(figsize=(6.5, 3.6))
plt.bar(cal['band'], cal['full_rate_now'], color='#1f6f50')
plt.ylim(0, 1); plt.ylabel('Full in 2025-26'); plt.xlabel('Same slot, share full in 2024-25')
plt.title('Last season as a forecast'); plt.show()"""),
    ("md", """## 6. Limits

- Booked places are not attendance. The full-session rate is an upper bound on room use and a lower bound on demand (no waitlists).
- 928 activity names were grouped into 11 families with keyword rules (`src/build_sessions.py`); about 3% fall in Other.
- 52 centre-months with zero bookings in every session were excluded as probable reporting gaps.
- Municipal centres may not resemble private clubs. No causal effects are estimated."""),
]


def build() -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    nb.metadata["kernelspec"] = {"name": "python3", "display_name": "Python 3", "language": "python"}
    nb.metadata["language_info"] = {"name": "python"}
    for kind, src in CELLS:
        nb.cells.append(nbf.v4.new_markdown_cell(src) if kind == "md" else nbf.v4.new_code_cell(src))
    return nb


def main() -> None:
    nb = build()
    NotebookClient(nb, timeout=600, kernel_name="python3", resources={"metadata": {"path": str(ROOT / "notebooks")}}).execute()
    (ROOT / "notebooks").mkdir(exist_ok=True)
    nbf.write(nb, ROOT / "notebooks" / "class_capacity_madrid.ipynb")
    clean = build()  # Kaggle copy without local outputs; Kaggle executes it.
    nbf.write(clean, ROOT / "delivery" / "kaggle" / "class-capacity-lab.ipynb")
    out = [c for c in nb.cells if c.cell_type == "code"]
    print("executed", len(out), "code cells")


if __name__ == "__main__":
    main()
