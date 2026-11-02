#!/usr/bin/env python3
"""Serve a site root for the atlas smoke test.

Every HTML response gets an error-capture hook as the first thing in <head>
(window errors, failed resource loads, unhandled rejections, console.error),
read back by the smoke script from window.__smoke. Every request that does not
answer 200/304 is appended to the log file, which catches failed fetches that
raise no page event.

    python3 serve.py <site-root> <port> <non-200 log file>
"""
import http.server
import socketserver
import sys
from pathlib import Path

ROOT, PORT, LOG = Path(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
HOOK = b"""<script>
window.__smoke = { errors: [] };
addEventListener('error', e => {
  const t = e.target;
  if (t && t !== window && (t.src || t.href)) __smoke.errors.push('resource: ' + (t.src || t.href));
  else __smoke.errors.push('error: ' + (e.message || e));
}, true);
addEventListener('unhandledrejection', e => __smoke.errors.push('rejection: ' + ((e.reason && e.reason.message) || e.reason)));
(() => { const ce = console.error; console.error = (...a) => { __smoke.errors.push('console: ' + a.join(' ')); ce.apply(console, a); }; })();
</script>
"""


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=str(ROOT), **k)

    def send_head(self):
        path = self.translate_path(self.path)
        p = Path(path)
        if p.is_dir() and self.path.split('?')[0].endswith('/'):
            p = p / 'index.html'
        if p.suffix == '.html' and p.is_file():
            body = p.read_bytes().replace(b'<head>', b'<head>\n' + HOOK, 1)
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            from io import BytesIO
            return BytesIO(body)
        return super().send_head()

    def log_request(self, code='-', size='-'):
        if str(code) not in ('200', '304'):
            with open(LOG, 'a') as f:
                f.write(f'{code} {self.path}\n')

    def log_message(self, *a):
        pass


class Server(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


Server(('127.0.0.1', PORT), Handler).serve_forever()
