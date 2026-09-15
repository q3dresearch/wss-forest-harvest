# Data shape

*Generated 2026-09-15T13:14:38Z by `wss schema` from the derived rows. Do not hand-edit — regenerate after any derive.*

**You should not need to download anything to read this.**

- **13,577 observations** across 1 partition(s), in **2 series**
  - `calfire.harvest.proposed` — 3,877 rows, **218 entities**
  - `skogsstyrelsen.harvest.notified` — 9,700 rows, **1320 entities**
- Raw: 437 file(s), 41,255,793 bytes on disk, 4 capture date(s), 2026-09-04 → 2026-09-08

## Sources

| source | cadence | endpoints | storage | personal data | licence |
| --- | --- | ---: | --- | --- | --- |
| `calfire.harvest.proposed` | weekly | 14 | git | none | California state open data; see https://data.ca.gov/ and CAL |
| `skogsstyrelsen.harvest.notified` | monthly | 226 | git | none | Skogsstyrelsen open data (Geodataportalen); verify terms bef |

## Columns

```
series_id, entity_id, observed_at, captured_at, metric, value, unit, source_id, raw_ref, parser_version
```

`entity_id` looks like: **calfire.harvest.proposed** `plan:ca:1-15NTMP-007-SON`, `plan:ca:1-16-018-HUM`, `plan:ca:1-16-049-MEN`; **skogsstyrelsen.harvest.notified** `cohort:se:01:2021:2021-09`, `cohort:se:01:2021:2021-10`, `cohort:se:01:2021:2021-11`

## Metrics

| metric | series | rows | entities | type | unit | distinct | range / samples |
| --- | --- | ---: | ---: | --- | --- | ---: | --- |
| `acres` | calfire.harvest.proposed | 518 | 218 | number | acres | 217 | `0.63` … `3249.55` |
| `county` | calfire.harvest.proposed | 516 | 217 | text |  | 28 | `AMA`, `BUT`, `CAL` |
| `filed_year` | calfire.harvest.proposed | 516 | 217 | number | year | 12 | `2015` … `2026` |
| `harvested_ha` | skogsstyrelsen.harvest.notified | 2,425 | 1320 | number | hectares | 863 | `0.0` … `832.4` |
| `note` | calfire.harvest.proposed | 168 | 117 | text |  | 94 | `17 acres Clearcut and 2 `, `3`, `AP is also Shelterwood R` |
| `notices` | skogsstyrelsen.harvest.notified | 2,425 | 1320 | number | count | 307 | `1` … `827` |
| `notified_ha` | skogsstyrelsen.harvest.notified | 2,425 | 1320 | number | hectares | 1313 | `0.3` … `4022.6` |
| `polygons` | calfire.harvest.proposed | 518 | 218 | number | count | 62 | `1` … `212` |
| `region` | calfire.harvest.proposed | 515 | 217 | number |  | 4 | `1` … `4` |
| `resubmitted_as` | calfire.harvest.proposed | 18 | 13 | text |  | 13 | `1-18-043-MEN`, `1-19NTMP-00011-MEN`, `1-20-00123-MEN` |
| `silviculture` | calfire.harvest.proposed | 515 | 217 | text |  | 16 | `Alternative Prescription`, `Clearcut`, `Commercial Thin` |
| `status` | calfire.harvest.proposed | 518 | 218 | text |  | 3 | `Denied`, `Proposed`, `Withdrawn` |
| `with_outcome` | skogsstyrelsen.harvest.notified | 2,425 | 1320 | number | count | 105 | `0` … `259` |
| `withdrawn_on` | calfire.harvest.proposed | 75 | 47 | date |  | 44 | `2016-01-04` … `2026-07-20` |

## Partitions

- `derived/observations/2026-09.csv.gz`
