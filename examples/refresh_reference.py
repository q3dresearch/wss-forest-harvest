#!/usr/bin/env python3
"""Rebuild reference/ — the two datasets this repo cites but does not capture.

    python examples/refresh_reference.py

  thp-archive-counts.csv   approved/completed plans per county and filing year,
                           summarised from CAL FIRE's permanent THP layer
  ca-counties.csv          land area and centroid, from the Census Gazetteer

Both publishers keep their own history, so mirroring them would be noise. What
the charts need is a denominator, and a denominator is a summary. Committing
the summary keeps every chart deterministic and offline; re-run this when you
want it current.
"""
from __future__ import annotations

import csv, json, re, subprocess, sys, time, urllib.parse
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REF = REPO / "reference"
# Version is read from the installed engine rather than hardcoded: a pinned
# string here went stale at 0.5.4 against a v0.6.0 engine and told publishers
# the wrong thing about who was calling.
try:
    from wss import __version__ as _WSS_VERSION
except ImportError:
    _WSS_VERSION = "unknown"
UA = (f"wss/{_WSS_VERSION} (contact: q3dresearch "
      "+https://github.com/q3dresearch/wss-forest-harvest)")
ARCHIVE = ("https://services1.arcgis.com/jUJYIo9tSA7EHvfZ/arcgis/rest/services/"
           "CAL_FIRE_Timber_Harvest_Plans_Service_view_Public/FeatureServer/0/query")
GAZ = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2023_Gazetteer/2023_gaz_counties_06.txt"


def get(url):
    return subprocess.run(["curl", "-sS", "--max-time", "120", "-A", UA, url],
                          capture_output=True, text=True).stdout


def archive_counts():
    """Distinct plans per (county, filing year, status). Plans, not polygons."""
    plans = {}
    off = 0
    while True:
        q = urllib.parse.urlencode({
            "where": "1=1", "outFields": "HD_NUM,COUNTY,THP_YEAR,PLAN_STAT",
            "returnGeometry": "false", "orderByFields": "OBJECTID",
            "resultOffset": off, "resultRecordCount": 2000, "f": "json"})
        d = json.loads(get(f"{ARCHIVE}?{q}"))
        if "error" in d:
            raise SystemExit(f"archive: {d['error']}")
        fs = d.get("features", [])
        for x in fs:
            a = x["attributes"]
            hd = (a.get("HD_NUM") or "").strip()
            if hd:
                plans[hd] = (a.get("COUNTY"), a.get("THP_YEAR"), a.get("PLAN_STAT"))
        if len(fs) < 2000:
            break
        off += 2000
        time.sleep(0.6)
    agg = defaultdict(int)
    for county, year, status in plans.values():
        agg[(county, year, status)] += 1
    out = REF / "thp-archive-counts.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["county", "filed_year", "plan_status", "plans"])
        for (c, y, s), n in sorted(agg.items(), key=lambda kv: (str(kv[0][0]), str(kv[0][1]), str(kv[0][2]))):
            w.writerow([c, y, s, n])
    print(f"  {out.name}: {len(plans):,} distinct plans -> {len(agg):,} rows")


# CAL FIRE uses a 3-letter county code. It is the first three letters of the
# name for most counties; these are the ones where it is not.
# Verified against the codes actually present in CAL FIRE's data. DEL/SMO were
# guessed wrong first time round (DNT/SMT); SBR and MOO carry 2 and 4 plans
# respectively, so their reading is low-confidence and barely load-bearing.
# MOO is left unmapped: MOD is already Modoc, and 4 plans is not worth a guess.
ODD = {"SCR": "Santa Cruz", "SCL": "Santa Clara", "DEL": "Del Norte",
       "SBR": "Santa Barbara", "SBT": "San Benito",
       "SJQ": "San Joaquin", "SLO": "San Luis Obispo", "SMO": "San Mateo",
       "CCA": "Contra Costa", "ELD": "El Dorado", "LAK": "Lake"}


def counties():
    rows = [l.split("\t") for l in get(GAZ).strip().splitlines()]
    hdr = [h.strip() for h in rows[0]]
    recs = [dict(zip(hdr, [c.strip() for c in r])) for r in rows[1:]]
    by_name = {r["NAME"].replace(" County", ""): r for r in recs}
    out = REF / "ca-counties.csv"
    with out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["code", "name", "land_sqmi", "centroid_lat", "centroid_lon"])
        n = 0
        for name, r in sorted(by_name.items()):
            code = next((c for c, v in ODD.items() if v == name), name[:3].upper())
            w.writerow([code, name, r["ALAND_SQMI"], r["INTPTLAT"], r["INTPTLONG"]])
            n += 1
    print(f"  {out.name}: {n} counties")


if __name__ == "__main__":
    REF.mkdir(exist_ok=True)
    counties()
    archive_counts()
