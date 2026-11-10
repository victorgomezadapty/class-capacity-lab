"""Raw Madrid 300076 session rows to a cleaned, aggregated slot table.

Output: data/processed/madrid_class_slots.csv.gz, one row per
season x month x centre x activity x weekday x start time, with session counts,
places offered, places booked, full sessions and empty sessions. This is the only
input of src/analysis.py, of the notebook and of the Kaggle dataset.
"""
from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "madrid"
OUT = ROOT / "data" / "processed"
KAGGLE = ROOT / "delivery" / "kaggle" / "dataset"
SEASONS = ["2022-23", "2023-24", "2024-25", "2025-26"]
MIN_PLACES = 5

COLS = ["year", "month", "date", "weekday", "start", "end", "activity", "centre",
        "places", "booked", "free", "type", "n_sessions"]

WEEKDAYS = {"lunes": "Mon", "martes": "Tue", "miercoles": "Wed", "jueves": "Thu",
            "viernes": "Fri", "sabado": "Sat", "domingo": "Sun"}

# Ordered rules on the accent-free, lower-case activity name. First match wins.
FAMILIES = [
    ("Aquatic fitness", r"acuatic|aquagym|acuagym|aquarun|water|piscina profunda"),
    ("Swimming", r"natacion|aletas|nado"),
    ("Pilates", r"pilates"),
    ("Mind-body and stretching", r"yoga|cuerpo[ -]?(y )?mente|estiramiento|stre?tching|streching|relaj|tai ?chi|body ?balance|gimnasias? suave|espalda sana"),
    ("Indoor cycling", r"ciclo"),
    ("Cross training and functional", r"cubo ?gym|cross|funcional|suspension|trx|hiit|calistenia|intervalos|circuito|propioceptiv|total training|^core"),
    ("Strength and toning", r"fuerza|musculacion|tonificacion|pump|gap|hipopresivo|abdomen"),
    ("Racket conditioning", r"padel|tenis|pickleball|badminton"),
    ("Outdoor walking and running", r"por madrid|marcha nordica|caminar|correr|atletismo"),
    ("Cardio and dance", r"fitness|aerofit|baile|zumba|combat|boxeo|step|aerobic"),
]


def plain(s: str) -> str:
    s = unicodedata.normalize("NFKD", str(s)).encode("ascii", "ignore").decode()
    return re.sub(r"\s+", " ", s.lower()).strip()


def family(name: str) -> str:
    p = plain(name)
    for fam, rx in FAMILIES:
        if re.search(rx, p):
            return fam
    return "Other"


def slot(hour: int) -> str:
    if hour < 12:
        return "Morning"
    if hour < 15:
        return "Midday"
    if hour < 18:
        return "Afternoon"
    return "Evening"


def load() -> tuple[pd.DataFrame, dict]:
    frames = []
    for s in SEASONS:
        d = pd.read_csv(RAW / f"open_{s}.csv", sep=";", dtype=str, encoding="utf-8").iloc[:, :13]
        d.columns = COLS
        d["season"] = s
        frames.append(d)
    raw = pd.concat(frames, ignore_index=True)
    q = {"raw_rows": int(len(raw))}
    d = raw[raw["type"].str.strip() == "Actividad dirigida"].copy()
    q["directed_rows"] = int(len(d))
    for c in ["places", "booked", "free", "month"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    d["date"] = pd.to_datetime(d["date"], dayfirst=True, errors="coerce")
    d["centre"] = d["centre"].str.strip()
    d["activity"] = d["activity"].str.strip()
    d["weekday"] = d["weekday"].map(lambda x: WEEKDAYS.get(plain(x), None))
    d["hour"] = pd.to_numeric(d["start"].str.split(":").str[0], errors="coerce")
    d["start"] = d["hour"].astype("Int64").astype(str).str.zfill(2) + ":" + d["start"].str.split(":").str[1].str.zfill(2)

    drop = {}
    m = d[["places", "booked", "date", "hour"]].isna().any(axis=1) | d["weekday"].isna()
    drop["missing_fields"] = int(m.sum()); d = d[~m]
    m = d["places"] < MIN_PLACES
    drop["fewer_than_5_places"] = int(m.sum()); d = d[~m]
    m = d["booked"] > d["places"]
    drop["booked_above_places"] = int(m.sum()); d = d[~m]
    m = (d["hour"] < 6) | (d["hour"] > 22)
    drop["start_outside_06_22"] = int(m.sum()); d = d[~m]
    cm = d.groupby(["season", "centre", "month"])["booked"].transform("sum")
    m = cm == 0
    drop["centre_months_with_zero_bookings"] = int(m.sum())
    q["centre_months_with_zero_bookings"] = int(d.loc[m, ["season", "centre", "month"]].drop_duplicates().shape[0])
    d = d[~m]
    q["dropped"] = drop
    q["analysed_sessions"] = int(len(d))
    return d, q


def main() -> None:
    d, q = load()
    d["family"] = d["activity"].map(family)
    d["slot"] = d["hour"].map(slot)
    d["full"] = (d["booked"] >= d["places"]).astype(int)
    d["empty"] = (d["booked"] == 0).astype(int)
    keys = ["season", "month", "centre", "activity", "family", "weekday", "start", "slot"]
    t = (d.groupby(keys, as_index=False)
           .agg(sessions=("places", "size"), places=("places", "sum"), booked=("booked", "sum"),
                full=("full", "sum"), empty=("empty", "sum")))
    t["month"] = t["month"].astype(int)
    t = t.sort_values(keys).reset_index(drop=True)
    OUT.mkdir(parents=True, exist_ok=True)
    t.to_csv(OUT / "madrid_class_slots.csv.gz", index=False, compression={"method": "gzip", "mtime": 0})
    KAGGLE.mkdir(parents=True, exist_ok=True)
    t.to_csv(KAGGLE / "madrid_class_slots.csv.gz", index=False, compression={"method": "gzip", "mtime": 0})
    q["slot_rows"] = int(len(t))
    q["activities"] = int(d["activity"].nunique())
    q["centres"] = int(d["centre"].nunique())
    q["date_min"] = str(d["date"].min().date()); q["date_max"] = str(d["date"].max().date())
    fam = d.groupby("family")["activity"].nunique().to_dict()
    q["activity_names_per_family"] = {k: int(v) for k, v in fam.items()}
    (OUT / "data_quality.json").write_text(json.dumps(q, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(q, indent=2))


if __name__ == "__main__":
    main()
