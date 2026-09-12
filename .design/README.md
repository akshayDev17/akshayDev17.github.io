# .design — the design record

**The live page is `../index.html` at the repository root.** Pages serves the root, so that is the
single source of truth; this folder is the record of how it got there.

| file | what it is |
|---|---|
| `direction.md` | the design contract — palette, type, layout, motion, and a v1→v10 revision log of what changed and why |
| `memory.md` | tokens in use, what each critique pass caught, and the reusable lessons |
| `experience-study.html` | a standalone study of the reference site's experience-section pattern |
| `home-v1/*.png` | full-page renders at 1440 and 390 |

**Privacy note:** this folder starts with a dot, and Jekyll excludes dot- and underscore-prefixed
paths by default, so none of it is served on the public site. That also keeps `_research/` private.
If you ever add a `.nojekyll` file — which a Next.js export will need, because `_next/` must not be
excluded — then everything here becomes publicly fetchable. Decide then whether that is wanted.
