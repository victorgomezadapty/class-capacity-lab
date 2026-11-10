# Source provenance

- **Publisher:** Ayuntamiento de Madrid, Portal de datos abiertos.
- **Dataset:** "Oferta y ocupación de plazas en actividades deportivas dirigidas", id 300076. https://datos.madrid.es/dataset/300076-0-deportes-ocupacion
- **License:** Creative Commons Attribution 4.0 (CC BY 4.0). https://creativecommons.org/licenses/by/4.0/
- **Files used** ("Clases abiertas y uso libre", CSV, one row per session):

| Season | Resource |
|---|---|
| 2022-23 | 300076-2-deportes-ocupacion-csv |
| 2023-24 | 300076-31-deportes-ocupacion-csv |
| 2024-25 | 300076-1-deportes-ocupacion-csv |
| 2025-26 | 300076-0-deportes-ocupacion-csv |

Downloaded on 2026-11-10 by `src/download_madrid.py`, which also writes sizes and SHA-256 hashes to `data/source_manifest.json`. Raw files are not committed. The derived slot table in `data/processed/` and `delivery/kaggle/dataset/` is shared under CC BY 4.0 with attribution to the Ayuntamiento de Madrid and a note that it was filtered, reclassified and aggregated.

Not used: seasons 2016-17 to 2019-20 and the "Clases cerradas" files are monthly class totals, not sessions. Season 2020-21 has session rows but no "Tipo de actividad" column, so directed classes cannot be separated from free use. Season 2021-22 has the column but was still affected by pandemic capacity limits; it is left out so the four analysed seasons are comparable. Adding it is a one-line change in `src/download_madrid.py` and `src/build_sessions.py`.
