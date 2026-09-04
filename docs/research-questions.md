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

| # | question | source |
| --- | --- | --- |
| 1 | When were plans withdrawn, and in which years did that spike? | `COMMENTS` dates (44 of 67) |
| 2 | Which counties withdraw most? | county from `HD_NUM` — Mendocino 13, Humboldt 10, Plumas 6 |
| 3 | Which silvicultural methods are withdrawn disproportionately? | `SILVI_1`, 22 values |
| 4 | How often is a withdrawal really a refiling? | `resubmitted_as` — 19% |
| 5 | What share of a filing cohort was approved? | join `HD_NUM` to the permanent THP layer |
| 6 | Where is harvest concentrated, and where does it fail? | geometry |

**Six of the twelve questions below need no capture at all.** They are a larder
recipe, and pretending otherwise would be dishonest.

## Answerable only by watching — what the archive is actually for

| # | question | why capture is required |
| --- | --- | --- |
| 7 | How long does a plan sit in Proposed before it resolves? | `COMMENTS` dates the withdrawal but nothing dates the proposal |
| 8 | Which plans vanish with no trace in either the archive or the withdrawn set? | only visible as a disappearance between captures |
| 9 | **Does CAL FIRE ever purge the withdrawal back-catalogue?** | if it does, this repository becomes the only record of it |
| 10 | Do plan boundaries change between proposal and approval? | geometry is overwritten in place |

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
