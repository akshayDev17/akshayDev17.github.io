#!/usr/bin/env python3
"""URL inventory of what GitHub Pages publishes for this repository.

Phase 0 baseline for moving the Election Atlas off GitHub Pages. Every row is a
URL a reader can request today, so a later host can be replayed against it:

  file      a tracked file Jekyll publishes byte-for-byte (no file has front matter)
  retired   a published file that held dummy data; expected to answer 404 once the
            dummy files are deleted, and listed so that 404 is not read as a regression
  redirect  a directory URL without its trailing slash (Pages answers 301 to the slash)
  page      a directory URL with its slash, served from that directory's index.html
  deeplink  a page URL carrying the query string the atlas pages read (?s= ?y= ?t= ?c=)

The local half is computed from a git ref, so it is reproducible: the same ref
always yields the same rows. `--live BASE` adds what the live host answered.

Usage:
  python3 .atlas-cutover/inventory.py --ref 4c64517 --out .atlas-cutover/url-inventory.tsv
  python3 .atlas-cutover/inventory.py --ref 4c64517 --live https://akshayprabhakant.com \
      --out .atlas-cutover/url-inventory.tsv
"""
import argparse
import concurrent.futures
import datetime
import hashlib
import json
import mimetypes
import os
import re
import subprocess
import sys
import urllib.error
import urllib.request

ATLAS = 'work/election-atlas'
DATA = ATLAS + '/data'

# The dummy files, by the plan's inventory (D1-D5). Each one says so in its own
# metadata; build_rows() re-reads that metadata and refuses to run if it does not.
AC_STATES = ['IN-BR', 'IN-CT', 'IN-HR', 'IN-OD', 'IN-PB', 'IN-TN', 'IN-UP', 'IN-WB']
DUMMY_YEARS = [2014, 2019, 2024]
RETIRED = sorted(
    [f'{DATA}/results/ac/{s}/{y}.json' for s in AC_STATES for y in DUMMY_YEARS]
    + [f'{DATA}/results/ac/{s}/{y}-detail.json' for s in AC_STATES for y in DUMMY_YEARS]
    + [f'{DATA}/results/ls/byel/2014.json', f'{DATA}/cabinet/union/2014.json']
    + [f'{DATA}/cabinet/state/IN-UP/{y}.json' for y in DUMMY_YEARS]
)
DUMMY_MARK = re.compile(r'synthetic|dummy', re.I)

# Text types GitHub Pages labels with a charset; everything else is bare.
CT_OVERRIDES = {'.js': 'application/javascript', '.json': 'application/json',
                '.md': 'text/markdown', '.mjs': 'application/javascript'}


def git(repo, *args, data=None):
    return subprocess.run(['git', '-C', repo, *args], input=data, check=True,
                          capture_output=True).stdout


def tracked_files(repo, ref):
    out = git(repo, 'ls-tree', '-r', '-z', '--name-only', ref).decode()
    return [p for p in out.split('\0') if p]


def jekyll_publishes(path):
    """Jekyll skips any path segment starting with '.', '_', '#' or '~', and the
    site's CNAME is a Pages setting rather than a page."""
    if path == 'CNAME':
        return False
    return not any(seg[:1] in '._#~' or seg.endswith('~') for seg in path.split('/'))


def blob_sha256(repo, ref, paths):
    """sha256 of each path's content at ref, through one `git cat-file --batch`."""
    req = ''.join(f'{ref}:{p}\n' for p in paths).encode()
    out = git(repo, 'cat-file', '--batch', data=req)
    shas, i = {}, 0
    for p in paths:
        nl = out.index(b'\n', i)
        size = int(out[i:nl].split()[2])
        body = out[nl + 1:nl + 1 + size]
        shas[p] = hashlib.sha256(body).hexdigest()
        i = nl + 1 + size + 1
    return shas


def blob_json(repo, ref, path):
    return json.loads(git(repo, 'show', f'{ref}:{path}'))


