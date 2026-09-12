# `data/photos/` — portraits of winners

One small portrait per constituency, used by the level-2 hover card. Nothing here is
required to draw a map; if this directory were deleted the atlas would still work and
the cards would simply lose their face.

## Layout

```
data/photos/
  ls/                          Lok Sabha
    2024/
      <unique_id>.jpg          542 files, 132x170, ~7.5 KB each
      credits.json             provenance: who each file is, and where it came from
```

`<unique_id>` is the same key the geometry and the result files use — the `unique_id`
property of the matching feature in `data/geo/india-pcs.json` (e.g. `S24_39`). It is
**not** `ls_seat_code`, which is what the map paths are keyed by; the page converts
between the two.

Images are stored at 2x the display slot (`68x85` CSS px) so they stay sharp on a
retina screen. `object-fit: cover` does the crop, so the source aspect is preserved
rather than squashed to the slot.

## How the join works

The source is the Lok Sabha Secretariat member directory:

```
https://sansad.in/api_ls/member?loksabha=18&size=6000&page=1     (544 records)
```

Each record carries `stateName`, `constName`, `partySname` and `imageUrl`. Seats are
matched on **state + constituency name**, folded by:

- lowercasing, dropping `(SC)` / `(ST)` markers
- **folding `&` to `and`** — without this, `Daman & Diu` and `Daman and Diu` fold to
  different keys and two seats silently drop out
- a short alias table: `Gauhati`→`Guwahati`, `Pondicherry`→`Puducherry`,
  `Andaman & Nicobar`→`Andaman and Nicobar Islands`, `NCT of Delhi`→Delhi

That matches **542 of 542** seats.

## Why this is 2024 only

The directory lists members **currently sitting**. Each person holds exactly one
constituency — the one they sit for now. So the join is valid for the term a member is
in and for no other:

- **2019 and 2014 cannot be built this way.** `Gandhi, Shri Rahul` has
  `loksabhaExpr: "14,15,16,17,18"` but a single `constituency` of `Rae Bareli`; he won
  **Wayanad** in 2019. Joining 2019 by seat would put his face on the wrong
  constituency. Same for Shobha Karandlaje (`Bangalore North`; won Udupi Chikmagalur in
  2019) and Chirag Paswan (`Hajipur`; won Jamui in 2019).
  **A wrong face on a politician is worse than no face**, so those years are left empty
  rather than approximated. Name-based joining is not a fix — it reached only 78.8%.

- **By-elections contaminate even 2024.** Where a seat has been by-elected since the
  general election, the directory holds the *by-election* winner. One seat is affected:
  **Wayanad** (`S11_4`), where the directory holds Priyanka Gandhi Vadra and the
  general election was won by Rahul Gandhi. The build detects this by checking every
  seat's member against the declared ECI 2024 winner in
  `data/results/ls/detail/2024.json`, and re-joins such a seat **by name against the
  whole directory** — which finds Rahul Gandhi's portrait on his Rae Bareli record.
  The correction is recorded in `credits.json` under `by_election_corrections`.

  The check flags 18 seats in total. Seventeen are the same person written differently
  — `AMRARAM` vs `Ram, Shri Amra`, `RAJESH RANJAN ALIAS PAPPU YADAV` vs
  `Ranjan, Shri Rajesh`, `DAGGUBATI PURANDHESHWARI` vs `Purandeswari, Dr. D.`. These
  are left as the seat record, which is the right person. Only Wayanad is a genuinely
  different person.

A useful invariant to re-check after any rebuild: of 542 files there are **541 distinct
images**, the one duplicate being Wayanad and Rae Bareli — both won by Rahul Gandhi in
2024. Any other duplication means a join has gone wrong.

## Licence

`credits.json` records this, and it is repeated here because it matters:

> No explicit reuse licence is stated by the source. Government of India material is
> generally covered by GODL-India, but this has **not** been confirmed for these
> portraits specifically. Establish it before relying on this directory.

The images are fetched at ~7.5 KB each to keep the whole set near 5 MB.

## Rebuilding

The fetch script is not kept in the repo. To reproduce: pull the member list, join on
state + constituency exactly as described above, apply the by-election correction, then
downscale each portrait to a long edge of 175px and store it as `<unique_id>.jpg`.
