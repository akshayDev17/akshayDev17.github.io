# Design memory — home page

Read this before the next design session. It exists so the next page starts from these decisions
instead of rediscovering them.

**This file covers the home page.** For `work/election-atlas/` read `.design/atlas-memory.md`,
which carries the atlas tokens, its measurements, and what its critic pass caught.

## Tokens in use (`home-v1/index.html`)

**Palette** — cool ground, one blue-violet accent with a job. Replaced the warm/terracotta system in v4.

| token | value | job |
|---|---|---|
| `--paper` | `#F4F6FA` | ground. Cool, blue-cast, never white. |
| `--paper-2` | `#EAEEF6` | raised ground: journal marks, IF chips |
| `--paper-3` | `#DEE4F0` | row hover. `--paper-2` was a 1.07:1 change and read as nothing. |
| `--ink` | `#0F1220` | text — 17.21:1 |
| `--muted` | `#5A6273` | secondary — 5.66:1 on paper, 4.80:1 on hover ground (the floor) |
| `--rule` / `--rule-2` | `#D3D9E6` / `#BCC4D6` | hairlines and tick marks |
| `--annot` | `#3A4BD8` | **annotation only** — current state, links, the IF chip. 6.11:1 on paper. |

Every text pair in the system passes AA. If you change any token, re-run the contrast check before
committing it — the accent was deliberately darkened from DeepSeek's `#4D6BFE`, which fails AA as
small text on a light ground.

**Type** — two families, strictly separated jobs.
- `--serif`: **Newsreader** (variable, optical size). Everything you read.
- `--mono`: **IBM Plex Mono**. Everything that is apparatus: numbers, labels, dates, links, the rail.
- Never a third family, never an icon font, never an emoji.

**Spacing** — `--s1…--s9` = 4 / 8 / 12 / 16 / 24 / 32 / 48 / 72 / 112.
**Column** — `--col: 56rem`. Every ruled block ends at the same x. This is the grid.
**Radius** — none. Sharp editorial edges are the decision; the only rounded thing removed was a chip.
**Motion** — 240ms, `cubic-bezier(.2,.7,.3,1)`, 8px rise + fade, once.

## What the critic passes caught (and what each taught)

Two passes, both by a subagent forbidden from writing code. Neither could view the images —
both decoded the PNGs programmatically and drove headless Chrome over CDP for real geometry.
Scores: **v1 5.6 → v2 6.3**.

**Real defects, not opinions:**
1. `max-width:52ch` on work descriptions **never applied** — `.desc` was an inline `<span>`, and
   that property is ignored on non-replaced inline boxes. Rendered ~97ch while the stylesheet
   claimed 52. *Lesson: measure the rendered box, not the declaration.*
2. The reveal observer's `-8%` bottom inset meant the last 427px of the page never intersected, so
   the shipped screenshot was missing the entire Contact block. *Lesson: an entrance animation with
   `opacity:0` as the default state is a content-loss bug waiting for a viewport.*
3. A bare `1fr` grid track takes its min-content floor from a `nowrap` child, which pushed the
   mobile document 131px wide. `minmax(0,1fr)` is the fix. *Lesson: `1fr` is `minmax(auto,1fr)`.*
4. `text-wrap:balance` on the headline left its longest line 164px short of the declared measure.
5. The rail's focus ring was clipped off the left edge — and my first fix moved it the wrong way
   (`outline-offset:1px` pushes a 2px ring to x=−3). Negative offset insets it. *Lesson: verify the
   direction a fix moves something, don't assume.*
6. I wrote "section titles in Newsreader" into the contract and then set them in Plex Mono.
   *Lesson: the contract is the standard the critic holds you to. Contradicting it is the most
   expensive kind of own goal.*
7. **The rail's labels overflowed their column by 16px** and neither critic pass caught it — the
   owner did, by eye. A column flex item's `min-width:auto` uses the longest unbreakable word, and
   `EXPERIENCE` in 11px mono with letter-spacing needs more than an 88px rail. The tell is one
   number: **an element's `scrollWidth` greater than its `clientWidth`**. Measure that on every
   fixed-width column, not just on the document.
8. **I read the reference wrong by reading only its headings.** I concluded gaurav's Experience had
   no bullets because a heading dump showed only company → role · dates. His bullets are plain
   `<li>` elements, so they never appear in a heading dump — and the thing I "simplified away" was
   the whole point of his section. *Lesson: to copy a section's manner, read its component source.
   Rendered headings tell you the outline, never the presentation.*
9. **Decoration I add without being asked is the decoration that gets removed.** The rail's
   graduation marks were my idea, added to make the rail "read as an instrument", and they read as
   bullets and formed a rotated T against the current-state border. The critic had suggested them
   too — both of us were decorating. They were removed once, restored, and removed again along with
   the scroll-measurement scale, which rendered as a growing blue bar the owner never asked for.
   **Do not add ticks or progress meters to the rail.**
10. **`IntersectionObserver` cannot track "which section am I in" on a page whose first section is
   already on screen at load.** It fires on *changes* of intersection state, so a target that starts
   intersecting never fires again until it leaves and returns — the first section can never take the
   marker back, and the last one can never reach a bottom-inset band. Read geometry against a
   reading line on every scroll instead: unconditional, correct at both document edges, and it
   removes the whole class of bug. Verified across ten scroll/click transitions for both directions.
11. **A ratio copied from a dark theme is not a value.** Copying `color-mix(card 50%)` from a design
   whose ground is `#0a0b0d` produces a 1.05:1 fill on a pale ground — the *number* travelled, the
   *intent* did not. Translucency, border mixes and tinted shadows are all functions of the ground
   they sit on. Copy the intent (a border that clears 3:1), recompute the value, and check it with a
   contrast function rather than by eye. The reference had already learned this and written it in its
   own palette comment; I read that file and still copied the ratio.
