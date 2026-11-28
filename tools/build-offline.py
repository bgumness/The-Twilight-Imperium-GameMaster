#!/usr/bin/env python3
"""Regenerate sw.js: the list of files the site keeps for offline use, and the site version.

Run from the repo root after changing any file the site serves:

    python tools/build-offline.py

The version is a hash of every served file, so it changes whenever any of them changes. Browsers that
already have the site download the new version in the background and offer "Update now"; nothing
switches mid-game on its own.
"""
import hashlib, json, os, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVED_DIRS = ['home', 'table', 'ledger', 'council', 'arbiter', 'shared', 'assets']
SERVED_FILES = ['index.html', 'manifest.webmanifest']
SKIP_EXT = {'.md', '.py', '.txt.bak'}


def files():
    out = list(SERVED_FILES)
    for d in SERVED_DIRS:
        for base, _, names in os.walk(os.path.join(ROOT, d)):
            for n in names:
                if n.startswith('.') or os.path.splitext(n)[1] in SKIP_EXT:
                    continue
                out.append(os.path.relpath(os.path.join(base, n), ROOT).replace(os.sep, '/'))
    return sorted(out)


def main():
    fl = files()
    if 'shared/version.js' not in fl:
        fl.append('shared/version.js'); fl.sort()
    h = hashlib.sha256()
    for f in fl:
        if f == 'shared/version.js':      # written below from the hash, so it can't be part of it
            continue
        h.update(f.encode())
        with open(os.path.join(ROOT, f), 'rb') as fh:
            h.update(fh.read())
    version = datetime.date.today().strftime('%Y.%m.%d') + '-' + h.hexdigest()[:8]
    # folders are requested as "ledger/" etc.; cache them under that name too
    urls = ['./'] + [d + '/' for d in ['home', 'table', 'ledger', 'council', 'arbiter']] + [f for f in fl if not f.endswith('/index.html') and f != 'index.html']
    tpl = open(os.path.join(ROOT, 'tools', 'sw.template.js'), encoding='utf-8').read()
    sw = tpl.replace('__VERSION__', version).replace('__FILES__', json.dumps(urls, indent=1))
    with open(os.path.join(ROOT, 'sw.js'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(sw)
    with open(os.path.join(ROOT, 'shared', 'version.js'), 'w', encoding='utf-8', newline='\n') as fh:
        fh.write(f"window.TI4_VERSION = {json.dumps(version)};\n")
    print(f'sw.js: version {version}, {len(urls)} files')


if __name__ == '__main__':
    sys.exit(main())
