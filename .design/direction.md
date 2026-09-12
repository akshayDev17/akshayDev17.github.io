# Direction — An atlas plate, not a brochure

**Artifact:** home page, `home-v1/index.html` · **Date:** v1 · **Status:** first build

## PRODUCT / USER / PRIMARY GOAL

- **Product:** the home page of a personal engineering site, to be built as static HTML on GitHub Pages.
- **User:** someone who has been handed the link — a hiring manager, a technical peer, a researcher who followed a paper. They are skimming on a laptop, often in a hurry, sometimes on a phone.
- **Primary goal:** in five seconds they understand *what this person builds*; in ninety seconds they have skimmed real work, real papers and real contact routes without clicking anything.
- **Content template:** Hero · About · Work · Research · Experience · Contact (adopted from the gaurav-gandhi reference).
- **What is explicitly NOT being copied:** his theme. No dark hero panel, no rounded card grid, no avatar circle, no centred stack of identical sections, no gradient text, no glass, no glow.

## VISUAL DIRECTION

**The page behaves like the front matter and index plates of a printed reference atlas** — paper ground, hairline rules, a measured left rail, and one annotation colour used only where something is current or clickable. It is a document that has been *compiled*, not a landing page that has been *assembled*.

The subject matter earns it: this person's work is atlases (electoral cartography), hierarchies (module mind maps) and traces (harness engineering). An atlas index is the honest form for that body of work.

## HIERARCHY

Order on the page: positioning sentence → record → **Work** → Research → Experience → Contact.

1. The positioning sentence — the single loudest thing on the page.
2. The Record — descriptive facts, mono labels, tabular figures, plus the toolkit.
3. **Work — the first section, and the page's anchor.** Five ruled index rows; no cards.
4. Research — one honest paragraph until the three papers arrive.
5. Experience — the CV rendered in full. It runs a close second to Work by area, and that is accepted: cutting real achievements to win a pixel contest is the wrong purchase. **Position and emphasis make Work the anchor, not area.**
6. Contact — quiet, low, deliberate. The first vermilion on the page belongs to the `01` section number and the `in progress` state, where it means something.

Everything else is apparatus and stays small, mono, and grey.

### Revision log — v1 → v2, after the critic pass

- **About folded into the title plate**; five sections became four. Work's first row moved from y1744 to y1296, and one repetitive opener band disappeared with it.
- **Section titles moved from Plex Mono to Newsreader.** v1 contradicted its own contract here, and the mono bars were why the page read "terminal" rather than "atlas".
- **Section rules are now full-bleed**, reaching the layout edges inside the rail gutter.
- **The rail gained graduation marks** and a current-section state on load; the last section now wins at the document end.
- **Mobile keeps its navigation** — the rail becomes a horizontal sticky bar instead of vanishing, and the apparatus type floor rises to 11–12px.
- **The placeholder box is gone**; Research is honest prose until the papers arrive. Bibliography CSS was removed with it and returns with them.
- Fixed: inert `max-width` on work descriptions (inline span → `display:block`), the 4px `.side`/`.idx` baseline split, the clipped rail focus ring, and a `1fr` grid track that pushed the mobile document 131px wide.

### Revision log — v3 → v4, from owner feedback

- **Palette replaced.** Warm paper + terracotta accent read as borrowed house style. Now a cool
  blue-violet system (see COLOR above), contrast-verified at every pairing.
- **The rail was genuinely overflowing.** Measured: the rail's content box was **104px inside an
  88px column**, so `EXPERIENCE` crossed the hairline and bled into the content margin. The rail is
  now 124px with a real left inset, and the slack is +17px at every desktop width.
- **Research rebuilt as a real section**, not one line: an instrument panel of citations / h-index /
  papers, then each paper as a ruled entry with a journal mark, a hyperlinked journal name, Q1 and
  impact-factor chips, the title, the author line with the owner emphasised, and its citation count.
  Data read from the owner's Google Scholar profile; both journals are Q1 (NAR IF 15.0, JCIM IF 6.4).
- **Experience reduced to the reference's shape**: company heading, roles beneath it, dates aligned
  right, **no bullets**. 866px → 510px.
