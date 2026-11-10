"""Download the Madrid 300076 session files used by Class Capacity Lab.

Source: Ayuntamiento de Madrid, "Oferta y ocupación de plazas en actividades
deportivas dirigidas", dataset 300076, https://datos.madrid.es/dataset/300076-0-deportes-ocupacion
License: CC BY 4.0. Raw files go to data/raw/madrid/ (not committed).
"""
from __future__ import annotations

import hashlib
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "madrid"
BASE = "https://datos.madrid.es/dataset/300076-0-deportes-ocupacion/resource"
# "Clases abiertas y uso libre" files: one row per session, four complete seasons.
RESOURCES = {
    "2022-23": "300076-2-deportes-ocupacion-csv",
    "2023-24": "300076-31-deportes-ocupacion-csv",
    "2024-25": "300076-1-deportes-ocupacion-csv",
    "2025-26": "300076-0-deportes-ocupacion-csv",
}


def url(resource: str) -> str:
    return f"{BASE}/{resource}/download/{resource}.csv"


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for season, res in RESOURCES.items():
        out = RAW / f"open_{season}.csv"
        if not out.exists():
            req = urllib.request.Request(url(res), headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req) as r:
                out.write_bytes(r.read())
        manifest[season] = {
            "url": url(res),
            "bytes": out.stat().st_size,
            "sha256": hashlib.sha256(out.read_bytes()).hexdigest(),
        }
        print(season, manifest[season]["bytes"])
    (ROOT / "data" / "source_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
