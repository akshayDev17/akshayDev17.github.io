// Checks the homepage as it is served.
//
//   node scripts/check-live.mjs                          the published site
//   node scripts/check-live.mjs --base http://127.0.0.1:8000 --bare
//                                                        a static copy (no site-shell)
//
// site-shell composes only the exact / (its route pattern also matches the
// query), so every other spelling of the homepage is GitHub Pages' page as
// committed and must work on its own. Checked:
// - / is composed by site-shell: the x-site-shell header, the site path, and
//   Apps cards matching site-shell's /_site/apps.json (the listed apps from
//   site-themes src/apps.ts, less the homepage). With --bare, / is checked like
//   the others instead.
// - /?utm_source=x and /index.html carry, on their own: the inline theme boot
//   script, a stylesheet that defines Classic Light and Classic Dark, and the
//   theme picker module. Their Apps cards are rendered in the browser from
//   /_site/apps.json.
// - None of them has the old left rail.
// With --bare, all three pages are loaded in headless Chrome (puppeteer-core,
// the system Chrome or CHROME_PATH), with every request to another origin
// refused, and checked by what they do: a stored classic-dark choice gives
// <html data-theme="classic-dark"> and the Classic Dark surface as the page
// background; the theme picker is defined and shows its select; there is no
// rail and nothing sticky or fixed outside the Experience cards, at desktop
// and phone widths; and the Apps section shows the fallback line with its
// reload link, since /_site/apps.json cannot be reached.
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

/** The Apps cards in a site-apps slot: [{ id, href, gated }]. */
function appCards(html) {
  const list = slot(html, 'site-apps') ?? '';
  return [...list.matchAll(/<li data-app="([^"]+)"( data-gated="")?><a href="([^"]+)"/g)].map(([, id, gated, href]) => ({
    id,
    href,
    gated: Boolean(gated),
  }));
}

/** The cards site-shell's /_site/apps.json says the homepage lists. */
async function listedApps(at) {
  const res = await get('/_site/apps.json');
  if (res.status !== 200) {
    at(`/_site/apps.json answers ${res.status}`);
    return null;
  }
  return JSON.parse(res.body)
    .filter((app) => app.id !== 'home')
    .map((app) => ({ id: app.id, href: app.path, gated: Boolean(app.gated) }));
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

async function checkStandalone(path, problems) {
  const page = await get(path);
  const at = (msg) => problems.push(`${path}: ${msg}`);
  if (page.status !== 200) return at(`status ${page.status}`);
  const head = page.body.slice(0, page.body.indexOf('</head>'));
  if (!/<script>\(function siteThemeBoot\(/.test(head)) at('no inline theme boot script in <head>');
  const css = /<link rel="stylesheet" href="(\/assets\/site-themes\/[^"]+\/themes\.css)">/.exec(head);
  const picker = /import \{ defineThemePicker \} from '([^']+)'; defineThemePicker\(\);/.exec(page.body);
  await checkThemeAssets(css?.[1], picker?.[1], at);
  if (!/<site-theme-picker[\s>]/.test(page.body)) at('no <site-theme-picker> element');
  if (/class="rail"/.test(page.body)) at('the left rail is back');
}