- **Elsewhere rebuilt icon-first**: five 56px hairline tiles with 24px inline SVG marks and mono
  labels. No prose list.
- **All five ruled blocks now share one right edge** — x=1092 at 1440 (record, stats, bibliography,
  chronology, links).

### Revision log — v4 → v5, from owner feedback

- **The rail's graduation marks are gone.** They were mine, not the reference's, and at 6px wide they
  read as bullets. Worse, the mark plus the current-state border formed a rotated T (⌐). Now the
  vertical rule alone carries "current", which is what it was always for.
- **Education left Experience** and became a `record` row in the title plate. Experience is now
  employment only.
- **Experience and Research both adopted the reference's card geometry**: a **two-column spread at
  ≥1024px** — a 16rem meta rail beside the content column — with a **sticky rail**, tech chips, a
  **dot-and-line ladder** for companies with more than one role, `h4` role titles under the company's
  `h3`, dates **hidden when they duplicate the company range**, and a **2px left rule** marking
  bullets instead of a dash.
- **The surface language is deliberately not his.** He uses rounded, tinted cards; this page keeps
  hairlines, no radius and no fill. Geometry borrowed, theme not — as instructed from the start.
- **Research gained its content**: real abstracts (Crossref + Europe PMC), real DOIs and PubMed IDs,
  volume/issue/pages, and a per-paper citation count.
- **The `jmark` journal initials are removed** — the full journal name is already hyperlinked.
- **Citations, UI/UX decision:** the section opens with the aggregate as an instrument panel
  (14 citations · h-index 2 · 3 papers); each paper then carries its own count in the **same mono
  figure** so a reader connects part to whole. It sits in the card's bottom row beside the DOI and
  PubMed links — one glance gives both "how cited is this" and "where do I read it" — and it is
  styled as a measurement, never as a pill or badge, which would read as a status instead of a fact.

## LAYOUT

- Two columns: a **fixed left rail** (124px, sticky) and an offset editorial column. Never centred.
- The rail is the *only* navigation — there is no top nav bar — and its one vertical rule marks the current section. No ticks, no progress meter.
- **Work is a two-column grid of cards** at ≥1024px, one column below. Each card carries its index number, title, one-line description and a ruled footer of facts.
- **Research is a column of cards.** Each paper is a spread at ≥1024px: journal, title, authors, citation count and links on the left; the abstract on the right.
- **Experience is a column of cards.** Each company is a spread: a 16rem sticky meta rail (company, dates, location, tech chips) beside the roles and bullets, with a dot-and-line ladder when a company has more than one role.
- Full-bleed hairline section rules reach the layout edges.

## SURFACE — the card system

Adopted from the reference at the owner's request, carrying **this** page's palette rather than its own.
Values read from its source, not estimated:

| property | reference | here |
|---|---|---|
| radius | `--radius: .5rem`, `rounded-xl` = ×1.4 → **11.2px** | same, `--r-card` |
| border | `1px color-mix(border 40%, transparent)` | same at 44% |
| surface | `color-mix(card 50%, transparent)` | same at 52%, white against the cool ground |
| padding | `1.5rem` (2rem at ≥1024 on the wide cards) | same |
| elevation | **hover only** — flat at rest | same |

The shadow is a **hover** state, not a resting one: `0 22px 48px -26px` in a 45% accent tint, plus a
4px lift and a small pointer-driven tilt. Cards are flat at rest because a resting shadow on a
document-style page reads as a widget shelf; the lift is what tells you the card is one object.

**Two card variants, and the split is load-bearing.** Cards that contain a sticky rail (Experience)
get **no `overflow:hidden` and no cursor wash**, because `overflow:hidden` destroys `position:sticky`
in a descendant. Only the Work cards carry the cursor-following radial wash, and only those get
`overflow:hidden` to clip it. This mirrors the reference's own architecture.

## GATES BEFORE DELIVERY

- AI-slop audit: no gradients, no glass, no orbs, no fake metrics, no "trusted by", no centred hero.
  **A card grid is permitted here** — but only because the cards hold real content, are distinguished
  by a hover elevation rather than decorative styling, and were a deliberate adoption rather than a
  default. A grid of cards whose only job is to hold a title and a logo would still fail this gate.
