#!/usr/bin/env python3
"""Headless smoke of the Election Atlas over a served worktree.

    python3 smoke.py <worktree> <base-url> <out-dir>

Drives chrome-devtools-axi `run` in batches. Per page it reads the error hook the
server injects (window errors, failed resource loads, unhandled rejections,
console.error) and the page's own state, and checks it against what the data
says should be there: data drawn where a file exists, a "not available yet" void
where one does not, and never the word "synthetic". The server's non-200 log is
checked separately (a failed fetch raises no page event).
"""
import concurrent.futures
import json
import os
import re
import subprocess
import sys
from pathlib import Path

WT, BASE, OUT = Path(sys.argv[1]), sys.argv[2].rstrip('/') + '/', Path(sys.argv[3])
DATA = WT / 'work/election-atlas/data'
OUT.mkdir(parents=True, exist_ok=True)
load = lambda rel: json.loads((DATA / rel).read_text(encoding='utf-8'))
manifest, avail, regions = load('manifest.json'), load('availability.json'), load('regions.json')['regions']
coverage = load('geo/ac/coverage.json')['checked']
LS_YEARS = manifest['elections']['ls']['years']
CYCLES = manifest['elections']['ac']['cycles']

COMMON = r"""
const PAPER2 = 'rgb(227, 233, 244)';
const visible = el => !!el && !el.hidden && !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
const txt = s => (document.querySelector(s) || {}).textContent || '';
const STATIC_VOIDS = [/^Not yet fetched/, /^No news yet/, /^There is no map of this state/];
function common() {
  const html = document.documentElement.outerHTML;
  const voids = [...document.querySelectorAll('.void')].filter(visible).map(v => v.textContent.trim());
  return {
    errors: (window.__smoke || { errors: ['no hook'] }).errors,
    synthetic: /synthetic/i.test(html),
    falseNone: /no by-elections (on record|in )/i.test(document.body.innerText),
    badVoids: voids.filter(v => !/^Not available yet — .+ ha(s|ve) not been added from .+\.$/.test(v) && !STATIC_VOIDS.some(r => r.test(v))),
    voids,
    footer: /Portraits: Parliament of India \(sansad\.in\)\. Party symbols: Wikimedia Commons contributors/.test(txt('footer.credits')),
  };
}
const filled = sel => [...document.querySelectorAll(sel)].filter(p => getComputedStyle(p).fill !== PAPER2).length;
const total = sel => document.querySelectorAll(sel).length;
"""

NATIONAL = r"""
async (u) => {
  const c = common();
  const stands = document.querySelector('.tense-opt[data-tense="stands"]');
  return { ...c,
    note: txt('#mapnote'),
    pressed: (document.querySelector('.tense-opt[aria-pressed="true"]') || {}).dataset?.tense,
    standsDisabled: stands && stands.getAttribute('aria-disabled') === 'true',
    pcFilled: filled('#map .pc'), pcTotal: total('#map .pc'),
    rows: total('#ntable-body tr'),
    cards: total('#belt-scroll .belt-card'),
    credits: total('#belt-scroll .photo-credit'),
    beltVoid: visible(document.querySelector('#belt-void')) ? txt('#belt-void') : null,
    beltTitle: txt('#belt-title'),
  };
}
"""

STATE = r"""
async (u) => {
  const c = common();
  const stands = document.querySelector('.tense-opt[data-tense="stands"]');
  return { ...c,
    pressed: (document.querySelector('.tense-opt[aria-pressed="true"]') || {}).dataset?.tense,
    standsDisabled: stands && stands.getAttribute('aria-disabled') === 'true',
    pcFilled: filled('#map-pc .pc'), pcTotal: total('#map-pc .pc'),
    pcRows: total('#table-pc tbody tr'), pcVoid: !!document.querySelector('#panel-pc .void'),
    capPc: txt('#cap-pc'), capAc: txt('#cap-ac'),
    acFilled: filled('#map-ac .ac'), acTotal: total('#map-ac .ac'),
    acYears: [...document.querySelectorAll('#years-ac .year')].map(b => ({ y: +b.dataset.year, na: b.getAttribute('aria-disabled') === 'true', on: b.getAttribute('aria-pressed') === 'true' })),
    acVoid: txt('#table-ac .void'), acRows: total('#table-ac tbody tr'),
    beltShown: visible(document.querySelector('#belt')),
    beltVoid: visible(document.querySelector('#belt-void')) ? txt('#belt-void') : null,
    cards: total('#belt-scroll .belt-card'),
  };
}
"""

