// Checks the homepage as it is served.
//
//   node scripts/check-live.mjs                          the published site
//   node scripts/check-live.mjs --base http://127.0.0.1:8000 --bare
//                                                        a static copy (no site-shell)
//
// site-shell composes only the exact / (its route pattern also matches the
// query), so every other spelling of the homepage is GitHub Pages' page as
// committed and must work on its own. Checked:
// - / is composed by site-shell: the x-site-shell header and the site row (Home
//   marked as the current page, no trail under it, no lock drawn), with no Apps
//   section or site-apps slot and the sections numbered in order. With --bare,
//   / is checked like the others instead.
// - /?utm_source=x and /index.html (and, with --bare, / too) are loaded in
//   headless Chrome (puppeteer-core, the system Chrome or CHROME_PATH) and
//   checked by what they do on their own: a stored classic-dark choice gives
//   <html data-theme="classic-dark"> from the first frame and the Classic Dark
//   surface as the page background; the site-themes stylesheet and picker
//   module they load are the real ones; the theme picker is defined and shows
//   its combobox; there is no rail and nothing sticky or fixed outside the
//   Experience cards, at desktop and phone widths; there is no Apps section;
//   and the sections are numbered 01, 02, … in order, with the contents line
//   linking to each of them, in the same order, by its id.
// With --bare every request to another origin is refused.
// --retries N waits and retries the whole check N times (60 s apart), for the
// CDN cache to catch up after a deployment.

const args = process.argv.slice(2);
const flag = (name) => args.includes(name);
const option = (name, fallback) => {
  const i = args.indexOf(name);
  return i >= 0 && args[i + 1] ? args[i + 1] : fallback;
};
const BASE = option('--base', 'https://akshayprabhakant.com').replace(/\/$/, '');
const BARE = flag('--bare');
const RETRIES = Number(option('--retries', '0'));

async function get(path) {
  const res = await fetch(BASE + path, { redirect: 'follow', headers: { 'cache-control': 'no-cache' } });
  return { status: res.status, headers: res.headers, body: await res.text() };
}

/** The contents of the first <site-slot name="..."> element. */
function slot(html, name) {
  const m = new RegExp(`<site-slot name="${name}"[^>]*>([\\s\\S]*?)</site-slot>`).exec(html);
  return m ? m[1] : null;
}

/**
 * Problems with the sections: numbered 01, 02, … in order, no Apps section,
 * and the contents line linking to each section by its id, in the same order.
 * sections: [{ id, num }] in page order; contents: the contents line's hrefs.
 */
function sectionProblems(sections, contents) {
  const problems = [];
  if (sections.length === 0) problems.push('no sections found');
  if (sections.some((s) => s.id === 'apps')) problems.push('the Apps section is back');
  const nums = sections.map((s) => s.num);
  const expected = sections.map((_, i) => String(i + 1).padStart(2, '0'));
  if (JSON.stringify(nums) !== JSON.stringify(expected))
    problems.push(`sections are numbered ${JSON.stringify(nums)}, not ${JSON.stringify(expected)}`);
  const targets = sections.map((s) => `#${s.id}`);
  if (JSON.stringify(contents) !== JSON.stringify(targets))
    problems.push(`the contents line links to ${JSON.stringify(contents)}, not the sections ${JSON.stringify(targets)}`);
  return problems;
}

/** The sections and contents-line links in served HTML, for sectionProblems. */
function sectionsInHtml(html) {
  const sections = [...html.matchAll(/<section id="([^"]+)">\s*<div class="shead"><span class="num">([^<]*)<\/span>/g)].map(([, id, num]) => ({ id, num }));
  const nav = /<nav class="contents"[^>]*>([\s\S]*?)<\/nav>/.exec(html)?.[1] ?? '';
  const contents = [...nav.matchAll(/<a href="([^"]+)"/g)].map(([, href]) => href);
  return { sections, contents };
}