/** What a loaded page shows: theme, picker, rail and pinned elements, the Apps section. */
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
      const select = el.shadowRoot?.querySelector('select');
      return select ? { value: select.value, options: [...select.options].map((o) => o.value) } : null;
    });
  const pinned = [...document.querySelectorAll('body *')]
    .filter((el) => ['sticky', 'fixed'].includes(getComputedStyle(el).position) && !el.closest('#experience'))
    .map((el) => el.tagName.toLowerCase() + (el.getAttribute('class') ? `.${el.getAttribute('class')}` : ''));
  const fallback = document.querySelector('#apps .apps-fallback');
  const reload = fallback?.querySelector('a[href]');
  return {
    theme: root.dataset.theme ?? null,
    background: getComputedStyle(root).backgroundColor,
    sheet: sheet ? new URL(sheet.href).pathname : null,
    picker: picker ? new URL(picker).pathname : null,
    pickerDefined: Boolean(customElements.get('site-theme-picker')),
    pickers,
    rail: Boolean(document.querySelector('.rail')),
    pinned,
    cards: document.querySelectorAll('#apps .site-apps li').length,
    fallbackShown: Boolean(fallback?.checkVisibility()),
    reloadsPage: Boolean(reload) && new URL(reload.href).pathname === location.pathname,
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
    await page.evaluateOnNewDocument(() => localStorage.setItem('site-theme', 'classic-dark'));
    await page.setRequestInterception(true);
    page.on('request', (req) => (req.url().startsWith(BASE + '/') ? req.continue() : req.abort()));
    const res = await page.goto(BASE + path, { waitUntil: 'load' });
    if (res.status() !== 200) return at(`status ${res.status()}`);
    await page
      .waitForFunction(
        () => customElements.get('site-theme-picker') && document.querySelector('#apps .site-apps, #apps .apps-fallback:not([hidden])'),
        { timeout: 15_000 },
      )
      .catch(() => {});

    const seen = await page.evaluate(observePage);
    if (seen.theme !== 'classic-dark') at(`a stored classic-dark choice gives data-theme ${JSON.stringify(seen.theme)}`);
    if (seen.sheet) {
      const dark = await page.evaluate(darkSurface, seen.sheet);
      if (seen.background !== dark) at(`the page background is ${seen.background}, not the Classic Dark surface ${dark}`);
    }
    await checkThemeAssets(seen.sheet, seen.picker, at);
    if (!seen.pickerDefined) at('site-theme-picker is not defined');
    if (!seen.pickers.some((p) => p && p.options.includes('classic-dark') && p.value === 'classic-dark'))
      at(`no visible theme picker shows its select set to classic-dark: ${JSON.stringify(seen.pickers)}`);
    if (seen.cards > 0) at(`${seen.cards} Apps cards rendered with /_site/apps.json unreachable`);
    if (!seen.fallbackShown) at('the Apps fallback line is not shown');
    else if (!seen.reloadsPage) at('the Apps fallback line has no link that reloads the page');

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

async function checkAllInBrowser(problems) {
  const { default: puppeteer } = await import('puppeteer-core');
  const browser = await puppeteer.launch({
    ...(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : { channel: 'chrome' }),
    args: process.env.CI ? ['--no-sandbox'] : [],
  });
  try {
    for (const path of ['/', '/?utm_source=x', '/index.html']) await checkInBrowser(browser, path, problems);
  } finally {
    await browser.close();
  }
}

async function checkComposed(problems) {
  const page = await get('/');
  const at = (msg) => problems.push(`/: ${msg}`);
  if (page.status !== 200) return at(`status ${page.status}`);
  if (!page.headers.get('x-site-shell')) at('not composed by site-shell (no x-site-shell header)');
  if (!/<nav class="sp" aria-label="Site path">/.test(slot(page.body, 'site-path') ?? '')) at('the site path slot was not filled');
  const apps = slot(page.body, 'site-apps') ?? '';
  if (!apps.startsWith('<style data-site-shell>')) at('the Apps slot was not filled');
  const expected = await listedApps(at);
  const cards = appCards(page.body);
  if (expected && JSON.stringify(cards) !== JSON.stringify(expected))
    at(`Apps cards are ${JSON.stringify(cards)}, /_site/apps.json lists ${JSON.stringify(expected)}`);
  if (/class="rail"/.test(page.body)) at('the left rail is back');
}

async function runOnce() {
  const problems = [];
  if (BARE) {
    await checkAllInBrowser(problems);
    return problems;
  }
  await checkComposed(problems);
  await checkStandalone('/?utm_source=x', problems);
  await checkStandalone('/index.html', problems);
  return problems;
}

for (let attempt = 0; ; attempt++) {
  const problems = await runOnce();
  if (problems.length === 0) {
    console.log(`ok: ${BASE} (${BARE ? 'in headless Chrome: /' : '/ composed'}, /?utm_source=x and /index.html standalone)`);
    break;
  }
  if (attempt >= RETRIES) {
    for (const p of problems) console.error(`FAIL ${p}`);
    process.exit(1);
  }
  console.log(`attempt ${attempt + 1}: ${problems.length} problem(s), retrying in 60 s`);
  await new Promise((r) => setTimeout(r, 60_000));
}
