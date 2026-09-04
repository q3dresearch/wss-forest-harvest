"""harvest.notified.v1 — Swedish harvest notifications, aggregated to cohorts.

Skogsstyrelsen keeps 1,381,643 *performed* harvest records back to 1979 and
keeps *notifications* only from 2021. The intention to fell ages out on a
five-year rolling window; the outcome is kept for ever. This source exists to
preserve the half that gets deleted.

**Every notice is preserved in `raw/`. This parser deliberately does not put
them in the observation table.** One capture is 128,052 notices; at eight
metrics each that is 840,000 rows and a 185 MB CSV per month — 2.2 GB a year in
anyone's working tree, for a file nobody can load. The archive is the raw
bytes; the observation table is a view, and the view is a cohort table.

The grain is (county, case year, month received). That is safe to aggregate
inside a parser only because it is **partition-contained**: endpoints are split
by county, case year and month-aligned date bands, so no two partitions ever
contribute to the same cohort key. Change the partition scheme and this
assumption dies with it — the same warning the California parser carries.

Two fields invite a wrong reading:

  AvvHa       hectares recorded as harvested, on 32,815 of 128,192 notices. The
              other 95,315 carry AvvSasong = 'Uppgift saknas' — the outcome is
              *unknown*, not absent. Emitted as `with_outcome`, never as a
              completion rate.
  Beteckn     the case number. The performed-harvest layer redacts its own to
              'Visas ej', so there is no join from intention to outcome.
"""

import json
import re
from collections import defaultdict

from wss import derive

PARSER_VERSION = "2"
SCHEMA_ID = "harvest.notified.v1"

_UNKNOWN = "uppgift saknas"
_STAMP = re.compile(r"/(\d{8})T\d{6}Z-")


def _observed_at(raw_ref):
    """Capture date from the raw filename: 226 partitions are one snapshot."""
    m = _STAMP.search(raw_ref or "")
    if not m:
        return None
    d = m.group(1)
    return f"{d[:4]}-{d[4:6]}-{d[6:8]}T00:00:00Z"


def _text(v):
    if v in (None, "", "None"):
        return None
    return str(v).strip() or None


def _month(ms):
    if ms in (None, "", "None"):
        return None
    try:
        v = int(float(ms))
    except (TypeError, ValueError):
        return None
    if v <= 0:
        return None
    import datetime

    return datetime.datetime.fromtimestamp(v / 1000, datetime.UTC).strftime("%Y-%m")


def _num(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def parse(payload, ctx):
    doc = json.loads(payload.decode("utf-8", "replace"))
    if "error" in doc:
        raise derive.DeriveError(f"service returned an error payload: {doc['error']}")
    observed_at = _observed_at(getattr(ctx, "raw_ref", ""))

    cohorts = defaultdict(lambda: {"notices": 0, "ha": 0.0, "outcome": 0, "harv": 0.0})
    for feat in doc.get("features", []):
        a = feat.get("attributes", {})
        county = _text(a.get("Lannr"))
        year = a.get("ArendeAr")
        month = _month(a.get("Inkomdatum"))
        if not county or not year or not month:
            continue
        c = cohorts[(county, year, month)]
        c["notices"] += 1
        c["ha"] += _num(a.get("AnmaldHa"))
        season = _text(a.get("AvvSasong"))
        if a.get("AvvHa") not in (None, "", "None") or (season and season.lower() != _UNKNOWN):
            c["outcome"] += 1
            c["harv"] += _num(a.get("AvvHa"))

    for (county, year, month), c in cohorts.items():
        entity = f"cohort:se:{county}:{year}:{month}"
        for metric, value, unit in (
            ("notices", c["notices"], "count"),
            ("notified_ha", round(c["ha"], 2), "hectares"),
            ("with_outcome", c["outcome"], "count"),
            ("harvested_ha", round(c["harv"], 2), "hectares"),
        ):
            yield derive.Observation(entity_id=entity, metric=metric, value=value,
                                     unit=unit, observed_at=observed_at)


derive.register(SCHEMA_ID, parse, PARSER_VERSION)
