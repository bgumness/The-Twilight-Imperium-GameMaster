#!/usr/bin/env python3
"""Run every browser test against a local copy of the site.

    pip install playwright && python -m playwright install chromium
    python tests/run_all.py            # from the repo root

Each test prints what it checked; look for ERRORS: [] at the end of each one."""
import os, subprocess, sys, time, http.server, threading, functools
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HERE = os.path.dirname(os.path.abspath(__file__))
TESTS = [('newgame', []), ('newgame', ['390', '844']), ('transfer', []), ('transfer', ['390', '844']), ('combat', []),
         ('home', []), ('review', []), ('twotabs', []), ('back', []), ('fonts', []), ('extras', []), ('offline', [])]
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a): pass
srv = http.server.ThreadingHTTPServer(('localhost', 8765), functools.partial(Quiet, directory=ROOT))
threading.Thread(target=srv.serve_forever, daemon=True).start()
out = os.path.join(ROOT, 'test-output'); os.makedirs(out, exist_ok=True)
failed = 0
for name, args in TESTS:
    print(f'\n=== {name} {" ".join(args)}', flush=True)
    r = subprocess.run([sys.executable, os.path.join(HERE, name + '.py'), *args], cwd=out, env=dict(os.environ, PYTHONPATH=HERE))
    failed += r.returncode != 0
srv.shutdown()
print(f'\n{len(TESTS) - failed} of {len(TESTS)} test scripts ran to completion')
sys.exit(1 if failed else 0)
