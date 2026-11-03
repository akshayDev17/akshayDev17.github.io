# my-github-io
Source code for personal portfolio website of Akshay Prabhakant

The Election Atlas of India lives in its own repository, [akshayDev17/election-atlas](https://github.com/akshayDev17/election-atlas), and is served at [akshayprabhakant.com/elections/india/](https://akshayprabhakant.com/elections/india/).

## Themes

Colours, elevation, card shape and fonts come from [akshayDev17/site-themes](https://github.com/akshayDev17/site-themes), pinned as a git tag in `package.json`. The site has no bundler, so `scripts/sync-site-themes.mjs` is its build step for themes. It inlines the package's boot script in the `<head>` of every page, so the first frame already has the visitor's theme, and copies `themes.css` and the picker modules into `assets/site-themes/<tag>/`. The site serves its own copy and fetches nothing from elsewhere for theming.

- After changing the pinned tag: `npm ci && npm run themes:sync`, then commit the result.
- `npm run themes:check` fails if a committed copy differs from the pinned tag. CI runs it on every PR and push to `main`.
- `.github/workflows/site-themes-bump.yml` checks daily for a newer site-themes tag and opens a bump PR with the copies regenerated. It can also be run by hand (`workflow_dispatch`). GitHub disables scheduled workflows after 60 days without repository activity, so every run calls the REST API (`PUT /repos/{owner}/{repo}/actions/workflows/site-themes-bump.yml/enable`) with `GITHUB_TOKEN` to keep the schedule enabled; this needs the `actions: write` permission the workflow grants.

`index.html` keeps its own variable names (`--paper`, `--ink`, `--annot`, …) as aliases of the package tokens. Do not define the package's own names (`--surface`, `--accent`, `--card`, …) in page CSS: a later `:root` rule would override every theme.