- Three-most-generic test applied at critique.
- Removal pass at the end.
- Rendered at 1440 and 390 and critiqued by a separate critic before this is called done.

## TYPOGRAPHY

- **Newsreader** (variable, optical-size axis) for the positioning sentence, section titles, work titles, paper titles, body prose. Used at genuinely different sizes rather than different weights.
- **IBM Plex Mono** for *all apparatus*: section numbers, labels, dates, statuses, links, captions, the rail. Nothing decorative is set in it.
- Two families with strictly separated jobs. No third family, no icon font.
- Body measure capped at 64ch. Line height 1.7 for prose, 1.25 for display.

**Measures as shipped**, measured against the 1088px column:

| block | measure | renders | gap at right |
|---|---|---|---|
| headline | 35ch | 1076px, 3 lines | 12px |
| standfirst / thesis | 75ch | 785px / 712px | 303 / 376px |
| record, grids, cards, tiles | `--col` | 1088px | 0 |

The body gaps are **accepted, not unfinished**. `ch` scales with font-size, so a fixed-pixel column
can only ever be *filled* by the largest type on the page. Closing the body gap needs **104ch** —
measured as 110–130 characters a line, past the point where the eye reliably finds the next line.
The limit is the readable one, not the filled one. Widening the body further would be a defect, not
a tidy-up.

### Measured scale — the known weakness

Read out of the rendered DOM, not the stylesheet: **14 distinct font sizes** across two families, and
**two weights** (400 and 500).

| family | sizes in use |
|---|---|
| Newsreader | 66 · 26 · 20 · 19 · 18 · 17 · 16 · 15 · 14 |
| IBM Plex Mono | 32 · 17 · 13 · 12 · 11 · 10 |

**What is right:** no sans-serif anywhere, and no default gesture-sans (Inter, Geist, Poppins, Space
Grotesk, DM Sans) — the usual signature of machine-made typography is a geometric grotesque, and this
page has none. Weights are held to two.

**What is wrong:** seven of the nine serif sizes sit inside six pixels of one another (14–20), so five
of them read as a single size rather than five levels; and the mono apparatus uses six sizes where two
would carry it. This is a scale with no ratio, chosen ad hoc — the improvisation is in the *sizes*,
not the *faces*. A proper pass would collapse the serif to ~4 steps and the mono to 2.

## COLOR

| token | value | job |
|---|---|---|
| `--paper` | `#F4F6FA` | ground — cool, blue-cast, never white |
| `--paper-2` | `#EAEEF6` | raised ground: journal marks, IF chips |
| `--paper-3` | `#DEE4F0` | row hover |
| `--ink` | `#0F1220` | text |
| `--rule` / `--rule-2` | `#D3D9E6` / `#BCC4D6` | hairlines, ticks, the rail |
| `--muted` | `#5A6273` | secondary text, descriptions |
| `--annot` | `#3A4BD8` | **annotation only** — current state, links, the impact-factor chip |

One accent, with a job: if a thing is not current, not a link, and not an annotation, it is never
blue-violet. No second accent, no gradients, no colour used decoratively.

**Why this and not the warm palette it replaced.** v1–v3 used warm paper with a terracotta accent,
which reads as another studio's house style rather than this person's. The ground is now cool and
slightly blue; the accent is a deep blue-violet in the same family as DeepSeek's own blue, darkened
from `#4D6BFE` to `#3A4BD8` so it clears 4.5:1 on every ground it is used on (measured 6.11:1 on
paper, 5.68:1 on paper-2, 5.18:1 on paper-3). Every text pair in the system passes AA; the minimum
is `muted` on the hover ground at 4.80:1.

**Journal marks.** The bibliography shows each journal as a hairline square holding its initials in
mono (`NAR`, `JCIM`). These are drawn marks, not publisher logos — real logos are third-party assets
with their own usage terms, and a portfolio does not need to redistribute them to be legible.

## DENSITY / INTERACTION / RESPONSIVE

- **Density:** fact-dense but rule-light — many lines, few boxes. Nothing floats.
- **Interaction:** rows are links. Hover darkens the row's ground and turns its number vermilion; the rail's active tick fills. Focus is a 2px ink outline, never removed.
- **Responsive:** below 900px the rail becomes a horizontal sticky bar with a 2px progress rule beneath it — navigation survives the collapse, and the active item scrolls itself into view. The index and chronology become single-column stacks; the apparatus type floor rises to 11–12px. Nothing is hidden that carries meaning.