def content_type(path):
    ext = os.path.splitext(path)[1].lower()
    if ext in CT_OVERRIDES:
        return CT_OVERRIDES[ext]
    return mimetypes.guess_type(path)[0] or 'application/octet-stream'


def keyify(name):
    """The MLA page's key: lowercase, drop (SC)/(ST), keep [a-z0-9]."""
    s = re.sub(r'\(sc\)|\(st\)', '', str(name or '').lower())
    return re.sub(r'[^a-z0-9]', '', s)


def deeplinks(repo, ref):
    manifest = blob_json(repo, ref, f'{DATA}/manifest.json')
    regions = [r['code'] for r in blob_json(repo, ref, f'{DATA}/regions.json')['regions']]
    ls_years = manifest['elections']['ls']['years']
    base = '/' + ATLAS
    rows = []
    for y in ls_years:
        rows.append(f'{base}/?y={y}')
        rows.append(f'{base}/?y={y}&t=stands')
    for s in regions:
        for y in ls_years:
            rows.append(f'{base}/state/?s={s}&y={y}')
            rows.append(f'{base}/state/?s={s}&y={y}&t=stands')
    files = set(tracked_files(repo, ref))
    for s in regions:
        idx = f'{DATA}/mplads/{s}/index.json'
        if idx in files:
            for m in blob_json(repo, ref, idx).get('mps', []):
                rows.append(f'{base}/mp/?s={s}&c={m["constituency_key"]}')
    for s in regions:
        topo = f'{DATA}/geo/ac/{s}.json'
        if topo in files:
            geoms = blob_json(repo, ref, topo)['objects']['acs']['geometries']
            for k in sorted({keyify(g['properties']['ac']) for g in geoms}):
                rows.append(f'{base}/mla/?s={s}&c={k}')
    return rows


def build_rows(repo, ref):
    published = sorted(p for p in tracked_files(repo, ref) if jekyll_publishes(p))
    missing = [p for p in RETIRED if p not in published]
    if missing:
        sys.exit(f'retired paths absent at {ref}: {missing}')
    for p in RETIRED:
        doc = blob_json(repo, ref, p)
        meta = ' '.join(str(doc.get(k, '')) for k in ('note', 'source'))
        if not DUMMY_MARK.search(meta):
            sys.exit(f'{p} at {ref} does not declare itself dummy data; refusing to retire it')
    shas = blob_sha256(repo, ref, published)
    retired = set(RETIRED)
    rows = []
    for p in published:
        kind = 'retired' if p in retired else 'file'
        expect = '404 retired: dummy data' if p in retired else '200'
        rows.append({'kind': kind, 'url': '/' + p, 'expect': expect,
                     'content_type': content_type(p), 'sha256': shas[p]})
    dirs = sorted({os.path.dirname(p) for p in published if os.path.basename(p) == 'index.html'})
    for d in dirs:
        slash = '/' + d + '/' if d else '/'
        sha = shas[(d + '/' if d else '') + 'index.html']
        rows.append({'kind': 'page', 'url': slash, 'expect': '200',
                     'content_type': 'text/html', 'sha256': sha})
        if d:
            rows.append({'kind': 'redirect', 'url': '/' + d, 'expect': '301 ' + slash,
                         'content_type': '', 'sha256': ''})
    index_sha = {'/' + d + '/': shas[d + '/index.html'] for d in dirs if d}
    for u in deeplinks(repo, ref):
        page = u.split('?')[0]
        rows.append({'kind': 'deeplink', 'url': u, 'expect': '200',
                     'content_type': 'text/html', 'sha256': index_sha[page]})
    return rows


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


OPENER = urllib.request.build_opener(NoRedirect)

