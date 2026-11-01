# Results

Every election result the atlas draws. Nothing else on a page is stored — no
percentage, no seat share, no "leading party" — because all of those are
derivable from what is here in one pass at read time, and a stored percentage is
a percentage that can disagree with its own counts.

---

## The shape of it

**Each tier carries two files per year, not one**, and they do different jobs.
This is the single most important thing to know before editing anything here.

| file | job | holds |
| --- | --- | --- |
| `…/{year}.json` | **colours the map** | the winner and its votes, per constituency |
| `…/{year}-detail.json` or `…/detail/{year}.json` | **fills the hover card** | *every* candidate, with name, party and votes |

The split exists because the two need different shapes. Colouring wants one row
per seat and nothing else; the card wants the whole field. Merging them would
mean shipping ~8,900 candidate rows to draw 543 polygons.

```
results/
├── ls/                      Lok Sabha — national files, filtered to a state at runtime
│   ├── {year}.json              state-level rollup, keyed by region code
│   ├── pc/{year}.json           one row per constituency
│   └── detail/{year}.json       every candidate, per constituency
└── ac/                      Legislative Assembly — one directory per state
    └── {STATE}/
        ├── {year}.json          one row per assembly constituency
        └── {year}-detail.json   every candidate, per assembly constituency
```

---

## Parliamentary — `ls/`

### `ls/{year}.json` — state level

Not read by the state page. Used for national rollups, and kept because it is the
only place the registered electorate is recorded.

```json
{
  "schema": 2, "election": "ls", "year": 2024,
  "regions": {
    "IN-UP": {
      "seats": 80,
      "electors": 154403112,
      "parties": [ { "code": "BJP", "seats": 33, "votes": 36364011 } ]
    }
  }
}
```

### `ls/pc/{year}.json` — constituency level

Keyed by the `unique_id` carried on the geometry in `data/geo/india-pcs.json`
(shape `S{state}_{seat}`, e.g. `S24_1`). `p` is the winner, `v` its votes, and
`o` is every other party that polled in that constituency.

```json
{
  "S24_1": {
    "st": "IN-UP",
    "p": "INC",
    "v": 547967,
    "o": { "BJP": 483425, "BSP": 180353, "IND": 7744, "AKBRPRVP": 5400, "NOTA": 4566 }
  }
}
```

Both `p` and the keys of `o` are party codes. Where `data/parties.json` covers the
party, its code is used; otherwise the Election Commission's own abbreviation is
kept verbatim. **A code not present in `parties.json` renders in the neutral
fallback grey** — see *Known gaps*.

### `ls/detail/{year}.json` — candidate level

Same keys as `pc/{year}.json`. `c` is the full candidate list, already sorted by
votes descending.

```json
{
  "S24_1": {
    "pc": "Saharanpur",
    "c": [ { "n": "IMRAN MASOOD",    "p": "INC", "v": 547967 },
           { "n": "RAGHAV LAKHANPAL", "p": "BJP", "v": 483425 } ]
  }
}
```

Votes are **general + postal**, which is the figure the Commission's own totals
reconcile against. Using the general column alone silently mis-assigns two seats
in 2024 — Mumbai North West and Jajpur both flip on postal votes.

---

## Legislative Assembly — `ac/`

One directory per state, because a state page never needs another state's seats.
Keys are the assembly constituency number *as the geometry carries it*, so they
join to `data/geo/ac/{STATE}.json` with no lookup table.

Files are named by the state's real assembly cycle (UP: 2017, 2022), not by
Lok Sabha years.

```json
// IN-UP/2022.json  (constituencies)
{ "1": { "p": "SP", "v": 134513 } }

// IN-UP/2022-detail.json  (constituencies)
{ "1": { "ac": "Behat",
         "c": [ { "n": "Umar Ali Khan", "p": "SP",  "v": 134513 },
                { "n": "Naresh Saini",  "p": "BJP", "v": 96633 } ] } }
```

An AC the report carries no result for (a poll countermanded and held later)
is absent from `constituencies` and listed in the file's `no_result`.

---

## What is real and what is not

**This matters and it is not obvious from the files**, because both carry a
`schema` field and look alike.

| | status |
| --- | --- |
| `ls/` — all four years | **Published Election Commission of India results.** Seat counts, votes and candidate names are the real figures. |
| `ac/` — real-cycle files (`provenance: "published"`) | **Published Election Commission of India results**, harvested by `tools/harvest-ac-results.py` from each report's table 10 and cross-checked against its tables 5 and 9. |
| `ls/byel/` | **Published Election Commission of India by-election results**, from ECI's index cards (`tools/harvest-ls-byel.py`). |

The assembly *boundaries* are a separate question — see `data/geo/ac/coverage.json`,
which records the eight states where they were validated.

---

## Coverage

| | 2009 | 2014 | 2019 | 2024 |
| --- | --- | --- | --- | --- |
| Lok Sabha — colouring | yes | yes | yes | yes |
| Lok Sabha — hover card | **no** | **no** | yes | yes |

Published assembly cycles (colouring and hover card), from ECI spreadsheets:

| state | cycles |
| --- | --- |
| IN-UP | 2017, 2022 |
| IN-WB | 2016, 2021, 2026 |
| IN-BR | 2020, 2025 |
| IN-TN | 2021, 2026 |
| IN-OD | 2019, 2024 |
| IN-PB | 2017, 2022 |
| IN-CT | 2023 |
| IN-HR | 2019, 2024 |

Not yet harvested: the cycles ECI publishes only as PDF (UP 2012, PB 2012,
HR 2014, OD 2014, BR 2015, CT 2013, CT 2018), and TN 2016, whose report's
table 5 disagrees with its own table 10.

Assembly data exists for eight states only: `IN-BR IN-CT IN-HR IN-OD IN-PB IN-TN
IN-UP IN-WB`. Every other state has no assembly geometry and therefore no
assembly results — not missing files, but a boundary set that does not exist.

**The Lok Sabha hover card does nothing on 2009 and 2014.** `ls/detail/` covers
2019 and 2024 only. Both years have colouring data, so the maps draw correctly
and the card silently fails — the same class of bug as a fetch that resolves to
nothing. Closing it is a re-run of the extractor in `tools/`, not new work.

---

## Rules this directory follows

1. **Absolute counts only.** No file stores a percentage, a share, or a leading
   party. Every one of those is computed in the page. The one exception is a
   by-election event's `turnout`, which the pages read directly; the `electors`
   and `polled` counts it is computed from are stored beside it.
2. **Codes, never names.** Files carry region codes and party codes. A name that
   appears anywhere came from `data/regions.json` or `data/parties.json`.
3. **Every file says where it came from, and only published data is allowed.**
   Harvested files carry `"provenance": "published"` and a `source` with the
   publisher, URL, sha256 and fetch time; `tools/validate_records.py` refuses
   anything else. Synthetic or dummy data is never stored here.
4. **A missing file means the level is not published**, not that the data is
   broken. Readers are expected to handle absence rather than assume it.