## MOTION

Editorial and quiet. 240ms, `cubic-bezier(.2,.7,.3,1)`.
- Blocks rise 8px and fade in, once, as each enters the viewport.
- The rail's measurement line tracks scroll continuously.
- No parallax, no springs, no scroll-jacking, no looping motion.
- `prefers-reduced-motion`: all transforms removed, opacity only.

## IMAGERY

**none** — with one deliberate exception deferred to the case-study page. The home page must carry itself on typography, rules and composition. The election-atlas page will later get exactly one real map still at 16:9, because there the subject *is* cartographic. No stock imagery anywhere, no decorative SVG, no generated blobs.

## SIGNATURE

**The rail.** A numbered, labelled section index down the left edge that doubles as the entire
navigation and reports the current section with a single vertical rule. It is the one thing a
visitor will remember, and it comes from the subject rather than from a trend.

### Revision log — v5 → v6, from owner feedback

- **Tick marks and the scroll-measurement scale are removed.** Both were mine, not the reference's.
  The ticks read as bullets and, against the current-state border, formed a rotated T; the scale
  rendered as a growing blue bar built from the tick pattern. The rail is now index + current rule,
  nothing else. This is the second time decoration added for "instrument" flavour has been removed —
  the first was the same tick marks, restored once. Do not add them again.
- **The current-section marker is computed from geometry, not `IntersectionObserver`.** The observer
  reports only *changes* in intersection state, so the first section — already intersecting when the
  page loads — never fired again, and `00 About` could never take the marker back. `markCurrent()`
  now reads each section's top against a reading line at 32% of the viewport on every scroll, which
  is unconditional and correct at both edges of the document. Verified across ten transitions.

### Revision log — v6 → v7, from owner feedback

- **The card system is adopted** for Work, Research and Experience — see SURFACE above. Work moved
  from a ruled hairline index to a **two-column grid of cards**; Research papers and Experience
  companies became cards around their existing spreads.
- **The contract's own ban on card grids is lifted, with a condition** written into the gates: cards
  are permitted where they hold real content and are distinguished by elevation rather than
  decoration. Everything the AI-slop audit actually targets — gradients, glass, glow, orbs, fake
  metrics — is still banned.
- The reveal animation **fades the Experience cards instead of translating them**: `.rv` applies a
  transform to the element it animates, and a transformed ancestor turns a sticky descendant's
  containing block into that ancestor. `.job.rv{transform:none}` keeps the fade and keeps the rail.

### Revision log — v7 → v8, after the third critic pass

The critic scored v7 at 6.8/10 and found one real error of translation, which is worth recording
because it is the kind of mistake that looks like fidelity and is not:

- **The card's translucency maths is symmetric, and symmetry is wrong here.** The reference uses
  `color-mix(card 50%)` over near-black, where a half-white overlay is a large lift. Over a pale cool
  ground the same mix renders a **1.045:1** fill — a boundary the reader has to be told about — and
  `color-mix(border 40%)` over a light hairline landed at **1.19:1**. The reference's own palette
  comment records raising its border token until card outlines cleared 3:1, so the *intent* was
  legibility and only the *ratio* was copied. Fixed: an opaque white card, a `--card-line` at
  **3.06:1** against the ground, and a slightly deeper ground so the fill separates.
- **A tinted shadow on a light ground is a glow, not a shadow.** The critic measured my shadow at
  `rgb(212,217,244)` — *more blue than the ground* — and correctly pointed out that the AI-slop gate
  bans glow and that the accent is annotated as *current, link, or annotation*, none of which a hover
  shadow is. Depth now comes from a near-neutral ink shadow, and the hover no longer turns the border
  fully saturated accent.
- **Cards are now flat-vs-elevated by whether they are actually links.** Only `.work-card` (an `<a>`)
  elevates. Research and Experience keep the resting shadow and never move — before this, the
  896×559 Experience card promised a click it could not take, and had zero focusable descendants so
  its `:focus-within` branch could never fire for a keyboard user either.
