# TI4 GameMaster

A free companion website for Twilight Imperium 4th Edition + Prophecy of Kings, made by fans.
Open it and the opening screen explains everything. Three tools share one table setup:

- **Ledger** — objectives, VP track, round console, player clocks, game log.
- **Council Chamber** — agenda reveals with card art, voting and a laws/outcomes record.
- **Battle Arbiter** — automatic combat resolution in place of rolling dice, with a TV display mode.

There's also a TV table screen and a season record of finished games.

Everything runs in your browser. Your game is saved on your device; there are no accounts and no server.

## Works offline, installs like an app

Once the site has loaded, it keeps a complete copy and works with no connection. On a phone or tablet,
use "Add to Home Screen" to keep it like an app. When a new version is published, it downloads in the
background and the site offers "Update now"; nothing switches in the middle of a game on its own.

## Changing the site

After editing any file the site serves, run `python tools/build-offline.py` before committing. It
refreshes the offline file list and the version number in `sw.js`. Browser tests: see `tests/README.md`.

## Run it locally

Any static server works, for example:

```
npx serve .
# or
python -m http.server 8000
```

Then open http://localhost:8000 (opening `index.html` straight from disk blocks some browser features).

## Project

- `docs/ARCHITECTURE.md` — how the tools fit together and the shared game state.
- `docs/ART-AUDIT.md` — art that must be replaced before going public.
- The original artifact code is in the git history (the first commit's `_import/` folder).

See [NOTICE.md](NOTICE.md) for the fan-content notice and credits.
