# my-github-io
Source code for personal portfolio website of Akshay Prabhakant

The Election Atlas lives in its own repository, [akshayDev17/election-atlas](https://github.com/akshayDev17/election-atlas), and is served at [akshayprabhakant.com/elections/](https://akshayprabhakant.com/elections/).

## Themes

Colours, elevation, card shape and fonts come from [akshayDev17/site-themes](https://github.com/akshayDev17/site-themes), pinned as a git tag in `package.json`. The site has no bundler, so `scripts/sync-site-themes.mjs` is its build step for themes. It inlines the package's boot script in the `<head>` of every page, so the first frame already has the visitor's theme, and copies `themes.css` and the picker modules into `assets/site-themes/<tag>/`. The site serves its own copy and fetches nothing from elsewhere for theming.

- After changing the pinned tag: `npm ci && npm run themes:sync`, then commit the result.
- `npm run themes:check` fails if a committed copy differs from the pinned tag. CI runs it on every PR and push to `main`.
- `.github/workflows/site-themes-bump.yml` checks daily for a newer site-themes tag and opens a bump PR with the copies regenerated. It can also be run by hand (`workflow_dispatch`). GitHub disables scheduled workflows after 60 days without repository activity, so every run calls the REST API (`PUT /repos/{owner}/{repo}/actions/workflows/site-themes-bump.yml/enable`) with `GITHUB_TOKEN` to keep the schedule enabled; this needs the `actions: write` permission the workflow grants.

`index.html` keeps its own variable names (`--paper`, `--ink`, `--annot`, …) as aliases of the package tokens. Do not define the package's own names (`--surface`, `--accent`, `--card`, …) in page CSS: a later `:root` rule would override every theme.

## Navigation and site-shell

At exactly `akshayprabhakant.com/`, the request goes through site-shell, the Cloudflare Worker in site-themes (`shell/`). It composes the GitHub Pages page as it streams out:

- It adds its own copy of the theme boot script, the tokens and the picker script to `<head>`. The page's copies above then do nothing: the boot script and the picker each guard against running twice, and `themes.css` repeats the same values.
- It replaces the contents of `<site-slot name="site-path">` with the site row shared by every app (Home, then each app, the current one marked; an app's own page trail goes on its own line under it).

The row comes from site-themes `src/apps.ts`; the homepage has no Apps section of its own, since the row already links every app.

site-shell's route is the exact `/`, and the pattern matches the query too. So `/?utm_source=…`, `/index.html` and a fail-open are served straight from GitHub Pages. The page therefore has to work on its own:
- its own theme comes from the synced package;
- the site-path slot is empty.

`src/apps.ts` is the only list of apps: adding, renaming, locking or hiding an app there needs no change here.

`node scripts/check-live.mjs` (after `npm ci`) checks the published site: `/` is composed with the site row (Home marked as the current page, no trail under it, no lock drawn), and `/?utm_source=x` and `/index.html` are loaded in headless Chrome (puppeteer-core drives the system Chrome; set `CHROME_PATH` to use another binary) and checked by behaviour: a stored `classic-dark` choice is applied from the first frame, the theme picker renders, there is no rail or sticky navigation, and there is no Apps section. On every page checked, the sections are numbered 01, 02, … in order and the contents line links to each of them, in the same order, by its id. `.github/workflows/live-check.yml` runs it after each GitHub Pages deployment of `main`, and it can also be run by hand. On every PR and push to `main` it runs with `--bare` against a static copy of the repository: all three pages get the same browser checks with every other origin refused.
