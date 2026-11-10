"""Analysis of Madrid group class sessions. Input: the slot table built by
src/build_sessions.py. The same code runs in the Kaggle notebook.

Outcomes per session: occupancy = booked places / offered places, and
full = every offered place was booked. Booked is not attended: the source counts
places taken ("ocupadas"), not people who showed up.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

SEED = 20261110
N_BOOT = 1000
WEEKDAY_ORDER = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
SLOT_ORDER = ["Morning", "Midday", "Afternoon", "Evening"]
SEASONS = ["2022-23", "2023-24", "2024-25", "2025-26"]
MONTH_ORDER = [9, 10, 11, 12, 1, 2, 3, 4, 5, 6, 7, 8]
KEY = ["centre", "activity", "weekday", "start"]


def summarize(g: pd.DataFrame) -> pd.Series:
    s = g["sessions"].sum()
    return pd.Series({
        "sessions": int(s),
        "places": int(g["places"].sum()),
        "booked": int(g["booked"].sum()),
        "occupancy": g["booked"].sum() / g["places"].sum(),
        "full_rate": g["full"].sum() / s,
        "empty_rate": g["empty"].sum() / s,
    })


def by(t: pd.DataFrame, cols, order=None) -> pd.DataFrame:
    r = t.groupby(cols).apply(summarize, include_groups=False).reset_index()
    for c in ["sessions", "places", "booked"]:
        r[c] = r[c].astype(int)
    if order is not None and isinstance(cols, str):
        r[cols] = pd.Categorical(r[cols], order, ordered=True)
        r = r.sort_values(cols).reset_index(drop=True)
        r[cols] = r[cols].astype(str)
    return r


def cramers_v(t: pd.DataFrame, col: str) -> float:
    """Uncorrected Cramér's V between a factor and full / not full, from counts."""
    g = t.groupby(col)[["full", "sessions"]].sum()
    obs = np.column_stack([g["full"], g["sessions"] - g["full"]]).astype(float)
    exp = obs.sum(1, keepdims=True) * obs.sum(0, keepdims=True) / obs.sum()
    chi2 = ((obs - exp) ** 2 / exp).sum()
    k = min(obs.shape) - 1
    return float(np.sqrt(chi2 / (obs.sum() * k)))


def weighted_auc(score: np.ndarray, pos: np.ndarray, neg: np.ndarray) -> float:
    """AUC when each row carries pos full sessions and neg not-full sessions with one score. Ties count 0.5."""
    df = pd.DataFrame({"s": score, "p": pos, "n": neg}).groupby("s")[["p", "n"]].sum().sort_index()
    p, n = df["p"].to_numpy(float), df["n"].to_numpy(float)
    neg_below = np.cumsum(n) - n
    return float(((p * (neg_below + 0.5 * n)).sum()) / (p.sum() * n.sum()))


def history_scores(t: pd.DataFrame, train: str, test: str) -> pd.DataFrame:
    """Score each test-season recurring slot by its full rate in the previous season."""
    h = t[t["season"] == train]
    cur = t[t["season"] == test].groupby(KEY + ["family", "slot"], as_index=False)[["sessions", "full"]].sum()
    slot_hist = h.groupby(KEY)[["sessions", "full"]].sum()
    slot_hist = (slot_hist["full"] / slot_hist["sessions"]).rename("prev_slot")
    fam_hist = h.groupby(["family", "weekday", "slot"])[["sessions", "full"]].sum()
    fam_hist = (fam_hist["full"] / fam_hist["sessions"]).rename("prev_family")
    cur = cur.join(slot_hist, on=KEY).join(fam_hist, on=["family", "weekday", "slot"])
    return cur


def predictability(t: pd.DataFrame, train: str, test: str) -> dict:
    cur = history_scores(t, train, test)
    seen = cur.dropna(subset=["prev_slot", "prev_family"])
    pos, neg = seen["full"].to_numpy(), (seen["sessions"] - seen["full"]).to_numpy()
    return {
        "train": train, "test": test,
        "test_sessions": int(cur["sessions"].sum()),
        "covered_sessions": int(seen["sessions"].sum()),
        "coverage": float(seen["sessions"].sum() / cur["sessions"].sum()),
        "auc_same_slot": weighted_auc(seen["prev_slot"].to_numpy(), pos, neg),
        "auc_family_weekday_slot": weighted_auc(seen["prev_family"].to_numpy(), pos, neg),
        "full_rate_covered": float(seen["full"].sum() / seen["sessions"].sum()),
    }


def calibration(t: pd.DataFrame, train: str, test: str) -> pd.DataFrame:
    cur = history_scores(t, train, test).dropna(subset=["prev_slot"])
    bins = [-0.001, 0.0, 0.25, 0.5, 0.75, 1.0]
    labels = ["0%", "1-25%", "26-50%", "51-75%", "76-100%"]
    cur["band"] = pd.cut(cur["prev_slot"], bins=bins, labels=labels)
    r = cur.groupby("band", observed=False).agg(sessions=("sessions", "sum"), full=("full", "sum")).reset_index()
    r["full_rate_now"] = r["full"] / r["sessions"]
    r["band"] = r["band"].astype(str)
    return r


