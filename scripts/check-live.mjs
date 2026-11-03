// Checks the homepage as it is served.
//
//   node scripts/check-live.mjs                          the published site
//   node scripts/check-live.mjs --base http://127.0.0.1:8000 --bare
//                                                        a static copy (no site-shell)
//
// site-shell composes only the exact / (its route pattern also matches the
// query), so every other spelling of the homepage is GitHub Pages' page as
// committed and must work on its own. Checked:
// - / is composed by site-shell: the x-site-shell header, the site path and the
//   Apps list from site-themes src/apps.ts. With --bare, / is checked like the
//   others instead.
// - /?utm_source=x and /index.html carry, on their own: the inline theme boot
//   script, a stylesheet that defines Classic Light and Classic Dark, the theme
//   picker module, and the four Apps cards (locks on Quiz Room and Graph Notes).
// - None of them has the old left rail.
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

const APPS = [
  { id: 'chat', href: '/chat-archives', gated: false },
  { id: 'quiz', href: '/quiz', gated: true },
  { id: 'graph', href: '/graph/', gated: true },
  { id: 'atlas', href: '/elections/india/', gated: false },
];

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

function sameApps(cards) {
  return JSON.stringify(cards) === JSON.stringify(APPS);
}

async function checkStandalone(path, problems) {
  const page = await get(path);
  const at = (msg) => problems.push(`${path}: ${msg}`);
  if (page.status !== 200) return at(`status ${page.status}`);
  const head = page.body.slice(0, page.body.indexOf('</head>'));
  if (!/<script>\(function siteThemeBoot\(/.test(head)) at('no inline theme boot script in <head>');

  const css = /<link rel="stylesheet" href="(\/assets\/site-themes\/[^"]+\/themes\.css)">/.exec(head);
  if (!css) at('no site-themes stylesheet link in <head>');
  else {
    const sheet = await get(css[1]);
    if (sheet.status !== 200) at(`${css[1]} answers ${sheet.status}`);
    else if (!sheet.body.includes('[data-theme="classic-light"]') || !sheet.body.includes('[data-theme="classic-dark"]'))
      at(`${css[1]} does not define both Classic Light and Classic Dark`);
  }

  const picker = /import \{ defineThemePicker \} from '([^']+)'; defineThemePicker\(\);/.exec(page.body);
  if (!picker) at('no theme picker module');
  else {
    const mod = await get(picker[1]);
    if (mod.status !== 200 || !mod.body.includes('export function defineThemePicker')) at(`${picker[1]} is not the picker module`);
  }
  if (!/<site-theme-picker[\s>]/.test(page.body)) at('no <site-theme-picker> element');

  const cards = appCards(page.body);
  if (!sameApps(cards)) at(`Apps cards are ${JSON.stringify(cards)}, expected ${JSON.stringify(APPS)}`);
  if (/class="rail"/.test(page.body)) at('the left rail is back');
}

async function checkComposed(problems) {
  const page = await get('/');
  const at = (msg) => problems.push(`/: ${msg}`);
  if (page.status !== 200) return at(`status ${page.status}`);
  if (!page.headers.get('x-site-shell')) at('not composed by site-shell (no x-site-shell header)');
  if (!/<nav class="sp" aria-label="Site path">/.test(slot(page.body, 'site-path') ?? '')) at('the site path slot was not filled');
  const apps = slot(page.body, 'site-apps') ?? '';
  if (!apps.startsWith('<style data-site-shell>')) at('the Apps slot still holds the static fallback');
  const cards = appCards(page.body);
  if (!sameApps(cards)) at(`Apps cards are ${JSON.stringify(cards)}, expected ${JSON.stringify(APPS)}`);
  if (/class="rail"/.test(page.body)) at('the left rail is back');
}

async function runOnce() {
  const problems = [];
  if (BARE) await checkStandalone('/', problems);
  else await checkComposed(problems);
  await checkStandalone('/?utm_source=x', problems);
  await checkStandalone('/index.html', problems);
  return problems;
}

for (let attempt = 0; ; attempt++) {
  const problems = await runOnce();
  if (problems.length === 0) {
    console.log(`ok: ${BASE} (${BARE ? '/ standalone' : '/ composed'}, /?utm_source=x and /index.html standalone)`);
    break;
  }
  if (attempt >= RETRIES) {
    for (const p of problems) console.error(`FAIL ${p}`);
    process.exit(1);
  }
  console.log(`attempt ${attempt + 1}: ${problems.length} problem(s), retrying in 60 s`);
  await new Promise((r) => setTimeout(r, 60_000));
}