/** The site-themes stylesheet and picker module the page uses, fetched and checked. */
async function checkThemeAssets(sheetPath, pickerPath, at) {
  if (!sheetPath) at('no site-themes stylesheet');
  else {
    const sheet = await get(sheetPath);
    if (sheet.status !== 200) at(`${sheetPath} answers ${sheet.status}`);
    else if (!sheet.body.includes('[data-theme="classic-light"]') || !sheet.body.includes('[data-theme="classic-dark"]'))
      at(`${sheetPath} does not define both Classic Light and Classic Dark`);
  }
  if (!pickerPath) at('no theme picker module');
  else {
    const mod = await get(pickerPath);
    if (mod.status !== 200 || !mod.body.includes('export function defineThemePicker')) at(`${pickerPath} is not the picker module`);
  }
}

/** What a loaded page shows: theme, picker, rail and pinned elements, the sections and contents line. */
function observePage() {
  const root = document.documentElement;
  const sheet = document.querySelector('link[rel="stylesheet"][href*="/assets/site-themes/"]');
  const picker = performance
    .getEntriesByType('resource')
    .map((e) => e.name)
    .find((name) => name.includes('/assets/site-themes/') && name.endsWith('/picker.js'));
  const pickers = [...document.querySelectorAll('site-theme-picker')]
    .filter((el) => el.checkVisibility())
    .map((el) => {
      // site-themes main renders a select-only combobox; v0.2.0 and earlier a native select.
      const root = el.shadowRoot;
      const options = [...(root?.querySelectorAll('[role="listbox"] [role="option"]') ?? [])];
      const chosen = options.find((o) => o.getAttribute('aria-selected') === 'true');
      if (root?.querySelector('[role="combobox"]') && chosen)
        return { value: chosen.dataset.value, options: options.map((o) => o.dataset.value) };
      const select = root?.querySelector('select');
      return select ? { value: select.value, options: [...select.options].map((o) => o.value) } : null;
    });
  const pinned = [...document.querySelectorAll('body *')]
    .filter((el) => ['sticky', 'fixed'].includes(getComputedStyle(el).position) && !el.closest('#experience'))
    .map((el) => el.tagName.toLowerCase() + (el.getAttribute('class') ? `.${el.getAttribute('class')}` : ''));
  return {
    firstFrameTheme: window.__firstFrameTheme ?? null,
    theme: root.dataset.theme ?? null,
    background: getComputedStyle(root).backgroundColor,
    sheet: sheet ? new URL(sheet.href).pathname : null,
    picker: picker ? new URL(picker).pathname : null,
    pickerDefined: Boolean(customElements.get('site-theme-picker')),
    pickers,
    rail: Boolean(document.querySelector('.rail')),
    pinned,
    appsShown: Boolean(document.querySelector('#apps, site-slot[name="site-apps"]')),
    sections: [...document.querySelectorAll('main section[id]')].map((s) => ({
      id: s.id,
      num: s.querySelector(':scope > .shead .num')?.textContent.trim() ?? null,
    })),
    contents: [...document.querySelectorAll('nav.contents a')].map((a) => a.getAttribute('href')),
  };
}

/** The Classic Dark surface from the served site-themes catalogue, as a computed colour. */
async function darkSurface(sheetPath) {
  const { THEMES } = await import(new URL('themes.js', location.origin + sheetPath).href);
  const probe = document.createElement('i');
  probe.style.color = THEMES.find((t) => t.id === 'classic-dark').color.surface;
  document.body.append(probe);
  const color = getComputedStyle(probe).color;
  probe.remove();
  return color;
}

