# my-github-io
Source code for personal portfolio website of Akshay Prabhakant

The Election Atlas of India lives in its own repository, [akshayDev17/election-atlas](https://github.com/akshayDev17/election-atlas), and is served at [akshayprabhakant.com/elections/india/](https://akshayprabhakant.com/elections/india/).

## Themes and navigation

GitHub Pages serves `index.html` from this repository's root. At `akshayprabhakant.com/` the request goes through site-shell, the Cloudflare Worker in [akshayDev17/site-themes](https://github.com/akshayDev17/site-themes) (`shell/`), which composes the page as it streams out:

- It adds the theme head block to `<head>`: the inline boot script (so the first frame already has the visitor's theme), the theme tokens, and the script that defines `<site-theme-picker>`.
- It fills `<site-slot name="site-path">` with the site path shared by every app, and `<site-slot name="site-apps">` with the Apps cards. Both come from the site's one app list, site-themes `src/apps.ts`: adding, renaming, locking or hiding an app is a change there, not here.

This repository has no build step and no dependencies. A theme or app-list change reaches the homepage when site-shell deploys, with no PR here.

If site-shell is skipped (it fails open and serves Pages' page unchanged), the page still renders in Classic Light: the `:where(:root)` block at the top of the page's `<style>` is a copy of site-themes `shell/generated/fallback.css`, and the slots show what the page put inside them (nothing for the site path, a one-line note for the Apps list). There is no theme picker in that state.

`index.html` keeps its own variable names (`--paper`, `--ink`, `--annot`, …) as aliases of the shared tokens. Do not define the shared names (`--surface`, `--accent`, `--card`, …) in a `:root` rule in page CSS: it would override every theme. The fallback block may define them only because `:where()` gives it zero specificity.
