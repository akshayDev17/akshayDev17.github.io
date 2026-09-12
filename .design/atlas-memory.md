# Design memory — the election atlas

Read this before touching `work/election-atlas/`. It records what was decided, what the
critic caught, and the numbers that are easy to get wrong twice.

Direction files: `.design/atlas-direction.md` (level 1), `.design/atlas-level2-direction.md`
(level 2), `.design/atlas-level1-table-direction.md` (the national table).

## Tokens

No new tokens. The national table was built entirely from what level 1 already had.

| token | value | job here |
| --- | --- | --- |
| `--paper` | `#EEF1F8` | ground |
| `--paper-2` | `#E3E9F4` | the "dull" state — unselected parties, row hover, caveat surface |
| `--ink` | `#0F1220` | text, state outlines, selection edge. 15.28:1 on `--paper-2` (APCA Lc 91.9) |
| `--muted` | `#525A6B` | labels; rows left out of a selection. 6.12:1 on `--paper` (APCA Lc 75.6 — the floor) |
| `--rule` / `--rule-2` | `#D3D9E6` / `#BCC4D6` | hairlines |
| `--table-w` | `clamp(16.5rem,20vw,19rem)` | the table measure. Fixed, never proportional |
| `--map-spill` | `1` | the one dial: >1 trades page scroll for map width |

**No accent colour, and this is load-bearing.** Every saturated hue on these pages is a
party. The conventional caution orange is `BJP #E8590C`; `SP #D32F2F` and `DMK #C62828`
are the reds; `TDP #FFC300` is the amber. A warning colour or a red dot would read as a
party, and a 9px coloured square is *literally* the party swatch (`#card .sw`,
`.ntable .sw`). Selection, focus and warning are therefore all expressed in `--ink`.

## Numbers to not re-derive

- **India's projected extent is 0.8839 wide : 1 tall.** Width and height cannot both be
  filled. The map is always height-bound on a normal viewport, so its width is derived.
- At 1440x900 the map is **649px wide** in a 1325px column. Multiplying 731 by 0.884 gives
  646, not 877 — a critic got this backwards and built a whole fix on it. Divide.
- `--map-spill:1` holds **0 forced page scroll** at every viewport tested (1440x900,
  1280x720, 1024x768, 900x700, 390x800, 360x640). That is the page's primary constraint.
- 743 party codes polled nationally in 2024. `seats>0 OR share>=0.5%` gives **48 parties
  covering 96.6%** of the vote.

## What the critic caught, and the fixes

The critic pass was **pixel-sampled, not visual** — the critic model had no image input and
said so rather than claiming a look. It decoded the PNGs with a pure-Python decoder.

| finding | fix |
| --- | --- |
| The map/table gap was **76px at 900 wide and 421px at 1280** — not stable, therefore residue rather than composition | `.field` became `grid-template-columns:max-content var(--table-w)`. `1fr` took all the slack and threw the table to the far edge; a fixed track keeps it beside the plate and lets slack fall past both. **Gap is now 24–37px at every width** |
| Hover and selected shared `--paper-2`, so with a filter live a hovered non-selected row wore the *selected* surface | Hover is now a **fill**, selection is a **leading edge**. They cannot share a shape |
| `+N more` carried populated figures under clickable rows and read as withheld | Removed, with an explicit stated cut instead. (The critic assumed ~40 parties; there are 743, so "show all" was not viable) |
| The table announced itself as a caption, not a control | A live hint line: the contract by default, the count when a filter is on. `clear selection` promoted to `--ink` at body scale |
| `Seats won` measured 56px against ~26px siblings, so the header read as one string | Shortened to `Seats`; `table-layout:fixed` with fixed column tracks, which also stops the figures shifting on sort |
| Icon-only sort reset beside a text one | Both are text now |

**Rejected fix, and why it matters:** the critic computed the map element as 877px wide
(from `884/1000 x 731`) and concluded 149px of internal slack was drifting the columns. The
ratio divides, not multiplies: the element is 649px, which the probe measured directly.
A confidently-argued fix built on a backwards ratio would have "corrected" something that
was already right. **Measure the claim before acting on it, however well-argued.**

## Lessons

1. **A gap that changes with the viewport is not composition, it is the absence of a
   decision.** The tell was 76 → 421px, not the absolute size. An `1fr` track beside a
   fixed one always produces this: it eats the slack and pins the second object to the edge.
2. **Two states must never share a shape.** Hover and selection differing by a 2px line is
   not a distinction, it is a coin flip on a dark screen.
3. **An explicit, stated criterion beats a silent cap.** `+N more` is a dead end that looks
   clickable; "parties holding a seat, or polling 0.5%" is honest and the reader can audit it.
   Both clauses are needed — a seats-only cut drops BSP (2.04%), BJD (1.46%) and AIADMK
   (1.39%), parties that polled in the millions and won nothing.
4. **`max-content` is the right track for a height-bound object.** It sizes to the object
   instead of stretching, which is what let the table sit beside the map without a JS
   measurement.
5. **Verify with the real event.** `:focus-visible` does not match after a mouse click, so a
   focus-ring rule written only for keyboard leaves the clicked case broken. Dispatch real
   mouse events; do not infer from the selector.