- **The cursor wash leaked.** The handler nulled its card without clearing it, so every card the
  pointer had crossed stayed `--card-on:1` — measured two cards lit at once, and a tilt frozen at
  whatever position the mouse left. Verified fixed: crossing card 0 → card 1 now leaves `0 , 1`.
- **The index number sits beside the title again** (3px optical offset) rather than 22.8px above it;
  the Work grid moved its two-column split to 901px so the 901–1023px band stops rendering a
  700–800px-wide card with a two-line description and a half-empty last line; chips became pills so
  the card's 11.2px radius is not contradicted by square chips inside it; and `.job` re-entered the
  reveal list as a fade.

### Revision log — v8 → v9, from owner feedback

- **"Earlier builds" removed from Work.** Four entries; earlier projects are no longer on the home page.
- **The Research readings are centred** in three equal cells filling the row, divided by hairlines,
  instead of left-packed with a gap — a reading should span its instrument.
- **Research cards are now clickable**, with the same elevation and tilt as the Work cards, opening
  the paper in a new tab. Nested anchors are invalid HTML, so the mechanism is a **stretched link**:
  the paper title is an anchor carrying an `::after` overlay covering the whole card, while every
  inner link (journal, DOI, PubMed) is raised above it at `z-index:2` so each keeps its own target.
  Verified by hit-testing: the empty corner of a paper card resolves to the DOI anchor, and the DOI
  and journal links resolve to themselves.
  **This supersedes the v8 rule that "only `.work-card` elevates".** The test is not *is the card an
  `<a>`* but *is the card a link* — and a stretched overlay makes it one. Experience remains the only
  card that does not elevate, correctly: it still has no target to point at.
- The pointer-tracking listener generalised from `.work-grid` to `.work-grid, .bib` so the tilt works
  on both. The wash is contained by `isolation:isolate` on `.card` with the wash at `z-index:-1`,
  which paints above the card's own background and below every in-flow child — the arrangement that
  lets one absolute overlay cover a card while ordinary content still sits on top of it.

### Revision log — v9 → v10, from owner feedback

- **The display face is back to Newsreader.** Instrument Serif was tried as the display face and
  rejected — it did not sit right on this page. `--display` remains a separate token so the decision
  stays swappable, but it now points at `--serif`. If it is tried again, the headline measure has to
  move with it: a face with a narrower set needs a larger `ch` value for the same physical line.
- **The layout is now CENTRED with a fixed column** — variant B of four that were built and compared
  (fixed/left, fixed/centred, proportional/left, proportional/centred). The column is 1088px; at 1440,
  1920 and 2560 the gutters measure **114/114, 354/354, 674/674** — perfectly symmetric, where the
  left-pinned layout left 156px, 620px and 1260px of dead space on one side.
- **The centring is one value.** `--pad` is now
  `max(clamp(1.25rem,5vw,5.5rem), calc((100vw - var(--rail) - var(--col)) / 2))`. The second term is
  the leftover space once the rail and the column have taken theirs — and because the section rules
  and every full-bleed element derive from `--pad`, that one value relocates the column *and*
  everything measured against it. No margins, no wrapper, no drift.
- **The pitfall that cost two rounds, recorded so it is not repeated:** `main{max-width:84rem}` capped
  the box, so a viewport-derived gutter made the padding exceed the box — the column collapsed to
  **0px wide with a 20,906px document at 2560**. Any layout whose padding is derived from the viewport
  must remove that cap. It first appeared as the *smaller* symptom — a proportional `--col` that
  measured 1168px at both 1920 and 2560, i.e. never grew — before becoming a catastrophic one.
- Proportional width was measured and **not adopted**: it reached 1620px at 1920 and 1760px at 2560,
  but only by changing the arrangement too (Work 4-up, Research 2-up). The reasoning is kept here in
  case a large-screen pass is ever wanted.

## GATES BEFORE DELIVERY

- AI-slop audit: no card grid, no gradients, no glass, no orbs, no fake metrics, no "trusted by", no centred hero.
- Three-most-generic test applied at critique.
- Removal pass at the end.
- Rendered at 1440 and 390 and critiqued by a separate critic before this is called done.
