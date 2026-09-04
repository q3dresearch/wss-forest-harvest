#!/usr/bin/env python3
"""Render charts from the archive as SVG. Stdlib only — no GIS packages.

    python examples/visualize.py

  harvest-map.svg      where plans sit, coloured by status, with real polygons
  status-changes.svg   which plans changed status between captures

Geometry comes from the raw archive (already WGS84 — the endpoints request
outSR=4326), status from derived/observations. So a map is nothing more than
lon/lat -> x/y and an SVG <path>: no shapefile reader, no reprojection, no
basemap. The plans trace California's timber country by themselves.
"""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from xml.sax.saxutils import escape

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "examples" / "charts"
SURFACE, INK, INK2, MUTED = "#fcfcfb", "#0b0b0b", "#52514e", "#898781"
GRID, ORANGE, BLUE, VIOLET = "#e1e0d9", "#eb6834", "#2a78d6", "#4a3aa7"
FONT = 'system-ui, -apple-system, "Segoe UI", sans-serif'
COLOR = {"Proposed": BLUE, "Withdrawn": ORANGE, "Denied": VIOLET}


def T(x, y, s, size=12, fill=INK, anchor="start", weight="normal", tab=False):
    st = "font-variant-numeric: tabular-nums;" if tab else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family=\'{FONT}\' font-size="{size}" '
            f'fill="{fill}" text-anchor="{anchor}" font-weight="{weight}" style="{st}">{escape(str(s))}</text>')


def save(parts, name):
    parts.append("</svg>")
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text("\n".join(parts), encoding="utf-8")
    print(f"  wrote examples/charts/{name}")


def observations():
    """{observed_at: {entity: {metric: value}}}, deduplicated on captured_at."""
    seen = {}
    for part in sorted((REPO / "derived" / "observations").glob("*.csv")):
        with part.open(encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                k = (r["observed_at"], r["entity_id"], r["metric"])
                if k not in seen or r["captured_at"] > seen[k][0]:
                    seen[k] = (r["captured_at"], r["value"])
    out = defaultdict(lambda: defaultdict(dict))
    for (obs, ent, metric), (_, val) in seen.items():
        out[obs][ent][metric] = val
    return out


def polygons():
    """Every polygon from the newest capture, as (HD_NUM, status, rings)."""
    files = sorted((REPO / "raw").rglob("*.json"))
    if not files:
        return []
    newest = max(f.parent.name for f in files) if False else None
    stamp = max(f.name[:16] for f in files)          # capture timestamp prefix
    out = []
    for f in files:
        if not f.name.startswith(stamp[:9]):          # same capture day
            continue
        try:
            doc = json.loads(f.read_text(encoding="utf-8", errors="replace"))
        except json.JSONDecodeError:
            continue
        for feat in doc.get("features", []):
            rings = (feat.get("geometry") or {}).get("rings") or []
            a = feat.get("attributes", {})
            if rings and a.get("HD_NUM"):
                out.append((a["HD_NUM"], a.get("PLAN_STAT") or "?", rings))
    return out


def centroid(rings):
    pts = [p for r in rings for p in r]
    if not pts:
        return None
    return sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)


