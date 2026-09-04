# What this archive is for

Written after the first capture, and after finding that a claim in the first
version of the README was wrong. The honest split matters more than the pitch.

## The mistake worth recording

The first README said *"a third of proposed acreage is already withdrawn."*
That divided a **ten-year retained back-catalogue of withdrawals** by a
**two-year flow of live proposals**. The two populations sit in the same layer
and are not comparable.

- Of 149 Proposed plans, **141 were filed in 2025–26** — the live pipeline.
- Of 67 Withdrawn plans, filing years run **2015–2026** — a retained archive.

Measured properly against CAL FIRE's permanent record (~5,000 polygons, roughly
250 plans, per filing year), retained withdrawals run **1–13 plans a year**.
Withdrawal is rare, not common.

## The field that was missed

`COMMENTS` was not requested on the first build. It is populated on **88% of
withdrawn plans** and carries three things nothing else in the layer does:

- **a withdrawal date** — 44 of 67 plans, which is why the withdrawal timeline
  can be charted from a single download with no archive at all
- **a reason** — e.g. *"Withdrawn before approval 10/20/2020 due to Castle Fire"*
- **a replacement plan number** — 13 of 67 (19%) say *"Resubmitted as
  1-20-00123-MEN"*, so a withdrawal is often a refiling, not a death

The README previously claimed there was no reason field. There is.

## Answerable from one download — no archive needed

| # | question | answered by | finding |
| --- | --- | --- | --- |
| 1 | When were plans withdrawn? | `withdrawal-record.svg` | peaks in 2020 and 2022 |
| 2 | Which counties have the highest withdrawal rate? | `county-risk.svg` | **Sonoma 14.6%, Humboldt 1.4%** — the county with the most withdrawals has nearly the lowest rate |
| 3 | Which withdrawals are really refilings? | `county-risk.svg` (violet) | 13 of 67; Plumas drops 9.0% → 7.6%, Butte and Tuolumne to zero |
| 4 | How often overall? | same | 19% of withdrawals name a replacement |
| 5 | What share of a filing cohort is approved? | `cohort-approval.svg` | **roughly 97 in 100** |
| 6 | Does geography explain any of it? | `geography.svg` | latitude r = −0.40, harvest intensity r = −0.32 — weak, not significant at n=16 |

**Six of the twelve questions below need no capture at all.** They are a larder
recipe, and pretending otherwise would be dishonest.

## Answerable only by watching — what the archive is actually for

| # | question | why capture is required |
| --- | --- | --- |
| 7 | How long does a plan sit in Proposed before it resolves? | `COMMENTS` dates the withdrawal but nothing dates the proposal |
| 8 | Which plans vanish with no trace in either register? | only visible as a disappearance between captures |
| 9 | **Does CAL FIRE ever purge the withdrawal back-catalogue?** | if it does, this repository becomes the only record of it |
| 10 | Do plan boundaries change between proposal and approval? | geometry is overwritten in place |

Progress against all four is drawn in `pipeline-watch.svg`, which counts
captures rather than pretending to answers.

## Denominators

Rates need a base, and the base is CAL FIRE's permanent THP layer joined on
`HD_NUM`, plus the Census county gazetteer for land area and centroid. Both
keep their own history, so `reference/` holds a committed *summary* rather than
a mirror — regenerate with `examples/refresh_reference.py`.

Two caveats travel with every rate here:

- The retained withdrawal set may be incomplete, so each rate is a **lower
  bound**.
- One county code (`MOO`, 4 plans of 3,406) does not match the gazetteer and is
  excluded rather than guessed at.

Question 9 is the strongest justification and also the most speculative: the
back-catalogue is retained *today*, and nothing guarantees it will be. The
first months of capture are the test.

## Not answerable from this source at all

- Volume harvested, or what was actually cut — this is the proposal stage.
- Landowner or timber owner — those fields exist only on the permanent THP
  layer, which is also where the personal-data problem would start.

## The honest verdict

This is a **thin** wss case resting mainly on questions 8 and 9, wrapped around
a **strong** larder recipe that needs one download. It was published before
this analysis was done, which was the wrong order.