MP = r"""
async (u) => {
  const c = common();
  return { ...c,
    title: txt('#p-const'), name: txt('#p-name'), role: txt('#p-role'),
    face: !!document.querySelector('#p-face img, #p-face .monogram'),
    credit: txt('#p-credit'),
    fund: total('#fund .fstep'), lsStats: total('#ls-stats .ls-stat'),
    mpladsVoid: txt('#mplads-body .void'), lsVoid: txt('#ls-body .void'),
    mla: [...document.querySelectorAll('#ac-cross a')].map(a => a.getAttribute('href')),
  };
}
"""

MLA = r"""
async (u) => {
  const c = common();
  return { ...c,
    title: txt('#p-const'), name: txt('#p-name'), facts: total('#p-facts .fact'),
    resultVoid: visible(document.querySelector('#result-void')) ? txt('#result-void') : null,
    cross: total('#pc-cross a'),
  };
}
"""


def probe_expr(probe):
    """A self-contained async IIFE string: the shared helpers, then the probe."""
    return '(async () => {' + COMMON + '\nreturn await (' + probe.strip() + ')(); })()'


def run_batch(name, urls, probe, settle=1500, click=None, workers=1):
    """chrome-devtools-axi runs over urls, split across `workers` named browser
    sessions; returns {url: probe result}."""
    if workers > 1 and len(urls) > 1:
        parts = [urls[i::workers] for i in range(workers)]
        res = {}
        with concurrent.futures.ThreadPoolExecutor(workers) as ex:
            futs = [ex.submit(run_batch, f'{name}-w{i}', part, probe, settle, click, 1) for i, part in enumerate(parts) if part]
            for f in futs:
                res.update(f.result())
        return res
    session = 'smoke-' + name.split('-w')[-1] if '-w' in name else 'smoke-0'
    script = f"""
const PROBE = {json.dumps(probe_expr(probe))};
const STATE_PROBE = {json.dumps(probe_expr(STATE))};
const urls = {json.dumps(urls)};
const clicks = {json.dumps(click or {})};
for (const u of urls) {{
  try {{
    await page.open({json.dumps(BASE)} + u);
    await page.wait({settle});
    let r;
    if (clicks[u]) {{
      r = [];
      for (const y of clicks[u]) {{
        await page.eval(`(() => {{ document.querySelector('#years-ac .year[data-year="${{y}}"]').click(); return 1; }})()`);
        await page.wait(800);
        r.push({{ y, ...(await page.eval(STATE_PROBE)) }});
      }}
    }} else r = await page.eval(PROBE);
    console.log(JSON.stringify({{ u, r }}));
  }} catch (e) {{ console.log(JSON.stringify({{ u, fail: String(e) }})); }}
}}
"""
    (OUT / f'{name}.js').write_text(script, encoding='utf-8')
    env = {**os.environ, 'CHROME_DEVTOOLS_AXI_SESSION': session}
    p = subprocess.run(['chrome-devtools-axi', 'run'], input=script, capture_output=True, text=True, timeout=3000, env=env)
    res = {}
    for line in p.stdout.splitlines():
        line = line.strip()
        if line.startswith('{"u"'):
            d = json.loads(line)
            res[d['u']] = d.get('r', {'fail': d.get('fail')})
    (OUT / f'{name}.json').write_text(json.dumps(res, indent=1, ensure_ascii=False), encoding='utf-8')
    if len(res) != len(urls):
        print(f'{name}: only {len(res)} of {len(urls)} results; stdout tail: {p.stdout[-600:]} stderr: {p.stderr[-600:]}')
    return res


problems = []


def bad(u, why):
    problems.append(f'{u}: {why}')


def check_common(u, r):
    if 'fail' in r:
        return bad(u, 'probe failed: ' + str(r['fail']))
    if r['errors']:
        bad(u, 'errors: ' + '; '.join(r['errors'])[:300])
    if r['synthetic']:
        bad(u, 'page says "synthetic"')
    if r['falseNone']:
        bad(u, 'claims no by-elections without a by-election file')
    if r['badVoids']:
        bad(u, 'void with unexpected wording: ' + r['badVoids'][0][:120])
    if not r['footer']:
        bad(u, 'image credit footer missing')


def roster(kind, *keys):
    node = avail['cabinet'][kind]
    for k in keys:
        node = (node or {}).get(str(k))
    return node or {'sworn_in': False, 'as_it_stands': False}


