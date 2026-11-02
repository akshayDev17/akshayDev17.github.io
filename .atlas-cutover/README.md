# Atlas cutover baseline

The URL inventory taken before the Election Atlas changes host. It lives under a
dot-path so Jekyll does not publish it.

- `inventory.py` builds it from a git ref (reproducible) and, with `--live`,
  fetches every row from the live host.
- `url-inventory.tsv` is the output for ref `4c64517`, fetched live from
  `https://akshayprabhakant.com` on 2026-11-01 (UTC).

```
python3 .atlas-cutover/inventory.py --ref 4c64517 --live https://akshayprabhakant.com \
    --out .atlas-cutover/url-inventory.tsv
```

## What the rows are

| kind | rows | what |
|---|---|---|
| `file` | 650 | tracked files Jekyll publishes byte-for-byte |
| `retired` | 669 | published files that held dummy data (53), a party image Wikipedia carries only under fair use (3: DMK, LJSP, RJD), or a stored copy of an official member portrait with its credits (613: everything under `data/photos/ls/2024/` and `data/photos/cabinet/2024/`, retired by the owner's decision to show initials plus a sansad.in link); expected to answer **404** once they are deleted, and listed so that 404 is not read as a regression |
| `page` | 5 | directory URLs with the trailing slash (`/`, the atlas and its `state/`, `mp/`, `mla/`) |
| `redirect` | 4 | the four atlas directory URLs without the slash; Pages answers 301 to the slash |
| `deeplink` | 1,991 | page URLs with the query strings the pages read: `?y=` and `&t=stands` on the national page, `state/?s=&y=` (with and without `&t=stands`) for every state and Lok Sabha year, `mp/?s=&c=` for every MPLADS constituency, `mla/?s=&c=` for every mapped assembly constituency |

Columns: `expect` is the status after the retired files are removed; `sha256` is the
committed file's hash; `live_*` is what the host answered.

## Findings from the live run

- **Pages publishes 1,319 files, not 1,395.** Jekyll also skips path segments
  that start with `_`, which drops 76 files under `work/election-atlas/tools/vendor`
  (`__init__.py`, `_imaging*.so` and so on). The live host answers 404 for them.
- Every published file, page, redirect and deep link answered as expected, and
  every non-HTML body matched the committed bytes.
- **The Cloudflare edge rewrites HTML.** It adds a hidden crawler link, a
  challenge-platform script and the Web Analytics beacon to every HTML response.
  `inventory.py` strips those three before hashing, after which every atlas page
  matches its committed file.
- **The home page (`/`, `/index.html`) still differs after that**, because
  Cloudflare Email Address Obfuscation replaces its `mailto:` link with a
  `/cdn-cgi/l/email-protection` link and adds `email-decode.min.js`. This is an
  edge setting, not a content change.