# The Cloudflare edge in front of Pages rewrites every HTML response: a hidden
# crawler link after <body>, a challenge-platform script and the Web Analytics
# beacon before </body>, with per-request tokens. They are removed before
# hashing, so the live hash of an HTML page compares to the committed file.
EDGE_LINK = re.compile(rb'<a href="[^"]*/cdn-cgi/content\?[^"]*"[^>]*>.*?</a>', re.S)
EDGE_SCRIPT = re.compile(rb'<script>\(function\(\)\{function c\(\).*?__CF\$cv\$params.*?</script>', re.S)
EDGE_BEACON = re.compile(rb'<script[^>]*src="https://static\.cloudflareinsights\.com/[^"]*"[^>]*></script>\n?', re.S)


def strip_edge_injections(body):
    for pattern in (EDGE_LINK, EDGE_SCRIPT, EDGE_BEACON):
        body = pattern.sub(b'', body)
    return body


def fetch(base, url):
    req = urllib.request.Request(base + url, headers={'User-Agent': 'atlas-url-inventory/1'})
    try:
        with OPENER.open(req, timeout=120) as r:
            ct = r.headers.get('Content-Type', '')
            if ct.startswith('text/html'):
                return r.status, ct, hashlib.sha256(strip_edge_injections(r.read())).hexdigest(), ''
            h = hashlib.sha256()
            for chunk in iter(lambda: r.read(1 << 16), b''):
                h.update(chunk)
            return r.status, ct, h.hexdigest(), ''
    except urllib.error.HTTPError as e:
        return e.code, e.headers.get('Content-Type', ''), '', e.headers.get('Location', '')
    except Exception as e:  # network failure: recorded, not fatal
        return 0, type(e).__name__, '', ''


def add_live(rows, base):
    with concurrent.futures.ThreadPoolExecutor(8) as ex:
        results = ex.map(lambda r: fetch(base, r['url']), rows)
        for r, (status, ct, sha, loc) in zip(rows, results):
            r.update(live_status=status, live_content_type=ct, live_sha256=sha, live_location=loc)


COLUMNS = ['kind', 'url', 'expect', 'content_type', 'sha256',
           'live_status', 'live_content_type', 'live_sha256', 'live_location']


def write_tsv(rows, out, ref, base):
    with open(out, 'w', encoding='utf-8') as f:
        f.write(f'# ref={ref}\n')
        if base:
            stamp = datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%MZ')
            f.write(f'# live={base} fetched={stamp}\n')
        f.write('\t'.join(COLUMNS) + '\n')
        for r in rows:
            f.write('\t'.join(str(r.get(c, '')) for c in COLUMNS) + '\n')


def summarise(rows, live):
    counts = {}
    for r in rows:
        counts[r['kind']] = counts.get(r['kind'], 0) + 1
    print('rows:', len(rows), counts)
    if not live:
        return
    bad = []
    for r in rows:
        want = r['expect'].split()[0]
        got = str(r.get('live_status', ''))
        if r['kind'] == 'retired':
            want = '200'  # still live until the dummy files are deleted
        if got != want:
            bad.append((r['url'], want, got))
        elif r['sha256'] and r.get('live_sha256') and r['sha256'] != r['live_sha256']:
            bad.append((r['url'], 'sha ' + r['sha256'][:12], 'sha ' + r['live_sha256'][:12]))
        elif r['kind'] == 'redirect' and not r.get('live_location', '').endswith(r['expect'].split()[1]):
            bad.append((r['url'], r['expect'], r.get('live_location', '')))
    print('live mismatches:', len(bad))
    for b in bad[:50]:
        print('  ', *b)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--ref', required=True, help='git ref whose tree Pages publishes')
    ap.add_argument('--live', help='base URL to fetch every row from, e.g. https://akshayprabhakant.com')
    ap.add_argument('--out', required=True)
    ap.add_argument('--repo', default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    a = ap.parse_args()
    ref = git(a.repo, 'rev-parse', '--short', a.ref).decode().strip()
    rows = build_rows(a.repo, ref)
    if a.live:
        add_live(rows, a.live.rstrip('/'))
    write_tsv(rows, a.out, ref, a.live)
    summarise(rows, a.live)


if __name__ == '__main__':
    main()