# ── national: every LS year x both tenses ─────────────────────────────────
nat_urls = [f'?y={y}' + t for y in LS_YEARS for t in ('', '&t=stands')]
for u, r in run_batch('national', nat_urls, NATIONAL, settle=2500).items():
    check_common(u, r)
    if 'fail' in r:
        continue
    y = int(re.search(r'y=(\d+)', u).group(1))
    byel = avail['ls']['byel'][str(y)]
    ros = roster('union', y)
    stands_ok = byel or ros['as_it_stands']
    want = 'stands' if ('t=stands' in u and stands_ok) else 'elected'
    if r['pressed'] != want:
        bad(u, f'tense {r["pressed"]}, expected {want}')
    if r['standsDisabled'] == stands_ok:
        bad(u, f'"As it stands" disabled={r["standsDisabled"]} with stands data={stands_ok}')
    if not r['pcFilled'] or r['rows'] == 0:
        bad(u, 'national map or table empty where the result file exists')
    has_roster = ros['as_it_stands'] if want == 'stands' else ros['sworn_in']
    if has_roster and (not r['cards'] or r['beltVoid']):
        bad(u, 'cabinet roster exists but the belt shows no cards')
    if has_roster and r['credits'] != r['cards']:
        bad(u, f'{r["cards"]} cabinet cards but {r["credits"]} photo credits')
    if not has_roster and (r['cards'] or not r['beltVoid']):
        bad(u, 'cabinet roster missing but the belt is not the void')
    if not byel and 'by-election record not available yet' not in r['note']:
        bad(u, 'map note does not say the by-election record is not available yet')

# ── state: every state x every LS year x both tenses ──────────────────────
state_urls = [f'state/?s={s["code"]}&y={y}' + t for s in regions for y in LS_YEARS for t in ('', '&t=stands')]
state_res = {}
state_res.update(run_batch('state', state_urls, STATE, settle=1800, workers=4))
for u, r in state_res.items():
    check_common(u, r)
    if 'fail' in r:
        continue
    s = re.search(r's=([A-Z-]+)', u).group(1)
    y = int(re.search(r'y=(\d+)', u).group(1))
    cyc = CYCLES.get(s, [])
    shown = [a['y'] for a in r['acYears'] if a['on']]
    shown_cycle = shown[0] if shown else None
    stands_ok = avail['ls']['byel'][str(y)] or (shown_cycle and roster('state', s, shown_cycle)['as_it_stands'])
    want = 'stands' if ('t=stands' in u and stands_ok) else 'elected'
    if r['pressed'] != want:
        bad(u, f'tense {r["pressed"]}, expected {want}')
    if bool(r['standsDisabled']) == bool(stands_ok):
        bad(u, f'"As it stands" disabled={r["standsDisabled"]} with stands data={bool(stands_ok)}')
    if not r['pcFilled'] or not r['pcRows'] or r['pcVoid']:
        bad(u, 'Lok Sabha panel empty or void where the result file exists')
    if s in coverage and cyc:
        ok = {int(k): v for k, v in avail['ac'][s]['cycles'].items()}
        if [a['y'] for a in r['acYears']] != cyc:
            bad(u, f'assembly years {[a["y"] for a in r["acYears"]]}, expected cycles {cyc}')
        if any(a['na'] == ok[a['y']] for a in r['acYears']):
            bad(u, 'assembly year marked unavailable/available against availability.json')
        latest = max([c for c in cyc if ok[c]] or cyc)
        if shown_cycle != latest:
            bad(u, f'assembly panel shows {shown_cycle}, expected {latest}')
        if ok[latest]:
            if not r['acFilled'] or not r['acRows'] or r['acVoid']:
                bad(u, 'assembly result exists but the panel is empty or void')
        else:
            if r['acFilled'] or r['acRows'] or 'Not available yet' not in r['acVoid'] \
                    or 'not available yet' not in r['capAc'] or not r['acTotal']:
                bad(u, 'assembly cycle missing but the panel is not the void over blank boundaries')
        has_roster = roster('state', s, latest)['as_it_stands' if want == 'stands' else 'sworn_in']
        if not r['beltShown']:
            bad(u, 'state council belt hidden for a state with assembly cycles')
        elif has_roster == bool(r['beltVoid']):
            bad(u, 'state council belt: void/roster mismatch with availability.json')
    elif s not in coverage:
        if r['beltShown']:
            bad(u, 'belt shown for a state without assembly cycles')
        if not any(v.startswith('There is no map') for v in r['voids']):
            bad(u, 'unmapped state without its no-map note')

