# How it works

## Two sources, two shapes

| | California | Sweden |
| --- | --- | --- |
| cadence | weekly, 14 GETs | monthly, 226 GETs (~8 min) |
| grain | one row per plan | one row per (county, case year, month) |
| raw per capture | 2.2 MB | 31 MB |
| derived per capture | 0.9 MB | 2.1 MB |

## The observation table is a view, not a copy

California emits one row per plan. Sweden does not: 128,052 notices at eight
metrics each is 840,000 rows and a **185 MB CSV per capture** — 2.2 GB a year
in anyone's working tree, for a file nobody can load. The Swedish parser
aggregates to (county, case year, month received) instead: **10,002 rows,
2.1 MB**, an 88× reduction that reconciles to 128,200 notices against the
service's 128,192.

Every individual notice is still in `raw/`. That is where the archive lives.

Aggregating inside a parser is normally wrong, because a capture is split
across partitions and a per-partition total is not a total. It is safe here
**by construction**: endpoints split by county, case year and month-aligned
date bands, so no two partitions touch the same cohort key. Change the
partition scheme and this assumption dies with it.

## Geometry, and why there is no GIS dependency

California requests `outSR=4326` with `maxAllowableOffset=0.0002`, generalising
polygons server-side to ~22 m: 1.78 MB down to 291 KB per partition, median 42
to 9 vertices, no polygon lost. Shapes live in `raw/`, status in `derived/`,
and `examples/visualize.py` joins them.

Because the service returns WGS84 already, a map is lon/lat → x/y and an SVG
`<path>`. No shapefile reader, no reprojection, no basemap, no plotting
library. A timelapse is one panel per `observed_at`.

Sweden is captured without geometry — at 128k polygons it would cost 73 MB a
capture for a map the cohort table does not need.

## `observed_at` is pinned to the capture date

Neither service publishes an "as of" stamp, so derive would otherwise date each
observation by the second its partition was fetched — one capture arriving as
14 or 226 snapshots seconds apart. Both parsers read the date from the raw
filename instead.

## Byte-stability is not free

Skogsstyrelsen returns rows in a different order on every request: three
identical fetches gave three different hashes at an identical byte count.
Without `orderByFields` every capture looks changed, dedup never fires, and the
archive grows without bound while nothing flags it. CAL FIRE's hosted service
happens to be stable; that is luck, not contract. See
[casing a site](../wss-engine/docs/casing-a-site.md), question 5b.

## Completeness is asserted, not assumed

Both services cap a response — 2,000 features — and say so in the payload while
returning HTTP 200. Partitions are sized well under the cap and keyed on a
**business key, not a surrogate id**: `HD_NUM` in California, county plus case
year in Sweden. A gate fails the capture if any response reports truncation.

## Denominators are cited, not captured

`reference/` holds a committed summary of CAL FIRE's permanent THP layer and
the Census county gazetteer — both keep their own history, so mirroring them
would be noise. `examples/refresh_reference.py` rebuilds it. Committing the
summary keeps every chart deterministic and offline.

## Running it

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
export WSS_CONTACT="you or your repo URL"

wss validate
wss doctor calfire.harvest.proposed      # read the raw response before trusting it
wss capture --cadence weekly && wss derive
python examples/visualize.py             # redraw examples/charts/
```

Three scheduled workflows: `capture-weekly` (California, Mondays 22:10 UTC),
`capture-monthly` (Sweden, 5th at 22:40), `derive` the day after, `health`
daily. No workflow names a source — capture shards whatever `registry/` marks
active, so infrastructure never changes when sources do.

To go live: push this repo and the engine under one owner, set the repo secret
`WSS_CONTACT`, then run a capture by hand once and confirm the bot's data
commit lands.

## Adding a source

1. `registry/<source_id>.yml`, `status: paused`.
2. A parser in `parsers/` if the payload shape is new.
3. `wss doctor <source_id>` — **read the raw response**.
4. Flip to `active`, commit. No workflow edits, ever.
