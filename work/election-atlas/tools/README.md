# tools

Build scripts for the election atlas.
Run from `work/election-atlas/` (paths below are relative to it).

## Succession

1. `build-ls-results.py`
   - builds Lok Sabha result files
2. `eci_pdf.py`
   - PDF fallback, auto-invoked by the above
3. `fetch-cabinet.py`
   - fetches the Union Council of Ministers
4. `join-sansad.py`
   - enriches the cabinet with party / state / constituency / photo

## Scripts

### build-ls-results.py

- source: ECI Statistical Reports (retrieved into `_research/eci/`, gitignored)
  - `https://www.eci.gov.in/`
  - `https://results.eci.gov.in/`
- output: `data/results/ls/pc/{year}.json` + state files
- run: `python3 tools/build-ls-results.py --year 2024`
- verify: `python3 tools/build-ls-results.py --year 2024 --check`

### eci_pdf.py

- recovers a constituency × candidate table from an ECI PDF
- used by `build-ls-results.py` for years with no XLS (e.g. 2009, 2014)
- not run directly

### fetch-cabinet.py

- source: PM India portfolios + PIB communiqués
  - `https://www.pmindia.gov.in/en/news_updates/portfolios-of-the-union-council-of-ministers-2/`
  - `https://www.pib.gov.in/PressReleasePage.aspx` (reshuffles)
- output: name / rank / portfolio + `changes` (reshuffles)
- run: `python3 tools/fetch-cabinet.py --cycle 2024 --out data/cabinet/union/2024.json`
- reshuffles: `--communique <pib-url>` (repeatable)
- preview: `--dry-run`

### join-sansad.py

- source: Parliament of India member directory
  - Lok Sabha: `https://sansad.in/api_ls/member`
  - Rajya Sabha: `https://sansad.in/api_rs/member/in-council-of-ministers`
- adds: party, state, constituency, photo
- run: `python3 tools/join-sansad.py --cycle 2024 --in <fetched.json> --out <enriched.json>`
- options: `--photo-dir`, `--no-download`, `--dry-run`

## Notes

- fetches use `curl` (this machine's Python SSL bundle is broken)
- cabinet artifacts land in `data/cabinet/union/` + `data/photos/cabinet/`
- party colours + symbol images have no `.gov.in` source; symbol names only:
  - `https://www.eci.gov.in/eci-backend/public/api/list-of-political-party`
  - `https://www.eci.gov.in/eci-backend/public/api/recognition-derecognition`
