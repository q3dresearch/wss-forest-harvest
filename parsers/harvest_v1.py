"""harvest.v1 — one observation per timber harvest plan, per capture.

The service returns one row per *polygon*; a plan carries many. 4,486 polygons
were 217 distinct HD_NUMs at first capture, so anything counted per row is out
by roughly twenty. This parser aggregates to the plan, which is also the unit
CAL FIRE approves, withdraws and denies.

Aggregating inside a parser is normally wrong here, because each capture is
split across partitions and a per-partition total is not a total. It is safe in
this one case *by construction*: partitions are HD_NUM ranges, so every polygon
of a plan lands in the same partition. Change the partition key and this
assumption dies with it.

This source publishes no "as of" stamp of its own. Left alone, derive would
date each observation by the moment its partition was fetched, and one capture
would arrive as fourteen snapshots seconds apart — impossible to read as a
single state of the register. So observed_at is pinned to the capture *date*,
taken from the raw file's own timestamp. All partitions of one run then share
one observed_at, which is what a snapshot means.

Geometry is deliberately not emitted. It is not a measurement, it does not
belong in a long-format observation table, and it would swamp it. The raw
archive keeps the polygons; examples/visualize.py reads shapes from there and
joins them to the status history from here.
"""

import json
import re
from collections import defaultdict

from wss import derive

PARSER_VERSION = "2"
SCHEMA_ID = "harvest.v1"


_STAMP = re.compile(r"/(\d{8})T\d{6}Z-")


def _observed_at(raw_ref):
    """Capture date from the raw filename, so a run is one snapshot."""
    m = _STAMP.search(raw_ref or "")
    if not m:
        return None
    d = m.group(1)
    return f"{d[:4]}-{d[4:6]}-{d[6:8]}T00:00:00Z"


def _text(v):
    if v in (None, "", "None"):
        return None
    return str(v).strip() or None


def _acres(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return 0.0


def parse(payload, ctx):
    doc = json.loads(payload.decode("utf-8", "replace"))
    if "error" in doc:
        raise derive.DeriveError(f"service returned an error payload: {doc['error']}")

    observed_at = _observed_at(getattr(ctx, "raw_ref", ""))
    plans = defaultdict(lambda: {"acres": 0.0, "polygons": 0, "attrs": {}})
    for feat in doc.get("features", []):
        a = feat.get("attributes", {})
        hd = _text(a.get("HD_NUM"))
        if not hd:
            continue
        p = plans[hd]
        p["acres"] += _acres(a.get("GIS_ACRES"))
        p["polygons"] += 1
        # polygons of one plan share these; last non-empty wins
        for k in ("PLAN_STAT", "REGION", "SILVI_1", "PROJECT_NAME"):
            v = _text(a.get(k))
            if v:
                p["attrs"][k] = v

    for hd, p in plans.items():
        entity = f"plan:ca:{hd}"
        attrs = p["attrs"]
        for metric, value, unit in (
            ("status", attrs.get("PLAN_STAT"), ""),
            ("region", attrs.get("REGION"), ""),
            ("silviculture", attrs.get("SILVI_1"), ""),
            ("acres", round(p["acres"], 2), "acres"),
            ("polygons", p["polygons"], "count"),
        ):
            if value is None:
                continue
            yield derive.Observation(entity_id=entity, metric=metric, value=value,
                                     unit=unit, observed_at=observed_at)


derive.register(SCHEMA_ID, parse, PARSER_VERSION)
