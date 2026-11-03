// Checks the homepage as it is served.
//
//   node scripts/check-live.mjs                          the published site
//   node scripts/check-live.mjs --base http://127.0.0.1:8000 --bare
//                                                        a static copy (no site-shell)
//
// site-shell composes only the exact / (its route pattern also matches the
// query), so every other spelling of the homepage is GitHub Pages' page as
// committed and must work on its own. Checked:
// - / is composed by site-shell: the x-site-shell header, the site row (Home
//   marked as the current page, no trail under it), and Apps cards matching
//   site-shell's /_site/apps.json (the listed apps from site-themes
//   src/apps.ts, less the homepage). No lock is drawn in either. With --bare, /
//   is checked like the others instead.
// - /?utm_source=x and /index.html (and, with --bare, / too) are loaded in
//   headless Chrome (puppeteer-core, the system Chrome or CHROME_PATH) and
//   checked by what they do on their own: a stored classic-dark choice gives
//   <html data-theme="classic-dark"> from the first frame and the Classic Dark
//   surface as the page background; the site-themes stylesheet and picker
//   module they load are the real ones; the theme picker is defined and shows
//   its combobox; there is no rail and nothing sticky or fixed outside the
//   Experience cards, at desktop and phone widths; and the Apps section shows
//   the cards /_site/apps.json lists, with no lock drawn and a gated app's name
//   carrying a visually hidden " (sign-in required)", or, when it cannot be
//   reached, the fallback line with its reload link.
// With --bare every request to another origin is refused, so /_site/apps.json
// cannot be reached and the fallback line is expected; /index.html is then
// loaded once more with /_site/apps.json answered by STUB_APPS below, so the
// page's own Apps renderer is checked too.
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
const APPS_JSON = 'https://akshayprabhakant.com/_site/apps.json';
const GATED_NOTE = ' (sign-in required)';
// What /_site/apps.json answers in the --bare stub run: synthetic entries in
// its shape (not the real list, which lives only in site-themes src/apps.ts):
// the homepage, which the cards leave out, then an open app and a gated one.
const STUB_APPS = [
  { id: 'home', label: 'Home', path: '/', blurb: 'Stub homepage', gated: false },
  { id: 'stub-open', label: 'Stub Open', path: '/stub-open/', blurb: 'Stub open app', gated: false },
  { id: 'stub-gated', label: 'Stub Gated', path: '/stub-gated/', blurb: 'Stub gated app', gated: true },
];
const cardsOf = (apps) => apps.filter((app) => app.id !== 'home').map((app) => ({ id: app.id, href: app.path, gated: Boolean(app.gated) }));

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
async function listedApps(problems) {
  const res = await get('/_site/apps.json');
  if (res.status !== 200) {
    problems.push(`/_site/apps.json answers ${res.status}`);
    return null;
  }
  return cardsOf(JSON.parse(res.body));
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
  const fallback = document.querySelector('#apps .apps-fallback');
  const reload = fallback?.querySelector('a[href]');
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
    cards: [...document.querySelectorAll('#apps .site-apps li')].map((li) => ({
      id: li.dataset.app,
      href: li.querySelector('a')?.getAttribute('href') ?? null,
      gated: 'gated' in li.dataset,
      visible: li.checkVisibility(),
      lockDrawn: Boolean(li.querySelector('svg, img')),
      hiddenNote: li.querySelector('.site-apps-name .site-vh')?.textContent ?? null,
    })),
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

/**
 * apps: the cards /_site/apps.json lists, or null when it cannot be reached.
 * stub (--bare only): the body /_site/apps.json answers instead of being refused.
 */
async function checkInBrowser(browser, path, apps, problems, stub = null) {
  const at = (msg) => problems.push(`${path}${stub ? ' (stubbed apps.json)' : ''}: ${msg}`);
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
        if (stub && req.url() === APPS_JSON)
          return req.respond({ status: 200, contentType: 'application/json', headers: { 'access-control-allow-origin': '*' }, body: JSON.stringify(stub) });
        return req.abort();
      });
    }
    const res = await page.goto(BASE + path, { waitUntil: 'load' });
    if (res.status() !== 200) return at(`status ${res.status()}`);
    await page
      .waitForFunction(
        () => customElements.get('site-theme-picker') && document.querySelector('#apps .site-apps, #apps .apps-fallback:not([hidden])'),
        { timeout: 15_000 },
      )
      .catch(() => {});

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
    if (apps) {
      const cards = seen.cards.map(({ id, href, gated }) => ({ id, href, gated }));
      if (JSON.stringify(cards) !== JSON.stringify(apps))
        at(`Apps cards are ${JSON.stringify(cards)}, /_site/apps.json lists ${JSON.stringify(apps)}`);
      if (seen.cards.some((c) => !c.visible)) at('some Apps cards are not visible');
      if (seen.fallbackShown) at('the Apps fallback line is shown next to the cards');
      for (const c of seen.cards) {
        if (c.lockDrawn) at(`the ${c.id} Apps card draws a lock`);
        const note = c.gated ? GATED_NOTE : null;
        if (c.hiddenNote !== note) at(`the ${c.id} Apps card's hidden note is ${JSON.stringify(c.hiddenNote)}, not ${JSON.stringify(note)}`);
      }
    } else {
      if (seen.cards.length > 0) at(`${seen.cards.length} Apps cards rendered with /_site/apps.json unreachable`);
      if (!seen.fallbackShown) at('the Apps fallback line is not shown');
      else if (!seen.reloadsPage) at('the Apps fallback line has no link that reloads the page');
    }

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