12. **A tinted shadow on a light ground is a glow.** Measured at `rgb(212,217,244)` — *bluer than the
   ground*, i.e. emitted light rather than cast darkness. Depth comes from neutral ink at low alpha.
   And it spent the accent colour on decoration, which the palette rules forbid.
13. **`overflow:hidden` and `position:sticky` cannot coexist in the same ancestor chain.** A card
   that needs to clip a decorative child therefore cannot contain a sticky rail. Decide which the
   card is for before styling it.
14. **Only the thing that is a link may look clickable.** Giving every card the same hover elevation
   advertised interaction on a 559px panel with zero focusable descendants — a promise the markup
   could not keep, and one a keyboard user could never even see.

**The structural one:** the first pass found About inserted between the record and Work, so the first
piece of work sat 1.94 screens down. The fix was not to trim About but to **fold it into the title
plate**, which also removed one of five identical opener bands. Work's first row went y1744 → y1375.

15. **A chart whose labels contradict the numbers beside it is worse than no chart.** The seat strip
    grouped states by the party each *leads*, so a run labelled "BJP 387" sat an inch from a readout
    saying "BJP 211". Both were right. A reader had no way to learn they counted different things, and
    no amount of styling fixes a graphic that means two things at once. When two numbers sit on one
    screen, make them count the same thing or say plainly what each counts.

16. **When colour is the only channel, the palette is a data problem — score it against the data's own
    adjacency, not against taste.** Deriving the border graph from the TopoJSON's shared arcs turned
    "these colours look fine" into 32 pairs and a ΔE per pair. It found TDP amber 22 ΔE from BJP
    saffron across three real borders, and two parties that were byte-identical. It also proved one
    pair *cannot* be fixed: TDP/BJP/DMK form a triangle inside the orange-to-red arc, so any three
    colours there are either indistinguishable or stop being recognisable as those parties. The
    answer was a second channel, not a cleverer palette. **Optimising a colour metric alone will
    happily hand you a muddy brown for the BJP.** Constrain hue family first, then separate.

17. **A redraw silently invalidates everything bound to the old elements.** `drawMap()` rebuilds every
    `<path>` on resize; listeners attached per path died with them, so the map drew perfectly and did
    nothing at all — and the paths also lost the inline `--c` that coloured them, rendering black.
    Both were invisible in a screenshot. Delegate events from a stable ancestor, and treat "apply
    state to elements" as a function that must re-run after any rebuild.

18. **Mixing projected and geographic coordinates fails silently.** `geoPath.centroid()` returns
    pixels; `geoContains()` takes [longitude, latitude]. Every containment test returned false, every
    map label was dropped, and nothing threw. The guard `if (at) continue` turned a units bug into a
    blank feature.

19. **Headless `--virtual-time-budget` freezes CSS transitions.** A computed style read after a state
    change returns a mid-interpolation colour — an orange that was on its way to grey read as "the
    empty state is broken". Assert rendered colours with transitions disabled, or the measurement
    will send you chasing a bug that is not there.

20. **Measure the composition; do not eyeball it.** "The map looks a bit small" is not actionable.
    `getBBox()` against the container said the map filled **65%** of its column — 216px of dead space —
    and that the strip's axis fell 27px below the fold. Resizing the column to the map's real ink
    dimensions took it to 97%, and putting the readout's totals beside its table rather than above it
    brought the whole instrument back above 900px. Both were arithmetic, not taste.

21. **Not every defect is a layout defect.** The mobile footer was 629px of fine print and read as a
    spacing failure. Two columns measured **634px against 629px** — halving the width doubles the
    lines and the pairing saves nothing. The height was text volume. Measure the competing fix before
    rewriting the layout.

22. **A breakpoint should drop a channel, not shrink it.** The seat strip keeps its party runs below
    60rem and drops the per-state subdivisions. The state split stops being legible long before the
    party split does, so keeping both would mean neither reads — and the bar would be 23% gaps.

## Numbers worth keeping

| | v1 | v2 | v3 |
|---|---|---|---|
| Desktop height | 5313px | 3741px | **3324px** |
| Mobile height | 7848px | 5359px | **4998px** |
| First work row | y1744 | y1375 | **y1036** |
| Work vs Experience | 796 / 1630 | 945 / 933 | **894 / 866** |
| Ruled-block right edge | none shared | none shared | **x1056, all three** |
| Mobile overflow | — | 0 | **0** |
| Stranded reveals | 3 of 30 | 0 of 22 | **0 of 20** |

## Open items

- **Four routes and `/cv.pdf` do not exist**: `/work/harness-atlas/`, `/work/ml-engineering-atlas/`,
  `/work/mcp-youtube-extract/`, `/work/election-atlas/`, `/work/`, `/cv.pdf`. The markup is correct
  for the final site; the pages are the next build. The side column labelling two of them `live`
  refers to the artifacts existing, not to the routes resolving.
- Root-absolute paths (`/work/…`) are correct **because** the repo is `akshayDev17.github.io`, a user
  site. If it ever becomes a project page, every one of them breaks.
- Research is honest prose, not a bibliography, until the three paper titles/venues/abstracts arrive.
  The bibliography CSS was removed with the placeholder and returns with them.
- At ≥1920px the full-bleed rules stop at x1432 and leave a widening empty field. Left-pinned is
  intentional at 1440; at 2560 it wants a decision.