# ── every assembly cycle for the mapped states ────────────────────────────
cyc_urls = {f'state/?s={s}&y={LS_YEARS[-1]}': CYCLES[s] for s in sorted(CYCLES) if s in coverage}
for u, rs in run_batch('cycles', list(cyc_urls), STATE, settle=1800, click=cyc_urls).items():
    s = re.search(r's=([A-Z-]+)', u).group(1)
    if isinstance(rs, dict):
        bad(u, 'cycle clicks failed: ' + str(rs.get('fail')))
        continue
    for r in rs:
        uu = f'{u} assembly {r["y"]}'
        check_common(uu, r)
        ok = avail['ac'][s]['cycles'][str(r['y'])]
        on = [a['y'] for a in r['acYears'] if a['on']]
        if on != [r['y']]:
            bad(uu, f'pressed year {on}')
        if ok and (r['acVoid'] or not r['acFilled']):
            bad(uu, 'cycle present but drawn as void')
        if not ok and (r['acFilled'] or f'{r["y"]} assembly results' not in r['acVoid']):
            bad(uu, 'cycle missing but not the void')

# ── MP pages the state pages link to ──────────────────────────────────────
def keyify_state(name, abbr):
    k = re.sub(r'[^a-z0-9]', '', re.sub(r'\(sc\)|\(st\)', '', str(name or '').lower()))
    return k[:-len(abbr)] if abbr and k.endswith(abbr.lower()) else k


mp_urls = []
for s in sorted(avail.get('mplads', {})):
    idx = load(f'mplads/{s}/index.json')
    abbr = s.split('-')[1]
    by_name = {keyify_state(m['constituency'], abbr): m['constituency_key'] for m in idx['mps']}
    topo = load(f'geo/ls/{s}.json')
    for g in topo['objects']['pcs']['geometries']:
        key = by_name.get(keyify_state(g['properties']['ls_seat_name'], abbr))
        if key:
            mp_urls.append(f'mp/?s={s}&c={key}')
mp_urls = sorted(set(mp_urls))
mla_urls = set()
for u, r in run_batch('mp', mp_urls, MP, settle=1800, workers=4).items():
    check_common(u, r)
    if 'fail' in r:
        continue
    s, c = re.search(r's=([A-Z-]+)&c=(\w+)', u).groups()
    has_par = c in avail['parliament'].get(s, [])
    has_mplads = c in avail['mplads'].get(s, [])
    if not r['name'] or r['name'] in ('—', 'Result not available yet'):
        bad(u, f'no member name ({r["name"]!r})')
    if not r['face']:
        bad(u, 'no portrait and no monogram')
    if has_par != bool(r['lsStats']) or has_par == bool(r['lsVoid']):
        bad(u, f'Sansad record present={has_par} but stats={r["lsStats"]} void={bool(r["lsVoid"])}')
    if has_mplads != bool(r['fund']) or has_mplads == bool(r['mpladsVoid']):
        bad(u, f'MPLADS present={has_mplads} but fund={r["fund"]} void={bool(r["mpladsVoid"])}')
    if s in coverage and not r['mla']:
        bad(u, 'no assembly seats linked for a mapped state')
    for h in r['mla']:
        mla_urls.add(h.replace('../', ''))

# ── MLA pages the MP pages link to ────────────────────────────────────────
mla_urls = sorted(mla_urls)
mla_res = {}
mla_res.update(run_batch('mla', mla_urls, MLA, settle=900, workers=4))
for u, r in mla_res.items():
    check_common(u, r)
    if 'fail' in r:
        continue
    s = re.search(r's=([A-Z-]+)', u).group(1)
    any_cycle = any(avail['ac'].get(s, {}).get('cycles', {}).values())
    if r['title'] == re.search(r'c=(\w+)', u).group(1):
        bad(u, 'constituency not resolved from the boundary set')
    if not any_cycle and (r['facts'] or r['name'] != 'Result not available yet' or not r['resultVoid']):
        bad(u, 'no assembly cycle added but the MLA hero is not the void')
    if any_cycle and (r['resultVoid'] and r['facts']):
        bad(u, 'MLA hero shows both a result and the void')

summary = {
    'pages': {'national': len(nat_urls), 'state': len(state_urls), 'assembly_cycles': sum(len(v) for v in cyc_urls.values()),
              'mp': len(mp_urls), 'mla': len(mla_urls)},
    'problems': problems,
}
(OUT / 'summary.json').write_text(json.dumps(summary, indent=1, ensure_ascii=False), encoding='utf-8')
print(json.dumps(summary['pages']), 'problems:', len(problems))
for p in problems[:60]:
    print(' ', p)