async function checkAllInBrowser(paths, apps, problems, stub = null) {
  const { default: puppeteer } = await import('puppeteer-core');
  const browser = await puppeteer.launch({
    ...(process.env.CHROME_PATH ? { executablePath: process.env.CHROME_PATH } : { channel: 'chrome' }),
    args: process.env.CI ? ['--no-sandbox'] : [],
  });
  try {
    for (const path of paths) await checkInBrowser(browser, path, apps, problems, stub);
  } finally {
    await browser.close();
  }
}

async function checkComposed(apps, problems) {
  const page = await get('/');
  const at = (msg) => problems.push(`/: ${msg}`);
  if (page.status !== 200) return at(`status ${page.status}`);
  if (!page.headers.get('x-site-shell')) at('not composed by site-shell (no x-site-shell header)');
  const path = slot(page.body, 'site-path') ?? '';
  const appsSlot = slot(page.body, 'site-apps') ?? '';
  if (!/<nav class="sp" aria-label="Site"><ul class="sp-apps">/.test(path)) at('the site row slot was not filled');
  else {
    if (!/<a class="sp-app" href="\/" aria-current="page"><span class="sp-label">Home<\/span>/.test(path)) at('the site row does not mark Home as the current page');
    if (/class="sp-trail"/.test(path)) at('the site row has a trail under it on the homepage');
  }
  if (!appsSlot.startsWith('<style data-site-shell>')) at('the Apps slot was not filled');
  if (/<svg\b/.test(path + appsSlot)) at('the site row or the Apps cards draw a lock (an <svg>)');
  const cards = appCards(page.body);
  if (apps && JSON.stringify(cards) !== JSON.stringify(apps))
    at(`Apps cards are ${JSON.stringify(cards)}, /_site/apps.json lists ${JSON.stringify(apps)}`);
  if (/class="rail"/.test(page.body)) at('the left rail is back');
}

async function runOnce() {
  const problems = [];
  if (BARE) {
    await checkAllInBrowser(['/', '/?utm_source=x', '/index.html'], null, problems);
    await checkAllInBrowser(['/index.html'], cardsOf(STUB_APPS), problems, STUB_APPS);
    return problems;
  }
  const apps = await listedApps(problems);
  await checkComposed(apps, problems);
  await checkAllInBrowser(['/?utm_source=x', '/index.html'], apps, problems);
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