async function checkInBrowser(browser, path, problems) {
  const at = (msg) => problems.push(`${path}: ${msg}`);
  const page = await browser.newPage();
  try {
    await page.setViewport({ width: 1280, height: 900 });
    await page.emulateMediaFeatures([{ name: 'prefers-color-scheme', value: 'light' }]);
    await page.evaluateOnNewDocument(() => {
      localStorage.setItem('site-theme', 'classic-dark');
      requestAnimationFrame(() => {
        window.__firstFrameTheme = document.documentElement.dataset.theme ?? null;
      });
    });
    if (BARE) {
      await page.setRequestInterception(true);
      page.on('request', (req) => {
        if (req.url().startsWith(BASE + '/')) return req.continue();
        return req.abort();
      });
    }
    const res = await page.goto(BASE + path, { waitUntil: 'load' });
    if (res.status() !== 200) return at(`status ${res.status()}`);
    await page.waitForFunction(() => customElements.get('site-theme-picker'), { timeout: 15_000 }).catch(() => {});

    const seen = await page.evaluate(observePage);
    if (seen.firstFrameTheme !== 'classic-dark')
      at(`a stored classic-dark choice gives data-theme ${JSON.stringify(seen.firstFrameTheme)} on the first frame`);
    if (seen.theme !== 'classic-dark') at(`a stored classic-dark choice gives data-theme ${JSON.stringify(seen.theme)}`);
    if (seen.sheet) {
      const dark = await page.evaluate(darkSurface, seen.sheet);
      if (seen.background !== dark) at(`the page background is ${seen.background}, not the Classic Dark surface ${dark}`);
    }
    await checkThemeAssets(seen.sheet, seen.picker, at);
    if (!seen.pickerDefined) at('site-theme-picker is not defined');
    if (!seen.pickers.some((p) => p && p.options.includes('classic-dark') && p.value === 'classic-dark'))
      at(`no visible theme picker shows its combobox set to classic-dark: ${JSON.stringify(seen.pickers)}`);
    if (seen.appsShown) at('the Apps section or its site-apps slot is back');
    for (const p of sectionProblems(seen.sections, seen.contents)) at(p);

    for (const [width, height] of [[1280, 900], [390, 844]]) {
      await page.setViewport({ width, height });
      const { rail, pinned } = await page.evaluate(observePage);
      if (rail) at(`the left rail is back at ${width}px`);
      if (pinned.length) at(`sticky or fixed at ${width}px: ${pinned.join(', ')}`);
    }
  } finally {
    await page.close();
  }
}

async function checkAllInBrowser(paths, problems) {
  const { default: puppeteer } = await import('puppeteer-core');
  const browser = await puppeteer.launch({
    ...(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : { channel: 'chrome' }),
    args: process.env.CI ? ['--no-sandbox'] : [],
  });
  try {
    for (const path of paths) await checkInBrowser(browser, path, problems);
  } finally {
    await browser.close();
  }
}

async function checkComposed(problems) {
  const page = await get('/');
  const at = (msg) => problems.push(`/: ${msg}`);
  if (page.status !== 200) return at(`status ${page.status}`);
  if (!page.headers.get('x-site-shell')) at('not composed by site-shell (no x-site-shell header)');
  const path = slot(page.body, 'site-path') ?? '';
  if (!/<nav class="sp" aria-label="Site"><ul class="sp-apps">/.test(path)) at('the site row slot was not filled');
  else {
    if (!/<a class="sp-app" href="\/" aria-current="page"><span class="sp-label">Home<\/span>/.test(path)) at('the site row does not mark Home as the current page');
    if (/class="sp-trail"/.test(path)) at('the site row has a trail under it on the homepage');
  }
  if (/<svg\b/.test(path)) at('the site row draws a lock (an <svg>)');
  if (slot(page.body, 'site-apps') !== null || /<section id="apps"/.test(page.body)) at('the Apps section or its site-apps slot is back');
  const { sections, contents } = sectionsInHtml(page.body);
  for (const p of sectionProblems(sections, contents)) at(p);
  if (/class="rail"/.test(page.body)) at('the left rail is back');
}

async function runOnce() {
  const problems = [];
  if (BARE) {
    await checkAllInBrowser(['/', '/?utm_source=x', '/index.html'], problems);
    return problems;
  }
  await checkComposed(problems);
  await checkAllInBrowser(['/?utm_source=x', '/index.html'], problems);
  return problems;
}

for (let attempt = 0; ; attempt++) {
  const problems = await runOnce();
  if (problems.length === 0) {
    console.log(`ok: ${BASE} (${BARE ? '/, ' : '/ composed; '}/?utm_source=x and /index.html in headless Chrome)`);
    break;
  }
  if (attempt >= RETRIES) {
    for (const p of problems) console.error(`FAIL ${p}`);
    process.exit(1);
  }
  console.log(`attempt ${attempt + 1}: ${problems.length} problem(s), retrying in 60 s`);
  await new Promise((r) => setTimeout(r, 60_000));
}