def cluster_bootstrap(t: pd.DataFrame, train: str, test: str, n_boot: int = N_BOOT) -> dict:
    """Resample centres (not sessions) because sessions of one centre are not independent."""
    cur = history_scores(t, train, test).dropna(subset=["prev_slot", "prev_family"])
    test_t = t[t["season"] == test]
    centres = np.array(sorted(test_t["centre"].unique()))
    per_c = test_t.groupby("centre")[["sessions", "full", "places", "booked"]].sum().reindex(centres)
    groups = {c: g for c, g in cur.groupby("centre")}
    rng = np.random.default_rng(SEED)
    full_rate, occ, auc_slot, auc_fam = [], [], [], []
    for _ in range(n_boot):
        pick = rng.choice(centres, size=len(centres), replace=True)
        s = per_c.loc[pick].sum()
        full_rate.append(s["full"] / s["sessions"]); occ.append(s["booked"] / s["places"])
        g = pd.concat([groups[c] for c in pick if c in groups], ignore_index=True)
        pos, neg = g["full"].to_numpy(), (g["sessions"] - g["full"]).to_numpy()
        auc_slot.append(weighted_auc(g["prev_slot"].to_numpy(), pos, neg))
        auc_fam.append(weighted_auc(g["prev_family"].to_numpy(), pos, neg))
    ci = lambda x: [float(np.percentile(x, 2.5)), float(np.percentile(x, 97.5))]
    return {"n_boot": n_boot, "clusters": int(len(centres)), "full_rate": ci(full_rate), "occupancy": ci(occ),
            "auc_same_slot": ci(auc_slot), "auc_family_weekday_slot": ci(auc_fam)}


def slot_persistence(t: pd.DataFrame, train: str, test: str) -> float:
    """Session-weighted correlation of a recurring slot's occupancy across two seasons."""
    a = t[t["season"] == train].groupby(KEY)[["booked", "places", "sessions"]].sum()
    b = t[t["season"] == test].groupby(KEY)[["booked", "places", "sessions"]].sum()
    j = a.join(b, lsuffix="_a", rsuffix="_b", how="inner")
    x, y, w = j["booked_a"] / j["places_a"], j["booked_b"] / j["places_b"], j["sessions_b"]
    mx, my = np.average(x, weights=w), np.average(y, weights=w)
    cov = np.average((x - mx) * (y - my), weights=w)
    return float(cov / np.sqrt(np.average((x - mx) ** 2, weights=w) * np.average((y - my) ** 2, weights=w)))


def run(t: pd.DataFrame, n_boot: int = N_BOOT) -> dict:
    latest, prev = SEASONS[-1], SEASONS[-2]
    tl = t[t["season"] == latest]
    head = summarize(t).to_dict()
    head_latest = summarize(tl).to_dict()
    centres_latest = by(tl, "centre")
    big = centres_latest[centres_latest["sessions"] >= 500]
    res = {
        "overall": {k: (int(v) if k in ("sessions", "places", "booked") else float(v)) for k, v in head.items()},
        "latest": {k: (int(v) if k in ("sessions", "places", "booked") else float(v)) for k, v in head_latest.items()},
        "centres": int(t["centre"].nunique()),
        "activities": int(t["activity"].nunique()),
        "season": by(t, "season", SEASONS),
        "family": by(t, "family").sort_values("full_rate", ascending=False).reset_index(drop=True),
        "weekday": by(t, "weekday", WEEKDAY_ORDER),
        "slot": by(t, "slot", SLOT_ORDER),
        "month": by(t, "month", MONTH_ORDER),
        "weekday_slot": by(t, ["weekday", "slot"]),
        "family_slot": by(t, ["family", "slot"]),
        "centre_spread_latest": {
            "centres": int(len(big)),
            "min": float(big["full_rate"].min()), "p10": float(big["full_rate"].quantile(0.1)),
            "median": float(big["full_rate"].median()), "p90": float(big["full_rate"].quantile(0.9)),
            "max": float(big["full_rate"].max()),
        },
        "cramers_v": {c: cramers_v(t, c) for c in ["centre", "activity", "family", "slot", "weekday", "month", "season"]},
        "predictability": [predictability(t, SEASONS[i], SEASONS[i + 1]) for i in range(len(SEASONS) - 1)],
        "persistence": [{"train": SEASONS[i], "test": SEASONS[i + 1], "r": slot_persistence(t, SEASONS[i], SEASONS[i + 1])}
                        for i in range(len(SEASONS) - 1)],
        "calibration": calibration(t, prev, latest),
        "bootstrap_latest": cluster_bootstrap(t, prev, latest, n_boot),
    }
    return res


def checks(res: dict, t: pd.DataFrame) -> None:
    assert res["overall"]["sessions"] == int(t["sessions"].sum())
    assert res["season"]["sessions"].sum() == res["overall"]["sessions"]
    assert 0 <= res["overall"]["occupancy"] <= 1 and 0 <= res["overall"]["full_rate"] <= 1
    for p in res["predictability"]:
        assert 0.5 < p["auc_same_slot"] <= 1
    lo, hi = res["bootstrap_latest"]["full_rate"]
    assert lo <= res["latest"]["full_rate"] <= hi
