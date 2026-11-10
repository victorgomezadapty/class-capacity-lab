"""Run the analysis and write every public artefact: result tables, site data,
and the three HTML pages filled from templates in src/templates/.

Usage: python src/build_site.py   (after src/build_sessions.py)
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import analysis as A  # noqa: E402

PROC = ROOT / "data" / "processed"
SITE = ROOT / "site"
TPL = ROOT / "src" / "templates"

FAM_ES = {
    "Racket conditioning": "Acondicionamiento de raqueta", "Pilates": "Pilates", "Indoor cycling": "Ciclo indoor",
    "Strength and toning": "Fuerza y tonificación", "Cardio and dance": "Cardio y baile",
    "Aquatic fitness": "Fitness acuático", "Mind-body and stretching": "Cuerpo-mente y estiramientos",
    "Cross training and functional": "Cross training y funcional", "Other": "Otras", "Swimming": "Natación",
    "Outdoor walking and running": "Caminar y correr al aire libre",
}


def pct(x, d=1, lang="en"):
    s = f"{100 * x:.{d}f}"
    return (s.replace(".", ",") if lang == "es" else s) + "%"


def num(x, d=2, lang="en"):
    s = f"{x:.{d}f}"
    return s.replace(".", ",") if lang == "es" else s


def thou(n, lang="en"):
    s = f"{int(n):,}"
    return s.replace(",", ".") if lang == "es" else s


def tokens(r: dict) -> dict:
    o, L, b = r["overall"], r["latest"], r["bootstrap_latest"]
    seas = r["season"].set_index("season")
    ws = r["weekday_slot"].set_index(["weekday", "slot"])
    fam = r["family"].set_index("family")
    pr = r["predictability"]
    last = pr[-1]
    cs = r["centre_spread_latest"]
    v = r["cramers_v"]
    cal = r["calibration"].set_index("band")
    T = {}
    for lang in ("en", "es"):
        P = lambda x, d=1: pct(x, d, lang)
        N = lambda x, d=2: num(x, d, lang)
        K = lambda x: thou(x, lang)
        t = {
            "sessions": K(o["sessions"]), "places": K(o["places"]), "booked": K(o["booked"]),
            "centres": K(r["centres"]), "activities": K(r["activities"]),
            "occ": P(o["occupancy"]), "full": P(o["full_rate"]), "empty": P(o["empty_rate"]),
            "l_sessions": K(L["sessions"]), "l_occ": P(L["occupancy"]), "l_full": P(L["full_rate"]), "l_empty": P(L["empty_rate"]),
            "l_full_lo": P(b["full_rate"][0]), "l_full_hi": P(b["full_rate"][1]),
            "l_occ_lo": P(b["occupancy"][0]), "l_occ_hi": P(b["occupancy"][1]),
            "full_first": P(seas.loc["2022-23", "full_rate"]), "full_last": P(seas.loc["2025-26", "full_rate"]),
            "occ_first": P(seas.loc["2022-23", "occupancy"]), "occ_last": P(seas.loc["2025-26", "occupancy"]),
            "mon_eve": P(ws.loc[("Mon", "Evening"), "full_rate"]), "tue_eve": P(ws.loc[("Tue", "Evening"), "full_rate"]),
            "fri_eve": P(ws.loc[("Fri", "Evening"), "full_rate"]),
            "sat_aft": P(ws.loc[("Sat", "Afternoon"), "full_rate"]), "sun_aft": P(ws.loc[("Sun", "Afternoon"), "full_rate"]),
            "racket": P(fam.loc["Racket conditioning", "full_rate"]), "pilates": P(fam.loc["Pilates", "full_rate"]),
            "cycling": P(fam.loc["Indoor cycling", "full_rate"]), "swimming": P(fam.loc["Swimming", "full_rate"]),
            "outdoor": P(fam.loc["Outdoor walking and running", "full_rate"]),
            "cross_empty": P(fam.loc["Cross training and functional", "empty_rate"]),
            "pilates_empty": P(fam.loc["Pilates", "empty_rate"]),
            "auc": N(last["auc_same_slot"]), "auc_lo": N(b["auc_same_slot"][0]), "auc_hi": N(b["auc_same_slot"][1]),
            "auc_fam": N(last["auc_family_weekday_slot"]), "auc_fam_lo": N(b["auc_family_weekday_slot"][0]),
            "auc_fam_hi": N(b["auc_family_weekday_slot"][1]),
            "auc_min": N(min(p["auc_same_slot"] for p in pr)), "auc_max": N(max(p["auc_same_slot"] for p in pr)),
            "coverage": P(last["coverage"], 0), "cov_min": P(min(p["coverage"] for p in pr), 0), "cov_max": P(max(p["coverage"] for p in pr), 0),
            "covered": K(last["covered_sessions"]),
            "pers_min": N(min(p["r"] for p in r["persistence"])), "pers_max": N(max(p["r"] for p in r["persistence"])),
            "cs_n": K(cs["centres"]), "cs_min": P(cs["min"]), "cs_p10": P(cs["p10"]), "cs_med": P(cs["median"]),
            "cs_p90": P(cs["p90"]), "cs_max": P(cs["max"]),
            "v_activity": N(v["activity"]), "v_family": N(v["family"]), "v_centre": N(v["centre"]),
            "v_slot": N(v["slot"]), "v_weekday": N(v["weekday"]), "v_month": N(v["month"]), "v_season": N(v["season"]),
            "cal0": P(cal.loc["0%", "full_rate_now"]), "cal4": P(cal.loc["76-100%", "full_rate_now"]),
            "nboot": K(b["n_boot"]), "clusters": K(b["clusters"]),
        }
        T[lang] = t
    return T


def site_data(r: dict, t: pd.DataFrame) -> dict:
    cube = (t.groupby(["season", "family", "weekday", "slot"], as_index=False)
              [["sessions", "places", "booked", "full", "empty"]].sum())
    month = t.groupby(["season", "family", "month"], as_index=False)[["sessions", "places", "booked", "full", "empty"]].sum()
    latest = t[t["season"] == A.SEASONS[-1]]
    cen = A.by(latest, "centre")
    cen = cen[cen["sessions"] >= 500].sort_values("full_rate", ascending=False)
    return {
        "seasons": A.SEASONS, "weekdays": A.WEEKDAY_ORDER, "slots": A.SLOT_ORDER, "months": A.MONTH_ORDER,
        "families": list(r["family"]["family"]), "family_es": FAM_ES,
        "cols": ["sessions", "places", "booked", "full", "empty"],
        "cube": cube[["season", "family", "weekday", "slot", "sessions", "places", "booked", "full", "empty"]].values.tolist(),
        "month": month[["season", "family", "month", "sessions", "places", "booked", "full", "empty"]].values.tolist(),
        "centres_latest": cen[["centre", "sessions", "occupancy", "full_rate", "empty_rate"]].round(4).values.tolist(),
        "calibration": r["calibration"].round(4).to_dict("records"),
        "predictability": r["predictability"], "persistence": r["persistence"],
        "bootstrap_latest": r["bootstrap_latest"], "cramers_v": r["cramers_v"],
        "overall": r["overall"], "latest": r["latest"],
    }


def fill(template: str, T: dict) -> str:
    def rep(m):
        lang, key = m.group(1), m.group(2)
        if lang == "bi":
            return f'<span data-l="en">{T["en"][key]}</span><span data-l="es">{T["es"][key]}</span>'
        return T[lang][key]
    out = re.sub(r"\{\{(en|es|bi):([a-z0-9_]+)\}\}", rep, template)
    assert "{{" not in out, "unfilled token"
    return out


def main() -> None:
    t = pd.read_csv(PROC / "madrid_class_slots.csv.gz")
    r = A.run(t)
    A.checks(r, t)
    for k in ["season", "family", "weekday", "slot", "month", "weekday_slot", "family_slot", "calibration"]:
        r[k].to_csv(PROC / f"{k}.csv", index=False, float_format="%.6f")
    scal = {k: v for k, v in r.items() if not isinstance(v, pd.DataFrame)}
    (PROC / "results.json").write_text(json.dumps(scal, indent=2) + "\n", encoding="utf-8")
    data = site_data(r, t)
    (SITE / "assets" / "data.js").write_text(
        "// Generated by src/build_site.py from Madrid 300076 (CC BY 4.0). Aggregates only.\n"
        "window.CCL = " + json.dumps(data, separators=(",", ":"), ensure_ascii=False) + ";\n", encoding="utf-8")
    T = tokens(r)
    (PROC / "site_tokens.json").write_text(json.dumps(T, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    for name in ["index.html", "dashboard.html", "evidence.html"]:
        src = TPL / name
        if src.exists():
            (SITE / name).write_text(fill(src.read_text(encoding="utf-8"), T), encoding="utf-8")
    print(json.dumps(T["en"], indent=1))


if __name__ == "__main__":
    main()