def chart_map(polys, snap, as_of):
    pts = [c for c in (centroid(r) for _, _, r in polys) if c]
    if not pts:
        return
    lon0, lon1 = min(p[0] for p in pts), max(p[0] for p in pts)
    lat0, lat1 = min(p[1] for p in pts), max(p[1] for p in pts)
    ym = lambda lat: math.log(math.tan(math.pi / 4 + math.radians(lat) / 2))
    Y0, Y1 = ym(lat0), ym(lat1)
    W, H, PL, PT, MW, MH = 980, 750, 46, 148, 460, 550
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="{SURFACE}"/>',
         T(38, 46, "Where California proposes to cut, and where it gives up", 21, INK, weight="600"),
         T(38, 70, f"{len(polys):,} harvest-plan polygons, {as_of}. Each dot is one polygon, sized by acres.", 13.5, INK2),
         T(38, 90, "No basemap — the plans trace the state's timber country themselves.", 11.5, MUTED)]
    acres = {e.split(":")[-1]: float(v.get("acres", 0) or 0) for e, v in snap.items()}
    npoly = {e.split(":")[-1]: float(v.get("polygons", 1) or 1) for e, v in snap.items()}
    order = {"Proposed": 0, "Denied": 1, "Withdrawn": 2}
    for hd, status, rings in sorted(polys, key=lambda t: order.get(t[1], 3)):
        c = centroid(rings)
        if not c:
            continue
        x = PL + (c[0] - lon0) / (lon1 - lon0) * MW
        y = PT + (Y1 - ym(c[1])) / (Y1 - Y0) * MH
        per = acres.get(hd, 0) / max(npoly.get(hd, 1), 1)
        r = max(1.1, min(9.0, math.sqrt(max(per, 0)) * 0.9))
        p.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{COLOR.get(status, MUTED)}" fill-opacity="0.5"/>')

    # inset: the densest cluster, at a zoom where polygons are legible
    IX, IY, IW, IH, span = 570, 148, 370, 300, 0.05
    cents = [(centroid(r), s, r) for _, s, r in polys]
    cents = [(c, s, r) for c, s, r in cents if c]
    best, bestn = None, -1
    for c, _, _ in cents[::7]:
        n = sum(1 for k, _, _ in cents if abs(k[0] - c[0]) <= span and abs(k[1] - c[1]) <= span * 0.62)
        if n > bestn:
            best, bestn = c, n
    if best:
        b0, b1 = best[0] - span, best[0] + span
        c0, c1 = best[1] - span * 0.62, best[1] + span * 0.62
        p.append(f'<rect x="{IX}" y="{IY}" width="{IW}" height="{IH}" fill="#f6f5f1" stroke="{GRID}"/>')
        near = 0
        for c, s, rings in cents:
            if not (b0 <= c[0] <= b1 and c0 <= c[1] <= c1):
                continue
            near += 1
            for ring in rings:
                d = []
                for lon, lat in ring:
                    d.append(f"{'M' if not d else 'L'}{IX + (lon-b0)/(b1-b0)*IW:.1f},{IY + (c1-lat)/(c1-c0)*IH:.1f}")
                if len(d) > 2:
                    col = COLOR.get(s, MUTED)
                    p.append(f'<path d="{" ".join(d)}Z" fill="{col}" fill-opacity="0.30" stroke="{col}" stroke-width="1.1"/>')
        p.append(T(IX, IY - 10, f"ACTUAL POLYGONS — {near} near {best[1]:.1f}N {abs(best[0]):.1f}W", 10, MUTED, weight="600"))
        p.append(T(IX, IY + IH + 18, "Generalised server-side to ~22 m; median 9 vertices.", 11, MUTED))

    tally = defaultdict(lambda: [0, 0.0])
    for e, v in snap.items():
        s = v.get("status")
        if not s:
            continue
        tally[s][0] += 1
        tally[s][1] += float(v.get("acres", 0) or 0)
    ly = IY + IH + 60
    p.append(T(IX, ly, "PLAN STATUS", 10, MUTED, weight="600"))
    ly += 18
    total_ac = sum(v[1] for v in tally.values()) or 1
    for s in ("Proposed", "Withdrawn", "Denied"):
        if s not in tally:
            continue
        p.append(f'<circle cx="{IX+6}" cy="{ly+4}" r="5.5" fill="{COLOR[s]}" fill-opacity="0.6"/>')
        p.append(T(IX + 20, ly + 8, s, 12.5, INK))
        n = tally[s][0]
        p.append(T(IX + 190, ly + 8, f"{n:,} plan" + ("" if n == 1 else "s"), 12.5, INK2, anchor="end", tab=True))
        p.append(T(IX + 300, ly + 8, f"{tally[s][1]:,.0f} ac", 12.5, INK2, anchor="end", tab=True))
        ly += 24
    p.append(T(IX, ly + 22, f"{tally['Withdrawn'][1]/total_ac*100:.0f}% of proposed acreage is already withdrawn,", 12.5, ORANGE, weight="600"))
    p.append(T(IX, ly + 40, "and none of it reaches the permanent THP archive.", 12.5, INK2))
    p.append(T(PL, PT + MH + 30, "each dot is one polygon, sized by its share of the plan's acres", 11, MUTED))
    save(p, "harvest-map.svg")


def chart_changes(data):
    dates = sorted(data)
    W, H = 900, 380
    p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         f'<rect width="{W}" height="{H}" fill="{SURFACE}"/>',
         T(38, 46, "Which plans changed status", 21, INK, weight="600"),
         T(38, 70, "Every move between Proposed, Withdrawn and Denied, capture to capture.", 13.5, INK2)]
    if len(dates) < 2:
        p.append(f'<rect x="60" y="118" width="{W-120}" height="180" fill="#f4f3ef"/>')
        p.append(T(W / 2, 196, f"{len(dates)} of 2 captures", 26, INK, anchor="middle", weight="600", tab=True))
        p.append(T(W / 2, 224, "A withdrawal is erased from the public record; this is the only place it survives.",
                   12.5, INK2, anchor="middle"))
        p.append(T(W / 2, 250, "renderable at the next weekly capture", 12, ORANGE, anchor="middle"))
        p.append(T(38, 340, "Drawing a trend from one observation would be worse than drawing nothing.", 11.5, MUTED))
        save(p, "status-changes.svg")
        return
    prev, now = dates[-2], dates[-1]
    moves = [(e, data[prev][e].get("status"), data[now][e].get("status"))
             for e in data[now] if e in data[prev]
             and data[prev][e].get("status") != data[now][e].get("status")]
    p.append(T(38, 92, f"{prev[:10]} → {now[:10]} · {len(moves)} plan(s) moved", 12, MUTED))
    y = 130
    for e, was, now_v in sorted(moves)[:12]:
        p.append(T(60, y, e.split(":")[-1], 12.5, INK, tab=True))
        p.append(T(300, y, f"{was} → {now_v}", 12.5, COLOR.get(now_v, INK2), weight="600"))
        y += 22
    save(p, "status-changes.svg")


def main():
    data = observations()
    if not data:
        print("  no observations — run wss capture && wss derive")
        return
    latest = max(data)
    chart_map(polygons(), data[latest], latest[:10])
    chart_changes(data)


if __name__ == "__main__":
    main()
